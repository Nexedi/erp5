translateString = context.Base_translateString

portal = context.getPortalObject()

return [
  ("query_by", {"parent_uid": [portal.person_module.getUid(),
                               portal.organisation_module.getUid()]}),
  ("layout", {
    "x": {
      "title": translateString("Portal Type"),
      "key": "portal_type"
    },
    "y": {
      "title": translateString("Quantity")
    }
  }),
  ("title", translateString("Types from Person and Organisation module"))
]
