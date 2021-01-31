__author__ = 'florian.mueller'

"""
Modified by David 200629
"""

import numpy as np
import os
import copy
import h5py
import logging
from tqdm import tqdm
from ConfigParser import ConfigParser
import pickle
import matplotlib.pyplot as plt
import Help
from config import config

from BasicCluster import BasicCluster
from FeatureAdder import FeatureAdder
from Geometry import GeometryDivide

"""
Design goals:
-consistent and easy maintainable data management class
-output data format easy extendable
-filter options easy to apply
-including of corrections for photons counts and time stamps
-lower computational load, esp. RAM usage
-config parser: dataset/filter/value
"""

logging.basicConfig(level=logging.DEBUG)

class CreateData(object):
    def __init__(self, config_file=None):
        """!
        Constructor of CreateData class. The CreateData class is used to generate data suitable for MonoCal
        based on .CaptureDebugSingles or .DebugSingles output files from hitAnalysis in the experiment folder structure.
        Several filter can be applied to select the data which are configured in the CreateData.ini file.

        @param config_file: Path to the config file for this class.
        """
        self._found_files = None
        self._options = {"output_file_name_reference": "reference.hdf5",
                         "output_file_name_test": "test.hdf5",
                         "rootdir": "./",
                         "file_extension": ".DebugSingles",
                         "single_file": False,
                         "single_file_name": "",
                         "single_file_selection_dataset": "",
                         "swapped": False,
                         "reference_events": 900000,
                         "test_events": 100000,
                         "chaining_style": "iterative",
                         "sampling": "sorted",
                         "grid": {
                             "x": {"offset": 0.,
                                   "start": -1.,
                                   "step": -1.},
                             "y": {"offset": 0.,
                                   "start": -1.,
                                   "step": -1.},
                            },
                         "pixel_number" : 144,
                         "die_number" : 36,
                         "cal_stack" : 6,
                         "coinc_stack" :-1,
                         "anger_position" : True,
                         "cog_position" : True,
                         "photon_values" : True,
                         "tofpet" : False,
                         "chip_a": 0,
                         "chip_b": 0,
                         "energycalibration": False
                         }
        self._filter = {"min_photons": self._filter_min_photons,
                        "max_photons": self._filter_max_photons,
                        "min_dies": self._filter_min_die_readout,
                        "min_energy": self._filter_min_energy,
                        "max_energy": self._filter_max_energy,
                        "complete_events": self._filter_complete_events}
        self._filter_requested = {}

        if config_file is not None:
            self._config_parser(config_file)

        if self._options["energycalibration"] and self._options["tofpet"] and self._options["file_extension"] == ".hdf5":
            self._options["file_extension"] = 'unqualifiedClusters.hdf5'
        elif not self._options["energycalibration"] and self._options["tofpet"] and self._options["file_extension"] == ".hdf5":
            self._options["file_extension"] = '_coincClusters.hdf5'
            
        self._reference_data = {"cal_timestamps": np.empty((0, self._options["die_number"]), dtype=int)
                                #"coinc_timestamps": np.empty((0, self._options["die_number"]), dtype=int)
                                }
        self._test_data = {"cal_timestamps": np.empty((0, self._options["die_number"]), dtype=int)
                           #"coinc_timestamps": np.empty((0, self._options["die_number"]), dtype=int)
                           }
        self._current_data = {"data": {"cal_timestamps": np.empty((0, self._options["die_number"]), dtype=int),
                                       #"coinc_timestamps": np.empty((0, self._options["die_number"]), dtype=int)
                                       },
                              "selected_reference": 0,
                              "selected_test": 0}
