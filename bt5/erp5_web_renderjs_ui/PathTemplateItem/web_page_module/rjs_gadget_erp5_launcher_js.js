/*globals window, document, RSVP, rJS,
          URI, location, XMLHttpRequest, console, navigator, ProgressEvent*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console, navigator, ProgressEvent) {
  "use strict";

  var MAIN_SCOPE = "m";

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

  function route(my_root_gadget, my_scope, my_method, argument_list) {
    return my_root_gadget.getDeclaredGadget(my_scope)
      .push(undefined, function (error) {
        if (error instanceof rJS.ScopeError) {
          var element = my_root_gadget
                          .element
                          .querySelector("[data-gadget-scope='" +
                                         my_scope + "']");
          if (element !== null) {
            return my_root_gadget.declareGadget(
              element.getAttribute('data-gadget-async-url'),
              {
                scope: my_scope,
                element: element
              }
            );
          }
        }
        throw error;
      })
      .push(function (my_gadget) {
        if (argument_list) {
          return my_gadget[my_method].apply(my_gadget, argument_list);
        }
        return my_gadget[my_method]();
      });
  }

  function updateHeader(gadget) {
    var header_gadget;
    return gadget.getDeclaredGadget("header")
      .push(function (result) {
        header_gadget = result;
        return header_gadget.notifySubmitted();
      })
      .push(function () {
        return header_gadget.render(gadget.props.header_argument_list);
      });
  }

  function updatePanel(gadget) {
    return route(gadget, 'panel', 'render', [gadget.props.panel_argument_list]);
  }

  function increaseLoadingCounter(gadget) {
    gadget.props.loading_counter += 1;
    if (gadget.props.loading_counter === 1) {
      return route(gadget, 'header', 'notifyLoading');
    }
    return new RSVP.Queue();
  }

  function decreaseLoadingCounter(gadget) {
    gadget.props.loading_counter -= 1;
    if (gadget.props.loading_counter < 0) {
      gadget.props.loading_counter = 0;
      // throw new Error("Unexpected negative loading counter");
    }
    if (gadget.props.loading_counter === 0) {
      return route(gadget, 'header', 'notifyLoaded');
    }
    return new RSVP.Queue();
  }

  function callJioGadget(gadget, method, param_list) {
    var called = true;
    return increaseLoadingCounter(gadget)
      .push(function () {
        return gadget.getDeclaredGadget("jio_gadget");
      })
      .push(function (jio_gadget) {
        return jio_gadget[method].apply(jio_gadget, param_list);
      })
      .push(function (result) {
        return decreaseLoadingCounter(gadget)
          .push(function () {
            return result;
          });
      }, function (error) {
        if (called) {
          return decreaseLoadingCounter(gadget)
            .push(function () {
              throw error;
            });
        }
        throw error;
      });
  }

  function displayErrorContent(gadget, error) {
    // Do not break the application in case of errors.
    // Display it to the user for now,
    // and allow user to go back to the frontpage
    var error_text = "";
    if (error instanceof ProgressEvent) {
      error = error.target.error;
    }

    if ((error !== undefined) && (error.target instanceof XMLHttpRequest)) {
      error_text = error.target.toString() + " " +
        error.target.status + " " +
        error.target.statusText + "\n" +
        error.target.responseURL + "\n\n" +
        error.target.getAllResponseHeaders();
    } else if (error instanceof Error) {
      error_text = error.toString();
    } else {
      error_text = JSON.stringify(error);
    }

    console.error(error);
    if (error instanceof Error) {
      console.error(error.stack);
    }
    if (gadget.props === undefined) {
      // Gadget has not yet been correctly initialized
      throw error;
    }

    return gadget.changeState({
      error_text: error_text,
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
  rJS(window)
    .setState({
      setting_id: "setting/" + document.head.querySelector(
        'script[data-renderjs-configuration="application_title"]'
      ).textContent
    })
    .ready(function () {
      var gadget = this,
        setting_gadget,
        setting;
      this.props = {
        loading_counter: 0,
        content_element: this.element.querySelector('.gadget-content')
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
      var jio_gadget,
        gadget = this,
        key = argument_list[0],
        value = argument_list[1];
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
          doc[key] = value;
          return jio_gadget.put(gadget.state.setting_id, doc);
        });
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
        route(this, "notification", 'notify', argument_list)
      ]);
    })
    .allowPublicAcquisition('notifySubmitted', function notifySubmitted(
      argument_list
    ) {
      return RSVP.all([
        route(this, "header", 'notifySubmitted'),
        route(this, "notification", 'notify', argument_list),
        route(this, "router", 'notify', argument_list)
      ]);
    })
    .allowPublicAcquisition('notifyChange', function notifyChange(
      argument_list
    ) {
      return RSVP.all([
        route(this, "header", 'notifyChange'),
        route(this, "notification", 'notify', argument_list),
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

    .allowPublicAcquisition('hidePanel', function hidePanel(param_list) {
      return hideDesktopPanel(this, param_list[0]);
    })
    .allowPublicAcquisition('triggerPanel', function triggerPanel() {
      return route(this, "panel", "toggle");
    })
    .allowPublicAcquisition('renderEditorPanel',
                            function renderEditorPanel(param_list) {
        return route(this, "editor_panel", 'render', param_list);
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
    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        route_result = gadget.state;

      if (modification_dict.hasOwnProperty('error_text')) {
        return gadget.dropGadget(MAIN_SCOPE)
          .push(undefined, function () {
            // Do not crash the app if the pg gadget in not defined
            // ie, keep the original error on screen
            return;
          })
          .push(function () {
            // XXX Improve error rendering
            gadget.props.content_element.innerHTML =
              "<br/><br/><br/><pre></pre>";
            gadget.props.content_element.querySelector('pre').textContent =
              "Error: " + gadget.state.error_text;
            // reset gadget state
            gadget.state = {};
            // XXX Notify error
          });
      }

      if (modification_dict.hasOwnProperty('url')) {
        return renderMainGadget(
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

              return RSVP.all([
                updateHeader(gadget),
                updatePanel(gadget)
              ]);
              // XXX Drop notification
              // return header_gadget.notifyLoaded();
            }
          });
      }

      // Same subgadget
      return gadget.getDeclaredGadget(MAIN_SCOPE)
        .push(function (page_gadget) {
          return page_gadget.render(gadget.state.options);
        })
        .push(function () {
          return RSVP.all([
            updateHeader(gadget),
            updatePanel(gadget)
          ]);
        });
    })
    // Render the page
    .declareMethod('render', function render(route_result, keep_message) {
      var gadget = this;

      // Reinitialize the loading counter
      gadget.props.loading_counter = 0;
      // By default, init the header options to be empty
      // (ERP5 title by default + sidebar)
      initHeaderOptions(gadget);
      initPanelOptions(gadget);
      return increaseLoadingCounter(gadget)
        .push(function () {
          var promise_list = [
            route(gadget, 'panel', 'close'),
            route(gadget, 'editor_panel', 'close'),
            route(gadget, 'router', 'notify', [{modified : false}])
          ];
          if (keep_message !== true) {
            promise_list.push(route(gadget, 'notification', 'close'));
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          return gadget.changeState({url: route_result.url,
                                     options: route_result.options});
        })
        .push(function () {
          return decreaseLoadingCounter(gadget);
        }, function (error) {
          return decreaseLoadingCounter(gadget)
            .push(function () {
              return displayError(gadget, error);
            });
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
    });

}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console, navigator, ProgressEvent));