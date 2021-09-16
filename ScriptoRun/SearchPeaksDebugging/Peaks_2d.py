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
x_gauss2 = []
y_gauss2 = []
x_gauss3 = []
y_gauss3 = []

for i in range(500000):
    x_gauss1.append(random.gauss(42, 2))
    y_gauss1.append(random.gauss(42, 2))
    x_gauss2.append(random.gauss(60, 2))
    y_gauss2.append(random.gauss(80, 2))
    x_gauss3.append(random.gauss(30, 2))
    y_gauss3.append(random.gauss(20, 2))

x_all = x + x_gauss1 + x_gauss2 + x_gauss3
y_all = y + y_gauss1 + y_gauss2 + y_gauss3

x_bins = np.arange(0, 100, 0.5)
binsx = len(x_bins) - 1
y_bins = np.arange(0, 100, 0.5)
binsy = len(y_bins) - 1
dest = np.zeros((binsx, binsy))

sigma = 5
threshold = 50
background = False
deconIterations = 30
markov = False
averWindow = 3
max_n = 10

h = ROOT.TH2D("peakfit", "MFB Peak Fit", binsx, 0, 100, binsy, 0, 100)

for i in range(len(x_all)):
    h.Fill(x_all[i], y_all[i])

# source = np.zeros((binsx, binsy), dtype=np.float64)
# dest = np.zeros((binsx, binsy), dtype=np.float64)

source, c_source = {}, array.array("L", [0]*binsx)
dest, c_dest = {}, array.array("L", [0]*binsx)
def new_numpy1d_with_pointer(size):
    np_a = np.zeros(size, dtype=np.float64)
    pointer, read_only_flag = np_a.__array_interface__["data"]
    return np_a, pointer

for i in xrange(binsx):
    source[i], c_source[i] = new_numpy1d_with_pointer(binsy)
    dest[i], c_dest[i] = new_numpy1d_with_pointer(binsy)

histogram = np.zeros((binsx, binsy))

for i in range(binsx):
    for j in range(binsy):
        source[i][j] = h.GetBinContent(i, j)
        histogram[i][j] = h.GetBinContent(i, j)
h.Draw("COL")


# def create_pointer(bins):
#     data = np.zeros(bins)
#     pointers = []
#     pointers_pointer = []
#     for i in range(bins):
#         pointers.append(ctypes.byref(ctypes.c_double(data[i])))
#         pointers_pointer.append(ctypes.byref(ctypes.c_wchar(pointers[i])))
#     return data, pointers

# def create_pointer(bins):
#     data = np.zeros((bins, bins), dtype=np.float64)
#     c_float_p = ctypes.POINTER(ctypes.c_float)
#     data_p = data.ctypes.data_as(c_float_p)
#     return data, data_p
#
#
# a, b = create_pointer(binsx)
# for i in range(binsx):
#     for j in range(binsy):
#         a[i][j] = h.GetBinContent(i, j)


spectrum = ROOT.TSpectrum2(max_n)

npeaks = spectrum.SearchHighRes(c_source, c_dest, binsx, binsy, sigma,
                                threshold, background, deconIterations, markov, averWindow)
print("npeaks", npeaks)
posx = spectrum.GetPositionX()
posy = spectrum.GetPositionY()
x_pos = []
y_pos = []
for kl in range(npeaks):
    x_pos.append(x_bins[int(posx[kl])])
    y_pos.append(y_bins[int(posy[kl])])

print("x_pos = ", x_pos)
print("y_pos = ", y_pos)
fig = plt.figure(figsize=(7, 3))
ax = fig.add_subplot(111, title='imshow: square bins')
plt.imshow(histogram, interpolation='nearest', origin='lower',
           extent=[x_bins[0], x_bins[-1], y_bins[0], y_bins[-1]])

plt.colorbar()
plt.scatter(x_pos, y_pos, color="r", s=6)
plt.show()

