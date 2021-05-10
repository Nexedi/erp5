/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, asBoolean , ensureArray,
         mergeGlobalActionWithRawActionList*/
(function (window, document, rJS, RSVP, Node, asBoolean, ensureArray,
           mergeGlobalActionWithRawActionList) {
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
      if (action_list[i].class_name) {
        // Avoid add class='undefined' in HTML
        a_element.setAttribute('class', action_list[i].class_name);
      }
      a_element.href = href_list[index + i];
      a_element.textContent = action_list[i].title;
      dd_element.appendChild(a_element);
      fragment.appendChild(dd_element);
    }
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
        jump_view = options.jump_view,
        visible = options.visible,
        extra_menu_list = options.extra_menu_list,
        display_workflow_list,
        context = this,
        workflow_list,
        group_mapping,
        view_list,
        action_list,
        clone_list,
        jump_list;

      if (visible === undefined) {
        visible = context.state.visible;
      }

      if (options.display_workflow_list === undefined) {
        display_workflow_list = true;
      } else {
        display_workflow_list = asBoolean(options.display_workflow_list);
      }

      if ((erp5_document !== undefined) && (jio_key !== undefined)) {
        group_mapping = mergeGlobalActionWithRawActionList(jio_key,
          view, jump_view,
          erp5_document._links, [
            "action_workflow",
            "action_object_view", [
              "action_object_jio_action",
              "action_object_jio_button",
              "action_object_jio_fast_input"
            ],
            "action_object_clone_action",
            "action_object_jio_jump"
          ], {
            "action_object_jio_action": "display_dialog_with_history",
            "action_object_clone_action": "display_dialog_with_history"
          }, {
            "action_object_clone_action": true
          });

        workflow_list = JSON.stringify(group_mapping.action_workflow);
        view_list = JSON.stringify(group_mapping.action_object_view);
        action_list = JSON.stringify(group_mapping.action_object_jio_action);
        clone_list = JSON.stringify(group_mapping.action_object_clone_action);
        jump_list = JSON.stringify(group_mapping.action_object_jio_jump);
      }

      if (extra_menu_list !== undefined) {
        extra_menu_list = JSON.stringify(extra_menu_list);
      }

      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            display_workflow_list: display_workflow_list,
            workflow_list: workflow_list,
            view_list: view_list,
            action_list: action_list,
            clone_list: clone_list,
            jump_list: jump_list,
            global: true,
            jio_key: jio_key,
            view: view,
            jump_view: jump_view,
            editable: asBoolean(options.editable) || asBoolean(editable) || false,
            extra_menu_list: extra_menu_list
          });
        });
    })
    .onStateChange(function onStateChange(modification_dict) {
      var i,
        gadget = this,
        workflow_list,
        view_list,
        action_list,
        clone_list,
        jump_list,
        dl_fragment,
        dl_element,
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
            return gadget.getDeclaredGadget('erp5_searchfield');
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
            return RSVP.all([
              gadget.getUrlForList([
                {command: 'display'},
                {command: 'display', options: {page: "front"}},
                {command: 'display', options: {page: "worklist"}},
                {command: 'display', options: {page: "history"}},
                {command: 'display_stored_state', options: {page: "search"}},
                {command: 'display', options: {page: "preference"}},
                {command: 'display', options: {page: "logout"}}
              ]),
              gadget.getTranslationList([
                'Editable',
                'Home',
                'Modules',
                'Worklists',
                'History',
                'Search',
                'Preferences',
                'Logout'
              ]),
              gadget.getDeclaredGadget("erp5_checkbox")
            ]);
          })
          .push(function (result_list) {
            var editable_value = [],
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
              ul_element = gadget.element.querySelector("ul");

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
            if (gadget.state.editable) {
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
          modification_dict.hasOwnProperty("view") ||
          modification_dict.hasOwnProperty("jump_view") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("action_list") ||
          modification_dict.hasOwnProperty("clone_list") ||
          modification_dict.hasOwnProperty("jump_list") ||
          modification_dict.hasOwnProperty("jio_key") ||
          modification_dict.hasOwnProperty("view_list") ||
          modification_dict.hasOwnProperty("extra_menu_list"))) {

        dl_fragment = document.createDocumentFragment();
        gadget.element.querySelector("dl").textContent = '';
        if (this.state.view_list !== undefined) {
          queue
            .push(function () {
              var parameter_list = [];

              view_list = JSON.parse(gadget.state.view_list);
              action_list = JSON.parse(gadget.state.action_list);
              clone_list = JSON.parse(gadget.state.clone_list);
              jump_list = JSON.parse(gadget.state.jump_list);
              workflow_list = JSON.parse(gadget.state.workflow_list);

              parameter_list = view_list.concat(workflow_list).concat(
                action_list
              ).concat(clone_list).concat(jump_list).map(function (options) {return options.url_kw;});
              return RSVP.all([
                gadget.getUrlForList(parameter_list),
                gadget.getTranslationList(['Views', 'Workflows', 'Actions',
                                           'Jumps'])
              ]);
            })
            .push(function (result_list) {
              appendDt(dl_fragment, result_list[1][0], 'eye',
                       view_list, result_list[0], 0);
              if (gadget.state.display_workflow_list) {
                // show Workflows only on document
                appendDt(dl_fragment, result_list[1][1], 'random',
                  workflow_list, result_list[0], view_list.length);
              }
              appendDt(dl_fragment, result_list[1][2], 'cogs',
                       action_list.concat(clone_list), result_list[0],
                       view_list.length + workflow_list.length);
              appendDt(dl_fragment, result_list[1][3], 'plane',
                       jump_list, result_list[0],
                       view_list.length + workflow_list.length +
                       action_list.length + clone_list.length);
            });
        }
        if (gadget.state.hasOwnProperty("extra_menu_list") &&
            gadget.state.extra_menu_list) {
          queue
            .push(function () {
              return gadget.getTranslationList(['Global']);
            })
            .push(function (translation_list) {
              var extra_menu_list = JSON.parse(gadget.state.extra_menu_list),
                href_list = [];
              for (i = 0; i < extra_menu_list.length; i += 1) {
                extra_menu_list[i].options = {
                  "class_name": extra_menu_list[i].active ? "active" : "",
                  "title": extra_menu_list[i].title
                };
                href_list.push(extra_menu_list[i].href);
              }
              appendDt(dl_fragment, translation_list[0], 'globe',
                       extra_menu_list, href_list, 0);
            });
        }
      }
      queue
        .push(function () {
          if (dl_fragment) {
            dl_element = gadget.element.querySelector("dl");
            while (dl_element.firstChild) {
              dl_element.removeChild(dl_element.firstChild);
            }
            dl_element.appendChild(dl_fragment);
          }
        });
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

    .allowPublicAcquisition("notifyFocus", function notifyFocus() {
      // All html5 fields in ERP5JS triggers this method when focus
      // is triggered. This is usefull to display error text.
      // But, in the case of panel, we don't need to handle anything.
      return;
    })
    .allowPublicAcquisition("notifyBlur", function notifyFocus() {
      // All html5 fields in ERP5JS triggers this method when blur
      // is triggered now. This is usefull to display error text.
      // But, in the case of panel, we don't need to handle anything.
      return;
    })

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

}(window, document, rJS, RSVP, Node, asBoolean, ensureArray,
  mergeGlobalActionWithRawActionList));