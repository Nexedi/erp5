/*globals window, document, RSVP, rJS, Handlebars,
          loopEventListener, jQuery, URI, location, XMLHttpRequest, console*/
/*jslint indent: 2, maxlen: 80*/
(function (window, document, RSVP, rJS, Handlebars, loopEventListener,
           $, XMLHttpRequest, location, console) {
  "use strict";

  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  var hateoas_url = "hateoas/",
    MAIN_SCOPE = "m",
    MAIN_PAGE_PREFIX = "gadget_gkr_";

  function updateHeader(gadget) {
    if (gadget.props.header_argument_list === undefined) {
      gadget.props.header_argument_list = {};
    }
    if (gadget.props.loading_counter === 0) {
      gadget.props.header_element.innerHTML =
        gadget.props.header_template(
          gadget.props.header_argument_list
        );
    } else {
      gadget.props.header_argument_list.loading_title =
        gadget.props.loading_title;
      gadget.props.header_element.innerHTML =
        gadget.props.sync_loader_template(
          gadget.props.header_argument_list
        );
    }
  }

  function increaseLoadingCounter(gadget) {
    return new RSVP.Queue()
      .push(function () {
        gadget.props.loading_counter += 1;
        if (gadget.props.loading_counter === 1) {
          return updateHeader(gadget);
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
          return updateHeader(gadget);
        }
      });
  }

  function callJioGadget(gadget, method, param_list) {
    var called = false;
    var jiogadget = null;
    var repair_retry_count_max = 10;
    var repair_retry_count = 0;

    function __callJioGadget(){
      return new RSVP.Queue()
        .push(function () {
          called = true;
          return increaseLoadingCounter(gadget);
        })
        .push(function () {
          return gadget.getDeclaredGadget("jio_gadget");
        })
        .push(function (jio_gadget) {
          jiogadget = jio_gadget;
          return jio_gadget[method].apply(jio_gadget, param_list);
        })
        .push(function (result) {
          if (method == "repair"){
            jiogadget.post({portal_type: "Sync Log", result: 1, time: new Date().getTime()});
            removeTemporaryBaseData(jiogadget);
            }
          return decreaseLoadingCounter(gadget)
            .push(function () {
              return result;
            });
        }, function (error) {
             if (method == "repair"){
               jiogadget.post({portal_type: "Sync Log", result: 0, time: new Date().getTime()});
               repair_retry_count++;
               console.log('sync retrying '+repair_retry_count)
               if (repair_retry_count < repair_retry_count_max){
                 return __callJioGadget();
               }
             }
             removeTemporaryBaseData(jiogadget);
             if (called) {
               return decreaseLoadingCounter(gadget)
               .push(function () {
                 throw error;
               });
             }
             throw error;
           });
    }
    return __callJioGadget();
  }

  function renderMainGadget(gadget, url, options) {
    return gadget.declareGadget(url, {
      scope: MAIN_SCOPE
    })
      .push(function (page_gadget) {
        var sub_options = options[MAIN_SCOPE] || {};
        delete options[MAIN_SCOPE];
        if (page_gadget.render === undefined) {
          return [page_gadget];
        }
        return RSVP.all([
          page_gadget,
          page_gadget.render(sub_options)
        ]);
      })
      .push(function (all_result) {
        return all_result[0];
      });
  }

  function renderPage(gadget, options) {
    console.log(options.page);
    return renderMainGadget(gadget,
                            MAIN_PAGE_PREFIX + "page_" + options.page + ".html",
                            options);
  }

  function renderJioPage(gadget, options) {
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
        return jio_gadget.get(options.jio_key);
      })
      .push(undefined, function (error) {
        // User has to initialize the app on the first access.
        if ((error !== undefined) && (error.status_code === 404)) {
          if (/_module$/.test(options.jio_key)) {
            return gadget.aq_pleasePublishMyState({page: "sync"})
              .push(gadget.pleaseRedirectMyHash.bind(gadget));
          }
        }
        throw error;
      })
      .push(function (doc) {
        var sub_options = {};
        sub_options[MAIN_SCOPE] = {
          doc: doc,
          jio_key: options.jio_key,
          search: options.search,
          begin_from: options.begin_from
        };
        var base_portal_type = doc.portal_type.toLowerCase().replace(/\s/g, "_")
        if (base_portal_type.search(/_temp$/) >= 0){
          base_portal_type = base_portal_type.substr(0, base_portal_type.length-5)//Remove "_temp"
        }
        return renderMainGadget(
          gadget,
          MAIN_PAGE_PREFIX + "jio_"
            + base_portal_type
            + "_" + options.page + ".html",
          sub_options
        );
      });
  }

  function displayErrorContent(gadget, error) {
    // Do not break the application in case of errors.
    // Display it to the user for now,
    // and allow user to go back to the frontpage
    var error_text = "";
    if ((error !== undefined) && (error.target !== undefined) && (error.target.status === 401)) {
      // Redirect to the login view
      return gadget.aq_pleasePublishMyState({page: "login"})
        .push(gadget.pleaseRedirectMyHash.bind(gadget));
    }
    if (error instanceof RSVP.CancellationError) {
      return;
    }

    if (error instanceof XMLHttpRequest) {
      error_text = error.toString() + " " +
        error.status + " " +
        error.statusText;
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
        return gadget.dropGadget("pg")
          .push(undefined, function () {
            // Do not crash the app if the pg gadget in not defined
            // ie, keep the original error on screen
            return;
          });
      });
  }


  //////////////////////////////////////////
  // History Support with Jio
  //////////////////////////////////////////
  function createJio(gadget, shared_gadget) {
    return gadget.getDeclaredGadget("jio_gadget")
      .push(function (jio_gadget) {
/*
        return jio_gadget.createJio({
          type: "erp5",
          url: (new URI(hateoas_url)).absoluteTo(location.href).toString(),
          default_view_reference: "jio_view"
        });
*/
        return jio_gadget.createJio({
          type: "replicate",
          // XXX This drop the signature lists...
          query: {
            query: 'portal_type:( ' +
              '"Product Module" ' +
              'OR "Organisation Module" ' +
              'OR "Purchase Record Module" ' +
              'OR "Purchase Record" ' +
              'OR "Purchase Price Record Module" ' +
              'OR "Purchase Price Record" ' +
              'OR "Sale Record Module" ' +
              'OR "Sale Record" ' +
              'OR "Sale Price Record Module" ' +
              'OR "Sale Price Record" ' +
              'OR "Inventory Move Record Module" ' +
              'OR "Inventory Move Record" ' +
              'OR "Production Record Module" ' +
              'OR "Production Record" ' +
              'OR "Daily Statement Record Module"' +
              'OR "Daily Statement Record"' +
              'OR "Report Item Module" ' +
              'OR "Report Item" ' +
              'OR "Report Total" ' +
              ') ' +
              'OR (portal_type:"Currency" AND validation_state:"validated") ' +
              'OR (portal_type:"Product" AND validation_state:("validated" OR "submitted")) ' +
              'OR (portal_type:"Organisation" AND validation_state:("validated" OR "submitted")) ' +
              'OR (portal_type:"Storage Node" AND validation_state:"validated") ' +
              'OR (portal_type:"Category" AND (   relative_url:"region/%" ' +
              '                                OR relative_url:"quantity_unit/%" ' +
              '                                OR relative_url:"product_line/%")) ' +
              'OR (portal_type:"Person" AND reference:"'+Cookies.get('jid')+'")',
            limit: [0, 1234567890]
          },
          use_remote_post: true,
          conflict_handling: 2,
          check_local_modification: false,
          check_local_creation: true,
          check_local_deletion: false,
          check_remote_modification: false,
          check_remote_creation: true,
          check_remote_deletion: true,
          local_sub_storage: {

            type: "rjs",
            gadget: shared_gadget,
            sub_storage: {

            type: "query",
            sub_storage: {
              type: "uuid",
              sub_storage: {
                type: "indexeddb",
                database: "erp5js_gkr_"+Cookies.get('jid')
              }
            }

            }
          },
          remote_sub_storage: {
            type: "erp5",
            url: (new URI(hateoas_url)).absoluteTo(location.href).toString(),
            default_view_reference: "jio_view"
          }
        });

      });
  }

  //////////////////////////////////////////
  // Page rendering
  //////////////////////////////////////////
  function redirectToDefaultPage(gadget) {
    // Redirect to expected page by default
    return gadget.aq_pleasePublishMyState({
      page: "setting"
    })
      .push(gadget.pleaseRedirectMyHash.bind(gadget));
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          $(element).trigger("create");
          g.props.loading_counter = 0;
          g.props.element = element;
          g.props.header_element = element.querySelector('.gadget-header')
                                          .querySelector('div');
          g.props.content_element = element.querySelector('.gadget-content');
          g.props.panel_element = element.querySelector('#mypanel');

          g.props.edit_template = Handlebars.compile(
            document.querySelector(".edit-template").innerHTML
          );
          g.props.header_template = Handlebars.compile(
            document.querySelector(".header-template").innerHTML
          );
          g.props.sync_loader_template = Handlebars.compile(
            document.querySelector(".sync-loader-template").innerHTML
          );
          g.props.panel_template = Handlebars.compile(
            document.querySelector(".panel-template").innerHTML
          );
        });
    })
    // Configure jIO storage
    .ready(function (g) {
//      return createJio(g);

      return g.getDeclaredGadget("shared_jio_gadget")
        .push(function (shared_gadget) {
          return createJio(g, shared_gadget);
        });

    })
    .ready(function (g) {
      return g.getDeclaredGadget('translation_gadget')
        .push(function (translation_gadget) {
          return RSVP.all([
            translation_gadget.translate('Loading'),
            translation_gadget.translate('Menu'),
            translation_gadget.translateHtml(g.props.panel_template())
          ]);
        })
        .push(function (string_list) {
          g.props.loading_title = string_list[0];
          g.props.header_element.parentElement.querySelector('a').textContent =
            string_list[1];
          g.props.panel_element.innerHTML = string_list[2];
          $(g.props.panel_element).enhanceWithin();
        });
    })

    //////////////////////////////////////////
    // Acquired method
    //////////////////////////////////////////
    .declareAcquiredMethod('pleaseRedirectMyHash', 'pleaseRedirectMyHash')

    //////////////////////////////////////////
    // Allow Acquisition
    //////////////////////////////////////////
    .allowPublicAcquisition("translateHtml", function (argument_list) {
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          return translation_gadget.translateHtml(argument_list[0]);
        });
    })
    .allowPublicAcquisition("translate", function (argument_list) {
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          return translation_gadget.translate(argument_list[0]);
        });
    })
    .allowPublicAcquisition("redirect", function (param_list) {
      var gadget = this;
      return gadget.aq_pleasePublishMyState.apply(gadget, param_list)
        .push(gadget.pleaseRedirectMyHash.bind(gadget));
    })
    .allowPublicAcquisition("getUrlFor", function (param_list) {
      return this.aq_pleasePublishMyState.apply(this, param_list);
    })
    .allowPublicAcquisition("updateHeader", function (param_list) {
      var gadget = this;
      return this.getDeclaredGadget("translation_gadget")
        .push(function (translation_gadget) {
          var promise_list = [];
          gadget.props.header_argument_list = param_list[0];

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
        });
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
    .allowPublicAcquisition("jio_repair", function (param_list) {
      return callJioGadget(this, "repair", param_list);
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    // Render the page
    .declareMethod('render', function (options) {
      var gadget = this;

      gadget.props.options = options;
      // Reinitialize the loading counter
      gadget.props.loading_counter = 0;
      return new RSVP.Queue()
        .push(function () {
          return increaseLoadingCounter(gadget);
        })
        .push(function () {
          $("#mypanel").panel("close");
          // By default, init the header options to be empty
          // (ERP5 title by default + sidebar)
          gadget.props.header_argument_list = [{
            title: gadget.props.application_title || "ERP5"
          }];

          if (options.jio_key === undefined) {
            if (options.page === undefined) {
              redirectToDefaultPage(gadget);
            } else {
              return renderPage(gadget, options);
            }
          } else {
            return renderJioPage(gadget, options);
          }
        })

        .push(function (main_gadget) {
          var input;
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

                updateHeader(gadget);

                // Clear first to DOM, append after to reduce flickering/manip
                while (element.firstChild) {
                  element.removeChild(element.firstChild);
                }
                content_container.appendChild(fragment);
                element.appendChild(content_container);

                $(element).trigger("create");

                input = element.querySelector("input");
                if (input !== null) {
                  input.focus();
                  input.select();
                }
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
/*
    .declareService(function () {
      ////////////////////////////////////
      // Appcache handling
      ////////////////////////////////////
      var gadget = this,
        appcache = window.applicationCache,
        // Wait 5 seconds by default
        delay = 5000,
        increase = 0,
        promise;

      function handleCacheError(error) {
        console.info('cache manifest update failed...');
        console.log(appcache.status);
        console.log(error);
        return new RSVP.Queue()
          .push(function () {
            // Increase delay after each try, to prevent killing the browser bandwith
            // 5 seconds, 10, 30, 2 minutes, 10 minutes, 1 hour...
            increase += 1;
            delay = delay * increase;
            return RSVP.delay(delay);
          })
          .push(function () {
            appcache.update();
          });
      }

      // Listen to form submit
      promise = loopEventListener(
        appcache,
        'error',
        false,
        handleCacheError
      );

      switch (appcache.status) {
      case appcache.UNCACHED:
        // UNCACHED == 0
        console.log('UNCACHED');
        // XXX reload needed
        break;
  case appcache.IDLE: // IDLE == 1
    console.log( 'IDLE');
    appcache.update();
    break;
  case appcache.CHECKING: // CHECKING == 2
    console.log( 'CHECKING');
    break;
  case appcache.DOWNLOADING: // DOWNLOADING == 3
    console.log( 'DOWNLOADING');
    break;
  case appcache.UPDATEREADY:  // UPDATEREADY == 4
    console.log( 'UPDATEREADY');
    break;
  case appcache.OBSOLETE: // OBSOLETE == 5
    console.log( 'OBSOLETE');
    appcache.update();
    break;
  default:
    console.log( 'UKNOWN CACHE STATUS');
    break;
};
//      appcache.update();
      return promise;
    });
*/

}(window, document, RSVP, rJS, Handlebars, loopEventListener, jQuery,
  XMLHttpRequest, location, console));