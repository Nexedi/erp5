# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
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

import os
import shutil
import tempfile
import inspect
import traceback
from pprint import pformat

from Products.CMFCore.utils import UniqueObject

import OFS
import transaction
from cStringIO import StringIO
from zExceptions import BadRequest
from zExceptions import Unauthorized
from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from App.config import getConfiguration
from App import RefreshFuncs
from Shared.DC.ZRDB.TM import TM
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.ERP5Type import Permissions
from Products.ERP5Type import _dtmldir
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Core.Folder import OFS_HANDLER

from Products.ERP5Type.Utils import readLocalPropertySheet, writeLocalPropertySheet, getLocalPropertySheetList
from Products.ERP5Type.Utils import readLocalExtension, writeLocalExtension, getLocalExtensionList
from Products.ERP5Type.Utils import readLocalTest, writeLocalTest, getLocalTestList
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, getLocalDocumentList
from Products.ERP5Type.Utils import readLocalConstraint, writeLocalConstraint, getLocalConstraintList
from Products.ERP5Type.InitGenerator import getProductDocumentPathList

from Products.ERP5Type.Base import newTempDocumentationHelper

from Products.ERP5Type import allowClassTool
from DateTime import DateTime

import Products

from zLOG import LOG, WARNING

global_stream = None

"""
  ClassTool allows to create classes from the ZMI using code templates.
  ZMI-created classes can then be edited again.
  All classes can also be reloaded from the ZMI to avoid restarting zope.

  ClassTool is a high potential security risk for a website, it is hence
  disabled by default by using a dummy ClassTool.
  See Products.ERP5Type.allowClassTool for the way to enable full-featured
  ClassTool.
"""

COPYRIGHT = "Copyright (c) 2002-%s Nexedi SA and Contributors. All Rights Reserved." % DateTime().year()
LOCAL_DIRECTORY_LIST = ('Document', 'Extensions', 'Constraint', 'tests', 'PropertySheet')
ATTRIBUTE_INSPECTION_SKIP_LIST = '''
__implemented__
__provides__
'''.strip().splitlines()


class ClassToolMixIn:
  """
    Provides common methods which portal_classes should always provide
  """
  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.ManagePortal, 'getPropertySheetPropertyIdList')
  def getPropertySheetPropertyIdList(self):
    """
    Returns the sorted list of property IDs defined in the current instance
    in global and local property sheets
    """
    property_sheet_name_list = Products.ERP5Type.PropertySheet.__dict__.keys()
    property_sheet_name_list = filter(lambda k: not k.startswith('__'),  property_sheet_name_list)
    result_dict = {}
    for property_sheet_name in property_sheet_name_list:
      for property in getattr(getattr(Products.ERP5Type.PropertySheet, property_sheet_name),
                              '_properties', ()):
        result_dict[property['id']] = None
        if property.has_key('storage_id'):
          result_dict[property['storage_id']] = None
    result = result_dict.keys()
    result.sort()
    return result

  security.declareProtected(Permissions.ManagePortal, 'getDocumentationHelper')
  def getDocumentationHelper(self, class_name, uri, REQUEST=None):
    """
    Builds a documentation helper class with given URI and type
    """
    from Products.ERP5Type import DocumentationHelper
    class_object = getattr(DocumentationHelper, class_name)
    helper = class_object(uri).__of__(self)
    if REQUEST is not None:
      return helper.view()
    return helper

