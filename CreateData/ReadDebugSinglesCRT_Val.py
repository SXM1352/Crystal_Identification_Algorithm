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

def __parallel_apply_line_by_line(input_file_path, chunk_size_factor, num_procs, skiplines, func_apply, func_args,
                                fout=None):
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
    print("Num_parallel is: ", num_parallel)

    jobs = __chunkify_file(input_file_path, 1024 * 1024 * chunk_size_factor, skiplines) #jobs are the lines of the file

    jobs = [list(x) + [func_apply] + func_args for x in jobs] # x is each line, jobs will be now a list with each slected line and the function that will be applied to each line

    print("Starting the parallel pool for {} jobs ".format(len(jobs)))

    lines_counter = 0

    pool = mp.Pool(num_parallel,
                   maxtasksperchild=1000)  # maxtaskperchild - if not supplied some weird happend and memory blows as the processes keep on lingering

    dic_HVD = {}

    outputs = []
    for i in range(0, len(jobs)-num_parallel, num_parallel):
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
        print("All Done in time ", time.time() - t1)

    print("Total lines we have = {}".format(lines_counter))

    pool.close()
    pool.terminate()
    return outputs, dic_HVD

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
# parser.add_argument('--fileType', dest='fType', help='Specifiy which type of file to be read', default='.DebugCoincidentSingles')
# parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')

args = parser.parse_args()
# file_type, pathtodirectoryRead = args.fType, args.fileDirect
pathtodirectoryRead = args.fileDirect

list_save_crt = {"stack_id": [2,3],
                 "dicval_000": [192, 193], "dicval_100": [193, 194], "dicval_010": [194, 195], "dicval_111": [199, 200]}
stack_id = {}
photons = {}
timeStamps = {}

dicval_000 = {}
dicval_100 = {}
dicval_010 = {}
dicval_111 = {}

dicpos_000 = {}  # x and y from COG HVD
dicpos_100 = {}
dicpos_010 = {}
dicpos_111 = {}

list_save_dic_crt = {"stack_id": stack_id,
                     "dicval_000": dicval_000, "dicval_100": dicval_100, "dicval_010": dicval_010, "dicval_111": dicval_111}

# folder_dir = pathtodirectorySave_pickle
# CHECK_FOLDER = os.path.isdir(folder_dir)

file_type = '.DebugCoincidentSingles'
# Obtain this info from file
stack_id = 'measurement' #108

# If folder doesn't exist, then create it.
# if not CHECK_FOLDER:
#     os.makedirs(folder_dir)
#     print("created folder : ", folder_dir)
for i_s in list_save_crt.keys():
    index = list_save_crt[i_s]
    print(index)

    outp, list_save_dic_crt[i_s] = __parallel_apply_line_by_line(
        pathtodirectoryRead + "{}{}".format(stack_id, file_type),
        1000, 31, 0, __index_inline_crt, [index[0], index[1]], fout=None)
    # for name in list_save_dic.keys():
    #name = i_s
    #dic_HVD = list_save_dic_crt[name]
    #__save_data(folder_dir, dic_HVD, name)

cogRef_cal = []

cogRef_coinc = []

stack_id_cal = list_save_dic_crt['stack_id'][0]
stack_id_coinc = list_save_dic_crt['stack_id'][1]

for cluster in list_save_dic_crt['stack_id'].keys():
    if list_save_dic_crt['stack_id'][cluster] == stack_id_cal:
        cogRef_cal.append([int(list_save_dic_crt["dicval_000"][cluster][0]), int(list_save_dic_crt["dicval_100"][cluster][0]),
                       int(list_save_dic_crt["dicval_010"][cluster][0]), int(list_save_dic_crt["dicval_111"][cluster][0])])

    elif list_save_dic_crt['stack_id'][cluster] == stack_id_coinc:
        cogRef_coinc.append([int(list_save_dic_crt["dicval_000"][cluster][0]), int(list_save_dic_crt["dicval_100"][cluster][0]),
                       int(list_save_dic_crt["dicval_010"][cluster][0]), int(list_save_dic_crt["dicval_111"][cluster][0])])

print("Arrays ready for time")

cogRef_cal = np.array(cogRef_cal)

cogRef_coinc = np.array(cogRef_coinc)

print("Arrays ready.")

# pathtodirectorySave_hdf = "/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/20210315_NEW_hdf5Data/"
pathtodirectorySave_hdf = pathtodirectoryRead + 'hdf5Data/'
folder_dir = pathtodirectorySave_hdf
CHECK_FOLDER = os.path.isdir(folder_dir)
# If folder doesn't exist, then create it.
if not CHECK_FOLDER:
    os.makedirs(folder_dir)
    print("created folder : ", folder_dir)

n_events = int(len(cogRef_cal))
# MODIFY NUMBER OF EVENTS FOR ALL POSSIBLE FILES

with h5py.File('{}cogRef_cal.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 4), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cogRef_cal[i: i + dset.chunks[0]]


with h5py.File('{}cogRef_coinc.hdf5'.format(pathtodirectorySave_hdf), 'w') as f:
    dset = f.create_dataset("data", (n_events, 4), chunks=True)

    for i in range(0, n_events, dset.chunks[0]):
        dset[i: i + dset.chunks[0]] = cogRef_coinc[i: i + dset.chunks[0]]
