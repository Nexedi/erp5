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

from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo

from Products.CMFCore.WorkflowCore import WorkflowAction
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLMatrix import XMLMatrix
from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5.Document.Movement import Movement

from zLOG import LOG

class Container(Movement, XMLObject):
    """
      Container is equivalent to a movement with qty 1.0 and resource = to the kind of packaging
      Container may point to item (ex. Container serial No or Parcel Serial No if tracing required)
      Container may eventually usa optional property sheet to store parcel No information (we use
      Item property sheet for that). Some acquisition may be required...

      Container Line / Container Cell is used to store quantities (never accounted)
      Container Line / Countainer Cell may point to Item
    """

    meta_type = 'ERP5 Container'
    portal_type = 'Container'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Declarative interfaces
    __implements__ = ( Interface.Variated, )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.Amount
                      , PropertySheet.Task
                      , PropertySheet.Arrow
                      , PropertySheet.Movement
                      , PropertySheet.Price
                      , PropertySheet.VariationRange
                      , PropertySheet.ItemAggregation
                      , PropertySheet.Item
                      , PropertySheet.Container
                      , PropertySheet.SortIndex
                      )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
Une ligne tarifaire."""
         , 'icon'           : 'order_line_icon.gif'
         , 'product'        : 'ERP5'
         , 'factory'        : 'addContainer'
         , 'immediate_view' : 'container_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Container',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'container_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'list'
          , 'name'          : 'Object Contents'
          , 'category'      : 'object_action'
          , 'action'        : 'folder_contents'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : 'order_line_print'
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

    # Force in _edit to modify variation_base_category_list first
    security.declarePrivate( '_edit' )
    def _edit(self, REQUEST=None, force_update = 0, **kw):
      # No Variations at this level
      Movement._edit(self, REQUEST=REQUEST, force_update = force_update, **kw)
      # Fire activity to update quantities in delivery lines
      self.getDeliveryValue().activate().updateTargetQuantityFromContainerQuantity()

    security.declareProtected(Permissions.AccessContentsInformation, 'getQuantity')
    def getQuantity(self):
      """
        Returns 1 because only one container is shipped
      """
      return 1.0

    security.declareProtected(Permissions.AccessContentsInformation, 'getTargetQuantity')
    def getTargetQuantity(self):
      """
        Returns 1 because only one container is shipped
      """
      return 1.0

    security.declareProtected(Permissions.AccessContentsInformation, 'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      # Always accountable - to account the containers which we use
      return 1

    security.declareProtected( Permissions.ModifyPortalContent, 'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """
          This method can be overriden
      """
      return 0

    security.declareProtected(Permissions.View, 'isDivergent')
    def isDivergent(self):
      """
        Returns 1 if the target is not met according to the current information
        After and edit, the isOutOfTarget will be checked. If it is 1,
        a message is emitted

        emit targetUnreachable !
      """
      return 0

    def getContainerText(self):
      """
        Creates a unique string which allows to compare/hash two containers
      """
      result = ""
      container_line_list = list(self.objectValues())
      container_line_list.sort(lambda x, y: cmp(x.getResource(), y.getResource()))
      for container_line in container_line_list:
        if container_line.hasCellContent():
          container_cell_list = list(container_line.objectValues())
          container_cell_list.sort(lambda x, y: cmp(x.getVariationText(), y.getVariationText()))
          for container_cell in container_cell_list:
            result += "%s %s %s\n" % (container_cell.getResource(), container_cell.getTargetQuantity(), '|'.join(container_cell.getVariationText().split('\n')))
        else:
          result += "%s %s\n" % (container_line.getResource(), container_line.getTargetQuantity())
      container_list = list(self.objectValues(spec = self.meta_type))
      container_list.sort(lambda x, y: cmp(x.getContainerText(), y.getContainerText()))
      more_result = ""
      for container in container_list:
        more_result += container.getContainerText()
      result = result + '\n'.join(map(lambda x: " %s" % x, more_result.split('\n')))
      return result
