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

from Products.ERP5.interfaces.production_movement import IProductionMovement
from Products.ERP5.interfaces.arrow_base import IArrowBase

class IMovement(IProductionMovement, IArrowBase):
  """Movement interface specification

  A movement represents an amount of resources which
  is moved along an Arrow (source and destination)
  from a source A to a destination B.
  """
  def isMovement():
    """
    Returns True if this movement should be indexed in the
    stock table of the catalog, False else.
    """

  def isAccountable():
    """
    Returns True if this movement impacts the stock levels of source and
    destination.
    """

  def isMovingItem(item):
    """
    Returns True if this movement physically move the item from a tracking
    point of view.
    """

# For backward compatibility only
from Products.ERP5.interfaces.accounting_movement import IAccountingMovement
from Products.ERP5.interfaces.asset_movement import IAssetMovement
