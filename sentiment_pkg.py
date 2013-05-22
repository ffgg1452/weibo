#coding:utf-8
'''
Created on 2013-4-28

@author: Alvaro
'''
from ctypes import *
import re,os,time

class Sentiment(object):
    def __init__(self):
        self.train_list = []
        self.test_list = []
        self.dll = cdll.LoadLibrary("ICTCLAS50.dll")
        try:
            self.dll.ICTCLAS_Init(c_char_p("."))
        except:
            print 'Init FAIL!'
            exit(0)
        print 'Init SUCCESS!'
    
    def importFromTxt(self,filename1,filename2):
        f1 = open(filename1, 'r')
        f2 = open(filename2, 'r')
        self.test_list = [x[:-1] for i in f2.readlines()]
        temp = [x[:-1] for i in f1.readlines()]
        for i in temp:
            one = re.search(r'^(.*?)\t(\w)')
            self.train_list.append([one.group(1), one.group(2)])
    
    def _divide(self,todo):
        self.dll.ICTCLAS_SetPOSmap(c_int(1))
        outlist = []
        i= todo.encode('utf-8')
        strlen = len(c_char_p(i).value)
        t_buffer = c_buffer(strlen*6)
        self.dll.ICTCLAS_ParagraphProcess(c_char_p(i),c_int(strlen),t_buffer,c_int(0),1)
        result = [x.decode("utf-8") for x in t_buffer.value.split()]
        for j in result:
            print len(j)
            if (j[-1] in u'nvfadye' and len(j)>3) or (j[-1] == 'w'):
                outlist.append(j)
        return outlist
    
    def naiveBayes(self): 
        if not self.train_list:
            print '训练集无效'
            return False
        elif not self.test_list:
            print '测试集无效'
            return False
        word_list={}
        sum = 0
        positive = 0
        for i in range(len(self.train_list)):
            if self.train_list[i][1] == 'p':
                senti = 1
                positive += 1
            elif self.train_list[i][1] == 'n':
                senti = 0
            else:
                continue
            sum += 1
            div_1 = self._divide(self.train_list[i][0])
            for j in div:
                if j in wordlist.keys():
                    wordlist[j][0] += 1
                    wordlist[j][1] += senti
                else:
                    wordlist[j] = [1,senti]
        p_positive = 1.0*positive/sum
        senti_list = []
        for i in self.test_list:
            senti_p = 1
            senti_n = 1
            div_2 = self._divide(i)
            for j in div_2:
                if j in word_list.keys():
                    inc = 1.0*word_list[j][2]
                    senti_p *= inc
                    senti_n *= 1-inc
            senti_result = (senti_p*p_positive - senti_n*(1-p_positive))
            senti_list.append(senti_result)
        return senti_list
        
