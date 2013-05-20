# -*- coding: utf-8 -*-
'''
Created on 2013-3-11

@author: Alvaro
'''
import sqlite3
import urllib, urllib2, cookielib
import re, time, base64, os, HTMLParser, datetime
import rsa,binascii


user_name = "qiaoyq%40mail.ustc.edu.cn"       
pass_word = "14142323"          
init_url = 'http://weibo.com/1665964555/yxYcxxe41' #'http://weibo.com/1499104401/yrsKE8wSN'    
pubkey_1 = 'EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443'
pubkey_2 = '10001'


def rsa_encrypt(servertime,nonce,passwd):
    '''rsa加密'''
    msg = servertime+'\t'+nonce+'\n'+passwd
    pubkey = rsa.PublicKey(int(pubkey_1,16),int(pubkey_2,16))
    return binascii.b2a_hex(rsa.encrypt(msg,pubkey))


class Cookie(object):
    def __init__(self):
        self.cookie = 'SINAGLOBAL=4094117090323.8486.1364265042490; ULV=1366872559761:7:5:2:6733298246961.887.1366872559510:1366532341920; UOR=,,login.sina.com.cn; myuid=2671992203; un=qiaoyq@mail.ustc.edu.cn; SinaRot_wb_r_topic=83; USRUG=usrmdins411_114; USRV5WB=usrmdins311140; _s_tentry=login.sina.com.cn; Apache=6733298246961.887.1366872559510; ULOGIN_IMG=13668731831143; SUS=SID-2671992203-1366875837-JA-mg2vh-d9ac7e5c93a55b953e897d0772486469; SUE=es%3Dfb7901cdc216d34ca4c9ce2a84e66b1c%26ev%3Dv1%26es2%3Da1e2fdb026669f32fc06b0b5387cc413%26rs0%3D6L3jz8%252FQjOUQ4%252Fv3bCemjiUC8%252FV9ykdutM5CAZNrZxYLHKEQzNa5%252BLGclUAZttIztZZS8awWC7AVRmr%252BP277xPeaM3ZDCZ96xHxc%252BmPnOC0ID5PRaJPwRV6vMQuy2o48x0l1TWpl%252Bay97ugO4%252BFV9bEMdEpaHsHfYwv3DHdAUow%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1366875838%26et%3D1366962238%26d%3Dc909%26i%3D9db4%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D4%26st%3D0%26uid%3D2671992203%26user%3Dqiaoyq%2540mail.ustc.edu.cn%26ag%3D4%26name%3Dqiaoyq%2540mail.ustc.edu.cn%26nick%3Dtest_ustc%26fmp%3D%26lcp%3D; ALF=1369467837; SSOLoginState=1366875838; wvr=5'
        self.cj = cookielib.MozillaCookieJar()
        self.opener =  urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')]

    def _request(self, url, bodies = {}, headers = {}):
        '''请求预处理'''
        i=0
        j=0
        while 1:
            request = urllib2.Request(url, urllib.urlencode(bodies), headers = headers)
            try:
                response = self.opener.open(request,timeout=5)
                break
            except:
                time.sleep(10)
            i+=1
            if i == 5:
                raise
        while 1:
            try:
                content = response.read()
                break
            except:
                time.sleep(1)
            j+=1
            if j == 5:
                raise
        return content
    

class Search(object):
    '''处理搜索请求的类'''
    def __init__(self,keyword,cookie,db,uid,max_page=50):
        self.cookie = cookie
        self.db = db
        self.uid = uid 
        self.keyword = keyword
        self.last_page = 0
        self.regex_div = re.compile(r'"pid":"pl_weibo_feedlist"(.*?)</script>')
        self.regex_list = re.compile(r'(<a nick-name=.*?<\\/div>\\n <\\/dd>\\n <dd class=\\"clear\\"><\\/dd>\\n<\\/dl>\\n)')
        self.regex_detail = re.compile(r'<a nick-name=\\"(.*?)\\".*?\\uff1a<em>(.*?)<\\/em>\\n  .*?(\d{16})\\">\\u8f6c\\u53d1.*?<\\/span>\\n <a href=\\"(.*?)\\" title=\\".*?" date=\\"(\d{13})\\"')
