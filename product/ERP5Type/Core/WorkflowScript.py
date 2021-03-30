# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
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
from AccessControl.class_init import InitializeClass
from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type import Permissions
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin

SCRIPT_PREFIX = 'script_'

class WorkflowScript(IdAsReferenceMixin(SCRIPT_PREFIX),
                     PythonScript):
  """
  Script within a Workflow taking state_change as a parameter.

  Difference with Python Script: Reference added and ID automatically set to
  reference prefixed with SCRIPT_PREFIX (Workflow Sctrips are at the same
  level as Transitions, States, Variables and Worklists).
  """
  meta_type = 'ERP5 Workflow Script'
  portal_type = 'Workflow Script'
  add_permission = Permissions.AddPortalContent

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = (
    'Base',
    'XMLObject',
    'CategoryCore',
    'DublinCore',
    'PythonScript',
    'Reference',
  )

InitializeClass(WorkflowScript)
