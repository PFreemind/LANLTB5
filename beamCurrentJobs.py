import os
parts = [ 3, 10, 30, 100]
runs = [
"33362", #sept 7 dedicated running
#"33478", #10 pA run
"33498"  #longer 10 pA run
]

jobs = []

for part in parts:
    for run in runs:
          cmd = "python3.10 beamCurrents.py -r "+str(run)+" -e 1500  -n "+str(part)
          print(cmd)
          jobs.append(cmd)
       #   os.system(cmd)


import ROOT as r
import pulseAnalysis as p
import copy
cuts = [
    "no cuts",
    "largeEarlyPulse veto",
    "energy cut, E > 1500 keV",
    "veto and cut",
    "LYSO, none",
    "LYSO, largeEarlyPulses",
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

sigmaGraphsEnergy = []
sigmaFits = []
poissonGraphsEnergy = []
poissonFits = []
#compare 2 graphs per cut that should go as the sqrt(N) and be equal
#do for N, THEN energy
#then add background subtracted runs
#make these all gifs so you can go through and explain them in slides 1-by-1

can = r.TCanvas()
can.SetLogy(1)
iPart = 0
leg = r.TLegend(0.3, 0.15,  0.85, 0.55)
#for run in runs: #graphs
for i in range(nCuts): #colors
    sigmaGraphs.append(copy.deepcopy( r.TGraphErrors()) )
    sigmaFits.append(r.TF1("fS"+str(i),"TMath::Sqrt( [1]*x ) + [0]", 0, 100))
    sigmaFits[i].SetParLimits(1,0.1, 20)
    sigmaFits[i].SetLineWidth(1)
    poissonGraphs.append(copy.deepcopy( r.TGraphErrors()) )
    poissonFits.append(r.TF1("fP"+str(i),"TMath::Sqrt( [1]*x ) + [0]", 0, 100))
    poissonFits[i].SetParLimits(1,0.1, 20)
    poissonFits[i].SetLineWidth(1)
    iPart = 0
    for part in parts: # points
        filename = "pulseCountingRun"+str(run)+"_n"+str(part)+".root"
        f = r.TFile.Open("./"+filename,"READ")
        t = f.Get("rates")
  #      g = f.Get("g"+suffix(i)+str(i))
       
        hSignal = r.TH1F("hSignal", "", 100, 0, 1000)
        hPoisson = r.TH1F("hPoisson","", 100, 0, 1000 )
        for e in t:
            signalRate = t.signalRate[i]
            poissonErr = t.poissonErr[i]
            signal_BGRate = t.signal_BGRate[i]
            poissonErrBGRate = t.signal_BGRate[i]
            hSignal.Fill(signalRate)
            hPoisson.Fill(poissonErr)
            
        sigmaGraphs[i].AddPoint(part,  hSignal.GetRMS() )
        sigmaGraphs[i].SetPointError(iPart,  0.0, hSignal.GetRMSError() )

        poissonGraphs[i].AddPoint(part, hPoisson.GetMean() )
        poissonGraphs[i].SetPointError(iPart, 0.0, hPoisson.GetMeanError() )

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
    leg.AddEntry(sigmaGraphs[i], "#sigma ( #mu ( rate ))        "+cuts[i])
    leg.AddEntry(poissonGraphs[i], "#mu ( #sigma_{Poisson} ( rate )) "+cuts[i])

    if i ==0:
        sigmaGraphs[i].SetTitle("Comparison of Sample Std Dev to Poisson Errors;Number of partitions of run;Estimated Error [Hz];")
        sigmaGraphs[i].SetMinimum(0.1)
        sigmaGraphs[i].Draw("AP")
    else:
       sigmaGraphs[i].Draw("same&&P")
    sigmaGraphs[i].Fit("fS"+str(i), "R" )
    poissonGraphs[i].Draw("P&&same")
    poissonGraphs[i].Fit("fP"+str(i),"R")
    leg.Draw()
    p.savePlots(can, "./", "systematicsCheck_cut" + str(i) )
    i+=1
     #   if suffix == "" or suffix == "E"
      #      sigmaGraphs[i].SetPointError(index?, 0, g.Get)
       # if suffix == "BG" or suffix == "EBG"
       #     sigmaGraphs[i].append( g.GetRMS(2) )
                
            #std dev  == mean (poissonErrs)?
            
            #plot the std dev and mean of poisson errors as a fcn of n
            # fit to sqrt(N)


print("the run/completed jobs:")
for job in jobs:
    print(job)


