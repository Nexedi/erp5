# -*- coding: utf-8 -*-
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

from App.config import getConfiguration
import os
import shutil
import sys

from Acquisition import Implicit, Explicit
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFActivity.ActiveResult import ActiveResult
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.DiffUtils import DiffFile
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import transactional_cached
from Products.ERP5Type import Permissions
from Products.ERP5.Document.BusinessTemplate import BusinessTemplateMissingDependency
from Products.ERP5.genbt5list import generateInformation
from Acquisition import aq_base
from tempfile import mkstemp, mkdtemp
from Products.ERP5 import _dtmldir
from cStringIO import StringIO
from urllib import pathname2url, urlopen, splittype, urlretrieve
import urllib2
import re
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError
import struct
import cPickle
from base64 import b64encode, b64decode
from Products.ERP5Type.Message import translateString
from zLOG import LOG, INFO, WARNING
from base64 import decodestring
import subprocess
import time

WIN = os.name == 'nt'

CATALOG_UPDATABLE = object()
ModuleSecurityInfo(__name__).declarePublic('CATALOG_UPDATABLE')

class BusinessTemplateUnknownError(Exception):
  """ Exception raised when the business template
      is impossible to find in the repositories
  """
  pass

class UnsupportedComparingOperator(Exception):
  """ Exception when the comparing string is unsupported
  """
  pass

class BusinessTemplateIsMeta(Exception):
  """ Exception when the business template is provided by another one
  """
  pass

