##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.ERP5Type.Document.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir
from Products.ERP5.ERP5Globals import alarm_type_list
from Products.CMFCore import CMFCorePermissions
from DateTime import DateTime


from zLOG import LOG

class AlarmTool(BaseTool):
  """
  This tool will be usefull to  manage alarms. There's
  alarms everywhere in ERP5, and it is a nice idea to be able
  to manage all of them from a central point.

  Inside this tool we will have a way to retrieve all reports comings
  from Alarms,...
  """
  id = 'portal_alarms'
  meta_type = 'ERP5 Alarm Tool'
  portal_type = 'Alarm Tool'
  allowed_types = ('Supply Alarm Line',)

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainAlarmTool', _dtmldir )

  security.declareProtected( Permissions.ManagePortal , 'manageAlarmList' )
  manageAlarmList = DTMLFile( 'manageAlarmList', _dtmldir )

  manage_options = ( ( { 'label'   : 'Overview'
             , 'action'   : 'manage_overview'
             }
            , { 'label'   : 'All Alarms'
             , 'action'   : 'manageAlarmList'
             }
            )
           + Folder.manage_options
           )



  # API to manage alarms
  """
  This is what we should do:

  -- be able to see all alarms stored everywhere
  -- defines global alarms
  -- activate an alarm
  -- see reports
  -- see active alarms
  -- retrieve all alarms
  """

  security.declareProtected(Permissions.ModifyPortalContent, 'getAlarmList')
  def getAlarmList(self):
    """
    We retrieve thanks to the catalog the full list of alarms
    """
    catalog_search = self.portal_catalog(portal_type = alarm_type_list)
    alarm_list = map(lambda x:x.getObject(),catalog_search)
    return alarm_list

  security.declareProtected(Permissions.ModifyPortalContent, 'tic')
  def tic(self):
    """
    We will look at all alarms and see if they should be activated,
    if so then we will activate them.
    """
    current_date = DateTime()
    for alarm in self.getAlarmList():
      if alarm.isActive(): # do nothing if already active
        continue
      if alarm.getNextStartDate() <= current_date:
        alarm.activeSense()









#    security.declareProtected(Permissions.AccessContentsInformation, 'manageActiveSense')
#    def manageActiveSense(self, object_path, REQUEST=None):
#      """
#        Invokes all methods for object "object_path"
#      """
#      if type(object_path) is type(''):
#        object_path = tuple(object_path.split('/'))
#      object = self.unrestrictedTraverse(object_path)
#      object.activeSense()
#      if REQUEST is not None:
#        return REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), 'manageAlarmList'))
#
#    security.declareProtected(Permissions.AccessContentsInformation, 'manageSolve')
#    def manageSolve(self, object_path, REQUEST=None):
#      """
#        Invokes all methods for object "object_path"
#      """
#      if type(object_path) is type(''):
#        object_path = tuple(object_path.split('/'))
#      object = self.unrestrictedTraverse(object_path)
#      object.solve()
#      if REQUEST is not None:
#        return REQUEST.RESPONSE.redirect('%s/%s' % (self.absolute_url(), 'manageAlarmList'))
#





InitializeClass(AlarmTool)
