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
from zLOG import LOG

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
    or description if ratio value is empty,
    None if ratio_reference not found
    """
    object_ratio_list = self.contentValues(portal_type=\
        'Pay Sheet Model Ratio Line')
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


  security.declareProtected(Permissions.AddPortalContent,
                          'createPaySheetLine')
  def createPaySheetLine(self, cell_list, title='', res='', desc='', 
      base_amount_list=None, int_index=None, **kw):
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
      for category in cell['axe_list']:
        if category not in var_cat_list: 
          var_cat_list.append(category)

    # Construct the description
    description = None
    if len(desc) > 0:
      description = desc#'\n'.join(desc)
    # Add a new Pay Sheet Line
    payline = self.newContent(
             portal_type                  = 'Pay Sheet Line',
             title                        = title,
             description                  = description,
             source_section               =  \
                self.getPortalObject().restrictedTraverse(res).getSource(),
             resource                     = res,
             destination_section          = self.getDestinationSection(),
             destination                  = self.getDestinationSection(),
             variation_base_category_list = ('tax_category', 'salary_range'),
             variation_category_list      = var_cat_list,
             base_amount_list             = base_amount_list,
             int_index                    = int_index,
             **kw)

    base_id = 'movement'
    a = payline.updateCellRange(script_id = 'PaySheetLine_asCellRange',
                                base_id   = base_id)
    # create cell_list
    for cell in good_cell_list:
      cell_cat_list = cell['axe_list']
      paycell = payline.newCell(base_id = base_id, *cell_cat_list)
      # if the quantity aven't be completed, it should be set to 1 (=100%)
      if cell['price']:
        price = cell['price']
      else: 
        price = 1
      paycell.edit( mapped_value_property_list = ('price', 'quantity')
                  , quantity                   = cell['quantity']
                  , price                      = price
                  , force_update               = 1
                  , category_list              = cell_cat_list
                  )

    return payline



  security.declareProtected(Permissions.AddPortalContent,
                          'createEditablePaySheetLineList')
  def createEditablePaySheetLineList(self, listbox, **kw):
    '''
      this script is called by the preview form to ask to the accountable 
      the values  of the editables lines and create corresponding 
      PaySheetLines with this values
    '''

    paysheet = self 

    paysheet_items = {}
    for line in listbox:
      model_line = paysheet.getPortalObject().restrictedTraverse(\
                                                          line['model_line'])
      service      = model_line.getResourceValue()
      service_id   = service.getId()
      quantity     = line['quantity']
      price        = line['price']
      tax_category = line['tax_category_relative_url']

      variation_category_list = model_line.getVariationCategoryList(\
                                            base_category_list='salary_range')
      salary_range_categories = []
      #for category in resource_variation_category_list:
      for category in variation_category_list:
        if category.startswith('salary_range/'): 
          salary_range_categories.append(category)

      # perhaps here it will be necesary to raise an error ?
      if not paysheet_items.has_key(service_id):
        paysheet_items[service_id] = { 
                           'title'            : model_line.getTitleOrId(),
                           'desc'             : [],
                           'base_amount_list' : model_line.getBaseAmountList(),
                           'res'              : service.getRelativeUrl(),
                           'int_index'        : model_line.getFloatIndex(),
                           'cell_list'        : []
                         }
      
      # create cells if a value has been entered 
      if quantity or price:
        for salary_range in salary_range_categories: 
          # Define an empty new cell
          new_cell = None
          new_cell = { 'axe_list' : [tax_category,salary_range]
                     , 'quantity' : quantity
                     , 'price'    : price
                     }
          # Add the cell to the conresponding paysheet item 
          if new_cell: 
            paysheet_items[service_id]['cell_list'].append(new_cell) 
            # Save the comment as description 
            if model_line.getDescription():
              paysheet_items[service_id]['desc'].append(\
                                                  model_line.getDescription())
            else:
              resource_description = \
                                model_line.getResourceValue().getDescription()
              paysheet_items[service_id]['desc'].append(resource_description)

    # Create a paysheet item for each service with user data in it
    for item in paysheet_items.values():
      if item['cell_list']:
        if len(item['desc']) > 0: 
          desc = '\n'.join(item['desc'])
        else: 
          desc = None
        paysheet.createPaySheetLine( 
                                    title     = item['title'],
                                    res       = item['res'],
                                    desc      = desc,
                                    cell_list = item['cell_list'],
                                    int_index = item['int_index'],
                                    base_amount_list=item['base_amount_list'],)


  security.declareProtected(Permissions.ModifyPortalContent,
                          'createNotEditablePaySheetLineList')
  def createNotEditablePaySheetLineList(self, **kw):
    '''
      get all data required to create not editable paysheet lines and create it
      editable paysheet lines have been created by a script
    '''

    # Get Precision
    precision = self.getPriceCurrencyValue().getQuantityPrecision()


    # in this dictionary will be saved the current amount corresponding to 
    # the tuple (tax_category, base_amount) :
    # current_amount = base_amount_current_value_dict[base_amount]
    base_amount_current_value_dict = {}

    def sortByIntIndex(a, b):
      return cmp(a.getIntIndex(),
                 b.getIntIndex())


    base_amount_list = self.portal_categories['base_amount'].contentValues()
    base_amount_list.sort(sortByIntIndex)

    # it's important to get the editable lines to know if they contribute to
    # a base_amount (this is required to do the calcul later)

    # get edited lines:
    paysheetline_list = self.contentValues(portal_type = ['Pay Sheet Line'])

    for paysheetline in paysheetline_list:
      service = paysheetline.getResourceValue()
      base_amount_list = service.getBaseAmountList(base=1)
      for base_amount in base_amount_list:
        paysheetcell_list = paysheetline.contentValues(portal_type = \
                                                            ['Pay Sheet Cell'])
        for paysheetcell in paysheetcell_list:
          tax_category = paysheetcell.getTaxCategory(base=1)
          if tax_category and paysheetcell.getQuantity():
            if base_amount_current_value_dict.has_key(base_amount):
              old_val = base_amount_current_value_dict[base_amount]
            else:
              old_val = 0
            new_val = old_val + paysheetcell.getQuantity()
            # increment the corresponding amount
            base_amount_current_value_dict[base_amount] = new_val

    # get not editables model lines
    model = self.getSpecialiseValue()
    model_line_list = model.contentValues(portal_type='Pay Sheet Model Line',
                                          sort_on='int_index')
    model_line_list = [line for line in model_line_list if not line.getEditable()]

    pay_sheet_line_list = []

    # main loop : find all informations and create cell and PaySheetLines
    for model_line in model_line_list:
      cell_list       = []
      # test with predicate if this model line could be applied
      if not model_line.test(self,):
        # This line should not be used
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
      
      variation_share_list = model_line.getVariationCategoryList(\
                                      base_category_list=['tax_category',])
      variation_slice_list = model_line.getVariationCategoryList(\
                                      base_category_list=['salary_range',])

      for slice in variation_slice_list:
        for share in variation_share_list:
          cell = model_line.getCell(slice, share)
          if cell is None:
            LOG('createNotEditablePaySheetLineList : cell is None')
            continue
          # get the slice :
          model_slice = model_line.getParentValue().getCell(slice)
          quantity = 0.0
          price = 0.0
          if model_slice is None:
            LOG('createNotEditablePaySheetLineList : model_slice %s is None' %\
                                                                          slice)
            continue
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

          if getattr(self, script_name, None) is None:
            raise ValueError, "Unable to find `%s` calculation script" % \
                                                             script_name
          calculation_script = getattr(self, script_name, None)
          quantity=0
          price=0
          LOG('script_name :', 0, script_name)
          result = calculation_script(\
            base_amount_current_value_dict=base_amount_current_value_dict,
            share=share, #XXX
            model_slice_min=model_slice_min, 
            model_slice_max=model_slice_max, 
            cell=cell,)

          quantity = result['quantity']
          price = result['price']

          # Cell creation :
          # Define an empty new cell
          new_cell = { 'axe_list' : [share, slice],
                       'quantity' : quantity,
                       'price'    : price,
                     }
          cell_list.append(new_cell)

        # update base participation
        base_participation_list = service.getBaseAmountList(base=1)
        for base_participation in base_participation_list:
          if quantity:
            if base_amount_current_value_dict.has_key(base_participation):
              old_val = base_amount_current_value_dict[base_participation]
            else:
              old_val = 0
            new_val = old_val + quantity

            if price:
              new_val = round((old_val + quantity*price), precision) 
            base_amount_current_value_dict[base_participation] = new_val

      if cell_list:
        # create the PaySheetLine
        pay_sheet_line = self.createPaySheetLine(
                                    title     = title,
                                    res       = res,
                                    int_index = int_index,
                                    desc      = desc,
                                    base_amount_list = base_amount_list,
                                    cell_list = cell_list,
                                  )
        pay_sheet_line_list.append(pay_sheet_line)


    # this script is used to add a line that permit to have good accounting 
    # lines
    post_calculation_script = getattr(self,
                                'PaySheetTransaction_postCalculation', None)
    if post_calculation_script:
      post_calculation_script()

    return pay_sheet_line_list
