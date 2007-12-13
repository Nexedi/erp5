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

    def getReferenceList(self, portal_type_list):
      '''
        return all objects reference of the model wich portal_type is in the
        portal_type_list
      '''
      reference_list = []
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
          if reference is not None:
            reference_list.append(reference)
          else:
            LOG('PaySheetModel getReferenceList', 0, '%s reference '
                'property is empty' % object.getTitle() or
                object.getRelativeUrl())

      return reference_list


    def getInheritanceModelReferenceDict(self, model_reference_dict,
        model_list, portal_type_list, reference_list):
      '''
        return a dict with the model url as key and a list of reference 
        as value. Normaly, a Reference appear only one time in the final output
      '''
      # handle the case where just one model is given
      if type(model_list) != type([]):
        model_list = [model_list,]

      for model in model_list:
        model_reference_list=model.getReferenceList(portal_type_list)
        unique_list = []

        for reference in model_reference_list:
          if reference not in reference_list:
            reference_list.append(reference)
            unique_list.append(reference)

        model_reference_dict[model.getRelativeUrl()]=unique_list

        new_model_list = model.getSpecialiseValueList()
        model_reference_dict = self.getInheritanceModelReferenceDict(\
            model_reference_dict=model_reference_dict,
            model_list=new_model_list,
            portal_type_list=portal_type_list,
            reference_list=reference_list,)
      return model_reference_dict

