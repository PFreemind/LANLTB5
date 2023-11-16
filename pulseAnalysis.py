import ROOT as r
import numpy as np
from array import array
import requests
import os
import configparser
import math
import csv
import argparse


# scripting to parse and plot david's pulse data from 2022 November Beam Development

# .ant file parsing
#1 = event number
#2 = time since start of run (here I just set that equal to event number)
#3 = time between events (here I just set it to 1)
#4 = number of pulses in the event in any channel
#5 = number of pulses in channel 1 in the event
#6 = number of pulses in channel 2 in the event
#7 = number of pulses in channel 3 in the event
#8 = number of pulses in channel 4 in the event
#9 = RMS of the waveform containing this particular pulse, as measured from samples at the start of the waveform
#10 = channel number
#11 = pulse number within this channel (starts at 0 for first pulse)
#12 = time of the pulse within the waveform, in ns
#13 = area of the pulse in nVs
#14 = height of the pulse in mV
#15 = width of the pulse in ns
#16 = area of the pulse calibrated to number of photoelectrons
#17 = area of the pulse calibrated in keV


'''
// Definition of variables in the dirpipulses ant file
antdef n 30 // Number of columns per line
// Event wide information
antdef run 1 // Run number
antdef evt 2 // Event number within
antdef tInRun 3 // Time since start of run in seconds
antdef tBetweenEvents 4 // Time since previous event in seconds
antdef nPulses 5 // Number of pulses in event summed over both channels
antdef nCh1Pulses 6 // Number of pulses in channel 1
antdef nCh2Pulses 7 // Number of pulses in channel 2
antdef RMS1 8 // RMS for channel 1
antdef RMS2 9 // RMS for channel 2
antdef Ped1 10 // Pedestal for channel 1 (subtracted before pulse finding)
antdef Ped2 11 // Pedestal for channel 2 (subtracted before pulse finding)
// The following are the sum of all pulses in different time windows.
// Region a is well before the trigger, b is before the trigger window
// Region c is after the trigger, and d is well after the trigger.
// The specific time windows will be adjusted based on run type,
// but the intent for LANL is a=preRF, b=RF, c=beam, d=post-beam
// These are not yet implimented and for now just 0
antdef Area1a 12 // Total CH1 area in waveform for time region a
antdef Area1b 13 // Total CH1 area in waveform for time region b
antdef Area1c 14 // Total CH1 area in waveform for time region c
antdef Area1d 15 // Total CH1 area in waveform for time region d
antdef Area2a 16 // Total CH2 area in waveform for time region a
antdef Area2b 17 // Total CH2 area in waveform for time region b
antdef Area2c 18 // Total CH2 area in waveform for time region c
antdef Area2d 19 // Total CH2 area in waveform for time region d
// Pulse specific information
antdef chan 20 // Channel number for pulse (1 or 2)
antdef ipulse 21 // number of pulse within waveform for this particular channel
antdef t 22 // Time of pulse (in address units)
antdef A 23 // Area of pulse (in ADCxAddress units)
antdef V 24 // Height of pulse (in ADC counts)
antdef width 25 // Width of pulse (in Address units)
antdef E 26 // Calibrated energy of pulse (in keV)
antdef dt 27 // Time to nearest other pulse in the channel (65536=none)
antdef dtOther 28 // Time to nearest pulse in other channel (65536=none)
antdef coinc 29 // Flag=1 if coincident |dtOther|<4, 0 if not
antdef qual 30 // Pulse quality flag, 0=good
// The quality flag is based on compatibility of V vs A and width vs A.
// The quality flag is not yet implimented and for now just 0.
'''

