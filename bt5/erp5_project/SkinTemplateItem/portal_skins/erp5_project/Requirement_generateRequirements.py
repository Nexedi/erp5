context_obj = context.getObject()
translateString = context.Base_translateString

requirement_module_type   = 'Requirement Module'
requirement_document_type = 'Requirement Document'
requirement_type          = 'Requirement'

if context_obj.getPortalType() == requirement_module_type:
  # we are in a module, so create a requirement document
  requirement_doc = context_obj.newContent( portal_type = requirement_document_type
                                      , title       = kw['requirement_document_title']
                                      , description = kw['requirement_document_description']
                                      )
  destination_obj = requirement_doc
elif context_obj.getPortalType() in (requirement_document_type, requirement_type):
  destination_obj = context_obj
else:
  return context.Base_redirect(
    form_id,
    keep_items=dict(
      portal_status_level='error',
      portal_status_message=translateString('Error: bad context')))

# this list contain all requirements items
requirements_items = []

# get the user information
for requirement_line in listbox:
  if 'listbox_key' in requirement_line:
    requirement_line_id = int(requirement_line['listbox_key'])
    requirement = {}
    requirement['id'] = requirement_line_id
    requirement['title'] = requirement_line['requirement_title']
    requirement['sub_title'] = requirement_line['sub_requirement_title']
    requirement['sub_description'] = requirement_line['sub_requirement_description']
    requirements_items.append(requirement)

# sort the requirements list by id to have the same order of the user
requirements_items.sort(key=lambda x: x['id'])

clean_requirements = {}
clean_requirements_key_list = [] # use a list for keys, to keep ordering
description_dict = {}
has_1st_level_requirement = False
has_2nd_level_requirement = False
new_1st_level_requirement = None

# scan every fast input line to create a structured and comprehensive list of requirements and sub-requirements
for requirement_item in requirements_items:
  # the item has a first level requirement
  if requirement_item['title'] not in ('', None):
    has_1st_level_requirement = True
    new_1st_level_requirement = []
    new_1st_level_requirement_title = requirement_item['title']
    description_dict[new_1st_level_requirement_title] = ''
  else:
    has_1st_level_requirement = False

  # the item has a second level requirement, built it
  if requirement_item['sub_title'] not in ('', None):
    has_2nd_level_requirement = True
    new_2nd_level_feat = {}
    new_2nd_level_feat['title'] = requirement_item['sub_title']
    if requirement_item['sub_title'] not in ('', None):
      new_2nd_level_feat['description'] = requirement_item['sub_description']
    else:
      new_2nd_level_feat['description'] = None
  else:
    has_2nd_level_requirement = False
    description_dict[requirement_item['title']] =\
          requirement_item['sub_description']

  if has_2nd_level_requirement and new_1st_level_requirement != None:
    new_1st_level_requirement.append(new_2nd_level_feat)

  if has_1st_level_requirement:
    if new_1st_level_requirement_title in clean_requirements:
      new_1st_level_requirement = clean_requirements[new_1st_level_requirement_title] + new_1st_level_requirement
    clean_requirements[new_1st_level_requirement_title] = new_1st_level_requirement
    clean_requirements_key_list.append(new_1st_level_requirement_title)

int_index = 0
destination_object_subobject_list = destination_obj.contentValues(checked_permission='View')
if len(destination_object_subobject_list):
  int_index = max([req.getIntIndex() for req in destination_object_subobject_list])

sub_requirement_int_index = 0
int_index_step = 10

# create requirement objects and sub-requirements
for key in clean_requirements_key_list:
  int_index += int_index_step
  new_1st_requirement = destination_obj.newContent( portal_type = requirement_type
                                              , title       = key
                                              , int_index   = int_index
                                              , description = description_dict[key]
                                              )
  sub_requirement_int_index = 0
  for second_level in clean_requirements[key]:
    sub_requirement_int_index += 10
    new_1st_requirement.newContent( portal_type = requirement_type
                                                , title       = second_level['title']
                                                , description = second_level['description']
                                                , int_index   = sub_requirement_int_index
                                                )
# return to the requirement
return context.Base_redirect(form_id,
 keep_items=dict(portal_status_message=translateString('Requirement document added.')))
