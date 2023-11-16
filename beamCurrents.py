import argparse
import ROOT as r
import numpy as np
from array import array
import requests
import os
import math
import csv
import pulseAnalysis as p
import copy
r.gStyle.SetOptFit(0)
    
def plotSigmaCurves(parts, run): #to be run on the pulseCounting.root file produced by beamCurrents.py, see beamCurrentJobs.py for implementation
    cuts = [
        "no cuts",
        "largeEarlyPulse veto",
        "energy cut, E > 1500 keV",
        "veto and cut",
        "LYSO, none",
        "LYSO, largeEarlyPulses",
        "E < 500 keV",
        "E > 500 keV && E < 1500 keV"
    ]
    nCuts = len(cuts)

    suffixes = [
    "",
    "BG",
    "E",
    "EBG"
    ]#symbols

    sigmaGraphs = []
    poissonGraphs = []

    sigmaGraphsE = []
    sigmaFits = []
    poissonGraphsE = []
    poissonFits = []
    #compare 2 graphs per cut that should go as the sqrt(N) and be equal
    #do for N, THEN energy
    #then add background subtracted runs
    #make these all gifs so you can go through and explain them in slides 1-by-1
    can = r.TCanvas()
    canE = r.TCanvas()
    can.SetLogy(1)
    canE.SetLogy(1)
    iPart = 0
    for i in range(nCuts): #colors
        sigmaGraphs.append(copy.deepcopy( r.TGraphErrors()) )
        sigmaGraphsE.append(copy.deepcopy( r.TGraphErrors()) )
        sigmaFits.append(r.TF1("fS"+str(i),"TMath::Sqrt( [1]*x ) + [0]", 0, 200))
        sigmaFits[i].SetParLimits(1,0.1, 20)
        sigmaFits[i].SetLineWidth(1)
        poissonGraphs.append(copy.deepcopy( r.TGraphErrors()) )
        poissonGraphsE.append(copy.deepcopy( r.TGraphErrors()) )
        poissonFits.append(r.TF1("fP"+str(i),"TMath::Sqrt( [1]*x ) + [0]", 0, 200))
        poissonFits[i].SetParLimits(1,0.1, 20)
        if str(run)=="33362":
            sigmaFits[i].SetParLimits(1, 1e2, 2e6)
            sigmaFits[i].SetParameter(0, 3250)
            sigmaFits[i].SetParameter(1, 384050)
            poissonFits[i].SetParLimits(1, 1e2, 2e6)
            poissonFits[i].SetParLimits(0, -10, 100)
            poissonFits[i].SetParameter(0, 0)
            poissonFits[i].SetParameter(1, 164600)
            poissonFits[i].SetLineWidth(1)
        iPart = 0
        for part in parts: # points
            filename = "pulseCountingRun"+str(run)+"_n"+str(part)+".root"
            f = r.TFile.Open("./"+filename,"READ")
            t = f.Get("rates")
      #      g = f.Get("g"+suffix(i)+str(i))
           
            if str(run) == "33362":
                hSignal = r.TH1F("hSignal", "", 100, 0, 1e5)
                hPoisson = r.TH1F("hPoisson","", 100, 0, 1e4 )
                hEnergy = r.TH1F("hEnergy", "", 800, 0, 4e5)
                hPoissonE = r.TH1F("hPoissonE", "", 800, 0, 4e5)
            else:
                hSignal = r.TH1F("hSignal", "", 100, 0, 1000)
                hPoisson = r.TH1F("hPoisson","", 100, 0, 1000 )
                hEnergy = r.TH1F("hEnergy", "", 800, 0, 4000)
                hPoissonE = r.TH1F("hPoissonE", "", 800, 0, 4000)
            for e in t:
                signalRate = t.signalRate[i]
                energyRate = t.energyRate[i]
                poissonErr = t.poissonErr[i]
                poissonErrE = t.poissonErrE[i]
                signal_BGRate = t.signal_BGRate[i]
                poissonErrBGRate = t.signal_BGRate[i]
                hSignal.Fill(signalRate)
                hPoisson.Fill(poissonErr)
                hEnergy.Fill(energyRate)
                hPoissonE.Fill(poissonErrE)
            sigmaGraphs[i].AddPoint(part,  hSignal.GetStdDev() )
            sigmaGraphs[i].SetPointError(iPart,  0.0, hSignal.GetRMSError() )
            sigmaGraphsE[i].AddPoint(part,  hEnergy.GetRMS() )
            sigmaGraphsE[i].SetPointError(iPart,  0.0, hEnergy.GetRMSError() )


            poissonGraphs[i].AddPoint(part, hPoisson.GetMean() )
            poissonGraphs[i].SetPointError(iPart, 0.0, hPoisson.GetMeanError() )
            poissonGraphsE[i].AddPoint(part, hPoissonE.GetMean() )
            poissonGraphsE[i].SetPointError(iPart, 0.0, hPoissonE.GetMeanError() )
            iPart += 1
        sigmaGraphs[i].SetMarkerColor(p.colors[i])
        sigmaGraphs[i].SetLineColor(p.colors[i])

        sigmaGraphs[i].SetMarkerStyle(41)
        poissonGraphs[i].SetMarkerColor(p.colors[i])
        poissonGraphs[i].SetLineColor(p.colors[i])
        poissonGraphs[i].SetMarkerStyle(40)
        poissonGraphs[i].SetLineStyle(8)
        sigmaFits[i].SetLineColor(p.colors[i])
        poissonFits[i].SetLineColor(p.colors[i])
        poissonFits[i].SetLineStyle(8)
       
        #if i ==0:
        sigmaGraphs[i].SetTitle("Comparison of Sample Std Dev to Poisson Errors;Number of partitions of run;Estimated Error [Hz];")
        can.cd()
        sigmaGraphs[i].SetMinimum(0.1)#0.1)
        sigmaGraphs[i].SetMaximum(40)#40
        if str(run) == "33362":
            sigmaGraphs[i].SetMinimum(1)#0.1)
            sigmaGraphs[i].SetMaximum(3e4)#40)
        sigmaGraphs[i].Draw("AP")
        #else:
        #   sigmaGraphs[i].Draw("same&&P")
        sigmaGraphs[i].Fit("fS"+str(i), "R" )
        poissonGraphs[i].Draw("P&&same")
        poissonGraphs[i].Fit("fP"+str(i),"R")
        leg = r.TLegend(0.3, 0.15,  0.85, 0.55)
        leg.AddEntry(sigmaGraphs[i], "#sigma ( #mu ( rate ))        "+cuts[i]+" #chi^{2}/NDF ="+str(sigmaFits[i].GetChisquare())[0:5]+" / "+str(sigmaFits[i].GetNDF()) )
        leg.AddEntry(poissonGraphs[i], "#mu ( #sigma_{Poisson} ( rate )) "+cuts[i]+" #chi^{2}/NDF ="+str(poissonFits[i].GetChisquare())[0:5]+" / "+str(poissonFits[i].GetNDF()) )
        leg.Draw()
        p.savePlots(can, "./plots/Run"+run+"/", "Run"+str(run)+"systematicsCheck_cut" + str(i) )
        
        sigmaGraphsE[i].SetTitle("Comparison of Sample Std Dev to Poisson Errors;Number of partitions of run;Estimated Error [Hz];")
        sigmaGraphsE[i].SetMinimum(0.1)#0.1)
        sigmaGraphsE[i].SetMaximum(100)#40)
        canE.cd()
        if str(run) == "33362":
            sigmaGraphsE[i].SetMinimum(1)#0.1)
            sigmaGraphsE[i].SetMaximum(3e4)#40)
        sigmaGraphsE[i].Draw("AP")
        #else:
        #   sigmaGraphsE[i].Draw("same&&P")
        sigmaGraphsE[i].Fit("fS"+str(i), "R" )
        poissonGraphsE[i].Draw("P&&same")
        poissonGraphsE[i].Fit("fP"+str(i),"R")
        leg = r.TLegend(0.3, 0.15,  0.85, 0.55)
        leg.AddEntry(sigmaGraphs[i], "#sigma ( #mu ( rate ))        "+cuts[i]+" #chi^{2}/NDF ="+str(sigmaFits[i].GetChisquare())[0:5]+" / "+str(sigmaFits[i].GetNDF()) )
        leg.AddEntry(poissonGraphsE[i], "#mu ( #sigma_{Poisson} ( rate )) "+cuts[i]+" #chi^{2}/NDF ="+str(poissonFits[i].GetChisquare())[0:5]+" / "+str(poissonFits[i].GetNDF()) )
        leg.Draw()
        p.savePlots(can, "./plots/Run"+run+"/", "Run"+str(run)+"systematicsCheckE_cut" + str(i) )
        i+=1
         #   if suffix == "" or suffix == "E"
          #      sigmaGraphs[i].SetPointError(index?, 0, g.Get)
           # if suffix == "BG" or suffix == "EBG"
           #     sigmaGraphs[i].append( g.GetRMS(2) )
                    
                #std dev  == mean (poissonErrs)?
                
                #plot the std dev and mean of poisson errors as a fcn of n
                # fit to sqrt(N)

