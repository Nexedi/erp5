# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2007 Nexedi SARL and Contributors. All Rights Reserved.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from Products.ERP5Security.ERP5GroupManager import ConsistencyError
from Products.ERP5Type import Permissions

#############################################################
## Define permissions on EGov modules
#############################################################

def setPermissionsOnEGovModule(self, portal_type_object):
  """
  This script sets the permissions on erp5 roles
  according to a procedure settings in the request hosting form
  """
  #XXX Complete Permissions class in Products.ERP5Type 
  #include all zope permissions
  aquired_permission_list= [ 'Access Transient Objects','Access arbitrary user session data'
                           , 'Access session data',  'Add Accelerated HTTP Cache Managers'
                           , 'Add Browser Id Manager','Add CMF Action Icons Tools'
                           , 'Add CMF Setup Tools','Add CMF Unique Id Tools'
                           , 'Add Configured CMF Sites','Add ERP5 Form Printouts'
                           , 'Add Plugin Registrys', 'Add RAM Cache Managers'
                           , 'Add ReStructuredText Documents','Add Session Data Manager'
                           , 'Add Site Roots','Add Temporary Folder', 'Add Transient Object Container'
                           , 'Add Virtual Host Monsters','Add Z Gadfly Database Connections'
                           , 'Add ZODB Mount Points','Add Zope Tutorials','Change Browser Id Manager'
                           , 'Change Session Data Manager', 'Create Transient Objects'
                           , 'Edit ReStructuredText','Manage Transient Object Container'
                           ]
  zope_permission_list =  [
                          'Access contents information','Access future portal content',
                          'Access inactive portal content','Add BTreeFolder2s',
                          'Add CMF Active Processs','Add CMF Caching Policy Managers',
                          'Add CMF Calendar Tools','Add CMF Core Tools',
                          'Add CMF Default Tools', 'Add CMF Sites',
                          'Add CMFActivity Tools','Add CMFCategory Tools',
                          'Add CMFMailIn Tools', 'Add Content Type Registrys','Add Cookie Crumblers',
                          'Add Database Methods','Add Documents, Images, and Files',
                          'Add ERP5 Filesystem Formulator Forms',
                          'Add ERP5 Forms','Add ERP5 OOo Templates',
                          'Add ERP5 PDF Forms','Add ERP5 PDF Templates',
                          'Add ERP5 Publications','Add ERP5 Reports',
                          'Add ERP5 Sites','Add ERP5 Subscriptions',
                          'Add ERP5 Tools','Add ERP5Catalog Tools',
                          'Add ERP5Form Tools',
                          'Add ERP5SyncML Tools','Add ERP5Type Tools',
                          'Add ExtFiles','Add ExtImages',
                          'Add External Methods','Add Filesystem Directory Views',
                          'Add Folders','Add Formulator Forms',
                          'Add LocalContents','Add LocalFolders',
                          'Add Localizers','Add MailHost objects',
                          'Add MessageCatalogs','Add MimetypesRegistry Tools',
                          'Add Page Templates','Add Pluggable Index',
                          'Add PortalTransforms Tools',
                          'Add Python Scripts','Add User Folders',
                          'Add Vocabularies', 'Add Z MySQL Database Connections',
                          'Add Z MySQL Deferred Database Connections','Add ZCatalogs',
                          'Add ZMailIn Clients','Add ZMailMessages',
                          'Add portal content','Add portal events',
                          'Add portal folders','Add portal member',
                          'Add portal topics','Change DTML Documents','Change DTML Methods',
                          'Change Database Connections','Change Database Methods',
                          'Change ExtFile/ExtImage','Change External Methods',
                          'Change Formulator Fields','Change Formulator Forms',
                          'Change Images and Files','Change Lock Information',
                          'Change Page Templates','Change Python Scripts',
                          'Change Versions', 'Change ZMailIn','Change ZMailMessages',
                          'Change bindings','Change cache managers',
                          'Change cache settings','Change configuration',
                          'Change local roles','Change permissions',
                          'Change portal events','Change portal topics',
                          'Change proxy roles','Copy or Move','Create class instances',
                          'Define permissions','Delete objects',
                          'Download ExtFile/ExtImage','Edit Factories',
                          'Edit target','FTP access','Import/Export objects',
                          'Join/leave Versions','List folder contents',
                          'List portal members','List undoable changes',
                          'Log Site Errors','Log to the Event Log',
                          'Mail forgotten password','Manage Access Rules',
                          'Manage Groups','Manage Selenium test cases',
                          'Manage Vocabulary','Manage WebDAV Locks','Manage Z Classes',
                          'Manage ZCatalog Entries','Manage ZCatalogIndex Entries',
                          'Manage languages','Manage messages',
                          'Manage portal','Manage properties',
                          'Manage users','Modify Cookie Crumblers',
                          'Modify portal content','Open/Close Database Connection',
                          'Open/Close Database Connections','Post mail to ZMailIn',
                          'Query Vocabulary','Reply to item','Request review',
                          'Review portal content','Save/discard Version changes',
                          'Search ZCatalog','Search for principals',
                          'Set own password','Set own properties',
                          'Take ownership','Test Database Connections',
                          'Translate Content','Undo changes',
                          'Use Database Methods','Use Factories',
                          'Use external editor','Use mailhost services',
                          'View','View History',
                          'View ZMailMessage','View management screens',
                          'WebDAV Lock items','WebDAV Unlock items',
                          'WebDAV access',
                          ]

  agent_permission_list = [Permissions.AccessContentsInformation, Permissions.AddPortalContent \
                                       ,Permissions.CopyOrMove, Permissions.ModifyPortalContent \
                                       ,Permissions.ListFolderContents,Permissions.View, 'View History' \
                                       ]
  view_permission_list= [ Permissions.AccessContentsInformation, Permissions.ListFolderContents  \
                        , Permissions.View ]

  citizen_role_list = ['role/citoyen', 'role/citoyen/national', 'role/citoyen/etranger']
  company_role_list = ['role/entreprise', 'role/entreprise/agence', 'role/entreprise/siege', 'role/entreprise/succursale']
  agent_role_list = ['role/gouvernement']

  role_permission_dict =  {'Agent':    agent_permission_list,
                           'Associate':[Permissions.AccessContentsInformation, Permissions.ListFolderContents \
                                       ,Permissions.View, Permissions.CopyOrMove, 'View History'  \
                                       ],
                           'Auditor':  [Permissions.AccessContentsInformation, Permissions.ListFolderContents  \
                                       ,Permissions.View, 'View History' \
                                       ],
                           'Assignee': [Permissions.AccessContentsInformation, Permissions.ListFolderContents \
                                       ,Permissions.CopyOrMove, Permissions.View, 'View History' \
                                       ],
                           'Assignor': [Permissions.AccessContentsInformation, Permissions.AddPortalContent \
                                       ,Permissions.AddPortalFolders, Permissions.CopyOrMove \
                                       ,Permissions.View, Permissions.ModifyPortalContent \
                                       ,Permissions.DeleteObjects, Permissions.ListFolderContents, 'View History' \
                                       ],
                           'Manager':  zope_permission_list
                          }

  #set acquired local role on the portal type
  portal_type_object.setTypeAcquireLocalRole(1)
  #Agent role should have access permissions on the portal type
  portal_type_object.manage_role(role_to_manage='Agent', permissions=view_permission_list)

  # if the procedure needs no authentification anonymous should access and add
  if portal_type_object is not None:
    step_authentication =  portal_type_object.getStepAuthentication()
    step_subscription =  portal_type_object.getStepSubscription()
    if not step_authentication: # and not step_subscription
      #Anonymous should have access, add, modify and delete permissions on the module
      self.manage_role(role_to_manage='Anonymous', permissions=agent_permission_list)
      #Anonymous should also have access to the portal type
      portal_type_object.manage_role(role_to_manage='Anonymous', permissions=view_permission_list)

  #set acquired permissionson the module
  self.manage_acquiredPermissions(aquired_permission_list)
  for (role, permission_list) in role_permission_dict.items():
    self.manage_role(role_to_manage=role, permissions=permission_list)
  

