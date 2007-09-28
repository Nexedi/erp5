import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from Products.MimetypesRegistry.mime_types import text_plain
from Products.MimetypesRegistry.mime_types import text_xml
from Products.MimetypesRegistry.mime_types import application_octet_stream
from utils import input_file_path

class TestMimeTypesclass(ATSiteTestCase):

    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.registry = self.portal.mimetypes_registry

    def testClassify(self):
        reg = self.registry
        c = reg._classifiers()
        self.failUnless(c[0].name().startswith("Extensible Markup Language"),
                        c[0].name())

        #Real XML
        data = "<?xml version='1.0'?><foo>bar</foo>"
        mt = reg.classify(data)
        self.failUnless(isinstance(mt, text_xml), str(mt))

        # with leading whitespace (http://dev.plone.org/archetypes/ticket/622)
        # still valid xml
        data = " <?xml version='1.0'?><foo>bar</foo>"
        mt = reg.classify(data)
        self.failUnless(isinstance(mt, text_xml), str(mt))
        
        # also #622: this is not xml
        data = 'xml > plain text'
        mt = reg.classify(data)
        self.failUnless(str(mt) != 'text/xml')

        #Passed in MT
        mt = reg.classify(data, mimetype="text/plain")
        self.failUnless(isinstance(mt, text_plain), str(mt))

        #Passed in filename
        mt = reg.classify(data, filename="test.xml")
        self.failUnless(isinstance(mt, text_xml), str(mt))
        mt = reg.classify(data, filename="test.jpg")
        self.failUnlessEqual(str(mt), 'image/jpeg')

        # use xml classifier
        mt = reg.classify('<?xml ?>')
        self.failUnless(isinstance(mt, text_xml), str(mt))

        # test no data return default
        mt = reg.classify('')
        self.failUnless(isinstance(mt, text_plain), str(mt))
        reg.defaultMimetype = 'text/xml'
        mt = reg.classify('')
        self.failUnless(isinstance(mt, text_xml), str(mt))

        # test unclassifiable data and no stream flag (filename)
        mt = reg.classify('xxx')
        self.failUnless(isinstance(mt, text_plain), str(mt))

        # test unclassifiable data and file flag
        mt = reg.classify('baz', filename='xxx')
        self.failUnless(isinstance(mt, application_octet_stream), str(mt))

    def testExtension(self):
        reg = self.registry
        data = "<foo>bar</foo>"
        mt = reg.lookupExtension(filename="test.xml")
        self.failUnless(isinstance(mt, text_xml), str(mt))

        mt = reg.classify(data, filename="test.foo")
        self.failUnless(isinstance(mt, application_octet_stream), str(mt))

        mt = reg.classify(data, filename="test.tgz")
        self.failUnlessEqual(str(mt), 'application/x-tar')

        mt = reg.classify(data, filename="test.tar.gz")
        self.failUnlessEqual(str(mt), 'application/x-tar')

        mt = reg.classify(data, filename="test.pdf.gz")
        self.failUnlessEqual(str(mt), 'application/pdf')

    def testFDOGlobs(self):
        # The mime types here might only match if they match a glob on
        # the freedesktop.org registry.
        data = ''
        reg = self.registry
        mt = reg.classify(data, filename="test.anim1")
        self.failUnlessEqual(str(mt), 'video/x-anim')

        mt = reg.classify(data, filename="test.ini~")
        self.failUnlessEqual(str(mt), 'application/x-trash')

        mt = reg.classify(data, filename="test.ini%")
        self.failUnlessEqual(str(mt), 'application/x-trash')

        mt = reg.classify(data, filename="test.ini.bak")
        self.failUnlessEqual(str(mt), 'application/x-trash')

        mt = reg.classify(data, filename="test.f90")
        self.failUnlessEqual(str(mt), 'text/x-fortran')

        mt = reg.classify(data, filename="test.f95")
        self.failUnlessEqual(str(mt), 'text/x-fortran')

        mt = reg.classify(data, filename="makefile")
        self.failUnlessEqual(str(mt), 'text/x-makefile')

        mt = reg.classify(data, filename="Makefile")
        self.failUnlessEqual(str(mt), 'text/x-makefile')

        mt = reg.classify(data, filename="makefile.ac")
        self.failUnlessEqual(str(mt), 'text/x-makefile')

        mt = reg.classify(data, filename="makefile.in")
        self.failUnlessEqual(str(mt), 'text/x-makefile')

        mt = reg.classify(data, filename="AUTHORS")
        self.failUnlessEqual(str(mt), 'text/x-authors')

        mt = reg.classify(data, filename="INSTALL")
        self.failUnlessEqual(str(mt), 'text/x-install')

    def testLookup(self):
        reg = self.registry
        mt = reg.lookup('text/plain')
        self.failUnless(isinstance(mt[0], text_plain), str(mt[0]))

        # Test lookup of aliases in SMI database (see smi_mimetypes)
        mt1 = reg.lookup('application/vnd.wordperfect')
        mt2 = reg.lookup('application/wordperfect')
        self.assertEqual(mt1, mt2)

        mt = reg.lookup('text/notexistent')
        self.failUnlessEqual(mt, ())

    def testAdaptMt(self):
        data, filename, mt = self.registry('bar', mimetype='text/xml')
        # this test that data has been adaped and file seeked to 0
        self.failUnlessEqual(data, 'bar')
        self.failUnlessEqual(filename, None)
        self.failUnless(isinstance(mt, text_xml), str(mt))

    def testAdaptFile(self):
        file = open(input_file_path("rest1.rst"))
        data, filename, mt = self.registry(file)
        # this test that data has been adaped and file seeked to 0
        self.failUnlessEqual(data, file.read())
        file.close()
        self.failUnlessEqual(filename, "rest1.rst")
        self.assertEqual(str(mt), 'text/x-rst')

    def testAdaptData(self):
        data, filename, mt = self.registry('<?xml ?>')
        # this test that data has been adaped and file seeked to 0
        self.failUnlessEqual(data, '<?xml ?>')
        self.failUnlessEqual(filename, None)
        self.failUnless(isinstance(mt, text_xml), str(mt))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMimeTypesclass))
    return suite

if __name__ == '__main__':
    framework()
