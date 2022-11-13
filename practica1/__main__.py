from practica1 import agent_minimax, joc


def main():
    rana = agent_minimax.Rana("Papafritta", es_max=True)
    rana2 = agent_minimax.Rana("Billy", es_max=False)
    lab = joc.Laberint([rana, rana2], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
