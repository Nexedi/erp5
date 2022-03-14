translate = context.Base_translateString

item_list = [("", "")] + [
  (translate(x), y) for x,y in [
    ("Draft", "draft"), ("Shared", "shared"), ("Released", "released"),
  ]
]

if context.getTypeBasedMethod('getPreferredAttachedDocumentPublicationState')() == "published":
  item_list.append((translate("Published"), "published"))

return item_list
