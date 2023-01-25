"""
  Generate a tree of
  depth, parent, **kw
"""

from Products.ERP5Type.Cache import CachingMethod
from erp5.component.module.Log import log
#log("depth: %s parent: %s kw: %s" % (depth, repr(parent), repr(kw)))
#log("selection: %s" % repr(context.portal_selections.getSelectionParamsFor('crawled_content_selection')))



def getAvailableSubjectList(subject_list=(), container_uid=None):
  """
    Returns the list of available subjects for all documents
    located in the current container (if defined) and which
    already match all subjects of subject_list

    NOTE: for now only 3 levels of subject are available
  """
  #log("In getAvailableSubjectList with container: %s subject_list: %s" % (container_uid, subject_list))
  kw = dict(subject="!=",
            select_list=["subject.subject"],
            group_by=["subject.subject"],
            #src__=1
            )
  if container_uid: kw['parent_uid'] = container_uid
  subject_len = len(subject_list)
  for i in range(0,3):
    if subject_len > i:
      kw['subject_filter_%s' % i] = subject_list[i]
  result_list = context.portal_catalog(**kw)
  #return result_list
  result = filter(lambda x: x not in subject_list,
                map(lambda r: r.subject, result_list))
  result.sort()
  return result

#return repr(getAvailableSubjectList(subject_list=["toto"], container=context))
#return getAvailableSubjectList(container=context)

request = context.REQUEST
domain_list = []

selection = context.portal_selections.getSelectionParamsFor('crawled_content_selection')
object_path = selection.get('object_path')
portal = context.getPortalObject()
external_source = portal.restrictedTraverse(object_path)
external_source_uid = external_source.getUid()

getAvailableSubjectList = CachingMethod(getAvailableSubjectList,
      id=('%s_%s' % (script.id, ''),
          ''),
      cache_factory='erp5_ui_short')

if depth == 0:
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid)
  subject_list = ()
elif depth == 1:
  subject_list = [parent.getCriterionList()[0].identity]
  #log("subject_list: %s " % subject_list)
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,
                                         subject_list=subject_list)
elif depth == 2:
  subject_list = [parent.getCriterionList()[0].identity]
  subject_list += [parent.getParentValue().getCriterionList()[0].identity]
  #log("subject_list: %s " % subject_list)
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,
                                         subject_list=subject_list)
elif depth == 3:
  subject_list = [parent.getCriterionList()[0].identity]
  subject_list += [parent.getParentValue().getCriterionList()[0].identity]
  subject_list += [parent.getParentValue().getParentValue().getCriterionList()[0].identity]
  #log("subject_list: %s " % subject_list)
  domain_subject_list = getAvailableSubjectList(container_uid=external_source_uid,
                                         subject_list=subject_list)
else:
  domain_subject_list = ()
  subject_list = ()

for subject in domain_subject_list:
  if subject:
    criterion_property_list = ['subject']
    for i in range(0,min(depth,3)):
      criterion_property_list.append('subject_filter_%s' % i)
    domain = parent.generateTempDomain(id='sub' + subject)
    domain.edit(title = subject,
                domain_generator_method_id=script.id,
                criterion_property_list=criterion_property_list)
    domain.setCriterion('subject', identity=subject)
    for i in range(0, min(depth,3)):
      domain.setCriterion('subject_filter_%s' % i, identity=subject_list[i])
    domain_list.append(domain)

return domain_list
