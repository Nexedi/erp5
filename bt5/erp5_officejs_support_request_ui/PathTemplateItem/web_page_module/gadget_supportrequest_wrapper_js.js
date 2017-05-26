/*global window, rJS, RSVP, URI */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 79 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .allowPublicAcquisition("redirect", function (param_list) {
      var gadget = this;
      return gadget.redirect({command: 'change', options: {
        view: gadget.hateoas_url +
          "ERP5Document_getHateoas?mode=traverse&relative_url=" +
          encodeURIComponent(param_list[0].options.jio_key) +
          "&view=fast_view",
        page: 'form',
        jio_key: param_list[0].options.jio_key
      }
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this,
        view;
      gadget.options = options;
      return gadget.getUrlParameter('view')
        .push(function (result) {
          view = result;
          return gadget.getDeclaredGadget('erp5_form');
        })
        .push(function (form) {
          gadget.form = form;
          return form.render({
            view: view,
            jio_key: options.jio_key
          });
        })
        .push(function () {
          return gadget.getSetting('hateoas_url');
        })
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        });
    })
    .declareMethod('triggerSubmit', function () {
      return this.form.triggerSubmit();
    });
}(window, rJS));