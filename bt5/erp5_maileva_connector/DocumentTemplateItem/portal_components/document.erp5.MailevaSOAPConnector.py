# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 Nexedi SA and Contributors. All Rights Reserved.
#                    Aurélien Calonne <aurel@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
import suds
import base64


class MailevaElementOptions():
  def __init__(self, document):
    self._document = document
  def toXML(self):
    return '''
      <pjs:Options>
        <pjs:RequestOption>
          <mlv:DigitalOption>
            <mlv:FoldOption>
              <mlv:DepositTitle>%s</mlv:DepositTitle>
            </mlv:FoldOption>
            <mlv:DepositType>PAYSLIP</mlv:DepositType>
            <mlv:DigitalArchiving>600</mlv:DigitalArchiving>
          </mlv:DigitalOption>
        </pjs:RequestOption>
      </pjs:Options>
    ''' % self._document.getTitle()

class MailevaElementContent():
  def __init__(self, value):
    self._value = value
  def toXML(self):
    return '''
    <com:Content>
      <com:Value>%s</com:Value>
	  </com:Content>
    ''' % self._value

class MailevaElementDocumentData():
  def __init__(self, content):
    self._content = content
  def toXML(self):
    return '''
    <pjs:DocumentData>
      <pjs:Documents>
	    	<pjs:Document Id="001">
          %s
	  	  </pjs:Document>
	    </pjs:Documents>
    </pjs:DocumentData>
    ''' % (self._content.toXML())


class MailevaElementSender():
  def __init__(self, paper_address):
    self._paper_address = paper_address
  def toXML(self):
    return '''
    <pjs:Senders>
      <pjs:Sender Id="001">
        %s
      </pjs:Sender>
    </pjs:Senders>
    ''' % (self._paper_address.toXML())