def getNbeam(start=0, stop=1000, run = "Run33362", energyCut=1500, current=1.0, memDepth=4096):
    dir = "./pulse_data/"
    file =r.TFile.Open(dir+run+"_dirpipulses.root","READ")
    t=file.Get("pulses")
    h = r.TH1F("h",";Pulse energy (keV); Counts", 256, 0, 4000)
    hE = r.TH1F("hE",";Pulse energy (keV); Counts", 256, 0, 4000)
    hPE = r.TH1F("hPE",";Pulse energy (keV); Counts", 256, 0, 4000)
    hP = r.TH1F("hP",";Pulse energy (keV); Counts", 256, 0, 4000)
    hT = r.TH1F("hT",";Pulse time (s); Counts", 3000, 0, 10800)
    hTE = r.TH1F("hTE",";Pulse time (s); Counts", 256, 3000, 18000)
    hTP = r.TH1F("hTP",";Pulse time (s); Counts", 256, 3000, 18000)

    h2 = r.TH1F("h2",";Pulse energy (keV); Counts", 256, 0, 4000)
    hP2 = r.TH1F("hP2",";Pulse energy (keV); Counts", 256, 0, 4000)
    hT2 = r.TH1F("hT2",";Pulse time (s); Counts", 256, 3000, 18000)
    hTP2 = r.TH1F("hTP2",";Pulse time (s); Counts", 256, 3000, 18000)
    
    hElo = r.TH1F("hElo",";Pulse energy (keV); Counts", 256, 0, 4000)
    hEmid = r.TH1F("hEmid",";Pulse energy (keV); Counts", 256, 0, 4000)

    hTElo = r.TH1F("hTElo",";Pulse time (s); Counts", 256, 3000, 18000)
    hTEmid = r.TH1F("hTEmid",";Pulse time (s); Counts", 256, 3000, 18000)
    cuts = "evt>=start and evt <= stop and tP > 500 and tP < 3500 and iPulse>0"
    if memDepth == 65536:
        #only keep triggers between 36 - 38k
        end = memDepth - 500
        begin = 38000
    else:
        begin = 500
        end = 3500
        #     and ( (tP >begin and tP < end) )
    evts = []
    nEvt = 0
    evts2 = []
    nEvt2 = 0
    for e in t:
        evt=t.evt
        tin=t.tin
        tP=t.tP
        #  evt = t.evt2
        amp = t.amp
        ch = t.ch
        keV = t.keV
        coinc = t.coinc
        area = t.area
        area1a = t.area1a
        area1b = t.area1b
        area2a = t.area2a
        area2b = t.area2b
        iPulse = t.iPulse
        if evt>stop:
            break
        if evt>=start and evt <= stop and tP > begin and tP < end and iPulse>0:
           # print (keV)
            if ch == 1:
                h.Fill(keV) #fill the histogram for no cuts
                hT.Fill(tin)

                if area1a < 3000 and area1b < 3000:
                    hP.Fill(keV)  #fill the histogram for a veto on large early pulses
                    hTP.Fill(tin)
                else:
                    if evt not in evts:
                        evts.append(evt)
                        nEvt+=1 #count the number of events excluded by the veto
                if keV> float(energyCut):
                    hE.Fill(keV)  # fill the histogram for the energy cut
                    hTE.Fill(tin)
                    if area1a < 3000 and area1b < 3000:
                        hPE.Fill(keV)# fill the histogram for the energy cut and large pulse veto
                elif keV <= float(energyCut) and keV >500:
                    hEmid.Fill(keV)
                    hTEmid.Fill(tin)
                elif keV < 500:
                    hElo.Fill(keV)
                    hTElo.Fill(tin)
                    
            if ch == 2:
                h2.Fill(keV)
                hT2.Fill(tin)
                if area2a < 3000 and area2b < 3000:
                    hP2.Fill(keV)  #fill the histogram for a veto on large early pulses
                    hTP2.Fill(tin)
                else:
                    if evt not in evts2:
                        evts2.append(evt)
                        nEvt2+=1 #count the number of events excluded by the veto

    can = r.TCanvas()
    h.Draw()
    h2.SetLineColor(2)
    h2.Draw("same")
   # p.savePlots(can, "./plots/"+run, "pulseCount_evt_"+str(stop))
    
    leg = r.TLegend()
    can = r.TCanvas()
  #  can.SetLogy(1)
  #  hT.SetMinimum(0.1)
    leg.AddEntry(hT)
