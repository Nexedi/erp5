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

from zope.interface import Interface

class IMovementGroup(Interface):
  """Movement Group interface specification

  The purpose of MovementGroup is to define how movements are grouped, [YES] XXX
  and how values are updated from simulation movements. [NO] XXX
  """
  def test(document, property_dict, **kw):
    """Returns a tuple of 2 values.
    First one is True if document contains identical values than some
    contained property_dict.
    Second one is a modified version of property_dict.

    TODO:
      - take into account the possibility to use Divergence Testers
        to build movement groups
      - how does separate method relate to matching provided by
        Divergence Testers
      - consider an interface for property groups. Is it the same or
        different ?
    """

  def separate(movement_list):
    """
    Returns a list of lists of movements, which are grouped by some of their
    properties.
    """

  def isBranch():
    """Returns True if self can be taken as branch point by the builder.
    """
