#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
from rmgpy.chemkin import loadChemkinFile
from rmgpy.rmg.model import CoreEdgeReactionModel
from rmgpy.rmg.output import saveOutputHTML
from PIL import Image

resultFolder = 'result'
mechFileInp = 'chem_annotated.inp'
mechFileCti = 'chem_annotated.cti'
spcFile = 'species_dictionary.txt'
mechHTML = 'mech.html'
mechFolder = 'mech'
ignitionDelayFolder = 'ID'
pathwayFolder = 'pathway'
pathwayFile = 'plotRxnPath.py'
spcFolder = 'species'
structureFolder = 'structure'

rmgInputFile = 'input.py'
rmgBatchFile = 'RunRMG'

inp2ctiTool = 'inp2cti'
inp2ctiBatchFile = 'cheminp2xml.bat'

# Rename the 'result' folder to be 'mech' folder
if os.path.exists(resultFolder) and os.path.isfile(os.path.join(resultFolder, mechFileInp)):
	os.rename(resultFolder, mechFolder)

# Move rmg input file and rmg batch file to the 'mech' folder
if os.path.exists(mechFolder) and os.path.isfile(rmgInputFile):
	shutil.move(rmgInputFile, os.path.join(mechFolder, rmgInputFile))
	shutil.move(rmgBatchFile, os.path.join(mechFolder, rmgBatchFile))

# Move inp2ctiTool into the 'mech' folder
if os.path.exists(mechFolder) and os.path.exists(inp2ctiTool):
	shutil.move(inp2ctiTool, mechFolder) 

# Move inp file into inp2ctiTool folder
if os.path.exists(os.path.join(mechFolder, inp2ctiTool)) and os.path.isfile(os.path.join(mechFolder, mechFileInp)):
	shutil.copy(os.path.join(mechFolder, mechFileInp), os.path.join(mechFolder, inp2ctiTool))

# Convert inp to cti
if os.path.isfile(os.path.join(mechFolder, inp2ctiTool, mechFileInp)) and not os.path.isfile(os.path.join(mechFolder, inp2ctiTool, mechFileCti)):
	subprocess.call('cd {0} & dir & {1}'.format(os.path.join(mechFolder, inp2ctiTool), inp2ctiBatchFile), shell=True)

# Correct the misinterpreted elements line in the original cti file
originalCti = os.path.join(mechFolder, inp2ctiTool, mechFileCti)
if os.path.isfile(originalCti):
	with open(originalCti, 'r') as f:
		stream = f.readlines()
	stream[3] = '          elements="H C O N Ne Ar He Si S Cl",\n'
	with open(originalCti, 'w') as f:
		f.writelines(stream)

# Copy the cti file to the root dir
if not os.path.isfile(mechFileCti):
	shutil.copy(originalCti, mechFileCti)

# Create ignition delay calculation folder
if not os.path.exists(ignitionDelayFolder):
	os.makedirs(ignitionDelayFolder)
	shutil.copy(mechFileCti, os.path.join(ignitionDelayFolder,mechFileCti))

# Create pathway calculation folder
if not os.path.exists(pathwayFolder):
	os.makedirs(pathwayFolder)
	shutil.copy(mechFileCti, os.path.join(pathwayFolder,mechFileCti))
	shutil.move(pathwayFile, os.path.join(pathwayFolder,pathwayFile))

# Generate HTML file
if not os.path.isfile(os.path.join(mechFolder, mechHTML)):
	print 'create reaction model...'
	model = CoreEdgeReactionModel()
	print 'load chemkin file...'
	model.core.species, model.core.reactions = loadChemkinFile(os.path.join(mechFolder, mechFileInp), os.path.join(mechFolder, spcFile))
	print 'save HTML file...'
	saveOutputHTML(os.path.join(mechFolder, mechHTML), model)
	print 'finished!'

# Copy the 'species' folder generated during the generation of HTML file to the 'pathway' folder. Rename the copy as 'structure'
structureDir = os.path.join(pathwayFolder, structureFolder)
if not os.path.exists(structureDir):
	shutil.copytree(os.path.join(mechFolder, spcFolder), structureDir)
	for filename in os.listdir(structureDir):
	    if filename.endswith(').png'):
	        filename = os.path.join(structureDir, filename)
	        im = Image.open(filename)
	        # f = 200.0/max(im.width, im.height)
	        f = 3
	        im = im.resize((int(im.width*f), int(im.height*f)))
	        im.save(filename)


