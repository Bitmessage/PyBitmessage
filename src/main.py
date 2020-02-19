"""This module is for thread start."""
import state
from bitmessagemain import main

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading for PyBitmessage......")
    from bitmessagemain import main
    main()
