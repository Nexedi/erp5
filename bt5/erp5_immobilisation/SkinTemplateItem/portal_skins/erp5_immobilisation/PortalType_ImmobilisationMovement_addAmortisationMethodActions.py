view_id_basis = "%s_%s_amortisation_method_view_details"
view_action_basis = "Immobilisation_%s%sAmortisationMethodViewDetails"
view_condition_basis = "object/Immobilisation_isUsing%s%sAmortisationMethod"
view_permissions_basis = ('View',)
amortisation_method_view = 'amortisation_method_view'

action_list = context.listActions()

print("Making portal type '%s' an Immobilisation Movement :" % context.getId())
# Add a view for each amortisation method
amortisation_method_list = context.Immobilisation_getAmortisationMethodList()
for method in amortisation_method_list:
  region = method[0]
  id = method[1].getId()
  title = method[1].title or id
  action_id =  view_id_basis % (region, id)

  print("- Adding View for method '%s'... " % title, end=' ')

  # Check if the action already exists
  exists = 0
  for action in action_list:
    if getattr(action, "id", None) == action_id:
      print("already exists")
      exists = 1

  if not exists:
    capitalized_id = "".join([o.capitalize() for o in id.split("_")])
    action_action = view_action_basis % (region, capitalized_id)
    action_condition = view_condition_basis % (region.capitalize(), capitalized_id)
    context.addAction(id = action_id,
                      name = "Amortisation Details",
                      action = action_action,
                      condition = action_condition,
                      permission = view_permissions_basis,
                      category = "object_view",
                      visible=1)
    print("OK")

print()

return printed
