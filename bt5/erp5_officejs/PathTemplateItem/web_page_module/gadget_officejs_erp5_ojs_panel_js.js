/*jslint nomen: true, indent: 2, maxerr: 3, unparam: true */
/*global window, document, rJS, Handlebars, RSVP, Node, loopEventListener */
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
    panel_template_body_list = Handlebars.compile(template_element
                         .getElementById("panel-template-body-list")
                         .innerHTML),
    panel_template_body_desktop = Handlebars.compile(template_element
                                  .getElementById("panel-template-body-desktop")
                                  .innerHTML);

  function getElementList(gadget, element_list) {
    var i = 0,
      element_info_list = [],
      url_for_parameter_list = [],
      element_info,
      key;
    for (key in element_list) {
      if (element_list.hasOwnProperty(key)) {
        element_info = element_list[key];
        url_for_parameter_list.push({ command: 'change',
                                      options: element_info });
        element_info_list[i] = { reference: element_info.reference,
                                 title: element_info.title};
        i += 1;
      }
    }
    return gadget.getUrlForList(url_for_parameter_list)
      .push(function (url_list) {
        var action_list = [], j, element;
        for (j = 0; j < url_list.length; j += 1) {
          element = { href: url_list[j],
            icon: null,
            name: element_info_list[j].reference,
            title: element_info_list[j].title };
          action_list.push(element);
        }
        return action_list;
      });
  }

  function appendDt(fragment, dt_title, dt_icon, action_list) {
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
      a_element.href = action_list[i].href;
      a_element.textContent = action_list[i].title;
      dd_element.appendChild(a_element);
      fragment.appendChild(dd_element);
    }
  }

  gadget_klass
    .setState({
      visible: false,
      desktop: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

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
        context = this;
      if (erp5_document !== undefined) {
        workflow_list = erp5_document._links.action_workflow || [];
        view_list = erp5_document._links.action_object_view || [];
        if (workflow_list.constructor !== Array) {
          workflow_list = [workflow_list];
        }
        if (view_list.constructor !== Array) {
          view_list = [view_list];
        }
        // Prevent has much as possible to modify the DOM panel
        // stateChange prefer to compare strings
        workflow_list = JSON.stringify(workflow_list);
        view_list = JSON.stringify(view_list);
      }
      return context.getUrlParameter('editable')
        .push(function (editable) {
          return context.changeState({
            workflow_list: workflow_list,
            view_list: view_list,
            global: true,
            portal_type: options.portal_type,
            jio_key: options.jio_key,
            editable: options.editable || editable || false
          });
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
            // XXX: Customize panel header!
            return context.translateHtml(
              panel_template_header() +
                panel_template_body()
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

      if (modification_dict.hasOwnProperty("editable")) {
        queue
          // Update the global links
          .push(function () {
            return RSVP.all([
              context.getUrlFor({command: 'display'}),
              context.getUrlFor({command: 'display', options: {page: "ojs_configurator"}}),
              context.getUrlFor({command: 'display', options: {page: "ojs_sync", 'auto_repair': true}})
            ]);
          })
          .push(function (result_list) {
            return context.translateHtml(
              panel_template_body_list({
                "document_list_href": result_list[0],
                "storage_href": result_list[1],
                "sync_href": result_list[2]
              })
            );
          })

          .push(function (result) {
            context.element.querySelector("ul").innerHTML = result;
          });
      }

      if ((this.state.global === true) &&
          (modification_dict.hasOwnProperty("desktop") ||
          modification_dict.hasOwnProperty("editable") ||
          modification_dict.hasOwnProperty("workflow_list") ||
          modification_dict.hasOwnProperty("view_list"))) {
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
                view_list = JSON.parse(gadget.state.view_list);

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
              return RSVP.all(promise_list);
            })
            .push(function (result_list) {
              var i,
                result_workflow_list = [],
                result_view_list = [],
                workflow_list = JSON.parse(gadget.state.workflow_list),
                view_list = JSON.parse(gadget.state.view_list);

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
              gadget.element.querySelector("dl").innerHTML = panel_template_body_desktop({
                workflow_list: result_workflow_list,
                view_list: result_view_list
              });
            });
        }
      }

      queue
        .push(function () {
          return gadget.declareGadget("gadget_officejs_common_util.html");
        })
        .push(function (gadget_utils) {
          return gadget_utils.getViewAndActionDict(modification_dict.portal_type,
                                                   modification_dict.jio_key);
        })
        .push(function (view_action_dict) {
          return RSVP.all([
            getElementList(gadget, view_action_dict.view_list),
            getElementList(gadget, view_action_dict.action_list)
          ]);
        })
        .push(function (view_action_list) {
          var dl_element,
            dl_fragment = document.createDocumentFragment();
          dl_element = gadget.element.querySelector("dl");
          while (dl_element.firstChild) {
            dl_element.removeChild(dl_element.firstChild);
          }
          if (view_action_list[0].length > 0) {
            appendDt(dl_fragment, "VIEWS", 'eye',
                     view_action_list[0]);
            dl_element.appendChild(dl_fragment);
          }
          if (view_action_list[1].length > 0) {
            appendDt(dl_fragment, "ACTIONS", 'cogs',
                     view_action_list[1]);
            dl_element.appendChild(dl_fragment);
          }
          return queue;
        });
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
        if (window.matchMedia("(min-width: 85em)").matches) {
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

    .allowPublicAcquisition('notifyChange', function (argument_list, scope) {
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
            return context.redirect({command: 'change', options: options});
          });
      }
      // Typing a search query should not modify the header status
      return;
    })
    .allowPublicAcquisition('notifyValid', function () {
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
            page: "ojs_document_list"
          };
          if (data.search) {
            options.extended_search = data.search;
          }
          // Remove focus from the search field
          document.activeElement.blur();
          return gadget.redirect({command: 'display', options: options});
        });

    }, false, true)

    .onEvent('blur', function (evt) {
      // XXX Horrible hack to clear the search when focus is lost
      // This does not follow renderJS design, as a gadget should not touch
      // another gadget content
      if (evt.target.type === 'search') {
        evt.target.value = "";
      }
    }, true, false);

}(window, document, rJS, Handlebars, RSVP, Node, loopEventListener));
