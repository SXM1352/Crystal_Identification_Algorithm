import os
import argparse
import psutil
import cPickle as pickle
import datetime

from GroupPickles import C_Group
from CalibPVLoadandPlot import CalibLoadPlot

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

def write_commands(jobs, pathtodirectoryRead):
    list_commands = []
    for j in jobs:
        command = 'python' + ' ' + '/home/david.perez/TestParallel/CheckClusterParallel_main.py' + ' --initEvent {} --finalEvent {} --fileDirectory {}'.format(j[0], j[1], pathtodirectoryRead)
        list_commands.append(command)
    return list_commands
def write_commands_calib(jobs, pathtodirectoryRead):
    list_commands = []
    for j in jobs:
        command = 'python' + ' ' + '/home/david.perez/TestRoot/CalibPVSpectrum_main.py' + ' --finalEvent {} --fileDirectory {}'.format(j[1], pathtodirectoryRead)
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
    parser.add_argument('--nCPU', dest='nCPU', help='Specifiy the number of CPUs to be used  \
                                             (N where N=1,2,...)')
    parser.add_argument('--nEvents', dest='nEvents', help='Specifiy the number of events  \
                                                 (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                     directory where to read the files from')

    args = parser.parse_args()
    n_Procs, n_Events, pathtodirectoryRead = int(args.nCPU), int(args.nEvents), args.fileDirect
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'# + 'Parallel/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'# + 'Parallel/'

    pathtodirectorySaveParallel = 'Parallel/'
    pathtodirectorySavePV = 'PhotonSpectrum/'

    # pathtodirectoryReadLUD = 'dic-LUD/'
    # pathtodirectoryReadHDF5 = 'hdf5Data/'
    # pathtodirectoryCheck = 'dic-checked/'

    CHECK_FOLDER = os.path.isdir(pathtodirectoryRead)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectoryRead)
        print("created folder : ", pathtodirectoryRead)

    CHECK_FOLDER = os.path.isdir(pathtodirectoryRead + pathtodirectorySaveParallel)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectoryRead + pathtodirectorySaveParallel)
        print("created folder : ", pathtodirectoryRead + pathtodirectorySaveParallel)

    CHECK_FOLDER = os.path.isdir(pathtodirectoryRead + pathtodirectorySavePV)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectoryRead + pathtodirectorySavePV)
        print("created folder : ", pathtodirectoryRead + pathtodirectorySavePV)


    n_Procs_total = psutil.cpu_count()
    if n_Procs >= n_Procs_total:
        n_Procs = n_Procs_total - 1

    print('Number of used CPU: ', n_Procs)
    print('Number of available CPU: ', n_Procs_total)

    n_jobs_per_proc = int(n_Events/n_Procs)

    jobs = __chunkify_data(n_Procs, n_jobs_per_proc)
    __save_Jobs(jobs, pathtodirectoryRead + pathtodirectorySaveParallel)

    list_commands = write_commands(jobs, pathtodirectoryRead)

    fCommand = create_finalCommand(list_commands)

    fCommand = fCommand  + ' & wait'

    print('Final Command:', fCommand)

    os.system(fCommand) #check clusters

    Group_jobs = C_Group(jobs, pathtodirectoryRead + pathtodirectorySaveParallel, pathtodirectorySavePV) #group pickles
    Group_jobs.runCGroup()

    FitEnSpectrumCommand = 'python' + ' ' + '/home/david.perez/TestRoot/FitEnergySpectrumRunAll.py' + ' --fileDirectory {}'.format(pathtodirectoryRead + pathtodirectorySaveParallel + pathtodirectorySavePV) + ' & wait'

    os.system(FitEnSpectrumCommand) #fit crystals

    list_commands_calib = write_commands_calib(jobs, pathtodirectoryRead)

    fCommand_Calib = create_finalCommand(list_commands_calib)

    fCommand_Calib = fCommand_Calib + ' & wait'

    os.system(fCommand_Calib) #calibrate detector

    Plot_Calib = CalibLoadPlot(jobs, pathtodirectoryRead + pathtodirectorySaveParallel)
    Plot_Calib.runCalibLoadPlot() #create root and txt files from calib

    print(time_init)
    print(str(datetime.datetime.now()))

if __name__ == '__main__':
    main()
