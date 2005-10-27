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
import os, tarfile, string, commands

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from tempfile import mkstemp
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
        Save BT in folder format
      """
      cfg = getConfiguration()
      path = os.path.join(cfg.clienthome, '%s' % (business_template.getTitle(),))
      business_template.export(path=path, local=1)
      if REQUEST is not None:
        ret_url = business_template.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        qs = '?portal_status_message=Saved+in+%s+.' % path
        if RESPONSE is None: RESPONSE = REQUEST.RESPONSE
        return REQUEST.RESPONSE.redirect( ret_url + qs )

    security.declareProtected( 'Import/Export objects', 'export' )
    def export(self, business_template, REQUEST=None, RESPONSE=None):
      """
        Export BT in tarball format 
      """
      path = business_template.getTitle()
      export_string = business_template.export(path=path)
      if RESPONSE is not None:
        RESPONSE.setHeader('Content-type','tar/x-gzip')
        RESPONSE.setHeader('Content-Disposition',
                           'inline;filename=%s-%s.bt5' % (business_template.getTitle(), business_template.getVersion()))
      try:
        return export_string.getvalue()
      finally:
        export_string.close()

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

    def _importBT(self, path=None, id=id):
      """
        Import template from a temp file
      """
      file = open(path, 'r')
      # read magic key to determine wich kind of bt we use
      file.seek(0)
      magic = file.read(5)
      file.close()
      if magic == '<?xml': # old version
        self._importObjectFromFile(path, id=id)
        bt = self[id]
        bt.id = id # Make sure id is consistent
        bt._tarfile = 0        
      else: # new version
        tar = tarfile.open(path, 'r:gz')
        # create bt object
        self.newContent(portal_type='Business Template', id=id)
        bt = self._getOb(id)
        for prop in bt.propertyMap():
          type = prop['type']
          pid = prop['id']
          if pid in ('uid', 'id', 'rid', 'sid', 'id_group', 'last_id'):
            continue
          prop_path = os.path.join(tar.members[0].name, 'bt', pid)
          info = tar.getmember(prop_path)
          value = tar.extractfile(info).read()
          if type == 'text' or type == 'string' or type == 'int':
            bt.setProperty(pid, value, type)
          elif type == 'lines' or type == 'tokens':
            bt.setProperty(pid[:-5], value.split('\n'), type)

        # import all other files from bt
        fobj = open(path, 'r')
        bt.importFile(file=fobj)
        fobj.close()
        tar.close()
      os.remove(path)
      return bt

    def download(self, url, id=None, REQUEST=None):
      """
        Download Business template, can be file or local directory
      """
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)
      from urllib import splittype, urlretrieve

      type, name = splittype(url)
      if os.path.isdir(name): # new version of business template in plain format (folder)
        file_list = []
        def callback(arg, directory, files):
          for file in files:
            file_list.append(os.path.join(directory, file))

        os.path.walk(name, callback, None)        
        file_list.sort()
        # import bt object
        self.newContent(portal_type='Business Template', id=id)
        bt = self._getOb(id)
        bt_path = os.path.join(name, 'bt')

        # import properties
        for prop in bt.propertyMap():
          type = prop['type']
          pid = prop['id']
          if pid in ('uid', 'id', 'rid', 'sid', 'id_group', 'last_id'):
            continue
          prop_path = os.path.join(bt_path, pid)
          value = open(prop_path, 'r').read()
          if type in ('text', 'string', 'int'):
            bt.setProperty(pid, value, type)
          elif type in ('lines', 'tokens'):
            bt.setProperty(pid[:-5], value.split(str(os.linesep)), type)
          
        # import all others objects
        bt.importFile(dir=1, file=file_list, root_path=name)
      else:
        tempid, temppath = mkstemp()      
        file, headers = urlretrieve(url, temppath)
        bt = self._importBT(temppath, id)
      bt.reindexObject()

      if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Template+Downloaded+Successfully"
                           % self.absolute_url())

    def importFile(self, import_file=None, id=None, REQUEST=None, **kw):
      """
        Import Business template from one file
      """
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)
        
      if (import_file is None) or (len(import_file.read()) == 0) :
        if REQUEST is not None :
          REQUEST.RESPONSE.redirect("%s?portal_status_message=No+file+or+an+empty+file+was+specified"
              % self.absolute_url())
          return
        else :
          raise 'Error', 'No file or an empty file was specified'
        
      # copy to a temp location
      import_file.seek(0) #Rewind to the beginning of file
      tempid, temppath = mkstemp()
      tempfile = open(temppath, 'w')
      tempfile.write(import_file.read())
      tempfile.close()
      
      bt = self._importBT(temppath, id)      
      bt.reindexObject()

      if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Template+Imported+Successfully"
                           % self.absolute_url())

    def runUnitTestList(self, test_list=[], **kwd) :
      """
        Runs Unit Tests related to this Business Template
      """
      
      from Products.ERP5Type.tests.runUnitTest import getUnitTestFile
      return os.popen('/usr/bin/python %s %s 2>&1' % (getUnitTestFile(), ' '.join(test_list))).read()

    security.declareProtected(Permissions.DeletePortalContent, 'deleteBackupObjects')

    def deleteBackupObjects(self, dry_run=1) :
      """
      removes 'btsave' objects from the ZODB
      """
      import re
      backup_re = re.compile('_btsave_[0-9]+$')
      backup_list = []

      portal = self.getPortalObject()
      for module in portal.objectValues() :
        if backup_re.search(module.getId()) :
          backup_list.append((module.getId(), portal))
        else :
          for oid in module.objectIds() :
            if backup_re.search(oid) :
              backup_list.append((oid, module))
      if dry_run :
        return '\n'.join(['%s in %s' % e for e in backup_list])
      else :
        for oid, module in backup_list :
          module.manage_delObjects(oid)

InitializeClass(TemplateTool)
