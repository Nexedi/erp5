##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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

from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Method
from Products.ERP5Type.PsycoWrapper import psyco
from zLOG import LOG
from zLOG import WARNING


class DefaultGetter(Method):
  """
  Gets a default reference object
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, warning=0):
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    return instance._getDefaultRelatedProperty(
                           self._key, 'relative_url',
                           spec=kw.get('spec',()),
                           filter=kw.get('filter', None),
                           portal_type=kw.get('portal_type',()),
                           checked_permission=kw.get('checked_permission', None))

  psyco.bind(__call__)

Getter = DefaultGetter

class ListGetter(Method):
  """
  Gets a list of reference objects
  """
  _need__name__=1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  func_code = func_code()
  func_code.co_varnames = ('self', )
  func_code.co_argcount = 1
  func_defaults = ()

  def __init__(self, id, key, warning=0):
    self._id = id
    self.__name__ = id
    self._key = key
    self._warning = warning

  def __call__(self, instance, *args, **kw):
    if self._warning:
      LOG("ERP5Type", WARNING, "Deprecated Getter Id: %s" % self._id)
    return instance._getRelatedPropertyList(
                          self._key, 'relative_url',
                          spec=kw.get('spec',()),
                          filter=kw.get('filter', None),
                          portal_type=kw.get('portal_type',()),
                          checked_permission=kw.get('checked_permission', None))

  psyco.bind(__call__)

class SetGetter(ListGetter):
  """
  Gets a category value set
  """
  def __call__(self, instance, *args, **kw):
    result_list = ListGetter.__call__(self, instance, *args, **kw)
    result_set = dict([(x, 0) for x in result_list]).keys()
    return result_set