#    hT.Draw()
    hTE.SetLineColor(r.kGreen+2)
    leg.AddEntry(hTE,str(energyCut)+" keV cut")
    hTE.Draw("same")
    hTP.SetLineColor(r.kRed+1)
    leg.AddEntry(hTE,"Large pulse veto")
    leg.AddEntry(hT)
    hTP.Draw("same")
    leg.Draw
 #   p.savePlots(can, "./plots/"+run, "pulseTime_evt_"+str(stop))
    #tell me how many pulses there were
    nPulses = h.GetEntries()
  #  print("oh boy there are a bunch of pulses: ",nPulses )
#    input("")
    
    #write things to .txt/csv
    # field names
    tin = hT.GetMean()
    fields = ["cut","start", "stop", "counts", "nEvts", "current (nA)", "totalEnergy (keV)"]
        # data rows of csv file

    rows = [ ["none", start, stop, h.GetEntries(), stop-start+1 , h.Integral(), h.GetRMS(), tin, hT.GetRMS()],
        ["largeEarlyPulses", start, stop, hP.GetEntries(), stop-start+1 - nEvt, hP.Integral(), hP.GetRMS(), tin, hT.GetRMS() ],
        ["energy", start, stop, hE.GetEntries(), stop-start+1 , hE.Integral(), hE.GetRMS(), tin, hT.GetRMS()],
        ["both", start, stop, hPE.GetEntries(), stop-start+1 - nEvt , hPE.Integral(), hPE.GetRMS(), tin, hT.GetRMS() ],
        ["LYSOnone", start, stop, h2.GetEntries(), stop-start+1 , h2.Integral(), h2.GetRMS(), tin, hT.GetRMS()],
        ["LYSOlargeEarlyPulses", start, stop, hP2.GetEntries(), stop-start+1 - nEvt2, hP2.Integral(), hP2.GetRMS(), tin, hT.GetRMS() ],
        ["energyLo", start, stop, hElo.GetEntries(), stop-start+1 , hElo.Integral(), hElo.GetRMS(), tin, hT.GetRMS()],
        ["energyMid", start, stop, hEmid.GetEntries(), stop-start+1 , hEmid.Integral(), hEmid.GetRMS(), tin, hT.GetRMS()],
    ]


    # name of csv file
    '''
    filename = "beamCounting_evt_"+str(stop)+".csv"
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
            
        # writing the fields
        csvwriter.writerow(fields)
            
        # writing the data rows
        csvwriter.writerows(rows)
    '''
    
 #   print(fields)
