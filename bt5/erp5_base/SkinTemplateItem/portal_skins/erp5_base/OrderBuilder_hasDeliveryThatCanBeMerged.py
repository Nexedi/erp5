mergeable_delivery_list_list = context.getMergeableDeliveryListList()
if not mergeable_delivery_list_list:
  return ()
if fixit:
  context.OrderBuilder_mergeDeliveryList(mergeable_delivery_list_list)
return [context.Base_translateString(
  "The Following Deliveries can be merged ${delivery_list_list}",
  mapping={
    'delivery_list_list': str([[x.getRelativeUrl() for x in y] for y in mergeable_delivery_list_list])
  }
)]
