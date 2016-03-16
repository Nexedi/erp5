"""
  This script creates assignments based on the fast input information.
  It should take into account any assignment which were already created
  so that they are not duplicated.
"""
portal = context.getPortalObject()
person_module = context.getPortalObject().person_module
items = []
for line in listbox:
  if line.has_key('listbox_key') and line['last_name'] not in ('', None):
    line_id = int(line['listbox_key'])
    item = {}
    item['id'] = line_id
   # item['title']= line['title']
    item['first_name'] = line['first_name']
    item['last_name'] = line['last_name']
    item['start_date'] = line['start_date']
    item['default_birthplace_address_city'] = line['default_birthplace_address_city']
    item['function'] = line['function']
    item['choice'] = line['choice']
    item['status'] = line['status']
    item['old_function'] = line['old_function']
    items.append(item)
items.sort(lambda x, y: cmp(x['id'], y['id']))
context_obj = context.getObject()
if context_obj.getPortalType()=='M2 Bis':
   context_obj= context_obj.getParentValue()
   form_id = 'M2Bis_view'

# create corresponding assignment
for item in items:
  portal = context.getPortalObject()
  new_items=[]
#if the person in the fast input is a new person, create assignment
  if item['status'] == '_new_action' :
    if item['choice'] == '_action_create':
      person_module = context.getPortalObject().person_module
      person_title = item['first_name'] + ' ' + item['last_name']
      person_third_party = person_module.newContent(portal_type='Person',
                                                   title=person_title,
                                                   first_name=item['first_name'],
                                                   last_name =item['last_name'],
                                                   start_date=item['start_date'],
             default_birthplace_address_city=item['default_birthplace_address_city'],)
      person_third_party_assignment = \
             person_third_party.newContent(portal_type='Assignment',
                                          function=item['function'],
                                          destination_form_value=context_obj) 
      person_third_party_assignment.openSubmit()
    else:
      person = portal.restrictedTraverse(item['choice'])
      assignment = person.newContent(portal_type='Assignment',
                                     function=item['function'],
                                     destination_form_value=context_obj)
      assignment.openSubmit()
  elif item['status'] == '_action_maintain':
    pass
  elif item['status'] == '_action_modify':
    person = portal.restrictedTraverse(item['choice'])
    corporate_registration_code = context_obj.getCorporateRegistrationCode()
    organisation_list = [organisation.getObject() for organisation in portal.portal_catalog(parent_uid=portal.organisation_module.getUid(), 
                         corporate_registration_code=corporate_registration_code)]
    #function_relative_url = '/'.join(('function', item['old_function']))
    for organisation in organisation_list:
      # XXX for assignment in assignment_list:
      for assignment in person.contentValues(portal_type='Assignment',
                                              checked_permission='View'):
        if assignment.getValidationState() =='open' and \
            assignment.getFunction() == item['old_function'] and \
            organisation in assignment.getDestinationValueList():
          assignment.edit(function=item['function'],
                          destination_value=organisation,)
  elif item['status']=='_go_action':
    person = portal.restrictedTraverse(item['choice'])
    corporate_registration_code = context_obj.getCorporateRegistrationCode()
    organisation_list = [organisation.getObject() for organisation in portal.portal_catalog(parent_uid=portal.organisation_module.getUid(), 
                         corporate_registration_code=corporate_registration_code)]
    for organisation in organisation_list:
      for assignment in person.contentValues(portal_type='Assignment',
                                               checked_permission='View'):
        if assignment.getValidationState() =='open' and \
              assignment.getFunction() == item['old_function'] and \
              organisation in assignment.getDestinationValueList():
          assignment.edit(destination_form_value=context_obj)
          assignment.cancel()

role_type = 'Assignment' 
if context_obj.getPortalType()=='M2':
 form_id = 'M2_view'
elif context_obj.getPortalType()=='P2':
 form_id = 'P2_view'
ignore_layout = 0
editable_mode = 1
ignore_layout = int(ignore_layout)
editable_mode = int(editable_mode)
message = role_type.replace(' ', '+') + '(s)+added.'
redirect_url = '%s/%s?ignore_layout:int=%s&editable_mode:int=%s&portal_status_message=%s' % (
                                  context.absolute_url(),
                                  form_id,
                                  ignore_layout,
                                  editable_mode,
                                  message)
# return to the feature module
return context.REQUEST.RESPONSE.redirect(redirect_url)
