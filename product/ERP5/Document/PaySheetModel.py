##############################################################################
#
# Copyright (c) 2007-2009, Nexedi SA and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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
from Products.ERP5.Document.TradeCondition import TradeCondition
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5.Document.Delivery import Delivery
from zLOG import LOG

#XXX TODO: review naming of new methods
#XXX WARNING: current API naming may change although model should be stable.

class PaySheetModel(TradeCondition, XMLMatrix, Delivery):
  """A PaySheetModel defines calculation rules for paysheets.

    PaySheetModel are used to define calculating rules specific to a
    date, a convention, a group of employees ...
    The class inherit from Delivery, because it contains movements.
  """

  meta_type = 'ERP5 Pay Sheet Model'
  portal_type = 'Pay Sheet Model'
  model_line_portal_type_list = 'Pay Sheet Model Line'
  isPredicate = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Version
                    , PropertySheet.DublinCore
                    , PropertySheet.Folder
                    , PropertySheet.Comment
                    , PropertySheet.Arrow
                    , PropertySheet.TradeCondition
                    , PropertySheet.Order
                    , PropertySheet.PaySheetModel
                    , PropertySheet.MappedValue
                    , PropertySheet.Amount
                    , PropertySheet.DefaultAnnotationLine
                    )

  security.declareProtected( Permissions.AccessContentsInformation, 'getCell')
  def getCell(self, *kw , **kwd):
    '''
    Overload the function getCell to be able to search a cell on the
    inheritance model tree
    '''
    cell = XMLMatrix.getCell(self, *kw, **kwd)
    # if cell not found, look on the inherited models
    if cell is None:
      if kwd.has_key('paysheet'):
        model_list = self.findEffectiveSpecialiseValueList(\
            start_date=kwd['paysheet'].getStartDate(),
            stop_date=kwd['paysheet'].getStopDate())
      else:
        model_list = self.findSpecialiseValueList(context=self)
      if self in model_list:
        model_list.remove(self)
      for specialised_model in model_list:
        cell = XMLMatrix.getCell(specialised_model, *kw, **kwd)
        if cell is not None:
          return cell
    return cell

  security.declareProtected(Permissions.AccessContentsInformation,
      'getReferenceDict')
  def getReferenceDict(self, portal_type_list, property_list=()):
    '''Return all objects reference and id of the model wich portal_type is in
    the portal_type_list. If type does not have a reference, it's ID is used.
    If property_list is provided, only objects for which at least one of
    properties is true will be added.
    '''
    reference_dict = {}
    object_list = self.contentValues(portal_type=portal_type_list,
        sort_on='id')
    for obj in object_list:
      keep = (len(property_list) == 0)
      for property_ in property_list:
        if obj.hasProperty(property_):
          keep = 1
          break
      if keep:
        reference_dict[obj.getProperty('reference', obj.getId())] = obj.getId()
    return reference_dict

  security.declareProtected(Permissions.AccessContentsInformation,
      'findEffectiveSpecialiseValueList')
  def findEffectiveSpecialiseValueList(self, start_date=None, stop_date=None):
    '''Return a list of effective models
    '''
    model_list = self.findSpecialiseValueList(self)
    if start_date is None and stop_date is None:
      return model_list

    new_list = [model.getEffectiveModel(start_date, stop_date) for model in\
        model_list]
    return new_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getInheritanceReferenceDict')
  def getInheritanceReferenceDict(self, portal_type_list,
      property_list=()):
    '''Returns a dict with the model url as key and a list of reference as
    value. Normaly, a Reference appear only one time in the final output.
    It uses Breadth First Search.
    If property_list is not empty, documents for which all properties in
    property_list are false will be skipped.
    '''
    model_list = self.findSpecialiseValueList(context=self)
    reference_list = []
    model_reference_dict = {}
    for model in model_list:
      id_list = []
      model_reference_list = model.getReferenceDict(
                           portal_type_list, property_list=property_list)
      for reference in model_reference_list.keys():
        if reference not in reference_list:
          reference_list.append(reference)
          id_list.append(model_reference_list[reference])

      if id_list != []:
        model_reference_dict[model.getRelativeUrl()]=id_list

    return model_reference_dict

  security.declareProtected(Permissions.AccessContentsInformation,
      'getEffectiveModel')
  def getEffectiveModel(self, start_date=None, stop_date=None):
    '''return the more appropriate model using effective_date, expiration_date
    and version number
    '''
    reference = self.getReference()
    if not reference:
      return self

    effective_model_list = []
    model_object_list = [result.getObject() for result in \
        self.portal_catalog(portal_type='Pay Sheet Model',
                            reference=reference,)]
                            #sort_on=(('version','descending'),))]
    # XXX currently, version is not catalogued, so sort using python
    def sortByVersion(a, b):
      return cmp(b.getVersion(), a.getVersion())
    model_object_list.sort(sortByVersion)

    for current_model in model_object_list:
      # if there is a model with exact dates, return it
      if start_date == current_model.getEffectiveDate() and \
          stop_date == current_model.getExpirationDate():
        effective_model_list.append(current_model)
    if len(effective_model_list):
      return effective_model_list[0]

    # else, if there is model wich has effective period containing 
    # the start_date and the stop date of the paysheet, return it
    for current_model in model_object_list:
      if start_date >= current_model.getEffectiveDate() and \
          stop_date <= current_model.getExpirationDate():
        effective_model_list.append(current_model)
    if len(effective_model_list):
      return effective_model_list[0]
    # if no effective model are found (ex. because dates are None), return self
    return self

  security.declareProtected(Permissions.AccessContentsInformation,
      'getModelIneritanceEffectiveProperty')
  def getModelIneritanceEffectiveProperty(self, paysheet, property_name):
    """Get a property from an effective model
    """
    v = self.getProperty(property_name)
    if v:
      return v
    model_list = self.findEffectiveSpecialiseValueList(\
        start_date=paysheet.getStartDate(), stop_date=paysheet.getStopDate())
    for specialised_model in model_list:
      v = specialised_model.getProperty(property_name)
      if v:
        return v
