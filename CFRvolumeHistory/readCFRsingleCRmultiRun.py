#!/usr/bin/env python
# encoding: utf-8
"""
This script is used to read the CFR engine RON test experiment pressure history.
Peng Zhang
Nov-16-2016
"""

import csv
import os

###############################################
def readCFRsingleRun(filename):
	cad = []
	p_avg = []
	indexTitleLine = None
	
	with open(filename, 'r') as f:
		stream = f.readlines()
	
	for i in range(len(stream)):
		if indexTitleLine is not None:
			try:
				temp = map(float, stream[i].split('\t'))
				cad.append(temp[0])
				p_avg.append(sum(temp[1:])/(len(temp)-1))
			except:
				print filename, indexTitleLine, i
	
		if stream[i].startswith('%CAD'):
			indexTitleLine = i
			#print filename, i
	
	return cad, p_avg

###############################################
if __name__ == '__main__':

	output = 'output.csv'
	cad = []
	p_avg = []
	identicalCAD = True

	for filename in os.listdir(os.getcwd()):
		if filename.startswith('CFR_20') and filename.endswith('.txt'):
			cad_temp, p_temp = readCFRsingleRun(filename)
			cad.append(cad_temp)
			p_avg.append(p_temp)

	for i in range(len(cad[0])):
		for j in range(len(cad)):
			if cad[j][i] != cad[0][i]:
				print 'ERROR: CAD from Run #0 and #{0} is not identical! Please check the input file!'.format(j)
				identicalCAD = False
				break

	if identicalCAD == True:
		with open(output, 'w') as f:
			writer = csv.writer(f, delimiter = ',', lineterminator='\n')
			title = ['CAD', 'p_avg']
			for i in range(len(p_avg)):
				title += ['p{0}'.format(i+1)]
			writer.writerow(title)

			for i in range(len(cad[0])):
				p_i_list = [p[i] for p in p_avg]
				writer.writerow([cad[0][i]] + [sum(p_i_list)/len(p_i_list)] + p_i_list)

