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
from Products.ERP5Type.Utils import readLocalDocument, writeLocalDocument, getLocalDocumentList

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
                        ,{ 'label'      : 'Extensions'
                         , 'action'     : 'manage_viewExtensionList'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainDocumentTool', _dtmldir )

    security.declareProtected( Permissions.ManagePortal, 'manage_viewPropertySheetList' )
    manage_viewPropertySheetList = DTMLFile( 'viewPropertySheetList', _dtmldir )

    security.declareProtected( Permissions.ManagePortal, 'manage_viewDocumentList' )
    manage_viewDocumentList = DTMLFile( 'viewDocumentList', _dtmldir )

    security.declareProtected( Permissions.ManagePortal, 'manage_viewExtensionList' )
    manage_viewExtensionList = DTMLFile( 'viewExtensionList', _dtmldir )

    security.declareProtected( Permissions.ManagePortal, 'manage_editDocumentForm' )
    manage_editDocumentForm = DTMLFile( 'editDocumentForm', _dtmldir )

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

    security.declareProtected( Permissions.ManagePortal, 'getLocalDocumentList' )
    def getLocalDocumentList(self):
      """
        Return a list of Document id which can be modified through the web
      """
      return getLocalDocumentList()

    security.declareProtected( Permissions.ManagePortal, 'getDocumentText' )
    def getDocumentText(self, class_id):
      """
        Updates a Document with a new text
      """
      return readLocalDocument(class_id)

    security.declareProtected( Permissions.ManagePortal, 'newDocument' )
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

    security.declareProtected( Permissions.ManagePortal, 'editDocument' )
    def editDocument(self, class_id, text, REQUEST=None):
      """
        Updates a Document with a new text
      """
      previous_text = readLocalDocument(class_id)
      writeLocalDocument(class_id, text)
      if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&message=Document+Saved' % (self.absolute_url(), class_id))

    security.declareProtected( Permissions.ManagePortal, 'importDocument' )
    def importDocument(self, class_id, REQUEST=None):
      """
        Imports a document class
      """
      from Products.ERP5Type.Utils import importLocalDocument
      local_product = self.Control_Panel.Products.ERP5Type
      app = local_product._p_jar.root()['Application']
      importLocalDocument(class_id)
      if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_editDocumentForm?class_id=%s&message=Document+Reloaded+Successfully' % (self.absolute_url(), class_id))

InitializeClass(ClassTool)
