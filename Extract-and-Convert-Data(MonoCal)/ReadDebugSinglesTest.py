import cPickle as pickle
import psutil #process and systems utils
import time
import os
import multiprocessing as mp
import gc #garbage collector

def chunkify_file(fname, size=1024*1024*1000, skiplines=-1):
    """
    function to divide a large text file into chunks each having size ~= size so that the chunks are line aligned

    Params :
        fname : path to the file to be chunked
        size : size of each chink is ~> this
        skiplines : number of lines in the begining to skip, -1 means don't skip any lines
    Returns :
        start and end position of chunks in Bytes
    """
    chunks = []
    fileEnd = os.path.getsize(fname)
    with open(fname, "rb") as f:
        if(skiplines > 0):
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
            count+=1

            if chunkEnd > fileEnd:
                break
    return chunks

def parallel_apply_line_by_line_chunk(chunk_data):
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

        for i,line in enumerate(lines):
            ret = func_apply(line, *func_args)
            if(ret != None):
                chunk_res.append(ret)
    return chunk_res

def parallel_apply_line_by_line(input_file_path, chunk_size_factor, num_procs, skiplines, func_apply, func_args, fout=None):
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

    jobs = chunkify_file(input_file_path, 1024 * 1024 * chunk_size_factor, skiplines)

    jobs = [list(x) + [func_apply] + func_args for x in jobs]

    print("Starting the parallel pool for {} jobs ".format(len(jobs)))

    lines_counter = 0

    pool = mp.Pool(num_parallel, maxtasksperchild=1000)  # maxtaskperchild - if not supplied some weird happend and memory blows as the processes keep on lingering

    dic_HVD = {}

    outputs = []
    for i in range(0, len(jobs), num_parallel):
        print("Chunk start = ", i)
        t1 = time.time()
        chunk_outputs = pool.map(parallel_apply_line_by_line_chunk, jobs[i : i + num_parallel])

        for i, subl in enumerate(chunk_outputs):
            #print(i, subl)
            for x in subl:
                if(fout != None):
                    print(x, fout)
                else:
                    outputs.append(x)
                dic_HVD[lines_counter] = x
                lines_counter += 1

        del(chunk_outputs)
        gc.collect()
        print("All Done in time ", time.time() - t1)

    print("Total lines we have = {}".format(lines_counter))

    pool.close()
    pool.terminate()
    return outputs, dic_HVD


def count_words_line(line):
    return len(line.split(","))

def word_inline(line):
    return line.strip().split(",")[-1]

def index_inline(line, index):
    return line.strip().split(",")[index]

def save_data(folder, dic_HVD, name):
    with open('{}/{}.pickle'.format(folder, name), 'wb') as handle:
        pickle.dump(dic_HVD, handle, protocol=pickle.HIGHEST_PROTOCOL)

# outp, dic_pv111 = parallel_apply_line_by_line("/home/david.perez/Desktop/1.0_1.0_20200701/9013106.DebugSingles", 100, 16, 0, index_inline, [i], fout=None)
# print(dic_pv111[999999])

list_save = {"dicval_000":[192], "dicval_100":[193], "dicval_010":[194], "dicval_111":[199], "dicpos_000":[200,201], "dicpos_100":[202,203], "dicpos_010":[204,205], "dicpos_111":[214,215], "dicpv_000":[216], "dicpv_100":[217], "dicpv_010":[218], "dicpv_111":[223]}

# dicval_000: 192
# dicval_100: 193
# dicval_010: 194
# dicval_111: 199
#
# dicpos_000: [200,201]  # x and y from COG HVD
# dicpos_100: [202,203]
# dicpos_010: [204,205]
# dicpos_111: [214,215]
#
# dicpv_000: [216]  # photon values from COG HVD
# dicpv_100: [217]
# dicpv_010: [218]
# dicpv_111: [223]

dicval_000= {}
dicval_100= {}
dicval_010= {}
dicval_111= {}

dicpos_000= {"pos":[-1,-1]}  # x and y from COG HVD
dicpos_100= {"pos":[-1,-1]}
dicpos_010= {"pos":[-1,-1]}
dicpos_111= {"pos":[-1,-1]}

dicpv_000= {} # photon values from COG HVD
dicpv_100= {}
dicpv_010= {}
dicpv_111= {}


#list_save_dic_list = [dicval_000, dicval_100, dicval_010, dicval_111, dicpos_000, dicpos_100, dicpos_010, dicpos_111, dicpv_000, dicpv_100, dicpv_010, dicpv_111]
list_save_dic = {"dicval_000":dicval_000, "dicval_100":dicval_100, "dicval_010":dicval_010, "dicval_111":dicval_111, "dicpos_000":dicpos_000, "dicpos_100":dicpos_100, "dicpos_010":dicpos_010, "dicpos_111":dicpos_111, "dicpv_000":dicpv_000, "dicpv_100":dicpv_100, "dicpv_010":dicpv_010, "dicpv_111":dicpv_111}

list_DBFiles = ["00", "0", ""]

list_DBFiles_2 = [range(10), range(10,100), range(100,150)]


for i_db_n, i_db in enumerate(list_DBFiles):
    i_db_2 = list_DBFiles_2[i_db_n]
    for j_db_2 in i_db_2:
        folder_dir = "/home/david.perez/Desktop/20210209_2m-2019-10-18_PickleData/" + str(i_db) + str(j_db_2)
        CHECK_FOLDER = os.path.isdir(folder_dir)
        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(folder_dir)
            print("created folder : ", folder_dir)
        for i_s in list_save.keys():
            index = list_save[i_s]
            print(index)
            if len(index) > 1:
                for j_n, j in enumerate(index):
                    outp, list_save_dic[i_s]["pos"][j_n] = parallel_apply_line_by_line("/media/david.perez/pet-scratch/Measurements/Hypmed/2019-09-20_-_15-25-35_-_Hypmed_Coinc/2019-09-20_-_15-25-43_-_first_tests/2019-10-18_-_15-52-50_-_3layersBaSO_08mm_2m/ramdisks_2019-10-18_-_16-39-34/SplitDebugSingles/1.0_1.0_20210129/{}{}_106.DebugSingles".format(i_db, j_db_2),
                                                      100, 16, 0, index_inline, [j], fout=None)
            else:
                outp, list_save_dic[i_s] = parallel_apply_line_by_line(
                    "/media/david.perez/pet-scratch/Measurements/Hypmed/2019-09-20_-_15-25-35_-_Hypmed_Coinc/2019-09-20_-_15-25-43_-_first_tests/2019-10-18_-_15-52-50_-_3layersBaSO_08mm_2m/ramdisks_2019-10-18_-_16-39-34/SplitDebugSingles/1.0_1.0_20210129/{}{}_106.DebugSingles".format(i_db,j_db_2),
                    100, 16, 0, index_inline, [index[0]], fout=None)


        #for name in list_save_dic.keys():
            name = i_s
            dic_HVD = list_save_dic[name]
            save_data(folder_dir, dic_HVD, name)

