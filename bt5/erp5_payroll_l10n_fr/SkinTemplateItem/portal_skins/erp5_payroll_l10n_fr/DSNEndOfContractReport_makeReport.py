from erp5.component.module.DateUtils import getNumberOfDayInMonth
import six

def getLastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

if context.getSourceAdministration() is None:
  return context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "DSN can't be built if some fields are empty"))

portal = context.getPortalObject()
getDSNBlockDict = context.DSNMonthlyReport_getDataDict
getEventDSNBlockDict = context.DSNEarlyRecoveryReport_getDataDict

# Get all paysheets for requested month
related_accounting_transaction_list = context.getAggregateRelatedValueList()
paysheet_list = sorted([transaction for transaction in related_accounting_transaction_list
                       if transaction.getPortalType() == "Pay Sheet Transaction"], key=lambda x: x.getTitle()) # Sorting for idempotent result in tests
if len(paysheet_list) != 1:
  return context.Base_redirect(message='Exactly one paysheet should be declared')

# Retrieve related documents
paysheet = paysheet_list[0]
employee = paysheet.getSourceSectionValue()
career = employee.getDefaultCareerValue()
establishment = career.getSubordinationValue()
organisation = career.getDestinationValue()
disenrollment_record = employee.Person_getCareerRecord('DSN Disenrollment Record')
enrollment_record = employee.Person_getCareerRecord('DSN Enrollment Record')

# Set up variables needed for the DSN Report
dsn_file = []
nb_dsn = 1
organisation_contact = context.getSourceAdministrationValue()
dsn_order = portal.portal_ids.generateNewId(
  id_generator='continuous_integer_increasing',
  id_group='dsn_event_counter'
)

# Compute values related to the declaration
paysheet_data_dict = paysheet.PaySheetTransaction_getSocialContributionDict()
collective_contract_list = getDSNBlockDict(block_id='S21.G00.15')

# DSN HEADERS
dsn_file.append(getDSNBlockDict(block_id='S10.G00.00'))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.01', target=organisation))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.02', target=organisation_contact))

# DSN End Of Contract Report's Body
dsn_file.append(context.DSNEndOfContractReport_getDataDict(
  block_id='S20.G00.05', order=dsn_order
))

dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.06', target=organisation))
dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.11', target=establishment))

for collective_contract in collective_contract_list:
  if collective_contract['S21.G00.15.005'] in set([x[1] for x in paysheet_data_dict['taxable_base']]):
    dsn_file.append({key: value for key, value in collective_contract.items() if key != 'S21.G00.15.004'})

dsn_file.append(getEventDSNBlockDict(block_id='S21.G00.30', target=employee))

dsn_file.append(
  context.DSNEndOfContractReport_getDataDict(
    block_id='S21.G00.40', target=employee.getDefaultCareerValue(), enrollment_record=enrollment_record
  )
)

dsn_file.append(getDSNBlockDict("S21.G00.62", enrollment_record=enrollment_record, disenrollment_record=disenrollment_record))

dsn_file.append(getDSNBlockDict("S21.G00.63", enrollment_record=enrollment_record, disenrollment_record=disenrollment_record))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.71', enrollment_record=enrollment_record))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.50',
                                date=getLastDateOfMonth(paysheet.getStopDate()),
                                net_salary=paysheet_data_dict['net_salary'],
                                net_taxable_salary=paysheet_data_dict['net_taxable_salary']))

for remuneration_block in paysheet_data_dict['remuneration']:
  if 'S21.G00.51.011' in remuneration_block and remuneration_block['S21.G00.51.011'] not in ('001', '002'):
    continue
  dsn_file.append(remuneration_block)

for bonus_category in six.itervalues(paysheet_data_dict['other_bonus']):
  dsn_file.append(getDSNBlockDict(block_id='S21.G00.52', target=bonus_category))

for bonus_category in six.itervalues(paysheet_data_dict['other_income']):
  dsn_file.append(getDSNBlockDict(block_id='S21.G00.54', target=bonus_category))

# Print DSN Record
rubric_counter = 0

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
