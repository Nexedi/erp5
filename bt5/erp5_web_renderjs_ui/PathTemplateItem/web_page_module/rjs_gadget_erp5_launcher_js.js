/*globals window, document, RSVP, rJS,
          URI, location, XMLHttpRequest, console, navigator*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS,
           XMLHttpRequest, location, console, navigator) {
  "use strict";

  var MAIN_SCOPE = "m";

  function renderMainGadget(gadget, url, options) {
    return gadget.declareGadget(url, {
      scope: MAIN_SCOPE
    })
      .push(function (page_gadget) {
        gadget.props.m_options_string = JSON.stringify(options);
        if (page_gadget.render === undefined) {
          return [page_gadget];
        }
        return RSVP.all([
          page_gadget,
          page_gadget.render(options)
        ]);
      })
      .push(function (all_result) {
        return all_result[0];
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
    return RSVP.Queue()
      .push(function () {
        return my_root_gadget.getDeclaredGadget(my_scope);
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
    return gadget.getDeclaredGadget("panel")
      .push(function (panel_gadget) {
        return panel_gadget.render(gadget.props.panel_argument_list);
      });
  }

  function increaseLoadingCounter(gadget) {
    return new RSVP.Queue()
      .push(function () {
        gadget.props.loading_counter += 1;
        if (gadget.props.loading_counter === 1) {
          return gadget.getDeclaredGadget("header")
            .push(function (header_gadget) {
              return header_gadget.notifyLoading();
            });
        }
      });
  }

  function decreaseLoadingCounter(gadget) {
    return new RSVP.Queue()
      .push(function () {
        gadget.props.loading_counter -= 1;
        if (gadget.props.loading_counter < 0) {
          gadget.props.loading_counter = 0;
          // throw new Error("Unexpected negative loading counter");
        }
        if (gadget.props.loading_counter === 0) {
          return gadget.getDeclaredGadget("header")
            .push(function (header_gadget) {
              return header_gadget.notifyLoaded();
            });
        }
      });
  }

  function callJioGadget(gadget, method, param_list) {
    var called = false;
    return new RSVP.Queue()
      .push(function () {
        called = true;
        return increaseLoadingCounter(gadget);
      })
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

    if (error.target instanceof XMLHttpRequest) {
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
    .ready(function () {
      var gadget = this,
        setting_gadget,
        setting;
      this.props = {
        loading_counter: 0,
        content_element: this.element.querySelector('.gadget-content'),
        setting_id: "setting/" + document.head.querySelector(
          'script[data-renderjs-configuration="application_title"]'
        ).textContent
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

          return setting_gadget.get(gadget.props.setting_id)
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

          return setting_gadget.put(gadget.props.setting_id, setting);
        })
        .push(function () {
          // Configure jIO storage
          return gadget.getDeclaredGadget("jio_gadget");
        })

        .push(function (jio_gadget) {
          return jio_gadget.createJio(setting.jio_storage_description);
        })
        .push(function () {
          return gadget.getDeclaredGadget('panel');
        })
        .push(function (panel_gadget) {
          return panel_gadget.render({});
        })
        .push(function () {
          return gadget.getDeclaredGadget('router');
        })
        .push(function (router_gadget) {
          return router_gadget.start();
        });
    })

    //////////////////////////////////////////
    // Allow Acquisition
    //////////////////////////////////////////
    .allowPublicAcquisition("getSetting", function (argument_list) {
      var gadget = this,
        key = argument_list[0],
        default_value = argument_list[1];
      return gadget.getDeclaredGadget("setting_gadget")
        .push(function (jio_gadget) {
          return jio_gadget.get(gadget.props.setting_id);
        })
        .push(function (doc) {
          return doc[key] || default_value;
        }, function (error) {
          if (error.status_code === 404) {
            return default_value;
          }
          throw error;
        });
    })
    .allowPublicAcquisition("setSetting", function (argument_list) {
      var jio_gadget,
        gadget = this,
        key = argument_list[0],
        value = argument_list[1];
      return gadget.getDeclaredGadget("setting_gadget")
        .push(function (result) {
          jio_gadget = result;
          return jio_gadget.get(gadget.props.setting_id);
        })
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return {};
          }
          throw error;
        })
        .push(function (doc) {
          doc[key] = value;
          return jio_gadget.put(gadget.props.setting_id, doc);
        });
    })
    .allowPublicAcquisition("translateHtml", function (argument_list) {
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          return translation_gadget.translateHtml(argument_list[0]);
        });
    })

    // XXX Those methods may be directly integrated into the header,
    // as it handles the submit triggering
    .allowPublicAcquisition('notifySubmitting', function (argument_list) {
      return RSVP.all([
        route(this, "header", 'notifySubmitting'),
        route(this, "notification", 'notify', argument_list)
      ]);
    })
    .allowPublicAcquisition('notifySubmitted', function (argument_list) {
      return RSVP.all([
        route(this, "header", 'notifySubmitted'),
        route(this, "notification", 'notify', argument_list)
      ]);
    })
    .allowPublicAcquisition('notifyChange', function (argument_list) {
      return RSVP.all([
        route(this, "header", 'notifyChange'),
        route(this, "notification", 'notify', argument_list)
      ]);
    })

    .allowPublicAcquisition('refresh', function () {
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

    .allowPublicAcquisition("translate", function (argument_list) {
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          return translation_gadget.translate(argument_list[0]);
        });
    })

    .allowPublicAcquisition("redirect", function (param_list) {
      return this.getDeclaredGadget('router')
        .push(function (router_gadget) {
          return router_gadget.redirect.apply(router_gadget, param_list);
        });
    })
    .allowPublicAcquisition('reload', function () {
      return location.reload();
    })
    .allowPublicAcquisition("getUrlParameter", function (param_list) {
      return this.getDeclaredGadget('router')
        .push(function (router_gadget) {
          return router_gadget.getUrlParameter.apply(router_gadget, param_list);
        });
    })
    .allowPublicAcquisition("getUrlFor", function (param_list) {
      return this.getDeclaredGadget('router')
        .push(function (router_gadget) {
          return router_gadget.getCommandUrlFor.apply(router_gadget,
                                                      param_list);
        });
    })

    .allowPublicAcquisition("updateHeader", function (param_list) {
      var gadget = this;
      initHeaderOptions(gadget);
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          var promise_list = [],
            key;
          for (key in param_list[0]) {
            if (param_list[0].hasOwnProperty(key)) {
              gadget.props.header_argument_list[key] = param_list[0][key];
            }
          }

          promise_list.push(translation_gadget.translate(
            gadget.props.header_argument_list.title
          ));
          if (gadget.props.header_argument_list.hasOwnProperty('right_title')) {
            promise_list.push(translation_gadget.translate(
              gadget.props.header_argument_list.right_title
            ));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          gadget.props.header_argument_list.title = result_list[0];
          if (result_list.length === 2) {
            gadget.props.header_argument_list.right_title = result_list[1];
          }

          // XXX Sven hack: number of _url determine padding for
          // subheader on ui-content
          var key,
            count = 0;
          for (key in gadget.props.header_argument_list) {
            if (gadget.props.header_argument_list.hasOwnProperty(key)) {
              if (key.indexOf('_url') > -1) {
                count += 1;
              }
            }
          }
          if (count > 2) {
            gadget.props.sub_header_class = "ui-has-subheader";
          }
        });
    })

    .allowPublicAcquisition("updatePanel", function (param_list) {
      var gadget = this;
      initPanelOptions(gadget);
      gadget.props.panel_argument_list = param_list[0];
    })

    .allowPublicAcquisition('hidePanel', function (param_list) {
      return hideDesktopPanel(this, param_list[0]);
    })
    .allowPublicAcquisition('triggerPanel', function () {
      return route(this, "panel", "toggle");
    })
    .allowPublicAcquisition('renderEditorPanel', function (param_list) {
      return route(this, "editor_panel", 'render', param_list);
    })
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      return callJioGadget(this, "allDocs", param_list);
    })
    .allowPublicAcquisition("jio_remove", function (param_list) {
      return callJioGadget(this, "remove", param_list);
    })
    .allowPublicAcquisition("jio_post", function (param_list) {
      return callJioGadget(this, "post", param_list);
    })
    .allowPublicAcquisition("jio_put", function (param_list) {
      return callJioGadget(this, "put", param_list);
    })
    .allowPublicAcquisition("jio_get", function (param_list) {
      return callJioGadget(this, "get", param_list);
    })
    .allowPublicAcquisition("jio_allAttachments", function (param_list) {
      return callJioGadget(this, "allAttachments", param_list);
    })
    .allowPublicAcquisition("jio_getAttachment", function (param_list) {
      return callJioGadget(this, "getAttachment", param_list);
    })
    .allowPublicAcquisition("jio_putAttachment", function (param_list) {
      return callJioGadget(this, "putAttachment", param_list);
    })
    .allowPublicAcquisition("jio_removeAttachment", function (param_list) {
      return callJioGadget(this, "removeAttachment", param_list);
    })
    .allowPublicAcquisition("jio_repair", function (param_list) {
      return callJioGadget(this, "repair", param_list);
    })
    .allowPublicAcquisition("triggerSubmit", function (param_list) {
      return this.getDeclaredGadget(MAIN_SCOPE)
        .push(function (main_gadget) {
          return main_gadget.triggerSubmit.apply(main_gadget, param_list);
        });
    })
    .allowPublicAcquisition("triggerMaximize", function (param_list) {
      return triggerMaximize(this, param_list[0]);
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("renderApplication", function (param_list) {
      return this.render.apply(this, param_list);
    })
    .onStateChange(function (modification_dict) {
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
            gadget.props.content_element.innerHTML = "<br/><br/><br/><pre></pre>";
            gadget.props.content_element.querySelector('pre').textContent =
              "Error: " + gadget.state.error_text;
            // XXX Notify error
          });
      }

      if (modification_dict.hasOwnProperty('url')) {
        return new RSVP.Queue()
          .push(function () {
            return renderMainGadget(
              gadget,
              route_result.url,
              route_result.options
            );
          })
          .push(function (main_gadget) {
            // Append loaded gadget in the page
            if (main_gadget !== undefined) {
              var element = gadget.props.content_element,
                content_container = document.createDocumentFragment();
              // content_container.className = "ui-content " +
              //   (gadget.props.sub_header_class || "");
              // reset subheader indicator
              delete gadget.props.sub_header_class;

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
    .declareMethod('render', function (route_result, keep_message) {
      var gadget = this;

      // Reinitialize the loading counter
      gadget.props.loading_counter = 0;
      // By default, init the header options to be empty
      // (ERP5 title by default + sidebar)
      initHeaderOptions(gadget);
      initPanelOptions(gadget);
      return new RSVP.Queue()
        .push(function () {
          return increaseLoadingCounter(gadget);
        })
        .push(function () {
          var promise_list = [
            route(gadget, 'panel', 'close'),
            route(gadget, 'editor_panel', 'close')
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
              throw error;
            });
        });
    })

    /////////////////////////////////
    // Handle sub gadgets services
    /////////////////////////////////
    .allowPublicAcquisition('reportServiceError', function (param_list,
                                                            gadget_scope) {
      if (gadget_scope === undefined) {
        // don't fail in case of dropped subgadget (like previous page)
        return;
      }

      return displayError(this, param_list[0]);
    })

    .onEvent('submit', function () {
      return displayError(this, new Error("Unexpected form submit"));
    });

}(window, document, RSVP, rJS,
  XMLHttpRequest, location, console, navigator));