class PaperAddress():
  def __init__(self, recipient):
    self._recipient = recipient
    # maybe use codification
    self. _country_code = {
      'Afghanistan': 'AF',
      'Afrique du Sud':'ZA',
      'Albanie': 'AL',
      'Algérie': 'DZ',
      'Allemagne': 'DE',
      'Andorre': 'AD',
      'Angola': 'AO',
      'Anguilla':'AI',
      'Antarctique': 'AQ',
      'Antigua et Barbuda': 'AG',
      'Antilles néerlandaises': 'AN',
      'Arabie saoudite': 'SA',
      'Argentine': 'AR',
      'Arménie': 'AM',
      'Aruba': 'AW',
      'Australie': 'AU',
      'Autriche': 'AT',
      'Azerbaidjan': 'AZ',
      'Bahamas': 'BS',
      'Bahrein': 'BH',
      'Bangladesh': 'BD',
      'Barbade': 'BB',
      'Bélarus': 'BY',
      'Belgique': 'BE',
      'Belize': 'BZ',
      'Bénin': 'BJ',
      'Bermudes': 'BM',
      'Bhoutan': 'BT',
      'Bolivie': 'BO',
      'Bosnie-Herzégovine': 'BA',
      'Botswana': 'BW',
      'Bouvet': 'BV',
      'Brésil': 'BR',
      'Brunei Darussalam': 'BN',
      'Bulgarie': 'BG',
      'Burkina Faso': 'BF',
      'Burundi': 'BI',
      'Caïmans': 'KY',
      'Cambodge': 'KH',
      'Cameroun': 'CM',
      'Canada': 'CA',
      'Cap-Vert': 'CV',
      'Centrafrique': 'CF',
      'Chili': 'CL',
      'Chine': 'CN',
      'Christmas': 'CX',
      'Chypre': 'CY',
      'Cocos': 'CC',
      'Colombie': 'CO',
      'Comores': 'KM',
      'Congo': 'CG',
      'Congo, La République Démocratique Du': 'CD',
      'Cook': 'CK',
      'Corée': 'KR',
      'Corée Populaire': 'KP',
      'Costa Rica': 'CR',
      "Côte d'Ivoire": 'CI',
      'Croatie': 'HR',
      'Cuba': 'CU',
      'Danemark': 'DK',
      'Djibouti': 'DJ',
      'Dominique': 'DM',
      'Egypte': 'EG',
      'El Salvador': 'SV',
      'Emirats Arabes Unis': 'AE',
      'Equateur': 'EC',
      'Erythrée': 'ER',
      'Espagne': 'ES',
      'Estonie': 'EE',
      'Etats-Unis': 'US',
      'Ethiopie': 'ET',
      'Falkland': 'FK',
      'Féroé': 'FO',
      'Fidji': 'FJ',
      'Finlande': 'FI',
      'France': 'FR',
      'Gabon': 'GA',
      'Gambie': 'GM',
      'Géorgie': 'GE',
      'Géorgie Du Sud Et Les Iles Sandwich Du Sud': 'GS',
      'Ghana': 'GH',
      'Gibraltar': 'GI',
      'Grèce': 'GR',
      'Grenade': 'GD',
      'Groenland': 'GL',
      'Guadeloupe': 'GP',
      'Guam': 'GU',
      'Guatemala': 'GT',
      'Guinée': 'GN',
      'Guinée-Bissau': 'GW',
      'Guinée équatoriale': 'GQ',
      'Guyana': 'GY',
      'Guyane française': 'GF',
      'Haïti': 'HT',
      'Heard et Mc Donald': 'HM',
      'Honduras': 'HN',
      'Hong-Kong': 'HK',
      'Hongrie': 'HU',
      'Iles Mineures des Etats-Unis': 'UM',
      'Iles Vierges Britanniques': 'VG',
      'Iles Vierges des Etats-Unis': 'VI',
      'Inde': 'IN',
      'Indonésie': 'ID',
      'Iran': 'IR',
      'Iraq': 'IQ',
      'Irlande': 'IE',
      'Islande': 'IS',
      'Israël': 'IL',
      'Italie': 'IT',
      'Jamaïque': 'JM',
      'Japon': 'JP',
      'Jordanie': 'JO',
      'Kazakhstan': 'KZ',
      'Kenya': 'KE',
      'Kirghizistan': 'KG',
      'Kiribati': 'KI',
      'Koweït': 'KW',
      'Laos': 'LA',
      'Lesotho': 'LS',
      'Lettonie': 'LV',
      'Liban': 'LB',
      'Libéria': 'LR',
      'Libye': 'LY',
      'Liechtenstein': 'LI',
      'Lituanie': 'LT',
      'Luxembourg': 'LU',
      'Macao': 'MO',
      "Macédoine, L'ex-République Yougoslave De": 'MK',
      'Madagascar': 'MG',
      'Malaisie': 'MY',
      'Malawi': 'MW',
      'Maldives': 'MV',
      'Mali': 'ML',
      'Malte': 'MT',
      'Mariannes Septentrionales': 'MP',
      'Maroc': 'MA',
      'Marshall': 'MH',
      'Martinique': 'MQ',
      'Maurice': 'MU',
      'Mauritanie': 'MR',
      'Mayotte': 'YT',
      'Mexique': 'MX',
      'Micronésie': 'FM',
      'Moldavie': 'MD',
      'Monaco': 'MC',
      'Mongolie': 'MN',
      'Montserrat':'MS',
      'Mozambique': 'MZ',
      'Myanmar': 'MM',
      'Namibie': 'NA',
      'Nauru': 'NR',
      'Népal': 'NP',
      'Nicaragua': 'NI',
      'Niger': 'NE',
      'Nigéria': 'NG',
      'Nioué': 'NU',
      'Norfolk': 'NF',
      'Norvège': 'NO',
      'Nouvelle-Calédonie': 'NC',
      'Nouvelle-Zélande': 'NZ',
      'Océan Indien': 'IO',
      'Oman': 'OM',
      'Ouganda': 'UG',
      'Ouzbekistan': 'UZ',
      'Pakistan': 'PK',
      'Palau': 'PW',
      'Palestinien Occupé, Territoire': 'PS',
      'Panama': 'PA',
      'Papouasie-Nouvelle-Guinée': 'PG',
      'Paraguay': 'PY',
      'Pays-Bas': 'NL',
      'Pérou': 'PE',
      'Philippines': 'PH',
      'Pitcairn': 'PN',
      'Pologne': 'PL',
      'Polynésie française': 'PF',
      'Porto Rico': 'PR',
      'Portugal': 'PT',
      'Qatar': 'QA',
      'République Slovaque': 'SK',
      'République Tchèque': 'CZ',
      'République Dominicaine': 'DO',
      'Réunion': 'RE',
      'Roumanie': 'RO',
      'Royaume-Uni':'GB',
      'Russie': 'RU',
      'Rwanda': 'RW',
      'Sahara occidental': 'EH',
      'Saint-Barthélemy': 'BL',
      'Saint-Kitts-et-Nevis': 'KN',
      'Saint-Marin': 'SM',
      'Saint-Martin (partie française)': 'MF',
      'Saint-Pierre-et-Miquelon': 'PM',
      'Saint-Vincent-et-les-Grenadines': 'VC',
      'Sainte-Hélène': 'SH',
      'Sainte-Lucie': 'LC',
      'Salomon': 'SB',
      'Samoa': 'WS',
      'Samoa américaines': 'AS',
      'Sao Tomé-et-Principe': 'ST',
      'Sénégal': 'SN',
      'Serbie-et-Monténégro': 'CS',
      'Seychelles': 'SC',
      'Sierra Leone': 'SL',
      'Singapour': 'SG',
      'Slovénie': 'SI',
      'Somalie': 'SO',
      'Soudan': 'SD',
      'Sri Lanka': 'LK',
      'Suède': 'SE',
      'Suisse': 'CH',
      'Suriname': 'SR',
      'Svalbard et île Jan Mayen': 'SJ',
      'Swaziland': 'SZ',
      'Syrie': 'SY',
      'Tadjikistan': 'TJ',
      'Taïwan': 'TW',
      'Tanzanie': 'TZ',
      'Tchad': 'TD',
      'Terres australes françaises': 'TF',
      'Thaïlande': 'TH',
      'Timor-Leste': 'TL',
      'Togo': 'TG',
      'Tokélaou': 'TK',
      'Tonga': 'TO',
      'Trinité-et-Tobago': 'TT',
      'Tunisie': 'TN',
      'Turkménistan': 'TM',
      'Turks et Caiques': 'TC',
      'Turquie': 'TR',
      'Tuvalu': 'TV',
      'Ukraine': 'UA',
      'Uruguay': 'UY',
      'Vanuatu': 'VU',
      'Vatican': 'VA',
      'Venezuela': 'VE',
      'Viet Nam': 'VN',
      'Wallis et Futuna': 'WF',
      'Yémen': 'YE',
      'Zambie': 'ZM',
      'Zimbabwe': 'ZW'
    }

  def toXML(self):
    address_line = self._recipient.getDefaultAddressText()
    country = self._recipient.getDefaultAddressRegionTitle()
    if country not in self._country_code:
      raise ValueError('Unknown Country: %s' % country)
    country_code = self._country_code[country]
    if self._recipient.getPortalType() == 'Person':
      address_line_xml = "<com:AddressLine1>%s %s</com:AddressLine1>" % (self._recipient.getSocialTitleTitle(), self._recipient.getTitle())
    else:
      address_line_xml = "<com:AddressLine1>%s</com:AddressLine1>" % self._recipient.getCorporateName()
    address_line_list = address_line.split('\n')
    if len(address_line_list) > 5:
      raise ValueError('Address %s has more than 5 lines' % address_line)
    if len(address_line_list) < 2:
      raise ValueError('Address %s has less than 2 lines' % address_line)
    for index in range(len(address_line_list) - 1):
      address_line_xml += "<com:AddressLine%s>%s</com:AddressLine%s>\n" % (index + 2, address_line_list[index], index + 2)
    address_line_xml += "<com:AddressLine6>%s</com:AddressLine6>\n" % (address_line_list[-1])
    return '''
    <com:PaperAddress>
	  	<com:AddressLines>
        %s
  		</com:AddressLines>
  		<com:Country>%s</com:Country>
  		<com:CountryCode>%s</com:CountryCode>
	</com:PaperAddress>
  ''' % (address_line_xml, country, country_code)

