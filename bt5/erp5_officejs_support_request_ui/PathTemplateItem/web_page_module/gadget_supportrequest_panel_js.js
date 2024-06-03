/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, asBoolean , ensureArray,
         mergeGlobalActionWithRawActionList, domsugar*/
(function (window, document, rJS, RSVP, Node, asBoolean, ensureArray,
           mergeGlobalActionWithRawActionList, domsugar) {
  "use strict";

/**
 *  This gadget is same as web_page_module/rjs_gadget_erp5_panel_js with the following differences:
 *    - only Home, Support Requests, Preferences and Logout actions ( no "Modules", "Worklists", "History", ... )
 *    - no [ ] editable checkbox
 *    - object actions does not show "Actions" and "Workflows" is named "Decision"
 *    - search only search support requests
 */

  function appendDt(fragment, dt_title, dt_icon,
                    action_list, href_list, index) {
// <dt class="ui-btn-icon-left ui-icon-eye">Views</dt>
// {{#each view_list}}
// <dd class="document-listview">
//   <a class="{{class_name}}" href="{{href}}">{{title}}</a>
// </dd>
// {{/each}}
    //////////////////////
    var element_list = [
      domsugar('dt', {
        text: dt_title,
        'class': 'ui-btn-icon-left ui-icon-' + dt_icon
      })
    ],
      i;
    for (i = 0; i < action_list.length; i += 1) {
      element_list.push(domsugar('dd', {'class': 'document-listview'}, [
        domsugar('a', {
          href: href_list[index + i],
          text: action_list[i].title,
          'class': action_list[i].class_name || null
        })
      ]));
    }
    fragment.appendChild(domsugar(null, element_list));
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
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
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
    //    action_list,
    //    clone_list,
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
//        action_list = JSON.stringify(group_mapping.action_object_jio_action);
//        clone_list = JSON.stringify(group_mapping.action_object_clone_action);
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
    //        action_list: action_list,
    //        clone_list: clone_list,
            jump_list: jump_list,
            global: true,
            jio_key: jio_key,
            view: view,
            jump_view: jump_view,
            editable: false, // asBoolean(options.editable) || asBoolean(editable) || false,
            extra_menu_list: extra_menu_list
          });
        });
    })
    .onStateChange(function onStateChange(modification_dict) {
      var i,
        gadget = this,
        workflow_list,
        view_list,
        jump_list,
        dl_fragment,
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
            return RSVP.hash({
              url_list: gadget.getUrlForList([
                {command: 'display'},
                {command: 'display', options: {jio_key: "support_request_module"}},
                {command: 'display', options: {page: "supportrequest_preference"}},
                {command: 'display', options: {page: "logout"}}
              ]),
              translation_list: gadget.getTranslationList([
                'Home',
                'Support Requests',
                'Preferences',
                'Logout'
              ])
            });
          })
          .push(function (result_dict) {
            var element_list = [],
              icon_and_key_list = [
                'home', null,
                'life-ring', null,
                'sliders', null,
                'power-off', 'o'
              ];

            for (i = 0; i < result_dict.url_list.length; i += 1) {
              // <li><a href="URL" class="ui-btn-icon-left ui-icon-ICON" data-i18n="TITLE" accesskey="KEY"></a></li>
              element_list.push(domsugar('li', [
                domsugar('a', {
                  href: result_dict.url_list[i],
                  'class': 'ui-btn-icon-left ui-icon-' + icon_and_key_list[2 * i],
                  accesskey: icon_and_key_list[2 * i + 1],
                  text: result_dict.translation_list[i]
                })
              ]));
            }
            domsugar(gadget.element.querySelector("ul"),
                     [domsugar(null, element_list)]);
          });
      }

      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("view") ||
          modification_dict.hasOwnProperty("jump_view") ||
          modification_dict.hasOwnProperty("workflow_list") ||
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
              jump_list = JSON.parse(gadget.state.jump_list);
              workflow_list = JSON.parse(gadget.state.workflow_list);

              parameter_list = view_list
                .concat(workflow_list)
                .concat(jump_list)
                .map(function (options) {
                  return options.url_kw;
                });
              return RSVP.hash({
                url_list: gadget.getUrlForList(parameter_list),
                translation_dict: gadget.getTranslationDict([
                  'Views', 'Decisions', 'Jumps'
                ])
              });
            })
            .push(function (result_dict) {
              appendDt(dl_fragment, result_dict.translation_dict.Views, 'eye',
                       view_list, result_dict.url_list, 0);
              if (gadget.state.display_workflow_list) {
                // show Workflows only on document
                appendDt(dl_fragment, result_dict.translation_dict.Decisions, 'cogs',
                  workflow_list, result_dict.url_list, view_list.length);
              }
              appendDt(dl_fragment, result_dict.translation_dict.Jumps, 'plane',
                       jump_list, result_dict.url_list,
                       view_list.length + workflow_list.length);
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
                href_list.push(extra_menu_list[i].href);
                extra_menu_list[i] = {
                  "class_name": extra_menu_list[i].active ? "active" : "",
                  "title": extra_menu_list[i].title
                };
              }
              appendDt(dl_fragment, translation_list[0], 'globe',
                       extra_menu_list, href_list, 0);
            });
        }
      }
      queue
        .push(function () {
          if (dl_fragment) {
            domsugar(gadget.element.querySelector("dl"), [dl_fragment]);
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

    .allowPublicAcquisition('notifyChange', function notifyChange() {
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
            redirect_options.extended_search =  '(' + data.search + ' AND portal_type: "Support Request")';
          } else {
            redirect_options.extended_search = '( portal_type: "Support Request")';
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
  mergeGlobalActionWithRawActionList, domsugar));