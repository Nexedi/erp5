/*global window, rJS, document */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, document) {
  "use strict";

  // TODO: move this to common utils
  function getFormInfo(form_definition) {
    var child_gadget_url,
      form_type,
      action_category = form_definition.action_type;
    switch (action_category) {
    case 'object_list':
      form_type = 'list';
      child_gadget_url = 'gadget_erp5_pt_form_list.html';
      break;
    case 'object_dialog':
      form_type = 'dialog';
      child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
      break;
    case 'object_jio_js_script':
      form_type = 'dialog';
      child_gadget_url = 'gadget_erp5_pt_form_dialog.html';
      break;
    default:
      form_type = 'page';
      child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
    }
    return [form_type, child_gadget_url];
  }

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        gadget_utils,
        jio_document,
        portal_type,
        front_page;
      return gadget.declareGadget(common_utils_gadget_url)
        .push(function (result) {
          gadget_utils = result;
          return gadget.jio_get(options.jio_key);
        })
        .push(function (result) {
          jio_document = result;
          if (jio_document.portal_type === undefined) {
            throw new Error('Can not display document: ' + options.jio_key);
          }
        }, function (error) {})
        .push(function () {
          return gadget.getSetting('parent_portal_type');
        })
        .push(function (parent_portal_type) {
          if (jio_document) {
            portal_type = jio_document.portal_type;
          } else if (options.portal_type) {
            portal_type = options.portal_type;
          } else {
            portal_type = parent_portal_type;
          }
          front_page = portal_type === parent_portal_type;
          return gadget_utils.getFormDefinition(portal_type, default_view);
        })
        .push(function (form_definition) {
          var form_info = getFormInfo(form_definition),
            form_type = form_info[0],
            child_gadget_url = form_info[1];
          return gadget.changeState({
            jio_key: options.jio_key,
            doc: jio_document,
            portal_type: portal_type,
            child_gadget_url: child_gadget_url,
            form_definition: form_definition,
            form_type: form_type,
            editable: false,
            view: options.view || default_view,
            front_page: front_page
          });
        });
    })

    .onStateChange(function () {
      var fragment = document.createElement('div'),
        gadget = this,
        options;
      while (this.element.firstChild) {
        this.element.removeChild(this.element.firstChild);
      }
      this.element.appendChild(fragment);
      return gadget.declareGadget("gadget_officejs_form_view.html", {element: fragment,
                                                                     scope: 'form_view'})
        .push(function (form_view_gadget) {
          return form_view_gadget.render(gadget.state);
        });
    })

    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (view_gadget) {
          return view_gadget.getDeclaredGadget('fg');
        })
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    });

}(window, rJS, document));