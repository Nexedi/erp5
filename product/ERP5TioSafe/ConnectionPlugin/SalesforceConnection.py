##############################################################################
#
# Copyright (c) 2010 Nexedi SARL and Contributors. All Rights Reserved.
#                    Herve Poulain <herve@nexedi.com>
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

import urllib2
from lxml import etree
from Products.ERP5TioSafe.Utils import EchoDictTarget

class MethodWrapper(object):

  def __init__(self, method, conn):
    self._method = method
    self._conn = conn

  def __call__(self, **kw):
    body = kw.get('data')
    if body is None:
      return
    # add session and body to the xml query and realise query

    # FIXME-RV: The following namespaces are not used so remove from the message
    # it's possible that you need for other element but to sync plugin -> erp5
    # it's not requires
#    xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/"
#    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#    xmlns:urn1="urn:sobject.partner.soap.sforce.com"
    data = """
      <soapenv:Envelope xmlns:ns0="urn:partner.soap.sforce.com"
                        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Header>
          <ns0:SessionHeader>
            <ns0:sessionId>%s</ns0:sessionId>
          </ns0:SessionHeader>
        </soapenv:Header>
        <soapenv:Body>
          %s
        </soapenv:Body>
      </soapenv:Envelope>""" % (self._conn._session_id, body)

    request = urllib2.Request(
        url=self._conn._server_url,
        headers=self._conn._header,
        data=data,
    )
    response = urllib2.urlopen(request)
    # ------------------------ #
    # test to send an insert
    test_data = """
      <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                         xmlns:urn="urn:partner.soap.sforce.com"
                         xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
        <soapenv:Header>
          <urn:SessionHeader>
            <urn:sessionId>%s</urn:sessionId>
          </urn:SessionHeader>
        </soapenv:Header>
        <soapenv:Body>
          <urn:create>
            <urn:sObjects xsi:type="ns3:Contact" 
                          xmlns:ns3="urn:sobject.enterprise.soap.sforce.com">
              <ns3:Name><b>Kirk Hammett</b></ns3:Name>
              <ns3:FirstName><b>Kirk</b></ns3:FirstName>
              <ns3:LastName><b>Hammett</b></ns3:LastName>
              <ns3:Email><b>kirk@hammett.com</b></ns3:Email>
            </urn:sObjects>
          </urn:create>
        </soapenv:Body>
      </soapenv:Envelope>""" % (self._conn._session_id, )
    rq = urllib2.Request(
        url=self._conn._server_url,
        headers=self._conn._header,
        data=test_data,
    )
    import pdb; pdb.set_trace()
    res = urllib2.urlopen(rq)
    # ------------------------ #
    return self._conn._server_url, response.read()


class SalesforceConnection:
  """
    Holds an Salesforce connection.
  """
  __allow_access_to_unprotected_subobjects__ = 1

  def __init__(self, url, user_name=None, password=None, credentials=None):
    """
    url (string)
      The requested url
    user_name (string or None)
    password (string is None)
      The password is composed by user password and token.
    credentials (AuthenticationBase subclass instance or None)
      The interface-level (http) credentials to use.
    """
    self._url = url
    self._user_name = user_name
    self._password = password
    self._credentials = credentials
    self._session_id = None
    self._server_url = None
    self._header = {
        'Content-type': 'text/xml',
        'Soapaction': u'""',
        'User-agent': 'Python',
    }

  def connect(self):
    """Get a handle to a remote connection."""
    # Declare:
    #   - header used to login through http request
    #   - data sent for login to salesforce
    #   - paser_dict allows to parse and retrieve data from xml
    headers = self._header.copy()
    headers['Soapaction'] = u'login'
    headers['Username'] = self._user_name
    headers['Password'] = self._password
    data = """
      <soapenv:Envelope soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                        xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/"
                        xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
                        xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:xsd="http://www.w3.org/1999/XMLSchema">
        <soapenv:Body>
          <ns1:login xmlns:ns1="urn:partner.soap.sforce.com" soapenc:root="1">
            <username xsi:type="xsd:string">%s</username>
            <password xsi:type="xsd:string">%s</password>
          </ns1:login>
        </soapenv:Body>
      </soapenv:Envelope>""" % (self._user_name, self._password)
    base_tag = '{urn:partner.soap.sforce.com}'
    parser_dict = {
        base_tag+'result' : ('result', True),
        base_tag+'serverUrl' : ('server_url', False),
        base_tag+'sessionId' : ('session_id', False),
    }
    # Execute query, retrieve xml response and save session id and serveur url
    # to realise queries
    request = urllib2.Request(url=self._url, headers=headers, data=data)
    response = urllib2.urlopen(request)
    xml = response.read()
    parser = etree.XMLParser(target = EchoDictTarget(parser_dict))
    result = etree.XML(str(xml), parser,)
    assert(len(result), 1) # Only one result, which contains session elements
    self._server_url = result[0]['server_url']
    self._session_id = result[0]['session_id']
    return self

  def __getattr__(self, name):
    if not name.startswith("_"):
      return MethodWrapper(name, self)
