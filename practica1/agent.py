"""

ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        # secuencia bots
        self.__test = [AccionsRana.ESPERAR, AccionsRana.ESPERAR, AccionsRana.BOTAR]
        # Es cancela el bot? No la cancela, ignora les dos seguents accions
        self.__test2 = [AccionsRana.BOTAR, AccionsRana.BOTAR, AccionsRana.BOTAR]
        # Com es mou
        self.__test3 = [AccionsRana.ESPERAR, AccionsRana.MOURE, AccionsRana.MOURE]

    def pinta(self, display):
        pass

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        if len(self.__test3) == 0:
            print("esp")
            return AccionsRana.ESPERAR

        a = self.__test3.pop()
        print(a)
        return a, Direccio.DRETA
