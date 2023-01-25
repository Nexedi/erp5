context_obj = context.getObject()

role_type = 'Test Case Step'

# this list contain all items
items = []

# get the next int index
result = context_obj.searchFolder(portal_type = role_type, sort_on = (('int_index', 'DESC'),), limit = 1)
try:
  int_index = result[0].getObject().getIntIndex() + 1
except: #XXX
  int_index = 1

# get the user information
for line in listbox:
  if 'listbox_key' in line and line['title'] not in ('', None):
    line_id = int(line['listbox_key'])
    item = {}
    item['id'] = line_id
    item['int_index'] = int_index
    item['title'] = line['title']
    item['description'] = line['description']
    item['reaction_description'] = line['reaction_description']
    item['source_section'] = line['source_section']
    items.append(item)
    int_index += 1

# sort the list by id to have the same order of the user
items.sort(lambda x, y: cmp(x['id'], y['id']))

# create corresponding objects
for item in items:
  context_obj.newContent( portal_type          = role_type
                        , int_index            = item['int_index']
                        , title                = item['title']
                        , description          = item['description']
                        , reaction_description = item['reaction_description']
                        , source_section       = item['source_section']
                        )

# return to the feature module
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/TestCase_viewTestCaseStepList?portal_status_message=' + role_type.replace(' ', '+') + 's+Added.')
