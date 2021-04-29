# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 19:25:49 2021

@author: David
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as pch
from matplotlib.colors import LogNorm
import cPickle as pickle

class SanCheckPlot(object):
    
    def __init__(self, cg, Ref_Sections, ludHVD, dist_min_y_list, dist_min_x_list):
        self.cg = cg
        self.Ref_Sections = Ref_Sections
        
        self.ludHVD = ludHVD
        
        self.dist_min_y_list = dist_min_y_list
        self.dist_min_x_list = dist_min_x_list

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
        return closest_rc, low_dist
    
    def __final_check_plot(self, dic_crystal, median_columns, dic_inv_plot):
        
        roww = 0
        x_arr_all = []
        y_arr_all = []
        all_row_x = []
        all_row_y = []
        
        dic_columns_x = {}
        dic_columns_y = {}

        dic_columns_x_roi = {'col_12':{}, 'col_3':{}}
        dic_columns_y_roi = {'col_12':{}, 'col_3':{}}

        for co in median_columns.keys():
            dic_columns_x[co] = []
            dic_columns_y[co] = []
        for i in dic_crystal.keys():
    
    #        x_al = np.array(Extract_x(dic_rows[ij][0]))
    #        y_al = np.array(Extract_y(dic_rows[ij][0]))
    
            if dic_crystal[i]["center"] and dic_crystal[i]["valid"]:

                row_new = dic_crystal[i]["row"]
                if row_new != roww:
                    all_row_x.append(x_arr_all)
                    all_row_y.append(y_arr_all)
                    x_arr_all = []
                    y_arr_all = []
                    roww = row_new

                if len(dic_crystal[i]["center"].keys()) > 1:
                    pass
    #                for cr in dic_crystal[i]["center"].keys():
    #                    x_arr_all.append(dic_crystal[i]["center"][cr][0][0])
    #                    y_arr_all.append(dic_crystal[i]["center"][cr][0][1])
    #                    closest_col = clo_rs(cg, dic_crystal[i]["center"][cr][0][0], median_columns)
    #                    if closest_col or closest_col == 0:
    #                        dic_columns_x[closest_col].append(dic_crystal[i]["center"][cr][0][0])
    #                        dic_columns_y[closest_col].append(dic_crystal[i]["center"][cr][0][1])
                else:
                    try:
                        if len(dic_crystal[i]["roi"]) > 1:
                            pass
                        else:
                            # print(dic_crystal[i])
                            x_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                            y_arr_all.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])

                            closest_col, low_dist = self.__clo_rs(
                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0], median_columns,
                                self.dist_min_x_list)
                            if closest_col or closest_col == 0:
                                dic_columns_x[closest_col].append(
                                    dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                dic_columns_y[closest_col].append(
                                    dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                            else:
                                if self.cg == 0 or self.cg == 2 or low_dist > 0.4:
                                    dic_crystal[i]["valid"] = False
                            if dic_crystal[i]["valid"]:
                                if 'col_12' in dic_crystal[i].keys():
                                    if dic_crystal[i]['col_12'] % 2 != 0 or dic_crystal[i]['col_12'] == 0 or \
                                            dic_crystal[i]['col_12'] == 64:
                                        if dic_crystal[i]['col_12'] in dic_columns_x_roi['col_12'].keys():
                                            dic_columns_x_roi['col_12'][dic_crystal[i]['col_12']].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                            dic_columns_y_roi['col_12'][dic_crystal[i]['col_12']].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                                        else:
                                            dic_columns_x_roi['col_12'][dic_crystal[i]['col_12']] = []
                                            dic_columns_y_roi['col_12'][dic_crystal[i]['col_12']] = []
                                            dic_columns_x_roi['col_12'][dic_crystal[i]['col_12']].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                            dic_columns_y_roi['col_12'][dic_crystal[i]['col_12']].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                                    else:
                                        if dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1) in \
                                                dic_columns_x_roi['col_3'].keys():
                                            dic_columns_x_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                            dic_columns_y_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                                        else:
                                            dic_columns_x_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)] = []
                                            dic_columns_y_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)] = []
                                            dic_columns_x_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                            dic_columns_y_roi['col_3'][
                                                dic_crystal[i]['col_12'] - ((dic_crystal[i]['col_12'] / 2) + 1)].append(
                                                dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                                if 'col_3' in dic_crystal[i].keys():
                                    if dic_crystal[i]['col_3'] in dic_columns_x_roi['col_3'].keys():
                                        dic_columns_x_roi['col_3'][dic_crystal[i]['col_3']].append(
                                            dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                        dic_columns_y_roi['col_3'][dic_crystal[i]['col_3']].append(
                                            dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                                    else:
                                        dic_columns_x_roi['col_3'][dic_crystal[i]['col_3']] = []
                                        dic_columns_y_roi['col_3'][dic_crystal[i]['col_3']] = []
                                        dic_columns_x_roi['col_3'][dic_crystal[i]['col_3']].append(
                                            dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0])
                                        dic_columns_y_roi['col_3'][dic_crystal[i]['col_3']].append(
                                            dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1])
                    except:
                        pass

        #The last row is defined outside
        all_row_x.append(x_arr_all)
        all_row_y.append(y_arr_all)
    
        fig, ax = plt.subplots(figsize=(10, 10))
        
        if self.ludHVD:#ludHVD?
            x_lud = []
            y_lud = []
            for i in self.ludHVD.keys():
                if self.ludHVD[i]:
                    x_lud.append(i[0])
                    y_lud.append(i[1])
           
            plt.scatter(x_lud, y_lud)

        if self.Ref_Sections.size != 0:
            ref_total_x = self.Ref_Sections[0][:, 0]
            ref_total_y = self.Ref_Sections[0][:, 1]
            for ref in self.Ref_Sections[1:]:
                 ref_total_y = np.concatenate((ref_total_y, ref[:, 1]), axis=0)
                 ref_total_x = np.concatenate((ref_total_x, ref[:, 0]), axis=0)

            hist1 = ax.hist2d(ref_total_x, ref_total_y, bins=1000, range=[[-24,24],[-24,24]], norm=LogNorm())
            fig.colorbar(hist1[3], ax=ax)

        for kl in range(len(all_row_y)):
            plt.plot(all_row_x[kl],all_row_y[kl], '-ok', mfc='C1', mec='C1')
            
        # for kl in dic_columns_x.keys():
        #     plt.plot(dic_columns_x[kl],dic_columns_y[kl], '-ok', mfc='C1', mec='C1')

        for kl in dic_columns_x_roi['col_3'].keys():
            # indexes = range(len(dic_columns_y_roi['col_3'][kl]))
            # indexes.sort(key=dic_columns_y_roi['col_3'][kl].__getitem__)
            # sorted_y = map(dic_columns_y_roi['col_3'][kl].__getitem__, indexes)
            # sorted_x = map(dic_columns_x_roi['col_3'][kl].__getitem__, indexes)
            plt.plot(dic_columns_x_roi['col_3'][kl],dic_columns_y_roi['col_3'][kl], '-ok', mfc='C1', mec='C1')

        for kl in dic_columns_x_roi['col_12'].keys():
            # indexes = range(len(dic_columns_y_roi['col_12'][kl]))
            # indexes.sort(key=dic_columns_y_roi['col_12'][kl].__getitem__)
            # sorted_y = map(dic_columns_y_roi['col_12'][kl].__getitem__, indexes)
            # sorted_x = map(dic_columns_x_roi['col_12'][kl].__getitem__, indexes)
            plt.plot(dic_columns_x_roi['col_12'][kl], dic_columns_y_roi['col_12'][kl], '-ok', mfc='C1', mec='C1')


        for inv in dic_inv_plot.keys():
            print(dic_inv_plot[inv], inv)
            plt.plot(dic_inv_plot[inv][dic_inv_plot[inv].keys()[0]][0],dic_inv_plot[inv][dic_inv_plot[inv].keys()[0]][1], ".", color="r") 
        
        for i in dic_crystal.keys(): #check where there are two or more, one color, if invalid, but points, red, one point and valid, green, all the rows connected
            if dic_crystal[i]["valid"] and dic_crystal[i]["center"]: #look for bug in 010 with valid true but no center
                try:
                    if len(dic_crystal[i]["center"].keys()) > 1:
                        for cr in dic_crystal[i]["center"].keys():
                            dic_crystal[i]["ghost"] = 'QF=QF+QF*0.2'
                            plt.plot(dic_crystal[i]["center"][cr][0][0],dic_crystal[i]["center"][cr][0][1], ".", color="b")# mfc="C1")
                    elif len(dic_crystal[i]["roi"]) > 1:
                        dic_crystal[i]["ghost"] = '(ALONE)QF=QF+QF*0.2'
                        plt.plot(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0], dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1], ".",
                                 color="dodgerblue")  # mfc="C1")
                    else:
                        print(dic_crystal[i])
                        plt.plot(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0], dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1], ".", color="g")#mfc="C1")
                except:
                    print(dic_crystal[i])
                    plt.plot(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0],
                             dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1], ".",
                             color="g")  # mfc="C1")
            else:
                pass
                if dic_crystal[i]["center"]:
                    if len(dic_crystal[i]["center"].keys()) > 1:
                        for cr in dic_crystal[i]["center"].keys():
                            plt.plot(dic_crystal[i]["center"][cr][0][0],dic_crystal[i]["center"][cr][0][1], ".", color="r")#mfc="C2")
                    else:
                        plt.plot(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][0],dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0][1], ".", color="r")#mfc="C1")
       
        x_size = 3.8016
        y_size = 3.2
        pix_x = [-21.95982,-18.04018,-13.95982,-10.04018,-5.95982, -2.04018, 2.04018,5.98982,10.04018,13.95982,18.04018,21.95982]
        pix_y = [21.6704,18.3296,13.6704,10.3296,5.6704,2.3296,-2.3296,-5.6704,-10.3296,-13.6704,-18.3296,-21.6704]
        
        for pix_x_i in pix_x:
            for pix_y_i in pix_y:
                rect = pch.Rectangle((pix_x_i-x_size/2,pix_y_i-y_size/2),x_size,y_size, linewidth=0.5, edgecolor="dimgray",facecolor="none")
                ax.add_patch(rect)
                
        plt.xlabel("x")
        plt.ylabel("y")
        plt.xlim(-24,24)
        plt.ylim(-24,24)
        plt.show()
        
        return dic_crystal
        
    def runSanCheckPlot(self, dic_crystal, median_columns, dic_inv):

        dic_crystal = self.__final_check_plot(dic_crystal, median_columns, dic_inv)

        return dic_crystal