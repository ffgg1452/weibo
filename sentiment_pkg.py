#coding:utf-8
'''
Created on 2013-4-28

@author: Alvaro
'''
from ctypes import *
import re, os, time, random, math



class SentimentData(object):
    def __init__(self):
        self.train_list = []
        self.test_list = []
        self.dll = cdll.LoadLibrary("ICTCLAS50.dll")
        try:
            self.dll.ICTCLAS_Init(c_char_p("."))
        except:
            print '初始化分词工具失败'
            exit(0)
        print '初始化分词工具成功'
    
    def importFromTxt(self, filename1, filename2):
        f1 = open(filename1, 'r')
        f2 = open(filename2, 'r')
#         self.test_list = [self._divide(x[:-1]) for x in f2.readlines()]
        temp = [x[:-1] for x in f1.readlines()]
        for i in temp:
            one = re.search(r'^(.*?)\t(\w)', i)
            if one.group(2) in 'np':
                self.train_list.append([self._divide(one.group(1)), one.group(2)])
        temp = [x[:-1] for x in f2.readlines()]
        for i in temp:
            one = re.search(r'^(.*?)\t(\w)', i)
            if one.group(2) in 'np':
                self.test_list.append([self._divide(one.group(1)), one.group(2)])
        print '导入数据文件成功'        


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
        print '开始选择特征'
        
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
            word_list[i][2] = 1.0 * (a * d - b * c) ** 2 / ((a + b) * (c + d))
            temp_list.append(word_list[i] + [i])
        aa = temp_list.sort(key = lambda x:x[2], reverse = True)
        threshold = temp_list[0][2] / 50
        print temp_list[-1][2]
        for i in range(len(temp_list)):
            if temp_list[i][2] < threshold:
                break
        feature_len = i
#         feature_len = 400 if len(temp_list) > 400 else len(temp_list)
        self.feature_list = {}
        for i in temp_list[:feature_len]:
            self.feature_list[i[3]] = i[0:3]
        self.train_stat = {'sum':sum, 'positive':positive, 'negative':sum-positive}
        ss = 1
        
 
