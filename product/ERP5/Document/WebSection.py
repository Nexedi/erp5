# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2008 Nexedi SA and Contributors. All Rights Reserved.
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

from Persistence import Persistent

# Global keys used for URL generation
WEB_SECTION_PORTAL_TYPE_TUPLE = ('Web Section', 'Web Site')

# WebSection Document class has been migrated to ZODB Components and this module
# has been kept here because of WebSectionTraversalHook which is not an ERP5
# object
kept_for_backward_compatibility_only = True
class WebSectionTraversalHook(Persistent):
  """Traversal hook to change the skin selection for this websection.
  """
  def __call__(self, container, request):
    if not request.get('ignore_layout', None):
      # If a skin selection is defined in this web section, change the skin now.
      skin_selection_name = container.getSkinSelectionName()
      if skin_selection_name and \
         ((request.get('portal_skin', None) is None) or \
          container.getPortalType() not in WEB_SECTION_PORTAL_TYPE_TUPLE):
        container.getPortalObject().changeSkin(skin_selection_name)
