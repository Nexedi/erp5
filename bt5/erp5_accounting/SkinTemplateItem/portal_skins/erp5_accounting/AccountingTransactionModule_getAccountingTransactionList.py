portal = context.getPortalObject()
getUid = portal.portal_categories.getCategoryUid

section_category = params.pop('section_category', None)
section_category_strict = params.pop('section_category_strict', None)
params['accounting_transaction.section_uid'] = ''
if section_category:
  params['accounting_transaction.section_uid'] = portal.Base_getSectionUidListForSectionCategory(
                                   section_category, strict_membership=section_category_strict)
  currency = portal.Base_getCurrencyForSectionCategory(section_category, section_category_strict)
  precision = portal.account_module.getQuantityPrecisionFromResource(currency)
  portal.REQUEST.set('precision', precision)

# rewrite payment_mode_relative_url to uid
payment_mode_relative_url = params.pop('payment_mode_relative_url', None)
if payment_mode_relative_url:
  params['default_payment_mode_uid'] = \
    portal.portal_categories.payment_mode.getCategoryUid(payment_mode_relative_url)

# rewrite currency to uid
resource = params.pop('resource', None)
if resource:
  params['accounting_transaction.resource_uid'] = getUid(resource)


# XXX wrong name compat
# TODO: make it better on search dialog
node_list = params.pop('node', None)
if node_list:
  params['accounting_transaction_line_node_uid'] = [
      getUid(node) for node in node_list]

entity = params.pop('entity', None)
if entity:
  params['accounting_transaction.mirror_section_uid'] = getUid(entity)

if not params.get('operation_date'):
  params.pop('from_date', None)
  params.pop('to_date', None)
  if from_date or to_date:
    if from_date:
      if to_date:
        params['operation_date'] = dict(
                    query=(from_date, to_date),
                    range='minngt')
      else:
        params['operation_date'] = dict(
                    query=(from_date, ),
                    range='min')
    else:
      params['operation_date'] = dict(
                  query=(to_date, ),
                  range='ngt')

amount = params.pop('amount', '')
if amount not in (None, ''):
  params['accounting_transaction_line_total_price'] = amount
else:
  amount_range_min = params.pop('amount_range_min', None)
  amount_range_max = params.pop('amount_range_max', None)
  if amount_range_min or amount_range_max:
    if amount_range_min:
      if amount_range_max:
        params['accounting_transaction_line_total_price'] = dict(
                    query=(amount_range_min, amount_range_max),
                    range='minmax')
      else:
        params['accounting_transaction_line_total_price'] = dict(
                    query=(amount_range_min, ),
                    range='min')
    else:
      params['accounting_transaction_line_total_price'] = dict(
                  query=(amount_range_max, ),
                  range='max')


creation_date_range_min = params.pop('creation_date_range_min', None)
creation_date_range_max = params.pop('creation_date_range_max', None)
if creation_date_range_min or creation_date_range_max:
  if creation_date_range_min:
    if creation_date_range_max:
      params['creation_date'] = dict(
                  query=(creation_date_range_min, creation_date_range_max),
                  range='minmax')
    else:
      params['creation_date'] = dict(
                  query=(creation_date_range_min, ),
                  range='min')
  else:
    params['creation_date'] = dict(
                query=(creation_date_range_max, ),
                range='max')

select_dict = params.get('select_dict') or {}
select_dict['total_debit'] = None
select_dict['total_credit'] = None
# XXX: force mapping of reference column to catalog, to take advantage of (portal_type, reference) index.
# Without this, ColumnMapper would choose to use accounting_transaction.reference, because a lot of
# columns from that table are used. But it does not realise there is no portal_type column *and*
# a (portal_type, reference) index exists on catalog.
select_dict['reference'] = 'catalog.reference'
select_dict['specific_reference'] = None
select_dict['project_uid'] = None
select_dict['payment_uid'] = None
select_dict['mirror_section_uid'] = None
select_dict['operation_date'] = None
params['select_dict'] = select_dict

# We group by uid to really filter duplicated lines, but this makes generated
# query much slower, and in reality duplicated lines are transactions for which
# both source section and destination section match the criterions. This can be
# because there are no criterion on section_uid or because both sections are members
# of the selected group. In the later it can be accepted as not a problem.
if not params.get('accounting_transaction.section_uid'):
  params.setdefault('group_by', ('uid',))

if stat:
  return context.countFolder(**params)
return context.searchFolder(**params)
