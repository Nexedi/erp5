# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                            Łukasz Nowak <luke@nexedi.com>
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
erp5.component.interface.IDivergenceMessage
"""
from zope.interface import Interface

class IDivergenceMessage(Interface):
  def getMovementGroup():
    """Returns movement group of a builder which was
    responsible for generating tested_property.

    XXX-JPS - REFACTOR NEEDED

    Issue 1:
      This is wrong since multiple builders can be used to
      build a single Delivery. Moreover, what is used for grouping
      and what is used to set properties can be different.

    Issue 2:
      This class is related to ERP5 and not to ERP5Type
    """

  def getCollectOrderGroup():
    """Wraps and canonises result of Movement Groups' getCollectOrderGroup getter"""
