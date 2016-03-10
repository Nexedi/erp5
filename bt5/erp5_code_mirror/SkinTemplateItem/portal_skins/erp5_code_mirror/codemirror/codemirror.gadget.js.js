/*jslint nomen: true, indent: 2 */
/*global window, rJS, CodeMirror, document, RSVP, loopEventListener */
(function (window, rJS, CodeMirror, RSVP) { //, loopEventListener) {
  "use strict";

  // XXXXXXXXXXXXXXXXXXX REMOVE THIS FUNCTION AFTER ADDING IT ON ERP5 GLOBALS ON CLASSIC VIEWS
  var loopEventListener = function (target, type, useCapture, callback, prevent_default) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback, callback_promise;

    if (prevent_default === undefined) {
      prevent_default = true;
    }

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        target.removeEventListener(type, handle_event_callback, useCapture);
      }
      cancelResolver();
    }
    function itsANonResolvableTrap(resolve, reject) {
      var result;
      handle_event_callback = function (evt) {
        if (prevent_default) {
          evt.stopPropagation();
          evt.preventDefault();
        }

        cancelResolver();

        try {
          result = callback(evt);
        } catch (e) {
          result = RSVP.reject(e);
        }

        callback_promise = result;
        new RSVP.Queue()
        .push(function () {
          return result;
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            canceller();
            reject(error);
          }
        });
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  };

  function requestFullScreen(element) {
    if ((document.fullScreenElement && document.fullScreenElement !== null) ||
        (!document.mozFullScreen && !document.webkitIsFullScreen)) {
      if (element.requestFullScreen) {
        element.requestFullScreen();
      } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
      } else if (element.webkitRequestFullScreen) {
        /*global Element */
        element.webkitRequestFullScreen(Element.ALLOW_KEYBOARD_INPUT);
      }
    }
  }
  function multiAddEventListener(object, event_names, listener) {
    event_names.forEach(function (event_name) {
      object.addEventListener(event_name, listener);  // XXX don't use addEventListener!
    });
  }
  function multiRemoveEventListener(object, event_names, listener) {
    event_names.forEach(function (event_name) {
      object.removeEventListener(event_name, listener);  // XXX don't use removeEventListener!
    });
  }

  function gadgetRequestFullScreen(gadget) {
    var cm = gadget.props.editor, event_names = ["webkitfullscreenchange", "mozfullscreenchange", "fullscreenchange"];
    requestFullScreen(cm.getWrapperElement());
    multiAddEventListener(document, event_names, function listener() {
      multiRemoveEventListener(document, event_names, listener);
      cm.setOption("fullScreen", true);
      multiAddEventListener(document, event_names, function listener2() {
        multiRemoveEventListener(document, event_names, listener2);
        cm.setOption("fullScreen", false);
      });
    });
  }

  function gadgetRequestMaximize(gadget) {  // put to a declared method ? (maximize)
    return gadget.requestMaximize()
      .push(function (accepted) {
        if (accepted) {
          if (gadget.props.maximizeButton) {  // XXX display button on maximized ?
            gadget.props.maximizeButton.textContent = "Unmaximize";
          }
          gadget.props.maximized = true;
          gadget.props.editor.getWrapperElement().style.height = "100%";
          gadget.props.editor.refresh();
        }
      });
  }

  function gadgetLeaveMaximize(gadget) {  // put to a declared method ? (unmaximize)
    return gadget.leaveMaximize()
      .push(function (accepted) {
        if (accepted) {
          if (gadget.props.maximizeButton) {  // XXX display button on maximized ?
            gadget.props.maximizeButton.textContent = "Maximize";
          }
          gadget.props.maximized = false;
          gadget.props.editor.getWrapperElement().style.height = "";
          gadget.props.editor.refresh();
        }
      });
  }

  function cmFoldAtCursor(cm) {
    cm.foldCode(cm.getCursor());
  }

  rJS(window)
    //.declareAcquiredMethod("submitData", "triggerSubmit")
    .declareAcquiredMethod("requestMaximize", "requestMaximize")
    .declareAcquiredMethod("leaveMaximize", "leaveMaximize")
    .ready(function (g) {
      g.props = {};
      g.options = null;

      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareMethod('render', function (options) {
      var event_list = [], submit_data_deferred = RSVP.defer();
      this.props.key = options.key;
      this.props.value = options.value || "";
      this.props.editable = options.editable === undefined ? true : options.editable;
      if (this.props.editable) {
        this.props.textarea = document.createElement("textarea");
        this.props.textarea.value = this.props.value;
        this.props.maximizeButton = document.createElement("button");
        this.props.maximizeButton.textContent = "Maximize";
        this.props.fullScreenButton = document.createElement("button");
        this.props.fullScreenButton.textContent = "Fullscreen";
        this.props.element.appendChild(this.props.maximizeButton);
        this.props.element.appendChild(this.props.fullScreenButton);
        this.props.element.appendChild(this.props.textarea);
        this.props.editor = CodeMirror.fromTextArea(
          this.props.textarea,
          {
            lineNumbers: true,
            matchBrackets: true,
            showCursorWhenSelecting: true,
            autofocus: false,
            indentWithTabs: false,
            fullScreen: false,
            extraKeys: {
              "Ctrl-Space": "autocomplete",
              "Ctrl-Q": cmFoldAtCursor,
              "Ctrl-S": function (cm) {
                this.submitData().push(null, submit_data_deferred.reject);
              }.bind(this)
            }
          }
        );
        event_list.push(submit_data_deferred.promise);
        event_list.push(loopEventListener(this.props.element, "keyup", false, function (event) {
          if (this.props.maximized && event.keyCode === 27) {
            event.preventDefault();
            return gadgetLeaveMaximize(this);
          }
        }.bind(this), false));
        event_list.push(loopEventListener(this.props.maximizeButton, "click", false, function (event) {
          this.props.editor.focus();
          if (this.props.maximized) {  // XXX display button on maximized ?
            return gadgetLeaveMaximize(this);
          }
          return gadgetRequestMaximize(this);
        }.bind(this)));
        event_list.push(loopEventListener(this.props.fullScreenButton, "click", false, function (event) {
          this.props.editor.focus();
          return gadgetRequestFullScreen(this);
        }.bind(this)));
      } else {
        this.props.pre = document.createElement("pre");
        this.props.pre.textContent = this.props.value;
        this.props.element.appendChild(this.props.pre);
      }
      return RSVP.all([event_list]);
    })
    .declareMethod('getContent', function () {
      var form_data = {};
      if (this.props.editable) {
        form_data[this.props.key] = this.props.editor.getValue();
      } else {
        form_data[this.props.key] = this.props.value;
      }
      return form_data;
    });
}(window, rJS, CodeMirror, RSVP));//, loopEventListener));
