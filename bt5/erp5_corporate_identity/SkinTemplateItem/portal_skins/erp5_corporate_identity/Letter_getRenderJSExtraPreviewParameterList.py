"""
================================================================================
Return parameters to correctly display the RenderJS gadget
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# context_url:                   relative url of the context calling this script

return [('editor', 'pdf'), ('portal_type', context.Letter_getPredecessor(context_url=context_url).getPortalType()), ('maximize', True)]
