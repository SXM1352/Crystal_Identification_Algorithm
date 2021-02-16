__author__ = "david.perez.gonzalez" 
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:49:59 2021

@author: David.Perez.Gonzalez
"""
#module imports
import numpy as np
from itertools import groupby
import logging

#class imports
from Peak_Helper import PeakHelper

class PeakLabels(object):
    def __init__(self, cg, pclosest, c_roi, rows, dop_columns_accepted_edge, dop_min_edge, dop_max_edge, lenmin_edge, lenmax_edge, rows_accepted, dop_columns_accepted, len_columns_accepted, dop_min_cent, dop_max_cent, lenmin_cent, lenmax_cent):
        self.cg = cg
        
        self.pclosest = pclosest
        self.c_roi = c_roi
        self.rows = rows
        self.dop_columns_accepted_edge = dop_columns_accepted_edge
        self.dop_min_edge = dop_min_edge
        self.dop_max_edge = dop_max_edge
        self.lenmin_edge = lenmin_edge
        self.lenmax_edge = lenmax_edge
        
        self.rows_accepted = rows_accepted 
        self.dop_columns_accepted = dop_columns_accepted
        self.len_columns_accepted = len_columns_accepted   
        self.dop_min_cent = dop_min_cent
        self.dop_max_cent = dop_max_cent
        self.lenmin_cent = lenmin_cent
        self.lenmax_cent = lenmax_cent 
 
        
    def label(self, dic_palone, dic_rdefect, dic_crystal, dic_rows, dic_c): 
        """!
        Define the function to set the labels to our peaks

        @param dic_palone: peaks that have no row assigned
        @type dic_palone: dict
        @param dic_rdefect: row presumably incorrectly assigned
        @type dic_rdefect: dict
        @param dic_crystal: ids of crystal
        @type dic_crystal: dict
        @param dic_rows: peaks ordered by row
        @type dic_rows: dict
        @param dic_c: Creates reference peaks using center of rois (the most defined peak)
        @type dic_c: dict

        @return: None
        """
        rows_rest = []
        found = False
        dop = 0 #when activated we are in the rows with "double" peaks
        #a function could be created to sepparate dop = 0 and dop = 1, remember!
        
        self.c_roi_invalid = np.zeros(36)
        self.c_roi_defect = 0
        row_defect = False
        dic_rdefect[self.c_roi] = {} #to be able to store more than one row
        
        i_change = False
        h_change = False
        n_alone = 0
        nh_alone = 0
        peaks_alone = []
        
        dic_palo = {} # a joker dictionary
        n_rdefect = 0
        
        print("self.c_roi is: ", self.c_roi)
        for i in dic_rows.keys(): #we need to remove those rows that are classified and then loop again the rest
            i_crystal = i

            ch = np.where(np.abs(np.subtract(np.array(PeakHelper.Extract_x(dic_rows[i][0])),self.pclosest[0]))==np.min(np.abs(np.subtract(np.array(PeakHelper.Extract_x(dic_rows[i][0])),self.pclosest[0]))))
            ch = ch[0]
            
            if not found:
                ch = np.where(np.array(dic_rows[i][0])==self.pclosest) #closest peak to the reference from each row
                ch = np.array([key for key,group in groupby(ch[0]) if len(list(group)) > 1])
                ch_cent = np.where(np.array(dic_rows[i][0])==self.pclosest) #peak at the center to take reference
                ch_cent = np.array([key for key,group in groupby(ch_cent[0]) if len(list(group)) > 1])
                print("ch_cent is: ",ch_cent)
                print(dic_rows[i])
                i_clo = i
            
            if ch_cent.size>0: #the peak is found (we need one to assure we have found the peak with x,y values and not only with x or y)
                found = True
                if i_change:
                    i_crystal = i - n_alone
                if len(dic_rows[i][0]) == 1 and i != dic_rows.keys()[-1] and abs(np.diff([dic_rows[i][0][0][0],dic_rows[i_clo][0][ch_cent[0]][0]])) < 0.3: #to deal with the peaks that are alone and are important for the reference peaks (close to the center)
                    if abs(np.diff([np.median(PeakHelper.Extract_y(dic_rows[i+1][0])),dic_rows[i][0][0][1]])) > abs(np.diff([np.median(PeakHelper.Extract_y(dic_rows[i-1][0])),dic_rows[i][0][0][1]])): #if distance from alone to the median from the line under it is larger than the distance to the median from the line above, it goes to the above one
                        dic_rows[i-1][0].append(dic_rows[i][0][0])
                        dic_rows[i-1][0] = sorted(dic_rows[i-1][0])
                        dic_rows[i-1][1] = np.diff(PeakHelper.Extract_x(dic_rows[i-1][0]))
                        i = i - 1
                        i_crystal = i_crystal - 1
                        i_change = True
                        n_alone += 1
                        if dop == 0:
                            dop = 1
                        else:
                            dop = 0
                    else:
                        dic_rows[i+1][0].append(dic_rows[i][0][0])
                        dic_rows[i+1][0] = sorted(dic_rows[i+1][0])
                        dic_rows[i+1][1] = np.diff(PeakHelper.Extract_x(dic_rows[i+1][0]))
                        i_change = True
                        n_alone += 1
                        continue
                if len(dic_rows[i][0]) < 3 and i != dic_rows.keys()[-1] and abs(np.diff([dic_rows[i][0][0][0],dic_rows[i_clo][0][ch_cent[0]][0]])) >= 0.3: #if peaks are alone and quite far away from center (not really important now), they are saved for later analysis
                    if dic_c[self.c_roi][0] == 0 and dic_rows[i][0][ch[0]] == dic_rows[i][0][0] and len(dic_rows[i][0]) > 1:
                        pass
                    elif dic_c[self.c_roi][0] == 30 and dic_rows[i][0][ch[0]] == dic_rows[i][0][-1] and len(dic_rows[i][0]) > 1: 
                        pass   
                    else:
                        i_change = True
                        
                        peaks_alone.append(dic_rows[i][0])
                        print("Alone st.")
                        print(dic_rows[i][0])
                        dic_palo[n_alone] = dic_rows[i][0]
                        if (self.c_roi in dic_palone.keys()):
                            dic_palo[dic_palone[self.c_roi].keys()[0]] = dic_palone[self.c_roi].values()[0]
                            dic_palone[self.c_roi] = dic_palo
                        else:
                            dic_palone[self.c_roi] = dic_palo
                        dic_palo = {}
                        n_alone += 1
                        continue        
                if dop == 1: 
                    #print("A sanity check is also needed in case of missing the reference peak. On the edges is less probable")
                    if ch_cent[0] == 0:
                        for en_j, j in enumerate(dic_rows[i][0]):
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+en_j]]["center"][self.c_roi] = [j]
                            if len(dic_rows[i][0]) > self.dop_min_edge and len(dic_rows[i][0]) < self.dop_max_edge:
                                if i_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-self.dop_columns_accepted_edge and en_j <= ch[0]+self.dop_columns_accepted_edge: #we limit the rows that are out of range
                                    dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+en_j]]["valid"] = True
                    elif dic_rows[i_clo][0][ch_cent[0]] == dic_rows[i_clo][0][-1]: #right side edge
                        one_three = range(len(dic_rows[i][0]))#[0,1,2,3,4,5,6]
                        one_three.reverse()
                        for en_j, j in enumerate(dic_rows[i][0]):
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+4)-one_three[en_j]]]["center"][self.c_roi] = [j] #we use the columns from single peaks (3rd layer) as reference because of the main ref, so we need to multiply by 2 to get the one from 1/2 layers and then +4 because we want to set the last column possible as reference and then set the rest
                            if len(dic_rows[i][0]) > self.dop_min_edge and len(dic_rows[i][0]) < self.dop_max_edge:
                                if i_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-self.dop_columns_accepted_edge and en_j <= ch[0]+self.dop_columns_accepted_edge: #with the numbers of peaks we play with the peak in the middle (reference fomr main ref)
                                    dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+4)-one_three[en_j]]]["valid"] = True
                    else: 
                        #print("#row with 1st and 2nd peaks when we are not at the edges, we need to find also reference peaks (in the middle? those closest to x=12,etcc) for these rows")
                        for en_j, j in enumerate(dic_rows[i][0]):
                            try:
                                dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+2)+(en_j-ch[0])]]["center"][self.c_roi] = [j]
                                
                                if len(dic_rows[i][0]) > self.dop_min_cent and len(dic_rows[i][0]) < self.dop_max_cent: #before 7 and 14(010)/7,15 for 000 and 100
                                    if i_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-(self.dop_columns_accepted) and en_j <= ch[0]+(self.dop_columns_accepted): #we want to take the column under the last column from 3rd layer
                                        dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+2)+(en_j-ch[0])]]["valid"] = True
                            except:
                      #          print("Problem choosing the correct row.")
                                row_defect = True       
                    dop = 0
                else: # dop == 0: 
                    for en_j, j in enumerate(dic_rows[i][0]):
                        if dic_c[self.c_roi][0] == 0 or dic_c[self.c_roi][0] == 30: #we check whether we are at the edges
                            if dic_c[self.c_roi][0] == 0 and ch_cent[0] != 0:
                                #print("Problem finding reference. Sanity check activated.")
                                self.c_roi_defect = self.c_roi
                                row_defect = True
                            elif dic_c[self.c_roi][0] == 30 and dic_rows[i_clo][0][ch_cent[0]] != dic_rows[i_clo][0][-1]: #right side edge
                                #print("Problem finding reference. Sanity check activated.")
                                self.c_roi_defect = self.c_roi
                                row_defect = True
                            elif dic_c[self.c_roi][0] == 30 and dic_rows[i][0][ch[0]] != dic_rows[i][0][-1]:
                                #print("Problem finding reference for a secondary row. Information not valid?")
                                #pass
                                row_defect = True
                            elif dic_c[self.c_roi][0] == 0 and ch[0] != 0: #right side edge
                                #print("Problem finding reference for a secondary row. Information not valid?")
                                #pass
                                row_defect = True
                            else:
                                dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["center"][self.c_roi] = [j]
                                
                                if len(dic_rows[i][0]) > self.lenmin_edge and len(dic_rows[i][0]) < self.lenmax_edge:
                                    if self.cg == 1:
                                        self.len_columns_accepted = self.len_columns_accepted-1
                                    if dic_c[self.c_roi][0] == 30: #we are at the right side
                                        if i_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-self.len_columns_accepted:
                                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True
                                    else:
                                        if i_crystal <= i_clo+self.rows_accepted and en_j <= ch[0]+self.len_columns_accepted:
                                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True    
                        else: #we have to create a sanity check for missing points also on the other regions, but unlikely (it is the most defined peak)
                            try:
                                dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["center"][self.c_roi] = [j]
                                
                                if len(dic_rows[i][0]) > self.lenmin_cent and len(dic_rows[i][0]) < self.lenmax_cent:
                                    if i_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-(self.len_columns_accepted-1) and en_j <= ch[0]+(self.len_columns_accepted-1): #we deal with less columns when peaks from 3rd layer
                                        dic_crystal[self.rows[dic_c[self.c_roi][1]+(i_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True
                            except:
                            #    print("Problem choosing the correct row.")
                                row_defect = True
                    dop = 1
                if row_defect:
                    dic_rdefect[self.c_roi][n_rdefect] = dic_rows[i][0]
                    n_rdefect += 1
                    row_defect = False
                self.c_roi_invalid[self.c_roi_defect] = self.c_roi_defect    
            else:
                rows_rest.append(i) #we need to stop the loop when the peak is found and then loop over the rest
        dop = 1 #we start again and the row before ours is with 1,3
        rows_rest.reverse()
        for h in rows_rest: #remember that here we have h!
            h_crystal = h
            ch = np.where(np.abs(np.subtract(np.array(PeakHelper.Extract_x(dic_rows[h][0])),self.pclosest[0]))==np.min(np.abs(np.subtract(np.array(PeakHelper.Extract_x(dic_rows[h][0])),self.pclosest[0]))))
            ch = ch[0]
            
            if h_change:
                h_crystal = h + nh_alone
            if len(dic_rows[h][0]) == 1 and h != 0 and abs(np.diff([dic_rows[h][0][0][0],dic_rows[i_clo][0][ch_cent[0]][0]])) < 0.3:
                if abs(np.diff([np.median(PeakHelper.Extract_y(dic_rows[h-1][0])),dic_rows[h][0][0][1]])) > abs(np.diff([np.median(PeakHelper.Extract_y(dic_rows[h+1][0])),dic_rows[h][0][0][1]])): #if distance from alone to the median from the line under it is larger than the distance to the median from the line above, it goes to the above one
                    dic_rows[h+1][0].append(dic_rows[h][0][0])
                    dic_rows[h+1][0] = sorted(dic_rows[h+1][0])
                    dic_rows[h+1][1] = np.diff(PeakHelper.Extract_x(dic_rows[h+1][0]))
                    h_change = True
                    nh_alone += 1
                    h_crystal = h_crystal + 1
                    h = h + 1
                    if dop == 0:
                        dop = 1
                    else:
                        dop = 0
                else:
                    dic_rows[h-1][0].append(dic_rows[h][0][0])
                    dic_rows[h-1][0] = sorted(dic_rows[h-1][0])
                    dic_rows[h-1][1] = np.diff(PeakHelper.Extract_x(dic_rows[h-1][0]))
                    h_change = True
                    nh_alone += 1
                    continue
            if len(dic_rows[h][0]) < 3 and h != 0 and abs(np.diff([dic_rows[h][0][0][0],dic_rows[i_clo][0][ch_cent[0]][0]])) >= 0.3: #we check it is not an important peak
                if dic_c[self.c_roi][0] == 0 and dic_rows[h][0][ch[0]] == dic_rows[h][0][0] and len(dic_rows[i][0]) > 1:
                    pass
                elif dic_c[self.c_roi][0] == 30 and dic_rows[h][0][ch[0]] == dic_rows[h][0][-1] and len(dic_rows[i][0]) > 1: 
                    pass   
                else:
                    h_change = True
                    nh_alone += 1
                    peaks_alone.append(dic_rows[h][0])
                    dic_palo[n_alone] = dic_rows[h][0]
                    if (self.c_roi in dic_palone.keys()):
                        dic_palo[dic_palone[self.c_roi].keys()[0]] = dic_palone[self.c_roi].values()[0]
                        dic_palone[self.c_roi] = dic_palo
                    else:
                        dic_palone[self.c_roi] = dic_palo
                    dic_palo = {}
                    n_alone += 1
                    continue
            if dop == 1: 
                if ch_cent[0] == 0:
                    for en_j, j in enumerate(dic_rows[h][0]):
                        dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+en_j]]["center"][self.c_roi] = [j]
                        if len(dic_rows[h][0]) > self.dop_min_edge and len(dic_rows[h][0]) < self.dop_max_edge:
                            if h_crystal >= i_clo-self.rows_accepted and en_j >= ch[0]-self.dop_columns_accepted_edge and en_j <= ch[0]+self.dop_columns_accepted_edge:
                                dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+en_j]]["valid"] = True
                elif dic_rows[i_clo][0][ch_cent[0]] == dic_rows[i_clo][0][-1]: #right side edge
                    one_three = range(len(dic_rows[h][0]))#[0,1,2,3,4,5,6]
                    one_three.reverse()
                    for en_j, j in enumerate(dic_rows[h][0]):
                        try:
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+4)-one_three[en_j]]]["center"][self.c_roi] = [j] # +4 because we want to set the last column possible as reference and then set the rest
                            if len(dic_rows[h][0]) > self.dop_min_edge and len(dic_rows[h][0]) < self.dop_max_edge:
                                if h_crystal >= i_clo-self.rows_accepted and en_j >= ch[0]-self.dop_columns_accepted_edge and en_j <= ch[0]+self.dop_columns_accepted_edge:
                                    dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+4)-one_three[en_j]]]["valid"] = True
                        except:
                            #print("Problem choosing the correct row.")
                            row_defect = True
                else: 
                    one_three = range(2,len(dic_rows[h][0])+2)#[2,3,4,5,6,7,8]
                    for en_j, j in enumerate(dic_rows[h][0]):
                        try:
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+2)+(en_j-ch[0])]]["center"][self.c_roi] = [j]
                            
                            if len(dic_rows[h][0]) > self.dop_min_cent and len(dic_rows[h][0]) < self.dop_max_cent: #before 7 and 14(010)/7,15(100)
                                if h_crystal >= i_clo-self.rows_accepted and en_j >= ch[0]-(self.dop_columns_accepted) and en_j <= ch[0]+(self.dop_columns_accepted):
                                    dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][((dic_c[self.c_roi][0]*2)+2)+(en_j-ch[0])]]["valid"] = True 
                        except:
                            #print("Problem choosing the correct row.")
                            row_defect = True         
                dop = 0
            else: # dop == 0: 
                for en_j, j in enumerate(dic_rows[h][0]):
                    if dic_c[self.c_roi][0] == 0 or dic_c[self.c_roi][0] == 30:
                        if dic_c[self.c_roi][0] == 0 and ch_cent[0] != 0:
                            #print("Problem finding reference. Sanity check activated.")
                            self.c_roi_defect = self.c_roi
                            row_defect = True
                        elif dic_c[self.c_roi][0] == 30 and dic_rows[i_clo][0][ch_cent[0]] != dic_rows[i_clo][0][-1]: #right side edge
                            #print("Problem finding reference. Sanity check activated.")
                            self.c_roi_defect = self.c_roi
                            row_defect = True
                        elif dic_c[self.c_roi][0] == 30 and dic_rows[h][0][ch[0]] != dic_rows[h][0][-1]:
                            #pass
                            row_defect = True
                            #print("Problem finding reference for a secondary row. Information not valid?")
                        elif dic_c[self.c_roi][0] == 0 and ch[0] != 0: #left side edge
                            #pass
                            row_defect = True
                            #print("Problem finding reference for a secondary row. Information not valid?")
                        else:
                            #print(dic_rows[h][0])
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["center"][self.c_roi] = [j]
    
                            if len(dic_rows[h][0]) > self.lenmin_edge and len(dic_rows[h][0]) < self.lenmax_edge:
            #                    print("LEN")
                                if self.cg == 1:
                                        self.len_columns_accepted = self.len_columns_accepted-1
                                if dic_c[self.c_roi][0] == 30: #we are at the right side
                                    if h_crystal <= i_clo+self.rows_accepted and en_j >= ch[0]-self.len_columns_accepted:
                                        dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True
                                else:
                                    if h_crystal >= i_clo-self.rows_accepted and en_j <= ch[0]+self.len_columns_accepted:
                                        dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True
                    else:
                        try:
                            dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["center"][self.c_roi] = [j]
                            #lenmin = 3
                            #lenmax = 8 #before 11(000), 8(010), 9(100)
                            if len(dic_rows[h][0]) > self.lenmin_cent and len(dic_rows[h][0]) < self.lenmax_cent:
                                if h_crystal >= i_clo-self.rows_accepted and en_j >= ch[0]-(self.len_columns_accepted-1) and en_j <= ch[0]+(self.len_columns_accepted-1):
                                    dic_crystal[self.rows[dic_c[self.c_roi][1]+(h_crystal-i_clo)][dic_c[self.c_roi][0]+(en_j-ch[0])]]["valid"] = True
                        except:
                            #print("Problem choosing the correct row.")
                            row_defect = True
                dop = 1
                if row_defect:
                    dic_rdefect[self.c_roi][n_rdefect] = dic_rows[h][0]  
                    n_rdefect += 1
                    row_defect = False
            self.c_roi_invalid[self.c_roi_defect] = self.c_roi_defect
    
        return dic_crystal,dic_palone, dic_rdefect