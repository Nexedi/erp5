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
import threading
import time
import warnings
import sys
import inspect
import persistent
from hashlib import md5 as md5_new, sha1 as sha_new
from lxml import html
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

# XXX-JPS: We need naming conventions and central list of decorators.
def simple_decorator(decorator):
  """Decorator to turn simple function into well-behaved decorator

  See also http://wiki.python.org/moin/PythonDecoratorLibrary

  XXX We should use http://pypi.python.org/pypi/decorator/ instead,
      to make decorators ZPublisher-friendly (but it is probably to slow).
  """
  def new_decorator(f):
    g = decorator(f)
    try:
      g.__name__ = f.__name__
    except AttributeError:
      # XXX: Should be "convertToMixedCase(f._transition_id)"
      g.__name__ = f._m.__name__ # WorkflowMethod
    else:
      g.__doc__ = f.__doc__
      g.__dict__.update(f.__dict__)
    g._original = f # for tab_completion navigation in IPython
    return g
  # Now a few lines needed to make simple_decorator itself
  # be a well-behaved decorator.
  new_decorator.__name__ = decorator.__name__
  new_decorator.__doc__ = decorator.__doc__
  new_decorator._original = decorator # for tab_completion navigation in IPython
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

warnings.simplefilter("default")

def _showwarning(message, category, filename, lineno, file=None, line=None):
  if file is None:
    LOG("%s:%u %s: %s" % (filename, lineno, category.__name__, message),
        WARNING, '')
  else:
    file.write(warnings.formatwarning(message, category, filename, lineno, line))
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

_pylint_message_re = re.compile(
  '^(?P<type>[CRWEF]):\s*(?P<row>\d+),\s*(?P<column>\d+):\s*(?P<message>.*)$')

def checkPythonSourceCode(source_code_str, portal_type=None):
  """
  Check source code with pylint or compile() builtin if not available.

  TODO-arnau: Get rid of NamedTemporaryFile (require a patch on pylint to
              allow passing a string) and this should probably return a proper
              ERP5 object rather than a dict...
  """
  if not source_code_str:
    return []

  try:
    from pylint.lint import Run
    from pylint.reporters.text import TextReporter
  except ImportError, error:
    try:
      compile(source_code_str, '<string>', 'exec')
      return []
    except Exception, error:
      if isinstance(error, SyntaxError):
        message = {'type': 'F',
                   'row': error.lineno,
                   'column': error.offset,
                   'text': error.message}
      else:
        message = {'type': 'F',
                   'row': -1,
                   'column': -1,
                   'text': str(error)}

      return [message]

  import cStringIO
  import tempfile
  import sys

  #import time
  #started = time.time()
  message_list = []
  output_file = cStringIO.StringIO()
  try:
    with tempfile.NamedTemporaryFile(suffix='.py') as input_file:
      input_file.write(source_code_str)
      input_file.flush()

      args = [input_file.name, '--reports=n', '--indent-string="  "',
           # Disable Refactoring and Convention messages which are too verbose
           # TODO-arnau: Should perphaps check ERP5 Naming Conventions?
           '--disable=R,C',
           # 'String statement has no effect': eg docstring at module level
           '--disable=W0105',
           # 'Using possibly undefined loop variable %r': Spurious warning
           # (loop variables used after the loop)
           '--disable=W0631',
           # 'fixme': No need to display TODO/FIXME entry in warnings
           '--disable=W0511',
           # 'Unused argument %r': Display for readability or when defining abstract methods
           '--disable=W0613',
           # 'Catching too general exception %s': Too coarse
           # TODO-arnau: Should consider raise in except
           '--disable=W0703',
           # 'Used * or ** magic': commonly used in ERP5
           '--disable=W0142',
           # 'Class has no __init__ method': Spurious warning
           '--disable=W0232',
           # 'Attribute %r defined outside __init__': Spurious warning
           '--disable=W0201',
           # Dynamic class generation so some attributes may not be found
           # TODO-arnau: Enable it properly would require inspection API
           # '%s %r has no %r member'
           '--disable=E1101,E1103',
           # 'No name %r in module %r'
           '--disable=E0611',
           # map and filter should not be considered bad as in some cases
           # map is faster than its recommended replacement (list
           # comprehension)
           '--bad-functions=apply,input',
           # 'Access to a protected member %s of a client class'
           '--disable=W0212',
           # string module does not only contain deprecated functions...
           '--deprecated-modules=regsub,TERMIOS,Bastion,rexec']

      if portal_type == 'Interface Component':
        # Interface inherits from InterfaceClass:
        # Inheriting 'Interface', which is not a class. (inherit-non-class)
        args.append('--disable=E0239')
        # Interfaces methods may have no arguments:
        # Method has no argument (no-method-argument)
        args.append('--disable=E0211')
        # Method should have "self" as first argument (no-self-argument)
        args.append('--disable=E0213')

      try:
        from pylint.extensions.bad_builtin import __name__ as ext
        args.append('--load-plugins=' + ext)
      except ImportError:
        pass
      Run(args, reporter=TextReporter(output_file), exit=False)

    output_file.reset()
    for line in output_file:
      match_obj = _pylint_message_re.match(line)
      if match_obj:
        message_list.append({'type': match_obj.group('type'),
                             'row': int(match_obj.group('row')),
                             'column': int(match_obj.group('column')),
                             'text': match_obj.group('message')})
  finally:
    output_file.close()

  #LOG('Utils', INFO, 'Checking time (pylint): %.2f' % (time.time() - started))
  return message_list

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
  with open(path) as f:
    return f.read()

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
  with open(path, 'w') as f:
    f.write(text)
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
  with open(path) as f:
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
    with open(path) as f:
      module = imp.load_source(class_id, path, f)
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
  with open(path) as f:
    module = imp.load_source(class_id, path, f)
    setattr(Products.ERP5Type.Constraint, class_id, getattr(module, class_id))

