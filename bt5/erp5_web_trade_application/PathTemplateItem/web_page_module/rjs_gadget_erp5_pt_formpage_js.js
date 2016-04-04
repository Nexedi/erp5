/*global window, rJS, URI, jQuery */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, URI, $) {
  "use strict";

  var gadget_klass = rJS(window);
  // DEFAULT_VIEW_REFERENCE = "view";

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('triggerSubmit', function () {
      return this.getDeclaredGadget('fg')
        .push(function (g) {
          return g.triggerSubmit();
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this,
        element = gadget.props.element,
        erp5_document,
        erp5_form,
        queue,
        form_gadget;

      gadget.props.jio_key = options.jio_key;
      gadget.props.options = options;

      queue = gadget.jio_getAttachment(options.jio_key, options.view);
      queue
        .push(function (result) {
          var uri;
          if (!result._embedded) {
            return gadget.jio_getAttachment(options.jio_key, "links")
              .push(function (result) {
                return gadget.redirect({command: 'change', options: {
                  view: result._links.view[0].href,
                  editable: undefined,
                  page: undefined
                }});
              });
          }
          if (options.hasOwnProperty("form_validation_error")) {
            result._embedded._view = options.form_validation_error;
          }
          uri = new URI(result._embedded._view._links.form_definition.href);
          erp5_document = result;
          queue
            .push(function () {
              return gadget.jio_getAttachment(uri.segment(2), "view");
            })
            .push(function (result) {
              erp5_form = result;

              var url = "gadget_erp5_pt_" + erp5_form.pt;
              // XXX Hardcoded specific behaviour for form_view
              if ((options.editable !== undefined) && (erp5_form.pt === "form_view")) {
                url += "_editable";
              }
              url += ".html";

              return gadget.declareGadget(url, {
                scope: "fg"
              });
            })
            .push(function (result) {
              var sub_options = options.fg || {};
              sub_options.erp5_document = erp5_document;
              sub_options.form_definition = erp5_form;
              sub_options.view = options.view;
              sub_options.action_view = options.action_view;
              sub_options.jio_key = options.jio_key;
              sub_options.editable = options.editable;

              form_gadget = result;
              return form_gadget.render(sub_options);
            })
            .push(function () {
              return form_gadget.getElement();
            })
            .push(function (fragment) {
              // Clear first to DOM, append after to reduce flickering/manip
              while (element.firstChild) {
                element.removeChild(element.firstChild);
              }
              element.appendChild(fragment);
              if (options.hasOwnProperty("form_validation_error")) {
                $(element).trigger("create");
              }
            });
        });
      return queue;
    })

    .allowPublicAcquisition("displayFormulatorValidationError", function (param_list) {
      var options = this.props.options;
      options.form_validation_error = param_list[0];
      return this.render(options);
    });

}(window, rJS, URI, jQuery));