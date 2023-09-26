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

def getNbeam(start=0, stop=1000, run = "Run33362", energyCut=1500, current=1.0):
    dir = "./pulse_data/"
    file =r.TFile.Open(dir+run+"_dirpipulses.root","READ")
    t=file.Get("pulses")
    h = r.TH1F("h",";Pulse energy (keV); Counts", 256, 0, 2500)
    hE = r.TH1F("hE",";Pulse energy (keV); Counts", 256, 0, 2500)
    hPE = r.TH1F("hPE",";Pulse energy (keV); Counts", 256, 0, 2500)
    hP = r.TH1F("hP",";Pulse energy (keV); Counts", 256, 0, 2500)
    hT = r.TH1F("hT",";Pulse time (s); Counts", 256, 3000, 18000)
    hTE = r.TH1F("hTE",";Pulse time (s); Counts", 256, 3000, 18000)
    hTP = r.TH1F("hTP",";Pulse time (s); Counts", 256, 3000, 18000)

    evts = []
    nEvt = 0
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
        iPulse = t.iPulse
        if evt>stop:
            break
        if evt>=start and evt <= stop and ch == 1 and tP > 500 and tP < 3500 and iPulse>0:
           # print (keV)
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
                    hPE.Fill(keV) # fill the histogram for the energy cut and large pulse veto
    can = r.TCanvas()
    h.Draw()
   # p.savePlots(can, "./plots/"+run, "pulseCount_evt_"+str(stop))
    
    leg = r.TLegend()
    can = r.TCanvas()
  #  can.SetLogy(1)
    hT.SetMinimum(0.1)
    leg.AddEntry(hT)
    hT.Draw()
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
    fields = ["cut","start", "stop", "counts", "nEvts", "current (nA)"]
        # data rows of csv file
    rows = [ ["none", start, stop, h.GetEntries(), stop-start+1 ],
        ["largeEarlyPulses", start, stop, hP.GetEntries(), stop-start+1 - nEvt ],
        ["energy", start, stop, hE.GetEntries(), stop-start+1 ],
        ["both", start, stop, hPE.GetEntries(), stop-start+1 - nEvt  ] ]
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
    
