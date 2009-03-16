##############################################################################
#
# Copyright (c) 2007, Nexedi SA and Contributors. All Rights Reserved.
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
    override of the function getCell to ba able to search a cell on the
    inheritance model
    '''
    cell = XMLMatrix.getCell(self, *kw, **kwd)
    # if cell not found, look on the inherited models
    if cell is None:
      for specialised_model in self.getSpecialiseValueList():
        cell = specialised_model.getCell(*kw, **kwd)
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
        reference_dict[obj.getProperty('reference',
                                       obj.getId())] = obj.getId()
    return reference_dict

  security.declareProtected(Permissions.AccessContentsInformation,
      'getInheritanceModelTreeAsList')
  def getInheritanceModelTreeAsList(self):
    '''Return a list of models. It uses Breadth First Search. 
    '''
    model = self
    already_add_models = [model]
    model_list = [model]
    final_list = [model]
    while len(model_list) != 0:
      model = model_list.pop(0)
      specialise_list = model.getSpecialiseValueList()
      while len(specialise_list) !=0:
        child = specialise_list.pop(0)
        # this should avoid circular dependencies
        if child not in already_add_models:
          already_add_models.append(child)
          model_list.append(child)
          final_list.append(child)
    return final_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getInheritanceEffectiveModelTreeAsList')
  def getInheritanceEffectiveModelTreeAsList(self, paysheet):
    '''Return a list of effective models. It uses Breadth First Search. 
    '''
    model = self.getEffectiveModel(paysheet)
    already_add_models = [model]
    model_list = [model]
    final_list = [model]
    while len(model_list) != 0:
      model = model_list.pop(0)
      specialise_list = model.getSpecialiseValueList()
      while len(specialise_list) !=0:
        child = specialise_list.pop(0)
        child = child.getEffectiveModel(paysheet)
        # this should avoid circular dependencies
        if child not in already_add_models:
          already_add_models.append(child)
          model_list.append(child)
          final_list.append(child)
    return final_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getInheritanceEffectiveModelReferenceDict')
  def getInheritanceEffectiveModelReferenceDict(self, paysheet,
      portal_type_list, property_list=()):
    '''Returns a dict with the model url as key and a list of reference as
    value. Normaly, a Reference appear only one time in the final output.
    It uses Breadth First Search. 
    If property_list is not empty, documents for which all properties in
    property_list are false will be skipped.
    '''
    model_list = self.getInheritanceEffectiveModelTreeAsList(paysheet,
                                                    portal_type_list,
                                                    property_list)
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
      'getInheritanceModelReferenceDict')
  def getInheritanceModelReferenceDict(self, portal_type_list,
      property_list=()):
    '''Returns a dict with the model url as key and a list of reference as
    value. Normaly, a Reference appear only one time in the final output.
    It uses Breadth First Search. 
    If property_list is not empty, documents for which all properties in
    property_list are false will be skipped.
    '''
    model_list = self.getInheritanceModelTreeAsList()
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
  def getEffectiveModel(self, context):
    '''
    return the more appropriate model using effective_date, expiration_date 
    and version number
    '''
    reference = self.getReference()
    if not reference:
      return self

    effective_model_list = []
    start_date = context.getStartDate()
    stop_date = context.getStopDate()
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
    model_list = self.getInheritanceEffectiveModelTreeAsList(paysheet)
    for specialised_model in model_list:
      v = specialised_model.getProperty(property_name)
      if v:
        return v
