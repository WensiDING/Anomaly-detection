labelPath = "/home/wensi/workspace/tryout/label_g_2.csv"
inputPath = "/home/wensi/workspace/tryout/label_hs_2.csv"

import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.preprocessing import binarize

evaluation = pd.read_csv(labelPath,header=0,names=['imsi','label'],index_col=False,dtype={'imsi':str})
tmp = pd.read_csv(inputPath,header=0,names=['imsi','pred_label'],dtype={'imsi':str})

evaluation = pd.merge(evaluation,tmp,on='imsi')

print ("Accuracy_score: %f" % (metrics.accuracy_score(evaluation.label,evaluation.pred_label)))
print ("F1_score: %f" % (metrics.f1_score(evaluation.label,evaluation.pred_label)))
print ("Confusion_matrix: ", metrics.confusion_matrix(evaluation.label,evaluation.pred_label))
