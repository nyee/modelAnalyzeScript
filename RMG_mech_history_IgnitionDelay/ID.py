"""
Constant-pressure, adiabatic kinetics simulation.
"""

import sys
import os
import csv
import numpy as np
import cantera as ct
# os.system('cheminp2xml.bat')
if os.path.isfile('output.csv'):
	f0= open('output.csv','a')
	csvfile_ign = csv.writer(f0,
								 delimiter=',', lineterminator='\n')
else:
	f0= open('output.csv','w')
	csvfile_ign = csv.writer(f0, delimiter=',', lineterminator='\n')
	csvfile_ign.writerow(['RXN','RXN_INDEX','P','T','A-MULTI','IDT_MAX_DP/DT'])
# Reaction 1-6296
# 
index_list = list(range(1,2))
P_list = [20]
T_list = list(range(800,825,25))
for P_eff in P_list:
	for T_eff in T_list:
		for index_reaction in index_list:
			gas = ct.Solution('chem_annotated.cti')
			air = ct.Solution('air.xml')
			gas.TPX = T_eff, P_eff*1e5, 'C8H10O(1):1, butane(5):9, O2(2):68.5, N2:274'
			r = ct.IdealGasReactor(gas)
			env = ct.Reservoir(air)
			factor = 1
			gas.set_multiplier(factor,index_reaction-1)
			
			w = ct.Wall(r, env)
			w.expansion_rate_coeff = 0.0  # set expansion parameter. dV/dt = KA(P_1 - P_2)
			w.area = 1.0

			t_end = 1
			dt = 1.e-6
			n_steps = int(t_end/dt)
			sim = ct.ReactorNet([r])
			time = 0.0
			n_species = 4
			data = np.zeros((n_steps,n_species))
			N_plot = 0
			for n in range(n_steps):
				time += dt
				p_old = r.thermo.P
				sim.advance(time)
				data[n-1,0] = time   # time in ms
				data[n-1,1] = r.T
				data[n-1,2] = r.thermo.P/100000
				data[n-1,3] = (r.thermo.P - p_old)/dt
				# print(sim.time*1000,r.thermo.P/100000,r.T)
				N_plot = N_plot + 1
				if r.T > T_eff + 800:
					break
				# print('%10.3e %10.3f %10.3f '%(sim.time,r.T, r.thermo.P/1E5))
			indices = np.argmax(data[:,3])

			if r.T > T_eff+800:
				ignition = indices*dt*1000
				print('P=%.2f [bar] T=%.2f [K] Ignition Delay = %.2f [ms]'%(P_eff,T_eff,ignition))
				T_inv = 1000./T_eff
				csvfile_ign.writerow([gas.reaction_equation(index_reaction-1),index_reaction,P_eff,T_eff,factor,ignition])
			else:
				csvfile_ign.writerow([gas.reaction_equation(index_reaction-1),index_reaction,P_eff,T_eff,factor,'*'])				
f0.close()
	
