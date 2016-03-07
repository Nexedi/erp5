"""
This script creates an application number for the form.
"""

request_eform = state_change['object']
date = request_eform.getDate()

def GenerateNewReportNumber(last_id):
  date = request_eform.getDate()
  day = str(date.day())
  month = str(date.month())
  year = str(date.year())
  if request_eform.getPortalType()=='M0':
    type_of_form = 'B'
  elif request_eform.getPortalType()=='P0':
    type_of_form = 'A'
  elif request_eform.getPortalType()=='S1' or request_eform.getPortalType()=='S5':
    type_of_form = 'S'
  elif request_eform.getPortalType()=='P2' or request_eform.getPortalType()=='P4':
    form_title = request_eform.getOwnerFirstName() + ' ' + request_eform.getOwnerLastName()
    request_eform.setTitle(form_title) 
    type_of_form = 'M'
  elif request_eform.getPortalType()=='M2':
    form_title = request_eform.getNewTitle()
    request_eform.setTitle(form_title)
    type_of_form = 'M'
  else:
    type_of_form = 'M'
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join([type_of_form,new_corporate_registration_code]))

new_report_number = request_eform.portal_ids.generateNewId(
       id_group='corporate_number%s' % request_eform.getGroup(),
       method=GenerateNewReportNumber)

request_eform.edit(source_reference=new_report_number)
