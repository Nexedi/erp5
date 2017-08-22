portal = context.getPortalObject()

# get the related Support Request, this should not be None
support_request_list = portal.portal_catalog(portal_type="Support Request", id=context.getId()) # with id keyword, this function will return a sequence data type which contains one element.

support_request_object = support_request_list[0].getObject()

support_request_link = context.absolute_url()
hash_position = support_request_link.index('support_request_module')

new_support_request_link = support_request_link[:hash_position] + '#/' + support_request_link[hash_position:]

return new_support_request_link
