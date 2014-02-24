import os.path
import unittest


def suite():
    src_root = os.path.split(os.path.dirname(__file__))[0]
    return unittest.TestLoader().discover(src_root, pattern="*.py")