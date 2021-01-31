# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 02:51:06 2020

@author: David
"""


import pickle
import numpy as np
import atexit
from time import clock
import time

def secondsToStr(t):
    return "%d:%02d:%02d.%03d" % \
        reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
            [(t*1000,),1000,60,60])

line = "="*40
def log(s, elapsed=None):
    print line
    print secondsToStr(clock()), '-', s
    if elapsed:
        print "Elapsed time:", elapsed
    print line
    print

def endlog():
    end = clock()
    elapsed = end-start
    log("End Program", secondsToStr(elapsed))

def now():
    return secondsToStr(clock())

start = clock()
atexit.register(endlog)
log("Start Program")

def read_data_COG(NVD):
    with open('cog{}test.pickle'.format(NVD), 'rb') as handle:
        cogNVDtest = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        
    with open('dic-LUD-{}.pickle'.format(NVD), 'rb') as handle:
        ludNVD = pickle.load(handle) # 000, 100, 010, 111 
    
    with open('cog{}ref.pickle'.format(NVD), 'rb') as handle:
        cogNVDref = pickle.load(handle) # 000, 100, 010, 111
        
    return cogNVDtest, ludNVD, cogNVDref

cog000test, lud000, cog000ref =  read_data_COG("000") 
cog100test, lud100, cog100ref =  read_data_COG("100") 
cog010test, lud010, cog010ref =  read_data_COG("010") 
cog111test, lud111, cog111ref =  read_data_COG("111") 

with open('cogTest4.pickle', 'rb') as handle:
    cogtest = pickle.load(handle) # 000, 100, 010, 111
    
with open('cogref.pickle', 'rb') as handle:
    cogref = pickle.load(handle) # 000, 100, 010, 111  
 
log("Check Program")

   
def CrystalDict():
    """
    Define Crystal identification dictionary with respective ids for all the peaks based on layer
     
    @return: None
    @rtype:
    """
    m=1
    row=[]
    j=0
    p=0
    rows=[]
    dic_crystal = {}
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
                    dic_crystal[r] = peakii
                else:
                    if n%2 != 0:
                        peakii={
                                'row'         : j,
                                'layer'       : 1,
                                'id'          : r,
                                'center'     : {},
                                'valid'    : False
                                }
                        dic_crystal[r] = peakii
                    else:
                        peakjj={
                                'row'         : j,
                                'layer'       : 2,
                                'id'          : r,
                                'center'     : {},
                                'valid'    : False
                                }
                        dic_crystal[r] = peakjj 
                        
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
                dic_crystal[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)
        
    return rows, dic_crystal

def d_labels(dic_crystal, cogref, lud010, cog010ref, cogtest, cog010test, dic_labels_count_layer1, dic_labels_count_layer2, dic_labels_count_layer3):
    for i, cgt in enumerate(cogref):
        #if all(cgt) == 1: #000 is always 1 and if any is 0, 111 is 0
    #    if cgt[1] == 1 and cgt[2] == 1:
    #    	if lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)] != None: 
    #    	        if dic_crystal[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]]["layer"] == 1:
    #            	    	dic_labels_count_layer1[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]] += 1
    #            	if dic_crystal[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]]["layer"] == 2:
    #                		dic_labels_count_layer2[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]] += 1
    #            	if dic_crystal[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]]["layer"] == 3:
    #                		dic_labels_count_layer3[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]] += 1
        if cgt[1] == 1 and cgt[2] == 1:
        	if lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)] != None and lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["valid"] == True: 
        	        if dic_crystal[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]]["layer"] == 1:
                	    	dic_labels_count_layer1[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]] += 1
                	if dic_crystal[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]]["layer"] == 2:
                    		dic_labels_count_layer2[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]] += 1
                	if dic_crystal[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]]["layer"] == 3:
                    		dic_labels_count_layer3[lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["id"]] += 1
    print("SEcond")        
    for i, cgt in enumerate(cogtest):
        #if all(cgt) == 1: #000 is always 1 and if any is 0, 111 is 0
    #    if cgt[1] == 1 and cgt[2] == 1:
    #        if lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)] != None:
    #                if dic_crystal[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]]["layer"] == 1:
    #                        dic_labels_count_layer1[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]] += 1
    #                if dic_crystal[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]]["layer"] == 2:
    #                        dic_labels_count_layer2[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]] += 1
    #                if dic_crystal[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]]["layer"] == 3:
    #                        dic_labels_count_layer3[lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["id"]] += 1
        if cgt[1] == 1 and cgt[2] == 1:
            if lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)] != None and lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["valid"] == True:
                    if dic_crystal[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]]["layer"] == 1:
                            dic_labels_count_layer1[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]] += 1
                    if dic_crystal[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]]["layer"] == 2:
                            dic_labels_count_layer2[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]] += 1
                    if dic_crystal[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]]["layer"] == 3:
                            dic_labels_count_layer3[lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["id"]] += 1
    
            #print("The crystal selected for this cluster with COG-000 is: ", lud000[round(cog000test[i][0],1),round(cog000test[i][1],1)]["CLOP"]["id"])
            #print("The crystal selected for this cluster with COG-100 is: ", lud100[round(cog100test[i][0],1),round(cog100test[i][1],1)]["CLOP"]["id"])
    #        dic_labels_count[lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["id"]] += 1
    return dic_labels_count_layer1, dic_labels_count_layer2, dic_labels_count_layer3



def d_labels_count(dic_crystal, dic_labels_count_layer1, dic_labels_count_layer2, dic_labels_count_layer3, dic_labels_count):

    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 1:
            dic_labels_count_layer1[i] = 0
    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 2:
            dic_labels_count_layer2[i] = 0
    for i in dic_crystal.keys():
        if dic_crystal[i]["layer"] == 3:
            dic_labels_count_layer3[i] = 0
        
    
    for i in range(3425):
        dic_labels_count[i] = 0
        
    return dic_labels_count_layer1, dic_labels_count_layer2, dic_labels_count_layer3, dic_labels_count


def data_l(dic_labels_count_layer1, dic_labels_count_layer2, dic_labels_count_layer3, data, data2, data3):
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer1.keys()):
        
        data[index][index2] = dic_labels_count_layer1[i]
        index2 += 1
        if index2 == 34:
            index2 = 0
            index += 1
            
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer2.keys()):
        
        data2[index][index2] = dic_labels_count_layer2[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
         
    index = 0
    index2 = 0
    for i in sorted(dic_labels_count_layer3.keys()):
        
        data3[index][index2] = dic_labels_count_layer3[i]
        index2 += 1
        if index2 == 31:
            index2 = 0
            index += 1
    return data, data2, data3    

def save_dic_COG(dic_labels_count_layer1_NVD, dic_labels_count_layer2_NVD, dic_labels_count_layer3_NVD, NVD):
    
    with open('dic-layer1-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(dic_labels_count_layer1_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
    with open('dic-layer2-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(dic_labels_count_layer2_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
    with open('dic-layer3-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(dic_labels_count_layer3_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
    print("save_010")   

def save_data_COG(data_NVD, data2_NVD, data3_NVD, NVD):
    
    print("pickle_NVD")
    with open('data-layer1-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(data_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
    with open('data-layer2-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(data2_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
    with open('data-layer3-{}-valid.pickle'.format(NVD), 'wb') as handle:
        pickle.dump(data3_NVD, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
     
    
rows,dic_crystal = CrystalDict()
data = np.zeros((36,34))
data2 = np.zeros((36,31))
data3 = np.zeros((35,31))

print("Start_000")

dic_labels_count_layer1_000 = {}
dic_labels_count_layer2_000 = {}
dic_labels_count_layer3_000 = {}

dic_labels_count_000 = {}

dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000, dic_labels_count_000 = d_labels_count(dic_crystal, dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000, dic_labels_count_000)

dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000 = d_labels(dic_crystal, cogref, lud010, cog010ref, cogtest, cog010test, dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000) 


save_dic_COG(dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000, "000") 

data_000, data2_000, data3_000 = data_l(dic_labels_count_layer1_000, dic_labels_count_layer2_000, dic_labels_count_layer3_000, data, data2, data3)

save_data_COG(data_000, data2_000, data3_000, "000")

print("Start_010")

dic_labels_count_layer1_010 = {}
dic_labels_count_layer2_010 = {}
dic_labels_count_layer3_010 = {}

dic_labels_count_010 = {}

dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010, dic_labels_count_010 = d_labels_count(dic_crystal, dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010, dic_labels_count_010)

dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010 = d_labels(dic_crystal, cogref, lud010, cog010ref, cogtest, cog010test, dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010) 


save_dic_COG(dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010, "010") 

data_010, data2_010, data3_010 = data_l(dic_labels_count_layer1_010, dic_labels_count_layer2_010, dic_labels_count_layer3_010, data, data2, data3)

save_data_COG(data_010, data2_010, data3_010, "010")

print("Start_100")

dic_labels_count_layer1_100 = {}
dic_labels_count_layer2_100 = {}
dic_labels_count_layer3_100 = {}

dic_labels_count_100 = {}

dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100, dic_labels_count_100 = d_labels_count(dic_crystal, dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100, dic_labels_count_100)

dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100 = d_labels(dic_crystal, cogref, lud010, cog010ref, cogtest, cog010test, dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100) 


save_dic_COG(dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100, "100") 

data_100, data2_100, data3_100 = data_l(dic_labels_count_layer1_100, dic_labels_count_layer2_100, dic_labels_count_layer3_100, data, data2, data3)

save_data_COG(data_100, data2_100, data3_100, "100")

print("Start_111")

dic_labels_count_layer1_111 = {}
dic_labels_count_layer2_111 = {}
dic_labels_count_layer3_111 = {}

dic_labels_count_111 = {}

dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111, dic_labels_count_111 = d_labels_count(dic_crystal, dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111, dic_labels_count_111)

dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111 = d_labels(dic_crystal, cogref, lud010, cog010ref, cogtest, cog010test, dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111) 


save_dic_COG(dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111, "111") 

data_111, data2_111, data3_111 = data_l(dic_labels_count_layer1_111, dic_labels_count_layer2_111, dic_labels_count_layer3_111, data, data2, data3)

save_data_COG(data_111, data2_111, data3_111, "111")



log("End Program")
    
