__author__ = 'david.perez.gonzalez'
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:07:20 2021

@author: David
"""

#module imports
import cPickle as pickle
import numpy as np
import atexit
from time import clock
import time
import h5py

import logging
import logging.config

#class imports
from CheckClusters import C_Cluster

def main(): 
    """
    Runs the checks on the cluster, plot the results and save them into a file
    """

    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')   
    # we can use an argparser for the values we use, this is temporary
    line = "="*40
    start = clock()
    #Events_list = ["Events_with_all", "Events_100_111_010", "Events_000_010_100", "Events_100_111_000", "Events_010_111_000", "Events_010_100", "Events_010_111", "Events_100_111", "Events_000_111", "Events_000_010", "Events_000_100", "Events_000", "Events_100", "Events_010", "Events_111"]
    dic_Events = {}
    dic_Events["ALL"] = {"000":True, "100":True, "010":True, "111":True}
    
    dic_Events["three_100_111_010"] = {"000":False, "100":True, "010":True, "111":True}
    dic_Events["three_000_010_100"] = {"000":True, "100":True, "010":True, "111":False}
    dic_Events["three_100_111_000"] = {"000":True, "100":True, "010":False, "111":True}
    dic_Events["three_010_111_000"] = {"000":True, "100":False, "010":True, "111":True}
    
    dic_Events["two_010_100"] = {"000":False, "100":True, "010":True, "111":False}
    dic_Events["two_010_111"] = {"000":False, "100":False, "010":True, "111":True}
    dic_Events["two_100_111"] = {"000":False, "100":True, "010":False, "111":True}
    dic_Events["two_000_111"] = {"000":True, "100":False, "010":False, "111":True}
    dic_Events["two_000_010"] = {"000":True, "100":False, "010":True, "111":False}
    dic_Events["two_000_100"] = {"000":True, "100":True, "010":False, "111":False}
    
    dic_Events["QF_000"] = {"000":True, "100":False, "010":False, "111":False}
    dic_Events["QF_100"] = {"000":False, "100":True, "010":False, "111":False}
    dic_Events["QF_010"] = {"000":False, "100":False, "010":True, "111":False}
    dic_Events["QF_111"] = {"000":False, "100":False, "010":False, "111":True}
    
    dic_Events["None"] = {"000":False, "100":False, "010":False, "111":False}
    
    Check_Cluster = C_Cluster(line, start, dic_Events)
    Check_Cluster.runCluster()

        
    logging.info('Thanks for using our software. Hope to see you soon. ## (in Peak_main)\n')

if __name__=='__main__':
    main()