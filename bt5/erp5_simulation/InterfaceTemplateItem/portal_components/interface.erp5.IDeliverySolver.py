# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from zope.interface import Interface, Attribute

class IDeliverySolver(Interface):
  """Delivery Solver interface specification

  This interface must be implemented by all delivery solvers which are
  used to solve quantity related divergences in ERP5 simulation.
  Delivery solvers are usually built by SolverTool and invoked by target
  solvers.

  Delivery solvers are initialised with a list of simulation movements
  and provide methods (setQuantity, getQuantity) to manipulate the total
  quantity of movements.
  """

  def __init__(movement_list):
    """
    Initialises the delivery solver.

    movement_list -- a list of simulation movement on which delivery
    solver operates
    """

  title = Attribute('The title of the delivery solver.')

  def getTotalQuantity():
    """
    Return the total quantity by summing the quantity of each simulation
    movement.
    """

  def setTotalQuantity(quantity):
    """
    Sets the total quantity of simulation movements by increasing or
    reducing the quantity and ratio of each simulation movement. This
    method implements the solver specific algorith (ex. FIFO, LIFO,
    average, least cost)

    NOTE: is this the right place to update delivery ratio ?
    """
