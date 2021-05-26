import os, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                 directory where to read the files from')
parser.add_argument('--stackID', dest='sID', help='Specifiy the stackID to be read')

args = parser.parse_args()
pathtodirectoryRead, stack_id = args.fileDirect, args.sID

number = 1
file = "{}{}.DebugSingles".format(pathtodirectoryRead, stack_id)
count = 0

try:
    with open(file,'r+b') as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            if char != '\n' and f.tell() == end:
                # print "No change: file does not end with a newline"
                # exit(1)
                pass
            if char == '\n':
                count += 1
            if count == number + 1:
                f.truncate()
                print "Removed " + str(number) + " lines from end of file"
                exit(0)
            f.seek(-1, os.SEEK_CUR)
            print('Done.')
except:
    number = 1
    file = "{}{}.DebugCoincidentSingles".format(pathtodirectoryRead, stack_id)
    count = 0
    with open(file,'r+b') as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        while f.tell() > 0:
            f.seek(-1, os.SEEK_CUR)
            char = f.read(1)
            if char != '\n' and f.tell() == end:
                # print "No change: file does not end with a newline"
                # exit(1)
                pass
            if char == '\n':
                count += 1
            if count == number + 1:
                f.truncate()
                print "Removed " + str(number) + " lines from end of file"
                exit(0)
            f.seek(-1, os.SEEK_CUR)

if count < number + 1:
    print "No change: requested removal would leave empty file"
    exit(3)