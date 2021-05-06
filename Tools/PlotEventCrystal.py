# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 14:58:33 2021
@author: David
"""
import pandas as pd

import numpy as np
import cPickle as pickle
import h5py
import argparse
from textwrap import dedent
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch
from matplotlib.colors import LogNorm
import itertools
import time
import os

def checkFolder(pathDirectory):
    CHECK_FOLDER = os.path.isdir(pathDirectory)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathDirectory)
        print("created folder : ", pathDirectory)
def CrystalDict():
    """!
    Define Crystal identification dictionary with respective ids for all the peaks
    based on the different layers

    @return: rows =  ids of crystal ordered by row and column,
        dic_crystal_test = id from crystals
    @rtype: 2D-arr, dict
    """
    m = 1
    row = []
    j = 0
    p = 0
    rows = []
    dic_crystal_test = {}
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
                        'cluster': [],
                        'valid': False
                    }
                    dic_crystal_test[r] = peakii
                else:
                    if n % 2 != 0:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'cluster': [],
                            'valid': False
                        }
                        dic_crystal_test[r] = peakii
                    else:
                        peakjj = {
                            'row': j,
                            'layer': 2,
                            'id': r,
                            'cluster': [],
                            'valid': False
                        }
                        dic_crystal_test[r] = peakjj

            row = []
            j += 1
            p += 1

        elif i >= (65 * m + 31 * p) and j % 2 != 0:
            row_neg = [-1] * len(row)
            new_row = list(itertools.chain(*zip(row_neg, row)))
            new_row.append(-1)
            new_row.append(-1)
            new_row.insert(0,-1)

            rows.append(new_row)
            for r in row:
                peakkk = {
                    'row': j,
                    'layer': 3,
                    'id': r,
                    'cluster': [],
                    'valid': False
                }
                dic_crystal_test[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)

    return rows, dic_crystal_test
def __read_data_COG(HVD, pathtodirectoryReadHDF5):

    with h5py.File("{}cog{}ref.hdf5".format(pathtodirectoryReadHDF5, HVD),
                   "r") as f:
        dset = f["data"]
        cogHVDref = dset[:]  # 000, 100, 010, 111

    return cogHVDref

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                             directory where to read the files from')
parser.add_argument('--saveDirectory', dest='saveDirect', help='Specifiy the name of the   \
                                             directory where to read the files from', default='None')
parser.add_argument('--auto', dest='auto', help='Automatically plot everything (Default Off) e.g. "--auto On".', default='Off')
args = parser.parse_args()

pathtodirectoryRead, pathtodirectorySaveCM, auto = args.fileDirect, args.saveDirect, args.auto

pathtodirectoryReadCC = pathtodirectoryRead + 'Parallel/'
pathtoHDF5 = pathtodirectoryRead + 'hdf5Data/'

pathtodirectorySave = pathtodirectoryRead

checkFolder(pathtodirectorySaveCM)

variable = 0
rows, dic_crystal_test = CrystalDict()
rows = np.array(rows)

print("importing...")
with open('{}dic_crystal_cluster.pickle'.format(pathtodirectoryReadCC), 'rb') as handle:
    dic_crystal_cluster = pickle.load(handle)

cog000ref = __read_data_COG("000", pathtoHDF5)
cog100ref = __read_data_COG("100", pathtoHDF5)
cog010ref = __read_data_COG("010", pathtoHDF5)
cog111ref = __read_data_COG("111", pathtoHDF5)
print('imported.')

x_size = 3.8016
y_size = 3.2
pix_x = [-21.95982, -18.04018, -13.95982, -10.04018, -5.95982, -2.04018, 2.04018, 5.98982, 10.04018, 13.95982,
         18.04018, 21.95982]
pix_y = [21.6704, 18.3296, 13.6704, 10.3296, 5.6704, 2.3296, -2.3296, -5.6704, -10.3296, -13.6704, -18.3296,
         -21.6704]

if auto == 'On':
    for layer in range(1,4):
        # WHEN ROW OR LAYER IS SELECTED; CRYSTAL IS -1
        # add option to show plot
        # add option to create log with selected data

        layer = int(layer)
        row = int(-1)
        column = int(-1)
        i_crystal_input = int(-1)

        if column != -1:
            list_column = rows[:, column]
        else:
            list_column = [-1]

        list_clusters = []
        for i_crystal in dic_crystal_test.keys():
            if dic_crystal_test[i_crystal]["layer"] == layer or layer == -1:
                if dic_crystal_test[i_crystal]["row"] == row or row == -1:
                    if dic_crystal_test[i_crystal]["id"] in list_column or column == -1:
                        if dic_crystal_test[i_crystal]["id"] == i_crystal_input or i_crystal_input == -1:
                            list_clusters = list_clusters + dic_crystal_cluster[
                                i_crystal]  # we get crystals that we want and obtain the list of clusters that belong to those crystals
        x_hist_000 = []
        y_hist_000 = []
        x_hist_100 = []
        y_hist_100 = []
        x_hist_010 = []
        y_hist_010 = []
        x_hist_111 = []
        y_hist_111 = []

        for cluster in list_clusters:
            # import cogref from 000,100,010 or 111
            # take coordinates and plot and so
            # or import whole file, but not necessary, I think
            # add tileID
            x_hist_000.append(cog000ref[cluster][0])
            y_hist_000.append(cog000ref[cluster][1])
            x_hist_100.append(cog100ref[cluster][0])
            y_hist_100.append(cog100ref[cluster][1])
            x_hist_010.append(cog010ref[cluster][0])
            y_hist_010.append(cog010ref[cluster][1])
            x_hist_111.append(cog111ref[cluster][0])
            y_hist_111.append(cog111ref[cluster][1])

        fig, _axs = plt.subplots(2, 2, figsize=(25, 25))
        axs = _axs.flatten()
        # 000
        ax0 = axs[0]
        hist0 = ax0.hist2d(x_hist_000, y_hist_000, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax0.set_xlim([-24.5, 24.5])
        # ax0.set_ylim([-25.7, 25.7])
        fig.colorbar(hist0[3], ax=ax0)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax0.add_patch(rect)
        ax0.set_title('000')

        # 100
        ax1 = axs[1]
        hist1 = ax1.hist2d(x_hist_100, y_hist_100, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax1.set_xlim([-24.5, 24.5])
        # ax1.set_ylim([-25.7, 25.7])
        fig.colorbar(hist1[3], ax=ax1)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax1.add_patch(rect)
        ax1.set_title('100')

        # 010
        ax2 = axs[2]
        hist2 = ax2.hist2d(x_hist_010, y_hist_010, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax2.set_xlim([-24.5, 24.5])
        # ax2.set_ylim([-25.7, 25.7])
        fig.colorbar(hist2[3], ax=ax2)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax2.add_patch(rect)
        ax2.set_title('010')

        # 111
        ax3 = axs[3]
        hist3 = ax3.hist2d(x_hist_111, y_hist_111, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax3.set_xlim([-24.5, 24.5])
        # ax3.set_ylim([-25.7, 25.7])
        fig.colorbar(hist3[3], ax=ax3)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax3.add_patch(rect)
        ax3.set_title('111')

        plt.setp(_axs[-1, :], xlabel='x')
        plt.setp(_axs[:, 0], ylabel='y')

        plt.suptitle('Layer,Row,Col,Id_{},-1,-1,-1'.format(layer))

        if pathtodirectorySaveCM != 'None':
            finaldirectorySave = pathtodirectorySaveCM + 'ClusterMaps/'
            checkFolder(finaldirectorySave)
            plt.savefig('{}Layer,Row,Col,Id_{},-1,-1,-1.png'.format(finaldirectorySave, layer))
        else:
            plt.show()
else:
    while variable != "quit": #CREATE ARGPARSE TO PARSE INPUT WITH ROW; LAYER; CRYSTAL
        #WHEN ROW OR LAYER IS SELECTED; CRYSTAL IS -1
        #add option to show plot
        #add option to create log with selected data
        variable = raw_input("Enter layer (1, 2 or 3), row, column, id of the crystal or type 'quit' to exit: /n"+
                             "Example:'1,2,-1,-1' /n"+ "Hints: '-1' means 'all'. There may be rows only with crystals from layer 3 or from layer 1,2. There might be crystal not belonging to the indicated row/column/layer. ")
        if variable == "quit":
            continue
        #myFunc(["first", "2", "-1"])
        layer = int(variable.split(',')[0])
        row = int(variable.split(',')[1])
        column = int(variable.split(',')[2])
        i_crystal_input = int(variable.split(',')[3])

        if column != -1:
            list_column = rows[:,column]
        else:
            list_column = [-1]

        list_clusters = []
        for i_crystal in dic_crystal_test.keys():
            if dic_crystal_test[i_crystal]["layer"] == layer or layer == -1:
                if dic_crystal_test[i_crystal]["row"] == row or row == -1:
                    if dic_crystal_test[i_crystal]["id"] in list_column or column == -1:
                        if dic_crystal_test[i_crystal]["id"] == i_crystal_input or i_crystal_input == -1:
                            list_clusters = list_clusters + dic_crystal_cluster[i_crystal]              #we get crystals that we want and obtain the list of clusters that belong to those crystals
        x_hist_000 = []
        y_hist_000 = []
        x_hist_100 = []
        y_hist_100 = []
        x_hist_010 = []
        y_hist_010 = []
        x_hist_111 = []
        y_hist_111 = []

        for cluster in list_clusters:
            # import cogref from 000,100,010 or 111
            # take coordinates and plot and so
            # or import whole file, but not necessary, I think
            #add tileID
            x_hist_000.append(cog000ref[cluster][0])
            y_hist_000.append(cog000ref[cluster][1])
            x_hist_100.append(cog100ref[cluster][0])
            y_hist_100.append(cog100ref[cluster][1])
            x_hist_010.append(cog010ref[cluster][0])
            y_hist_010.append(cog010ref[cluster][1])
            x_hist_111.append(cog111ref[cluster][0])
            y_hist_111.append(cog111ref[cluster][1])

        fig, _axs = plt.subplots(2, 2, figsize=(25,25))
        axs = _axs.flatten()
        #000
        ax0 = axs[0]
        hist0 = ax0.hist2d(x_hist_000, y_hist_000, bins=1000, range=[[-24, 24], [-24, 24]],
                          norm=LogNorm())
        # ax0.set_xlim([-24.5, 24.5])
        # ax0.set_ylim([-25.7, 25.7])
        fig.colorbar(hist0[3], ax=ax0)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax0.add_patch(rect)
        ax0.set_title('000')

        # 100
        ax1 = axs[1]
        hist1 = ax1.hist2d(x_hist_100, y_hist_100, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax1.set_xlim([-24.5, 24.5])
        # ax1.set_ylim([-25.7, 25.7])
        fig.colorbar(hist1[3], ax=ax1)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax1.add_patch(rect)
        ax1.set_title('100')

        # 010
        ax2 = axs[2]
        hist2 = ax2.hist2d(x_hist_010, y_hist_010, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax2.set_xlim([-24.5, 24.5])
        # ax2.set_ylim([-25.7, 25.7])
        fig.colorbar(hist2[3], ax=ax2)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax2.add_patch(rect)
        ax2.set_title('010')

        # 111
        ax3 = axs[3]
        hist3 = ax3.hist2d(x_hist_111, y_hist_111, bins=1000, range=[[-24, 24], [-24, 24]],
                           norm=LogNorm())
        # ax3.set_xlim([-24.5, 24.5])
        # ax3.set_ylim([-25.7, 25.7])
        fig.colorbar(hist3[3], ax=ax3)
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i - x_size / 2, pix_y_i - y_size / 2), x_size, y_size, linewidth=0.5,
                                     edgecolor="dimgray", facecolor="none")
                ax3.add_patch(rect)
        ax3.set_title('111')

        plt.setp(_axs[-1, :], xlabel='x')
        plt.setp(_axs[:, 0], ylabel='y')

        plt.suptitle('Layer,Row,Col,Id_{}'.format(variable))

        if pathtodirectorySaveCM != 'None':
            finaldirectorySave = pathtodirectorySaveCM + 'ClusterMaps/'
            checkFolder(finaldirectorySave)
            plt.savefig('{}Layer,Row,Col,Id_{}.png'.format(finaldirectorySave, variable))
        else:
            plt.show()