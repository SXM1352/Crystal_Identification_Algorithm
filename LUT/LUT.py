# -*- coding: utf-8 -*-
__author__ = 'david.perez.gonzalez'
"""
LUT.py provides a frame to create the look up tables and store
the information about the closest peaks to each grid point.
"""
import cPickle as pickle
import os
from matplotlib.collections import PolyCollection, LineCollection
# from scipy.spatial  import ConvexHull
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import Delaunay
import argparse

class LUD():
    def __init__(self, decimals, init_event, final_event, selected_HVD, pathtodirectory):
        # self.precision_grid = 2
        self.decimals = decimals # 0.01
        self.HVD_list = ["000", "010", "100", "111"]
        self.val_region_HVD_list = [0.1, 0.1, 0.1, 0.1] #[0.2, 0.2, 0.2, 0.3]
        self.n_roi = [36, 30, 30, 25]
        self.selected_HVD = int(selected_HVD)
        self.pathtodirectory = pathtodirectory
        self.init_event = init_event
        self.final_event = final_event

        self.pathtodirectoryReadLUD = 'dic-LUD/'
        # self.pathtodirectoryReadHDF5 = 'hdf5Data/'
        self.pathtodirectoryCheck = 'dic-checked/'

        self.pathtodirectoryRead = self.pathtodirectory + self.pathtodirectoryCheck

        self.pathtodirectorySave = self.pathtodirectory + self.pathtodirectoryReadLUD

    def __in_hull(self, p, hull):
        """
        Test if points in `p` are in `hull`

        `p` should be a `NxK` coordinates of `N` points in `K` dimensions
        `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of the
        coordinates of `M` points in `K`dimensions for which Delaunay triangulation
        will be computed
        """
        if not isinstance(hull, Delaunay):
            hull = Delaunay(hull)

        return hull.find_simplex(p) >= 0

    def __hull_ROI(self, roi):
        if not isinstance(roi,Delaunay):
            hull = Delaunay(roi)
        return hull

    def __calculate_Hull(self, dic_crystal_roi, cg):
        hull_list = []
        for roi_nr in range(self.n_roi[cg]):
            points_roi = []
            for id in dic_crystal_roi.keys():
                try:
                    print("DER BUMS HIER IST REAL:", dic_crystal_roi[id]["roi"])
                except:
                    print("DEN BUMS GIBT ES NICHT!!!!")
                if dic_crystal_roi[id]["valid"] and dic_crystal_roi[id]["center"]:
                    if len(dic_crystal_roi[id]['roi']) > 1 or len(dic_crystal_roi[id]["center"].keys()) > 1:
                        pass
                    elif dic_crystal_roi[id]['roi'][0] == roi_nr:
                        points_roi.append(dic_crystal_roi[id]['center'][dic_crystal_roi[id]['center'].keys()[0]][0])
            hull_list.append(self.__hull_ROI(np.array(points_roi)))
        return hull_list

    def __euqli_dist(self, p, q, squared=False):
        # Calculates the euclidean distance, the "ordinary" distance between two
        # points
        #
        # The standard Euclidean distance can be squared in order to place
        # progressively greater weight on objects that are farther apart. This
        # frequently used in optimization problems in which distances only have
        # to be compared.
        if squared:
            return ((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2)
        else:
            return np.sqrt(((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2))

    def __closest_peak(self, coordinate,dic_crystal): #select the peak which closest to the coordinate given
        low_dist = float('inf')
        low_dist_2 = None
        closest_peak = None
        crystal_2 = None
        crystal = None
        closest_peak_2 = None
    #    Valid = False
    #    Valid_2 = False #we have it already in peak_dic
        for i in dic_crystal.keys():
            if dic_crystal[i]["center"]:
                #Peaks.append(dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0])
    #    for p in Peaks:
    #        closest(Centers[roi],dic_rows[cc][0])
                if len(dic_crystal[i]["center"].keys()) > 1:
                    for peak in dic_crystal[i]["center"].keys():
                        p = dic_crystal[i]["center"][peak][0]
                        dist = self.__euqli_dist(p,coordinate)
                        if crystal != i:
                            if dist < low_dist:
                                low_dist_2 = low_dist
                                closest_peak_2 = closest_peak
                                crystal_2 = crystal
                                low_dist = dist
                                closest_peak = p
                                crystal = i

                            elif dist < low_dist_2:
                                low_dist_2 = dist
                                closest_peak_2 = p
                                crystal_2 = i
                        else:
                            if dist < low_dist:
                                low_dist = dist
                                closest_peak = p
                                crystal = i
                else:
                    p = dic_crystal[i]["center"][dic_crystal[i]["center"].keys()[0]][0]
                    dist = self.__euqli_dist(p,coordinate)
                    if dist < low_dist:
                        low_dist_2 = low_dist
                        closest_peak_2 = closest_peak
                        crystal_2 = crystal
                        low_dist = dist
                        closest_peak = p
                        crystal = i

                    elif dist < low_dist_2:
                        low_dist_2 = dist
                        closest_peak_2 = p
                        crystal_2 = i

    #    if dic_crystal[crystal]["valid"]:
    #        Valid = True
    #    else:
    #        Valid = False
    #
    #    if dic_crystal[crystal_2]["valid"]:
    #        Valid_2 = True
    #    else:
    #        Valid_2 = False

        return closest_peak, low_dist, crystal, closest_peak_2, low_dist_2, crystal_2

    def __f_lud(self, cg, dic_crystal, val_region, dic_label, lud, precision_grid, decimals):
        n_lud = 0
        print("DAMDAMN")
        hull_list = self.__calculate_Hull(dic_crystal, cg)
        print("DAMDAMN111111")
        for i in np.arange(self.init_event, self.final_event, -decimals):#24,-24.1,-decimals): #change depends on cog

            for j in np.arange(-24,24+decimals,decimals):
                p_clo, l_d, cry, p_clo_2, l_d_2, cry_2 = self.__closest_peak((round(i,precision_grid),round(j,precision_grid)),dic_crystal)
                into = False
                if l_d < 1: #0: now set to one to activate Hull
                    for cH in hull_list:
                        inside = self.__in_hull(np.array([[round(i,precision_grid),round(j,precision_grid)]]), cH)

                        if inside[0]:
                            into = True
                            break
                if l_d < val_region or into:
                    if l_d_2 != 0:
                        QF = l_d/(l_d+l_d_2)
                        dic_label["CLOP"] = dic_crystal[cry]
                        dic_label["2CLOP"] = dic_crystal[cry_2]

                        if 'ghost' in dic_label["CLOP"].keys():
                            QF = QF + (QF*0.2)

                        dic_label["QF"] = QF
                        lud[round(i, precision_grid), round(j, precision_grid)] = dic_label
                        dic_label = {}
                    else:
                        QF = 0
                        dic_label["CLOP"] = dic_crystal[cry]
                        dic_label["2CLOP"] = dic_crystal[cry_2]

                        dic_label["QF"] = QF
                        lud[round(i, precision_grid), round(j, precision_grid)] = dic_label
                        dic_label = {}
                        # print(round(i,precision_grid),round(j,precision_grid))
                        # print(l_d)
                        # print("l_2", l_d_2)
                        # print(lud[round(i, precision_grid), round(j, precision_grid)] )
                else:
                    lud[round(i, precision_grid), round(j, precision_grid)] = None
                n_lud += 1
            #i_lud += 1
        print("DAMDAMN22222222")
        return lud

    def runLUD(self):
        if self.selected_HVD == -1:
            n_HVD = 4
            fixed_cg = False
        else:
            n_HVD = 1
            fixed_cg = True
        for cg in range(n_HVD):
            if fixed_cg:
                cg = self.selected_HVD  # 0 for 000, 1 for 100, 2 for 010, 3 for 111
            HVD = self.HVD_list[cg]
            val_region_HVD = self.val_region_HVD_list[cg]
            precision_grid = len(self.decimals.split(".")[1])
            decimals = float(self.decimals)

            with open(
                    '{}dic-crystal-{}-checked.pickle'.format(self.pathtodirectoryRead, HVD),
                    'rb') as handle:
                dic_crystal_HVD = pickle.load(handle)

            lud_HVD = {}
            dic_label_HVD = {}
            print("Ist heir ein Bugg?")
            # print(dic_crystal_HVD.keys())
            lud_HVD = self.__f_lud(cg, dic_crystal_HVD, val_region_HVD, dic_label_HVD, lud_HVD, precision_grid, decimals)
            print("Anscheinend nicht :)")
            CHECK_FOLDER = os.path.isdir(self.pathtodirectorySave)
            # If folder doesn't exist, then create it.
            if not CHECK_FOLDER:
                os.makedirs(self.pathtodirectorySave)
                print("created folder : ", self.pathtodirectorySave)

            with open(
                    '{}dic-LUD-{}-{}.pickle'.format(self.pathtodirectorySave, HVD, self.final_event),
                    'wb') as handle:
                pickle.dump(lud_HVD, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

            print("done.")

def main():
    print("333333333333")
    parser = argparse.ArgumentParser()
    print("4444444444444")
    parser.add_argument('--HVD N', dest='HVD', help='Specifiy the HVD algorithm to show  \
                                                         (N where N= 0 (=000), 1 (=100), 2 (=010), 3 (=111) or -1 for ALL)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                             directory where to read the files from')
    parser.add_argument('--initEvent', dest='initEvent', help='Specifiy the first event  \
                                             (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--finalEvent', dest='finalEvent', help='Specifiy the last event  \
                                                 (N where N=0,1,2,..., finalEvent)')
    parser.add_argument('--precision', dest='decimals', help='Specifiy the precision of the lut \
                                                     e.g.: "0.01" or "0.1".')
    print("55555555555555555555")
    args = parser.parse_args()
    print("6666666666666")
    decimals, init_event, final_event, selected_HVD, pathtodirectory = args.decimals, int(args.initEvent), int(args.finalEvent), int(args.HVD), args.fileDirect
    print("777777777777777")
    LUT = LUD(decimals, init_event, final_event, selected_HVD, pathtodirectory)
    print("888888888888888")
    LUT.runLUD()
    print("99999999999999999999")

if __name__=='__main__':
    print("11111111")
    main()
    print("222222222")