import pandas as pd
import numpy as np
import time
from sklearn.base import BaseEstimator
from sklearn.neighbors import NearestNeighbors
from itertools import combinations
from sklearn import metrics
from scipy.stats import randint as sp_randint
from sklearn.grid_search import RandomizedSearchCV
from sklearn.preprocessing import binarize

inputPath = "/home/wensi/workspace/tryout/result.csv"
labelPath = "/home/wensi/workspace/tryout/label.csv"
outputPath = "/home/wensi/workspace/tryout/random_lof.csv"
dimension = 6
num_iter = 20
num_cv = 3
## build a dictionary for all the combination of variables
items = range(dimension)
count = 0
variables = {}
# combinations of two or more variables are listed 
for i in range(2,dimension+1):
    for var in combinations(items,i):
        variables[count]=var
        count+=1
tuned_params = {'MinPtsLB':sp_randint(11,31),'MinPtsUB':sp_randint(31,81),'Vars':sp_randint(0,count)}

## write the time cost and corresponding score of every hyperparameter to a file
with open(outputPath,"a") as myfile:
## construct a estimator for model lof
    class ModeleLof(BaseEstimator):
        def __init__(self,MinPtsLB=11,MinPtsUB=30,Vars=1):
            self.MinPtsLB = MinPtsLB
            self.MinPtsUB = MinPtsUB
            self.Vars = Vars
        def lof(self,X):
            lof = []
            X = X[:,variables[self.Vars]]
            for minpts in range(self.MinPtsLB,self.MinPtsUB):
                nbrs = NearestNeighbors(n_neighbors=minpts,algorithm='auto').fit(X)
                distances, indices = nbrs.kneighbors(X)
                loc = []
                for i in range(0,len(indices)):
                    tmp = 0
                    for j in range(1,minpts):
                        if distances[indices[i,j],minpts-1]<distances[i,j]:
                            tmp=tmp+distances[i,j]
                        else:
                            tmp=tmp+distances[indices[i,j],minpts-1]
                    loc.append((minpts-1)/tmp)
                oldlof = lof
                lof = []
                for i in range(0,len(indices)):
                    tmp = 0
                    for j in range(1,minpts):
                        tmp=tmp+loc[indices[i,j]]
                    lof.append(tmp/(loc[i]*(minpts-1)))
                if minpts==self.MinPtsLB:
                    continue
                else:
                    lof = np.maximum(lof,oldlof)
            lof = np.asarray(lof)
            lim = np.percentile(lof,99.8)
            maxi = np.max(lof[lof<lim])
            lof[lof<1] = 1
            lof[lof<lim] = 1 - (maxi - lof[lof<lim])/(maxi-1)
            lof[lof>1] = 1
            # maxi = np.max(lof)
            # mini = np.min(lof)
            # d = maxi-mini
            # lof=1-((lof-mini)/d)
            return lof
        def fit(self,X,y):
            lof = self.lof(X)
            fpr,tpr,thresholds = metrics.roc_curve(y,lof)
            self.thres = thresholds[fpr<0.1][-1]
            self.X_ = X
            return self

        def score(self,X,y):
            print(self.MinPtsLB,self.MinPtsUB,self.Vars)
            start = time.time()
            lim = len(X)
            X = np.vstack((X,self.X_))
            lof = self.lof(X)[:lim]
            lof = lof.reshape(-1,1)
            y_pred_class = binarize(lof,self.thres).reshape(1,-1)[0]
            self.score_ = metrics.f1_score(y,y_pred_class)
            myfile.write(str(time.time()-start)+'\n')
            return self.score_
    ## initialise X and y for the model lof and do the feature scaling
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


    gs = RandomizedSearchCV(ModeleLof(),tuned_params,n_iter=num_iter,cv=num_cv,refit=False)
    gs.fit(X,y)
    ## write to file
    for i in range(num_iter):
        myfile.write(str(gs.grid_scores_[i].mean_validation_score) + '\n')
    myfile.write(str(gs.grid_scores_))
