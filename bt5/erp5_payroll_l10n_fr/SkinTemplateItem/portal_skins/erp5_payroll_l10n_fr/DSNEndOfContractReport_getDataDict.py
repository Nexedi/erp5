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
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def formatFloat(number):
  return "{:.2f}".format(float(number))

# Declaration
if block_id == 'S20.G00.05':
  now = DateTime()
  rubric_value_dict['S20.G00.05.001'] = '02' # End of Contract DSN
  rubric_value_dict['S20.G00.05.002'] = '01' # Normal Declaration
  rubric_value_dict['S20.G00.05.003'] = '11'
  rubric_value_dict['S20.G00.05.004'] = kw['order'] # Declaration.Ordre, incremented for each DSN
  rubric_value_dict['S20.G00.05.006'] = ''
  rubric_value_dict['S20.G00.05.007'] = formatDate(DateTime(now.year(), now.month(), now.day()))
  rubric_value_dict['S20.G00.05.009'] = ''
  rubric_value_dict['S20.G00.05.010'] = '01'

elif block_id == 'S21.G00.40':
  item = target.getAggregateValue()
  rubric_value_dict["S21.G00.40.001"] = formatDate(item.getCareerStartDate())
  rubric_value_dict["S21.G00.40.009"] = '00000'
  rubric_value_dict["S21.G00.40.019"] = target.getSubordinationValue().getCorporateRegistrationCode().replace(' ','')
  rubric_value_dict["S21.G00.40.026"] = enrollment_record.getCivilServantStatus()

return rubric_value_dict
