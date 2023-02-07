document = state_change['object']


if not document.getValidationState() in ('published', 'published_alive'):
  return

document.WebPage_reindexRelatedWebCampaign()
