import copy
import tracemalloc
from queue import PriorityQueue

from stopwatch import Stopwatch

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio
from dataclasses import dataclass, field


class Estat:
    MOVS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self, nom_agent: str, info: dict = None, pare=None):
        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare
        self.__pes = 0

        self.__dir_bot = None
        self.__bots_restants = 0
        self.__nom = nom_agent

    def __hash__(self):
        return hash(tuple(self.__info))

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        if self.__pare and other.pare:
            return self.__info == other.__info and self.__pare[1] == other.pare[1]
        else:
            return self.__info == other.__info and self.__bots_restants == other.__bots_restants

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    def iniciar_bot(self, direccio: Direccio):
        self.__dir_bot = direccio
        self.__bots_restants = 2

    def seguir_bot(self):
        self.__bots_restants -= 1
        return self.__dir_bot

    def botant(self) -> bool:
        return self.__bots_restants > 0

    def no_es_segur(self, pos: tuple[int, int]) -> bool:
        mida_taulell = self[ClauPercepcio.MIDA_TAULELL]

        return (
                pos in self[ClauPercepcio.PARETS] or
                (pos[0] > mida_taulell[0] - 1 or pos[0] < 0) or
                (pos[1] > mida_taulell[1] - 1 or pos[1] < 0)
        )

    def genera_fill(self) -> list:
        if self.botant():
            direccio = self.seguir_bot()
            # Si ha acabat el bot, podem generar la posició final del bot
            if not self.botant():
                nou_estat = copy.deepcopy(self)
                nou_estat.pare = (self, (AccionsRana.ESPERAR, Direccio.ESQUERRE))
                nova_posicio = self._calcula_casella(
                    posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=2)
                nou_estat[ClauPercepcio.POSICIO][self.__nom] = nova_posicio
                nou_estat.pes = self.__pes + 0.5
                return [nou_estat]
            else:

                nou_estat = copy.deepcopy(self)
                nou_estat.pare = (self, (AccionsRana.ESPERAR, Direccio.DALT))
                nou_estat.pes = self.__pes + 0.5
                nou_estat.pes = self.__pes + 0.5
                return [nou_estat]

        estats_generats = []
        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        # Moure
        for direccio in direccions:
            nova_posicio = self._calcula_casella(
                posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=1)

            if self.no_es_segur(nova_posicio):
                continue

            nou_estat = copy.deepcopy(self)
            nou_estat.pare = (self, (AccionsRana.MOURE, direccio))
            nou_estat.pes = self.__pes + 1
            nou_estat[ClauPercepcio.POSICIO][self.__nom] = nova_posicio
            estats_generats.append(nou_estat)

        # Botar
        for direccio in direccions:
            nova_posicio = self._calcula_casella(
                posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=2)

            if self.no_es_segur(nova_posicio):
                continue

            # No actualizam la posició, serà modificada en la darrera espera
            nou_estat = copy.deepcopy(self)
            nou_estat.iniciar_bot(direccio)
            nou_estat.pare = (self, (AccionsRana.BOTAR, direccio))
            nou_estat.pes = self.__pes + 6
            estats_generats.append(nou_estat)

        # Esperar
        nou_estat = copy.deepcopy(self)
        nou_estat.pare = (self, (AccionsRana.ESPERAR, Direccio.BAIX))
        nou_estat.pes = self.__pes + 0.5
        estats_generats.append(nou_estat)

        return estats_generats

    def calc_heuristica(self) -> float:
        pos = self[ClauPercepcio.POSICIO][self.__nom]
        pizza = self[ClauPercepcio.OLOR]
        distancia = abs(pizza[0] - pos[0]) + abs(pizza[1] - pos[1])
        return distancia + self.pes

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


@dataclass(order=True)
class PrioritizedItem:
    prioritat: int
    estat: Estat = field(compare=False)


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        pass

    def _cerca(self, estat) -> bool:
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put(
            PrioritizedItem(estat.calc_heuristica(), estat))

        actual = None
        while not self.__oberts.empty():
            actual = self.__oberts.get()
            actual = actual.estat
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

                accions.append(accio)
                iterador = pare
            self.__accions = accions
            return True
        else:
            return False

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(self.nom, percep.to_dict())
        if self.__accions is None:
            stopwatch = Stopwatch()
            stopwatch.start()
            self._cerca(estat=estat_inicial)
            stopwatch.stop()
            print(stopwatch.report())

            tracemalloc.start()
            self._cerca(estat=estat_inicial)
            print("Memory (B)", tracemalloc.get_traced_memory())
            tracemalloc.stop()

        if len(self.__accions) > 0:
            acc = self.__accions.pop()

            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR
