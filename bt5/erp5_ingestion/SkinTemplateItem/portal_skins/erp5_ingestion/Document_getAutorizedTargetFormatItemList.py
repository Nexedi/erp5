autorized_format_list = []
format_list = context.getTargetFormatItemList()
for format in format_list:
  if context.Document_isTargetFormatPermitted(format[1]):
   autorized_format_list.append(format)
return autorized_format_list
