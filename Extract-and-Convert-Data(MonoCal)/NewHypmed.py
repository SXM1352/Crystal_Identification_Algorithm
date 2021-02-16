# -*- coding: utf-8 -*-
__author__ = "david.perez.gonzalez" 

#from sklearn.cluster import AgglomerativeClustering, Birch
from Positioning import sciKitSkeleton
from Positioning.skModels import _skbase
from config import config
#from CreateData_v2 import CreateData
#from FeatureAdder import FeatureAdder
from Geometry import GeometryDivide
#from sklearn.neighbors import KNeighborsClassifier,KNeighborsRegressor
#from sklearn import metrics
#from xgboost import XGBClassifier, XGBRegressor, DMatrix
#from EnergyCalibration import EnergyCalibration
#from Positioning.XGB_helper import eval_function_xgb

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

class Hypmed(_skbase):
    """
    Working frame regarding the crystal identification algorithms
    """
    def __init__(self, ini_file=config().monocal_path+"Positioning/Hypmed.ini"):
        self._parameters = {"geometry" : "powertile",
                            "layers" : 3,
                            "n_clusters" : 3425,
                            "pix_size_x" : -1,
                            "pix_size_y" : -1,
                            "pix_pos_x" : None,
                            "pix_pos_y" : None}
        try:
            self._config_read(ini_file)
            print(ini_file)
        except:
            logging.warning("unexpected structure of the ini_file, use the default settings")

        self.sket = sciKitSkeleton()
        self.geo = GeometryDivide(self._parameters["geometry"])
        self._labels = None
        self._centers = np.zeros((self._parameters.get("n_clusters"), 2))
        self._cluster_variance = np.empty((self._parameters.get("n_clusters"),2))
        self._cluster_std = np.empty((self._parameters.get("n_clusters"),2))
        self._centersCOG = np.empty((self._parameters.get("n_clusters"), 2))
        self._COG_positions = None
        self._prediction_ref = None
        self._prediction_test = None
        self.savedir = None #There should be an saving directory in the ini file

    def valid_events(self):
        """
        Filter events with conditions obtained by HitAnalysis converting them into masked arrays
        Comments: Masked arrays are computationally more expensive than normal arrays
        Only 4 out of 8 cog computed centers are used due to their easy visualization
        @return: None
        @rtype:
        """
        self.sket._cogRef = np.logical_xor(self.sket._cogRef,1).astype(int) #swap 1 and 0 to mask events that are invalid #work with this one those with 1 in 4 take 1 sonst no and so on and then use the modified one as masked array!
        self.sket._cog000Ref = np.ma.masked_array(self.sket._cog000Ref, mask=np.column_stack((self.sket._cogRef[:,0],self.sket._cogRef[:,0])))
        self.sket._cog100Ref = np.ma.masked_array(self.sket._cog100Ref, mask=np.column_stack((self.sket._cogRef[:,1],self.sket._cogRef[:,1])))
        self.sket._cog010Ref = np.ma.masked_array(self.sket._cog010Ref, mask=np.column_stack((self.sket._cogRef[:,2],self.sket._cogRef[:,2])))
#        self.sket._cog110Ref = np.ma.masked_array(self.sket._cog110Ref, mask=np.column_stack((self.sket._cogRef[:,3],self.sket._cogRef[:,3])))
#        self.sket._cog001Ref = np.ma.masked_array(self.sket._cog001Ref, mask=np.column_stack((self.sket._cogRef[:,4],self.sket._cogRef[:,4])))
#        self.sket._cog101Ref = np.ma.masked_array(self.sket._cog101Ref, mask=np.column_stack((self.sket._cogRef[:,5],self.sket._cogRef[:,5])))
#        self.sket._cog011Ref = np.ma.masked_array(self.sket._cog011Ref, mask=np.column_stack((self.sket._cogRef[:,6],self.sket._cogRef[:,6])))
        self.sket._cog111Ref = np.ma.masked_array(self.sket._cog111Ref, mask=np.column_stack((self.sket._cogRef[:,7],self.sket._cogRef[:,3]))) # instead of 3, it should be 7 when we are importing 8 COG
        
        # self.sket._cogTest = np.logical_xor(self.sket._cogTest,1).astype(int)
        # self.sket._cog000Test = np.ma.masked_array(self.sket._cog000Test, mask=np.column_stack((self.sket._cogTest[:,0],self.sket._cogTest[:,0])))
        # self.sket._cog100Test = np.ma.masked_array(self.sket._cog100Test, mask=np.column_stack((self.sket._cogTest[:,1],self.sket._cogTest[:,1])))
        # self.sket._cog010Test = np.ma.masked_array(self.sket._cog010Test, mask=np.column_stack((self.sket._cogTest[:,2],self.sket._cogTest[:,2])))
