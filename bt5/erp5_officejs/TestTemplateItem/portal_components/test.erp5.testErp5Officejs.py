# Copyright (c) 2002-2017 Nexedi SA and Contributors. All Rights Reserved.
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from base64 import b64decode

class TestErp5Officejs(ERP5TypeTestCase):

  def test_webPageRestrictedTraverseOnViewSkinSelection(self):
    """
      Check we can restricted traverse an image from a web page on the default
      skin selection. (`web_page.getDocumentValue(reference)`)
    """
    # test initialisation
    image = self.portal.image_module.newContent(
      portal_type="Image",
      reference="TEST-Test.Restricted.Traverse.With.ERP5.Officejs",
      version="001",
      language="en",
      filename="white_pixel.png",
      data=b64decode("".join([
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEw",
        "EAmpwYAAAAB3RJTUUH4QUdBikq4C9IOgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdp",
        "dGggR0lNUFeBDhcAAAAMSURBVAjXY/j//z8ABf4C/tzMWecAAAAASUVORK5CYII=",
      ])),
    )
    image.publish()
    web_page = self.portal.web_page_module.newContent(
      portal_type="Web Page",
    )
    self.tic()

    # actual test
    other_image = web_page.restrictedTraverse("TEST-Test.Restricted.Traverse.With.ERP5.Officejs")
    self.assertEquals(image.getUid(), other_image.getUid())
