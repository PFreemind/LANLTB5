import pulseAnalysis
import ROOT as r
scalingFactor = 100#to convert from area to keV

colors =[
r.kRed,
r.kBlue+1,
r.kGreen+2,
r.kMagenta,
r.kCyan+2,
r.kBlack+2,
r.kOrange+2,
r.kRed+2,
]
color =[
r.kBlue -10,
r.kBlue ,
r.kBlue -6,
r.kBlack,
]

dir = "./plots"
dataDir = "./pulse_data"
r.gStyle.SetOptStat(0)

def peakPlot(run=8117):
    file = r.TFile.Open(dataDir+'/Run'+str(run)+'_pulses.root', "READ")
    tree = file.Get("pulses")
    can = r.TCanvas()
  #  can.SetLogy(1)
   # print(tree.Print()) #check the tree
    
    hbase = r.TH1F("hbase","Beam spectroscopy;Energy [keV];Entries", 200, 0, 2.5e3)
    hbase.Draw()
    cut =[
    " tP<0e3 ",
    " tP>0  and tP<180e3 ",
    " tP>180e3 ",
    ]
    hbase.SetMaximum(8000)
    h= []
    leg = r.TLegend(0.4, 0.3, 0.8, 0.55)
    labels = [
    "before LBEG",
    "during LBEG",
    "after LBEG",
    ]
    for i in range(3):
        h.append(r.TH1F("h"+str(i),"h"+str(i),200, 0, 2.5e3))

    for entry in tree:
        ch  = tree.ch
        evt = tree.evt
        amp = tree.amp
        area = tree.area
        tP =  tree.tP
        keV = tree.keV
        if tP<=0:
           h[0].Fill(keV)
        if tP>0 and tP<=180e3:
            h[1].Fill(keV)
        if tP>180e3:
            h[2].Fill(keV)
    h[1].Scale(2.2)
    h[2].Scale(1.5)
    for i in range(3):
        print("there are a bunch of entries in tree ",str(i),": ",h[i].GetEntries() )
    #    h[i].Scale(1./h[i].GetEntries())
        leg.AddEntry(h[i], labels[i])
        h[i].SetLineColor(colors[i])
        h[i].Draw("same&&HIST")
           # input()
    leg.Draw()
    can.SaveAs(dir+"/peakPlotRun"+str(run)+".pdf")
    can.SaveAs(dir+"/peakPlotRun"+str(run)+".png")
#    input() #to pause and check the plot while running
    return h

def timePlot():
    can2 = r.TCanvas()
    runs = [8114, 8115, 8116, 8117]
    hbase2 = r.TH1F("hbase2","Pulse times; Pulse time [#mus];Entries/Trigger", 100, -800, 800)
    hbase2.SetMaximum(30)
    hbase2.Draw()
    h = []
    i =0
    leg = r.TLegend(0.18, 0.3, 0.57, 0.6)
    labels = [
    "RF only",
    "1-7 mA (nominal) beam",
    "1 mA (low current) beam",
    "1 mA, 40 MeV beam stop"
    ]
    for run in runs:
        h.append(r.TH1F("h"+str(run),"h"+str(run),100,-800, 800))
    for run in runs:
        file = r.TFile.Open(dataDir+'/Run'+str(run)+'_pulses.root', "READ")
        tree = file.Get("pulses")
        h[i].Print()
        h[i].SetLineColor(color[i])
        for entry in tree:
            h[i].Fill(tree.tP/1000.0)
        h[i].Scale(1.0/tree.evt)
        h[i].Draw("same")
        leg.AddEntry(h[i], labels[i])
        i+=1
    can2.SetLogy(1)
    leg.Draw()
    can2.SaveAs(dir+"/timing plot.pdf")
    can2.SaveAs(dir+"/timing plot.png")
#    input()
    return 0
    
    
calibration_runs = [
6056
]
def selfCal():
    #open runs
    tree = TFile.Open(calibration_runs[0], "READ")
    
    #plot them, with cuts and scale factors
    

if __name__ == "__main__":
    peakPlot()
    timePlot()
