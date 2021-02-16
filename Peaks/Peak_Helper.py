__author__ = "david.perez.gonzalez" 
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:52:04 2021

@author: David
"""
import logging
import numpy as np

class PeakHelper(object):
    def __init__(self):
        pass
    
    @staticmethod 
    def euqli_dist(p, q, squared=True):
        """!
        Calculates the euclidean distance, the "ordinary" distance between two
        points
         
        The standard Euclidean distance can be squared in order to place
        progressively greater weight on objects that are farther apart. This
        frequently used in optimization problems in which distances only have
        to be compared.

        @param p: coordinates of point
        @type p: list
        @param q: coordinates of point
        @type q: list
        @param squared: 
        @type squared: boolean

        @return: distance
        @rtype: float
        """
        if squared:
            return ((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2)
        else:
            return np.sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))
        

    @staticmethod 
    def ref_peaks():
        """!
        Creates reference peaks using center of rois (the most defined peak)
        
        @return: list of Centers, dictionary with centers and coordinates
        @rtype: list, dict
        """
        peak_ref000_r = [5,17,29,41,53,65]
        peak_ref000_c = [0,6,12,18,24,30]
    
        peak_ref010_r = [11,23,35,47,59]
        peak_ref010_c = [0,6,12,18,24,30]
        
        peak_ref100_r = [5,17,29,41,53,65]
        peak_ref100_c = [3,9,15,21,27]
        
        peak_ref111_r = [11,23,35,47,59]
        peak_ref111_c = [3,9,15,21,27]
    
        Centers_000 = []
        Centers_010 = []
        Centers_100 = []
        Centers_111 = []
        dic_c000 = {}
        dic_c010 = {}
        dic_c100 = {}
        dic_c111 = {}
        roi = 0
        y_shift = 0
        for pri_000 in peak_ref000_r:
            x_shift = 0
            for prj_000 in peak_ref000_c:
                Cent_000 = [-20+x_shift,20-y_shift]
                Centers_000.append(Cent_000)
                dic_c000[roi] = [prj_000,pri_000]
                x_shift += 8
                roi += 1
    
            y_shift += 8
            
        roi = 0
        y_shift = 0
        for pri_010 in peak_ref010_r:
            x_shift = 0
            for prj_010 in peak_ref010_c:
                
                Cent_010 = [-20+x_shift,16-y_shift]
                Centers_010.append(Cent_010)
                dic_c010[roi] = [prj_010,pri_010]
                roi += 1
                x_shift += 8
                
            y_shift += 8
    
        roi = 0
        y_shift = 0
        for pri_100 in peak_ref100_r:
            x_shift = 0
            for prj_100 in peak_ref100_c:
                
                Cent_100 = [-16+x_shift,20-y_shift]
                Centers_100.append(Cent_100)
                dic_c100[roi] = [prj_100,pri_100]
                roi += 1            
                x_shift += 8
                
            y_shift += 8 
            
        roi = 0
        y_shift = 0
        for pri_111 in peak_ref111_r:
            x_shift = 0
            for prj_111 in peak_ref111_c:
                
                Cent_111 = [-16+x_shift,16-y_shift]
                Centers_111.append(Cent_111)
                dic_c111[roi] = [prj_111,pri_111]
                roi += 1            
                x_shift += 8
                
            y_shift += 8 
        return [Centers_000,Centers_010,Centers_100,Centers_111], [dic_c000, dic_c010, dic_c100, dic_c111]

    @staticmethod 
    def CrystalDict():
        """!
        Define Crystal identification dictionary with respective ids for all the peaks
        based on the different layers
         
        @return: rows =  ids of crystal ordered by row and column,
            dic_crystal_test = id from crystals
        @rtype: 2D-arr, dict
        """
        m=1
        row=[]
        j=0
        p=0
        rows=[]
        dic_crystal_test = {}
        for i in range(3426):
            if i >= (65*m + 31*p) and j%2 == 0:
                rows.append(row)
                #s = 1
                for n,r in enumerate(row):
                    if n == 0 or n == 64:
                        peakii={
                                'row'         : j,
                                'layer'       : 1,
                                'id'          : r,
                                'center'     : {},
                                'valid'    : False
                                }
                        dic_crystal_test[r] = peakii
                    else:
                        if n%2 != 0:
                            peakii={
                                    'row'         : j,
                                    'layer'       : 1,
                                    'id'          : r,
                                    'center'     : {},
                                    'valid'    : False
                                    }
                            dic_crystal_test[r] = peakii
                        else:
                            peakjj={
                                    'row'         : j,
                                    'layer'       : 2,
                                    'id'          : r,
                                    'center'     : {},
                                    'valid'    : False
                                    }
                            dic_crystal_test[r] = peakjj 
                            
                row = []
                j += 1
                p += 1
                    
            elif i >= (65*m+ 31*p) and j%2 != 0:
                rows.append(row)
                for r in row:
                    peakkk={
                            'row'         : j,
                            'layer'       : 3,
                            'id'          : r,
                            'center'     : {},
                            'valid'    : False
                            }
                    dic_crystal_test[r] = peakkk
                row = []
                j += 1
                m += 1
            else:
                pass
            row.append(i)
            
        return rows, dic_crystal_test


        
    @staticmethod     
    def Extract_x(lst): 
        return [item[0] for item in lst] 
    
    @staticmethod 
    def Extract_y(lst): 
        return [item[1] for item in lst] 