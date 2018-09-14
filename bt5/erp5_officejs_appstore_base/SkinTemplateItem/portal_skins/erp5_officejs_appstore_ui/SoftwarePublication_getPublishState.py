return {
  'field_gadget_param': {
    'key': 'ojs_publish_action',
    'default': '',
    'renderjs_extra': '{"jio_key": "%s", "select": "%s", "state": "%s"}' %
      (context.getRelativeUrl(), context.SoftwarePublication_isPublished(), context.getSimulationStateTitle()),
    'url': 'gadget_ojs_appstore_publish_button.html',
    'type': 'GadgetField',
    'editable': 0
  }
}
