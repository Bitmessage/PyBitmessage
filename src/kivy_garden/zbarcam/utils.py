from kivy.utils import platform
from PIL import ImageOps


def is_android():
    return platform == 'android'


def is_ios():
    return platform == 'ios'


def fix_android_image(pil_image):
    """
    On Android, the image seems mirrored and rotated somehow, refs #32.
    """
    if not is_android():
        return pil_image
    pil_image = pil_image.rotate(90)
    pil_image = ImageOps.mirror(pil_image)
    return pil_image
