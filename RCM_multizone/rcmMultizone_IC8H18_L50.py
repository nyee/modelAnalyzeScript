"""
Multi-Zone simulation for RCM experiments. Three-zone in this case.
	1) Adiabatic core zone
	2) Boundary layer zone
	3) Crevice zone
Including Mass Transfer and Compression Process
Infinite heat loss for the crevice zone

More assumptions please see the paper below:
First-stage ignition delay in the negative temperature coefficient behavior: Experiment and simulation
http://dx.doi.org/10.1016/j.combustflame.2016.03.002

Credits:
Peng Zhang
Weiqi Ji
Xin He

Last editted by Peng Zhang (zhangpeng13@mails.tinghua.edu.cn / zhangp09@126.com)
Tsinghua Univ.
Center for Combustion Energy - RCM Lab
Dec-01-2016
"""

import sys
import os
import csv
import numpy as np
import cantera as ct
import datetime

starttime = datetime.datetime.now()

######################################################################################################################
# Set the initial condition of the mixture
P = 1.1017E5 # pressure unit: Pa
T = 299.05 # temperature unit: K
mix_comp = 'IC8H18:1, O2:12.5, AR:75' # mixture composition. Molar ratio.

# Input the ic8 model
mixture = ct.Solution('ic8mech.xml')	# Set the state of the reactive mixture
mixture.TPX = T, P, mix_comp
air = ct.Solution('air.xml')

mixture_unr = ct.Solution('ic8mech_unr.xml')	# Set the state of the unreactive mixture
mixture_unr.TPX = T, P, mix_comp

r1 = ct.IdealGasReactor(mixture)	# Set core zone
r2 = ct.IdealGasReactor(mixture_unr)	# Set boundary layer zone
r3 = ct.IdealGasReactor(mixture_unr)	# Set crevice zone

v1 = ct.Valve(r1,r2)			# Add a valve between the main combustion chamber and the boundary layer
v2 = ct.Valve(r2,r3)			# Add a valve between the boundary layer and the crevice

Env = ct.Reservoir(air)			# Set the environment
w1 = ct.Wall(Env, r1)
w2 = ct.Wall(Env, r2)
w3 = ct.Wall(Env, r3)

######################################################################################################################
#

v1.set_valve_coeff(5E-6)  		# Set mass flow rate for valve1
v2.set_valve_coeff(5E-6)  		# Set mass flow rate for valve2

# Set the geometry of the RCM
dia_2 = 50.8E-3 # Diameter of the combustion chamber.
height = 2E-3 # Height of the boundary layer
dia_1 = dia_2 - 2 * height

stroke = 500.E-3 # Stroke of the RCM
cle = 17E-3 + 50.0E-3 # Clearence height of the RCM

area_1 = np.pi / 4 * dia_1 * dia_1
area_2 = np.pi / 4 * (dia_2*dia_2 - dia_1*dia_1)
Awalls = np.pi * dia_2 * (stroke + cle)

r1.volume = area_1 * ( stroke + cle ) - area_1*height*2 # Initial volume of the core zone
r2.volume = area_2 * ( stroke + cle ) + area_1*height*2 # Initial volume of the boundary layer zone
r3.volume = 1.3412E-5 # Volume of the crevice zone. It doesn't change with time

w1.area = area_1
w2.area = area_2
w3.area = 0.00833

h_1 = 0
w1.heat_transfer_coeff = h_1	# Set combustion chamber to be adiabatic

Tw = 300
k_g = air.thermal_conductivity
bl_2 = 0.3E-3
h_2 = k_g / bl_2				# Set heat loss for boundary layer

scale = 1E5
h_3 = k_g * scale
w3.heat_transfer_coeff = h_3	# Set heat loss for crevice

######################################################################################################################
# The piston movement is fitted into five phases.
# Phase1: 0-20 ms accelerate
# Phase2: 20-31 ms accelerate
# Phase3: 31-33 ms decelerate
# Phase4: 33-35.5 ms decelerate
# Phase5: 35.5-335.5 ms stopped
steps_1 = 200
t_1 = 0.020
t_step_1 = t_1/steps_1
steps_2 = 110
t_2 = 0.031
t_step_2 = (t_2 - t_1)/steps_2
steps_3 = 200
t_3 = 0.033
t_step_3 = (t_3 - t_2)/steps_3
steps_4 = 250
t_4 = 0.0355
t_step_4 = (t_4 - t_3)/steps_4
steps_5 = 3000
t_5 = 0.3355
t_step_5 = (t_5 - t_4)/steps_5

# Velocity of the piston
v_1 = ct.Func1(lambda t: 21/20*1000*t )
v_2 = ct.Func1(lambda t: (26.5-21)/11*(t*1000-20)+21 )
v_3 = ct.Func1(lambda t: (26.5 - 1)/2*(33-t*1000)+1 )
v_4 = ct.Func1(lambda t: (35.5-t*1000)/2.5*1 )
v_5 = ct.Func1(lambda t: 0 )

