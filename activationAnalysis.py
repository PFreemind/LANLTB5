import argparse
import ROOT as r
import numpy as np
from array import array
import requests
import os
import configparser
import math
import csv
import pulseAnalysis as p


#get number of LYSO pulses in  a run

def getNLYSO(tree):
    nLYSO = 0
    for e in tree:
        coinc = tree.coinc
        if coinc:
            nLYSO+=1
    return float(nLYSO)

def getBGSpecrtrum(tree, name):
    h = r.TH1F(name,";Energy (keV); Counts [a.u.]", 256, 0, 2500)
#    h1 = r.TH1F("h1",";Energy (keV); Counts [a.u.]", 256, 0, 2500)
    for e in t0:
        evt=tree.evt
        tin=tree.tin
        tP=tree.tP
        #  evt = tree.evt2
        amp = tree.amp
        ch = tree.ch
        keV = tree.keV
        coinc = tree.coinc
        area = tree.area
        area1a = tree.area1a
        area1b = tree.area1b
        iPulse = tree.iPulse
        keV = tree.keV
        if coinc == 0 and ch == 1:     #cuts go here
            h.Fill(keV)
    return h
#get runs

if __name__ == "__main__":
    dir = "./pulse_data/"
    file0 =r.TFile.Open(dir+"Run33677_dirpipulses.root","READ")
    t0=file0.Get("pulses")
    file1 =r.TFile.Open(dir+"Run33737_dirpipulses.root","READ")
    t1=file1.Get("pulses")
    #get the number of LYSO counts for scaling:
    scale0 = getNLYSO(t0)
    scale1 = getNLYSO(t1)
    
    #get the background spectra, (cuts on ch, coinc)
    h0  =   getBGSpecrtrum(t0, "h")
    h1  =   getBGSpecrtrum(t1, "h1")
    
    h0.Scale(1.0/scale0)
    h1.Scale(1.0/scale1)
    
    #do some drawing
    can = r.TCanvas()
    leg = r.TLegend()
    h0.Draw()
    leg.AddEntry(h0, "Run33677, Sept 23" )
    h1.SetLineColor(2)
    h1.Draw("same")
    leg.AddEntry(h0, "Run33737, Sept 25" )
    p.savePlots(can, "./","Sept23_25_keV")


#plot spectra scaled to

