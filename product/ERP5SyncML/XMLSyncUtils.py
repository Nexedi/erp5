# -*- coding: utf-8 -*-
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
from Products.ERP5SyncML.Signature import Signature
from AccessControl.SecurityManagement import newSecurityManager
from ERP5Diff import ERP5Diff
from zLOG import LOG, INFO

from lxml import etree
from lxml.builder import ElementMaker
from SyncCode import SYNCML_NAMESPACE
nsmap = {'syncml' : SYNCML_NAMESPACE}
E = ElementMaker(namespace=SYNCML_NAMESPACE, nsmap=nsmap)
parser = etree.XMLParser(remove_blank_text=True)

from xml.dom import minidom

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
    xml = (E.SyncHdr(
            E.VerDTD('1.2'),
            E.VerProto('SyncML/1.2'),
            E.SessionID('%s' % session_id),
            E.MsgID('%s' % msg_id),
          ))
    target_node = E.Target(E.LocURI(target))
    if target_name:
      target_node.append(E.LocName(target_name.decode('utf-8')))
    xml.append(target_node)
    source_node = E.Source(E.LocURI(source))
    if source_name:
      source_node.append(E.LocName(source_name.decode('utf-8')))
    xml.append(source_node)
    if dataCred:
      xml.append(E.Cred(
                  E.Meta(E.Format(authentication_format, xmlns='syncml:metinf'),
                  E.Type(authentication_type, xmlns='syncml:metinf'),),
                  E.Data(dataCred)
                  ))
    return xml

  def SyncMLAlert(self, cmd_id, sync_code, target, source, last_anchor, 
      next_anchor):
    """
      Since the Alert section is always almost the same, this is the
      way to set one quickly.
    """
    xml = (E.Alert(
            E.CmdID('%s' % cmd_id),
            E.Data('%s' % sync_code),
            E.Item(
              E.Target(
                E.LocURI(target)
                ),
              E.Source(
                E.LocURI(source)
                ),
              E.Meta(
                E.Anchor(
                  E.Last(last_anchor),
                  E.Next(next_anchor)
                  )
                )
              )
            ))
    return xml

  def SyncMLStatus(self, remote_xml, data_code, cmd_id, next_anchor,
                   subscription=None):
    """
    return a status bloc with all status corresponding to the syncml
    commands in remote_xml
    """
    namespace = self.getNamespace(remote_xml.nsmap)
    #list of element in the SyncBody bloc
    sub_syncbody_element_list = remote_xml.xpath('/syncml:SyncML/syncml:SyncBody/*')
    message_id = self.getMessageIdFromXml(remote_xml)
    status_list = []
    target_uri = '%s' %\
    remote_xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Target/syncml:LocURI)')
    source_uri = '%s' %\
    remote_xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Source/syncml:LocURI)')
    if data_code != self.AUTH_REQUIRED:
      xml = (E.Status(
               E.CmdID('%s' % cmd_id),
               E.MsgRef('%s' % message_id),
               E.CmdRef('0'),
               E.Cmd('SyncHdr'),
               E.TargetRef(target_uri),
               E.SourceRef(source_uri),
               E.Data('%s' % data_code),
               ))
      cmd_id += 1
      status_list.append(xml)
    for sub_syncbody_element in sub_syncbody_element_list:
      if sub_syncbody_element.xpath('local-name()') not in ('Status', 'Final', 'Get'):
        xml = (E.Status(
                 E.CmdID('%s' % cmd_id),
                 E.MsgRef('%s' % message_id),
                 E.CmdRef('%s' %\
                 sub_syncbody_element.xpath('string(.//syncml:CmdID)')),
                 E.Cmd('%s' % sub_syncbody_element.xpath('name()'))
                 ))
        cmd_id += 1
        target_ref = sub_syncbody_element.xpath('string(.//syncml:Target/syncml:LocURI)')
        if target_ref:
          xml.append(E.TargetRef('%s' % target_ref))
        source_ref = sub_syncbody_element.xpath('string(.//syncml:Source/syncml:LocURI)')
        if source_ref:
          xml.append(E.SourceRef('%s' % source_ref))
        if sub_syncbody_element.xpath('local-name()') == 'Add':
          xml.append(E.Data('%s' % self.ITEM_ADDED))
        elif sub_syncbody_element.xpath('local-name()') == 'Alert' and \
            sub_syncbody_element.xpath('string(.//syncml:Data)') == \
            str(self.SLOW_SYNC):
          xml.append(E.Data('%s' % self.REFRESH_REQUIRED))
        elif sub_syncbody_element.xpath('local-name()') == 'Alert':
          xml.append(E.Item(E.Data(E.Anchor(E.Next(next_anchor)))))
        else:
          xml.append(E.Data('%s' % self.SUCCESS))
        status_list.append(xml)
      #FIXME to do a test for Get
      if sub_syncbody_element.xpath('local-name()') == 'Get'\
          and subscription is not None:
        cmd_ref = '%s' % sub_syncbody_element.xpath('string(.//syncml:CmdID)')
        syncml_result = self.SyncMLPut(
                                  cmd_id,
                                  subscription,
                                  markup='Results',
                                  cmd_ref=cmd_ref,
                                  message_id=message_id)
        if syncml_result is not None:
          status_list.append(syncml_result)
        cmd_id += 1

    return status_list, cmd_id

  def SyncMLConfirmation(self, cmd_id=None, target_ref=None, cmd=None,
      sync_code=None, msg_ref=None, cmd_ref=None, source_ref=None,
      remote_xml=None):
    """
    This is used in order to confirm that an object was correctly
    synchronized
    """
    if remote_xml is not None:
      namespace = self.getNamespace(remote_xml.nsmap)
      msg_ref = '%s' %\
      remote_xml.xpath("string(/syncml:SyncML/syncml:SyncHdr/syncml:MsgID)")
      cmd_ref = '%s' % remote_xml.xpath("string(.//syncml:CmdID)")
      target_ref = '%s' % remote_xml.xpath("string(.//syncml:Target/syncml:LocURI)")
      source_ref = '%s' % remote_xml.xpath("string(.//syncml:Source/syncml:LocURI)")
    xml = E.Status()
    if cmd_id:
      xml.append(E.CmdID('%s' % cmd_id))
    if msg_ref:
      xml.append(E.MsgRef(msg_ref))
    if cmd_ref:
      xml.append(E.CmdRef(cmd_ref))
    if cmd:
      xml.append(E.Cmd(cmd))
    if target_ref:
      xml.append(E.TargetRef(target_ref))
    if source_ref:
      xml.append(E.SourceRef(source_ref))
    if sync_code:
      xml.append(E.Data('%s'% sync_code))
    return xml

  def SyncMLChal(self, cmd_id, cmd, target_ref, source_ref, auth_format,
      auth_type, auth_code):
    """
    This is used in order to ask crendentials
    """
    xml = (E.Status(
             E.CmdID('%s' % cmd_id),
             E.MsgRef('1'),
             E.CmdRef('0'),
             E.Cmd(cmd),
             E.TargetRef(target_ref),
             E.SourceRef(source_ref),
             E.Chal(
               E.Meta(
                 E.Format(auth_format, xmlns='syncml:metinf'),
                 E.Type(auth_type, xmlns='syncml:metinf')
                 )
               ),
            E.Data('%s' % auth_code)
            ))
    return xml

  def SyncMLPut(self, cmd_id, subscription, markup='Put', cmd_ref=None,
      message_id=None):
    """
    this is used to inform the server of the CTType version supported
    but if the server use it to respond to a Get request, it's a <Result> markup
    instead of <Put>
    """
    conduit_name = subscription.getConduit()
    conduit = self.getConduitByName(conduit_name)
    xml = None
    #if the conduit support the SyncMLPut :
    if getattr(conduit, 'getCapabilitiesCTTypeList', None) is not None and \
       getattr(conduit, 'getCapabilitiesVerCTList', None) is not None and \
       getattr(conduit, 'getPreferedCapabilitieVerCT', None) is not None:
      xml = Element('{%s}%s' % (SYNCML_NAMESPACE, markup))
      xml.append(E.CmdID('%s' % cmd_id))
      if message_id:
        xml.append(E.MsgRef('%s' % message_id))
      if cmd_ref:
        xml.append(E.CmdRef('%s' % cmd_ref))
      xml.extend((E.Meta(E.Type('application/vnd.syncml-devinf+xml')),
                 E.Item(E.Source(E.LocURI('./devinf11')),
                 E.Data(E.DevInf(
                   E.VerDTD('1.1'),
                   E.Man('Nexedi'),
                   E.Mod('ERP5SyncML'),
                   E.OEM('Open Source'),
                   E.SwV('0.1'),
                   E.DevID(subscription.getSubscriptionUrl()),
                   E.DevTyp('workstation'),
                   E.UTC(),
                   E.DataStore(E.SourceRef(subscription.getSourceURI()))
                   )
                 )
               )))
      data_store = xml.find('Item/Data/DevInf/DataStore')
      tx_element_list = []
      rx_element_list = []
      for type in conduit.getCapabilitiesCTTypeList():
        if type != self.MEDIA_TYPE['TEXT_XML']:
          for x_version in conduit.getCapabilitiesVerCTList(type):
            rx_element_list.append(E.Rx(E.CTType(type), E.VerCT(x_version)))
            tx_element_list.append(E.Tx(E.CTType(type), E.VerCT(x_version)))
      rx_pref = Element('{%s}Rx-Pref' % SYNCML_NAMESPACE)
      rx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
      data_store.append(rx_pref)
      data_store.extend(rx_element_list)
      tx_pref = Element('{%s}Tx-Pref' % SYNCML_NAMESPACE)
      tx_pref.extend((E.CTType(conduit.getPreferedCapabilitieCTType()),
                      E.VerCT(conduit.getPreferedCapabilitieVerCT())))
      data_store.append(tx_pref)
      data_store.extend(tx_element_list)
      data_store.append(E.SyncCap(
                          E.SyncType('2'),
                          E.SyncType('1'),
                          E.SyncType('4'),
                          E.SyncType('6')
                          ))
    return xml

  def sendMail(self, fromaddr, toaddr, id_sync, msg):
    """
      Send a message via email
      - sync_object : this is a publication or a subscription
      - message : what we want to send
    """
    header = "Subject: %s\n" % id_sync
    header += "To: %s\n\n" % toaddr
    msg = header + msg
    #LOG('SubSendMail', DEBUG,'from: %s, to: %s' % (fromaddr,toaddr))
    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, toaddr, msg)
    # if we want to send the email to someone else (debugging)
    #server.sendmail(fromaddr, "seb@localhost", msg)
    server.quit()

  def getNamespace(self, nsmap):
    """
      Set the namespace prefix, check if argument is conform
      and return the full namespace updated for syncml
      nsmap -- The namespace of the received xml
    """
    #search urn compatible in the namespaces of nsmap
    urns = filter(lambda v: v.upper() in self.URN_LIST, nsmap.values())
    if urns:
      namespace = etree.FunctionNamespace(urns[0])
      namespace.prefix = 'syncml'
      return namespace
    else:
      raise ValueError, "Sorry, the given namespace is not supported"

  def addXMLObject(self, cmd_id=0, object=None, xml_string=None,
                  more_data=0, gid=None, media_type=None):
    """
      Add an object with the SyncML protocol
    """
    data_node = E.Data()
    if media_type == self.MEDIA_TYPE['TEXT_XML'] and isinstance(xml_string, str):
      data_node.append(etree.XML(xml_string, parser=parser))
    elif media_type == self.MEDIA_TYPE['TEXT_XML'] and \
         not isinstance(xml_string, str):
      #xml_string could be Partial element if partial XML
      data_node.append(xml_string)
    else:
      cdata = etree.CDATA(xml_string.decode('utf-8'))
      data_node.text = cdata
    xml = (E.Add(
            E.CmdID('%s' % cmd_id),
            E.Meta(
              E.Type(media_type)
              ),
            E.Item(
              E.Source(
                E.LocURI(gid)
                ),
              data_node
              )
            ))
    if more_data:
      item_node = xml.find('{%s}Item' % SYNCML_NAMESPACE)
      item_node.append(E.MoreData())
    return etree.tostring(xml, encoding='utf-8', pretty_print=True)

  def deleteXMLObject(self, cmd_id=0, object_gid=None, rid=None):
    """
      Delete an object with the SyncML protocol
    """
    if rid:
      elem_to_append = E.Target(E.LocURI('%s' % rid))
    else:
      elem_to_append = E.Source(E.LocURI('%s' % object_gid))
    xml = (E.Delete(
             E.CmdID('%s' % cmd_id),
             E.Item(
               elem_to_append
               )
             ))
    return etree.tostring(xml, encoding='utf-8', pretty_print=True)

  def replaceXMLObject(self, cmd_id=0, object=None, xml_string=None,
                       more_data=0, gid=None, rid=None, media_type=None):
    """
      Replace an object with the SyncML protocol
    """
    if rid:
      elem_to_append = E.Target(E.LocURI('%s' % rid))
    else:
      elem_to_append = E.Source(E.LocURI('%s' % gid))
    data_node = E.Data()
    if not isinstance(xml_string, (str, unicode)):
      data_node.append(xml_string)
    else:
      data_node.append(etree.XML(xml_string, parser=parser))
    xml = (E.Replace(
             E.CmdID('%s' % cmd_id),
             E.Meta(
               E.Type(media_type)
               ),
             E.Item(
               elem_to_append,
               data_node
               )
             ))
    if more_data:
      item_node = xml.find('{%s}Item' % SYNCML_NAMESPACE)
      item_node.append(E.MoreData())
    return etree.tostring(xml, encoding='utf-8', pretty_print=True)

  def getXupdateObject(self, object_xml=None, old_xml=None):
    """
    Generate the xupdate with the new object and the old xml
    """
    erp5diff = ERP5Diff()
    erp5diff.compare(old_xml, object_xml)
    if isinstance(erp5diff._result, minidom.Document):
      #XXX While ERP5Diff use minidom, this part needs to be keeped.
      #minidom is buggy, add namespace declaration, and version attributes
      attr_version = erp5diff._result.createAttributeNS(None, 'version')
      attr_version.value = '1.0'
      erp5diff._result.documentElement.setAttributeNodeNS(attr_version)
      attr_ns = erp5diff._result.createAttributeNS(None, 'xmlns:xupdate')
      attr_ns.value = 'http://www.xmldb.org/xupdate'
      erp5diff._result.documentElement.setAttributeNodeNS(attr_ns)
      xupdate = erp5diff._result.toxml('utf-8')
    else:
      #Upper version of ERP5Diff produce valid XML.
      xupdate = erp5diff.outputString()
    #omit xml declaration
    xupdate = xupdate[xupdate.find('<xupdate:modifications'):]
    return xupdate

  def getSessionIdFromXml(self, xml):
    """
    We will retrieve the session id of the message
    """
    return int(xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:SessionID)',
                         namespaces=xml.nsmap))

  def getMessageIdFromXml(self, xml):
    """
    We will retrieve the message id of the message
    """
    return int(xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:MsgID)',
                         namespaces=xml.nsmap))

  def getTarget(self, xml):
    """
    return the target in the SyncHdr section
    """
    return '%s' %\
      xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Target/syncml:LocURI)',
                namespaces=xml.nsmap)

  def getAlertLastAnchor(self, xml):
    """
      Return the value of the last anchor, in the
      alert section of the xml_stream
    """
    return '%s' %\
      xml.xpath('string(.//syncml:Alert/syncml:Item/syncml:Meta/syncml:Anchor/syncml:Last)',
                namespaces=xml.nsmap)

  def getAlertNextAnchor(self, xml):
    """
      Return the value of the next anchor, in the
      alert section of the xml_stream
    """
    return '%s' %\
      xml.xpath('string(.//syncml:Alert/syncml:Item/syncml:Meta/syncml:Anchor/syncml:Next)',
                namespaces=xml.nsmap)

  def getSourceURI(self, xml):
    """
    return the source uri of the data base
    """
    return '%s' %\
      xml.xpath('string(//syncml:SyncBody/syncml:Alert/syncml:Item/syncml:Source/syncml:LocURI)',
                namespaces=xml.nsmap)

  def getTargetURI(self, xml):
    """
    return the target uri of the data base
    """
    return '%s' %\
      xml.xpath('string(//syncml:SyncBody/syncml:Alert/syncml:Item/syncml:Target/syncml:LocURI)',
                namespaces=xml.nsmap)

  def getSubscriptionUrlFromXML(self, xml):
    """
    return the source URI of the syncml header
    """
    return '%s' % xml.xpath('string(//syncml:SyncHdr/syncml:Source/syncml:LocURI)',
                            namespaces=xml.nsmap)

  def getStatusTarget(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    return '%s' % xml.xpath('string(syncml:TargetRef)', namespaces=xml.nsmap)

  def getStatusCode(self, xml):
    """
      Return the value of the alert code inside the xml_stream
    """
    status_code = '%s' % xml.xpath('string(syncml:Data)', namespaces=xml.nsmap)
    if status_code:
      return int(status_code)
    return None

  def getStatusCommand(self, xml):
    """
      Return the value of the command inside the xml_stream
    """
    cmd = None
    if xml.xpath('local-name()') == 'Status':
      cmd = '%s' % xml.xpath('string(syncml:Cmd)', namespaces=xml.nsmap)
    return cmd

  def getCred(self, xml):
    """
      return the credential information : type, format and data
    """
    format = '%s' %\
    xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Meta/*[local-name() = "Format"])',
              namespaces=xml.nsmap)
    type = '%s' %\
    xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Meta/*[local-name() = "Type"])',
              namespaces=xml.nsmap)
    data = '%s' % xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred/syncml:Data)',
                            namespaces=xml.nsmap)

    return (format, type, data)

  def checkCred(self, xml):
    """
      Check if there's a Cred section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:Cred)', namespaces=xml.nsmap))

  def getChal(self, xml):
    """
      return the chalenge information : format and type
    """
    format = '%s' % xml.xpath('string(//*[local-name() = "Format"])', namespaces=xml.nsmap)
    type = '%s' % xml.xpath('string(//*[local-name() = "Type"])', namespaces=xml.nsmap)
    return (format, type)

  def checkChal(self, xml):
    """
      Check if there's a Chal section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Status/syncml:Chal)',
                          namespaces=xml.nsmap))

  def checkMap(self, xml):
    """
      Check if there's a Map section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Map)', namespaces=xml.nsmap))

  def setRidWithMap(self, xml, subscriber):
    """
      get all the local objects of the given target id and set them the rid with
      the given source id (in the Map section)
    """
    item_list = xml.xpath('/syncml:SyncML/syncml:SyncBody/syncml:Map/syncml:MapItem',
                          namespaces=xml.nsmap)
    for map_item in item_list:
      gid = '%s' % map_item.xpath('string(.//syncml:Target/syncml:LocURI)', namespaces=xml.nsmap)
      signature = subscriber.getSignatureFromGid(gid)
      rid = '%s' % map_item.xpath('string(.//syncml:Source/syncml:LocURI)', namespaces=xml.nsmap)
      signature.setRid(rid)

  def getAlertCodeFromXML(self, xml):
    """
      Return the value of the alert code inside the full syncml message
    """
    alert_code = '%s' %\
    xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Alert/syncml:Data)',
              namespaces=xml.nsmap)
    if alert_code:
      return int(alert_code)
    else:
      return None

  def checkAlert(self, xml):
    """
      Check if there's an Alert section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Alert)',
                namespaces=xml.nsmap))

  def checkSync(self, xml):
    """
      Check if there's an Sync section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Sync)',
                namespaces=xml.nsmap))

  def checkFinal(self, xml):
    """
      Check if there's an Final section in the xml_stream
      The end sections (inizialisation, modification) have this tag
    """
    return  bool(xml.xpath('/syncml:SyncML/syncml:SyncBody/syncml:Final',
                 namespaces=xml.nsmap))

  def checkStatus(self, xml):
    """
      Check if there's a Status section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Status)',
                namespaces=xml.nsmap))

  def getSyncActionList(self, xml):
    """
    return the list of the action (could be "add", "replace", "delete").
    """
    return xml.xpath('//syncml:Add|//syncml:Delete|//syncml:Replace',
                     namespaces=xml.nsmap)

  def getSyncBodyStatusList(self, xml):
    """
    return the list of dictionary corredponding to the data of each status bloc
    the data are : cmd, code and source
    """
    status_list = []
    status_node_list = xml.xpath('//syncml:Status')
    for status in status_node_list:
      tmp_dict = {}
      tmp_dict['cmd'] = '%s' % status.xpath('string(./syncml:Cmd)',
                                            namespaces=xml.nsmap)
      tmp_dict['code'] = '%s' % status.xpath('string(./syncml:Data)',
                                             namespaces=xml.nsmap)
      tmp_dict['source'] = '%s' % status.xpath('string(./syncml:SourceRef)',
                                               namespaces=xml.nsmap)
      tmp_dict['target'] = '%s' % status.xpath('string(./syncml:TargetRef)',
                                               namespaces=xml.nsmap)
      status_list.append(tmp_dict)
    return status_list

  def getDataText(self, xml):
    """
    return the section data in text form, it's usefull for the VCardConduit
    """
    return '%s' % xml.xpath('string(.//syncml:Item/syncml:Data)',
                            namespaces=xml.nsmap)

  def getDataSubNode(self, xml):
    """
      Return the node starting with <object....> of the action
    """
    object_node_list = xml.xpath('.//syncml:Item/syncml:Data/*[1]',
                                 namespaces=xml.nsmap)
    if object_node_list:
      return object_node_list[0]
    return None

  def getActionId(self, xml):
    """
      Return the rid of the object described by the action
    """
    id = '%s' % xml.xpath('string(.//syncml:Item/syncml:Source/syncml:LocURI)',
                          namespaces=xml.nsmap)
    if not id:
      id = '%s' % xml.xpath('string(.//syncml:Item/syncml:Target/syncml:LocURI)',
                            namespaces=xml.nsmap)
    return id

  def checkActionMoreData(self, xml):
    """
      Return the rid of the object described by the action
    """
    return bool(xml.xpath('.//syncml:Item/syncml:MoreData',
                          namespaces=xml.nsmap))

  def getActionType(self, xml):
    """
      Return the type of the object described by the action
    """
    return '%s' % xml.xpath('string(.//syncml:Meta/syncml:Type)',
                            namespaces=xml.nsmap)

  def cutXML(self, xml_string):
    """
    Sliced a xml tree a return two fragment
    """
    line_list = xml_string.split('\n')
    short_string = '\n'.join(line_list[:self.MAX_LINES])
    rest_string = '\n'.join(line_list[self.MAX_LINES:])
    xml_tree = E.Partial()
    xml_tree.text = etree.CDATA(short_string.decode('utf-8'))
    return xml_tree, rest_string

  def getSyncMLData(self, domain=None, remote_xml=None, cmd_id=0,
                    subscriber=None, xml_confirmation_list=None, conduit=None,
                    max=None, **kw):
    """
    This generate the syncml data message. This returns a string
    with all modification made locally (ie replace, add ,delete...)

    if object is not None, this usually means we want to set the
    actual xupdate on the signature.
    """
    #LOG('getSyncMLData starting...', DEBUG, domain.getId())
    if isinstance(conduit, str):
      conduit = self.getConduitByName(conduit)
    if xml_confirmation_list is None:
      xml_confirmation_list = []
    local_gid_list = []
    syncml_data_list = kw.get('syncml_data_list', [])
    result = {'finished':1}
    if isinstance(remote_xml, (str, unicode)):
      remote_xml = etree.XML(remote_xml, parser=parser)
    if domain.isOneWayFromServer():
      #Do not set object_path_list, subscriber send nothing it's a client
      subscriber.setRemainingObjectPathList([])
    elif subscriber.getRemainingObjectPathList() is None:
      object_list = domain.getObjectList()
      object_path_list = [x.getPhysicalPath() for x in object_list]
      subscriber.setRemainingObjectPathList(object_path_list)
      if subscriber.getMediaType() == self.MEDIA_TYPE['TEXT_VCARD']:
        #here the method getGidFromObject don't return the good gid because
        #the conduit use the catalog to determine it and object are not yet
        #cataloged so if there is many times the same gid, we must count it
        gid_not_encoded_list = []
        for object in object_list:
          #LOG('getSyncMLData :', DEBUG, 'object:%s,  objectTitle:%s, local_gid_list:%s' % (object, object.getTitle(), local_gid_list))
          gid = b16decode(domain.getGidFromObject(object))
          if gid in gid_not_encoded_list:
            number = len([item for item in gid_not_encoded_list if item.startswith(gid)])
            if number:
              gid = '%s__%s' %  (gid, str(number+1))
          gid_not_encoded_list.append(gid)
          local_gid_list.append(b16encode(gid))
          #LOG('getSyncMLData :', DEBUG,'gid_not_encoded_list:%s, local_gid_list:%s, gid:%s' % (gid_not_encoded_list, local_gid_list, gid))
      else:
        local_gid_list = [domain.getGidFromObject(x) for x in object_list]
      # Objects to remove
      #LOG('getSyncMLData remove object to remove ...', DEBUG, '')
      for object_gid in subscriber.getGidList():
        if object_gid not in local_gid_list:
          # This is an object to remove
          signature = subscriber.getSignatureFromGid(object_gid)
          if signature.getStatus() != self.PARTIAL:
            # If partial, then we have a signature but no local object
            rid = signature.getRid()
            syncml_data_list.append(self.deleteXMLObject(object_gid=object_gid,
                                                         rid=rid,
                                                         cmd_id=cmd_id))
            cmd_id += 1
          # Delete Signature if object does not exist anymore
          subscriber.delSignature(object_gid)

    local_gid_list = []
    loop = 0
    for object_path in subscriber.getRemainingObjectPathList():
      if max is not None and loop >= max:
        result['finished'] = 0
        break
      #LOG('getSyncMLData object_path', INFO, object_path)
      object = self.unrestrictedTraverse(object_path)
      status = self.SENT
      object_gid = domain.getGidFromObject(object)
      if not object_gid:
        continue
      local_gid_list += [object_gid]
      force = 0
      if ''.join(syncml_data_list).count('\n') < self.MAX_LINES and not \
          object.id.startswith('.'):
        # If not we have to cut
        #LOG('getSyncMLData', 0, 'object_path: %s' % '/'.join(object_path))
        #LOG('getSyncMLData', 0, 'xml_mapping: %s' % str(domain.getXMLMapping()))
        #LOG('getSyncMLData', 0, 'code: %s' % str(self.getAlertCodeFromXML(remote_xml)))
        #LOG('getSyncMLData', 0, 'gid_list: %s' % str(local_gid_list))
        #LOG('getSyncMLData', 0, 'subscriber.getGidList: %s' % subscriber.getGidList())
        #LOG('getSyncMLData', 0, 'hasSignature: %s' % str(subscriber.hasSignature(object_gid)))
        #LOG('getSyncMLData', 0, 'alert_code == slowsync: %s' % str(self.getAlertCodeFromXML(remote_xml) == self.SLOW_SYNC))

        signature = subscriber.getSignatureFromGid(object_gid)
        ## Here we first check if the object was modified or not by looking at dates
        status = self.SENT
        more_data = 0
        # For the case it was never synchronized, we have to send everything
        if signature is not None and signature.getXMLMapping() is None:
          pass
        elif signature is None or\
            (not signature.hasXML() and\
            signature.getStatus() != self.PARTIAL) or\
            self.getAlertCodeFromXML(remote_xml) == self.SLOW_SYNC:
          #LOG('getSyncMLData', DEBUG, 'Current object.getPath: %s' % object.getPath())
          xml_string = conduit.getXMLFromObjectWithId(object,\
                       xml_mapping=domain.getXMLMapping())
          gid = subscriber.getGidFromObject(object)
          signature = Signature(id=gid, object=object).__of__(subscriber)
          signature.setTempXML(xml_string)
          if xml_string.count('\n') > self.MAX_LINES:
            more_data = 1
            xml_string, rest_string = self.cutXML(xml_string)
            signature.setPartialXML(rest_string)
            status = self.PARTIAL
            signature.setAction('Add')
          #in first, we try with rid if there is one
          gid = signature.getRid() or signature.getGid()
          syncml_data_list.append(self.addXMLObject(
                                  cmd_id=cmd_id,
                                  object=object,
                                  gid=gid,
                                  xml_string=xml_string,
                                  more_data=more_data,
                                  media_type=subscriber.getMediaType()))
          cmd_id += 1
          signature.setStatus(status)
          subscriber.addSignature(signature)
        elif signature.getStatus() in (self.NOT_SYNCHRONIZED,
                                       self.PUB_CONFLICT_MERGE,):
          # We don't have synchronized this object yet but it has a signature
          xml_object = conduit.getXMLFromObjectWithId(object,\
                       xml_mapping=domain.getXMLMapping()) 
          #LOG('getSyncMLData', DEBUG, 'checkMD5: %s' % str(signature.checkMD5(xml_object)))
          #LOG('getSyncMLData', DEBUG, 'getStatus: %s' % str(signature.getStatus()))
          if signature.getStatus() == self.PUB_CONFLICT_MERGE:
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                    cmd_id=cmd_id,
                                    source_ref=signature.getGid(),
                                    sync_code=self.CONFLICT_MERGE,
                                    cmd='Replace'))
          set_synchronized = 1
          if not signature.checkMD5(xml_object):
            set_synchronized = 0
            if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
              # If there is no xml, we re-send all the objects
              xml_string = xml_object
            else:
             # This object has changed on this side, we have to generate some xmldiff
              xml_string = self.getXupdateObject(xml_object, signature.getXML())
              if xml_string.count('\n') > self.MAX_LINES:
                # This make comment fails, so we need to replace
                more_data = 1
                xml_string, rest_string = self.cutXML(xml_string)
                signature.setPartialXML(rest_string)
                status = self.PARTIAL
                signature.setAction('Replace')
                signature.setStatus(status)
            rid = signature.getRid()#in first, we try with rid if there is
            gid = signature.getGid()
            syncml_data_list.append(self.replaceXMLObject(
                                        cmd_id=cmd_id, object=object,
                                        gid=gid, rid=rid,
                                        xml_string=xml_string,
                                        more_data=more_data,
                                        media_type=subscriber.getMediaType()))
            cmd_id += 1
            signature.setTempXML(xml_object)
          # Now we can apply the xupdate from the subscriber
          subscriber_xupdate = signature.getSubscriberXupdate()
          #LOG('getSyncMLData subscriber_xupdate', DEBUG, subscriber_xupdate)
          if subscriber_xupdate is not None:
            # The modification in the xml from signature is compare and update
            # with xml_xupdate from subscriber
            old_xml = signature.getXML()
            conduit.updateNode(
                        xml=subscriber_xupdate,
                        object=object,
                        previous_xml=old_xml,
                        force=(domain.getDomainType() == self.SUB),
                        simulate=0)
            xml_object = conduit.getXMLFromObjectWithId(object,\
                         xml_mapping=domain.getXMLMapping()) 
            signature.setTempXML(xml_object)
          if set_synchronized: # We have to do that after this previous update
            # We should not have this case when we are in CONFLICT_MERGE
            signature.setStatus(self.SYNCHRONIZED)
        elif signature.getStatus() == self.PUB_CONFLICT_CLIENT_WIN:
          # We have decided to apply the update
          # XXX previous_xml will be geXML instead of getTempXML because
          # some modification was already made and the update
          # may not apply correctly
          xml_update = signature.getPartialXML()
          conduit.updateNode(
                      xml=xml_update,
                      object=object,
                      previous_xml=signature.getXML(),
                      force=1)
          xml_confirmation_list.append(self.SyncMLConfirmation(
                                  cmd_id=cmd_id,
                                  target_ref=object_gid,
                                  sync_code=self.CONFLICT_CLIENT_WIN,
                                  cmd='Replace'))
          signature.setStatus(self.SYNCHRONIZED)
        elif signature.getStatus() == self.PARTIAL:
          xml_string = signature.getPartialXML()
          if(subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']):
            xml_to_send = conduit.getXMLFromObjectWithId(object,\
                                  xml_mapping=domain.getXMLMapping()) 
          elif xml_string.count('\n') > self.MAX_LINES:
            more_data = 1
            # Receive the chunk of partial xml
            short_string = signature.getFirstChunkPdata(self.MAX_LINES)
            xml_to_send = E.Partial()
            xml_to_send.text = etree.CDATA(short_string.decode('utf-8'))
            status = self.PARTIAL
          else:
            xml_to_send = E.Partial()
            xml_to_send.text = etree.CDATA(xml_string.decode('utf-8'))
          signature.setStatus(status)
          if signature.getAction() == 'Replace':
            rid = signature.getRid()
            # In first, we try with rid if there is one
            gid = signature.getGid()
            syncml_data_list.append(self.replaceXMLObject(
                                       cmd_id=cmd_id,
                                       object=object,
                                       gid=gid,
                                       rid=rid,
                                       xml_string=xml_to_send,
                                       more_data=more_data,
                                       media_type=subscriber.getMediaType()))
          elif signature.getAction() == 'Add':
            #in fisrt, we try with rid if there is one
            gid = signature.getRid() or signature.getGid()
            syncml_data_list.append(self.addXMLObject(
                                        cmd_id=cmd_id,
                                        object=object,
                                        gid=gid,
                                        xml_string=xml_to_send,
                                        more_data=more_data,
                                        media_type=subscriber.getMediaType()))
        if not more_data:
          subscriber.removeRemainingObjectPath(object_path)
      else:
        result['finished'] = 1
        break
      loop += 1
    result['syncml_data_list'] = syncml_data_list
    result['xml_confirmation_list'] = xml_confirmation_list
    result['cmd_id'] = cmd_id
    return result

  def applyActionList(self, domain=None, subscriber=None, cmd_id=0,
                      remote_xml=None, conduit=None, simulate=0):
    """
    This just look to a list of action to do, then id applies
    each action one by one, thanks to a conduit
    """
    namespace = self.getNamespace(remote_xml.nsmap)
    xml_confirmation_list = []
    has_next_action = 0
    gid_from_xml_list = []
    destination = self.unrestrictedTraverse(domain.getDestinationPath())
    #LOG('applyActionList args', DEBUG, 'domain : %s\n subscriber : %s\n cmd_id: %s'\ 
    #% (domain.getPath(), subscriber.getPath(), cmd_id))
    #LOG('XMLSyncUtils applyActionList', DEBUG, self.getSyncActionList(remote_xml))
    for action in self.getSyncActionList(remote_xml):
      conflict_list = []
      status_code = self.SUCCESS
      # Thirst we have to check the kind of action it is

      # The rid is the Temporary GUID (SYNCML Protocol). the rid sent by the
      # client unlike gid. The rid is in MapItem for each Action Map it's the LocURI in
      # the action. 
      gid = rid = self.getActionId(action)
      #The action delete hasn't need a gid and retrieve the gid of conduit for
      #object.
      if action.xpath('local-name()') != 'Delete':
        data_action = self.getDataSubNode(action)
        if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
          #data in unicode
          data_action = self.getDataText(action)
        if getattr(conduit, 'getGidFromXML', None) is not None and \
          conduit.getGidFromXML(data_action, namespace, gid_from_xml_list):
          gid = conduit.getGidFromXML(data_action, namespace, gid_from_xml_list)
          gid_from_xml_list.append(gid)
          gid = b16encode(gid)
      #the rid unlike gid, it's the rid or gid (if rid == gid) will use for
      #retrieve object and send response to client
      signature = subscriber.getSignatureFromGid(gid)
      object = subscriber.getObjectFromGid(gid)
      object_id = domain.generateNewIdWithGenerator(object=destination, gid=gid)
      if rid == gid:
        #We can't use our own gid and the temporary GUID is useless
        rid = None
      if signature is not None:
        signature.setRid(rid)
      else:
        signature = Signature(id=gid, rid=rid, status=self.NOT_SYNCHRONIZED,
                                object=object).__of__(subscriber)
        signature.setObjectId(object_id)
        subscriber.addSignature(signature)
      force = signature.getForce()
      partial_data = '%s' % action.xpath('string(.//syncml:Item/syncml:Data/syncml:Partial)')
      if not self.checkActionMoreData(action):
        data_subnode = None
        if partial_data:
          if signature.hasPartialXML():
            signature.appendPartialXML(partial_data)
            data_subnode = signature.getPartialXML()
          else:
            data_subnode = partial_data
          #LOG('applyActionList', DEBUG, 'data_subnode: %s' % data_subnode)
          if subscriber.getMediaType() == self.MEDIA_TYPE['TEXT_XML']:
            data_subnode = etree.XML(data_subnode, parser=parser)
        else:
          if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
            data_subnode = self.getDataText(action)
          else:
            data_subnode = self.getDataSubNode(action)
        if action.xpath('local-name()') == 'Add':
          # Then store the xml of this new subobject
          reset = 0
          if object is None:
            add_data = conduit.addNode(xml=data_subnode,
                                       object=destination,
                                       object_id=object_id)
            conflict_list.extend(add_data['conflict_list'])
            # Retrieve directly the object from addNode
            object = add_data['object']
            if object is not None:
              signature.setPath(object.getPhysicalPath())
              signature.setObjectId(object.getId())
          else:
            reset = 1
            # Object was retrieve but need to be updated without recreated
            # usefull when an object is only deleted by workflow.
            if data_subnode is not None:
              xml_string = conduit.convertToXml(data_subnode)
              actual_xml = conduit.getXMLFromObjectWithId(object,
                           xml_mapping=domain.getXMLMapping(force=1))
              actual_xml = conduit.convertToXml(actual_xml)
              xml_string_gid = conduit.replaceIdFromXML(xml_string, gid)
              actual_xml_gid = conduit.replaceIdFromXML(actual_xml, gid)
              # use gid as compare key because their ids can be different
              data_subnode = self.getXupdateObject(xml_string_gid, actual_xml_gid)
            conflict_list.extend(conduit.updateNode(
                                        xml=data_subnode,
                                        object=object,
                                        previous_xml=signature.getXML(),
                                        force=force,
                                        simulate=simulate,
                                        reset=reset))
            xml_object = conduit.getXMLFromObjectWithId(object,\
                         xml_mapping=domain.getXMLMapping()) 
            signature.setTempXML(xml_object)
          if object is not None:
            #LOG('applyActionList', DEBUG, 'addNode, found the object')
            if reset:
              #After a reset we want copy the LAST XML view on Signature.
              #this implementation is not sufficient, need to be improved.
              if not isinstance(xml_object, str):
                xml_object = etree.tostring(xml_object, encoding='utf-8',
                                            pretty_print=True)
            else: 
              xml_object = conduit.getXMLFromObjectWithId(object,\
                           xml_mapping=domain.getXMLMapping()) 
            signature.setStatus(self.SYNCHRONIZED)
            #signature.setId(object.getId())
            signature.setPath(object.getPhysicalPath())
            signature.setXML(xml_object)
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                    cmd_id=cmd_id,
                                    cmd='Add',
                                    sync_code=self.ITEM_ADDED,
                                    remote_xml=action))
            cmd_id +=1
        elif action.xpath('local-name()') == 'Replace':
          #LOG('applyActionList', DEBUG, 'object: %s will be updated...' % str(object))
          if object is not None:
            #LOG('applyActionList', DEBUG, 'object: %s will be updated...' % object.id)
            signature = subscriber.getSignatureFromGid(gid)
            #LOG('applyActionList', DEBUG, 'previous signature: %s' % str(signature))
            previous_xml = signature.getXML()
            conflict_list += conduit.updateNode(
                                        xml=data_subnode,
                                        object=object,
                                        previous_xml=previous_xml,
                                        force=force,
                                        simulate=simulate)
            xml_object = conduit.getXMLFromObjectWithId(object,\
                         xml_mapping=domain.getXMLMapping())
            signature.setTempXML(xml_object)
            if conflict_list:
              status_code = self.CONFLICT
              signature.setStatus(self.CONFLICT)
              signature.setConflictList(signature.getConflictList()+conflict_list)
              data_subnode_string = etree.tostring(data_subnode, encoding='utf-8')
              signature.setPartialXML(data_subnode_string)
            elif not simulate:
              signature.setStatus(self.SYNCHRONIZED)
            xml_confirmation_list.append(self.SyncMLConfirmation(
                                    cmd_id=cmd_id,
                                    cmd='Replace',
                                    sync_code=status_code,
                                    remote_xml=action))
            cmd_id +=1
            if simulate:
              # This means we are on the publisher side and we want to store
              # the xupdate from the subscriber and we also want to generate
              # the current xupdate from the last synchronization
              data_subnode_string = etree.tostring(data_subnode, encoding='utf-8')
              #LOG('applyActionList, subscriber_xupdate:', TRACE, data_subnode_string)
              signature.setSubscriberXupdate(data_subnode_string)

        elif action.xpath('local-name()') == 'Delete':
          LOG("applyactionlist delete",INFO,"")
          object_id = signature.getId()
          #LOG('applyActionList Delete on : ', DEBUG, (signature.getId(), subscriber.getObjectFromGid(object_id)))
          if subscriber.getMediaType() != self.MEDIA_TYPE['TEXT_XML']:
            data_subnode = self.getDataText(action)
          else:
            data_subnode = self.getDataSubNode(action)
          #LOG('applyActionList, object gid to delete :', 0, subscriber.getObjectFromGid(object_id))
          if subscriber.getObjectFromGid(object_id) is not None:
          #if the object exist:
            conduit.deleteNode(
                        xml=data_subnode,
                        object=destination,
                        object_id=subscriber.getObjectFromGid(object_id).getId())
            subscriber.delSignature(gid)
          xml_confirmation_list.append(self.SyncMLConfirmation(
                                  cmd_id=cmd_id,
                                  cmd='Delete',
                                  sync_code=status_code,
                                  remote_xml=action))
      else: # We want to retrieve more data
        signature.setStatus(self.PARTIAL)
        signature.appendPartialXML(partial_data) 
        #LOG('applyActionList', DEBUG, 'previous_partial: %s' % str(previous_partial))
        #LOG('applyActionList', DEBUG, 'waiting more data for :%s' % signature.getId())
        xml_confirmation_list.append(self.SyncMLConfirmation(
                                cmd_id=cmd_id,
                                cmd= "%s" % action.xpath('name()'),
                                sync_code=self.WAITING_DATA,
                                remote_xml=action))
      if conflict_list and signature is not None:
        # We had a conflict
        signature.setStatus(self.CONFLICT)

    return (xml_confirmation_list, has_next_action, cmd_id)

  def applyStatusList(self, subscriber=None, remote_xml=None):
    """
    This read a list of status list (ie syncml confirmations).
    This method have to change status codes on signatures
    """
    status_list = self.getSyncBodyStatusList(remote_xml)
    has_status_list = 0
    destination_waiting_more_data = 0
    for status in status_list:
      if not status['code']:
        continue
      status_cmd = status['cmd']
      object_gid = status['source']
      if not object_gid:
        object_gid = status['target']
      status_code = int(status['code'])
      signature = subscriber.getSignatureFromGid(object_gid)
      if signature is None and\
      not(subscriber.getSynchronizeWithERP5Sites()):
        #the client give his id but not the gid
        signature = subscriber.getSignatureFromRid(object_gid)
      if status_cmd in ('Add', 'Replace',):
        has_status_list = 1
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
        has_status_list = 1
        if status_code == self.SUCCESS:
          if signature is not None:
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
    Send the server modification, this happens after the Synchronization
    initialization
    """
    has_response = 0 #check if syncmodif replies to this messages
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    #LOG('SyncModif', DEBUG, 'Starting... domain: %s' % domain.getId())
    # Get informations from the header
    xml_header = remote_xml[0]
    #FIXME to apply a DTD or schema
    if xml_header.xpath('local-name()') != "SyncHdr":
      LOG('SyncModif', INFO, 'This is not a SyncML Header')
      raise ValueError, "Sorry, This is not a SyncML Header"

    subscriber = domain # If we are the client, this is fine
    simulate = 0 # used by applyActionList, should be 0 for client
    if domain.domain_type == self.PUB:
      simulate = 1
      subscription_url = self.getSubscriptionUrlFromXML(xml_header)
      subscriber = domain.getSubscriber(subscription_url)

    # We have to check if this message was not already, this can be dangerous
    # to update two times the same object
    message_id = self.getMessageIdFromXml(remote_xml)
    correct_message = subscriber.checkCorrectRemoteMessageId(message_id)
    if not correct_message: # We need to send again the message
      LOG('SyncModif, no correct message:', INFO, "sending again...")
      last_xml = subscriber.getLastSentMessage()
      LOG("SyncModif last_xml :", INFO, last_xml)
      remote_xml = etree.tostring(remote_xml, encoding='utf-8',
                                  xml_declaration=True,
                                  pretty_print=True)
      LOG("SyncModif remote_xml :", INFO, remote_xml)
      if last_xml:
        has_response = 1
        if domain.domain_type == self.PUB: # We always reply
          self.sendResponse(
                    from_url=domain.publication_url,
                    to_url=subscriber.subscription_url,
                    sync_id=domain.getTitle(),
                    xml=last_xml, domain=domain,
                    content_type=domain.getSyncContentType())
        elif domain.domain_type == self.SUB:
          self.sendResponse(
                    from_url=domain.subscription_url,
                    to_url=domain.publication_url,
                    sync_id=domain.getTitle(),
                    xml=last_xml,
                    domain=domain,
                    content_type=domain.getSyncContentType())
      return {'has_response':has_response, 'xml':last_xml}
    subscriber.setLastSentMessage('')

    # First apply the list of status codes
    (destination_waiting_more_data, has_status_list) = self.applyStatusList(
                                                      subscriber=subscriber,
                                                      remote_xml=remote_xml)

    alert_code = self.getAlertCodeFromXML(remote_xml)
    # Import the conduit and get it
    conduit = self.getConduitByName(subscriber.getConduit())
    # Then apply the list of actions
    (xml_confirmation_list, has_next_action, cmd_id) = self.applyActionList(
                                          cmd_id=cmd_id,
                                          domain=domain,
                                          subscriber=subscriber,
                                          remote_xml=remote_xml,
                                          conduit=conduit, simulate=simulate)

    xml = E.SyncML()

    # syncml header
    if domain.domain_type == self.PUB:
      xml.append(self.SyncMLHeader(
                  subscriber.getSessionId(),
                  subscriber.incrementMessageId(),
                  subscriber.getSubscriptionUrl(),
                  domain.getPublicationUrl()))
    elif domain.domain_type == self.SUB:
      xml.append(self.SyncMLHeader(
                  domain.getSessionId(), domain.incrementMessageId(),
                  domain.getPublicationUrl(),
                  domain.getSubscriptionUrl()))

    # syncml body
    sync_body = E.SyncBody()
    xml.append(sync_body)

    xml_status, cmd_id = self.SyncMLStatus(
                                    remote_xml,
                                    self.SUCCESS,
                                    cmd_id,
                                    subscriber.getNextAnchor(),
                                    subscription=subscriber)
    sync_body.extend(xml_status)

    destination_url = ''
    # alert message if we want more data
    if destination_waiting_more_data:
      sync_body.append(self.SyncMLAlert(
                        cmd_id,
                        self.WAITING_DATA,
                        subscriber.getTargetURI(),
                        subscriber.getSourceURI(),
                        subscriber.getLastAnchor(),
                        subscriber.getNextAnchor()))
    # Now we should send confirmations
    cmd_id_before_getsyncmldata = cmd_id
    cmd_id = cmd_id+1
    if domain.getActivityEnabled():
      #use activities to get SyncML data.
      remote_xml = etree.tostring(remote_xml, encoding='utf-8',
                                    xml_declaration=True, pretty_print=False)
      xml_tree = etree.tostring(xml, encoding='utf-8', xml_declaration=True,
                                pretty_print=False)
      xml_confirmation_list = [etree.tostring(xml, encoding='utf-8',\
                                              xml_declaration=True,\
                                              pretty_print=False) for xml in \
                                              xml_confirmation_list]
      domain.activate(activity='SQLQueue',
                      tag=domain.getId(),
                      priority=self.PRIORITY).activateSyncModif(
                      domain_relative_url=domain.getRelativeUrl(),
                      remote_xml=remote_xml,
                      xml_tree=xml_tree,
                      subscriber_relative_url=subscriber.getRelativeUrl(),
                      cmd_id=cmd_id,
                      xml_confirmation_list=xml_confirmation_list,
                      syncml_data_list=[],
                      cmd_id_before_getsyncmldata=cmd_id_before_getsyncmldata,
                      has_status_list=has_status_list,
                      has_response=has_response )
      return {'has_response':1, 'xml':''}
    else:
      result = self.getSyncMLData(domain=domain,
                             remote_xml=remote_xml,
                             subscriber=subscriber,
                             cmd_id=cmd_id,
                             xml_confirmation_list=xml_confirmation_list,
                             conduit=conduit,
                             max=None)
      syncml_data_list = result['syncml_data_list']
      xml_confirmation_list = result['xml_confirmation_list']
      cmd_id = result['cmd_id']
      return self.sendSyncModif(syncml_data_list, cmd_id_before_getsyncmldata,
                                subscriber, domain, xml_confirmation_list,
                                remote_xml, xml, has_status_list,
                                has_response)

  def deleteRemainObjectList(self, domain, subscriber):
    """
    This method allow deletion on not synchronised Objects at the end of Synchronisation session.
    Usefull only after reseting in One Way Sync
    """
    object_list = domain.getObjectList()
    gid_list = [domain.getGidFromObject(x) for x in object_list]
    domain_path = domain.getPath()
    subscriber_path = subscriber.getPath()
    while len(gid_list):
      sliced_gid_list = [gid_list.pop() for i in gid_list[:self.MAX_OBJECTS]]
      #Split List Processing in activities
      self.activate(activity='SQLQueue',
                    tag=domain.getId(),
                    priority=self.PRIORITY).activateDeleteRemainObjectList(domain_path,
                                                                       subscriber_path,
                                                                       sliced_gid_list)

  def activateDeleteRemainObjectList(self, domain_path, subscriber_path, gid_list):
    """
    Execute Deletion in Activities
    """
    domain = self.unrestrictedTraverse(domain_path)
    subscriber = self.unrestrictedTraverse(subscriber_path)
    destination = self.unrestrictedTraverse(domain.getDestinationPath())
    conduit_name = subscriber.getConduit()
    conduit = self.getConduitByName(conduit_name)
    for gid in gid_list:
      if subscriber.getSignatureFromGid(gid) is None:
        object_id = b16decode(gid)
        conduit.deleteObject(object=destination, object_id=object_id)

  def activateSyncModif(self, **kw):
    domain = self.unrestrictedTraverse(kw['domain_relative_url'])
    subscriber = self.unrestrictedTraverse(kw['subscriber_relative_url'])
    conduit = subscriber.getConduit()
    result = self.getSyncMLData(domain=domain, subscriber=subscriber,
                                conduit=conduit, max=self.MAX_OBJECTS, **kw)
    syncml_data_list = result['syncml_data_list']
    cmd_id = result['cmd_id']
    kw['syncml_data_list'] = syncml_data_list
    kw['cmd_id'] = cmd_id
    finished = result['finished']
    if not finished:
      domain.activate(activity='SQLQueue',
                      tag=domain.getId(),
                      priority=self.PRIORITY).activateSyncModif(**kw)
    else:
      cmd_id = result['cmd_id']
      cmd_id_before_getsyncmldata = kw['cmd_id_before_getsyncmldata']
      remote_xml = etree.XML(kw['remote_xml'], parser=parser)
      xml_tree = etree.XML(kw['xml_tree'], parser=parser)
      xml_confirmation_list = kw['xml_confirmation_list']
      has_status_list = kw['has_status_list']
      has_response = kw['has_response']
      return self.sendSyncModif(
                        syncml_data_list,
                        cmd_id_before_getsyncmldata,
                        subscriber,
                        domain,
                        xml_confirmation_list,
                        remote_xml,
                        xml_tree,
                        has_status_list,
                        has_response)

  def sendSyncModif(self, syncml_data_list, cmd_id_before_getsyncmldata,
                    subscriber, domain, xml_confirmation_list, remote_xml,
                    xml_tree, has_status_list, has_response):
    # XXX the better is a namespace for all
    namespace = self.getNamespace(xml_tree.nsmap)
    sync_body = xml_tree.find('SyncBody')
    if sync_body is None:
      sync_body = xml_tree.xpath('syncml:SyncBody')[0]
    if syncml_data_list:
      sync_node = E.Sync(E.CmdID('%s' % cmd_id_before_getsyncmldata))
      sync_body.append(sync_node)
      target_uri = subscriber.getTargetURI()
      if target_uri:
        sync_node.append(E.Target(E.LocURI(target_uri)))
      source_uri = subscriber.getSourceURI()
      if source_uri:
        sync_node.append(E.Source(E.LocURI(source_uri)))
      for syncml_data in syncml_data_list:
        sync_node.append(etree.XML(syncml_data, parser=parser))
    for xml_confirmation in xml_confirmation_list:
      if isinstance(xml_confirmation, str):
        xml_confirmation = etree.XML(xml_confirmation, parser=parser)
      sync_body.append(xml_confirmation)

    self.sync_finished = 0 
    if domain.domain_type == self.PUB: # We always reply
      # When the publication recieved the response Final and the modification 
      # data is finished so the publication send the tag "Final"
      if not self.checkSync(remote_xml) and not xml_confirmation_list\
        and not syncml_data_list and self.checkFinal(remote_xml):
        sync_body.append(E.Final())
        self.sync_finished = 1
      xml_string = etree.tostring(xml_tree, encoding='utf-8', pretty_print=True)
      subscriber.setLastSentMessage(xml_string)
      self.sendResponse(
                from_url=domain.publication_url,
                to_url=subscriber.subscription_url,
                sync_id=domain.getTitle(),
                xml=xml_string,
                domain=domain,
                content_type=domain.getSyncContentType())
      if self.sync_finished == 1:
        LOG('this is the end of the synchronisation session from PUB !!!', INFO, domain.getId())
        subscriber.setAuthenticated(False)
        domain.setAuthenticated(False)
      has_response = 1
    elif domain.domain_type == self.SUB:
      # the modification data is finished on the subscription so the tag
      # "Final" sent to the publication
      if not self.checkAlert(remote_xml) and not xml_confirmation_list\
        and not syncml_data_list:
        sync_body.append(E.Final())
        self.sync_finished = 1
      xml_string = etree.tostring(xml_tree, encoding='utf-8', pretty_print=True)
      if not self.sync_finished or not self.checkFinal(remote_xml):
        subscriber.setLastSentMessage(xml_string)
        self.sendResponse(
                  from_url=domain.subscription_url,
                  to_url=domain.publication_url,
                  sync_id=domain.getTitle(),
                  xml=xml_string, domain=domain,
                  content_type=domain.getSyncContentType())
        has_response = 1
      #When the receive the final element and the sub finished synchronization
      else:
        if domain.isOneWayFromServer():
          self.deleteRemainObjectList(domain, subscriber)
        LOG('this is the end of the synchronisation session from SUB !!!', INFO, domain.getId())
        domain.setAuthenticated(False)
    return {'has_response':has_response, 'xml':xml_string}

  def xml2wbxml(self, xml):
    """
    convert xml string to wbxml using a temporary file
    """
    #LOG('xml2wbxml starting ...', DEBUG, '')
    import os
    f = open('/tmp/xml2wbxml', 'w')
    f.write(xml)
    f.close()
    os.system('/usr/bin/xml2wbxml -o /tmp/xml2wbxml /tmp/xml2wbxml')
    f = open('/tmp/xml2wbxml', 'r')
    wbxml = f.read()
    f.close()
    return wbxml

  def wbxml2xml(self, wbxml):
    """
    convert wbxml string to xml using a temporary file
    """
    #LOG('wbxml2xml starting ...', DEBUG, '')
    import os
    f = open('/tmp/wbxml2xml', 'w')
    f.write(wbxml)
    f.close()
    os.system('/usr/bin/wbxml2xml -o /tmp/wbxml2xml /tmp/wbxml2xml')
    f = open('/tmp/wbxml2xml', 'r')
    xml = f.read()
    f.close()
    return xml

  def PubSync(self, publication_path, msg=None, RESPONSE=None, subscriber=None):
    """
      This is the synchronization method for the server
    """
    from Products.ERP5SyncML.Publication import Subscriber
    #LOG('PubSync', DEBUG, 'Starting... publication: %s' % (publication_path))
    # Read the request from the client
    publication = self.unrestrictedTraverse(publication_path)
    xml_client = msg
    if xml_client is None:
      xml_client = self.readResponse(from_url=publication.getPublicationUrl())
    #LOG('PubSync', DEBUG, 'Starting... msg: %s' % str(xml_client))
    result = None
    if xml_client is not None:
      if isinstance(xml_client, (str, unicode)):
        xml_client = etree.XML(xml_client, parser=parser)
      #FIXME to apply a DTD or schema
      if xml_client.xpath('local-name()') != "SyncML":
        LOG('PubSync', INFO, 'This is not a SyncML Message')
        raise ValueError, "Sorry, This is not a SyncML Message"
      alert_code = self.getAlertCodeFromXML(xml_client)
      # Get informations from the header
      client_header = xml_client[0]
      #FIXME to apply a DTD or schema
      if client_header.xpath('local-name()') != "SyncHdr":
        LOG('PubSync', INFO, 'This is not a SyncML Header')
        raise ValueError, "Sorry, This is not a SyncML Header"
      subscription_url = self.getSubscriptionUrlFromXML(client_header)
      # Get the subscriber or create it if not already in the list
      subscriber = publication.getSubscriber(subscription_url)
      if subscriber is None:
        subscriber = Subscriber(publication.generateNewId(), subscription_url)
        subscriber.setXMLMapping(publication.getXMLMapping())
        subscriber.setConduit(publication.getConduit())
        publication.addSubscriber(subscriber)
        subscriber = subscriber.__of__(publication)
        # first synchronization
        result = self.PubSyncInit(publication=publication,
                                  xml_client=xml_client,
                                  subscriber=subscriber,
                                  sync_type=self.SLOW_SYNC)
      elif self.checkAlert(xml_client) and \
          alert_code in (self.TWO_WAY, self.SLOW_SYNC, \
          self.ONE_WAY_FROM_SERVER):
        subscriber.setXMLMapping(publication.getXMLMapping())
        subscriber.setConduit(publication.getConduit())
        result = self.PubSyncInit(publication=publication,
                                  xml_client=xml_client,
                                  subscriber=subscriber,
                                  sync_type=alert_code)
      else:
        #we log the user authenticated to do the synchronization with him
        if self.checkMap(xml_client) :
          self.setRidWithMap(xml_client, subscriber)
        if subscriber.isAuthenticated():
            uf = self.getPortalObject().acl_users
            user = uf.getUserById(subscriber.getUser()).__of__(uf)
            newSecurityManager(None, user)
            result = self.PubSyncModif(publication, xml_client)
        else:
          result = self.PubSyncModif(publication, xml_client)
    elif subscriber is not None:
      # This looks like we are starting a synchronization after
      # a conflict resolution by the user
      result = self.PubSyncInit(publication=publication,
                                xml_client=None,
                                subscriber=subscriber,
                                sync_type=self.TWO_WAY)
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')
    elif result is not None:
      return result

  def SubSync(self, subscription_path, msg=None, RESPONSE=None):
    """
      This is the synchronization method for the client
    """
    response = None #check if subsync replies to this messages
    subscription = self.unrestrictedTraverse(subscription_path)
    if msg is None and (subscription.getSubscriptionUrl()).find('file') >= 0:
      msg = self.readResponse(sync_id=subscription.getSubscriptionUrl(),
                              from_url=subscription.getSubscriptionUrl())
    if msg is None:
      response = self.SubSyncInit(subscription)
    else:
      xml_client = msg
      if isinstance(xml_client, (str, unicode)):
        xml_client = etree.XML(xml_client, parser=parser)
        status_list = self.getSyncBodyStatusList(xml_client)
        if status_list:
          status_code_syncHdr = status_list[0]['code']
          if status_code_syncHdr.isdigit():
            status_code_syncHdr = int(status_code_syncHdr)
          #LOG('SubSync status code : ', DEBUG, status_code_syncHdr)
          if status_code_syncHdr == self.AUTH_REQUIRED:
            if self.checkChal(xml_client):
              authentication_format, authentication_type = self.getChal(xml_client)
              #LOG('SubSync auth_required :', DEBUG, 'format:%s, type:%s' % (authentication_format, authentication_type))
              if authentication_format is not None and \
                  authentication_type is not None:
                subscription.setAuthenticationFormat(authentication_format)
                subscription.setAuthenticationType(authentication_type)
            else:
              raise ValueError, "Sorry, the server chalenge for an \
                  authentication, but the authentication format is not find"

            LOG('SubSync', INFO, 'Authentication required')
            response = self.SubSyncCred(subscription, xml_client)
          elif status_code_syncHdr == self.UNAUTHORIZED:
            LOG('SubSync', INFO, 'Bad authentication')
            return {'has_response':0, 'xml':xml_client}
          else:
            response = self.SubSyncModif(subscription, xml_client)
        else:
          response = self.SubSyncModif(subscription, xml_client)

    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')
    else:
      return response

