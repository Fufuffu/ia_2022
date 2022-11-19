import copy
import itertools
import random
from queue import PriorityQueue

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    priority: float
    item: Any = field(compare=False)


class Rana(joc.Rana):
    MAX_POBLACIO = 50

    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__accions = None

    def pinta(self, display):
        pass

    def _genetic(self, percep):
        # Genetic pool
        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        accions = [AccionsRana.BOTAR, AccionsRana.MOURE, AccionsRana.ESPERAR]

        genetic_pool = []

        for element in itertools.product(accions, direccions):
            genetic_pool.append(element)

        poblacio = []
        while len(poblacio) < self.MAX_POBLACIO:
            ind = Individu()
            ind.genera_individu(genetic_pool)
            if ind.es_segur(percep[ClauPercepcio.POSICIO]['Miquel'], percep[ClauPercepcio.PARETS],
                            percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
                poblacio.append(ind)

        print(percep[ClauPercepcio.POSICIO]['Miquel'])
        print(percep[ClauPercepcio.OLOR])
        """SELECTION"""
        end = False
        iteraciones = 0
        while not end:
            cua_fitness = PriorityQueue()
            for i in poblacio:
                if i.es_meta(percep[ClauPercepcio.POSICIO]['Miquel'], percep[ClauPercepcio.PARETS],
                             percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
                    end = True
                    ind_sol = i
                    break

                cua_fitness.put(
                    PrioritizedItem(i.fitness(), i))

            """CROSSOVER"""
            for i in range(self.MAX_POBLACIO - 1):

                # Agafar dos individus aleatoris
                index_ind1 = i
                index_ind2 = i + 1
                i += 1

                ind1 = poblacio[index_ind1]
                ind2 = poblacio[index_ind2]

                # Com a mínim intercanviam un gen
                if len(ind1.info()) > len(ind2.info()):
                    index_cross = random.randint(0, len(ind2.info()) - 1)
                else:
                    index_cross = random.randint(0, len(ind1.info()) - 1)

                # Crossover
                print("CRUCE ---------------------")
                print(index_cross)
                print(ind1.info())
                print(ind2.info())
                print(ind1.info()[:index_cross])
                print(ind2.info()[index_cross:])

                fill1_info = ind1.info()[:index_cross] + ind2.info()[index_cross:]
                fill2_info = ind2.info()[:index_cross] + ind1.info()[index_cross:]
                print(fill1_info)
                print(fill2_info)

                """MUTACIÓ"""
                # Probabilitat de un deu percent de mutació
                if iteraciones > 100:
                    probabilitat = 1
                else:
                    probabilitat = random.randint(1, 10)
                if probabilitat == 1:
                    fill1_info.append(random.choice(genetic_pool))
                    print("MUTACION _____________________________")

                if iteraciones > 100:
                    probabilitat = 1
                else:
                    probabilitat = random.randint(1, 10)
                if probabilitat == 1:
                    fill2_info.append(random.choice(genetic_pool))
                    print("MUTACION ---------------------------")

                # Creació fills i veure si son segurs
                fill1 = Individu()
                fill1.set_info(fill1_info)
                if fill1.es_segur(percep[ClauPercepcio.POSICIO]['Miquel'], percep[ClauPercepcio.PARETS],
                                  percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
                    cua_fitness.put(
                        PrioritizedItem(fill1.fitness(), fill1))

                fill2 = Individu()
                fill2.set_info(fill2_info)
                if fill2.es_segur(percep[ClauPercepcio.POSICIO]['Miquel'], percep[ClauPercepcio.PARETS],
                                  percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
                    cua_fitness.put(
                        PrioritizedItem(fill2.fitness(), fill2))

            if not end:
                poblacio = []
                for i in range(self.MAX_POBLACIO):
                    ind_aux = cua_fitness.get()
                    ind_aux = ind_aux.item
                    poblacio.append(ind_aux)

            print(iteraciones)
            iteraciones += 1

        accions = []
        for i in ind_sol.info():
            accions.insert(0, i)
            if i[0] == AccionsRana.BOTAR:
                accions.insert(0, (AccionsRana.ESPERAR, Direccio.DRETA))
                accions.insert(0, (AccionsRana.ESPERAR, Direccio.DRETA))

        self.__accions = accions
        return True

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:

        if self.__accions is None:
            self._genetic(percep)

        if len(self.__accions) > 0:
            acc = self.__accions.pop()

            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR


class Individu:
    ind_size = 14

    MOVS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self):
        self.__info = []
        self.__fitness = -1

    def info(self):
        return self.__info

    def fitness(self):
        return self.__fitness

    def set_info(self, list: []):
        self.__info = list

    def genera_individu(self, genetic_pool: []):
        for i in range(Individu.ind_size):
            self.__info.append(random.choice(genetic_pool))

    @staticmethod
    def _calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Individu.MOVS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)

    def es_segur(self, pos_inicial: (int, int), parets: [(int, int)], mapa: (int, int), meta: (int, int)):
        pos_actual = (pos_inicial[0], pos_inicial[1])
        cont = 0
        for i in self.__info:
            pos_anterior = pos_actual
            if i[0] == AccionsRana.MOURE:
                pos_actual = Individu._calcula_casella(pos_actual, i[1], 1)
            elif i[0] == AccionsRana.BOTAR:
                pos_actual = Individu._calcula_casella(pos_actual, i[1], 2)

            cont += 1
            if pos_actual in parets or pos_actual[0] >= mapa[0] or pos_actual[0] < 0 or pos_actual[1] >= mapa[1] or \
                    pos_actual[1] < 0:
                if cont == 1:
                    return False
                else:
                    self.__info = self.__info[:cont - 1]
                    self.__fitness = self.fitness_fuction(pos_anterior, meta)
                    return True

            if pos_actual == meta:
                self.__info = self.__info[:cont]
                self.__fitness = len(self.__info) * 0.2
                return True

        self.__fitness = self.fitness_fuction(pos_actual, meta)
        return True

    def fitness_fuction(self, pos_actual: (int, int), meta: (int, int)):
        distancia = abs(meta[0] - pos_actual[0]) + abs(meta[1] - pos_actual[1])
        return 0.8 * distancia + 0.2 * len(self.__info)

    def es_meta(self, pos_inicial: (int, int), parets: [(int, int)], mapa: (int, int), meta: (int, int)):
        pos_actual = (pos_inicial[0], pos_inicial[1])
        for i in self.__info:
            if i[0] == AccionsRana.MOURE:
                pos_actual = Individu._calcula_casella(pos_actual, i[1], 1)
            elif i[0] == AccionsRana.BOTAR:
                pos_actual = Individu._calcula_casella(pos_actual, i[1], 2)

            if pos_actual == meta:
                return True
        return False