def getSecurityCategoryFromAssignment(self, base_category_list, user_name, 
    object, portal_type, child_category_list=[]):
  """
  This script returns a list of dictionaries which represent
  the security groups which a person is member of. It extracts
  the categories from the current user assignment.
  It is useful in the following cases:
  
  - associate a document (ex. an accounting transaction)
    to the division which the user was assigned to
    at the time it was created
  
  - calculate security membership of a user
  
  The parameters are
  
    base_category_list -- list of category values we need to retrieve
    user_name          -- string obtained from 
                                        getSecurityManager().getUser().getId()
    object             -- object which we want to assign roles to
    portal_type        -- portal type of object
  """
  category_list = []
  person_object_list = self.portal_catalog.unrestrictedSearchResults(\
                                portal_type='Person', reference=user_name)
  
  if len(person_object_list) != 1:
    if len(person_object_list) > 1:
      raise ConsistencyError("Error: There is more than one Person with reference '%s'" % user_name)
    else:
      # if a person_object was not found in the module, we do nothing more
      # this happens for example when a manager with no associated person 
      # object creates a person_object for a new user
      return []
  person_object = person_object_list[0].getObject()
  
  # We look for every valid assignments of this user
  assignment_list = person_object.contentValues(filter={'portal_type':'Assignment'})
  for assignment in assignment_list:
    if assignment.getValidationState() == 'open':
      category_dict = {}
      for base_category in base_category_list:
        category_value_list = assignment.getAcquiredValueList(base_category)
        if category_value_list:
          for category_value in category_value_list:
            if base_category in child_category_list:
              if category_value.getPortalType() not in \
                  ('Base Category', 'ERP5 Site'):
                while category_value.getPortalType() not in \
                    ('Base Category', 'ERP5 Site'):
                  category_dict.setdefault(base_category, []).append('%s*' % \
                      category_value.getRelativeUrl())
                  category_value = category_value.getParentValue()
              else:
                category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
            else:
              category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
      category_list.append(category_dict)
  
  return category_list


