from practica1 import agent_profunditat, joc


def main():
    rana = agent_profunditat.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
