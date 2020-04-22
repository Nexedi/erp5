company_employees_number = kw.get('company_employees_number', 1)
next_transition = context.getNextTransition().getRelativeUrl()

if company_employees_number>1:
  # mark next transition  as multiple
  context.setMultiEntryTransition(next_transition, company_employees_number)
else:
  # explicitly reset next transition as not multiple because
  # we may have already set it as multiple
  context.setMultiEntryTransition(next_transition, 0)

# store globally
context.setGlobalConfigurationAttr(company_employees_number=company_employees_number)
