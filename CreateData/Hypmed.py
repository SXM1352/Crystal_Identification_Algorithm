# -*- coding: utf-8 -*-
__author__ = "david.perez.gonzalez"

'''
INSTALL PATHOS TO BE ABLE TO USE CLASSES'''

import os
import argparse
import cPickle as pickle
import psutil  # process and systems utils
import time
import os
import multiprocessing as mp
import gc  # garbage collector
import h5py
import numpy as np

def __chunkify_file(fname, size=1024 * 1024 * 1000, skiplines=-1):
    """
    function to divide a large text file into chunks each having size ~= size so that the chunks are line aligned

    Params :
        fname : path to the file to be chunked
        size : size of each chunk is ~> this
        skiplines : number of lines in the begining to skip, -1 means don't skip any lines
    Returns :
        start and end position of chunks in Bytes
    """
    chunks = []
    fileEnd = os.path.getsize(fname)
    with open(fname, "rb") as f:
        if (skiplines > 0):
            for i in range(skiplines):
                f.readline()

        chunkEnd = f.tell()
        count = 0
        while True:
            chunkStart = chunkEnd
            f.seek(f.tell() + size, os.SEEK_SET)
            f.readline()  # make this chunk line aligned
            chunkEnd = f.tell()
            chunks.append((chunkStart, chunkEnd - chunkStart, fname))
            count += 1

            if chunkEnd > fileEnd:
                break
    return chunks

def __parallel_apply_line_by_line_chunk(chunk_data):
    """
    function to apply a function to each line in a chunk

    Params :
        chunk_data : the data for this chunk
    Returns :
        list of the non-None results for this chunk
    """
    chunk_start, chunk_size, file_path, func_apply = chunk_data[:4]
    func_args = chunk_data[4:]

    t1 = time.time()
    chunk_res = []
    with open(file_path, "rb") as f:
        f.seek(chunk_start)
        cont = f.read(chunk_size).decode(encoding='utf-8')
        lines = cont.splitlines()

        for i, line in enumerate(lines):
            ret = func_apply(line, *func_args)
            if (ret != None):
                chunk_res.append(ret)
    return chunk_res

def __parallel_apply_line_by_line(start, stop, input_file_path, chunk_size_factor, num_procs, skiplines, func_apply, func_args, fout=None, or_all = False):
    """
    function to apply a supplied function line by line in parallel

    Params :
        input_file_path : path to input file
        chunk_size_factor : size of 1 chunk in MB
        num_procs : number of parallel processes to spawn, max used is num of available cores - 1
        skiplines : number of top lines to skip while processing
        func_apply : a function which expects a line and outputs None for lines we don't want processed
        func_args : arguments to function func_apply
        fout : do we want to output the processed lines to a file
    Returns :
        list of the non-None results obtained be processing each line
        dictionary with values
    """
    num_parallel = min(num_procs, psutil.cpu_count()) - 1
    # print("Num_parallel is: ", num_parallel)

    jobs = __chunkify_file(input_file_path, 1024 * 1024 * chunk_size_factor, skiplines) #jobs are the lines of the file

    jobs = [list(x) + [func_apply] + func_args for x in jobs] # x is each line, jobs will be now a list with each slected line and the function that will be applied to each line
    # print("Starting the parallel pool for {} jobs ".format(len(jobs)))

    lines_counter = 0

    pool = mp.Pool(num_parallel,
                   maxtasksperchild=1000)  # maxtaskperchild - if not supplied some weird happend and memory blows as the processes keep on lingering

    dic_HVD = {}

    outputs = []

    num_parallel = 8
    # print("LENGTH:", len(jobs))
    if or_all:
        stop = len(jobs)
    for i in range(start, stop, num_parallel): #len(jobs) ->
        print("Chunk start = ", i)
        t1 = time.time()
        chunk_outputs = pool.map(__parallel_apply_line_by_line_chunk, jobs[i: i + num_parallel])

        for i, subl in enumerate(chunk_outputs):
            #print(i, subl)
            for x in subl:
                if (fout != None):
                    #print(x, fout)
                    print('ERROR with fout')
                else:
                    outputs.append(x)
                #list_float = [float(element_list) for element_list in x]
                dic_HVD[lines_counter] = x
                lines_counter += 1

        del (chunk_outputs)
        gc.collect()
        print("Actual number of lines we have = {}".format(lines_counter))

    print("Total number of lines we have = {}".format(lines_counter))

    pool.close()
    pool.terminate()
    # return outputs, dic_HVD
    return outputs
