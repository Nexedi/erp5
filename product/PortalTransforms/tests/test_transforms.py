from __future__ import nested_scopes

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase

from utils import input_file_path, output_file_path, normalize_html,\
     load, matching_inputs
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import idatastream
from Products.MimetypesRegistry.MimeTypesTool import MimeTypesTool
from Products.PortalTransforms.TransformEngine import TransformTool

from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms.transforms.image_to_gif import image_to_gif
from Products.PortalTransforms.transforms.image_to_png import image_to_png
from Products.PortalTransforms.transforms.image_to_jpeg import image_to_jpeg
from Products.PortalTransforms.transforms.image_to_bmp import image_to_bmp
from Products.PortalTransforms.transforms.image_to_tiff import image_to_tiff
from Products.PortalTransforms.transforms.image_to_ppm  import image_to_ppm
from Products.PortalTransforms.transforms.image_to_pcx  import image_to_pcx

from os.path import exists
import sys
# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'

class TransformTest(ATSiteTestCase):

    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        input = open(self.input)
        orig = input.read()
        input.close()
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename)
        self.assert_(idatastream.isImplementedBy(res_data))
        got = res_data.getData()
        try:
            output = open(output)
        except IOError:
            import sys
            print >>sys.stderr, 'No output file found.'
            print >>sys.stderr, 'File %s created, check it !' % self.output
            output = open(output, 'w')
            output.write(got)
            output.close()
            self.assert_(0)
        expected = output.read()
        if self.normalize is not None:
            expected = self.normalize(expected)
            got = self.normalize(got)
        output.close()

        self.assertEquals(got, expected,
                          '[%s]\n\n!=\n\n[%s]\n\nIN %s(%s)' % (
            got, expected, self.transform.name(), self.input))
        self.assertEquals(self.subobjects, len(res_data.getSubObjects()),
                          '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
            self.subobjects, len(res_data.getSubObjects()), self.transform.name(), self.input))

    def testSame(self):
        self.do_convert(filename=self.input)

    def testSameNoFilename(self):
        self.do_convert()

    def __repr__(self):
        return self.transform.name()

class PILTransformsTest(ATSiteTestCase):
    def afterSetUp(self):
        ATSiteTestCase.afterSetUp(self)
        self.pt = self.portal.portal_transforms

    def test_image_to_bmp(self):
        self.pt.registerTransform(image_to_bmp())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/x-ms-bmp',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/x-ms-bmp')

    def test_image_to_gif(self):
        self.pt.registerTransform(image_to_gif())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/png')
        data = self.pt.convertTo(target_mimetype='image/gif',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/gif')

    def test_image_to_jpeg(self):
        self.pt.registerTransform(image_to_jpeg())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
        data = self.pt.convertTo(target_mimetype='image/jpeg',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/jpeg')

    def test_image_to_png(self):
        self.pt.registerTransform(image_to_png())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/png',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/png')

    def test_image_to_pcx(self):
        self.pt.registerTransform(image_to_pcx())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
        data = self.pt.convertTo(target_mimetype='image/pcx',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/pcx')

    def test_image_to_ppm(self):
        self.pt.registerTransform(image_to_ppm())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/png')
        data = self.pt.convertTo(target_mimetype='image/x-portable-pixmap',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/x-portable-pixmap')

    def test_image_to_tiff(self):
        self.pt.registerTransform(image_to_tiff())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/tiff',orig=data)
        self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/tiff')


TRANSFORMS_TESTINFO = (
    ('Products.PortalTransforms.transforms.pdf_to_html',
     "demo1.pdf", "demo1.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.word_to_html',
     "test.doc", "test_word.html", normalize_html, 0
     ),
    ('Products.PortalTransforms.transforms.lynx_dump',
     "test_lynx.html", "test_lynx.txt", None, 0
     ),
    ('Products.PortalTransforms.transforms.html_to_text',
     "test_lynx.html", "test_html_to_text.txt", None, 0
     ),
    ('Products.PortalTransforms.transforms.identity',
     "rest1.rst", "rest1.rst", None, 0
     ),
    ('Products.PortalTransforms.transforms.text_to_html',
     "rest1.rst", "rest1.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.safe_html',
     "test_safehtml.html", "test_safe.html", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_bmp',
     "logo.jpg", "logo.bmp", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_gif',
     "logo.bmp", "logo.gif", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_jpeg',
     "logo.gif", "logo.jpg", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_png',
     "logo.bmp", "logo.png", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_ppm',
     "logo.gif", "logo.ppm", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_tiff',
     "logo.png", "logo.tiff", None, 0
     ),
    ('Products.PortalTransforms.transforms.image_to_pcx',
     "logo.png", "logo.pcx", None, 0
     ),
    )

def initialise(transform, normalize, pattern):
    global TRANSFORMS_TESTINFO
    for fname in matching_inputs(pattern):
        outname = '%s.out' % fname.split('.')[0]
        #print transform, fname, outname
        TRANSFORMS_TESTINFO += ((transform, fname, outname, normalize, 0),)


# ReST test cases
initialise('Products.PortalTransforms.transforms.rest', normalize_html, "rest*.rst")
# Python test cases
initialise('Products.PortalTransforms.transforms.python', normalize_html, "*.py")

# FIXME missing tests for image_to_html, st

TR_NAMES = None

def make_tests(test_descr=TRANSFORMS_TESTINFO):
    """generate tests classes from test info

    return the list of generated test classes
    """
    tests = []
    for _transform, tr_input, tr_output, _normalize, _subobjects in test_descr:
        # load transform if necessary
        if type(_transform) is type(''):
            try:
                _transform = load(_transform).register()
            except MissingBinary:
                # we are not interessted in tests with missing binaries
                continue
            except:
                import traceback
                traceback.print_exc()
                continue

        if TR_NAMES is not None and not _transform.name() in TR_NAMES:
            print 'skip test for', _transform.name()
            continue

        class TransformTestSubclass(TransformTest):
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    tests.append(PILTransformsTest)
    return tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in make_tests():
        suite.addTest(makeSuite(test))
    return suite

if __name__ == '__main__':
    framework()
