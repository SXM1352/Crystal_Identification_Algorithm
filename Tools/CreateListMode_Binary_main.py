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
from CreateListMode_Binary import ListModeC

def main():
    """
    Runs the checks on the cluster, plot the results and save them into a file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--stackidA_cal', dest='stack_idA', help='Specifiy id of cal stack', default='6')
    parser.add_argument('--stackidB_coinc', dest='stack_idB', help='Specifiy id of coinc stack', default='8')

    parser.add_argument('--moduleidA_cal', dest='module_idA', help='Specifiy id of cal module', default='1')
    parser.add_argument('--moduleidB_coinc', dest='module_idB', help='Specifiy id of coinc module', default='1')

    parser.add_argument('--loglikeA_cal', dest='loglikeA', help='Specifiy loglikeA (not used)', default='0')
    parser.add_argument('--loglikeB_coinc', dest='loglikeB', help='Specifiy loglikeB (not used)', default='0')

    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')
    # parser.add_argument('--typeStack', dest='typeStack', help='Specifiy if the stack is  \
    #                                                                      "_cal" or "_coinc".',
    #                     default='')
    args = parser.parse_args()

    pathtodirectoryRead, stack_idA, stack_idB, module_idA, module_idB, loglikeA, loglikeB = args.fileDirect, args.stack_idA, args.stack_idB, args.module_idA, args.module_idB, args.loglikeA, args.loglikeB
    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    start = clock()

    C_ListMode = ListModeC(pathtodirectoryRead, stack_idA, stack_idB, module_idA, module_idB, loglikeA, loglikeB)
    C_ListMode.run_CreateListMode()

    logging.info('Thanks for using our software. Hope to see you soon. ## (in Check_main)\n')


if __name__ == '__main__':
    print(str(datetime.datetime.now()))
    main()
    print(str(datetime.datetime.now()))