
import cPickle as pickle
import h5py
import argparse
from textwrap import dedent
import sys
import re
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
from matplotlib import cm
import matplotlib
import itertools
import os

# from LabelsPlots import Plot_Labels_with_Values

def checkFolder(pathDirectory):
    CHECK_FOLDER = os.path.isdir(pathDirectory)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathDirectory)
        print("created folder : ", pathDirectory)

def CrystalDict():
    """
    Define Crystal identification dictionary with respective ids for all the peaks based on layer

    @return: None
    @rtype:
    """
    m = 1
    row = []
    j = 0
    p = 0
    rows = []
    dic_crystal = {}
    for i in range(3426):
        if i >= (65 * m + 31 * p) and j % 2 == 0:
            rows.append(row)
            # s = 1
            for n, r in enumerate(row):
                if n == 0 or n == 64:
                    peakii = {
                        'row': j,
                        'layer': 1,
                        'id': r,
                        'E_r(%FWHM)': [],
                        'Mean': []
                    }
                    dic_crystal[r] = peakii
                else:
                    if n % 2 != 0:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'E_r(%FWHM)': [],
                            'Mean': []
                        }
                        dic_crystal[r] = peakii
                    else:
                        peakjj = {
                            'row': j,
                            'layer': 2,
                            'id': r,
                            'E_r(%FWHM)': [],
                            'Mean': []
                        }
                        dic_crystal[r] = peakjj

            row = []
            j += 1
            p += 1
        elif i >= (65 * m + 31 * p) and j % 2 != 0:
            rows.append(row)
            for r in row:
                peakkk = {
                    'row': j,
                    'layer': 3,
                    'id': r,
                    'E_r(%FWHM)': [],
                    'Mean': []
                }
                dic_crystal[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)

    return dic_crystal

def normalizeAndSplit(l):
    ''' function to split an input line and remove unwanted characters \
    input parameters: \
    l = line to parse'''

    #l = re.sub("\s*#.*", "", l)	# Remove comments
    l = re.sub('^\s*', '', l)	# Remove leading white space
    #l = re.sub('\s*$', '', l)	# Remove trailing whitespace
    #l = re.sub('\s+', '\t', l)	# Normalize whitespace to tabs
    #l = re.sub('\r', '', l)		# Remove \r
    l = re.sub('\n', '', l)		# Remove \l
    #l = re.sub(':', ',', l)		# Remove \l
    l = l.split()
    return l

def dic_calFactor_HVD(pathtodirectoryRead, HVD, dic_HVD):
    with open('{}CalibPVLog{}.txt'.format(pathtodirectoryRead, HVD), 'r') as finput:
        lines = finput.readlines()
        E_r_2 = 100.
        for line in lines:
            el = normalizeAndSplit(line)
            id_crystal = int(el[0])
            mean = el[13]
            cal_factor = 511. / float(mean)
            E_r = float(el[-1])
            valid_P = int(el[1])
            if valid_P:
                if id_crystal in dic_HVD.keys():
                    if E_r < E_r_2:
                        dic_HVD[id_crystal] = {'cal_factor': cal_factor, 'mean': mean, 'E_r(%FWHM)': E_r}
                else:
                    dic_HVD[id_crystal] = {'cal_factor': cal_factor, 'mean': mean, 'E_r(%FWHM)': E_r}
                E_r_2 = E_r
    return dic_HVD

