import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
global Beta,Time, Fatality
Beta  = 10 #Antal smittsamma kontakter
Time = 8 #Tiden sjuk/smittsam om man är sjuka
Fatality = 0.005	# kan beskrivas senare som en fördelning

class Stad:
    S = 0  #Antalet personer som kan smittal
    N = 0 # Totalt antal individer i staden
    I = 0 #Antalet smittade
    R = 0# Antalet tillfrisknade
    D = 0 # Antal döda
    C = [] #Andel kontakter mellan personer i staden och de i staden på indexet
    def __init__(self, pop, infected, contacts):
        self.N = pop
        self.I = infected
        self.S = pop-infected
        self.C = contacts

    def infected(self):
        self.I+=1;
        self.S-=1

    def recover(self):
        self.R+=1
        self.I-=1

    def die(self):
        self.D+=1
        self.I-=1

    def get_Infected(self):
        return self.I

    def get_Population(self):
        return self.N

    def get_Susceptible(self):
        return self.S



def timeStep(W, stadslista): #Tar ett tidssteg, givet en lista med Sannolikhet/tid för alla händelser
    R = sum(W)
    timeStep = np.random.exponential(1/R)
    event = np.random.uniform(0,R)
    count = 0
    for i in range(len(W)):
        count += W[i]
        if count>=event:
            break
    stad=i//3
    Händelse=i%3
    if Händelse == 0:
        stadslista[stad].infected()
    elif Händelse == 1:
        stadslista[stad].recover()
    else:
        stadslista[stad].die()
    return timeStep

def update(stadslista):
    Händelser = []
    for i in range(len(stadslista)):
        stad = stadslista[i]
        W_infect = Beta*stad.S/(Time*stad.N)*sum(map(lambda s:s.I*s.C[i], stadslista)) #Sannolikhet att någon i staden smittas
        W_recover = stad.I/Time #Sannolikhet att någon i staden tillfrisknar
        W_die = Fatality*stad.I/Time #Sannolikhet att någon i staden dör
        Händelser.extend([W_infect, W_recover,W_die])
    return Händelser


def Simulate(end_time, stadslista): #Gör simuleringen
    t = 0
    Händelser = update(stadslista)
    InfectedList = [[] for i in range(len(stadslista))]
    nextDay = 1
    while t<end_time and sum(Händelser)>0:
        for i in range(len(stadslista)):
            InfectedList[i].append(stadslista[i].get_Infected()/stadslista[i].N)
        while t<nextDay and sum(Händelser)>0:
            delta_t = timeStep(Händelser, stadslista)
            t += delta_t
            Händelser = update(stadslista)
        nextDay+=1
    return InfectedList
#Cool_visualisation(Data)

"""def Cool_visualisation(Data):
continue"""
def main():
    Stad_A = Stad(300000,100, [19/20, 1/20])
    Stad_B = Stad(100000,0, [2/10,8/10])
    stadslista = [Stad_A,Stad_B]
    result = Simulate(10, stadslista)
    for i in range(len(stadslista)):
        plt.plot(result[i])
        stad = stadslista[i]
        print("Total infected:", (stad.R+stad.I)/stad.N, "Dead:", stad.D/stad.N)
    plt.show()

if __name__ == "__main__":
    main()
