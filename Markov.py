import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import statistics as st

global Beta, Time, Fatality, vaccinated
Beta = 18  # Antal smittsamma kontakter
Time = 8  # Tiden sjuk/smittsam om man är sjuka
Fatality = 0.001  # kan beskrivas senare som en fördelning
vaccinated = 0.97 * 0.95  # 97% vaccinerade med 95% effektivit vaccin


class Stad:
    S = 0  # Antalet personer som kan smittal
    N = 0  # Totalt antal individer i staden
    I = 0  # Antalet smittade
    R = 0  # Antalet tillfrisknade
    C = []  # Andel kontakter med personer från olika städer
    V = 0  # Antal vaccinerade

    def __init__(self, pop, infected, contacts):
        self.N = pop
        self.I = infected
        self.V = vaccinated * pop
        self.S = pop - infected - self.R - self.V
        self.C = contacts

    def infected(self):
        self.I += 1;
        self.S -= 1

    def recover(self):
        self.R += 1
        self.I -= 1


def timeStep(W, stadslista):  # Tar ett tidssteg, givet en lista med Sannolikhet/tid för alla händelser
    R = sum(W)
    timeStep = np.random.exponential(1 / R)
    event = np.random.uniform(0, R)
    count = 0
    for i in range(len(W)):
        count += W[i]
        if count >= event:
            break
    stad = i // 2
    Händelse = i % 2
    if Händelse == 0:
        stadslista[stad].infected()
    elif Händelse == 1:
        stadslista[stad].recover()
    return timeStep


def update(stadslista):  # Uppdaterar sannolikheterna för de olika händelserna
    Händelser = []
    for i in range(len(stadslista)):
        stad = stadslista[i]
        W_infect = Beta * stad.S / (Time * stad.N) * sum(
            map(lambda s: s.I * s.C[i], stadslista))  # Sannolikhet att någon i staden smittas
        W_recover = stad.I / Time * 1 / (1 + Fatality)  # Sannolikhet att någon i staden tillfrisknar
        Händelser.extend([W_infect, W_recover])
    return Händelser


def Simulate(end_time, stadslista):  # Gör simuleringen t.o.m sluttimde eller inga fler händelser kommer hända
    t = 0
    Händelser = update(stadslista)
    InfectedList = [[] for i in range(len(stadslista))]
    nextDay = 1
    while t < end_time and sum(Händelser) > 0:
        for i in range(0, len(stadslista)):
            InfectedList[i].append(
                (stadslista[i].I / (stadslista[i].N-stadslista[i].V)))
        while t < nextDay / 24 and sum(Händelser) > 0:
            delta_t = timeStep(Händelser, stadslista)
            t += delta_t
            Händelser = update(stadslista)
        nextDay += 1
    return InfectedList


