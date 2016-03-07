preferences = box.KnowledgeBox_getDefaultPreferencesDict()
h = str(preferences.get('preferred_height'))
w = str(preferences.get('preferred_width'))
t = str(preferences.get('preferred_title'))

s = """<script type="text/javascript" src="http://gmodules.com/ig/ifr?url=http://www.google.com/ig/modules/datetime.xml&amp;up_color=blue&amp;up_firstDay=1&amp;synd=open&amp;w=""" + w + """&amp;h=""" + h + """&amp;title=""" + t + """&amp;lang=fr&amp;country=ALL&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>"""

return s