#         self.regex_user = re.compile(r'<a nick-name=\\"(.*?)\\" href=\\"(.*?)\\" target=\\"_blank\\" title=\\".*?\\" usercard=\\"id=(\d*?)&usercardkey=weibo_mp\\" suda\-data=\\"key=tblog_search_v4\.1&value=weibo_(.*?):\d*?\\">.*?(<.*?>)?<\\/a>\\uff1a<em>')
#         self.regex_post = re.compile(r'\\uff1a<em>(.*?)<\\/em>\\n  <\\/p>\\n (  <ul class=\\"piclist\\" node-type=\\"feed_list_media_prev\\">\\n   <li>\\n <img class=\\"bigcursor\\" src=\\"(.*?)\\")?')
#         self.regex_detail = re.compile(r'(\d{16})\\">\\u8f6c\\u53d1(\((\d*?)\))?<\\/a>.*?\\u8bc4\\u8bba(\((\d*?)\))?<\\/a>\\n <\\/span>\\n <a href=\\"(.*?)\\" title=\\".*?" date=\\"(\d{13})\\"')
        self.header = {
                  'Host' : 's.weibo.com'
        }
        self.htmlparser=HTMLParser.HTMLParser()
        self.run(max_page)
        
        
    def run(self,max_page):
        self.onePage('1')
        if int(self.last_page) > max_page:
            l_page = max_page
        else:
            l_page = int(self.last_page)
        for i in range(2,l_page+1):
            self.onePage(i)
            
    def onePage(self,page):
        bodies = dict(xsort = 'hot', page = page, scope = 'ori', Refer = 'g')
        req = 'http://s.weibo.com/weibo/' + urllib.quote(self.keyword).replace('%','%25') + '&' + urllib.urlencode(bodies)        
        print 'page:'+str(page)
        while 1:
            content = self.cookie._request(req, {}, self.header)
            print content
    #         print content
            if not self.last_page:
                self.last_page= re.findall(r"value=weibo_page_1' >(\d{1,2})<\\/a>",content)[-1]
            print content
            try:
                div = self.regex_div.search(content).group(1)
                break
            except:
                print '异常...'
                time.sleep(5)
        lists = self.regex_list.findall(div)
        sss=1
        for i in lists:
            print i
            self.onePost(i)
        
    def onePost(self,content_raw):
        ''' 对一条微博的内容进行处理     '''
        detail = self.regex_detail.search(content_raw)
        (name,text,mid,url,time) = (eval('u"%s"'%detail.group(1)),self._post(detail.group(2)),detail.group(3),detail.group(4).replace(r'\/','/'),self._time(detail.group(5)))
        print name+':'+text
        if not self.db.select('post', '*', 'mid="%s"'%detail.group(3)):
            self.db.insert('post', mid=mid, text=text, time=time, url=url, name=name)

    def _post(self,raw_data):
        ''' 对微博内容进行处理
            return:微博内容
        '''
        text=eval('u"%s\"'%self.htmlparser.unescape(re.sub(r'<img src=.*? title=\\\\"|\\\\" type=\\\\"face\\\\" \\\\/>|<.*?>',r'',raw_data).replace(r'\/',r'/')).replace(r'"',r'\"')) #.encode("utf-8")
        return text
    
    def _time(self,raw_time):
        '''对微博的发布时间进行处理'''
        t = time.gmtime(int(raw_time)/1000+28800)
        ptime = datetime.datetime(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
        return ptime

        
class Login(object):
    '''处理登陆过程的类'''
    def __init__(self, cookie):
        self.cookie = cookie
        self.user = user_name
        if not self.tryLogin(user_name,pass_word):
            cookie_o = '    SINAGLOBAL=6313897871157.115.1367764261439; ULV=1368415797727:13:13:2:1895082794250.7397.1368415797699:1368333010880; UOR=,,login.sina.com.cn; myuid=2642681933; un=qiaoyq@mail.ustc.edu.cn; _s_tentry=-; Apache=1895082794250.7397.1368415797699; USRHAWB=usrmdins21133; WBStore=4639942f83659774|undefined; SUS=SID-2671992203-1368428144-JA-fghy7-6ce72a963ca719d94b23fb4d677b6469; SUE=es%3D5016b754c87a1b2eafbefcb5cdc29fce%26ev%3Dv1%26es2%3Df8ca0df8f3ff0f09c55a7d6a84eff4d8%26rs0%3DiBuvgVts2xHZ0%252FwUXQMb6u5PkCNszq2R6z9bQCJxrKq0TdRtsWyBpO5nqVfzBVVL%252BIKUmdKIRgmEPpZ1ynhCysJCXIjnFa2ZvL%252FiXLAJub08lW3yELmWALhaw%252FBxhVZK3Fe5mtEDNM4ku7d%252B4ddk0vSnVqOj7xPkxxmr%252B3YVeWU%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1368428144%26et%3D1368514544%26d%3Dc909%26i%3D608b%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26uid%3D2671992203%26user%3Dqiaoyq%2540mail.ustc.edu.cn%26ag%3D4%26name%3Dqiaoyq%2540mail.ustc.edu.cn%26nick%3Dtest_ustc%26fmp%3D%26lcp%3D; ALF=1371020143; SSOLoginState=1368428144; wvr=5; ULOGIN_IMG=13684284127617'
            cookie.opener.addheaders=[('Cookie',cookie_o)]
            self.uid = '2671992203'

    def tryLogin(self, username, password):
        '''登陆过程'''
        su=base64.b64encode(username)
        bodies = dict(_=int(time.time()),checkpin='1',callback='sinaSSOController.preloginCallBack',client='ssologin.js(v1.4.5)',entry='weibo',rsakt='mod',su=su)
        preloadurl = 'http://login.sina.com.cn/sso/prelogin.php'
        content = self.cookie._request(preloadurl, bodies)
        re_bodies = eval(re.findall('\{.*?\}',content)[0])
        password = rsa_encrypt(str(re_bodies['servertime']),re_bodies['nonce'],pass_word)
        bodies={'encoding':'UTF-8',
                'entry':'weibo',        
                'from':'',
                'gateway':'1',
                'nonce':re_bodies['nonce'],
                'pagerefer':'',
                'prelt':'169',
                'pwencode':'rsa2',
                'returntype':'META',
                'rsakv':re_bodies['rsakv'],
                'savestate':'7',
                'servertime':re_bodies['servertime'],
                'service':'miniblog',
                'sp':password,
                'su':su,
                'url':'http://www.weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
                'useticket':'1',
                'vsnf':'1'
        }
        
        content = self.cookie._request('http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)', bodies)
        moreurl = re.findall('replace\([\'|"](.*?)[\'|"]\)',content)
        surl=moreurl[0]
        if len(moreurl) == 0: print "登录失败!"
        content = self.cookie._request(surl, headers=dict(Referer='http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)',Host='www.weibo.com'))
        print content
        username1=username.replace('%40','@',1)
        if username1 in content:
            print "登录成功！"
            uid = re.findall(r'"uniqueid":"(\d{10})"',content)[0] 
            self.uid=uid
            return True
        
        print "登录失败，正在重试"
        return False
        

class MyDB(object):
    '''sqlite3数据库处理'''
    def __init__(self, filename):
        dirs = os.getcwd()
        self.path = dirs+'\\database\\'+filename+'.sqlite3'#r"\weibo2"
        self.conn = sqlite3.connect(self.path)
        try:
            self.cursor = self.conn.cursor()
        except:
            raise
        self.cursor.execute("SELECT tbl_name FROM sqlite_master WHERE type='table';")
        tbl_existence = [x[0] for x in self.cursor.fetchall()]
        if 'post' not in tbl_existence:
            self.cursor.execute('''create table post(
                mid varchar(13) UNIQUE NOT NULL,
                name varchar(30),
                time datetime NOT NULL,
                text varchar(200),
                url varchar(50) NOT NULL,
                Primary Key(mid)
            );''')

        self.conn.commit()
    
    def __del__(self):
        self.cursor.close()
        self.conn.close()
        
    def insert(self,table,**args):
        '''
        table:str 表名
        args:dict 属性名+属性值
        '''
        keys = args.keys()
        sql = 'insert into '+table+'('+','.join(keys)+') values(?'+',?'*(len(keys)-1)+');' 
        l = tuple([args[i] for i in keys])
        self.cursor.execute(sql,l)
        self.conn.commit()
    
    def select(self,table,keys,conditions=None):
        '''
        table:str 表名
        keys:list 各列表项为属性名
        conditions:str 所有条件描述    
        '''
        if conditions:
            conditions = ' where ' + conditions
        else:
            conditions = ''
        sql='select '+','.join(keys)+' from '+table+conditions+';'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result
        
    def update(self,table,oldkeys,**newkeys):
        '''
        table:str 表名
        newkeys:dict 属性名=新属性值
        oldkeys:str "属性名=旧属性值"
        '''
        keys = newkeys.keys()
        sql ='update '+table+' set '+','.join([i+'=?' for i in keys])+' where '+oldkeys+';'
        self.cursor.execute(sql,tuple([newkeys[i] for i in keys]))
        self.conn.commit()

if __name__ == '__main__':
    db = MyDB('2013_05_06_lichengpengjiuzai')
    cookie=Cookie()
    user = Login(cookie)
    ss = Search('朝鲜 渔船',cookie,db,user.uid)
#     bb=Repost('http://weibo.com/1189591617/ztZeSm2fw',cookie,db,user.uid)
