# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets <jp@nexedi.com>
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
from Products.ERP5Type.Core.Folder import Folder
from Products.CMFCore.utils import UniqueObject

class CallableTool(UniqueObject, Folder):
  """
  A tool that can be used to add scripts and other callable methods (including 
  ZSQL templates and HTML templates) to ERP5. It replaces portal_skins.
  """

  id = 'portal_callables'
  meta_type = 'ERP5 Callable Tool'
  portal_type = 'Callable Tool'

  def _setOb(self, object_id, obj):
    """
      Update portal_skins cache with the new files.
    """
    Folder._setOb(self, object_id, obj)
    portal_skins = getattr(self, 'portal_skins', None)
    if portal_skins is None:
      return
    portal_skins = self.getPortalObject().portal_skins
    _updateCacheEntry = getattr(portal_skins.aq_base, '_updateCacheEntry', None)
    if _updateCacheEntry is None:
      return
    _updateCacheEntry(self.id, object_id)