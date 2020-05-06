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

from collections import defaultdict
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet

from erp5.component.document.Delivery import Delivery

class PackingList(Delivery):
  """
      Delivery/PackingList is the main document
      which allows to control causality in the simulation

      PackingList have 2 different states:

      - solved: this happens when quantities and target
        quantities are the same

      - diverged: this happens when quantities and target
        quantities are different

      Resolution of diverged PackingList is achieved by workflow
      methods. Such workflow methods eventually change
      movements in the simulation. Typical solution include:

      - reduce quantity

      - split delivery

      - postpone delivery

      solutions are implemented as solvers
  """
  # CMF Type Definition
  meta_type = 'ERP5 Packing List'
  portal_type = 'Packing List'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Comment
                    , PropertySheet.Movement
                    , PropertySheet.TradeCondition
                    , PropertySheet.Order
                    )

  #######################################################
  # Container computation
  security.declareProtected(Permissions.AccessContentsInformation,
                            'isPacked')
  def isPacked(self):
    """
        Returns true if all quantities for all variations of resources are in
        containers.

        FIXME: this method does not support packing list with 2 movements of
        same resource.
    """
    # build a mapping of
    # (resource, variation_text) -> quantity
    container_dict = defaultdict(int)
    for container in self.contentValues(
        portal_type=self.getPortalContainerTypeList()):
      for container_line in container.contentValues(
        portal_type=self.getPortalContainerLineTypeList(),):
        if container_line.hasCellContent(base_id='movement'):
          for container_cell in container_line.contentValues(
              portal_type=self.getPortalContainerLineTypeList(),):
            key = (container_cell.getResource(),
              container_cell.getVariationText())
            container_dict[key] += container_cell.getQuantity()
        else:
          key = (container_line.getResource(),
            container_line.getVariationText())
          container_dict[key] += container_line.getQuantity()

    if not container_dict:
      return False

    # Check that all movements are packed.
    for movement in self.getMovementList():
      key = (movement.getResource(),
             movement.getVariationText())
      if container_dict.get(key) != movement.getQuantity():
        return False
    return True