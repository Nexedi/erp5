'''Returns budget cells matching an accounting transaction line.
'''
portal = context.getPortalObject()

def makeContext(doc, **kw):
  categories = []
  for k, v in kw.items():
    if v:
      categories.append('%s/%s' % (k,v))
  return doc.asContext(categories=categories)

financial_section = ''
budget_section = ''
group = ''

if context.AccountingTransaction_isSourceView():
  node = context.getSourceValue()
  if node is not None:
    financial_section = node.getFinancialSection()
    budget_section = node.getBudgetSection()
  section = context.getSourceSectionValue()
  if section is not None:
    group = section.getGroup()

  tmp_context = makeContext(
       context,
       region=context.getSourceRegion(),
       ## XXX or destination region ? this means the budget configuration has
       # to be known at that point.
       source_section=context.getDestinationSection(),
       destination_section=context.getSourceSection(),
       source=context.getDestination(),
       destination=context.getSource(),
       resource=context.getResource(),
       financial_section=financial_section,
       budget_section=budget_section,
       group=group,
  )
else:
  node = context.getDestinationValue()
  if node is not None:
    financial_section = node.getFinancialSection()
    budget_section = node.getBudgetSection()
  section = context.getDestinationSectionValue()
  if section is not None:
    group = section.getGroup()

  tmp_context = makeContext(
       context,
       region=context.getDestinationRegion(), #XXX
       destination_section=context.getSourceSection(),
       source_section=context.getDestinationSection(),
       destination=context.getDestination(),
       source=context.getSource(),
       resource=context.getResource(),
       financial_section=financial_section,
       budget_section=budget_section,
       group=group,
 )

return portal.portal_domains.searchPredicateList(context=tmp_context, portal_type='Budget Cell')
