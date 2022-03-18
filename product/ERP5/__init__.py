# -*- coding: utf-8 -*-
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
    ERP5 Free Software ERP
"""
from __future__ import absolute_import

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
import sys
from . import Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals( this_module, globals(), permissions_module = Permissions)
from AccessControl import ModuleSecurityInfo

from Products.ERP5Type.Globals import package_home
product_path = package_home( globals() )

# Define object classes and tools
from .Tool import CategoryTool, IdTool, TemplateTool,\
                 AlarmTool,\
                 TrashTool,\
                 SolverTool
from . import ERP5Site
from .Document import PythonScript, SQLMethod
object_classes = ( ERP5Site.ERP5Site,
                   PythonScript.PythonScriptThroughZMI,
                   SQLMethod.SQLMethod,
                 )
portal_tools = ( CategoryTool.CategoryTool,
                 IdTool.IdTool,
                 TemplateTool.TemplateTool,
                 AlarmTool.AlarmTool,
                 TrashTool.TrashTool,
                 SolverTool.SolverTool,
                )
content_classes = ()
content_constructors = ()

# Finish installation
def initialize( context ):
  from . import Document
  # Initialize
  initializeProduct(context, this_module, globals(),
                         document_module = Document,
                         document_classes = document_classes,
                         object_classes = object_classes,
                         portal_tools = portal_tools,
                         content_constructors = content_constructors,
                         content_classes = content_classes)

  # Allow some usefull classes and fonctions in TTW code
  ModuleSecurityInfo('ZODB.POSException').declarePublic('ConflictError')
  ModuleSecurityInfo('Products.CMFCore.WorkflowCore').declarePublic(
                                                   'WorkflowException')

  # Make sure InteactionWorkflow is visible in UI
  from Products.ERP5Type import WITH_LEGACY_WORKFLOW
  if WITH_LEGACY_WORKFLOW:
    import Products.ERP5.InteractionWorkflow

# backward compatibility names
XML = None
UI = None
