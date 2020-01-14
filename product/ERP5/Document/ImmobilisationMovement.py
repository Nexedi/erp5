##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Guillaume Michon <guillaume.michon@e-asc.com>
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

from Products.ERP5Type import Permissions, PropertySheet

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Movement import Movement

from string import capitalize

UNIMMOBILISING_METHOD = "unimmobilise"
NO_CHANGE_METHOD = "no_change"
AMORTISATION_METHOD_PREFIX = "portal_skins/erp5_accounting_"
IMMOBILISATION_NEEDED_PROPERTY_LIST = [
              ("date",   "stop_date",           "Date"),
              ("method", "amortisation_method", "Amortisation Method"),
             ]
IMMOBILISATION_UNCONTINUOUS_NEEDED_PROPERTY_LIST = [
              ("main_price",     "amortisation_start_price", "Immobilised Price"),
              ("disposal_price", "disposal_price",           "Disposal Price"),
              ("duration",       "amortisation_duration",    "Amortisation Duration"),
              ("vat",            "immobilisation_vat",       "VAT"),
              ("input_account",          "input_account",    "Input Account"),
              ("output_account",         "output_account",   "Output Account"),
              ("immobilisation_account", "immobilisation_account", "Immobilisation Account"),
              ("amortisation_account",   "amortisation_account",   "Amortisation Account"),
              ("depreciation_account",   "depreciation_account",   "Depreciation Account"),
              ("vat_account",            "immobilisation_vat_account", "VAT Account"),
              ("extra_cost_account",     "extra_cost_account",     "Extra Costs Account"),
             ]
IMMOBILISATION_FACULTATIVE_PROPERTY_LIST = [
              ("monthly_amortisation_account", "monthly_amortisation_account", "Monthly Amortisation Account"),
              ("extra_cost_price",    "extra_cost_price", "Extra Costs Price"),
              ("durability", "durability", "Durability"),
             ]



