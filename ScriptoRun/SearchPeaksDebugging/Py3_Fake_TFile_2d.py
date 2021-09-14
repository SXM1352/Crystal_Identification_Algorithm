import random
import numpy as np
import ROOT
import array
import matplotlib.pyplot as plt
import ctypes
import copy

x = []
y = []
for i in range(15000):
    x.append(random.random() * 100)
    y.append(random.random() * 100)

x_gauss1 = []
y_gauss1 = []

for i in range(500000):
    x_gauss1.append(random.gauss(87, 2))
    y_gauss1.append(random.gauss(87, 2))

x_all = x + x_gauss1
y_all = y + y_gauss1

x_bins = np.arange(0, 100, 0.5)
y_bins = np.arange(0, 100, 0.5)
binsx = len(x_bins) - 1
binsy = len(y_bins) - 1

dest = np.zeros((binsx,binsy))
source = np.zeros((binsx, binsy))

sigma_list = [5]
threshold_list = [50]
background_list = [False]
deconIterations_list = [30]
markov_list = [False]
averWindow_list = [3]
max_n_list = [100]

#source = np.histogram(x_all, binsx)[0]

h = ROOT.TH2D("peakfit", "MFB Peak Fit", binsx, 0, 100, binsy, 0, 100)

for i in range(len(x_all)):
    h.Fill(x_all[i], y_all[i])

source = np.zeros((binsx, binsy))
dest = np.zeros((binsx, binsy))
# for i in range(len(dest)):
#     for j in range(len(dest[i])):
#         dest[i][j] =

for i in range(binsx):
    for j in range(binsy):
        source[i][j] = h.GetBinContent(i, j)

h.Draw("COL")





for sigma in sigma_list:
    for threshold in threshold_list:
        for background in background_list:
            for deconIterations in deconIterations_list:
                for markov in markov_list:
                    for averWindow in averWindow_list:
                        for max_n in max_n_list:

                            spectrum = ROOT.TSpectrum2(max_n)

                            npeaks = spectrum.SearchHighRes(np.array(source, dtype=np.float64), np.array(dest, dtype=np.float64), binsx, binsy, sigma,
                                                            threshold, background, deconIterations, markov, averWindow)
                            print("npeaks", npeaks)
                            posx = spectrum.GetPositionX()
                            x_pos = []
                            y_pos = []
                            for kl in range(npeaks):
                                x_pos.append(x_bins[int(posx[kl])])
                                y_pos.append(y_bins[int(posy[kl])])


                            fig = plt.figure(figsize=(7, 3))
                            ax = fig.add_subplot(111, title='imshow: square bins')
                            plt.imshow(source, interpolation='nearest', origin='lower',
                                       extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]])

                            plt.colorbar()
                            plt.scatter(x_pos, y_pos, color="r", s=6)
                            plt.show()

