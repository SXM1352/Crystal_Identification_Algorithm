# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 19:19:27 2021

@author: David
"""
import numpy as np

class SanCheckCol(object):
    
    def __init__(self, cg, dist_x):
        self.cg = cg

        self.dist_x = dist_x
        
        self.dist_x_v = self.dist_x[self.cg]
        
    def __order_median(self, median_columns):
        sorted_values = sorted(median_columns.values())
        for i,j in enumerate(sorted(median_columns.keys())):
            median_columns[j] = sorted_values[i]
        return median_columns
        
    def __peaks_col23(self, dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c):    
        i_i = 0
        for i in range(2,63,2): #create entries for dict from peaks at 2nd and 3rd layer
            i_r = i
            if self.cg == 1 and i_r == 6:
                all_row_x_c.append(x_arr_all_c)
                all_row_y_c.append(y_arr_all_c)
                x_arr_all_c = []
                y_arr_all_c = []
                
                dic_all_row_x_c[i_i] = dic_x_arr_all_c
                dic_all_row_y_c[i_i] = dic_y_arr_all_c
                dic_x_arr_all_c = {}
                dic_y_arr_all_c = {}
                i_i += 1
                continue
            if self.cg == 1 and i_r == 58:
                all_row_x_c.append(x_arr_all_c)
                all_row_y_c.append(y_arr_all_c)
                x_arr_all_c = []
                y_arr_all_c = []
                
                dic_all_row_x_c[i_i] = dic_x_arr_all_c
                dic_all_row_y_c[i_i] = dic_y_arr_all_c
                dic_x_arr_all_c = {}
                dic_y_arr_all_c = {}
                i_i += 1
                continue
            for j in range(71):
                if j%2 == 0:
                    if dic_crystal[i_r]["center"] and dic_crystal[i_r]["valid"]:
                        for i_cr in dic_crystal[i_r]["center"].keys():
                            x_arr_all_c.append(dic_crystal[i_r]["center"][i_cr][0][0])
                            y_arr_all_c.append(dic_crystal[i_r]["center"][i_cr][0][1])       
                            
                            dic_x_arr_all_c[i_r] = dic_crystal[i_r]["center"][i_cr][0][0]
                            dic_y_arr_all_c[i_r] = dic_crystal[i_r]["center"][i_cr][0][1]
                    i_r += 63 - i_i
                else:
                    if dic_crystal[i_r]["center"] and dic_crystal[i_r]["valid"]:
                        for i_cr in dic_crystal[i_r]["center"].keys():
                            x_arr_all_c.append(dic_crystal[i_r]["center"][i_cr][0][0])
                            y_arr_all_c.append(dic_crystal[i_r]["center"][i_cr][0][1])       
                            
                            dic_x_arr_all_c[i_r] = dic_crystal[i_r]["center"][i_cr][0][0]
                            dic_y_arr_all_c[i_r] = dic_crystal[i_r]["center"][i_cr][0][1]
    
                    i_r += 33 + i_i
            
            #if x_arr_all_c:
            all_row_x_c.append(x_arr_all_c)
            all_row_y_c.append(y_arr_all_c)
            x_arr_all_c = []
            y_arr_all_c = []
            
            dic_all_row_x_c[i_i] = dic_x_arr_all_c
            dic_all_row_y_c[i_i] = dic_y_arr_all_c
            dic_x_arr_all_c = {}
            dic_y_arr_all_c = {}
            i_i += 1
        
        return dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c
    
    def __peaks_col1(self, dic_crystal, dic_x_arr_all_c_1, dic_y_arr_all_c_1, dic_all_row_x_c_1, dic_all_row_y_c_1, x_arr_all_c_1, y_arr_all_c_1, all_row_x_c_1, all_row_y_c_1):    
             
        i_i_1 = 0
        col = 0
        while col < 65:
            label_peak = col
            if self.cg == 1 and col == 59:
                col += 2
                all_row_x_c_1.append(x_arr_all_c_1)
                all_row_y_c_1.append(y_arr_all_c_1)
                dic_all_row_x_c_1[i_i_1] = dic_x_arr_all_c_1
                dic_all_row_y_c_1[i_i_1] = dic_y_arr_all_c_1
                x_arr_all_c_1 = []
                y_arr_all_c_1 = []
                dic_x_arr_all_c_1 = {}
                dic_y_arr_all_c_1 = {}
                i_i_1 += 1
                continue

            for j in range(0,71,2): #rows
                if dic_crystal[label_peak]["center"] and dic_crystal[label_peak]["valid"]:
                    for i_cr in dic_crystal[label_peak]["center"].keys():
                        x_arr_all_c_1.append(dic_crystal[label_peak]["center"][i_cr][0][0])
                        y_arr_all_c_1.append(dic_crystal[label_peak]["center"][i_cr][0][1])       
                        
                        dic_x_arr_all_c_1[label_peak] = dic_crystal[label_peak]["center"][i_cr][0][0]
                        dic_y_arr_all_c_1[label_peak] = dic_crystal[label_peak]["center"][i_cr][0][1]
    
                label_peak += 96
            all_row_x_c_1.append(x_arr_all_c_1)
            all_row_y_c_1.append(y_arr_all_c_1)
            
            dic_all_row_x_c_1[i_i_1] = dic_x_arr_all_c_1
            dic_all_row_y_c_1[i_i_1] = dic_y_arr_all_c_1
            if col == 64:
                pass
            else:
                x_arr_all_c_1 = []
                y_arr_all_c_1 = []
                dic_x_arr_all_c_1 = {}
                dic_y_arr_all_c_1 = {}
            
            if col == 0 or col == 63:
                col += 1
            else:
                col += 2
                
            i_i_1 += 1
        return dic_all_row_x_c_1, dic_all_row_y_c_1, all_row_x_c_1, all_row_y_c_1
    
    def __med_col(self, median_columns, all_row_y_c, all_row_x_c, columnn):
        for kl in range(len(all_row_y_c)): 
            median_x = np.median(all_row_x_c[kl])
            if not np.isnan(median_x):
                median_columns[columnn] = median_x
            if columnn == 0:
                columnn = 1
            elif columnn == 63:
                columnn = 64
            else:
                columnn += 2     
        median_columns = self.__order_median(median_columns)
        
        return median_columns
    
    def __check_peaks_coln(self, dic_crystal, dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn):
        
        orig_col = columnn
        
        dic_double = {} # a joke dictionary to include double points in main dictionary
        dic_nrch = {} # a joker dictionary):
    
        median_columns = self.__med_col(median_columns, all_row_y_c, all_row_x_c, columnn)
        
        columnn = orig_col
        #print(median_columns)
        for kl in range(len(all_row_y_c)): 
            #print("EE", columnn)
            inv_peaks_col_x = []
            inv_peaks_col_y = []
            try:
                median_x = median_columns[columnn]
            except KeyError:
                if columnn == 0:
                    columnn = 1
                elif columnn == 63:
                    columnn = 64
                else:
                    columnn += 2
                continue
            if columnn == 0:
                columnn = 1
            elif columnn == 63:
                columnn = 64
            else:
                columnn += 2

            for jl in all_row_x_c[kl]:
                #print("jl",jl)
                #print(median_x)
                if np.abs(np.diff([jl,median_x])) > self.dist_x_v:
                    
                    #print("x ",all_row_x_c[kl])
                    #print("y ",all_row_y_c[kl])
                    for kk in dic_all_row_x_c[kl].keys():
                        #print("kk",dic_all_row_x_c[kl][kk])
                        if dic_all_row_x_c[kl][kk] == jl:
                          #  invalid_cr = kk
                            if dic_crystal[kk]["center"].keys() > 1: # we need a loop because it is only defined once in dic_all_row
                                VAL = False
                                for i_cr in dic_crystal[kk]["center"].keys():
                                    if np.abs(np.diff([dic_crystal[kk]["center"][i_cr][0][0],median_x])) > 10: #distnace to assure that they do not belong together
                                        for i_cr2 in dic_crystal[kk]["center"].keys():
                                            if i_cr2 != i_cr:
                                                
                                                dic_double[i_cr2] = dic_crystal[kk]["center"][i_cr2] 
                                                
                                        dic_nrch[i_cr] = dic_crystal[kk]["center"][i_cr]        
                                        dic_recheck_col[n_rechecks] = dic_nrch
                                        dic_nrch = {}
                                        n_rechecks += 1
                                        
                                        dic_crystal[kk]["center"] = dic_double
                                        dic_double = {}
                                                
                                    elif np.abs(np.diff([dic_crystal[kk]["center"][i_cr][0][0],median_x])) <= self.dist_x_v:
                                         VAL = True
                                         for i_cr2 in dic_crystal[kk]["center"].keys():
                                            if i_cr2 != i_cr:
                                                inv_peaks_col_x.append(dic_crystal[kk]["center"][i_cr2][0][0])
                                                inv_peaks_col_y.append(dic_crystal[kk]["center"][i_cr2][0][1])
                                        
                                if not VAL:
                                    dic_crystal[kk]["valid"] = False
                                    #jl_y = dic_all_row_y_c[kl][kk]
                             #       print(jl_y)
                             #       print(jl)
                                    for i_cr in dic_crystal[kk]["center"].keys():
                                        inv_peaks_col_x.append(dic_crystal[kk]["center"][i_cr][0][0])
                                        inv_peaks_col_y.append(dic_crystal[kk]["center"][i_cr][0][1])
                                        
                                        
                                
                            else:
                                
                                dic_crystal[kk]["valid"] = False
                                jl_y = dic_all_row_y_c[kl][kk]
                         #       print(jl_y)
                         #       print(jl)
                                inv_peaks_col_x.append(jl)
                                inv_peaks_col_y.append(jl_y)

            for rmm in range(len(inv_peaks_col_y)):
                try:
                    all_row_x_c[kl].remove(inv_peaks_col_x[rmm])
                    all_row_y_c[kl].remove(inv_peaks_col_y[rmm])
                except:
                    pass #it can happen that they are exactly the same and thus from loop twice as much
                    
        return median_columns, dic_crystal, dic_recheck_col
    
    
    def __check_coln(self, dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn): # a joker dictionary):
        
        if columnn == 2:
            dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c = self.__peaks_col23(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c)
        
        elif columnn == 0:
            dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c = self.__peaks_col1(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c)
  
        median_columns, dic_crystal, dic_recheck_col = self.__check_peaks_coln(dic_crystal, dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn)          

        return dic_crystal, median_columns, dic_recheck_col
    
    def __check_median(self, dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c, median_columns, columnn):
        if columnn == 2:
            dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c = self.__peaks_col23(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c)
        
        elif columnn == 0:
            dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c = self.__peaks_col1(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c)
  
        median_columns = self.__med_col(median_columns, all_row_y_c, all_row_x_c, columnn)
        
        return median_columns
    
    def runCheckCol(self, dic_crystal):
        dic_x_arr_all_c = {}
        dic_y_arr_all_c = {}
        dic_all_row_x_c = {}
        dic_all_row_y_c = {}
        
        x_arr_all_c = [] #single iteration
        y_arr_all_c = []
        all_row_x_c = [] #whole list
        all_row_y_c = []
        
        dic_x_arr_all_c_1 = {} #from first layer
        dic_y_arr_all_c_1 = {}
        dic_all_row_x_c_1 = {}
        dic_all_row_y_c_1 = {}
        
        x_arr_all_c_1 = []
        y_arr_all_c_1 = []
        all_row_x_c_1 = []
        all_row_y_c_1 = []
        
        
        median_columns = {}
        columnn_23 = 2
        columnn_1 = 0
        #columns 2 and 3
        median_columns = self.__check_median(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c, median_columns, columnn_23)
        #column 1
        median_columns = self.__check_median(dic_crystal, dic_x_arr_all_c_1, dic_y_arr_all_c_1, dic_all_row_x_c_1, dic_all_row_y_c_1, x_arr_all_c_1, y_arr_all_c_1, all_row_x_c_1, all_row_y_c_1, median_columns, columnn_1)
        
        return median_columns


    def runSanCheckCol(self, dic_crystal):

        dic_x_arr_all_c = {}
        dic_y_arr_all_c = {}
        dic_all_row_x_c = {}
        dic_all_row_y_c = {}
        
        x_arr_all_c = [] #single iteration
        y_arr_all_c = []
        all_row_x_c = [] #whole list
        all_row_y_c = []
        
        dic_x_arr_all_c_1 = {} #from first layer
        dic_y_arr_all_c_1 = {}
        dic_all_row_x_c_1 = {}
        dic_all_row_y_c_1 = {}
        
        x_arr_all_c_1 = []
        y_arr_all_c_1 = []
        all_row_x_c_1 = []
        all_row_y_c_1 = []
        
        dic_recheck_col = {}
        n_rechecks = 0
        
        median_columns = {}
        columnn_23 = 2
        columnn_1 = 0
        #columns 2 and 3
        dic_crystal, median_columns, dic_recheck_col = self.__check_coln(dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn_23)
        #column 1
        dic_crystal, median_columns, dic_recheck_col = self.__check_coln(dic_crystal, dic_x_arr_all_c_1, dic_y_arr_all_c_1, dic_all_row_x_c_1, dic_all_row_y_c_1, x_arr_all_c_1, y_arr_all_c_1, all_row_x_c_1, all_row_y_c_1, dic_recheck_col, n_rechecks, median_columns, columnn_1)


        return dic_crystal, median_columns, dic_recheck_col