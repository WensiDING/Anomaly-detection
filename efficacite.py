inputPath = "/home/wensi/workspace/tryout/random_hs.csv"
num_iter = 3
num_cv = 3

import numpy as np
from matplotlib import pyplot as plt

with open(inputPath,"r") as f:
    eff = f.read().splitlines()

eff = np.array(eff[:len(eff)-1])
eff = eff.astype(float)
times = eff[:num_cv*num_iter].reshape(num_iter,num_cv)
times = np.mean(times,axis=1)
scores = eff[num_cv*num_iter:]
index = np.argsort(scores)
times = times[index]
scores = scores[index]
print(times)
print(scores)
plt.plot(scores,times)
plt.show()
