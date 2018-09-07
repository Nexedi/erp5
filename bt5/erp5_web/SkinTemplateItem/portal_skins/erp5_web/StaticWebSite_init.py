"""
================================================================================
Set default parameters of static web site for redirection
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
context.edit(
  layout_configuration_form_id="StaticWebSite_viewRedirectAssistConfiguration",
  skin_selection_name="RedirectAssist",
  custom_render_method_id="StaticWebSite_getRedirectSourceUrl"
)