#                              "meta_data": {"posX": np.empty((0, 1), dtype=float),
#                                            "posY": np.empty((0, 1), dtype=float)}}
        if self._options["tofpet"]:
            self._reference_data.update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=float),
                                         "coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=float)
                                         })
            self._test_data.update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=float),
                                    "coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=float)
                                    })
            self._current_data["data"].update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=float),
                                               "coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=float)
                                               })
        else:
            self._reference_data.update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                         #"coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                         })
            self._test_data.update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                    #"coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                    })
            self._current_data["data"].update({"cal_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                               #"coinc_photons": np.empty((0, self._options["pixel_number"]), dtype=int)
                                               })

        if self._options["anger_position"]:
            self._reference_data.update({"cal_anger": np.empty((0,2), dtype=float)
                                         #"coinc_anger": np.empty((0,2), dtype=float)
                                         })
            self._test_data.update({"cal_anger": np.empty((0,2), dtype=float)
                                   # "coinc_anger": np.empty((0,2), dtype=float)
                                    })
            self._current_data["data"].update({"cal_anger": np.empty((0,2), dtype=float)
                                               #"coinc_anger": np.empty((0,2), dtype=float)
                                               })
        
        if self._options["cog_position"]:
            self._reference_data.update({"cal_cog": np.empty((0,8), dtype=int),
                                         "cal_cog000": np.empty((0,2), dtype=float),
                                         "cal_cog100": np.empty((0,2), dtype=float),
                                         "cal_cog010": np.empty((0,2), dtype=float),
                                         "cal_cog110": np.empty((0,2), dtype=float),
                                         "cal_cog001": np.empty((0,2), dtype=float),
                                         "cal_cog101": np.empty((0,2), dtype=float),
                                         "cal_cog011": np.empty((0,2), dtype=float),
                                         "cal_cog111": np.empty((0,2), dtype=float)
                                         })
            self._test_data.update({"cal_cog": np.empty((0,8), dtype=int),
                                    "cal_cog000": np.empty((0,2), dtype=float),
                                    "cal_cog100": np.empty((0,2), dtype=float),
                                    "cal_cog010": np.empty((0,2), dtype=float),
                                    "cal_cog110": np.empty((0,2), dtype=float),
                                    "cal_cog001": np.empty((0,2), dtype=float),
                                    "cal_cog101": np.empty((0,2), dtype=float),
                                    "cal_cog011": np.empty((0,2), dtype=float),
                                    "cal_cog111": np.empty((0,2), dtype=float)
                                    })
            self._current_data["data"].update({"cal_cog": np.empty((0,8), dtype=int),
                                               "cal_cog000": np.empty((0,2), dtype=float),
                                               "cal_cog100": np.empty((0,2), dtype=float),
                                               "cal_cog010": np.empty((0,2), dtype=float),
                                               "cal_cog110": np.empty((0,2), dtype=float),
                                               "cal_cog001": np.empty((0,2), dtype=float),
                                               "cal_cog101": np.empty((0,2), dtype=float),
                                               "cal_cog011": np.empty((0,2), dtype=float),
                                               "cal_cog111": np.empty((0,2), dtype=float)
                                               })
        if self._options["photon_values"]:
            self._reference_data.update({"photonv_cog000": np.empty((0,1), dtype=float),
                                         "photonv_cog100": np.empty((0,1), dtype=float),
                                         "photonv_cog010": np.empty((0,1), dtype=float),
                                         "photonv_cog110": np.empty((0,1), dtype=float),
                                         "photonv_cog001": np.empty((0,1), dtype=float),
                                         "photonv_cog101": np.empty((0,1), dtype=float),
                                         "photonv_cog011": np.empty((0,1), dtype=float),
                                         "photonv_cog111": np.empty((0,1), dtype=float)
                                         })
            self._test_data.update({"photonv_cog000": np.empty((0,1), dtype=float),
                                    "photonv_cog100": np.empty((0,1), dtype=float),
                                    "photonv_cog010": np.empty((0,1), dtype=float),
                                    "photonv_cog110": np.empty((0,1), dtype=float),
                                    "photonv_cog001": np.empty((0,1), dtype=float),
                                    "photonv_cog101": np.empty((0,1), dtype=float),
                                    "photonv_cog011": np.empty((0,1), dtype=float),
                                    "photonv_cog111": np.empty((0,1), dtype=float)
                                    })
            self._current_data["data"].update({"photonv_cog000": np.empty((0,1), dtype=float),
                                               "photonv_cog100": np.empty((0,1), dtype=float),
                                               "photonv_cog010": np.empty((0,1), dtype=float),
                                               "photonv_cog110": np.empty((0,1), dtype=float),
                                               "photonv_cog001": np.empty((0,1), dtype=float),
                                               "photonv_cog101": np.empty((0,1), dtype=float),
                                               "photonv_cog011": np.empty((0,1), dtype=float),
                                               "photonv_cog111": np.empty((0,1), dtype=float)
                                               })

    def _config_parser(self, config_file):
        config = ConfigParser(allow_no_value=True)
        config.read(config_file)
        for item in config.items("options"):
            if item[0] in self._options:
                itemtype = type(self._options[item[0]])
                logging.debug("%s, %s", item, itemtype)
                self._options[item[0]] = itemtype(item[1])
                logging.debug("after setting: %s , %s", self._options[item[0]], type(self._options[item[0]]))
            else:
                logging.warning("%s not known. Please refer to documentation for further information.", item)
        for item in config.items("grid"):
            logging.debug("%s", item[0].split("/"))
            direction, option = item[0].split("/")
            if direction in self._options["grid"]:
                itemtype = type(self._options["grid"][direction][option])
                logging.debug("%s, %s", item, itemtype)
                self._options["grid"][direction][option] = itemtype(item[1])
                logging.debug("after setting: %s %s", self._options["grid"][direction][option], type(self._options["grid"][direction][option]))
            else:
                logging.warning("%s not known. Please refer to documentation for further information.", item)
        i = 0
        for item in config.items("filter"):
            dataset, filter, option = item[0].split("/")
            logging.debug("%s, %s, %s", dataset, filter, option)
            self._filter_requested[i] = [self._filter[filter], dataset, int(option)]
            i += 1
            logging.info("%s", self._filter_requested)

    def _search_files(self):
        import os
        self._found_files = []
        for root, dirnames, filenames in Help.walklevel(self._options["rootdir"], level=1):
            for filename in filenames:
                if filename.endswith(self._options["file_extension"]):
                    self._found_files.append(os.path.join(root, filename))

    def _read_files(self, file):
        if (self._options["file_extension"] == ".DebugCoincidentSingles" or self._options["file_extension"] == ".DebugSingles" or self._options["file_extension"] == "_coincClusters.txt" or self._options["file_extension"] == "unqualifiedClusters.txt" or self._options["file_extension"] == "_qualifiedClusters.txt"):
            BC = BasicCluster(file)
            self._current_data["data"]["cal_photons"] = BC.sortClusterPhotons(self._options["cal_stack"])
            self._current_data["data"]["cal_timestamps"] = BC.sortClusterTimeStampDies(self._options["cal_stack"])
            if self._options["anger_position"]:
                self._current_data["data"]["cal_anger"] = BC.sortClusterAngerPositions(self._options["cal_stack"])
            if self._options["cog_position"]:
                self._current_data["data"]["cal_cog"] = BC.sortClusterCOGPositions(self._options["cal_stack"])
                self._current_data["data"]["cal_cog000"] = BC.sortClusterCOGPositions000(self._options["cal_stack"])
                self._current_data["data"]["cal_cog100"] = BC.sortClusterCOGPositions100(self._options["cal_stack"])
                self._current_data["data"]["cal_cog010"] = BC.sortClusterCOGPositions010(self._options["cal_stack"])
                self._current_data["data"]["cal_cog110"] = BC.sortClusterCOGPositions110(self._options["cal_stack"])
                self._current_data["data"]["cal_cog001"] = BC.sortClusterCOGPositions001(self._options["cal_stack"])
                self._current_data["data"]["cal_cog101"] = BC.sortClusterCOGPositions101(self._options["cal_stack"])
                self._current_data["data"]["cal_cog011"] = BC.sortClusterCOGPositions011(self._options["cal_stack"])
                self._current_data["data"]["cal_cog111"] = BC.sortClusterCOGPositions111(self._options["cal_stack"])
            if self._options["photon_values"]:
                self._current_data["data"]["photonv_cog000"] = BC.sortPhotonValuesCOG000(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog100"] = BC.sortPhotonValuesCOG100(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog010"] = BC.sortPhotonValuesCOG010(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog110"] = BC.sortPhotonValuesCOG110(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog001"] = BC.sortPhotonValuesCOG001(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog101"] = BC.sortPhotonValuesCOG101(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog011"] = BC.sortPhotonValuesCOG011(self._options["cal_stack"])
                self._current_data["data"]["photonv_cog111"] = BC.sortPhotonValuesCOG111(self._options["cal_stack"])

            #if self._options["tofpet"]:
                # self._current_data["data"]["cal_channels"] = BC.sortClusterChannels(self._options["cal_stack"])
                # if self._options["coinc_stack"] != -1:
                #     self._current_data["data"]["coinc_channels"] = BC.sortClusterChannels(self._options["coinc_stack"])
                # else:
                #     self._current_data["data"]["coinc_channels"] = np.ones((len(self._current_data["data"]["cal_channels"]),2))*(-1)

