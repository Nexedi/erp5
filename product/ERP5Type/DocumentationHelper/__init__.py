# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007-2008 Nexedi SA and Contributors. All Rights Reserved.
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

from DocumentationSection import DocumentationSection

# Automatic import "à la" Document would be more consistent
# I even wonder whether using Document classes everywhere would be better
# from a reflexive point of view (ie. to build persistent documentation)
from DocumentationHelper import DocumentationHelper
from AccessorMethodDocumentationHelper import AccessorMethodDocumentationHelper
from BusinessTemplateDocumentationHelper import BusinessTemplateDocumentationHelper
from CallableDocumentationHelper import CallableDocumentationHelper
from ClassMethodDocumentationHelper import ClassMethodDocumentationHelper
from DCWorkflowDocumentationHelper import DCWorkflowDocumentationHelper
from InstancePropertyDocumentationHelper import InstancePropertyDocumentationHelper
from PortalDocumentationHelper import PortalDocumentationHelper
from PortalTypeDocumentationHelper import PortalTypeDocumentationHelper
from PortalTypeInstanceDocumentationHelper import PortalTypeInstanceDocumentationHelper
from PortalTypeRoleDocumentationHelper import PortalTypeRoleDocumentationHelper
from PortalTypeActionDocumentationHelper import PortalTypeActionDocumentationHelper
from PortalTypePropertySheetDocumentationHelper import PortalTypePropertySheetDocumentationHelper
from PropertyDocumentationHelper import PropertyDocumentationHelper
from WorkflowMethodDocumentationHelper import WorkflowMethodDocumentationHelper
from DCWorkflowStateDocumentationHelper import DCWorkflowStateDocumentationHelper
from DCWorkflowTransitionDocumentationHelper import DCWorkflowTransitionDocumentationHelper
from DCWorkflowVariableDocumentationHelper import DCWorkflowVariableDocumentationHelper
from DCWorkflowWorklistDocumentationHelper import DCWorkflowWorklistDocumentationHelper
from DCWorkflowScriptDocumentationHelper import DCWorkflowScriptDocumentationHelper
from SkinFolderDocumentationHelper import SkinFolderDocumentationHelper
from InteractionWorkflowDocumentationHelper import InteractionWorkflowDocumentationHelper
from CatalogMethodDocumentationHelper import CatalogMethodDocumentationHelper
from SkinFolderItemDocumentationHelper  import SkinFolderItemDocumentationHelper
from ScriptPythonDocumentationHelper import ScriptPythonDocumentationHelper
from ERP5FormDocumentationHelper import ERP5FormDocumentationHelper
from PageTemplateDocumentationHelper import PageTemplateDocumentationHelper
from ZSQLMethodDocumentationHelper import ZSQLMethodDocumentationHelper
from BaseCategoryDocumentationHelper import BaseCategoryDocumentationHelper
from ERP5SiteDocumentationHelper import ERP5SiteDocumentationHelper

