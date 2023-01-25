from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
from Products.CMFActivity.ActiveResult import ActiveResult
portal = context.getPortalObject()

# fixit could remove the grouping reference when lines are grouped together but do not match
assert not fixit, NotImplemented

# a mapping of currency precision for each section
precision_by_section_uid = {}

# Check grouping reference for both source and destination.
def check(node_uid, section_uid, mirror_section_uid):
  precision = precision_by_section_uid[section_uid]
  if mirror_section_uid is None:
    mirror_section_uid = SimpleQuery(mirror_section_uid=None)
  line_list = portal.portal_simulation.getMovementHistoryList(
                  portal_type=portal.getPortalAccountingMovementTypeList(),
                  grouping_reference=context.getGroupingReference(),
                  node_uid=node_uid,
                  section_uid=section_uid,
                  mirror_section_uid=mirror_section_uid)
  if not line_list:
    return
  total = round(sum([(l.total_price or 0) for l in line_list]), precision)
  if total != 0:
    # XXX if n transactions that do not match are grouped together, the same
    # problem will be reported n times.
    portal.restrictedTraverse(active_process).postResult(
     ActiveResult(summary=script.getId(),
         detail='%s has wrong grouping (%s)' % (context.getRelativeUrl(), total),
         result='',
         severity=100))

  # XXX we could check this as well
  """
  max_date = max([l.date for l in line_list])
  for line in line_list:
    assert line.getGroupingDate() in (max_date, None)
  """

node_uid = context.getSourceUid(portal_type='Account')
section_uid = None
section = context.getSourceSectionValue(portal_type='Organisation')
if section is not None:
  section = section.Organisation_getMappingRelatedOrganisation()
  section_uid = section.getUid()
  precision_by_section_uid[section_uid] = context.getQuantityPrecisionFromResource(
    section.getPriceCurrency())

mirror_section_uid = context.getDestinationSectionUid()

if node_uid and section_uid:
  check(node_uid=node_uid, section_uid=section_uid, mirror_section_uid=mirror_section_uid)

node_uid = context.getDestinationUid()
section_uid = None
section = context.getDestinationSectionValue(portal_type='Organisation')
if section is not None:
  section = section.Organisation_getMappingRelatedOrganisation()
  section_uid = section.getUid()
  precision_by_section_uid[section_uid] = context.getQuantityPrecisionFromResource(
    section.getPriceCurrency())
mirror_section_uid = context.getSourceSectionUid()

if node_uid and section_uid:
  check(node_uid=node_uid, section_uid=section_uid, mirror_section_uid=mirror_section_uid)