colors=[
r.kOrange+2,
r.kRed+1,
r.kGreen+2,
r.kCyan-2,
r.kBlue,
r.kGreen,
r.kBlack,
r.kMagenta+1,
r.kGray+1,
r.kSpring-7,
r.kGreen-10,
r.kGreen-8,
r.kGreen-8,
r.kGreen-6,
r.kGreen-5,
r.kGreen,
r.kGreen+1,
r.kGreen+2,
r.kGreen+3,
r.kGreen+4,
r.kOrange+1,
]
# read ntpule into root trees, to be used for histogram and other plotting
def makeTree(input, output):
  out = r.TFile(output,"RECREATE")
  t = r.TTree("pulses", "pulses")
  evt =  array('f', [0])
  tS  =  array('f', [0])
  tE  =  array('f', [0])
  nP  =  array('f', [0])
  n1  =  array('f', [0])
  n2  =  array('f', [0])
  n3  =  array('f', [0])
  n4  =  array('f', [0])
  rms =  array('f', [0])
  ch  =  array('f', [0])
  pC  =  array('f', [0])
  tP  =  array('f', [0])
  area=  array('f', [0])
  area1a=  array('f', [0])
  area1b=  array('f', [0])
  area2a=  array('f', [0])
  area2b=  array('f', [0])
  area1c=  array('f', [0])
  area2c=  array('f', [0])
  amp =  array('f', [0])
  width= array('f', [0])
  NPE =  array('f', [0])
  keV =  array('f', [0])
  coinc =  array('f', [0])
  tin =  array('f', [0])
  dt =  array('f', [0])
  dtO =  array('f', [0])
  iPulse =  array('f', [0])
  tBetweenEvents =  array('f', [0])
  
  t.Branch("nP", nP, "nP/F")
  t.Branch("evt", evt, "evt/F")
  t.Branch("ch", ch, "ch/F")
  t.Branch("tP", tP, "tP/F")
  t.Branch("area", area, "area/F")
  t.Branch("area1a", area1a, "area1a/F")
  t.Branch("area1b", area1b, "area1b/F")
  t.Branch("area2a", area2a, "area2a/F")
  t.Branch("area2b", area2b, "area2b/F")
  t.Branch("area1c", area1c, "area1c/F")
  t.Branch("area2c", area2c, "area2c/F")
  t.Branch("amp", amp, "amp/F")
  t.Branch("width", width, "width/F")
  t.Branch("keV", keV, "keV/F")
  t.Branch("n1", n1, "n1/F")
  t.Branch("n2", n2, "n2/F")
  t.Branch("coinc", n2, "coinc/F")
  t.Branch("tin", tin, "tin/F")
  t.Branch("dt", dt, "dt/F")
  t.Branch("dtO", dtO, "dtO/F")
  t.Branch("iPulse", iPulse, "iPulse/F")
  t.Branch("tBetweenEvents", tBetweenEvents, "tBetweenEvents/F")

  f = open (input,  'r')
  lines = f.readlines()
  count = 0
  for line in lines:
    val = line.split(' ')
   # print(type(val[0]), val[0])
  #  print(count)
  #  print(val)
    evt[0] = (float(val[1]) )
    tBetweenEvents[0] = (float(val[3]) )
    nP[0] = (float(val[4]) )
    n1[0] = (float(val[5]) )
    n2[0] = (float(val[6]) )
    ch[0] = int(val[19])
    #stupid hardcoing for 8125
    #if val[11] == '795483.43\x0050':
    #  val[11] ='795483.43'
    tP[0]= float(val[21])
    area[0] = float(val[22])
    area1a[0] = float(val[11])
    area2a[0] = float(val[15])
    area1b[0] = float(val[12])
    area2b[0] = float(val[16])
    area1c[0] = float(val[13])
    area2c[0] = float(val[17])
    amp[0] = float(val[23])
    width[0] = float(val[24])
    keV[0] = float(val[25])
    coinc[0] = float(val[28])
    dt[0] = float(val[26])
    dtO[0] = float(val[27])
    tin[0] = float(val[2])
    iPulse[0] = float(val[20])
  #  print("evt= "+str(evt[0])+" ch= "+str(ch[0])+", amp = "+str(amp[0]))
   # print("evt= "+str(float(val[0]))+" ch= "+str(float(val[9]))+", amp = "+str(amp[0]))
    t.Fill()
    count += 1
  t.Write()
 # out.Close()
  print ("I made a .root file with a tree: "+output)
  return 0
    
#investigate the turn on for the RF: how does energy (area) spectrum vary for different time cuts along the RF leading edge?
def turnOn(input):
#run8112
#make some histograms, one for each time cut
#loop through tree, fill the histograms
  f = r.TFile(input,"READ")
  t = r.Get("pulses")
  #for entry in t:
    
