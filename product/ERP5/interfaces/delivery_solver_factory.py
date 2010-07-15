# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from zope.interface import Interface

class IDeliverySolverFactory(Interface):
  """Delivery Solver Factory interface specification

  IDeliverySolverFactory provides methods to create delivery
  solver instances and retrieve metadata related to delivery
  solvers.
  """

  def newDeliverySolver(portal_type, movement_list):
    """
    Return a new instance of delivery solver of the given
    portal_type and with appropriate parameters.

    portal_type -- the portal_type of the delivery solver.

    movement_list -- movements to initialise the instance with
    """

  def getDeliverySolverTranslatedItemList(portal_type_list=None):
    """
    Return the list of translated titles and portal types of available
    delivery solvers. Use this method to fill listfields in user interface
    forms.

    portal_type_list -- optional parameter to filter results only
                       with provided portal types
    """
