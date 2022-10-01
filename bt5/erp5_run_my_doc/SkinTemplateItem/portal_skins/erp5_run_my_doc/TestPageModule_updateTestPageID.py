"""
This script is intended to be run before exporting business template of test pages
It will change ID of all published/shared/released test page so that it can be exported easily
"""
portal = context.getPortalObject()

test_pages = portal.test_page_module.searchFolder(validation_state=
  ('published', 'published_alive','released', 'released_alive',
   'shared', 'shared_alive',))
print(len(test_pages))
new_page_list = []
for page in test_pages:
  print("changing ID of %s to %s of document in state %s" %(page.getRelativeUrl(), page.getReference(), page.getValidationState()))
  if not dry_run:
    page.setId(page.getReference())
    print("\tpage changed")
  new_page_list.append(page.getReference())

print("finished")

print("For business template Path")
for p in new_page_list:
  print("test_page_module/"+p)
  print("test_page_module/"+p+"/**")


return printed
