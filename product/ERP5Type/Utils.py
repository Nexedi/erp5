# -*- coding: utf-8 -*-
#############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

# Required modules - some modules are imported later to prevent circular deadlocks
import os
import re
import string
import time
import warnings
import sys
import inspect
import persistent
from hashlib import md5 as md5_new, sha1 as sha_new
from Products.ERP5Type.Globals import package_home
from Products.ERP5Type.Globals import DevelopmentMode
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_self

from AccessControl import ModuleSecurityInfo
from AccessControl.SecurityInfo import allow_class
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager

from Products.CMFCore import utils
from Products.CMFCore.Expression import Expression
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.ZCatalog.Lazy import LazyMap

try:
  import chardet
except ImportError:
  chardet = None
try:
  import magic
except ImportError:
  magic = None

def simple_decorator(decorator):
  """Decorator to turn simple function into well-behaved decorator

  See also http://wiki.python.org/moin/PythonDecoratorLibrary

  XXX We should use http://pypi.python.org/pypi/decorator/ instead,
      to make decorators ZPublisher-friendly.
  """
  def new_decorator(f):
    g = decorator(f)
    g.__name__ = f.__name__
    g.__doc__ = f.__doc__
    g.__dict__.update(f.__dict__)
    return g
  # Now a few lines needed to make simple_decorator itself
  # be a well-behaved decorator.
  new_decorator.__name__ = decorator.__name__
  new_decorator.__doc__ = decorator.__doc__
  new_decorator.__dict__.update(decorator.__dict__)
  return new_decorator

from Products.ERP5Type import Permissions
from Products.ERP5Type import document_class_registry
from Products.ERP5Type.Accessor.Constant import PropertyGetter as \
    PropertyConstantGetter
from Products.ERP5Type.Accessor.Constant import Getter as ConstantGetter
from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
from zLOG import LOG, BLATHER, PROBLEM, WARNING, INFO, TRACE

#####################################################
# Avoid importing from (possibly unpatched) Globals
#####################################################
from Products.ERP5Type.Globals import get_request

#####################################################
# Compatibility - XXX - BAD
#####################################################

from Accessor.TypeDefinition import type_definition
from Accessor.TypeDefinition import list_types

#####################################################
# Generic sort method
#####################################################

sort_kw_cache = {}

def sortValueList(value_list, sort_on=None, sort_order=None, **kw):
  """Sort values in a way compatible with ZSQLCatalog.
  """
  if sort_on is not None:
    if isinstance(sort_on, str):
      sort_on = (sort_on,)
    # try to cache keyword arguments for sort()
    sort_on = tuple([isinstance(x, str) and x or tuple(x) for x in sort_on])
    try:
      sort_kw = sort_kw_cache[(sort_on, sort_order)]
    except (KeyError, TypeError):
      new_sort_on = []
      reverse_dict = {}
      for key in sort_on:
        if isinstance(key, str):
          reverse = (sort_order in ('descending', 'reverse', 'DESC'))
          new_sort_on.append((key, reverse, None))
          reverse_dict[reverse] = True
        else:
          if len(key) == 1:
            reverse = (sort_order in ('descending', 'reverse', 'DESC'))
            new_sort_on.append((key[0], reverse, None))
            reverse_dict[reverse] = True
          elif len(key) == 2:
            reverse = (key[1] in ('descending', 'reverse', 'DESC'))
            new_sort_on.append((key[0], reverse, None))
            reverse_dict[reverse] = True
          else:
            # Emulate MySQL types
            as_type = key[2].lower()
            if as_type in ('int', 'bigint'):
              f=int
            elif as_type in ('float', 'real', 'double'):
              f=float
            else:
              # XXX: For an unknown type, use a string.
              f=str
            reverse = (key[1] in ('descending', 'reverse', 'DESC'))
            new_sort_on.append((key[0], reverse, f))
            reverse_dict[reverse] = True

      if len(reverse_dict) == 1:
        # if we have only one kind of reverse value (i.e. all True or all
        # False), we can use sort(key=func) that is faster than
        # sort(cmp=func).
        def sortValue(a):
          value_list = []
          for key, reverse, as_type in new_sort_on:
            x = a.getProperty(key, None)
            if as_type is not None:
              try:
                x = as_type(x)
              except TypeError:
                pass
            value_list.append(x)
          return value_list
        sort_kw = {'key':sortValue, 'reverse':reverse}
        sort_kw_cache[(sort_on, sort_order)] = sort_kw
      else:
        # otherwise we use sort(cmp=func).
        def sortValues(a, b):
          result = 0
          for key, reverse, as_type in new_sort_on:
            x = a.getProperty(key, None)
            y = b.getProperty(key, None)
            if as_type is not None:
              try:
                x = as_type(x)
                y = as_type(y)
              except TypeError:
                pass
            result = cmp(x, y)
            if reverse:
              result = -result
            if result != 0:
              break
          return result
        sort_kw = {'cmp':sortValues}
        sort_kw_cache[(sort_on, sort_order)] = sort_kw

    if isinstance(value_list, LazyMap):
      new_value_list = [x for x in value_list]
      value_list = new_value_list

    value_list.sort(**sort_kw)

  return value_list

#####################################################
# Logging
#####################################################

def _showwarning(message, category, filename, lineno, file=None, line=None):
  if file is None:
    LOG("%s:%u %s: %s" % (filename, lineno, category.__name__, message),
        WARNING, '')
  else:
    # BACK: In Python 2.6 we need to pass along the "line" parameter to
    # formatwarning(). For now we don't to keep backward compat with Python 2.4
    file.write(warnings.formatwarning(message, category, filename, lineno))
warnings.showwarning = _showwarning

def deprecated(message=''):
  @simple_decorator
  def _deprecated(wrapped):
    m = message or "Use of '%s' function (%s, line %s) is deprecated." % (
      wrapped.__name__, wrapped.__module__, wrapped.func_code.co_firstlineno)
    def deprecated(*args, **kw):
      warnings.warn(m, DeprecationWarning, 2)
      return wrapped(*args, **kw)
    return deprecated
  if callable(message):
    m, message = message, ''
    return _deprecated(m)
  return _deprecated

#####################################################
# Useful methods
#####################################################

_cached_convertToUpperCase = {}
def convertToUpperCase(key):
  """
    This function turns an attribute name into
    a method name according to the ERP5 naming conventions
  """
  try:
    return _cached_convertToUpperCase[key]
  except KeyError:
    if not isinstance(key, basestring):
      raise TypeError, '%s is not a string' % (key,)
    _cached_convertToUpperCase[key] = ''.join([part.capitalize() for part in key.split('_')])
    return _cached_convertToUpperCase[key]

UpperCase = convertToUpperCase

def convertToLowerCase(key):
  tmp = []
  assert(key[0].isupper())
  for i in key:
    if i.isupper():
      tmp.append('_')
      tmp.append(i.lower())
    else:
      tmp.append(i)
  return ''.join(tmp)
LowerCase = convertToLowerCase


def convertToMixedCase(key):
  """
    This function turns an attribute name into
    a method name according to the ERP5 naming conventions
  """
  if not isinstance(key, basestring):
    raise TypeError, '%s is not a string' % (key,)
  parts = str(key).split('_', 1)
  if len(parts) == 2:
    parts[1] = convertToUpperCase(parts[1])
  return ''.join(parts)

# Some set operations
def cartesianProduct(list_of_list):
  """
    Be carefull : one mathematical property of cartesian product is that
    when you do a cartesian products of a set and an empty set, the result
    is an empty set.
  """
  if len(list_of_list) == 0:
    return [[]]
  result = []
  append = result.append
  head = list_of_list[0]
  tail = list_of_list[1:]
  product = cartesianProduct(tail)
  for v in head:
    for p in product:
      append([v] + p)
  return result

# Some list operations
def keepIn(value_list, filter_list):
  # XXX this is [x for x in value_list if x in filter_list]
  result = []
  for k in value_list:
    if k in filter_list:
      result += [k]
  return result

def rejectIn(value_list, filter_list):
  # XXX this is [x for x in value_list if x not in filter_list]
  result = []
  for k in value_list:
    if not(k in filter_list):
      result += [k]
  return result

# Conversions between path, object and uids
def pathToUid(list):
  pass

def pathToValue(list):
  pass


def uidToPath(list):
  pass

def uidToValue(list):
  pass


def referenceToPath(list):
  pass

# Path
def getPath(object_or_path, **kw):
  """Returns the absolute path of an object
  """
  if isinstance(object_or_path, (list, tuple)):
    path = '/'.join(object_or_path)
  elif isinstance(object_or_path, str):
    path = object_or_path
  else:
    path = object_or_path.getPhysicalPath()
    path = '/'.join(path)
  if kw.get('tuple'):
    return path.split('/')
  return path

def int2letter(i):
  """
  Convert an integer to letters, to generate spreadsheet column id
  0=>A, 25=>Z, 26=>AA, 27=>AB, ...
  """
  if i < 26:
    return (chr(i + ord('A')))
  d, m = divmod(i, 26)
  return int2letter(d - 1) + int2letter(m)

#Get message id for translation
def getMessageIdWithContext(msg_id, context, context_id):
  return '%s [%s in %s]' % (msg_id, context, context_id)

#Get translation of msg id
def getTranslationStringWithContext(self, msg_id, context, context_id):
   portal = self.getPortalObject()
   localizer = portal.Localizer
   selected_language = localizer.get_selected_language()
   msg_id_context = getMessageIdWithContext(msg_id, context, context_id)
   result = localizer.erp5_ui.gettext(msg_id_context, default='')
   if result == '':
     result = localizer.erp5_ui.gettext(msg_id)
   return result.encode('utf8')

from rfc822 import AddressList

def Email_parseAddressHeader(text):
  """
  Given a text taken from a From/To/CC/... email header,
  return a list of tuples (name, address) extracted from
  this header
  """
  return AddressList(text).addresslist

def fill_args_from_request(*optional_args):
  """Method decorator to fill missing args from given request

  Without this decorator, code would have to rely on ZPublisher to get
  paramaters from the REQUEST, which leads to much code duplication (copy and
  paster of possible paramaters with their default values).

  This decorator optional takes an list of names for parameters that are not
  required by the method.
  """
  def decorator(wrapped):
    names = inspect.getargspec(wrapped)[0]
    assert names[:2] == ['self', 'REQUEST']
    del names[:2]
    names += optional_args
    def wrapper(self, REQUEST=None, *args, **kw):
      if REQUEST is not None:
        for k in names[len(args):]:
          if k not in kw:
            v = REQUEST.get(k, kw)
            if v is not kw:
              kw[k] = v
      return wrapped(self, REQUEST, *args, **kw)
    wrapper.__name__ = wrapped.__name__
    wrapper.__doc__ = wrapped.__doc__
    return wrapper
  if len(optional_args) == 1 and not isinstance(optional_args[0], basestring):
    function, = optional_args
    optional_args = ()
    return decorator(function)
  return decorator

#####################################################
# Globals initialization
#####################################################

from InitGenerator import InitializeDocument, InitializeInteractor, registerInteractorClass

# List Regexp
python_file_expr = re.compile("py$")

def getModuleIdList(product_path, module_id):
  global python_file_expr
  path = os.path.join(product_path, module_id)
  module_name_list = []
  module_lines = []
  try:
    file_list = os.listdir(path)
    for file_name in file_list:
      if file_name != '__init__.py':
        if python_file_expr.search(file_name,1):
          module_name = file_name[0:-3]
          module_name_list += [module_name]
  except:
    LOG('ERP5Type', BLATHER,
        'No %s directory in %s' % (module_id, product_path))
  return path, module_name_list

# EPR5Type global modules update
def updateGlobals(this_module, global_hook,
                  permissions_module=None, is_erp5_type=0):
  """
    This function does all the initialization steps required
    for a Zope / CMF Product
  """
  product_path = package_home( global_hook )

  if not is_erp5_type:
    # Add _dtmldir
    this_module._dtmldir = os.path.join( product_path, 'dtml' )

    module_list = (
        ('PropertySheet', importLocalPropertySheet),
        ('interfaces', importLocalInterface),
        ('Constraint', importLocalConstraint),
    )
    # Update PropertySheet Registry
    for module_id, import_method in module_list:
      path, module_id_list = getModuleIdList(product_path, module_id)
      for module_id in module_id_list:
        import_method(module_id, path=path)

    # Update Permissions
    if permissions_module is not None:
      for key in dir(permissions_module):
        # Do not consider private keys
        if key[0:2] != '__':
          setattr(Permissions, key, getattr(permissions_module, key))
  else:
    # We have to parse interface list in order to generate some accessors
    # even if we are on the ERP5Type product
    path, module_id_list = getModuleIdList(product_path, 'interfaces')
    import_method = importLocalInterface
    for module_id in module_id_list:
      import_method(module_id, path=path, is_erp5_type=is_erp5_type)

  module_name = this_module.__name__
  # Return core document_class list (for ERP5Type only)
  # this was introduced to permit overriding ERP5Type Document classes
  # which was not possible when they were define in the Document folder
  path, core_module_id_list = getModuleIdList(product_path, 'Core')
  for document in core_module_id_list:
    module_path = '.'.join((module_name, 'Core', document, document))
    InitializeDocument(document, module_path)
  # Return document_class list
  path, module_id_list = getModuleIdList(product_path, 'Document')
  for document in module_id_list:
    module_path = '.'.join((module_name, 'Document', document, document))
    InitializeDocument(document, module_path)

  # Return interactor_class list
  path, interactor_id_list = getModuleIdList(product_path, 'Interactor')
  for interactor in interactor_id_list:
    InitializeInteractor(interactor, interactor_path=path)

  return module_id_list + core_module_id_list

#####################################################
# Modules Import
#####################################################

import imp

from App.config import getConfiguration

from Products.ERP5Type.Globals import InitializeClass
from Accessor.Base import func_code
from Products.CMFCore.utils import manage_addContentForm, manage_addContent
from AccessControl.PermissionRole import PermissionRole

python_file_parser = re.compile('^(.*)\.py$')

def getLocalPropertySheetList():
  if not getConfiguration:
    return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()
  return result

def removeLocalPropertySheet(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  for ext in ('py', 'pyc', 'pyo'):
    f = os.path.join(path, "%s.%s" % (class_id, ext))
    if os.path.exists(f):
      os.remove(f)

def readLocalPropertySheet(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    text = f.read()
  finally:
    f.close()
  return text

def writeLocalPropertySheet(class_id, text, create=1, instance_home=None):
  if instance_home is None:
    instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  if not os.path.exists(path):
    os.mkdir(path)
    LOG('ERP5Type', WARNING, 'Created missing but required directory: %s' %path)
  path = os.path.join(path, "%s.py" % class_id)
  if create:
    if os.path.exists(path):
      raise IOError, 'the file %s is already present' % path
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()
  # load the file, so that an error is raised if file is invalid
  module = imp.load_source(class_id, path)
  getattr(module, class_id)

def importLocalPropertySheet(class_id, path = None):
  from Products.ERP5Type import PropertySheet
  if path is None:
    # We should save a copy in ZODB here XXX
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "PropertySheet")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    module = imp.load_source(class_id, path, f)
    klass = None
    try:
      klass = getattr(module, class_id)
    except AttributeError:
      raise AttributeError("Property Sheet '%s' should contain a class " \
          "with the same name" % class_id)
    setattr(PropertySheet, class_id, klass)
    # Register base categories
    registerBaseCategories(klass)
  finally:
    f.close()

base_category_dict = {}
def registerBaseCategories(property_sheet):
  global base_category_dict
  category_list = getattr(property_sheet, '_categories', ())
  if isinstance(category_list, str):
    category_list = (category_list,)
  for bc in category_list :
    base_category_dict[bc] = 1

def importLocalInterface(module_id, path = None, is_erp5_type=False):
  def provides(class_id):
    # Create interface getter
    accessor_name = 'provides' + class_id
    setattr(BaseClass, accessor_name, lambda self: self.provides(class_id))
    BaseClass.security.declarePublic(accessor_name)
  class_id = "I" + convertToUpperCase(module_id)
  if is_erp5_type:
    provides(class_id)
  else:
    if path is None:
      instance_home = getConfiguration().instancehome
      path = os.path.join(instance_home, "interfaces")
    path = os.path.join(path, "%s.py" % module_id)
    f = open(path)
    try:
      module = imp.load_source(class_id, path, f)
    finally:
      f.close()
    from zope.interface import Interface
    from Products.ERP5Type import interfaces
    InterfaceClass = type(Interface)
    for k, v in module.__dict__.iteritems():
      if type(v) is InterfaceClass and v is not Interface:
        setattr(interfaces, k, v)
        provides(class_id)

def importLocalConstraint(class_id, path = None):
  import Products.ERP5Type.Constraint
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Constraint")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    module = imp.load_source(class_id, path, f)
    setattr(Products.ERP5Type.Constraint, class_id, getattr(module, class_id))
  finally:
    f.close()

def importLocalInteractor(class_id, path=None):
  import Products.ERP5Type.Interactor
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Interactor")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    module = imp.load_source(class_id, path, f)
    setattr(Products.ERP5Type.Interactor, class_id, getattr(module, class_id))
    registerInteractorClass(class_id, getattr(Products.ERP5Type.Interactor, class_id))
  finally:
    f.close()

def getLocalExtensionList():
  if not getConfiguration:
    return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()
  return result

def getLocalTestList():
  if not getConfiguration:
    return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "tests")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()
  return result

def getLocalConstraintList():
  if not getConfiguration:
    return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Constraint")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()
  return result

