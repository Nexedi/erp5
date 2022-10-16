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

#NOTUSED yet # get a level-ordered list of primary key
# primary_keys = []
# for level_rule in transformation_rules:
#   primary_keys.append(level_rule['primary_key'])

# get a level-ordered list of input/output name pairs and their required status
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

# get a level-ordered list of required fields
# TODO : auto;atically add the primary_key
required_field = []
for level_rule in transformation_rules:
  new_required_level = []
  for data_item in level_rule['data']:
    if data_item['required'] == True:
      new_required_level.append(data_item['input_data_name'])
  required_field.append(new_required_level)



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



# the intermediate ordered-list of data and levels
ordered_items = []
ordered_levels = []

# scan every fast input line to create a structured and comprehensive list of items
for line in fast_input_lines:

  # the list of covered level of the line
  line_levels = []

  # test every level to know if they are OK
  level_depth = -1
  for required_level in required_field:
    # increase the level-depth
    level_depth += 1
    valid_level = None
    # to validate this level, check every required field
    for field_to_test in required_level:
      if line[field_to_test] in ('', None):
        valid_level = False
        break
      else:
        valid_level = True

    # the current level is ok
    if valid_level != False:
      # add the current level to the list of good ones
      line_levels.append(level_depth)

  # exclude empty line
  if len(line_levels) > 0:
    # put data of the line to a structured list
    line_data = []
    for level in line_levels:
      new_level_data = {}
      for io_name_pair in io_names[level]:
        new_level_data[io_name_pair[1]] = line[io_name_pair[0]]
      new_level_data['portal_type'] = level_portal_types[level]
      line_data.append({level : new_level_data})

    # save the line data item and the level list in the right order
    ordered_items += line_data
    ordered_levels += line_levels



# the clean ordered list of data
clean_data = []

# list of processed level
processed_level = []

# exclude level-incoherent objects
for i in range(len(ordered_items)):
  current_item_level = ordered_levels[i]
  current_item_data = ordered_items[i]
  item_ok = False

  # handle the "root" item case (must be a 0-level)
  if current_item_level == 0:
    item_ok = True

  # to compare with previous items, some must be alredy processed
  if len(processed_level) > 0 and item_ok == False:
    prev_item_level = ordered_levels[i-1]

    # the current item and the previous one are follower
    if current_item_level == prev_item_level+1 or current_item_level == prev_item_level:
      item_ok = True
    else:
      # the current item must be in the processed level list to be accepted as sub object
      if current_item_level in processed_level:
        item_ok = True

  # item is level-coherent, so keep it
  if item_ok == True:
    # add to the clean list
    clean_data.append(list(current_item_data.values())[0])
    # add to the processed list of level
    processed_level.append(current_item_level)

clean_levels = processed_level



# the final structured list of data
structured_data = []

# create a list of ordered list
series_list = []
new_serie = []
for i in range(len(clean_levels)):
  current_item_level = clean_levels[i]
  current_item_data = clean_data[i]

  # handle the "root" item case (must be a 0-level)
  if current_item_level == 0:
    if len(new_serie) > 0:
      series_list.append(new_serie)
    new_serie = [(i, current_item_level)]
  else:
    prev_item_level = clean_levels[i-1]
    # the current item and the previous one are of the same serie
    if current_item_level > prev_item_level:
      new_serie.append((i, current_item_level))
    elif current_item_level == prev_item_level:
      series_list.append(new_serie)
      new_serie = [(i, current_item_level)]

# the last element must be saved
series_list.append(new_serie)



# this function create a serie from a simple data structure
def simpleStructure(serie):
  previous_level = []
  for (data_id, data_level) in serie[::-1]:
    previous_level = [(data_id, data_level, previous_level)]
  return previous_level

# create the complex data structure
data_groups = []
new_group = []
for serie in series_list:
  simple_struct = simpleStructure(serie)
  # zero delimit the zone between two groups
  if simple_struct[0][1] == 0:
    # save the last group
    if len(new_group) > 0:
      data_groups.append(new_group)
    # start a new group
    new_group = [simple_struct]
  else:
    new_group.append(simple_struct)

# the last element must be saved
data_groups.append(new_group)

print(data_groups)


# [
#
#  [
#   [(0, 0, [(1, 1, [])])],
#   [(2, 1, [])],
#   [(3, 1, [])]
#  ],
#
#  [
#   [(4, 0, [(5, 1, [])])],
#   [(6, 1, [])]
#  ]
#
# ]
#
#
# [[(0, 0, [(1, 1, [])])], [(2, 1, [])]] -->  [(0, 0, [(1, 1, []), (2, 1, [])])]

def getLastSubList(current_list):
  return current_list[-1][2]

def setLastSubList(current_list, last_sub_list_value):
  current_list[-1][2] = last_sub_list_value
  return current_list

def getListLevel(current_list):
  return current_list[-1][1]

def aggregate(big_list, item_to_add):
  if big_list == []:
    return []
  if getListLevel(big_list) == getListLevel(item_to_add):
    print("big_list " + big_list)
    print("item_to_add " + item_to_add)
    big_list.append(item_to_add)
    return big_list
  else:
    new_big_list_sub_level = aggregate(getLastSubList(big_list), item_to_add)
    print("new_big_list_sub_level " + new_big_list_sub_level)
    print("big_list " + big_list)
    return None #setLastSubList(big_list, new_big_list_sub_level)


for group in data_groups:
  collapsed_group = group[0]
  for serie_group in group[1:]:
    print(serie_group)
    collapsed_group = aggregate(collapsed_group, serie_group)

  print(collapsed_group)


#     if
#     collapsed_group.append()



# for simple_struct in simple_structures:
#   if simple_struct


return printed
