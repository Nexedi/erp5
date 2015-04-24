# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#          Julien Muchembled <jm@nexedi.com>,
#          Boris Kocherov <bk@raskon.ru>
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

from Products.CMFActivity.Errors import ActivityPendingError
from Products.ERP5Type.CopySupport import CopyContainer
from zLOG import LOG, WARNING

def GenerateIdFromReferenceMixin(prefix):
  prefix_ = prefix + "_"
  class GenerateIdAsReferenceMixin(object):

    def __init__(self, ob_id):
      if not ob_id.startswith(prefix_):
        ob_id = prefix_ + ob_id
      self.id = ob_id

    def cb_isMoveable(self):
      return self.cb_userHasCopyOrMovePermission()

    def __migrate(self):
      self._setIdByRefernce()

    def _genIdByRefernce(self, old_id=None, reference=None):
      if not old_id:
        old_id = self.id
      if not reference:
        reference = getattr(self, 'reference', None)
      if reference:
        base_id = new_id = "_".join((prefix, reference))
      else:
        base_id = new_id = prefix
      if old_id != new_id and not old_id.startswith(new_id + "_"):
        parent = self.getParentValue()
        if not reference:
          new_id = base_id + "_" + old_id
        int_ob_id = 0
        while 0 <= int_ob_id <= 100:
          if new_id not in parent:
            break
          int_ob_id += 1
          new_id = base_id + "_%d" % (int_ob_id,)
        if new_id in parent:
          int_ob_id = parent.generateNewId()
          new_id = base_id + "_%d" % (int_ob_id,)
        if new_id in parent:
          LOG("GenerateIdFromReferenceMixin", WARNING, "Skipping migration id of %r in %r"
              " %s, due to ID conflict" % (new_id, parent.getId(), parent.getPortalType()))
        else:
          return new_id
      return None

    def _setIdByRefernce(self, old_id=None, reference=None):
      new_id = self._genIdByRefernce(old_id, reference)
      if new_id:
        try:
          self.setId(new_id)
        except ActivityPendingError:
          parent = self.getParentValue()
          LOG("GenerateIdFromReferenceMixin", WARNING, "Skipping update id of %r in %r"
              " %s, due to pending activities" % (old_id, parent.getId(), parent.getPortalType()))

    def getId(self, default=None):
      """
       It's only for migration.
       it' can be removed if all instances updating
      """
      ob_id = self._baseGetId(default)
      migration = getattr(self, '_v_idmigration', False)
      if not migration and not ob_id.startswith(prefix_):
        self._v_idmigration = True
        new_id = self._genIdByRefernce(old_id=ob_id)
        try:
          self.setId(new_id)
        except ActivityPendingError:
          parent = self.getParentValue()
          LOG("GenerateIdFromReferenceMixin", WARNING, "Skipping migration of %r in %r"
              " %s, due to pending activities" % (old_id, parent.getId(), parent.getPortalType()))
        return new_id
      return ob_id

    def _setId(self, ob_id):
      """
       update id for moved and copied objects
      """
      if not ob_id.startswith(prefix_):
        ob_id = prefix_ + ob_id
      return CopyContainer._setId(self, ob_id)

    def _setReference(self, value):
      """
       update id if reference change
      """
      self._setIdByRefernce(reference=value)
      self._baseSetReference(value)

  return GenerateIdAsReferenceMixin
