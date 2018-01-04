from Products.ZSQLCatalog.SQLCatalog import Query, NegatedQuery
configuration_dict = {'portal_type': ["Manufacturing Order", "Manufacturing Execution"]}
portal = context.getPortalObject()
if context.getPortalType() in portal.getPortalResourceTypeList():
  # only show production related to current resource
  delivery_uid_set = set()
  for line in portal.portal_catalog(portal_type="Manufacturing Execution Line",
                                    query=NegatedQuery(Query(simulation_state=["draft", "cancelled", "delivered"])),
                                    default_resource_uid=context.getUid(),
                                    select_dict={"parent_uid": None}):
    delivery_uid_set.add(line.parent_uid)
  # to make sure to filter even if nothing match
  delivery_uid_set.add(0)
  configuration_dict["delivery_uid_list"] = [x for x in delivery_uid_set]
return configuration_dict
