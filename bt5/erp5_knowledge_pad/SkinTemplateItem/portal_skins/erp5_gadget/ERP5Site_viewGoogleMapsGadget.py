preferences = box.KnowledgeBox_getDefaultPreferencesDict()
h = str(preferences.get('preferred_height'))
w = str(preferences.get('preferred_width'))
t = str(preferences.get('preferred_title'))
location = str(preferences.get('preferred_location'))
language = str(preferences.get('preferred_language'))
large_map = '1'
kml = '0'


s = """<script type="text/javascript" src="http://gmodules.com/ig/ifr?url=http://www.google.com/ig/modules/mapsearch.xml&amp;up_location=""" + location + """&amp;up_largeMapMode=""" + large_map + """&amp;up_kml=""" + kml + """&amp;up_traffic=&amp;up_locationCacheString=&amp;up_locationCacheLat=&amp;up_locationCacheLng=&amp;up_mapType=m&amp;up_idleZoom=11&amp;up_transitionQuery=&amp;up_rawquery=&amp;up_selectedtext=&amp;synd=open&amp;w=""" + w + """&amp;h=""" + h + """&amp;title=""" + t + """&amp;lang=""" + language +"""&amp;country=ALL&amp;border=%23ffffff%7C3px%2C1px+solid+%23999999&amp;output=js"></script>"""

return s
