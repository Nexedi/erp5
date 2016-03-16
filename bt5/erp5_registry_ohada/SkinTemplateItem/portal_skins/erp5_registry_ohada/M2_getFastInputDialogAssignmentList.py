"""
  This script creates a list Person objects based
  on the M2 form information. It updates the list of persons
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
              description=None, function=None, old_function=None,
              new=None, going=None, maintained=None, modified=None, **kw):
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
  status = None
  if new:
    status = '_new_action'
  elif going:
    status = '_go_action'
  elif maintained:
    status = '_action_maintain'
  elif modified:
    status = '_action_modify'
  person = context.getPortalObject().person_module.newContent(
    portal_type='Person',
    uid=uid_string,
    first_name=first_name,
    last_name=last_name,
    start_date=start_date,
    default_birthplace_address_city=default_birthplace_address_city,
    function=function,
    old_function=old_function,
    description=description,
    status=status,
    temp_object=1,
    is_indexable=0,
  )
  result_list.append(person)
  uid += 1



#Create Shareholders
addPerson(first_name=context.getFirstAssociateFirstname(),
          last_name=context.getFirstAssociateLastname(),
          start_date=context.getFirstAssociateBirthday(),
          default_birthplace_address_city=context.getFirstAssociateBirthplace(),
          function=context.getFirstAssociateNewQuality(),
          old_function=context.getFirstAssociateOldQuality(),
          new=context.getFirstAssociateNewCheck(),
          going=context.getFirstAssociateGoingCheck(),
          maintained=context.getFirstAssociateMaintainedCheck(),
          modified=context.getFirstAssociateModifiedCheck(),)

addPerson(first_name=context.getSecondAssociateFirstname(),
          last_name=context.getSecondAssociateLastname(),
          start_date=context.getSecondAssociateBirthday(),
          default_birthplace_address_city=context.getSecondAssociateBirthplace(),
          function=context.getSecondAssociateNewQuality(),
          old_function=context.getSecondAssociateOldQuality(),
          new=context.getSecondAssociateNewCheck(),
          going=context.getSecondAssociateGoingCheck(),
          maintained=context.getSecondAssociateMaintainedCheck(),
          modified=context.getSecondAssociateModifiedCheck(),)

# only if there is M2 bis form :
m2_bis_result = context.contentValues(portal_type='M2 Bis')
number_list = ('Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh',
    'Eighth', 'Ninth')

if len(m2_bis_result):
  for m2 in m2_bis_result:
    for number in number_list:
      associateFirstName = getattr(m2, 'get%sAssociateFirstname' % number, None)
      associateLastName = getattr(m2, 'get%sAssociateLastname' % number, None)
      associateBirthday = getattr(m2, 'get%sAssociateBirthday' % number, None)
      associateBirthPlace = getattr(m2, 'get%sAssociateBirthplace' % number, None)
      associateAnotherInfo = getattr(m2, 'get%sAssociateAnotherInfo' % number, None)
      addPerson(first_name=associateFirstName(),
                last_name=associateLastName(),
                start_date=associateBirthday(),
                default_birthplace_address_city=associateBirthPlace(),
                function='entreprise/associe',
                old_function=None,
                description=associateAnotherInfo(),)


#Create Managers
addPerson(first_name=context.getFirstAdministratorFirstname(),
          last_name=context.getFirstAdministratorLastname(),
          start_date=context.getFirstAdministratorBirthday(),
          default_birthplace_address_city=context.getFirstAdministratorBirthplace(),
          function=context.getFirstAdministratorNewQuality(),
          old_function=context.getFirstAdministratorOldQuality(),
          new=context.getFirstAdministratorNewCheck(),
          going=context.getFirstAdministratorGoingCheck(),
          maintained=context.getFirstAdministratorMaintainedCheck(),
          modified=context.getFirstAdministratorModifiedCheck(),)

addPerson(first_name=context.getSecondAdministratorFirstname(),
          last_name=context.getSecondAdministratorLastname(),
          start_date=context.getSecondAdministratorBirthday(),
          default_birthplace_address_city=context.getSecondAdministratorBirthplace(),
          function=context.getSecondAdministratorNewQuality(),
          old_function=context.getSecondAdministratorOldQuality(),
          new=context.getSecondAdministratorNewCheck(),
          going=context.getSecondAdministratorGoingCheck(),
          maintained=context.getSecondAdministratorMaintainedCheck(),
          modified=context.getSecondAdministratorModifiedCheck(),)

# only if there is M2 bis form :
number_list = ('Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh',
    'Eighth', 'Ninth', 'Tenth')

if len(m2_bis_result):
  for m2 in m2_bis_result:
    for number in number_list:
      administratorFirstName = getattr(m2, 'get%sAdministratorFirstname' % number, None)
      administratorLastName = getattr(m2, 'get%sAdministratorLastname' % number, None)
      administratorBirthday = getattr(m2, 'get%sAdministratorBirthday' % number, None)
      administratorBirthPlace = getattr(m2, 'get%sAdministratorBirthplace' % number, None)
      administratorAnotherInfo = getattr(m2, 'get%sAdministratorAnotherInfo' % number, None)

      addPerson(first_name=administratorFirstName(),
                last_name=administratorLastName(),
                start_date=administratorBirthday(),
                default_birthplace_address_city=administratorBirthPlace(),
                function='entreprise/directeur/administrateur',
                old_function=None,
                description=administratorAnotherInfo(),)

number_list = ('First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh')

if len(m2_bis_result):
  for m2 in m2_bis_result:
    for number in number_list:
      auditorFirstName = getattr(m2, 'get%sAuditorFirstname' % number, None)
      auditorLastName = getattr(m2, 'get%sAuditorLastname' % number, None)
      auditorBirthday = getattr(m2, 'get%sAuditorBirthday' % number, None)
      auditorBirthPlace = getattr(m2, 'get%sAuditorBirthplace' % number, None)
      AuditorAnotherInfo = getattr(m2, 'get%sAuditorAnotherInfo' % number, None)

      addPerson(first_name=auditorFirstName(),
                last_name=auditorLastName(),
                start_date=auditorBirthday(),
                default_birthplace_address_city=auditorBirthPlace(),
                function='comptabilite/commissaire',
                old_function=None,
                description=auditorAnotherInfo(),)

return result_list
