from Products.ERP5Security import SUPER_USER
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
import msgpack
import requests

def ERP5Site_bootstrapWendelinTelecomWebUiTest(self, step):
  if step not in ['ingestor_user', 'client_user', 'admin_user', 'ors']:
    raise ValueError('Unsupported bootstrap step: %s' % step)

  portal = self.getPortalObject()

  if step == 'ingestor_user':
    sm = getSecurityManager()
    try:
      newSecurityManager(None, portal.acl_users.getUser(SUPER_USER))

      ingestor_user_reference = 'web_test_ingestor_user'
      if len(
        portal.portal_catalog(
          portal_type='Person',
          reference=ingestor_user_reference
        )
      ) != 0:
        return 'Done'

      ingestor_user = portal.person_module.newContent(
        portal_type='Person',
        reference=ingestor_user_reference
      )
      ingestor_user.newContent(
        portal_type='Assignment',
        title='Ingestor',
        function='ingestor'
      ).open()
      ingestor_user.newContent(
        portal_type='ERP5 Login',
        reference=ingestor_user_reference,
        password=ingestor_user_reference
      ).validate()
      ingestor_user.validate()

    finally:
      setSecurityManager(sm)

  elif step == 'client_user':
    sm = getSecurityManager()
    try:
      newSecurityManager(None, portal.acl_users.getUser(SUPER_USER))

      client_user_reference = 'web_test_client_user'
      client_user = portal.portal_catalog.getResultValue(
        portal_type='Person',
        reference=client_user_reference,
        validation_state='validated'
      )
      if client_user is not None:
        return 'Done'

      project_reference = 'web_test_project'
      project = portal.portal_catalog.getResultValue(
        portal_type='Project',
        reference=project_reference,
        validation_state='validated'
      )
      if project is None:
        project = portal.project_module.newContent(
          portal_type='Project',
          reference=project_reference,
        )
        project.validate()

      destination_project = project.getRelativeUrl()

      client_user = portal.person_module.newContent(
        portal_type='Person',
        reference=client_user_reference
      )
      client_user.newContent(
        portal_type='Assignment',
        title='User for %s' % project_reference,
        destination_project=destination_project,
        function='user'
      ).open()
      client_user.newContent(
        portal_type='ERP5 Login',
        reference=client_user_reference,
        password=client_user_reference
      ).validate()
      client_user.validate()

    finally:
      setSecurityManager(sm)

  elif step == 'admin_user':
    sm = getSecurityManager()
    try:
      newSecurityManager(None, portal.acl_users.getUser(SUPER_USER))

      admin_user_reference = 'web_test_admin_user'
      if len(
        portal.portal_catalog(
          portal_type='Person',
          reference=admin_user_reference
        )
      ) != 0:
        return 'Done'

      admin_user = portal.person_module.newContent(
        portal_type='Person',
        reference=admin_user_reference
      )
      admin_user.newContent(
        portal_type='Assignment',
        title='Administrator',
        function='administrator'
      ).open()
      admin_user.newContent(
        portal_type='ERP5 Login',
        reference=admin_user_reference,
        password=admin_user_reference
      ).validate()
      admin_user.validate()

    finally:
      setSecurityManager(sm)

  elif step == 'ors':
    sm = getSecurityManager()
    try:
      newSecurityManager(None, portal.acl_users.getUser(SUPER_USER))

      project_reference = 'web_test_project'
      project = portal.portal_catalog.getResultValue(
        portal_type='Project',
        reference=project_reference,
        validation_state='validated'
      )
      if project is None:
        project = portal.project_module.newContent(
          portal_type='Project',
          reference=project_reference,
        )
        project.validate()

      web_test_project_url = project.getRelativeUrl()

      ors_tag_dict = {
        'ors000_COMP-0000_e0x00000Test': (
          web_test_project_url,
          None
        ),
        'ors001_COMP-0001_e0x00001Test': (
          None,
          'ORS 001 e0x00001 Test'
        ),
      }
      for ors_tag in ors_tag_dict:
        destination_project_url = ors_tag_dict[ors_tag][0]
        ors_title = ors_tag_dict[ors_tag][1]

        data_acquisition_unit = portal.portal_catalog.getResultValue(
          portal_type='Data Acquisition Unit',
          reference=ors_tag,
          validation_state='validated'
        )
        if data_acquisition_unit is None:
          data_acquisition_unit = portal.data_acquisition_unit_module.newContent(
            portal_type='Data Acquisition Unit',
            reference=ors_tag,
            title=ors_title,
          )
          data_acquisition_unit.validate()

        data_supply = data_acquisition_unit.DataAcquisitionUnit_createOrsDataSupply(batch=1)

        # Link Data Supply to project
        if destination_project_url is not None:
          data_supply.setDestinationProject(destination_project_url)

    finally:
      setSecurityManager(sm)

  return 'Done'

def ERP5Site_ingestTestLogData(self, ors_tag, ingestor_reference):
  portal = self.getPortalObject()

  # Preventing ingesting the same data more than once
  data_array = portal.portal_catalog.getResultValue(
    portal_type='Data Array',
    reference='ORS eNB Log Data Transformation-e_utran-%s' % ors_tag,
    validation_state='validated'
  )
  if data_array is not None:
    if data_array.getArrayShape() is not None \
      and data_array.getArrayShape() not in [(), (0,)]:
      return 'Done'

  ingestion_reference = 'ors.%s' % ors_tag
  log_data = {
    'log': portal.web_page_module.test_example_ors_enb_log_valid.getTextContent()
  }
  msgpack_data = msgpack.packb([0, log_data], use_bin_type=True)
  header_dict = {'CONTENT_TYPE': 'application/octet-stream'}
  ingestion_url = portal.portal_ingestion_policies.ors_enb_log_ingestion.getAbsoluteUrl() \
    + '/ingest?reference=' + ingestion_reference
  requests.post(
    ingestion_url,
    auth=(ingestor_reference, ingestor_reference),
    data={'data_chunk': msgpack_data},
    headers=header_dict,
    timeout=60,
    verify=False
  )
  return 'Done'

def ERP5Site_activateWendelinHandleAnalysisAlarmTest(self):
  portal = self.getPortalObject()

  portal.portal_alarms.wendelin_handle_analysis.activeSense()
  return 'Alarm activated'