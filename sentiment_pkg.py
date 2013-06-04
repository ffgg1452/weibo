#coding:utf-8
'''
Created on 2013-4-28

@author: Alvaro
'''
from ctypes import *
import re, os, time, random, math
from sklearn import svm

C_Linear = {'other_0':1.0, 'weibo_0':1.0, 'other_1':1.0, 'weibo_1':1.0}
C_RBF = {'other_0':32.0, 'weibo_0':2.0, 'other_1':2048.0, 'weibo_1':2.0, 'other_2':2.0, 'weibo_2':2.0}
gamma = {'other_0':0.0078125, 'weibo_0':0.125, 'other_1':0.001953125, 'weibo_1':2.0, 'other_2':0.125, 'weibo_2':0.5}


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
        threshold = temp_list[0][2] / 30
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
#         model = []
#         word_list = self.dataset.feature_list.keys()
#         for i in range(len(word_list)):
#             model.append(1.0*self.feature_list[i][1]/self.feature_list[i][0])
        pass
        return (self.dataset.train_stat['sum'], self.dataset.train_stat['positive'], self.feature_list)
    
    def classify(self, trained_model): 
        if not self.test_list:
            print '测试集无效'
            return False
        sum = trained_model[0]
        positive = trained_model[1]
        word_list = trained_model[2]
#         model = trained_model[3]
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
        print p_detected
        print p_all - p_detected
        print n_detected
        print n_all - n_detected
#         for i in range(len(senti_list)):
#             print ''.join([j[:-2] for j in self.test_list[i]])
#             print senti_list[i]
        return senti_list
    
#     


class SupportVM_L(object):
    def __init__(self, dataset, **arg):
        self.dataset = dataset
        self.train_list = self.dataset.train_list
        self.test_list = self.dataset.test_list
        self.feature_list = self.dataset.feature_list
        self.word_list = self.feature_list.keys()
        self.para = arg

    
    def _matrix(self, data_list, flag = False):
        
        matrix_x = [[float(0) for j in self.word_list] for i in range(len(data_list))]
        matrix_y = [float(0) for i in range(len(data_list))]
        for i in range(len(data_list)):
            if data_list[i][1] == 'p':
                matrix_y[i] = 1.0
            elif data_list[i][1] == 'n':
                matrix_y[i] = -1.0
            else:
                continue
            sum = 0
            for s in range(len(self.word_list)):
                
                if self.word_list[s] in data_list[i][0]:
                    matrix_x[i][s] = 1.0
                else:
                    continue
                    matrix_x[i][s] = 0.0
                if flag == True:
                    tf = 1.0 * (data_list[i][0].count(self.word_list[s])) / len(data_list[i][0])
                    idf = math.log(1.0 * (len(self.train_list) + 1)/(self.dataset.feature_list[self.word_list[s]][0]), 2)
                    weight = tf * idf
                    sum += weight ** 2 
                else:
                    weight = 1.0
                matrix_x[i][s] *= weight
            if flag == False or sum == 0:
                continue
            for s in range(len(self.word_list)):
                matrix_x[i][s] *= 1.0 / (sum ** 0.5)
        return (matrix_x, matrix_y)
    def train(self):
        
        matrix = self._matrix(self.dataset.train_list, True)
        fo = open('gen.dat','w')
        out_list = []
        for i in range(len(matrix[1])):
            ss = [str(j+1) + ':' + str(matrix[0][i][j]) for j in range(len(matrix[0][i]))]
            out_list.append(str(matrix[1][i]) + ' ' + ' '.join(ss) + '\n')
        fo.writelines(out_list)
        fo.close()
        if self.para['kernel'] == 'rbf':
            self.svmc = svm.SVC(kernel = 'rbf', C = self.para['C'], gamma = self.para['gamma'])
        else:
            self.svmc = svm.SVC(kernel = 'linear', C = self.para['C'])
        print self.svmc
        self.svmc.fit(matrix[0], matrix[1])
        
        
        pass
    
    def classify(self):
        matrix = self._matrix(self.dataset.test_list, True)
        result = self.svmc.predict(matrix[0])
        p_all = 0
        n_all = 0
        p_detected = 0
        n_detected = 0
        for i in range(len(matrix[1])):
            if matrix[1][i] == 1.0:
                p_all += 1
                if result[i] == 1.0:
                    p_detected += 1
            else:
                n_all += 1
                if result[i] == -1.0:
                    n_detected += 1
        print 1.0 * p_detected / p_all
        print 1.0 * n_detected / n_all
        print 1.0 * p_detected / (n_all - n_detected + p_detected)
        print 1.0 * n_detected / (p_all - p_detected + n_detected)
        print p_detected
        print p_all - p_detected
        print n_detected
        print n_all - n_detected