def removeLocalExtension(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  for ext in ('py', 'pyc', 'pyo'):
    f = os.path.join(path, "%s.%s" % (class_id, ext))
    if os.path.exists(f):
      os.remove(f)

def readLocalExtension(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    text = f.read()
  finally:
    f.close()
  return text

def removeLocalTest(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "tests")
  for ext in ('py', 'pyc', 'pyo'):
    f = os.path.join(path, "%s.%s" % (class_id, ext))
    if os.path.exists(f):
      os.remove(f)

def readLocalTest(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "tests")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    text = f.read()
  finally:
    f.close()
  return text

def readLocalConstraint(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Constraint")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    text = f.read()
  finally:
    f.close()
  return text

def writeLocalExtension(class_id, text, create=1, instance_home=None):
  if instance_home is None:
    instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  if not os.path.exists(path):
    os.mkdir(path)
    LOG('ERP5Type', WARNING, 'Created missing but required directory: %s' %path)
  path = os.path.join(path, "%s.py" % class_id)
  if create:
    if os.path.exists(path):
      raise IOError, 'the file %s is already present' % path
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()

def writeLocalTest(class_id, text, create=1, instance_home=None):
  if instance_home is None:
    instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "tests")
  if not os.path.exists(path):
    os.mkdir(path)
    LOG('ERP5Type', WARNING, 'Created missing but required directory: %s' %path)
  path = os.path.join(path, "%s.py" % class_id)
  if create:
    if os.path.exists(path):
      raise IOError, 'the file %s is already present' % path
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()

def writeLocalConstraint(class_id, text, create=1, instance_home=None):
  if instance_home is None:
    instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Constraint")
  if not os.path.exists(path):
    os.mkdir(path)
    LOG('ERP5Type', WARNING, 'Created missing but required directory: %s' %path)
  path = os.path.join(path, "%s.py" % class_id)
  if create:
    if os.path.exists(path):
      raise IOError, 'the file %s is already present' % path
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()
  # load the file, so that an error is raised if file is invalid
  module = imp.load_source(class_id, path)
  getattr(module, class_id)

def removeLocalConstraint(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Constraint")
  for ext in ('py', 'pyc', 'pyo'):
    f = os.path.join(path, "%s.%s" % (class_id, ext))
    if os.path.exists(f):
      os.remove(f)

def getLocalDocumentList():
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()
  return result

def removeLocalDocument(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  for ext in ('py', 'pyc', 'pyo'):
    f = os.path.join(path, "%s.%s" % (class_id, ext))
    if os.path.exists(f):
      os.remove(f)
  if document_class_registry.pop(class_id, None):
    # restore original class (from product) if any
    from Products.ERP5Type.InitGenerator import product_document_registry
    product_path = product_document_registry.get(class_id)
    if product_path:
      importLocalDocument(class_id, class_path=product_path)
    else:
      pass # XXX Do we need to clean up ?

def readLocalDocument(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    text = f.read()
  finally:
    f.close()
  return text

def writeLocalDocument(class_id, text, create=1, instance_home=None):
  if instance_home is None:
    instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  if not os.path.exists(path):
    os.mkdir(path)
    LOG('ERP5Type', WARNING, 'Created missing but required directory: %s' %path)
  path = os.path.join(path, "%s.py" % class_id)
  if create:
    if os.path.exists(path):
      raise IOError, 'the file %s is already present' % path
  # check there is no syntax error (that's the most we can do at this time)
  compile(text, path, 'exec')
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()

def setDefaultClassProperties(property_holder):
  """Initialize default properties for ERP5Type Documents.
  """
  pdict = property_holder.__dict__
  if not 'isPortalContent' in pdict:
    property_holder.isPortalContent = PropertyConstantGetter('isPortalContent',
                                                     value=True)
  if not 'isRADContent' in pdict:
    property_holder.isRADContent = 1
  if not 'add_permission' in pdict:
    property_holder.add_permission = Permissions.AddPortalContent
  if not '__implements__' in pdict:
    property_holder.__implements__ = ()
  if not 'property_sheets' in pdict:
    property_holder.property_sheets = ()
  # Add default factory type information
  if not 'factory_type_information' in pdict and \
         'meta_type' in pdict and 'portal_type' in pdict:
    name = property_holder.__name__
    property_holder.factory_type_information = \
      {    'id'             : property_holder.portal_type
         , 'meta_type'      : property_holder.meta_type
         , 'description'    : getattr(property_holder, '__doc__',
                                "Type generated by ERPType")
         , 'icon'           : 'document_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'add%s' % name
         , 'immediate_view' : '%s_view' % name
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : '%s_view' % name
          , 'permissions'   : ( Permissions.View, )
          },
        )
      }

class PersistentMigrationMixin(object):
  """
  All classes issued from ERP5Type.Document.XXX submodules
  will gain with mixin as a base class.

  It allows us to migrate ERP5Type.Document.XXX.YYY classes to
  erp5.portal_type.ZZZ namespace

  Note that migration can be disabled by setting the '_no_migration'
  class attribute to a nonzero value, as all old objects in the system
  should inherit from this mixin
  """
  _no_migration = 0

  def __setstate__(self, value):
    klass = self.__class__
    if PersistentMigrationMixin._no_migration \
        or klass.__module__ in ('erp5.portal_type', 'erp5.temp_portal_type'):
      super(PersistentMigrationMixin, self).__setstate__(value)
      return

    portal_type = value.get('portal_type')
    if portal_type is None:
      portal_type = getattr(klass, 'portal_type', None)
    if portal_type is None:
      LOG('ERP5Type', PROBLEM,
          "no portal type was found for %s (class %s)" \
               % (self, klass))
      super(PersistentMigrationMixin, self).__setstate__(value)
    else:
      # proceed with migration
      import erp5.portal_type
      newklass = getattr(erp5.portal_type, portal_type)
      assert self.__class__ != newklass
      self.__class__ = newklass
      self.__setstate__(value)
      LOG('ERP5Type', TRACE, "Migration for object %s" % self)

from Globals import Persistent, PersistentMapping

def importLocalDocument(class_id, path=None, class_path=None):
  """Imports a document class and registers it in ERP5Type Document
  repository ( Products.ERP5Type.Document )
  """
  import Products.ERP5Type.Document
  import Permissions

  if class_path:
    assert path is None
    module_path = class_path.rsplit('.', 1)[0]
    module = __import__(module_path, {}, {}, (module_path,))
  else:
    # local document in INSTANCE_HOME/Document/
    # (created by ClassTool?)
    if path is None:
      instance_home = getConfiguration().instancehome
      path = os.path.join(instance_home, "Document")
    path = os.path.join(path, "%s.py" % class_id)
    module_path = "erp5.document"
    class_path = "%s.%s" % (module_path, class_id)
    module = imp.load_source(class_path, path)
    klass = getattr(module, class_id, None)
    # Tolerate that Document doesn't define any class, which can be useful
    # if we only want to monkey patch.
    # XXX A new 'Patch' folder should be introduced instead. Each module would
    #     define 2 methods: 'patch' and 'unpatch' (for proper upgrading).
    if klass is None:
      assert hasattr(module, 'patch')
      return
    import erp5.document
    setattr(erp5.document, class_id, klass)
  document_class_registry[class_id] = class_path

  ### Migration
  module_name = "Products.ERP5Type.Document.%s" % class_id

  # Most of Document modules define a single class
  # (ERP5Type.Document.Person.Person)
  # but some (eek) need to act as module to find other documents,
  # e.g. ERP5Type.Document.BusinessTemplate.SkinTemplateItem
  #
  def migrate_me_document_loader(document_name):
    klass = getattr(module, document_name)
    if issubclass(klass, (Persistent, PersistentMapping)):
      setDefaultClassProperties(klass)
      InitializeClass(klass)

      class MigrateMe(PersistentMigrationMixin, klass):
        pass
      MigrateMe.__name__ = document_name
      MigrateMe.__module__ = module_name
      return MigrateMe
    else:
      return klass
  from dynamic.dynamic_module import registerDynamicModule
  document_module = registerDynamicModule(module_name,
                                          migrate_me_document_loader)

  setattr(Products.ERP5Type.Document, class_id, document_module)

  ### newTempFoo
  from Products.ERP5Type.ERP5Type import ERP5TypeInformation
  klass = getattr(module, class_id)
  temp_type = ERP5TypeInformation(klass.portal_type)
  temp_document_constructor = temp_type.constructTempInstance

  temp_document_constructor_name = "newTemp%s" % class_id
  setattr(Products.ERP5Type.Document,
          temp_document_constructor_name,
          temp_document_constructor)
  ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic(
                      temp_document_constructor_name,) # XXX Probably bad security

  # XXX really?
  return klass, tuple()

def initializeLocalRegistry(directory_name, import_local_method):
  """
  Initialize local directory.
  """
  if not getConfiguration: return
  instance_home = getConfiguration().instancehome
  document_path = os.path.join(instance_home, directory_name)
  python_file_expr = re.compile("py$")
  # For unit testing.
  if os.access(document_path, os.F_OK):
    file_list = os.listdir(document_path)
  else:
    file_list = ()
  for file_name in file_list:
    if file_name != '__init__.py':
      if python_file_expr.search(file_name,1):
        module_name = file_name[0:-3]
        try:
          import_local_method(module_name, path=document_path)
          LOG('ERP5Type', BLATHER,
              'Added local %s to ERP5Type repository: %s (%s)'
              % (directory_name, module_name, document_path))
        except Exception, e:
          if DevelopmentMode:
            raise
          LOG('E5RP5Type', PROBLEM,
              'Failed to add local %s to ERP5Type repository: %s (%s)'
              % (directory_name, module_name, document_path), error=e)

def initializeLocalDocumentRegistry():
  # XXX Arg are not consistent
  initializeLocalRegistry("Document", importLocalDocument)

def initializeLocalPropertySheetRegistry():
  initializeLocalRegistry("PropertySheet", importLocalPropertySheet)

def initializeLocalConstraintRegistry():
  initializeLocalRegistry("Constraint", importLocalConstraint)

def initializeLocalInteractorRegistry():
  initializeLocalRegistry("Interactor", importLocalInteractor)


#####################################################
# Product initialization
#####################################################

def registerDocumentClass(module_name, class_name):
  """
  register a class in document_class_registry without overwriting
  existing records
  """
  old_value = document_class_registry.get(class_name)
  new_value = "%s.%s" % (module_name, class_name)

  if old_value is not None:
    old_was_erp5 = old_value.startswith('Products.ERP5')
    new_is_erp5 = module_name.startswith('Products.ERP5')

    conflict = True
    if not old_was_erp5:
      if new_is_erp5:
        # overwrite the non-erp5 class with the erp5 class
        # likely to happen with e.g. CMF Category Tool and ERP5 Category Tool
        LOG('Utils', INFO, 'Replacing non-ERP5 class %s by ERP5 class %s' %
              (old_value, new_value))
        conflict = False
    elif not new_is_erp5:
      # argh, trying to overwrite an existing erp5 class.
      LOG('Utils', INFO,
          'Ignoring replacement of ERP5 class %s by non-ERP5 class %s' %
            (old_value, new_value))
      return

    if conflict:
      raise TypeError("Class %s and %s from different products have the "
                      "same name" % (old_value, new_value))

  document_class_registry[class_name] = new_value

def initializeProduct( context,
                       this_module,
                       global_hook,
                       document_module=None,
                       document_classes=(), # XXX - Never used - must be likely removed
                       object_classes=(),
                       portal_tools=(),
                       content_constructors=(),
                       content_classes=()):
  """
    This function does all the initialization steps required
    for a Zope / CMF Product
  """
  module_name = this_module.__name__

  # Content classes are exceptions and should be registered here.
  # other products were all already registered in updateGlobals()
  # because getModuleIdList works fine for Document/ and Core/
  for klass in content_classes:
    registerDocumentClass(klass.__module__, klass.__name__)

  mixin_module = getattr(this_module, 'mixin', None)
  if mixin_module is not None:
    from Products.ERP5Type import mixin_class_registry
    for k, submodule in inspect.getmembers(mixin_module, inspect.ismodule):
      for klassname, klass in inspect.getmembers(submodule, inspect.isclass):
        # only classes defined here
        if 'mixin' in klass.__module__ and not issubclass(klass, Exception):
          classpath = '.'.join((module_name, 'mixin', k, klassname))
          mixin_class_registry[klassname] = classpath

  product_name = module_name.split('.')[-1]

  # Define FactoryTypeInformations for all content classes
  contentFactoryTypeInformations = []
  for content in content_classes:
    if hasattr(content, 'factory_type_information'):
      contentFactoryTypeInformations.append(content.factory_type_information)


  # Try to make some standard directories available
  try:
    registerDirectory('skins', global_hook)
  except:
    LOG("ERP5Type", BLATHER, "No skins directory for %s" % product_name)
  try:
    registerDirectory('help', global_hook)
  except:
    LOG("ERP5Type", BLATHER, "No help directory for %s" % product_name)

  # create dynamic modules if they dont exist, this only ever happens
  # once.
  try:
    import erp5.portal_type
  except ImportError:
    from dynamic.portal_type_class import initializeDynamicModules
    initializeDynamicModules()
    import erp5.portal_type

  # Tools initialization
  tools = portal_tools
  if len(tools) > 0:
    for tool in tools:
      registerDocumentClass(tool.__module__, tool.__name__)
    try:
      utils.ToolInit('%s Tool' % product_name,
                      tools=tools,
                      icon='tool.png',
                      ).initialize( context )
    except TypeError:
      # product_name parameter is deprecated in CMF
      utils.ToolInit('%s Tool' % product_name,
                      tools=tools,
                      product_name=product_name,
                      icon='tool.png',
                      ).initialize( context )

  for klass in content_classes:
    # This id the default add permission to all ojects
    klass_permission='Add portal content'
    # We are looking if a permission type is defined in the document
    if hasattr(klass, 'permission_type'):
      klass_permission=klass.permission_type

    #LOG("ContentInit", 0, str(content_constructors))
    utils.ContentInit(klass.meta_type,
                      content_types=[klass],
                      permission=klass_permission,
                      extra_constructors=tuple(content_constructors),
                      fti=contentFactoryTypeInformations,
                     ).initialize( context )

  # Register Help and API Reference
  # This trick to make registerHelp work with 2 directories is taken from
  # CMFCore
  help = context.getProductHelp()
  lastRegistered = help.lastRegistered
  context.registerHelp(directory='help', clear=1)
  context.registerHelp(directory='interfaces', clear=1)
  if help.lastRegistered != lastRegistered:
    help.lastRegistered = None
    context.registerHelp(directory='help', clear=1)
    help.lastRegistered = None
    context.registerHelp(directory='interfaces', clear=0)

  context.registerHelpTitle('%s Help' % product_name)

  # Register Objets
  for c in object_classes:
    registerDocumentClass(c.__module__, c.__name__)
    icon = getattr(c, 'icon', None)
    permission = getattr(c, 'permission_type', None)
    context.registerClass(c,
                          constructors = c.constructors,
                          permission = permission,
                          icon = icon)

class ConstraintNotFound(Exception):
  pass

def createConstraintList(property_holder, constraint_definition):
  """
    This function creates constraint instances for a class
    and a property

    constraint_definition -- the constraint with all attributes
  """
  from Products.ERP5Type import Constraint
  try:
    consistency_class = getattr(Constraint, constraint_definition['type'])
  except AttributeError:
    LOG("ERP5Type", PROBLEM, "Can not find Constraint: %s" \
        % constraint_definition['type'], error=sys.exc_info())
    raise ConstraintNotFound(repr(constraint_definition))
  consistency_instance = consistency_class(**constraint_definition)
  property_holder.constraints += [consistency_instance]

#####################################################
# Constructor initialization
#####################################################

def createExpressionContext(object, portal=None):
  """
    Return a context used for evaluating a TALES expression.
  """
  tv = getTransactionalVariable()
  cache_key = ('createExpressionContext', id(object))
  try:
    return tv[cache_key]
  except KeyError:
    pass
  if portal is None and object is not None:
    portal = object.getPortalObject()

  if object is None or getattr(object, 'aq_base', None) is None:
    folder = portal
  else:
    folder = object
    # Search up the containment hierarchy until we find an
    # object that claims it's a folder.
    while folder is not None:
      if getattr(aq_base(folder), 'isPrincipiaFolderish', 0):
        # found it.
        break
      else:
        folder = aq_parent(aq_inner(folder))

  if portal is not None:
    pm = getattr(portal, 'portal_membership', None)
    if pm is None or pm.isAnonymousUser():
      member = None
    else:
      member = pm.getAuthenticatedMember()
  else:
    member = None

  if object is None:
    object_url = ''
  else:
    object_url = object.absolute_url()

  if folder is None:
    folder_url = ''
  else:
    folder_url = folder.absolute_url()

  if portal is None:
    portal_url = ''
  else:
    portal_url = portal.absolute_url()

  data = {
      'object_url':   object_url,
      'folder_url':   folder_url,
      'portal_url':   portal_url,
      'object':       object,
      'folder':       folder,
      'portal':       portal,
      'nothing':      None,
      'request':      getattr( object, 'REQUEST', None ),
      'modules':      SecureModuleImporter,
      'member':       member,
      'here':         object,
      # XXX 'here' is deprecated throughout the Zope code base. 'context' is
      # the proper name these days
      'context':         object,
      }
  ec = getEngine().getContext(data)
  tv[cache_key] = ec
  return ec

def getExistingBaseCategoryList(portal, base_cat_list):
  cache = getReadOnlyTransactionCache()
  if cache is None:
    cache = getTransactionalVariable()
  category_tool = getattr(portal, 'portal_categories', None)
  if category_tool is None:
    # most likely, accessor generation when bootstrapping a site
    if not getattr(portal, '_v_bootstrapping', False):
      warnings.warn("Category Tool is missing. Accessors can not be generated.")
    return ()

  new_base_cat_list = []
  for base_cat in base_cat_list:
    if base_cat is None:
      # a Dynamic Category Property specifies a TALES Expression which
      # may return a list containing None, so just skip it
      continue

    key = (base_cat,)
    try:
      value = cache[key]
    except KeyError:
      value = category_tool._getOb(base_cat, None)
      if value is None:
        warnings.warn("Base Category %r is missing."
                      " Accessors can not be generated." % base_cat, Warning)
      cache[key] = value
    if value is not None:
      new_base_cat_list.append(base_cat)
  return tuple(new_base_cat_list)

def createRelatedAccessors(portal_categories, property_holder, econtext,
                           base_category_list=None):
  if base_category_list is None:
    base_category_list = []
    # first extend the Tales category definitions into base_category_list
    for cat in base_category_dict:
      if isinstance(cat, Expression):
        result = cat(econtext)
        if isinstance(result, (list, tuple)):
          base_category_list.extend(result)
        else:
          base_category_list.append(result)
      else:
        base_category_list.append(cat)

  for cat in base_category_list:
    # Get read and write permission
    cat_object = portal_categories.get(cat, None)
    if cat_object is not None:
      read_permission = Permissions.__dict__.get(
                              cat_object.getReadPermission(),
                              Permissions.AccessContentsInformation)
      if isinstance(read_permission, Expression):
        read_permission = read_permission(econtext)
    else:
      read_permission = Permissions.AccessContentsInformation
    # Actually create accessors
    createRelatedValueAccessors(property_holder, cat, read_permission=read_permission)
  # Unnecessary to create these accessors more than once.
  base_category_dict.clear()


def createAllCategoryAccessors(portal, property_holder, cat_list, econtext):
  if portal is not None:
    portal_categories = getattr(portal, 'portal_categories', None)
  else:
    portal_categories = None
  for cat in cat_list:
    # Create free text accessors.
    prop = {
      'id'         : '%s_free_text' % cat,
      'description': 'free text to specify %s' % cat,
      'type'       : 'text',
      'default'    : '',
      'mode'       : 'w'
    }
    # XXX These are only for backward compatibility.
    if cat == 'group':
      prop['storage_id'] = 'group'
    elif cat == 'site':
      prop['storage_id'] = 'location'
    createDefaultAccessors(
                      property_holder,
                      prop['id'],
                      prop=prop,
                      read_permission=Permissions.AccessContentsInformation,
                      write_permission=Permissions.ModifyPortalContent,
                      portal=portal)

    # Get read and write permission
    if portal_categories is not None:
      cat_object = portal_categories.get(cat, None)
    else:
      cat_object = None
    if cat_object is not None:
      read_permission = Permissions.__dict__.get(
                              cat_object.getReadPermission(),
                              Permissions.AccessContentsInformation)
      if isinstance(read_permission, Expression):
        read_permission = read_permission(econtext)
      write_permission = Permissions.__dict__.get(
                              cat_object.getWritePermission(),
                              Permissions.ModifyPortalContent)
      if isinstance(write_permission, Expression):
        write_permission = write_permission(econtext)
    else:
      read_permission = Permissions.AccessContentsInformation
      write_permission = Permissions.ModifyPortalContent
    # Actualy create accessors
    createCategoryAccessors(property_holder, cat,
      read_permission=read_permission, write_permission=write_permission)
    createValueAccessors(property_holder, cat,
      read_permission=read_permission, write_permission=write_permission)

default_translation_property_dict = {
  'id' : 'translation_domain',
  'description' : '',
  'default' : '',
  'type' : 'string',
  'mode' : 'w',
}
def setDefaultProperties(property_holder, object=None, portal=None):
    """
      This methods sets default accessors for this object as well
      as consistency checkers, based on the definition
      stored in PropertySheet objects.

      Accessors include

      - attribute accessors (ie. a string, float value stored by the object)

      - category accessors (ie. a membership of an object to a category)

      - relation accessors (ie. a kind of membership where the category
                            instance is content)

      - programmable acquisition acessors (ie. attribute accessors which
                                           are based on relations)

      Consistency checkers are intended to check the content consistency
      (ex. ariry of a relation) as well as fix content consistency
      through a default consistency fixing method.

    Set default attributes in current object for all properties in '_properties'
    """
    econtext = createExpressionContext(object, portal)
    # First build the property list from the property sheet
    # and the class properties
    prop_list = []
    # Do not consider superclass _properties definition
    for prop in property_holder.__dict__.get('_properties', []):
      # Copy the dict so that Expression objects are not overwritten.
      prop_list.append(prop.copy())
    # Do not consider superclass _categories definition
    cat_list = property_holder.__dict__.get('_categories', [])
    # a list of declarative consistency definitions (ie. constraints)
    # Do not consider superclass _constraints definition
    constraint_list = property_holder.__dict__.get('_constraints', [])

    # Evaluate TALES expressions.
    for prop in prop_list:
      for key,value in prop.items():
        if isinstance(value, Expression):
          prop[key] = value(econtext)
    new_cat_list = []
    for cat in cat_list:
      if isinstance(cat, Expression):
        result = cat(econtext)
        if isinstance(result, (tuple, list)):
          new_cat_list.extend(result)
        else:
          new_cat_list.append(result)
      else:
        new_cat_list.append(cat)
    cat_list = getExistingBaseCategoryList(portal, new_cat_list)

    from Products.ERP5Type.mixin.constraint import ConstraintMixin
    for const in constraint_list:
      if isinstance(const, ConstraintMixin):
        continue
      for key, value in const.items():
        if isinstance(value, Expression):
          const[key] = value(econtext)

    # Store ERP5 properties on specific attributes
    property_holder._erp5_properties = tuple(prop_list)

    # Create default accessors for property sheets
    converted_prop_list = []
    converted_prop_set = set()
    for prop in prop_list:
      if prop['type'] not in type_definition:
        LOG("ERP5Type.Utils", INFO,
            "Invalid type '%s' of property '%s' for Property Sheet '%s'" % \
            (prop['type'], prop['id'], property_holder.__name__))
        continue

      read_permission = prop.get('read_permission',
                                 Permissions.AccessContentsInformation)
      if isinstance(read_permission, Expression):
        read_permission = read_permission(econtext)
      write_permission = prop.get('write_permission',
                                  Permissions.ModifyPortalContent)
      if isinstance(write_permission, Expression):
        write_permission = write_permission(econtext)

      if 'base_id' in prop:
        continue
      if prop['id'] not in converted_prop_set:
        if prop['type'] != 'content':
          converted_prop_list.append(prop)
        converted_prop_set.add(prop['id'])

      # Create range accessors, if this has a range.
      if prop.get('range', 0):
        for value in ('min', 'max'):
          range_prop = prop.copy()
          del range_prop['range']
          range_prop.pop('storage_id', None)
          if range_prop.get('acquisition_accessor_id', 0):
            range_prop['acquisition_accessor_id'] = '%sRange%s' % (
                 range_prop['acquisition_accessor_id'], value.capitalize())
          range_prop['alt_accessor_id'] = (
                                'get' + convertToUpperCase(prop['id']),)
          createDefaultAccessors(
                      property_holder,
                      '%s_range_%s' % (prop['id'], value),
                      prop=range_prop,
                      read_permission=read_permission,
                      write_permission=write_permission,
                      portal=portal)

      # Create translation accesor, if translatable is set
      if prop.get('translatable', 0):
        # make accessors like getTranslatedProperty
        createTranslationAccessors(
                  property_holder,
                  'translated_%s' % (prop['id']),
                  prop,
                  read_permission=read_permission,
                  write_permission=write_permission)
        createTranslationLanguageAccessors(
                  property_holder,
                  prop,
                  read_permission=read_permission,
                  write_permission=write_permission,
                  portal=portal)
        # make accessor to translation_domain
        # first create default one as a normal property
        accessor_id = '%s_translation_domain' % prop['id']
        createDefaultAccessors(
                  property_holder,
                  accessor_id,
                  prop=default_translation_property_dict,
                  read_permission=read_permission,
                  write_permission=write_permission,
                  portal=portal)
        # then overload accesors getPropertyTranslationDomain
        default = prop.get('translation_domain', '')
        createTranslationAccessors(
                        property_holder,
                        accessor_id,
                        prop,
                        read_permission=read_permission,
                        write_permission=write_permission,
                        default=default)
      createDefaultAccessors(
                      property_holder,
                      prop['id'],
                      prop=prop,
                      read_permission=read_permission,
                      write_permission=write_permission,
                      portal=portal)
    # Create Category Accessors
    createAllCategoryAccessors(portal, property_holder, cat_list, econtext)

    property_holder.constraints = []
    for constraint in constraint_list:
      # ZODB Property Sheets constraints are no longer defined by a
      # dictionary but by a ConstraintMixin, thus just append it to
      # the list of constraints
      if isinstance(constraint, ConstraintMixin):
        property_holder.constraints.append(constraint)
      else:
        createConstraintList(property_holder, constraint_definition=constraint)

    # ERP5 _properties and Zope _properties are somehow different
    # The id is converted to the Zope standard - we keep the original id
    # as base_id
    new_converted_prop_list = []
    for prop in converted_prop_list:
      new_prop = prop.copy()
      if prop['type'] in list_types or prop.get('multivalued', 0):
        # Display as list
        if not prop.get('base_id', None):
          new_prop['base_id'] = prop['id']
          new_prop['id'] = prop['id'] + '_list'
      if prop.get('acquisition_base_category') is not None \
              and not prop.get('acquisition_copy_value'):
        # Set acquisition values as read only if no value is copied
        new_prop['mode'] = 'r'
      new_converted_prop_list.append(new_prop)
    # Set the properties of the class
    property_holder._properties = tuple(new_converted_prop_list)
    property_holder._categories = tuple(cat_list)
    property_holder._constraints = tuple(constraint_list)
    # And the default values - default values are needed
    # for historical reasons : many objects have a default
    # value defines at the class level. The use of None
    # allows to create the equivalent of NULL values
    # - new - XXX
    # We remove such properties here
    #from Base import Base as BaseClass
    for prop in converted_prop_list:
      if prop['type'] not in type_definition:
        raise TypeError, '"%s" is invalid type for propertysheet' % \
                                        prop['type']
      #if not hasattr(property_holder, prop['id']):
        # setattr(property_holder, prop['id'], None) # This makes sure no acquisition will happen
        # but is wrong when we use storage_id .....
      #storage_id = prop.get('storage_id', prop['id'])
      #if not hasattr(BaseClass, storage_id):
        # setattr(property_holder, storage_id, None) # This breaks things with aq_dynamic
        #setattr(BaseClass, storage_id, None) # This blocks acquisition
      #else:
        #LOG('existing property',0,str(storage_id))
        #if prop.get('default') is not None:
        #  # setattr(property_holder, prop['id'], prop.get('default'))
        #  pass
        #else:
        #  # setattr(property_holder, prop['id'], defaults[prop['type']])
        #  pass

#####################################################
# Accessor initialization
#####################################################

from Base import Base as BaseClass
from Accessor import Base, List, Acquired, Content,\
                     AcquiredProperty, ContentProperty, \
                     Alias

def createDefaultAccessors(property_holder, id, prop = None,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent,
    portal=None):
  """
    This function creates accessor and setter for a class
    and a property

    property_holder -- the class to add an accessor to

    id    -- the id of the property

    prop  -- the property definition of the property
  """
  override = prop.get('override',0)
  ######################################################
  # Create Translation Acquired Accessors.
  if prop.get('translation_acquired_property_id'):
    createTranslationAcquiredPropertyAccessors(property_holder, prop,
                                               portal=portal)

  ######################################################
  # Create Portal Category Type Accessors.
  if prop['type'] == 'group_type':
    createGroupTypeAccessors(property_holder, prop,
                             read_permission=read_permission,
                             portal=portal)

  ######################################################
  # Create Getters
  elif prop.get('acquisition_base_category') is not None:
    # Create getters for an acquired property
    # XXXX Missing Boolean accessor
    accessor_args = (
                prop['type'],
                prop.get('default'),
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('storage_id'),
                prop.get('alt_accessor_id'),
                prop.get('acquisition_object_id'),
                (prop['type'] in list_types or prop.get('multivalued', 0)),
                (prop['type'] == 'tales')
                )
    # Base Getter
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
    # Default Getter
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
    # List Getter
    if prop['type'] in list_types or prop.get('multivalued', 0):
      accessor_name = 'get' + UpperCase(id) + 'List'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'List'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter, accessor_args)
      # Set Getter
      accessor_name = 'get' + UpperCase(id) + 'Set'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.SetGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Set'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.SetGetter, accessor_args)
    if prop['type'] == 'content':
      #LOG('Value Object Accessor', 0, prop['id'])
      # Base Getter
      accessor_name = 'get' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
      # Default Getter
      accessor_name = 'getDefault' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.DefaultGetter, accessor_args)
      # List Getter
      accessor_name = 'get' + UpperCase(id) + 'ValueList'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
      if not hasattr(property_holder, accessor_name) or override:
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter, accessor_args)
      # AcquiredProperty Getters
      if prop.get('acquired_property_id'):
        for aq_id in prop['acquired_property_id']:
          composed_id = "%s_%s" % (id, aq_id)
          # Getter
          # print "Set composed_id accessor %s" % composed_id
          accessor_name = 'get' + UpperCase(composed_id)
          # print "Set accessor_name accessor %s" % accessor_name
          accessor_args = (
                prop['type'],
                prop['portal_type'],
                aq_id,
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('storage_id'),
                prop.get('alt_accessor_id'),
                prop.get('acquisition_object_id'),
                (prop['type'] in list_types or prop.get('multivalued', 0)),
                (prop['type'] == 'tales')
                )
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.Getter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = '_baseGet' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.Getter, accessor_args)
          # Default Getter
          accessor_name = 'getDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.DefaultGetter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = '_baseGetDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.DefaultGetter, accessor_args)
          # List Getter
          ################# NOT YET
          # Setter
          accessor_name = 'set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, '_' + accessor_name, Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.Setter, accessor_args)
          accessor_name = '_baseSet' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.Setter, accessor_args)
          # Default Setter
          accessor_name = 'setDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, '_' + accessor_name, Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_setDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.DefaultSetter, accessor_args)
          accessor_name = '_baseSetDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, AcquiredProperty.DefaultSetter, accessor_args)
          # List Getter
          ################# NOT YET

  elif prop['type'] in list_types or prop.get('multivalued', 0):
    # The base accessor returns the first item in a list
    # and simulates a simple property
    # The default value is the first element of prop.get('default') if it exists
    default = prop.get('default')
    accessor_args = (prop['type'], prop.get('default'), prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.Getter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.Getter, accessor_args)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.DefaultGetter, accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.ListGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.ListGetter, accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.SetGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, List.SetGetter, accessor_args)
  elif prop['type'] == 'content':
    accessor_args = (prop['type'], prop.get('portal_type'), prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.Getter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.Getter, accessor_args)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.DefaultGetter, accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ListGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ListGetter, accessor_args)
    # Create value getters for a list property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ValueGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ValueGetter, accessor_args)
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.DefaultValueGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.DefaultValueGetter, accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ValueListGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Content.ValueListGetter, accessor_args)
    if prop.get('acquired_property_id'):
      for aq_id in prop['acquired_property_id']:
        for composed_id in ("%s_%s" % (id, aq_id), "default_%s_%s" % (id, aq_id)) :
          accessor_name = 'get' + UpperCase(composed_id)
          accessor_args = (prop['type'], aq_id, prop.get('portal_type'), prop.get('storage_id'))
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, ContentProperty.Getter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = 'get' + UpperCase(composed_id) + 'List'
          list_accessor_args = (prop['type'], aq_id + '_list', prop.get('portal_type'), prop.get('storage_id'))
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id + '_list',
                                             ContentProperty.Getter, list_accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          # No default getter YET XXXXXXXXXXXXXX
          # No list getter YET XXXXXXXXXXXXXX
          accessor_name = '_set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id, ContentProperty.Setter, accessor_args)
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_set' + UpperCase(composed_id) + 'List'
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, composed_id + '_list',
                                             ContentProperty.Setter, list_accessor_args)
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = 'set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, '_' + accessor_name, Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = 'set' + UpperCase(composed_id) + 'List'
          if not hasattr(property_holder, accessor_name) or override:
            property_holder.registerAccessor(accessor_name, '_' + accessor_name, Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          # No default getter YET XXXXXXXXXXXXXX
          # No list getter YET XXXXXXXXXXXXXX
  else:
    accessor_args = (prop['type'], prop.get('default'), prop.get('storage_id'))
    # Create getters for a simple property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Base.Getter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or override:
      property_holder.registerAccessor(accessor_name, id, Base.Getter, accessor_args)
  ######################################################
  # Create Setters
  if prop['type'] == 'group_type':
    # No setter
    pass
  elif prop['type'] in list_types or prop.get('multivalued', 0):
    # Create setters for a list property by aliasing
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    accessor_args = (prop['type'], prop.get('storage_id'))
    # Create setters for a list property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.Setter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.Setter, accessor_args)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.DefaultSetter, accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.DefaultSetter, accessor_args)
    setter_name = '_set' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.ListSetter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.ListSetter, accessor_args)
    setter_name = '_set' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.SetSetter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.SetSetter, accessor_args)
  elif prop['type'] == 'content':
    # Create setters for an object property
    # Create setters for a list property (reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    base_setter_name = 'set' + UpperCase(id)
    # The default setter sets the first item of a list without changing other items
    default_setter_name = 'setDefault' + UpperCase(id)
    # Create setters for an object property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + base_setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + default_setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + base_setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + default_setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    accessor_args = (prop['type'], prop.get('storage_id'))
    # Create setters for an object property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter, accessor_args)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter, accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter, accessor_args)
    setter_name = '_set' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter, accessor_args)
    setter_name = '_setDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter, accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter, accessor_args)
  else:
    accessor_args = (prop['type'], prop.get('storage_id'))
    # Create setters for a simple property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Base.Setter, accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Base.Setter, accessor_args)
  ######################################################
  # Create testers
  if prop['type'] == 'group_type':
    # No testters
    pass
  elif prop['type'] == 'content':
    # XXX This approach is wrong because testers for all properties
    # should be created upfront rather than on demand
    accessor_args = (prop['type'], prop.get('storage_id'))
    tester_name = 'has' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, Content.Tester, accessor_args)
      property_holder.declareProtected(read_permission, tester_name)
  else:
    accessor_args = (prop['type'], prop.get('storage_id'))
    tester_name = 'has' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, Base.Tester, accessor_args)
      property_holder.declareProtected(read_permission, tester_name)

    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, Base.Tester, accessor_args)

    # List Tester
    tester_name = 'has' + UpperCase(id) + 'List'
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, List.Tester, accessor_args)
      property_holder.declareProtected(read_permission, tester_name)
    tester_name = '_baseHas' + UpperCase(id) + 'List'
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, List.Tester, accessor_args)
    tester_name = 'hasDefault' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, List.Tester, accessor_args)
      property_holder.declareProtected(read_permission, tester_name)
    tester_name = '_baseHasDefault' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, List.Tester, accessor_args)

    # First Implementation of Boolean Accessor
    tester_name = 'is' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, Base.Getter,
                     (prop['type'], prop.get('default'), prop.get('storage_id')))
      property_holder.declareProtected(read_permission, tester_name)
    tester_name = '_baseIs' + UpperCase(id)
    if not hasattr(property_holder, tester_name) or prop.get('override', 0):
      property_holder.registerAccessor(tester_name, id, Base.Getter,
                     (prop['type'], prop.get('default'), prop.get('storage_id')))

