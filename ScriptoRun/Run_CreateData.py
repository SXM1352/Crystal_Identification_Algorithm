import os
import argparse
import psutil
import cPickle as pickle
import datetime


def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')

    args = parser.parse_args()
    stack_id, pathtodirectory = args.sID, args.fileDirect

    command_RemLin = 'python RemoveLastLine.py --stackID {} --fileDirectory {}'.format(stack_id, pathtodirectory)
    os.system(command_RemLin)

    command_ReadDB = 'python ReadDebugSinglesTotal.py --stackID {} --fileDirectory {}'.format(stack_id, pathtodirectory)
    os.system(command_ReadDB)

    command_ReadDB = 'python NewHypmed_main.py --fileDirectory {}'.format(pathtodirectory)
    os.system(command_ReadDB)

    command_CiA = 'python RunCiA.py --fileDirectory {} --HVD -1'.format(pathtodirectory)
    os.system(command_CiA)

if __name__ == '__main__':
    main()