/*globals window, document, RSVP, rJS,
          jQuery, URI, location, XMLHttpRequest, console*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS, loopEventListener,
           $, XMLHttpRequest, location, console) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Desactivate jQuery Mobile URL management
  /////////////////////////////////////////////////////////////////
  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

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

  function route(my_root_gadget, my_scope, my_method, my_param_list) {
    return RSVP.Queue()
      .push(function () {
        return my_root_gadget.getDeclaredGadget(my_scope);
      })
      .push(function (my_gadget) {
        if (my_param_list) {
          return my_gadget[my_method].apply(my_gadget, my_param_list);
        }
        return my_gadget[my_method]();
      });
  }

  function updateHeader(gadget) {
    return gadget.getDeclaredGadget("header")
      .push(function (header_gadget) {
        return header_gadget.render(gadget.props.header_argument_list);
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
    if (error instanceof RSVP.CancellationError) {
      return;
    }

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
    // XXX Improve error rendering
    gadget.props.content_element.innerHTML = "<br/><br/><br/><pre></pre>";
    gadget.props.content_element.querySelector('pre').textContent =
      "Error: " + error_text;
    // XXX Notify error
  }

  function displayError(gadget, error) {
    return new RSVP.Queue()
      .push(function () {
        return displayErrorContent(gadget, error);
      })
      .push(function () {
        return gadget.dropGadget(MAIN_SCOPE)
          .push(undefined, function () {
            // Do not crash the app if the pg gadget in not defined
            // ie, keep the original error on screen
            return;
          });
      });
  }

  function getSetting(gadget, key, default_value) {
    return gadget.getDeclaredGadget("setting_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.get("setting");
      })
      .push(function (doc) {
        return doc[key] || default_value;
      }, function (error) {
        if (error.status_code === 404) {
          return default_value;
        }
        throw error;
      });
  }

  function setSetting(gadget, key, value) {
    var jio_gadget;
    return gadget.getDeclaredGadget("setting_gadget")
      .push(function (result) {
        jio_gadget = result;
        return jio_gadget.get("setting");
      })
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return {};
        }
        throw error;
      })
      .push(function (doc) {
        doc[key] = value;
        return jio_gadget.put('setting', doc);
      });
  }

  //////////////////////////////////////////
  // Page rendering
  //////////////////////////////////////////
  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          $(element).trigger("create");
          g.props.loading_counter = 0;
          g.props.element = element;
          g.props.content_element = element.querySelector('.gadget-content');
        });
    })
    // Configure setting storage
    .ready(function (g) {
      return g.getDeclaredGadget("setting_gadget")
        .push(function (jio_gadget) {
          return jio_gadget.createJio({
            type: "indexeddb",
            database: window.location.pathname + "setting"
          });
        });
    })
    .ready(function (g) {
      // Extract configuration parameters stored in HTML
      // XXX Will work only if top gadget...
      var element_list =
        document.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        key,
        value,
        i,
        queue = new RSVP.Queue();

      function push(a, b) {
        queue.push(function () {
          return setSetting(g, a, b);
        });
      }

      for (i = 0; i < len; i += 1) {
        key = element_list[i].getAttribute('data-renderjs-configuration');
        value = element_list[i].textContent;
        g.props[key] = value;
        push(key, value);
      }
      return queue;
    })
    .ready(function (g) {
      return setSetting(g, 'hateoas_url',
          (new URI(g.props.hateoas_url))
            .absoluteTo(location.href)
            .toString()
        );
    })
    // Configure jIO storage
    .ready(function (g) {
      var jio_gadget;
      return g.getDeclaredGadget("jio_gadget")
        .push(function (result) {
          jio_gadget = result;
          return getSetting(g, 'jio_storage_description');
        })
        .push(function (result) {
          return jio_gadget.createJio(result);
        });
    })
    .ready(function (g) {
      return g.getDeclaredGadget('panel')
        .push(function (panel_gadget) {
          return panel_gadget.render();
        });
    })
    .ready(function (g) {
      return g.getDeclaredGadget('router')
        .push(function (router_gadget) {
          return router_gadget.start();
        });
    })

    //////////////////////////////////////////
    // Allow Acquisition
    //////////////////////////////////////////
    .allowPublicAcquisition("getSetting", function (argument_list) {
      return getSetting(this, argument_list[0], argument_list[1]);
    })
    .allowPublicAcquisition("getSettingList",
                            function getSettingList(argument_list) {
        var key_list = argument_list[0];
        return route(this, 'setting_gadget', 'get', ['setting'])
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
    .allowPublicAcquisition("setSetting", function (argument_list) {
      return setSetting(this, argument_list[0], argument_list[1]);
    })
    .allowPublicAcquisition("translateHtml", function (argument_list) {
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          return translation_gadget.translateHtml(argument_list[0]);
        });
    })

    // XXX Those methods may be directly integrated into the header,
    // as it handles the submit triggering
    .allowPublicAcquisition('notifySubmitting', function () {
      return route(this, "header", 'notifySubmitting');
    })
    .allowPublicAcquisition('notifySubmitted', function () {
      return route(this, "header", "notifySubmitted");
    })
    .allowPublicAcquisition('notifyChange', function () {
      return route(this, "header", 'notifyChange');
    })

    .allowPublicAcquisition('refresh', function () {
      var gadget = this;
      return gadget.getDeclaredGadget(MAIN_SCOPE)
        .push(function (main) {
          if (main.render !== undefined) {
            return main.render(JSON.parse(gadget.props.m_options_string))
              .push(function () {
                $(gadget.props.content_element).trigger("create");
              });
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
    .allowPublicAcquisition("getTranslationList",
                            function getTranslationList(argument_list) {
        return route(this, 'translation_gadget', 'getTranslationList',
                     argument_list);
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
          return main_gadget.triggerSubmit(param_list);
        });
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .allowPublicAcquisition("renderApplication", function (param_list) {
      return this.renderXXX.apply(this, param_list);
    })
    // Render the page
    .declareMethod('renderXXX', function (options) {
      var gadget = this;

      gadget.props.options = options;
      // Reinitialize the loading counter
      gadget.props.loading_counter = 0;
      // By default, init the header options to be empty
      // (ERP5 title by default + sidebar)
      initHeaderOptions(gadget);
      return new RSVP.Queue()
        .push(function () {
          return increaseLoadingCounter(gadget);
        })
        .push(function () {
          return gadget.getDeclaredGadget('panel');
        })
        .push(function (panel_gadget) {
          return panel_gadget.close();
        })
        .push(function () {
          return gadget.getDeclaredGadget('editor_panel');
        })
        .push(function (editor_panel) {
          return editor_panel.close();
        })
        .push(function () {
          return gadget.getDeclaredGadget('router');
        })
        .push(function (router_gadget) {
          return router_gadget.route(options);
        })
        .push(function (route_result) {
          return renderMainGadget(
            gadget,
            route_result.url,
            route_result.options
          );
        })
        .push(function (main_gadget) {
          // Append loaded gadget in the page
          if (main_gadget !== undefined) {
            return main_gadget.getElement()
              .push(function (fragment) {
                var element = gadget.props.content_element,
                  content_container = document.createElement("div");
                content_container.className = "ui-content " +
                  (gadget.props.sub_header_class || "");
                // reset subheader indicator
                delete gadget.props.sub_header_class;

                // go to the top of the page
                window.scrollTo(0, 0);

                // Clear first to DOM, append after to reduce flickering/manip
                while (element.firstChild) {
                  element.removeChild(element.firstChild);
                }
                content_container.appendChild(fragment);
                element.appendChild(content_container);

                $(element).trigger("create");

                return updateHeader(gadget);
                // XXX Drop notification
                // return header_gadget.notifyLoaded();
              });
          }
        })
        .push(function () {
          return decreaseLoadingCounter(gadget);
        }, function (error) {
          return decreaseLoadingCounter(gadget)
            .push(function () {
              throw error;
            });
        })
        .push(undefined, function (error) {
          return displayError(gadget, error);
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

    .declareService(function () {
      ////////////////////////////////////
      // Form submit listening. Prevent browser to automatically
      // handle the form submit in case of a bug
      ////////////////////////////////////
      var gadget = this;

      function catchFormSubmit() {
        return displayError(gadget, new Error("Unexpected form submit"));
      }

      // Listen to form submit
      return loopEventListener(
        gadget.props.element,
        'submit',
        false,
        catchFormSubmit
      );
    });

}(window, document, RSVP, rJS, rJS.loopEventListener, jQuery,
  XMLHttpRequest, location, console));