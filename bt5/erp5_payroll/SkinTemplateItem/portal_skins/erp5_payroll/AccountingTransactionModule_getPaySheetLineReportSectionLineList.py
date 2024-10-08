from Products.PythonScripts.standard import Object
from DateTime import DateTime

request = context.REQUEST
portal = context.getPortalObject()
translateString = portal.Base_translateString

section_category = request['section_category']
section_uid_list = portal.Base_getSectionUidListForSectionCategory(section_category)

# currency precision
currency = portal.Base_getCurrencyForSection(section_category)
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

from_date = None
if request.get('from_date'):
  from_date = DateTime(request['from_date'])
at_date = DateTime(request['at_date'])
simulation_state = request['simulation_state']
resource = request['resource']
ledger = request.get('ledger', None)

portal_simulation = context.getPortalObject().portal_simulation

inventory_param_dict = {
    'group_by_node' : 1,
    'group_by_variation': 1,
    'section_uid' : section_uid_list,
    'at_date' : at_date,
    'from_date' : from_date,
    'simulation_state' : simulation_state,
    'precision' : precision,
    'resource' : resource,
    'ledger' : ledger,
    'only_accountable': False,
    'portal_type' : ('Pay Sheet Line', 'Pay Sheet Cell'),
}

employee_param_dict = inventory_param_dict.copy()
employee_param_dict['contribution_share_uid'] = portal.portal_categories.contribution_share.employee.getUid()

employer_param_dict = inventory_param_dict.copy()
employer_param_dict['contribution_share_uid'] = portal.portal_categories.contribution_share.employer.getUid()

if request.get('mirror_section'):
  mirror_section = request['mirror_section']
  employee_param_dict['mirror_section'] = mirror_section
  employer_param_dict['mirror_section'] = mirror_section

employee_inventory_list = portal_simulation.getInventoryList(**employee_param_dict)
employer_inventory_list = portal_simulation.getInventoryList(**employer_param_dict)

inventory_list = {}

employee_total = 0
employer_total = 0
base_total = 0

i = 0
for inventory in employee_inventory_list:
  price = - (inventory.total_price or 0)
  movement = inventory.getObject()
  employee = movement.getDestinationValue()
  salary_range = movement.getSalaryRange()
  salary_range_title = movement.getSalaryRange() and\
                          movement.getSalaryRangeValue().getTranslatedTitle()

  i = i + 1
  inventory_list[(employee.getUid(), salary_range)] = Object(id=i,
               employee_career_reference=employee.getCareerReference(),
               employee_title=employee.getTitle(),
               employee_career_function=employee.getCareerFunctionTitle(),
               salary_range=salary_range,
               salary_range_title=salary_range_title,
               employee=price,
               base=inventory.quantity, )
  employee_total += price
  base_total += inventory.quantity

for inventory in employer_inventory_list:
  price = - (inventory.total_price or 0)
  movement = inventory.getObject()
  employee = movement.getDestinationValue()
  salary_range = movement.getSalaryRange()
  salary_range_title = movement.getSalaryRange() and\
                          movement.getSalaryRangeValue().getTranslatedTitle()

  key = (employee.getUid(), salary_range)
  if key not in inventory_list:
    inventory_list[key] = Object(id=i,
               employee_career_reference=employee.getCareerReference(),
               employee_title=employee.getTitle(),
               employee_career_function=employee.getCareerFunctionTitle(),
               employee=0,
               salary_range=salary_range,
               salary_range_title=salary_range_title,
               base=inventory.quantity, )
    base_total += inventory.quantity
    i = i + 1

  employee = inventory.getDestinationValue()
  inventory_list[key].employer = price
  inventory_list[key].total = inventory_list[key].employee + price
  employer_total += price

total = employee_total + employer_total

request.set('employee_total', employee_total)
request.set('employer_total', employer_total)
request.set('base_total', base_total)
request.set('total', total)


# sort by salary range, and add intermediate sums if needed
sorted_inventory_list = sorted(
  inventory_list.values(),
  key=lambda i: (
    i.salary_range or '',
    i.employee_career_reference or '',
    i.employee_title or '',
  ))

i = 0
intermediate_base_total = 0
intermediate_employee_total = 0
intermediate_employer_total = 0

multiple_salary_range = 0
if sorted_inventory_list:
  new_inventory_list = []

  current_salary_range = sorted_inventory_list[0]['salary_range']
  current_salary_range_title = sorted_inventory_list[0]['salary_range_title']

  for inventory in sorted_inventory_list:
    i = i+1
    inventory['id'] = i

    if inventory['salary_range'] != current_salary_range:
      multiple_salary_range = 1
      new_inventory_list.append(Object(
               employee_title=translateString('Total ${salary_range_title}',
                     mapping=dict(salary_range_title=current_salary_range_title)),
               base=intermediate_base_total,
               employee=intermediate_employee_total,
               employer=intermediate_employer_total))

      intermediate_base_total = 0
      intermediate_employee_total = 0
      intermediate_employer_total = 0

      current_salary_range = inventory['salary_range']
      current_salary_range_title = inventory['salary_range_title']

    intermediate_base_total += inventory['base']
    intermediate_employee_total += inventory.get('employee', 0)
    intermediate_employer_total += inventory.get('employer', 0)
    new_inventory_list.append(inventory)

  if multiple_salary_range:
    new_inventory_list.append(Object(
           employee_title=translateString('Total ${salary_range_title}',
                 mapping=dict(salary_range_title=current_salary_range_title)),
           base=intermediate_base_total,
           employee=intermediate_employee_total,
           employer=intermediate_employer_total))

  return new_inventory_list


return []
