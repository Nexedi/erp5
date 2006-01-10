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

from Products.ERP5Type import Base, Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Core import MetaNode, MetaResource
from Products.CMFCore.WorkflowCore import WorkflowMethod

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Amount import Amount
from Products.ERP5.Document.Movement import Movement

from string import capitalize
from zLOG import LOG

class Immobilisation(Movement, XMLObject):
  """
    An Immobilisation object holds the information about
    an accounting immobilisation (in order to amortise an object)

    It is an instant movement without source or destination, but which
    implies a state change and a source_decision and a source_destination
    Do not index in stock table
  """
  meta_type = 'ERP5 Immobilisation'
  portal_type = 'Immobilisation'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isMovement = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

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
 


  security.declareProtected(Permissions.View, 'getDefaultDurability')
  def getDefaultDurability(self, **kw):
    """
    Returns a calculated value of the remaining durability
    of the item at the immobilisation movement date
    """
    item = self.getParent()
    current_date = self.getStopDate()
    if current_date is None or item is None:
      return None
    return item.getRemainingDurability(current_date, from_immobilisation=1, **kw)
  
  
  security.declareProtected(Permissions.View, 'getDurabilityOrDefaultDurability')
  def getDurabilityOrDefaultDurability(self, **kw):
    """
    Returns the remaining durability.
    If it is None, returns the default durability
    """
    durability = self.getDurability()
    if durability is None:
      durability = self.getDefaultDurability(**kw)
    return durability

    
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
  
  
  security.declareProtected(Permissions.View, 'getAmortisationOrDefaultAmortisationDuration')
  def getAmortisationOrDefaultAmortisationDuration(self, **kw):
    """
    Returns the remaining amortisation duration.
    If it is None, returns the default remaining amortisation duration.
    """
    amortisation_duration = self.getAmortisationDuration()
    if amortisation_duration is None:
      amortisation_duration = self.getDefaultAmortisationDuration(**kw)
    return amortisation_duration
    

  security.declareProtected(Permissions.ModifyPortalContent, 'getDefaultAmortisationPrice')
  def getDefaultAmortisationPrice(self, with_currency=0, **kw):
    """
    Returns a calculated value of amortisation value
    at the immobilisation movement date
    """
    item = self.getParent()
    current_date = self.getStopDate()
    if current_date is None or item is None:
      return None
    returned_value = item.getAmortisationPrice(current_date, from_immobilisation=1, with_currency=with_currency, **kw)
    return returned_value
  
  
  security.declareProtected(Permissions.View, 'getAmortisationOrDefaultAmortisationPrice')
  def getAmortisationOrDefaultAmortisationPrice(self, with_currency=0, **kw):
    """
    Returns the amortisation value.
    If it is None, returns the default amortisation value.
    """
    amortisation_price = self.getAmortisationStartPrice()
    if amortisation_price is None:
      amortisation_price = self.getDefaultAmortisationPrice(with_currency=with_currency, **kw)
    return amortisation_price


  security.declarePrivate('_checkConsistency')
  def _checkConsistency(self, fixit=0, mapped_value_property_list=()):
    relative_url = self.getRelativeUrl()
    def checkValue(property_dict):
      """
      property_dict must have the following format :
      { "property_name" : { "values" : [list of forbidden values], "message" :
                                               ["type of error", degree, "Error message"] },
        ...
      }
      """
      errors = []
      for property in property_dict.keys():
        getter = getattr(self, "get" + ''.join( [capitalize(x) for x in property.split("_")] ), None)
        if getter is None:
          errors += [(relative_url, "Accessor inconsistency", 100, "No accessor for property %s" % property)]
        else:
          property_value = getter()
          forbidden_value_list = property_dict[property]["values"]
          if property_value in forbidden_value_list:
            message = property_dict[property]["message"]
            errors += [(relative_url, message[0], message[1], message[2])]
      return errors
      
    
    errors = []
   
    # Checks common to every amortisation method
    errors.extend( checkValue( { "parent"    : { "values": [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "The immobilisation movement does not apply on an item" ] },
                                 "stop_date" : { "values": [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "Date property is empty" ] },
                                 "durability": { "values": [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "Durability property is empty" ] },
                               } ) )


    if self.getImmobilisation():
      errors.extend( checkValue( { "amortisation_duration"    : { "values" : [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "Amortisation duration property is empty"] },
                                   "amortisation_start_price" : { "values" : [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "Amortisation price property is empty"] },
                                   "amortisation_method" : { "values" : [None, ""], "message":
                                       [ "Property value inconsistency", 100,
                                         "No amortisation method"] },
                                   "vat" : { "values" : [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "VAT Amount property is empty"] },
                                   "section_value" : { "values" : [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "The corresponding item does not belong to an organisation at this date"] },
                                   "disposal_price" : { "values": [None], "message":
                                       [ "Property value inconsistency", 100, 
                                         "Disposal price property is empty" ] },
                                   "price_currency" : { "values" : [None], "message":
                                       [ "Property value inconsistency", 100,
                                         "The organisation which owns the item at this date has no amortisation currency"] 
                               } } ) )  


      for (account, text) in ( (self.getInputAccount()         , "Input Account"),
                               (self.getOutputAccount()        , "Output Account"),
                               (self.getImmobilisationAccount(), "Immobilisation Account"),
                               (self.getAmortisationAccount()  , "Amortisation Account"),
                               (self.getDepreciationAccount()  , "Deprecisation Account"),
                               (self.getVatAccount()           , "VAT Account") ):
        if account is None or account is "":
          errors += [(relative_url, "Property value inconsistency", 100, text + ' property is empty')]
                
      section = self.getSectionValue()
      if section is not None:
        financial_date = section.getFinancialYearStopDate()
        if financial_date is None:
          errors += [(relative_url, "Property value inconsistency", 100,
                             "The organisation which owns the item at this date has no financial year end date")]
      
      
      # Checks specific to each amortisation method
      if self.getAmortisationMethod():
        specific_parameter_list = self.getAmortisationMethodParameter("specific_parameter_list")["specific_parameter_list"]
        for parameter in specific_parameter_list:
          errors.extend( checkValue( { parameter : { "values" : [None], 'message':
                                        ["Property value inconsistency", 100,
                                        "%s property is empty" % parameter ] } } ) )

    if errors:
      LOG("errors :", 0, repr(errors))
    return errors
      
      
  security.declareProtected(Permissions.View, 'getSectionValue')
  def getSectionValue(self):
    """
    Returns the organisation which owns the item on which the
    immobilisation movement applies, at the time of the immobilisation
    movement
    See Item.getSectionValue for more details
    """
    item = self.getParent()
    date = self.getStopDate()
    if item is None or date is None:
      return None  
    return item.getSectionValue(at_date = date)
  
  
  security.declareProtected(Permissions.View, 'getSectionTitle')
  def getSectionTitle(self):
    """
    Returns the name of the organisation which owns the
    item on which the immobilisation movement applies, at the
    time of the immobilisation movement
    """
    section = self.getSectionValue()
    if section is None:
      return None
    return section.getTitle()
  
  
  security.declareProtected(Permissions.View, 'getPriceCurrency')
  def getPriceCurrency(self):
    """
    Returns the used currency id for this particular immobilisation movement
    """
    section = self.getSectionValue()
    if section is not None:
      return section.getSocialCapitalCurrencyId()
    return None
  
   
  security.declareProtected(Permissions.View, 'checkImmobilisationConsistency')
  def checkImmobilisationConsistency(self, *args, **kw):
    """
    Checks the consistency about immobilisation values
    """
    return self._checkConsistency(*args, **kw)


  security.declareProtected(Permissions.View, 'getAmortisationMethodParameter')
  def getAmortisationMethodParameter(self, parameter_list):
    """
    Returns a dictionary containing the value of each parameter
    whose name is given in parameter_list.
    The value is get from the amortisation method parameter folder
    (e.g. portal_skins/erp5_immobilisation/eu/linear)
    This folder has specifical parameters needed for calculation
    """
    if type(parameter_list) == type(""):
      parameter_list = [parameter_list]
    parameter_dict = {}
    for parameter in parameter_list:
      parameter_dict[parameter] = None
    amortisation_method = self.getAmortisationMethod()
    parameter_object = self.restrictedTraverse("erp5_accounting_" + amortisation_method)
    if parameter_object is not None:
      for parameter in parameter_list:
        parameter_dict[parameter] = getattr(parameter_object, parameter, None)
    return parameter_dict

  security.declareProtected(Permissions.View, 'isUsingAmortisationMethod')
  def isUsingAmortisationMethod(self, method):
    """
    Return true if this item is using the given method
    """
    if self.getAmortisationMethod() == method:
      return 1
    return 0

  security.declareProtected(Permissions.View, 'isUsingEuLinearAmortisationMethod')
  def isUsingEuLinearAmortisationMethod(self):
    """
    Return true if this item is using this method
    """
    return self.isUsingAmortisationMethod('eu/linear')

  security.declareProtected(Permissions.View, 'isUsingFrDegressiveAmortisationMethod')
  def isUsingFrDegressiveAmortisationMethod(self):
    """
    Return true if this item is using this method
    """
    return self.isUsingAmortisationMethod('fr/degressive')

  security.declareProtected(Permissions.View, 'isUsingFrActualUseAmortisationMethod')
  def isUsingFrActualUseAmortisationMethod(self):
    """
    Return true if this item is using this method
    """
    return self.isUsingAmortisationMethod('fr/actual_use')
