__author__ = 'florian.mueller'

"""
Modified by David 200629

Modified by David 210129 to include photon values
"""

import logging
import numpy as np
import os
from ConfigParser import ConfigParser
from config import config

class BasicCluster:
    def __init__(self, fname, ini_file=config().monocal_path+"CreateData.ini"):
        self._column_dict = {"stackid": 2,
                             "timestampcluster": 3,
                             "clustersize": 4,
                             "clusterflag": 5,
                             "photonsum": 6,
                             "angerx": 7,
                             "angery": 8,
                             "crystalbin": 9,
                             "crystalenergy": 10,
                             "likelihood": 11,
                             "photonstart": 12,
                             "nbphotonvalues": 144,
                             "timestampsstart": 156,
                             "nbtimestamps" : 36,
                             "channelstart" : 3,
                             "nbchannels": 1,
                             "mainchannelid": 2,
                             "cogpositionsstart": 192,
                             "nbcogpos": 8,
                             "000x": 200, # x and y from COG HVD
                             "000y": 201,
                             "100x": 202,
                             "100y": 203,
                             "010x": 204,
                             "010y": 205,
                             "110x": 206,
                             "110y": 207,
                             "001x": 208,
                             "001y": 209,
                             "101x": 210,
                             "101y": 211,
                             "011x": 212,
                             "011y": 213,
                             "111x": 214,
                             "111y": 215,
                             "pv000": 216, #photon values from COG HVD
                             "pv100": 217,
                             "pv010": 218,
                             "pv110": 219,
                             "pv001": 220,
                             "pv101": 221,
                             "pv011": 222,
                             "pv111": 223
                             }
        self._tofpet = True
        self._single_read = True

        if ini_file is not None:
            self._config_read(ini_file)

        if self._single_read:
            """
            file is only read once and split into the different parts afterwards
            """

            if self._tofpet:
                file = np.genfromtxt(fname, dtype=float, delimiter=',', skip_header=1)
                self._stackID = file[:, self._column_dict.get("stackid")].copy().astype(int)
                self._timeStampCluster = file[:, self._column_dict.get("timestampcluster")].copy().astype(int)
                self._channels = np.concatenate(file[:,[range(self._column_dict.get("channelstart"),self._column_dict.get("channelstart")+self._column_dict.get("nbchannels"))]].copy().astype(int))
                self._photons = np.concatenate(file[:, [range(self._column_dict.get("photonstart"), self._column_dict.get("photonstart") + self._column_dict.get("nbphotonvalues"))]].copy())
                self._timeStamps = np.concatenate(file[:, [range(self._column_dict.get("timestampsstart"), self._column_dict.get("timestampsstart") + self._column_dict.get("nbtimestamps"))]].copy().astype(int))
            else:
                file = np.genfromtxt(fname, dtype=float, delimiter=',')
                self._stackID = file[:, self._column_dict.get("stackid")].copy().astype(int)
                self._timeStampCluster = file[:, self._column_dict.get("timestampcluster")].copy().astype(int)
                self._clusterSize = file[:, self._column_dict.get("clustersize")].copy().astype(int)
                self._clusterFlag = file[:, self._column_dict.get("clusterflag")].copy().astype(int)
                self._photonSum = file[:, self._column_dict.get("photonsum")].copy().astype(int)
                self._angerX = file[:, self._column_dict.get("angerx")].copy()
                self._angerY = file[:, self._column_dict.get("angery")].copy()
                self._crystalBin = file[:, self._column_dict.get("crystalbin")].copy().astype(int)
                self._crystalEnergy = file[:, self._column_dict.get("crystalenergy")].copy().astype(int)
                self._likelihood = file[:, self._column_dict.get("likelihood")].copy().astype(int)
                self._photons = np.concatenate(file[:, [range(self._column_dict.get("photonstart"), self._column_dict.get("photonstart") + self._column_dict.get("nbphotonvalues"))]].copy())
                self._timeStamps = np.concatenate(file[:, [range(self._column_dict.get("timestampsstart"), self._column_dict.get("timestampsstart") + self._column_dict.get("nbtimestamps"))]].copy().astype(int))
                self._COGpositions = np.concatenate(file[:, [range(self._column_dict.get("cogpositionsstart"), self._column_dict.get("cogpositionsstart") + self._column_dict.get("nbcogpos"))]].copy().astype(int))
                self._000x = file[:, self._column_dict.get("000x")].copy()
                self._000y = file[:, self._column_dict.get("000y")].copy()
                self._100x = file[:, self._column_dict.get("100x")].copy()
                self._100y = file[:, self._column_dict.get("100y")].copy()
                self._010x = file[:, self._column_dict.get("010x")].copy()
                self._010y = file[:, self._column_dict.get("010y")].copy()
                self._110x = file[:, self._column_dict.get("110x")].copy()
                self._110y = file[:, self._column_dict.get("110y")].copy()
                self._001x = file[:, self._column_dict.get("001x")].copy()
                self._001y = file[:, self._column_dict.get("001y")].copy()
                self._101x = file[:, self._column_dict.get("101x")].copy()
                self._101y = file[:, self._column_dict.get("101y")].copy()
                self._011x = file[:, self._column_dict.get("011x")].copy()
                self._011y = file[:, self._column_dict.get("011y")].copy()
                self._111x = file[:, self._column_dict.get("111x")].copy()
                self._111y = file[:, self._column_dict.get("111y")].copy()
                self._pv000 = file[:, self._column_dict.get("pv000")].copy()
                self._pv100 = file[:, self._column_dict.get("pv100")].copy()
                self._pv010 = file[:, self._column_dict.get("pv010")].copy()
                self._pv110 = file[:, self._column_dict.get("pv110")].copy()
                self._pv001 = file[:, self._column_dict.get("pv001")].copy()
                self._pv101 = file[:, self._column_dict.get("pv101")].copy()
                self._pv011 = file[:, self._column_dict.get("pv011")].copy()
                self._pv111 = file[:, self._column_dict.get("pv111")].copy()

        else:
            if self._tofpet:
                self._stackID = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("stackid"))
                self._timeStampCluster = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("timestampcluster"))
                self._photons = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=range(self._column_dict.get("photonstart"), self._column_dict.get("photonstart") + self._column_dict.get("nbphotonvalues"), 1))
                self._timeStamps = np.genfromtxt(fname, dtype=int, delimiter=",", usecols=range(self._column_dict.get("timestampsstart"), self._column_dict.get("timestampsstart") + self._column_dict.get("nbtimestamps"), 1))
                self._channels = np.genfromtxt(fname, dtype=int, delimiter=",", usecols=range(self._column_dict.get("channelstart"), self._column_dict.get("channelstart") + self._column_dict.get("nbchannels"), 1))
            else:
                self._stackID = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("stackid"), invalid_raise = False) # "invalid_raise = False" means if there is a line causing problems it is not taken into account
                self._timeStampCluster = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("timestampcluster"), invalid_raise = False)
                self._clusterSize = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("clustersize"), invalid_raise = False)
                self._clusterFlag = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("clusterflag"), invalid_raise = False)
                self._photonSum = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("photonsum"), invalid_raise = False)
                self._angerX = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("angerx"), invalid_raise = False)
                self._angerY = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("angery"), invalid_raise = False)
                self._crystalBin = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("crystalbin"), invalid_raise = False)
                self._crystalEnergy = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("crystalenergy"), invalid_raise = False)
                self._likelihood = np.genfromtxt(fname, dtype=int, delimiter=',', usecols=self._column_dict.get("likelihood"), invalid_raise = False)
                self._photons = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=range(self._column_dict.get("photonstart"),self._column_dict.get("photonstart")+self._column_dict.get("nbphotonvalues"), 1), invalid_raise = False)
                self._timeStamps = np.genfromtxt(fname, dtype=int, delimiter=",", usecols=range(self._column_dict.get("timestampsstart"),self._column_dict.get("timestampsstart")+self._column_dict.get("nbtimestamps"), 1), invalid_raise = False)
                self._COGpositions = np.genfromtxt(fname, dtype=int, delimiter=",", usecols=range(self._column_dict.get("cogpositionsstart"),self._column_dict.get("cogpositionsstart")+self._column_dict.get("nbcogpos"), 1), invalid_raise = False)
                self._000x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("000x"), invalid_raise = False)
                self._000y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("000y"), invalid_raise = False)
                self._100x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("100x"), invalid_raise = False)
                self._100y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("100y"), invalid_raise = False)
                self._010x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("010x"), invalid_raise = False)
                self._010y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("010y"), invalid_raise = False)
                self._110x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("110x"), invalid_raise = False)
                self._110y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("110y"), invalid_raise = False)
                self._001x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("001x"), invalid_raise = False)
                self._001y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("001y"), invalid_raise = False)
                self._101x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("101x"), invalid_raise = False)
                self._101y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("101y"), invalid_raise = False)
                self._011x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("011x"), invalid_raise = False)
                self._011y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("011y"), invalid_raise = False)
                self._111x = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("111x"), invalid_raise = False)
                self._111y = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("111y"), invalid_raise = False)
                self._pv000 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv000"), invalid_raise = False)
                self._pv100 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv100"), invalid_raise = False)
                self._pv010 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv010"), invalid_raise = False)
                self._pv110 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv110"), invalid_raise = False)
                self._pv001 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv001"), invalid_raise = False)
                self._pv101 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv101"), invalid_raise = False)
                self._pv011 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv011"), invalid_raise = False)
                self._pv111 = np.genfromtxt(fname, dtype=float, delimiter=',', usecols=self._column_dict.get("pv111"), invalid_raise = False)

    def _config_read(self, config_file):
        config = ConfigParser(allow_no_value=True)
        config.read(config_file)
        self._single_read = config.get("parameters","single_read")
        self._tofpet = config.get("options","tofpet")
        for column in config.items("columns"):
            if column[0] in self._column_dict:
                self._column_dict[str(column[0])] = int(column[1].encode('UTF8'))
            else:
                logging.error("cannot interpret the given parameter value "+str(column[0]))


    def getPhotons(self, row, col="option"):
        if col != "option" and 0 <= col < self._photons.shape[1] and 0 <= row <= self._photons.shape[0]:
            return self._photons[row][col]
        elif col != "option":
            logging.error("#col or #row out of range, cluster has a shape of: %s", self._photons.shape)
        elif 0 <= row <= self._photons.shape[0]:
            return self._photons[row]
        else:
            logging.error("cannot handle, cluster has a shape of: %s", self._photons.shape)

    def getPhotonSum(self, row):
        if 0 <= row < self._photonSum.shape[0]:
            return self._photonSum[row]
        else:
            logging.error("row out of range, length is %s", self._photonSum.shape[0])
            
    def getPhotonValueCOGArray000(self):
        pvcog000 = []
        pvcog000.append(self._pv000)
        pvcog000 = np.asanyarray(pvcog000)
        return pvcog000

    def getPhotonValueCOGArray100(self):
        pvcog100 = []
        pvcog100.append(self._pv100)
        pvcog100 = np.asanyarray(pvcog100)
        return pvcog100
    
    def getPhotonValueCOGArray010(self):
        pvcog010 = []
        pvcog010.append(self._pv010)
        pvcog010 = np.asanyarray(pvcog010)
        return pvcog010
    
    def getPhotonValueCOGArray110(self):
        pvcog110 = []
        pvcog110.append(self._pv110)
        pvcog110 = np.asanyarray(pvcog110)
        return pvcog110
    
    def getPhotonValueCOGArray001(self):
        pvcog001 = []
        pvcog001.append(self._pv001)
        pvcog001 = np.asanyarray(pvcog001)
        return pvcog001
    
    def getPhotonValueCOGArray101(self):
        pvcog101 = []
        pvcog101.append(self._pv101)
        pvcog101 = np.asanyarray(pvcog101)
        return pvcog101
    
    def getPhotonValueCOGArray011(self):
        pvcog011 = []
        pvcog011.append(self._pv011)
        pvcog011 = np.asanyarray(pvcog011)
        return pvcog011
    
    def getPhotonValueCOGArray111(self):
        pvcog111 = []
        pvcog111.append(self._pv111)
        pvcog111 = np.asanyarray(pvcog111)
        return pvcog111

    def getAngerPosition(self):
        angerX = []
        angerY = []
        angerX.append(self._angerX)
        angerY.append(self._angerY)
        angerX = np.asanyarray(angerX)
        angerY = np.asanyarray(angerY)
        return angerX, angerY
    
    def getCOGPositionArray000(self):
        cog000XY = np.empty((len(self._000x),2), dtype=float)
        for i in range(len(self._000x)):
            cog000XY[i,0] = self._000x[i]
            cog000XY[i,1] = self._000y[i]
        return cog000XY
    def getCOGPositionArray100(self):
        cog100XY = np.empty((len(self._100x),2), dtype=float)
        for i in range(len(self._100x)):
            cog100XY[i,0] = self._100x[i]
            cog100XY[i,1] = self._100y[i]
        return cog100XY
    def getCOGPositionArray010(self):
        cog010XY = np.empty((len(self._010x),2), dtype=float)
        for i in range(len(self._010x)):
            cog010XY[i,0] = self._010x[i]
            cog010XY[i,1] = self._010y[i]
        return cog010XY
    def getCOGPositionArray110(self):
        cog110XY = np.empty((len(self._110x),2), dtype=float)
        for i in range(len(self._110x)):
            cog110XY[i,0] = self._110x[i]
            cog110XY[i,1] = self._110y[i]
        return cog110XY
    def getCOGPositionArray001(self):
        cog001XY = np.empty((len(self._001x),2), dtype=float)
        for i in range(len(self._001x)):
            cog001XY[i,0] = self._001x[i]
            cog001XY[i,1] = self._001y[i]
        return cog001XY
    def getCOGPositionArray101(self):
        cog101XY = np.empty((len(self._101x),2), dtype=float)
        for i in range(len(self._101x)):
            cog101XY[i,0] = self._101x[i]
            cog101XY[i,1] = self._101y[i]
        return cog101XY
    def getCOGPositionArray011(self):
        cog011XY = np.empty((len(self._011x),2), dtype=float)
        for i in range(len(self._011x)):
            cog011XY[i,0] = self._011x[i]
            cog011XY[i,1] = self._011y[i]
        return cog011XY
    def getCOGPositionArray111(self):
        cog111XY = np.empty((len(self._111x),2), dtype=float)
        for i in range(len(self._111x)):
            cog111XY[i,0] = self._111x[i]
            cog111XY[i,1] = self._111y[i]
        return cog111XY

    def getAngerPositionArray(self):
        angerXY = np.empty((len(self._angerX),2), dtype=float)
        for i in range(len(self._angerX)):
            angerXY[i,0] = self._angerX[i]
            angerXY[i,1] = self._angerY[i]
        return angerXY

    def getPhotonSumSpecific(self,row):
        if 0<= row < self._photons.shape[0]:
            helper = Positioning()
            mainDie = int(helper.posIndexPixeltoDie(np.argmax(self._photons[row])))
            logging.debug("main Die is %s", mainDie)
            photonsum = 0
            pixels = helper.allPosIndexPixelofDie(mainDie)
            if self._photons[row][pixels[0]] >= 0:  # dies are just read out completely, so it's enough to check one pixel
                for i in range(0,4):
                    photonsum += self._photons[row][pixels[i]]
            for die in range(0,16):
                if helper.diesAreNeighbors(mainDie, die):  #equals == True
                    pixels = helper.allPosIndexPixelofDie(die)
                    if pixels[0] >= 0: # dies are just read out completely, so it's enough to check one pixel
                        for i in range(0,4):
                            photonsum += self._photons[row][pixels[i]]
                logging.debug("%s and %s are neighbors. Cumulated photonsum until now: %s", mainDie, die, photonsum)
            logging.debug("specific photonsum is %s instead of %s", photonsum, self._photonSum[row])
            return photonsum
        else:
            logging.error("cannot handle, cluster has a shape of: %s", self._photons.shape)

    def normalizeCluster(self):
        for i in range(0, self._photons.shape[0] - 1):
            for j in range(0,64):
                if self._photons[i][j] != -1:
                    self._photons[i][j] = self._photons[i][j] / self._photonSum[i]

    def normalizeClusterSpecific(self):
        for row in range(0, self._photons.shape[0]-1):
            helper = Positioning()
            mainDie = int(helper.posIndexPixeltoDie(np.argmax(self._photons[row])))
            photonsum = self.getPhotonSumSpecific(row)
            pixels = helper.allPosIndexPixelofDie(mainDie)
            if self._photons[row][pixels[0]] >= 0:  # dies are just read out completely, so it's enough to check one pixel
                for i in range(0,4):
                    self._photons[row][pixels[i]] = self._photons[row][pixels[i]]/photonsum
            for die in range(0,16):
                pixels = helper.allPosIndexPixelofDie(die)
                if self._photons[row][pixels[0]] >= 0:  # dies are just read out completely, so it's enough to check one pixel
                    if helper.diesAreNeighbors(mainDie, die):  #equals == True
                        for i in range(0,4):
                            self._photons[row][pixels[i]] = self._photons[row][pixels[i]]/photonsum
                    else:
                        if die != mainDie:
                            for i in range(0,4):
                                self._photons[row][pixels[i]] = 0

    def sortClusterGeneral(self, stack, object):
        tmp_array = []
        for i in range(0, object.shape[0]):
            if self._stackID[i] == stack:
                tmp_array.append(object[i])
        return np.asanyarray(tmp_array)
    
    def sortClusterTimeStamp(self, stack):
        return self.sortClusterGeneral(stack, self._timeStampCluster)

    def sortClusterPhotons(self, stack):
        return self.sortClusterGeneral(stack, self._photons)

    def sortClusterTimeStampDies(self, stack):
        return self.sortClusterGeneral(stack, self._timeStamps)
    
    def sortPhotonValuesCOG000(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray000())
    def sortPhotonValuesCOG100(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray100())
    def sortPhotonValuesCOG010(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray010())
    def sortPhotonValuesCOG110(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray110())
    def sortPhotonValuesCOG001(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray001())
    def sortPhotonValuesCOG101(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray101())
    def sortPhotonValuesCOG011(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray011())
    def sortPhotonValuesCOG111(self, stack):
        return self.sortClusterGeneral(stack, self.getPhotonValueCOGArray111())       
    
    def sortClusterCOGPositions(self, stack):
        return self.sortClusterGeneral(stack, self._COGpositions)
    
    def sortClusterCOGPositions000(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray000())
    def sortClusterCOGPositions100(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray100())
    def sortClusterCOGPositions010(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray010())
    def sortClusterCOGPositions110(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray110())
    def sortClusterCOGPositions001(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray001())
    def sortClusterCOGPositions101(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray101())
    def sortClusterCOGPositions011(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray011())
    def sortClusterCOGPositions111(self, stack):
        return self.sortClusterGeneral(stack, self.getCOGPositionArray111())    

    def sortClusterAngerPositions(self, stack):
        return self.sortClusterGeneral(stack, self.getAngerPositionArray())

    def sortClusterChannels(self, stack):
        return self.sortClusterGeneral(stack, self._channels)

    def filterClusterByMainPixel(self, mainPixel="option", stack="option"):
        tmp_array = []
        if mainPixel == "option":
            logging.error("input of MainPixel is needed, use MainPixelHist to obtain the value")
        if stack=="option":
            stack = 3
            logging.info("Stack was set to default value 3")
        for row in range(0, self._photons.shape[0]-1):
            if self._stackID[row] == stack and mainPixel == np.argmax(self._photons[row]):
                tmp_array.append(self._photons[row])
        return np.asanyarray(tmp_array)

    def filterClusterByMainDie(self, mainDie="option", stack="option"):
        tmp_array = []
        if mainDie == "option":
            logging.error("input of MainDie is needed, use MainDieHist to obtain the value")
        if stack=="option":
            stack = 3
            logging.info("Stack was set to default value 3")
        helper = Positioning()
        for row in range(0, self._photons.shape[0]-1):
            if self._stackID[row] == stack and mainDie == helper.posIndexPixeltoDie(np.argmax(self._photons[row])):
                tmp_array.append(self._photons[row])
        return np.asanyarray(tmp_array)



