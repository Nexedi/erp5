"""Rewrite a python script as a regular function, with names bound.

"""
script_name = context.getId()

asgns = context.getBindingAssignments()
name_context = asgns.getAssignedName('name_context', 'context')
binding_context = binding_container = binding_script = binding_namespace = binding_subpath = ''
if name_context:
  klass = 'Base'
  if '_' in script_name:
    klass, _ = script_name.split('_', 1)
  binding_context = '{name_context} = erp5.portal_type.{klass}()'.format(
    name_context=name_context, klass=klass)
name_container = asgns.getAssignedName('name_container', 'container')
if name_container:
  binding_container = '{name_container} = {name_context}.getParentValue()'.format(
    name_container=name_container, name_context=name_context)
name_script = asgns.getAssignedName('name_script', 'script')
if name_script:
  binding_script = '{name_script} = erp5.portal_type.PythonScript()'.format(
    name_script=name_script)
name_namespace = asgns.getAssignedName('name_namespace', '')
if name_namespace:
  binding_namespace = '{name_namespace} = dict()'.format(
    name_namespace=name_namespace)
name_subpath = asgns.getAssignedName('name_subpath', 'traverse_subpath')
if name_subpath:
  binding_subpath = '{name_subpath} = ["sub", "path"]'.format(
    name_subpath=name_subpath)

parameter_signature = context.getParameterSignature()

header = """
import erp5.portal_type
{binding_context}
{binding_container}
{binding_script}
{binding_namespace}
{binding_subpath}


def {script_name}({parameter_signature}):
""".format(
  binding_context=binding_context,
  binding_container=binding_container,
  binding_script=binding_script,
  binding_namespace=binding_namespace,
  binding_subpath=binding_subpath,
  script_name=script_name,
  parameter_signature=parameter_signature)

return header
