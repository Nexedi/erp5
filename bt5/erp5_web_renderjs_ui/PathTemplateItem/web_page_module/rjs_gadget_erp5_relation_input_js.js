/*jslint indent: 2, maxerr: 3, nomen: true, maxlen: 80 */
/*global window, rJS, RSVP, URI,
 SimpleQuery, ComplexQuery, Query, QueryFactory, document*/
(function (window, rJS, RSVP, URI, document,
  SimpleQuery, ComplexQuery, Query, QueryFactory) {
  "use strict";

  function displayNonEditableLink(gadget) {
    return gadget.getUrlFor({
      command: 'index',
      options: {
        jio_key: gadget.state.value_relative_url
      }
    })
      .push(function (href) {
// <div>
//   <a href={{href}}>{{value}}</a>
// </div>
        // XXX Use html5 element gadget
        var div_element = document.createElement('div'),
          a_element = document.createElement('a');
        a_element.textContent = gadget.state.value_text;
        a_element.href = href;

        while (gadget.element.firstChild) {
          gadget.element.removeChild(gadget.element.firstChild);
        }
        div_element.appendChild(a_element);
        gadget.element.appendChild(a_element);
      });
  }

  function displayNonEditableText(gadget) {
    gadget.element.textContent = gadget.state.value_text;
  }

  function buildEditableInputHTML(gadget) {
// <div class="relation-input ui-input-text">
//   <div>
//     <input type='search' title="{{title}}" name="{{name}}"
//            id="{{name}}" autocomplete="off" value="{{value}}" >
//     <ul class="search_ul"></ul>
//   </div>
// </div>
    var div_element = document.createElement('div'),
      sub_div_element = document.createElement('div'),
      input_element = document.createElement('input'),
      ul_element = document.createElement('ul');
    div_element.setAttribute('class', 'relation-input ui-input-text');
    input_element.setAttribute('type', 'search');
    input_element.setAttribute('title', gadget.state.title);
    input_element.setAttribute('name', gadget.state.key);
    input_element.setAttribute('id', gadget.state.key);
    input_element.setAttribute('autocomplete', 'off');
    input_element.setAttribute('value', gadget.state.value_text);
    ul_element.setAttribute('class', 'search_ul');

    while (gadget.element.firstChild) {
      gadget.element.removeChild(gadget.element.firstChild);
    }
    div_element.appendChild(sub_div_element);
    sub_div_element.appendChild(input_element);
    sub_div_element.appendChild(ul_element);
    gadget.element.appendChild(div_element);
  }

  function createEditableLink(gadget, class_name) {
    // Add an airplane link
    var a = document.createElement('a'),
      div = gadget.element.querySelector('input').parentElement;
    a.setAttribute('tabindex', -1);
    a.setAttribute('class', class_name);
    a.textContent = 'Jump to this document';
    if (div.nextElementSibling !== null) {
      div.parentElement.removeChild(div.nextElementSibling);
    }
    div.parentElement.appendChild(a);
  }

  function createEditableButton(gadget, class_name) {
    // Add a search button
    var button = document.createElement('button'),
      div = gadget.element.querySelector('input').parentElement;
    button.setAttribute('tabindex', -1);
    button.setAttribute('class', class_name);
    button.setAttribute('type', 'button');
    if (div.nextElementSibling !== null) {
      div.parentElement.removeChild(div.nextElementSibling);
    }
    div.parentElement.appendChild(button);
  }

  function redirectToTheSearchListbox(gadget) {
    return gadget.getFormContent({
      format: "json"
    })
      .push(function (content) {
        var input = gadget.element.querySelector('input'),
          extended_search = "";
        if (input.value) {
          extended_search = Query.objectToSearchText(
            new SimpleQuery({
              key: gadget.state.catalog_index,
              value: input.value
            })
          );
        }
        return gadget.redirect({
          command: 'index',
          options: {
            page: "relation_search",
            url: gadget.state.url,
            view: gadget.state.search_view,
            extended_search: extended_search,
            back_field: gadget.state.key,
            relation_index: gadget.state.relation_index
          },
          form_content: content
        });
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getFormContent", "getFormContent")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("translate", "translate")
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
        search_view: options.search_view,
        url: options.url,
        allow_creation: options.allow_creation,
        portal_types: JSON.stringify(options.portal_types),
        translated_portal_types:
          JSON.stringify(options.translated_portal_types),
        has_focus: false,
        relation_index: options.relation_index,
        value_relative_url: options.value_relative_url,
        value_uid: options.value_uid,
        value_text: options.value_text,
        value_portal_type: options.value_portal_type
      },
        sort_list = JSON.parse(options.sort_list_json);
      sort_list.map(function (sort) {
        var order = sort[1].toLowerCase();
        if (order.startsWith('asc')) {
          sort[1] = 'ascending';
        } else if (order.startsWith('desc')) {
          sort[1] = 'descending';
        }
      });
      state_dict.sort_list_json = JSON.stringify(sort_list);

      return this.changeState(state_dict);
    })

    .declareJob('detachChangeState', function (value_uid, catalog_index) {
      var gadget = this;
      return gadget.jio_allDocs({
        "query":  Query.objectToSearchText(new SimpleQuery({
          key: "catalog.uid",
          value: value_uid
        })),
        "limit": [0, 1],
        "select_list": [catalog_index]
      })
        .push(function (result) {
          if (!result.data.total_rows) {
            // Uid was not found.
            // Do not change the display
            return;
          }
          return gadget.changeState({
            value_text: result.data.rows[0]
                              .value[catalog_index]
          });
        })
        .push(function () {
          return gadget.notifyChange();
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        input = null,
        value_text = gadget.state.value_text,
        // target_url,
        SEARCHING_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext" +
          " ui-input-clear ui-icon-spinner ui-icon-spin",
        JUMP_ON_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-plane ui-shadow-inset ui-btn-inline",
        JUMP_OFF_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-plane ui-shadow-inset ui-btn-inline ui-disabled",
        SEARCH_CLASS_STR = "ui-btn ui-corner-all ui-btn-icon-notext " +
          "ui-icon-search ui-shadow-inset ui-btn-inline",
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
        buildEditableInputHTML(gadget);
      }

      input = gadget.element.querySelector("input");
      if (modification_dict.hasOwnProperty("value_text")) {
        input.value = gadget.state.value_text;
      }

      gadget.element.querySelector(".search_ul").innerHTML = "";
      // Display the airplane link or the search button
      if ((gadget.state.value_relative_url) || (gadget.state.value_text)) {
        createEditableLink(gadget, JUMP_UNKNOWN_CLASS_STR);
      } else {
        return createEditableButton(gadget, SEARCH_CLASS_STR);
      }

      // Check if the airplane link has to be updated
      return RSVP.Queue()
        .push(function () {
          var plane = gadget.element.querySelector("a"),
            ul = gadget.element.querySelector(".search_ul");
          plane.href = '';

          // uid is known
          // User selected a document from a listbox
          if ((gadget.state.value_uid) && (!gadget.state.value_text)) {
            plane.className = SEARCHING_CLASS_STR;
            return gadget.detachChangeState(gadget.state.value_uid,
                                            gadget.state.catalog_index);
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
              return new RSVP.Queue(RSVP.all([

                gadget.jio_allDocs({
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
                  select_list: [gadget.state.catalog_index, "uid"],
                  sort_on: JSON.parse(gadget.state.sort_list_json)
                }),

                gadget.getTranslationList([
                  'Create New',
                  'Explore the Search Result List'
                ])

              ]))
                .push(function (result_list) {
                  var i,
                    row,
                    portal_type_list,
                    translated_portal_type_list,
                    fragment_element = document.createDocumentFragment(),
                    li_element;

                  plane.className = JUMP_UNKNOWN_CLASS_STR;

                  // Documents
// <li class="ui-icon-sign-in ui-btn-icon-right" data-relative-url="{{id}}"
//     data-uid="{{uid}}">{{value}}</li>
                  for (i = 0; i < result_list[0].data.rows.length; i += 1) {
                    row = result_list[0].data.rows[i];
                    li_element = document.createElement('li');
                    li_element.setAttribute('class',
                      'ui-icon-sign-in ui-btn-icon-right');
                    li_element.setAttribute('data-relative-url', row.id);
                    li_element.setAttribute('data-uid', row.value.uid);
                    li_element.textContent =
                      row.value[gadget.state.catalog_index];
                    fragment_element.appendChild(li_element);
                  }

                  // New documents
//  <li class="ui-icon-plus ui-btn-icon-right" data-i18n="Create New"
//      data-create-object="{{value}}" name="{{name}}">Create New
//    <span> {{name}}: {{../value}}</span></li>
                  if (gadget.state.allow_creation) {
                    portal_type_list =
                      JSON.parse(gadget.state.portal_types);
                    translated_portal_type_list =
                      JSON.parse(gadget.state.translated_portal_types);
                    for (i = 0; i < portal_type_list.length; i += 1) {
                      li_element = document.createElement('li');
                      li_element.setAttribute('class',
                        'ui-icon-plus ui-btn-icon-right');
                      li_element.setAttribute('data-create-object',
                                              portal_type_list[i]);
                      li_element.setAttribute('name',
                        translated_portal_type_list[i]);
                      li_element.textContent =
                        result_list[1][0] + ' ' +
                        translated_portal_type_list[i] +
                        ': ' + value_text;
                      fragment_element.appendChild(li_element);
                    }
                  }

                  // Explore
// <li class="ui-icon-search ui-btn-icon-right" data-explore=true
//     data-i18n="Explore the Search Result List" ></li>
                  li_element = document.createElement('li');
                  li_element.setAttribute('class',
                    'ui-icon-search ui-btn-icon-right');
                  li_element.setAttribute('data-explore',
                                          true);
                  li_element.textContent = result_list[1][1];
                  fragment_element.appendChild(li_element);

                  while (ul.firstChild) {
                    ul.removeChild(ul.firstChild);
                  }
                  ul.appendChild(fragment_element);
                });
            }, function (error) {
              if (error instanceof Error &&
                  error.hash &&
                  error.hash.expected &&
                  error.hash.expected.length === 1 &&
                  error.hash.expected[0] === "'QUOTE'") {
                return gadget.getTranslationList([
                  "Invalid search criteria"
                ])
                  .push(function (translation_list) {
                    return gadget.notifyInvalid(translation_list[0]);
                  });
              }
              throw error;
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
    }, {mutex: 'changestate'})


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
        new_state = {},
        tag_name = evt.target.tagName.toLowerCase();

      if (tag_name === 'button') {
        // Go to the search listbox
        return redirectToTheSearchListbox(gadget);
      }

      if (tag_name === 'li' || tag_name === 'span') {
        if (tag_name === 'li') {
          li = evt.target;
        } else {
          li = evt.target.parentElement;
        }
        data_relative_url = li.getAttribute("data-relative-url");
        data_uid = li.getAttribute("data-uid");
        data_portal_type = li.getAttribute("data-create-object");
        data_explore = li.getAttribute("data-explore");

        // User want to create a new document
        if (data_portal_type) {
          new_state.value_portal_type = data_portal_type;
          new_state.has_focus = false;
          return gadget.changeState(new_state);
        }

        // User selected an existing document
        if (data_relative_url) {
          new_state.value_text = li.textContent;
          new_state.value_relative_url = data_relative_url;
          new_state.value_uid = data_uid;
          new_state.has_focus = false;
          return gadget.changeState(new_state);
        }

        // Go to the search listbox
        if (data_explore) {
          return redirectToTheSearchListbox(gadget);
        }
      }
    }, false, false)

    .onEvent('blur', function (evt) {
      var gadget = this;
      if (evt.target.tagName.toLowerCase() === 'input') {
        return new RSVP.Queue()
          .push(function () {
            // Wait a bit to handle click :/
            return RSVP.delay(200);
          })
          .push(function () {
            return gadget.changeState({
              has_focus: false
            });
          });
      }
    }, true, false)

    .onEvent('focus', function (evt) {
      var gadget = this;
      if (evt.target.tagName.toLowerCase() === 'input') {
        return gadget.changeState({
          has_focus: true
        });
      }
    }, true, false)

    .declareMethod('checkValidity', function () {
      var gadget = this;

      if ((this.state.value_text) && (
          (this.state.value_relative_url === null) &&
            (this.state.value_uid === null) &&
            (this.state.value_portal_type === null)
        )) {
        return gadget.translate("No such document was found")
          .push(function (error_message) {
            return gadget.notifyInvalid(error_message);
          })
          .push(function () {
            return false;
          });
      }
      return true;
    }, {mutex: 'changestate'})

    // XXX Use html5 input
    .onEvent('invalid', function (evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false)

    .onEvent('change', function () {
      return this.notifyChange();
    }, false, false)


    .onEvent('input', function (event) {
      if (!this.state.editable) {
        return;
      }

      var context = this;
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

}(window, rJS, RSVP, URI, document,
  SimpleQuery, ComplexQuery, Query, QueryFactory));
