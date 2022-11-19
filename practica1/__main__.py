from practica1 import agent_minimax, joc


def main():
    rana = agent_minimax.Rana("Miquel")
    rana2 = agent_minimax.Rana("Tomeu")
    lab = joc.Laberint([rana, rana2], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
