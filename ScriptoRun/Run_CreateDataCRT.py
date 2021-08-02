import os
import argparse
import psutil
import cPickle as pickle
import datetime
from time import sleep

'''
Directory of files should be in a ini file for future uses of this project, right now it is not needed since it is run always in the same machine
'''

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    # parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')
    # parser.add_argument('--precision', dest='decimals', help='Specifiy the precision of the lut \
    #                                                      e.g.: "0.01" or "0.1".')
    # parser.add_argument('--nEvents', dest='nEvents', help='Specifiy the number of events  \
    #                                                      (N where N=0,1,2,..., finalEvent)')

    args = parser.parse_args()
    # decimals, stack_id, n_Events, pathtodirectory = args.decimals, args.sID, int(args.nEvents), args.fileDirect
    pathtodirectory = args.fileDirect

    # command_RemLin = 'python /home/david.perez/cia/CreateData/RemoveLastLine.py --stackID {} --fileDirectory {}'.format('measurement', pathtodirectory)
    # os.system(command_RemLin)

    # print('waiting...')
    # sleep(18000)

    # command_ReadDB_Photon = 'python /home/david.perez/cia/CreateData/ReadDebugSinglesCRT_Photon.py --fileDirectory {}'.format(pathtodirectory)
    # os.system(command_ReadDB_Photon)

    command_ReadDB_Pos = 'python /home/david.perez/cia/CreateData/ReadDebugSinglesCRT_Pos.py --fileDirectory {}'.format(
        pathtodirectory)
    os.system(command_ReadDB_Pos)

    # command_ReadDB_TimeStamp = 'python /home/david.perez/cia/CreateData/ReadDebugSinglesCRT_TimeStamp.py --fileDirectory {}'.format(
    #     pathtodirectory)
    # os.system(command_ReadDB_TimeStamp)

    command_ReadDB_Val = 'python /home/david.perez/cia/CreateData/ReadDebugSinglesCRT_Val.py --fileDirectory {}'.format(
        pathtodirectory)
    os.system(command_ReadDB_Val)

    command_ReadDB_PV = 'python /home/david.perez/cia/CreateData/ReadDebugSinglesCRT_PV.py --fileDirectory {}'.format(
        pathtodirectory)
    os.system(command_ReadDB_PV)

    # command_NH = 'python /home/david.perez/cia/CreateData/NewHypmed_main.py --fileDirectory {}'.format(pathtodirectory)
    # os.system(command_NH)

    # command_CiA = 'python /home/david.perez/cia/ScriptoRun/RunCiA.py --fileDirectory {} --HVD -1 --nCPU 6 --precision {} --nEvents {}'.format(pathtodirectory, decimals, n_Events)
    # os.system(command_CiA)

if __name__ == '__main__':
    main()