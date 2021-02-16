# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:51 2020

@author: David
"""
import cPickle as pickle
import numpy as np
import atexit
from time import clock
import time
import h5py

class C_Cluster(object):
    #we need to sepparate the main() from here, but it is a good start
    def __init__(self, line, start, dic_Events, ):
        self.line = line
        
        self.start = start
        self.dic_Events = dic_Events

    def __secondsToStr(self,t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])
    
    def __log(self, s, elapsed=None):
        print self.line
        print self.__secondsToStr(clock()), '-', s
        if elapsed:
            print "Elapsed time:", elapsed
        print self.line
        print
    
    
    def __endlog(self):
        end = clock()
        elapsed = end-self.start
        self.__log("End Program", self.__secondsToStr(elapsed))
    
    def __now(self):
        return self.__secondsToStr(clock())

    
    def __read_data_COG(self, HVD):
        try:
            with open('/home/david.perez/Desktop/pv{}test.pickle'.format(HVD), 'rb') as handle:
                pvHVDtest = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        except:
            pvHVDtest = -1

        try:
            with open('/home/david.perez/Desktop/cog{}test.pickle'.format(HVD), 'rb') as handle:
                cogHVDtest = pickle.load(handle) # 000, 100, 010, 111 order of columns!!!
        except:
            cogHVDtest = -1
            
        with open('/home/david.perez/Desktop/dic-LUD-{}.pickle'.format(HVD), 'rb') as handle:
            ludHVD = pickle.load(handle) # 000, 100, 010, 111

        with h5py.File("/home/david.perez/Desktop/cog{}ref.hdf5".format(HVD), "r") as f:
            dset = f["data"]
            cogHVDref = dset[:] # 000, 100, 010, 111

        with h5py.File("/home/david.perez/Desktop/pv{}ref.hdf5".format(HVD), "r") as f:
            dset = f["data"]
            pvHVDref = dset[:] # 000, 100, 010, 111
            
        # with open('/home/david.perez/Desktop/pv{}ref.pickle'.format(HVD), 'rb') as handle:
        #     pvHVDref = pickle.load(handle) # 000, 100, 010, 111
        #
        # with open('/home/david.perez/Desktop/cog{}ref.pickle'.format(HVD), 'rb') as handle:
        #     cogHVDref = pickle.load(handle) # 000, 100, 010, 111
            
        return cogHVDtest, pvHVDtest, ludHVD, pvHVDref, cogHVDref

    def __CrystalDict(self):
        """
        Define Crystal identification dictionary with respective ids for all the peaks based on layer

        @return: None
        @rtype:
        """
        m = 1
        row = []
        j = 0
        p = 0
        rows = []
        dic_crystal = {}
        for i in range(3426):
            if i >= (65 * m + 31 * p) and j % 2 == 0:
                rows.append(row)
                # s = 1
                for n, r in enumerate(row):
                    if n == 0 or n == 64:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'pv': []
                        }
                        dic_crystal[r] = peakii
                    else:
                        if n % 2 != 0:
                            peakii = {
                                'row': j,
                                'layer': 1,
                                'id': r,
                                'pv': []
                            }
                            dic_crystal[r] = peakii
                        else:
                            peakjj = {
                                'row': j,
                                'layer': 2,
                                'id': r,
                                'pv': []
                            }
                            dic_crystal[r] = peakjj

                row = []
                j += 1
                p += 1
            elif i >= (65 * m + 31 * p) and j % 2 != 0:
                rows.append(row)
                for r in row:
                    peakkk = {
                        'row': j,
                        'layer': 3,
                        'id': r,
                        'pv': []
                    }
                    dic_crystal[r] = peakkk
                row = []
                j += 1
                m += 1
            else:
                pass
            row.append(i)

        return dic_crystal

    def __getDuplicatesWithCount(self, listOfElems):
        ''' Get frequency count of duplicate elements in the given list '''
        dictOfElems = dict()
        # Iterate over each element in list
        for elem in listOfElems:
            # If element exists in dict then increment its value else add it in dict
            if elem in dictOfElems:
                dictOfElems[elem] += 1
            else:
                dictOfElems[elem] = 1    
     
        # Filter key-value pairs in dictionary. Keep pairs whose value is greater than 1 i.e. only duplicate elements from list. There is no case where two labels are against two labels.
        dictOfElems = { key:value for key, value in dictOfElems.items() if value > 1}
        # Returns a dict of duplicate elements and their frequency count
        return dictOfElems
    
    def __Checker(self, cgt, i, cog000, cog100, cog010, cog111, pv000, pv100, pv010, pv111):
        pos000 = None
        pos010 = None
        pos100 = None
        pos111 = None
        
        id000 = None
        id010 = None
        id100 = None
        id111 = None
        
        qf = {}
        dic_Id = {}

        if self.lud100[round(cog100[i][0],1),round(cog100[i][1],1)] != None and self.lud100[round(cog100[i][0],1),round(cog100[i][1],1)]["CLOP"]["valid"] == True:# and cgt[1] == 1: #if we want to include only valid from hitAnalysis
            pos100 = self.lud100[round(cog100[i][0],1),round(cog100[i][1],1)] #introduce in each iteration
            id100 = pos100["CLOP"]["id"]
            qf[id100] = pos100["QF"] 
            dic_Id["100"] = {"id": id100, "QF": qf[id100], "COORDS": pos100["CLOP"]["center"], "pv": pv100[i]}
        else:
            dic_Id["100"] = {"COORDS":[round(cog100[i][0],1),round(cog100[i][1],1)]}
        
        if self.lud111[round(cog111[i][0],1),round(cog111[i][1],1)] != None and self.lud111[round(cog111[i][0],1),round(cog111[i][1],1)]["CLOP"]["valid"] == True:# and cgt[3] == 1:
            pos111 = self.lud111[round(cog111[i][0],1),round(cog111[i][1],1)]
            id111 = pos111["CLOP"]["id"]
            qf[id111] = pos111["QF"]
            dic_Id["111"] = {"id": id111, "QF": qf[id111], "COORDS": pos111["CLOP"]["center"], "pv": pv111[i]}
        else:
            dic_Id["111"] = {"COORDS":[round(cog111[i][0],1),round(cog111[i][1],1)]}

        if self.lud010[round(cog010[i][0],1),round(cog010[i][1],1)] != None and self.lud010[round(cog010[i][0],1),round(cog010[i][1],1)]["CLOP"]["valid"] == True:# and cgt[2] == 1:
            pos010 = self.lud010[round(cog010[i][0],1),round(cog010[i][1],1)]
            id010 = pos010["CLOP"]["id"]
            qf[id010] = pos010["QF"]
            dic_Id["010"] = {"id": id010, "QF": qf[id010], "COORDS": pos010["CLOP"]["center"], "pv": pv010[i]}
        else:
            dic_Id["010"] = {"COORDS":[round(cog111[i][0],1),round(cog111[i][1],1)]}

        if self.lud000[round(cog000[i][0],1),round(cog000[i][1],1)] != None and self.lud000[round(cog000[i][0],1),round(cog000[i][1],1)]["CLOP"]["valid"] == True:
            pos000 = self.lud000[round(cog000[i][0],1),round(cog000[i][1],1)]
            id000 = pos000["CLOP"]["id"]
            qf[id000] = pos000["QF"]
            dic_Id["000"] = {"id": id000, "QF": qf[id000], "COORDS": pos000["CLOP"]["center"], "pv": pv000[i]}
        else:
            dic_Id["000"] = {"COORDS":[round(cog111[i][0],1),round(cog111[i][1],1)]}
        # List of strings
        listOfIds = [id100, id111, id010, id000]

# Get a dictionary containing duplicate elements in list and their frequency count
        dictOfElems = self.__getDuplicatesWithCount(listOfIds) 
        
        return qf, dictOfElems, dic_Id
            
    def __Repetition_of_Labels(self, key, dic_Id, dic_Events_Counts):
        COG = {}

        COG["000"] = False
        COG["100"] = False
        COG["010"] = False
        COG["111"] = False
        try:
            if key == dic_Id["000"]["id"]:
                COG["000"] = True
        except:
            pass
        try:
            if key == dic_Id["100"]["id"]:
                COG["100"] = True
        except:
            pass
        try:
            if key == dic_Id["010"]["id"]:
                COG["010"] = True
        except:
            pass
        try:
            if key == dic_Id["111"]["id"]:
                COG["111"] = True
        except:
            pass
        for i in self.dic_Events.keys():
            if self.dic_Events[i] == COG:
                dic_Events_Counts[i] += 1
                
        return COG, dic_Events_Counts      
            
            
            
    def __Counter(self, dic_cluster, dic_Events_Counts, cog, dic_labels_count, cog000, cog100, cog010, cog111, pv000, pv100, pv010, pv111): #CHEEECKK
        #stop = False
        for i, cgt in enumerate(cog[self.init_event:self.final_event]):
            stop = False
            dic_cluster[i] = {}
            #if all(cgt) == 1: #000 is always 1 and if any is 0, 111 is 0
            #if cgt[1] == 1 and cgt[2] == 1:# 000, 100, 010, 111
            if cgt[0] == 1: #all events #this filter can actuaaly be done later with dic_Id
                QF_final = 1.
                QF_2_final = -1
                COORD_final = -1
                COORD_2_final = -1
                COG_final = -1
                COG_2_final = -1
                PV_final = -1
                PV_2_final = -1
                id_2 = "-1"
                
                qf, dictOfElems, dic_Id = self.__Checker(cgt, i, cog000, cog100, cog010, cog111, pv000, pv100, pv010, pv111)
                for key, value in dictOfElems.items():
                    if key != None:
                        if value > 1: #the value which is more than once (repeated) is taken
                            dic_labels_count[key] += 1 
                            stop = True
                            dic_cluster[i]["id"] = key
                            COG, dic_Events_Counts = self.__Repetition_of_Labels(key, dic_Id, dic_Events_Counts)
                            for j in COG.keys():
                                if COG[j]:
                                    try:
                                        if dic_Id[j]["QF"] < QF_final:
                                            QF_final = dic_Id[j]["QF"]
                                            COORD_final = dic_Id[j]["COORDS"]
                                            COG_final = j
                                            PV_final = dic_Id[j]["pv"]
                                    except KeyError:
                                        pass #it could be that dic_Id does not have the corresponding key
                                        
                                else:
                                    try:
                                        if dic_Id[j]["QF"] < QF_2_final:
                                            QF_2_final = dic_Id[j]["QF"]
                                            COORD_2_final = dic_Id[j]["COORDS"]
                                            id_2 = dic_Id[j]["id"]
                                            COG_2_final = j
                                            PV_2_final = dic_Id[j]["pv"]
                                    except KeyError:
                                        pass #it could be that dic_Id does not have the corresponding key
                                        
                            dic_cluster[i]["QF"] = QF_final
                            dic_cluster[i]["COORDS"] = COORD_final
                            dic_cluster[i]["COG"] = COG_final
                            dic_cluster[i]["pv"] = PV_final
                            dic_cluster[i]["COG_ALL"] = COG

                            if id_2 != "-1": #we only define those variables if they are representatives
                                dic_cluster[i]["id_2"] = id_2
                                dic_cluster[i]["QF_2"] = QF_2_final
                                dic_cluster[i]["COORDS_2"] = COORD_2_final
                                dic_cluster[i]["COG_2"] = COG_2_final
                                dic_cluster[i]["pv_2"] = PV_2_final

                            else: #when not, the cog is shown as -1
                                dic_cluster[i]["COG_2"] = COG_2_final
                           #SEPARATE TRUE FROM FALSE TO USE IT FOR FILLING THE DICTIONARY
                            
#ONLY THOSE WHICH HAVE A DEFINITION CAN BE ADDED TO THE DICT; IF THEIR COORDINATES DOES NOT HAVE A VALUE FROM THE LUT

                if not stop:
                    bestQF = 1. #min(qf.values())
                    bestQF_2 = 1.
                    bestId = "-1"
                    bestId_2 = "-1"
                    COORD_final = -1
                    COORD_final_2 = -1
                    COG_final = -1
                    COG_final_2 = -1
                    PV_final = -1
                    PV_final_2 = -1

                    for j in dic_Id.keys():
                        try:
                            if dic_Id[j]["QF"] < bestQF:
                                bestQF_2 = bestQF
                                bestId_2 = bestId
                                COORD_final_2 = COORD_final
                                COG_final_2 = COG_final
                                PV_final_2 = PV_final

                                bestQF = dic_Id[j]["QF"]
                                bestId = dic_Id[j]["id"]
                                COORD_final = dic_Id[j]["COORDS"]
                                COG_final = j
                                PV_final = dic_Id[j]["pv"]

                            elif dic_Id[j]["QF"] < bestQF_2:
                                bestQF_2 = dic_Id[j]["QF"]
                                bestId_2 = dic_Id[j]["id"]
                                COORD_final_2 = dic_Id[j]["COORDS"]
                                COG_final_2 = j
                                PV_final_2 = dic_Id[j]["pv"]
                        except KeyError:
                            pass #it could be that dic_Id does not have the corresponding key
                    if bestId != "-1":  #we only define those variables if they are representatives
                        dic_labels_count[bestId] += 1

                        dic_cluster[i]["id"] = bestId
                        dic_cluster[i]["QF"] = bestQF
                        dic_cluster[i]["COORDS"] = COORD_final
                        dic_cluster[i]["COG"] = COG_final
                        dic_cluster[i]["pv"] = PV_final
                        COG, dic_Events_Counts = self.__Repetition_of_Labels(bestId, dic_Id, dic_Events_Counts)
                        dic_cluster[i]["COG_ALL"] = COG
                        print("QF")
                        if bestId_2 != "-1":
                            dic_cluster[i]["id_2"] = bestId_2
                            dic_cluster[i]["QF_2"] = bestQF_2
                            dic_cluster[i]["COORDS_2"] = COORD_final_2
                            dic_cluster[i]["COG_2"] = COG_final_2
                            dic_cluster[i]["pv_2"] = PV_final_2


                    else: #when not we show only the coordinates that did not find any COG (111 is selected as it is the one which covers more area and it is easier to understand visually)
                        dic_cluster[i]["COORDS"] = dic_Id["111"]["COORDS"]
                        print("Event out of range.")
        return dic_Events_Counts, dic_labels_count, dic_cluster
    
    def __Counts_in_layers(self, dic_labels_count):
        dic_labels_count_layer1 = {}
        dic_labels_count_layer2 = {}
        dic_labels_count_layer3 = {}
        
        dic_crystal = self.__CrystalDict()
                
        for i in dic_crystal.keys():
            if dic_crystal[i]["layer"] == 1:
                dic_labels_count_layer1[i] = dic_labels_count[i]
        for i in dic_crystal.keys():
            if dic_crystal[i]["layer"] == 2:
                dic_labels_count_layer2[i] = dic_labels_count[i]
        for i in dic_crystal.keys():
            if dic_crystal[i]["layer"] == 3:
                dic_labels_count_layer3[i] = dic_labels_count[i]
        with open('dic-layer1-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(dic_labels_count_layer1, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
        with open('dic-layer2-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(dic_labels_count_layer2, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)
        with open('dic-layer3-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
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
        with open('data-layer1-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('data-layer2-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(data2, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27)  
        with open('data-layer3-all{}-valid.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(data3, handle, protocol=pickle.HIGHEST_PROTOCOL)   #protocol to make it faster it selects last protocol available for current python version (important in py27) 

    def __PV_in_layers(self, dic_cluster):
        data_cluster_pv_layer1 = []
        data_cluster_pv_layer2 = []
        data_cluster_pv_layer3 = []
        # data_cluster_pv_total = [] one can just concatenate the other lists

        dic_crystal = self.__CrystalDict()  # so we have the pv from each crystal

        for i in dic_cluster.keys():
            if len(dic_cluster[i].keys()) > 2:
                dic_crystal[dic_cluster[i]['id']]['pv'].append(dic_cluster[i]['pv'])
                if dic_crystal[dic_cluster[i]['id']]["layer"] == 1:
                    data_cluster_pv_layer1.append(dic_cluster[i]['pv'])

                elif dic_crystal[dic_cluster[i]['id']]["layer"] == 2:
                    data_cluster_pv_layer2.append(dic_cluster[i]['pv'])

                elif dic_crystal[dic_cluster[i]['id']]["layer"] == 3:
                    data_cluster_pv_layer3.append(dic_cluster[i]['pv'])

        with h5py.File('datapv-layer1-{}-valid.hdf5'.format("ALL"), 'w') as f:
            dset = f.create_dataset("data", (len(data_cluster_pv_layer1),), chunks=True)

            for i in range(0, len(data_cluster_pv_layer1), dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = data_cluster_pv_layer1[i: i + dset.chunks[0]]

        with h5py.File('datapv-layer2-{}-valid.hdf5'.format("ALL"), 'w') as f:
            dset = f.create_dataset("data", (len(data_cluster_pv_layer2),), chunks=True)

            for i in range(0, len(data_cluster_pv_layer2), dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = data_cluster_pv_layer2[i: i + dset.chunks[0]]

        with h5py.File('datapv-layer3-{}-valid.hdf5'.format("ALL"), 'w') as f:
            dset = f.create_dataset("data", (len(data_cluster_pv_layer3),), chunks=True)

            for i in range(0, len(data_cluster_pv_layer3), dset.chunks[0]):
                dset[i: i + dset.chunks[0]] = data_cluster_pv_layer3[i: i + dset.chunks[0]]

        print("pickle")
        with open('datapv-{}-valid.pickle'.format("ALL"), 'wb') as handle:
            pickle.dump(dic_crystal, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Events_Counts(self, dic_Events_Counts):
        with open('dic-Events{}-Counts.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(dic_Events_Counts, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def __save_Dic_Cluster(self, dic_cluster):
        with open('dic-{}cluster.pickle'.format(self.final_event), 'wb') as handle:
            pickle.dump(dic_cluster, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)
    def runCluster(self):

        atexit.register(self.__endlog)
        self.__log(self.line, "Start Program")
        
        cog000test, pv000test, self.lud000, pv000ref, cog000ref =  self.__read_data_COG("000") 
        cog100test, pv100test, self.lud100, pv100ref, cog100ref =  self.__read_data_COG("100") 
        cog010test, pv010test, self.lud010, pv010ref, cog010ref =  self.__read_data_COG("010") 
        cog111test, pv111test, self.lud111, pv111ref, cog111ref =  self.__read_data_COG("111") 

        try:
            with open('/home/david.perez/Desktop/cogTest4.pickle', 'rb') as handle:
                cogtest = pickle.load(handle) # 000, 100, 010, 111
        except:
            self.__log("Events are not split into ref and test.")
            cogtest = -1

        with h5py.File("/home/david.perez/Desktop/cogRef.hdf5", "r") as f:
            dset = f["data"]
            cogref = dset[:] # 000, 100, 010, 111
        # with open('/home/david.perez/Desktop/cogRef.pickle', 'rb') as handle:
        #     cogref = pickle.load(handle) # 000, 100, 010, 111
         
        self.__log("Check Program")
        
        #Explanation of these factor, to obtain statistics!!
        #self.dic_Events = {"ALL": {"000":True, "100": True, "010": True, "111": True}, "100_111_010": {"000":False, "100": True, "010": True, "111": True}, "100_111_000": {"000":True, "100": True, "010": False, "111": True}, "010_111_000": {"000":True, "100": False, "010": True, "111": True}, "010_100_000": {"000":True, "100": True, "010": True, "111": False}, "two_010_100": {"000":False, "100": True, "010": True, "111": False}, "two_010_111": {"000":False, "100": False, "010": True, "111": True}, "two_100_111": {"000":False, "100": True, "010": False, "111": True}, "two_000_111": {"000":True, "100": False, "010": False, "111": True}, "two_000_010": {"000":True, "100": False, "010": True, "111": False}, "two_000_100": {"000":True, "100": True, "010": False, "111": False}, "QF_000": {"000":True, "100": False, "010": False, "111": False} ,"QF_100": {"000":False, "100": True, "010": False, "111": False}, "QF_010": {"000":False, "100": False, "010": True, "111": False}, "QF_111": {"000":False, "100": False, "010": False, "111": True}}

    #    for i_event in range(0,5): #when we want to split it (not so much use of the RAM)
        dic_Events_Counts = {}

        for j in self.dic_Events.keys():
            dic_Events_Counts[j] = 0

        dic_cluster = {}

        # self.init_event = (i_event) * (29946785)
        # self.final_event = (i_event + 1) * (29946785)
        self.init_event = 0
        self.final_event = len(cogref)

        # for j in range(len(cogref[self.init_event:self.final_event])): #len(cogtest) has to be added in case we split the data
        #     clusterjj={
        #         'id'        : -1,
        #         'COORDS'    : {},
        #         'COG'       : "-1",
        #         'pv'        : -1,
        #         'QF'        : -1,
        #         'id_2'      : -1,
        #         'COORDS_2'  : {},
        #         'COG_2'     : "-1",
        #         'pv_2'      : -1,
        #         'QF_2'      : -1,
        #         'COG_ALL'   : {}
        #         }
        #     dic_cluster[j] = clusterjj

        dic_labels_count = {}

        for i in range(3425):
            dic_labels_count[i] = 0

        print("Start")
        #dic_Events_Counts, dic_labels_count, dic_cluster = self.__Counter(dic_cluster, dic_Events_Counts, cogtest, dic_labels_count, cog000test, cog100test, cog010test, cog111test)

        dic_Events_Counts, dic_labels_count, dic_cluster = self.__Counter(dic_cluster, dic_Events_Counts, cogref, dic_labels_count, cog000ref, cog100ref, cog010ref, cog111ref, pv000ref, pv100ref, pv010ref, pv111ref)

        self.__Counts_in_layers(dic_labels_count)

        self.__PV_in_layers(dic_cluster)

        self.__save_Events_Counts(dic_Events_Counts)

        self.__save_Dic_Cluster(dic_cluster)

        self.__log("SAVED")

        self.__log("End Program")