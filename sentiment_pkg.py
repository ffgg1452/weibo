#coding:utf-8
'''
Created on 2013-4-28

@author: Alvaro
'''
from ctypes import *
import re, os, time, random

class SentimentData(object):
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
    
    def importFromTxt(self, filename1, filename2):
        f1 = open(filename1, 'r')
        f2 = open(filename2, 'r')
        self.test_list = [self._divide(x[:-1]) for x in f2.readlines()]
        temp = [x[:-1] for x in f1.readlines()]
        for i in temp:
            one = re.search(r'^(.*?)\t(\w)', i)
            if one.group(2) in 'np':
                self.train_list.append([self._divide(one.group(1)), one.group(2)])


    def _divide(self, todo):
        self.dll.ICTCLAS_SetPOSmap(c_int(1))
        outlist = []
        i= todo.encode('utf-8')
        strlen = len(c_char_p(i).value)
        t_buffer = c_buffer(strlen*6)
        self.dll.ICTCLAS_ParagraphProcess(c_char_p(i), c_int(strlen), t_buffer, c_int(0), 1)
        result = [x.decode("utf-8") for x in t_buffer.value.split()]
        for j in result:
            outlist.append(j)
        return outlist
    
    def featureSelect(self):
        sum = 0
        positive = 0
        word_list = {}
        for i in range(len(self.train_list)):
            if self.train_list[i][1] == 'p':
                senti = 1
                positive += 1
            elif self.train_list[i][1] == 'n':
                senti = 0
            else:
                continue
            sum += 1
            already = []
            for j in self.train_list[i][0]:
                if j in already:
                    continue
                already.append(j)
                if j in word_list.keys():
                    word_list[j][0] += 1
                    word_list[j][1] += senti
                else:
                    word_list[j] = [1, senti, 0]
        temp_list = []
        for i in word_list.keys():
            if word_list[i][0] < 3:
                continue
            a = word_list[i][1]
            b = word_list[i][0] - word_list[i][1]
            c = positive - a
            d = sum - positive - b
            word_list[i][2] = (a * d - b * c) ** 2 / ((a + b) * (c + d))
            temp_list.append(word_list[i] + [i])
        aa = temp_list.sort(key = lambda x:x[2], reverse = True)
        feature_len = 1000 if len(temp_list) > 1000 else len(temp_list)
        self.feature_list = temp_list[:feature_len]
        ss = 1
 
