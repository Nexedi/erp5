from Products.ERP5Type.DateUtils import getNumberOfDayInMonth

portal = context.getPortalObject()

paysheet = portal.accounting_module[paysheet_id]

remuneration_bloc = {}
result = []
is_trainee = (True if enrollment_record.getContractType() == '29' else False)
is_corporate_executive = (True if enrollment_record.getContractType() == '80' else False)

career_start_date = enrollment_record.getCareerStartDate()
career_stop_date = enrollment_record.getCareerStopDate()

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def formatFloat(number):
  return "{:.02f}".format(number)

def getRemunerationBlocAsDict(remuneration_type, amount):
  "Make Remuneration Blocs. Adjust values if needed"
  bloc = {}
  # Corporate executives and trainees don't contribute to unemployment fee
  if is_corporate_executive and remuneration_type == '002':
    amount = 0.
  elif is_trainee and remuneration_type == '002':
    amount = 0.
  # Nexedi trainees don't pay social fees
  elif is_trainee and remuneration_type == '003':
    amount = 0.
  bloc['S21.G00.51.001'] = formatDate(paysheet.getStartDate())
  bloc['S21.G00.51.002'] = formatDate(paysheet.getStopDate())
  bloc['S21.G00.51.009'] = '' # Only one contract/employee
  bloc['S21.G00.51.010'] = '00000'
  bloc['S21.G00.51.011'] = remuneration_type
  bloc['S21.G00.51.012'] = ''
  bloc['S21.G00.51.013'] = formatFloat(amount)
  return bloc

remuneration_types = (('001', 'gross'), ('002', 'gross'), ('003', 'gross'), ('010', 'gross'))

salary = {}
salary['gross'] = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/base_amount/payroll/report/salary/gross")

for remuneration_type, salary_type in remuneration_types:
  result.append(getRemunerationBlocAsDict(remuneration_type, salary[salary_type]))
  if remuneration_type == '002':
    usual_working_time = float(enrollment_record.getWorkingUnitQuantity())
    employee_worked_time = float(paysheet.getWorkTimeAnnotationLineQuantity())
    # Case 1 : employee was never missing
    if employee_worked_time - usual_working_time >= 0 \
      or career_start_date == paysheet.getStartDate() \
      or career_stop_date == paysheet.getStopDate():
      result.append({'S21.G00.53.001': '01',
                     'S21.G00.53.002': formatFloat(employee_worked_time),
                     'S21.G00.53.003': '10'})
    else:
      # http://dsn-info.custhelp.com/app/answers/detail/a_id/643
      result.append({'S21.G00.53.001': '01',
                     'S21.G00.53.002': formatFloat(employee_worked_time),
                     'S21.G00.53.003': '10'})
      result.append({'S21.G00.53.001': '02',
                     'S21.G00.53.002': formatFloat(usual_working_time - employee_worked_time),
                     'S21.G00.53.003': '10'})

# Make blocs 54 : other incomes
other_income_category_list = set(portal.portal_categories.base_amount.payroll.l10n.fr.other_income.getCategoryChildValueList())

for paysheet_line in paysheet.PaySheetTransaction_getMovementList():
  service = paysheet_line.getResourceValue()
  income_category = set(service.getBaseContributionValueList()).intersection(other_income_category_list)
  if len(income_category) > 0:
    income_category = income_category.pop()
    # base is different in the case of the "ticket_restaurant" contribution
    base = (paysheet_line.employer_total_price if income_category.getCodification() == '17' else paysheet_line.base)
    if float(base) == 0.:
      continue
    result.append({'S21.G00.54.001': income_category.getCodification(),
                   'S21.G00.54.002': formatFloat(abs(base)),
                   'S21.G00.54.003': formatDate(paysheet_line.getStartDate()),
                   'S21.G00.54.004': formatDate(paysheet_line.getStopDate())})

return result
