previous_tag = tag
current_tag = tag
index = 0
for me in context.portal_catalog(
  portal_type='Manufacturing Execution',
  simulation_state = 'confirmed',
  strict_ledger_uid = (
    context.portal_categories.ledger.manufacturing.quality_insurance.getUid(),
    context.portal_categories.ledger.manufacturing.electronic_insurance.getUid())
):
  current_tag = '%s-%s' % (tag, index)
  me.activate(
    after_tag= previous_tag,
    tag=current_tag,
    after_path_and_method_id = (me.getPath(), ('_updateSimulation', 'updateCausalityState'))
  ).ManufacturingExecution_buildQualityAssurance()
  previous_tag = current_tag
  index += 1


context.activate(after_tag=current_tag).getId()
