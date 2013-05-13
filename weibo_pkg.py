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
        self.regex_user = re.compile(r'<a nick-name=\\"(.*?)\\" href=\\"(.*?)\\" target=\\"_blank\\" title=\\".*?\\" usercard=\\"id=(\d*?)&usercardkey=weibo_mp\\" suda\-data=\\"key=tblog_search_v4\.1&value=weibo_(.*?):\d*?\\">.*?(<.*?>)?<\\/a>\\uff1a<em>')
        self.regex_post = re.compile(r'\\uff1a<em>(.*?)<\\/em>\\n  <\\/p>\\n (  <ul class=\\"piclist\\" node-type=\\"feed_list_media_prev\\">\\n   <li>\\n <img class=\\"bigcursor\\" src=\\"(.*?)\\")?')
        self.regex_detail = re.compile(r'(\d{16})\\">\\u8f6c\\u53d1(\((\d*?)\))?<\\/a>.*?\\u8bc4\\u8bba(\((\d*?)\))?<\\/a>\\n <\\/span>\\n <a href=\\"(.*?)\\" title=\\".*?" date=\\"(\d{13})\\"')
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
            time.sleep(1)
    def onePage(self,page):
        bodies = dict(xsort = 'hot', page = page, scope = 'ori')
        req = 'http://s.weibo.com/weibo/' + urllib.quote(self.keyword).replace('%','%25') + '&' + urllib.urlencode(bodies)        
        content = self.cookie._request(req, {}, self.header)
        print 'page:'+str(page)
#         print content
        if not self.last_page:
            self.last_page= re.findall(r"value=weibo_page_1' >(\d{1,2})<\\/a>",content)[-1]
        div = self.regex_div.search(content).group(1)
        print div
        lists = self.regex_list.findall(div)
        sss=1
        for i in lists:
            self.onePost(i)
        
        pass
    def onePost(self,content_raw):
        ''' 对一条微博的内容进行处理     '''
        user_raw = self.regex_user.findall(content_raw)[0]
        detail_raw = self.regex_detail.findall(content_raw)[0]
        post_raw = self.regex_post.findall(content_raw)[0]
        user = self._user(user_raw)
        if user is False:
            return
        post = self._post(post_raw)
        detail = self._detail(detail_raw)
        print user['name']+':'+post[0]
        if not self.db.select('post', '*', 'mid="%s"'%detail['mid']):
            self.db.insert('post', mid=detail["mid"], comments=detail["comments"], reposts=detail["reposts"], uid=user["uid"], picture=post[1], text=post[0], time=detail['time'], url=detail['url'], prev_mid='', root_mid=detail['mid'])
        else:
            self.db.update('post', 'mid=%s'%detail['mid'], comments=detail['comments'], reposts=detail['reposts'])

