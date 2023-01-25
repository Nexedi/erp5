# -*- coding: utf-8 -*-
## Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from os import path
from logging import getLogger, Formatter

from AccessControl import ClassSecurityInfo

from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5Type.Globals import InitializeClass
from erp5.component.module.SyncMLConstant import ACTIVITY_PRIORITY, \
    SynchronizationError
from erp5.component.module.SyncMLMessage import SyncMLRequest
from erp5.component.module.SyncMLEngineSynchronous import SyncMLSynchronousEngine
from erp5.component.module.SyncMLEngineAsynchronous import SyncMLAsynchronousEngine
from Products.ERP5.ERP5Site import getSite

synchronous_engine = SyncMLSynchronousEngine()
asynchronous_engine = SyncMLAsynchronousEngine()

# Logging channel definitions
# Main logging channel
syncml_logger = getLogger('ERP5SyncML')
# Direct logging to "[instancehome]/log/ERP5SyncML.log", if this
# directory exists. Otherwise, it will end up in root logging
# facility (ie, event.log).
from App.config import getConfiguration
instancehome = getConfiguration().instancehome
if instancehome is not None:
  log_directory = path.join(instancehome, 'log')
  if path.isdir(log_directory):
    from Signals import Signals
    from ZConfig.components.logger.loghandler import FileHandler
    log_file_handler = FileHandler(path.join(log_directory,
                                                'ERP5SyncML.log'))
    # Default zope log format string borrowed from
    # ZConfig/components/logger/factory.xml, but without the extra "------"
    # line separating entries.
    log_file_handler.setFormatter(Formatter(
      "%(asctime)s %(levelname)s %(name)s %(message)s",
      "%Y-%m-%dT%H:%M:%S"))
    Signals.registerZopeSignals([log_file_handler])
    syncml_logger.addHandler(log_file_handler)
    syncml_logger.propagate = 0


def checkAlertCommand(syncml_request):
  """
  This parse the alert commands received and return a
  dictionnary mapping database to sync mode
  """
  database_alert_list = []
  # XXX To be moved on engine
  search = getSite().portal_categories.syncml_alert_code.searchFolder
  for alert in syncml_request.alert_list:
    if alert["data"] == "222":
      # 222 is for asking next message, do not care
      continue
    # Retrieve the category
    # XXX Categories must be redefined, ID must be code, not title so
    # that we can drop the use of searchFolder
    alert_code_category_list = search(reference=alert['data'])
    if len(alert_code_category_list) == 1:
      alert_code_category = alert_code_category_list[0].getId()
    else:
      # Must return (405) Command not allowed
      raise NotImplementedError("Alert code is %s, got %s category" %
                                (alert['data'],
                                 len(alert_code_category_list)))
    # Copy the whole dict & add the category id
    alert["code"] = alert_code_category
    database_alert_list.append(alert)

  return database_alert_list



