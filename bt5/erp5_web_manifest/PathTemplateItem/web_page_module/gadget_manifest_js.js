/*global window, document, rJS, RSVP, jQuery, console, jQuery, XMLHttpRequest, loopEventListener, URI, location */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, document, rJS, RSVP, $, XMLHttpRequest, console, loopEventListener, location) {
  "use strict";

  var DEFAULT_VIEW_REFERENCE = "view";

  /////////////////////////////////////////////////////////////////
  // Desactivate jQuery Mobile URL management
  /////////////////////////////////////////////////////////////////
  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  /////////////////////////////////////////////////////////////////
  // Some functions
  /////////////////////////////////////////////////////////////////
  function mergeSubDict(dict) {
    var subkey,
      subkey2,
      subresult2,
      value,
      result = {};
    for (subkey in dict) {
      if (dict.hasOwnProperty(subkey)) {
        value = dict[subkey];
        if (value instanceof Object) {
          subresult2 = mergeSubDict(value);
          for (subkey2 in subresult2) {
            if (subresult2.hasOwnProperty(subkey2)) {
              // XXX key should not have an . inside
              if (result.hasOwnProperty(subkey + "." + subkey2)) {
                throw new Error("Key " + subkey + "." +
                                subkey2 + " already present");
              }
              result[subkey + "." + subkey2] = subresult2[subkey2];
            }
          }
        } else {
          if (result.hasOwnProperty(subkey)) {
            throw new Error("Key " + subkey + " already present");
          }
          result[subkey] = value;
        }
      }
    }
    return result;
  }

  function listenHashChange(gadget) {

    function extractHashAndDispatch(evt) {
      var hash = (evt.newURL || window.location.toString()).split('#')[1],
        subhashes,
        subhash,
        keyvalue,
        index,
        options = {};
      if (hash === undefined) {
        hash = "";
      } else {
        hash = hash.split('?')[0];
      }

      function optionalize(key, value, dict) {
        var key_list = key.split("."),
          kk,
          i;
        for (i = 0; i < key_list.length; i += 1) {
          kk = key_list[i];
          if (i === key_list.length - 1) {
            dict[kk] = value;
          } else {
            if (!dict.hasOwnProperty(kk)) {
              dict[kk] = {};
            }
            dict = dict[kk];
          }
        }
      }

      subhashes = hash.split('&');
      for (index in subhashes) {
        if (subhashes.hasOwnProperty(index)) {
          subhash = subhashes[index];
          if (subhash !== '') {
            keyvalue = subhash.split('=');
            if (keyvalue.length === 2) {

              optionalize(decodeURIComponent(keyvalue[0]),
                decodeURIComponent(keyvalue[1]),
                options);

            }
          }
        }
      }

      if (gadget.renderXXX !== undefined) {
        return gadget.renderXXX(options);
      }
    }

    var result = loopEventListener(window, 'hashchange', false,
                                   extractHashAndDispatch),
      event = document.createEvent("Event");

    event.initEvent('hashchange', true, true);
    event.newURL = window.location.toString();
    window.dispatchEvent(event);
    return result;
  }

  function renderPage(gadget, page_name, options) {
    return gadget.declareGadget(page_name, {
      scope: "pg"
    })
      .push(function (page_gadget) {
        var sub_options = options.pg || {},
          key;
        delete options.pg;
        for (key in options) {
          if (options.hasOwnProperty(key)) {
            sub_options[key] = options[key];
          }
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

  function displayErrorContent(gadget, error) {
    // Do not break the application in case of errors.
    // Display it to the user for now, and allow user to go back to the frontpage
    var error_text = "";
    if ((error.target !== undefined) && (error.target.status === 401)) {
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
    console.error(error.stack);
    // XXX Improve error rendering
    gadget.props.article.innerHTML = "<br/><br/><br/><pre></pre>";
    gadget.props.article.querySelector('pre').textContent = "Error: " + error_text;
  }

  function displayError(gadget, error) {
    return gadget.getDeclaredGadget("header")
      .push(function (g) {
        return g.notifyError();
      })
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

  /////////////////////////////////////////////////////////////////
  // Gadget behaviour
  /////////////////////////////////////////////////////////////////

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {
        translation_lookup: ""
      };
//      return g.getDeclaredGadget("breadcrumb")
//        .push(function (sub_gadget) {
//          g.props.breadcrumb_gadget = sub_gadget;
//        });
    })

    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
          g.props.article = element.querySelector("article");

          // XXX Will work only if top gadget...
          var element_list = document.querySelectorAll("[data-renderjs-configuration]"),
            len = element_list.length,
            key,
            value,
            i;

          for (i = 0; i < len; i += 1) {
            key = element_list[i].getAttribute('data-renderjs-configuration');
            value = element_list[i].textContent;
            if (value !== "") {
              g.props[key] = value;
            }
          }
        });
    })

    .declareMethod("aq_pleasePublishMyState", function (options) {
      var key,
        first = true,
        hash = "#";
      options = mergeSubDict(options);
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (!first) {
            hash += "&";
          }
          hash += encodeURIComponent(key) + "=" +
            encodeURIComponent(options[key]);
          first = false;
        }
      }
      return hash;
    })

    /////////////////////////////////////////////////////////////////
    // handle acquisition
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("pleaseRedirectMyHash", "pleaseRedirectMyHash")

    // bridge translation gadget
    .allowPublicAcquisition("getTranslationMethod", function () {
      var root = (new URI(this.props.hateoas_url)).absoluteTo(location.href).toString();
      return root + this.props.translation_lookup;
    })
    .allowPublicAcquisition("changeLanguage", function (param_list) {
      if (this.setLanguage) {
        return this.getDeclaredGadget("translate")
          .push(function (translation_gadget) {
            return translation_gadget.changeLanguage.apply(
              translation_gadget,
              param_list
            );
          });
      }
    })
    .allowPublicAcquisition("getLanguageList", function (param_list) {
      if (this.setLanguage) {
        return this.getDeclaredGadget("translate")
          .push(function (translation_gadget) {
            return translation_gadget.getLanguageList.apply(
              translation_gadget,
              param_list
            );
          });
      }
      return JSON.stringify([]);
    })
    .allowPublicAcquisition("translateHtml", function (param_list) {
      if (this.setLanguage) {
        return this.getDeclaredGadget("translate")
          .push(function (translation_gadget) {
            return translation_gadget.translateHtml.apply(
              translation_gadget,
              param_list
            );
          });
      }
      return param_list;
    })
    .allowPublicAcquisition("translate", function (param_list) {
      if (this.setLanguage) {
        return this.getDeclaredGadget("translate")
          .push(function (translation_gadget) {
            return translation_gadget.translate.apply(
              translation_gadget,
              param_list
            );
          });
      }
      return param_list;
    })
    .allowPublicAcquisition("getTranslationList", function (param_list) {
      if (this.setLanguage) {
        return this.getDeclaredGadget("translate")
          .push(function (translation_gadget) {
            return translation_gadget.getTranslationList.apply(
              translation_gadget,
              param_list
            );
          });
      }
      return param_list;
    })

    .allowPublicAcquisition("whoWantToDisplayThis", function (param_list) {
      // Hey, I want to display some URL
      var options = {
        jio_key: param_list[0],
        view: DEFAULT_VIEW_REFERENCE
      };
      if (param_list[1] !== undefined) {
        if (param_list[1].editable !== undefined) {
          options.editable = param_list[1].editable;
        }
      }
      return this.aq_pleasePublishMyState(options);
    })
    .allowPublicAcquisition("whoWantToDisplayThisPage", function (param_list) {
      // Hey, I want to display some URL
      var options = {
        jio_key: this.state_parameter_dict.jio_key,
        view: param_list[0].name || DEFAULT_VIEW_REFERENCE
      };
      if (param_list[0].editable !== undefined) {
        options.editable = param_list[0].editable;
      }
      if (param_list[0].page !== undefined) {
        options.page = param_list[0].page;
      }
      return this.aq_pleasePublishMyState(options);
    })
    .allowPublicAcquisition("whoWantToDisplayThisFrontPage", function (param_list) {
      // Hey, I want to display some URL
      var options = {
        page: param_list[0]
      };
      return this.aq_pleasePublishMyState(options);
    })

    .allowPublicAcquisition("renderPageHeader", function (param_list) {
      // XXX Sven hack: number of _url determine padding for subheader on ui-content 
      function hasSubNavigation(my_param_dict) {
        var i,
          count = 0;
        for (i in my_param_dict) {
          if (my_param_dict.hasOwnProperty(i) && i.indexOf("_url") > -1) {
            count += 1;
          }
        }
        return count;
      }

      if (hasSubNavigation(param_list[0]) > 2) {
        this.props.sub_header_class = "ui-has-subheader";
      }
      this.props.header_argument_list = param_list;
    })

    .allowPublicAcquisition('reportServiceError', function (param_list, gadget_scope) {
      if (gadget_scope === undefined) {
        // don't fail in case of dropped subgadget (like previous page)
        // only accept errors from header, panel and displayed page
        return;
      }
      return displayError(this, param_list[0]);
    })
    // XXX translate: while header calls render on ready, this is needed to
    // update the header once translations are available
    .allowPublicAcquisition('notifyUpdate', function () {
      return this.getDeclaredGadget("header")
        .push(function (header_gadget) {
          return header_gadget.notifyUpdate();
        });
    })
    .allowPublicAcquisition('notifySubmitting', function () {
      return this.getDeclaredGadget("header")
        .push(function (header_gadget) {
          return header_gadget.notifySubmitting();
        });
    })

    .allowPublicAcquisition('notifySubmitted', function () {
      return this.getDeclaredGadget("header")
        .push(function (header_gadget) {
          return header_gadget.notifySubmitted();
        });
    })
    .allowPublicAcquisition('notifyChange', function () {
      return this.getDeclaredGadget("header")
        .push(function (header_gadget) {
          return header_gadget.notifyChange();
        });
    })
    .allowPublicAcquisition('triggerSubmit', function () {
      return this.getDeclaredGadget("pg")
        .push(function (page_gadget) {
          return page_gadget.triggerSubmit();
        });
    })
    .allowPublicAcquisition('triggerPanel', function () {
      return this.getDeclaredGadget("panel")
        .push(function (panel_gadget) {
          return panel_gadget.toggle();
        });
    })
    .allowPublicAcquisition('getSiteRoot', function () {
      return this.getSiteRoot();
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    // XXX translate: called before ready(), so props is not available.
    // Needed to lookup to retrieve HAL to fetch site module/runner languages 
    .declareMethod('getSiteRoot', function () {
      return (new URI(this.props.hateoas_url)).absoluteTo(location.href).toString();
    })

    // Render the page
    .declareMethod('configure', function (options) {
      var gadget = this,
        elements,
        div,
        key;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (key === "translation_lookup") {
            gadget.setLanguage = true;
          }
          gadget.props[key] = options[key];
        }
      }
      if (gadget.setLanguage) {
        elements = gadget.props.element;
        div = document.createElement("div");
        elements.appendChild(div);
        return new RSVP.Queue()
          .push(function () {
            return gadget.declareGadget("gadget_translate.html",
                                        {scope: "translate"});
          })
          .push(function () {
            return gadget.dropGadget("panel");
          })
          .push(function () {
            return gadget.declareGadget(gadget.props.panel_gadget,
                                         {scope: "panel",
                                          element: div});
          })
          .push(function () {
            return createJio(gadget);
          });
      }
    })

    // Render the page
    .declareMethod('renderXXX', function (options) {
      var gadget = this,
        header_gadget,
        panel_gadget,
        main_gadget;

      gadget.props.options = options;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget("header"),
            gadget.getDeclaredGadget("panel")
          ]);
        })
        .push(function (my_gadget_list) {
          header_gadget = my_gadget_list[0];
          panel_gadget = my_gadget_list[1];
          return RSVP.all([
            panel_gadget.render({}),
            header_gadget.notifyLoading()
          ]);
        })
        .push(function () {
          // By default, init the header options to be empty (ERP5 title by default + sidebar)
          gadget.props.header_argument_list = [{
            panel_action: true,
            page_title: gadget.props.application_title || "ERP5"
          }];

          gadget.state_parameter_dict = {
            jio_key: options.jio_key,
            view: options.view
          };

          if ((options.jio_key !== undefined) && (options.page === undefined)) {
            options.page = "form";
            options.view = options.view || DEFAULT_VIEW_REFERENCE;
          }
          if (options.page === undefined) {
            // Not rendering a jio document and not page requested.
            // URL is probably empty: redirect to the frontpage
            // Check if a custom frontpage is defined
            if (!gadget.props.frontpage_gadget) {
              return gadget.aq_pleasePublishMyState({page: 'front'})
                .push(gadget.pleaseRedirectMyHash.bind(gadget));
            }
            return renderPage(gadget, gadget.props.frontpage_gadget, options);
          }

          return renderPage(gadget, "gadget_manifest_page_" + options.page + ".html", options);
        })

        .push(function (result) {
          main_gadget = result;

          return header_gadget.render.apply(header_gadget, gadget.props.header_argument_list);
        })
        .push(function () {
          // Append loaded gadget in the page
          if (main_gadget !== undefined) {
            return main_gadget.getElement()
              .push(function (fragment) {
                var element = gadget.props.article,
                  content_container = document.createElement("div");
                content_container.className = "ui-content " + (gadget.props.sub_header_class || "");
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
                return header_gadget.notifyLoaded();
              });
          }
        })

        .push(undefined, function (error) {
          return displayError(gadget, error);
        });
    })

    .declareService(function () {
      ////////////////////////////////////
      // Form submit listening. Prevent browser to automatically handle the form submit in case of a bug
      ////////////////////////////////////
      var gadget = this;

      function catchFormSubmit() {
        return displayError(new Error("Unexpected form submit"));
      }

      // Listen to form submit
      return loopEventListener(
        gadget.props.element,
        'submit',
        false,
        catchFormSubmit
      );
    })


    .declareService(function () {
      return listenHashChange(this);
    });

}(window, document, rJS, RSVP, jQuery, XMLHttpRequest, console, loopEventListener, location));