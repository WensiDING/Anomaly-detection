from collections import defaultdict
import time
import numpy as np
import pandas as pd
import random as rd

inputPath = "/home/wensi/workspace/tryout/result.csv"
outputPath = "/home/wensi/workspace/tryout/result7.csv"
rd.seed(20)
maxDepth = 15
psi = 250
numTree = 25
dimension = 5
sizeLimit = 25

#read input file and initialise the result
scores = []
res_inter = pd.read_csv(inputPath,dtype={'imsi':str})
datas = res_inter.iloc[:,1:(dimension+1)].as_matrix()

# normalisation and replacement of NAs (optional)
# means = np.nanmean(datas,axis=0)
# for i in range(0,dimension):
#     datas[:,i][np.isnan(datas[:,i])]=means[i]
# amax = np.amax(datas,axis=0)
# amin = np.amin(datas,axis=0)
# datas = (datas-amin)/(amax-amin)

def tree(): return defaultdict(tree)

def buildSingleHS_Tree(root,mins,maxs,m,n):
    if m==maxDepth:
        root[m][n]=[0,0,0,0]
    else:
        q = int(round((dimension-1)*rd.random()))
        p = (maxs[q]+mins[q])/2
        tmp = maxs[q]
        maxs[q] = p
        buildSingleHS_Tree(root,mins,maxs,m+1,2*n-1)
        maxs[q] = tmp
        mins[q] = p
        buildSingleHS_Tree(root,mins,maxs,m+1,2*n)
        root[m][n]=[q,p,0,0]

def UpdateMass(root,x,m,n,refWindow):
    val = root[m][n]
    if refWindow:
        val[2]+=1
    else:
        val[3]+=1
    if m < maxDepth:
        q = val[0]
        p = val[1]
        if x[q] < p:
            UpdateMass(root,x,m+1,2*n-1,refWindow)
        else:
            UpdateMass(root,x,m+1,2*n,refWindow)

def UpdateTree(root):
    m = 0
    n = 0
    while m<= maxDepth:
        while n <= 2**m:
            val = root[m][n]
            val[2] = val[3]
            val[3] = 0
            n+=1
        n=1
        m+=1

def Score(x,root):
    m=0
    n=1
    while(m<maxDepth and root[m][n][2]>sizeLimit):
        q = root[m][n][0]
        p = root[m][n][1]
        m+=1
        if x[q]<p :
            n = 2*n-1
        else:
            n= 2*n
    return root[m][n][2]*(2**m)

def hs_tree(psi,numTree,data):
    #initialise a set of trees
    setTrees = []
    for i in range(numTree):
        setTrees.append(tree())
        mins = []
        maxs = []
        for j in range(dimension):
            s = rd.uniform(0,1)
            mins.append(s-2*max(s,1-s))
            maxs.append(s+2*max(s,1-s))
        buildSingleHS_Tree(setTrees[i],mins,maxs,0,1)
    #initialise mass
    for i in range(numTree):
        root = setTrees[i]
        for j in range(psi):
            UpdateMass(root,data[j],0,1,1)
    #calculate scores
    count = 0
    index = 0
    while index<len(data):
        score = 0
        for i in range(numTree):
            root = setTrees[i]
            x = data[index]
            score += Score(x,root)
            UpdateMass(root,x,0,1,0)
        scores.append(score)
        count+=1
        index+=1
        if count==psi:
            for i in range(numTree):
                UpdateTree(setTrees[i])
            count=0

start = time.time()
hs_tree(psi,numTree,datas)
print("temps de calcul: %f" % (time.time()-start))
res_inter['scores'] = scores
res_inter.sort_values(by='scores',inplace=True)
res_inter.index=range(1,len(res_inter)+1)
res = res_inter.loc[:,['imsi','scores']]
res.to_csv(outputPath,index=False)
