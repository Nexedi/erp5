from erp5.component.module.DiffUtils import DiffFile
from Products.PythonScripts.standard import html_quote

def sortDiffObjectList(diff_object_list):
  return sorted(diff_object_list, key=lambda x: (x.object_state, x.object_class, x.object_id))

url_prefix = html_quote(context.getPortalObject().absolute_url())

link_configuration = {}
for key in ["Skin", "Workflow"]:
  link_configuration[key] = '<a href="' + url_prefix + '/%(object_id)s/manage_main">%(object_id)s</a>' # ZMI
link_configuration["PortalTypeWorkflowChain"] = '<a href="' + url_prefix + '/portal_workflow/manage_main">%s</a>' # ZMI
for key in ["Path", "Category", "PortalType", "Module", "PropertySheet"]:
  link_configuration[key] = '<a href="' + url_prefix + '/%(object_id)s">%(object_id)s</a>' # ERP5
for key in ["PortalTypePropertySheet", "PortalTypeBaseCategory",
            "PortalTypeBaseCategory", "PortalTypeAllowedContentType"]:
  link_configuration[key] = '<a href="' + url_prefix + '/portal_types/%(object_id)s">%(object_id)s</a>' # ERP5
link_configuration["Action"] = '<a href="' + url_prefix + '/portal_types/%(object_id)s/../BaseType_viewAction">%(object_id)s</a>' # ERP5

print("<div>")
for diff_object in sortDiffObjectList(diff_object_list):
  if getattr(diff_object, "error", None) is not None:
    print("<p>")
    print("Error")
    print(("(%s) -" % html_quote(diff_object.object_class)))
    if diff_object.object_class in link_configuration:
      print((link_configuration[diff_object.object_class] % {"object_id": html_quote(diff_object.object_id)}))
    else:
      print((html_quote(diff_object.object_id)))
    print("</p>")
    if detailed:
      print("<p>")
      print((html_quote(diff_object.error)))
      print("</p>")
  else:
    print("<p>")
    print((html_quote(diff_object.object_state)))
    print(("(%s) -" % html_quote(diff_object.object_class)))
    if diff_object.object_class in link_configuration:
      print((link_configuration[diff_object.object_class] % {"object_id": html_quote(diff_object.object_id)}))
    else:
      print((html_quote(diff_object.object_id)))
    print("</p>")
    if detailed and getattr(diff_object, "data", None) is not None:
      print("<div>")
      print((DiffFile(diff_object.data).toHTML()))
      print("</div>")
print("</div>")
return printed
