#context = self
# vim: ts=2 sw=2 et

STRIP_IF_EMPTY = True
request = context.REQUEST
result = []
GAP = context.portal_categories.restrictedTraverse(request['gap_base'])
organisation_id = context.restrictedTraverse(request['organisation']).getUid()

# OOo specific variables
ooo_struct = dict (
		line = 8,
		rows = ('C','D'),
		)

def getAccountsForGap(gap_id):
  return GAP.restrictedTraverse(gap_id).getGapRelatedValueList(portal_type='Account')

def getUniqueGapList(accounts_list):
	return list(dict([ (x.getGap(),True) for x in accounts_list]).keys())

def getCell(row_number=1):
	return '%s%d'%(ooo_struct['rows'][row_number-1], ooo_struct['line'])

def addLine(n_type, text, level, value=None, formula=None, value2=None, formula2=None, schedule='X'):
#    if value == 0.0:
#        return
	if formula == '=':
		formula = 'N/A'
	if formula2 == '=':
		formula2 = 'N/A'
	result.append( dict(
		t=n_type,
		text='    '*level+(text),
		level=level,
		formula=formula,
		formula2=formula2,
		value=value,
		value2=value2,
		schedule=schedule
		)
		)
	ooo_struct['line'] = ooo_struct['line'] + 1

def addScheduleForAccounts(accounts_list, less_accounts_list, minus, detail_mode=False):
	tmp_list = []
	if detail_mode:
		getInventoryList = context.portal_simulation.getInventoryList
		for acc in accounts_list:
			transactions = getInventoryList(node_uid = acc.getUid(),
					section_uid= organisation_id,
					simulation_state=request['simulation_state'],
					at_date=request['at_date'],
					from_date=request['from_date'])
			for trans in transactions:
				trans = trans.getObject()
				parent = trans.getExplanationValue()
				tmp_list.append(
						dict(description=parent.getDescription() or 'No description given',
							title = parent.getTitle(),
							quantity =  trans.getQuantity()
							)
						)
		sort_tmp_list = [(x['description'],x) for x in tmp_list]
		sort_tmp_list.sort()
		tmp_list = [x[1] for x in sort_tmp_list]
	else:
		getInventory = context.portal_simulation.getInventory

		sign_fn = lambda x: x
		if minus:
			sign_fn = lambda x: -x

		for acc in accounts_list:
			inventory = getInventory(node_uid = acc.getUid(),
					section_uid= organisation_id,
					simulation_state=request['simulation_state'],
					at_date=request['at_date'],
					from_date=request['from_date'])
			tmp_list.append(
					dict(
						description=acc.getTitle(),
						title = '',
						quantity = sign_fn(inventory)
					)
					)

		for acc in less_accounts_list:
			inventory = getInventory(node_uid = acc.getUid(),
					section_uid= organisation_id,
					simulation_state=request['simulation_state'],
					at_date=request['at_date'],
					from_date=request['from_date'])
			tmp_list.append(
					dict(
						description="LESS: "+acc.getTitle(),
						title = '',
						quantity = inventory
					)
					)
			# for every mode:
	loop_dict['schedules'][loop_dict['schedule_index']] = tmp_list

# Don't break lines, it makes things unreadable
# Parameters:
#  t        : type of the node (section, sub or end)
#  gap      : list of concerned gap entries (summed up)
#  less_gap : list of gap to be substracted from the inventory (applied AFTER the minus flag interpretation)
#  sections : list of sub-nodes (only for section and sub)
# Flags:
#  minus : revert the sign
#  less  : substract from total
# detailed_schedule : list transactions instead of accounts balance
structure = (
    dict(title='SOURCE OF FUNDS',t='section',
      sections=(
        dict(title='Shareholders Funds',t='sub',
          sections=(
            dict(title='Capital',t='end', gap=['liability/capital'], less_gap=['asset/current/drawings'], minus=True, detailed_schedule=True),
            dict(title='Reserves and Surplus',t='end', gap=['liability/reserves_and_surplus'], minus=True),
            )
          ),
		dict(title='Deferred Tax Liability',t='end', gap=['liability/deferred_tax']),
          dict(title='Loan Funds',t='sub',
            sections=(
              dict(title='Secured Loans',t='end', gap=['liability/loans/secured_loans'], minus=True, detailed_schedule=True ),
              dict(title='Unsecured Loans',t='end', gap=['liability/loans/unsecured_loans'], minus=True),
              )
            )
          )
        ),
    dict(title='APPLICATION OF FUNDS',t='section',
      sections=(
        dict(title='Fixed Assets',t='sub',
          sections=(
            dict(title='Gross Block',t='end', gap=['asset/fixed/gross_block']),
#            dict(title='Depreciation',t='end', gap=['asset/fixed/depreciation'], less=True),
#            dict(title='Net Block',t='end', gap=['asset/fixed/net_block']),
            dict(title='Capital Work-in-Progress',t='end', gap=['asset/fixed/capital_work_in_progress']),
            )
          ),
        dict(title='Investments',t='end', gap=['asset/investment']),
        dict(title='Current Assets, Loans and Advances',t='sub',
          sections=(
            dict(title='Cash and Bank Balances',t='end',gap=['asset/current/bank_account','asset/current/cash_in_hand']),
            dict(title='Loans and Advances',t='end', gap=['asset/current/loans_and_advances','asset/current/deposits']),
            dict(title='Provisions',t='end', gap=['asset/current/provisions']),
            dict(title='Stock in Trade',t='end', gap=['asset/current/stock_in_trade']),
            dict(title='Sundry Debtors',t='end', gap=['asset/current/sundry_debtors']),
            dict(title='Current Liabilities',t='end', gap=['liability/current'],less=True, minus=True),
            dict(title='Current Provisions',t='end', gap=['liability/provisions'],less=True, minus=True),
            )
          ),
        dict(title='Miscellaneous Expenditure (To the extent not written off or adjusted)',t='sub',
          sections=(
            dict(title='Preliminary Expenses',t='end',gap=['asset/misc/preliminary']),
            dict(title='Profit and Loss',t='end',gap=['asset/misc/profit_and_loss']),
            )
          )
        )
      )
    )

