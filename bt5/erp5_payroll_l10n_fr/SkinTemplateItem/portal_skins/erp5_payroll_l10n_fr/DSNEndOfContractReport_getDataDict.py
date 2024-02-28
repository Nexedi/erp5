rubric_value_dict = {}


def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())


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
