"""
================================================================================
Return parameters to correctly display the RenderJS gadget
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# context_url:                   relative url of the context calling this script

return [('project_title', context.getTitle()), ('jio_key', context.getRelativeUrl())]