if allowClassTool():

  class TemporaryInstanceHome(TM):
    _finalize = None
    path = None

    def __init__(self):
      pass

    def getPath(self):
      return self.path

    def _begin(self):
      self.path = tempfile.mkdtemp()
      try:
        for name in LOCAL_DIRECTORY_LIST:
          os.mkdir(os.path.join(self.path, name))
      except:
        shutil.rmtree(self.path)
        raise

    def _finish(self):
      instance_home = getConfiguration().instancehome
      for name in LOCAL_DIRECTORY_LIST:
        source_dir = os.path.join(self.path, name)
        destination_dir = os.path.join(instance_home, name)
        for fname in os.listdir(source_dir):
          source_file = os.path.join(source_dir, fname)
          destination_file = os.path.join(destination_dir, fname)
          try:
            os.remove(destination_file)
          except OSError:
            pass
          shutil.move(source_file, destination_file)
      shutil.rmtree(self.path, 1)

    def _abort(self):
      shutil.rmtree(self.path, 1)


  class FileProxy(OFS.Image.File):
    """Proxy to a file.
    """
    # XXX This meta type to make external editor happy
    meta_type = 'Script (Python)'
    def __init__(self, folder, id, read=True):
      self._folder = folder
      self._setId(id)
      self.content_type = 'text/x-python'
      if read:
        self.data = self._folder.read(id)
        self.size = len(self.data)

    def update_data(self, data, content_type=None, size=None):
      # in OFS.Image.File, all writes are done through this method, so we
      # replace it by a method that delegates to portal classes
      return self._folder.write(self.getId(), data, create=False)

    def wl_lockmapping(self, *args, **kw):
      # We store web dav locks on portal classes itself
      return self.aq_parent.aq_parent.wl_lockmapping(*args, **kw)

  InitializeClass(FileProxy)

  _MARKER = object()

  class FolderProxy(OFS.Folder.Folder):
    """Proxy to a Folder
    """
    all_meta_types = ()
    def __init__(self, id, reader, writer, importer, lister):
      self._setId(id)
      self.read = reader
      self.__writer = writer
      self.__importer = importer
      self.__lister = lister

    def objectIds(self, spec=None):
      return self.__lister()

    def write(self, class_id, text, create=True):
      self.__writer(class_id, text, create=create)
      current_transaction = transaction.get()
      if hasattr(current_transaction, 'addAfterCommitHook'):
        current_transaction.addAfterCommitHook(self.reimport, (class_id, ),)
      else:
        LOG('ClassTool', WARNING, 'Transaction does not support '
             'addAfterCommitHook, code will not be reloaded')

    def reimport(self, status, class_id):
      if status and self.__importer is not None:
        self.__importer(class_id)
        self.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
      
    def _getOb(self, key, default=_MARKER ):
      if key in self.objectIds():
        return FileProxy(self, key).__of__(self)
      # maybe the file has just been uploaded, and is still in the temporary
      # instance home, in such case we return an empty file.
      if key in getattr(self, '_v_created', {}):
        return FileProxy(self, key, read=False).__of__(self)
      if default is not _MARKER:
        return default
      raise AttributeError, key

    def PUT_factory(self, name, typ, body):
      # store the information that this file has just been created, and cannot
      # be read yet, because the transaction is not commited.
      self._v_created = {name: True}
      self.write(name, body, create=True)
      return self._getOb(name)

    def _verifyObjectPaste(self, ob, validate_src=True):
      # we only allow FileProxy (this is used in PUT)
      if not isinstance(ob, FileProxy):
        raise Unauthorized
    
  InitializeClass(FolderProxy)
  
  class ClassTool(BaseTool, ClassToolMixIn):
      """
        This is the full-featured version of ClassTool.
      """
      id = 'portal_classes'
      meta_type = 'ERP5 Class Tool'
      portal_type = 'Class Tool'
      isIndexable = False

      # Declarative Security
      security = ClassSecurityInfo()
    
      # we set _folder_handler to OFS_HANDLER to have default behaviour of
      # using objectIds and _getOb
      _folder_handler = OFS_HANDLER
      def objectIds(self, spec=None):
        return ('PropertySheet', 'Document', 'Constraint', 'Extensions', 'tests')

      def __contains__(self, key):
        return key in self.objectIds()

      def _getOb(self, key, default=_MARKER):
        from Products.ERP5Type.Utils import importLocalPropertySheet
        from Products.ERP5Type.Utils import importLocalDocument
        from Products.ERP5Type.Utils import importLocalConstraint
        if key == 'PropertySheet':
          return FolderProxy('PropertySheet',
                             reader=readLocalPropertySheet,
                             writer=self.writeLocalPropertySheet,
                             importer=importLocalPropertySheet,
                             lister=getLocalPropertySheetList,
                             ).__of__(self)
        if key == 'Document':
          return FolderProxy('Document',
                             reader=readLocalDocument,
                             writer=self.writeLocalDocument,
                             importer=importLocalDocument,
                             lister=getLocalDocumentList,
                             ).__of__(self)
        if key == 'Constraint':
          return FolderProxy('Constraint',
                             reader=readLocalConstraint,
                             writer=self.writeLocalConstraint,
                             importer=importLocalConstraint,
                             lister=getLocalConstraintList,
                             ).__of__(self)
        if key == 'Extensions':
          return FolderProxy('Extensions',
                             reader=readLocalExtension,
                             writer=self.writeLocalExtension,
                             importer=None,
                             lister=getLocalExtensionList,
                             ).__of__(self)
        if key == 'tests':
          return FolderProxy('tests',
                             reader=readLocalTest,
                             writer=self.writeLocalTest,
                             importer=None,
                             lister=getLocalTestList,
                             ).__of__(self)
        if default is not _MARKER:
          return default
        raise AttributeError, key

      #
      #   ZMI methods
      #
      manage_options = ( ( { 'label'      : 'Overview'
                          , 'action'     : 'manage_overview'
                          }
                          ,{ 'label'      : 'Documents'
                          , 'action'     : 'manage_viewDocumentList'
                          }
                          ,{ 'label'      : 'PropertySheets'
                          , 'action'     : 'manage_viewPropertySheetList'
                          }
                          ,{ 'label'      : 'Constraints'
                          , 'action'     : 'manage_viewConstraintList'
                          }
                          ,{ 'label'      : 'Extensions'
                          , 'action'     : 'manage_viewExtensionList'
                          }
                          ,{ 'label'      : 'Tests'
                          , 'action'     : 'manage_viewTestList'
                          }
                          ,{ 'label'      : 'Reload Product'
                          , 'action'     : 'manage_viewProductReload'
                          }
                          ,{ 'label'      : 'Product Generation'
                          , 'action'     : 'manage_viewProductGeneration'
                          }
                          ,
                          )
                      + tuple (
                          filter(lambda a: a['label'] not in ('Contents', 'View'),
                                                        Folder.manage_options))
                      )

      security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
      manage_overview = DTMLFile( 'explainClassTool', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewPropertySheetList' )
      manage_viewPropertySheetList = DTMLFile( 'viewPropertySheetList', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewDocumentList' )
      manage_viewDocumentList = DTMLFile( 'viewDocumentList', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewExtensionList' )
      manage_viewExtensionList = DTMLFile( 'viewExtensionList', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewTestList' )
      manage_viewTestList = DTMLFile( 'viewTestList', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewConstraintList' )
      manage_viewConstraintList = DTMLFile( 'viewConstraintList', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_editDocumentForm' )
      manage_editDocumentForm = DTMLFile( 'editDocumentForm', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_editExtensionForm' )
      manage_editExtensionForm = DTMLFile( 'editExtensionForm', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_editTestForm' )
      manage_editTestForm = DTMLFile( 'editTestForm', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_editConstraintForm' )
      manage_editConstraintForm = DTMLFile( 'editConstraintForm', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_editPropertySheetForm' )
      manage_editPropertySheetForm = DTMLFile( 'editPropertySheetForm', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewProductGeneration' )
      manage_viewProductGeneration = DTMLFile( 'viewProductGeneration', _dtmldir )

      security.declareProtected( Permissions.ManagePortal, 'manage_viewProductReload' )
      manage_viewProductReload = DTMLFile( 'viewProductReload', _dtmldir )

      def _clearCache(self):
        """
          Clears the cache of all databases
        """
        database = self.Control_Panel.Database
        for name in database.getDatabaseNames():
          from zLOG import LOG
          LOG('_clearCache', 0, str(name))
          database[name].manage_minimize()

      def _changeEditingPreferences(self, REQUEST, height=None, width=None,
                                    dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences."""
        dr = {"Taller":5, "Shorter":-5}.get(height, 0)
        dc = {"Wider":5, "Narrower":-5}.get(width, 0)
        if isinstance(height, int): dtpref_rows = height
        if isinstance(width, int) or \
           isinstance(width, str) and width.endswith('%'):
            dtpref_cols = width
        rows = str(max(1, int(dtpref_rows) + dr))
        cols = str(dtpref_cols)
        if cols.endswith('%'):
           cols = str(min(100, max(25, int(cols[:-1]) + dc))) + '%'
        else:
           cols = str(max(35, int(cols) + dc))
        e = (DateTime("GMT") + 365).rfc822()
        setCookie = REQUEST["RESPONSE"].setCookie
        setCookie("dtpref_rows", rows, path='/', expires=e)
        setCookie("dtpref_cols", cols, path='/', expires=e)
        REQUEST.other.update({"dtpref_cols":cols, "dtpref_rows":rows})



      security.declareProtected( Permissions.ManagePortal, 'getLocalPropertySheetList' )
      def getLocalPropertySheetList(self):
        """
          Return a list of PropertySheet id which can be modified through the web
        """
        return getLocalPropertySheetList()

      security.declareProtected( Permissions.ManagePortal, 'getLocalExtensionList' )
      def getLocalExtensionList(self):
        """
          Return a list of Extension id which can be modified through the web
        """
        return getLocalExtensionList()

      security.declareProtected( Permissions.ManagePortal, 'getLocalTestList' )
      def getLocalTestList(self):
        """
          Return a list of Test id which can be modified through the web
        """
        return getLocalTestList()

      security.declareProtected( Permissions.ManagePortal, 'getLocalConstraintList' )
      def getLocalConstraintList(self):
        """
          Return a list of Constraint id which can be modified through the web
        """
        return getLocalConstraintList()

      security.declareProtected( Permissions.ManagePortal, 'getLocalDocumentList' )
      def getLocalDocumentList(self):
        """
          Return a list of Document id which can be modified through the web
        """
        return getLocalDocumentList()

      security.declareProtected( Permissions.ManagePortal, 'getProductDocumentPathList' )
      def getProductDocumentPathList(self):
        """
          Return a list of Document id which can be modified through the web
        """
        return getProductDocumentPathList()

      security.declareProtected( Permissions.ManagePortal, 'getDocumentText' )
      def getDocumentText(self, class_id):
        """
          Updates a Document with a new text
        """
        return readLocalDocument(class_id)

      security.declareProtected( Permissions.ManageExtensions, 'newDocument' )
      def newDocument(self, class_id, REQUEST=None):
        """
          Updates a Document with a new text
        """
        text = """\
##############################################################################
#
# %s
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.XMLObject import XMLObject

class %s(XMLObject):
  # CMF Type Definition
  meta_type = 'MYPROJECT Template Document'
  portal_type = 'Template Document'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                      )""" % (COPYRIGHT, class_id)
        self.writeLocalDocument(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&manage_tabs_message=Document+Created' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editDocument' )
      def editDocument(self, class_id, text, REQUEST=None):
        """
          Updates a Document with a new text
        """
        previous_text = readLocalDocument(class_id)
        try:
          self.writeLocalDocument(class_id, text, create=0)
        except SyntaxError, msg:
          if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&errors=%s' % (self.absolute_url(), class_id, msg))
            return
          else:
            return msg
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&manage_tabs_message=Document+Saved' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'importDocument' )
      def importDocument(self, class_id, class_path=None, REQUEST=None):
        """
          Imports a document class
        """
        from Products.ERP5Type.Utils import importLocalDocument
        local_product = self.Control_Panel.Products.ERP5Type
        app = local_product._p_jar.root()['Application']
        importLocalDocument(class_id, path=class_path)

        # Clear object cache and reset _aq_dynamic after reload
        self._clearCache()
        self.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()

        if REQUEST is not None and class_path is None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&manage_tabs_message=Document+Reloaded+Successfully' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editAndImportDocument' )
      def editAndImportDocument(self, class_id, text, REQUEST=None):
        """
        Edit & Import a document class
        """
        errors = self.editDocument(class_id, text)
        if errors is not None:
          if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&errors=%s' % (self.absolute_url(), class_id, errors))
            return
          else:
            return errors

        self.importDocument(class_id)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&manage_tabs_message=Document+Save+And+Reloaded+Successfully' % (self.absolute_url(), class_id))

      def changeDocumentEditingPreferences(self, REQUEST, class_id, height=None, width=None,
                                           dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences for documents."""
        self._changeEditingPreferences(REQUEST, height=height, width=width,
                                       dtpref_cols=dtpref_cols, dtpref_rows=dtpref_rows)
        REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s' % (self.absolute_url(),
                                                                              class_id))


      security.declareProtected( Permissions.ManagePortal, 'getPropertySheetText' )
      def getPropertySheetText(self, class_id):
        """
          Updates a PropertySheet with a new text
        """
        return readLocalPropertySheet(class_id)

      security.declareProtected( Permissions.ManageExtensions, 'newPropertySheet' )
      def newPropertySheet(self, class_id, REQUEST=None):
        """
          Updates a PropertySheet with a new text
        """
        text = """\
##############################################################################
#
# %s
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

class %s:
  \"\"\"
      %s properties for all ERP5 objects
  \"\"\"

  _properties = (
      {   'id'          : 'a_property',
          'description' : 'A local property description',
          'type'        : 'string',
          'mode'        : '' },
  )


""" % (COPYRIGHT, class_id, class_id)
        self.writeLocalPropertySheet(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&manage_tabs_message=PropertySheet+Created' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editPropertySheet' )
      def editPropertySheet(self, class_id, text, REQUEST=None):
        """
          Updates a PropertySheet with a new text
        """
        previous_text = readLocalPropertySheet(class_id)
        self.writeLocalPropertySheet(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&manage_tabs_message=PropertySheet+Saved' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'importPropertySheet' )
      def importPropertySheet(self, class_id, REQUEST=None):
        """
          Imports a PropertySheet class
        """
        from Products.ERP5Type.Utils import importLocalPropertySheet
        local_product = self.Control_Panel.Products.ERP5Type
        app = local_product._p_jar.root()['Application']
        importLocalPropertySheet(class_id)
        # Reset _aq_dynamic after reload
        # There is no need to reset the cache in this case because
        # XXX it is not sure however that class defined propertysheets will be updated
        self.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&manage_tabs_message=PropertySheet+Reloaded+Successfully' % (self.absolute_url(), class_id))

      def changePropertySheetEditingPreferences(self, REQUEST, class_id, height=None, width=None,
                                            dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences for property sheet."""
        self._changeEditingPreferences(REQUEST, height=height, width=width,
                                       dtpref_cols=dtpref_cols, dtpref_rows=dtpref_rows)
        REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s' % (self.absolute_url(),
                                                                               class_id))

      security.declareProtected( Permissions.ManagePortal, 'getExtensionText' )
      def getExtensionText(self, class_id):
        """
          Updates a Extension with a new text
        """
        return readLocalExtension(class_id)

      security.declareProtected( Permissions.ManageExtensions, 'newExtension' )
      def newExtension(self, class_id, REQUEST=None):
        """
          Updates a Extension with a new text
        """
        text = """\
##############################################################################
#
# %s
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

def myExtensionMethod(self, param=None):
  pass
""" % COPYRIGHT
        self.writeLocalExtension(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editExtensionForm?class_id=%s&manage_tabs_message=Extension+Created' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editExtension' )
      def editExtension(self, class_id, text, REQUEST=None):
        """
          Updates a Extension with a new text
        """
        previous_text = readLocalExtension(class_id)
        self.writeLocalExtension(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editExtensionForm?class_id=%s&manage_tabs_message=Extension+Saved' % (self.absolute_url(), class_id))

      def changeExtensionEditingPreferences(self, REQUEST, class_id, height=None, width=None,
                                            dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences for extensions."""
        self._changeEditingPreferences(REQUEST, height=height, width=width,
                                       dtpref_cols=dtpref_cols, dtpref_rows=dtpref_rows)
        REQUEST.RESPONSE.redirect('%s/manage_editExtensionForm?class_id=%s' % (self.absolute_url(),
                                                                               class_id))


      security.declareProtected( Permissions.ManagePortal, 'getTestText' )
      def getTestText(self, class_id):
        """
          Updates a Test with a new text
        """
        return readLocalTest(class_id)

      security.declareProtected( Permissions.ManageExtensions, 'newTest' )
      def newTest(self, class_id, REQUEST=None):
        """
          Updates a Test with a new text
        """
        text = '''\
##############################################################################
#
# %s
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class Test(ERP5TypeTestCase):
  """
  A Sample Test Class
  """

  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ('erp5_base',)

  def afterSetUp(self):
    """
    This is ran before anything, used to set the environment
    """
    # here, you can create the categories and objects your test will depend on
    pass

  def test_01_sampleTest(self):
    """
    A Sample Test

    For the method to be called during the test,
    its name must start with 'test'.
    The '_01_' part of the name is not mandatory,
    it just allows you to define in which order the tests are to be launched.
    Tests methods (self.assert... and self.failIf...)
    are defined in /usr/lib/python/unittest.py.
    """
    self.assertEqual(0, 1)
''' % COPYRIGHT
        self.writeLocalTest(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editTestForm?class_id=%s&manage_tabs_message=Test+Created' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editTest' )
      def editTest(self, class_id, text, REQUEST=None):
        """
          Updates a Test with a new text
        """
        previous_text = readLocalTest(class_id)
        self.writeLocalTest(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editTestForm?class_id=%s&manage_tabs_message=Test+Saved' % (self.absolute_url(), class_id))

      def changeTestEditingPreferences(self, REQUEST, class_id, height=None, width=None,
                                            dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences for test."""
        self._changeEditingPreferences(REQUEST, height=height, width=width,
                                       dtpref_cols=dtpref_cols, dtpref_rows=dtpref_rows)
        REQUEST.RESPONSE.redirect('%s/manage_editTestForm?class_id=%s' % (self.absolute_url(),
                                                                               class_id))


      security.declareProtected( Permissions.ManagePortal, 'getConstraintText' )
      def getConstraintText(self, class_id):
        """
          Updates a Constraint with a new text
        """
        return readLocalConstraint(class_id)

      security.declareProtected( Permissions.ManageExtensions, 'newConstraint' )
      def newConstraint(self, class_id, REQUEST=None):
        """
          Updates a Constraint with a new text
        """
        if class_id == '':
          if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_viewConstraintList?manage_tabs_message=You+must+specify+a+class+name' % (self.absolute_url(),))
            return
        text = """\
##############################################################################
#
# %s
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

from Products.ERP5Type.Constraint import Constraint

class %s(Constraint):
  \"\"\"
    Explain here what this constraint checker does
  \"\"\"

  def checkConsistency(self, obj, fixit = 0):
    \"\"\"
      Implement here the consistency checker
      whenever fixit is not 0, object data should be updated to
      satisfy the constraint
    \"\"\"

    error_list = []

    # Do the job here

    return error_list
""" % (COPYRIGHT, class_id)
        self.writeLocalConstraint(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s&manage_tabs_message=Constraint+Created' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'editConstraint' )
      def editConstraint(self, class_id, text, REQUEST=None):
        """
          Updates a Constraint with a new text
        """
        previous_text = readLocalConstraint(class_id)
        self.writeLocalConstraint(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s&manage_tabs_message=Constraint+Saved' % (self.absolute_url(), class_id))

      security.declareProtected( Permissions.ManageExtensions, 'importConstraint' )
      def importConstraint(self, class_id, REQUEST=None):
        """
          Imports a Constraint class
        """
        from Products.ERP5Type.Utils import importLocalConstraint
        local_product = self.Control_Panel.Products.ERP5Type
        app = local_product._p_jar.root()['Application']
        importLocalConstraint(class_id)
        # Reset _aq_dynamic after reload
        # There is no need to reset the cache in this case because
        # XXX it is not sure however that class defined propertysheets will be updated
        self.portal_types.resetDynamicDocumentsOnceAtTransactionBoundary()
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s&manage_tabs_message=Constraint+Reloaded+Successfully' % (self.absolute_url(), class_id))


      def changeConstraintEditingPreferences(self, REQUEST, class_id, height=None, width=None,
                                            dtpref_cols="100%", dtpref_rows="20"):
        """Change editing preferences for constraint."""
        self._changeEditingPreferences(REQUEST, height=height, width=width,
                                       dtpref_cols=dtpref_cols, dtpref_rows=dtpref_rows)
        REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s' % (self.absolute_url(),
                                                                                class_id))

      security.declareProtected( Permissions.ManageExtensions, 'generateProduct' )
      def generateProduct(self, product_id,
                          document_id_list=(), property_sheet_id_list=(), constraint_id_list=(),
                          extension_id_list=(), test_id_list=(),
                          generate_cvsignore=0, REQUEST=None):
        """Generate a Product
        """
        if not product_id:
          message = 'Product Name must be specified'
          if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(
                    '%s/manage_viewProductGeneration?manage_tabs_message=%s' %
                    (self.absolute_url(), message.replace(' ', '+')))
          raise BadRequest(message)

        # Ensure that Products exists.
        product_path = os.path.join(getConfiguration().instancehome, 'Products')
        if not os.path.exists(product_path):
          os.mkdir(product_path)

        # Make a new Product directory if not present.
        base_path = os.path.join(product_path, product_id)
        if not os.path.exists(base_path):
          os.mkdir(base_path)

        # Make sub-directories if not present.
        for d in ('interfaces', 'Document', 'PropertySheet', 'Extensions', 'Tool', 'Constraint',
                  'tests', 'help', 'skins', 'dtml', ):
          path = os.path.join(base_path, d)
          if not os.path.exists(path):
            os.mkdir(path)
          # Create an empty __init__.py.
          init = os.path.join(path, '__init__.py')
          if not os.path.exists(init):
            open(init, 'w').close()
          # For convenience, make .cvsignore.
          if generate_cvsignore:
            cvsignore = os.path.join(path, '.cvsignore')
            if not os.path.exists(cvsignore):
              with open(cvsignore, 'w') as f:
                f.write('*.pyc' + os.linesep)

        # Create a Permissions module for this Product.
        permissions = os.path.join(base_path, 'Permissions.py')
        if not os.path.exists(permissions):
          open(permissions, 'w').close()

        # Make .cvsignore for convenience.
        if generate_cvsignore:
          cvsignore = os.path.join(base_path, '.cvsignore')
          if not os.path.exists(cvsignore):
            with open(cvsignore, 'w') as f:
              f.write('*.pyc' + os.linesep)

        # Create an init file for this Product.
        init = os.path.join(base_path, '__init__.py')
        if not os.path.exists(init):
          text = '''\
##############################################################################
#
# %s
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
"""
    ERP5 Free Software ERP
"""

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
import sys, Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals( this_module, globals(), permissions_module = Permissions)

# Finish installation
def initialize( context ):
  import Document
  initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = (),
                         portal_tools = (),
                         content_constructors = (),
                         content_classes = ())
''' % COPYRIGHT
          with open(init, 'w') as f:
            f.write(text)

        # Create a skeleton README.txt.
        readme = os.path.join(base_path, 'README.txt')
        if not os.path.exists(readme):
          text = '''
%s

  %s was automatically generated by ERP5 Class Tool.
''' % (product_id, product_id)
          with open(readme, 'w') as f:
            f.write(text)

        # Now, copy selected code.
        for d, m, id_list in (('Document', readLocalDocument, document_id_list),
                              ('PropertySheet', readLocalPropertySheet, property_sheet_id_list),
                              ('Constraint', readLocalConstraint, constraint_id_list),
                              ('tests', readLocalTest, test_id_list),
                              ('Extensions', readLocalExtension, extension_id_list)):
          for class_id in id_list:
            path = os.path.join(base_path, d, class_id) + '.py'
            text = m(class_id)
            with open(path, 'w') as f:
              f.write(text)

        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_viewProductGeneration?manage_tabs_message=New+Product+Saved+In+%s' % (self.absolute_url(), base_path))

      security.declareProtected( Permissions.ManagePortal,
                                 'asDocumentationHelper')
      def asDocumentationHelper(self, class_id):
        """
          This function generates a TempDocumentationHelper for a class of a
          given name.

          XXX: this code is (almost) duplicated from ERP5Types/Base.py:asDocumentationHelper
        """

        import erp5.portal_type
        # XXX so this is ugly, but should disappear with classes in ZODB
        my_class = getattr(erp5.portal_type, class_id)

        method_list = []
        property_list = []
        dochelper = newTempDocumentationHelper(self, self.getId(), title=class_id,
                      type=my_class.__class__.__name__,
                      description=inspect.getdoc(my_class))
        try:
          dochelper.setSourcePath(inspect.getsourcefile(my_class))
        except (IOError, TypeError), err:
          pass
        if getattr(my_class, '__bases__', None) is not None:
          dochelper.setInheritanceList([type(x) for x in my_class.__bases__])
        #dochelper.my_security =
        for k, v in my_class.__dict__.items():
          if k in ATTRIBUTE_INSPECTION_SKIP_LIST:
            # skip attributes we don't know how to inspect
            continue
          subdochelper = newTempDocumentationHelper(dochelper, k, title=k,
                           description=inspect.getdoc(v),
                           security=pformat(getattr(my_class,
                                                 '%s__roles__' % (k,),
                                                 None)))
          try:
            subdochelper.setType(v.__class__.__name__)
          except AttributeError:
            pass
          try:
            subdochelper.setSourcePath(inspect.getsourcefile(v))
          except (IOError, TypeError), err:
            pass
          try:
            subdochelper.setSourceCode(inspect.getsource(v))
          except (IOError, TypeError), err:
            pass
          try:
            subdochelper.setArgumentList(inspect.getargspec(v))
          except (IOError, TypeError), err:
            pass
          if subdochelper.getType() in ('function',):
            method_list.append(subdochelper)
          elif subdochelper.getType() in ('int', 'float', 'long', 'str', 'tuple', 'dict', 'list') \
           and not subdochelper.getTitle().startswith('__') :
            subdochelper.setContent(pformat(v))
            property_list.append(subdochelper)
        method_list.sort()
        dochelper.setStaticMethodList(method_list)
        property_list.sort()
        dochelper.setStaticPropertyList(property_list)
        return dochelper

      def _createTemporaryInstanceHome(self):
        if getattr(self, '_v_instance_home', None) is None:
          self._v_instance_home = TemporaryInstanceHome()
        self._v_instance_home._register()

      security.declareProtected( Permissions.ManageExtensions, 'writeLocalPropertySheet' )
      def writeLocalPropertySheet(self, class_id, text, create=1):
        self._createTemporaryInstanceHome()
        writeLocalPropertySheet(class_id, text, create=create,
                                instance_home=self._v_instance_home.getPath())

      security.declareProtected( Permissions.ManageExtensions, 'writeLocalExtension' )
      def writeLocalExtension(self, class_id, text, create=1):
        self._createTemporaryInstanceHome()
        writeLocalExtension(class_id, text, create=create,
                            instance_home=self._v_instance_home.getPath())

      security.declareProtected( Permissions.ManageExtensions, 'writeLocalTest' )
      def writeLocalTest(self, class_id, text, create=1):
        self._createTemporaryInstanceHome()
        writeLocalTest(class_id, text, create=create,
                       instance_home=self._v_instance_home.getPath())

      security.declareProtected( Permissions.ManageExtensions, 'writeLocalDocument' )
      def writeLocalDocument(self, class_id, text, create=1):
        self._createTemporaryInstanceHome()
        writeLocalDocument(class_id, text, create=create,
                           instance_home=self._v_instance_home.getPath())

      security.declareProtected( Permissions.ManageExtensions, 'writeLocalConstraint' )
      def writeLocalConstraint(self, class_id, text, create=1):
        self._createTemporaryInstanceHome()
        writeLocalConstraint(class_id, text, create=create,
                             instance_home=self._v_instance_home.getPath())

      security.declareProtected(Permissions.ManagePortal, 'readTestOutput')
      def readTestOutput(self, position=0):
        """
        Return unread part of the test result
        """
        result = ''
        position = int(position)
        global global_stream
        if global_stream is not None:
          global_stream.seek(position)
          result = global_stream.read()
        return result

      security.declarePrivate('_getCommaSeparatedParameterList')
      def _getCommaSeparatedParameterList(self, parameter_list):
        # clean parameter_list and split it by commas if necessary
        if not parameter_list:
          parameter_list = ()
        elif isinstance(parameter_list, basestring):
          parameter_list = tuple(parameter_name.strip()
                                 for parameter_name in parameter_list.split(',')
                                 if parameter_name.strip())
        return parameter_list

      security.declareProtected(Permissions.ManagePortal, 'runLiveTest')
      def runLiveTest(self, test_list=None, run_only=None, debug=False,
                      verbose=False):
        """
        Launch live tests

        run_only=STRING      Run only specified test methods delimited with
                             commas (e.g. testFoo,testBar). This can be regular
                             expressions.
        debug=boolean        Invoke debugger on errors / failures.
        verbose=boolean      Display more information when running tests
        """
        # Allow having strings for verbose and debug
        verbose = int(verbose) and True or False
        debug = int(debug) and True or False
        test_list = self._getCommaSeparatedParameterList(test_list)
        run_only = self._getCommaSeparatedParameterList(run_only)
        if not test_list:
          # no test to run
          return ''
        path = os.path.join(getConfiguration().instancehome, 'tests')
        verbosity = verbose and 2 or 1
        global global_stream
        global_stream = StringIO()
        from Products.ERP5Type.tests.ERP5TypeLiveTestCase import runLiveTest
        try:
          result = runLiveTest(test_list,
                              run_only=run_only,
                              debug=debug,
                              path=path,
                              stream=global_stream,
                              verbosity=verbosity)
        except ImportError:
          traceback.print_exc(file=global_stream)
        global_stream.seek(0)
        return global_stream.read()

      def getProductList(self):
        """ List all products """
        return self.Control_Panel.Products.objectIds()

      def reloadProduct(self, product_id, REQUEST=None):
        """ Reload a given product """
        product = self.Control_Panel.Products[product_id]
        if product._readRefreshTxt() is None:
            raise Unauthorized, 'refresh.txt not found'
        message = None
        if RefreshFuncs.performFullRefresh(product._p_jar, product.id):
            from ZODB import Connection
            Connection.resetCaches() # Clears cache in future connections.
            message = 'Product refreshed.'
        else:
            message = 'An exception occurred. Check your log'

        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_viewProductReload?manage_tabs_message=%s' % (self.absolute_url(), message))

else:

  class ClassTool(BaseTool, ClassToolMixIn):
      """
        Dummy version of ClassTool.
      """
      id = 'portal_classes'
      meta_type = 'ERP5 Dummy Class Tool'
      portal_type = 'Dummy Class Tool'
      isIndexable = False

      # Declarative Security
      security = ClassSecurityInfo()

      security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
      manage_overview = DTMLFile( 'explainDummyClassTool', _dtmldir )

InitializeClass(ClassTool)