#    for row in rows:
  #      print(row)
    return rows
    
def getRate(before, during, after, current, nSamples):
    signalCounts = []
    bgCounts = []
    signal_BGCounts = []
    signalRate = []
    signalEnergy = []
    BGenergy = []
    poissonErr = []
    signal_BGRate = []
    poissonErrBG = []
    time = []
    tin = []
    start = []
    stop = []
    energyRate = []
    energyBGRate = []
    poissonErrE = []
    poissonErrEBG = []
    energyBG = []
    tinErr = []
    i = 0
    for row in before:
        nEvt = during[i][4]
        counts = during[i][3] + 1e-9
        nEvtAfter = after[i][4]
        countsBefore = before[i][3] + 1e-9
        energyBefore = before[i][5]
        countsAfter = after[i][3] + 1e-9
        energyAfter = before[i][5]
        nEvtBefore = before[i][4]
        timeInRun = during[i][7]
        timeInRunErr = before[i][8]
        start.append( during[i][1] )
        stop.append(during[i][2])
        stopBefore = before[i][2]
        startAfter =  after[i][1]
        errBefore = before[i][6]/pow(countsBefore, 0.5)
        errDuring = during[i][6]/pow(counts, 0.5)
        errAfter = after[i][6]/pow(countsAfter, 0.5)
        tin.append(timeInRun)
        tinErr.append(timeInRunErr)
        signalEnergy.append(during[i][5])
        time.append( nSamples * 25.0e-9 * nEvt)
        signalRate.append(counts/time[i])
        poissonErr.append(pow(counts,0.5)/time[i])
        energyRate.append(signalEnergy[i]/time[i])
        poissonErrE.append(poissonErr[i]*signalEnergy[i])
        signalCounts.append(counts)
        nAfter = after[i]
        midpoint = (start[i]+stop[i])/2.
        relativePosition =  (midpoint - stopBefore)/(startAfter - stopBefore) # for linearly varying background
        bg = (countsAfter *  nEvt/nEvtAfter * (relativePosition) + countsBefore * nEvt/nEvtBefore * (1. - relativePosition) )
        bgE =(energyAfter *  nEvt/nEvtAfter + energyBefore * nEvt/nEvtBefore) * 0.5
        signal_BGCounts.append(signalCounts[i]-bg)
        signal_BGRate.append((signal_BGCounts[i])/time[i])
        poissonErrBG.append(pow(abs(signal_BGCounts[i]), 0.5)/time[i])
        energyBG.append(signalEnergy[i]-bgE)
        energyBGRate.append((signalEnergy[i]-bgE)/time[i])
        poissonErrEBG.append(pow( errBefore*errBefore + errDuring*errDuring + errAfter*errAfter, 0.5)/time[i])
        bgCounts.append(bg)
        i+=1
  #  print(signalRate)
    ret = [ start, stop, signalRate, poissonErr,  signal_BGRate, poissonErrBG, time, current, signalCounts, signal_BGCounts, bgCounts, signalEnergy, energyRate,poissonErrE, energyBGRate, poissonErrEBG, tin, tinErr ]
   # print(ret)
    return ret

def getHist(g): #gets a histogram from a tgrapherrors
#use histograms instead of graphs
    # get first and last x-values to set histogram limits
    n = g.GetN()
    xLow = g.GetPointX(0)
    xHigh = g.GetPointX(n-1)
    # create histograms, making sure that the overlapping times match
    hG = r.TH1F("hFromTGraph", "", n, xLow, xHigh)
    for i in range(n):
        hG.SetBinContent(i, g.GetPointY(i))
       # print(g.GetPointY(i))
       #print("bin content ", h.GetBinContent(i))
        hG.SetBinError(i, g.GetErrorY(i))
    return hG
    #
#then you can use chi2test for comparison
#

