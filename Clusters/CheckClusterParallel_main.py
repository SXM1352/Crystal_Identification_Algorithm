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
from CheckClusterParallel import C_Cluster


def __CrystalDict_AssignEvents():
    """!
    Define Crystal identification dictionary with respective ids for all the peaks
    based on the different layers

    @return: rows =  ids of crystal ordered by row and column,
        dic_crystal_test = id from crystals
    @rtype: 2D-arr, dict
    """
    m = 1
    row = []
    j = 0
    p = 0
    rows = []
    dic_crystal_test = {}
    for i in range(3426):
        if i >= (65 * m + 31 * p) and j % 2 == 0:
            rows.append(row)
            # s = 1
            for n, r in enumerate(row):
                if n == 0 or n == 64:
                    peakii = {
                        'row': j,
                        'layer': 1,
                        'id': r,
                        'n_events': 0
                    }
                    dic_crystal_test[r] = peakii
                else:
                    if n % 2 != 0:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'n_events': 0
                        }
                        dic_crystal_test[r] = peakii
                    else:
                        peakjj = {
                            'row': j,
                            'layer': 2,
                            'id': r,
                            'n_events': 0
                        }
                        dic_crystal_test[r] = peakjj

            row = []
            j += 1
            p += 1

        elif i >= (65 * m + 31 * p) and j % 2 != 0:
            row_neg = [-1] * len(row)
            new_row = list(itertools.chain(*zip(row_neg, row)))
            new_row.append(-1)
            new_row.append(-1)
            new_row.insert(0, -1)

            rows.append(new_row)
            for r in row:
                peakkk = {
                    'row': j,
                    'layer': 3,
                    'id': r,
                    'n_events': 0
                }
                dic_crystal_test[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)

    return dic_crystal_test


def main():
    """
    Runs the checks on the cluster, plot the results and save them into a file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--initEvent', dest='initEvent', help='Specifiy the first event  \
                                         (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--finalEvent', dest='finalEvent', help='Specifiy the last event  \
                                             (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')
    args = parser.parse_args()

    init_event, final_event, pathtodirectoryRead = int(args.initEvent), int(args.finalEvent), args.fileDirect
    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    start = clock()
    # Events_list = ["Events_with_all", "Events_100_111_010", "Events_000_010_100", "Events_100_111_000", "Events_010_111_000", "Events_010_100", "Events_010_111", "Events_100_111", "Events_000_111", "Events_000_010", "Events_000_100", "Events_000", "Events_100", "Events_010", "Events_111"]
    dic_Events = {}
    dic_Events["ALL"] = {"000": True, "100": True, "010": True, "111": True}
    dic_Events["three_100_111_010"] = {"000": False, "100": True, "010": True, "111": True}
    dic_Events["three_000_010_100"] = {"000": True, "100": True, "010": True, "111": False}
    dic_Events["three_100_111_000"] = {"000": True, "100": True, "010": False, "111": True}
    dic_Events["three_010_111_000"] = {"000": True, "100": False, "010": True, "111": True}
    dic_Events["two_010_100"] = {"000": False, "100": True, "010": True, "111": False}
    dic_Events["two_010_111"] = {"000": False, "100": False, "010": True, "111": True}
    dic_Events["two_100_111"] = {"000": False, "100": True, "010": False, "111": True}
    dic_Events["two_000_111"] = {"000": True, "100": False, "010": False, "111": True}
    dic_Events["two_000_010"] = {"000": True, "100": False, "010": True, "111": False}
    dic_Events["two_000_100"] = {"000": True, "100": True, "010": False, "111": False}
    dic_Events["000"] = {"000": True, "100": False, "010": False, "111": False}
    dic_Events["100"] = {"000": False, "100": True, "010": False, "111": False}
    dic_Events["010"] = {"000": False, "100": False, "010": True, "111": False}
    dic_Events["111"] = {"000": False, "100": False, "010": False, "111": True}

    dic_Events["None"] = {"000": False, "100": False, "010": False, "111": False}

    dic_AssignE = {}
    dic_AssignE["ALL"] = __CrystalDict_AssignEvents()
    dic_AssignE["three_100_111_010"] = __CrystalDict_AssignEvents()
    dic_AssignE["three_000_010_100"] = __CrystalDict_AssignEvents()
    dic_AssignE["three_100_111_000"] = __CrystalDict_AssignEvents()
    dic_AssignE["three_010_111_000"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_010_100"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_010_111"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_100_111"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_000_111"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_000_010"] = __CrystalDict_AssignEvents()
    dic_AssignE["two_000_100"] = __CrystalDict_AssignEvents()
    dic_AssignE["000_QF"] = __CrystalDict_AssignEvents()
    dic_AssignE["100_QF"] = __CrystalDict_AssignEvents()
    dic_AssignE["010_QF"] = __CrystalDict_AssignEvents()
    dic_AssignE["111_QF"] = __CrystalDict_AssignEvents()
    dic_AssignE["000_ONLY_VALID"] = __CrystalDict_AssignEvents()
    dic_AssignE["100_ONLY_VALID"] = __CrystalDict_AssignEvents()
    dic_AssignE["010_ONLY_VALID"] = __CrystalDict_AssignEvents()
    dic_AssignE["111_ONLY_VALID"] = __CrystalDict_AssignEvents()

    # pathtodirectoryRead =
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

    Check_Cluster = C_Cluster(init_event, final_event,
        start, dic_Events, dic_AssignE, pathtodirectoryRead)
    Check_Cluster.runCluster()

    logging.info('Thanks for using our software. Hope to see you soon. ## (in Check_main)\n')


if __name__ == '__main__':
    print(str(datetime.datetime.now()))
    main()
    print(str(datetime.datetime.now()))
