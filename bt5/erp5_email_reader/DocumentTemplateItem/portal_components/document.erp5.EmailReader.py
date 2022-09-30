# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
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

# ERP5 imports
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.ExternalSource import ExternalSource
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.Cache import transactional_cached

# IMAP imports
import imaplib

# Transaction Management
from Shared.DC.ZRDB.TM import TM

# LOGs
from zLOG import LOG, ERROR, INFO

_MARKER = []

# Plugin server classes
class MailServer(TM):
  """
    Base Class for all Mail Server Plugins
  """
  def __init__(self, host, user, password, port=None):
    raise NotImplementedError

  def getMessageUIDList(self, message_folder=None):
    raise NotImplementedError

  def getMessageFolderList(self):
    raise NotImplementedError

  def getMessageData(self, uid, message_folder=None):
    raise NotImplementedError

class IMAPSServer(MailServer):
  """
    Implements a transactional IMAP SSL server
    connector. In case of transaction failure, connections
    are closed and logged out.

    XXX - Rewrite everything to use UID!
  """
  successful_select = False
  # Code inspired from ActivityBuffer
  _p_oid=_p_changed=_registered=None

  def __init__(self, host, user, password, port=993):
    """
      Instanciate a new IMAPS server
      and keep track of all parameters
    """
    self.host = host
    self.user = user
    self.password = password
    self.port = port
    self.message_folder = _MARKER
    self.server = imaplib.IMAP4_SSL(self.host) # XXX What about port ?
    self.server.login(user, password) # What about failures ?
    response, message_count = self.server.select() # XXX response not taken into account
                                                   # XXX What about failures ?
    TM._register(self) # Register transaction once everything is ready
                       # XXX - This leaves a small probability of failure (to be researched)
                       # If the transaction is cancelled just before

  def _finish(self, *ignored):
    """
      Make sure connection is closed and logged out
      at the end of a transaction
    """
    LOG('IMAPSServer', 0, '_finish %r' % (self,))
    try:
      # Try to close and logout
      if self.successful_select:
        self.server.close()
      self.server.logout()
    except:
      LOG('IMAPSServer', ERROR, "exception during _finish",
          error=True)
      raise

  def _abort(self, *ignored):
    """
      Make sure connection is closed and logged out
      at the end of an aborted transaction
    """
    LOG('IMAPSServer', 0, '_abort %r' % (self,))
    try:
      # Try to close and logout
      if self.successful_select:
        self.server.close()
      self.server.logout()
    except:
      LOG('IMAPSServer', ERROR, "exception during _abort",
          error=True)
      raise

  def _selectMessageFolder(self, message_folder):
    """
      Select the given message folder
    """
    if self.message_folder is _MARKER or self.message_folder != message_folder:
      self.message_folder = message_folder
      if message_folder:
        LOG('message_folder',0, message_folder)
        response, message_count = self.server.select(message_folder) # XXX response not taken into account
      else:
        response, message_count = self.server.select() # XXX response not taken into account
      LOG('server.select folder %s' % message_folder, INFO, "Response: %s" % response)
      if response in ('OK', 'EXISTS'): # is this right status list XXX
        self.successful_select = True
        self.message_count = message_count[0]
        LOG('server.select folder %s' % message_folder, INFO, "Count: %s" % self.message_count)
      else:
        raise ValueError(message_count[0]) # Use a better exception here XXX
    return self.message_count

  def getMessageUIDList(self, message_folder=None):
    """
      Returns the list of UID for all messages in a given folder.

      message_folder -- the name of the folder to ingest messages from
    """
    self._selectMessageFolder(message_folder)
    query = "ALL"
    response, message_id_list = self.server.uid('search', None, query) # XXX - reponse not taken into account
    result = message_id_list[0].split()
    result.reverse() # Download the latest first
    return result

  def getMessageFolderList(self):
    """
      Returns the list of folders of the current server

      XXX - Danger - because we are in multithreaded environment
      there is a risk here that the selected mailbox changes during
      execution (hopefully not with current implementation which creates
      on IMAPServer instance per transaction)
    """
    result = []
    response, folder_list = self.server.list() # XXX - reponse not taken into account
    for folder in folder_list:
      if folder is not None:
        # strings are of the form '(\\HasChildren) "." "INBOX.Business.OpenBrick.Prospects"'
        #                           folder_flags    delimeter folder
        folder_flags, folder_name = folder.split(') "', 1)
        folder_flags = folder_flags.strip('(')
        folder_delimiter, folder_name = folder.split('" ', 1)
        folder_name = folder_name.strip('"')
        result.append(folder_name)
    return result

  def getMessageData(self, uid, message_folder=None):
    """
      Returns the message data for a given UID in a given folder

      uid -- the IMAP UID of the message to ingest

      message_folder -- the name of the folder to ingest messages from
    """
    self._selectMessageFolder(message_folder)
    response, message = self.server.uid('fetch', uid, '(RFC822)') # XXX - reponse not taken into account
    if response != 'OK':
      LOG('getMessageData', INFO,
                        "Unable to fetch the message with UID %s in folder %s \n"\
                        "Response was: %s message list: %s" % (uid, message_folder,
                        str(response), str(message)))
      return None
    #LOG('getMessageData %s' % uid, INFO, (response, message))
    message = message[0]
    if message:
      return message[1]
    else:
      LOG('getMessageData', ERROR,
                        "None message with UID %s in folder %s \n"\
                        "Response was: %s message list: %s" % (uid, message_folder,
                        str(response), str(message)))
      return None

