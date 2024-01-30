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
from erp5.component.module.SyncMLConstant import SynchronizationError

syncml_logger = getLogger('ERP5SyncML')

class SyncMLSynchronousEngine(SyncMLEngineMixin):
  """
  Implement a synchronous engine wait for IO
  """

  def processClientSynchronization(self, syncml_request, subscription):
    """ Global method that process the package 3 of SyncML DS Protocol """

    syncml_logger.info("xxx Client processing data from server xxx")
    syncml_logger.info("\tstatus %s, sync %s, final %s",
                       len(syncml_request.status_list),
                       len(syncml_request.sync_command_list),
                       syncml_request.isFinal)
    # Process sync logged in
    subscription._loginUser()

    if syncml_request.alert_list:
      syncml_logger.warning("Got an alert from server not processed : %s",
                            syncml_request.alert_list)
      # Must check what server tell about database synchronization
      # and update the mode if required

    syncml_response = subscription.generateBaseResponse()

    # Read & apply status about databases & synchronizations
    try:
      self._readStatusList(syncml_request, subscription, syncml_response)
    except SynchronizationError:
      # Looks like we process an already received message
      syncml_logger.error("%s does no process packet due to error",
                          subscription.getRelativeUrl())
      return

    if syncml_request.isFinal and \
      subscription.getSynchronizationState() == "initializing":
      # Client sends its modifications first
      # before getting the one from server
      subscription.sendModifications()  # Worfklow action

    # Do action according to synchronization state
    if subscription.getSynchronizationState() == "initializing":
      raise ValueError("Subscription still initializing, must not get here")
    elif subscription.getSynchronizationState() == "sending_modifications":
      # Client always sent its modifications first
      if subscription.getSyncmlAlertCode() in ("one_way_from_server",
                                               "refresh_from_server_only"):
        # We only get data from server
        finished = True
        syncml_response.addFinal()
      else:
        finished = subscription._getSyncMLData(syncml_response=syncml_response,
                                               min_gid=None, max_gid=None)
        if finished:
          # Delete message will contain final tag
          subscription.getDeletedSyncMLData(syncml_response=syncml_response)

      syncml_logger.info("-> Client sendind modification, finished %s", finished)
      if finished:
        # Will then start processing sync commands from server
        subscription.processSyncRequest()

    elif subscription.getSynchronizationState() == "processing_sync_requests":
      # In a second time, clients applied modifications from server
      if subscription.getSyncmlAlertCode() == "refresh_from_server_only":
        syncml_response=None
      subscription.applyActionList(
        syncml_request=syncml_request,
        syncml_response=syncml_response,
        simulate=False)
      syncml_logger.info("-> Client sending %s notification of object synchronized",
                         syncml_response.sync_confirmation_counter)
      if syncml_request.isFinal:
        # Notify that all modifications were applied
        syncml_response.addFinal()
        # Synchronization process is now finished
        subscription.finish()
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

    # Send the message
    subscription.sendMessage(xml=bytes(syncml_response))

    return bytes(syncml_response)


  def processServerSynchronization(self, subscriber, syncml_request):
    """
    Process the package 4 of the SyncML DS exchange
    """
    if not subscriber.checkCorrectRemoteMessageId(
        syncml_request.header['message_id']):
      syncml_logger.warning("Resending last message")
      syncml_response = subscriber.getLastSentMessage("")  # XXX
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
      # XXX This can be called on subscription instead
      syncml_response = subscriber.generateBaseResponse()

      # Apply status about object send & synchronized if any
      self._readStatusList(syncml_request, subscriber, syncml_response, True)

      if syncml_request.isFinal:
        if subscriber.getSynchronizationState() == \
              "waiting_notifications":
          # We got the last notifications from clients
          subscriber.finish()
        elif subscriber.getSynchronizationState() != \
              "processing_sync_requests":
          raise SynchronizationError("Got final request although not waiting for it")

      # XXX We compute gid list so that we do not get issue with catalog
      # XXX This is a hack, if real datasynchronization is implemented
      # diff of objects must be computed before any process of data from
      # clients, which is not the case here
      # XXX To avoid issue with multiple message, this must be stored
      # in memcached instead of this variable
      if subscriber.getSynchronizationState() == "initializing":
        raise ValueError("Subscription still initializing, must not get here")
      if subscriber.getSynchronizationState() == "processing_sync_requests":
        # First server process sync commands from client
        if subscriber.getSyncmlAlertCode() == "refresh_from_client_only":
          # No need to send back hack XXX this is erp5 specific optimisation
          # as no signature is created
          subscriber.applyActionList(
            syncml_request=syncml_request,
            syncml_response=None,
            simulate=True)
        else:
          subscriber.applyActionList(
            syncml_request=syncml_request,
            syncml_response=syncml_response,
            simulate=True)

        syncml_logger.info("-> Server sending %s notification of sync",
                           syncml_response.sync_confirmation_counter)
        if syncml_request.isFinal:
          # Server will now send its modifications
          subscriber.sendModifications()
          # Run indexation only once client has sent its modifications
          subscriber.indexSourceData()

      # Do not continue in elif, as sending modifications is done in the same
      # package as sending notifications
      if subscriber.getSynchronizationState() == "sending_modifications":
        # In a second time, server send its modifications
        if subscriber.getSyncmlAlertCode() in ("one_way_from_client",
                                               "refresh_from_client_only"):
          # We only get data from client
          finished = True
          syncml_response.addFinal()
        else:
          finished = subscriber._getSyncMLData(syncml_response=syncml_response,
                                               min_gid=None, max_gid=None)
          if finished:
            # Delete message will contain final tag
            subscriber.getDeletedSyncMLData(syncml_response=syncml_response)

        syncml_logger.info("-> Server sendind data, finished %s", finished)
        if finished:
          subscriber.waitNotifications()
          # Do not go into finished here as we must wait for
          # notifications from client
      if subscriber.getSynchronizationState() == "finished":
        syncml_logger.info('--- synchronization ended on the server side ---')
        if subscriber.getAuthenticationState() == 'logged_in':
          subscriber.logout()
        subscriber._edit(authenticated_user=None,
                         remaining_object_path_list=None)
        syncml_response = b""  # XXX This is expected by unit test only
        # Body must be sent even when there is no data to notify client

    subscriber.sendMessage(xml=bytes(syncml_response))

    # Return message for unit test purpose
    return bytes(syncml_response)
