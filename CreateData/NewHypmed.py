# -*- coding: utf-8 -*-
__author__ = "david.perez.gonzalez" 

import numpy as np
import matplotlib.pyplot as plt
#from configparser import ConfigParser
#from config import config
import logging
import ROOT as r
import os
import time
import h5py
import cPickle as pickle

class Hypmed():
    """
    Working frame regarding the crystal identification algorithms
    """
    def __init__(self, pathtodirectoryRead, savepath):
        self.pathtodirectoryRead = pathtodirectoryRead

        self.savepath = savepath

        self.pathtodirectorySaveRefSections = self.savepath + 'RefSections/'
        self.pathtodirectorySavehist = self.savepath + 'hist/'

        self.pathtodirectoryReadHDF5 = self.pathtodirectoryRead + 'hdf5Data/'
        self.pathtodirectorySaveHDF5 = self.pathtodirectoryReadHDF5

        CHECK_FOLDER = os.path.isdir(self.pathtodirectorySaveRefSections)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(self.pathtodirectorySaveRefSections)
            print("created folder : ", self.pathtodirectorySaveRefSections)

        CHECK_FOLDER = os.path.isdir(self.pathtodirectorySavehist)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(self.pathtodirectorySavehist)
            print("created folder : ", self.pathtodirectorySavehist)

    def loadTOTALData_Pickles(self):
        self.dicval_000 = {}
        self.dicval_100 = {}
        self.dicval_010 = {}
        self.dicval_111 = {}

        self.dicpos_000 = {}  # x and y from COG HVD
        self.dicpos_100 = {}
        self.dicpos_010 = {}
        self.dicpos_111 = {}

        self.dicpv_000 = {}  # photon values from COG HVD
        self.dicpv_100 = {}
        self.dicpv_010 = {}
        self.dicpv_111 = {}

        self.list_save_dic = {"dicval_000":self.dicval_000, "dicval_100":self.dicval_100, "dicval_010":self.dicval_010,
                              "dicval_111":self.dicval_111, "dicpos_000":self.dicpos_000, "dicpos_100":self.dicpos_100,
                              "dicpos_010":self.dicpos_010, "dicpos_111":self.dicpos_111, "dicpv_000":self.dicpv_000,
                              "dicpv_100":self.dicpv_100, "dicpv_010":self.dicpv_010, "dicpv_111":self.dicpv_111}
        for name in self.list_save_dic.keys():

            with open('{}/{}.pickle'.format(self.pathtodirectoryRead + 'PickleData', name), "rb") as fin:
                dic_hvd = pickle.load(fin)
            self.list_save_dic[name] = dic_hvd
        self.cogRef = []

        self.cog000Ref = []
        self.cog100Ref = []
        self.cog010Ref = []
        self.cog111Ref = []

        self.pv000Ref = []
        self.pv100Ref = []
        self.pv010Ref = []
        self.pv111Ref = []

        for cluster in self.list_save_dic["dicpv_000"].keys():
            self.cogRef.append([int(self.list_save_dic["dicval_000"][cluster]), int(self.list_save_dic["dicval_100"][cluster]),
                           int(self.list_save_dic["dicval_010"][cluster]), int(self.list_save_dic["dicval_111"][cluster])])

            self.pv000Ref.append(float(self.list_save_dic["dicpv_000"][cluster]))
            self.pv100Ref.append(float(self.list_save_dic["dicpv_100"][cluster]))
            self.pv010Ref.append(float(self.list_save_dic["dicpv_010"][cluster]))
            self.pv111Ref.append(float(self.list_save_dic["dicpv_111"][cluster]))

            self.cog000Ref.append(self.list_save_dic["dicpos_000"][cluster])
            self.cog100Ref.append(self.list_save_dic["dicpos_100"][cluster])
            self.cog010Ref.append(self.list_save_dic["dicpos_010"][cluster])
            self.cog111Ref.append(self.list_save_dic["dicpos_111"][cluster])

        self.cogRef = np.array(self.cogRef)

        self.cog000Ref = np.array(self.cog000Ref)
        self.cog100Ref = np.array(self.cog100Ref)
        self.cog010Ref = np.array(self.cog010Ref)
        self.cog111Ref = np.array(self.cog111Ref)

        self.pv000Ref = np.array(self.pv000Ref)
        self.pv100Ref = np.array(self.pv100Ref)
        self.pv010Ref = np.array(self.pv010Ref)
        self.pv111Ref = np.array(self.pv111Ref)
        print("Arrays ready")

    #    return self.cogRef, self.cog000Ref, self.cog100Ref, self.cog010Ref, self.cog111Ref, self.pv000Ref, self.pv100Ref, self.pv010Ref, self.pv111Ref

    def load_raw_data(self):
        """
        Loading events and photon values from hdf5 data

        @return: None
        @rtype:
        """
        print("cogRef")
        with h5py.File("{}cogRef.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.cogRef = dset[:]

        print("cog000")
        with h5py.File("{}cog000ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.cog000Ref = dset[:]

        print("cog100")
        with h5py.File("{}cog100ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.cog100Ref = dset[:]

        print(010)
        with h5py.File("{}cog010ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.cog010Ref = dset[:]

        print("cog111")
        with h5py.File("{}cog111ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.cog111Ref = dset[:]

        print("pv000")
        with h5py.File("{}pv000ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.pv000Ref = dset[:]

        print("pv100")
        with h5py.File("{}pv100ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.pv100Ref = dset[:]

        print("pv010")
        with h5py.File("{}pv010ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.pv010Ref = dset[:]

        print("pv111")
        with h5py.File("{}pv111ref.hdf5".format(self.pathtodirectoryReadHDF5), "r") as f:
            dset = f["data"]
            self.pv111Ref = dset[:]

    def valid_events(self, n_events):
        """
        Filter events with conditions obtained by HitAnalysis (full neighbours filter)
        Comments: Masked arrays are computationally more expensive than normal arrays
        Only 4 out of 8 cog computed centers are used due to their easy visualization
        @return: None
        @rtype:
        """
        self.new_cog000 = []
        self.new_cog100 = []
        self.new_cog010 = []
        self.new_cog111 = []

        for i_n in range(n_events):             # range(len(self.new_cog000))
            if i_n % (n_events/5) == 0:
                print(i_n)

            if self.cogRef[i_n][0]:
                self.new_cog000.append(self.cog000Ref[i_n])
            if self.cogRef[i_n][1]:
                self.new_cog100.append(self.cog100Ref[i_n])
            if self.cogRef[i_n][2]:
                self.new_cog010.append(self.cog010Ref[i_n])
            if self.cogRef[i_n][3]:
                self.new_cog111.append(self.cog111Ref[i_n])

        self.cog000Ref = self.new_cog000
        self.cog100Ref = self.new_cog100
        self.cog010Ref = self.new_cog010
        self.cog111Ref = self.new_cog111

        self.cog000Ref = np.array(self.cog000Ref)
        self.cog100Ref = np.array(self.cog100Ref)
        self.cog010Ref = np.array(self.cog010Ref)
        self.cog111Ref = np.array(self.cog111Ref)


    def region_ana(self):#, xmin,xmax,ymin,ymax):
        """
        Filter events using region of interest (square)
        
        @return: None
        @rtype:
        """
#        self.xmax = xmax
#        self.xmin = xmin
#        self.ymax = ymax
#        self.ymin = ymin
        #the limits set are those to obtain the peaks needed, it must be adaptable!!
        #limits must be defined for every COG
        self.Ref000_Sections = []
        self.Ref010_Sections = []
        self.Ref100_Sections = []
        self.Ref111_Sections = []

        y_shift = 0
        for i_000 in range(6):
            x_shift = 0
            for j_000 in range(6):
                self.Section000Ref = self.cog000Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.cog000Ref[:,0],-21.7+x_shift),np.less_equal(self.cog000Ref[:,0],-18.3+x_shift)),np.logical_and(np.greater_equal(self.cog000Ref[:,1],18.3-y_shift),np.less_equal(self.cog000Ref[:,1],21.7-y_shift))))]
                self.Ref000_Sections.append(self.Section000Ref)
                
                x_shift += 8
            y_shift += 8
            
        y_shift = 0
        for i_010 in range(5):
            x_shift = 0
            for j_010 in range(6):
                self.Section010Ref = self.cog010Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.cog010Ref[:,0],-21.7+x_shift),np.less_equal(self.cog010Ref[:,0],-18.3+x_shift)),np.logical_and(np.greater_equal(self.cog010Ref[:,1],12-y_shift),np.less_equal(self.cog010Ref[:,1],19.8-y_shift))))]
                self.Ref010_Sections.append(self.Section010Ref)

                x_shift += 8
            y_shift += 8

        y_shift = 0
        for i_100 in range(6):
            x_shift = 0
            for j_100 in range(5):
                self.Section100Ref = self.cog100Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.cog100Ref[:,0],-20+x_shift),np.less_equal(self.cog100Ref[:,0],-12+x_shift)),np.logical_and(np.greater_equal(self.cog100Ref[:,1],18.7-y_shift),np.less_equal(self.cog100Ref[:,1],21.3-y_shift))))]
                self.Ref100_Sections.append(self.Section100Ref)

                x_shift += 8
            y_shift += 8 
            
        y_shift = 0
        for i_111 in range(5):
            x_shift = 0
            for j_111 in range(5):
                self.Section111Ref = self.cog111Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.cog111Ref[:,0],-20+x_shift),np.less_equal(self.cog111Ref[:,0],-12+x_shift)),np.logical_and(np.greater_equal(self.cog111Ref[:,1],12-y_shift),np.less_equal(self.cog111Ref[:,1],20-y_shift))))]
                self.Ref111_Sections.append(self.Section111Ref)

                x_shift += 8
            y_shift += 8


    def save_raw_data(self):
        """
        Saving events and photon values into hdf5 data

        @return: None
        @rtype:
        """
        n_events = int(len(self.cogRef))
        #MODIFY NUMBER OF EVENTS FOR ALL POSSIBLE FILES
        with h5py.File('{}cogRef.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events, 4), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.cogRef[i: i + dset.chunks[0]]

        with h5py.File('{}cog000ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events, 2), chunks=True)
            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.cog000Ref[i: i + dset.chunks[0]]

        with h5py.File('{}cog100ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events, 2), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.cog100Ref[i: i + dset.chunks[0]]

        with h5py.File('{}cog010ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events, 2), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.cog010Ref[i: i + dset.chunks[0]]

        with h5py.File('{}cog111ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events, 2), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.cog111Ref[i: i + dset.chunks[0]]


        with h5py.File('{}pv000ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events,), chunks=True)
            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.pv000Ref[i: i + dset.chunks[0]]

        with h5py.File('{}pv100ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events,), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.pv100Ref[i: i + dset.chunks[0]]

        with h5py.File('{}pv010ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events,), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.pv010Ref[i: i + dset.chunks[0]]

        with h5py.File('{}pv111ref.hdf5'.format(self.pathtodirectorySaveHDF5), 'w') as f:
            dset = f.create_dataset("data", (n_events,), chunks=True)

            for i in range(0, n_events, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self.pv111Ref[i: i + dset.chunks[0]]

    def save_RefSection_into_file(self):
        """
        Saving flood maps hits into pickle data
        
        @return: None
        @rtype:
        """
        #to save alltogether:
        # Hyp.Ref000_Sections_together = np.zeros((149641579, 2))
        #
        # w = 0
        # for i in range(len(Hyp.Ref000_Sections)):
        #     for j in range(len(Hyp.Ref000_Sections[i])):
        #         Hyp.Ref000_Sections_together[w] = Hyp.Ref000_Sections[i][j]
        #         w += 1

        with open('{}Ref000_Sections.pickle'.format(self.pathtodirectorySaveRefSections), 'wb') as handle:
            pickle.dump(self.Ref000_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('{}Ref010_Sections.pickle'.format(self.pathtodirectorySaveRefSections), 'wb') as handle:
            pickle.dump(self.Ref010_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('{}Ref100_Sections.pickle'.format(self.pathtodirectorySaveRefSections), 'wb') as handle:
            pickle.dump(self.Ref100_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('{}Ref111_Sections.pickle'.format(self.pathtodirectorySaveRefSections), 'wb') as handle:
            pickle.dump(self.Ref111_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
    
    def save_hist_into_file(self):
        """
        Saving Histograms into pickle data
        
        @return: None
        @rtype:
        """
        self.hist0_all = []
        self.hist01_all = []
        self.hist10_all = []
        self.hist1_all = []
    
        for i_36 in range(36):
            fig, axs = plt.subplots(nrows=2, ncols=2)
            
            axs[0, 0].set_title('Linear normalization')
            hist0 = axs[0, 0].hist2d(self.Ref000_Sections[i_36][:, 0], self.Ref000_Sections[i_36][:, 1], bins=100)
            self.hist0_all.append(hist0)
            
            with open('{}hist000_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                pickle.dump(hist0, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
            
            if i_36 < 30:
                axs[0, 1].set_title('Linear normalization')
                hist01 = axs[0, 1].hist2d(self.Ref010_Sections[i_36][:, 0], self.Ref010_Sections[i_36][:, 1], bins=100)
                self.hist01_all.append(hist01)
                with open('{}hist010_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist01, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

                axs[1, 0].set_title('Linear normalization')
                hist10 = axs[1, 0].hist2d(self.Ref100_Sections[i_36][:, 0], self.Ref100_Sections[i_36][:, 1], bins=100)
                self.hist10_all.append(hist10)
                with open('{}hist100_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist10, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

            if i_36 < 25:
                axs[1, 1].set_title('Linear normalization')
                hist1 = axs[1, 1].hist2d(self.Ref111_Sections[i_36][:, 0], self.Ref111_Sections[i_36][:, 1], bins=100)
                self.hist1_all.append(hist1)
                with open('{}hist111_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist1, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

        with open('{}hist000.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist0_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
            
        with open('{}hist010.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist01_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
            
        with open('{}hist100.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist10_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27) 
            
        with open('{}hist111.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist1_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

    def save_hist_into_file_noplot(self):
        """
        Saving Histograms into pickle data

        @return: None
        @rtype:
        """
        self.hist0_all = []
        self.hist01_all = []
        self.hist10_all = []
        self.hist1_all = []

        for i_36 in range(36):

            hist0 = np.histogram2d(self.Ref000_Sections[i_36][:, 0], self.Ref000_Sections[i_36][:, 1], bins=100)
            self.hist0_all.append(hist0)

            with open('{}hist000_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                pickle.dump(hist0, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

            if i_36 < 30:
                hist01 = np.histogram2d(self.Ref010_Sections[i_36][:, 0], self.Ref010_Sections[i_36][:, 1], bins=100)
                self.hist01_all.append(hist01)
                with open('{}hist010_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist01, handle,
                                protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

                hist10 = np.histogram2d(self.Ref100_Sections[i_36][:, 0], self.Ref100_Sections[i_36][:, 1], bins=100)
                self.hist10_all.append(hist10)
                with open('{}hist100_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist10, handle,
                                protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

            if i_36 < 25:
                hist1 = np.histogram2d(self.Ref111_Sections[i_36][:, 0], self.Ref111_Sections[i_36][:, 1], bins=100)
                self.hist1_all.append(hist1)
                with open('{}hist111_{}.pickle'.format(self.pathtodirectorySavehist, str(i_36)), 'wb') as handle:
                    pickle.dump(hist1, handle,
                                protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

        with open('{}hist000.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist0_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

        with open('{}hist010.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist01_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

        with open('{}hist100.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist10_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

        with open('{}hist111.pickle'.format(self.pathtodirectorySavehist), 'wb') as handle:
            pickle.dump(self.hist1_all, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def runHypmed(self):
        self.load_raw_data()
        self.valid_events()
        self.region_ana()
        self.save_RefSection_into_file()
        self.save_hist_into_file_noplot()