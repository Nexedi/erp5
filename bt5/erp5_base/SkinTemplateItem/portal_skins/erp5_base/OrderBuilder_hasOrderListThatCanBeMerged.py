mergeable_order_list_list = context.getMergeableDeliveryListList()
if not mergeable_order_list_list:
  return ()
if fixit:
  context.OrderBuilder_mergeOrderList(mergeable_order_list_list)
return [context.Base_translateString(
  "The Following Orders can be merged ${order_list_list}",
  mapping={
    'order_list_list': str([[x.getRelativeUrl() for x in y] for y in mergeable_order_list_list])
  }
)]
