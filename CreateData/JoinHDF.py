# -*- coding: utf-8 -*-
__author__ = "david.perez.gonzalez" 

import numpy as np
import matplotlib.pyplot as plt
#from configparser import ConfigParser
#from config import config
import logging
import os
import time
import h5py
import cPickle as pickle

'108'
pathtodirectoryReadHDF5_side = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-06-18_-_10-17-43_-_CoincSideM/2021-06-18_-_10-18-50_-_015-033-2021_06_18/2021-06-18_-_11-12-49_-_Second3OV_Side30Min/ramdisks_2021-06-18_-_11-50-18/Coinc_analysis/Stack8_coinc/hdf5Data/'
pathtodirectoryReadHDF5_other = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-06-18_-_10-17-43_-_CoincSideM/2021-06-18_-_10-18-50_-_015-033-2021_06_18/2021-06-18_-_12-00-27_-_Third3OV_OtherSide30Min/ramdisks_2021-06-18_-_12-44-54/Coinc_analysis/Stack8_coinc/hdf5Data/'
pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-06-18_-_10-17-43_-_CoincSideM/2021-06-18_-_10-18-50_-_015-033-2021_06_18/2021-06-21_Join-Sides30Min/Coinc_analysis/Stack8_coinc/'

#One side
with h5py.File("{}cogref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    cogRef_side = dset[:]

with h5py.File("{}cog000ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    cog000Ref_side = dset[:]
with h5py.File("{}cog100ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    cog100Ref_side = dset[:]
with h5py.File("{}cog010ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    cog010Ref_side = dset[:]
with h5py.File("{}cog111ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    cog111Ref_side = dset[:]

with h5py.File("{}pv000ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    pv000Ref_side = dset[:]
with h5py.File("{}pv100ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    pv100Ref_side = dset[:]
with h5py.File("{}pv010ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    pv010Ref_side = dset[:]
with h5py.File("{}pv111ref_coinc.hdf5".format(pathtodirectoryReadHDF5_side ), "r") as f:
    dset = f["data"]
    pv111Ref_side = dset[:]


#Other Side
with h5py.File("{}cogRef_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    cogRef_other = dset[:]

with h5py.File("{}cog000ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    cog000Ref_other = dset[:]
with h5py.File("{}cog100ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    cog100Ref_other = dset[:]
with h5py.File("{}cog010ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    cog010Ref_other = dset[:]
with h5py.File("{}cog111ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    cog111Ref_other = dset[:]

with h5py.File("{}pv000ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    pv000Ref_other = dset[:]
with h5py.File("{}pv100ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    pv100Ref_other = dset[:]
with h5py.File("{}pv010ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    pv010Ref_other = dset[:]
with h5py.File("{}pv111ref_coinc.hdf5".format(pathtodirectoryReadHDF5_other), "r") as f:
    dset = f["data"]
    pv111Ref_other = dset[:]
    
cogRef = np.concatenate((cogRef_other, cogRef_side))
cog111Ref = np.concatenate((cog111Ref_other, cog111Ref_side))
cog010Ref = np.concatenate((cog010Ref_other, cog010Ref_side))
cog100Ref = np.concatenate((cog100Ref_other, cog100Ref_side))
cog000Ref = np.concatenate((cog000Ref_other, cog000Ref_side))

pv111Ref = np.concatenate((pv111Ref_other, pv111Ref_side))
pv010Ref = np.concatenate((pv010Ref_other, pv010Ref_side))
pv100Ref = np.concatenate((pv100Ref_other, pv100Ref_side))
pv000Ref = np.concatenate((pv000Ref_other, pv000Ref_side))


# pathtodirectorySave_hdf = "/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/20210315_NEW_hdf5Data/"
pathtodirectorySave_hdf = pathtodirectoryRead + 'hdf5Data/'
folder_dir = pathtodirectorySave_hdf
CHECK_FOLDER = os.path.isdir(folder_dir)
# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.makedirs(folder_dir)
    print("created folder : ", folder_dir)

n_events = int(len(cog000Ref))
# MODIFY NUMBER OF EVENTS FOR ALL POSSIBLE FILES


with h5py.File('{}cogRef_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 4), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cogRef[i: i + dset.chunks[0]]

with h5py.File('{}cog000ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 2), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cog000Ref[i: i + dset.chunks[0]]
        

with h5py.File('{}cog100ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 2), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cog100Ref[i: i + dset.chunks[0]]

with h5py.File('{}cog010ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 2), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cog010Ref[i: i + dset.chunks[0]]

with h5py.File('{}cog111ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 2), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cog111Ref[i: i + dset.chunks[0]]

with h5py.File('{}pv000ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events,), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = pv000Ref[i: i + dset.chunks[0]]

with h5py.File('{}pv100ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events,), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = pv100Ref[i: i + dset.chunks[0]]

with h5py.File('{}pv010ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events,), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = pv010Ref[i: i + dset.chunks[0]]

with h5py.File('{}pv111ref_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events,), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = pv111Ref[i: i + dset.chunks[0]]