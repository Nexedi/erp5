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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import UniqueObject, _checkPermission, _getAuthenticatedUser
from Products.ERP5Type.Globals import InitializeClass
from Acquisition import aq_base
from DateTime import DateTime

from zLOG import LOG

class InterpolationTool (UniqueObject):
    """
    The InterpolationTool centralises interpolation
    policies to calculate values from the mapped values.

    Currently, the interpolation is simple and closed. All mapped
    values are selected and put in memory. Then, some algo is applied
    to determine a value.

    Examples of applications:

    - calculate the price of resource X for customer Y under
      condition Z

    ERP5 main application : implement attribute lookup and interpolation
    policy. Configuration done for now through mappedvalues. Later,
    this could be done another way.

    Try to mimic: ???? (Reports ?)...
    
    Status : OK
    """
    id = 'portal_interactions'
    meta_type = 'ERP5 Interaction Tool'
    portal_type = 'Interpolation Tool'
    security = ClassSecurityInfo()

    manage_options = ( { 'label' : 'Overview', 'action' : 'manage_overview' }
                     ,
                     ) + ZCatalog.manage_options


    def __init__(self):
        ZCatalog.__init__(self, self.getId())

    # Explicite Inheritance
    _listAllowedRolesAndUsers = CMFCoreCatalogTool._listAllowedRolesAndUsers
    __url = CMFCoreCatalogTool.__url

InitializeClass(InterpolationTool)
