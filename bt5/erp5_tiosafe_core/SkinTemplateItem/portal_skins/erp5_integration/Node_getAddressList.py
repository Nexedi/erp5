""" Retrieve the address list of the node. """

return context.contentValues(portal_type='Address',
                             sort_on='int_index')
