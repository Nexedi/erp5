"""
================================================================================
Insert reports linked to in a document (including backcompat handling)
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------
# doc_content                string representation of document content
# doc_language               language to pass along to report for translations
# doc_format                 output format being generated

import re

document = context

# backcompat
def getReportViaFancyName(my_report_name):
  for follow_up in document_required_follow_up_list:
    #report_name = follow_up.split("insertFollowUp").pop().split("Report")[0]
    report_name = my_report_name.split("insertFollowUp").pop().split("Report")[0]
    detail_name = "Detail" in report_name
    coverage_name = "Coverage" in report_name

    # extra curl: CostEffortReport requires format (base|detailed)
    if detail_name:
      report_name = report_name.replace("Detail", "")

    #method_name = ''.join(['Base_render', report_name, 'TextDocumentReportAsHtml'])
    method_name = ''.join(['Base_generate', report_name, 'Report'])
    method_call = getattr(follow_up, method_name)
    if method_call is not None:

      # extra curl: Coverage report requires parameter details (1|0)
      if coverage_name:
        return method_call(comment_visibility=True)[0].encode(encoding='UTF-8')
      elif detail_name:
        return method_call(format='detailed',display_detail = 1)[0].encode(encoding='UTF-8')
      else:
        return method_call()[0].encode(encoding='UTF-8')

if (doc_content.find('${WebPage_')):
  document_allowed_portal_type_list = ["Project", "Sale Opportunity", "Sale Order"]
  document_required_follow_up_list = [x.getObject() for x in document.portal_catalog(
    portal_type=document_allowed_portal_type_list,
    follow_up_related_uid=document.getUid(),
    limit=1
  )]
  substitution_list = re.findall(r'\${WebPage_(.*)}', doc_content)
  for substitution_report in substitution_list:
    if substitution_report == 'insertTableOfReferences':
      continue
    placeholder = ''.join(['${WebPage_', substitution_report, '}'])
    substitution_content = getReportViaFancyName(substitution_report)
    doc_content = doc_content.replace(placeholder, substitution_content)

# new handler
# fetch reports same way as embedding documents = via links, like:
# <a href="project_module/1234?report=bam&param1=foo&param2=bar">report</a>
# retrieve relative_url, try to access, see if report is callable, if so
# call it with the parameters provided

for link in re.findall('([^[]<a.*?</a>[^]])', doc_content):
  link_reference = None
  link_reference_list = re.findall('href=\"(.*?)\"', link)
  if len(link_reference_list) == 0:
    link_reference = re.findall("href=\'(.*?)\'", link)
  if len(link_reference_list) == 0:
    link_reference = None
  if len(link_reference_list) > 0:
    link_reference = link_reference_list[0]

  if link_reference is not None and link_reference.find("report=") > -1:

    # url for report, check if report can be found.
    report_name = None
    link_split = link_reference.split("?")
    if len(link_split) > 1:
      link_relative_url = link_split[0]
      link_param_list = link_split[1].replace("&amp;", "&").split("&")
      link_param_dict = {}
      link_param_dict["document_language"] = doc_language
      link_param_dict["format"] = doc_format
      for param in link_param_list:
        param_key, param_value = param.split("=")
        if param_key == "report":
          report_name = param_value
        else:
          link_param_dict[param_key] = param_value

      # XXX report must be callable directly and generate the full output
      if report_name is not None:
        target_context = document.restrictedTraverse(link_relative_url, None)
        if target_context is not None:
          target_caller = getattr(target_context, report_name, None)
          if target_caller is not None:
            substitution_content = target_caller(**link_param_dict)
            # Note: switched to report returning a tuple with (content, header-title, header-subtitle)
            doc_content = doc_content.replace(link, substitution_content[0].encode("utf-8").strip())

return doc_content
