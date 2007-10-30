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

import warnings

from ZPublisher.HTTPRequest import FileUpload
from TypeDefinition import type_definition, list_types, ATTRIBUTE_PREFIX
from Accessor import Accessor as Method
from Acquisition import aq_base
from zLOG import LOG

from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.PsycoWrapper import psyco

# Creation of default constructor
class func_code: pass

class Setter(Method):
    """
      Sets an attribute value. ATTRIBUTE_PREFIX and storage_id allow
      a simple form of data access parametrisations
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    # More information at http://www.zope.org/Members/htrd/howto/FunctionTemplate
    func_code = func_code()
    func_code.co_varnames = ('self','value')
    func_code.co_argcount = 2
    func_defaults = ()

    def __init__(self, id, key, property_type, reindex=1, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._reindex = reindex
      self._property_type = property_type
      self._cast = type_definition[property_type]['cast']
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id

    def __call__(self, instance, *args, **kw):
      value = args[0]
      if not self._reindex:
        # Modify the property
        if value in self._null:
          setattr(instance, self._storage_id, None)
        elif self._property_type == 'content':
          # A file object should be provided
          file_upload = args[0]
          if isinstance(file_upload, FileUpload):
            if file_upload:
              try:
                o = getattr(instance, self._storage_id)
              except AttributeError:
                # We create a default type
                o = instance.PUT_factory(self._storage_id,
                                        file_upload.headers.get('content-type', None), file_upload )
                instance._setObject(self._storage_id, o)
                o = getattr(instance, self._storage_id)
              o.manage_upload(file = file_upload)
          else:
            LOG('ERP5Type WARNING',0,'%s is not an instance of FileUpload' % str(file_upload))
        else:
          setattr(instance, self._storage_id, self._cast(args[0]))
      else:
        # Call the private setter
        warnings.warn("The reindexing accessors are deprecated.\n"
                      "Please use Alias.Reindex instead.",
                      DeprecationWarning)
        method = getattr(instance, '_' + self._id)
        method(*args, **kw)
      if self._reindex: instance.reindexObject() # XXX Should the Setter check
                                                 # if the property value has changed
                                                 # to decide reindexing, like edit() ?

from Products.CMFCore.Expression import Expression
def _evaluateTales(instance=None, value=None):
  from Products.ERP5Type.Utils import createExpressionContext
  expression = Expression(value)
  econtext = createExpressionContext(instance)
  return expression(econtext)

evaluateTales = CachingMethod(_evaluateTales, id = 'evaluateTales', cache_factory='erp5_content_short')

class Getter(Method):
    """
    Gets an attribute value. A default value can be provided if needed.

    Note that 'default' argument is the first positional argument, this is
    important if you want to override a Getter in a class,  overloaded
    accessors have to respect this::

    getSomething(self, [default], [name=value, [name=value], ])

    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, property_type, default=None, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      self._default = default
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id
      self._is_tales_type = (property_type == 'tales')

    def __call__(self, instance, *args, **kw):
      if len(args) > 0:
        default = args[0]
      else:
        default = self._default
      # No acquisition on properties but inheritance.
      # Instead of using getattr, which use inheritance from SuperClass
      # why not use __dict__.get directly ?
      # It seems slower when property is defined, but much more faster if not
      value = getattr(aq_base(instance), self._storage_id, None)
      if value is not None:
        if self._is_tales_type and kw.get('evaluate', 1):
          return evaluateTales(instance, value)
        else:
          return value
      if self._is_tales_type and default is not None and kw.get('evaluate', 1):
        return evaluateTales(instance, default)
      return default

    psyco.bind(__call__)

class Tester(Method):
    """
      Tests if an attribute value exists
    """
    _need__name__=1

    # Generic Definition of Method Object
    # This is required to call the method form the Web
    func_code = func_code()
    func_code.co_varnames = ('self',)
    func_code.co_argcount = 1
    func_defaults = ()

    def __init__(self, id, key, property_type, storage_id=None):
      self._id = id
      self.__name__ = id
      self._key = key
      self._property_type = property_type
      self._null = type_definition[property_type]['null']
      if storage_id is None:
        storage_id = "%s%s" % (ATTRIBUTE_PREFIX, key)
      self._storage_id = storage_id

    def __call__(self, instance, *args, **kw):
      return getattr(aq_base(instance), self._storage_id, None) is not None
