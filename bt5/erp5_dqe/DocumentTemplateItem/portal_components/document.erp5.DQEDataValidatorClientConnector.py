import requests
from json import loads
from socket import timeout
from requests import ConnectionError as _ConnectionError, Timeout
from Products.ERP5Type.XMLObject import XMLObject
from six.moves import urllib
from zLOG import LOG, INFO

class DQEDataValidatorClientConnector(XMLObject):

  def call(
    self,
    method_name,
    service,
    params=None,
    archive_kw=None,
  ):
    if params is None:
      params = {}
    params['Licence'] = self.getLicenseNumber()
    if archive_kw is None:
      archive_kw = {}
    try:
      base_url = self.getServerUrl() + method_name + '/'
      response = requests.get(base_url, params=params, timeout=self.getTimeout())
    except (Timeout, timeout, _ConnectionError):
      raw_response = 'TIMEOUT'
      result_dict = {}
    else:
      if response.ok:
        raw_response = response.content
        result_dict = loads(raw_response)
      else:
        LOG(
          'DQEDataValidatorClientConnector', INFO,
          'DQEDataValidatorClientConnector returns Non-ok response : %s' % response.text
        )
        raw_response = response.text
        result_dict = {}
    finally:
      archiveExchange = self._getTypeBasedMethod('archiveExchange')
      if archiveExchange is not None:
        archiveExchange(
          raw_request=base_url + '?' + urllib.urlparse.urlencode(params), # XXX is this correct?
          raw_response=raw_response,
          service=service,
          archive_kw=archive_kw,
          comment='',
        )
    return result_dict

  def validateEmailAddress(
    self,
    email_string,
    service,
    archive_kw=None,
  ):
    response = self.call(
      'DQEEMAILLOOKUP',
      service,
      params={
        'Email': email_string,
      },
      archive_kw=archive_kw,
    )
    return response

  def validatePostalAddress(
    self,
    address,
    country_code,
    service,
    max_size=38,
    archive_kw=None,
  ):
    response = self.call(
      'RNVP',
      service,
      params={
        'Adresse': address,
        'Pays': country_code,
        'Instance': 0,
        'Taille': max_size,
      },
      archive_kw=archive_kw,
    )
    return response

  def validateTelephoneNumber(
    self,
    telephone_number,
    country_code,
    service,
    number_format=0,
    status='N',
    archive_kw=None,
  ):
    response = self.call(
      'TEL',
      service,
      params={
        'Tel': telephone_number,
        'Pays': country_code,
        'Format': number_format,
        'Status': status,
      },
      archive_kw=archive_kw,
    )
    return response

  def validateSIRETNumber(
    self,
    siret_number,
    service,
    archive_kw=None,
  ):
    response = self.call(
      'SIRETINFO',
      service,
      params={
        'Siret': siret_number,
      },
      archive_kw=archive_kw,
    )
    return response

  def checkRelocation(
    self,
    first_name,
    last_name,
    address,
    zip_code,
    city,
    service,
    social_title='',
    complement='',
    lieu_dit='',
    archive_kw=None,
  ):
    response = self.call(
      'ESTOCADE',
      service,
      params={
        'Nom': last_name,
        'Prenom': first_name,
        'Adresse': address,
        'CodePostal': zip_code,
        'Ville': city,
        'Civilite': social_title,
        'Complement': complement,
        'LieuDit': lieu_dit,
      },
      archive_kw=archive_kw,
    )
    return response
