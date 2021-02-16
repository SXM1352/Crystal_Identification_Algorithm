import cPickle as pickle
import logging

from PSFTools import PSFTools
from Geometry import GeometryDivide
from voxelizer import voxelizer

#sys.path.insert(1, os.path.join(sys.path[0], ".."))
from Help import *

from Positioning.XGB_helper import eval_function_xgb
from .Helper import Helper


class sciKitSkeleton(object, eval_function_xgb):
    def __init__(self):
        self._classifier = False
        self.sk = None
        self.psf = PSFTools()
        self._add_features = None
        self._known_datasets = {".hdf5": ["cal_photons", "cal_anger", "cal_cog", "cal_cog000", "cal_cog100", "cal_cog010", "cal_cog110", "cal_cog001", "cal_cog101", "cal_cog011", "cal_cog111" ],
                                ".npz": ["photons", "posX", "posY"]}

    @property
    def add_features(self):
        return self._add_features

    @add_features.setter
    def add_features(self, add_features):
        if not isinstance(add_features, list):
            print "add features has to be list of strings"
            return -1
        self._add_features = add_features
        self.sk._add_features = add_features

    def saveModel(self, file):
        """!
        Saves the current model to a pickle.

        @param file: file
        @type file: string
        @return: None
        @rtype:
        """
        pickle.dump(self.sk, open(file, "wb"), protocol=-1)

    def saveEvalResults(self, file):
        """!
        Saves evaluation results obtained during the training process if available. (XGB only).
        @param file: filename
        @type file: string
        @return: None
        @rtype:
        """
        pickle.dump(self.sk.evals_result(), open(file, "wb"), protocol=-1)

    def loadModel(self, file):
        """!
        Loads a saved model from specified pickle file. Tries to load add features to the
        sket class from the private variable of sket.sk.

        @param file: path to file containing the model
        @type file: string
        @return: None
        @rtype:
        """
        self.sk = pickle.load(open(file, "rb"))

        try:
            self._add_features = self.sk._add_features
            logging.info("Features loaded from pickle file")
        except:
            pass

    def _loadData(self, file, datasets):
        """!
        Loads data from specified pickle file. It creates a variable
        for every set of data

        @param file: path to file containing the data
        @type ref: str
        @param datasets: selected data
        @type test: str or list of str
        @return: sets of data
        @rtype: tuple
        """
        data = loadData(file, datasets)
        return tuple(data[datasets[i]] for i in range(len(datasets)))

    def _split_datasets(self, datasets):
        if datasets == "":
            datasets = ["default"]
        if isinstance(datasets[0], list):
            splitted_datasets = (datasets[i] for i in range(len(datasets)))
        else:
            splitted_datasets = (datasets for i in range(5))
        return splitted_datasets

    def _replace_default_in_dataset(self, file, dataset):
        if dataset[0] == "default":
            if file.endswith(".hdf5"):
                return self._known_datasets[".hdf5"]
            elif file.endswith(".npz"):
                return self._known_datasets[".npz"]
            else:
                print "file format not known"
                return dataset
        else:
            return dataset

    def loadData(self, ref, test, datasets=""):
        all_datasets = self._split_datasets(datasets)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(ref, current_dataset)
        self._photonsRef, self._posXRef, self._posYRef = self._loadData(ref, current_dataset)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(test, current_dataset)
        self._photonsTest, self._posXTest, self._posYTest = self._loadData(test, current_dataset)
        # attack in next refactoring, default as classifier is not longer suitable
        self._referenceLabels = []
        self._testLabels = []
        if self._classifier:
            for elem in range(self._photonsRef.shape[0]):
                self._referenceLabels.append(str(self._posXRef[elem]) + "_" + str(self._posYRef[elem]))
            for elem in range(self._photonsTest.shape[0]):
                self._testLabels.append(str(self._posXTest[elem]) + "_" + str(self._posYTest[elem]))
        else:
            self._referenceLabels = np.column_stack((self._posXRef, self._posYRef))
            self._testLabels = np.column_stack((self._posXTest, self._posYTest))

    def loadDataPickles_and_save(self):
        self.dicval_000 = {}
        self.dicval_100 = {}
        self.dicval_010 = {}
        self.dicval_111 = {}

        self.dicpos_000 = {"pos": [-1, -1]}  # x and y from COG HVD
        self.dicpos_100 = {"pos": [-1, -1]}
        self.dicpos_010 = {"pos": [-1, -1]}
        self.dicpos_111 = {"pos": [-1, -1]}

        self.dicpv_000 = {}  # photon values from COG HVD
        self.dicpv_100 = {}
        self.dicpv_010 = {}
        self.dicpv_111 = {}
        self.list_DBFiles = ["00", "0", ""]

        self.list_DBFiles_2 = [range(10), range(10, 100), range(100, 150)]
        self.list_save_dic = {"dicval_000":self.dicval_000, "dicval_100":self.dicval_100, "dicval_010":self.dicval_010, "dicval_111":self.dicval_111, "dicpos_000":self.dicpos_000, "dicpos_100":self.dicpos_100, "dicpos_010":self.dicpos_010, "dicpos_111":self.dicpos_111, "dicpv_000":self.dicpv_000, "dicpv_100":self.dicpv_100, "dicpv_010":self.dicpv_010, "dicpv_111":self.dicpv_111}
        for name in self.list_save_dic.keys():
            print("name is: ", name)
            n_events = 0
            for i_db_n, i_db in enumerate(self.list_DBFiles):
                print("Check")
                i_db_2 = self.list_DBFiles_2[i_db_n]
                for j_db_2 in i_db_2:
                    folder_dir = "/home/david.perez/Desktop/20210209_2m-2019-10-18_PickleData/" + str(i_db) + str(j_db_2)
                    with open('{}/{}.pickle'.format(folder_dir, name), "rb") as fin:
                        while True:
                            try:
                                dic_hvd = pickle.load(fin)
                            except EOFError:
                                break
                            for i in dic_hvd.keys():
                                self.list_save_dic[name][n_events] = dic_hvd[i]
                                n_events += 1
            self.save_data_pickles("/home/david.perez/Desktop", self.list_save_dic[name], name)
            print("saved")

    def loadTOTALData_Pickles(self):
        self.dicval_000 = {}
        self.dicval_100 = {}
        self.dicval_010 = {}
        self.dicval_111 = {}

        self.dicpos_000 = {"pos": [-1, -1]}  # x and y from COG HVD
        self.dicpos_100 = {"pos": [-1, -1]}
        self.dicpos_010 = {"pos": [-1, -1]}
        self.dicpos_111 = {"pos": [-1, -1]}

        self.dicpv_000 = {}  # photon values from COG HVD
        self.dicpv_100 = {}
        self.dicpv_010 = {}
        self.dicpv_111 = {}

        self.list_save_dic = {"dicval_000":self.dicval_000, "dicval_100":self.dicval_100, "dicval_010":self.dicval_010, "dicval_111":self.dicval_111, "dicpos_000":self.dicpos_000, "dicpos_100":self.dicpos_100, "dicpos_010":self.dicpos_010, "dicpos_111":self.dicpos_111, "dicpv_000":self.dicpv_000, "dicpv_100":self.dicpv_100, "dicpv_010":self.dicpv_010, "dicpv_111":self.dicpv_111}
        for name in self.list_save_dic.keys():
            folder_dir = "/home/david.perez/Desktop/"
            with open('{}/{}-TOTAL.pickle'.format(folder_dir, name), "rb") as fin:
                dic_hvd = pickle.load(fin)
            self.list_save_dic[name] = dic_hvd
        self._cogRef = []

        self._cog000Ref = []
        self._cog100Ref = []
        self._cog010Ref = []
        self._cog111Ref = []

        self._pv000Ref = []
        self._pv100Ref = []
        self._pv010Ref = []
        self._pv111Ref = []


        for i in self.list_save_dic["dicval_000"].keys():
            self._cogRef.append([int(self.list_save_dic["dicval_000"][i]), int(self.list_save_dic["dicval_100"][i]), int(self.list_save_dic["dicval_010"][i]), int(self.list_save_dic["dicval_111"][i])])
        for i in self.list_save_dic["dicpos_000"].keys()[0:-1]:
            for j in range(len(self.list_save_dic["dicpos_000"][i][0])):
                self._cog000Ref.append([float(self.list_save_dic["dicpos_000"][i][0][j]),float(self.list_save_dic["dicpos_000"][i][1][j])])
                self._cog100Ref.append([float(self.list_save_dic["dicpos_100"][i][0][j]),float(self.list_save_dic["dicpos_100"][i][1][j])])
                self._cog010Ref.append([float(self.list_save_dic["dicpos_010"][i][0][j]),float(self.list_save_dic["dicpos_010"][i][1][j])])
                self._cog111Ref.append([float(self.list_save_dic["dicpos_111"][i][0][j]),float(self.list_save_dic["dicpos_111"][i][1][j])])
        for i in self.list_save_dic["dicpv_000"].keys():
            self._pv000Ref.append(float(self.list_save_dic["dicpv_000"][i]))
            self._pv100Ref.append(float(self.list_save_dic["dicpv_100"][i]))
            self._pv010Ref.append(float(self.list_save_dic["dicpv_010"][i]))
            self._pv111Ref.append(float(self.list_save_dic["dicpv_111"][i]))

        self._cogRef = np.array(self._cogRef)

        self._cog000Ref = np.array(self._cog000Ref)
        self._cog100Ref = np.array(self._cog100Ref)
        self._cog010Ref = np.array(self._cog010Ref)
        self._cog111Ref = np.array(self._cog111Ref)

        self._pv000Ref = np.array(self._pv000Ref)
        self._pv100Ref = np.array(self._pv100Ref)
        self._pv010Ref = np.array(self._pv010Ref)
        self._pv111Ref = np.array(self._pv111Ref)
        print("Arrays ready")

    #    return self._cogRef, self._cog000Ref, self._cog100Ref, self._cog010Ref, self._cog111Ref, self._pv000Ref, self._pv100Ref, self._pv010Ref, self._pv111Ref

    def save_data_pickles(self, folder, dic_HVD, name):
        with open('{}/{}-TOTAL.pickle'.format(folder, name), 'wb') as handle:
            pickle.dump(dic_HVD, handle, protocol=pickle.HIGHEST_PROTOCOL)


    def loadDataHyp(self, ref, test, datasets=""):
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
        all_datasets = self._split_datasets(datasets)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(ref, current_dataset)
        self._photonsRef, self._angerRef, self._cogRef, self._cog000Ref, self._cog100Ref, self._cog010Ref, self._cog110Ref, self._cog001Ref, self._cog101Ref, self._cog011Ref, self._cog111Ref, self._pv000Ref, self._pv100Ref, self._pv010Ref, self._pv110Ref, self._pv001Ref, self._pv101Ref, self._pv011Ref, self._pv111Ref = self._loadData(ref, current_dataset)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(test, current_dataset)
        self._photonsTest, self._angerTest, self._cogTest, self._cog000Test, self._cog100Test, self._cog010Test, self._cog110Test, self._cog001Test, self._cog101Test, self._cog011Test, self._cog111Test, self._pv000Test, self._pv100Test, self._pv010Test, self._pv110Test, self._pv001Test, self._pv101Test, self._pv011Test, self._pv111Test = self._loadData(test, current_dataset)
        # attack in next refactoring, default as classifier is not longer suitable
        self._referenceLabels = self._angerRef
        self._testLabels = self._angerTest
