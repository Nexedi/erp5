from __future__ import absolute_import
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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

from past.builtins import cmp
from .Accessor import Accessor

# Creation of default constructor
class func_code: pass

class PropertyGetter:
  """
  This is class is mostly used in order to handle compatibility
  issues when we wish to make a property a method. For instance,
  we would like to change from isIndexable=1 to a method isIndexable().
  """
  __code__ = func_code = func_code()
  __code__.co_varnames = ()
  __code__.co_argcount = 0
  __defaults__ = func_defaults = ()

  def __init__(self, id, value=None):
    self._id = id
    self.__name__ = id
    self.value = value

  def __call__(self):
    return self.value

  def __bool__(self):
    return bool(self.value)
  __nonzero__ = __bool__ # six.PY2

  def __int__(self):
    return int(self.value)

  def __float__(self):
    return float(self.value)

  # following methods are used for < > == != , etc
  def __eq__(self, other):
    return int(self.value) == int(other)

  def __ne__(self, other):
    return int(self.value) != int(other)

  def __cmp__(self, other):
    return cmp(int(self.value), int(other))

class Getter(Accessor):
  """
  Returns a constant value, either by method call
  or through type cast (ex. boolean, int, float).
  This method can be useful to turn existing constant
  properties of classes into methods, yet retaining
  compatibility.
  """
  _need__name__ = 1

  # Generic Definition of Method Object
  # This is required to call the method form the Web
  # More information at http://www.zope.org/Members/htrd/howto/FunctionTemplate
  __code__ = func_code = func_code()
  __code__.co_varnames = ('self', )
  __code__.co_argcount = 1
  __defaults__ = func_defaults = ()

  def __init__(self, id, key, value=None):
    self._id = id
    self._key = key
    self.__name__ = id
    self.value = value
    # Do not publish deprecated Constant getter
    self.__doc__ = None

  def __call__(self, instance):
    return self.value
