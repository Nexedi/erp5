css_link = context.REQUEST.get("css_link", "slides.css")

return"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <link href="//fonts.googleapis.com/css?family=Oswald" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="%s">
    <script type="text/javascript" src="slides.js"></script>
    <meta charset="utf-8">
    <title>%s</title>
    <!-- Your Slides -->
  </head>
  <body>
%s
  </body>
</html>""" % (css_link, context.getTitle(), context.getTextContent())
