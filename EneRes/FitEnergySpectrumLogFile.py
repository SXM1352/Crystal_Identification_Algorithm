# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 14:58:33 2021
@author: David
"""
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
import time
import os


def CrystalDict():
    """!
    Define Crystal identification dictionary with respective ids for all the peaks
    based on the different layers

    @return: rows =  ids of crystal ordered by row and column,
        dic_crystal_test = id from crystals
    @rtype: 2D-arr, dict
    """
    m = 1
    row = []
    j = 0
    p = 0
    rows = []
    dic_crystal_test = {}
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
                        'center': {},
                        'valid': False
                    }
                    dic_crystal_test[r] = peakii
                else:
                    if n % 2 != 0:
                        peakii = {
                            'row': j,
                            'layer': 1,
                            'id': r,
                            'center': {},
                            'valid': False
                        }
                        dic_crystal_test[r] = peakii
                    else:
                        peakjj = {
                            'row': j,
                            'layer': 2,
                            'id': r,
                            'center': {},
                            'valid': False
                        }
                        dic_crystal_test[r] = peakjj

            row = []
            j += 1
            p += 1

        elif i >= (65 * m + 31 * p) and j % 2 != 0:
            row_neg = [-1] * len(row)
            new_row = list(itertools.chain(*zip(row_neg, row)))
            new_row.append(-1)
            new_row.append(-1)
            new_row.insert(0,-1)

            rows.append(new_row)
            for r in row:
                peakkk = {
                    'row': j,
                    'layer': 3,
                    'id': r,
                    'center': {},
                    'valid': False
                }
                dic_crystal_test[r] = peakkk
            row = []
            j += 1
            m += 1
        else:
            pass
        row.append(i)

    return rows, dic_crystal_test

def __fitPeaks(hist, i_crystal):
    """!
    Looks for the peaks present in the photonSpectrum using
    a routine created by ROOT (Search) and fit them to obtain the calibration factor

    @return: xycoord_arr with peak coordinates
    @rtype: array
    """
    maxRange=10000
    minRange=500
    hist.GetXaxis().SetRangeUser(minRange, maxRange)
    spectrum = TSpectrum(5, 10)
    '''
    maxpositions: maximum number of peaks
    resolution: NOT USED determines resolution of the neighbouring peaks default value is 1 correspond to 3 sigma distance between peaks. Higher values allow higher resolution (smaller distance between peaks. May be set later through SetResolution.
    '''
    hBack = spectrum.Background(hist, 5, "Compton")

    #hist_clone = hist.Clone(str(i) + "_backgroundRM") # i must be the crystal id

    hist.Add(hBack, -1.) # this remove the background (hist = hist + (-1)*hBack)

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
        #print(xcoord)
        # use gaus with width width depending on energy value:
        preFitHalfRange = xcoord * 0.03
        if xcoord < 500.:
            preFitHalfRange = xcoord * 0.10

        elif xcoord < 1000.:
            preFitHalfRange = xcoord * 0.05

        # elif xcoord < 2000.:
        #     preFitHalfRange = xcoord * 0.02
        #
        # elif xcoord < 3000.:
        #     preFitHalfRange = xcoord * 0.01

        #print(preFitHalfRange)
        fitStart = xcoord - preFitHalfRange

        fitStop = xcoord + preFitHalfRange

        #print(fitStop)
        #print(fitStart)
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
        #print(fitStop)
        #print(fitStart)
        #check for minimum of fit bins:
        fitStart_bin = hist.FindBin(fitStart)
        fitStop_bin = hist.FindBin(fitStop)
        #print(fitStop_bin)
        #print(fitStart_bin)
        if (fitStop_bin - fitStart_bin) <= 10:
            fitRangeBins = (fitStop_bin - fitStart_bin)
            fitRangeMid = (fitStart+fitStop) / 2.
            fitstart_original = fitStart
            fitStart = fitRangeMid - (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.
            fitStop = fitRangeMid + (fitRangeMid-fitstart_original) / (fitRangeBins / 2.) * 6.


        gaus.SetLineStyle(1)
        gaus.SetRange(fitStart, fitStop)
        hist.Fit(gaus, "RQ+")
        #print('mean: ', gaus.GetParameter(1))
        #print('errormean: ', gaus.GetParError(1))
        #print('sigma: ', gaus.GetParameter(2))
        #print('errorsigma: ', gaus.GetParError(2))
        #print(gaus.GetChisquare())
        #print(gaus.GetNDF())
        #print('height: ', gaus.Eval(gaus.GetParameter(1)))

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

        #print('cal_factor: ', tmpPeak['cal_factor'])

        marker = TMarker(tmpPeak['mean'], tmpPeak['peak_height'], 3)
        #markers << marker;
        markers[kl] = marker

        fwhm = tmpPeak['sigma'] / tmpPeak['mean'] * 2.3548 #ask where does that come from?
        #print('fwhm: ', fwhm)
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
        #print('E_r: ', ((gaus.GetParameter(2) / gaus.GetParameter(1))*100.*2.3548))
        peakInfoSave['fitStart'] = ['fStart: ' + str(fitStart)]
        peakInfoSave['fitStop'] = ['fStop: ' + str(fitStop)]
        peakInfoSave['valid_peaks'] = [str(len(validPeaks))]
        peakInfoSave['all_peaks'] = ['/ '+ str(nPeaks)]
        peakInfoSave['id'] = [str(i_crystal)]
        peakInfoSave_all[kl] = peakInfoSave

        stacked = THStack(str(kl) + "_stacked", str(kl) + "_stacked")
        hBack.SetLineColor(kRed)
        stacked.Add(hBack)
        stacked.Add(hist)
    if nPeaks == 0:
        stacked = THStack('NoPeak' + "_stacked", 'NoPeak' + "_stacked")

    return hist, stacked, peakInfoSave_all

def set_char_TCanvas_TPad(c1, pad, h1d, leg, datapv, i_crystal):
    print("{} will be plotted.".format(i_crystal))
    print("The corresponding row is: ", datapv[i_crystal]["row"])
    print("The corresponding layer is: ", datapv[i_crystal]["layer"])
    pad.Draw()
    pad.cd()
    pad.GetFrame().SetFillColor(0)
    pad.GetFrame().SetBorderMode(-1)
    pad.GetFrame().SetBorderSize(5)

    h1d.SetLineColor(kBlue)
    h1d.SetFillColorAlpha(kBlue, 0.35)
    for x in datapv[i_crystal]['pv']:
        try:
            h1d.Fill(x)
        except:
            pass
    n_entries = h1d.GetEntries()
    if n_entries > 100:
        try:
            h1d, stacked, peakInfoSave = __fitPeaks(h1d, i_crystal)
        except:
            stacked = None
            peakInfoSave = None
            print("ERROR: Problem while fitting. Skip and continue. Please, Check.")
    else:
        stacked = None
        peakInfoSave = None

    h1d.Draw()

    leg.SetBorderSize(0) # no border
    leg.SetFillColor(0) # probably kWhite
    leg.SetFillStyle(0) # I'm guessing this just means pure color, no patterns
    leg.SetTextFont(42)
    leg.SetTextSize(0.035) # somewhat large, may need to play with this to make the plot look ok
    leg.AddEntry(h1d,"{}".format(i_crystal),"L") # AddEntry(TGraph/TH1D varName, what you want the legend to say for this graph, show the line)
    leg.Draw() # draw it!
    c1.Update()
    #
    # Open a ROOT file and save the histogram
    #

    h1d.Write()
    if not stacked == None:
        stacked.Write()

    return peakInfoSave

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                             directory where to read the files from')
args = parser.parse_args()

pathtodirectoryRead = args.fileDirect
pathtodirectorySave = pathtodirectoryRead

# auto_inter = raw_input('Please, select "auto" to run over the 4 algorithms and create the corresponding logfiles or "inter" to have a look at the plots: ')
# if auto_inter == "auto":
#     gROOT.SetBatch(True)

with open('{}datapv-000-valid.pickle'.format(pathtodirectoryRead), "rb") as handle:
    datapv000 = pickle.load(handle)  # 000, 100, 010, 111

with open('{}datapv-100-valid.pickle'.format(pathtodirectoryRead), "rb") as handle:
    datapv100 = pickle.load(handle)  # 000, 100, 010, 111

with open('{}datapv-010-valid.pickle'.format(pathtodirectoryRead), "rb") as handle:
    datapv010 = pickle.load(handle)  # 000, 100, 010, 111

with open('{}datapv-111-valid.pickle'.format(pathtodirectoryRead), "rb") as handle:
    datapv111 = pickle.load(handle)  # 000, 100, 010, 111

"""
There is a discrepancy between root fit and python fit. In fact,
 root fit default uses mode “I” [Use integral of function in bin, normalized by the bin volume,
 instead of value at bin center] and python fit uses mode “W” [Ignore the bin uncertainties
 when fitting using the default least square (chi2) method but skip empty bins]. I got 
 the same fitting result now by switching root fit option to “RQW”.
