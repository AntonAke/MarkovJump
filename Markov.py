import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
Beta_a = [2, 1]		% Kontakter i [population a, population b]
Beta_b = [1,2]
Time = 7
Fatality = 0.005	%kan beskrivas senare som en fördelning
gamma = 1 %Sannolikhet att tillfrriskna per tidsenhet


S_a = 100 % Totalt antal individer i populationen a
S_b = 100 % Totalt antal individer i populationen b
I_a = 1   % Antal smittade i a
I_b = 0		% Antal smittade i b
R_a = 0		% Antalet tillfrisknade
R_b = 0
D_a = 0 	% Antal döda
D_b = 0
N_a = S_a + I_a + R_a
N_b = S_b + I_b + R_b
W_infect_a = (Beta_a[0]*S_a*I_a + Beta_a[1]*I_b*S_a)/(Time*N_a) %Sannolikhet att någon i A smittas per tidsenhet
W_infect_b = (Beta_b[0]*S_b*I_a + Beta_b[1]*I_b*S_b)/(Time*N_a) %Sannolikhet att någon i B smittas per tidsenhet
W_recover_a = gamma*I_a %Sannolikhet att någon i A tillfrisknar per tidsenhet
W_recover_b = gamma*I_b %Sannolikhet att någon i B tillfrisknar per tidsenhet
W_die_a = fatality*I_a/Time %Sannolikhet att någon i A dör per tidsenhet
W_die_b = fatality*I_b/Time %Sannolikhet att någon i B dör per tidsenhet

def TimeStep(R, W): #Takes a time step
  timeStep = np.random.exponential(R,1)
  event = np.random.uniform(0,1)
  return (timeStep,event)

def Simulate(time): #Does the simulation
  t = 0
  timeList = []
  InfectedList = []
  while t<time:
    (delta_t, event) = TimeStep(R,W)
    t += dt
        #do event
    #Plot result
    timeList.append(time)
    InfectedList.append(I_a)
