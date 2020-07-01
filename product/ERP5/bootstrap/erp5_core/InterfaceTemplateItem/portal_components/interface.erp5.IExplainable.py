# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
"""
erp5.component.interface.IExplainable
"""

from zope.interface import Interface

class IExplainable(Interface):
  """Explainable interface specification

  IExplainable defines the notion of Explanation in  ERP5 simulation.
  Explanation was initially introduced  to provide better indexing of
  movements in stock and movement tables. Thanks to explanation, it is
  possible to relate unbuilt simulation movements (ex. planned sourcing)
  to a root explanation (ex. a production order). This is used
  in the inventory browser user interface to provide an explanation
  for each simulated movement which is not yet built. Explanation of
  simulation movements are sometimes used to calculate efficiently aggregated
  quantities and prices of all simulation movements which are part of the
  same simulation tree.

  IExplainable is implemented by all simulation movements.

  Explanations in ERP5 are also used in another meaning, as a way to calculate
  efficiently aggregated quantities and prices of movements in a Delivery.
  The current interface is unrelated to this meaning.
  """
  def getExplanationValueList():
    """Returns the list of deliveries of parent simulation
    movements. The first item in the list is the immediate
    explanation value. The last item in the list is the root
    explanation.
    """

  def getRootExplanationValue():
    """Returns the delivery of the root simulation
    movement.
    """

  def getImmediateExplanationValue():
    """Returns the delivery of the first parent simulation
    which has a delivery.
    """

  def getExplanationLineValueList():
    """Returns the list of delivery lines of parent simulation
    movements. The first item in the list is the immediate
    explanation value. The last item in the list is the root
    explanation.
    """

  def getRootExplanationLineValue():
    """Returns the delivery line of the root simulation
    movement.
    """

  def getImmediateExplanationLineValue():
    """Returns the delivery line of the first parent simulation
    which has a delivery.
    """

  # Compatibility API
  def getExplanationUid():
    """Returns the UID of the root explanation
    """