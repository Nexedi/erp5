/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  var gadget_klass = rJS(window),
    MAIN_PAGE_PREFIX = "gadget_officejs_",
    DEFAULT_PAGE = "hr_front",
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
      console.log('hr router render app');
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
      console.log('router ready');
      gadget.props = {
        start_deferred: RSVP.defer()
      };
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
        });
      console.log('router ready 2', gadget.props);
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
      if (options !== undefined && options.toExternal) {
        window.location.replace(options.url);
        return RSVP.timeout(REDIRECT_TIMEOUT); // timeout if not redirected
      }
      else {
        return this.getCommandUrlFor(options)
          .push(function (hash) {
            window.location.replace(hash);
            // prevent returning unexpected response
            // wait for the hash change to occur
            // fail if nothing happens
            return RSVP.timeout(REDIRECT_TIMEOUT);
          });
      }
    })

    .declareMethod('route', function (options) {
      var gadget = this,
        args = options.args;
      gadget.options = options;
      if (args.jio_key === undefined || args.jio_key === '') {
        if (args.page === undefined || args.page === '' || args.page === "hr_front") {
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
            search: args.search,
            came_from_jio_key: args.came_from_jio_key
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
      var gadget = this,
        element_list =
          gadget.props.element.querySelectorAll("[data-renderjs-configuration]"),
        len = element_list.length,
        key,
        value,
        i,
        queue = new RSVP.Queue();

      function push(a, b) {
        queue.push(function () {
          return gadget.setSetting(a, b);
        });
      }

      for (i = 0; i < len; i += 1) {
        key = element_list[i].getAttribute('data-renderjs-configuration');
        value = element_list[i].textContent;
        push(key, value);
      }
      console.log('router resolve start deferred');
      this.props.start_deferred.resolve();
    })
    .declareService(function () {
      console.log('router hr service');
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          console.log('router hr wait for start deferred', gadget.props.start_deferred.promise);
          return gadget.props.start_deferred.promise;
        })
        .push(function () {
          console.log('router hr listen hash change');
          return listenHashChange(gadget);
        })
        .push(undefined, function (error) {
          console.warn('router service', error);
          throw error;
        });
    });

}(window, rJS));