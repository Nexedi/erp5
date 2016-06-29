portal = context.getPortalObject()

rubrics_values = {}

france_territory_code = ('FR' ,'GP', 'BL', 'MF', 'MQ', 'GF', 'RE', 'PM', 'YT', 'WF', 'PF', 'NC', 'MC')

context.Localizer.translationContext('fr')

def getCountryCode(country_name):
  # Careful with utf-8 chars
  countries = str(context.countriesList.data).split('\n')
  for country in countries:
    country_record = country.split(';')
    if country_name.upper() == country_record[1].strip():
      return country_record[0]

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def formatFloat(number):
  return "{:.2f}".format(float(number))
  
def LastDateOfMonth(year, month):
  if month == 12:
    return DateTime(year, 12, 31)
  else :
    next_month = DateTime(year, month+1, 1)
    return next_month - 1

# Bloc Declaration
if block_id == 'S20.G00.05':
  now = DateTime()
  rubrics_values['S20.G00.05.001'] = kw['dsn_type']
  rubrics_values['S20.G00.05.002'] = '01'
  rubrics_values['S20.G00.05.003'] = '11'
  rubrics_values['S20.G00.05.004'] = '1' # TODO : to increment for each new event DSN
  rubrics_values['S20.G00.05.006'] = ''
  rubrics_values['S20.G00.05.007'] = formatDate(DateTime(now.year(), now.month(), now.day()))
  rubrics_values['S20.G00.05.009'] = ''

if block_id == 'S20.G00.07':
  rubrics_values['S20.G00.07.001'] = ' '.join((target.getLastName(), target.getFirstName()))
  rubrics_values['S20.G00.07.002'] = target.getDefaultTelephoneCoordinateText()
  rubrics_values['S20.G00.07.003'] = target.getDefaultEmailUrlString()
  rubrics_values['S20.G00.07.004'] = '09'

# Entreprise
if block_id == 'S21.G00.06':
  rubrics_values['S21.G00.06.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[:9]
  rubrics_values['S21.G00.06.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]

# Etablissement
elif block_id == 'S21.G00.11':
  establishment_country_code = getCountryCode(target.getDefaultAddress().getRegionTranslatedTitle())
  rubrics_values['S21.G00.11.001'] = target.getCorporateRegistrationCode()[-5:]
  rubrics_values['S21.G00.11.003'] = target.getDefaultAddressStreetAddress()
  rubrics_values['S21.G00.11.004'] = target.getDefaultAddressZipCode()
  rubrics_values['S21.G00.11.005'] = target.getDefaultAddressCity()
  rubrics_values['S21.G00.11.006'] = ''
  rubrics_values['S21.G00.11.007'] = ''

# Individu
if block_id == 'S21.G00.30':
  rubrics_values["S21.G00.30.001"] = ''.join(target.getSocialCode().split(' '))[:13] # sometimes there are spaces in textfield
  rubrics_values["S21.G00.30.002"] = target.getLastName()
  rubrics_values["S21.G00.30.003"] = '' # Nom d'usage
  rubrics_values["S21.G00.30.004"] = ' '.join([target.getFirstName(), target.getMiddleName() or '']).strip()
  rubrics_values["S21.G00.30.006"] = formatDate(target.getStartDate())

# Contrat
if block_id == 'S21.G00.40':
  item = target.getAggregateValue()
  rubrics_values["S21.G00.40.001"] = formatDate(item.getCareerStartDate())
  rubrics_values["S21.G00.40.009"] = '00000'
  rubrics_values["S21.G00.40.019"] = target.getSubordinationValue().getCorporateRegistrationCode().replace(' ','')

return rubrics_values
