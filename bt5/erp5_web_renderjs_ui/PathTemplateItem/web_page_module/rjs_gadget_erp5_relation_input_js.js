/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS, RSVP, URI, Handlebars,
 SimpleQuery, ComplexQuery, Query, QueryFactory*/
(function (window, rJS, RSVP, URI,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars) {
  "use strict";


  var gadget_klass = rJS(window),

    relation_link_source = gadget_klass.__template_element
                         .getElementById("relation-link-template")
                         .innerHTML,
    relation_link_template = Handlebars.compile(relation_link_source),

    relation_input_source = gadget_klass.__template_element
                         .getElementById("relation-input-template")
                         .innerHTML,
    relation_input_template = Handlebars.compile(relation_input_source),

    relation_listview_source = gadget_klass.__template_element
                         .getElementById("relation-listview-template")
                         .innerHTML,
    relation_listview_template = Handlebars.compile(relation_listview_source);


  function displayNonEditableLink(gadget) {
    return gadget.getUrlFor({
      command: 'index',
      options: {
        jio_key: gadget.state.value_relative_url
      }
    })
      .push(function (href) {
        // XXX Use html5 element gadget
        gadget.element.innerHTML = relation_link_template({
          value: gadget.state.value_text,
          href: href
        });
      });
  }

  function displayNonEditableText(gadget) {
    gadget.element.textContent = gadget.state.value_text;
  }

  function displayEditableLink(gadget, class_name) {
    return gadget.translateHtml(relation_input_template({
      href: "#",
      value: gadget.state.value_text,
      title: gadget.state.title,
      name: gadget.state.key,
      class_name: class_name
    }))
      .push(function (html) {
        gadget.element.innerHTML = html;
      });
  }

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getFormContent", "getFormContent")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    // .declareAcquiredMethod("addRelationInput", "addRelationInput")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var state_dict = {
        editable: options.editable,
        query: options.query,
        catalog_index: options.catalog_index,
        allow_jump: options.allow_jump,
        // required: field_json.required,
        title: options.title,
        key: options.key,
        view: options.view,
        url: options.url,
        allow_creation: options.allow_creation,
        portal_types: options.portal_types,
        translated_portal_types: options.translated_portal_types,
        has_focus: false,
        relation_index: options.relation_index,
        value_relative_url: options.value_relative_url,
        value_uid: options.value_uid,
        value_text: options.value_text,
        value_portal_type: options.value_portal_type
      };

      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        queue = new RSVP.Queue(),
        value_text = gadget.state.value_text,
        // target_url,
        SEARCHING_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext" +
          " ui-input-clear ui-icon-spinner ui-icon-spin",
        JUMP_ON_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-plane ui-shadow-inset ui-btn-inline",
        JUMP_OFF_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-plane ui-shadow-inset ui-btn-inline ui-disabled",
        JUMP_ADD_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-plus ui-shadow-inset ui-btn-inline ui-disabled",
        JUMP_UNKNOWN_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-warning ui-shadow-inset ui-btn-inline ui-disabled";

      // Non editable
      if (!gadget.state.editable) {
        if ((gadget.state.value_relative_url) && (gadget.state.allow_jump)) {
          return displayNonEditableLink(gadget);
        }
        return displayNonEditableText(gadget);
      }

      if (modification_dict.hasOwnProperty('editable')) {
        // First display of the input
        queue.push(function () {
          return displayEditableLink(gadget, JUMP_UNKNOWN_CLASS_STR);
        });
      }

      return queue
        .push(function () {
          var plane = gadget.element.querySelector("a"),
            ul = gadget.element.querySelector(".search_ul"),
            input = gadget.element.querySelector("input");
          ul.innerHTML = "";
          plane.href = '';

          if (input.value !== gadget.state.value_text) {
            input.value = gadget.state.value_text;
          }

          // uid is known
          // User selected a document from a listbox
          if ((gadget.state.value_uid) && (!gadget.state.value_text)) {
            plane.className = SEARCHING_CLASS_STR;
            return gadget.jio_allDocs({
              "query":  Query.objectToSearchText(new SimpleQuery({
                key: "catalog.uid",
                value: gadget.state.value_uid,
                limit: [0, 1]
              })),
              "select_list": [gadget.state.catalog_index]
            })
              .push(function (result) {
                return gadget.changeState({
                  value_text: result.data.rows[0]
                    .value[gadget.state.catalog_index]
                });
              });
          }


          // Expected portal type has been selected.
          // User want to create a new document
          if (gadget.state.value_portal_type) {
            plane.className = JUMP_ADD_CLASS_STR;
            return;
          }

          // Relative URL is known. Display plane icon
          if (gadget.state.value_relative_url) {
            if (gadget.state.allow_jump) {
              return gadget.getUrlFor({
                command: 'index',
                options: {
                  jio_key: gadget.state.value_relative_url
                }
              })
                .push(function (url) {
                  plane.href = url;
                  plane.className = JUMP_ON_CLASS_STR;
                });
            }

            if (modification_dict.hasOwnProperty('value_text')) {
              plane.className = JUMP_UNKNOWN_CLASS_STR;
            } else {
              plane.className = JUMP_OFF_CLASS_STR;
            }
            return;
          }

          // No text, user want to delete the content
          if (!gadget.state.value_text) {
            plane.className = JUMP_OFF_CLASS_STR;
            return;
          }

          // User entered text, but didn't select
          // from the list
          if (!gadget.state.has_focus) {
            plane.className = JUMP_UNKNOWN_CLASS_STR;
            return;
          }

          // User typed some text.
          // Propose some documents in a list
          plane.className = SEARCHING_CLASS_STR;

          return new RSVP.Queue()
            .push(function () {
              // Wait a bit before launching the catalog query
              // as user may still type new characters
              return RSVP.delay(200);
            })
            .push(function () {
              return gadget.jio_allDocs({
                query: Query.objectToSearchText(new ComplexQuery({
                  operator: "AND",
                  query_list: [
                    QueryFactory.create(
                      new URI(gadget.state.query).query(true).query
                    ),
                    new SimpleQuery({
                      key: gadget.state.catalog_index,
                      value: value_text
                    })
                  ]
                })),
                limit: [0, 10],
                select_list: [gadget.state.catalog_index, "uid"]
              });
            })
            .push(function (result) {
              var list = [],
                i,
                type = [];
              if (gadget.state.allow_creation) {
                for (i = 0; i < gadget.state.portal_types.length; i += 1) {
                  type.push({
                    name: gadget.state.translated_portal_types[i],
                    value: gadget.state.portal_types[i]
                  });
                }
              }
              for (i = 0; i < result.data.rows.length; i += 1) {
                list.push({
                  id: result.data.rows[i].id,
                  value: result.data.rows[i].value[gadget.state.catalog_index],
                  uid: result.data.rows[i].value.uid
                });
              }
              plane.className = JUMP_UNKNOWN_CLASS_STR;
              return gadget.translateHtml(relation_listview_template({
                list: list,
                type: type,
                value: value_text
              }));
            })
            .push(function (html) {
              ul.innerHTML = html;
            });
        });

    })


    .declareMethod('getContent', function () {
      var gadget = this,
        result = {};

      if (gadget.state.editable) {
        result = {
          value_relative_url: gadget.state.value_relative_url,
          value_text: gadget.state.value_text,
          value_portal_type: gadget.state.value_portal_type,
          value_uid: gadget.state.value_uid
        };
      }
      return result;
    })


    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (evt) {
      var gadget = this,
        li,
        data_relative_url,
        data_uid,
        data_portal_type,
        data_explore,
        new_state = {};

      if (evt.target.tagName.toLowerCase() === 'li') {
        li = evt.target;
        data_relative_url = li.getAttribute("data-relative-url");
        data_uid = li.getAttribute("data-uid");
        data_portal_type = li.getAttribute("data-create-object");
        data_explore = li.getAttribute("data-explore");

        // User want to create a new document
        if (data_portal_type) {
          new_state.value_portal_type = data_portal_type;
          return gadget.changeState(new_state);
        }

        // User selected an existing document
        if (data_relative_url) {
          new_state.value_text = li.textContent;
          new_state.value_relative_url = data_relative_url;
          new_state.value_uid = data_uid;
          return gadget.changeState(new_state);
        }

        // Go to the search listbox
        if (data_explore) {
          return gadget.getFormContent({
            format: "json"
          })
            .push(function (content) {
              var input = gadget.element.querySelector('input');
              return gadget.redirect({
                command: 'index',
                options: {
                  page: "relation_search",
                  url: gadget.state.url,
                  extended_search: Query.objectToSearchText(
                    new SimpleQuery({
                      key: gadget.state.catalog_index,
                      value: input.value
                    })
                  ),
                  view: gadget.state.view,
                  back_field: gadget.state.key,
                  relation_index: gadget.state.relation_index
                },
                form_content: content
              });
            });
        }
      }
    }, false, false)

    .onEvent('blur', function (evt) {
      if (evt.target === this.element.querySelector(".search_ul")) {
        return this.changeState({
          has_focus: false
        });
      }
    }, true, false)

    .declareMethod('checkValidity', function () {
      return true;
    })

    // XXX Use html5 input
    .onEvent('invalid', function (evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false)

    .onEvent('change', function () {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)


    .onEvent('input', function (event) {
      if (!this.state.editable) {
        return;
      }

      var context = this;

      //XXX temporary hack to remove users from project
      if(event.target.value == ""){
        event.target.value = " ";
      }

      return this.changeState({
        value_text: event.target.value,
        value_relative_url: null,
        value_uid: null,
        value_portal_type: null,
        has_focus: true
      })
        .push(function () {
          return context.notifyChange();
        });
    }, true, false);

}(window, rJS, RSVP, URI,
  SimpleQuery, ComplexQuery, Query, QueryFactory, Handlebars));
