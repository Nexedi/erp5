# coding: utf-8
import six
portal = context.getPortalObject()
translateString = portal.Base_translateString
request = context.REQUEST

tax_use_list = portal.portal_preferences.getPreferredTaxUseList() or ["use/trade/tax"]

# display only title line instead of description
use_line_title =  request.get('use_line_title', 0)

def getFieldAsString(field):
  return ', '.join(getFieldAsLineList(field))

def getFieldAsLineList(field):
  """Returns the text as a list of lines."""
  field = field or ''
  text = field.replace('\r', '')
  text_list = text.split('\n')
  return [x for x in text_list if x]

def getProductAndLineDesc(prod_desc, line_desc):
  line_list = []
  if line_desc:
    line_list.extend(getFieldAsLineList(line_desc))
  elif prod_desc:
    line_list.extend(getFieldAsLineList(prod_desc))
  return line_list

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

def getCorporateRegCode(reg_code):
  s = ''
  if reg_code:
    s += '%s: %s' % (translateString('Corporate Registration Code'), reg_code)
  return s

def getSocialCapital(reg_cap):
  s = ''
  if reg_cap:
    s += '%s: %s€' % (translateString('Social Capital'), reg_cap)
  return s

preferred_date_order = portal.portal_preferences.getPreferredDateOrder() or 'ymd'
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
  if 'custom' == order.getPaymentConditionTradeDate():
    return getOrderedDate(order.getPaymentConditionPaymentDate())
  end_of_month = order.getPaymentConditionPaymentEndOfMonth()
  days = order.getPaymentConditionPaymentTerm()
  if days:
    if end_of_month:
      return translateString("${days} Days End of Month", mapping=dict(days=days))
    return translateString("${days} Days", mapping=dict(days=days))
  elif end_of_month:
    return translateString("End of Month")
  return getOrderedDate(order.getStartDate())

def getTaxLineList(order):
  tax_line_list = [line for line in
       order.contentValues(portal_type=order.getPortalTaxMovementTypeList())
       if line.getTotalPrice()]
  for line in order.Base_getSpecialisedAggregatedAmountList():
    if any(line.isMemberOf(tax_use) for tax_use in tax_use_list):
      tax_line_list.append(line)
  tax_line_list.sort(key=lambda line:line.getTitle())
  return tax_line_list

line_base_contribution_list = []
tax_free_line_totalprice = 0
line_list = []
line_not_tax = []
line_tax = []
line_tax_no_rate = {}
total_price = 0.0
total_tax_price = 0.0
number_line_not_tax = 0

def unicodeDict(d):
  if six.PY3:
    return d
  for k, v in six.iteritems(d):
    if isinstance(v, str):
      d.update({k: unicode(v, 'utf8')})  # pylint:disable=undefined-variable
  return d


