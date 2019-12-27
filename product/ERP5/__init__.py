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

# Update ERP5 Globals
from Products.ERP5Type.Utils import initializeProduct, updateGlobals
import sys, Permissions
this_module = sys.modules[ __name__ ]
document_classes = updateGlobals( this_module, globals(), permissions_module = Permissions)
from Products.PythonScripts.Utility import allow_class
from AccessControl import ModuleSecurityInfo

import MovementGroup
allow_class(MovementGroup)

from Products.ERP5Type.Globals import package_home
product_path = package_home( globals() )

# Define object classes and tools
from Tool import CategoryTool, SimulationTool, RuleTool, IdTool, TemplateTool,\
                 TestTool, DomainTool, AlarmTool, OrderTool, DeliveryTool,\
                 TrashTool, ContributionTool, NotificationTool, PasswordTool,\
                 GadgetTool, ContributionRegistryTool, IntrospectionTool,\
                 AcknowledgementTool, SolverTool, SolverProcessTool,\
                 UrlRegistryTool, InterfaceTool,\
                 CertificateAuthorityTool, InotifyTool, TaskDistributionTool
import ERP5Site
from Document import PythonScript, SQLMethod
object_classes = ( ERP5Site.ERP5Site,
                   PythonScript.PythonScriptThroughZMI,
                   SQLMethod.SQLMethod,
                 )
portal_tools = ( CategoryTool.CategoryTool,
                 SimulationTool.SimulationTool,
                 RuleTool.RuleTool,
                 IdTool.IdTool,
                 TemplateTool.TemplateTool,
                 AlarmTool.AlarmTool,
                 DomainTool.DomainTool,
                 TestTool.TestTool,
                 OrderTool.OrderTool,
                 DeliveryTool.DeliveryTool,
                 TrashTool.TrashTool,
                 PasswordTool.PasswordTool,
                 ContributionTool.ContributionTool,
                 NotificationTool.NotificationTool,
                 GadgetTool.GadgetTool,
                 ContributionRegistryTool.ContributionRegistryTool,
                 IntrospectionTool.IntrospectionTool,
                 AcknowledgementTool.AcknowledgementTool,
                 SolverTool.SolverTool,
                 SolverProcessTool.SolverProcessTool,
                 UrlRegistryTool.UrlRegistryTool,
                 CertificateAuthorityTool.CertificateAuthorityTool,
                 InotifyTool.InotifyTool,
                 TaskDistributionTool.TaskDistributionTool,
                 InterfaceTool.InterfaceTool,
                )
content_classes = ()
content_constructors = ()

# Finish installation
def initialize( context ):
  import Document
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
  import Products.ERP5.InteractionWorkflow

# backward compatibility names
XML = None
UI = None
