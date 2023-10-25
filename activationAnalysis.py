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
    nEvt = 0
    for e in tree:
        coinc = tree.coinc
        ch = tree.ch
        nEvt=tree.evt+1
        if coinc==1 and ch ==1:
            nLYSO+=1
    return float(nLYSO), nEvt

def getBGSpectrum(tree, name):
    h = r.TH1F(name,";Energy (keV); Counts [a.u.]", 600, 0, 4000)
    h2 = r.TH1F(name+"2",";Energy (keV); Counts [a.u.]", 600, 0, 4000)
    ht = r.TH1F(name+"t",";time between events (ms); Counts [a.u.]", 100, 0, 99)
    ht2 = r.TH1F(name+"t2",";time between events (ms); Counts [a.u.]", 100, 0, 99)
    
#    h1 = r.TH1F("h1",";Energy (keV); Counts [a.u.]", 256, 0, 2500)
    for e in tree:
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
        tBetweenEvents = tree.tBetweenEvents
        if coinc == 0:# or coinc == 1:
            if ch == 1:     #cuts go here
                h.Fill(keV)
            if ch == 2:
                h2.Fill(keV * 8.0)
        #if coinc == 1:
        if ch == 1 and iPulse == 0 and coinc == 0:     #cuts go here #iPulse cut to only count one time per event window (instead of counting for every pulse)
            ht.Fill(tBetweenEvents)
        if ch == 2  and iPulse == 0:
            ht2.Fill(tBetweenEvents)
    return h, ht, h2, ht2
#get runs

def getBeamRate( run = "Run33677", memDepth=4096):
#tell me rate of beam pulses for a given run
    dir = "./pulse_data/"
    file =r.TFile.Open(dir+run,"READ")
    t=file.Get("pulses")
    counts = 0
    if memDepth < 4096:
        return 0
    else:
        end = memDepth - 500
        begin = 38000
    
    for e in t:
        evt=t.evt
        tP=t.tP
        #  evt = t.evt2
        amp = t.amp
        ch = t.ch
        keV = t.keV
        coinc = t.coinc
        area = t.area
        iPulse = t.iPulse
        if tP > begin and tP < end and iPulse>0 and ch ==1:
            counts+=1
    time = evt * 25e-9 * (end-begin)
    rate = counts/time
    return rate
    