class DigitalAddress():
  def __init__(self, recipient, job_start_date):
    self._recipient = recipient
    self._job_start_date = job_start_date
  def toXML(self):
    return '''
    <com:DigitalAddress>
     <com:FirstName>%s</com:FirstName>
     <com:LastName>%s</com:LastName>
	   <com:Identifier>%s</com:Identifier>
     <com:JobPosition>%s</com:JobPosition>
     <com:JobStartDate>%s</com:JobStartDate>
    </com:DigitalAddress>
    ''' % (self._recipient.getRegistrationNumber(), self._recipient.getFirstName(), self._recipient.getLastName(), self._recipient.getCareerTitle(), self._job_start_date)

class MailevaElementRecipient():
  def __init__(self, paper_address, digital_address):
    self._paper_address = paper_address
    self._digital_address = digital_address
  def toXML(self):
    return '''
    <pjs:Recipients>
      <pjs:Internal>
        <pjs:Recipient Id="1">
          %s
          %s
        </pjs:Recipient>
      </pjs:Internal>
    </pjs:Recipients>
     ''' %( self._paper_address.toXML(), self._digital_address.toXML())

class MailevaElementRequest():
  def __init__(self, recipient, sender, document_data, options):
    self._recipient = recipient
    self._sender =  sender
    self._document_data = document_data
    self._options = options
  def toXML(self):
    return '''
    <pjs:Requests>
      <pjs:Request MediaType="DIGITAL" TrackId="Bulletindesalaires">
        %s
        %s
        %s
        %s
      </pjs:Request>
   </pjs:Requests>
   ''' % (self._sender.toXML(), self._recipient.toXML(), self._document_data.toXML(), self._options.toXML())

