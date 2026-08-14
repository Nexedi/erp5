/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, RSVP, Node, domsugar,
         mergeGlobalActionWithRawActionList*/
(function (window, document, rJS, RSVP, Node, domsugar,
           mergeGlobalActionWithRawActionList) {
  "use strict";



  function appendDt(fragment, dt_title, dt_icon,
                    action_list, href_list, index) {
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
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("getTranslationList", "getTranslationList")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")

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
      var jio_key = 'artificial_task_module', //options.jio_key,
        view = options.view,
        jump_view = options.jump_view,
        visible = options.visible,
        action_list = [],
        context = this;

      if (visible === undefined) {
        visible = context.state.visible;
      }

      return context.jio_getAttachment(jio_key, 'links')
        .push(function (result) {
          var url_mapping = mergeGlobalActionWithRawActionList(
              jio_key, view, jump_view, result._links,
              ["action_object_jio_action"],
              {"action_object_jio_action": "display_dialog_with_history"}
            ),
            index;
          action_list = result._links.action_object_jio_action || [];

          for (index = 0; index < action_list.length; index += 1) {
            if (action_list[index].name === 'new') {
              break;
            }
          }
          return context.getUrlFor(
            url_mapping.action_object_jio_action[index].url_kw
          )
            .push(function (new_task_url) {
              action_list = [{
                href: new_task_url,
                title: action_list[index].title
              }];
            });
        })
        .push(function () {
          return context.getUrlParameter('editable');
        })
        .push(function (editable) {
          return context.changeState({
            visible: visible,
            global: true,
            jio_key: jio_key,
            view: view,
            jump_view: jump_view,
            editable: editable,
            action_list: JSON.stringify(action_list)
          });
        });
    })
    .onStateChange(function onStateChange(modification_dict) {
      var i,
        gadget = this,
        dl_fragment,
        action_list,
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
                {
                  command: 'display_stored_state',
                  options: {
                    jio_key: "artificial_task_module",
                    page: "form",
                    view: "view"
                  }
                },
                {command: 'display', options: {page: "history"}},
                //{command: 'display_stored_state', options: {page: "search"}},
                {command: 'display', options: {page: "my_account"}},
                {command: 'display', options: {page: "logout"}}
              ]),
              translation_list: gadget.getTranslationList([
                'Home',
                'Artificial Task Module',
                'History',
                //'Search',
                'My Account',
                'Logout'
              ])
            });
          })
          .push(function (result_dict) {
            var element_list = [],
              icon_and_key_list = [
                'home', null,
                'puzzle-piece', 'm',
                'tasks', 'w',
                'history', 'h',
                'search', 's',
                'sliders', null,
                'power-off', 'o'
              ];

            for (i = 0; i < result_dict.url_list.length; i += 1) {
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
          modification_dict.hasOwnProperty("action_list"))) {

        dl_fragment = document.createDocumentFragment();
        gadget.element.querySelector("dl").textContent = '';
        queue
          .push(function () {
            var parameter_list = [];
            action_list = JSON.parse(gadget.state.action_list);
            return RSVP.hash({
              translation_dict: gadget.getTranslationDict([
                'Actions'
              ])
            });
          })
          .push(function (result_dict) {
            appendDt(dl_fragment, result_dict.translation_dict.Actions, 'cogs',
                     action_list, action_list.map(x => x.href), 0);

          });
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
            redirect_options.extended_search =  '(' + data.search + ' AND portal_type: "Artificial Task")';
          } else {
            redirect_options.extended_search = '( portal_type: "Artificial Task")';
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

}(window, document, rJS, RSVP, Node, domsugar,
  mergeGlobalActionWithRawActionList));