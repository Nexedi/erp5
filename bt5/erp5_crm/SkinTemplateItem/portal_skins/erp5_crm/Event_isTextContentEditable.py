"""
  Returns true if the text content of this Event is editable.

  The underlying idea is that once the content of an event has
  been placed in a MIME envelope and set as the default file
  of the Event, the event is considered as frozen and can not
  be modified.
"""
return getattr(context, 'hasFile', None) is not None and not context.hasFile() \
  and (context.getPortalType() != 'Mail Message' \
       or context.getSimulationState() not in ('started', 'stopped', 'delivered'))
