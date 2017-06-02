"""
  This script tries to find most appropriate persons
  based on first name, last name, etc.

  Current approach:
  - find people with given first name and last name
  - put in first position the one with same date

  Issues: this will fail if many people share the same name.
  Query performance will be miserable if the birthday is not 
  take into account. Also, if the system is not able to
  search approximate choice, it will fail too because
  users will just create persons.

  TODO: improve the script so that the script always try
  to find something to display. This may require to 
  do some full text search if the keyword based search fails.
"""

# Define portal
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
from string import capitalize
from string import upper
from string import lower
portal = context.getPortalObject()
result = []

person_module = context.getPortalObject().person_module

# Find candidate list
#title=' '.join((person_firstname,person_last_name))
if person_first_name.find('-') != -1 and person_last_name.find(' ') != -1:
  person_first_name = person_first_name.replace('-','%')
  person_last_name = person_last_name.replace(' ','%')
elif person_first_name.find(' ') != -1 and person_last_name.find("'") != -1:
  person_first_name = person_first_name.replace(' ','%')
  person_last_name = person_last_name.replace("'",'%')
elif person_first_name.find(' ') !=-1 and person_last_name.find(' ') != -1:
  person_first_name = person_first_name.replace(' ','%')
  person_last_name = person_last_name.replace(' ','%')
elif person_first_name.find('-') != -1 or person_first_name.find(' ') != -1:
  person_first_name = person_first_name.replace('-','%')
  person_first_name = person_first_name.replace(' ','%')
elif person_last_name.find('-')!=-1 or person_last_name.find(' ') != -1 or person_last_name.find("'") != -1:
  person_last_name = person_last_name.replace('-','%')
  person_last_name = person_last_name.replace(' ','%')
  person_last_name = person_last_name.replace("'",'%')

person_title = ' '.join((person_first_name,person_last_name))
person_title_reversed = ' '.join((person_last_name,person_first_name))
if person_start_date == None or person_birthplace == None:
  query = ComplexQuery(Query(title = person_title),
                       Query(title = person_title_reversed),
                       Query(title = person_first_name),
                       Query(title = person_last_name),
                       logical_operator = "OR")
else:
  query = ComplexQuery(Query(title = person_title),
                       ComplexQuery(
                         Query(title = person_title),
                         Query(birth_date = person_start_date),
                         logical_operator = "AND"),
                       ComplexQuery(
                         Query(title = person_title),
                         Query(birthplace_city = person_birthplace),
                         logical_operator = "AND"),
                       ComplexQuery(
                         Query(birth_date = person_start_date),
                         Query(birthplace_city = person_birthplace),
                         logical_operator = "AND"),
                       ComplexQuery(
                         Query(title = person_title_reversed),
                         Query(title = person_first_name),
                         Query(title = person_last_name),
                         logical_operator = "OR"),
                       ComplexQuery(
                         Query(title = person_title),
                         Query(birth_date = [DateTime(person_start_date.year(), 1, 1), DateTime(person_start_date.year(), 12, 31),],range = 'minmax'),
                         logical_operator = "AND"),
                         logical_operator = "OR")
#select_expression = \
#"""((title ="%s") + (start_date ="%s") + (birthplace_city ="%s"))AS result_order
#""" % (person_title, person_start_date, person_birthplace)

candidate_list = sorted(
  context.portal_catalog(
    portal_type='Person',
    query=query,
    select_list=['title'],
  ),
  key=lambda x: x.title == person_title
)

for candidate in candidate_list:
  candidate_first_name = candidate.getFirstName()
  candidate_last_name = candidate.getLastName()
  if not candidate_first_name:
    candidate_first_name = 'Prénom non définit'
  if not candidate_last_name:
    candidate_last_name = 'Nom non définit'
    
  if candidate.getStartDate()==None and candidate.getDefaultBirthplaceAddressCity()==None:
     candidate_start_date = 'Date non définie'
     candidate_birthplace_address_city = 'Lieu non défini'
  elif candidate.getDefaultBirthplaceAddressCity()==None:
     candidate_birthplace_address_city = 'Lieu non défini'
     candidate_start_date = str(candidate.getStartDate())
  elif candidate.getStartDate()==None:
     candidate_start_date = 'Date non définie'
     candidate_birthplace_address_city = str(candidate.getDefaultBirthplaceAddressCity())
  else:
     candidate_start_date = str(candidate.getStartDate())
     candidate_birthplace_address_city = str(candidate.getDefaultBirthplaceAddressCity())
  result.append((' '.join((candidate_first_name,
                           candidate_last_name,
                           candidate_start_date,
                           candidate_birthplace_address_city)),candidate.getRelativeUrl()))

# Append extra actions
result.append(('-', '_no_action'))
result.append(('New Person', '_action_create'))
return result
