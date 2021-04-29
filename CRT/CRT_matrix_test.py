import os
import argparse
import pandas as pd
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1D, TFile, TLegend, TH1D, THStack, TFitResultPtr, TFitResult, TSpectrum, TMath, TMarker, TFile
from ROOT import gROOT, gBenchmark
from ROOT import kBlack, kBlue, kRed, kGreen, kYellow
import cPickle as pickle

import h5py
import numpy as np
import pyximport
pyximport.install()
import matplotlib.pyplot as plt
from cython_posTile import Positioning as pos
from PSFTools import PSFTools
psf = PSFTools()
pos = pos()

def __fitPeaks(hist, i_crystal):
    """!
    Looks for the peaks present in the photonSpectrum using
    a routine created by ROOT (Search) and fit them to obtain the calibration factor

    @return: xycoord_arr with peak coordinates
    @rtype: array
    """
    maxRange=10000
    minRange=-10000
    hist.GetXaxis().SetRangeUser(minRange, maxRange)
    spectrum = TSpectrum(2, 5)
    '''
    maxpositions: maximum number of peaks
    resolution: NOT USED determines resolution of the neighbouring peaks default value is 1 correspond to 3 sigma distance between peaks. Higher values allow higher resolution (smaller distance between peaks. May be set later through SetResolution.
    '''
    #hBack = spectrum.Background(hist, 5)

    #hist_clone = hist.Clone(str(i) + "_backgroundRM") # i must be the crystal id

    #hist.Add(hBack, -1.) # this remove the background (hist = hist + (-1)*hBack)

    threshold = 0.50

    nPeaks = spectrum.Search(hist, 4., '', threshold) #sigma=4

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
        # use gaus with width width depending on mean value:
        if abs(xcoord) < 25:
            preFitHalfRange = 25
        else:
            preFitHalfRange = xcoord

        # if xcoord < 500.:
        #     preFitHalfRange = xcoord * 0.10
        #
        # elif xcoord < 1000.:
        #     preFitHalfRange = xcoord * 0.05

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

        #print('cal_factor: ', tmpPeak['cal_factor'])

        marker = TMarker(tmpPeak['mean'], tmpPeak['peak_height'], 3)
        #markers << marker;
        markers[kl] = marker

        fwhm = tmpPeak['sigma'] * 2.3548
        print('fwhm: ', fwhm)
        #fwhm is the e_r in this case and a upper limit of 20 could be tried, not good -> ~300 peaks are out then
        #chi square is highly biased by the background removal and when the left side is removed and thus not symetric with the right side of the peak, the chi square increases at values around 40
        #that is why the condition for chi square will be set to be more conservative
        if fwhm >= 2000 and fwhm <= 10 and (np.abs(np.abs(tmpPeak['position'] - tmpPeak['mean']) / tmpPeak['position']) < 0.2) and tmpPeak['chi2_ndof'] <= 50.: #(chi2 before 20)
        #validPeaks.append(tmpPeak) #make dictionary??
            validPeaks[kl] = tmpPeak
            valid_P = 1
            marker.SetMarkerStyle(kGreen)
        else:
            gaus.SetLineColor(kGreen)
            marker.SetMarkerStyle(kYellow)
            valid_P = 0

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
        #peakInfoSave['E_r[%(sigma)]'] = ['E_r[%(sigma)]: ' + str((gaus.GetParameter(2) / gaus.GetParameter(1))*100.)]
        peakInfoSave['CRT[(FWHM)]'] = ['CRT[(FWHM)]: ' + str(gaus.GetParameter(2)*2.3548)]
        #print('E_r: ', ((gaus.GetParameter(2) / gaus.GetParameter(1))*100.*2.3548))
        peakInfoSave['fitStart'] = ['fStart: ' + str(fitStart)]
        peakInfoSave['fitStop'] = ['fStop: ' + str(fitStop)]
        peakInfoSave['valid_peaks'] = [valid_P]
        peakInfoSave['all_peaks'] = ['/ '+ str(nPeaks)]
        peakInfoSave['id'] = [str(i_crystal)]
        peakInfoSave_all[kl] = peakInfoSave

        #stacked = THStack(str(kl) + "_stacked", str(kl) + "_stacked")
        #hBack.SetLineColor(kRed)
        #stacked.Add(hBack)
        #stacked.Add(hist)
    # if nPeaks == 0:
    #     stacked = THStack('NoPeak' + "_stacked", 'NoPeak' + "_stacked")

    return hist, peakInfoSave_all

