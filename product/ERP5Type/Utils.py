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

# Required modules - some modules are imported later to prevent circular
deadlocks
import os
import re
import string
import time
from md5 import new as md5_new
from sha import new as sha_new

from Globals import package_home
from Globals import DevelopmentMode
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition import aq_self

from AccessControl.SecurityInfo import allow_class

from Products.CMFCore import utils
from Products.CMFCore.Expression import Expression
from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.Expressions import getEngine
from Products.PageTemplates.Expressions import SecureModuleImporter
from Products.ZCatalog.Lazy import LazyMap

from Products.ERP5Type import Permissions
from Products.ERP5Type import Constraint

from Products.ERP5Type.Cache import getReadOnlyTransactionCache
from zLOG import LOG, BLATHER, PROBLEM, WARNING

from AccessControl.SecurityManagement import newSecurityManager,
getSecurityManager

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
    _cached_convertToUpperCase[key] = ''.join([part.capitalize() for part in
key.split('_')])
    return _cached_convertToUpperCase[key]

UpperCase = convertToUpperCase

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

def pathToUid(list):
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

def int2letters(i):
  """
  Convert an integer to letters, to generate spreadsheet column id
  A, B, C ..., Z, AA, AB, ..., AZ, BA, ..., ZZ, AAA ...
  """
  if i < 26:
    return (chr(i + ord('A')))
  d, m = divmod(i, 26)
  return int2letter(d - 1) + int2letter(m)

#Get message id for translation
def getMessageIdWithContext(msg_id, context, context_id):
  return '%s [%s in %s]' % (msg_id,context,context_id)

#Get translation of msg id
def getTranslationStringWithContext(self, msg_id, context,      context_id):
   portal = self.getPortalObject()
   portal_workflow = portal.portal_workflow
   localizer = portal.Localizer
   selected_language = localizer.get_selected_language()
   msg_id_context = getMessageIdWithContext(msg_id,context, context_id)
   result = localizer.erp5_ui.gettext(
               msg_id_context,default='')   
   if result == '':
     result = localizer.erp5_ui.gettext(msg_id)
   return result.encode('utf8')
from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Utils').declarePublic(
'getMessageIdForWorkflowState','getTranslationStringWithContext',
'getMessageIdWithContext' )
#####################################################
# Globals initialization
#####################################################

from InitGenerator import InitializeDocument

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

    # Update PropertySheet Registry
    for module_id in ('PropertySheet', 'Interface', 'Constraint', ):
      path, module_id_list = getModuleIdList(product_path, module_id)
      if module_id == 'PropertySheet':
        import_method = importLocalPropertySheet
      elif module_id == 'Interface':
        import_method = importLocalInterface
      elif module_id == 'Constraint':
        import_method = importLocalConstraint
      for module_id in module_id_list:
        import_method(module_id, path=path)

    # Update Permissions
    if permissions_module is not None:
      for key in dir(permissions_module):
        # Do not consider private keys
        if key[0:2] != '__':
          setattr(Permissions, key, getattr(permissions_module, key))

  # Return core document_class list (for ERP5Type only)
  # this was introduced to permit overriding ERP5Type Document classes
  # which was not possible when they were define in the Document folder
  path, core_module_id_list = getModuleIdList(product_path, 'Core')
  for document in core_module_id_list:
    InitializeDocument(document, document_path=path)
  # Return document_class list
  path, module_id_list = getModuleIdList(product_path, 'Document')
  for document in module_id_list:
    InitializeDocument(document, document_path=path)
  return module_id_list + core_module_id_list

#####################################################
# Modules Import
#####################################################

import imp

# Zope 2.6.x does not have App.Config
try:
  from App.config import getConfiguration
except ImportError:
  getConfiguration = None
  pass

from Globals import InitializeClass
from Accessor.Base import func_code
from Products.CMFCore.utils import manage_addContentForm, manage_addContent
from AccessControl.PermissionRole import PermissionRole
from MethodObject import Method

class DocumentConstructor(Method):
    func_code = func_code()
    func_code.co_varnames = ('folder', 'id', 'REQUEST', 'kw')
    func_code.co_argcount = 2
    func_defaults = (None,)

    def __init__(self, klass):
      self.klass = klass

    def __call__(self, folder, id, REQUEST=None,
                 activate_kw=None, is_indexable=None, reindex_kw=None, **kw):
      o = self.klass(id)
      if activate_kw is not None:
        o.__of__(folder).setDefaultActivateParameters(**activate_kw)
      if reindex_kw is not None:
        o.__of__(folder).setDefaultReindexParameters(**reindex_kw)        
      if is_indexable is not None:
        o.isIndexable = is_indexable
      folder._setObject(id, o)
      o = folder._getOb(id)
      # if no activity tool, the object has already an uid
      if getattr(aq_base(o), 'uid', None) is None:
        o.uid = folder.portal_catalog.newUid()
      if kw: o._edit(force_update=1, **kw)
      if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )

class TempDocumentConstructor(DocumentConstructor):

    def __init__(self, klass):
      # Create a new class to set permissions specific to temporary objects.
      class TempDocument(klass):
        isTempDocument = 1
        pass

      # Replace some attributes.
      for name in ('isIndexable', 'reindexObject', 'recursiveReindexObject',
                   'activate', 'setUid', 'setTitle', 'getTitle', 'getUid'):
        setattr(TempDocument, name, getattr(klass, '_temp_%s' % name))

      # Make some methods public.
      for method_id in ('reindexObject', 'recursiveReindexObject',
                        'activate', 'setUid', 'setTitle', 'getTitle',
                        'edit', 'setProperty', 'getUid', 'setCriterion',
                        'setCriterionPropertyList'):
        setattr(TempDocument, '%s__roles__' % method_id, None)

      self.klass = TempDocument

    def __call__(self, folder, id, REQUEST=None, **kw):
      # CMF constructInstance is never used to build temp objects
      # so we never return the id.
      o = self.klass(id)
      if folder.isTempObject():
        folder._setObject(id, o)
      o = o.__of__(folder)
      if kw:
        o._edit(force_update=1, **kw)
      return o


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
    setattr(PropertySheet, class_id, getattr(module, class_id))
    # Register base categories
    registerBaseCategories(getattr(module, class_id))
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

def importLocalInterface(class_id, path = None):
  import Products.ERP5Type.Interface
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Interface")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  try:
    module = imp.load_source(class_id, path, f)
    setattr(Products.ERP5Type.Interface, class_id, getattr(module, class_id))
  finally:
    f.close()

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
  f = open(path, 'w')
  try:
    f.write(text)
  finally:
    f.close()

def setDefaultClassProperties(property_holder):
  """Initialize default properties for ERP5Type Documents.
  """
  if not property_holder.__dict__.has_key('isPortalContent'):
    property_holder.isPortalContent = 1
  if not property_holder.__dict__.has_key('isRADContent'):
    property_holder.isRADContent = 1
  if not property_holder.__dict__.has_key('add_permission'):
    property_holder.add_permission = Permissions.AddPortalContent
  if not property_holder.__dict__.has_key('__implements__'):
    property_holder.__implements__ = ()
  if not property_holder.__dict__.has_key('property_sheets'):
    property_holder.property_sheets = ()
  # Add default factory type information
  if not property_holder.__dict__.has_key('factory_type_information') and \
         property_holder.__dict__.has_key('meta_type') and \
         property_holder.__dict__.has_key('portal_type'):
    property_holder.factory_type_information = \
      {    'id'             : property_holder.portal_type
         , 'meta_type'      : property_holder.meta_type
         , 'description'    : getattr(property_holder, '__doc__',
                                "Type generated by ERPType")
         , 'icon'           : 'document_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'add%s' % property_holder.__name__
         , 'immediate_view' : '%s_view' % property_holder.__name__
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : '%s_view' % property_holder.__name__
          , 'permissions'   : ( Permissions.View, )
          },
        )
      }

def importLocalDocument(class_id, document_path = None):
  """Imports a document class and registers it in ERP5Type Document
  repository ( Products.ERP5Type.Document )
  """
  import Products.ERP5Type.Document
  import Permissions
  import Products
  if document_path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Document")
  else:
    path = document_path
  path = os.path.join(path, "%s.py" % class_id)
  
  # Import Document Class and Initialize it
  f = open(path)
  try:
    document_module = imp.load_source(
          'Products.ERP5Type.Document.%s' % class_id, path, f)
    document_class = getattr(document_module, class_id)
    document_constructor = DocumentConstructor(document_class)
    document_constructor_name = "add%s" % class_id
    document_constructor.__name__ = document_constructor_name
    setattr(Products.ERP5Type.Document, class_id, document_module)
    setattr(Products.ERP5Type.Document, document_constructor_name,
                                      document_constructor)
    setDefaultClassProperties(document_class)
    from AccessControl import ModuleSecurityInfo
    ModuleSecurityInfo('Products.ERP5Type.Document').declareProtected(
        Permissions.AddPortalContent, document_constructor_name,)
    InitializeClass(document_class)
  finally:
    f.close()

  # Temp documents are created as standard classes with a different constructor
  # which patches some methods are the instance level to prevent reindexing
  from Products.ERP5Type import product_path as erp5_product_path
  temp_document_constructor = TempDocumentConstructor(document_class)
  temp_document_constructor_name = "newTemp%s" % class_id
  temp_document_constructor.__name__ = temp_document_constructor_name
  setattr(Products.ERP5Type.Document,
          temp_document_constructor_name,
          temp_document_constructor)
  ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic(
                      temp_document_constructor_name,) # XXX Probably bad
