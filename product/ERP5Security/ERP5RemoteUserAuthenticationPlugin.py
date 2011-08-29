# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################


from zLOG import LOG, PROBLEM, WARNING
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import sys

from AccessControl.SecurityManagement import newSecurityManager,\
    getSecurityManager, setSecurityManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import \
    _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Security.ERP5UserManager import ERP5UserManager, SUPER_USER
from ZODB.POSException import ConflictError
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor
from Products.ERP5Security.ERP5GroupManager import ConsistencyError, NO_CACHE_MODE
from Products.ERP5Type.ERP5Type \
  import ERP5TYPE_SECURITY_GROUP_ID_GENERATION_SCRIPT
from Products.ERP5Type.Cache import CachingMethod
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery


#Form for new plugin in ZMI
manage_addERP5RemoteUserAuthenticationPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5RemoteUserAuthenticationPlugin', globals(),
  __name__='manage_addERP5RemoteUserAuthenticationPluginForm')

def addERP5RemoteUserAuthenticationPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a ERP5RemoteUserAuthenticationPlugin to a Pluggable Auth Service. """

  plugin = ERP5RemoteUserAuthenticationPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect(
          '%s/manage_workspace'
          '?manage_tabs_message='
          'ERP5RemoteUserAuthenticationPlugin+added.'
          % dispatcher.absolute_url())


class ERP5RemoteUserAuthenticationPlugin(ERP5UserManager):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Certificate Authority Authentication Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from the request header. """
    creds = {}
    getHeader = getattr(request, 'getHeader', None)
    if getHeader is None:
      # use get_header instead for Zope-2.8
      getHeader = request.get_header
    user_id = getHeader('REMOTE_USER')
    if user_id is not None:
      creds['login'] = user_id
      creds['remote_host'] = request.get('REMOTE_HOST', '')
      try:
        creds['remote_address'] = request.getClientAddr()
      except AttributeError:
        creds['remote_address'] = request.get('REMOTE_ADDR', '')
      return creds
    else:
      # fallback to default way
      return DumbHTTPExtractor().extractCredentials(request)

  ################################
  #     IAuthenticationPlugin    #
  ################################
  security.declarePrivate('authenticateCredentials')
  def authenticateCredentials(self, credentials):
    """Authentificate with credentials"""
    login = credentials.get('login', None)
    # Forbidden the usage of the super user.
    if login == SUPER_USER:
      return None

    #Search the user by his login
    user_list = self.getUserByLogin(login)
    if len(user_list) != 1:
      return None
    return (login, login)

#List implementation of class
classImplements(ERP5RemoteUserAuthenticationPlugin,
                plugins.IAuthenticationPlugin)

classImplements( ERP5RemoteUserAuthenticationPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )

InitializeClass(ERP5RemoteUserAuthenticationPlugin)
