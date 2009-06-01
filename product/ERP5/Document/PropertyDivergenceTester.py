##############################################################################
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

from AccessControl import ClassSecurityInfo

from Products.ERP5Type.XMLObject import XMLObject

from Products.ERP5Type.DivergenceMessage import DivergenceMessage
from Products.ERP5Type import Permissions, PropertySheet, interfaces

class PropertyDivergenceTester(XMLObject):
  """
  The purpose of this divergence tester is to check the
  consistency between delivery movement and simulation movement
  for some specific properties.
  """
  meta_type = 'ERP5 Property Divergence Tester'
  portal_type = 'Property Divergence Tester'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative interfaces
  __implements__ = ( interfaces.IDivergenceTester, )

  # Declarative properties
  property_sheets = (   PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.DivergenceTester
                     )

  def test(self, simulation_movement):
    """
    This is the fast method to test, return True or False.
    It depends if the simulation_movement is divergent or not.
    """
    return len(self.explain(simulation_movement)) != 0

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
      delivery_mvt_property = delivery_mvt.getProperty(tested_property_id)
      simulation_mvt_property = simulation_movement.getProperty(tested_property_id)
      if delivery_mvt_property != simulation_mvt_property:
        message = DivergenceMessage(
                   divergence_scope='property',
                   object_relative_url=delivery_mvt.getRelativeUrl(),
                   simulation_movement=simulation_movement,
                   decision_value=delivery_mvt_property ,
                   prevision_value=simulation_mvt_property,
                   tested_property=tested_property_id,
                   message=tested_property_title,
        )
        divergence_message_list.append(message)

    return divergence_message_list

  def _splitStringList(self, string_list):
     """
     Convert a list of string with a pipe (ex: ["azert | qsdfg", ] )
     to a list of tuple (ex: [("azert", "qsdfg"), ] )
     """
     return [tuple([x.strip() for x in x.split('|')]) for x in string_list]
