# -*- coding: utf-8 -*-
## Copyright (c) 2011 Nexedi SARL and Contributors. All Rights Reserved.
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

from lxml.builder import ElementMaker
from lxml.etree import Element
from lxml import etree
import six

from erp5.component.module.XMLSyncUtils import resolveSyncmlStatusCode, \
     encode, resolveSyncmlAlertCode
from erp5.component.module.SyncMLConstant import SYNCML_NAMESPACE, NSMAP

parser = etree.XMLParser(remove_blank_text=True)
E = ElementMaker(namespace=SYNCML_NAMESPACE, nsmap=NSMAP)

# We use the version 1.2 of the protocol defined by the open mobile alliance
# See http://www.openmobilealliance.org/technical/release_program/ds_v12.aspx
DS_PROTOCOL_VERSION="1.2"


class SyncMLResponse(object):
  """
  SyncMLResponse is used to build a message that will be send to a syncml
  server or client.

  SyncML message are xml type and so are based on the lxml to create and
  render it
  """

  def __init__(self):
    self.data = E.SyncML()
    self.data_append = self.data.append
    self.body = None
    self.command_id = 0
    self.sync_confirmation_counter = 0
    self.sync = None

  def __len__(self):
    # To check if it has to be done on whole message or only the body
    return len(bytes(self))

  def __bytes__(self):
    return etree.tostring(self.data, encoding='utf-8', xml_declaration=True,
                          pretty_print=True)
  if six.PY2:
    __str__ = __bytes__

  def _getNextCommandId(self):
    """
    Generate the next command id and store it
    """
    self.command_id += 1
    return str(self.command_id)

  def addFinal(self):
    self.body_append(E.Final())

  def addBody(self):
    self.body = E.SyncBody()
    self.data_append(self.body)
    self.body_append = self.body.append

  def addHeader(self, session_id, message_id, target, source,
                target_name=None, source_name=None, user_id=None,
                password=None, authentication_format='b64',
                authentication_type='syncml:auth-basic'):
    """
    Header defines :
    - protocol version (for now only 1.2 is supported)
    - source & target URI
    - credentials if provided
    """
    xml = (E.SyncHdr(
             E.VerDTD(DS_PROTOCOL_VERSION),
             E.VerProto('SyncML/%s' %(DS_PROTOCOL_VERSION,)),
             E.SessionID('%s' % session_id),  # Global to a sync session
             E.MsgID('%s' % message_id),  # identify uniquely message from a
                                          # sync session on a site
             ))
    # Target device and service
    target_node = E.Target(E.LocURI(target))
    if target_name:
      target_node.append(E.LocName(target_name.decode('utf-8')))
    xml.append(target_node)
    # Device or service addressing
    # If connected to the internet, can be url form like
    # If device, can be specific to device
    source_node = E.Source(E.LocURI(source))
    if source_name:
      source_node.append(E.LocName(source_name.decode('utf-8')))
    xml.append(source_node)
    # Add credential informations
    if user_id and password:
      if authentication_type == 'syncml:auth-basic':
        # base64 formating of "userid:password"
        credential = "%s:%s" % (user_id, password)
        credential = encode(authentication_format, credential).decode()
      elif authentication_type == "syncml:auth-md5":
        # base64 coded md5 for user "XXX", password "XXX", nonce "XXX"
        raise NotImplementedError("MD5 authentication not supported")
      else:
        raise ValueError("Bad authentication type provided : %s" %
                         (authentication_type,))

      xml.append(
        E.Cred(
          E.Meta(E.Format(authentication_format, xmlns='syncml:metinf'),
                 E.Type(authentication_type, xmlns='syncml:metinf'),),
                 E.Data(credential)
                 ))

    self.data_append(xml)

  def addChallengeMessage(self, message_reference, target,
                                source, command="SyncHdr",
                                authentication_format='b64',
                                authentication_type='syncml:auth-basic',
                                authentication_code='missing_credentials'):
    """
    Create a challenge message (CHAL) which is used to asked credentials to a client
    """
    authentication_code = resolveSyncmlStatusCode(authentication_code)
    xml = (E.Status(E.CmdID(self._getNextCommandId()),
                    E.MsgRef(str(message_reference)),
                    E.CmdRef('0'),
                    E.Cmd(command),
                    E.TargetRef(target),
                    E.SourceRef(source),
                    E.Chal(
                          E.Meta(
                      E.Format(authentication_format, xmlns='syncml:metinf'),
                      E.Type(authentication_type, xmlns='syncml:metinf')
                      )
                          ),
                    E.Data(authentication_code)
                    ))
    self.body_append(xml)

  def addStatusMessage(self, message_reference,
                        command_reference, command, target,
                        source, status_code, anchor=None):
    """
    Build a status message

    Status message are used to answer a command (credential, alert) and so
    contains a reference to the original message
    """
    status = E.Status(
      E.CmdID(self._getNextCommandId()),
      E.MsgRef(str(message_reference)),
      E.CmdRef(str(command_reference)),
      E.Cmd(command),
      E.TargetRef(target),
      E.SourceRef(source),
      E.Data(resolveSyncmlStatusCode(status_code)),
      )
    if anchor:
      item = E.Item(
        E.Data(
          E.Anchor(anchor, xmlns='syncml:metinf')
          )
        )
      status.append(item)
    self.body_append(status)

  def addAlertCommand(self, alert_code, target, source,
                       last_anchor, next_anchor):
    """
    Construct an Alert command
    """
    alert = (E.Alert(
      E.CmdID(self._getNextCommandId()),
      E.Data(resolveSyncmlAlertCode(alert_code)),  # alert code
      E.Item(
        E.Target(
          # Target database
          E.LocURI(target)
          ),
        E.Source(
          # Source database
          E.LocURI(source)
          ),
        E.Meta(
          E.Anchor(
            E.Last(last_anchor),
            E.Next(next_anchor)
            )
          )
        )
      )
      )

    self.body_append(alert)

  #
  # XXX Following methods must be reviewed
  #
  def addCredentialMessage(self, subscription):
    """
    Create a credential message (CRED) which is returned by the client after
    receiving a challenge message
    """
    raise NotImplementedError("To review")