security

  # Update Meta Types
  new_meta_types = []
  for meta_type in Products.meta_types:
    if meta_type['name'] != document_class.meta_type:
      new_meta_types.append(meta_type)
    else:
      # Update new_meta_types
      instance_class = None
      new_meta_types.append(
            { 'name': document_class.meta_type,
              'action': ('manage_addProduct/%s/%s' % (
                         'ERP5Type', document_constructor_name)),
              'product': 'ERP5Type',
              'permission': document_class.add_permission,
              'visibility': 'Global',
              'interfaces': document_class.__implements__,
              'instance': instance_class,
              'container_filter': None
              },)
  Products.meta_types = tuple(new_meta_types)
  # Update Constructors
  m = Products.ERP5Type._m
  if hasattr(document_class, 'factory_type_information'):
    constructors = ( manage_addContentForm
                   , manage_addContent
                   , document_constructor
                   , temp_document_constructor
                   , ('factory_type_information',
                        document_class.factory_type_information) )
  else:
    constructors = ( manage_addContentForm
                   , manage_addContent
                   , document_constructor
                   , temp_document_constructor )
  initial = constructors[0]
  m[initial.__name__]=manage_addContentForm
  default_permission = ('Manager',)
  pr=PermissionRole(document_class.add_permission, default_permission)
  m[initial.__name__+'__roles__']=pr
  for method in constructors[1:]:
    if isinstance(method, tuple):
      name, method = method
    else:
      name=os.path.split(method.__name__)[-1]
    if name != 'factory_type_information':
      # Add constructor to product dispatcher
      m[name]=method
    else:
      # Append fti to product dispatcher
      if not m.has_key(name): m[name] = []
      m[name].append(method)
    m[name+'__roles__']=pr

def initializeLocalRegistry(directory_name, import_local_method,
                            path_arg_name='path'):
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
          # XXX Arg are not consistent
          import_local_method(module_name, **{path_arg_name: document_path})
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
  initializeLocalRegistry("Document", importLocalDocument,
                          path_arg_name='document_path')

def initializeLocalPropertySheetRegistry():
  initializeLocalRegistry("PropertySheet", importLocalPropertySheet)

def initializeLocalConstraintRegistry():
  initializeLocalRegistry("Constraint", importLocalConstraint)

#####################################################
# Product initialization
#####################################################

def initializeProduct( context,
                       this_module,
                       global_hook,
                       document_module=None,
                       document_classes=None,
                       object_classes=None,
                       portal_tools=None,
                       content_constructors=None,
                       content_classes=None):
  """
    This function does all the initialization steps required
    for a Zope / CMF Product
  """
  if document_classes is None: document_classes = []
  if object_classes is None: object_classes = []
  if portal_tools is None: portal_tools = []
  if content_constructors is None: content_constructors = []
  if content_classes is None: content_classes = []
  product_name = this_module.__name__.split('.')[-1]

  # Define content constructors for Document content classes (RAD)
  initializeDefaultConstructors(content_classes)
  extra_content_constructors = []
  for content_class in content_classes:
    if hasattr(content_class, 'add' + content_class.__name__):
      extra_content_constructors += [
                getattr(content_class, 'add' + content_class.__name__)]
    if hasattr(content_class, 'newTemp' + content_class.__name__):
      extra_content_constructors += [
                getattr(content_class, 'newTemp' + content_class.__name__)]

  # Define FactoryTypeInformations for all content classes
  contentFactoryTypeInformations = []
  for content in content_classes:
    if hasattr(content, 'factory_type_information'):
      contentFactoryTypeInformations.append(content.factory_type_information)

  # Aggregate
  content_constructors = list(content_constructors) +
list(extra_content_constructors)

  # Begin the initialization steps
  bases = tuple(content_classes)
  tools = portal_tools
  z_bases = utils.initializeBasesPhase1( bases, this_module )
  z_tool_bases = utils.initializeBasesPhase1( tools, this_module )

  # Try to make some standard directories available
  try:
    registerDirectory('skins', global_hook)
  except:
    LOG("ERP5Type", BLATHER, "No skins directory for %s" % product_name)
  try:
    registerDirectory('help', global_hook)
  except:
    LOG("ERP5Type", BLATHER, "No help directory for %s" % product_name)

  # Finish the initialization
  utils.initializeBasesPhase2( z_bases, context )
  utils.initializeBasesPhase2( z_tool_bases, context )

  if len(tools) > 0:
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
  context.registerHelp(directory='Interface', clear=1)
  if help.lastRegistered != lastRegistered:
    help.lastRegistered = None
    context.registerHelp(directory='help', clear=1)
    help.lastRegistered = None
    context.registerHelp(directory='Interface', clear=0)

  context.registerHelpTitle('%s Help' % product_name)

  # Register Objets
  for c in object_classes:
    if hasattr(c, 'icon'):
      icon = getattr(c, 'icon')
    else:
      icon = None
    if hasattr(c, 'permission_type'):
      context.registerClass( c,
                           constructors = c.constructors,
                           permission = c.permission_type,
                           icon = icon)
    else:
      context.registerClass( c,
                           constructors = c.constructors,
                           icon = icon)

