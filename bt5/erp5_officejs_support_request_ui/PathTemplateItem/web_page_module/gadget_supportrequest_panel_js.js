/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, Handlebars, RSVP, Node */
(function (window, document, rJS, Handlebars, RSVP, Node, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // temlates
  /////////////////////////////////////////////////////////////////
  // Precompile templates while loading the first gadget instance
  var gadget_klass = rJS(window),
    template_element = gadget_klass.__template_element,
    panel_template_header = Handlebars.compile(template_element
                         .getElementById("panel-template-header")
                         .innerHTML),
    panel_template_body = Handlebars.compile(template_element
                         .getElementById("panel-template-body")
                         .innerHTML),
    panel_template_body_desktop = Handlebars.compile(template_element
                                  .getElementById("panel-template-body-desktop")
                                  .innerHTML);

  gadget_klass
    .setState({
      visible: false,
      desktop: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('toggle', function () {
      return this.changeState({
        visible: !this.state.visible
      });
    })
    .declareMethod('close', function () {
      return this.changeState({
        visible: false
      });
    })

    .declareMethod('render', function (options) {
      var erp5_document = options.erp5_document,
        workflow_list,
        view_list,
        jump_list;
      if (erp5_document !== undefined) {
        workflow_list = erp5_document._links.action_workflow || [];
        view_list = erp5_document._links.action_object_view || [];
        jump_list = erp5_document._links.action_object_jio_jump || [];
        if (workflow_list.constructor !== Array) {
          workflow_list = [workflow_list];
        }
        if (view_list.constructor !== Array) {
          view_list = [view_list];
        }
        if (jump_list.constructor !== Array) {
          jump_list = [jump_list];
        }
        // Prevent as much as possible to modify the DOM panel
        // stateChange prefer to compare strings
        workflow_list = JSON.stringify(workflow_list);
        view_list = JSON.stringify(view_list);
        jump_list = JSON.stringify(jump_list);
      }
      return this.changeState({
        workflow_list: workflow_list,
        view_list: view_list,
        jump_list: jump_list,
        global: true,
        editable: options.editable
      });
    })

    .onStateChange(function (modification_dict) {
      var context = this,
        gadget = this,
        queue = new RSVP.Queue(),
        tmp_element;

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
            return RSVP.all([
              context.getUrlFor({command: 'display', options: {page: "supportrequest_preference"}}),
              context.getUrlFor({command: 'display', options: {page: "logout"}}),
              context.getUrlFor({command: 'display_stored_state', options: {jio_key: "support_request_module"}})
            ]);
          })
          .push(function (result_list) {
            // XXX: Customize panel header!
            return context.translateHtml(
              panel_template_header() +
                panel_template_body({
                  "preference_href": result_list[0],
                  "logout_href": result_list[1],
                  "supportrequest_href": result_list[2]
                })
            );
          })
          .push(function (my_translated_or_plain_html) {
            tmp_element = document.createElement('div');
            tmp_element.innerHTML = my_translated_or_plain_html;
            return context.declareGadget('gadget_erp5_searchfield.html', {
              scope: "erp5_searchfield",
              element: tmp_element.querySelector('[data-gadget-scope="erp5_searchfield"]')
            });
          })
          .push(function (search_gadget) {
            return search_gadget.render({
              focus: false
            });
          })
          .push(function () {
            context.element.querySelector("div").appendChild(tmp_element);
            return context.listenResize();
          });
      }
      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("desktop") ||
          modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("view_list") ||
          modification_dict.hasOwnProperty("jump_list"))) {
        if (!(this.state.desktop && (this.state.view_list !== undefined))) {
          queue
            .push(function () {
              gadget.element.querySelector("dl").textContent = '';
            });
        } else {
          queue
            .push(function () {
              var i = 0,
                promise_list = [],
                workflow_list = JSON.parse(gadget.state.workflow_list),
                view_list = JSON.parse(gadget.state.view_list),
                jump_list = JSON.parse(gadget.state.jump_list);

              for (i = 0; i < workflow_list.length; i += 1) {
                promise_list.push(
                  gadget.getUrlFor({
                    command: 'change',
                    options: {
                      view: workflow_list[i].href,
                      page: undefined
                    }
                  })
                );
              }
              for (i = 0; i < view_list.length; i += 1) {
                promise_list.push(
                  gadget.getUrlFor({
                    command: 'change',
                    options: {
                      view: view_list[i].href,
                      page: undefined
                    }
                  })
                );
              }
              for (i = 0; i < jump_list.length; i += 1) {
                promise_list.push(
                  gadget.getUrlFor({
                    command: 'change',
                    options: {
                      view: jump_list[i].href,
                      page: undefined
                    }
                  })
                );
              }
              return RSVP.all(promise_list);
            })
            .push(function (result_list) {
              var i,
                result_workflow_list = [],
                result_view_list = [],
                result_jump_list = [],
                workflow_list = JSON.parse(gadget.state.workflow_list),
                view_list = JSON.parse(gadget.state.view_list),
                jump_list = JSON.parse(gadget.state.jump_list);
              for (i = 0; i < workflow_list.length; i += 1) {
                result_workflow_list.push({
                  title: workflow_list[i].title,
                  href: result_list[i]
                });
              }
              for (i = 0; i < view_list.length; i += 1) {
                result_view_list.push({
                  title: view_list[i].title,
                  href: result_list[i + workflow_list.length]
                });
              }
              for (i = 0; i < jump_list.length; i += 1) {
                result_jump_list.push({
                  title: jump_list[i].title,
                  href: result_list[i + workflow_list.length + view_list.length]
                });
              }
              return gadget.translateHtml(
                panel_template_body_desktop({
                  workflow_list: result_workflow_list,
                  view_list: result_view_list,
                  jump_list: result_jump_list
                })
              ).push(function (my_translated_or_plain_html) {
                gadget.element.querySelector("dl").innerHTML = my_translated_or_plain_html;
              })
            });
        }
      }

      return queue;
    })

    /////////////////////////////////////////////////////////////////
    // declared services
    /////////////////////////////////////////////////////////////////
    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)

    .declareJob('listenResize', function () {
      // resize should be only trigger after the render method
      // as displaying the panel rely on external gadget (for translation for example)
      var result,
        event,
        context = this;
      function extractSizeAndDispatch() {
        if (window.matchMedia("(min-width: 767px)").matches) {
          return context.changeState({
            desktop: true
          });
        }
        return context.changeState({
          desktop: false
        });
      }
      result = loopEventListener(window, 'resize', false,
                                 extractSizeAndDispatch);
      event = document.createEvent("Event");
      event.initEvent('resize', true, true);
      window.dispatchEvent(event);
      return result;
    })

    .allowPublicAcquisition('notifyChange', function () {
      // Typing a search query should not modify the header status
      return;
    })
    .onEvent('submit', function () {
      var gadget = this;

      return gadget.getDeclaredGadget("erp5_searchfield")
        .push(function (search_gadget) {
          return search_gadget.getContent();
        })
        .push(function (data) {
          var options = {
            page: "search"
          };
          if (data.search) {
            options.extended_search = '(' + data.search + ' AND portal_type: "Support Request")';
          } else {
            options.extended_search = '( portal_type: "Support Request")';
          }
          // Remove focus from the search field
          document.activeElement.blur();
          return gadget.redirect({command: 'display', options: options});
        });

    }, false, true)
    .onEvent('click', function (evt) {
      if ((evt.target.nodeType === Node.ELEMENT_NODE) &&
          (evt.target.tagName === 'BUTTON')) {
        return this.toggle();
      }
    }, false, false)
    .onEvent('blur', function (evt) {
      // XXX Horrible hack to clear the search when focus is lost
      // This does not follow renderJS design, as a gadget should not touch
      // another gadget content
      if (evt.target.type === 'search') {
        evt.target.value = "";
      }
    }, true, false);

}(window, document, rJS, Handlebars, RSVP, Node, rJS.loopEventListener));
