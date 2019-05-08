/*global window, document, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP) {
  "use strict";

  //TODO rename this gadget as "front or main" gadget
  //check if this can be done by the controller and use that gadget instead

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("isDesktopMedia", "isDesktopMedia")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        default_view = "jio_view",
        common_utils_gadget_url = "gadget_officejs_common_utils.html",
        child_gadget_url = 'gadget_erp5_pt_form_list.html',
        portal_type,
        //In a future, the post list will be within a thread. For now:
        fake_thread_uid = "thread-" + ("0000" + ((Math.random() * Math.pow(36, 4)) | 0).toString(36)).slice(-4);
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('parent_portal_type'),
            gadget.declareGadget("gadget_officejs_common_utils.html")
          ]);
        })
        .push(function (result) {
            portal_type = result[0];
            return result[1].getFormDefinition(result[0], default_view, {source_reference: fake_thread_uid});
          })
          .push(function (form_definition) {
            return gadget.changeState({
              jio_key: options.jio_key,
              portal_type: portal_type,
              //TODO child_gadget_url should be decided in utils.getFormDefinition based on form type
              child_gadget_url: child_gadget_url,
              form_definition: form_definition,
              form_type: 'list',
              editable: false,
              view: default_view,
              front_page: true
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

}(window, document, rJS, RSVP));