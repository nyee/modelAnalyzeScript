#!/usr/bin/env python
# encoding: utf-8
"""
This script is used to convert the averaged pressure history into volume history.
Peng Zhang
Nov-16-2016
"""

import csv
import os
import math

def computeGamma(T, molarDict):

	spcList = ['N2', 'MF', 'AR', 'O2', 'iOctane', 'nHeptane']
	for spc in spcList:
		if spc not in molarDict:
			molarDict[spc] = 0
		else:
			assert molarDict[spc] >= 0

	if T > 1000:
		N2 = 2.95257626 +1.39690057E-3*T -4.92631691E-7*T**2 +7.86010367E-11*T**3 -4.60755321E-15*T**4
		O2 = 3.66096083 +6.56365523E-4*T -1.41149485E-7*T**2 +2.05797658E-11*T**3 -1.29913248E-15*T**4
	else:
		N2 = 3.53100528 -1.23660987E-4*T -5.02999437E-7*T**2 +2.43530612E-09*T**3 -1.40881235E-12*T**4
		O2 = 3.78245636 -2.99673415E-3*T +9.84730200E-6*T**2 -9.68129508E-09*T**3 +3.24372836E-12*T**4

	if T > 1391:
		nHeptane = 2.22148969E+01 +3.47675750E-02*T -1.18407129E-05*T**2 +1.83298478E-09*T**3 -1.06130266E-13*T**4
	else:
		nHeptane =-1.26836187E+00 +8.54355820E-02*T -5.25346786E-05*T**2 +1.62945721E-08*T**3 -2.02394925E-12*T**4

	if T > 1396:
		iOctane = 2.71373590E+01 +3.79004890E-02*T -1.29437358E-05*T**2 +2.00760372E-09*T**3 -1.16400580E-13*T**4
	else:
		iOctane =-4.20868893E+00 +1.11440581E-01*T -7.91346582E-05*T**2 +2.92406242E-08*T**3 -4.43743191E-12*T**4

	if T > 1386:
		MF = 8.83721102E+00 +1.18067858E-02*T -4.33048364E-06*T**2 +6.97279519E-10*T**3 -4.12494798E-14*T**4
	else:
		MF = -4.01347389E-01 +3.26807673E-02*T -2.24733349E-05*T**2 +7.97426097E-09*T**3 -1.18353141E-12*T**4

	AR = 2.5

	R=8.31451 # Universal gas constant. Unit: J/(mol-K)

	Cp = (molarDict['N2']*N2 + 
		molarDict['O2']*O2 + 
		molarDict['AR']*AR + 
		molarDict['MF']*MF +
		molarDict['iOctane']*iOctane + 
		molarDict['nHeptane']*nHeptane ) *R
	Cv = Cp - R

	return Cp/Cv

def computeTcCR(T0, P_ratio, molarDict):
	dT = 0.01 # Define the temperature step used in integral.
	T_temp = T0
	calcTc = 0
	calcCR = 0

	while calcTc < math.log(P_ratio):
		gamma = computeGamma(T_temp, molarDict)
		calcTc += gamma/(gamma-1)/T_temp*dT
		calcCR += 1.0/(gamma-1)/T_temp*dT
		T_temp += dT

	# Return Tc and CR
	return T_temp, math.exp(calcCR)

def computeTemperatureVolumeHistory(T0, P0, Plist, molarDict):
	P0 = float(P0)
	Tlist = []
	Vlist = []

	i =0
	for P in Plist:
		i+=1
		print i
		T_temp, CR_temp = computeTcCR(T0, P/P0, molarDict)
		Tlist.append(T_temp)
		Vlist.append(1./CR_temp)

	return Tlist, Vlist

def computeCFRVolumeHistory(T0, P0, filename, molarDict):
	# Use computeTemperatureVolumeHistory to compute volume history. Then set the volume at TDC as 1.
	rpm = 599
	startCAD = -146
	endCAD = 100

	cad2sec = 1./6/rpm

	with open(filename, 'r') as f:
		stream = f.readlines()
	
	for i in range(len(stream)):
		stream[i] = stream[i].split(',')

	if stream[0][0] == 'CAD' and stream[0][1] == 'p_avg':
		stream.pop(0)
		cad = map(float, [i[0] for i in stream])
		p_avg = map(float, [i[1] for i in stream])
		
	cad_abs = [abs(i) for i in cad]
	indexTDC = cad_abs.index(min(cad_abs))

	if cad_abs[indexTDC]<1e-4:
		indexList = [10*i+indexTDC for i in range(startCAD, endCAD+1)]
	pList = [p_avg[i] for i in indexList]
	cadList = [cad[i] for i in indexList]

	Tlist, Vlist = computeTemperatureVolumeHistory(T0, P0, pList, molarDict)
	vTDC = Vlist[abs(startCAD)+1]
	Vlist = [Vlist[i]/vTDC for i in range(len(Vlist))]
	with open('Vhistory.csv', 'w') as f:
		writer = csv.writer(f, delimiter = ',', lineterminator='\n')
		writer.writerow(['time/ms', 'CAD', 'V', 'p_avg', 'T'])
		for i in range(len(cadList)):
			writer.writerow([(cadList[i]-cadList[0])*cad2sec*1000, cadList[i], Vlist[i], pList[i], Tlist[i]])

################################################################################
if __name__ == '__main__':
	
	# Please input molar concentration.
	T0 = 325 	# K
	P0 = 1.08943 	# bar / CR = 9.212, P0 = 1.08943 / CR = 6.821, P0 = 1.088942
	# Pc = 12.03		# bar
	molarDict = {
		'iOctane': 	1,
		'nHeptane': 0,
		'N2':		47, 
		'O2':		12.5 }
	
	molarSum = float(sum(molarDict.values()))
	if abs(molarSum-1) > 1e-4:
		print 'Warning: The sum of the initial concentrations is not 1... Try to normalize the concentrations...'
		for key in molarDict:
			molarDict[key] = molarDict[key]/molarSum
		print molarDict

	# print computeTcCR(T0, Pc/P0, molarDict)
	# print computeTemperatureVolumeHistory(T0, P0, [Pc, Pc], molarDict)
	print computeCFRVolumeHistory(T0, P0, 'cad_Pavg_1cycle.csv', molarDict)
