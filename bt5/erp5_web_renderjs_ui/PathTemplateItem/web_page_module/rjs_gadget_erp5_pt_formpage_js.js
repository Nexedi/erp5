/*global window, rJS, URI */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, URI) {
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
    // declared methods
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
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_getAttachment(options.jio_key, options.view)
        .push(function (result) {
          var uri;
          if (!result._embedded) {
            return gadget.jio_getAttachment(options.jio_key, "links")
              .push(function (result2) {
                return gadget.redirect({command: 'change', options: {
                  view: result2._links.view[0].href,
                  page: undefined
                }});
              });
          }

          uri = new URI(result._embedded._view._links.form_definition.href);
          return gadget.jio_getAttachment(uri.segment(2), "view")
            .push(function (erp5_form) {
              var url = "gadget_erp5_pt_" + erp5_form.pt;
              // XXX Hardcoded specific behaviour for form_view
              if ((options.editable !== undefined) && (erp5_form.pt === "form_view")) {
                url += "_editable";
              }
              url += ".html";

              return gadget.changeState({
                jio_key: options.jio_key,
                options: options,
                view: options.view,
                url: url,
                erp5_document: JSON.stringify(result),
                erp5_form: JSON.stringify(erp5_form)
              });
            });
        });
    })
    .onStateChange(function (modification_dict) {
      var queue,
        gadget = this,
        options = this.state.options,
        page_template_gadget,
        clean_dom = modification_dict.hasOwnProperty('url');
      if (clean_dom) {
        queue = gadget.declareGadget(gadget.state.url, {scope: "fg"});
      } else {
        queue = gadget.getDeclaredGadget("fg");
      }
      return queue
        .push(function (result) {
          page_template_gadget = result;

          var sub_options = options.fg || {},
            erp5_document = JSON.parse(gadget.state.erp5_document),
            erp5_form = JSON.parse(gadget.state.erp5_form);

          loadFormContent(gadget, erp5_document._embedded._view);

          sub_options.erp5_document = erp5_document;
          sub_options.form_definition = erp5_form;
          sub_options.view = options.view;
          sub_options.action_view = options.action_view;
          sub_options.jio_key = options.jio_key;
          sub_options.editable = options.editable;

          return page_template_gadget.render(sub_options);

        })
        .push(function () {
          if (clean_dom) {
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
              erp5_document: JSON.parse(gadget.state.erp5_document),
              editable: gadget.state.options.editable
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
    });

}(window, rJS, URI));