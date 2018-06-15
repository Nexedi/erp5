/*global window, rJS, document, loopEventListener, RSVP */
/*jslint nomen: true, indent: 2, maxlen: 80 */
(function (window, rJS, document, loopEventListener, RSVP) {
  "use strict";

  var MAIN_PAGE_PREFIX = "gadget_interface_validator_",
    DEFAULT_PAGE = "form",
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
                args[decodeURIComponent(keyvalue[0])] =
                  decodeURIComponent(keyvalue[1]);
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

  rJS(window)
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
          result += prefix + encodeURIComponent(key) + "=" +
            encodeURIComponent(options[key]);
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
      var args = options.args,
        page;

      page = args.page || DEFAULT_PAGE;
      return {
        url: MAIN_PAGE_PREFIX + "page_" + page + ".html",
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

}(window, rJS, document, loopEventListener, RSVP));