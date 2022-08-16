/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
/*global domsugar, window, rJS, RSVP */
(function (domsugar, window, rJS, RSVP) {
  "use strict";

  var URL_DISPLAY_PARAMETER = 'view',
    MAIN_SCOPE = 'sub_gadget';

  function searchERP5Action(gadget, jio_key, action_name) {
    return gadget.jio_getAttachment(jio_key, 'links')
      .push(function (document_view) {
        var action, action_data, i, j;
        for (i = 0; i < Object.keys(document_view._links).length; i = i + 1) {
          action = Object.keys(document_view._links)[i];
          if (document_view._links.hasOwnProperty(action)) {
            if (document_view._links[action].constructor !== Array) {
              document_view._links[action] = [document_view._links[action]];
            }
            for (j = 0;  j < document_view._links[action].length; j = j + 1) {
              action_data = document_view._links[action][j];
              if (action_data.name === action_name) {
                return action_data.href;
              }
            }
          }
        }
        throw new Error('Action not found: ' + action_name);
      });
  }

  function loadChildGadget(gadget, gadget_url, must_declare, callback) {
    var queue,
      child_gadget;
    if (must_declare) {
      queue = gadget.declareGadget(gadget_url, {scope: MAIN_SCOPE});
    } else {
      queue = gadget.getDeclaredGadget(MAIN_SCOPE);
    }
    return queue
      .push(function (result) {
        child_gadget = result;
        if (callback) {
          return callback(result);
        }
      })
      .push(function (result) {
        if (must_declare) {
          domsugar(gadget.element, [child_gadget.element]);
        }
        return result;
      });
  }

  function renderEmbeddedForm(gadget, jio_key, action_name, must_declare) {
    return searchERP5Action(gadget, jio_key, action_name)
      .push(function (action_href) {
        return loadChildGadget(gadget, "gadget_erp5_page_form.html",
                               must_declare,
                               function (form_gadget) {
            return form_gadget.render({
              jio_key: jio_key,
              view: action_href
            });
          });
      });
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("getTranslationDict", "getTranslationDict")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")

    .declareMethod('triggerSubmit', function () {
      var argument_list = arguments;
      return loadChildGadget(this, "gadget_erp5_page_form.html",
                             false,
                             function (form_gadget) {
          return form_gadget.triggerSubmit.call(form_gadget, argument_list);
        });
    })

    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .allowPublicAcquisition('updatePanel', function () {
      return;
    })

    ////////////////////////////////////////////////////////////////////
    // Go
    ////////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options, action_list) {
      if (action_list === undefined) {
        action_list = [];
      }
      return this.changeState({
        display_step: options[URL_DISPLAY_PARAMETER] || undefined,
        action_list: JSON.stringify(action_list),
        // Force display in any case to refresh the menus
        render_timestamp: new Date().getTime(),
        first_render: true
      });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        _,
        action_list = JSON.parse(gadget.state.action_list),
        url_list;

      if ((gadget.state.display_step === undefined) &&
          (action_list.length > 0)) {
        // display the first action by default
        return gadget.redirect({
          command: 'change',
          options: {
            view: 0
          }
        });
      }

      return gadget.getTranslationDict(['Home'])
        .push(function (translation_dict) {
          _ = translation_dict;
          var url_for_list = [{
            command: 'history_previous'
          }],
            i;
          for (i = 0; i < action_list.length; i += 1) {
            url_for_list.push({
              command: 'change',
              options: {
                view: i
              }
            });
          }
          return gadget.getUrlForList(url_for_list);
        })
        .push(function (result) {
          url_list = result;
          return gadget.updateHeader({
            page_title: _.Home,
            page_icon: 'home',
            front_url: url_list[0]
          });
        })

        .push(function () {
          var first_render = modification_dict.hasOwnProperty('first_render'),
            element_list = [],
            i,
            active,
            matching_action_index = -1,
            promise_list = [],
            extra_menu_list = [];

          // Try to display the matching action
          for (i = 0; i < action_list.length; i += 1) {
            if (gadget.state.display_step === i.toString()) {
              matching_action_index = i;
              active = true;
            } else {
              active = false;
            }
            // Prepare to display action list if no action found
            element_list.push(
              domsugar('li', [
                domsugar('a', {
                  href: url_list[i + 1],
                  text: action_list[i].title
                })
              ])
            );
            extra_menu_list.push({
              href: url_list[i + 1],
              title: action_list[i].title,
              active: active
            });
          }

          if (matching_action_index === -1) {
            // XXX hacky, but enough to force reloading the page gadget
            // during the next render
            gadget.state.first_render = false;
            domsugar(gadget.element, [
              domsugar('img', {src: 'gadget_erp5_panel.png'}),
              domsugar('ul', {
                'class': 'document-listview'
              }, element_list)
            ]);
          } else {
            promise_list.push(renderEmbeddedForm(
              gadget,
              action_list[matching_action_index].jio_key,
              action_list[matching_action_index].erp5_action,
              first_render
            ));
          }

          promise_list.push(gadget.updatePanel({
            extra_menu_list: extra_menu_list
          }));
          return RSVP.all(promise_list);
        });
    });

}(domsugar, window, rJS, RSVP));