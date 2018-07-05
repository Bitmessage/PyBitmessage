"""This module is for thread start."""
from bitmessagemain import main
import state

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading......")
    main()
