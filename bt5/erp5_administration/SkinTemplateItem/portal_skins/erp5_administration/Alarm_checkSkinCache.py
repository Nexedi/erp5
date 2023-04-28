ap = context.newActiveProcess()

context.activate(
  activity='SQLDict',
  active_process=ap.getRelativeUrl(),
  tag=tag
  ).Alarm_checkSkinCacheActive(fixit=fixit)
