if 'sort_on' in kw:
  del kw['sort_on']

return context.searchFolder(sort_on=[
    ('modification_date', 'descending'),
    # XXX to get stable test result, we also sort by start date (because modification date
    # has a one second precision)
    ('delivery.start_date', 'descending'),
    ], **kw)
