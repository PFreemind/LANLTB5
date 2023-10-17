import os
import beamCurrents as bc

parts = [ 1,3]# 3, 10, 30, 100]
runs = [
"33362", #sept 7 dedicated running
#"33478", #10 pA run
#"33498"  #longer 10 pA run
]
jobs = []



for part in parts:
    for run in runs:
          cmd = "python3.10 beamCurrents.py -r "+str(run)+" -e 1500  -n "+str(part)
          print(cmd)
          jobs.append(cmd)
          os.system(cmd)
          
bc.plotSigmaCurves(parts,run)
print("the run/completed jobs:")
for job in jobs:
    print(job)
    
    
