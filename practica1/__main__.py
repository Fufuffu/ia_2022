from practica1 import agent_heuristica, joc


def main():
    rana = agent_heuristica.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
