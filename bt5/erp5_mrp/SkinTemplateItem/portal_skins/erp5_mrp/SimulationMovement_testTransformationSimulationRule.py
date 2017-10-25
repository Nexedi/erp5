specialise_list = context.getSpecialiseValueList(portal_type="Transformation")
if  (len(specialise_list) == 1 and
     context.getResource() == specialise_list[0].getResource()):
  parent = context.getParentValue()
  if parent.getSpecialiseValue().getPortalType() == "Delivery Simulation Rule":
    movement = context.getParentValue().getDeliveryValue()

    return movement is not None and movement.getPortalType() in (
      "Production Order Line", "Production Order Cell",
      "Manufacturing Order Line", "Manufacturing Order Cell")
