'''
Register a virtual ORS with the given COMP ID and tag title.
Virtual ORS follow a specific tag format: orsVIRT_COMP-<comp_id>_<tag_title>-<current_date>.
'''

from datetime import datetime

portal = context.getPortalObject()

now_date_str = datetime.today().strftime('%Y%m%d-%H%M%S')

virtual_ors_tag = 'orsVIRT_COMP-%s_%s-%s' % (comp_id, tag_title, now_date_str)

# Check if virtual ORS is already registered
data_acquisition_unit = context.portal_catalog.getResultValue(
  portal_type='Data Acquisition Unit',
  reference=virtual_ors_tag,
  validation_state='validated'
)
if data_acquisition_unit:
  if batch:
    return data_acquisition_unit
  return data_acquisition_unit.Base_redirect('view', keep_items={
    'portal_status_message': 'A virtual ORS with this tag is already registered.',
    'portal_status_level': 'error'
  })

data_acquisition_unit = portal.data_acquisition_unit_module.newContent(
  portal_type='Data Acquisition Unit',
  reference=virtual_ors_tag,
  virtual_ors=True,
)
data_acquisition_unit.validate()
# Don't redirect to new Data Supply
_ = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

if batch:
  return data_acquisition_unit
return data_acquisition_unit.Base_renderForm(
  'DataAcquisitionUnit_viewVirtualOrsInformationDialog',
  message='Virtual ORS successfully registered.',
  keep_items={
    'your_virtual_ors_tag': virtual_ors_tag
  }
)
