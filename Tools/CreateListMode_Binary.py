import pandas as pd
import numpy as np
import cPickle as pickle
import h5py
import argparse
from textwrap import dedent
import sys
import itertools
import re
import os
import pyximport
pyximport.install()
import matplotlib.pyplot as plt
from cython_posTile import Positioning as pos
from PSFTools import PSFTools
psf = PSFTools()
pos = pos()

class ListModeC():
    def __init__(self, pathtodirectoryRead, stack_idA, stack_idB, module_idA, module_idB, loglikeA, loglikeB):
        self.pathtodirectoryRead = pathtodirectoryRead

        self.stack_idA = stack_idA
        self.stack_idB = stack_idB
        self.module_idA = module_idA
        self.module_idB = module_idB
        self.loglikeA = loglikeA
        self.loglikeB = loglikeB

        self.pathtodirectorySave = self.pathtodirectoryRead

        self.pathtodirectoryReadCal = 'Stack{}_cal/'.format(self.stack_idA)
        self.pathtodirectoryReadCoinc = 'Stack{}_coinc/'.format(self.stack_idB)

        self.pathtodirectoryReadListMode = 'Parallel/'
        self.pathtodirectoryReadhdf5Data = 'hdf5Data/'

        # self.pathtodirectoryReadCoinc = 'stack'
        self.dt = np.dtype([
            ('crystal_idA', np.uint16),
            ('crystal_idB', np.uint16),
            ('stack_idA', np.uint16),
            ('stack_idB', np.uint16),
            ('module_idA', np.uint16),
            ('module_idB', np.uint16),
            ('energyA', np.float32),
            ('energyB', np.float32),
            ('loglikeA', np.float32),
            ('loglikeB', np.float32),
            ('timeDiff', np.float32),
            ('timeStampA', np.ulonglong)
        ])


    def checkFolder(self, pathDirectory):
        CHECK_FOLDER = os.path.isdir(pathDirectory)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(pathDirectory)
            print("created folder : ", pathDirectory)

    def run_CreateListMode(self):
        print('importing...')
        with h5py.File("{}timeStamps_coinc.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadCoinc + self.pathtodirectoryReadhdf5Data), "r") as f:
            dset = f["data"]
            coinc_timestamps = dset[:]
        with h5py.File("{}timeStamps_cal.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadCal + self.pathtodirectoryReadhdf5Data), "r") as f:
            dset = f["data"]
            cal_timestamps = dset[:]

        with h5py.File("{}photons_coinc.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadCoinc + self.pathtodirectoryReadhdf5Data), "r") as f:
            dset = f["data"]
            coinc_photons = dset[:]
        with h5py.File("{}photons_cal.hdf5".format(self.pathtodirectoryRead + self.pathtodirectoryReadCal + self.pathtodirectoryReadhdf5Data), "r") as f:
            dset = f["data"]
            cal_photons = dset[:]
        print('imported...')

        def select_events(array, indices):
            return np.concatenate(array[indices])

        cal_mainDieS = np.asanyarray([pos.posIndexPixeltoDie(x) for x in np.argmax(cal_photons, axis=1)])
        coinc_mainDieS = np.asanyarray([pos.posIndexPixeltoDie(x) for x in np.argmax(coinc_photons, axis=1)])

        cal_timestamps_mainDie = cal_timestamps[np.arange(len(cal_timestamps)), cal_mainDieS.astype('int')]
        coinc_timestamps_mainDie = coinc_timestamps[np.arange(len(coinc_timestamps)), coinc_mainDieS.astype('int')]

        with open('{}dic_listmode_total.pickle'.format(self.pathtodirectoryRead + self.pathtodirectoryReadCal + self.pathtodirectoryReadListMode),
                  'r') as inp:
            dic_listmode_cal = pickle.load(inp)

        with open('{}dic_listmode_total.pickle'.format(self.pathtodirectoryRead + self.pathtodirectoryReadCoinc + self.pathtodirectoryReadListMode),
                  'r') as inp:
            dic_listmode_coinc = pickle.load(inp)

        events_cal = dic_listmode_cal.keys()
        events_coinc = dic_listmode_coinc.keys()
        events = np.intersect1d(events_cal, events_coinc)

        cal_timestamps_selected = cal_timestamps_mainDie[events]
        coinc_timestamps_selected = coinc_timestamps_mainDie[events]

        diff = coinc_timestamps_selected - cal_timestamps_selected

        crystal_idA = np.ones(len(events))*(-1)
        crystal_idB = np.ones(len(events))*(-1)

        energyA = np.ones(len(events))*(-1)
        energyB = np.ones(len(events))*(-1)
        for i, cluster in enumerate(events):

            crystal_idA[i] = dic_listmode_cal[cluster]['crystal_id']
            crystal_idB[i] = dic_listmode_coinc[cluster]['crystal_id']

            energyA[i] = dic_listmode_cal[cluster]['keV']
            energyB[i] = dic_listmode_coinc[cluster]['keV']

        listmode_arr = np.zeros((len(diff),12))

        listmode_arr[:, 0] = crystal_idA
        listmode_arr[:, 1] = crystal_idB

        listmode_arr[:, 2] = self.stack_idA
        listmode_arr[:, 3] = self.stack_idB
        listmode_arr[:, 4] = self.module_idA
        listmode_arr[:, 5] = self.module_idB

        listmode_arr[:, 6] = energyA
        listmode_arr[:, 7] = energyB

        listmode_arr[:, 8] = self.loglikeA
        listmode_arr[:, 9] = self.loglikeB
        listmode_arr[:,10] = diff
        listmode_arr[:, 11] = cal_timestamps_selected

        listmode = np.array(list(map(tuple, listmode_arr)), dtype=self.dt)

        # with open('measurement_coincs_hitAnalysis.extlistmode','rb') as data:
#    #  first = np.fromfile(g,dtype=np.uint16,count = 6)
#   #   second = np.fromfile(g,dtype=np.float32,count = 5)
#  #    first1 = np.fromfile(g,dtype=np.uint16,count = 2)
#  #
#     third = np.fromfile(g,dtype=np.ulonglong,count = 1)
#             data = g.read()
#             third = np.fromfile(data,dtype=dt,count = 1)


# df = pd.DataFrame(third)

        with open('{}measurement_coinc_new.extlistmode'.format(self.pathtodirectoryRead), 'wb') as f:
             listmode.tofile(f)