# Heat loss setting for the boundary layer zone. It varies with the wall area.
q_1 = ct.Func1(lambda t: -1/area_2*(r2.T - Tw)*h_2*(2*(area_1+area_2) + Awalls - t*t/0.02*21/2*np.pi*dia_2) )
q_2 = ct.Func1(lambda t: -1/area_2*(r2.T - Tw)*h_2*(2*(area_1+area_2) + Awalls - (0.02*21/2 + (21+((26.5-21)/0.011*(t-0.02))+21)*(t-0.02)/2)*np.pi*dia_2) )
q_3 = ct.Func1(lambda t: -1/area_2*(r2.T - Tw)*h_2*(2*(area_1+area_2) + Awalls - (0.02*21/2 + (21+26.5)*0.011/2 + ( (26.5-1)/0.002*(0.033-t)+1 +26.5 )*(t-0.031)/2)*np.pi*dia_2) )
q_4 = ct.Func1(lambda t: -1/area_2*(r2.T - Tw)*h_2*(2*(area_1+area_2) + Awalls - (0.02*21/2 + (21+26.5)*0.011/2 + (26.5+1)*0.002/2 + (0.0025*1/2 - (0.0355-t)*(0.0355-t)/0.0025*1/2) )*np.pi*dia_2) )
q_5 = ct.Func1(lambda t: -1/area_2*(r2.T - Tw)*h_2*(2*(area_1+area_2) + Awalls - (0.02*21/2 + (21+26.5)*0.011/2 + (26.5+1)*0.002/2 + 0.0025*1/2 )*np.pi*dia_2) )


n_steps = steps_1 + steps_2 + steps_3 + steps_4 + steps_5
data = np.zeros( (n_steps, 13) )
total_mass = r1.mass + r2.mass + r3.mass


sim = ct.ReactorNet([r1, r2, r3])
print('Setup is done. Start simulation...')

######################################################################################################################
#
print('Part 1')
endtime = datetime.datetime.now()
print (endtime-starttime)

n = 0
time = 0.0
w1.set_velocity(v_1) 
w2.set_velocity(v_1) 
w2.set_heat_flux(q_1)
while time - t_1 <= -t_step_1/10:
	time += t_step_1
	sim.advance(time)
	data[n,:] = time, r1.T, r1.thermo.P*1.0e-5, r1.volume, r1.mass/total_mass, r2.T, r2.thermo.P*1.0e-5, r2.volume, r2.mass/total_mass, r3.T, r3.thermo.P*1.0e-5, r3.volume, r3.mass/total_mass
	n += 1

print('Part 2')
endtime = datetime.datetime.now()
print (endtime-starttime)
sim.set_initial_time(t_1)
w1.set_velocity(v_2) 
w2.set_velocity(v_2) 
w2.set_heat_flux(q_2)
while time - t_2 <= -t_step_2/10:
	time += t_step_2
	sim.advance(time)
	data[n,:] = time, r1.T, r1.thermo.P*1.0e-5, r1.volume, r1.mass/total_mass, r2.T, r2.thermo.P*1.0e-5, r2.volume, r2.mass/total_mass, r3.T, r3.thermo.P*1.0e-5, r3.volume, r3.mass/total_mass
	n += 1

print('Part 3')
endtime = datetime.datetime.now()
print (endtime-starttime)
sim.set_initial_time(t_2)
w1.set_velocity(v_3) 
w2.set_velocity(v_3) 
w2.set_heat_flux(q_3)
while time - t_3 <= -t_step_3/10:
	time += t_step_3
	sim.advance(time)
	data[n,:] = time, r1.T, r1.thermo.P*1.0e-5, r1.volume, r1.mass/total_mass, r2.T, r2.thermo.P*1.0e-5, r2.volume, r2.mass/total_mass, r3.T, r3.thermo.P*1.0e-5, r3.volume, r3.mass/total_mass
	n += 1

print('Part 4')
endtime = datetime.datetime.now()
print (endtime-starttime)
sim.set_initial_time(t_3)
w1.set_velocity(v_4) 
w2.set_velocity(v_4) 
w2.set_heat_flux(q_4)
while time - t_4 <= -t_step_4/10:
	time += t_step_4
	sim.advance(time)
	data[n,:] = time, r1.T, r1.thermo.P*1.0e-5, r1.volume, r1.mass/total_mass, r2.T, r2.thermo.P*1.0e-5, r2.volume, r2.mass/total_mass, r3.T, r3.thermo.P*1.0e-5, r3.volume, r3.mass/total_mass
	n += 1

print('Part 5')
endtime = datetime.datetime.now()
print (endtime-starttime)
end_num = n_steps
sim.set_initial_time(t_4)
w1.set_velocity(v_5) 
w2.set_velocity(v_5) 
w2.set_heat_flux(q_5)
while time - t_5 <= -t_step_5/10:
	time += t_step_5
	sim.advance(time)
	data[n,:] = time, r1.T, r1.thermo.P*1.0e-5, r1.volume, r1.mass/total_mass, r2.T, r2.thermo.P*1.0e-5, r2.volume, r2.mass/total_mass, r3.T, r3.thermo.P*1.0e-5, r3.volume, r3.mass/total_mass
	n += 1
	if r1.T >2500:
		end_num = n-1
		break

print('Simulation finished!')
endtime = datetime.datetime.now()
print (endtime-starttime)

######################################################################################################################
#
outfile = open('L50_r.csv', 'w')
csvfile = csv.writer(outfile, delimiter=',', lineterminator='\n')
csvfile.writerow(['time (s)', 'T1 (K)', 'P1 (bar)', 'V1 (m3)', 'mf1 (%)', 'T2 (K)', 'P2 (bar)', 'V (m3)', 'mf2 (%)', 'T3 (K)', 'P3 (bar)', 'V 3 (m3)', 'mf3 (%)'])

temp = np.zeros((end_num, 13))
temp = data[ 0:end_num, 0:13 ]
csvfile.writerows(temp)

######################################################################################################################
#
outfile.close()
print('Output written to file Multi_Zone.csv')
print('Directory: '+os.getcwd())

endtime = datetime.datetime.now()
print (endtime-starttime)

	
