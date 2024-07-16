from Products.PythonScripts.standard import html_quote
import six
portal = context.getPortalObject()
skin_folder = portal.portal_skins[original_skin_name]
new_skin_folder = portal.portal_skins[new_skin_name]

output_list = ["""<html><head><style>
table { border-collapse: collapse; }
th, td { border: 1px solid gray; padding: 0 .3em; }
</style></head><body>"""]
output_append = output_list.append
for original_form in skin_folder.objectValues():
  if original_form.meta_type in ('ERP5 Form', 'ERP5 Report') and \
     not original_form.getId().endswith('FieldLibrary'):
    new_form = new_skin_folder[original_form.id]
    for original_field in original_form.objectValues():
      try:
        new_field = new_form[original_field.id]
      except KeyError:
        output_append("<p>Missing %s in %s</p>" % (original_field.id, new_form.id))
        continue
      try:
        new_value_dict, new_value_tales = portal.Base_getFieldData(new_field)
      except AttributeError:
        output_append("<p>Dead proxy field %s %s</p>" % (original_field.id, new_form.id))
        continue

      original_value_dict, original_value_tales = portal.Base_getFieldData(
        original_field)
      if original_value_dict == new_value_dict and \
         original_value_tales == new_value_tales:
        continue

      output_append("<p>%s/%s<blockquote><table><tr><th>name</th>"
        "<th><a href='%s/manage_main'>old</a></th>"
        "<th><a href='%s/manage_main'>new</a></th>"
        "</tr>" % (
          new_form.id, new_field.id,
          original_field.absolute_url(), new_field.absolute_url()))

      output_list += ("<tr><td>%s</td></tr>" % "</td><td>".join(
            map(html_quote, ('[%s]' % key if T else key, str(old), str(new[key]))))
        for T, old, new in ((0, original_value_dict, new_value_dict),
                            (1, original_value_tales, new_value_tales))
        for key, old in six.iteritems(old)
        if old != new[key])

      output_append("</table></blockquote><p>")

output_append("Finished<br>")
output_append("  </body>")
output_append("</html>")
return "\n".join(output_list)
