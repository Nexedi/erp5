# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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

from zope.interface import Interface

class IIdGenerator(Interface):
  """
  Rounding tool interface
  """

  def generateNewId(id_group=None, default=None, poison=False):
    """
    Generate the next id in the sequence of ids of a particular group

    Parameters :

    id_group (string)
      This is the name of a particular sequence if ids.

    default (string or int or float, depending on the generator)
       Default value of the sequence (optional).
       The first time an id is generated for that sequence, this
       default will be returned.

       If the default value is incompatible with the generator,
       ValueError will be raised.

    poison (bool)
      If True, return the next id in requested sequence, and permanently break
      that sequence's state, so that no new id may be successfuly generated
      from it. Useful to ensure seamless migration away from this generator,
      without risking a (few) late generation from happening after migration
      code already moved sequence's state elsewhere.
    """

  def generateNewIdList(id_group=None, default=None, id_count=1, poison=False):
    """
    Generate a list of next ids in the sequence of ids of a particular group

    Parameters :

    id_group (string)
      This is the name of a particular sequence if ids.

    default (string or int or float, depending on the generator)
       Default value of the sequence (optional).
       The first time an id is generated for that sequence, this
       default will be returned.

       If the default value is incompatible with the generator,
       ValueError will be raised.

    method
       This allows to customize the way id are generated. This
       method should take as parameter the previously generated
       id (optional). By default, ids are managed like integers and
       are increased one by one

    poison (bool)
      If True, return the next id in requested sequence, and permanently break
      that sequence's state, so that no new id may be successfuly generated
      from it. Useful to ensure seamless migration away from this generator,
      without risking a (few) late generation from happening after migration
      code already moved sequence's state elsewhere.
    """

  def initializeGenerator():
    """
    Initialize generator. This is mostly used when a new ERP5 site
    is created. Some generators will need to do some initialization like
    creating SQL Database, prepare some data in ZODB, etc
    """

  def clearGenerator():
    """
    Clear generators data. This can be usefull when working on a
    development instance or in some other rare cases. This will
    loose data and must be use with caution

    This can be incompatible with some particular generator implementation,
    in this case a particular error will be raised (to be determined and
    added here)
    """

  def exportGeneratorIdDict():
    """
    Export last id values in a dictionnary in the form { group_id : last_id }

    This can be incompatible with some particular generator implementation,
    in this case a particular error will be raised (to be determined and
    added here)
    """

  def importGeneratorIdDict(id_dict, clear=False):
    """
    Import data, this is usefull if we want to replace a generator by
    another one. It will allows to make the new generator starting from
    values of the old one

    Parameters :

    id_dict (dict)
      A dictionnary in the form { group_id : last_id }

    clear(bool)
      A boolean to clear the generator before import the data

    This can be incompatible with some particular generator implementation,
    in this case a particular error will be raised (to be determined and
    added here)
    """
