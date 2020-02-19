# pylint: disable=too-many-locals,too-many-arguments,too-many-function-args
"""
Usage
-----

>>> import qtidenticon
>>> qtidenticon.render_identicon(code, size)

Return a PIL Image class instance which have generated identicon image.
``size`` specifies `patch size`. Generated image size is 3 * ``size``.
"""

from PyQt4 import QtGui
from PyQt4.QtCore import QPointF, QSize, Qt
from PyQt4.QtGui import QPainter, QPixmap, QPolygonF


class IdenticonRendererBase(object):
    """Encapsulate methods around rendering identicons"""

    PATH_SET = []

    def __init__(self, code):
        """
        :param code: code for icon
        """
        if not isinstance(code, int):
            code = int(code)
        self.code = code

    def render(self, size, twoColor, opacity, penwidth):
        """
        render identicon to QPicture

        :param size: identicon patchsize. (image size is 3 * [size])
        :returns: :class:`QPicture`
        """

        # decode the code
        middle, corner, side, foreColor, secondColor, swap_cross = self.decode(self.code, twoColor)

        # make image
        image = QPixmap(QSize(size * 3 + penwidth, size * 3 + penwidth))

        # fill background
        backColor = QtGui.QColor(255, 255, 255, opacity)
        image.fill(backColor)

        kwds = {
            'image': image,
            'size': size,
            'foreColor': foreColor if swap_cross else secondColor,
            'penwidth': penwidth,
            'backColor': backColor}

        # middle patch
        image = self.drawPatchQt((1, 1), middle[2], middle[1], middle[0], **kwds)

        # side patch
        kwds['foreColor'] = foreColor
        kwds['patch_type'] = side[0]
        for i in xrange(4):
            pos = [(1, 0), (2, 1), (1, 2), (0, 1)][i]
            image = self.drawPatchQt(pos, side[2] + 1 + i, side[1], **kwds)

        # corner patch
        kwds['foreColor'] = secondColor
        kwds['patch_type'] = corner[0]
        for i in xrange(4):
            pos = [(0, 0), (2, 0), (2, 2), (0, 2)][i]
            image = self.drawPatchQt(pos, corner[2] + 1 + i, corner[1], **kwds)

        return image

    def drawPatchQt(self, pos, turn, invert, patch_type, image, size, foreColor,
                    backColor, penwidth):  # pylint: disable=unused-argument
        """
        :param size: patch size
        """
        path = self.PATH_SET[patch_type]
        if not path:
            # blank patch
            invert = not invert
            path = [(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)]

        polygon = QPolygonF([QPointF(x * size, y * size) for x, y in path])

        rot = turn % 4
        rect = [QPointF(0., 0.), QPointF(size, 0.), QPointF(size, size), QPointF(0., size)]
        rotation = [0, 90, 180, 270]

        nopen = QtGui.QPen(foreColor, Qt.NoPen)
        foreBrush = QtGui.QBrush(foreColor, Qt.SolidPattern)
        if penwidth > 0:
            pen_color = QtGui.QColor(255, 255, 255)
            pen = QtGui.QPen(pen_color, Qt.SolidPattern)
            pen.setWidth(penwidth)

        painter = QPainter()
        painter.begin(image)
        painter.setPen(nopen)

        painter.translate(pos[0] * size + penwidth / 2, pos[1] * size + penwidth / 2)
        painter.translate(rect[rot])
        painter.rotate(rotation[rot])

        if invert:
            # subtract the actual polygon from a rectangle to invert it
            poly_rect = QPolygonF(rect)
            polygon = poly_rect.subtracted(polygon)
        painter.setBrush(foreBrush)
        if penwidth > 0:
            # draw the borders
            painter.setPen(pen)
            painter.drawPolygon(polygon, Qt.WindingFill)
        # draw the fill
        painter.setPen(nopen)
        painter.drawPolygon(polygon, Qt.WindingFill)

        painter.end()

        return image

    def decode(self, code, twoColor):
        """virtual functions"""

        raise NotImplementedError


