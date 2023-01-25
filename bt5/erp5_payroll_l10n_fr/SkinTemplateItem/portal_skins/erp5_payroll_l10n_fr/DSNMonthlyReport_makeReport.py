from erp5.component.module.DateUtils import addToDate, getNumberOfDayInMonth

if context.getSourceAdministration() is None \
   or context.getEffectiveDate() is None \
   or context.getQuantity() is None:
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

last_date_of_month = getLastDateOfMonth(context.getEffectiveDate())
first_date_of_month = DateTime(context.getEffectiveDate().year(),
                               context.getEffectiveDate().month(),
                               1)

# Get all paysheets for requested month
related_accounting_transaction_list = context.getAggregateRelatedValueList()
payment_transaction_list = sorted([transaction for transaction in related_accounting_transaction_list
                                   if transaction.getPortalType() == "Payment Transaction"], key=lambda x: x.getDestinationSectionTitle())
paysheet_list = sorted([transaction for transaction in related_accounting_transaction_list
                       if transaction.getPortalType() == "Pay Sheet Transaction"], key=lambda x: x.getTitle()) # Sorting for idempotent result in tests
paysheet_id_list =  [transaction.getId() for transaction in paysheet_list]

change_block_dict = context.DSNMonthlyReport_getChangeBlockDict()

organisation_contact = context.getSourceAdministrationValue()
if len(paysheet_list):
  establishment = accounting_module.restrictedTraverse(paysheet_id_list[0]).getDestinationTradeValue()
else:
  establishment = context.getSourceTradeValue()
establishment_registration_code = ''.join(establishment.getCorporateRegistrationCode().split(' '))

# Finds the head office of the comany
if len(payment_transaction_list):
  organisation = payment_transaction_list[0].getSourceSectionValue()
elif len(paysheet_list):
  organisation = paysheet_list[0].getDestinationSectionValue()
else:
  organisation = context.getSourceSectionValue()


# Variable containing all the record of the DSN
dsn_file = []
nb_dsn = 1 # Increment for each DSN

# XXX: for the moment just use one of the payment transactions to retrieve
# the bank account. Later, a special accounting document should be provided
if len(payment_transaction_list):
  bank_account = payment_transaction_list[0].getSourcePaymentValue()
else:
  bank_account, = [bank_account for bank_account
                   in organisation.objectValues(portal_type='Bank Account')
                   if bank_account.getValidationState() == 'validated']
leave_period_dict = context.DSNMonthlyReport_getLeavePeriodDict(bank_account)
employee_list = []
leaving_employee_list = []

# DSN HEADERS
dsn_type = ('01' if len(paysheet_list) else '02')
dsn_file.append(getDSNBlockDict(block_id='S10.G00.00', type=dsn_type))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.01', target=organisation))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.02', target=organisation_contact))

# Monthly DSN
dsn_file.append(getDSNBlockDict(block_id='S20.G00.05', year=declared_year, month=declared_month, order=nb_dsn, type=dsn_type))

# empty DSN
if dsn_type == '02':
  dsn_file.append(getDSNBlockDict(block_id='S10.G00.08', target=organisation_contact))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.06', target=organisation))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.11', target=establishment, manpower=len(paysheet_id_list)))
collective_contract = getDSNBlockDict(block_id='S21.G00.15')

# Print aggregated cotisations
employee_result_list = [
  (paysheet.getSourceSectionValue().Person_getSocialDeclarationDataDict(context),
  paysheet.PaySheetTransaction_getSocialContributionDict())
  for paysheet in paysheet_list
]

if len(employee_result_list):
  employee_data_list, paysheet_data_list = zip(*employee_result_list)
else:
  employee_data_list, paysheet_data_list = [], []

insurance_contract_id_list = set()
for employee_data_dict, paysheet_data_dict in employee_result_list:
  insurance_contract_id_list.update(set([x[1] for x in paysheet_data_dict['taxable_base']]))

collective_contract_list = getDSNBlockDict(block_id='S21.G00.15')
for collective_contract in collective_contract_list:
  if collective_contract['S21.G00.15.005'] in insurance_contract_id_list:
    dsn_file.append(collective_contract)

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
      for summing_parameter in ('base', 'quantity'):
        aggregated_social_contribution_dict[ctp_code][summing_parameter] = \
          aggregated_social_contribution_dict[ctp_code][summing_parameter] + employee_ctp[ctp_code][summing_parameter]

