portal = context.getPortalObject()
Base_translateString = portal.Base_translateString
split_depth = 2
if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}

def getSubFieldDict():
  def getSubFieldDictCache():
    # Define a dictionary where we store the subfields to display.
    sub_field_dict = {}
    # Try to assign each item to a sub field.
    for item in item_list:
      # Get value of the item
      item_value = item[int(not is_right_display)]
      if item_value is None:
        continue

      # Hash key from item_value
      item_split = item_value.split('/')
      item_key = '/'.join(item_split[:split_depth])

      # Create a new subfield if necessary
      if item_key not in sub_field_dict:
        # Create property dict (key are field parameters)
        sub_field_property_dict = default_sub_field_property_dict.copy()
        sub_field_property_dict['key'] = item_key
        sub_field_property_dict['title'] = Base_translateString("GAP - ${gap_title}", mapping=dict(
                    gap_title=context.portal_categories.resolveCategory(
                          'gap/%s' % item_key).getTranslatedTitle()))
        sub_field_property_dict['required'] = 0
        sub_field_property_dict['field_type'] = 'ListField'
        sub_field_property_dict['size'] = 1
        sub_field_property_dict['item_list'] = [('', '') ]
        sub_field_property_dict['value'] = None
        sub_field_dict[item_key] = sub_field_property_dict

      sub_field_dict[item_key]['item_list'].append(item)
      sub_field_property_dict['size'] = 1
    return sub_field_dict

  from Products.ERP5Type.Cache import CachingMethod
  getSubFieldDictCache = CachingMethod(
      getSubFieldDictCache,
      id='Account_getSubFieldDict.%s' % portal.Localizer.get_selected_language())
  # Those cached dictionnaries are later modified, we just reset the 'value'
  # key to return clean dictionnaries.
  sub_field_dict = getSubFieldDictCache()
  for k in list(sub_field_dict.keys()):
    sub_field_dict[k]['value'] = None
  return sub_field_dict

sub_field_dict = getSubFieldDict()
# Update sub_field_dict with values
for item_value in value_list:
  if item_value:
    # Hash key from item_value
    item_split = item_value.split('/')
    item_key = '/'.join(item_split[:split_depth])
    
    if item_key not in sub_field_dict:
      # This can only happens if an accounting plan have been uninstalled
      sub_field_property_dict = default_sub_field_property_dict.copy()
      sub_field_property_dict['key'] = item_key
      sub_field_property_dict['title'] = item_key
      sub_field_property_dict['required'] = 0
      sub_field_property_dict['field_type'] = 'ListField'
      sub_field_property_dict['size'] = 1
      sub_field_property_dict['item_list'] = [('', '')]
      sub_field_property_dict['value'] = None
      sub_field_dict[item_key] = sub_field_property_dict

    sub_field_dict[item_key]['value'] = item_value

# Return the list of subfield configuration.
return list(sub_field_dict.values())
