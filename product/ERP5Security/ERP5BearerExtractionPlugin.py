# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from Products.ERP5Type.Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor

from AccessControl.SecurityManagement import getSecurityManager,\
    setSecurityManager, newSecurityManager
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery

#Form for new plugin in ZMI
manage_addERP5BearerExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5BearerExtractionPlugin', globals(),
  __name__='manage_addERP5BearerExtractionPluginForm')

def addERP5BearerExtractionPlugin(dispatcher, id, token_portal_type,
  title=None, REQUEST=None):
  """ Add a ERP5BearerExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5BearerExtractionPlugin(id, token_portal_type, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect(
          '%s/manage_workspace'
          '?manage_tabs_message='
          'ERP5BearerExtractionPlugin+added.'
          % dispatcher.absolute_url())

class ERP5BearerExtractionPlugin(BasePlugin):
  """
  Plugin to authenicate as machines.
  """

  meta_type = "ERP5 Bearer Extraction Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, token_portal_type, title=None):
    #Register value
    self._setId(id)
    self.title = title
    self.token_portal_type = token_portal_type

  ####################################
  #ILoginPasswordHostExtractionPlugin#
  ####################################
  security.declarePrivate('extractCredentials')
  def extractCredentials(self, request):
    """ Extract credentials from the request header. """
    creds = {}
    authorisation = request._auth
    if authorisation is not None:
      if 'Bearer' in authorisation:
        l = authorisation.split()
        if len(l) == 2:
          token = l[1]
          sm = getSecurityManager()
          if sm.getUser().getId() != SUPER_USER:
            newSecurityManager(self, self.getUser(SUPER_USER))
          try:
            now = DateTime()
            token_document = self.portal_catalog.getResultValue(
              portal_type=self.token_portal_type,
              reference=token,
              query=SimpleQuery(comparison_operator='<=', expiration_date=now),
              validation_state='validated'
            )
            if token_document is not None:
              if token_document.getReference() == token and \
                token_document.getExpirationDate() <= now and \
                token_document.getValidationState() == 'validated' and \
                token_document.getDestinationReference() is not None:
                  creds['external_login'] = \
                    token_document.getDestinationReference()
          finally:
            setSecurityManager(sm)
          if 'external_login' in  creds:
            creds['external_login'] = token
            creds['remote_host'] = request.get('REMOTE_HOST', '')
            try:
              creds['remote_address'] = request.getClientAddr()
            except AttributeError:
              creds['remote_address'] = request.get('REMOTE_ADDR', '')
            return creds


    # fallback to default way
    return DumbHTTPExtractor().extractCredentials(request)

#List implementation of class
classImplements( ERP5BearerExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5BearerExtractionPlugin)
