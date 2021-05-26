# read calibTXT, extract mean and calculate calib_factor
# four dic with 000,010,100,111 and id_crystal and calib factor (= 511. / tmpPeak['mean']) {'111': {33:0.14386492736,69:0.1590328470}}
#loop over dic_calibPV and new array with calib values
import pandas as pd
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1D, TFile, TLegend, TH1D, THStack, TFitResultPtr, TFitResult, TSpectrum, TMath, TMarker, TFile
from ROOT import gROOT, gBenchmark
from ROOT import kBlack, kBlue, kRed, kGreen, kYellow
import numpy as np
import cPickle as pickle
import h5py
import argparse
from textwrap import dedent
import sys
import itertools
import re
import os

class CalibLoadPlot():
    def __init__(self, splits, pathtodirectoryRead):
        self.splits = splits

        self.HVD_list = ["000", "100", "010", "111"]

        self.pathtodirectoryRead = pathtodirectoryRead
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-02-17_-_15-20-39_-_2011002000_A41B0821-034_2021-02-05/2021-02-17_-_16-17-01_-_floodmapWithSources/ramdisks_2021-02-17_-_16-37-36/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/'
        # self.pathtodirectoryRead = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

        self.pathtodirectorySave = self.pathtodirectoryRead

        self.pathtodirectoryReadCrystal = 'CrystalsKeV/'

        # self.pathtodirectorySavePV = '20210304_NEW-2021-02-17_PhotonSpectrum/'
        # self.pathtodirectorySavePV = '20210303_NEW-2021-02-17_PhotonSpectrum/'
        # self.pathtodirectorySavePV = '20210315_NEW_PhotonSpectrum/'

        # self.pathtodirectorySave = '/home/david.perez/TestParallel/'
        # self.pathtodirectorySavePV = 'PV/'

    def checkFolder(self, pathDirectory):
        CHECK_FOLDER = os.path.isdir(pathDirectory)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(pathDirectory)
            print("created folder : ", pathDirectory)

    def normalizeAndSplit(self, l):
        ''' function to split an input line and remove unwanted characters \
        input parameters: \
        l = line to parse'''

        #l = re.sub("\s*#.*", "", l)	# Remove comments
        l = re.sub('^\s*', '', l)	# Remove leading white space
        #l = re.sub('\s*$', '', l)	# Remove trailing whitespace
        #l = re.sub('\s+', '\t', l)	# Normalize whitespace to tabs
        #l = re.sub('\r', '', l)		# Remove \r
        l = re.sub('\n', '', l)		# Remove \l
        #l = re.sub(':', ',', l)		# Remove \l
        l = l.split()
        return l
    def dic_calFactor_HVD(self, pathtodirectoryRead, HVD, dic_HVD):
        with open('{}CalibPVLog{}.txt'.format(pathtodirectoryRead, HVD), 'r') as finput:
            lines = finput.readlines()
            E_r_2 = 100.
            for line in lines:
                el = self.normalizeAndSplit(line)
                id_crystal = int(el[0])
                mean = el[13]
                cal_factor = 511. / float(mean)
                E_r = float(el[-1])
                if id_crystal in dic_HVD.keys():
                    if E_r < E_r_2:
                        dic_HVD[id_crystal] = cal_factor
                else:
                    dic_HVD[id_crystal] = cal_factor
                E_r_2 = E_r
        return dic_HVD

    def __fitPeaks(self, hist, n_entries):
        """!
        Looks for the peaks present in the photonSpectrum using
        a routine created by ROOT (Search) and fit them to obtain the calibration factor

        @return: xycoord_arr with peak coordinates
        @rtype: array
        """
        maxRange=2000
        minRange=0
        hist.GetXaxis().SetRangeUser(minRange, maxRange)
        spectrum = TSpectrum(5, 10)
        '''
        maxpositions: maximum number of peaks
        resolution: NOT USED determines resolution of the neighbouring peaks default value is 1 correspond to 3 sigma distance between peaks. Higher values allow higher resolution (smaller distance between peaks. May be set later through SetResolution.
        '''
        hBack = spectrum.Background(hist, 2, "Compton")

        #hist_clone = hist.Clone(str(i) + "_backgroundRM") # i must be the crystal id

        # hist.Add(hBack, -1.) # this remove the background (hist = hist + (-1)*hBack)

        n_entries_afterFit = hist.GetEntries()
        print('n_entries_afterFit', n_entries_afterFit)

        threshold = 0.50

        nPeaks = spectrum.Search(hist, 4., '', threshold) #sigma=4

        # posx_array = spectrum->GetPositionX();
        # posy_array = spectrum->GetPositionY();

        # spectrum = TSpectrum2(300)  # we need to set the maximum amount of peaks it can find!!!!!
        # nPeaks = spectrum.SearchHighRes(c_source, c_dest, binsx, binsy, self.sigma, self.threshold, self.rmBackground,
        #                                 self.convIter, self.markov,
        #                                 self.mIter)  # sigma,thrs,bckg, thrs to 4 if we want all peaks in 111, sonst 6 for 111, 7 for 100

        posx_array = spectrum.GetPositionX()
        posy_array = spectrum.GetPositionY()
        # xycoord_arr = []

        validPeaks = {}
        allPeaks = {}
        fits = {}
        markers = {}
        peakInfoSave_all = {}
        for kl in range(nPeaks):
            xcoord = posx_array[kl]
            ycoord = posy_array[kl]
            print(xcoord)
            # use gaus with width width depending on energy value:
            preFitHalfRange = xcoord * 0.03
            # if xcoord < 500.:
            #     preFitHalfRange = xcoord * 0.10
            #
            # elif xcoord < 1000.:
            #     preFitHalfRange = xcoord * 0.05

            # elif xcoord < 2000.:
            #     preFitHalfRange = xcoord * 0.02
            #
            # elif xcoord < 3000.:
            #     preFitHalfRange = xcoord * 0.01

            print(preFitHalfRange)
            fitStart = xcoord - preFitHalfRange

            fitStop = xcoord + preFitHalfRange

            print(fitStop)
            print(fitStart)
            fitStart_bin = hist.FindBin(fitStart)

            fitStop_bin = hist.FindBin(fitStop)


            if fitStart_bin == fitStop_bin:
                fitStart = hist.GetBinLowEdge(fitStart_bin)
                fitStop = hist.GetBinLowEdge(fitStop_bin+1)


            #check for minimum of fit bins:
            elif (fitStop_bin - fitStart_bin) <= 10:
                fitRangeBins = (fitStop_bin - fitStart_bin)
                fitRangeMid = (fitStart+fitStop) / 2.
                fitstart_original = fitStart
                fitStart = fitRangeMid - (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.
                fitStop = fitRangeMid + (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.

            #define prefit gauss
            gaus = TF1("gaus_peak_" + str(kl), "gaus", fitStart, fitStop)
            gaus.SetParameter(0, ycoord)
            gaus.SetParameter(1, xcoord)
            gaus.SetParameter(2, preFitHalfRange / 2.3548)
            gaus.SetLineStyle(2)
            gaus.SetLineStyle(2)

            #prefit
            hist.Fit(gaus, "RQ+")
            #fits << gaus; to run the fit?? to store the different fits
            fits[kl] = gaus

            #use fit results to define fit range as 2 * FWHM range
            fitStart = gaus.GetParameter(1) - gaus.GetParameter(2) * 2.3548 * 0.65
            fitStop = gaus.GetParameter(1) + gaus.GetParameter(2) * 2.3548 * 0.65

            if (fitStart < minRange):
                fitStart = minRange

            if (fitStop > maxRange):
                fitStop = maxRange
            print(fitStop)
            print(fitStart)
            #check for minimum of fit bins:
            fitStart_bin = hist.FindBin(fitStart)
            fitStop_bin = hist.FindBin(fitStop)
            print(fitStop_bin)
            print(fitStart_bin)
            if (fitStop_bin - fitStart_bin) <= 10:
                fitRangeBins = (fitStop_bin - fitStart_bin)
                fitRangeMid = (fitStart+fitStop) / 2.
                fitstart_original = fitStart
                fitStart = fitRangeMid - (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.
                fitStop = fitRangeMid + (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.


            gaus.SetLineStyle(1)
            gaus.SetRange(fitStart, fitStop)
            hist.Fit(gaus, "RQ+")
            print('mean: ', gaus.GetParameter(1))
            print('errormean: ', gaus.GetParError(1))
            print('sigma: ', gaus.GetParameter(2))
            print('errorsigma: ', gaus.GetParError(2))
            print(gaus.GetChisquare())
            print(gaus.GetNDF())
            print('height: ', gaus.Eval(gaus.GetParameter(1)))

            PeakInfo = {}
            tmpPeak = {}
            tmpPeak['position'] = xcoord
            tmpPeak['mean'] = gaus.GetParameter(1)
            tmpPeak['mean_error'] = gaus.GetParError(1)
            tmpPeak['sigma'] = gaus.GetParameter(2)
            tmpPeak['sigma_error'] = gaus.GetParError(2)
            if gaus.GetNDF() == 0:
                tmpPeak['chi2_ndof'] = 'NDF: 0'
            else:
                tmpPeak['chi2_ndof'] = gaus.GetChisquare() / gaus.GetNDF()
            tmpPeak['cal_factor'] = 511. / tmpPeak['mean']
            tmpPeak['peak_height'] = gaus.Eval(gaus.GetParameter(1))
            tmpPeak['fitStart'] = fitStart
            tmpPeak['fitStop']= fitStop
            #tmpPeak.fit = gaus

            print('cal_factor: ', tmpPeak['cal_factor'])

            marker = TMarker(tmpPeak['mean'], tmpPeak['peak_height'], 3)
            #markers << marker;
            markers[kl] = marker

            fwhm = tmpPeak['sigma'] / tmpPeak['mean'] * 2.3548 #ask where does that come from?
            print('fwhm: ', fwhm)
            if fwhm >= 0.05 and fwhm <= 0.25 and tmpPeak['chi2_ndof'] <= 20. and (np.abs(tmpPeak['position'] - tmpPeak['mean']) / tmpPeak['position'] < 0.2) and tmpPeak['position'] > 400 and tmpPeak['position'] < 4000:
            #validPeaks.append(tmpPeak) #make dictionary??
                validPeaks[kl] = tmpPeak

                marker.SetMarkerStyle(kGreen)
            else:
                gaus.SetLineColor(kGreen)
                marker.SetMarkerStyle(kYellow)


            hist.GetListOfFunctions().Add(marker)
            #allPeaks.append(tmpPeak) #make dictionary??
            allPeaks[kl] = tmpPeak

            peakInfoSave = {}
            peakInfoSave['position'] = ['pos: ' + str(xcoord)]
            peakInfoSave['mean'] = ['mean: ' + str(gaus.GetParameter(1))]
            peakInfoSave['mean_error'] = ['m_err: ' + str(gaus.GetParError(1))]
            peakInfoSave['sigma'] = ['sigma: ' + str(gaus.GetParameter(2))]
            peakInfoSave['sigma_error'] = ['s_err: ' + str(gaus.GetParError(2))]
            if gaus.GetNDF() == 0:
                peakInfoSave['chi2_ndof'] = ['NDF: 0']
            else:
                peakInfoSave['chi2_ndof'] = ['c2_ndf: ' + str(gaus.GetChisquare() / gaus.GetNDF())]
            peakInfoSave['E_r[%(sigma)]'] = ['E_r[%(sigma)]: ' + str((gaus.GetParameter(2) / gaus.GetParameter(1))*100.)]
            peakInfoSave['E_r[%(FWHM)]'] = ['E_r[%(FWHM)]: ' + str((gaus.GetParameter(2) / gaus.GetParameter(1))*100.*2.3548)]
            print('E_r: ', ((gaus.GetParameter(2) / gaus.GetParameter(1))*100.*2.3548))
            peakInfoSave['fitStart'] = ['fStart: ' + str(fitStart)]
            peakInfoSave['fitStop'] = ['fStop: ' + str(fitStop)]
            peakInfoSave['valid_peaks'] = [str(len(validPeaks))]
            peakInfoSave['all_peaks'] = ['/ '+ str(nPeaks)]
            peakInfoSave['n_entries'] = ['n_entries: ' + str(n_entries)]
            peakInfoSave_all[kl] = peakInfoSave

            stacked = THStack(str(kl) + "_stacked", str(kl) + "_stacked")
            hBack.SetLineColor(kRed)
            stacked.Add(hBack)
            stacked.Add(hist)
        if nPeaks == 0:
            stacked = THStack('NoPeak' + "_stacked", 'NoPeak' + "_stacked")

        return hist, stacked, peakInfoSave_all

    def set_char_TCanvas_TPad(self, c1, pad, h1d, leg, datapv):
        pad.Draw()
        pad.cd()
        pad.GetFrame().SetFillColor(0)
        pad.GetFrame().SetBorderMode(-1)
        pad.GetFrame().SetBorderSize(5)

        h1d.SetLineColor(kBlue)
        h1d.SetFillColorAlpha(kBlue, 0.35)
        for x in datapv:
            h1d.Fill(x)
        n_entries = h1d.GetEntries()
        print('n_entries: ', n_entries)
        try:
            h1d, stacked, peakInfoSave = self.__fitPeaks(h1d, n_entries)
        except:
            stacked = None
            peakInfoSave = None
            print("ERROR: Problem while fitting. Skip and continue. Please, Check.")

        h1d.Draw()

        leg.SetBorderSize(0) # no border
        leg.SetFillColor(0) # probably kWhite
        leg.SetFillStyle(0) # I'm guessing this just means pure color, no patterns
        leg.SetTextFont(42)
        leg.SetTextSize(0.035) # somewhat large, may need to play with this to make the plot look ok
        leg.AddEntry(h1d,"Final-Spectrum","L") # AddEntry(TGraph/TH1D varName, what you want the legend to say for this graph, show the line)
        leg.Draw() # draw it!
        c1.Update()
        #
        # Open a ROOT file and save the histogram
        #

        h1d.Write()
        if not stacked == None:
            stacked.Write()

        return peakInfoSave

    def __load_calibFinal(self):
        hist_array_total = []
        hist_array_layer1 = []
        hist_array_layer2 = []
        hist_array_layer3 = []
        hist_array_crystals = [[] for i in range(3425)]

        for event in self.splits:
            final_event = event[1]
            with open('{}array_calibFinalPV_Total_{}.pickle'.format(self.pathtodirectoryRead, final_event), 'r') as arrinput:
                hist_array_total_temp = pickle.load(arrinput)
                for pvc in hist_array_total_temp:
                    hist_array_total.append(pvc)

            with open('{}array_calibFinalPV_Layer1_{}.pickle'.format(self.pathtodirectoryRead, final_event),
                      'r') as arrinput:
                hist_array_layer1_temp = pickle.load(arrinput)
                for pvc in hist_array_layer1_temp:
                    hist_array_layer1.append(pvc)

            with open('{}array_calibFinalPV_Layer2_{}.pickle'.format(self.pathtodirectoryRead, final_event),
                      'r') as arrinput:
                hist_array_layer2_temp = pickle.load(arrinput)
                for pvc in hist_array_layer2_temp:
                    hist_array_layer2.append(pvc)

            with open('{}array_calibFinalPV_Layer3_{}.pickle'.format(self.pathtodirectoryRead, final_event),
                      'r') as arrinput:
                hist_array_layer3_temp = pickle.load(arrinput)
                for pvc in hist_array_layer3_temp:
                    hist_array_layer3.append(pvc)

            with open('{}array_calibFinalPV_Crystals_{}.pickle'.format(self.pathtodirectoryRead, final_event),
                      'r') as arrinput:
                hist_array_crystals_temp = pickle.load(arrinput)
                for index_pvc, pvc in enumerate(hist_array_crystals_temp):
                    hist_array_crystals[index_pvc] = hist_array_crystals[index_pvc] + pvc

        hist_array_list = [hist_array_total, hist_array_layer1, hist_array_layer2, hist_array_layer3, hist_array_crystals]
        return hist_array_list

    def __load_save_dic_listmode(self):
        'function to save the values (cluster, crystal and keV) we need for the listmode binary file.'
        dic_listmode = {}

        for event in self.splits:
            final_event = event[1]
            with open('{}dic_listmode_{}.pickle'.format(self.pathtodirectoryRead, final_event), 'r') as input:
                dic_listmode_temp = pickle.load(input)
                dic_listmode.update(dic_listmode_temp)

        with open('{}dic_listmode_{}.pickle'.format(self.pathtodirectoryRead, 'total'), 'wb') as handle:
            pickle.dump(dic_listmode, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

    def runCalibLoadPlot(self):

        gROOT.SetBatch(True)

        self.checkFolder(self.pathtodirectorySave + self.pathtodirectoryReadCrystal)

        print("importing...")

        # with open('{}array_calibFinalPV_1.pickle'.format(pathtodirectoryRead), 'r') as arrinput:
        #     hist_array_1 = pickle.load(arrinput)
        # with open('{}array_calibFinalPV_2.pickle'.format(pathtodirectoryRead), 'r') as arrinput:
        #     hist_array_2 = pickle.load(arrinput)
        # hist_array = hist_array_1+hist_array_2

        hist_array_list = self.__load_calibFinal()

        layers = ['Total', 'Layer1', 'Layer2', 'Layer3']

        print("imported.")
        for n_layer, layer in enumerate(layers):
            myfile = TFile('{}FittingFinalPV_{}.root'.format(self.pathtodirectorySave, layer), 'RECREATE')
            canva = TCanvas('c', 'Fit', 200, 10, 900, 900)
            pad = TPad('pad', 'The pad with the histogram', 0.05, 0.05, 0.95, 0.95, 0)
            h1d = TH1D('h1d', 'PV', (2000 - 0) / 5, 0, 2000)
            legend = TLegend()
            #add tileID

            hist_array = hist_array_list[n_layer]
            peakInfoSave_all = self.set_char_TCanvas_TPad(canva, pad, h1d, legend, hist_array)
            print(peakInfoSave_all)
            with open('{}CalibPVLog{}.txt'.format(self.pathtodirectorySave, layer), 'a') as fout:
                for peak in peakInfoSave_all.keys():
                    print(peakInfoSave_all[peak])
                    df = pd.DataFrame(peakInfoSave_all[peak],
                                      columns=['valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                               'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                               'E_r[%(sigma)]',
                                               'E_r[%(FWHM)]', 'n_entries'])  # create a dataframe with the data of the current file

                    fout.write(df.to_string(header=False,
                                            index=False))  # we write the dataframe with the index
                    fout.write('\n')  # a newline to place correctly the next rows
            myfile.Close()
        print('Layers are finished')
        self.__load_save_dic_listmode()

        crystals_n = range(3425)
        hist_array_crystals = hist_array_list[-1]
        for crystal in crystals_n:
            hist_array = hist_array_crystals[crystal]
            if hist_array:
                myfile = TFile('{}FittingFinalPV_{}.root'.format(self.pathtodirectorySave + self.pathtodirectoryReadCrystal, crystal), 'RECREATE')
                canva = TCanvas('c', 'Fit', 200, 10, 900, 900)
                pad = TPad('pad', 'The pad with the histogram', 0.05, 0.05, 0.95, 0.95, 0)
                h1d = TH1D('h1d', 'PV', (2000 - 0) / 5, 0, 2000)
                legend = TLegend()
                #add tileID

                peakInfoSave_all = self.set_char_TCanvas_TPad(canva, pad, h1d, legend, hist_array)
                print(peakInfoSave_all)
                with open('{}CalibPVLog{}.txt'.format(self.pathtodirectorySave + self.pathtodirectoryReadCrystal, crystal), 'a') as fout:
                    for peak in peakInfoSave_all.keys():
                        print(peakInfoSave_all[peak])
                        df = pd.DataFrame(peakInfoSave_all[peak],
                                          columns=['valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                                   'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                                   'E_r[%(sigma)]',
                                                   'E_r[%(FWHM)]', 'n_entries'])  # create a dataframe with the data of the current file

                        fout.write(df.to_string(header=False,
                                                index=False))  # we write the dataframe with the index
                        fout.write('\n')  # a newline to place correctly the next rows
                myfile.Close()

