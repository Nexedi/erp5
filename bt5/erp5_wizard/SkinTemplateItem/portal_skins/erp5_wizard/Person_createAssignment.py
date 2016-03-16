group = kw.get('group')
function = kw.get('function')
activity = kw.get('activity')
title = kw.get('title')
description = kw.get('description')
start_date = kw.get('start_date')
stop_date = kw.get('stop_date')

if None not in [start_date, stop_date, group, function]:
  assignment = context.newContent(portal_type='Assignment', **kw)
  assignment.open()
  return assignment
