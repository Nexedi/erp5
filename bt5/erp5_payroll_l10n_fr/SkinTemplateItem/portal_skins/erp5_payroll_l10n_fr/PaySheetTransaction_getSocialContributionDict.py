from erp5.component.module.DateUtils import getNumberOfDayInMonth

portal = context.getPortalObject()
portal_categories = portal.portal_categories

other_information_data_dict = context.PaySheetTransaction_getOtherInformationsDataDict()

result = {
  'ctp': {},
  'individual_contribution': {},
  'taxable_base': {},
  'taxable_base_component' : {},
  'other_income': {},
  'other_bonus': {},
  'remuneration' : [],
  'net_salary': context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution='base_contribution/base_amount/payroll/report/salary/net', contribution_share='contribution_share/employee'),
  'net_taxable_salary': other_information_data_dict["salaire_net_imposable_float"],
  'pay_sheet_transaction': context,
}

all_ctp_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/ctp').objectValues(portal_type='Category')) # TODO
all_indivual_contribution_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/individual_contribution').objectValues(portal_type='Category'))
all_taxable_base_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/taxable_base').objectValues(portal_type='Category'))
all_taxable_base_component_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/taxable_base_component').objectValues(portal_type='Category'))
all_other_income_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/other_income').objectValues(portal_type='Category'))
all_other_bonus_set = set(portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/other_bonus').objectValues(portal_type='Category'))
trainee_base_contribution = portal_categories.getCategoryValue('base_amount/payroll/l10n/fr/base/gratification_stage')

enrollment_record = context.getSourceSectionValue().Person_getCareerRecord('DSN Enrollment Record')

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def formatFloat(number):
  return "{:.02f}".format(number)

def getINSEECode(zip_code):
  insee_code_list = str(context.INSEECodeList).split('\n')
  for code in insee_code_list:
    insee_record = code.split(';')
    if zip_code == insee_record[1]:
      return insee_record[0]
  return None

def getLastDateOfMonth(date):
  return DateTime(date.year(), date.month(), getNumberOfDayInMonth(date))

def isFullMonthPaysheet(paysheet):
  paysheet_date = paysheet.getStartDate()
  last_date_of_month = getLastDateOfMonth(paysheet_date)
  first_date_of_month = DateTime(paysheet_date.year(),
                                 paysheet_date.month(),
                                 1)
  return first_date_of_month == paysheet.getStartDate() and last_date_of_month == paysheet.getStopDate()

ZIP_CODE = context.getDestinationSectionValue().getDefaultAddressZipCode()
INSEE_CODE = getINSEECode(ZIP_CODE)

def makeCTPBlock(movement, category):
  quantity = 0.
  if category[:3] in ('437', '671', '801'):
    quantity = getattr(movement, 'employer_total_price', 0.) + getattr(movement, 'employee_total_price', 0.)
  return {
    'code': category,
    'corporate_registration_code': movement.getSourceSectionValue(),
    'cap': ('921' if category[-1] == 'P' else '920'),
    'rate': (abs(getattr(movement, 'employer_price') * 100) if category in ('100A', '900T', '901D', '863A', '734A') else ''),
    'base': movement.base,
    'quantity': quantity,
    'zip_code': (INSEE_CODE if category == '900T' else ''),
    'start_date': movement.getStartDate(),
    'stop_date': movement.getStopDate(),
  }

def makeTaxableBaseBlock(movement, category):
  return {
    'code': category,
    'start_date': movement.getStartDate(),
    'stop_date': movement.getStopDate(),
    'base': movement.base,
    'contract_id': movement.PaySheetTransactionLine_getInsuranceContractId()
  }

def makeTaxableBaseComponentBlock(movement, category):
  if category == '03':
    base = getattr(movement, 'employer_total_price') * -1
  elif category == '20':
    base = (getattr(movement, 'employer_total_price', 0) + getattr(movement, 'employee_total_price', 0)) * -1
  elif category in ('01', '02'):
    # Base is the relative minimum salary
    minimum_salary = float(context.getRatioQuantityFromReference('salaire_minimum_mensuel'))
    if isFullMonthPaysheet(context):
      base = minimum_salary
    else:
      worked_time = float(enrollment_record.getWorkingUnitQuantity())
      normal_working_time = float(enrollment_record.getStandardWorkingUnit())
      base = minimum_salary * (worked_time / normal_working_time)
  else:
    base = movement.base
  return {
    'code': category,
    'base': base,
    'start_date': movement.getStartDate(),
    'stop_date': movement.getStopDate(),
    'contract_id': movement.PaySheetTransactionLine_getInsuranceContractId()
  }

def makeIndividualContributionBlock(movement, category):
  base = quantity = 0.0
  if category in ('063', '064'):
    quantity = (getattr(movement, 'employer_total_price', 0) + getattr(movement, 'employee_total_price', 0)) * -1
    # If "reduction generale but CTP is 801P then it should be positive, as we have to give money back
  elif category == '018':
    base = movement.base
    quantity = (getattr(movement, 'employer_total_price', 0) + getattr(movement, 'employee_total_price', 0)) * -1
    if 'base_amount/payroll/l10n/fr/ctp/801P' not in movement.getBaseContributionList():
      assert quantity <= 0., "Quantity in %s should be negative" % movement.absolute_url()
    else:
      assert quantity >= 0., "Quantity in %s should be positive" % movement.absolute_url()
  elif category in ('059',):
    quantity = (getattr(movement, 'employer_total_price', 0) + getattr(movement, 'employee_total_price', 0)) * -1
  else:
    base = movement.base
  return {
    'code': category,
    'corporate_registration_code': movement.getSourceSectionValue().getCorporateRegistrationCode(),
    'base': base,
    'quantity': quantity,
    'zip_code': (INSEE_CODE if category == '226' else ''),
    'contract_id': movement.PaySheetTransactionLine_getInsuranceContractId(),
  }

def makeOtherIncomeBlock(movement, category):
  return {
    'code': category,
    'quantity': (movement.base if category != '17' else movement.employer_total_price * (-1)),
    'start_date': movement.getStartDate(),
    'stop_date': movement.getStopDate()
  }

def makeOtherBonusBlock(movement, category):
  return {
    'code': category,
    'quantity': movement.base,
    'start_date': (movement.getStartDate() if category in ('026', '027', '029') else ''),
    'stop_date': (movement.getStopDate()  if category in ('026', '027', '029') else ''),
  }

for movement in context.PaySheetTransaction_getMovementList():
  if not movement.base:
    continue

  contribution_set = set(movement.getBaseContributionValueList())

  ctp_set = all_ctp_set.intersection(contribution_set)
  for category in ctp_set:
    category = category.getCodification()
    contribution_dict = makeCTPBlock(movement, category)
    if category in result["ctp"]:
      result['ctp'][category]['base'] = result['ctp'][category]['base'] + contribution_dict['base']
      result['ctp'][category]['quantity'] = result['ctp'][category]['quantity'] + contribution_dict['quantity']
    else:
      result['ctp'][category] = contribution_dict

  taxable_base_set = all_taxable_base_set.intersection(contribution_set)
  for category in taxable_base_set:
    category = category.getCodification()
    contribution_dict = makeTaxableBaseBlock(movement, category)
    if (category, contribution_dict['contract_id']) in result['taxable_base']:
      result['taxable_base'][(category, contribution_dict['contract_id'])]['base'] = result['taxable_base'][(category, contribution_dict['contract_id'])]['base'] + contribution_dict['base']
    else:
      result['taxable_base'][(category, contribution_dict['contract_id'])] = contribution_dict

  taxable_base_component_set = all_taxable_base_component_set.intersection(contribution_set)
  for category in taxable_base_component_set:
    category = category.getCodification()
    contribution_dict = makeTaxableBaseComponentBlock(movement, category)
    if (category, contribution_dict['contract_id']) in result["taxable_base_component"]:
      result['taxable_base_component'][(category, contribution_dict['contract_id'])]['base'] = result['taxable_base_component'][(category, contribution_dict['contract_id'])]['base'] + contribution_dict['base']
    else:
      result['taxable_base_component'][(category, contribution_dict['contract_id'])] = contribution_dict

  individual_contribution_set = all_indivual_contribution_set.intersection(contribution_set)
  for category in individual_contribution_set:
    category = category.getCodification()
    contribution_dict = makeIndividualContributionBlock(movement, category)
    if (category, contribution_dict['contract_id']) in result["individual_contribution"]:
      result['individual_contribution'][(category, contribution_dict['contract_id'])]['base'] = result['individual_contribution'][(category, contribution_dict['contract_id'])]['base'] + contribution_dict['base']
      result['individual_contribution'][(category, contribution_dict['contract_id'])]['quantity'] = result['individual_contribution'][(category, contribution_dict['contract_id'])]['quantity'] + contribution_dict['quantity']
    else:
      result['individual_contribution'][(category, contribution_dict['contract_id'])] = contribution_dict

  other_income_set = all_other_income_set.intersection(contribution_set)
  for category in other_income_set:
    category = category.getCodification()
    contribution_dict = makeOtherIncomeBlock(movement, category)
    if contribution_dict['quantity']:
      if category in result["other_income"]:
        result['other_income'][category]['quantity'] = result['other_income'][category]['quantity'] + contribution_dict['quantity']
      else:
        result['other_income'][category] = contribution_dict

  other_bonus_set = all_other_bonus_set.intersection(contribution_set)
  total_bonus = 0.0
  for category in other_bonus_set:
    category = category.getCodification()
    contribution_dict = makeOtherBonusBlock(movement, category)
    if contribution_dict['quantity']:
      if category in result["other_bonus"]:
        result['other_bonus'][category]['quantity'] = result['other_bonus'][category]['quantity'] + contribution_dict['quantity']
      else:
        result['other_bonus'][category] = contribution_dict
      total_bonus += contribution_dict['quantity']

  if trainee_base_contribution in contribution_set:
    trainee_bonus = movement.base
    result['taxable_base'][('02', '')] = {
      'code': '02',
      'start_date': movement.getStartDate(),
      'stop_date': movement.getStopDate(),
      'base': 0.,
      'contract_id': ''
    }
    result['taxable_base'][('03', '')] = {
      'code': '03',
      'start_date': movement.getStartDate(),
      'stop_date': movement.getStopDate(),
      'base': 0.,
      'contract_id': ''
    }
    result['individual_contribution'][('022', '')] = {
      'code': '022',
      'corporate_registration_code': '',
      'base': trainee_bonus,
      'quantity': 0.,
      'zip_code': '',
      'contract_id': '',
    }

# Let's try to calculate CTP 400D, which doesn't appear in the paysheet

if len(result['ctp']):
  year_to_date_gross_salary = float(other_information_data_dict['year_to_date_gross_salary'])
  try:
    minimum_salary = float(context.getRatioQuantityFromReference('salaire_minimum_mensuel'))
  except:
    raise AttributeError(context.getUrl())
  if year_to_date_gross_salary < 2.5 * minimum_salary * int(context.getStopDate().month()):
    category = '400D'
    result['ctp'][category] = {
      'code': category,
      'cap': ('921' if category[-1] == 'P' else '920'),
      'rate': '',
      'base': year_to_date_gross_salary,
      'quantity': 0,
      'zip_code': ''
    }

######################################################################
# Remuneration and Activity

is_trainee = (True if enrollment_record.getContractType() == '29' else False)
is_corporate_executive = (True if enrollment_record.getContractType() == '80' else False)
career_start_date = enrollment_record.getCareerStartDate()
career_stop_date = enrollment_record.getCareerStopDate()

def getRemunerationBlockAsDict(remuneration_type, amount):
  "Make Remuneration Blocs. Adjust values if needed"
  bloc = {}
  # Corporate executives and trainees don't contribute to unemployment fee
  if is_corporate_executive and remuneration_type == '002':
    amount = 0.
  elif is_trainee and remuneration_type == '001':
    amount = trainee_bonus
  elif is_trainee and remuneration_type == '002':
    amount = 0.
  # Nexedi trainees don't pay social fees
  elif is_trainee and remuneration_type == '003':
    amount = 0.
  bloc['S21.G00.51.001'] = formatDate(context.getStartDate())
  bloc['S21.G00.51.002'] = formatDate(context.getStopDate())
  bloc['S21.G00.51.009'] = '' # Only one contract/employee
  bloc['S21.G00.51.010'] = '00000'
  bloc['S21.G00.51.011'] = remuneration_type
  bloc['S21.G00.51.012'] = ''
  bloc['S21.G00.51.013'] = formatFloat(amount)
  return bloc

remuneration_types = (('001', 'gross'), ('002', 'gross'), ('003', 'gross'), ('010', 'gross'))

salary = {}
salary['gross'] = context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/base_amount/payroll/report/salary/gross") - total_bonus

for remuneration_type, salary_type in remuneration_types:
  result['remuneration'].append(getRemunerationBlockAsDict(remuneration_type, salary[salary_type]))
  if remuneration_type == '002':
    usual_working_time = float(enrollment_record.getWorkingUnitQuantity())
    employee_worked_time = float(context.getWorkTimeAnnotationLineQuantity())
    # Case 1 : employee was never missing
    if employee_worked_time - usual_working_time >= 0 \
      or career_start_date == context.getStartDate() \
      or career_stop_date == context.getStopDate():
      result['remuneration'].append({
        'S21.G00.53.001': '01',
        'S21.G00.53.002': formatFloat(employee_worked_time),
        'S21.G00.53.003': '10'
      })
    else:
      # http://dsn-info.custhelp.com/app/answers/detail/a_id/643
      result['remuneration'].append({
        'S21.G00.53.001': '01',
        'S21.G00.53.002': formatFloat(employee_worked_time),
        'S21.G00.53.003': '10'})
      result['remuneration'].append({
        'S21.G00.53.001': '02',
        'S21.G00.53.002': formatFloat(usual_working_time - employee_worked_time),
        'S21.G00.53.003': '10'})

######################################################################
# Bonus

return result
