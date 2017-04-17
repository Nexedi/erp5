from Products.ERP5Type.DateUtils import getNumberOfDayInMonth

if context.getSourceAdministration() is None \
   or context.getEffectiveDate() is None \
   or context.getQuantity() is None \
   or len(context.getAggregateRelatedIdList()) <= 0:
  return context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "DSN can't be built if some fields are empty"))

portal = context.getPortalObject()
accounting_module = portal.getDefaultModuleValue("Pay Sheet Transaction")
getDSNBlockDict = context.DSNMonthlyReport_getDataDict
getEventDSNBlockDict = context.DSNEarlyRecoveryReport_getDataDict

def getLastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

# Gather data for DSN
declared_month = context.getEffectiveDate().month()
declared_year = context.getEffectiveDate().year()

# Get all paysheets for requested month
related_accounting_transaction_list = context.getAggregateRelatedValueList()
payment_transaction_list = sorted([transaction for transaction in related_accounting_transaction_list
                                   if transaction.getPortalType() == "Payment Transaction"], key=lambda x: x.getDestinationSectionTitle())
paysheet_list = sorted([transaction for transaction in related_accounting_transaction_list
                       if transaction.getPortalType() == "Pay Sheet Transaction"], key=lambda x: x.getTitle()) # Sorting for idempotent result in tests
paysheet_id_list =  [transaction.getId() for transaction in paysheet_list]

change_block_dict = context.DSNMonthlyReport_getChangeBlockDict()

organisation_contact = context.getSourceAdministrationValue()
establishment = accounting_module.restrictedTraverse(paysheet_id_list[0]).getDestinationSectionValue()
establishment_registration_code = ''.join(establishment.getCorporateRegistrationCode().split(' '))
# Finds the head office of the comany
organisation = payment_transaction_list[0].getSourceSectionValue()


# Variable containing all the record of the DSN
dsn_file = []
dsn_order = 1 # Increment for each DSN

# XXX: for the moment just use one of the payment transactions to retrieve
# the bank account. Later, a special accounting document should be provided
leave_period_dict = context.DSNMonthlyReport_getLeavePeriodDict(payment_transaction_list[0])
employee_list = []

# DSN HEADERS
dsn_file.append(getDSNBlockDict(block_id='S10.G00.00'))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.01', target=organisation))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.02', target=organisation_contact))

# Monthly DSN
dsn_file.append(getDSNBlockDict(block_id='S20.G00.05', year=declared_year, month=declared_month, order=dsn_order))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.06', target=organisation))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.11', target=establishment, manpower=len(paysheet_id_list)))
collective_contract = getDSNBlockDict(block_id='S21.G00.15')
if isinstance(collective_contract, list):
  dsn_file.extend(collective_contract)
else:
  dsn_file.append(collective_contract)

# Print aggregated cotisations
employee_result_list = [
  (paysheet.getSourceSectionValue().Person_getSocialDeclarationDataDict(context),
  paysheet.PaySheetTransaction_getSocialContributionDict())
  for paysheet in paysheet_list
]

employee_data_list, paysheet_data_list = zip(*employee_result_list)

# Generate aggregated contributions
aggregated_social_contribution_dict = {}
social_contribution_organisation = None
social_contribution_start_date = None
social_contribution_stop_date = None
for employee_result in paysheet_data_list:
  employee_ctp = employee_result['ctp']
  for ctp_code in employee_ctp:
    if social_contribution_organisation is None:
      social_contribution_organisation = employee_ctp[ctp_code]['corporate_registration_code']
      social_contribution_start_date = employee_ctp[ctp_code]['start_date']
      social_contribution_stop_date = employee_ctp[ctp_code]['stop_date']
    if ctp_code not in aggregated_social_contribution_dict:
      aggregated_social_contribution_dict[ctp_code] = employee_ctp[ctp_code].copy()
    else:
      aggregated_social_contribution_dict[ctp_code]['base'] = \
        aggregated_social_contribution_dict[ctp_code]['base'] + employee_ctp[ctp_code]['base']

