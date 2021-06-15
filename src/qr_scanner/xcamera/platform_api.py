from kivy.utils import platform


def play_shutter():
    # bah, apparently we need to delay the import of kivy.core.audio, lese
    # kivy cannot find a camera provider, at lease on linux. Maybe a
    # gstreamer/pygame issue?
    from kivy.core.audio import SoundLoader
    sound = SoundLoader.load("data/shutter.wav")
    sound.play()


if platform == 'android':
    from .android_api import (
        LANDSCAPE, PORTRAIT, take_picture, set_orientation, get_orientation)

else:

    # generic fallback for taking pictures. Probably not the best quality,
    # they are meant mostly for testing
    LANDSCAPE = 'landscape'
    PORTRAIT = 'portrait'

    def take_picture(camera_widget, filename, on_success):
        camera_widget.texture.save(filename, flipped=False)
        play_shutter()
        on_success(filename)

    def set_orientation(value):
        previous = get_orientation()
        print('FAKE orientation set to {}'.format(value))
        get_orientation.value = value
        return previous

    def get_orientation():
        return get_orientation.value
    get_orientation.value = PORTRAIT
