from Products.ERP5Type.Cache import CachingMethod

if url == None:
  raise Exception("No url parameter provided.")

# XXX will only work for instances without authentication
context.REQUEST.response.setHeader("Access-Control-Allow-Origin", "*")

def retrieveOpenhubAnalysis(url):
  return context.Software_getOpenHubLatestAnalysis(url)

retrieveOpenhubAnalysis = CachingMethod(
  retrieveOpenhubAnalysis,
  id="retrieveOpenhubAnalysis", 
  cache_factory="erp5_content_long"
)

return retrieveOpenhubAnalysis(url)
