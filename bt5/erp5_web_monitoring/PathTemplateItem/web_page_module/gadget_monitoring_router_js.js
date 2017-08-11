/*global window, rJS, loopEventListener, document, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, loopEventListener, document, RSVP) {
  "use strict";

  var gadget_klass = rJS(window),
    MAIN_PAGE_PREFIX = "gadget_monitoring_",
    DEFAULT_PAGE = "main",
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

    .declareMethod("getCommandUrlFor", function (options) {
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
      if (args.page === undefined || args.page === '') {
        args.page = DEFAULT_PAGE;
      }
      if (args.page === "view") {
        return {
          url: "gadget_monitoring_promise_interface.html",
          options: args
        };
      }
      return {
        url: MAIN_PAGE_PREFIX + args.page + ".html",
        options: args
      };
    })

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

}(window, rJS, loopEventListener, document, RSVP));