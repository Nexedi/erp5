##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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


import os, re, string, sys
from Globals import package_home, InitializeClass

from zLOG import LOG

global product_document_registry
product_document_registry = []

def InitializeDocument(document_class, document_path=None):
  global product_document_registry
  InitializeClass(document_class)
  # Register class in ERP5Type.Document
  product_document_registry.append(((document_class.__name__, document_path)))

def initializeProductDocumentRegistry():
  from Utils import importLocalDocument
  for (class_id, document_path) in product_document_registry:
    importLocalDocument(class_id, document_path=document_path)
    print 'Added product document to ERP5Type repository: %s (%s)' % (class_id, document_path)

# Code Generation of __init__.py files
def generateInitFiles(this_module, global_hook,
                      generate_document=1, generate_property_sheet=1, generate_constraint=1, generate_interface=1):
  # Determine product_path
  product_path = package_home( global_hook )
  # Add _dtmldir
  this_module._dtmldir = os.path.join( product_path, 'dtml' )
  # This regular expression is used to check is a file is a python file
  python_file_expr = re.compile("py$")

  # Create Document __init__.py file
  document_path = product_path + '/Document'
  document_module_name_list = []
  document_module_lines = ["from Products.ERP5Type import Document as ERP5TypeDocumentRepository\n\n"]
  try:
    file_list = os.listdir(document_path)
    for file_name in file_list:
      if file_name != '__init__.py':
        if python_file_expr.search(file_name,1):
          module_name = file_name[0:-3]
          document_module_name_list += [module_name]
          document_module_lines += ["""\
# Hide internal implementation
from Products.ERP5Type.InitGenerator import InitializeDocument
import %s as ERP5%s
if not hasattr(ERP5TypeDocumentRepository, '_override_%s'): ERP5TypeDocumentRepository.%s = ERP5%s  # Never override a local Document class
# Default constructor for %s
# Can be overriden by adding a method add%s in class %s
def add%s(folder, id, REQUEST=None, **kw):
  o = ERP5TypeDocumentRepository.%s.%s(id)
  folder._setObject(id, o)
  if kw is not None: o.__of__(folder)._edit(force_update=1, **kw)
  # contentCreate already calls reindex 3 times ...
  # o.reindexObject()
  if REQUEST is not None:
      REQUEST['RESPONSE'].redirect( 'manage_main' )

InitializeDocument(ERP5TypeDocumentRepository.%s.%s, document_path='%s')

class Temp%s(ERP5TypeDocumentRepository.%s.%s):
  isIndexable = 0

  def reindexObject(self, *args, **kw):
    pass

  def recursiveReindexObject(self, *args, **kw):
    pass

  def activate(self):
    return self

from Products.PythonScripts.Utility import allow_class
allow_class(Temp%s)

def newTemp%s(folder, id, REQUEST=None, **kw):
  o = Temp%s(id)
  o = o.__of__(folder)
  if kw is not None: o._edit(force_update=1, **kw)
  return o

ERP5TypeDocumentRepository.newTemp%s = newTemp%s
from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.ERP5Type.Document').declarePublic('newTemp%s',)

""" % (module_name, module_name,
       module_name, module_name, module_name,
       module_name,
       module_name, module_name,
       module_name,
       module_name, module_name,
       module_name, module_name, document_path,
       module_name, module_name, module_name,
       module_name,
       module_name,
       module_name,
       module_name, module_name,
       module_name,)]

    if generate_document:
      try:
        document_init_file = open(document_path + '/__init__.py', 'w')
        document_init_file.write(string.join(document_module_lines, '\n'))
        document_init_file.close()
      except:
        LOG('ERP5Type:',0,'Could not write Document __init__.py files for %s' % product_path)
  except:
      LOG('ERP5Type:',0,'No Document directory in %s' % product_path)

  # Create Property __init__.py file
  property_path = product_path + '/PropertySheet'
  property_module_name_list = []
  property_module_lines = []
  try:
    file_list = os.listdir(property_path)
    for file_name in file_list:
      if file_name != '__init__.py':
        if python_file_expr.search(file_name,1):
          module_name = file_name[0:-3]
          property_module_name_list += [module_name]
          property_module_lines += ['from %s import %s' % (module_name, module_name)]
    if generate_property_sheet:
      try:
        property_init_file = open(property_path + '/__init__.py', 'w')
        property_init_file.write(string.join(property_module_lines, '\n'))
        property_init_file.close()
      except:
        LOG('ERP5Type:',0,'Could not write PropertySheet __init__.py files for %s' % product_path)
  except:
      LOG('ERP5Type:',0,'No PropertySheet directory in %s' % product_path)

  # Create Interface __init__.py file
  interface_path = product_path + '/Interface'
  interface_module_name_list = []
  interface_module_lines = []
  try:
    file_list = os.listdir(interface_path)
    for file_name in file_list:
      if file_name != '__init__.py':
        if python_file_expr.search(file_name,1):
          module_name = file_name[0:-3]
          interface_module_name_list += [module_name]
          interface_module_lines += ['from %s import %s' % (module_name, module_name)]
    if generate_interface:
      try:
        interface_init_file = open(interface_path + '/__init__.py', 'w')
        interface_init_file.write(string.join(interface_module_lines, '\n'))
        interface_init_file.close()
      except:
        LOG('ERP5Type:',0,'Could not write Interface __init__.py files for %s' % product_path)
  except:
      LOG('ERP5Type:',0,'No Interface directory in %s' % product_path)

  # Create Constraint __init__.py file
  constraint_path = product_path + '/Constraint'
  constraint_module_name_list = []
  constraint_module_lines = []
  try:
    file_list = os.listdir(constraint_path)
    for file_name in file_list:
      if file_name != '__init__.py':
        if python_file_expr.search(file_name,1):
          module_name = file_name[0:-3]
          constraint_module_name_list += [module_name]
          constraint_module_lines += ['from %s import %s' % (module_name, module_name)]
    if generate_constraint:
      try:
        constraint_init_file = open(constraint_path + '/__init__.py', 'w')
        constraint_init_file.write(string.join(constraint_module_lines, '\n'))
        constraint_init_file.close()
      except:
        LOG('ERP5Type:',0,'Could not write Constraint __init__.py files for %s' % product_path)
  except:
      LOG('ERP5Type:',0,'No Constraint directory in %s' % product_path)

  return document_module_name_list
