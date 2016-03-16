skin_folder = getattr(context.portal_skins, original_skin_name)
new_skin_folder = getattr(context.portal_skins, new_skin_name)

output_list = []
output_append = output_list.append
output_append("<html>")
output_append("  <body>")
for original_form in skin_folder.objectValues():
  if (original_form.meta_type=='ERP5 Form' or original_form.meta_type=='ERP5 Report') and not original_form.getId().endswith('FieldLibrary'):
    new_form = getattr(new_skin_folder, original_form.id)
    for original_field in original_form.objectValues():
      new_field = getattr(new_form, original_field.id, None)
      if new_field is None:
        output_append("Missing %s in %s" % (original_field.id, new_form))

      else:

        original_value_dict, original_value_tales = context.Base_getFieldData(original_field)

        try:
          new_value_dict, new_value_tales = context.Base_getFieldData(new_field)
        except AttributeError:
          new_value_dict = new_value_tales = None
          output_append("Dead proxy field %s %s" % (original_field.id, new_form))

        if new_value_dict is not None:

          if (original_value_dict != new_value_dict) or \
            (original_value_tales != new_value_tales):

            output_append("%s %s <a href='%s'>old</a> <a href='%s'>new</a>" % (
                new_form.id, new_field.id,
                original_field.absolute_url() + '/manage_main',
                new_field.absolute_url() + '/manage_main'))
            output_append("<blockquote><ul>")


            for key, original_value in original_value_dict.items():
              if original_value != new_value_dict[key]:
                output_append("  <li>" + key + ' Origin: %s ' % original_value \
                              + ' New: %s</li>' % new_value_dict[key])

            for key, original_value in original_value_tales.items():
              if original_value != new_value_tales[key]:
                output_append("  <li>" + key + ' Origin: %s ' % original_value \
                              + ' New: %s<br></li>' % new_value_tales[key])
            output_append("</ul></blockquote>")

output_append("Finished<br>")
output_append("  </body>")
output_append("</html>")
return "\n".join(output_list)
