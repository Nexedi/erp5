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

import os
from Products.CMFCore.utils import UniqueObject

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type import Permissions, _dtmldir
from zLOG import LOG, INFO, WARNING

class BaseTool (UniqueObject, Folder):
    """
       Base class for all ERP5 Tools
    """
    id = 'portal_base_tool'       # Override this
    meta_type = 'ERP5 Base Tool'  # Override this
    allowed_types = ()            # Override this

    # Declarative Security
    security = ClassSecurityInfo()

    #
    #   ZMI methods
    #
    manage_options = ( ( { 'label'      : 'Overview'
                         , 'action'     : 'manage_overview'
                         }
                        ,
                        )
                     + Folder.manage_options
                     )

    security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
    manage_overview = DTMLFile( 'explainBaseTool', _dtmldir )

    # Filter content (ZMI))
    def __init__(self, id=None):
        if id is None:
          id = self.__class__.id
        return Folder.__init__(self, id)

    def _bootstrap(self, bt_name, item_name, content_id_list):
      from Products.ERP5.Document.BusinessTemplate import quote
      traverse = self.unrestrictedTraverse
      path = os.path.join(bt_name, item_name, self.id)
      for root, dirs, files in os.walk(path):
        container_path = root.split(os.sep)[3:]
        load = traverse(container_path)._importObjectFromFile
        if container_path:
          id_set = set(x[:-4] for x in files if x[-4:] == '.xml')
        else:
          id_set = set(quote(x) for x in content_id_list)
          id_set.difference_update(quote(x) for x in self.objectIds())
        dirs[:] = id_set.intersection(dirs)
        for file in id_set:
          load(os.path.join(root, file + '.xml'),
               verify=False, set_owner=False, suppress_events=True)

    # Filter content (ZMI))
    def filtered_meta_types(self, user=None):
        # Filters the list of available meta types.
        all = BaseTool.inheritedAttribute('filtered_meta_types')(self)
        meta_types = []
        for meta_type in self.all_meta_types():
            if meta_type['name'] in self.allowed_types:
                meta_types.append(meta_type)
        return meta_types

    def _migrateToPortalTypeClass(self):
      portal_type = self.getPortalType()
      # Tools are causing problems: they used to have no type_class, or wrong
      # type_class, or sometimes have no type definitions at all.
      # Check that everything is alright before trying
      # to migrate the tool:
      from Products.ERP5.ERP5Site import getSite
      types_tool = getSite().portal_types
      type_definition = getattr(types_tool, portal_type, None)
      if type_definition is None:
        LOG('BaseTool._migrateToPortalTypeClass', WARNING,
            "No portal type definition was found for Tool '%s'"
            " (class %s, portal_type '%s')"
            % (self.getId(), self.__class__.__name__, portal_type))
        return

      type_class = type_definition.getTypeClass()
      if type_class in ('Folder', None):
        # wrong type_class, fix it manually:
        from Products.ERP5Type import document_class_registry
        document_class_name = portal_type.replace(' ', '')
        if document_class_name in document_class_registry:
          type_definition.type_class = document_class_name
        else:
          LOG('BaseTool._migrateToPortalTypeClass', WARNING,
              'No document class could be found for portal type %s'
              % portal_type)
          return

      return super(BaseTool, self)._migrateToPortalTypeClass()

InitializeClass(BaseTool)
