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
  Return the content of a web page
"""
def urlread(url):
  from six.moves.urllib.request import urlopen
  return urlopen(url).read()

"""
  Remove everything but the test in a webpage
"""
def extractTest(text):
  import lxml.html
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
  return testcode.strip()

"""
  HTML5 Presentation validador
"""
def validateHTML5Document(text):
  import lxml.html
  root = lxml.html.fromstring(text)
  section_list = root.xpath('//section')
  count = 0
  error_list = []
  # XXX Lack of translation support here.
  for section in section_list:
    count += 1
    if section.xpath("h1") == []:
      error_list.append("Section %s had no h1." % count)

    if section.get("class") in ["screenshot", "illustration"]:
      if section.xpath("img") == []:
        error_list.append("Section %s has class %s but it doesn't have any image." % (count, section.get("class")))
      else:
        if section.xpath("img")[0].get("title") == None:
          error_list.append("At section %s, img has no title attribute." % count)

        if section.xpath("img")[0].get("alt") == None:
          error_list.append("At section %s, img has no alt attribute." % count)

    if section.xpath("details") == []:
      error_list.append("Section %s has no details tag." % (count))

  return error_list