def importLocalInteractor(class_id, path=None):
  import Products.ERP5Type.Interactor
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Interactor")
  path = os.path.join(path, "%s.py" % class_id)
  with open(path) as f:
    module = imp.load_source(class_id, path, f)
    setattr(Products.ERP5Type.Interactor, class_id, getattr(module, class_id))
    registerInteractorClass(class_id, getattr(Products.ERP5Type.Interactor, class_id))

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
  with open(path) as f:
    return f.read()

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
  with open(path) as f:
    return f.read()

def readLocalConstraint(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Constraint")
  path = os.path.join(path, "%s.py" % class_id)
  with open(path) as f:
    return f.read()

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
  with open(path, 'w') as f:
    f.write(text)

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
  with open(path, 'w') as f:
    f.write(text)

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
  with open(path, 'w') as f:
    f.write(text)
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
  with open(path) as f:
    return f.read()

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
  with open(path, 'w') as f:
    f.write(text)

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


def importLocalDocument(class_id, path=None, class_path=None):
  """Imports a document class and registers it in ERP5Type Document
  repository ( Products.ERP5Type.Document )
  """
  import Products.ERP5Type.Document

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
  sys.modules[module_name] = module
  setattr(Products.ERP5Type.Document, class_id, module)

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
              % (directory_name, module_name, document_path), error=True)

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

  if old_value:
    if class_name == 'CategoryTool':
      if module_name == 'Products.CMFCategory.CategoryTool':
        LOG('Utils', WARNING,
            "Ignoring replacement of %s by %s" % (old_value, new_value))
        return
      assert module_name == 'Products.ERP5.Tool.CategoryTool', module_name
      LOG('Utils', WARNING, "Replacing %s by %s" % (old_value, new_value))
    else:
      raise Exception("Class %s and %s from different products have the "
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
    import importlib
    path, module_id_list = getModuleIdList(package_home(this_module.__dict__), 'mixin')
    for module_id in module_id_list:
      submodule = importlib.import_module('%s.%s' % (mixin_module.__name__, module_id))
      for klassname, klass in inspect.getmembers(submodule, inspect.isclass):
        # only classes defined here
        if 'mixin' in klass.__module__ and not issubclass(klass, Exception):
          classpath = '.'.join((module_name, 'mixin', module_id, klassname))
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
    import erp5.component
  except ImportError:
    from .dynamic.dynamic_module import initializeDynamicModules
    initializeDynamicModules()
    import erp5.portal_type
    import erp5.component

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

  # Register Help and API Reference. This trick to make registerHelp works
  # with 2 directories was taken originally from CMFCore, but it required at
  # least a (possibly) help directory...
  help = context.getProductHelp()
  lastRegistered = help.lastRegistered

  help_list = []
  for d in 'help', 'interfaces':
    if os.path.exists(os.path.join(this_module.__path__[0], d)):
      context.registerHelp(directory=d, clear=1)
      help_list.append(d)

  if help.lastRegistered != lastRegistered and len(help_list) > 1:
    for i, d in enumerate(help_list):
      help.lastRegistered = None
      context.registerHelp(directory=d, clear=not i)

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

#####################################################
# TALES Expression
#####################################################

# This gets the Engine and CompilerError classes for TALES Expression
# wherever it is defined (which is different depending on the Zope
# version)
ExpressionEngine = getEngine()
CompilerError = ExpressionEngine.getCompilerError()

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
  ec = ExpressionEngine.getContext(data)
  tv[cache_key] = ec
  return ec

def evaluateExpressionFromString(expression_context, expression_string):
  """
  Evaluate a TALES Expression from the given string with the given
  Expression context (as returned by createExpressionContext for
  instance).

  Any exception normally raised when parsing and evaluating a TALES
  Expression is re-raised as a ValueError.

  @param expression_context: Expression context
  @type expression_context: Products.PageTemplates.Expressions.ZopeContext
  @param expression_string: TALES Expression string to evaluate
  @type expression_string: str
  """
  if expression_string is None:
    return None

  try:
    return Expression(expression_string)(expression_context)
  # An AttributeError is raised when instanciating an Expression
  # class, and CompilerError and ValueError are raised in case of
  # error when evaluation the expression
  except (AttributeError, CompilerError, ValueError), e:
    raise ValueError("Error in TALES expression: '%s': %s" % (expression_string,
                                                              str(e)))

def isValidTALESExpression(value):
  """return if given value is valid TALES Expression.
  This validator only validates Syntax of TALES Expression,
  it does not tell that Expression is callable on given context

  - value: string we try to compile

  return tuple: (boolean result, error_message or None)
  """
  try:
    ExpressionEngine.compile(value)
  except CompilerError, message:
    return False, message
  else:
    return True, None

#####################################################
# More Useful methods which require Base
#####################################################
from Products.ERP5Type.Base import Base as BaseClass

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
            error=True)

