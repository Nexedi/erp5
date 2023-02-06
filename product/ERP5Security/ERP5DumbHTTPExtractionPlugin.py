# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Nexedi SA and Contributors. All Rights Reserved.
#                    Tristan Cavelier <tristan.cavelier@nexedi.com>
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

from Products.ERP5Type.Globals import InitializeClass

from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.PluggableAuthService.interfaces import plugins
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.PluggableAuthService import DumbHTTPExtractor

from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class ERP5DumbHTTPExtractionPlugin(BasePlugin):
  """
    Default authentication behavior
  """

  meta_type = "ERP5 Dumb HTTP Extraction Plugin"
  security = ClassSecurityInfo()

  def __init__(self, id, title=None):
    #Register value
    self._setId(id)
    self.title = title

  security.declarePrivate('extractCredentials')
  @UnrestrictedMethod
  def extractCredentials(self, request):
    # BBB Zope2
    # Fix possibly broken _auth for very long auth
    if getattr(request, '_auth', '').lower().startswith('basic '):
      request._auth = request._auth.replace('\n', '')
    return DumbHTTPExtractor().extractCredentials(request);

#Form for new plugin in ZMI
manage_addERP5DumbHTTPExtractionPluginForm = PageTemplateFile(
  'www/ERP5Security_addERP5DumbHTTPExtractionPlugin', globals(),
  __name__='manage_addERP5DumbHTTPExtractionPluginForm')

def addERP5DumbHTTPExtractionPlugin(dispatcher, id, title=None, REQUEST=None):
  """ Add an ERP5DumbHTTPExtractionPlugin to a Pluggable Auth Service. """

  plugin = ERP5DumbHTTPExtractionPlugin(id, title)
  dispatcher._setObject(plugin.getId(), plugin)

  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect(
      '%s/manage_workspace'
      '?manage_tabs_message='
      'ERP5DumbHTTPExtractionPlugin+added.'
      % dispatcher.absolute_url())

#List implementation of class
classImplements(ERP5DumbHTTPExtractionPlugin,
                plugins.ILoginPasswordHostExtractionPlugin
               )
InitializeClass(ERP5DumbHTTPExtractionPlugin)
