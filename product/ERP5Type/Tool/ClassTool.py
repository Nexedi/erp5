##############################################################################
#
# Copyright (c) 2002-2004 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from Products.CMFCore.utils import UniqueObject

from Acquisition import Implicit
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from Products.ERP5Type import Permissions
from Products.ERP5Type import _dtmldir
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Document.Folder import Folder

from Products.ERP5Type.Utils import readLocalPropertySheet, writeLocalPropertySheet, getLocalPropertySheetList
from Products.ERP5Type.Utils import readLocalExtension, writeLocalExtension, getLocalExtensionList
from Products.ERP5Type.Utils import readLocalTest, writeLocalTest, getLocalTestList
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, getLocalDocumentList
from Products.ERP5Type.Utils import readLocalConstraint, writeLocalConstraint, getLocalConstraintList
from Products.ERP5Type.InitGenerator import getProductDocumentPathList

from Products.ERP5Type.Base import _aq_reset

from Products.ERP5Type import allowClassTool

if allowClassTool():

  class ClassTool(BaseTool):
      """
      A tool to edit code through the web
      """
      id = 'portal_classes'
      meta_type = 'ERP5 Class Tool'
  
      # Declarative Security
      security = ClassSecurityInfo()
  
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
                          ,
                          )
                      + tuple (
                          filter(lambda a: a['label'] not in ('Contents', 'View'), 
                                                        Folder.manage_options))
                      )
  
      security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
      manage_overview = DTMLFile( 'explainDocumentTool', _dtmldir )
  
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
  
      # Clears the cache of all databases
      def _clearCache(self):
        database = self.Control_Panel.Database
        for name in database.getDatabaseNames():
          from zLOG import LOG
          LOG('_clearCache', 0, str(name))
          database[name].manage_minimize()
      
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
        text = """
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.XMLObject import XMLObject

class %s(XMLObject):
    # CMF Type Definition
    meta_type = 'MYPROJECT Template Document'
    portal_type = 'Template Document'
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      )""" % class_id
        writeLocalDocument(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&message=Document+Created' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'editDocument' )
      def editDocument(self, class_id, text, REQUEST=None):
        """
          Updates a Document with a new text
        """
        previous_text = readLocalDocument(class_id)
        writeLocalDocument(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&message=Document+Saved' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'importDocument' )
      def importDocument(self, class_id, class_path=None, REQUEST=None):
        """
          Imports a document class
        """
        from Products.ERP5Type.Utils import importLocalDocument
        local_product = self.Control_Panel.Products.ERP5Type
        app = local_product._p_jar.root()['Application']
        importLocalDocument(class_id, document_path=class_path)
        
        # Clear object cache and reset _aq_dynamic after reload
        self._clearCache()
        _aq_reset()
        
        if REQUEST is not None and class_path is None:
          REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&message=Document+Reloaded+Successfully' % (self.absolute_url(), class_id))
  
  
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
        text = """
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

class PropertySheetTemplate:
    \"\"\"
        PropertySheetTemplate properties for all ERP5 objects
    \"\"\"

    _properties = (
        {   'id'          : 'a_property',
            'description' : 'A local property description',
            'type'        : 'string',
            'mode'        : '' },
    )
  

"""
        writeLocalPropertySheet(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&message=PropertySheet+Created' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'editPropertySheet' )
      def editPropertySheet(self, class_id, text, REQUEST=None):
        """
          Updates a PropertySheet with a new text
        """
        previous_text = readLocalPropertySheet(class_id)
        writeLocalPropertySheet(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&message=PropertySheet+Saved' % (self.absolute_url(), class_id))
  
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
        _aq_reset() 
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editPropertySheetForm?class_id=%s&message=PropertySheet+Reloaded+Successfully' % (self.absolute_url(), class_id))
  
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
        text = """
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

def myExtensionMethod(self, param=None):
  pass
"""
        writeLocalExtension(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editExtensionForm?class_id=%s&message=Extension+Created' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'editExtension' )
      def editExtension(self, class_id, text, REQUEST=None):
        """
          Updates a Extension with a new text
        """
        previous_text = readLocalExtension(class_id)
        writeLocalExtension(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editExtensionForm?class_id=%s&message=Extension+Saved' % (self.absolute_url(), class_id))
  
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
        text = '''
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG

class Test(ERP5TypeTestCase):
  """
    This is a Sample Test
  """
  # variable used for this test
  run_all_test = 1

  def getTitle(self):
    return "SampleTest"

  def getBusinessTemplateList(self):
    """
    Tuple of Business Templates we need to install
    """
    return ()

  def enableLightInstall(self):
    """
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    Return if we should create (1) or not (0) an activity tool
    """
    return 1

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('alex', '', ['Manager'], [])
    user = uf.getUserById('alex').__of__(uf)
    newSecurityManager(None, user)

  def afterSetUp(self, quiet=1, run=1):
    """
    This is ran before anything, used to set the environment
    """
    self.login()

  def test_01_SampleTest(self, quiet=0, run=run_all_test):
    """
    A Sample Test
    """
    if not run: return
    if not quiet:
      ZopeTestCase._print('\\nTest SampleTest ')
      LOG('Testing... ',0,'testSampleTest')
    self.assertEqual(0, 1)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite
'''
        writeLocalTest(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editTestForm?class_id=%s&message=Test+Created' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'editTest' )
      def editTest(self, class_id, text, REQUEST=None):
        """
          Updates a Test with a new text
        """
        previous_text = readLocalTest(class_id)
        writeLocalTest(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editTestForm?class_id=%s&message=Test+Saved' % (self.absolute_url(), class_id))
  
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
        text = """
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type.Constraint import Constraint

class ConstraintTemplate(Constraint):
    \"\"\"
      Explain here what this constraint checker does
    \"\"\"

    def checkConsistency(self, object, fixit = 0):
      \"\"\"
        Implement here the consistency checker
        whenever fixit is not 0, object data should be updated to 
        satisfy the constraint
      \"\"\"

      errors = []
      
      # Do the job here
      
      return errors
"""
        writeLocalConstraint(class_id, text)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s&message=Constraint+Created' % (self.absolute_url(), class_id))
  
      security.declareProtected( Permissions.ManageExtensions, 'editConstraint' )
      def editConstraint(self, class_id, text, REQUEST=None):
        """
          Updates a Constraint with a new text
        """
        previous_text = readLocalConstraint(class_id)
        writeLocalConstraint(class_id, text, create=0)
        if REQUEST is not None:
          REQUEST.RESPONSE.redirect('%s/manage_editConstraintForm?class_id=%s&message=Constraint+Saved' % (self.absolute_url(), class_id))
    
else:
  
  class ClassTool(BaseTool):
      """
      A tool to edit code through the web
      """
      id = 'portal_classes'
      meta_type = 'ERP5 Dummy Class Tool'
  
      # Declarative Security
      security = ClassSecurityInfo()
  
      security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
      manage_overview = DTMLFile( 'explainDummyClassTool', _dtmldir )        

InitializeClass(ClassTool)
      
