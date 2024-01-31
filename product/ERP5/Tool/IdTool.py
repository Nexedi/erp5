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

import six
import warnings
import zope.interface

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type.Cache import caching_instance_method
from Products.ERP5Type import Permissions, interfaces
from zLOG import LOG, WARNING, INFO, ERROR
from Products.ERP5 import _dtmldir

from BTrees.Length import Length

_marker = object()

@zope.interface.implementer(interfaces.IIdTool)
class IdTool(BaseTool):
  """
    This tools handles the generation of IDs.
  """
  id = 'portal_ids'
  meta_type = 'ERP5 Id Tool'
  portal_type = 'Id Tool'
  title = 'Id Generators'

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainIdTool', _dtmldir )

  def newContent(self, *args, **kw):
    """
      the newContent is overriden to not use generateNewId
    """
    if id not in kw:
      new_id = self._generateNextId()
      if new_id is not None:
        kw['id'] = new_id
      else:
        raise ValueError('Failed to gererate id')
    return BaseTool.newContent(self, *args, **kw)

  def _get_id(self, id):
    """
      _get_id is overrided to not use generateNewId
      It is used for example when an object is cloned
    """
    if self._getOb(id, None) is None :
      return id
    return self._generateNextId()

  @caching_instance_method(id='IdTool._getLatestIdGenerator',
    cache_factory='erp5_content_long')
  def _getLatestIdGenerator(self, reference):
    """
      Tries to find the id_generator with the latest version
      from the current object.
      Use the low-level to create a site without catalog
    """
    assert reference
    id_last_generator = None
    version_last_generator = 0
    for generator in self.objectValues():
      if generator.getReference() == reference:
        # Version Property Sheet defines 'version' property as a 'string'
        version = int(generator.getVersion())
        if version > version_last_generator:
          id_last_generator = generator.getId()
          version_last_generator = version
    if id_last_generator is None:
      raise KeyError(repr(reference))
    return id_last_generator

  def _getLatestGeneratorValue(self, id_generator):
    """
      Return the last generator with the reference
    """
    return self._getOb(self._getLatestIdGenerator(id_generator))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewId')
  def generateNewId(self, id_group=None, default=None, method=_marker,
                    id_generator=None, poison=False):
    """
      Generate the next id in the sequence of ids of a particular group
    """
    if id_group in (None, 'None'):
      raise ValueError('%r is not a valid id_group' % id_group)
    # for compatibilty with sql data, must not use id_group as a list
    if six.PY3 and isinstance(id_group, bytes):
      warnings.warn('id_group must be a string, not bytes.', BytesWarning)
      id_group = id_group.decode('utf-8')
    if not isinstance(id_group, str):
      id_group = repr(id_group)
      warnings.warn('id_group must be a string, other types '
                    'are deprecated.', DeprecationWarning)
    if id_generator is None:
      id_generator = 'document'
    if method is not _marker:
      warnings.warn("Use of 'method' argument is deprecated", DeprecationWarning)
    try:
      #use _getLatestGeneratorValue here for that the technical level
      #must not call the method
      last_generator = self._getLatestGeneratorValue(id_generator)
      new_id = last_generator.generateNewId(
        id_group=id_group,
        default=default,
        poison=poison,
      )
    except KeyError:
      # XXX backward compatiblity
      if self.getTypeInfo():
        LOG('generateNewId', ERROR, 'while generating id')
        raise
      else:
        # Compatibility code below, in case the last version of erp5_core
        # is not installed yet
        warnings.warn("You are using an old version of erp5_core to generate"
                      "ids.\nPlease update erp5_core business template to "
                      "use new id generators", DeprecationWarning)
        dict_ids = getattr(aq_base(self), 'dict_ids', None)
        if dict_ids is None:
          dict_ids = self.dict_ids = PersistentMapping()
        new_id = None
        # Getting the last id
        if default is None:
          default = 0
        marker = []
        new_id = dict_ids.get(id_group, marker)
        if method is _marker:
          if new_id is marker:
            new_id = default
          else:
            new_id = new_id + 1
        else:
          if new_id is marker:
            new_id = default
          new_id = method(new_id)
        # Store the new value
        dict_ids[id_group] = new_id
    return new_id

  security.declareProtected(Permissions.AccessContentsInformation,
                            'generateNewIdList')
  def generateNewIdList(self, id_group=None, id_count=1, default=None,
                        store=_marker, id_generator=None, poison=False):
    """
      Generate a list of next ids in the sequence of ids of a particular group
    """
    if id_group in (None, 'None'):
      raise ValueError('%r is not a valid id_group' % id_group)
    if six.PY3 and isinstance(id_group, bytes):
      warnings.warn('id_group must be a string, not bytes.', BytesWarning)
      id_group = id_group.decode('utf-8')
    # for compatibilty with sql data, must not use id_group as a list
    if not isinstance(id_group, str):
      id_group = repr(id_group)
      warnings.warn('id_group must be a string, other types '
                    'are deprecated.', DeprecationWarning)
    if id_generator is None:
      id_generator = 'uid'
    if store is not _marker:
      warnings.warn("Use of 'store' argument is deprecated.",
                    DeprecationWarning)
    try:
      #use _getLatestGeneratorValue here for that the technical level
      #must not call the method
      last_generator = self._getLatestGeneratorValue(id_generator)
      new_id_list = last_generator.generateNewIdList(id_group=id_group,
                         id_count=id_count, default=default, poison=poison)
    except (KeyError, ValueError):
      # XXX backward compatiblity
      if self.getTypeInfo():
        LOG('generateNewIdList', ERROR, 'while generating id')
        raise
      else:
        # Compatibility code below, in case the last version of erp5_core
        # is not installed yet
        warnings.warn("You are using an old version of erp5_core to generate"
                      "ids.\nPlease update erp5_core business template to "
                      "use new id generators", DeprecationWarning)
        new_id = None
        if default is None:
          default = 1
        # XXX It's temporary, a New API will be implemented soon
        #     the code will be change
        portal = self.getPortalObject()
        try:
          query = portal.IdTool_zGenerateId
          commit = portal.IdTool_zCommit
        except AttributeError:
          portal_catalog = portal.portal_catalog.getSQLCatalog()
          query = portal_catalog.z_portal_ids_generate_id
          commit = portal_catalog.z_portal_ids_commit
        try:
          result = query(id_group=id_group, id_count=id_count, default=default)
        finally:
          commit()
        new_id = result[0]['LAST_INSERT_ID()']
        if store:
          if getattr(aq_base(self), 'dict_length_ids', None) is None:
            # Length objects are stored in a persistent mapping: there is one
            # Length object per id_group.
            self.dict_length_ids = PersistentMapping()
          if self.dict_length_ids.get(id_group) is None:
            self.dict_length_ids[id_group] = Length(new_id)
          self.dict_length_ids[id_group].set(new_id)
        if six.PY2:
          new_id_list = range(new_id - id_count, new_id)
        else:
          new_id_list = list(range(new_id - id_count, new_id))
    return new_id_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'initializeGenerator')
  def initializeGenerator(self, id_generator=None, all=False):
    """
    Initialize generators. This is mostly used when a new ERP5 site
    is created. Some generators will need to do some initialization like
    creating SQL Database, prepare some data in ZODB, etc
    """
    if not all:
      #Use _getLatestGeneratorValue here for that the technical level
      #must not call the method
      last_generator = self._getLatestGeneratorValue(id_generator)
      last_generator.initializeGenerator()
    else:
      # recovery all the generators and initialize them
      for generator in self.objectValues(\
                       portal_type='Application Id Generator'):
        generator.initializeGenerator()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'clearGenerator')
  def clearGenerator(self, id_generator=None, all=False):
    """
    Clear generators data. This can be usefull when working on a
    development instance or in some other rare cases. This will
    loose data and must be use with caution

    This can be incompatible with some particular generator implementation,
    in this case a particular error will be raised (to be determined and
    added here)
    """
    if not all:
      #Use _getLatestGeneratorValue here for that the technical level
      #must not call the method
      last_generator = self._getLatestGeneratorValue(id_generator)
      last_generator.clearGenerator()

    else:
      if len(self.objectValues()) == 0:
        # compatibility with old API
        self.getPortalObject().IdTool_zDropTable()
        self.getPortalObject().IdTool_zCreateTable()
      for generator in self.objectValues(\
                       portal_type='Application Id Generator'):
        generator.clearGenerator()

  ## XXX Old API deprecated
  #backward compatibility
  security.declareProtected(Permissions.AccessContentsInformation,
                           'generateNewLengthIdList')
  generateNewLengthIdList = generateNewIdList

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getLastLengthGeneratedId')
  def getLastLengthGeneratedId(self, id_group, default=None):
    """
    Get the last length id generated
    """
    warnings.warn('getLastLengthGeneratedId is deprecated',
                   DeprecationWarning)
    # check in persistent mapping if exists
    if getattr(aq_base(self), 'dict_length_ids', None) is not None:
      last_id = self.dict_length_ids.get(id_group)
      if last_id is not None:
        return last_id.value - 1
    # otherwise check in mysql
    # XXX It's temporary, a New API will be implemented soon
    #     the code will be change
    portal = self.getPortalObject()
    try:
      query = portal.IdTool_zGetLastId
    except AttributeError:
      query = portal.portal_catalog.getSQLCatalog().z_portal_ids_get_last_id
    result = query(id_group=id_group)
    if len(result):
      try:
        return result[0]['last_id']
      except KeyError:
        return result[0]['LAST_INSERT_ID()']
    return default

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getLastGeneratedId')
  def getLastGeneratedId(self, id_group=None, default=None):
    """
    Get the last id generated
    """
    warnings.warn('getLastGeneratedId is deprecated', DeprecationWarning)
    if getattr(aq_base(self), 'dict_ids', None) is None:
      self.dict_ids = PersistentMapping()
    last_id = None
    if id_group is not None and id_group != 'None':
      last_id = self.dict_ids.get(id_group, default)
    return last_id

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setLastGeneratedId')
  def setLastGeneratedId(self, new_id, id_group=None):
    """
    Set a new last id. This is usefull in order to reset
    a sequence of ids.
    """
    if getattr(aq_base(self), 'dict_ids', None) is None:
      self.dict_ids = PersistentMapping()
    if id_group is not None and id_group != 'None':
      self.dict_ids[id_group] = new_id

  security.declareProtected(Permissions.AccessContentsInformation,
                           'generateNewLengthId')
  def generateNewLengthId(self, id_group=None, default=None, store=_marker):
     """Generates an Id using a conflict free id generator. Deprecated.
     """
     warnings.warn('generateNewLengthId is deprecated.\n'
                   'Use generateNewIdList with a sql id_generator',
                   DeprecationWarning)
     if store is not _marker:
       return self.generateNewIdList(id_group=id_group,
                        id_count=1, default=default, store=store)[0]
     return self.generateNewIdList(id_group=id_group,
                        id_count=1, default=default)[0]

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

  security.declarePrivate('dumpDictLengthIdsItems')
  def dumpDictLengthIdsItems(self):
    """
      Store persistently data from SQL table portal_ids.
    """
    portal_catalog = getattr(self, 'portal_catalog').getSQLCatalog()
    query = getattr(portal_catalog, 'z_portal_ids_dump')
    dict_length_ids = getattr(aq_base(self), 'dict_length_ids', None)
    if dict_length_ids is None:
      dict_length_ids = self.dict_length_ids = PersistentMapping()
    for line in query().dictionaries():
      id_group = line['id_group']
      last_id = line['last_id']
      stored_last_id = self.dict_length_ids.get(id_group)
      if stored_last_id is None:
        self.dict_length_ids[id_group] = Length(last_id)
      else:
        stored_last_id_value = stored_last_id()
        if stored_last_id_value < last_id:
          stored_last_id.set(last_id)
        else:
          if stored_last_id_value > last_id:
            LOG('IdTool', WARNING, 'ZODB value (%r) for group %r is higher ' \
                'than SQL value (%r). Keeping ZODB value untouched.' % \
                (stored_last_id, id_group, last_id))

InitializeClass(IdTool)