from Accessor import Category

def createCategoryAccessors(property_holder, id,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent):
  """
    This function creates category accessor and setter for a class
    and a property
  """
  accessor_name = 'get' + UpperCase(id) + 'List'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.ListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'List'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.ListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.SetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.SetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'ItemList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.ItemListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)

  accessor_name = 'getDefault' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter, ())

  accessor_name = 'get' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter, ())

  accessor_name = 'has' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.Tester, ())
    property_holder.declareProtected(read_permission, accessor_name)

  setter_name = 'set' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  accessor_args = ()
  setter_name = '_set' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.Setter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.Setter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.ListSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.ListSetter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.SetSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.SetSetter, accessor_args)

  setter_name = '_setDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.DefaultSetter, accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.DefaultSetter, accessor_args)


from Accessor import Value, Related, RelatedValue, Translation

def createValueAccessors(property_holder, id,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent):
  """
    Creates relation accessors for category id

  """
  accessor_name = 'get' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ListGetter, ())
  accessor_name = UpperCase(id) + 'Values'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)

  accessor_name = 'get' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.SetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.SetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'TitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'TitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TranslatedTitleListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TranslatedTitleListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TranslatedTitleSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TranslatedTitleSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'ReferenceList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ReferenceListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ReferenceList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ReferenceListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'ReferenceSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ReferenceSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ReferenceSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.ReferenceSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'IdList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.IdListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'IdList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.IdListGetter, ())
  accessor_name = UpperCase(id) + 'Ids'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.IdListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)

  accessor_name = 'get' + UpperCase(id) + 'IdSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.IdSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'IdSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.IdSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'LogicalPathList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.LogicalPathListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPathList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.LogicalPathListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'LogicalPathSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.LogicalPathSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPathSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.LogicalPathSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.UidListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.UidListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.UidSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.UidSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'PropertyList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertyListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertyList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertyListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'PropertySet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertySetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertySet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertySetGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultGetter, ())
  accessor_name = 'get' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'TranslatedTitle'
  accessor = Value.DefaultTranslatedTitleGetter(accessor_name, id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedTitleGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedTitleGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Reference'
  accessor = Value.DefaultReferenceGetter(accessor_name, id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultReferenceGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultReferenceGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultReferenceGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultReferenceGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleOrIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleOrIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleOrIdGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTitleOrIdGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultPropertyGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultPropertyGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultPropertyGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultPropertyGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultLogicalPathGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultLogicalPathGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'TranslatedLogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedLogicalPathGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultLogicalPathGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultLogicalPathGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedLogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultTranslatedLogicalPathGetter, ())

  setter_name = 'set' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  accessor_args = ()
  setter_name = '_set' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.Setter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.Setter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.ListSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.ListSetter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.SetSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.SetSetter, accessor_args)

  setter_name = '_setDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.DefaultSetter, accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.DefaultSetter, accessor_args)

  # Uid setters
  setter_name = 'set' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name, Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = '_set' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetter, accessor_args)

  setter_name = '_setDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidDefaultSetter, accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidDefaultSetter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidListSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidListSetter, accessor_args)

  setter_name = '_set' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetSetter, accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetSetter, accessor_args)


