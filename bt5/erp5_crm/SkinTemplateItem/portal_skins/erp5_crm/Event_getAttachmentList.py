# Get the list of attachments
portal_type_list = ('PDF', 'Image',)

aggregate_list = context.getAggregateValueList(
   portal_type=portal_type_list)

sub_document_list = [x.getObject() for x in context.searchFolder(
   portal_type=portal_type_list)]

return aggregate_list + sub_document_list
