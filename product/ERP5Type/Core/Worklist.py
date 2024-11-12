# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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

import re

from AccessControl import ClassSecurityInfo
from Products.CMFCore.Expression import Expression
from Products.ERP5Type import Permissions
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.mixin.guardable import GuardableMixin
from Products.ERP5Type.Core.Predicate import Predicate
from Products.ERP5Type.Utils import deprecated

tales_re = re.compile(r'(\w+:)?(.*)')

class Worklist(IdAsReferenceMixin("worklist_"), GuardableMixin, Predicate):
    """
    ERP5 Worklist.

    Variables:
      - Workflow Variable where for_catalog == 1.
      - State Variable.
      - SECURITY_PARAMETER_ID (local_roles).
    """
    meta_type = 'ERP5 Worklist'
    portal_type = 'Worklist'
    add_permission = Permissions.AddPortalContent

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    property_sheets = (
      'Base',
      'XMLObject',
      'CategoryCore',
      'DublinCore',
      'Reference',
      'Comment',
      'Guard',
      'ActionInformation',
      'Predicate',
    )

    @security.protected(Permissions.AccessContentsInformation)
    def getIdentityCriterionDict(self):
      """
      XXX: Move this to Predicate class?
      """
      try:
        return dict(self._identity_criterion)
      except AttributeError:
        return {}

    # XXX(PERF): hack to see Category Tool responsability in new workflow slowness
    @security.protected(Permissions.AccessContentsInformation)
    def getActionType(self):
      prefix_length = len('action_type/')
      action_type_list = [path[prefix_length:] for path in self.getCategoryList()
                          if path.startswith('action_type/')]
      try:
        return action_type_list[0]
      except IndexError:
        return None

from Products.ERP5Type import WITH_LEGACY_WORKFLOW
if WITH_LEGACY_WORKFLOW:
  Worklist.security.declareProtected(Permissions.AccessContentsInformation,
                                     'getVarMatchKeys')
  Worklist.getVarMatchkeys = \
    deprecated('getVarMatchKeys() deprecated; use getCriterionPropertyList()')\
              (lambda self: self.getCriterionPropertyList())

  Worklist.security.declareProtected(Permissions.AccessContentsInformation,
                                     'getVarMatch')
  Worklist.getVarMatch = \
    deprecated('getVarMatch() deprecated; use getIdentityCriterionDict()')\
              (lambda self, id: tuple(self._identity_criterion.get(id, ())))

from Products.ERP5Type.Globals import InitializeClass
InitializeClass(Worklist)
