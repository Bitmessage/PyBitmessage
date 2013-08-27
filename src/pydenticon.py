"""
Python implementation of PHP Identicons, found here:
http://sourceforge.net/projects/identicons/

Licensed under the GPLv3.
"""
from PIL import Image, ImageDraw, ImagePath, ImageColor
from math import fabs as abs
from hashlib import md5
import StringIO

class Pydenticon:
    """
    Generate an identicon.

    """

    WHITE = (255, 255, 255)

    def __init__(self, input, size = 128):
        self.hash = md5(input).hexdigest()
        self.size = size

    def as_string(self):
        """
        Return the image as a string representation of a PNG file.

        """
        if not hasattr(self, 'image'):
            self.image = self._render()
        output = StringIO.StringIO()
        self.image.save(output, format="PNG")
        contents = output.getvalue()
        output.close()
        return contents

    def save(self, filename):
        """
        Save the result as a PNG file.

        """
        if not hasattr(self, 'image'):
            self.image = self._render()
        self.image.save(filename, format="PNG")

    def _get_sprite(self, shape, r, g, b, rotation):
        """
        Generate sprite for corners and sides and returnro a PIL.Image object.

        """        
        sprite = Image.new("RGB", (self.size, self.size),  self.WHITE)
        
        if shape == 0: # triangle
            points = [
                    0.5,1,
                    1,0,
                    1,1
            ]
        elif shape == 1: #parallelogram
            points = [
                    0.5,0,
                    1,0,
                    0.5,1,
                    0,1
            ]
        elif shape == 2: # mouse ears
            points = [
                    0.5,0,
                    1,0,
                    1,1,
                    0.5,1,
                    1,0.5
            ]
        elif shape == 3: # ribbon
            points = [
                    0,0.5,
                    0.5,0,
                    1,0.5,
                    0.5,1,
                    0.5,0.5
            ]
        elif shape == 4: # sails
            points = [
                    0,0.5,
                    1,0,
                    1,1,
                    0,1,
                    1,0.5
            ]
        elif shape == 5: # fins
            points = [
                    1,0,
                    1,1,
                    0.5,1,
                    1,0.5,
                    0.5,0.5
            ]
        elif shape == 6: # beak
            points = [
                    0,0,
                    1,0,
                    1,0.5,
                    0,0,
                    0.5,1,
                    0,1
            ]
        elif shape == 7: # chevron
            points = [
                    0,0,
                    0.5,0,
                    1,0.5,
                    0.5,1,
                    0,1,
                    0.5,0.5
            ]
        elif shape == 8: # fish
            points = [
                    0.5,0,
                    0.5,0.5,
                    1,0.5,
                    1,1,
                    0.5,1,
                    0.5,0.5,
                    0,0.5
            ]
        elif shape == 9: # kite
            points = [
                    0,0,
                    1,0,
                    0.5,0.5,
                    1,0.5,
                    0.5,1,
                    0.5,0.5,
                    0,1
            ]
        elif shape == 10: # trough
            points = [
                    0,0.5,
                    0.5,1,
                    1,0.5,
                    0.5,0,
                    1,0,
                    1,1,
                    0,1
            ]
        elif shape == 11: # rays
            points = [
                    0.5,0,
                    1,0,
                    1,1,
                    0.5,1,
                    1,0.75,
                    0.5,0.5,
                    1,0.25
            ]
        elif shape == 12: # double rhombus
            points = [
                    0,0.5,
                    0.5,0,
                    0.5,0.5,
                    1,0,
                    1,0.5,
                    0.5,1,
                    0.5,0.5,
                    0,1
            ]
        elif shape == 13: # crown
            points = [
                    0,0,
                    1,0,
                    1,1,
                    0,1,
                    1,0.5,
                    0.5,0.25,
                    0.5,0.75,
                    0,0.5,
                    0.5,0.25
            ]
        elif shape == 14: # radioactive
            points = [
                    0,0.5,
                    0.5,0.5,
                    0.5,0,
                    1,0,
                    0.5,0.5,
                    1,0.5,
                    0.5,1,
                    0.5,0.5,
                    0,1
            ]
        else: # tiles
            points = [
                    0,0,
                    1,0,
                    0.5,0.5,
                    0.5,0,
                    0,0.5,
                    1,0.5,
                    0.5,1,
                    0.5,0.5,
                    0,1
            ]
            
        # apply ratios
        for i in range(0, len(points)):
            points[i] = points[i] * self.size

        draw = ImageDraw.Draw(sprite)
        draw.polygon(points, fill=(r, g, b))

	for i in range(rotation):
            sprite = sprite.rotate(90)

        return sprite
    
    def _get_center(self, shape, fR, fG, fB, bR, bG, bB, useBg):
        """
        Generate sprite for center block and return a PIL.Image object.

        """
        sprite = Image.new("RGB", (self.size, self.size), self.WHITE)

        # make sure there's enough contrast before we use background color of side sprite
        sufficient_contrast = (
            abs(fR - bR) > 127 or abs(fG - bG) > 127 or abs(fB - bB) > 127
        )
        if useBg > 0 and sufficient_contrast:            
            bg = (bR, bG, bB)
        else:            
            bg = (255, 255, 255)        
        
        if shape == 0: # empty
            points = []

        elif shape == 1: # fill
            points = [
                    0,0,
                    1,0,
                    1,1,
                    0,1
            ]
        elif shape == 2: # diamond
            points = [
                    0.5,0,
                    1,0.5,
                    0.5,1,
                    0,0.5
            ]
        elif shape ==  3: # reverse diamond
            points = [
                    0,0,
                    1,0,
                    1,1,
                    0,1,
                    0,0.5,
                    0.5,1,
                    1,0.5,
                    0.5,0,
                    0,0.5
            ]
        elif shape ==  4: # cross
            points = [
                    0.25,0,
                    0.75,0,
                    0.5,0.5,
                    1,0.25,
                    1,0.75,
                    0.5,0.5,
                    0.75,1,
                    0.25,1,
                    0.5,0.5,
                    0,0.75,
                    0,0.25,
                    0.5,0.5
            ]
        elif shape ==  5: # morning star
            points = [
                    0,0,
                    0.5,0.25,
                    1,0,
                    0.75,0.5,
                    1,1,
                    0.5,0.75,
                    0,1,
                    0.25,0.5
            ]
        elif shape ==  6: # small square
            points = [
                    0.33,0.33,
                    0.67,0.33,
                    0.67,0.67,
                    0.33,0.67
            ]
        elif shape ==  7: # checkerboard
            points = [
                    0,0,
                    0.33,0,
                    0.33,0.33,
                    0.66,0.33,
                    0.67,0,
                    1,0,
                    1,0.33,
                    0.67,0.33,
                    0.67,0.67,
                    1,0.67,
                    1,1,
                    0.67,1,
                    0.67,0.67,
                    0.33,0.67,
                    0.33,1,
                    0,1,
                    0,0.67,
                    0.33,0.67,
                    0.33,0.33,
                    0,0.33
            ]

        # apply ratios
        for i in range(0, len(points)):
            points[i] = points[i] * self.size

        if len(points) > 0:
            draw = ImageDraw.Draw(sprite)
            draw.polygon(points, fill=(fR, fG, fB))

        return sprite        

    def _render(self):
        """
        Render the image and return the PIL.Image object.

        """
        # parse hash string
        corner_sprite_shape = int(self.hash[0:1], 16)
        side_sprite_shape   = int(self.hash[1:2], 16)
        center_sprite_shape = int(self.hash[2:3], 16) & 7

        corner_sprite_rot = int(self.hash[3:4], 16) & 3
        side_sprite_rot   = int(self.hash[4:5], 16) & 3
        center_sprite_bg  = int(self.hash[5:6], 16) % 2

        # corner sprite foreground color
        corner_sprite_fg_r = int(self.hash[6:8], 16)
        corner_sprite_fg_g = int(self.hash[8:10], 16)
        corner_sprite_fg_b = int(self.hash[10:12], 16)

        # side sprite foreground color
        side_sprite_fg_r = int(self.hash[12:14], 16)
        side_sprite_fg_g = int(self.hash[14:16], 16)
        side_sprite_fg_b = int(self.hash[16:18], 16)

        # final angle of rotation
        angle = int(self.hash[18:20], 16)

        # start with blank 3X sized identicon
        identicon = Image.new("RGB", (self.size*3, self.size*3), self.WHITE)

        # generate corner sprites
        corner = self._get_sprite(
            corner_sprite_shape,
            corner_sprite_fg_r,
            corner_sprite_fg_g,
            corner_sprite_fg_b,
            corner_sprite_rot
        )        
        identicon.paste(corner, (0, 0))        
        corner = corner.rotate(90)
        identicon.paste(corner, (0, self.size*2))
        corner = corner.rotate(90)
        identicon.paste(corner, (self.size*2, self.size*2))
        corner = corner.rotate(90)
        identicon.paste(corner, (self.size*2, 0))        

        # generate side sprites
        side = self._get_sprite(
            side_sprite_shape,
            side_sprite_fg_r,
            side_sprite_fg_g,
            side_sprite_fg_b,
            side_sprite_rot
        )        
        identicon.paste(side, (self.size, 0))
        side = side.rotate(90)
        identicon.paste(side, (0, self.size))
        side = side.rotate(90)
        identicon.paste(side, (self.size, self.size*2))
        side = side.rotate(90)
        identicon.paste(side, (self.size*2, self.size))

        # generate center sprite
        center = self._get_center(
            center_sprite_shape,
            corner_sprite_fg_r,
            corner_sprite_fg_g,
            corner_sprite_fg_b,
            side_sprite_fg_r,
            side_sprite_fg_g,
            side_sprite_fg_b,
            center_sprite_bg
        )        
        identicon.paste(center, (self.size, self.size))        

        # resize image
        resized = identicon.resize(
            (self.size, self.size),
            Image.ANTIALIAS
        )

        return resized