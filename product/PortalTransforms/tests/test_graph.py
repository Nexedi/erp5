from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from utils import input_file_path
FILE_PATH = input_file_path("demo1.pdf")

class TestGraph(ATSiteTestCase):

    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.engine = self.portal.portal_transforms

    def testGraph(self):
        data = open(FILE_PATH, 'r').read()
        requirements = self.engine._policies.get('text/plain', [])
        if requirements:
            out = self.engine.convertTo('text/plain', data, filename=FILE_PATH)
            self.failUnless(out.getData())

    def testIdentity(self):
        orig = 'Some text'
        converted = self.engine.convertTo(
            'text/plain', 'Some text', mimetype='text/plain')
        self.assertEquals(orig, str(converted))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGraph))
    return suite