def countPulses(file):
  f = r.TFile(file)
  t = f.Get("pulses")
  count = 0
  #[before rf, in LBEG, after LBEG]
  nCh1 = [0,0,0]
  nCh2 = [0,0,0]
  nCh5 = [0,0,0]
  for event in t:
    evt = t.evt
    area = t.area
    ch = t.ch
    tP = t.tP
    amp = t.amp
    width = t.width
    if tP< -700e3 and tP > -1100e3: # tP>-900:   before the RF
      if ch == 1:
        nCh1[0]+=1
      if ch == 2:
        nCh2[0]+=1
      if ch == 5:
        nCh5[0]+=1
    if tP < 700e3 and (tP > 190e3 or (area>100e3 and tP>0 )):  #add area cut later...
      if ch==1:
        nCh1[1]+=1
      if ch==2:
        nCh2[1]+=1
      if ch ==5:
        nCh5[1]+=1
    count+=1
  print("for file "+ file +":")
  print(nCh1, nCh2, nCh5)
  return (nCh1, nCh2, nCh5)
    
def downloadAnt(run, url, dir = './pulse_data/'):
    resp = requests.get(url)
    print ("copying file from "+url)
    ant = resp.text
    #f = open(dir+"Run"+str(run)+"_pulses.ant","w")
    f = open(dir+"Run"+str(run)+"_dirpipulses.ant","w")
    f.write(ant)

def downloadConfig(run, dirpi, dir = './pulse_data/'):
    cmsPath = "pmfreeman@tau.physics.ucsb.edu:/net/cms26/cms26r0/pmfreeman/XRD/DiRPi_v3/dirpi"
    path = cmsPath+str(dirpi)+"/Run"+str(run)+"/config.ini"
    dest = dir+"Run"+str(run)+"_config.ini"
    cmd = "scp "+path+" "+dest
    print(cmd)
    os.system(cmd)
    #resp = requests.get(url)
    #ant = resp.text
    #f = open(dir+"Run"+str(run)+"_config.ini","w")
    #f.write(ant)

def getRunList(start = 7000, stop = 22000):
  #get list of dirpi runs
    #    parse it for LANL devices/run numbers:
  urlist = "http://cms2.physics.ucsb.edu/DiRPiRuns"
  resp = requests.get(urlist)
  txt = resp.text
  lines = txt.split("\n")
  runList =[]
  exceptions = [7330, 7471, 7495,7502,7522,7525, 7569, 7570, 7667,7673, 7685,7761,7787, 8314, 20212,  ]
  #need a run dictionary
  dictList = []
  for line in lines:
    if line =="": continue
    dirpirun   = int(line.split(" ")[0])
    run   = int(line.split(" ")[1])
    dirpi = int(line.split(" ")[2])
    if (run>=start and run<=stop and ( dirpi == 12 or dirpi == 5 or dirpi == 13 ) and run not in exceptions and not (run>7536 and run<7562) ): #dirpi == 1 or dirpi == 7 or dirpi == 8 or dirpi == 9 or
      runList.append([run, dirpirun, dirpi])
#  print (runList)
  #trim empty runs from the list
#  runList = trimEmptyRuns(runList)
  return runList
  
  
