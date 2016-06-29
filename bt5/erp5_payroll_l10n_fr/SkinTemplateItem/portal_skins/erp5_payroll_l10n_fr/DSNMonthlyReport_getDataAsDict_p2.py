from Products.ERP5Type.DateUtils import getNumberOfDayInMonth

portal = context.getPortalObject()

rubric_value_dict = {}

france_territory_code = ('FR' ,'GP', 'BL', 'MF', 'MQ', 'GF', 'RE', 'PM', 'YT', 'WF', 'PF', 'NC', 'MC')

context.Localizer.translationContext('fr')

def getCountryCode(country_name):
  # Careful with utf-8 chars
  country_list = str(context.countriesList.data).split('\n')
  for country in country_list:
    country_record = country.split(';')
    if country_name.upper() == country_record[1].strip():
      return country_record[0]

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def formatFloat(number):
  return "{:.02f}".format(float(number))
  
def LastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

# Changements
if block_id in ('S21.G00.31', 'S21.G00.41', 'S21.G00.72'):
  change_bloc = kw['change_bloc']
  change_date = kw['change_date']
  rubric_value_dict[block_id + ".001"] = change_date
  for rubric, value in change_bloc.iteritems():
    rubric_value_dict[rubric] = value

# Envoi
if block_id == 'S10.G00.00':
  rubric_value_dict['S10.G00.00.001'] = 'Logiciel maison'
  rubric_value_dict['S10.G00.00.002'] = 'Logiciel maison'
  rubric_value_dict['S10.G00.00.003'] = ''
  rubric_value_dict['S10.G00.00.004'] = ''
  rubric_value_dict['S10.G00.00.005'] = context.getFormat()
  rubric_value_dict['S10.G00.00.006'] = 'P02V01'
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
  rubric_value_dict['S10.G00.02.001'] = '01'
  rubric_value_dict['S10.G00.02.002'] = ' '.join((target.getLastName(), target.getFirstName()))
  rubric_value_dict['S10.G00.02.003'] = '02'
  rubric_value_dict['S10.G00.02.004'] = target.getDefaultEmailUrlString()
  rubric_value_dict['S10.G00.02.005'] = target.getDefaultTelephoneCoordinateText()
  rubric_value_dict['S10.G00.02.006'] = ''