#        if self._classifier:
#            for elem in range(self._photonsRef.shape[0]):
#                self._referenceLabels.append(str(self._posXRef[elem]) + "_" + str(self._posYRef[elem]))
#            for elem in range(self._photonsTest.shape[0]):
#                self._testLabels.append(str(self._posXTest[elem]) + "_" + str(self._posYTest[elem]))
#        else:
#            self._referenceLabels = np.column_stack((self._posXRef, self._posYRef))
#            self._testLabels = np.column_stack((self._posXTest, self._posYTest))        

    def fitData(self, use_eval=False, **kwargs):
        """!
        Trains the model. Parameter can be specified via instance.sk.set_params().

        @return: None
        @rtype:
        """
        if use_eval is True:
            try:
                self.sk.fit(self._photonsRef, self._referenceLabels, eval_set=[(self._photonsTest, self._testLabels)], eval_metric=self._multiple_eval, **kwargs)
            except:
                self._referenceLabels = np.reshape(self._referenceLabels, (self._referenceLabels.size,))
                self._photonsRef = np.reshape(self._photonsRef, (self._photonsRef.size,))
                self.sk.fit(self._photonsRef, self._referenceLabels, eval_set=[(self._photonsTest, self._testLabels)], eval_metric=self._multiple_eval, **kwargs)
        else:
            try:
                self.sk.fit(self._photonsRef, self._referenceLabels, **kwargs)
            except:
                self._referenceLabels = np.reshape(self._referenceLabels, (self._referenceLabels.size,))
                self._photonsRef = np.reshape(self._photonsRef, (self._photonsRef.size,))
                self.sk.fit(self._photonsRef, self._referenceLabels, **kwargs)


    def findPosition(self, element):
        """!
        Finds the position for the element in the loaded test data.

        @param element: element of the test data
        @type element: int
        @return: estimated position
        @rtype: tuple (posX, posY), float
        """
        label = self.sk.predict(self._photonsTest[element])[0]
        if self._classifier:
            position = label.split("_")
            posX, posY = position[0], position[1]
            return (posX, posY)
        else:
            posX, posY = label[0], label[1]
            return (posX, posY)

    def score(self):
        """!
        Calculates the score of the current fit regarding to the loaded test data. The score is defined by the ratio of
         exactly positioned events.

        @return: score
        @rtype: float
        """
        score = self.sk.score(self._photonsTest, self._testLabels)
        print "Current score: ", score
        return score

    def extractTestDataPSF(self, posX, posY, is_close=True, atol=0.001):
        """!
        Extract data suitable for PSFTools class for a given position.
        In the case that given position is not found in grid, functions exits with error: "list index out of range"

        @param k: Number of NN
        @type k: int
        @param posX: Position X
        @type posX: float
        @param posY: Position Y
        @type posY: float
        @param is_close: Accept events with position within a tolerance of 0.001 mm instead of equality. Can be useful to
        exclude floating point errors. Options decreases speed of function (order of 10 ms). Default: True
        @type is_close: True/False
        @param atol: absolute tolerance if is_close option is used
        @type atol: float
        @return: list of data suitable for PSFTools class
        @rtype: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        """
        data = [] #format: posX, posY, last line: posXRef, posYRef
        if is_close:
            indexList = np.intersect1d(np.argwhere(np.isclose(self._posXTest, posX, atol=atol) == True), np.argwhere(np.isclose(self._posYTest, posY, atol= atol) == True), assume_unique=False)
        else:
            indexList = np.intersect1d(np.argwhere(self._posXTest == posX), np.argwhere(self._posYTest == posY), assume_unique=False)
        if indexList.shape[0] == 0:
            print "No test data at the given position found."
            return -1
        logging.debug("shape of index list: %s", len(indexList))
        #for event in indexList:
        #    posX, posY = self.findPosition(event)
        #    data.append([posX, posY])
        posX = self.skX.predict(self._photonsTest[indexList])
        posY = self.skY.predict(self._photonsTest[indexList])
        data = np.column_stack((posX, posY))
        data = np.vstack((data, [self._posXTest[indexList[1]], self._posYTest[indexList[1]]]))
        return np.asarray(data).astype(float)


    def TreefindOptimum(self, min_depth=1, max_depth=15, show_plot=False, set_optimum_parameter=True):
        """!
        Finds the optimum depth of the decision tree classifier. For the quality of the fitted model, the score
        (see score method) is the valuation standard. Additionally, scores for different regions of the data set are
        calculated using PSFTools scores function. Results can be displayed using showPlot flag.

        @param min_depth: Minimum depth of tree
        @type min_depth: int
        @param max_depth: Maximum depth of tree
        @type max_depth: int
        @param show_plot: show results of optimization of the model, default: False
        @type show_plot: True/False
        @param set_optimum_parameter: Applies the found optimum parameter and fits the model again, default: True
        @type set_optimum_parameter: True/False
        @return: optimum depth
        @rtype: int
        """
        depth = []
        score = []
        middleScore = []
        cornerScore1  = []
        cornerScore2 = []
        for depth_walk in range(min_depth, max_depth+1):
            self.sk.set_params(max_depth=depth_walk, min_samples_leaf=150, min_samples_split=150)
            self.fitData()
            depth.append(depth_walk)
            score.append(self.score())
            gridDimensions =  PositioningHelper().findGrid(self._posXTest, self._posYTest)
            middlePoint = PositioningHelper().findGridMiddle(self._posXTest, self._posYRef)
            middleScore.append(self.psf.score(self.extractTestDataPSF(middlePoint[0], middlePoint[1]),1.5))
            cornerScore1.append(self.psf.score(self.extractTestDataPSF(gridDimensions[0], gridDimensions[2]), 1.5))
            cornerScore2.append(self.psf.score(self.extractTestDataPSF(gridDimensions[1], gridDimensions[3]), 1.5))
        if show_plot:
            plt.figure()
            plt.subplot(211)
            plt.title("Score vs depth of decision tree")
            plt.plot(depth, score)
            plt.subplot(212)
            plt.title("Score vs depth of decision tree")
            plt.plot(depth, middleScore, label="middle")
            plt.plot(depth, cornerScore1, label="corner1")
            plt.plot(depth, cornerScore2, label="corner2")
            plt.legend()
            plt.savefig("TreeFindOptimum.png")
            plt.show()
        if set_optimum_parameter:
            self.sk.set_params(max_depth=depth[score.index(max(score))], min_samples_leaf=50)
        return depth[score.index(max(score))]