def cleanRun(target, t0 = 48000, t1=50000, LYSO=False):
    # make a new tree and file to write to
    cleanRun = r.TFile.Open(target+".clean", "RECREATE")
    tree = r.TTree("pulses","pulses")
      
    evtb =  array('f', [0])
    evtb2 =  array('f', [0])
    tS  =  array('f', [0])
    tE  =  array('f', [0])
    nP  =  array('f', [0])
    n1  =  array('f', [0])
    n2  =  array('f', [0])
    n3  =  array('f', [0])
    n4  =  array('f', [0])
    rms =  array('f', [0])
    ch  =  array('f', [0])
    pC  =  array('f', [0])
    tP  =  array('f', [0])
    area=  array('f', [0])
    amp =  array('f', [0])
    width= array('f', [0])
    NPE =  array('f', [0])
    keV =  array('f', [0])
    coinc =  array('f', [0])
    tin =  array('f', [0])
    dt =  array('f', [0])
    dtO =  array('f', [0])

    tree.Branch("nP", nP, "nP/F")
    tree.Branch("evt", evtb, "evt/F")
    tree.Branch("evt2", evtb2, "evt2/F")
    tree.Branch("ch", ch, "ch/F")
    tree.Branch("tP", tP, "tP/F")
    tree.Branch("area", area, "area/F")
    tree.Branch("amp", amp, "amp/F")
    tree.Branch("width", width, "width/F")
    tree.Branch("keV", keV, "keV/F")
    tree.Branch("coinc", n2, "coinc/F")
    tree.Branch("tin", tin, "tin/F")
    tree.Branch("dt", dt, "dt/F")
    tree.Branch("dtO", dtO, "dtO/F")
    # get average pulse time for each event
    prevEvt = int(0)
    infile = r.TFile.Open(target, "READ")
    intree = infile.Get("pulses")
    entries = []
    goodEvts =[]
    evtCount = 1e-10
    totaltP = 0
    for entry in intree:
        evt=intree.evt
        if evt != prevEvt:
            meantP = totaltP/evtCount
            totaltP = 0
            evtCount = 1e-10
            if meantP > t0 and meantP < t1:
                goodEvts.append(1) #event is good
            else:
                goodEvts.append(0)
        else:
            totaltP+=intree.tP
            evtCount+=1
        prevEvt = int(evt)
    #get the last entry
    meantP = totaltP/evtCount
    if meantP > t0 and meantP < t1:
        goodEvts.append(1) #event is good
    else:
        goodEvts.append(0)
    totaltP = 0
    evtCount = 0
    #loop tree again, selcting good events to be written to the new tree
#    print ("list of good events: ", goodEvts)
    prevEvt = int(0)
    evtIndex = int(0)
    count = 0
    for entry in intree:
        if count%1000==0 and count > 0:
            print("processing entry: ",count)
        evt=intree.evt
        if evt != prevEvt:
            evtIndex += 1
            print("new event ", evtIndex)
        if goodEvts[evtIndex] == 1:
            intree.GetEntry(count)
            evtb[0] = (float(intree.evt) )
            evtb2[0] = (float(evtIndex) )                #       nP[0] = (float(intree.nP ))
            ch[0] = int(intree.ch)
            #stupid hardcoing for 8125
            #if val[11] == '795483.43\x0050':
            #  val[11] ='795483.43'
    #        print(intree.tP)
            tP[0]= float(intree.tP)
            area[0] = float(intree.area)
            amp[0] = float(intree.amp)
            width[0] = float(intree.width)
            keV[0] = float(intree.keV)
            nP[0] = float(intree.nP)
            tree.Fill()
           # print("filling up my tree")
        else:
            intree.GetEntry()
        prevEvt = evt
        count+=1
     #   if count>15000:
      #      break
    
    tree.Print()
    cleanRun.cd()
    tree.Write()
    cleanRun.Close()
    
def getDuplicates(lst):
    unique_rows = set()
    duplicate_rows = []
    uniques = []
    for row in lst:
        run = row[0]
        dirpi = row[2]
       # if not hasDataOnCms(dirpi, run):
        #    print("skipping empty run: ", run)
         #   continue
        last_two_elements = row[-2:]  # Get the last two elements of the row
        row_tuple = tuple(last_two_elements)
        if row_tuple in unique_rows:
            duplicate_rows.append(row)
            duplicate_rows.append(next(filter(lambda x: tuple(x[-2:]) == row_tuple, lst)))
        else:
            unique_rows.add(row_tuple)
            uniques.append(row)
    return duplicate_rows, uniques

def combineRuns(lists, runList, memoryDepth=65536):
    config = configparser.ConfigParser()
    for lst in lists:
        #open a new .root file
        dirpi = lst[0]
        dirpiNRun = [lst[1][0], dirpi]
        firstRun = 0
        for row in reversed(runList):
            if row[-2:] == dirpiNRun:
                firstRun = row[0]
       # comboRun = r.TFile("Run"+firstRun+"_combined.root", "RECREATE")
    #      mTree = r.TTree("merged","merged")
        cmd ="hadd -f "+dir+"Run"+str(firstRun)+"_combined.root "
        run=0
        for drun in lst[1]:
            dirpiNRun = [drun, dirpi]
            for row in reversed(runList):
                if row[-2:] == dirpiNRun:
                    run = row[0]
                else:
                    continue
            #run = next(filter(lambda x: tuple(x[-2:]) == dirpiNRun, lst[1]))
            file = dir+"Run"+str(run)+"_config.ini"
            print(file)
            config.read(file)
            print(run)
            depth = int(config["data"]["memory_depth"])
            print ("memory depth: ", depth)
            if depth == memoryDepth:
                print ("found global run:", run ," ", drun, " ",dirpi)
                cmd+=dir+"run"+str(run)+"_pulses.root "
       #     infile = r.TFile(dir +"Run"+str(run)+"_pulses.root", "READ")
       #     intree = infile.Get("pulses")
       #     tlist.Add(intree)
       # mTree = r.TTree.MergeTrees(tlist)
       # comboRun.Write(tlist)
        os.system(cmd)
