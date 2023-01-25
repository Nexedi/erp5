context_obj = context.getObject()

role_type = 'Document Analysis Lexicon Item'

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
    item['lexicon_item_type'] = line['type']
    item['lexicon_item_ubm'] = line['ubm']
    item['item_class'] = line['class']
    item['item_property_sheet'] = line['propertysheet']
    items.append(item)

# sort the list by id to have the same order of the user
items.sort(lambda x, y: cmp(x['id'], y['id']))

# create corresponding objects
for item in items:
  context_obj.newContent( portal_type        = role_type
                        , title              = item['title']
                        , description        = item['description']
                        , lexicon_item_type  = item['lexicon_item_type']
                        , lexicon_item_ubm        = item['lexicon_item_ubm']
                        , item_class        = item['item_class']
                        , item_property_sheet        = item['item_property_sheet']
                        )

# return to the feature module
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + '?portal_status_message=' + role_type.replace(' ', '+') + '(s)+added.')
