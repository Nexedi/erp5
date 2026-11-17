"""
  Sends a bug line with the forge fast input, then goes to the new line,
  which the bug messages only list once indexed.
"""
bug_line = context.Bug_doBugLineSendFastInputAction(title=title,
                                                    text_content=text_content,
                                                    batch_mode=1)
kw['keep_items'] = dict(
  portal_status_message=context.Base_translateString('Bug Line sent.'))
return bug_line.Base_redirect('view', **kw)