class SupportVM_N(object):
    def __init__(self, dataset):
        self.dataset = dataset
        self.train_list = self.dataset.train_list
        self.test_list = self.dataset.test_list
        self.feature_list = self.dataset.feature_list
        self.accuracy = 1E-3
        self.C = 32
        self.tolerance = 0.001
        self.alpha = []
        self.w = []
        self.b = float(0)
        self.kcache = {}
        sigma = 2 ** 4
        self.parameters = [sigma]
#         self.kernelName = 'RBF'

        self.kernelName = 'Linear'

    def _matrix(self, dataset):
        train_list = dataset.train_list
        feature_list = dataset.feature_list
        word_list = feature_list.keys()
        dirs = os.getcwd()
        fo = open(dirs + r'\weibodata\gen_train.dat', 'w')
        fo1 = open(dirs + r'\weibodata\gen_test.dat', 'w')
        
        matrix_x = [[0 for j in word_list] for i in range(len(train_list))]
        matrix_x1 = [[0 for j in word_list] for i in range(len(self.test_list))]
        matrix_y = [0 for i in range(len(train_list))]
        for i in range(len(train_list)):
            if self.train_list[i][1] == 'p':
                matrix_y[i] = 1
            elif self.train_list[i][1] == 'n':
                matrix_y[i] = -1
            else:
                continue
            for s in range(len(word_list)):
#                 tf = 1.0 * train_list[i][0].count(word_list[s]) / len(train_list[i][0])
#                 idf = math.log((len(train_list) + 1)/self.dataset.feature_list[word_list[s]][0], 2)
                if word_list[s] in train_list[i][0]:
                    matrix_x[i][s] = 1
                else:
                    matrix_x[i][s] = -1
#                 matrix_x[i][s] *= tf * idf
        out_list = []
        for i in range(len(matrix_y)):
            ss = [str(j+1) + ':' + str(matrix_x[i][j]) for j in range(len(matrix_x[i]))]
            out_list.append(str(matrix_y[i]) + ' ' + ' '.join(ss) + '\n')
        fo.writelines(out_list)
        fo.close()
        for i in range(len(self.test_list)):
            if self.test_list[i][1] == 'p':
                aaaaa = 1
            elif self.test_list[i][1] == 'n':
                aaaaa = -1
            else:
                continue
            print aaaaa
            for s in range(len(word_list)):
#                 tf = 1.0 * train_list[i][0].count(word_list[s]) / len(train_list[i][0])
#                 idf = math.log((len(train_list) + 1)/self.dataset.feature_list[word_list[s]][0], 2)
                if word_list[s] in self.test_list[i][0]:
                    matrix_x1[i][s] = 1
                else:
                    matrix_x1[i][s] = -1
#                 matrix_x[i][s] *= tf * idf
        out_list = []
        for i in range(len(self.test_list)):
            ss = [str(j+1) + ':' + str(matrix_x1[i][j]) for j in range(len(matrix_x1[i]))]
            out_list.append(str(aaaaa) + ' ' + ' '.join(ss) + '\n')
            print out_list[i]
        fo1.writelines(out_list)
        fo1.close()
        return (word_list, matrix_x, matrix_y)

    def DotProduct(self,i1,i2):
        '''To get vector's dot product for training.'''
        dot = float(0)
        for i in range(0,len(self.trainx[0])):
            dot += self.trainx[i1][i] * self.trainx[i2][i]  
        return dot
        
    def Kernel(self):
        '''To get kernel function with configuration for training.

            kernel function includes RBF,Linear and so on.'''      
        if self.kernelName == 'RBF':
            return lambda xi,yi: math.exp((2*self.DotProduct(xi,yi)-self.DotProduct(xi,xi)-self.DotProduct(yi,yi))/(2*float(self.parameters[0])*float(self.parameters[0])))
        elif self.kernelName == 'Linear':
            return lambda xi,yi:self.DotProduct(xi,yi) + float(self.parameters[0])
    def DotVectorProduct(self,v1,v2):
        '''To get vector's dot product for testing.'''
