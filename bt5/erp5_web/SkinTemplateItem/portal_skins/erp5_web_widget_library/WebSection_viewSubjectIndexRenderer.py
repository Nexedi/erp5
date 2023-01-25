"""
  XXX This script does not work after the change of subject table in r40057.

  This Widget lists all documents of the current section
  by subject. For each subject, it creates a title (<h1>)
  then lists all documents which meet the section predicate
  and provides a permanent URL to them.

  Result is cached for high performance.
"""

web_section_value = context.getWebSectionValue()
web_section_url = web_section_value.absolute_url()
context = web_section_value

def buildIndex(language=None):
  from Products.ZSQLCatalog.SQLCatalog import NegatedQuery, Query
  # Retrieve the different subjects in the catalog
  subject_list = context.searchResults(
      select_list=['subject', 'reference'],
      query=NegatedQuery(Query(subject=None)),
      language=language or '',
      sort_on=(('subject', 'ascending'), ('title', 'ascending')),
      #src__=1,
   )
  #return subject_list
  #return map(lambda x:(x.subject, x.reference), subject_list)
  # Convert the result into list
  # This is not the fastest approach but should be OK for
  # moderate size
  subject_list = list(subject_list)
  subject_count = len(subject_list) # Not the fastest (use countResults instead)

  # Return immediately if empty
  if not subject_count:
    return '<p></p>'

  # Now build the page
  result = []
  last_subject = None
  for subject in subject_list:
    if last_subject != subject.subject:
      subject_title = subject.subject
      subject_title = subject_title[0].upper() + subject_title[1:]
      result.append("<h1>%s</h1>" % subject_title)
    result.append("""<p><a href="%s/%s/view">%s</a></p>""" % (web_section_url, subject.reference, subject.title))
    last_subject = subject.subject
  return '\n'.join(result)

from Products.ERP5Type.Cache import CachingMethod
buildIndex = CachingMethod(buildIndex,
                   id=('WebSection_viewSubjectIndexRenderer', web_section_url))
language = context.Localizer.get_selected_language()
return buildIndex(language=language)