class sciKitSkeletonLin(sciKitSkeleton):
    def __init__(self, classifier= None, zData = False):
        self.skX = None
        self.skY = None
        if classifier is True:
            print "This option is not longer supported, please use an older commit"
        self._zData = zData
        if zData:
            self.skZ = None
            self._known_datasets = {".hdf5": ["cal_photons", "posX", "posY", "posZ"],
                                    ".npz": ["photons", "posX", "posY", "posZ"]}
        else:
            self._known_datasets = {".hdf5": ["cal_photons", "posX", "posY"],
                                    ".npz": ["photons", "posX", "posY"]}
        self.psf = PSFTools()



    def loadData(self, ref, test, datasets=""):
        """!
        Loads the specified data and creates suitable labels.

        @param ref: path to reference data
        @type ref: string
        @param test: path to test data
        @type test: string
        @return: None
        @rtype:
        """
        all_datasets = self._split_datasets(datasets)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(ref, current_dataset)
        if self._zData:
            self._photonsRef, self._posXRef, self._posYRef, self._posZRef = self._loadData(ref, current_dataset)
        else:
            self._photonsRef, self._posXRef, self._posYRef = self._loadData(ref, current_dataset)
        current_dataset = next(all_datasets)
        current_dataset = self._replace_default_in_dataset(test, current_dataset)
        if self._zData:
            self._photonsTest, self._posXTest, self._posYTest, self._posZTest = self._loadData(test, current_dataset)
        else:
            self._photonsTest, self._posXTest, self._posYTest = self._loadData(test, current_dataset)


    def saveModel(self, file):
        """!
        Saves the current model to a pickle.

        @param file: file
        @type file: string
        @return: None
        @rtype:
        """
        pickle.dump(self.skX, open(os.path.join(os.path.dirname(file), "X_" + os.path.basename(file)), "wb"), protocol=-1)
        pickle.dump(self.skY, open(os.path.join(os.path.dirname(file), "Y_" + os.path.basename(file)), "wb"), protocol=-1)
        if self._zData:
            pickle.dump(self.skZ, open(os.path.join(os.path.dirname(file), "Z_" + os.path.basename(file)), "wb"), protocol=-1)

    def loadModel(self, file1, file2, file3 = ""):
        """!
        Loads a saved model from specified pickle file.

        @param file1: path to file containing the model for x direction
        @type file1: string
        @param file2: path to file containing the model for y direction
        @type file2: string
        @return: None
        @rtype:
        """
        self.skX = pickle.load(open(file1, "rb"))
        self.skY = pickle.load(open(file2, "rb"))
        if file3 != "":
            self.skZ = pickle.load(open(file3, "rb"))

    def fitData(self, direction=""):
        """!
        Trains the model. Parameter can be specified via instance.sk.set_params().

        @return: None
        @rtype:
        """
        if direction == "":
            self.skX.fit(self._photonsRef, self._XreferenceLabels)
            self.skY.fit(self._photonsRef, self._YreferenceLabels)
            if self._zData:
                self.skZ.fit(self._photonsRef, self._ZreferenceLabels)
        elif direction == "z":
            self.skZ.fit(self._photonsRef, self._ZreferenceLabels)
        elif direction == "x":
            self.skX.fit(self._photonsRef, self._XreferenceLabels)
        elif direction == "y":
            self.skY.fit(self._photonsRef, self._YreferenceLabels)


    def score(self, direction = ""):
        """!
        Calculates the score of thepsf current fit regarding to the loaded test data. For classifiers, the score is defined
        by the ratio of exactly positioned events.

        @return: score
        @rtype: float
        """
        if direction == "":
            scoreX = self.skX.score(self._photonsTest, self._XtestLabels)
            scoreY = self.skY.score(self._photonsTest, self._YtestLabels)

            if self._zData:
                scoreZ = self.skZ.score(self._photonsTest, self._ZtestLabels)
                print "Current score X: ", scoreX, "\t" , "Y:", scoreY, "\t", "Z:", scoreZ
                return {"scoreX": scoreX, "scoreY": scoreY, "scoreZ": scoreZ}

            else:
                print "Current score X: ", scoreX, "\t", "Y:", scoreY
                return {"scoreX": scoreX, "scoreY": scoreY}

        elif direction == "x":
            scoreX = self.skX.score(self._photonsTest, self._XtestLabels)
            print "Current score X: ", scoreX
            return {"scoreX": scoreX}

        elif direction == "y":
            scoreY = self.skY.score(self._photonsTest, self._YtestLabels)
            print "Current score Y: ", scoreY
            return {"scoreY": scoreY}

        elif direction == "z":
            scoreZ = self.skZ.score(self._photonsTest, self._ZtestLabels)
            print "Current score Z: ", scoreZ
            return {"scoreZ": scoreZ}


    def findPosition(self, element, direction=""):
        """!
        Finds the position for the element in the loaded test data.

        @param element: element of the test data
        @type element: int
        @return: estimated position
        @rtype: tuple (posX, posY), float
        """
        posX = self.skX.predict(self._photonsTest[element])[0]
        posY = self.skY.predict(self._photonsTest[element])[0]

        if self._zData:
            posZ = self.skZ.predict(self._photonsTest[element])[0]
            if self._classifier:
                posX = float(posX)
                posY = float(posY)
                posZ = float(posZ)
            if direction == "x":
                return posX
            elif direction == "y":
                return posY
            elif direction == "z":
                return posZ
            else:
                return (posX, posY, posZ)

        else:
            if self._classifier:
                posX = float(posX)
                posY = float(posY)
            if direction == "x":
                return posX
            elif direction == "y":
                return posY
            else:
                return (posX, posY)

    def TreefindOptimum(self, obj, direction="x", min_depth=1, max_depth=15, show_plot=False, set_optimum_parameter=True):
        """!
        Finds the optimum depth of the decision tree classifier. For the quality of the fitted model, the score
        (see score method) is the valuation standard. Additionally, scores for different regions of the data set are
        calculated using PSFTools scores function. Results can be displayed using showPlot flag.

        @param min_depth: Minimum depth of tree
        @type min_depth: int
        @param max_depth: Maximum depth of tree
        @type max_depth: int
        @param show_plot: show results of optimization of the model, default: False
        @type show_plot: True/False
        @param set_optimum_parameter: Applies the found optimum parameter and fits the model again, default: True
        @type set_optimum_parameter: True/False
        @return: optimum depth
        @rtype: int
        """
        depth = []
        score = []
        middleScore = []
        cornerScore1  = []
        cornerScore2 = []
        for depth_walk in range(min_depth, max_depth+1):
            print "Depth ", depth_walk
            obj.set_params(max_depth=depth_walk)
            self.fitData(direction=direction)
            depth.append(depth_walk)
            scoreVal = self.score(direction=direction)
            if direction=="x":
                scoreVal = scoreVal["scoreX"]
            elif direction=="y":
                scoreVal = scoreVal["scoreY"]
            else:
                scoreVal = scoreVal["scoreZ"]
            score.append(scoreVal)
            if self._zData:
                pass

            else:   # TODO: extractTestDataPSF adjustment for no bins
                gridDimensions =  PositioningHelper().findGrid(self._posXTest, self._posYTest)
                middlePoint = PositioningHelper().findGridMiddle(self._posXTest, self._posYRef)
                middleScore.append(self.psf.score(self.extractTestDataPSF(middlePoint[0], middlePoint[1]),1.5))
                cornerScore1.append(self.psf.score(self.extractTestDataPSF(gridDimensions[0], gridDimensions[2]), 1.5))
                cornerScore2.append(self.psf.score(self.extractTestDataPSF(gridDimensions[1], gridDimensions[3]), 1.5))

            pickle.dump(obj, open("model_" + direction + "_depth_" + str(depth_walk) + ".p", "wb"), protocol=-1)
            #pickle.dump(self.skY, open(os.path.join(os.path.dirname(file), "Y_" + os.path.basename(file)), "wb"),protocol=-1)
        if show_plot:
            plt.figure()
            if self._zData:
                plt.title("Score vs depth of decision tree")
                plt.plot(depth, score)
                plt.legend()
                plt.savefig("optimization" + direction + ".png")
                #plt.show()
            else:
                plt.subplot(211)
                plt.title("Score vs depth of decision tree")
                plt.plot(depth, score)
                plt.subplot(212)
                plt.title("Score vs depth of decision tree")
                plt.plot(depth, middleScore, label="middle")
                plt.plot(depth, cornerScore1, label="corner1")
                plt.plot(depth, cornerScore2, label="corner2")
                plt.legend()
                plt.savefig("optimization" + direction + ".png")
                #plt.show()
        if set_optimum_parameter:
            obj.set_params(max_depth=depth[score.index(max(score))], min_samples_leaf=50)
        return depth[score.index(max(score))]

    def extractTestDataPSFLin(self, pos, direction):
        data = [] #format: posX, posY, last line: posXRef, posYRef
        indexList = [] #list for saving indices of BackUp_Data ("global indices")
        for row in range(self._photonsTest.shape[0]):
            if direction == "x":
                if pos == self._posXTest[row]:
                    indexList.append(row)
            elif direction == "y":
                if pos == self._posYTest[row]:
                    indexList.append(row)
        logging.debug("shape of index list: %s", len(indexList))
        for event in indexList:
            pos = self.findPosition(event, direction)
            if direction == "x":
                data.append([pos, 0])
            elif direction == "y":
                data.append([0, pos])
        if direction == "x":
            data.append([self._posXTest[indexList[1]], 0])
        elif direction == "y":
            data.append([0, self._posYTest[indexList[1]]])
        return np.asarray(data).astype(float)