# Find the payment transaction for the social contributions
for payment in payment_transaction_list:
  if payment.getDestinationSectionValue().getCorporateRegistrationCode() == social_contribution_organisation:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.20',
                                    target=payment,
                                    corporate_registration_code=social_contribution_organisation,
                                    establishment=establishment))
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.22',
                                    target=payment,
                                    corporate_registration_code=social_contribution_organisation,
                                    establishment=establishment,
                                    start_date=social_contribution_start_date,
                                    stop_date=social_contribution_stop_date))
    for ctp_code in aggregated_social_contribution_dict:
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.23',
                                      target=aggregated_social_contribution_dict[ctp_code]))
  else:
    corporate_registration_code = payment.getDestinationSectionValue().getCorporateRegistrationCode()
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.20',
                                    target=payment,
                                    corporate_registration_code=corporate_registration_code,
                                    establishment=establishment))
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.55', target=payment, establishment=establishment))

for employee_data_dict, paysheet_data_dict in employee_result_list:
  enrollment_record = employee_data_dict['enrollment_record']
  employee = employee_data_dict['person_relative_url']
  employee_list.append(employee)

  dsn_file.append(employee_data_dict['person'])
  
  change_block_dict = context.DSNMonthlyReport_getChangeBlockDict()

  contract_change_block_list = []
  if employee in change_block_dict:
    for rubric_root, change_date_block in change_block_dict[employee].iteritems():
      if rubric_root == 'S21.G00.31':
        for date, change_block in change_date_block.iteritems():
          dsn_file.append(getDSNBlockDict(block_id=rubric_root, change_block=change_block, change_date=date)) 
      elif rubric_root == 'S21.G00.41':
        for date, change_block in change_date_block.iteritems():
          contract_change_block_list.append(getDSNBlockDict(block_id=rubric_root, change_block=change_block, change_date=date))

  employee_data_dict['contract']['S21.G00.40.019'] = establishment_registration_code
  dsn_file.append(employee_data_dict['contract'])
  dsn_file.extend(contract_change_block_list)

  if employee in leave_period_dict:
    for leave_period in leave_period_dict[employee]:
      leave_block = {rubric: leave_period.get(rubric, None) 
                      for rubric in ('S21.G00.60.001',
                                     'S21.G00.60.002',
                                     'S21.G00.60.003',
                                     'S21.G00.60.010',
                                     'S21.G00.60.011',
                                     'S21.G00.60.012')}
      dsn_file.append(leave_block)

  death_insurance_contract = getDSNBlockDict(block_id='S21.G00.70', enrollment_record=enrollment_record)
  if isinstance(death_insurance_contract, list):
    dsn_file.extend(death_insurance_contract)
  else:
    dsn_file.append(death_insurance_contract)

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.71', enrollment_record=enrollment_record))

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.50',
                                  net_salary=paysheet_data_dict['net_salary'],
                                  net_taxable_salary=paysheet_data_dict['net_taxable_salary']))

  for remuneration_block in paysheet_data_dict['remuneration']:
    dsn_file.append(remuneration_block)

  for bonus_category in paysheet_data_dict['other_bonus'].itervalues():
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.52', target=bonus_category))

  for bonus_category in paysheet_data_dict['other_income'].itervalues():
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.54', target=bonus_category))

  for taxable_base_category in paysheet_data_dict['taxable_base'].itervalues():
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.78', target=taxable_base_category))
    if taxable_base_category['code'] == '02': # Assiette Brute plafonnee
      if ('063', '') in paysheet_data_dict['individual_contribution']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('063', '')]))
        del paysheet_data_dict['individual_contribution'][('063', '')]
      if taxable_base_category['code'] == '03': # Assiette Brute deplafonnee
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.79', target=paysheet_data_dict['taxable_base_component'][('01', '')]))
        del paysheet_data_dict['taxable_base_component'][('01', '')]
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('018', '')]))
        del paysheet_data_dict['individual_contribution'][('018', '')]

    if taxable_base_category['code'] == '03': # Assiette Brute deplafonnee
      if ('03', '') in paysheet_data_dict['taxable_base_component']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.79', target=paysheet_data_dict['taxable_base_component'][('03', '')]))
        del paysheet_data_dict['taxable_base_component'][('03', '')]
      if ('064', '') in paysheet_data_dict['individual_contribution']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('064', '')]))
        del paysheet_data_dict['individual_contribution'][('064', '')]

      if ('226', '') in paysheet_data_dict['individual_contribution']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('226', '')]))
        del paysheet_data_dict['individual_contribution'][('226', '')]

    if taxable_base_category['code'] == '31':
      for related_component_code in ('11', '13', '20'):
        if (related_component_code, taxable_base_category['contract_id']) not in paysheet_data_dict['taxable_base_component']:
          continue
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.79', target=paysheet_data_dict['taxable_base_component'][(related_component_code, taxable_base_category['contract_id'])], pay_sheet_transaction=paysheet_data_dict['pay_sheet_transaction']))
        del paysheet_data_dict['taxable_base_component'][(related_component_code, taxable_base_category['contract_id'])]
      if ('059', taxable_base_category['contract_id']) in paysheet_data_dict['individual_contribution']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('059', taxable_base_category['contract_id'])]))
        del paysheet_data_dict['individual_contribution'][('059', taxable_base_category['contract_id'])]

  for taxable_base_component_category in paysheet_data_dict['taxable_base_component'].itervalues():
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.79', target=taxable_base_component_category))
    if ('03', '') in taxable_base_component_category:
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=paysheet_data_dict['individual_contribution'][('064', '')]))
      del paysheet_data_dict['individual_contribution'][('064', '')]

  for individual_contribution_category in paysheet_data_dict['individual_contribution'].itervalues():
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.81', target=individual_contribution_category))

  dsn_file.append(employee_data_dict['seniority'])

