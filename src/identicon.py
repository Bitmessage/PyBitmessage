#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
identicon.py
identicon python implementation.
by Shin Adachi <shn@glucose.jp>

= usage =

== commandline ==
>>> python identicon.py [code]

== python ==
>>> import identicon
>>> identicon.render_identicon(code, size)

Return a PIL Image class instance which have generated identicon image.
```size``` specifies `patch size`. Generated image size is 3 * ```size```.
"""
# g
# PIL Modules
import Image
import ImageDraw
import ImagePath
import ImageColor


__all__ = ['render_identicon', 'IdenticonRendererBase']


class Matrix2D(list):
    """Matrix for Patch rotation"""
    def __init__(self, initial=[0.] * 9):
        assert isinstance(initial, list) and len(initial) == 9
        list.__init__(self, initial)

    def clear(self):
        for i in xrange(9):
            self[i] = 0.

    def set_identity(self):
        self.clear()
        for i in xrange(3):
            self[i] = 1.

    def __str__(self):
        return '[%s]' % ', '.join('%3.2f' % v for v in self)

    def __mul__(self, other):
        r = []
        if isinstance(other, Matrix2D):
            for y in xrange(3):
                for x in xrange(3):
                    v = 0.0
                    for i in xrange(3):
                        v += (self[i * 3 + x] * other[y * 3 + i])
                    r.append(v)
        else:
            raise NotImplementedError
        return Matrix2D(r)

    def for_PIL(self):
        return self[0:6]

    @classmethod
    def translate(kls, x, y):
        return kls([1.0, 0.0, float(x),
                    0.0, 1.0, float(y),
                    0.0, 0.0, 1.0])

    @classmethod
    def scale(kls, x, y):
        return kls([float(x), 0.0, 0.0,
                    0.0, float(y), 0.0,
                    0.0, 0.0, 1.0])

    """
    # need `import math`
    @classmethod
    def rotate(kls, theta, pivot=None):
        c = math.cos(theta)
        s = math.sin(theta)

        matR = kls([c, -s, 0., s, c, 0., 0., 0., 1.])
        if not pivot:
            return matR
        return kls.translate(-pivot[0], -pivot[1]) * matR *
            kls.translate(*pivot)
    """
    
    @classmethod
    def rotateSquare(kls, theta, pivot=None):
        theta = theta % 4
        c = [1., 0., -1., 0.][theta]
        s = [0., 1., 0., -1.][theta]

        matR = kls([c, -s, 0., s, c, 0., 0., 0., 1.])
        if not pivot:
            return matR
        return kls.translate(-pivot[0], -pivot[1]) * matR * \
            kls.translate(*pivot)


class IdenticonRendererBase(object):
    PATH_SET = []
    
    def __init__(self, code):
        """
        @param code code for icon
        """
        if not isinstance(code, int):
            code = int(code)
        self.code = code
    
    def render(self, size):
        """
        render identicon to PIL.Image
        
        @param size identicon patchsize. (image size is 3 * [size])
        @return PIL.Image
        """
        
        # decode the code
        middle, corner, side, foreColor, backColor = self.decode(self.code)

        # make image        
        image = Image.new("RGB", (size * 3, size * 3))
        draw = ImageDraw.Draw(image)
        
        # fill background
        draw.rectangle((0, 0, image.size[0], image.size[1]), fill=0)
        
        kwds = {
            'draw': draw,
            'size': size,
            'foreColor': foreColor,
            'backColor': backColor}
        # middle patch
        self.drawPatch((1, 1), middle[2], middle[1], middle[0], **kwds)

        # side patch
        kwds['type'] = side[0]
        for i in xrange(4):
            pos = [(1, 0), (2, 1), (1, 2), (0, 1)][i]
            self.drawPatch(pos, side[2] + 1 + i, side[1], **kwds)
        
        # corner patch
        kwds['type'] = corner[0]
        for i in xrange(4):
            pos = [(0, 0), (2, 0), (2, 2), (0, 2)][i]
            self.drawPatch(pos, corner[2] + 1 + i, corner[1], **kwds)
        
        return image
                
    def drawPatch(self, pos, turn, invert, type, draw, size, foreColor,
            backColor):
        """
        @param size patch size
        """
        path = self.PATH_SET[type]
        if not path:
            # blank patch
            invert = not invert
            path = [(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)]
        patch = ImagePath.Path(path)
        if invert:
            foreColor, backColor = backColor, foreColor
        
        mat = Matrix2D.rotateSquare(turn, pivot=(0.5, 0.5)) *\
              Matrix2D.translate(*pos) *\
              Matrix2D.scale(size, size)
        
        patch.transform(mat.for_PIL())
        draw.rectangle((pos[0] * size, pos[1] * size, (pos[0] + 1) * size,
            (pos[1] + 1) * size), fill=backColor)
        draw.polygon(patch, fill=foreColor, outline=foreColor)

    ### virtual functions
    def decode(self, code):
        raise NotImplementedError


class DonRenderer(IdenticonRendererBase):
    """
    Don Park's implementation of identicon
    see : http://www.docuverse.com/blog/donpark/2007/01/19/identicon-updated-and-source-released
    """
    
    PATH_SET = [
        [(0, 0), (4, 0), (4, 4), (0, 4)],   # 0
        [(0, 0), (4, 0), (0, 4)],
        [(2, 0), (4, 4), (0, 4)],
        [(0, 0), (2, 0), (2, 4), (0, 4)],
        [(2, 0), (4, 2), (2, 4), (0, 2)],   # 4
        [(0, 0), (4, 2), (4, 4), (2, 4)],
        [(2, 0), (4, 4), (2, 4), (3, 2), (1, 2), (2, 4), (0, 4)],
        [(0, 0), (4, 2), (2, 4)],
        [(1, 1), (3, 1), (3, 3), (1, 3)],   # 8   
        [(2, 0), (4, 0), (0, 4), (0, 2), (2, 2)],
        [(0, 0), (2, 0), (2, 2), (0, 2)],
        [(0, 2), (4, 2), (2, 4)],
        [(2, 2), (4, 4), (0, 4)],
        [(2, 0), (2, 2), (0, 2)],
        [(0, 0), (2, 0), (0, 2)],
        []]                                 # 15
    MIDDLE_PATCH_SET = [0, 4, 8, 15]
    
    # modify path set
    for idx in xrange(len(PATH_SET)):
        if PATH_SET[idx]:
            p = map(lambda vec: (vec[0] / 4.0, vec[1] / 4.0), PATH_SET[idx])
            PATH_SET[idx] = p + p[:1]
    
    def decode(self, code):
        # decode the code        
        middleType  = self.MIDDLE_PATCH_SET[code & 0x03]
        middleInvert= (code >> 2) & 0x01
        cornerType  = (code >> 3) & 0x0F
        cornerInvert= (code >> 7) & 0x01
        cornerTurn  = (code >> 8) & 0x03
        sideType    = (code >> 10) & 0x0F
        sideInvert  = (code >> 14) & 0x01
        sideTurn    = (code >> 15) & 0x03
        # bug reported by Masato Hagiwara
        # http://lilyx.net/iconlang-en/
        # blue        = (code >> 16) & 0x1F
        # green       = (code >> 21) & 0x1F
        blue        = (code >> 17) & 0x1F
        green       = (code >> 22) & 0x1F
        red         = (code >> 27) & 0x1F
        
        foreColor = (red << 3, green << 3, blue << 3)
        
        return (middleType, middleInvert, 0),\
               (cornerType, cornerInvert, cornerTurn),\
               (sideType, sideInvert, sideTurn),\
               foreColor, ImageColor.getrgb('white')


def render_identicon(code, size, renderer=None):
    if not renderer:
        renderer = DonRenderer
    return renderer(code).render(size)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print 'usage: python identicon.py [CODE]....'
        raise SystemExit
    
    for code in sys.argv[1:]:
        if code.startswith('0x') or code.startswith('0X'):
            code = int(code[2:], 16)
        elif code.startswith('0'):
            code = int(code[1:], 8)
        else:
            code = int(code)
        
        icon = render_identicon(code, 24)
        icon.save('%08x.png' % code, 'PNG')
