# -*- coding: utf-8 -*-
"""
Created on Sat Jan 16 21:35:03 2021

@author: David
"""
import numpy as np

class SanCheckRow(object):
    
    def __init__(self, cg, dist_y):
        self.cg = cg

        self.dist_y = dist_y
        
        self.dist_y_v = self.dist_y[self.cg]
        
    def __check_median(self, dic_crystal, dic_x_arr_all, dic_y_arr_all, dic_all_row_x, dic_all_row_y, x_arr_all, y_arr_all, all_row_x, all_row_y, median_rows, roww):
        for i in dic_crystal.keys():
            if dic_crystal[i]["center"] and dic_crystal[i]["valid"]:
                row_new = dic_crystal[i]["row"]
                if row_new != roww:
                    dic_all_row_y[roww] = dic_y_arr_all
                    dic_all_row_x[roww] = dic_x_arr_all
                    median_y = np.median(y_arr_all)
                    if not np.isnan(median_y):
                        median_rows[roww] = median_y
                    
                    dic_x_arr_all = {}
                    dic_y_arr_all = {}
                    all_row_x.append(x_arr_all)
                    all_row_y.append(y_arr_all)
                    x_arr_all = []
                    y_arr_all = []
                    roww = row_new 
                if len(dic_crystal[i]["center"].keys()) > 1:
                    for cr in dic_crystal[i]["center"].keys():
                        x_arr_all.append(dic_crystal[i]["center"][cr][0][0])
                        y_arr_all.append(dic_crystal[i]["center"][cr][0][1])
                        dic_y_arr_all[i] = dic_crystal[i]["center"][cr][0][1]
                        dic_x_arr_all[i] = dic_crystal[i]["center"][cr][0][0]
                        
                else:
                    x_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                    y_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1]) 
                    dic_y_arr_all[i] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1] 
                    dic_x_arr_all[i] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0]
                #The last row is defined outside
        dic_all_row_y[roww] = dic_y_arr_all
        dic_all_row_x[roww] = dic_x_arr_all
        median_y = np.median(y_arr_all)
        median_rows[roww] = median_y
        
        return median_rows

    def __check_row(self, dic_crystal, dic_x_arr_all, dic_y_arr_all, dic_all_row_x, dic_all_row_y, x_arr_all, y_arr_all, all_row_x, all_row_y, median_rows, roww):              
                    
        for i in dic_crystal.keys():
            if dic_crystal[i]["center"] and dic_crystal[i]["valid"]:
                row_new = dic_crystal[i]["row"]
                if row_new != roww:
                    dic_all_row_y[roww] = dic_y_arr_all
                    dic_all_row_x[roww] = dic_x_arr_all
                    inv_peaks_col_x_1 = []
                    inv_peaks_col_y_1 = []
                    median_y = np.median(y_arr_all)
                    if not np.isnan(median_y):
                        median_rows[roww] = median_y
                    for jl in y_arr_all:
                      #  # print(np.abs(np.diff([jl,median_x])))
                        if np.abs(np.diff([jl,median_y])) > self.dist_y_v:
                     #       # print("jl",jl)
                            for kk in dic_y_arr_all.keys():
                     #           # print("kk",dic_all_row_x_c_1[kl][kk])
                                if dic_y_arr_all[kk] == jl:
                                    #invalid_cr = kk
                                    dic_crystal[kk]["valid"] = False
                                    jl_x = dic_x_arr_all[kk]
                                    inv_peaks_col_y_1.append(jl)
                                    inv_peaks_col_x_1.append(jl_x)
                                    
                    for rmm in range(len(inv_peaks_col_y_1)):
                        ## print(rmm)
                        try:
                            x_arr_all.remove(inv_peaks_col_x_1[rmm])
                            y_arr_all.remove(inv_peaks_col_y_1[rmm])
                        except:
                            pass
                    
                    dic_x_arr_all = {}
                    dic_y_arr_all = {}
                    all_row_x.append(x_arr_all)
                    all_row_y.append(y_arr_all)
                    x_arr_all = []
                    y_arr_all = []
                    roww = row_new 
                if len(dic_crystal[i]["center"].keys()) > 1:
                    for cr in dic_crystal[i]["center"].keys():
                        x_arr_all.append(dic_crystal[i]["center"][cr][0][0])
                        y_arr_all.append(dic_crystal[i]["center"][cr][0][1])
                        dic_y_arr_all[i] = dic_crystal[i]["center"][cr][0][1]
                        dic_x_arr_all[i] = dic_crystal[i]["center"][cr][0][0]
                        
                else:
                    x_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                    y_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1]) 
                    dic_y_arr_all[i] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1] 
                    dic_x_arr_all[i] = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0]        
        #The last row is defined outside
        dic_all_row_y[roww] = dic_y_arr_all
        dic_all_row_x[roww] = dic_x_arr_all
        inv_peaks_col_x_1 = []
        inv_peaks_col_y_1 = []
        median_y = np.median(y_arr_all)
        median_rows[roww] = median_y
        for jl in y_arr_all:
          #  # print(np.abs(np.diff([jl,median_x])))
            if np.abs(np.diff([jl,median_y])) > self.dist_y_v:
         #       # print("jl",jl)
                for kk in dic_y_arr_all.keys():
         #           # print("kk",dic_all_row_x_c_1[kl][kk])
                    if dic_y_arr_all[kk] == jl:
                        #invalid_cr = kk
                        dic_crystal[kk]["valid"] = False
                        jl_x = dic_x_arr_all[kk]
                        inv_peaks_col_y_1.append(jl)
                        inv_peaks_col_x_1.append(jl_x)
        for rmm in range(len(inv_peaks_col_y_1)):
                ## print(rmm)
                try:
                    x_arr_all.remove(inv_peaks_col_x_1[rmm])
                    y_arr_all.remove(inv_peaks_col_y_1[rmm])
                except:
                    pass
        all_row_x.append(x_arr_all)
        all_row_y.append(y_arr_all)

        return dic_crystal, median_rows
    
    def runCheckRow(self, dic_crystal):

        roww = 0
        x_arr_all = []
        y_arr_all = []
        all_row_x = []
        all_row_y = []
        dic_all_row_x = {}
        dic_all_row_y = {}
        dic_x_arr_all = {}
        dic_y_arr_all = {}
        
        median_rows = {}

        median_rows = self.__check_median(dic_crystal, dic_x_arr_all, dic_y_arr_all, dic_all_row_x, dic_all_row_y, x_arr_all, y_arr_all, all_row_x, all_row_y, median_rows, roww)

        return median_rows
    
    def runSanCheckRow(self, dic_crystal):

        roww = 0
        x_arr_all = []
        y_arr_all = []
        all_row_x = []
        all_row_y = []
        dic_all_row_x = {}
        dic_all_row_y = {}
        dic_x_arr_all = {}
        dic_y_arr_all = {}
        
        median_rows = {}

        dic_crystal, median_rows = self.__check_row(dic_crystal, dic_x_arr_all, dic_y_arr_all, dic_all_row_x, dic_all_row_y, x_arr_all, y_arr_all, all_row_x, all_row_y, median_rows, roww)

        return dic_crystal, median_rows