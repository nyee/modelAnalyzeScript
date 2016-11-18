The script 'plotRxnPath.py' in this folder is used to plot the reaction path diagram in a constant volume, adiabatic kinetics simulation.

The simulation is performed using Cantera.

'chem_annotated.cti' is the mech file.

The dir 'structure' contains the species images which could be obtained from an RMG job.

The script 'resizePNGSize.py' could be used to resize the structure images if you find they are not in proper size in the rxn path diagram.


Previously the pathway analysis tool in cantera could generate a rxn pathway diagram with the species labeled with species names. 
It's a boring work to indentify the major species in this diagram.
Here I am trying to replace the text labels with the species images.
Hopefully it will make the model analysis process less painful.

It could be modified to simulate a constant pressure, constant temperature reactor by setting the wall expansion_rate_coeff and heat transfer coeff large enough. 
If you did that, please push it to the RMG/WIP_script repo.

Peng
Nov-14-2016


