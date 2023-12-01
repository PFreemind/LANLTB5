import os
import beamCurrents as bc
import ROOT as r
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-t', '--trees', action ='store_true', help = 'bool for making ROOT trees' )
args = parser.parse_args()
trees = args.trees

r.gROOT.SetBatch(True)

parts = [3,10,20,50]# 3, 10, 20, 30, 50, 100]
runs = [
"33362", #sept 7 dedicated running
#"50064",
#"46903",
#"48743",
#"49049",
#"49074",
#"49438",
#"49504",
#"50011",
#"50112",
#"33478", #10 pA run
#"33498"  #longer 10 pA run
]
jobs = []



for part in parts:
    for run in runs:
        cmd = "python3.10 beamCurrents.py -r "+str(run)+" -e 1500  -n "+str(part)+" -b"
        print(cmd)
        jobs.append(cmd)
        if trees:
            os.system(cmd)

for run in runs:
    bc.plotSigmaCurves(parts,run)

print("completed jobs: ")
for job in jobs:
    print(job)
    
    
