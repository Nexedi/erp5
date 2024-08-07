from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
import six

class TestWorkflowMixin(ERP5TypeTestCase):
  def getWorklistDocumentCountFromActionName(self, action_name):
    # action_name look like: "Documents to validate (3)"
    self.assertEqual(action_name[-1], ')')
    left_parenthesis_offset = action_name.rfind('(')
    self.assertNotEqual(left_parenthesis_offset, -1)
    return int(action_name[left_parenthesis_offset + 1:-1])

  def checkWorklist(self, action_list, name, count,
                    url_parameter_dict=None, workflow_id=None):
    entry_list = [
      x for x in action_list if x['name'].startswith(name)
                             and (
                               workflow_id is None
                               or 'workflow_id' in x
                                  and x['workflow_id'] == workflow_id
                             )
    ]

    # ensure there is a single entry in action list
    self.assertEqual(len(entry_list), count and 1)
    if count:
      self.assertEqual(count,
        self.getWorklistDocumentCountFromActionName(entry_list[0]['name']))
    if entry_list and url_parameter_dict:
      url = entry_list[0].get('url')
      self.assertTrue(url, 'Can not check url parameters without url')
      url = '%s%s' % (self.portal.getId(), url[len(self.portal.absolute_url()):])
      # Touch URL to save worklist parameters in listbox selection
      self.assertEqual(200, self.publish(url, user='manager').getStatus())
      self.commit()

      selection_name = getattr(self, 'module_selection_name', None)
      if selection_name is not None:
        selection_parameter_dict = self.portal.portal_selections.getSelectionParamsFor(selection_name)
        for parameter, value in six.iteritems(url_parameter_dict):
          self.assertIn(parameter, selection_parameter_dict)
          self.assertEqual(value, selection_parameter_dict[parameter])

  def clearCache(self):
    self.portal.portal_caches.clearAllCache()
