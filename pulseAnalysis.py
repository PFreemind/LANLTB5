import ROOT as r
import numpy as np
from array import array
import requests
import os
import configparser

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
  
  t.Branch("nP", nP, "nP/F")
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
    nP[0] = (float(val[3]) )
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
    
def downloadAnt(run, url, dir = './pulse_data/'):
    resp = requests.get(url)
    ant = resp.text
    f = open(dir+"Run"+str(run)+"_pulses.ant","w")
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

def getRunList(start = 7000, stop = 21000):
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
    if (run>start and run<stop and ( dirpi == 5) and run not in exceptions and not (run>7536 and run<7562) ): #dirpi == 1 or dirpi == 7 or dirpi == 8 or dirpi == 9 or
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
      
    tree.Branch("nP", nP, "nP/F")
    tree.Branch("evt", evtb, "evt/F")
    tree.Branch("evt2", evtb2, "evt2/F")
    tree.Branch("ch", ch, "ch/F")
    tree.Branch("tP", tP, "tP/F")
    tree.Branch("area", area, "area/F")
    tree.Branch("amp", amp, "amp/F")
    tree.Branch("width", width, "width/F")
    tree.Branch("keV", keV, "keV/F")
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
    nEvt = t.evt2
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

    netEvt = 0
    prevEvt = 0
    for entry in t:
        tP =t.tP * tick
        evt=t.evt
        evt2=t.evt2
      #  evt = t.evt2
        amp = t.amp
        ch = t.ch
        hT.Fill(tP)
        if ch ==1:
            h1.Fill(amp)
            h1evt.Fill(evt2, amp)
        if ch ==2:
            h2.Fill(amp)
            h2evt.Fill(evt2, amp)
        hevt.Fill(evt2)
        htPevt.Fill(evt2, tP)
        #if number of pulses is 1, do LYSO stuff
        
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
  runs = [8312, 8313] # [8122, 8123, 8124, 8125, 8126]#8116, 8117, 8118, 8119, 8120]
  dir = './pulse_data/'
  exceptions = []
 # f = open("DiRPiRuns.txt","w")
  runList = getRunList(20000, 21000)
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
  '''
  for run in runList:
    url = "http://cms2.physics.ucsb.edu/DRS/Run"+str(run[0])+"/Run"+str(run[0])+"_pulses.ant"
    dirpi = str(run[2])
    try:
        downloadAnt(str(run[0]), url, dir)
        downloadConfig(str(run[0]), dirpi, dir)
        file = dir +'Run'+str(run[0])+'_pulses.ant'
        rfile = dir +'Run'+str(run[0])+'_pulses.root'
        output = dir +'Run'+str(run[0])+'_pulses.root'
        makeTree(file, output)
     #   countPulses(rfile)/plots/230703225358_68513.gif
    except:
        print("skipping run "+ str(run[0]))
        print (url)
        exceptions.append(run)
    count+=1
  print("the list of exceptions: ",exceptions)
 
 '''
 
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
  '''
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
    

   # lines =ant.split("\n")
    #parsed = []
    #for line in lines:
    #    pline = line.split(" ")
    #    parsed.append(line)
   

