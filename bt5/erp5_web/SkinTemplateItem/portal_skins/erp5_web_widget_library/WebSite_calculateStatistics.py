"""
  A simple script to calculate some statistics
  about documents and persons in the system.

"""
from Products.ERP5Type.Cache import CachingMethod

def sortDictByValues(adict):
  """
    Sort a dictionary by maximal values.
    Return sorted list of tuples [(key, value),...]
  """
  items = adict.items()
  items.sort(key=lambda x: x[1], reverse=True)
  return items

def calculateStatistics():
  portal = context.getPortalObject()
  portal_catalog = portal.portal_catalog
  portal_types = context.portal_types

  # document statistics
  documents_groups = {}
  documents_owners = {}
  documents_classifications = {}
  document_content_types = portal_types['Document Module'].getTypeAllowedContentTypeList()
  all_documents = portal_catalog.searchResults(portal_type = document_content_types)
  total_documents = portal_catalog.countResults(portal_type = document_content_types)[0][0]
  total_documents_released = portal_catalog.countResults(portal_type = document_content_types,
                                                         validation_state = 'released')[0][0]
  total_documents_shared = portal_catalog.countResults(portal_type = document_content_types,
                                                       validation_state = 'shared')[0][0]
  total_documents_draft = portal_catalog.countResults(portal_type = document_content_types,
                                                      validation_state = 'draft')[0][0]
  total_documents_published = portal_catalog.countResults(portal_type = document_content_types,
                                                        validation_state = 'published')[0][0]
  # get what's still not in catalog as info
  for doc in all_documents:
    obj = doc.getObject()
    # count classification
    classification = obj.getClassification()
    if classification is not None:
      documents_classifications[classification] = documents_classifications.get(classification, 0) + 1
    # count devision
    group = obj.getGroup()
    if group is not None:
      documents_groups[group] = documents_groups.get(group, 0) + 1
    # XXX: count owner
    doc_owner = doc.Base_getOwnerId()
    if doc_owner is not None and doc_owner.find('@')!=-1:
      # we have a website user. we wanted to filter Zope users
      documents_owners[doc_owner] = documents_owners.get(doc_owner, 0) + 1
  # sort the most "productive" devision group by number of documents contributed
  documents_groups_sorted = sortDictByValues(documents_groups)
  # sort sort the most "productive" person by number of documents contributed
  documents_owners_sorted = sortDictByValues(documents_owners)
  documents_stats = dict(total_documents = total_documents,
                         total_documents_released = total_documents_released,
                         total_documents_shared = total_documents_shared,
                         total_documents_draft = total_documents_draft,
                         total_documents_published = total_documents_published,
                         documents_groups_sorted = documents_groups_sorted,
                         documents_owners_sorted = documents_owners_sorted,
                         classifications = documents_classifications)
  # person statistics
  total_persons = portal_catalog.countResults(portal_type = 'Person')[0][0]
  total_persons_draft = portal_catalog.countResults(portal_type = 'Person',
                                                    validation_state = 'draft')[0][0]
  total_persons_validated = portal_catalog.countResults(portal_type = 'Person',
                                                      validation_state = 'validated')[0][0]
  persons_stats = dict(total_persons = total_persons,
                       total_persons_draft = total_persons_draft,
                       total_persons_validated = total_persons_validated)
  # final statistics
  statistics = dict(documents = documents_stats,
                    persons = persons_stats)
  return statistics

# cache statistics for a short period
cached_method = CachingMethod(calculateStatistics,
                              script.id,
                              'erp5_content_short')
stats = cached_method() #calculateStatistics()

return stats
