# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:51 2020

@author: David
"""

import pickle as pickle
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

class C_Group(object):
    def __init__(self, splits, pathtodirectoryRead, pathtodirectorySavePV):
        # print("Diese Splits", splits)
        self.splits = splits

        self.HVD_list = ["000", "100", "010", "111"]

        self.pathtodirectoryRead = pathtodirectoryRead
        self.pathtodirectorySavePV = pathtodirectorySavePV
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

        self.pathtodirectorySave = self.pathtodirectoryRead

        # self.pathtodirectorySavePV = 'PV/'

        # CHECK_FOLDER = os.path.isdir(self.pathtodirectorySave + self.pathtodirectorySavePV)
        # # If folder doesn't exist, then create it.
        # if not CHECK_FOLDER:
        #     os.makedirs(self.pathtodirectorySave + self.pathtodirectorySavePV)
        #     print("created folder : ", self.pathtodirectorySave + self.pathtodirectorySavePV)

    def __group_Events_Counts(self, final_event, dic_Events_Counts): #not only update, but append!!!!!!!!!!!!!!!!!!!!!
        with open('{}dic-Events{}-Counts.pickle'.format(self.pathtodirectorySave, final_event), 'rb') as handle:
            dic_Events_Counts_temp = pickle.load(handle)
            if dic_Events_Counts:
                for k in dic_Events_Counts_temp.keys():
                    dic_Events_Counts[k] += dic_Events_Counts_temp[k]
            else:
                dic_Events_Counts = dic_Events_Counts_temp
        return dic_Events_Counts

    def __group_Assign_Events(self, final_event, dic_AssignE): #not only update, but append!!!!!!!!!!!!!!!!!!!!!
        with open('{}dic_AssignE{}.pickle'.format(self.pathtodirectorySave, final_event), 'rb') as handle:
            dic_AssignE_temp = pickle.load(handle)
            if dic_AssignE:
                for k in dic_AssignE_temp.keys():
                    for cry in dic_AssignE_temp[k].keys():
                        dic_AssignE[k][cry]['n_events'] += dic_AssignE_temp[k][cry]['n_events']
            else:
                dic_AssignE = dic_AssignE_temp
        return dic_AssignE

    def __group_calib_PV(self, final_event, data_cluster_calib_pv_all, dic_crystal_cluster):
        with open('{}dic_calibPV{}.pickle'.format(self.pathtodirectorySave, final_event), 'rb') as handle:
            dic_temp = pickle.load(handle)
            # data_cluster_calib_pv_all.update(dic_temp)  # 000, 100, 010, 111
        for cluster in dic_temp.keys():
            dic_crystal_cluster[dic_temp[cluster]['id']].append(cluster)

        return data_cluster_calib_pv_all, dic_crystal_cluster

    def __group_PV_in_HVD(self, final_event, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111):
        data_cluster_pv_list = [data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111]
        # not only update, but append!!!!!!!!!!!!!!!!!!!!!
        for cg in range(4):
            HVD = self.HVD_list[cg]
            #data_cluster_pv_list[cg]
            data_cluster_pv_HVD_temp = {}
            with open('{}datapv-{}-valid{}.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySavePV, HVD,
                                                          final_event), 'rb') as handle:
                data_cluster_pv_HVD_temp = pickle.load(handle)
                if data_cluster_pv_list[cg]:
                    for k in data_cluster_pv_HVD_temp.keys():
                        if data_cluster_pv_HVD_temp[k]['pv']:
                            for pv in data_cluster_pv_HVD_temp[k]['pv']:
                                data_cluster_pv_list[cg][k]['pv'].append(pv)
                else:
                    data_cluster_pv_list[cg] = data_cluster_pv_HVD_temp
        return data_cluster_pv_list[0], data_cluster_pv_list[1], data_cluster_pv_list[2], data_cluster_pv_list[3]#data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111

    def __save_Events_Counts(self, dic_Events_Counts):
        print('{}dic-Events-Counts.pickle'.format(self.pathtodirectorySave))
        with open('{}dic-Events-Counts.pickle'.format(self.pathtodirectorySave), 'wb') as handle:
            pickle.dump(dic_Events_Counts, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Assign_Events(self, dic_AssignE):
        print('{}dic_AssignE.pickle'.format(self.pathtodirectorySave))
        with open('{}dic_AssignE.pickle'.format(self.pathtodirectorySave), 'wb') as handle:
            pickle.dump(dic_AssignE, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_calib_PV(self, data_cluster_calib_pv_all):
        print('{}dic_calibPV.pickle'.format(self.pathtodirectorySave))
        with open('{}dic_calibPV.pickle'.format(self.pathtodirectorySave), 'wb') as handle:
            pickle.dump(data_cluster_calib_pv_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Crystal_Cluster(self, dic_crystal_cluster):
        print('{}dic_crystal_cluster.pickle'.format(self.pathtodirectorySave))
        with open('{}dic_crystal_cluster.pickle'.format(self.pathtodirectorySave), 'wb') as handle:
            pickle.dump(dic_crystal_cluster, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __PV_in_HVD(self, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111):

        data_cluster_pv_list = [data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111]

        for cg in range(4):
            HVD = self.HVD_list[cg]
            print('{}datapv-{}-valid.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySavePV, HVD))
            with open('{}datapv-{}-valid.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySavePV, HVD),
                      'wb') as handle:
                pickle.dump(data_cluster_pv_list[cg], handle,
                            protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)


    def runCGroup(self):
        data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111 = {},{},{},{}
        dic_Events_Counts = {}
        dic_AssignE = {}
        data_cluster_calib_pv_all = {}
        dic_crystal_cluster = {}
        for i in range(3425):
            dic_crystal_cluster[i] = []
        print('Grouping...')
        # print(self.splits)
        # self.splits = ["2553191", "5106382"] #Meins
        for sp in self.splits:
            final_event = sp[1] #MEINS
            # print("SPSPSPSP:", sp)
            # final_event = sp #MEINS
            try:
                data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111 = self.__group_PV_in_HVD(final_event, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111)
            except:
                print("Problem grouping PV.")

            try:
                dic_Events_Counts = self.__group_Events_Counts(final_event, dic_Events_Counts)
            except:
                print("Problem grouping dic_Events_Counts.")

            try:
                dic_AssignE = self.__group_Assign_Events(final_event, dic_AssignE)
            except:
                print("Problem grouping AssignE.")

            try:
                data_cluster_calib_pv_all, dic_crystal_cluster = self.__group_calib_PV(final_event, data_cluster_calib_pv_all, dic_crystal_cluster)
            except:
                print("Problem grouping CalibPV.")
        print('Saving...')
        try:
            self.__PV_in_HVD(data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111)
            print("PV is saved.")
        except:
            print("Problem saving PV.")

        try:
            self.__save_Events_Counts(dic_Events_Counts)
            print("dic_Events_Counts is saved.")
        except:
            print("Problem saving dic_Events_Counts.")

        try:
            self.__save_Assign_Events(dic_AssignE)
            print("AssignE is saved.")
        except:
            print("Problem saving AssignE.")

        self.__save_Crystal_Cluster(dic_crystal_cluster)

        try:
            self.__save_calib_PV(data_cluster_calib_pv_all)
            print("CalibPV is saved.")
        except:
            print("Problem saving CalibPV.")
        print('Saved.')

