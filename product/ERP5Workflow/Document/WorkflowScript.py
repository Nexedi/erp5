##############################################################################
#
# Copyright (c) 2015 Nexedi SARL and Contributors. All Rights Reserved.
#                    Wenjie Zheng <wenjie.zheng@tiolive.com>
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
from App.special_dtml import HTMLFile
from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from Products.ERP5Type.id_as_reference import IdAsReferenceMixin

SCRIPT_PREFIX = 'script_'

class WorkflowScript(PythonScript, IdAsReferenceMixin("script_", "prefix")):
  meta_type = 'ERP5 Python Script'
  portal_type = 'Workflow Script'
  add_permission = Permissions.AddPortalContent
  default_reference = ''
  _params = ''

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Reference
                      , PropertySheet.PythonScript
                      )

  security.declarePublic("execute")
  execute = PythonScript.__call__

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getScriptParameterList')
  def getScriptParameterList(self):
    ''' returns script's parameter for use by Pylint '''
    return self._params

InitializeClass(WorkflowScript)
