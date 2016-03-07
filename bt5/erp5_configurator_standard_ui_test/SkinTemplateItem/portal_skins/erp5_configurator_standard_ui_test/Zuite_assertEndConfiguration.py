portal = context.getPortalObject()
html_status_report = str(portal.portal_configurator.getInstallationStatusReport(active_process_id=2))
message_list = ["Configuration is over. Enjoy your new ERP5 system!",
                "Please click link below.",
                "You will be redirected to a form in which you can login using",
                "one of yours newly created ERP5 user accounts."]

for message in message_list:
  if not message in html_status_report:
    return 'False'

return 'True'
