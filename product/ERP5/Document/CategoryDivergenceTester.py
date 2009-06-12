#############################################################################
#
# Copyright (c) 2006-2008 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

import zope.interface
from AccessControl import ClassSecurityInfo

from Products.ERP5Type.DivergenceMessage import DivergenceMessage
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5.Document.PropertyDivergenceTester import \
                                               PropertyDivergenceTester

class CategoryDivergenceTester(PropertyDivergenceTester):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for some specific categories.
  """
  meta_type = 'ERP5 Category Divergence Tester'
  portal_type = 'Category Divergence Tester'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  zope.interface.implements( interfaces.IDivergenceTester, )

  # Declarative properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.DivergenceTester
  )


  def explain(self, simulation_movement):
    """
    This method returns a list of messages that contains
    the divergence of the Delivery Line.
    """
    divergence_message_list = []
    tested_property = self.getTestedPropertyList()

    delivery_mvt = simulation_movement.getDeliveryValue()
    for tested_property_id, tested_property_title in \
                                  self._splitStringList(tested_property):
      message = None
      delivery_mvt_category_list = \
          delivery_mvt.getPropertyList(tested_property_id)
      simulation_category_list = \
          simulation_movement.getPropertyList(tested_property_id)

      # XXX Don't we need to check the order too ?
      delivery_mvt_category_list.sort()
      simulation_category_list.sort()

      if delivery_mvt_category_list != simulation_category_list:
        delivery_mvt_category_title_list = []
        for mvt_category in delivery_mvt_category_list:
          category_value = delivery_mvt.resolveCategory(mvt_category)
          if category_value is not None:
            if category_value.getPortalType() == 'Category':
              delivery_mvt_category_title_list.append(category_value.getTranslatedTitle())
            else:
              delivery_mvt_category_title_list.append(category_value.getTitle())

        simulation_category_title_list = []
        for mvt_category in simulation_category_list:
          category_value = delivery_mvt.resolveCategory(mvt_category)
          if category_value is not None:
            if category_value.getPortalType() == 'Category':
              simulation_category_title_list.append(category_value.getTranslatedTitle())
            else:
              simulation_category_title_list.append(category_value.getTitle())

        message = DivergenceMessage(
                     divergence_scope='category',
                     object_relative_url=delivery_mvt.getRelativeUrl(),
                     simulation_movement=simulation_movement,
                     decision_value=delivery_mvt_category_list,
                     prevision_value=simulation_category_list,
                     decision_title=', '.join(delivery_mvt_category_title_list),
                     prevision_title=', '.join(simulation_category_title_list),
                     tested_property=tested_property_id,
                     message=tested_property_title,
        )

        divergence_message_list.append(message)

    return divergence_message_list
