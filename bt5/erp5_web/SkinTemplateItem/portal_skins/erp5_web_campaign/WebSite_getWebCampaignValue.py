from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery


now = DateTime()

uid_list = [x.getUid() for x in context.portal_catalog(
  portal_type='Web Campaign',
  validation_state='published',
  start_date = SimpleQuery(start_date=now, comparison_operator='<='),
  stop_date = SimpleQuery(stop_date=now, comparison_operator='>=')
)]
if uid_list:
  # Returns a list of Web Campaign which a given web page is part of.
  web_campaign_list = context.portal_domains.searchPredicateList(
    context=context,
    uid=uid_list
  )

  if len(web_campaign_list)==1:
    return web_campaign_list[0]