def skapaStäder(Befolkning, AntalSmittadeP, AntalSmittadeIP,
                AntalA):  # Skapar en stadslista med rätt antal kontakter mellan städerna samt pendlarna, icke-pendalre har jämt index i listan
    AntalStäder = len(Befolkning)
    AntalAFrån = [[AntalA[j][i] for i in range(AntalStäder)] for j in
                  range(AntalStäder)]  # Värdet på index i,j är antalet personer från stad i som jobbar i stad i
    AndelP = [1 - AntalAFrån[i][i] / sum(AntalAFrån[i]) for i in range(AntalStäder)]  # Andel pendlare från varje stad
    AntalP = [Befolkning[i] * AndelP[i] for i in range(len(Befolkning))]  # antal pendlare
    AntalIckeP = [Befolkning[i] - AntalP[i] for i in range(len(Befolkning))]
    stadslista = []

    for i in range(len(AntalA)):
        IPKontakt = [(AntalA[i][j // 2] / sum(AntalA[i]) * 0.5) if (j % 2 == 1 or j == 2 * i)
                     else 0 for j in
                     range(AntalStäder * 2)]  # Beräknar kontakter för icke-pendlare från arbetare i personens stad
        IPKontakt[2 * i] += 0.5 * (1 - AndelP[i])  # Lägger till kontakter hemfifrån för icke-pendlare
        IPKontakt[2 * i + 1] = 0.5 * AndelP[i]  # Kontakter hemifrån från pendlare
        PKontakt = [(AntalAFrån[i][j // 2] / sum(AntalAFrån[i]) * 0.5) if (j % 2 == 0 or j == 2 * i + 1)
                    else 0 for j in range(
            AntalStäder * 2)]  # Beräknar kontakter för pendlare från personer som arbetar i deras arbetskommun
        PKontakt[2 * i] = 0.5 * (1 - AndelP[i])  # Lägger till kontakter från ickependlare med pendlare
        PKontakt[2 * i + 1] += 0.5 * AndelP[i]  # HemmaKontakter från pendlare med pendlare
        StadIckeP = Stad(AntalIckeP[i], AntalSmittadeIP[i], IPKontakt)
        StadP = Stad(AntalP[i], AntalSmittadeP[i], PKontakt)
        stadslista.append(StadIckeP)
        stadslista.append(StadP)
    return stadslista


def plot(stadslista, result):  # Plottar resultatet för en stadslita och en
    Stadsnamn = ["Malmö", "Lund", "Ystad"]
    for i in range(len(stadslista) // 2):
        plt.plot(np.add(result[i*2], result[i*2 + 1]), label=Stadsnamn[i])
        plt.legend()
        plt.xlabel('tid(Dagar)')
        plt.ylabel('Andel smittade')
        stad = stadslista[2 * i]
        pendlare = stadslista[2 * i + 1]
        print("Total infected:", (stad.I + pendlare.I) / (stad.N + pendlare.N-stad.V-pendlare.V))
    print([st.variance(result[i]) for i in range(3)])

def plotPendlare(stadslista, result):  # Plottar resultatet för en stadslita och en
    Grupp = ["Ickependlare", "Pendlare"]
    Stadsnamn = ["Malmö", "Lund", "Ystad"]
    for i in range(len(stadslista) // 2):
        plt.figure(5+i)
        plt.plot(result[2*i], label=Grupp[0])
        plt.plot(result[2*i+1],label=Grupp[1])
        plt.legend()
        plt.title(Stadsnamn[i])
        plt.xlabel("tid(Dagar)")
        plt.ylabel("Andel smittade")
        stad = stadslista[2 * i]
        pendlare = stadslista[2 * i + 1]
        print("Infected Commuters:", stad.I/ (stad.N-stad.V))
        print("Infected non-Commuters:", (pendlare.I) / (pendlare.N-pendlare.V))
    print([st.variance(result[i]) for i in range(3)])

def köraDen():
    Befolkning = [344166, 124935, 30850]
    AntalSmittadeP = [0, 0, 0]
    AntalSmittadeIP = [0, 0, 20]
    AntalDagar = 100
    AntalA = [[133043, 11817, 1689], [11868, 32806, 413],
              [583, 191, 8840]]  # Antal arbetande i stad i från stad j [i][j]

    extremvärden(Befolkning, AntalSmittadeP, AntalSmittadeIP, AntalDagar, AntalA, 10)


def extremvärden(Befolkning, AntalSmittadeP, AntalSmittadeIP, AntalDagar, AntalA, AntalG):
    minst = skapaStäder(Befolkning, AntalSmittadeP, AntalSmittadeIP, AntalA)


    minstresultat = Simulate(AntalDagar, minst)
    antalMinst = sum([stad.R + stad.I for stad in minst])
    mest, mestresultat, antalMest = minst, minstresultat, antalMinst
    for i in range(AntalG):  # Simulerar smittspridningen ett visst antal gånger och sparar de fall där smittan är störst/minst
        stadslista = skapaStäder(Befolkning, AntalSmittadeP, AntalSmittadeIP, AntalA)
        resultat = Simulate(AntalDagar, stadslista)
        antal = sum([stad.R + stad.I for stad in stadslista])
        if antal < antalMinst:
            minst = stadslista
            antalMinst = antal
            minstresultat = resultat
        elif antal > antalMest:
            mest = stadslista
            antalMest = antal
            mestresultat = resultat
    plt.figure(1)
    plot(minst, minstresultat)
    plt.figure(2)
    plot(mest, mestresultat)
    plotPendlare(mest, mestresultat)
    plt.show()

if __name__ == "__main__":
    köraDen()
