##############################################################################
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
import os, re, string, sys
from Globals import package_home
from ZPublisher.HTTPRequest import FileUpload
from Acquisition import aq_base, aq_inner, aq_parent, aq_self

from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.ERP5Type import Permissions
from Products.ERP5Type import Constraint
from Products.ERP5Type import Interface
from Products.ERP5Type import PropertySheet

from zLOG import LOG

#####################################################
# Global Switches
#####################################################

INITIALIZE_PRODUCT_RAD = 1 # If set to 0, product documents are not initialized
                           # this will divide by two memory usage taken by getters and setters
                           # 0 value is suggested for new ERP5 projetcs

#####################################################
# Compatibility - XXX - BAD
#####################################################

from Accessor.TypeDefinition import *


#####################################################
# Generic sort method
#####################################################

def sortOnId(sort_id):
  return lambda a,b: cmp(a[1].getProperty(sort_id), b[1].getProperty(sort_id))

#####################################################
# Useful methods
#####################################################

def convertToUpperCase(key):
  """
    This function turns an attribute name into
    a method name according to the ERP5 naming conventions
  """
  result = ''
  parts = string.split(str(key),'_')
  for part in parts:
    letter_list = list(part)
    letter_list[0] = string.upper(letter_list[0])
    result = result + string.join(letter_list,'')
  return result

UpperCase = convertToUpperCase

# Some set operations
def cartesianProduct(list_of_list):
  if len(list_of_list) == 0:
    return [[]]
  result = []
  head = list_of_list[0]
  tail = list_of_list[1:]
  product = cartesianProduct(tail)
  for v in head:
    for p in product:
      result += [[v] + p]
  return result

# Some list operations
def keepIn(value_list, filter_list):
  result = []
  for k in value_list:
    if k in filter_list:
      result += [k]
  return result

def rejectIn(value_list, filter_list):
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
def getPath(o):
    """
    Returns the absolute path of an object
    """
    return string.join(o.getPhysicalPath(),'/')

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
      LOG('ERP5Type:',0,'No PropertySheet directory in %s' % product_path)
  return path, module_name_list

# EPR5Type global modules update
def updateGlobals( this_module, global_hook, permissions_module = None, is_erp5_type=0):
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
      print path
      print module_id_list
      if module_id == 'PropertySheet':
        import_method = importLocalPropertySheet
      elif module_id == 'Interface':
        import_method = importLocalInterface
      elif module_id == 'Constraint':
        import_method = importLocalConstraint
      else:
        import_method = None
      for module_id in module_id_list:
        import_method(module_id, path=path)
  
    # Update Permissions
    if permissions_module is not None:
      for key in dir(permissions_module):
        # Do not consider private keys
        if key[0:2] != '__':
          setattr(Permissions, key, getattr(permissions_module, key))

  # Return document_class list
  path, module_id_list = getModuleIdList(product_path, 'Document')
  for document in module_id_list:
    InitializeDocument(document, document_path=path)
  return module_id_list
        
#####################################################
# Modules Import
#####################################################

import imp, os, re

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

    def __call__(self, folder, id, REQUEST=None, **kw):
      o = self.klass(id)
      folder._setObject(id, o)
      if kw is not None: o.__of__(folder)._edit(force_update=1, **kw)
      if REQUEST is not None:
          REQUEST['RESPONSE'].redirect( 'manage_main' )

python_file_parser = re.compile('^(.*)\.py$')

def getLocalPropertySheetList():
  if not getConfiguration: return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()      
  return result

def readLocalPropertySheet(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  text = f.read()
  f.close()
  return text

def writeLocalPropertySheet(class_id, text):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "PropertySheet")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path, 'w')
  f.write(text)

def importLocalPropertySheet(class_id, path = None):
  import Products.ERP5Type.PropertySheet
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "PropertySheet")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  module = imp.load_source(class_id, path, f)
  setattr(Products.ERP5Type.PropertySheet, class_id, getattr(module, class_id))

def importLocalInterface(class_id, path = None):
  import Products.ERP5Type.Interface
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Interface")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  module = imp.load_source(class_id, path, f)
  setattr(Products.ERP5Type.Interface, class_id, getattr(module, class_id))

def importLocalConstraint(class_id, path = None):
  import Products.ERP5Type.Interface
  if path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Constraint")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  module = imp.load_source(class_id, path, f)
  setattr(Products.ERP5Type.Constraint, class_id, getattr(module, class_id))

def getLocalExtensionList():
  if not getConfiguration: return []
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  file_list = os.listdir(path)
  result = []
  for fname in file_list:
    if python_file_parser.match(fname) is not None:
      result.append(python_file_parser.match(fname).groups()[0])
  result.sort()      
  return result

def readLocalExtension(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  text = f.read()
  f.close()
  return text

def writeLocalExtension(class_id, text):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Extensions")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path, 'w')
  f.write(text)

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

def readLocalDocument(class_id):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  text = f.read()
  f.close()
  return text

def writeLocalDocument(class_id, text):
  instance_home = getConfiguration().instancehome
  path = os.path.join(instance_home, "Document")
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path, 'w')
  f.write(text)

