__author__ = 'david.perez.gonzalez'
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

import logging
import logging.config

# class imports
from CalibPVSpectrum import CalibPV

def main():
    """
    Runs the checks on the cluster, plot the results and save them into a file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--finalEvent', dest='finalEvent', help='Specifiy the last event  \
                                             (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')
    parser.add_argument('--typeStack', dest='typeStack', help='Specifiy if the stack is  \
                                                                         "_cal" or "_coinc".',
                        default='')
    args = parser.parse_args()

    final_event, pathtodirectoryRead, stack_type = int(args.finalEvent), args.fileDirect, args.typeStack
    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    start = clock()
    # Events_list = ["Events_with_all", "Events_100_111_010", "Events_000_010_100", "Events_100_111_000", "Events_010_111_000", "Events_010_100", "Events_010_111", "Events_100_111", "Events_000_111", "Events_000_010", "Events_000_100", "Events_000", "Events_100", "Events_010", "Events_111"]


    # pathtodirectoryRead =
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

    C_Calib = CalibPV(final_event, pathtodirectoryRead, stack_type)
    C_Calib.RunCalibPV()

    logging.info('Thanks for using our software. Hope to see you soon. ## (in Check_main)\n')


if __name__ == '__main__':
    print(str(datetime.datetime.now()))
    main()
    print(str(datetime.datetime.now()))