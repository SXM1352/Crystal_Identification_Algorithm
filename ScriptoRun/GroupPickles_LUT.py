# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:51 2020

@author: David
"""

import cPickle as pickle
import numpy as np
import atexit
from time import clock
import time
import h5py
import os
import itertools
import pandas as pd

# from multiprocessing import Manager,Pool,Lock
import psutil  # process and systems utils
# import multiprocessing as mp

class LUT_Group(object):
    def __init__(self, splits, pathtodirectoryRead):

        self.splits = splits

        self.HVD_list = ["000", "100", "010", "111"]

        self.pathtodirectoryRead = pathtodirectoryRead

        self.pathtodirectorySave = self.pathtodirectoryRead
        self.pathtodirectorySaveLUT = 'dic-LUD/'

        CHECK_FOLDER = os.path.isdir(self.pathtodirectorySave + self.pathtodirectorySaveLUT)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(self.pathtodirectorySave + self.pathtodirectorySaveLUT)
            print("created folder : ", self.pathtodirectorySave + self.pathtodirectorySaveLUT)

    def __group_LUT_in_HVD(self, final_event, data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111):
        data_LUT_list = [data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111]
        # not only update, but append!!!!!!!!!!!!!!!!!!!!!
        for cg in range(4):
            HVD = self.HVD_list[cg]
            #data_LUT_list[cg]
            data_cluster_LUT_HVD_temp = {}
            with open('{}dic-LUD-{}-{}.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySaveLUT, HVD,
                                                          final_event), 'rb') as handle:
                data_cluster_LUT_HVD_temp = pickle.load(handle)
                data_LUT_list[cg].update(data_cluster_LUT_HVD_temp)
                # if data_LUT_list[cg]:
                #     for k in data_cluster_LUT_HVD_temp.keys():
                #         if data_cluster_LUT_HVD_temp[k]:
                #             data_LUT_list[cg][k] =
                # else:
                #     data_LUT_list[cg] = data_cluster_LUT_HVD_temp
        return data_LUT_list[0], data_LUT_list[1], data_LUT_list[2], data_LUT_list[3]#data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111

    def __LUT_in_HVD(self, data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111):

        data_LUT_list = [data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111]

        for cg in range(4):
            HVD = self.HVD_list[cg]
            with open('{}dic-LUD-{}.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySaveLUT, HVD),
                      'wb') as handle:
                pickle.dump(data_LUT_list[cg], handle,
                            protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)


    def runLUTGroup(self):
        data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111 = {},{},{},{}

        print('Grouping...')
        for sp in self.splits:
            final_event = sp[1]
            # try:
            data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111 = self.__group_LUT_in_HVD(final_event, data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111)
            # except:
            #     print("Problem grouping PV.")


        print('Saving...')
        # try:
        self.__LUT_in_HVD(data_LUT_000, data_LUT_100, data_LUT_010, data_LUT_111)
        #     print("PV is saved.")
        # except:
        #     print("Problem saving PV.")

        print('Saved.')

