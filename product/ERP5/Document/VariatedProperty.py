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
from Products.ERP5.Variated import Variated
from Products.ERP5Type.Utils import cartesianProduct
from Products.ERP5.ERP5Globals import resource_type_list

from zLOG import LOG

class VariatedProperty(XMLObject, XMLMatrix, Variated):
    """
        VariatedReference defines a reference which
        can take multiples values depending of the variations of a resource

        Maybe defined by mapped values inside the resource
    """

    meta_type = 'ERP5 Variated Property'
    portal_type = 'Variated Property'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.VariatedProperty
                      , PropertySheet.VariationRange
                      , PropertySheet.MappedValue
                      )

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Local property sheet
    _properties = (
      { 'id'          : 'variation_base_category',
        'storage_id'  : 'variation_base_category_list',
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
A VariatedProperty."""
         , 'icon'           : 'variated_reference_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addVariatedProperty'
         , 'immediate_view' : 'variated_property_view'
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'variated_property_view'
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


    security.declareProtected( Permissions.ModifyPortalContent, 'newCellContent' )
    def newCellContent(self, id):
      """
          This method can be overriden
      """
      self.invokeFactory(type_name="Set Mapped Value",id=id)
      return self.get(id)

    security.declarePrivate('_checkConsistency')
    def _checkConsistency(self, fixit=0):
      """
        Check the constitency of transformation elements
      """
      error_list = XMLMatrix._checkConsistency(self, fixit=fixit)

      # First quantity
      # We build an attribute equality and look at all cells
      constraint = Constraint.AttributeEquality(
        domain_base_category_list = ('coloris', 'taille',),
        predicate_operator = 'SUPERSET_OF',
        mapped_value_property_list = ['code_ean13'] )
      for k in self.getCellKeys(base_id = 'cell'):
        LOG("VariatedProperty: ",0,"_check: k: %s" % str(k))
        kw={}
        kw['base_id'] = 'cell'
        c = self.getCell(*k, **kw)
        if c is not None:
          LOG("VariatedProperty: ",0,"_check: c: %s" % str(c))
          predicate_value = []
          for p in k:
            if p is not None: predicate_value += [p]
          constraint.edit(predicate_value_list = predicate_value)
          if fixit:
            error_list += constraint.fixConsistency(c)
          else:
            error_list += constraint.checkConsistency(c)

      return error_list

