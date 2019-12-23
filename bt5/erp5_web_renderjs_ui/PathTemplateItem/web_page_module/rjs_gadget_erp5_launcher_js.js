/*globals window, document, RSVP, rJS,
          URI, location, XMLHttpRequest, console, navigator, Event,
          URL*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console, navigator, Event,
           URL) {
  "use strict";

  var MAIN_SCOPE = "m",
    default_state_json_string = JSON.stringify({
      panel_visible: false,
      setting_id: "setting/" + document.head.querySelector(
        'script[data-renderjs-configuration="application_title"]'
      ).textContent
    });

  function renderMainGadget(gadget, url, options) {
    var page_gadget;
    return gadget.declareGadget(url, {
      scope: MAIN_SCOPE
    })
      .push(function (result) {
        page_gadget = result;
        gadget.props.m_options_string = JSON.stringify(options);
        if (page_gadget.render !== undefined) {
          return page_gadget.render(options);
        }
      })
      .push(function () {
        return page_gadget;
      });
  }

  function initHeaderOptions(gadget) {
    gadget.props.header_argument_list = {
      panel_action: true,
      title: gadget.props.application_title || "OfficeJS"
    };
  }

  function initPanelOptions(gadget) {
    gadget.props.panel_argument_list = {};
  }

  function executeRouteMethod(my_gadget, my_method, argument_list) {
    // Execute a method on a gadget
    if (argument_list) {
      return my_gadget[my_method].apply(my_gadget, argument_list);
    }
    return my_gadget[my_method]();
  }

  function route(my_root_gadget, my_scope, my_method, argument_list) {
    // If the gadget already has been declared, execute the method
    // No need to care about concurrency at this point.
    // This should be handled by the gadget itself if needed
    if (my_root_gadget.props.is_declared_gadget_dict[my_scope]) {
      return my_root_gadget.getDeclaredGadget(my_scope)
        .push(function (my_gadget) {
          return executeRouteMethod(my_gadget, my_method, argument_list);
        });
    }
    // declare the gadget and run the method
    var method;
    if (my_scope === 'notification') {
      method = my_root_gadget.declareAndExecuteNotificationGadget;
    } else if (my_scope === 'translation_gadget') {
      method = my_root_gadget.declareAndExecuteTranslationGadget;
    } else if (my_scope === 'header') {
      method = my_root_gadget.declareAndExecuteHeaderGadget;
    } else if (my_scope === 'panel') {
      method = my_root_gadget.declareAndExecutePanelGadget;
    } else if (my_scope === 'editor_panel') {
      method = my_root_gadget.declareAndExecuteEditorPanelGadget;
    } else {
      throw new Error('Unknown gadget scope: ' + my_scope);
    }
    return method.apply(my_root_gadget, [
      my_scope,
      my_method,
      argument_list
    ]);
  }

  function updateHeader(gadget) {
    return route(gadget, "header", 'notifySubmitted')
      .push(function () {
        return route(gadget, 'header', 'notifyLoaded');
      })
      .push(function () {
        return route(gadget, "header", 'render',
                     [gadget.props.header_argument_list]);
      });
  }

  function updatePanel(gadget) {
    return route(gadget, 'panel', 'render', [gadget.props.panel_argument_list]);
  }

  function refreshHeaderAndPanel(gadget, refresh) {
    var promise;
    if (refresh) {
      promise = route(gadget, "header", 'render',
                      [gadget.props.header_argument_list]);
    } else {
      promise = updateHeader(gadget);
    }
    return RSVP.all([
      promise,
      updatePanel(gadget)
    ]);
  }

  function callJioGadget(gadget, method, param_list) {
    return route(gadget, 'jio_gadget', method, param_list);
  }

  function displayErrorContent(gadget, original_error) {
    var error_list = [original_error],
      i,
      error,
      error_response,
      error_text = "";

    // Do not break the application in case of errors.
    // Display it to the user for now,
    // and allow user to go back to the frontpage

    // Add error handling stack
    error_list.push(new Error('stopping ERP5JS'));

    for (i = 0; i < error_list.length; i += 1) {
      error = error_list[i];
      if (error instanceof Event) {
        error = {
          string: error.toString(),
          message: error.message,
          type: error.type,
          target: error.target
        };
        if (error.target !== undefined) {
          error_list.splice(i + 1, 0, error.target);
        }
      }
      if (error instanceof XMLHttpRequest) {
        if (error.getResponseHeader('Content-Type').indexOf('text/') === 0) {
          error_response = error.response;
        }
        error = {
          message: error.toString(),
          readyState: error.readyState,
          status: error.status,
          statusText: error.statusText,
          response: error.response,
          responseUrl: error.responseUrl,
          response_headers: (error.getAllResponseHeaders()
                             ? error.getAllResponseHeaders().split('\r\n')
                             : null)
        };
      }
      if (error.constructor === Array ||
          error.constructor === String ||
          error.constructor === Object) {
        try {
          error = JSON.stringify(error, null, '  ');
        } catch (ignore) {
        }
      }

      error_text += error.message || error;
      error_text += '\n';

      if (error.fileName !== undefined) {
        error_text += 'File: ' +
          error.fileName +
          ': ' + error.lineNumber + '\n';
      }
      if (error.stack !== undefined) {
        error_text += 'Stack: ' + error.stack + '\n';
      }
      error_text += '---\n';
    }

    console.error(original_error);
    if (original_error instanceof Error) {
      console.error(original_error.stack);
    }
    if (gadget.props === undefined) {
      // Gadget has not yet been correctly initialized
      throw error;
    }
    if (error_response && error_response.text) {
      return error_response.text().then(
        function (request_error_text) {
          return gadget.changeState({
            error_text: error_text,
            request_error_text: request_error_text,
            url: undefined
          });
        }
      );
    }
    return gadget.changeState({
      error_text: error_text,
      request_error_text: error_response,
      url: undefined
    });

  }

  function displayError(gadget, error) {
    if (error instanceof RSVP.CancellationError) {
      return;
    }
    return displayErrorContent(gadget, error);
  }

  function hideDesktopPanel(gadget, hide) {
    var element = gadget.element.querySelector('div[data-role="page"]');
    if (hide) {
      if (!element.classList.contains('desktop-panel-hidden')) {
        element.classList.toggle('desktop-panel-hidden');
      }
    } else {
      if (element.classList.contains('desktop-panel-hidden')) {
        element.classList.remove('desktop-panel-hidden');
      }
    }
  }

  function triggerMaximize(gadget, maximize) {
    if (gadget.props.deferred_minimize !== undefined) {
      gadget.props.deferred_minimize.resolve();
      gadget.props.deferred_minimize = undefined;
    }
    hideDesktopPanel(gadget, maximize);
    if (maximize) {
      return route(gadget, 'header', 'setButtonTitle', [{
        icon: "compress",
        action: "maximize"
      }])
        .push(function () {
          gadget.props.deferred_minimize = RSVP.defer();
          return gadget.props.deferred_minimize.promise;
        })
        .push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            return triggerMaximize(gadget, false);
          }
        });
    }
    return route(gadget, 'header', 'setButtonTitle', [{}]);
  }

  //////////////////////////////////////////
  // Page rendering
  //////////////////////////////////////////
  function declareAndExecuteRouteMethod(my_scope, my_method,
                                        argument_list) {
    // Must be called in a mutex protected method only
    // The idea is to prevent loading the same gadget twice thanks to the mutex
    var my_root_gadget = this,
      my_gadget,
      element;
    // If a previous mutex method was running, no need to redeclare the gadget
    if (my_root_gadget.props.is_declared_gadget_dict[my_scope]) {
      return my_root_gadget.getDeclaredGadget(my_scope)
        .push(function (my_gadget) {
          return executeRouteMethod(my_gadget, my_method, argument_list);
        });
    }
    element = my_root_gadget.element
                            .querySelector("[data-gadget-scope='" +
                                           my_scope + "']");
    return my_root_gadget.declareGadget(
      element.getAttribute('data-gadget-async-url'),
      {scope: my_scope}
    )
      .push(function (result) {
        my_gadget = result;
        return executeRouteMethod(my_gadget, my_method, argument_list);
      })
      .push(function (result) {
        // Wait for the method to be finished before adding the gadget to the
        // DOM. This reduces the panel flickering on slow machines
        element.parentNode.replaceChild(my_gadget.element, element);
        my_root_gadget.props.is_declared_gadget_dict[my_scope] = true;
        return result;
      });
  }

  function setSettingDict(gadget, setting_dict) {
    var jio_gadget,
      update_setting;
    return gadget.getDeclaredGadget("setting_gadget")
      .push(function (result) {
        jio_gadget = result;
        return jio_gadget.get(gadget.state.setting_id);
      })
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return {};
        }
        throw error;
      })
      .push(function (doc) {
        for (var key in setting_dict) {
          if (setting_dict.hasOwnProperty(key)) {
            if (!doc.hasOwnProperty(key) ||
                doc[key] !== setting_dict[key]) {
              doc[key] = setting_dict[key];
              update_setting = true;
            }
          }
        }
        if (update_setting) {
          return jio_gadget.put(gadget.state.setting_id, doc);
        }
      });
  }

  rJS(window)

    // Add mutex protected defered gadget loader.
    // Multiple mutex are needed, to not prevent concurrent loading on
    // different gadgets
    .declareMethod(
      'declareAndExecuteNotificationGadget',
      declareAndExecuteRouteMethod,
      {mutex: 'declareAndExecuteNotificationGadget'}
    )
    .declareMethod(
      'declareAndExecuteTranslationGadget',
      declareAndExecuteRouteMethod,
      {mutex: 'declareAndExecuteTranslationGadget'}
    )
    .declareMethod(
      'declareAndExecuteHeaderGadget',
      declareAndExecuteRouteMethod,
      {mutex: 'declareAndExecuteHeaderGadget'}
    )
    .declareMethod(
      'declareAndExecutePanelGadget',
      declareAndExecuteRouteMethod,
      {mutex: 'declareAndExecutePanelGadget'}
    )
    .declareMethod(
      'declareAndExecuteEditorPanelGadget',
      declareAndExecuteRouteMethod,
      {mutex: 'declareAndExecuteEditorPanelGadget'}
    )

    .setState(JSON.parse(default_state_json_string))
    .ready(function () {
      var gadget = this,
        setting_gadget,
        setting;
      this.props = {
        content_element: this.element.querySelector('.gadget-content'),
        is_declared_gadget_dict: {
          setting_gadget: true,
          router: true,
          jio_gadget: true
        }
      };
      // Configure setting storage
      return gadget.getDeclaredGadget("setting_gadget")
        .push(function (result) {
          setting_gadget = result;
          return setting_gadget.createJio({
            type: "indexeddb",
            database: "setting"
          });
        })
        .push(function () {

          return setting_gadget.get(gadget.state.setting_id)
            .push(undefined, function (error) {
              if (error.status_code === 404) {
                return {};
              }
              throw error;
            });
        })
        .push(function (result) {
          setting = result;
          // Extract configuration parameters stored in HTML
          // XXX Will work only if top gadget...
          var element_list =
            document.head
            .querySelectorAll("script[data-renderjs-configuration]"),
            len = element_list.length,
            key,
            value,
            i;

          for (i = 0; i < len; i += 1) {
            key = element_list[i].getAttribute('data-renderjs-configuration');
            value = element_list[i].textContent;
            gadget.props[key] = value;
            setting[key] = value;
          }

          // Calculate erp5 hateoas url
          setting.hateoas_url = (new URI(gadget.props.hateoas_url))
                              .absoluteTo(location.href)
                              .toString();

          if (setting.hasOwnProperty('service_worker_url') &&
              (setting.service_worker_url !== '')) {
            if (navigator.serviceWorker !== undefined) {
              // Check if a ServiceWorker already controls the site on load
              if (!navigator.serviceWorker.controller) {
                // Register the ServiceWorker
                navigator.serviceWorker.register(setting.service_worker_url);
              }
            }
          }

          return setting_gadget.put(gadget.state.setting_id, setting);
        })
        .push(function () {
          // Configure jIO storage
          return gadget.getDeclaredGadget("jio_gadget");
        })

        .push(function (jio_gadget) {
          return jio_gadget.createJio(setting.jio_storage_description);
        })
        .push(function () {
          return route(gadget, 'router', 'start');
        });
    })

    //////////////////////////////////////////
    // Allow Acquisition
    //////////////////////////////////////////
    .allowPublicAcquisition("getSettingList",
                            function getSettingList(argument_list) {
        var key_list = argument_list[0];
        return route(this, 'setting_gadget', 'get', [this.state.setting_id])
          .push(function (doc) {
            var i,
              result_list = [];
            for (i = 0; i < key_list.length; i += 1) {
              result_list[i] = doc[key_list[i]];
            }
            return result_list;
          }, function (error) {
            if (error.status_code === 404) {
              return new Array(key_list.length);
            }
            throw error;
          });
      })
    .allowPublicAcquisition("getSetting", function getSetting(argument_list) {
      var gadget = this,
        key = argument_list[0],
        default_value = argument_list[1];
      return route(gadget, 'setting_gadget', 'get', [gadget.state.setting_id])
        .push(function (doc) {
          return doc[key] || default_value;
        }, function (error) {
          if (error.status_code === 404) {
            return default_value;
          }
          throw error;
        });
    })
    .allowPublicAcquisition("setSetting", function setSetting(argument_list) {
      var setting_dict = {};
      setting_dict[argument_list[0]] = argument_list[1];
      return setSettingDict(this, setting_dict);
    })
    .allowPublicAcquisition("setSettingList",
                            function setSettingList(argument_list) {
        var setting_dict = argument_list[0];
        return setSettingDict(this, setting_dict);
      })
    .allowPublicAcquisition("translateHtml", function translateHtml(
      argument_list
    ) {
      return route(this, 'translation_gadget', 'translateHtml', argument_list);
    })

    // XXX Those methods may be directly integrated into the header,
    // as it handles the submit triggering
    .allowPublicAcquisition('notifySubmitting', function notifySubmitting(
      argument_list
    ) {
      return RSVP.all([
        route(this, "header", 'notifySubmitting'),
        this.deferChangeState({
          // Force calling notify
          notification_timestamp: new Date().getTime(),
          notification_options: argument_list[0]
        })
      ]);
    })
    .allowPublicAcquisition('notifySubmitted', function notifySubmitted(
      argument_list
    ) {
      return RSVP.all([
        route(this, "header", 'notifySubmitted'),
        this.deferChangeState({
          // Force calling notify
          notification_timestamp: new Date().getTime(),
          notification_options: argument_list[0]
        }),
        route(this, "router", 'notify', argument_list)
      ]);
    })
    .allowPublicAcquisition('notifyChange', function notifyChange(
      argument_list
    ) {
      return RSVP.all([
        route(this, "header", 'notifyChange'),
        this.deferChangeState({
          // Force calling notify
          notification_timestamp: new Date().getTime(),
          notification_options: argument_list[0]
        }),
        route(this, "router", 'notify', argument_list)
      ]);
    })

    .allowPublicAcquisition('isDesktopMedia', function isDesktopMedia() {
      return window.matchMedia("(min-width: 85em)").matches;
    })

    .allowPublicAcquisition('refresh', function refresh() {
      var gadget = this;
      return gadget.getDeclaredGadget(MAIN_SCOPE)
        .push(function (main) {
          if (main.render !== undefined) {
            return main.render(JSON.parse(gadget.props.m_options_string));
          }
        }, function () {
          return;
        });
    })

    .allowPublicAcquisition("translate", function translate(argument_list) {
      return route(this, 'translation_gadget', 'translate', argument_list);
    })
    .allowPublicAcquisition("getTranslationList",
                            function getTranslationList(argument_list) {
        return route(this, 'translation_gadget', 'getTranslationList',
                     argument_list);
      })
    .allowPublicAcquisition("getLanguage", function getLanguage() {
      return route(this, 'translation_gadget', 'getLanguage');
    })

    .allowPublicAcquisition("redirect", function redirect(param_list) {
      return route(this, 'router', 'redirect', param_list);
    })
    .allowPublicAcquisition('reload', function reload() {
      return location.reload();
    })
    .allowPublicAcquisition("getUrlParameter", function getUrlParameter(
      param_list
    ) {
      return route(this, 'router', 'getUrlParameter', param_list);
    })
    .allowPublicAcquisition("getUrlFor", function getUrlFor(param_list) {
      return route(this, 'router', 'getCommandUrlFor', param_list);
    })
    .allowPublicAcquisition("getUrlForList", function getUrlForList(
      param_list
    ) {
      return route(this, 'router', 'getCommandUrlForList', param_list);
    })

    .allowPublicAcquisition("updateHeader", function updateHeader(param_list) {
      initHeaderOptions(this);
      var text_list = [],
        key,
        gadget = this;
      for (key in param_list[0]) {
        if (param_list[0].hasOwnProperty(key)) {
          gadget.props.header_argument_list[key] = param_list[0][key];
        }
      }

      text_list.push(gadget.props.header_argument_list.title);
      if (gadget.props.header_argument_list.hasOwnProperty('right_title')) {
        text_list.push(gadget.props.header_argument_list.right_title);
      }
      return route(gadget, 'translation_gadget', 'getTranslationList',
                   text_list)
        .push(function (result_list) {
          gadget.props.header_argument_list.title = result_list[0];
          if (result_list.length === 2) {
            gadget.props.header_argument_list.right_title = result_list[1];
          }
        });
    })

    .allowPublicAcquisition("updatePanel", function updatePanel(param_list) {
      var gadget = this;
      initPanelOptions(gadget);
      gadget.props.panel_argument_list = param_list[0];
    })

    .allowPublicAcquisition('refreshHeaderAndPanel',
                            function acquireRefreshHeaderAndPanel() {
      return refreshHeaderAndPanel(this, true);
    })

    .allowPublicAcquisition('hidePanel', function hidePanel(param_list) {
      return hideDesktopPanel(this, param_list[0]);
    })
    .allowPublicAcquisition('triggerPanel', function triggerPanel() {
      // Force calling panel toggle
      return this.deferChangeState({
        panel_visible: new Date().getTime()
      });
    })
    .allowPublicAcquisition('renderEditorPanel',
                            function renderEditorPanel(param_list) {
        return this.deferChangeState({
          // Force calling editor panel render
          editor_panel_render_timestamp: new Date().getTime(),
          editor_panel_url: param_list[0],
          editor_panel_options: param_list[1]
        });
      })
    .allowPublicAcquisition("jio_allDocs", function jio_allDocs(param_list) {
      return callJioGadget(this, "allDocs", param_list);
    })
    .allowPublicAcquisition("jio_remove", function jio_remove(param_list) {
      return callJioGadget(this, "remove", param_list);
    })
    .allowPublicAcquisition("jio_post", function jio_post(param_list) {
      return callJioGadget(this, "post", param_list);
    })
    .allowPublicAcquisition("jio_put", function jio_put(param_list) {
      return callJioGadget(this, "put", param_list);
    })
    .allowPublicAcquisition("jio_get", function jio_get(param_list) {
      return callJioGadget(this, "get", param_list);
    })
    .allowPublicAcquisition("jio_allAttachments",
                            function jio_allAttachments(param_list) {
        return callJioGadget(this, "allAttachments", param_list);
      })
    .allowPublicAcquisition("jio_getAttachment",
                            function jio_getAttachment(param_list) {
        return callJioGadget(this, "getAttachment", param_list);
      })
    .allowPublicAcquisition("jio_putAttachment",
                            function jio_putAttachment(param_list) {
        return callJioGadget(this, "putAttachment", param_list);
      })
    .allowPublicAcquisition("jio_removeAttachment",
                            function jio_removeAttachment(param_list) {
        return callJioGadget(this, "removeAttachment", param_list);
      })
    .allowPublicAcquisition("jio_repair", function jio_repair(param_list) {
      return callJioGadget(this, "repair", param_list);
    })
    .allowPublicAcquisition("triggerSubmit", function triggerSubmit(
      param_list
    ) {
      return this.getDeclaredGadget(MAIN_SCOPE)
        .push(function (main_gadget) {
          return main_gadget.triggerSubmit.apply(main_gadget, param_list);
        });
    })
    .allowPublicAcquisition("triggerMaximize", function maximize(
      param_list
    ) {
      return triggerMaximize(this, param_list[0]);
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("renderApplication", function renderApplication(
      param_list
    ) {
      return this.render.apply(this, param_list);
    })

    .declareJob('deferChangeState', function deferChangeState(state) {
      return this.changeState(state);
    })
    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        route_result = gadget.state,
        promise_list;

      if (modification_dict.hasOwnProperty('error_text')) {
        return gadget.dropGadget(MAIN_SCOPE)
          .push(undefined, function () {
            // Do not crash the app if the pg gadget in not defined
            // ie, keep the original error on screen
            return;
          })
          .push(function () {
            var element = gadget.props.content_element,
              container = document.createElement("section"),
              paragraph,
              iframe,
              link;

            paragraph = document.createElement("p");
            paragraph.textContent =
              'Please report this unhandled error to the support team, ' +
              'and go back to the ';
            link = document.createElement("a");
            link.href = '#';
            link.textContent = 'homepage';
            paragraph.appendChild(link);
            container.appendChild(paragraph);

            container.appendChild(document.createElement("br"));

            paragraph = document.createElement("p");
            paragraph.textContent = 'Location: ';
            link = document.createElement("a");
            link.href = link.textContent = window.location.toString();
            paragraph.appendChild(link);
            container.appendChild(paragraph);

            paragraph = document.createElement("p");
            paragraph.textContent = 'User-agent: ' + navigator.userAgent;
            container.appendChild(paragraph);

            paragraph = document.createElement("p");
            paragraph.textContent =
              'Date: ' + new Date(Date.now()).toISOString();
            container.appendChild(paragraph);

            paragraph = document.createElement("p");
            paragraph.textContent = 'Online: ' + navigator.onLine;
            container.appendChild(paragraph);

            container.appendChild(document.createElement("br"));

            link = document.createElement("code");
            link.textContent = gadget.state.error_text;
            paragraph = document.createElement("pre");
            paragraph.appendChild(link);
            container.appendChild(paragraph);

            // Remove the content
            while (element.firstChild) {
              element.removeChild(element.firstChild);
            }
            element.appendChild(container);

            // make an iframe to display error page from XMLHttpRequest.
            if (gadget.state.request_error_text) {
              iframe = document.createElement('iframe');
              container.appendChild(iframe);
              iframe.srcdoc = gadget.state.request_error_text;
            }

            // reset gadget state
            gadget.state = JSON.parse(default_state_json_string);
          });
      }

      promise_list = [];

      // Update the main gadget
      if (modification_dict.hasOwnProperty('render_timestamp')) {
        // By default, init the header options to be empty
        // (ERP5 title by default + sidebar)
        initHeaderOptions(gadget);
        initPanelOptions(gadget);
        if (!modification_dict.hasOwnProperty('first_bootstrap')) {
          promise_list.push(route(gadget, 'header', 'notifyLoading'));
        }
      }
      if (modification_dict.hasOwnProperty('url')) {
        promise_list.push(renderMainGadget(
          gadget,
          route_result.url,
          route_result.options
        )
          .push(function (main_gadget) {
            // Append loaded gadget in the page
            if (main_gadget !== undefined) {
              var element = gadget.props.content_element,
                content_container = document.createDocumentFragment();

              // go to the top of the page
              window.scrollTo(0, 0);

              // Clear first to DOM, append after to reduce flickering/manip
              while (element.firstChild) {
                element.removeChild(element.firstChild);
              }
              content_container.appendChild(main_gadget.element);
              element.appendChild(content_container);

              return refreshHeaderAndPanel(gadget);
              // XXX Drop notification
              // return header_gadget.notifyLoaded();
            }
          }));
      } else if (modification_dict.hasOwnProperty('render_timestamp')) {
        // Same subgadget
        promise_list.push(gadget.getDeclaredGadget(MAIN_SCOPE)
          .push(function (page_gadget) {
            return page_gadget.render(gadget.state.options);
          })
          .push(function () {
            return refreshHeaderAndPanel(gadget);
          }));
      }

      // Update the panel state
      if (modification_dict.hasOwnProperty('panel_visible')) {
        if (gadget.state.panel_visible !== false) {
          promise_list.push(route(this, 'panel', "toggle"));
        } else {
          promise_list.push(route(this, 'panel', "close"));
        }
      }
      // Update the editor panel
      if (modification_dict.hasOwnProperty('editor_panel_url') ||
          modification_dict.hasOwnProperty('editor_panel_render_timestamp')) {
        promise_list.push(
          route(gadget, 'editor_panel', 'render',
                [gadget.state.editor_panel_url,
                 gadget.state.editor_panel_options])
        );
      }

      // Update the notification
      if (modification_dict.hasOwnProperty('notification_options') ||
          modification_dict.hasOwnProperty('notification_timestamp')) {
        if (gadget.state.notification_options === undefined) {
          promise_list.push(
            route(gadget, "notification", 'close')
          );
        } else {
          promise_list.push(
            route(this, "notification", 'notify',
                  [gadget.state.notification_options])
          );
        }
      }

      return RSVP.all(promise_list);
    })
    // Render the page
    .declareMethod('render', function render(route_result, keep_message) {
      var gadget = this;
      return gadget.changeState({
        first_bootstrap: true,
        url: route_result.url,
        options: route_result.options,
        panel_visible: false,
        editor_panel_url: undefined,
        notification_options: (keep_message === true) ?
                              gadget.state.notification_options : undefined,
        // Force calling main gadget render
        render_timestamp: new Date().getTime()
      })
        .push(undefined, function (error) {
          return displayError(gadget, error);
        });
    })

    /////////////////////////////////
    // Handle sub gadgets services
    /////////////////////////////////
    .allowPublicAcquisition('reportServiceError', function reportServiceError(
      param_list,
      gadget_scope
    ) {
      if (gadget_scope === undefined) {
        // don't fail in case of dropped subgadget (like previous page)
        return;
      }

      return displayError(this, param_list[0]);
    })

    .onEvent('submit', function submit() {
      return displayError(this, new Error("Unexpected form submit"));
    })

    /////////////////////////////////////////////////////////////////
    // For Firefox, Wallpaper URL must be absolute one.
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var index, styleSheet, wallpaper_url, wallpaper_absolute_url;
      if (navigator.userAgent.toLowerCase().indexOf('firefox') > -1) {
        for (index = 0; index < document.styleSheets.length; index += 1) {
          styleSheet = document.styleSheets[index];
          if ((styleSheet.href !== null) &&
              (styleSheet.href.startsWith('data:text/css;'))) {
            wallpaper_url = styleSheet.cssRules[0].style
              .backgroundImage.slice(4, -1).replace(/["']/g, '');
            wallpaper_absolute_url = new URL(
              wallpaper_url,
              window.location.toString()
            );
            styleSheet.cssRules[0].style.backgroundImage =
              'url("' + wallpaper_absolute_url.href + '")';
            break;
          }
        }
        index = null;
        styleSheet = null;
        wallpaper_url = null;
        wallpaper_absolute_url = null;
      }
    });

}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console, navigator, Event, URL));