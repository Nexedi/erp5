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

import smtplib
from Products.ERP5SyncML.SyncCode import SyncCode
from Products.ERP5SyncML.Subscription import Signature
from DateTime import DateTime
from StringIO import StringIO
from xml.dom.ext import PrettyPrint
from ERP5Diff import ERP5Diff
import random
from zLOG import LOG
try:
  from Products.CMFActivity.ActiveObject import ActiveObject
except ImportError:
  LOG('XMLSyncUtils',0,"Can't import ActiveObject")
  class ActiveObject:
    pass
import commands

try:
  from Ft.Xml import Parse
except ImportError:
  LOG('XMLSyncUtils',0,"Can't import Parse")
  class Parse:
    def __init__(self, *args, **kw):
      raise ImportError, "Sorry, it was not possible to import Ft library"

try:
      from base64 import b16encode, b16decode
except ImportError:
      from base64 import encodestring as b16encode, decodestring as b16decode

class XMLSyncUtilsMixin(SyncCode):

  def SyncMLHeader(self, session_id, msg_id, target, source, target_name=None, 
      source_name=None, dataCred=None, authentication_format='b64', 
      authentication_type='syncml:auth-basic'):
    """
      Since the Header is always almost the same, this is the
      way to set one quickly.
    """
    xml_list = []
    xml = xml_list.append
    xml(' <SyncHdr>\n')
    xml('  <VerDTD>1.1</VerDTD>\n')
    xml('  <VerProto>SyncML/1.1</VerProto>\n')
    xml('  <SessionID>%s</SessionID>\n' % session_id)
    xml('  <MsgID>%s</MsgID>\n' % msg_id)
    xml('  <Target>\n')
    xml('   <LocURI>%s</LocURI>\n' % target)
    if target_name not in (None, ''):
      xml('   <LocName>%s</LocName>\n' %target_name)
    xml('  </Target>\n')
    xml('  <Source>\n')
    xml('   <LocURI>%s</LocURI>\n' % source) 
    if source_name not in (None, ''):
      xml('   <LocName>%s</LocName>\n' % source_name)
    xml('  </Source>\n')
    if dataCred not in (None, ''):
      xml('  <Cred>\n')
      xml('   <Meta>\n')
      xml("    <Format xmlns='syncml:metinf'>%s</Format>\n" % authentication_format)
      xml("    <Type xmlns='syncml:metinf'>%s</Type>\n" % authentication_type)
      xml('   </Meta>\n')
      xml('   <Data>%s</Data>\n' % dataCred)
      xml('  </Cred>\n')
    xml(' </SyncHdr>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def SyncMLAlert(self, cmd_id, sync_code, target, source, last_anchor, 
      next_anchor):
    """
      Since the Alert section is always almost the same, this is the
      way to set one quickly.
    """
    xml_list = []
    xml = xml_list.append
    xml('  <Alert>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    xml('   <Data>%s</Data>\n' % sync_code)
    xml('   <Item>\n')
    xml('    <Target>\n')
    xml('     <LocURI>%s</LocURI>\n' % target)
    xml('    </Target>\n')
    xml('    <Source>\n')
    xml('     <LocURI>%s</LocURI>\n' % source)
    xml('    </Source>\n')
    xml('    <Meta>\n')
    xml('     <Anchor xmlns=\'syncml:metinf\'>\n')
    xml('      <Last>%s</Last>\n' % last_anchor)
    xml('      <Next>%s</Next>\n' % next_anchor)
    xml('     </Anchor>\n')
    xml('    </Meta>\n')
    xml('   </Item>\n')
    xml('  </Alert>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def SyncMLStatus(self, cmd_id, target_ref, source_ref, sync_code, 
      next_anchor=None):
    """
      Since the Status section is always almost the same, this is the
      way to set one quickly.
    """
    xml_list = []
    xml = xml_list.append
    xml('  <Status>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    xml('   <TargetRef>%s</TargetRef>\n' % target_ref)
    xml('   <SourceRef>%s</SourceRef>\n' % source_ref)
    xml('   <Data>%s</Data>\n' % sync_code)
    if next_anchor is not None:
      xml('   <Item>\n')
      xml('    <Data>\n')
      xml('     <Anchor xmlns=\'syncml:metinf\'>\n')
      xml('      <Next>%s</Next>\n' % next_anchor)
      xml('     </Anchor>\n')
      xml('    </Data>\n')
      xml('   </Item>\n')
    xml('  </Status>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def SyncMLConfirmation(self, cmd_id=None, target_ref=None, cmd=None, 
      sync_code=None, msg_ref=None, cmd_ref=None, source_ref=None, 
      remote_xml=None):
    """
    This is used in order to confirm that an object was correctly
    synchronized
    """
    if remote_xml is not None :
      msg_ref=remote_xml.xpath("string(//MsgID)").encode('utf-8')
      cmd_ref=remote_xml.xpath("string(.//CmdID)").encode('utf-8')
      target_ref=remote_xml.xpath("string(.//Target/LocURI)").encode('utf-8')
      source_ref=remote_xml.xpath("string(.//Source/LocURI)").encode('utf-8')

    xml_list = []
    xml = xml_list.append
    xml('  <Status>\n')
    #here there is a lot of test to keep compatibility with older call
    if cmd_id not in (None,'') :
      xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    if msg_ref not in (None,''):
      xml('   <MsgRef>%s</MsgRef>\n' % msg_ref)
    if cmd_ref not in (None,''):
      xml('   <CmdRef>%s</CmdRef>\n' %cmd_ref)
    if cmd not in (None,''):
      xml('   <Cmd>%s</Cmd>\n' % cmd)
    if target_ref not in (None,''):
      xml('   <TargetRef>%s</TargetRef>\n' % target_ref)
    if source_ref not in (None,''):
      xml('   <SourceRef>%s</SourceRef>\n' % source_ref)
    if sync_code not in (None,''):
      xml('   <Data>%s</Data>\n' % sync_code)
    xml('  </Status>\n')
    xml_a = ''.join(xml_list)
    return xml_a
    
  def SyncMLChal(self, cmd_id, cmd, target_ref, source_ref, auth_format, 
      auth_type, data_code):
    """
    This is used in order to ask crendentials
    """
    xml_list = []
    xml = xml_list.append
    xml('  <Status>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    xml('   <Cmd>%s</Cmd>\n' % cmd)
    xml('   <TargetRef>%s</TargetRef>\n' % target_ref)
    xml('   <SourceRef>%s</SourceRef>\n' % source_ref)
    xml('   <Chal>\n')
    xml('    <Meta>\n')
    xml("     <Format xmlns='syncml:metinf'>%s</Format>\n" % auth_format)
    xml("     <Type xmlns='syncml:metinf'>%s</Type>\n" % auth_type)
    xml('    </Meta>\n')
    xml('   </Chal>\n')
    xml('   <Data>%s</Data>\n' % str(data_code))
    xml('  </Status>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def SyncMLPut(self, cmd_id, subscription):
    """
    this is used to inform the server of the CTType version supported
    """
    from Products.ERP5SyncML import Conduit
    # Import the conduit and get it
    conduit_name = subscription.getConduit()
    if conduit_name.startswith('Products'):
      path = conduit_name
      conduit_name = conduit_name.split('.')[-1]
      conduit_module = __import__(path, globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    else:
      conduit_module = __import__('.'.join([Conduit.__name__, conduit_name]),
                                  globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    #if the conduit support the SyncMLPut :
    if hasattr(conduit, 'getCapabilitiesCTType') and \
        hasattr(conduit, 'getCapabilitiesVerCTList') and \
        hasattr(conduit, 'getPreferedCapabilitieVerCT'):
      xml_list = []
      xml = xml_list.append
      if conduit.getCapabilitiesVerCTList() not in ([], None):
        xml('  <Put>\n')
        xml('   <CmdID>%s</CmdID>\n' % cmd_id)
        xml('   <Meta>\n')
        xml('    <Type>application/vnd.syncml-devinf+xml</Type>\n');
        xml('   </Meta>\n')
        xml('   <Item>\n')
        xml('    <Source>\n')
        xml('     <LocURI>./devinf11</LocURI>\n')
        xml('    </Source>\n')
        xml('    <Data>\n')
        xml('     <DevInf>\n')
        xml('      <VerDTD>1.1</VerDTD>\n')
        xml('      <Man>Fabien MORIN</Man>\n')
        xml('      <Mod>ERP5SyncML</Mod>\n')
        xml('      <OEM>Open Source</OEM>\n')
        xml('      <SwV>0.1</SwV>\n')
        xml('      <DevID>%s</DevID>\n' % subscription.getSubscriptionUrl())
        xml('      <DevTyp>workstation</DevTyp>\n')
        xml('      <UTC/>\n')
        xml('      <DataStore>\n')
        xml('       <SourceRef>%s</SourceRef>\n' % subscription.getSourceURI())
        xml('       <Rx-Pref>\n')
        xml('        <CTType>%s</CTType>\n' % conduit.getCapabilitiesCTType())
        xml('        <VerCT>%s</VerCT>\n' % conduit.getPreferedCapabilitieVerCT())
        xml('       </Rx-Pref>\n')
        for rx_version in conduit.getCapabilitiesVerCTList():
          xml('       <Rx>\n')
          xml('        <CTType>%s</CTType>\n' % conduit.getCapabilitiesCTType())
          xml('        <VerCT>%s</VerCT>\n' % rx_version)
          xml('       </Rx>\n')

        xml('       <Tx-Pref>\n')
        xml('        <CTType>%s</CTType>\n' % conduit.getCapabilitiesCTType())
        xml('        <VerCT>%s</VerCT>\n' % conduit.getPreferedCapabilitieVerCT())
        xml('       </Tx-Pref>\n')
        for tx_version in conduit.getCapabilitiesVerCTList():
          xml('       <Tx>\n')
          xml('        <CTType>%s</CTType>\n' % conduit.getCapabilitiesCTType())
          xml('        <VerCT>%s</VerCT>\n' % rx_version)
          xml('       </Tx>\n')

        xml('       <SyncCap>\n')
        xml('        <SyncType>2</SyncType>\n')
        xml('        <SyncType>1</SyncType>\n')
        xml('        <SyncType>4</SyncType>\n')
        xml('        <SyncType>6</SyncType>\n')
        xml('       </SyncCap>\n')

        xml('      </DataStore>\n')
        xml('     </DevInf>\n')
        xml('    </Data>\n')
        xml('   </Item>\n')
        xml('  </Put>\n')
      xml_a = ''.join(xml_list)
      return xml_a
    return ''


  def sendMail(self, fromaddr, toaddr, id_sync, msg):
    """
      Send a message via email
      - sync_object : this is a publication or a subscription
      - message : what we want to send
    """
    header = "Subject: %s\n" % id_sync
    header += "To: %s\n\n" % toaddr
    msg = header + msg
    #LOG('SubSendMail',0,'from: %s, to: %s' % (fromaddr,toaddr))
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddr, msg)
    # if we want to send the email to someone else (debugging)
    #server.sendmail(fromaddr, "seb@localhost", msg)
    server.quit()

  def addXMLObject(self, cmd_id=0, object=None, xml_string=None,
                  more_data=0,gid=None, media_type=None):
    """
      Add an object with the SyncML protocol
    """
    xml_list = []
    xml = xml_list.append
    xml('   <Add>\n')
    xml('    <CmdID>%s</CmdID>\n' % cmd_id)
    xml('    <Meta>\n')
    xml('     <Type>%s</Type>\n' % media_type)
    xml('    </Meta>\n')
    xml('    <Item>\n')
    xml('     <Source>\n')
    xml('      <LocURI>%s</LocURI>\n' % gid)
    xml('     </Source>\n')
    if media_type == self.MEDIA_TYPE['TEXT_XML']:
      xml('     <Data>')
      xml(xml_string)
      xml('</Data>\n')
    else:
      xml('     <Data><![CDATA[')
      xml(xml_string)
      xml('\n]]></Data>\n')
    if more_data == 1:
      xml('     <MoreData/>\n')
    xml('    </Item>\n')
    xml('   </Add>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def deleteXMLObject(self, cmd_id=0, object_gid=None, xml_object=''):
    """
      Delete an object with the SyncML protocol
    """
    xml_list = []
    xml = xml_list.append
    xml('   <Delete>\n')
    xml('    <CmdID>%s</CmdID>\n' % cmd_id)
    xml('    <Item>\n')
    xml('     <Source>\n')
    xml('      <LocURI>%s</LocURI>\n' % object_gid)
    xml('     </Source>\n')
    #xml('     <Data>\n')  #this 2 lines seems to be useless
    #xml('     </Data>\n')
    xml('    </Item>\n')
    xml('   </Delete>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def replaceXMLObject(self, cmd_id=0, object=None, xml_string=None,
                       more_data=0, gid=None, media_type=None):
    """
      Replace an object with the SyncML protocol
    """
    xml_list = []
    xml = xml_list.append
    xml('   <Replace>\n')
    xml('    <CmdID>%s</CmdID>\n' % cmd_id)
    xml('    <Meta>\n')
    xml('     <Type>%s</Type>\n' % media_type)
    xml('    </Meta>\n')
    xml('    <Item>\n')
    xml('     <Source>\n')
    xml('      <LocURI>%s</LocURI>\n' % str(gid))
    xml('     </Source>\n')
    xml('     <Data>')
    xml(xml_string)
    xml('     </Data>\n')
    if more_data == 1:
      xml('     <MoreData/>\n')
    xml('    </Item>\n')
    xml('   </Replace>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def getXupdateObject(self, object_xml=None, old_xml=None):
    """
    Generate the xupdate with the new object and the old xml
    """
    erp5diff = ERP5Diff()
    erp5diff.compare(old_xml, object_xml)
    xupdate_doc = erp5diff._result
    #minidom is buggy, add namespace declaration, and version
    attr_ns = xupdate_doc.createAttribute('xmlns:xupdate')
    attr_ns.value = 'http://www.xmldb.org/xupdate'
    attr_version = xupdate_doc.createAttribute('version')
    attr_version.value='1.0'
    xupdate_doc.documentElement.setAttributeNode(attr_ns)
    xupdate_doc.documentElement.setAttributeNode(attr_version)
    xupdate = xupdate_doc.toxml()
    #omit xml declaration
    xupdate = xupdate[xupdate.find('<xupdate:modifications'):]
    return xupdate

  def getSessionId(self, xml):
    """
    We will retrieve the session id of the message
    """
    session_id = 0
    session_id = xml.xpath('string(/SyncML/SyncHdr/SessionID)')
    session_id = int(session_id)
    return session_id
    
  def getMessageId(self, xml):
    """
    We will retrieve the message id of the message
    """
    message_id = 0
    message_id = xml.xpath('string(/SyncML/SyncHdr/MsgID)')
    message_id = int(message_id)
    return message_id

  def getTarget(self, xml):
    """
    return the target in the SyncHdr section
    """
    url = ''
    url = xml.xpath('string(/SyncML/SyncHdr/Target/LocURI)')
    url = url.encode('utf-8')
    return url

  def getAlertLastAnchor(self, xml_stream):
    """
      Return the value of the last anchor, in the
      alert section of the xml_stream
    """
    first_node = xml_stream.childNodes[0]

    # Get informations from the body
    client_body = first_node.childNodes[3]
    last_anchor = client_body.xpath('string(/Alert/Item/Meta/Anchor/Last)')
    last_anchor = last_anchor.encode('utf-8')
    return last_anchor

  def getAlertNextAnchor(self, xml_stream):
    """
      Return the value of the next anchor, in the
      alert section of the xml_stream
    """
    first_node = xml_stream.childNodes[0]
    if first_node.nodeName != "SyncML":
      print "This is not a SyncML message"

    # Get informations from the body
    client_body = first_node.childNodes[3]
    next_anchor = client_body.xpath('string(/Alert/Item/Meta/Anchor/Next)')
    next_anchor = next_anchor.encode('utf-8')
    return next_anchor

  def getSourceURI(self, xml):
    """
    return the source URI of the syncml header
    """
    subscription_url = xml.xpath('string(//SyncHdr/Source/LocURI)')
    if isinstance(subscription_url, unicode):
      subscription_url = subscription_url.encode('utf-8')
    return subscription_url
  
  def getStatusTarget(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    status = xml.xpath('string(TargetRef)')
    if isinstance(status, unicode):
      status = status.encode('utf-8')
    return status

  def getStatusCode(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    status_code = xml.xpath('string(Data)')
    if status_code not in ('', None, []):
      return int(status_code)
    return None

  def getStatusCommand(self, xml):
    """
      Return the value of the command inside the xml_stream
    """
    if xml.nodeName=='Status':
      cmd = xml.xpath('string(//Status/Cmd)')
      if isinstance(cmd, unicode):
        cmd = cmd.encode('utf-8')
      return cmd
    else:
      return None

  def getCred(self, xml):
    """
      return the credential information : type, format and data
    """
    format=''
    type=''
    data=''

    first_node = xml.childNodes[0]
    format = first_node.xpath("string(/SyncML/SyncHdr/Cred/Meta/*[local-name() = 'Format'])")
    type = first_node.xpath("string(/SyncML/SyncHdr/Cred/Meta/*[local-name() = 'Type'])")
    data = first_node.xpath('string(/SyncML/SyncHdr/Cred/Data)')

    format = format.encode('utf-8')
    type = type.encode('utf-8')
    data = data.encode('utf-8')
    return (format, type, data)

  def checkCred(self, xml_stream):
    """
      Check if there's a Cred section in the xml_stream
    """
    if xml_stream.xpath('string(SyncML/SyncHdr/Cred)') not in ('', None, []):
      return True
    return False

  def getChal(self, xml):
    """
      return the chalenge information : format and type
    """    
    format=None
    type=None

    first_node = xml.childNodes[0]
    format = first_node.xpath("string(//*[local-name() = 'Format'])")
    type = first_node.xpath("string(//*[local-name() = 'Type'])")

    format = format.encode('utf-8')
    type = type.encode('utf-8')
    return (format, type)

  def checkChal(self, xml_stream):
    """
      Check if there's a Chal section in the xml_stream
    """
    if xml_stream.xpath('string(SyncML/SyncBody/Status/Chal)') \
        not in ('', None, []):
      return True
    return False

  def getAlertCode(self, xml_stream):
    """
      Return the value of the alert code inside the full syncml message
    """
    alert_code = xml_stream.xpath('string(SyncML/SyncBody/Alert/Data)')
    if alert_code not in (None, ''):
      return int(alert_code)
    else:
      return None

  def checkAlert(self, xml_stream):
    """
      Check if there's an Alert section in the xml_stream
    """
    alert = False
    if xml_stream.xpath('string(SyncML/SyncBody/Alert)') not in ('', None, []):
      alert = True
    return alert

  def checkSync(self, xml_stream):
    """
      Check if there's an Sync section in the xml_xtream
    """
    sync = False
    if xml_stream.xpath('string(SyncML/SyncBody/Sync)') not in ('', None, []):
      sync = True
    return sync

  def checkStatus(self, xml_stream):
    """
      Check if there's a Status section in the xml_xtream
    """
    status = False
    if xml_stream.xpath('string(SyncML/SyncBody/Status)') not in ('', None, []):
      status = True
    return status

  def getSyncActionList(self, xml_stream):
    """
    return the list of the action (could be "add", "replace", "delete").
    """
    return xml_stream.xpath('//Add|//Delete|//Replace')

  def getSyncBodyStatusList(self, xml_stream):
    """
    return the list of dictionary corredponding to the data of each status bloc
    the data are : cmd, code and source
    """
    status_list = []
    xml = xml_stream.xpath('//Status')
    for status in xml:
      tmp_dict = {}
      tmp_dict['cmd']     = status.xpath('string(./Cmd)').encode('utf-8')
      tmp_dict['code']    = status.xpath('string(./Data)').encode('utf-8')
      tmp_dict['source']  = status.xpath('string(./SourceRef)').encode('utf-8')
      tmp_dict['target']  = status.xpath('string(./TargetRef)').encode('utf-8')
      status_list.append(tmp_dict)
    return status_list

  def getDataText(self, action):
    """
    return the section data in text form, it's usefull for the VCardConduit
    """
    data = action.xpath('string(Item/Data)')
    if isinstance(data, unicode):
      data = data.encode('utf-8')
    return data

  def getDataSubNode(self, action):
    """
      Return the node starting with <object....> of the action
    """
    if action.xpath('.//Item/Data') not in ([], None):
      data_node = action.xpath('.//Item/Data')[0]
      if data_node.hasChildNodes():
        return data_node.childNodes[0]
    return None

  def getPartialData(self, action):
    """
      Return the node starting with <object....> of the action
    """
    comment_list = action.xpath('.//Item/Data[comment()]')
    if comment_list != []:
      return comment_list[0].childNodes[0].data.encode('utf-8')
    return None

  def getActionId(self, action, action_name):
    """
      Return the rid of the object described by the action
    """
    id = action.xpath('string(.//Item/Source/LocURI)')
    if id in (None, ''):
      id = action.xpath('string(.//Item/Target/LocURI)')
    if isinstance(id, unicode):
      id = id.encode('utf-8')
    return id

  def checkActionMoreData(self, action):
    """
      Return the rid of the object described by the action
    """
    if action.xpath('Item/MoreData') not in ([],None) :
      return True
    return False

  def getActionType(self, action):
    """
      Return the type of the object described by the action
    """
    action_type = action.xpath('string(Meta/Type)')
    if isinstance(action_type, unicode):
      action_type = action_type.encode('utf-8')
    return action_type

  def getElementNodeList(self, node):
    """
      Return childNodes that are ElementNode
    """
    return node.xpath('*')

  def getTextNodeList(self, node):
    """
      Return childNodes that are ElementNode
    """
    subnode_list = []
    for subnode in node.childNodes or []:
      if subnode.nodeType == subnode.TEXT_NODE:
        subnode_list += [subnode]
    return subnode_list
  
  def getAttributeNodeList(self, node):
    """
      Return childNodes that are ElementNode
    """
    return node.xpath('@*')

  def getSyncMLData(self, domain=None, remote_xml=None, cmd_id=0,
                    subscriber=None, xml_confirmation=None, conduit=None,
                    max=None, **kw):
    """
    This generate the syncml data message. This returns a string
    with all modification made locally (ie replace, add ,delete...)

    if object is not None, this usually means we want to set the
    actual xupdate on the signature.
    """
    local_gid_list = []
    syncml_data = kw.get('syncml_data','')
    result = {'finished':1}
    if isinstance(remote_xml, str) or isinstance(remote_xml, unicode):
      remote_xml = Parse(remote_xml)
    if subscriber.getRemainingObjectPathList() is None:
      object_list = domain.getObjectList()
      object_path_list = map(lambda x: x.getPhysicalPath(),object_list)
      subscriber.setRemainingObjectPathList(object_path_list)

      #object_gid = domain.getGidFromObject(object)
      local_gid_list = map(lambda x: domain.getGidFromObject(x),object_list)
      # Objects to remove
      for object_gid in subscriber.getGidList():
        if not (object_gid in local_gid_list):
          # This is an object to remove
          signature = subscriber.getSignatureFromGid(object_gid)
          if signature.getStatus()!=self.PARTIAL: # If partial, then we have a signature
                                                  # but no local object
            xml_object = signature.getXML()
            if xml_object is not None: # This prevent to delete an object that
                                      # we were not able to create
              rid = signature.getRid()
              if rid != None:
                object_gid=rid #to use the remote id if it exist
              syncml_data += self.deleteXMLObject(xml_object=signature.getXML()\
                  or '', object_gid=object_gid,cmd_id=cmd_id)
              cmd_id += 1

    local_gid_list = []
    loop = 0
    for object_path in subscriber.getRemainingObjectPathList():
      if max is not None and loop >= max:
        result['finished'] = 0
        break
      object = self.unrestrictedTraverse(object_path)
      status = self.SENT
      object_gid = domain.getGidFromObject(object)
      if object_gid in ('', None):
        continue
      local_gid_list += [object_gid]
      force = 0
      if syncml_data.count('\n') < self.MAX_LINES and not \
          object.id.startswith('.'):
        # If not we have to cut
        #LOG('getSyncMLData',0,'xml_mapping: %s' % str(domain.xml_mapping))
        #LOG('getSyncMLData',0,'code: %s' % str(self.getAlertCode(remote_xml)))
        #LOG('getSyncMLData',0,'gid_list: %s' % str(local_gid_list))
        #LOG('getSyncMLData',0,'subscriber.getGidList: %s' % subscriber.getGidList())
        #LOG('getSyncMLData',0,'hasSignature: %s' % str(subscriber.hasSignature(object_gid)))
        #LOG('getSyncMLData',0,'alert_code == slowsync: %s' % str(self.getAlertCode(remote_xml)==self.SLOW_SYNC))
        signature = subscriber.getSignatureFromGid(object_gid)

        # Here we first check if the object was modified or not by looking at dates
        if signature is not None:
          signature.checkSynchronizationNeeded(object)
        status = self.SENT
        more_data=0
        # For the case it was never synchronized, we have to send everything
        if signature is not None and signature.getXMLMapping()==None:
          pass
        elif signature == None or (signature.getXML() == None and \
            signature.getStatus() != self.PARTIAL) or \
            self.getAlertCode(remote_xml) == self.SLOW_SYNC:
          #LOG('PubSyncModif',0,'Current object.getPath: %s' % object.getPath())
          xml_object = domain.getXMLFromObject(object)
          xml_string = xml_object
          if isinstance(xml_string, unicode):
            xml_string = xml_object.encode('utf-8')
          gid = subscriber.getGidFromObject(object)
          signature = Signature(id=gid,object=object)
          signature.setTempXML(xml_object)
          if xml_string.count('\n') > self.MAX_LINES:
            if xml_string.find('--') >= 0: # This make comment fails, so we need to replace
              xml_string = xml_string.replace('--','@-@@-@')
            more_data=1
            i = 0
            short_string = ''
            rest_string = xml_string
            while i < self.MAX_LINES:
              short_string += rest_string[:rest_string.find('\n')+1]
              rest_string = xml_string[len(short_string):]
              i += 1
            #LOG('getSyncMLData',0,'setPartialXML with: %s' % str(rest_string))
            signature.setPartialXML(rest_string)
            status = self.PARTIAL
            signature.setAction('Add')
            xml_string = '<!--' + short_string + '-->'
          gid = signature.getRid()#in fisrt, we try with rid if there is one
          if gid == None:
            gid = signature.getGid()
          syncml_data += self.addXMLObject(cmd_id=cmd_id, object=object, 
              gid=gid, xml_string=xml_string, 
              more_data=more_data, media_type=subscriber.getMediaType())
          cmd_id += 1
          signature.setStatus(status)
          subscriber.addSignature(signature)
        elif signature.getStatus()==self.NOT_SYNCHRONIZED \
            or signature.getStatus()==self.PUB_CONFLICT_MERGE: # We don't have synchronized this object yet
          xml_object = domain.getXMLFromObject(object)
          #LOG('getSyncMLData',0,'checkMD5: %s' % str(signature.checkMD5(xml_object)))
          #LOG('getSyncMLData',0,'getStatus: %s' % str(signature.getStatus()))
          if signature.getStatus()==self.PUB_CONFLICT_MERGE:
            xml_confirmation += self.SyncMLConfirmation(cmd_id=cmd_id, 
                source_ref=signature.getGid(), sync_code=self.CONFLICT_MERGE, 
                cmd='Replace')
          set_synchronized = 1
          if not signature.checkMD5(xml_object):
            set_synchronized = 0
            # This object has changed on this side, we have to generate some xmldiff
            xml_string = self.getXupdateObject(
                                      domain.getXMLFromObject(object),
                                      signature.getXML())
            if xml_string.count('\n') > self.MAX_LINES:
              # This make comment fails, so we need to replace
              if xml_string.find('--') >= 0:
                xml_string = xml_string.replace('--','@-@@-@')
              i = 0
              more_data=1
              short_string = ''
              rest_string = xml_string
              while i < self.MAX_LINES:
                short_string += rest_string[:rest_string.find('\n')+1]
                rest_string = xml_string[len(short_string):]
                i += 1
              signature.setPartialXML(rest_string)
              status = self.PARTIAL
              signature.setAction('Replace')
              xml_string = '<!--' + short_string + '-->'
            signature.setStatus(status)
            if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
              xml_string = domain.getXMLFromObject(object)
            gid = signature.getRid()#in fisrt, we try with rid if there is one
            if gid == None:
              gid = signature.getGid()
            syncml_data += self.replaceXMLObject(cmd_id=cmd_id, object=object,
                                                 gid=gid, xml_string=xml_string,
                                                 more_data=more_data,
                                                 media_type=subscriber.getMediaType())
            cmd_id += 1
            signature.setTempXML(xml_object)
          # Now we can apply the xupdate from the subscriber
          subscriber_xupdate = signature.getSubscriberXupdate()
          #LOG('getSyncMLData subscriber_xupdate',0,subscriber_xupdate)
          if subscriber_xupdate is not None:
            old_xml = signature.getXML()
            conduit.updateNode(xml=subscriber_xupdate, object=object,
                previous_xml=old_xml, force=(domain.getDomainType() == self.SUB),
                simulate=0)
            xml_object = domain.getXMLFromObject(object)
            signature.setTempXML(xml_object)
          if set_synchronized: # We have to do that after this previous update
            # We should not have this case when we are in CONFLICT_MERGE
            signature.setStatus(self.SYNCHRONIZED)
        elif signature.getStatus()==self.PUB_CONFLICT_CLIENT_WIN:
          # We have decided to apply the update
          # XXX previous_xml will be geXML instead of getTempXML because
          # some modification was already made and the update
          # may not apply correctly
          xml_update = signature.getPartialXML()
          conduit.updateNode(xml=signature.getPartialXML(), object=object,
                            previous_xml=signature.getXML(),force=1)
          xml_confirmation += self.SyncMLConfirmation(cmd_id=cmd_id, 
              target_ref=object_gid, sync_code=self.CONFLICT_CLIENT_WIN,
              cmd='Replace')
          signature.setStatus(self.SYNCHRONIZED)
        elif signature.getStatus()==self.PARTIAL:
          xml_string = signature.getPartialXML()
          if xml_string.count('\n') > self.MAX_LINES:
            i = 0
            more_data=1
            short_string = ''
            rest_string = xml_string
            while i < self.MAX_LINES:
              short_string += rest_string[:rest_string.find('\n')+1]
              rest_string = xml_string[len(short_string):]
              i += 1
            signature.setPartialXML(rest_string)
            xml_string = short_string
            status = self.PARTIAL
          if xml_string.find('--') >= 0: # This make comment fails, so we need to replace
            xml_string = xml_string.replace('--','@-@@-@')
          xml_string = '<!--' + xml_string + '-->'
          signature.setStatus(status)
          if(subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']):
            xml_string = domain.getXMLFromObject(object)
          #LOG('xml_string =', 0, xml_string)
          if signature.getAction()=='Replace':
            gid = signature.getRid()#in fisrt, we try with rid if there is one
            if gid == None:
              gid = signature.getGid()
            syncml_data += self.replaceXMLObject(cmd_id=cmd_id, object=object,
                gid=gid, xml_string=xml_string, more_data=more_data,
                media_type=subscriber.getMediaType())
          elif signature.getAction()=='Add':
            gid = signature.getRid()#in fisrt, we try with rid if there is one
            if gid == None:
              gid = signature.getGid()
            syncml_data += self.addXMLObject(cmd_id=cmd_id, object=object, 
                gid=gid, xml_string=xml_string, 
                more_data=more_data, media_type=subscriber.getMediaType())
      else:
        result['finished'] = 1
        break
      loop += 1
    result['syncml_data'] = syncml_data
    result['xml_confirmation'] = xml_confirmation
    result['cmd_id'] = cmd_id
    return result

  def applyActionList(self, domain=None, subscriber=None, cmd_id=0,
                      remote_xml=None,conduit=None,simulate=0):
    """
    This just look to a list of action to do, then id applies
    each action one by one, thanks to a conduit
    """
    xml_confirmation = ''
    has_next_action = 0
    destination = self.unrestrictedTraverse(domain.getDestinationPath())
    #LOG('applyActionList args',0,'domain : %s\n subscriber : %s\n cmd_id : %s' % (domain, subscriber, cmd_id))
    for action in self.getSyncActionList(remote_xml):
      conflict_list = []
      status_code = self.SUCCESS
      # Thirst we have to check the kind of action it is
      partial_data = self.getPartialData(action)
      rid = self.getActionId(action, action.nodeName)
      if action.nodeName != 'Delete':
        if hasattr(conduit, 'getGidFromXML'):
          gid = b16encode(conduit.getGidFromXML(self.getDataText(action)))
        else:
          gid=rid
      else:
        gid=rid
      object_id = domain.generateNewIdWithGenerator(object=destination,gid=gid)
      signature = subscriber.getSignatureFromGid(gid)
      if signature != None and rid != gid:
        #in this case, the object was created on another subscriber than erp5
        # and we should save it's remote id
        signature.setRid(rid)
      #LOG('gid == rid ?', 0, 'gid=%s, rid=%s' % (gid, rid))
      object = subscriber.getObjectFromGid(gid)
      #LOG('applyActionList subscriber.getObjectFromGid %s' % gid,0,object)
      if signature == None:
        #LOG('applyActionList, signature is None',0,signature)
        if gid == rid:
          signature = Signature(id=gid, status=self.NOT_SYNCHRONIZED, 
              object=object).__of__(subscriber)
        else:
          signature = Signature(rid=rid, id=gid, status=self.NOT_SYNCHRONIZED,
              object=object).__of__(subscriber)
        signature.setObjectId(object_id)
        subscriber.addSignature(signature)
      force = signature.getForce()
      #LOG('applyActionList',0,'object: %s' % repr(object))
      if self.checkActionMoreData(action) == 0:
        data_subnode = None
        if partial_data != None:
          signature_partial_xml = signature.getPartialXML()
          if signature_partial_xml is not None:
            data_subnode = signature.getPartialXML() + partial_data
          else:
            data_subnode = partial_data
          #LOG('SyncModif',0,'data_subnode: %s' % data_subnode)
          if subscriber.getMediaType() == self.MEDIA_TYPE['TEXT_XML']:
            data_subnode = Parse(data_subnode)
            data_subnode = data_subnode.childNodes[0] # Because we just created a new xml
          # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
        else:
          if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
            data_subnode = self.getDataText(action)
          else:
            data_subnode = self.getDataSubNode(action)
        if action.nodeName == 'Add':
          # Then store the xml of this new subobject
          if object is None:
            object_id = domain.generateNewIdWithGenerator(object=destination,gid=gid)
            #if object_id is not None:
            add_data = conduit.addNode(xml=data_subnode, 
                object=destination, object_id=object_id)
            if add_data['conflict_list'] not in ('', None, []):
              conflict_list += add_data['conflict_list']
            # Retrieve directly the object from addNode
            object = add_data['object']
            #LOG('XMLSyncUtils, in ADD add_data',0,add_data)
            if object is not None:
              signature.setPath(object.getPhysicalPath())
              signature.setObjectId(object.getId())
          else:
            #Object was retrieve but need to be updated without recreated
            #usefull when an object is only deleted by workflow.
            object_id = domain.generateNewIdWithGenerator(object=destination,gid=gid)
            add_data = conduit.addNode(xml=data_subnode,
                                       object=destination,
                                       object_id=object_id,
                                       sub_object=object)
            if add_data['conflict_list'] not in ('', None, []):
              conflict_list += add_data['conflict_list']
          if object is not None:
            #LOG('SyncModif',0,'addNode, found the object')
            #mapping = getattr(object,domain.getXMLMapping(),None)
            xml_object = domain.getXMLFromObject(object)
            #if mapping is not None:
            #  xml_object = mapping()
            signature.setStatus(self.SYNCHRONIZED)
            #signature.setId(object.getId())
            signature.setPath(object.getPhysicalPath())
            signature.setXML(xml_object)
            xml_confirmation += self.SyncMLConfirmation(
                cmd_id=cmd_id, 
                cmd='Add', 
                sync_code=self.ITEM_ADDED,
                remote_xml=action)
            cmd_id +=1
        elif action.nodeName == 'Replace':
          #LOG('SyncModif',0,'object: %s will be updated...' % str(object))
          if object is not None:
            #LOG('SyncModif',0,'object: %s will be updated...' % object.id)
            signature = subscriber.getSignatureFromGid(gid)
            #LOG('SyncModif',0,'previous signature: %s' % str(signature))
            previous_xml = signature.getXML()
            #LOG('SyncModif',0,'previous signature: %i' % len(previous_xml))
            conflict_list += conduit.updateNode(xml=data_subnode, object=object,
                              previous_xml=signature.getXML(),force=force,
                              simulate=simulate)
            xml_object = domain.getXMLFromObject(object)
            signature.setTempXML(xml_object)
            if conflict_list != []:
              status_code = self.CONFLICT
              signature.setStatus(self.CONFLICT)
              signature.setConflictList(signature.getConflictList() \
                  + conflict_list)
              string_io = StringIO()
              PrettyPrint(data_subnode,stream=string_io)
              data_subnode_string = string_io.getvalue()
              signature.setPartialXML(data_subnode_string)
            elif not simulate:
              signature.setStatus(self.SYNCHRONIZED)
            xml_confirmation += self.SyncMLConfirmation(\
                cmd_id=cmd_id, 
                cmd='Replace', 
                sync_code=status_code,
                remote_xml=action)
            cmd_id +=1
            if simulate:
              # This means we are on the publiher side and we want to store
              # the xupdate from the subscriber and we also want to generate
              # the current xupdate from the last synchronization
              string_io = StringIO()
              PrettyPrint(data_subnode,stream=string_io)
              data_subnode_string = string_io.getvalue()
              #LOG('applyActionList, subscriber_xupdate:',0,data_subnode_string)
              signature.setSubscriberXupdate(data_subnode_string)

        elif action.nodeName == 'Delete':
          object_id = signature.getId()
          if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']: 
            data_subnode = self.getDataText(action)
          else:
            data_subnode = self.getDataSubNode(action)
          if subscriber.getObjectFromGid(object_id) not in (None, ''):
          #if the object exist:
            conduit.deleteNode(xml=data_subnode, object=destination, 
                object_id=subscriber.getObjectFromGid(object_id).getId())
            subscriber.delSignature(gid)
          xml_confirmation += self.SyncMLConfirmation(
              cmd_id=cmd_id, 
              cmd='Delete',
              sync_code=status_code,
              remote_xml=action)
      else: # We want to retrieve more data
        signature.setStatus(self.PARTIAL)
        #LOG('SyncModif',0,'setPartialXML: %s' % str(previous_partial))
        previous_partial = signature.getPartialXML() or ''
        #if previous_partial.find(partial_data)<0: # XXX bad thing
        previous_partial += partial_data
        signature.setPartialXML(previous_partial)
        #LOG('SyncModif',0,'previous_partial: %s' % str(previous_partial))
        #LOG('SyncModif',0,'waiting more data for :%s' % signature.getId())
        #xml_confirmation += self.SyncMLConfirmation(cmd_id, object_gid, 
        #    self.WAITING_DATA, action.nodeName)
        xml_confirmation += self.SyncMLConfirmation(\
            cmd_id=cmd_id, 
            cmd=action.nodeName, 
            sync_code=self.WAITING_DATA,
            remote_xml=action)
      if conflict_list != [] and signature is not None:
        # We had a conflict
        signature.setStatus(self.CONFLICT)

    return (xml_confirmation,has_next_action,cmd_id)

  def applyStatusList(self, subscriber=None,remote_xml=None):
    """
    This read a list of status list (ie syncml confirmations).
    This method have to change status codes on signatures
    """
    status_list = self.getSyncBodyStatusList(remote_xml)
    has_status_list = 0
    destination_waiting_more_data = 0
    if status_list != []:
      for status in status_list:
        status_cmd = status['cmd']
        #if status_cmd in ('Delete'):
        #  object_gid = status['target']
        #else:
        object_gid = status['source']
        status_code = int(status['code'])
        if status_cmd in ('Add','Replace'):
          has_status_list = 1
          signature = subscriber.getSignatureFromGid(object_gid)
          if signature == None:
            signature = subscriber.getSignatureFromRid(object_gid)
          if status_code == self.CHUNK_OK:
            destination_waiting_more_data = 1
            signature.setStatus(self.PARTIAL)
          elif status_code == self.CONFLICT:
            signature.setStatus(self.CONFLICT)
          elif status_code == self.CONFLICT_MERGE:
            # We will have to apply the update, and we should not care 
            # about conflicts, so we have to force the update
            signature.setStatus(self.NOT_SYNCHRONIZED)
            signature.setForce(1)
          elif status_code == self.CONFLICT_CLIENT_WIN:
            # The server was agree to apply our updates, nothing to do
            signature.setStatus(self.SYNCHRONIZED)
          elif status_code in (self.SUCCESS, self.ITEM_ADDED):
            signature.setStatus(self.SYNCHRONIZED)
        elif status_cmd == 'Delete':
          if status_code == self.SUCCESS:
            signature = subscriber.getSignatureFromGid(object_gid)
            if signature == None:
              signature = subscriber.getSignatureFromRid(object_gid)
            subscriber.delSignature(signature.getGid())
    return (destination_waiting_more_data, has_status_list)


class XMLSyncUtils(XMLSyncUtilsMixin):

  def Sync(self, id, msg=None, RESPONSE=None):
    """
    This is the main method for synchronization
    """
    pass

  def SyncInit(self, domain):
    """
    Initialization of a synchronization, this is
    used for the first message of every synchronization
    """
    pass

  def getConduitByName(self, conduit_name):
    """
    Get Conduit Object by given name.
    The Conduit can be located in Any Products according to naming Convention
    Products.<Product Name>.Conduit.<Conduit Module> ,if conduit_name equal module's name.
    By default Conduit must be defined in Products.ERP5SyncML.Conduit.<Conduit Module>
    """
    from Products.ERP5SyncML import Conduit
    if conduit_name.startswith('Products'):
      path = conduit_name
      conduit_name = conduit_name.split('.')[-1]
      conduit_module = __import__(path, globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    else:
      conduit_module = __import__('.'.join([Conduit.__name__, conduit_name]),
                                  globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    return conduit

  def SyncModif(self, domain, remote_xml):
    """
    Modification Message, this is used after the first
    message in order to send modifications.
    """
    """
      Send the server modification, this happens after the Synchronization
      initialization
    """
    has_response = 0 #check if syncmodif replies to this messages
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    #LOG('SyncModif',0,'Starting... domain: %s' % str(domain))

    first_node = remote_xml.childNodes[0]
    # Get informations from the header
    xml_header = first_node.childNodes[1]
    if xml_header.nodeName != "SyncHdr":
      #LOG('PubSyncModif',0,'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"

    subscriber = domain # If we are the client, this is fine
    simulate = 0 # used by applyActionList, should be 0 for client
    if domain.domain_type == self.PUB:
      simulate = 1
      subscription_url = self.getSourceURI(xml_header) 
      subscriber = domain.getSubscriber(subscription_url)

    # We have to check if this message was not already, this can be dangerous
    # to update two times the same object
    message_id = self.getMessageId(remote_xml)
    correct_message = subscriber.checkCorrectRemoteMessageId(message_id)
    if not correct_message: # We need to send again the message
      #LOG('SyncModif, no correct message:',0,"sending again...")
      last_xml = subscriber.getLastSentMessage()
      #LOG("last_xml :", 0, last_xml)
      if last_xml != '':
        has_response = 1
        if domain.domain_type == self.PUB: # We always reply
          self.sendResponse(from_url=domain.publication_url, 
              to_url=subscriber.subscription_url, sync_id=domain.getTitle(), 
              xml=last_xml,domain=domain)
        elif domain.domain_type == self.SUB:
          self.sendResponse(from_url=domain.subscription_url, 
              to_url=domain.publication_url, sync_id=domain.getTitle(), 
              xml=last_xml, domain=domain)
      return {'has_response':has_response,'xml':last_xml}
    subscriber.setLastSentMessage('')

    # First apply the list of status codes
    (destination_waiting_more_data,has_status_list) = self.applyStatusList(
                                         subscriber=subscriber,
                                         remote_xml=remote_xml)

    alert_code = self.getAlertCode(remote_xml)
    # Import the conduit and get it
    conduit = self.getConduitByName(subscriber.getConduit())
    # Then apply the list of actions
    (xml_confirmation, has_next_action, cmd_id) = self.applyActionList(
                                      cmd_id=cmd_id,
                                      domain=domain,
                                      subscriber=subscriber,
                                      remote_xml=remote_xml,
                                      conduit=conduit, simulate=simulate)
    #LOG('SyncModif, has_next_action:',0,has_next_action)

    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')

    # syncml header
    if domain.domain_type == self.PUB:
      xml(self.SyncMLHeader(subscriber.getSessionId(), 
        subscriber.incrementMessageId(), subscriber.getSubscriptionUrl(), 
        domain.getPublicationUrl()))
    elif domain.domain_type == self.SUB:
      xml(self.SyncMLHeader(domain.getSessionId(), domain.incrementMessageId(),
        domain.getPublicationUrl(), domain.getSubscriptionUrl()))
    
    # Add or replace objects
    syncml_data = ''

    # syncml body
    xml(' <SyncBody>\n')

    # status for SyncHdr
    message_id = self.getMessageId(remote_xml)
    xml('  <Status>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    cmd_id += 1
    xml('   <MsgRef>%s</MsgRef>\n' % message_id)
    xml('   <CmdRef>0</CmdRef>\n') #to make reference to the SyncHdr, it's 0
    xml('   <Cmd>SyncHdr</Cmd>\n')
    xml('   <TargetRef>%s</TargetRef>\n' \
      % remote_xml.xpath('string(//SyncHdr/Target/LocURI)').encode('utf-8'))
    xml('   <SourceRef>%s</SourceRef>\n' \
      % remote_xml.xpath('string(//SyncHdr/Source/LocURI)').encode('utf-8'))
    xml('   <Data>200</Data>\n')
    xml('  </Status>\n')

    #list of element in the SyncBody bloc
    syncbody_element_list = remote_xml.xpath('//SyncBody/*')
    
    #add the status bloc corresponding to the receive command
    for syncbody_element in syncbody_element_list:
      if str(syncbody_element.nodeName) not in ('Status', 'Final', 'Replace'):
        xml('  <Status>\n')
        xml('   <CmdID>%s</CmdID>\n' % cmd_id)
        cmd_id += 1
        xml('   <MsgRef>%s</MsgRef>\n' % message_id)
        xml('   <CmdRef>%s</CmdRef>\n' \
            % syncbody_element.xpath('string(.//CmdID)').encode('utf-8'))
        xml('   <Cmd>%s</Cmd>\n' % syncbody_element.nodeName.encode('utf-8'))

        target_ref = syncbody_element.xpath('string(.//Target/LocURI)').encode('utf-8')
        if target_ref not in (None, ''):
          xml('   <TargetRef>%s</TargetRef>\n' % target_ref )
        source_ref = syncbody_element.xpath('string(.//Source/LocURI)').encode('utf-8')
        if source_ref not in (None, ''):
          xml('   <SourceRef>%s</SourceRef>\n' % source_ref )

        #xml('   <Data>%s</Data>\n' % subscriber.getSynchronizationType())
        if syncbody_element.nodeName.encode('utf-8') == 'Add':
          xml('   <Data>%s</Data>\n' % '201')
        else:
          xml('   <Data>%s</Data>\n' % '200')

       # if syncbody_element.xpath('.//Item') not in ([], None, '') and\
       #     syncbody_element.xpath('.//Item.....'): #contient une ancre Next...

        xml('   <Item>\n')
        xml('    <Data>\n')
        xml('     <Anchor xmlns="syncml:metinf">\n')
        xml('      <Next>%s</Next>\n' % subscriber.getNextAnchor())
        xml('     </Anchor>\n')
        xml('    </Data>\n')
        xml('   </Item>\n')

        xml('  </Status>\n')

    destination_url = ''
    # alert message if we want more data
    if destination_waiting_more_data == 1:
      xml(self.SyncMLAlert(cmd_id, self.WAITING_DATA,
                              subscriber.getTargetURI(),
                              subscriber.getSourceURI(),
                              subscriber.getLastAnchor(),
                              subscriber.getNextAnchor()))
    # Now we should send confirmations
    cmd_id_before_getsyncmldata = cmd_id
    cmd_id = cmd_id+1
    if getattr(domain, 'getActivityEnabled', None) and domain.getActivityEnabled():
      #use activities to get SyncML data.
      if not (isinstance(remote_xml, str) or isinstance(remote_xml, unicode)):
        string_io = StringIO()
        PrettyPrint(remote_xml,stream=string_io)
        remote_xml = string_io.getvalue()
      self.activate().SyncModifActivity(
                      domain_relative_url = domain.getRelativeUrl(),
                      remote_xml = remote_xml,
                      subscriber_relative_url = subscriber.getRelativeUrl(),
                      cmd_id = cmd_id,
                      xml_confirmation = xml_confirmation,
                      syncml_data = '',
                      cmd_id_before_getsyncmldata = cmd_id_before_getsyncmldata,
                      xml_list = xml_list,
                      has_status_list = has_status_list,
                      has_response = has_response )
      return {'has_response':1, 'xml':''}
    else:
      result = self.getSyncMLData(domain=domain,
                             remote_xml=remote_xml,
                             subscriber=subscriber,
                             cmd_id=cmd_id,xml_confirmation=xml_confirmation,
                             conduit=conduit)
      syncml_data = result['syncml_data']
      xml_confirmation = result['xml_confirmation']
      cmd_id = result['cmd_id']
      return self.sendSyncModif(syncml_data, cmd_id_before_getsyncmldata,
                                subscriber, domain, xml_confirmation,
                                remote_xml, xml_list, has_status_list, has_response)

  def SyncModifActivity(self, **kw):
    domain = self.unrestrictedTraverse(kw['domain_relative_url'])
    subscriber = self.unrestrictedTraverse(kw['subscriber_relative_url'])
    conduit = subscriber.getConduit()
    result = self.getSyncMLData(domain = domain, subscriber = subscriber,
                                conduit = conduit, max = 100, **kw)
    syncml_data = result['syncml_data']
    kw['syncml_data'] = syncml_data
    finished = result['finished']
    if not finished:
      self.activate().SyncModifActivity(**kw)
    else:
      xml_confirmation = result['xml_confirmation']
      cmd_id = result['cmd_id']
      cmd_id_before_getsyncmldata = kw['cmd_id_before_getsyncmldata']
      remote_xml = Parse(kw['remote_xml'])
      xml_list = kw['xml_list']
      has_status_list = kw['has_status_list']
      has_response = kw['has_response']
      return self.sendSyncModif(syncml_data, cmd_id_before_getsyncmldata,
                              subscriber, domain, xml_confirmation,
                              remote_xml, xml_list, has_status_list, has_response)

  def sendSyncModif(self, syncml_data, cmd_id_before_getsyncmldata, subscriber,
                    domain, xml_confirmation, remote_xml, xml_list,
                    has_status_list, has_response):
    xml = xml_list.append
    if syncml_data != '':
      xml('  <Sync>\n')
      xml('   <CmdID>%s</CmdID>\n' % cmd_id_before_getsyncmldata)
      if domain.domain_type == self.SUB:
        if subscriber.getTargetURI() not in ('', None):
          xml('   <Target>\n')
          xml('    <LocURI>%s</LocURI>\n' % subscriber.getTargetURI())
          xml('   </Target>\n')
        if subscriber.getSourceURI() not in ('', None):
          xml('   <Source>\n')
          xml('    <LocURI>%s</LocURI>\n' % subscriber.getSourceURI())
          xml('   </Source>\n')
      elif domain.domain_type == self.PUB:
        if domain.getTargetURI() not in ('', None):
          xml('   <Target>\n')
          xml('    <LocURI>%s</LocURI>\n' % domain.getTargetURI())
          xml('   </Target>\n')
        if domain.getSourceURI() not in ('', None):
          xml('   <Source>\n')
          xml('    <LocURI>%s</LocURI>\n' % domain.getSourceURI())
          xml('   </Source>\n')
      xml(syncml_data)
      xml('  </Sync>\n')
    xml(xml_confirmation)
    xml('  <Final/>\n')
    xml(' </SyncBody>\n')
    xml('</SyncML>\n')
    xml_a = ''.join(xml_list)

    if domain.domain_type == self.PUB: # We always reply
      subscriber.setLastSentMessage(xml_a)
      self.sendResponse(from_url=domain.publication_url, 
          to_url=subscriber.subscription_url, sync_id=domain.getTitle(), 
          xml=xml_a,domain=domain)
      has_response = 1
    elif domain.domain_type == self.SUB:
      if self.checkAlert(remote_xml) or \
          (xml_confirmation,syncml_data)!=('','') or \
          has_status_list:
        subscriber.setLastSentMessage(xml_a)
        self.sendResponse(from_url=domain.subscription_url, 
            to_url=domain.publication_url, sync_id=domain.getTitle(), 
            xml=xml_a,domain=domain)
        has_response = 1
    return {'has_response':has_response,'xml':xml_a}
