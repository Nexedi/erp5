/*global window, rJS, URI, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, URI, RSVP) {
  "use strict";

  function loadFormContent(gadget, result) {
    var key;
    if (gadget.state.options.form_content) {
      for (key in result) {
        if (result.hasOwnProperty(key)) {
          if (gadget.state.options.form_content[result[key].key]) {
            result[key].default = gadget.state.options.form_content[result[key].key];
          }
        }
      }
    }
  }


  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("updatePanel", "updatePanel")

    /////////////////////////////////////////////////////////////////
    // Proxy methods to the child gadget
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })
    .declareMethod('checkValidity', function () {
      return this.getDeclaredGadget('fg')
        .push(function (declared_gadget) {
          return declared_gadget.checkValidity();
        });
    })
    .declareMethod('getContent', function () {
      return this.getDeclaredGadget('fg')
        .push(function (declared_gadget) {
          return declared_gadget.getContent();
        });
    })

    /////////////////////////////////////////////////////////////////
    // Own methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      var gadget = this;
      return gadget.jio_allDocs(param_list[0])
        .push(function (result) {
          var i;
          if (result.data.rows.length) {
            for (i = 0; i < result.data.rows.length; i += 1) {
              loadFormContent(gadget, result.data.rows[i].value);
            }
          }
          return result;
        });
    })
    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })
    /**
     * Render obtain ERP5 Document and assigned Form Definition.
     * 
     * Arguments:
     * `erp5_document` or parameters to obtain one: `jio_key`, `view`
     * `editable`
     */
    .declareMethod("render", function (options) {
      var gadget = this,
        promise_queue = new RSVP.Queue(),
        new_state = {
          options: options,
          erp5_document: undefined,
          erp5_form: undefined,
          url: undefined
        };

      if (options.hasOwnProperty('erp5_document')) {
        // if we get erp5 document during rendering then no need to fetch it
        new_state.erp5_document = options.erp5_document;
        // remove reference to erp5_document from options (and new_state.options)
        // otherwise we get infinite loop
        delete options.erp5_document;
      } else {
        promise_queue
          .push(function () {
            return gadget.jio_getAttachment(options.jio_key, options.view);
          })
          .push(function (result) {
            new_state.erp5_document = result;

            if (!result._embedded) {
              return gadget.jio_getAttachment(options.jio_key, "links")
                .push(function (result2) {
                  return gadget.redirect({command: 'change', options: {
                    view: result2._links.view[0].href,
                    page: undefined
                  }});
                });
            }
          });
      }

      // options.editable differs when it comes from the erp5_launcher of FormBox - try to unify it here
      if (options.editable === "true" || options.editable === true || options.editable === "1" || options.editable === 1) {
        options.editable = 1;
      } else {
        options.editable = 0;
      }

      return promise_queue
        .push(function () {
          var uri = new URI(new_state.erp5_document._embedded._view._links.form_definition.href);
          return gadget.jio_getAttachment(uri.segment(2), "view");
        })
        .push(function (erp5_form) {
          var url = "gadget_erp5_pt_" + erp5_form.pt;
          // XXX Hardcoded specific behaviour for form_view
          if ((options.editable === 1) && (erp5_form.pt === "form_view")) {
            url += "_editable";
          }
          url += ".html";

          new_state.url = url;
          new_state.erp5_form = JSON.stringify(erp5_form);

          new_state.erp5_document = JSON.stringify(new_state.erp5_document);
          return gadget.changeState(new_state);
        });
    })

    .onStateChange(function (modification_dict) {
      var queue,
        gadget = this,
        options = this.state.options,
        page_template_gadget,
        erp5_document = JSON.parse(gadget.state.erp5_document),
        erp5_form = JSON.parse(gadget.state.erp5_form);

      if (modification_dict.hasOwnProperty('url')) {
        queue = gadget.declareGadget(gadget.state.url, {scope: "fg"});
      } else {
        queue = gadget.getDeclaredGadget("fg");
      }
      return queue
        .push(function (result) {
          page_template_gadget = result;

          var sub_options = options.fg || {};

          loadFormContent(gadget, erp5_document._embedded._view);

          sub_options.erp5_document = erp5_document;
          sub_options.form_definition = erp5_form;
          sub_options.view = options.view;
          sub_options.action_view = options.action_view;
          sub_options.jio_key = options.jio_key; // jIO identifier of currently rendered ERP5 document
          sub_options.editable = options.editable; // form decides on editability of its fields

          return page_template_gadget.render(sub_options);
        })
        .push(function () {
          if (modification_dict.hasOwnProperty('url')) {
            return page_template_gadget.getElement()
              .push(function (fragment) {
                var element = gadget.element;
                // Clear first to DOM, append after to reduce flickering/manip
                while (element.firstChild) {
                  element.removeChild(element.firstChild);
                }
                element.appendChild(fragment);
              });
          }
        })
        .push(function () {
          var jio_key = gadget.state.options.jio_key;
          /*jslint regexp: true*/
          if (/^[^\/]+_module\/.+$/.test(jio_key)) {
            /*jslint regexp: false*/
            return gadget.updatePanel({
              erp5_document: erp5_document,
              editable: gadget.state.options.editable,
              view: options.view
            });
          }
        });
    })
    .allowPublicAcquisition("displayFormulatorValidationError", function (param_list) {
      var erp5_document = JSON.parse(this.state.erp5_document);
      erp5_document._embedded._view = param_list[0];
      // Force refresh
      erp5_document._now = Date.now();

      return this.changeState({erp5_document: JSON.stringify(erp5_document)});
    })
    /** Re-render whole form page with completely new form. */
    .allowPublicAcquisition("updateForm", function (args, subgadget_id) {
      var erp5_document = JSON.parse(this.state.erp5_document),
        options = this.state.options;
      erp5_document._embedded._view = args[0];
      erp5_document._now = Date.now();  // force refresh
      // We choose render instead of changeState because the new form can use
      // different page_template (reports are setup in form_dialog but rendered
      // in report_view).
      // Validation provides document updated for error texts but uses the same
      // form thus the same view thus the same url - no DOM modifications
      //
      // We modify inplace state.options because render method uses and removes
      // erp5_document hidden in its options.
      options.erp5_document = erp5_document;
      return this.render(options);
    });

}(window, rJS, URI, RSVP));