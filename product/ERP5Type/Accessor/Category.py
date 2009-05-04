##############################################################################
#
# Copyright (c) 2002-2003 Nexedi SARL and Contributors. All Rights Reserved.
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


from Base import func_code, type_definition, list_types, ATTRIBUTE_PREFIX, Setter as BaseSetter, Getter as BaseGetter
from zLOG import LOG
from Products.ERP5Type.PsycoWrapper import psyco

class ListSetter(BaseSetter):
    """
      Sets a category
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', 'category')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      instance._setCategoryMembership(self._key, args[0],
                                      spec=kw.get('spec',()),
                                      filter=kw.get('filter', None),
                                      portal_type=kw.get('portal_type',()),
                                      base=kw.get('base', 0),
                                      keep_default=0,
                                      checked_permission=kw.get('checked_permission', None))
      return (instance, )

Setter = ListSetter

class DefaultSetter(BaseSetter):
    """
      Sets a category
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', 'category')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      instance._setDefaultCategoryMembership(self._key, args[0],
                                                 spec=kw.get('spec',()),
                                                 filter=kw.get('filter', None),
                                                 portal_type=kw.get('portal_type',()),
                                                 base=kw.get('base', 0),
                                                 checked_permission=kw.get('checked_permission', None))
      return (instance, )

class SetSetter(BaseSetter):
    """
      Sets a set of category
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', 'category')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      """
      We should take care that the provided argument has no
      duplicate values
      """
      if type(args[0]) in (type([]),type(())):
        new_list = []
        for item in args[0]:
          if item not in new_list:
            new_list.append(item)
      else:
        new_list = args[0]
      instance._setCategoryMembership(self._key, new_list,
                                      spec=kw.get('spec',()),
                                      filter=kw.get('filter', None),
                                      portal_type=kw.get('portal_type',()),
                                      base=kw.get('base', 0),
                                      keep_default=1,
                                      checked_permission=kw.get('checked_permission', None))
      return (instance, )


class DefaultGetter(BaseGetter):
    """
      Gets a default category value
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
        kw['default'] = default
      else:
        default = None
      return instance._getDefaultAcquiredCategoryMembership(self._key, **kw)
    psyco.bind(__call__)

class ListGetter(BaseGetter):
    """
      Gets a category value list
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      if not kw.has_key('base'):
        kw['base'] = 0
      return instance._getAcquiredCategoryMembershipList(self._key, **kw)
    psyco.bind(__call__)

class SetGetter(ListGetter):
    """
    Gets a category value set
    """
    def __call__(self, instance, *args, **kw):
      result_list = ListGetter.__call__(self, instance, *args, **kw)
      result_set = dict([(x, 0) for x in result_list]).keys()
      return result_set


# ItemList is outdated XXX -> ItemList

class ItemListGetter(BaseGetter):
    """
      Gets a category value list
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self', 'args', 'kw',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key):
      self._id = id
      self.__name__ = id
      self._key = key

    def __call__(self, instance, *args, **kw):
      return instance._getAcquiredCategoryMembershipItemList(self._key, base=0, **kw)

    psyco.bind(__call__)


class Tester(ListGetter):
  """Tests if the category is set.
  """
  def __call__(self, instance, *args, **kw):
    return not not ListGetter.__call__(self, instance, *args, **kw)

