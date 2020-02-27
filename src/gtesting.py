import os
import shutil

if __name__ == "__main__":
    APPNAME = "PyBitmessage"
    if os.path.isdir(os.path.expanduser(os.path.join("~", ".config/" + APPNAME + "/"))):
        shutil.rmtree(os.path.expanduser(os.path.join("~", ".config/" + APPNAME + "/")))
    else:
        pass
    import state
    state.qttesting = True
    print(" --------------------------------- Graphical Qt Testing --------------------------------- ")
    from bitmessagemain import main
    main()