def Counts_in_layers(dic_HVD, HVD, list_events):
    data_cluster_pvFinal_layer1_m = {}
    data_cluster_pvFinal_layer2_m = {}
    data_cluster_pvFinal_layer3_m = {}

    data_cluster_pvFinal_layer1_er = {}
    data_cluster_pvFinal_layer2_er = {}
    data_cluster_pvFinal_layer3_er = {}

    dic_crystal = CrystalDict() #not necessary, but faster?

    list_usedCrystalPV = []
    for event in list_events:
        final_event = event[1]
        with open('{}array_usedCrystalPV_{}_{}.txt'.format(pathtodirectorySave, HVD, final_event), 'r') as finput:
            lines = finput.readlines()
            for line in lines:
                el = normalizeAndSplit(line)
                id_crystal = int(el[0])
                if id_crystal in list_usedCrystalPV:
                    pass
                else:
                    list_usedCrystalPV.append(id_crystal)

    # with open('{}array_usedCrystalPV_{}.pickle'.format(pathtodirectorySave, HVD), "rb") as handle:
    #     list_usedCrystalPV = pickle.load(handle)  # 000, 100, 010, 111


    for i in dic_crystal.keys():
        if i in dic_HVD.keys() and i in list_usedCrystalPV:
            mean = dic_HVD[i]['mean']
            e_r = dic_HVD[i]['E_r(%FWHM)']
        else:
            mean = 0
            e_r = 0

        if dic_crystal[i]['layer'] == 1:
            data_cluster_pvFinal_layer1_m[i] = mean
            data_cluster_pvFinal_layer1_er[i] = e_r

        elif dic_crystal[i]['layer'] == 2:
            data_cluster_pvFinal_layer2_m[i] = mean
            data_cluster_pvFinal_layer2_er[i] = e_r

        elif dic_crystal[i]['layer'] == 3:
            data_cluster_pvFinal_layer3_m[i] = mean
            data_cluster_pvFinal_layer3_er[i] = e_r


    data1_m = np.zeros((36, 34))
    data2_m = np.zeros((36, 31))
    data3_m = np.zeros((35, 31))
    data1_er = np.zeros((36, 34))
    data2_er = np.zeros((36, 31))
    data3_er = np.zeros((35, 31))
    print("svae")
    index = 0
    index2 = 0
    for i in sorted(data_cluster_pvFinal_layer1_m.keys()):
        data1_m[index][index2] = data_cluster_pvFinal_layer1_m[i]
        data1_er[index][index2] = data_cluster_pvFinal_layer1_er[i]
        index2 += 1
        if index2 == 34:
            index2 = 0
            index += 1
    index = 0
    index2 = 0
    for i in sorted(data_cluster_pvFinal_layer2_m.keys()):
        data2_m[index][index2] = data_cluster_pvFinal_layer2_m[i]
        data2_er[index][index2] = data_cluster_pvFinal_layer2_er[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
    index = 0
    index2 = 0
    for i in sorted(data_cluster_pvFinal_layer3_m.keys()):
        data3_m[index][index2] = data_cluster_pvFinal_layer3_m[i]
        data3_er[index][index2] = data_cluster_pvFinal_layer3_er[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
    return data1_m, data2_m, data3_m, data1_er, data2_er, data3_er

class Plot_Crystal_Map():
    def __init__(self):
        pass
    def __layer(self, x_ini,x_fin,y_ini,y_fin):
        xiter_pcolor = np.arange(x_ini,x_fin+1.34,1.34) #1.34 is the theoretical one, but adaptative to electronics
        yiter_pcolor = np.arange(y_ini-1.34,y_fin,1.34) #why we take +- 1.34: https://stackoverflow.com/questions/23549195/matplotlib-pcolor-does-not-plot-last-row-and-column
        xiter = np.arange(x_ini, x_fin, 1.34)  # 1.34 is the theoretical one, but adaptative to electronics
        yiter = np.arange(y_ini, y_fin, 1.34)
        print(len(xiter)*len(yiter))
        print(len(xiter))
        print(len(yiter))
        xx=np.fromiter(xiter,dtype=np.float)
        yy=np.fromiter(yiter,dtype=np.float)
        xo, yo = np.meshgrid(xx,yy,indexing='xy')

        print(len(xiter_pcolor) * len(yiter_pcolor))
        print(len(xiter_pcolor))
        print(len(yiter_pcolor))
        xx_pcolor = np.fromiter(xiter_pcolor, dtype=np.float)
        yy_pcolor = np.fromiter(yiter_pcolor, dtype=np.float)
        xo_pcolor, yo_pcolor = np.meshgrid(xx_pcolor, yy_pcolor, indexing='xy')
        return xo,yo, xo_pcolor, yo_pcolor

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
    def runPlot(self, data1, data2, data3, title, pathtodirectorySaveCM, HVD):
        # make grid First Layer
        xpo, ypo, xo_pcolor, yo_pcolor = self.__layer(-22.11,22.78,-23.45,24.12) #0.67 -21.95982 x, 21.6704 y
        xo1, yo1 = xpo, ypo
        xo1_pcolor, yo1_pcolor = xo_pcolor, yo_pcolor
        # make grid Second Layer
        xo2, yo2, xo2_pcolor, yo2_pcolor = self.__layer(-20.1,20.77,-23.45,24.12)

        # make grid Third Layer
        xo3, yo3, xo3_pcolor, yo3_pcolor = self.__layer(-20.1,20.77,-22.78,23.45)

        x_size = 3.8016
        y_size = 3.2
        pix_x = [-21.95982,-18.04018,-13.95982,-10.04018,-5.95982, -2.04018, 2.04018,5.98982,10.04018,13.95982,18.04018,21.95982]
        pix_y = [21.6704,18.3296,13.6704,10.3296,5.6704,2.3296,-2.3296,-5.6704,-10.3296,-13.6704,-18.3296,-21.6704]

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

        fig, _axs = plt.subplots(2, 2, figsize=(25,25))
        axs = _axs.flatten()

        #cbar = np.linspace(min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), max([np.amax(data1), np.amax(data2), np.amax(data3)]), 6, endpoint=True)

        #plt.subplot(2,2,1)
        ax0 = axs[0]
        #pcm2 = ax0.scatter(x2, y2, marker = "x",s=20, linewidths = 0, c=(t2), cmap='viridis', label="2nd Layer", norm=matplotlib.colors.LogNorm())
        #pcm2 = ax0.imshow(data2, cmap=plt.cm.jet)#interpolation ='nearest', cmap=plt.cm.jet)

        print(min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]))
        print(max([np.amax(data1), np.amax(data2), np.amax(data3)]))
        x_layer2 = xo2_pcolor-0.665
        y_layer2 = np.flip(yo2_pcolor)+0.665
        #pcm2 = ax0.pcolor(x_layer2, y_layer2, data2, cmap=plt.cm.jet, norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)
        if title == "E_r(%FWHM)":
            pcm2 = ax0.pcolor(x_layer2, y_layer2, data2, cmap=plt.cm.jet, norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm2 = ax0.pcolor(x_layer2, y_layer2, data2, cmap=plt.cm.jet, norm = matplotlib.colors.Normalize(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)

        ax0.set_xlim([-24.5, 24.5])
        ax0.set_ylim([-25.7, 25.7])
        #plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='lower right', borderaxespad=0.) #bbox_to_anchor=(1.05, 1),
        fig.colorbar(pcm2, ax=ax0)#, ticks=cbar)

        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i-x_size/2,pix_y_i-y_size/2),x_size,y_size, linewidth=0.5, edgecolor="dimgray",facecolor="none")
                ax0.add_patch(rect)
        ax0.set_title('Layer 2')

        #plt.subplot(2, 2, 2)
        ax1 = axs[1]
        # pcm_ = ax1.scatter(x, y, marker="2", s=20, linewidths=0, c=(t), cmap=plt.cm.jet, label="1st Layer",
        #                   norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))
        # pcm_2 = ax1.scatter(x2, y2, marker="x", s=20, linewidths=0, c=(t2), cmap=plt.cm.jet, label="2nd Layer",
        #                   norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))
        # pcm_3 = ax1.scatter(x3, y3, marker="+", s=20, linewidths=0, c=(t3), cmap=plt.cm.jet, label="3rd Layer",
        #                   norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))
        if title == "E_r(%FWHM)":
            pcm_ = ax1.scatter(x, y, marker="2", s=20, linewidths=0, c=(t), cmap=plt.cm.jet, label="1st Layer", norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm_ = ax1.scatter(x, y, marker="2", s=20, linewidths=0, c=(t), cmap=plt.cm.jet, label="1st Layer",
                               norm=matplotlib.colors.Normalize(vmin=min(
                                   [min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]),
                                    min(data3[np.nonzero(data3)])]),
                                                              vmax=max([np.amax(data1), np.amax(data2), np.amax(data3)])))
        if title == "E_r(%FWHM)":
            pcm_2 = ax1.scatter(x2, y2, marker="x", s=20, linewidths=0, c=(t2), cmap=plt.cm.jet, label="2nd Layer", norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm_2 = ax1.scatter(x2, y2, marker="x", s=20, linewidths=0, c=(t2), cmap=plt.cm.jet, label="2nd Layer",
                            norm=matplotlib.colors.Normalize(vmin=min(
                                [min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]),
                                 min(data3[np.nonzero(data3)])]),
                                                           vmax=max([np.amax(data1), np.amax(data2), np.amax(data3)])))
        if title == "E_r(%FWHM)":
            pcm_3 = ax1.scatter(x3, y3, marker="+", s=20, linewidths=0, c=(t3), cmap=plt.cm.jet, label="3rd Layer", norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm_3 = ax1.scatter(x3, y3, marker="+", s=20, linewidths=0, c=(t3), cmap=plt.cm.jet, label="3rd Layer",
                            norm=matplotlib.colors.Normalize(vmin=min(
                                [min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]),
                                 min(data3[np.nonzero(data3)])]),
                                                           vmax=max([np.amax(data1), np.amax(data2), np.amax(data3)])))

        ax1.set_xlim([-24.5, 24.5])
        ax1.set_ylim([-25.7, 25.7])
        plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='best', borderaxespad=0.)  # bbox_to_anchor=(1.05, 1),

        fig.colorbar(pcm_3, ax=ax1)#, ticks=cbar)
        #fig.colorbar(pcm_3, ax=ax1)

        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax1.add_patch(rect)
        ax1.set_title('ALL Layers')

        #plt.subplot(2, 2, 3)
        ax2 = axs[2]
        # pcm3 = ax2.scatter(x3, y3, marker="+", s=20, linewidths=0, c=(t3), cmap='viridis', label="3rd Layer",
        #                    norm=matplotlib.colors.LogNorm())
        x_layer3 = xo3_pcolor - 0.665
        y_layer3 = np.flip(yo3_pcolor) + 0.665
        # pcm3 = ax2.pcolor(x_layer3, y_layer3, data3, cmap=plt.cm.jet,
        #                   norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)
        if title == "E_r(%FWHM)":
            pcm3 = ax2.pcolor(x_layer3, y_layer3, data3, cmap=plt.cm.jet, norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm3 = ax2.pcolor(x_layer3, y_layer3, data3, cmap=plt.cm.jet,
                          norm=matplotlib.colors.Normalize(vmin=min(
                              [min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]),
                               min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1), np.amax(data2), np.amax(
                              data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)

        ax2.set_xlim([-24.5, 24.5])
        ax2.set_ylim([-25.7, 25.7])
        #plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='lower right', borderaxespad=0.)  # bbox_to_anchor=(1.05, 1),

        fig.colorbar(pcm3, ax=ax2)

        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax2.add_patch(rect)
        ax2.set_title('Layer 3')

        #plt.subplot(2, 2, 4)
        ax3 = axs[3]
        # pcm = ax3.scatter(x, y, marker="2", s=20, linewidths=0, c=(t), cmap='viridis', label="1st Layer",
        #                   norm=matplotlib.colors.LogNorm())
        x_layer1 = xo1_pcolor - 0.665
        y_layer1 = np.flip(yo1_pcolor) + 0.665
        # pcm = ax3.pcolor(x_layer1, y_layer1, data1, cmap=plt.cm.jet,
        #                   norm = matplotlib.colors.LogNorm(vmin=min([min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]), min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1),np.amax(data2),np.amax(data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)
        if title == "E_r(%FWHM)":
            pcm = ax3.pcolor(x_layer1, y_layer1, data1, cmap=plt.cm.jet, norm=matplotlib.colors.Normalize(vmin=5, vmax=25))  # interpolation ='nearest', cmap=plt.cm.jet)
        else:
            pcm = ax3.pcolor(x_layer1, y_layer1, data1, cmap=plt.cm.jet,
                         norm=matplotlib.colors.Normalize(vmin=min(
                             [min(data1[np.nonzero(data1)]), min(data2[np.nonzero(data2)]),
                              min(data3[np.nonzero(data3)])]), vmax=max([np.amax(data1), np.amax(data2), np.amax(
                             data3)])))  # interpolation ='nearest', cmap=plt.cm.jet)

        ax3.set_xlim([-24.5, 24.5])
        ax3.set_ylim([-25.7, 25.7])
        # plt.legend(bbox_to_anchor=(-0.03, 0.75), loc='lower right', borderaxespad=0.)  # bbox_to_anchor=(1.05, 1),

        fig.colorbar(pcm, ax=ax3)

        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax3.add_patch(rect)
        ax3.set_title('Layer 1')

        plt.setp(_axs[-1, :], xlabel='x [mm]')
        plt.setp(_axs[:, 0], ylabel='y [mm]')

        plt.suptitle(str(title) + ' - ' + HVD)

        if pathtodirectorySaveCM != 'None':
            finaldirectorySaveCMCM = pathtodirectorySaveCM + 'CrystalMaps/'
            checkFolder(finaldirectorySaveCMCM)
            finaldirectorySaveE = finaldirectorySaveCMCM + 'EneResolution/'
            checkFolder(finaldirectorySaveE)
            finaldirectorySaveM = finaldirectorySaveCMCM + 'MeanValues/'
            checkFolder(finaldirectorySaveM)
            if title == "E_r(%FWHM)":
                plt.savefig('{}CrystalMaps/EneResolution/Er-{}.png'.format(pathtodirectorySaveCM, HVD))
            elif title == 'Mean':
                plt.savefig('{}CrystalMaps/MeanValues/MeanV-{}.png'.format(pathtodirectorySaveCM, HVD))
        else:
            plt.show()
# to distinguish between layers and plot it to check better energy resolution
# rows, dic_crystal_test = CrystalDict()
# rows = np.array(rows)

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                             directory where to read the files from.')
parser.add_argument('--saveDirectory', dest='saveDirect', help='Specifiy the name of the   \
                                             directory where to save the files in.', default='None')
parser.add_argument('--auto', dest='auto', help='Automatically plot everything (Default Off) e.g. "--auto On".', default='Off')
args = parser.parse_args()

pathtodirectory, pathtodirectorySaveCM, auto = args.fileDirect, args.saveDirect, args.auto

pathtodirectoryRead = pathtodirectory + 'Parallel/'

pathtodirectorySave = pathtodirectoryRead

pathtoPV = 'PhotonSpectrum/'

checkFolder(pathtodirectorySaveCM)

HVD_list = ['000', '100', '010', '111']
dic_calFactor_000 = {}
dic_calFactor_100 = {}
dic_calFactor_010 = {}
dic_calFactor_111 = {}

dic_calFactor_000 = dic_calFactor_HVD(pathtodirectoryRead + pathtoPV, '000', dic_calFactor_000)
dic_calFactor_100 = dic_calFactor_HVD(pathtodirectoryRead + pathtoPV, '100', dic_calFactor_100)
dic_calFactor_010 = dic_calFactor_HVD(pathtodirectoryRead + pathtoPV, '010', dic_calFactor_010)
dic_calFactor_111 = dic_calFactor_HVD(pathtodirectoryRead + pathtoPV, '111', dic_calFactor_111)

list_dic_calFactor = [dic_calFactor_000, dic_calFactor_100, dic_calFactor_010, dic_calFactor_111]
variable = 0

with open('{}Jobs_list.pickle'.format(pathtodirectoryRead), 'rb') as handle:
    list_Events = pickle.load(handle)  # 000, 100, 010, 111

if auto == 'On':
    for HVD in range(4):
        # WHEN ROW OR LAYER IS SELECTED; CRYSTAL IS -1
        # add option to create log with selected data
        data1_m, data2_m, data3_m, data1_er, data2_er, data3_er = Counts_in_layers(list_dic_calFactor[HVD], HVD_list[HVD],
                                                                                   list_Events)
        CrytalMap = Plot_Crystal_Map()
        CrytalMap.runPlot(data1_m, data2_m, data3_m, 'Mean', pathtodirectorySaveCM, HVD_list[HVD])
        CrytalMap.runPlot(data1_er, data2_er, data3_er, "E_r(%FWHM)", pathtodirectorySaveCM, HVD_list[HVD])
else:
    while variable != "quit": #CREATE ARGPARSE TO PARSE INPUT WITH ROW; LAYER; CRYSTAL
        #WHEN ROW OR LAYER IS SELECTED; CRYSTAL IS -1
        #add option to show plot
        #add option to create log with selected data
        variable = raw_input('Enter index (0->000, 1->100, 2->010, 3->111) or "quit" to exit: ')
        if variable == "quit":
            continue
        HVD = int(variable.split(',')[0])

        data1_m, data2_m, data3_m, data1_er, data2_er, data3_er = Counts_in_layers(list_dic_calFactor[HVD], HVD_list[HVD], list_Events)
        CrytalMap = Plot_Crystal_Map()
        CrytalMap.runPlot(data1_m, data2_m, data3_m, 'Mean', pathtodirectorySaveCM, HVD_list[HVD])
        CrytalMap.runPlot(data1_er, data2_er, data3_er, "E_r(%FWHM)", pathtodirectorySaveCM, HVD_list[HVD])
