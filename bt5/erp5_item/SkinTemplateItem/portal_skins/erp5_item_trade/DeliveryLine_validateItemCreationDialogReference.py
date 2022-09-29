dialog = getattr(context, dialog_id)
if dialog.has_field('your_item_extra_property_list') and editor and len(request.get("field_listbox_reference_%s" % request.cell.uid))<=6:
  reference = "%s%s" % (request.get("field_your_prefix_reference"), request.get('field_listbox_reference_%s' % request.cell.uid).zfill(6))
  test_result = request.cell.Base_validateEan13Code(reference,request)

  if test_result ==True:
    request.form["field_listbox_reference_%s" % request.cell.uid] = reference
    request.set("field_listbox_reference_%s" % request.cell.uid,reference)
    result = [x.getObject() for x in context.portal_catalog(portal_type = request.get("field_your_type"),
              reference= reference)]
    if (result !=[] or test_result ==False ):
      return False
  elif test_result == False:
    return False
return True
