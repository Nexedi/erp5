'''This script check that all required files have been uploaded'''
from Products.DCWorkflow.DCWorkflow import ValidationFailed
document = state_change['object']
portal = document.getPortalObject()
N_ = portal.Base_translateString

if document.PDFDocument_getRequirementCount() != 0:
  message = '%s following document (s) are missing to submit the request ' % document.PDFDocument_getRequirementCount()
  message = N_(message)
  raise ValidationFailed(message)
