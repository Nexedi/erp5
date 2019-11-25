"""
  This script is used in parallel list fields
  to implement a new 'multi list field behaviour' 
  (it repeats category items
  in such way that it is possible to select multiple
  categories for the same document )
"""
if default_sub_field_property_dict is None:
  default_sub_field_property_dict = {}
# Initialise result
sub_field_list = []

title = default_sub_field_property_dict['title']

# Maximum size of the MultiListField
default_sub_field_property_dict.update(title='&nbsp;',
                                       key='default:list',
                                       field_type='ListField',
                                       size=1,
                                       item_list=[('', '')] + item_list,
                                       value=None)
for value in value_list:
  new_dict = default_sub_field_property_dict.copy()
  new_dict['value'] = value
  sub_field_list.append(new_dict)

sub_field_list.append(default_sub_field_property_dict)

sub_field_list[0]['title'] = title
return sub_field_list