def createRelatedValueAccessors(property_holder, id, read_permission=Permissions.AccessContentsInformation):

  upper_case_id = UpperCase(id)
  # Related Values (ie. reverse relation getters)

  # AccessorClass: (accessor_name, )
  accessor_dict = {
    # List getter
    RelatedValue.ListGetter: (
      '%s%sRelatedValues' % (upper_case_id[0].lower(),
                             upper_case_id[1:]),
      'get%sRelatedValueList' % upper_case_id,
      '_categoryGet%sRelatedValueList' % upper_case_id,
    ),

    # Set getter
    RelatedValue.SetGetter: (
      'get%sRelatedValueSet' % upper_case_id,
      '_categoryGet%sRelatedValueSet' % upper_case_id,
    ),

    # Default value getter
    RelatedValue.DefaultGetter: (
      'getDefault%sRelatedValue' % upper_case_id,
      'get%sRelatedValue' % upper_case_id,
      '_categoryGetDefault%sRelatedValue' % upper_case_id,
      '_categoryGet%sRelatedValue' % upper_case_id,
    ),

    # Related Relative Url
    Related.ListGetter: (
      'get%sRelatedList' % upper_case_id,
      '_categoryGet%sRelatedList' % upper_case_id,
    ),

    # Related as Set
    Related.SetGetter: (
      'get%sRelatedSet' % upper_case_id,
      '_categoryGet%sRelatedSet' % upper_case_id,
    ),

    # Default getter
    Related.DefaultGetter: (
      'getDefault%sRelated' % upper_case_id,
      'get%sRelated' % upper_case_id,
      '_categoryGetDefault%sRelated' % upper_case_id,
      '_categoryGet%sRelated' % upper_case_id,
    ),

    # Related Ids (ie. reverse relation getters)
    RelatedValue.IdListGetter: (
      '%s%sRelatedIds' % (upper_case_id[0].lower(),
                          upper_case_id[1:]),
      'get%sRelatedIdList' % upper_case_id,
      '_categoryGet%sRelatedIdList' % upper_case_id,
    ),

    # Related Ids as Set
    RelatedValue.IdSetGetter: (
      'get%sRelatedIdSet' % upper_case_id,
      '_categoryGet%sRelatedIdSet' % upper_case_id,
    ),

    # Default Id getter
    RelatedValue.DefaultIdGetter: (
      'getDefault%sRelatedId' % upper_case_id,
      'get%sRelatedId' % upper_case_id,
      '_categoryGetDefault%sRelatedId' % upper_case_id,
      '_categoryGet%sRelatedId' % upper_case_id,
    ),

    # Related Title list
    RelatedValue.TitleListGetter: (
      'get%sRelatedTitleList' % upper_case_id,
      '_categoryGet%sRelatedTitleList' % upper_case_id,
    ),

    # Related Title Set
    RelatedValue.TitleSetGetter: (
      'get%sRelatedTitleSet' % upper_case_id,
      '_categoryGet%sRelatedTitleSet' % upper_case_id,
    ),

    # Related default title
    RelatedValue.DefaultTitleGetter: (
      'getDefault%sRelatedTitle' % upper_case_id,
      'get%sRelatedTitle' % upper_case_id,
      '_categoryGetDefault%sRelatedTitle' % upper_case_id,
      '_categoryGet%sRelatedTitle' % upper_case_id,
    ),

    # Related Property list
    RelatedValue.PropertyListGetter: (
      'get%sRelatedPropertyList' % upper_case_id,
      '_categoryGet%sRelatedPropertyList' % upper_case_id,
    ),

    # Related Property Set
    RelatedValue.PropertySetGetter: (
      'get%sRelatedPropertySet' % upper_case_id,
      '_categoryGet%sRelatedPropertySet' % upper_case_id,
    ),

    # Related default title
    RelatedValue.DefaultPropertyGetter: (
      'getDefault%sRelatedProperty' % upper_case_id,
      'get%sRelatedProperty' % upper_case_id,
      '_categoryGetDefault%sRelatedProperty' % upper_case_id,
      '_categoryGet%sRelatedProperty' % upper_case_id,
    ),
  }

  for accessor_class, accessor_name_list in accessor_dict.items():
    for accessor_name in accessor_name_list:
      if property_holder is not None:
        if not hasattr(property_holder, accessor_name):
          property_holder.registerAccessor(accessor_name, id, accessor_class, ())
          if accessor_name[0] != '_':
            property_holder.declareProtected(read_permission, accessor_name)
      else:
        accessor = accessor_class(accessor_name, id)
        if not hasattr(BaseClass, accessor_name):
          setattr(BaseClass, accessor_name,
                  accessor.dummy_copy(accessor_name))
          # Declare the security of method which doesn't start with _
          if accessor_name[0] != '_':
            BaseClass.security.declareProtected(read_permission, accessor_name)

