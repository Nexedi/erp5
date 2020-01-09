##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
from AccessControl.PermissionRole import PermissionRole

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5.Document.Movement import Movement

class Container(Movement, XMLObject):
    """
      Container is equivalent to a movement with qty 1.0 and resource =
      to the kind of packaging Container may point to item (ex.
      Container serial No or Parcel Serial No if tracing required)
      Container may eventually usa optional property sheet to store
      parcel No information (we use Item property sheet for that). Some
      acquisition may be required...

      A Container which does not point to an Item can act itself as an Item
      for traceability.

      Container Line / Container Cell is used to store quantities (never
      accounted)
      Container Line / Countainer Cell may point to Item
    """

    meta_type = 'ERP5 Container'
    portal_type = 'Container'

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

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

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getQuantity')
    def getQuantity(self, default=1.0):
      """
        Returns 1 because only one container is shipped
      """
      return 1.0

    security.declareProtected(Permissions.AccessContentsInformation,
                              'isAccountable')
    def isAccountable(self):
      """
        Returns 1 if this needs to be accounted
        Only account movements which are not associated to a delivery
        Whenever delivery is there, delivery has priority
      """
      # Always accountable - to account the containers which we use
      return 1

    security.declareProtected( Permissions.ModifyPortalContent,
                              'hasCellContent' )
    def hasCellContent(self, base_id='movement'):
      """
          This method can be overriden
      """
      return 0

    security.declareProtected(Permissions.AccessContentsInformation, 'isDivergent')
    def isDivergent(self):
      """Return True if this movement diverges from the its simulation.
      Containers are never divergent.
      """
      return False

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainerText')
    def getContainerText(self):
      """
        Creates a unique string which allows to compare/hash two containers
      """
      result = ""
      container_line_list = list(self.objectValues())
      container_line_list.sort(key=lambda x: x.getResource())
      for container_line in container_line_list:
        if container_line.hasCellContent():
          container_cell_list = list(container_line.objectValues())
          container_cell_list.sort(key=lambda x: x.getVariationText())
          for container_cell in container_cell_list:
            result += "%s %s %s\n" % (container_cell.getResource(),
                                      container_cell.getQuantity(),
                                      '|'.join(container_cell.getVariationText().split('\n')))
        else:
          result += "%s %s\n" % (container_line.getResource(), container_line.getQuantity())
      container_list = list(self.objectValues(spec = self.meta_type))
      container_list.sort(key=lambda x: x.getContainerText())
      more_result = ""
      for container in container_list:
        more_result += container.getContainerText()
      result = result + '\n'.join(map(lambda x: " %s" % x, more_result.split('\n')))
      return result

    # Used for optimization - requires reindexing using container_uid
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainerUid')
    def getContainerUid(self):
      return self.getUid()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainerValue')
    def getContainerValue(self):
      return self

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainer')
    def getContainer(self):
      return self.getRelativeUrl()

    # Quantity methods
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainedTotalQuantity')
    def getContainedTotalQuantity(self, recursive = 0):
      """
        The sum of quantities of contained lines
      """
      result = 0.0
      for o in self.contentValues(filter =
                    {'portal_type': self.getPortalContainerLineTypeList()}):
        result += o.getTotalQuantity()
      if recursive:
        for o in self.contentValues(filter =
                    {'portal_type': self.getPortalContainerTypeList()}):
          result += o.getContainedTotalQuantity()
      return result

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getContainedTotalPrice')
    def getContainedTotalPrice(self, recursive = 0):
      """
        The sum of price of contained lines
      """
      result = 0.0
      for o in self.contentValues(filter =
                    {'portal_type': self.getPortalContainerLineTypeList()}):
        result += o.getTotalPrice()
      if recursive:
        for o in self.contentValues(filter =
                    {'portal_type': self.getPortalContainerTypeList()}):
          result += o.getContainedTotalPrice()
      return result

    # Item Access
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getTrackedItemUidList')
    def getTrackedItemUidList(self):
      """
        Return a list of uid for related items.
        If this container is related to no item, it is treated as an Item
      """
      ### XXX We should filter by portal type here
      item_uid_list = self.getAggregateUidList()
      if len(item_uid_list): return item_uid_list
      return (self.getUid(),)

    # XXX: Dirty but required for erp5_banking_core
    getBaobabSourceUid = lambda x: x.getSourceUid()
    getBaobabSourceUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationUid = lambda x: x.getDestinationUid()
    getBaobabDestinationUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceSectionUid = lambda x: x.getSourceSectionUid()
    getBaobabSourceSectionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationSectionUid = lambda x: x.getDestinationSectionUid()
    getBaobabDestinationSectionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourcePaymentUid = lambda x: x.getSourcePaymentUid()
    getBaobabSourcePaymentUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationPaymentUid = lambda x: x.getDestinationPaymentUid()
    getBaobabDestinationPaymentUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceFunctionUid = lambda x: x.getSourceFunctionUid()
    getBaobabSourceFunctionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationFunctionUid = lambda x: x.getDestinationFunctionUid()
    getBaobabDestinationFunctionUid__roles__ = PermissionRole(Permissions.View)

    getBaobabSourceProjectUid = lambda x: x.getSourceProjectUid()
    getBaobabSourceProjectUid__roles__ = PermissionRole(Permissions.View)

    getBaobabDestinationProjectUid = lambda x: x.getDestinationProjectUid()
    getBaobabDestinationProjectUid__roles__ = PermissionRole(Permissions.View)
