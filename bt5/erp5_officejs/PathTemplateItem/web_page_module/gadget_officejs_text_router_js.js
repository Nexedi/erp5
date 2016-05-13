/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('gadget_officejs_text_serviceworker.js')
    .then(function (reg) {
      // registration worked
      console.log('Registration succeeded. Scope is ' + reg.scope);
    })
    .then(undefined, function (error) {
      // registration failed
      console.log('Registration failed with ' + error);
    });
  }

  var gadget_klass = rJS(window),
    MAIN_PAGE_PREFIX = "gadget_officejs_",
    DEFAULT_PAGE = "text_list",
    REDIRECT_TIMEOUT = 5000;

  function listenHashChange(gadget) {
    function extractHashAndDispatch(evt) {
      var hash = (evt.newURL || window.location.toString()).split('#')[1],
        subhashes,
        subhash,
        keyvalue,
        index,
        args = {};
      if (hash !== undefined) {
        subhashes = hash.split('&');
        for (index in subhashes) {
          if (subhashes.hasOwnProperty(index)) {
            subhash = subhashes[index];
            if (subhash !== '') {
              keyvalue = subhash.split('=');
              if (keyvalue.length === 2) {
                args[decodeURIComponent(keyvalue[0])] = decodeURIComponent(keyvalue[1]);
              }
            }
          }
        }
      }

      return gadget.renderApplication({
        args: args
      });

    }

    var result = loopEventListener(window, 'hashchange', false,
                                   extractHashAndDispatch),
      event = document.createEvent("Event");
    event.initEvent('hashchange', true, true);
    event.newURL = window.location.toString();
    window.dispatchEvent(event);
    return result;
  }

  gadget_klass

    .ready(function (gadget) {
      gadget.props = {
        start_deferred: RSVP.defer()
      };
    })

    .declareMethod("getCommandUrlFor", function(options) {
      var prefix = '',
        result,
        key;
      result = "#";
      for (key in options) {
        if (options.hasOwnProperty(key) && options[key] !== undefined) {
          // Don't keep empty values
          result += prefix + encodeURIComponent(key) + "=" + encodeURIComponent(options[key]);
          prefix = '&';
        }
      }
      return result;
    })

    .declareMethod('redirect', function (options) {
      return this.getCommandUrlFor(options)
        .push(function (hash) {
          window.location.replace(hash);
          // prevent returning unexpected response
          // wait for the hash change to occur
          // fail if nothing happens
          return RSVP.timeout(REDIRECT_TIMEOUT);
        });
    })

    .declareMethod('route', function (options) {
      var gadget = this,
        args = options.args;
      gadget.options = options;
      if (args.jio_key === undefined || args.jio_key === '') {
        if (args.page === undefined || args.page === '' || args.page === "document_list") {
          args.page = DEFAULT_PAGE;
        }
        return {
          url: MAIN_PAGE_PREFIX + "page_" + args.page + ".html",
          options: args
        };
      }
      return gadget.jio_get(args.jio_key)
        .push(function (doc) {
          var sub_options = {},
            base_portal_type = doc.portal_type.toLowerCase().replace(/\s/g, "_");
          sub_options = {
            doc: doc,
            jio_key: args.jio_key,
            search: args.search
          };
          if (base_portal_type.search(/_temp$/) >= 0) {
            //Remove "_temp"
            base_portal_type = base_portal_type.substr(
              0,
              base_portal_type.length - 5
            );
          }
          return {
            url: MAIN_PAGE_PREFIX + "jio_"
              + base_portal_type
              + "_" + args.page + ".html",
            options: sub_options
          };
        });
    })
    
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('renderApplication', 'renderApplication')
    .declareMethod('start', function () {
      this.props.start_deferred.resolve();
    })
    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.start_deferred.promise;
        })
        .push(function () {
          return listenHashChange(gadget);
        });
    });

}(window, rJS));