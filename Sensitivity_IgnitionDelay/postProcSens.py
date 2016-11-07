"""
Constant-pressure, adiabatic kinetics simulation.
"""

import sys
import os
import csv
import numpy as np
import xlsxwriter

##########################################################################################
# Input Section
numCore = 16 	# Make sure it is even
numStart = 1
numEnd = 4702

##########################################################################################
# Generate parameter
numSeg = numCore/2
numRxn = numEnd - numStart + 1
numStep = numRxn/numSeg		# At least in python 2.7, this is integer division
listStart = [0]*numSeg
listEnd = [0]*numSeg

lineFlag = 0
data = []

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
		filePath = '\X' + prefix + '_' + str(listStart[i-1]) + '_' +str(listEnd[i-1])
		filePath = os.getcwd() + filePath
		if not os.path.exists(filePath):
			print 'Warning: Maybe this case has NOT been calculated!!! Please check!!!'
			break
		else:
			with open(filePath + '\output.csv','rb') as dataFile:
				reader = csv.reader(dataFile)
				
				if j==1:
					for row in reader:
						if row[0] == 'RXN':
							continue
						else:
							data.append(row)
				else:
					for row in reader:
						if row[0] == 'RXN':
							continue
						else:
							if data[lineFlag][0]==row[0]:
								data[lineFlag].append(row[4])
								data[lineFlag].append(row[5])
							else:
								print "ERROR! Something wrong. Please check."
								break
							lineFlag +=1
						
for i in range(0,numRxn):
	data[i][1] = int(data[i][1])
	data[i][2] = float(data[i][2])
	data[i][3] = float(data[i][3])
	data[i][4] = float(data[i][4])
	data[i][5] = float(data[i][5])
	data[i][6] = float(data[i][6])
	data[i][7] = float(data[i][7])
	sens = np.log(float(data[i][5])/float(data[i][7]))/np.log(float(data[i][4])/float(data[i][6]))
	data[i].append(sens)
	data[i].append(abs(sens))

# f0= open('IDSens.csv','w')
# sens_file = csv.writer(f0, delimiter=',', lineterminator='\n')
# sens_file.writerows(data)

workbook = xlsxwriter.Workbook('IDSens.xlsx')
worksheet = workbook.add_worksheet()
row = 0
col = 0


for i in range(0, numRxn):
	for j in range(0, 10):
		worksheet.write(i, j, data[i][j])

workbook.close()


