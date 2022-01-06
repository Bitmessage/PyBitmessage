"""Mock kivy app with mock threads."""
from pybitmessage import state

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading......")
    from bitmessagemock import main
    main()
