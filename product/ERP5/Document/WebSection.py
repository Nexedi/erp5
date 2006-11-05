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
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet,\
                              Constraint, Interface, Cache
from Products.ERP5.Document.Domain import Domain
from Acquisition import ImplicitAcquisitionWrapper, aq_base, aq_inner
from Products.ERP5Type.Base import TempBase
from Globals import get_request

from zLOG import LOG

class WebSection(Domain):
    """
      A Web Section is a Domain with an extended API intended to
      support the creation of Web front ends to ERP5 contents.
    """
    # CMF Type Definition
    meta_type = 'ERP5 Web Section'
    portal_type = 'Web Section'
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
                      , PropertySheet.SortIndex
                      )

    # Draft - this is being worked on
    # Due to some issues in acquisition, the implementation  of getWebSectionValue
    # through acquisition by containment does not work for URLs
    # such as web_site_module/a/b/c/web_page_module/d
    # getWebSectionValue will return web_site_module/a/b instead
    # of web_site_module/a/b/c
    #security.declareProtected(Permissions.AccessContentsInformation, 'getWebSectionValue')
    #def getWebSectionValue(self):
      #"""
        #Returns the current web section (ie. self) though containment acquisition
      #"""
      #return self

