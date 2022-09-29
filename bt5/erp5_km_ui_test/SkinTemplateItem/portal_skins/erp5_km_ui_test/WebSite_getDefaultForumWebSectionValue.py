"""
  Every site should have one forum as theme uses it to get latest discussion posts.
  Forum relative url is taken from web site configuration itself.

  This is all arbitrary...
"""

website = context.getWebSiteValue()
default_forum_url = website.getProperty('default_forum_relative_url', 'discussions')
return website.restrictedTraverse(default_forum_url, None)
