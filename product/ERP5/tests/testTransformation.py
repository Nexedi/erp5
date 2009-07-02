##############################################################################
#
# Copyright (c) 2009 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG

class TestTransformationMixin:
  """
  Mixin class for checking transformations
  """
  transformation_portal_type = 'Transformation'
  transformed_resource_portal_type = \
     'Transformation Transformed Resource'
  component_portal_type = 'Component'

  def createTransformation(self):
    module = self.getPortalObject().getDefaultModule(
        self.transformation_portal_type)
    transformation = module.newContent(portal_type=self.transformation_portal_type)
    return transformation

  def createTransformedResource(self, transformation=None):
    transformed_resource = transformation.newContent(
        portal_type=self.transformed_resource_portal_type)
    return transformed_resource

  def createComponent(self, variation_property_list=None):
    module = self.getPortalObject().getDefaultModule(self.component_portal_type)
    component = module.newContent(portal_type=self.component_portal_type)
    if variation_property_list is not None:
      component.setVariationPropertyList(variation_property_list)
    return component

class TestTransformation(TestTransformationMixin, ERP5TypeTestCase):

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_mrp',)

  def test_01_getAggregatedAmountListWithVariatedProperty(self):
    """
    Make sure that getAggregatedAmountList is still working properly if we
    have additionnals propertysheets on transformations lines and that used
    variation properties
    """
    # Only for testing purpose, use a property sheet that has nothing to
    # do with component. It would have been possible to create a new
    # property sheet for this test
    self._addPropertySheet(self.transformed_resource_portal_type, 'Bug')
    variation_property_list = ['tested']

    transformation = self.createTransformation()
    transformed_resource = self.createTransformedResource(transformation)
    component = self.createComponent(
        variation_property_list=variation_property_list)
    transformed_resource.edit(
        resource_value=component,
        quantity=1)
    transformed_resource.setTested(True)
    aggregated_amount_list = transformation.getAggregatedAmountList()
    self.assertEquals(len(aggregated_amount_list), 1)
    aggregated_amount = aggregated_amount_list[0]
    # Make sure that the isTested method is working properly on the
    # temp object
    self.assertTrue(aggregated_amount.isTested())
