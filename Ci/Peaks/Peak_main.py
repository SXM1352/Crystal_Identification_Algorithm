__author__ = 'david.perez.gonzalez'
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:58:11 2021

@author: David
"""

# module imports
import argparse
import logging
import logging.config
import cPickle as pickle
import numpy as np

# class imports
from Peak_Labels import PeakLabels
from Peak_Finder import PeakFinder
from Peak_Plot import PeakPlot
from Peak_Helper import PeakHelper

"""
Peak_main.py provides a frame to run a peak finder on the corresponding
given data (flood maps split into regions of interest) by
looking at the median values of the complete sets of data. 
"""


# -------------Main---------------------------------
def main():
    """
    Runs the peak finder, assign the first labels on the peaks,
    plot the results and save them into a files (dictionaries)
    """
    logging.config.fileConfig('/home/janko.lambertus/Masterarbeit/Git/cia/ini-files/logging.ini')
    logging.getLogger('cia')

    logging.info('----------------------------------')
    logging.info('NEW RUN OF THE PROGRAM \n')
    # we can use an argparser for the values we use, this is temporary
    # or we could use a file
    # adapt to run for all the cog!
    parser = argparse.ArgumentParser()
    parser.add_argument('--HVD N', dest='HVD', help='Specifiy the HVD algorithm to show  \
                                                     (N where N= 0 (=000), 1 (=100), 2 (=010), 3 (=111) or -1 for ALL)')
    parser.add_argument('--fileDirectory', dest='fileDirect', help='Specifiy the name of the   \
                                                         directory where to read the files from')
    args = parser.parse_args()

    selected_HVD, pathtodirectoryRead = int(args.HVD), args.fileDirect
    # dir = '/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-12_-_15-42-31_-_2010002165_A41B0821-015_2021-03-08/2021-03-15_-_12-30-54_-_floodmapWithSources/ramdisks_2021-03-15_-_13-06-48/'

    readdir = pathtodirectoryRead + 'hist/'
    readdir_refSections = pathtodirectoryRead + 'RefSections/'
    savedir = pathtodirectoryRead
    # cg = 1 #0 for 000, 1 for 010, 2 for 100, 3 for 111 #CAREFUL WITH ORDER, it changes thresholds and more
    HVD_list = ["000", "010", "100", "111"]

    if selected_HVD == -1:
        n_HVD = 4
        fixed_cg = False
    else:
        n_HVD = 1
        fixed_cg = True
    for cg in range(n_HVD):
        if fixed_cg:
            cg = selected_HVD  # 0 for 000, 1 for 010, 2 for 100, 3 for 111
        HVD = HVD_list[cg]

        n_p_list = [36, 30, 30, 25]
        n_p = n_p_list[cg]  # number of pickles

        # ht_list = ["hist0", "hist01", "hist10", "hist1"]
        jr_fixed = None
        # jr_fixed = 5
        # ht = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist{}_{}.pickle'.format(HVD, p), 'rb')) for p in range(n_p)]
        # ht = [pickle.load(open('/home/david.perez/Desktop/Pickles/hist{}_{}.pickle'.format(HVD,jr_fixed)))]

        ht = [pickle.load(open('{}hist{}_{}.pickle'.format(readdir,
                                                           HVD, p), 'rb')) for p in range(n_p)]
        # ht = [pickle.load(open('/media/david.perez/pet-scratch/Measurements/Hypmed/2021-02-17_-_15-20-29_-_HypmedStacks/2021-03-01_-_13-29-22_-_2011002000_A41B069400001_2021-02-25/2021-03-01_-_16-27-02_-_floodmapWithSources2/ramdisks_2021-03-01_-_16-53-55/20210303_NEW-2021-02-17_hist/hist{}_{}.pickle'.format(HVD,jr_fixed)))]

        x_arr = []
        y_arr = []
        rows, dic_crystal = PeakHelper.CrystalDict()
        Centers_COG, dic_c = PeakHelper.ref_peaks()
        dic_palone = {}
        dic_rdefect = {}

        # we can use an ini-file to store the values we use, this temporary
        bins = 100  # same forall
        sigma = [3.3, 2.5, 1.5, 1.5]  # 3.3 works for 000,1.5 works fine for 111 and 100, 2.5 for 010 #normal
        # sigma = [3.3, 3, 3, 1.5] #3.3 works for 000,1.5 works fine for 111 and 100, 2.5 for 010

        # threshold = [2, 3, 2, 4]
        threshold = [2, 6, 7, 4]  #2 works for 000,4 in 111 for all and 6 for most(same for 010), 7 for 100, # for normal measurement with high activity source

        rmBackground = True  # forall
        convIter = 200  # forall with more tends to reagroup peaks and with less some are missing
        markov = False  # forall smoothing function to remark peaks, but works for us, peaks with different heights and sigmas
        mIter = 3  # forall no interest marov is false

        if cg == 0:  # cog000
            rows_accepted = 2  # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
            dop_columns_accepted = 3  # (3 for 100)(2 for 000 and 010) same
            len_columns_accepted = 2  # (3 for 100)(2 for 000 and 010) same      -1 when in the middle
            dop_min_cent = 5  # before 7 and 14(010)/7,15 for 000 and 100
            dop_max_cent = 15
            lenmin_cent = 3
            lenmax_cent = 11  # before 11(000), 8(010), 9(100)
        elif cg == 1:  # 010
            rows_accepted = 6  # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
            dop_columns_accepted = 2  # (3 for 100)(2 for 000 and 010) same
            len_columns_accepted = 2  # (3 for 100)(2 for 000 and 010) same     -1 when in the middle
            dop_min_cent = 5  # before 7 and 14(010)/7,15 for 000 and 100
            dop_max_cent = 14
            lenmin_cent = 2
            lenmax_cent = 8  # before 11(000), 8(010), 9(100)
        elif cg == 2:  # 100
            rows_accepted = 2  # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
            dop_columns_accepted = 6  # (3 for 100)(2 for 000 and 010) same
            len_columns_accepted = 3  # (3 for 100)(2 for 000 and 010) same     -1 when in the middle
            dop_min_cent = 7  # before 7 and 14(010)/7,15 for 000 and 100
            dop_max_cent = 15
            lenmin_cent = 3
            lenmax_cent = 8  # before 11(000), 8(010), 9(100)
        elif cg == 3:  # cog111
            rows_accepted = 7  # (2 for 000 and 100)(4 for 010)number of rows above and under the middle that we accept
            dop_columns_accepted = 7  # (3 for 100)(2 for 000 and 010) same
            len_columns_accepted = 4  # (3 for 100)(2 for 000 and 010) same    -1 when in the middle
            dop_min_cent = 5  # before 7 and 14(010)/7,15 for 000 and 100
            dop_max_cent = 15
            lenmin_cent = 3
            lenmax_cent = 11  # before 11(000), 8(010), 9(100)

        dop_columns_accepted_edge = 2

        dop_min_edge = 5  # always
        dop_max_edge = 9  # always

        lenmin_edge = 1  # always
        lenmax_edge = 5  # always

        for jr, roi_hist in enumerate(ht):
            # print("ROI_HIST!!!:", roi_hist[0][1])
            if jr == 15:
                with open('/home/janko.lambertus/SearchHighRes.pickle', 'wb') as handle:
                    pickle.dump(roi_hist, handle,
                                protocol=pickle.HIGHEST_PROTOCOL)

            pFinder = PeakFinder(cg, roi_hist, bins, sigma[cg], threshold[cg], rmBackground, convIter, markov, mIter)
            dic_rows = pFinder.runPeakFinder()  # steps[cg], cg) #100 for 111; in principle also for 100; 010 needs 50 (or less); and 000 auch
            if jr_fixed:
                jr = jr_fixed  # in  case we want to see only one
            else:
                pass
            pclosest, c_roi = pFinder.closest_to_cent(dic_rows, Centers_COG[cg], jr)

            pLabels = PeakLabels(cg, pclosest, c_roi, rows, dop_columns_accepted_edge, dop_min_edge, dop_max_edge,
                                 lenmin_edge, lenmax_edge, rows_accepted, dop_columns_accepted, len_columns_accepted,
                                 dop_min_cent, dop_max_cent, lenmin_cent, lenmax_cent)
            dic_crystal, dic_palone, dic_rdefect = pLabels.label(dic_palone, dic_rdefect, dic_crystal, dic_rows,
                                                                 dic_c[cg])  # auch global!!!

            print("palone", dic_palone)
            print("rdefect", dic_rdefect)
            # print("dc_c", dic_crystal[1703])


            # active_area = raw_input('jr={} (active area): '.format(jr))
            active_area = False
            if active_area:
            # if jr == 15:
                for ij in dic_rows.keys():
                    x = np.array(PeakHelper.Extract_x(dic_rows[ij][0]))
                    y = np.array(PeakHelper.Extract_y(dic_rows[ij][0]))
                    x_arr.append(x)
                    y_arr.append(y)
                # print("PLOTTER x_arr", x_arr)
                # print("PLOTTER y_arr", y_arr)
                # print("PLOTTER jr", jr)
                # print("PLOTTER HVD", HVD)
                # print("PLOTTER readdir_refSections", readdir_refSections)
                pplot = PeakPlot(x_arr, y_arr, jr, HVD, readdir_refSections)
                pplot.runPeakPlot()

        # with open('{}/dic-crystal-{}.pickle'.format(savedir, HVD), 'wb') as handle:
        #     pickle.dump(dic_crystal, handle, protocol=pickle.HIGHEST_PROTOCOL)

        logging.info('Dictionary containing labels of crystals saved in ' + savedir + '/ \n')

        # with open('{}/dic_pAlone-{}.pickle'.format(savedir, HVD), 'wb') as handle:
        #     pickle.dump(dic_palone, handle, protocol=pickle.HIGHEST_PROTOCOL)

        logging.info('Dictionary containing peaks which were not assigned to any row saved in ' + savedir + '/ \n')

        # with open('{}/dic_rDefect-{}.pickle'.format(savedir, HVD), 'wb') as handle:
        #     pickle.dump(dic_rdefect, handle, protocol=pickle.HIGHEST_PROTOCOL)

        logging.info('Dictionary containing wrongly assigned rows of peaks saved in ' + savedir + '/ \n')

    logging.info('Thanks for using our software. Hope to see you soon. ## (in Peak_main)\n')


if __name__ == '__main__':
    main()
