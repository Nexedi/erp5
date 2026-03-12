from StringIO import StringIO
portal = context.getPortalObject()
container = portal.portal_skins[container_id)
container.manage_addProduct['PythonScripts'].manage_addPythonScript(id=script_id)
script = container[script_id]
script.ZPythonScript_edit(script_params, StringIO(script_content))
return "Successfully created a new Python Script '%s' in '%s'" % (
  script_id,
  skin_folder
)
