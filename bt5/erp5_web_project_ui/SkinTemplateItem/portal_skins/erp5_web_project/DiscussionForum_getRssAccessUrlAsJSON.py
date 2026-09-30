"""Return the personal RSS feed URL as JSON for the forum view gadget.

The token is minted here, on the reader's click, never on form render.
"""
import json
context.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
return json.dumps({'rss_url': context.DiscussionForum_getRssAccessUrl()})