def getSecurityCategoryFromEntity(self, base_category_list, entity_name, 
    object, portal_type, child_category_list=None, portal_type_list=None):
  """
  This script returns a list of dictionaries which represent
  the security groups which a person is member of. It extracts
  the categories from the current user assignment.
  It is useful in the following cases:
  
  - associate a document (ex. an accounting transaction)
    to the division which the user was assigned to
    at the time it was created
  
  - calculate security membership of a user
  
  The parameters are
  
    base_category_list -- list of category values we need to retrieve
    entity_name          -- string obtained from 
                                        getSecurityManager().getUser().getId()
    object             -- object which we want to assign roles to
    portal_type_list   -- list of portal type to search the entity
  """
  if portal_type_list is None:
    portal_type_list = self.portal_type_list
  if child_category_list is None:
    child_category_list = []

  category_list = []
  object_list = self.portal_catalog.unrestrictedSearchResults(portal_type=portal_type_list, reference=entity_name)
  
  if len(object_list) != 1:
    if len(object_list) > 1:
      raise ConsistencyError("Error: There is more than one Entity with reference '%s'" % entity_name)
    else:
      # if a person_object was not found in the module, we do nothing more
      # this happens for example when a manager with no associated person 
      # object creates a person_object for a new user

      portal = self.getPortalObject()

      # this permit to get the module of the application. The goal is to
      # work with anonymous applications, even if they are not reindexed
      module_id = self.REQUEST.get('anonymous_module', None)
      if module_id:
        module =  getattr(portal, module_id, None)
        if module is not None:
          result = module._getOb(entity_name, None)
          if result is not None:
            object = result
          else:
            return []
      else:
        return []
  else:
    object = object_list[0].getObject()
  
  category_dict = {}
  for base_category in base_category_list:
    category_value_list = object.getAcquiredValueList(base_category)
    if category_value_list:
      for category_value in category_value_list:
        if base_category in child_category_list:
          if category_value.getPortalType() not in \
              ('Base Category', 'ERP5 Site'):
            while category_value.getPortalType() not in \
                ('Base Category', 'ERP5 Site'):
              category_dict.setdefault(base_category, []).append('%s*' % \
                  category_value.getRelativeUrl())
              category_value = category_value.getParentValue()
          else:
            category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
        else:
          category_dict.setdefault(base_category, []).append(category_value.getRelativeUrl())
  category_list.append(category_dict)
  
  return category_list



def getSecurityCategoryFromAssignmentParent(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=base_category_list)

def getSecurityCategoryFromAssignmentParentGroup(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=('group',))
 
def getSecurityCategoryFromAssignmentParentFunction(self, base_category_list,
                                       user_name, object, portal_type):
  return getSecurityCategoryFromAssignment(self, base_category_list,
                                       user_name, object, portal_type, child_category_list=('function',))

