from Products.ERP5Type.DateUtils import getIntervalBetweenDates, getNumberOfDayInMonth

portal = context.getPortalObject()
portal_categories = context.portal_categories

rubric_value_dict = {}

france_territory_code = ('FR' ,'GP', 'BL', 'MF', 'MQ', 'GF', 'RE', 'PM', 'YT', 'WF', 'PF', 'NC', 'MC')

def getCountryCode(target):
  region = portal_categories.getCategoryValue(target.getDefaultAddressRegion(), base_category="region")
  if region is None:
    raise ValueError("Country should be defined in address field of %s" % target.getRelativeUrl())
  codification = region.getCodification()
  if codification is None:
    raise ValueError("Region %s doesn't have codification" % region.getRelativeUrl())
  return codification

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year()) if datetime else ''
  

def formatFloat(number):
  return "{:.02f}".format(float(number))

def getLastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

def getPaymentPeriod(date, period_type):
  import math
  if period_type == 'M':
    denominator = 1
  elif period_type == 'T':
    denominator = 3
  elif period_type == 'S':
    denominator = 6
  else:
    raise ValueError('Unknown denominator type : %s' % period_type)
  return "%d%s%02d" % (date.year(), period_type, math.ceil(date.month() / denominator))

# Changements
if block_id in ('S21.G00.31', 'S21.G00.41', 'S21.G00.72'):
  change_block = kw['change_block']
  change_date = kw['change_date']
  rubric_value_dict[block_id + ".001"] = change_date
  for rubric, value in change_block.iteritems():
    rubric_value_dict[rubric] = value

# Envoi
if block_id == 'S10.G00.00':
  rubric_value_dict['S10.G00.00.001'] = 'Logiciel maison'
  rubric_value_dict['S10.G00.00.002'] = 'Logiciel maison'
  rubric_value_dict['S10.G00.00.003'] = ''
  rubric_value_dict['S10.G00.00.004'] = ''
  rubric_value_dict['S10.G00.00.005'] = '01'
  rubric_value_dict['S10.G00.00.006'] = 'P03V01'
  rubric_value_dict['S10.G00.00.007'] = '01'
  rubric_value_dict['S10.G00.00.008'] = '01'

