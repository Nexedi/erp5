##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Ivan Tyagov <ivan@nexedi.com>
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

import os
import tempfile
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from AccessControl.SecurityManagement import setSecurityManager
from Products.ERP5 import _dtmldir
from Products.ERP5Type.Utils import _setSuperSecurityManager
from App.config import getConfiguration
import tarfile

_MARKER = []

class IntrospectionTool(BaseTool):
  """
    This tool provides both local and remote introspection.
  """

  id = 'portal_introspections'
  title = 'Introspection Tool'
  meta_type = 'ERP5 Introspection Tool'
  portal_type = 'Introspection Tool'
  allowed_content_types = ('Anonymized Introspection Report', 'User Introspection Report',) # XXX User Portal Type please

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainIntrospectionTool', _dtmldir )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getFilteredActionDict')
  def getFilteredActionDict(self, user_name=_MARKER):
    """
      Returns menu items for a given user
    """
    portal = self.getPortalObject()
    is_portal_manager = getToolByName(portal, 
      'portal_membership').checkPermission(Permissions.ManagePortal, self)
    downgrade_authenticated_user = user_name is not _MARKER and is_portal_manager
    if downgrade_authenticated_user:
      # downgrade to desired user
      original_security_manager = _setSuperSecurityManager(self, user_name)

    # call the method implementing it
    erp5_menu_dict = getToolByName(portal, 'portal_actions').listFilteredActionsFor(portal)

    if downgrade_authenticated_user:
      # restore original Security Manager
      setSecurityManager(original_security_manager)

    # Unlazyfy URLs and other lazy values so that it can be marshalled
    result = {}
    for key, action_list in erp5_menu_dict.items():
      result[key] = map(lambda action:dict(action), action_list)

    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                           'getModuleItemList')
  def getModuleItemList(self, user_name=_MARKER):
    """
      Returns menu items for a given user
    """
    portal = self.getPortalObject()
    is_portal_manager = getToolByName(portal, 
      'portal_membership').checkPermission(Permissions.ManagePortal, self)
    downgrade_authenticated_user = user_name is not _MARKER and is_portal_manager
    if downgrade_authenticated_user:
      # downgrade to desired user
      original_security_manager = _setSuperSecurityManager(self, user_name)

    # call the method implementing it
    erp5_module_list = portal.ERP5Site_getModuleItemList()

    if downgrade_authenticated_user:
      # restore original Security Manager
      setSecurityManager(original_security_manager)

    return erp5_module_list

  def _getLocalFile(self, REQUEST, RESPONSE, file_path, 
                         tmp_file_path='/tmp/', compressed=1):
    """
      It should return the local file compacted as tar.gz.
    """
    if file_path.startswith('/'):
      raise IOError, 'The file path must be relative not absolute'
    instance_home = getConfiguration().instancehome
    file_path = os.path.join(instance_home, file_path)
    if not os.path.exists(file_path):
      raise IOError, 'The file: %s does not exist.' % file_path

    if compressed:
      tmp_file_path = tempfile.mktemp(dir=tmp_file_path)
      tmp_file = tarfile.open(tmp_file_path,"w:gz")
      tmp_file.add(file_path)
      tmp_file.close()
      RESPONSE.setHeader('Content-type', 'application/x-tar')
    else:
      tmp_file_path = file_path

    f = open(tmp_file_path)
    try:
      RESPONSE.setHeader('Content-Length', os.stat(tmp_file_path).st_size)
      RESPONSE.setHeader('Content-Disposition', \
                 'attachment;filename="%s.tar.gz"' % file_path.split('/')[-1])
      for data in f:
        RESPONSE.write(data)
    finally:
      f.close()

    if compressed:
      os.remove(tmp_file_path)

    return ''

  security.declareProtected(Permissions.ManagePortal, 'getAccessLog')
  def getAccessLog(self,  compressed=1, REQUEST=None):
    """
      Get the Access Log.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response, 
                               file_path='log/Z2.log', 
                               compressed=1) 

  security.declareProtected(Permissions.ManagePortal, 'getAccessLog')
  def getEventLog(self,  compressed=1, REQUEST=None):
    """
      Get the Access Log.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response,
                               file_path='log/event.log',
                               compressed=1)

  security.declareProtected(Permissions.ManagePortal, 'getAccessLog')
  def getDataFs(self,  compressed=1, REQUEST=None):
    """
      Get the Access Log.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response,
                               file_path='var/Data.fs',
                               compressed=1)

InitializeClass(IntrospectionTool)