if __name__ == "__main__":
    #r.gROOT.SetBatch(True)
    dir = "./pulse_data/"
    file0 =r.TFile.Open(dir+"Run33677_dirpipulses.root","READ")
    t0=file0.Get("pulses")
    file1 =r.TFile.Open(dir+"Run33737_dirpipulses.root","READ")
    t1=file1.Get("pulses")
    #get the number of LYSO counts for scaling:
    scale0, foo = getNLYSO(t0)
    print("The scale factor for Run33677 is: ", scale0)
    scale1, foo = getNLYSO(t1)
    print("The scale factor for Run33737 is: ", scale1)
    runs = [
    "Run33677_dirpipulses.root",
    "Run33682_dirpipulses.root",
    "Run33687_dirpipulses.root",
    "Run33692_dirpipulses.root",
    "Run33697_dirpipulses.root",
    "Run33702_dirpipulses.root",
    "Run33707_dirpipulses.root",
    "Run33712_dirpipulses.root",
    "Run33717_dirpipulses.root",
    "Run33722_dirpipulses.root",
    "Run33727_dirpipulses.root",
    "Run33732_dirpipulses.root",
    "Run33737_dirpipulses.root",
 #   "Run33344_dirpipulses.root",
 #   "Run33347_dirpipulses.root",
 #   "Run33857_dirpipulses.root",
  #  "Run33871_dirpipulses.root",
    ]
    
    times = []
    scales = []
    nEvts = []
    errx = []
    errt = []
    erry = []
    hs = r.THStack("hs","")
    i =0
    offset = 47.333333
    can = r.TCanvas()
    can.SetLogy(1)
    r.gStyle.SetOptFit(1)
    f1 = r.TF1("f1","expo", 20, 50)
    taus = []
    taus2 = []
    tausC = []
    tauErrs = []
    tauErrsC = []
        #in addition to taus and scales, we can get a direct measurement of the rate with pulse counting
    rates = []
    
    for run in runs:
        print("looping")
        times.append(offset + 2.0 + 4.0 * i)
        file =r.TFile.Open(dir+run,"READ")
        t=file.Get("pulses")
        if i ==0:
            template = t
        n, nEvt = getNLYSO(t)
       # print("the normalization factor is:")
        nLYSOErr = pow(n, 0.5)
        errx.append(0.0001)
        erry.append(nLYSOErr)#1.0/pow(n,0.5))
        errt.append(0.)#1.0/pow(n,0.5))
        scales.append(1.0/n)
        nEvts.append(nEvt)
        h, ht, h2, ht2 = getBGSpectrum(t, "h"+str(i))
        h.Scale(1.0/n)
        h2.Scale(1.0/n)
    #    scale = p.getLYSOCal(template, t)
        leg = r.TLegend()
        scale = 1
        h.SetTitle("t ="+str(int(times[i]))+" hrs, LYSO cal = "+str(scale)+";Energy (keV); Counts [a.u.]")
        h.SetMaximum(1)
        h.SetMinimum(1e-5)
        h.Draw()
        leg.AddEntry(h, "NaI")
        h2.SetLineColor(2)
        
        h2.SetMaximum(1)
        h2.SetMinimum(1e-5)
        h2.Draw("same")
        leg.AddEntry(h2, "LYSO")
        leg.Draw()
        p.savePlots(can, "./", "decay_gifs_"+str(int(times[i])).zfill(4) )
        ht.SetMaximum(1e5)
        ht.SetMinimum(0.5)
        ht.Draw()
       # ht2.SetLineColor(2)
      #  ht2.Draw("same")
        ht.Fit("f1","R")
        tau = -1.0/ (f1.GetParameter(1) + 1e-9)
        tauErr = (f1.GetParError(1) )
        tauErrs.append(tauErr)
        taus.append(tau)
     #   tau += 1000 * 25e-9 * 1000 #correction to include acquisition window #actually, you don't want this
        tau *= nEvt
        tausC.append(tau)
        tauErr *= nEvt
        tauErrsC.append(tauErr)
        rates.append( getBeamRate( run , 65536) )
       # ht2.Fit("f1","R")
       # tau2 = -1.0/ (f1.GetParameter(1))
       # taus2.append(tau2)
  #      scale = p.getLYSOCal(template, t)
        
        p.savePlots(can, "./", "decay_timeBetween_"+str(int(times[i])).zfill(4))
        
        hs.Add(  h )
        i+=1
        
    print("loop finished")
    #[5.473939302289152, 5.848022149352433, 6.255403284859799, 6.779214655278007, 7.117872952411881, 7.436453168346582, 7.764800641956702, 8.1172037565354, 8.324471001179337, 8.641901384313158, 8.840880903006541, 9.144335511186412, 9.350988676919194]
    #hs.Draw()
   # p.savePlots(can, "./", "decay_gifs")
    can = r.TCanvas()
    r.gStyle.SetOptFit(1)
    can.SetLogy(1)
    g = r.TGraphErrors(i, np.array(times), np.array(scales), np.array(errx), np.array(erry) )
    g.SetTitle("Normalization factors;Time after beam run [hr]; Normalization factor")
    g.SetMinimum(8e-6)
    g.SetMaximum(3e-5)
    g.Draw("ALP")
    f4 =  r.TF1("f4","expo", 0, 100 )
    g.Fit("f4")
    p.savePlots(can, "./", "scaleFactors")
    
    gT = r.TGraphErrors(i, np.array(tausC), np.array( np.reciprocal(scales) ), np.array(tauErrsC), np.array(erry) )
    can.SetLogy(0)
    gT.SetMarkerStyle(1)
    gT.SetTitle("Normalization factor comparison;#tau [ms]; Normalization factor from nLYSO")
   # gT.SetMinimum(0)
    #gT.SetMaximum(3e-5)
    gT.Draw("ALP")
    f5 =  r.TF1("f5","x*[0]", 0, 100 )
    gT.Fit("f5")
    p.savePlots(can, "./", "nLYSOvsTau")

    #get the background spectra, (cuts on ch, coinc)
    h0,h0t  =   getBGSpectrum(t0, "h")[0:2]
    h1,h1t  =   getBGSpectrum(t1, "h1")[0:2]
 #   ht0 = getTau(t0)
    
    h0.Scale(1.0/scale0)
    h1.Scale(1.0/scale1)
    
    #do some drawing
    can = r.TCanvas()
    can.SetLogy(1)
    leg = r.TLegend(0.15, 0.2, 0.4, 0.4)
    h0.Draw()
    leg.AddEntry(h0, "Run33677, Sept 23" )
    h1.SetMarkerColor(2)
    h1.SetLineColor(2)
    h1.Draw("same")
    leg.AddEntry(h1, "Run33737, Sept 25" )
    leg.Draw()
    #fitting of main peak in initial after-beam spectrum
    f0 = r.TF1("f0","gaus(0)+expo(3)", 350, 600 )
    f0.SetParLimits(0,0.01, 0.1)
    f0.SetParLimits(1,460, 500)
    f0.SetParLimits(2,10, 100)
    f0.SetRange(350, 550)
    f0.SetLineColor(r.kBlue)
    h0.Fit("f0", "R")
    #double peak fitting with single gaussian
    f1 = r.TF1("f1","gaus(0)+expo(3)", 350, 600 )
    f1.SetParLimits(0,0.001, 0.01)
    f1.SetParLimits(1,460, 500)
    f1.SetParLimits(2,10, 100)
    f1.SetRange(350, 700)
    h1.Fit("f1", "R")
 # double peak fitting
    f2 = r.TF1("f2","gaus(0)+expo(3)+gaus(5)", 350, 600 )
    f2.SetParLimits(0,0.001, 0.01)
    f2.SetParLimits(1,460, 485)
    f2.SetParLimits(2,10, 100)
    f2.SetParLimits(5,0.001, 0.01)
    f2.SetParLimits(6,485, 510)
    f2.SetParLimits(7,10, 100)
    f2.SetRange(350, 550)
    h1.Fit("f2", "R")
    
    f3 = r.TF1("f3","gaus(0)", 55, 75 )
    f3.SetLineColor(r.kBlue)
    h0.Fit("f3","R")
    f3.SetRange(90, 110)
    h0.Fit("f3","R")
    
    f3.SetRange(55, 75)
    f3.SetLineColor(2)
    h1.Fit("f3","R")
    f3.SetRange(90, 110)
    h1.Fit("f3","R")
    
    p.savePlots(can, "./","Sept23_25_keV")
    
    import subprocess
    params = ['convert', 'decay_gifs*png', 'decaySept23_25.gif']
    subprocess.check_call(params)
    params = ['convert', 'decay_timeBetween_*png', 'tBetweenSept23_25.gif']
    subprocess.check_call(params)



#plot spectra scaled to