# Find the payment transaction for the social contributions
if len(payment_transaction_list):
  for payment in payment_transaction_list:
    corporate_registration_code = payment.getDestinationSectionValue().getCorporateRegistrationCode()
    if corporate_registration_code == social_contribution_organisation.getCorporateRegistrationCode():
      if establishment.isQuaterlyPayment():
        amount_list = []
        for i in range(3):
          start_date = addToDate(first_date_of_month, month=-i)
          stop_date = getLastDateOfMonth(addToDate(first_date_of_month, month=-i)) + 1
          amount = -1. * portal.portal_simulation.getInventory(
            from_date=start_date,
            to_date=stop_date,
            section_uid=organisation.getUid(),
            mirror_section_uid=social_contribution_organisation.getUid(),
            node_uid=portal.account_module['securite_sociale'].getUid(),
            ledger_uid=portal.portal_categories.ledger.accounting.general.getUid(),
            parent_portal_type='Accounting Transaction',
          )
          amount_list.append(amount)
          dsn_file.append(getDSNBlockDict(block_id='S21.G00.20',
                                          target=payment,
                                          corporate_registration_code=social_contribution_organisation.getCorporateRegistrationCode(),
                                          first_date_of_month=start_date,
                                          last_date_of_month=getLastDateOfMonth(start_date),
                                          establishment=establishment,
                                          payer=establishment,
                                          amount=amount_list[-1]))
        # Let's check that difference is < 1 cts
        assert sum(amount_list) - payment.AccountingTransactionLine_statSourceDebit() * 100 < 1, 'Error, URSSAF Amount to Pay for each month is different for URSSAF Amount to pay in total'
        amount = amount_list[0]
      else:
        amount = payment.AccountingTransactionLine_statSourceDebit()
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.20',
                                        target=payment,
                                        corporate_registration_code=social_contribution_organisation.getCorporateRegistrationCode(),
                                        first_date_of_month=first_date_of_month,
                                        last_date_of_month=last_date_of_month,
                                        establishment=establishment,
                                        payer=establishment))
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.22',
                                      corporate_registration_code=corporate_registration_code,
                                      establishment=establishment,
                                      start_date=social_contribution_start_date,
                                      stop_date=social_contribution_stop_date,
                                      amount=amount))
      for ctp_code in aggregated_social_contribution_dict:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.23',
                                        target=aggregated_social_contribution_dict[ctp_code]))
    else:
      if organisation.isQuaterlyPayment():
        start_date = addToDate(first_date_of_month, month=-2)
      else:
        start_date = first_date_of_month
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.20',
                                      target=payment,
                                      corporate_registration_code=corporate_registration_code,
                                      first_date_of_month=start_date,
                                      last_date_of_month=last_date_of_month,
                                      establishment=establishment,
                                      payer=organisation))
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.55', target=payment, establishment=establishment))
elif len(paysheet_list):
  # If there is no Payment Transaction, then the organisation pays quaterly
  amount = -1. * portal.portal_simulation.getInventory(
    from_date=first_date_of_month,
    to_date=last_date_of_month + 1,
    section_uid=establishment.getUid(),
    mirror_section_uid=social_contribution_organisation.getUid(),
    node_uid=portal.account_module['securite_sociale'].getUid(),
    ledger_uid=portal.portal_categories.ledger.accounting.general.getUid(),
    parent_portal_type='Accounting Transaction',
  )
  dsn_file.append(getDSNBlockDict(block_id='S21.G00.22',
                                  corporate_registration_code=social_contribution_organisation.getCorporateRegistrationCode(),
                                  establishment=establishment,
                                  start_date=first_date_of_month,
                                  stop_date=last_date_of_month,
                                  amount=amount))
  for ctp_code in aggregated_social_contribution_dict:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.23',
                                    target=aggregated_social_contribution_dict[ctp_code]))

