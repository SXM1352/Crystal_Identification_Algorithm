# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 15:07:30 2020

@author: David
"""
import matplotlib.pyplot as plt
import numpy as np
import csv
import pickle
import matplotlib.patches as pch
from matplotlib.colors import LogNorm

with open('Ref000_Sections-together.pickle', 'rb') as handle:
    Ref111_Sections_2 = pickle.load(handle)

fig, ax = plt.subplots(figsize=(100, 100))

hist1 = ax.hist2d(Ref111_Sections_2[:, 0], Ref111_Sections_2[:, 1], bins=3, range=[[11.7,12.2],[-12.2,-11.7]], norm=LogNorm())
fig.colorbar(hist1[3], ax=ax)
plt.show()