'''
def getLYSOCal(templateRun, testRun, keV2ADC = 10):
#make histograms with fits, find scaling parameter between template and test, get keV calibration from that
    h1, h2 = getLYSOSpectra(templateRun)
    h3, h4 = getLYSOSpectra(testRun)
    minemd1 = compHists(h1, h3)
    minemd2 = compHists(h2, h4)
    for alpha in np.linspace(0.5, 2, 0.001):
        emd1 = compHists(h1, h3, alpha)
        emd2 = compHists(h2, h4, alpha)
        if emd1 < minemd1:
            minemd1 = emd1
            minAlpha1 = alpha
        if emd2 < minemd2:
            minemd2 = emd2
            minAlpha2 = alpha
    #also want to plot histograms
    #get keV/ADC value
    keV = keV2ADC / alpha
    return minAlpha1, minAlpha2, keVADC
    '''

def getLYSOspectrum(tree, name, xscale = 1.0):
    h = r.TH1F(name,";Energy (keV); Counts [a.u.]", 600, 0, 4000)
    for evt in tree:
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
        keV = tree.keV * xscale
        tBetweenEvents = tree.tBetweenEvents
        if coinc == 1 and ch == 1 :
            h.Fill(keV)
    return h

def getLYSOCal(tree, testTree, nSteps = 40):
    h = getLYSOspectrum(tree, "h")
    h.Draw()
    maxKolmogorov = 0
    bestScale = 0
    for i in range (nSteps):
        xscale = pow(1.2, float(i)/float(nSteps)  * 2.0 - 1.0)
        ht = getLYSOspectrum(testTree, "ht"+str(i), xscale)
        ht.Draw()
        Kolm = h.KolmogorovTest(ht)
        if Kolm > maxKolmogorov:
            maxKolmogorov = Kolm
            bestScale = xscale
    return bestScale, maxKolmogorov, h, ht
    
def compHists(h1, h2, alpha = 1.0):
    sum = 0
    nBins = h1.GetNbinsX()
    nBins2 = h2.GetNbinsX()
    #scaling for number of entries
    h1.Scale(float(1./h1.GetEntries() ) )
    h2.Scale(float(1./h2.GetEntries() ) )

    if nBins != nBins2:
      print("Histograms have different numbers of bins! Exiting...")
      return -999
      
    for i in range(nBins):
      x1 = h1.GetBinContent(i)* alpha
      x2 =  h2.GetBinContent(i)
      diff = x1 - x2
      if x1+x2==0:continue
      sum = sum + pow(diff*diff,0.5)/(x1+x2)
    return sum

def getTemplateSpect():
    file = r.TFile.Open(templateRun, "READ")
    t = file.Get("pulses")
    #fill histogram for template
    c = r.TCanvas()
    i = -1
    i2 = 0
    h1 = r.TH1F("h",";Pulse amplitude [ADC]; Scaled counts", 256, 0, 255)
    h2 = r.TH1F("h",";Pulse amplitude [ADC]; Scaled counts", 256, 0, 255)
    for entry in t: #while(true)
        i += 1
        i2 = i+1
        if t.nPulses == 2:
            t.GetEntry(i)
            amp1 = t.amp
            ch1= t.ch
            t.GetEntry(i2)
            amp2 = t.amp
            ch2 = t.ch
            if amp1 >thresh and amp2 > thresh and ch1 ==1 and ch2 ==2:
                #yay looks like a good calibration event
                h1.Fill("amp1")
                h2.Fill("amp2")
    return h1, h2
#ok, those are the template spectra
#now get the same spectra from the run of interest


