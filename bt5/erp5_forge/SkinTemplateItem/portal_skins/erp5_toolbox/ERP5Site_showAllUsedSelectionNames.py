# This tool is able to check, if selection_name in listboxes in forms
# are unique "enough".
# It shall print nothing on properly made site, which will mean
# that one selection_name is set in unique named form.
# Script supports same-named form in many portal_skins.
# but only if selection name appears more then once.
# It is based on ERP5Site_checkXhtmlForm
# To check your installation run it as:
#  portal_skins/ERP5Site_showAllUsedSelectionNames
#   default invocation
#  portal_skins/ERP5Site_showAllUsedSelectionNames?all_selections=1
#   will show even proper selections, you can check if selection_name
#   is same in other skins for some form

o = context

def recurse(o, callback, seldict):
  for obj in o.objectValues():
    if obj.meta_type == 'ERP5 Form':
      callback(obj,seldict)
    elif obj.meta_type == 'Folder':
      recurse(obj, callback, seldict)

def callback(o,seldict):
  pt = o.pt
  listbox_count = 0
  if len(o.get_fields()) != 0:
    if pt not in ('documentation_template', 'sort_list_dialog', 'configure_list_dialog'):
      for group in o.get_groups(include_empty = 1):
        fields = o.get_fields_in_group(group)
        for field in fields:
          if field.meta_type == 'ListBox':
            listbox_count = listbox_count + 1
            form_name = o.absolute_url() # TODO it could be done much better
            # assumes that name of form is unique enough
            form_name = form_name[form_name.rfind('/')+1:]
            if field.get_value('selection_name') in seldict:
              old_list = seldict[field.get_value('selection_name')]
              if form_name not in old_list:
                old_list.append(form_name)
              seldict[field.get_value('selection_name')] = old_list # TODO update to reimplement
            else:
              old_list = [form_name]
              seldict[field.get_value('selection_name')] = old_list

seldict = {}
recurse(o, callback, seldict)

for selection_name in seldict.keys():
  if len(seldict[selection_name]) != 1 or all_selections:
    print("'%s' [%s]"%(selection_name,len(seldict[selection_name])))
    for form_name in seldict[selection_name]:
      print("\t%s"%(form_name,))
return printed
