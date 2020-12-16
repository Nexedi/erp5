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
    return self.getPortalObject().portal_synchronizations

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyPublisherValue')
  def applyPublisherValue(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    document = self.getOriginValue()
    subscriber = self.getSubscriber()
    gid = subscriber.getGidFromObject(document)
    signature = subscriber.getSignatureFromGid(gid)
    signature.delConflict(self)
    if not signature.getConflictList():
      signature.resolveConflictWithMerge()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'applyPublisherDocument')
  def applyPublisherDocument(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    subscriber = self.getSubscriber()
    for c in self._getPortalSynchronizationTool().getConflictList(
        self.getOriginValue()):
      if c.getSubscriber() == subscriber:
        c.applyPublisherValue()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherDocument')
  def getPublisherDocument(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    return self.getOriginValue()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherDocumentPath')
  def getPublisherDocumentPath(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    return self.getOrigin()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocument')
  def getSubscriberDocument(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    return self.unrestrictedTraverse(
      self.getSubscriberDocumentPath())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocumentPath')
  def getSubscriberDocumentPath(self):
    """
    XXX-AUREL : Comment to be fixed
    """
    subscriber = self.getSubscriber()
    publisher_object = self.getOriginValue()
    conduit = subscriber.getConduit()
    publisher_xml = conduit.getXMLFromObjectWithId(publisher_object,
                       xml_mapping=subscriber.getXmlBindingGeneratorMethodId(),
                       context_document=subscriber.getPath())
    directory = publisher_object.aq_inner.aq_parent
    object_id = self._getPortalSynchronizationTool()._getCopyId(publisher_object)

    conduit.addNode(xml=publisher_xml, object=directory, object_id=object_id,
                    signature=self.getParentValue())
    subscriber_document = directory._getOb(object_id)
    for c in self._getPortalSynchronizationTool().getConflictList(
        self.getOriginValue()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue(document=subscriber_document)
    copy_path = subscriber_document.getPhysicalPath()
    return copy_path

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applySubscriberDocument')
  def applySubscriberDocument(self):
    """
    XXX Comment to be fixed
    """
    # XXX-AUREL : when we solve one conflict, it solves all conflicts related
    # to the same object ? is it the wanted behaviour ?
    subscriber = self.getSubscriber()
    for c in self._getPortalSynchronizationTool().getConflictList(
        self.getOriginValue()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'applySubscriberValue')
  def applySubscriberValue(self, document=None):
    """
    XXX Comment to be fixed
    """
    solve_conflict = 1
    if not document:
      document = self.getOriginValue()
    else:
      # This means an object was given, this is used in order
      # to see change on a copy, so don't solve conflict
      solve_conflict = False
    subscriber = self.getSubscriber()
    # get the signature:
    gid = subscriber.getGidFromObject(document)
    signature = subscriber.getSignatureFromGid(gid)
    # Import the conduit and get it
    conduit = subscriber.getConduit()
    conduit.updateNode(xml=self.getDiffChunk(), object=document,
                       force=True, signature=signature)
    if solve_conflict:
      signature.delConflict(self)
      if not signature.getConflictList():
        signature.resolveConflictWithMerge()

  def getSubscriber(self):
    """
    Return the grand parent subscriber
    """
    return self.getParentValue().getParentValue()
