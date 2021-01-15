"""This module is for thread start."""
import state
import sys
from termcolor import colored
print(colored('kivy is not supported at the moment for this version..........', 'red'))
sys.exit()

from bitmessagemain import main

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading......")
    main()