class ImmobilisationMovement(Movement, XMLObject):
  """
    An ImmobilisationMovement is a generic object representing an immobilisation
    and optional amortisation decision for any item. It holds information about
    an accounting immobilisation (in order to amortise an object)
  """
  meta_type = 'ERP5 Immobilisation Movement'
  portal_type = 'Immobilisation Movement'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

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


  def _checkImmobilisationConsistency(self, fixit=0, mapped_value_property_list=(), to_translate=1):
    """
    If to_translate is set, the method may return a dictionary {'msg':'...', 'mapping':{} }
    """
    from erp5.component.interface.IImmobilisationItem import IImmobilisationItem

    relative_url = self.getRelativeUrl()
    def checkValuesAreNotNone(property_list):
      errors = []
      for key, value, name in property_list:
        value = 'get' + ''.join(map(capitalize, value.split('_')))
        value = getattr(self, value, None)
        if value is not None:
          value = value()
        if key == 'method' and not value:
          value = NO_CHANGE_METHOD
        errors.extend(checkValue(variable=value,
                                 forbidden_value_list=[None],
                                 error_message=["Property value inconsistency", 0, "%s property is empty" % name]
                                )
                     )
      return errors

    def checkValue(variable,
                   forbidden_value_list=None,
                   authorized_value_list=None,
                   error_message=["Error Type", 0, "Error message"]):
      if forbidden_value_list is not None:
        if type(forbidden_value_list) != type([]):
          forbidden_value_list = [forbidden_value_list]
        if variable in forbidden_value_list:
          return [ tuple([relative_url] + error_message) ]
      if authorized_value_list is not None:
        if type(authorized_value_list) != type([]):
          authorized_value_list = [authorized_value_list]
        if variable not in authorized_value_list:
          return [ tuple([relative_url] + error_message) ]
      return []

    errors = []
    # Check absolutely needed values
    method = self.getAmortisationMethod() or NO_CHANGE_METHOD
    errors.extend(checkValuesAreNotNone(IMMOBILISATION_NEEDED_PROPERTY_LIST))
    property_list = self.getNeededSpecificParameterListForItem(None)
    errors.extend(checkValuesAreNotNone(property_list))

    # Check if the date of this movement is unique
    date_error = 0
    for item in self.getAggregateValueList():
      if IImmobilisationItem.providedBy(item):
        same_date_list = item.getUnfilteredImmobilisationMovementValueList(
                       from_date = self.getStopDate(),
                       to_date = self.getStopDate(),
                       include_to_date = 1)
        error_found = 0
        for other_movement in same_date_list:
          if other_movement != self and other_movement.getRootDeliveryValue().getImmobilisationState() == 'valid':
            error_found = 1
            date_error = 1
        if error_found:
          if to_translate:
            msg = {'msg':"An other movement already exists at the same date for item ${item}",
                   'mapping': {'item':item.getRelativeUrl()}
                  }
          else:
            msg = "An other movement alreay exists at the same date for item %s" % item.getRelativeUrl()
          errors.append([self.getRelativeUrl(),
                        "Property value inconsistency", 0,
                        msg
                       ])

    # Return to avoid infinite loops in case of date errors
    if date_error:
      return errors

    item_list = self.getAggregateValueList()

    if len(item_list) == 0:
      # No item aggregated, so the movement is considered as valid
      #errors.append([self.getRelativeUrl(),
      #               "Property value inconsistency", 0,
      #               "No item aggregated"])
      return errors

    # Check values needed if the amortisation method is not continuous
    check_uncontinuous = 0
    if self.getStopDate() is not None:
      if method not in [None, "", NO_CHANGE_METHOD, UNIMMOBILISING_METHOD]:
        get_amo_method_parameter = self.getAmortisationMethodParameter("continuous")
        continuous = get_amo_method_parameter["continuous"]
        if not continuous:
          check_uncontinuous = 1
        # We need to check if the preceding movement is in the same period, and valid
        # This check must be done on each item
        else:
          # We need to check if the preceding movement is in the same period, and if it is valid
          # This check must be done on each item
          def checkPreviousMovementForItem(movement, item):
            previous_movement = item.getLastImmobilisationMovementValue(at_date=movement.getStopDate())
            if previous_movement is None:
              return 0
            if previous_movement.getImmobilisationState() == 'valid':
              if previous_movement.getAmortisationMethod() not in ("", NO_CHANGE_METHOD):
                return 1
              return checkPreviousMovementForItem(previous_movement, item)
            return checkPreviousMovementForItem(previous_movement, item)
          for item in self.getAggregateValueList():
            if IImmobilisationItem.providedBy(item):
              if not checkPreviousMovementForItem(self,item):
                check_uncontinuous = 1
              else:
                # The last movement which is not a NO_CHANGE is valid
                # Now check if the method is the same, then if the period is really continuing from previous movement
                previous_movement = item.getLastImmobilisationMovementValue(at_date=self.getStopDate())
                previous_movement_method = previous_movement.getActualAmortisationMethodForItem(item)
                if previous_movement_method != method:
                  check_uncontinuous = 1
                  # If the previous method is the same, it means the previous movement did
                  # not stop the immobilisation, because stopping is a particular method
    if check_uncontinuous:
      errors.extend(checkValuesAreNotNone(IMMOBILISATION_UNCONTINUOUS_NEEDED_PROPERTY_LIST))
      property_list = self.getUncontinuousNeededSpecificParameterListForItem(None)
      errors.extend(checkValuesAreNotNone(property_list))

    # Do not check facultative properties (of course)

    # Check owner change for each aggregated item
    # XXX Checking it here would be inadequate, since the owner can change by multiple ways :
    # adding a new movement for this item, changing it, modifying related organisation, etc...
    # It is not compatible with a validity workflow approach since the causalities are too numerous
    # The actual check is done in ImmobilisableItem.getImmobilisationPeriodList()
    return errors


  security.declareProtected(Permissions.AccessContentsInformation,
                            'checkImmobilisationConsistency')
  def checkImmobilisationConsistency(self, *args, **kw):
    """
    Checks the consistency about immobilisation values
    """
    return self._checkImmobilisationConsistency(*args, **kw)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAmortisationMethodParameter')
  def getAmortisationMethodParameter(self, parameter_list, **kw):
    """
    Returns a dictionary containing the value of each parameter
    whose name is given in parameter_list.
    Warning : can only be used on a movement whose amortisation_method
    is not in (None, NO_CHANGE_METHOD)
    """
    if self.getAmortisationMethod() in (None, "", NO_CHANGE_METHOD):
      return None
    return self.getAmortisationMethodParameterForItem(None, parameter_list, **kw)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getAmortisationMethodParameterForItem')
  def getAmortisationMethodParameterForItem(self, item, parameter_list, split_char=None, split_qty=3, **kw):
    """
    Returns a dictionary containing the value of each parameter
    whose name is given in parameter_list.
    The value is get from the amortisation method parameter folder
    (e.g. portal_skins/erp5_accounting_eu/linear)
    This folder has specifical parameters needed for calculation
    'item' can be None to access parameters on a movement whose method is not NO_CHANGE_METHOD nor None
    """
    parameter_dict = {}
    if type(parameter_list) == type(""):
      parameter_list = [parameter_list]
    for parameter in parameter_list:
      parameter_dict[parameter] = None
    amortisation_method = self.getActualAmortisationMethodForItem(item, **kw)
    if amortisation_method not in (None, NO_CHANGE_METHOD, UNIMMOBILISING_METHOD, ""):
      parameter_object = self.getPortalObject().unrestrictedTraverse(AMORTISATION_METHOD_PREFIX + amortisation_method)
      if parameter_object is not None:
        for parameter in parameter_list:
          parameter_dict[parameter] = getattr(parameter_object, parameter, None)

    if (split_char is not None) and (split_qty != 0):
      new_parameter_dict = {}
      for key in parameter_dict.keys():
        param_list = parameter_dict[key]
        if param_list is None:
          new_parameter_dict[key] = []
        if type(param_list) != type([]) and type(param_list) != type(()):
          param_list = [param_list]
        new_param_list = []
        for param in param_list:
          if param is not None:
            if param.find(split_char) != -1:
              param = param.split(split_char)
              param = [x.strip() for x in param]
            if type(param) != type([]) and type(param) != type(()):
              param = [param]
            if len(param) > split_qty:
              param = param[:split_qty]
            while len(param) < split_qty:
              param.append(param[-1])
            new_param_list.append(param)
        new_parameter_dict[key] = new_param_list
      parameter_dict = new_parameter_dict
    return parameter_dict


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getActualAmortisationMethodForItem')
  def getActualAmortisationMethodForItem(self, item, **kw):
    """
    Returns the actual amortisation method by getting the previous
    movement method if the current one is NO_CHANGE_METHOD
    """
    method = self.getAmortisationMethod()
    if method not in (None, "", NO_CHANGE_METHOD):
      return method

    stop_date = self.getStopDate()
    if stop_date is None or item is None:
      return None
    previous_movement_list = item.getPastImmobilisationMovementValueList(at_date=stop_date, **kw)
    if previous_movement_list is None:
      return None
    for i in range(len(previous_movement_list)-1, -1, -1):
      movement = previous_movement_list[i]
      if movement.getAmortisationMethod() not in (None, "", NO_CHANGE_METHOD):
        return movement.getAmortisationMethod()
    return None


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getNeededSpecificParameterListForItem')
  def getNeededSpecificParameterListForItem(self, item, **kw):
    """
    Returns the list of specific parameters which are
    needed for the amortisation calculation for the given item
    """
    return self.getAmortisationMethodParameterForItem(item=item,
                                                      parameter_list="needed_specific_parameter_list",
                                                      split_char = '|',
                                                      split_qty = 3,
                                                      **kw)["needed_specific_parameter_list"]


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getUncontinuousNeededSpecificParameterListForItem')
  def getUncontinuousNeededSpecificParameterListForItem(self, item, **kw):
    """
    Returns the list of specific parameters which are
    needed for the amortisation calculation for the given item
    when the amortisation is not continuing the previous period
    """
    return self.getAmortisationMethodParameterForItem(item=item,
                                                      parameter_list="uncontinuous_needed_specific_parameter_list",
                                                      split_char = '|',
                                                      split_qty = 3,
                                                      **kw)["uncontinuous_needed_specific_parameter_list"]


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getFacultativeSpecificParameterListForItem')
  def getFacultativeSpecificParameterListForItem(self, item, **kw):
    """
    Returns the list of specific parameters which are
    facultative for the amortisation calculation for the given item
    """
    return self.getAmortisationMethodParameterForItem(item=item,
                                                      parameter_list="facultative_specific_parameter_list",
                                                      split_char = '|',
                                                      split_qty = 3,
                                                      **kw)["facultative_specific_parameter_list"]


  security.declareProtected(Permissions.AccessContentsInformation,
                            'isUsingAmortisationMethod')
  def isUsingAmortisationMethod(self, method):
    """
    Return true if this item is using the given method
    """
    return self.getAmortisationMethod() == method

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getImmobilisationState')
  def getImmobilisationState(self):
    """
    Return root delivery immobilisation state, or None if this is not chained
    to an immobilisation workflow
    """
    root_delivery = self.getRootDeliveryValue()
    if getattr(root_delivery, 'getImmobilisationState', None) is not None:
      return root_delivery.getImmobilisationState()


