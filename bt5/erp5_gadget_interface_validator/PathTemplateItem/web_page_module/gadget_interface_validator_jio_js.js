/*global window, rJS, RSVP, jIO, QueryFactory, SimpleQuery, URL */
/*jslint indent: 2, maxerr: 3, nomen: true */
(function (window, rJS, RSVP, jIO, QueryFactory, SimpleQuery, URL) {
  "use strict";

  //////////////////////////////////////////////
  // Helpers
  //////////////////////////////////////////////
  function endsWith(str, suffix) {
    // http://simonwillison.net/2006/Jan/20/escape/
    suffix = suffix.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$&");
    return (new RegExp(suffix + '$', 'i')).test(str);
  }

  function fetchPrecacheData(precache_url) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: precache_url,
          dataType: 'json'
        });
      })
      .push(function (evt) {
        var key,
          precache_dict = evt.target.response,
          result_list = [],
          precache_absolute_url = (new URL(precache_url, window.location)).href;
        for (key in precache_dict) {
          if (precache_dict.hasOwnProperty(key)) {
            result_list.push((new URL(key, precache_absolute_url)).href);
          }
        }
        return result_list;
      });
  }

  function filterGadgetList(filename_list) {
    // XXX Filtering should be done instead by loading
    // each URL and report which one are correctly
    // loaded gadget
    var gadget_list = [],
      i;
    for (i = 0; i < filename_list.length; i += 1) {
      if (endsWith(filename_list[i], '.html') ||
          endsWith(filename_list[i], '/')) {
        gadget_list.push(filename_list[i]);
      }
    }
    return gadget_list;
  }


  function wrapJioCall(gadget, method_name, argument_list) {
    var storage = gadget.state_parameter_dict.jio_storage;

    return storage[method_name].apply(storage, argument_list);
  }

  //////////////////////////////////////////////
  // Storage
  //////////////////////////////////////////////
  function InterfaceValidatorStorage() {
    return;
  }

  InterfaceValidatorStorage.prototype.hasCapacity = function (name) {
    // XXX That's a lie
    // This can not do all this thing for now
    // But displaying the listbox requires those capacities
    return ((name === "list") || (name === "query") ||
            (name === "select") || (name === "limit") ||
            (name === "sort"));
  };

  InterfaceValidatorStorage.prototype.buildQuery = function (options) {
    // XXX HARDCODED
    var query = QueryFactory.create(options.query || '');
    if (!((query instanceof SimpleQuery) && (query.key === 'precache_url'))) {
      // Only accept simple query with an appcache_url
      return [];
    }
    return fetchPrecacheData(query.value)
    // return fetchAppcacheData('gadget_interface_validator_test.appcache')
      .push(function (filename_list) {
        return filterGadgetList(filename_list);
      })
      .push(function (url_list) {
        // XXX Sort to stabilize the tests
        url_list.sort();
        var result_list = [],
          i;
        for (i = 0; i < url_list.length; i += 1) {
          result_list.push({
            id: url_list[i],
            value: {url: url_list[i]},
            doc: {}
          });
        }
        return result_list;
      });
  };

  InterfaceValidatorStorage.prototype.get = function (id) {
    return {
      portal_type: 'Gadget URL Definition',
      url: id
    };
  };

  jIO.addStorage('interface_validator', InterfaceValidatorStorage);

  rJS(window)

    .ready(function (gadget) {
      return gadget.getDeclaredGadget('jio')
        .push(function (jio_gadget) {
          // Initialize the gadget local parameters
          gadget.state_parameter_dict = {jio_storage: jio_gadget};
        });
    })

    .declareMethod('createJio', function () {
      return this.state_parameter_dict.jio_storage.createJio({
        type: "interface_validator"
      });
    })

    .declareMethod('allDocs', function () {
      return wrapJioCall(this, 'allDocs', arguments);
    })
    .declareMethod('get', function () {
      return wrapJioCall(this, 'get', arguments);
    });

}(window, rJS, RSVP, jIO, QueryFactory, SimpleQuery, URL));