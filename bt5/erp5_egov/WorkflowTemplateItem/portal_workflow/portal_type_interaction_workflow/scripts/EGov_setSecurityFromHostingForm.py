procedure_request = state_change['object']

nb_line = 32

# map_role_dict = {'access_type':'erp5_mapped_role_name'}
map_role_dict = {'View':'Auditor',
                 'Process':'Assignee',
                 'Validate':'Assignor',
                 'Associate':'Associate'
                }

# map_group_function_dict = {'index':['group_relative_url','function_relative_url', list(erp5_mapped_role_name)]}
map_group_function_dict = {}


# Get the procedure's target

j=0
for i in range (nb_line)[1:]:
  param_list = []
  role_list=[]
  if hasattr(procedure_request, 'getInvolvedServiceFunction%s' % i) and hasattr(procedure_request, 'getInvolvedServiceGroup%s' % i):
    getFunction = getattr(procedure_request, 'getInvolvedServiceFunction%s' % i, None)
    getGroup = getattr(procedure_request, 'getInvolvedServiceGroup%s' % i, None)
    if getFunction():
      param_list.append('function/%s' % getFunction())
    if getGroup():
      param_list.append('group/%s*' % getGroup())      

  if hasattr(procedure_request, 'getInvolvedServiceView%s' % i): 
    getView = getattr(procedure_request, 'getInvolvedServiceView%s' % i, None)
    if getView(): 
      role_list.append(map_role_dict['View'])

  if hasattr(procedure_request, 'getInvolvedServiceValidate%s' % i): 
    getValidate = getattr(procedure_request, 'getInvolvedServiceValidate%s' % i, None)
    if getValidate(): 
      role_list.append(map_role_dict['Validate'])

  if hasattr(procedure_request, 'getInvolvedServiceProcess%s' % i): 
    getProcess = getattr(procedure_request, 'getInvolvedServiceProcess%s' % i, None)
    if getProcess(): 
      role_list.append(map_role_dict['Process'])

  if hasattr(procedure_request, 'getInvolvedServiceAssociate%s' % i): 
    getAssociate = getattr(procedure_request, 'getInvolvedServiceAssociate%s' % i, None)
    if getAssociate(): 
      role_list.append(map_role_dict['Associate']) 
      
  if param_list and role_list: 
    role_definition = ','.join(role_list)
    param_list.append(role_definition)
    map_group_function_dict[j] = param_list
    j=j+1


#Create the default role for Assignee
procedure_request.newContent(portal_type='Role Information',
                     title='Default Assignee Role Information',
                     role_name='Assignee',
                     description='Last assigned person',
                     role_base_category_script_list='group function site',
                     role_base_category_script_id='ERP5Site_getSecurityFromWorkflowAssignment',
                     )

"""
#Create Associate user or service role
procedure_request.newContent(portal_type='Role Information',
                     title='Default Associate User or Service Role Information',
                     role_name_list=[Associate, Assignee],
                     description='Any associate user or service',
                     role_base_category_script_id='ERP5Site_getSecurityFromWorkflowHistory',
                     )
"""

#XXX Sometimes securities are generated using information in form
#In this case a specific function sould be used as role_base_category_script_id
for (seq,role_definition) in map_group_function_dict.items():
  role_name = role_definition[-1]
  role_name_list = role_name.split(',')
  procedure_request.newContent(portal_type='Role Information',
                     title='Role Information %s' % (seq+1),
                     role_name_list=role_name_list,
                     description='Generated Role Information - %s ' % role_name,
                     role_base_category_list='group function',
                     role_base_category_script_id='',
                     role_category_list=role_definition[:-1])
