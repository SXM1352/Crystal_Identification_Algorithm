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
import argparse
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
                        'n_events': 0
                    }
                    dic_crystal_test[r] = peakii
                else:
                    if n % 2 != 0:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'n_events': 0
                        }
                        dic_crystal_test[r] = peakii
                    else:
                        peakjj = {
                            'row': j,
                            'layer': 2,
                            'id': r,
                            'n_events': 0
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
                    'n_events': 0
                }
                dic_crystal_test[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)

    return dic_crystal_test

def Counts_in_layers(dic_Assign):
    dic_labels_count_layer1 = {}
    dic_labels_count_layer2 = {}
    dic_labels_count_layer3 = {}

    dic_crystal = CrystalDict() #not necessary, but faster?

    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 1:
            dic_labels_count_layer1[i] = dic_Assign[i]["n_events"]
    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 2:
            dic_labels_count_layer2[i] = dic_Assign[i]["n_events"]
    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 3:
            dic_labels_count_layer3[i] = dic_Assign[i]["n_events"]

    data1 = np.zeros((36, 34))
    data2 = np.zeros((36, 31))
    data3 = np.zeros((35, 31))
    print("svae")
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer1.keys()):
        data1[index][index2] = dic_labels_count_layer1[i]
        index2 += 1
        if index2 == 34:
            index2 = 0
            index += 1
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer2.keys()):
        data2[index][index2] = dic_labels_count_layer2[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer3.keys()):
        data3[index][index2] = dic_labels_count_layer3[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
    return data1, data2, data3

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                             directory where to read the files from')
parser.add_argument('--saveDirectory', dest='saveDirect', help='Specifiy the name of the   \
                                             directory where to read the files from', default='None')
parser.add_argument('--DecisionTag', dest='DT', help='Specifiy the name of the   \
                                             decision tag that you want to plot', default='-1')
args = parser.parse_args()

pathtodirectoryRead, pathtodirectorySaveCM, DT = args.fileDirect, args.saveDirect, args.DT

pathtodirectoryReadCC = pathtodirectoryRead + 'Parallel/'
pathtoHDF5 = pathtodirectoryRead + 'hdf5Data/'

pathtodirectorySave = pathtodirectorySaveCM

checkFolder(pathtodirectorySaveCM)

with open('{}dic_AssignE.pickle'.format(pathtodirectoryReadCC), 'rb') as handle:
    dic_AssignE = pickle.load(handle)  # 000, 100, 010, 111

from LabelsPlots import Plot_Labels_with_Values

if DT == '-1':
    for data_name in dic_AssignE.keys():
        data1, data2, data3 = Counts_in_layers(dic_AssignE["{}".format(data_name)])

        Assign = Plot_Labels_with_Values()
        Assign.runPlot(data1, data2, data3, "{}".format(data_name), pathtodirectorySaveCM)
else:
    data_name = DT

    data1, data2, data3 = Counts_in_layers(dic_AssignE["{}".format(data_name)])

    Assign = Plot_Labels_with_Values()
    Assign.runPlot(data1, data2, data3, "{}".format(data_name), pathtodirectorySaveCM)

# except:
#     with open('{}dic-126894299cluster.pickle'.format(pathtodirectoryRead), 'rb') as handle:
#         dic_cluster = pickle.load(handle)  # 000, 100, 010, 111
#
#     dic_AssignE = {}
#     dic_AssignE["ALL"] = CrystalDict()
#     dic_AssignE["three_100_111_010"] = CrystalDict()
#     dic_AssignE["three_000_010_100"] = CrystalDict()
#     dic_AssignE["three_100_111_000"] = CrystalDict()
#     dic_AssignE["three_010_111_000"] = CrystalDict()
#     dic_AssignE["two_010_100"] = CrystalDict()
#     dic_AssignE["two_010_111"] = CrystalDict()
#     dic_AssignE["two_100_111"] = CrystalDict()
#     dic_AssignE["two_000_111"] = CrystalDict()
#     dic_AssignE["two_000_010"] = CrystalDict()
#     dic_AssignE["two_000_100"] = CrystalDict()
#     dic_AssignE["000_QF"] = CrystalDict()
#     dic_AssignE["100_QF"] = CrystalDict()
#     dic_AssignE["010_QF"] = CrystalDict()
#     dic_AssignE["111_QF"] = CrystalDict()
#     dic_AssignE["000_ONLY_VALID"] = CrystalDict()
#     dic_AssignE["100_ONLY_VALID"] = CrystalDict()
#     dic_AssignE["010_ONLY_VALID"] = CrystalDict()
#     dic_AssignE["111_ONLY_VALID"] = CrystalDict()
#
#
#     for i in dic_cluster.keys():
#         if len(dic_cluster[i].keys()) > 3:  # only the valid ones
#             for j in dic_Events.keys():
#                 if dic_Events[j] == dic_cluster[i]["COG_ALL"]:
#                     if dic_cluster[i]['COG'].endswith('_ONLY_VALID') or dic_cluster[i]['COG'].endswith('_QF'):
#                         dic_AssignE[dic_cluster[i]['COG']][dic_cluster[i]["id"]]['n_events'] += 1
#                     else:
#                         dic_AssignE[j][dic_cluster[i]["id"]]['n_events'] += 1
#
#     with open('{}dic_AssignE.pickle'.format(pathtodirectorySave), 'wb') as handle:
#         pickle.dump(dic_AssignE, handle,
#                     protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)




