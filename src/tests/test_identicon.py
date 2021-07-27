"""Tests for qidenticon"""

import atexit
import unittest

try:
    from PyQt5 import QtGui, QtWidgets
    from xvfbwrapper import Xvfb
    from pybitmessage import qidenticon
except ImportError:
    Xvfb = None
    # raise unittest.SkipTest(
    #     'Skipping graphical test, because of no PyQt or xvfbwrapper')
else:
    vdisplay = Xvfb(width=1024, height=768)
    vdisplay.start()
    atexit.register(vdisplay.stop)


sample_code = 0x3fd4bf901b9d4ea1394f0fb358725b28
sample_size = 48


@unittest.skipUnless(
    Xvfb, 'Skipping graphical test, because of no PyQt or xvfbwrapper')
class TestIdenticon(unittest.TestCase):
    """QIdenticon implementation test case"""

    @classmethod
    def setUpClass(cls):
        """Instantiate QtWidgets.QApplication"""
        cls.app = QtWidgets.QApplication([])

    def test_qidenticon_samples(self):
        """Generate 4 qidenticon samples and check their properties"""
        icon_simple = qidenticon.render_identicon(sample_code, sample_size)
        self.assertIsInstance(icon_simple, QtGui.QPixmap)
        self.assertEqual(icon_simple.height(), sample_size * 3)
        self.assertEqual(icon_simple.width(), sample_size * 3)
        self.assertFalse(icon_simple.hasAlphaChannel())

        # icon_sample = QtGui.QPixmap()
        # icon_sample.load('../images/qidenticon.png')
        # self.assertFalse(
        #     icon_simple.toImage(), icon_sample.toImage())

        icon_x = qidenticon.render_identicon(
            sample_code, sample_size, opacity=0)
        self.assertTrue(icon_x.hasAlphaChannel())