class ConstraintNotFound(Exception):
  pass

def createConstraintList(property_holder, constraint_definition):
  """
    This function creates constraint instances for a class
    and a property

    constraint_definition -- the constraint with all attributes
  """
  try:
    consistency_class = getattr(Constraint, constraint_definition['type'])
  except AttributeError:
    LOG("ERP5Type", PROBLEM, "Can not find Constraint: %s" % \
                       constraint_definition['type'])
    raise ConstraintNotFound(repr(constraint_definition))
  consistency_instance = consistency_class(**constraint_definition)
  property_holder.constraints += [consistency_instance]

#####################################################
# Constructor initialization
#####################################################

def initializeDefaultConstructors(klasses):
    for klass in klasses:
      if getattr(klass, 'isRADContent', 0) and hasattr(klass, 'security'):
        setDefaultConstructor(klass)
        klass.security.declareProtected(Permissions.AddPortalContent,
                                        'add' + klass.__name__)

def setDefaultConstructor(klass):
    """
      Create the default content creation method
    """
    document_constructor_name = 'add' + klass.__name__
    if not hasattr(klass, document_constructor_name):
      document_constructor = DocumentConstructor(klass)
      setattr(klass, document_constructor_name, document_constructor)
      document_constructor.__name__ = document_constructor_name

    temp_document_constructor_name = 'newTemp' + klass.__name__
    if not hasattr(klass, temp_document_constructor_name):
      temp_document_constructor = TempDocumentConstructor(klass)
      setattr(klass, temp_document_constructor_name, temp_document_constructor)
      temp_document_constructor.__name__ = temp_document_constructor_name
      klass.security.declarePublic(temp_document_constructor_name)


def createExpressionContext(object, portal=None):
  """
    Return a context used for evaluating a TALES expression.
  """
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
    pm = getToolByName(portal, 'portal_membership')
    if pm.isAnonymousUser():
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
      }
  return getEngine().getContext(data)

def getExistingBaseCategoryList(portal, base_cat_list):
  cache = getReadOnlyTransactionCache(portal)
  if cache is None:
    from Products.ERP5Type.TransactionalVariable import getTransactionalVariable
    cache = getTransactionalVariable(portal)
  category_tool = portal.portal_categories
  new_base_cat_list = []
  for base_cat in base_cat_list:
    key = (base_cat,)
    try:
      value = cache[key]
    except KeyError:
      value = category_tool._getOb(base_cat, None)
      if value is None:
        LOG('ERP5Type.Utils.getExistingBaseCategoryList', PROBLEM,
'base_category "%s" is missing, can not generate Accessors' % (base_cat))
      cache[key] = value
    if value is not None:
      new_base_cat_list.append(base_cat)
  return tuple(new_base_cat_list)

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
    legalTypes = type_definition.keys()
    # First build the property list from the property sheet
    # and the class properties
    prop_list = []
    # Do not consider superclass _properties definition
    for prop in property_holder.__dict__.get('_properties', []):
      # Copy the dict so that Expression objects are not overwritten.
      prop_list.append(prop.copy())
    cat_list = []
    cat_list += property_holder.__dict__.get('_categories',[]) # Do not consider
superclass _categories definition
    constraint_list = []  # a list of declarative consistency definitions (ie.
constraints)
    constraint_list += property_holder.__dict__.get('_constraints',[]) # Do not
