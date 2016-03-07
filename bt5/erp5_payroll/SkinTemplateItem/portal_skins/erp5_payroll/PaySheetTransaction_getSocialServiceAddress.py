'''
  return the address line of the Social Service wich indice is line_number
  if the line_number is None, return all the address lines
'''

social_insurance_annotation_line_value = \
    context.getSocialInsuranceAnnotationLineValue()
if social_insurance_annotation_line_value is not None:
  organisation = social_insurance_annotation_line_value.getSourceValue()
else:
  return ''

street_address = '%s\n%s\n%s %s' % \
                              (organisation.getTitle() or '',
                               organisation.getDefaultAddressStreetAddress(''),
                               organisation.getDefaultAddressZipCode(''),
                               organisation.getDefaultAddressCity(''),)

# return the good lines
if line_number is None:
  return street_address
elif len(street_address.split('\n')) >= line_number:
  return street_address.split('\n')[line_number]
else:
  return ''
