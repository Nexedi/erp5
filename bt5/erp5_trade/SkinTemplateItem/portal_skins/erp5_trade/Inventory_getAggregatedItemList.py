from DateTime import DateTime
def sorted(seq):
  seq = seq[:]
  seq.sort()
  return seq

portal = context.getPortalObject()
request = portal.REQUEST

if not at_date:
  at_date=DateTime()

brain = context

tracking_parameters = dict(
    node_uid=brain.node_uid,
    resource_uid=brain.resource_uid,
    at_date=at_date,
    )

result_list = []

if context.getVariationCategoryList():
  tracking_parameters['variation_text'] = brain.variation_text


for tracking_brain in portal.portal_simulation.getCurrentTrackingList(
                            **tracking_parameters):
  item = tracking_brain.getObject()
 
  item_dict = "%s : %s"% ( item.getReference(),
                           item.getQuantity(at_date=at_date) )
  result_list.append(item_dict)

return sorted(result_list)
