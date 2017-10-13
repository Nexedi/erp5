follow_up_object, = context.getPortalObject().portal_catalog(relative_url=follow_up, limit=1)
follow_up_object.edit()  # update modification date
result = context.PostModule_createHTMLPostFromText(
  follow_up,
  predecessor,
  data,
  file,
)
return result
