from erp5.component.module.Log import log

after_script_id = context.getResourceValue().getConfigurationAfterScriptId()
after_script = getattr(context, after_script_id, None)
if after_script is not None:
  return after_script()

log("After script not found for %s." % context.getRelativeUrl())
