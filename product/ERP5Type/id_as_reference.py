# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#                    Julien Muchembled <jm@nexedi.com>
#               2015 wenjie Zheng <wenjie.zheng@tiolive.com>
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
from Acquisition import aq_base
from Products.CMFActivity.Errors import ActivityPendingError
from Products.ERP5Type import Permissions, PropertySheet
from zLOG import LOG, WARNING

def IdAsReferenceMixin(extra_string, string_type="suffix"):

  extra_string_index = -len(extra_string)

  class IdAsReferenceMixin(object):
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)
    def cb_isMoveable(self):
      return self.cb_userHasCopyOrMovePermission()
    security.declareProtected(Permissions.AccessContentsInformation,
                              'getIdAsReferenceSuffix')
    @staticmethod
    def getIdAsReferenceSuffix():
      return extra_string

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getReference')
    def getReference(self, *args):
      id = self.id
      if string_type == "suffix":
        if id[extra_string_index:] == extra_string:
          return id[:extra_string_index]
        try:
          return self._baseGetReference(*args)
        except AttributeError:
          return getattr(aq_base(self), 'default_reference', (args or [None])[0])
      elif string_type == "prefix":
        if id[:extra_string_index] == extra_string:
          return id[extra_string_index:]
        try:
          return self._baseGetReference(*args)
        except AttributeError:
          return getattr(aq_base(self), 'default_reference', (args or [None])[0])

    def _setReference(self, value):
      parent = self.getParentValue()
      self.__dict__.pop('default_reference', None)
      if string_type == "prefix":
        new_id = extra_string + value
      elif string_type == "suffix":
        new_id = value + extra_string
      if parent.has_key(new_id):
        LOG("IdAsReferenceMixin", WARNING, "Skipping adding of %r in %r"
            " property sheet, due to ID conflict" % (new_id, parent.getId()))
      else:
        self.setId(new_id)
        self.default_reference = value

    security.declareProtected(Permissions.ModifyPortalContent, 'setReference')
    setReference = _setReference

  return IdAsReferenceMixin