# Destinataire CRE (compte rendu d'exploitation)
if block_id == 'S10.G00.03':
  rubric_value_dict['S10.G00.03.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[:9]
  rubric_value_dict['S10.G00.03.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]
  rubric_value_dict['S10.G00.03.003'] = target.getDefaultEmailUrlString()

# Declaration
if block_id == 'S20.G00.05':
  now = DateTime()
  rubric_value_dict['S20.G00.05.001'] = '01' # Monthly DSN
  rubric_value_dict['S20.G00.05.002'] = '01'
  rubric_value_dict['S20.G00.05.003'] = '11'
  rubric_value_dict['S20.G00.05.004'] = kw['order'] # Declaration.Ordre, incremented for each DSN
  rubric_value_dict['S20.G00.05.005'] = formatDate(DateTime(kw['year'], kw['month'], 1))
  rubric_value_dict['S20.G00.05.006'] = ''
  rubric_value_dict['S20.G00.05.007'] = formatDate(DateTime(now.year(), now.month(), now.day()))
  rubric_value_dict['S20.G00.05.008'] = '01'
  rubric_value_dict['S20.G00.05.009'] = ''

# Entreprise
if block_id == 'S21.G00.06':
  # Calculate the average manpower of all year, if month is December
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
  establishment_country_code = getCountryCode(target.getDefaultAddress().getRegionTranslatedTitle())
  rubric_value_dict['S21.G00.11.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]
  rubric_value_dict['S21.G00.11.002'] = target.getActivityCode()
  rubric_value_dict['S21.G00.11.003'] = target.getDefaultAddressStreetAddress().strip()
  rubric_value_dict['S21.G00.11.004'] = target.getDefaultAddressZipCode()
  rubric_value_dict['S21.G00.11.005'] = target.getDefaultAddressCity()
  rubric_value_dict['S21.G00.11.006'] = ''
  rubric_value_dict['S21.G00.11.007'] = ''
  rubric_value_dict['S21.G00.11.008'] = int(context.getQuantity())
  rubric_value_dict['S21.G00.11.009'] = ''
  rubric_value_dict['S21.G00.11.012'] = ''
  rubric_value_dict['S21.G00.11.015'] = (establishment_country_code if establishment_country_code not in france_territory_code else '')
  rubric_value_dict['S21.G00.11.016'] = ''
  rubric_value_dict['S21.G00.11.017'] = ''

# Adhesion prevoyance sans personnel couvert
if block_id == 'S21.G00.15':
  rubric_value_dict['S21.G00.15.001'] = ''
  rubric_value_dict['S21.G00.15.002'] = ''
  rubric_value_dict['S21.G00.15.003'] = ''

# Versement organisme de protection sociale
if block_id == 'S21.G00.20':
  bank_account = context.getSourceFundingValue()
  rubric_value_dict['S21.G00.20.001'] = ''
  rubric_value_dict['S21.G00.20.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))
  rubric_value_dict['S21.G00.20.003'] = bank_account.getBicCode()
  rubric_value_dict['S21.G00.20.004'] = bank_account.getIban()
  rubric_value_dict['S21.G00.20.005'] = ''
  rubric_value_dict['S21.G00.20.006'] = formatDate(DateTime(kw['year'], kw['month'], 1))
  rubric_value_dict['S21.G00.20.007'] = formatDate(LastDateOfMonth(DateTime(kw['year'], kw['month'])))

# Bordereau de cotisation due
if block_id == 'S21.G00.22':
  rubric_value_dict['S21.G00.22.001'] = ''
  rubric_value_dict['S21.G00.22.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))
  rubric_value_dict['S21.G00.22.003'] = formatDate(DateTime(kw['year'], kw['month'], 1))
  rubric_value_dict['S21.G00.22.004'] = formatDate(LastDateOfMonth(DateTime(kw['year'], kw['month'])))
  rubric_value_dict['S21.G00.22.005'] = '' # Sum of all contributions for the social services organisation

# Individu
if block_id == 'S21.G00.30':
  birth_country_code = getCountryCode(target.getDefaultAddress().getRegionTranslatedTitle())
  address = target.getDefaultAddressStreetAddress().strip().split('\n')
  rubric_value_dict["S21.G00.30.001"] = "".join(target.getSocialCode('').split(' '))[:13]
  rubric_value_dict["S21.G00.30.002"] = target.getLastName()
  rubric_value_dict["S21.G00.30.003"] = ''
  rubric_value_dict["S21.G00.30.004"] = " ".join([target.getFirstName(), target.getMiddleName() or '']).strip()
  rubric_value_dict["S21.G00.30.005"] = ''
  rubric_value_dict["S21.G00.30.006"] = formatDate(target.getStartDate())
  rubric_value_dict["S21.G00.30.007"] = (target.getDefaultBirthplaceAddressCity() if enrollment_item.getBirthCountryCode() in france_territory_code else enrollment_item.getBirthCountryCode())
  rubric_value_dict["S21.G00.30.008"] = address[0].strip()
  rubric_value_dict["S21.G00.30.009"] = target.getDefaultAddressZipCode()
  rubric_value_dict["S21.G00.30.010"] = target.getDefaultAddressCity()
  rubric_value_dict["S21.G00.30.011"] = (birth_country_code if birth_country_code not in france_territory_code else '')
  rubric_value_dict["S21.G00.30.012"] = enrollment_item.getDistributionCode() or ''
  rubric_value_dict["S21.G00.30.013"] = enrollment_item.getUeCode()
  rubric_value_dict["S21.G00.30.014"] = enrollment_item.getBirthDepartment()
  rubric_value_dict["S21.G00.30.015"] = enrollment_item.getBirthCountryCode()
  rubric_value_dict["S21.G00.30.016"] = ''
  rubric_value_dict["S21.G00.30.017"] = (' '.join(address[1:]).strip() if len(address) > 1 else '')
  rubric_value_dict["S21.G00.30.018"] = target.getDefaultEmailCoordinateText() or ''
  rubric_value_dict["S21.G00.30.019"] = ''
  rubric_value_dict["S21.G00.30.020"] = target.getCareerReference('')

# Contrat
if block_id == 'S21.G00.40':
  # target is a career
  rubric_value_dict["S21.G00.40.001"] = formatDate(enrollment_item.getCareerStartDate())
  rubric_value_dict["S21.G00.40.002"] = enrollment_item.getConventionalStatus()
  rubric_value_dict["S21.G00.40.003"] = enrollment_item.getComplementaryRetirementStatus()
  rubric_value_dict["S21.G00.40.004"] = enrollment_item.getSocioprofessionalCategory()
  rubric_value_dict["S21.G00.40.005"] = ''
  rubric_value_dict["S21.G00.40.006"] = target.getTitle()
  rubric_value_dict["S21.G00.40.007"] = enrollment_item.getContractType()
  rubric_value_dict["S21.G00.40.008"] = enrollment_item.getSpecialContractType()
  rubric_value_dict["S21.G00.40.009"] = '00000'
  rubric_value_dict["S21.G00.40.010"] = ('' if enrollment_item.getContractType() != '29' else formatDate(enrollment_item.getCareerStopDate()))
  rubric_value_dict["S21.G00.40.011"] = enrollment_item.getWorkingUnitType()
  rubric_value_dict["S21.G00.40.012"] = formatFloat(enrollment_item.getStandardWorkingUnit())
  rubric_value_dict["S21.G00.40.013"] = formatFloat(enrollment_item.getWorkingUnitQuantity())
  rubric_value_dict["S21.G00.40.014"] = enrollment_item.getFullTimeStatus()
  rubric_value_dict["S21.G00.40.015"] = formatFloat(enrollment_item.getWageMeasure())
  rubric_value_dict["S21.G00.40.016"] = enrollment_item.getLocalScheme()
  rubric_value_dict["S21.G00.40.017"] = target.getCollectiveAgreementTitle()
  rubric_value_dict["S21.G00.40.018"] = enrollment_item.getMedicalScheme()
  rubric_value_dict["S21.G00.40.019"] = '' 
  rubric_value_dict["S21.G00.40.020"] = enrollment_item.getRetirementScheme()
  rubric_value_dict["S21.G00.40.021"] = ''
  rubric_value_dict["S21.G00.40.022"] = ''
  rubric_value_dict["S21.G00.40.023"] = ''
  rubric_value_dict["S21.G00.40.024"] = enrollment_item.getExpatriateStatus()
  rubric_value_dict["S21.G00.40.025"] = ''
  rubric_value_dict["S21.G00.40.026"] = enrollment_item.getCivilServantStatus()
  rubric_value_dict["S21.G00.40.027"] = ''
  rubric_value_dict["S21.G00.40.028"] = ''
  rubric_value_dict["S21.G00.40.029"] = ''
  rubric_value_dict["S21.G00.40.030"] = ''
  rubric_value_dict["S21.G00.40.031"] = ''
  rubric_value_dict["S21.G00.40.032"] = ''
  rubric_value_dict["S21.G00.40.033"] = ''

# Versement Individu
if block_id == 'S21.G00.50':
  # target is a paysheet
  rubric_value_dict['S21.G00.50.001'] = formatDate(context.getEffectiveDate())
  rubric_value_dict['S21.G00.50.002'] = formatFloat(target.PaySheetTransaction_getOtherInformationsDataDict()["salaire_net_imposable_float"])
  rubric_value_dict['S21.G00.50.003'] = ''
  rubric_value_dict['S21.G00.50.004'] = formatFloat(target.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution='base_contribution/base_amount/payroll/report/salary/net', contribution_share='contribution_share/employee'))

# Prime
if block_id == 'S21.G00.52':
  # target is a paysheet
  rubric_value_dict['S21.G00.52.001'] = ''
  rubric_value_dict['S21.G00.52.002'] = ''
  rubric_value_dict['S21.G00.52.003'] = formatDate(target.getStartDate())
  rubric_value_dict['S21.G00.52.004'] = formatDate(target.getStopDate())
  rubric_value_dict['S21.G00.52.005'] = '' # follow to default assignment and getStartDate
  rubric_value_dict['S21.G00.52.006'] = '00000'

# Fin du contrat
if block_id == 'S21.G00.62':
  rubric_value_dict['S21.G00.62.001'] = formatDate(enrollment_item.getCareerStopDate())
  if enrollment_item.getContractType() == '29':
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
  # Hard-coded because we only have 1 time this bloc
  # for each person. And data is always the same
  # 006 only when just hired. 005 not mandatory
  if enrollment_item.getContractType() == '29':
    return rubric_value_dict
  start_date = enrollment_item.getCareerStartDate()
  if start_date.year() == context.getEffectiveDate().year() \
      and start_date.month() == context.getEffectiveDate().month():
        just_hired = True
  else:
    just_hired = False
  rubric_value_dict['S21.G00.70.001'] = '168119'
  rubric_value_dict['S21.G00.70.002'] = 'AGEN01'
  rubric_value_dict['S21.G00.70.003'] = ''
  rubric_value_dict['S21.G00.70.004'] = 'CAD01_1'
  rubric_value_dict['S21.G00.70.005'] = ''
  rubric_value_dict['S21.G00.70.006'] = (formatDate(start_date) if just_hired else '')

# Retraite complementaire
if block_id == 'S21.G00.71':
  # Hard-coded because we only have 1 time this bloc for each person.
  # '90000' value has to be provided for trainees
  rubric_value_dict['S21.G00.71.002'] = ('G081' if enrollment_item.getContractType() != '29' else '90000')

if block_id == 'S21.G00.78':
  rubric_value_dict['S21.G00.78.001'] = kw['base_code']
  rubric_value_dict['S21.G00.78.002'] = formatDate(target.getStartDate())
  rubric_value_dict['S21.G00.78.003'] = formatDate(target.getStopDate())
  rubric_value_dict['S21.G00.78.004'] = formatFloat(round(kw['amount'], 2))

if block_id == 'S21.G00.79':
  rubric_value_dict['S21.G00.79.001'] = kw['base_code']
  rubric_value_dict['S21.G00.79.002'] = ''
  rubric_value_dict['S21.G00.79.003'] = ''
  rubric_value_dict['S21.G00.79.004'] = formatFloat(kw['base'])

if block_id == 'S21.G00.81':
  rubric_value_dict['S21.G00.81.001'] = kw['base_code']
  rubric_value_dict['S21.G00.81.002'] = kw['social_entity']
  rubric_value_dict['S21.G00.81.003'] = formatFloat(kw['base'])
  rubric_value_dict['S21.G00.81.004'] = kw.get('amount', '')
  rubric_value_dict['S21.G00.81.005'] = kw.get('insee_code', '')

if block_id == 'S90.G00.90':
  rubric_value_dict['S90.G00.90.001'] = int(kw['length']) + 2
  rubric_value_dict['S90.G00.90.002'] = kw['dsn_record_counter']
  
return rubric_value_dict
