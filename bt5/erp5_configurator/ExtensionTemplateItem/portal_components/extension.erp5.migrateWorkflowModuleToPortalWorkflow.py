def titleToReference(title):
  reference = title.replace(' ', '_').lower()
  return reference

def migrateToERP5Workflow(portal_workflow, configurator_workflow):
  """
  Convert Configurator Workflow (workflow_module/*) to ERP5 Workflow.
  """
  workflow_id = configurator_workflow.getId()
  relative_url = "%s/%s" % (portal_workflow.getRelativeUrl(), workflow_id)
  def getCategoryList(prefix, category_value_list):
    return ['%s/%s%s' % (relative_url, prefix, titleToReference(o.getTitle()))
            for o in category_value_list ]

  workflow = portal_workflow.newContent(
    portal_type='Workflow',
    reference=configurator_workflow.getId(),
    comment=configurator_workflow.getComment(),
    description=configurator_workflow.getDescription(),
    state_base_category=configurator_workflow.getProperty('state_base_category'),
    state_variable=configurator_workflow.getProperty('state_variable_name'),
    source_list=getCategoryList('state_', configurator_workflow.getSourceValueList()),
    # ConfiguratorWorkflow PropertySheet
    configuration_after_script_id=configurator_workflow.getConfigurationAfterScriptId())
  for business_configuration in configurator_workflow.getRelatedValueList(
      portal_type='Business Configuration'):
    business_configuration.setResourceValue(workflow)

  for subobject in configurator_workflow.objectValues():
    title = subobject.getTitle()
    reference = titleToReference(title)

    if subobject.getPortalType() == 'State':
      state = workflow.newContent(
        portal_type='Workflow State',
        reference=reference,
        title=title,
        destination_list=getCategoryList('transition_', subobject.getDestinationValueList()),
        comment=subobject.getComment(),
        description=subobject.getDescription())
      for business_configuration in subobject.getRelatedValueList(
          portal_type='Business Configuration'):
        business_configuration.setCurrentStateValue(state)

    elif subobject.getPortalType() == 'Transition':
# XXX_1: Workflows only call Workflow Script and do not call Python Script in
#        portal_skins but Configurator Workflows do. For now leave them as they
#        ({before,after}_script_id property) but they should be migrated later on.
#
#      def addWorkflowScript(script_id_property):
#        old_script_id = getattr(subobject.aq_base, script_id_property, None)
#        if old_script_id:
#          old_script = portal_workflow.getPortalObject().unrestrictedTraverse(old_script_id)
#          script = workflow.newContent(id=workflow.getScriptIdByReference(old_script.id),
#                                       portal_type='Workflow Script')
#          script.defeault_reference = old_script.id
#          script.setTitle(old_script.title)
#          script.setParameterSignature('state_change')
#          script.setBody(old_script._body)
#          script.setProxyRole(old_script._proxy_roles)
#          return script
#      before_script_value = addWorkflowScript('before_script_id')
#      after_script_value = addWorkflowScript('after_script_id')

      transition = workflow.newContent(
        portal_type='Workflow Transition',
        reference=reference,
        title=title,
        destination_list=getCategoryList('state_', subobject.getDestinationValueList()),
        comment=subobject.getComment(),
        description=subobject.getDescription(),
# XXX_1: before_script_value=before_script_value,
#        after_script_value=after_script_value,
        guard_expression=subobject.getProperty('guard_expression'),
        # ConfiguratorWorkflowTransition Property Sheet
        transition_form_id=subobject.getProperty('transition_form_id'))
# XXX_1: Should use the normal {before,after}_script Workflow Property.
      try:
        transition.before_script_id = subobject.aq_base.before_script_id
      except AttributeError:
        pass
      try:
        transition.after_script_id = subobject.aq_base.after_script_id
      except AttributeError:
        pass
      # XXX: Transition Variable: Not used in erp5.git, used elsewhere?

    elif subobject.getPortalType() == 'Variable':
      if reference in ('action',
                       'actor',
                       'comment',
                       'error_message',
                       'history',
                       'portal_type',
                       'time'):
        continue

      workflow.newContent(
        portal_type='Workflow Variable',
        reference=reference,
        title=title,
        description=subobject.getDescription(),
        automatic_update=subobject.getAutomaticUpdate(),
        variable_default_expression=subobject.aq_base.initial_value,
        comment=subobject.getComment())

    # default_image
    elif subobject.getPortalType() == 'Embedded File':
      copy_data = configurator_workflow.manage_copyObjects([subobject.getId()])
      workflow.manage_pasteObjects(copy_data)

    else:
      raise NotImplementedError(
        "%s: Portal Type '%s'" % (subobject.getRelativeUrl(),
                                  subobject.getPortalType()))

  return workflow

def migrateWorkflowModuleToPortalWorkflow(self, recreate=False):
  """
  Migrate workflow_module to new-style ERP5Workflows: workflow_module was implemented
  for Configurators, based on DCWorkflow (portal_workflow), and a step towards migrating
  DCWorkflows to ERP5 Objects. Now that portal_workflow is a real ERP5 Object, these must
  be migrated to portal_workflow.
  """
  portal = self.getPortalObject()
  try:
    workflow_module = portal.workflow_module
  except AttributeError:
    return "Nothing to do as workflow_module does not exist."
  portal_workflow = portal.portal_workflow
  assert portal_workflow.getPortalType() == 'Workflow Tool'

  from zLOG import LOG
  for configurator_workflow in workflow_module.objectValues():
    id_ = configurator_workflow.getId()
    if id_ in portal_workflow:
      if not recreate:
        continue
      portal_workflow._delOb(id_)

    new_workflow = migrateToERP5Workflow(portal_workflow, configurator_workflow)
    LOG("migrateWorkflowModuleToPortalWorkflow", 0,
             "Migrated %s to %s" % (configurator_workflow.getRelativeUrl(),
                                                    new_workflow.getRelativeUrl()))

  return 'Done'