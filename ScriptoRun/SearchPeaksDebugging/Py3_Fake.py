import random
import numpy as np
import ROOT
import array
import matplotlib.pyplot as plt
import ctypes

x = []
y = []
for i in range(15000):
    x.append(random.random() * 100)
    y.append(random.random() * 100)

x_gauss1 = []
y_gauss1 = []


for i in range(500000):
    x_gauss1.append(random.gauss(50, 2))
    y_gauss1.append(random.gauss(50, 2))

# plt.figure()
# plt.scatter(x,y,marker=".")
# plt.scatter(x_gauss1, y_gauss1, marker=".", color="r")
# plt.scatter(x_gauss2, y_gauss2, marker=".", color="g")
# plt.show()


x_all = x + x_gauss1
y_all = y + y_gauss1

# plt.figure()
# plt.scatter(x_all, y_all)
# plt.show()
x_bins = np.arange(0, 100, 0.5)
y_bins = np.arange(0, 100, 0.5)
binsx = len(x_bins) - 1
binsy = len(y_bins) - 1
dest = np.zeros((binsx, binsy))

# fig = plt.figure(figsize=(7, 3))
# ax = fig.add_subplot(111, title='Floodmap_Test')
# plt.imshow(H, interpolation='nearest', origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
# plt.show()

sigma_list = [5]
threshold_list = [50]
background_list = [False]
deconIterations_list = [30]
markov_list = [False]
averWindow_list = [3]
max_n_list = [10]

H, xedges, yedges = np.histogram2d(x_all, y_all, bins=(x_bins, y_bins))
H = H.T

for sigma in sigma_list:
    for threshold in threshold_list:
        for background in background_list:
            for deconIterations in deconIterations_list:
                for markov in markov_list:
                    for averWindow in averWindow_list:
                        for max_n in max_n_list:

                            spectrum = ROOT.TSpectrum2(max_n)
                            npeaks = spectrum.SearchHighRes(np.array(H, dtype=np.float64), dest, binsx, binsy,
                                                            sigma, threshold, background, deconIterations, markov,
                                                            averWindow)
                            print("npeaks", npeaks)
                            posx = spectrum.GetPositionX()
                            posy = spectrum.GetPositionY()
                            x_pos = []
                            y_pos = []
                            for kl in range(npeaks):
                                x_pos.append(xedges[int(posx[kl])])
                                y_pos.append(yedges[int(posy[kl])])

                            # spectrum.Print()
                            fig = plt.figure(figsize=(7, 3))
                            ax = fig.add_subplot(111, title='imshow: square bins')
                            plt.imshow(H, interpolation='nearest', origin='lower',
                                       extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])

                            plt.colorbar()
                            plt.scatter(x_pos, y_pos, color="r", s=6)
                            plt.show()
