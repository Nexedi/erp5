"""
  This script creates a list Person objects based
  on the M0 form information. It updates the list of persons
  based on fast input entries.
"""
from string import zfill
global result_list
global uid
uid = 0
result_list = []
request = context.REQUEST
listbox = getattr(request, 'listbox', None) # Retrieve the fast input data if any

def addPerson(first_name=None, last_name=None,
              start_date=None, default_birthplace_address_city=None,
              default_address_text=None, description=None, 
              function=None, **kw):
  """
    This creates a single temporary person with all appropriate parameters
  """
  global result_list
  global uid
  if not (first_name or last_name):
    return
  uid_string = 'new_%s' % zfill(uid, 3)
  if listbox is not None:
    # Use input parameters instead of default
    # if available in listbox
    line = listbox[zfill(uid, 3)]
    if line.has_key('last_name') and line.has_key('first_name') :
      first_name = line['first_name']
      last_name = line['last_name']
  person = context.newContent(
    portal_type='Person',
    uid=uid_string,
    first_name=first_name,
    last_name=last_name,
    start_date=start_date,
    default_birthplace_address_city = default_birthplace_address_city,
    default_address_text=default_address_text,
    function=function,
    description=description,
    temp_object=1,
    is_indexable=0,
  )
  result_list.append(person)
  uid += 1

#Create Shareholders

#Create Managers
addPerson(first_name=context.getFirstAdministratorFirstName(),
          last_name=context.getFirstAdministratorLastName(),
          start_date=context.getFirstAdministratorBirthday(),
          default_birthplace_address_city=context.getFirstAdministratorBirthplace(),
          default_address_text=context.getFirstAdministratorAddress(),)

addPerson(first_name=context.getSecondAdministratorFirstName(),
          last_name=context.getSecondAdministratorLastName(),
          start_date=context.getSecondAdministratorBirthday(),
          default_birthplace_address_city=context.getSecondAdministratorBirthplace(),
          default_address_text=context.getSecondAdministratorAddress(),)


return result_list
