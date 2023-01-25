"""
This script is part of erp5_ingestion bt5.
It is used to define the preference order of data sources used when
ingesting a document.

Data source listed first is preferred over one listed later.

Possible data sources:

 * 'input' - data that is already set on the document (through web
interface for example), supplied in the email text or submitted
from the contribute form.

 * 'content' - metadata available in document content itself

 * 'filename' - filename of the ingested document

 * 'user_login' - user login of the logged in user

"""
order = ['input', 'content', 'filename', 'user_login']
return order