consider superclass _constraints definition
    for base in property_holder.property_sheets:
      for prop in base._properties:
        # Copy the dict so that Expression objects are not overwritten.
        prop_list.append(prop.copy())
      if hasattr(base, '_categories'):
        if isinstance(base._categories, (tuple, list)):
          cat_list += base._categories
        else:
          cat_list += [base._categories]
      if hasattr(base, '_constraints'):
        constraint_list += base._constraints

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

    for const in constraint_list:
      for key,value in const.items():
        if isinstance(value, Expression):
          const[key] = value(econtext)

    # Store ERP5 properties on specific attributes
    property_holder._erp5_properties = tuple(prop_list)

    # Create default accessors for property sheets
    converted_prop_list = []
    converted_prop_keys = {}
    for prop in prop_list:
      read_permission = prop.get('read_permission',
                                 Permissions.AccessContentsInformation)
      if isinstance(read_permission, Expression):
        read_permission = read_permission(econtext)
      write_permission = prop.get('write_permission',
                                  Permissions.ModifyPortalContent)
      if isinstance(write_permission, Expression):
        write_permission = write_permission(econtext)
      if prop['type'] in legalTypes:
        if 'base_id' in prop:
          continue
        if not converted_prop_keys.has_key(prop['id']):
          if prop['type'] != 'content':
            converted_prop_list += [prop]
          converted_prop_keys[prop['id']] = 1

        # Create range accessors, if this has a range.
        if prop.get('range', 0):
          for value in ('min', 'max'):
            range_prop = prop.copy()
            del range_prop['range']
            if 'storage_id' in range_prop:
              del range_prop['storage_id']
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
                        write_permission=write_permission)

        # Create translation accesor, if translatable is set
        if prop.get('translatable', 0):
          # make accessors like getTranslatedProperty
          createTranslationAccessors(
                    property_holder,
                    'translated_%s' % (prop['id']),
                    read_permission=read_permission,
                    write_permission=write_permission)
          # make accessor to translation_domain
          # first create default one as a normal property
          txn_prop = {}
          txn_prop['description'] = ''
          txn_prop['default'] = ''
          txn_prop['id'] = 'translation_domain'
          txn_prop['type'] = 'string'
          txn_prop['mode'] = 'w'
          createDefaultAccessors(
                    property_holder,
                    '%s_%s' %(prop['id'], txn_prop['id']),
                    prop=txn_prop,
                    read_permission=read_permission,
                    write_permission=write_permission)
          # then overload accesors getPropertyTranslationDomain
          if prop.has_key('translation_domain'):
            default = prop['translation_domain']
          else:
            default = ''
          createTranslationAccessors(
                          property_holder,
                          '%s_translation_domain' % (prop['id']),
                          read_permission=read_permission,
                          write_permission=write_permission,
                          default=default)
        createDefaultAccessors(
                        property_holder,
                        prop['id'],
                        prop=prop,
                        read_permission=read_permission,
                        write_permission=write_permission)
      else:
        raise TypeError, '"%s" is illegal type for propertysheet' % \
                                            prop['type']
    # Create Category Accessors
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
      if cat == 'group':        prop['storage_id'] = 'group'
      elif cat == 'site':
        prop['storage_id'] = 'location'
      createDefaultAccessors(
                        property_holder,
                        prop['id'],
                        prop=prop,
                        read_permission=Permissions.AccessContentsInformation,
                        write_permission=Permissions.ModifyPortalContent)

      # Get read and write permission
      if portal is not None:
        cat_object = portal.portal_categories.get(cat, None)
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
    if object is not None and property_holder.__name__ == "Base":
                            # XXX use if possible is and real class
      base_category_list = []
      for cat in base_category_dict.keys():
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
        if portal is not None:
          cat_object = portal.portal_categories.get(cat, None)
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
        createRelatedValueAccessors(cat, read_permission=read_permission,
                                         write_permission=write_permission)
      # Unnecessary to create these accessors more than once.
      base_category_dict.clear()
    # Create the constraint method list - always check type
    property_holder.constraints = [
                  Constraint.PropertyTypeValidity(id='type_check',
                  description="Type Validity Check Error") ]

    for const in constraint_list:
      createConstraintList(property_holder, constraint_definition=const)
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
      if prop.has_key('acquisition_base_category')\
              and not prop.get('acquisition_copy_value'):
        # Set acquisition values as read only if no value is copied
        new_prop['mode'] = 'r'
      new_converted_prop_list += [new_prop]
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
    from Base import Base as BaseClass
    for prop in converted_prop_list:
      if prop['type'] in legalTypes:
        #if not hasattr(property_holder, prop['id']):
          # setattr(property_holder, prop['id'], None) # This makes sure no
acquisition will happen
          # but is wrong when we use storage_id .....
        storage_id = prop.get('storage_id', prop['id'])
        #if not hasattr(BaseClass, storage_id):
          # setattr(property_holder, storage_id, None) # This breaks things with
aq_dynamic
          #setattr(BaseClass, storage_id, None) # This blocks acquisition
        #else:
          #LOG('existing property',0,str(storage_id))
          #if prop.get('default') is not None:
          #  # setattr(property_holder, prop['id'], prop.get('default'))
          #  pass
          #else:
          #  # setattr(property_holder, prop['id'], defaults[prop['type']])
          #  pass
      else:
          raise TypeError, '"%s" is illegal type for propertysheet' % \
                                          prop['type']

##########################################
# Localizer is not always loaded prior to ERP5 products,
# thus, as Localizer is supposed to patch Global to add get_request to it,
# we prefer to redefine get_request inside ERP5Type/Utils,
# to avoid the case when Global wasn't patched and get_request is not available.
##########################################
try:
  import Products.iHotfix
  get_request = Products.iHotfix.get_request
except (ImportError, AttributeError):
  import Products.Localizer
  get_request = Products.Localizer.get_request

#####################################################
# Accessor initialization
#####################################################

from Base import Base as BaseClass
from Accessor import Base, List, Acquired, Content,\
                     AcquiredProperty, ContentProperty, \
                     Alias

