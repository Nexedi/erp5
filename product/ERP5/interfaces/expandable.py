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
"""
Products.ERP5.interfaces.expandable
"""

from zope.interface import Interface

class IExpandable(Interface):
  """
    An Expandable class provides methods which trigger
    the generation of the root applied rule of a simulation tree
    and its expansion. Classes which implement IExpandable include
    Deliveries (whenever can be the cause of an Applied Rule),
    Items (whenever they are the cause of a movement sequence)
    such as Subscription Items or Immobilisation Items, Movements
    (which have been previously built).
  """

  def expand(applied_rule_id=None, activate_kw=None, **kw):
    """
      Expand the current Expandable class into the simulation.
      If no applied_rule_id is provided, try first to find 
      appropriate applied rule if any to start expansion process.

      applied_rule_id -- a hint parameter (optional), which can
                         be provided to reindex the whole 
                         simulation tree from the root applied rule

      activate_kw -- (TO BE EXPLAINED BY KAZ)
    """
