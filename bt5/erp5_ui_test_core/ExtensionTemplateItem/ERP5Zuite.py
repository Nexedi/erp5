def UpdateImage(image):
  image._update_image_info()

def urlread(url):
  import urllib
  return urllib.urlopen(url).read()

def editZPT(zpt, text):
  zpt.pt_edit(text, 'text/html')

"""
  Remove everything but the test in a webpage
"""
def parseTutorial(text, title):
  import lxml.html
  from lxml import etree
  root = lxml.html.fromstring(text)
  table_list = root.xpath('//test')
  html = """
<html xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:metal="http://xml.zope.org/namespaces/metal">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>"""+ title + """</title>
  </head>
  <body>
    <table name="SELENIUM-TEST" cellpadding="1" cellspacing="1" border="1">
      <thead>
        <tr class="title">
          <td colspan="3">"""+ title + """</td>
        </tr>
      </thead>
      <tbody>
"""

  for table in table_list:
    table = table[0]
    if len(table) > 0:
      for row in table[-1]:
        if len(row) == 1:
          html += row[0].text
        else:
          html += lxml.html.tostring(row)
  html +="""
      </tbody>
    </table>
  </body>
</html>"""
  return html

"""
  Add the test at the end of the webpage (overwrite the current test if there's already one) and hide it
"""
def appendTestToWebPage(text, test_text):
  import lxml.html
  root = lxml.html.fromstring(text)
  test_root = lxml.html.fromstring(test_text)
  test_root = test_root.xpath('//table')[0]
  tutorial_test = lxml.html.fromstring('<table></table>')
  tutorial_test.tag = test_root.tag
  for att in test_root.attrib.keys():
    tutorial_test.attrib[att] = test_root.attrib[att]
  tutorial_test.append(test_root[1])
  hidden_list = [tutorial_test] + tutorial_test.xpath('//span')
  for element in hidden_list:
    element.attrib['style']='display:none;'
  table_list = root.xpath('//table[@id="SELENIUM-TEST"]')
  if(len(table_list) == 0):
    root.append(tutorial_test)
  else:
    root.replace(table_list[0], tutorial_test)
  return lxml.html.tostring(root).replace('\n','').replace("\'","'")
