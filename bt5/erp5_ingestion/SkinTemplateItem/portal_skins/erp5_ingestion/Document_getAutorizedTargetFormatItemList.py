autorized_format_item_list = []
for format_item_list in context.getTargetFormatItemList():
  if context.Document_isTargetFormatPermitted(format_item_list[1]):
    autorized_format_item_list.append(format_item_list)
return autorized_format_item_list
