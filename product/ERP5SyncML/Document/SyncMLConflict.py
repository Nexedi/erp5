# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Base import Base
from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet

class SyncMLConflict(Base):
  """
    object_path : the path of the obect
    keyword : an identifier of the conflict
    publisher_value : the value that we have locally
    subscriber_value : the value sent by the remote box

  """

  meta_type = 'ERP5 Conflict'
  portal_type = 'SyncML Conflict'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.SyncMLConflict )

  def _getPortalSynchronizationTool(self):
    return getToolByName(self.getPortalObject(), 'portal_synchronizations')

  def applyPublisherValue(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    p_sync.applyPublisherValue(self)

  def applyPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    p_sync.applyPublisherDocument(self)

  def getPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    return p_sync.getPublisherDocument(self)

  def getPublisherDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    return p_sync.getPublisherDocumentPath(self)

  def getSubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    return p_sync.getSubscriberDocument(self)

  def getSubscriberDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    return p_sync.getSubscriberDocumentPath(self)

  def applySubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = self._getPortalSynchronizationTool()
    p_sync.applySubscriberDocument(self)

  def applySubscriberValue(self, object=None):
    """
    get the domain
    """
    p_sync = self._getPortalSynchronizationTool()
    p_sync.applySubscriberValue(self, object=object)

  def getSubscriber(self):
    """
    Return the grand parent subscriber
    """
    return self.getParentValue().getParentValue()
