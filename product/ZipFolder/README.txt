ZipFolder is a folder, 

plus:

- manage_upload(Form) to upload a zip file
  The zip file's content will be used to
  create Document/File/Folder/Image objects inside the
  folder

- manage_addZipFolder accepts an optional zip file,
  to upload a zip file directly

minus:

- doesn't create index_html or acl_users in constructor


Some problems still exist:

- zipfile.py doesn't handle all zipfile formats yet
- zipfile.py of Python 2.0 is broken
- zipfile.py for Python < 2.0 does not exist

If you are using Python 1.52, or experiencing problems 
unpacking zip files with Python 2.0, copy zipfile152.py 
in this package to zipfile.py.

This is a modified version of the Python zipfile.py (release 1.11
or later):

 - it requires zlib to run on python 1.52
 - it contains a fix for a file header problem (fixed in Python 2.1)
 - doesn't seem to work with zope-win32 (binary distribution)