#def getLYSOCal(defaultRun, testRun):
#make histograms with fits, find scaling parameter between template and test, get keV calibration from that

def makePlots(run, dir = "./plots", tick = 50. / 1000.):
    #open the .root file, get tree
    f = r.TFile.Open(run,"READ")
    t = f.Get("pulses")

    entries = t.GetEntries()
    t.GetEntry(entries-1)
    nEvt = t.evt
    duration = t.tin
    prefix = str(run).split("/")[-1].split(".")[0]
    runX = prefix.split("_")[0]
    os.system("mkdir "+str(dir)+"/"+str(runX))
    plotDir = str(dir)+"/"+str(runX)+"/"
    print("the prefix is ", prefix )
    # v vs t colz to check for out of time rf triggers
    hT = r.TH1F("hT", ";pulse time [us];", 200, 0, 100 )
    h1 =  r.TH1F("h1", ";pulse amp [ADC];", 256, 0 , 255 )
    h2 =  r.TH1F("h2", ";pulse amp [ADC];", 256, 0 , 255 )
    hevt =  r.TH1F("hevt", ";event;", 100, 0, nEvt)
    htPevt =  r.TH2F("htPevt", "; event;", 100, 0 , nEvt, 200, 0 , 100, )
    h1evt =  r.TH2F("h1evt", ";Event;Ch1 Pulse Amplitude [ADC]", 100, 0 , nEvt, 256, 0 , 255 )
    h2evt =  r.TH2F("hwevt", ";Event;Ch2 Pulse Amplitude [ADC]", 100, 0 , nEvt, 256, 0 , 255 )
    hkeV = r.TH1F("hkeV", ";Energy (keV);", 100, 50,2000)
    hkeVhi = r.TH1F("hkeVhi", ";Energy (keV);", 100, 100,2000)
    hLYSO =  r.TH1F("hLYSO", ";Area (nV*S);", 200, 0,4e3)
    htin =  r.TH1F("htin", ";t[s];", 200, 0, duration)
    l=[]
    nbins=200
    #for i in range(10):
     #   l.append( r.TH1F("ht"+str(i)+"00", ";t[s];", 100, 0, duration) )
    l.append( r.TH1F("ht100", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht200", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht300", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht400", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht500", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht600", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht700", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht800", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht900", ";t[s];", nbins, 0, duration) )
    l.append( r.TH1F("ht1000", ";t[s];", nbins, 0, duration) )
    print("list appended")
    netEvt = 0
    prevEvt = 0
    for entry in t:
        tP =t.tP * tick
        evt=t.evt
        evt2=t.evt
        tin=t.tin
      #  evt = t.evt2
        amp = t.amp
        ch = t.ch
        keV = t.keV
        coinc = t.coinc
        hT.Fill(tP)
        area = t.area
        if ch == 1:
            if coinc == 0:
                h1.Fill(amp)
                h1evt.Fill(evt2, amp)
                hkeV.Fill(keV)
                energy = math.floor(keV/200)
                htin.Fill(tin)
                if energy>9:
                    energy=9
                l[energy].Fill(tin)
                if keV > 1400 and keV < 2000:
                    hkeVhi.Fill(keV)
            if coinc == 1:
             hLYSO.Fill(area)
        if ch ==2:
            h2.Fill(amp)
            h2evt.Fill(evt2, amp)
        hevt.Fill(evt2)
        htPevt.Fill(evt2, tP)
        #if number of pulses is 1, do LYSO stuff
    print("loop finished")
    can = r.TCanvas()
    hT.Draw()
    savePlots(can, plotDir, prefix+"_tP")
    h1.Draw()
    savePlots(can, plotDir, prefix+"_amp1")
    h2.Draw()
    savePlots(can, plotDir, prefix+"_amp2")
    htPevt.Draw("colz")
    savePlots(can, plotDir, prefix+"_tPevt")
    hevt.Draw()
    savePlots(can, plotDir, prefix+"_evt")
    h1evt.Draw("colz")
    savePlots(can, plotDir, prefix+"_amp1evt")
    
    #fitting for 480 keV peak
    r.gStyle.SetOptFit(1)
    f2 = r.TF1("f2","gaus(0)+expo(3)", 350, 600 )
    f2.SetParLimits(0,1000, 8000)
    f2.SetParLimits(1,460, 500)
    f2.SetParLimits(2,10, 100)
    f2.SetRange(350, 700)
    hkeV.Fit("f2", "R")
    hkeV.GetXaxis().SetTitle("Energy (keV)")
    savePlots(can, plotDir, prefix+"_keV1")
    
    r.gStyle.SetOptStat(1)
    hkeVhi.Draw()
    savePlots(can, plotDir, prefix+"_keV1hi")
    
    r.gStyle.SetOptStat(1)
    hLYSO.Draw()
    savePlots(can, plotDir, prefix+"_LYSO")
    
    htin.Draw()
    can.SetLogy(1)
    can.SaveAs(plotDir+prefix+"_tin.png")
    can.SaveAs(plotDir+prefix+"_tin.pdf")
    can.SaveAs(plotDir+prefix+"_tin.C")
  #  can.SetLogy(0)
    #savePlots(can, prefix, prefix+"_tin")
    leg = r.TLegend(0.6, 0.35, 0.85, 0.85 )
    for i in range(10):
        l[i].Draw("")
        savePlots(can, plotDir, prefix+"_tin_"+str( (i+1) *2 )+"00keV")

    for i in range(10):
        l[i].SetLineColor(colors[i])
        l[i].SetMinimum(1)
        leg.AddEntry(l[i], str((i+1)*200)+" keV")
        if i ==0:
            l[i].Draw("")
        else:
            l[i].Draw("same")
    leg.Draw()
    savePlots(can, plotDir, prefix+"_tin_"+"summary")
 #   t.Draw("amp:evt2>>h2(200)","","colz")
 #   can.Update()
 #   can.SaveAs(plotDir+"/"+prefix+"_ampevt")
    
    #lyso cal included here
    #npulses vs evt/time