def createGroupTypeAccessors(property_holder, prop,
  read_permission=None, portal=None):
  """
  Generate accessors that allows to know if we belongs to a particular
  group of portal types
  """
  raise ValueError("This method is not used. Remove it?")
  # Getter
  group = prop['group_type']
  accessor_name = 'is' + UpperCase(group) + 'Type'
  value = prop['default']
  accessor_args = (value,)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, ConstantGetter,
                                     accessor_args)
    property_holder.declareProtected(read_permission, accessor_name)

def createTranslationAcquiredPropertyAccessors(
  property_holder,
  property,
  read_permission=Permissions.AccessContentsInformation,
  write_permission=Permissions.ModifyPortalContent,
  portal=None):
  """Generate translation acquired property accessor to Base class"""
  property = property.copy()
  translation_acquired_property_id_list = []
  accessor_dict_list = []

  # Language Dependent Getter/Setter
  for language in portal.Localizer.get_languages():
    language_key = language.replace('-', '_')
    for acquired_property_id in property['acquired_property_id']:
      key = '%s_translated_%s' % (language_key, acquired_property_id)
      capitalised_composed_id = UpperCase("%s_%s" % (property['id'], key))
      accessor_args = (
        property['type'],
        property['portal_type'],
        key,
        property['acquisition_base_category'],
        property['acquisition_portal_type'],
        property['acquisition_accessor_id'],
        property.get('acquisition_copy_value',0),
        property.get('acquisition_mask_value',0),
        property.get('storage_id'),
        property.get('alt_accessor_id'),
        property.get('acquisition_object_id'),
        (property['type'] in list_types or property.get('multivalued', 0)),
        (property['type'] == 'tales'),
        )

      accessor_dict_list.append({'name':'get' + capitalised_composed_id,
                                 'key': key,
                                 'class':Translation.AcquiredPropertyGetter,
                                 'argument':accessor_args,
                                 'permission':read_permission})
      accessor_dict_list.append({'name':'_baseGet' + capitalised_composed_id,
                                 'key': key,
                                 'class':Translation.AcquiredPropertyGetter,
                                 'argument':accessor_args,
                                 'permission':read_permission})
      accessor_dict_list.append({'name': 'getDefault' + capitalised_composed_id,
                                 'key': key,
                                 'class': Translation.AcquiredPropertyGetter,
                                 'argument': accessor_args,
                                 'permission': read_permission})
      accessor_dict_list.append({'name': 'set' + capitalised_composed_id,
                                 'key': '_set' + capitalised_composed_id,
                                 'class': Alias.Reindex,
                                 'argument': (),
                                 'permission': write_permission})
      accessor_dict_list.append({'name': '_set' + capitalised_composed_id,
                                 'key': key,
                                 'class': AcquiredProperty.DefaultSetter,
                                 'argument': accessor_args,
                                 'permission': write_permission})
      accessor_dict_list.append({'name': 'setDefault' + capitalised_composed_id,
                                 'key': '_set' + capitalised_composed_id,
                                 'class': Alias.Reindex,
                                 'argument': (),
                                 'permission': write_permission})

  # Language Independent Getter
  for acquired_property_id in property['acquired_property_id']:
    if acquired_property_id in property.get('translation_acquired_property_id',()):
      key = 'translated_%s' % acquired_property_id
      capitalised_composed_id = UpperCase('%s_%s' % (property['id'], key))
      accessor_args = (
        property['type'],
        property['portal_type'],
        key,
        property['acquisition_base_category'],
        property['acquisition_portal_type'],
        property['acquisition_accessor_id'],
        property.get('acquisition_copy_value',0),
        property.get('acquisition_mask_value',0),
        property.get('storage_id'),
        property.get('alt_accessor_id'),
        property.get('acquisition_object_id'),
        (property['type'] in list_types or property.get('multivalued', 0)),
        (property['type'] == 'tales'),
        )

      accessor_dict_list.append({'name': 'get' + capitalised_composed_id,
                                 'key': key,
                                 'class': Translation.AcquiredPropertyGetter,
                                 'argument': accessor_args,
                                 'permission': read_permission})
      accessor_dict_list.append({'name': '_baseGet' + capitalised_composed_id,
                                 'key': key,
                                 'class': Translation.AcquiredPropertyGetter,
                                 'argument': accessor_args,
                                 'permission': read_permission})
      accessor_dict_list.append({'name': 'getDefault' + capitalised_composed_id,
                                 'key': key,
                                 'class': Translation.AcquiredPropertyGetter,
                                 'argument': accessor_args,
                                 'permission': read_permission})

  for accessor_dict in accessor_dict_list:
    accessor_name = accessor_dict['name']
    if getattr(property_holder, accessor_name, None) is None:
      property_holder.registerAccessor(accessor_name, # id
                                       accessor_dict['key'],
                                       accessor_dict['class'],
                                       accessor_dict['argument'])
      property_holder.declareProtected(accessor_dict['permission'],
                                       accessor_name)

