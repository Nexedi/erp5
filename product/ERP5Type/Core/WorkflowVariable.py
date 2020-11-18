# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Romain Courteaud <romain@nexedi.com>
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
from Products.ERP5Type import Permissions
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.mixin.guardable import GuardableMixin
from Products.ERP5Type.mixin.expression import ExpressionMixin

class WorkflowVariable(IdAsReferenceMixin("variable_"),
                       XMLObject,
                       GuardableMixin,
                       ExpressionMixin('variable_default_expression')):
    """
    A ERP5 Workflow Variable.
    """
    meta_type = 'ERP5 Variable'
    portal_type = 'Workflow Variable'
    add_permission = Permissions.AddPortalContent

    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    property_sheets = (
      'Base',
      'XMLObject',
      'CategoryCore',
      'DublinCore',
      'Reference',
      'Variable',
      'Guard',
      'WorkflowVariable',
    )
