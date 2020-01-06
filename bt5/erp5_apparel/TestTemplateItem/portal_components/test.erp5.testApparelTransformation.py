##############################################################################
#
# Copyright (c) 2004, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Guillaume Michon <guillaume.michon@e-asc.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5.tests.testOrder import TestOrderMixin

class TestApparelTransformation(TestOrderMixin, ERP5TypeTestCase):
  """
    Test Transformations with erp5_apparel configuration

    This test :
      - is checking so many values
      - is specific to erp5_apparel, so does not allows to reuse it's code

    Therefore, it's better to use testTransformation for future tests
  """
  transformation_portal_type = 'Transformation'
  component_portal_type = 'Apparel Component'
  component_variation_portal_type = 'Apparel Component Variation'
  transformed_resource_portal_type = 'Transformation Transformed Resource'
  operation_portal_type = 'Transformation Operation'

  def afterSetUp(self):
    super(TestApparelTransformation, self).afterSetUp()
    self.login()

  def getTitle(self):
    return "Transformation"

  def createCategories(self):
    TestOrderMixin.createCategories(self)
    self.portal.portal_categories.quantity_unit.newContent(
      id='time').newContent(id='min')

  def getBusinessTemplateList(self):
    """
    """
    return list(TestOrderMixin.getBusinessTemplateList(self)) + ['erp5_mrp']

  def stepCreateComponentDict(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a number of variated component
    """
    portal = self.getPortal()
    component_module = portal.getDefaultModule(self.component_portal_type)

    components = [
      { 'name':'zip', 'quantity': 100., 'prices':[10.] },
      { 'name':'tissu', 'quantity': 50., 'prices':[4.5, 7.] },
      { 'name':'bouton', 'quantity': 1000., 'prices':[150.] }, ]

    component_dict = {}
    for component_info in components:
      component_name = component_info['name']
      component = component_module.newContent(title=component_name)
      component_dict[component_name] = component
      variation1 = component.newContent(
                          portal_type=self.component_variation_portal_type,
                          id='1')
      variation2 = component.newContent(
                          portal_type=self.component_variation_portal_type,
                          id='2')
      variations = [variation1, variation2]

      # Commit and catalog
      self.tic()

      component.setVariationBaseCategoryList(['variation'])
      component.setPVariationBaseCategoryList(['variation'])
      # Variation are automatically acquired if they are individual variation.
#       component.setCategoryList(
#                     ['variation/' + x.getRelativeUrl() for x in variations] )
      # Set the price
      supply_line = component.newContent(portal_type='Supply Line')
      supply_line.edit(mapped_value_property_list=['base_price'],
          priced_quantity=component_info['quantity'])
      component_prices = component_info['prices']
      if len(component_prices) == 1:
        supply_line.edit(
            membership_criterion_base_category = ['variation'],
            membership_criterion_category = ['variation/' + x.getRelativeUrl() for x in variations],
            base_price = component_prices[0])
      else:
#         supply_line.setVariationBaseCategoryList(['variation'])
        supply_line.updateCellRange(base_id = 'path')
        for i in range(2):
          supply_cell = supply_line.newCell(
                   'variation/apparel_component_module/%s/%d' % \
                                      (component.getId(),(i+1)),
                   portal_type='Supply Cell',
                   base_id='path')
          supply_cell.edit(
            membership_criterion_base_category = ['variation'],
            membership_criterion_category = ['variation/' + variations[i].getRelativeUrl()],
            base_price = component_prices[i],
            mapped_value_property_list = ['base_price'],
            resource = supply_line.getResource() )
    sequence.edit(component_dict=component_dict)


  def stepCreateOperationDict(self, sequence=None, sequence_list=None, **kw):
    """
      Create a number of operations
    """
    portal = self.getPortal()
    operation_dict = {}
    for operation_name in ('piquage', 'taillage'):
      operation = portal.portal_categories.operation.newContent(operation_name,
        quantity_unit='time/min')
      operation_dict[operation_name] = operation
    sequence.edit(operation_dict=operation_dict)


  def stepCreateTransformation(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a transformation
    """
    portal = self.getPortal()
    resource = sequence.get('resource')

    transformation_module = portal.getDefaultModule(self.transformation_portal_type)
    transformation = transformation_module.newContent(portal_type=self.transformation_portal_type)
    sequence.edit(transformation=transformation)
    transformation.setResourceValue(resource)
    transformation.setVariationBaseCategoryList(('size','colour', 'morphology'))


  def stepCreateIncludedTransformation(self, sequence=None, sequence_list=None, **kw):
    """
      Create a transformation to be included into the other
    """
    portal = self.getPortal()
    resource = sequence.get('resource')
    transformation_module = portal.getDefaultModule(self.transformation_portal_type)
    transformation = transformation_module.newContent(portal_type = self.transformation_portal_type)
    sequence.edit(included_transformation = transformation)
    transformation.setResourceValue(resource)
    transformation.setVariationBaseCategoryList(('size',))


  def stepCreateTransformationLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create transformed resources and operations for transformation
    """
    transformation = sequence.get('transformation')
    component_dict = sequence.get('component_dict')

    # Transformed Resource 1 : permanent consumption
    tr_resource_name = 'bouton'
    transformed_resource = transformation.newContent(portal_type=self.transformed_resource_portal_type)
    transformed_resource.edit(
        title = tr_resource_name,
        quantity = 2.,
        resource_value = component_dict[tr_resource_name],
        int_index=1,
        )
    transformed_resource.edit(
       categories = transformed_resource.getCategoryList() + ['variation/' + component_dict[tr_resource_name]['1'].getRelativeUrl()])

    # Transformed Resource 2 : 1 variation axis
    line_list =  [ ('size/Baby',     '1'),
                   ('size/Child/32', '2'),
                   ('size/Child/34', '1'),
                   ('size/Man',      '2'),
                   ('size/Woman',    '1') ]
    tr_resource_name = 'zip'
    transformed_resource = transformation.newContent(portal_type=self.transformed_resource_portal_type)
    transformed_resource.edit(
        title = tr_resource_name,
        quantity = 1.,
        resource_value = component_dict[tr_resource_name],
        int_index=2,
        )
    base_category_list = ['size']
    transformed_resource.setVariationBaseCategoryList(base_category_list)
    range_list = [x[0] for x in line_list]
    transformed_resource.setCellRange(range_list, base_id='variation')
    for line in line_list:
      size, variation = line
      variation = component_dict[tr_resource_name][variation]
      cell = transformed_resource.newCell(size, base_id='variation')
      cell.edit(
        membership_criterion_base_category = base_category_list,
        membership_criterion_category = [size],
        categories = ('variation/' + variation.getRelativeUrl() ) )
    self.tic()

    # Transformed Resource 3 : 3 variation axis
    line_list = [ ('size/Baby', 'ColourVariation1', 'MorphologyVariation1', '2', 3.),
                  ('size/Baby', 'ColourVariation1', 'MorphologyVariation2', '1', 3.5),
                  ('size/Baby', 'ColourVariation2', 'MorphologyVariation1', '1', 3.),
                  ('size/Baby', 'ColourVariation2', 'MorphologyVariation2', '2', 3.5),
                  ('size/Baby', 'ColourVariation3', 'MorphologyVariation1', '1', 3.5),
                  ('size/Baby', 'ColourVariation3', 'MorphologyVariation2', '1', 3.5),

                  ('size/Child/32', 'ColourVariation1', 'MorphologyVariation1', '1', 6.),
                  ('size/Child/32', 'ColourVariation1', 'MorphologyVariation2', '1', 6.5),
                  ('size/Child/32', 'ColourVariation2', 'MorphologyVariation1', '1', 6.),
                  ('size/Child/32', 'ColourVariation2', 'MorphologyVariation2', '2', 6.5),
                  ('size/Child/32', 'ColourVariation3', 'MorphologyVariation1', '2', 6.),
                  ('size/Child/32', 'ColourVariation3', 'MorphologyVariation2', '1', 6.5),

                  ('size/Child/34', 'ColourVariation1', 'MorphologyVariation1', '1', 9.),
                  ('size/Child/34', 'ColourVariation1', 'MorphologyVariation2', '2', 9.5),
                  ('size/Child/34', 'ColourVariation2', 'MorphologyVariation1', '2', 9.),
                  ('size/Child/34', 'ColourVariation2', 'MorphologyVariation2', '1', 9.5),
                  ('size/Child/34', 'ColourVariation3', 'MorphologyVariation1', '2', 9.),
                  ('size/Child/34', 'ColourVariation3', 'MorphologyVariation2', '2', 9.5),

                  ('size/Man', 'ColourVariation1', 'MorphologyVariation1', '2', 12.),
                  ('size/Man', 'ColourVariation1', 'MorphologyVariation2', '2', 12.5),
                  ('size/Man', 'ColourVariation2', 'MorphologyVariation1', '2', 12.),
                  ('size/Man', 'ColourVariation2', 'MorphologyVariation2', '1', 12.5),
                  ('size/Man', 'ColourVariation3', 'MorphologyVariation1', '1', 12.),
                  ('size/Man', 'ColourVariation3', 'MorphologyVariation2', '2', 12.5),

                  ('size/Woman', 'ColourVariation1', 'MorphologyVariation1', '2', 15.),
                  ('size/Woman', 'ColourVariation1', 'MorphologyVariation2', '1', 15.5),
                  ('size/Woman', 'ColourVariation2', 'MorphologyVariation1', '1', 15.),
                  ('size/Woman', 'ColourVariation2', 'MorphologyVariation2', '2', 15.5),
                  ('size/Woman', 'ColourVariation3', 'MorphologyVariation1', '2', 15.),
                  ('size/Woman', 'ColourVariation3', 'MorphologyVariation2', '2', 15.5),
               ]
    mapping_dict = {'ColourVariation1': 'colour/apparel_model_module/1/1',
                    'ColourVariation2': 'colour/apparel_model_module/1/2',
                    'ColourVariation3': 'colour/apparel_model_module/1/3',
                    'MorphologyVariation1': 'morphology/apparel_model_module/1/4',
                    'MorphologyVariation2': 'morphology/apparel_model_module/1/5',
                    '1': 'apparel_component_module/2/1',
                    '2': 'apparel_component_module/2/2' }


    tr_resource_name = 'tissu'
    transformed_resource = transformation.newContent(portal_type=self.transformed_resource_portal_type)
    transformed_resource.edit(
        title = tr_resource_name,
        resource_value = component_dict[tr_resource_name],
        int_index=3,
        )
    base_category_list = ['size', 'colour', 'morphology']
    transformed_resource.setVariationBaseCategoryList(base_category_list)
    variation_range_list_list = []
    for base_category in base_category_list:
      variation_range_category_list = transformation.getVariationRangeCategoryList(base_category_list=[base_category])
      variation_range_list_list.append(variation_range_category_list)

    transformed_resource.setCellRange(base_id='variation', *variation_range_list_list)
    transformed_resource.setCellRange(base_id='quantity', *variation_range_list_list)

    # Define the cells
    for line in line_list:
      size, colour, morphology, variation, quantity = line
      colour = mapping_dict[colour]
      morphology = mapping_dict[morphology]
      variation = component_dict[tr_resource_name][variation]
      cell_variation = transformed_resource.newCell(size, colour, morphology, base_id='variation')
      cell_quantity = transformed_resource.newCell(size, colour, morphology, base_id='quantity')
      cell_variation.edit(
        membership_criterion_base_category = base_category_list,
        membership_criterion_category = [size, colour, morphology],
        categories = ('variation/' + variation.getRelativeUrl()) )
      cell_quantity.edit(
        membership_criterion_base_category = base_category_list,
        membership_criterion_category = [size, colour, morphology],
        quantity = quantity,
        mapped_value_property_list = ['quantity'] )
    self.tic()


  def stepCreateIncludedTransformationLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create transformed resources and operations for transformation
    """
    transformation = sequence.get('included_transformation')
    operation_dict = sequence.get('operation_dict')
    component_dict = sequence.get('component_dict')

    # Operation 1 : permanent consumption
    op_name = 'taillage'
    operation = transformation.newContent(portal_type=self.operation_portal_type)
    operation.edit(
        title = op_name,
        quantity = 10.,
        resource_value=operation_dict[op_name],
        int_index=4,
        )

    # Operation 2 : 1 variation axis
    line_list =  [ ('size/Baby',     2.),
                   ('size/Child/32', 2.5),
                   ('size/Child/34', 3.),
                   ('size/Man',      3.5),
                   ('size/Woman',    4.) ]
    op_name = 'piquage'
    operation = transformation.newContent(portal_type=self.operation_portal_type)
    operation.edit(
        title = op_name,
        resource_value=operation_dict[op_name],
        int_index=5,
        )
    base_category_list = ['size']
    operation.setVariationBaseCategoryList(base_category_list)
    range_list = [x[0] for x in line_list]
    operation.setCellRange(range_list, base_id='quantity')
    for line in line_list:
      size, quantity = line
      cell = operation.newCell(size, base_id='quantity')
      cell.edit(
        membership_criterion_base_category = base_category_list,
        membership_criterion_category = [size],
        quantity = quantity,
        mapped_value_property_list = ['quantity'])
    self.tic()

  # Transformed Resource : 1 variation axis
    line_list =  [ ('size/Baby',     1.),
                   ('size/Child/32', 1.5),
                   ('size/Child/34', 2.),
                   ('size/Man',      3.),
                   ('size/Woman',    2.5) ]
    tr_resource_name = 'tissu'
    transformed_resource = transformation.newContent(portal_type=self.transformed_resource_portal_type)
    transformed_resource.edit(
        title = tr_resource_name,
        resource_value = component_dict[tr_resource_name],
        int_index=6,
        )
    transformed_resource.edit(
       categories = transformed_resource.getCategoryList() + ['variation/' + component_dict[tr_resource_name]['1'].getRelativeUrl()])
    base_category_list = ['size']
    transformed_resource.setVariationBaseCategoryList(base_category_list)
    range_list = [x[0] for x in line_list]
    transformed_resource.setCellRange(range_list, base_id='quantity')
    for line in line_list:
      size, quantity = line
      cell = transformed_resource.newCell(size, base_id='quantity')
      cell.edit(
        membership_criterion_base_category = base_category_list,
        membership_criterion_category = [size],
        quantity = quantity,
        mapped_value_property_list = ['quantity'])
    self.tic()


  def stepIncludeTransformation(self, sequence=None, sequence_list=None, **kw):
    transformation = sequence.get('transformation')
    included_transformation = sequence.get('included_transformation')
    transformation.edit(specialise_value = included_transformation)


  def stepVerifyTransformationAggregatedAmountList(self, sequence=None, sequence_list=None, **kw):
    """
      Verify the return of getAggregatedAmountList
    """
    expected_list = [
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.42], 'total':.82, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.315], 'total':.715, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.27], 'total':.67, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.49], 'total':.89, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.315], 'total':.715, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.315], 'total':.715, 'duration':[None,None,None], 'total_duration':None},

      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.54], 'total':.94, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.585], 'total':.985, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.54], 'total':.94, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.91], 'total':1.31, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.84], 'total':1.24, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.585], 'total':.985, 'duration':[None,None,None], 'total_duration':None},

      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.81], 'total':1.21, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.33], 'total':1.73, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.26], 'total':1.66, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.855], 'total':1.255, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.26], 'total':1.66, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.33], 'total':1.73, 'duration':[None,None,None], 'total_duration':None},

      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.68], 'total':2.08, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.75], 'total':2.15, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.68], 'total':2.08, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.125], 'total':1.525, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.08], 'total':1.48, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.75], 'total':2.15, 'duration':[None,None,None], 'total_duration':None},

      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,2.1], 'total':2.5, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.395], 'total':1.795, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.35], 'total':1.75, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,2.17], 'total':2.57, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,2.1], 'total':2.5, 'duration':[None,None,None], 'total_duration':None},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,2.17], 'total':2.57, 'duration':[None,None,None], 'total_duration':None},
       ]
    transformation = sequence.get('transformation')
    self.verifyAggregatedAmountList(transformation, expected_list)


  def stepVerifyIncludedTransformationAggregatedAmountList(self, sequence=None, sequence_list=None, **kw):
    """
      Verify the return of getAggregatedAmountList
    """
    expected_list = [
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.09], 'total':.09, 'duration':[10.,2.,None], 'total_duration':12.},

      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.135], 'total':.135, 'duration':[10.,2.5,None], 'total_duration':12.5},

      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.18], 'total':.18, 'duration':[10.,3.,None], 'total_duration':13.},

      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.27], 'total':.27, 'duration':[10.,3.5,None], 'total_duration':13.5},

      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[None,None,.225], 'total':.225, 'duration':[10.,4.,None], 'total_duration':14.},
       ]
    transformation = sequence.get('included_transformation')
    self.verifyAggregatedAmountList(transformation, expected_list)


  def stepVerifySpecialisedTransformationAggregatedAmountList(self, sequence=None, sequence_list=None, **kw):
    """
      Verify the return of AggregatedAmountList for a transformation which includes another one
    """
    expected_list = [
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.42,None,None,.09], 'total':.91, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.315,None,None,.09], 'total':.805, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.27,None,None,.09], 'total':.76, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.49,None,None,.09], 'total':.98, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.315,None,None,.09], 'total':.805, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},
      {'id':('size/Baby', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.315,None,None,.09], 'total':.805, 'duration':[None,None,None,10.,2.,None], 'total_duration':12.},

      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.54,None,None,.135], 'total':1.075, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.585,None,None,.135], 'total':1.12, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.54,None,None,.135], 'total':1.075, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.91,None,None,.135], 'total':1.445, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.84,None,None,.135], 'total':1.375, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},
      {'id':('size/Child/32', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.585,None,None,.135], 'total':1.12, 'duration':[None,None,None,10.,2.5,None], 'total_duration':12.5},

      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,.81,None,None,.18], 'total':1.39, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.33,None,None,.18], 'total':1.91, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.26,None,None,.18], 'total':1.84, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,.855,None,None,.18], 'total':1.435, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.26,None,None,.18], 'total':1.84, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},
      {'id':('size/Child/34', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.33,None,None,.18], 'total':1.91, 'duration':[None,None,None,10.,3.,None], 'total_duration':13.},

      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.68,None,None,.27], 'total':2.35, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.75,None,None,.27], 'total':2.42, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.68,None,None,.27], 'total':2.35, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.125,None,None,.27], 'total':1.795, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.08,None,None,.27], 'total':1.75, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},
      {'id':('size/Man', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.75,None,None,.27], 'total':2.42, 'duration':[None,None,None,10.,3.5,None], 'total_duration':13.5},

      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,2.1,None,None,.225], 'total':2.725, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/1', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,1.395,None,None,.225], 'total':2.02, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,1.35,None,None,.225], 'total':1.975, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/2', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,2.17,None,None,.225], 'total':2.795, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/4'),
         'amount':[.3,.1,2.1,None,None,.225], 'total':2.725, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
      {'id':('size/Woman', 'colour/apparel_model_module/1/3', 'morphology/apparel_model_module/1/5'),
         'amount':[.3,.1,2.17,None,None,.225], 'total':2.795, 'duration':[None,None,None,10.,4.,None], 'total_duration':14.},
       ]
    transformation = sequence.get('transformation')
    self.verifyAggregatedAmountList(transformation, expected_list)


  def verifyAggregatedAmountList(self, transformation, expected_list):
    """
      Verify aggregated data according to an expected structure
    """
    produced_resource = transformation.getResource()
    production_order_module = self.portal.getDefaultModule("Production Order")
    production_order = production_order_module.newContent(
                                      portal_type="Production Order",
                                      temp_object=1,
                                      specialise_value=transformation)
    for _, expected in enumerate(expected_list):
      context = production_order.newContent(
          portal_type="Production Order Line",
          quantity=1,
          variation_category_list=expected['id'],
          resource=produced_resource,
      )
      aggregated_amount_list = context.getAggregatedAmountList()

      # Check total price and duration for each component
      r = lambda x: x and round(x, 10)
      self.assertEqual(set(zip(expected['amount'], expected['duration'])),
        {(r(x.getTotalPrice()), r(x.getDuration()))
         for x in aggregated_amount_list})

      # Check global quantity
      total_price = aggregated_amount_list.getTotalPrice()
      error_msg = 'Total price for AggregatedAmountList differs between ' \
                  'expected (%s) and aggregated (%s) (%s)' % \
                  (total_price, expected['total'], expected['id'])
      self.assertEqual(round(total_price, 10), round(expected['total'], 10),
                        error_msg)

      # Check global duration
      total_duration = aggregated_amount_list.getTotalDuration()
      expected_duration = expected['total_duration']
      error = 0
      if total_duration is None and expected_duration is not None:
        error = 1
      if expected_duration is None and total_duration is not None:
        error = 1
      if total_duration is not None and expected_duration is not None:
        if round(total_duration, 10) != round(expected_duration, 10):
          error = 1
      if error == 1:
        error_msg = 'Total duration differs between expected (%s) and ' \
                    'aggregated (%s) (%s)' % \
                     (expected_duration, total_duration, expected['id'])
        LOG('TEST ERROR :', 0, error_msg)
      # XXX Is it alright to exit this test with an error without raising
      # anything?
      # self.assertFalse(error, error_msg)


  def test_01_getAggregatedAmountList(self):
    """
      Test the method getAggregatedAmountList
    """
    sequence_list = SequenceList()
    # Test with a simply order without cell
    sequence_string = '\
                      CreateComponentDict \
                      CreateOperationDict \
                      Tic \
                      CreateVariatedResource \
                      Tic \
                      CreateTransformation \
                      Tic \
                      CreateTransformationLine \
                      Tic \
                      CreateIncludedTransformation \
                      Tic \
                      CreateIncludedTransformationLine \
                      Tic \
                      VerifyTransformationAggregatedAmountList \
                      VerifyIncludedTransformationAggregatedAmountList \
                      IncludeTransformation \
                      Tic \
                      VerifySpecialisedTransformationAggregatedAmountList \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)