class NaiveBayes(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.train_list = self.dataset.train_list
        self.test_list = self.dataset.test_list
        self.feature_list = self.dataset.feature_list
    def train(self):
        if not self.train_list:
            print '训练集无效'
            return False
        word_list = {}
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
            for j in div_1:
                if j in word_list.keys():
                    word_list[j][0] += 1
                    word_list[j][1] += senti
                else:
                    word_list[j] = [1, senti]
        print len(word_list)
        return (sum, positive, word_list)
    
    def classify(self, trained_model): 
        if not self.test_list:
            print '测试集无效'
            return False
        sum = trained_model[0]
        positive = trained_model[1]
        word_list = trained_model[2]
        p_positive = 1.0*positive/sum
        senti_list = []
        for i in self.test_list:
            senti_p = 1
            senti_n = 1
            div_2 = self.dataset._divide(i)
            for j in div_2:
                if j in word_list.keys():
                    inc_p = 1.0 * word_list[j][1] / positive
                    inc_n = 1.0 * (word_list[j][0] - word_list[j][1]) / (sum - positive)
                    senti_p *= inc_p
                    senti_n *= inc_n
            senti_result = (senti_p * p_positive - senti_n * (1 - p_positive))
            senti_list.append(senti_result)
        for i in range(len(senti_list)):
            print self.test_list[i]
            print senti_list[i]
        return senti_list
#     

class SupportVM(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.train_list = dataset.train_list
        self.test_list = dataset.test_list
        self.boundAlpha = []
        self.b = 0.0
        
    def _initKernel(self, x):
        k = [([0])*len(x) for i in range(len(x))]
        for i in range(len(x)):
            for j in range(len(x)):
                sum = 0
                for t in x[0].keys():
                    sum += x[i][t]*x[j][t]
                k[i][j] = sum
        return k                     

    def _matrix(self, train_list):
        word_list = {}
        matrix_x = [{} for i in range(len(train_list))]
        matrix_y = [0 for i in range(len(train_list))]
        sum = 0
        positive = 0
        for i in range(len(self.train_list)):
            if self.train_list[i][1] == 'p':
                senti = 1
                positive += 1
                matrix_y[i] = 1
            elif self.train_list[i][1] == 'n':
                senti = 0
                matrix_y[i] = 0
            else:
                continue
            sum += 1
            for s in word_list.keys():
                matrix_x[i][s] = 0
            div_1 = self.dataset._divide(self.train_list[i][0])
            for j in div_1:
                matrix_x[i][j] = 1
                if j in word_list.keys():
                    word_list[j][0] += 1
                    word_list[j][1] += senti
                    
                else:
                    word_list[j] = [1, senti]
                    for t in range(i):
                        matrix_x[t][j] = 0
                        
        print len(word_list)
        for i in matrix_x:
            print len(i)
        return (sum, positive, word_list, matrix_x, matrix_y)
         
    def _getE(self, i):
        sum = 0
        for j in range(len(self.x)):
            sum += self.alpha[j] * self.y[j]*self.kernel[j][i]
        return sum + self.b - self.y[i]
        
    def _findMax(self, e_i, set):
        max = 0
        max_index = -1
        for j in range(len(set)):
            e_j = self._getE(j)
            if (abs(e_i - e_j)>max):
                max = abs(e_i - e_j)
                max_index = j
        return max_index
    
    def _randomSelect(self, i):
        while True:
            j = random.randint(0, len(self.x))
            if i != j:
                break
        return j

    
    def train(self):
        if not self.train_list:
            print '训练集无效'
            return False
        elif not self.test_list:
            print '测试集无效'
            return False
        
        matrix = self._matrix(self.train_list)
        self.x = matrix[3]
        self.y = matrix[4]
        index = self.x[0].keys()
        self.kernel = self._initKernel(self.x)
        C = 1.0
        tol = 0.01
        max_passes = 5
        self.alpha = [0 for i in range(len(x))]
        passes = 0
        
        while passes < max_passes:
            alpha_changed = 0
            for i in range(len(x)):
                e_i = self._getE(i)
                
                if (y[i] * e_i < -tol and self.alpha[i]<C) or (y[i] * e_i > tol and self.alpha[i]>0):
                    if len(bound_alpha)>0:
                        j = self._findMax(e_i, boundAlpha)
                    else:
                        j = self._randomSelect(i)
                e_j = self._getE(j)
                oldai = self.alpha[i]
                oldaj = self.alpha[j]
                
                if (self.y[i] != self.y[j]):
                    L = max([0, self.alpha[j] - self.alpha[i]])
                    H = min([C, C - self.alpha[i] + self.alpha[j]])
                else:
                    L = max([0, self.alpha[i] + self.alpha[i] - C])
                    H = min([0, self.alpha[i] + self.alpha[j]])
                eta = 2.0 * self.kernel[i][j] - self.kernel[i][i] - self.kernel[j][j]
                
                if eta >= 0:
                    continue
                
                self.alpha[j] = self.alpha[j] - self.y[j] * (e_i - e_j) / eta
                if 0 < self.alpha[j] and self.alpha[j] < C:
                    self.boundAlpha.append(j)
                
                if self.alpha[j] < L:
                    self.alpha[j] = L
                elif self.alpha[j] > H:
                    self.alpha[j] = H
                    
                if abs(self.alpha[j] - oldaj) < 1e-5:
                    continue
                
                self.alpha[i] = self.alpha[i] + self.y[i] * self.y[j] * (oldaj - self.alpha[j])
                if 0 < self.alpha[i] and self.alpha[i] < C:
                    self.boundAlpha.append(i)
                    
                b1 = self.b - e_i - self.y[i] * (self.alpha[i] - oldai) * self.kernel[i][i] - self.y[j] * (self.alpha[j] - oldaj) * self.kernel[i][j]
                b2 = self.b - e_j - self.y[i] * (self.alpha[i] - oldai) * self.kernel[i][j] - self.y[j] * (self.alpha[j] - oldaj) * self.kernel[j][j]
                
                if 0 < self.alpha[i] and self.alpha[i] < C:
                    self.b = b1
                elif 0 < self.alpha[j] and self.alpha[j] < C:
                    self.b = b2
                else:
                    self.b = (b1 + b2) / 2
                
                num_changed_alphas += 1
        if num_changed_alphas == 0:
            passes += 1
        else:
            passes = 0
        return (self.alpha, self.y, self.b)
            
    def classify(self, trained_model):
        senti_list = []
        for i in range(len(self.test_list)):
            length = len(trained_model[1])
            sum = 0
            for j in range(length):
                sum += trained_model[1][j] * trained_model[0][j] * self.kernel[j][i]
            sum += trained_model[2]
            senti_list.append(object)
        return senti_list
        
                    

if __name__ == '__main__':
    dirs = os.getcwd()
    test = SentimentData()
    test.importFromTxt(dirs + r'\weibodata\2013_05_08_tagged.txt', dirs + r'\weibodata\untagged_post_distinct_test.txt')
    test.featureSelect()