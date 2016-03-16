ap = context.newActiveProcess()

context.activate(
  active_process=ap.getRelativeUrl(),
  tag=tag,
  ).Alarm_checkSkinCacheActive(fixit=fixit)