def getRate(before, during, after, current):
    signalCounts = []
    bgCounts = []
    signal_BGCounts = []
    signalRate = []
    poissonErr = []
    signal_BGRate = []
    poissonErrBG = []
    time = []
    start = []
    stop = []
    i = 0
    for row in before:
        nEvt = during[i][4]
        counts = during[i][3]
        nEvtAfter = after[i][4]
        countsAfter = after[i][3]
        nEvtBefore = before[i][4]
        countsBefore = before[i][3]
        start.append( during[i][1] )
        stop.append(during[i][2])
        time.append( 3000. * 25.0e-9 * nEvt)
        signalRate.append(counts/time[i])
        poissonErr.append(pow(counts,0.5)/time[i])
        signalCounts.append(counts)
        nAfter = after[i]
        bg = (countsAfter *  nEvt/nEvtAfter + countsBefore * nEvt/nEvtBefore) * 0.5
        signal_BGCounts.append(signalCounts[i]-bg)
        signal_BGRate.append((signal_BGCounts[i])/time[i])
        poissonErrBG.append(pow(abs(signal_BGCounts[i]), 0.5)/time[i] )
        bgCounts.append(bg)
        i+=1
       # print(i)
  #  print(signalRate)
    ret = [ start, stop, signalRate,   poissonErr,  signal_BGRate,   poissonErrBG ,  time, current, signalCounts, signal_BGCounts, bgCounts       ]
   # print(ret)
    return ret

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='measure some beam currents')
    parser.add_argument('-r', '--run', help='run number',type=str)
    parser.add_argument('-e', '--energyCut', help='energy cut in keV',type=str)
    parser.add_argument('-a', '--areaCut', help='area cut in keV',type=str)

    args = parser.parse_args()
    run =args.run
    energyCut=args.energyCut
    areaCut=args.areaCut
    run="Run"+str(run)
    
    if run=="Run33362":
        pairs = [
        [12000, 16000, 17000, 21500, 22000, 24000, 0.5], #0.5nA background
        [26000, 33000, 33700, 38200, 39000, 48000, 1],
        [39000, 48000, 51200, 56000, 56500, 64500, 1.5],
        [56500, 64500, 68400, 73000, 77000, 87000, 2],
        [77000, 87000, 94000, 97500, 99000, 108000, 3],
  #      [99000, 108000, 113000,116500, 99000, 108000, 0.05], #50 pA
  #      [99000, 108000, 121000,124000, 99000, 108000, 0.01], #10 pA
  #      [99000, 108000, 130000,133000, 99000, 108000, 0.001], #1 pA
  #      [99000, 108000, 137500,140700, 99000, 108000, 0.001], #1 pA
        ]
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
        nParts = 10
        parts = np.linspace (105000, 225000, nParts+1)
        for i in range (nParts):
            part = [88000 , 100000, parts[i], parts[i+1], 225001, 400000, 0.01]
            pairs.append(part)
        
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
        nParts = 100
        parts = np.linspace (105000, 240000, nParts+1)
        for i in range (nParts):
            part = [88000 , 100000, parts[i], parts[i+1], 250000, 400000, 0.01],
            pairs.append(part)
    
    elif run=="Run33498":
        pairs = []
        nParts = 100
        parts = np.linspace (290000, 520000, nParts+1)
        for i in range (nParts):
            part = [0 , 60000, parts[i], parts[i+1], 600000, 65000, 0.01]
            pairs.append(part)
    filename="pulseCounting"+run+".root"
                  #  tuples start stop signalRate,     signal_BGRate,  poissonErr, poissonErrBG , rateS_BG, signal_BG,  time, current
    file =r.TFile.Open(filename,"RECREATE")
    
    start =  array('f', [0,0 ,0, 0])
    stop =  array('f', [0,0 ,0, 0])
    signalRate =  array('f', [0,0 ,0, 0])
    poissonErr  =  array('f', [0,0 ,0, 0])
    signal_BGRate  =  array('f', [0,0 ,0, 0])
    poissonErrBG  =  array('f', [0,0 ,0, 0])
    time  =  array('f', [0,0 ,0, 0])
    current  =  array('f', [0,0 ,0, 0])
    signalCounts  = array('f', [0,0 ,0, 0])
    signal_BGCounts  = array('f', [0,0 ,0, 0])
    bgCounts  = array('f', [0,0 ,0, 0])
    
    tree = r.TTree("rates", "rates")
    tree.Branch("start", start, "start[4]/F")
    tree.Branch("stop", stop, "stop[4]/F")
    tree.Branch("signalRate", signalRate, "signalRate[4]/F")
    tree.Branch("poissonErr", poissonErr, "poissonErr[4]/F")
    tree.Branch("signal_BGRate", signal_BGRate, "signal_BGRate[4]/F")
    tree.Branch("poissonErrBG", poissonErrBG, "poissonErrBG[4]/F")
    tree.Branch("time", time, "time[4]/F")
    tree.Branch("current", current, "current")
    tree.Branch("signalCounts", signalCounts, "signalCounts[4]/F")
    tree.Branch("signal_BGCounts", signal_BGCounts, "signal_BGCounts[4]/F")
    tree.Branch("bgCounts", bgCounts, "bgCounts[4]/F")

    h = r.TH1F("h",";Pulse rate (Hz); Counts", 100, 0, 250)
    hBG = r.TH1F("hBG",";Pulse rate (Hz); Counts", 100, 0, 250)
    hErr = r.TH1F("hErr",";Pulse rate (Hz); Counts", 100, 0, 25)
    hErrBG = r.TH1F("hErrBG",";Pulse rate (Hz); Counts", 100, 0, 25)
    histos = [h, hBG, hErr, hErrBG]
    #filename="pulseCounting"+run+".csv"
 #   with open(filename, 'w') as csvfile:
            # creating a csv writer object
           # csvwriter = csv.writer(csvfile)
    for pair in pairs:
        start[0] = pair[0]
        stop[0] = pair[1]
        before = getNbeam(start[0],stop[0], run, energyCut, pair[6])
        start[0] = pair[2]
        stop[0] = pair[3]
        during = getNbeam(start[0],stop[0], run, energyCut, pair[6])
        start[0] = pair[4]
        stop[0] = pair[5]
        after = getNbeam(start[0],stop[0], run, energyCut, pair[6])
        ret = getRate(before, during, after, pair[6])
        print("the return of get rate is " )
        print(ret)
        #start, stop, signalRate,   poissonErr,  signal_BGRate,   poissonErrBG ,  time, current, signalCounts, signal_BGCounts, bgCounts        ]
        for i in range(4):
            start[i] = ret[0][i]
            stop[i] = ret[1][i]
            signalRate[i] =  ret[2][i]
            poissonErr[i]  =  ret[3][i]
            signal_BGRate[i]  =  ret[4][i]
            poissonErrBG[i]  =  ret[5][i]
            time[i]  = ret[6][i]
            current[i]  =  ret[7]
            signalCounts[i]  = ret[8][i]
            signal_BGCounts[i]  = ret[9][i]
            bgCounts[i]  = ret[10][i]
            if i == 0:
                h.Fill(signalRate[i])
                hBG.Fill(signal_BGRate[i])
                hErr.Fill(poissonErr[i])
                hErrBG.Fill(poissonErrBG[i])
        tree.Fill()
        #fill ntuple from ret? # tuples start stop signalRate,     signal_BGRate,  poissonErr, poissonErrBG , rateS_BG, signal_BG,  time, current?
        #then every run has an nutuple with the things we actually want to measure
        rows = [before, during, after]
        rows = []
        for i in range(4):
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
    # writing the data rows
       # csvwriter.writerows(rows)
    file.cd()
    tree.Write()
    for histo in histos:
        histo.Write()
    file.Write()
    rows = getNbeam(105000,225000, run, energyCut)


