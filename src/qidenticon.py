#!/usr/bin/env python
# -*- coding:utf-8 -*-

###
# qidenticon.py is Licesensed under FreeBSD License.
# (http://www.freebsd.org/copyright/freebsd-license.html)
#
# Copyright 2013 "Sendiulo". All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###

###
# identicon.py is Licesensed under FreeBSD License.
# (http://www.freebsd.org/copyright/freebsd-license.html)
#
# Copyright 1994-2009 Shin Adachi. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###

"""
qidenticon.py
identicon python implementation with QPixmap output
by sendiulo <sendiulo@gmx.net>

based on
identicon.py
identicon python implementation.
by Shin Adachi <shn@glucose.jp>

= usage =

== python ==
>>> import qtidenticon
>>> qtidenticon.render_identicon(code, size)

Return a PIL Image class instance which have generated identicon image.
```size``` specifies `patch size`. Generated image size is 3 * ```size```.
"""

# we probably don't need all of them, but i don't want to check now
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

__all__ = ['render_identicon', 'IdenticonRendererBase']

class IdenticonRendererBase(object):
    PATH_SET = []
    
    def __init__(self, code):
        """
        @param code code for icon
        """
        if not isinstance(code, int):
            code = int(code)
        self.code = code
    
    def render(self, size, twoColor, transparent, penwidth):
        """
        render identicon to QPixmap
        
        @param size identicon patchsize. (image size is 3 * [size])
        @return QPixmap
        """
        
        # decode the code
        middle, corner, side, foreColor, secondColor, swap_cross = self.decode(self.code, twoColor)

        # make image
        image = QPixmap(QSize(size * 3 +penwidth, size * 3 +penwidth))
        
        # fill background
        backColor = QtGui.QColor(255,255,255,(not transparent) * 255)
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
        kwds['type'] = side[0]
        for i in xrange(4):
            pos = [(1, 0), (2, 1), (1, 2), (0, 1)][i]
            image = self.drawPatchQt(pos, side[2] + 1 + i, side[1], **kwds)
            
        # corner patch
        kwds['foreColor'] = secondColor
        kwds['type'] = corner[0]
        for i in xrange(4):
            pos = [(0, 0), (2, 0), (2, 2), (0, 2)][i]
            image = self.drawPatchQt(pos, corner[2] + 1 + i, corner[1], **kwds)
        
        return image
                

    def drawPatchQt(self, pos, turn, invert, type, image, size, foreColor,
            backColor, penwidth):
        """
        @param size patch size
        """
        path = self.PATH_SET[type]
        if not path:
            # blank patch
            invert = not invert
            path = [(0., 0.), (1., 0.), (1., 1.), (0., 1.), (0., 0.)]

        
        polygon = QPolygonF([QPointF(x*size,y*size) for x,y in path])
        
        rot = turn % 4
        rect = [QPointF(0.,0.), QPointF(size, 0.), QPointF(size, size), QPointF(0., size)]
        rotation = [0,90,180,270]
        
        nopen = QtGui.QPen(foreColor, Qt.NoPen)
        foreBrush = QtGui.QBrush(foreColor, Qt.SolidPattern)
        if penwidth > 0:
            pen_color = QtGui.QColor(223, 223, 223)
            pen = QtGui.QPen(pen_color, Qt.SolidPattern)
            pen.setWidth(penwidth)
        
        painter = QPainter()
        painter.begin(image)
        painter.setPen(nopen)
        
        painter.translate(pos[0]*size +penwidth/2, pos[1]*size +penwidth/2)
        painter.translate(rect[rot])
        painter.rotate(rotation[rot])
        
        if invert:
            # subtract the actual polygon from a rectangle to invert it
            rect_polygon = QPolygonF(rect)
            polygon = rect_polygon.subtracted(polygon)
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
    
    def decode(self, code, twoColor):
        # decode the code
        shift  = 0; middleType  = (code >> shift) & 0x03
        shift += 2; middleInvert= (code >> shift) & 0x01
        shift += 1; cornerType  = (code >> shift) & 0x0F
        shift += 4; cornerInvert= (code >> shift) & 0x01
        shift += 1; cornerTurn  = (code >> shift) & 0x03
        shift += 2; sideType    = (code >> shift) & 0x0F
        shift += 4; sideInvert  = (code >> shift) & 0x01
        shift += 1; sideTurn    = (code >> shift) & 0x03
        shift += 2; blue        = (code >> shift) & 0x1F
        shift += 5; green       = (code >> shift) & 0x1F
        shift += 5; red         = (code >> shift) & 0x1F
        shift += 5; second_blue = (code >> shift) & 0x1F
        shift += 5; second_green= (code >> shift) & 0x1F
        shift += 5; second_red  = (code >> shift) & 0x1F
        shift += 1; swap_cross  = (code >> shift) & 0x01
        
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


def render_identicon(code, size, twoColor=False, transparent=False, penwidth=0, renderer=None):
    if not renderer:
        renderer = DonRenderer
    return renderer(code).render(size, twoColor, transparent, penwidth)