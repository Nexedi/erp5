portal = context.getPortalObject()

preferred_absence_calendar_period_type = portal.portal_preferences\
        .getPreferredAbsenceCalendarPeriodType()

method_id = portal.portal_preferences.getPreference(
     'preferred_category_child_item_list_method_id', 'getCategoryChildCompactLogicalPathItemList')

category = portal.portal_categories.calendar_period_type

if preferred_absence_calendar_period_type:
  category = category.restrictedTraverse(preferred_absence_calendar_period_type, category)

return getattr(category, method_id)(local_sort_id=('int_index', 'translated_title'),
                                    checked_permission='View',
                                    is_self_excluded=0,
                                    base=1)