def setDefaultClassProperties(document_class):
  if not document_class.__dict__.has_key('isPortalContent'):
    document_class.isPortalContent = 1
  if not document_class.__dict__.has_key('isRADContent'):
    document_class.isRADContent = 1
  if not document_class.__dict__.has_key('add_permission'):
    document_class.add_permission = Permissions.AddPortalContent
  if not document_class.__dict__.has_key('__implements__'):
    document_class.__implements__ = ()
  if not document_class.__dict__.has_key('property_sheets'):
    document_class.property_sheets = ()
  # Add default factory type information
  if not document_class.__dict__.has_key('factory_type_information') and \
         document_class.__dict__.has_key('meta_type') and document_class.__dict__.has_key('portal_type'):
    document_class.factory_type_information = \
      {    'id'             : document_class.portal_type
         , 'meta_type'      : document_class.meta_type
         , 'description'    : getattr(document_class, '__doc__', "Type generated by ERPType")
         , 'icon'           : 'document.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'add%s' % document_class.__name__
         , 'immediate_view' : '%s_view' % document_class.__name__
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : '%s_view' % document_class.__name__
          , 'permissions'   : ( Permissions.View, )
          }
        , { 'id'            : 'print'
          , 'name'          : 'Print'
          , 'category'      : 'object_print'
          , 'action'        : '%s_print' % document_class.__name__
          , 'permissions'   : (
              Permissions.View, )
          }
        , { 'id'            : 'metadata'
          , 'name'          : 'Metadata'
          , 'category'      : 'object_view'
          , 'action'        : 'metadata_view'
          , 'permissions'   : (
              Permissions.View, )
          }
        )
      }
    
