# vobject integration for ERP5

try:
  import vobject
except ImportError:
  raise ImportError('vobject is not properly installed, get it from '\
                    ' http://vobject.skyhouseconsulting.com')

def decode(string):
  if not string:
    return ''
  return unicode(string, 'utf8', 'repr')

def Person_viewPersonAsvCard(self, REQUEST=None):
  """Returns a vCard representation of a Person object.
  """
  vcard = vobject.vCard()
  # name
  vcard.add('n')
  vcard.n.value = vobject.vcard.Name( family=decode(self.getFirstName()),
                                      given=decode(self.getLastName()),
                                      additional=decode(self.getMiddleName()),
                                      prefix=decode(self.getPrefix()),
                                      suffix=decode(self.getSuffix()) )
  # formatted name
  vcard.add('fn')
  vcard.fn.value = decode(self.getTitle())
  
  # organisation
  if self.getSubordination():
    vcard.add('org')
    vcard.org.value = decode(self.getSubordinationTitle())

  # default email
  email = self.getDefaultEmailValue()
  if email is not None:
    vcard.add('email')
    vcard.email.value = email.getUrlString()
    vcard.email.type_param = 'PREF'
  
  # alt. emails
  for addr in self.contentValues(filter=dict(portal_type=['Email'])):
    if addr.getId() not in ('default_email', ):
      c = vcard.add('email')
      c.value = decode(addr.asText())
      c.type_param = 'INTERNET'

  # default address
  address = self.getDefaultAddressValue()
  if address is not None:
    addr = vcard.add('adr')
    addr.value = vobject.vcard.Address(
                                street=decode(address.getStreetAddress()),
                                city=decode(address.getCity()),
                                region=decode(address.getRegionTitle()),
                                code=decode(address.getZipCode()))
    addr.type_param = 'PREF'

  # alt. addresses
  for addr in self.contentValues(filter=dict(portal_type=['Address'])):
    if addr.getId() not in ('default_address', ):
      c = vcard.add('adr')
      c.value = vobject.vcard.Address(
                                street=decode(addr.getStreetAddress()),
                                city=decode(addr.getCity()),
                                region=decode(addr.getRegionTitle()),
                                code=decode(addr.getZipCode()))
      c.type_param = decode(addr.getTitle())

  # default telephone
  tel = self.getDefaultTelephoneValue()
  if tel is not None:
    vcard.add('tel')
    vcard.tel.value = decode(tel.asText())
    vcard.tel.type_param = 'PREF'
  
  # default fax
  default_fax = self.getDefaultFaxValue()
  if default_fax is not None:
    fax = vcard.add('tel')
    fax.value = decode(default_fax.asText())
    fax.type_param = 'FAX'
  
  # alt. telephones
  for tel in self.contentValues(filter=dict(
                         portal_type=['Telephone', 'Fax'])):
    if tel.getId() not in ('default_telephone', 'default_fax'):
      c = vcard.add('tel')
      c.value = decode(tel.asText())

  # default image
  if getattr(self, 'getDefaultImage', None) is not None:
    image = self.getDefaultImage()
    if image is not None:
      photo = vcard.add('photo')
      photo.value = image.manage_FTPget()
      photo.encoding_param = 'b'

  if REQUEST:
    REQUEST.RESPONSE.setHeader('Content-type', 'text/x-vcard')
  return vcard.serialize().encode('utf8')
  
def PersonModule_importvCard(self):
  """Import persons from a vCard file.
  """
  return NotImplemented

