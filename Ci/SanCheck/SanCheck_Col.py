# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 19:19:27 2021
@author: David
"""
import numpy as np

#class imports

class SanCheckCol(object):
    def __init__(self, cg, dist_x):
        self.cg = cg
        self.dist_x = dist_x
        self.dist_x_v = self.dist_x[self.cg]
        
    def __order_median(self, median_columns):
        """!
        Order the median of the columns, in case some are mixed

        @param median_columns: medians of columns
        @type median_columns: dict

        @return: median_columns
        @rtype: dict
        """
        sorted_values = sorted(median_columns.values())
        for i,j in enumerate(sorted(median_columns.keys())):
            median_columns[j] = sorted_values[i]
        return median_columns
        
    def __peaks_col23(self, dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c):
        """!
        Create entries for dict from peaks at 2nd and 3rd layer

        @param dic_crystal: ids of crystal
        @type dic_crystal: dict
        @param dic_x_arr_all_c: ids of crystals from x column
        @type dic_x_arr_all_c: dict
        @param dic_y_arr_all_c: ids of crystals from y column
        @type dic_y_arr_all_c: dict
        @param dic_all_row_x_c: ids of crystals from x row
        @type dic_all_row_x_c: dict
        @param dic_all_row_y_c: ids of crystals from y row
        @type dic_all_row_y_c: dict
        @param x_arr_all_c: ids of crystals from x column
        @type x_arr_all_c: dict
        @param y_arr_all_c: ids of crystals from y column
        @type y_arr_all_c: dict
        @param all_row_x_c: ids of crystals from x row
        @type all_row_x_c: dict
        @param all_row_y_c: ids of crystals from y row
        @type all_row_y_c: dict
        
        @return: dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c
        @rtype: dict, dict, dict, dict
        """
        i_i = 0
        for i in range(2,63,2): 
            i_r = i
            if self.cg == 2:
                if i_r == 58 or i_r == 6:
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
            if self.cg == 0:
                if i_r == 58 or i_r == 6:
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
        """!
        Create entries for dict from peaks at 1st layer

        @param dic_crystal: ids of crystal
        @type dic_crystal: dict
        @param dic_x_arr_all_c_1: ids of crystals from x column
        @type dic_x_arr_all_c_1: dict
        @param dic_y_arr_all_c_1: ids of crystals from y column
        @type dic_y_arr_all_c_1: dict
        @param dic_all_row_x_c_1: ids of crystals from x row
        @type dic_all_row_x_c_1: dict
        @param dic_all_row_y_c_1: ids of crystals from y row
        @type dic_all_row_y_c_1: dict
        @param x_arr_all_c_1: ids of crystals from x column
        @type x_arr_all_c_1: dict
        @param y_arr_all_c_1: ids of crystals from y column
        @type y_arr_all_c_1: dict
        @param all_row_x_c_1: ids of crystals from x row
        @type all_row_x_c_1: dict
        @param all_row_y_c_1: ids of crystals from y row
        @type all_row_y_c_1: dict
        
        @return: dic_all_row_x_c_1, dic_all_row_y_c_1, all_row_x_c_1, all_row_y_c_1
        @rtype: dict, dict, dict, dict
        """
             
        i_i_1 = 0
        col = 0
        while col < 65:
            label_peak = col
            if self.cg == 2 and col == 59:
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
            # if self.cg == 0 and col == 59:
            #     col += 2
            #     all_row_x_c_1.append(x_arr_all_c_1)
            #     all_row_y_c_1.append(y_arr_all_c_1)
            #     dic_all_row_x_c_1[i_i_1] = dic_x_arr_all_c_1
            #     dic_all_row_y_c_1[i_i_1] = dic_y_arr_all_c_1
            #     x_arr_all_c_1 = []
            #     y_arr_all_c_1 = []
            #     dic_x_arr_all_c_1 = {}
            #     dic_y_arr_all_c_1 = {}
            #     i_i_1 += 1
            #     continue

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

    def __closest(self, cur_pos, positions):
        """!
        Find the x-closest position to the point given from a list
        Input parameters: \

        @param cur_pos: coordinates of point to compare with
        @type cur_pos: list
        @param positions: x-coord candidates to be close
        @type positions: list

        @return: closest_pos with x-coordinates of closest peak
        @rtype: list
        """
        low_dist = float('inf')
        closest_pos = None
        for pos in positions:
            dist = np.abs(np.diff([cur_pos, pos]))
            if dist < low_dist:
                low_dist = dist
                closest_pos = pos
        return closest_pos, low_dist

    def __left_side(self, median_columns, median_x, columnn):
        for i in range(3):
            if columnn == 0:
                median_columns[columnn] = min(median_x)
                median_x.remove(min(median_x))
                columnn = 1
            else:
                if columnn < 5:
                    median_columns[columnn] = min(median_x)
                    median_x.remove(min(median_x))
                    columnn += 2
        return median_columns

    def __inner_side(self, median_columns, median_x, col_list, columnn, pos_col):
        if self.cg == 2 or self.cg == 0:
            n_cols_2 = 0
            n_cols_0 = 0
            low_dist_min = 1.5
        elif self.cg == 3:
            n_cols_2 = 2
            n_cols_0 = 4
            low_dist_min = 3.5
        if columnn == 2:
            for i_n, col in enumerate(col_list):
                col_main, low_dist = self.__closest(pos_col[i_n], median_x)
                #if low_dist < 1.5:
                median_columns[col] = col_main
                # print("col_main", col_main)
                # print(median_x)
                # print(len(median_x))
                median_x.remove(col_main)
                # print(median_x)
                # print(len(median_x))
                j_pos = 0
                j_neg = 0
                for j in range(2+n_cols_2):
                    col_i, low_dist = self.__closest(pos_col[i_n], median_x)
                    # print("col_i", col_i)
                    if low_dist > low_dist_min:
                        pass
                    elif col_i > col_main:
                        median_columns[col + (2*(j_pos+1))] = col_i
                        median_x.remove(col_i)
                        j_pos += 1
                    elif col_i < col_main:
                        median_columns[col - (2*(j_neg+1))] = col_i
                        median_x.remove(col_i)
                        j_neg += 1
        else:
            for i_n, col in enumerate(col_list):
                col_main = median_columns[col]
                j_pos = 0
                j_neg = 0
                for j in range(2+n_cols_0):
                    col_i, low_dist = self.__closest(pos_col[i_n], median_x)
                    if low_dist > low_dist_min:
                        pass
                    elif col_i > col_main:
                        median_columns[col + (j_pos*2+1)] = col_i
                        median_x.remove(col_i)
                        j_pos += 1
                    elif col_i < col_main:
                        median_columns[col - (j_neg*2+1)] = col_i
                        median_x.remove(col_i)
                        j_neg += 1
        return median_columns
                #two closest column to this one and compare which is left and which right
    def __right_side(self, median_columns, median_x, columnn):
        col_list_23 = [62, 60]
        col_list_1 = [64, 63, 61]

        if columnn == 0:
            for j in col_list_1:
                median_columns[j] = max(median_x)
                median_x.remove(max(median_x))

        else:
            for i in col_list_23:
                median_columns[i] = max(median_x)
                median_x.remove(max(median_x))

        return median_columns

    def __med_col(self, median_columns, all_row_y_c, all_row_x_c, columnn):
        #only temporary make the other function global for every cg
        for kl in range(len(all_row_y_c)):
            #if len(all_row_x_c[kl]) > 6:
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

    def __med_col_010(self, median_columns, all_row_y_c, all_row_x_c, columnn):
        """!
        Order the median of the columns, in case some are mixed

        @param median_columns: medians of columns
        @type median_columns: dict
        @param all_row_x_c: ids of crystals from x row
        @type all_row_x_c: dict
        @param all_row_y_c: ids of crystals from y row
        @type all_row_y_c: dict
        @param column: id of column
        @type column: integer

        @return: median_columns
        @rtype: dict
        """
        if self.cg == 2:
            col_list = [14, 26, 38, 50]
            pos_col = [-12, -4, 4, 12]
            median_x = []

            for kl in range(len(all_row_y_c)):
                if len(all_row_x_c[kl]) > 5:
                    median_x.append(np.median(all_row_x_c[kl]))
            median_columns = self.__left_side(median_columns, median_x, columnn) #check they are close enough to reference
            # print("left",median_columns)
            median_columns = self.__inner_side(median_columns, median_x, col_list, columnn, pos_col)
            # print("in",median_columns)
            median_columns = self.__right_side(median_columns, median_x, columnn)
            # print("right", median_columns)
            #median_columns = self.__order_median(median_columns)
        elif self.cg == 0:
            col_list = [14, 26, 38, 50]
            pos_col = [-12, -4, 4, 12]
            median_x = []

            for kl in range(len(all_row_y_c)):
                if len(all_row_x_c[kl]) > 5:
                    median_x.append(np.median(all_row_x_c[kl]))
            median_columns = self.__left_side(median_columns, median_x, columnn) #check they are close enough to reference
            # print("left",median_columns)
            median_columns = self.__inner_side(median_columns, median_x, col_list, columnn, pos_col)
            # print("in",median_columns)
            median_columns = self.__right_side(median_columns, median_x, columnn)
            # print("right", median_columns)
            #median_columns = self.__order_median(median_columns)
        elif self.cg == 3:
            col_list = [8, 20, 32, 44, 56]
            pos_col = [-16, -8, 0, 8, 16]
            median_x = []

            for kl in range(len(all_row_y_c)):
                if len(all_row_x_c[kl]) > 5:
                    median_x.append(np.median(all_row_x_c[kl]))
            # print("med", median_x)
            median_columns = self.__inner_side(median_columns, median_x, col_list, columnn, pos_col)
            # print("in", median_columns)

        return median_columns
    
    def __check_peaks_coln(self, dic_crystal, dic_all_row_x_c, dic_all_row_y_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn):
        """!
        Check peaks with the medians and if they are not close enough "self.dist_x_v"
        they are saved to be rechecked later

        @param dic_crystal: ids of crystal
        @type dic_crystal: dict
        @param dic_all_row_x_c: ids of crystals from x row
        @type dic_all_row_x_c: dict
        @param dic_all_row_y_c: ids of crystals from y row
        @type dic_all_row_y_c: dict
        @param all_row_x_c: ids of crystals from x row
        @type all_row_x_c: dict
        @param all_row_y_c: ids of crystals from y row
        @type all_row_y_c: dict
        
        @param dic_recheck_col: crystal that do not fit the median of the column
        @type dic_recheck_col: dict
        @param n_rechecks: number of peaks which need to be rechecked
        @type n_rechecks: integer
        
        @param median_columns: medians of columns
        @type median_columns: dict
        @param column: id of column
        @type column: integer
        
        @return: median_columns, dic_crystal, dic_recheck_col
        @rtype: dict, dict, dict
        """
        orig_col = columnn
        
        dic_double = {} # a joke dictionary to include double points in main dictionary
        dic_nrch = {} # a joker dictionary):
        if self.cg == 2:
            median_columns = self.__med_col_010(median_columns, all_row_y_c, all_row_x_c, columnn)
        else:
            median_columns = self.__med_col(median_columns, all_row_y_c, all_row_x_c, columnn)
        
        columnn = orig_col
        for kl in range(len(all_row_y_c)): 
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
                if np.abs(np.diff([jl,median_x])) > self.dist_x_v:
                    for kk in dic_all_row_x_c[kl].keys():
                        if dic_all_row_x_c[kl][kk] == jl:
                            if dic_crystal[kk]["center"].keys() > 1: # we need a loop because it is only defined once in dic_all_row
                                VAL = False
                                for i_cr in dic_crystal[kk]["center"].keys():
                                    if np.abs(np.diff([dic_crystal[kk]["center"][i_cr][0][0],median_x])) > 10: #distance to assure that they do not belong together
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

                                    for i_cr in dic_crystal[kk]["center"].keys():
                                        inv_peaks_col_x.append(dic_crystal[kk]["center"][i_cr][0][0])
                                        inv_peaks_col_y.append(dic_crystal[kk]["center"][i_cr][0][1])
                            else:
                                dic_crystal[kk]["valid"] = False
                                jl_y = dic_all_row_y_c[kl][kk]
                                
                                inv_peaks_col_x.append(jl)
                                inv_peaks_col_y.append(jl_y)
            for rmm in range(len(inv_peaks_col_y)):
                try:
                    all_row_x_c[kl].remove(inv_peaks_col_x[rmm])
                    all_row_y_c[kl].remove(inv_peaks_col_y[rmm])
                except:
                    pass #it can happen that they are exactly the same and thus from loop twice as much
                    
        return median_columns, dic_crystal, dic_recheck_col
    
    def __check_coln(self, dic_crystal, dic_x_arr_all_c, dic_y_arr_all_c, dic_all_row_x_c, dic_all_row_y_c, x_arr_all_c, y_arr_all_c, all_row_x_c, all_row_y_c, dic_recheck_col, n_rechecks, median_columns, columnn):
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

        if self.cg == 2:
            median_columns = self.__med_col_010(median_columns, all_row_y_c, all_row_x_c, columnn)
        else:
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