# (C) Copyright 2004 Nexedi SARL <http://nexedi.com>
# Authors: Sebastien Robin <seb@nexedi.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

from Products.CPSCore.ProxyBase import ProxyBase, ProxyFolder
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Globals import InitializeClass
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Document.Folder import Folder
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCore.CMFCorePermissions import ViewManagementScreens
from Products.CMFCore.utils import getToolByName
from zLOG import LOG

# First we should make ProxyBase a subclass of Base
# XXX doesn't works at all
#ProxyBase.__bases__ += (ERP5Base,)
#ProxyDocument.__bases__ += (ERP5Base,)

class PatchedProxyBase(ProxyBase):

    security = ClassSecurityInfo()


    def manage_afterEdit(self):
        """
        We have to notify the proxy tool we have modified
        this object
        """
        px_tool= getToolByName(self,'portal_proxies')
        utool = getToolByName(self, 'portal_url')
        rpath = utool.getRelativeUrl(self)
        px_tool._modifyProxy(self,rpath)



    def _propertyMap(self):
        """
        Returns fake property sheet
        """
        property_sheet = []

        #property_sheet += self._properties

        property_sheet += [
            {
              'id'    :   'docid',
              'type'  :   'string'
            },
            {
              'id'    :   'default_language',
              'type'  :   'string'
            },
            {
              'id'    :   'default_language',
              'type'  :   'string'
            },
            {
              'id'    :   'sync_language_revisions', # XXX we have to manage dict type
              'type'  :   'dict'
            }
            ]
        return tuple(property_sheet + list(getattr(self, '_local_properties', ())))

    security.declareProtected(View, 'getSyncLanguageRevisions')
    def getSyncLanguageRevisions(self):
        """Get the mapping of language -> revision."""
        return self._language_revs.copy()

    security.declareProtected(View, 'setSyncLanguageRevisions')
    def setSyncLanguageRevisions(self, dict):
        """Set the mapping of language -> revision."""
        for lang in dict.keys():
            self.setLanguageRevision(lang,dict[lang])

    security.declareProtected(View, 'getSyncRepoHistory')
    def getSyncRepoHistory(self):
        """Get the mapping of language -> revision."""
        return self._language_revs.copy()

    security.declareProtected(View, 'setSyncRepoHistory')
    def setSyncRepoHistory(self, dict):
        """Set the mapping of language -> revision."""
        repotool = getToolByName(self, 'portal_repository')
        #repotool.
        for lang in dict.keys():
            self.setLanguageRevision(lang,dict[lang])


ProxyBase.getPath = Base.getPath
ProxyBase.getProperty = Base.getProperty
ProxyBase._setProperty = Base._setProperty
ProxyBase._edit = Base._edit
ProxyBase.asXML = Base.asXML
ProxyBase._propertyMap = PatchedProxyBase._propertyMap
ProxyBase.manage_afterEdit = PatchedProxyBase.manage_afterEdit
ProxyBase.getSyncLanguageRevisions = PatchedProxyBase.getSyncLanguageRevisions
ProxyBase.setSyncLanguageRevisions = PatchedProxyBase.setSyncLanguageRevisions
ProxyBase.getSyncRepoHistory = PatchedProxyBase.getSyncRepoHistory
ProxyBase.setSyncRepoHistory = PatchedProxyBase.setSyncRepoHistory

ProxyFolder.asXML = Folder.asXML
ProxyFolder.manage_setLocalPermissions = Folder.manage_setLocalPermissions
ProxyFolder.get_local_permissions = Folder.get_local_permissions

from Products.CPSCore.CPSBase import CPSBaseDocument

class PatchedCPSBaseDocument(CPSBaseDocument):

    security = ClassSecurityInfo()


    def _propertyMap(self):
        """
        Returns fake property sheet
        """
        property_sheet = []

        property_sheet += self._properties

        property_sheet += [
            {
              'id'    :   'Title',
              'type'  :   'string'
            },
            {
              'id'    :   'description',
              'type'  :   'string'
            },
            ]
        return tuple(property_sheet + list(getattr(self, '_local_properties', ())))

CPSBaseDocument.getPath = Base.getPath
CPSBaseDocument.getProperty = Base.getProperty
CPSBaseDocument._setProperty = Base._setProperty
CPSBaseDocument._edit = Base._edit
CPSBaseDocument.asXML = Base.asXML
CPSBaseDocument.get_local_permissions = Base.get_local_permissions
CPSBaseDocument.manage_setLocalPermissions = Base.manage_setLocalPermissions
CPSBaseDocument._propertyMap = PatchedCPSBaseDocument._propertyMap

