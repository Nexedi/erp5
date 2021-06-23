translateString = context.Base_translateString

portal = context.getPortalObject()

return [
  ("query_by", "portal_type"),
  ("base_query", {"parent_uid": [portal.person_module.getUid(),
                                 portal.organisation_module.getUid()]}),
  ("x_title", translateString("Portal Type")),
  ("title", translateString("Types from Person and Organisation module"))
]
