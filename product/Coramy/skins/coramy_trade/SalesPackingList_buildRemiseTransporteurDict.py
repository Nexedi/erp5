## Script (Python) "SalesPackingList_buildRemiseTransporteurDict"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
delivery_list = context.object_action_list(selection_name='sales_packing_list_selection')

# we sort the deliveries by source_section, transporteur, destination
RTDict = {}
for delivery in delivery_list :
  source_section = delivery.getSourceSectionTitle()
  if not source_section in RTDict.keys() :
    RTDict[source_section] = {}
  transporteur = delivery.getDeliveryMode()
  if not transporteur in RTDict[source_section].keys() :
    RTDict[source_section][transporteur] = {}
  destination = delivery.getDestination()
  if not destination in RTDict[source_section][transporteur].keys() :
    RTDict[source_section][transporteur][destination] = []
  
  RTDict[source_section][transporteur][destination].append(delivery)

return RTDict
