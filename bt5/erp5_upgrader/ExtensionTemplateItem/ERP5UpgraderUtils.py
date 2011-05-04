# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#                    Ivan Tyagov <ivan@nexedi.com>
#                    Yusei TAHARA <yusei@nexedi.com>
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

from App.config import getConfiguration
from Products.ERP5Type.Log import log
from Products.CMFActivity.ActiveResult import ActiveResult
from time import sleep
import os
from Acquisition import aq_base

def ERP5Site_editERP5SiteProperty(self, prop, value):
  """
    The ERP5Site miss this method, so we implement.
  """
  portal = self.getPortalObject()
  method = portal._setProperty
  if portal.hasProperty(prop):
    method = portal._updateProperty
  method(prop, value)
  return True

def ERP5Site_restartZopeInstance(self):
  """
    Zope must be restart after update the Products or Software
    But the restart into one activity, will make the activity always
    fail and with the server will be restart many times.

    This method use a flag to define if the server was already restarted.
    If yes, the flag is removed and the restart will be ignored.

    This method should be run into a single activity to prevent rollback
    other parts.
  """
  import Lifetime
  Lifetime.shutdown(1,fast=1)
  log("Zope Restart was launched.")

  active_result = ActiveResult()
  active_result.edit(summary="Zope Restart",
                     severity=0,
                     detail="Zope was restart Sucessfully.")
  return active_result

def ERP5Site_clearActivities(self):
  """
    This method is used to recreated the activities keeping the 
    previous activities from one activity. The issue related to recreate 
    the Activity tables from one activity is that the activity (this method) 
    is also recreated, so it is kept for ever. 

    This method use a flag to define if the portal already recreated the 
    activities table. If yes, the flag is removed and the recreation will 
    be ignored.

    This method should be run into a single activity to prevent some action
    be excetured many times other parts.
  """
  instance_home = getConfiguration().instancehome
  flag_fs_path = instance_home + "/ACTIVITY_RECREATE_FLAG"
  log("Start to Clear activities.")
  if not os.path.exists(flag_fs_path):
    try:
      flag = open(flag_fs_path, 'w+')
      log("Clear Activities")
      self.getPortalObject().portal_activities.manageClearActivities(keep=1)
      active_result = ActiveResult()
      active_result.edit(summary="Activities Recreated",
                       severity=0,
                       detail="Activities Tables was recreated Sucessfully.")
      return active_result
    except:
      os.remove(flag_fs_path)
      raise 

  os.remove(flag_fs_path)
  return

def ERP5Site_runVerificationScript(self, method_id):
  """ Run a Python Script return the method. This should avoid raise error, 
      even one intergrity verification script raise error, and provide good
      information.
  """
  method = getattr(self.getPortalObject(), method_id, None)
  if method is None:
    return 'Script %s was not Found!' % (method_id)
  try:
    integrity_result = method()
  except Exception, e:
    # Is it required include the trace back
    return 'Script %s fail to run, Exception: %s , message: %s .' % (method_id, e.__class__, e )
  if len(integrity_result) > 0:
    return '%s : \n - %s ' % (method_id, '\n - '.join(integrity_result))

def ERP5Site_changeAuthoredDocumentListOwnership(self, old_owner, new_owner):
  """
    Change owneship for all documents in the system belonging to 
    an user (i.e. represented by user_name/reference).
  """
  # Move import to here prevents the raise error when this External 
  # Be imported during the upgrade.
  from Products.ERP5Type.Utils import _setSuperSecurityManager
  from AccessControl.SecurityManagement import setSecurityManager
  from Products.ERP5Security.ERP5UserManager import SUPER_USER

  result = []
  orginal_security_manager = _setSuperSecurityManager(self, SUPER_USER)
  portal = self.getPortalObject()
  user_folder = portal.acl_users

  new_owner_as_user = user_folder.getUserById(new_owner).__of__(user_folder)
  document_list = portal.portal_catalog.unrestrictedSearchResults(owner = old_owner)
  for document in document_list:
    document = document.getObject()
    #  change document ownership
    document.changeOwnership(new_owner_as_user)
    # fix local roles
    for item in document.get_local_roles():
      user = item[0]
      role_list = item[1]
      if user == old_owner:
        # replace old Owner with new One
        document.manage_delLocalRoles((old_owner,))
        document.manage_setLocalRoles(new_owner, role_list)
    result.append(document.getRelativeUrl())
    # finally reindex document
    document.reindexObject()

  # restore security
  setSecurityManager(orginal_security_manager)
  return dict(old_owner = old_owner, \
              new_owner = new_owner, \
              changed_document_list = result)
