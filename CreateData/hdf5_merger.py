import numpy as np
import h5py


class merge():

    def __init__(self):
        self.hdf5_name = {}

    def add_hdf5(self, hdf5_name, data_name, new_name):
        self.hdf5_name[new_name] = np.array(h5py.File(hdf5_name, "r")[data_name])

    def save_hdf5(self, path):
        file = h5py.File(path, "a")
        for key in self.hdf5_name:
            file[str(key)] = self.hdf5_name[key]
        file.close()

    def sort_xy(self, path, name):
        file = h5py.File(path + name, "a")
        lenght = len(file["cog000_xy"])*2

        x1 = -22.
        x2 = 22.
        y1 = 0.
        y2 = 35.

        a = (y2-y1)/(x2-x1)
        b = y2 - a * x2

        print("a=", a, ", b=", b)
        file_dir = h5py.File(path + "Data_x_Ref.hdf5", "a")
        file_dir["cog000"] = np.reshape(np.array(file["cog000_xy"]), lenght)[::2][:600000]
        file_dir["posY"] = np.array(list(map(int, np.reshape(np.array(file["cog000_xy"]), lenght)[::2][:600000] * a + b)))
        file_dir["cog010"] = np.reshape(np.array(file["cog010_xy"]), lenght)[::2][:600000]
        file_dir["cog100"] = np.reshape(np.array(file["cog100_xy"]), lenght)[::2][:600000]
        file_dir["cog111"] = np.reshape(np.array(file["cog111_xy"]), lenght)[::2][:600000]
        file_dir["cal_photons"] = np.array(file["photons"])[:600000]
        # file_dir["coinc_photons"] = np.array(file["photons"])
        file_dir["posX"] = np.full(600000, 5)
        file_dir.close()

        file_dir = h5py.File(path + "Data_x_Test.hdf5", "a")
        file_dir["cog000"] = np.reshape(np.array(file["cog000_xy"]), lenght)[::2][600000:800000]
        file_dir["posY"] = np.array(list(map(int, np.reshape(np.array(file["cog000_xy"]), lenght)[::2][600000:800000] * a + b)))
        file_dir["cog010"] = np.reshape(np.array(file["cog010_xy"]), lenght)[::2][600000:800000]
        file_dir["cog100"] = np.reshape(np.array(file["cog100_xy"]), lenght)[::2][600000:800000]
        file_dir["cog111"] = np.reshape(np.array(file["cog111_xy"]), lenght)[::2][600000:800000]
        file_dir["cal_photons"] = np.array(file["photons"])[600000:800000]
        # file_dir["coinc_photons"] = np.array(file["photons"])
        file_dir["posX"] = np.full(200000, 5)
        file_dir.close()

        file_dir = h5py.File(path + "Data_y_Ref.hdf5", "a")
        file_dir["cog000"] = np.reshape(np.array(file["cog000_xy"]), lenght)[1::2][:600000]
        file_dir["posY"] = np.array(list(map(int, np.reshape(np.array(file["cog000_xy"]), lenght)[1::2][:600000] * a + b)))
        file_dir["cog010"] = np.reshape(np.array(file["cog010_xy"]), lenght)[1::2][:600000]
        file_dir["cog100"] = np.reshape(np.array(file["cog100_xy"]), lenght)[1::2][:600000]
        file_dir["cog111"] = np.reshape(np.array(file["cog111_xy"]), lenght)[1::2][:600000]
        file_dir["cal_photons"] = np.array(file["photons"])[:600000]
        # file_dir["coinc_photons"] = np.array(file["photons"])
        file_dir["posX"] = np.full(600000, 5)
        file_dir.close()

        file_dir = h5py.File(path + "Data_y_Test.hdf5", "a")
        file_dir["cog000"] = np.reshape(np.array(file["cog000_xy"]), lenght)[1::2][600000:800000]
        file_dir["posY"] = np.array(list(map(int, np.reshape(np.array(file["cog000_xy"]), lenght)[1::2][600000:800000] * a + b)))
        file_dir["cog010"] = np.reshape(np.array(file["cog010_xy"]), lenght)[1::2][600000:800000]
        file_dir["cog100"] = np.reshape(np.array(file["cog100_xy"]), lenght)[1::2][600000:800000]
        file_dir["cog111"] = np.reshape(np.array(file["cog111_xy"]), lenght)[1::2][600000:800000]
        file_dir["cal_photons"] = np.array(file["photons"])[600000:800000]
        # file_dir["coinc_photons"] = np.array(file["photons"])
        file_dir["posX"] = np.full(200000, 5)
        file_dir.close()
        file.close()


