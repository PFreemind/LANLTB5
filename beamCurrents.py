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

def getNbeam(start=0, stop=1000, run = "Run33362", energyCut=1500):
    dir = "./pulse_data/"
    file =r.TFile.Open(dir+run+"_dirpipulses.root","READ")
    t=file.Get("pulses")
    h = r.TH1F("h",";Pulse energy (keV); Counts", 256, 0, 2500)
    hE = r.TH1F("hE",";Pulse energy (keV); Counts", 256, 0, 2500)
    hPE = r.TH1F("hPE",";Pulse energy (keV); Counts", 256, 0, 2500)
    hP = r.TH1F("hP",";Pulse energy (keV); Counts", 256, 0, 2500)
    
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
        if evt>=start and evt <= stop and ch == 1 and tP > 500 and tP < 3000:
           # print (keV)
            h.Fill(keV)
            if area1a < 3000 and area1b < 3000:
                hP.Fill(keV)
                if evt not in evts:
                    evts.append(evt)
                    nEvt += 1
            if keV> energyCut:
                hE.Fill(keV)
                if area1a < 3000 and area1b < 3000:
                    hPE.Fill(keV)
    can = r.TCanvas()
    h.Draw()
    p.savePlots(can, "./plots/"+run, "pulseCount_evt_"+str(stop))
    #tell me how many pulses there were
    nPulses = h.GetEntries()
    
  #  print("oh boy there are a bunch of pulses: ",nPulses )
#    input("")
    
    #write things to .txt/csv
    # field names
    fields = ["cut","start", "stop", "counts", "nEvts"]
        
    # data rows of csv file
    rows = [ ["none", start, stop, h.GetEntries(), stop-start+1 ],
        ["largeEarlyPulses", start, stop, hP.GetEntries(), nEvt ],
        ["energy", start, stop, hE.GetEntries(), stop-start+1 ],
        ["both", start, stop, hPE.GetEntries(), nEvt  ] ]
    # name of csv file
    filename = "beamCounting_evt_"+str(stop)+".csv"
    # writing to csv file
    with open(filename, 'w') as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
            
        # writing the fields
        csvwriter.writerow(fields)
            
        # writing the data rows
        csvwriter.writerows(rows)
    print(fields)
    for row in rows:
        print(row)
    return rows
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='measure some beam currents')
    parser.add_argument('-r', '--run', help='run number',type=str)
    
    args = parser.parse_args()
    run =args.run
    run="Run"+str(run)
    
    if run=="Run33362":
        pairs = [
        [12000, 16000], #0.5nA background
        [17000, 21500], #0.5 nA
        [22000, 24000],
        [26000, 33000],
        [33700, 38200], #1.0 nA
        [39000, 48000],
        [51200, 56000], #1.5 nA
        [56500, 64500],
        [68400, 73000], # 2 nA
        [77000, 87000],
        [94000, 97500], #3 nA
        [99000, 108000], #3 nA after
        ]
    elif run=="Run33361":
        #for run 33361, with dirpi13
        pairs = [
        [13500 , 14500], #0.5nA background
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
    elif run=="Run33478"
        #dirpi5, Run33478
        pairs = [
        [88000 , 100000],
        [105000, 125000],
        [125001, 145000],
        [145001, 165000],
        [165001, 185000],
        [185001, 205000],
        [205001, 225000],
        [225001, 400000],
        ]

    filename="pulseCounting"+run+".csv"
    with open(filename, 'w') as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)
                
            for pair in pairs:
                start = pair[0]
                stop = pair[1]
                rows = getNbeam(start,stop, run)
                
            # writing the data rows
                csvwriter.writerows(rows)

        
 #   getNbeam(start,stop, run = "Run33361")

    #need to add event counting

    # ok, need cuts and lit iteration
    #chat cuts