#        if len(v1) != len(v2):
#            print 'The dimensions of two vector should equal'
#            return 0.0
        dot = float(0)
        for i in range(0,len(v1)):
            dot += v1[i] * v2[i]
        return dot
        
    def KernelVector(self, v1, v2):
        '''To get kernel function for testing.'''
        if self.kernelName == 'RBF':
            return math.exp((2*self.DotVectorProduct(v1, v2)-self.DotVectorProduct(v1, v1)-self.DotVectorProduct(v2, v2))/(2*float(self.parameters[0])*float(self.parameters[0])))
        elif self.kernelName == 'Linear':
            return self.DotVectorProduct(v1, v2) + float(self.parameters[0])
 
    def F(self,i1):
        '''To calculate output of an sample.

            return output.'''
        if self.kernelName == 'Linear':
            dot = 0
            for i in range(0,len(self.trainx[0])):
                dot += self.w[i] * self.trainx[i1][i];    
            return dot + self.b

        K = self.Kernel()   
        final = 0.0
        for i in range(0,len(self.alpha)):
            if self.alpha[i] > 0:
                key1 = '%s%s%s'%(str(i1), '-', str(i))
                key2 = '%s%s%s'%(str(i), '-', str(i1))
                if self.kcache.has_key(key1):
                    k = self.kcache[key1]
                elif self.kcache.has_key(key2):
                    k = self.kcache[key2]
                else:
                    k =  K(i1,i)
                    self.kcache[key1] = k
                    
                final += self.alpha[i] * self.trainy[i] * k
        final += self.b
        return final

    def examineExample(self,i1):
        '''To find the first lagrange multipliers.

                then find the second lagrange multipliers.'''
        y1 = self.trainy[i1]
        alpha1 = self.alpha[i1]

        E1 = self.F(i1) - y1

        kkt = y1 * E1

        if (kkt > self.tolerance and kkt > 0) or (kkt <- self.tolerance and kkt < self.C):#not abide by KKT conditions
            if self.FindMaxNonbound(i1,E1):
                return 1
            elif self.FindRandomNonbound(i1):
                return 1
            elif self.FindRandom(i1):
                return 1
        return 0

    def FindMaxNonbound(self,i1,E1):
        '''To find second lagrange multipliers from non-bound.

            condition is maximum |E1-E2| of non-bound lagrange multipliers.'''
        i2 = -1
        maxe1e2 = None
        for i in range(0,len(self.alpha)):
            if self.alpha[i] > 0 and self.alpha[i] < self.C:
                E2 = self.F(i) - self.trainy[i]
                tmp = math.fabs(E1-E2)
                if maxe1e2 == None or maxe1e2 < tmp:
                    maxe1e2 = tmp
                    i2 = i
        if i2 >= 0 and self.StepOnebyOne(i1,i2) :
            return  1              
        return 0

    def FindRandomNonbound(self,i1):
        '''To find second lagrange multipliers from non-bound.

            condition is random of non-bound lagrange multipliers.'''
        k = random.randint(0,len(self.alpha)-1)
        for i in range(0,len(self.alpha)):
            i2 = (i + k)%len(self.alpha)
            if self.alpha[i2] > 0 and self.alpha[i2] < self.C and self.StepOnebyOne(i1,i2):
                return 1
        return 0

    def FindRandom(self,i1):
        '''To find second lagrange multipliers from all.

            condition is random one of all lagrange multipliers.'''
        k = random.randint(0,len(self.alpha)-1)
        for i in range(0,len(self.alpha)):
            i2 = (i + k)%len(self.alpha)
            if self.StepOnebyOne(i1,i2):
                return 1
        return 0


    def W(self,alpha1new,alpha2newclipped,i1,i2,E1,E2, k11, k22, k12):
        '''To calculate W value.'''

        K = self.Kernel()
        alpha1 = self.alpha[i1]
        alpha2 = self.alpha[i2]
        y1 = self.trainy[i1]
        y2 = self.trainy[i2]
        s = y1 * y2
        
        w1 = alpha1new * (y1 * (self.b - E1) + alpha1 * k11 + s * alpha2 * k12)
        w1 += alpha2newclipped * (y2 * (self.b - E2) + alpha2 * k22 + s * alpha1 * k12)
        w1 = w1 - k11 * alpha1new * alpha1new/2 - k22 * alpha2newclipped * alpha2newclipped/2 - s * k12 * alpha1new * alpha2newclipped
        return w1
    
    def StepOnebyOne(self, i1, i2):
        if i1 == i2:
            return 0
        print 'a_', i1, ' and a_', i2
        K = self.Kernel()
        
        alpha1 = self.alpha[i1]
        alpha2 = self.alpha[i2]
        alpha1new = -1.0
        alpha2new = -1.0
        alpha2newclipped = -1.0
        y1 = self.trainy[i1]
        y2 = self.trainy[i2]
        s = y1 * y2
        
        key11 = '%s%s%s'%(str(i1), '-', str(i1))
        key22 = '%s%s%s'%(str(i2), '-', str(i2))
        key12 = '%s%s%s'%(str(i1), '-', str(i2))
        key21 = '%s%s%s'%(str(i2), '-', str(i1))
        if self.kcache.has_key(key11):
            k11 = self.kcache[key11]
        else:
            k11 = K(i1,i1)
            self.kcache[key11] = k11    
            
        if self.kcache.has_key(key22):
            k22 = self.kcache[key22]
        else:
            k22 = K(i2,i2)
            self.kcache[key22] = k22
            
        if self.kcache.has_key(key12):
            k12 = self.kcache[key12]
        elif self.kcache.has_key(key21):
            k12 = self.kcache[key21]
        else:
            k12 = K(i1,i2)
            self.kcache[key12] = k12       
        
        eta = k11 + k22 - 2 * k12
        
        E1 = self.F(i1) - y1        
        E2 = self.F(i2) - y2 
        
        L = 0.0
        H = 0.0
        if y1*y2 == -1:
            gamma = alpha2 - alpha1
            if gamma > 0:
                L = gamma
                H = self.C
            else:
                L = 0
                H = self.C + gamma            

        if y1*y2 == 1:
            gamma = alpha2 + alpha1
            if gamma - self.C > 0:
                L = gamma - self.C
                H = self.C
            else:
                L = 0
                H = gamma
        if H == L:
            return 0
        
        if -eta < 0:
            #to calculate apha2's new value
            alpha2new = alpha2 + y2 * (E1 - E2)/eta
            
            if alpha2new < L:
                alpha2newclipped = L
            elif alpha2new > H:
                 alpha2newclipped = H
            else:
                alpha2newclipped = alpha2new
        else:            
            w1 = self.W(alpha1 + s * (alpha2 - L),L,i1,i2,E1,E2, k11, k22, k12)
            w2 = self.W(alpha1 + s * (alpha2 - H),H,i1,i2,E1,E2, k11, k22, k12)
            if w1 - w2 > self.accuracy:
                alpha2newclipped = L
            elif w2 - w1 > self.accuracy:
                alpha2newclipped = H
            else:
                alpha2newclipped = alpha2  
        
        if math.fabs(alpha2newclipped - alpha2) < self.accuracy * (alpha2newclipped + alpha2 + self.accuracy):
            return 0
        
        alpha1new = alpha1 + s * (alpha2 - alpha2newclipped)
        if alpha1new < 0:
            alpha2newclipped += s * alpha1new
            alpha1new = 0
        elif alpha1new > self.C:
            alpha2newclipped += s * (alpha1new - self.C)
            alpha1new = self.C
        #------------------------end   to move lagrange multipliers.----------------------------
        if alpha1new > 0 and alpha1new < self.C:
            self.b += (alpha1-alpha1new) * y1 * k11 + (alpha2 - alpha2newclipped) * y2 *k12 - E1
        elif alpha2newclipped > 0 and alpha2newclipped < self.C:
            self.b += (alpha1-alpha1new) * y1 * k12 + (alpha2 - alpha2newclipped) * y2 *k22 - E2
        else:
            b1 = (alpha1-alpha1new) * y1 * k11 + (alpha2 - alpha2newclipped) * y2 *k12 - E1 + self.b
            b2 = (alpha1-alpha1new) * y1 * k12 + (alpha2 - alpha2newclipped) * y2 *k22 - E2 + self.b
            self.b = (b1 + b2)/2
        
        if self.kernelName == 'Linear':
            for j in range(0,len(self.trainx[0])):
                self.w[j] += (alpha1new - alpha1) * y1 * self.trainx[i1][j] + (alpha2newclipped - alpha2) * y2 * self.trainx[i2][j]
                
        self.alpha[i1] = alpha1new
        self.alpha[i2] = alpha2newclipped
        
        print 'a', i1, '=',alpha1new,'a', i2,'=', alpha2newclipped
        return 1     
        
    
    def train(self):
        matrix = self._matrix(self.dataset)
        self.word_list = matrix[0]
        self.trainx = matrix[1]
        self.trainy = matrix[2]
        numChanged = 0
        examineAll = 1
        for i in range(0,len(self.trainx)):
            self.alpha.append(0.0)
        for j in range(0, len(self.trainx[i])):
            self.w.append(float(0))
        while numChanged > 0 or examineAll:
            numChanged = 0
