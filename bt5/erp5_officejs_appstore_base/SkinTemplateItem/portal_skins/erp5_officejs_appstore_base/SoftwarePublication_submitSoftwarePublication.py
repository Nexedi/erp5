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


software_release_url = software_release.getRelativeUrl()

tag = "preparing_sr_%s" % software_release_url
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
  document.activate(tag=tag).submit()

software_release.activate(after_tag=tag, tag=tag + "_2").SoftwareRelease_fixRelatedWebSection()

if portal.portal_workflow.isTransitionPossible(zip_file, 'submit'):
  zip_file.submit()
if portal.portal_workflow.isTransitionPossible(software_release, 'submit'):
  software_release.submit()
software_publication.activate(after_tag=tag + "_2").submit()
