# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

from Products.ERP5.interfaces.amount import IAmount

class IProductionMovement(IAmount):
  """Production Movement private interface specification

  Production movements have a source or a destination equal
  to None. They are used to represent productions or
  consumptions or resources according to the following
  specification:

    (A -> B)
      production_quantity means nothing
      consumption_quantity means nothing

    (A -> Nothing)
    if quantity > 0
      consumption_quantity = quantity
      production_quantity = 0

    if quantity < 0
      consumption_quantity = 0
      production_quantity = - quantity

    (Nothing -> B)
    if quantity > 0
      consumption_quantity = 0
      production_quantity = quantity

    if quantity < 0
      consumption_quantity = - quantity
      production_quantity = 0
  """
  def getConsumptionQuantity():
    """
    Returns the consumed quantity during production
    """

  def getProductionQuantity():
    """
    Returns the produced quantity during production
    """
