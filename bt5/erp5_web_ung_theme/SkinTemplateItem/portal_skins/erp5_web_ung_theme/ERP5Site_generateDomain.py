"""
  This script generates a sections list to filter the document on UNG Docs.
"""

from Products.ERP5Type.Cache import CachingMethod

def getAvailableSubjectList(subject_list=()):
  """
    Returns the list of available subjects for all documents
    located in the current container (if defined) and which
    already match all subjects of subject_list
  """
  subject_list = ()
  portal_type_list = ["Web Table", "Web Page", "Web Illustration"]
  kw = dict(portal_type=portal_type_list,
            subject="!=",)
  subject_len = len(subject_list)
  result_list = context.portal_catalog(**kw)

  subject_list = []
  for keyword_list in  filter(lambda x: x not in subject_list, 
                       map(lambda r: r.subject, result_list)):
     for keyword in keyword_list:
       if keyword not in subject_list:
         subject_list.append(keyword)

  return subject_list

def appendTempDomain(id, 
                     title,
                     property_dict,
                     parent=parent,
                     membership_criterion_base_category=(),
                     membership_criterion_category=()):
  domain = parent.generateTempDomain(id=id)
  domain.edit(title=title,
              domain_generator_method_id=script.id,
              membership_criterion_base_category=membership_criterion_base_category,
              membership_criterion_category=membership_criterion_category) 

  domain.setCriterionPropertyList(property_dict.keys())
  for key, value in property_dict.items():
    domain.setCriterion(key, value)

  domain_list.append(domain)

domain_list = []

if depth > 1:
  return domain_list

getAvailableSubjectListCached = CachingMethod(getAvailableSubjectList, 
                                              id='%s_%s' % (script.id, 'subject_list_cached'),
                                              cache_factory='erp5_ui_short')

subject_list = getAvailableSubjectListCached()

for subject in subject_list:
  appendTempDomain("subject_" + subject,
                   subject.capitalize(),
                   dict(subject=subject),
                   parent,
                   ("by_subject",),
                   ("by_subject",))


return domain_list
