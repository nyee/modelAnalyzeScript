"""
Constant volume, adiabatic kinetics simulation. Plot rxn path diagram.

Previously the pathway analysis tool in cantera could generate a rxn pathway diagram with the species labeled with
species name. It's a boring work to indentify the major species in this diagram.
Here I am trying to label the species in that diagram with the species structure and SMILES.
Hopefully it will make the model analysis process less painful.
Peng Zhang
Nov-14-2016
"""

import sys
import os
import csv
import numpy as np

import cantera as ct

###########################
# Input section
gas = ct.Solution('chem_annotated.cti') # Input mech file.
air = ct.Solution('air.xml')

P = 20      # Initial pressure. Unit: bar 
T = 700     # Initial temperature. Unit: K
dt = 1e-5   # Time step.
n_steps = int(1.0/dt) # Total time steps. Set the end time long enough. Here we set it to be 1 second. 

gas.TPX = T, P*1e5, 'C8H10O(1):1, butane(5):9, O2(2):68.5, N2:274'  # Mixture composition.
###########################
# Cantera reaction network setting
r = ct.IdealGasReactor(gas)
env = ct.Reservoir(air)
w = ct.Wall(r, env)
w.expansion_rate_coeff = 0.0
w.area = 1.0
sim = ct.ReactorNet([r])
###########################
time = 0.0 # Initialize time
for n in range(n_steps):
    time += dt
    sim.advance(time)
    # print r.T    # Uncomment this line to moniter the calculation progress.

    if r.T > T + 50:
        print 'Initial temperature: {0} K'.format(T)
        print 'End temperature:     {0:.0f} K'.format(r.T)
        print 'End time:            {0} ms'.format(time*1000)
        ###########################################
        # Reaction path diagram setting
        element = 'C'
        diagram = ct.ReactionPathDiagram(gas, element)
        diagram.threshold = 0.05    # Default value is 0.005
        diagram.scale = bool(0)
        diagram.label_threshold = 1/100000000 # For now, I'm not sure what this is used for.
        diagram.show_details = bool(0) # Make it 1 to turn on details.
        ###########################################

        dot_file = 'rxnpath.dot'
        diagram.write_dot(dot_file)
        break
#---------------------------------------------------------------------------------------
# Plot the rxn path diagram and label nodes with spc structures.
dotFileOriginal = dot_file
dotFileNew = 'rxnpath_Structure.dot'    # This is an intermediate file, which will be deleted in the end.
imgFileNew = 'rxnpath_Structure.png'    # This is the rxn path pic. 
structureDir = 'structure'              # This dir stores the structure of the species. 

structureDict = {}
for filename in os.listdir(structureDir):
    if filename.endswith(').png'): 
        fnLeftParentheses = filename.rfind('(')
        fnRightParenthese = filename.rfind(')')
        structureDict[filename[fnLeftParentheses:fnRightParenthese+1]] = filename

with open(dotFileOriginal, 'r') as f:
    stream = f.readlines()
for i in range(len(stream)):
    indexLabel = stream[i].find('label')
    if indexLabel > 0:
        indexLeftQuote = stream[i].find('="', indexLabel)
        indexRightQuote = stream[i].find('"];', indexLabel)
        stripLabelQuote = stream[i][indexLeftQuote+2:indexRightQuote]
        if 'fwd:' not in stripLabelQuote and '(' in stripLabelQuote:
            indexLeftParentheses = stripLabelQuote.find('(')
            indexRightParentheses = stripLabelQuote.find(')')
            spcIndex = stripLabelQuote[indexLeftParentheses: indexRightParentheses+1]
            if spcIndex in structureDict:
                newLabel = """penwidth=0, shape=box, margin=0, label=<<TABLE border="0">
<TR><TD><IMG scale="True" SRC="{0}"/></TD></TR>
<TR><TD>{1}</TD></TR>
</TABLE>>];
""".format(os.path.join(structureDir, structureDict[spcIndex]), stripLabelQuote)
                stream[i] = stream[i][:indexLabel]+newLabel
            else:
                print 'Warning: {0} is not in the structure dictionary! Use the original label.'.format(stripLabelQuote)

with open(dotFileNew, 'w') as f:
    f.writelines(stream)

os.system('dot {0} -Tpng -o{1} -Gdpi=300'.format(dotFileNew, imgFileNew))
print("Wrote output file to '{0}'.".format(imgFileNew))

# Remove the intermediate dot file.
os.remove(dotFileOriginal)
os.remove(dotFileNew)