ModuleSecurityInfo(__name__).declarePublic('BusinessTemplateUnknownError')

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
    allowed_types = (
      'ERP5 Business Template',
      'ERP5 Business Package',
      'ERP5 Business Manager',
      )

    # This stores information on repositories.
    repository_dict = {}

    # Declarative Security
    security = ClassSecurityInfo()

    security.declareProtected(Permissions.ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('explainTemplateTool', _dtmldir)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstalledBusinessTemplate')
    def getInstalledBusinessTemplate(self, title, strict=False, **kw):
      """Returns an installed version of business template of a given title.

        Returns None if business template is not installed or has been uninstalled.
        It not "installed" business template is found, look at replaced ones.
        This is mostly usefull if we are looking for the installed business
        template in a transaction replacing an existing business template.
        If strict is true, we do not take care of "replaced" business templates.
      """
      # This can be slow if, say, 10000 business templates are present.
      # However, that unlikely happens, and using a Z SQL Method has a
      # potential danger because business templates may exchange catalog
      # methods, so the database could be broken temporarily.
      last_bt = last_time = None
      for bt in self.objectValues(portal_type=['Business Template', 'Business Package']):
        if bt.getTitle() == title or title in bt.getProvisionList():
          state = bt.getInstallationState()
          if state == 'installed':
            return bt
          if state == 'not_installed':
            last_transition = bt.workflow_history \
              ['business_template_installation_workflow'][-1]
            if last_transition['action'] == 'uninstall': # There is not uninstalled state !
              t = last_transition['time']
              if last_time < t:
                last_bt = None
                last_time = t
          elif state == 'replaced' and not strict:
            t = bt.workflow_history \
              ['business_template_installation_workflow'][-1]['time']
            if last_time < t:
              last_bt = bt
              last_time = t
      return last_bt

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstalledBusinessTemplatesList')
    def getInstalledBusinessTemplatesList(self):
      """Deprecated.
      """
      DeprecationWarning('getInstalledBusinessTemplatesList is deprecated; Use getInstalledBusinessTemplateList instead.', DeprecationWarning)
      return self.getInstalledBusinessTemplateList()

    def _getInstalledBusinessTemplateList(self, only_title=0):
      """Get the list of installed business templates.
      """
      installed_bts = []
      for bt in self.contentValues(portal_type=['Business Template', 'Business Package']):
        if bt.getInstallationState() == 'installed':
          bt5 = bt
          if only_title:
            bt5 = bt.getTitle()
          installed_bts.append(bt5)
      return installed_bts

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstalledBusinessTemplateList')
    def getInstalledBusinessTemplateList(self):
      """Get the list of installed business templates.
      """
      return self._getInstalledBusinessTemplateList(only_title=0)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstalledBusinessTemplateTitleList')
    def getInstalledBusinessTemplateTitleList(self):
      """Get the list of installed business templates.
      """
      return self._getInstalledBusinessTemplateList(only_title=1)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getInstalledBusinessTemplateRevision')
    def getInstalledBusinessTemplateRevision(self, title, **kw):
      """
        Return the revision of business template installed with the title
        given
      """
      bt = self.getInstalledBusinessTemplate(title)
      if bt is not None:
        return bt.getRevision()
      return None

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getBuiltBusinessTemplateList')
    def getBuiltBusinessTemplateList(self):
      """Get the list of built and not installed business templates.
      """
      return [bt for bt in self.objectValues(portal_type='Business Template')
                 if bt.getInstallationState() == 'not_installed' and
                    bt.getBuildingState() == 'built']

    @property
    def asRepository(self):
      class asRepository(Explicit):
        """Export business template by their title

        Provides a view of template tool allowing a user to download the last
        edited business template with a URL like:
          http://.../erp5/portal_templates/asRepository/erp5_core
        """
        def __before_publishing_traverse__(self, self2, request):
          path = request['TraversalRequestNameStack']
          self.subpath = tuple(reversed(path))
          del path[:]
        def __call__(self, REQUEST, RESPONSE):
          title, = self.subpath
          last_bt = None, None
          for bt in self.aq_parent.searchFolder(title=title):
            bt = bt.getObject()
            modified = bt.getModificationDate()
            if last_bt[0] < modified and bt.getInstallationState() != 'deleted':
              last_bt = modified, bt
          if last_bt[1] is None:
            return RESPONSE.notFoundError(title)
          RESPONSE.setHeader('Content-type', 'application/data')
          RESPONSE.setHeader('Content-Disposition',
                             'inline;filename=%s-%s.zexp' % (title, last_bt[0]))
          if REQUEST['REQUEST_METHOD'] == 'GET':
            bt = last_bt[1]
            if bt.getBuildingState() != 'built':
              bt.build()
            return self.aq_parent.manage_exportObject(bt.getId(), download=1)
      return asRepository().__of__(self)

    security.declareProtected(Permissions.ManagePortal,
                              'getDefaultBusinessTemplateDownloadURL')
    def getDefaultBusinessTemplateDownloadURL(self):
      """Returns the default download URL for business templates.
      """
      return "file://%s/" % pathname2url(
                  os.path.join(getConfiguration().instancehome, 'bt5'))

    security.declareProtected('Import/Export objects', 'save')
    def save(self, business_template, REQUEST=None, RESPONSE=None):
      """
        Save the BusinessTemplate in the servers's filesystem.
      """
      cfg = getConfiguration()
      path = os.path.join(cfg.clienthome,
                          '%s' % (business_template.getTitle(),))
      path = pathname2url(path)
      business_template.export(path=path, local=True)
      if REQUEST is not None:
        psm = translateString('Saved in ${path} .',
                              mapping={'path':pathname2url(path)})
        ret_url = '%s/%s?portal_status_message=%s' % \
                  (business_template.absolute_url(),
                   REQUEST.get('form_id', 'view'), psm)
        if RESPONSE is None:
          RESPONSE = REQUEST.RESPONSE
        return REQUEST.RESPONSE.redirect( ret_url )

    security.declareProtected( 'Import/Export objects', 'export' )
    def export(self, business_template, REQUEST=None, RESPONSE=None, is_package=False):
      """
        Export the Business Template as a bt5 file and offer the user to
        download it.
      """
      export_string = business_template.export()
      try:
        if RESPONSE is not None:
          RESPONSE.setHeader('Content-type','tar/x-gzip')
          if not is_package:
            RESPONSE.setHeader('Content-Disposition', 'inline;filename=%s-%s.bt5'
              % (business_template.getTitle(), business_template.getVersion()))
          else:
            RESPONSE.setHeader('Content-Disposition', 'inline;filename=%s.bp5'
            % business_template.getTitle())
        return export_string.getvalue()
      finally:
        export_string.close()

    security.declareProtected( 'Import/Export objects', 'publish' )
    def publish(self, business_template, url, username=None, password=None):
      """
        Publish the given business template at the given URL.
      """
      business_template.build()
      export_string = self.manage_exportObject(id=business_template.getId(),
                                               download=True)
      bt = Resource(url, username=username, password=password)
      bt.put(file=export_string,
             content_type='application/x-erp5-business-template')
      business_template.setPublicationUrl(url)

    security.declareProtected(Permissions.ManagePortal, 'update')
    def update(self, business_template):
      """
        Update an existing template from its publication URL.
      """
      url = business_template.getPublicationUrl()
      id = business_template.getId()
      bt = Resource(url)
      export_string = bt.get().get_body()
      self.deleteContent(id)
      self._importObjectFromFile(StringIO(export_string), id=id)


    security.declareProtected( Permissions.ManagePortal, 'manage_download' )
    def manage_download(self, url, id=None, REQUEST=None):
      """The management interface for download.
      """
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)

      bt = self.download(url, id=id)

      if REQUEST is not None:
        ret_url = bt.absolute_url()
        psm = translateString("Business template downloaded successfully.")
        REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                    % (ret_url, psm))

    def _download_local(self, path, bt_id, format_version=1):
      """Download Business Template from local directory or file
      """
      if format_version == 2:
        bp = self.newContent(bt_id, 'Business Package')
        bp.importFile(path)
        return bp
      elif format_version == 3:
        bm = self.newContent(bt_id, 'Business Manager')
        bm.importFile(path)
        return bm

      bt = self.newContent(bt_id, 'Business Template')
      bt.importFile(path)
      return bt

    def _download_url(self, url, bt_id):
      tempid, temppath = mkstemp()
      try:
        os.close(tempid) # Close the opened fd as soon as possible.
        file_path, headers = urlretrieve(url, temppath)
        if re.search(r'<title>.*Revision \d+:', open(file_path, 'r').read()):
          # this looks like a subversion repository, try to check it out
          LOG('ERP5', INFO, 'TemplateTool doing a svn checkout of %s' % url)
          return self._download_svn(url, bt_id)

        return self._download_local(file_path, bt_id)
      finally:
        os.remove(temppath)

    def _download_svn(self, url, bt_id):
      svn_checkout_tmp_dir = mkdtemp()
      svn_checkout_dir = os.path.join(svn_checkout_tmp_dir, 'bt')
      try:
        from Products.ERP5VCS.WorkingCopy import getVcsTool
        getVcsTool('svn').__of__(self).export(url, svn_checkout_dir)
        return self._download_local(svn_checkout_dir, bt_id)
      finally:
        shutil.rmtree(svn_checkout_tmp_dir)

    security.declareProtected( 'Import/Export objects', 'download' )
    def download(self, url, id=None, REQUEST=None):
      """
      Download Business Template from url, can be file or local directory
      """
      # For backward compatibility: If REQUEST is passed, it is likely that we
      # come from the management interface.
      if REQUEST is not None:
        return self.manage_download(url, id=id, REQUEST=REQUEST)
      if id is None:
        id = self.generateNewId()

      urltype, path = splittype(url)
      if WIN and urltype and '\\' in path:
        urltype = None
        path = url
      if urltype and urltype != 'file':
        if '/portal_templates/asRepository/' in url:
          # In this case, the downloaded BT is already built.
          bt = self._p_jar.importFile(urlopen(url))
          bt.id = id
          del bt.uid
          return self[self._setObject(id, bt)]
        bt = self._download_url(url, id)
      else:
        template_version_path_list = [
                                      name+'/bp/template_format_version',
                                      name+'/bm/template_format_version',
                                     ]

        for path in template_version_path_list:
          try:
            file = open(os.path.normpath(path))
          except IOError:
            continue
        try:
          format_version = int(file.read())
          file.close()
        except UnboundLocalError:
          # In case none of the above paths do have template_format_version
          format_version = 1
        # XXX: Download only needed in case the file is in directory
        bt = self._download_local(os.path.normpath(name), id, format_version)

      bt.build(no_action=True)
      return bt

    security.declareProtected('Import/Export objects', 'importBase64EncodedText')
    def importBase64EncodedText(self, file_data=None, id=None, REQUEST=None,
                                batch_mode=False, **kw):
      """
        Import Business Template from passed base64 encoded text.
      """
      import_file = StringIO(decodestring(file_data))
      return self.importFile(import_file = import_file, id = id, REQUEST = REQUEST,
                             batch_mode = batch_mode, **kw)

    security.declareProtected('Import/Export objects', 'importFile')
    def importFile(self, import_file=None, id=None, REQUEST=None,
                   batch_mode=False, **kw):
      """
        Import Business Template from one file
      """
      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)

      if id is None:
        id = self.generateNewId()

      if (import_file is None) or (len(import_file.read()) == 0):
        if REQUEST is not None:
          psm = translateString('No file or an empty file was specified.')
          REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                    % (self.absolute_url(), psm))
          return
        else :
          raise RuntimeError, 'No file or an empty file was specified'
      # copy to a temp location
      import_file.seek(0) #Rewind to the beginning of file
      tempid, temppath = mkstemp()
      try:
        os.close(tempid) # Close the opened fd as soon as possible
        with open(temppath, 'wb') as tempfile:
          tempfile.write(import_file.read())
        bt = self._download_local(temppath, id)
      finally:
        os.remove(temppath)
      bt.build(no_action=True)
      bt.reindexObject()

      if not batch_mode and \
         (REQUEST is not None):
        ret_url = bt.absolute_url()
        psm = translateString("Business templates imported successfully.")
        REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                  % (ret_url, psm))
      elif batch_mode:
        return bt

    security.declareProtected(Permissions.ManagePortal, 'getDiffFilterScriptList')
    def getDiffFilterScriptList(self):
      """
      Return list of scripts usable to filter diff
      """
      # XXX, the "or ()" should not be there, the preference tool is
      # inconsistent, the called method should not return None when
      # nothing is selected
      portal = self.getPortalObject()
      script_list = []
      for script_id in portal.portal_preferences\
         .getPreferredDiffFilterScriptIdList() or ():
        try:
          script_list.append(getattr(portal, script_id))
        except AttributeError:
          LOG("TemplateTool", WARNING, "Unable to find %r script" % script_id)
      return script_list

    security.declareProtected(Permissions.ManagePortal, 'getFilteredDiffAsHTML')
    def getFilteredDiffAsHTML(self, diff):
      """
      Return the diff filtered by python scripts into html format
      """
      return self.getFilteredDiff(diff).toHTML()

    def _cleanUpTemplateFolder(self, folder_path):
      file_object_list = [x for x in os.listdir(folder_path)]
      for file_object in file_object_list:
        file_object_path = os.path.join(folder_path, file_object)
        if os.path.isfile(file_object_path):
          os.unlink(file_object_path)
        else:
          shutil.rmtree(file_object_path)

    security.declareProtected( 'Import/Export objects', 'importAndReExportBusinessTemplateFromPath' )
    def importAndReExportBusinessTemplateFromPath(self, template_path):
      """
        Imports the template that is in the template_path and exports it to the
        same path.

        We want to clean this directory, i.e. remove all files before
        the export. Because this is called as activity though, it could cause
        the following problem:
        - Activity imports the template
        - Activity removes all files from template_path
        - Activity fails in export.
        Then the folder contents will be changed, so when retrying the
        activity may succeed without the user understanding that files were
        erased. For this reason export is done in 3 steps:
        - First to a temporary directory
        - If there was no error delete contents of template_path
        - Copy the contents of the temporary directory to the template_path
      """
      import_template = self.download(url=template_path)
      export_dir = mkdtemp()
      try:
        import_template.export(path=export_dir, local=True)
        self._cleanUpTemplateFolder(template_path)
        file_name_list = [x for x in os.listdir(export_dir)]
        for file_name in file_name_list:
          temp_file_path = os.path.join(export_dir, file_name)
          destination_file_path = os.path.join(template_path, file_name)
          shutil.move(temp_file_path, destination_file_path)
      except:
        raise
      finally:
        shutil.rmtree(export_dir)

    security.declareProtected( 'Import/Export objects', 'importAndReExportBusinessTemplateListFromPath' )
    def importAndReExportBusinessTemplateListFromPath(self, repository_list, REQUEST=None, **kw):
      """
        Migrate business templates to new format where files like .py or .html
        are exported seprately than the xml.
      """
      repository_list = filter(bool, repository_list)

      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)
        
      if len(repository_list) == 0 and REQUEST:
        ret_url = self.absolute_url()
        REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                  % (ret_url, 'No repository was defined'))
                                    
      for repository in repository_list:
        repository = repository.rstrip('\n')
        repository = repository.rstrip('\r')
        for business_template_id in os.listdir(repository):
          template_path = os.path.join(repository, business_template_id)
          if os.path.isfile(template_path):
            LOG(business_template_id,0,'is file, so it is skipped')
          else:
            if not os.path.exists((os.path.join(template_path, 'bt'))):
              LOG(business_template_id,0,'has no bt sub-folder, so it is skipped')
            else:
              self.activate(activity='SQLQueue').\
                importAndReExportBusinessTemplateFromPath(template_path)

    security.declareProtected( 'Import/Export objects', 'migrateBTToBP')
    def migrateBTToBP(self, template_path, REQUEST=None, **kw):
      """
        Migrate business template repository to Business Package repo.
        Business Package completely rely only on PathTemplateItem and to show
        the difference between both of them

        So, the steps should be:
        1. Install the business template which is going to be migrated
        2. Create a new Business Package with random id and title
        3. Add the path, build and export the template
        4. Remove the business template from the directory and add the business
        package there instead
        5. Change the ID and title of the business package
        6. Export the business package to the directory, leaving anything in
        the installed erp5 unchanged
      """
      import_template = self.download(url=template_path)
      if import_template.getPortalType == 'Business Package':
        LOG(import_template.getTitle(),0,'Already migrated')
        return

      export_dir = mkdtemp()

      installed_bt_list = self.getInstalledBusinessTemplatesList()
      installed_bt_title_list = [bt.title for bt in installed_bt_list]

      is_installed = False
      if import_template.getTitle() not in installed_bt_title_list:
        # Install the business template
        import_template.install(**kw)
        is_installed = True

      # Make list of object paths which needs to be added in the bp5
      # This can be decided by looping over every type of items we do have in
      # bt5 and checking if there have been any changes being made to it via this
      # bt5 installation or not.
      # For ex:
      # CatalogTempalteMethodItem, CatalogResultsKeyItem, etc. do make some
      # changes in erp5_mysql_innodb(by adding properties, by adding sub-objects),
      # so we need to add portal_catalog/erp5_mysql_innodb everytime we find
      # a bt5 making changes in any of these items.

      portal_path = self.getPortalObject()
      template_path_list = []
      property_path_list = []

      # For modules, we don't need to create path for the module
      module_list = import_template.getTemplateModuleIdList()
      template_path_list.extend(module_list)

      # For portal_types, we have to add path and subobjetcs
      portal_type_id_list = import_template.getTemplatePortalTypeIdList()
      portal_type_path_list = []
      for id in portal_type_id_list:
        portal_type_path_list.append('portal_types/'+id)
        portal_type_path_list.append('portal_types/'+id+'/**')
      template_path_list.extend(portal_type_path_list)

      # For categories, we create path for category objects as well as the subcategories
      category_list = import_template.getTemplateBaseCategoryList()
      category_path_list = []
      for base_category in category_list:
        category_path_list.append('portal_categories/'+base_category)
        category_path_list.append('portal_categories/'+base_category+'/**')
      template_path_list.extend(category_path_list)

      # For portal_skins, we export the folder
      portal_skin_list = import_template.getTemplateSkinIdList()
      portal_skin_path_list = []
      for skin in portal_skin_list:
        portal_skin_path_list.append('portal_skins/'+skin)
        portal_skin_path_list.append('portal_skins/'+skin+'/**')
      template_path_list.extend(portal_skin_path_list)

      # For workflow chains,
      # We have 2 objects in the Business Template design where we deal with
      # workflow objects, we deal with the installation separately:
      # 1. Workflow_id : We export the whole workflow objects in this case
      # 2. Portal Workflow chain: It is already being exported via portal_types
      # XXX: CHECK For 2, keeping in mind the migration of workflow would be merged
      # before this part where we make workflow_list as property of portal_type
      workflow_id_list = import_template.getTemplateWorkflowIdList()
      workflow_path_list = []
      for workflow in workflow_id_list:
        workflow_path_list.append('portal_workflow/' + workflow)
        workflow_path_list.append('portal_workflow/' + workflow + '/**')
      template_path_list.extend(workflow_path_list)

      # For paths, we add them directly to the path list
      template_path_list.extend(import_template.getTemplatePathList())

      # Catalog methods would be added as sub objects
      catalog_method_item_list = import_template.getTemplateCatalogMethodIdList()
      catalog_method_path_list = []
      for method in catalog_method_item_list:
        catalog_method_path_list.append('portal_catalog/' + method)
      template_path_list.extend(catalog_method_path_list)

      # For catalog objects, we check if there is any catalog object, and then
      # add catalog object also in the path if there is
      template_catalog_datetime_key   = import_template.getTemplateCatalogDatetimeKeyList()
      template_catalog_full_text_key  = import_template.getTemplateCatalogFullTextKeyList()
      template_catalog_keyword_key    = import_template.getTemplateCatalogKeywordKeyList()
      template_catalog_local_role_key = import_template.getTemplateCatalogLocalRoleKeyList()
      template_catalog_multivalue_key = import_template.getTemplateCatalogMultivalueKeyList()
      template_catalog_related_key    = import_template.getTemplateCatalogRelatedKeyList()
      template_catalog_request_key    = import_template.getTemplateCatalogRequestKeyList()
      template_catalog_result_key     = import_template.getTemplateCatalogResultKeyList()
      template_catalog_result_table   = import_template.getTemplateCatalogResultTableList()
      template_catalog_role_key       = import_template.getTemplateCatalogRoleKeyList()
      template_catalog_scriptable_key = import_template.getTemplateCatalogScriptableKeyList()
      template_catalog_search_key     = import_template.getTemplateCatalogSearchKeyList()
      template_catalog_security_uid_column = import_template.getTemplateCatalogSecurityUidColumnList()
      template_catalog_topic_key      = import_template.getTemplateCatalogTopicKeyList()

      catalog_property_list = [
        template_catalog_datetime_key,
        template_catalog_full_text_key,
        template_catalog_keyword_key,
        template_catalog_local_role_key,
        template_catalog_multivalue_key,
        template_catalog_related_key,
        template_catalog_request_key,
        template_catalog_result_key,
        template_catalog_result_table,
        template_catalog_role_key,
        template_catalog_scriptable_key,
        template_catalog_search_key,
        template_catalog_security_uid_column,
        template_catalog_topic_key,
        ]
      is_property_added = any(catalog_property_list)

      properties_removed = [
        'sql_catalog_datetime_search_keys_list',
        'sql_catalog_full_text_search_keys_list',
        'sql_catalog_keyword_search_keys_list',
        'sql_catalog_local_role_keys_list',
        'sql_catalog_multivalue_keys_list',
        'sql_catalog_related_keys_list',
        'sql_catalog_request_keys_list',
        'sql_search_result_keys_list',
        'sql_search_tables_list',
        'sql_catalog_role_keys_list',
        'sql_catalog_scriptable_keys_list',
        'sql_catalog_search_keys_list',
        'sql_catalog_security_uid_columns_list',
        'sql_catalog_topic_search_keys_list'
        ]

      removable_property = {}

      if is_property_added:
        if catalog_method_path_list:
          catalog_path = catalog_method_path_list[0].rsplit('/', 1)[0]
        else:
          catalog_path = 'portal_catalog/erp5_mysql_innodb'
        template_path_list.append(catalog_path)
        removable_property[catalog_path] = properties_removed
        for prop in properties_removed:
            property_path_list.append(catalog_path + ' | ' + prop)

      # Add these catalog items in the object_property instead of adding
      # dummy path item for them
      if import_template.getTitle() == 'erp5_mysql_innodb_catalog':
        template_path_list.extend('portal_catalog/erp5_mysql_innodb')

      # Add portal_property_sheets
      property_sheet_id_list = import_template.getTemplatePropertySheetIdList()
      property_sheet_path_list = []
      for property_sheet in property_sheet_id_list:
        property_sheet_path_list.append('portal_property_sheets/' + property_sheet)
        property_sheet_path_list.append('portal_property_sheets/' + property_sheet + '/**')
      template_path_list.extend(property_sheet_path_list)

      # Create new objects for business package
      bp5_package = self.newContent(
                                    portal_type='Business Package',
                                    title=import_template.getTitle()
                                    )

      bp5_package.edit(
        template_path_list=template_path_list,
        template_object_property_list=property_path_list
        )

      kw['removable_property'] = removable_property
      bp5_package.build(**kw)
      # Export the newly built business package to the export directory
      bp5_package.export(path=export_dir, local=True)
      if is_installed:
        import_template.uninstall()

    security.declareProtected( 'Import/Export objects', 'migrateBTListToBP')
    def migrateBTListToBP(self, repository_list, REQUEST=None, **kw):
      """
      Run migration for BT5 one by one in a given repository. This will be done
      via activities.
      """
      repository_list = filter(bool, repository_list)

      if REQUEST is None:
        REQUEST = getattr(self, 'REQUEST', None)

      if len(repository_list) == 0 and REQUEST:
        ret_url = self.absolute_url()
        REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                  % (ret_url, 'No repository was defined'))

      for repository in repository_list:
        repository = repository.rstrip('\n')
        repository = repository.rstrip('\r')
        for business_template_id in os.listdir(repository):
          template_path = os.path.join(repository, business_template_id)
          if os.path.isfile(template_path):
            LOG(business_template_id,0,'is file, so it is skipped')
          else:
            if not os.path.exists((os.path.join(template_path, 'bt'))):
              LOG(business_template_id,0,'has no bt sub-folder, so it is skipped')
            else:
              self.migrateBTToBP(template_path)
              #self.activate(activity='SQLQueue').\
              #  migrateBTToBP(template_path)

    security.declareProtected(Permissions.ManagePortal, 'getFilteredDiff')
    def getFilteredDiff(self, diff):
      """
      Filter the diff using python scripts
      """
      diff_file_object = DiffFile(diff)
      diff_block_list = diff_file_object.getModifiedBlockList()
      if diff_block_list:
        script_list = self.getDiffFilterScriptList()
        for block, line_tuple in diff_block_list:
          for script in script_list:
            if script(line_tuple[0], line_tuple[1]):
              diff_file_object.children.remove(block)
              break
      # XXX-Aurel : this method should return a text diff but
      # DiffFile does not provide yet such feature
      return diff_file_object

    security.declareProtected(Permissions.ManagePortal, 'diffObjectAsHTML')
    def diffObjectAsHTML(self, REQUEST, **kw):
      """
        Convert diff into a HTML format before reply
        This is compatible with ERP5VCS look and feel but
        it is preferred in future we use more difflib python library.
      """
      return DiffFile(self.diffObject(REQUEST, **kw)).toHTML()

    security.declareProtected(Permissions.ManagePortal, 'diffObject')
    def diffObject(self, REQUEST, **kw):
      """
        Make diff between two objects, whose paths are stored in values bt1
        and bt2 in the REQUEST object.
      """
      bt1_id = getattr(REQUEST, 'bt1', None)
      bt2_id = getattr(REQUEST, 'bt2', None)
      if bt1_id is not None and bt2_id is not None:
        bt1 = self._getOb(bt1_id)
        bt2 = self._getOb(bt2_id)
        if self.compareVersions(bt1.getVersion(), bt2.getVersion()) < 0:
          return bt2.diffObject(REQUEST, compare_with=bt1_id)
        else:
          return bt1.diffObject(REQUEST, compare_with=bt2_id)
      else:
        object_id = getattr(REQUEST, 'object_id', None)
        bt1_id = object_id.split('|')[0]
        bt1 = self._getOb(bt1_id)
        REQUEST.set('object_id', object_id.split('|')[1])
        return bt1.diffObject(REQUEST)

    security.declareProtected( 'Import/Export objects',
                               'updateRepositoryBusinessTemplateList' )

    def updateRepositoryBusinessTemplateList(self, repository_list,
        REQUEST=None, RESPONSE=None, genbt5list=0, **kw):
      """
        Update the information on Business Templates from repositories.

      For local repositories, genbt5list > 0 enables automatic generation
      of bt5list, without saving it on disk:
      - genbt5list=1: only if bt5list is missing
      - genbt5list>1: always
      """
      self.repository_dict = PersistentMapping()
      property_list = ('title', 'version', 'revision', 'description', 'license',
                       'dependency', 'test_dependency', 'provision', 'copyright',
                       'force_install')
      #LOG('updateRepositoryBusiessTemplateList', 0,
      #    'repository_list = %r' % (repository_list,))
      for repository in repository_list:
        urltype, url = splittype(repository)
        if WIN and urltype and '\\' in url:
          urltype = None
          url = repository
        if urltype and urltype != 'file':
          f = urlopen(repository + '/bt5list')
        else:
          url = os.path.expanduser(url)
          bt5list = os.path.join(url, 'bt5list')
          if genbt5list > os.path.exists(bt5list):
            f = generateInformation(url)
            f.seek(0)
          else:
            f = open(bt5list, 'rb')
        try:
          try:
            doc = parse(f)
          except ExpatError:
            if REQUEST is not None:
              psm = translateString('Invalid repository: ${repo}',
                                    mapping={'repo':repository})
              REQUEST.RESPONSE.redirect("%s?portal_status_message=%s"
                                       % (self.absolute_url(), psm))
              return
            else:
              raise RuntimeError, 'Invalid repository: %s' % repository
          try:
            property_dict_list = []
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
              property_dict['version'] = \
                  temp_property_dict.get('version', [''])[0]
              property_dict['revision'] = \
                  temp_property_dict.get('revision', [''])[0]
              property_dict['description'] = \
                  temp_property_dict.get('description', [''])[0]
              property_dict['license'] = \
                  temp_property_dict.get('license', [''])[0]
              property_dict['dependency_list'] = \
                  temp_property_dict.get('dependency', ())
              property_dict['test_dependency_list'] = \
                  temp_property_dict.get('test_dependency', ())
              property_dict['provision_list'] = \
                  temp_property_dict.get('provision', ())
              property_dict['copyright_list'] = \
                  temp_property_dict.get('copyright', ())
              property_dict['force_install'] = \
                  int(temp_property_dict.get('force_install', [0])[0])

              property_dict_list.append(property_dict)
          finally:
            doc.unlink()
        finally:
          f.close()

        #XXX: Hardcoding 'erp5_mysql_innodb_catalog' BP in the list
        bp_dict ={
          'copyright_list': ['Copyright (c) 2001-2017 Nexedi SA'],
          'dependency_list': [],
          'description': '',
          'force_install': 0,
          'id': 'erp5_mysql_innodb_catalog',
          'license': 'GPL',
          'provision_list': ['erp5_catalog'],
          'revision': '',
          'test_dependency_list': [],
          'title': 'erp5_mysql_innodb_catalog',
          'version': '1.0'}
        if repository.endswith('/bt5'):
          property_dict_list.append(bp_dict)

        self.repository_dict[repository] = tuple(property_dict_list)

      if REQUEST is not None:
        ret_url = self.absolute_url() + '/' + REQUEST.get('dialog_id', 'view')
        psm = translateString("Business templates updated successfully.")
        REQUEST.RESPONSE.redirect("%s?cancel_url=%s&portal_status_message=%s&dialog_category=object_exchange&selection_name=business_template_selection"
                                  % (ret_url, REQUEST.form.get('cancel_url', ''), psm))

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRepositoryList' )
    def getRepositoryList(self):
      """
        Get the list of repositories.
      """
      return self.repository_dict.keys()

    security.declarePublic( 'decodeRepositoryBusinessTemplateUid' )
    def decodeRepositoryBusinessTemplateUid(self, uid):
      """
        Decode the uid of a business template from a repository.
        Return a repository and an id.
      """
      return cPickle.loads(b64decode(uid))

    security.declarePublic( 'encodeRepositoryBusinessTemplateUid' )
    def encodeRepositoryBusinessTemplateUid(self, repository, id):
      """
        encode the repository and the id of a business template.
        Return an uid.
      """
      return b64encode(cPickle.dumps((repository, id)))

    security.declarePublic('compareVersionStrings')
    def compareVersionStrings(self, version, comparing_string):
      """
       comparing_string is like "<= 0.2" | "operator version"
       operators supported: '<=', '<' or '<<', '>' or '>>', '>=', '=' or '=='
      """
      operator, comp_version = comparing_string.split(' ')
      diff_version = self.compareVersions(version, comp_version)
      if operator == '<' or operator == '<<':
        if diff_version < 0:
          return True;
        return False;
      if operator == '<=':
        if diff_version <= 0:
          return True;
        return False;
      if operator == '>' or operator == '>>':
        if diff_version > 0:
          return True;
        return False;
      if operator == '>=':
        if diff_version >= 0:
          return True;
        return False;
      if operator == '=' or operator == '==':
        if diff_version == 0:
          return True;
        return False;
      raise UnsupportedComparingOperator, 'Unsupported comparing operator: %s'%(operator,)

    security.declareProtected(Permissions.AccessContentsInformation,
                              'IsOneProviderInstalled')
    def IsOneProviderInstalled(self, title):
      """
        return true if a business template that
        provides the bt with the given title is
        installed
      """
      installed_bt_list = self.getInstalledBusinessTemplatesList()
      for bt in installed_bt_list:
        provision_list = bt.getProvisionList()
        if title in provision_list:
          return True
      return False

    security.declareProtected(Permissions.AccessContentsInformation,
                               'getLastestBTOnRepos')
    def getLastestBTOnRepos(self, title, version_restriction=None):
      """
       It's possible we have different versions of the same BT
       available on various repositories or on the same repository.
       This function returns the latest one that meet the version_restriction
       (i.e "<= 0.2") in the following form :
       tuple (repository, id)
      """
      result = None
      for repository, property_dict_list in self.repository_dict.items():
        for property_dict in property_dict_list:
          provision_list = property_dict.get('provision_list', [])
          if title in provision_list:
            raise BusinessTemplateIsMeta, 'Business Template %s is provided by another one'%(title,)
          if title == property_dict['title']:
            if (version_restriction is None) or (self.compareVersionStrings(property_dict['version'], version_restriction)):
              if (result is None) or (self.compareVersions(property_dict['version'], result[2]) > 0):
                result = (repository, property_dict['id'], property_dict['version'])
      if result is not None:
        return (result[0], result[1])
      else:
        raise BusinessTemplateUnknownError, 'Business Template %s (%s) could not be found in the repositories'%(title, version_restriction or '')

    security.declareProtected(Permissions.AccessContentsInformation,
                              'getProviderList')
    def getProviderList(self, title):
      """
       return a list of business templates that provides
       the given business template
      """
      result_list = []
      for repository, property_dict_list in self.repository_dict.items():
        for property_dict in property_dict_list:
          provision_list = property_dict['provision_list']
          if (title in provision_list) and (property_dict['title'] not in result_list):
            result_list.append(property_dict['title'])
      return result_list

    security.declareProtected(Permissions.AccessContentsInformation,
                               'getDependencyList')
    @transactional_cached(lambda self, bt, with_test_dependency_list=False:
                          (bt, with_test_dependency_list))
    def getDependencyList(self, bt, with_test_dependency_list=False):
      """
       Return the list of missing dependencies for a business
       template, given a tuple : (repository, id)
      """
      # We do not take into consideration the dependencies
      # for meta business templates
      if bt[0] != 'meta':
        result_list = []
        for repository, property_dict_list in self.repository_dict.items():
          if repository == bt[0]:
            for property_dict in property_dict_list:
              if property_dict['id'] == bt[1]:
                dependency_list = [q.strip() for q in
                                   property_dict['dependency_list'] if q]
                if with_test_dependency_list:
                  dependency_list.extend([q.strip() for q in
                                          property_dict['test_dependency_list'] if q])
                for dependency_couple in dependency_list:
                  # dependency_couple is like "erp5_xhtml_style (>= 0.2)"
                  dependency_couple_list = dependency_couple.split(' ', 1)
                  dependency = dependency_couple_list[0]
                  version_restriction = None
                  if len(dependency_couple_list) > 1:
                    version_restriction = dependency_couple_list[1]
                    if version_restriction.startswith('('):
                      # Something like "(>= 1.0rc6)".
                      version_restriction = version_restriction[1:-1]
                  require_update = False
                  if dependency not in result_list:
                    # Get the lastest version of the dependency on the
                    # repository that meet the version restriction
                    provider_installed = False
                    bt_dep = None
                    try:
                      bt_dep = self.getLastestBTOnRepos(dependency, version_restriction)
                    except BusinessTemplateUnknownError:
                      raise BusinessTemplateMissingDependency, 'While analysing %s the following dependency could not be satisfied: %s (%s)\nReason: Business Template could not be found in the repositories'%(bt[1], dependency, version_restriction or '')
                    except BusinessTemplateIsMeta:
                      provider_list = self.getProviderList(dependency)
                      for provider in provider_list:
                        if self.getInstalledBusinessTemplate(provider) is not None:
                          bt_dep = self.getLastestBTOnRepos(provider)
                          break
                      if bt_dep is None:
                        bt_dep = ('meta', dependency)
                    sub_dep_list = self.getDependencyList(bt_dep)
                    for sub_dep in sub_dep_list:
                      if sub_dep not in result_list:
                        result_list.append(sub_dep)
                    result_list.append(bt_dep)
                return result_list
        raise BusinessTemplateUnknownError, 'The Business Template %s could not be found on repository %s'%(bt[1], bt[0])
      return []

    security.declareProtected(Permissions.ManagePortal,
                              'findProviderInBTList')
    def findProviderInBTList(self, provider_list, bt_list):
      """
       Find one provider in provider_list which is present in
       bt_list and returns the found tuple (repository, id)
       in bt_list.
      """
      for provider in provider_list:
        for repository, id in bt_list:
          if id.startswith(provider):
            return (repository, id)
      raise BusinessTemplateUnknownError, 'Provider not found in bt_list'

    security.declareProtected(Permissions.AccessContentsInformation,
                              'sortBusinessTemplateList')
    def sortBusinessTemplateList(self, bt_list):
      """
      Sort a list of business template in repositories according to
      dependencies

      bt_list : list of (repository, id) tuple.
      """
      sorted_bt_list = []
      title_id_mapping = {}

      # Calculate the dependency graph
      dependency_dict = {}
      provition_dict = {}
      repository_dict = {}
      undependent_list = []

      for repository, bt_id in bt_list:
        bt = [x for x in self.repository_dict[repository] \
              if x['id'] == bt_id][0]
        bt_title = bt['title']
        repository_dict[bt_title] = repository
        dependency_dict[bt_title] = [x.split(' ')[0] for x in bt['dependency_list']]
        title_id_mapping[bt_title] = bt_id
        if not dependency_dict[bt_title]:
          del dependency_dict[bt_title]
        for provision in list(bt['provision_list']):
          provition_dict[provision] = bt_title
        undependent_list.append(bt_title)

      # Calculate the reverse dependency graph
      reverse_dependency_dict = {}
      for bt_id, dependency_id_list in dependency_dict.items():
        update_dependency_id_list = []
        for dependency_id in dependency_id_list:

          # Get ride of provision id
          if dependency_id in provition_dict:
            dependency_id = provition_dict[dependency_id]
          update_dependency_id_list.append(dependency_id)

          # Fill incoming edge dict
          if dependency_id in reverse_dependency_dict:
            reverse_dependency_dict[dependency_id].append(bt_id)
          else:
            reverse_dependency_dict[dependency_id] = [bt_id]

          # Remove from free node list
          try:
            undependent_list.remove(dependency_id)
          except ValueError:
            pass

        dependency_dict[bt_id] = update_dependency_id_list

      # Let's sort the bt5!
      while undependent_list:
        bt_id = undependent_list.pop(0)
        if bt_id not in repository_dict:
          continue
        sorted_bt_list.insert(0, (repository_dict[bt_id], title_id_mapping[bt_id]))
        for dependency_id in dependency_dict.get(bt_id, []):

          local_dependency_list = reverse_dependency_dict[dependency_id]
          local_dependency_list.remove(bt_id)
          if local_dependency_list:
            reverse_dependency_dict[dependency_id] = local_dependency_list
          else:
            del reverse_dependency_dict[dependency_id]
            undependent_list.append(dependency_id)

      if len(sorted_bt_list) != len(bt_list):
        raise NotImplementedError, \
          "Circular dependencies on %s" % reverse_dependency_dict.keys()
      else:
        return sorted_bt_list

    security.declareProtected(Permissions.AccessContentsInformation,
                              'sortDownloadedBusinessTemplateList')
    def sortDownloadedBusinessTemplateList(self, id_list):
      """
      Sort a list of already downloaded business templates according to
      dependencies

      id_list : list of business template's id in portal_templates.
      """
      def isDepend(a, b):
        # return True if a depends on b.
        dependency_list = [x.split(' ')[0] for x in a.getDependencyList()]
        provision_list = list(b.getProvisionList()) + [b.getTitle()]
        for i in provision_list:
          if i in dependency_list:
            return True
          return False

      sorted_bt_list = []
      for bt_id in id_list:
        bt = self._getOb(bt_id)
        for j in range(len(sorted_bt_list)):
          if isDepend(sorted_bt_list[j], bt):
            sorted_bt_list.insert(j, bt)
            break
        else:
           sorted_bt_list.append(bt)
      sorted_bt_list = [bt.getId() for bt in sorted_bt_list]
      return sorted_bt_list

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getRepositoryBusinessTemplateList' )
    def getRepositoryBusinessTemplateList(self, update_only=False,
             template_list=None, **kw):
      """Get the list of Business Templates in repositories.

         update_only: return only bt that needs to be updated
         template_list: only returns bt within the given list
      """
      from Products.ERP5Type.Document import newTempBusinessTemplate
      result_list = []
      template_set = None
      if template_list is not None:
        template_set = set(template_list)

      template_item_list = []
      # First of all, filter Business Templates in repositories.
      template_item_dict = {}
      for repository, property_dict_list in self.repository_dict.items():
        for property_dict in property_dict_list:
          title = property_dict['title']
          if template_set and not(title in template_set):
            continue
          if not update_only:
            template_item_list.append((repository, property_dict))
          else:
            if title not in template_item_dict:
              # If this is the first time to see this business template,
              # insert it.
              template_item_dict[title] = (repository, property_dict)
            else:
              # If this business template has been seen before, insert it only
              # if this business template is newer.
              previous_repository, previous_property_dict = \
                  template_item_dict[title]
              if self.compareVersions(previous_property_dict['version'],
                                      property_dict['version']) < 0:
                template_item_dict[title] = (repository, property_dict)
      # Next, select only updated business templates.
      if update_only:
        for repository, property_dict in template_item_dict.values():
          installed_bt = \
              self.getInstalledBusinessTemplate(property_dict['title'], strict=True)
          if installed_bt is not None:
            diff_version = self.compareVersions(installed_bt.getVersion(),
                                                property_dict['version'])
            if diff_version < 0:
              template_item_list.append((repository, property_dict))
            elif diff_version == 0 \
                  and property_dict['revision'] \
                  and installed_bt.getRevision() != property_dict['revision']:
                    template_item_list.append((repository, property_dict))
          elif template_list is not None:
            template_item_list.append((repository, property_dict))

      # Create temporary Business Template objects for displaying.
      for repository, property_dict in template_item_list:
        property_dict = property_dict.copy()
        id = filename = property_dict.pop('id')
        installed_bt = \
            self.getInstalledBusinessTemplate(property_dict['title'])
        if installed_bt is not None:
          installed_version = installed_bt.getVersion()
          installed_revision = installed_bt.getShortRevision()
          if installed_bt.getRevision() == property_dict['revision']:
            version_state = 'present'
          else:
            version_state = 'different'
        else:
          installed_version = ''
          installed_revision = ''
          version_state = 'new'
        uid = self.encodeRepositoryBusinessTemplateUid(repository, id)
        obj = newTempBusinessTemplate(self, 'temp_' + uid,
                                      version_state = version_state,
                                      version_state_title=version_state.title(),
                                      filename = filename,
                                      installed_version = installed_version,
                                      installed_revision = installed_revision,
                                      repository = repository, **property_dict)
        obj.setUid(uid)
        result_list.append(obj)
      result_list.sort(key=lambda x: x.getTitle())
      return result_list

    security.declareProtected( Permissions.AccessContentsInformation,
                               'getUpdatedRepositoryBusinessTemplateList' )
    def getUpdatedRepositoryBusinessTemplateList(self, **kw):
      """Get the list of updated Business Templates in repositories.
      """
      #LOG('getUpdatedRepositoryBusinessTemplateList', 0, 'kw = %r' % (kw,))
      return self.getRepositoryBusinessTemplateList(update_only=True, **kw)

    security.declarePublic('compareVersions')
    def compareVersions(self, version1, version2):
      """
        Return negative if version1 < version2, 0 if version1 == version2,
        positive if version1 > version2.

      Here is the algorithm:
        - Non-alphanumeric characters are not significant, besides the function
          of delimiters.
        - If a level of a version number is missing, it is assumed to be zero.
        - An alphabetical character is less than any numerical value.
        - Numerical values are compared as integers.

      This implements the following predicates:
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

    def _getBusinessTemplateUrlDict(self):
      business_template_url_dict = {}
      for bt in self.getRepositoryBusinessTemplateList():
        url, name = self.decodeRepositoryBusinessTemplateUid(bt.getUid())
        if name.endswith('.bt5'):
          name = name[:-4]
        business_template_url_dict[name] = {
          'url': '%s/%s' % (url, bt.filename),
          'revision': bt.getRevision()
          }
      return business_template_url_dict

    security.declareProtected(Permissions.ManagePortal,
        'installBusinessTemplatesFromRepositories')
    def installBusinessTemplatesFromRepositories(self, *args, **kw):
      """Deprecated.
      """
      DeprecationWarning('installBusinessTemplatesFromRepositories is deprecated; Use self.installBusinessTemplateListFromRepository instead.', DeprecationWarning)
      return self.installBusinessTemplateListFromRepository(*args, **kw)

    security.declareProtected(Permissions.ManagePortal,
         'resolveBusinessTemplateListDependency')
    def resolveBusinessTemplateListDependency(self,
                                              template_title_list,
                                              with_test_dependency_list=False):
      available_bt5_list = self.getRepositoryBusinessTemplateList()

      template_title_list = set(template_title_list)
      installed_bt5_title_list = self.getInstalledBusinessTemplateTitleList()

      bt5_set = set()
      for available_bt5 in available_bt5_list:
        if available_bt5.title in template_title_list:
          template_title_list.remove(available_bt5.title)
          bt5 = self.decodeRepositoryBusinessTemplateUid(available_bt5.uid)
          bt5_set.add(bt5)
          meta_dependency_set = set()
          for dep_repository, dep_id in self.getDependencyList(
              bt5,
              with_test_dependency_list):
            if dep_repository != 'meta':
              bt5_set.add((dep_repository, dep_id))
            else:
              meta_dependency_set.add((dep_repository, dep_id))
          for dep_repository, dep_id in meta_dependency_set:
            provider_list = self.getProviderList(dep_id)
            provider_installed = False
            provider_title = None
            for provider in provider_list:
              if provider in [i[1].replace(".bt5", "") for i in bt5_set] or \
                    provider in installed_bt5_title_list or \
                    provider in template_title_list:
                provider_title = provider
                for candidate in available_bt5_list:
                  if candidate.title == provider:
                    bt5_set.add(\
                      self.decodeRepositoryBusinessTemplateUid(
                          candidate.uid))
                    break
                break
            if provider_title is None and len(provider_list) == 1:
              provider_title = provider_list[0]
            LOG('resolveBT, provider_title', 0, provider_title)
            if provider_title:
              for candidate in available_bt5_list:
                if candidate.title == provider_title:
                  bt5_set.add(\
                    self.decodeRepositoryBusinessTemplateUid(
                        candidate.uid))
                  break
            else:
              raise BusinessTemplateMissingDependency,\
                "Unable to resolve dependencies for %s, options are %s" \
                    % (dep_id, provider_list)

      if len(template_title_list) > 0:
         raise BusinessTemplateUnknownError, 'The Business Template %s could not be found on repositories %s' % \
             (list(template_title_list), self.getRepositoryList())
      return self.sortBusinessTemplateList(list(bt5_set))

    security.declareProtected(Permissions.ManagePortal,
        'installBusinessTemplateListFromRepository')
    def installBusinessTemplateListFromRepository(self, template_list,
        only_different=True, update_catalog=False, activate=False,
        install_dependency=False):
      """Installs template_list from configured repositories by default only newest"""
      # XXX-Luke: This method could replace
      # TemplateTool_installRepositoryBusinessTemplateList while still being
      # possible to reuse by external callers

      operation_log = []
      resolved_template_list = self.resolveBusinessTemplateListDependency(
                   template_list)
      installed_bt5_dict = {x.getTitle(): x.getRevision()
        for x in self.getInstalledBusinessTemplateList()}
      if only_different:
        template_url_dict = self._getBusinessTemplateUrlDict()

      def checkAvailability(bt_title):
        return bt_title in template_list or bt_title in installed_bt5_dict
      missing_dependency_list = [i for i in resolved_template_list
                                 if not checkAvailability(i[1].replace(".bt5", ""))]

      if not install_dependency and len(missing_dependency_list) > 0:
        raise BusinessTemplateMissingDependency,\
            "Impossible to install, please install the following dependencies before: %s" \
            % [x[1] for x in missing_dependency_list]

      activate_kw =  dict(activity="SQLQueue", tag="start_%s" % (time.time()))
      for repository, bt_id in resolved_template_list:
        if only_different:
          bt = template_url_dict.get(bt_id)
          if bt is not None and bt['revision'] == installed_bt5_dict.get(bt_id):
            continue
        bt_url = '%s/%s' % (repository, bt_id)
        param_dict = dict(download_url=bt_url, only_different=only_different)
        param_dict["update_catalog"] = update_catalog

        if activate:
          self.activate(**activate_kw).\
                updateBusinessTemplateFromUrl(**param_dict)
          activate_kw["after_tag"] = activate_kw["tag"]
          activate_kw["tag"] = bt_id
          operation_log.append('Installed %s using activities' % (bt_id))
        else:
          document = self.updateBusinessTemplateFromUrl(**param_dict)
          operation_log.append('Installed %s with revision %s' % (
              document.getTitle(), document.getShortRevision()))

      return operation_log

    security.declareProtected(Permissions.ManagePortal,
            'updateBusinessTemplateFromUrl')
    def updateBusinessTemplateFromUrl(self, download_url, id=None,
                                         keep_original_list=None,
                                         before_triggered_bt5_id_list=None,
                                         after_triggered_bt5_id_list=None,
                                         update_catalog=False,
                                         reinstall=False,
                                         active_process=None,
                                         force_keep_list=None,
                                         only_different=True):
      """
        This method download and install a bt5, from a URL.

        keep_original_list can be used to make paths not touched at all

        force_keep_list can be used to force path to be modified or removed
        even if template system proposes not touching it
      """
      if keep_original_list is None:
        keep_original_list = []
      if before_triggered_bt5_id_list is None:
        before_triggered_bt5_id_list = []
      if after_triggered_bt5_id_list is None:
        after_triggered_bt5_id_list = []
      if force_keep_list is None:
        force_keep_list = []
      if active_process is None:
        installed_dict = {}
        def log(msg):
          LOG('TemplateTool.updateBusinessTemplateFromUrl', INFO, msg)
      else:
        active_process = self.unrestrictedTraverse(active_process)
        if getattr(aq_base(active_process), 'installed_dict', None) is None:
          active_process.installed_dict = PersistentMapping()
        installed_dict = active_process.installed_dict
        message_list = []
        log = message_list.append

      log("Installing %s ..." % download_url)
      imported_bt5 = self.download(url = download_url, id = id)
      bt_title = imported_bt5.getTitle()

      if reinstall:
        install_kw = None
      else:
        if only_different:
          previous_bt5 = self.getInstalledBusinessTemplate(bt_title)
          if previous_bt5 and \
             imported_bt5.getRevision() == previous_bt5.getRevision():
            log("%s is already installed with revision %s"
                % (bt_title, imported_bt5.getShortRevision()))
            return imported_bt5

        install_kw = {}
        for listbox_line in imported_bt5.BusinessTemplate_getModifiedObject():
          item = listbox_line.object_id
          state = listbox_line.object_state
          if state.startswith('Removed'):
            # The following condition could not be used to automatically decide
            # if an item must be kept or not. For example, this would not work
            # for items installed by PortalTypeWorkflowChainTemplateItem.
            maybe_moved = installed_dict.get(listbox_line.object_id, '')
            log('%s: %s%s' % (state, item,
              maybe_moved and ' (moved to %s ?)' % maybe_moved))
          else:
            installed_dict[item] = bt_title

          # For actions which suggest that item shall be kept and item is not
          # explicitely forced, keep the default -- do nothing
          # XXX: 'force_keep_list' variable is misnamed.
          should_keep = item not in force_keep_list and state in (
            'Modified but should be kept', 'Removed but should be kept')
          # If item is forced to be untouched, do not touch it
          if item in keep_original_list or should_keep:
            if not should_keep:
              log('Item %r is in force_keep_list and keep_original_list,'
                  ' as keep_original_list has precedence item is NOT MODIFIED'
                  % item)
            install_kw[item] = 'nothing'
          else:
            install_kw[item] = listbox_line.choice_item_list[0][1]

      # Run before script list
      for before_triggered_bt5_id in before_triggered_bt5_id_list:
        log('Execute %r' % before_triggered_bt5_id)
        imported_bt5.unrestrictedTraverse(before_triggered_bt5_id)()

      # Note: CATALOG_UPDATABLE should only be used in eceptional cases
      #       where the caller installs several bts and does not know
      #       which ones need to update catalog. Handling catalog should be
      #       usually done at upgrader level.
      if update_catalog is CATALOG_UPDATABLE and install_kw != {}:
        update_catalog = imported_bt5.isCatalogUpdatable()

      imported_bt5.install(object_to_update=install_kw,
                           update_catalog=update_catalog)

      # Run After script list
      for after_triggered_bt5_id in after_triggered_bt5_id_list:
        log('Execute %r' % after_triggered_bt5_id)
        imported_bt5.unrestrictedTraverse(after_triggered_bt5_id)()
      if active_process is not None:
        active_process.postResult(ActiveResult(
          '%03u. %s' % (len(active_process.getResultList()) + 1, bt_title),
          detail='\n'.join(message_list)))
      else:
        log("Updated %s from %s" % (bt_title, download_url))

      return imported_bt5

    security.declareProtected(Permissions.ManagePortal,
            'installMultipleBusinessPackage')
    def installMultipleBusinessPackage(self, bp5_list):
      """
      Install multiple Business Package at the same time
      """
      # XXX: Compare before calling install on path object property items
      from Products.ERP5.Document.BusinessPackage import \
                    ObjectPropertyTemplatePackageItem, PathTemplatePackageItem

      final_path_item = bp5_list[0]._path_item
      final_prop_item = bp5_list[0]._object_property_item

      for bp5 in bp5_list:
        final_path_item += bp5._path_item
        final_prop_item += bp5._object_property_item

      final_path_item.install()
      final_prop_item.install()

    security.declareProtected(Permissions.ManagePortal,
            'combineMultipleBusinessManager')
    def combineMultipleBusinessManager(self, bm_list):
      """
      Combines multiple BM to form single flattened BM
      """
      new_bm_list = bm_list[:]
      # Create the final Business Manager
      if len(bm_list) == 1:
        combinedBM = new_bm_list[0]
      else:
        # Better to create a new Business Manager than to make change
        # in the installed one
        combinedBM = self.newContent(portal_type='Business Manager')
        combinedBM.build()
        # Summation should also consider arithmetic on the Business Item(s)
        # having same path and layer and combine them.

        new_bm_list.insert(0, combinedBM)
        combinedBM = reduce(lambda x, y: x+y, new_bm_list)

      # XXX: We are missing the part of creating installed_BM for all the BM
      # we have in bm_list, because this would be needed in case we build
      # Business Manager again.

      # Reduce the final Business Manager
      combinedBM.reduceBusinessManager()
      # combinedBM.flattenBusinessManager()

      return combinedBM

    security.declareProtected(Permissions.ManagePortal,
            'installBusinessManager')
    def installBusinessManager(self, bm):
      """
      Run installation on flattened Business Manager
      """
      if bm.getStatus() == 'reduced':
        # Run install on separate Business Item one by one
        for path_item in bm._path_item_list:
          path_item.install(self)
      else:
        raise ValueError, 'Business Manager not flattened, cannot install'

    security.declareProtected(Permissions.ManagePortal,
            'installMultipleBusinessManager')
    def installMultipleBusinessManager(self, bm_list):
      """
      Run installation on flattened Business Manager
      """
      final_bm_list = []
      installed_bm_list = self.getInstalledBusinessManagerList()
      installed_bm_title_list = self.getInstalledBusinessManagerTitleList()
      installed_bm_dict = dict(zip(installed_bm_title_list, installed_bm_list))
      for bm in bm_list:

        if bm.title in installed_bm_title_list:

          # Not very suitable way to look for already installed BM
          installed_bm = installed_bm_dict[bm.title]
          # XXX: Installed BM is already reduced. For the Business Manager we
          # are planning to install, we should reduce it also.
          compared_bm = self.compareBusinessManager(bm, installed_bm)
          final_bm_list.append(compared_bm)

        else:
          final_bm_list.append(bm)

      combinedBM = self.combineMultipleBusinessManager(final_bm_list)
      self.installBusinessManager(combinedBM)

      # Explicilty change the status of Business Manager which are installed
      for bm in bm_list:
        bm.setStatus('installed')

    def getInstalledBusinessManagerList(self):
      bm_list = self.objectValues(portal_type='Business Manager')
      installed_bm_list = [bm for bm in bm_list if bm.getStatus() == 'installed']
      return installed_bm_list

    def getInstalledBusinessManagerTitleList(self):
      installed_bm_list = self.getInstalledBusinessManagerList()
      if not len(installed_bm_list):
        return []
      installed_bm_title_list = [bm.title for bm in installed_bm_list]
      return installed_bm_title_list

    security.declareProtected(Permissions.ManagePortal,
            'compareMultipleBusinessManager')
    def compareBusinessManager(self, new_bm, old_bm):
      """
      Compare two business manager and return a new Business manager based on
      the difference. This is specially required to compare two versions of
      Business Manager(s).
      """
      compared_bm = new_bm-old_bm
      return compared_bm

    security.declareProtected(Permissions.ManagePortal,
            'getBusinessTemplateUrl')
    def getBusinessTemplateUrl(self, base_url_list, bt5_title):
      """
        This method verify if the business template are available
        into one url (repository).
      """
      if base_url_list is None:
        base_url_list = self.getRepositoryList()
      # This list could be preconfigured at some properties or
      # at preferences.
      for base_url in base_url_list:
        url = "%s/%s" % (base_url, bt5_title)
        if base_url == "INSTANCE_HOME_REPOSITORY":
          url = "file://%s/bt5/%s" % (getConfiguration().instancehome,
                                      bt5_title)
          LOG('ERP5', INFO, "TemplateTool: INSTANCE_HOME_REPOSITORY is %s." \
              % url)
        try:
          urllib2.urlopen(url)
          return url
        except (urllib2.HTTPError, OSError):
          # XXX Try again with ".bt5" in case the folder format be used
          # Instead tgz one.
          url = "%s.bt5" % url
          try:
            urllib2.urlopen(url)
            return url
          except (urllib2.HTTPError, OSError):
            pass
      LOG('ERP5', INFO, 'TemplateTool: %s was not found into the url list: '
                        '%s.' % (bt5_title, base_url_list))
      return None

    security.declareProtected(Permissions.ManagePortal,
        'upgradeSite')
    def upgradeSite(self, bt5_list, deprecated_after_script_dict=None,
                    deprecated_reinstall_set=None, dry_run=False,
                    delete_orphaned=False,
                    keep_bt5_id_set=[],
                    update_catalog=False):
      """
      Upgrade many business templates at a time. bt5_list should
      contains only final business templates, then all dependencies
      are calculated, and missing business templates will be added,
      old business templates will be updated, and orphelin business
      templates will be deleted

      keep_bt5_id_set: business template that should not be deleted.
                       This is useful if we want to keep an old business
                       template without updating it and without removing it

      deprecated_reinstall_set: this parameter is obsolete, please set
                                force_install property at business template level
                                It list all business templates who needs
                                reinstall

      update_catalog: handling catalog should be handled outside upgradeSite.
                      This option only exists for the case where it is not
                      known which bts need catalog update. In this case one
                      can pass CATALOG_UPDATABLE which will be propagated to
                      updateBusinessTemplateFromUrl.
      """
      # make sure that we updated information on repository
      self.updateRepositoryBusinessTemplateList(self.getRepositoryList())
      # do upgrade
      message_list = []
      deprecated_reinstall_set = deprecated_reinstall_set or set()
      def append(message):
        message_list.append(message)
        LOG('upgradeSite', 0, message)
      dependency_list = [x[1] for x in \
        self.resolveBusinessTemplateListDependency(bt5_list)]
      update_bt5_list = self.getRepositoryBusinessTemplateList(
        template_list=dependency_list)
      update_bt5_list.sort(key=lambda x: dependency_list.index(x.title))
      for bt5 in update_bt5_list:
        reinstall = bt5.title in deprecated_reinstall_set or bt5.force_install
        if (not(reinstall) and bt5.version_state == 'present') or \
            bt5.title in keep_bt5_id_set:
          continue
        append("Update %s business template in state %s%s" % \
          (bt5.title, bt5.version_state, (reinstall and ' (reinstall)') or ''))
        if not(dry_run):
          bt5_url = "%s/%s" % (bt5.repository, bt5.title)
          self.updateBusinessTemplateFromUrl(bt5_url, reinstall=reinstall,
                                             update_catalog=update_catalog)
      if delete_orphaned:
        if keep_bt5_id_set is None:
          keep_bt5_id_set = set()
        to_remove_bt5_list = [x for x in self.getInstalledBusinessTemplateList()
                              if x.title not in dependency_list]
        sorted_to_remove_bt5_id_list = self.sortDownloadedBusinessTemplateList(
                                  [x.id for x in to_remove_bt5_list])
        sorted_to_remove_bt5_id_list.reverse()
        to_remove_bt5_list.sort(
          key=lambda x: sorted_to_remove_bt5_id_list.index(x.id))
        for bt in to_remove_bt5_list:
          if bt.title in keep_bt5_id_set:
            continue
          append("Uninstall business template %s" % bt.title)
          if not(dry_run):
            # XXX Here is missing parameters to really remove stuff
            bt.uninstall()

      return message_list

InitializeClass(TemplateTool)