loop_dict = dict(
		section_prefix = 'I',
		sub_prefix = 1,
		end_prefix = 'a',
		schedule_index = 'A',
		schedules = {}
		)

def do_section(item):
	addLine(item['t'],"%s. %s"%(loop_dict['section_prefix'],item['title']),loop_dict['level'])
	loop_dict['section_prefix'] = loop_dict['section_prefix'] + 'I'
	loop_dict['sub_prefix'] = 1
	loop_dict['bigtotal'] = []
	loop_dict['bigtotal2'] = []
	loop_dict['level'] =  loop_dict['level'] + 1
	for subitem in item['sections']:
		parse_structure(subitem)
	addLine('total','Total',loop_dict['level'],formula='='+(''.join(loop_dict['bigtotal'])), formula2='='+(''.join(loop_dict['bigtotal2'])))
	loop_dict['level'] =  loop_dict['level'] - 1

def do_end(item):
	local_accounts = []
	less_local_accounts = []
	for gap_id in item['gap']:
		local_accounts.extend( getAccountsForGap(gap_id) )
	inventory = context.FiscalReportCell_doGetInventory( getUniqueGapList(local_accounts),
			from_date=request['from_date'],at_date=request['at_date'],simulation_state=request['simulation_state'])
	inventory2 = context.FiscalReportCell_doGetInventory( getUniqueGapList(local_accounts),
			from_date=request['from_date2'],at_date=request['at_date2'],simulation_state=request['simulation_state'])
	# reverse the sign
	if 'minus' in item and inventory != 0.0:
		inventory = - inventory
		inventory2 = - inventory2
	# substract the sum of a list of gaps from the inventory
	if 'less_gap' in item:
		for gap_id in item['less_gap']:
			less_local_accounts.extend( getAccountsForGap(gap_id) )
		less_inventory = context.FiscalReportCell_doGetInventory( getUniqueGapList(less_local_accounts),
			from_date=request['from_date'],at_date=request['at_date'],simulation_state=request['simulation_state'])
		less_inventory2 = context.FiscalReportCell_doGetInventory( getUniqueGapList(less_local_accounts),
			from_date=request['from_date2'],at_date=request['at_date2'],simulation_state=request['simulation_state'])
		inventory = inventory - less_inventory
		inventory2 = inventory2 - less_inventory2
	if STRIP_IF_EMPTY and not local_accounts and not less_local_accounts:
		return
	if loop_dict['level'] == 1:
		end_title = "%d. %s"%(loop_dict['sub_prefix'], item['title'])
		loop_dict['sub_prefix'] = loop_dict['sub_prefix'] + 1
	else:
		end_title = "(%s) %s"%(loop_dict['end_prefix'],item['title'])
		loop_dict['end_prefix'] = chr(ord(loop_dict['end_prefix'])+1)
	# update the total
	if 'less' in item:
		loop_dict['total'].append( '-'+getCell() )
		loop_dict['total2'].append( '-'+getCell(2) )
		end_title = 'LESS: '+end_title
	else:
		loop_dict['total'].append( '+'+getCell() )
		loop_dict['total2'].append( '+'+getCell(2) )
	addLine(item['t'], end_title, loop_dict['level'], inventory, value2 = inventory2, schedule = loop_dict['schedule_index'])
	addScheduleForAccounts(local_accounts, less_local_accounts, 'minus' in item, 'detailed_schedule' in item)
	loop_dict['schedule_index'] = chr(ord(loop_dict['schedule_index'])+1)

def do_sub(item):
	addLine(item['t'],"%d. %s"%(loop_dict['sub_prefix'],item['title']),loop_dict['level'])
	loop_dict['sub_prefix'] = loop_dict['sub_prefix'] + 1
	loop_dict['end_prefix'] = 'a'
	loop_dict['total'] =  []
	loop_dict['total2'] =  []
	loop_dict['level'] =  loop_dict['level'] + 1
	for subitem in item['sections']:
		parse_structure(subitem)
	addLine('minitotal','',loop_dict['level'],formula='='+(''.join(loop_dict['total'])), formula2='='+(''.join(loop_dict['total2'])))
	loop_dict['bigtotal'].extend(loop_dict['total'])
	loop_dict['bigtotal2'].extend(loop_dict['total2'])
	loop_dict['level'] =  loop_dict['level'] - 1

handlers = dict(sub = do_sub, section = do_section, end = do_end)

def parse_structure(item):
	handlers[item['t']](item)

for item in structure:
	loop_dict['level'] = 0
	parse_structure(item)
#return '\n'.join(result)
return (result, loop_dict['schedules'])
