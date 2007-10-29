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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName

from Products.ERP5 import _dtmldir

import threading

from BTrees.Length import Length

class IdTool(BaseTool):
  """
    This tools handles the generation of IDs.

    TODO - XXX: please use base tool
  """
  id = 'portal_ids'
  meta_type = 'ERP5 Id Tool'
  portal_type = 'Id Tool'

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainIdTool', _dtmldir )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getLastGeneratedId')
  def getLastGeneratedId(self,id_group=None,default=None):
    """
    Get the last id generated
    """
    if getattr(self, 'dict_ids', None) is None:
      self.dict_ids = PersistentMapping()
    last_id = None
    if id_group is not None and id_group!='None':
      last_id = self.dict_ids.get(id_group, default)
    return last_id
        
  security.declareProtected(Permissions.ModifyPortalContent,
                            'setLastGeneratedId')
  def setLastGeneratedId(self,new_id,id_group=None):
    """
    Set a new last id. This is usefull in order to reset
    a sequence of ids.
    """
    if getattr(self, 'dict_ids', None) is None:
      self.dict_ids = PersistentMapping()
    if id_group is not None and id_group!='None':
      l = threading.Lock()
      l.acquire()
      try:
        self.dict_ids[id_group] = new_id
      finally:
        l.release()
        
  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewId')
  def generateNewId(self, id_group=None, default=None, method=None):
    """
      Generate a new Id
    """
    
    if getattr(self, 'dict_ids', None) is None:
      self.dict_ids = PersistentMapping()

    new_id = None
    if id_group is not None and id_group!='None':
      # Getting the last id
      last_id = None
      l = threading.Lock()
      l.acquire()
      try:
        class Dummy:
          pass
        dummy = Dummy()
        last_id = self.dict_ids.get(id_group, dummy)
        if last_id is dummy:
          if default is None:
            new_id=0
          else:
            new_id=default

        else:
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewLongId')
  def generateNewLongId(self, **kw):
    """
      Returns the ZODB transation id to be used as an identifier.
      It's a 64bits number, so it can look ugly and/or huge to users.
    """
    tid = get_transaction()._id;
    # It's a 64 bits number, but sometimes it returns as a negative int... so
    # make it positive again and add 2**63.
    return (tid < 0) and (2**63 - tid) or tid;

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getDictLengthIdsItems')
  def getDictLengthIdsItems(self):
    """
      Return a copy of dict_length_ids.
      This is a workaround to access the persistent mapping content from ZSQL
      method to be able to insert initial tuples in the database at creation.
    """
    if getattr(self, 'dict_length_ids', None) is None:
      self.dict_length_ids = PersistentMapping()
    return self.dict_length_ids.items()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewLengthIdList')
  def generateNewLengthIdList(self, id_group=None, id_count=1, default=None,
                              store=1):
    """
      Generates a list of Ids.
      The ids are generated using mysql and then stored in a Length object in a
      persistant mapping to be persistent.
      We use MySQL to generate IDs, because it is atomic and we don't want
      to generate any conflict at zope level. The possible downfall is that
      some IDs might be skipped because of failed transactions.
      "Length" is because the id is stored in a python object inspired by
      BTrees.Length. It doesn't have to be a length.

      store : if we want do store the new id into the zodb, we want it
              by default
    """
    if getattr(self, 'dict_length_ids', None) is None:
      # Length objects are stored in a persistent mapping: there is one
      # Length object per id_group.
      self.dict_length_ids = PersistentMapping()

    new_id = None
    if id_group in (None, 'None'):
      raise ValueError, '%s is not a valid group Id.' % (repr(id_group), )
    if not isinstance(id_group, str):
      id_group = repr(id_group)
    if default is None:
      default = 1
    # FIXME: A skin folder should be used to contain ZSQLMethods instead of
    # default catalog, like activity tool (anyway, it uses activity tool
    # ZSQLConnection, so hot reindexing is not helping here).
    portal_catalog = getToolByName(self, 'portal_catalog').getSQLCatalog()
    query = getattr(portal_catalog, 'z_portal_ids_generate_id')
    commit = getattr(portal_catalog, 'z_portal_ids_commit')
    if None in (query, commit):
      raise AttributeError, 'Error while generating Id: ' \
        'z_portal_ids_generate_id and/or z_portal_ids_commit could not ' \
        'be found.'
    try:
      result = query(id_group=id_group, id_count=id_count, default=default)
    finally:
      commit()
    new_id = result[0]['LAST_INSERT_ID()']
    if self.dict_length_ids.get(id_group) is None:
      self.dict_length_ids[id_group] = Length(new_id)
    if store:
      self.dict_length_ids[id_group].set(new_id)
    return range(new_id - id_count, new_id)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewLengthId')
  def generateNewLengthId(self, id_group=None, default=None, store=1):
    """
      Generates an Id.
      See generateNewLengthIdList documentation for details.
    """
    return self.generateNewLengthIdList(id_group=id_group, id_count=1, 
        default=default, store=store)[0]

InitializeClass(IdTool)