class TreeClassifier(sciKitSkeleton):
    def __init__(self):
        self._classifier=True
        self.sk = DecisionTreeClassifier()
        self.psf = PSFTools()


from sklearn.tree import DecisionTreeRegressor
class TreeRegressor(sciKitSkeleton):
    def __init__(self):
        self._classifier=False
        self.sk = DecisionTreeRegressor()
        self.psf = PSFTools()

from sklearn.ensemble import RandomForestClassifier
class RandomForrestClassifier(sciKitSkeleton):
    def __init__(self):
        self._classifier=True
        self.sk = RandomForestClassifier()
        self.psf = PSFTools()
        self.sk.set_params()

    def ForrestFindOptimum(self, min_depth=1, max_depth=15, max_trees=10, show_plot=False, set_optimum_parameter=True):
        """!
        Finds the optimum depth of the decision tree classifier. For the quality of the fitted model, the score
        (see score method) is the valuation standard. Additionally, scores for different regions of the data set are
        calculated using PSFTools scores function. Results can be displayed using showPlot flag.

        @param min_depth: Minimum depth of tree
        @type min_depth: int
        @param max_depth: Maximum depth of tree
        @type max_depth: int
        @param show_plot: show results of optimization of the model, default: False
        @type show_plot: True/False
        @param set_optimum_parameter: Applies the found optimum parameter and fits the model again, default: True
        @type set_optimum_parameter: True/False
        @return: optimum depth
        @rtype: int
        """
        depth = []
        score = []
        middleScore = []
        cornerScore1  = []
        cornerScore2 = []
        for tree in range(1,max_trees):
            print "trees", tree
            self.sk.set_params(n_estimators=tree)
            for depth_walk in range(min_depth, max_depth+1):
                self.sk.set_params(max_depth=depth_walk, min_samples_leaf=50)
                self.fitData()
                depth.append(depth_walk)
                score.append(self.score())
                gridDimensions =  PositioningHelper().findGrid(self._posXTest, self._posYTest)
                middlePoint = PositioningHelper().findGridMiddle(self._posXTest, self._posYRef)
                middleScore.append(self.psf.score(self.extractTestDataPSF(middlePoint[0], middlePoint[1]),1.5))
                cornerScore1.append(self.psf.score(self.extractTestDataPSF(gridDimensions[0], gridDimensions[2]), 1.5))
                cornerScore2.append(self.psf.score(self.extractTestDataPSF(gridDimensions[1], gridDimensions[3]), 1.5))
        if show_plot:
            plt.figure()
            plt.subplot(211)
            plt.title("Score vs depth of decision tree")
            plt.plot(depth, score)
            plt.subplot(212)
            plt.title("Score vs depth of decision tree")
            plt.plot(depth, middleScore, label="middle")
            plt.plot(depth, cornerScore1, label="corner1")
            plt.plot(depth, cornerScore2, label="corner2")
            plt.legend()
            plt.show()
        if set_optimum_parameter:
            self.sk.set_params(max_depth=depth[score.index(max(score))], min_samples_leaf=50)
        return depth[score.index(max(score))]

