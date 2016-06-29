from Products.ERP5Type.DateUtils import addToDate

portal = context.getPortalObject()
accounting_module = portal.accounting_module

getDSNblockAsDict = context.DSNMonthlyReport_getDataAsDict_p2
getEventDSNblockAsDict = context.DSNEarlyRecoveryReport_getDataAsDict_p2

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def getDSNReport(leave_period, dsn_order):
  dsn_report = []

  # DSN HEADERS
  dsn_report.append(getDSNblockAsDict(block_id='S10.G00.00'))
  dsn_report.append(getDSNblockAsDict(block_id='S10.G00.01', target=organisation))
  dsn_report.append(getDSNblockAsDict(block_id='S10.G00.02', target=organisation_contact))
  dsn_report.append(getDSNblockAsDict(block_id='S10.G00.03', target=organisation))
  
  # Early Recovery DSN : identification data
  employee = leave_period.getDestinationValue()
  dsn_report.append(getEventDSNblockAsDict(block_id='S20.G00.05', dsn_type='05', order=dsn_order))
  dsn_report.append(getEventDSNblockAsDict(block_id='S20.G00.07', target=organisation_contact))
  dsn_report.append(getEventDSNblockAsDict(block_id='S21.G00.06', target=organisation))
  dsn_report.append(getEventDSNblockAsDict(block_id='S21.G00.11', target=employee.getDefaultCareerValue().getSubordinationValue()))
  dsn_report.append(getEventDSNblockAsDict(block_id='S21.G00.30', target=employee))
  dsn_report.append(getEventDSNblockAsDict(block_id='S21.G00.40', target=employee.getDefaultCareerValue()))
  
  # Make the leave block, containing information about the early recovery
  leave_block = {'S21.G00.60.001': leave_period.getResourceValue().getCodification(),
                 'S21.G00.60.002': formatDate(leave_period.getStartDate()),
                 'S21.G00.60.003': formatDate(leave_period.getStopDate()),
                 'S21.G00.60.010': formatDate(leave_period.getExpirationDate()),
                 'S21.G00.60.011': '01'} # Normal come back
  dsn_report.append(leave_block)

  return dsn_report

# Get information for this DSN report
organisation = context.getSourceSectionValue()
organisation_contact = context.getSourceAdministrationValue()
leave_period = context.getAggregateValue()

dsn_file = []
dsn_order = 2 # 1 is always monthly DSN

if leave_period.getExpirationDate() <= leave_period.getStopDate():
  dsn_order += 1
  dsn_file = getDSNReport(leave_period, dsn_order)
else:
  context.REQUEST.response.redirect("%s?portal_status_message=%s" % (context.absolute_url(), "No need to create this DSN event report : return date is not previous to last leaved date."))

# Print DSN
rubric_counter = 0

for block in dsn_file:
  for rubric in sorted(block):
    if block[rubric]:
      rubric_counter += 1
      print "%s,'%s'" % (rubric, block[rubric])
footer = getDSNblockAsDict(block_id='S90.G00.90', length=rubric_counter, dsn_record_counter=1)
for rubric in sorted(footer.keys()):
  print "%s,'%s'" % (rubric, footer[rubric])

context.setData(printed.strip())

context.REQUEST.response.redirect("%s%s?portal_status_message=%s" % (context.absolute_url(), context.getPath(), "Event DSN Record Created."))
