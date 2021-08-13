# -*- coding: utf-8 -*-
__author__ = 'david.perez.gonzalez'
"""
Run_CreateDataCRT.py provides a frame to run the different routines to create the 
hdf5 files out of the raw data in the .DebugCoincidentSingles files.
"""

import os
import argparse
# import psutil
# import cPickle as pickle
import datetime
# from time import sleep

'''
Directory of files should be in a ini file for future uses of this project, right now it is not needed since it is run always in the same machine
'''

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    # parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')
    parser.add_argument('--saveDirectory', dest='saveDirect', help='Specifiy the name of the   \
                                                         directory where to save the files')
    # parser.add_argument('--precision', dest='decimals', help='Specifiy the precision of the lut \
    #                                                      e.g.: "0.01" or "0.1".')
    # parser.add_argument('--nEvents', dest='nEvents', help='Specifiy the number of events  \
    #                                                      (N where N=0,1,2,..., finalEvent)')

    args = parser.parse_args()
    # decimals, stack_id, n_Events, pathtodirectory = args.decimals, args.sID, int(args.nEvents), args.fileDirect
    pathtodirectory, savedirectory = args.fileDirect, args.saveDirect

    # command_RemLin = 'python /home/david.perez/cia/CreateData/RemoveLastLine.py --stackID {} --fileDirectory {}'.format('measurement', pathtodirectory)
    # os.system(command_RemLin)

    command_ReadDB_Photon = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/ReadDebugSinglesCRT_Photon.py --fileDirectory {} --saveDirectory {}'.format(pathtodirectory, savedirectory)
    os.system(command_ReadDB_Photon)

    command_ReadDB_Pos = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/ReadDebugSinglesCRT_Pos.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectory, savedirectory)
    os.system(command_ReadDB_Pos)

    command_ReadDB_TimeStamp = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/ReadDebugSinglesCRT_TimeStamp.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectory, savedirectory)
    os.system(command_ReadDB_TimeStamp)

    command_ReadDB_Val = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/ReadDebugSinglesCRT_Val.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectory, savedirectory)
    os.system(command_ReadDB_Val)

    command_ReadDB_PV = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/ReadDebugSinglesCRT_PV.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectory, savedirectory)
    os.system(command_ReadDB_PV)

    command_NH = 'python /home/janko.lambertus/Masterarbeit/Git/cia/CreateData/NewHypmed_main.py --fileDirectory {}'.format(savedirectory)
    os.system(command_NH)

    command_CiA = 'python /home/janko.lambertus/git/cia/ScriptoRun/RunCiA.py --fileDirectory {} --HVD -1 --nCPU 6 --precision 0.1 --nEvents 30'.format(savedirectory)
    os.system(command_CiA)

if __name__ == '__main__':
    main()


# python Run_CreateDataCRT.py --fileDirectory /media/janko.lambertus/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ --saveDirectory /media/janko.lambertus/pet-scratch/Janko/Master/Data/CIA_FT/Test3/