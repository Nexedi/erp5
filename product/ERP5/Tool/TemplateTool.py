##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solane <jp@nexedi.com>
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

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Document import Folder
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

class TemplateTool (UniqueObject, Folder):
    """
    The RulesTool implements portal object
    transformation policies.

    An object transformation template is defined by
    a domain and a transformation pattent:

    The domain is defined as:

    - the meta_type it applies to

    - the portal_type it applies to

    - the conditions of application (category membership, value range,
      security, function, etc.)

    The transformation template is defined as:

    - a tree of portal_types starting on the object itself

    - default values for each node of the tree, incl. the root itself

    When a transformation is triggered, it will check the existence of
    each node and eventually update values

    Transformations are very similar to XSLT in the XML world.

    Examples of applications:

    - generate accounting movements from a stock movement

    - generate a birthday event from a person

    ERP5 main application : generate submovements from movements
    according to templates. Allows to parametrize modules
    such as payroll.

    Try to mimic: XSL semantics

    Status : OK

    NEW NAME : Rules Tool
    """
    id = 'portal_templates'
    meta_type = 'ERP5 Template Tool'
    allowed_types = ( 'ERP5 Business Template',)

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainRuleTool', _dtmldir )

    # Filter content (ZMI))
    def __init__(self):
        return Folder.__init__(self, TemplateTool.id)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = TemplateTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

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

    def publish(self, business_template, url, username=None, password=None):
      """
        Publish in a format or another
      """
      business_template.build()
      export_string = self.manage_exportObject(id=business_template.getId(), download=1)
      bt = Resource(url, username=username, password=password)
      bt.put(file=export_string, content_type='application/erp5-business-template')
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

    def download(self, url, id=None):
      """
        Update an existing template
      """
      from urllib import urlretrieve
      file, headers = urlretrieve(url)
      if id is None: id = self.generateNewId()      
      self._importObjectFromFile(file, id=id)

InitializeClass(TemplateTool)
