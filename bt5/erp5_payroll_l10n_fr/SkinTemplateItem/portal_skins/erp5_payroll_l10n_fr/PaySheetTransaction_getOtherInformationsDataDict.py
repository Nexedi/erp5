import six
portal = context.getPortalObject()
translateString = portal.Base_translateString
quantity_renderer = portal.Base_viewFieldLibrary.my_view_mode_money_quantity.render_pdf
paysheet = context

def getFieldAsLineList(field):
  """Returns the text as a list of lines."""
  field = field or ''
  text = field.replace('\r', '')
  text_list = text.split('\n')
  return [x for x in text_list if x]

def getEmployeeNumber(source_section_career):
  employee_number = source_section_career.getReference()
  s = ''
  if employee_number:
    s = '%s: %s' % (translateString('Employee Number'), employee_number)
  return s

def getSocialCodeId(social_code_id):
  s = ''
  if social_code_id:
    s += '%s: %s' % (translateString('Social Code'), social_code_id)
  return s

def getCareerId(career_title):
  s = ''
  if career_title and career_title != 'default_career':
    s += '%s: %s' % (translateString('Career Title'), career_title)
  return s

def getCollectiveAgreementId(collective_agreement):
  s = ''
  if collective_agreement:
    s += '%s: %s' % (translateString('Collective Agreement'), collective_agreement)
  return s

def getSalaryLevelId(salary_level):
  s = ''
  if salary_level:
    s += '%s: %s' % (translateString('Salary Level'), salary_level)
  return s

def getCareerCoefficientId(career_coefficient):
  s = ''
  if career_coefficient:
    s += '%s: %s' % (translateString('Salary Coefficient'), career_coefficient)
  return s

def getHiringDateId(date):
  s = ''
  if date:
    s += '%s: %s' % (translateString('Hiring Date'), date)
  return s

def getPriceCurrencyId(currency):
  s = ''
  if currency:
    s += '%s: %s' % (translateString('Price Currency'), currency)
  return s

getMovementTotalPriceFromCategory = paysheet.PaySheetTransaction_getMovementTotalPriceFromCategory
getMovementQuantityFromCategory = paysheet.PaySheetTransaction_getMovementQuantityFromCategory

salaire_net_imposable = paysheet.PaySheetTransaction_getPaysheetTaxableSalary()

def getTaxableNetPayId(salaire_net_imposable):
  s = ''
  if salaire_net_imposable:
    s += '%s: %s' % (translateString('Taxable Net Pay'), salaire_net_imposable)
  return s

total_employee_tax = getMovementTotalPriceFromCategory(\
    no_base_contribution=True,
    include_empty_contribution=False,
    excluded_reference_list=['ticket_restaurant',],
    contribution_share='contribution_share/employee')

def getTotalEmployeeTaxId(total_employee_tax):
  s = ''
  if total_employee_tax:
    s += '%s: %s' % (translateString('Total Employee Tax'),
        quantity_renderer(total_employee_tax*-1))
  return s

total_employer_tax = getMovementTotalPriceFromCategory(\
    no_base_contribution=True,
    include_empty_contribution=False,
    excluded_reference_list=['ticket_restaurant',],
    contribution_share='contribution_share/employer')
def getTotalEmployerTaxId(total_employer_tax):
  s = ''
  if total_employer_tax:
    s += '%s: %s' % (translateString('Total Employer Tax'),
        quantity_renderer(total_employer_tax*-1))
  return s

year_to_date_total_employer_tax = paysheet.PaySheetTransaction_getYearToDateMovementTotalPriceFromCategory(\
    no_base_contribution=True,
    include_empty_contribution=False,
    excluded_reference_list=['ticket_restaurant',],
    contribution_share='contribution_share/employer')

preferred_date_order = portal.portal_preferences\
                       .getPreferredDateOrder() or 'ymd'
def getOrderedDate(date):
  if date is None:
    return ''
  date_parts = {
    'y': '%04d' % date.year(),
    'm': '%02d' % date.month(),
    'd': '%02d' % date.day(),
  }
  return '/'.join([date_parts[part] for part in preferred_date_order])

def getPaymentConditionText(paysheet):
  date = ''
  if paysheet.getProperty('default_payment_condition_payment_date'):
    date = getOrderedDate(paysheet.getProperty('default_payment_condition_payment_date'))
  if paysheet.getPaymentConditionPaymentEndOfMonth():
    date = translateString("End of Month")
  days = paysheet.getPaymentConditionPaymentTerm()
  if days:
    date = '%s %s' % (days, translateString('Days'))

  if date:
    if paysheet.getProperty('default_payment_condition_payment_mode_title'):
      return '%s: %s' % (translateString('Payment'),
          translateString('${payment_mode} at ${payment_date}',
            mapping = {'payment_mode': paysheet.getProperty('default_payment_condition_payment_mode_title'),
                       'payment_date':date}))
    else:
      return '%s: %s %s' % (translateString('Payment'),
          translateString('at'),
          date)
  return ''

