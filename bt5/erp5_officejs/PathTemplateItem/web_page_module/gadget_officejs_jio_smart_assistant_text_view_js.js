/*global window, rJS, RSVP, URL,
  promiseEventListener, document*/
/*jslint indent:2, maxlen: 80, nomen: true */
(function (window, rJS, RSVP, SimpleQuery, ComplexQuery, Query) {
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
    .declareAcquiredMethod("jio_get", "jio_get")


    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        state = {
          title: options.doc.title,
          agent_title: options.doc.agent_title,
          description: options.doc.description,
          validation_state: options.doc.validation_state,
          jio_key: options.jio_key
        };

      gadget.type = options.doc.type;

      return gadget.jio_get(options.jio_key)
        .push(function (content) {
          state.content = content;
          state.text = content.text_content;

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
      var gadget = this,
        title;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (result) {
          title = result.title;

          if (result.text_ === "") {
            result.text_ = " ";
          }
          return gadget.updateDocument({
            'text_content': result.text_,
            title: title
          });
        })
        .push(function () {
          return gadget.notifySubmitted({
            "message": "Data Updated",
            "status": "success"
          });
        });
    })
    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('button[type="submit"]').click();
    }, {mutex: 'render'})

    .onStateChange(function () {
      var gadget = this,
        column_list = [
          ['agent_title', 'Title'],
          ['description', 'Reply'],
          ['modification_date', 'Modification Date'],
          ['validation_state', 'Validation State']
        ],
        jio_key = gadget.state.jio_key,
        portal_type = ["Query"],
        agent_relative_url = jio_key,
        query = "urn:jio:allDocs?query=",
        jio_query_list = [];
      jio_query_list.push(new SimpleQuery({
        key: "portal_type",
        operator: "",
        type: "simple",
        value: portal_type
      }));
      jio_query_list.push(new SimpleQuery({
        key: "agent_relative_url",
        operater: "",
        type: "simple",
        value: agent_relative_url
      }));
      query += Query.objectToSearchText(new ComplexQuery({
          operator: "AND",
          query_list: jio_query_list,
          type: "complex"
        }));

      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {
                "_view": {
                  "my_title": {
                    "description": "",
                    "title": "Title",
                    "default": gadget.state.title,
                    "css_class": "",
                    "required": 1,
                    "editable": 1,
                    "key": "title",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "my_text": {
                    "default": gadget.state.text,
                    "css_class": "",
                    "required": 0,
                    "editable": 1,
                    "key": "text_",
                    "hidden": 0,
                    "renderjs_extra": '{"editor": "fck_editor"}',
                    "type": "GadgetField",
                    "url": "gadget_editor.html",
                    "sandbox": "public"
                  },
                  "my_validation_state": {
                    "description": "",
                    "title": "State",
                    "default": gadget.state.validation_state,
                    "css_class": "",
                    "required": 1,
                    "editable": 0,
                    "key": "validation_state",
                    "hidden": 0,
                    "type": "StringField"
                  },
                  "listbox": {
                    "column_list": column_list,
                    "show_anchor": 0,
                    "default_params": {},
                    "editable": 0,
                    "editable_column_list": [],
                    "key": "field_listbox",
                    "lines": 5,
                    "list_method": "portal_catalog",
                    "query": query,
                    "portal_type": [],
                    "search_column_list": column_list,
                    "sort_column_list": column_list,
                    "sort": [['modification_date', 'descending']],
                    "title": "Related Queries",
                    "type": "ListBox"
                  }
                }
              },
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_title"],
                  ["my_validation_state"]]
              ], [
                "bottom",
                [["listbox"], ["my_text"]]
              ]]
            }
          });
        });
    });
}(window, rJS, RSVP, SimpleQuery, ComplexQuery, Query));