def getScale(h1, h2, min =0.3 , max =0.5, nSteps = 100):
    for i in range(nSteps):
         scale = (0.3 * pow( 0.5/0.3 , float(i)/float(nSteps) ) )
         htmp = r.TH1F("htmp","", h1.GetNBins(), h1.GetXaxis().GetXmin(), h1.GetXaxis().GetXmax() )
         print("test scale: ", scale)
         h2.Scale(scale)
         #rebin h2 to match h1
         chi2 = h1.Chi2Test(h2, "W")
         if i ==0 :
            minChi2 = chi2
            mindex = i
         if chi2 < minChi2:
            minChi2 = chi2
            mindex = i
    scale = (0.3 * pow( 0.5/0.3 , mindex/nSteps ) )
    return scale, minChi2
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='measure some beam currents')
    parser.add_argument('-r', '--run', help='run number',type=str)
    parser.add_argument('-e', '--energyCut', help='energy cut in keV',type=str)
    parser.add_argument('-a', '--areaCut', help='area cut in keV',type=str)
    parser.add_argument('-n', '--nParts', help='number of paritions for systematic error analysis',type=str)
    parser.add_argument('-b', '--batch', action ='store_true', help = 'bool for running batch mode' )
    
   

    args = parser.parse_args()
    run = args.run
    energyCut = args.energyCut
    areaCut = args.areaCut
    nParts = int(args.nParts)
    batch = args.batch
    run = "Run"+str(run)
    memDepth = 4096
    nCuts = 8
    if batch:
        r.gROOT.SetBatch(True)
    if run=="Run33362":
    # beforeBeam start index, before stop index, during start, during end, after start, after end, beam Current (nA)
        pairs = [
        [12000, 16000, 17000, 21500, 22000, 24000, 0.5], #0.5nA background
        [26000, 33000, 33700, 38200, 39000, 48000, 1],
        [39000, 48000, 51200, 56000, 56500, 64500, 1.5],
        [56500, 64500, 68400, 73000, 77000, 87000, 2],
        [77000, 87000, 94000, 97500, 99000, 108000, 3],
     #   [99000, 108000, 113000,116500, 99000, 108000, 0.05], #50 pA
      #  [99000, 108000, 121000,124000, 99000, 108000, 0.01], #10 pA
      #  [99000, 108000, 130000,133000, 99000, 108000, 0.001], #1 pA
       # [99000, 108000, 137500,140700, 99000, 108000, 0.001], #1 pA
        ]
        pairs = []
        parts = np.linspace (94000, 97500, nParts+1)
        for i in range (nParts):
            part = [77000, 87000, parts[i], parts[i+1], 99000, 108000, 3.0]
            pairs.append(part)
    elif run=="Run33618": # high current run, 50 nA
        pairs = [
        [0, 8000, 10000, 13500, 13900, 14500, 1], #0.5nA background
        [13900, 14500, 14700, 15400, 15500, 16000, 10], #0.5nA background
        [15500, 16000, 16300, 17700, 18000, 19200, 10], #0.5nA background
        [18000, 19200, 19700, 21200, 21500, 22800, 50], #0.5nA background
        [21500, 22800, 23000, 23600, 25000, 26500, 50], #0.5nA background
        [27900, 28700, 27100, 27600, 27900, 28700, 50], #0.5nA background
        [27900, 28700, 10000, 28900, 29600, 31000, 50], #0.5nA background
  #      [99000, 108000, 113000,116500, 99000, 108000, 0.05], #50 pA
  #      [99000, 108000, 121000,124000, 99000, 108000, 0.01], #10 pA
  #      [99000, 108000, 130000,133000, 99000, 108000, 0.001], #1 pA
  #      [99000, 108000, 137500,140700, 99000, 108000, 0.001], #1 pA
        ]
        memDepth = 65536
    elif run=="Run52539":
        pairs = []
        parts = np.linspace (105000, 195000, nParts+1)
        for i in range (nParts):
            part = [80000, 95000, parts[i], parts[i+1], 205000, 220000, 3.0]
            pairs.append(part)
        memDepth = 4096
    elif run=="46903":
        pairs = []
        parts = np.linspace (105000, 195000, nParts+1)
        for i in range (nParts):
            part = [80000, 95000, parts[i], parts[i+1], 205000, 220000, 3.0]
            pairs.append(part)
        memDepth = 4096
    elif run=="Run33361":
        #for run 33361, with dirpi13
        pairs = [
        [13500 , 14500, 14800 , 16000, ], #0.5nA background
        [14800 , 16000], #0.5 nA
        [17200 , 19400],
        [19700 , 20900],#1.0 nA
        [21100 , 24000],
        [24800 , 26100],#1.5 nA
        [32300 , 35200],
        [29500 , 31000],# 2 nA
        [32300 , 35200],
        [37000, 38600], #3 nA
        [39000, 41500], #3 nA after
        ]
    elif run=="Run33478":
        #dirpi5, Run33478
  #      pairs = [
  #      [88000 , 100000, 105000, 125000, 225001, 400000, 0.01],
  #      [88000 , 100000, 125001, 145000, 225001, 400000, 0.01],
   #     [88000 , 100000, 145001, 165000, 225001, 400000, 0.01],
    #    [88000 , 100000, 165001, 185000, 225001, 400000, 0.01],
     #   [88000 , 100000, 185001, 205000, 225001, 400000, 0.01],
      #  [88000 , 100000, 205001, 225000, 225001, 400000, 0.01],
       # [88000 , 100000, 105000, 125000, 225001, 400000, 0.01],
       # ]
        pairs = []
        parts = np.linspace (105000, 240000, nParts+1)
        for i in range (nParts):
            part = [88000 , 100000, parts[i], parts[i+1], 250000, 400000, 0.01]
            pairs.append(part)
    
    elif run=="Run33498":
        pairs = []
        parts = np.linspace (290000, 520000, nParts+1)
        for i in range (nParts):
            part = [0 , 60000, parts[i], parts[i+1], 600000, 65000, 0.01]
            pairs.append(part)
    
    if memDepth == 65536:
        #only keep triggers between 36 - 38k
        end = memDepth - 500
        begin = 38000
    else:
        begin = 500
        end = 3500
    
    filename="pulseCounting"+run+"_n"+str(nParts)+".root"
                  #  tuples start stop signalRate,     signal_BGRate,  poissonErr, poissonErrBG , rateS_BG, signal_BG,  time, current
    file =r.TFile.Open(filename,"RECREATE")
    
    start =  array('f', [0,0 ,0, 0,0,0,0,0]) # on entry per cut
    stop =  array('f', [0,0 ,0, 0,0,0,0,0])
    signalRate =  array('f', [0,0 ,0, 0,0,0,0,0])
    poissonErr  =  array('f', [0,0 ,0, 0,0,0,0,0])
    signal_BGRate  =  array('f', [0,0 ,0, 0,0,0,0,0])
    poissonErrBG  =  array('f',[0,0 ,0, 0,0,0,0,0])
    time  =  array('f', [0,0 ,0, 0,0,0,0,0])
    current  =  array('f', [0,0 ,0, 0,0,0,0,0])
    signalCounts  = array('f', [0,0 ,0, 0,0,0,0,0])
    signalEnergy  = array('f', [0,0 ,0, 0,0,0,0,0])
    signal_BGCounts  = array('f', [0,0 ,0, 0,0,0,0,0])
    bgCounts  = array('f', [0,0 ,0, 0,0,0,0,0])
    ch  = array('f', [0,0 ,0, 0,0,0,0,0])
    energyRate = array('f', [0,0,0,0,0,0,0,0])
    energyRate_BG = array('f', [0,0,0,0,0,0,0,0])
    poissonErrE = array('f', [0,0,0,0,0,0,0,0])
    poissonErrEBG = array('f', [0,0,0,0,0,0,0,0])
    tin = array('f', [0,0,0,0,0,0,0,0])

    tree = r.TTree("rates", "rates")
    tree.Branch("start", start, "start[8]/F")
    tree.Branch("stop", stop, "stop[8]/F")
    tree.Branch("signalRate", signalRate, "signalRate[8]/F")
    tree.Branch("poissonErr", poissonErr, "poissonErr[8]/F")
    tree.Branch("signal_BGRate", signal_BGRate, "signal_BGRate[8]/F")
    tree.Branch("poissonErrBG", poissonErrBG, "poissonErrBG[8]/F")
    tree.Branch("time", time, "time[8]/F")
    tree.Branch("current", current, "current")
    tree.Branch("signalCounts", signalCounts, "signalCounts[8]/F")
    tree.Branch("signalEnergy", signalCounts, "signalEnergy[8]/F")
    tree.Branch("signal_BGCounts", signal_BGCounts, "signal_BGCounts[8]/F")
    tree.Branch("ch", ch, "ch[8]/F")
    tree.Branch("energyRate", energyRate, "energyRate[8]/F")
    tree.Branch("energyRate_BG", energyRate_BG, "energyRate_BG[8]/F")
    tree.Branch("poissonErrE", poissonErrE, "poissonErrE[8]/F")
    tree.Branch("poissonErrEBG", poissonErrEBG, "poissonErrEBG[8]/F")

    h = r.TH1F("h",";Pulse rate (Hz); Counts", 100, 0, 250)
    hBG = r.TH1F("hBG",";Pulse rate (Hz); Counts", 100, 0, 250)
    hErr = r.TH1F("hErr",";Pulse rate (Hz); Counts", 100, 0, 25)
    hErrBG = r.TH1F("hErrBG",";Pulse rate (Hz); Counts", 100, 0, 25)
    hE = r.TH1F("hE",";Summed pulse energy (keV); Counts", 100, 0, 250)
    hErrE = r.TH1F("hErrE",";#sigma(Summed pulse energy (keV)); Counts", 100, 0, 50)
    histos = [h, hBG, hErr, hErrBG, hE, hErrE]
    h2 = r.TH1F("h2",";Pulse rate (Hz); Counts", 100, 0, 250)
    hBG2 = r.TH1F("hBG2",";Pulse rate (Hz); Counts", 100, 0, 250)
    hErr2 = r.TH1F("hErr2",";Pulse rate (Hz); Counts", 100, 0, 25)
    hErrBG2 = r.TH1F("hErrBG2",";Pulse rate (Hz); Counts", 100, 0, 25)
    histos2 = [h, hBG, hErr, hErrBG]
    #filename="pulseCounting"+run+".csv"
 #   with open(filename, 'w') as csvfile:
            # creating a csv writer object
           # csvwriter = csv.writer(csvfile)
    graphs = []
    graphsBG = []
    graphsE = []
    graphsEBG = []
    rate_v_time =[]
    rate_v_timeBG =[]
    electrometer_v_time = []
    videoReadings = "ZoomVideoReadings_10th_frame.txt"
    correction = 891 #correction in seconds for the 14:51 betwwen start of Run33362 and Zoom video
    skip_start_time = 2475/25
   # correction =  correction +   skip_start_time
    times = []
    readings = []
    electrometer_v_time.append(copy.deepcopy( r.TGraphErrors()))
    with  open(videoReadings, 'r') as v:
        lines = v.readlines()
        #times.append(float(v.split(",")[0]))
       # readings.append(float(v.split(",")[0])*scale)
        for l in lines:
            electrometer_v_time[0].AddPoint(float(l.split(",")[0]) + correction , float(l.split(",")[1]))
    mean = electrometer_v_time[0].GetMean(2)
    hElectrometer = getHist(electrometer_v_time[0])
    mean*=2.7
    electrometer_v_time[0].Scale(1./mean)

    for i in range(nCuts):
        graphs.append(copy.deepcopy( r.TGraphErrors()) )
        graphsBG.append(copy.deepcopy(r.TGraphErrors()) )
        graphsE.append(copy.deepcopy(r.TGraphErrors()) )
        graphsEBG.append(copy.deepcopy(r.TGraphErrors()) )
        rate_v_time.append(copy.deepcopy(r.TGraphErrors()) )
        rate_v_time[i].SetTitle("Rate vs start, "+str(pairs[0][6])+" nA beam current ;Time [s];Pulse rate [Hz]")
        rate_v_time[i].GetXaxis().SetTickLength(0.01)
        rate_v_time[i].GetXaxis().SetNdivisions(100)
       # rate_v_time[i].GetXaxis().SetRangeUser(0, 1e4)
        rate_v_time[i].GetXaxis().SetLimits(0, 1e4)
        rate_v_timeBG.append(copy.deepcopy(r.TGraphErrors()) )
        rate_v_timeBG[i].SetTitle("Rate vs start, "+str(pairs[0][6])+" nA beam current ;Time [s];Pulse rate [Hz]")
        rate_v_timeBG[i].GetXaxis().SetTickLength(0.01)
        rate_v_timeBG[i].GetXaxis().SetNdivisions(100)
       # rate_v_time[i].GetXaxis().SetRangeUser(0, 1e4)
        rate_v_timeBG[i].GetXaxis().SetLimits(0, 1e4)
        graphs[i].SetMarkerStyle(1)
        #graphs[i].SetMarkerSize(5)
        graphsBG[i].SetMarkerStyle(32)
        graphsE[i].SetMarkerStyle(23)
        graphsEBG[i].SetMarkerStyle(32)
    graphs[0].SetTitle(";Beam current [nA];Pulse rate [Hz]")
    graphsE[0].SetTitle(";Beam current [nA];Summed pulse energy [keV]")

    iPair = 0
    for pair in pairs:
        start[0] = pair[0]
        stop[0] = pair[1]
        print("getting number of background pulses before")
        before = getNbeam(start[0],stop[0], run, energyCut, pair[6], memDepth) # returns an array with the number of beam pulses before, during, and after the beam on period
        start[0] = pair[2]
        stop[0] = pair[3]
        print("getting number of beam-induced pulses")
        during = getNbeam(start[0],stop[0], run, energyCut, pair[6],  memDepth)
        start[0] = pair[4]
        stop[0] = pair[5]
        print("getting number of background pulses after")
        after = getNbeam(start[0],stop[0], run, energyCut, pair[6])
        print("the length of before is: ", len(before) )
        ret = getRate(before, during, after, pair[6], end - begin)
        print("the return of getRate is " )
        print(ret)
        nCuts = len(ret[0])
        i = 0
        #ret = [ start, stop, signalRate,   poissonErr,  signal_BGRate,   poissonErrBG ,  time, current, signalCounts, signal_BGCounts, bgCounts        ]
        for i in range(nCuts): #loop over the different cuts
            start[i] = ret[0][i]
            stop[i] = ret[1][i]
            signalRate[i] =  ret[2][i]
            poissonErr[i]  =  ret[3][i]
            signal_BGRate[i]  =  ret[4][i]
            poissonErrBG[i]  =  ret[5][i]

            time[i]  = ret[6][i]
            current[i]  =  ret[7]
            signalCounts[i]  = ret[8][i]
            signalEnergy[i]  = ret[11][i]
            signal_BGCounts[i]  = ret[9][i]
            bgCounts[i]  = ret[10][i]
            energyRate[i] = ret[12][i]
            poissonErrE[i] = ret[13][i]
            energyRate_BG[i] = ret[14][i]
            poissonErrEBG[i] = ret[15][i]
            tin[i] = ret[16][i]
            if i <4:
                ch[i] = 1
            else:
                ch[i] = 2
            if i == 0:
                h.Fill(signalRate[i])
                hBG.Fill(signal_BGRate[i])
                hErr.Fill(poissonErr[i])
                hErrBG.Fill(poissonErrBG[i])
                hE.Fill(signalEnergy[i])
                hErrE.Fill(poissonErrE[i])
                print(poissonErrE[i])
            graphs[i].AddPoint(float(current[i]), float(signalRate[i]) )
            graphs[i].SetPointError(iPair, float( 0.), float(poissonErr[i]) )
           # graphsE[i].AddPoint(float(current[i]), float(energyRate[i]) )
           # graphsE[i].SetPointError(iPair, float( 0.), float(poissonErrE[i]) )
            graphsBG[i].AddPoint( float(current[i]), float(signal_BGRate[i]) )
            graphsBG[i].SetPointError(iPair,  float(0.), float(poissonErrBG[i]) )
            rate_v_time[i].SetMinimum(0.01)
            rate_v_time[i].SetMaximum(3)
            rate_v_timeBG[i].SetMinimum(0.01)
            rate_v_timeBG[i].SetMaximum(3)
            print("the time in run is ", float(tin[i] ))
            rate_v_time[i].AddPoint(float(tin[i] ), float(signalRate[i]) ) # was 'start' before
            rate_v_time[i].SetPointError(iPair, float(0.), float(poissonErr[i]))
            rate_v_timeBG[i].AddPoint(float(tin[i] ), float(signalRate[i]) ) # was 'start' before
            rate_v_timeBG[i].SetPointError(iPair, float(0.), float(poissonErr[i]))
            #graphsEBG[i].AddPoint( float(current[i]), float(energyRate_BG[i]) )
            #graphsEBG[i].SetPointError(iPair,  float(0.), float(poissonErrEBG[i]) )
            i+=1
        tree.Fill()
        #fill ntuple from ret? # tuples start stop signalRate,     signal_BGRate,  poissonErr, poissonErrBG , rateS_BG, signal_BG,  time, current?
        #then every run has an nutuple with the things we actually want to measure
        rows = [before, during, after]
        rows = []
        for i in range(nCuts):
            rows.append([])
        i=-1
        for list in before:
            i+=1
            for entry in list:
                #print(rows)
                #print(i)
                rows[i].append(entry)
        i=-1
        for list in during:
            i+=1
            for entry in list:
                rows[i].append(entry)
        i=-1
        for list in after:
            i+=1
            for entry in list:
                rows[i].append(entry)

        iPair+=1

    # writing the data rows
       # csvwriter.writerows(rows)
    file.cd()
    tree.Write()
    for histo in histos:
        histo.Write()
    # save tgraphs here?
    
    can = r.TCanvas()
    can.SetLogy(1)
    can.SetLogx(1)
    i = 0
    leg = r.TLegend(0.55,0.15, 0.85, 0.35)
    cuts = [
    "no cuts",
    "largeEarlyPulse veto",
    "energy cut, E > 1500 keV",
    "veto and cut",
    "LYSO, none",
    "LYSO, largeEarlyPulses",
    "lo energy cut",
    "mid energy cut"
    ]
    for g in graphs:
        g.SetMinimum(10)
        g.SetLineColor(p.colors[i])
        g.SetMarkerStyle(23)
        g.SetMarkerColor(p.colors[i])
        if i ==0:
            g.Draw("AP")
        else:
            g.Draw("same&&P")
        leg.AddEntry(g, cuts[i])
        leg.Draw()
        p.savePlots(can,"./plots/"+run+"/", run+"_rateSummary_"+str(i))
        g.Write("g"+str(i))
        i+=1
    i=0
    for g in graphsBG:
        g.SetLineColor(p.colors[i])
        g.SetMarkerColor(p.colors[i])
        g.SetMarkerStyle(24)
        g.Draw("same&&P")
       # leg.AddEntry(g, "with background subtracted")
        p.savePlots(can,"./plots/"+run+"/","Run"+run+"_rateSummaryBG_"+str(i) )
        g.Write("gBG"+str(i))
        can.Write()
        i+=1
    leg.Draw()
    can.Write()
    i =0
    leg = r.TLegend(0.65,0.2, 0.8, 0.35)
    for g in graphsE:
        g.SetMinimum(100)
        g.SetLineColor(p.colors[i])
        g.SetMarkerColor(p.colors[i])
        g.SetMarkerStyle(23)
        if i ==0:
            g.Draw("AP")
        else:
            g.Draw("same&&P")
        leg.AddEntry(g, cuts[i])
       # leg.AddEntry(g, "with background subtracted")
        g.Write()
        g.Write("gBGE"+str(i))
        i+=1
    leg.Draw()
    i=0
    for g in graphsEBG:
        g.SetLineColor(p.colors[i])
        g.SetMarkerColor(p.colors[i])
        g.SetMarkerStyle(24)
        g.Draw("same&&P")
       # leg.AddEntry(g, "with background subtracted")
        g.Write("gEBG"+str(i))
        can.Write()
        i+=1
    can.SetLogy(1)
    can.SetLogx(1)
    i=0
    for g in rate_v_time:
        leg = r.TLegend(0.65, 0.2, 0.8, 0.35)
        g.SetLineColor(p.colors[i])
     #   g.SetLineStyle(10)
        g.SetMarkerColor(p.colors[i])
        g.SetMarkerStyle(1)
       # if i ==0:
       #     g.Draw("AP")
      #  else:
        g.GetXaxis().SetLimits(0, 1e4)
        g.GetXaxis().SetRangeUser(0, 1e4)
        g.Draw("APL")       # leg.AddEntry(g, "with background subtracted")
        mean = g.GetMean(2)
        hPMT = getHist(g)
        g.Scale(1./mean)
      #  scale, chi2 = getScale(hPMT, hElectrometer)
        scale = 1.
        leg.AddEntry(g, cuts[i] + " scale = " + str(scale) )
        electrometer_v_time[0].Scale(scale)
        electrometer_v_time[0].Draw("same")
        leg.Draw()
        g.Write("rate_v_time"+str(i))
        can.Write()
        p.savePlots(can,"./plots/"+run+"/", run+"_rate_v_time_n"+str( g.GetN() )+"_"+str(i) )
        i+=1
    i=0
    for g in rate_v_timeBG:
        leg = r.TLegend(0.65, 0.2, 0.8, 0.35)
        g.SetLineColor(p.colors[i])
      #  g.SetLineStyle(10)
        g.SetMarkerColor(p.colors[i])
        g.SetMarkerStyle(1)
       # if i ==0:
       #     g.Draw("AP")
      #  else:
        g.GetXaxis().SetLimits(0, 1e4)
        g.GetXaxis().SetRangeUser(0, 1e4)
        g.Draw("APL")       # leg.AddEntry(g, "with background subtracted")
        mean = g.GetMean(2)
        g.Scale(1./mean)
        leg.AddEntry(g, cuts[i])
        electrometer_v_time[0].Draw("same")
        leg.Draw()
        g.Write("rate_v_timeBG"+str(i))
        can.Write()
        p.savePlots(can,"./plots/"+run+"/", run+"_rate_v_timeBG_n"+str( g.GetN() )+"_"+str(i) )
        i+=1
    can.Write()
    i =0
  #  p.savePlots(can,"./plots/"+run+"/", "Run"+run+"_energySummary")
    can.Write()

    file.Write()
  #  rows = getNbeam(105000,225000, run, energyCut)


