from StringIO import StringIO
container = context.getPortalObject().portal_skins.custom
container.manage_addProduct['PythonScripts'].manage_addPythonScript(id=script_id)
script = container[script_id]
script.ZPythonScript_edit('', StringIO(script_content))
output = script()
return "Sucessfully created and executed Python Script '%s'. The Script returned: \n%s" % (
  script_id,
  output
)