#    # create element 'SyncML' with a default namespace
#    xml = E.SyncML()
#    # syncml header
#    xml.append(self.buildHeader(
#      session_id=subscription.incrementSessionId(),
#      msg_id=subscription.incrementMessageId(),
#      target=subscription.getUrlString(),
#      source=subscription.getSubscriptionUrlString(),
#      user_id=subscription.getUserId(),
#      password=subscription.getPassword(),
#      authentication_format=subscription.getAuthenticationFormat(),
#      authentication_type=subscription.getAuthenticationType()))
#
#    # Build the message body
#    sync_body = E.SyncBody()
#
#    # alert message
#    sync_body.append(self.buildAlertMessage(
#      command_id=self._getNextCommandId(),
#      alert_code=subscription.getSyncmlAlertCode(),
#      target=subscription.getDestinationReference(),
#      source=subscription.getSourceReference(),
#      last_anchor=subscription.getLastAnchor(),
#      next_anchor=subscription.getNextAnchor()))
#    syncml_put = self.buildPutMessage(subscription)
#    if syncml_put is not None:
#      sync_body.append(syncml_put)
#    sync_body.append(E.Final())
#
#    xml.append(sync_body)
#    xml_string = etree.tostring(xml, encoding='utf-8', xml_declaration=True,
#                                pretty_print=True)
#    self.data_append(xml_string)


  def addPutMessage(self,subscription, markup='Put',
                    cmd_ref=None, message_id=None):
    """
    This returns the service capabilities
    this is used to inform the server of the CTType version supported
    but if the server use it to respond to a Get request, it's a <Result> markup
    instead of <Put>


    Use Cases :
    The client must send its capabilities at firts synchronization with a server
    or when its information has changed since previous synchronization.

    The client must be able to send it when requested by server
    The server must be albe to sent it when requested by client

    Both must be able to handle and process these informations
    """
    return
