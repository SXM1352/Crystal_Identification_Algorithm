# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 17:52:29 2020

@author: david.perez
"""


from os import rename, listdir

#split 106.DebugSingles 106.DebugSingles_ -a 3 -d -l 1000000
#fnames = listdir('/home/david.perez/Desktop/1.0_1.0_20210125/')
fnames = listdir('/media/david.perez/pet-scratch/Measurements/Hypmed/2019-09-20_-_15-25-35_-_Hypmed_Coinc/2019-09-20_-_15-25-43_-_first_tests/2019-10-18_-_15-52-50_-_3layersBaSO_08mm_2m/ramdisks_2019-10-18_-_16-39-34/SplitDebugSingles/')
#print(fnames)

        
for fname in fnames:        
    try:
        DS = fname.split("_")[0]
        badsuffix = fname.split("_")[1]
        preffix = badsuffix+"_"
        print(preffix)
        print(DS)
        final_name = preffix + DS
        print(final_name)

        rename(fname, final_name)
    except:
        print("Qué pasa?")

#import os
#
#paths = (os.path.join(root, filename)
#        for root, _, filenames in os.walk('/home/david.perez/Desktop/1.0_1.0_20190802/')
#        for filename in filenames)
#
#for path in paths:
#    # the '#' in the example below will be replaced by the '-' in the filenames in the directory
#    newname = path.replace('_0', '')
#    if newname != path:
#        os.rename(path, newname)


