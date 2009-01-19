##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Invoice import Invoice
from Products.ERP5Type.Utils import cartesianProduct
from zLOG import LOG, DEBUG, INFO

#XXX TODO: review naming of new methods
#XXX WARNING: current API naming may change although model should be stable.

class PaySheetTransaction(Invoice):
  """
  A paysheet will store data about the salary of an employee
  """

  meta_type = 'ERP5 Pay Sheet Transaction'
  portal_type = 'Pay Sheet Transaction'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem
                    , PropertySheet.CategoryCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Delivery
                    , PropertySheet.PaySheet
                    , PropertySheet.Movement
                    , PropertySheet.Amount
                    , PropertySheet.XMLObject
                    , PropertySheet.TradeCondition
                    , PropertySheet.DefaultAnnotationLine
                    )

  # Declarative Interface
  __implements__ = ( )


  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityFromReference')
  def getRatioQuantityFromReference(self, ratio_reference=None):
    """
    return the ratio value correponding to the ratio_reference,
    None if ratio_reference not found
    """
    # get ratio lines
    portal_type_list = ['Pay Sheet Model Ratio Line']
    object_ratio_list = self.contentValues(portal_type=portal_type_list)

    # look for ratio lines on the paysheet
    if object_ratio_list:
      for obj in object_ratio_list:
        if obj.getReference() == ratio_reference:
          return obj.getQuantity()

    # if not find in the paysheet, look on dependence tree
    sub_object_list = self.getInheritedObjectValueList(portal_type_list)
    object_ratio_list = sub_object_list
    for object in object_ratio_list:
      if object.getReference() == ratio_reference:
        return object.getQuantity()

    return None 

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityList')
  def getRatioQuantityList(self, ratio_reference_list):
    """
    Return a list of reference_ratio_list correponding values.
    reference_ratio_list is a list of references to the ratio lines
    we want to get.
    """
    if not isinstance(ratio_reference_list, (list, tuple)):
      return [self.getRatioQuantityFromReference(ratio_reference_list)]
    return [self.getRatioQuantityFromReference(reference) \
        for reference in ratio_reference_list]

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityFromReference')
  def getAnnotationLineFromReference(self, reference=None):
    """Return the annotation line corresponding to the reference.
    Returns None if reference not found
    """
    # look for annotation lines on the paysheet
    annotation_line_list = self.contentValues(portal_type=['Annotation Line'])
    if annotation_line_list:
      for annotation_line in annotation_line_list:
        if annotation_line.getReference() == reference:
          return annotation_line

    # if not find in the paysheet, look on dependence tree
    for annotation_line in self.getInheritedObjectValueList(['Annotation Line']):
      if annotation_line.getReference() == reference:
        return annotation_line

    return None 

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityList')
  def getAnnotationLineListList(self, reference_list):
    """Return a list of annotation lines corresponding to the reference_list
    reference_list is a list of references to the Annotation Line we want 
    to get.
    """
    if not isinstance(reference_list, (list, tuple)):
      return [self.getAnnotationLineFromReference(reference_list)]
    return [self.getAnnotationLineFromReference(reference) \
        for reference in reference_list]

  security.declareProtected(Permissions.AddPortalContent,
                            'createPaySheetLine')
  def createPaySheetLine(self, cell_list, title='', resource='',
                         description='', base_contribution_list=None, int_index=None,
                         categories=None, **kw):
    '''
    This function register all paysheet informations in paysheet lines and 
    cells. Select good cells only
    '''
    if not resource:
      raise ValueError, "Cannot create Pay Sheet Line without resource"

    good_cell_list = []
    for cell in cell_list:
      if cell['quantity'] or cell['price']:
        good_cell_list.append(cell)
    if len(good_cell_list) == 0:
      return
    # Get all variation categories used in cell_list
    var_cat_list = []
    for cell in good_cell_list:
      # Don't add a variation category if already in it
      for category in cell['category_list']:
        if category not in var_cat_list:
          var_cat_list.append(category)

    resource_value = self.getPortalObject().unrestrictedTraverse(resource)
    # Add a new Pay Sheet Line
    payline = self.newContent(
                       portal_type='Pay Sheet Line',
                       title=title,
                       description=description,
                       destination=self.getSourceSection(),
                       resource_value=resource_value,
                       destination_section=self.getDestinationSection(),
                       variation_base_category_list=('tax_category',
                                                     'salary_range'),
                       variation_category_list=var_cat_list,
                       base_contribution_list=base_contribution_list,
                       int_index=int_index,
                       **kw)

    # add cells categories to the Pay Sheet Line
    # it's a sort of inheritance of sub-object data
    if categories:
      categories_list = payline.getCategoryList()
      categories_list.extend(categories)
      # XXX editing categories directly is wrong !
      payline.edit(categories=categories_list)

    base_id = 'movement'
    a = payline.updateCellRange(base_id=base_id)
    # create cell_list
    for cell in good_cell_list:
      paycell = payline.newCell(base_id=base_id, *cell['category_list'])
      paycell.edit(mapped_value_property_list=('price', 'quantity'),
                   force_update=1,
                   **cell)
    return payline


  security.declareProtected(Permissions.AccessContentsInformation,
                          'getEditableModelLineAsDict')
  def getEditableModelLineAsDict(self, listbox, paysheet):
    '''
      listbox is composed by one line for each slice of editables model_lines
      this script will return editable model lines as a dict with the 
      properties that could/have be modified.
    '''
    portal = paysheet.getPortalObject()

    model_line_dict = {}
    for line in listbox:
      model_line_url = line['model_line']
      model_line = portal.restrictedTraverse(model_line_url)

      salary_range_relative_url=line['salary_range_relative_url']
      if salary_range_relative_url == '':
        salary_range_relative_url='no_slice'
      
      # if this is the first slice of the model_line, create the dict
      if not model_line_dict.has_key(model_line_url):
        model_line_dict[model_line_url] = {'int_index' :\
            model_line.getIntIndex()}

      model_line_dict[model_line_url][salary_range_relative_url] = {}
      slice_dict = model_line_dict[model_line_url][salary_range_relative_url]
      for tax_category in model_line.getTaxCategoryList():
        if line.has_key('%s_quantity' % tax_category) and \
            line.has_key('%s_price' % tax_category):
          slice_dict[tax_category] = dict(
                      quantity=line['%s_quantity' % tax_category],
                      price=line['%s_price' % tax_category],)
        else:
          LOG('ERP5', INFO, 'No attribute %s_quantity or %s_price for model_line %s' %
                   ( tax_category, tax_category, model_line_url ))
       
    return model_line_dict


  security.declareProtected(Permissions.AccessContentsInformation,
                          'getNotEditableModelLineAsDict')
  def getNotEditableModelLineAsDict(self, paysheet):
    '''
      return the not editable lines as dict
    '''
    model = paysheet.getSpecialiseValue()

    def sortByIntIndex(a, b):
      return cmp(a.getIntIndex(), b.getIntIndex())

    # get model lines
    portal_type_list = ['Pay Sheet Model Line']
    sub_object_list = paysheet.getInheritedObjectValueList(portal_type_list)
    sub_object_list.sort(sortByIntIndex)
    model_line_list = sub_object_list

    model_line_dict = {}
    for model_line in model_line_list:
      model_line_url = model_line.getRelativeUrl()
      cell_list = model_line.contentValues(portal_type='Pay Sheet Cell')

      for cell in cell_list:
        salary_range_relative_url = \
            cell.getVariationCategoryList(base_category_list='salary_range')
        tax_category = cell.getTaxCategory()
        if len(salary_range_relative_url):
          salary_range_relative_url = salary_range_relative_url[0]
        else:
          salary_range_relative_url = 'no_slice'
        
        # if this is the first slice of the model_line, create the dict
        if not model_line_dict.has_key(model_line_url):
          model_line_dict[model_line_url] = {'int_index' :\
              model_line.getIntIndex()}

        model_line_dict[model_line_url][salary_range_relative_url] = {}
        slice_dict = model_line_dict[model_line_url][salary_range_relative_url]
        slice_dict[tax_category] = dict(quantity=cell.getQuantity(),
                                        price=cell.getPrice())

    return model_line_dict


  security.declareProtected(Permissions.ModifyPortalContent,
                            'createPaySheetLineList')
  def createPaySheetLineList(self, listbox=None, batch_mode=0, **kw):
    '''Create all Pay Sheet Lines (editable or not)

      parameters :

      - batch_mode :if batch_mode is enabled (=1) then there is no preview view,
                    and editable lines are considered as not editable lines.
                    This is usefull to generate all PaySheet of a company.
                    Modification values can be made on each paysheet after, by
                    using the "Calculation of the Pay Sheet Transaction"
                    action button. (concerned model lines must be editable)

    '''

    paysheet = self
    
    if not batch_mode and listbox is not None:
      model_line_dict = paysheet.getEditableModelLineAsDict(listbox=listbox,
          paysheet=paysheet)

    # Get Precision
    precision = paysheet.getPriceCurrencyValue().getQuantityPrecision()

    # in this dictionary will be saved the current amount corresponding to 
    # the tuple (tax_category, base_amount) :
    # current_amount = base_amount_dict[base_amount][share]
    base_amount_dict = {}

    model = paysheet.getSpecialiseValue()

    def sortByIntIndex(a, b):
      return cmp(a.getIntIndex(), b.getIntIndex())

    # get model lines
    portal_type_list = ['Pay Sheet Model Line']
    sub_object_list = paysheet.getInheritedObjectValueList(portal_type_list)
    sub_object_list.sort(sortByIntIndex)
    model_line_list = sub_object_list

    pay_sheet_line_list = []

    # main loop : find all informations and create cell and PaySheetLines
    for model_line in model_line_list:
      cell_list = []
      # test with predicate if this model line could be applied
      if not model_line.test(paysheet,):
        # This model_line should not be applied
        LOG('ERP5', DEBUG, 'createPaySheetLineList: Model Line %s (%s) will'
            ' not be applied, because predicates does not match' %
            ( model_line.getTitle(), model_line.getRelativeUrl() ))
        continue

      service = model_line.getResourceValue()
      if service is None:
        raise ValueError, 'Model Line %s has no resource' % (
                                        model_line.getRelativeUrl())
      title = model_line.getTitleOrId()
      int_index = model_line.getFloatIndex()
      resource = service.getRelativeUrl()
      base_contribution_list = model_line.getBaseContributionList()
      
      # get the service provider, either on the model line, or using the
      # annotation line reference.
      source_section = None
      source_annotation_line_reference = \
                    model_line.getSourceAnnotationLineReference()
      if model_line.getSource():
        source_section = model_line.getSource()
      elif source_annotation_line_reference:
        for annotation_line in paysheet.contentValues(
                                    portal_type='Annotation Line'):
          annotation_line_reference = annotation_line.getReference() \
                                           or annotation_line.getId()
          if annotation_line_reference == source_annotation_line_reference \
              and annotation_line.getSource():
            source_section = annotation_line.getSource()
            break

      if model_line.getDescription():
        desc = model_line.getDescription()
        # if the model_line description is empty, the payroll service
        # description is used
      else:
        desc = service.getDescription()

      base_category_list = model_line.getVariationBaseCategoryList()
      category_list_list = []
      for base_cat in base_category_list:
        category_list = model_line.getVariationCategoryList(
                                        base_category_list=base_cat)
        category_list_list.append(category_list)
      cartesian_product = cartesianProduct(category_list_list)

      share = None
      slice = 'no_slice'
      indice = 0
      categories = []
      for cell_coordinates in cartesian_product:
        indice += 1
        cell = model_line.getCell(*cell_coordinates)
        if cell is None:
          LOG('ERP5', INFO, "Can't find the cell corresponding to those cells"
              " coordinates : %s" % cell_coordinates)
          # XXX is it enough to log ?
          continue

        if len(cell.getVariationCategoryList(\
            base_category_list='tax_category')):
          share = cell.getVariationCategoryList(\
              base_category_list='tax_category')[0]

        if len(cell.getVariationCategoryList(\
            base_category_list='salary_range')):
          slice = cell.getVariationCategoryList(\
              base_category_list='salary_range')[0]
    
        # get the edited values if this model_line is editable
        # and replace the original cell values by this ones
        if model_line.isEditable() and not batch_mode:
          tax_category = cell.getTaxCategory()

          # get the dict who contain modified values
          line_dict = model_line_dict[model_line.getRelativeUrl()]

          def getModifiedCell(cell, slice_dict, tax_category):
            '''
              return a cell with the modified values (contained in slice_dict)
            '''
            if slice_dict:
              if slice_dict.has_key(tax_category):
                if slice_dict[tax_category].has_key('quantity'):
                  cell = cell.asContext(\
                      quantity=slice_dict[tax_category]['quantity'])
                if slice_dict[tax_category].has_key('price'):
                  cell = cell.asContext(price=slice_dict[tax_category]['price'])
            return cell

          cell = getModifiedCell(cell, line_dict[slice], tax_category)

        # get the slice :
        model_slice = model_line.getParentValue().getCell(slice)
        quantity = 0.0
        price = 0.0
        model_slice_min = 0
        model_slice_max = 0
        if model_slice is None:
          pass # that's not a problem :)

        else:
          model_slice_min = model_slice.getQuantityRangeMin()
          model_slice_max = model_slice.getQuantityRangeMax()

        ######################
        # calculation part : #
        ######################

        # get script in this order
        # 1 - model_line script
        # 2 - model script
        # 3 - get the default calculation script

        # get the model line script
        script_name = model_line.getCalculationScriptId()
        if script_name is None:
          # if model line script is None, get the default model script
          script_name = model.getDefaultCalculationScriptId()
        if script_name is None:
          # if no calculation script found, use a default script :
          script_name = 'PaySheetTransaction_defaultCalculationScript'

        if getattr(paysheet, script_name, None) is None:
          raise ValueError, "Unable to find `%s` calculation script" % \
                                                           script_name
        calculation_script = getattr(paysheet, script_name, None)
        quantity=0
        price=0
        cell_dict = calculation_script(base_amount_dict=base_amount_dict,
                                       cell=cell,)
        cell_dict.update({'category_list': cell_coordinates})

        if cell_dict.has_key('categories'):
          for cat in cell_dict['categories']:
            if cat not in categories:
              categories.append(cat)

        quantity = cell_dict['quantity']
        price = cell_dict['price']

        if quantity and price:
          cell_list.append(cell_dict)

          # update the base_contribution
          for base_contribution in base_contribution_list:
            if quantity:
              if base_amount_dict.has_key(base_contribution) and \
                  base_amount_dict[base_contribution].has_key(share):
                old_val = base_amount_dict[base_contribution][share]
              else:
                old_val = 0
              new_val = old_val + quantity
              if not base_amount_dict.has_key(base_contribution):
                base_amount_dict[base_contribution]={}

              if price:
                new_val = round((old_val + quantity*price), precision)
              base_amount_dict[base_contribution][share] = new_val

      if cell_list and model_line.isCreatePaysheetLine():
        # create the PaySheetLine
        pay_sheet_line = paysheet.createPaySheetLine(
                                            title=title,
                                            resource=resource,
                                            source_section=source_section,
                                            int_index=int_index,
                                            desc=desc,
                                            base_contribution_list=base_contribution_list,
                                            cell_list=cell_list,
                                            categories=categories)
        pay_sheet_line_list.append(pay_sheet_line)


    # this script is used to add a line that permit to have good accounting 
    # lines
    post_calculation_script = paysheet._getTypeBasedMethod('postCalculation')
    if post_calculation_script:
      post_calculation_script()

    return pay_sheet_line_list

  def getInheritedObjectValueList(self, portal_type_list, property_list=()):
    '''Return a list of all subobjects of the herited model (incuding the
      dependencies).
      If property_list is provided, only subobjects with at least one of those
      properties is defined will be taken into account
    '''
    model = self.getSpecialiseValue()
    model_reference_dict = model.getInheritanceModelReferenceDict(
                                   portal_type_list=portal_type_list,
                                   property_list=property_list)

    sub_object_list = []
    traverse = self.getPortalObject().unrestrictedTraverse
    for model_url, id_list in model_reference_dict.items():
      model = traverse(model_url)
      sub_object_list.extend([model._getOb(x) for x in id_list])

    return sub_object_list

