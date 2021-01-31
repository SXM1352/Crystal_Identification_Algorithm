# -*- coding: utf-8 -*-
"""
Created on Thu Dec 17 17:29:28 2020

@author: David
"""

from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import numpy as np
#import csv
import pickle



def euqli_dist(p, q, squared=True):
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

def closest_peak(coordinate,dic_crystal): #select the peak which closest to the coordinate given
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
                    dist = euqli_dist(p,coordinate)
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
                dist = euqli_dist(p,coordinate)
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

def f_lud(dic_crystal, val_region, dic_label, lud):
    n_lud = 0
    for i in np.arange(24,-24.1,-0.1): #change depends on cog
        
        for j in np.arange(-24,24.1,0.1):
            p_clo, l_d, cry, p_clo_2, l_d_2, cry_2 = closest_peak((round(i,1),round(j,1)),dic_crystal)
            if l_d > val_region:
                lud[round(i,1),round(j,1)] = None
            else:
                
                dic_label["CLOP"] = dic_crystal[cry]
                dic_label["2CLOP"] = dic_crystal[cry_2]
                QF = l_d/(l_d+l_d_2)
                dic_label["QF"] = QF
                lud[round(i,1),round(j,1)] = dic_label
                dic_label = {}
            n_lud += 1
        #i_lud += 1
    return lud

#with open('output000.csv') as csvfile:
#    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#    for row in spamreader:
#        print(', '.join(row))
         
with open('/home/david.perez/Desktop/dic-crystal-111-checked.pickle', 'rb') as handle:
    dic_crystal_111 = pickle.load(handle)
         
lud_111 = {}
dic_label_111 = {}
#j_lud = 0
val_region_111 = 0.2 #1 for 111, 0.5 for the rest?
lud_111 = f_lud(dic_crystal_111, val_region_111, dic_label_111, lud_111)

    
with open('/home/david.perez/Desktop/dic-LUD-111.pickle', 'wb') as handle:
    pickle.dump(lud_111, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  

print("111 done.")

with open('/home/david.perez/Desktop/dic-crystal-100-checked.pickle', 'rb') as handle:
    dic_crystal_100 = pickle.load(handle)
         
lud_100 = {}
dic_label_100 = {}
#j_lud = 0
val_region_100 = 0.1 #0.2 for 111, 0.1 for the rest?
lud_100 = f_lud(dic_crystal_100, val_region_100, dic_label_100, lud_100)

    
with open('/home/david.perez/Desktop/dic-LUD-100.pickle', 'wb') as handle:
    pickle.dump(lud_100, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
   
print("100 done.")

with open('/home/david.perez/Desktop/dic-crystal-010-checked.pickle', 'rb') as handle:
    dic_crystal_010 = pickle.load(handle)
         
lud_010 = {}
dic_label_010 = {}
#j_lud = 0
val_region_010 = 0.1 #0.2 for 111, 0.1 for the rest?
lud_010 = f_lud(dic_crystal_010, val_region_010, dic_label_010, lud_010)

    
with open('/home/david.perez/Desktop/dic-LUD-010.pickle', 'wb') as handle:
    pickle.dump(lud_010, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    
print("010 done.")

with open('/home/david.perez/Desktop/dic-crystal-000-checked.pickle', 'rb') as handle:
    dic_crystal_000 = pickle.load(handle)
         
lud_000 = {}
dic_label_000 = {}
#j_lud = 0
val_region_000 = 0.1 #0.2 for 111, 0.1 for the rest?
lud_000 = f_lud(dic_crystal_000, val_region_000, dic_label_000, lud_000)

    
with open('/home/david.perez/Desktop/dic-LUD-000.pickle', 'wb') as handle:
    pickle.dump(lud_000, handle, protocol=pickle.HIGHEST_PROTOCOL) 
    
print("000 done.")