/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, asBoolean , ensureArray, SimpleQuery, ComplexQuery, Query*/
(function (window, document, rJS, RSVP, Node, asBoolean, ensureArray, SimpleQuery, ComplexQuery, Query) {
  "use strict";

  function appendDt(fragment, dt_title, dt_icon,
                    action_list, href_list, index) {
// <dt class="ui-btn-icon-left ui-icon-eye">Views</dt>
// {{#each view_list}}
// <dd class="document-listview">
//   <a class="{{class_name}}" href="{{href}}">{{title}}</a>
// </dd>
// {{/each}}
    var dt_element = document.createElement('dt'),
      dd_element,
      a_element,
      i;
    dt_element.textContent = dt_title;
    dt_element.setAttribute('class', 'ui-btn-icon-left ui-icon-' + dt_icon);
    fragment.appendChild(dt_element);
    for (i = 0; i < action_list.length; i += 1) {
      dd_element = document.createElement('dd');
      dd_element.setAttribute('class', 'document-listview');
      a_element = document.createElement('a');
      a_element.setAttribute('class', action_list[i].class_name);
      a_element.href = href_list[index + i];
      a_element.textContent = action_list[i].title;
      dd_element.appendChild(a_element);
      fragment.appendChild(dd_element);
    }
  }

  function getUrlParameterDict(jio_key, view, sort_list, column_list, extended_search) {
    return {
      command: 'push_history',
      options: {
        'jio_key': jio_key,
        'page': 'form',
        'view': view,
        'field_listbox_sort_list:json': sort_list,
        'field_listbox_column_list:json': column_list,
        'extended_search': extended_search
      }
    };
  }

  function createProjectQuery(project_jio_key, key_value_list) {
    var i, query_list = [], id_query_list = [], id_complex_query;
    if (project_jio_key) {
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key
      }));
      id_query_list.push(new SimpleQuery({
        key: "source_project__relative_url",
        operator: "",
        type: "simple",
        value: project_jio_key + "/%%"
      }));
      id_complex_query = new ComplexQuery({
        operator: "OR",
        query_list: id_query_list,
        type: "complex"
      });
      query_list.push(id_complex_query);
    }
    for (i = 0; i < key_value_list.length; i += 1) {
      query_list.push(new SimpleQuery({
        key: key_value_list[i][0],
        operator: "",
        type: "simple",
        value: key_value_list[i][1]
      }));
    }
    return Query.objectToSearchText(new ComplexQuery({
      operator: "AND",
      query_list: query_list,
      type: "complex"
    }));
  }

  rJS(window)
    .setState({
      visible: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function toggle() {
      return this.changeState({
        visible: !this.state.visible
      });
    })
    .declareMethod('close', function close() {
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('render', function render(options) {
      var erp5_document = options.erp5_document,
        jio_key = options.jio_key,
        view = options.view,
        visible = options.visible,
        display_workflow_list,
        context = this,
        workflow_list,
        view_list,
        action_list,
        i;

      if (visible === undefined) {
        visible = context.state.visible;
      }

      if (options.display_workflow_list === undefined) {
        display_workflow_list = true;
      } else {
        display_workflow_list = asBoolean(options.display_workflow_list);
      }

      if ((erp5_document !== undefined) && (jio_key !== undefined)) {
        workflow_list = ensureArray(erp5_document._links.action_workflow);
        view_list = ensureArray(erp5_document._links.action_object_view);
        action_list = ensureArray(erp5_document._links.action_object_jio_action)
          .concat(ensureArray(erp5_document._links.action_object_jio_button))
          .concat(ensureArray(erp5_document._links.action_object_jio_fast_input));

        if (view === 'view') {
          for (i = 0; i < view_list.length; i += 1) {
            view_list[i].class_name = view_list[i].name === view ? 'active' : '';
          }
        } else {
          for (i = 0; i < workflow_list.length; i += 1) {
            workflow_list[i].class_name = workflow_list[i].href === view ? 'active' : '';
          }
          for (i = 0; i < view_list.length; i += 1) {
            view_list[i].class_name = view_list[i].href === view ? 'active' : '';
          }
          for (i = 0; i < action_list.length; i += 1) {
            action_list[i].class_name = action_list[i].href === view ? 'active' : '';
          }
        }
        // Prevent has much as possible to modify the DOM panel
        // stateChange prefer to compare strings
        workflow_list = JSON.stringify(workflow_list);
        view_list = JSON.stringify(view_list);
        action_list = JSON.stringify(action_list);
      }
      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            display_workflow_list: display_workflow_list,
            workflow_list: workflow_list,
            view_list: view_list,
            action_list: action_list,
            global: true,
            jio_key: jio_key,
            editable: asBoolean(options.editable) || asBoolean(editable) || false
          });
        });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var context = this,
        gadget = this,
        workflow_list,
        queue = new RSVP.Queue();

      if (modification_dict.hasOwnProperty("visible")) {
        if (this.state.visible) {
          if (!this.element.classList.contains('visible')) {
            this.element.classList.toggle('visible');
          }
        } else {
          if (this.element.classList.contains('visible')) {
            this.element.classList.remove('visible');
          }
        }
      }

      if (modification_dict.hasOwnProperty("global")) {
        queue
          .push(function () {
            return context.getDeclaredGadget('erp5_searchfield');
          })
          .push(function (search_gadget) {
            return search_gadget.render({
              focus: false,
              extended_search: ''
            });
          });
      }

      if (modification_dict.hasOwnProperty("editable")) {
        queue
          // Update the global links
          .push(function () {
            return gadget.getSetting("hateoas_url");
          })
          .push(function (hateoas_url) {
            var project_view = hateoas_url +
              '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
              'project_module&view=ProjectModule_viewProjectManagementList',
              document_view = hateoas_url +
              '/ERP5Document_getHateoas?mode=traverse&relative_url=' +
              'document_module&view=Project_viewDocumentList';
            return RSVP.all([
              context.getUrlForList([
                {
                  'command': 'display',
                  'options': {
                    'page': 'form',
                    'editable': 0,
                    'jio_key': 'project_module',
                    'view': project_view,
                    'field_listbox_sort_list:json': [["title", "ascending"]],
                    'field_listbox_column_list:json': ["title",
                                                       "default_destination_section_title"],
                    'extended_search': 'selection_domain_state_project_domain:  "started"'
                  }
                },
                getUrlParameterDict('task_module', "view", [["delivery.start_date", "descending"]],
                  ["title", "delivery.start_date", "source_title"],
                  createProjectQuery(null,
                    [["selection_domain_state_task_domain", "confirmed"]])),
                getUrlParameterDict('task_report_module', 'view', [["delivery.start_date", "descending"]],
                  ["title", "delivery.start_date", "source_title"],
                  createProjectQuery(null,
                    [["selection_domain_state_task_report_domain", "confirmed"]])),
                getUrlParameterDict('document_module', document_view, [["modification_date", "descending"]],
                  ["download", "title", "reference", "modification_date"],
                  createProjectQuery(null, [["selection_domain_state_document_domain", "confirmed"]])),
                getUrlParameterDict('bug_module', "view", [["delivery.start_date", "descending"]],
                  ["title", "description", "source_person_title", "destination_person_title", "delivery.start_date"],
                  createProjectQuery(null,
                    [["selection_domain_state_bug_domain", "open"]])),
                getUrlParameterDict('test_result_module', 'view', [["delivery.start_date", "descending"]],
                  null, createProjectQuery(null, [])),
                {command: 'display', options: {page: "logout"}}
              ]),
              context.getTranslationList([
                'Editable',
                'Projects',
                'Tasks',
                'Tasks Reports',
                'Documents',
                'Bugs',
                'Tests',
                'Logout'
              ]),
              context.getDeclaredGadget("erp5_checkbox")
            ]);
          })
          .push(function (result_list) {
            var editable_value = [],
              i,
              ul_fragment = document.createDocumentFragment(),
              a_element,
              li_element,
              icon_and_key_list = [
                'home', null,
                'puzzle-piece', 'm',
                'tasks', 'w',
                'history', 'h',
                'search', 's',
                'sliders', null,
                'power-off', 'o'
              ],
              ul_element = context.element.querySelector("ul");

            for (i = 0; i < result_list[0].length; i += 1) {
              // <li><a href="URL" class="ui-btn-icon-left ui-icon-ICON" data-i18n="TITLE" accesskey="KEY"></a></li>
              a_element = document.createElement('a');
              li_element = document.createElement('li');
              a_element.href = result_list[0][i];
              a_element.setAttribute('class', 'ui-btn-icon-left ui-icon-' + icon_and_key_list[2 * i]);
              if (icon_and_key_list[2 * i + 1] !== null) {
                a_element.setAttribute('accesskey', icon_and_key_list[2 * i + 1]);
              }
              a_element.textContent = result_list[1][i + 1];
              li_element.appendChild(a_element);
              ul_fragment.appendChild(li_element);
            }

            while (ul_element.firstChild) {
              ul_element.removeChild(ul_element.firstChild);
            }
            ul_element.appendChild(ul_fragment);

            // Update the checkbox field value
            if (context.state.editable) {
              editable_value = ['editable'];
            }
            return result_list[2].render({field_json: {
              editable: true,
              name: 'editable',
              key: 'editable',
              hidden: false,
              items: [[result_list[1][0], 'editable']],
              'default': editable_value
            }});
          });
      }

      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("action_list") ||
          modification_dict.hasOwnProperty("jio_key") ||
          modification_dict.hasOwnProperty("view_list"))) {
        if (this.state.view_list === undefined) {
          gadget.element.querySelector("dl").textContent = '';
        } else {
          queue
            .push(function () {
              var i = 0,
                parameter_list = [],
                view_list = JSON.parse(gadget.state.view_list),
                action_list = JSON.parse(gadget.state.action_list);
              workflow_list = JSON.parse(gadget.state.workflow_list);

              for (i = 0; i < view_list.length; i += 1) {
                parameter_list.push({
                  command: 'display_with_history',
                  options: {
                    jio_key: gadget.state.jio_key,
                    view: view_list[i].href
                  }
                });
              }
              for (i = 0; i < workflow_list.length; i += 1) {
                parameter_list.push({
                  command: 'display_dialog_with_history',
                  options: {
                    jio_key: gadget.state.jio_key,
                    view: workflow_list[i].href
                  }
                });
              }
              for (i = 0; i < action_list.length; i += 1) {
                parameter_list.push({
                  command: 'display_dialog_with_history',
                  options: {
                    jio_key: gadget.state.jio_key,
                    view: action_list[i].href
                  }
                });
              }
              return RSVP.all([
                gadget.getUrlForList(parameter_list),
                gadget.getTranslationList(['Views', 'Workflows', 'Actions'])
              ]);
            })
            .push(function (result_list) {
              var dl_element,
                dl_fragment = document.createDocumentFragment(),
                view_list = JSON.parse(gadget.state.view_list),
                action_list = JSON.parse(gadget.state.action_list);

              appendDt(dl_fragment, result_list[1][0], 'eye',
                       view_list, result_list[0], 0);
              if (gadget.state.display_workflow_list) {
                // show Workflows only on document
                appendDt(dl_fragment, result_list[1][1], 'random',
                  workflow_list, result_list[0], view_list.length);
              }
              appendDt(dl_fragment, result_list[1][2], 'cogs',
                       action_list, result_list[0],
                       view_list.length + workflow_list.length);

              dl_element = gadget.element.querySelector("dl");
              while (dl_element.firstChild) {
                dl_element.removeChild(dl_element.firstChild);
              }
              dl_element.appendChild(dl_fragment);
            });
        }
      }

      return queue;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function click(evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)

    .allowPublicAcquisition('notifyChange', function notifyChange(
      argument_list,
      scope
    ) {
      if (scope === 'erp5_checkbox') {
        var context = this;
        return context.getDeclaredGadget('erp5_checkbox')
          .push(function (gadget) {
            return gadget.getContent();
          })
          .push(function (result) {
            var options = {editable: undefined};
            if (result.editable.length === 1) {
              options.editable = true;
            }
            return context.redirect({command: 'change', options: options}, true);
          });
      }
      // Typing a search query should not modify the header status
      return;
    }, {mutex: 'changestate'})
    .allowPublicAcquisition('notifyValid', function notifyValid() {
      // Typing a search query should not modify the header status
      return;
    })

    .onEvent('submit', function submit() {
      var gadget = this,
        search_gadget,
        redirect_options = {
          page: "search"
        };

      return gadget
        .getDeclaredGadget("erp5_searchfield")
        .push(function (declared_gadget) {
          search_gadget = declared_gadget;
          return search_gadget.getContent();
        })
        .push(function (data) {
          if (data.search) {
            redirect_options.extended_search = data.search;
          }
          // let the search gadget know its current state (value and focus)
          // in order to be able to zero it out in the next Promise
          // input gadget's state does not reflect immediate reality
          // so we need to manage its state from the parent
          return search_gadget.render({
            extended_search: data.search,
            focus: true
          });
        })
        .push(function () {
          // we want the search field in side panel to be empty and blured
          return search_gadget.render({
            extended_search: '',
            focus: false  // we don't want focus on the empty field for sure
          });
        })
        .push(function () {
          return gadget.redirect({command: 'store_and_display', options: redirect_options}, true);
        });

    }, /*useCapture=*/false, /*preventDefault=*/true);

}(window, document, rJS, RSVP, Node, asBoolean, ensureArray, SimpleQuery, ComplexQuery, Query));
