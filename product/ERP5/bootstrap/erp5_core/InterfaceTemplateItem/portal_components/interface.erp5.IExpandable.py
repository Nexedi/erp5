# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
erp5.component.interface.IExpandable
"""
from zope.interface import Interface

class IExpandable(Interface):
  """Common Interface for Applied Rules and Simulation Movements
  """
  def expand(expand_policy=None, activate_kw=None):
    """
    Update subobjects of this document and expand them

    expand_policy -- string defining whether a node in the simulation tree
                     should be expand immediately or in a separate activity,
                     or None to use the preferred policy

    activate_kw -- activity parameters, required to control
                   activity constraints

    Available policies: immediate, deferred, vertical_time_bound
    """
