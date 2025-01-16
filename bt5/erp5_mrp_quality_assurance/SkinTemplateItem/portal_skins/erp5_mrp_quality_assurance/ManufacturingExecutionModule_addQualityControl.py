portal = context.getPortalObject()
translate = portal.Base_translateString

control_value_list = []

new_control_value_list = []

me_quality_list = []
manufacturing_execution_list = context.ManufacturingExecutionMovement_getOpenManufacturingExecutionList()

if not manufacturing_execution_list:
  return context.Base_redirect(
    'view',
    keep_items={
      'portal_status_message': translate('Please choose Manufacturing execution'),
      'portal_status_level': 'error'
    }
  )

if new_control_list:
  new_control_list = list(set(new_control_list))

expected_use_list = ['manufacturing/quality_control']
for control in control_list:
  value = portal.restrictedTraverse(control)
  if value.getUse() not in expected_use_list:
    return context.Base_redirect(
      'view',
      keep_items={
        "portal_status_message": translate(
          "${control} has no valid use",
          mapping = {
            'control': control.getTitle()
          }),
        'portal_status_level': 'error'
      }
    )
  control_value_list.append(value)

for me in manufacturing_execution_list:
  po = me.getCausalityValue(portal_type='Production Order')
  me_quality = po.ProductionOrder_getRelatedManufacturingExecutionDict()['quality_execution']
  if me_quality.getSimulationState() == 'delivered':
    return context.Base_redirect(
      'view',
      keep_items={
        "portal_status_message": translate(
          "${production_order} is not allowed to add quality control",
          mapping = {
            'production_order': po.getReference()
          }),
        'portal_status_level': 'error'
      }
    )
  me_quality_list.append(me_quality)

"""
how to prevent resubmit
countMessage = portal.portal_activities.countMessage
double_click_action = True
for me_quality in me_quality_list:
  if not countMessage(path=me_quality.getPath(), method_id='ManufacturingExecution_addAndConfirmNewQualityControl'):
    double_click_action = False
    break

if double_click_action:
  return context.Base_redirect(
    'view',
    keep_items={
      "portal_status_message": translate(
        "Quality controls will be added in background"
      ),
      'portal_status_level': 'success'
    }
  )

"""

for new_control in new_control_list:
  new_control_value = portal.portal_catalog.getResultValue(portal_type='Service', title=new_control)
  if new_control_value and new_control_value.getUse() not in expected_use_list:
    return context.Base_redirect(
      'view',
      keep_items={
        "portal_status_message": translate(
          "${new_control} is already existed and has no valid use",
          mapping = {
            'new_control': new_control
          }),
        'portal_status_level': 'error'
      }
    )
# check ok, now create data

for new_control in new_control_list:
  new_control_value = portal.portal_catalog.getResultValue(portal_type='Service', title=new_control)
  if new_control_value:
    new_control_value_list.append(new_control_value)
  else:
    new_control_value_list.append(portal.service_module.newContent(
      portal_type='Service',
      reference=new_control,
      title=new_control,
      use = 'manufacturing/quality_control',
      individual_variation_base_category_list=None,
    ))

control_value_list = control_value_list + new_control_value_list
if not control_value_list:
  return context.Base_redirect(
    'view',
    keep_items={
      "portal_status_message": translate(
        "No Quality control is defined"
      )
    }
  )
for me_quality in me_quality_list:
  base_application_list = []
  line_id_list = []
  for i in me_quality.objectValues(portal_type='Manufacturing Execution Line'):
    base_application_list = i.getBaseApplicationList()
    if base_application_list:
      break
  for control_value in control_value_list:
    line = me_quality.newContent(
      base_application_list = base_application_list,
      portal_type='Manufacturing Execution Line',
      quantity = -1,
      int_index = -1, # mark as manually added
      resource_value = control_value
    )
    line_id_list.append(line.getId())
  me_quality.activate(
  ).ManufacturingExecution_addAndConfirmNewQualityControl(line_id_list)


return context.Base_redirect(
  'view',
  keep_items={
    "portal_status_message": translate(
      "Quality controls will be added in background"
    ),
    'portal_status_level': 'success'
  }
)
