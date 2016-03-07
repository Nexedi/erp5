preferences = box.KnowledgeBox_getDefaultPreferencesDict()
h = str(preferences.get('preferred_height'))
w = str(preferences.get('preferred_width'))
t = str(preferences.get('preferred_title'))

s = """<script type="text/javascript" src="http://gmodules.com/ig/ifr?url=http://www.google.com/ig/modules/calendar-for-your-site.xml&amp;up_showCalendar2=1&amp;up_showAgenda=1&amp;up_calendarFeeds=(%7B%7D)&amp;up_firstDay=Sunday&amp;up_syndicatable=true&amp;up_stylesheet=&amp;up_sub=1&amp;up_c0u=&amp;up_c0c=&amp;up_c1u=&amp;up_c1c=&amp;up_c2u=&amp;up_c2c=&amp;up_c3u=&amp;up_c3c=&amp;up_min=&amp;up_start=&amp;up_timeFormat=1%3A00pm&amp;up_calendarFeedsImported=0&amp;synd=open&amp;w=""" + w + """&amp;h=""" + h + """&amp;title="""+ t + """&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>"""

return s
