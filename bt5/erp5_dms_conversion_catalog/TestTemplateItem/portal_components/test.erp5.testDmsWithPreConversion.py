# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Nicolas Delaby <nicolas@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest
from erp5.component.test.testDms import TestDocument

class TestDocumentWithPreConversion(TestDocument):
  """
    Test basic document - related operations
    with Flare
  """
  def getTitle(self):
    return "DMS with Preconversion"

  def test_preConvertedReferencedImageInWebPageContent(self):
    # create an image
    upload_file = self.makeFileUpload('cmyk_sample.jpg')
    image = self.portal.image_module.newContent(portal_type='Image',
                                               reference='Embedded-XXX',
                                               version='001',
                                               language='en')
    image.edit(file=upload_file)
    image.publish()
    self.tic()

    # after a web page creation, the referenced images are found and should be pre converted
    # with the parameters given in their src URL
    web_page = self.portal.web_page_module.newContent(portal_type="Web Page")
    web_page.setTextContent('''<b> test </b>
<img src="Embedded-XXX?format=png&display=large&quality=64"/>
<img src="Embedded-XXX?format=jpeg&display=large&quality=64"/>''')
    web_page.publish()
    self.tic()

    # check that referenced in Web Page's content image(s) is well converted
    self.assertTrue(image.hasConversion(**{'format':'jpeg', 'display':'large', 'quality':64}))
    self.assertTrue(image.hasConversion(**{'format':'png', 'display':'large', 'quality':64}))
    self.assertSameSet(['Embedded-XXX?format=png&display=large&quality=64', \
                        'Embedded-XXX?format=jpeg&display=large&quality=64'],
                        web_page.Base_extractImageUrlList())

  def test_Base_isConvertible(self):
    """
      Test pre converion only happens on proper documents.
    """
    image = self.portal.image_module.newContent(portal_type='Image',
                                               reference='Embedded-XXX',
                                               version='001',
                                               language='en')

    # draft image is not convertible
    upload_file = self.makeFileUpload('cmyk_sample.jpg')
    image.edit(file=upload_file)
    self.tic()
    self.assertEqual(False, image.Base_isConvertible())

    # published image with data is convertible
    image.publish()
    self.tic()
    self.assertEqual(True, image.Base_isConvertible())

    image = self.portal.image_module.newContent(portal_type='Image',
                                               reference='Embedded-YYY',
                                               version='001',
                                               language='en')
    image.publish()
    self.tic()

    # published empty image is not convertible
    self.assertEqual(False, image.Base_isConvertible())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDocumentWithPreConversion))
  return suite


# vim: syntax=python shiftwidth=2
