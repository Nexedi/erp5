##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type import Permissions

from Products.ERP5 import _dtmldir

import threading

from zLOG import LOG

class IdTool(UniqueObject, Folder):
    """
    This tools allows to generate new ids
    """
    id = 'portal_ids'
    meta_type = 'ERP5 Id Tool'
    portal_type = 'Id Tool'
    allowed_types = ( 'ERP5 Order Rule', 'ERP5 Transformation Rule',)

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
    manage_overview = DTMLFile( 'explainIdTool', _dtmldir )

    # Filter content (ZMI))
    def __init__(self):
      return Folder.__init__(self, IdTool.id)
        

    # Filter content (ZMI))
    def generateNewId(self, id_group=None, default=None, method=None):
      """
      Generate a new Id

      XXX We should in the future use class instead of method to generate
      new ids. It would be nice to have a management page giving the list
      of id_group with each time the last_id and the class generator
      """
      LOG('generateNewId',0,'id_group: %s' % str(id_group))
      if not hasattr(self,'dict_ids'):
        self.dict_ids = PersistentMapping()

      LOG('generateNewId',0,'dict_ids: %s' % str(self.dict_ids))
      new_id = None
      if id_group is not None and id_group!='None':
        # Getting the last id
        last_id = None
        l = threading.Lock()
        l.acquire()
        try:
          if self.dict_ids.has_key(id_group):
            last_id = self.dict_ids[id_group]
          elif default is not None:
            last_id = default
          else:
            last_id = 0

          # Now generate a new id
          if method is not None:
            new_id = method(last_id)
          else:
            new_id = last_id + 1
          
          # Store the new value
          self.dict_ids[id_group] = new_id
        finally:
          l.release()

      return new_id




InitializeClass(IdTool)
