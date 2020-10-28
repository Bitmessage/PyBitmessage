import os


_files = (
    'keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat',
    '.api_started', 'unittest.lock'
)


def cleanup(home=None, files=_files):
    """Cleanup application files"""
    if not home:
        import state
        home = state.appdata
    for pfile in files:
        try:
            os.remove(os.path.join(home, pfile))
        except OSError:
            pass
