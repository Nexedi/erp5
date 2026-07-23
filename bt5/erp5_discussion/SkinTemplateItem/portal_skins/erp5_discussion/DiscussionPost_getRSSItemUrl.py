"""Per-item RSS <link> for this Discussion Post.

This delegates to a link builder (DiscussionPost_getAppItemRSSUrl)
installed by a higher-level bt (e.g. erp5_web_project_ui)
when present, and otherwise emits no per-item link.
"""
build_item_url = getattr(context, 'DiscussionPost_getAppItemRSSUrl', None)
if build_item_url is None:
  return ''
return build_item_url()