def createDefaultAccessors(property_holder, id, prop = None,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent):
  """
    This function creates accessor and setter for a class
    and a property

    property_holder -- the class to add an accessor to

    id    -- the id of the property

    prop  -- the property definition of the property
  """
  ######################################################
  # Create Getters
  if prop.has_key('acquisition_base_category'):
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
                prop.get('acquisition_sync_value',0),
                prop.get('storage_id'),
                prop.get('alt_accessor_id'),
                prop.get('acquisition_object_id'),
                (prop['type'] in list_types or prop.get('multivalued', 0)),
                (prop['type'] == 'tales')
                )
    # Base Getter
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
    # Default Getter
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
    # List Getter
    if prop['type'] in list_types or prop.get('multivalued', 0):
      accessor_name = 'get' + UpperCase(id) + 'List'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter,
accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'List'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter,
accessor_args)
      # Set Getter
      accessor_name = 'get' + UpperCase(id) + 'Set'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.SetGetter,
accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Set'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.SetGetter,
accessor_args)
    if prop['type'] == 'content':
      #LOG('Value Object Accessor', 0, prop['id'])
      # Base Getter
      accessor_name = 'get' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
      # Default Getter
      accessor_name = 'getDefault' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id,
Acquired.DefaultGetter, accessor_args)
      # List Getter
      accessor_name = 'get' + UpperCase(id) + 'ValueList'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter,
accessor_args)
        property_holder.declareProtected( read_permission, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
      if not hasattr(property_holder, accessor_name) or prop.get('override',0):
        property_holder.registerAccessor(accessor_name, id, Acquired.ListGetter,
accessor_args)
      # AcquiredProperty Getters
      if prop.has_key('acquired_property_id'):
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
                prop.get('acquisition_sync_value',0),
                prop.get('storage_id'),
                prop.get('alt_accessor_id'),
                prop.get('acquisition_object_id'),
                (prop['type'] in list_types or prop.get('multivalued', 0)),
                (prop['type'] == 'tales')
                )
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.Getter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = '_baseGet' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.Getter, accessor_args)
          # Default Getter
          accessor_name = 'getDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.DefaultGetter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = '_baseGetDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.DefaultGetter, accessor_args)
          # List Getter
          ################# NOT YET
          # Setter
          accessor_name = 'set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, '_' + accessor_name,
Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.Setter, accessor_args)
          accessor_name = '_baseSet' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.Setter, accessor_args)
          # Default Setter
          accessor_name = 'setDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, '_' + accessor_name,
Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_setDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.DefaultSetter, accessor_args)
          accessor_name = '_baseSetDefault' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
AcquiredProperty.DefaultSetter, accessor_args)
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
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.Getter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.Getter,
accessor_args)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.DefaultGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.DefaultGetter,
accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.ListGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.ListGetter,
accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.SetGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, List.SetGetter,
accessor_args)
  elif prop['type'] == 'content':
    accessor_args = (prop['type'], prop.get('portal_type'),
prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.Getter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.Getter,
accessor_args)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.DefaultGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.DefaultGetter,
accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.ListGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.ListGetter,
accessor_args)
    # Create value getters for a list property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.ValueGetter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Content.ValueGetter,
accessor_args)
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Content.DefaultValueGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Content.DefaultValueGetter, accessor_args)
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Content.ValueListGetter, accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id,
Content.ValueListGetter, accessor_args)
    if prop.has_key('acquired_property_id'):
      for aq_id in prop['acquired_property_id']:
        for composed_id in ("%s_%s" % (id, aq_id), "default_%s_%s" % (id,
aq_id)) :
          accessor_name = 'get' + UpperCase(composed_id)
          accessor_args = (prop['type'], aq_id, prop.get('portal_type'),
prop.get('storage_id'))
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
ContentProperty.Getter, accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          accessor_name = 'get' + UpperCase(composed_id) + 'List'
          list_accessor_args = (prop['type'], aq_id + '_list',
prop.get('portal_type'), prop.get('storage_id'))
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id +
'_list', 
                                             ContentProperty.Getter,
list_accessor_args)
            property_holder.declareProtected( read_permission, accessor_name )
          # No default getter YET XXXXXXXXXXXXXX
          # No list getter YET XXXXXXXXXXXXXX
          accessor_name = '_set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id,
ContentProperty.Setter, accessor_args)
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = '_set' + UpperCase(composed_id) + 'List'
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, composed_id +
'_list', 
                                             ContentProperty.Setter,
list_accessor_args)
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = 'set' + UpperCase(composed_id)
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, '_' + accessor_name,
Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          accessor_name = 'set' + UpperCase(composed_id) + 'List'
          if not hasattr(property_holder, accessor_name) or
prop.get('override',0):
            property_holder.registerAccessor(accessor_name, '_' + accessor_name,
Alias.Reindex, ())
            property_holder.declareProtected( write_permission, accessor_name )
          # No default getter YET XXXXXXXXXXXXXX
          # No list getter YET XXXXXXXXXXXXXX
  else:
    accessor_args = (prop['type'], prop.get('default'), prop.get('storage_id'))
    # Create getters for a simple property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Base.Getter,