def set_char_TCanvas_TPad(c1, pad, h1d, leg, data_fill, i_crystal):
    print("{} will be plotted.".format(i_crystal))
    # print("The corresponding row is: ", datapv[i_crystal]["row"])
    # print("The corresponding layer is: ", datapv[i_crystal]["layer"])
    pad.Draw()
    pad.cd()
    pad.GetFrame().SetFillColor(0)
    pad.GetFrame().SetBorderMode(-1)
    pad.GetFrame().SetBorderSize(5)

    h1d.SetLineColor(kBlue)
    h1d.SetFillColorAlpha(kBlue, 0.35)
    for x in data_fill:
        try:
            h1d.Fill(x)
        except:
            print('Error filling histogram. Check filling values.')
    n_entries = h1d.GetEntries()
    if n_entries > 100:
        try:
            h1d, peakInfoSave = __fitPeaks(h1d, i_crystal)
        except:
            # stacked = None
            peakInfoSave = None
            print("ERROR: Problem while fitting. Skip and continue. Please, Check.")
    else:
        # stacked = None
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
    # if not stacked == None:
    #     stacked.Write()

    return peakInfoSave

parser = argparse.ArgumentParser()
# parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')

args = parser.parse_args()
pathtodirectoryRead = args.fileDirect

# file = h5py.File("reference.hdf5", "r+")
print('importing...')
with h5py.File("{}timeStamps_coinc.hdf5".format(pathtodirectoryRead), "r") as f:
    dset = f["data"]
    coinc_timestamps = dset[:]
with h5py.File("{}timeStamps_cal.hdf5".format(pathtodirectoryRead), "r") as f:
    dset = f["data"]
    cal_timestamps = dset[:]

with h5py.File("{}photons_coinc.hdf5".format(pathtodirectoryRead), "r") as f:
    dset = f["data"]
    coinc_photons = dset[:]
with h5py.File("{}photons_cal.hdf5".format(pathtodirectoryRead), "r") as f:
    dset = f["data"]
    cal_photons = dset[:]
print('imported...')

# with h5py.File("{}dic_CLuster_cal.hdf5".format(pathtodirectoryRead), "r") as f: #we need to have the crystal label of all events from cal
#     dset = f["data"]
#     cal_crystalS = dset[:]
# with h5py.File("{}dic_CLuster_coinc.hdf5".format(pathtodirectoryRead), "r") as f: #we need to have the crystal label of all events from coinc
#     dset = f["data"]
#     coinc_crystalS = dset[:]
# coinc_timestamps = file["coinc_timestamps"][:].astype(float)
# cal_photons = file["cal_photons"][:]
# coinc_photons = file["coinc_photons"][:]
# cal_timestamps = file["cal_timestamps"][:].astype(float)
cal_timestamps[cal_timestamps==0] = np.nan
coinc_timestamps[coinc_timestamps == 0] = np.nan

def select_events(array, indices):
    return np.concatenate(array[indices])


cal_mainDieS = np.asanyarray([pos.posIndexPixeltoDie(x) for x in np.argmax(cal_photons, axis=1)])
coinc_mainDieS = np.asanyarray([pos.posIndexPixeltoDie(x) for x in np.argmax(coinc_photons, axis=1)])

time_matrix = np.zeros((1298,73))
time_matrix[:,72] = 1
time_matrix[1296,0:36] = 1
time_matrix[1296,72] = 0
time_matrix[1297,36:72] = 1
time_matrix[1297, 72] = 0
time_differences = np.zeros(1298)
matrix_line = 0

