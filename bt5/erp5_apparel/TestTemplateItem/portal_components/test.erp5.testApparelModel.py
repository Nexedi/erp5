##############################################################################
#
# Copyright (c) 2009, 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5Type.tests.utils import reindex
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestApparelModel(ERP5TypeTestCase):

  def getTitle(self):
    return "Apparel Model"

  def getBusinessTemplateList(self):
    return (
      'erp5_base',
      'erp5_pdm',
      'erp5_trade',
      'erp5_apparel')

  def afterSetUp(self):
    """Prepare the test."""
    self.createCategories()

  @reindex
  def createCategories(self):
    """Create the categories for our test. """
    # create categories
    for cat_string in self.getNeededCategoryList():
      base_cat = cat_string.split("/")[0]
      # if base_cat not exist, create it
      if getattr(self.getPortal().portal_categories, base_cat, None) is None:
        self.getPortal().portal_categories.newContent(
                                          portal_type='Base Category',
                                          id=base_cat)
      path = self.getPortal().portal_categories[base_cat]
      for cat_id in cat_string.split("/")[1:]:
        if not cat_id in path.objectIds():
          path = path.newContent(
                    portal_type='Category',
                    id=cat_id,
                    title=cat_id.title())
        else:
          path = path[cat_id]
    # check categories have been created
    for cat_string in self.getNeededCategoryList():
      self.assertNotEquals(None,
                self.getCategoryTool().restrictedTraverse(cat_string),
                cat_string)

  def getNeededCategoryList(self):
    """return a list of categories that should be created."""
    return ('composition/acrylique',
            'composition/elasthane',
           )

  def test_checkCopyComposition(self):
    '''
    Check that it's possible to copy composition from a model, and that cells
    are well created.
    '''
    portal = self.getPortal()

    # defin an apparel fabric
    apparel_fabric_module = portal.getDefaultModule('Apparel Fabric')
    apparel_fabric = apparel_fabric_module.newContent(
        portal_type = 'Apparel Fabric')
    apparel_fabric.setCategoryList(
        ('composition/acrylique',
         'composition/elasthane'))
    apparel_fabric.updateCellRange(base_id = 'composition')

    # create composition cells
    apparel_fabric.newCell(
        'composition/acrylique',
        base_id = 'composition',
        portal_type = 'Mapped Value',
        quantity = 0.88)
    apparel_fabric.newCell(
        'composition/elasthane',
        base_id ='composition',
        portal_type = 'Mapped Value',
        quantity = 0.12)

    # add some color variations
    fabric_color1 = apparel_fabric.newContent(
        portal_type = 'Apparel Fabric Colour Variation',
        title = 'Bleu ciel')
    fabric_color2 = apparel_fabric.newContent(
        portal_type = 'Apparel Fabric Colour Variation',
        title = 'Volcano')

    # create an Apparel Colour Range
    apparel_colour_range_module = portal.getDefaultModule('Apparel Colour Range')
    apparel_colour_range = apparel_colour_range_module.newContent(
        portal_type = 'Apparel Colour Range')
    color1 = apparel_colour_range.newContent(
        title = 'Blue',
        portal_type = 'Apparel Colour Range Variation')
    apparel_colour_range.newContent(
        title = 'Red',
        portal_type = 'Apparel Colour Range Variation')

    variation1 = color1.newContent(
        title = 'Ocean',
        int_index = 2,
        portal_type = 'Apparel Colour Range Variation Line')
    variation2 = color1.newContent(
        title = 'Volcano',
        int_index = 1,
        portal_type = 'Apparel Colour Range Variation Line')

    variation1.setSpecialiseValue(fabric_color1)
    variation2.setSpecialiseValue(fabric_color2)

    # create an Apparel Model
    apparel_model_module = portal.getDefaultModule('Apparel Model')
    apparel_model = apparel_model_module.newContent(portal_type='Apparel Model')
    apparel_model.setSpecialiseValue(apparel_colour_range)
    apparel_model.ApparelModel_copyComposition()

    # check the cells have been copied
    cell_list = apparel_model.contentValues(portal_type = 'Mapped Value')
    self.assertEqual(len(cell_list), 2)

    acrylique = apparel_model.getCell(
        'composition/acrylique',
        base_id = 'composition')
    self.assertNotEquals(acrylique, None)
    self.assertEqual(acrylique.getProperty('quantity'), 0.88)

    elasthane = apparel_model.getCell(
        'composition/elasthane',
        base_id = 'composition')
    self.assertNotEquals(elasthane, None)
    self.assertEqual(elasthane.getProperty('quantity'), 0.12)

    # check indexes are present
    self.assertTrue(apparel_model.index.has_key('composition'))
    index = apparel_model.index['composition'][0]
    self.assertTrue(index.has_key('composition/elasthane'))
    self.assertTrue(index.has_key('composition/acrylique'))

  def test_checkCopyColourRangeVariation(self):
    '''
    Check that it's possible to copy colour range variation from a model, and
    that cells are well created.
    '''


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestApparelModel))
  return suite
