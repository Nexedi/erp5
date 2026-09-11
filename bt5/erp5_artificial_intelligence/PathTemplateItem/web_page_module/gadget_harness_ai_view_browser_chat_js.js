/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")

    .declareMethod('render', function (options) {
      var gadget = this;
      gadget.options = options;
      return gadget.getSetting('hateoas_url')
        .push(function (hateoas_url) {
          gadget.hateoas_url = hateoas_url;
        })
        .push(function () {
          var state_dict = {
            id: options.jio_key,
            view: options.view,
            editable: options.editable,
            erp5_document: options.erp5_document,
            form_definition: options.form_definition,
            erp5_form: options.erp5_form || {}
          };
          return gadget.changeState(state_dict);
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.getDeclaredGadget("gadget_chat")
        .push(function (chat_gadget) {
          var rendered_form = gadget.state.erp5_document._embedded._view;
          return chat_gadget.render({
            'chat_state': rendered_form.my_simulation_state['default'],
            'hateoas_url': gadget.hateoas_url,
            'request_options': {
              'document_id': gadget.options.jio_key,
              // Builders, not resolved URLs: gadget_chat_agent_harness_js calls each
              // one with the document_id to get the actual URL to use.
              'post_url': function (document_id) {
                return gadget.hateoas_url + document_id + "/ArtificialTask_createCommentLine";
              },
              'get_url': function (document_id) {
                return gadget.hateoas_url + document_id + "/ArtificialTask_getCommentPostListAsJson";
              },
              'process_url': function (document_id) {
                return gadget.hateoas_url + document_id + "/ArtificialTask_processingTask";
              }
            },
            'editor_options' : {
              editor: 'gadget_editor.html',
              options: {
                value: "",
                key: "comment",
                portal_type: "Artificial Task Line",
                editable: true,
                editor: 'codemirror',
                maximize: true
              }
            }
          });

        })

        // render the header
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.getUrlFor({command: 'change', options: {page: "tab"}}),
            calculatePageTitle(gadget, gadget.state.erp5_document)
          ]);
        })
        .push(function (all_result) {
          return gadget.updateHeader({
            selection_url: all_result[0],
            previous_url: all_result[1],
            next_url: all_result[2],
            tab_url: all_result[3],
            page_title: all_result[4]
          });
        });
    });
}(window, rJS, RSVP, calculatePageTitle));