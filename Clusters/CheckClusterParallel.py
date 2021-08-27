# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:51 2020

@author: David
"""
"""
RunCheckParallel.py provides a routine to iterate over the clusters and
identify the scintillating crystal.
"""

import cPickle as pickle
import numpy as np
import atexit
from time import clock
import time
import h5py
import os
import pandas as pd

# from multiprocessing import Manager,Pool,Lock
import psutil  # process and systems utils
# import multiprocessing as mp
# from multiprocess import Lock
# import pathos.multiprocessing as mp
import gc  # garbage collector

class C_Cluster(object):

    def __init__(self, init_event, final_event, start, dic_Events, dic_AssignE, pathtodirectoryRead, decimals, stack_type):
        self.line = "=" * 40
        print("Oder startet direkt der Bums hier?")
        # self.lock = Lock()

        self.start = start
        self.dic_Events = dic_Events
        self.dic_AssignE = dic_AssignE

        self.init_event = init_event
        self.final_event = final_event

        self.HVD_list = ["000", "100", "010", "111"]
        self.decimals = int(decimals) # 2 = 0.01

        self.stack_type = stack_type

        self.pathtodirectoryRead = pathtodirectoryRead
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

        self.pathtodirectoryReadLUD = 'dic-LUD/'
        self.pathtodirectoryReadHDF5 = 'hdf5Data/'
        # self.pathtodirectoryReadLUD = '20210304_NEW-2021-02-17_dic-LUD/'
        # self.pathtodirectoryReadHDF5 = '20210302_NEW-2021-02-17_hdf5Data/'
        # self.pathtodirectoryReadLUD = '20210303_NEW-2021-02-17_dic-LUD/'
        # self.pathtodirectoryReadHDF5 = '20210302_NEW-2021-02-17_hdf5Data/'
        # self.pathtodirectoryReadLUD = '20210315_NEW_dic-LUD/'
        # self.pathtodirectoryReadHDF5 = '20210315_NEW_hdf5Data/'

        self.pathtodirectorySave = self.pathtodirectoryRead + 'Parallel/'
        # self.pathtodirectorySave = "/media/janko.lambertus/pet-scratch/Janko/Master/Data/CIA_FT/Parallel/"
        self.pathtodirectorySavePV = 'PhotonSpectrum/'
        # self.pathtodirectorySavePV = '20210304_NEW-2021-02-17_PhotonSpectrum/'
        # self.pathtodirectorySavePV = '20210303_NEW-2021-02-17_PhotonSpectrum/'
        # self.pathtodirectorySavePV = '20210315_NEW_PhotonSpectrum/'

        # self.pathtodirectorySave = '/home/david.perez/TestParallel/'
        # self.pathtodirectorySavePV = 'PV/'

        self.fout_dic_Cluster = '{}dic_Cluster{}.hdf5'.format(self.pathtodirectorySave, self.final_event)
        print("SELF.FOUT_DIC_CLUSTER: ", self.fout_dic_Cluster)

        self.fout_dic_notSelectedCluster = '{}dic-notSelected-Cluster{}.hdf5'.format(self.pathtodirectorySave, self.final_event)

        CHECK_FOLDER = os.path.isdir(self.pathtodirectorySave + self.pathtodirectorySavePV)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(self.pathtodirectorySave + self.pathtodirectorySavePV)
            print("created folder : ", self.pathtodirectorySave + self.pathtodirectorySavePV)

        CHECK_FILE = os.path.isfile(self.fout_dic_Cluster)
        # If folder doesn't exist, then create it.
        if CHECK_FILE:
            os.remove(self.fout_dic_Cluster)
            print("Modified file : ", self.fout_dic_Cluster)

        CHECK_FILE = os.path.isfile(self.fout_dic_notSelectedCluster)
        # If folder doesn't exist, then create it.
        if CHECK_FILE:
            os.remove(self.fout_dic_notSelectedCluster)
            print("Modified file : ", self.fout_dic_notSelectedCluster)

        # ADD DIRECTORIES TO READ FILES AND TO SAVE FILES

    def __secondsToStr(self, t):
        return "%d:%02d:%02d.%03d" % \
               reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                      [(t * 1000,), 1000, 60, 60])

    def __log(self, s, elapsed=None):
        print(self.line)
        print(self.__secondsToStr(clock()), '-', s)
        if elapsed:
            print("Elapsed time:", elapsed)
        print(self.line)

    def __endlog(self):
        end = clock()
        elapsed = end - self.start
        self.__log("End Program", self.__secondsToStr(elapsed))

    def __now(self):
        return self.__secondsToStr(clock())

    def __read_data_COG(self, HVD):
        try:
            print("Read: {}hdf5Data/pv{}test.pickle".format(self.pathtodirectoryRead, HVD))
            with open("{}/hdf5Data/pv{}test.pickle".format(self.pathtodirectoryRead, HVD), 'rb') as handle:
                pvHVDtest = pickle.load(handle)  # 000, 100, 010, 111 order of columns!!!
        except:
            "{}hdf5Data/pv{}test.pickle doesn work".format(self.pathtodirectoryRead, HVD)

        try:
            print('Read: {}hdf5Data/cog{}test.pickle'.format(self.pathtodirectoryRead, HVD))
            with open('{}/hdf5Data/cog{}test.pickle'.format(self.pathtodirectoryRead, HVD), 'rb') as handle:
                cogHVDtest = pickle.load(handle)  # 000, 100, 010, 111 order of columns!!!
        except:
            print('{}hdf5Data/cog{}test.pickle doesn work'.format(self.pathtodirectoryRead, HVD))
            cogHVDtest = -1

        try:
            print('Read: {}dic-LUD-{}.pickle'.format(self.pathtodirectoryRead + self.pathtodirectoryReadLUD, HVD))
            with open('{}dic-LUD-{}.pickle'.format(self.pathtodirectoryRead + self.pathtodirectoryReadLUD, HVD),
                      'rb') as handle:
                ludHVD = pickle.load(handle)  # 000, 100, 010, 111
        except:
            # print("dicLUD not available", HVD)
            print('{}dic-LUD-{}.pickle doesn \'t work'.format(self.pathtodirectoryRead + self.pathtodirectoryReadLUD, HVD))

        try:
            print("Read: {}cog{}ref{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type))
            with h5py.File("{}cog{}ref{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type),
                           "r") as f:
                dset = f["data"]
                cogHVDref = dset[self.init_event:self.final_event]  # 000, 100, 010, 111
        except:
            print('{}cog{}ref{}.hdf5 doesn\'t work'.format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type))

        try:
            print("Read: {}pv{}ref{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type))
            with h5py.File("{}pv{}ref{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type), "r") as f:
                dset = f["data"]
                pvHVDref = dset[self.init_event:self.final_event]  # 000, 100, 010, 111
        except:
            print("{}pv{}ref{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, HVD, self.stack_type))

        # with open('/home/david.perez/Desktop/pv{}ref.pickle'.format(HVD), 'rb') as handle:
        #     pvHVDref = pickle.load(handle) # 000, 100, 010, 111
        #
        # with open('/home/david.perez/Desktop/cog{}ref.pickle'.format(HVD), 'rb') as handle:
        #     cogHVDref = pickle.load(handle) # 000, 100, 010, 111

        return cogHVDtest, pvHVDtest, ludHVD, pvHVDref, cogHVDref

    def __CrystalDict(self):
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
                            'pv': []
                        }
                        dic_crystal[r] = peakii
                    else:
                        if n % 2 != 0:
                            peakii = {
                                'row': j,
                                'layer': 1,
                                'id': r,
                                'pv': []
                            }
                            dic_crystal[r] = peakii
                        else:
                            peakjj = {
                                'row': j,
                                'layer': 2,
                                'id': r,
                                'pv': []
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
                        'pv': []
                    }
                    dic_crystal[r] = peakkk
                row = []
                j += 1
                m += 1
            else:
                pass
            row.append(i)

        return dic_crystal

    def __getDuplicatesWithCount(self, listOfElems):
        ''' Get frequency count of duplicate elements in the given list '''
        dictOfElems = dict()
        # Iterate over each element in list
        for elem in listOfElems:
            # If element exists in dict then increment its value else add it in dict
            if elem in dictOfElems:
                dictOfElems[elem] += 1
            else:
                dictOfElems[elem] = 1

                # Filter key-value pairs in dictionary. Keep pairs whose value is greater than 1 i.e. only duplicate elements from list. There is no case where two labels are against two labels.
        dictOfElems = {key: value for key, value in dictOfElems.items() if value > 1}
        # Returns a dict of duplicate elements and their frequency count
        return dictOfElems

    def __Checker(self, cgt, i, cog000_i, cog100_i, cog010_i, cog111_i, pv000, pv100, pv010, pv111, decimals):
        pos000 = None
        pos010 = None
        pos100 = None
        pos111 = None

        id000 = None
        id010 = None
        id100 = None
        id111 = None

        qf = {}
        dic_Id = {}
        # print("First :", self.lud000[0], "Second :", self.lud000[0])
        # print("First :", self.lud000.keys())
        if self.lud000[round(cog000_i[0], decimals), round(cog000_i[1], decimals)] != None and self.lud000[round(cog000_i[0], decimals), round(cog000_i[1], decimals)]["CLOP"]["valid"] == True:
            pos000 = self.lud000[round(cog000_i[0], decimals), round(cog000_i[1], decimals)]
            id000 = pos000["CLOP"]["id"]
            qf[id000] = pos000["QF"]
            dic_Id["000"] = {"id": id000, "QF": qf[id000], "COORDS": pos000["CLOP"]["center"], "pv": pv000[i]}
        else:
            dic_Id["000"] = {"COORDS": [round(cog000_i[0], decimals), round(cog000_i[1], decimals)], "pv": pv000[i]}

        try:
            if self.lud100[round(cog100_i[0], decimals), round(cog100_i[1], decimals)] != None and self.lud100[round(cog100_i[0], decimals), round(cog100_i[1], decimals)]["CLOP"]["valid"] == True and cgt[1] == 1:  # if we want to include only valid from hitAnalysis
                pos100 = self.lud100[round(cog100_i[0], decimals), round(cog100_i[1], decimals)]  # introduce in each iteration
                id100 = pos100["CLOP"]["id"]
                qf[id100] = pos100["QF"]
                dic_Id["100"] = {"id": id100, "QF": qf[id100], "COORDS": pos100["CLOP"]["center"], "pv": pv100[i]}
            else:
                dic_Id["100"] = {"COORDS": [round(cog100_i[0], decimals), round(cog100_i[1], decimals)], "pv": pv100[i]}
        except:
            dic_Id["100"] = {"COORDS": [-30, 30], "pv": 0}
            self.lud100[round(cog100_i[0], decimals), round(cog100_i[1], decimals)] = [30, 30]

        try:
            if self.lud010[round(cog010_i[0], decimals), round(cog010_i[1], decimals)] != None and self.lud010[round(cog010_i[0], decimals), round(cog010_i[1], decimals)]["CLOP"]["valid"] == True and cgt[2] == 1:
                pos010 = self.lud010[round(cog010_i[0], decimals), round(cog010_i[1], decimals)]
                id010 = pos010["CLOP"]["id"]
                qf[id010] = pos010["QF"]
                dic_Id["010"] = {"id": id010, "QF": qf[id010], "COORDS": pos010["CLOP"]["center"], "pv": pv010[i]}
            else:
                dic_Id["010"] = {"COORDS": [round(cog010_i[0], decimals), round(cog010_i[1], decimals)], "pv": pv010[i]}
        except:
            dic_Id["010"] = {"COORDS": [-30, 30], "pv": 0}
            self.lud010[round(cog010_i[0], decimals), round(cog010_i[1], decimals)] = [30, 30]

        if self.lud111[round(cog111_i[0], decimals), round(cog111_i[1], decimals)] != None and self.lud111[round(cog111_i[0], decimals), round(cog111_i[1], decimals)]["CLOP"]["valid"] == True and cgt[3] == 1:
            pos111 = self.lud111[round(cog111_i[0], decimals), round(cog111_i[1], decimals)]
            id111 = pos111["CLOP"]["id"]
            qf[id111] = pos111["QF"]
            dic_Id["111"] = {"id": id111, "QF": qf[id111], "COORDS": pos111["CLOP"]["center"], "pv": pv111[i]}
        else:
            dic_Id["111"] = {"COORDS": [round(cog111_i[0], decimals), round(cog111_i[1], decimals)], "pv": pv111[i], 'Flag': cgt,
                             'LUT_000': self.lud000[round(cog000_i[0], decimals), round(cog000_i[1], decimals)],
                             'LUT_100': self.lud100[round(cog100_i[0], decimals), round(cog100_i[1], decimals)],
                             'LUT_010': self.lud010[round(cog010_i[0], decimals), round(cog010_i[1], decimals)],
                             'LUT_111': self.lud111[round(cog111_i[0], decimals), round(cog111_i[1], decimals)]}

        # List of strings
        listOfIds = [id100, id111, id010, id000]

        # Get a dictionary containing duplicate elements in list and their frequency count
        dictOfElems = self.__getDuplicatesWithCount(listOfIds)

        return qf, dictOfElems, dic_Id

    def __Repetition_of_Labels(self, key, dic_Id, dic_Events_Counts):
        COG = {}

        COG["000"] = False
        COG["100"] = False
        COG["010"] = False
        COG["111"] = False
        try:
            if key == dic_Id["000"]["id"]:
                COG["000"] = True
        except:
            pass
        try:
            if key == dic_Id["100"]["id"]:
                COG["100"] = True
        except:
            pass
        try:
            if key == dic_Id["010"]["id"]:
                COG["010"] = True
        except:
            pass
        try:
            if key == dic_Id["111"]["id"]:
                COG["111"] = True
        except:
            pass
        for i in self.dic_Events.keys():
            if self.dic_Events[i] == COG:
                dic_Events_Counts[i] += 1

        return COG, dic_Events_Counts

    def __multiple_Labels(self, dic_Id, dictOfElems, dic_labels_count, stop, dic_cluster, dic_Events_Counts, i):
        COG = None
        QF_final = 1.
        QF_2_final = -1
        COORD_final = -1
        COORD_2_final = -1
        COG_final = -1
        COG_2_final = -1
        # PV_final = -1
        # PV_2_final = -1
        id_2 = "-1"
        for key, value in dictOfElems.items():
            if key != None:
                if value > 1:  # the value which is more than once (repeated) is taken (it means that more than one COG indicates the same label for this event)
                    dic_labels_count[key] += 1
                    stop = True
                    COG_test, dic_Events_Counts = self.__Repetition_of_Labels(key, dic_Id, dic_Events_Counts)
                    for j in COG_test.keys():
                        if COG_test[j]:
                            try:
                                if dic_Id[j]["QF"] < QF_final:
                                    dic_cluster[i]["id"] = key
                                    QF_final = dic_Id[j]["QF"]
                                    COORD_final = dic_Id[j]["COORDS"]
                                    COG_final = j
                                    COG = COG_test
                                    # PV_final = dic_Id[j]["pv"]
                            except KeyError:
                                pass  # it could be that dic_Id does not have the corresponding key

                        else:
                            try:
                                if dic_Id[j]["QF"] < QF_2_final:
                                    QF_2_final = dic_Id[j]["QF"]
                                    COORD_2_final = dic_Id[j]["COORDS"]
                                    id_2 = dic_Id[j]["id"]
                                    COG_2_final = j
                                    # PV_2_final = dic_Id[j]["pv"]
                            except KeyError:
                                pass  # it could be that dic_Id does not have the corresponding key

                    dic_cluster[i]["QF"] = QF_final
                    dic_cluster[i]["COORDS"] = COORD_final
                    dic_cluster[i]["COG"] = COG_final
                    # dic_cluster[i]["pv"] = PV_final
                    dic_cluster[i]["COG_ALL"] = COG

                    if id_2 != "-1":  # we only define those variables if they are representatives
                        dic_cluster[i]["id_2"] = id_2
                        dic_cluster[i]["QF_2"] = QF_2_final
                        dic_cluster[i]["COORDS_2"] = COORD_2_final
                        dic_cluster[i]["COG_2"] = COG_2_final
                        # dic_cluster[i]["pv_2"] = PV_2_final

                    else:  # when not, the cog is shown as -1
                        dic_cluster[i]["COG_2"] = COG_2_final
                # SEPARATE TRUE FROM FALSE TO USE IT FOR FILLING THE DICTIONARY
        return dic_labels_count, stop, dic_cluster, COG, dic_Events_Counts

    def __Counter(self, dic_cluster, dic_notSelected_cluster, dic_Events_Counts, cog, dic_labels_count, cog000, cog100, cog010, cog111, pv000,
                  pv100, pv010, pv111):

        data_cluster_pv_000 = self.__CrystalDict()

        data_cluster_pv_100 = self.__CrystalDict()

        data_cluster_pv_010 = self.__CrystalDict()

        data_cluster_pv_111 = self.__CrystalDict()

        data_cluster_calib_pv_all = {}

        i = self.init_event #cluster identification (which event is it)
        
        decimals = self.decimals
        
        for i_cgt, cgt in enumerate(cog):
            # print("i_cgt: ", i_cgt, "        cgt: ", cgt, "         i: ", i)
            data_cluster_calib_pv = {'id': None, 'selected_pv': None,
                                     'COG': None}  # if one needs more pv values, one can go to the respected hdf5 file
            stop = False
            dic_cluster[i] = {}

            dic_cluster[i]["id"] = -1
            dic_cluster[i]["QF"] = -1.
            dic_cluster[i]["COORDS"] = -1.
            dic_cluster[i]["COG"] = -1.
            dic_cluster[i]["id_2"] = -1
            dic_cluster[i]["QF_2"] = -1.
            dic_cluster[i]["COORDS_2"] = -1.
            dic_cluster[i]["COG_2"] = -1.
            dic_cluster[i]['Cluster'] = i
            dic_cluster[i]['ROI'] = []

            dic_cluster[i]['Order_Coord'] = []
            dic_cluster[i]['ROI_2'] = []
            dic_cluster[i]['Order_Coord_2'] = []

            cog000_i = cog000[i_cgt]
            cog100_i = cog100[i_cgt]
            cog010_i = cog010[i_cgt]
            cog111_i = cog111[i_cgt]
            # print("BIG PROBLEM: ")
            # print("cgt", cgt)
            # print("i_cgt:", i_cgt)
            # print("cog000_i:", cog000_i)
            # print("cog100_i:", cog100_i)
            # print("cog010_i:", cog010_i)
            # print("cog111_i:", cog111_i)
            # print("pv000:", pv000)
            # print("pv100:", pv100)
            # print("pv010:", pv010)
            # print("pv111:", pv111)
            # print("decimals:", decimals)
            qf, dictOfElems, dic_Id = self.__Checker(cgt, i_cgt, cog000_i, cog100_i, cog010_i, cog111_i, pv000, pv100, pv010, pv111, decimals)

            dic_labels_count, stop, dic_cluster, COG, dic_Events_Counts = self.__multiple_Labels(dic_Id, dictOfElems,
                                                                                                 dic_labels_count, stop,
                                                                                                 dic_cluster,
                                                                                                 dic_Events_Counts, i)
            if not stop:
                bestQF = 1.  # min(qf.values())
                bestQF_2 = 1.
                bestId = "-1"
                bestId_2 = "-1"
                COORD_final = -1
                COORD_final_2 = -1
                COG_final = -1
                COG_final_2 = -1
                # PV_final = -1
                # PV_final_2 = -1

                for j_keys in dic_Id.keys():
                    try:
                        if dic_Id[j_keys]["QF"] < bestQF:  # when the peak is not valid it does not have QF
                            bestQF_2 = bestQF
                            bestId_2 = bestId
                            COORD_final_2 = COORD_final
                            COG_final_2 = COG_final
                            # PV_final_2 = PV_final

                            bestQF = dic_Id[j_keys]["QF"]
                            bestId = dic_Id[j_keys]["id"]
                            COORD_final = dic_Id[j_keys]["COORDS"]
                            COG_final = j_keys
                            # PV_final = dic_Id[j_keys]["pv"]

                        elif dic_Id[j_keys]["QF"] < bestQF_2:
                            bestQF_2 = dic_Id[j_keys]["QF"]
                            bestId_2 = dic_Id[j_keys]["id"]
                            COORD_final_2 = dic_Id[j_keys]["COORDS"]
                            COG_final_2 = j_keys
                            # PV_final_2 = dic_Id[j_keys]["pv"]
                    except KeyError:
                        pass  # it could be that dic_Id does not have the corresponding key (QF) because it is not valid
                if bestId != "-1":  # we only define those variables if they are representatives
                    dic_labels_count[bestId] += 1

                    dic_cluster[i]["id"] = bestId
                    dic_cluster[i]["QF"] = bestQF
                    dic_cluster[i]["COORDS"] = COORD_final
                    dic_cluster[i]["COG"] = COG_final
                    # dic_cluster[i]["pv"] = PV_final
                    COG, dic_Events_Counts = self.__Repetition_of_Labels(bestId, dic_Id, dic_Events_Counts)
                    dic_cluster[i]["COG_ALL"] = COG
                    # print("QF")
                    if bestId_2 != "-1":
                        dic_cluster[i]["id_2"] = bestId_2
                        dic_cluster[i]["QF_2"] = bestQF_2
                        dic_cluster[i]["COORDS_2"] = COORD_final_2
                        dic_cluster[i]["COG_2"] = COG_final_2
                        # dic_cluster[i]["pv_2"] = PV_final_2
                        dic_cluster[i]["COG"] = COG_final + '_QF'
                    else:
                        dic_cluster[i]["COG"] = COG_final + '_ONLY_VALID'
            if dic_cluster[i]['id'] != -1.:
                for i_roi in dic_cluster[i]['COORDS'].keys():
                    dic_cluster[i]['ROI'].append(i_roi)
                    dic_cluster[i]['Order_Coord'].append(dic_cluster[i]['COORDS'][i_roi][0])

                if dic_cluster[i]['COORDS_2'] != -1:
                    for i_roi_2 in dic_cluster[i]['COORDS_2'].keys():
                        dic_cluster[i]['ROI_2'].append(i_roi_2)
                        dic_cluster[i]['Order_Coord_2'].append(dic_cluster[i]['COORDS_2'][i_roi_2][0])
                else:
                    dic_cluster[i]['ROI_2'].append(-1.)
                    dic_cluster[i]['Order_Coord_2'].append([-1., -1.])

                dic_cluster[i]['ROI'] = str(dic_cluster[i]['ROI'])
                dic_cluster[i]['Order_Coord'] = str(dic_cluster[i]['Order_Coord'])
                dic_cluster[i]['ROI_2'] = str(dic_cluster[i]['ROI_2'])
                dic_cluster[i]['Order_Coord_2'] = str(dic_cluster[i]['Order_Coord_2'])

                data_cluster_calib_pv['id'] = dic_cluster[i]["id"]

                if dic_cluster[i]['COG'].endswith('_ONLY_VALID') or dic_cluster[i]['COG'].endswith('_QF'):
                    data_cluster_calib_pv['selected_pv'] = dic_Id[dic_cluster[i]["COG"].split('_')[0]]['pv']
                    data_cluster_calib_pv['COG'] = dic_cluster[i]["COG"].split('_')[0]  # HVD_PV
                else:
                    data_cluster_calib_pv['selected_pv'] = dic_Id[dic_cluster[i]["COG"]]['pv']
                    data_cluster_calib_pv['COG'] = dic_cluster[i]["COG"]  # HVD_PV

                #in first layer, not include the photon count in all calib_factor, but only in the selected one
                #it does not change much the final results, improves Er by 0.2% difference
                if data_cluster_pv_000[dic_cluster[i]["id"]]['layer'] == 1:
                    if data_cluster_calib_pv['COG'] == "000":  # cgt[0] == 1 and # if len(dic_Id["000"].keys()) > 3: #only the valid ones from hitAnalysis
                        data_cluster_pv_000[dic_cluster[i]["id"]]['pv'].append(dic_Id["000"]['pv'])

                    if data_cluster_calib_pv['COG'] == "100":  # cgt[1] == 1 and # if len(dic_Id["100"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_100[dic_cluster[i]["id"]]['pv'].append(dic_Id["100"]['pv'])

                    if data_cluster_calib_pv['COG'] == "010":  # cgt[2] == 1 and  # if len(dic_Id["010"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_010[dic_cluster[i]["id"]]['pv'].append(dic_Id["010"]['pv'])

                    if data_cluster_calib_pv['COG'] == "111":  # cgt[3] == 1 and  is already in our condition # if len(dic_Id["111"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_111[dic_cluster[i]["id"]]['pv'].append(dic_Id["111"]['pv'])
                else:

                    if 'id' in dic_Id["000"].keys(): # cgt[0] == 1 and # if len(dic_Id["000"].keys()) > 3: #only the valid ones from hitAnalysis
                        data_cluster_pv_000[dic_cluster[i]["id"]]['pv'].append(dic_Id["000"]['pv'])

                    if 'id' in dic_Id["100"].keys(): # cgt[1] == 1 and # if len(dic_Id["100"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_100[dic_cluster[i]["id"]]['pv'].append(dic_Id["100"]['pv'])

                    if 'id' in dic_Id["010"].keys(): # cgt[2] == 1 and  # if len(dic_Id["010"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_010[dic_cluster[i]["id"]]['pv'].append(dic_Id["010"]['pv'])

                    if 'id' in dic_Id["111"].keys(): # cgt[3] == 1 and  is already in our condition # if len(dic_Id["111"].keys()) > 3:  # only the valid ones
                        data_cluster_pv_111[dic_cluster[i]["id"]]['pv'].append(dic_Id["111"]['pv'])

                data_cluster_calib_pv_all[i] = data_cluster_calib_pv

                for j in self.dic_Events.keys():
                    if self.dic_Events[j] == dic_cluster[i]["COG_ALL"]:
                        if dic_cluster[i]['COG'].endswith('_ONLY_VALID') or dic_cluster[i]['COG'].endswith('_QF'):
                            self.dic_AssignE[dic_cluster[i]['COG']][dic_cluster[i]["id"]]['n_events'] += 1
                        else:
                            self.dic_AssignE[j][dic_cluster[i]["id"]]['n_events'] += 1
            else:
                # dic_notSelected_cluster[i] = {}
                # dic_notSelected_cluster[i]["COORDS"] = -1
                # dic_notSelected_cluster[i]['Cluster'] = i
                # dic_notSelected_cluster[i]["COORDS"] = str([dic_Id["111"]["COORDS"]])
                # dic_notSelected_cluster[i]["Flag"] = str([dic_Id["111"]["Flag"]])
                # dic_notSelected_cluster[i]["LUT_000"] = str([dic_Id["111"]["LUT_000"]])
                # dic_notSelected_cluster[i]["LUT_100"] = str([dic_Id["111"]["LUT_100"]])
                # dic_notSelected_cluster[i]["LUT_010"] = str([dic_Id["111"]["LUT_010"]])
                # dic_notSelected_cluster[i]["LUT_111"] = str([dic_Id["111"]["LUT_111"]])
                dic_Events_Counts['None'] += 1
                dic_cluster.pop(i)

            i += 1
        return dic_Events_Counts, dic_labels_count, dic_cluster, dic_notSelected_cluster, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111, data_cluster_calib_pv_all

    def __save_Events_Counts(self, dic_Events_Counts):
        with open('{}dic-Events{}-Counts.pickle'.format(self.pathtodirectorySave, self.final_event), 'wb') as handle:
            pickle.dump(dic_Events_Counts, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Assign_Events(self):
        with open('{}dic_AssignE{}.pickle'.format(self.pathtodirectorySave, self.final_event), 'wb') as handle:
            pickle.dump(self.dic_AssignE, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_calib_PV(self, data_cluster_calib_pv_all):
        with open('{}dic_calibPV{}.pickle'.format(self.pathtodirectorySave, self.final_event), 'wb') as handle:
            pickle.dump(data_cluster_calib_pv_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __PV_in_HVD(self, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111):

        data_cluster_pv_list = [data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111]

        for cg in range(4):
            HVD = self.HVD_list[cg]
            #data_cluster_pv_HVD = data_cluster_pv_list[cg]
            with open('{}datapv-{}-valid{}.pickle'.format(self.pathtodirectorySave + self.pathtodirectorySavePV, HVD, self.final_event),
                      'wb') as handle:
                pickle.dump(data_cluster_pv_list[cg], handle,
                            protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Dic_notSelected_Cluster(self, dic_notSelected_cluster):
        # with open(self.fout_dic_notSelectedCluster, 'a') as fout:
            # print(peakInfoSave_all[peak])
        df_dic_notSelectedCluster = pd.DataFrame.from_dict(dic_notSelected_cluster,
                            columns=['COORDS', 'LUT_000', 'LUT_100', 'LUT_010', 'LUT_111', 'Flag'],
                            orient='index')  # create a dataframe with the data of the current file
        df_dic_notSelectedCluster.to_hdf(self.fout_dic_notSelectedCluster, key='dic_Cluster', mode='a', format='table', append=True,
                              data_columns=['COORDS', 'LUT_000', 'LUT_100', 'LUT_010', 'LUT_111', 'Flag', ],
                              min_itemsize={'COORDS': 100, 'index': 10, 'Flag': 10, 'LUT_000':100, 'LUT_100':100, 'LUT_010':100, 'LUT_111':100})  # we write the dataframe with the index

            # fout.write(df.to_csv(header=False,
            #                      index=False, sep='|'))  # we write the dataframe with the index
            # fout.write('\n')  # a newline to place correctly the next rows

    def __save_Dic_Cluster(self, dic_cluster):
        # df_dic_Cluster = pd.DataFrame(dic_cluster[i],
        #                   columns=['id', 'Order_Coord', 'ROI', 'QF', 'id_2', 'Order_Coord_2', 'ROI_2', 'QF_2'],
        #                   index=['{}'.format(dic_cluster[i]['Cluster'])])  # create a dataframe with the data of the current file
        df_dic_Cluster = pd.DataFrame.from_dict(dic_cluster,
                                    columns=['id', 'Order_Coord', 'ROI', 'QF', 'id_2', 'Order_Coord_2', 'ROI_2', 'QF_2', "Cluster"],
                                    orient='index')  # create a dataframe with the data of the current file
        # print("Der PATH!!!", self.fout_dic_Cluster)
        df_dic_Cluster.to_hdf(self.fout_dic_Cluster, key='dic_Cluster', mode='a', format='table', append=True,
                  data_columns=['id', 'Order_Coord', 'ROI', 'QF', 'id_2', 'Order_Coord_2', 'ROI_2', 'QF_2', "Cluster"], min_itemsize={'Order_Coord':100, 'Order_Coord_2':100, 'ROI':10, 'ROI_2':10, 'index':10})  # we write the dataframe with the index
        #
        # print("Der ZWEITE PATH!!!", '{}dic-{}cluster2.pickle'.format(self.pathtodirectorySave, self.final_event))
        with open('{}dic-{}cluster2.pickle'.format(self.pathtodirectorySave, self.final_event), 'wb') as handle:
            pickle.dump(dic_cluster, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def runCluster(self):

        atexit.register(self.__endlog)
        self.__log(self.line, "Start Program")

        cog000test, pv000test, self.lud000, pv000ref, cog000ref = self.__read_data_COG("000")
        cog100test, pv100test, self.lud100, pv100ref, cog100ref = self.__read_data_COG("100")
        cog010test, pv010test, self.lud010, pv010ref, cog010ref = self.__read_data_COG("010")
        cog111test, pv111test, self.lud111, pv111ref, cog111ref = self.__read_data_COG("111")

        print("HERE IT IS COG000test", cog000test)
        print("HERE IT IS pv000test", pv000test)
        print("HERE IT IS self.lud000", len(self.lud000))
        print("HERE IT IS pv000ref", pv000ref)
        print("HERE IT IS COG000ref", cog000ref)




        # try:
        #     with open('/home/david.perez/Desktop/cogTest4.pickle', 'rb') as handle:
        #         cogtest = pickle.load(handle)  # 000, 100, 010, 111
        # except:
        #     self.__log("Events are not split into ref and test.")
        #     cogtest = -1

        # print("DER ABSOLUT NEUE PATH:", "{}cogRef{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, self.stack_type))
        with h5py.File("{}cogRef{}.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadHDF5, self.stack_type), "r") as f:
            dset = f["data"]
            cogref = dset[self.init_event:self.final_event]  # 000, 100, 010, 111
        # with open('/home/david.perez/Desktop/cogRef.pickle', 'rb') as handle:
        #     cogref = pickle.load(handle) # 000, 100, 010, 111

        self.__log("Check Program")

        #    for i_event in range(0,5): #when we want to split it (not so much use of the RAM)
        dic_Events_Counts = {}

        for j in self.dic_Events.keys():
            # print("KEYS!!! of self.dic_Events: ", j)
            dic_Events_Counts[j] = 0

        dic_cluster = {}
        dic_notSelected_cluster = {}
        dic_labels_count = {}

        for i in range(3425):
            dic_labels_count[i] = 0

        print("Start")
        # dic_Events_Counts, dic_labels_count, dic_cluster = self.__Counter(dic_cluster, dic_Events_Counts, cogtest, dic_labels_count, cog000test, cog100test, cog010test, cog111test)

        dic_Events_Counts, dic_labels_count, dic_cluster, dic_notSelected_cluster, data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111, data_cluster_calib_pv_all = self.__Counter(dic_cluster, dic_notSelected_cluster, dic_Events_Counts, cogref, dic_labels_count, cog000ref, cog100ref, cog010ref, cog111ref, pv000ref, pv100ref, pv010ref, pv111ref)

        self.__log("Counter is over.")

        try:
            self.__PV_in_HVD(data_cluster_pv_000, data_cluster_pv_100, data_cluster_pv_010, data_cluster_pv_111)
            self.__log("PV is saved.")
        except:
            print("Problem saving PV.")

        try:
            self.__save_Events_Counts(dic_Events_Counts)
            self.__log("dic_Events_Counts is saved.")
        except:
            print("Problem saving dic_Events_Counts.")

        try:
            self.__save_Assign_Events()
            self.__log("AssignE is saved.")
        except:
            print("Problem saving AssignE.")

        try:
            self.__save_calib_PV(data_cluster_calib_pv_all)
            self.__log("CalibPV is saved.")
        except:
            print("Problem saving CalibPV.")

        # try:
        #     self.__save_Dic_Cluster(dic_cluster)
        #     self.__log("DicCluster is saved.")
        # except:
        #     print("Problem saving DicCluster.")
        self.__save_Dic_Cluster(dic_cluster)
        # try:
        #     self.__save_Dic_notSelected_Cluster(dic_notSelected_cluster)
        #     self.__log("DicnotSelectedCluster is saved.")
        # except:
        #     print("Problem saving DicnotSelectedCluster.")
        self.__save_Dic_notSelected_Cluster(dic_notSelected_cluster)

        self.__log("SAVED")

        self.__log("End Program")