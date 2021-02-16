# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 14:58:33 2021
@author: David
"""
from ROOT import TCanvas, TPad, TFormula, TF1, TPaveLabel, TH1F, TFile, TLegend
from ROOT import gROOT, gBenchmark
from ROOT import kBlack, kBlue, kRed
import numpy as np
import cPickle as pickle
import h5py

c1 = TCanvas( 'c1', 'Fill example', 200, 10, 900, 900 )
"""
[in]	name	canvas name
[in]	title	canvas title
[in]	wtopx,wtopy	are the pixel coordinates of the top left corner of the canvas (if wtopx < 0) the menubar is not shown)
[in]	ww	is the canvas size in pixels along X
[in]	wh	is the canvas size in pixels along Y
"""
pad2 = TPad( 'pad2', 'The pad with the histogram', 0.05, 0.05, 0.95, 0.95, 0 )
"""
[in]	name	pad name
[in]	title	pad title
[in]	xlow	[0,1] is the position of the bottom left point of the pad expressed in the mother pad reference system
[in]	ylow	[0,1] is the Y position of this point.
[in]	xup	[0,1] is the x position of the top right point of the pad expressed in the mother pad reference system
[in]	yup	[0,1] is the Y position of this point.
[in]	color	pad color
[in]	bordersize	border size in pixels
[in]	bordermode	border mode

    bordermode = -1 box looks as it is behind the screen
    bordermode = 0 no special effects
    bordermode = 1 box looks as it is in front of the screen
"""
pad2.Draw()
gBenchmark.Start( 'fillTest' )
#
# A function (any dimension) or a formula may reference
# an already defined formula
#
#form1 = TFormula( 'form1', 'abs(sin(x)/x)' )
#sqroot = TF1( 'sqroot', 'x*gaus(0) + [3]*form1', 0, 10 ) #numbers are only for the limit of the function
#sqroot.SetParameters( 10, 4, 1, 20 ) #here the different params are defined, in ths case the first three are for Gaus and the fourth one [3] is for the formula we have defined
#pad1.SetGridx()
#pad1.SetGridy()
#pad1.GetFrame().SetFillColor( 0 )
#pad1.GetFrame().SetBorderMode( -1 )
#pad1.GetFrame().SetBorderSize( 5 )
#sqroot.SetLineColor( 4 )
#sqroot.SetLineWidth( 6 )
#sqroot.Draw()
#lfunction = TPaveLabel( 5, 39, 9.8, 46, 'The sqroot function' )
#lfunction.SetFillColor( 0 )
#lfunction.Draw()
#c1.Update()
#
# Create a one dimensional histogram (one float per bin)
# and fill it following the distribution in function sqroot.
#
pad2.cd()
pad2.GetFrame().SetFillColor( 0 )
pad2.GetFrame().SetBorderMode( -1 )
pad2.GetFrame().SetBorderSize( 5 )

h1f = TH1F( 'h1f', 'Test PV', (5000-500)/45, 500, 5000)
h1f.SetLineColor(kBlue)
"""
TH1F::TH1F 	( 	const char *  	name,
		const char *  	title,
		Int_t  	nbinsx,
		Double_t  	xlow,
		Double_t  	xup 
	) 	
"""
#h1f.SetFillColor( 45 ) #color from the inner side of the histogram

with open('datapv-ALL-valid.pickle', "rb") as handle:
    datapv = pickle.load(handle)  # 000, 100, 010, 111

i_crystal = 1500
for x in datapv[i_crystal]['pv']:
    h1f.Fill(x)

h1f.Draw()

leg = TLegend() # TLegend(x1,y1,x2,y2) where x,y are in units of percentage of canvas (i.e. x,y \in [0,1])
leg.SetBorderSize(0) # no border
leg.SetFillColor(0) # probably kWhite
leg.SetFillStyle(0) # I'm guessing this just means pure color, no patterns
leg.SetTextFont(42)
leg.SetTextSize(0.035) # somewhat large, may need to play with this to make the plot look ok
leg.AddEntry(h1f,"{}".format(i_crystal),"L") # AddEntry(TGraph/TH1D varName, what you want the legend to say for this graph, show the line)

leg.Draw() # draw it!

c1.Update()
#
# Open a ROOT file and save the histogram
#
#myfile = TFile( 'SingleCrystalPV.root', 'RECREATE' )
# form1.Write()
# sqroot.Write()
#h1f.Write()
#myfile.Close()
gBenchmark.Show( 'fillTest' )

"""
There is a discrepancy between root fit and python fit. In fact,
 root fit default uses mode “I” [Use integral of function in bin, normalized by the bin volume,
 instead of value at bin center] and python fit uses mode “W” [Ignore the bin uncertainties
 when fitting using the default least square (chi2) method but skip empty bins]. I got 
 the same fitting result now by switching root fit option to “RQW”.
"""
raw_input("Press Enter to be able to analyze further crystals.")

while i_crystal != "exit":
    i_crystal = raw_input("Enter id of crystal to be plotted or type 'exit' to quit: ")
    if i_crystal == "exit":
        continue
    else:
        i_crystal = int(i_crystal)
    print("{} will be plotted.".format(i_crystal))
    print("The corresponding layer is: ", datapv[i_crystal]["layer"])
    print("The corresponding row is: ", datapv[i_crystal]["row"])
    c1 = TCanvas('c1', 'Fill example', 200, 10, 900, 900)

    pad2 = TPad('pad2', 'The pad with the histogram', 0.05, 0.05, 0.95, 0.95, 0)

    pad2.Draw()
    gBenchmark.Start('fillTest')

    pad2.cd()
    pad2.GetFrame().SetFillColor(0)
    pad2.GetFrame().SetBorderMode(-1)
    pad2.GetFrame().SetBorderSize(5)

    h1f = TH1F('h1f', 'Test PV', (5000 - 500) / 45, 500, 5000)
    h1f.SetLineColor(kBlue)

    for x in datapv[i_crystal]['pv']:
        h1f.Fill(x)

    h1f.Draw()

    leg = TLegend() # TLegend(x1,y1,x2,y2) where x,y are in units of percentage of canvas (i.e. x,y \in [0,1])
    leg.SetBorderSize(0) # no border
    leg.SetFillColor(0) # probably kWhite
    leg.SetFillStyle(0) # I'm guessing this just means pure color, no patterns
    leg.SetTextFont(42)
    leg.SetTextSize(0.035) # somewhat large, may need to play with this to make the plot look ok
    leg.AddEntry(h1f,"{}".format(i_crystal),"L") # AddEntry(TGraph/TH1D varName, what you want the legend to say for this graph, show the line)

    leg.Draw() # draw it!

    c1.Update()