"""Return the personal URL of the aggregated forum feed as JSON for the link gadget."""
import json
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
return json.dumps({"rss_url": context.Base_getRssAccessUrl(
  "WebSection_viewLatestForumPostListAsRSS")})
