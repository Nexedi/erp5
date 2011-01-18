# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from zLOG import LOG, PROBLEM
from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import sys

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.PluggableAuthService import \
    _SWALLOWABLE_PLUGIN_EXCEPTIONS
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from ZODB.POSException import ConflictError
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor

#Form for new plugin in ZMI
manage_addVifibMachineAuthenticationPluginForm = PageTemplateFile(
  'www/Vifib_addVifibMachineAuthenticationPlugin', globals(),
  __name__='manage_addVifibMachineAuthenticationPluginForm')

def addVifibMachineAuthenticationPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add a VifibMachineAuthenticationPlugin to a Pluggable Auth Service. """

  plugin = VifibMachineAuthenticationPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect(
          '%s/manage_workspace'
          '?manage_tabs_message='
          'VifibMachineAuthenticationPlugin+added.'
          % dispatcher.absolute_url())

@transactional_cached(lambda portal, *args: args)
def getUserByLogin(portal, login):
  if isinstance(login, basestring):
    login = login,
  result = portal.portal_catalog.unrestrictedSearchResults(
      select_expression='reference',
      portal_type=["Computer", "Software Instance"],
      reference=dict(query=login, key='ExactMatch'))
  # XXX: Here, we filter catalog result list ALTHOUGH we did pass
  # parameters to unrestrictedSearchResults to restrict result set.
  # This is done because the following values can match person with
  # reference "foo":
  # "foo " because of MySQL (feature, PADSPACE collation):
  #  mysql> SELECT reference as r FROM catalog
  #      -> WHERE reference="foo      ";
  #  +-----+
  #  | r   |
  #  +-----+
  #  | foo |
  #  +-----+
  #  1 row in set (0.01 sec)
  # "bar OR foo" because of ZSQLCatalog tokenizing searched strings
  #  by default (feature).
  return [x.getObject() for x in result if x['reference'] in login]


class VifibMachineAuthenticationPlugin(BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "Vifib Machine Authentication Plugin"
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
      creds['machine_login'] = user_id
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
    login = credentials.get('machine_login', None)
    # Forbidden the usage of the super user.
    if login == SUPER_USER:
      return None

    #Search the user by his login
    user_list = self.getUserByLogin(login)
    if len(user_list) != 1:
      return None
    return (login, login)

  def getUserByLogin(self, login):
    # Search the Catalog for login and return a list of person objects
    # login can be a string or a list of strings
    # (no docstring to prevent publishing)
    if not login:
      return []
    if isinstance(login, list):
      login = tuple(login)
    elif not isinstance(login, tuple):
      login = str(login)
    try:
      return getUserByLogin(self.getPortalObject(), login)
    except ConflictError:
      raise
    except:
      LOG('VifibMachineAuthenticationPlugin', PROBLEM, 'getUserByLogin failed',
        error=sys.exc_info())
      # Here we must raise an exception to prevent callers from caching
      # a result of a degraded situation.
      # The kind of exception does not matter as long as it's catched by
      # PAS and causes a lookup using another plugin or user folder.
      # As PAS does not define explicitely such exception, we must use
      # the _SWALLOWABLE_PLUGIN_EXCEPTIONS list.
      raise _SWALLOWABLE_PLUGIN_EXCEPTIONS[0]

#List implementation of class
classImplements(VifibMachineAuthenticationPlugin,
                plugins.IAuthenticationPlugin)
classImplements( VifibMachineAuthenticationPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )


InitializeClass(VifibMachineAuthenticationPlugin)
