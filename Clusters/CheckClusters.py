# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:51 2020

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
    with open('/home/david.perez/Desktop/cog{}test.pickle'.format(NVD), 'rb') as handle:
        cogNVDtest = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        
    with open('/home/david.perez/Desktop/dic-LUD-{}.pickle'.format(NVD), 'rb') as handle:
        ludNVD = pickle.load(handle) # 000, 100, 010, 111 
    
    with open('/home/david.perez/Desktop/cog{}ref.pickle'.format(NVD), 'rb') as handle:
        cogNVDref = pickle.load(handle) # 000, 100, 010, 111
        
    return cogNVDtest, ludNVD, cogNVDref

cog000test, lud000, cog000ref =  read_data_COG("000") 
cog100test, lud100, cog100ref =  read_data_COG("100") 
cog010test, lud010, cog010ref =  read_data_COG("010") 
cog111test, lud111, cog111ref =  read_data_COG("111") 

with open('/home/david.perez/Desktop/cogTest4.pickle', 'rb') as handle:
    cogtest = pickle.load(handle) # 000, 100, 010, 111
    
with open('/home/david.perez/Desktop/cogref.pickle', 'rb') as handle:
    cogref = pickle.load(handle) # 000, 100, 010, 111
 
 
log("Check Program")

ssm2 = 0
st2 = 0

ssm = 0
st = 0

ssm3 = 0
st3 = 0

ssm1 = 0
ssm4 = 0
ssm5 = 0
ssm6 = 0
ssm7 = 0
ssm8 = 0
ssm9 = 0
ssm10 = 0

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

def getDuplicatesWithCount(listOfElems):
    ''' Get frequency count of duplicate elements in the given list '''
    dictOfElems = dict()
    # Iterate over each element in list
    for elem in listOfElems:
        # If element exists in dict then increment its value else add it in dict
        if elem in dictOfElems:
            dictOfElems[elem] += 1
        else:
            dictOfElems[elem] = 1    
 
    # Filter key-value pairs in dictionary. Keep pairs whose value is greater than 1 i.e. only duplicate elements from list.
    dictOfElems = { key:value for key, value in dictOfElems.items() if value > 1}
    # Returns a dict of duplicate elements and thier frequency count
    return dictOfElems

dic_labels_count_layer1 = {}
dic_labels_count_layer2 = {}
dic_labels_count_layer3 = {}


rows,dic_crystal = CrystalDict()    
    
dic_labels_count = {}

for i in range(3425):
    dic_labels_count[i] = 0

print("Start")

for i, cgt in enumerate(cogtest):
    stop = False
    #if all(cgt) == 1: #000 is always 1 and if any is 0, 111 is 0
    #if cgt[1] == 1 and cgt[2] == 1:# 000, 100, 010, 111
    if cgt[0] == 1: #all events

        st += 1
        pos000 = None
        pos010 = None
        pos100 = None
        pos111 = None
        
        id000 = None
        id010 = None
        id100 = None
        id111 = None
        
        qf = {}

        if lud100[round(cog100test[i][0],1),round(cog100test[i][1],1)] != None and lud100[round(cog100test[i][0],1),round(cog100test[i][1],1)]["CLOP"]["valid"] == True and cgt[1] == 1:
            pos100 = lud100[round(cog100test[i][0],1),round(cog100test[i][1],1)] #introduce in each iteration
            id100 = pos100["CLOP"]["id"]
            qf[id100] = pos100["QF"]
            
        
        if lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)] != None and lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]["CLOP"]["valid"] == True and cgt[3] == 1:            
            pos111 = lud111[round(cog111test[i][0],1),round(cog111test[i][1],1)]
            id111 = pos111["CLOP"]["id"]
            qf[id111] = pos111["QF"]

        if lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)] != None and lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]["CLOP"]["valid"] == True and cgt[2] == 1:
            pos010 = lud010[round(cog010test[i][0],1),round(cog010test[i][1],1)]
            id010 = pos010["CLOP"]["id"]
            qf[id010] = pos010["QF"]
        
        if lud000[round(cog000test[i][0],1),round(cog000test[i][1],1)] != None and lud000[round(cog000test[i][0],1),round(cog000test[i][1],1)]["CLOP"]["valid"] == True:
            pos000 = lud000[round(cog000test[i][0],1),round(cog000test[i][1],1)]
            id000 = pos000["CLOP"]["id"]
            qf[id000] = pos000["QF"]
        
        # List of strings
        listOfIds = [id100, id111, id010, id000]
