from builtins import object
import json

# This script provides the backend-functionality of the Juypter Notebook RenderJS Extension.
# Due to the internal protocol of the ERP5Kernel and the ERP5-Jupyter-Backend messages between
# Javascript in the client and the ERP5Kernel are exchange via objections containing
# Javascript code as _repr_html_.

# Here a schematic overview of the messaging:
# 1. Extension-Function is called in the notebook (e.g. loadGadget("gadget", "https://someurl.com/gadget"))
# 2. Code is processed by the ERP5Kernel (client)
# 3. Code is sent to the ERP5-Backend
# 4. The required logic is handled by this script in the backend
# 5. This script returns an object with _repr_html_ containing the JS-response for the client
# 6. The ERP5-Backend sends a response to the ERP5Kernel (client)
# 7. The ERP5Kernel interprets the object with _repr_html_ as text/html message and injects it into the notebook
# 8. Now the Javascript code is executed as part of the (client) extension (e.g. a renderJS-gadget is loaded into the page)

class RJSExtension(object):

  def __init__(self):
    pass


  # Create the original load_gadget with modified rsvp, renderjs
  # Because jupyter notebook has already loaded when this can be called
  # a manual initialization of the whole renderJS setup is required
  #
  # First the libs rsvp, renderjs-gadget-global and renderjs (patched)
  # are injected into the page. The patch on renderjs itself is to enable
  # the following manual bootstrap

  # After the scripts are present, a div is appended containing the
  # loading_gadget.

  # After everything is inplace, rJS.manualBootstrap initializes the
  # loading_gadget in exactly the same way as when rJS is normally initialized
  # (on-load)
  def initRenderJS(self):
    script = '''
    <script>
    var loadingDiv = document.querySelector(".loading_gadget");
    if(loadingDiv == null) {
      console.log("~~ Initializing RenderJS!");
      $.getScript("/nbextensions/renderjs_nbextension/rsvp-2.0.4.js", function() {
        console.log("~~ loading_gadget: rsvp.js loaded");
        $.getScript("/nbextensions/renderjs_nbextension/rjs_gadget_global_js.js", function() {
          console.log("~~ loading_gadget: renderjs-gadget-global.js loaded");
          $.getScript("/nbextensions/renderjs_nbextension/renderjs-latest.js", function() {
            console.log("~~ loading_gadget: renderjs.js loaded");
            $("#notebook-container").append('<div data-gadget-url="/nbextensions/renderjs_nbextension/loading_gadget.html" data-gadget-scope="public"></div>');
            rJS.manualBootstrap();
          });
        });
      });
    } else {
      console.log("~~ Renderjs seems to be initialized already!");
    }
    </script>'''
    return RJSHtmlMessage(script)


  # Load a gadget given a unique ref and URL to the HTML file of the gadget
  # -> Fires an event which loading_gadget listens on and passes on the URL
  def loadGadget(self, ref, gadgetUrl):
    script = '''
    <script>
    var load_event = new CustomEvent("load_gadget",
    { "detail": { "url": "''' + gadgetUrl + '", "gadgetId": "' + ref + '''" }});

    var loadingDiv = document.querySelector(".loading_gadget");
    if(loadingDiv != null) {
      loadingDiv.dispatchEvent(load_event);
    } else {
      console.log("~~ load: RenderJS init required first!");
    }
    </script>
    '''
    return RJSHtmlMessage(script)


  # Fires an event with
  #    * the ref of the gadget
  #    * the name of the declared_method
  #    * the arguments to be passed to the declared_method
  # The arguments are packed into a json string and passed to js as such
  def callDeclaredMethod(self, ref, method_name, *args):
    j_str = json.dumps(args)
    script = '''
    <script>
    var call_event = new CustomEvent("call_gadget",
    { "detail": {
    "gadgetId": "''' + ref + '''",
    "methodName": "''' + method_name + '''",
    "methodArgs": ''' + "'" + j_str + "'" + '''
    }});
    var loadingDiv = document.querySelector(".loading_gadget");
    if(loadingDiv != null) {
    loadingDiv.dispatchEvent(call_event);
    } else {
    console.log("~~ call: RenderJS init required first!");
    }
    </script>
    '''
    return RJSHtmlMessage(script)


  # Fires an event to the destroy this gadget
  # Only thing passed is the ref of the gadget
  def destroyGadget(self, ref):
    script = '''
    <script>
    var destroy_event = new CustomEvent("destroy_gadget",
    { "detail": { "gadgetId": "''' + ref + '''" }});
    var loadingDiv = document.querySelector(".loading_gadget");
    if(loadingDiv != null) {
      loadingDiv.dispatchEvent(destroy_event);
    } else {
      console.log("~~ destroy: RenderJS init required first!");
    }
    </script>
    '''
    return RJSHtmlMessage(script)


class RJSHtmlMessage(object):
  '''
    Represents a HTML-injection into the frontend. Returning such an object from the ERP5
    backend is sufficient, as the _repr_html_ will be called internally.
  '''
  def __init__(self, html):
    self.html = html
  def _repr_html_(self):
    return self.html

obj = RJSExtension()
return obj
