# -*- coding: utf-8 -*-
__author__ = 'david.perez.gonzalez'
"""
NewHypmed_main.py provides a frame to run 'NewHypmed.py'.
"""

#module imports
import argparse
import logging
import logging.config
import cPickle as pickle
import numpy as np
import os
import datetime

#class imports
from NewHypmed import Hypmed

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

    Hyp = Hypmed(pathtodirectoryRead)
    Hyp.runHypmed()

    logging.info('Thanks for using our software. Hope to see you soon. ## (in NewHypmed_main)\n')


if __name__ == '__main__':
    print(str(datetime.datetime.now()))
    main()
    print(str(datetime.datetime.now()))