__author__ = "david.perez.gonzalez" 
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 15:07:30 2020

@author: David
"""
import numpy as np

#class imports


class SanCheckInv(object):
    
    def __init__(self, dist_min_x_list, dist_min_y_list, dist_min_xy_list, median_rows, median_columns, rows, cg):
        self.cg = cg
        
        self.median_rows = median_rows
        self.median_columns = median_columns
        self.rows = rows
        
        self.dist_min_x_list = dist_min_x_list
        self.dist_min_y_list = dist_min_y_list
        
        self.dist_min_xy_list = dist_min_xy_list
        
    
    def __euqli_dist(self, p, q, squared=False):
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
        
    def __closest_peak_comp(self, coordinate,peaks): #select the peak which closest to the coordinate given
        low_dist = float('inf')
        low_dist_2 = None
        closest_peak = None
        closest_peak_2 = None
        for i in peaks.keys():
            p = peaks[i]
            dist = self.__euqli_dist(p,coordinate)
            if dist < low_dist:
                low_dist_2 = low_dist
                closest_peak_2 = closest_peak
                low_dist = dist
                closest_peak = p
            elif dist < low_dist_2:
                low_dist_2 = dist
                closest_peak_2 = p
                
        return closest_peak, closest_peak_2
    
    def __clo_rs_app_Peak(self, peaks, coordinate, dist_min):
        low_dist = dist_min
        c_roi_def = None
        closest_peak = None
        delete = None
        for i in peaks.keys():
            c_roi = peaks[i].keys()[0]
            dist = self.__euqli_dist(peaks[i][c_roi],coordinate)
            if dist < low_dist:
                low_dist = dist
                closest_peak = peaks[i][c_roi]
                c_roi_def = c_roi
                delete = i
        if closest_peak:
            peaks[delete][c_roi_def] = [33, 33]
            
        return closest_peak, c_roi_def, peaks        
    
    def __clo_rs(self, cur_peak_xy, median_rc, dist_min): #find the closest position to the point given from a dict
        low_dist = float('inf')
        closest_rc = None
        for rc in median_rc.keys():
            dist = abs(np.diff([cur_peak_xy, median_rc[rc]]))
            if dist < low_dist:
                low_dist = dist
                closest_rc = rc
        if low_dist > dist_min[self.cg]:
            closest_rc = None
            
        return closest_rc
    
    def __clo_rs_inv(self, cur_peak_xy, median_rc, dist_min): #find the closest position to the point given from a dict
        low_dist = float('inf')
        closest_rc = None
        for rc in median_rc.keys():
            dist = abs(np.diff([cur_peak_xy, median_rc[rc]]))
            if dist < low_dist:
                low_dist = dist
                closest_rc = rc
        dist_min_inv = dist_min[self.cg] + 0.5
        if low_dist > dist_min_inv:
            closest_rc = None
            
        return closest_rc
    
    def __clo_rs_app(self, cur_peak_xy, median_rc, dist_min): #find the closest position to the point given from a dict
        closest_rc = False
        dist = abs(np.diff([cur_peak_xy, median_rc]))
        dist_min_inv = dist_min[self.cg] + 0.2
        if dist > dist_min_inv:
            closest_rc = True
            
        return closest_rc    
    
    def __clo2_rs(self, cur_peak_xy, median_rc, dist_min): #find the 2closest position to the point given from a dict
        low_dist = float('inf')
        closest_rc = None
        closest2_rc = None
        
        for rc in median_rc.keys():
            dist = abs(np.diff([cur_peak_xy, median_rc[rc]]))
            if dist < low_dist:
                low_dist_2 = low_dist
                closest2_rc = closest_rc
                low_dist = dist
                closest_rc = rc
            elif dist < low_dist_2:
                low_dist_2 = dist
                closest2_rc = rc
        if low_dist > dist_min[self.cg]:
            closest2_rc = None
    
        return closest2_rc
    
    def __f_recheck(self, dic_recheck, dic_inv, dic_crystal):
        for j in dic_recheck.keys():
            closest_row = self.__clo_rs(dic_recheck[j][dic_recheck[j].keys()[0]][0][1], self.median_rows, self.dist_min_y_list)
            closest_col = self.__clo_rs(dic_recheck[j][dic_recheck[j].keys()[0]][0][0], self.median_columns, self.dist_min_x_list)
            if closest_row != None and closest_col != None:
                closest_col_orig = closest_col
                if closest_row%2 != 0:
                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                        # print("mmmm")
                        dic_inv[np.max(dic_inv.keys())+1] = {dic_recheck[j].keys()[0]: dic_recheck[j][dic_recheck[j].keys()[0]][0]}
                        continue
                    else:
                        closest_col = (closest_col-2)/2   
                if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
            
                    dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                    #we set them as valid because the lines are only from valid columns and rows
                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                #    # print("cry",rows[closest_row][closest_col])
                    # print("Tworks8")                     
                else: #there is already a peak, nearby free labels are searched and it comes from recheck, from peaks that were with rows, but wrong ones, so possible to find empty labels in the nearby
                    if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                        # print("mist")
                        # print("cry",self.rows[closest_row][closest_col])
                        closest2_row = self.__clo2_rs(dic_recheck[j][dic_recheck[j].keys()[0]][0][1], self.median_rows, self.dist_min_y_list)
                        closest2_col = self.__clo2_rs(dic_recheck[j][dic_recheck[j].keys()[0]][0][0], self.median_columns, self.dist_min_x_list)
                        # print("cry",closest2_row,closest2_col)
                        
                        try:
                            if closest2_row != None and closest2_col != None:
                                if closest2_row%2 != 0:
                                    if closest2_col%2 != 0 or closest2_col == 64 or closest2_col == 0:
                                        # print("mmmm")
                                        dic_inv[np.max(dic_inv.keys())+1] = {dic_recheck[j].keys()[0]: dic_recheck[j][dic_recheck[j].keys()[0]][0]}
                                        continue
                                    else:
                                        closest2_col = (closest2_col-2)/2
                                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                        dic_inv[np.max(dic_inv.keys())+1] = {dic_recheck[j].keys()[0]: dic_recheck[j][dic_recheck[j].keys()[0]][0]}
                                        # print("mmmm")
                                        continue
                                    else:
                                        closest_col = (closest_col-2)/2
                                else:
                                    dic_inv[np.max(dic_inv.keys())+1] = {dic_recheck[j].keys()[0]: dic_recheck[j][dic_recheck[j].keys()[0]][0]}
                                    continue
                            if not dic_crystal[self.rows[closest2_row][closest_col]]["center"]: #no peak
                                dic_crystal[self.rows[closest2_row][closest_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                        #we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest2_row][closest_col]]["valid"] = True
                                # print("cry",self.rows[closest2_row][closest_col])
                                # print("works8_cryrow")
                            elif not dic_crystal[self.rows[closest_row][closest2_col]]["center"]: #no peak
                                dic_crystal[self.rows[closest_row][closest2_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                        #we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest_row][closest2_col]]["valid"] = True
                                # print("cry",self.rows[closest_row][closest2_col])
                                # print("works8_crycol")
                            elif not dic_crystal[self.rows[closest2_row][closest2_col]]["center"]: #no peak
                                dic_crystal[self.rows[closest2_row][closest2_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                        #we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest2_row][closest2_col]]["valid"] = True
                                # print("cry",self.rows[closest2_row][closest2_col])
                                # print("works8_crycolrow")
                        except:
                            print("Not work, problem with second row/column")
                        #pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                    else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                        peaks_to_compare = {"valid":dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0], "new":dic_recheck[j][dic_recheck[j].keys()[0]][0]}
                        # print(peaks_to_compare)
                        # print(self.median_columns[closest_col_orig])
                        # print(self.median_rows[closest_row])
                        coordinate = [self.median_columns[closest_col_orig], self.median_rows[closest_row]]
                        clo_p, clo_p2 = self.__closest_peak_comp(coordinate,peaks_to_compare)
                        # print("clop_recheck",clo_p,clo_p2)
                        #clo_p2 must be plotted
                        dic_inv[np.max(dic_inv.keys())+1] = {dic_recheck[j].keys()[0]: clo_p2}
                        
                        dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                        
                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck[j].keys()[0]] = [clo_p]
                #we set them as valid because the lines are only from valid columns and rows
                        
#                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                        # print("works9label")
                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True # we set them as valid because the lines are only from valid columns and rows
            else:
                print("mist2")
            
        return dic_crystal, dic_inv
    
    def __f_palone(self, dic_palone, dic_inv, dic_crystal):
        for ij in dic_palone.keys():
            for j in dic_palone[ij].keys():
                # print(dic_palone)
                # print(dic_palone[ij], ij)
                # print(dic_palone[ij][j][0][1])
                # print(dic_palone[ij][j][0][0])
                for joker in dic_palone[ij][j]:
                    # print(joker)
                    closest_row = self.__clo_rs(joker[1], self.median_rows, self.dist_min_y_list)
                    closest_col = self.__clo_rs(joker[0], self.median_columns, self.dist_min_x_list)
                    # print(closest_row)
                    # print(closest_col)
                    if closest_row != None and closest_col != None:
                        closest_col_orig = closest_col
                        if closest_row%2 != 0:
                                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                        # print("mmmm24")
                                        dic_inv[np.max(dic_inv.keys())+1] = {ij: joker}
                                        continue
                                    else:
                                        closest_col = (closest_col-2)/2
                     
                        if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
                    
                            dic_crystal[self.rows[closest_row][closest_col]]["center"][ij] = [joker]
                            #we set them as valid because the lines are only from valid columns and rows
                            dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                            
                            # print("AA")                            
                        else: #there is already a peak
                            if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
 
                                # print("secondPEAK943") 
                                peaks_to_compare = {"valid":dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0], "new":joker}
                                # print(peaks_to_compare)
                                # print(self.median_columns[closest_col_orig])
                                # print(self.median_rows[closest_row])
                                coordinate = [self.median_columns[closest_col_orig], self.median_rows[closest_row]]
                                clo_p, clo_p2 = self.__closest_peak_comp(coordinate,peaks_to_compare)
                                # print("clop_alone",clo_p,clo_p2)
                                #clo_p2 must be plotted
                                dic_inv[np.max(dic_inv.keys())+1] = {ij: clo_p2}
                                
                                dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                                
                                dic_crystal[self.rows[closest_row][closest_col]]["center"][ij] = [clo_p]
                        #we set them as valid because the lines are only from valid columns and rows

        #                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck[j].keys()[0]] = dic_recheck[j][dic_recheck[j].keys()[0]]
                                # print("works9label")
                                dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True # we set them as valid because the lines are only from valid columns and rows
        #                      
                                pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                            else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                                dic_crystal[self.rows[closest_row][closest_col]]["center"][ij] = [joker]              
                                
                      #  we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                    else:
                        dic_inv[np.max(dic_inv.keys()) + 1] = {ij: joker}
        return dic_crystal, dic_inv
    
    def __f_rdefect(self, dic_rdefect, dic_crystal):
        for ij in dic_rdefect.keys():
            for j in dic_rdefect[ij].keys():
                # print("RDFECT",dic_rdefect[ij][j][0][1])
                # print("RDFECT2",dic_rdefect[ij][j][0][0])
                for joker in dic_rdefect[ij][j]:
                    # print("RDFECTj",joker)
                    closest_row = self.__clo_rs(joker[1], self.median_rows, self.dist_min_y_list)
                    closest_col = self.__clo_rs(joker[0], self.median_columns, self.dist_min_x_list)
                    # print(closest_row)
                    # print(closest_col)
                    
                    if closest_row != None and closest_col != None:
                        if closest_row%2 != 0:
                                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                        # print("mmmm24")
                                        continue
                                    else:
                                        closest_col = (closest_col-2)/2
                                        
                        # print("dic_C",dic_crystal[self.rows[closest_row][closest_col]])
                        if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
                    
                            dic_crystal[self.rows[closest_row][closest_col]]["center"][ij] = [joker]
                            #we set them as valid because the lines are only from valid columns and rows
                            dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                            
                            # print("AA")                        
                        else: #there is already a peak
                            if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                                # print("secondPEAK982") #it does not happen at all
                                pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                            else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                                dic_crystal[self.rows[closest_row][closest_col]]["center"][ij] = [joker]              
                                
                      #  we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                
        return dic_crystal
    
    def __f_recheckcol(self, dic_recheck_col, dic_crystal):          
        for j in dic_recheck_col.keys():
            closest_row = self.__clo_rs(dic_recheck_col[j][dic_recheck_col[j].keys()[0]][0][1], self.median_rows, self.dist_min_y_list)
            closest_col = self.__clo_rs(dic_recheck_col[j][dic_recheck_col[j].keys()[0]][0][0], self.median_columns, self.dist_min_x_list)
            
            if closest_row != None and closest_col != None:
                if closest_row%2 != 0:
                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                        # print("mmmm657")
                        continue
                    else:
                        closest_col = (closest_col-2)/2 
                # print(dic_recheck_col[j])
             
                if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
            
                    dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck_col[j].keys()[0]] = dic_recheck_col[j][dic_recheck_col[j].keys()[0]]
                    #we set them as valid because the lines are only from valid columns and rows
                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                    # print("works8567")                       
                else: #there is already a peak
                    if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                        # print("secondPEAK1014") #it does not happen at all
                        pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                    else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                        
                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_recheck_col[j].keys()[0]] = dic_recheck_col[j][dic_recheck_col[j].keys()[0]]
                        # print("works9label765")
                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True # we set them as valid because the lines are only from valid columns and rows
            else:
                # print("mist2567")
        return dic_crystal
    
    def __f_checkdouble(self, dic_double, dic_crystal):
        for i in dic_crystal.keys(): 
            if dic_crystal[i]["center"]:
                if len(dic_crystal[i]["center"].keys()) > 1:
                    # print(dic_crystal[i])
                    for j in dic_crystal[i]["center"].keys():
                        closest_row = self.__clo_rs(dic_crystal[i]["center"][j][0][1], self.median_rows, self.dist_min_y_list)
                        closest_col = self.__clo_rs(dic_crystal[i]["center"][j][0][0], self.median_columns, self.dist_min_x_list)
                        
                        if closest_row != None and closest_col != None:
                            if closest_row%2 != 0:
                                if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                    # print("mmmm24")
                                    for i_cr2 in dic_crystal[i]["center"].keys():
                                        if i_cr2 != j:
                                            if np.abs(np.diff([dic_crystal[i]["center"][j][0][0],dic_crystal[i]["center"][i_cr2][0][0]])) > 3:                                        
                                                dic_double[i_cr2] = dic_crystal[i]["center"][i_cr2] 
                                            else:
                                                dic_double = dic_crystal[i]["center"]
                                    dic_crystal[i]["center"] = dic_double
                                    dic_double = {}
                                    continue
                                else:
                                    closest_col = (closest_col-2)/2
                            if self.rows[closest_row][closest_col] != i:
                                        
                                # print(dic_crystal[i]["center"][j])
                             
                                if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
                            
                                    dic_crystal[self.rows[closest_row][closest_col]]["center"][j] = dic_crystal[i]["center"][j]
                                    #we set them as valid because the lines are only from valid columns and rows
                                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                    # print("works24")
                                    for i_cr2 in dic_crystal[i]["center"].keys():
                                        if i_cr2 != j:
                                            
                                            dic_double[i_cr2] = dic_crystal[i]["center"][i_cr2] 
                                        
                                    dic_crystal[i]["center"] = dic_double
                                    dic_double = {}                    
                                else: #there is already a peak
                                    if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                                        # print("secondPEAK1074") #it does not happen at all
                                        pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                                    else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks, but in valid zone, so valid!)
                                        dic_crystal[self.rows[closest_row][closest_col]]["center"][j] = dic_crystal[i]["center"][j]
                                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                        for i_cr2 in dic_crystal[i]["center"].keys():
                                            if i_cr2 != j:
                                                
                                                dic_double[i_cr2] = dic_crystal[i]["center"][i_cr2] 
                                        dic_crystal[i]["center"] = dic_double
                                        dic_double = {}
                                        # print("works25")
                            else:
                                dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                        else:
                            # print("mist25")
                            # print(dic_crystal[i]["center"][j])
                            for i_cr2 in dic_crystal[i]["center"].keys():
                                if i_cr2 != j:
                                    if np.abs(np.diff([dic_crystal[i]["center"][j][0][0],dic_crystal[i]["center"][i_cr2][0][0]])) > 3:                                        
                                        dic_double[i_cr2] = dic_crystal[i]["center"][i_cr2] 
                                    else: #we do so we can deal with 3
                                        dic_double = dic_crystal[i]["center"]
                            dic_crystal[i]["center"] = dic_double
                            dic_double = {}
                            
        return dic_crystal
    
    def __check_inv(self, dic_crystal, dic_recheck, dic_nrch, dic_double, rows, n_rechecks, dic_inv): #select the peak which closest to the coordinate given
        for i in dic_crystal.keys():
            if dic_crystal[i]["center"]:
                if not dic_crystal[i]["valid"]:
                    # print(dic_crystal[i])
                    
                    if len(dic_crystal[i]["center"].keys()) > 1:
                        for cr in dic_crystal[i]["center"].keys():
                            try:
                                closest_row = self.__clo_rs(dic_crystal[i]["center"][cr][0][1], self.median_rows, self.dist_min_y_list)
                                closest_col = self.__clo_rs(dic_crystal[i]["center"][cr][0][0], self.median_columns, self.dist_min_x_list)
                            except:
                                closest_row = None
                                closest_col = None
                                # print("Peak was already analised.")
                            if closest_row != None and closest_col != None:
                                # print("HEY")
                                if closest_row%2 != 0:
                                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                        continue
                                    else:
                                        closest_col = (closest_col-2)/2
                                if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #center is empty
                                    #we include the new peak in the corresponding label
                                    dic_crystal[self.rows[closest_row][closest_col]]["center"][cr] = dic_crystal[i]["center"][cr]
                                    #we set it as valid because the lines are only from valid columns and rows
                                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                    
                                    #we need to remove the peak from the incorrect label
                                    for cr_rm in dic_crystal[i]["center"].keys(): #to remove we loop and redefine with not cr
                                        if cr_rm != cr:
                                            dic_double[cr_rm] = dic_crystal[i]["center"][cr_rm]
                                    dic_crystal[i]["center"] = dic_double
                                    dic_double = {}
                                    
                                    # print("works")                                  
                                else: #there is already a peak
                                    if rows[closest_row][closest_col] != i: #we need to check that it is not the same label
                                        if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                                            #we should inlcude it as a second peak
                                            # print("secondPEAK656") #it does not happen at all
                                            pass #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                                        else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                                            ## print(i,closest_row,closest_col)
                                            if len(dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()) > 1:
                                                for cr_rch in dic_crystal[self.rows[closest_row][closest_col]]["center"].keys():
                                                    dic_nrch[cr_rch] = dic_crystal[self.rows[closest_row][closest_col]]["center"][cr_rch]        
                                                    dic_recheck[n_rechecks] = dic_nrch
                                                    dic_nrch = {}
                                                    n_rechecks += 1
                                            else:
                                                dic_nrch[dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]] = dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]]
                                                dic_recheck[n_rechecks] = dic_nrch
                                                dic_nrch = {}
                                                n_rechecks += 1
                                            dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                                            
                                            dic_crystal[self.rows[closest_row][closest_col]]["center"][cr] = dic_crystal[i]["center"][cr]
                                    #we set them as valid because the lines are only from valid columns and rows
                                            dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                            
                                            if len(dic_crystal[i]["center"].keys()) > 1:
                                            
                                                for cr_rm in dic_crystal[i]["center"].keys(): #to remove we loop and redefine with not cr
                                                    if cr_rm != cr:
                                                        dic_double[cr_rm] = dic_crystal[i]["center"][cr_rm]
                                                dic_crystal[i]["center"] = dic_double
                                                dic_double = {}
                                            else:
                                                dic_crystal[i]["center"] = {}
                                            
                                            # print("works2")
                                    else: #if it is the same label, we could set it as valid 
                                        # print("i_row")
                                        # print(dic_crystal[self.rows[closest_row][closest_col]])
                                        if len(dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()) > 1:
                                            if np.abs(np.diff([dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0][0],dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[1]][0][0]])) > 10:
                                                for i_cr2 in dic_crystal[self.rows[closest_row][closest_col]]["center"].keys():
                                                    if i_cr2 != cr:
                                                        dic_nrch[i_cr2] = dic_crystal[self.rows[closest_row][closest_col]]["center"][i_cr2]        
                                                        dic_recheck[n_rechecks] = dic_nrch
                                                        dic_nrch = {}
                                                        n_rechecks += 1
                                                        
                                                dic_double[cr] = dic_crystal[self.rows[closest_row][closest_col]]["center"][cr] #only works if there are only two peaks, with three does not
                                                dic_crystal[self.rows[closest_row][closest_col]]["center"] = dic_double
                                                dic_double = {}
                                        
                                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True  
                                        # print("works3")
                    else:
                        closest_row = self.__clo_rs(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1], self.median_rows, self.dist_min_y_list)
                        closest_col = self.__clo_rs(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0], self.median_columns, self.dist_min_x_list)
                        # print(closest_row)
                        # print(closest_col)
                        
                        if closest_row != None and closest_col != None:
                            closest_col_orig = closest_col
                            valid_new = True
                            if closest_row%2 != 0:
                                if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                                    dic_inv[np.max(dic_inv.keys())+1] = {dic_crystal[i]["center"].keys()[0]: dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0]}
                                    continue
                                else:
                                    closest_col = (closest_col-2)/2
                                    valid_new = False
                            # print("HEY2")
                            # print(dic_crystal[i])
                     
                            if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
    
                                dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[i]["center"].keys()[0]] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]]
                                #we set them as valid because the lines are only from valid columns and rows
                                dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                
                                dic_crystal[i]["center"] = {}
                                # print(dic_crystal[self.rows[closest_row][closest_col]])
                                # print("works4")
                            else: #there is already a peak
                                if rows[closest_row][closest_col] != i: #we need to check that it is not the same label
                                    if dic_crystal[self.rows[closest_row][closest_col]]["valid"]:
                                        # print("secondPEAK738") 
                                        if valid_new:
                                            peaks_to_compare = {"valid":dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0], "new":dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0]}
                                            # print(peaks_to_compare)
                                            # print(self.median_columns[closest_col_orig])
                                            # print(self.median_rows[closest_row])
                                            coordinate = [self.median_columns[closest_col_orig], self.median_rows[closest_row]]
                                            clo_p, clo_p2 = self.__closest_peak_comp(coordinate,peaks_to_compare)
                                            # print("clop_check_inv",clo_p,clo_p2)
                                            dic_nrch[dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]] = [clo_p2]
                                            dic_recheck[n_rechecks] = dic_nrch
                                            dic_nrch = {}
                                            n_rechecks += 1
                                            
                                            dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                                            
                                            dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[i]["center"].keys()[0]] = [clo_p]
                                    #we set them as valid because the lines are only from valid columns and rows
                                            
                                            dic_crystal[i]["center"] = {}
                                        else:
                                            dic_inv[np.max(dic_inv.keys())+1] = {dic_crystal[i]["center"].keys()[0]: dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0]}
                                         #there is already a peak with this label and it is valid from the restrictions, that is why the new peak cannot change its label
                                    else: #this would be not that probable, because it is invalid, with center and it is not the same peak (most likely double peaks)
                                        ## print(closest_row,closest_col,i)
                                        if len(dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()) > 1:
                                            for cr_rch in dic_crystal[self.rows[closest_row][closest_col]]["center"].keys():
                                                dic_nrch[cr_rch] = dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]]        
                                                dic_recheck[n_rechecks] = dic_nrch
                                                dic_nrch = {}
                                                n_rechecks += 1
                                        else:
                                            dic_nrch[dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]] = dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]]
                                            dic_recheck[n_rechecks] = dic_nrch
                                            dic_nrch = {}
                                            n_rechecks += 1
                                        
                                        dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                                        
                                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[i]["center"].keys()[0]] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]]
                                #we set them as valid because the lines are only from valid columns and rows
                                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                                        
                                        dic_crystal[i]["center"] = {}
                                        
                                        # print("works5") 
                                else: #if it is the same label, we could set it as valid 
                                    # print("i_row")
                                    # print(dic_crystal[self.rows[closest_row][closest_col]])
                                    if len(dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()) > 1:
                                        if np.abs(np.diff([dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0][0],dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[1]][0][0]])) > 10:
                                            for i_cr2 in dic_crystal[self.rows[closest_row][closest_col]]["center"].keys():
                                                if i_cr2 != cr:
                                                    dic_nrch[i_cr2] = dic_crystal[self.rows[closest_row][closest_col]]["center"][i_cr2]        
                                                    dic_recheck[n_rechecks] = dic_nrch
                                                    dic_nrch = {}
                                                    n_rechecks += 1
                                                    
                                            dic_double[cr] = dic_crystal[self.rows[closest_row][closest_col]]["center"][cr] #only works if there are only two peaks, with three does not
                                            dic_crystal[self.rows[closest_row][closest_col]]["center"] = dic_double
                                            dic_double = {}
                                    
                                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True  
                                    # print("works7")

        return dic_crystal, dic_recheck, dic_inv
    
    def __f_inv(self, dic_crystal, dic_inv, dic_inv_plot):
        # print("diccc", dic_inv)
        for j in dic_inv.keys():
            # print(dic_inv[j])
            closest_row = self.__clo_rs(dic_inv[j][dic_inv[j].keys()[0]][1], self.median_rows, self.dist_min_y_list)
            closest_col = self.__clo_rs(dic_inv[j][dic_inv[j].keys()[0]][0], self.median_columns, self.dist_min_x_list)
            if closest_row != None and closest_col != None:
                closest_col_orig = closest_col
                if closest_row%2 != 0:
                    if closest_col%2 != 0 or closest_col == 64 or closest_col == 0:
                        # print("mmmm")
                        dic_inv_plot[np.max(dic_inv_plot.keys())+1] = {dic_inv[j].keys()[0]: dic_inv[j][dic_inv[j].keys()[0]]}
                        continue
                    else:
                        closest_col = (closest_col-2)/2
                        
                if not dic_crystal[self.rows[closest_row][closest_col]]["center"]: #no peak
            
                    dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_inv[j].keys()[0]] = [dic_inv[j][dic_inv[j].keys()[0]]]
                    #we set them as valid because the lines are only from valid columns and rows
                    dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                #    # print("cry",rows[closest_row][closest_col])
                    # print("Tworks8")                             
                else:
                    # print("H")
                    # print(dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0])
                    # print(dic_inv[j][dic_inv[j].keys()[0]])
                    if dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0] == dic_inv[j][dic_inv[j].keys()[0]]:
                        # print("AY")
                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                    else:
                        peaks_to_compare = {"valid":dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]][0], "new":dic_inv[j][dic_inv[j].keys()[0]]}
                        # print(peaks_to_compare)
                        # print(self.median_columns[closest_col_orig])
                        # print(self.median_rows[closest_row])
                        coordinate = [self.median_columns[closest_col_orig], self.median_rows[closest_row]]
                        clo_p, clo_p2 = self.__closest_peak_comp(coordinate,peaks_to_compare)
                        # print("clop_f_inv",clo_p,clo_p2)
                        
                        #dic_crystal[self.rows[closest_row][closest_col]]["center"] = {}
                        
                        dic_crystal[self.rows[closest_row][closest_col]]["center"][dic_crystal[self.rows[closest_row][closest_col]]["center"].keys()[0]] = [clo_p]
                #we set them as valid because the lines are only from valid columns and rows
                        dic_crystal[self.rows[closest_row][closest_col]]["valid"] = True
                        
                        dic_inv_plot[np.max(dic_inv_plot.keys())+1] = {dic_inv[j].keys()[0]: clo_p2} 
                        dic_inv_plot[np.max(dic_inv_plot.keys())+1] = {dic_inv[j].keys()[0]: dic_inv[j][dic_inv[j].keys()[0]]}
            else:
                dic_inv_plot[np.max(dic_inv_plot.keys()) + 1] = {dic_inv[j].keys()[0]: dic_inv[j][dic_inv[j].keys()[0]]}
        for i in dic_crystal.keys():
            if dic_crystal[i]["center"]:
                if not dic_crystal[i]["valid"]:
                    # print(dic_crystal[i])
                    for n_c, c in enumerate(self.rows[dic_crystal[i]["row"]][:]):
                        if c == dic_crystal[i]["id"]:
                            col = n_c
                            if dic_crystal[i]["row"]%2 != 0:
                                col = (n_c*2)+2
                            # print(col)
                            # print(dic_crystal[i]["row"])
                            if (col in self.median_columns.keys()):
                                if (dic_crystal[i]["row"] in self.median_rows.keys()):
                                    # print(self.median_columns[col])
                                    closest_row = self.__clo_rs_app(dic_inv[j][dic_inv[j].keys()[0]][1], self.median_rows[dic_crystal[i]["row"]], self.dist_min_y_list)
                                    closest_col = self.__clo_rs_app(dic_inv[j][dic_inv[j].keys()[0]][0], self.median_columns[col], self.dist_min_x_list)
                                    if closest_row and closest_col:
                                        # print("BINGO")
                                        dic_crystal[self.rows[dic_crystal[i]["row"]][n_c]]["valid"] = True
                                        # print(dic_crystal[self.rows[dic_crystal[i]["row"]][n_c]])
                    
        return dic_crystal, dic_inv_plot
    
    def check_def(self, dic_crystal, dic_inv):
        # print("TN", dic_inv)
        for r_n, r in enumerate(self.rows[:]):
            for c_n, c in enumerate(self.rows[r_n][:]):
                col = c_n
                if r_n%2 != 0:
                    col = (c_n*2)+2
                closest_peak = None
                if (col in self.median_columns.keys()):
                    if (r_n in self.median_rows.keys()):
                        if self.cg == 2 and col == 59:
                                dic_crystal[self.rows[r_n][c_n]]["valid"] = False
                                continue
                        elif self.cg == 2 and col == 5:
                                dic_crystal[self.rows[r_n][c_n]]["valid"] = False
                                continue
                        if not dic_crystal[self.rows[r_n][c_n]]["center"]:
                                # print(self.median_columns[col])
                                # print(self.median_rows[r_n])
                                dist_1 = self.__euqli_dist([-13.257852, 15.744], [self.median_columns[col], self.median_rows[r_n]])
                                dist_2 = self.__euqli_dist([-12.815904, 15.666], [self.median_columns[col], self.median_rows[r_n]])
                                # print("dist_1", dist_1)
                                # print("dist_2", dist_2)
                                closest_peak, c_roi, dic_inv = self.__clo_rs_app_Peak(dic_inv, [self.median_columns[col], self.median_rows[r_n]], self.dist_min_xy_list[self.cg])
                if closest_peak:
                    # print("BINGO2")
                    dic_crystal[self.rows[r_n][c_n]]["center"][c_roi] = [closest_peak]
                    dic_crystal[self.rows[r_n][c_n]]["valid"] = True
                    # print(dic_crystal[self.rows[r_n][c_n]])
                    
        return dic_crystal, dic_inv
                    
    def runSanCheckInv(self, dic_crystal, dic_palone, dic_rdefect, dic_recheck_col):
        dic_recheck = {}
        n_rechecks = 0
        dic_nrch = {} # a joker dictionary
        
        dic_double = {} #a dic just to help with the redefinition of keys and so on
        
        dic_inv = {}
        dic_inv_plot = {}
        dic_inv[0] = {33: [33,33]}
        dic_inv_plot[0] = {33: [33,33]}
        
        dic_crystal, dic_recheck, dic_inv = self.__check_inv(dic_crystal, dic_recheck, dic_nrch, dic_double, self.rows, n_rechecks, dic_inv)

        dic_crystal, dic_inv = self.__f_recheck(dic_recheck, dic_inv, dic_crystal)
                        
        dic_crystal, dic_inv = self.__f_palone(dic_palone, dic_inv, dic_crystal)
        
        dic_crystal = self.__f_rdefect(dic_rdefect, dic_crystal)
                                
        dic_crystal = self.__f_recheckcol(dic_recheck_col, dic_crystal)
        
        dic_crystal = self.__f_checkdouble(dic_double, dic_crystal)
        
        dic_crystal, dic_inv_plot = self.__f_inv(dic_crystal, dic_inv, dic_inv_plot)
        
        return dic_crystal, dic_inv_plot


