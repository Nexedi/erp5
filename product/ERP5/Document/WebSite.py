##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Domain import Domain
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from Products.ERP5Type.Base import TempBase
from Globals import get_request
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.User import emergency_user
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager

from zLOG import LOG

Domain_getattr = Domain.inheritedAttribute('__getattr__')

class WebSite(Domain):
    """
      A Web Site root class. This class is used by ERP5 Commerce
      to define the root of an eCommerce site.

      WARNING:
        - Z Catalog Search permission must be set for Anonymous

      TODO:
        - accelerate document lookup by caching acceptable keys
        - fix missing REQUEST information in aq_dynamic documents
    """
    # CMF Type Definition
    meta_type = 'ERP5 Web Site'
    portal_type = 'Web Site'
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.WebSite
                      )


    def _aq_dynamic(self, name):
      """
        Try to find a suitable document based on the
        web site local naming policies as defined by
        the WebSite_getDocument script """
      # First let us call the super method
      dynamic = Domain._aq_dynamic(self, name)
      if dynamic is not None :
        return dynamic
      # Do some optimisation here for names which can not the names of documents
      if name.startswith('_') or name.startswith('portal_')\
          or name.startswith('aq_') or name.startswith('selection_') \
          or name.startswith('sort-') or name == 'getLayout':
        return None
      # Create a non recursion variable
      if not hasattr(self, '_v_allow_lookup'): self._v_allow_lookup = {}
      if self._v_allow_lookup.has_key(name):
        return self._v_allow_lookup[name]
      try:
        self._v_allow_lookup[name] = None
        old_manager = getSecurityManager()
        portal = self.getPortalObject()
        # Use the webmaster identity to find documents
        user = portal.acl_users.getUserById(self.getWebmaster())
        newSecurityManager(get_request(), user)
        document = self.WebSite_getDocument(portal, name)
        self._v_allow_lookup[name] = document
        setSecurityManager(old_manager)
      except:
        # Cleanup non recursion dict in case of exception
        if self._v_allow_lookup.has_key(name): del self._v_allow_lookup[name]
        raise
      return document