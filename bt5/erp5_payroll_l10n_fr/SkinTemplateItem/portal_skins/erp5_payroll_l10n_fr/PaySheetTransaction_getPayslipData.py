from DateTime import DateTime
import six

line_dict_list = context.PaySheetTransaction_getLineListAsDict()
non_subject_amount = 'base_amount/payroll/report_section/l10n/fr/amount_non_subject_to_contribution'
gross_category = 'base_amount/payroll/report/salary/gross'
net_social = 'base_amount/payroll/report/salary/net_social'
contribution_relief = 'base_amount/payroll/report_section/l10n/fr/contribution_relief'
income_tax = 'base_amount/payroll/report_section/l10n/fr/income_tax'
csg_crds_taxable_to_income_tax = 'base_amount/payroll/report_section/l10n/fr/csg_crds_taxable_to_income_tax'
csg_non_taxable_to_income_tax = 'base_amount/payroll/report_section/l10n/fr/csg_non_taxable_to_income_tax'
report_section_to_group_list=[
  'base_amount/payroll/report_section/l10n/fr/family-social_security',
  'base_amount/payroll/report_section/l10n/fr/unemployment_insurance',
  'base_amount/payroll/report_section/l10n/fr/other_employer_contributions',
  'base_amount/payroll/report_section/l10n/fr/work_accident-occupational_disease',
  'base_amount/payroll/report_section/l10n/fr/contribution_relief']

contribution_line_list = []
no_contribution_line_list = []
income_tax_dict = {
  'base': 0,
  'employee_price': 0,
  'employee_total_price': 0
}
csg_base = 0
total_contribution_relief = 0


def getReportSectionTitle(title):
  if 'report_section' in title:
    return context.portal_categories.restrictedTraverse(title).getTitle()
  return title

def getFakeLineDictForNewSection(title, base=0, employer_price=0, employer_total_price=0, employee_price=0, employee_total_price=0, report_section=False):
  style_class = ['report-title']
  if report_section:
    style_class.append('report-section')
  return  {
    'style_class': style_class,
    'title': context.Base_translateString(title).upper(),
    'base': base,
    'employer_price': employer_price,
    'employer_total_price': employer_total_price,
    'employee_price': employee_price,
    'employee_total_price': employee_total_price
  }

def groupSameReportSectionLine(line_to_group_list):
  tmp_base_dict = {}
  tmp2_base_dict = {}
  title = getReportSectionTitle(line_to_group_list[0]['report_section'])
  # First group by base amount
  for line_dict in line_to_group_list:
    base = line_dict['base']
    if base not in tmp_base_dict:
      tmp_base_dict[base] = getFakeLineDictForNewSection(title,base)
    tmp_base_dict[base]['employer_price'] = tmp_base_dict[base]['employer_price'] + (line_dict['employer_price'] or 0)
    tmp_base_dict[base]['employer_total_price'] = tmp_base_dict[base]['employer_total_price'] + (line_dict['employer_total_price'] or 0)
    tmp_base_dict[base]['employee_price'] = tmp_base_dict[base]['employee_price'] + (line_dict['employee_price'] or 0)
    tmp_base_dict[base]['employee_total_price'] = tmp_base_dict[base]['employee_total_price'] + (line_dict['employee_total_price'] or 0)
 # Check if can group by same rate
  for value in six.itervalues(tmp_base_dict):
    new_key = (value['employer_price'], value['employee_price'])
    if new_key not in tmp2_base_dict:
      tmp2_base_dict[new_key] = value
    else:
      tmp2_base_dict[new_key]['base'] = tmp2_base_dict[new_key]['base'] + value['base']
      tmp2_base_dict[new_key]['employer_total_price'] = tmp2_base_dict[new_key]['employer_total_price'] + value['employer_total_price']
      tmp2_base_dict[new_key]['employee_total_price'] = tmp2_base_dict[new_key]['employee_total_price'] + value['employee_total_price']
  new_value_list = []
  # recalculate for rounding issue
  for _, value_dict in sorted(tmp2_base_dict.items()):
    value_dict['employer_total_price'] = value_dict['base'] * value_dict['employer_price']
    value_dict['employee_total_price'] = value_dict['base'] * value_dict['employee_price']
    new_value_list.append(value_dict)
  return new_value_list



def getReportSectionDictList(line_dict_list):
  new_line_dict_list = []
  previous_line_dict = None
  previous_report_section = None
  line_to_group_list = []
  exception_line = True
  employee_total_price = 0
  employer_total_price = 0

  for current_line_dict in line_dict_list:
    current_report_section = current_line_dict['report_section']
    # New section
    if previous_report_section != current_report_section:
      if len(line_to_group_list):
        new_line_dict_list += groupSameReportSectionLine(line_to_group_list)
        exception_line = True
        line_to_group_list = []

    # add one line for gross salary
    if (previous_line_dict is not None
      and gross_category in previous_line_dict['base_contribution_list']  # pylint:disable=unsubscriptable-object
      and gross_category not in current_line_dict['base_contribution_list']):
      new_line_dict_list.append(
        getFakeLineDictForNewSection(
          context.Base_translateString("Gross Salary"),
          base=context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/%s"%gross_category),
          report_section=True
        ))

    if current_line_dict['report_section'] in report_section_to_group_list:
      line_to_group_list.append(current_line_dict)
    else:
      if previous_report_section != current_report_section:
        new_line_dict_list.append(getFakeLineDictForNewSection(getReportSectionTitle(current_report_section)))
      # same report section, but few lines need to group but other not
      if len(line_to_group_list) and exception_line:
        exception_line = False
        new_line_dict_list.append(getFakeLineDictForNewSection(getReportSectionTitle(current_report_section)))
      new_line_dict_list.append(current_line_dict)

    previous_report_section = current_report_section
    previous_line_dict = current_line_dict
    employer_total_price += (current_line_dict['employer_total_price'] or 0)
    employee_total_price += (current_line_dict['employee_total_price'] or 0)
  if len(line_to_group_list):
    new_line_dict_list += groupSameReportSectionLine(line_to_group_list)
  return new_line_dict_list, employer_total_price, employee_total_price

