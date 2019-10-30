# -*- coding: utf-8 -*-
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
import sys
import tempfile
import json
import tarfile
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from AccessControl.SecurityManagement import setSecurityManager
from Products.ERP5 import _dtmldir
from Products.ERP5.Tool.LogMixin import LogMixin
from Products.ERP5Type.Utils import \
  _setSuperSecurityManager, FileAsStreamIterator
from App.config import getConfiguration
from AccessControl import Unauthorized
from Products.ERP5Type.Cache import CachingMethod
from cgi import escape

import logging

_MARKER = []

event_log = logging.getLogger()
access_log = logging.getLogger("access")

class IntrospectionTool(LogMixin, BaseTool):
  """
    This tool provides both local and remote introspection.
  """

  id = 'portal_introspections'
  title = 'Introspection Tool'
  meta_type = 'ERP5 Introspection Tool'
  portal_type = 'Introspection Tool'

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'manage_overview')
  manage_overview = DTMLFile('explainIntrospectionTool', _dtmldir )

  #
  #   Remote menu management
  #
  security.declareProtected(Permissions.AccessContentsInformation,
                            'getFilteredActionDict')
  def getFilteredActionDict(self, user_name=_MARKER):
    """
      Returns menu items for a given user
    """
    portal = self.getPortalObject()
    is_portal_manager = portal.portal_membership.checkPermission(\
      Permissions.ManagePortal, self)

    downgrade_authenticated_user = user_name is not _MARKER and is_portal_manager
    if downgrade_authenticated_user:
      # downgrade to desired user
      original_security_manager = _setSuperSecurityManager(self, user_name)

    # call the method implementing it
    erp5_menu_dict = portal.portal_actions.listFilteredActionsFor(portal)

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
      Returns module items for a given user
    """
    portal = self.getPortalObject()
    is_portal_manager = portal.portal_membership.checkPermission(
      Permissions.ManagePortal, self)

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

  #
  #   Local file access
  #
  def _getLocalFile(self, REQUEST, RESPONSE, file_path,
                         tmp_file_path='/tmp/', compressed=1):
    """
      It should return the local file compacted or not as tar.gz.
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
      try:
        tmp_file.add(file_path)
      finally:
        tmp_file.close()
      RESPONSE.setHeader('Content-type', 'application/x-tar')
      RESPONSE.setHeader('Content-Disposition', \
                 'attachment;filename="%s.tar.gz"' % file_path.split('/')[-1])
    else:
      RESPONSE.setHeader('Content-type', 'application/txt')
      RESPONSE.setHeader('Content-Disposition', \
                 'attachment;filename="%s.txt"' % file_path.split('/')[-1])

      tmp_file_path = file_path

    r = FileAsStreamIterator(tmp_file_path, remove_file=compressed)
    RESPONSE.setHeader('Content-Length', str(len(r)))
    return r

  def __getEventLogPath(self):
    """
      Get the Event Log.
    """
    return event_log.handlers[0].baseFilename


  def __getAccessLogPath(self):
    """
      Get the Event Log.
    """
    return access_log.handlers[0].baseFilename

  def _tailFile(self, file_name, line_number=10):
    """
    Do a 'tail -f -n line_number filename'
    """
    log_file = os.path.join(getConfiguration().instancehome, file_name)
    if not os.path.exists(log_file):
      raise IOError, 'The file: %s does not exist.' % log_file

    char_per_line = 75

    with open(log_file,'r') as tailed_file:
      while 1:
        try:
          tailed_file.seek(-1 * char_per_line * line_number, 2)
        except IOError:
          tailed_file.seek(0)
        pos = tailed_file.tell()

        lines = tailed_file.read().split("\n")
        if len(lines) > (line_number + 1) or not pos:
          break
        # The lines are bigger than we thought
        char_per_line *= 1.3  # Inc for retry

    start = max(len(lines) - line_number - 1, 0)
    return "\n".join(lines[start:len(lines)])

  security.declareProtected(Permissions.ManagePortal, 'tailEventLog')
  def tailEventLog(self):
    """
    Tail the Event Log.
    """
    return escape(self._tailFile(self.__getEventLogPath(), 500))

  security.declareProtected(Permissions.ManagePortal, 'tailAccessLog')
  def tailAccessLog(self):
    """
    Tail the Event Log.
    """
    return escape(self._tailFile(self.__getAccessLogPath(), 50))

  security.declareProtected(Permissions.ManagePortal, 'getAccessLog')
  def getAccessLog(self, compressed=1, REQUEST=None):
    """
      Get the Access Log.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response,
                               file_path=self.__getAccessLogPath(),
                               compressed=compressed)

  security.declareProtected(Permissions.ManagePortal, 'getEventLog')
  def getEventLog(self, compressed=1, REQUEST=None):
    """
      Get the Event Log.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response,
                               file_path=self.__getEventLogPath(),
                               compressed=compressed)

  security.declareProtected(Permissions.ManagePortal, 'getDataFs')
  def getDataFs(self, compressed=1, REQUEST=None):
    """
      Get the Data.fs.
    """
    if REQUEST is not None:
      response = REQUEST.RESPONSE
    else:
      return "FAILED"

    return self._getLocalFile(REQUEST, response,
                               file_path='var/Data.fs',
                               compressed=compressed)

  #
  #   Instance variable definition access
  #
  security.declareProtected(Permissions.ManagePortal, '_loadExternalConfig')
  def _loadExternalConfig(self):
    """
      Load configuration from one external file, this configuration
      should be set for security reasons to prevent people access
      forbidden areas in the system.
    """
    def cached_loadExternalConfig():
      import ConfigParser
      config = ConfigParser.ConfigParser()
      config.readfp(open('/etc/erp5.cfg'))
      return config

    cached_loadExternalConfig = CachingMethod(cached_loadExternalConfig,
                                id='IntrospectionTool__loadExternalConfig',
                                cache_factory='erp5_content_long')
    return  cached_loadExternalConfig()

  security.declareProtected(Permissions.ManagePortal, '_getSoftwareHome')
  def _getSoftwareHome(self):
    """
      Get the value of SOFTWARE_HOME for zopectl startup script
      or from zope.conf (whichever is most relevant)
    """
    return getConfiguration().softwarehome

  security.declareProtected(Permissions.ManagePortal, '_getPythonExecutable')
  def _getPythonExecutable(self):
    """
      Get the value of PYTHON for zopectl startup script
      or from zope.conf (whichever is most relevant)
    """
    return sys.executable

  security.declareProtected(Permissions.ManagePortal, '_getProductPathList')
  def _getProductPathList(self):
    """
      Get the value of SOFTWARE_HOME for zopectl startup script
      or from zope.conf (whichever is most relevant)
    """
    return getConfiguration().products

  security.declareProtected(Permissions.ManagePortal, '_getSystemVersionDict')
  def _getSystemVersionDict(self):
    """
      Returns a dictionnary with all versions of installed libraries
      {
         'python': '2.4.3'
       , 'pysvn': '1.2.3'
       , 'ERP5' : "5.4.3"
      }
      NOTE: consider using autoconf / automake tools ?
    """
    def cached_getSystemVersionDict():
      import pkg_resources
      version_dict = {}
      for dist in pkg_resources.working_set:
        version_dict[dist.key] = dist.version

      from Products import ERP5 as erp5_product
      erp5_product_path = os.path.dirname(erp5_product.__file__)
      try:
        with open(os.path.join(erp5_product_path, "VERSION.txt")) as f:
          erp5_version = f.read().strip().replace("ERP5 ", "")
      except Exception:
        erp5_version = None

      version_dict["ProductS.ERP5"] = erp5_version
      return version_dict

    get_system_version_dict = CachingMethod(
                  cached_getSystemVersionDict,
                  id='IntrospectionTool__getSystemVersionDict',
                  cache_factory='erp5_content_long')

    return get_system_version_dict()

  security.declareProtected(Permissions.ManagePortal,
      '_getExternalConnectionDict')
  def _getExternalConnectionDict(self):
    """ Return a dictionary with all connections from ERP5 to an External
        Service, this may include MySQL, Memcached, Kumofs, Ldap or any other.

        The standard format is:
	  {'relative_url/method_or_property_id' : method_value_output,}.
    """
    connection_dict = {}
    portal = self.getPortalObject()

    def collect_information_by_method(document, method_id):
      method_object = getattr(document, method_id, None)
      key = "%s/%s" % (document.getRelativeUrl(), method_id)
      connection_dict[key] = method_object()

    portal = self.getPortalObject()

    # Collect information from portal memcached
    for plugin in portal.portal_memcached.objectValues():
      collect_information_by_method(plugin, "getUrlString")

    system_preference = \
       portal.portal_preferences.getActiveSystemPreference()

    if system_preference is not None:
      # Conversion Server information
      collect_information_by_method(system_preference,
                         'getPreferredOoodocServerAddress')
      collect_information_by_method(system_preference,
                         'getPreferredOoodocServerPortNumber')
      collect_information_by_method(system_preference,
                         'getPreferredDocumentConversionServerUrl')

    def collect_information_by_property(document, property_id):
      key = "%s/%s" % (document.getId(), property_id)
      connection_dict[key] = str(getattr(document, property_id, None))

    # Collect information related to Mail Server.
    collect_information_by_property(self.MailHost,'smtp_host')
    collect_information_by_property(self.MailHost,'smtp_port')

    # Collect information related to Databases. ie.: MySQL, LDap?
    for conn in self.objectValues(["CMFActivity Database Connection",
                                   "Z MySQL Database Connection",
                                   "Z MySQL Deferred Database Connection"]):

      collect_information_by_property(conn,'connection_string')

    # collect information from certificate authority
    certificate_authority = getattr(portal, 'portal_certificate_authority',
      None)
    if certificate_authority is not None:
      collect_information_by_property(certificate_authority,
        'certificate_authority_path')
    return connection_dict

  security.declareProtected(Permissions.ManagePortal,
      '_getBusinessTemplateRevisionDict')
  def _getBusinessTemplateRevisionDict(self):
    """ Return a Dictionary of installed business templates and their revisions
    """
    business_template_dict = {}
    for installed in self.portal_templates.getInstalledBusinessTemplateList():
       business_template_dict[installed.getTitle()] = installed.getRevision()
    return business_template_dict

  security.declareProtected(Permissions.ManagePortal,
      '_getActivityDict')
  def _getActivityDict(self):
    """ Return a Dictionary with the snapshot with the status of activities.
        failures (-2 and -3) and running.
    """
    activity_dict = {}
    # XXX Maybe this is not so efficient check. Performance Optimization
    # should be consider.
    activity_dict['failure'] = len(self.portal_activities.getMessageList(processing_node=-2))
    activity_dict['total'] = len(self.portal_activities.getMessageList())
    return activity_dict

  security.declareProtected(Permissions.ManagePortal, 'getSystemSignatureDict')
  def getSystemSignatureDict(self):
    """ Returns a dictionary with all information related to the instance.
    This information can report what resources (memcache, mysql, zope,
    python, libraries) the instance is using. Also, what business templates are
    installed.

    Such information is usefull to detect changes in the system, into upgrader,
    slapos and/or to build Introspection Reports.
    """
    business_template_repository_list = self.portal_templates.getRepositoryList()
    return dict(
           activity_dict=self._getActivityDict(),
           version_dict=self._getSystemVersionDict(),
           external_connection_dict=self._getExternalConnectionDict(),
           business_template_dict=self._getBusinessTemplateRevisionDict(),
           business_template_repository_list=business_template_repository_list)

  security.declareProtected(Permissions.ManagePortal, 'getSystemSignatureAsJSON')
  def getSystemSignatureAsJSON(self, REQUEST=None):
    """
      Returns the information as JSON.

      THIS merhod could be a decorator or use a some other clever way to convert
      the getSystemSignatureDict
    """
    if REQUEST is not None:
      REQUEST.set("Content-Type", "application/json")
    return json.dumps(self.getSystemSignatureDict())

InitializeClass(IntrospectionTool)