class Positioning:
    def __init__(self):
        self._tile_length = 32.6
        self._pix_size = self._tile_length/8.
        #self.pos_xy=np.empty([64,2])
        #self.posIndexPixelto_xy()

    def posIndextoCol(self, posIndexPixel):
        return posIndexPixel % 8 + 1

    def posIndextoRow(self, posIndexPixel):
        return posIndexPixel / 8 + 1

    def posIndexPixelto_xy(self):
        self._tile_length= 32.6
        self._pix_size= self._tile_length/8.
        self.pos_xy=np.empty([64,2])
        for i in range(0,64):
            self.pos_xy[i][0]= -self._tile_length/2 + self._pix_size/2 + (self.posIndextoCol(i)-1)*self._pix_size
            self.pos_xy[i][1]= -self._tile_length/2 + self._pix_size/2 + (self.posIndextoRow(i)-1)*self._pix_size

    def posIndexPixelto_x(self, pixel):
        return -self._tile_length/2 + self._pix_size/2 + (self.posIndextoCol(pixel)-1)*self._pix_size

    def posIndexPixelto_y(self, pixel):
        return -self._tile_length/2 + self._pix_size/2 + (self.posIndextoRow(pixel)-1)*self._pix_size

    def posIndexPixeltoDie(self, posIndexPixel):
        mainDieCol = round(self.posIndextoCol(posIndexPixel)/2.)
        mainDieRow = round(self.posIndextoRow(posIndexPixel)/2.)
        return mainDieCol+4.0*mainDieRow-5

    def allPosIndexPixelofDie(self,posIndexDie):
        pixels = []
        pixels.append(0 + 2 * posIndexDie) #first pixel - index 0...
        pixels.append(1 + 2 * posIndexDie)
        pixels.append(8 + 2 * posIndexDie)
        pixels.append(9 + 2 * posIndexDie)
        if posIndexDie >3:
            for i in range(0,4):
                pixels[i]+=8
        if posIndexDie >7:
            for i in range(0,4):
                pixels[i]+=8
        if posIndexDie >11:
            for i in range(0,4):
                pixels[i]+=8
        pixels = map(int, pixels)
        return pixels

    def diesAreNeighbors(self, posIndexDie1, posIndexDie2):#inputs have to be integers
        if posIndexDie1 == posIndexDie2:
            return False
        col1 = posIndexDie1 % 4
        row1 = posIndexDie1 / 4
        col2 = posIndexDie2 % 4
        row2 = posIndexDie2 / 4
        if abs(col1-col2)<=1 and abs(row1-row2)<=1:
            return True
        else:
            return False

    def diesAreDirectNeighbors(self, posIndexDie1, posIndexDie2):
        if posIndexDie1 == posIndexDie2:
            return False
        col1 = posIndexDie1 % 4
        row1 = posIndexDie1 / 4
        col2 = posIndexDie2 % 4
        row2 = posIndexDie2 / 4
        if abs(col1-col2)==1 and abs(row1-row2) == 0:
            return True
        elif abs(col1 - col2) == 0 and abs(row1 - row2) == 1:
            return True
        else:
            return False

    def diesAreDiagonalNeighbors(self, posIndexDie1, posIndexDie2):
        if posIndexDie1 == posIndexDie2:
            return False
        col1 = posIndexDie1 % 4
        row1 = posIndexDie1 / 4
        col2 = posIndexDie2 % 4
        row2 = posIndexDie2 / 4
        if abs(col1 - col2) == 1 and abs(row1 - row2) == 1:
            return True
        else:
            return False

    def pixsArNeighbors(self, posIndexPixel1, posIndexPixel2):
        if posIndexPixel1 == posIndexPixel2:
            return False
        if abs(self.posIndextoCol(posIndexPixel1) - self.posIndextoCol(posIndexPixel2)) <= 1 and abs(self.posIndextoRow(posIndexPixel1) - self.posIndextoRow(posIndexPixel2)) <= 1:
            return True
        else:
            return False

    def pixsAreDirectNeighbors(self, posIndexPixel1, posIndexPixel2):
        if posIndexPixel1 == posIndexPixel2:
            return False
        if abs(self.posIndextoCol(posIndexPixel1) - self.posIndextoCol(posIndexPixel2)) == 1 and (self.posIndextoRow(posIndexPixel1) == self.posIndextoRow(posIndexPixel2)):
            return True
        elif self.posIndextoCol(posIndexPixel1) == self.posIndextoCol(posIndexPixel2) and abs((self.posIndextoRow(posIndexPixel1) - self.posIndextoRow(posIndexPixel2))) == 1:
            return True
        else:
            return False

    def pixsAreDiagonalNeighbors(self, posIndexPixel1, posIndexPixel2):
        if posIndexPixel1 == posIndexPixel2:
            return  False
        if abs(self.posIndextoCol(posIndexPixel1) - self.posIndextoCol(posIndexPixel2)) == 1 and abs(self.posIndextoRow(posIndexPixel1) - self.posIndextoRow(posIndexPixel2)) == 1:
            return True
        else:
            return False
