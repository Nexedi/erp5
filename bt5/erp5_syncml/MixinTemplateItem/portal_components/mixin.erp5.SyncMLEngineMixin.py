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

import six
from logging import getLogger

from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.PluggableAuthService.interfaces.plugins import \
     IAuthenticationPlugin

from erp5.component.module.XMLSyncUtils import resolveSyncmlStatusCode, decode
from erp5.component.module.SyncMLMessage import SyncMLResponse
from erp5.component.module.SyncMLConstant import NULL_ANCHOR, ACTIVITY_PRIORITY, \
    SynchronizationError

syncml_logger = getLogger('ERP5SyncML')


class SyncMLEngineMixin(object):
  """
  Mixin class that holds generci methods used by engines
  """

  security = ClassSecurityInfo()


  security.declarePrivate('_readStatusList')
  def _readStatusList(self, syncml_request, domain, syncml_response=None,
                      generate_alert=False):
    """
    Read status (answer to command) and act according to them
    """
    sync_status_counter = 0
    path_list = []
    for status in syncml_request.status_list:
      if status["command"] == "SyncHdr":  # Check for authentication
        if domain.getSynchronizationState() != "initializing":
          raise SynchronizationError(
            "Authentication header found although it is already done")
        if status['status_code'] == \
            resolveSyncmlStatusCode('missing_credentials'):
          # Server challenged an authentication
          syncml_logger.info("\tServer required an authentication")
          if domain.getAuthenticationFormat() != \
              status['authentication_format'] or \
              domain.getAuthenticationType() != \
              status['authentication_type']:
            raise ValueError('Authentication definition mismatch between \
  client (%s-%s) and server (%s-%s)' % (domain.getAuthenticationFormat(),
                                        domain.getAuthenticationType(),
                                        status['authentication_format'],
                                        status['authentication_type']))
          # XXX Not working To Review !
          raise NotImplementedError("Adding credentials")
          # syncml_response = domain.generateBaseResponse()
          # syncml_response.addCredentialMessage(domain)
          # return syncml_response

        elif status['status_code'] == \
          resolveSyncmlStatusCode('invalid_credentials'):
          syncml_logger.error("\tClient authentication refused")
          raise ValueError("Server rejected client authentication")
        elif status['status_code'] == \
          resolveSyncmlStatusCode('authentication_accepted'):
          syncml_logger.error("\tClient authentication accepted")
        else:
          raise ValueError('Unknown status code %s for authentication'
                           % (status['status_code']))
      elif status["command"] == "Alert":  # Status about database synchronization
        # XXX Must check status for asked synchrozation
        # and must be done for command, not for
        # For now do nothing = say it is always OK
        syncml_logger.info("\tChecking database, will generate alert %s",
                           generate_alert)
      elif status["command"] in ('Add', 'Replace'):
        sync_status_counter += 1
        object_gid = status['source'] or status['target']
        if domain.getSyncmlAlertCode() == "refresh_from_client_only":
          # No signature is created for this kind of sync
          if status['status_code'] not in (resolveSyncmlStatusCode('success'),
                                           resolveSyncmlStatusCode('item_added')):
            raise ValueError("Impossible to synchronize object %s"
                             % (status['source'] or status['target']))
        else:
          signature = domain.getSignatureFromGid(object_gid)
          if not signature:  # XXX previous call must raise Key/Index-Error instead
            raise ValueError("Impossible to find signature in %s for gid %s"
                             % (domain.getPath(), object_gid))
          if status['status_code'] == resolveSyncmlStatusCode('conflict'):
            signature.changeToConflict()
            syncml_logger.error("\tObject in conflict %s",
                                status['source'] or status['target'])
          elif status['status_code'] == resolveSyncmlStatusCode(
              'conflict_resolved_with_merge'):
            # We will have to apply the update, and we should not care
            # about conflicts, so we have to force the update
            signature.noConflict()
            signature.setForce(True)
            syncml_logger.error("\tObject merged %s",
                                status['source'] or status['target'])
          elif status['status_code'] in (resolveSyncmlStatusCode('success'),
                                         resolveSyncmlStatusCode('item_added'),
                                         resolveSyncmlStatusCode(
                                           'conflict_resolved_with_client_command_winning')):
            syncml_logger.error("\tObject synchronized %s",
                                status['source'] or status['target'])
            if signature.getValidationState() != "no_conflict":
              signature.noConflict()
            signature.synchronize()
          elif status['status_code'] == resolveSyncmlStatusCode('chunk_accepted'):
            syncml_logger.info("Chunk was accepted for %s", object_gid)
          else:
            raise ValueError("Unknown status code : %r" % (status['status_code'],))
          # Index signature now to fill the data column
          path_list.append(signature.getPath())
      elif status['command'] == 'Delete':
        sync_status_counter += 1
        object_gid = status['source'] or status['target']
        signature = domain.getSignatureFromGid(object_gid)
        if status['status_code'] == resolveSyncmlStatusCode('success'):
          if signature:
            domain.z_delete_data_from_path(path=signature.getPath())
            domain._delObject(signature.getId())
          else:
            raise ValueError("Found no signature to delete for gid %s" %(object_gid,))
        else:
          raise ValueError("Unknown status code : %r" % (status['status_code'],))
        syncml_logger.error("\tObject deleted %s",
                            status['source'] or status['target'])

      else:
        raise ValueError("Unknown status command : %r" % (status['command'],))
    if len(path_list):
      domain.ERP5Site_indexSyncMLDocumentList(path_list)
    return sync_status_counter

  #
  # Method used by the SyncML DS Client (ie Subscription)
  #
  def initializeClientSynchronization(self, subscription):
    """ Client Initialisation package to server (pkg 1)

    Client must inform the server which database it want to synchronize
    and which type og synchronization is desired.

    Options that can be included in this package :
    - authentification
    - service capabilities (PUT)

    Note that this package can be combined with package 3, this is the case of
    'Sync without separate initialization'. Client may implement it. This is not
    done here but can be a way of improvement to decrease number of messages
    exchanged.
    """
    syncml_logger.info('--- Starting synchronization on client side : %s ---',
                       subscription.getPath())
    if not subscription.getSynchronizationState() == "initializing":
      # This can be called many time in sync init when credentials failed
      subscription.initialize()  # Worflow action
    subscription.createNewAnchor()

    # The user launching the synchronization is save so that when we get an
    # request from the the server, it get process with this user
    # XXX this can be managed using credentials like on server part ?
    user_id = getSecurityManager().getUser().getId()
    subscription._loginUser(user_id)
    subscription._edit(authenticated_user=user_id)
    if subscription.getAuthenticationState() != 'logged_in':
      # Workflow action
      subscription.login()

    subscription.indexSourceData(client=True)

    # Create the package 1
    syncml_response = SyncMLResponse()

    # Create the header part
    session_id = subscription.generateNewSessionId()
    subscription.setSessionId(session_id)
    header_kw = {'session_id': session_id,
                 'message_id': subscription.getNextMessageId(),
                 'target': subscription.getUrlString(),
                 'source': subscription.getSubscriptionUrlString(),
                 # Include credentials
                 'user_id': subscription.getUserId(),
                 'password': subscription.getPassword(),
                 'authentication_format':
                   subscription.getAuthenticationFormat(),
                 'authentication_type':
                   subscription.getAuthenticationType()
                 }
    syncml_response.addHeader(**header_kw)

    # Create the body part which consists of :
    # - one alert command per database to sync, each containing its anchors
    # - one put command (optional)
    # - one get command if client when device capabilities of server (optional)
    syncml_response.addBody()
    # Here we only run one synchronization at a time, so only one alert command
    # is created
    syncml_response.addAlertCommand(
      alert_code=subscription.getSyncmlAlertCode(),
      target=subscription.getDestinationReference(),
      source=subscription.getSourceReference(),
      last_anchor=subscription.getLastAnchor(),
      next_anchor=subscription.getNextAnchor())

    # Generate the put command
    syncml_response.addPutMessage(subscription)

    return syncml_response


  #
  # Methods used by the SyncML DS Server (ie Publication in erp5)
  #
  def processServerInitialization(self, publication, syncml_request, subscriber,
                                  alert_dict):
    """
    This is the method called on server side when initializing a
    new synchronization.

    This method is called by client on server. Server will generate
    Package 2 messages based on what it got from clients

    Server will returns :
    - Header with credential if authentication is needed
    - Status answering the authentication & alert commands of the client
    - Alert command for each database to be synchronized
   (Following messages/commands are not implemented)
    - Status about the device information if sent by client
    - Result element containing device information if client requested it
    - Put command if the server want to send its service capabilities
    - Get command if the server want to get the client service capabilities
    """
    if subscriber is None:
      # first synchronization, create the subscribtion object under the publication
      # it will be used to store status of synchronization
      syncml_logger.info("\t\tCreating a subscriber")
      # Define source/destination on subscriber as it will be used by protocol
      # Source is server/publication, Destination is client/subscription
      subscriber = publication.createUnrestrictedSubscriber(
        # Publication information
        source_reference=alert_dict['target'],
        subscription_url_string=syncml_request.header['target'],
        # Subscription information
        destination_reference=alert_dict['source'],
        url_string=syncml_request.header['source'],
        # Other information copied from publication
        xml_binding_generator_method_id=
          publication.getXmlBindingGeneratorMethodId(),
        conduit_module_id=publication.getConduitModuleId(),
        list_method_id=publication.getListMethodId(),
        gid_generator_method_id=publication.getGidGeneratorMethodId(),
        source=publication.getSource(),
        synchronization_id_generator_method_id =
          publication.getSynchronizationIdGeneratorMethodId(), # XXX Deprecated
        is_activity_enabled = publication.getIsActivityEnabled(),
        # Protocol information
        syncml_alert_code="syncml_alert_code/%s" %(alert_dict["code"],),
        session_id=syncml_request.header['session_id'],
        last_message_id=syncml_request.header['message_id'],
        )
    else:
      if subscriber.getSessionId() == syncml_request.header['session_id']:
        # We do not start a new session migth be a duplicated message
        if not subscriber.checkCorrectRemoteMessageId(
            syncml_request.header["message_id"]):
          syncml_logger.warning("Resending last init message")
          return subscriber.getLastSentMessage("")
      else:
        # XXX must check that previous session ended before
        subscriber.edit(session_id=syncml_request.header['session_id'])

    if alert_dict["code"] in ('two_way', 'slow_sync',
                              'one_way_from_server',
                              'refresh_from_client_only',
                              'one_way_from_client'):
      # Make sure we update configuration based on publication data
      # so that manual edition is propagated
      # XXX Must check all properties that must be setted
      subscriber.setXmlBindingGeneratorMethodId(
        publication.getXmlBindingGeneratorMethodId())
      subscriber.setConduitModuleId(publication.getConduitModuleId())
    else:
      raise NotImplementedError('Alert code not handled yet: %r'
                                % syncml_request.alert['data'])


    syncml_logger.info('--- Starting synchronization on server side : %s in mode %s ---',
                       publication.getPath(), alert_dict["data"])
    # at the begining of the synchronization the subscriber is not authenticated
    if subscriber.getAuthenticationState() == 'logged_in':
      subscriber.logout()

    if not subscriber.getSynchronizationState() == "initializing":
      # This can be called many time in sync init when credentials failed
      subscriber.initialize()  # Workflow action

    # XXX it must be known that here we do a server layer authentication,
    # The database layer authentication is not implemented, although we defined
    # credentials on pub/sub documents
    authentication_code = None
    if not len(syncml_request.credentials):
      syncml_logger.info("\tReceived message without credential, will ask for them")
      authentication_code = "missing_credentials"
    else:
      # First try to authenticate the client
      if syncml_request.credentials['type'] == "syncml:auth-md5":
        # MD5 authentication is not supported
        raise NotImplementedError("MD5 authentication not supported")

      if syncml_request.credentials['type'] == publication.getAuthenticationType():
        decoded = decode(syncml_request.credentials['format'],
                         syncml_request.credentials['data'])
        if decoded and b':' in decoded:
          login, password = decoded.split(b':')
          if six.PY3:
            login = login.decode()
            password = password.decode()
          # TODO: make it work for users existing anywhere
          user_folder = publication.getPortalObject().acl_users
          for _, plugin in user_folder._getOb('plugins')\
              .listPlugins(IAuthenticationPlugin):
            if plugin.authenticateCredentials(
                {'login': login, 'password': password}) is not None:
              subscriber.login()
              syncml_logger.info("\tServer accepted authentication for user %s",
                                 login)
              authentication_code = 'authentication_accepted'
              subscriber._loginUser(login)
              subscriber._edit(authenticated_user=login)
              break
            else:
              # When authentication is invalid, a second try is possible for the client
              # if header_kw["message_id"] == 1:
              #   authentication_code = 'missing_credentials'
              # else:
              authentication_code = 'invalid_credentials'
              syncml_logger.error("\tServer rejected authentication for %s", login)
        else:
          # if header_kw["message_id"] == 1:
          #   authentication_code = 'missing_credentials'
          # else:
          authentication_code = 'invalid_credentials'
          syncml_logger.warning(
            "\tCredentials does not look like auth-basis, decoded value is '%s,'",
            decoded)
      else:
        # To complete, must send a challenge message
        syncml_logger.warning(
          "\tAuthentication type does not math, from client '%s', from server '%s'",
            syncml_request.credentials['type'],
            publication.getAuthenticationType())
        authentication_code = 'missing_credentials'


    # Build the xml message for the Sync initialization package
    syncml_response = SyncMLResponse()
    syncml_response.addHeader(session_id=subscriber.getSessionId(),
                             message_id=subscriber.getNextMessageId(),
                             target=syncml_request.header['source'],
                             source=publication.getUrlString())
    # syncml body
    syncml_response.addBody()

    if authentication_code == 'authentication_accepted':
      sync_type_validation_code = "success"
      sync_type = alert_dict["data"]

      # Now check the alert command sent by client
      if alert_dict['code'] == 'slow_sync' and \
          subscriber.getNextAnchor() != NULL_ANCHOR:
        # If slow sync, then resend everything
        syncml_logger.info("\tClient requested a slow sync, signatures are reset on server side")
        subscriber.resetAllSignatures()
        subscriber.resetAnchorList()
      elif subscriber.getNextAnchor() != alert_dict['last_anchor']:
        # Anchor does not match, must start a slow sync
        syncml_logger.warning("\tAnchor does not match on server, \
           received is %s, stored %s. Will start a slow sync",
           alert_dict['last_anchor'],
           subscriber.getNextAnchor())
        sync_type_validation_code = "command_failed" # Error 500
        sync_type = 'slow_sync'
      else:
        # Last synchronization went fine
        subscriber.setNextAnchor(alert_dict['next_anchor'])

      # Two status message must be sent here
      # - One answering about the authentication
      # - One answering about the database synchronization status
      # Then one aler message per database is send, client must
      # follow sync type in this alert message is status was KO

      # Status about authentication
      syncml_response.addStatusMessage(
        message_reference=syncml_request.header['message_id'],
        command_reference=0,  # answer to a header
        command='SyncHdr',
        status_code=authentication_code,
        target=syncml_request.header['target'],
        source=syncml_request.header['source']
        )

      # Status about database sync
      syncml_response.addStatusMessage(
        message_reference=syncml_request.header['message_id'],
        command_reference=alert_dict['command_id'],
        command='Alert',
        status_code=sync_type_validation_code,
        target=alert_dict['target'],
        source=alert_dict['source'],
        anchor=alert_dict['next_anchor'])

      # one alert message for each database to sync
      syncml_response.addAlertCommand(
        alert_code=sync_type,
        target=alert_dict['target'],
        source=alert_dict['source'],
        last_anchor=subscriber.getLastAnchor(),
        next_anchor=subscriber.getNextAnchor())

      # Server get sync commands from client first
      subscriber.processSyncRequest()
    else:
      # Add a status message with a challenge command
      syncml_response.addChallengeMessage(
        message_reference=syncml_request.header['message_id'],
        target=syncml_request.header['source'],
        source=syncml_request.header['target'],
        authentication_format=publication.getAuthenticationFormat(),
        authentication_type=publication.getAuthenticationType(),
        authentication_code=authentication_code)

    # Generate and send the message
    syncml_response.addFinal()
    if subscriber.getIsActivityEnabled():
      subscriber.activate(
        activity="SQLQueue",
        after_tag = "%s_reset" % subscriber.getPath(),
        # Wait for all reset to be done
        # before starting sync
        priority=ACTIVITY_PRIORITY,
        tag=publication.getRelativeUrl()).sendMessage(xml=bytes(syncml_response))
    else:
      subscriber.sendMessage(xml=bytes(syncml_response))

    return syncml_response
