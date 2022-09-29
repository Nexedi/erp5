portal = context.getPortalObject()
if context.getSource():
  generator_base = "free_subscription_request"
  reference_base = "FSR"
  group_reference = context.getSourceValue().getGroupReference("")
  counter = portal.portal_ids.generateNewId(
      id_generator="uid",
      id_group='.'.join((generator_base, 'reference', group_reference)),
      default=1)

  source_reference = '%s-%s-%05d' % (reference_base, group_reference, counter)
  context.setReference(source_reference)
