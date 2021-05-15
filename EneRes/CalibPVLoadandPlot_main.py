# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:07:20 2021

@author: David
"""

# module imports
from time import clock
import datetime

import argparse
import itertools
import cPickle as pickle

import logging
import logging.config

# class imports
from CalibPVLoadandPlot import CalibLoadPlot

def main():
    """
    Runs the checks on the cluster, plot the results and save them into a file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')
    args = parser.parse_args()

    pathtodirectoryRead = args.fileDirect
    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    start = clock()
    # Events_list = ["Events_with_all", "Events_100_111_010", "Events_000_010_100", "Events_100_111_000", "Events_010_111_000", "Events_010_100", "Events_010_111", "Events_100_111", "Events_000_111", "Events_000_010", "Events_000_100", "Events_000", "Events_100", "Events_010", "Events_111"]

    pathtodirectorySaveParallel = 'Parallel/'
    with open('{}Jobs_list.pickle'.format(pathtodirectoryRead + pathtodirectorySaveParallel),
              'rb') as handle:
        jobs = pickle.load(handle)  # 000, 100, 010, 111

    Plot_Calib = CalibLoadPlot(jobs, pathtodirectoryRead + pathtodirectorySaveParallel)
    Plot_Calib.runCalibLoadPlot()  # create root and txt files from calib

    logging.info('Thanks for using our software. Hope to see you soon. ## (in Check_main)\n')


if __name__ == '__main__':
    print(str(datetime.datetime.now()))
    main()
    print(str(datetime.datetime.now()))