"""
variable = 0
rows, dic_crystal_test = CrystalDict()
rows = np.array(rows)


while variable != "quit": #CREATE ARGPARSE TO PARSE INPUT WITH ROW; LAYER; CRYSTAL
    #WHEN ROW OR LAYER IS SELECTED; CRYSTAL IS -1
    #add option to show plot
    #add option to create log with selected data
    variable = raw_input("Enter COG (HVD), layer (1, 2 or 3), row, column, id of the crystal, Y/N to create log with data or type 'quit' to exit: /n"+
                         "Example:'000,1,2,-1,-1,N' /n"+ "Hints: '-1' means 'all'. There may be rows only with crystals from layer 3 or from layer 1,2. There might be crystal not belonging to the indicated row/column/layer. ")
    if variable == "quit":
        continue
    #myFunc(["first", "2", "-1"])
    HVD = str(variable.split(',')[0])
    layer = int(variable.split(',')[1])
    row = int(variable.split(',')[2])
    column = int(variable.split(',')[3])
    i_crystal_input = int(variable.split(',')[4])
    log_input = str(variable.split(',')[5])

    if log_input == 'Y':
        print('Option to save logfile is deactivated.')
        # gROOT.SetBatch(True)
        # CHECK_FILE = os.path.isfile('{}CalibPVLog{}.txt'.format(pathtodirectorySave, HVD))
        # # If folder doesn't exist, then create it.
        # if CHECK_FILE:
        #     with open('{}CalibPVLog{}.txt'.format(pathtodirectorySave, HVD), 'w+') as fout:
        #         pass
        #     print("Modified file : ", '{}CalibPVLog{}.txt'.format(pathtodirectorySave, HVD))
    else:
        # gROOT.SetBatch(False)
        pass

    myfile = TFile('{}FittingPV{}_temp.root'.format(pathtodirectorySave, HVD), 'RECREATE')

    if HVD == "000":
        datapv = datapv000
    if HVD == "100":
        datapv = datapv100
    if HVD == "010":
        datapv = datapv010
    if HVD == "111":
        datapv = datapv111

    if column != -1:
        list_column = rows[:,column]
    else:
        list_column = [-1]
    c_list = []
    pad_list = []
    h1d_list = []
    leg_list = []
    #date_min = time.strftime('%Y-%m-%d_%H-%M',time.localtime())
    for i_crystal in datapv.keys():
        if datapv[i_crystal]["layer"] == layer or layer == -1:
            if datapv[i_crystal]["row"] == row or row == -1:
                if datapv[i_crystal]["id"] in list_column or column == -1:
                    if datapv[i_crystal]["id"] == i_crystal_input or i_crystal_input == -1:
                        if datapv[i_crystal]['pv']:
                            c_list.append(TCanvas('c{}'.format(i_crystal), 'Fit {}'.format(i_crystal), 200, 10, 900, 900))
                            pad_list.append(TPad('pad{}'.format(i_crystal), 'The pad with the histogram {}'.format(i_crystal), 0.05, 0.05, 0.95, 0.95, 0))
                            h1d_list.append(TH1D('h1d - {}'.format(i_crystal), 'PV - {}'.format(i_crystal), (10000 - 0) / 50, 0, 10000))
                            leg_list.append(TLegend())
                            #h1d_list[-1], valid_peaks_dic = __fitPeaks(h1d_list[-1])

                            peakInfoSave_all = set_char_TCanvas_TPad(c_list[-1], pad_list[-1], h1d_list[-1], leg_list[-1], datapv, i_crystal)
                            #add tileID
                            if log_input == 'Y':
                                print('logfile is deactivated-')
                                if not peakInfoSave_all == None:
                                    pass
                                #     with open('{}CalibPVLog{}.txt'.format(pathtodirectorySave, HVD), 'a') as fout:
                                #         for peak in peakInfoSave_all.keys():
                                #             print(peakInfoSave_all[peak])
                                #             df = pd.DataFrame(peakInfoSave_all[peak], columns=['id', 'valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                #                                                         'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                #                                                         'E_r[%(sigma)]', 'E_r[%(FWHM)]'])  # create a dataframe with the data of the current file
                                #
                                #             fout.write(df.to_string(header=False,
                                #                                         index=False))  # we write the dataframe with the index
                                #             fout.write('\n')  # a newline to place correctly the next rows
                                else:
                                    print('No peaks available in your selection.')
                            print(peakInfoSave_all)

    myfile.Close()
