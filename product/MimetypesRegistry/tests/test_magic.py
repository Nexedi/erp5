import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from Products.MimetypesRegistry.mime_types.magic import guessMime
from utils import input_file_path

samplefiles = [
    ('OOoWriter', 'application/vnd.sun.xml.writer'),
    ('OOoCalc', 'application/vnd.sun.xml.calc'),
    ('sxw-ooo-trolltech', 'application/vnd.sun.xml.writer'), # file from limi
    ('simplezip', 'application/zip'),
]

class TestGuessMagic(ATSiteTestCase):
    
    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.registry = self.portal.mimetypes_registry

    def test_guessMime(self):
        for filename, expected in samplefiles:
            file = open(input_file_path(filename))
            data = file.read()
            file.close()
            
            # use method direct
            got = guessMime(data)
            self.failUnlessEqual(got, expected)
            
            # use mtr-tool
            got_from_tool = self.registry.classify(data)
            self.failUnlessEqual(got_from_tool, expected)            
            
            # now cut it to the first 8k if greater
            if len(data) > 8192:
                data=data[:8192]
                got_cutted = self.registry.classify(data)
                self.failUnlessEqual(got_cutted, expected)          


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGuessMagic))
    return suite

if __name__ == '__main__':
    framework()