def __count_words_line(line):
    return len(line.split(","))

def __word_inline(line):
    return line.strip().split(",")[-1]

def __index_inline(line, index):
    return line.strip().split(",")[index]

def __index_inline_crt(line, index_init, index_fin):
    return [float(element_list) for element_list in line.strip().split(",")[index_init:index_fin]]

def __list_index_inline(line, list_index):
    return [line.strip().split(",")[index] for index in list_index]

def __save_data(folder, dic_HVD, name):
    with open('{}/{}.pickle'.format(folder, name), 'wb') as handle:
        pickle.dump(dic_HVD, handle, protocol=pickle.HIGHEST_PROTOCOL)

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')

args = parser.parse_args()

# list_save_crt = {"stack_id": [2,3], "dicpos_000": [200, 202], "dicpos_100": [202, 204],
#                  "dicpos_010": [204, 206], "dicpos_111": [214, 216], "photons": [12,156]}

###############ÄNDERN####################
pathtodirectoryRead = "/media/janko.lambertus/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/"
pathtodirectorySave_hdf = "/media/janko.lambertus/pet-scratch/Janko/Master/Data/2021_06_04/All_Photons/"

list_save_crt = {"photons": [12, 156], "cog_111": [214, 216]}

steps = 24
start = np.arange(0,1000, steps)

n_dim = {"photons": list_save_crt["photons"][1]-list_save_crt["photons"][0],
         "cog_111": list_save_crt["cog_111"][1]-list_save_crt["cog_111"][0]}

# save_name = {"photons": '{}all_photons_{}_{}.hdf5'.format(pathtodirectorySave_hdf, start, stop),
#              "cog_111": '{}all_cog111_{}_{}.hdf5'.format(pathtodirectorySave_hdf, start, stop)}
x1 = -22.
x2 = 22.
y1 = 0.
y2 = 35.
a = (y2 - y1) / (x2 - x1)
b = y2 - a * x2
#########################################
def routine(start, steps):
    stop = start + steps
    file_type = '.DebugSingles'
    # Obtain this info from file
    stack_id = '108' #108
    outp = {}

    for i_s in list_save_crt.keys():
        index = list_save_crt[i_s]
        print("We start with {} with index {}".format(i_s, index))

        outp[i_s] = __parallel_apply_line_by_line(start, stop,
            pathtodirectoryRead + "{}{}".format(stack_id, file_type),
            100, 25, 0, __index_inline_crt, [index[0], index[1]], fout=None)
        print("Ready with {}".format(i_s))

    print("Arrays ready to write hdf5")
    # for j in outp.keys():
    #     print("We save {} ".format(save_name[j]))
    #     data_array = np.array(outp[j])
    #
    #     folder_dir = pathtodirectorySave_hdf
    #     CHECK_FOLDER = os.path.isdir(folder_dir)
    #
    #     if not CHECK_FOLDER:
    #         os.makedirs(folder_dir)
    #         print("created folder : ", folder_dir)
    #
    #     n_events = len(data_array)
    #     # # # MODIFY NUMBER OF EVENTS FOR ALL POSSIBLE FILES
    #     with h5py.File(save_name[j], 'w') as f:
    #         dset = f.create_dataset("data", (n_events, n_dim[j]), chunks=True)
    #
    #         for i in range(0, n_events, dset.chunks[0]):
    #             dset[i: i + dset.chunks[0]] = data_array[i: i + dset.chunks[0]]
    #     print("{} has a ready hdf5".format(save_name[j]))
    lenght = len(outp["cog_111"])*2
    outp["posX_original"] = np.reshape(np.array(outp["cog_111"]), lenght)[::2]
    outp["posX"] = np.array(list(map(int, np.reshape(np.array(outp["cog_111"]), lenght)[::2] * a + b)))

    # outp["posY_original"] = np.reshape(np.array(outp["cog_111"]), lenght)[1::2]
    # outp["posY"] = np.array(list(map(int, np.reshape(np.array(outp["cog_111"]), lenght)[1::2] * a + b)))



    file = h5py.File("{}Data_{}_{}".format(pathtodirectorySave_hdf, start, stop), "a")
    for key in outp.keys():
        print("Now saving {}".format(key))
        file[key] = np.array(outp[key])
    file.close()
    return 0

for i in start:
    routine(i, steps)