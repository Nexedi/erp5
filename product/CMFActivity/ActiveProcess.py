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

from zLOG import LOG

manage_addActiveProcessForm=DTMLFile('dtml/ActiveProcess_add', globals())

def addActiveProcess( self, id, title='', REQUEST=None ):
    """
        Add a new Category and generate UID by calling the
        ZSQLCatalog
    """
    sf = ActiveProcess( id )
    sf._setTitle(title)
    self._setObject( id, sf )
    sf = self._getOb( id )
    sf.reindexObject()
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)

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
                      , PropertySheet.Folder )

    # Declarative constructors
    constructors =   (manage_addActiveProcessForm, addActiveProcess)

    # Base methods
    def _generateNewId(self):
      """
        Generate a new result id for internal storage
      """
      try:
        my_id = int(self.getLastId())
      except:
        my_id = 1
      while self.result_list.has_key(my_id):
        my_id = my_id + 1
      self._setLastId(str(my_id)) # Make sure no reindexing happens

      return my_id

    security.declareProtected(CMFCorePermissions.ManagePortal, 'postResult')
    def postResult(self, result):
      if not hasattr(self, 'result_list'):
        self.result_list = IOBTree()
      self.result_list[self._generateNewId()] = result

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

InitializeClass( ActiveProcess )
