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

def enableEgovProcedureLogin(self, portal_type):
  '''
  set properties to enable the login on Person and Organisation
  and subcription forms (citizen, company, agent)
  '''
  portal = self.getPortalObject()

  def getAclUsers(self):
    return getattr(self.getPortalObject(), 'acl_users', None)
  acl_users = getAclUsers(self)
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
  return '- %s Login Enabled' % portal_type

def setUpEGovSecurityManager(self):
  '''use safi PAS to be able to login organisation'''

  portal = self.getPortalObject()

  def getAclUsers(self):
    return getattr(self.getPortalObject(), 'acl_users', None)

  acl_users = getAclUsers(self)

  # Add EGOVUserManager
  ZopeTestCase.installProduct('EGOVSecurity')
  erp5security_dispatcher = acl_users.manage_addProduct['ERP5eGovSecurity']
  # don't add it if it's already here
  if {'meta_type': 'EGOV User Manager', 'id': 'egov_users'} not in \
      erp5security_dispatcher._d._objects:
    erp5security_dispatcher.addEGOVUserManager('egov_users')
  if {'meta_type': 'EGOV Group Manager', 'id': 'egov_groups'} not in \
      erp5security_dispatcher._d._objects :
    erp5security_dispatcher.addEGOVGroupManager('egov_groups')
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


def setUpInstance(self):
  '''call all other set up method to prepare the site for eGOV Instance'''
  message_list = []
  message_list.append(setUpEGovSecurityManager(self))

  message_list.append('')
  message_list.append('Set Up sequence completed')
  return '\n'.join(message_list)