# Add leave event DSN if needed
last_date_of_month = getLastDateOfMonth(context.getEffectiveDate())
first_date_of_month = DateTime(context.getEffectiveDate().year(),
                               context.getEffectiveDate().month(),
                               1)

if len(leave_period_dict):
  for employee in leave_period_dict:
    for period in leave_period_dict[employee]:
      leave_date_as_string = period['S21.G00.60.002']
      year = int(leave_date_as_string[4:])
      month = int(leave_date_as_string[2:4])
      day = int(leave_date_as_string[:2])
      leave_date = DateTime(year, month, day)
      if leave_date < first_date_of_month:
        continue
      if employee in employee_list:
        dsn_order += 1
        employee = portal.restrictedTraverse(employee)
        dsn_file.append(getEventDSNBlockDict(block_id='S20.G00.05', dsn_type='04', order=dsn_order)) #'04' is DSN Leave Event
        dsn_file.append(getEventDSNBlockDict(block_id='S20.G00.07', target=organisation_contact))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.06', target=organisation))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.11', target=establishment))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.30', target=employee))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.40', target=employee.getDefaultCareerValue()))
        dsn_file.append(period)

# Print DSN Record
last_block = ''
rubric_counter = 0

# DEBUG MODE
# 
# for block in dsn_file:
#   for rubric in sorted(block.keys()):
#     if block[rubric]:
#       if rubric[:10] != last_block:
#         print
#         last_block = rubric[:10]
#       print "%s,'%s'" % (rubric, block[rubric])
# return printed

dsn_report_string = ""

# NORMAL MODE
for block in dsn_file:
  for rubric in sorted(block):
    if block[rubric]:
      rubric_counter += 1
      dsn_report_string += "%s,'%s'\n" % (rubric, block[rubric])

# Footer block
footer = getDSNBlockDict(block_id='S90.G00.90', length=rubric_counter, dsn_record_counter=dsn_order)
for rubric in sorted(footer.keys()):
  dsn_report_string += "%s,'%s'\n" % (rubric, footer[rubric])

context.setTextContent(dsn_report_string.strip())

if batch_mode:
  # Set charset for response
  context.REQUEST.response.setHeader("Content-Type", "text/plain; charset=iso-8859-1")
  return

context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "Monthly DSN Record Created."))