#####################################################
# Miscellaneous
#####################################################

def sleep(t=5):
  """
  Wait for a given time
  """
  time.sleep(t)

def stopProcess(process, graceful=5):
    if process.pid and process.returncode is None:
        if graceful:
            process.terminate()
            t = threading.Timer(graceful, process.kill)
            t.start()
            # PY3: use waitid(WNOWAIT) and call process.poll() after t.cancel()
            r = process.wait()
            t.cancel()
            return r
        process.kill()
        return process.wait()

from ctypes import CDLL, util as ctypes_util, get_errno, c_int, c_long
libc = CDLL(ctypes_util.find_library('c'), use_errno=True)

class Prctl(object):

    def __init__(self, option, nargs=1):
        self.option = option
        self.args0 = (0,) * (4 - nargs)

    def __call__(self, *args):
        try:
            prctl = self._prctl
        except AttributeError:
            prctl = self._prctl = libc.prctl
            prctl.argtypes = c_int, c_long, c_long, c_long, c_long
        r = prctl(self.option, *(args + self.args0))
        if r == -1:
            e = get_errno()
            raise OSError(e, os.strerror(e))
        return r

PR_SET_PDEATHSIG = Prctl(1)

#####################################################
# Timezones
#####################################################

def getCommonTimeZoneList():
  """ Get common (country/capital(major cities) format) timezones list """
  try:
    from pytz import common_timezones
  except ImportError:
    return ()
  return tuple(common_timezones)


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

_reencodeUrlEscapes_map = {chr(x): chr(x) if chr(x) in
    # safe
    "!'()*-." "0123456789" "_~"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    # reserved (maybe unsafe)
    "#$&+,/:;=?@[]"
  else "%%%02X" % x
  for x in xrange(256)}

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

#####################################################
# Replacement for Products.CMFDefault
#####################################################

class IllegalHTML(ValueError):
    """ Illegal HTML error.
    """


def bodyfinder(text):
  try:
    return html.tostring(html.fromstring(text).find("body"))
  except Exception:
    return text


def formatRFC822Headers(headers):
  """ Convert the key-value pairs in 'headers' to valid RFC822-style
      headers, including adding leading whitespace to elements which
      contain newlines in order to preserve continuation-line semantics.

      This code is taken from Products.CMFDefault.utils and modified
      for ERP5 purpose
  """
  munged = []
  linesplit = re.compile(r'[\n\r]+?')
  for key, value in headers:
    if value is not None:
      if type(value) in (list, tuple):
        vallines = map(str, value)
      else:
        vallines = linesplit.split(str(value))
      munged.append('%s: %s' % (key, '\r\n  '.join(vallines)))
  return '\r\n'.join(munged)
