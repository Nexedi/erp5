##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import cStringIO
from webdav.client import Resource
from Products.CMFCore.utils import UniqueObject

from App.config import getConfiguration
import os

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

from Products.ERP5 import _dtmldir

from zLOG import LOG

class LocalConfiguration(Implicit):
  """
    Holds local configuration information
  """
  def __init__(self, **kw):
    self.__dict__.update(kw)

  def update(self, **kw):
    self.__dict__.update(kw)

class TemplateTool (BaseTool):
    """
      TemplateTool manages Business Templates.

      TemplateTool provides some methods to deal with Business Templates:

        - download

        - publish

        - install

        - update

        - save
    """
    id = 'portal_templates'
    meta_type = 'ERP5 Template Tool'
    portal_type = 'Template Tool'
    allowed_types = ( 'ERP5 Business Template',)

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainRuleTool', _dtmldir )

    # Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
TemplateTool manages Business Templates."""
         , 'icon'           : 'folder_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addFolder'
         , 'immediate_view' : 'Folder_viewContentList'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ('Business Template',
                                      )
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'Folder_viewContentList'
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'search'
          , 'name'          : 'Search'
          , 'category'      : 'object_search'
          , 'action'        : 'BusinessTemplate_search'
          , 'permissions'   : (
              Permissions.View, )
          }
        )
      }

    # Import a business template
    def importURL(self, url):
      """
        Import a business template
      """
      # Copy it to import directory
      # and import in self

    def updateLocalConfiguration(self, template, **kw):
      template_id = template.getId()
      if not hasattr(self, '_local_configuration'): self._local_configuration = PersistentMapping()
      if not self._local_configuration.has_key(template_id):
        self._local_configuration[template_id] = LocalConfiguration(**kw)
      else:
        self._local_configuration[template_id].update(**kw)

    def getLocalConfiguration(self, template):
      template_id = template.getId()
      if not hasattr(self, '_local_configuration'): self._local_configuration = PersistentMapping()
      local_configuration = self._local_configuration.get(template_id, None)
      if local_configuration is not None:
        return local_configuration.__of__(self)
      return None

    def save(self, business_template, toxml=None):
      """
        Save in a format or another
      """
      business_template.build()
      self.manage_exportObject(id=business_template.getId(), toxml=toxml)
      suffix = toxml and 'xml' or 'zexp'
      cfg = getConfiguration()
      f = os.path.join(cfg.clienthome, '%s.%s' % (business_template.getId(), suffix))
      return f

    def publish(self, business_template, url, username=None, password=None):
      """
        Publish in a format or another
      """
      business_template.build()
      export_string = self.manage_exportObject(id=business_template.getId(), download=1)
      bt = Resource(url, username=username, password=password)
      bt.put(file=export_string, content_type='application/x-erp5-business-template')
      business_template.setPublicationUrl(url)

    def update(self, business_template):
      """
        Update an existing template
      """
      url = business_template.getPublicationUrl()
      id = business_template.getId()
      bt = Resource(url)
      export_string = bt.get().get_body()
      self.deleteContent(id)
      self._importObjectFromFile(cStringIO.StringIO(export_string), id=id)

    def download(self, url, id=None, REQUEST=None):
      """
        Update an existing template
      """
      from urllib import urlretrieve
      file, headers = urlretrieve(url)
      if id is None: id = self.generateNewId()
      self._importObjectFromFile(file, id=id)
      bt = self[id]
      bt.id = id # Make sure id is consistent
      bt.immediateReindexObject()

      if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Template+Downloaded+Successfully"
                           % self.absolute_url())

InitializeClass(TemplateTool)
