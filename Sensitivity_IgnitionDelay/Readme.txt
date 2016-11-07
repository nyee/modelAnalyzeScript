The scripts in this folder are used to perform brute force sensitivity analysis for ignition delay.
It individually perturbs the A-factor of each reaction and simulates the ignition delay in a closed 0-D system.
In IDT_auto.py, you could input the number of cores that you want to use to speed up the calculation. All the rxns in the range of `numStart` to `numEnd` will be analyzed.
Simulation conditions, including the pressure, temperature, and iniitial concentrations, are specified in IDT_SENSITIVITY.py
Run IDT_auto.py to submit the sub-jobs on pharos.
After finishing the whole job, run postProcSens.py to collect the calculation results from each folder to obtain the final results.

P. Zhang
Nov.7, 2016
One day before the election day.