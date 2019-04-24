/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_utils;

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (gadget) {
      return gadget_utils.renderGadget(gadget);
    })

    .declareMethod("handleRender", function (gadget, options, action_reference, form_definition) {
      return gadget.declareGadget("gadget_officejs_form_view.html")
      .push(function (declared_gadget) {
        gadget_utils = declared_gadget;
        var child_gadget_url = 'gadget_erp5_pt_form_view_editable.html';
        return gadget.jio_get(options.jio_key)
        .push(function (parent_document) {
          var title = parent_document.title;
          if (!title.startsWith('Re: ')) { title = 'Re: ' + parent_document.title; }
          return gadget.changeState({
            doc: {title: title},
            parent_document: parent_document,
            child_gadget_url: child_gadget_url,
            form_definition: form_definition,
            view: action_reference,
            editable: true,
            has_more_views: false,
            has_more_actions: false,
            is_form_list: false
          });
        });
      });
    })

    .declareMethod("handleSubmit", function (gadget, jio_key, content_dict) {
      var document = {
        my_title: gadget.state.doc.title,
        portal_type: gadget.state.parent_document.portal_type,
        parent_relative_url: gadget.state.parent_document.parent_relative_url,
        my_source_reference: gadget.state.parent_document.source_reference
      }, property;
      for (property in content_dict) {
        if (content_dict.hasOwnProperty(property)) {
          document['my_' + property] = content_dict[property];
        }
      }
      return gadget_utils.createDocument(document)
      .push(function (id) {
        jio_key = id;
        return gadget.notifySubmitting();
      })
      .push(function () {
        return gadget.notifySubmitted({message: 'Data Updated', status: 'success'});
      })
      .push(function () {
        return gadget.redirect({
          command: 'display',
          options: {
            jio_key: jio_key,
            editable: true
          }
        });
      });
    });

}(window, rJS, RSVP));