accessor_args)
      property_holder.declareProtected( read_permission, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name) or prop.get('override',0):
      property_holder.registerAccessor(accessor_name, id, Base.Getter,
accessor_args)
  ######################################################
  # Create Setters
  if prop['type'] in list_types or prop.get('multivalued', 0):
    # Create setters for a list property by aliasing
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    accessor_args = (prop['type'], prop.get('storage_id'), 0)
    # Create setters for a list property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.Setter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.Setter,
accessor_args)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.DefaultSetter,
accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.DefaultSetter,
accessor_args)
    setter_name = '_set' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.ListSetter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'List'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.ListSetter,
accessor_args)
    setter_name = '_set' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.SetSetter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'Set'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, List.SetSetter,
accessor_args)
  elif prop['type'] == 'content':
    # Create setters for an object property
    # Create setters for a list property (reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    base_setter_name = 'set' + UpperCase(id)
    # The default setter sets the first item of a list without changing other
items
    default_setter_name = 'setDefault' + UpperCase(id)
    # Create setters for an object property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + base_setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + default_setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + base_setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = 'setDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + default_setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    accessor_args = (prop['type'], prop.get('storage_id'), 0)
    # Create setters for an object property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter,
accessor_args)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter,
accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter,
accessor_args)
    setter_name = '_set' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.Setter,
accessor_args)
    setter_name = '_setDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter,
accessor_args)
    setter_name = '_baseSetDefault' + UpperCase(id) + 'Value'
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Content.DefaultSetter,
accessor_args)
  else:
    accessor_args = (prop['type'], prop.get('storage_id'), 0)
    # Create setters for a simple property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
      property_holder.declareProtected(write_permission, setter_name)
    setter_name = '_set' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Base.Setter,
accessor_args)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(property_holder, setter_name):
      property_holder.registerAccessor(setter_name, id, Base.Setter,
accessor_args)
  ######################################################
  # Create testers
  if prop['type'] == 'content':
    # XXX This approach is wrong because testers for all properties
    # should be created upfront rather than on demand
    tester_name = 'has' + UpperCase(id)
    tester = Content.Tester(tester_name, id, prop['type'],
                                                  storage_id =
prop.get('storage_id'))
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(read_permission, tester_name)
    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))
  else:
    tester_name = 'has' + UpperCase(id)
    tester = Base.Tester(tester_name, id, prop['type'],
                                                  storage_id =
prop.get('storage_id'))
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(read_permission, tester_name)
    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))

    # List Tester
    tester_name = 'has' + UpperCase(id) + 'List'
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))
      BaseClass.security.declareProtected(read_permission, tester_name)
    tester_name = '_baseHas' + UpperCase(id) + 'List'
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))
    tester_name = 'hasDefault' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))
      BaseClass.security.declareProtected(read_permission, tester_name)
    tester_name = '_baseHasDefault' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester.dummy_copy(tester_name))

    # First Implementation of Boolean Accessor
    tester_name = 'is' + UpperCase(id)
    if not hasattr(property_holder, tester_name):
      property_holder.registerAccessor(tester_name, id, Base.Getter,
                     (prop['type'], prop.get('default'),
prop.get('storage_id')))
      property_holder.declareProtected(read_permission, tester_name)
    tester_name = '_baseIs' + UpperCase(id)
    if not hasattr(property_holder, tester_name):
      property_holder.registerAccessor(tester_name, id, Base.Getter,
                     (prop['type'], prop.get('default'),
prop.get('storage_id')))

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
    property_holder.registerAccessor(accessor_name, id, Category.ItemListGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)

  accessor_name = 'getDefault' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter,
())

  accessor_name = 'get' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.DefaultGetter,
())

  accessor_name = 'has' + UpperCase(id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Category.Tester, ())
    property_holder.declareProtected(read_permission, accessor_name)

  setter_name = 'set' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  accessor_args = (0,)
  setter_name = '_set' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.Setter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.Setter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.ListSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'List'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.ListSetter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.SetSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Set'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.SetSetter,
accessor_args)

  setter_name = '_setDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.DefaultSetter,
accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id)
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Category.DefaultSetter,
accessor_args)


from Accessor import Value, Related, RelatedValue, Translation

