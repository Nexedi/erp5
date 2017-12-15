portal = context.getPortalObject()
# We must copy these properties as they are retrieved from data
content_dict = context.getPropertyDictFromContent()
content_dict['title'] = context.getTitle()
content_dict['text_content'] = context.getTextContent()
content_dict['content_type'] = context.getContentType()
content_dict['data'] = None
# we may have specified (i.e. user input) source and destination
content_dict['destination_list'] = content_dict.get('destination_list', []) + \
                                     [x.getRelativeUrl() for x in context.getDestinationValueList() \
                                       if x.getRelativeUrl() not in content_dict.get('destination_list', [])]
content_dict['source_list'] = content_dict.get('source_list', []) + \
                                     [x.getRelativeUrl() for x in context.getSourceValueList() \
                                       if x.getRelativeUrl() not in content_dict.get('source_list', [])]
context.edit(**content_dict)
# reset reference
context.Event_generateReference()
# remove aggregates which are not attachments (ie: interface_post objects)
document_type_list = portal.getPortalEmbeddedDocumentTypeList() + portal.getPortalDocumentTypeList()
attachment_list = context.getAggregateList(portal_type=document_type_list)
context.setAggregateList(attachment_list)
