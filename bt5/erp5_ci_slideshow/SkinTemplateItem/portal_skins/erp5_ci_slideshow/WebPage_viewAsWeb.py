"""
================================================================================
Presentation Layout ?portal_skin=CI_slideshow
================================================================================
"""
import re

def getSlideList(content):
  return re.findall(r'<section[^>]*?>(.*?)</section>', content, re.S)

def getDetails(content):
  return content.find("</details>") > -1

def getNestedSection(content):
  return content.find("<section") > -1

def removeSlidesWithoutDetailsFromNotes(content):
  slide_list = getSlideList(content)
  
  # empty slide if no <detail>
  for slide in slide_list:
    if getNestedSection(slide) is False:
      content = content.replace(slide, '')
  
  # remove empty slides
  content = content.replace('<section></section>','')
  content = re.sub(r'<section class="[^"]*"></section>', '', content)
  
  # remove empty slides with class
  return content

def removeEmptyDetails(content):
  return content.replace('<details open="open"></details>', '')

def getThemeFromFirstFollowUpProduct():
  follow_up_list = context.getFollowUpValueList(
    portal_type="Product",
    checked_permission='View'
  )

  if len(follow_up_list) > 0:
    full_title = follow_up_list[0].getTitle()
    return full_title.split(" Software")[0].lower()
  return "nexedi"

document = context

# wkhtmltopdf
document_output_type = document.REQUEST.form.get("output", default=None)

document_content = removeEmptyDetails(document.getTextContent())
document_theme = getThemeFromFirstFollowUpProduct()
document_title = document.getTitle()
document_description = document.getDescription()
document_creation_year = document.getCreationDate().strftime('%Y')
document_theme_logo_url = "NXD-Media.Logo." + document_theme.capitalize()
document_theme_logo = context.restrictedTraverse(document_theme_logo_url)
document_claim = document_theme_logo.getDescription()

# XXX requires proxy_role
#document_contributor_list = ', '.join(document.getContributorTitleList())
document_contributor_list = ""

# backwards compatability with old slideshow 
# requires to wrap content of slides that contain <details> into nested 
# <section> tags. this is done here
has_details = getDetails(document_content)
if has_details is True:
  slide_list = getSlideList(document_content)

  for slide in slide_list:
    if getDetails(slide) is True:
      cleaned = slide.split('<details')[0]
      wrapped = ''.join(["<section>", cleaned, "</section>"])
      updated = slide.replace(cleaned, wrapped)
      document_content = document_content.replace(slide, updated)

# wkhtmltopdf
if document_output_type == "footer":
  return """
  <!Doctype html>
  <html class="ci-%s">
    <head>
      <meta charset="utf-8">
      <title>%s</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">

      <!-- fonts -->
      <link rel="stylesheet" href="roboto/roboto.css" />
      <link rel="stylesheet" href="roboto/roboto-condensed.css" />

      <link rel="stylesheet" href="css/theme/white_custom.css?portal_skin=CI_slideshow" id="theme" />
      <link rel="stylesheet" href="css/custom.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="lib/css/zenburn.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="css/custom_pdf.css?portal_skin=CI_slideshow" />

      <script type="text/javascript">
          function setPlaceholdersWithUrlParameters() {
            var vars={};
            var x=window.location.search.substring(1).split('&');
            for (var i in x) {var z=x[i].split('=',2);vars[z[0]] = unescape(z[1]);}
            var x=['frompage','topage','page','webpage','section','subsection','subsubsection'];
            for (var i in x) {
              var y = document.getElementsByClassName(x[i]);
              for (var j=0; j<y.length; ++j) y[j].textContent = vars[x[i]];
            }
          }
      </script>
    </head>
    	<body class="ci-presentation" onload="setPlaceholdersWithUrlParameters()">
        <div class="ci-presentation-footer">
  		    <div class="ci-presentation-container-left">
  		      <img src="NXD-Media.Logo.Nexedi?format=png" alt="Nexedi Logo" />
  		    </div>
  		    <div class="ci-presentation-container-center">%s</div>
  		    <div class="ci-presentation-container-right">
  		      %s &copy; Nexedi SA<br/>
  		      %s<span class="page"></span> | <span class="topage"></span>
  		    </div>
  		  </div>
      </body>
	 </html>
  """ % (
    document_theme,
    document_title,
    document_description,
    document_creation_year,
    document_contributor_list
  )

if document_output_type == "cover":
  return """
  <!Doctype html>
  <html class="ci-pdf ci-%s">
    <head>
      <meta charset="utf-8">
      <title>%s</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">

      <!-- fonts -->
      <link rel="stylesheet" href="roboto/roboto.css" />
      <link rel="stylesheet" href="roboto/roboto-condensed.css" />

      <link rel="stylesheet" href="css/theme/white_custom.css?portal_skin=CI_slideshow" id="theme" />
      <link rel="stylesheet" href="css/custom.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="lib/css/zenburn.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="css/custom_pdf.css?portal_skin=CI_slideshow" />
      
      <!-- logo-box and slogan -->
      <style type="text/css">
        html .ci-presentation-intro.present:before {
          content: "%s";
          background: #FFF url("%s?format=png") center no-repeat;
          background-size: 300px;
        }
      </style>
    </head>
    <body class="ci-presentation">
      <div class="reveal">
        <div class="slides">
          <section class="ci-presentation-intro present">
    		    <h2>%s</h2>
    		  </section>
  		  </div>
		  </div>
    </body>
  </html>
  """ % (
    document_theme,
    document_title,
    document_claim,
    document_theme_logo_url,
    document_title
  )

