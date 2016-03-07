source = context.getSource()
destination = context.getDestinationSection()
context.log(source, destination)
if source is None or destination is None:
  return None

has_banknote = 0
has_coin = 0

for movement in context.getMovementList():
  resource_portal_type = movement.getResourceValue().getPortalType()
  if resource_portal_type == 'Coin':
    has_coin = 1
    break
  elif resource_portal_type == 'Banknote':
    has_banknote = 1
    break

if has_banknote == 1:
  if source.split("/")[-1] == destination.split("/")[-1] or "transit" not in source:
    destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis" % destination
  else:
    destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis_en_transit_allant_a/%s" % (destination, source.split("/")[-1])
elif has_coin == 1:
  destination = "%s/caveau/serre/encaisse_des_billets_neufs_non_emis" % destination
else:
  destination = None

return destination
