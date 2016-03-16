preferences = box.KnowledgeBox_getDefaultPreferencesDict()
h = str(preferences.get('preferred_height'))
w = str(preferences.get('preferred_width'))
t = str(preferences.get('preferred_title'))

s = """<script type="text/javascript" src="http://www.gmodules.com/ig/ifr?url=http://hosting.gmodules.com/ig/gadgets/file/107548476258517015585/google.xml&amp;synd=open&amp;w=""" + w + """&amp;h=""" + h + """&amp;title=""" + t + """&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>"""

return s
