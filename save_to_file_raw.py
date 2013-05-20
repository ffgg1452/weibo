# -*- coding=utf-8 -*-
'''
Created on 2013-4-25

@author: Alvaro
'''
import sqlite3
import codecs
import os

def run():
    dir = os.getcwd()
    filename = dir+'\\weibodata\\'+'untagged_%s.txt'
    
    con = sqlite3.connect(dir+'\\database\\'+'\\2013_05_06_lichengpengjiuzai.sqlite3')
    cur = con.cursor()
    sql = 'select * from %s;'
    tbl = {'post':['mid','time','text','url','name']}
#            'user':['url','followers','type','name','uid','gender','district','posts'],
#            'picture':['path','filename']}        
    tbl_seq = tbl.keys()
    for i in tbl_seq:
        fp1 = codecs.open(filename%i,'w','utf-8')
#         quote = [eval('\'\"%s\"\''%x) for x in tbl[i]]
        sss = ['\"%s\" as %s'%(tbl[i][y],tbl[i][y]) for y in range(len(tbl[i]))]
        sql = r'select %s from %s;'%(','.join(tbl[i]),i) 
        cur.execute(sql)
        list1 = cur.fetchall()
      #  cur.execute("select 'mid' as mid,'time' as time,'comments' as comments,'reposts' as reposts,'picture' as picture,'text' as text,'url' as url,'uid' as uid,'prev_mid' as prev_mid,'root_mid' as root_mid union all select  from posts"
        for j in list1:
            line = j[2]+'\r\n'
    #        print line
            fp1.write(line)
                        
        fp1.close()
    
    cur.close()
    con.close()

if __name__ == '__main__':
    run()