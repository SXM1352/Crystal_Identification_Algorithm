# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 10:24:20 2020

@author: David
"""
from Hypmed import *
Hyp = Hypmed_Clustering()
Hyp.sket.loadDataHyp("/home/david.perez/Desktop/defCOG90Mreference.hdf5", "/home/david.perez/Desktop/defCOG10Mtest.hdf5")
Hyp.valid_events()
Hyp.region_ana()
Hyp.Floodmap()
Hyp.save_hist(Hyp.hist0_all[0])
#Hyp.PeakFinderPlot()
