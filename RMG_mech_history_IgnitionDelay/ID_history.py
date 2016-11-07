"""
This script is used to calculate the ignition delay of a series mech files generated during RMG running.
It could be used to visulize the variation of the ignition delay with the enlargement of the model.
"""

import sys
import os
import shutil
import subprocess
import csv
#import numpy as np
#import cantera as ct
# os.system('cheminp2xml.bat')

cwd = os.getcwd()
mechPath = os.path.join(cwd, 'mech')
wd = cwd
# wd = os.path.join(cwd, 'wd')
inp2xml = os.path.join(wd, 'cheminp2xml.bat')
#print cwd
#print mechPath

filenames = [filename for filename in os.listdir(mechPath) if filename.endswith('.inp')]
tempInp = os.path.join(wd, 'chem_annotated.inp')
tempCti = os.path.join(wd, 'chem_annotated.cti')
#logFile = 'log_ID_history.txt'
f0= open('filename.csv','w')
csvfile_ign = csv.writer(f0, delimiter=',', lineterminator='\n')

for filename in filenames:
	print filename
	csvfile_ign.writerow([filename])
	filePath = os.path.join(mechPath, filename)
	shutil.copyfile(filePath, tempInp)
	subprocess.call(inp2xml)
	subprocess.call('python ID.py')

	os.remove(tempInp)
	os.remove(tempCti)

f0.close()