# Annual Taxes
if organisation == establishment and declared_month == 12:
  tax_list = organisation.Organisation_getAnnualTaxDictList(context)
  for tax in tax_list:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.44', target=establishment, **tax))


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

  if enrollment_record.getCareerStopDate() != None and \
     first_date_of_month <= enrollment_record.getCareerStopDate() <= last_date_of_month:
    if enrollment_record.getContractType() != '29':
      leaving_employee_list.append(employee)
      disenrollment_record = portal.restrictedTraverse(employee).Person_getCareerRecord('DSN Disenrollment Record')
      dsn_file.append({rubric: value
                       for rubric, value in getDSNBlockDict("S21.G00.62", enrollment_record=enrollment_record, disenrollment_record=disenrollment_record).items()
                       if rubric in ('S21.G00.62.001',
                                     'S21.G00.62.002',
                                     'S21.G00.62.006',
                                     'S21.G00.62.016',
                                     'S21.G00.62.017')})

  # All employees don't share all the insurance contract, so here we need to
  # know to which the employee contributes. Let's loop over the keys of
  # paysheet_data_dict['taxable_base'],
  # which are of the form : (contribution_category, contract_id)
  insurance_contract_id_list = set([x[1] for x in paysheet_data_dict['taxable_base']])

  for insurance_contract_id in insurance_contract_id_list:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.70',
                                    enrollment_record=enrollment_record,
                                    contract_id=insurance_contract_id))

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
      if ('01', '') in paysheet_data_dict['taxable_base_component']:
        dsn_file.append(getDSNBlockDict(block_id='S21.G00.79', target=paysheet_data_dict['taxable_base_component'][('01', '')]))
        del paysheet_data_dict['taxable_base_component'][('01', '')]
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
if len(leave_period_dict):
  for employee in leave_period_dict:
    for period in leave_period_dict[employee]:
      #leave_date_as_string = period['S21.G00.60.002']
      #year = int(leave_date_as_string[4:])
      #month = int(leave_date_as_string[2:4])
      #day = int(leave_date_as_string[:2])
      #leave_date = DateTime(year, month, day)
      #if leave_date < first_date_of_month:
      #  continue
      if employee in employee_list:
        nb_dsn += 1
        dsn_order = portal.portal_ids.generateNewId(
          id_generator='continuous_integer_increasing',
          id_group='dsn_event_counter')
        employee = portal.restrictedTraverse(employee)
        dsn_file.append(getEventDSNBlockDict(block_id='S20.G00.05', dsn_type='04', order=dsn_order))
        dsn_file.append(getEventDSNBlockDict(block_id='S20.G00.07', target=organisation_contact))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.06', target=organisation))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.11', target=establishment))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.30', target=employee))
        dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.40', target=employee.getDefaultCareerValue()))
        dsn_file.append(period)


# Add end of contract event DSN if needed
# Usually we don't merge the monthly DSN with the End of Contract DSN,
# but if we need the code is below :

#for employee in leaving_employee_list:
#  nb_dsn += 1
#  employee = portal.restrictedTraverse(employee)
#  dsn_order = portal.portal_ids.generateNewId(
#    id_generator='continuous_integer_increasing',
#    id_group='dsn_event_counter')
#  disenrollment_record = employee.Person_getCareerRecord('DSN Disenrollment Record')
#  enrollment_record = employee.Person_getCareerRecord('DSN Enrollment Record')
#  for employee_data_dict, paysheet_data_dict in employee_result_list:
#    if employee_data_dict['person_relative_url'] == employee.getRelativeUrl():
#      break
#  dsn_file.append(context.DSNEndOfContractReport_getDataDict(
#    block_id='S20.G00.05', order=dsn_order
#  ))
#  dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.06', target=organisation))
#  dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.11', target=establishment))
#  for collective_contract in collective_contract_list:
#    if collective_contract['S21.G00.15.005'] in set([x[1] for x in paysheet_data_dict['taxable_base']]):
#      dsn_file.append({key: value for key, value in collective_contract.items() if key != 'S21.G00.15.004'})
#  dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.30', target=employee))
#  dsn_file.append(
#    context.DSNEndOfContractReport_getDataDict(
#      block_id='S21.G00.40', target=employee.getDefaultCareerValue(), enrollment_record=enrollment_record
#    )
#  )
#  dsn_file.append(getDSNBlockDict("S21.G00.62", enrollment_record=enrollment_record, disenrollment_record=disenrollment_record))
#  dsn_file.append(getDSNBlockDict("S21.G00.63", enrollment_record=enrollment_record, disenrollment_record=disenrollment_record))
#  dsn_file.append(getDSNBlockDict(block_id='S21.G00.71', enrollment_record=enrollment_record))
#  dsn_file.append(getDSNBlockDict(block_id='S21.G00.50',
#                                  net_salary=paysheet_data_dict['net_salary'],
#                                  net_taxable_salary=paysheet_data_dict['net_taxable_salary']))
#  for remuneration_block in paysheet_data_dict['remuneration']:
#    if 'S21.G00.51.011' in remuneration_block and remuneration_block['S21.G00.51.011'] not in ('001', '002'):
#      continue
#    dsn_file.append(remuneration_block)
#  for bonus_category in paysheet_data_dict['other_bonus'].itervalues():
#    dsn_file.append(getDSNBlockDict(block_id='S21.G00.52', target=bonus_category))
#
#  for bonus_category in paysheet_data_dict['other_income'].itervalues():
#    dsn_file.append(getDSNBlockDict(block_id='S21.G00.54', target=bonus_category))


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
footer = getDSNBlockDict(block_id='S90.G00.90', length=rubric_counter, dsn_record_counter=nb_dsn)
for rubric in sorted(footer.keys()):
  dsn_report_string += "%s,'%s'\n" % (rubric, footer[rubric])

context.setTextContent(dsn_report_string.strip())

if batch_mode:
  # Set charset for response
  context.REQUEST.response.setHeader("Content-Type", "text/plain; charset=iso-8859-1")
  return

context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "Monthly DSN Record Created."))
