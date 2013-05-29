#-*- coding=utf-8 -*-

import os,math

def text_cmp(s1,s2):
    max = 0
    len1 = len(s1)
    len2 = len(s2)
    flag = False if len1<len2 else True
    len_min = len1 if flag else len2
    for i in range(abs(len1-len2)+1):
        sum = 0
        for j in range(len1+len2):
            if flag:
                if j+i>=len1 or j>=len2:
                    break
                elif s1[j+i]==s2[j]:
                    sum += 1
            else:
                if j>=len1 or j+i>=len2:
                    break
                elif s1[j]==s2[j+i]:
                    sum += 1
        max = max if max>=sum else sum
    para = 1.0 if flag else -1.0
    result = para*max/(len1+len2)
    return result
    
    
def run(list1):
    for i in range(len(list1)-1):
        if not list1[i]:
            continue
        for j in range(i+1,len(list1)):
            if not list1[j]:
                continue
            cmp = text_cmp(list1[i],list1[j])
            if cmp > 0.3:
                
                
                print '==============================================================='
                print list1[i]
                print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                print list1[j]
                print '==============================================================='
                list1[j] = ''
                continue
            elif cmp < -0.3:
                
                print '==============================================================='
                print list1[i]
                print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
                print list1[j]
                print '==============================================================='
                list1[i] = ''
                break
            
                
if __name__ == '__main__':
    dirs = os.getcwd()
    f1 = open(dirs+r'\\weibodata\\0524.txt','r')
    f2 = open(dirs+r'\\weibodata\\0524_distinct.txt','w')
    list1 = f1.readlines()
    run(list1)
    f2.writelines(list1)
    f1.close()
    f2.close()
    