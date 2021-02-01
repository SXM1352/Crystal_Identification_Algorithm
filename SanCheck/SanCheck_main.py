# -*- coding: utf-8 -*-

__author__ = 'david.perez.gonzalez'
"""
Created on Fri Jan 15 19:27:39 2021

@author: David
"""

#module imports
import argparse
import logging
import logging.config
import pickle
import numpy as np

#class imports
from Peak_Helper import PeakHelper
from SanCheck_Col import SanCheckCol
from SanCheck_Row import SanCheckRow
from SanCheck_Inv import SanCheckInv
from SanCheck_Plot import SanCheckPlot

"""
SanCheck_main.py provides a frame to run sanity checks on the corresponding
given data (ordered labels of peaks distributed in region of interest) by
looking at the median values of the complete sets of data. 
"""

def read_data_COG(HVD):
    """
    read data from the three dictionaries containing all the peaks ordered by \
    its extracted condition at first place. \
    Input parameters: \
    HVD = string (it indicates which COG algorithm is used to check)
    
    Returns: \
    dic_crystal = dictionary containing most of peaks ordered by rows
    dic_palone = dictionary containing those peaks which did not find a 
    corresponding row. \
    dic_rdefect dictionary containing rows which are considered to be wrongly
    labelled. \
    RefNVD_Sections = original flood maps to be plotted with the labelled peaks
    ludHVD = look-up-table to be plotted with the labelled peaks
    """
    
    with open('./010/dic-crystal-{}.pickle'.format(HVD), 'rb') as handle:
        dic_crystal = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        
    with open('./010/dic_pAlone-{}.pickle'.format(HVD), 'rb') as handle:
        dic_palone = pickle.load(handle) # 000, 100, 010, 111 
    
    with open('./010/dic_rDefect-{}.pickle'.format(HVD), 'rb') as handle:
        dic_rdefect = pickle.load(handle) # 000, 100, 010, 111
    
    RefHVD_Sections = np.array([])
    
    ludHVD = np.array([])
    
#    with open('dic-LUD-{}.pickle'.format(HVD), 'rb') as handle:
#        ludHVD = pickle.load(handle) # 000, 100, 010, 111
    
#    with open('Ref{}_Sections-together.pickle'.format(HVD), 'rb') as handle:
#        RefNVD_Sections = pickle.load(handle)
        
    return dic_crystal, dic_palone, dic_rdefect, RefHVD_Sections, ludHVD

def main(): 
    """
    Runs the checks on the data, plot the results and save them into a file
    """
    logging.config.fileConfig('ini-files/logging.ini')
    logging.getLogger('cia')    

    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')   
    # we can use an argparser for the values we use, this is temporary
    
    savedir = '.'
            
    for cg in range(1):
        cg = 1 #0 for 000, 1 for 010, 2 for 100, 3 for 111 
        HVD_list = ["000", "010", "100", "111"]
        
        HVD = HVD_list[cg]
        
        dic_crystal, dic_palone, dic_rdefect, RefNVD_Sections, ludHVD = read_data_COG(HVD)
        
        dist_x = [0.2,0.2,0.25,0.3] #range for the interval of accepted peaks for columns in different COG
        
        dist_y = [0.3,0.45,0.2,0.3] #range for the interval of accepted peaks for rows in different COG
        
        dist_min_x = [0.25,0.25,0.185,0.4] #minimum distance between one peak and the corresponding row or column
        dist_min_y = [0.25,0.4,0.185,0.4]
        
        dist_min_xy_list = [0.4,0.4,0.4,0.4]
    
        CheckCol = SanCheckCol(cg, dist_x)
        dic_crystal, m_cols, dic_recheck_col = CheckCol.runSanCheckCol(dic_crystal)
        print("m_col",m_cols)
        
        CheckRow = SanCheckRow(cg, dist_y)
        dic_crystal, m_rows = CheckRow.runSanCheckRow(dic_crystal)
        print("m_rows",m_rows)
            
        rows, no_use_dic = PeakHelper.CrystalDict()
        CheckInv = SanCheckInv(dist_min_x, dist_min_y, dist_min_xy_list, m_rows, m_cols, rows, cg)
        dic_crystal, dic_inv = CheckInv.runSanCheckInv(dic_crystal, dic_palone, dic_rdefect, dic_recheck_col)
    
            
        onlyCheckCol = SanCheckCol(cg, dist_x)
        m_cols_def = onlyCheckCol.runCheckCol(dic_crystal)
        print("m_col_def",m_cols_def)
        
        onlyCheckRow = SanCheckRow(cg, dist_y)
        m_rows_def = onlyCheckRow.runCheckRow(dic_crystal)
        
        print("m_rows_def",m_rows_def)
           
        
        CheckInv_def = SanCheckInv(dist_min_x, dist_min_y, dist_min_xy_list, m_rows_def, m_cols_def, rows, cg)
        dic_crystal, dic_inv = CheckInv_def.check_def(dic_crystal, dic_inv)
        
        CheckPlot = SanCheckPlot(cg, RefNVD_Sections, ludHVD, dist_min_x, dist_min_y)
        dic_crystal_f = CheckPlot.runSanCheckPlot(dic_crystal, m_cols_def, dic_inv)
        
        #Extract result        
#        with open('{}/dic-crystal-{}-checked.pickle'.format(savedir, HVD), 'wb') as handle:
#            pickle.dump(dic_crystal_f, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
#    
        logging.info('Dictionary containing checked labels of peaks saved in ' + savedir + '/ \n')
        
    logging.info('Thanks for using our software. Hope to see you soon. ## (in Peak_main)\n')

if __name__=='__main__':
    main()