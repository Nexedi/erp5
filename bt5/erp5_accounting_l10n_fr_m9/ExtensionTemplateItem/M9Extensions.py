##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
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

from zExceptions import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.User import UnrestrictedUser


def AccountingTransactionLine_setGroupingReference(self,
           grouping_reference, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized('Cannot be called through the web')
  self.setGroupingReference(grouping_reference)

def AccountingTransaction_setPaymentDate(self,
           payment_date, REQUEST=None):
  if REQUEST is not None:
    raise Unauthorized('Cannot be called through the web')
  
  old_sm = getSecurityManager()
  try:
    newSecurityManager(None, UnrestrictedUser(
                                  'system_user',
                                  'system_user',
                                  ['Manager'],
                                  []).__of__(self.acl_users))
    self.setPaymentConditionPaymentDate(payment_date)
  finally:
    setSecurityManager(old_sm)

def Invoice_afterFollowUp(self, sci):
  """Workflow script to set the recovery status without security check."""
  invoice = sci['object']
  follow_up_count = sci.getPortal().portal_workflow.getInfoFor(
                        sci['object'], 'follow_up_count')

  if follow_up_count == 0:
    invoice.setRecoveryStatus('R0')
  elif follow_up_count == 1:
    invoice.setRecoveryStatus('R1')
  elif follow_up_count == 2:
    invoice.setRecoveryStatus('R2')
  elif follow_up_count == 3:
    invoice.setRecoveryStatus('R3')
  else:
    assert 0, 'invalid follow up count %s' % follow_up_count

def Invoice_afterPause(self, sci):
  """Workflow script to set the recovery status without security check."""
  invoice = sci['object']
  invoice.setRecoveryStatus(sci.kwargs['recovery_status'])

def Invoice_setRecoveryStatus(self, value, REQUEST=None):
  """Workflow script to set the recovery status without security check."""
  if REQUEST is not None:
    raise Unauthorized('Cannot be called through the web')
  self.setRecoveryStatus(value)

def Base_setShortTitle(self, value, REQUEST=None):
  """Set the short title of a document, without the need to have the Modify
  portal content on this document."""
  if REQUEST is not None:
    raise Unauthorized('Cannot be called through the web')
  self.setShortTitle(value)

def PaymentTransaction_setAggregateValue(self, value,
                activate_kw=None, REQUEST=None):
  """Set the aggregate relation between a Payment Transaction and the Transfer.
  Supports passing activate_kw for reindexing.
  """
  if REQUEST is not None:
    raise Unauthorized('Cannot be called through the web')
  self._setAggregateValue(value)
  if activate_kw is None:
    activate_kw = {}
  self.activate(activate_kw=activate_kw).recursiveImmediateReindexObject()
  
