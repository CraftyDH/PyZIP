from pyzip import run as runPyzip
import unittest
import zipfile
import os
import shutil
import filecmp


def checkFileEqual(self, f1, f2):
    with open(f1) as first:
        with open(f2) as second:
            self.assertEqual(first.read(), second.read())


def checkFiles(self, files):
    with zipfile.ZipFile("test.zip") as f:
        f.extractall("test")
    for file in files:
        checkFileEqual(self, file, "./test/" + os.path.basename(file))


def checkFolders(self):
    check = filecmp.dircmp("test", "check")
    self.assertFalse(bool(check.diff_files) or bool(
        check.left_only) or bool(check.right_only))


def checkZips(self):
    with zipfile.ZipFile("test.zip") as f:
        f.extractall("test")
    with zipfile.ZipFile("check.zip") as f:
        f.extractall("check")
    checkFolders(self)


def clean():
    try:
        os.remove("test.zip")
    except FileNotFoundError:
        pass
    try:
        os.remove("check.zip")
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree("./test")
    except FileNotFoundError:
        pass
    try:
        shutil.rmtree("./check")
    except FileNotFoundError:
        pass


def copyToCheck(files):
    os.mkdir('./check')
    for file in files:
        shutil.copyfile(file, "./check/" + os.path.basename(file))


def add(files):
    runPyzip(["test.zip", "add", *files])


def addcheck(files):
    runPyzip(["check.zip", "add", *files])


def remove(files):
    runPyzip(["test.zip", "remove", *files])


def extract(files=[]):
    runPyzip(["test.zip", "extract", *files, "-o", "test"])


class Test_Add(unittest.TestCase):
    def testCleanAdd(self):
        clean()
        add(["testfiles/1.md"])
        checkFiles(self, ["testfiles/1.md"])
    # Add 1 file and check that files are the same

    def testAdd_5(self):
        clean()
        add(["testfiles/1.md", "testfiles/2.md",
             "testfiles/3.md", "testfiles/4.md", "testfiles/5.md"])
        checkFiles(self, ["testfiles/1.md", "testfiles/2.md",
                          "testfiles/3.md", "testfiles/4.md", "testfiles/5.md"])

    def testAdd_1_then_2(self):
        clean()
        add(["testfiles/1.md"])
        add(["testfiles/2.md", "testfiles/3.md"])
        checkFiles(self, ["testfiles/1.md", "testfiles/2.md",
                          "testfiles/3.md"])


class Test_Remove(unittest.TestCase):
    def testCleanRemove(self):
        clean()
        addcheck(["testfiles/2.md"])

        add(["testfiles/1.md", "testfiles/2.md"])
        remove(["1.md"])
        checkZips(self)

    def testRemoveAddRemove(self):
        clean()
        addcheck(["testfiles/3.md"])

        add(["testfiles/1.md", "testfiles/2.md"])
        remove(["1.md"])
        add(["testfiles/3.md", "testfiles/4.md"])
        remove(["2.md", "4.md"])

        checkZips(self)


class Test_Extract(unittest.TestCase):
    def testExtract(self):
        clean()

        copyToCheck(["testfiles/1.md"])

        add(["testfiles/1.md"])
        extract()
        checkFolders(self)

    def testExtract_1(self):
        clean()

        copyToCheck(["testfiles/2.md"])

        add(["testfiles/1.md", "testfiles/2.md"])
        extract(["testfiles/2.md"])
        checkFolders(self)
