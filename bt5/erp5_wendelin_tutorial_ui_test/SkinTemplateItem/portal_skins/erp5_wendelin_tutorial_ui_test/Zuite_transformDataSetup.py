portal = context.getPortalObject()

dataAnalysisLine = context.portal_catalog.getResultValue(portal_type='Python Script',
                                                 title="DataAnalysisLine_convertEnvironmentDataStreamToArray")
if dataAnalysisLine is not None:
  portal.portal_callables.deleteContent(dataAnalysisLine.getId())
return "Init ok."
