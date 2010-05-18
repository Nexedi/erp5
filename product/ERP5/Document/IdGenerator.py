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

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Cache import caching_instance_method
from Products.ERP5Type.Base import Base
from Products.CMFCore.utils import getToolByName
from zLOG import LOG, INFO

class IdGenerator(Base):
  """
    Generator of Ids
  """
  zope.interface.implements(interfaces.IIdGenerator)
  # CMF Type Definition
  meta_type = 'ERP5 Id Generator'
  portal_type = 'Id Generator'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative property
  property_sheets = ( PropertySheet.Base,
                      PropertySheet.Version,
                      PropertySheet.Reference)

  security.declareProtected(Permissions.AccessContentsInformation,
      'getLatestVersionValue')
  def getLatestVersionValue(self, **kw):
    """
      Return the last generator with the reference
    """
    id_tool = getToolByName(self, 'portal_ids', None)
    last_id = id_tool._getLatestIdGenerator(self.getReference())
    last_version = id_tool._getOb(last_id)
    return last_version

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewId')
  def generateNewId(self, id_group=None, default=None,):
    """
     Generate the next id in the sequence of ids of a particular group
     Use int to store the last_id, use also a persistant mapping for to be
     persistent.
    """
    specialise = self.getSpecialiseValue()
    if specialise is None:
      raise ValueError, "the id generator %s doesn't have specialise value" %\
                        self.getReference()
    return specialise.getLatestVersionValue().generateNewId(id_group=id_group,
                                              default=default)

  security.declareProtected(Permissions.AccessContentsInformation,
      'generateNewIdList')
  def generateNewIdList(self, id_group=None, id_count=1, default=None):
    """
      Generate a list of next ids in the sequence of ids of a particular group
      Store the last id on a database in the portal_ids table
      If stored in zodb is enable, to store the last id use Length inspired
      by BTrees.Length to manage conflict in the zodb, use also a persistant
      mapping to be persistent
    """
    # For compatibilty with sql data, must not use id_group as a list
    if not isinstance(id_group, str):
      raise TypeError, 'id_group is not a string'
    specialise = self.getSpecialiseValue()
    if specialise is None:
      raise ValueError, "the id generator %s doesn't have specialise value" %\
                        self.getReference()
    return specialise.getLatestVersionValue().generateNewIdList(id_group=id_group, \
                                              id_count=id_count, default=default)

  security.declareProtected(Permissions.ModifyPortalContent,
      'initializeGenerator')
  def initializeGenerator(self):
    """
      Initialize generator. This is mostly used when a new ERP5 site
      is created. Some generators will need to do some initialization like
      creating SQL Database, prepare some data in ZODB, etc
    """
    specialise = self.getSpecialiseValue()
    if specialise is None:
      raise ValueError, "the id generator %s doesn't have specialise value" %\
                        self.getReference()
    specialise.getLatestVersionValue().initializeGenerator()

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
    specialise = self.getSpecialiseValue()
    if specialise is None:
      raise ValueError, "the id generator %s doesn't have specialise value" %\
                        self.getReference()
    specialise.getLatestVersionValue().clearGenerator()

