# import sys
# sys.path.insert(1, 'C:\\Users\\David\\Google Drive\\RWTHDrive\\MasterThesis\\Programs\\ClassificationCluster')
#
# from CheckClusters_main import *
import os
import argparse
import psutil
import cPickle as pickle
import datetime

def write_commands(jobs, pathtodirectory):
    list_commands = []
    for j in jobs:
        command = 'python' + ' ' + 'LUT.py' + ' --HVD {} --fileDirectory {}'.format(j, pathtodirectory) #/home/david.perez/newEnv/Tenerife/gitFolder/monocal/Positioning/
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

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    parser.add_argument('--HVD N', dest='HVD', help='Specifiy the HVD algorithm to show  \
                                                     (N where N= 0 (=000), 1 (=100), 2 (=010), 3 (=111) or -1 for ALL)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')

    args = parser.parse_args()
    selected_HVD, pathtodirectory = int(args.HVD), args.fileDirect

    command_PeakF = 'python Peak_main.py --fileDirectory {} --HVD -1'.format(pathtodirectory)
    os.system(command_PeakF)

    command_SanCheck = 'python SanCheck_main.py --fileDirectory {} --HVD -1'.format(pathtodirectory)
    os.system(command_SanCheck)

    pathtodirectoryReadLUD = 'dic-LUD/'

    CHECK_FOLDER = os.path.isdir(pathtodirectory + pathtodirectoryReadLUD)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectory + pathtodirectoryReadLUD)
        print("created folder : ", pathtodirectory + pathtodirectoryReadLUD)

    if selected_HVD == -1:
        jobs = range(4) # we take all HVD algorithms, if one wants only want: 0 (=000), 1 (=100), 2 (=010), 3 (=111)
    else:
        jobs = [selected_HVD]

    list_commands = write_commands(jobs, pathtodirectory)

    fCommand = create_finalCommand(list_commands)

    fCommand = fCommand  + ' & wait'

    os.system(fCommand)  # LUT

    command_CheckC = 'python RunCheckParallel.py --fileDirectory {} --nCPU 48 --nEvents 95000000'.format(pathtodirectory)
    os.system(command_CheckC)

if __name__ == '__main__':
    main()

#os.system('python' + ' ' + '/home/david.perez/newEnv/Tenerife/gitFolder/monocal/Positioning/LUT.py')

# os.system('python' + ' ' + '/home/david.perez/newEnv/Tenerife/gitFolder/monocal/Positioning/CheckClusters_main.py')
#
# os.system('python' + ' ' + '/home/david.perez/TestRoot/FitEnergySpectrumRunAll.py')
#
# os.system('python' + ' ' + '/home/david.perez/TestRoot/CalibPVSpectrum.py')
#
# os.system('python' + ' ' + '/home/david.perez/TestRoot/CalibPVLoadandPlot.py')