class DonRenderer(IdenticonRendererBase):
    """
    Don Park's implementation of identicon
    see: http://www.docuverse.com/blog/donpark/2007/01/19/identicon-updated-and-source-released
    """

    PATH_SET = [
        # [0] full square:
        [(0, 0), (4, 0), (4, 4), (0, 4)],
        # [1] right-angled triangle pointing top-left:
        [(0, 0), (4, 0), (0, 4)],
        # [2] upwardy triangle:
        [(2, 0), (4, 4), (0, 4)],
        # [3] left half of square, standing rectangle:
        [(0, 0), (2, 0), (2, 4), (0, 4)],
        # [4] square standing on diagonale:
        [(2, 0), (4, 2), (2, 4), (0, 2)],
        # [5] kite pointing topleft:
        [(0, 0), (4, 2), (4, 4), (2, 4)],
        # [6] Sierpinski triangle, fractal triangles:
        [(2, 0), (4, 4), (2, 4), (3, 2), (1, 2), (2, 4), (0, 4)],
        # [7] sharp angled lefttop pointing triangle:
        [(0, 0), (4, 2), (2, 4)],
        # [8] small centered square:
        [(1, 1), (3, 1), (3, 3), (1, 3)],
        # [9] two small triangles:
        [(2, 0), (4, 0), (0, 4), (0, 2), (2, 2)],
        # [10] small topleft square:
        [(0, 0), (2, 0), (2, 2), (0, 2)],
        # [11] downpointing right-angled triangle on bottom:
        [(0, 2), (4, 2), (2, 4)],
        # [12] uppointing right-angled triangle on bottom:
        [(2, 2), (4, 4), (0, 4)],
        # [13] small rightbottom pointing right-angled triangle on topleft:
        [(2, 0), (2, 2), (0, 2)],
        # [14] small lefttop pointing right-angled triangle on topleft:
        [(0, 0), (2, 0), (0, 2)],
        # [15] empty:
        []]
    # get the [0] full square, [4] square standing on diagonale, [8] small centered square, or [15] empty tile:
    MIDDLE_PATCH_SET = [0, 4, 8, 15]

    # modify path set
    for idx in xrange(len(PATH_SET)):
        if PATH_SET[idx]:
            p = [(vec[0] / 4.0, vec[1] / 4.0) for vec in PATH_SET[idx]]
            PATH_SET[idx] = p + p[:1]

    def decode(self, code, twoColor):
        """decode the code"""

        shift = 0
        middleType = (code >> shift) & 0x03
        shift += 2
        middleInvert = (code >> shift) & 0x01
        shift += 1
        cornerType = (code >> shift) & 0x0F
        shift += 4
        cornerInvert = (code >> shift) & 0x01
        shift += 1
        cornerTurn = (code >> shift) & 0x03
        shift += 2
        sideType = (code >> shift) & 0x0F
        shift += 4
        sideInvert = (code >> shift) & 0x01
        shift += 1
        sideTurn = (code >> shift) & 0x03
        shift += 2
        blue = (code >> shift) & 0x1F
        shift += 5
        green = (code >> shift) & 0x1F
        shift += 5
        red = (code >> shift) & 0x1F
        shift += 5
        second_blue = (code >> shift) & 0x1F
        shift += 5
        second_green = (code >> shift) & 0x1F
        shift += 5
        second_red = (code >> shift) & 0x1F
        shift += 1
        swap_cross = (code >> shift) & 0x01

        middleType = self.MIDDLE_PATCH_SET[middleType]

        foreColor = (red << 3, green << 3, blue << 3)
        foreColor = QtGui.QColor(*foreColor)

        if twoColor:
            secondColor = (second_blue << 3, second_green << 3, second_red << 3)
            secondColor = QtGui.QColor(*secondColor)
        else:
            secondColor = foreColor

        return (middleType, middleInvert, 0),\
               (cornerType, cornerInvert, cornerTurn),\
               (sideType, sideInvert, sideTurn),\
            foreColor, secondColor, swap_cross


def render_identicon(code, size, twoColor=False, opacity=255, penwidth=0, renderer=None):
    """Render an image"""

    if not renderer:
        renderer = DonRenderer
    return renderer(code).render(size, twoColor, opacity, penwidth)
