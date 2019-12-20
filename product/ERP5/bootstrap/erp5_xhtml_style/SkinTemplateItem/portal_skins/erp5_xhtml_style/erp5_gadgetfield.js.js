/*global window, rJS, RSVP, document, console*/
/*jslint nomen: true, maxlen:80, indent:2*/
(function (window, rJS, RSVP, document, console) {
  "use strict";

  function promiseEventListener(target, type, useCapture) {
    //////////////////////////
    // Resolve the promise as soon as the event is triggered
    // eventListener is removed when promise is cancelled/resolved/rejected
    //////////////////////////
    var handle_event_callback;

    function canceller() {
      target.removeEventListener(type, handle_event_callback, useCapture);
    }

    function resolver(resolve) {
      handle_event_callback = function (evt) {
        canceller();
        evt.stopPropagation();
        evt.preventDefault();
        resolve(evt);
        return false;
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function displayFieldError(error) {
    console.warn(error);
    // Display the error message in the portal_status location
    // As renderJS does not report which element is failing while loading
    // a gadget
    var error_element = document.getElementById('transition_message');
    error_element.textContent = error + '. ' + error_element.textContent;
  }

  function getGadgetContent(gadget) {
    return gadget.getContent()
      .push(undefined, function (error) {
        // Do not crash if gadget getContent is wrongly implemented,
        // ie, UI should work even if one gadget does not
        displayFieldError(error);
        return {};
      });
  }

  rJS(window)
    .setState({
      rejected_dict: {},
      field_list: [],
      gadget_list: []
    })

    .allowPublicAcquisition('reportGadgetDeclarationError',
                            function (argument_list, scope) {
        // Do not crash the UI in case of wrongly configured gadget,
        // bad network, loading bug.
        this.state.rejected_dict[scope] = null;
        return displayFieldError(argument_list[0]);
      })


    .allowPublicAcquisition('reportServiceError',
                            function (argument_list) {
        // Do not crash the UI in case of gadget service error.
        return displayFieldError(argument_list[0]);
      })

    /////////////////////////////////////////////////////////////////
    // Support some methods used in ERP5JS
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition('notifyChange',
                            function () {
       // This flag is used for erp5.js's onBeforeUnload warning for unsaved changes.
        window.changed = true;
        return;
      })

    .allowPublicAcquisition('notifyValid',
                            function () {
        return;
      })

    .allowPublicAcquisition('notifySubmit', function () {
      return this.element.querySelector('form').querySelector('[type="submit"]').click();
    })

    // Comply to interface_translation.html, but without actually translating.
    .allowPublicAcquisition('translate', function (argument_list) {
      return argument_list[0];
    })
    .allowPublicAcquisition('getTranslationList', function (argument_list) {
      return argument_list[0];
    })
    .allowPublicAcquisition('translateHtml', function (argument_list) {
      return argument_list[0];
    })
    .allowPublicAcquisition('redirect', function (argument_list) {
        var argument = argument_list[0];
        if (argument.command === 'raw' && argument.options && argument.options.url) {
          location.replace(argument.options.url);
        }
      })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      // Call render on all gadget fields
      var gadget = this,
        field_list = [],
        i;

      return new RSVP.Queue()
        .push(function () {
          var field_element_list =
            gadget.element.querySelectorAll("[data-gadget-value]"),
            field_element,
            field_scope,
            field_url,
            promise_list = [];

          for (i = 0; i < field_element_list.length; i += 1) {
            field_element = field_element_list[i];
            field_url = field_element.getAttribute("data-gadget-url");
            field_scope = field_element.getAttribute("data-gadget-scope");

            // Renderable
            if ((field_url !== undefined) && (field_url !== null) &&
                (field_scope !== null) &&
                (!gadget.state.rejected_dict.hasOwnProperty(field_scope))) {
              field_list.push({
                sandbox: field_element.getAttribute("data-gadget-sandbox"),
                editable: (field_element.getAttribute("data-gadget-editable") !== null),
                key: field_element.getAttribute("data-gadget-editable"),
                value: field_element.getAttribute("data-gadget-value"),
                extra: field_element.getAttribute("data-gadget-renderjs-extra") || "{}"
              });
              promise_list.push(gadget.getDeclaredGadget(field_scope));
            }
          }
          gadget.state.field_list = field_list;
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          gadget.state.gadget_list = result_list;
          var iframe,
            sub_element,
            sub_value,
            sub_key,
            render_kw,
            promise_list = [];
          for (i = 0; i < field_list.length; i += 1) {
            if (result_list[i].render !== undefined) {
              sub_value = field_list[i].value;
              sub_key = field_list[i].key;
              try {
                render_kw = JSON.parse(field_list[i].extra);
              } catch (e) {
                console.log(e); /* same remark as below (when render() fails) */
                render_kw = {};
              }
              render_kw.key = sub_key;
              render_kw.value = sub_value;
              render_kw.editable = field_list[i].editable;
              promise_list.push(
                result_list[i].render(render_kw)
                  .push(undefined, displayFieldError)
                    /* XXX Highlight the gadget element with a small colored
                     *       error message. Clicking on the element could unroll
                     *       more information like the traceback. */
              );
            }
          }
          return RSVP.all(promise_list);
        });
    })

    .declareService(function () {
      /*Do not use ajax call but submit an hidden form.
        So in this way, we can use form submit mecanisme
        provided by browser.
        if use ajax, we should get the return page manually
        which is difficult.
        The new hidden fields have been added with the 
        gadget values and the submit button which 
        has been activated (relation field image, save button, etc).
        This is done by listening the "click" event on the 
        submit/image button.
        After all, submit the form manually again.
      */

      var context = this,
        form = this.element.querySelector("form");

      return new RSVP.Queue()
        .push(function () {
          var image_list = context.element
                                  .querySelectorAll("input[type='image']"),
            submit_list = context.element
                                 .querySelectorAll("button[type='submit']"),
            i,
            promise_list = [];

          promise_list.push(promiseEventListener(context.element, "submit",
                                                 false));
          for (i = 0; i < image_list.length; i += 1) {
            promise_list.push(promiseEventListener(image_list[i], "click",
                                                   false));
          }
          for (i = 0; i < submit_list.length; i += 1) {
            promise_list.push(promiseEventListener(submit_list[i], "click",
                                                   false));
          }
          return RSVP.any(promise_list);
        })
        .push(function (evt) {
          var input,
            hidden_button,
            target,
            i,
            promise_list = [];
          if (evt.type === "click") {
            input = document.createElement("input");
            input.setAttribute("type", "hidden");
            target = evt.currentTarget || evt.target;
            input.setAttribute("name", target.getAttribute("name"));
            form.appendChild(input);
          } else {
            hidden_button = context.element.querySelector(".hidden_button");
            hidden_button.setAttribute("type", "hidden");
          }
          for (i = 0; i < context.state.gadget_list.length; i += 1) {
            if (context.state.gadget_list[i].getContent !== undefined &&
                context.state.field_list[i].editable !== null) {
              promise_list.push(getGadgetContent(context.state.gadget_list[i]));
            }
          }
          return RSVP.all(promise_list);
        })
        .push(function (content_list) {
          var input,
            i,
            name;
          for (i = 0; i < content_list.length; i += 1) {
            for (name in content_list[i]) {
              if (content_list[i].hasOwnProperty(name)) {
                input = document.createElement("input");
                input.setAttribute("type", "hidden");
                input.setAttribute("name", name);
                input.setAttribute("value", content_list[i][name]);
                form.appendChild(input);
              }
            }
          }
          return form.submit();
        });
    });

}(window, rJS, RSVP, document, console));