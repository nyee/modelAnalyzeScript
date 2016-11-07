"""
Constant-pressure, adiabatic kinetics simulation.
"""
import os
import shutil

##########################################################################################
# Input Section
numCore = 16 	# Make sure it is even
numStart = 1
numEnd = 4702
mechFile = 'chem_annotated.cti'
calcFile = 'IDT_SENSITIVITY.py'
batchFile = 'RunIDSens'

##########################################################################################
# Generate parameter
numSeg = numCore/2
numRxn = numEnd - numStart + 1
numStep = numRxn/numSeg		# At least in python 2.7, this is integer division
listStart = [0]*numSeg
listEnd = [0]*numSeg

for i in range(1,numSeg+1):
	listStart[i-1] = numStart + (i-1)*numStep
	if i!=numSeg:
		listEnd[i-1] = i*numStep
	else:
		listEnd[i-1] = numEnd

	# Create directories and files
	for j in range(1,3):
		if j==1:
			prefix='05'
		else:
			prefix='2'
		filePath = '/X' + prefix + '_' + str(listStart[i-1]) + '_' +str(listEnd[i-1])
		filePath = os.getcwd() + filePath
		if os.path.exists(filePath):
			print 'Warning: Maybe this case has been calculated!!! Please check!!!'
			break
		else:
			os.makedirs(filePath)

		# Copy mech file to subdirectory
		shutil.copy2(mechFile, filePath)
		
		# Generate calc file
		with open(calcFile,'r') as calcFileFlag:
			dataCalcFile = calcFileFlag.readlines()
		dataCalcFile[16] = 'index_list = list(range(' + str(listStart[i-1]) + ',' + str(listEnd[i-1]+1) + '))\n'
		if prefix=='05':
			dataCalcFile[27] = '			factor = 0.5' + '\n'
		else:
			dataCalcFile[27] = '			factor = 2' + '\n'
		with open(filePath + '/'+ calcFile,'w') as batchCalcFile:
			batchCalcFile.writelines(dataCalcFile)

		# Generate batchjob submission file
		with open(batchFile,'r') as batchFileFlag:
			dataBatchFile = batchFileFlag.readlines()
		dataBatchFile[7] = '#$ -N X' + prefix + '_' + str(i) + 'in' + str(numSeg) + '\n'
		dataBatchFile[8] = 'python ' + calcFile + '\n'
		with open(filePath + '/'+ batchFile,'w') as batchBatchFile:
			batchBatchFile.writelines(dataBatchFile)

		# Submit batch job
		os.chdir(filePath + '/')
		os.system('qsub ' + batchFile)
		os.chdir('..')


