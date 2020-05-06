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
from Products.ERP5Type.XMLMatrix import XMLMatrix

class PaySheetModel(TradeCondition, XMLMatrix):
  """A PaySheetModel defines calculation rules for paysheets.

    PaySheetModel are used to define calculating rules specific to a
    date, a convention, a group of employees ...
    The class inherit from Delivery, because it contains movements.
  """

  meta_type = 'ERP5 Pay Sheet Model'
  portal_type = 'Pay Sheet Model'
  model_line_portal_type_list = 'Pay Sheet Model Line'

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
                    , PropertySheet.Reference
                    , PropertySheet.Version
                    , PropertySheet.Arrow
                    , PropertySheet.TradeCondition
                    , PropertySheet.Order
                    , PropertySheet.PaySheetModel
                    , PropertySheet.MappedValue
                    , PropertySheet.Amount
                    , PropertySheet.DefaultAnnotationLine
                    )

  security.declareProtected( Permissions.AccessContentsInformation, 'getCell')
  def getCell(self, *args, **kw):
    '''Overload the function getCell to be able to search a cell on the
    inheritance model tree if the cell is not found on current one.
    '''
    paysheet = kw.get('paysheet')
    if paysheet is None:
      paysheet = self.getPortalObject().newContent(
        temp_object=True,
        portal_type='Pay Sheet Transaction',
        id='',
        specialise_value=self)
    model_list = self.findEffectiveSpecialiseValueList(paysheet)
    for specialised_model in model_list:
      cell = XMLMatrix.getCell(specialised_model, *args, **kw)
      if cell is not None:
        return cell

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getReferenceDict')
  def getReferenceDict(self, portal_type_list, property_list=None):
    """Return a dict containing all id's of the objects contained in
    this model and corresponding to the given portal_type. The key of the dict
    are the reference (or id if no reference)
    """
    if property_list is None:
      property_list=[]
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
                            'getInheritanceReferenceDict')
  def getInheritanceReferenceDict(self, context, portal_type_list,
                                  property_list=None):
    '''Returns a dict with the model url as key and a list of reference as
    value. A Reference can appear only one time in the final output.
    If property_list is not empty, documents which don't have any of theses
    properties will be skipped.
    '''
    reference_list = []
    model_reference_dict = {}
    for model in self.findEffectiveSpecialiseValueList(context):
      id_list = []
      model_reference_list = model.getReferenceDict(
                            portal_type_list, property_list=property_list)
      for reference in model_reference_list.keys():
        if reference not in reference_list:
          reference_list.append(reference)
          id_list.append(model_reference_list[reference])
      if len(id_list) != 0:
        model_reference_dict[model.getRelativeUrl()]=id_list
    return model_reference_dict

  security.declareProtected(Permissions.AccessContentsInformation,
      'getModelInheritanceEffectiveProperty')
  def getModelInheritanceEffectiveProperty(self, paysheet, property_name):
    """Get a property from an effective model
    """
    model_list = self.findEffectiveSpecialiseValueList(paysheet)
    for specialised_model in model_list:
      v = specialised_model.getProperty(property_name)
      if v:
        return v
