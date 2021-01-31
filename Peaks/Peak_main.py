# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:58:11 2021

@author: David
"""

#module imports
import argparse
import logging
import logging.config
import pickle
import numpy as np

#class imports
from Peak_Labels import PeakLabels
from Peak_Finder import PeakFinder
from Peak_Plot import PeakPlot
from Peak_Helper import PeakHelper

#-------------Main---------------------------------
def main():
    # we can use a argparser for the values we use, this temporary
    n_p = 30 #number of pickles
    #hist0 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist0_{}.pickle'.format(p), 'rb')) for p in range(n_p)]    
    #hist0 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist0_6.pickle'))]
    hist0 = False
    
    hist01 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist01_{}.pickle'.format(p), 'rb')) for p in range(n_p)]    
    #hist01 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist01_23.pickle', 'rb'))]
    #hist01 = False
    
    #☻hist10 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist10_{}.pickle'.format(p), 'rb')) for p in range(n_p)]    
    #hist10 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist10_8.pickle', 'rb'))]
    hist10 = False
    
    #hist1 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist1_{}.pickle'.format(p), 'rb')) for p in range(n_p)]    
    #hist1 = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist1_3.pickle', 'rb'))]
    hist1 = False
   
    x_arr = []
    y_arr = []
    rows, dic_crystal = PeakHelper.CrystalDict()
    Centers_COG, dic_c = PeakHelper.ref_peaks()
    dic_palone = {}
    dic_rdefect = {}
    
    #order is important
    hist = [hist0, hist01, hist10, hist1] #CAREFUL WITH ORDER, it changes thresholds and more
    
    # we can use a file to store the values we use, this temporary
    bins = 100 #same forall
    sigma = [3.3, 2.5, 1.5, 1.5] #3.3 works for 000,1.5 works fine for 111 and 100, 2.5 for 010
    threshold = [2, 6, 7, 4]  #2 works for 000,4 in 111 for all and 6 for most(same for 010), 7 for 100,
    rmBackground = True #forall
    convIter = 200 #forall with more tends to reagroup peaks and with less some are missing
    markov = False #forall smoothing function to remark peaks, but works for us, peaks with diffreent heights and sigmas
    mIter = 3
    
    
    
    for cg, ht in enumerate(hist):
        if ht:
            # we can use a file to store the values we use, this temporary
            if cg == 0: #cog000
                rows_accepted = 2 # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
                dop_columns_accepted = 3 # (3 for 100)(2 for 000 and 010) same
                len_columns_accepted = 2 # (3 for 100)(2 for 000 and 010) same      -1 when in the middle   
                dop_min_cent = 5  #before 7 and 14(010)/7,15 for 000 and 100
                dop_max_cent = 15
                lenmin_cent = 3
                lenmax_cent = 11 #before 11(000), 8(010), 9(100)
            elif cg == 1: #010
                rows_accepted = 6 # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
                dop_columns_accepted = 2 # (3 for 100)(2 for 000 and 010) same
                len_columns_accepted = 2 # (3 for 100)(2 for 000 and 010) same     -1 when in the middle 
                dop_min_cent = 5  #before 7 and 14(010)/7,15 for 000 and 100
                dop_max_cent = 14
                lenmin_cent = 2
                lenmax_cent = 8 #before 11(000), 8(010), 9(100)
            elif cg == 2: #100
                rows_accepted = 2 # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
                dop_columns_accepted = 6 # (3 for 100)(2 for 000 and 010) same
                len_columns_accepted = 3 # (3 for 100)(2 for 000 and 010) same     -1 when in the middle    
                dop_min_cent = 7  #before 7 and 14(010)/7,15 for 000 and 100
                dop_max_cent = 15
                lenmin_cent = 3
                lenmax_cent = 8 #before 11(000), 8(010), 9(100)
            elif cg == 3: #cog111
                rows_accepted = 7 # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
                dop_columns_accepted = 7 # (3 for 100)(2 for 000 and 010) same
                len_columns_accepted = 4 # (3 for 100)(2 for 000 and 010) same    -1 when in the middle    
                dop_min_cent = 5  #before 7 and 14(010)/7,15 for 000 and 100
                dop_max_cent = 15
                lenmin_cent = 3
                lenmax_cent = 11 #before 11(000), 8(010), 9(100)
            
            dop_columns_accepted_edge = 2
            
            dop_min_edge = 5 #always
            dop_max_edge = 9 #always
        
            lenmin_edge = 1 #always
            lenmax_edge = 5 #always
            
            for jr,roi_hist in enumerate(ht):
                pFinder = PeakFinder(cg, roi_hist, bins,sigma[cg],threshold[cg],rmBackground,convIter,markov,mIter)
                dic_rows = pFinder.runPeakFinder() #steps[cg], cg) #100 for 111; in principle also for 100; 010 needs 50 (or less); and 000 auch 
                #jr = 23 #in  case we want to see only one
                    
                pclosest, c_roi = pFinder.closest_to_cent(dic_rows, Centers_COG[cg], jr)
                print("pclosest is: ",pclosest)
                pLabels = PeakLabels(cg, pclosest, c_roi, rows, dop_columns_accepted_edge, dop_min_edge, dop_max_edge, lenmin_edge, lenmax_edge, rows_accepted, dop_columns_accepted, len_columns_accepted, dop_min_cent, dop_max_cent, lenmin_cent, lenmax_cent)
                dic_crystal, dic_palone, dic_rdefect = pLabels.label(dic_palone, dic_rdefect, dic_crystal, dic_rows, dic_c[cg]) #auch global!!!
                        
                print("palone",dic_palone)
                print("rdefect", dic_rdefect)


                for ij in dic_rows.keys():
                    x = np.array(PeakHelper.Extract_x(dic_rows[ij][0]))
                    y = np.array(PeakHelper.Extract_y(dic_rows[ij][0]))
                    x_arr.append(x)
                    y_arr.append(y)

                #pPlot = PeakPlot(x_arr, y_arr, jr)
                #pPlot.runPeakPlot()
#                for ji in peaks_alone:
#                    
#                    
#                    for ij in ji:
#                        x = ij[0]
#                        y = ij[1]
#                        x_arr.append(x)
#                        y_arr.append(y)

    
    with open('/home/david.perez/Desktop/dic-crystal-010.pickle', 'wb') as handle:
        pickle.dump(dic_crystal, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    with open('/home/david.perez/Desktop/dic_pAlone-010.pickle', 'wb') as handle:
        pickle.dump(dic_palone, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
        
    with open('/home/david.perez/Desktop/dic_rDefect-010.pickle', 'wb') as handle:
        pickle.dump(dic_rdefect, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #plt.savefig('/home/david.perez/Desktop/Peaksall010.png')
#    runn(hist01, 100)
#    runn(hist1, 80)
#    runn(hist10, 25)
if __name__=='__main__':
    main()