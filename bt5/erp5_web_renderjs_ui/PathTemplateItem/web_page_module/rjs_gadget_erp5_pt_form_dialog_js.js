/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO */
(function (window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO) {
  "use strict";

  function extractParamListFromContentDisposition(text) {
    // text = " ATTACHMENT; FILENAME = MyFile "
    // Returns -> [" ATTACHMENT", " FILENAME = MyFile "]
    return text.split(";");
  }

  function parseContentDispositionParam(text) {
    // text = " ATTACHMENT"
    // Returns -> {name:"attachment", value:null}
    // text = " FILENAME = MyFile "
    // Returns -> {name:"filename", value:"MyFile"}
    var i, l = text.length;
    for (i = 0; i < l; i += 1) {
      if (text[i] === "=") {
        return {name: text.slice(0, i).trim().toLowerCase(), value: text.slice(i + 1).trim()};
      }
    }
    return {name: text.trim().toLowerCase(), value: null};
  }

  function parseEachContentDispositionParamToDict(paramList) {
    // paramList = [" ATTACHMENT", " FILENAME = MyFile "]
    // Returns -> {attachment: null, filename: "MyFile"}
    var i, l = paramList.length, r = {}, p = null;
    for (i = 0; i < l; i += 1) {
      p = parseContentDispositionParam(paramList[i]);
      r[p.name] = p.value;
    }
    return r;
  }

  function parseContentDisposition(text) {
    // text = " ATTACHMENT; FILENAME = MyFile "
    // Returns -> {attachment:null, filename:"MyFile"}
    return parseEachContentDispositionParamToDict(extractParamListFromContentDisposition(text));
  }

  function extractFilenameFromContentDisposition(text) {
    // text = " ATTACHMENT; FILENAME = \"MyFile \" "
    // Returns -> "MyFile "
    var o = parseContentDisposition(text);
    if (typeof o.filename === "string") {
      if (o.filename[0] === "\"" && o.filename[o.filename.length - 1] === "\"") {
        return o.filename.slice(1, -1);
      }
      return o.filename;
    }
    return null;
  }

  rJS(window)
    .setState({
      title: ""
    })
    /////////////////////////////////////////////////////////////////
    // acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("displayFormulatorValidationError",
                           "displayFormulatorValidationError")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      this.element.querySelector('input[type="submit"]').click();
    })

    .declareMethod('render', function (options) {
      var state_dict = {
        id: options.jio_key,
        view: options.view,
        editable: options.editable,
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        erp5_form: options.erp5_form || {}
      };

      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var form_gadget = this,
        icon,
        selector = form_gadget.element.querySelector("h3"),
        title,
        i,
        view_list = this.state.erp5_document._links.action_workflow || [];

      title = this.state.form_definition.title;

      // XXX hardcoded...
      switch (title) {
      case "Create User":
        icon = " ui-icon-user";
        break;
      case "Create Document":
        icon = " ui-icon-file-o";
        break;
      case "Validate Workflow Action":
        icon = " ui-icon-share-alt";
        break;
      case "Submit":
        icon = " ui-icon-check";
        break;
      default:
        icon = " ui-icon-random";
        break;
      }

      for (i = 0; i < view_list.length; i += 1) {
        if (view_list[i].href === this.state.view) {
          title = view_list[i].title;
        }
      }


      // Calculate the h3 properties
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            form_gadget.translate(form_gadget.state.form_definition.title),
            form_gadget.translate(title)
          ]);
        })
        .push(function (translated_title_list) {
          form_gadget.element.querySelector('input.dialogconfirm').value = translated_title_list[1];

          selector.textContent = "\u00A0" + translated_title_list[0];
          selector.className = "ui-content-title ui-body-c ui-icon ui-icon-custom" + icon;

          // Render the erp5_from
          return form_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          var form_options = form_gadget.state.erp5_form;

          // <span class="ui-icon ui-icon-custom ui-icon-random">&nbsp;</span>
          form_options.erp5_document = form_gadget.state.erp5_document;
          form_options.form_definition = form_gadget.state.form_definition;
          form_options.view = form_gadget.state.view;
          return erp5_form.render(form_options);
        })
        .push(function () {
          // Render the headers
          return RSVP.all([
            form_gadget.getUrlFor({command: 'change', options: {page: undefined, view: undefined}}),
            calculatePageTitle(form_gadget, form_gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          form_gadget.element.querySelector('a.dialogcancel').href = all_result[0];
          return form_gadget.updateHeader({
            cancel_url: all_result[0],
            page_title: all_result[1]
          });
        });
    })

    .declareJob("deferRevokeObjectUrlWithLink", function (object_url, a_tag) {
      return new RSVP.Queue()
        .push(function () {
          return RSVP.delay(10);
        })
        .push(function () {
          URL.revokeObjectURL(object_url);
          document.body.removeChild(a_tag);
        });
    })

    .onEvent('submit', function () {
      var form_gadget = this,
        action = this.state.erp5_document._embedded._view._actions.put,
        form_id = this.state.erp5_document._embedded._view.form_id,
        redirect_to_parent;

      return form_gadget.notifySubmitting()
        .push(function () {
          return form_gadget.getDeclaredGadget("erp5_form");
        })
        .push(function (erp5_form) {
          return erp5_form.getContent();
        })
        .push(function (content_dict) {
          var data = {},
            key;

          data[form_id.key] = form_id['default'];
          // XXX Hardcoded
          data.dialog_id = form_id['default'];
          data.dialog_method = action.action;
          //XXX hack for redirect, difined in form
          redirect_to_parent = content_dict.field_your_redirect_to_parent;
          for (key in content_dict) {
            if (content_dict.hasOwnProperty(key)) {
              data[key] = content_dict[key];
            }
          }

          return form_gadget.jio_putAttachment(
            form_gadget.state.id,
            action.href,
            data
          );

        })
        .push(function (evt) {
          if (evt.target.responseType === "blob") {
            return RSVP.all([
              evt,
              jIO.util.readBlobAsText(evt.target.response)
            ]);
          }
          return [evt, {target: {result: evt.target.response}}];
        })
        .push(function (result_list) {
          var evt = result_list[0],
            responseText = result_list[1].target.result,
            location = evt.target.getResponseHeader("X-Location"),
            jio_key,
            list = [],
            a,
            object_url,
            message;
          try {
            message = JSON.parse(responseText).portal_status_message;
          } catch (ignore) {
          }
          list.push(form_gadget.notifySubmitted(message));

          if (redirect_to_parent) {
            list.push(form_gadget.redirect({command: 'history_previous'}));
          } else {
            if (location === undefined || location === null) {
              // Download the data
              if (evt.target.responseType === "blob") {
                message = evt.target.response;
              } else {
                message = new Blob([evt.target.response], {type: evt.target.getResponseHeader("Content-Type")});
              }
              object_url = URL.createObjectURL(message);
              a = document.createElement("a");
              a.style = "display: none";
              a.href = object_url;
              a.download = extractFilenameFromContentDisposition(evt.target.getResponseHeader("Content-Disposition")) || "untitled";
              document.body.appendChild(a);
              a.click();
              form_gadget.deferRevokeObjectUrlWithLink(object_url, a);
            } else {
              jio_key = new URI(location).segment(2);
              if (form_gadget.state.id === jio_key) {
                // Do not update navigation history if dialog redirect to the same document
                list.push(form_gadget.redirect({command: 'change', options: {jio_key: jio_key, view: "view", page: undefined, editable: form_gadget.state.editable}}));
              } else {
                list.push(form_gadget.redirect({command: 'push_history', options: {jio_key: jio_key, editable: form_gadget.state.editable}}));
              }
            }
          }
          return RSVP.all(list);
        })
        .push(undefined, function (error) {
          if (error.target !== undefined) {
            var error_text = 'Encountered an unknown error. Try to resubmit',
              promise;
            // if we know what the error was, try to precise it for the user 
            if (error.target.status === 400) {
              error_text = 'Input data has errors';
            } else if (error.target.status === 403) {
              error_text = 'You do not have the permissions to edit the object';
            } else if (error.target.status === 0) {
              error_text = 'Document was not saved! Resubmit when you are online or the document accessible';
            }
            // display translated error_text to user
            promise = form_gadget.notifySubmitted()
              .push(function () {
                return form_gadget.translate(error_text);
              })
              .push(function (message) {
                return form_gadget.notifyChange(message + '.');
              });
            // if server validation of form data failed (indicated by response code 400)
            // we parse out field errors and display them to the user
            if (error.target.status === 400) {
              promise
                .push(function () {
                  // when the server-side validation returns the error description
                  if (error.target.responseType === "blob") {
                    return jIO.util.readBlobAsText(error.target.response);
                  }
                  // otherwise return (most-likely) textual response of the server
                  return {target: {result: error.target.response}};
                })
                .push(function (event) {
                  return form_gadget.displayFormulatorValidationError(JSON.parse(event.target.result));
                });
            }
            return promise;
          }
          throw error;
        });

    }, false, true);


}(window, rJS, RSVP, URI, calculatePageTitle, Blob, URL, document, jIO));