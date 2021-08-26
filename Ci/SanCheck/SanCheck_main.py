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
import cPickle as pickle
import numpy as np
import os

#class imports
from Peak_Helper import PeakHelper #it can be included as a package, but from python 3 on it is not needed
from SanCheck_Col import SanCheckCol
from SanCheck_Row import SanCheckRow
from SanCheck_Inv import SanCheckInv
from SanCheck_Plot import SanCheckPlot
"""
SanCheck_main.py provides a frame to run sanity checks on the corresponding
given data (ordered labels of peaks distributed in region of interest) by
looking at the median values of the complete sets of data. 
"""

def dic_HVD_ROI(rows_HVD_ROI, cols_HVD_ROI_12, cols_HVD_ROI_3, dic_checked_ROI, rows):
    dic_HVD_ROI = {}
    index = 0
    for i_n, i in enumerate(rows_HVD_ROI):
        for c_n, c in enumerate(cols_HVD_ROI_3):
            dic_HVD_ROI[index] = {}
            dic_HVD_ROI[index]['rows'] = []
            for j in range(i[0], i[1]):
                dic_HVD_ROI[index]['rows'].append(j)
            dic_HVD_ROI[index]['cols_3'] = []
            for col in range(c[0], c[1]):
                dic_HVD_ROI[index]['cols_3'].append(col)
            index += 1
    index = 0
    for i_n, i in enumerate(rows_HVD_ROI):
        for c_n, c in enumerate(cols_HVD_ROI_12):
            dic_HVD_ROI[index]['cols_12'] = []
            for col in range(c[0], c[1]):
                dic_HVD_ROI[index]['cols_12'].append(col)

            index += 1

    for roi in dic_HVD_ROI.keys():
        for r in dic_HVD_ROI[roi]['rows']:
            if r % 2 == 0:
                for c in dic_HVD_ROI[roi]['cols_12']:
                    dic_checked_ROI[rows[r][c]]['col_12'] = c
                    if 'roi' in dic_checked_ROI[rows[r][c]].keys():
                        dic_checked_ROI[rows[r][c]]['roi'].append(roi)
                    else:
                        dic_checked_ROI[rows[r][c]]['roi'] = []
                        dic_checked_ROI[rows[r][c]]['roi'].append(roi)
            else:
                for c in dic_HVD_ROI[roi]['cols_3']:
                    dic_checked_ROI[rows[r][c]]['col_3'] = c
                    if 'roi' in dic_checked_ROI[rows[r][c]].keys():
                        dic_checked_ROI[rows[r][c]]['roi'].append(roi)
                    else:
                        dic_checked_ROI[rows[r][c]]['roi'] = []
                        dic_checked_ROI[rows[r][c]]['roi'].append(roi)
    return dic_checked_ROI

def read_data_COG(HVD, pathtodirectoryRead):
    """!
    Read data from the three dictionaries containing all the peaks ordered by \
    its extracted condition at first place. \
    Input parameters: \
    @param HVD: it indicates which COG algorithm is used to check
    @type HVD: string 
    
    @return:
    dic_crystal = dictionary containing most of peaks ordered by rows,
    dic_palone = dictionary containing those peaks which did not find a 
    corresponding row, 
    dic_rdefect dictionary containing rows which are considered to be wrongly
    labelled,
    RefHVD_Sections = original flood maps to be plotted with the labelled peaks,
    ludHVD = look-up-table to be plotted with the labelled peaks
    """
    # pathtodirectoryRead = 'C:\\Users\\David\\Google Drive\\RWTHDrive\\MasterThesis\\2021-03-16-Crystal-015\\'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'
    # pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'

    pathtodirectoryLUD = 'dic-LUD/'
    pathtodirectoryRefS = 'RefSections/'

    # pathtodirectoryRefS = '20210315_NEW_RefSections/'
    # pathtodirectoryLUD = '20210315_NEW_dic-LUD/'

    with open('{}dic-crystal-{}.pickle'.format(pathtodirectoryRead, HVD), 'rb') as handle:
        dic_crystal = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        
    with open('{}dic_pAlone-{}.pickle'.format(pathtodirectoryRead, HVD), 'rb') as handle:
        dic_palone = pickle.load(handle) # 000, 100, 010, 111 
    
    with open('{}dic_rDefect-{}.pickle'.format(pathtodirectoryRead, HVD), 'rb') as handle:
        dic_rdefect = pickle.load(handle) # 000, 100, 010, 111

    CHECK_FILE = os.path.isfile('{}Ref{}_Sections.pickle'.format(pathtodirectoryRead + pathtodirectoryRefS, HVD))
    if CHECK_FILE:
        with open('{}Ref{}_Sections.pickle'.format(pathtodirectoryRead + pathtodirectoryRefS, HVD), 'rb') as handle:
            RefHVD_Sections = np.array(pickle.load(handle))
    else:
        RefHVD_Sections = np.array([])

    CHECK_FILE = os.path.isfile('{}dic-LUD-{}.pickle'.format(pathtodirectoryRead + pathtodirectoryLUD, HVD))
    if CHECK_FILE:
        with open('{}dic-LUD-{}.pickle'.format(pathtodirectoryRead + pathtodirectoryLUD, HVD), 'rb') as handle:
            ludHVD = pickle.load(handle) # 000, 100, 010, 111
    else:
        ludHVD = None

    return dic_crystal, dic_palone, dic_rdefect, RefHVD_Sections, ludHVD

