# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 01:42:16 2020

@author: David
"""
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from matplotlib import cm
import cPickle as pickle
import matplotlib
import itertools
import os

# data = np.random.random_sample((36,34))
#
# def read_data_COG(NVD):
#     with open('./20210121NEWCHECK/data-layer1-{}-valid.pickle'.format(NVD), 'rb') as handle:
#         data1 = pickle.load(handle) # 000, 100, 010, 111
#
#     with open('./20210121NEWCHECK/data-layer2-{}-valid.pickle'.format(NVD), 'rb') as handle:
#         data2 = pickle.load(handle) # 000, 100, 010, 111
#
#     with open('./20210121NEWCHECK/data-layer3-{}-valid.pickle'.format(NVD), 'rb') as handle:
#         data3 = pickle.load(handle) # 000, 100, 010, 111
#
#     return data1, data2, data3
#
# data1000, data2000, data3000 =  read_data_COG("000")
# data1100, data2100, data3100 =  read_data_COG("100")
# data1010, data2010, data3010 =  read_data_COG("010")
# data1111, data2111, data3111 =  read_data_COG("111")
#
# #data1 = (data1100+data1000+data1010+data1111)/4
# #data2 = (data2100+data2000+data2010+data2111)/4
# #data3 = (data3100+data3000+data3010+data3111)/4
#
# data1 = data1100
# data2 = data2100
# data3 = data3100

# pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
#
# with open('{}data-layer1-all126894299-valid.pickle'.format(pathtodirectoryRead), 'rb') as handle:
#     data1 = pickle.load(handle) # 000, 100, 010, 111
#
# with open('{}data-layer2-all126894299-valid.pickle'.format(pathtodirectoryRead), 'rb') as handle:
#     data2 = pickle.load(handle) # 000, 100, 010, 111
#
# with open('{}data-layer3-all126894299-valid.pickle'.format(pathtodirectoryRead), 'rb') as handle:
#     data3 = pickle.load(handle) # 000, 100, 010, 111

class Plot_Labels_with_Values():
    def __init__(self):
        pass
    def __layer(self, x_ini,x_fin,y_ini,y_fin):
        xiter = np.arange(x_ini,x_fin,1.34) #1.34 is the theoretical one, but adaptative to electronics
        yiter = np.arange(y_ini,y_fin,1.34)
        print(len(xiter)*len(yiter))
        print(len(xiter))
        print(len(yiter))
        xx=np.fromiter(xiter,dtype=np.float)
        yy=np.fromiter(yiter,dtype=np.float)
        xo, yo = np.meshgrid(xx,yy,indexing='xy')
        return xo,yo

    def __axis_f(self, MLx, MLy,AMLx, AMLy,xl,yl,ax):
        ax.set_xlim(xl)
        ax.set_ylim(yl)

        # Change major ticks to show every 20.
        ax.xaxis.set_major_locator(MultipleLocator(MLx))
        ax.yaxis.set_major_locator(MultipleLocator(MLy))

        # Change minor ticks to show every 5. (20/4 = 5)
        ax.xaxis.set_minor_locator(AutoMinorLocator(AMLx))
        ax.yaxis.set_minor_locator(AutoMinorLocator(AMLy))

        # Turn grid on for both major and minor ticks and style minor slightly
        # differently.
        ax.grid(which='major', color='#CCCCCC', linestyle='--')
        ax.grid(which='minor', color='#CCCCCC', linestyle=':')

        ax.set_axisbelow(True)
        #
        ax.set_aspect(1.0) #keep aspects 1:1 between axis
        return ax

    def __checkFolder(self, pathDirectory):
        CHECK_FOLDER = os.path.isdir(pathDirectory)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(pathDirectory)
            print("created folder : ", pathDirectory)
    def runPlot(self, data1, data2, data3, title, pathtodirectorySave):
        # make grid First Layer
        xpo, ypo = self.__layer(-22.11,22.78,-23.45,24.12) #0.67 -21.95982 x, 21.6704 y
        xo1, yo1 = xpo, ypo
        # make grid Second Layer
        xo2, yo2 = self.__layer(-20.1,20.77,-23.45,24.12)

        # make grid Third Layer
        xo3, yo3 = self.__layer(-20.1,20.77,-22.78,23.45)

        x_size = 3.8016
        y_size = 3.2
        pix_x = [-21.95982,-18.04018,-13.95982,-10.04018,-5.95982, -2.04018, 2.04018,5.98982,10.04018,13.95982,18.04018,21.95982]
        pix_y = [21.6704,18.3296,13.6704,10.3296,5.6704,2.3296,-2.3296,-5.6704,-10.3296,-13.6704,-18.3296,-21.6704]

        #fig1, ax1 = plt.subplots(figsize=(100, 100))
        # Set axis ranges; by default this will put major ticks every 25.

        #fig = plt.figure()
        #ax = Axes3D(fig)


        #ax = self.__axis_f(22.78, 24.12, 17,18,(-22.78, 22.78),(-24.12, 24.12),ax) #14.925373134328357


        #lx= len(data[0])            # Work out matrix dimensions
        #ly= len(data[:,0])
        ##xpos = np.arange(0,lx,1)    # Set up a mesh of positions
        ##ypos = np.arange(0,ly,1)
        ##xpos, ypos = np.meshgrid(xpos+0.25, ypos+0.25)
        #
        #xpos = xpo.flatten()   # Convert positions to 1D array
        #ypos = np.flip(ypo)
        #ypos = ypos.flatten()
        #zpos = np.zeros(lx*ly)
        #
        #dx = 0.5 * np.ones_like(zpos)
        #dy = dx.copy()
        #dz = data.flatten()
        #
        #
        ##surf = ax.plot_trisurf(xpos, ypos, dz, cmap=cm.jet, linewidth=0.1)
        #
        ##cs = ['r', 'g', 'b', 'y', 'c'] * ly
        #
        #values = np.linspace(0.2, 1., xpos.ravel().shape[0])
        #values = (dz-dz.min())/np.float_(dz.max()-dz.min())
        #colors = cm.rainbow(values)
        ##ax.bar3d(xpos,ypos,zpos, dx, dy, dz, color=colors)
        ##
        ##
        ##
        ###sh()
        ##ax.w_xaxis.set_ticklabels(column_names)
        ##ax.w_yaxis.set_ticklabels(row_names)
        #ax.set_xlabel('x')
        #ax.set_ylabel('y')
        #ax.set_zlabel('Occurrence')
        #
        #plt.show()

        xpos1 = xo1.flatten()   # Convert positions to 1D array
        ypos1 = np.flip(yo1)
        ypos1 = ypos1.flatten()
        dz1 = data1.flatten()

        xpos2 = xo2.flatten()   # Convert positions to 1D array
        ypos2 = np.flip(yo2)
        ypos2 = ypos2.flatten()
        dz2 = data2.flatten()

        xpos3 = xo3.flatten()   # Convert positions to 1D array
        ypos3 = np.flip(yo3)
        ypos3 = ypos3.flatten()
        dz3 = data3.flatten()

        x = xpos1
        y = ypos1
        t = dz1

        x2 = xpos2
        y2 = ypos2
        t2 = dz2
        print(t2)

        x3 = xpos3
        y3 = ypos3
        t3 = dz3

        fig, ax = plt.subplots(1, 1, figsize=(15,15))

        pcm = plt.scatter(x, y, marker = "2",s=20, linewidths = 0, c=(t), cmap='viridis', label="1st Layer", norm=matplotlib.colors.LogNorm())
        pcm2 = plt.scatter(x2, y2, marker = "x",s=20, linewidths = 0, c=(t2), cmap='viridis', label="2nd Layer", norm=matplotlib.colors.LogNorm())
        pcm3 = plt.scatter(x3, y3, marker = "+",s=20, linewidths = 0, c=(t3), cmap='viridis', label="3rd Layer", norm=matplotlib.colors.LogNorm())
        plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='lower right', borderaxespad=0.) #bbox_to_anchor=(1.05, 1),

        plt.colorbar()
        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')

        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i-x_size/2,pix_y_i-y_size/2),x_size,y_size, linewidth=0.5, edgecolor="dimgray",facecolor="none")
                ax.add_patch(rect)
        plt.title(str(title))
        if pathtodirectorySave != 'None':
            finaldirectorySaveCM = pathtodirectorySave + 'CrystalMaps/'
            self.__checkFolder(finaldirectorySaveCM)
            finaldirectorySave = finaldirectorySaveCM + 'NumberClusters/'
            self.__checkFolder(finaldirectorySave)
            plt.savefig('{}{}.png'.format(finaldirectorySave, title))
        else:
            plt.show()
# PLWV = Plot_Labels_with_Values()
# PLWV.runPlot(data1,data2,data3,"ALL EVENTS")