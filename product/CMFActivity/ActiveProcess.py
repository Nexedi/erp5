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

from Acquisition import aq_base
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type import PropertySheet
from BTrees.IOBTree import IOBTree
from Products.CMFActivity.ActiveObject import DISTRIBUTABLE_STATE, INVOKE_ERROR_STATE, VALIDATE_ERROR_STATE

from zLOG import LOG

manage_addActiveProcessForm=DTMLFile('dtml/ActiveProcess_add', globals())

def addActiveProcess(self, id, title='', REQUEST=None, activate_kw=None, **kw):
    """
        Add a new Category and generate UID by calling the
        ZSQLCatalog. This code is inspired from Document Constructor
        in Products.ERP5Type.Utils and should probably be merged.
    """
    o = ActiveProcess(id)
    if activate_kw is not None:
      o.__of__(self).setDefaultActivateParameters(**activate_kw)
    o.uid = self.portal_catalog.newUid()
    self._setObject(id, o)
    o = self._getOb(id)
    if kw: o._edit(force_update=1, **kw)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( 'manage_main' )

class ActiveProcess(Base):
    """
        ActiveProcess is used to centralise interaction between multiple ActiveObject
        RENAME: ActiveResult
    """

    meta_type='CMF Active Process'
    portal_type='Active Process'
    isPortalContent = 0 
    isRADContent = 1
    icon = None

    # Declarative security
    security = ClassSecurityInfo()
    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'manage_editProperties',
                              'manage_changeProperties',
                              'manage_propertiesForm',
                                )

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.SimpleItem
                      , PropertySheet.Folder 
                      , PropertySheet.ActiveProcess )

    # Declarative constructors
    constructors =   (manage_addActiveProcessForm, addActiveProcess)

    # Base methods
    def _generateNewId(self):
      """
        Generate a new result id for internal storage
      """
      try:
        my_id = int(self.getLastId())
      except TypeError:
        my_id = 1
      while self.result_list.has_key(my_id):
        my_id = my_id + 1
      self._setLastId(str(my_id)) # Make sure no reindexing happens

      return my_id

    security.declareProtected(CMFCorePermissions.ManagePortal, 'postResult')
    def postResult(self, result):
      if not hasattr(self, 'result_list'):
        self.result_list = IOBTree()
      result.id = self._generateNewId()
      self.result_list[result.id] = result

    security.declareProtected(CMFCorePermissions.ManagePortal, 'getResultList')
    def getResultList(self, **kw):
      """
        Returns the list of results
      """
      if not hasattr(self, 'result_list'):
        self.result_list = IOBTree()
      # Improve this to include sort order XXX
      return self.result_list.values()

#     security.declareProtected(CMFCorePermissions.ManagePortal, 'getErrorListText')
#     def getResultListText(self):
#       """
#         Returns the list of errors as text
#       """
#       return '\n'.join(map(lambda x:repr(x), self.error_list))
#
    security.declareProtected(CMFCorePermissions.ManagePortal, 'activateResult')
    def activateResult(self, result):
      if result not in (None, 0, '', (), []):
        #self.activate().postError(result)
        self.postResult(result) # Until we get SQLQueue
      # If result is a callable, then use it to propagate result (... ??? )
      #if callable(result):
      #  return self.activateResult(Result(self, 'activateResult',result())

    security.declareProtected( CMFCorePermissions.View, 'hasActivity' )
    def hasActivity(self, **kw):
      """
        Tells if there is still some activities not finished attached to this process
      """
      activity_tool = getattr(self, 'portal_activities', None)
      if activity_tool is None: return 0 # Do nothing if no portal_activities
      return activity_tool.hasActivity(None, active_process = self, **kw)

    security.declareProtected( CMFCorePermissions.View, 'hasErrorActivity' )
    def hasErrorActivity(self, **kw):
      """
        Tells if some attached activities are in a error 
      """
      return self.hasActivity(processing_node = INVOKE_ERROR_STATE)

    security.declareProtected( CMFCorePermissions.View, 'hasInvalidActivity' )
    def hasInvalidActivity(self, **kw):
      """
        Tells if an object if active
      """
      return self.hasActivity(processing_node = VALIDATE_ERROR_STATE)

    def start():
      # start activities related to this process
      pass

    def stop():
      # stop activities related to this process
      pass

    def flush(self):
      # flush  activities related to this process
      activity_tool = getattr(self, 'portal_activities', None)
      if activity_tool is None: return # Do nothing if no portal_activities
      return activity_tool.flush(None, active_process = self, invoke = 0) # FLush


InitializeClass( ActiveProcess )
