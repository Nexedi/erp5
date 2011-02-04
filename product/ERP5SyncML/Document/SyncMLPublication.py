# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

from Products.ERP5SyncML.Document.SyncMLSubscription import SyncMLSubscription
from Products.ERP5Type import Permissions
from AccessControl import ClassSecurityInfo
from Products.ERP5SyncML.SyncMLConstant import ACTIVITY_PRIORITY
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod

class SyncMLPublication(SyncMLSubscription):
  """Reply to request from SyncML clients,
  Serve data to be synchronized.
  """

  meta_type = 'ERP5 Publication'
  portal_type = 'SyncML Publication' # may be useful in the future...

  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriber')
  def getSubscriber(self, subscription_url):
    """
    return the subscriber corresponding the to subscription_url
    """
    subscriber = None
    for subscription in self.contentValues(portal_type='SyncML Subscription'):
      if subscription.getSubscriptionUrlString() == subscription_url:
        subscriber = subscription
        break
    return subscriber

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberList')
  def getSubscriberList(self):
    """
      Get the list of subscribers
    """
    return self.contentValues(portal_type='SyncML Subscription')

  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetSubscriberList')
  def resetSubscriberList(self):
    """
      Reset all subscribers
    """
    id_list = []
    for subscriber in self.contentValues(portal_type='SyncML Subscription'):
      subscriber.resetSignatureList()
      id_list.append(subscriber.getId())
    self.activate(activity='SQLQueue',
                  tag=self.getId(),
                  after_tag=id_list,
                  priority=ACTIVITY_PRIORITY).manage_delObjects(id_list)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConflictList')
  def getConflictList(self, *args, **kw):
    """
      Return the list of conflicts from all subscribers
    """
    conflict_list = []
    for subscriber in self.getSubscriberList():
      conflict_list.extend(subscriber.getConflictList())
    return conflict_list

  security.declarePrivate('createUnrestrictedSubscriber')
  @UnrestrictedMethod
  def createUnrestrictedSubscriber(self, **kw):
    """Create a subscriber even if user is anonymous
    """
    kw['portal_type'] = 'SyncML Subscription'
    return self.newContent(**kw)
