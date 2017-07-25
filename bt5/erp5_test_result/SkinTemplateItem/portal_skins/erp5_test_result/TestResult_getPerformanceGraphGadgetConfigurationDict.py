from base64 import urlsafe_b64encode
import json

list_method_template = ""

# list_method_template is a hack until better API is found.
# it allows to make jio.all_docs calling a python script
# http://10.0.80.187:2200/erp5/web_site_module/renderjs_runner/hateoas/ERP5Document_getHateoas
portal = context.getPortalObject()
custom_search_template_no_editable = "%(root_url)s/hateoas/%(script_id)s?mode=search" + \
                     "&relative_url=%(relative_url)s" \
                     "&list_method=%(list_method)s" \
                     "&default_param_json=%(default_param_json)s" \
                     "&test_title=%(test_title)s" \
                     "{&query,select_list*,limit*,sort_on*,local_roles*}"

list_method_template = custom_search_template_no_editable % {
        "root_url": portal.absolute_url(),
        "script_id": "TestResultModule_getTestPerfResultList",
        "relative_url": context.getRelativeUrl().replace("/", "%2F"),
        "list_method": "TestResultModule_getTestPerfResultList",
        "default_param_json": urlsafe_b64encode(json.dumps({'test_title': context.getTitle()})),
        "test_title": context.getTitle()
      }


return {'list_method_template': list_method_template}
