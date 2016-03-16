emission_letter_dict = {}

for a in site_list:
  if not a.startswith('site'):
    a = 'site/' + a
  site_codification = context.portal_categories.getCategoryValue(a).getCodification()
  if site_codification not in ('', None):
    lower_letter = site_codification[0].lower()
    if lower_letter == 'z':
      lower_letter = 'k'
    emission_letter_dict[lower_letter] = 1

return emission_letter_dict.keys()
