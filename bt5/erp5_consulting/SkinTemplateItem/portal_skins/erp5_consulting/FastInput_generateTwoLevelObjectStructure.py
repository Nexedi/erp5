##################################################
#### About the transformation_rules structure ####
# a key indicate that input of that level having the same value must be grouped together
# the key has the value of one 'input_data_name' of the corresponding level
# a key is unique and required (in this version)
##################################################

# some analysis of transformation rules
# get all input data names
input_data_names = []
for level_rule in transformation_rules:
  for data_item in level_rule['data']:
    input_data_names.append(data_item['input_data_name'])
# get a level-ordered list of key
data_keys = []
for level_rule in transformation_rules:
  data_keys.append(level_rule['data_key'])
# get a level-ordered list of input/output name pairs
io_names = []
for level_rule in transformation_rules:
  new_io_names_level = []
  for data_item in level_rule['data']:
    new_io_names_level.append([data_item['input_data_name'], data_item['output_property']])
  io_names.append(new_io_names_level)
# get a level-ordered list of portal_types
level_portal_types = []
for level_rule in transformation_rules:
  level_portal_types.append(level_rule['portal_type'])

# this list contain all fast input lines
fast_input_lines = []

# get the fast input form datas
for inputline in listbox:
  if 'listbox_key' in inputline:
    line = {}
    line['id'] = int(inputline['listbox_key'])
    for data_name in input_data_names:
      line[data_name] = inputline[data_name]
    fast_input_lines.append(line)

# sort the list by id to have the same order of the user
fast_input_lines.sort(lambda x, y: cmp(x['id'], y['id']))

structured_input_data = {}
has_1st_level = False
has_2nd_level = False
new_1st_level_sub_items = None

# scan every fast input line to create a structured and comprehensive list of items
for line in fast_input_lines:
  # the line has first level informations
  if line[data_keys[0]] not in ('', None):
    has_1st_level = True
    new_1st_level_sub_items = []
    new_1st_level_properties = {}
    new_1st_level_key = line[data_keys[0]]
    for io_name_pair in io_names[0]:
      new_1st_level_properties[io_name_pair[1]] = line[io_name_pair[0]]
  else:
    has_1st_level = False

  # the line has second level informations, so built the second level
  if line[data_keys[1]] not in ('', None):
    has_2nd_level = True
    new_2nd_level_item = {}
    for io_name_pair in io_names[1]:
      new_2nd_level_item[io_name_pair[1]] = line[io_name_pair[0]]
  else:
    has_2nd_level = False

  if has_2nd_level == True and new_1st_level_sub_items != None:
    new_1st_level_sub_items.append(new_2nd_level_item)

  if has_1st_level == True:
    if new_1st_level_key in structured_input_data:
      new_1st_level_sub_items = structured_input_data[new_1st_level_key][1] + new_1st_level_sub_items
    else:
      structured_input_data[new_1st_level_key] = [None, None]
      structured_input_data[new_1st_level_key][0] = new_1st_level_properties
    structured_input_data[new_1st_level_key][1] = new_1st_level_sub_items

# create items objects and sub-objects
for upper_level_key in structured_input_data:
  first_level = structured_input_data[upper_level_key][0]
  new_1st_level_obj = destination.newContent(portal_type = level_portal_types[0])
  for property_title in first_level.keys():
    new_1st_level_obj.setProperty(property_title, first_level[property_title])
  second_level_id = 0
  for second_level in structured_input_data[upper_level_key][1]:
    second_level_id += 10
    new_2nd_level_obj = new_1st_level_obj.newContent( portal_type = level_portal_types[1]
                                                    , id          = str(second_level_id).zfill(4)
                                                    )
    for property_title in second_level.keys():
      new_2nd_level_obj.setProperty(property_title, second_level[property_title])

# return to the module
return context.REQUEST.RESPONSE.redirect(destination.absolute_url() + '?portal_status_message=' + level_portal_types[0].replace(' ', '+') + '(s)+added.')
