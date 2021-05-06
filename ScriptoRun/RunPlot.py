import os
import argparse
import psutil
import cPickle as pickle
import datetime

def checkFolder(pathDirectory):
    CHECK_FOLDER = os.path.isdir(pathDirectory)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathDirectory)
        print("created folder : ", pathDirectory)

def main():
    time_init = str(datetime.datetime.now())
    parser = argparse.ArgumentParser()
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                     directory where to read the files from')
    parser.add_argument('--saveDirectory', dest='SavePlot', help='Specifiy the name of the   \
                                                                 directory where to save the files in.', default='None')
    args = parser.parse_args()
    pathtodirectoryRead, savePlot = args.fileDirect, args.SavePlot

    command_AE = 'python /home/david.perez/cia/Tools/AssignEvents.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectoryRead, savePlot)
    # from ini file!! nEvents and nCPU
    os.system(command_AE)

    command_SE = 'python /home/david.perez/cia/Tools/Statistic_Events.py --fileDirectory {} --saveDirectory {}'.format(
        pathtodirectoryRead, savePlot)
    # from ini file!! nEvents and nCPU
    os.system(command_SE)

    command_CM = 'python /home/david.perez/cia/EneRes/CrystalMap-ERes-Mean.py --fileDirectory {} --saveDirectory {} --auto On'.format(
        pathtodirectoryRead, savePlot)
    # from ini file!! nEvents and nCPU
    os.system(command_CM)

    command_PEC = 'python /home/david.perez/cia/Tools/PlotEventCrystal.py --fileDirectory {} --saveDirectory {} --auto On'.format(
        pathtodirectoryRead, savePlot)
    # from ini file!! nEvents and nCPU
    os.system(command_PEC)

    print(time_init)
    print(str(datetime.datetime.now()))

if __name__ == '__main__':
    main()
