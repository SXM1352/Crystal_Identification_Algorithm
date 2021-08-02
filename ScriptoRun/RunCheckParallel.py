# -*- coding: utf-8 -*-
__author__ = 'david.perez.gonzalez'
"""
RunCheckParallel.py provides a frame to iterate over the clusters and
identify the scintillating crystal, find calibration factors of each crystal
in every ROI, determine the energy of the scintillating event and plot the energy spectra.
"""

import os
import argparse
import psutil
import cPickle as pickle
import datetime
from time import sleep

from GroupPickles import C_Group
# from CalibPVLoadandPlot import CalibLoadPlot

def __chunkify_data(n_proc, size):
    """
    function to divide a large file into chunks each having size ~= size so that the chunks are equal

    Params :
        fname : path to the file to be chunked
        size : size of each chunk is ~> this
    Returns :
        start and end position of chunks in Bytes
    """
    chunks = []
    chunkEnd = 0
    dataEnd = n_proc*size

    while True:
        chunkStart = chunkEnd
        chunkEnd = chunkStart + size
        if chunkEnd > dataEnd:
            #chunkEnd = dataEnd
            #chunks.append([chunkStart, chunkEnd])
            break
        chunks.append([chunkStart, chunkEnd])

    return chunks

def write_commands(jobs, pathtodirectoryRead, decimals, stack_type):
    list_commands = []
    for j in jobs:
        if stack_type == '_coinc' or stack_type == '_cal':
            command = 'python' + ' ' + '/home/david.perez/cia/Clusters/CheckClusterParallel_main.py' + ' --initEvent {} --finalEvent {} --fileDirectory {} --precision {} --typeStack {}'.format(j[0], j[1], pathtodirectoryRead, decimals, stack_type)

        else:
            command = 'python' + ' ' + '/home/david.perez/cia/Clusters/CheckClusterParallel_main.py' + ' --initEvent {} --finalEvent {} --fileDirectory {} --precision {}'.format(j[0], j[1], pathtodirectoryRead, decimals)

        list_commands.append(command)
    return list_commands
def write_commands_calib(jobs, pathtodirectoryRead, stack_type):
    list_commands = []
    for j in jobs:
        if stack_type == '_coinc' or stack_type == '_cal':
            command = 'python' + ' ' + '/home/david.perez/cia/EneRes/CalibPVSpectrum_main.py' + ' --finalEvent {} --fileDirectory {} --typeStack {}'.format(j[1], pathtodirectoryRead, stack_type)

        else:
            command = 'python' + ' ' + '/home/david.perez/cia/EneRes/CalibPVSpectrum_main.py' + ' --finalEvent {} --fileDirectory {}'.format(j[1], pathtodirectoryRead)

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

def checkFolder(pathDirectory):
    CHECK_FOLDER = os.path.isdir(pathDirectory)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathDirectory)
        print("created folder : ", pathDirectory)

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    parser.add_argument('--nCPU', dest='nCPU', help='Specifiy the number of CPUs to be used  \
                                             (N where N=1,2,...)')
    parser.add_argument('--nEvents', dest='nEvents', help='Specifiy the number of events  \
                                                 (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                     directory where to read the files from')
    parser.add_argument('--saveDirectory', dest='SavePlot', help='Specifiy the name of the   \
                                                                 directory where to save the files in.', default='None')
    parser.add_argument('--precision', dest='decimals', help='Specifiy the precision of the lut \
                                                             e.g.: "2" for 0.01 or "1" for 0.1.')
    parser.add_argument('--typeStack', dest='typeStack', help='Specifiy if the stack is  \
                                                                         "_cal" or "_coinc".',
                        default='')
    args = parser.parse_args()
    decimals, n_Procs, n_Events, pathtodirectoryRead, savePlot, stack_type = args.decimals, int(args.nCPU), int(args.nEvents), args.fileDirect, args.SavePlot, args.typeStack

    pathtodirectorySaveParallel = 'Parallel/'
    pathtodirectorySavePV = 'PhotonSpectrum/'

    checkFolder(pathtodirectoryRead)

    checkFolder(pathtodirectoryRead + pathtodirectorySaveParallel)

    checkFolder(pathtodirectoryRead + pathtodirectorySaveParallel + pathtodirectorySavePV)

    n_Procs_total = psutil.cpu_count()
    if n_Procs >= n_Procs_total:
        n_Procs = n_Procs_total - 1

    print('Number of used CPU: ', n_Procs)
    print('Number of available CPU: ', n_Procs_total)

    n_jobs_per_proc = int(n_Events/n_Procs)

    jobs = __chunkify_data(n_Procs, n_jobs_per_proc)
    __save_Jobs(jobs, pathtodirectoryRead + pathtodirectorySaveParallel)

    list_commands = write_commands(jobs, pathtodirectoryRead, decimals, stack_type)

    fCommand = create_finalCommand(list_commands)

    fCommand = fCommand  + ' & wait'

    print('Final Command:', fCommand)

    # print('waiting...')
    # sleep(4000)

    os.system(fCommand) #check clusters

    Group_jobs = C_Group(jobs, pathtodirectoryRead + pathtodirectorySaveParallel, pathtodirectorySavePV) #group pickles
    Group_jobs.runCGroup()

    FitEnSpectrumCommand = 'python' + ' ' + '/home/david.perez/cia/EneRes/FitEnergySpectrumRunAll.py' + ' --fileDirectory {}'.format(pathtodirectoryRead + pathtodirectorySaveParallel + pathtodirectorySavePV) + ' & wait'

    os.system(FitEnSpectrumCommand) #fit crystals on HVDs to find calib_factors

    list_commands_calib = write_commands_calib(jobs, pathtodirectoryRead, stack_type)

    fCommand_Calib = create_finalCommand(list_commands_calib)

    fCommand_Calib = fCommand_Calib + ' & wait'

    os.system(fCommand_Calib) #calibrate detector

    CalibLoadPlotCommand = 'python' + ' ' + '/home/david.perez/cia/EneRes/CalibPVLoadandPlot_main.py' + ' --fileDirectory {}'.format(pathtodirectoryRead) + ' & wait'
    os.system(CalibLoadPlotCommand)  # plot calib detector

    if stack_type == '_coinc' or stack_type == '_cal':
        command_Plot = 'python /home/david.perez/cia/ScriptoRun/RunPlot.py --fileDirectory {} --saveDirectory {} --typeStack {}'.format(
            pathtodirectoryRead, savePlot, stack_type)
    else:
        command_Plot = 'python /home/david.perez/cia/ScriptoRun/RunPlot.py --fileDirectory {} --saveDirectory {}'.format(
            pathtodirectoryRead, savePlot, stack_type)

    # from ini file!! nEvents and nCPU
    os.system(command_Plot)
    print(time_init)
    print(str(datetime.datetime.now()))

if __name__ == '__main__':
    main()
