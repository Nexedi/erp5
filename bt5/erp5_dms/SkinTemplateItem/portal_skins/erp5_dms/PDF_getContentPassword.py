# type: () -> bytes
"""Returns the password for this PDF file, if it is known by the system.

This is a customization entry point, used to display the PDF content to
logged in users, if they have the permission to view the PDF.

Note that this is not used for full-text extraction, password protected
PDFs are not indexed, in order not to leak the content.
"""
assert REQUEST is None and not container.REQUEST.args
return None
