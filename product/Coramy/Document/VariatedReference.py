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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.Utils import cartesianProduct

from Products.ERP5.ERP5Globals import resource_type_list

from zLOG import LOG

class VariatedReference(XMLObject, XMLMatrix):
    """
        VariatedReference defines a reference which
        can take multiples values depending of the variations of a resource

        Maybe defined by mapped values inside the resource
    """

    meta_type = 'CORAMY Variated Reference'
    portal_type = 'Variated Reference'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.VariatedReference
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Local property sheet
    _properties = (
      { 'id'          : 'variation_base_category',
        'storage_id'  : 'variation_base_category_list', # Coramy Compatibility
        'description' : "",
        'type'        : 'tokens',
        'acquisition_portal_type'   : resource_type_list,
        'acquisition_copy_value'    : 0,
        'acquisition_mask_value'    : 0,
        'acquisition_sync_value'    : 0,
        'acquisition_accessor_id'   : 'getVariationBaseCategoryList',
        'acquisition_depends'       : None,
        'mode'        : 'w' },
    )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
A VariatedReference."""
         , 'icon'           : 'variated_reference_icon.gif'
         , 'product'        : 'Coramy'
         , 'factory'        : 'addVariatedReference'
         , 'immediate_view' : 'variated_reference_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'transformed_resource_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'variated_reference_print'
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
          , 'action'        : 'translation_template_view'
          , 'permissions'   : (
              Permissions.TranslateContent, )
          }
        )
      }

    ### Variation matrix definition
    #
    security.declareProtected(Permissions.ModifyPortalContent, '_setReferenceVariationBaseCategoryList')
    def _setReferenceVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which the reference
        variates on
      """
      # XXX - may be incompatible with future versions of ERP5
      self.reference_variation_base_category_list = value
      kwd = {}
      kwd['base_id'] = self.getReferenceType()
      kw = []
      resource = self.aq_parent
      line_id = 'coloris'
      column_id = 'taille'
      line = [[None]]
      column = [[None]]
      
      for v in value:
        if v == line_id:
          line = [resource.getVariationRangeCategoryItemList(base_category_list = line_id, base=0)]
        elif v == column_id:
          column = [resource.getVariationRangeCategoryItemList(base_category_list = column_id, base=0)]
        else:
          kw += [resource.getVariationRangeCategoryItemList(base_category_list = v, base=0)]
      kw = line + column + kw
      self.setCellRange(*kw, **kwd)
      # Empty cells if no variation
      if line == [[None]] and column == [[None]]:
        self.delCells(base_id=self.getReferenceType())
      # And fix it in case the cells are not renamed (XXX this will be removed in the future)
      # self._checkConsistency(fixit=1)

    security.declareProtected(Permissions.ModifyPortalContent, 'setReferenceVariationBaseCategoryList')
    def setReferenceVariationBaseCategoryList(self, value):
      """
        Defines the possible base categories which Quantity value (Q)
        variate on and reindex the object
      """
      self._setReferenceVariationBaseCategoryList(value)
      self.reindexObject()

    # Methods for matrix UI widgets
    security.declareProtected(Permissions.AccessContentsInformation, 'getLineItemList')
    def getLineItemList(self):
      base_category = 'coloris'
      if base_category in self.getReferenceVariationBaseCategoryList():
        clist = self.aq_parent.getVariationRangeCategoryItemList(base_category, base=0)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getColumnItemList')
    def getColumnItemList(self):
      base_category = 'taille'
      if base_category in self.getReferenceVariationBaseCategoryList():
        clist = self.aq_parent.getCategoryMembershipList(base_category, base=1)
      else:
        clist = [None]
      result = []
      for c in clist:
        result += [(c,c)]
      return result

    security.declareProtected(Permissions.AccessContentsInformation, 'getTabItemList')
    def getTabItemList(self):
      resource = self.aq_parent
      line_id = 'coloris'
      column_id = 'taille'
      base_category_list = resource.getVariationBaseCategoryList()
      base_category = []
      for c in base_category_list:
        if not c in (line_id, column_id):
          if c in self.getReferenceVariationBaseCategoryList():
            base_category += [resource.getVariationRangeCategoryItemList(c, base=0)]
      if len(base_category) > 0:
        clist = cartesianProduct(base_category)
        result = []
        for c in clist:
          result += [(c,c)]
      else:
        result = [(None,'')]
      return result
      
    security.declareProtected( Permissions.ModifyPortalContent, 'newCell' )
    def newCell(self, *kw, **kwd):
      result = XMLMatrix.newCell(self, *kw, **kwd)
      result._setPredicateOperator("SUPERSET_OF")
      membership_list = []
      for c in kw:
        if c is not None:
          membership_list += [c]
      result._setPredicateValueList(membership_list)
      base_id = kwd.get('base_id', 'cell')
      result._setDomainBaseCategoryList(self.getReferenceVariationBaseCategoryList())
      return result

    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Set Mapped Value",id=id)
      return self.get(id)


from SetMappedValue import SetMappedValue

class SetMappedValuePatch(SetMappedValue):

    def getEan13Code(self):
      """
        returns ean13 code for Coramy
      """
      if hasattr(self, 'code_ean13'):
        return self.code_ean13
      return self._baseGetEan13Code()
        
SetMappedValue.getEan13Code = SetMappedValuePatch.getEan13Code    
