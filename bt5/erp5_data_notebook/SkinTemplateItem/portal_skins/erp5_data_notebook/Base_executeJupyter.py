"""
Python script to create Data Notebook or update existing Data Notebooks
identifying notebook by reference from user.

Expected behaviour from this script:-
1. Return unauthorized message for non-developer user.
2. Create new 'Data Notebook' for new reference.
3. Add new 'Data Notebook Line'to the existing Data Notebook on basis of reference.
4. Return python dictionary containing list of all notebooks for 'request_reference=True'
"""

portal = context.getPortalObject()
# Check permissions for current user and display message to non-authorized user 
if not portal.Base_checkPermission('portal_components', 'Manage Portal'):
  return "You are not authorized to access the script"

import json

# Convert the request_reference argument string to their respeced boolean values
request_reference = {'True': True, 'False': False}.get(request_reference, False)

# Return python dictionary with title and reference of all notebooks
# for request_reference=True
if request_reference:
  data_notebook_list = portal.portal_catalog(portal_type='Data Notebook')
  notebook_detail_list = [{'reference': obj.getReference(), 'title': obj.getTitle()} for obj in data_notebook_list]
  return notebook_detail_list

if not reference:
  message = "Please set or use reference for the notebook you want to use"
  return message

# Take python_expression as '' for empty code from jupyter frontend
if not python_expression:
  python_expression = ''

# Get Data Notebook with the specific reference
data_notebook = portal.portal_catalog.getResultValue(portal_type='Data Notebook',
                      reference=reference)

# Create new Data Notebook if reference doesn't match with any from existing ones
if not data_notebook:
  notebook_module = portal.getDefaultModule(portal_type='Data Notebook')
  data_notebook = notebook_module.DataNotebookModule_addDataNotebook(
    title=title,
    reference=reference,
    batch_mode=True
  )

# Add new Data Notebook Line to the Data Notebook
data_notebook_line = data_notebook.DataNotebook_addDataNotebookLine(
  notebook_code=python_expression,
  batch_mode=True
)

# Get active_process associated with data_notebook object
process_id = data_notebook.getProcess()
active_process = portal.portal_activities[process_id]
# Add a result object to Active Process object
result_list = active_process.getResultList()

# Get local variables saves in Active Result, local varibales are saved as
# persistent mapping object
old_local_variable_dict = result_list[0].summary
if not old_local_variable_dict:
  old_local_variable_dict = context.Base_addLocalVariableDict()

# Pass all to code Base_runJupyter external function which would execute the code
# and returns a dict of result
final_result = context.Base_runJupyter(python_expression, old_local_variable_dict)
code_result = final_result['result_string']
new_local_variable_dict = final_result['local_variable_dict']
ename = final_result['ename']
evalue = final_result['evalue']
traceback = final_result['traceback']
status = final_result['status']
mime_type = final_result['mime_type']

# Call to function to update persistent mapping object with new local variables
# and save the variables in the Active Result pertaining to the current Data Notebook
new_dict = context.Base_updateLocalVariableDict(new_local_variable_dict)
result_list[0].edit(summary=new_dict)

result = {
  u'code_result': code_result,
  u'ename': ename,
  u'evalue': evalue,
  u'traceback': traceback,
  u'status': status,
  u'mime_type': mime_type
}

# Catch exception while seriaizing the result to be passed to jupyter frontend
# and in case of error put code_result as None and status as 'error' which would
# be shown by Jupyter frontend
try:
  serialized_result = json.dumps(result)
except UnicodeDecodeError:
  result = {
    u'code_result': None,
    u'ename': u'UnicodeDecodeError',
    u'evalue': None,
    u'traceback': None,
    u'status': u'error',
    u'mime_type': mime_type
  }
  serialized_result = json.dumps(result)

data_notebook_line.edit(notebook_code_result=code_result, mime_type=mime_type)

return serialized_result
