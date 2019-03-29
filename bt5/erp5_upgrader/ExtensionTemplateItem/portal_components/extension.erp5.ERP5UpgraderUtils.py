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
import os


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
  except Exception as e:
    # Is it required include the trace back
    return 'Script %s fail to run, Exception: %s , message: %s .' % (method_id, e.__class__, e )
  if len(integrity_result) > 0:
    return '%s : \n - %s ' % (method_id, '\n - '.join(integrity_result))

def ERP5Site_dumpWorkflowChainByPortalType(self, REQUEST=None):
  # This method outputs the workflow chain by portal type
  # ---
  # {"Account": ['account_workflow', "edit_workflow"]}
  # ---
  #
  if REQUEST:
    raise RuntimeError("You can not call this script from the url")
  workflow_tool = self.getPortalObject().portal_workflow
  cbt = workflow_tool._chains_by_type
  ti = workflow_tool._listTypeInfo()
  chain_by_type_dict = {}
  for t in ti:
    id = t.getId()
    title = t.Title()
    if title == id:
      title = None
    if cbt is not None and cbt.has_key(id):
      chain = sorted(cbt[id])
    else:
      chain = ['(Default)']
    chain_by_type_dict.setdefault(id, []).extend(chain)
  return chain_by_type_dict