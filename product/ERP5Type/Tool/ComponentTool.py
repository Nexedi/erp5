# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                     Jean-Paul Smets <jp@nexedi.com>
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


""" Component Tool module for ERP5 """
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions

class ComponentLoader:
  """
    A callable class which delegates component load to ComponentTool
    and which contains attributes which can either be called or
    implement default component access for different types of components
  """
  def __init__(self):
    self.component = self
    # This could be automated by introspecting 
    # portal_types and listing all component types
    self.document = TypedComponentLoader('Document Component')
    self.interface = TypedComponentLoader('Interface Component')
    self.mixin = TypedComponentLoader('Mixin Component')
    self.accessor = TypedComponentLoader('Accessor Component')
    self.test = TypedComponentLoader('Test Component')
    self.extension = TypedComponentLoader('Extension Component')
    
  def __call__(self, portal_type, reference, version=None):
    site = getSite()
    return site.portal_components.loadComponent(portal_type, reference, version=version)

def TypedComponentLoader(ComponentLoader):
  """
    A callable class which delegates component load to
    ComponentLoader and provides default component access through
    attributes.
  """
  def __init__(self, portal_type):
    self._portal_type = portal_type
    
  def __call__(self, reference, version=None):
    return ComponentLoader.__call__(self._portal_type, reference, version=version)

  def __getattr__(self, key):
    if key.startswith('_'):
      return self.__dict__[key]
    return self(key)

component = ComponentLoader()

component_revision = None
component_dict = None

class ComponentTool(BaseTool):
  """
    This tool provides methods to load the the different types 
    of components of the ERP5 framework: Document classes, interfaces,
    mixin classes, fields, accessors, etc.
  """

  id = "portal_components"
  meta_type = "ERP5 Component Tool"
  portal_type = "Component Tool"

  security = ClassSecurityInfo()
  manage_options = BaseTool.manage_options

  def loadComponent(self, portal_type, reference, version=None):
    """
    This first version compiles all components once. A lazy
    version could be more efficient.
    """
    global component_dict
    # Reset cache if modified
    #if component_revision is None:
    #  component_dict = None
    if component_dict is None:
      component_dict = {}
      for document in contentValues():
        portal_type = document.getPortalType()
        version = document.getVersion()
        reference = document.getReference()
        component = document.loadComponent()
        typed_component_dict = component_dict.setdefault(portal_type, {})
        component_version_dict = typed_component_dict.setdefault(reference, {})
        # How to handle default ?
        component_version_dict[version] = component
        component_version_dict[None] = component
    return component_dict[portal_type][reference][version]
