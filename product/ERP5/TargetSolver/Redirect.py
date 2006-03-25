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


from Products.ERP5.Tool.SimulationTool import registerTargetSolver
from TargetSolver import TargetSolver

class Redirect(TargetSolver):
  """
    Redirects all simulation movements to new target
  """

  def solve(self, movement, new_target):
    """
      Updates all sources and destinations to new values defined 
      in self by mapping 
        source -> target_source
        destination -> target_destination
        source_section -> target_source_section
        destination_section -> target_destination_section
    """
    for p in ('source', 'destination'):
      for q in ('source', 'destination'):
        if movement.getProperty(p) == getattr(self, q):
          self.setProperty(p, getattr(self, 'target_%s' % q))
          break
    for p in ('source_section', 'destination_section'):
      for q in ('source_section', 'destination_section'):
        if movement.getProperty(p) == getattr(self, q):
          self.setProperty(p, getattr(self, 'target_%s' % q))
          break
    delivery_value = movement.getDeliveryValue() # Get delivery movement
    if delivery_value is not None:
      delivery_value = delivery_value.getDeliveryValue() # Get root delivery
      if delivery_value is not None:
        delivery_value.activate(after_method_id = 'propagateResourceToSimulation').updateFromSimulation()

registerTargetSolver(Redirect)
