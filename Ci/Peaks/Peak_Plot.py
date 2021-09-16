# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:59:04 2021

@author: David
"""
import matplotlib.patches as pch
import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle


class PeakPlot():
    def __init__(self, x_arr, y_arr, jr, HVD, pathtodirectoryRead):
        self.x_arr = x_arr
        self.y_arr = y_arr
        self.jr = jr
        self.HVD = HVD
        self.pathtodirectoryRead = pathtodirectoryRead
        
    def runPeakPlot(self):
        plt.clf()
        figure2,ax = plt.subplots()
        for kl in range(len(self.x_arr)):
            plt.plot(self.x_arr[kl],self.y_arr[kl], '-ok', mfc='C1', mec='C1')

        x_size = 3.8016
        y_size = 3.2
        pix_x = [-21.95982,-18.04018,-13.95982,-10.04018,-5.95982, -2.04018, 2.04018,5.98982,10.04018,13.95982,18.04018,21.95982]
        pix_y = [21.6704,18.3296,13.6704,10.3296,5.6704,2.3296,-2.3296,-5.6704,-10.3296,-13.6704,-18.3296,-21.6704]
        
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i-x_size/2,pix_y_i-y_size/2),x_size,y_size, linewidth=0.5, edgecolor="dimgray",facecolor="none")
                ax.add_patch(rect)
        plt.xlabel("x")
        plt.ylabel("y")
        # plt.show()
        plt.savefig("{}Plotties/Peakfinder_{}.pdf".format(self.pathtodirectoryRead, self.jr))

        with open('{}Ref{}_Sections.pickle'.format(self.pathtodirectoryRead, self.HVD), 'rb') as handle:
                     refHVD = pickle.load(handle)
        fig, axs = plt.subplots(nrows=2, ncols=2)
        hi = axs[1, 1].hist2d(refHVD[self.jr][:, 0], refHVD[self.jr][:, 1], bins=100)
        
        for kl in range(len(self.x_arr)):
            plt.plot(self.x_arr[kl],self.y_arr[kl], '-ok', mfc='C1', mec='C1')
        # plt.show()
        plt.savefig("{}Plotties/Peakfinder2_{}.pdf".format(self.pathtodirectoryRead, self.jr))
