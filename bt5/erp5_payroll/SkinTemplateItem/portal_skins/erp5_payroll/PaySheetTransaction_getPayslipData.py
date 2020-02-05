from DateTime import DateTime


line_dict_list = context.PaySheetTransaction_getLineListAsDict()
new_line_dict_list = []
previous_line_dict = None
previous_report_section = None
gross_category = 'base_amount/payroll/report/salary/gross'
line_to_group_list = []
exception_line = True


def getReportSectionTitle(title):
  if title.startswith('report_section'):
    return context.portal_categories.restrictedTraverse(title).getTitle()
  return title

def getFakeLineDictForNewSection(title, base=0, employer_price=0, employer_total_price=0, employee_price=0, employee_total_price=0):
  return  {
    'title': title.upper(),
    'base': base,
    'employer_price': employer_price,
    'employer_total_price': employer_total_price,
    'employee_price': employee_price,
    'employee_total_price': employee_total_price
  }

def groupSameReportSectionLine(line_to_group_list):
  tmp_base_dict = {}
  title = getReportSectionTitle(line_to_group_list[0]['report_section'])
  for line_dict in line_to_group_list:
    base = line_dict['base']
    if base not in tmp_base_dict:
      tmp_base_dict[base] = getFakeLineDictForNewSection(title,base)
    tmp_base_dict[base]['employer_price'] = tmp_base_dict[base]['employer_price'] + (line_dict['employer_price'] or 0)
    tmp_base_dict[base]['employer_total_price'] = tmp_base_dict[base]['employer_total_price'] + (line_dict['employer_total_price'] or 0)
    tmp_base_dict[base]['employee_price'] = tmp_base_dict[base]['employee_price'] + (line_dict['employee_price'] or 0)
    tmp_base_dict[base]['employee_total_price'] = tmp_base_dict[base]['employee_total_price'] + (line_dict['employee_total_price'] or 0)
  new_value_list = []
  for _, value in tmp_base_dict.iteritems():
    new_value_list.append(value)
  return new_value_list


employer_total_price = 0
employee_total_price = 0
for current_line_dict in line_dict_list:
  if current_line_dict['resource_title'].startswith('CSG'):
    csg_base = current_line_dict['base']
  current_report_section = current_line_dict['report_section'] or current_line_dict['group']
  # New section
  if previous_report_section != current_report_section:
    if len(line_to_group_list):
      new_line_dict_list += groupSameReportSectionLine(line_to_group_list)
      exception_line = True
      line_to_group_list = []

    if current_report_section == 'report_section/payroll/fr/amount_not_subject_to_contribution':
      new_line_dict_list.append(
        getFakeLineDictForNewSection(
          context.Base_translateString("TOTAL FEES AND CONTRIBUTIONS"),
          employer_total_price=employer_total_price,
          employee_total_price=employee_total_price))
      employer_total_price = 0
      employee_total_price = 0
  # add one line for gross salary
  if previous_line_dict is not None and gross_category in previous_line_dict['base_contribution_list'] and gross_category not in current_line_dict['base_contribution_list']:
    new_line_dict_list.append(
      getFakeLineDictForNewSection(
        context.Base_translateString("Gross Salary"),
        base=context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/%s"%gross_category)))

  if current_line_dict['group_by_report_section']:
    line_to_group_list.append(current_line_dict)
  else:
    if previous_report_section != current_report_section:
      new_line_dict_list.append(getFakeLineDictForNewSection(getReportSectionTitle(current_report_section)))
    if len(line_to_group_list) and exception_line:
      exception_line = False
      new_line_dict_list.append(getFakeLineDictForNewSection(getReportSectionTitle(current_report_section)))
    new_line_dict_list.append(current_line_dict)

  employer_total_price += (current_line_dict['employer_total_price'] or 0)
  employee_total_price += (current_line_dict['employee_total_price'] or 0)
  previous_report_section = current_report_section
  previous_line_dict = current_line_dict

new_line_dict_list.append(
  getFakeLineDictForNewSection(
    context.Base_translateString("TOTAL AMOUNTS NOT SUBJECT TO CONTRIBUTIONS"),
    employer_total_price=employer_total_price,
    employee_total_price=employee_total_price))

gross_salary = context.PaySheetTransaction_getMovementTotalPriceFromCategory(base_contribution="base_contribution/%s"%gross_category)
net_salary = context.PaySheetTransaction_getMovementTotalPriceFromCategory(
  base_contribution='base_contribution/base_amount/payroll/report/salary/net',
  contribution_share='contribution_share/employee')
currency = context.getPriceCurrencyValue() is not None and context.getPriceCurrencyValue().getShortTitle() or context.getPriceCurrencyReference() or ''

start_date = context.getStartDate()
amount_benefit = 0
if DateTime('2018/01/01') <= start_date <= DateTime('2018/09/30'):
  amount_benefit = gross_salary * 0.022 - csg_base * 0.017
elif start_date >= DateTime('2018/10/01'):
  amount_benefit = gross_salary * 0.0315 - csg_base * 0.017




return {
  "payslip_line_list": new_line_dict_list,
  "gross_salary": gross_salary,
  "net_salary": net_salary,
  "currency": currency,
  "amount_benefit": amount_benefit
}
