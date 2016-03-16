""" Retrieve the arrow list of the transaction. """
transaction = context.getObject()

sub = context.restrictedTraverse(context_document)
while sub.getParentValue().getPortalType() !=  "Synchronization Tool":
  sub = sub.getParentValue()

im = sub.Base_getRelatedObjectList(portal_type='Integration Module')[0].getObject()
org_module = im.getParentValue().organisation_module
org_pub = org_module.getSourceSectionValue()
person_module = im.getParentValue().person_module
person_pub = person_module.getSourceSectionValue()

# contains the result list
result_list = []

# set arrow list
arrow_list = [
    ['getSource', 'getDestination', ""],
    ['getSourceAdministration', 'getDestinationAdministration', 'Administration'],
    ['getSourceCarrier', 'getDestinationCarrier', 'Carrier'],
    ['getSourceDecision', 'getDestinationDecision', 'Decision'],
    ['getSourceSection', 'getDestinationSection', 'Ownership'],
    ['getSourcePayment', 'getDestinationPayment', 'Payment'],
]

# browse and add the arrows if exists a source or a destination
for get_source, get_destination, category in arrow_list:
  source_free_text = getattr(transaction, "%sFreeText" %get_source)(None)
  source = getattr(transaction, "%sValue" %get_source)(None)
  destination_free_text = getattr(transaction, "%sFreeText" %get_destination)(None)
  destination = getattr(transaction, "%sValue" %get_destination)(None)

  if source is not None or destination is not None:
    arrow_dict = {'source': None, 'destination': None, 'category': category}
  else:
    continue

  if source_free_text is not None:
    arrow_dict['source'] = source_free_text
  elif source is not None:
    if source.getPortalType() == "Person":
      arrow_dict['source'] = person_pub.getGidFromObject(object=source, encoded=False)
    else:
      arrow_dict['source'] = org_pub.getGidFromObject(object=source, encoded=False)

  if destination_free_text is not None:
    arrow_dict['destination'] = destination_free_text
  elif destination is not None:
    if destination.getPortalType() == "Person":
      arrow_dict['destination'] = person_pub.getGidFromObject(object=destination, encoded=False)
    else:
      arrow_dict['destination'] = org_pub.getGidFromObject(object=destination, encoded=False)

  result_list.append(arrow_dict)

return result_list
