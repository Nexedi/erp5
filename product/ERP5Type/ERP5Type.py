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

from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo

import Products.CMFCore.TypesTool
from Products.CMFCore.TypesTool import ScriptableTypeInformation, FactoryTypeInformation, TypesTool
from Products.CMFCore.interfaces.portal_types import ContentTypeInformation as ITypeInformation

from Products.ERP5Type import _dtmldir
from Products.ERP5Type import Permissions as ERP5Permissions

class ERP5AcquisitionType:
    """
      Mix in class
    """
    pass

class ERP5TypeInformation( ScriptableTypeInformation, ERP5AcquisitionType ):
    """
    ERP5 Types are based on Scriptable Type (this will eventually require some rewriting
    of Utils... and addXXX methods)

    The most important feature of ERP5Types is programmable acquisition which
    allows to define attributes which are acquired through categories.

    Another feature is to define the way attributes are stored (localy,
    database, etc.). This allows to combine multiple attribute sources
    in a single object..
    """

    __implements__ = ITypeInformation

    meta_type = 'ERP5 Type Information'
    security = ClassSecurityInfo()

    _properties = ScriptableTypeInformation._properties

    manage_options = (ScriptableTypeInformation.manage_options[:2] +
                      ({'label':'Acquisition',
                        'action':'manage_editAcquisitionForm'},) +
                      ScriptableTypeInformation.manage_options[2:])


    #
    #   Acquisition editing interface
    #

    _actions_form = DTMLFile( 'editActions', _dtmldir )

    security.declareProtected(ERP5Permissions.ManagePortal, 'manage_editAcquisitionForm')
    def manage_editAcquisitionForm(self, REQUEST, manage_tabs_message=None):
        """
        Shows the 'Actions' management tab.
        """
        actions = []
        for a in self.getActions():
            a = a.copy()
            p = a['permissions']
            if p:
                a['permission'] = p[0]
            else:
                a['permission'] = ''
            if not a.has_key('category'):
                a['category'] = 'object'
            if not a.has_key('id'):
                a['id'] = cookString(a['name'])
            if not a.has_key( 'visible' ):
                a['visible'] = 1
            actions.append(a)
        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form(self, REQUEST,
                                  actions=actions,
                                  possible_permissions=pp,
                                  management_view='Actions',
                                  manage_tabs_message=manage_tabs_message)

InitializeClass( ERP5TypeInformation )

typeClasses = [
    {'class':FactoryTypeInformation,
     'name':FactoryTypeInformation.meta_type,
     'action':'manage_addFactoryTIForm',
     'permission':'Manage portal'},
    {'class':ScriptableTypeInformation,
     'name':ScriptableTypeInformation.meta_type,
     'action':'manage_addScriptableTIForm',
     'permission':'Manage portal'},
    {'class':ERP5TypeInformation,
     'name':ERP5TypeInformation.meta_type,
     'action':'manage_addERP5TIForm',
     'permission':'Manage portal'},
    ]

class ERP5TypesTool(TypesTool):
    """
      Only used to patch standard TypesTool
    """
    meta_type = 'ERP5 Type Information'
    
    security = ClassSecurityInfo()

    security.declareProtected(ERP5Permissions.ManagePortal, 'manage_addERP5TIForm')
    def manage_addERP5TIForm(self, REQUEST):
        ' '
        return self._addTIForm(
            self, REQUEST,
            add_meta_type=ERP5TypeInformation.meta_type,
            types=self.listDefaultTypeInformation())

# Dynamic patch
Products.CMFCore.TypesTool.typeClasses = typeClasses
Products.CMFCore.TypesTool.TypesTool.manage_addERP5TIForm = ERP5TypesTool.manage_addERP5TIForm
