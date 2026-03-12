import os.path
portal = context.getPortalObject()
root, ext = os.path.splitext(file_path)
assert ext == ".py", "file_path must be a python file"
component_id = os.path.basename(root)
text_content = script.readLocalFile(file_path)
component = portal.portal_components[component_id]
component.setTextContent(text_content)
return "Successfully updated component '%s' from file_path '%s'" %(component_id, file_path)
