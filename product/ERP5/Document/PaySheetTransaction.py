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


  security.declareProtected(Permissions.AddPortalContent,
                          'createPaySheetLine')
  def createPaySheetLine(self, cell_list, title='', res='', desc='', **kw):
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
        paysheet_items[service_id] = { 'title'   : model_line.getTitleOrId()
                                     , 'id'      : model_line.getId()
                                     , 'desc'    : []
                                     , 'res'     : service.getRelativeUrl()
                                     , 'cell_list'   : []
                                     }
      
      # create cells if a value has been entered by accountable
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
                        title    = item['title']
                      , id       = item['id']
                      , res      = item['res']
                      , desc     = desc
                      , cell_list    = item['cell_list']
                      )


  security.declareProtected(Permissions.ModifyPortalContent,
                          'createNotEditablePaySheetLineList')
  def createNotEditablePaySheetLineList(self, **kw):
    '''
      get all data required to create not editable paysheet lines and create it
      editable paysheet lines have been created by a script
    '''

    # Get Precision
    precision = self.getPriceCurrencyValue().getQuantityPrecision()

    def getDictList(category_list):
      '''
        This method return a list of dict wich are composed with the given
        category as key and an integer as value. It's used to find datas 
        in a two-dimensional table
      '''
      list_of_dict = []
      for category in category_list:
        base_amount_list=[x.getRelativeUrl() for x in\
                          self.portal_categories[category].objectValues()]
        list_of_dict.append(dict([[base, base_amount_list.index(base)] \
            for base in base_amount_list]))
      return list_of_dict

    def getEmptyTwoDimentionalTable(nb_columns=0, nb_rows=0):
      '''
        create a two-dimentional table with nb_columns columns and nb_rows rows
        all item of this table are set to None
        ex : with nb_columns=2 and nb_rows=4, this function returns :
        [[None, None, None, None], [None, None, None, None]]
      '''
      base_amount = []
      for i in range(nb_columns):
        line = []
        for j in range(nb_rows):
          line.append(None)
        base_amount.append(line)
      return base_amount

    # this dict permit to have the index of the category in the table
    column, row = getDictList(['tax_category', 'base_amount'])
    base_amount_table = getEmptyTwoDimentionalTable(nb_columns=len(column),
                                                    nb_rows=len(row))
    # XXX currently, there is a problem not resolved yet :
    # if a tax_category have a base_application ('non_deductible_tax','bonus')
    # and if a bonus have a base_application ('base_salary',), calculation 
    # must be made in a particular order, and sometimes, it's possible to 
    # have circular dependencies and so, impossible to resove this cases.
    # The best, will to do calculation with understanding dependencies and 
    # raise an error if there is circular dependence. Currently, caluls are 
    # made in a paticular order defined by the list order_of_calculation 
    # so dependencies are not taken into account. 
    # And result are wrong in some cases.
    # solutions :
    #  1 - do calculation without any order and redo evry calculs while a value
    #  in the base_amount_table have changed. This is a little slow but safe.
    #  2 - determine an order using dependencies graph, but this solution 
    #  is not evolutive and safe, because it not take into account the new 
    #  categories
    #  3 - add an order field in paysheet lines and model lines : the user 
    #  must determine an order manually and it will be easy to apply it
    # in my opinion, the best solution for the accountant is the first, but it 
    # will be slow, the easier is the 3.


    # It's important to do calculation in a precise order,
    # most of time, a tax could depend on base_salary and bonus, 
    # so they must be calculated before

    def sortByIntIndex(a, b):
      return cmp(a.getIntIndex(),
                 b.getIntIndex())


    base_amount_list = self.portal_categories['base_amount'].contentValues()
    base_amount_list.sort(sortByIntIndex)
    order_of_calculation = [x.getRelativeUrl() for x in base_amount_list]
    #order_of_calculation = ('base_amount/base_salary', 'base_amount/bonus', 
    #                        'base_amount/non_deductible_tax', 
    #                        'base_amount/deductible_tax')

    # it's important to get the editable lines to know if they contribute to
    # a base_amount (this is required to do the calcul later
    # get edited lines:
    paysheetline_list = self.contentValues(portal_type = ['Pay Sheet Line'])

    for paysheetline in paysheetline_list:
      service = paysheetline.getResourceValue()
      base_amount_list = service.getBaseAmountList(base=1)
      for base_amount in base_amount_list:
        if not row.has_key(base_amount):
           raise ValueError, "Unable to find `%s` base_amount category" % \
                                                                 base_amount
        paysheetcell_list = paysheetline.contentValues(portal_type = \
                                                            ['Pay Sheet Cell'])
        for paysheetcell in paysheetcell_list:
          tax_category = paysheetcell.getTaxCategory(base=1)
          if tax_category and paysheetcell.getQuantity():
            old_val = base_amount_table[column[tax_category]][row[base_amount]]
            if old_val is not None:
              new_val = old_val + paysheetcell.getQuantity()
            else: 
              new_val = paysheetcell.getQuantity()
            base_amount_table[column[tax_category]][row[base_amount]] = new_val

    # get not editables model lines
    model = self.getSpecialiseValue()
    model_line_list = model.contentValues(portal_type='Pay Sheet Model Line')

    pay_sheet_line_list = []
    employee_tax_amount = 0

    # initilise a dict with model_line relative url and 0 value to know
    # if a contribution have already been calculated
    already_calculate = dict([[model_line.getRelativeUrl(), 0] \
        for model_line in model_line_list])

    # main loop : find all informations and create cell and PaySheetLines
    for base_ordered in order_of_calculation:
      for model_line in model_line_list:

        # get only not editables model lines
        if model_line.getEditable():
          continue
        if model_line.getResourceValue().getBaseAmountList(base=1) and \
            base_ordered not in \
            model_line.getResourceValue().getBaseAmountList(base=1):
            continue
        if already_calculate[model_line.getRelativeUrl()]:
          continue
        else:
          already_calculate[model_line.getRelativeUrl()] = 1
        # this prevent to calculate two times the same model line if it's 
        # resource have many Base Participation, it will be calculate 
        # many times. 

        cell_list       = []
        # test with predicate if this model line could be applied
        if not model_line.test(self,):
          # This line should not be used
          continue

        service     = model_line.getResourceValue()
        title       = model_line.getTitleOrId()
        id          = model_line.getId()
        res         = service.getRelativeUrl()
        if model_line.getDescription():
          desc      = ''.join(model_line.getDescription())
        # if the model_line description is empty, the payroll service 
        # description is used
        else: desc  = ''.join(service.getDescription())
        
        variation_share_list = model_line.getVariationCategoryList(\
                                        base_category_list=['tax_category',])
        variation_slice_list = model_line.getVariationCategoryList(\
                                        base_category_list=['salary_range',])

        for share in variation_share_list:
          base_application = None
          for slice in variation_slice_list:

            #get the amount of application for this line
            base_application_list = model_line.getBaseAmountList(base=1)
            if base_application is None:
              base_application = 0
              for base in model_line.getBaseAmountList(base=1):
                if base_amount_table[column[share]][row[base]] is not None:
                  base_application += \
                      base_amount_table[column[share]][row[base]]
              
            cell = model_line.getCell(slice, share)
            
            if cell is not None:
              # get the slice :
              model_slice = None
              model_slice = model_line.getParentValue().getCell(slice)
              quantity = 0.0
              price = 0.0
              if model_slice is not None:
                model_slice_min = model_slice.getQuantityRangeMin()
                model_slice_max = model_slice.getQuantityRangeMax()
                quantity = cell.getQuantity()
                price = cell.getPrice()

                ######################
                # calculation part : #
                ######################
                script_name = model.getLocalizedCalculationScriptId()
                if script_name is None or \
                    getattr(self, script_name, None) is None:
                  # if no calculation script found, use a default method :
                  if not quantity:
                    if base_application <= model_slice_max:
                      quantity = base_application
                    else: 
                      quantity = model_slice_max
                else:
                  localized_calculation_script = getattr(self, script_name, 
                                                         None)
                  quantity, price = localized_calculation_script(\
                      paysheet=self, 
                      model_slice_min = model_slice_min, 
                      model_slice_max=model_slice_max, 
                      quantity=quantity, 
                      price=price, 
                      model_line=model_line)

              # Cell creation :
              # Define an empty new cell
              new_cell = { 'axe_list' : [share, slice]
                         , 'quantity' : quantity
                         , 'price'    : price
                         }
              cell_list.append(new_cell)

              #XXX this is a hack to have the net salary
              if price is not None and 'employee_share' in share and\
                  base_ordered not in ('base_salary', 'bonus') :
                employee_tax_amount += round((price * quantity), precision)

              # update base participation
              base_participation_list = service.getBaseAmountList(base=1)
              for base_participation in base_participation_list:
                old_val = \
                    base_amount_table[column[share]][row[base_participation]]

                if quantity:
                  if old_val is not None:
                    new_val = old_val + quantity
                  else:
                    new_val = quantity
                  if price:
                    if old_val is not None:
                      new_val = round((old_val + quantity*price), precision)
                base_amount_table[column[share]][row[base_participation]]= \
                                                                        new_val
                base_amount_table[column[share]][row[base_participation]] = \
                                                                        new_val

            # decrease the base_application used for this model line if 
            if cell is not None :
              base_application -= quantity

        if cell_list:
          # create the PaySheetLine
          pay_sheet_line = self.createPaySheetLine(
                                                    title     = title
                                                  , id        = id
                                                  , res       = res
                                                  , desc      = desc
                                                  , cell_list = cell_list
                                                  )
          pay_sheet_line_list.append(pay_sheet_line)

    # create a line of the total tax payed by the employee
    # this hack permit to calculate the net salary
    new_cell = { 'axe_list' : [ 'tax_category/employer_share',
                                'salary_range/france/forfait']
               , 'quantity'     : employee_tax_amount
               , 'price'     : 1
               }
    pay_sheet_line = self.createPaySheetLine(
              title    = 'total employee contributions'
            , res      = 'payroll_service_module/total_employee_contributions'
            , desc     = 'this line permit to calculate the sum of the employer'
                         ' share and permit to calculate the net salary'
            , cell_list    = [new_cell])

    return pay_sheet_line_list