class sciKitSkeletonLinPin():
    """!
    Wrapper class designed for the use with line collimator and sciKit-Learn regression methods.

    Example
    --------
    from sklearn.ensemble import GradientTreeBoosting
    sket = sciKitSkeletonLinPin()
    sket.skX = GradientTreeBoosting()
    sket.skX = GradientTreeBoosting()
    sket.skX.set_params(n_estimators=50)
    sket.skY.set_params(n_estimators=50)
    sket.loadData("up", "swapped", "pinhole")
    sket.fitData()
    sket.score()

    """
    def __init__(self):
        self.skX = None
        self.skY = None

    def loadData(self, up, swapped, pin):
        """!
        Load data.

        @param up: data of "up" orientation of the crystal, photon-values and y coordinate given
        @type up: path to data
        @param swapped: data of "swapped" orientation of the crystal, photon-values and x coordinate given
        @type swapped: path to data
        @param pin: data generated with pinhole collimator, photon-values, x and y coordinates given
        @type pin: path to data
        @return: None
        @rtype:
        """
        """help = Helper()
        self._photonsXRef, self._posXRef, y = help.loadData(swapped)
        self._photonsYRef, x, self._posYRef = help.loadData(up)
        self._photonsPin, self._posXPin, self._posYPin = help.loadData(pin)
        # round positions to eliminate floating point errors
        self._posXRef, self._posYRef = np.round(self._posXRef, 2), np.round(self._posYRef, 2)
        self._posXPin, self._posYPin = np.round(self._posXPin, 2), np.round(self._posYPin, 2)"""
        if up.endswith(".hdf5"):
            ref = loadData(up)
            self._photonsYRef, x, self._posYRef = ref["cal_photons"], ref["posX"], ref["posY"]
        else:
            help = Helper()
            self._photonsYRef, x, self._posYRef = help.loadData(up)
        if swapped.endswith(".hdf5"):
            test = loadData(swapped)
            self._photonsXRef, self._posXRef, y = test["cal_photons"], test["posX"], test["posY"]
        else:
            help = Helper()
            self._photonsXRef, self._posXRef, y = help.loadData(swapped)
        if pin.endswith(".hdf5"):
            ref = loadData(pin)
            self._photonsPin, self._posXPin, self._posYPin = ref["cal_photons"], ref["posX"], ref["posY"]
        else:
            help = Helper()
            self._photonsPin, self._posXPin, self._posYPin = help.loadData(pin)

    def fitData(self):
        """!
        Fit the model.

        @return: None
        @rtype:
        """
        self.skX.fit(self._photonsXRef, self._posXRef)
        self.skY.fit(self._photonsYRef, self._posYRef)

    def getFilterValues(self, filter_threshold=10):
        """!
        Searches for all positions that are not unique and returns them. Using the extractPSFTestDataFilter function,
        these values can be excluded from the PSFData and the following analysis.

        Hint:
        This is an experimental function and maybe useful for RandomForestRegressor-models. Those events that lead to
        the same predicted position seem to worsen the performance parameter (especially bias vector).

        @param filter_threshold:
        @type filter_threshold:
        @return:
        @rtype:
        """
        filterX = self.skX.predict(self._photonsXRef)
        val_filterX, counts_filterX = np.unique(filterX, return_counts=True)
        filterX = val_filterX[np.argwhere(counts_filterX >= filter_threshold)]
        #print filterX
        print "filter ratio X: ", np.sum(counts_filterX[counts_filterX >= filter_threshold])*1./val_filterX.shape[0]
        filterY = self.skY.predict(self._photonsYRef)
        val_filterY, counts_filterY = np.unique(filterY, return_counts=True)
        filterY = val_filterY[np.argwhere(counts_filterY >= filter_threshold)]
        #print filterY
        print "filter ratio Y: ", np.sum(counts_filterY[counts_filterY >= filter_threshold])*1./val_filterY.shape[0]
        self._filterX = filterX
        self._filterY = filterY
        return (filterX, filterY)

    def score(self):
        """!
        Calculates the score for both directions on the basis of the pinhole data.

        @return: None
        @rtype:
        """
        print self.skX.score(self._photonsPin, self._posXPin)
        print self.skY.score(self._photonsPin, self._posYPin)

    def findPosition(self, indexList):
        """!
        Finds the position of pinhole-test-events.

        @param indexList: Indices of the events under test.
        @type indexList: Int, list of ints, array of ints
        @return: position (x and y)
        @rtype: tuple of floats
        """
        posX = self.skX.predict(self._photonsPin[indexList])
        posY = self.skY.predict(self._photonsPin[indexList])
        return (posX, posY)

    def extractTestDataPSF(self, posX, posY, is_close=True, atol=0.001):
        """!
        Extract PSF-test-data for the given position.

        @param posX: position x
        @type posX:  float
        @param posY: position y
        @type posY: float
        @param is_close: Accept events with position within a tolerance of 0.001 mm instead of equality. Can be useful to
        exclude floating point errors. Options decreases speed of function (order of 10 ms). Default: True
        @type is_close: True/False
        @param atol: absolute tolerance if is_close option is used
        @type atol: float
        @return: PSF-test-data
        @rtype: np.array
        """
        if is_close:
            indexList = np.intersect1d(np.argwhere(np.isclose(self._posXPin, posX, atol=atol) == True), np.argwhere(np.isclose(self._posYPin, posY, atol= atol) == True), assume_unique=False)
        else:
            indexList = np.intersect1d(np.argwhere(self._posXPin == posX), np.argwhere(self._posYPin == posY), assume_unique=False)
        if indexList.shape[0] == 0:
            print "No test data at the given position found."
            return -1
        X, Y = self.findPosition(indexList)
        data = np.column_stack((X, Y))
        data = np.vstack((data, [posX, posY]))
        return data

    def extractTestDataPSFFilter(self, posX, posY):
        """!
        Extract PSF-test-data without those events that lead to positions created by getFilterValues function
        for the given position.

        @param posX: position x
        @type posX:  float
        @param posY: position y
        @type posY: float
        @return: PSF-test-data
        @rtype: np.array
        """
        psfdata = self.extractTestDataPSFRaw(posX, posY)
        #print "shape psfdata: ", psfdata.shape
        delX = []
        for elem in self._filterX:
            tmp = np.argwhere(psfdata == elem)
            if len(tmp) != 0:
                delX.append(tmp)
        delX = np.concatenate(delX)
        #print "delX", delX
        psfdata = np.delete(psfdata, delX, axis=0)
        #print "shape first delete:", psfdata.shape
        delY = []
        for elem in self._filterY:
            tmp = np.argwhere(psfdata == elem)
            if len(tmp) != 0:
                delY.append(tmp)
        delY = np.concatenate(delY)
        psfdata = np.delete(psfdata, delY, axis= 0)
        #print "final shape", psfdata.shape
        return psfdata

    def saveModel(self, file):
        """!
        Saves the current model to a pickle.

        @param file: file
        @type file: string
        @return: None
        @rtype:
        """
        pickle.dump(self.skX, open(os.path.join(os.path.dirname(file), "X_" + os.path.basename(file)), "wb"), protocol=-1)
        pickle.dump(self.skY, open(os.path.join(os.path.dirname(file), "Y_" + os.path.basename(file)), "wb"), protocol=-1)

    def loadModel(self, file1, file2):
        """!
        Loads a saved model from specified pickle file.

        @param file1: path to file containing the model for x direction
        @type file1: string
        @param file2: path to file containing the model for y direction
        @type file2: string
        @return: None
        @rtype:
        """
        self.skX = pickle.load(open(file1, "rb"))
        self.skY = pickle.load(open(file2, "rb"))