diff_cal_all = {}
CHECK_FILE = os.path.isfile('{}CalibCRTLog{}.txt'.format(pathtodirectoryRead, 'cal'))
# If folder doesn't exist, then create it.
if CHECK_FILE:
    with open('{}CalibCRTLog{}.txt'.format(pathtodirectoryRead, 'cal'), 'w+') as fout:
        pass
    print("Modified file : ", '{}CalibCRTLog{}.txt'.format(pathtodirectoryRead, 'cal'))

CHECK_FILE = os.path.isfile('{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, 'cal'))
# If folder doesn't exist, then create it.
if CHECK_FILE:
    with open('{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, 'cal'), 'w+') as fout:
        pass
    print("Modified file : ", '{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, 'cal'))
gROOT.SetBatch(True)
for cal_mainDie in range(36):
    diff_cal = []
    c_list = []
    pad_list = []
    h1d_list = []
    leg_list = []
    for coinc_mainDie in range(36):
        #print matrix_line
        events_cal = np.where(cal_mainDie == cal_mainDieS)[0]
        events_coinc = np.where(coinc_mainDie == coinc_mainDieS)[0]
        events = np.intersect1d(events_cal, events_coinc)
        cal_time_selected = cal_timestamps[events]
        cal_time_selected = cal_time_selected[:,cal_mainDie]
        coinc_time_selected = coinc_timestamps[events]
        coinc_time_selected = coinc_time_selected[:,coinc_mainDie]
        diff = cal_time_selected - coinc_time_selected
        print "events, cal_mainDie, coinc_mainDie", diff.shape, cal_mainDie, coinc_mainDie
        #print([di for di in diff])
        if diff.shape[0] >= 1500:
            mean = np.mean(diff)
            std = np.std(diff)
            bins = 300
            y, x = np.histogram(diff, bins, range=(mean - 3 * std, mean + 3 * std))

            left, middle, right = psf.fwxm(x[0:bins], y, 0.5, False)
            print left, middle, right
            print "CRT FWHM: ", right - left

            c_list.append(TCanvas('c{}'.format(cal_mainDie+coinc_mainDie), 'Fit {}'.format(cal_mainDie+coinc_mainDie), 200, 10, 900, 900))
            pad_list.append(
                TPad('pad{}'.format(cal_mainDie+coinc_mainDie), 'The pad with the histogram {}'.format(cal_mainDie+coinc_mainDie), 0.05, 0.05, 0.95,
                     0.95, 0))
            h1d_list.append(TH1D('h1d - {}'.format(cal_mainDie+coinc_mainDie), 'PV - {}'.format(cal_mainDie+coinc_mainDie), (20000 - 0) / 50, -10000, 10000))
            leg_list.append(TLegend())
            # h1d_list[-1], valid_peaks_dic = __fitPeaks(h1d_list[-1])

            peakInfoSave_all = set_char_TCanvas_TPad(c_list[-1], pad_list[-1], h1d_list[-1], leg_list[-1], diff,
                                                     cal_mainDie+coinc_mainDie)
            time_matrix[matrix_line, 72] = 1

            #print(peakInfoSave_all)
            middle_root = float(peakInfoSave_all[peakInfoSave_all.keys()[0]]['mean'][0].split(':')[1])
            print("middle ROOT", middle_root)

            time_matrix[matrix_line, cal_mainDie] = 1
            time_matrix[matrix_line, coinc_mainDie + 36] = 1
            time_differences[matrix_line] = middle_root
            diff = diff.tolist()
            diff_cal += diff

        matrix_line += 1
    if diff_cal:

        mean_cal = np.mean(diff_cal)
        std_cal = np.std(diff_cal)
        bins_cal = 300
        y_cal, x_cal = np.histogram(diff_cal, bins_cal, range=(mean_cal - 1 * std_cal, mean_cal + 1 * std_cal))

        left_cal, middle_cal, right_cal = psf.fwxm(x_cal[0:bins_cal], y_cal, 0.5, False)
        CRT = right_cal - left_cal
        print(left_cal, middle_cal, right_cal)
        print("CRT FWHM: ", CRT)
        diff_cal_all[cal_mainDie] = {'DPC': [cal_mainDie], 'CRT': [CRT], 'middle_cal': [middle_cal]}
        with open('{}CalibCRTLog{}.txt'.format(pathtodirectoryRead, 'cal'), 'a') as fout:
            # print(peakInfoSave_all[peak])
            df = pd.DataFrame(diff_cal_all[cal_mainDie],
                              columns=['DPC', 'CRT', 'middle_cal'])  # create a dataframe with the data of the current file

            fout.write(df.to_string(header=False,
                                    index=False))  # we write the dataframe with the index
            fout.write('\n')  # a newline to place correctly the next rows

        c_list.append(TCanvas('c{}'.format(cal_mainDie), 'Fit {}'.format(cal_mainDie), 200, 10, 900, 900))
        pad_list.append(
            TPad('pad{}'.format(cal_mainDie), 'The pad with the histogram {}'.format(cal_mainDie), 0.05, 0.05, 0.95,
                 0.95, 0))
        h1d_list.append(TH1D('h1d - {}'.format(cal_mainDie), 'PV - {}'.format(cal_mainDie), (20000 - 0) / 50, -10000, 10000))
        leg_list.append(TLegend())
        # h1d_list[-1], valid_peaks_dic = __fitPeaks(h1d_list[-1])

        peakInfoSave_all = set_char_TCanvas_TPad(c_list[-1], pad_list[-1], h1d_list[-1], leg_list[-1], diff_cal,
                                                 cal_mainDie)
        if not peakInfoSave_all == None:
            with open('{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, 'cal'), 'a') as fout:
                for peak in peakInfoSave_all.keys():
                    # print(peakInfoSave_all[peak])
                    df = pd.DataFrame(peakInfoSave_all[peak],
                                      columns=['id', 'valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                               'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                               'CRT[(FWHM)]'])  # create a dataframe with the data of the current file

                    fout.write(df.to_string(header=False,
                                            index=False))  # we write the dataframe with the index
                    fout.write('\n')  # a newline to place correctly the next rows
        # variable = raw_input('please enter')
    #print time_matrix
    #print time_differences
gROOT.SetBatch(False)
print time_matrix
print time_differences

with open(
        '{}tMatrix.pickle'.format(pathtodirectoryRead),
        'wb') as handle:
    pickle.dump(time_matrix, handle,
                protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)
with open(
        '{}tDiff.pickle'.format(pathtodirectoryRead),
        'wb') as handle:
    pickle.dump(time_differences, handle,
                protocol=pickle.HIGHEST_PROTOCOL)  # protocol to make it faster it selects last protocol available for current python version (important in py27)

print "before skew correction"
cal_timestamps_x = np.nanmin(cal_timestamps, axis=1)
coinc_timestamps_x = np.nanmin(coinc_timestamps, axis=1)
print(coinc_timestamps_x)

diff = cal_timestamps_x - coinc_timestamps_x

cal_mainDie = 'Stack'
c_list = []
pad_list = []
h1d_list = []
leg_list = []

c_list.append(TCanvas('c{}'.format(cal_mainDie), 'Fit {}'.format(cal_mainDie), 200, 10, 900, 900))
pad_list.append(
    TPad('pad{}'.format(cal_mainDie), 'The pad with the histogram {}'.format(cal_mainDie), 0.05, 0.05, 0.95,
         0.95, 0))
h1d_list.append(TH1D('h1d - {}'.format(cal_mainDie), 'PV - {}'.format(cal_mainDie), (20000 - 0) / 50, -10000, 10000))
leg_list.append(TLegend())
# h1d_list[-1], valid_peaks_dic = __fitPeaks(h1d_list[-1])

peakInfoSave_all = set_char_TCanvas_TPad(c_list[-1], pad_list[-1], h1d_list[-1], leg_list[-1], diff,
                                         cal_mainDie)
if not peakInfoSave_all == None:
    with open('{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, cal_mainDie), 'a') as fout:
        for peak in peakInfoSave_all.keys():
            # print(peakInfoSave_all[peak])
            df = pd.DataFrame(peakInfoSave_all[peak],
                              columns=['id', 'valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                       'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                       'CRT[(FWHM)]'])  # create a dataframe with the data of the current file

            fout.write(df.to_string(header=False,
                                    index=False))  # we write the dataframe with the index
            fout.write('\n')  # a newline to place correctly the next rows

mean = np.mean(diff)
std = np.std(diff)
bins = 500
#y, x = np.histogram(diff, bins, range=(mean - 3 * std, mean + 3 * std))
y, x = np.histogram(diff, bins, range=(-3000, 3000))

left, middle, right = psf.fwxm(x[0:bins], y, 0.5, True)
print "CRT", right - left
print "middle", middle

variable = raw_input('please enter')

# skew correction
skews = np.linalg.lstsq(time_matrix, time_differences)[0]
skews_old = skews.astype(int)
skews_cal = skews[0:36]
skews_coinc = skews[36:72]

print("skews_cal", skews_cal)
print("skews_coinc", skews_coinc)

print(coinc_timestamps)
cal_timestamps -= skews_cal
coinc_timestamps += skews_coinc  ## ???? or different sign, value for flight time has to be constant
print(coinc_timestamps)

print "after correction"
cal_timestamps_x = np.nanmin(cal_timestamps, axis=1)
coinc_timestamps_x = np.nanmin(coinc_timestamps, axis=1)
print(coinc_timestamps_x)

diff = cal_timestamps_x - coinc_timestamps_x

cal_mainDie = 'Stack_skew'
c_list = []
pad_list = []
h1d_list = []
leg_list = []

c_list.append(TCanvas('c{}'.format(cal_mainDie), 'Fit {}'.format(cal_mainDie), 200, 10, 900, 900))
pad_list.append(
    TPad('pad{}'.format(cal_mainDie), 'The pad with the histogram {}'.format(cal_mainDie), 0.05, 0.05, 0.95,
         0.95, 0))
h1d_list.append(TH1D('h1d - {}'.format(cal_mainDie), 'PV - {}'.format(cal_mainDie), (20000 - 0) / 20, -10000, 10000))
leg_list.append(TLegend())
# h1d_list[-1], valid_peaks_dic = __fitPeaks(h1d_list[-1])

peakInfoSave_all = set_char_TCanvas_TPad(c_list[-1], pad_list[-1], h1d_list[-1], leg_list[-1], diff,
                                         cal_mainDie)
if not peakInfoSave_all == None:
    with open('{}CalibCRTLog{}ROOT.txt'.format(pathtodirectoryRead, cal_mainDie), 'a') as fout:
        for peak in peakInfoSave_all.keys():
            # print(peakInfoSave_all[peak])
            df = pd.DataFrame(peakInfoSave_all[peak],
                              columns=['id', 'valid_peaks', 'all_peaks', 'fitStart', 'position', 'fitStop',
                                       'chi2_ndof', 'mean', 'mean_error', 'sigma', 'sigma_error',
                                       'CRT[(FWHM)]'])  # create a dataframe with the data of the current file

            fout.write(df.to_string(header=False,
                                    index=False))  # we write the dataframe with the index
            fout.write('\n')  # a newline to place correctly the next rows

mean = np.mean(diff)
std = np.std(diff)
bins = 500
#y, x = np.histogram(diff, bins, range=(mean - 3 * std, mean + 3 * std))
y, x = np.histogram(diff, bins, range=(-3000, 3000))

left, middle, right = psf.fwxm(x[0:bins], y, 0.5, True)
print "CRT", right - left
print "middle", middle

variable = raw_input('please enter')



'''106, 1, 6, 807990479098781, 4, 255, 3727, -13.8835, 18.4328, 14, 0, 0,
30, 166, 710, 189, 0, 0, 0, 0, 0, 0, 0, 0, 33, 251, 1108, 394, 0, 0, 0, 0, 0, 0, 0, 0, 21, 211, 336, 139, 0, 0, 0, 0, 0, 0, 0, 0, 15, 40, 64, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
807990479100276, 807990479098781, 0, 0, 0, 0, 807990479099409, 807990479099053, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

110, 1, 10, 807990479098743, 2, 63, 2045, 14.0645, 21.184, 9, 0, 0, 
0, 0, 0, 0, 0, 0, 0, 0, 239, 1191, 260, 42, 0, 0, 0, 0, 0, 0, 0, 0, 59, 152, 77, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 807990479098743, 807990479099558, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

106, 1, 6, 807992126255679, 2, 63, 2864, -13.3942, -20.8198, 134, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24, 88, 388, 242, 0, 0, 0, 0, 0, 0, 0, 0, 20, 231, 1374, 497, 0, 0, 0, 0, 0, 0, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 807992126256318, 807992126255679, 0, 0, 0, 0

110, 1, 10, 807992126255591, 2, 63, 1204, 16.6894, -21.0511, 142, 0, 0,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 21, 79, 118, 16, 0, 0, 0, 0, 0, 0, 0, 0, 34, 359, 533, 44,
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 807992126255591, 807992126255604


cal_photons = np.array([30, 166, 710, 189, 0, 0, 0, 0, 0, 0, 0, 0, 33, 251, 1108, 394, 0, 0, 0, 0, 0, 0, 0, 0, 21, 211, 336, 139, 0, 0, 0, 0, 0, 0, 0, 0, 15, 40, 64, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
coinc_photons = np.array([0, 0, 0, 0, 0, 0, 0, 0, 239, 1191, 260, 42, 0, 0, 0, 0, 0, 0, 0, 0, 59, 152, 77, 25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)

cal_timestamps = np.array([807990479100276, 807990479098781, 0, 0, 0, 0, 807990479099409, 807990479099053, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
coinc_timestamps = np.array([0, 0, 0, 0, 807990479098743, 807990479099558, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)

cal_timestamps[cal_timestamps==0] = np.nan
coinc_timestamps[coinc_timestamps == 0] = np.nan
'''

# time_matrix_c = np.zeros((1298, 73))
# time_matrix_c[:, 72] = 1
# time_matrix_c[1296, 0:36] = 1
# time_matrix_c[1296, 72] = 0
# time_matrix_c[1297, 36:72] = 1
# time_matrix_c[1297, 72] = 0
# time_differences_c = np.zeros(1298)
# matrix_line_c = 0
#
# #here we use the corrected timestamps given by the DPC calibration and already the minimum time is selected
# for cal_crystal in range(3425):
#     for coinc_crystal in range(3425):
#         # print matrix_line
#         events_cal_c = np.where(cal_crystal == cal_crystalS)[0]
#         events_coinc_c = np.where(coinc_crystal == coinc_crystalS)[0]
#         events_c = np.intersect1d(events_cal_c, events_coinc_c)
#         cal_time_selected_c = cal_timestamps_x[events_c]
#         #cal_time_selected_c = cal_time_selected_c[:, cal_crystal]
#         coinc_time_selected_c = coinc_timestamps_x[events_c]
#         #coinc_time_selected_c = coinc_time_selected_c[:, coinc_crystal]
#         diff_c = cal_time_selected_c - coinc_time_selected_c
#         print "events, cal_crystal, coinc_crystal", diff_c.shape, cal_crystal, coinc_crystal
#         if diff_c.shape[0] >= 1000:
#             time_matrix_c[matrix_line_c, 72] = 1
#             mean_c = np.mean(diff_c)
#             std_c = np.std(diff_c)
#             bins_c = 500
#             y_c, x_c = np.histogram(diff_c, bins_c, range=(mean_c - 30 * std_c, mean_c + 30 * std_c))
#
#             left_c, middle_c, right_c = psf.fwxm(x_c[0:bins_c], y_c, 0.5, False)
#             print left_c, middle_c, right_c
#             print "CRT FWHM: ", right_c - left_c
#
#             time_matrix_c[matrix_line_c, cal_crystal] = 1
#             time_matrix_c[matrix_line_c, coinc_crystal + 36] = 1
#             time_differences_c[matrix_line_c] = middle_c
#
#         matrix_line_c += 1