def savePlots(canvas, plotDir, prefix):
    canvas.SaveAs(plotDir+"/"+prefix+".png")
    canvas.SaveAs(plotDir+"/"+prefix+".pdf")
    canvas.SaveAs(plotDir+"/"+prefix+".C")
    return 0

def trimEmptyRuns(runList, remote=False):
    import paramiko

    # SSH connection details
    print("going")
    hostname = 'tau.physics.ucsb.edu'
    port = 22
    username = 'pmfreeman'
    password = ''
    if remote:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
            # Automatically add the server's host key (uncomment the line below if necessary)
            # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connect to the remote host
        client.connect(hostname, port, username, password)

            # Open an SFTP session on the SSH connection
        sftp = client.open_sftp()
    # Remote directory path
    for row in runList:
        dirpi = str(row[2])
        run = str(row[0])
        remote_directory = '/net/cms26/cms26r0/pmfreeman/XRD/DiRPi_v3/dirpi'+str(dirpi)+'/Run'+str(run)
        print(remote_directory)
        command = f"[ -d '{remote_directory}' ] && echo 'Directory exists'"
        if remote:
            stdin, stdout, stderr = client.exec_command(command)
        else:
            stdin, stdout, stderr = os.system(command)
        output = stdout.read().decode().strip()
        # Return True if the directory exists, False otherwise
        if output == 'Directory exists':
        # List the contents of the remote directory
            if remote:
                directory_contents = sftp.listdir(remote_directory)
            else:
                directory_contents = os.listdir(remote_directory)
            # Print the directory contents
            count=0
            for item in directory_contents:
                print(item)
                count+=1
                break
            if count==0:
                runList.remove(row)
        else:
            runList.remove(row)
            print("removing empty run ",row[0]," from list")
    # Close the SFTP session and the SSH connection
    sftp.close()
    client.close()
    return runList
#oh fuck anything involving ssh?

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='measure some beam currents')
  parser.add_argument('-f', '--first', help='first (global) run number',type=int, default = 33300 )
  parser.add_argument('-l', '--last', help='last (global) run number ',type=int, default = 40000 )
  parser.add_argument('-t', '--noTrees', action ='store_true', help = 'use this option to turn off tree making' )
  parser.add_argument('-p', '--noPlots', action ='store_true',  help = 'use this option to turn off plotting')
  
  args = parser.parse_args()
  first = args.first
  last = args.last
  noTrees = args.noTrees
  noPlots = args.noPlots
  runs = [8312, 8313] # [8122, 8123, 8124, 8125, 8126]#8116, 8117, 8118, 8119, 8120]
  dir = './pulse_data/'
  exceptions = []
 # f = open("DiRPiRuns.txt","w")
  runList = getRunList(first, last)
  #print ("runlist: ")
