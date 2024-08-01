from App.Management import Navigation
from ZODB.POSException import ConflictError
from Acquisition import aq_parent
import json
import six

def manage_page_footer(self):
  default = '</body></html>'
  # Not within an ERP5 Site, use default footer
  if getattr(self, 'getPortalObject', None) is None:
    return default

  portal = self.getPortalObject()
  try:
    # Make sure we are able to display ZMI when preference tool / catalog does
    # not work.
    editor = portal.portal_preferences.getPreference('preferred_source_code_editor')
  except ConflictError:
    raise
  except:
    editor = None

  # REQUEST['PUBLISHED'] can be the form in the acquisition context of the
  # document, or a method bound to the document (after a POST it is a bound method)
  published = self.REQUEST.get('PUBLISHED')
  document = getattr(published, '__self__', None) # bound method
  if document is None:
    document = aq_parent(published)

  if getattr(document, 'meta_type', None) is None:
    return default

  portal_url = portal.portal_url()
  mode = 'plain_text'    # default mode
  textarea_selector = '' # jQuery selector for the origin textarea that we will
                         # change into an editor

  live_check_python_script = 0 # Check python scripts on the fly
  bound_names = 'undefined'

  if document.meta_type in ('DTML Document', 'DTML Method'):
    if document.getId().endswith('.js'):
      mode = 'javascript'
    elif document.getId().endswith('.ts'):
      mode = 'typescript'
    elif document.getId().endswith('.css'):
      mode = 'css'
    textarea_selector = 'textarea[name="data:text"]'
  elif document.meta_type in ('File', ):
    if 'javascript' in document.getContentType():
      mode = 'javascript'
    elif 'typescript' in document.getContentType():
      mode = 'typescript'
    elif 'css' in document.getContentType():
      mode = 'css'
    elif 'html' in document.getContentType():
      if editor == 'codemirror':
        mode = 'htmlmixed'
      else:
        mode = 'html'
    textarea_selector = 'textarea[name="filedata:text"]'
  elif document.meta_type in ('Script (Python)', 'ERP5 Python Script', 'ERP5 Workflow Script', ):
    mode = 'python'
    textarea_selector = 'textarea[name="body:text"]'
    # printed is from  RestrictedPython.RestrictionMutator the rest comes
    # from RestrictedPython.Utilities.utility_builtins
    bound_names = json.dumps(
      document.getBindingAssignments().getAssignedNamesInOrder()
       + ['printed', 'same_type', 'string', 'sequence', 'random', 'DateTime',
           'whrandom', 'reorder', 'sets', 'test', 'math'])
    live_check_python_script = 1 # XXX make it a preference ?
  elif document.meta_type in ('Z SQL Method', 'ERP5 SQL Method'):
    mode = 'sql'
    textarea_selector = 'textarea[name="template:text"]'
  elif document.meta_type in ('Page Template', 'ERP5 OOo Template', ):
    if 'html' in document.content_type:
      if editor == 'codemirror':
        mode = 'htmlmixed'
      else:
        mode = 'html'
    else:
      mode = 'xml'
    textarea_selector = 'textarea[name="text:text"]'

  if mode == 'plain_text':
    if document.getId().endswith('.less'):
      mode = 'less'

  if not textarea_selector:
    return default

  portal_type = document.meta_type
  if editor == 'codemirror' and getattr(portal, 'code_mirror_support', None) is not None:
    keymap = portal.portal_preferences.getPreferredSourceCodeEditorKeymap()
    return '''<script type="text/javascript" src="%s/jquery/core/jquery.min.js"></script>
              %s
              </body>
            </html>''' % (portal_url,
                          portal.code_mirror_support(textarea_selector=textarea_selector,
                                                     portal_url=portal_url,
                                                     bound_names=bound_names,
                                                     mode=mode,
                                                     keymap=keymap,
                                                     portal_type=portal_type))
  elif editor == 'monaco' and getattr(portal, 'monaco_editor_support', None) is not None:
    monaco_editor_support = portal.monaco_editor_support(
      textarea_selector=textarea_selector,
      portal_url=portal_url,
      bound_names=bound_names,
      mode=mode)
    if six.PY2:
      monaco_editor_support = monaco_editor_support.encode('utf-8')
    return '''%s
              </body>
            </html>''' % monaco_editor_support
  elif editor in (None, 'text_area') and mode == 'python':
    # Set Zope4's default ace editor indent size to 2.
    return '''<script type="text/javascript">$(function(){if(typeof ace == "object"){ace.config.$defaultOptions.session.tabSize.initialValue = 2;} if(typeof editor == "object"){editor.getSession().setTabSize(2);}})</script>'''

  return default

Navigation.manage_page_footer = manage_page_footer