class sciKitSkeletonDOI(sciKitSkeleton):
    """!
    Wrapper class designed for the use with line collimator and sciKit-Learn regression methods for side irradiation.
    """
    def __init__(self):
        self._offset = 0. # trick for alignment of simulated and experimental coordinate system
        self.giveIndexList=False #give Index of event to KNN_1D() in find Position() if requested


    def loadDOIData(self, ref, test, datasets=[]):
        """!
        Load doi data created with PositionAdderDOI class.

        @param ref: path to reference data
        @type ref: string
        @param test: path to test data
        @type test: string
        """
        if ref.endswith(".npz"):
            ref = np.load(ref)
            self._photonsRef, self._posXRef, self._posYRef, self._doiRef = ref["photons"], ref["posX"], ref["posY"], ref["doi"]
        else:
            data = loadData(ref, datasets)
            self._photonsRef, self._posXRef, self._posYRef, self._doiRef = data[datasets[0]],data[datasets[1]], data[datasets[2]], data[datasets[3]]
        if test.endswith(".npz"):
            test = np.load(test)
            self._photonsTest, self._posXTest, self._posYTest, self._doiTest = test["photons"], test["posX"], test["posY"], \
                                                                               test["doi"]
        else:
            data = loadData(test, datasets)
            self._photonsTest, self._posXTest, self._posYTest, self._doiTest = data[datasets[0]], data[datasets[1]], \
                                                                               data[datasets[2]], data[datasets[3]]
        self._referenceLabels = self._doiRef
        self._testLabels = self._doiTest

    def findPosition(self, element):
        """!
        Finds the position of pinhole-test-events.

        @param indexList: Indices of the events under test.
        @type indexList: Int, list of ints, array of ints
        @return: doi
        @rtype: float or array of float
        """
        #return self.sk.predict(self._photonsTest[element].reshape((-1,self._photonsRef.shape[1])))
        if self.giveIndexList==True:
            return self.sk.predict(self._photonsTest[element],element)
        return self.sk.predict(self._photonsTest[element])

    def extractTestDataPSF(self, pos, psf_tools_comp = True, is_close=True, atol=0.001):
        """!
        Extract PSF test data for the use with PSFTools class.

        @param pos: position under test
        @type pos: float
        @param psf_tools_comp: Compatibility to PSFTools class (adds a second column with zeros),. default:True
        @type psf_tools_comp: True/False
        @param is_close: Accept events with position within a tolerance of 0.001 mm instead of equality. Can be useful to
        exclude floating point errors. Options decreases speed of function (order of 10 ms). Default: True
        @type is_close: True/False
        @param atol: absolute tolerance if is_close option is used
        @type atol: float
        @return: PSF-test-data
        @rtype: np.array
        """
        if is_close:
            indexList = np.where(np.isclose(self._testLabels, pos, atol=atol) == True)[0]
        else:
            indexList = np.where(self._testLabels == pos)[0]
        if indexList.shape[0] == 0:
            print "No test data at the given position found."
            return -1
        #print indexList
        data = self.findPosition(indexList)
        #print np.concatenate(data)
        #print pos
        data = data.flatten() # dirty quick trick, proove
        data += self._offset
        data = np.hstack((data, pos))
        if psf_tools_comp == False:
            return data
        else:
            data = np.column_stack((data, np.zeros( data.shape[0])))
            return data

    def extractTestDataPSFGlobal(self, psf_tools_comp=True):
        if psf_tools_comp is False:
            return self._testLabels - self.sk.predict(self._photonsTest)
        else:
            if self.giveIndexList==True:
                n=len(self._photonsTest)
                result = self.sk.predict(self._photonsTest,np.arange(0,n,1))
            else:
                result=self.sk.predict(self._photonsTest)
            #data = self._testLabels - self.sk.predict(self._photonsTest)
            data = np.empty(len(result))
            for i in range(len(result)):
                data[i] = self._testLabels[i] - result[i]
            data = np.hstack((data, 0.))
            data = np.column_stack((data, np.zeros(data.shape[0])))
            return data

