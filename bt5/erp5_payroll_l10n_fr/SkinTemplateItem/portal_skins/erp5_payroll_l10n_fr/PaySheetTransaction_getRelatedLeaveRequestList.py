if context.getStartDate():
  return context.portal_catalog(
    portal_type= 'Leave Request',
    destination_uid=context.getSourceSectionUid(),
    **{'delivery.start_date': {'range': 'minngt', "query": (
      context.getStartDate(), context.getStopDate())}})
