/*globals window, document, RSVP, rJS, Handlebars, promiseEventListener,
          loopEventListener, jQuery*/
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, $) {
  "use strict";

  $.mobile.ajaxEnabled = false;
  $.mobile.linkBindingEnabled = false;
  $.mobile.hashListeningEnabled = false;
  $.mobile.pushStateEnabled = false;

  var DEFAULT_PAGE = "upload",
    GADGET_SCOPE = "connection";

  function redirectToDefaultPage(gadget) {
    // Redirect to expected page by default
    return gadget.aq_pleasePublishMyState({page: DEFAULT_PAGE})
      .push(gadget.pleaseRedirectMyHash.bind(gadget));
  }

  function renderShowPage(gadget) {
    // we create a new show gadget here 
    return gadget.declareGadget('gadget_wendelin_show.html', {
      scope: GADGET_SCOPE, // is ok a gadget share same scope as another one ?
      element: gadget.props.connection_element
    })
        // Ivan: when promises of creating a sub gadget is done we call callback in .push
        // we use .push rather than .then due to cancel of RSVP written by romain
        .push(function (sub_gadget) {
          // we call render method which we defined on the gadget in a promise way
          // options already saved in gadgets' Ram representation
        var options = gadget.props.options;
        return sub_gadget.render(options);
      });
  }

  function renderUploadPage(gadget) {
    // we create a new Upload gadget here 
    return gadget.declareGadget('gadget_wendelin_upload.html', {
      scope: GADGET_SCOPE,
      element: gadget.props.connection_element
    })
      .push(function (sub_gadget) {
        // we call render method which we defined on the gadget in a promise way
        return sub_gadget.render();
      });
  }

  function renderListboxPage(gadget) {
    // we create a new listbox gadget here 
    return gadget.declareGadget('gadget_wendelin_listbox.html', {
      scope: GADGET_SCOPE,
      element: gadget.props.connection_element
    })
      .push(function (sub_gadget) {
        // we call render method which we defined on the gadget in a promise way
        return sub_gadget.render();
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      // g.getElement() is a promise but we need result of it
      return g.getElement()
        .push(function (result) {
          g.props.connection_element = result.querySelector(".gadget-content");
          g.props.link_element = result.querySelector(".alldoclink");
          g.props.upload_link_element = result.querySelector(".uploadlink");
        });
    })
    // Configure jIO to use localstorage
    .ready(function (g) {
      return g.getDeclaredGadget("JIO")
        .push(function (gadget) {
          return gadget.createJio({
            type:  "query",
            sub_storage: {
              type: "indexeddb",
              document_id: "/",
              database: "test_ivan"
            }
          });
        });
    })
    .ready(function (g) {
      return g.aq_pleasePublishMyState({page: 'listbox'})
        .push(function (url) {
           g.props.link_element.href = url;
         })
         .push (function() {
           return g.aq_pleasePublishMyState({page: 'upload'})
         })
         .push(function (url) {
           g.props.upload_link_element.href = url;
         });
    })

    //////////////////////////////////////////
    // Acquired method
    //////////////////////////////////////////
    .declareAcquiredMethod('pleaseRedirectMyHash', 'pleaseRedirectMyHash')
    .allowPublicAcquisition("goAndSaveToHistory", function (param_list) {
      window.location = param_list[0];
    })
    .allowPublicAcquisition("jio_allDocs", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.allDocs.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_post", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.post.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_put", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.put.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("aq_putAttachment", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.putAttachment.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("jio_get", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.get.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("aq_getAttachment", function (param_list) {
      return this.getDeclaredGadget("JIO")
        .push(function (jio_gadget) {
          return jio_gadget.getAttachment.apply(jio_gadget, param_list);
        });
    })
    .allowPublicAcquisition("whoWantsToDisplayThisDocument",
      function (param_list) {
        // Hey, I want to display some jIO document
        var kw = {
            page: param_list[1] || "upload"
          };
        if (param_list[0] !== undefined) {
          kw.id = param_list[0];
        }
        return this.aq_pleasePublishMyState(kw);
      })

    //////////////////////////////////////////
    // Declare method (methods of the gadget!)
    //////////////////////////////////////////
    .declareMethod('render', function (options) {
      var result,
        gadget = this,
        element = gadget.props.connection_element;

      gadget.props.options = options;

      // do clean up old DOM element's contents
      while (element.firstChild) {
        element.removeChild(element.firstChild);
      }

      // based on page parameter show respective sub gadget inside same page
      if (options.page === undefined) {
        result = redirectToDefaultPage(this);
      } else if (options.page === 'upload') {
        // show an upload page
        result = renderUploadPage(gadget);
      } else if (options.page === 'listbox') {
        // show an upload page
        result = renderListboxPage(this);
      } else if (options.page === 'show') {
        // show an upload page (ivan)
        result = renderShowPage(this);
      } else {
        throw new Error(options.page);
      }

      return result
        // Let JQM know it has to render this
        .push(function () {
          $(gadget.props.element).trigger("create");
        })
        .push(undefined, function (error) {
          // XXX Improve renderJS error class
          if ((error instanceof Error) &&
              (error.message === "Gadget scope '" +
                                 GADGET_SCOPE +
                                 "' is not known.")) {
            // redirec to default page
            return gadget.aq_pleasePublishMyState({page: DEFAULT_PAGE})
              .push(gadget.pleaseRedirectMyHash.bind(gadget));
          }
          throw error;
        });
    });

}(window, rJS, jQuery));