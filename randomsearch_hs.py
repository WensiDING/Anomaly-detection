import random as rd
import time
import pandas as pd
import numpy as np
from sklearn import metrics
from scipy.stats import randint as sp_randint
from itertools import combinations
from sklearn.base import BaseEstimator
from sklearn.grid_search import RandomizedSearchCV
from collections import defaultdict
from sklearn.preprocessing import binarize

inputPath = "/home/wensi/workspace/tryout/result.csv"
labelPath = "/home/wensi/workspace/tryout/label.csv"
outputPath = "/home/wensi/workspace/tryout/random_hs.csv"
dimension = 6
num_iter = 20
num_cv = 3
## build a dictionary for all the combination of variables(at least two variables)
items = range(dimension)
count = 0
variables = {}
for i in range(2,dimension+1):
    for var in combinations(items,i):
        variables[count]=var
        count+=1

tuned_params = {'maxDepth':sp_randint(3,15),'psi':sp_randint(200,300),'numTree':sp_randint(10,30),'Vars':sp_randint(0,count)}

with open(outputPath,"a") as myfile:
    class ModeleTree(BaseEstimator):
        sizeLimit = 25
        rd.seed(10)
        def __init__(self,maxDepth=3, psi = 250, numTree = 25,Vars=0):
            self.maxDepth = maxDepth
            self.psi = psi
            self.numTree = numTree
            self.Vars = Vars
            self.dim = len(variables[Vars])

        def tree(self): return defaultdict(self.tree)

        def buildSingleHS_Tree(self,root,mins,maxs,m,n):
            if m==self.maxDepth:
                root[m][n]=[0,0,0,0]
            else:
                q = int(round((self.dim-1)*rd.random()))
                p = (maxs[q]+mins[q])/2
                tmp = maxs[q]
                maxs[q] = p
                self.buildSingleHS_Tree(root,mins,maxs,m+1,2*n-1)
                maxs[q] = tmp
                mins[q] = p
                self.buildSingleHS_Tree(root,mins,maxs,m+1,2*n)
                root[m][n]=[q,p,0,0]
        def UpdateMass(self,root,x,m,n,refWindow):
            val = root[m][n]
            if refWindow:
                val[2]+=1
            else:
                val[3]+=1
            if m < self.maxDepth:
                q = val[0]
                p = val[1]
                if x[q] < p:
                    self.UpdateMass(root,x,m+1,2*n-1,refWindow)
                else:
                    self.UpdateMass(root,x,m+1,2*n,refWindow)
        def UpdateTree(self,root):
            m = 0
            n = 0
            while m<= self.maxDepth:
                while n <= 2**m:
                    val = root[m][n]
                    val[2] = val[3]
                    val[3] = 0
                    n+=1
                n=1
                m+=1
        def Score(self,x,root):
            m=0
            n=1
            while(m<self.maxDepth and root[m][n][2]>self.sizeLimit):
                q = root[m][n][0]
                p = root[m][n][1]
                m+=1
                if x[q]<p :
                    n = 2*n-1
                else:
                    n= 2*n
            return root[m][n][2]*(2**m)
        def hs_tree(self,psi,numTree,data):
            data = data[:,variables[self.Vars]]
            setTrees = []
            scores = []
            for i in range(numTree):
                setTrees.append(self.tree())
                mins = []
                maxs = []
                for j in range(self.dim):
                    s = rd.uniform(0,1)
                    mins.append(s-2*max(s,1-s))
                    maxs.append(s+2*max(s,1-s))
                self.buildSingleHS_Tree(setTrees[i],mins,maxs,0,1)
            for i in range(numTree):
                root = setTrees[i]
                for j in range(psi):
                    self.UpdateMass(root,data[j],0,1,1)
            count = 0
            index = 0
            while index<len(data):
                score = 0
                for i in range(numTree):
                    root = setTrees[i]
                    x = data[index]
                    score += self.Score(x,root)
                    self.UpdateMass(root,x,0,1,0)
                scores.append(score)
                count+=1
                index+=1
                if count==psi:
                    for i in range(numTree):
                        self.UpdateTree(setTrees[i])
                    count=0
            scores = np.asarray(scores)
            scores = scores.astype(float)
            lim = np.percentile(scores,0.2)
            maxi = np.max(scores)
            mini = np.min(scores[scores>lim])
            scores[scores<=lim] = 1.0
            scores[scores>lim] = (maxi-scores[scores>lim])/(maxi-mini)
            # maxi = np.max(scores)
            # mini = np.min(scores)
            # d = maxi-mini
            # scores=1-((scores-mini)/d)
            return scores
        def fit(self,X,y):
            scores = self.hs_tree(self.psi,self.numTree,X)
            fpr,tpr,thresholds = metrics.roc_curve(y,scores)
            self.thres = thresholds[fpr<0.1][-1]
            self.X_ = X
            return self
        def score(self,X,y):
            start = time.time()
            lim = len(X)
            X = np.vstack((X,self.X_))
            scores = self.hs_tree(self.psi,self.numTree,X)[:lim]
            scores = scores.reshape(-1,1)
            y_pred_class = binarize(scores,self.thres).reshape(1,-1)[0]
            self.score_ = metrics.f1_score(y,y_pred_class)
            myfile.write(str(time.time()-start)+'\n')
            #print(metrics.confusion_matrix(y,y_pred_class))
            return self.score_

    res_inter = pd.read_csv(inputPath,index_col=False,dtype={'imsi':str})
    tmp = pd.read_csv(labelPath,index_col=False,dtype={'imsi':str},usecols={'label'})
    X = res_inter.iloc[:,1:(dimension+1)].as_matrix()
    y = tmp.as_matrix()
    # normalisation and replacement of NAs (optional)
    # means = np.nanmean(X,axis=0)
    # for i in range(0,dimension):
    #     X[:,i][np.isnan(X[:,i])]=means[i]
    # amax = np.amax(X,axis=0)
    # amin = np.amin(X,axis=0)
    # X = (X-amin)/(amax-amin)


    gs = RandomizedSearchCV(ModeleTree(),tuned_params,n_iter=num_iter,cv=num_cv,refit=False)
    gs.fit(X,y)
    for i in range(num_iter):
        myfile.write(str(gs.grid_scores_[i].mean_validation_score)+'\n')
    myfile.write(str(gs.grid_scores_))
