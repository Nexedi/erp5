transformation = state_change['object']
resource = transformation.getResourceValue()

if resource is not None:
  activate_kw=dict(after_path=transformation.getPath())
  resource.reindexObject(activate_kw=activate_kw)
