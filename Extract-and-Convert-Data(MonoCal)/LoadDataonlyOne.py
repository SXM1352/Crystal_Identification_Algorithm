# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 14:57:01 2020

@author: David
"""


def loadData(filename, read="all", reference=False):
    # type: (object, object, object) -> object
    """
    Read data preprocessed data from files. Supported types are hdf5 and npz.

    @param filename: file to read
    @param read: choose which data are read. If option "all" is used, all available data are read. Choose single
    datasets by using a list of strings.
    @param reference: hdf5 allows to copy the data to RAM or make a reference to the file on disk, default: False
    @return: dict of the read data
    """
    # check input
    if read != "all" and not isinstance(read, list):
        print "input for read not understood, no data read"
        return -1
    read_data = {}
    if isinstance(filename, basestring):
        if filename.endswith(".hdf5"):
            file = h5py.File(filename, "r")
            if read == "all":
                to_read = file.keys()
            else:
                to_read = read
            for elem in to_read:
                if reference:
                    read_data[elem] = file[elem]
                else:
                    read_data[elem] = file[elem][:]
        elif filename.endswith(".npz"):
            file = np.load(filename)
            if read == "all":
                to_read = file.files
            else:
                to_read = read
            for elem in to_read:
                read_data[elem] = file[elem]
        else:
            print "file type is not supported"
    return read_data

def _loadData(file, datasets):
    data = loadData(file, datasets)
    return tuple(data[datasets[i]] for i in range(len(datasets)))

#datasets = {".hdf5": ["cal_photons", "cal_anger", "cal_cog", "cal_cog000", "cal_cog100", "cal_cog010", "cal_cog110", "cal_cog001", "cal_cog101", "cal_cog011", "cal_cog111" ]}

datasets = ["cal_cog"]


def loadDataHyp(test, datasets):
    """!
    Loads data from specified pickle file. It creates a variable
    for every set of data

    @param ref: path to file containing the data for training
    @type ref: str
    @param test: path to file containing the data for testing
    @type test: str
    @param datasets: selected data
    @type test: str or list of str
    @return: None
    """
#    all_datasets = self._split_datasets(datasets)
#    current_dataset = next(all_datasets)
#    current_dataset = self._replace_default_in_dataset(ref, current_dataset)
    #photonsRef, angerRef, cogRef, cog000Ref, cog100Ref, cog010Ref, cog110Ref, cog001Ref, cog101Ref, cog011Ref, cog111Ref = loadData(ref, current_dataset)
    #cogRef = loadData(ref, dataset)

#    current_dataset = next(all_datasets)
#    current_dataset = self._replace_default_in_dataset(test, current_dataset)
    #photonsTest, angerTest, cogTest, cog000Test, cog100Test, cog010Test, cog110Test, cog001Test, cog101Test, cog011Test, cog111Test = loadData(test, current_dataset)
    cogTest = loadData(test, datasets)
    # attack in next refactoring, default as classifier is not longer suitable
#    referenceLabels = angerRef
#    testLabels = angerTest
    return cogTest