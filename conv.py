# -*- coding=utf-8 -*-
import re,os,codecs

def run():
    dirs = os.getcwd()
    filename = 'lichengpengzhangpeng_ori_post.txt'
    fp1 = file(dirs+'\\weibodata\\'+filename,'r')
    fp2 = file(dirs+'\\sentiment\\untagged\\'+filename.replace('post', 'untagged'),'w')
    buffers = fp1.readlines()
    buffers.pop(0)
    outlist = [(re.search(r'^.*?\t.*?\t.*?\t.*?\t.*?\t(.*?)\t',i).group(1).decode('utf-8')+u'\n').encode('utf-8') for i in buffers]

    fp2.writelines(outlist)
    fp1.close()
    fp2.close()

if __name__ == '__main__':
    run()
