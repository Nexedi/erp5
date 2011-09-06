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
from Products.CMFCore.utils import getToolByName
from ERP5Diff import ERP5Diff
from zLOG import LOG, INFO

from lxml import etree
from lxml.builder import ElementMaker
from SyncMLConstant import SYNCML_NAMESPACE, NSMAP, MAX_LEN
E = ElementMaker(namespace=SYNCML_NAMESPACE, nsmap=NSMAP)
parser = etree.XMLParser(remove_blank_text=True)

from base64 import b64encode, b64decode
from imp import load_source

def encode(format, string_to_encode):
  """
    return the string_to_encode encoded with format format
  """
  if not format:
    return string_to_encode
  if format == 'b64':
    return b64encode(string_to_encode)
  #elif format is .... put here the other formats
  else:#if there is no format corresponding with format, raise an error
    LOG('encode : unknown or not implemented format : ', INFO, format)
    raise ValueError, "Sorry, the server ask for the format %s but \
          it's unknow or not implemented" % format

def decode(format, string_to_decode):
  """
    return the string_to_decode decoded with format format
  """
  string_to_decode = string_to_decode.encode('utf-8')
  if not format:
    return string_to_decode
  if format == 'b64':
    return b64decode(string_to_decode)
  #elif format is .... put here the other formats
  else:#if there is no format corresponding with format, raise an error
    LOG('decode : unknown or not implemented format :', INFO, format)
    raise ValueError, "Sorry, the format %s is unknow or \
          not implemented" % format

def isDecodeEncodeTheSame(string_encoded, string_decoded, format):
  """
    return True if the string_encoded is equal to string_decoded encoded 
    in format
  """
  return encode(format, string_decoded) == string_encoded

def xml2wbxml(xml):
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

def wbxml2xml(wbxml):
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


def getConduitByName(conduit_name):
  """
  Get Conduit Object by given name.
  The Conduit can be located in Any Products according to naming Convention
  Products.<Product Name>.Conduit.<Conduit Module> ,if conduit_name equal module's name.
  By default Conduit must be defined in Products.ERP5SyncML.Conduit.<Conduit Module>
  Conduit can also be defined as Extension to have it editable through the web, in this
  case its definition must be Extensions.<Conduit Module>
  """
  if conduit_name.startswith('Products'):
    path = conduit_name
    conduit_name = conduit_name.split('.')[-1]
    conduit_module = __import__(path, globals(), locals(), [''])
  elif conduit_name.startswith('Extensions'):
    conduit_module = __import__(conduit_name, globals(), locals(), [''])
    conduit_name = conduit_name.split('.')[-1]
  else:
    from Products.ERP5SyncML import Conduit
    conduit_module = __import__('.'.join([Conduit.__name__, conduit_name]),
                                globals(), locals(), [''])
  conduit_instance = getattr(conduit_module, conduit_name)()
  return conduit_instance

def resolveSyncmlStatusCode(context, category_id):
  """Return reference of syncml_status_code category
  """
  category_tool = getToolByName(context.getPortalObject(), 'portal_categories')
  return category_tool.getCategoryValue(category_id,
                                        base_category='syncml_status_code')\
                                                                .getReference()

def resolveSyncmlAlertCode(portal, category_id):
  """Return reference of syncml_alert_code category
  """
  category_tool = getToolByName(portal, 'portal_categories')
  return category_tool.getCategoryValue(category_id,
                                        base_category='syncml_alert_code')\
                                                                .getReference()


def getAlertCodeFromXML(xml):
  """
    Return the value of the alert code inside the full syncml message
  """
  alert_code = '%s' % xml.xpath('string(/syncml:SyncML/syncml:SyncBody/'\
                                'syncml:Alert/syncml:Data)',
                                namespaces=xml.nsmap)
  return alert_code

def checkAlert(xml):
  """
    Check if there's an Alert section in the xml_stream
  """
  return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Alert)',
              namespaces=xml.nsmap))

def getMessageIdFromXml(xml):
  """
  We will retrieve the message id of the message
  """
  return int(xml.xpath('string(/syncml:SyncML/syncml:SyncHdr/syncml:MsgID)',
                       namespaces=xml.nsmap))

def getSubscriptionUrlFromXML(xml):
  """return the source URI of the syncml header
  """
  return '%s' % xml.xpath('string(//syncml:SyncHdr/syncml:Source/'\
                          'syncml:LocURI)', namespaces=xml.nsmap)

def checkFinal(xml):
  """
    Check if there's an Final section in the xml_stream
    The end sections (inizialisation, modification) have this tag
  """
  return  bool(xml.xpath('/syncml:SyncML/syncml:SyncBody/syncml:Final',
               namespaces=xml.nsmap))

def setRidWithMap(xml, subscriber):
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

def getSyncBodyStatusList(xml):
  """
  return the list of dictionary corredponding to the data of each status bloc
  the data are : cmd, code and source
  """
  status_list = []
  status_node_list = xml.xpath('//syncml:Status', namespaces=xml.nsmap)
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

def getDataText(xml):
  """
  return the section data in text form, it's usefull for the VCardConduit
  """
  return '%s' % xml.xpath('string(.//syncml:Item/syncml:Data)',
                          namespaces=xml.nsmap)

def getDataSubNode(xml):
  """
    Return the content of syncml stream
  """
  object_node_list = xml.xpath('.//syncml:Item/syncml:Data/*[1]',
                               namespaces=xml.nsmap)
  if object_node_list:
    return object_node_list[0]
  return None

def getXupdateObject(object_xml=None, old_xml=None):
  """
  Generate the xupdate with the new object and the old xml
  """
  erp5diff = ERP5Diff()
  erp5diff.compare(old_xml, object_xml)
  #Upper version of ERP5Diff produce valid XML.
  xupdate = erp5diff.outputString()
  #omit xml declaration
  xupdate = xupdate[xupdate.find('<xupdate:modifications'):]
  return xupdate

#def cutXML(xml_string):
  #"""
  #Sliced a xml tree a return two fragment
  #"""
  #line_list = xml_string.split('\n')
  #short_string = '\n'.join(line_list[:MAX_LINES])
  #rest_string = '\n'.join(line_list[MAX_LINES:])
  #xml_string = etree.CDATA(short_string.decode('utf-8'))
  #return xml_string, rest_string

def cutXML(xml_string):
  """
  Sliced a xml tree a return two fragment
  """
  short_string = xml_string[:MAX_LEN]
  rest_string = xml_string[MAX_LEN:]
  xml_string = etree.CDATA(short_string.decode('utf-8'))
  return xml_string, rest_string

class XMLSyncUtilsMixin(object):

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

  #def getNamespace(self, nsmap):
    #"""
      #Set the namespace prefix, check if argument is conform
      #and return the full namespace updated for syncml
      #nsmap -- The namespace of the received xml
    #"""
    ##search urn compatible in the namespaces of nsmap
    #urns = filter(lambda v: v.upper() in self.URN_LIST, nsmap.values())
    #if urns:
      #namespace = etree.FunctionNamespace(urns[0])
      #namespace.prefix = 'syncml'
      #return namespace
    #else:
      #raise ValueError, "Sorry, the given namespace is not supported"

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

  def checkStatus(self, xml):
    """
      Check if there's a Status section in the xml_stream
    """
    return bool(xml.xpath('string(/syncml:SyncML/syncml:SyncBody/syncml:Status)',
                namespaces=xml.nsmap))

  def getActionType(self, xml):
    """
      Return the type of the object described by the action
    """
    return '%s' % xml.xpath('string(.//syncml:Meta/syncml:Type)',
                            namespaces=xml.nsmap)

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