def importLocalDocument(class_id, document_path = None):
  """
    Imports a document class and registers it as
  """

  #__import__('Document.Test')
  import Products.ERP5Type.Document
  import Permissions
  import Products
  if document_path is None:
    instance_home = getConfiguration().instancehome
    path = os.path.join(instance_home, "Document")
  else:
    path = document_path
  path = os.path.join(path, "%s.py" % class_id)
  f = open(path)
  document_module = imp.load_source('Products.ERP5Type.Document.%s' % class_id, path, f) # This is the right way
  document_class = getattr(document_module, class_id)
  document_constructor = DocumentConstructor(document_class)
  document_constructor_name = "add%s" % class_id
  document_constructor.__name__ = document_constructor_name
  default_permission = ('Manager',)  
  setattr(Products.ERP5Type.Document, class_id, document_module)
  setattr(Products.ERP5Type.Document, document_constructor_name, document_constructor)
  setDefaultClassProperties(document_class)
  pr=PermissionRole(document_class.add_permission, default_permission)
  document_constructor.__roles__ = pr # There used to be security breach which was fixed (None replaced by pr)
  InitializeClass(document_class)
  # Update Meta Types
  new_meta_types = []
  for meta_type in Products.meta_types:
    if meta_type['name'] != class_id:
      new_meta_types.append(meta_type)
    else:
      # Update new_meta_types
      instance_class = None
      new_meta_types.append(
            { 'name': document_class.meta_type,
              'action': ('manage_addProduct/%s/%s' % ('ERP5Type', document_constructor_name)),
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
  constructors = ( manage_addContentForm
                 , manage_addContent
                 , document_constructor )
  initial = constructors[0]
  m[initial.__name__]=manage_addContentForm
  m[initial.__name__+'__roles__']=pr
  for method in constructors[1:]:
    name=os.path.split(method.__name__)[-1]
    m[name]=method
    m[name+'__roles__']=pr


#     ( manage_addContentForm
#                                , manage_addContent
#                                , self
#                                , ('factory_type_information', self.fti)
#                                ) + self.extra_constructors
  # except IOError,


def initializeLocalDocumentRegistry():
  if not getConfiguration: return
  instance_home = getConfiguration().instancehome
  document_path = os.path.join(instance_home, "Document")
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
          importLocalDocument(module_name, document_path = document_path)
          LOG('Added local document to ERP5Type repository: %s (%s)' % (module_name, document_path),0,'')
          print 'Added local document to ERP5Type repository: %s (%s)' % (module_name, document_path)
        except:
          LOG('Failed to add local document to ERP5Type repository: %s (%s)' % (module_name, document_path),0,'')
          print 'Failed to add local document to ERP5Type repository: %s (%s)' % (module_name, document_path)

#####################################################
# Product initialization
#####################################################

def initializeProduct( context, this_module, global_hook,
                           document_module = None,
                           document_classes=None, object_classes=None, portal_tools=None,
                           content_constructors=None, content_classes=None):
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

  # Define content classes from document_classes
  #LOG('Begin initializeProduct %s %s' % (document_module, document_classes),0,'')
  extra_content_classes = []
  #if document_module is not None:
  if 0:
    for module_name in document_classes:
      #LOG('Inspecting %s %s' % (document_module, module_name),0,'')
      candidate = getattr(document_module, module_name)
      candidate = getattr(candidate, module_name)
      #LOG('Found %s' % candidate,0,'')
      if hasattr(candidate, 'isPortalContent'):
        if candidate.isPortalContent == 1:
          extra_content_classes += [candidate]

  # Initialize Default Properties and Constructors for RAD classes
  if INITIALIZE_PRODUCT_RAD:
    #initializeDefaultProperties(content_classes)
    #initializeDefaultProperties(extra_content_classes)
    initializeDefaultProperties(object_classes)
    #initializeDefaultConstructors(content_classes) Does not work yet
    

  # Define content constructors for Document content classes (RAD)
  extra_content_constructors = []
  for content_class in extra_content_classes:
    if hasattr(content_class, 'add' + content_class.__name__):
      extra_content_constructors += [getattr(content_class, 'add' + content_class.__name__)]
    else:
      extra_content_constructors += [getattr(document_module, 'add' + content_class.__name__)]

  # Define FactoryTypeInformations for all content classes
  contentFactoryTypeInformations = []
  for content in content_classes:
    if hasattr(content, 'factory_type_information'):
      contentFactoryTypeInformations.append(content.factory_type_information)
  for content in extra_content_classes:
    if hasattr(content, 'factory_type_information'):
      contentFactoryTypeInformations.append(content.factory_type_information)

  # Aggregate
  content_classes = list(content_classes) + list(extra_content_classes)
  content_constructors = list(content_constructors) + list(extra_content_constructors)

  # Begin the initialization steps
  bases = tuple(content_classes)
  tools = portal_tools
  z_bases = utils.initializeBasesPhase1( bases, this_module )
  z_tool_bases = utils.initializeBasesPhase1( tools, this_module )

  # Try to make some standard directories available
  try:
    registerDirectory('skins', global_hook)
  except:
    LOG("ERP5Type:",0,"No skins directory for %s" % product_name)
  try:
    registerDirectory('help', global_hook)
  except:
    LOG("ERP5Type:",0,"No help directory for %s" % product_name)

  # Finish the initialization
  utils.initializeBasesPhase2( z_bases, context )
  utils.initializeBasesPhase2( z_tool_bases, context )

  if len(tools) > 0:
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

    utils.ContentInit(    klass.meta_type
                        , content_types=[klass]
                        , permission=klass_permission
                        , extra_constructors=tuple(content_constructors)
                        , fti=contentFactoryTypeInformations
                        ).initialize( context )

  # Register Help
  context.registerHelp(directory='help')
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

def createConstraintList(klass, constraint_definition):
  """
    This function creates constraint instances for a class
    and a property

    constraint_definition -- the constraint with all attributes
  """
  consistency_class = getattr(Constraint, constraint_definition['type'])
  consistency_instance = consistency_class(**constraint_definition)
  klass.constraints += [consistency_instance]

#####################################################
# Constructor initialization
#####################################################

def initializeDefaultConstructors(klasses):
    for klass in klasses:
      if getattr(klass, 'isRADContent', 0) and hasattr(klass, 'security'):
        setDefaultConstructor(klass)
        klass.security.declareProtected(Permissions.AddPortalContent, 'add' + klass.__name__)

def setDefaultConstructor(klass):
    """
      Create the default content creation method
    """
    if not hasattr(klass, 'add' + klass.__name__):
      setattr(klass, 'add' + klass.__name__, Constructor(klass))

# Creation of default property accessors and values
def initializeDefaultProperties(klasses):
    """
    Creates class attributes with a default value.
    """
    for klass in klasses:
      if getattr(klass, 'isRADContent', 0):
        setDefaultClassProperties(klass)
        setDefaultProperties(klass)

def setDefaultProperties(klass):
    """
      This methods sets default accessors for this object as well
      as consistency checkers, based on the definition
      stored in PropertySheet objects.

      Accessors include

      - attribute accessors (ie. a string, float value stored by the object)

      - category accessors (ie. a membership of an object to a category)

      - relation accessors (ie. a kind of membership where the category instance is content)

      - programmable acquisition acessors (ie. attribute accessors which are based on relations)

      Consistency checkers are intended to check the content consistency (ex. ariry of a relation)
      as well as fix content consistency through a default consistency fixing method.

    Set default attributes in current object for all properties in '_properties'
    """
    legalTypes = type_definition.keys()
    # First build the property list from the property sheet
    # and the class properties
    prop_list = []
    prop_list += klass.__dict__.get('_properties',[]) # Do not consider superclass _properties definition
    cat_list = []
    constraint_list = []  # a list of declarative consistency definitions (ie. constraints)
    for base in klass.property_sheets:
        prop_list += base._properties
        if hasattr(base, '_categories'):
          cat_list += base._categories
        if hasattr(base, '_constraints'):
          constraint_list += base._constraints
    # Create default accessors for property sheets
    converted_prop_list = []
    converted_prop_keys = {}
    for prop in prop_list:
      if prop['type'] in legalTypes:
        if not converted_prop_keys.has_key(prop['id']):
          if prop['type'] != 'content': converted_prop_list += [prop]
          converted_prop_keys[prop['id']] = 1
        createDefaultAccessors(klass, prop['id'], prop=prop)
      else:
        raise TypeError, '"%s" is illegal type for propertysheet' % \
                                            prop['type']
    # Create Category Accessors
    for cat in cat_list:
      createCategoryAccessors(klass, cat)
      createValueAccessors(klass, cat)
    # Create the constraint method list - always check type
    klass.constraints = [Constraint.PropertyTypeValidity(id='type_check')]
    for const in constraint_list:
      createConstraintList(klass, constraint_definition=const)
    # ERP5 _properties and Zope _properties are somehow different
    # The id is converted to the Zope standard - we keep the original id as base_id
    new_converted_prop_list = []
    for prop in converted_prop_list:
      new_prop = prop.copy()
      if prop['type'] in list_types or prop.get('multivalued', 0):
        # Display as list
        new_prop['base_id'] = prop['id']
        new_prop['id'] = prop['id'] + '_list'
      if prop.has_key('acquisition_base_category') and not prop.get('acquisition_copy_value'):
        # Set acquisition values as read only if no value is copied
        new_prop['mode'] = 'r'
      new_converted_prop_list += [new_prop]
    # Set the properties of the class
    klass._properties = tuple(new_converted_prop_list)
    klass._categories = tuple(cat_list)
    klass._constraints = tuple(constraint_list)
    # And the default values - default values are needed
    # for historical reasons : many objects have a default
    # value defines at the class level. The use of None
    # allows to create the equivalent of NULL values
    # - new - XXX
    # We remove such properties here
    for prop in converted_prop_list:
      if prop['type'] in legalTypes:
        #if not hasattr(klass, prop['id']):
          # setattr(klass, prop['id'], None) # This makes sure no acquisition will happen
          # but is wrong when we use storage_id .....
        storage_id = prop.get('storage_id', prop['id'])
        if not hasattr(klass, storage_id):
          setattr(klass, storage_id, None)
        #else:
          #LOG('existing property',0,str(storage_id))
          #if prop.get('default') is not None:
          #  # setattr(klass, prop['id'], prop.get('default'))
          #  pass
          #else:
          #  # setattr(klass, prop['id'], defaults[prop['type']])
          #  pass
      else:
          raise TypeError, '"%s" is illegal type for propertysheet' % \
                                          prop['type']

#####################################################
# Accessor initialization
#####################################################

from Base import Base as BaseClass
from Accessor import Base, List, Object, Acquired, Content, AcquiredProperty, ContentProperty
import types

# Compile accessors
for accessor in [Base, List, Object, Acquired, Content]:
  for a_class in accessor.__dict__.items():
    if type(a_class) is types.ClassType:
      if hasattr(a_class, '__call__'):
        bind(getattr(a_class, '__call__'))

def createDefaultAccessors(klass, id, prop = None):
  """
    This function creates accessor and setter for a class
    and a property

    klass -- the class to add an accessor to

    id    -- the id of the property

    prop  -- the property definition of the property
  """
  ######################################################
  # Create Getters
  if prop.has_key('acquisition_base_category'):
    # Create getters for an acquired property
    # The base accessor returns the first item in a list
    # and simulates a simple property
    # XXXX Missing Boolean accessor
    accessor_name = 'get' + UpperCase(id)
    base_accessor = Acquired.DefaultGetter(accessor_name,
                id,
                prop['type'],
                prop.get('default'),
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('acquisition_sync_value',0),
                storage_id = prop.get('storage_id'),
                alt_accessor_id = prop.get('alt_accessor_id'),
                is_list_type =  (prop['type'] in list_types or prop.get('multivalued', 0))
                )
    # The default accessor returns the first item in a list
    default_accessor = base_accessor
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'List'
    list_accessor = Acquired.ListGetter(accessor_name,
                id,
                prop['type'],
                prop.get('default'),
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('acquisition_sync_value',0),
                storage_id = prop.get('storage_id'),
                alt_accessor_id = prop.get('alt_accessor_id'),
                is_list_type =  (prop['type'] in list_types or prop.get('multivalued', 0))
                )
    # Base Getter
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    # Default Getter
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    # List Getter
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
    if prop['type'] == 'content':
      #LOG('Value Object Accessor', 0, prop['id'])
      # Base Getter
      accessor_name = 'get' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, base_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, base_accessor)
      # Default Getter
      accessor_name = 'getDefault' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, default_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, default_accessor)
      # List Getter
      accessor_name = 'get' + UpperCase(id) + 'ValueList'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, list_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, list_accessor)
      # AcquiredProperty Getters
      if prop.has_key('acquired_property_id'):
        for aq_id in prop['acquired_property_id']:
          composed_id = "%s_%s" % (id, aq_id)
          # print "Set composed_id accessor %s" % composed_id
          accessor_name = 'get' + UpperCase(composed_id)
          # print "Set accessor_name accessor %s" % accessor_name
          base_accessor = AcquiredProperty.Getter(accessor_name,
                composed_id,
                prop['type'],
                prop['portal_type'],
                aq_id,
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('acquisition_sync_value',0),
                storage_id = prop.get('storage_id'),
                alt_accessor_id = prop.get('alt_accessor_id'),
                is_list_type =  (prop['type'] in list_types or prop.get('multivalued', 0))
                )
          if not hasattr(klass, accessor_name) or prop.get('override',0):
            setattr(klass, accessor_name, base_accessor)
            klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
          accessor_name = '_baseGet' + UpperCase(id)
          if not hasattr(klass, accessor_name) or prop.get('override',0):
            setattr(klass, accessor_name, base_accessor)
          # Default Getter
          ################# NOT YET 
          # List Getter
          ################# NOT YET 
          accessor_name = 'set' + UpperCase(composed_id)
          base_accessor = AcquiredProperty.Setter(accessor_name,
                composed_id,
                prop['type'],
                prop['portal_type'],
                aq_id,
                prop['acquisition_base_category'],
                prop['acquisition_portal_type'],
                prop['acquisition_accessor_id'],
                prop.get('acquisition_copy_value',0),
                prop.get('acquisition_mask_value',0),
                prop.get('acquisition_sync_value',0),
                storage_id = prop.get('storage_id'),
                alt_accessor_id = prop.get('alt_accessor_id'),
                is_list_type =  (prop['type'] in list_types or prop.get('multivalued', 0)),
                reindex = 1
                )
          if not hasattr(klass, accessor_name) or prop.get('override',0):
            setattr(klass, accessor_name, base_accessor)
            klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
          accessor_name = 'baseSet' + UpperCase(id)
          if not hasattr(klass, accessor_name) or prop.get('override',0):
            setattr(klass, accessor_name, base_accessor)
          # Default Getter
          ################# NOT YET 
          # List Getter
          ################# NOT YET 
          
        
    if prop['type'] == 'object':
      #LOG('Value Object Accessor', 0, prop['id'])
      # Base Getter
      accessor_name = 'get' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, base_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, base_accessor)
      # Default Getter
      accessor_name = 'getDefault' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, default_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, default_accessor)
      # List Getter
      accessor_name = 'get' + UpperCase(id) + 'ValueList'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, list_accessor)
        klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
      accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
      if not hasattr(klass, accessor_name) or prop.get('override',0):
        setattr(klass, accessor_name, list_accessor)

  elif prop['type'] in list_types or prop.get('multivalued', 0):
    # The base accessor returns the first item in a list
    # and simulates a simple property
    # The default value is the first elelement of prop.get('default') is it exists
    default = prop.get('default')
    try:
      default = default[0]
    except:
      default = None
    accessor_name = 'get' + UpperCase(id)
    base_accessor = List.Getter(accessor_name, id, prop['type'], default_value = default,
                                                 storage_id = prop.get('storage_id'))
    # The default accessor returns the first item in a list
    accessor_name = 'getDefault' + UpperCase(id)
    default_accessor = List.DefaultGetter(accessor_name, id, prop['type'], default_value = default,
                                                 storage_id = prop.get('storage_id'))
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'List'
    list_accessor = List.ListGetter(accessor_name, id, prop['type'],
             default_value = prop.get('default'), storage_id = prop.get('storage_id'))
    # The set accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'Set'
    set_accessor = List.SetGetter(accessor_name, id, prop['type'], default_value = prop.get('default'),
                                                 storage_id = prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, set_accessor)
    accessor_name = 'get' + UpperCase(id) + 'Set'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, set_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Set'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
  elif prop['type'] == 'content':
    # Create url getters for an object property
    accessor_name = 'get' + UpperCase(id)
    base_accessor = Content.Getter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The default accessor returns the first item in a list
    accessor_name = 'getDefault' + UpperCase(id)
    default_accessor = Content.DefaultGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'List'
    list_accessor = Content.ListGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
    # Create getters for an object property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    base_accessor = Content.ValueGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The default accessor returns the first item in a list
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    default_accessor = Content.DefaultValueGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    list_accessor = Content.ValueListGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # Create value getters for a list property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
    if prop.has_key('acquired_property_id'):
      for aq_id in prop['acquired_property_id']:
        composed_id = "%s_%s" % (id, aq_id)
        # print "Set composed_id accessor %s" % composed_id
        accessor_name = 'get' + UpperCase(composed_id)
        # print "Set accessor_name accessor %s" % accessor_name
        base_accessor = ContentProperty.Getter(accessor_name, composed_id, prop['type'], aq_id, 
                portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
        if not hasattr(klass, accessor_name) or prop.get('override',0):
          setattr(klass, accessor_name, base_accessor)
          klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )                
        # No default getter YET XXXXXXXXXXXXXX
        # No list getter YET XXXXXXXXXXXXXX      
        accessor_name = '_set' + UpperCase(composed_id)
        base_accessor = ContentProperty.Setter(accessor_name, composed_id, prop['type'], aq_id, 
                portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'), reindex=0)
        if not hasattr(klass, accessor_name) or prop.get('override',0):
          setattr(klass, accessor_name, base_accessor)
          klass.security.declareProtected( Permissions.ModifyPortalContent, accessor_name )                
        accessor_name = 'set' + UpperCase(composed_id)
        base_accessor = ContentProperty.Setter(accessor_name, composed_id, prop['type'], aq_id, 
                portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'), reindex=1)
        if not hasattr(klass, accessor_name) or prop.get('override',0):
          setattr(klass, accessor_name, base_accessor)
          klass.security.declareProtected( Permissions.ModifyPortalContent, accessor_name )                
        # No default getter YET XXXXXXXXXXXXXX
        # No list getter YET XXXXXXXXXXXXXX              
  elif prop['type'] == 'object':
    # Create url getters for an object property
    accessor_name = 'get' + UpperCase(id)
    base_accessor = Object.Getter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The default accessor returns the first item in a list
    accessor_name = 'getDefault' + UpperCase(id)
    default_accessor = Object.DefaultGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'List'
    list_accessor = Object.ListGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # Create getters for a list property
    accessor_name = 'get' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    accessor_name = 'getDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    accessor_name = 'get' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'List'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
    # Create getters for an object property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    base_accessor = Object.ValueGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The default accessor returns the first item in a list
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    default_accessor = Object.DefaultValueGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # The list accessor returns the whole list
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    list_accessor = Object.ValueListGetter(accessor_name, id, prop['type'],
            portal_type = prop.get('portal_type'), storage_id = prop.get('storage_id'))
    # Create value getters for a list property
    accessor_name = 'get' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, base_accessor)
    accessor_name = 'getDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGetDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, default_accessor)
    accessor_name = 'get' + UpperCase(id) + 'ValueList'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id) + 'ValueList'
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, list_accessor)
  else:
    # Create getters for a simple property
    accessor_name = 'get' + UpperCase(id)
    accessor = Base.Getter(accessor_name, id, prop['type'], default_value = prop.get('default'),
                                                 storage_id = prop.get('storage_id'))
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, accessor)
      klass.security.declareProtected( Permissions.AccessContentsInformation, accessor_name )
    accessor_name = '_baseGet' + UpperCase(id)
    if not hasattr(klass, accessor_name) or prop.get('override',0):
      setattr(klass, accessor_name, accessor)
  ######################################################
  # Create Setters
  if prop['type'] in list_types or prop.get('multivalued', 0):
    # Create setters for a list property (reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = 'set' + UpperCase(id)
    base_setter = List.Setter(setter_name, id, prop['type'], reindex=1,
                                                 storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list without changing other items
    setter_name = 'setDefault' + UpperCase(id)
    default_setter = List.DefaultSetter(setter_name, id, prop['type'], reindex=1,
                                                 storage_id = prop.get('storage_id'))
    # The list setter sets the whole list
    setter_name = 'set' + UpperCase(id) + 'List'
    list_setter = List.ListSetter(setter_name, id, prop['type'], reindex=1,
                                                 storage_id = prop.get('storage_id'))
    # The list setter sets the whole list
    setter_name = 'set' + UpperCase(id) + 'Set'
    set_setter = List.SetSetter(setter_name, id, prop['type'], reindex=1,
                                                 storage_id = prop.get('storage_id'))
    # Create setters for a list property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'set' + UpperCase(id) + 'List'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, list_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Set'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, set_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = '_set' + UpperCase(id)
    base_setter = List.Setter(setter_name, id, prop['type'], reindex=0,
                                                 storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list
    setter_name = '_setDefault' + UpperCase(id)
    default_setter = List.DefaultSetter(setter_name, id, prop['type'], reindex=0,
                                                 storage_id = prop.get('storage_id'))
    # The list setter sets the whole list
    setter_name = '_set' + UpperCase(id) + 'List'
    list_setter = List.ListSetter(setter_name, id, prop['type'], reindex=0,
                                                 storage_id = prop.get('storage_id'))
    # The list setter sets the whole list
    setter_name = '_set' + UpperCase(id) + 'Set'
    list_setter = List.SetSetter(setter_name, id, prop['type'], reindex=0,
                                                 storage_id = prop.get('storage_id'))
    # Create setters for a list property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_set' + UpperCase(id) + 'List'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, list_setter)
    setter_name = '_baseSet' + UpperCase(id) + 'List'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, list_setter)
    setter_name = '_set' + UpperCase(id) + 'Set'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, set_setter)
    setter_name = '_baseSet' + UpperCase(id) + 'Set'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, set_setter)
  elif prop['type'] == 'content':
    # Create setters for an object property
    # Create setters for a list property (reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = 'set' + UpperCase(id)
    base_setter = Content.Setter(setter_name, id, prop['type'], reindex=1,
             storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list without changing other items
    setter_name = 'setDefault' + UpperCase(id)
    default_setter =  Content.DefaultSetter(setter_name, id, prop['type'], reindex=1,
             storage_id = prop.get('storage_id'))
    # Create setters for an object property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'setDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = '_set' + UpperCase(id)
    base_setter = Content.Setter(setter_name, id, prop['type'], reindex=0,
             storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list without changing other items
    setter_name = '_setDefault' + UpperCase(id)
    default_setter =  Content.DefaultSetter(setter_name, id, prop['type'], reindex=0,
             storage_id = prop.get('storage_id'))
    # Create setters for an object property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_set' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_baseSet' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_setDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_baseSetDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
  elif prop['type'] == 'object':
    # Create setters for an object property
    # Create setters for a list property (reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = 'set' + UpperCase(id)
    base_setter = Object.Setter(setter_name, id, prop['type'], reindex=1,
             storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list without changing other items
    setter_name = 'setDefault' + UpperCase(id)
    default_setter =  Object.DefaultSetter(setter_name, id, prop['type'], reindex=1,
             storage_id = prop.get('storage_id'))
    # Create setters for an object property
    setter_name = 'set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'set' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = 'setDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    # Create setters for a list property (no reindexing)
    # The base accessor sets the list to a singleton
    # and allows simulates a simple property
    setter_name = '_set' + UpperCase(id)
    base_setter = Object.Setter(setter_name, id, prop['type'], reindex=0,
             storage_id = prop.get('storage_id'))
    # The default setter sets the first item of a list without changing other items
    setter_name = '_setDefault' + UpperCase(id)
    default_setter =  Object.DefaultSetter(setter_name, id, prop['type'], reindex=0,
             storage_id = prop.get('storage_id'))
    # Create setters for an object property
    setter_name = '_set' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_setDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_baseSetDefault' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_set' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_baseSet' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, base_setter)
    setter_name = '_setDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
    setter_name = '_baseSetDefault' + UpperCase(id) + 'Value'
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, default_setter)
  else:
    # Create setters for a simple property
    setter_name = 'set' + UpperCase(id)
    setter = Base.Setter(setter_name, id, prop['type'], reindex=1,
                                                 storage_id = prop.get('storage_id'))
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, setter)
      klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)
    setter_name = '_set' + UpperCase(id)
    setter = Base.Setter(setter_name, id, prop['type'], reindex=0,
                                                 storage_id = prop.get('storage_id'))
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, setter)
    setter_name = '_baseSet' + UpperCase(id)
    if not hasattr(klass, setter_name):
      setattr(klass, setter_name, setter)
  ######################################################
  # Create testers
  if prop['type'] == 'content':
    tester_name = 'has' + UpperCase(id)
    tester = Content.Tester(tester_name, id, prop['type'],
                                                  storage_id = prop.get('storage_id'))
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
  if prop['type'] == 'object':
    tester_name = 'has' + UpperCase(id)
    tester = Object.Tester(tester_name, id, prop['type'],
                                                  storage_id = prop.get('storage_id'))
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
  else:
    tester_name = 'has' + UpperCase(id)
    tester = Base.Tester(tester_name, id, prop['type'],
                                                  storage_id = prop.get('storage_id'))
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseHas' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)

    # List Tester
    tester_name = 'has' + UpperCase(id) + 'List'
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseHas' + UpperCase(id) + 'List'
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
    tester_name = 'hasDefault' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)
      BaseClass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseHasDefault' + UpperCase(id)
    if not hasattr(BaseClass, tester_name):
      setattr(BaseClass, tester_name, tester)

    # First Implementation of Boolean Accessor
    tester_name = 'is' + UpperCase(id)
    tester = Base.Getter(tester_name, id, prop['type'],
                                                  storage_id = prop.get('storage_id'))
    if not hasattr(klass, tester_name):
      setattr(klass, tester_name, tester)
      klass.security.declareProtected(Permissions.AccessContentsInformation, tester_name)
    tester_name = '_baseIs' + UpperCase(id)
    tester = Base.Getter(tester_name, id, prop['type'],
                                                  storage_id = prop.get('storage_id'))
    if not hasattr(klass, tester_name):
      setattr(klass, tester_name, tester)