#            if (not self._options["anger_position"]) and self._options["coinc_stack"] != -1:
#                self._current_data["data"]["coinc_photons"] = BC.sortClusterPhotons(self._options["coinc_stack"])
#                self._current_data["data"]["coinc_timestamps"] = BC.sortClusterTimeStampDies(self._options["coinc_stack"])
#                if self._options["cog_position"]:
#                    self._current_data["data"]["cal_cog"] = BC.sortClusterCOGPositions(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog000"] = BC.sortClusterCOGPositions000(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog100"] = BC.sortClusterCOGPositions100(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog010"] = BC.sortClusterCOGPositions010(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog110"] = BC.sortClusterCOGPositions110(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog001"] = BC.sortClusterCOGPositions001(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog101"] = BC.sortClusterCOGPositions101(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog011"] = BC.sortClusterCOGPositions011(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog111"] = BC.sortClusterCOGPositions111(self._options["cal_stack"])
#
#
#            elif self._options["anger_position"] and self._options["coinc_stack"] != -1:
#                self._current_data["data"]["cal_anger"] = BC.sortClusterAngerPositions(self._options["cal_stack"])
#                self._current_data["data"]["coinc_anger"] = BC.sortClusterAngerPositions(self._options["coinc_stack"])
#                self._current_data["data"]["coinc_photons"] = BC.sortClusterPhotons(self._options["coinc_stack"])
#                self._current_data["data"]["coinc_timestamps"] = BC.sortClusterTimeStampDies(self._options["coinc_stack"])
#                if self._options["cog_position"]:
#                    self._current_data["data"]["cal_cog"] = BC.sortClusterCOGPositions(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog000"] = BC.sortClusterCOGPositions000(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog100"] = BC.sortClusterCOGPositions100(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog010"] = BC.sortClusterCOGPositions010(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog110"] = BC.sortClusterCOGPositions110(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog001"] = BC.sortClusterCOGPositions001(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog101"] = BC.sortClusterCOGPositions101(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog011"] = BC.sortClusterCOGPositions011(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog111"] = BC.sortClusterCOGPositions111(self._options["cal_stack"])
#
#            elif self._options["anger_position"] and self._options["coinc_stack"] == -1:
#                self._current_data["data"]["cal_anger"] = BC.sortClusterAngerPositions(self._options["cal_stack"])
#                self._current_data["data"]["coinc_anger"] = np.ones(np.shape(self._current_data["data"]["cal_anger"]))*(-1)
#                self._current_data["data"]["coinc_photons"] = np.ones(np.shape(self._current_data["data"]["cal_photons"]))*(-1)
#                self._current_data["data"]["coinc_timestamps"] = np.ones(np.shape(self._current_data["data"]["cal_timestamps"]))*(-1)
#                if self._options["cog_position"]:
#                    self._current_data["data"]["cal_cog"] = BC.sortClusterCOGPositions(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog000"] = BC.sortClusterCOGPositions000(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog100"] = BC.sortClusterCOGPositions100(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog010"] = BC.sortClusterCOGPositions010(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog110"] = BC.sortClusterCOGPositions110(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog001"] = BC.sortClusterCOGPositions001(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog101"] = BC.sortClusterCOGPositions101(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog011"] = BC.sortClusterCOGPositions011(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog111"] = BC.sortClusterCOGPositions111(self._options["cal_stack"])
#            
#            else:
#                self._current_data["data"]["coinc_photons"] = np.ones(np.shape(self._current_data["data"]["cal_photons"]))*(-1)
#                self._current_data["data"]["coinc_timestamps"] = np.ones(np.shape(self._current_data["data"]["cal_timestamps"]))*(-1)
#                if self._options["cog_position"]:
#                    self._current_data["data"]["cal_cog"] = BC.sortClusterCOGPositions(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog000"] = BC.sortClusterCOGPositions000(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog100"] = BC.sortClusterCOGPositions100(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog010"] = BC.sortClusterCOGPositions010(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog110"] = BC.sortClusterCOGPositions110(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog001"] = BC.sortClusterCOGPositions001(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog101"] = BC.sortClusterCOGPositions101(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog011"] = BC.sortClusterCOGPositions011(self._options["cal_stack"])
#                    self._current_data["data"]["cal_cog111"] = BC.sortClusterCOGPositions111(self._options["cal_stack"])

        elif self._options["file_extension"] == ".hdf5" or self._options["file_extension"] == "unqualifiedClusters.hdf5" or self._options["file_extension"] == "_coincClusters.hdf5":
            print "in read hdf5 file"
            rd_file = h5py.File(file, "r")
            print rd_file.keys()
            if self._options["tofpet"]:
                if self._options["chip_a"] == self._options["cal_stack"] and self._options["chip_b"] == self._options["coinc_stack"]:
                    for elem in rd_file.keys():
                        #print elem
                        print rd_file[elem]
                        if elem[-1] == 'A' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["cal_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'A' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["cal_timestamps"] = rd_file[elem][:]
                        elif elem[-1] == 'B' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["coinc_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'B' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["coinc_timestamps"] = rd_file[elem][:]
                    rd_file.close()
                elif self._options["chip_a"] == self._options["cal_stack"] and self._options["coinc_stack"] == -1:
                    for elem in rd_file.keys():
                        #print elem[-1]
                        print rd_file[elem]
                        if elem[-1] == 'A' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["cal_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'A' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["cal_timestamps"] = rd_file[elem][:]
                    rd_file.close()
                    self._current_data["data"]["coinc_photons"] = np.ones(np.shape(self._current_data["data"]["cal_photons"])) * (-1)
                    self._current_data["data"]["coinc_timestamps"] = np.ones(np.shape(self._current_data["data"]["cal_timestamps"])) * (-1)
                elif self._options["chip_b"] == self._options["cal_stack"] and self._options["coinc_stack"] == -1:
                    for elem in rd_file.keys():
                        #print elem[-1]
                        print rd_file[elem]
                        if elem[-1] == 'B' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["cal_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'B' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["cal_timestamps"] = rd_file[elem][:]
                    rd_file.close()
                    self._current_data["data"]["coinc_photons"] = np.ones(np.shape(self._current_data["data"]["cal_photons"])) * (-1)
                    self._current_data["data"]["coinc_timestamps"] = np.ones(np.shape(self._current_data["data"]["cal_timestamps"])) * (-1)
                elif self._options["chip_b"] == self._options["cal_stack"] and self._options["chip_a"] == self._options["coinc_stack"]:
                    for elem in rd_file.keys():
                        #print elem
                        print rd_file[elem]
                        if elem[-1] == 'B' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["cal_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'B' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["cal_timestamps"] = rd_file[elem][:]
                        elif elem[-1] == 'A' and rd_file[elem].dtype == "float64":
                            self._current_data["data"]["coinc_photons"] = rd_file[elem][:]
                        elif elem[-1] == 'A' and rd_file[elem].dtype == "int64":
                            self._current_data["data"]["coinc_timestamps"] = rd_file[elem][:]
                    rd_file.close()
            else:
                for elem in rd_file.keys():
                    print rd_file[elem]
                    self._current_data["data"][elem] = rd_file[elem][:]
                rd_file.close()

        else:
            logging.error("file type not supported yet")

    def _back_up_read_data(self):
        # used in single-file-mode only, creates unique identifiers for the positions and back-ups data
        # as source for the positioning selections and filter operations
        if not isinstance(self._options["single_file_selection_dataset"], list):
            self._options["single_file_selection_dataset"] = self._options["single_file_selection_dataset"].split(",")
        logging.debug(self._options["single_file_selection_dataset"])
        selection_data = {}
        for elem in self._options["single_file_selection_dataset"]:
            selection_data[elem] = self._current_data["data"][elem].astype(str)
        for i, elem in enumerate(self._options["single_file_selection_dataset"]):
            if i == 0 and len(selection_data) == 1:
                identifier = selection_data[elem]
            elif i==0:
                identifier = np.char.add(selection_data[elem], "/")
            elif i == len(selection_data)-1:
                identifier = np.char.add(identifier, selection_data[elem])
            else:
                identifier = np.char.add(identifier, selection_data[elem])
                identifier = np.char.add(identifier, "/")
            print identifier
        for elem in self._current_data["data"].keys():
            try:
                tmp = self._current_data["data"][elem].shape[1]
            except:
                print "reshaping ", elem
                self._current_data["data"][elem] = self._current_data["data"][elem].reshape((-1, 1))
        self._back_up_data = copy.deepcopy(self._current_data)
        self._back_up_data["position_identifier"] = np.asanyarray(identifier)
        self._found_positions = np.unique(identifier)


    def _read_data_position(self, position):
        # used in single-file-mode only
        indices = np.where(position == self._back_up_data["position_identifier"])[0]
        print indices
        for elem in self._back_up_data["data"]:
            print elem
            self._current_data["data"][elem] = self._back_up_data["data"][elem][indices].copy()

    def _extract_coordinate(self, file = None):
        if self._options["single_file"]:
            position = map(float, file.split("/"))
            if len(position) != 2:
                posX = -1
                posY = -1
            else:
                posX, posY = position[0], position[1]
        elif self._options["tofpet"]:
            posY, posX = float(file.split("/")[-2].split("_")[-1][1:]), float(file.split("/")[-2].split("_")[-2][1:])
        else:
            posX, posY = map(float, file.split("/")[-2].split("_"))[0:2]
        print posX, posY
        posX -= self._options["grid"]["x"]["offset"]
        posY -= self._options["grid"]["y"]["offset"]
        self._current_data["meta_data"]["posX"] = posX
        self._current_data["meta_data"]["posY"] = posY
        # write the values also to this dict for selecting accepted files;
        # the "current data" dict is not used to maintain conformity with data structure
        self._options["grid"]["x"]["current"] = posX
        self._options["grid"]["y"]["current"] = posY


    def _swap_coordinates(self):
        if self._options["swapped"]:
            self._current_data["meta_data"]["posX"], self._current_data["meta_data"]["posY"] = self._current_data["meta_data"]["posY"], self._current_data["meta_data"]["posX"]
            self._options["grid"]["x"]["current"], self._options["grid"]["y"]["current"] = self._options["grid"]["y"]["current"], self._options["grid"]["x"]["current"]

    def _accept_position(self):
        for elem in self._options["grid"]:
            #print elem
            start_point = self._options["grid"][elem]["start"]
            offset = self._options["grid"][elem]["offset"]
            step = self._options["grid"][elem]["step"]
            if step == -1:
                continue
            current_position = self._options["grid"][elem]["current"]
            number_steps = (current_position + offset - start_point)/step
            logging.debug("number steps %s", number_steps)
            # prove if stepping in right direction
            if number_steps < 0:
                return False
            # prove if this is an integer step
            if not np.isclose(number_steps, np.round(number_steps, 0), atol=0.001):
                return False
        return True

    def _initiate_file(self, force=False):
        if not force:
            if os.path.isfile(self._options["output_file_name_reference"]) or os.path.isfile(self._options["output_file_name_test"]):
                print "Warning! Already existing hdf5 files would be overriden. " \
                      "Choose different file name for output. Aborting!"
                return -1
        self._file_reference = h5py.File(self._options["output_file_name_reference"], "w")
        self._file_test = h5py.File(self._options["output_file_name_test"], "w")
        self._file_reference_data_set = {}
        self._file_test_data_set = {}
        if self._options["single_file"]:
            selected_dataset_groups = ["data"]
        else:
           # selected_dataset_groups = ["data", "meta_data"]
           selected_dataset_groups = ["data"]
        for data_set in selected_dataset_groups:
            for elem in self._current_data[data_set].keys():
                try:
                    tmp = self._current_data[data_set][elem].shape[1]
                    print(elem)
                    print(tmp)
                    print(self._current_data[data_set][elem].shape)
                except:
                    print "reshaping ", elem
                    self._current_data[data_set][elem] = np.reshape(self._current_data[data_set][elem],(-1,1))
                self._file_reference_data_set[elem] = self._file_reference.create_dataset(elem, shape=(0,self._current_data[data_set][elem].shape[1]), dtype=self._current_data[data_set][elem].dtype, maxshape=(None, self._current_data[data_set][elem].shape[1]), compression="gzip")
                self._file_test_data_set[elem] = self._file_test.create_dataset(elem, shape=(0,self._current_data[data_set][elem].shape[1]), dtype=self._current_data[data_set][elem].dtype, maxshape=(None, self._current_data[data_set][elem].shape[1]), compression="gzip")

    def _save_data(self):
        print("save")
        if self._options["single_file"]:
            datasets = ["data"]
        else:
            #datasets = ["data", "meta_data"]
            datasets = ["data"]
        for data_set in datasets:
            if self._options["sampling"] == "random":
                # allows random sampling of the data, training and test are not mixed up
                total_data = self._current_data["selected_reference"] + self._current_data["selected_test"]
                random_shape = self._current_data["data"]["cal_photons"].shape[0]  # this are at least the total data or more
                sorted_indices = np.arange(0, random_shape)
                random_indices = np.random.choice(sorted_indices, total_data, replace=False)  # equals a permutation
                reference = random_indices[0:self._current_data["selected_reference"]]
                test = random_indices[-self._current_data["selected_test"]:]
                logging.debug("randomized selected reference events %s", reference.shape)
                logging.debug("randomized selected test events %s", test.shape)
                logging.debug("intersection test of random sampling: %s", np.intersect1d(reference, test))
            for elem in self._current_data[data_set].keys():
                # saving for reference data
                previous = self._file_reference_data_set[elem].shape[0]
                add = self._current_data["selected_reference"]
                new = previous + self._current_data["selected_reference"]
                logging.info("reference %s, previous, new %s %s", elem, previous, new)
                self._file_reference_data_set[elem].resize(new, 0)
                logging.debug("%s", self._file_reference_data_set[elem].shape)
                logging.debug("%s", self._current_data[data_set][elem])
                print(self._current_data[data_set][elem].shape)
                print(self._current_data[data_set]["cal_cog010"].shape)
                print(self._current_data[data_set]["cal_cog010"])
                if data_set is "meta_data":
                    logging.debug("in meta data")
                    self._file_reference_data_set[elem][previous:new] = self._current_data[data_set][elem]
                else:
                    if self._options["sampling"] == "random":
                        self._file_reference_data_set[elem][previous:new] = self._current_data[data_set][elem][reference]
                    else:
                        tmp = self._current_data[data_set][elem][0:add]
                        print(tmp)
                        print(tmp.shape)
                        if tmp.ndim == 1:
                            tmp = tmp.reshape(-1,1)
                        if tmp.shape[0] == 1:
                            tmp = tmp.reshape(-1,1)
                            tmp = tmp[0:add]
                        logging.debug("%s", self._file_reference_data_set[elem].shape)
                        self._file_reference_data_set[elem][previous:new] = tmp
                        del tmp
                # saving for test data
                previous = self._file_test_data_set[elem].shape[0]
                add = self._current_data["selected_test"]
                new = previous + self._current_data["selected_test"]
                logging.info("test %s, previous, new %s, %s", elem, previous, new)
                self._file_test_data_set[elem].resize(new, 0)
                if data_set is "meta_data":
                    self._file_test_data_set[elem][previous:new] = self._current_data[data_set][elem]*np.ones((add,1))
                else:
                    if self._options["sampling"] == "random":
                        self._file_test_data_set[elem][previous:new] = self._current_data[data_set][elem][test]
                    else:
                        tmp = self._current_data[data_set][elem][-add:]
                    if tmp.ndim == 1:
                        tmp = tmp.reshape(-1, 1)
                    if tmp.shape[0] == 1:
                        tmp = tmp.reshape(-1,1)
                        tmp = tmp[-add:]
                    self._file_test_data_set[elem][previous:new] = tmp

    def _chain_filters(self):
        if not bool(self._filter_requested):  # empty dicts evaluate to False in Python
            return -1
        # intersection style
        if self._options["chaining_style"] == "intersect":
            accepted_events = None
            for elem in self._filter_requested:
                indices = self._filter_requested[elem][0](self._current_data["data"][self._filter_requested[elem][1]], self._filter_requested[elem][2])
                if accepted_events is None:
                    accepted_events = indices
                else:
                    accepted_events = np.intersect1d(accepted_events, indices)
            for elem in self._current_data["data"]:
                self._current_data["data"][elem] = self._current_data["data"][elem][indices]
        # iterative style
        elif self._options["chaining_style"] == "iterative":
            for elem in self._filter_requested:
                indices = self._filter_requested[elem][0](self._current_data["data"][self._filter_requested[elem][1]], self._filter_requested[elem][2])
                for dataset in self._current_data["data"]:
                    print "debug: ", dataset
                    self._current_data["data"][dataset] = self._current_data["data"][dataset][indices]

    def _filter_min_photons(self, dataset, min_photons):
        data = dataset.copy()
        data[data < 0] = 0
        photon_sum = np.sum(data, axis=1)
        indices = np.where(photon_sum >= min_photons)[0]
        return indices

    def _filter_max_photons(self, dataset, max_photons):
        data = dataset.copy()
        data[data < 0] = 0
        photon_sum = np.sum(data, axis=1)
        indices = np.where(photon_sum <= max_photons)[0]
        return indices

    def _filter_min_die_readout(self, dataset, min_number_die):
        dataset = dataset
        dies = np.count_nonzero(dataset >= 0, axis=1)/4.
        indices = np.where(dies >= min_number_die)[0]
        return indices

    def _filter_min_energy(self, dataset, min_energy):
        dataset = dataset.copy()
        dataset[dataset < 0] = 0
        indices = np.where(np.sum(dataset < min_energy, axis=1) < 1)[0]
        return indices

    def _filter_max_energy(self, dataset, max_energy):
        dataset = dataset.copy()
        indices = np.where(np.sum(dataset > max_energy, axis=1) < 1)[0]
        return indices

    def _filter_complete_events(self, dataset, number_sipms):
        dataset = dataset.copy()
        indices = np.where(np.sum(dataset < 0, axis=1) == (self._options["pixel_number"] - number_sipms))
        return indices

    def _adjust_reference_test(self):
        available_data = self._current_data["data"]["cal_photons"].shape[0] #Modified, but it does not affect (only shape)
        reference_wanted = self._options["reference_events"]
        test_wanted = self._options["test_events"]
        reference_selected = None
        test_selected = None
        if reference_wanted + test_wanted <= available_data:
            reference_selected = reference_wanted
            test_selected = test_wanted
        elif reference_wanted <= available_data:
            reference_selected = reference_wanted
            test_selected = available_data - reference_selected
        elif reference_wanted > available_data:
            reference_selected = available_data
            test_selected = 0
        # prove consistency
        if reference_selected + test_selected > available_data:
            logging.warning("More data selected than available, separation between reference and test events may be corrupted!")
        self._current_data["selected_reference"] = reference_selected
        self._current_data["selected_test"] = test_selected

    def iterate(self):
        """!
        Walk to the the folder structure, read data from the hitAnalysis files, select those singles according to
        the set filters and write them to the hdf5 suitable MonoCal file.

        @return: None
        """
        if self._found_files is None:
            self._search_files()
            print 'search done'
        if self._options["single_file"] is False:
            print 'initialising file'
            self._initiate_file()
            for file in tqdm(self._found_files):
#                if self._options["file_extension"] == ".hdf5" or self._options["file_extension"] == "unqualifiedClusters.hdf5" or self._options["file_extension"] == "_coincClusters.hdf5" and self._options["tofpet"]:
#                    self._extract_coordinate(file)
#                    if self._accept_position() is False:
#                        print "rejected position, ", self._current_data["meta_data"], "change if swapped = True"
#                        continue
#                    self._swap_coordinates()
#                elif self._options["file_extension"] == ".hdf5" and not self._options["tofpet"]:
#                    pass
#                else:
#                    pass
#                    self._extract_coordinate(file)
#                    if self._accept_position() is False:
#                        print "rejected position, ", self._current_data["meta_data"], "change if swapped = True"
#                        continue
#                    self._swap_coordinates()
                self._read_files(file)
                self._chain_filters()
                self._adjust_reference_test()
                self._save_data()
        else:
            print 'reading files'
            self._read_files(self._options["single_file_name"])
            print 'back up data'
            self._back_up_read_data()
            self._initiate_file()
            for elem in tqdm(self._found_positions):
                self._extract_coordinate(elem)
                if self._accept_position() is False:
                    print "rejected position, ", self._current_data["meta_data"]
                    continue
                self._swap_coordinates()
                self._read_data_position(elem)
                self._chain_filters()
                self._adjust_reference_test()
                self._save_data()

class CreateData_Add():
    def __init__(self):
        """!
        Constructor of the CreateData_Add class.
        This class is used to provide infrastructure for classes adding further values
        to singles in the hdf5 files.
        """
        pass

    def load_data(self, file):
        self._file = h5py.File(file, "r+")

    def close_file(self):
        self._file.close()

    def get_available_datasets(self):
        """!
        Prints and returns datasets of the loaded file.

        @return: datasets
        """
        print self._file.keys()
        return self._file.keys()

    def save_data(self, file):
        pass


class CreateData_Add_Position(CreateData_Add):
    def __init__(self, geometry="monolith"):
        """!
        Constructor of the CreateData_Add_Positioning class.
        This class is used for adding the estimated position to events in the CreateData-output files.
        """
        self._geo = GeometryDivide(geometry)
        self._positioning_models = {}
        self._tmp = {}

    def load_positioning_model(self, dataset, direction, model, added_features=""):
        """!
        Load positioning models from a pickle file or an existing class instance.

        @param dataset: Data for the position estimation.
        @param direction: Determines which position values is added. Use x, y or z as input.
        @param model: Path to a pickle file or a sket class instance.
        @param added_features: Specify AF used in the positioning model.
        @return: None
        """
        dict_key = dataset + direction
        self._positioning_models[dict_key] = {}
        self._positioning_models[dict_key]["dataset"] = dataset
        self._positioning_models[dict_key]["direction"] = direction
        if isinstance(model, str):
            self._positioning_models[dict_key]["model"] = pickle.load(open(model))
        else:
            self._positioning_models[dict_key]["model"] = model
        self._positioning_models[dict_key]["AF"] = added_features
        try:
            self._positioning_models[dict_key]["AF"] = self._positioning_models[dict_key]["model"]._add_features
            print "add features loaded from positioning model"
        except:
            pass

    def do_positioning(self):
        """!
        Run all position estimations provided by the load_positioning_model function.

        @return: None
        """
        for positioning in self._positioning_models:
            print positioning
            data = self._file[self._positioning_models[positioning]["dataset"]][:]
            print data
            if self._positioning_models[positioning]["AF"] is not "":
                add = FeatureAdder(self._positioning_models[positioning]["AF"], True)
                add.geometry = self._geo
                add.data = data
                add.add_features()
                data = add._data_added.copy()
                add._data_added = None
                add.data = None
            positions = self._positioning_models[positioning]["model"].predict(data)
            print positions, positions.shape
            dataset_name = self._generate_dataset_name(positioning)
            self._file.create_dataset(dataset_name, data=positions)

    def _generate_dataset_name(self, dataset):
        if "cal" in dataset:
            tmp1 = "cal"
        else:
            tmp1 = "coinc"
        if "x" in self._positioning_models[dataset]["direction"]:
            tmp2 = "posX"
        elif "y" in self._positioning_models[dataset]["direction"]:
            tmp2 = "posY"
        else:
            tmp2 = "posZ"
        name = tmp1 + "_" + tmp2 + "_" + "estimated"
        return name

    def make_uniform_distribution(self, measured, estimated, events, binning, pos_min=None, pos_max=None):
        """!
        Select events from the loaded database to achieve a uniform distribution.
        Function relies on two positioning parameters:
        1. Measured data: Binned data (discrete, usually doi)
        2. Estimated data: Estimated data (continuous, usually x or y)

        The selected events are stored in a private dict of the class. These data can be used with this
        function to achieve uniform distributions also in other directions. The datasets saved in the
        private dict are named $dataset_name_before_selection + "_tmp".

        @param measured: discrete data, name of the data set
        @type measured: str
        @param estimated: continuous data, name of the data set
        @type estimated: str
        @param events: number of events to keep
        @type: int
        @param binning: Binning which shall be applied to the continuous data
        @type binning: float
        @param pos_min:
        @type pos_min:
        @param pos_max:
        @type pos_max:
        @return: indices of selected events
        """
        dataset = measured
        if "tmp" in measured:
            measured = self._tmp[measured]
        else:
            measured = self._file[measured][:]
        if "tmp" in estimated:
            estimated = self._tmp[estimated]
        else:
            estimated = self._file[estimated][:]
        selected = []
        if pos_min is None:
            pos_min = np.min(estimated)
        else:
            pos_min = pos_min
        if pos_max is None:
            pos_max = np.max(estimated)
        else:
            pos_max = pos_max
        logging.debug("pos_min %s, pos_max %s", pos_min, pos_max)
        for point in np.unique(measured):
            discrete_ind = np.where(np.isclose(measured,point))[0]
            logging.debug("discrete_ind %s", discrete_ind)
            for position in np.arange(pos_min, pos_max, binning):
                pos_ind = np.where((estimated >= position) & (estimated < position + binning))[0]
                logging.debug("pos_ind %s", pos_ind)
                accepted_events = np.intersect1d(discrete_ind, pos_ind)
                logging.debug("accepted: %s, %s, %s", point, position, accepted_events.shape)
                selected.append(accepted_events[0:events])
        selected = np.concatenate(selected)
        print "events selected"
        for elem in self._file.keys():
            if "tmp" in dataset:
                set = elem + "_tmp"
                tmp = self._tmp[set]
            else:
                tmp = self._file[elem][:]
            tmp = tmp[selected]
            self._tmp[elem + "_tmp"] = tmp
        return selected

    def make_uniform_distribution_single(self, estimated, events, binning, pos_min=None, pos_max=None, sampling="random"):
        """!
        Select events from the loaded database to achieve a uniform distribution.
        Function relies only on one dataset which can originate from both an estimator or a measurement. The
        uniformity of the other datasets is achieved by a randomized sampling (set as default).

        The selected events are stored in a private dict of the class. These data can be used with this
        function to achieve uniform distributions also in other directions. The datasets saved in the
        private dict are named $dataset_name_before_selection + "_tmp".

        @param estimated: name of the dataset which needs to be uniformed
        @type estimated: string
        @param events: number of events per bin
        @type events: int
        @param binning: binning applied to the dataset
        @type binning: float
        @param pos_min: minimum position of data. If no value is set, the function determines
        the global minimum.
        @type pos_min: float
        @param pos_max: maximum position of the data. If no value is set, the function determines
        the global maximum.
        @type pos_max: float
        @param sampling: Select if a randomized sampling is applied or the first entries are used. Default: "random"
        @type sampling: string, "sampling"/"first"
        @return: selected indices
        """
        dataset = estimated  # save name of the dataset for detection if the data originate from _tmp dictionary
        if "tmp" in estimated:
            estimated = self._tmp[estimated]
        else:
            estimated = self._file[estimated][:]
        selected = []
        if pos_min is None:
            pos_min = np.min(estimated)
        else:
            pos_min = pos_min
        if pos_max is None:
            pos_max = np.max(estimated)
        else:
            pos_max = pos_max
        logging.debug("pos_min %s, pos_max %s", pos_min, pos_max)
        for position in np.arange(pos_min, pos_max, binning):
            pos_ind = np.where((estimated >= position) & (estimated < position + binning))[0]
            logging.debug("pos_ind %s", pos_ind.shape[0])
            if sampling == "random":
                if events >= pos_ind.shape[0]:
                    events_sel = pos_ind.shape[0]
                else:
                    events_sel = events
                selected.append(np.random.choice(pos_ind, events_sel, replace=False))
            else:
                selected.append(pos_ind[0:events])
        selected = np.concatenate(selected)
        print len(selected), " events selected"
        for elem in self._file.keys():
            if "tmp" in dataset:
                logging.debug("select data from tmp dictionary")
                set = elem + "_tmp"
                tmp = self._tmp[set]
            else:
                tmp = self._file[elem][:]
            tmp = tmp[selected]
            self._tmp[elem + "_tmp"] = tmp
        return selected

    def write_uniform_data(self, fname):
        """!
        Writing the selected data to a new hdf5 file.

        @param fname: Name of the created file.
        @type fname: str
        @return: None
        """
        file = h5py.File(fname, "w")
        for elem in self._tmp:
            dataset_name = elem[0:-4]
            file.create_dataset(dataset_name, data=self._tmp[elem], compression="gzip")

    def plot_profile(self, datasets, binning, show=True):
        """!
        Plots the histogram of given datasets. An unlimited number of datasets can be plotted. The
        binning of the histograms can be specified for every histogram individually or set to
        a fixed value for all histograms.

        @param datasets: list of datasets names to plot
        @type datasets: list of str
        @param binning: binning for the histograms. If an int is given, this binning is applied
        to all histogram. If a list of ints is given, these values are mapped to the corresponding histograms.
        @type binning: int or list of int
        @param show: Show the plot, default: True. If False, the plt object is returned by the function.
        @type show: True/False
        @return: plt object if show is True, None otherwise
        """
        number_plots = len(datasets)
        for i, dataset in enumerate(datasets):
            plt.subplot(number_plots, 1, i+1)
            if "tmp" in dataset:
                data = self._tmp[dataset]
            else:
                data = self._file[dataset][:]
            if isinstance(binning, list):
                plt.hist(data, binning[i])
            else:
                plt.hist(data, binning)
            plt.title(dataset)
        plt.tight_layout()
        if not show:
            return plt
        plt.show()



from EnergyCalibration import EnergyCalculation

class CreateData_Add_Energy(CreateData_Add):
    def __init__(self):
        self._ec = {} # ec = energy_calibration

    def load_energy_calibration(self, dataset, calibration_folder, filter, geometry="monolith", main_die=True):
        self._ec[dataset] = {}
        self._ec[dataset]["dataset"] = dataset
        self._ec[dataset]["calibration_folder"] = calibration_folder
        self._ec[dataset]["filter"] = filter
        self._ec[dataset]["calibration"] = EnergyCalculation(filter, geometry_name=geometry, main_die=True)
        self._load_coordinates(dataset)

    def _load_coordinates(self, dataset):
        if "cal" in dataset:
            prefix = "cal"
        else:
            prefix = "coinc"
        self._ec[dataset]["posX"] = prefix + "_posX_estimated"
        self._ec[dataset]["posY"] = prefix + "_posY_estimated"
        self._ec[dataset]["posZ"] = prefix + "_posZ_estimated"

    def _dataset_name(self, dataset):
        suffix = "_energy"
        if "cal" in dataset:
            return "cal" + suffix
        else:
            return "coinc" + suffix

    def voxelize(self, **kwargs):
        pass
    #create pickle file saving the voxelation in the energy calibration folder

    def calc_energy(self):
        for elem in self._ec:
            self._ec[elem]["calibration"]._photons = self._file[elem][:]
            self._ec[elem]["calibration"]._posX = self._file[self._ec[elem]["posX"]][:]
            self._ec[elem]["calibration"]._posY = self._file[self._ec[elem]["posY"]][:]
            try:
                self._ec[elem]["calibration"]._posZ = self._file[self._ec[elem]["posZ"]][:]
            except:
                self._ec[elem]["calibration"]._posZ = np.ones(self._ec[elem]["calibration"]._posY.shape[0]) # DOI is set to 1 for every event
                print "position in z-direction not found!"
                print "Assuming no DOI is used"
            self._ec[elem]["calibration"]._energies = np.ones(self._ec[elem]["calibration"]._photons.shape[0])
            self._ec[elem]["calibration"].vox._photons = self._ec[elem]["calibration"]._photons
            self._ec[elem]["calibration"].vox._posX = self._ec[elem]["calibration"]._posX
            self._ec[elem]["calibration"].vox._posY = self._ec[elem]["calibration"]._posY
            self._ec[elem]["calibration"].vox._posZ = self._ec[elem]["calibration"]._posZ
            self._ec[elem]["calibration"].loadEnergyCalibration(self._ec[elem]["calibration_folder"])
            self._ec[elem]["calibration"].calcEnergy()
            dataset_name = self._dataset_name(elem)
            self._file.create_dataset(dataset_name, data = self._ec[elem]["calibration"]._energies)



