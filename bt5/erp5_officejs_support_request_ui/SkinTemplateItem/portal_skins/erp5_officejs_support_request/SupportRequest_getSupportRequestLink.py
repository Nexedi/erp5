support_request_link = context.absolute_url()
hash_position = support_request_link.index('support_request_module')

new_support_request_link = support_request_link[:hash_position] + '#/' + support_request_link[hash_position:]

return new_support_request_link
