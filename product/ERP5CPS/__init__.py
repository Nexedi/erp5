# (C) Copyright 2004 Nexedi SARL <http://nexedi.com>
# Authors: Sebastien Robin <seb@nexedi.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#

import CPSCorePatch, CPSDocumentPatch, SynchronizationToolPatch

import CPSCorePatch, CPSDocumentPatch, SynchronizationToolPatch

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
from Products.ERP5Type import Permissions
import sys

this_module = sys.modules[ __name__ ]
document_classes = updateGlobals( this_module, globals(), permissions_module =
Permissions)

# Define object classes and tools
import ERP5CPSSite

object_classes = ( ERP5CPSSite.ERP5CPSSite,)
portal_tools = ( )
content_classes = ()
content_constructors = ()

# Finish installation
def initialize( context ):
  import Document
  from zLOG import LOG
  LOG('In ERP5CPS initialize', 0, '')
  initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = object_classes,
                         portal_tools = portal_tools,
                         content_constructors = content_constructors,
                         content_classes = content_classes)