#    # XXX-Aurel : must be reviewed according to specification
#    # This part can be skipped for now
#    conduit = subscription.getConduit()
#    xml = None
#    # The conduit defined what capabilities the service offers
#    if getattr(conduit, 'getCapabilitiesCTTypeList', None) and \
#        getattr(conduit, 'getCapabilitiesVerCTList', None) and \
#        getattr(conduit, 'getPreferedCapabilitieVerCT', None):
#      xml = Element('{%s}%s' % (SYNCML_NAMESPACE, markup))
#      xml.append(E.CmdID(self._getNextCommandId()))
#      if message_id:
#        xml.append(E.MsgRef('%s' % message_id))
#      if cmd_ref:
#        xml.append(E.CmdRef('%s' % cmd_ref))
#      xml.extend((E.Meta(E.Type('application/vnd.syncml-devinf+xml')),
#                  E.Item(E.Source(E.LocURI('./devinf12')),
#                         E.Data(E.DevInf(E.VerDTD('1.2'),
#                                         E.Man('Nexedi'),
#                                         E.Mod('ERP5SyncML'),
#                                         E.OEM('Open Source'),
#                                         E.SwV('0.1'),
#                                         E.DevID(subscription.getSubscriptionUrlString()),
#                                         E.DevTyp('workstation'),
#                                         E.UTC(),
#                                         E.DataStore(E.SourceRef(subscription.getSourceReference()))
#                                         )
#                                )
#                         )))
#      data_store = xml.find('{%(ns)s}Item/{%(ns)s}Data/{%(ns)s}DevInf/{%(ns)s}DataStore' % {'ns': SYNCML_NAMESPACE})
#      tx_element_list = []
#      rx_element_list = []
#      for cttype in conduit.getCapabilitiesCTTypeList():
#        if cttype != 'text/xml':
#          for x_version in conduit.getCapabilitiesVerCTList(cttype):
#            rx_element_list.append(E.Rx(E.CTType(cttype), E.VerCT(x_version)))
#            tx_element_list.append(E.Tx(E.CTType(cttype), E.VerCT(x_version)))
#      rx_pref = Element('{%s}Rx-Pref' % SYNCML_NAMESPACE)
#      rx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
#                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
#      data_store.append(rx_pref)
#      data_store.extend(rx_element_list)
#      tx_pref = Element('{%s}Tx-Pref' % SYNCML_NAMESPACE)
#      tx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
#                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
#      data_store.append(tx_pref)
#      data_store.extend(tx_element_list)
#      data_store.append(E.SyncCap(
#        E.SyncType('2'),
#        E.SyncType('1'),
#        E.SyncType('4'),
#        E.SyncType('6')
#        ))
#    self.data_append(xml)


  def addSyncCommand(self, sync_command, gid, data, media_type, more_data):
    """
    Generate the sync command
    XXX media type must be managed by conduit, no this class
    """
    self._initSyncTag()
    data_node = E.Data()
    # XXX to be remove later to use only CDATA
    if media_type == 'text/xml':
      if isinstance(data, bytes):
        data_node.append(etree.XML(data, parser=parser))
      elif isinstance(data, etree.CDATA):
        # data could be Data element if partial XML
        data_node.text = data
      else:
        # XXX Is it suppose to happen ?
        data_node.append(data)
    else:
      if isinstance(data, etree.CDATA):
        data_node.text = data
      else:
        cdata = etree.CDATA(data.decode('utf-8'))
        data_node.text = cdata

    main_tag = Element('{%s}%s' % (SYNCML_NAMESPACE, sync_command))
    main_tag.extend((E.CmdID(self._getNextCommandId()),
                     E.Meta(E.Type(media_type)),
                     E.Item(E.Source(E.LocURI(gid)), data_node)))
    if more_data:
      item_node = main_tag.find('{%s}Item' % SYNCML_NAMESPACE)
      item_node.append(E.MoreData())

    self.sync_append(main_tag)

  def _initSyncTag(self):
    if self.sync is None:
      # Initialize Sync subtag
      self.sync = E.Sync()
      self.body_append(self.sync)
      self.sync_append = self.sync.append

  # XXX-Aurel : must be renamed to buildSyncMLDeletion & moved
  def addDeleteCommand(self, gid=None):
    """
    Delete an object with the SyncML protocol
    """
    self._initSyncTag()
    xml = (E.Delete(
        E.CmdID(
          self._getNextCommandId()),
        E.Item(
          E.Source(E.LocURI('%s' % gid))
          )
        ))
    self.sync_append(xml)

  def addConfirmationMessage(self, command, sync_code, target_ref=None,
                             source_ref=None, command_ref=None,
                             message_ref=None):
    """
    This is used in order to confirm that an object was correctly
    synchronized
    """
    xml = E.Status()
    xml.append(E.CmdID(self._getNextCommandId()))
    if message_ref:
      xml.append(E.MsgRef(str(message_ref)))
    if command_ref:
      xml.append(E.CmdRef(str(command_ref)))
    xml.append(E.Cmd(command))
    # Add either target ou source
    if target_ref:
      xml.append(E.TargetRef(target_ref))
    if source_ref:
      xml.append(E.SourceRef(source_ref))
    xml.append(E.Data(resolveSyncmlStatusCode(sync_code)))

    self.body_append(xml)
    self.sync_confirmation_counter += 1