class MailevaElementUser():

  def __init__(self, login, password):
    self._login = login
    self._password = password

  def toXML(self):
    return '''
    <pjs:User AuthType="PLAINTEXT">
      <pjs:Login>%s</pjs:Login>
      <pjs:Password>%s</pjs:Password>
    </pjs:User>
    ''' % (self._login, self._password)

class MailevaElementCampaign():

  def __init__(self, user, requests):
    self._user = user
    self._requests = requests

  def toXML(self):
    return '''
    <?xml version="1.0" encoding="UTF-8"?>
<pjs:Campaign  xmlns:com="http://www.maileva.fr/CommonSchema"
  xmlns:pjs="http://www.maileva.fr/MailevaPJSSchema"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:mlv="http://www.maileva.fr/MailevaSpecificSchema"
  xmlns:spec="http://www.maileva.fr/MailevaSpecificSchema">
  Version="5.0" Application="connecteur_Maileva">
    %s
    %s
</pjs:Campaign>
  ''' % (self._user.toXML(), self._requests.toXML())

class MailevaSOAPConnector(XMLObject):
  # CMF Type Definition
  meta_type = 'Mail Eva Soap Connector'
  portal_type = 'Mail Eval Soap Connector'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                      )
  def submitRequest(self, recipient, sender, document):
    xml = self.generateRequestXML(recipient, sender, document)
    response =suds.client.Client(self.getUrlString()).service.submit(xml)
    return xml, response

  def generateRequestXML(self, recipient, sender, document):
    # maileval login/password
    user = MailevaElementUser(self.getUserId(), self.getPassword())

    # recipient address
    recipient_paper_address = PaperAddress(recipient)

    source_section_career_results = self.getPortalObject().portal_catalog(
      portal_type = 'Career',
      parent_uid = recipient.getUid(),
      subordination_uid = sender.getUid(),
      validation_state = 'open'
    )
    source_section_career = (source_section_career_results[0].getObject()if len(source_section_career_results) else recipient.getDefaultCareerValue() or '')
    digital_address = DigitalAddress(recipient, source_section_career.getStartDate())
    recipient = MailevaElementRecipient(recipient_paper_address, digital_address)

    #sender address
    sender_paper_address = PaperAddress(sender)
    sender = MailevaElementSender(sender_paper_address)

    # document content
    content = MailevaElementContent(base64.b64encode(document.getData()))
    document_data = MailevaElementDocumentData(content)

    options = MailevaElementOptions(document)
    # request
    requests = MailevaElementRequest(recipient, sender, document_data, options)

    # main element
    campaign = MailevaElementCampaign(user, requests)
    return campaign.toXML().decode('utf8')

