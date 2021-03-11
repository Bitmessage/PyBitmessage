"""This module is for thread start."""
import state

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading......")
    # from bitmessagemain import main
    from bitmessagemain_mock_test import main
    main()
