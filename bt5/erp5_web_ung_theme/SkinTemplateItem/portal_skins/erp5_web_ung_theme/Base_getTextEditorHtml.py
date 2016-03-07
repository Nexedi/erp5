"""
  This script is hack to get the html of FCKEditor. 
  The goals is open the html form to send e-mail without reload the page.
  XXX - This script will be remove as soon as possible to use a good way
"""
extra_content = extra_context = {"inputvalue": "", "inputname": "Compose Mail"}

return context.fckeditor_wysiwyg_support.pt_render(extra_context=extra_context)
