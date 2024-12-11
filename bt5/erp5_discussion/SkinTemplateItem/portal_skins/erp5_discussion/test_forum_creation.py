portal = context.getPortalObject()
test_id = "roque_test"

# utils functions -----------------------------------------------------------
def _mixDict(*dict_list):
  result = {}
  for obj in dict_list:
    result.update(obj)
  return result
def _createObject(from_, mixKW, searchKW={}, newContentKW={}):
  result = from_.searchFolder(**_mixDict(mixKW, searchKW))
  len_result = len(result)
  if len_result == 0:
    return from_.newContent(**_mixDict(mixKW, newContentKW))
  if len_result == 1:
    return result[0]
  raise ValueError("Cannot choose object, check instance state")
# // utils functions ---------------------------------------------------------

# setup site -----------------------------------------------------------------
# - web_site_module/site_$id
test_web_site = _createObject(
  portal.web_site_module,
  dict(
    portal_type = "Web Site",
    id = test_id + "_web_site"
  )
)
# - web_site_module/site_$id/public_websection
test_public_web_section = _createObject(
  test_web_site,
  dict(
    portal_type = "Web Section",
    id = "public_section"
  )
)
# - portal_categories/publication_section/blog
publication_section_blog = _createObject(
  portal.portal_categories.publication_section, dict(
    portal_type = "Category",
    id = "blog"
  ), newContentKW = dict(title = "Blog")
)
publication_section_blog_path = "publication_section/blog"
# - portal_categories/publication_section/forum
publication_section_forum = _createObject(
  portal.portal_categories.publication_section,
  dict(
    portal_type = "Category",
    id = "forum"
  ),
  newContentKW = dict(title = "Forum")
)
publication_section_forum_path = "publication_section/forum"
# // setup site ---------------------------------------------------------------

# create public blog and forum
try:
  test_public_web_section.WebSection_createBlogAndForum(
    create_blog=True,
    create_forum=True,
    blog_id="blog_%s" % test_id,
    forum_id="forum_%s" % test_id,
  )
except:
  pass
# check what was created
blog = test_public_web_section.searchFolder(
  portal_type="Web Section",
  id="blog_%s" % test_id
)[0].getObject()
forum = test_public_web_section.searchFolder(
  portal_type="Web Section",
  id="forum_%s" % test_id
)[0].getObject()

print("blog.getMembershipCriterionCategoryList (should be %s):" % publication_section_blog_path)
print(blog.getMembershipCriterionCategoryList())
print('blog criterion list (should be ("portal_type", "Web Page")):')
print([(x.property, x.identity) for x in blog.getCriterionList()])
print("forum.getMembershipCriterionCategoryList (should be %s):" % publication_section_forum_path)
print(forum.getMembershipCriterionCategoryList())
print('forum criterion list (should be ("portal_type", "Discussion Thread")):')
print([(x.property, x.identity) for x in forum.getCriterionList()])

print(blog.getRelativeUrl())
print(forum.getRelativeUrl())
return printed