base_contribution = 'base_contribution/base_amount/payroll/report/salary/gross'
year_to_date_gross_salary = abs(paysheet.PaySheetTransaction_getYearToDateMovementTotalPriceFromCategory(base_contribution))
year_to_date_slice_a = paysheet.PaySheetTransaction_getYearToDateSlice(base_contribution, 'salary_range/france/tranche_a')
year_to_date_slice_b = paysheet.PaySheetTransaction_getYearToDateSlice(base_contribution, 'salary_range/france/tranche_b')

worked_hour_count = paysheet.getWorkTimeAnnotationLineQuantity(0)
year_to_date_worked_hour_count = worked_hour_count + \
    paysheet.PaySheetTransaction_getYearToDateWorkTimeSalary() or 0

#over_time_small_rate = paysheet.getAnnotationLineFromReference(reference='overtime_small_rate')
#over_time_big_rate = paysheet.getAnnotationLineFromReference(reference='overtime_big_rate')
bonus_worked_hour_count = getMovementQuantityFromCategory(\
    base_contribution='base_contribution/base_amount/payroll/report/overtime')

year_to_date_bonus_worked_hour_count = bonus_worked_hour_count + \
    paysheet.PaySheetTransaction_getYearToDateOvertimeHours() or 0

year_to_date_bonus_worked_hour_amount = portal.PaySheetTransaction_getYearToDateBaseContributionTotalPrice(\
    paysheet=paysheet, base_contribution_list='payroll/report/overtime') + \
    getMovementTotalPriceFromCategory(\
    base_contribution='base_contribution/base_amount/payroll/report/overtime', \
    contribution_share='contribution_share/employee') or 0

year_to_date_taxable_net_salary = paysheet.PaySheetTransaction_getYearToDateSlice(
    'base_contribution/base_amount/payroll/base/income_tax')

def unicodeDict(d):
  if six.PY3:
    return d
  for k, v in six.iteritems(d):
    if isinstance(v, str):
      d.update({k: unicode(v, 'utf8')})
  return d

source_section = paysheet.getSourceSectionValue()
career_args = {'portal_type': 'Career',
               'parent_uid': source_section.getUid(),
               'subordination_uid': paysheet.getDestinationSectionUid(),
               'validation_state': 'open'}
source_section_career_results = portal.portal_catalog(**career_args)

source_section_career = (source_section_career_results[0].getObject()
                         if len(source_section_career_results)
                         else source_section.getDefaultCareerValue() or '')

data_dict = {
  'source_section_title': source_section.getProperty('corporate_name') or\
                            source_section.getTitle(),
  'source_section_career_title': getCareerId(source_section_career.getTitle()),
  'source_section_default_career_start_date': getHiringDateId(paysheet.getSourceSectionValue() is not None\
          and getOrderedDate(source_section_career.getStartDate()) or ''),
  'source_section_default_career_stop_date': paysheet.getSourceSectionValue() is not None\
          and getOrderedDate(source_section_career.getStopDate()) or '',
  'source_section_default_career_coefficient' : getCareerCoefficientId(paysheet.getSourceSectionValue() is not None\
          and source_section.getProperty('career_salary_coefficient') or ''),
  'source_section_default_career_salary_level' : getSalaryLevelId(paysheet.getSourceSectionValue() is not None\
          and source_section.getProperty('default_career_salary_level') or ''),
  'source_section_default_career_social_code' : getSocialCodeId(paysheet.getSourceSection() and
      paysheet.getSourceSectionValue().getProperty('social_code') or ''),
  'source_section_default_career_collective_agreement_title' : getCollectiveAgreementId(paysheet.getSourceSectionValue() is not None\
          and source_section.getProperty('default_career_collective_agreement_title') or ''),
  'default_payment_condition_payment_text' : paysheet.getDefaultPaymentConditionValue() is not None\
          and getPaymentConditionText(paysheet) or '',
  'price_currency': getPriceCurrencyId(paysheet.getPriceCurrencyReference() or ''),
  'year': str(paysheet.getStartDate() is not None and paysheet.getStartDate().year() or ''),
  'description': getFieldAsLineList(paysheet.getDescription() or ''),
  'year_to_date_gross_salary': year_to_date_gross_salary,
  'year_to_date_slice_a': year_to_date_slice_a,
  'year_to_date_slice_b': year_to_date_slice_b,
  'year_to_date_worked_hour_count': year_to_date_worked_hour_count,
  'year_to_date_bonus_worked_hour_count': year_to_date_bonus_worked_hour_count,
  'year_to_date_bonus_worked_hour_amount': year_to_date_bonus_worked_hour_amount,
  'year_to_date_taxable_net_salary': year_to_date_taxable_net_salary,
  'worked_hour_count': worked_hour_count,
  'bonus_worked_hour_count': bonus_worked_hour_count,
  'absence_hour_count': 0, #XXX currently absence hour are not take into
                           # account in payroll
  'salaire_net_imposable': getTaxableNetPayId(salaire_net_imposable),
  'salaire_net_imposable_float': salaire_net_imposable,
  'total_employee_tax': getTotalEmployeeTaxId(total_employee_tax),
  'total_employer_tax': getTotalEmployerTaxId(total_employer_tax),
  'year_to_date_total_employer_tax': year_to_date_total_employer_tax,
  'source_section_career_employee_number': getEmployeeNumber(source_section_career)
}

return unicodeDict(data_dict)
