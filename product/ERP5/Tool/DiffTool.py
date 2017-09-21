# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2017 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

class DiffTool(BaseTool):
  """
  A portal tool that provides all kinds of utilities to
  compare objetcs.
  """
  id = 'portal_diff'
  title = 'Diff Tool'
  meta_type = 'ERP5 Diff Tool'
  portal_type = 'Portal Diff Tool'
  allowed_types = ()

  # Declarative Security
  security = ClassSecurityInfo()

  def diffPortalObject(self, old, new, path=None, patch_format="deepdiff"):
    """
      Returns a PortalPatch instance with the appropriate formate
      original -- original object
      new -- new object
      path -- optional path to specify which property to diff
      patch_format -- optional format (rfc6902 or deepdiff)
    """
    pass

InitializeClass(DiffTool)
