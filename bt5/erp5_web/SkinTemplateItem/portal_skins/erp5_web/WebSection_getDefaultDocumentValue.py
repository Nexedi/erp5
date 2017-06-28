"""
 This script is part of ERP5 Web

 ERP5 Web is a business template of ERP5 which provides a way
 to create web sites which can display selected
 ERP5 contents through multiple custom web layouts.

 This script returns the default document to display
 as the front page of a given Web Section or Web Site.
 If no default is found, it returns None.

 The default implementation should look at published
 documents which are associated to the section
 through the aggregate relation and try to display those
 which are available in the user language if any.

 Other implementations are possible: ex. display the last
 version in the closest language rather than
 the latest version in the user language.

 This script is intended to be overriden by creating a new script
 within a Web Section or a  Web Site instance. Customisation
 is also possible per portal type or per meta type through
 portal skins. It is recommended to use the first approach
 to host multiple sites on a single ERP5Site instance.
"""
# First get all the applicable references
# There might be more than one reference due to security differences
# (ex. a default restricted web page and a default public web page)
reference_list = context.getAggregateReferenceList()
if not reference_list: return None # Quick return

# We should only display those documents which are shared
# to some extend. This list takes into account some common
# state IDs used in ERP5.
return context.getDocumentValue(name=reference_list,
            validation_state=('released', 'released_alive', 'published', 'published_alive',
                              'shared', 'shared_alive', 'public', 'validated'))
