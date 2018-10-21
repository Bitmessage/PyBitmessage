"""
src/bitmessageqt/utils.py
=========================

"""

import hashlib
import os

from PyQt4 import QtGui

import state
from addresses import addBMIfNotPresent
from bmconfigparser import BMConfigParser

str_broadcast_subscribers = '[Broadcast subscribers]'
str_chan = '[chan]'


def identiconize(address):
    """Return an identicon derived from an address"""
    # pylint: disable=too-many-locals
    size = 48

    if not BMConfigParser().getboolean('bitmessagesettings', 'useidenticons'):
        return QtGui.QIcon()

    # If you include another identicon library, please generate an
    # example identicon with the following md5 hash:
    # 3fd4bf901b9d4ea1394f0fb358725b28

    identicon_lib = BMConfigParser().safeGet(
        'bitmessagesettings', 'identiconlib', 'qidenticon_two_x')

    # As an 'identiconsuffix' you could put "@bitmessge.ch" or "@bm.addr"
    # to make it compatible with other identicon generators. (Note however,
    # that E-Mail programs might convert the BM-address to lowercase first.)
    # It can be used as a pseudo-password to salt the generation of
    # the identicons to decrease the risk of attacks where someone creates
    # an address to mimic someone else's identicon.
    identiconsuffix = BMConfigParser().get('bitmessagesettings', 'identiconsuffix')
    idcon = QtGui.QIcon()

    if identicon_lib[:len('qidenticon')] == 'qidenticon':
        # print identicon_lib
        # originally by:
        # :Author:Shin Adachi <shn@glucose.jp>
        # Licesensed under FreeBSD License.
        # stripped from PIL and uses QT instead (by sendiulo, same license)
        import qidenticon
        addr_hash = hashlib.md5(addBMIfNotPresent(address) + identiconsuffix).hexdigest()
        use_two_colors = (identicon_lib[:len('qidenticon_two')] == 'qidenticon_two')
        opacity = int(not((identicon_lib == 'qidenticon_x') | (identicon_lib == 'qidenticon_two_x') |
                          (identicon_lib == 'qidenticon_b') | (identicon_lib == 'qidenticon_two_b'))) * 255
        penwidth = 0
        image = qidenticon.render_identicon(int(addr_hash, 16), size, use_two_colors, opacity, penwidth)

    elif identicon_lib == 'pydenticon':
        # Here you could load pydenticon.py (just put it in the "src" folder of your Bitmessage source)
        # It is not included in the source, because it is licensed under GPLv3
        # GPLv3 is a copyleft license that would influence our licensing
        # Find the source here: http://boottunes.googlecode.com/svn-history/r302/trunk/src/pydenticon.py
        # note that it requires PIL to be installed: http://www.pythonware.com/products/pil/
        try:
            from pydenticon import Pydenticon
        except ImportError:
            pass
        else:
            idcon_render = Pydenticon(addBMIfNotPresent(address) + identiconsuffix, size * 3)
            rendering = idcon_render._render()  # pylint: disable=protected-access
            data = rendering.convert("RGBA").tostring("raw", "RGBA")
            qim = QtGui.QImage(data, size, size, QtGui.QImage.Format_ARGB32)
            image = QtGui.QPixmap.fromImage(qim)

    idcon.addPixmap(image, QtGui.QIcon.Normal, QtGui.QIcon.Off)

    return idcon


def avatarize(address):
    """
    loads a supported image for the given address' hash form 'avatars' folder
    falls back to default avatar if 'default.*' file exists
    falls back to identiconize(address)
    """
    # pylint: disable=global-statement
    global str_broadcast_subscribers

    idcon = QtGui.QIcon()
    addr_hash = hashlib.md5(addBMIfNotPresent(address)).hexdigest()
    if address == str_broadcast_subscribers:
        # don't hash [Broadcast subscribers]
        addr_hash = address
    # http://pyqt.sourceforge.net/Docs/PyQt4/qimagereader.html#supportedImageFormats
    # print QImageReader.supportedImageFormats ()
    # QImageReader.supportedImageFormats ()
    extensions = ['PNG', 'GIF', 'JPG', 'JPEG', 'SVG', 'BMP', 'MNG', 'PBM', 'PGM', 'PPM', 'TIFF', 'XBM', 'XPM', 'TGA']
    # try to find a specific avatar
    for ext in extensions:
        lower_hash = state.appdata + 'avatars/' + addr_hash + '.' + ext.lower()
        upper_hash = state.appdata + 'avatars/' + addr_hash + '.' + ext.upper()
        if os.path.isfile(lower_hash):
            # print 'found avatar of ', address
            idcon.addFile(lower_hash)
            return idcon
        elif os.path.isfile(upper_hash):
            # print 'found avatar of ', address
            idcon.addFile(upper_hash)
            return idcon
    # if we haven't found any, try to find a default avatar
    for ext in extensions:
        lower_default = state.appdata + 'avatars/' + 'default.' + ext.lower()
        upper_default = state.appdata + 'avatars/' + 'default.' + ext.upper()
        if os.path.isfile(lower_default):
            idcon.addFile(lower_default)
            return idcon
        elif os.path.isfile(upper_default):
            idcon.addFile(upper_default)
            return idcon
    # If no avatar is found
    return identiconize(address)
