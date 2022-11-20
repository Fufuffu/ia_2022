from practica1 import agent_amplada, joc


def main():
    rana = agent_amplada.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