def createTranslationAccessors(property_holder, id, property,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent, default=''):
  """
  Generate the translation accessor for a class and a property
  """
  capitalised_id = UpperCase(id)
  if 'translated' in id:
    accessor_name = 'get' + capitalised_id
    private_accessor_name = '_baseGet' + capitalised_id
    if not hasattr(property_holder, accessor_name):
      property_holder.registerAccessor(accessor_name,
                                       id,
                                       Translation.TranslatedPropertyGetter,
                                       (property['id'], property['type'], None, default))
      property_holder.declareProtected(read_permission, accessor_name)
    if not hasattr(property_holder, private_accessor_name):
      property_holder.registerAccessor(private_accessor_name,
                                       id,
                                       Translation.TranslatedPropertyGetter,
                                       (property['id'], property['type'], None, default))

  if 'translation_domain' in id:
    # Getter
    accessor_name = 'get' + capitalised_id
    property_holder.registerAccessor(accessor_name,
                                     id,
                                     Translation.PropertyTranslationDomainGetter,
                                     ('string', default,))
    property_holder.declareProtected(read_permission, accessor_name)


def createTranslationLanguageAccessors(property_holder, property,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent, default='',
    portal=None):
  """
  Generate translation language accessors
  """
  accessor_dict_list = []

  localizer = getattr(portal, 'Localizer', None)
  if localizer is None:
    if not getattr(portal, '_v_bootstrapping', False):
      warnings.warn("Localizer is missing. Accessors can not be generated.")
    return

  for language in localizer.get_languages():
    language_key = language.replace('-', '_')
    composed_id = '%s_translated_%s' % (language_key, property['id'])
    capitalised_compose_id = UpperCase(composed_id)

    # get
    getter_accessor_args = (property['id'], property['type'], language, default)
    accessor_dict_list.append({'name': 'get' + capitalised_compose_id,
                               'class': Translation.TranslatedPropertyGetter,
                               'argument': getter_accessor_args,
                               'permission': read_permission})
    accessor_dict_list.append({'name': '_baseGet' + capitalised_compose_id,
                               'class': Translation.TranslatedPropertyGetter,
                               'argument': getter_accessor_args,
                               'permission': read_permission})

    # has
    has_accessor_args = (property['id'], property['type'], language)
    accessor_dict_list.append({'name': 'has' + capitalised_compose_id,
                               'class': Translation.TranslatedPropertyTester,
                               'argument': has_accessor_args,
                               'permission': read_permission})

    # set
    accessor_dict_list.append({'name':'set' + capitalised_compose_id,
                               'key': '_set' + capitalised_compose_id,
                               'class': Alias.Reindex,
                               'argument': (),
                               'permission': write_permission})
    setter_accessor_args = (property['id'], property['type'], language)
    accessor_dict_list.append({'name': '_set' + capitalised_compose_id,
                               'class': Translation.TranslationPropertySetter,
                               'argument': setter_accessor_args,
                               'permission': write_permission})

  for accessor_dict in accessor_dict_list:
    accessor_name = accessor_dict['name']
    if getattr(property_holder, accessor_name, None) is None:
      property_holder.registerAccessor(accessor_name,
                                       accessor_dict.get('key', None),
                                       accessor_dict['class'],
                                       accessor_dict['argument'])
      property_holder.declareProtected(accessor_dict['permission'],
                                       accessor_name)


#####################################################
# More Useful methods which require Base
#####################################################

def assertAttributePortalType(o, attribute_name, portal_type):
  """
    portal_type   --    string or list
  """
  # Checks or deletes
  if getattr(o, attribute_name, None) is not None:
    value = getattr(o, attribute_name)
    if not isinstance(value, BaseClass):
      # Delete local attribute if it exists
      if getattr(aq_self(o), attribute_name, None) is not None:
        delattr(o, attribute_name)
      # But do not delete object
      #if attribute_name in o.objectIds():
      #  o._delObject(attribute_name)
    if o._getOb(attribute_name, None) is not None:
      try:
        if isinstance(portal_type, str):
          portal_type = [portal_type]
        if getattr(o, attribute_name).portal_type not in portal_type:
          o._delObject(attribute_name)
      except (KeyError, AttributeError), err:
        LOG('ERP5Type', PROBLEM, "assertAttributePortalType failed on %s" % o,
            error=err)

#####################################################
# Monkey Patch
#####################################################

from types import FunctionType
def monkeyPatch(from_class,to_class):
  for id, m in from_class.__dict__.items():
      if type(m) is FunctionType:
          setattr(to_class, id, m)


def sleep(t=5):
  """
  Wait for a given time
  """
  time.sleep(t)


#####################################################
# Timezones
#####################################################

def getCommonTimeZoneList():
  """ Get common (country/capital(major cities) format) timezones list """
  try:
    from pytz import common_timezones
  except ImportError:
    return []
  return common_timezones


#####################################################
# Processing of ZRDB.Results objects
#####################################################

from Shared.DC.ZRDB.Results import Results

