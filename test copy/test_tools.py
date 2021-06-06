import unittest
import os
from tools import sanitizePath


class Test_Sanitization(unittest.TestCase):
    def test(self):
        self.assertEqual(sanitizePath("path"), "path")
        self.assertEqual(sanitizePath("C:/path"), "path")
        self.assertEqual(sanitizePath("D://path"), "path")
        self.assertEqual(sanitizePath("../../../../path"), "path")
        self.assertEqual(sanitizePath("path/path/path"),
                         "path{0}path{0}path".format(os.sep))
        self.assertEqual(sanitizePath("path/path/../path"),
                         "path{0}path{0}path".format(os.sep))
        self.assertEqual(sanitizePath("path\\path\\path"),
                         "path{0}path{0}path".format(os.sep))
        self.assertEqual(sanitizePath("path//path//path"),
                         "path{0}path{0}path".format(os.sep))
        self.assertEqual(sanitizePath("path\\\\path\\\\path"),
                         "path{0}path{0}path".format(os.sep))