#     def _user(self,raw_data):
#         '''对用户信息进行处理'''
#         user = dict(name=eval('u"%s\"'%raw_data[0]),uid=raw_data[2],profile=raw_data[1].replace(r'\/',r'/'),type=",".join(self._type(raw_data[4])))
#         headers=dict(Host='www.weibo.com',Referer='http://www.weibo.com/u/'+self.uid+'?wvr=5&wvr=5&lf=reg')
#         bodies=dict(_wv='5',type='1',mark='',id=user['uid'],_t='0',__rnd=str(int(time.time()*1000)))
#         user_card = self.cookie._request('http://www.weibo.com/aj/user/cardv5?'+urllib.urlencode(bodies), {}, headers)
#         if user_card[9:14]=='100001':
#             return False
#         hehe=re.findall(r'<em class=\\"W_ico12 ((fe)?male)\\" .*?<\\/em> (.*?) <\\/p>.*?\\/fans\?refer=usercard&wvr=5\\">\\u7c89\\u4e1d<\\/a> (\d*?(\\u4e07|\\u4ebf)?)<\\/li>.*?profile\?refer=usercard&wvr=5\\">\\u5fae\\u535a<\\/a> (\d*?(\\u4e07|\\u4ebf)?)<\\/li>',user_card)[0]
#         followers = eval('u"%s\"'%hehe[3])
#         posts = eval('u"%s\"'%hehe[5])
#         district = eval('u"%s\"'%hehe[2])
#         gender = hehe[0][0].upper()
#         user['followers'] = followers
#         user['district'] = district
#         user['gender'] = gender
#         user['posts'] = posts
#         return user
    
    def _post(self,raw_data):
        ''' 对微博内容进行处理
            return:(微博内容，微博图片名，微博图片url)
        '''
        text=eval('u"%s\"'%self.htmlparser.unescape(re.sub(r'<img src=.*? title=\\\\"|\\\\" type=\\\\"face\\\\" \\\\/>|<.*?>',r'',raw_data[0]).replace(r'\/',r'/')).replace(r'"',r'\"')) #.encode("utf-8")
        if raw_data[2]:
            picture = re.findall(r'\\/thumbnail\\/([\d\w]*?\.\w{3})', raw_data[2])[0].replace(r'thumbnail',r'large')
        else:
            picture = ""
        return (text,picture,raw_data[2].replace(r'\/',r'/').replace(r'thumbnail',r'large'))
    def _detail(self,raw_data):
        '''对微博的细节信息进行处理'''
        mid = raw_data[0]
        reposts = raw_data[2] if raw_data[2] else '0'
        comments = raw_data[4] if raw_data[4] else '0'
        url = raw_data[5].replace(r'\/',r'/')
        t = time.gmtime(int(raw_data[6])/1000+28800)
        ptime = datetime.datetime(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
        return dict(mid=mid,reposts=reposts,comments=comments,url=url,time=ptime)

    def _type(self,data):
        '''对用户类别进行处理'''
        types = []
        if r'class=\"approve\"' in data:
            types.append("Verified_p")
        elif r'class=\"approve_co\"' in data:
            types.append("Verified_co")
        elif r'class=\"ico_club\"' in data:
            types.append("Daren")
        if r'class=\"ico_member\"' in data:
            types.append("Vip")
        return types
        
class Login(object):
    '''处理登陆过程的类'''
    def __init__(self, cookie):
        self.cookie = cookie
        self.user = user_name
        if not self.tryLogin(user_name,pass_word):
            cookie_o = 'SINAGLOBAL=4094117090323.8486.1364265042490; ULV=1366872559761:7:5:2:6733298246961.887.1366872559510:1366532341920; UOR=,,login.sina.com.cn; myuid=2671992203; un=qiaoyq@mail.ustc.edu.cn; SinaRot_wb_r_topic=83; USRUG=usrmdins411_114; USRV5WB=usrmdins311140; _s_tentry=login.sina.com.cn; Apache=6733298246961.887.1366872559510; ULOGIN_IMG=13668731831143; SUS=SID-2671992203-1366875837-JA-mg2vh-d9ac7e5c93a55b953e897d0772486469; SUE=es%3Dfb7901cdc216d34ca4c9ce2a84e66b1c%26ev%3Dv1%26es2%3Da1e2fdb026669f32fc06b0b5387cc413%26rs0%3D6L3jz8%252FQjOUQ4%252Fv3bCemjiUC8%252FV9ykdutM5CAZNrZxYLHKEQzNa5%252BLGclUAZttIztZZS8awWC7AVRmr%252BP277xPeaM3ZDCZ96xHxc%252BmPnOC0ID5PRaJPwRV6vMQuy2o48x0l1TWpl%252Bay97ugO4%252BFV9bEMdEpaHsHfYwv3DHdAUow%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1366875838%26et%3D1366962238%26d%3Dc909%26i%3D9db4%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D4%26st%3D0%26uid%3D2671992203%26user%3Dqiaoyq%2540mail.ustc.edu.cn%26ag%3D4%26name%3Dqiaoyq%2540mail.ustc.edu.cn%26nick%3Dtest_ustc%26fmp%3D%26lcp%3D; ALF=1369467837; SSOLoginState=1366875838; wvr=5'
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
        self.path = dirs+'\\database\\'+filename#r"\weibo2"
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
                name varchar(30)
                time datetime NOT NULL,
                text varchar(200),
                url varchar(50) NOT NULL,
                uid varchar(10) NOT NULL,
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

    
# class Repost(object):
#     '''处理转发关系的类'''
#     def __init__(self,init_url,cookie,db,my_uid):
#         self.url_list = []
#         self.root_url = init_url
#         self.html_parser = HTMLParser.HTMLParser()
#         self.cookie = cookie
#         self.db = db
#         self.my_uid = my_uid
#         self.prev = ''
#         self.root = ''
#         self.run(init_url)
#     
#         
#     def run(self,url):
#         div_post = r'\\"WB_detail\\"(.*?)"\}\)</script>'
#         header1 = {
#                   'Host':'www.weibo.com',
#                   'Referer':'http://www.weibo.com/u/'+self.my_uid+'?wvr=5&'
#                   }
#         try:
#             content = self.cookie._request(url,{},header1)
#         except:
#             return False
#             self.run_ex(url)
#         div = re.search(div_post, content).group(1)
#         uid = re.search(r'fuid=(\d*?)\\"',div).group(1)
#         rid_mid = re.findall(r'[^\w^\d]mid=\\"(\d{14,18})[^\d]', div)
#         mid = rid_mid[-1]
#         root_mid = rid_mid[0]
#         self.root = root_mid
#         rep = re.search(r'forward_counter.*?>转发\(?(\d*?)\)?<',div).group(1)
#         if not rep:
#             rep = '0'
#         com = re.search(r'comment_counter.*?>评论\(?(\d*?)\)?<',div).group(1)
#         if not com:
#             com = '0'
#         text_o = self.html_parser.unescape(re.sub(r'<a .*?>|<\\/a>|<img .*? title=\\"|\\" alt=\\".*?\\" type=\\"face\\" \\/>|<img .*?\.png.*?>|<.*?>',r'',re.search(r'nick-name=\\".*?\\">(.*?)<\\/em>',div).group(1)))
#         try:
#             text = re.search(r'(^.*?)\\/\\/@',text_o).group(1).replace(r'\/',r'/').decode('utf-8')
#         except:
#             text = text_o.replace(r'\/',r'/').decode('utf-8')
#         try:
#             img_url = re.search(r'src=\\"(http:\\/\\/ww\d\.sinaimg\.cn\\/(bmiddle|square)\\/[\w\d\.]*?)\\"',content).group(1).replace(r'\/',r'/').replace(r'bmiddle',r'large').replace(r'square',r'large')
#             img_name = re.search(r'([\w\d]*?\.jpg|[\w\d]*?\.gif)',img_url).group(1)
#         except:
#             img_url = ''
#             img_name = ''  
#         t = time.gmtime(int(re.search(r'date=\\"(\d*?)\\"',div).group(1))/1000+28800) 
#         ptime = datetime.datetime(t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
#         user = self._user(uid)
#         print user['name']+':'+text
#         if not self.db.select('post', '*', 'mid="%s"'%mid):
#             self.db.insert('post', mid=mid, comments=com, reposts=rep, uid=uid, picture=img_name, text=text, time=ptime, url=url, prev_mid=self.prev, root_mid=self.root)
#         else:
#             self.db.update('post', 'mid=%s'%mid, prev_mid=self.prev, reposts=rep)
#         if not self.db.select('user', '*', 'uid=%s'%uid):
#             self.db.insert('user',uid=uid,name=user['name'],followers=user['followers'],type=user['type'],url=user['url'],district=user['district'],gender=user['gender'],posts=user['posts'])
#         else:
#             self.db.update('user', 'uid=%s'%uid, followers=user['followers'], name=user['name'], type=user['type'], posts=user['posts'], gender=user['gender'], district=user['district'])
#         self.prev = mid
#         self.url_list.append((mid,init_url))
#         while len(self.url_list):
#             next = self.url_list.pop(0)
#             print '还有%s条微博在队列中'%str(len(self.url_list))
#             self.prev = next[0]
#             self.get_repost(next[0], next[1])
#         
#         
#         
#     def _user(self,uid):
#         '''对用户信息进行处理'''
#         user={}
#         headers=dict(Host='www.weibo.com',Referer='http://www.weibo.com/u/'+self.my_uid+'?wvr=5&wvr=5&lf=reg')
#         bodies=dict(_wv='5',type='1',mark='',id=uid,_t='0',__rnd=str(int(time.time()*1000)))
#         user_card = self.cookie._request('http://www.weibo.com/aj/user/cardv5?'+urllib.urlencode(bodies), {}, headers)
# #         print user_card
#         if user_card[9:15] !='100000':
#             return False
# #         heihei = re.search(r'fnick=(.*?)(\\"|&)',user_card).group(1)
#         user['name'] = eval('u"%s\"'%re.search(r'title=\\"(.*?)\\"',user_card).group(1))
#         user['url'] = 'http://www.weibo.com/u/'+uid
#         hehe=re.findall(r'(<a target.*?)?<em class=\\"W_ico12 ((fe)?male)\\" .*?<\\/em> (.*?) <\\/p>.*?\\/fans\?refer=usercard&wvr=5\\">\\u7c89\\u4e1d<\\/a> (\d*?(\\u4e07|\\u4ebf)?)<\\/li>.*?profile\?refer=usercard&wvr=5\\">\\u5fae\\u535a<\\/a> (\d*?(\\u4e07|\\u4ebf)?)<\\/li>',user_card)[0]
#         followers = eval('u"%s\"'%hehe[4])
#         posts = eval('u"%s\"'%hehe[6])
#         district = eval('u"%s\"'%hehe[3])
#         gender = hehe[1][0].upper()
#         user['type'] = ','.join(self._type(hehe[0]))
#         user['followers'] = followers
#         user['district'] = district
#         user['gender'] = gender
#         user['posts'] = posts
#         return user
#     def _type(self,data):
#         '''对用户类别进行处理'''
#         types = []
#         if r'class=\"W_ico16 approve\"' in data:
#             types.append("Verified_p")
#         elif r'class=\"W_ico16 approve_co\"' in data:
#             types.append("Verified_co")
#         elif r'class=\"W_ico16 ico_club\"' in data:
#             types.append("Daren")
#         if r'class=\"W_ico16 ico_member\"' in data:
#             types.append("Vip")
#         return types     
#         
#             
#     def get_repost(self,mid,url):
#         header = dict(Host='www.weibo.com',Referer=url)
#         content = self.cookie._request('http://www.weibo.com/aj/mblog/info/big?'+'&'.join(['_wv=5', 'id='+mid, '__rnd='+str(int(time.time()*1000)), '_t=0']),{},header )
#         ss=1
#         try:
#             max_page = re.findall(r'action-type=\\"feed_list_page\\">(\d{1,5})<\\/a>',content)[-1]
#         except:
#             max_page = '1'
#         for i in range(int(max_page),0,-1):
#             self.one_page(str(i),mid)
#         sss=1
#         
#     def one_page(self,page,root_mid):
#         header = dict(Host='www.weibo.com',Referer=self.root_url)
#         self.servertime = int(time.time())
#         content = self.cookie._request('http://www.weibo.com/aj/mblog/info/big?'+'&'.join(['_wv=5', 'id='+root_mid, '__rnd='+str(int(self.servertime*1000)), '_t=0', 'max_id=9999999999999', 'page='+page]),{},header )
#         replist = re.findall(r'mid=\\"(\d{16}).*?usercard=\\"id=(\d*?)\\">.*?uff1a<em>(.*?)<\\/em>.*?\\"S_txt2\\">\((.*?)\).*?&url=(http:[\w\d\\\./]*?)&.*?\\u8f6c\\u53d1\(?(\d*?)\)?<',content)
#         while len(replist):
#             i = replist.pop()
#             user = self._user(i[1])
#             if not user:
#                 continue
#             text_o = self.html_parser.unescape(re.sub(r'<a .*?>|<\\/a>|<img .*? title=\\"|\\" alt=\\".*?\\" type=\\"face\\" \\/>|<img .*?\.png.*?>|<.*?>',r'',i[2]))
#             try:
#                 text = eval('u"%s\"'%re.search(r'(^.*?)\\/\\/@',text_o).group(1).replace(r'\/',r'/').replace(r'"',r'\"'))
#             except:
#                 text = eval('u"%s\"'%text_o.replace(r'\/',r'/').replace(r'"',r'\"'))
#             print user['name']+':'+text
#             url = i[4].replace(r'\/',r'/')     
#             if i[5]:
#                 self.url_list.append((i[0],url))
#                 rep = i[5]
#             else:
#                 rep = '0'
#               
#             pass
#             if not self.db.select('post', '*', 'mid="%s"'%i[0]):
#                 self.db.insert('post', mid=i[0], comments='0', reposts=rep, uid=i[1], picture='', text=text, time=self.time_conv(i[3], self.servertime), url=url, prev_mid=self.prev, root_mid=self.root)
#             else:
#                 self.db.update('post', 'mid=%s'%i[0], prev_mid=self.prev, reposts=rep)
#             if not self.db.select('user', '*', 'uid=%s'%i[1]):
#                 self.db.insert('user',uid=i[1],name=user['name'],followers=user['followers'],type=user['type'],url=user['url'],district=user['district'],gender=user['gender'],posts=user['posts'])
#             else:
#                 self.db.update('user', 'uid=%s'%i[1], followers=user['followers'], name=user['name'], type=user['type'], posts=user['posts'], gender=user['gender'], district=user['district'])
#             
#             
# 
#     def time_conv(self,stime,servertime):
#         '''时间转换'''
#         servtime = time.localtime(float(int(servertime)))
#         if '-' in stime:
#             ftime = time.strptime(stime, '%Y-%m-%d %H:%M')
#         elif r'\u6708' in stime:
#             ftime = time.strptime(str(servtime[0])+' '+stime,'%Y %m\u6708%d\u65e5 %H:%M')
#         elif r'\u4eca\u5929' in stime:
#             ftime = time.strptime(str(servtime[0])+' '+str(servtime[1])+' '+str(servtime[2])+stime,'%Y %m %d\u4eca\u5929 %H:%M')                       
#         else:
#             num = re.search(r'^(.*?)\\u',stime).group(1)
#             ftime = time.localtime(int(servertime)-int(num)*(60 if r'\u5206\u949f' in stime else 1))
#         ptime = datetime.datetime(ftime.tm_year,ftime.tm_mon,ftime.tm_mday,ftime.tm_hour,ftime.tm_min,ftime.tm_sec)
#         return ptime

if __name__ == '__main__':
    db = MyDB('2013_05_06_lichengpengjiuzai')
    cookie=Cookie()
    user = Login(cookie)
    ss = Search('李承鹏 救灾',cookie,db,user.uid)
#     bb=Repost('http://weibo.com/1189591617/ztZeSm2fw',cookie,db,user.uid)
