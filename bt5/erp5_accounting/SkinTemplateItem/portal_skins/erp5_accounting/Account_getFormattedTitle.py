if account is None:
  account = context

gap_id = account.Account_getGapId(gap_root=gap_root)
title  = account.getTranslatedTitle()

if gap_id:
  title = "%s - %s" % (gap_id, title)

return title
