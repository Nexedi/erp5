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
              start_date=None, default_birthplace_address_city='',
              default_address_text='', description=None, 
              function=None, **kw):
  """
   This creates a single temporary person with all appropriate parameters
  """
  # don't add person if there is no first_name
  if not first_name:
    return

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

  person = context.getPortalObject().person_module.newContent(
    portal_type='Person',
    uid=uid_string,
    first_name=first_name,
    last_name=last_name,
    start_date=start_date,
    default_birthplace_address_city=default_birthplace_address_city,
    default_address_text=default_address_text,
    function=function,
    description=description,
    temp_object=1,
    is_indexable=0,
  )
  result_list.append(person)
  uid += 1



#Create Shareholders
addPerson(first_name=context.getFirstAssociateFirstname(),
          last_name=context.getFirstAssociateLastname(),
          start_date=context.getFirstAssociateBirthday(),
          default_address_text=context.getFirstAssociateAddress(),
          default_birthplace_address_city=context.getFirstAssociateBirthplace(),)

addPerson(first_name=context.getSecondAssociateFirstname(),
          last_name=context.getSecondAssociateLastname(),
          start_date=context.getSecondAssociateBirthday(),
          default_address_text=context.getSecondAssociateAddress(),
          default_birthplace_address_city=context.getSecondAssociateBirthplace(),)

addPerson(first_name=context.getThirdAssociateFirstname(),
          last_name=context.getThirdAssociateLastname(),
          start_date=context.getThirdAssociateBirthday(),
          default_address_text=context.getThirdAssociateAddress(),
          default_birthplace_address_city=context.getThirdAssociateBirthplace(),)

# only if there is M0 bis form :
m0_bis_result = context.contentValues(portal_type='M0 Bis')
number_list = ('Fourth', 'Fifth', 'Sixth', 'Seventh',
    'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth',
    'Thirteenth', 'Fourteenth', 'Fifteenth', 'Sixteenth',
    'Seventeenth')

if len(m0_bis_result):
  for m0 in m0_bis_result:
    for number in number_list:
      associateFirstName = getattr(m0, 'get%sAssociateFirstname' % number, None)
      associateLastName = getattr(m0, 'get%sAssociateLastname' % number, None)
      associateBirthday = getattr(m0, 'get%sAssociateBirthday' % number, None)
      associateBirthPlace = getattr(m0, 'get%sAssociateBirthplace' % number, None)
      associateAnotherInfo = getattr(m0, 'get%sAssociateAnotherInfo' % number, None)

      addPerson(first_name=associateFirstName(),
                last_name=associateLastName(),
                start_date=associateBirthday(),
                default_birthplace_address_city=associateBirthPlace(),
                description=associateAnotherInfo(),)




#Create Managers
addPerson(first_name=context.getFirstAdministratorFirstname(),
          last_name=context.getFirstAdministratorLastname(),
          start_date=context.getFirstAdministratorBirthday(),
          default_birthplace_address_city=context.getFirstAdministratorBirthplace(),
          default_address_text=context.getFirstAdministratorAddress(),
          function=context.getFirstAdministratorFunction(),)

addPerson(first_name=context.getSecondAdministratorFirstname(),
          last_name=context.getSecondAdministratorLastname(),
          start_date=context.getSecondAdministratorBirthday(),
          default_birthplace_address_city=context.getSecondAdministratorBirthplace(),
          default_address_text=context.getSecondAdministratorAddress(),
          function=context.getSecondAdministratorFunction(),)

# only if there is M0 bis form :
number_list = ('Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh',
    'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth',
    'Thirteenth', 'Fourteenth', 'Fifteenth', 'Sixteenth')

if len(m0_bis_result):
  for m0 in m0_bis_result:
    for number in number_list:
      administratorFirstName = getattr(m0, 'get%sAdministratorFirstname' % number, None)
      administratorLastName = getattr(m0, 'get%sAdministratorLastname' % number, None)
      administratorBirthday = getattr(m0, 'get%sAdministratorBirthday' % number, None)
      administratorBirthPlace = getattr(m0, 'get%sAdministratorBirthplace' % number, None)
      administratorAnotherInfo = getattr(m0, 'get%sAdministratorAnotherInfo' % number, None)

      addPerson(first_name=administratorFirstName(),
                last_name=administratorLastName(),
                start_date=administratorBirthday(),
                default_birthplace_address_city=administratorBirthPlace(),
                description=administratorAnotherInfo(),)


#Create Auditors
addPerson(first_name=context.getFirstAuditorFirstname(),
          last_name=context.getFirstAuditorLastname(),
          start_date=context.getFirstAuditorBirthday(),
          default_birthplace_address_city=context.getFirstAuditorBirthplace(),
          default_address_text=context.getFirstAuditorAddress(),)

addPerson(first_name=context.getSecondAuditorFirstname(),
          last_name=context.getSecondAuditorLastname(),
          start_date=context.getSecondAuditorBirthday(),
          default_birthplace_address_city=context.getSecondAuditorBirthplace(),
          default_address_text=context.getSecondAuditorAddress(),)

return result_list
