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
"""
"""

from zope.interface import Interface

class IMovementCollection(Interface):
  """Movement Collection interface specification

  Documents which implement IMovementCollection provide
  a list access to all movements which they contain.
  IMovementCollection is the abstraction of all classes
  which contain movements. This includes Deliveries,
  Applied Rules, etc.

  TODO:
    - extract from Delivery.py class all methods
      which are common to ApplieRule.py
    - should IMovementCollection be designed
      in such way that DeliveryLine is also
      an IMovementCollection ?
  """
  def getMovementList(portal_type=None, **kw):
    """
    Returns all movements of the collection
    """
