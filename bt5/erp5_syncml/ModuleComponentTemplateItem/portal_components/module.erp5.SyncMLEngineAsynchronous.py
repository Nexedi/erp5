# -*- coding: utf-8 -*-
## Copyright (c) 2012 Nexedi SARL and Contributors. All Rights Reserved.
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

from logging import getLogger

from erp5.component.mixin.SyncMLEngineMixin import SyncMLEngineMixin
from erp5.component.module.SyncMLConstant import ACTIVITY_PRIORITY
from Products.ERP5.ERP5Site import getSite
from six.moves import range

syncml_logger = getLogger('ERP5SyncML')


class SyncMLAsynchronousEngine(SyncMLEngineMixin):
  """ Implement synchronization engine using activities """


  def processClientSynchronization(self, syncml_request, subscription):
    """ Global method that process the package 3, 4 & 5 of SyncML DS Protocol """
    syncml_logger.info("xxx Client processing data from server (%s) xxx",
                       subscription.getSynchronizationState())
    syncml_logger.info("\tstatus %s, sync %s, final %s",
                       len(syncml_request.status_list),
                       len(syncml_request.sync_command_list),
                       syncml_request.isFinal)
    # We must log in with user defined
    subscription._loginUser()

    if syncml_request.alert_list:
      syncml_logger.warning("Got an alert from server not processed : %s",
                            syncml_request.alert_list)
      # Must check what server tell about database synchronization
      # and update the mode if required

    # Read status about databases & synchronizations
    self._readStatusList(syncml_request, subscription)

    if syncml_request.isFinal and \
      subscription.getSynchronizationState() == "initializing":
      # Server validated authentication ( must be done in readStatus list)
      # Client sends its modifications first before getting the one from server
      subscription.sendModifications()  # Worfklow action

    syncml_response = None
    tag = subscription.getRelativeUrl()

    # Do action according to synchronization state
    if subscription.getSynchronizationState() == "initializing":
      raise ValueError("Subscription still initializing, must not get here")
    elif subscription.getSynchronizationState() == "sending_modifications":
      # This is the package 3 of the sync process
      if subscription.getSyncmlAlertCode() in ("one_way_from_server",
                                               "refresh_from_server_only"):
        # We only get data from server
        syncml_response = subscription.generateBaseResponse()
        syncml_response.addFinal()
      else:
        # Make sure it is launched after indexation step
        self.runGetAndActivate(subscription=subscription, tag=tag,
                               after_method_id=("getAndIndex",
                                                "ERP5Site_indexSyncMLDocumentList"))
        syncml_logger.info("X-> Client is sendind modification in activities")
        # As we generated all activities to send data at once, process must not
        # go back here, go into processing state thus status will be applied and
        # if no sync command received, the process will just go on
      subscription.processSyncRequest()
    elif subscription.getSynchronizationState() == "processing_sync_requests":
      # In a second time, clients applied modifications from server
      # This is the package 5 of the protocol
      if syncml_request.isFinal or len(syncml_request.sync_command_list):
        # Either we get no sync command but a final tag notifying it is finished
        # Either we get sync command
        # Either we get both
        # Otherwise, it is just status message, no need to come here
        self.runApplySyncCommand(subscription=subscription,
                                 syncml_request=syncml_request,
                                 tag=tag)
        syncml_logger.info("-> Client apply command in %d activities",
                           len(syncml_request.sync_command_list))
      if syncml_request.isFinal:
        if not syncml_response:
          syncml_response = subscription.generateBaseResponse()
        # We got and process all sync command from server
        # notify it that all modifications were applied
        syncml_response.addFinal()
        # Send the message in activity after all sync command are applied
        subscription.activate(activity="SQLQueue",
                              priority=ACTIVITY_PRIORITY,
                              after_path_and_method_id =
                              (subscription.getPath(),
                               'applySyncCommand'),
                               after_tag=tag,).sendMessage(
                                 xml=bytes(syncml_response))
        # Synchronization process is now finished
        syncml_logger.info("\tClient finished processing messages from server")
        subscription.finish()
        syncml_response = None # XXX Do not resend the message
    else:
      raise ValueError("Unmanaged state of synchronization %s : %s"
                       % (subscription.getRelativeUrl(),
                          subscription.getSynchronizationState()))

    if subscription.getSynchronizationState() == "finished":
      # We do not expect anymore message from server
      # XXX Map of UID is not implemented
      syncml_logger.info('--- synchronization ended on the client side ---')
      # Remove authentication
      if subscription.getAuthenticationState() == 'logged_in':
        subscription.logout()
      subscription._edit(authenticated_user=None)

    if syncml_response:
      # Send the message in activity to prevent recomputing data in case of
      # transport failure
      syncml_logger.info("....client sending message....")
      subscription.activate(activity="SQLQueue").sendMessage(
        xml=bytes(syncml_response))


  def processServerSynchronization(self, subscriber, syncml_request):
    """
    Process the package 4 of the SyncML DS exchange
    """
    if False:  # pylint:disable=using-constant-test
      pass
      # not subscriber.checkCorrectRemoteMessageId(
      #   syncml_request.header['message_id']):
      # # Use memcached instead of storing data on subscription
      # syncml_logger.warning("Resending last message")
      # syncml_response = subscriber.getLastSentMessage("")  # XXX
    else:
      syncml_logger.info("xxx Server processing data from client xxx")
      syncml_logger.info("\tstatus %s, sync %s, final %s",
         len(syncml_request.status_list),
         len(syncml_request.sync_command_list),
         syncml_request.isFinal)
      # we log the user authenticated to do the synchronization with him
      if subscriber.getAuthenticationState() == 'logged_in':
        subscriber._loginUser()
      else:
        # Do not run sync if not authenticated
        raise ValueError("Authentication failed, impossible to sync data")

      # Apply command & send modifications
      # Apply status about object send & synchronized if any
      self._readStatusList(syncml_request, subscriber,
                                                 generate_alert=True)
      syncml_response = None
      tag = subscriber.getRelativeUrl()
      after_method_id = None
      if subscriber.getSynchronizationState() == "sending_modifications":
        if syncml_request.isFinal:
          # Do the final process after all other message are processed
          syncml_logger.info("server will finish sync in activity")
          subscriber.activate(after_method_id=('processServerSynchronization',
                                               'processClientSynchronization',
                                               'applySyncCommand'),
                              after_tag=(tag,
                                      subscriber.getParentValue().getRelativeUrl()),
                              activity="SQLQueue",
                              priority=ACTIVITY_PRIORITY+1).finishSynchronization()
        # We only got notifications, nothing to do
        if not len(syncml_request.sync_command_list):
          return
        # But we still might get sync command from activities
        # Order is not yet respected for the final sync command XXX to be reviewed

      # XXX We compute gid list so that we do not get issue with catalog
      # XXX This is a hack, if real datasynchronization is implemented
      # diff of objects must be computed before any process of data from
      # clients, which is not the case here
      # XXX To avoid issue with multiple message, this must be stored
      # in memcached instead of this variable
      if subscriber.getSynchronizationState() == "initializing":
        raise ValueError("Subscription still initializing, must not get here")
      if subscriber.getSynchronizationState() == "processing_sync_requests":
        # First server process sync commands : Pkg 3 of the sync process
        self.runApplySyncCommand(subscription=subscriber,
                                 syncml_request=syncml_request, tag=tag)
        syncml_logger.info("-> Server apply command in %d activities",
                           len(syncml_request.sync_command_list))
        if syncml_request.isFinal:
          # Server then sends its modifications
          subscriber.sendModifications()
          # Run indexation only once client have sent its modifications
          subscriber.indexSourceData()
          # Start to send modification only once we have processed
          # all message from client
          after_method_id=('processServerSynchronization',
                           'ERP5Site_indexSyncMLDocumentList')
          # XXX after tag might also be required to make sure all data are indexed
          tag = (tag, "%s_reset" % subscriber.getPath(),)
      # Do not continue in elif, as sending modifications is done in the same
      # package as sending notifications
      if subscriber.getSynchronizationState() == "sending_modifications":
        # In a second time, server send its modifications, package 4
        if subscriber.getSyncmlAlertCode() in ("one_way_from_client",
                                               "refresh_from_client_only"):
          # We only get data from client
          activity_created = False
        else:
          # Send all modification using activities
          activity_created = self.runGetAndActivate(subscription=subscriber,
                                                    after_method_id=after_method_id,
                                                    tag=tag)
          syncml_logger.info("X--> Server is sending modifications in activities %s", activity_created)
        if not activity_created:
          # Server has no modification to send to client, return final message
          syncml_logger.info("X-> Server sending final message")
          if not syncml_response:
            syncml_response = subscriber.generateBaseResponse()
          syncml_response.addFinal()

      if subscriber.getSynchronizationState() == "finished":
        raise ValueError('Should not get here')

    if syncml_response:
      subscriber.activate(activity="SQLQueue",
                          after_method_id=after_method_id,
                          after_tag=tag).sendMessage(
                            xml=bytes(syncml_response))

  def runGetAndActivate(self, subscription, tag, after_method_id=None):
    """
    Launch the browsing of GID that will call the generation of syncml commands
    """
    activate_kw = {
      'activity' : 'SQLQueue',
      'after_method_id' : after_method_id,
      'tag' :tag,
      'priority' :ACTIVITY_PRIORITY
      }
    pref = getSite().portal_preferences
    subscription.getAndActivate(
      callback="sendSyncCommand",
      activate_kw=activate_kw,
      packet_size=pref.getPreferredDocumentRetrievedPerActivityCount(),
      activity_count=pref.getPreferredRetrievalActivityCount(),
      )
    # then send the final message of this sync part
    if pref.getPreferredCheckDeleteAtEnd():
      subscription.activate(after_tag=tag,
                          priority=ACTIVITY_PRIORITY+1).getDeletedSyncMLData()
    else:
      subscription.activate(after_tag=tag,
                            priority=ACTIVITY_PRIORITY+1)._sendFinalMessage()
    return True


  def runApplySyncCommand(self, subscription, syncml_request, tag):
    """
    Launch the apply sync command in activity
    """
    send_response = subscription.getSyncmlAlertCode() != "refresh_from_client_only"
    if send_response and len(syncml_request.sync_command_list):
      # Generate a list of responses ID here to be scallable
      response_id_list = subscription.getNextMessageIdList(
        id_count=len(syncml_request.sync_command_list))
      response_id_list.reverse()
    else:
      response_id_list = [None for _ in
                          range(len(syncml_request.sync_command_list))]
    split = getSite().portal_preferences.getPreferredSyncActionPerActivityCount()
    if not split:  # We do not use activities
      if send_response:
        syncml_response = subscription.generateBaseResponse()
      else:
        syncml_response = None
      subscription.applyActionList(syncml_request, syncml_response)
      if syncml_response:
        subscription.activate(
          activity="SQLQueue",
          priority=ACTIVITY_PRIORITY,
          tag=subscription.getRelativeUrl()).sendMessage(xml=bytes(syncml_response))
    else:
      # XXX For now always split by one
      activate = subscription.activate
      activate_kw = {
        "activity" :"SQLQueue",
        "priority" : ACTIVITY_PRIORITY,
        "tag" : tag,
        "group_method_id" : None,
        "group_method_cost" : 1./float(split),
        }
      for action in syncml_request.sync_command_list:
        syncml_logger.info("---> launch action in activity %s", action)
        activate(**activate_kw).applySyncCommand(
          response_message_id=response_id_list.pop(),
          activate_kw=activate_kw,
          action=action,
          request_message_id=syncml_request.header["message_id"],
          simulate=False)
        # Response is sent by the activity
