#%load_ext autoreload
#%autoreload 2

from NewHypmed import *
read_path = "/media/janko.lambertus/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/" \
       "2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/"
save_path = "/media/janko.lambertus/pet-scratch/Janko/Master/Data/2021_06_01_Test/"
Hyp = Hypmed(read_path, save_path)
# Hyp.load_raw_data()
# Hyp.valid_events(n_events = 100000)
# Hyp.region_ana()