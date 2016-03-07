"""
  Is a web section rendered. (it's not a list_mode or dialog_mode')
"""
return context.REQUEST.get('current_web_section') is not None
