# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 15:23:41 2021

@author: David
"""

from os import path
from ROOT import TCanvas, TFile, TPaveText
from ROOT import gROOT, gBenchmark
import numpy as np
import cPickle as pickle

 
c1 = TCanvas( 'c1', 'The Fit Canvas', 200, 10, 700, 500 )
c1.SetGridx()
c1.SetGridy()
c1.GetFrame().SetFillColor( 21 )
c1.GetFrame().SetBorderMode(-1 )
c1.GetFrame().SetBorderSize( 5 )

 
gBenchmark.Start( 'fit1' )
#
# We connect the ROOT file generated in a previous tutorial
#
fill = TFile( 'py-fillrandom.root' )
 
#
# The function "ls()" lists the directory contents of this file
#
fill.ls()
 
#
# Get object "sqroot" from the file.
#
 
sqroot = gROOT.FindObject( 'sqroot' )
sqroot.Print()
 
#
# Now fit histogram h1f with the function sqroot
#
h1f = gROOT.FindObject( 'h1f' )
h1f.SetFillColor( 45 )
h1f.Fit( 'gaus' )

fit = h1f.GetFunction('gaus')
std = h1f.GetStdDev()

print("std ", std)
FWHM = 2*np.sqrt(2*np.log(2))*std
print("stdF ",FWHM)
#https://root.cern.ch/doc/master/classTH1.html to know about the use of getstddev
#https://root.cern.ch/root/htmldoc/guides/users-guide/Histograms.html#important-note-on-returned-statistics-getmean-getstddev-etc. example where it coulb be problematic (it does not affect us in principle, only with range)

"""
why is it better to use std from histogram and not from fitting:
    https://math.stackexchange.com/questions/753933/stdev-and-mean-from-gaussian-fit-vs-from-classical-formula
"""

sigma = fit.GetParameter(2)
print("sigma ",sigma)
 
# We now annotate the picture by creating a PaveText object
# and displaying the list of commands in this macro
#


fitlabel = TPaveText( 0.6, 0.3, 0.9, 0.80, 'NDC' )
fitlabel.SetTextAlign( 12 )
fitlabel.SetFillColor( 42 )
fitlabel.ReadFile(path.join(str(gROOT.GetTutorialDir()), 'pyroot', 'fit1_py.py'))
fitlabel.Draw()
c1.Update()
gBenchmark.Show( 'fit1' )

myfile = TFile( 'py-fitrandom.root', 'CREATE' )
h1f.Write()
myfile.Close()

sFWHM = 2*np.sqrt(2*np.log(2))*sigma
print("sF ",sFWHM)

"""
https://root.cern.ch/doc/master/classTF1.html

Return the number of degrees of freedom in the fit the fNDF parameter has been previously computed during a fit.

The number of degrees of freedom corresponds to the number of points used in the fit minus the number of free parameters. 
"""


raw_input("Press enter to continue. ")