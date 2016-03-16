"""Returns the default sender for response events.

This script is here so that we can easily customized depending on the context event, ticket or user preferences.
"""

return context.Event_getPreferredResponseEventSourceItemList()[-1][1]
