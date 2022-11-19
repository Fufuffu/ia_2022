from practica1 import agent_genetic, joc


def main():
    rana = agent_genetic.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
