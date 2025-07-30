"""
This script returns the list of items based on the preferred
resources for events. It is intended to be used
by ListField instances.
"""
return context.Ticket_getResourceItemList(portal_type='Data Event')
