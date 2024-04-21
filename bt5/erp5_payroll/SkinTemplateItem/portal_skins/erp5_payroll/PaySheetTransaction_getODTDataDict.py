import six
translateString = context.Base_translateString


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

def getEmail(email):
  s = ''
  if email:
    s += '%s: %s' % (translateString('Email'), email)
  return s

def getVatId(vat_id):
  s = ''
  if vat_id:
    s += '%s: %s' % (translateString('VAT ID'), vat_id)
  return s

def getActivityCodeId(activity_code_id):
  s = ''
  if activity_code_id:
    s += '%s: %s' % (translateString('Activity Code'), activity_code_id)
  return s

def getCorporateRegistrationCodeId(corporate_registration_code_id):
  s = ''
  if corporate_registration_code_id:
    s += '%s: %s' % (translateString('Corporate Registration Code'), corporate_registration_code_id)
  return s

def getSocialCodeId(social_code_id):
  s = ''
  if social_code_id:
    s += '%s: %s' % (translateString('Social Code'), social_code_id)
  return s

def getCareerId(career_title):
  s = ''
  if career_title:
    s += '%s: %s' % (translateString('Career Title'), career_title)
  return s

preferred_date_order = context.getPortalObject().portal_preferences\
                                          .getPreferredDateOrder() or 'ymd'
def getOrderedDate(date):
  if date is None:
    return ''
  date_parts = {
    'y': '%04d' % date.year(),
    'm': '%02d' % date.month(),
    'd': '%02d' % date.day(),
  }
  return '/'.join([date_parts[part] for part in preferred_date_order])

def getPaymentConditionText(order):
  if order.getPaymentConditionPaymentEndOfMonth():
    return translateString("End of Month")
  days = order.getPaymentConditionPaymentTerm()
  if days:
    return '%s %s' % (days, translateString('Days'))
  return ''

def getSocialOrganisationValue():
  model = context.getSpecialiseValue()
  if model is not None:
    business_process_list = model.findEffectiveSpecialiseValueList(\
              context=context, portal_type_list=['Business Process'])
    business_process = None
    if len(business_process_list):
      # XXX currently, is too complicated to use more than
      # one Business Process, so the first (which is the nearest from the
      # delivery) is took
      business_process = business_process_list[0]
      business_path_list = business_process.getTradeModelPathValueList(trade_phase=\
          'payroll/invoicing/social_security', context=context)
      if len(business_path_list) > 1:
        raise NotImplementedError('For now, it can not support more'
              ' than one business_path with same trade_phase.'
              ' %r have same trade_phase' % business_path_list)
      if len(business_path_list) == 1:
        business_path = business_path_list[0]
        return business_path.getSourceSectionValue()

  return None


line_list = []
total_price = 0.0

def unicodeDict(d):
  if six.PY3:
    return d
  for k, v in six.iteritems(d):
    if isinstance(v, str):
      d.update({k: six.text_type(v, 'utf8')})
  return d

line_list = context.PaySheetTransaction_getLineListAsDict()
inch_cm_ratio = 2.54 / 100.0

class EmptyOrganisation:
  """Used for default when organisation is not found.
  """
  def getTitle(self):
    return ''
  def getDefaultAddressText(self):
    return ''
  def getDefaultAddressRegionTitle(self):
    return ''
  def getDefaultImagePath(self):
    return ''
  def getDefaultImageHeight(self):
    return 0
  def getDefaultImageWidth(self):
    return 0
  def getProperty(self, prop, d=''):
    return d

source = context.getSourceValue()
if source is None:
  source = EmptyOrganisation()

destination = context.getDestinationValue()
if destination is None:
  destination = EmptyOrganisation()

source_section = context.getSourceSectionValue()
if source_section is None:
  source_section = EmptyOrganisation()

destination_section = context.getDestinationSectionValue()
if destination_section is None:
  destination_section = EmptyOrganisation()

source_administration = context.getSourceAdministrationValue(
                              portal_type='Organisation')
if source_administration is None:
  source_administration = context.getSourceSectionValue()
if source_administration is None:
  source_administration = EmptyOrganisation()

destination_administration = context.getDestinationAdministrationValue(
                              portal_type='Organisation')
if destination_administration is None:
  destination_administration = context.getDestinationSectionValue()
if destination_administration is None:
  destination_administration = EmptyOrganisation()

social_organisation = getSocialOrganisationValue()

