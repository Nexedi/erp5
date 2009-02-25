############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Vincent Pelletier <vincent@nexedi.com>
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

from ZEO.ClientStorage import ClientStorage
from zLOG import LOG, WARNING, INFO

LAST_COMMITED_TID_PROPERTY_ID = '_last_commited_tid'

# Hook tpc_finish's hook method.
# New hook must be a local method because it must access tpc_finish's "self"
# and original hook.

LOG('TIDStorage',INFO,'Monkey patching ClientStorage.tpc_finish and ClientStorage.getLastCommitedTID')

original_tpc_finish = ClientStorage.tpc_finish
def tpc_finish(self, txn, f=None):
  def saveTIDOnInstance(tid):
    if f is not None:
      f(tid)
    setattr(self, LAST_COMMITED_TID_PROPERTY_ID, tid)
  return original_tpc_finish(self, txn, f=saveTIDOnInstance)
ClientStorage.tpc_finish = tpc_finish

def getLastCommitedTID(self):
  """
    Return last commited tid for this storage, or None if no transaction
    was commited yet.
  """
  return getattr(self, LAST_COMMITED_TID_PROPERTY_ID, None)
ClientStorage.getLastCommitedTID = getLastCommitedTID

