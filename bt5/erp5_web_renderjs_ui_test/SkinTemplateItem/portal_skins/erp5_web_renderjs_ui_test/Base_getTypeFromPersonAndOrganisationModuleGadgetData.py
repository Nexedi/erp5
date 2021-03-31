translateString = context.Base_translateString

portal = context.getPortalObject()

return [
  ("query_by", "portal_type"),
  ("base_query", "parent_uid:=%s OR parent_uid:=%s" % (portal.person_module.getUid(),
                                                        portal.organisation_module.getUid())),
  ("title", translateString("Portal Type")),
  ("graph_title", translateString("Types from Person and Organisation module"))
]
