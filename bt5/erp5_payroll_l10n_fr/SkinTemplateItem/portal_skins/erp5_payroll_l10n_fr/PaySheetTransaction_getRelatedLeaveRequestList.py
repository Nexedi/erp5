from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
if context.getStartDate():
  return context.portal_catalog(
    portal_type= 'Leave Request',
    destination_uid=context.getSourceSectionUid(),
    query=ComplexQuery(
      Query(**{'range': 'nlt', 'delivery.start_date': context.getStartDate()}),
      Query(**{'range': 'ngt', 'delivery.start_date': context.getStopDate()}),
      logical_operator='AND')
  )
