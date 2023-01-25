""" Return a list of sections from the tax type definition.

XXX this script is overkill, we could directly iterate on tax return line instead.
"""

tax_type_definition = context.portal_types[context.getPortalType()]

section_list = []
for tax_return_line in tax_type_definition.contentValues(
      portal_type='Tax Return Line',
      sort_on=('float_index',),):
  section_list.append(
    dict(section_title=tax_return_line.getTitle(),
         selection_params=dict(
           base_contribution_list=tax_return_line.getBaseContributionList(base=1),
           portal_type=tax_return_line.getPropertyList('line_portal_type'),
           delivery_portal_type=tax_return_line.getPropertyList('delivery_portal_type'),
           column_list=[item for item in enumerate(tax_return_line.getBaseContributionTranslatedTitleList())],
           multiplier=tax_return_line.getProperty('multiplier'),
           total_price=tax_return_line.getProperty('asset_price'),
           only_accountable=tax_return_line.getProperty('only_accountable'),
           journal_list=None,
         )))

return section_list
