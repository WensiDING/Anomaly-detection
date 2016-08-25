labelPath = "/home/wensi/workspace/tryout/label_new.csv"
inputPath = "/home/wensi/workspace/tryout/result5_new.csv"
threshold_fp = 0.1
model = "hs_tree"

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
from scipy.stats import norm

evaluation = pd.read_csv(labelPath,header=0,names=['imsi','label'],index_col=False,dtype={'imsi':str})

tmp = pd.read_csv(inputPath,header=0,names=['imsi','score'],dtype={'imsi':str})

def normalization_lof(tmp):
    lim = np.percentile(tmp.score,99.8)
    maxi = np.max(tmp.loc[tmp.score<lim,'score'])
    tmp.loc[tmp.score<1,'score'] = 1
    tmp.loc[tmp.score<lim,'score'] = 1 - (maxi - tmp.loc[tmp.score<lim,'score'])/(maxi-1)
    tmp.loc[tmp.score>1,'score'] = 1
    return tmp
def normalization_hs(tmp):
    tmp['score'] = tmp.score.astype(float)
    lim = np.percentile(tmp.score,0.2)
    maxi = np.max(tmp.score)
    mini = np.min(tmp.score[tmp.score>lim])
    tmp.loc[tmp.score<=lim,'score'] = 1.0
    tmp.loc[tmp.score>lim,'score'] = (maxi-tmp.loc[tmp.score>lim,'score'])/(maxi-mini)
    return tmp

if model=="lof":
    tmp = normalization_lof(tmp)
if model == "hs_tree":
    tmp = normalization_hs(tmp)

evaluation = pd.merge(evaluation,tmp,on='imsi')
fpr,tpr,thresholds = metrics.roc_curve(evaluation['label'],evaluation['score'])

print ("AUC Score: %f" % (metrics.roc_auc_score(evaluation['label'],evaluation['score'])))
print ("Threshold: %f" % thresholds[fpr<threshold_fp][-1])
plt.plot(fpr,tpr)
plt.xlim([0.0,1.0])
plt.ylim([0.0,1.0])
plt.grid(True)
plt.show()
