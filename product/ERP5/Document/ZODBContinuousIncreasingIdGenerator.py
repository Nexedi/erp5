##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Daniele Vanbaelinghem <daniele@nexedi.com>
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
from Products.ERP5Type.Utils import ensure_list

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, interfaces
from Products.ERP5.Document.IdGenerator import IdGenerator
from BTrees.OOBTree import OOBTree

from zLOG import LOG, INFO

@zope.interface.implementer(interfaces.IIdGenerator)
class ZODBContinuousIncreasingIdGenerator(IdGenerator):
  """
    Create some Ids with the zodb storage
  """
  # CMF Type Definition
  meta_type = 'ERP5 ZODB Continous Increasing Id Generator'
  portal_type = 'ZODB Continous Increasing Id Generator'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _generateNewId(self, id_group, id_count=1, default=None, poison=False):
    """
     Return the new_id from the last_id of the zodb
     Use int to store the last_id, use also a persistant mapping for to be
     persistent.
    """
    if id_group in (None, 'None'):
      raise ValueError('%r is not a valid group Id.' % id_group)
    if not isinstance(id_group, str):
      raise TypeError('id_group must be str')
    if default is None:
      default = 0
    last_id_dict = getattr(self, 'last_id_dict', None)
    if last_id_dict is None:
      # If the dictionary not exist initialize generator
      self.initializeGenerator()
      last_id_dict = self.last_id_dict
    # Retrieve the last id and increment
    new_id = last_id_dict.get(id_group, default - 1) + id_count
    # Store the new_id in the dictionary
    last_id_dict[id_group] = None if poison else new_id
    return new_id

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewId')
  def generateNewId(self, id_group=None, default=None, poison=False):
    """
      Generate the next id in the sequence of ids of a particular group
    """
    return self._generateNewId(id_group=id_group, default=default, poison=poison)

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewIdList')
  def generateNewIdList(self, id_group=None, id_count=1, default=None, poison=False):
    """
      Generate a list of next ids in the sequence of ids of a particular group
    """
    new_id = 1 + self._generateNewId(id_group=id_group, id_count=id_count,
                                     default=default, poison=poison)
    return ensure_list(range(new_id - id_count, new_id))

  security.declareProtected(Permissions.ModifyPortalContent,
      'initializeGenerator')
  def initializeGenerator(self):
    """
      Initialize generator. This is mostly used when a new ERP5 site
      is created. Some generators will need to do some initialization like
      prepare some data in ZODB
    """
    LOG('initialize ZODB Generator', INFO, 'Id Generator: %s' % (self,))
    if getattr(self, 'last_id_dict', None) is None:
      self.last_id_dict = OOBTree()

    # XXX compatiblity code below, dump the old dictionnaries
    portal_ids = getattr(self, 'portal_ids', None)
    # Dump the dict_ids dictionary
    if getattr(portal_ids, 'dict_ids', None) is not None:
      for id_group, last_id in portal_ids.dict_ids.items():
        if not isinstance(id_group, str):
          assert not isinstance(id_group, bytes), id_group
          id_group = repr(id_group)
        if id_group in self.last_id_dict and \
           self.last_id_dict[id_group] > last_id:
          continue
        self.last_id_dict[id_group] = last_id

  security.declareProtected(Permissions.ModifyPortalContent,
      'clearGenerator')
  def clearGenerator(self):
    """
      Clear generators data. This can be usefull when working on a
      development instance or in some other rare cases. This will
      loose data and must be use with caution

      This can be incompatible with some particular generator implementation,
      in this case a particular error will be raised (to be determined and
      added here)
    """
    # Remove dictionary
    self.last_id_dict = OOBTree()

  security.declareProtected(Permissions.ModifyPortalContent,
      'exportGeneratorIdDict')
  def exportGeneratorIdDict(self):
    """
      Export last id values in a dictionnary in the form { group_id : last_id }
    """
    return dict(self.last_id_dict)

  security.declareProtected(Permissions.ModifyPortalContent,
      'importGeneratorIdDict')
  def importGeneratorIdDict(self, id_dict, clear=False):
    """
      Import data, this is usefull if we want to replace a generator by
      another one.
    """
    if clear:
      self.clearGenerator()
    if not isinstance(id_dict, dict):
      raise TypeError('the argument given is not a dictionary')
    for key, value in id_dict.items():
      if not isinstance(key, str):
        raise TypeError('key %r given in dictionary is not str' % (key, ))
      if not isinstance(value, six.integer_types):
        raise TypeError('the value given in dictionary is not a integer')
    self.last_id_dict.update(id_dict)

  security.declareProtected(Permissions.ModifyPortalContent,
       'rebuildGeneratorIdDict')
  def rebuildGeneratorIdDict(self):
    """
      Rebuild generator id dict.
      In fact, export it, clear it and import it into new dict.
      This is mostly intendted to use when we are migrating the id dict
      structure.
    """
    id_dict = self.exportGeneratorIdDict()
    self.importGeneratorIdDict(id_dict=id_dict, clear=True)