class NaiveBayes(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.train_list = self.dataset.train_list
        self.test_list = self.dataset.test_list
        self.feature_list = self.dataset.feature_list
#     def train(self):
#         if not self.train_list:
#             print '训练集无效'
#             return False
#         word_list = {}
#         sum = 0
#         positive = 0
#         for i in range(len(self.train_list)):
#             if self.train_list[i][1] == 'p':
#                 senti = 1
#                 positive += 1
#             elif self.train_list[i][1] == 'n':
#                 senti = 0
#             else:
#                 continue
#             sum += 1
#             div_1 = self._divide(self.train_list[i][0])
#             for j in div_1:
#                 if j in word_list.keys():
#                     word_list[j][0] += 1
#                     word_list[j][1] += senti
#                 else:
#                     word_list[j] = [1, senti]
#         print len(word_list)
#         return (sum, positive, word_list)
#     
    def train(self):
        
        pass
        return (self.dataset.train_stat['sum'], self.dataset.train_stat['positive'], self.feature_list)
    
    def classify(self, trained_model): 
        if not self.test_list:
            print '测试集无效'
            return False
        sum = trained_model[0]
        positive = trained_model[1]
        word_list = trained_model[2]
        p_positive = 1.0*positive/sum
        senti_list = []
        p_all = 0
        n_all = 0
        p_detected = 0
        n_detected = 0
        for i in self.test_list:
            senti_p = 1
            senti_n = 1
            div_2 = i[0]
            if i[1] == 'p':
                p_all += 1
            elif i[1] == 'n':
                n_all += 1
            already = []
            for j in div_2:
                if j in word_list.keys() and j not in already:
                    already.append(j)
                    inc_p = 1.0 * word_list[j][1] / positive
                    inc_n = 1.0 * (word_list[j][0] - word_list[j][1]) / (sum - positive)
                    senti_p *= inc_p
                    senti_n *= inc_n
            senti_result = (senti_p * p_positive - senti_n * (1 - p_positive))
            senti_list.append(senti_result)
            if senti_result > 0 and i[1] == 'p':
                p_detected += 1
            if senti_result < 0 and i[1] == 'n':
                n_detected += 1
        print 1.0 * p_detected / p_all
        print 1.0 * n_detected / n_all
        print 1.0 * p_detected / (n_all - n_detected + p_detected)
        print 1.0 * n_detected / (p_all - p_detected + n_detected)
#         for i in range(len(senti_list)):
#             print ''.join([j[:-2] for j in self.test_list[i]])
#             print senti_list[i]
        return senti_list
    
#     

class SupportVM(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.train_list = dataset.train_list
        self.test_list = dataset.test_list
        self.bound_alpha = []
        self.b = 0.0
        
    def _initKernel(self, x):
        k = [([0])*len(x) for i in range(len(x))]
        for i in range(len(x)):
            for j in range(len(x)):
                if i>j:
                    k[i][j] = k[j][i]
                    continue
                else:
                    k[i][j] = self._kernelRBF(x[i], x[j])
#                     k[i][j] = self._kernelLinear(x[i], x[j])
#             print '第'+str(i)+'行'
        return k                     

    def _matrix(self, dataset):
        train_list = dataset.train_list
        feature_list = dataset.feature_list
        word_list = feature_list.keys()
        dirs = os.getcwd()
        fo = open(dirs + r'\weibodata\gen_train.dat', 'w')
        matrix_x = [[0 for j in word_list] for i in range(len(train_list))]
        matrix_y = [0 for i in range(len(train_list))]
        for i in range(len(train_list)):
            if self.train_list[i][1] == 'p':
                matrix_y[i] = 1
            elif self.train_list[i][1] == 'n':
                matrix_y[i] = -1
            else:
                continue
            for s in range(len(word_list)):
                tf = 1.0 * train_list[i][0].count(word_list[s]) / len(train_list[i][0])
                idf = math.log((len(train_list) + 1)/self.dataset.feature_list[word_list[s]][0], 2)
                if word_list[s] in train_list[i][0]:
                    matrix_x[i][s] = 1
                else:
                    matrix_x[i][s] = -1
                matrix_x[i][s] *= tf * idf
        out_list = []
        for i in range(len(matrix_y)):
            ss = [str(j+1) + ':' + str(matrix_x[i][j]) for j in range(len(matrix_x[i]))]
            out_list.append(str(matrix_y[i]) + ' ' + ' '.join(ss) + '\n')
        fo.writelines(out_list)
        fo.close()
        return (word_list, matrix_x, matrix_y)
         
    def _getE(self, i):
        sum = 0
        for j in range(len(self.x)):
            sum += self.alpha[j] * self.y[j] * self.kernel[j][i]
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
            j = random.randint(0, len(self.x)-1)
            if i != j:
                break
        return j
    
    def _kernelRBF(self, x1, x2):
        gamma = 8.0
        sum = 0.0
        for i in range(len(x1)):
            sum += (x1[i] - x2[i]) ** 2
        return math.exp(-1.0 * sum * gamma)
            
    def _kernelLinear(self, x1, x2):
        sum = 0
        for i in range(len(x1)):
            sum += x1[i]*x2[i]
        return sum
    
    def train(self):
        if not self.train_list:
            print '训练集无效'
            return False
        elif not self.test_list:
            print '测试集无效'
            return False
        print '开始训练SVM。。。'
        matrix = self._matrix(self.dataset)
        self.x = matrix[1]
        self.y = matrix[2]
        index = matrix[0]
        self.kernel = self._initKernel(self.x)
        C_RBF = 8.0
        C_Linear = 2 ** -5
        C = C_RBF
        tol = 0.01
        max_passes = 5
        self.alpha = [0 for i in range(len(self.x))]
        passes = 0
        
        while passes < max_passes:
            alpha_changed = 0
            for i in range(len(self.x)):
                e_i = self._getE(i)
                
                if (self.y[i] * e_i < -tol and self.alpha[i]<C) or (self.y[i] * e_i > tol and self.alpha[i]>0):
                    if len(self.bound_alpha)>0:
                        j = self._findMax(e_i, self.bound_alpha)
                    else:
                        j = self._randomSelect(i)
                    e_j = self._getE(j)
                    oldai = self.alpha[i]
                    oldaj = self.alpha[j]
                    
                    if (self.y[i] != self.y[j]):
                        L = max([0, self.alpha[j] - self.alpha[i]])
                        H = min([C, C - self.alpha[i] + self.alpha[j]])
                    else:
                        L = max([0, self.alpha[j] + self.alpha[i] - C])
                        H = min([0, self.alpha[i] + self.alpha[j]])
                    if L == H:
                        continue
                    eta = 2.0 * self.kernel[i][j] - self.kernel[i][i] - self.kernel[j][j]
                    
                    if eta >= 0:
                        
                        continue
                    
                    self.alpha[j] = self.alpha[j] - self.y[j] * (e_i - e_j) / eta
                    if 0 < self.alpha[j] and self.alpha[j] < C and j not in self.bound_alpha:
                        self.bound_alpha.append(j)
                    
                    if self.alpha[j] < L:
                        self.alpha[j] = L
                    elif self.alpha[j] > H:
                        self.alpha[j] = H
                    diff = abs(self.alpha[j] - oldaj)    
                    if abs(self.alpha[j] - oldaj) < 1e-5:
                        continue
                    
                    self.alpha[i] = self.alpha[i] + self.y[i] * self.y[j] * (oldaj - self.alpha[j])
                    if 0 < self.alpha[i] and self.alpha[i] < C and i not in self.bound_alpha:
                        self.bound_alpha.append(i)
                        
                    b1 = self.b - e_i - self.y[i] * (self.alpha[i] - oldai) * self.kernel[i][i] - self.y[j] * (self.alpha[j] - oldaj) * self.kernel[i][j]
                    b2 = self.b - e_j - self.y[i] * (self.alpha[i] - oldai) * self.kernel[i][j] - self.y[j] * (self.alpha[j] - oldaj) * self.kernel[j][j]
                    
                    if 0 < self.alpha[i] and self.alpha[i] < C:
                        self.b = b1
                    elif 0 < self.alpha[j] and self.alpha[j] < C:
                        self.b = b2
                    else:
                        self.b = (b1 + b2) / 2
                    
                    alpha_changed += 1
            if alpha_changed == 0:
                passes += 1
            else:
                passes = 0
        return (self.alpha, self.x, self.y, self.b)
            
    def classify(self, trained_model):
        print '开始测试SVM。。。'
        senti_list = []
        p_all = 0
        n_all = 0
        p_detected = 0
        n_detected = 0
        for i in range(len(self.test_list)):
            length = len(trained_model[1])
            div = self.test_list[i][0]
            sum = 0
            xi = []
            for t in self.dataset.feature_list.keys():
                if t in div:
                    xi.append(1)
                else:
                    xi.append(0)
            for j in range(length):
                sum += trained_model[2][j] * trained_model[0][j] * self._kernelRBF(trained_model[1][j], xi)
#                 sum += trained_model[2][j] * trained_model[0][j] * self._kernelLinear(trained_model[1][j], xi)
            sum += trained_model[3]
            if self.test_list[i][1] == 'p':
                p_all += 1
                if sum > 0:
                    p_detected += 1
            elif self.test_list[i][1] == 'n':
                n_all += 1
                if sum < 0:
                    n_detected += 1
                
            senti_list.append(sum)
        print 1.0 * p_detected / p_all
        print 1.0 * n_detected / n_all
        print 1.0 * p_detected / (n_all - n_detected + p_detected)
        print 1.0 * n_detected / (p_all - p_detected + n_detected)
        return senti_list
    

if __name__ == '__main__':
    dirs = os.getcwd()
    test = SentimentData()
    set = '\weibodata\\'
#     set = '\otherdata\\'
    test.importFromTxt(dirs + set + r'train.txt', dirs + set + r'test.txt')
    test.featureSelect()
        
#         ss = NaiveBayes(test)
#         ss.classify(ss.train())
# 
    tt = SupportVM(test)
    m2 = tt.train()
    tt.classify(m2)
    
#     test.featureSelect()
#     aa = NaiveBayes(test)
#     trained_model = aa.train()
#     aa.classify(trained_model)