def createValueAccessors(property_holder, id,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent):
  """
    Creates relation accessors for category id

     TODO: Security declarations must be checked

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
    property_holder.registerAccessor(accessor_name, id, Value.TitleListGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleListGetter,
())

  accessor_name = 'get' + UpperCase(id) + 'TitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleSetGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.TitleSetGetter,
())

  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.TranslatedTitleListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitleList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.TranslatedTitleListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.TranslatedTitleSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitleSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.TranslatedTitleSetGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'ReferenceList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.ReferenceListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ReferenceList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.ReferenceListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'ReferenceSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.ReferenceSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ReferenceSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.ReferenceSetGetter, ())

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
    property_holder.registerAccessor(accessor_name, id,
Value.LogicalPathListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPathList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.LogicalPathListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'LogicalPathSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.LogicalPathSetGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPathSet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.LogicalPathSetGetter, ())

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
    property_holder.registerAccessor(accessor_name, id,
Value.PropertyListGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertyList'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.PropertyListGetter, ())

  accessor_name = 'get' + UpperCase(id) + 'PropertySet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertySetGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertySet'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.PropertySetGetter,
())

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
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Title'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'TranslatedTitle'
  accessor = Value.DefaultTranslatedTitleGetter(accessor_name, id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTranslatedTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTranslatedTitleGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTranslatedTitleGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'TranslatedTitle'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTranslatedTitleGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Reference'
  accessor = Value.DefaultReferenceGetter(accessor_name, id)
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultReferenceGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultReferenceGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultReferenceGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Reference'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultReferenceGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter,
())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultUidGetter,
())

  accessor_name = 'getDefault' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter,
())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter,
())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Id'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id, Value.DefaultIdGetter,
())

  accessor_name = 'getDefault' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleOrIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleOrIdGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleOrIdGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleOrId'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultTitleOrIdGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultPropertyGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultPropertyGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultPropertyGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'Property'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultPropertyGetter, ())

  accessor_name = 'getDefault' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultLogicalPathGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultLogicalPathGetter, ())
    property_holder.declareProtected(read_permission, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultLogicalPathGetter, ())
  accessor_name = '_categoryGet' + UpperCase(id) + 'LogicalPath'
  if not hasattr(property_holder, accessor_name):
    property_holder.registerAccessor(accessor_name, id,
Value.DefaultLogicalPathGetter, ())

  setter_name = 'set' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  accessor_args = (0,)
  setter_name = '_set' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.Setter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.Setter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.ListSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.ListSetter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.SetSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.SetSetter,
accessor_args)

  setter_name = '_setDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.DefaultSetter,
accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id) + 'Value'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.DefaultSetter,
accessor_args)

  # Uid setters
  setter_name = 'set' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'setDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, '_' + setter_name,
Alias.Reindex, ())
    property_holder.declareProtected(write_permission, setter_name)

  setter_name = '_set' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetter,
accessor_args)

  setter_name = '_setDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidDefaultSetter,
accessor_args)
  setter_name = '_categorySetDefault' + UpperCase(id) + 'Uid'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidDefaultSetter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidListSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'UidList'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidListSetter,
accessor_args)

  setter_name = '_set' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetSetter,
accessor_args)
  setter_name = '_categorySet' + UpperCase(id) + 'UidSet'
  if not hasattr(property_holder, setter_name):
    property_holder.registerAccessor(setter_name, id, Value.UidSetSetter,
accessor_args)


def createRelatedValueAccessors(id,
read_permission=Permissions.AccessContentsInformation,
                                   
write_permission=Permissions.ModifyPortalContent):

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

  permission = read_permission
  for accessor_class, accessor_name_list in accessor_dict.items():

    # First element is the original accessor
    accessor_name = accessor_name_list[0]
    accessor = accessor_class(accessor_name, id)
    if not hasattr(BaseClass, accessor_name):
      setattr(BaseClass, accessor_name, accessor)
      # Declare the security of method which doesn't start with _
      if accessor_name[0] != '_':
        BaseClass.security.declareProtected(permission, accessor_name)

    # Others are dummy copies
    for accessor_name in accessor_name_list[1:]:
      if not hasattr(BaseClass, accessor_name):
        setattr(BaseClass, accessor_name, 
                accessor.dummy_copy(accessor_name))
        # Declare the security of method which doesn't start with _
        if accessor_name[0] != '_':
          BaseClass.security.declareProtected(permission, accessor_name)

def createTranslationAccessors(property_holder, id,
    read_permission=Permissions.AccessContentsInformation,
    write_permission=Permissions.ModifyPortalContent, default=''):
  """
  Generate the translation accessor for a class and a property
  """
  if 'translated' in id:
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(property_holder, accessor_name):
      property_holder.registerAccessor(accessor_name, id,
Translation.TranslatedPropertyGetter, ())
      property_holder.declareProtected(read_permission, accessor_name)
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(property_holder, accessor_name):
      property_holder.registerAccessor(accessor_name, id,
Translation.TranslatedPropertyGetter, ())

  if 'translation_domain' in id:
    # Getter
    accessor_name = 'get' + UpperCase(id)
    property_holder.registerAccessor(accessor_name, id,
        Translation.PropertyTranslationDomainGetter, ('string', default,))
    property_holder.declareProtected(read_permission, accessor_name)


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
