from App.Management import Navigation
from ZODB.POSException import ConflictError
from Acquisition import aq_parent
import json

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

  if editor not in ('ace', 'codemirror'):
    return default

  # REQUEST['PUBLISHED'] can be the form in the acquisition context of the
  # document, or a method bound to the document (after a POST it is a bound method)
  published = self.REQUEST['PUBLISHED']
  document = getattr(published, 'im_self', None) # bound mehtod
  if document is None:
    document = aq_parent(published)

  if getattr(document, 'meta_type', None) is None:
    return default

  portal_url = portal.portal_url()
  mode = 'plain_text'    # default mode
  textarea_selector = '' # jQuery selector for the origin textarea that we will
                         # change into an ace editor

  live_check_python_script = 0 # Check python scripts on the fly
  bound_names = 'undefined'

  if document.meta_type in ('DTML Document', 'DTML Method'):
    if document.getId().endswith('.js'):
      mode = 'javascript'
    elif document.getId().endswith('.css'):
      mode = 'css'
    textarea_selector = 'textarea[name="data:text"]'
  elif document.meta_type in ('File', ):
    if 'javascript' in document.getContentType():
      mode = 'javascript'
    elif 'css' in document.getContentType():
      mode = 'css'
    textarea_selector = 'textarea[name="filedata:text"]'
  elif document.meta_type in ('Script (Python)', ):
    mode = 'python'
    textarea_selector = 'textarea[name="body:text"]'
    # printed is from  RestrictedPython.RestrictionMutator the rest comes
    # from RestrictedPython.Utilities.utility_builtins
    bound_names = json.dumps(
      document.getBindingAssignments().getAssignedNamesInOrder()
       + ['printed', 'same_type', 'string', 'sequence', 'random', 'DateTime',
           'whrandom', 'reorder', 'sets', 'test', 'math'])
    live_check_python_script = 1 # XXX make it a preference ?
  elif document.meta_type in ('Z SQL Method', ):
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

  if not textarea_selector:
    return default

  if editor == 'codemirror' and getattr(portal, 'code_mirror_support', None) is not None:
    return '''<script type="text/javascript" src="%s/jquery/core/jquery.min.js"></script>
              %s
              </body>
            </html>''' % (portal_url,
                          portal.code_mirror_support(textarea_selector=textarea_selector,
                                                     portal_url=portal_url,
                                                     bound_names=bound_names,
                                                     mode=mode))
  else:
    return '''
<script type="text/javascript" src="%(portal_url)s/jquery/core/jquery.min.js"></script>
<script type="text/javascript" src="%(portal_url)s/ace/ace.js"></script>
<script type="text/javascript" src="%(portal_url)s/ace/mode-%(mode)s.js"></script>
<script type="text/javascript" src="%(portal_url)s/ace/ext-settings_menu.js"></script>
<script type="text/javascript" src="%(portal_url)s/ace/ext-language_tools.js"></script>

<script type="text/javascript">
$(document).ready(function() {
  var textarea = $('%(textarea_selector)s');
  if (textarea.length) {
    $('<div id="editor">')
      .css({"position": "relative", "height": textarea.height()})
      .appendTo(textarea.parent());
    textarea.hide();

    var beforeunload_warning_set = false,
        editor = ace.edit("editor"),
        Mode = ace.require('ace/mode/%(mode)s').Mode;

    editor.getSession().setMode(new Mode());
    editor.getSession().setTabSize(2);

    ace.require("ace/ext/language_tools");
    editor.setOptions({ enableBasicAutocompletion: true, enableSnippets: true });

    timer = 0;
    function checkPythonScript() {
      if (%(live_check_python_script)s) {
        if (timer) {
          window.clearTimeout(timer);
          timer = 0;
        }
        timer = window.setTimeout(function() {
          $.post('%(portal_url)s/ERP5Site_checkPythonSourceCodeAsJSON',
            {'data': JSON.stringify(
            { code: editor.getSession().getValue(),
              bound_names: %(bound_names)s,
              params: $('input[name="params"]').val() })},
            function(data){
              editor.getSession().setAnnotations(data.annotations);
            }
          )
        }, 500);
      }
    }

    editor.getSession().setValue(textarea.val());
    var href_line_array = /.*?[^#]*line=(\d+)/.exec(window.location.href)
    if(href_line_array && href_line_array.length == 2) {
      editor.focus();
      editor.gotoLine(href_line_array[1], 0, false);
    }

    editor.getSession().on('change', function(){
      textarea.val(editor.getSession().getValue());
      if (!beforeunload_warning_set) {
        window.onbeforeunload = function() { return "You have unsaved changes"; };
        beforeunload_warning_set = true;
      }
      checkPythonScript();
    });

    checkPythonScript();

    $('input[value="Save Changes"]').click(function() {
        window.onbeforeunload = function() { return; };
    });

    editor.commands.addCommand({
      name: "save",
      bindKey: {win: "Ctrl-S", mac: "Command-S"},
      exec: function() {
        $('input[value="Save Changes"]').click();
      }
    });

    ace.require('ace/ext/settings_menu').init(editor);

  };
});
</script>
</body>
</html>''' % locals()

Navigation.manage_page_footer = manage_page_footer
