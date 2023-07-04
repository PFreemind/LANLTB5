import ROOT as r
import numpy as np
from array import array
import requests

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
  amp =  array('f', [0])
  width= array('f', [0])
  NPE =  array('f', [0])
  keV =  array('f', [0])
  
  t.Branch("evt", evt, "evt/F")
  t.Branch("ch", ch, "ch/F")
  t.Branch("tP", tP, "tP/F")
  t.Branch("area", area, "area/F")
  t.Branch("amp", amp, "amp/F")
  t.Branch("width", width, "width/F")
  t.Branch("keV", keV, "keV/F")

  f = open (input,  'r')
  lines = f.readlines()
  count = 0
  for line in lines:
    val = line.split(' ')
  #  print(type(val[0]), val[0])
  #  print(count)
  #  print(val)
    evt[0] = (float(val[0]) )
    ch[0] = int(val[9])
    #stupid hardcoing for 8125
    #if val[11] == '795483.43\x0050':
    #  val[11] ='795483.43'
    tP[0]= float(val[11])
    area[0] = float(val[12])
    amp[0] = float(val[13])
    width[0] = float(val[14])
    keV[0] = float(val[16])
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
    
def downloadAnt(run):
    resp = requests.get(url)
    ant = resp.text
    f = open("Run"+str(run)+"_pulses.ant","w")
    f.write(ant)
  
def getRunList():
  #get list of dirpi runs
    #    parse it for LANL devices/run numbers:
  urlist = "http://cms2.physics.ucsb.edu/DiRPiRuns"
  resp = requests.get(urlist)
  txt = resp.text
  lines = txt.split("\n")
  runList =[]
  exceptions = [7330, 7471, 7495,7502,7522,7525, 7569, 7570, 7667,7673, 7685,7761,7787 ]
  #need a run dictionary
  runDict = {"dirpirun":0, "run":0,"dirpi":1}
  dictList = []
  for line in lines:
    if line =="": continue
    dirpirun   = int(line.split(" ")[0])
    run   = int(line.split(" ")[1])
    dirpi = int(line.split(" ")[2])
   
    dictList.append(runDict)
    if (run>7000 and run<8314 and (dirpi == 1 or dirpi == 7 or dirpi == 8 or dirpi == 9 ) and run not in exceptions and not (run>7536 and run<7562) ):
      runList.append(run)
      runDict["run"]=run
      runDict["dirpi"]=dirpi
      runDict["dirpirun"]=dirpirun
  print (runList)
  return runList, runDict
  
if __name__ == "__main__":
  runs = [8312, 8313] # [8122, 8123, 8124, 8125, 8126]#8116, 8117, 8118, 8119, 8120]
  dir = './'
  
 # f = open("DiRPiRuns.txt","w")
  runList = getRunList()
  # make .root files for runs in runlist
  for run in runList:
    url = "http://cms2.physics.ucsb.edu/DRS/Run"+str(run)+"/Run"+str(run)+"_pulses.ant"
    try:
        downloadAnt(run)
        file = dir +'Run'+str(run)+'_pulses.ant'
        rfile = dir +'Run'+str(run)+'_pulses.root'
        output = dir +'run'+str(run)+'_pulses.root'
        makeTree(file, output)
        countPulses(rfile)
    except:
        print("skipping run "+ str(run))
        exceptions.append(run)
  print("the list of exceptions: ",exceptions)
  #combine runs as noted in spreadsheet
  lists = [
  [264,279],
  [7379,7384,7389]
  ]
    
  for list in lists:
        #open a new .root file
        firstRun = str(list[0])
        comboRun = r.TFile(firstRun+"_combined.root", "RECREATE")
        tree = r.TTree("merged","merged")
        for drun in list:
            
            infile = r.TFile(dir +"Run"+str(run)+"_pulses.root", "READ")
            intree = infile.Get("pulses")
            tree.Merge(tree, intree)
        comboRun.Write(tree)
    

   # lines =ant.split("\n")
    #parsed = []
    #for line in lines:
    #    pline = line.split(" ")
    #    parsed.append(line)
   