class sciKitSkeleton1D(sciKitSkeletonDOI):
    def __init__(self):
        self.giveIndexList = False
        self._offset = 0.

    def loadData(self, ref, test, direction, datasets=[]):
        if ref.endswith(".hdf5"):
            ref = loadData(ref)
            self._photonsRef, self._posXRef, self._posYRef = ref[datasets[0]], ref[datasets[1]], ref[datasets[2]]
        else:
            help = Helper()
            self._photonsRef, self._posXRef, self._posYRef = help.loadData(ref)
        if test.endswith(".hdf5"):
            test = loadData(test)
            self._photonsTest, self._posXTest, self._posYTest = test[datasets[0]], test[datasets[1]], test[datasets[2]]
        else:
            help = Helper()
            self._photonsTest, self._posXTest, self._posYTest = help.loadData(test)
        if direction == "x":
            self._referenceLabels = self._posXRef
            self._testLabels = self._posXTest
        else:
            self._referenceLabels = self._posYRef
            self._testLabels = self._posYTest


class MultipleSket(sciKitSkeleton1D):
    def __init__(self):
        self.skets = {}
        self._div = GeometryDivide()
        self._geometry = self._div._geometries

    def loadData(self, ref, test, direction):
        help = Helper()
        self._photonsRef, self._posXRef, self._posYRef = help.loadData(ref)
        self._photonsTest, self._posXTest, self._posYTest = help.loadData(test)
        if direction == "x":
            self._referenceLabels = self._posXRef
            self._testLabels = self._posXTest
        else:
            self._referenceLabels = self._posYRef
            self._testLabels = self._posYTest

    def initialize(self):
        self._div.data = self._photonsRef
        self._div.label = self._referenceLabels
        self._div.detect_geometry()
        for elem in self._geometry:
            self.skets[elem] = sciKitSkeleton1D()
            self.skets[elem]._photonsRef, self.skets[elem]._referenceLabels = self._div.sort_geometry(elem)
        self._div.data = self._photonsTest
        self._div.label = self._testLabels
        self._div.detect_geometry()
        try:
            import xgboost
        except:
            print "xgboost seems not properly installed. Please check your installation and path."
            return -1
        for elem in self._geometry:
            self.skets[elem]._photonsTest, self.skets[elem]._testLabels = self._div.sort_geometry(elem)
            self.skets[elem].sk = xgboost.XGBRegressor()

    def to_all(self, command):
        for elem in self.skets:
            print "self.skets[" + str(elem) + "]." + command
            exec("self.skets[" + str(elem) + "]." + command)