#  print(runList)
  dictList = []
  [duplicates, uniques] = getDuplicates(runList)
 
  print("duplicates:")
  for row in duplicates:
    print(row[1], row[2], row[0])
  
  print("uniques:")
  for row in uniques:
    print(row[1], row[2], row[0])
  runList = uniques
  # make .root files for runs in runlist
  count = 0
  
  for run in runList:
    url = "http://cms2.physics.ucsb.edu/DRS/Run"+str(run[0])+"/Run"+str(run[0])+"_dirpipulses.ant"
    dirpi = str(run[2])
    try:
        downloadAnt(str(run[0]), url, dir)
        downloadConfig(str(run[0]), dirpi, dir)
        file = dir +'Run'+str(run[0])+'_dirpipulses.ant'
        rfile = dir +'Run'+str(run[0])+'_dirpipulses.root'
        output = dir +'Run'+str(run[0])+'_dirpipulses.root'
        if not noTrees:
          #  print("test")
            makeTree(file, output)
        if not  noPlots:
            makePlots(output)
        #countPulses(rfile)/plots/230703225358_68513.gif
    except:
        print("skipping run "+ str(run[0]))
        print (url)
        exceptions.append(run)
    count+=1
   # cleanRun(output, -10000, 70000)
    
  print("the list of exceptions: ",exceptions)
 
 
 
  #combine runs as noted in spreadsheet
  '''
  runLists = [
 # [264,279],
  [1, [i for i in range(245, 277)] ],
  [8, [313,314] ],
  [8, [300,294,288,282,276,270,264,258,252,246] ],
  #  [5, [i for i in range(50, 59)] ]
  ]
  
#  combineRuns(runLists,runList)
      #clean the RF runs
    #for run in combined runs:
     #   cleanRun(run)
  
  runListsCrocker = [
 # [264,279],
#  [1, [i for i in range(245, 277)] ],
#  [8, [313,314] ],
#  [8, [300,294,288,282,276,270,264,258,252,246] ],
    [5, [i for i in range(297, 316)] ]
  ]
  combineRuns(runListsCrocker,runList, 4096)
#  for run in
  cleanRun(run, -10000, 10000)
 #now make the plots
    
'''
   # lines =ant.split("\n")
    #parsed = []
    #for line in lines:
    #    pline = line.split(" ")
    #    parsed.append(line)
   



'''
#fitting routine:

pulses->Draw("keV>>h2(100, 100, 2000)","ch==1")
auto f2 = new TF1("f2","gaus(0)+expo(3)", 350, 700 )
f2->SetParLimits(0,50, 1000)
f2->SetParLimits(1,460, 500)
f2->SetParLimits(2,10, 100)
f2->SetRange(300, 700)
h2->Fit("f2", "R")
h2->GetXaxis()->SetTitle("Energy (keV)")




pulses->Draw("keV:evt>>h2(100, 0, 55e3, 50, 0, 1500","ch==1","colz")
h2->SetTitle("Beam Pulses")
h2->GetXaxis()->SetTitle("Event")
h2->GetYaxis()->SetTitle("Energy (keV)")

'''
'''
def getNbeam(start=0, stop=1000, run = "Run33362", energyCut=1800):
    dir = "./pulse_data/"
    file =r.TFile.Open(dir+run+"_dirpipulses.root","READ")
    t=file.Get("pulses")
    h = r.TH1F("h",";Pulse energy (keV); Counts", 256, 0, 4000)
    hE = r.TH1F("hE",";Pulse energy (keV); Counts", 256, 0, 4000)
    hPE = r.TH1F("hPE",";Pulse energy (keV); Counts", 256, 0, 4000)
    hP = r.TH1F("hP",";Pulse energy (keV); Counts", 256, 0, 4000)
    
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
    savePlots(can, "./plots/"+run, "pulseCount_evt_"+str(stop))
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
'''
'''
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
'''
'''
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

#dirpi5, Run33478
pairs = [
[88000 , 100000],
[105000, 240000],
[250000, 400000],
]

run="Run33478"
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
'''
