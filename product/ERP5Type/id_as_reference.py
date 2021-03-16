# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

import transaction
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.CMFActivity.Errors import ActivityPendingError
from zLOG import LOG, WARNING
from Acquisition import aq_base

def IdAsReferenceMixin(affix):
  # Prefix or suffix
  is_suffix = (affix[0] == '_')
  affix_len = len(affix)

  class IdAsReferenceMixin(object):
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    def cb_isMoveable(self):
      return self.cb_userHasCopyOrMovePermission()

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getIdAsReferenceAffix')
    @staticmethod
    def getIdAsReferenceAffix():
      return affix

    # Backward-compatibility: Use getIdAsReferenceAffix instead
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getIdAsReferenceSuffix')
    getIdAsReferenceSuffix = getIdAsReferenceAffix

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getReference')
    def getReference(self, *args):
      id = self.id
      if is_suffix:
        if id[-affix_len:] == affix:
          return id[:-affix_len]
      elif id[:affix_len] == affix: # prefix
        return id[affix_len:]
      try:
        return self._baseGetReference(*args)
      except AttributeError:
        return getattr(aq_base(self), 'default_reference', (args or [None])[0])

    def _setReference(self, value):
      self.__dict__.pop('default_reference', None) # BBB
      self.setId((value + affix) if is_suffix else (affix + value))

    security.declareProtected(Permissions.ModifyPortalContent, 'setReference')
    setReference = _setReference

  return IdAsReferenceMixin