def main(): 
    """
    Runs the checks on the data, plot the results and save them into a file
    """
    # logging.config.fileConfig('ini-files/logging.ini')
    # logging.getLogger('cia')

    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    parser = argparse.ArgumentParser()
    parser.add_argument('--HVD N', dest='HVD', help='Specifiy the HVD algorithm to show  \
                                                 (N where N= 0 (=000), 1 (=100), 2 (=010), 3 (=111) or -1 for ALL)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                     directory where to read the files from.')
    parser.add_argument('--saveDirectory', dest='SavePlot', help='Specifiy the name of the   \
                                                         directory where to save the files in.', default='None')
    # parser.add_argument('--plot', dest='plot_active', help='Plot grid of found peaks. 0: Off, 1: On.')
    args = parser.parse_args()

    selected_HVD, pathtodirectoryRead, pathtodirectorySavePlot = int(args.HVD), args.fileDirect, args.SavePlot

    pathtodirectorySave = 'dic-checked/'

    CHECK_FOLDER = os.path.isdir(pathtodirectoryRead + pathtodirectorySave)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathtodirectoryRead + pathtodirectorySave)
        # print("created folder : ", pathtodirectoryRead + pathtodirectorySave)

    # cols_111_ROI_12 = [[2, 15], [14, 27], [26, 39], [38, 51], [50, 63]]
    # cols_111_ROI_3 = [[0, 7], [6, 13], [12, 19], [18, 25], [24, 31]]
    # rows_111_ROI = [[5, 18], [17, 30], [29, 42], [41, 54], [53, 66]]
    #
    # cols_000_ROI_12 = [[0, 9], [8, 21], [20, 33], [32, 45], [44, 57], [56, 65]]
    # cols_000_ROI_3 = [[0, 4], [3, 10], [9, 16], [15, 22], [21, 28], [27, 31]]
    # rows_000_ROI = [[0, 12], [11, 24], [23, 36], [35, 48], [47, 60], [59, 71]]
    #
    # cols_010_ROI_12 = [[0, 9], [8, 21], [20, 33], [32, 45], [44, 57], [56, 65]]
    # cols_010_ROI_3 = [[0, 4], [3, 10], [9, 16], [15, 22], [21, 28], [27, 31]]
    # rows_010_ROI = [[5, 18], [17, 30], [29, 42], [41, 54], [53, 66]]
    #
    # cols_100_ROI_12 = [[2, 15], [14, 27], [26, 39], [38, 51], [50, 63]]
    # cols_100_ROI_3 = [[0, 7], [6, 13], [12, 19], [18, 25], [24, 31]]
    # rows_100_ROI = [[0, 12], [11, 24], [23, 36], [35, 48], [47, 60], [59, 71]]
    cols_ROI_12 = [[[0, 9], [8, 21], [20, 33], [32, 45], [44, 57], [56, 65]],
                       [[2, 15], [14, 27], [26, 39], [38, 51], [50, 63]],
                       [[0, 9], [8, 21], [20, 33], [32, 45], [44, 57], [56, 65]],
                       [[2, 15], [14, 27], [26, 39], [38, 51], [50, 63]]]

    cols_ROI_3 = [[[0, 4], [3, 10], [9, 16], [15, 22], [21, 28], [27, 31]],
                      [[0, 7], [6, 13], [12, 19], [18, 25], [24, 31]],
                      [[0, 4], [3, 10], [9, 16], [15, 22], [21, 28], [27, 31]],
                      [[0, 7], [6, 13], [12, 19], [18, 25], [24, 31]]]

    rows_ROI = [[[0, 12], [11, 24], [23, 36], [35, 48], [47, 60], [59, 71]],
                    [[0, 12], [11, 24], [23, 36], [35, 48], [47, 60], [59, 71]],
                    [[5, 18], [17, 30], [29, 42], [41, 54], [53, 66]],
                    [[5, 18], [17, 30], [29, 42], [41, 54], [53, 66]]]

    HVD_list = ["000", "100", "010", "111"]
    print("FEHLER?!11111")
    if selected_HVD == -1:
        n_HVD = 4
        fixed_cg = False
    else:
        n_HVD = 1
        fixed_cg = True
    for cg in range(n_HVD):
        if fixed_cg:
            cg = selected_HVD #0 for 000, 1 for 100, 2 for 010, 3 for 111
        HVD = HVD_list[cg]
        rows_HVD_ROI = rows_ROI[cg]
        cols_HVD_ROI_12 = cols_ROI_12[cg]
        cols_HVD_ROI_3 = cols_ROI_3[cg]

        dic_crystal, dic_palone, dic_rdefect, RefHVD_Sections, ludHVD = read_data_COG(HVD, pathtodirectoryRead)
        
        dist_x = [0.15,0.25,0.2,0.3] #range for the interval of accepted peaks for columns in different COG
        
        dist_y = [0.3,0.2,0.4,0.3] #range for the interval of accepted peaks for rows in different COG
        
        dist_min_x = [0.2,0.185,0.2,0.4] #minimum distance between one peak and the corresponding row or column
        dist_min_y = [0.25,0.185,0.3,0.4]
        
        dist_min_xy_list = [0.3,0.35,0.2,0.4]
    
        CheckCol = SanCheckCol(cg, dist_x)
        dic_crystal, m_cols, dic_recheck_col = CheckCol.runSanCheckCol(dic_crystal)
        # print("m_col",m_cols)
        
        CheckRow = SanCheckRow(cg, dist_y)
        dic_crystal, m_rows = CheckRow.runSanCheckRow(dic_crystal)
        # print("m_rows",m_rows)
            
        rows, no_use_dic = PeakHelper.CrystalDict()
        CheckInv = SanCheckInv(dist_min_x, dist_min_y, dist_min_xy_list, m_rows, m_cols, rows, cg)
        dic_crystal, dic_inv = CheckInv.runSanCheckInv(dic_crystal, dic_palone, dic_rdefect, dic_recheck_col)
    
            
        onlyCheckCol = SanCheckCol(cg, dist_x)
        m_cols_def = onlyCheckCol.runCheckCol(dic_crystal)
        # print("m_col_def",m_cols_def)

        onlyCheckRow = SanCheckRow(cg, dist_y)
        m_rows_def = onlyCheckRow.runCheckRow(dic_crystal)

        # print("m_rows_def",m_rows_def)

        CheckInv_def = SanCheckInv(dist_min_x, dist_min_y, dist_min_xy_list, m_rows_def, m_cols_def, rows, cg)
        dic_crystal, dic_inv = CheckInv_def.check_def(dic_crystal, dic_inv)

        dic_crystal_ROI = dic_HVD_ROI(rows_HVD_ROI, cols_HVD_ROI_12, cols_HVD_ROI_3, dic_crystal, rows)
        
        CheckPlot = SanCheckPlot(cg, RefHVD_Sections, ludHVD, dist_min_x, dist_min_y, HVD, pathtodirectorySavePlot)
        dic_crystal_f = CheckPlot.runSanCheckPlot(dic_crystal_ROI, m_cols_def, dic_inv)
        print("BUUUUMSSS11111111111")
        #Extract result
        with open('{}dic-crystal-{}-checked.pickle'.format(pathtodirectoryRead + pathtodirectorySave, HVD), 'wb') as handle:
            pickle.dump(dic_crystal_f, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
        print("BUUUUUUMSSSSS222222222222")
        logging.info('Dictionary containing checked labels of peaks saved in ' + pathtodirectoryRead + pathtodirectorySave + '/ \n')
        
    logging.info('Thanks for using our software. Hope to see you soon. ## (in Peak_main)\n')

if __name__=='__main__':
    main()