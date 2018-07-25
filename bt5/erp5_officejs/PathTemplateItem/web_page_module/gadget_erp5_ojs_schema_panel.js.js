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
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

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
      return RSVP.Queue()
        .push(function () {
          return context.getSetting('jio_storage_name');
        })
        .push(function (storage_name) {
          if (!storage_name) {
            return ["[]", true];
          }
          return RSVP.all([
            context.jio_allDocs({
              "query": '(portal_type:"JSON Schema") AND (NOT (title:""))',
              "limit": [0, 31],
              "select_list": ["title", "reference"],
              "sort_on": [["title", "descending"]]
            })
              .push(function (result) {
                return JSON.stringify(result.data.rows);
              }),
            context.getSetting('developer_mode')
          ]);
        })
        .push(function (ret) {
          var schema_list = ret[0],
            developer_mode = ret[1];
          if (developer_mode === undefined) {
            developer_mode = true;
          }
          if (developer_mode === "false") {
            developer_mode = false;
          }
          return context.changeState({
            workflow_list: workflow_list,
            view_list: view_list,
            schema_list: schema_list,
            global: true,
            developer_mode: developer_mode
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
            return context.declareGadget('gadget_erp5_field_multicheckbox.html', {
              scope: "developer_mode",
              element: tmp_element.querySelector('[data-gadget-scope="developer_mode"]')
            });
          })
          .push(function () {
            context.element.querySelector("div").appendChild(tmp_element);
            return context.listenResize();
          });
      }

      if (modification_dict.hasOwnProperty("schema_list") ||
          modification_dict.hasOwnProperty("developer_mode")) {
        queue
          .push(function () {
            function gen_element(element, title, css, accesskey) {
              return context.getUrlFor(element)
                .push(function (url) {
                  return {
                    title: title,
                    href: url,
                    icon_class: css,
                    accesskey: accesskey
                  };
                });
            }
            var i,
              row,
              tasks = [],
              schema_list = JSON.parse(context.state.schema_list);
            if (context.state.developer_mode) {
              tasks.push(gen_element({command: 'display', options: {page: "ojs_schema_document_list"}},
                "Schemas", "search", "s"));
            }
            for (i = 0; i < schema_list.length; i += 1) {
              row = schema_list[i];
              tasks.push(gen_element({command: 'display', options: {
                page: "ojs_schema_document_list",
                portal_type: "JSON Document",
                schema: row.id,
                schema_title: row.value.title
              }}, row.value.title, "search"));
            }
            tasks.push(gen_element({command: 'display', options: {page: "ojs_sync", 'auto_repair': true}},
              "Synchronize", "refresh"));
            tasks.push(gen_element({command: 'display', options: {page: "ojs_configurator"}},
              "Storages", "dropbox"));
            if (context.state.developer_mode) {
              tasks.push(gen_element({command: 'index', options: {page: "ojs_zip_upload"}},
                "Upload", "upload"));
            }
            return RSVP.all(tasks);
          })
          .push(function (result_list) {
            return context.translateHtml(
              panel_template_body_list(result_list)
            );
          })

          .push(function (result) {
            context.element.querySelector("ul").innerHTML = result;

            // Update the checkbox field value
            return RSVP.all([
              context.getDeclaredGadget("developer_mode"),
              context.translate("Developer Mode")
            ]);
          })
          .push(function (result_list) {
            var value = [],
              developer_mode_gadget = result_list[0],
              title = result_list[1];
            if (context.state.developer_mode) {
              value = ['developer'];
            }
            return developer_mode_gadget.render({field_json: {
              editable: true,
              name: 'developer',
              key: 'developer',
              hidden: false,
              items: [[title, 'developer']],
              default: value
            }});
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
      if (scope === 'developer_mode' && argument_list[0] === "change") {
        var context = this;
        return context.getDeclaredGadget('developer_mode')
          .push(function (gadget) {
            return gadget.getContent();
          })
          .push(function (result) {
            var value = "false";
            if (result.developer.length === 1) {
              value = true;
            }
            return context.setSetting("developer_mode", value);
          })
          .push(function () {
            return context.updatePanel({});
          });
      }
      // Typing a search query should not modify the header status
      return;
    }, {mutex: 'changestate'})
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
            page: "ojs_schema_document_list"
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
