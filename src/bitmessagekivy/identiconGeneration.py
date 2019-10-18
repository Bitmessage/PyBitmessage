"""
src/identiconGeneration.py
=================================
"""
# pylint: disable=import-error
import hashlib
from io import BytesIO

from PIL import Image
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image as kiImage
""" Core classes for loading images and converting them to a Texture.
The raw image data can be keep in memory for further access """


# constants
RESOLUTION = 128, 128
V_RESOLUTION = 7, 7
BACKGROUND_COLOR = 255, 255, 255, 255
MODE = "RGB"


def generate(Generate_string=None):
    """Generating string"""
    hash_string = generate_hash(Generate_string)
    color = random_color(hash_string)
    image = Image.new(MODE, V_RESOLUTION, BACKGROUND_COLOR)
    image = generate_image(image, color, hash_string)
    image = image.resize(RESOLUTION, 0)

    data = BytesIO()
    image.save(data, format='png')
    data.seek(0)
    # yes you actually need this
    im = CoreImage(BytesIO(data.read()), ext='png')
    beeld = kiImage()
    # only use this line in first code instance
    beeld.texture = im.texture
    return beeld
    # image.show()


def generate_hash(string):
    """Generating hash"""
    try:
        # make input case insensitive
        string = str.lower(string)
        hash_object = hashlib.md5(str.encode(string))
        print(hash_object.hexdigest())

        # returned object is a hex string
        return hash_object.hexdigest()

    except IndexError:
        print("Error: Please enter a string as an argument.")


def random_color(hash_string):
    """Getting random color"""
    # remove first three digits from hex string
    split = 6
    rgb = hash_string[:split]

    split = 2
    r = rgb[:split]
    g = rgb[split:2 * split]
    b = rgb[2 * split:3 * split]

    color = (int(r, 16), int(g, 16),
             int(b, 16), 0xFF)

    return color


def generate_image(image, color, hash_string):
    """Generating images"""
    hash_string = hash_string[6:]

    lower_x = 1
    lower_y = 1
    upper_x = int(V_RESOLUTION[0] / 2) + 1
    upper_y = V_RESOLUTION[1] - 1
    limit_x = V_RESOLUTION[0] - 1
    index = 0

    for x in range(lower_x, upper_x):
        for y in range(lower_y, upper_y):
            if int(hash_string[index], 16) % 2 == 0:
                image.putpixel((x, y), color)
                image.putpixel((limit_x - x, y), color)

            index = index + 1

    return image
