import os.path
root, ext = os.path.splitext(file_path)
assert ext == ".py", "file_path must be a python file"
component_id = os.path.basename(root)
portal = context.getPortalObject()
component = portal.portal_components[component_id]
script.writeLocalFile(file_path, component.getTextContent())
return "Successfully updated component '%s' from path '%s'" %(component_id, file_path)
