import numpy as np
import matplotlib.pyplot as plt
import cPickle as pickle
import argparse
import os


def checkFolder(pathDirectory):
    CHECK_FOLDER = os.path.isdir(pathDirectory)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        os.makedirs(pathDirectory)
        print("created folder : ", pathDirectory)

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                             directory where to read the files from')
parser.add_argument('--saveDirectory', dest='saveDirect', help='Specifiy the name of the   \
                                             directory where to read the files from', default='None')
args = parser.parse_args()

pathtodirectoryRead, pathtodirectorySaveST = args.fileDirect, args.saveDirect

pathtodirectoryReadCC = pathtodirectoryRead + 'Parallel/'
pathtoHDF5 = pathtodirectoryRead + 'hdf5Data/'

pathtodirectorySave = pathtodirectorySaveST

checkFolder(pathtodirectorySave)

with open('{}dic-Events-Counts.pickle'.format(pathtodirectoryReadCC), 'rb') as handle:
    dic_Events = pickle.load(handle)  # 000, 100, 010, 111

with open('{}dic_AssignE.pickle'.format(pathtodirectoryReadCC), 'rb') as handle:
    dic_AssignE = pickle.load(handle)  # 000, 100, 010, 111

N_columns = 5
all_HVD = (dic_Events["ALL"], 0, 0, 0, 0)

three_100_111_010 = (0, dic_Events["three_100_111_010"], 0, 0, 0)
three_100_111_000 = (0, dic_Events["three_100_111_000"], 0, 0, 0)
three_010_111_000 = (0, dic_Events["three_010_111_000"], 0, 0, 0)
three_010_100_000 = (0, dic_Events["three_000_010_100"], 0, 0, 0)

two_010_100 = (0, 0, dic_Events["two_010_100"], 0, 0)
two_010_111 = (0, 0, dic_Events["two_010_111"], 0, 0)
two_100_111 = (0, 0, dic_Events["two_100_111"], 0, 0)
two_000_111 = (0, 0, dic_Events["two_000_111"], 0, 0)
two_000_010 = (0, 0, dic_Events["two_000_010"], 0, 0)
two_000_100 = (0, 0, dic_Events["two_000_100"], 0, 0)

# QF_000 = (0, 0, 0, dic_Events["QF_000"], 0)
# QF_100 = (0, 0, 0, dic_Events["QF_100"], 0)
# QF_010 = (0, 0, 0, dic_Events["QF_010"], 0)
# QF_111 = (0, 0, 0, dic_Events["QF_111"], 0)

total_qf_000 = 0
total_qf_100 = 0
total_qf_010 = 0
total_qf_111 = 0

total_only_000 = 0
total_only_100 = 0
total_only_010 = 0
total_only_111 = 0
for i in dic_AssignE['ALL'].keys():
    total_qf_000 += dic_AssignE["000_QF"][i]['n_events']
    total_qf_100 += dic_AssignE["100_QF"][i]['n_events']
    total_qf_010 += dic_AssignE["010_QF"][i]['n_events']
    total_qf_111 += dic_AssignE["111_QF"][i]['n_events']

    total_only_000 += dic_AssignE["000_ONLY_VALID"][i]['n_events']
    total_only_100 += dic_AssignE["100_ONLY_VALID"][i]['n_events']
    total_only_010 += dic_AssignE["010_ONLY_VALID"][i]['n_events']
    total_only_111 += dic_AssignE["111_ONLY_VALID"][i]['n_events']

QF_000 = (0, 0, 0, total_qf_000, 0)
QF_100 = (0, 0, 0, total_qf_100, 0)
QF_010 = (0, 0, 0, total_qf_010, 0)
QF_111 = (0, 0, 0, total_qf_111, 0)

only_000 = (0, 0, 0, 0, total_only_000)
only_100 = (0, 0, 0, 0, total_only_100)
only_010 = (0, 0, 0, 0, total_only_010)
only_111 = (0, 0, 0, 0, total_only_111)

