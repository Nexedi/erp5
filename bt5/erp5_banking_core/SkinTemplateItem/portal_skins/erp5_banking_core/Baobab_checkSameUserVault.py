# this script compare a given vault to the one of the assignment of the current user
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

site_list = context.Baobab_getUserAssignedSiteList()
for site in site_list:
  if site in vault:
    return

msg = Message(domain = "ui", message="Vault differ between initialisation and transition")
raise ValidationFailed(msg,)
