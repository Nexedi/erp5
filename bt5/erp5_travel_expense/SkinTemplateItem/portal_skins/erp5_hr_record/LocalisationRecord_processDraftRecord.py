portal = context.getPortalObject()
record = context

if record.getSimulationState() != "draft":
  return


#user may create multi record in less one minute, so just delivry since geo location is same
for i in portal.portal_catalog(portal_type='Localisation Record', source_uid=record.getSourceUid(),simulation_state=('draft', 'stopped')):
  i.deliver()

clone = record.Base_createCloneDocument(batch_mode=True)
clone.stop()
