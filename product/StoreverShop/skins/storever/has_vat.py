##parameters=euvat , country

# Tells if this client has to pay VAT

eu_countries = [ 'Austria', 'Belgium', 'Denmark', 'Finland', 'France', 'Germany', 'Greece', 'Ireland', 'Italy', 'Luxembourg', 'Netherlands', 'Portugal', 'Spain', 'Sweden' ,'United Kingdom']

if euvat != '' and country != 'France':
  return 0
if not country in eu_countries:
  return 0
return 1