data_dict = {
  'source_section_title': source_section.getProperty('corporate_name') or\
                            source_section.getTitle(),
  'source_section_image_path': context.getSourceSectionValue() is not None\
          and context.getSourceSectionValue().getDefaultImagePath() or '',
  'source_section_image_width': context.getSourceSectionValue() is not None\
          and context.getSourceSectionValue().getDefaultImageWidth()  is not None\
          and context.getSourceSectionValue().getDefaultImageWidth() \
              * inch_cm_ratio or '',
  'source_section_image_height': context.getSourceSectionValue() is not None\
          and context.getSourceSectionValue().getDefaultImageHeight()  is not None\
          and context.getSourceSectionValue().getDefaultImageHeight() \
              * inch_cm_ratio or '',
  'source_section_address': context.getSourceSection() and
              context.getSourceSectionValue().getDefaultAddressText() or '',
  'source_section_telfax': getPhoneAndFax(context.getSourceSection() and \
                        context.getSourceSectionValue().getTelephoneText() or '',
          context.getSourceSection() and \
              context.getSourceSectionValue().getFaxText() or ''),
  'source_section_email': getEmail(context.getSourceSection() and
          context.getSourceSectionValue().getEmailText() or ''),
  'source_section_vatid': getVatId(context.getSourceSection() and\
                           getattr(context.getSourceSectionValue(), 'getVatCode', None)\
                           is not None and\
                           context.getSourceSectionValue().getVatCode() or ''),
  'source_section_career_title': getCareerId(context.getSourceSection() and
          context.getSourceSectionValue().getCareerTitle() or ''),

  'source_administration_title': \
      source_administration.getProperty('corporate_name') \
      or source_administration.getTitle(),
  'source_administration_address': getOneLineAddress(
                                      source_administration.getDefaultAddressText(),
                                      source_administration.getDefaultAddressRegionTitle()),
  'source_administration_telfax':
          getPhoneAndFax(source_administration.getProperty('telephone_text', ''),
                         source_administration.getProperty('fax_text', '')),
  'source_administration_email':
          getEmail(source_administration.getProperty('email_text', '')),
  'source_administration_vatid':
          getVatId(source_administration.getProperty('vat_code', '')),

  'source_title': source.getProperty('corporate_name') or source.getTitle(),
  'source_address': getOneLineAddress(
          context.getSource() and
              context.getSourceValue().getDefaultAddressText() or '',
          context.getSource() and
              context.getSourceValue().getDefaultAddressRegionTitle() or ''),
  'source_telfax': getPhoneAndFax(context.getSource() and \
                        context.getSourceValue().getTelephoneText() or '',
          context.getSource() and \
              context.getSourceValue().getFaxText() or ''),
  'source_email': getEmail(context.getSource() and
          context.getSourceValue().getEmailText() or ''),
  'source_vatid': getVatId(context.getSource() and
      context.getSourceValue().getProperty('vat_code', '') or ''),

  'source_decision_title': context.getSourceDecisionTitle() or '',
  'source_decision_image_path': context.getSourceDecisionValue(portal_type='Organisation') is not None\
          and context.getSourceDecisionValue(portal_type='Organisation').getDefaultImagePath() or '',
  'source_decision_image_width': context.getSourceDecisionValue(portal_type='Organisation') is not None\
          and context.getSourceDecisionValue(portal_type='Organisation').getDefaultImageWidth() is not None\
          and context.getSourceDecisionValue(portal_type='Organisation').getDefaultImageWidth() \
              * inch_cm_ratio or '',
  'source_decision_image_height': context.getSourceDecisionValue(portal_type='Organisation') is not None\
          and context.getSourceDecisionValue(portal_type='Organisation').getDefaultImageHeight() is not None\
          and context.getSourceDecisionValue(portal_type='Organisation').getDefaultImageHeight() \
              * inch_cm_ratio or '',
  'source_decision_address':getOneLineAddress(
          context.getSourceDecision() and
              context.getSourceDecisionValue().getDefaultAddressText() or '',
          context.getSourceDecision() and \
              context.getSourceDecisionValue().getDefaultAddressRegionTitle() or ''),
  'source_decision_telfax': getPhoneAndFax(context.getSourceDecision() and
          context.getSourceDecisionValue().getTelephoneText() or '',
      context.getSourceDecision() and \
          context.getSourceDecisionValue().getFaxText() or ''),
  'source_decision_email': getEmail(context.getSourceDecision() and
      context.getSourceDecisionValue().getEmailText() or ''),
  'source_decision_vatid': getVatId(context.getSourceDecision() and\
                           getattr(context.getSourceDecisionValue(), 'getVatCode', None)\
                           is not None and\
                           context.getSourceDecisionValue().getVatCode() or ''),

  'destination_title': destination.getProperty('corporate_name') or destination.getTitle(),
  'destination_address': getOneLineAddress(
      context.getDestination() and \
          context.getDestinationValue().getDefaultAddressText() or '',
      context.getDestination() and \
          context.getDestinationValue().getDefaultAddressRegionTitle() or ''),
  'destination_telfax': getPhoneAndFax(context.getDestination() and
      context.getDestinationValue().getTelephoneText() or '',
      context.getDestination() and context.getDestinationValue().getFaxText() or ''),
  'destination_email': getEmail(context.getDestination() and \
      context.getDestinationValue().getEmailText() or ''),
  'destination_vatid': getVatId(context.getDestination() and
      context.getDestinationValue().getProperty('vat_code', '') or ''),

  'destination_section_title': destination_section.getProperty('corporate_name') or \
                                  destination_section.getTitle(),
  'destination_section_image_path': destination_section.getDefaultImagePath(),
  'destination_section_image_width': context.getDestinationSectionValue() is not None\
      and context.getDestinationSectionValue().getDefaultImageWidth() is not None\
      and context.getDestinationSectionValue().getDefaultImageWidth() * inch_cm_ratio or '',
  'destination_section_image_height': context.getDestinationSectionValue() is not None\
      and context.getDestinationSectionValue().getDefaultImageHeight() is not None\
      and context.getDestinationSectionValue().getDefaultImageHeight() * inch_cm_ratio or '',
  'destination_section_address': getOneLineAddress(
      context.getDestinationSection() and context.getDestinationSectionValue().getDefaultAddressText() or '',
      context.getDestinationSection() and context.getDestinationSectionValue().getDefaultAddressRegionTitle() or ''),
  'destination_section_telfax': getPhoneAndFax(
      context.getDestinationSection() and context.getDestinationSectionValue().getTelephoneText() or '',
      context.getDestinationSection() and context.getDestinationSectionValue().getFaxText() or ''),
  'destination_section_email': getEmail(context.getDestinationSection() and context.getDestinationSectionValue().getEmailText() or ''),
  'destination_section_vatid': getVatId(context.getDestinationSection() and
      context.getDestinationSectionValue().getProperty('vat_code') or ''),
  'destination_section_corporate_registration_codeid': getCorporateRegistrationCodeId(context.getDestinationSection() and
      context.getDestinationSectionValue().getProperty('corporate_registration_code') or ''),
  'destination_section_activity_codeid': getActivityCodeId(context.getDestinationSection() and
      context.getDestinationSectionValue().getProperty('activity_code') or ''),
  'destination_section_social_codeid': getSocialCodeId(context.getDestinationSection() and
      context.getDestinationSectionValue().getProperty('social_code') or ''),
  'destination_section_social_company_title' : social_organisation is not None and social_organisation.getTitle() or '',
  'destination_section_social_address': social_organisation is not None and getOneLineAddress(\
                                            social_organisation.getDefaultAddressText(),
                                            social_organisation.getDefaultAddressRegionTitle()) or '',
  'destination_administration_title':\
    destination_administration.getProperty('corporate_name') or \
                                destination_administration.getTitle(),
  'destination_administration_address': getOneLineAddress(
                                      destination_administration.getDefaultAddressText(),
                                      destination_administration.getDefaultAddressRegionTitle()),
  'destination_administration_telfax':
          getPhoneAndFax(destination_administration.getProperty('telephone_text', ''),
                         destination_administration.getProperty('fax_text', '')),
  'destination_administration_email':
          getEmail(destination_administration.getProperty('email_text', '')),
  'destination_administration_vatid':
          getVatId(destination_administration.getProperty('vat_code', '')),

  'reference': context.getReference() or '',
  'start_date': getOrderedDate(context.getStartDate()) or '',
  'stop_date': getOrderedDate(context.getStopDate()) or '',
  'creation_date': getOrderedDate(context.getCreationDate()) or '',
  'currency': context.getPriceCurrencyValue() is not None and context.getPriceCurrencyValue().getShortTitle() or context.getPriceCurrencyReference() or '',
  'payment_condition': getPaymentConditionText(context),
  'delivery_mode': context.getDeliveryModeTitle() or '',
  'incoterm': context.getIncoterm() and context.getIncotermValue().getCodification() or '',

  'total_price_novat': total_price,
  'description': getFieldAsLineList(context.getDescription() or ''),
  'specialise_title': context.getProperty('specialise_title',''),

  'line_list': line_list,
}

return unicodeDict(data_dict)
