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

from Products.ERP5Type.Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import permissions as CMFCorePermissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type import PropertySheet
from Products.ERP5Type.ConflictFree import ConflictFreeLog
from BTrees.OOBTree import OOBTree
from BTrees.Length import Length
from random import randrange
from .ActiveResult import ActiveResult

manage_addActiveProcessForm = DTMLFile('dtml/ActiveProcess_add', globals())

def addActiveProcess(self, id, title='', REQUEST=None, activate_kw=None, **kw):
  """Add a new Active Process.
  """
  o = ActiveProcess(id)
  if activate_kw is not None:
    o.__of__(self).setDefaultActivateParameterDict(activate_kw)
  o.uid = self.portal_catalog.newUid()
  self._setObject(id, o)
  o = self._getOb(id)
  if kw:
    o._edit(force_update=1, **kw)
  if REQUEST is not None:
    REQUEST['RESPONSE'].redirect( 'manage_main' )
  return o

class ActiveProcess(Base):
  """
      ActiveProcess is used to centralise interaction between multiple
      ActiveObject
      RENAME: ActiveResult
  """

  meta_type = 'CMF Active Process'
  portal_type = 'Active Process'
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
                    , PropertySheet.CategoryCore
                    , PropertySheet.ActiveProcess )

  # Declarative constructors
  constructors =   (manage_addActiveProcessForm, addActiveProcess)

  def __init__(self, *args, **kw):
    Base.__init__(self, *args, **kw)
    self.result_list = ConflictFreeLog()

  security.declareProtected(CMFCorePermissions.ManagePortal, 'postResult')
  def postResult(self, result):
    try:
      result_id = result.id
    except AttributeError:
      try:
        result_list = self.result_list
      except AttributeError:
        # BBB: self was created before implementation of __init__
        self.result_list = result_list = ConflictFreeLog()
      else:
        if type(result_list) is not ConflictFreeLog: # BBB: result_list is IOBTree
          # use a random id in order to store result in a way with
          # fewer conflict errors
          random_id = randrange(0, 10000 * (self.result_len.value + 1))
          while random_id in result_list:
            random_id += 1
          result_list[random_id] = result
          self.result_len.change(1)
          return
      result_list.append(result)
    else:
      try:
        self.result_dict[result_id] = result
      except AttributeError:
        self.result_dict = OOBTree({result.id: result})

  security.declareProtected(CMFCorePermissions.ManagePortal, 'postActiveResult')
  def postActiveResult(self, *args, **kw):
    return self.postResult(ActiveResult(*args, **kw))

  security.declareProtected(CMFCorePermissions.ManagePortal, 'getResultList')
  def getResultList(self, **kw):
    """
      Returns the list of results
    """
    # Improve this to include sort order XXX
    try:
      result_list = self.result_list
    except AttributeError:
      # BBB: self was created before implementation of __init__
      return []
    # XXX: ConflictFreeLog does not support indexing so cast to list for the
    #      moment, although this is inefficient and the caller never needs a
    #      copy (currently). Same for IOBTree.itervalues().
    if type(result_list) is not ConflictFreeLog: # BBB: result_list is IOBTree
      return list(result_list.values())
    return list(result_list)

  security.declareProtected(CMFCorePermissions.ManagePortal, 'getResultDict')
  def getResultDict(self, **kw):
    """
      Returns the result Dict
    """
    try:
      return self.result_dict
    except AttributeError:
      self.result_dict = result_dict = OOBTree()
      return result_dict

  security.declareProtected( CMFCorePermissions.View, 'hasActivity' )
  def hasActivity(self, **kw):
    """
      Tells if there is still some activities not finished attached to this
      process
    """
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None:
      return 0 # Do nothing if no portal_activities
    return activity_tool.hasActivity(None, active_process_uid = self.getUid(),
      **kw)

  security.declareProtected( CMFCorePermissions.View, 'hasErrorActivity' )
  def hasErrorActivity(self, **kw):
    """
      Tells if some attached activities are in a error
    """
    return self.hasActivity(only_invalid=True)

  def getCreationDate(self):
    """
      Define a Creation Date for an active process
      thanks to the start date
    """
    return self.getStartDate()

  def flush(self):
    # flush  activities related to this process
    activity_tool = getattr(self, 'portal_activities', None)
    if activity_tool is None:
      return # Do nothing if no portal_activities
    return activity_tool.flush(None, active_process = self, invoke = 0) # FLush


InitializeClass( ActiveProcess )
