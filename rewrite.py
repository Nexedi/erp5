#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function

# Rewrite workflow history lists for the new format introduced in
#   https://lab.nexedi.com/nexedi/erp5/merge_requests/941
# executed with:
#   find -wholename '**Item/portal_components/**.xml' -or -wholename '**/PathTemplateItem/**.xml' | xargs -n10 -P10 ~/srv/slapos/soft/7b82cba46eead19d8388b0a3359c6185/bin/python rewrite.py | tee rewrite.log

import sys
from lxml import etree
from lxml.builder import E

def reindent(elements):
  """Reindent the workflow item list that is now in a _log
  """
  for e in elements:
    if e.text and '\n' in e.text:
      e.text = e.text + '      '
    if e.tail and '\n' in e.tail:
      if e.tag == 'item':
        if e.tail == '\n            ':
          e.tail =   '\n                  '
        else:
          assert e.tail == '\n          '
          e.tail =         '\n                '
      else:
        e.tail = e.tail + '      '
    # this is not about reindenting, but also make sure that <string></string>
    # does not become <string/> in this process.
    if e.tag == 'string' and not e.text:
      e.text = ''
    reindent(e)
  return elements



for filename in sys.argv[1:]:
  with open(filename, 'r') as f:
    previous_content = f.read()
  if '<![CDATA[' in previous_content:
    print ('🙈 ', filename, "skipped because it uses CDATA that this script does not know how to convert")
    continue
  if 'Products.ERP5Type.Message' in previous_content:
    print ('🙈 ', filename, "skipped because it uses Products.ERP5Type.Message that this script does not know how to convert")
    continue

  with open(filename) as f:
    tree = etree.parse(f)
  root = tree.getroot()

  # this script does not know how to convert this (we have some only in erp5_demo_maxma_sample )
  if tree.xpath(
      '//record/pickle/tuple/global[@name="WorkflowHistoryList" and @module="Products.ERP5Type.patches.WorkflowTool"]'
    ):
    print ('🙈 ', filename, "skipped because it uses tuple in for WorkflowHistoryList")
    continue

  class_name_elements = tree.xpath(
      '//record/pickle/global[@name="WorkflowHistoryList" and @module="Products.ERP5Type.patches.WorkflowTool"]'
  )

  if not class_name_elements:
    print ('✅ ', filename, "was already up to date")
    continue

  skipped = False
  for class_name_element in class_name_elements:
    if class_name_element.find('../../pickle[2]/tuple/').tag != 'none':
      print ('🙈 ', filename, "skipped because it has multiple buckets WorkflowHistoryList which this script does not know how to convert")
      skipped = True
      break

    class_name_element.attrib['module'] = 'Products.ERP5Type.Workflow'
    old_pickle, = class_name_element.xpath('../../pickle[2]')

    record = old_pickle.getparent()
    record.remove(old_pickle)

    pickle = E.pickle(
      '\n      ',
      E.dictionary(
        '\n        ',
        E.item(
          '\n            ',
          E.key(' ', E.string('_log'), ' '),
          '\n            ',
          E.value(
            '\n              ',
            # We save **all** the list in the same bucket
            # while not strictly correct, business template histories
            # should not be long. Most have only one element.
            *reindent(old_pickle.xpath('./tuple//list'))),
            '\n        '
        ),
        '\n      '
      ),
      '\n    '
    )
    pickle.tail = '\n  '
    record.append(pickle)
  if skipped:
    continue

  new_content = '<?xml version="1.0"?>\n' + etree.tostring(root, pretty_print=True, encoding="utf-8")
  if new_content == previous_content:
    print ('✅ ', filename, "was already up to date")
  else:
    with open(filename, 'w') as f:
      f.write(new_content)
    print ('✍️ ', filename, "updated to new WorkflowHistoryList serialization format")
