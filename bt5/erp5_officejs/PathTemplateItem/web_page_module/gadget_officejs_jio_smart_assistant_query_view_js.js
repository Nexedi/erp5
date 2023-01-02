/*global window, rJS, RSVP, jIO, Blob*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateDocument", "updateDocument")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_get", "jio_get")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        state = {
          title: options.doc.title,
          text_content: options.doc.text_content,
          owner: options.doc.owner,
          agent_title: options.doc.agent_title,
          validation_state: options.doc.validation_state,
          description: options.doc.description,
          modification_date: options.doc.modification_date,
          relative_url: options.doc.agent_relative_url,
          link: options.doc.link,

          jio_key: options.jio_key
        };

      gadget.type = options.doc.type;

      return gadget.jio_get(options.jio_key)
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'selection_previous'}),
            gadget.getUrlFor({command: 'selection_next'}),
            gadget.changeState(state)
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: "Smart Assistant",
            save_action: true,
            selection_url: url_list[0],
            previous_url: url_list[1],
            next_url: url_list[2]
          });
        });

    }, {mutex: 'render'})

    .onEvent('submit', function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
            return gadget.updateDocument({text_content: result.text_content});
          })
        .push(function () {
          return gadget.notifySubmitted({
            "message": "Data updated",
            "status": "success"
          });
        })
        .push(function () {
          return gadget.redirect({command: 'reload'});
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})

    .onStateChange(function () {
      var gadget = this;

      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_title": {
                    "description": "",
                    "title": "Smart Asisstant Type",
                    "default": gadget.state.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_owner": {
                    "description": "",
                    "title": "From: ",
                    "default": gadget.state.owner,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "owner",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_agent_title": {
                    "relation_item_relative_url":
                      [gadget.state.relative_url],
                    "type": "RelationStringField",
                    "label": true,
                    "sort": [],
                    "relation_item_key":
                       "subfield_field_my_agent_title_item",
                    "description": "",
                    "catalog_index": "title",
                    "editable": 0,
                    "allow_creation": 0,
                    "allow_jump": 1,
                    "key": "agent_title",
                    "translated_portal_types": ["Category"],
                    "title": "Context",
                    "default": [gadget.state.agent_title],
                    "css_class": "",
                    "relation_field_id":
                      "subfield_field_my_agent_title_relation",
                    "required": 1,
                    "url": "agent_title",
                    "hidden": 0,
                    "portal_types": ["Category"],
                    "view": "view"
                  },
                  "your_modification_date": {
                    "description": "",
                    "title": "Modification Date",
                    "default": gadget.state.modification_date,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "modification_date",
                    "hidden": 0,
                    "timezone_style": 1,
                    "date_only": 0,
                    "type": "DateTimeField"
                  },
                  "your_validation_state": {
                    "description": "",
                    "title": "Validation State",
                    "default": gadget.state.validation_state,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "validation_state",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_description": {
                    "description": "",
                    "title": "Reply",
                    "default": gadget.state.description,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "description",
                    "hidden": 0,
                    "type": "TextAreaField"
                  },
                  "my_link": {
                    "editable": 1,
                    "required": 0,
                    "default": {"direct_url": gadget.state.link,
                                "target_type": "display",
                                "textContent": gadget.state.link},
                    "url": "gadget_erp5_page_ojs_link_field.html",
                    "type": "GadgetField",
                    "description": "",
                    "title": "Url",
                    "css_class": "",
                    "key": "link",
                    "hidden": 0,
                    "allow_jump": 1
                  },
                  "my_text_content": {
                    "description": "",
                    "title": "Answer",
                    "default": gadget.state.text_content,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "text_content",
                    "hidden": 0,
                    "type": "TextAreaField"
                  }
                }
              },
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_agent_title"], ["my_title"]]
              ], [
                "right",
                [
                  ["your_validation_state"],
                  ["your_modification_date"],
                  ["my_owner"]
                ]], [
                "center",
                [["my_description"], ["my_link"],
                  ["my_text_content"]]
              ]]
            }
          });
        });
    });
}(window, rJS, RSVP));