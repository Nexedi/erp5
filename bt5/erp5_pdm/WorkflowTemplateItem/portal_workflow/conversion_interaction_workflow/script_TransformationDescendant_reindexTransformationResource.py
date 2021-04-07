transformation = state_change['object']

# The script can be called from a Line or from a Cell
# Find the Transformation ancestor
while transformation.getPortalType() != "Transformation":
  transformation = transformation.getParentValue()

resource = transformation.getResourceValue()
if resource is not None:
  activate_kw=dict(after_path=transformation.getPath())
  resource.reindexObject(activate_kw=activate_kw)