class SynchronizationTool(BaseTool):
  """ This tool implements the SyncML Protocol

  SyncML Protocol defines how to synchronize data between clients and server.

  Here is a mapping of the specification with the implementation in this tool :
  - client are subscriptions
  - server are publications
  - change log are managed through the use of signatures. A signature contains
    the last data sent and which was successfully synchronized. When running a
    new synchronization new data is compared with the one stored in signature
    to detect changes.
  """
  meta_type = 'ERP5 Synchronizations'
  portal_type = 'Synchronization Tool'
  title = 'Synchronizations'

  id = "portal_synchronizations"

  security = ClassSecurityInfo()

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConflictList')
  def getConflictList(self, context=None):
    """
    Retrieve the list of all conflicts
    Here the list is as follow :
    [conflict_1,conflict2,...] where conflict_1 is like:
    ['publication',publication_id,object.getPath(),property_id,
    publisher_value,subscriber_value]
    """
    conflict_list = []
    for publication in self.searchFolder(portal_type='SyncML Publication'):
      for result in publication.searchFolder(
          portal_type='SyncML Subscription'):
        subscriber = result.getObject()
        sub_conflict_list = subscriber.getConflictList()
        for conflict in sub_conflict_list:
          if context is None or conflict.getOriginValue() == context:
            conflict_list.append(conflict.__of__(subscriber))
    for result in self.searchFolder(portal_type='SyncML Subscription'):
      subscription = result.getObject()
      sub_conflict_list = subscription.getConflictList()
      for conflict in sub_conflict_list:
        if context is None or conflict.getOriginValue() == context:
          conflict_list.append(conflict.__of__(subscription))
    return conflict_list

  security.declareProtected(Permissions.AccessContentsInformation,
                             'getDocumentConflictList')
  def getDocumentConflictList(self, context=None):
    """
    Retrieve the list of all conflicts for a given document
    Well, this is the same thing as getConflictList with a path
    """
    return self.getConflictList(context)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberDocumentVersion')
  def getSubscriberDocumentVersion(self, conflict, docid):
    """
    Given a 'conflict' and a 'docid' refering to a new version of a
    document, applies the conflicting changes to the document's new
    version. By so, two differents versions of the same document will be
    available.
    Thus, the manager will be able to open both version of the document
    before selecting which one to keep.
    """
    subscriber = conflict.getSubscriber()
    publisher_object = conflict.getOrigineValue()
    publisher_xml = self.getXMLObject(
                       object=publisher_object,
                       xml_mapping=subscriber.getXmlBindingGeneratorMethodId())
    directory = publisher_object.aq_parent
    object_id = docid
    if object_id in directory.objectIds():
      directory._delObject(object_id)  # XXX Why not manage_delObjects ?
      # Import the conduit and get it
      conduit = subscriber.getConduit()
      conduit.addNode(xml=publisher_xml, object=directory,
                      object_id=object_id,
                      signature=conflict.getParentValue())
      subscriber_document = directory._getOb(object_id)
      for c in self.getConflictList(conflict.getOriginValue()):
        if c.getSubscriber() == subscriber:
          c.applySubscriberValue(document=subscriber_document)
      return subscriber_document

  # XXX- ?
  def _getCopyId(self, document):
    directory = document.aq_inner.aq_parent
    if directory.getId() != 'portal_repository':
      document_id = document.getId() + '_conflict_copy'
      if document_id in directory.objectIds():
        directory._delObject(document_id)  # XXX manage_delObjects ?
    else:
      repotool = directory
      docid = repotool.getDocidAndRevisionFromObjectId(document.getId())[0]
      new_rev = repotool.getFreeRevision(docid) + 10  # make sure it's not gonna provoke conflicts
      document_id = repotool._getId(docid, new_rev)
    return document_id

  #
  # XXX-Aurel : the following methods must be moved to a specific part that
  # manages protocols to send/receive messages
  #
  security.declarePublic('readResponse')
  def readResponse(self, text='', sync_id=None, from_url=None):
    """
    We will look at the url and we will see if we need to send mail, http
    response, or just copy to a file.
    """
    syncml_logger.info('readResponse sync_id %s, text %s', sync_id, text)
    if text:
      # we are still anonymous at this time, use unrestrictedSearchResults
      # to fetch the Subcribers
      catalog_tool = self.getPortalObject().portal_catalog.unrestrictedSearchResults
      syncml_request = SyncMLRequest(text)

      # It is assumed that client & server does not share the same database ID
      # (source_reference); this must be checked using constraint
      for publication in catalog_tool(portal_type='SyncML Publication',
                                      source_reference=sync_id,
                                      validation_state='validated'):
        if publication.getUrlString() == syncml_request.header['target']:
          # Do not process in activity first checking, a message ordering
          # is required by protocol specification, only use activity when no
          # race condition can happen (ie no final tag)

          # XXX For now do in activity otherwise we never answer the HTTP request
          # directly and so it ends with client/server stuck waiting for answer and
          # on the other side we are doing an http request to send them
          if publication.getIsActivityEnabled():
            return self.activate(
              activity="SQLQueue",
              tag=publication.getRelativeUrl(),
              priority=ACTIVITY_PRIORITY-1).processServerSynchronization(
                publication.getPath(), text)
          else:
            return self.processServerSynchronization(publication.getPath(), text)

      for subscription in catalog_tool(portal_type='SyncML Subscription',
                                       source_reference=sync_id,
                                       validation_state='validated'):
        if subscription.getSubscriptionUrlString() == syncml_request.header['target']:
          if subscription.getIsActivityEnabled():
            return self.activate(activity="SQLQueue",
                                 priority=ACTIVITY_PRIORITY-1).processClientSynchronization(
                                   subscription.getPath(),text)
          else:
            return self.processClientSynchronization(subscription.getPath(), text)

      # XXX maybe it is better to generate a syncml error message
      raise ValueError("Impossible to find a pub/sub to process message %s:%s"
                       % (sync_id, syncml_request.header['target']))

    # we use from only if we have a file
    elif isinstance(from_url, basestring):
      if from_url.startswith('file:'):
        filename = from_url[len('file:'):]
        xml = None
        try:
          stream = open(filename, 'r')
        except IOError:
          # XXX-Aurel : Why raising here make unit tests to fail ?
          # raise ValueError("Impossible to read file %s, error is %s"
          #                  % (filename, msg))
          pass
        else:
          xml = stream.read()
          stream.close()
        syncml_logger.debug('readResponse xml from file is %s', xml)
        if xml:
          return xml
  #
  # End of part managing protocols
  #

  #
  # Following methods are related to server (Publication)
  #
  security.declarePrivate('processServerSynchronization')
  def processServerSynchronization(self, publication_path, msg=None):
    """
      This is the synchronization method for the server
    """
    # Read the request from the client
    publication = self.unrestrictedTraverse(publication_path)
    if publication.getIsActivityEnabled():
      engine = asynchronous_engine
    else:
      engine = synchronous_engine

    if msg is None:
      # Read message from file
      msg = self.readResponse(from_url=publication.getUrlString(),
                                     sync_id=publication.getSourceReference())
    if msg is not None:
      syncml_request = SyncMLRequest(msg)
      #syncml_logger.info("\tXML received from client %s" %(str(syncml_request)))

      # Get the subscriber
      subscription_url = syncml_request.header['source']
      subscriber = publication.getSubscriber(subscription_url)  # XXX method to be renamed

      # Alert commands are generated at initialization phase or when client ask
      # for the remaining messages
      database_alert_list = checkAlertCommand(syncml_request)
      assert len(database_alert_list) <= 1, "Multi-databases sync no supported"
      if len(database_alert_list):
        # We are initializing the synchronization
        if subscriber and subscriber.getSynchronizationState() not in \
              ("not_running", "initializing", "finished"):
          syncml_logger.error(
            'Trying to start a synchronization on server side : %s although synchronisation is already running',
            subscriber.getPath())
          # Prevent initilisation if sync already running
          return
        syncml_response = engine.processServerInitialization(
          publication=publication,
          syncml_request=syncml_request,
          subscriber=subscriber,
          alert_dict=database_alert_list[0])
      else:
        if not subscriber:
          raise ValueError("First synchronization message must contains alert command")
        else:
          # Let engine manage the synchronization
          try:
            return engine.processServerSynchronization(subscriber, syncml_request)
          except SynchronizationError:
            return
    else:
      # This must be implemented following the syncml protocol, not with this hack
      raise NotImplementedError("Starting sync process from server is forbidden")

    # Return message for unit test purpose
    return str(syncml_response)

  #
  # Following methods are related to client (subscription)
  #
  security.declareProtected(Permissions.ModifyPortalContent,
                            'processClientSynchronization')
  def processClientSynchronization(self, subscription_path, msg=None):
    """
      This is the synchronization method for the client

      This is the first method called to launch a synchronization process
    """
    subscription = self.unrestrictedTraverse(subscription_path)
    if subscription.getIsActivityEnabled():
      engine = asynchronous_engine
    else:
      engine = synchronous_engine

    if msg is None and subscription.getSubscriptionUrlString('').find('file') >= 0:
      # XXX This is a hack for unit test only, must be removed
      msg = self.readResponse(sync_id=subscription.getDestinationReference(),
                              from_url=subscription.getSubscriptionUrlString())


    if msg is None:
      # This is a synchronization initialisation call
      # Even if call on asynchronous engine, this will not use activities
      syncml_response = engine.initializeClientSynchronization(subscription)
    else:
      syncml_request = SyncMLRequest(msg)

      if not subscription.checkCorrectRemoteMessageId(
          syncml_request.header['message_id']):
        # Message already processed, resend the response
        # XXX How to make sure we send the good last response ?
        raise NotImplementedError
      else:
        return engine.processClientSynchronization(syncml_request, subscription)

    # Send the message
    if subscription.getIsActivityEnabled():
      subscription.activate(
        after_tag="%s_reset" %(subscription.getPath(),),
        activity="SQLQueue",
        after_method_id=('processServerSynchronization',
                         'getAndIndex',
                         'SQLCatalog_indexSyncMLDocumentList'),
        priority=ACTIVITY_PRIORITY,
        tag=subscription.getRelativeUrl()).sendMessage(str(syncml_response))
    else:
      subscription.sendMessage(str(syncml_response))

    return str(syncml_response)

InitializeClass(SynchronizationTool)
