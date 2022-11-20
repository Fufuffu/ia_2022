import copy
from dataclasses import dataclass

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio


class Estat:
    MAX_PROFUNDITAT = 4

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

    def __hash__(self):
        return hash(tuple(self.__info))

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        return self.__info == other.__info

    @staticmethod
    def nom_altre(nom: str) -> str:
        if nom == "Miquel":
            return "Tomeu"
        return "Miquel"

    def manhattan(self, nom: str) -> int:
        pos = self[ClauPercepcio.POSICIO][nom]
        pizza = self[ClauPercepcio.OLOR]
        return abs(pizza[0] - pos[0]) + abs(pizza[1] - pos[1])

    def evaluar(self, nom: str, es_max: bool, profunditat: int):
        if self.es_meta(nom) or profunditat == self.MAX_PROFUNDITAT:
            distancia_altre = self.manhattan(self.nom_altre(nom))
            distancia_rana = self.manhattan(nom)

            if es_max:
                return distancia_altre - distancia_rana
            else:
                return distancia_rana - distancia_altre

        return None

    def es_meta(self, nom: str) -> bool:
        return self[ClauPercepcio.POSICIO][nom] == self[ClauPercepcio.OLOR] or \
               self[ClauPercepcio.POSICIO][self.nom_altre(nom)] == self[ClauPercepcio.OLOR]

    def no_es_segur(self, pos: tuple[int, int], nom: str) -> bool:
        return pos in self[ClauPercepcio.PARETS] or \
               pos == self[ClauPercepcio.POSICIO][self.nom_altre(nom)] or \
               (pos[0] > 7 or pos[0] < 0) or \
               (pos[1] > 7 or pos[1] < 0)

    def genera_fill(self, nom: str) -> list:
        estats_generats = []

        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        # Moure
        for direccio in direccions:
            nova_posicio = self._calcula_casella(
                posicio=self[ClauPercepcio.POSICIO][nom], dir=direccio, magnitut=1)

            if self.no_es_segur(nova_posicio, nom):
                continue

            nou_estat = copy.deepcopy(self)
            nou_estat.pare = (self, (AccionsRana.MOURE, direccio))
            nou_estat[ClauPercepcio.POSICIO][nom] = nova_posicio
            estats_generats.append(nou_estat)

        # Botar
        for direccio in direccions:
            nova_posicio = self._calcula_casella(
                posicio=self[ClauPercepcio.POSICIO][nom], dir=direccio, magnitut=2)

            if self.no_es_segur(nova_posicio, nom):
                continue

            nou_estat = copy.deepcopy(self)
            nou_estat.pare = (self, (AccionsRana.BOTAR, direccio))
            nou_estat[ClauPercepcio.POSICIO][nom] = nova_posicio
            estats_generats.append(nou_estat)

        # Esperes
        nou_estat = copy.deepcopy(self)
        nou_estat.pare = (self, (AccionsRana.ESPERAR, Direccio.DRETA))
        estats_generats.append(nou_estat)

        return estats_generats

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

    @staticmethod
    def _calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Estat.MOVS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)


@dataclass
class EstatPuntuacio:
    puntuacio: int
    estat: Estat

    def __gt__(self, other):
        return self.puntuacio > other.puntuacio

    def __lt__(self, other):
        return self.puntuacio < other.puntuacio


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(args[0])
        self.__nom = args[0]
        self.__accions = []

        self.__es_max = True if self.__nom == "Miquel" else False

    def pinta(self, display):
        pass

    def minimax(self, estat: Estat, profunditat: int, es_max: bool, nom: str) -> EstatPuntuacio:
        score = estat.evaluar(nom, es_max, profunditat)
        if score is not None:
            iterador = estat
            while iterador.pare is not None and iterador.pare[0].pare is not None:
                pare, accio = iterador.pare
                iterador = pare

            return EstatPuntuacio(score, copy.deepcopy(iterador))

        puntuacio_fills = [self.minimax(estat_fill, profunditat + 1, not es_max, estat.nom_altre(nom)) for estat_fill in
                           estat.genera_fill(nom)]
        if es_max:
            return max(puntuacio_fills)
        else:
            return min(puntuacio_fills)

    def cerca_moviment(self, estat_inicial: Estat):
        resultat = self.minimax(estat_inicial, 0, self.__es_max, self.__nom)

        if resultat.estat.pare is not None:
            accio_final = resultat.estat.pare[1]
        else:
            accio_final = (AccionsRana.ESPERAR, Direccio.BAIX)

        if accio_final[0] == AccionsRana.BOTAR:
            self.__accions.append((AccionsRana.ESPERAR, Direccio.ESQUERRE))
            self.__accions.append((AccionsRana.ESPERAR, Direccio.ESQUERRE))
        self.__accions.append(accio_final)

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(percep.to_dict())

        if len(self.__accions) == 0:
            self.cerca_moviment(estat_inicial)

        if len(self.__accions) > 0:
            accio, direccio = self.__accions.pop()
            return accio, direccio
        else:
            return AccionsRana.ESPERAR
