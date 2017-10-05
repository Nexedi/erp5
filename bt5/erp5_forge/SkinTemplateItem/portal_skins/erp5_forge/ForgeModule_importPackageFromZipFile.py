import StringIO, zipfile

# This script was called by dialog erp5_forge/ForgeModule_importZipFileDialog/
# The script is for extract files in a zip file and import those files to erp5.

# For files not existed in erp5, create a new documentation.
# For files which already existed in erp5, update its content.
# For now, this script only hanlde seven types of file:
# gif, jpg, svg, png, html, css, js.

# This file mainly serve as an example.
# If you want to using this script or exteand its functionality.
# Please read the code first and make modification if needed.

document =None

if getattr(file, 'filename', '') != '':
  document_kw = {
    'batch_mode': True,
    'redirect_to_document': False,
    'file': file
  }
  
  document = context.Base_contribute(**document_kw)
  
  # depending on security model this should be changed accordingly
  document.publish()

data = document.getData()
zip_file_handle = StringIO.StringIO(data)
zip_file = zipfile.ZipFile(zip_file_handle, "r")
file_list = zip_file.namelist()

unhandled_files = []

def addWebPage(portal_type, file_id, file_reference, file_content, file_title):
  portal = self.getPortalObject()
  web_page = portal.web_page_module.newContent(
        portal_type=portal_type,
        id=file_id,
        reference=file_reference,
        text_content=file_content,
        title=file_title)
  return web_page

# Iterate through all files in this zip file.
for file_name in file_list:
  file_content = zip_file.read(file_name)
  file_id = file_name.replace('.', '_').replace('/', '_')
  file_title = file_name.split('/')[-1]
  file_type = file_title.split('.')[-1]

  # Only hanlde 7 file type for now.
  if file_type in ['gif', 'png', 'jpg', 'svg']:
    # original file name is the reference which used in ERP5
    image_list = portal.image_module.searchFolder(reference=file_name)
    if len(image_list) == 0:
      image = portal.image_module.newContent(
        portal_type='Image',
        id=file_id,
        reference=file_name,
        data=file_content,
        title=file_title
      )
      image.publish()
    elif len(image_list) == 1:
      image = image_list[0].getObject()
      image.edit(
        data=file_content,
        id=file_id
      )
    else:
      raise ValueError("More than one files has same reference")
    if image.getValidationState() == "draft":
      image.publishAlive()
  elif file_type in ['css', 'html', 'js']:
    web_page_list = portal.web_page_module.searchFolder(reference=file_name)
  
    if len(web_page_list) == 0:
      portal_type = {"js": "Web Script", "html": "Web Page", "css": "Web Style"}[file_type]
      web_page = addWebPage(
         portal_type,
         file_id,
         file_name,
         file_content,
         file_title
      )
    elif len(web_page_list) == 1:
      web_page = web_page_list[0].getObject()
      web_page.edit(text_content=file_content,
                    id=file_id)
    else:
      raise ValueError("More than one files has same reference")
    if web_page.getValidationState() == "draft":
      web_page.publish()
  else:
    unhandled_files.append(file_name)

# The return values are just for see the file list the unhandled files
return ["Import completed!", unhandled_files]
