from erp5.component.module.DateUtils import getNumberOfDayInMonth

if context.getSourceAdministration() is None \
   or context.getEffectiveDate() is None \
   or context.getFormat() is None \
   or context.getQuantity() is None \
   or len(context.getAggregateRelatedIdList()) <= 0:
  return context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "DSN can't be built if some fields are empty"))

portal = context.getPortalObject()
accounting_module = portal.getDefaultModuleValue("Pay Sheet Transaction")

getDSNBlockDict = context.DSNMonthlyReport_getDataDictPhaseTwo
getEventDSNBlockDict = context.DSNEarlyRecoveryReport_getDataDictPhaseTwo
getEmployeeRemunerationList = context.DSNMonthlyReport_getEmployeeRemunerationList

def getLastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

# Use The following to create a DEBUG Mode, in wich rubric's codes could be
# replaced by their title, and DSN consistency could be tested and reported

# # Import Rubrics from CSV File
# # Define a Rubric class
# class Rubric():
#   def __init__(self, title, id, semantic_id, min_length, max_length, regexp):
#     self.title = title
#     self.id = id
#     self.semantic_id = semantic_id
#     self.min_length = int(min_length)
#     self.max_length = int(max_length)
#     self.regexp = regexp

# # Import rubrics in dict
# rubric_list = context.DSN_rubric_list.data.split('\n')
# rubric_dict = {}

# for line_number, line in enumerate(rubric_list):
#   if line_number==0:
#     pass
#   else:
#     data = line.split(',')
#     try:
#       rubric_dict[data[1]] = Rubric(data[2], data[1], data[9], data[5], data[6], data[7])
#     except IndexError:
#       pass

# Define DSN type record as a tree :
# A DSN Report is basically a header and a footer encapsulating
# a kind of report.
#
# Here is the basic structure of a DSN, using a python tuple-tree representation
# dsn_record = (
# ("S10.G00.00", "1", (
#   ("S10.G00.01", "1", None),
#   ("S10.G00.02", "+", None),
#   ("S10.G00.03", "?", None),
#   monthly_dsn_type)),
# ("S90.G00.90", "1", None))
#
# monthly_dsn_type = \
# ('S20.G00.05',
# '1',
# (('S21.G00.06',
#   '1',
#   ('S21.G00.11',
#     '1',
#     (('S21.G00.15', '*', None),
#     ('S21.G00.20', '*', None),
#     ('S21.G00.22', '*', ('S21.G00.23', '*', None)),
#     ('S21.G00.30',
#       '*',
#       (('S21.G00.31', '*', None),
#       ('S21.G00.40',
#         '+',
#         (('S21.G00.41', '*', None),
#         ('S21.G00.60', '*', None),
#         ('S21.G00.62', '?', None),
#         ('S21.G00.65', '*', None),
#         ('S21.G00.70', '*', ('S21.G00.72', '*', None)),
#         ('S21.G00.71', '+', None))),
#       ('S21.G00.50',
#         '+',
#         (('S21.G00.51', '+', ('S21.G00.53', '*', None)),
#         ('S21.G00.52', '*', None),
#         ('S21.G00.54', '*', None),
#         ('S21.G00.78',
#           '*',
#           (('S21.G00.79', '*', None), ('S21.G00.81', '*', None)))))))))),
#   ('S21.G00.85', '*', None)))


# Gather data for DSN
declared_month = context.getEffectiveDate().month()
declared_year = context.getEffectiveDate().year()

# Get all paysheets for requested month
related_accounting_transaction_list = context.getAggregateRelatedValueList()
payment_transaction_list = [transaction for transaction in related_accounting_transaction_list
                            if transaction.getPortalType() == "Payment Transaction"]
paysheet_id_list = sorted([transaction.getId() for transaction in related_accounting_transaction_list
                           if transaction.getPortalType() == "Pay Sheet Transaction"]) # Sorting for idempotent result in tests

# DSN in phase 2 only reports social fees
if len(payment_transaction_list) != 1:
  return context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "Exactly one Payment Transaction must be reported per DSN"))

payment_transaction = payment_transaction_list.pop()

organisation_contact = context.getSourceAdministrationValue()
establishment = accounting_module.restrictedTraverse(paysheet_id_list[0]).getDestinationSectionValue()

# Finds the head office of the comany
organisation = payment_transaction.getSourceSectionValue()

leave_period_dict = context.DSNMonthlyReport_getLeavePeriodDict(payment_transaction)
employee_list = []

# Variable containing all the record of the DSN
dsn_file = []
dsn_order = 1 # Increment for each DSN

# DSN HEADERS
dsn_file.append(getDSNBlockDict(block_id='S10.G00.00'))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.01', target=organisation))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.02', target=organisation_contact))
dsn_file.append(getDSNBlockDict(block_id='S10.G00.03', target=organisation))


# Monthly DSN
dsn_file.append(getDSNBlockDict(block_id='S20.G00.05', year=declared_year, month=declared_month, order=dsn_order))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.06', target=organisation))

dsn_file.append(getDSNBlockDict(block_id='S21.G00.11', target=establishment, manpower=len(paysheet_id_list)))
dsn_file.append(getDSNBlockDict(block_id='S21.G00.15', target=establishment))

# Print aggregated cotisations
cotisation_dict = context.DSNMonthlyReport_getSocialContributionDict(paysheet_id_list)

bank_account = payment_transaction.getSourcePaymentValue()
bloc_versement = getDSNBlockDict(block_id='S21.G00.20', target=establishment, bank_account=bank_account, year=declared_year, month=declared_month)
for rubric, value in cotisation_dict['payment']:
  bloc_versement[rubric] = value
