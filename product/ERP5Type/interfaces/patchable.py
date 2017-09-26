# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SA and Contributors. All Rights Reserved.
#                    Ayush Tiwari <ayush.tiwari@nexedi.com>
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

class IPatchable(Interface):
  """
    An interface for objects that can be patched. This is useful
    to raise an exception for some objects that are not meant to be
    supported by BusinessTemplatePatchItem
  """

  def patch(patch, path=None, unified_diff_selection=None):
    """
      Apply a PortalPatch or PortalPatchOperation to an object

      unified_diff_selection -- a selection of lines in the unified diff
                                that will be applied

      path -- optional path in case one wants to patch only some properties
    """
