# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 13:27:59 2021

@author: David
"""
import pickle
import matplotlib.pyplot as plt
import numpy as np

with open('dic-LUD-{}.pickle'.format("010"), 'rb') as handle:
    ludHVD = pickle.load(handle) # 000, 100, 010, 111

x_lud = []
y_lud = []
for i in ludHVD.keys():
    if ludHVD[i]:
        x_lud.append(i[0])
        y_lud.append(i[1])
        
fig, ax = plt.subplots(1, 1)

plt.scatter(x_lud, y_lud, label="111")
ax.set_xlabel('x [mm]')
ax.set_ylabel('y [mm]')
        
plt.show()