dsn_file.append(bloc_versement)

bloc_payment_slip = getDSNBlockDict(block_id='S21.G00.22', target=establishment, year=declared_year, month=declared_month)
for rubric, value in cotisation_dict['total_payment_slip']:
  bloc_payment_slip[rubric] = value
dsn_file.append(bloc_payment_slip)

for bloc in cotisation_dict['aggregated_fee_list']:
  dsn_file.append(bloc)

change_block_dict = context.DSNMonthlyReport_getChangeBlockDict()

# Print records of Employees (1to1 relation to paysheet)
for paysheet_id in paysheet_id_list:
  paysheet = portal.accounting_module[paysheet_id]
  employee = paysheet.getSourceSectionValue()
  employee_list.append(employee)
  employee_change_block_dict = change_block_dict.get(employee, {})
  enrollment_record = employee.Person_getPayrollEnrollmentRecord(establishment)

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.30', target=employee, enrollment_record=enrollment_record))

  for date in sorted(employee_change_block_dict.get('S21.G00.31', ())):
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.31', change_bloc=employee_change_block_dict['S21.G00.31'][date], change_date=date))

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.40', target=employee.getDefaultCareerValue(), enrollment_record=enrollment_record))

  for date in sorted(employee_change_block_dict.get('S21.G00.41', ())):
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.41', change_bloc=employee_change_block_dict['S21.G00.41'][date], change_date=date))

  if employee in leave_period_dict:
    for leave_period in leave_period_dict[employee]:
      leave_bloc = {rubric: leave_period.get(rubric, None)
                      for rubric in ('S21.G00.60.001',
                                     'S21.G00.60.002',
                                     'S21.G00.60.003',
                                     'S21.G00.60.010',
                                     'S21.G00.60.011',
                                     'S21.G00.60.012')}
      dsn_file.append(leave_bloc)

  last_date_of_month = getLastDateOfMonth(context.getEffectiveDate())
  first_date_of_month = DateTime(context.getEffectiveDate().year(),
                                 context.getEffectiveDate().month(),
                                 1)

  if enrollment_record.getCareerStopDate() != None and \
     first_date_of_month <= enrollment_record.getCareerStopDate() <= last_date_of_month:
    dsn_file.append(getDSNBlockDict("S21.G00.62", enrollment_record=enrollment_record))

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.70', target=employee, enrollment_record=enrollment_record))

  for date in sorted(employee_change_block_dict.get('S21.G00.72', ())):
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.72', change_bloc=employee_change_block_dict['S21.G00.72'][date], change_date=date))

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.71', enrollment_record=enrollment_record))

  dsn_file.append(getDSNBlockDict(block_id='S21.G00.50', target=paysheet))

  for remuneration in getEmployeeRemunerationList(paysheet_id=paysheet_id, enrollment_record=enrollment_record):
    dsn_file.append(remuneration)

  individual_cotisation_dict = cotisation_dict['individual_fee_dict'][paysheet_id]
  for base_code in sorted(individual_cotisation_dict):
    if float(individual_cotisation_dict[base_code]) != 0.:
      dsn_file.append(getDSNBlockDict(block_id='S21.G00.78',
                                      target=paysheet,
                                      base_code=base_code,
                                      amount=individual_cotisation_dict[base_code]))

  cice_relative_min_salary = cotisation_dict['cice_relative_min_salary'].get(paysheet_id, None)
  fillon_relative_min_salary = cotisation_dict['fillon_relative_min_salary'].get(paysheet_id, None)
  fillon_individual_reduction = cotisation_dict['fillon_individual_reduction'].get(paysheet_id, None)
  transport_individual_fee = cotisation_dict['transport_individual_fee'].get(paysheet_id, None)

  if cice_relative_min_salary:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.79',
                                     base_code='02',
                                     base=cice_relative_min_salary))

  if fillon_relative_min_salary:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.79',
                                     base_code='01',
                                     base=fillon_relative_min_salary))
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.81',
                                     base_code='018',
                                     social_entity=transport_individual_fee[1],
                                     base=transport_individual_fee[0], # XXX
                                     amount=abs(fillon_individual_reduction) * -1))

  # For the moment, only S21.G00.81 for Versement Transport
  if transport_individual_fee is not None:
    dsn_file.append(getDSNBlockDict(block_id='S21.G00.81',
                                    base_code='226',
                                    base=transport_individual_fee[0],
                                    social_entity=transport_individual_fee[1],
                                    insee_code=transport_individual_fee[3]))

errors = []

# Add leave event DSN if needed
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
# def checkformat(rubric, value):
#   rubric_desc = rubric_dict[rubric]
#   if len(str(value)) < rubric_desc.min_length:
#     errors.append("%s value is too short : %s instead of %s" % (rubric, len(str(value)), rubric_desc.min_length))
#   if len(str(value)) > rubric_desc.max_length:
#     errors.append("%s value is too long" % (rubric))
#   try:
#     import re
#     if not re.search(rubric_desc.regexp, value):
#       errors.append("%s value doesn't match regexp" %(rubric))
#   except:
#     pass

# for block in dsn_file:
#   for rubric in sorted(block.keys()):
#     if block[rubric]:
#       checkformat(rubric, block[rubric])
#       if rubric[:10] != last_block:
#         print
#         last_block = rubric[:10]
#       print "%s,'%s'\t\t\t#%s" % (rubric, block[rubric], rubric_dict[rubric].semantic_id)

# if errors:
#   print "\n******************** %s ERRORS **********************" % len(errors)
#   for error in errors:
#     print error

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
