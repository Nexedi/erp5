import six
translateString = context.Base_translateString
portal = context.getPortalObject()
portal_preferences = portal.portal_preferences

def getFieldAsString(field):
  return ', '.join(getFieldAsLineList(field))

def getFieldAsLineList(field):
  """Returns the text as a list of lines."""
  field = field or ''
  text = field.replace('\r', '')
  text_list = text.split('\n')
  return [x for x in text_list if x]

def getOneLineAddress(text, region):
  text_list = [getFieldAsString(text)]
  if region:
    text_list.append(region)
  return ', '.join(text_list)

def getPhoneAndFax(phone, fax):
  s = ''
  if phone:
    s += '%s: %s' % (translateString('Tel'), phone)
  if fax:
    if s: s += ', '
    s += '%s: %s' % (translateString('Fax'), fax)
  return s

def getPreferredOrganisation():
  organisation = None
  organisation_url = portal_preferences.getPreferredSection()
  if organisation_url:
    organisation = portal.restrictedTraverse(organisation_url)
  return organisation

def getDelayTitle():
  if not context.getSaleSupplyLineMinDelay() and not context.getSaleSupplyLineMaxDelay():
    return None
  return translateString('${begin} to ${end} Weeks',
      mapping=dict(begin=int(context.getSaleSupplyLineMinDelay()/7.) or 0,
                   end=int(context.getSaleSupplyLineMaxDelay()/7.) or 0))

def getMorphologyTitle():
  apparel_morphology_list = context.contentValues(portal_type='Apparel Model Morphology Variation')
  apparel_morphology_title_list = [x.getTitle() for x in apparel_morphology_list]
  return ', '.join(apparel_morphology_title_list)

def getShapeMainImagePath():
  apparel_shape = context.getSpecialiseValue(portal_type='Apparel Shape')
  if apparel_shape:
    technical_drawing_list = apparel_shape.contentValues(portal_type='Apparel Technical Drawing')
    if len(technical_drawing_list):
      return technical_drawing_list[0].absolute_url()
  return None

def getPrototype():
  for colour_variation in context.contentValues(portal_type='Apparel Model Colour Variation'):
    if colour_variation.isPrototype():
      return colour_variation
  return None

def unicodeDict(d):
  if six.PY3:
    return d
  for k, v in six.iteritems(d):
    if isinstance(v, str):
      d.update({k: unicode(v, 'utf8')})
  return d

data_dict = {
  'delay_title': getDelayTitle() or '',
  'morphology_title': getMorphologyTitle() or '',
  'shape_main_image_path': getShapeMainImagePath() or '',
  'prototype_title': getPrototype() is not None and \
      getPrototype().getDestinationReference() or '',
  'prototype_image_path': getPrototype() is not None and getPrototype().absolute_url() or '',
  'preferred_organisation_image_path': getPreferredOrganisation() is not None\
      and getPreferredOrganisation().getDefaultImageAbsoluteUrl() or '',
  'preferred_organisation_corporate_name': getPreferredOrganisation() is not None\
      and (getPreferredOrganisation().getCorporateName() or\
        getPreferredOrganisation().getTitle()) or '',
  'preferred_organisation_address': getOneLineAddress(
            getPreferredOrganisation() is not None and\
              getPreferredOrganisation().getDefaultAddressText() or '',
            getPreferredOrganisation() is not None and\
              getPreferredOrganisation().getDefaultAddressRegionTitle() or ''),
  'preferred_organisation_telfax': getPhoneAndFax(
            getPreferredOrganisation() is not None and\
              getPreferredOrganisation().getTelephoneText() or '',
            getPreferredOrganisation() is not None and\
              getPreferredOrganisation().getFaxText() or ''),
  }

return data_dict
