##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon <guillaume@nexedi.com>
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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Core import MetaNode, MetaResource
from Products.CMFCore.WorkflowCore import WorkflowMethod

from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5.Document.Amount import Amount

from zLOG import LOG

class Immobilisation(XMLObject):
  """
    An Immobilisation object holds the information about
    an accounting immobilisation (in order to amortise an object)  
  """
  meta_type = 'ERP5 Immobilisation'
  portal_type = 'Immobilisation'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.View)

  # Declarative interfaces
  __implements__ = ( Interface.Variated, )

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Delivery
                      , PropertySheet.Reference
                      , PropertySheet.Amount
                      , PropertySheet.Price
                      , PropertySheet.Amortisation
                      )

                      
  # Factory Type Information
  factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An Immobilisation object holds the information about
an accounting immobilisation (in order to amortise an object)
            """
         , 'icon'           : 'segment_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addImmobilisation'
         , 'immediate_view' : 'predicate_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'predicate_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'segment_print'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_edit'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'translate'
          , 'name'          : 'Translate'
          , 'category'      : 'object_action'
          , 'action'        : 'segment_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }
 
 
  security.declareProtected(Permissions.View, 'getAmortisationOrDefaultAmortisationValue')
  def getAmortisationOrDefaultAmortisationValue(self, with_currency=0, **kw):
    """
    Returns the amortisation value.
    If it is None, returns the default amortisation value.
    """
    amortisation_value = self.getAmortisationValue()
    if amortisation_value is not None:
      return amortisation_value
    else:
      return self.getDefaultAmortisationValue(with_currency=with_currency, **kw)


  security.declareProtected(Permissions.View, 'getAmortisationOrDefaultAmortisationDuration')
  def getAmortisationOrDefaultAmortisationDuration(self, **kw):
    """
    Returns the remaining amortisation duration.
    If it is None, returns the default remaining amortisation duration.
    """
    amortisation_duration = self.getAmortisationDuration()
    if amortisation_duration is not None:
      return amortisation_duration
    else:
      return self.getDefaultAmortisationDuration(**kw)

    
  security.declareProtected(Permissions.View, 'getDefaultAmortisationDuration')
  def getDefaultAmortisationDuration(self, **kw):
    """
    Returns a calculated value of amortisation duration
    at the immobilisation movement date
    """
    item = self.getParent()
    current_date = self.getStopDate()
    if current_date is None or item is None:
      return None
    
    return item.getRemainingAmortisationDuration(current_date, from_immobilisation=1, **kw)
    

  security.declareProtected(Permissions.ModifyPortalContent, 'getDefaultAmortisationValue')
  def getDefaultAmortisationValue(self, with_currency=0, **kw):
    """
    Returns a calculated value of amortisation value
    at the immobilisation movement date
    """
    item = self.getParent()
    current_date = self.getStopDate()
    LOG('Immobilisation :',0, 'current_date=%s, item=%s' % (repr(current_date), repr(item)))
    if current_date is None or item is None:
      return None
    
    returned_value = item.getAmortisationPrice(current_date, from_immobilisation=1, with_currency=with_currency, **kw)
    return returned_value


  
  security.declareProtected(Permissions.View, 'isNotValid')
  def isNotValid(self):
    """
    Checks if necessary data is present on the immobilisation movement.
    Returns an error message, or None if the immobilisation is valid
    
    XXX please use checkConsistency API instead and try to use constraint
    checkers for implementation
    """
    item = self.getParent()
    if item is None:
      return "The immobilisation movement does not apply on an item"
    
    immo_date = self.getStopDate()
    if immo_date is None:
      return 'Date field is not filled'
    
    if self.getImmobilisation():
      immo_duration = self.getAmortisationDuration()
      if immo_duration is None:
        return 'Duration field is not filled'
      
      immo_value = self.getAmortisationValue()
      if immo_value is None:
        return 'Value field is not filled'
      
      immo_type = self.getAmortisationType()
      if immo_type is None or immo_type is "":
        return "Amortisation field is not filled"
        
      if immo_type == "degressive":
        fiscal_coef = self.getFiscalCoefficient()
        if fiscal_coef is None:
          return "Fiscal coefficient field is not filled"
      
      vat = self.getVat()
      if vat is None:
        return "VAT Amount field is not filled"
        
      
      
      for (account, text) in ( (self.getInputAccount()         , "Input Account"),
                               (self.getOutputAccount()        , "Output Account"),
                               (self.getImmobilisationAccount(), "Immobilisation Account"),
                               (self.getAmortisationAccount()  , "Amortisation Account"),
                               (self.getDepreciationAccount()  , "Deprecisation Account"),
                               (self.getVatAccount()           , "VAT Account") ):
        if account is None or account is "":
          return text + " list has no selected choice"
      
      organisation = self.getOrganisation()
      if organisation is None:
        return "Item %s does not belong to an organisation at this date" % item.getTitle()
      
      financial_date = organisation.getFinancialYearEndDate()
      if financial_date is None:
        return "The organisation which owns the item at this date has no financial year end date"
      
      currency = self.getCurrency()
      if currency is None:
        return "The organisation which owns the item at this date has no amortisation currency"
          
      return None
    
    
  security.declareProtected(Permissions.View, 'getOrganisation')
  def getOrganisation(self):
    """
    Returns the organisation which owns the item on which the
    immobilisation movement applies, at the time of the immobilisation
    movement
    
    XXX Naming problem -> it is an owner
    Please rename to getSectionValue on both item and immobilisation
    """
#     if self.isContext() and hasattr(self, 'organisation'):
#       return self.organisation
    
    item = self.getParent()
    date = self.getStopDate()
    if item is None or date is None:
      return None  
    LOG('Immobilisation :', 0, 'item = %s for immobilisation %s' % (repr(item), repr(self)))
    return item.getOwner(at_date = date)
  
  
  security.declareProtected(Permissions.View, 'getOrganisationTitle')
  def getOrganisationTitle(self):
    """
    Returns the name of the organisation which owns the
    item on which the immobilisation movement applies, at the
    time of the immobilisation movement
    
    XXX id. same naming problem getSectionTitle
    """
    organisation = self.getOrganisation()
    if organisation is None:
      return None
    return organisation.getTitle()
  
  
  security.declareProtected(Permissions.View, 'getCurrency')
  def getCurrency(self):
    """
    Returns the used currency id for this particular immobilisation movement
    
    XXX Rename to getPriceCurrency (this is the name we use at this point, it will be renamed
    some day to getTradeCurrency - make sure getPriceCurrencyValue is object and getPriceCurrency is not)
    """
    organisation = self.getOrganisation()
    if organisation is not None:
      LOG('Immobilisation :', 0, 'organisation = %s, currency = %s' % (repr(organisation), repr(organisation.getSocialCapitalCurrency())))
      return organisation.getSocialCapitalCurrency()
    LOG('Immobilisation :', 0, 'organisation = %s, currency = %s' % (repr(organisation), repr(None)))
    return None
  
    
  