class SyncMLRequest(object):
  """ SyncMLRequest represent a message received by the client or server"""

  def __init__(self, xml):
    if isinstance(xml, bytes):
      self.data = etree.XML(xml, parser=parser)
    else:
      raise ValueError("Do not know how to initialize message with data %r"
                       % (xml,))
    # Define default values for all variables that will contain parsed data
    self.credentials = {}
    self.header = {}
    self.alert_list = []
    self.status_list = []
    self.sync_command_list = []
    self.isFinal = False
    self.parse()

  def __bytes__(self):
    return etree.tostring(self.data, encoding='utf-8', xml_declaration=True,
                          pretty_print=True)
  if six.PY2:
    __str__ = __bytes__

  def parse(self):
    """
    Generic parse method that will call all sub methods to parse all xml data
    """
    self._parseHeader()
    self._parseCredentials()
    self._parseAlertCommand()
    self._parseStatusList()
    self._parseSyncCommandList()
    self._parseFinal()

  def _parseFinal(self):
    self.isFinal = bool(self.data.xpath(
      '/syncml:SyncML/syncml:SyncBody/syncml:Final',
      namespaces=self.data.nsmap))

  def _parseHeader(self):
    self.header = {
      'dtd_version': float(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:VerDTD)',
        namespaces=self.data.nsmap)),
      'protocol_version': str(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:VerProto)',
        namespaces=self.data.nsmap)),
      'session_id': int(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:SessionID)',
        namespaces=self.data.nsmap)),
      'message_id': int(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:MsgID)',
        namespaces=self.data.nsmap)),
      'target': str(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:Target/syncml:LocURI)',
        namespaces=self.data.nsmap)),
      'source': str(self.data.xpath(
        'string(/syncml:SyncML/syncml:SyncHdr/syncml:Source/syncml:LocURI)',
        namespaces=self.data.nsmap)),
      }

  def _parseCredentials(self):
    if len(self.data.xpath('/syncml:SyncML/syncml:SyncHdr/syncml:Cred',
                            namespaces=self.data.nsmap)):
      self.credentials = {
        'format': str(self.data.xpath(
          'string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Meta/syncml:Format)',
          namespaces=self.data.nsmap)),
        'type': str(self.data.xpath(
          'string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Meta/syncml:Type)',
          namespaces=self.data.nsmap)),
        'data': str(self.data.xpath(
          'string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Data)',
          namespaces=self.data.nsmap)),
          }

  def _parseAlertCommand(self):
    # XXX must parse a list of alert commands
    base_alert_xpath = "/syncml:SyncML/syncml:SyncBody/syncml:Alert"
    append = self.alert_list.append
    alert_node_list = self.data.xpath(base_alert_xpath,
                                      namespaces=self.data.nsmap)
    for alert in alert_node_list:
      alert_kw = {
        'command_id': int(alert.xpath('string(./syncml:CmdID)' ,
                                      namespaces=alert.nsmap)),
        'message_reference': str(alert.xpath('string(./syncml:MsgRef)' ,
                                             namespaces=alert.nsmap)),
        'command_reference': str(alert.xpath('string(./syncml:CmdRef)' ,
                                             namespaces=alert.nsmap)),
        'data': str(alert.xpath('string(./syncml:Data)' ,
                                namespaces=alert.nsmap)),
        'target': str(alert.xpath(
          'string(./syncml:Item/syncml:Target/syncml:LocURI)',
          namespaces=alert.nsmap)),
        'source': str(alert.xpath(
          'string(./syncml:Item/syncml:Source/syncml:LocURI)',
          namespaces=alert.nsmap)),
        'last_anchor': str(alert.xpath(
          'string(./syncml:Item/syncml:Meta/syncml:Anchor/syncml:Last)',
          namespaces=alert.nsmap)),
        'next_anchor': str(alert.xpath(
          'string(./syncml:Item/syncml:Meta/syncml:Anchor/syncml:Next)',
          namespaces=alert.nsmap)),
            }
      append(alert_kw)

  def _parseStatusList(self):
    append = self.status_list.append
    status_node_list = self.data.xpath('//syncml:Status', namespaces=self.data.nsmap)
    for status in status_node_list:
      status_kw = {
        "command_id": str(status.xpath('string(./syncml:Cmd)',
                                       namespaces=self.data.nsmap)),
        "message_reference" : str(status.xpath('string(./syncml:MsgRef)',
                                               namespaces=self.data.nsmap)),
        "command_reference" : str(status.xpath('string(./syncml:CmdRef)',
                                               namespaces=self.data.nsmap)),
        "command" : str(status.xpath('string(./syncml:Cmd)',
                                     namespaces=self.data.nsmap)),
        "status_code" : str(status.xpath('string(./syncml:Data)',
                                         namespaces=self.data.nsmap)),
        "target" : str(status.xpath('string(./syncml:TargetRef)',
                                    namespaces=self.data.nsmap)),
        "source" : str(status.xpath('string(./syncml:SourceRef)',
                                    namespaces=self.data.nsmap)),
        "anchor" : str(status.xpath(
          'string(./syncml:Item/syncml:Data/syncml:Anchor)',
          namespaces=self.data.nsmap)),
        "authentication_format" : str(status.xpath(
          'string(./syncml:Chal/syncml:Meta/syncml:Format)',
          namespaces=self.data.nsmap)),
        "authentication_type" : str(status.xpath(
          'string(./syncml:Chal/syncml:Meta/syncml:Type)',
          namespaces=self.data.nsmap))
        }
      append(status_kw)

  def _parseSyncCommandList(self):
    append = self.sync_command_list.append
    for sync_command in self.data.xpath(
        '//syncml:Add|//syncml:Delete|//syncml:Replace',
        namespaces=self.data.nsmap):
      sync_command_kw = {
        "command_id" : str(sync_command.xpath(
          'string(.//syncml:CmdID)',
          namespaces=self.data.nsmap)),
        "source" : str(sync_command.xpath(
          'string(.//syncml:Item/syncml:Source/syncml:LocURI)',
          namespaces=self.data.nsmap)),
        "target" : str(sync_command.xpath(
          'string(.//syncml:Item/syncml:Target/syncml:LocURI)',
          namespaces=self.data.nsmap)),
        "command" : str(sync_command.xpath(
          'local-name()',
          namespaces=self.data.nsmap)),
        "more_data" : bool(sync_command.xpath(
          './/syncml:Item/syncml:MoreData',
          namespaces=self.data.nsmap))
        }
      # Get xml data apart, we must render it as string for activity
      xml_data = sync_command.xpath('.//syncml:Item/syncml:Data/*',
                                    namespaces=self.data.nsmap)
      if xml_data:
        sync_command_kw["xml_data"] = etree.tostring(xml_data[0])
      else:
        # If not xml, return raw data
        # XXX This must be CDATA type
        data = sync_command.xpath('string(.//syncml:Item/syncml:Data)',
                                  namespaces=self.data.nsmap)
        if isinstance(data, etree.CDATA):
          parser_ = etree.XMLParser(strip_cdata=False)
          cdata = etree.XML(data, parser_)
          data = cdata.text
        if six.PY3:
          data = data.encode()
        sync_command_kw["raw_data"] = data

      append(sync_command_kw)
