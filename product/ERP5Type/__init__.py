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
"""
    ERP5Type is provides a RAD environment for Zope / CMF
    All ERP5 classes derive from ERP5Type
"""

# First import the minimal number of packages required by the code generation
from Products.ERP5Type.InitGenerator import generateInitFiles
import sys

# Update the self generated code for Document, PropertySheet and Interface
this_module = sys.modules[ __name__ ]
document_classes = generateInitFiles(this_module, globals(), generate_document=0)

# Import rest of the code and finish installation
from Products.ERP5Type.Utils import initializeProduct, initializeLocalDocumentRegistry
import Interface, PropertySheet, ZopePatch, StateChangeInfoPatch, \
       CMFCorePatch, FormulatorPatch

def initialize( context ):
  # Import Product Components
  from Tool import ClassTool
  import Document
  import Base, XMLObject
  # Define documents, classes, constructors and tools
  object_classes = ()
  content_constructors = ()
  content_classes = (Base.Base, XMLObject.XMLObject,)
  portal_tools = (ClassTool.ClassTool, )
  # Do initialization step
  initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = object_classes,
                         portal_tools = portal_tools,
                         content_constructors = content_constructors,
                         content_classes = content_classes)
  # We should register local classes at some point
  from Products.ERP5Type.InitGenerator import initializeProductDocumentRegistry
  initializeProductDocumentRegistry()
  initializeLocalDocumentRegistry()

from AccessControl.SecurityInfo import allow_module

allow_module('Products.ERP5Type.Cache')
