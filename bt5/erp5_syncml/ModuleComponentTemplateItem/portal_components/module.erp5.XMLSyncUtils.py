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
import os
from base64 import b64encode, b64decode
from lxml import etree
from lxml.builder import ElementMaker

from zLOG import LOG, INFO
from ERP5Diff import ERP5Diff
from DateTime import DateTime

from erp5.component.module.SyncMLConstant import SYNCML_NAMESPACE, NSMAP, MAX_LEN
from Products.ERP5.ERP5Site import getSite

E = ElementMaker(namespace=SYNCML_NAMESPACE, nsmap=NSMAP)
parser = etree.XMLParser(remove_blank_text=True)

def buildAnchorFromDate(date):
  if isinstance(date, DateTime):
    date = date.HTML4()
  date = date.replace("-", "")
  date = date.replace(":", "")
  return date


def encode(format, string_to_encode): # pylint: disable=redefined-builtin
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
    raise ValueError("Sorry, the server ask for the format %s but"
          " it's unknown or not implemented" % format)

def decode(format, string_to_decode): # pylint: disable=redefined-builtin
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
    raise ValueError("Sorry, the format %s is unknown or not implemented" % format)

def isDecodeEncodeTheSame(string_encoded, string_decoded, format): # pylint: disable=redefined-builtin
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
  By default Conduit must be defined as ZODB Components (erp5.component.module.<Conduit Module>)
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
  elif conduit_name.startswith('extension.'):
    conduit_module = __import__("erp5.component."+conduit_name, globals(), locals(), [''])
    conduit_name = conduit_name.split('.')[-1]
  else:
    conduit_module = __import__('erp5.component.module.'+conduit_name, globals(), locals(), [''])
  conduit_instance = getattr(conduit_module, conduit_name)()
  return conduit_instance

def resolveSyncmlStatusCode(category_id):
  """Return reference of syncml_status_code category
  """
  try:
    return str(int(category_id))
  except ValueError:
    return getSite().portal_categories.getCategoryValue(
      category_id,
      base_category='syncml_status_code').getReference()

def resolveSyncmlAlertCode(category_id):
  """Return reference of syncml_alert_code category
  """
  try:
    return str(int(category_id))
  except ValueError:
    return getSite().portal_categories.getCategoryValue(
            category_id,
            base_category='syncml_alert_code').getReference()


# def setRidWithMap(xml, subscriber):
#   """
#     get all the local objects of the given target id and set them the rid with
#     the given source id (in the Map section)
#   """
#   item_list = xml.xpath('/syncml:SyncML/syncml:SyncBody/syncml:Map/syncml:MapItem',
#                         namespaces=xml.nsmap)
#   for map_item in item_list:
#     gid = '%s' % map_item.xpath('string(.//syncml:Target/syncml:LocURI)', namespaces=xml.nsmap)
#     signature = subscriber.getSignatureFromGid(gid)
#     rid = '%s' % map_item.xpath('string(.//syncml:Source/syncml:LocURI)', namespaces=xml.nsmap)
#     signature.setRid(rid)


def getXupdateObject(object_xml=None, old_xml=None):
  """
  Generate the xupdate with the new object and the old xml
  """
  erp5diff = ERP5Diff()
  erp5diff.compare(old_xml, object_xml)
  #Upper version of ERP5Diff produce valid XML.
  if erp5diff._getResultRoot():
    xupdate = erp5diff.outputString()
    #omit xml declaration
    xupdate = xupdate[xupdate.find('<xupdate:modifications'):]
    return xupdate

def cutXML(xml_string, length=None):
  """
  Sliced a xml tree a return two fragment
  """
  if length is None:
    length = MAX_LEN
  short_string = xml_string[:length]
  rest_string = xml_string[length:]
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

