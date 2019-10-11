"""
================================================================================
Return parameters to correctly display the RenderJS gadget
================================================================================
"""

return [('project_title', context.getTitle()), ('jio_key', context.getRelativeUrl()),  ('project_reference', context.getReference())]
