from pyzip import run as runPyzip
import unittest
import zipfile
import os
from shutil import rmtree


def checkFileEqual(self, f1, f2):
    with open(f1) as first:
        with open(f2) as second:
            self.assertEqual(first.read(), second.read())


class Test_Add(unittest.TestCase):
    def clean(self):
        try:
            os.remove("test.zip")
        except FileNotFoundError:
            pass
        try:
            rmtree("./test")
        except FileNotFoundError:
            pass

    def testAdd(self, files=["testfiles/1.md"]):
        runPyzip(["test.zip", "add", *files])

    def checkFiles(self, files):
        with zipfile.ZipFile("test.zip") as f:
            f.extractall("test")
        for file in files:
            checkFileEqual(self, file, "./test/" + os.path.basename(file))

    def testCleanAdd(self):
        self.clean()
        self.testAdd()
    # Add 1 file and check that files are the same

    def testAdd_5(self):
        self.clean()
        self.testAdd(["testfiles/1.md", "testfiles/2.md",
                     "testfiles/3.md", "testfiles/4.md", "testfiles/5.md"])
        self.checkFiles(["testfiles/1.md", "testfiles/2.md",
                         "testfiles/3.md", "testfiles/4.md", "testfiles/5.md"])

    def testAdd_1_then_2(self):
        self.clean()
        self.testAdd(["testfiles/1.md"])
        self.testAdd(["testfiles/2.md", "testfiles/3.md"])
        self.checkFiles(["testfiles/1.md", "testfiles/2.md",
                         "testfiles/3.md"])