class sciKitSkeletonSegmented(sciKitSkeletonDOI):
    def __init__(self):
        self._offset = 0  # trick for alignment of simulated and experimental coordinate system
        self.vox_ref = voxelizer()
        self.vox_test = voxelizer()
        self._estimators = {}
        self.sk = None

    def voxelize(self, **kwargs):
        self.vox_ref._photons = self._photonsRef
        self.vox_ref._posX = self._posXRef
        self.vox_ref._posY = self._posYRef
        self.vox_ref._posZ = np.ones(self._posXRef.shape[0])
        self.vox_test._photons = self._photonsTest
        self.vox_test._posX = self._posXTest
        self.vox_test._posY = self._posYTest
        self.vox_test._posZ = np.ones(self._posYTest.shape[0])
        self.vox_ref.voxelize(dimZ = 2, binsZ = 1, **kwargs)
        self.vox_test.voxelize(dimZ = 2, binsZ = 1, **kwargs)
        self.vox_ref.fillVoxelLUT()
        self.vox_test.fillVoxelLUT()

    @property
    def sk(self):
        return self.sk

    @sk.setter
    def sk(self, estimator_class):
        for voxel in self.vox_ref._voxelLUT.keys():
            self._estimators[voxel] = estimator_class()

    @sk.getter
    def sk(self, voxel):
        return self._estimators[voxel]

    def fitData(self):
        for voxel in self.vox_ref._voxelLUT.keys():
            if voxel in ["x", "y", "z"]:
                continue
            events = self.vox_ref._voxelLUT[voxel]
            photons = self._photonsRef[events]
            photons = photons.reshape((-1,))
            print photons
            label = self._doiRef[events]
            label = label.reshape((-1,))
            print label
            self._estimators[voxel].fit(photons, label)

    def score(self):
        voxels = []
        score_values = []
        for voxel in self.vox_test._voxelLUT.keys():
            if voxel in ["x", "y", "z"]:
                continue
            if voxel not in self.vox_test._voxelLUT.keys():
                continue
            events = self.vox_test._voxelLUT[voxel]
            photons = self._photonsTest[events]
            photons = photons.reshape((-1,))
            labels = self._testLabels[events]
            predict = self._estimators[voxel].predict(photons)
            photons = photons[~np.isnan(predict)]
            labels = labels[~np.isnan(predict)]
            labels = labels.reshape((-1,))
            try:
                score = self._estimators[voxel].score(photons, labels)
                print score
            except:
                pass
            voxels.append(voxel)
            score_values.append(score)
        score_values = np.asanyarray(score_values)
        average = np.nanmean(score_values)
        print "average score", average
        return score_values, voxels

    def findPosition(self, element):
        predicted = []
        for entry in element:
            voxel = self.vox_test._eventLUT[entry]
            if voxel not in self.vox_ref._voxelLUT.keys():
                continue
            predicted.append(self._estimators[voxel].predict([self._photonsTest[entry]]))
        predicted = np.asanyarray(predicted)
        predicted = predicted[~np.isnan(predicted)]
        return predicted


class sciKitSkeletonDualReadout(sciKitSkeleton1D):
    """!
    sket class dedicated for dual side readout.
    Example usage:
    sket = sciKitSkeletonDualReadout()
    sket.loadDaten(>>ref<<, >>test<<, ["posX","posY,"cal_photons_front","cal_photons_back"])
    sket.sk = >>training_model<<
    sket.add_features(["COG","colSum"],["COG","rowSum","colSum"])
    sket.prepareDataForTraining()
    sket.fitData()
    ...
    """
    def __init__(self):
        self._parameters = {"direction": "x",
                            "add_features_back": [],
                            "add_features_front": []}
        self._photonsRef = None
        self._photonsTest = None
        self._posXRef = None
        self._posYRef = None
        self._posXTest = None
        self._posYTest = None
        self.sk = None

    # ToDo Transform to property
    def add_features(self, add_features_back, add_features_front):
        """!
        Configure the features to add with FeatureAdder class. See the FeatureAdder class for a
        list of supported features.
        @param add_features_back: Features to add for the front detector.
        @type add_features_back: list of strings
        @param add_features_front: Features to add for the back detector.
        @rtype add_features_front: list of strings
        @return:
        """
        self._parameters["add_features_back"], self._parameters["add_features_front"] = add_features_back, add_features_front
        self.sk._add_features_back, self.sk._add_features_front = add_features_back, add_features_front

    def loadData(self, ref, test, datasets=[]):
        """!
        Load training and test data sets.

        Attention: Datasets may need to be specified in a different order than usual. Check!
        @param ref: training data
        @param test: test data
        @param datasets: position X, position Y, data front detector, data back detector
        @rtype datasets: list of strings
        @return:
        """
        data = loadData(ref, datasets)
        self._posXRef, self._posYRef, self._photonsRefFront, self._photonsRefBack = data[datasets[0]], data[datasets[1]], data[datasets[2]], data[datasets[3]]
        data = loadData(test, datasets)
        self._posXTest, self._posYTest, self._photonsTestFront, self._photonsTestBack = data[datasets[0]], data[datasets[1]], data[datasets[2]], data[datasets[3]]
        del data

    def getParams(self,**kwargs):
        return self._parameters

    def setParams(self, **kwargs):
        for key in kwargs:
            if key in self._parameters.keys():
                self._parameters[key] = kwargs[key]
            else:
                print key, "not known. For available parameters call getParams()"

    def prepareDataForTraining(self):
        """!
        Call this function before fitting a model to the data.

        The data of back- and front-detector are merged and the labels are set according to the
        specifications in the parameters of this class.
        @return:
        """
        self._photonsRef = np.column_stack((self._photonsRefFront, self._photonsRefBack))
        self._photonsTest = np.column_stack((self._photonsTestFront, self._photonsTestBack))
        if self._parameters["direction"] is "x":
            self._referenceLabels = self._posXRef
            self._testLabels = self._posXTest
        elif self._parameters["direction"] is "y":
            self._referenceLabels = self._posYRef
            self._testLabels = self._posYTest
        else:
            print "direction not known. Choose either x or y as direction"
