# read calibTXT, extract mean and calculate calib_factor
# four dic with 000,010,100,111 and id_crystal and calib factor (= 511. / tmpPeak['mean']) {'111': {33:0.14386492736,69:0.1590328470}}
#loop over dic_calibPV and new array with calib values
import pandas as pd

import numpy as np
import cPickle as pickle
import h5py
import argparse
from textwrap import dedent
import sys
import itertools
import re

class CalibPV():
    def __init__(self, final_event, pathtodirectoryRead):
        # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
        #self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/Parallel/'
        # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'
        self.pathtodirectoryRead = pathtodirectoryRead

        # pathtodirectoryRead = "C:\\Users\\David\\Downloads\\"

        # pathtoPV = '20210304_NEW-2021-02-17_PhotonSpectrum/'
        # '20210303_NEW-2021-02-17_PhotonSpectrum/'
        # pathtoPV = '20210315_NEW_PhotonSpectrum/'

        self.pathtoHDF5 = 'hdf5Data/'
        self.pathtoDIC_Checked = 'dic-checked/'

        self.pathtodirectorySaveParallel = 'Parallel/'
        self.pathtoPV = 'PhotonSpectrum/'

        self.pathtodirectorySave = self.pathtodirectoryRead + self.pathtodirectorySaveParallel

        # self.pathtoHDF5 = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/20210315_NEW_hdf5Data/'
        # self.pathtoDIC_Checked = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/20210315_NEW_dic-checked/'

        self.HVD_list = ['000', '100', '010', '111']

        self.final_event = final_event

    def CrystalDict(self):
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
                            'id': r
                        }
                        dic_crystal[r] = peakii
                    else:
                        if n % 2 != 0:
                            peakii = {
                                'row': j,
                                'layer': 1,
                                'id': r
                            }
                            dic_crystal[r] = peakii
                        else:
                            peakjj = {
                                'row': j,
                                'layer': 2,
                                'id': r
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
                        'id': r
                    }
                    dic_crystal[r] = peakkk
                row = []
                j += 1
                m += 1
            else:
                pass
            row.append(i)

        return dic_crystal

    def normalizeAndSplit(self, l):
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
    def dic_calFactor_HVD(self, pathtodirectoryRead, HVD, dic_HVD):
        with open('{}CalibPVLog{}.txt'.format(pathtodirectoryRead, HVD), 'r') as finput:
            lines = finput.readlines()
            E_r_2 = 100.
            for line in lines:
                el = self.normalizeAndSplit(line)
                id_crystal = int(el[0])
                mean = el[13]
                cal_factor = 511. / float(mean)
                E_r = float(el[-1])
                valid_P = int(el[1])
                if valid_P:
                    #if E_r <= 20.:
                    if id_crystal in dic_HVD.keys():
                        if E_r < E_r_2:
                            dic_HVD[id_crystal] = {'cal_factor':cal_factor, 'E_r':E_r }
                    else:
                        dic_HVD[id_crystal] = {'cal_factor':cal_factor, 'E_r':E_r}
                    E_r_2 = E_r
        return dic_HVD

    def __save_calib_FinalPV(self, pathtodirectorySave, hist_array, part):
        with open('{}array_calibFinalPV_{}_{}.pickle'.format(pathtodirectorySave, part, self.final_event), 'wb') as handle:
            pickle.dump(hist_array, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_used_crystalPV(self, pathtodirectorySave, list_used_crystal, part):
        # with open('{}array_usedCrystalPV_{}.pickle'.format(pathtodirectorySave, part), 'wb') as handle:
        #     pickle.dump(list_used_crystal, handle,
        #                 protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

        with open('{}array_usedCrystalPV_{}_{}.txt'.format(pathtodirectorySave, part, self.final_event), 'w+') as fout:
            for label in list_used_crystal:
                fout.write(str(label))  # we write the dataframe with the index
                fout.write('\n')  # a newline to place correctly the next rows


    def hist_arr(self, event, hist_array, HVD, dic_cFa, dic_calibPVa, dic_cFa_used, dic_crystala, hist_array_layer1,
                 hist_array_layer2, hist_array_layer3, pv000ref_e, pv100ref_e, pv010ref_e, pv111ref_e, list_orig_clas, valid_HVD):
        #dic_calFactor_HVD = dic_cFa[HVD]
        calib_value = None
        #E_r = 100.
        if dic_calibPVa[event]['id']:
            if dic_calibPVa[event]['id'] in dic_cFa[HVD].keys():
                #if dic_calFactor_HVD[dic_calibPVa[event]['id']]['E_r'] < E_r:
                calib_value = (dic_calibPVa[event]['selected_pv']) * (dic_cFa[HVD][dic_calibPVa[event]['id']]['cal_factor'])
                HVD_final = HVD
                E_r = dic_cFa[HVD][dic_calibPVa[event]['id']]['E_r']
                list_orig_clas[0] += 1

            elif valid_HVD[3] and dic_calibPVa[event]['id'] in dic_cFa['111'].keys():
                calib_value = (pv111ref_e) * (dic_cFa['111'][dic_calibPVa[event]['id']]['cal_factor'])
                #hist_array.append(calib_value)
                #dic_cF_used['111'][dic_calibPVa[event]['id']] = 1
                HVD_final = '111'
                E_r = dic_cFa['111'][dic_calibPVa[event]['id']]['E_r']
                list_orig_clas[1] += 1

            elif valid_HVD[2] and dic_calibPVa[event]['id'] in dic_cFa['010'].keys():
                calib_value = (pv010ref_e) * (dic_cFa['010'][dic_calibPVa[event]['id']]['cal_factor'])

                HVD_final = '010'
                E_r = dic_cFa['010'][dic_calibPVa[event]['id']]['E_r']
                list_orig_clas[2] += 1

            elif valid_HVD[1] and dic_calibPVa[event]['id'] in dic_cFa['100'].keys():
                calib_value = (pv100ref_e) * (dic_cFa['100'][dic_calibPVa[event]['id']]['cal_factor'])

                HVD_final = '100'
                E_r = dic_cFa['100'][dic_calibPVa[event]['id']]['E_r']
                list_orig_clas[3] += 1

            elif valid_HVD[0] and dic_calibPVa[event]['id'] in dic_cFa['000'].keys():
                calib_value = (pv000ref_e) * (dic_cFa['000'][dic_calibPVa[event]['id']]['cal_factor'])

                HVD_final = '000'
                E_r = dic_cFa['000'][dic_calibPVa[event]['id']]['E_r']
                list_orig_clas[4] += 1
            else:
                list_orig_clas[5] += 1
                if dic_calibPVa[event]['id'] in dic_cFa['111'].keys():
                    calib_value = (pv111ref_e) * (dic_cFa['111'][dic_calibPVa[event]['id']]['cal_factor'])
                    HVD_final = '111'
                    list_orig_clas[6] += 1
                elif dic_calibPVa[event]['id'] in dic_cFa['010'].keys():
                    calib_value = (pv010ref_e) * (dic_cFa['010'][dic_calibPVa[event]['id']]['cal_factor'])
                    HVD_final = '010'
                    list_orig_clas[6] += 1
                elif dic_calibPVa[event]['id'] in dic_cFa['100'].keys():
                    calib_value = (pv100ref_e) * (dic_cFa['100'][dic_calibPVa[event]['id']]['cal_factor'])
                    HVD_final = '100'
                    list_orig_clas[6] += 1
                elif dic_calibPVa[event]['id'] in dic_cFa['000'].keys():
                    calib_value = (pv000ref_e) * (dic_cFa['000'][dic_calibPVa[event]['id']]['cal_factor'])
                    HVD_final = '000'
                    list_orig_clas[6] += 1
        if calib_value:
            hist_array.append(calib_value)
            dic_cFa_used[HVD_final][dic_calibPVa[event]['id']] = 1

            if dic_crystala[dic_calibPVa[event]['id']]['layer'] == 1:
                hist_array_layer1.append(calib_value)
            elif dic_crystala[dic_calibPVa[event]['id']]['layer'] == 2:
                hist_array_layer2.append(calib_value)
            elif dic_crystala[dic_calibPVa[event]['id']]['layer'] == 3:
                hist_array_layer3.append(calib_value)
        return hist_array, dic_cFa_used, hist_array_layer1, hist_array_layer2, hist_array_layer3, list_orig_clas

    def load_pv(self, pathtodirectoryRead, pathtodirectoryReadHDF5, HVD):
        with h5py.File("{}pv{}ref.hdf5".format(pathtodirectoryReadHDF5, HVD), "r") as f: #pathtodirectoryRead +
            dset = f["data"]
            pvHVDref = dset[:]  # 000, 100, 010, 111
        return pvHVDref

    def load_dic_checked(self):
        with open('{}dic-crystal-{}-checked.pickle'.format(self.pathtodirectoryRead + self.pathtoDIC_Checked, '000'), 'rb') as handle:
            dic_checked_000 = pickle.load(handle)
        with open('{}dic-crystal-{}-checked.pickle'.format(self.pathtodirectoryRead + self.pathtoDIC_Checked, '100'), 'rb') as handle:
            dic_checked_100 = pickle.load(handle)
        try:
            with open('{}dic-crystal-{}-checked.pickle'.format(self.pathtodirectoryRead + self.pathtoDIC_Checked, '010'), 'rb') as handle:
                dic_checked_010 = pickle.load(handle)
        except:
            dic_checked_010 = False
        with open('{}dic-crystal-{}-checked.pickle'.format(self.pathtodirectoryRead + self.pathtoDIC_Checked, '111'), 'rb') as handle:
            dic_checked_111 = pickle.load(handle)
        return dic_checked_000, dic_checked_100, dic_checked_010, dic_checked_111

    def RunCalibPV(self):
        dic_calFactor_000 = {}
        dic_calFactor_100 = {}
        dic_calFactor_010 = {}
        dic_calFactor_111 = {}

        dic_calFactor_000 = self.dic_calFactor_HVD(self.pathtodirectoryRead + self.pathtodirectorySaveParallel + self.pathtoPV, '000', dic_calFactor_000)
        dic_calFactor_100 = self.dic_calFactor_HVD(self.pathtodirectoryRead + self.pathtodirectorySaveParallel + self.pathtoPV, '100', dic_calFactor_100)
        dic_calFactor_010 = self.dic_calFactor_HVD(self.pathtodirectoryRead + self.pathtodirectorySaveParallel + self.pathtoPV, '010', dic_calFactor_010)
        dic_calFactor_111 = self.dic_calFactor_HVD(self.pathtodirectoryRead + self.pathtodirectorySaveParallel + self.pathtoPV, '111', dic_calFactor_111)

        pv000ref = self.load_pv(self.pathtodirectoryRead + self.pathtodirectorySaveParallel, self.pathtodirectoryRead + self.pathtoHDF5, '000')
        pv100ref = self.load_pv(self.pathtodirectoryRead + self.pathtodirectorySaveParallel, self.pathtodirectoryRead + self.pathtoHDF5, '100')
        pv010ref = self.load_pv(self.pathtodirectoryRead + self.pathtodirectorySaveParallel, self.pathtodirectoryRead + self.pathtoHDF5, '010')
        pv111ref = self.load_pv(self.pathtodirectoryRead + self.pathtodirectorySaveParallel, self.pathtodirectoryRead + self.pathtoHDF5, '111')

        #add tileID
        print("importing...")
        with open('{}dic_calibPV{}.pickle'.format(self.pathtodirectoryRead + self.pathtodirectorySaveParallel, self.final_event), 'r') as dicinput:
            dic_calibPV = pickle.load(dicinput)
        print("imported.")
        dic_used_crystals_000 = {}
        dic_used_crystals_100 = {}
        dic_used_crystals_010 = {}
        dic_used_crystals_111 = {}

        hist_array = []
        hist_array_layer1 = []
        hist_array_layer2 = []
        hist_array_layer3 = []
        dic_crystal = self.CrystalDict()

        dic_checked_000, dic_checked_100, dic_checked_010, dic_checked_111 = self.load_dic_checked()

        dic_cF = {'000': dic_calFactor_000, '100': dic_calFactor_100, '010': dic_calFactor_010, '111': dic_calFactor_111}
        dic_cF_used = {'000': dic_used_crystals_000, '100': dic_used_crystals_100, '010': dic_used_crystals_010, '111': dic_used_crystals_111}
        list_orig_clas = [0,0,0,0,0,0,0]
        for event in dic_calibPV.keys():
            pv000ref_e = pv000ref[event]
            pv100ref_e = pv100ref[event]
            pv010ref_e = pv010ref[event]
            pv111ref_e = pv111ref[event]
            valid_000 = dic_checked_000[dic_calibPV[event]['id']]['valid']
            valid_100 = dic_checked_100[dic_calibPV[event]['id']]['valid']
            if not dic_checked_010:
                valid_010 = False
            else:
                valid_010 = dic_checked_010[dic_calibPV[event]['id']]['valid']
            valid_111 = dic_checked_111[dic_calibPV[event]['id']]['valid']
            valid_HVD = [valid_000, valid_100, valid_010, valid_111]
            hist_array, dic_cF_used, hist_array_layer1, hist_array_layer2, hist_array_layer3, list_orig_clas = self.hist_arr(event, hist_array, dic_calibPV[event]['COG'], dic_cF, dic_calibPV, dic_cF_used, dic_crystal, hist_array_layer1, hist_array_layer2, hist_array_layer3, pv000ref_e, pv100ref_e, pv010ref_e, pv111ref_e, list_orig_clas, valid_HVD)

        with open('{}ListUsedHVD{}.txt'.format(self.pathtodirectorySave, self.final_event), 'a') as fout:
            fout.write(str(list_orig_clas))  # we write the dataframe with the index
            fout.write('\n')  # a newline to place correctly the next rows
        print("Done with Events.")

        list_used_crystals_000 = []
        for key in dic_cF_used['000'].keys():
            list_used_crystals_000.append(key)

        list_used_crystals_100 = []
        for key in dic_cF_used['100'].keys():
            list_used_crystals_100.append(key)

        list_used_crystals_010 = []
        for key in dic_cF_used['010'].keys():
            list_used_crystals_010.append(key)

        list_used_crystals_111 = []
        for key in dic_cF_used['111'].keys():
            list_used_crystals_111.append(key)

        self.__save_calib_FinalPV(self.pathtodirectorySave, hist_array_layer1, 'Layer1')
        self.__save_calib_FinalPV(self.pathtodirectorySave, hist_array_layer2, 'Layer2')
        self.__save_calib_FinalPV(self.pathtodirectorySave, hist_array_layer3, 'Layer3')
        self.__save_calib_FinalPV(self.pathtodirectorySave, hist_array, 'Total')

        self.__save_used_crystalPV(self.pathtodirectorySave, list_used_crystals_000, '000')
        self.__save_used_crystalPV(self.pathtodirectorySave, list_used_crystals_100, '100')
        self.__save_used_crystalPV(self.pathtodirectorySave, list_used_crystals_010, '010')
        self.__save_used_crystalPV(self.pathtodirectorySave, list_used_crystals_111, '111')


        print("Array is saved.")