for line in getSubLineList(context):
  prod_desc = line.getResource() is not None and \
           getFieldAsString(line.getResourceValue().getDescription()) or (
    request.get('international_form') and line.getResourceTitle() or line.getResourceTranslatedTitle() )
  if use_line_title:
    desc = (line.getTitle(), )
  else:
    desc = getProductAndLineDesc(prod_desc, line.getDescription())
  if getattr(line, 'hasLineContent', None) is not None\
        and line.hasLineContent()\
        or getattr(line, 'hasCellContent', None) is not None\
        and line.hasCellContent():
    # summary
    line_dict = {
      'style_name': 'Item_20_Table_20_Title',
      'left_style_name': 'Item_20_Table_20_Title_20_Left',
      'right_style_name': 'Item_20_Table_20_Title_20_Right',
      'index': line.getReference() or line.getIntIndex(),
      'source_reference': getSourceReference(line),
      'reference': line.getResource() is not None\
                      and line.getResourceValue().getReference() or '',
      'description': desc,
      'total_quantity': '',
      'quantity_unit': '',
      'stop_date': '',
      'base_price': '',
      'total_price': '',
      'specialise_title': '',
    }
  else:
    if line.getPortalType().endswith('Cell'):
      display_id = 'translated_title'
      if request.get('international_form'):
        display_id = 'title'
      variation_description = ', '.join([x[0] for x in line.getVariationCategoryItemList(display_id=display_id)])
      desc = ('%s %s' % (desc[0], variation_description), )
    is_tax = any(line.isMemberOf(tax_use) for tax_use in tax_use_list)

    #set the not_tax_line with the tax_number and the tax_line with the tax_name
    tax_number=''
    tax_name=''
    if not is_tax:
      if line.getBaseContributionList()==[]:
        tax_number='0'
      else:
        for contribution in line.getBaseContributionList():
          if contribution not in line_base_contribution_list:
            line_base_contribution_list.append(contribution)
          if tax_number=='':
            tax_number=str(line_base_contribution_list.index(contribution)+1)
          else:
            tax_number=tax_number+','+str(line_base_contribution_list.index(contribution)+1)
    else:
      tax_name=line.getBaseApplication()
    line_dict = {
      'style_name': 'Table_20_Contents',
      'left_style_name': 'Table_20_Contents_20_Left',
      'right_style_name': 'Table_20_Contents_20_Right',
      'index': line.getReference() or line.getIntIndex(),
      'source_reference': getSourceReference(line),
      'reference': line.getResource() is not None\
                      and line.getResourceValue().getReference() or '',
      'description': desc,
      'base_contribution':line.getBaseContribution() or None,
      'use_type':line.getResourceValue().getUse() or '',
      'use_type_tax':is_tax,
      'total_quantity': line.getTotalQuantity() or '',
      'tax_name':tax_name or '',
      'tax_number':tax_number or '',
      'quantity_unit': line.getQuantityUnitTranslatedTitle() or (
        line.getResource() and line.getResourceValue().getQuantityUnitTranslatedTitle()) or '',
      'stop_date': getOrderedDate(line.getStopDate()) or '',
      'base_price': line.getPrice() or '',
      'total_price': line.getTotalPrice() or 0,
      'specialise_title' : line.getProperty('specialise_title', ''),
    }

    if line_dict['use_type_tax']:
      if line.getQuantity():
        total_tax_price+=line.getTotalPrice() or 0.0
        line_tax.append(unicodeDict(line_dict.copy()))
    else:
      number_line_not_tax = number_line_not_tax+1
      line_dict['number_not_tax_line'] = number_line_not_tax
      total_price += line.getTotalPrice() or 0.0
      line_not_tax.append(unicodeDict(line_dict.copy()))
      #if one line of product hasn't tax, the tax table need to add a taxrate=0 line
      if line_dict['base_contribution'] is None:
        tax_free_line_totalprice = tax_free_line_totalprice + line_dict['total_price']
        line_tax_no_rate = {
            'tax_name': None ,
            'total_quantity': tax_free_line_totalprice,
            'base_price':  0.00 ,
            'total_price': 0.00 ,
        }
  line_list.append(unicodeDict(line_dict.copy()))
if line_tax_no_rate != {} :
  line_tax.append(unicodeDict(line_tax_no_rate.copy()))
for line_each in line_tax:
  if line_each['tax_name'] in line_base_contribution_list :
    number_tax_line=line_base_contribution_list.index(line_each['tax_name'])+1
  else:
    number_tax_line=0
  line_each.update({'number_tax_line': number_tax_line})
line_tax.sort(key=lambda obj:obj.get('number_tax_line'))

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
  def getTelephoneText(self):
    return ''
  def getFaxText(self):
    return ''
  def getEmailText(self):
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

source_decision = context.getSourceDecisionValue()
if source_decision is None:
  source_decision = EmptyOrganisation()

destination_decision = context.getDestinationDecisionValue()
if destination_decision is None:
  destination_decision = EmptyOrganisation()

if context.getPortalType() in portal.getPortalOrderTypeList():
  report_title = context.getSimulationState() == "draft" and "Draft Order" or "Order"
else:
  report_title = context.getSimulationState() == "draft" and "Draft Packing List" or "Packing List"

