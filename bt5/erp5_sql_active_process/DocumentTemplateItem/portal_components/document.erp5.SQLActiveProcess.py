# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2014 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from cPickle import dumps, loads
from AccessControl import ClassSecurityInfo
from MySQLdb import ProgrammingError
from Products.CMFActivity.ActiveProcess import ActiveProcess
from Products.CMFCore import permissions as CMFCorePermissions
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Globals import InitializeClass

class SQLActiveProcess(ActiveProcess):
  """
  Yet another Active Process class that stores Active Results in SQL database.
  """

  meta_type = 'CMF SQL Active Process'
  portal_type = 'SQL Active Process'

   # Declarative security
  security = ClassSecurityInfo()
  security.declareProtected(CMFCorePermissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                              )

  def __init__(self, *args, **kw):
    # No need to generate self.result_list.
    Base.__init__(self, *args, **kw)

  security.declareProtected(CMFCorePermissions.ManagePortal, 'postResult')
  def postResult(self, result):
    zPostResult = getattr(self, 'Base_zInsertIntoActiveResultTable')
    for _ in range(2):
      try:
        zPostResult(
          active_process_uid=self.getUid(),
          value=dumps(result)
        )
        break
      except ProgrammingError, error_value:
        if error_value[0] == 1146: # Table doesn't exist.
          getattr(self, 'Base_zCreateActiveResultTable')()
    else:
      raise error_value

  security.declareProtected(CMFCorePermissions.ManagePortal, 'getResultList')
  def getResultList(self, **kw):
    """
      Returns the list of results
    """
    zGetResultList = getattr(self, 'Base_zGetResultFromActiveResultTable')
    return [loads(e.value) for e in zGetResultList(active_process_uid=self.getUid())]

  security.declarePrivate('manage_beforeDelete')
  def manage_beforeDelete(self, item, container):
    zDeleteResultList = getattr(self, 'Base_zDeleteResultListFromActiveResultTable')
    zDeleteResultList(active_process_uid=self.getUid())

InitializeClass(SQLActiveProcess)