#             print 'numChanged =', numChanged
            if examineAll:
                for k in range(0, len(self.trainx)):
                    numChanged += self.examineExample(k)
            else:
                for k in range(0, len(self.trainx)):
                    if self.alpha[k] != 0 and self.alpha[k] != self.C:
                        numChanged += self.examineExample(k)
            print 'numChanged = ', numChanged
            if examineAll == 1:
                examineAll = 0
            elif numChanged == 0:
                examineAll = 1
        return (self.alpha, self.trainx, self.trainy, self.b)
    
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
                sum += trained_model[2][j] * trained_model[0][j] * self.KernelVector(trained_model[1][j], xi)
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
        print p_detected
        print p_all - p_detected
        print n_detected
        print n_all - n_detected
        return senti_list
        

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
        fo = open(dirs + r'\weibodata\gen_test.dat', 'w')
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
#                 tf = 1.0 * train_list[i][0].count(word_list[s]) / len(train_list[i][0])
#                 idf = math.log((len(train_list) + 1)/self.dataset.feature_list[word_list[s]][0], 2)
                if word_list[s] in train_list[i][0]:
                    matrix_x[i][s] = 1
                else:
                    matrix_x[i][s] = -1
#                 matrix_x[i][s] *= tf * idf
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
        gamma = 2 ** -9 # TFIDF:  weibo:2^- other:2^
                        # origin: weibo:2^ -9 other:2^-
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
        C_RBF = 2 ** 5  # TFIDF:  weibo:2 ^  other:
                        # origin: weibo:2 ^ 3 other:2^
        C_Linear = 2 ** 0
        C = C_RBF
#         C = C_Linear
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
#                     if L == H:
#                         continue
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
        print p_detected
        print p_all - p_detected
        print n_detected
        print n_all - n_detected
        return senti_list
    

if __name__ == '__main__':
    global C_Linear, C_RBF, gamma
    dirs = os.getcwd()
    test = SentimentData()
    set = '\weibodata\\'
#     set = '\otherdata\\'
    test.importFromTxt(dirs + set + r'train.txt', dirs + set + r'test.txt')
    test.featureSelect()
        
#     ss = NaiveBayes(test)
#     ss.classify(ss.train())
# 
    tt = SupportVM_L(dataset = test, kernel = 'linear', C = C_Linear['weibo_1'])
    m2 = tt.train()
    tt.classify()
    
#     test.featureSelect()
#     aa = NaiveBayes(test)
#     trained_model = aa.train()
#     aa.classify(trained_model)