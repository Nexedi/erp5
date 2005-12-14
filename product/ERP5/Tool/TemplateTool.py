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

from webdav.client import Resource
from Products.CMFCore.utils import UniqueObject

from App.config import getConfiguration
import os, tarfile, string, commands, OFS

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5.Document.BusinessTemplate import TemplateConditionError
from tempfile import mkstemp
from Products.ERP5 import _dtmldir
from OFS.Traversable import NotFound
from difflib import unified_diff
from cStringIO import StringIO
from zLOG import LOG
from urllib import pathname2url

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
    title = 'Template Tool'
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
      path = pathname2url(path)
      business_template.export(path=path, local=1)
      if REQUEST is not None:
        ret_url = business_template.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        qs = '?portal_status_message=Saved+in+%s+.' % pathname2url(path)
        if RESPONSE is None: RESPONSE = REQUEST.RESPONSE
        return REQUEST.RESPONSE.redirect( ret_url + qs )

    security.declareProtected( 'Import/Export objects', 'export' )
    def export(self, business_template, REQUEST=None, RESPONSE=None):
      """
        Export BT in tarball format 
      """
      path = business_template.getTitle()
      path = pathname2url(path)
      tmpfile_path = os.tmpnam()
      tmpdir_path = os.path.dirname(tmpfile_path)
      current_directory = os.getcwd()
      os.chdir(tmpdir_path)
      export_string = business_template.export(path=path)
      os.chdir(current_directory)
      if RESPONSE is not None:
        RESPONSE.setHeader('Content-type','tar/x-gzip')
        RESPONSE.setHeader('Content-Disposition',
                           'inline;filename=%s-%s.bt5' % \
                               (path, 
                                business_template.getVersion()))
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
      self._importObjectFromFile(StringIO(export_string), id=id)

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
        bt.setProperty('template_format_version', 0, type='int')
      else: # new version
        tar = tarfile.open(path, 'r:gz')
        # create bt object
        self.newContent(portal_type='Business Template', id=id)
        bt = self._getOb(id)
        prop_dict = {}
        for prop in bt.propertyMap():
          type = prop['type']
          pid = prop['id']
          prop_path = os.path.join(tar.members[0].name, 'bt', pid)
          try:
            info = tar.getmember(prop_path)
          except KeyError:
            continue
          value = tar.extractfile(info).read()
          if type == 'text' or type == 'string' or type == 'int':
            prop_dict[pid] = value
          elif type == 'lines' or type == 'tokens':
            prop_dict[pid[:-5]] = value.split(str(os.linesep))
        prop_dict.pop('id', '')
        bt.edit(**prop_dict)
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
          if 'CVS' not in directory:
            for file in files:
              file_list.append(os.path.join(directory, file))

        os.path.walk(name, callback, None)        
        file_list.sort()
        # import bt object
        self.newContent(portal_type='Business Template', id=id)
        bt = self._getOb(id)
        bt_path = os.path.join(name, 'bt')

        # import properties
        prop_dict = {}
        for prop in bt.propertyMap():
          type = prop['type']
          pid = prop['id']
          prop_path = os.path.join('.', bt_path, pid)
          if not os.path.exists(prop_path):
            continue          
          value = open(prop_path, 'r').read()
          if type in ('text', 'string', 'int'):
            prop_dict[pid] = value
          elif type in ('lines', 'tokens'):
            prop_dict[pid[:-5]] = value.split(str(os.linesep))
        prop_dict.pop('id', '')
        bt.edit(**prop_dict)
        # import all others objects
        bt.importFile(dir=1, file=file_list, root_path=name)
      else:
        tempid, temppath = mkstemp()      
        file, headers = urlretrieve(url, temppath)
        bt = self._importBT(temppath, id)
      bt.build(no_action=1)
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
      bt.build(no_action=1)
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

    def diff(self, **kw):
      """
      Make a diff between two Business Template
      """
      compare_to_installed = 0
      # get the business template      
      p = self.getPortalObject()
      portal_selections = p.portal_selections
      selection_name = 'business_template_selection' # harcoded because we can also get delete_selection
      uids = portal_selections.getSelectionCheckedUidsFor(selection_name)
      bt1 = self.portal_catalog.getObject(uids[0])
      if bt1.getBuildingState() != 'built':
        raise TemplateConditionError, 'Business Template must be built to make diff'
      if (getattr(bt1, 'template_format_version', 0)) != 1:
        raise TemplateConditionError, 'Business Template must be in new format'
      # check if there is a second bt is or if we compare to installed one
      if len(uids) == 2:
        bt2 = self.portal_catalog.getObject(uids[1])
        if bt2.getBuildingState() != 'built':
          raise TemplateConditionError, 'Business Template must be built to make diff'
        if (getattr(bt2, 'template_format_version', 0)) != 1:
          raise TemplateConditionError, 'Business Template must be in new format'
      else:
        compare_to_installed = 1
        installed_bt = self.getInstalledBusinessTemplate(title=bt1.getTitle())
        if installed_bt is None:
          raise NotFound, 'Installed business template with title %s not found' %(bt1.getTitle(),)
        LOG('compare to installed bt', 0, str((installed_bt.getTitle(), installed_bt.getId())))
        # get a copy of the installed bt
        bt2 = self.manage_clone(ob=installed_bt, id='installed_bt')
        bt2.edit(description='tmp bt generated for diff')
        
      # separate item because somes are exported with zope exportXML and other with our own method
      # and others are just python code on filesystem
      diff_msg = 'Diff between %s-%s and %s-%s' %(bt1.getTitle(), bt1.getId(), bt2.getTitle(), bt2.getId())
      # for the one with zope exportXml
      item_list_1 = ['_product_item', '_workflow_item', '_portal_type_item', '_category_item', '_path_item', '_skin_item', '_action_item']
      for item_name  in item_list_1:
        item1 = getattr(bt1, item_name)        
        # build current item if we compare to installed bt
        if compare_to_installed:
          getattr(bt2, item_name).build(bt2)
        item2 = getattr(bt2, item_name)
        for key in  item1._objects.keys():
          if item2._objects.has_key(key):
            object1 = item1._objects[key]
            object2 = item2._objects[key]
            f1 = StringIO()
            f2 = StringIO()
            OFS.XMLExportImport.exportXML(object1._p_jar, object1._p_oid, f1)
            OFS.XMLExportImport.exportXML(object2._p_jar, object2._p_oid, f2)
            obj1_xml = f1.getvalue()
            obj2_xml = f2.getvalue()
            f1.close()
            f2.close()
            ob1_xml_lines = obj1_xml.splitlines()
            ob2_xml_lines = obj2_xml.splitlines()
            diff_list = list(unified_diff(ob1_xml_lines, ob2_xml_lines, fromfile=bt1.getId(), tofile=bt2.getId(), lineterm=''))
            if len(diff_list) != 0:
              diff_msg += '\n\nObject %s diff :\n' %(key)
              diff_msg += '\n'.join(diff_list)

      # for our own way to generate xml
      item_list_2 = ['_site_property_item', '_module_item', '_catalog_result_key_item', '_catalog_related_key_item', '_catalog_result_table_item']
      for item_name  in item_list_2:
        item1 = getattr(bt1, item_name)        
        # build current item if we compare to installed bt
        if compare_to_installed:
          getattr(bt2, item_name).build(bt2)
        item2 = getattr(bt2, item_name)
        for key in  item1._objects.keys():
          if item2._objects.has_key(key):
            obj1_xml = item1.generate_xml(path=key)
            obj2_xml = item2.generate_xml(path=key)
            ob1_xml_lines = obj1_xml.splitlines()
            ob2_xml_lines = obj2_xml.splitlines()
            diff_list = list(unified_diff(ob1_xml_lines, ob2_xml_lines, fromfile=bt1.getId(), tofile=bt2.getId(), lineterm=''))
            if len(diff_list) != 0:
              diff_msg += '\n\nObject %s diff :\n' %(key)
              diff_msg += '\n'.join(diff_list)
              
      # for document located on filesystem
      item_list_3 = ['_document_item', '_property_sheet_item', '_extension_item', '_test_item', '_message_translation_item']
      for item_name  in item_list_3:
        item1 = getattr(bt1, item_name)        
        # build current item if we compare to installed bt
        if compare_to_installed:
          getattr(bt2, item_name).build(bt2)
        item2 = getattr(bt2, item_name)
        for key in  item1._objects.keys():
          if item2._objects.has_key(key):
            obj1_code = item1._objects[key]
            obj2_code = item2._objects[key]
            ob1_lines = obj1_code.splitlines()
            ob2_lines = obj2_code.splitlines()
            diff_list = list(unified_diff(ob1_lines, ob2_lines, fromfile=bt1.getId(), tofile=bt2.getId(), lineterm=''))
            if len(diff_list) != 0:
              diff_msg += '\n\nObject %s diff :\n' %(key)
              diff_msg += '\n'.join(diff_list)
              
      if compare_to_installed:
        self.manage_delObjects(ids=['installed_bt'])
      return diff_msg
          
InitializeClass(TemplateTool)
