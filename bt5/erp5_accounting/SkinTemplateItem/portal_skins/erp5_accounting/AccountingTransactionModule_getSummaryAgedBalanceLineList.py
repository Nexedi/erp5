from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

line_list = []
detail_line_list = portal\
    .AccountingTransactionModule_getDetailedAgedBalanceLineList(
               at_date, section_category, section_category_strict,
               simulation_state, period_list, account_type, detail=False, **kw)

period_id_list = ['period_future']
for idx, _ in enumerate(period_list):
  period_id_list.append('period_%s' % idx)
period_id_list.append('period_%s' % (idx + 1))

# Initialize to something that will not be equals to 
# detail_line.mirror_section_uid below.
# In case we have used an account with mirror section,
# then mirror_section_uid will be None
previous_mirror_section_uid = -1

for detail_line in detail_line_list:
  if previous_mirror_section_uid != detail_line.mirror_section_uid:
    line = Object(uid='new_',
                  mirror_section_title=detail_line.mirror_section_title,
                  total_price=0)
    line_list.append(line)
    previous_mirror_section_uid = detail_line.mirror_section_uid
  line['total_price'] = detail_line.total_price + line['total_price']

  for period_id in period_id_list:
    previous_value = line.get(period_id, 0)
    added_value = detail_line.get(period_id, 0)
    new_value = previous_value + added_value
    if previous_value or new_value:
      line[period_id] = new_value

return line_list