def mergeZRDBResults(results, key_column, edit_result):
  """
  Merge several ZRDB.Results into a single ZRDB.Results. It's done in 3 steps:
   1. Rename columns of every table (cf 1st parameter).
   2. Merge all source tables into a intermediate sparse table.
      Each processed row is identified according to the columns specified in the
      2nd parameter: Rows with the same values in the specified columns are
      merged together, otherwise they are stored separately.
   3. Convert the intermediate table into a ZRDB.Results structure.
      Cell values are copied or created according the 3rd parameter.
      By default, values aren't modified and empty cells are set to None.

  results     - List of ZRDB.Results to merge. Each item can also be a tuple
                (ZRDB.Results, rename_map) : the columns are renamed before
                any other processing, according to rename_map (dict).
  key_column  - 2 rows are merged if and only if there is the same value in
                the common column(s) specified by key_column.
                key_column can be either a string or a sequence of strings.
                () can be passed to merge 1-row tables.
  edit_result - Map { column_name: function | defaut_value } allowing to edit
                values (or specify default values) for certain columns in the
                resulting table:
                 - function (lambda row, column_name: new_value)
                 - default_value is interpreted as
                   (lambda row, column: row.get(column, default_value))
                Note that whenever a row doesn't have a matching row in every
                other table, the merged result before editing may contain
                incomplete rows. get_value also allows you to fill these rows
                with specific values, instead of the default 'None' value.
  """
  if isinstance(key_column,str):
    key_column = key_column,

  ## Variables holding the resulting table:
  items = [] # list of columns: each element is an item (cf ZRDB.Results)
  column_list = [] # list of columns:
                   # each element is a pair (column name, get_value)
  data = [] # list of rows of maps column_name => value

  ## For each key, record the row number in 'data'
  index = {}

  ## Set of columns already seen
  column_set = set()

  for r in results:
    ## Step 1
    if isinstance(r, Results):
      rename = {}
    else:
      r, rename = r
    new_column_list = []
    columns = {}
    for i, column in enumerate(r._searchable_result_columns()):
      name = column['name']
      name = rename.get(name, name)
      if name is None:
        continue
      columns[name] = i
      if name not in column_set:
        column_set.add(name)
        new_column_list.append(i)
        column = column.copy()
        column['name'] = name
        items.append(column)
        # prepare step 3
        get_value = edit_result.get(name)
        column_list += (name, hasattr(get_value, '__call__') and get_value or
          (lambda row, column, default=get_value: row.get(column, default))),

    ## Step 2
    try:
      index_pos = [ columns[rename.get(name,name)] for name in key_column ]
    except KeyError:
      raise KeyError("Missing '%s' column in source table" % name)
    for row in r:
      key = tuple(row[i] for i in index_pos)
      if key in index: # merge the row to an existing one
        merged_row = data[index[key]]
      else: # new row
        index[key] = len(data)
        merged_row = {}
        data.append(merged_row)
      for column, i in columns.iteritems():
        merged_row[column] = row[i]

  ## Step 3
  return Results((items, [
      [ get_value(row, column) for column, get_value in column_list ]
      for row in data
    ]))

#####################################################
# SQL text escaping
#####################################################
def sqlquote(x):
  """
  Escape data suitable for inclusion in generated ANSI SQL92 code for
  cases where bound variables are not suitable.

  Inspired from zope/app/rdb/__init__.py:sqlquote, modified to:
   - use isinstance instead of type equality
   - use string member methods instead of string module
  """
  if isinstance(x, basestring):
    x = "'" + x.replace('\\', '\\\\').replace("'", "''") + "'"
  elif isinstance(x, (int, long, float)):
    pass
  elif x is None:
    x = 'NULL'
  else:
    raise TypeError, 'do not know how to handle type %s' % type(x)
  return x

#####################################################
# Hashing
#####################################################

class GenericSum:
  def __init__(self, sum):
    self.sum = sum

  def digest(self):
    return self.sum.digest()

  def hexdigest(self):
    return self.sum.hexdigest()

  def update(self, data):
    self.sum.update(data)

  def copy(self):
    return self.__class__(self.sum.copy())

class md5(GenericSum):
  def __init__(self, *args):
    GenericSum.__init__(self, md5_new(*args))

allow_class(md5)

class sha(GenericSum):
  def __init__(self, *args):
    GenericSum.__init__(self, sha_new(*args))

allow_class(sha)

try:
  import smbpasswd
  class SambaPassword:
    def __init__(self):
      self.sum = smbpasswd

    def hash(self, value):
      return self.sum.hash(value)
except ImportError:
  class SambaPassword:
    pass
allow_class(SambaPassword)

#####################################################
# Security
#####################################################

def _setSuperSecurityManager(self, user_name=None):
  """ Change to super user account or passed user_name.
      Return original Security Manager
  """
  original_security_manager = getSecurityManager()
  if user_name is not None:
    user_folder = self.getPortalObject().acl_users
    user = user_folder.getUserById(user_name).__of__(user_folder)
  else:
    user = self.getWrappedOwner()
  newSecurityManager(self.REQUEST, user)
  return original_security_manager

#####################################################
# Processing of Conflict Resolver
#####################################################

class ScalarMaxConflictResolver(persistent.Persistent):
  """
    Store the last id generated
    The object support application-level conflict resolution
  """

  def __init__(self, value=0):
    self.value = value

  def __getstate__(self):
    return self.value

  def __setstate__(self, value):
    self.value = value

  def set(self, value):
    self.value = value

  def _p_resolveConflict(self, old, first_id, second_id):
    return max(first_id, second_id)

###################
#  URL Normaliser #
###################
from Products.PythonScripts.standard import url_unquote
try:
  import urlnorm
except ImportError:
  warnings.warn("urlnorm lib is not installed", DeprecationWarning)
  urlnorm = None
import urlparse
import urllib

# Regular expressions
re_cleanup_anchors = re.compile('#.*')
re_extract_port = re.compile(':(\d+)$')
def uppercaseLetter(matchobject):
  return matchobject.group(0).upper()
re_cleanup_escaped_url = re.compile('%\w\d')
re_cleanup_slashes = re.compile('/{2,}')
re_cleanup_tail = re.compile('\??$')

def legacyNormalizeUrl(url, base_url=None):
  """this method does normalisation itself.
  The result is less reliable but better than nothing
  """
  from Products.ERP5.mixin.url import no_host_protocol_list
  # remove anchors
  # http://www.example.com/page.html#ll -> http://www.example.com/page.html
  url = re_cleanup_anchors.sub('', url)
  url_split = urlparse.urlsplit(url)
  url_sheme = url_split[0]
  url_netloc = url_split[1]
  url_path = url_split[2]
  url_params = url_split[3]
  url_query = url_split[4]
  # strip ending dot in domain
  url_netloc = url_netloc.rstrip('.')
  if url_netloc:
    # Strip default port number
    # http://www.example.com:80/bar.html -> http://www.example.com/bar.html
    # https://www.example.com:443/bar.html -> https://www.example.com/bar.html
    protocol_port_mapping_dict = {'http': '80',
                                  'https': '443',
                                  'ftp': '21'}
    for protocol, port in protocol_port_mapping_dict.items():
      # extract port_number from domain
      match_object = re_extract_port.search(url_netloc)
      if url_sheme == protocol and match_object is not None and\
        match_object.group(1) == port:
        url_domain = re_extract_port.sub('', url_domain)
  if url_sheme in no_host_protocol_list:
    return url
  if base_url and not (url_sheme or url_netloc):
    # Make relative URL absolute
    url = urlparse.urljoin(base_url, url)
  # Remove double slashes
  # http://www.example.com//bar.html -> http://www.example.com/bar.html
  url_path = re_cleanup_slashes.sub('/', url_path)
  url = urlparse.urlunsplit((url_sheme, url_netloc, url_path,
                             url_params, url_query,))
  # Uppercase escaped characters
  # http://www.example.com/a%c2%b1b -> http://www.example.com/a%C2%B1b 
  re_cleanup_escaped_url.sub(uppercaseLetter, url)
  # Remove trailing '?'
  # http://www.example.com/? -> http://www.example.com/
  url = re_cleanup_tail.sub('', url)
  if isinstance(url, unicode):
    url = url.encode('utf-8')
  return url

def urlnormNormaliseUrl(url, base_url=None):
  """The normalisation up is delegated to urlnorm library.
  """
  try:
    try:
      url = urlnorm.norm(url)
    except UnicodeDecodeError:
      url = urlnorm.norm(url_unquote(url).decode('latin1'))
  except (AttributeError, UnicodeDecodeError, urlnorm.InvalidUrl):
    # This url is not valid, a better Exception will
    # be raised
    return url
  url_split = urlparse.urlsplit(url)
  url_protocol = url_split[0]
  url_domain = url_split[1]
  if base_url and not (url_protocol or url_domain):
    # Make relative URL absolute
    url = urlparse.urljoin(base_url, url)
  if isinstance(url, unicode):
    url = url.encode('utf-8')
  return url

if urlnorm is not None:
  normaliseUrl = urlnormNormaliseUrl
else:
  normaliseUrl = legacyNormalizeUrl

def guessEncodingFromText(data, content_type='text/html'):
  """
    Try to guess the encoding for this string.
    Returns None if no encoding can be guessed.
  This utility try use chardet for text/html
  By default python-magic is used
  XXX this implementation must migrate to cloudooo
  """
  if chardet is not None and content_type == 'text/html':
    # chardet works fine on html document
    return chardet.detect(data).get('encoding', None)
  elif magic is not None:
    # libmagic provides better result
    # for text/plain documents.
    enconding_detector = magic.Magic(mime_encoding=True)
    return enconding_detector.from_buffer(data)
  else:
    if chardet is None:
      message = 'No encoding detector found.'\
                ' You must install chardet and python-magic'
    else:
      message = 'No suitable encoding detector found.'\
                ' You must install python-magic'
    raise NotImplementedError, message

_reencodeUrlEscapes_map = dict((chr(x), chr(x) in (# safe
                                                   "!'()*-." "0123456789" "_~"
                                                   "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                                   "abcdefghijklmnopqrstuvwxyz"
                                                   # reserved (maybe unsafe)
                                                   "#$&+,/:;=?@[]")
                                        and chr(x) or "%%%02X" % x)
                               for x in xrange(256))
def reencodeUrlEscapes(url):
  """Fix a non-conformant %-escaped URL (or quote an unescaped one)

  This is a Python reimplementation of 'reencode_escapes' function of Wget 1.12
  """
  from string import hexdigits
  next_part = iter(url.split('%')).next
  url = [_reencodeUrlEscapes_map[c] for c in next_part()]
  try:
    while True:
      part = next_part()
      url.append('%')
      if len(part) < 2 or not (part[0] in hexdigits and part[1] in hexdigits):
        url.append('25')
      url += [_reencodeUrlEscapes_map[c] for c in part]
  except StopIteration:
    return ''.join(url)

from zope.tales.engine import Engine
from zope.tales.tales import CompilerError

def isValidTALESExpression(value):
  """return if given value is valid TALES Expression.
  This validator only validates Syntax of TALES Expression,
  it does not tell that Expression is callable on given context

  - value: string we try to compile

  return tuple: (boolean result, error_message or None)
  """
  try:
    Engine.compile(value)
  except CompilerError, message:
    return False, message
  else:
    return True, None