non_contribution_share_total_price = 0
# split line list to differents categories
for line_dict in line_dict_list:
  added_to_list = False
  for base_contribution in line_dict['base_contribution_list']:
    if base_contribution.startswith('base_amount/payroll/report_section/l10n/fr/'):
      added_to_list = True
      if base_contribution == income_tax:
        # Not add to list since income tax is show at other place
        income_tax_dict = {
          'base': line_dict['base'],
          'employee_price': line_dict['employee_price'],
          'employee_total_price': line_dict['employee_total_price']
        }
      else:
        if base_contribution == contribution_relief:
          total_contribution_relief += (line_dict['base'] * line_dict['employer_price']) #line_dict['employer_total_price']
        elif base_contribution in (csg_crds_taxable_to_income_tax, csg_non_taxable_to_income_tax):
          csg_base = line_dict['base']
        line_dict['report_section'] = base_contribution
        if base_contribution == non_subject_amount:
          if (line_dict['employee_total_price'] is None) and (line_dict['employer_total_price'] is None):
            line_dict['employee_total_price'] = line_dict['base']
            non_contribution_share_total_price += line_dict['base']
          no_contribution_line_list.append(line_dict)
        else:
          contribution_line_list.append(line_dict)
      break

  if not added_to_list:
    line_dict['report_section'] = line_dict['group']
    contribution_line_list.append(line_dict)

contribution_dict_list, contribution_employer_total_price, contribution_employee_total_price = getReportSectionDictList(contribution_line_list)
# fix rounding issue
contribution_employee_total_price = context.PaySheetTransaction_getMovementTotalPriceFromCategory(
  no_base_contribution=True,
  include_empty_contribution=False,
  excluded_reference_list=['ticket_restaurant', 'versement_interessement_pee', 'impot_revenu'],
  contribution_share='contribution_share/employee'
)
contribution_employer_total_price = context.PaySheetTransaction_getMovementTotalPriceFromCategory(
  no_base_contribution=True,
  include_empty_contribution=False,
  excluded_reference_list=['ticket_restaurant',],
  contribution_share='contribution_share/employer'
)

if len(contribution_dict_list):
  contribution_dict_list.append(
    getFakeLineDictForNewSection(
      context.Base_translateString("Total Contributions"),
      employer_total_price=contribution_employer_total_price,
      employee_total_price=contribution_employee_total_price,
      report_section=True
    ))

non_contribution_dict_list, non_contribution_employer_total_price, non_contribution_employee_total_price = getReportSectionDictList(no_contribution_line_list)
if len(non_contribution_dict_list):
  non_contribution_dict_list.append(
    getFakeLineDictForNewSection(
      context.Base_translateString("Total Amounts Non Subject To Contributions"),
      employer_total_price=non_contribution_employer_total_price,
      employee_total_price=non_contribution_employee_total_price,
      report_section=True
    ))

gross_salary = context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/%s"%gross_category)

net_social = context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/%s"%net_social)

# Set contribution_share to 'True' so it will return all movement with 0 contribution share

total_pay_by_employer = context.PaySheetTransaction_getMovementTotalPriceFromCategory(
  base_contribution='base_contribution/base_amount/payroll/report/salary/net',
  contribution_share='True') - contribution_employer_total_price - non_contribution_employer_total_price - non_contribution_share_total_price


net_salary = context.PaySheetTransaction_getMovementTotalPriceFromCategory(
  base_contribution='base_contribution/base_amount/payroll/report/salary/net',
  contribution_share='contribution_share/employee')


net_salary_before_income_tax = net_salary - income_tax_dict['employee_total_price']
currency = context.getPriceCurrencyValue() is not None and context.getPriceCurrencyValue().getShortTitle() or context.getPriceCurrencyReference() or ''

"""
from 01/01/18 to 30/09/18
amount = gross_salary * 2.2% - CSG * 1.7%
from 01/10/2018
amount = gross_salary * 3.15% - CSG * 1.7%
"""
amount_of_remuneration_evolution = 0
start_date = context.getStartDate()
if DateTime('2018/01/01') <= start_date <= DateTime('2018/09/30'):
  amount_of_remuneration_evolution = gross_salary * 0.022 - csg_base * 0.017
elif start_date >= DateTime('2018/10/01'):
  amount_of_remuneration_evolution = gross_salary * 0.0315 - csg_base * 0.017

net_social = net_social + gross_salary + contribution_employee_total_price
return {
  "contribution_dict_list": contribution_dict_list,
  "non_contribution_dict_list": non_contribution_dict_list,
  "gross_salary": gross_salary,
  "net_salary_before_income_tax": net_salary_before_income_tax,
  "net_salary": net_salary,
  "net_social": net_social,
  "currency": currency,
  "amount_of_remuneration_evolution": amount_of_remuneration_evolution,
  "income_tax_dict": income_tax_dict,
  'total_pay_by_employer': total_pay_by_employer,
  'total_contribution_relief': total_contribution_relief
}
