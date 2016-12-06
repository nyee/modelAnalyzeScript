#!/usr/bin/env python
# encoding: utf-8

"""
This script is used to extract ignition delay times from failed chemkin jobs.
Because of the stiffness of some models, chemkin jobs could get stuck around ignition.
Sometimes loose atol or rtol could solve this problem but sometimes not.
However chemkin did save all the intermediate steps information before it failed.
Ignition delay times could be derived from these information if chemkin did run enough long time.

P.Z.
Dec-5-2016
"""

import os

def readSingleStepSolution(singleStepSolution):
    solutionTimeFlag = 'DDASPK Transient Solution at Time =   '
    solutionTemperatureFlag = 'TEMPERATURE                     '
    indexTime = 0
    indexTemp = 0

    time = ''
    try:
        indexTime = singleStepSolution.find(solutionTimeFlag)
        indexTime += len(solutionTimeFlag)
        time = singleStepSolution[indexTime: indexTime+11]
        if singleStepSolution[indexTime+11: indexTime+14] == 'sec':
            time = float(time)*1000 # Convert to ms
        else:
            print 'Please check the time unit {0} in the output file.'.format(singleStepSolution[indexTime+12: indexTime+14])
    except:
        print 'Did not find solution TIME flag! Abandon the data of this time step!'
        return

    if indexTime > 0:
        try:
            indexTemp = singleStepSolution.find(solutionTemperatureFlag)
            indexTemp += len(solutionTemperatureFlag)
            temperature = singleStepSolution[indexTemp: indexTemp+11]
            if singleStepSolution[indexTemp+11: indexTemp+12]=='K':
                temperature = float(temperature)
            else:
                print 'Please check the temperature unit {0} in the output file.'.format(singleStepSolution[indexTemp+11: indexTemp+12])
        except:
            print 'Did not find solution TEMPERATURE flag! Abandon the data of this time step!'
            return

    return time, temperature

def readSolutionBlock(f):

    global singleStepSolutionHeader
    solutionBlockEndFlag = 'THE SPECIFIED END TIME HAS BEEN REACHED'
    singleStepSolutionList = []
    singleStepSolution = f.readline()
    line = f.readline()
    while line!='':
        if line == solutionBlockEndFlag:
            break
        if singleStepSolutionHeader in line:
            singleStepSolutionList.append(singleStepSolution)
            singleStepSolution = ''

        if line: singleStepSolution += line+'\n'

        line = f.readline()

    solutionTimeList = []
    solutionTempList = []
    for singleStepSolution in singleStepSolutionList:
        time, temperature = readSingleStepSolution(singleStepSolution)
        solutionTimeList.append(time)
        solutionTempList.append(temperature)

    return solutionTimeList, solutionTempList

def deriveIgnitionDelayTime(times, temperatures):
    # Derive ignition delay time based on the 800 K increase in temperature.
    assert len(times) == len(temperatures)
    diffT = [abs(T-800-temperatures[0]) for T in temperatures]
    return temperatures[0], times[diffT.index(min(diffT))]

# Previously tried to use maximum dT/dt definition. It's a little tricky to avoid zero division. 
# So I decided to shift the definition to the temperature increase. 
#    for i in range(len(times)-1):
#        #if temperatures[i]<2000:
#        if (times[i+1]-times[i]) != 0:
#            dTdt.append((temperatures[i+1]-temperatures[i])/(times[i+1]-times[i]))
#        else:
#            print 'Jump zero division', temperatures[i]
#
#        if temperatures[i]>=2000:
#            if abs(times(dTdt.index(max(dTdt))) - times[i]) < 0.1:
#                return times[i]
#    else:
#        return times(dTdt.index(max(dTdt)))

def processSingleOutFile(outFileName):

    global singleStepSolutionHeader

    singleStepSolutionHeader = 'PSPRNT: Printing of current solution from DDASPK:'

    with open(outFileName, 'r') as f:
        line0 = f.readline()
        while line0 != '':
            if singleStepSolutionHeader in line0:
                f.seek(-len(line0), 1)
                times, temperatures = readSolutionBlock(f)
                T0, ID = deriveIgnitionDelayTime(times, temperatures)
            line0 = f.readline()

    return T0, ID

def searchOutFiles():
    cwd = os.getcwd()
    outFiles = []
    for roots, dirs, files in os.walk(cwd):
        for filename in files: 
            if filename.endswith('.out'):
                outFiles.append(os.path.join(roots, filename))
    return outFiles

################################################################################
if __name__ == '__main__':
    
    T0s = [] # Initial temperature
    IDs = [] # Ignition delay
    outFiles = searchOutFiles()
    print '\n'.join(outFiles)
    for outFile in outFiles:
        T0, ID = processSingleOutFile(outFile)
        T0s.append(T0)
        IDs.append(ID)

    # Sort T0s and IDs
    T0s, IDs = (list(x) for x in zip(*sorted(zip(T0s, IDs))))

    # Write T0s and IDs into a file
    outputFile = 'IgnitionDelay.txt'
    with open(outputFile, 'w') as f:
        for i in range(len(T0s)):
            f.write(str(T0s[i])+ ', '+ str(IDs[i]) + '\n')
    
    print 'Finished!'
    