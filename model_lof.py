inputPath = "/home/wensi/workspace/tryout/result.csv"
outputPath = "/home/wensi/workspace/tryout/result4_new.csv"
dimension = 5
LB = 11
UB = 30


import numpy as np
import pandas as pd
import time
from sklearn.neighbors import NearestNeighbors

# read input file
res_inter = pd.read_csv(inputPath,dtype={'imsi':str})
variables = res_inter.iloc[:,1:(dimension+1)].as_matrix()

# normalisation and replacement of NAs (optional)
# means = np.nanmean(variables,axis=0)
# for i in range(0,dimension):
#     variables[:,i][np.isnan(variables[:,i])]=means[i]
# amax = np.amax(variables,axis=0)
# amin = np.amin(variables,axis=0)
# variables = (variables-amin)/(amax-amin)

lof = []
start = time.time()
# calculate lof
for minpts in range(LB,UB):
    nbrs = NearestNeighbors(n_neighbors=minpts,algorithm='auto').fit(variables)
    distances, indices = nbrs.kneighbors(variables)
    loc = []
    # calculate loc
    for i in range(0,len(indices)):
        tmp = 0
        for j in range(1,minpts):
            if distances[indices[i,j],minpts-1]<distances[i,j]:
                tmp=tmp+distances[i,j]
            else:
                tmp=tmp+distances[indices[i,j],minpts-1]
        loc.append((minpts-1)/tmp)
    # calculate lof and take the maximal value for each imsi
    oldlof = lof
    lof = []
    for i in range(0,len(indices)):
        tmp = 0
        for j in range(1,minpts):
            tmp=tmp+loc[indices[i,j]]
        lof.append(tmp/(loc[i]*(minpts-1)))
    if minpts==LB:
        continue
    else:
        lof = np.maximum(lof,oldlof)

print("temps de calcul: %f" % (time.time()-start))

# write out the result with descending lof
res_inter['lof'] = lof
res_inter.sort_values(by='lof',inplace=True,ascending=False)
res_inter.index=range(1,len(res_inter)+1)
res = res_inter.loc[:,['imsi','lof']]
res.to_csv(outputPath,index=False)