# Emetteur
if block_id == 'S10.G00.01':
  rubric_value_dict['S10.G00.01.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[:9] #SIREN
  rubric_value_dict['S10.G00.01.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:] #NIC
  rubric_value_dict['S10.G00.01.003'] = target.getCorporateName()
  rubric_value_dict['S10.G00.01.004'] = target.getDefaultAddressStreetAddress().strip()
  rubric_value_dict['S10.G00.01.005'] = target.getDefaultAddressZipCode()
  rubric_value_dict['S10.G00.01.006'] = target.getDefaultAddressCity()
  rubric_value_dict['S10.G00.01.007'] = ''
  rubric_value_dict['S10.G00.01.008'] = ''
  rubric_value_dict['S10.G00.01.009'] = ''
  rubric_value_dict['S10.G00.01.010'] = ''

# Contact Emetteur
if block_id == 'S10.G00.02':
  social_title_code = {
    'mr': '01',
    'mrs': '02',
    'miss': '02',
    'ms': '02',
  }[target.getSocialTitleId()]
  rubric_value_dict['S10.G00.02.001'] = social_title_code
  rubric_value_dict['S10.G00.02.002'] = ' '.join((target.getLastName(), target.getFirstName()))
  rubric_value_dict['S10.G00.02.004'] = target.getDefaultEmailUrlString()
  rubric_value_dict['S10.G00.02.005'] = target.getDefaultTelephoneCoordinateText()
  rubric_value_dict['S10.G00.02.006'] = ''

# Declaration
if block_id == 'S20.G00.05':
  now = DateTime()
  rubric_value_dict['S20.G00.05.001'] = '01' # Monthly DSN
  rubric_value_dict['S20.G00.05.002'] = '01' # Normal Declaration
  rubric_value_dict['S20.G00.05.003'] = '11'
  rubric_value_dict['S20.G00.05.004'] = kw['order'] # Declaration.Ordre, incremented for each DSN
  rubric_value_dict['S20.G00.05.005'] = formatDate(DateTime(kw['year'], kw['month'], 1))
  rubric_value_dict['S20.G00.05.006'] = ''
  rubric_value_dict['S20.G00.05.007'] = formatDate(DateTime(now.year(), now.month(), now.day()))
  rubric_value_dict['S20.G00.05.008'] = '01'
  rubric_value_dict['S20.G00.05.009'] = ''
  rubric_value_dict['S20.G00.05.010'] = '01'

# Entreprise
if block_id == 'S21.G00.06':
  # Calculate the average manpower of all year, if month is December
  # XXX : should be fixed to be corrct when there exists  DSN reports for
  # different establishments or organisations, or replaced/cancelled DSN reports
  average_manpower = ''
  if context.getEffectiveDate().month() == 12:
    manpower_list = []
    report_list = portal.dsn_module.searchFolder(effective_date=str(context.getEffectiveDate().year()))
    for month_report in report_list:
      manpower_list.append(int(month_report.getQuantity()))
    average_manpower = str(sum(manpower_list) / len(manpower_list))
  rubric_value_dict['S21.G00.06.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[:9]
  rubric_value_dict['S21.G00.06.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]
  rubric_value_dict['S21.G00.06.003'] = target.getActivityCode()
  rubric_value_dict['S21.G00.06.004'] = target.getDefaultAddressStreetAddress().strip()
  rubric_value_dict['S21.G00.06.005'] = target.getDefaultAddressZipCode()
  rubric_value_dict['S21.G00.06.006'] = target.getDefaultAddressCity()
  rubric_value_dict['S21.G00.06.007'] = ''
  rubric_value_dict['S21.G00.06.008'] = ''
  rubric_value_dict['S21.G00.06.009'] = average_manpower
  rubric_value_dict['S21.G00.06.010'] = ''
  rubric_value_dict['S21.G00.06.011'] = ''

# Etablissement
elif block_id == 'S21.G00.11':
  establishment_country_code = getCountryCode(target)
  rubric_value_dict['S21.G00.11.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]
  rubric_value_dict['S21.G00.11.002'] = target.getActivityCode()
  rubric_value_dict['S21.G00.11.003'] = target.getDefaultAddressStreetAddress().strip()
  rubric_value_dict['S21.G00.11.004'] = target.getDefaultAddressZipCode()
  rubric_value_dict['S21.G00.11.005'] = target.getDefaultAddressCity()
  rubric_value_dict['S21.G00.11.006'] = ''
  rubric_value_dict['S21.G00.11.007'] = ''
  rubric_value_dict['S21.G00.11.008'] = int(context.getQuantity())
  rubric_value_dict['S21.G00.11.009'] = ''
  rubric_value_dict['S21.G00.11.015'] = (establishment_country_code if establishment_country_code not in france_territory_code else '')
  rubric_value_dict['S21.G00.11.016'] = ''
  rubric_value_dict['S21.G00.11.017'] = ''
  rubric_value_dict['S21.G00.11.018'] = ''

if block_id == 'S21.G00.15':
  # XXX: Hack as some organisations may have several contracts
    return [
    {
      'S21.G00.15.001': 'REF_CONTRACT1',
      'S21.G00.15.002': 'ORGANISATION1',
      'S21.G00.15.004': '01',
      'S21.G00.15.005': '1',
    },
    {
      'S21.G00.15.001': 'REF_CONTRACT2',
      'S21.G00.15.002': 'ORGANISATION2',
      'S21.G00.15.004': '01',
      'S21.G00.15.005': '2',
    }]

# Versement organisme de protection sociale
if block_id == 'S21.G00.20':
  payment_transaction = target
  bank_account = target.getSourcePaymentValue()
  payment_source_trade = payment_transaction.getSourceTradeValue()

  if kw['establishment'] == payment_source_trade:
    # A main establishment is paying for this one
    rubric_value_dict['S21.G00.20.005'] = formatFloat(0.)
    rubric_value_dict['S21.G00.20.010'] = '06'
    rubric_value_dict['S21.G00.20.012'] = ''.join(payment_transaction.getSourceSectionValue().getCorporateRegistrationCode().split(' '))
  elif kw['establishment'] == payment_transaction.getSourceSectionValue():
    # Establishment pays for itself
    rubric_value_dict['S21.G00.20.003'] = bank_account.getBicCode()
    rubric_value_dict['S21.G00.20.004'] = bank_account.getIban()
    rubric_value_dict['S21.G00.20.005'] = payment_transaction.AccountingTransactionLine_statSourceDebit()
    rubric_value_dict['S21.G00.20.010'] = payment_transaction.getPaymentModeValue().getCodification()
    if payment_source_trade is not None:
      # Establishment pays also for another one
      rubric_value_dict['S21.G00.20.012'] = ''.join(kw['establishment'].getCorporateRegistrationCode().split(' '))

  rubric_value_dict['S21.G00.20.001'] = kw['corporate_registration_code']
  rubric_value_dict['S21.G00.20.002'] = ''.join(kw['establishment'].getCorporateRegistrationCode().split(' ')) # TODO: Check if it is always needed
  rubric_value_dict['S21.G00.20.006'] = formatDate(payment_transaction.getStartDate()) # TODO: check simulation correctly sets it
  rubric_value_dict['S21.G00.20.007'] = formatDate(payment_transaction.getStopDate())
  rubric_value_dict['S21.G00.20.008'] = ''

# Bordereau de cotisation due
if block_id == 'S21.G00.22':
  payment_transaction = target
  rubric_value_dict['S21.G00.22.001'] = kw['corporate_registration_code']
  rubric_value_dict['S21.G00.22.002'] = ''.join(kw['establishment'].getCorporateRegistrationCode().split(' '))
  rubric_value_dict['S21.G00.22.003'] = formatDate(kw['start_date'])
  rubric_value_dict['S21.G00.22.004'] = formatDate(kw['stop_date'])
  rubric_value_dict['S21.G00.22.005'] = payment_transaction.AccountingTransactionLine_statSourceDebit()

if block_id == 'S21.G00.23':
  rubric_value_dict['S21.G00.23.001'] = target['code'][:3]
  rubric_value_dict['S21.G00.23.002'] = target['cap']
  rubric_value_dict['S21.G00.23.003'] = ('' if not target['rate'] else formatFloat(target['rate']))
  if target['quantity']:
    assert target['quantity'] > 0
    rubric_value_dict['S21.G00.23.005'] = formatFloat(target['quantity'])
  else:
    rubric_value_dict['S21.G00.23.004'] = formatFloat(target['base'])
  rubric_value_dict['S21.G00.23.006'] = target['zip_code']

# Individu
if block_id == 'S21.G00.30':
  birth_country_code = getCountryCode(target)
  address = target.getDefaultAddressStreetAddress().strip().split('\n')
  rubric_value_dict["S21.G00.30.001"] = "".join(target.getSocialCode('').split(' '))[:13]
  rubric_value_dict["S21.G00.30.002"] = target.getLastName()
  rubric_value_dict["S21.G00.30.003"] = ''
  rubric_value_dict["S21.G00.30.004"] = " ".join([target.getFirstName(), target.getMiddleName() or '']).strip()
  if target.getSocialCode() is None:
    rubric_value_dict["S21.G00.30.005"] = ('01' if target.getGender() == 'male' else '02' if target.getGender() == 'female' else '')
  rubric_value_dict["S21.G00.30.006"] = formatDate(target.getStartDate())
  rubric_value_dict["S21.G00.30.007"] = (target.getDefaultBirthplaceAddressCity() if enrollment_record.getBirthCountryCode() in france_territory_code else enrollment_record.getBirthCountryCode())
  rubric_value_dict["S21.G00.30.008"] = address[0].strip()
  rubric_value_dict["S21.G00.30.009"] = ('' if enrollment_record.getDistributionCode() is not None else target.getDefaultAddressZipCode())
  rubric_value_dict["S21.G00.30.010"] = target.getDefaultAddressCity()
  rubric_value_dict["S21.G00.30.011"] = (birth_country_code if birth_country_code not in france_territory_code else '')
  rubric_value_dict["S21.G00.30.012"] = enrollment_record.getDistributionCode() or ''
  rubric_value_dict["S21.G00.30.013"] = enrollment_record.getUeCode()
  rubric_value_dict["S21.G00.30.014"] = enrollment_record.getBirthDepartment()
  rubric_value_dict["S21.G00.30.015"] = enrollment_record.getBirthCountryCode()
  rubric_value_dict["S21.G00.30.016"] = ''
  rubric_value_dict["S21.G00.30.017"] = (' '.join(address[1:]).strip() if len(address) > 1 else '')
  rubric_value_dict["S21.G00.30.018"] = target.getDefaultEmailCoordinateText() or ''
  rubric_value_dict["S21.G00.30.019"] = ''
  rubric_value_dict["S21.G00.30.020"] = target.getCareerReference('')

# Contrat
if block_id == 'S21.G00.40':
  # target is a career
  rubric_value_dict["S21.G00.40.001"] = formatDate(enrollment_record.getCareerStartDate())
  rubric_value_dict["S21.G00.40.002"] = enrollment_record.getConventionalStatus()
  rubric_value_dict["S21.G00.40.003"] = enrollment_record.getComplementaryRetirementStatus()
  rubric_value_dict["S21.G00.40.004"] = enrollment_record.getSocioprofessionalCategory()
  rubric_value_dict["S21.G00.40.005"] = ''
  rubric_value_dict["S21.G00.40.006"] = target.getTitle()
  rubric_value_dict["S21.G00.40.007"] = enrollment_record.getContractType()
  rubric_value_dict["S21.G00.40.008"] = enrollment_record.getSpecialContractType()
  rubric_value_dict["S21.G00.40.009"] = '00000'
  rubric_value_dict["S21.G00.40.010"] = ('' if enrollment_record.getContractType() not in ('02', '29') else formatDate(enrollment_record.getCareerStopDate()))
  rubric_value_dict["S21.G00.40.011"] = enrollment_record.getWorkingUnitType()
  rubric_value_dict["S21.G00.40.012"] = formatFloat(enrollment_record.getStandardWorkingUnit())
  rubric_value_dict["S21.G00.40.013"] = formatFloat(enrollment_record.getWorkingUnitQuantity())
  rubric_value_dict["S21.G00.40.014"] = enrollment_record.getFullTimeStatus()
  rubric_value_dict["S21.G00.40.016"] = enrollment_record.getLocalScheme()
  rubric_value_dict["S21.G00.40.017"] = target.getCollectiveAgreementTitle()
  rubric_value_dict["S21.G00.40.018"] = enrollment_record.getMedicalScheme()
  rubric_value_dict["S21.G00.40.019"] = ''.join(target.getDestinationValue().getCorporateRegistrationCode().split(' '))[-5:]
  rubric_value_dict["S21.G00.40.020"] = enrollment_record.getRetirementScheme()
  rubric_value_dict["S21.G00.40.021"] = enrollment_record.getEnrollmentCausality()
  rubric_value_dict["S21.G00.40.022"] = ''
  rubric_value_dict["S21.G00.40.023"] = ''
  rubric_value_dict["S21.G00.40.024"] = enrollment_record.getExpatriateStatus()
  rubric_value_dict["S21.G00.40.025"] = ''
  rubric_value_dict["S21.G00.40.026"] = enrollment_record.getCivilServantStatus()
  rubric_value_dict["S21.G00.40.027"] = ''
  rubric_value_dict["S21.G00.40.028"] = ''
  rubric_value_dict["S21.G00.40.029"] = ''
  rubric_value_dict["S21.G00.40.030"] = ''
  rubric_value_dict["S21.G00.40.031"] = ''
  rubric_value_dict["S21.G00.40.032"] = ''
  rubric_value_dict["S21.G00.40.033"] = ''
  rubric_value_dict["S21.G00.40.035"] = ''
  rubric_value_dict["S21.G00.40.036"] = '01'
  rubric_value_dict["S21.G00.40.037"] = '01'
  rubric_value_dict["S21.G00.40.038"] = ''
  rubric_value_dict["S21.G00.40.039"] = '200'
  rubric_value_dict["S21.G00.40.040"] = enrollment_record.getOccupationalAccidentRiskCode()
  rubric_value_dict["S21.G00.40.041"] = target.getSalaryLevelTitle()
  rubric_value_dict["S21.G00.40.042"] = ''
  rubric_value_dict["S21.G00.40.043"] = formatFloat(enrollment_record.getOccupationalAccidentRiskRate())


# Versement Individu
if block_id == 'S21.G00.50':
  # target is a paysheet
  rubric_value_dict['S21.G00.50.001'] = formatDate(context.getEffectiveDate())
  rubric_value_dict['S21.G00.50.002'] = kw['net_taxable_salary']
  rubric_value_dict['S21.G00.50.003'] = ''
  rubric_value_dict['S21.G00.50.004'] = kw['net_salary']

if block_id == 'S21.G00.52':
  rubric_value_dict['S21.G00.52.001'] = target['code']
  rubric_value_dict['S21.G00.52.002'] = formatFloat(target['quantity'])
  rubric_value_dict['S21.G00.52.003'] = formatDate(target['start_date'])
  rubric_value_dict['S21.G00.52.004'] = formatDate(target['stop_date'])
  rubric_value_dict['S21.G00.52.006'] = '00000'
  rubric_value_dict['S21.G00.52.007'] = ''

if block_id == 'S21.G00.54':
  rubric_value_dict['S21.G00.54.001'] = target['code']
  rubric_value_dict['S21.G00.54.002'] = formatFloat(target['quantity'])
  rubric_value_dict['S21.G00.54.003'] = formatDate(target['start_date'])
  rubric_value_dict['S21.G00.54.004'] = formatDate(target['stop_date'])

# Payment component
if block_id == 'S21.G00.55':
  # target is a payment transaction
    # target is a payment transaction
  corporate_registration_code = target.getDestinationSectionValue().getCorporateRegistrationCode()
  if corporate_registration_code not in ('ORGANISATION1', 'ORGANISATION2'):
    return {}
  payment_source_trade = target.getSourceTradeValue()
  if kw['establishment'] == payment_source_trade:
    rubric_value_dict['S21.G00.55.001'] = formatFloat(0.)
  elif kw['establishment'] == target.getSourceSectionValue():
    rubric_value_dict['S21.G00.55.001'] = target.AccountingTransactionLine_statSourceDebit()

  rubric_value_dict['S21.G00.55.002'] = ''
  rubric_value_dict['S21.G00.55.003'] = 'REF_CONTRACT' + corporate_registration_code[-1]
  rubric_value_dict['S21.G00.55.004'] = getPaymentPeriod(target.getStopDate(), 'M')

# Fin du contrat
if block_id == 'S21.G00.62':
  rubric_value_dict['S21.G00.62.001'] = formatDate(enrollment_record.getCareerStopDate())
  if enrollment_record.getContractType() == '29':
    rubric_value_dict['S21.G00.62.002'] = '999'
  # TODO : currently only works for end of training periods
  rubric_value_dict['S21.G00.62.003'] = ''
  rubric_value_dict['S21.G00.62.004'] = ''
  rubric_value_dict['S21.G00.62.005'] = ''
  rubric_value_dict['S21.G00.62.006'] = ''
  rubric_value_dict['S21.G00.62.007'] = ''
  rubric_value_dict['S21.G00.62.008'] = ''
  rubric_value_dict['S21.G00.62.009'] = ''
  rubric_value_dict['S21.G00.62.010'] = ''
  rubric_value_dict['S21.G00.62.011'] = ''
  rubric_value_dict['S21.G00.62.012'] = ''
  rubric_value_dict['S21.G00.62.013'] = ''
  rubric_value_dict['S21.G00.62.014'] = ''

# Autre suspension du contrat
if block_id == 'S21.G00.65':
  # TODO
  rubric_value_dict['S21.G00.65.001'] = ''
  rubric_value_dict['S21.G00.65.002'] = ''
  rubric_value_dict['S21.G00.65.003'] = ''

# Affiliation Prevoyance
if block_id == 'S21.G00.70':
  # XXX: Hack as some organisations may have several contracts
  return [
    {
      'S21.G00.70.004': 'Option1',
      'S21.G00.70.005': '',
      'S21.G00.70.012': '1',
      'S21.G00.70.013': '1',
    },
    {
      'S21.G00.70.004': 'Option2',
      'S21.G00.70.005': '1',
      'S21.G00.70.012': '2',
      'S21.G00.70.013': '2',
    }]

# Retraite complementaire
if block_id == 'S21.G00.71':
  # Hard-coded because we only have 1 time this bloc for each person.
  # '90000' value has to be provided for trainees
  if enrollment_record.getContractType() == '29':
    code = '90000'
  elif enrollment_record.getComplementaryRetirementStatus() == '04':
    code = 'RETA'
  elif enrollment_record.getComplementaryRetirementStatus() == '01':
    code = 'RETC'
  rubric_value_dict['S21.G00.71.002'] = code

if block_id == 'S21.G00.78':
  rubric_value_dict['S21.G00.78.001'] = target['code']
  rubric_value_dict['S21.G00.78.002'] = formatDate(target['start_date'])
  rubric_value_dict['S21.G00.78.003'] = formatDate(target['stop_date'])
  if target['code'] in ('31',):
    rubric_value_dict['S21.G00.78.004'] = '0.00'
  else:
    rubric_value_dict['S21.G00.78.004'] = formatFloat(round(target['base'], 2))
  rubric_value_dict['S21.G00.78.005'] = target['contract_id']

if block_id == 'S21.G00.79':
  rubric_value_dict['S21.G00.79.001'] = target['code']
  rubric_value_dict['S21.G00.79.004'] = formatFloat(target['base'])

if block_id == 'S21.G00.81':
  rubric_value_dict['S21.G00.81.001'] = target['code']
  rubric_value_dict['S21.G00.81.002'] = (target['corporate_registration_code'] if target['code'] not in ('059', '063', '064') else '')
  rubric_value_dict['S21.G00.81.003'] = (formatFloat(target['base']) if target['base'] else '')
  rubric_value_dict['S21.G00.81.004'] = (formatFloat(target['quantity']) if target['quantity'] else '')
  rubric_value_dict['S21.G00.81.005'] = target['zip_code']

if block_id == 'S21.G00.86':
  career_start_date = enrollment_record.getCareerStartDate()
  seniority = getIntervalBetweenDates(career_start_date, DateTime())
  if seniority['year'] != 0:
    rubric_value_dict['S21.G00.86.002'] = '03'
    rubric_value_dict['S21.G00.86.003'] = seniority['year']
  elif seniority['month'] != 0:
    rubric_value_dict['S21.G00.86.002'] = '02'
    rubric_value_dict['S21.G00.86.003'] = seniority['month']
  elif seniority['day'] != 0:
    rubric_value_dict['S21.G00.86.002'] = '01'
    rubric_value_dict['S21.G00.86.003'] = seniority['day']
  rubric_value_dict['S21.G00.86.001'] = '01'
  rubric_value_dict['S21.G00.86.005'] = '00000'

if block_id == 'S90.G00.90':
  rubric_value_dict['S90.G00.90.001'] = int(kw['length']) + 2
  rubric_value_dict['S90.G00.90.002'] = kw['dsn_record_counter']
  
return rubric_value_dict
