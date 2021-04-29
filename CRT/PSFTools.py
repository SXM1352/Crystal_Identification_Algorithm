__author__ = 'florian.mueller'

import collections
import numpy as np
from scipy import optimize, interpolate
import matplotlib.pyplot as plt
import logging
from ROOT import TGraph, TH1D, TH1F, TH2D, TCanvas, TList, TLegend, gStyle, TBox, TAttLine, gROOT, TArrow, TF1
from ROOT import SetOwnership
gROOT.SetBatch(False)

from Help import plot2D


class PSFTools:
    """
    Creating and manipulation different types of PSF, calculating percentiles and bias vectors. Additionally,
    the use a discrete 2d polar _coordinates is possible. Values obtained with these _coordinates don't rely on a
    projection and are therefore more reliable. Methods based on those choice or marked with the beginning
    TwoD... .
    """
    def __init__(self):
        pass

    def plotSimplePSF(self, data, save_plots=False): #ToDO Update function
        """
        Function creates PSF in 2D as well as x and y projections. Additionally quantiles are calculated.
        Plots can be saved to a .root file.

        @param data: PSFData
        @type data: posX, posY, last row: position of beam, shape(-1,2)
        @param save_plots: Option allows to _save all plots to a .root file, default: False
        @type save_plots: True/False
        @return: projectionX.GetMean(), projectionX.GetRMS(), projectionY.GetMean(), projectionY.GetRMS(), container_quantilesX[4], container_quantilesY[4]
        @rtype: tuple
        """
        list_plots = TList() #container for ROOT plots
        list_canvas = TList() #container for ROOT canvas
        #creating 2D PSF
        canvasPSF=TCanvas("PSF","",600,600)
        PSF = TH2D("", "", 21, -2.75*2, 2.75*2, 21, -2.75*2, 2.75*2)
        #PSF = TH2D("", "", 11*4, -2.75*4, 2.75*4, 11*4, -2.75*4, 2.75*4)
        PSF.GetXaxis().SetTitle("x [mm]")
        PSF.GetYaxis().SetTitle("y [mm]")
        posXRef, posYRef = data[-1][0], data[-1][1]
        data = np.delete(data, -1,0)
        for i in range(0, data.shape[0]):
            PSF.Fill(posXRef - data[i][0], posYRef - data[i][1],1)
        scale_factor = PSF.Integral()
        PSF.Scale(1/scale_factor)
        PSF.SetName("PSF " + str(posXRef) + " " + str(posYRef))
        PSF.SetTitle("PSF " + str(posXRef) + " " + str(posYRef))
        PSF.SetOption("COLZ")
        PSF.Draw("COLZ")

        #creating projectionX
        canvasProjX = TCanvas("projX","",600,600)
        projectionX = PSF.ProjectionX()
        scale_factor = projectionX.Integral()
        if scale_factor!=0: projectionX.Scale(1/scale_factor)
        projectionX.SetName("ProjectionX")
        projectionX.SetTitle("ProjectionX")
        projectionX.Draw()
        container_quantilesX = np.empty([5])
        probs = np.array([0.1,0.25,0.5,0.75,0.9])
        projectionX.GetQuantiles(5, container_quantilesX, probs)
        projectionX.SetStats(0)
        legProjX = TLegend(0.8,0.8,1,1)
        SetOwnership(legProjX, 0 )   # 0 = release (not keep), 1 = keep
        #legProjX.SetHeader("Projection X")
        legProjX.AddEntry(projectionX, "Entries: " +str(projectionX.GetEntries()), "")
        legProjX.AddEntry(projectionX, "Mean: " + str(projectionX.GetMean()),"")
        legProjX.AddEntry(projectionX, "RMS: " + str(projectionX.GetRMS()), "")
        for i in range(0, probs.shape[0]):
            legProjX.AddEntry(projectionX, str(probs[i]) + " quantile: " + str(container_quantilesX[i]), "" )
        legProjX.Draw()

        #creating cumulative projectionX
        canvasProjXCum = TCanvas("projXCum", "", 600,600)
        projectionXCumulative = projectionX.GetCumulative()
        projectionXCumulative.SetName("ProjectionX Cumulative")
        projectionXCumulative.SetTitle("ProjectionX Cumulative")
        projectionXCumulative.Draw()

        #creating projectionY
        canvasProjY = TCanvas("projY", "", 600,600)
        projectionY = PSF.ProjectionY()
        scale_factor = projectionY.Integral()
        if scale_factor != 0: projectionY.Scale(1/scale_factor)
        projectionY.SetTitle("ProjectionY")
        projectionY.SetName("ProjectionY")
        projectionY.Draw()
        container_quantilesY = np.empty([5])
        probs = np.array([0.1,0.25,0.5,0.75,0.9])
        projectionY.GetQuantiles(5, container_quantilesY, probs)
        projectionY.SetStats(0)
        legProjY = TLegend(0.8,0.8,1,1)
        SetOwnership(legProjY, 0 )   # 0 = release (not keep), 1 = keep
        legProjY.AddEntry(projectionY, "Entries: " +str(projectionY.GetEntries()), "")
        legProjY.AddEntry(projectionY, "Mean: " + str(projectionY.GetMean()),"")
        legProjY.AddEntry(projectionY, "RMS: " + str(projectionY.GetRMS()), "")
        for i in range(0, probs.shape[0]):
            legProjY.AddEntry(projectionY, str(probs[i]) + " quantile: " + str(container_quantilesY[i]), "" )
        legProjY.Draw()

        #creating cumulative projectionY)
        canvasProjYCum = TCanvas("projYCum", "", 600,600)
        projectionYCumulative = projectionY.GetCumulative()
        projectionYCumulative.SetName("ProjectionY Cumulative")
        projectionYCumulative.SetTitle("ProjectionY Cumulative")
        projectionYCumulative.Draw()

        #saving plots to list_plots
        list_plots.Add(PSF)
        list_plots.Add(projectionX)
        list_plots.Add(projectionXCumulative)
        list_plots.Add(projectionY)
        list_plots.Add(projectionYCumulative)
        if save_plots:
            list_plots.SaveAs("PSFplots.root")
        #saving_plots to list_canvas
        list_canvas.Add(canvasPSF)
        list_canvas.Add(canvasProjX)
        list_canvas.Add(canvasProjXCum)
        list_canvas.Add(canvasProjY)
        list_canvas.Add(canvasProjYCum)
        #return list_canvas
        return ([projectionX.GetMean(), projectionX.GetRMS(), projectionY.GetMean(), projectionY.GetRMS(), container_quantilesX[4], container_quantilesY[4]])

    def _splitPSFData(self, data, center_data=True):
        """
        Splits PSF data from positioning method's extractTestDataPSFData function.

        @param data: PSFData
        @type data: posX, posY, last row: position of beam, shape(-1,2)
        @param center_data: centers data around beam position, default = True
        @type center_data: True/False
        @return: splitted PSF data
        @rtype: tuple: x (np.array), y (np.array), posX (beam position), posY (beam position)
        """
        if center_data:
            return self._centerData(data)
        else:
            posX, posY = data[-1][0], data[-1][1]
            data = np.delete(data, -1, 0)
            x, y = data[:,0], data[:,1]
            return (x, y, posX, posY)

    def _centerData(self, data):
        """
        Centers given PSFdata around (0,0) and returns them.

        @param data: PSFdata
        @type data: posX, posY, last row: position of beam, shape(-1,2)
        @return: x _coordinates, y _coordinates, position of beam in global coordinate system (x and y)
        @rtype: tuple: x,y,posX,posY
        """
        PSFdata = data
        posX, posY = PSFdata[-1][0], PSFdata[-1][1]
        PSFdata = np.delete(PSFdata, -1, 0)
        x, y = PSFdata[:,0] - posX, PSFdata[:,1] - posY
        return (x, y, posX, posY)

    def fwxm_cross_section(self, data, bin_width = 0.25, min_pos = -15.875, max_pos = 15.875, threshold = 0.5, spline_interpolation = 0.01, control_plots=False):
        x, y, posX, posY = self._splitPSFData(data)

        x_edges = np.arange(min_pos - bin_width/2, max_pos + 3*bin_width/2, bin_width)  # setting up the bin edges and central positions
        x_center = x_edges - bin_width/2
        x_center = x_center[1:]
        y_edges = np.arange(min_pos - bin_width/2, max_pos + 3*bin_width/2, bin_width)
        y_center = y_edges - bin_width/2
        y_center = y_center[1:]
        x_interpolated_edges = np.linspace(min(x_edges), max(x_edges), num=int(len(x_edges)/spline_interpolation), endpoint=True)
        y_interpolated_edges = np.linspace(min(y_edges), max(y_edges), num=int(len(y_edges)/spline_interpolation), endpoint=True)

        hist = np.histogram2d(x, y, bins=(x_edges, y_edges))  # create the 2D hist and the cross sections
        if control_plots:
            plot2D(hist[0], add_text=False, show=False)
            plt.title("2D histogram PSF")
            plt.xlabel("positioning error x / mm")
            plt.ylabel("positioning error y / mm")
            plt.show()
        ind_cross_sec_x, ind_cross_sec_y = np.where(np.max(hist[0]) == hist[0])
        cross_sec_x = hist[0][ind_cross_sec_x].flatten()
        cross_sec_y = hist[0][:,ind_cross_sec_y].flatten()

        spline_x = interpolate.splrep(x_center, cross_sec_x)  # interpolate the cross sections with spline
        interpolated_cross_sec_x = interpolate.splev(x_interpolated_edges, spline_x)
        spline_y = interpolate.splrep(y_center, cross_sec_y)
        interpolated_cross_sec_y = interpolate.splev(y_interpolated_edges, spline_y)

        def _fwxm(x, y, control_plots=False, label=None):  # calculate fwxm; not the most efficient way, should be fast enough and reliable
            ind_max = np.argmax(y)
            right = ind_max + 1
            while y[right] > threshold * y[ind_max]:
                right += 1
            left = ind_max -1
            while y[left] > threshold * y[ind_max]:
                left -= 1
            fwxm = x[right] - x[left]
            if control_plots:
                plt.plot(x, y, label="width {0} mm".format(np.round(x[right]-x[left], 2)))
                plt.xlabel("positioning error / mm")
                plt.ylabel("counts")
                plt.arrow(x[left], y[ind_max]*threshold, x[right] - x[left], 0)
                plt.title("Cross Section {0}".format(label))
                plt.legend()
                plt.show()
            return fwxm
        fwxm_x = _fwxm(x_interpolated_edges, interpolated_cross_sec_x, control_plots=control_plots, label="x")
        fwxm_y = _fwxm(y_interpolated_edges, interpolated_cross_sec_y, control_plots=control_plots, label="y")
        return (fwxm_x, fwxm_y)

    def fwxmProjection(self, data, threshold=0.5, center_data=True, control_plots=False, output=False, step=0.1):
        """
        Calculates the FWXM of x and y projection of the given data. Returns a dict containing the information.
        Remark: To use this function, numpy version 1.9 or newer is required.

        @param data: PSFdata, extracted from positioning methods using theit extractTestDataPSF function
        @type data: posX, posY, last row: position of beam, shape(-1,2)
        @param threshold: fraction of the peak maximum (e.g. 0.5 for FWHM)
        @type threshold: number
        @param control_plots: opens control plots, default:False
        @type control_plots: True/False
        @param output: prints output to screen, default:False
        @type output: True/False
        @param step: Start point for binning search. Binning will be never lower than this threshold.
        @type step: float
        @return: FWXM for x and y projection as well as position of beam
        @rtype: dictionary with the following keys: projX (FWXM of x projection), projY (FWXM of y projection),
        posX (beam position x), posY (beam position y), x_max (projection x: maximum of peak; maybe centered data used?),
        y_max (projection y: maximum of peak; maybe centered data used?)
        """
        x, y, posX, posY = self._splitPSFData(data, center_data)
        # collaps data, np.unique function is used, requires numpy 1.9 or newer
        def binner(data):
            frequencies, bins = np.histogram(data, bins="auto")
            step_size= bins[1]-bins[0]
            distances = np.arange(bins[0]+step_size, bins[-1]+step_size/2, step_size)
            return distances, frequencies
        def binner2(data, step=0.1):
            good_binning = False
            step = step
            while not good_binning:
                step_before = step
                delta_step = 0.01
                frequencies, bins = np.histogram(data, bins = np.arange(-5,5.1,step))
                if output:
                    print "step", step, "frequencies", frequencies
                max_bin = np.argmax(frequencies)
                if output:
                    print frequencies[max_bin+1], frequencies[max_bin+2]
                for i in range(min(frequencies.shape[0]-max_bin-1, 4)):
                    if frequencies[max_bin + i] < frequencies[max_bin + i + 1]:
                        step += delta_step
                        delta_step = 0
                for i in range(min(max_bin-1,4)):
                    if frequencies[max_bin - i] < frequencies[max_bin - i - 1]:
                        step += delta_step
                        delta_step = 0
                if step_before == step:
                    good_binning = True
            distances = np.arange(bins[0]+step, bins[-1]+step/2, step)
            return distances, frequencies
        try:
            #x_distances, x_frequencies = np.unique(x, return_counts=True)
            #y_distances, y_frequencies = np.unique(y, return_counts=True)
            x_distances, x_frequencies = binner2(x, step)
            y_distances, y_frequencies = binner2(y, step)
            if output:
                print "x", x_distances, x_frequencies
                print "y", y_distances, y_frequencies
        except:
            print 'Numpy version 1.9 or newer is needed!'
        x_left, x_max, x_right = self.fwxm(x_distances, x_frequencies, threshold, control_plots)
        y_left, y_max, y_right = self.fwxm(y_distances, y_frequencies, threshold, control_plots)
        if output:
            print "Used threshold: ", threshold, " of maximum"
            print "Projection X:"
            print "left, max, right : ", x_left, x_max, x_right
            print "difference: ", abs(x_right - x_left)
            print "Projection Y:"
            print "left, max, right : ", y_left, y_max, y_right
            print "difference: ", abs(y_right - y_left)
        return {"projX": abs(x_right - x_left), "projY": abs(y_right - y_left), "posX": posX, "posY": posY, "x_max": x_max, "y_max": y_max}

    def percentiles(self, data, probs="", center_data=True):
        """
        Calculates percentiles of given data.

        @param data: PSFData
        @type data: posX, posY, last row: position of beam, shape(-1,2)
        @param probs: percentiles which should be probed, default: [0.1, 0.32, 0.5, 0.68, 0.9]
        @type probs: np.array containing percentiles
        @param center_data: option to center data around beam position, default: True
        @type center_data: True/False
        @return: percentiles of x and y projection as well as the used probs
        @rtype: dictionary with the following keys: xpercentiles, ypercentiles, probs
        """
        x, y, posX, posY = self._splitPSFData(data, center_data)
        x.sort()
        y.sort()
        if probs == "":
            probs = np.array([0.1, 0.32, 0.5, 0.68, 0.9]) #defining the used probs
        else:
            probs = probs
        length = x.shape[0]
        quantiles = np.ceil(probs*length).reshape([1,-1]) #reshaping for use as indices in array
        xpercentiles = x[tuple(quantiles.astype(int))].reshape([-1])
        ypercentiles = y[tuple(quantiles.astype(int))].reshape([-1])
        return {"xpercentiles": xpercentiles, "ypercentiles": ypercentiles, "probs": probs}

    def twoDPercentiles(self, data, probs="", bias_corrected=False, show_plot=False):
        """
        Calculates different percentiles on basis of euclidean distance.

        @param data: input data
        @type data: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        @param probs: percentiles which are calculated. If input is None, following values are calculated: 0.1, 0.32, 0.5, 0.68, 0.9
        @type probs: None or np.ndarray of shape (X,)
        @return: percentiles, probs
        @rtype: dict (np.ndarray of shape (X,) for probs and percentiles)
        """
        PSFdata = data
        posX, posY = PSFdata[-1][0], PSFdata[-1][1]
        PSFdata = np.delete(PSFdata, -1, 0)
        if bias_corrected:
            print "in bias correction"
            bias = self.biasVector(data)
            PSFdata[:,0], PSFdata[:,1] = PSFdata[:,0] - bias["x_component"], PSFdata[:,1] - bias["y_component"]
        distances = np.sqrt((PSFdata[:,0] - posX)**2 + (PSFdata[:,1] - posY)**2).reshape([-1,1])
        distances = np.sort(distances, axis= 0)
        length = distances.shape[0]
        if show_plot:
            x = np.linspace(0, 1, length, True)
            plt.plot(x, distances)
            plt.grid()
            plt.axvline(0.9)
            title = "Detector percentile function"
            if bias_corrected:
                title += " bias corrected"
            plt.title(title)
            plt.xlabel("Percentile")
            plt.ylabel("radius [mm]")
            plt.show()
        if probs == "":
            probs = np.array([0.1, 0.32, 0.5, 0.68, 0.9]) #defining the used probs
        else:
            probs = probs
        quantiles = np.ceil(probs*length).reshape([1,-1]) #reshaping for use as indices in array
        return {"percentiles": distances[tuple(quantiles.astype(int))].reshape([-1]), "probs": probs}

    def MAE(self, data):
        """
        Calculate the mean absolute error (MAE). For a two-dimensional distribution, the absolute error is based
        on the Euclidean distance.

        @param data: PSFdata
        @return: MAE
        @rtype: float
        """
        x, y, posX, posY = self._splitPSFData(data, False)
        absolute_error = np.sqrt((x - posX)**2 + (y - posY)**2)
        mae = np.mean(absolute_error)
        return mae

    def RMSE(self, data):
        """
        Caulculate the root mean squared error (RSME). For a two-dimensional distribution, the absolute error is based
        on the Euclidean distance.

        @param data: PSFdata
        @return: RMSE
        @rtype: float
        """
        x, y, posX, posY = self._splitPSFData(data, False)
        absolute_error = np.sqrt((x - posX)**2 + (y - posY)**2)
        mse = np.mean(np.square(absolute_error))
        rmse = np.sqrt(mse)
        return rmse

    def cumulativeDistributionFunction(self, data, abs_error=True, finalize=True, return_plot=False, xlim=-1, plot_percentile=False, percentile_list=[0.9]):
        """
        Cumulative Distribution Function for a given position. Method allows to collect multiple position and plots
        them into one graph.

        @param data: PSF data
        @type data: PSF data
        @param abs_error: Calculate and plot absolute error of positioning. Otherwise the errors of x and y direction
        are calculated and plotted separately. Default: True
        @type abs_error: True/False
        @param finalize: Finalizes the plot and display. If the plot is returned, displaying it is not possible.
        Default: True
        @type finalize: True/False
        @param return_plot: Returns plot and allows further modifications. Default: False
        @type return_plot: True/False
        @param xlim: maximum of x axis
        @type xlim: flaot
        @param plot_percentile: Plots lines for the given percentile values.
        @type plot_percentile: True/False
        @param percentile_list: Percentile values that will be marked with a line. Percentile and quantile values can be
        passed to the function.
        @type percentile_list: list of percentile or quantile values
        @return:
        @rtype:
        """
        x, y, posX, posY = self._splitPSFData(data, center_data=False)
        if abs_error:
            distances = np.sqrt((x - posX)**2 + (y - posY)**2).reshape([-1,1])
            distances = np.sort(distances, axis=0)
            length = distances.shape[0]
            scale = np.linspace(0, 1, length, True)
            plt.plot(distances, scale, label=str(posX) + "/" + str(posY))
        else:
            distancesX = abs(x-posX)
            distancesX = np.sort(distancesX, axis=0)
            distancesY = abs(y-posY)
            distancesY = np.sort(distancesY, axis=0)
            length = distancesX.shape[0]
            scale = np.linspace(0, 1, length, True)
            plt.plot(distancesX, scale, label="x-dir " + str(posX))
            plt.plot(distancesY, scale, label="y-dir " + str(posY))
        if plot_percentile:
            def plot_percentile(quantile, distances):
                length = distances.shape[0]
                value = distances[int(np.ceil(quantile*length))]
                plt.hlines(quantile, 0, value)
                plt.vlines(value, 0, quantile)
            for elem in percentile_list:
                if elem > 1:
                    elem /= 100.
                if abs_error:
                    plot_percentile(elem, distances)
                else:
                    print "Plotting percentile lines only available for absolute errors!"
        if finalize:
            if xlim >= 0:
                plt.xlim(0, xlim)
            plt.grid()
            plt.rc("font", size=20)
            plt.xlabel("error / mm")
            plt.ylabel("normalized probability")
            plt.title("Cumulative Distribution Function")
            plt.tight_layout()
            plt.legend(loc="best")
            if not return_plot:  # otherwise plot is deleted
                plt.show()
        if return_plot:
            return plt

    def _twoDPSFNormalizationFactors(self, posX1, posX2, posY1, posY2, binning):
        """
        Calculating the frequencies of the occuring values in discrete half-room polar _coordinates for normalization.

        @param posX1: starting point X
        @type posX1: float
        @param posX2: starting point Y
        @type posX2: float
        @param posY1: end point X
        @type posY1: float
        @param posY2: end point Y
        @type posY2: float
        @param binning: binning of the grid
        @type binning: float
        @return frequencies of the occuring values and values
        @rtype python dictionary; values accessable by .keys(), frequencies by .values()
        """
        gridX = np.arange(posX1, posX2 + binning, binning)
        gridY = np.arange(posY1, posY2 + binning, binning)
        distanceList = []
        logging.debug(gridX, gridY)
        for posX in gridX:
            for posY in gridY:
                distance = np.sqrt(posX**2 + posY**2)
                if posY > 0:
                    distanceList.append(distance)
                elif posY < 0:
                    distanceList.append(-1.*distance)
                elif posY == 0 and posX >= 0:
                    distanceList.append(distance)
                else:
                    distanceList.append(-1.*distance)
        import collections
        counter = collections.Counter(distanceList)
        return counter

    def _twoDPSFNormalizationFactorsBinning(self, posX1, posX2, posY1, posY2, binning, save=False):
        """
        Calculates normalization factors for discrete polar _coordinates by using an equidistant binning. Allows to _save the histogram with option="_save".

        @param posX1: starting point X
        @type posX1: float
        @param posX2: starting point Y
        @type posX2: float
        @param posY1: end point X
        @type posY1: float
        @param posY2: end point Y
        @type posY2: float
        @param binning: binning of the grid
        @type binning: float
        @param save: saving histogram to a root file, default= False
        @type option: True/False
        @return: dictionionary with normaliaztion factors, min of hist, max of hist and number bins of hist
        @rtype: dictionionary with keys: normalization_list (python list with BinCenter, BinContent), hist_min, hist_max, number_bins
        """
        counter = self._twoDPSFNormalizationFactors(posX1, posX2, posY1, posY2, binning)
        values = counter.keys()
        weights = counter.values()
        length = np.amax(values) - np.amin(values)
        number_bins = int(np.ceil(length/binning))
        return_dict = {"hist_min": np.amin(values), "hist_max": np.amax(values) + binning, "number_bins": number_bins }
        hist = TH1D("", "", number_bins, np.amin(values) - binning, np.amax(values)+binning)
        for i in range(len(values)):
            hist.Fill(values[i], weights[i])
        if save:
            hist.SetStats(0)
            hist.GetXaxis().SetTitle("value [mm]")
            hist.GetYaxis().SetTitle("#")
            hist.SetTitle("Normalization factors including rebinning for 2D PSF")
            hist.Draw()
            hist.SaveAs("histbinning.root")
        normalization_list = []
        for i in range(number_bins):
            normalization_list.append([hist.GetBinCenter(i), hist.GetBinContent(i)])
        return_dict["normalization_list"] = normalization_list
        return return_dict

    def plotTwoDPSF(self, data, binning, save=False):
        """
        Plots the 2D PSF function of a given point by the data based on discrete, splitted polar _coordinates. Saving the histogram with option="_save"

        @param data: input data, can usually be generated by the ExtractPSFTestData method of the Positioning algorithms.
        @type data: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        @param binning: binning of the data which yields to the PSFTestdata
        @type binning: float
        @param save: allows saving histogram, default: False
        @type save: True/False
        @return: histogram
        @rtype: ROOT TH1D
        """
        PSFdata = data
        posX, posY = PSFdata[-1][0], PSFdata[-1][1]
        PSFdata = np.delete(PSFdata, -1, 0)
        x, y = PSFdata[:,0] - posX, PSFdata[:,1] - posY
        length = x.shape[0]
        distance = np.sqrt(x**2 + y**2)
        # aquiering normalization factors and hist infos
        hist_infos = self._twoDPSFNormalizationFactorsBinning(np.min(x), np.max(x), np.min(y), np.max(y), binning)
        normalization_list = hist_infos["normalization_list"]
        hist_min = hist_infos["hist_min"]
        hist_max = hist_infos["hist_max"]
        bins = hist_infos["number_bins"]
        # calculate distances and fill to histogram
        canvas = TCanvas("2DPSF", "", 600, 600)
        hist = TH1D("2DPSF", "", bins, hist_min, hist_max)
        for i in range(length):
            if y[i] < 0:
                distance[i] *= -1
            elif y[i] == 0 and x[i] < 0:
                distance[i] *= -1
            hist.Fill(distance[i])
        normalized_bin_content = 1
        for i in range(bins):
            if normalization_list[i][1] != 0:
                normalized_bin_content = hist.GetBinContent(i)/normalization_list[i][1]
                print hist.GetBinContent(i), normalization_list[i][1], normalized_bin_content
            hist.SetBinContent(i, normalized_bin_content)
        hist.Scale(1./hist.Integral())
        hist.GetXaxis().SetTitle("distance [mm]")
        hist.GetYaxis().SetTitle("#")
        hist.SetTitle("2D PSF function based on discrete polar _coordinates for " + str(posX) + "," + str(posY))
        if save:
            hist.SaveAs("2dpsf" + str(posX) + "_" + str(posY) + ".root")
        return hist

    def plotTwoDPSFg(self, data, binning, save=False, output=False):
        """
        Plots the 2D PSF function of a given point by the data based on discrete, splitted polar _coordinates.
        Fits a gaussian shape to the distribution and calculates FWHM. Saving the graph with option="_save"

        @param data: input data, can usually be generated by the ExtractPSFTestData method of the Positioning algorithms.
        @type data: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        @param binning: binning of the data which yields to the PSFTestdata
        @type binning: float
        @param save: allows saving histogram to .root file, default: False
        @type save: True/False
        @param output: Prints results for FWHM, FWTM of fit and NEMA conform method, default: False
        @type output: True/False
        @return: graph
        @rtype: TGraph
        """
        from math import exp
        x, y, posX, posY = self._centerData(data)
        length = x.shape[0]
        distance = np.sqrt(x**2 + y**2)
        for i in range(length):
            if y[i] < 0:
                distance[i] *= -1
            elif y[i] == 0 and x[i] < 0:
                distance[i] *= -1
        distance_counter = collections.Counter(distance)
        counter = self._twoDPSFNormalizationFactors(np.amin(x), np.amax(x), np.amin(y), np.amax(y), binning)
        distance_final = []
        frequency_final =  []
        for key in counter:
            distance_counter[key] /= float(counter[key])
            distance_final.append(key)
            frequency_final.append(distance_counter[key])
            #print distance_counter[key], key
        distance_final, frequency_final = np.array(distance_final), np.array(frequency_final)
        #print distance_final.shape, frequency_final.shape
        canvas = TCanvas("2DPSF", "", 600, 600)
        graph = TGraph(distance_final.shape[0], distance_final, frequency_final)
        graph.SetMarkerStyle(3)
        graph.SetMarkerSize(3)
        graph.GetXaxis().SetTitle("distance [mm]")
        graph.GetYaxis().SetTitle("#")
        graph.SetTitle("2D PSF discrete polar _coordinates for " + str(posX) + "," + str(posY))
        graph.Draw("AP")
        # fits gaussian shape and caluclates FWHM
        fit=TF1("fit","[0]*exp(-0.5*((x-[1])/[2])**2)")
        fit.SetParameter(0, 800)
        fit.SetParameter(1, 0)
        fit.SetParameter(2, 0.3)
        fit.SetParName(0, "constant")
        fit.SetParName(1, "mean")
        fit.SetParName(2, "sigma")
        graph.Fit("fit", "", "", -10,10)
        sigma = fit.GetParameter(2)
        FWHM = 2.35482 * sigma
        FWTM = 4.29193 * sigma
        # adding legend to graph
        leg = TLegend(0.8,0.8,0.9,0.9)
        SetOwnership(leg, 0 )   # 0 = release (not keep), 1 = keep
        leg.AddEntry("", "FWHM " + str(FWHM) + " mm")
        leg.AddEntry("", "FWTM " + str(FWTM) + " mm")
        leg.Draw()
        if save:
            canvas.SaveAs("./PSF/2DPSF" + str(posX) + "_" + str(posY) +".root")
            control_plot_FWXM = True
        else:
            control_plot_FWXM = False
        left2, max2, right2 = self.fwxm(distance_final, frequency_final, 0.5, control_plot_FWXM)
        left10, max10, right10 = self.fwxm(distance_final, frequency_final, 0.1, control_plot_FWXM)
        if output:
            print "results fit"
            print "FWHM , FWTM" ,abs(FWHM), abs(FWTM)
            print "results NEMA"
            print "FWHM", "FWTM", abs(right2 - left2), abs(right10 - left10)
        return {"FWHM": abs(right2 - left2), "FWTM": abs(right10 - left10), "posX": posX, "posY": posY, "FWHM_x_max": max2, "FWTM_x_max": max10, "FWHMfit": abs(FWHM), "FWTMfit": abs(FWTM), "graph": graph}

    def fwxm(self, x, y, relative_threshold, control_plots=False, save_plots=False):
        """
        Determines the left and right x-position for peak data at a given
        threshold relative to the y-maximum.

        @param x: Array of x axis
        @type x: np array
        @param y: Array of y axis
        @type y: np array
        @param relative_threshold: fraction of the peak maximum (e.g. 0.5 for FWHM)
        @type relative_threshold: float
        @param save_plots: Saves plots in the current directory, default: False
        @type save_plots: True/False
        @return: (left, max, right) in x
        @rtype: tuple of floats
        """
        #assert len(x) == len(y)
        if len(y) < 3:
            return (0, 0, 0)

        maxbin = np.argmax(y)
        # maxbin 0 leads to an error due to the shift left for the minimum bound. Thus, the maxbin is shifted to the right
        if maxbin == 0:
            maxbin += 1
        fit_range = slice(maxbin-19, maxbin+20)
        parameters = np.polyfit(x[fit_range], y[fit_range], 2)
        xmax = -parameters[1] / (2*parameters[0])
        parabolic = lambda x: parameters[0] * x**2 + parameters[1] * x + parameters[2]
        ymax = parabolic(xmax)
        interpolation = interpolate.interp1d(x, y)

        # find the closest bins around maximum under threshold
        below_threshold = np.where(y - relative_threshold*ymax < 0)[0]
        # test if we don't fall under the threshold for the given data
        if (below_threshold > maxbin).all() or (below_threshold < maxbin).all():
            logging.warning("FWXM according to NEMA couldn't be calculated!")
            return (np.nan, np.nan, np.nan)
        x0 = x[below_threshold[below_threshold < maxbin][-1]]
        x1 = x[below_threshold[below_threshold > maxbin][0]]

        left, right = self._fwxm_f(interpolation, relative_threshold*ymax, xmax, x0, x1)
        if control_plots:
            import matplotlib.pyplot as plt
            plt.step(x, y, where="mid", color="blue")
            parabolic_x = np.linspace(x[fit_range.start], x[fit_range.stop - 1], 100)
            plt.plot(parabolic_x, parabolic(parabolic_x), color="black")
            plt.xlim(xmax - 5*(xmax - left), xmax + 5*(right - xmax))
            plt.annotate("", xy=(left, relative_threshold*ymax),
                         xytext=(right, relative_threshold*ymax),
                         arrowprops=dict(arrowstyle="<->"))
            if save_plots:
                plt.savefig("fwxm_nema.png")
            plt.show()
        return (left, xmax, right)

    def _fwxm_f(self, f, threshold, xmax, a, b):
        """
        Determines the left and right position of a peak-like function at a given
        threshold (e.g. ymax/2 for FWHM).

        @param f: 1D continuous function (e.g. from interp1d())
        @type f: scipy.interp1d()
        @param threshold: the y-threshold of function for which the width of
        the peak will be determined
        @type threshold: float
        @param xmax: the x-position of the maximum
        @type xmax: float
        @param a: lower end of the search interval in which the width must lie
        @type a; float
        @param b: upper end of the search interval
        @type b: float
        @return: left and right position
        @rtype: tuple of floats
        """
        g = lambda x: f(x) - threshold
        if g(a) * g(xmax) > 0:
            left = a
        else:
            left = optimize.brentq(g, a, xmax)
        if g(b) * g(xmax) > 0:
            right = b
        else:
            right = optimize.brentq(g, xmax, b)
        return (left, right)

    def biasVector(self, data):
        """
        Calculates the averaged bias vector.

        @param data: input data
        @type data: np.ndarray posX, posY, last row: position of beam, shape(-1,2)
        @return: averaged bias vector-components (basis and vector)
        @rtype: Python list [posX, posY, x_component, y_component, vector_length]
        """
        PSFdata = data
        posX, posY = PSFdata[-1][0], PSFdata[-1][1]
        PSFdata = np.delete(PSFdata, -1, 0)
        length = float(PSFdata.shape[0])
        x_component, y_component = sum(PSFdata[:,0] - posX)/length, sum(PSFdata[:,1] - posY)/length
        vector_length = np.sqrt(x_component**2 + y_component**2)
        return {"posX": posX, "posY": posY, "x_component": x_component, "y_component": y_component, "vec_length": vector_length}

    def sr(self, data):
        """
        Calculates the averaged euclidean distance between true beam position and estimated position.

        @param data: input data, can usually be generated by the ExtractPSFTestData method of the Positioning algorithms.
        @type data: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        @return: averaged euclidean distance, posX, posY
        @rtype: dict
        """
        x, y, posX, posY = self._splitPSFData(data, center_data=True)
        SR = np.sqrt(x**2 + y**2)
        SR = np.sum(SR)/x.shape[0]
        return {"SR": SR, "posX": posX, "posY": posY}

    def score(self, data, limit=1, bias_corrected=False):
        """
        Calculates the percentage of events that are positioned in a given circle around the beam position.

        @param data: input data, can usually be generated by the ExtractPSFTestData method of the Positioning algorithms.
        @type data: np.ndarray; posX, posY, last row: position of beam, shape(-1,2)
        @param limit: Limit which defines the circle
        @type limit: float
        @return: score
        @rtype: float
        """
        x, y, posX, posY = self._splitPSFData(data, center_data=True)
        if bias_corrected:
            print "in bias correction"
            bias = self.biasVector(data)
            x, y = x - bias["x_component"], y - bias["y_component"]
        dist = np.sqrt(x**2 + y**2)
        inside = 0.
        for elem in range(dist.shape[0]):
            if dist[elem] <= limit:
                inside += 1
        return inside/dist.shape[0]


import scipy.integrate as integrate
class BiasVectorModel():
    def __init__(self):
        self._grid = {"x_min": -5, "x_max": 5, "binning": 0.5}

    def modelFunction(self, point):
        prefactor = 1.
        mu = 0.
        sigma = 1.
        return lambda x:prefactor*np.exp(-(x-mu-point)**2/(2*sigma**2))

    def biasVectorModel(self):
        for position in np.arange(self._grid["x_min"], self._grid["x_max"]+0.01, self._grid["binning"]):
            result = integrate.quad(self.modelFunction(0), self._grid["x_min"], self._grid["x_max"])[0] - integrate.quad(self.modelFunction(position), self._grid["x_min"], self._grid["x_max"])[0]
            print position, result
