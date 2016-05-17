# TODO: domain names should be exported to a web site property.
#   domain_dict = {}
#   for web_site in portal_catalog(portal_type="Web Site", validation_state="published"):
#     domain = web_site.getDomainName("")
#     if domain != "":
#       domain_dict[domain] = web_site
#   return domain_dict
w = context.getPortalObject().web_site_module
return {
  "www.erp5.com": w.erp5_com_simplicity,
  "www.nexedi.com": w.nexedi_com_simplicity,
  "img.erp5.cn": w.erp5_community,
  "www.nexedi.co.jp": w.nexedi_japan,
  "www.osoe-project.org": w.osoe,
  "www.officejs.org": w.officejs,
  "www.neoppod.org": w.neoppod,
  "www.renderjs.org": w.renderjs,
  "www.j-io.org": w.jio,
  "www.vifib.com": w.vifib_resilience,
  "www.wendelin.io": w.wendelin,
  "jabberclient.app.officejs.com": w.jabber_client,
  "texteditor.app.officejs.com": w.officejs_text_editor,
  "spreadsheet.app.officejs.com": w.officejs_spreadsheet,
}