class IMAPServer(IMAPSServer):
  """
    Implements a transactional IMAP server
    connector. In case of transaction failure, connections
    are closed and logged out.
  """
  def __init__(self, host, user, password, port=143):
    IMAPSServer.__init__(self, host, user, password, port=port)

class POPSServer(MailServer):
  """
    Implements a transactional POP SSL server
    connector. In case of transaction failure, connections
    are closed and logged out.
  """
  # XXX - Not implemented yet

class POPServer(POPSServer):
  def __init__(self, host, user, password, port=143):
    POPSServer.__init__(self, host, user, password, port=port)


class EmailReader(ExternalSource):
  """
    This class implements an IMAP reader. It crawls email
    content in specific folders (defined by the user) and:
      - invokes message processors on every message

    Message processors can for example:
      - copy folder name as subject
      - move a message to another folder
      - copy a message to CRM
      - extract message content

    It inherits from ExternalSource to provide crawling ability (url_string = IMAP server)
    although this design approach is still uncertain (XXX)

    TODO:
      - make server classes resistant to network failure
        (ie. if DNS is down, there is no reason to set activity to -2
         since the next crawl will download again)
      - should we subscribe to IMAP folders?
      - if the imaplib using UID really? probably not, only sequence numbers
        API must thus be revised
      - refactor using the future merged architecture for crawling
        and synchronization (ie. crawling = sync)
      - consider integration with ERP5 Connect approach and data
        tiling as in data publica, instead of ad hoc implementation
  """
  # CMF Type Definition
  meta_type = 'ERP5 Email Reader'
  portal_type = 'Email Reader'
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Url
                    , PropertySheet.Login
                    , PropertySheet.ExternalDocument
                    )

  # Global values
  MAX_UID_LIST_SIZE = 100 # The number of messages to ingest at once

  ### Implementation - generic part - IMAP independent
  security.declareProtected(Permissions.ModifyPortalContent, 'crawlContent')
  def crawlContent(self):
    """
      Starts the reading process by invoking ingestMessageList on every
      folder
    """
    list_activity_tag = "IMAPReader_ingestMessageList_%s" % self.getRelativeUrl()
    available_folder_list = self._getMailServer().getMessageFolderList()
    folder_list = self.getCrawlingScopeList()
    if not folder_list:
      # Nothing is defined so we take it all
      folder_list = available_folder_list
    else:
      # A scope is defined, so we only need to filter
      folder_list = filter(lambda x: x in available_folder_list, folder_list)
    # Interleave default folder for better reactivity
    default_folder = self.getDefaultCrawlingScope()
    if default_folder and default_folder in available_folder_list:
      interleaved_list = []
      for folder in folder_list:
        interleaved_list.append(default_folder)
        interleaved_list.append(folder)
      folder_list = interleaved_list
    # And trigger activities
    self.activate(activity='SQLQueue', priority=2,
                  after_tag=list_activity_tag).crawlMessageFolderList(folder_list)
    # XXX - Start with default one and only use filtered mailboxes if defined

  security.declareProtected(Permissions.ModifyPortalContent, 'crawlMessageFolderList')
  def crawlMessageFolderList(self, message_folder_list):
    """
      Take the first folder in the message_folder_list and start
      ingesting messages. Then postpone ingestion for the rest of
      folders.

      XXX - TODO: crawl 10 folders at once
    """
    # Init dict
    if getattr(self, '_latest_uid', None) is None:
      self._latest_uid = {} # Keeps track of latest ingested

    # Take a single folder at once
    message_folder = message_folder_list[0]
    message_folder_list = message_folder_list[1:]
    list_activity_tag = "IMAPReader_ingestMessageList_%s" % self.getRelativeUrl()
    message_activity_tag = "IMAPReader_ingestMessage_%s" % self.getRelativeUrl()

    # Start ingestion on a single folder (at once)
    # This is very sequential and could be improved probably
    try:
      message_uid_list = self._getMailServer().getMessageUIDList(message_folder=message_folder)
    except ValueError, error_message:  # Use a better exception here XXX
      message_uid_list = []
    # Reduce list size based on asumption of growing sequence of uids
    latest_uid = self._latest_uid.get(message_folder, 0)
    message_uid_list = filter(lambda uid: int(uid) >  latest_uid, message_uid_list)
    # And update biggest uid - for next time
    for uid in message_uid_list:
      # Cache lastest UID (only works if uid is increasing) - XXX-JPS
      if int(uid) > self._latest_uid.get(message_folder, 0):
        self._latest_uid[message_folder] = int(uid)
    # Do not retrieve existing messages - XXX maybe there is a faster way to compute this
    # This should probably be handled within ingestMessageList and splitted among
    # activities
    message_uid_list = filter(lambda uid:
      not self.hasContent(self.getMessageID(uid, message_folder)), message_uid_list)
    self.activate(after_tag=message_activity_tag, priority=2, activity='SQLQueue',
                  tag=list_activity_tag).ingestMessageList(message_uid_list,
                                                   message_folder=message_folder)

    # Postpone the rest
    if message_folder_list:
      self.activate(activity='SQLQueue', priority=2,
                  after_tag=list_activity_tag).crawlMessageFolderList(message_folder_list)

  security.declareProtected(Permissions.ModifyPortalContent, 'ingestMessage')
  def ingestMessage(self, uid, message_folder=None):
    """
      Ingest a single message

      uid -- the IMAP UID of the message to ingest

      message_folder -- the name of the folder to ingest messages from
    """
    if not self.hasContent(self.getMessageID(uid, message_folder)):
      # Only ingest new messages (ie. messages which have not been ingested previously)
      # XXX - double check whether this is consistent with
      # IMAP (ie. read-only ?)
      message_data = self._getMailServer().getMessageData(uid, message_folder=message_folder)
      if message_data is None:
        return # Empty message - XXX Is this a good way of processing exceptions
      #LOG('message_data', 0, repr(message_data))
      contribution_tool = getToolByName(self, 'portal_contributions')
      # Ingestion process will do everything which is required to process
      # messages
      message_id = self.getMessageID(uid, message_folder)
      file_name = '%s.eml' % message_id
      contribution_tool.newContent(container=self, data=message_data,
                                   filename=file_name, id=message_id,
                                   portal_type='Email Thread') # It would be good to make this implicit
      LOG('ingestMessage in folder: %s' % message_folder, INFO, str(uid))

  security.declareProtected(Permissions.ModifyPortalContent, 'ingestMessageList')
  def ingestMessageList(self, uid_list, message_folder=None):
    """
      Ingest a collection of messages defined by uid_list and stored
      in the folder message_folder. Messages are ingested in small blocks
      in order not to create too many activities at once. The size of
      each block is defined by the hard coded constant MAX_UID_LIST_SIZE.
      Systems with multiple ZEO clients can ingest multiple messages
      at once and thus increase ingestion speed. Each message
      is ingest with an OFS ID equal to its IMAP UID. This approach
      simplified greatly the deduplication process.

      uid_list -- a list of IMAP UIDs to ingest

      message_folder -- the name of the folder to ingest messages from
    """
    uid_len = len(uid_list)
    message_activity_tag = "IMAPReader_ingestMessage_%s" % self.getRelativeUrl()
    list_activity_tag = "IMAPReader_ingestMessageList_%s" % self.getRelativeUrl()
    # Ingest MAX_UID_LIST_SIZE emails
    for uid in uid_list[0:min(uid_len, self.MAX_UID_LIST_SIZE)]:
      #if not self.hasContent(self.getMessageID(uid, message_folder)):
        # Only ingest new messages
        #self.activate(activity='SQLQueue', tag=message_activity_tag,
        #              priority=2).ingestMessage(uid,
        #                               message_folder=message_folder)
      self.ingestMessage(uid, message_folder=message_folder)

    # And save the rest
    if uid_len > self.MAX_UID_LIST_SIZE:
      # For now, we do a single threaded reader (per folder)
      # We invoke ingestMessageList once all individual messages have been ingested
      self.activate(after_tag=message_activity_tag, priority=2, activity='SQLQueue',
                    tag=list_activity_tag).ingestMessageList(
                uid_list[self.MAX_UID_LIST_SIZE:], message_folder=message_folder)

  security.declareProtected(Permissions.ModifyPortalContent, 'resetMessageIngestionCache')
  def resetMessageIngestionCache(self):
    """
    Reset the caches related to message ingestion.
    """
    self._latest_uid = {} # Keeps track of latest ingested

  security.declareProtected(Permissions.AccessContentsInformation, 'getMessageID')
  def getMessageID(self, uid, message_folder=None):
    """
      Returns the ID of a message based on the UID and
      on the message_folder name
    """
    if message_folder is None:
      return str(uid)
    return "%s-%s" % (message_folder.replace('/','.'), uid) # Can this be configurable, based on what ? date?

  security.declareProtected(Permissions.AccessContentsInformation, 'getMessageFolderList')
  @transactional_cached()
  def getMessageFolderList(self):
    """
      Returns the list of folders of the current server
      XXX Add read only transaction cache
    """
    server = self._getMailServer()
    return () if server is None else server.getMessageFolderList()

  ### Implementation - Private methods
  @transactional_cached()
  def _getMailServer(self):
    """
      A private method to retrieve a mail server
      based on the URL definition.

      XXX - Danger: if the server Url is changed, we
      break things. An interactor is required to clear
      the variable
    """
    # No server defined
    server_url = self.getURLServer()
    if not server_url:
      return

    # XXX - Here we need to add a switch (POP vs. IMAP vs. IMAPS etc.)
    url_protocol = self.getUrlProtocol('imaps') # Default to IMAP
    if url_protocol == 'imaps':
      server_class = IMAPSServer
    elif url_protocol == 'imap':
      server_class = IMAPServer
    elif url_protocol == 'pops':
      server_class = POPSServer
    elif url_protocol == 'pop':
      server_class = POPServer
    else:
      raise NotImplementedError

    return server_class(server_url, self.getUserId(), self.getPassword(),
                        port=self.getURLPort())
