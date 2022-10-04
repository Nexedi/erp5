destination_obj = context.getObject()

first_level_type  = 'Use Case Scenario'
second_level_type = 'Use Case Scenario Step'

# this list contain all input line items
items = []

# get the user information
for inputline in listbox:
  if 'listbox_key' in inputline:
    scenario = {}
    scenario['id'] = int(inputline['listbox_key'])
    scenario['title'] = inputline['scenario_title']
    scenario['step_title'] = inputline['step_title']
    scenario['step_description'] = inputline['step_description']
    scenario['step_actor'] = inputline['step_actor']
    items.append(scenario)

# sort the list by id to have the same order of the user
items.sort(lambda x, y: cmp(x['id'], y['id']))

clean_input_lines = {}
has_1st_level = False
has_2nd_level = False
new_1st_level_item = None

# scan every fast input line to create a structured and comprehensive list of items
for item in items:
  # the item has a first level
  if item['title'] not in ('', None):
    has_1st_level = True
    new_1st_level_item = []
    new_1st_level_key = item['title']
  else:
    has_1st_level = False

  # the item has a second level, so built it
  if item['step_title'] not in ('', None):
    has_2nd_level = True
    new_2nd_level_item = {}
    new_2nd_level_item['title'] = item['step_title']
    if item['step_title'] not in ('', None):
      new_2nd_level_item['description'] = item['step_description']
      new_2nd_level_item['actor'] = item['step_actor']
    else:
      new_2nd_level_item['description'] = None
      new_2nd_level_item['actor'] = None
  else:
    has_2nd_level = False

  if has_2nd_level == True and new_1st_level_item != None:
    new_1st_level_item.append(new_2nd_level_item)

  if has_1st_level == True:
    if new_1st_level_key in clean_input_lines:
      new_1st_level_item = clean_input_lines[new_1st_level_key] + new_1st_level_item
    clean_input_lines[new_1st_level_key] = new_1st_level_item

# get the next int index
result = destination_obj.searchFolder(portal_type = first_level_type, sort_on = (('int_index', 'DESC'),), limit = 1)
try:
  int_index = result[0].getObject().getIntIndex() + 1
except:
  int_index = 1

# create items objects and sub-objects
for key in clean_input_lines.keys():
  new_1st_level_obj = destination_obj.newContent( portal_type = first_level_type
                                                , int_index   = int_index
                                                , title       = key
                                                )
  int_index += 1

  second_level_int_index = 1
  for second_level in clean_input_lines[key]:
    new_2nd_level_obj = new_1st_level_obj.newContent( portal_type    = second_level_type
                                                    , int_index      = second_level_int_index
                                                    , title          = second_level['title']
                                                    , description    = second_level['description']
                                                    , source_section = second_level['actor']
                                                    )
    second_level_int_index += 1

# return to the module
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/view?portal_status_message=' + first_level_type.replace(' ', '+') + 's+Added.')
