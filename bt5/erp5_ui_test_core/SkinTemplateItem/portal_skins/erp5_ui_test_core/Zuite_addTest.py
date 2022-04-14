"""
  Include a page template contains a into a Zuite
"""
if REQUEST:
  raise RuntimeError("You can not call this script from the URL")

assert context.getPortalType() == "Test Tool", "bad context"

if test_id is None or test_id == '':
  test_id = ''.join(
    list(
      filter( # pylint:disable=deprecated-lambda
        lambda a: a not in [
          "'", '_', '-', '.', ' ', '~', ':', '/', '?', '#', '[', ']', '@', '!',
          '$', '&', '(', ')', '*', '+', ';', '='
        ], title)))

if test_id not in context.objectIds():
  factory = context.manage_addProduct['PageTemplates']
  factory.manage_addPageTemplate(test_id, title=title, text=text, REQUEST=None)
  test = getattr(context, test_id, None)
else:
  test = getattr(context, test_id, None)
  context.Zuite_editZPT(test, text)
  test.setTitle(text)

return test
