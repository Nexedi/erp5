from Products.PythonScripts.standard import Object
from DateTime import DateTime

request = context.REQUEST
portal = context.getPortalObject()

net_salary_base_amount_uid = \
              portal.portal_categories.base_amount.payroll.report.salary.net.getUid()
employee_contribution_share_uid = \
              portal.portal_categories.contribution_share.employee.getUid()

section_category = request['section_category']
section_uid = portal.Base_getSectionUidListForSectionCategory(section_category)

# currency precision
currency = portal.Base_getCurrencyForSection(section_category)
precision = portal.account_module.getQuantityPrecisionFromResource(currency)
request.set('precision', precision)

from_date = None
if request.get('from_date'):
  from_date = DateTime(request['from_date'])
at_date = DateTime(request['at_date'])
simulation_state = request['simulation_state']

ledger = request.get('ledger', None)

object_list = []
total_price = 0

# FIXME: this report does not support multiple Payment Condition
for inventory in portal.portal_simulation.getInventoryList(
                    parent_base_contribution_uid=net_salary_base_amount_uid,
                    contribution_share_uid=employee_contribution_share_uid,
                    portal_type=('Pay Sheet Line', 'Pay Sheet Cell'),
                    section_uid=section_uid,
                    simulation_state=simulation_state,
                    precision=precision,
                    from_date=from_date,
                    at_date=at_date,
                    only_accountable=False,
                    group_by_resource=0,
                    group_by_node=1,
                    ledger=ledger, ):
  price = inventory.total_price or 0
  total_price += price
  movement = inventory.getObject()
  employee = movement.getDestinationValue()
  employee_bank_account = movement.getExplanationValue()\
                                      .getDefaultPaymentConditionSourcePaymentTitle()

  object_list.append(
      Object(uid=-1,
             employee_career_reference=employee.getCareerReference(),
             employee_title=employee.getTitle(),
             employee_bank_account=employee_bank_account,
             total_price=price))

request.set('total_price', total_price)

return sorted(
  object_list,
  key=lambda o: (o.employee_career_reference or '', o.employee_title)
)
