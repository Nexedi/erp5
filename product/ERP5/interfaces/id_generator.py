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

  def generateNewId(id_group=None, default=None):
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

    """

  def generateNewIdList(id_group=None, default=None, id_count=1):
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
    """
