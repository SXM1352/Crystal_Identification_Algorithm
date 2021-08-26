# -*- coding: utf-8 -*-
__author__ = 'david.perez.gonzalez'
"""
RunCiA.py provides a frame to run the different routines to create the 
Crystal Position Maps out of the hdf5 data files.
"""

import os
import argparse
import psutil
import cPickle as pickle
import datetime
# from time import sleep

from GroupPickles_LUT import LUT_Group

def __chunkify_data(size):
    """
    function to divide a large file into chunks each having size ~= size so that the chunks are equal

    Params :
        fname : path to the file to be chunked
        size : size of each chunk is ~> this
    Returns :
        start and end position of chunks in Bytes
    """
    chunks = []
    chunkEnd = 24
    dataEnd = -24

    while True:
        chunkStart = chunkEnd
        chunkEnd = chunkStart - size
        if chunkEnd < dataEnd:
            #chunkEnd = dataEnd
            #chunks.append([chunkStart, chunkEnd])
            break
        chunks.append([chunkStart, chunkEnd])

    return chunks

def write_commands(jobs, pathtodirectory, jobs_per_HVD, precision):
    list_commands = []
    for j in jobs:
        for j_HVD in jobs_per_HVD:
            print("j = ", j)
            print("j_HVD = ", j_HVD)
            command = 'python' + ' ' + '/home/janko.lambertus/Masterarbeit/Git/cia/LUT/LUT.py' + ' --HVD {} --fileDirectory {} --initEvent {} --finalEvent {} --precision {}'.format(j, pathtodirectory, j_HVD[0], j_HVD[1], precision) #/home/david.perez/newEnv/Tenerife/gitFolder/monocal/Positioning/
            list_commands.append(command)
    return list_commands
def create_finalCommand(list_commands):
    fCommand = ''
    for com in list_commands:
        if fCommand:
            fCommand = fCommand + ' & ' + com
        else:
            fCommand = com
    return fCommand
def __save_Jobs(jobs, pathtodirectorySave):
    with open('{}Jobs_list.pickle'.format(pathtodirectorySave), 'wb') as handle:
        pickle.dump(jobs, handle,
                    protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    parser.add_argument('--HVD N', dest='HVD', help='Specifiy the HVD algorithm to show  \
                                                     (N where N= 0 (=000), 1 (=100), 2 (=010), 3 (=111) or -1 for ALL)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')
    parser.add_argument('--saveDirectory', dest='SavePlot', help='Specifiy the name of the   \
                                                             directory where to save the files in.', default='None')
    parser.add_argument('--nCPU', dest='nCPU', help='Specifiy the number of CPUs to be used per HVD  \
                                                 (N where N=1,2,... up to 6 if HVD=-1)')
    parser.add_argument('--precision', dest='decimals', help='Specifiy the precision of the lut \
                                                     e.g.: "0.01" or "0.1".')
    parser.add_argument('--nEvents', dest='nEvents', help='Specifiy the number of events  \
                                                     (N where N=0,1,2,..., finalEvent)')

    args = parser.parse_args()
    decimals, n_Procs, selected_HVD, n_Events, pathtodirectory, savePlot = args.decimals, int(args.nCPU), int(args.HVD), int(args.nEvents), args.fileDirect, args.SavePlot

    #Run routine to find peaks
    print("AAAAAAAAAAAAAAAAAAAAA")
    command_PeakF = 'python /home/janko.lambertus/Masterarbeit/Git/cia/Ci/Peaks/Peak_main.py --fileDirectory {} --HVD -1'.format(pathtodirectory)
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    os.system(command_PeakF)

    #run routine to label peaks
    print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
    command_SanCheck = 'python /home/janko.lambertus/Masterarbeit/Git/cia/Ci/SanCheck/SanCheck_main.py --HVD -1 --fileDirectory {} --saveDirectory {}'.format(pathtodirectory, savePlot)
    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
    os.system(command_SanCheck)
    print("EEEEEEEEEEEEEEEEEEEEEEEEEEE")
    pathtodirectoryReadLUD = 'dic-LUD/'
    print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")

    CHECK_FOLDER = os.path.isdir(pathtodirectory + pathtodirectoryReadLUD)
    print("GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG")
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectory + pathtodirectoryReadLUD)
        print("created folder : ", pathtodirectory + pathtodirectoryReadLUD)
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    if selected_HVD == -1:
        print("IIIIIIIIIIIIIIIIIIIIIIIII")
        jobs = range(4) # we take all HVD algorithms, for only one: 0 (=000), 1 (=100), 2 (=010), 3 (=111)
        print("JJJJJJJJJJJJJJJJJJJJJJJJJ")
    else:
        print("KKKKKKKKKKKKKKKKKKKKKKKKKK")
        jobs = [selected_HVD]
    print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
    #Select number of cpu to use
    n_Procs_total = psutil.cpu_count()
    print("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM")
    if n_Procs >= n_Procs_total:
        print("NNNNNNNNNNNNNNNNNNNNNNNNNNN")
        n_Procs = n_Procs_total - 1
    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
    print('Number of used CPU: ', n_Procs)
    print('Number of available CPU: ', n_Procs_total)

    #Divide jobs for LUT and speed the process up
    n_Events_LUT = 48
    n_jobs_per_proc = int(n_Events_LUT / n_Procs)
    print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")

    jobs_per_HVD = __chunkify_data(n_jobs_per_proc)
    print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
    __save_Jobs(jobs_per_HVD, pathtodirectory)
    print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
    print(jobs)
    print(pathtodirectory)
    print(jobs_per_HVD)
    print(decimals)

    list_commands = write_commands(jobs, pathtodirectory, jobs_per_HVD, decimals)
    print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSs")
    fCommand = create_finalCommand(list_commands)
    print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
    fCommand = fCommand  + ' & wait'
    print("UUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
    # print('waiting...')
    # sleep(4000)
    os.system(fCommand)  # LUT
    print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
    Group_jobs = LUT_Group(jobs_per_HVD, pathtodirectory) #group pickles
    print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
    Group_jobs.runLUTGroup()
    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    precision_grid = len(decimals.split(".")[1])
    print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
    command_CheckC = 'python /home/janko.lambertus/Masterarbeit/Git/cia/ScriptoRun/RunCheckParallel.py --nCPU 24 --nEvents {} --precision {} --fileDirectory {} --saveDirectory {}'.format(n_Events, precision_grid, pathtodirectory, savePlot)
    # from ini file!! nEvents and nCPU
    print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
    os.system(command_CheckC)
    print("FINISHED!!!!")

if __name__ == '__main__':
    main()

