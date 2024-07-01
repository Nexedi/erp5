# XXX Not updated, Immobilisation portal_type does not exist anymore
# but it has to update each delivery line and cell portal_type which
# has already such actions

# This script adds the needed actions in the Immobilisation portal_type, and
# each amortisable portal_type

def addAction(portal_type, portal_type_type, country, amortisation_method):
  print('Adding UI tab "Amortisation Details" for method %s on portal_type %s... ' % (amortisation_method,portal_type), end=' ')
  id = "%s_%s_amortisation_details_view" % (country, amortisation_method)
  if id in [x.id for x in portal_type.listActions()]:
    print("Already exists")
  else:
    if portal_type_type == "Immobilisation":
      action = "%s_Immobilisation_viewDetails" % amortisation_method
    else:
      action = "%s_Item_viewAmortisationDetails" % amortisation_method
    portal_type.addAction(id = id,
                          name = "Amortisation Details",
                          action = action,
                          condition = "object/IsUsing%s%sAmortisationMethod" % (
                                           country.capitalize(),
                                           "".join([x.capitalize() for x in amortisation_method.split('_')]) ),
                          permission = ('View',),
                          category = "object_view",
                          visible = 1)
    print("OK")
  return printed


if amortisation_method is None:
  return "No amortisation method specified"

tokens = amortisation_method.split('_')
if len(tokens) < 2:
  return "Bad amortisation method"

country = tokens[0]
amortisation_method = "".join(tokens[1:])

for portal_type in context.portal_types.objectValues():
  # Check if the portal_type is Immobilisation
  if portal_type.id == "Immobilisation":
    print(addAction(portal_type, "Immobilisation", country, amortisation_method), end=' ')
  else:
    # Check if the portal_type is amortisable
    if "immobilise" in [x.id for x in portal_type.listActions()]:
      print(addAction(portal_type, "Item", country, amortisation_method), end=' ')

return printed
