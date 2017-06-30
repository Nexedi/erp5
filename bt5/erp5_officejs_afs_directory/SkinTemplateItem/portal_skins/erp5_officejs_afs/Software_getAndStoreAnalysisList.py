from Products.ERP5Type.Cache import CachingMethod

def retrieveOpenhubAnalysis(url):
  return context.Software_getOpenHubLatestAnalysis(url)

retrieveOpenhubAnalysis = CachingMethod(
  retrieveOpenhubAnalysis,
  id="retrieveOpenhubAnalysis", 
  cache_factory="erp5_content_long"
)

def retrieveAndStoreOpenHubAnalysisXml():
  profile_url_list = context.Software_getAndStoreOpenHubLatestAnalysisList()
  for profile_url in profile_url_list:
    xml_content = retrieveOpenhubAnalysis(profile_url)
    #context.document.newContent(
    #  portal_type='Embedded File',
    #  id=profile_url + '.xml',
    #  file=xml_content,
    #  filename=profile_url + '.xml'
    #  language='en'
    #)
    #context.document.publishAlive()

retrieveAndStoreOpenHubAnalysisXml = CachingMethod(
  retrieveAndStoreOpenHubAnalysisXml,
  id="retrieveAndStoreOpenHubAnalysisXml",
  cache_factory="erp5_content_long"
)

return retrieveAndStoreOpenHubAnalysisXml()