from Accessor import Category

def createCategoryAccessors(klass, id):
  """
    This function creates category accessor and setter for a class
    and a property
  """
  accessor_name = 'get' + UpperCase(id) + 'List'
  accessor = Category.ListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'List'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'Set'
  accessor = Category.SetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Set'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'ItemList'
  accessor = Category.ItemListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)

  accessor_name = 'getDefault' + UpperCase(id)
  accessor = Category.DefaultGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  setter_name = 'set' + UpperCase(id)
  setter = Category.Setter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'set' + UpperCase(id) + 'List'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'setDefault' + UpperCase(id)
  setter = Category.DefaultSetter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = '_set' + UpperCase(id)
  setter = Category.Setter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_set' + UpperCase(id) + 'List'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id) + 'List'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_set' + UpperCase(id) + 'Set'
  setter = Category.SetSetter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id) + 'Set'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_setDefault' + UpperCase(id)
  setter = Category.DefaultSetter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySetDefault' + UpperCase(id)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)


from Accessor import Value, Related, RelatedValue

def createValueAccessors(klass, id):
  """
    Creates relation accessors for category id

     TODO: Security declarations must be checked

  """
  accessor_name = 'get' + UpperCase(id) + 'ValueList'
  accessor = Value.ListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ValueList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = UpperCase(id) + 'Values'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)

  accessor_name = 'get' + UpperCase(id) + 'ValueSet'
  accessor = Value.SetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'ValueSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'TitleList'
  accessor = Value.TitleListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'TitleSet'
  accessor = Value.TitleSetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'TitleSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'IdList'
  accessor = Value.IdListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'IdList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = UpperCase(id) + 'Ids'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)

  accessor_name = 'get' + UpperCase(id) + 'IdSet'
  accessor = Value.IdSetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'IdSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'UidList'
  accessor = Value.UidListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'UidList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'UidSet'
  accessor = Value.UidSetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'UidSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'PropertyList'
  accessor = Value.PropertyListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertyList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'PropertySet'
  accessor = Value.PropertySetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'PropertySet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Value'
  accessor = Value.DefaultGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Value'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = 'get' + UpperCase(id) + 'Value'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Value'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Title'
  accessor = Value.DefaultTitleGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Title'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Title'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Title'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Uid'
  accessor = Value.DefaultUidGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Uid'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Uid'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Uid'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Id'
  accessor = Value.DefaultIdGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Id'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Id'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Id'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Property'
  accessor = Value.DefaultIdGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Property'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Property'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Property'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  setter_name = 'set' + UpperCase(id) + 'Value'
  setter = Value.Setter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueList'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'set' + UpperCase(id) + 'ValueSet'
  setter = Value.SetSetter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'setDefault' + UpperCase(id) + 'Value'
  setter = Value.DefaultSetter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = '_set' + UpperCase(id) + 'Value'
  setter = Value.Setter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id) + 'Value'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_set' + UpperCase(id) + 'ValueList'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueList'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_set' + UpperCase(id) + 'ValueSet'
  setter = Value.SetSetter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySet' + UpperCase(id) + 'ValueSet'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  setter_name = '_setDefault' + UpperCase(id) + 'Value'
  setter = Value.DefaultSetter(setter_name, id, reindex=0)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
  setter_name = '_categorySetDefault' + UpperCase(id) + 'Value'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)

  # Uid setters
  setter_name = 'set' + UpperCase(id) + 'Uid'
  setter = Value.UidSetter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidList'
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)

  setter_name = 'set' + UpperCase(id) + 'UidSet'
  setter = Value.UidSetSetter(setter_name, id, reindex=1)
  if not hasattr(klass, setter_name):
    setattr(klass, setter_name, setter)
    klass.security.declareProtected(Permissions.ModifyPortalContent, setter_name)     
    
  # XXX Missing Uid setters
        
  # Related Values (ie. reverse relation getters)
  klass = BaseClass

  accessor_name = UpperCase(id) + 'RelatedValues'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  accessor = RelatedValue.ListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedValueList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedValueList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'RelatedValueSet'
  accessor = RelatedValue.SetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedValueSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'RelatedValue'
  accessor = RelatedValue.DefaultGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedValue'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'RelatedValue'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedValue'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  # Related Relative Url (ie. reverse relation getters)
  klass = BaseClass

  accessor_name = 'get' + UpperCase(id) + 'RelatedList'
  accessor = Related.ListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'RelatedSet'
  accessor = Related.SetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'Related'
  accessor = Related.DefaultGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'Related'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'Related'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'Related'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  # Related Ids (ie. reverse relation getters)
  klass = BaseClass

  accessor_name = UpperCase(id) + 'RelatedIds'
  accessor_name = string.lower(accessor_name[0]) + accessor_name[1:]
  accessor = RelatedValue.IdListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedIdList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedIdList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'RelatedIdSet'
  accessor = RelatedValue.IdSetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedIdSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'RelatedId'
  accessor = RelatedValue.DefaultIdGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedId'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'RelatedId'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedId'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  # Related Ids (ie. reverse relation getters)
  klass = BaseClass

  accessor_name = 'get' + UpperCase(id) + 'RelatedTitleList'
  accessor = RelatedValue.TitleListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedTitleList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'RelatedTitleSet'
  accessor = RelatedValue.TitleSetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedTitleSet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'RelatedTitle'
  accessor = RelatedValue.DefaultTitleGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedTitle'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'RelatedTitle'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedTitle'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  # Related Ids (ie. reverse relation getters)
  klass = BaseClass

  accessor_name = 'get' + UpperCase(id) + 'RelatedPropertyList'
  accessor = RelatedValue.PropertyListGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedPropertyList'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'get' + UpperCase(id) + 'RelatedPropertySet'
  accessor = RelatedValue.PropertySetGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedPropertySet'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)

  accessor_name = 'getDefault' + UpperCase(id) + 'RelatedProperty'
  accessor = RelatedValue.DefaultPropertyGetter(accessor_name, id)
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = 'get' + UpperCase(id) + 'RelatedProperty'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
    klass.security.declareProtected(Permissions.AccessContentsInformation, accessor_name)
  accessor_name = '_categoryGetDefault' + UpperCase(id) + 'RelatedProperty'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)
  accessor_name = '_categoryGet' + UpperCase(id) + 'RelatedProperty'
  if not hasattr(klass, accessor_name):
    setattr(klass, accessor_name, accessor)


#####################################################
# More Useful methods which require Base
#####################################################

def assertAttributePortalType(o, attribute_name, portal_type):
  """
    portal_type   --    string or list
  """
  # Checks or deletes
  if hasattr(o,attribute_name):
    value = getattr(o, attribute_name)
    if not isinstance(value, BaseClass):
      # Delete local attribute if it exists
      if hasattr(aq_self(o),attribute_name):
        delattr(o, attribute_name)
      # But do not delete object
      #if attribute_name in o.objectIds():
      #  o._delObject(attribute_name)
    if hasattr(o,attribute_name):
      try:
        if type(portal_type) is type('a'): portal_type = [portal_type]
        if getattr(o, attribute_name).portal_type not in portal_type:
          o._delObject(attribute_name)
      except:
        LOG("ERPType Warning: assertAttributePortalType",100,str(o.absolute_url()))

#####################################################
# Monkey Patch
#####################################################

from types import FunctionType
def monkeyPatch(from_class,to_class):
  for id, m in from_class.__dict__.items():
      if type(m) is FunctionType:
          setattr(to_class, id, m)
