import random
import numpy as np
import ROOT
import array
import matplotlib.pyplot as plt

x = []
y = []
for i in range(15000):
    x.append(random.random() * 100)
    y.append(random.random() * 100)
x_gauss1 = []
y_gauss1 = []
x_gauss2 = []
y_gauss2 = []

for i in range(500000):
    x_gauss1.append(random.gauss(50, 2))
    y_gauss1.append(random.gauss(50, 2))
#    x_gauss2.append(random.gauss(20, 3))
#    y_gauss2.append(random.gauss(20, 3))

plt.figure()
plt.scatter(x, y, marker=".")
plt.scatter(x_gauss1, y_gauss1, marker=".", color="r")
plt.scatter(x_gauss2, y_gauss2, marker=".", color="g")
plt.show()

x_all = x + x_gauss1 + x_gauss2
y_all = y + y_gauss1 + y_gauss2
# plt.figure()
# plt.scatter(x_all, y_all)
# plt.show()
x_bins = np.arange(0, 100, 0.5)
y_bins = np.arange(0, 100, 0.5)
H, xedges, yedges = np.histogram2d(x_all, y_all, bins=(x_bins, y_bins))
H = H.T


# fig = plt.figure(figsize=(7, 3))
# ax = fig.add_subplot(111, title='Floodmap_Test')
# plt.imshow(H, interpolation='nearest', origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
# plt.show()

def __new_numpy1d_with_pointer(size):
    np_a = np.zeros(size, dtype=np.float64)
    pointer, read_only_flag = np_a.__array_interface__["data"]
    return np_a, pointer


binsx = len(x_bins) - 1
binsy = len(y_bins) - 1

source1, c_source = {}, array.array("L", [0] * binsx)
dest1, c_dest = {}, array.array("L", [0] * binsx)

for i in range(binsx):
    source1[i], c_source[i] = __new_numpy1d_with_pointer(binsy)
    dest1[i], c_dest[i] = __new_numpy1d_with_pointer(binsy)

for j in range(0, binsx):
    for k in range(0, binsy):
        source1[j][k] = H[j][k]

sigma_list = [5]
threshold_list = [50]
background_list = [False]
deconIterations_list = [30]
markov_list = [False]
averWindow_list = [3]
max_n_list = [50]

for sigma in sigma_list:
    for threshold in threshold_list:
        for background in background_list:
            for deconIterations in deconIterations_list:
                for markov in markov_list:
                    for averWindow in averWindow_list:
                        for max_n in max_n_list:
                            spectrum = ROOT.TSpectrum2(max_n)
                            npeaks = spectrum.SearchHighRes(c_source, c_dest, binsx, binsy, sigma, threshold,
                                                            background, deconIterations, markov, averWindow)
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
                            # plt.savefig("/media/janko.lambertus/pet-scratch/Janko/Master/Data/CIA_FT/Test3/PeaksFinderPlots/{}_{}_{}_{}_{}_{}.png".format(sigma, #threshold, background, deconIterations, markov, averWindow))
                            plt.show()
# 2_4_False_5_True_5
# 2_4_True_15_True_20
# 2_4_True_5_True_20