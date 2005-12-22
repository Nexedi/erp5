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

from Acquisition import Implicit, aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5.Document.BusinessTemplate import TemplateConditionError
from tempfile import mkstemp, mkdtemp
from Products.ERP5 import _dtmldir
from OFS.Traversable import NotFound
from difflib import unified_diff
from cStringIO import StringIO
from zLOG import LOG
from urllib import pathname2url, urlopen, splittype, urlretrieve
import re
from xml.dom.minidom import parse
import struct
import cPickle
try:
  from base64 import b64encode, b64decode
except ImportError:
  from base64 import encodestring as b64encode, decodestring as b64decode

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
    
    # This stores information on repositories.
    repository_dict = {}

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
        return local_configuration.__of__(template)
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
      tmpdir_path = mkdtemp() # XXXXXXXXXXXXXXX Why is it necessary to create a temporary directory?
      current_directory = os.getcwd() # XXXXXXXXXXXXXXXXXX not thread safe
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

    security.declareProtected( 'Import/Export objects', 'publish' )
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
      try:
        # read magic key to determine wich kind of bt we use
        file.seek(0)
        magic = file.read(5)
      finally:
        file.close()
        
      if magic == '<?xml': # old version
        self._importObjectFromFile(path, id=id)
        bt = self[id]
        bt.id = id # Make sure id is consistent
        bt.setProperty('template_format_version', 0, type='int')
      else: # new version
        tar = tarfile.open(path, 'r:gz')
        try:
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
          try:
            bt.importFile(file=fobj)
          finally:
            fobj.close()
        finally:
          tar.close()
      return bt

    security.declareProtected( Permissions.ManagePortal, 'manage_download' )
    def manage_download(self, url, id=None, REQUEST=None):
      """The management interface for download.
      """
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)

      self.download(url, id=id)
            
      if REQUEST is not None:
        ret_url = self.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Templates+Downloaded+Successfully"
                           % ret_url)

    security.declareProtected( 'Import/Export objects', 'download' )
    def download(self, url, id=None, REQUEST=None):
      """
        Download Business template, can be file or local directory
      """
      # For backward compatibility; If REQUEST is passed, it is likely from the management interface.
      if REQUEST is not None:
        return self.manage_download(url, id=id, REQUEST=REQUEST)

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
        bt = self.newContent(portal_type='Business Template', id=id)
        id = bt.getId()
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
        try:
          os.close(tempid) # Close the opened fd as soon as possible.    
          file, headers = urlretrieve(url, temppath)
          if id is None:
            id = str(self.generateNewId())
          bt = self._importBT(temppath, id)
        finally:
          os.remove(temppath)
      bt.build(no_action=1)
      bt.reindexObject()

      return bt

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
          raise RuntimeError, 'No file or an empty file was specified'
      # copy to a temp location
      import_file.seek(0) #Rewind to the beginning of file
      tempid, temppath = mkstemp()
      try:
        os.close(tempid) # Close the opened fd as soon as possible
        tempfile = open(temppath, 'w')
        try:
          tempfile.write(import_file.read())
        finally:
          tempfile.close()
        bt = self._importBT(temppath, id)
      finally:
        os.remove(temppath)
      bt.build(no_action=1)
      bt.reindexObject()

      if REQUEST is not None:
        ret_url = self.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Templates+Imported+Successfully"
                           % ret_url)

    def runUnitTestList(self, test_list=[], **kwd) :
      """
        Runs Unit Tests related to this Business Template
      """
      
      from Products.ERP5Type.tests.runUnitTest import getUnitTestFile
      return os.popen('/usr/bin/python %s %s 2>&1' % (getUnitTestFile(), ' '.join(test_list))).read()

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
            obj1_xml = item1.generateXml(path=key)
            obj2_xml = item2.generateXml(path=key)
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

    security.declareProtected( 'Import/Export objects', 'updateRepositoryBusinessTemplateList' )
    def updateRepositoryBusinessTemplateList(self, repository_list, REQUEST=None, RESPONSE=None, **kw):
      """Update the information on Business Templates in repositories.
      """
      self.repository_dict = PersistentMapping()
      property_list = ('title', 'version', 'description', 'license', 'dependency', 'copyright')
      #LOG('updateRepositoryBusiessTemplateList', 0, 'repository_list = %r' % (repository_list,))
      for repository in repository_list:
        url = '/'.join([repository, 'bt5list'])
        f = urlopen(url)
        property_dict_list = []
        try:
          doc = parse(f)
          try:
            root = doc.documentElement
            for template in root.getElementsByTagName("template"):
              id = template.getAttribute('id')
              if type(id) == type(u''):
                id = id.encode('utf-8')
              temp_property_dict = {}
              for node in template.childNodes:
                if node.nodeName in property_list:
                  value = ''
                  for text in node.childNodes:
                    if text.nodeType == text.TEXT_NODE:
                      value = text.data
                      if type(value) == type(u''):
                        value = value.encode('utf-8')
                      break
                  temp_property_dict.setdefault(node.nodeName, []).append(value)

              property_dict = {}
              property_dict['id'] = id
              property_dict['title'] = temp_property_dict.get('title', [''])[0]
              property_dict['version'] = temp_property_dict.get('version', [''])[0]
              property_dict['description'] = temp_property_dict.get('description', [''])[0]
              property_dict['license'] = temp_property_dict.get('license', [''])[0]
              property_dict['dependency_list'] = temp_property_dict.get('dependency', ())
              property_dict['copyright_list'] = temp_property_dict.get('copyright', ())
              
              property_dict_list.append(property_dict)
          finally:
            doc.unlink()
        finally:
          f.close()
        
        self.repository_dict[repository] = tuple(property_dict_list)
        
      if REQUEST is not None:
        ret_url = self.absolute_url() + '/' + REQUEST.get('form_id', 'view')
        REQUEST.RESPONSE.redirect("%s?portal_status_message=Business+Templates+Updated+Successfully"
                           % ret_url)
                
    security.declareProtected( Permissions.AccessContentsInformation, 'getRepositoryList' )
    def getRepositoryList(self):
      """Get the list of repositories.
      """
      return self.repository_dict.keys()
      
    security.declarePublic( 'decodeRepositoryBusinessTemplateUid' )
    def decodeRepositoryBusinessTemplateUid(self, uid):
      """Decode the uid of a business template in a repository. Return a repository and an id.
      """
      return cPickle.loads(b64decode(uid))
      
    security.declareProtected( Permissions.AccessContentsInformation, 'getRepositoryBusinessTemplateList' )
    def getRepositoryBusinessTemplateList(self, update_only=0, **kw):
      """Get the list of Business Templates in repositories.
      """
      version_state_title_dict = { 'new' : 'New', 'present' : 'Present', 'old' : 'Old' }

      from Products.ERP5Type.Document import newTempBusinessTemplate
      template_list = []

      template_item_list = []
      if update_only:
        # First of all, filter Business Templates in repositories.
        template_item_dict = {}
        for repository, property_dict_list in self.repository_dict.items():
          for property_dict in property_dict_list:
            title = property_dict['title']
            if title not in template_item_dict:
              # If this is the first time to see this business template, insert it.
              template_item_dict[title] = (repository, property_dict)
            else:
              # If this business template has been seen before, insert it only if
              # this business template is newer.
              previous_repository, previous_property_dict = template_item_dict[title]
              if self.compareVersions(previous_property_dict['version'], property_dict['version']) < 0:
                template_item_dict[title] = (repository, property_dict)
        # Next, select only updated business templates.
        for repository, property_dict in template_item_dict.values():
          installed_bt = self.getInstalledBusinessTemplate(property_dict['title'])
          if installed_bt is not None:
            if self.compareVersions(installed_bt.getVersion(), property_dict['version']) < 0:
              template_item_list.append((repository, property_dict))
        # FIXME: resolve dependencies
      else:
        for repository, property_dict_list in self.repository_dict.items():
          for property_dict in property_dict_list:
            template_item_list.append((repository, property_dict))

      # Create temporary Business Template objects for displaying.
      for repository, property_dict in template_item_list:
        property_dict = property_dict.copy()
        id = property_dict['id']
        del property_dict['id']
        version = property_dict['version']
        version_state = 'new'
        for bt in self.searchFolder(title = property_dict['title']):
          result = self.compareVersions(version, bt.getObject().getVersion())
          if result == 0:
            version_state = 'present'
            break
          elif result < 0:
            version_state = 'old'
        version_state_title = version_state_title_dict[version_state]
        uid = b64encode(cPickle.dumps((repository, id)))
        obj = newTempBusinessTemplate(self, 'temp_' + uid,
                                      version_state = version_state,
                                      version_state_title = version_state_title,
                                      repository = repository, **property_dict)
        obj.setUid(uid)
        template_list.append(obj)
        
      return template_list

    security.declareProtected( Permissions.AccessContentsInformation, 'getUpdatedRepositoryBusinessTemplateList' )
    def getUpdatedRepositoryBusinessTemplateList(self, **kw):
      """Get the list of updated Business Templates in repositories.
      """
      #LOG('getUpdatedRepositoryBusinessTemplateList', 0, 'kw = %r' % (kw,))
      return self.getRepositoryBusinessTemplateList(update_only=1, **kw)
      
    def compareVersions(self, version1, version2):
      """Return negative if version1 < version2, 0 if version1 == version2, positive if version1 > version2.

      Here is the algorithm:

        - Non-alphanumeric characters are not significant, besides the function of delimiters.

        - If a level of a version number is missing, it is assumed to be zero.

        - An alphabetical character is less than any numerical value.

        - Numerical values are compared as integers.

      This archives the following predicates:

        - 1.0 < 1.0.1

        - 1.0rc1 < 1.0

        - 1.0a < 1.0.1

        - 1.1 < 2.0

        - 1.0.0 = 1.0
      """
      r = re.compile('(\d+|[a-zA-Z])')
      v1 = r.findall(version1)
      v2 = r.findall(version2)

      def convert(v, i):
        """Convert the ith element of v to an interger for a comparison.
        """
        #LOG('convert', 0, 'v = %r, i = %r' % (v, i))
        try:
          e = v[i]
          try:
            e = int(e)
          except ValueError:
            # ASCII code is one byte, so this produces negative.
            e = struct.unpack('b', e)[0] - 0x200
        except IndexError:
          e = 0
        return e
        
      for i in xrange(max(len(v1), len(v2))):
        e1 = convert(v1, i)
        e2 = convert(v2, i)
        result = cmp(e1, e2)
        if result != 0:
          return result

      return 0
      
InitializeClass(TemplateTool)
