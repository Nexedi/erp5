from erp5.component.module.DateUtils import addToDate
from Products.ZSQLCatalog.SQLCatalog import Query

portal = context.getPortalObject()
portal_categories = portal.portal_categories

now = DateTime()
effective_date = context.getEffectiveDate()
previous_pay_day = addToDate(effective_date, month=-1)

# Get period dates
result = portal.portal_catalog(portal_type="DSN Monthly Report",
                               simulation_state="validated",
                               sort_on=[("creation_date", "descending")])

from_date = DateTime(effective_date.year(), effective_date.month(), 1)

# We report leave periods which are not over yet ...
result = portal.portal_catalog(portal_type='Leave Request Period', query=Query(expiration_date=None))
leave_period_list = [period.getObject() for period in result]

# ... And leave periods which ended during last period
result = portal.portal_catalog(portal_type='Leave Request Period', expiration_date=">=%s" % from_date.strftime("%Y/%m"))
# We need to filter results, because we can't search in a date interval with
# a smaller grain than a month.
leave_period_list.extend([period.getObject() for period in result if period.getExpirationDate() > from_date])

def formatDate(datetime):
  return "%02d%02d%04d" % (datetime.day(), datetime.month(), datetime.year())

def getLeaveBlocAsDict(leave_period, leave_category):
  bloc = {}
  bloc['S21.G00.60.001'] = leave_category.getCodification()
  bloc['S21.G00.60.002'] = formatDate(leave_period.getStartDate())
  bloc['S21.G00.60.003'] = formatDate(leave_period.getStopDate())
  bloc['S21.G00.60.004'] = '01' # we do subrogation
  first_subrogation_day = addToDate(leave_period.getStartDate(), day=3)
  bloc['S21.G00.60.005'] = formatDate(first_subrogation_day)
  # 3 months of subrogation, as defined in the collective agreement
  bloc['S21.G00.60.006'] = formatDate(addToDate(first_subrogation_day, month=3, days=-1))
  bloc['S21.G00.60.007'] = bank_account.getIban()
  bloc['S21.G00.60.008'] = bank_account.getBicCode()
  # employee restarted work during this period
  if getattr(leave_period, 'expiration_date', None):
    bloc['S21.G00.60.010'] = formatDate(leave_period.getExpirationDate())
    bloc['S21.G00.60.011'] = '01' # Restart normally
  return bloc

leave_period_type_set = set(portal_categories.use.social_declaration.l10n.fr.leave.getCategoryChildValueList())

# Create dict containing a DSN leave blocs, grouped by employee
leave_dict = {}
for period in sorted(leave_period_list, key=lambda lp: lp.getCreationDate()):
  # some leave periods don't have to be reported in DSN
  period_resource = period.getResourceValue()
  assert period_resource is not None, 'No type set on Leave Request %s' % period.absolute_url()
  leave_category = set(period.getResourceValue().getUseValueList()).intersection(leave_period_type_set)
  if not leave_category:
    continue
  # Let's make a DSN Bloc for this leave period
  leave_category = leave_category.pop()
  if period.getDestinationValue() in leave_dict.keys():  # TODO: bug here, we check with getDestinationValue and set with getDestination 
    leave_dict[period.getDestination()].append(getLeaveBlocAsDict(period, leave_category))
  else:
    leave_dict[period.getDestination()] = [getLeaveBlocAsDict(period, leave_category),]

return leave_dict
