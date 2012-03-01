"""
  Parse the test report
"""
def parseTestReport(text):
  from lxml import etree
  parser = etree.HTMLParser(remove_comments=True)
  parser.feed(text)
  root = parser.close()
  table = root.xpath('//table[@id="SELENIUM-TEST"]')[0]
  report = dict()
  header = table[0][0]
  report['status'] = header.attrib['class'].find('passed') > -1
  report['name'] = header[0].text
  report["row_list"] = []
  report["column_list"] = [0,0,0]
  i=0
  for row in table[1]:
    report["row_list"].append(dict(cell_list=[], passed=False, failed=False, done=False, not_done=False))
    row_report = report["row_list"][i]
    if row.attrib['class'].find('failed') > -1:
      row_report['failed'] = True
    elif row.attrib['class'].find('done') > -1:
      row_report['done'] = True
    elif row.attrib['class'].find('passed') > -1:
      row_report['passed'] = True
    else:
      row_report['not_done'] = True
    for column in row:
      row_report["cell_list"].append(column.text)
    i += 1
  return report
  """
  title = table.xpath('//td')[0].text
  html[0][1].text = title

  # Insert completly the first table
  html[1].append(table)

  # Insert only the content of tbody
  for table in table_list[1:]:
    for row in table[-1]:
      html[1][-1].append(row)

  stack = [html[1]]
  # Let's display everything in the test by removing the style attributes (they're not supposed to have any style attributes at all during the tests)
  while stack:
    element = stack.pop()
    if element.attrib.has_key('style'):
      del element.attrib['style']
    for child in element:
      stack.append(child)
  
  return dict(title = title, text = lxml.html.tostring(html))
  """

"""
  Parse a HTML page and return a list of dictionnaries with the chapters and the tests they contain
"""
def parseTutorial(text):
  from Products.ERP5Type.Document import newTempBase
  from lxml import etree
  parser = etree.HTMLParser(remove_comments=True)
  parser.feed(text)
  root = parser.close()
  table_list = root.xpath('//table[@id="SELENIUM-TEST"]')
  table = table_list[0]

  listbox = []

  i = 0
  # Insert only the content of tbody
  for table in table_list:
    listbox.append(newTempBase(context.getPortalObject(),
                               '',
                               title = "Tested Chapter " + str(i),
                               tag   = 'h1'))
    if len(table) > 0:
      for row in table[-1]:
        if(row.tag.lower() == 'tr'):
          listbox.append(newTempBase(context.getPortalObject(),
                               '',
                               title = row[0][0].text,
                               tag   = 'tr',
                               arg0  = row[0][1].text,
                               arg1  = row[0][2].text))
        else:
          listbox.append(newTempBase(context.getPortalObject(),
                               '',
                               title = row[0][0].text,
                               tag   = 'tr',
                               arg0  = row[0][1].text,
                               arg1  = row[0][2].text))
          

  stack = [html[1]]
  # Let's display everything in the test by removing the style attributes (they're not supposed to have any style attributes at all during the tests)
  while stack:
    element = stack.pop()
    if element.attrib.has_key('style'):
      del element.attrib['style']
    for child in element:
      stack.append(child)
  
  return dict(title = title, text = lxml.html.tostring(html))

"""
  Return the content of a web page
"""
def urlread(url):
  import urllib
  return urllib.urlopen(url).read()

"""
  Remove everything but the test in a webpage
"""
def extractTest(text):
  import lxml.html
  from lxml import etree
  root = lxml.html.fromstring(text)
  table_list = root.xpath('//test')
  testcode = ""
  for table in table_list:
    table = table[0]
    if len(table) > 0:
      for row in table[-1]:
        if len(row) == 1:
          # Include Macros as it is defined by the user.
          testcode += row[0].text
        else:
          testcode += lxml.html.tostring(row)
  return testcode 
