import copy
import math
from queue import PriorityQueue
from typing import Tuple

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        pass

    def _cerca(self, estat):
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put(
            PrioritizedItem(estat.calc_heuristica(), estat))

        actual = None
        while not self.__oberts.empty():
            actual = self.__oberts.get()
            actual = actual.item
            if actual in self.__tancats:
                continue

            if actual.es_meta():
                break

            estats_fills = actual.genera_fill()

            for estat_f in estats_fills:
                self.__oberts.put(
                    PrioritizedItem(estat_f.calc_heuristica(), estat_f))

            self.__tancats.add(actual)

        if actual.es_meta():
            accions = []
            iterador = actual

            while iterador.pare is not None:
                pare, accio = iterador.pare

                for acc in accio:
                    accions.append(acc)
                iterador = pare
            self.__accions = accions
            return True
        else:
            return False

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(percep.to_dict())

        if self.__accions is None:
            self._cerca(estat=estat_inicial)

        if len(self.__accions) > 0:
            acc = self.__accions.pop()

            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR


class Estat:
    MOVS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self, info: dict = None, pare=None):
        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare
        self.__pes = 0

        self.__nom = "Miquel"

    def __hash__(self):
        return hash(self.__info[ClauPercepcio.POSICIO][self.__nom])

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        """Overrides the default implementation"""
        return (
                self[ClauPercepcio.POSICIO][self.__nom] == other[ClauPercepcio.POSICIO][self.__nom]
        )

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    def genera_fill(self) -> list:
        estats_generats = []

        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        accions = {
            AccionsRana.BOTAR: 2,
            AccionsRana.MOURE: 1
        }

        for accio, salts in accions.items():
            for direccio in direccions:
                nova_posicio = self._calcula_casella(
                    posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=salts)

                if nova_posicio in self[ClauPercepcio.PARETS] or \
                        (nova_posicio[0] > 7 or nova_posicio[0] < 0) or \
                        (nova_posicio[1] > 7 or nova_posicio[1] < 0):
                    continue

                nou_estat = copy.deepcopy(self)

                if AccionsRana.BOTAR == accio:
                    nou_estat.pare = (self, [(AccionsRana.ESPERAR, direccio),
                                             (AccionsRana.ESPERAR, direccio),
                                             (accio, direccio)])
                    nou_estat.pes = self.__pes + 7
                else:
                    nou_estat.pare = (self, [(accio, direccio)])
                    nou_estat.pes = self.__pes + 1

                nou_estat[ClauPercepcio.POSICIO][self.__nom] = nova_posicio

                estats_generats.append(nou_estat)

        return estats_generats

    def calc_heuristica(self):
        pos = self[ClauPercepcio.POSICIO][self.__nom]
        distancia = math.sqrt((pos[0]*pos[0]) + (pos[1]*pos[1]))
        return distancia + self.__pes

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

    @property
    def pes(self):
        return self.__pes

    @pes.setter
    def pes(self, value):
        self.__pes = value

    @staticmethod
    def _calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Estat.MOVS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)