#         
#     def count(self, textlist, sentilist):
#         wordlist={}
#         sum = 0
#         positive = 0
#         for i in range(len(textlist)):
#             if sentilist[i]=='p':
#                 senti = 1
#                 positive += 1
#             elif sentilist[i]=='n':
#                 senti = 0
#             else:
#                 continue
#             sum += 1
#             for j in textlist[i]:
#                 word_temp = re.search("^(.*?)/(\w)",j)
#                 word_text = word_temp.group(1)
#                 if len(word_text) == 1:
#                     continue
#                 word_char = word_temp.group(2)
#                 if j in wordlist.keys():
#                     wordlist[j][1]+=1
#                     wordlist[j][2]+=senti
#                 else:
#                     wordlist[j]=[word_char,1,senti]
#                     
#         return (wordlist,1.0*positive/sum)
# 
#     def judge(self, word_list_o, test_list):
#         word_list = word_list_o[0]
#         p_positive = word_list_o[1]
#         senti_list=[]
#         word_list_trim = {}
#         for i in word_list.keys():
#             if word_list[i][0][0] in u'nvfawdye' and len(i)>1:
#                 word_list_trim[i] = word_list[i]
#                 
#         for i in test_list:
#             senti_p = 1
#             senti_n = 1
#             for j in i:
#                 if j in word_list.keys():
#                     temp = word_list[j]
#                     inc = 1.0*word_list[j][2]/word_list[j][1]
#                     senti_p *= inc
#                     senti_n *= 1-inc
#             senti = (senti_p*p_positive-senti_n*(1-p_positive))    
#             senti_list.append(senti)
#         return senti_list
    
    def run(self, testlist):
        dirs = os.getcwd()
    #     ss = divide([u'在经历了商代的繁荣和西周的鼎盛后，青铜作为礼器的尊贵地位终于被动摇。公元前四世纪前后铁器出现，学术界将此定义为青铜时代的结束。但这个结束绵延又漫长。接下来整整一千年间，青铜器与铁器一直共存，虽然两者此消彼涨，但青铜把握了最后时机，为自己浇铸了一段华丽的谢幕。'])
        filein_tagged = file(dirs+'\\sentiment\\tagged\\2013_05_08_tagged.txt','r')
        filein_untagged = file(dirs+'\\sentiment\\untagged\\lichengpengzhangpeng_ori_untagged.txt','r')
    #     out = file(dirs+'\\sentiment\\result.txt','w')
        list1 = filein_tagged.readlines()
    #     ll = filein_untagged.readlines()
        list2 = [i[:-1] for i in filein_untagged.readlines()]
    
        text_list = []
        senti_list = []
        for i in list1:
            try:
                temp = re.search(r'^(.*?)\t([pcn])',i)
            except:
                pass
            try:
                text_list.append(temp.group(1))
            except:
                pass
            senti_list.append(temp.group(2))
        div_list1 = divide(text_list)
        div_list2 = divide(list2)#testlist)
        word_list = count(div_list1,senti_list) 
        result = judge(word_list,div_list2)
        for i in range(len(result)):
    #         if result[i]<0:
    #             print list2[i]
            print list2[i]+'\t'+str(result[i])+'\n'
    #         out.write(list2[i]+'\t'+str(result[i])+'\n')
        return result

if __name__ == '__main__':
    a=u'@李承鹏 接下来跟你唠唠你小肚鸡肠的问题。你一个老爷们（当然你自己可能觉得你是老娘们），从26号开始，一直唧唧歪歪的说那几顶帐篷的事儿，没完没了的连说了这有5、6天了吧？你还是个男人么？男人有你这么磨叨的吗？都没人搭理你了，你还一直没完没老的磨叨，你是心理有病吗？'
    test = Sentiment()
    test._divide(a)
#     run([])
#     dirs = os.getcwd()
# #     ss = divide([u'在经历了商代的繁荣和西周的鼎盛后，青铜作为礼器的尊贵地位终于被动摇。公元前四世纪前后铁器出现，学术界将此定义为青铜时代的结束。但这个结束绵延又漫长。接下来整整一千年间，青铜器与铁器一直共存，虽然两者此消彼涨，但青铜把握了最后时机，为自己浇铸了一段华丽的谢幕。'])
#     filein_tagged = file(dirs+'\\sentiment\\tagged\\zrs_0504_tagged.txt','r')
#     filein_untagged = file(dirs+'\\sentiment\\untagged\\yaanjiuyuan_untagged.txt','r')
#     out = file(dirs+'\\sentiment\\result.txt','w')
#     list1 = filein_tagged.readlines()
#     list2 = [i[:-1] for i in filein_untagged.readlines()]
# 
#     text_list = []
#     senti_list = []
#     for i in list1:
#         temp = re.search(r'^(.*?)\t([pcn])',i)
#         text_list.append(temp.group(1))
#         senti_list.append(temp.group(2))
#     div_list1 = divide(text_list)
#     div_list2 = divide(list2)
#     word_list = count(div_list1,senti_list) 
#     result = judge(word_list,div_list2)
#     for i in range(len(result)):
#         if result[i]<0:
#             print list2[i]
#         out.write(list2[i]+'\t'+str(result[i])+'\n')
#     print [str(i) for i in result]
#     out.close()