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
from xml.dom.ext.reader.Sax2 import FromXml
from xml.dom.minidom import parse, parseString
from DateTime import DateTime
from cStringIO import StringIO
from xml.dom.ext import PrettyPrint
import random
try:
  from Products.CMFActivity.ActiveObject import ActiveObject
except ImportError:
  LOG('XMLSyncUtils',0,"Can't import ActiveObject")
  class ActiveObject:
    pass
import commands
from zLOG import LOG

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
      xml('    <Format>%s</Format>\n' % authentication_format)
      xml('    <Type>%s</Type>\n' % authentication_type)
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

  def SyncMLConfirmation(self, cmd_id, target_ref, sync_code, cmd):
    """
    This is used in order to confirm that an object was correctly
    synchronized
    """
    xml_list = []
    xml = xml_list.append
    xml('  <Status>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    xml('   <TargetRef>%s</TargetRef>\n' % target_ref)
    xml('   <Cmd>%s</Cmd>\n' % cmd)
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
    xml('     <Format>%s</Format>\n' % auth_format)
    xml('     <Type>%s</Type>\n' % auth_type)
    xml('    </Meta>\n')
    xml('   </Chal>\n')
    xml('   <Data>%s</Data>\n' % str(data_code))
    xml('  </Status>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def sendMail(self, fromaddr, toaddr, id_sync, msg):
    """
      Send a message via email
      - sync_object : this is a publication or a subscription
      - message : what we want to send
    """
    header = "Subject: %s\n" % id_sync
    header += "To: %s\n\n" % toaddr
    msg = header + msg
    LOG('SubSendMail',0,'from: %s, to: %s' % (fromaddr,toaddr))
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddr, msg)
    # if we want to send the email to someone else (debugging)
    #server.sendmail(fromaddr, "seb@localhost", msg)
    server.quit()

  def addXMLObject(self, cmd_id=0, object=None, xml_string=None,
                   more_data=0,gid=None):
    """
      Add an object with the SyncML protocol
    """
    xml_list = []
    xml = xml_list.append
    xml('   <Add>\n')
    xml('    <CmdID>%s</CmdID>\n' % cmd_id)
    xml('    <Meta><Type>%s</Type></Meta>\n' % object.portal_type)
    xml('    <Item>\n')
    xml('     <Source>\n')
    xml('      <LocURI>%s</LocURI>\n' % gid)
    xml('     </Source>\n')
    xml('     <Data>\n')
    xml(xml_string)
    xml('     </Data>\n')
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
    xml('     <Data>\n')
    xml('     </Data>\n')
    xml('    </Item>\n')
    xml('   </Delete>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def replaceXMLObject(self, cmd_id=0, object=None, xml_string=None,
                       more_data=0,gid=None):
    """
      Replace an object with the SyncML protocol
    """
    xml_list = []
    xml = xml_list.append
    xml('   <Replace>\n')
    xml('    <CmdID>%s</CmdID>\n' % cmd_id)
    xml('    <Meta><Type>%s</Type></Meta>\n' % object.portal_type)
    xml('    <Item>\n')
    xml('     <Source>\n')
    xml('      <LocURI>%s</LocURI>\n' % str(gid))
    xml('     </Source>\n')
    xml('     <Data>\n')
    xml(xml_string)
    xml('     </Data>\n')
    if more_data == 1:
      xml('     <MoreData/>\n')
    xml('    </Item>\n')
    xml('   </Replace>\n')
    xml_a = ''.join(xml_list)
    return xml_a

  def getXupdateObject(self, object=None, xml_mapping=None, old_xml=None):
    """
    Generate the xupdate with the new object and the old xml
    We have to use xmldiff as a command line tool, because all
    over the xmldiff code, there's some print to the standard
    output, so this is unusable
    """
    filename = str(random.randrange(1,2147483600))
    old_filename = filename + '.old'
    new_filename = filename + '.new'
    file1 = open('/tmp/%s' % new_filename,'w')
    file1.write(self.getXMLObject(object=object,xml_mapping=xml_mapping))
    file1.close()
    file2 = open('/tmp/%s'% old_filename,'w')
    file2.write(old_xml)
    file2.close()
    xupdate = commands.getoutput('erp5diff /tmp/%s /tmp/%s' % 
        (old_filename,new_filename))
    xupdate = xupdate[xupdate.find('<xupdate:modifications'):]
    commands.getstatusoutput('rm -f /tmp/%s' % old_filename)
    commands.getstatusoutput('rm -f /tmp/%s' % new_filename)
    return xupdate

  def getXMLObject(self, object=None, xml_mapping=None):
    """
    This just allow to get the xml of the object
    """
    xml_method = None
    xml = ""
    if xml_mapping is not None:
      if hasattr(object,xml_mapping):
        xml_method = getattr(object,xml_mapping)
      elif hasattr(object,'manage_FTPget'):
        xml_method = getattr(object,'manage_FTPget')
      if xml_method is not None:
        xml = xml_method()
    return xml

  def getSessionId(self, xml):
    """
    We will retrieve the session id of the message
    """
    session_id = 0
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'SyncML':
        for subnode1 in self.getElementNodeList(subnode):
          if subnode1.nodeName == 'SyncHdr':
            for subnode2 in self.getElementNodeList(subnode1):
              if subnode2.nodeName == 'SessionID':
                session_id = int(subnode2.childNodes[0].data)
    return session_id
    
    
  def getMessageId(self, xml):
    """
    We will retrieve the message id of the message
    """
    message_id = 0
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'SyncML':
        for subnode1 in self.getElementNodeList(subnode):
          if subnode1.nodeName == 'SyncHdr':
            for subnode2 in self.getElementNodeList(subnode1):
              if subnode2.nodeName == 'MsgID':
                message_id = int(subnode2.childNodes[0].data)
    return message_id

  def getTarget(self, xml):
    """
    return the target in the SyncHdr section
    """
    url = ''
    for subnode in self.getElementNodeList(xml):
      if subnode.nodeName == 'SyncML':
        for subnode1 in self.getElementNodeList(subnode):
          if subnode1.nodeName == 'SyncHdr':
            for subnode2 in self.getElementNodeList(subnode1):
              if subnode2.nodeName == 'Target':
                for subnode3 in self.getElementNodeList(subnode2):
                  if subnode3.nodeName == 'LocURI':
                    url = subnode3.childNodes[0].data
    return url


  def getAlertLastAnchor(self, xml_stream):
    """
      Return the value of the last anchor, in the
      alert section of the xml_stream
    """
    first_node = xml_stream.childNodes[0]

    # Get informations from the body
    client_body = first_node.childNodes[3]
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and \
          subnode.nodeName == "Alert":
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and \
              subnode2.nodeName == "Item":
            for subnode3 in subnode2.childNodes:
              if subnode3.nodeType == subnode3.ELEMENT_NODE and \
                  subnode3.nodeName == "Meta":
                for subnode4 in subnode3.childNodes:
                  if subnode4.nodeType == subnode4.ELEMENT_NODE and \
                      subnode4.nodeName == "Anchor":
                    for subnode5 in subnode4.childNodes:
                      # Get the last time we had a synchronization
                     if subnode5.nodeType == subnode5.ELEMENT_NODE and \
                         subnode5.nodeName == "Last":
                        last_anchor = subnode5.childNodes[0].data
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
    if client_body.nodeName != "SyncBody":
      print "This is not a SyncML Body"
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and \
          subnode.nodeName == "Alert":
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and \
              subnode2.nodeName == "Item":
            for subnode3 in subnode2.childNodes:
              if subnode3.nodeType == subnode3.ELEMENT_NODE and \
                  subnode3.nodeName == "Meta":
                for subnode4 in subnode3.childNodes:
                 if subnode4.nodeType == subnode4.ELEMENT_NODE and \
                     subnode4.nodeName == "Anchor":
                    for subnode5 in subnode4.childNodes:
                      # Get the last time we had a synchronization
                      if subnode5.nodeType == subnode5.ELEMENT_NODE and \
                          subnode5.nodeName == "Next":
                        next_anchor = subnode5.childNodes[0].data
                        return next_anchor

  def getStatusTarget(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    # Get informations from the body
    if xml.nodeName=='Status':
      for subnode in xml.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and \
            subnode.nodeName == 'TargetRef':
          return subnode.childNodes[0].data
    return None

  def getStatusCode(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    # Get informations from the body
    if xml.nodeName=='Status':
      for subnode in xml.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and \
            subnode.nodeName == 'Data':
          return int(subnode.childNodes[0].data)
    return None

  def getStatusCommand(self, xml):
    """
      Return the value of the command inside the xml_stream
    """
    # Get informations from the body
    if xml.nodeName=='Status':
      for subnode in xml.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Cmd':
          return subnode.childNodes[0].data
    return None

  def getCred(self, xml):
    """
      return the credential information : type, format and data
    """    
    format=''
    type=''
    data=''
    

    first_node = xml.childNodes[0]
    if first_node.nodeName != "SyncML":
      print "This is not a SyncML message"
    # Get informations from the header
    xml_header = first_node.childNodes[1]
    if xml_header.nodeName != "SyncHdr":
      LOG('PubSyncModif',0,'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"

    for subnode in xml_header.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName=='Cred':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and \
              subnode2.nodeName == 'Meta':
            for subnode3 in subnode2.childNodes:
              if subnode3.nodeType == subnode3.ELEMENT_NODE and \
                  subnode3.nodeName == 'Format':
                    if len(subnode3.childNodes) > 0:
                      format=subnode3.childNodes[0].data
              if subnode3.nodeType == subnode3.ELEMENT_NODE and \
                  subnode3.nodeName == 'Type':
                    if len(subnode3.childNodes) > 0:
                      type=subnode3.childNodes[0].data
          if subnode2.nodeType == subnode2.ELEMENT_NODE and \
              subnode2.nodeName == 'Data':
                if len(subnode2.childNodes) > 0:
                  data=subnode2.childNodes[0].data
    return (format, type, data)

  def getAlertCode(self, xml_stream):
    """
      Return the value of the alert code inside the full syncml message
    """
    # Get informations from the body
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      LOG('XMLSyncUtils.getAlertCode',0,"This is not a SyncML Body")
      raise ValueError, "Sorry, This is not a SyncML Body"
    alert = 0
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName=='Alert':
        for subnode1 in subnode.childNodes:
          if subnode1.nodeType == subnode1.ELEMENT_NODE and subnode1.nodeName == 'Data':
            return int(subnode1.childNodes[0].data)
    return None

  def checkCred(self, xml_stream):
    """
      Check if there's a Cred section in the xml_stream
    """
    first_node = xml_stream.childNodes[0]
    # Get informations from the header
    xml_header = first_node.childNodes[1]
    if xml_header.nodeName != "SyncHdr":
      LOG('PubSyncModif',0,'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"
    cred = 0
    for subnode in xml_header.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Cred":
        cred=1
    return cred

  def checkAlert(self, xml_stream):
    """
      Check if there's an Alert section in the xml_stream
    """
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      print "This is not a SyncML Body"
    alert = 0
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Alert":
        alert = 1
    return alert

  def checkSync(self, xml_stream):
    """
      Check if there's an Sync section in the xml_xtream
    """
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      LOG('checkSync',0,"This is not a SyncML Body")
      raise ValueError, "Sorry, This is not a SyncML Body"
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Sync":
        return 1
    return 0

  def CheckStatus(self, xml_stream):
    """
      Check if there's a Status section in the xml_xtream
    """
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      print "This is not a SyncML Body"
    status = None
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Status":
        status = "1"
    return status

  def getNextSyncAction(self, xml_stream, last_action):
    """
      It goes throw actions in the Sync section of the SyncML file,
      then it returns the next action (could be "add", "replace",
      "delete").
    """
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      print "This is not a SyncML Body"
    next_action = None
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Sync":
        # if we didn't use this method before
        if last_action == None and len(subnode.childNodes) > 1:
          next_action = subnode.childNodes[1]
        else:
          found = None
          for subnode2 in subnode.childNodes:
            if subnode2.nodeType == subnode.ELEMENT_NODE and subnode2 != last_action and found is None:
              pass
            elif subnode2.nodeType == subnode.ELEMENT_NODE and subnode2 == last_action and found is None:
              found = 1
            elif subnode2.nodeType == subnode.ELEMENT_NODE and found is not None:
              next_action = subnode2
              break
    return next_action

  def getNextSyncBodyStatus(self, xml_stream, last_status):
    """
      It goes throw actions in the Sync section of the SyncML file,
      then it returns the next action (could be "add", "replace",
      "delete").
    """
    first_node = xml_stream.childNodes[0]
    client_body = first_node.childNodes[3]
    if client_body.nodeName != "SyncBody":
      LOG('getNextSyncBodyStatus',0,"This is not a SyncML Body")
      raise ValueError, "Sorry, This is not a SyncML Body"
    next_status = None
    found = None
    for subnode in client_body.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Status":
        # if we didn't use this method before
        if last_status == None:
          next_status = subnode
          return next_status
        elif subnode == last_status and found is None:
          found = 1
        elif found is not None:
          return subnode
    return next_status

  def getDataSubNode(self, action):
    """
      Return the node starting with <object....> of the action
    """
    for subnode in action.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Item':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'Data':
            for subnode3 in subnode2.childNodes:
              #if subnode3.nodeType == subnode3.ELEMENT_NODE and subnode3.nodeName == 'object':
              if subnode3.nodeType == subnode3.ELEMENT_NODE:
                return subnode3

  def getPartialData(self, action):
    """
      Return the node starting with <object....> of the action
    """
    for subnode in action.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Item':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'Data':
            for subnode3 in subnode2.childNodes:
              #if subnode3.nodeType == subnode3.ELEMENT_NODE and subnode3.nodeName == 'object':
              if subnode3.nodeType == subnode3.COMMENT_NODE:
                # No need to remove comment, it is already done by FromXml
                #if subnode3.data.find('<!--')>=0:
                #  data = subnode3.data
                #  data = data[data.find('<!--')+4:data.rfind('-->')]
                xml = subnode3.data
		if isinstance(xml, unicode):
                  xml = xml.encode('utf-8')
                return xml

    return None


  def getAttributeNodeList(self, node):
    """
      Return attributesNodes that are ElementNode XXX may be not needed at all
    """
    subnode_list = []
    for subnode in node.attributes:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE:
        subnode_list += [subnode]
    return subnode_list

  def getActionId(self, action):
    """
      Return the rid of the object described by the action
    """
    for subnode in action.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Item':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'Source':
            for subnode3 in subnode2.childNodes:
              if subnode3.nodeType == subnode3.ELEMENT_NODE and subnode3.nodeName == 'LocURI':
                return str(subnode3.childNodes[0].data)

  def checkActionMoreData(self, action):
    """
      Return the rid of the object described by the action
    """
    for subnode in action.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Item':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'MoreData':
            return 1
    return 0

  def getActionType(self, action):
    """
      Return the type of the object described by the action
    """
    for subnode in action.childNodes:
      if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == 'Meta':
        for subnode2 in subnode.childNodes:
          if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'Type':
            return str(subnode2.childNodes[0].data)

  def getElementNodeList(self, node):
    """
      Return childNodes that are ElementNode
    """
    #return node.getElementsByTagName('*')
    subnode_list = []
    for subnode in node.childNodes or []:
      if subnode.nodeType == subnode.ELEMENT_NODE:
        subnode_list += [subnode]
    return subnode_list

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
    attribute_list = []
    for subnode in node.attributes.values() or []:
      if subnode.nodeType == subnode.ATTRIBUTE_NODE:
        attribute_list += [subnode]
    return attribute_list

  def getSyncMLData(self, domain=None,remote_xml=None,cmd_id=0,
                          subscriber=None,destination_path=None,
                          xml_confirmation=None,conduit=None):
    """
    This generate the syncml data message. This returns a string
    with all modification made locally (ie replace, add ,delete...)

    if object is not None, this usually means we want to set the
    actual xupdate on the signature.
    """
    local_gid_list = []
    syncml_data = ''

    if subscriber.getRemainingObjectPathList() is None:
      object_list = domain.getObjectList()
      object_path_list = map(lambda x: x.getPhysicalPath(),object_list)
      LOG('getSyncMLData, object_path_list',0,object_path_list)
      subscriber.setRemainingObjectPathList(object_path_list)

      #object_gid = domain.getGidFromObject(object)
      local_gid_list = map(lambda x: domain.getGidFromObject(x),object_list)
      # Objects to remove
      #for object_id in id_list:
      for object_gid in subscriber.getGidList():
        if not (object_gid in local_gid_list):
          # This is an object to remove
          signature = subscriber.getSignature(object_gid)
          if signature.getStatus()!=self.PARTIAL: # If partial, then we have a signature
                                                  # but no local object
            xml_object = signature.getXML()
            if xml_object is not None: # This prevent to delete an object that we
                                      # were not able to create
              syncml_data += self.deleteXMLObject(xml_object=signature.getXML() or '',
                                                  object_gid=object_gid,cmd_id=cmd_id)

    local_gid_list = []
    #for object in domain.getObjectList():
    for object_path in subscriber.getRemainingObjectPathList():
      #object = subscriber.getDestination()._getOb(object_id)
      #object = subscriber.getDestination()._getOb(object_id)
      #try:
      object = self.unrestrictedTraverse(object_path)
      #except KeyError:
      #object = None
      status = self.SENT
      #gid_generator = getattr(object,domain.getGidGenerator(),None)
      object_gid = domain.getGidFromObject(object)
      local_gid_list += [object_gid]
      #if gid_generator is not None:
      #  object_gid = gid_generator()
      force = 0
      if syncml_data.count('\n') < self.MAX_LINES and not object.id.startswith('.'): # If not we have to cut
        #LOG('getSyncMLData',0,'xml_mapping: %s' % str(domain.xml_mapping))
        #LOG('getSyncMLData',0,'code: %s' % str(self.getAlertCode(remote_xml)))
        #LOG('getSyncMLData',0,'gid_list: %s' % str(local_gid_list))
        #LOG('getSyncMLData',0,'hasSignature: %s' % str(subscriber.hasSignature(object_gid)))
        #LOG('getSyncMLData',0,'alert_code == slowsync: %s' % str(self.getAlertCode(remote_xml)==self.SLOW_SYNC))
        signature = subscriber.getSignature(object_gid)
        #LOG('getSyncMLData',0,'current object: %s' % str(object.getId()))
        # Here we first check if the object was modified or not by looking at dates
        if signature is not None:
          signature.checkSynchronizationNeeded(object)
        status = self.SENT
        more_data=0
        # For the case it was never synchronized, we have to send everything
        if signature is not None and signature.getXMLMapping()==None:
          pass
        elif signature==None or (signature.getXML()==None and signature.getStatus()!=self.PARTIAL) or \
            self.getAlertCode(remote_xml)==self.SLOW_SYNC:
          #LOG('PubSyncModif',0,'Current object.getPath: %s' % object.getPath())
          LOG('getSyncMLData',0,'no signature for gid: %s' % object_gid)
          xml_object = self.getXMLObject(object=object,xml_mapping=domain.xml_mapping)
          xml_string = xml_object
          signature = Signature(gid=object_gid,id=object.getId(),object=object)
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
              #LOG('XMLSyncUtils',0,'rest_string: %s' % str(rest_string))
              i += 1
            #LOG('getSyncMLData',0,'setPartialXML with: %s' % str(rest_string))
            signature.setPartialXML(rest_string)
            status =self.PARTIAL
            signature.setAction('Add')
            xml_string = '<!--' + short_string + '-->'
          syncml_data += self.addXMLObject(cmd_id=cmd_id, object=object,gid=object_gid,
                                  xml_string=xml_string, more_data=more_data)
          cmd_id += 1
          signature.setStatus(status)
          subscriber.addSignature(signature)
        elif signature.getStatus()==self.NOT_SYNCHRONIZED \
            or signature.getStatus()==self.PUB_CONFLICT_MERGE: # We don't have synchronized this object yet
          xml_object = self.getXMLObject(object=object,xml_mapping=domain.xml_mapping)
          #LOG('getSyncMLData',0,'checkMD5: %s' % str(signature.checkMD5(xml_object)))
          #LOG('getSyncMLData',0,'getStatus: %s' % str(signature.getStatus()))
          if signature.getStatus()==self.PUB_CONFLICT_MERGE:
            xml_confirmation += self.SyncMLConfirmation(cmd_id,object.id,
                                  self.CONFLICT_MERGE,'Replace')
          set_synchronized = 1
          if not signature.checkMD5(xml_object):
            set_synchronized = 0
            # This object has changed on this side, we have to generate some xmldiff
            xml_string = self.getXupdateObject(object=object,
                                              xml_mapping=domain.xml_mapping,
                                              old_xml=signature.getXML())
            if xml_string.count('\n') > self.MAX_LINES:
              if xml_string.find('--') >= 0: # This make comment fails, so we need to replace
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
            syncml_data += self.replaceXMLObject(cmd_id=cmd_id,object=object,gid=object_gid,
                                                xml_string=xml_string, more_data=more_data)
            cmd_id += 1
            signature.setTempXML(xml_object)
          # Now we can apply the xupdate from the subscriber
          subscriber_xupdate = signature.getSubscriberXupdate()
          #LOG('getSyncMLData subscriber_xupdate',0,subscriber_xupdate)
          if subscriber_xupdate is not None:
            old_xml = signature.getXML()
            conduit.updateNode(xml=subscriber_xupdate, object=object,
                              previous_xml=old_xml,force=(domain.getDomainType==self.SUB),
                              simulate=0)
            xml_object = self.getXMLObject(object=object,xml_mapping=domain.xml_mapping)
            signature.setTempXML(xml_object)
          if set_synchronized: # We have to do that after this previous update
            # We should not have this case when we are in CONFLICT_MERGE
            signature.setStatus(self.SYNCHRONIZED)
        elif signature.getStatus()==self.PUB_CONFLICT_CLIENT_WIN:
          # We have decided to apply the update
          LOG('getSyncMLData',0,'signature.getTempXML(): %s' % str(signature.getTempXML()))
          # XXX previous_xml will be getXML instead of getTempXML because
          # some modification was already made and the update
          # may not apply correctly
          xml_update = signature.getPartialXML()
          conduit.updateNode(xml=signature.getPartialXML(), object=object,
                            previous_xml=signature.getXML(),force=1)
          xml_confirmation += self.SyncMLConfirmation(cmd_id,object_gid,
                                self.CONFLICT_CLIENT_WIN,'Replace')
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
          if signature.getAction()=='Replace':
            syncml_data += self.replaceXMLObject(cmd_id=cmd_id,object=object,gid=object_gid,
                                                xml_string=xml_string, more_data=more_data)
          elif signature.getAction()=='Add':
            syncml_data += self.addXMLObject(cmd_id=cmd_id, object=object,gid=object_gid,
                                    xml_string=xml_string, more_data=more_data)
    return (syncml_data,xml_confirmation,cmd_id)

  def applyActionList(self, domain=None, subscriber=None,destination_path=None,
                      cmd_id=0,remote_xml=None,conduit=None,simulate=0):
    """
    This just look to a list of action to do, then id applies
    each action one by one, thanks to a conduit
    """
    next_action = self.getNextSyncAction(remote_xml, None)
    xml_confirmation = ''
    has_next_action = 0
    if next_action is not None:
      has_next_action = 1
    while next_action != None:
      conflict_list = []
      status_code = self.SUCCESS
      # Thirst we have to check the kind of action it is
      partial_data = self.getPartialData(next_action)
      object_gid = self.getActionId(next_action)
      signature = subscriber.getSignature(object_gid)
      object = domain.getObjectFromGid(object_gid)
      if signature == None:
        LOG('applyActionList, signature is None',0,signature)
        signature = Signature(gid=object_gid,status=self.NOT_SYNCHRONIZED,object=object).__of__(subscriber)
        subscriber.addSignature(signature)
      force = signature.getForce()
      LOG('applyActionList',0,'object: %s' % repr(object))
      if self.checkActionMoreData(next_action) == 0:
        data_subnode = None
        if partial_data != None:
          signature_partial_xml = signature.getPartialXML()
          if signature_partial_xml is not None:
            data_subnode = signature.getPartialXML() + partial_data
          else:
            data_subnode = partial_data
          LOG('SyncModif',0,'data_subnode: %s' % data_subnode)
          #data_subnode = FromXml(data_subnode)
          data_subnode = parseString(data_subnode)
          data_subnode = data_subnode.childNodes[0] # Because we just created a new xml
          # document, with childNodes[0] a DocumentType and childNodes[1] the Element Node
        else:
          data_subnode = self.getDataSubNode(next_action)
        if next_action.nodeName == 'Add':
          # Then store the xml of this new subobject
          if object is None:
            object_id = domain.generateNewIdWithGenerator(object=destination_path,gid=object_gid)
            #if object_id is not None:
            add_data = conduit.addNode(xml=data_subnode, object=destination_path,
                                             object_id=object_id)
            conflict_list += add_data['conflict_list']
            # Retrieve directly the object from addNode
            object = add_data['object']
            LOG('XMLSyncUtils, in ADD add_data',0,add_data)
            signature.setPath(object.getPhysicalPath())
            LOG('applyActionList',0,'object after add: %s' % repr(object))
          if object is not None:
            LOG('SyncModif',0,'addNode, found the object')
            #mapping = getattr(object,domain.getXMLMapping(),None)
            xml_object = domain.getXMLFromObject(object)
            #if mapping is not None:
            #  xml_object = mapping()
            signature.setStatus(self.SYNCHRONIZED)
            signature.setId(object.getId())
            signature.setPath(object.getPhysicalPath())
            signature.setXML(xml_object)
            xml_confirmation +=\
                 self.SyncMLConfirmation(cmd_id,object_gid,self.SUCCESS,'Add')
            cmd_id +=1
        elif next_action.nodeName == 'Replace':
          LOG('SyncModif',0,'object: %s will be updated...' % str(object))
          if object is not None:
            LOG('SyncModif',0,'object: %s will be updated...' % object.id)
            signature = subscriber.getSignature(object_gid)
            LOG('SyncModif',0,'previous signature: %s' % str(signature))
            previous_xml = signature.getXML()
            #LOG('SyncModif',0,'previous signature: %i' % len(previous_xml))
            conflict_list += conduit.updateNode(xml=data_subnode, object=object,
                              previous_xml=signature.getXML(),force=force,
                              simulate=simulate)
            #mapping = getattr(object,domain.getXMLMapping(),None)
            xml_object = domain.getXMLFromObject(object)
            #if mapping is not None:
            #  xml_object = mapping()
            signature.setTempXML(xml_object)
            if conflict_list != []:
              status_code = self.CONFLICT
              signature.setStatus(self.CONFLICT)
              signature.setConflictList(signature.getConflictList()+conflict_list)
              string_io = StringIO()
              PrettyPrint(data_subnode,stream=string_io)
              data_subnode_string = string_io.getvalue()
              signature.setPartialXML(data_subnode_string)
            elif not simulate:
              signature.setStatus(self.SYNCHRONIZED)
            xml_confirmation += self.SyncMLConfirmation(cmd_id,
                                        object_gid,status_code,'Replace')
            cmd_id +=1
            if simulate:
              # This means we are on the publiher side and we want to store
              # the xupdate from the subscriber and we also want to generate
              # the current xupdate from the last synchronization
              string_io = StringIO()
              PrettyPrint(data_subnode,stream=string_io)
              data_subnode_string = string_io.getvalue()
              LOG('applyActionList, subscriber_xupdate:',0,data_subnode_string)
              signature.setSubscriberXupdate(data_subnode_string)

        elif next_action.nodeName == 'Delete':
          object_id = signature.getId()
          conduit.deleteNode(xml=self.getDataSubNode(next_action), object=destination_path,
                             object_id=object_id)
          subscriber.delSignature(object_gid)
          xml_confirmation += self.SyncMLConfirmation(cmd_id,
                                      object_gid,status_code,'Delete')
      else: # We want to retrieve more data
        signature.setStatus(self.PARTIAL)
        #LOG('SyncModif',0,'setPartialXML: %s' % str(previous_partial))
        previous_partial = signature.getPartialXML() or ''
        #if previous_partial.find(partial_data)<0: # XXX bad thing
        previous_partial += partial_data
        signature.setPartialXML(previous_partial)
        #LOG('SyncModif',0,'previous_partial: %s' % str(previous_partial))
        LOG('SyncModif',0,'waiting more data for :%s' % signature.getId())
        xml_confirmation += self.SyncMLConfirmation(cmd_id,object_gid,
                                                self.WAITING_DATA,next_action.nodeName)
      if conflict_list != [] and signature is not None:
        # We had a conflict
        signature.setStatus(self.CONFLICT)

      next_action = self.getNextSyncAction(remote_xml, next_action)
    return (xml_confirmation,has_next_action,cmd_id)

  def applyStatusList(self, subscriber=None,remote_xml=None):
    """
    This read a list of status list (ie syncml confirmations).
    This method have to change status codes on signatures
    """
    next_status = self.getNextSyncBodyStatus(remote_xml, None)
    LOG('applyStatusList, next_status',0,next_status)
    # We do not want the first one
    next_status = self.getNextSyncBodyStatus(remote_xml, next_status)
    has_status_list = 0
    if next_status is not None:
      has_status_list = 1
    destination_waiting_more_data = 0
    while next_status != None:
      object_gid = self.getStatusTarget(next_status)
      status_code = self.getStatusCode(next_status)
      status_cmd = self.getStatusCommand(next_status)
      signature = subscriber.getSignature(object_gid)
      LOG('SyncModif',0,'next_status: %s' % str(status_code))
      if status_cmd in ('Add','Replace'):
        if status_code == self.CHUNK_OK:
          destination_waiting_more_data = 1
          signature.setStatus(self.PARTIAL)
        elif status_code == self.CONFLICT:
          signature.setStatus(self.CONFLICT)
        elif status_code == self.CONFLICT_MERGE:
          # We will have to apply the update, and we should not care about conflicts
          # so we have to force the update
          signature.setStatus(self.NOT_SYNCHRONIZED)
          signature.setForce(1)
        elif status_code == self.CONFLICT_CLIENT_WIN:
          # The server was agree to apply our updates, nothing to do
          signature.setStatus(self.SYNCHRONIZED)
        elif status_code == self.SUCCESS:
          signature.setStatus(self.SYNCHRONIZED)
      elif status_cmd == 'Delete':
        if status_code == self.SUCCESS:
          subscriber.delSignature(object_gid)
      next_status = self.getNextSyncBodyStatus(remote_xml, next_status)
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

  def SyncModif(self, domain, remote_xml):
    """
    Modification Message, this is used after the first
    message in order to send modifications.
    """
    """
      Send the server modification, this happens after the Synchronization
      initialization
    """
    from Products.ERP5SyncML import Conduit
    has_response = 0 #check if syncmodif replies to this messages
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    LOG('SyncModif',0,'Starting... domain: %s' % str(domain))
    # Get the destination folder
    destination_path = self.unrestrictedTraverse(domain.getDestinationPath())

    first_node = remote_xml.childNodes[0]
    # Get informations from the header
    xml_header = first_node.childNodes[1]
    if xml_header.nodeName != "SyncHdr":
      LOG('PubSyncModif',0,'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"

    subscriber = domain # If we are the client, this is fine
    simulate = 0 # used by applyActionList, should be 0 for client
    if domain.domain_type == self.PUB:
      simulate = 1
      for subnode in xml_header.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Source":
	  for subnode2 in subnode.childNodes:
	    if subnode2.nodeType == subnode2.ELEMENT_NODE and subnode2.nodeName == 'LocURI':
	      subscription_url = str(subnode2.childNodes[0].data)
      subscriber = domain.getSubscriber(subscription_url)

    # We have to check if this message was not already, this can be dangerous
    # to update two times the same object
    message_id = self.getMessageId(remote_xml)
    correct_message = subscriber.checkCorrectRemoteMessageId(message_id)
    if not correct_message: # We need to send again the message
      LOG('SyncModif, no correct message:',0,"sending again...")
      last_xml = subscriber.getLastSentMessage()
      if last_xml != '':
        has_response = 1
        if domain.domain_type == self.PUB: # We always reply
          self.sendResponse(from_url=domain.publication_url, 
              to_url=subscriber.subscription_url, sync_id=domain.getTitle(), 
              xml=last_xml,domain=domain)
        elif domain.domain_type == self.SUB:
          self.sendResponse(from_url=domain.subscription_url, 
              to_url=domain.publication_url, sync_id=domain.getTitle(), xml=last_xml,domain=domain)
      return {'has_response':has_response,'xml':last_xml}
    subscriber.setLastSentMessage('')

    # First apply the list of status codes
    (destination_waiting_more_data,has_status_list) = self.applyStatusList(
                                         subscriber=subscriber,
                                         remote_xml=remote_xml)

    alert_code = self.getAlertCode(remote_xml)
    # Import the conduit and get it
    conduit_name = subscriber.getConduit()
    if conduit_name.startswith('Products'):
      path = conduit_name
      conduit_name = conduit_name.split('.')[-1]
      conduit_module = __import__(path, globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    else:
      conduit_module = __import__('.'.join([Conduit.__name__, conduit_name]),
                                  globals(), locals(), [''])
      conduit = getattr(conduit_module, conduit_name)()
    # Then apply the list of actions
    (xml_confirmation,has_next_action,cmd_id) = self.applyActionList(cmd_id=cmd_id,
                                         domain=domain,
                                         destination_path=destination_path,
                                         subscriber=subscriber,
                                         remote_xml=remote_xml,
                                         conduit=conduit, simulate=simulate)
    #LOG('SyncModif, has_next_action:',0,has_next_action)

    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')
    
    # syncml header
    if domain.domain_type == self.PUB:
      xml(self.SyncMLHeader(subscriber.getSessionId(), subscriber.incrementMessageId(),
          subscriber.getSubscriptionUrl(), domain.getPublicationUrl()))
    elif domain.domain_type == self.SUB:
      xml(self.SyncMLHeader(domain.getSessionId(), domain.incrementMessageId(),
        domain.getPublicationUrl(), domain.getSubscriptionUrl()))


    cmd_id += 1
    # Add or replace objects
    syncml_data = ''
    # Now we have to send our own modifications
    if has_next_action == 0 and not \
      (domain.domain_type==self.SUB and alert_code==self.SLOW_SYNC):
      (syncml_data,xml_confirmation,cmd_id) = self.getSyncMLData(domain=domain,
                                       remote_xml=remote_xml,
                                       subscriber=subscriber,
                                       destination_path=destination_path,
                                       cmd_id=cmd_id,xml_confirmation=xml_confirmation,
                                       conduit=conduit)

    # syncml body
    xml(' <SyncBody>\n')
    destination_url = ''
    if domain.domain_type == self.PUB:
      subscriber.NewAnchor()
      destination_url = domain.getPublicationUrl()
      xml(self.SyncMLStatus(cmd_id, subscriber.getSubscriptionUrl(),
                               domain.getDestinationPath(),
                               subscriber.getSynchronizationType(),
                               subscriber.getNextAnchor()))
    elif domain.domain_type == self.SUB:
      destination_url = domain.getPublicationUrl()
      xml(self.SyncMLStatus(cmd_id, domain.getPublicationUrl(),
                               subscriber.getDestinationPath(),
                               subscriber.getSynchronizationType(),
                               subscriber.getNextAnchor()))
    # alert message if we want more data
    if destination_waiting_more_data == 1:
      xml(self.SyncMLAlert(cmd_id, self.WAITING_DATA,
                              destination_url,
                              domain.getDestinationPath(),
                              subscriber.getLastAnchor(), 
                              subscriber.getNextAnchor()))
    # Now we should send confirmations
    xml(xml_confirmation)
    if syncml_data != '':
      xml('  <Sync>\n')
      xml(syncml_data)
      xml('  </Sync>\n')
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
