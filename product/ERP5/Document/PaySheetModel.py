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
from Products.ERP5Type.XMLMatrix import XMLMatrix
from zLOG import LOG, WARNING, DEBUG

#XXX TODO: review naming of new methods
#XXX WARNING: current API naming may change although model should be stable.

class PaySheetModel(TradeCondition, XMLMatrix):
  """
    PaySheetModel are used to define calculating rules specific to a 
    date, a convention, a enmployees group...
    This permit to applied a whole of calculating rules on a whole of
    pay sheets
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

  security.declareProtected( Permissions.View, 'getCell' )
  def getCell(self, *kw , **kwd):
    '''
    override of the function getCell to ba able to search a cell on the
    inheritance model
    '''
    LOG('getCell ', 0, kw)
    cell = XMLMatrix.getCell(self, *kw, **kwd)

    # if cell not found, look on the inherited models
    if cell is None and self.getSpecialiseValue() is not None:
      cell = self.getSpecialiseValue().getCell(*kw, **kwd)
    return cell


  def getReferenceDict(self, portal_type_list, get_none_reference=0):
    '''
      return all objects reference and id of the model wich portal_type is in the
      portal_type_list
      - parameters :
        o get_none_reference : permit to get a dict with all references
        not defined. This is usefull to get all object on the model paysheet
        inherite from.
    '''
    reference_dict={}

    object_list = self.contentValues(portal_type=portal_type_list,
        sort_on='id')

    for object in object_list:
      reference_method = getattr(object, 'getReference', None)
      if reference_method is None:
        LOG('PaySheetModel getReferenceList', 0, '%s have not '
            'getReference method' % object.getTitle() or
            object.getRelativeUrl())
      else:
        reference = reference_method()
        if reference is not None and not get_none_reference:
          reference_dict[reference]=object.getId()
        elif reference is None and get_none_reference:
          reference_dict[object.getId()]=object.getId()

    return reference_dict

  def getInheritanceModelReferenceDict(self, portal_type_list):
    '''
      return a dict with the model url as key and a list of reference 
      as value. Normaly, a Reference appear only one time in the final output
      It's use a Breadth First Search
    '''
    model = self
    already_add_models = [model]
    model_list = [model]
    model_reference_dict = {}
    reference_list = []
    id_list = []

    while len(model_list) != 0:
      model = model_list.pop(0)
      id_list = []
      specialise_list = model.getSpecialiseValueList()

      model_reference_list=model.getReferenceDict(portal_type_list)
      for reference in model_reference_list.keys():
        if reference not in reference_list:
          reference_list.append(reference)
          id_list.append(model_reference_list[reference])

      if id_list != []:
        model_reference_dict[model.getRelativeUrl()]=id_list

      while len(specialise_list) !=0:
        child = specialise_list.pop(0)

        # this should avoid circular dependencies
        if child not in already_add_models:
          already_add_models.append(child)
          model_list.append(child)

    return model_reference_dict