# Get a dictionary containing duplicate elements in list and their frequency count
        dictOfElems = getDuplicatesWithCount(listOfIds)     
        for key, value in dictOfElems.items():
            if key != None:
                if value > 1: #the value which is more than once (repeated) is taken
                    dic_labels_count[key] += 1 
                    stop = True
        if stop:
            continue
        
        bestQF = 1. #min(qf.values())
        
        for i in qf.keys():
            if qf[i] < bestQF:
                bestQF = qf[i]
                bestId = i
        try:        
            dic_labels_count[bestId] += 1   
        except:
            print("Peak not valid.")


for i, cgt in enumerate(cogref):
    stop = False
    #if all(cgt) == 1: #000 is always 1 and if any is 0, 111 is 0
    #if cgt[1] == 1 and cgt[2] == 1:
    if cgt[0] == 1:
        #print("The crystal selected for this cluster with COG-000 is: ", lud000[round(cog000test[i][0],1),round(cog000test[i][1],1)]["CLOP"]["id"])
        #print("The crystal selected for this cluster with COG-100 is: ", pos100["CLOP"]["id"])
        st += 1
        pos000 = None
        pos010 = None
        pos100 = None
        pos111 = None
        
        id000 = None
        id010 = None
        id100 = None
        id111 = None
        
        qf = {}

        if lud100[round(cog100ref[i][0],1),round(cog100ref[i][1],1)] != None and lud100[round(cog100ref[i][0],1),round(cog100ref[i][1],1)]["CLOP"]["valid"] == True and cgt[1] == 1:
            pos100 = lud100[round(cog100ref[i][0],1),round(cog100ref[i][1],1)] #introduce in each iteration
            id100 = pos100["CLOP"]["id"]
            qf[id100] = pos100["QF"]
            
        
        if lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)] != None and lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]["CLOP"]["valid"] == True and cgt[3] == 1:            
            pos111 = lud111[round(cog111ref[i][0],1),round(cog111ref[i][1],1)]
            id111 = pos111["CLOP"]["id"]
            qf[id111] = pos111["QF"]

        if lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)] != None and lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]["CLOP"]["valid"] == True and cgt[2] == 1:
            pos010 = lud010[round(cog010ref[i][0],1),round(cog010ref[i][1],1)]
            id010 = pos010["CLOP"]["id"]
            qf[id010] = pos010["QF"]
        
        if lud000[round(cog000ref[i][0],1),round(cog000ref[i][1],1)] != None and lud000[round(cog000ref[i][0],1),round(cog000ref[i][1],1)]["CLOP"]["valid"] == True:
            pos000 = lud000[round(cog000ref[i][0],1),round(cog000ref[i][1],1)]
            id000 = pos000["CLOP"]["id"]
            qf[id000] = pos000["QF"]
        
        # List of strings
        listOfIds = [id100, id111, id010, id000]
# Get a dictionary containing duplicate elements in list and their frequency count
        dictOfElems = getDuplicatesWithCount(listOfIds)     
        for key, value in dictOfElems.items():
            if key != None:
                if value > 1:
                    dic_labels_count[key] += 1 
                    stop = True
        if stop:
            continue
        
        bestQF = 1.#min(qf.values())
        
        for i in qf.keys():
            if qf[i] < bestQF:
                bestQF = qf[i]
                bestId = i
        try:        
            dic_labels_count[bestId] += 1   
        except:
            print("Peak not valid. (in REF)")
            
        
for i in dic_crystal.keys():
    if dic_crystal[i]["layer"] == 1:
        dic_labels_count_layer1[i] = dic_labels_count[i]
for i in dic_crystal.keys():
    if dic_crystal[i]["layer"] == 2:
        dic_labels_count_layer2[i] = dic_labels_count[i]
for i in dic_crystal.keys():
    if dic_crystal[i]["layer"] == 3:
        dic_labels_count_layer3[i] = dic_labels_count[i]    
        
with open('dic-layer1-all-valid.pickle', 'wb') as handle:
    pickle.dump(dic_labels_count_layer1, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
with open('dic-layer2-all-valid.pickle', 'wb') as handle:
    pickle.dump(dic_labels_count_layer2, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
with open('dic-layer3-all-valid.pickle', 'wb') as handle:
    pickle.dump(dic_labels_count_layer3, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
        
        
data = np.zeros((36,34))
data2 = np.zeros((36,31))
data3 = np.zeros((35,31))
print("svae")
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
print("pickle")
with open('data-layer1-all-valid.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
with open('data-layer2-all-valid.pickle', 'wb') as handle:
    pickle.dump(data2, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
with open('data-layer3-all-valid.pickle', 'wb') as handle:
    pickle.dump(data3, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
log("End Program")