if alarm.getParentValue().isSubscribed() and not alarm.isActive() and alarm.isEnabled():
  alarm.activeSense()