data_dict = {
  'report_title' : report_title,
  'source_section_title': source_section.getProperty('corporate_name') or\
                            source_section.getTitle(),
  'source_section_image_path': source_section.getDefaultImagePath() or '',
  'source_section_image_width': source_section.getDefaultImageWidth() is not None\
          and source_section.getDefaultImageWidth() \
              * inch_cm_ratio or '',
  'source_section_image_height': source_section.getDefaultImageHeight() is not None\
          and source_section.getDefaultImageHeight() \
              * inch_cm_ratio or '',
  'source_section_address': getOneLineAddress(
          source_section.getDefaultAddressText() or '',
          source_section.getDefaultAddressRegionTitle() or ''),
  'source_section_telfax': getPhoneAndFax(source_section.getTelephoneText() or '',
          source_section.getFaxText() or ''),
  'source_section_email': getEmail(source_section.getEmailText() or ''),
  'source_section_vatid': getVatId(getattr(source_section, 'getVatCode', None)\
                           is not None and\
                           source_section.getVatCode() or ''),
  'source_section_corporateregcode': getCorporateRegCode(getattr(source_section, 'getCorporateRegistrationCode', None)\
                           is not None and\
                           source_section.getCorporateRegistrationCode() or ''),
  'source_section_registeredcapital': getSocialCapital(getattr(source_section, 'getSocialCapital', None)\
                           is not None and\
                           source_section.getSocialCapital() or ''),

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
  'source_administration_registeredcapital':
          getSocialCapital(source_administration.getProperty('social_capital', '')),
  'source_administration_corporateregcode':
          getCorporateRegCode(source_administration.getProperty('corporate_registration_code', '')),

  'source_title': source.getProperty('corporate_name') or source.getTitle(),
  'source_address': getOneLineAddress(
          source.getDefaultAddressText() or '',
          source.getDefaultAddressRegionTitle() or ''),
  'source_telfax': getPhoneAndFax(source.getTelephoneText() or '',
          source.getFaxText() or ''),
  'source_email': getEmail(source.getEmailText() or ''),
  'source_vatid': getVatId(source.getProperty('vat_code', '') or ''),

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
          source_decision is not None and
              source_decision.getDefaultAddressText() or '',
          source_decision is not None and \
              source_decision.getDefaultAddressRegionTitle() or ''),
  'source_decision_telfax': getPhoneAndFax(source_decision is not None and
          source_decision.getTelephoneText() or '',
      source_decision is not None and \
          source_decision.getFaxText() or ''),
  'source_decision_email': getEmail(source_decision is not None and
      source_decision.getEmailText() or ''),
  'source_decision_vatid': getVatId(source_decision is not None and\
                           getattr(source_decision, 'getVatCode', None)\
                           is not None and\
                           source_decision.getVatCode() or ''),

  'destination_title': destination.getProperty('corporate_name') or destination.getTitle(),
  'destination_address': getOneLineAddress(
      destination.getDefaultAddressText() or '',
      destination.getDefaultAddressRegionTitle() or ''),
  'destination_telfax': getPhoneAndFax(destination.getTelephoneText() or '',
      destination.getFaxText() or ''),
  'destination_email': getEmail(destination.getEmailText() or ''),
  'destination_vatid': getVatId(destination.getProperty('vat_code', '') or ''),

  'destination_section_title': destination_section.getProperty('corporate_name') or \
                                  destination_section.getTitle(),
  'destination_section_image_path': destination_section.getDefaultImagePath(),
  'destination_section_image_width': destination_section.getDefaultImageWidth() is not None\
      and destination_section.getDefaultImageWidth() * inch_cm_ratio or '',
  'destination_section_image_height': destination_section.getDefaultImageHeight() is not None\
      and destination_section.getDefaultImageHeight() * inch_cm_ratio or '',
  'destination_section_address': getOneLineAddress(
      destination_section.getDefaultAddressText() or '',
      destination_section.getDefaultAddressRegionTitle() or ''),
  'destination_section_telfax': getPhoneAndFax(
      destination_section.getTelephoneText() or '',
      destination_section.getFaxText() or ''),
  'destination_section_email': getEmail(destination_section.getEmailText() or ''),
  'destination_section_vatid': getVatId(getattr(destination_section, 'getVatCode', None)\
                           is not None and\
                           destination_section.getVatCode() or ''),

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
  'destination_administration_registeredcapital':
          getSocialCapital(destination_administration.getProperty('social_capital', '')),
  'destination_administration_corporateregcode':
          getCorporateRegCode(destination_administration.getProperty('corporate_registration_code', '')),

  'destination_decision_title': context.getDestinationDecisionTitle() or '',
  'destination_decision_telfax': getPhoneAndFax(destination_decision.getTelephoneText() or '',
      destination_decision.getFaxText() or ''),
  'destination_decision_email': getEmail(destination_decision.getEmailText() or ''),

  'reference': context.getReference() or '',
  'start_date': getOrderedDate(context.getStartDate()) or '',
  'stop_date': getOrderedDate(context.getStopDate()) or '',
  'creation_date': getOrderedDate(context.getCreationDate()) or '',
  'currency': context.getPriceCurrencyReference() or '',
  'payment_condition': getPaymentConditionText(context),
  'delivery_mode': context.getDeliveryModeTranslatedTitle() or '',
  'incoterm': context.getIncoterm() and context.getIncotermValue().getCodification() or '',
  'total_price':total_price+total_tax_price,
  'total_price_exclude_tax': total_price,
  'total_tax_price':total_tax_price,
  'total_price_novat': total_price, # BBB
  'vat_list': getTaxLineList(context), # BBB
  'vat_total_price':total_tax_price, # BBB
  'description': getFieldAsLineList(context.getDescription()),
  'specialise_title': context.getProperty('specialise_title',''),
  'line_tax':line_tax,
  'line_not_tax':line_not_tax,
  'line_list': line_list,
}

return unicodeDict(data_dict)
