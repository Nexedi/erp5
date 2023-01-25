request = context.REQUEST
is_asynchronous_gadget = options.get('box', None) is None;

# determine parent_web_section_url
if is_asynchronous_gadget and \
   getattr(context, 'getWebSectionValue', None) is not None and \
   getattr(context, 'getDefaultDocumentValue', None) is not None:

  # current_web_section
  parent_web_section = context.restrictedTraverse(
                             request.get('parent_web_section_url', ''), None)
  if parent_web_section is not None and context.meta_type == 'ERP5 Form':
    current_web_section = parent_web_section
  else:
    current_web_section = context.getWebSectionValue()
  request.set('current_web_section', current_web_section)

  # current_web_document
  if request.get('current_web_document', None) is None:
    if context.getDefaultDocumentValue() is not None:
      current_web_document = context.getDefaultDocumentValue()
    else:
      current_web_document = context
    request.set('current_web_document', current_web_document)

  # is_web_section_default_document
  request.set('is_web_section_default_document',
              request.get('is_web_section_default_document', 0))
