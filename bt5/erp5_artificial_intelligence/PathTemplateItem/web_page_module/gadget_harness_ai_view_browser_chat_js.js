/*global window, rJS, RSVP, calculatePageTitle, FormData, URI, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, calculatePageTitle) {
  "use strict";

  var CHECK_TASK_RESPONSE_POLL_INTERVAL = 3000;

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

    .allowPublicAcquisition('getCommentPostList', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0];
      return gadget.jio_getAttachment(
        document_id,
        gadget.hateoas_url + document_id + "/ArtificialTask_getCommentPostListAsJson"
      );
    })
    .allowPublicAcquisition('postComment', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        form_data_json = argument_list[1];
      return gadget.jio_putAttachment(
        document_id,
        gadget.hateoas_url + document_id + "/ArtificialTask_createCommentLine",
        form_data_json
      );
    })
    .allowPublicAcquisition('requestProcessTask', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        body = argument_list[1];

      function checkTaskResponse(active_process_relative_url) {
        return gadget.jio_getAttachment(
          document_id,
          gadget.hateoas_url + document_id + "/ArtificialTask_checkTaskResponse?response_id=" +
            encodeURIComponent(active_process_relative_url)
        )
          .push(function (result) {
            if (result.status !== 'done') {
              return new RSVP.Queue(RSVP.delay(CHECK_TASK_RESPONSE_POLL_INTERVAL))
                .push(function () {
                  return checkTaskResponse(active_process_relative_url);
                });
            }
            return result;
          });
      }

      return gadget.jio_putAttachment(
        document_id,
        gadget.hateoas_url + document_id + "/ArtificialTask_processingTask",
        body
      )
        .push(function (evt) {
          return jIO.util.readBlobAsText(evt.target.response);
        })
        .push(function (text_evt) {
          return checkTaskResponse(text_evt.target.result);
        });
    })
    .allowPublicAcquisition('storeTaskResult', function (argument_list) {
      var gadget = this,
        document_id = argument_list[0],
        body = argument_list[1];
      return gadget.jio_putAttachment(
        document_id,
        gadget.hateoas_url + document_id + "/ArtificialTask_storeTaskResult",
        body
      );
    })

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
            'jio_key': gadget.options.jio_key,
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