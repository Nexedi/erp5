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

    def getInstalledBusinessTemplate(self, title, **kw):
      """
        Return a installed business template if any.
      """
      # This can be slow if, say, 10000 business templates are present.
      # However, that unlikely happens, and using a Z SQL Method has a potential danger
      # because business templates may exchange catalog methods, so the database could be
      # broken temporarily.
      for bt in self.contentValues(filter={'portal_type':'Business Template'}):
        if bt.getInstallationState() == 'installed' and bt.getTitle() == title:
          return bt
      return None

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

    security.declareProtected( 'Import/Export objects', 'save' )
    def save(self, business_template, REQUEST=None, RESPONSE=None):
      """
        Save in a format or another
      """
      cfg = getConfiguration()
      path = os.path.join(cfg.clienthome, '%s.bt5' % business_template.getTitle())
      export_string = self.manage_exportObject(id=business_template.getId(), toxml=1, download=1)
      f = open(path, 'wb')
      try:
        f.write(export_string)
      finally:
        f.close()

      if REQUEST is not None:
        ret_url = business_template.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        qs = '?portal_status_message=Saved+in+%s+.' % path
        if RESPONSE is None: RESPONSE = REQUEST.RESPONSE
        return REQUEST.RESPONSE.redirect( ret_url + qs )

    security.declareProtected( 'Import/Export objects', 'export' )
    def export(self, business_template, REQUEST=None, RESPONSE=None):
      """
        Export in a format or another
      """
      export_string = self.manage_exportObject(id=business_template.getId(), toxml=1, download=1)
      if RESPONSE is not None:
        RESPONSE.setHeader('Content-type','application/data')
        RESPONSE.setHeader('Content-Disposition',
                           'inline;filename=%s.bt5' % business_template.getTitle())
      return export_string

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
      self._importObjectFromFile(file, id=id)
      bt = self[id]
      bt.id = id # Make sure id is consistent
      #LOG('Template Tool', 0, 'Indexing %r, isIndexable = %r' % (bt, bt.isIndexable))
      bt.immediateReindexObject()

      if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Template+Downloaded+Successfully"
                           % self.absolute_url())

    def importFile(self, import_file=None, id=None, REQUEST=None, **kw):
      """
        Update an existing template
      """
      if (import_file is None) or (len(import_file.read()) == 0) :
        if REQUEST is not None :
          REQUEST.RESPONSE.redirect("%s?portal_status_message=No+file+or+an+empty+file+was+specified"
              % self.absolute_url())
          return
        else :
          raise 'Error', 'No file or an empty file was specified'
      import_file.seek(0) #Rewind to the beginning of file
      from tempfile import mkstemp
      tempid, temppath = mkstemp()
      tempfile = open(temppath, 'w')
      tempfile.write(import_file.read())
      tempfile.close()
      self._importObjectFromFile(temppath, id=id)
      os.remove(temppath)
      bt = self[id]
      bt.id = id # Make sure id is consistent
      #LOG('Template Tool', 0, 'Indexing %r, isIndexable = %r' % (bt, bt.isIndexable))
      bt.immediateReindexObject()

      if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Template+Imported+Successfully"
                           % self.absolute_url())

InitializeClass(TemplateTool)
