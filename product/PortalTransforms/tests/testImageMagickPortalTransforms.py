import os

from Testing import ZopeTestCase
from Products.PortalTransforms.tests.utils import input_file_path, normalize_html,\
     matching_inputs
from Products.PortalTransforms.transforms.image_to_gif import image_to_gif
from Products.PortalTransforms.transforms.image_to_png import image_to_png
from Products.PortalTransforms.transforms.image_to_jpeg import image_to_jpeg
from erp5.component.document.TransformImageToBmp import image_to_bmp
from Products.PortalTransforms.transforms.image_to_tiff import image_to_tiff
from Products.PortalTransforms.transforms.image_to_ppm  import image_to_ppm
from erp5.component.document.TransformImageToPcx  import image_to_pcx
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'

class ImageMagickTransformsTest(ERP5TypeTestCase, ZopeTestCase.Functional):
    def afterSetUp(self):
        super(ImageMagickTransformsTest, self).afterSetUp()
        self.pt = self.portal.portal_transforms

    def test_image_to_bmp(self):
        self.pt.registerTransform(image_to_bmp())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/x-ms-bmp',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/x-ms-bmp')

    def test_image_to_gif(self):
        self.pt.registerTransform(image_to_gif())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/png')
        data = self.pt.convertTo(target_mimetype='image/gif',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/gif')

    def test_image_to_jpeg(self):
        self.pt.registerTransform(image_to_jpeg())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
        data = self.pt.convertTo(target_mimetype='image/jpeg',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/jpeg')

    def test_image_to_png(self):
        self.pt.registerTransform(image_to_png())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/png',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/png')

    def test_image_to_pcx(self):
        self.pt.registerTransform(image_to_pcx())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
        data = self.pt.convertTo(target_mimetype='image/pcx',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/pcx')

    def test_image_to_ppm(self):
        self.pt.registerTransform(image_to_ppm())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/png')
        data = self.pt.convertTo(target_mimetype='image/x-portable-pixmap',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/x-portable-pixmap')

    def test_image_to_tiff(self):
        self.pt.registerTransform(image_to_tiff())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/tiff',orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/tiff')


# FIXME missing tests for image_to_html, st

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(ImageMagickTransformsTest))
    return suite
