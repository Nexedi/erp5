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
from AccessControl.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from App.special_dtml import HTMLFile
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Ticket import Ticket
from Products.ERP5.Document.PythonScript import PythonScript
from Products.ERP5Type.ConsistencyMessage import ConsistencyMessage
from zLOG import LOG, ERROR, DEBUG, WARNING

class WorkflowScript(PythonScript):
  meta_type = 'ERP5 Python Script'
  portal_type = 'Workflow Script'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.WorkflowScript
                      )

  def __init__(self, *args, **kw):
    PythonScript.__init__(self, *args, **kw)

  def __call__(self):
    r_url = self.REQUEST.get('URL')
    return self.REQUEST.RESPONSE.redirect(r_url+'/view')

  execute = PythonScript.__call__

  # We need to take __setstate__ from PythonScript in order to
  # generate _v_ft attributes which is necessary to run the script
  __setstate__ = PythonScript.__setstate__
InitializeClass(WorkflowScript)
