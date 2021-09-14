import random
import numpy as np
import ROOT
import matplotlib.pyplot as plt


x = []

for i in range(15000):
    x.append(random.random() * 100)
x_gauss1 = []

for i in range(500000):
    x_gauss1.append(random.gauss(42, 2))

x_all = x + x_gauss1

x_bins = np.arange(0, 100, 0.5)
binsx = len(x_bins) - 1

dest = np.zeros(binsx)

sigma_list = [5]
threshold_list = [50]
background_list = [False]
deconIterations_list = [30]
markov_list = [False]
averWindow_list = [3]
max_n_list = [10]

h = ROOT.TH1D("peakfit", "MFB Peak Fit", binsx, 0, 100)

for i in range(len(x_all)):
    h.Fill(x_all[i])

source = np.zeros(binsx)
dest = np.zeros(binsx)


for i in range(binsx):
    source[i] = h.GetBinContent(i)
h.Draw("COL")

for sigma in sigma_list:
    for threshold in threshold_list:
        for background in background_list:
            for deconIterations in deconIterations_list:
                for markov in markov_list:
                    for averWindow in averWindow_list:
                        for max_n in max_n_list:

                            spectrum = ROOT.TSpectrum(max_n)

                            npeaks = spectrum.SearchHighRes(np.array(source, dtype=np.float32), np.array(dest, dtype=np.float32), binsx, sigma,
                                                            threshold, background, deconIterations, markov, averWindow)
                            print("npeaks", npeaks)
                            posx = spectrum.GetPositionX()
                            x_pos = []
                            for kl in range(npeaks):
                                x_pos.append(x_bins[int(posx[kl])])

                            print("Peaks: ", x_pos)
                            plt.figure()
                            plt.hist(x_all, bins=binsx)
                            plt.show()