# menStd = (2, 3, 4, 1)
# womenStd = (3, 5, 2, 3)
ind = np.arange(N_columns)    # the x locations for the groups
width = 0.7       # the width of the bars: can also be len(x) sequence

plt.figure(figsize=(15,15))

p1 = plt.bar(ind, all_HVD, width)#, yerr=menStd)

p2 = plt.bar(ind, three_100_111_000, width)#, yerr=womenStd)

p3 = plt.bar(ind, three_010_100_000, width,
             bottom=(three_100_111_000[1]))#, yerr=womenStd)

p4 = plt.bar(ind, three_010_111_000, width,
             bottom=(three_100_111_000[1]+three_010_100_000[1]))

p5 = plt.bar(ind, three_100_111_010, width,
             bottom=(three_010_100_000[1]+three_100_111_000[1]+three_010_111_000[1]))#, yerr=womenStd)



p6 = plt.bar(ind, two_010_111, width)#, yerr=womenStd)
p7 = plt.bar(ind, two_100_111, width,
             bottom=(two_010_111[2]))#, yerr=womenStd)

p8 = plt.bar(ind, two_000_100, width,
             bottom=(two_100_111[2]+two_010_111[2]))#, yerr=womenStd)

p9 = plt.bar(ind, two_000_010, width,
             bottom=(two_010_111[2]+two_100_111[2]+two_000_100[2]))#, yerr=womenStd)
p10 = plt.bar(ind, two_000_111, width,
             bottom=(two_010_111[2]+two_100_111[2]+two_000_100[2]+two_000_010[2]))#, yerr=womenStd)
p11 = plt.bar(ind, two_010_100, width,
             bottom=(two_010_111[2]+two_100_111[2]+two_000_100[2]+two_000_010[2]+two_000_111[2]))#, yerr=womenStd)

p15 = plt.bar(ind, QF_111, width)#, yerr=womenStd)
p14 = plt.bar(ind, QF_010, width,
             bottom=(QF_111[3]))#, yerr=womenStd)

p13 = plt.bar(ind, QF_100, width,
             bottom=(QF_111[3]+QF_010[3]))#, yerr=womenStd)
p12 = plt.bar(ind, QF_000, width,
             bottom=(QF_100[3]+QF_111[3]+QF_010[3]))#, yerr=womenStd)


p16 = plt.bar(ind, only_000, width)#, yerr=womenStd)
p17 = plt.bar(ind, only_010, width,
             bottom=(only_000[4]))#, yerr=womenStd)

p18 = plt.bar(ind, only_100, width,
             bottom=(only_000[4]+only_010[4]))#, yerr=womenStd)
p19 = plt.bar(ind, only_111, width,
             bottom=(only_100[4]+only_000[4]+only_010[4]))#, yerr=womenStd)

plt.ylabel('# of Events')
plt.title('Classifications of Events')
plt.xticks(ind, ('ALL', '3 equals', '2 equals', 'QF', 'One Valid'))
#plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0], p7[0], p8[0], p9[0], p10[0], p11[0], p12[0], p13[0], p14[0], p15[0], p16[0], p17[0], p18[0], p19[0]),
           ("ALL", "three_100_111_000", "three_000_010_100", "three_010_111_000", "three_000_010_100",
            "two_010_111", "two_100_111", "two_000_100", "two_000_010", "two_000_111", "two_010_100", "QF_000", "QF_100", "QF_010", "QF_111", "Only_000", "Only_100", "Only_010", "Only_111"),
           loc ='best', ncol = 4)

if pathtodirectorySaveST != 'None':
    finaldirectorySave = pathtodirectorySave + 'Statistics/'
    checkFolder(finaldirectorySave)
    plt.savefig('{}NumberCluster_Decision.png'.format(finaldirectorySave))
else:
    plt.show()


