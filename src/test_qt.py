import state

if __name__ == "__main__":
    state.qttesting = True
    print(" --------------------------------- Graphical Qt Testing --------------------------------- ")
    from bitmessagemain import main

    main()
