builder_kw = {'activate_kw':{'tag':'build_amortisation_transaction'}}
applied_rule_list = []
if len(item_uid_list) > 0:
  item_value_list = [context.portal_catalog.getObject(uid) for uid in item_uid_list]
  for item_value in item_value_list:
    applied_rule = item_value.getCausalityRelatedValueList(portal_type='Applied Rule')
    if len(applied_rule) == 1:
      applied_rule_list.append(applied_rule[0])
  builder_kw['applied_rule_uid'] = [x.getUid() for x in applied_rule_list]
if at_date not in (None, 'None'):
  date_dict = {'query':[at_date],
               'range':'ngt'}
  builder_kw['stock.date'] = date_dict
if len(item_uid_list) > 0 and len(applied_rule_list) == 0:
  context.log('ERP5 Amortisation Build :','No applied rule to select for build with item_uid_list %s' % item_uid_list)
  return None
context.portal_deliveries.amortisation_transaction_builder.build(**builder_kw)
