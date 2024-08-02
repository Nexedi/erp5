from Products.PythonScripts.standard import Object
request = container.REQUEST
portal = context.getPortalObject()
stool = portal.portal_simulation

person_value_list = portal.portal_categories.restrictedTraverse(
    node_category).getGroupRelatedValueList(portal_type='Person',
                                            checked_permission='View')

# for stat
total_time_per_resource = {}
total_time = 0

result_list = []

# guess the list of resource used in presences
presence_resource_uid_list = [inventory.resource_uid for inventory
     in stool.getInventoryList(
                          from_date=from_date,
                          to_date=to_date,
                          portal_type=('Presence Request Period',
                                       'Group Calendar Assignment'),
                          group_by_resource=1)]


for person in person_value_list:
  result_dict = {}
  person_total = 0

  person_planned_time = person.getAvailableTime(
                          from_date=from_date,
                          to_date=to_date,
                          resource=presence_resource_uid_list)

  for inventory in stool.getInventoryList(
                          from_date=from_date,
                          to_date=to_date,
                          node_uid=person.getUid(),
                          portal_type='Leave Request Period',
                          group_by_resource=1):

    resource = inventory.resource_relative_url or ''

    if inventory.resource_uid in presence_resource_uid_list:
      raise ValueError("This report does not work when same resource are"
                       " used in presence and leave.")

    person_time = (person_planned_time - person.getAvailableTime(
                      from_date=from_date,
                      to_date=to_date,
                      resource=presence_resource_uid_list +
                              [inventory.resource_uid] )) / 60. / 60.

    result_dict[resource] = person_time

    total_time_per_resource[resource] = \
        person_time + total_time_per_resource.get(resource, 0)

    person_total += person_time
    total_time += person_time


  result_list.append(
      Object(
        uid='new_0',
        person_title=person.getTitle(),
        person_career_reference=person.getCareerReference(),
        total=person_total,
        **result_dict))

result_list.sort(key=lambda r: (r.person_career_reference or '', r.person_title or ''))
request.set('total_time', total_time)
request.set('total_time_per_resource', total_time_per_resource)

return result_list
