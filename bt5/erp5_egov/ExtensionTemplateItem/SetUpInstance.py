##############################################################################
#
# Copyright (c) 2008 Nexedi SARL and Contributors. All Rights Reserved.
#                    Fabien Morin <fabien@nexedi.com>
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
from Testing import ZopeTestCase
from Products import ERP5Security
from Products import PluggableAuthService

def setUpEGovPas(self):
  '''use safi PAS to be able to login organisation'''

  portal = self.getPortalObject()

  def getAclUsers(self):
    return getattr(self.getPortalObject(), 'acl_users', None)

  acl_users = getAclUsers(self)

  # Add SAFIUserManager
  ZopeTestCase.installProduct('SAFISecurity')
  erp5security_dispatcher = acl_users.manage_addProduct['SAFISecurity']
  # don't add it if it's already here
  if {'meta_type': 'SAFI User Manager', 'id': 'safi_users'} not in \
      erp5security_dispatcher._d._objects:
    erp5security_dispatcher.addSAFIUserManager('safi_users')
  if {'meta_type': 'SAFI Group Manager', 'id': 'safi_groups'} not in \
      erp5security_dispatcher._d._objects :
    erp5security_dispatcher.addSAFIGroupManager('safi_groups')
  # Register ERP5UserManager Interface
  acl_users.safi_users.manage_activateInterfaces(('IAuthenticationPlugin',
                                                  'IUserEnumerationPlugin',))
  acl_users.safi_groups.manage_activateInterfaces(('IGroupsPlugin',))

  # desactivate the erp5 plugin
  plugins = acl_users.safi_groups.plugins
  interface = plugins._getInterfaceFromName('IGroupsPlugin')
  if 'erp5_groups' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_groups')
  plugins = acl_users.safi_users.plugins
  interface = plugins._getInterfaceFromName('IAuthenticationPlugin')
  if 'erp5_users' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_users')
  interface = plugins._getInterfaceFromName('IUserEnumerationPlugin')
  if 'erp5_users' in list(plugins._getPlugins(interface)):
    plugins.deactivatePlugin( interface, 'erp5_users')

  # set properties to enable the login on Person and Organisation
  acl_users.safi_users.manage_changeProperties(portal_type_list=[
                                                      'Person',
                                                      'Organisation',
                                                      'Subscription Form'],)
  acl_users.safi_groups.manage_changeProperties(portal_type_list=[
                                                      'Person',
                                                      'Organisation',
                                                      'Subscription Form'],)
  return '- PAS security set up completed'

def setUpIdGenerator(self):
  '''set up id generator '_generatePerDayId' on all application wich need it'''
  portal = self.getPortalObject()
  
  portal_type_list = ['Subscription Form', 'Declaration TVA']
  module_set_list = []

  for portal_type in portal_type_list:
    # get module
    module = self.getDefaultModule(portal_type=portal_type, default=None)
    
    if module is not None:
      # set id generator on module
      module.setIdGenerator('_generatePerDayId')
      module_set_list.append(module.getId())

  if len(module_set_list):
    return '- ID Generator set on modules :\n    * %s' \
        % '\n    * '.join(module_set_list)
  return 'No module have been set with ID Generator !'

def setUpInstance(self):
  '''call all other set up method to prepare the site for SAFI project'''
  message_list = []
  message_list.append(self.setUpEGovPas())
  message_list.append(self.setUpIdGenerator())
  message_list.append(self.publishAllWebPages())

  message_list.append('')
  message_list.append('Set Up sequence completed')
  return '\n'.join(message_list)

def publishAllWebPages(self):
  '''web pages are accessible by anonymous users only if they are published'''
  web_page_module = self.getPortalObject().web_page_module
  for web_page in web_page_module.contentValues():
    web_page.publish()
  return '- All Web pages are published'
