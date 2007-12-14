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
import pprint
from zLOG import LOG

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

  # Global variables
  _transaction_line_portal_type = 'Pay Sheet Transaction Line'
  
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
      for object in object_ratio_list:
        if object.getReference() == ratio_reference:
          return object.getQuantity()

    # if not find in the paysheet, look on dependence tree
    sub_object_list = self.getSubObjectValueList(portal_type_list)
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
    if not isinstance(ratio_reference_list, list):
      return [self.getRatioQuantityFromReference(ratio_reference_list)]
    return [self.getRatioQuantityFromReference(reference) \
        for reference in ratio_reference_list]

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityFromReference')
  def getAnnotationLineFromReference(self, reference=None):
    """
    return the annotation line correponding to the reference,
    None if reference not found
    """
    # get Annotation Lines
    portal_type_list = ['Annotation Line']
    
    annotation_line_list = self.contentValues(portal_type=portal_type_list)

    # look for annotation lines on the paysheet
    if annotation_line_list:
      for annotation_line in annotation_line_list:
        if annotation_line.getReference() == reference:
          return annotation_line

    # if not find in the paysheet, look on dependence tree
    sub_object_list = self.getSubObjectValueList(portal_type_list)
    annotation_line_list = sub_object_list
    for annotation_line in annotation_line_list:
      if annotation_line.getReference() == reference:
        return annotation_line

    return None 

  security.declareProtected(Permissions.AccessContentsInformation,
                          'getRatioQuantityList')
  def getAnnotationLineListList(self, reference_list):
    """
    Return a annotation line list corresponding to the reference_list
    reference_list is a list of references to the Annotation Line we want 
    to get.
    """
    if not isinstance(reference_list, list):
      return [self.getAnnotationLineFromReference(reference_list)]
    return [self.getAnnotationLineFromReference(reference) \
        for reference in reference_list]

  security.declareProtected(Permissions.AddPortalContent,
                          'createPaySheetLine')
  def createPaySheetLine(self, cell_list, title='', res='', desc='', 
      base_amount_list=None, int_index=None, categories=None, **kw):
    '''
    This function register all paysheet informations in paysheet lines and 
    cells. Select good cells only
    '''
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

    # Construct the description
    description = None
    if len(desc) > 0:
      description = desc#'\n'.join(desc)

    source = self.getPortalObject().restrictedTraverse(res).getSource()
    # Add a new Pay Sheet Line
    payline = self.newContent(
             portal_type                  = 'Pay Sheet Line',
             title                        = title,
             description                  = description,
             destination                  = self.getSourceSection(),
             source_section               = source,
             resource                     = res,
             destination_section          = self.getDestinationSection(),
             variation_base_category_list = ('tax_category', 'salary_range'),
             variation_category_list      = var_cat_list,
             base_amount_list             = base_amount_list,
             int_index                    = int_index,
             **kw)

    # add cells categories to the Pay Sheet Line
    # it's a sort of inheritance of sub-object data
    if categories is not None:
      categories_list = payline.getCategoryList()
      categories_list.extend(categories)
      payline.edit(categories = categories_list)

    base_id = 'movement'
    a = payline.updateCellRange(base_id = base_id)
    # create cell_list
    for cell in good_cell_list:
      paycell = payline.newCell(base_id = base_id, *cell['category_list'])
      # if the price aven't be completed, it should be set to 1 (=100%)
      if not cell['price']:
        cell['price'] = 1
      paycell.edit( mapped_value_property_list = ('price', 'quantity'),
                    force_update               = 1,
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
          slice_dict[tax_category]=\
              {
                  'quantity' : line['%s_quantity' % tax_category],
                  'price' : line['%s_price' % tax_category],
              }
        else:
          LOG('Warning, no atribute %s_quantity or %s_price for model_line %s' %
              tax_category, tax_category, model_line_url, 0, '')
       
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
    sub_object_list = paysheet.getSubObjectValueList(portal_type_list)
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
        slice_dict[tax_category]=\
          {
              'quantity' : cell.getQuantity(),
              'price' : cell.getPrice(),
          }
       
    return model_line_dict


  security.declareProtected(Permissions.ModifyPortalContent,
                          'createPaySheetLineList')
  def createPaySheetLineList(self, listbox=None, batch_mode=0, **kw):
    '''
      create all Pay Sheet Lines (editable or not)

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


    base_amount_list = paysheet.portal_categories['base_amount'].contentValues()
    base_amount_list.sort(sortByIntIndex)


    # get model lines
    portal_type_list = ['Pay Sheet Model Line']
    sub_object_list = paysheet.getSubObjectValueList(portal_type_list)
    sub_object_list.sort(sortByIntIndex)
    model_line_list = sub_object_list

    pay_sheet_line_list = []

    # main loop : find all informations and create cell and PaySheetLines
    for model_line in model_line_list:
      cell_list       = []
      # test with predicate if this model line could be applied
      if not model_line.test(paysheet,):
        # This model_line should not be applied
        LOG('createPaySheetLineList :', 0, 
            'Model Line %s will not be applied, because predicates not match' % 
            model_line.getTitle())
        continue

      service          = model_line.getResourceValue()
      title            = model_line.getTitleOrId()
      int_index        = model_line.getFloatIndex()
      id               = model_line.getId()
      base_amount_list = model_line.getBaseAmountList()
      res              = service.getRelativeUrl()

      if model_line.getDescription():
        desc = ''.join(model_line.getDescription())
      # if the model_line description is empty, the payroll service 
      # description is used
      else: 
        desc = ''.join(service.getDescription())

      base_category_list = model_line.getVariationBaseCategoryList()
      list_of_list = []
      for base_cat in base_category_list:
        list = model_line.getVariationCategoryList(base_category_list=base_cat)
        list_of_list.append(list)
      cartesian_product = cartesianProduct(list_of_list)

      share = None
      slice = 'no_slice'
      indice = 0
      categories = []
      for tuple in cartesian_product:
        indice += 1
        cell = model_line.getCell(*tuple)
        if cell is None:
          LOG("Warning ! can't find the cell corresponding to this tuple : %s",
              0, tuple)
          continue

        if len(cell.getVariationCategoryList(base_category_list='tax_category')):
          share = \
              cell.getVariationCategoryList(base_category_list='tax_category')[0]

        if len(cell.getVariationCategoryList(base_category_list='salary_range')):
          slice = \
              cell.getVariationCategoryList(base_category_list='salary_range')[0]
    
        # get the edited values if this model_line is editable
        # and replace the original cell values by this ones
        if model_line.isEditable() and not batch_mode:
          tax_category = cell.getTaxCategory()

          # get the dict who contain modified values
          line_dict = model_line_dict[model_line.getRelativeUrl()]

          def getModifiedCell(cell, slice_dict, tax_category):
            '''
              return a cell with the modified values (conained in slice_dict)
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

          #LOG('createPaySheetLineList :', 0, 'model_slice of slice '
          #  '"%s" of the model_line "%s" is None' % (slice,
          #    model_line.getTitle()))

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
        #LOG('script_name :', 0, script_name)
        cell_dict = calculation_script(base_amount_dict=base_amount_dict, 
                                        cell=cell,)
        cell_dict.update({'category_list':tuple})

        if cell_dict.has_key('categories'):
          for cat in cell_dict['categories']:
            if cat not in categories:
              categories.append(cat)

        quantity = cell_dict['quantity']
        price = cell_dict['price']

#        # Define an empty new cell
#        new_cell = { 'axe_list' : tuple, # share, slice
#                     'quantity' : quantity,
#                     'price'    : price,
#                     #'categories' : causality/machin_module/annotation_line,
#                   }
        cell_list.append(cell_dict)

        # update the base_participation
        base_participation_list = service.getBaseAmountList(base=1)
        for base_participation in base_participation_list:
          if quantity:
            if base_amount_dict.has_key(base_participation) and \
                base_amount_dict[base_participation].has_key(share):
              old_val = base_amount_dict[base_participation][share]
            else:
              old_val = 0
            new_val = old_val + quantity
            if not base_amount_dict.has_key(base_participation):
              base_amount_dict[base_participation]={}

            if price:
              new_val = round((old_val + quantity*price), precision) 
            base_amount_dict[base_participation][share] = new_val

      if cell_list:
        # create the PaySheetLine
        pay_sheet_line = paysheet.createPaySheetLine(
                                              title     = title,
                                              res       = res,
                                              int_index = int_index,
                                              desc      = desc,
                                              base_amount_list = base_amount_list,
                                              cell_list = cell_list,
                                              categories= categories)
        pay_sheet_line_list.append(pay_sheet_line)


    # this script is used to add a line that permit to have good accounting 
    # lines
    post_calculation_script = getattr(paysheet,
                                'PaySheetTransaction_postCalculation', None)
    if post_calculation_script:
      post_calculation_script()

    return pay_sheet_line_list

  def getSubObjectValueList(self, portal_type_list):
    '''
      return a list of all subobject of the herited model (incuding the
      dependencies)
    '''
    model = self.getSpecialiseValue()

    model_reference_dict={}
    model.getInheritanceModelReferenceDict(\
        model_reference_dict=model_reference_dict, 
        model_list=model,
        portal_type_list=portal_type_list,
        reference_list=[])

    # add line of base model without reference
    model_dict = model.getReferenceDict(\
        portal_type_list=portal_type_list,
        get_none_reference=1)
    id_list = model_dict.values()
    if model_reference_dict.has_key(model.getRelativeUrl()):
      model_reference_dict[model.getRelativeUrl()].extend(id_list)
    else:
      model_reference_dict[model.getRelativeUrl()]=id_list

    # get sub objects
    key_list = model_reference_dict.keys()

    sub_object_list = []

    for key in key_list:
      id_list = model_reference_dict[key]
      model = self.getPortalObject().restrictedTraverse(key)
      if model is None:
        LOG("copyInheritanceSubObjects,", 0, "can't find model %s" % key)

      for id in id_list:
        object = model._getOb(id)
        sub_object_list.append(object)

    return sub_object_list

