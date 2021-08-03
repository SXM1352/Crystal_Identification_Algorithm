import h5py
import numpy as np
import time

##################Einstellen###############
n_segments = 35
path = "/media/janko.lambertus/pet-scratch/Janko/Master/Data/2021_06_04/All_Photons/"
file_name = "Data_0_24"
n_train = 20000
n_test = 6000
###########################################






list_pos_train = []
list_photons_train = []
list_pos_test = []
list_photons_test = []

for i in range(n_segments):
    list_pos_train.append([])
    list_photons_train.append([])
    list_pos_test.append([])
    list_photons_test.append([])

data = h5py.File("{}{}".format(path, file_name), "r")

# for i in data["posX"][:100]:
#     for j in range(len(list_pos)):
#         if len(list_pos[j]) == 3:
#             continue
#         if data["posX"][i] == j:
#             list_pos[j].append(data["posX"][i])
#             list_photons[j].append(data["photons"][i])

for i in range(n_segments):
    print(i)
    start = time.time()
    list_ind = np.where(data["posX"][:len(data["posX"])] == i)[0]
    # list_ind = np.where(data["posX"][:1000] == i)[0]

    for j in range(len(list_ind)):
        if len(list_pos_train[i]) == n_train:
            if len(list_pos_test[i]) == n_test:
                break
            list_pos_test[i].append(data["posX"][list_ind[j]])
            list_photons_test[i].append(data["photons"][list_ind[j]])
            continue
        list_pos_train[i].append(data["posX"][list_ind[j]])
        list_photons_train[i].append(data["photons"][list_ind[j]])
    print(len(list_pos_train[i]), len(list_photons_train[i]))
    print(len(list_pos_test[i]), len(list_photons_test[i]))
    print("This needed {} seconds".format(time.time()-start))

# file = h5py.File(path+"reference.hdf5", "a")
# file["posY"] = np.reshape(list_pos_train, (n_segments*n_train))
# file["cal_photons"] = np.reshape(list_photons_train, (n_segments*n_train, len(list_photons_train[0][0])))
# file.close()
#
# file = h5py.File(path+"test.hdf5", "a")
# file["posY"] = np.reshape(list_pos_test, (n_segments*n_test))
# file["cal_photons"] = np.reshape(list_photons_test, (n_segments*n_test, len(list_photons_test[0][0])))
# file.close()
