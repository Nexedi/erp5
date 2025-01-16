from DateTime import DateTime

ledger = context.getLedger()
if ledger not in ("manufacturing/quality_insurance", "manufacturing/electronic_insurance"):
  return []

if context.getQuantity() > 0:
  return []

if ledger == "manufacturing/quality_insurance":
  publication_section = "quality_insurance"
else:
  publication_section = "electronic_insurance"



resource_value = context.getResourceValue()

if not resource_value:
  return []
resource_use = resource_value.getUse()
use_dict = {
  "manufacturing/defect_notification": "",
  "manufacturing/quality_insurance":"",
  "manufacturing/gate": "Gate",
  "manufacturing/traceability": "Traceability",
  "manufacturing/quality_control": "Quality Control",
  "manufacturing/smon": "SMON",
  "manufacturing/acom": "ACOM"
}

if resource_use not in use_dict:
  return ['resource use: %s not in use dict: %s' % (resource_use, use_dict.keys())]
if resource_use in ("manufacturing/quality_insurance", "manufacturing/defect_notification"):
  return []

portal_type=use_dict[resource_use]

ME_insurance = context.getParentValue()

production_order = ME_insurance.getCausalityValue(portal_type='Production Order')

for me in production_order.getCausalityRelatedValueList(portal_type='Manufacturing Execution'):
  if me.getLedger() == 'manufacturing/execution':
    ME_execution = me
    break

vin = ME_execution.getAggregateValue(portal_type='VIN')


if portal_type == "Traceability":
  if not context.getAggregateValue(portal_type=portal_type):
    if not fixit:
      return ['No quality assurance element found']
    if ME_insurance.getLedger() ==  "manufacturing/quality_insurance":
      product_reference = resource_value.getReference().split('-')[-1]
    else:
      product_reference = resource_value.getReference()

    document_title = resource_value.getTitle()

    assurance_document = context.quality_assurance_module.newContent(
      portal_type=portal_type,
      title = document_title,
      reference = product_reference,
      int_index = context.getIntIndex(),
      description = resource_value.getDescription(),
      causality_value = ME_execution,
      aggregate_value = vin,
      effective_date = DateTime(),
      publication_section = publication_section
    )
    if ME_insurance.getLedger() ==  "manufacturing/quality_insurance":
      # check if really in BOM
      real_line = ME_execution.searchFolder(
        portal_type='Manufacturing Execution Line',
        limit=1,
         strict_resource_reference = product_reference)
      if real_line:
        assurance_document.edit(follow_up_value = real_line[0])

    context.setAggregateValue(assurance_document, portal_type=portal_type)
    assurance_document.plan()
    return []
  else:
    assurance_document = context.getAggregateValue(portal_type=portal_type)
    if (not assurance_document.getAggregate(portal_type="VIN")) and vin:
      assurance_document.setAggregateValue(vin, portal_type="VIN")


else:
  if not context.getAggregateValue(portal_type=portal_type):
    if not fixit:
      return ['No quality assurance element found']
    assurance_document = context.quality_assurance_module.newContent(
      portal_type=portal_type,
      title = resource_value.getTitle(),
      reference = resource_value.getReference(),
      int_index = context.getIntIndex(),
      description = resource_value.getDescription(),
      causality_value = ME_execution,
      aggregate_value = vin,
      publication_section = publication_section,
      effective_date = DateTime()
    )
    context.setAggregateValue(assurance_document, portal_type=portal_type)
    assurance_document.plan()
  else:
    assurance_document = context.getAggregateValue(portal_type=portal_type)
    if (not assurance_document.getAggregate(portal_type="VIN")) and vin:
      assurance_document.setAggregateValue(vin, portal_type="VIN")

return []
