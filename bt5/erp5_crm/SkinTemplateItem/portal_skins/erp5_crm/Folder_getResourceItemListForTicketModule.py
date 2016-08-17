allowed_content_type_list = context.portal_types[context.getPortalType()].getTypeAllowedContentTypeList()

if allowed_content_type_list:
  return context.newContent(portal_type=allowed_content_type_list[0], temp_object=True).Ticket_getResourceItemList(
    include_context=include_context,
    empty_item=empty_item,
    indent_category=indent_category,
    indent_resource=indent_resource,
    compact=compact,
    empty_category=empty_category,
    use_relative_url=use_relative_url)
return []