# outputting just the content requires to drop wrapping <divs> (reveal/slides)
# and add extra css to recreate the same layout. so a separate output=content
# instead of defaulting to None
if document_output_type == "content":
  return """
  <!Doctype html>
  <html class="ci-%s">
    <head>
  		<meta charset="utf-8">
      <title>%s</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">

      <!-- fonts -->
      <link rel="stylesheet" href="roboto/roboto.css" />
      <link rel="stylesheet" href="roboto/roboto-condensed.css" />

      <link rel="stylesheet" href="css/theme/white_custom.css?portal_skin=CI_slideshow" id="theme" />
      <link rel="stylesheet" href="css/custom.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="lib/css/zenburn.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="css/custom_pdf.css?portal_skin=CI_slideshow" />
      
  	</head>
  
  	<body class="ci-presentation">
  		<!-- <div class="reveal">
  			<div class="slides"> -->
  			  %s
  			<!-- </div>
  		</div> -->
  	</body>
  </html>
  """ % (
    document_theme,
    document_title,
    document_content
  )

# handouts
if document_output_type == "details":
  return """
  <!Doctype html>
  <html class="ci-%s">
    <head>
  		<meta charset="utf-8">
      <title>%s</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">

      <!-- fonts -->
      <link rel="stylesheet" href="roboto/roboto.css" />
      <link rel="stylesheet" href="roboto/roboto-condensed.css" />

      <link rel="stylesheet" href="css/theme/white_custom.css?portal_skin=CI_slideshow" id="theme" />
      <link rel="stylesheet" href="css/custom.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="lib/css/zenburn.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="css/custom_pdf.css?portal_skin=CI_slideshow" />
      <link rel="stylesheet" href="css/custom_wkhtmltopdf.css?portal_skin=CI_slideshow" />

  	</head>

  	<body class="ci-presentation ci-handout">
  		<!-- <div class="reveal">
  			<div class="slides"> -->
  			<section>
          <h1>Notes</h1>
        </section>
  			  %s
  			<!-- </div>
  		</div> -->
  	</body>
  </html>
  """ % (
    document_theme,
    document_title,
    #document_content
    removeSlidesWithoutDetailsFromNotes(document_content)
  )


# DEFAULT WebPage_viewAsWeb

return """
<!Doctype html>
<html class="ci-%s">
  <head>
		<meta charset="utf-8">
    <title>%s</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, minimal-ui">

    <!-- fonts -->
    <link rel="stylesheet" href="roboto/roboto.css" />
    <link rel="stylesheet" href="roboto/roboto-condensed.css" />

    <link rel="stylesheet" href="css/reveal_custom.css?portal_skin=CI_slideshow" />
    <link rel="stylesheet" href="css/theme/white_custom.css?portal_skin=CI_slideshow" id="theme" />
    <link rel="stylesheet" href="css/custom.css?portal_skin=CI_slideshow" />
    <link rel="stylesheet" href="lib/css/zenburn.css?portal_skin=CI_slideshow" />

    <!-- logo-box and slogan -->
    <style type="text/css">
      html .ci-presentation .slides .ci-presentation-intro.present:before {
        content: "%s";
        background: #FFF url("%s?format=png") center no-repeat;
        background-size: 300px;
      }
    </style>

		<!-- print/pdf 
		<script>
			var link = document.createElement( 'link' );
			link.rel = 'stylesheet';
			link.type = 'text/css';
			link.href = window.location.search.match( /print-pdf/gi ) ? 'css/orint.css?portal_skin=CI_slideshow' : 'css/paper.css?portal_skin=CI_slideshow';
			document.getElementsByTagName( 'head' )[0].appendChild( link );
		</script>
		-->
	</head>

	<body class="ci-presentation">

    <!-- Presentation -->
		<div class="reveal">

			<!-- section elements inside this container are displayed as slides -->
			<div class="slides">
			  
			  <!-- intro slide -->
			  <section class="ci-presentation-intro">
			    <h2>%s</h2>
			  </section>

			  <div class="ci-presentation-header">
			    <h2>%s</h2>
			  </div>
			  %s
			  <div class="ci-presentation-footer">
			    <div class="ci-presentation-container-left">
			      <img src="NXD-Media.Logo.Nexedi?format=png" alt="Nexedi Logo" />
			    </div>
			    <div class="ci-presentation-container-center">%s</div>
			    <div class="ci-presentation-container-right">
			      %s &copy; Nexedi SA<br/>
			      %s
			    </div>
			  </div>
			</div>
		</div>

		<script src="lib/js/head.min.js?portal_skin=CI_slideshow"></script>
		<script src="js/reveal_custom.js?portal_skin=CI_slideshow"></script>
		<script>
			Reveal.initialize({
			  width: 1280,
			  height: 920,
				controls: true,
				progress: true,
				history: true,
				center: false,
				transition: 'slide',
				dependencies: [
					{ src: 'lib/js/classList.js?portal_skin=CI_slideshow', condition: function() { return !document.body.classList; } },
					{ src: 'lib/js/highlight.js?portal_skin=CI_slideshow', async: true, condition: function() { return !!document.querySelector( 'pre code' ); }, callback: function() { hljs.initHighlightingOnLoad(); } },
					{ src: 'plugin/js/zoom-js/zoom.js?portal_skin=CI_slideshow', async: true }
				]
			});
			Reveal.configure({ slideNumber: 'c / t' });
		</script>
	</body>
</html>""" % (
  document_theme,
  document_title,
  document_claim,
  document_theme_logo_url,
  document_title,
  document_title,
  document_content,
  document_description,
  document_creation_year,
  document_contributor_list
)
