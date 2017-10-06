/*global window, rJS, RSVP, URI, document, Option */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 79 */
(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("notifyChange", "notifyChange")

    .allowPublicAcquisition("redirect", function (param_list) {
      var gadget = this;
      return gadget.redirect({command: 'change', options: {
        view: gadget.hateoas_url +
          "ERP5Document_getHateoas?mode=traverse&relative_url=" +
          encodeURIComponent(param_list[0].options.jio_key) +
          "&view=officejs_support_request_view",
        page: 'list',
        jio_key: param_list[0].options.jio_key
      }
        });
    })
    .allowPublicAcquisition("notifyChange", function (param_list) {
      if (param_list[0]) {
        return this.notifyChange("Please provide a description for this support request.");
      }
      return this.notifyChange(param_list[0]);
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
            editable: true,
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
    })
    .onEvent('change', function (evt) {
      if (evt.target.id === "field_your_project") {
        var gadget = this;

        return gadget.jio_getAttachment(
          'support_request_module',
          gadget.hateoas_url + 'support_request_module'
            + "/SupportRequest_getSupportTypeList"
            + "?project_id=" + evt.target.value + "&json_flag=True"
        ).push(function (sp_list) {
          var i, j,
            sp_select = document.getElementById('field_your_resource');
          for (i = sp_select.options.length - 1; i >= 0; i -= 1) {
            sp_select.remove(i);
          }

          for (j = 0; j < sp_list.length; j += 1) {
            sp_select.options[j] = new Option(sp_list[j][0], sp_list[j][1]);
          }
        });
      }
    }, false, false);
}(window, rJS));