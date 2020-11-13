# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2020 Nexedi SA and Contributors. All Rights Reserved.
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

import Zope2

Zope2_zpublisher_validated_hook_orig = Zope2.zpublisher_validated_hook
def Zope2_zpublisher_validated_hook(request, user):
  # If we are publishing a resource for an authenticated user, forbid shared
  # cached from storing it.
  # Historially, this was (for some reason) implemented in CookieCrumbler,
  # but it does not seem very consistent as it then depends on how the user
  # was authenticated. This is a more neutral implementated located.
  if user.getUserName() != 'Anonymous User':
    request.response.setHeader('Cache-Control', 'private')
  Zope2_zpublisher_validated_hook_orig(request, user)
Zope2.zpublisher_validated_hook = Zope2_zpublisher_validated_hook
