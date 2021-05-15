import os
import argparse
import psutil
import cPickle as pickle
import datetime

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

def write_commands(jobs, pathtodirectoryRead, decimals):
    list_commands = []
    for j in jobs:
        command = 'python' + ' ' + '/home/david.perez/cia/Clusters/CheckClusterParallel_main.py' + ' --initEvent {} --finalEvent {} --fileDirectory {} --precision {}'.format(j[0], j[1], pathtodirectoryRead, decimals)
        list_commands.append(command)
    return list_commands
def write_commands_calib(jobs, pathtodirectoryRead):
    list_commands = []
    for j in jobs:
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
                                                             e.g.: "0.01" or "0.1".')
    args = parser.parse_args()
    decimals, n_Procs, n_Events, pathtodirectoryRead, savePlot = args.decimals, int(args.nCPU), int(args.nEvents), args.fileDirect, args.SavePlot

    pathtodirectorySaveParallel = 'Parallel/'
    pathtodirectorySavePV = 'PhotonSpectrum/'

    checkFolder(pathtodirectoryRead)

    checkFolder(pathtodirectoryRead + pathtodirectorySaveParallel)

    checkFolder(pathtodirectoryRead + pathtodirectorySavePV)

    n_Procs_total = psutil.cpu_count()
    if n_Procs >= n_Procs_total:
        n_Procs = n_Procs_total - 1

    print('Number of used CPU: ', n_Procs)
    print('Number of available CPU: ', n_Procs_total)

    n_jobs_per_proc = int(n_Events/n_Procs)

    jobs = __chunkify_data(n_Procs, n_jobs_per_proc)
    __save_Jobs(jobs, pathtodirectoryRead + pathtodirectorySaveParallel)

    list_commands = write_commands(jobs, pathtodirectoryRead, decimals)

    fCommand = create_finalCommand(list_commands)

    fCommand = fCommand  + ' & wait'

    print('Final Command:', fCommand)

    os.system(fCommand) #check clusters

    # MAKE COMMAND!!!!
    Group_jobs = C_Group(jobs, pathtodirectoryRead + pathtodirectorySaveParallel, pathtodirectorySavePV) #group pickles
    Group_jobs.runCGroup()

    FitEnSpectrumCommand = 'python' + ' ' + '/home/david.perez/cia/EneRes/FitEnergySpectrumRunAll.py' + ' --fileDirectory {}'.format(pathtodirectoryRead + pathtodirectorySaveParallel + pathtodirectorySavePV) + ' & wait'

    os.system(FitEnSpectrumCommand) #fit crystals

    list_commands_calib = write_commands_calib(jobs, pathtodirectoryRead)

    fCommand_Calib = create_finalCommand(list_commands_calib)

    fCommand_Calib = fCommand_Calib + ' & wait'

    os.system(fCommand_Calib) #calibrate detector

    CalibLoadPlotCommand = 'python' + ' ' + '/home/david.perez/cia/EneRes/CalibPVLoadandPlot_main.py' + ' --fileDirectory {}'.format(pathtodirectoryRead) + ' & wait'
    os.system(CalibLoadPlotCommand)  # plot calib detector

    command_Plot = 'python /home/david.perez/cia/ScriptoRun/RunPlot.py --fileDirectory {} --saveDirectory {} --auto On'.format(
        pathtodirectoryRead + pathtodirectorySaveParallel, savePlot)
    # from ini file!! nEvents and nCPU
    os.system(command_Plot)
    print(time_init)
    print(str(datetime.datetime.now()))

if __name__ == '__main__':
    main()
