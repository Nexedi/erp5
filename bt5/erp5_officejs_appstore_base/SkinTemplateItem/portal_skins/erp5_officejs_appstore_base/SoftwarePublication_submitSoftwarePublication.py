software_publication = context

if software_publication.getSimulationState() != "draft":
  return

software_publication_line = software_publication.objectValues(
  portal_type="Software Publication Line",
)[0]

software_product = software_publication_line.getResourceValue(portal_type="Software Product")

if not software_product:
  return

portal = context.getPortalObject()
application_publication_section = portal.portal_categories.publication_section.application

zip_file = portal.portal_catalog.getResultValue(
  portal_type="File",
  strict_publication_section_uid=application_publication_section.package.getUid(),
  strict_follow_up_uid=software_publication.getUid(),
)

if not zip_file:
  # XXX Do something?
  return

software_release = software_publication_line.getAggregateValue(portal_type="Software Release")

from cStringIO import StringIO
import zipfile

zipbuffer = StringIO()
zipbuffer.write(str(zip_file.getData()))
zip_reader = zipfile.ZipFile(zipbuffer)
user_login = software_publication.getSourceReference()

version = software_release.getReference()

# look for Base Directory
base = ""
for name in zip_reader.namelist():
  if "/" in name:
    temp_base = name.split("/")[0]
    if base and base != temp_base:
      base = ""
      break
    else:
      base = temp_base
  else:
    base = ""
    break
if base:
  base += "/"
base_length = len(base)

def extractWebManifest(html_file):
  html = context.Base_parseHtml(html_file)
  for tag in html:
    if tag[0] == 'starttag' and tag[1] == 'link' and ('rel', 'manifest') in tag[2]:
      for attribute in tag[2]:
        if attribute[0] == 'href':
          return attribute[1]

software_release_url = software_release.getRelativeUrl()

tag = "preparing_sr_%s" % software_release_url
default_page = ""
for name in zip_reader.namelist():
  if zip_reader.getinfo(name).file_size == 0:
    continue
  temp_file = StringIO(zip_reader.read(name))
  url = name[base_length:]

  if url in ("index.html", "index.htm"):
    publication_section = application_publication_section.landing_page.getRelativeUrl()
  else:
    publication_section = application_publication_section.getRelativeUrl()

  document = portal.portal_contributions.newContent(
    file=temp_file,
    filename=url,
    redirect_to_document=False,
    user_login=user_login,
    reference=version + "/" + url,
    title=url,
    version=version,
    publication_section_value=publication_section,
    follow_up=software_release_url,
    portal_type="File",
  )
  # XX Hackish
  document.setCategoryList(
    document.getCategoryList() + ["contributor/" + software_publication.getSource()])
  if url in ("index.html", "index.htm"):
    default_page = document.getRelativeUrl()
    web_manifest_url = extractWebManifest(document.getData())
  document.activate(tag=tag).publish()

software_release.SoftwareRelease_fixRelatedWebSection(default_page=default_page, web_manifest = web_manifest_url)

if portal.portal_workflow.isTransitionPossible(zip_file, 'publish'):
  zip_file.publish()
if portal.portal_workflow.isTransitionPossible(software_release, 'submit'):
  software_release.submit()
software_publication.activate(after_tag=tag).submit()
