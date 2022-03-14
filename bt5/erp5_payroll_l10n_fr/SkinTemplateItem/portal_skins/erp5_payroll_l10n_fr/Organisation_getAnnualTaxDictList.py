portal = context.getPortalObject()

# Annual taxes are only to declare in May or December
current_month = dsn_report.getEffectiveDate().month()
if current_month not in (5, 12):
  return []

annual_tax_list = []
tax_property_name_list = {
  'apprenticeship_fee_liability': ('001', '002'),
  'apprenticeship_supplementary_fee_liability': ('003', '004'),
  'construction_effort_fee_liability': ('005', '006'),
  'continuous_professional_training_fee_liability': ('007', '008'),
  'salary_fee_liability': ('009', '010'),
  'cvae_fee_liability': ('011', '012'),
  'continuous_short_term_professional_training_fee_liability': ('013', '014'),
}

year_start_date = DateTime(dsn_report.getEffectiveDate().year(), 1, 1)
year_stop_date = DateTime(dsn_report.getEffectiveDate().year(), 12, 31)

for tax, value_list in list(tax_property_name_list.items()):
  # CVAE is now out of DSN's scope, so always declare as not subjected
  # http://dsn-info.custhelp.com/app/answers/detail/a_id/1885
  if tax == 'cvae_fee_liability':
    is_subjected = False
  else:
    is_subjected = context.getProperty(tax, False)

  amount = 0.
  if is_subjected:
    amount = portal.portal_simulation.getInventory(
      node_uid=portal.account_module.remuneration_personnel.getUid(), # XXX: hardcoded
      from_date=year_start_date,
      at_date=year_stop_date,
      section_uid=context.getUid(),
      portal_type="Accounting Transaction Line",
      simulation_state=['stopped', 'delivered'],
    )
  annual_tax_list.append({
    'tax_code': (value_list[0] if is_subjected else value_list[1]),
    'amount': amount,
    })

return annual_tax_list


# TODO : calculate base values for salary fee in case the company is subjected
# (for codes 015, 016 and 017 of S21.G00.44.001)
