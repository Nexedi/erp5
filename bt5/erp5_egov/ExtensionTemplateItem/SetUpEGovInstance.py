# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                  Fabien Morin <fabien@nexedi.com>
#                  Mohamadou Mbengue <mmbengue@gmail.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Testing import ZopeTestCase
from Products import ERP5Security
from Products import PluggableAuthService
from zLOG import LOG, WARNING, INFO
from Products.ERP5eGovSecurity.EGOVUserManager import addEGOVUserManager
from Products.ERP5eGovSecurity.EGOVGroupManager import addEGOVGroupManager

def allowAccessOnContributionRegistryPortalTypes(self):
  ''' Set Type Acquire Local Role '''

  portal = self.getPortalObject()
  portal_contribution_registry = portal.portal_contribution_registry
  pt_title_list =  [p.getDestinationPortalType()
    for p in portal_contribution_registry.contentValues()]
  exclude_pt_title_list = ['Web Page', 'DMS Ingestion', 'Default Predicate']

  for pt_title in pt_title_list:
    if pt_title not in exclude_pt_title_list:
      portal_type_object = portal.portal_types.getTypeInfo(pt_title)
      #set acquired local role on the portal type
      portal_type_object.setTypeAcquireLocalRole(1)

  return '- Access on Contribution Registry Portal Types allowed'

def allowAccessOnPersonAndOrganisation(self):
  '''Add local role on person and organisation to give
     administrative agent access.
  '''
  portal_type_list = map(self.getPortalObject().portal_types.getTypeInfo,
    ('Person', 'Person Module', 'Organisation', 'Organisation Module'))

  role_category_list = ['role/gouvernement']
  for ptype in portal_type_list:
    role_info_list=[role_info.getTitle() for role_info in ptype.contentValues(portal_type='Role Information')]
    if 'Agent Administratif' not in role_info_list:
      ptype.newContent(portal_type='Role Information',
                     title='Agent Administratif',
                     role_name='Auditor',
                     role_category_list=role_category_list)
  for ptype in portal_type_list:
    ptype.updateRoleMapping()

  return '- Access on Person and Organisation allowed for administrative agent'

def enableEgovProcedureLogin(self, portal_type):
  '''
  set properties to enable the login on Person and Organisation
  and subcription forms (citizen, company, agent)
  '''
  portal = self.getPortalObject()
  acl_users = portal.acl_users

  erp5security_dispatcher = acl_users.manage_addProduct['ERP5eGovSecurity']
  # add the portal_type in Egov portal_type_list
  if {'meta_type': 'EGOV User Manager', 'id': 'egov_users'} in \
      erp5security_dispatcher._d._objects:
    ptype_list = acl_users.egov_users.portal_type_list
    if not portal_type in ptype_list:
      ptype_list = ptype_list + (portal_type,)
      acl_users.egov_users.manage_changeProperties(portal_type_list=ptype_list,)
  if {'meta_type': 'EGOV Group Manager', 'id': 'egov_groups'} in \
      erp5security_dispatcher._d._objects :
    ptype_list = acl_users.egov_groups.portal_type_list
    if not portal_type in ptype_list:
      ptype_list = ptype_list + (portal_type,)
      acl_users.egov_groups.manage_changeProperties(portal_type_list=ptype_list,)
  return '- %s Login Enabled' % portal_type


def setUpEGovSecurityManager(self):
  '''use safi PAS to be able to login organisation'''
  
  portal = self.getPortalObject()
  acl_users = portal.acl_users

  # Add EGOVUserManager
  ZopeTestCase.installProduct('ERP5eGovSecurity')
  erp5security_dispatcher = acl_users.manage_addProduct['ERP5eGovSecurity']
  # don't add it if it's already here
  if {'meta_type': 'EGOV User Manager', 'id': 'egov_users'} not in \
      erp5security_dispatcher._d._objects:
    addEGOVUserManager(erp5security_dispatcher, 'egov_users')

  if {'meta_type': 'EGOV Group Manager', 'id': 'egov_groups'} not in \
      erp5security_dispatcher._d._objects :
    addEGOVGroupManager(erp5security_dispatcher, 'egov_groups')
    
  # Register ERP5UserManager Interface
  acl_users.egov_users.manage_activateInterfaces(('IAuthenticationPlugin',
                                                  'IUserEnumerationPlugin',))
  acl_users.egov_groups.manage_activateInterfaces(('IGroupsPlugin',))

  # desactivate the erp5 plugin
  plugins = acl_users.egov_groups.plugins
  interface = plugins._getInterfaceFromName('IGroupsPlugin')
  if 'erp5_groups' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_groups')
  plugins = acl_users.egov_users.plugins
  interface = plugins._getInterfaceFromName('IAuthenticationPlugin')
  if 'erp5_users' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_users')
  interface = plugins._getInterfaceFromName('IUserEnumerationPlugin')
  if 'erp5_users' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_users')

  # set properties to enable the login on Person and Organisation
  # and subcription forms (citizen, company, agent)
  acl_users.egov_users.manage_changeProperties(portal_type_list=[
                                                      'Person',
                                                      'Organisation'],)
  acl_users.egov_groups.manage_changeProperties(portal_type_list=[
                                                      'Person',
                                                      'Organisation'],)
  return '- EGOV security set up completed'

def publishAllWebPages(self):
  '''web pages are accessible by anonymous users only if they are published'''
  web_page_module = self.getPortalObject().web_page_module
  for web_page in web_page_module.contentValues():
    if web_page.getValidationState() != 'published':
      web_page.publish()
  return '- All web pages are published'

def allowAddingEGovTypes(self):
  '''Allow adding instance of portal_type EGov Type and Meta EGov Type'''
  types_tool = self.getPortalObject().portal_types.getTypeInfo()
  allowed_content_type_list = types_tool.getTypeAllowedContentTypeList()
  allowed_content_type_list.append('Meta EGov Type')
  allowed_content_type_list.append('EGov Type')
  types_tool.setTypeAllowedContentTypeList(allowed_content_type_list)
  return '- Instance of EGov Type and Meta EGov Type are allowed'

def setUpInstance(self):
  '''call all other set up method to prepare the site for eGOV Instance'''
  message_list = []
  message_list.append(setUpEGovSecurityManager(self))
  message_list.append(allowAccessOnPersonAndOrganisation(self))
  message_list.append(allowAccessOnContributionRegistryPortalTypes(self))
  message_list.append(publishAllWebPages(self))
  message_list.append(allowAddingEGovTypes(self))
  message_list.append('')
  message_list.append('Set Up sequence completed')
  return '\n'.join(message_list)

