for base_contribution in context.getBaseContributionList():
  if base_contribution.startswith('base_amount/payroll/report_section'):
    return context.portal_categories.restrictedTraverse(base_contribution).getTitle()
return context.getSourceSectionTitle()
