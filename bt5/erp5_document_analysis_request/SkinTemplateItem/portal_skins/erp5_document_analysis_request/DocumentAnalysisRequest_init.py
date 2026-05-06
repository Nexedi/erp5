import time, random

# Set document analysis request reference value
reference = time.strftime("%Y/%m/%d-%H%M-", time.gmtime()) + str(random.randint(10000, 99999))
context.setReference(reference)
follow_up_path = context.getPath()[6:]

# Set activity tag then launch Document analysis.
portal = context.getPortalObject()
tag = "document_analysis_request_" + reference
context.defaultActivateParameterDict({'tag': tag}, placeless=True)
portal.portal_activities.activate(after_tag=tag).DocumentAnalysis_createAnalysis(follow_up_path)

container.document_conversion_module.newContent(
  follow_up = follow_up_path
)
