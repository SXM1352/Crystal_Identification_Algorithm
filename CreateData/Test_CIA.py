#%load_ext autoreload
#%autoreload 2

from hdf5_merger import merge

merge = merge()

# path ="/media/janko.lambertus/pet-scratch/Janko/Master/Data/2021_06_04/test/"
# merge.add_hdf5(path+"cog010.hdf5", "data", "cog010_xy")
# merge.add_hdf5(path+"photons.hdf5", "data", "photons")

path = "/media/janko.lambertus/pet-scratch/Janko/Master/Data/2021_06_04/"
name = "Data.hdf5"

merge.sort_xy(path, name)