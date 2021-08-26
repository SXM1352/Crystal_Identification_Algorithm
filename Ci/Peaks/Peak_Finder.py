__author__ = "david.perez.gonzalez" 
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  7 13:19:47 2020
@author: David
"""
#--------Import modules-------------------------
import numpy as np
import array
import ROOT as r
import logging

#class imports
from Peak_Helper import PeakHelper

class PeakFinder(object):            
    def __init__(self, cg, hist,bins,sigma,threshold,rmBackground,convIter,markov,mIter):
        """!
        Constructor of PeakFinder class. The PeakFinder class is used to 
        find peaks on the flood maps provided by HitAnalysis.
        Those peaks are then ordered and classified by rows.
    
        @param cg: indicate which cog algorithm is used
        @type cg: integer
        @param hist: containing the corresponding flood map
        @type cg: histogram
        @param bins = indicate the number of bins used in the histograms [100 #same forall]
        @type bins: integer
        @param sigma = indicate the accepted sigma to find peaks [3.3 works for 000,1.5 works fine for 111 and 100, 2.5 for 010]
        @type sigma: float
        @param threshold = indicate the accepted threshold to find peaks [2 works for 000,4 in 111 for all and 6 for most(same for 010), 7 for 100]
        @type threshold: float
        @param rmBackground = indicate whether the threshold is removed or not [True #forall]
        @type rmBackground: boolean
        @param convIter = indicate how many time the convolution is applied [200 #forall with more tends to reagroup peaks and with less some are missing]
        @type convIter: integer
        @param markov = indicate whether a smoothing function is applied [False #forall smoothing function to remark peaks, but it does not work for us, peaks with diffreent heights and sigmas]
        @type markov: boolean
        @param mIter = indicate iterations of markov function [3 #forall no interest marov is false]
        @type mIter: integer
        """
        self.cg = cg
        self.hist = hist
        self.bins = bins
        self.sigma = sigma
        self.threshold = threshold
        self.rmBackground = rmBackground
        self.convIter = convIter
        self.markov = markov
        self.mIter = mIter

    def __new_numpy1d_with_pointer(self, size):
        """
        Creates arrays compatible with c++ to be used in ROOT
        Input parameters: \
        @param size: indicates how large the array should be
        @type size: int
        
        @return: np_a, pointer
        @rtype: arr, pointer
        """
        np_a = np.zeros( size, dtype=np.float64 )
        pointer, read_only_flag = np_a.__array_interface__["data"]
        return np_a, pointer
    
    def __getPeaksR(self):
        """!
        Looks for the peaks present in the flood maps using 
        a routine created by ROOT (SearchHighRes).

        @return: xycoord_arr with peak coordinates
        @rtype: array
        """
        binsx = self.bins
        binsy = self.bins
        source1, c_source = {}, array.array( "L", [0]*binsx )
        dest1, c_dest = {}, array.array( "L", [0]*binsx )
        
        for i in xrange(binsx):
            source1[i], c_source[i] = self.__new_numpy1d_with_pointer(binsy)
            dest1[i], c_dest[i] = self.__new_numpy1d_with_pointer(binsy)
        
        for j in range(1,binsx):
            for k in range(1,binsy):
                source1[j][k] = self.hist[0][j-1][k-1]
        spectrum = r.TSpectrum2(300) #we need to set the maximum amount of peaks it can find!!!!!
        npeaks = spectrum.SearchHighRes(c_source, c_dest, binsx, binsy, self.sigma, self.threshold, self.rmBackground, self.convIter, self.markov, self.mIter) #sigma,thrs,bckg, thrs to 4 if we want all peaks in 111, sonst 6 for 111, 7 for 100
        
        posx = spectrum.GetPositionX()
        posy = spectrum.GetPositionY()
        xycoord_arr = []
        # print(npeaks)
        for kl in range(npeaks):
            xcoord = self.hist[1][int(posx[kl])]
            ycoord = self.hist[2][int(posy[kl])]
            xycoord_arr.append([xcoord,ycoord])
        # print("Peaks are: ", xycoord_arr)
        return xycoord_arr

    def __closest(self, cur_pos, positions): 
        """!
        Find the closest poisition to the point given from a list
        Input parameters: \
        
        @param cur_pos: coordinates of point to compare with
        @type cur_pos: list
        @param positions: point candidates to be close
        @type positions: list
        
        @return: closest_pos with coordinates of closest peak
        @rtype: list
        """
        low_dist = float('inf')
        closest_pos = None
        for pos in positions:
            dist = PeakHelper.euqli_dist(cur_pos,pos)
            if dist < low_dist:
                low_dist = dist
                closest_pos = pos
        return closest_pos
    
    def closest_to_cent(self, dic_rows, Centers, roi):
        """!
        Function used in Peak_main.py
        Select the peak which is closest to the center peak given
        Input parameters: \
        
        @param dic_rows: rows from corresponding roi
        @type dic_rows: dict
        @param Centers: reference centers of corresponding roi
        @type Centers: dict
        @param roi: indicate which region of interest is used
        @type roi: integer
        
        @return: closest_pos with coordinates of closest peak, roi
        @rtype: list, integer
        """
        low_dist = float('inf')
        closest_pos = None
        for cc in dic_rows.keys():
            for pos in dic_rows[cc][0]:
                dist = PeakHelper.euqli_dist(Centers[roi],pos)
                if dist < low_dist:
                    low_dist = dist
                    closest_pos = pos
        return closest_pos, roi
    
    def __closest_y(self, positions): 
        """!
        Find all the peaks which are the closest to the initial one regarding the "y" coordinate
        Input parameters: \
        @param positions: peaks to check
        @type positions: list

        @return: dic_rows with rows from corresponding roi, positions with peaks not able to be assigned
        @rtype: dict, list
        """
        #low_dist = float('inf')
        if self.cg == 0:
            low_dist = 0.15
        elif self.cg == 2:
            low_dist = 0.1
        elif self.cg == 1 or self.cg == 3:
            low_dist = 0.2 #0.15 works fine with 000 and 100, but adapt to others (0.2 works for 010 and 111?)
        rows = []
        dic_rows = {}

        for ri in np.arange(20): #15 out of all to reduce time (maximum 15 rows) from those that are closer comparing only "y"
            row = []
            diff_list = []
            try:
                cur_pos = self.__closest((min(positions)[0],max([item[1] for item in positions])+1),positions) #we weight the y-value more than x-value
                row.append(cur_pos)
                for indx in np.where(np.array(positions)==cur_pos)[0]: #to check that we have x AND y the same (always together)
                    # using sum() + list comprehension 
                    # checking occurrences of K atleast N times  
                    if sum([1 for i in np.where(np.array(positions)==cur_pos)[0] if i == indx]) == 2:
                        positions.pop(indx) 
            except ValueError:
                pass
                ## print("Positions is empty or if it is not running fine, check for problem.")
            #calculate averaged dist in x,y to have a checker for the row and a possible interpolation in case of missing point
            """with 000 and 010 15 is enough, with 100 we need 20"""
            if self.cg == 0 or self.cg == 1:
                positionsV = sorted(positions[0:15], key=lambda x:x[0], reverse=False) #order by x the first 15 taken to avoid overtaking from other rows, careful with reverse true or false depending on sign
            elif self.cg == 3 or self.cg == 2:
                positionsV = sorted(positions[0:20], key=lambda x:x[0], reverse=False) #order by x the first 20 taken to avoid overtaking from other rows, careful with reverse true or false depending on sign
            for pos in positionsV: #20 or 15 out of all to reduce time (maximum 20 peaks per row)
                if not np.sign(cur_pos[1]) == np.sign(pos[1]):
                    dist = abs(cur_pos[1])+abs(pos[1])
                else:
                    dist = abs(cur_pos[1]-pos[1])
                if dist < low_dist and cur_pos[0] != pos[0]:
                    cur_pos = pos #to modify the limits while changing the position instead of a single horizontal band 
                    ## print(np.where(np.array(positions)==pos)) #it says where x OR y are the same
                    stop = False
                    for indx in np.where(np.array(positions)==pos)[0]: #to check that we have x AND y the same (always together)
                        if not stop:
                            st = 0 #new variable to check for x and y
                            for i in np.where(np.array(positions)==pos)[0]:
                                if i == indx:
                                    st += 1
                            if st == 2:
                                stop = True #x and y are from the same object
                                positions.pop(indx)
                        else:
                            pass
                    row.append(pos)
            row_sort = sorted(row, reverse=False)
            rows.append(row_sort)

            x_row = PeakHelper.Extract_x(row_sort)

            diff_list = np.diff(x_row) #diff between all elements next to each other, except themselves
            if row:
                dic_rows[ri] = [row_sort,diff_list]
    #sanity check to order the rows based on y in case some are mixed due to cur_pos
        check = [] 
        for ch in range(len(dic_rows.keys())):
            check.append([dic_rows[ch][0][0][1],dic_rows[ch][0][0][0]]) #we exchange the x and y only for the use of sorted(easier)
        check_sorted = sorted(check, reverse=True)
        new_dic_rows = {}
        if check == check_sorted:
            pass
        else:
            for j_dd in dic_rows.keys():
                for en_dd,i_dd in enumerate(check_sorted):
                    if dic_rows[j_dd][0][0][1] == i_dd[0] and dic_rows[j_dd][0][0][0] == i_dd[1]:
                        new_dic_rows[en_dd] = dic_rows[j_dd]  
        if new_dic_rows:
            dic_rows = new_dic_rows 
            
        return dic_rows, positions
    
    def runPeakFinder(self): 
        """!
        The main function to run the peak finder and obtain the rows
        Input parameters: \

        @return: dic_rows with rows from corresponding roi
        @rtype: dict
        """
        list1 = self.__getPeaksR() #sigma,thrs,bckg, thrs to 4 if we want all peaks in 111, sonst 6 for 111, 7 for 100
    
        list1 = np.round(list1,6).tolist() #6 is good because is the rounding for the normal numbers (without decimals from approx.
        list1 = sorted(list1, key=lambda x:x[1], reverse=True) #sorted according to "y"
    
        dic_rows,positionss = self.__closest_y(list1)
        # print(positionss)
        
        return dic_rows