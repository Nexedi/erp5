context_obj = context.getObject()

role_type = 'Document Analysis Document Item'

# this list contain all items
items = []

# get the user information
for line in listbox:
  if 'listbox_key' in line and line['item_title'] not in ('', None):
    line_id = int(line['listbox_key'])
    item = {}
    item['id'] = line_id
    item['title'] = line['item_title']
    item['description'] = line['item_description']
    items.append(item)

# sort the list by id to have the same order of the user
items.sort(lambda x, y: cmp(x['id'], y['id']))

# create corresponding objects
for item in items:
  context_obj.newContent( portal_type        = role_type
                        , title              = item['title']
                        , description        = item['description']
                        )

# return to the feature module
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=' + role_type.replace(' ', '+') + '(s)+added.')
