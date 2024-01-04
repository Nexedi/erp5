def sortDiffObjectList(diff_object_list):
  return sorted(diff_object_list, key=lambda x: (x.object_state, x.object_class, x.object_id))

for diff_object in sortDiffObjectList(diff_object_list):
  print(("%s (%s) - %s" % (diff_object.object_state, diff_object.object_class, diff_object.object_id)))
  if getattr(diff_object, "error", None) is not None:
    if detailed:
      print(("  %s" % diff_object.error))
    print("")
  else:
    if detailed and getattr(diff_object, "data", None) is not None:
      print(("%s" % diff_object.data.lstrip()))
    print("")

return printed
