from base64 import b64encode
portal = context.getPortalObject()

#web_page = portal.web_page_module.newContent(
#  text_content = text_content,
#  temp_object=1,
#  title="Bericht")

web_page = context.web_page_module["6"]

text_content = context.DataNotebook_toHtml()
web_page.setTextContent(text_content)
  
html_data = web_page.WebPage_exportAsSingleFile(format="html", allow_script=True)

pdf_file = portal.Base_cloudoooConvertFile(html_data, "html", "pdf",
  conversion_kw=dict(
    encoding="utf8",
    margin_top=10,
    margin_bottom=10,
    margin_left=10,
    margin_right=10,
    header_spacing=0,
    header_html_data=b64encode(""),
    footer_html_data=b64encode(""),
    print_media_type=True,
    javascript_delay=9000,
    page_size="A4",
    zoom=1,
    dpi="75"
  )
)

REQUEST = context.REQUEST
if REQUEST is not None:
  REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf")
  REQUEST.response.setHeader('Content-Length', len(pdf_file))
  #REQUEST.response.setHeader('Content-Disposition',
  #                         'attachment;filename="%s.pdf"' % context.getTitle())
return pdf_file
