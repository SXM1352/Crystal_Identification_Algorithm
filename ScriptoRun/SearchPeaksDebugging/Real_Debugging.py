import ROOT
import numpy as np
import array
import matplotlib.pyplot as plt
import pickle

objects = []
try:
    with (
    open("/media/janko.lambertus/pet-scratch/Janko/Master/Data/CIA_FT/Test3/hist/hist111_15.pickle", "rb")) as openfile:
        while True:
            try:
                objects.append(pickle.load(openfile))
            except EOFError:
                break
except:
    with open("/media/janko.lambertus/pet-scratch/Janko/Master/Data/CIA_FT/Test3/SearchHighRes.pickle", 'rb') as f:
        objects.append(pickle.load(f, encoding='latin1'))


def __new_numpy1d_with_pointer(size):
    np_a = np.zeros(size, dtype=np.float64)
    pointer, read_only_flag = np_a.__array_interface__["data"]
    return np_a, pointer


binsx = 100
binsy = 100

source1, c_source = {}, array.array("L", [0] * binsx)
dest1, c_dest = {}, array.array("L", [0] * binsx)

for i in range(binsx):
    source1[i], c_source[i] = __new_numpy1d_with_pointer(binsy)
    dest1[i], c_dest[i] = __new_numpy1d_with_pointer(binsy)

for j in range(0, binsx):
    for k in range(0, binsy):
        source1[j][k] = objects[0][0][j][k]

sigma = 1.5
threshold = 8
background = True
deconIterations = 200
markov = False
averWindow = 3
max_n = 1000

spectrum = ROOT.TSpectrum2(max_n)
npeaks = spectrum.SearchHighRes(c_source, c_dest, binsx, binsy, sigma, threshold, markov, deconIterations, markov,
                                averWindow)
print("npeaks", npeaks)
posx = spectrum.GetPositionX()
posy = spectrum.GetPositionY()
x = []
y = []
for kl in range(npeaks):
    x.append(objects[0][1][int(posx[kl])])
    y.append(objects[0][2][int(posy[kl])])

fig = plt.figure(figsize=(7, 3))
ax = fig.add_subplot(111, title='imshow: square bins')
plt.imshow(objects[0][0].T, interpolation='nearest', origin='lower',
           extent=[objects[0][1][0], objects[0][1][-1], objects[0][2][0], objects[0][2][-1]])
# ax = fig.add_subplot(111, title='pcolormesh: actual edges',
#        aspect='equal')
# X, Y = np.meshgrid(objects[0][1], objects[0][2])
# ax.pcolormesh(X, Y, objects[0][0].T)
plt.colorbar()
plt.scatter(x, y, color="r", s=6)
plt.show()


