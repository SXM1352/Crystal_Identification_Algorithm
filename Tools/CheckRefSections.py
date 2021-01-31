# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 16:56:34 2021

@author: David
"""


import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch
from matplotlib.colors import LogNorm
import pickle

with open('Ref000_Sections-together.pickle', 'rb') as handle:
         Ref000_Sections = pickle.load(handle)
Ref000_test_y = []
Ref000_test = []
for i in range(len(Ref000_Sections[:,1])):
     if Ref000_Sections[i,0] > 19 and Ref000_Sections[i,1] > 19 and Ref000_Sections[i,0] < 21 and Ref000_Sections[i,1] < 21:
         Ref000_test.append(Ref000_Sections[i,0])
         Ref000_test_y.append(Ref000_Sections[i,1])
fig, ax = plt.subplots(figsize=(100, 100))
hist1 = ax.hist2d(Ref000_Sections[:, 0], Ref000_Sections[:, 1], bins=1000, range=[[-24,24],[-24,24]], norm=LogNorm())
fig.colorbar(hist1[3], ax=ax)
plt.xlabel("x")
plt.ylabel("y")
plt.xlim(-24,24)
plt.ylim(-24,24)
plt.show()
