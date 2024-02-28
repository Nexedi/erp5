rubric_value_dict = {}


def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())


# Bloc Declaration
if block_id == 'S20.G00.05':
  now = DateTime()
  rubric_value_dict['S20.G00.05.001'] = kw['dsn_type']
  rubric_value_dict['S20.G00.05.002'] = '01'
  rubric_value_dict['S20.G00.05.003'] = '11'
  rubric_value_dict['S20.G00.05.004'] = kw['order']
  rubric_value_dict['S20.G00.05.006'] = ''
  rubric_value_dict['S20.G00.05.007'] = formatDate(DateTime(now.year(), now.month(), now.day()))
  rubric_value_dict['S20.G00.05.009'] = ''

if block_id == 'S20.G00.07':
  rubric_value_dict['S20.G00.07.001'] = ' '.join((target.getLastName(), target.getFirstName()))
  rubric_value_dict['S20.G00.07.002'] = target.getDefaultTelephoneCoordinateText()
  rubric_value_dict['S20.G00.07.003'] = target.getDefaultEmailUrlString()
  rubric_value_dict['S20.G00.07.004'] = '09'

# Entreprise
if block_id == 'S21.G00.06':
  rubric_value_dict['S21.G00.06.001'] = ''.join(target.getCorporateRegistrationCode().split(' '))[:9]
  rubric_value_dict['S21.G00.06.002'] = ''.join(target.getCorporateRegistrationCode().split(' '))[-5:]

# Etablissement
elif block_id == 'S21.G00.11':
  rubric_value_dict['S21.G00.11.001'] = target.getCorporateRegistrationCode()[-5:]
  rubric_value_dict['S21.G00.11.003'] = target.getDefaultAddressStreetAddress()
  rubric_value_dict['S21.G00.11.004'] = target.getDefaultAddressZipCode()
  rubric_value_dict['S21.G00.11.005'] = target.getDefaultAddressCity()
  rubric_value_dict['S21.G00.11.006'] = ''
  rubric_value_dict['S21.G00.11.007'] = ''

# Individu
if block_id == 'S21.G00.30':
  social_code = target.getSocialCode('')
  rubric_value_dict["S21.G00.30.001"] = ("" if not social_code else "".join(social_code.split(' '))[:13])
  rubric_value_dict["S21.G00.30.001"] = ''.join(target.getSocialCode('').split(' '))[:13] # sometimes there are spaces in textfield
  rubric_value_dict["S21.G00.30.002"] = target.getLastName()
  rubric_value_dict["S21.G00.30.003"] = '' # Nom d'usage
  rubric_value_dict["S21.G00.30.004"] = ' '.join([target.getFirstName(), target.getMiddleName() or '']).strip()
  rubric_value_dict["S21.G00.30.006"] = formatDate(target.getStartDate())
  rubric_value_dict["S21.G00.30.020"] = target.getCareerReference('')

# Contrat
if block_id == 'S21.G00.40':
  item = target.getAggregateValue()
  rubric_value_dict["S21.G00.40.001"] = formatDate(item.getCareerStartDate())
  rubric_value_dict["S21.G00.40.009"] = '00000'
  rubric_value_dict["S21.G00.40.019"] = target.getSubordinationValue().getCorporateRegistrationCode().replace(' ','')

return rubric_value_dict
