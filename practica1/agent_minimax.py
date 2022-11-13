import copy

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(args[0])
        self.__nom = args[0]
        self.__es_max = kwargs["es_max"]

    def pinta(self, display):
        pass

    def minimax(self, estat, es_max: bool):
        score = estat.evaluar()
        if score is not None:
            return estat

        estats_fill = estat.genera_fill()
        puntuacio_fills = [self.minimax(estat_fill, not es_max) for estat_fill in estats_fill]
        if es_max:
            return max(puntuacio_fills)
        else:
            return min(puntuacio_fills)

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(self.__nom, self.__es_max, 0, percep.to_dict())

        #fills_min = estat_inicial.genera_fill()

        #fills_min_max = fills_min[0].genera_fill()

        resultat = self.minimax(estat_inicial, self.__es_max)

        accio_final = None
        iterador = resultat

        while iterador.pare is not None:
            pare, accio = iterador.pare
            accio_final = accio
            iterador = pare

        if accio_final is None:
            return AccionsRana.ESPERAR

        accio, direccio = accio_final
        print(f"{resultat._Estat__nom}{resultat._Estat__info[ClauPercepcio.POSICIO][resultat._Estat__nom]}: {accio}, {direccio}")
        return accio, direccio


class Estat:
    MOVS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }
    MAX_PROFUNDITAT = 2

    def __init__(self, nom: str, es_max: bool, profunditat: int, info: dict = None, pare=None):
        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare

        self.__nom = nom
        self.__es_max = es_max
        self.__profunditat = profunditat

    def __hash__(self):
        return hash((self.__info[ClauPercepcio.POSICIO][self.__nom],
                     self.__info[ClauPercepcio.POSICIO][self.nom_altre(self.__nom)]))

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        return (
                self[ClauPercepcio.POSICIO][self.__nom] == other[ClauPercepcio.POSICIO][self.__nom] and
                self[ClauPercepcio.POSICIO][self.nom_altre(self.__nom)] == other[ClauPercepcio.POSICIO][
                    self.nom_altre(self.__nom)]
        )

    def __lt__(self, other):
        return self.evaluar() < other.evaluar()

    def __gt__(self, other):
        return self.evaluar() > other.evaluar()

    @staticmethod
    def nom_altre(nom: str) -> str:
        if nom == "Papafritta":
            return "Billy"
        return "Papafritta"

    def manhattan(self, nom: str) -> int:
        pos = self[ClauPercepcio.POSICIO][nom]
        pizza = self[ClauPercepcio.OLOR]
        return abs(pizza[0] - pos[0]) + abs(pizza[1] - pos[1])

    def evaluar(self):
        if self.es_meta() or self.__profunditat == self.MAX_PROFUNDITAT:
            distancia_altre = self.manhattan(self.nom_altre(self.__nom))
            distancia_rana = self.manhattan(self.__nom)

            if self.__es_max:
                return distancia_rana - distancia_altre
            else:
                return distancia_altre - distancia_rana

        return None

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    def genera_fill(self) -> list:
        if self.__profunditat == self.MAX_PROFUNDITAT:
            return []

        estats_generats = []

        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        accions = {
            # AccionsRana.BOTAR: 2,
            AccionsRana.MOURE: 1
        }

        if self.__es_max:
            nom_a_moure = self.__nom
        else:
            nom_a_moure = self.nom_altre(self.__nom)

        for accio, salts in accions.items():
            for direccio in direccions:
                nova_posicio = self._calcula_casella(
                    posicio=self[ClauPercepcio.POSICIO][nom_a_moure], dir=direccio, magnitut=salts)

                if nova_posicio in self[ClauPercepcio.PARETS] or \
                        nova_posicio == self[ClauPercepcio.POSICIO][self.nom_altre(nom_a_moure)] or \
                        (nova_posicio[0] > 7 or nova_posicio[0] < 0) or \
                        (nova_posicio[1] > 7 or nova_posicio[1] < 0):
                    continue

                nou_estat = copy.deepcopy(self)

                if AccionsRana.BOTAR == accio:
                    pass
                    #nou_estat.pare = [(AccionsRana.ESPERAR, direccio),
                    #                  (AccionsRana.ESPERAR, direccio),
                    #                  (accio, direccio)]
                else:
                    nou_estat.pare = (self, (accio, direccio))

                nou_estat.profunditat = self.profunditat + 1
                nou_estat.es_max = not self.es_max
                nou_estat[ClauPercepcio.POSICIO][nom_a_moure] = nova_posicio

                estats_generats.append(nou_estat)

        """
        nou_estat = copy.deepcopy(self)
        nou_estat.pare = (AccionsRana.ESPERAR, Direccio.DALT)
        nou_estat.es_max = not self.es_max
        nou_estat.profunditat = self.profunditat + 1
        estats_generats.append(nou_estat)
        """

        return estats_generats

    @property
    def profunditat(self):
        return self.__profunditat

    @profunditat.setter
    def profunditat(self, value):
        self.__profunditat = value

    @property
    def es_max(self):
        return self.__es_max

    @es_max.setter
    def es_max(self, value):
        self.__es_max = value

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