#        self.sket._cog110Test = np.ma.masked_array(self.sket._cog110Test, mask=np.column_stack((self.sket._cogTest[:,3],self.sket._cogTest[:,3])))
#        self.sket._cog001Test = np.ma.masked_array(self.sket._cog001Test, mask=np.column_stack((self.sket._cogTest[:,4],self.sket._cogTest[:,4])))
#        self.sket._cog101Test = np.ma.masked_array(self.sket._cog101Test, mask=np.column_stack((self.sket._cogTest[:,5],self.sket._cogTest[:,5])))
#        self.sket._cog011Test = np.ma.masked_array(self.sket._cog011Test, mask=np.column_stack((self.sket._cogTest[:,6],self.sket._cogTest[:,6])))
#         self.sket._cog111Test = np.ma.masked_array(self.sket._cog111Test, mask=np.column_stack((self.sket._cogTest[:,7],self.sket._cogTest[:,7])))

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
                self.Section000Ref = self.sket._cog000Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.sket._cog000Ref[:,0],-21.7+x_shift),np.less_equal(self.sket._cog000Ref[:,0],-18.3+x_shift)),np.logical_and(np.greater_equal(self.sket._cog000Ref[:,1],18.3-y_shift),np.less_equal(self.sket._cog000Ref[:,1],21.7-y_shift))))]
                self.Ref000_Sections.append(self.Section000Ref)
                
                x_shift += 8
            y_shift += 8
            
        y_shift = 0
        for i_010 in range(5):
            x_shift = 0
            for j_010 in range(6):
                self.Section010Ref = self.sket._cog010Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.sket._cog010Ref[:,0],-21.7+x_shift),np.less_equal(self.sket._cog010Ref[:,0],-18.3+x_shift)),np.logical_and(np.greater_equal(self.sket._cog010Ref[:,1],12-y_shift),np.less_equal(self.sket._cog010Ref[:,1],19.8-y_shift))))]
                self.Ref010_Sections.append(self.Section010Ref)

                x_shift += 8
            y_shift += 8

        y_shift = 0
        for i_100 in range(6):
            x_shift = 0
            for j_100 in range(5):
                self.Section100Ref = self.sket._cog100Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.sket._cog100Ref[:,0],-20+x_shift),np.less_equal(self.sket._cog100Ref[:,0],-12+x_shift)),np.logical_and(np.greater_equal(self.sket._cog100Ref[:,1],18.7-y_shift),np.less_equal(self.sket._cog100Ref[:,1],21.3-y_shift))))]
                self.Ref100_Sections.append(self.Section100Ref)

                x_shift += 8
            y_shift += 8 
            
        y_shift = 0
        for i_111 in range(5):
            x_shift = 0
            for j_111 in range(5):
                self.Section111Ref = self.sket._cog111Ref[np.where(np.logical_and(np.logical_and(np.greater_equal(self.sket._cog111Ref[:,0],-20+x_shift),np.less_equal(self.sket._cog111Ref[:,0],-12+x_shift)),np.logical_and(np.greater_equal(self.sket._cog111Ref[:,1],12-y_shift),np.less_equal(self.sket._cog111Ref[:,1],20-y_shift))))]
                self.Ref111_Sections.append(self.Section111Ref)

                x_shift += 8
            y_shift += 8

    def load_raw_data(self):
        """
        Loading events and photon values from hdf5 data

        @return: None
        @rtype:
        """

        with h5py.File("cogRef.hdf5", "r") as f:
            dset = f["data"]
            self._cogRef = dset[:]

        with h5py.File("cog000ref.hdf5", "r") as f:
            dset = f["data"]
            self._cog000Ref = dset[:]
        with h5py.File("cog100Ref.hdf5", "r") as f:
            dset = f["data"]
            self._cog100Ref = dset[:]
        with h5py.File("cog010Ref.hdf5", "r") as f:
            dset = f["data"]
            self._cog010Ref = dset[:]
        with h5py.File("cog111Ref.hdf5", "r") as f:
            dset = f["data"]
            self._cog111Ref = dset[:]

        with h5py.File("pv000ref.hdf5", "r") as f:
            dset = f["data"]
            self._pv000Ref = dset[:]
        with h5py.File("pv100Ref.hdf5", "r") as f:
            dset = f["data"]
            self._pv100Ref = dset[:]
        with h5py.File("pv010Ref.hdf5", "r") as f:
            dset = f["data"]
            self._pv010Ref = dset[:]
        with h5py.File("pv111Ref.hdf5", "r") as f:
            dset = f["data"]
            self._pv111Ref = dset[:]


    def save_raw_data(self):
        """
        Saving events and photon values into hdf5 data

        @return: None
        @rtype:
        """
        #MODIFY NUMBER OF EVENTS FOR ALL POSSIBLE FILES
        with h5py.File('cogRef.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925, 4), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self._cogRef[i: i + dset.chunks[0]]

        with h5py.File('cog000Ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925, 2), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self._cog000Ref[i: i + dset.chunks[0]]

        with h5py.File('cog100ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925, 2), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self._cog100Ref[i: i + dset.chunks[0]]

        with h5py.File('cog010ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925, 2), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self._cog010Ref[i: i + dset.chunks[0]]

        with h5py.File('cog111ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925, 2), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = self._cog111Ref[i: i + dset.chunks[0]]


        with h5py.File('pv000ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925,), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = Hyp.sket._pv000Ref[i: i + dset.chunks[0]]

        with h5py.File('pv100ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925,), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = Hyp.sket._pv100Ref[i: i + dset.chunks[0]]

        with h5py.File('pv010ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925,), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = Hyp.sket._pv010Ref[i: i + dset.chunks[0]]

        with h5py.File('pv111ref.hdf5', 'w') as f:
            dset = f.create_dataset("data", (149703925,), chunks=True)

            for i in range(0, 149703925, dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = Hyp.sket._pv111Ref[i: i + dset.chunks[0]]

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

        with open('Ref000_Sections.pickle', 'wb') as handle:
            pickle.dump(self.Ref000_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('Ref010_Sections.pickle', 'wb') as handle:
            pickle.dump(self.Ref010_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('Ref100_Sections.pickle', 'wb') as handle:
            pickle.dump(self.Ref100_Sections, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('Ref111_Sections.pickle', 'wb') as handle:
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
            
            with open('hist000_{}.pickle'.format(str(i_36)), 'wb') as handle:
                pickle.dump(hist0, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
            
            if i_36 < 30:
                axs[0, 1].set_title('Linear normalization')
                hist01 = axs[0, 1].hist2d(self.Ref010_Sections[i_36][:, 0], self.Ref010_Sections[i_36][:, 1], bins=100)
                self.hist01_all.append(hist01)
                with open('hist010_{}.pickle'.format(str(i_36)), 'wb') as handle:
                    pickle.dump(hist01, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

                axs[1, 0].set_title('Linear normalization')
                hist10 = axs[1, 0].hist2d(self.Ref100_Sections[i_36][:, 0], self.Ref100_Sections[i_36][:, 1], bins=100)
                self.hist10_all.append(hist10)
                with open('hist100_{}.pickle'.format(str(i_36)), 'wb') as handle:
                    pickle.dump(hist10, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

            if i_36 < 25:
                axs[1, 1].set_title('Linear normalization')
                hist1 = axs[1, 1].hist2d(self.Ref111_Sections[i_36][:, 0], self.Ref111_Sections[i_36][:, 1], bins=100)
                self.hist1_all.append(hist1)
                with open('hist111_{}.pickle'.format(str(i_36)), 'wb') as handle:
                    pickle.dump(hist1, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

        with open('hist000.pickle', 'wb') as handle:
            pickle.dump(self.hist0_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
            
        with open('hist010.pickle', 'wb') as handle:
            pickle.dump(self.hist01_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
            
        with open('hist100.pickle', 'wb') as handle:
            pickle.dump(self.hist10_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27) 
            
        with open('hist111.pickle', 'wb') as handle:
            pickle.dump(self.hist1_all, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

