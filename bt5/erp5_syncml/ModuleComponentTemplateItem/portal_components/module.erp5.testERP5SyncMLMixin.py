# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

class TestERP5SyncMLMixin(ERP5TypeTestCase):
  """
  Mixin class that hold methods
  usefull to manage synchronizations
  """
  def getSynchronizationTool(self):
    """
    Return the tootl
    """
    return self.portal.portal_synchronizations

  def addSynchronizationUser(self, user_id="syncml", password="syncmlpass"):
    """
    Add a user in acl_users that will be used for synchronization
    """
    acl_users = self.portal.acl_users
    if not acl_users.getUserById(user_id):
      acl_users._doAddUser(user_id, password, ['Manager'], [])
    return (user_id, password)

  def updateSynchronizationURL(self, url=None, object_list=None):
    """
    Update the url defined on publication & subscription to the one
    used by runUnitTest
    """
    if not url:
      url = self.portal.absolute_url()
    if not object_list:
      object_list = self.portal.portal_synchronizations.objectValues()
    for sync in object_list:
      if sync.getPortalType() == "SyncML Subscription":
        sync.edit(url_string=url,
                  subscription_url_string=url,
                  )
      else:
        sync.edit(url_string=url)

  def updateAuthenticationCredentials(self, user_id, password, object_list=None):
    """
    Update subscripbtion to use specific authentication credentials
    """
    if not object_list:
      object_list = self.portal.portal_synchronizations.objectValues(
        portal_type="SyncML Subscription")
    for sync in object_list:
      sync.edit(user_id=user_id,
                password=password)

  def validatePublicationList(self, publication_list=None):
    """
    Validate if possible publications
    if no publication given, validate them all
    """
    if not publication_list:
      publication_list = self.portal.portal_synchronizations.objectValues(
        portal_type="SyncML Publication")
    for publication in publication_list:
      if self.portal.portal_workflow.isTransitionPossible(publication, 'validate'):
        publication.validate()

  def validateSubscriptionList(self, subscription_list=None):
    """
    Validate if possible subscriptions
    if no subscription given, validate them all
    """
    if not subscription_list:
      subscription_list = self.portal.portal_synchronizations.objectValues(
        portal_type="SyncML Subscription")
    for subscription in subscription_list:
      if self.portal.portal_workflow.isTransitionPossible(subscription, 'validate'):
        subscription.validate()