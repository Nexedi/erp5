/*global window, rJS, loopEventListener, document, RSVP, URL */
/*jslint nomen: true*/
/*jslint indent: 2, maxlen: 80*/
(function (window, rJS) {
  "use strict";

  // Keep reference of the latest allDocs params which reach to this view
  // var SELECTION_KEY = "s",
  // Keep reference in the global navigation pattern
  // HISTORY KEY = "h"
  // Current display parameter
  // DISPLAY KEY = "d"
  var MAIN_PAGE_PREFIX = "gadget_trade_",
    PREVIOUS_KEY = "p",
    NEXT_KEY = "n",
    DROP_KEY = "u",
    PREFIX_DISPLAY = "/",
    PREFIX_COMMAND = "!",
    // PREFIX_ERROR = "?",
    COMMAND_DISPLAY_STATE = "display",
    COMMAND_LOGIN = "login",
    COMMAND_RAW = "raw",
    COMMAND_RELOAD = "reload",
    COMMAND_DISPLAY_STORED_STATE = "display_stored_state",
    COMMAND_CHANGE_STATE = "change",
    COMMAND_STORE_AND_CHANGE_STATE = "store_and_change",
    COMMAND_INDEX_STATE = "index",
    COMMAND_SELECTION_PREVIOUS = "selection_previous",
    COMMAND_SELECTION_NEXT = "selection_next",
    COMMAND_HISTORY_PREVIOUS = "history_previous",
    COMMAND_PUSH_HISTORY = "push_history",
    REDIRECT_TIMEOUT = 5000,
    VALID_URL_COMMAND_DICT = {};
  VALID_URL_COMMAND_DICT[COMMAND_DISPLAY_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_DISPLAY_STORED_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_CHANGE_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_STORE_AND_CHANGE_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_INDEX_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_SELECTION_PREVIOUS] = null;
  VALID_URL_COMMAND_DICT[COMMAND_SELECTION_NEXT] = null;
  VALID_URL_COMMAND_DICT[COMMAND_HISTORY_PREVIOUS] = null;
  VALID_URL_COMMAND_DICT[COMMAND_PUSH_HISTORY] = null;
  VALID_URL_COMMAND_DICT[COMMAND_LOGIN] = null;
  VALID_URL_COMMAND_DICT[COMMAND_RAW] = null;
  VALID_URL_COMMAND_DICT[COMMAND_RELOAD] = null;



  function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
  }
  //////////////////////////////////////////////////////////////////
  // Change URL functions
  //////////////////////////////////////////////////////////////////
  function changeState(hash) {
    // window.location = hash;
    return window.location.replace(hash);
  }

  function synchronousChangeState(hash) {
    changeState(hash);
    // prevent returning unexpected response
    // wait for the hash change to occur
    // fail if nothing happens
    return RSVP.timeout(REDIRECT_TIMEOUT);
  }

  //////////////////////////////////////////////////////////////////
  // Build URL functions
  //////////////////////////////////////////////////////////////////
  function getCommandUrlFor(gadget, command, options) {
    if (command === COMMAND_RAW) {
      return options.url;
    }
    var result = "#" + PREFIX_COMMAND + (command || ""),
      prefix = "?",
      key,
      tmp,
      tmp_dict;
    tmp_dict = gadget.props.options;
    for (key in tmp_dict) {
      if (tmp_dict.hasOwnProperty(key) && (tmp_dict[key] !== undefined)) {
        tmp = tmp_dict[key];
        if (endsWith(key, ":json")) {
          tmp = JSON.stringify(tmp);
        }
        result += prefix + PREVIOUS_KEY + "." +
          encodeURIComponent(key) + "=" + encodeURIComponent(tmp);
        prefix = "&";
      }
    }
    for (key in options) {
      if (options.hasOwnProperty(key)) {
        tmp = options[key];
        if (tmp === undefined) {
          // Key should be dropped from the URL
          result += prefix + DROP_KEY + "." + encodeURIComponent(key) + "=";
        } else {
          if (endsWith(key, ":json")) {
            tmp = JSON.stringify(tmp);
          }
          result += prefix + NEXT_KEY + "." +
            encodeURIComponent(key) + "=" + encodeURIComponent(tmp);
        }
        prefix = "&";
      }
    }
    if (command === COMMAND_LOGIN) {
      // Build URL template to allow getting user information
      result += '{' + prefix + 'n.me}';
    }
    return result;
  }


  function getDisplayUrlFor(jio_key, options) {
    var prefix = '?',
      result,
      tmp,
      key;
    result = "#" + PREFIX_DISPLAY + (jio_key || "");
    for (key in options) {
      if (options.hasOwnProperty(key) && options[key] !== undefined) {
        // Don't keep empty values
        tmp = options[key];
        if (endsWith(key, ":json")) {
          tmp = JSON.stringify(tmp);
        }
        result += prefix + encodeURIComponent(key) +
          "=" + encodeURIComponent(tmp);
        prefix = '&';
      }
    }
    return result;
  }

   //////////////////////////////////////////////////////////////////
  // exec command functions
  //////////////////////////////////////////////////////////////////
  function calculateChangeOptions(previous_options,
    next_options, drop_options) {
    var key;
    for (key in previous_options) {
      if (previous_options.hasOwnProperty(key)) {
        if (!next_options.hasOwnProperty(key)) {
          next_options[key] = previous_options[key];
        }
      }
    }
    for (key in drop_options) {
      if (drop_options.hasOwnProperty(key)) {
        delete next_options[key];
      }
    }
    return next_options;
  }


  function execDisplayCommand(next_options) {
    // console.warn(command_options);
    var jio_key = next_options.jio_key,
      hash;
    delete next_options.jio_key;

    hash = getDisplayUrlFor(jio_key, next_options);
    return new RSVP.Queue()
      .push(function () {
        return synchronousChangeState(hash);
      });
  }

  function execIndexCommand(next_options) {
    // console.warn(command_options);
    var jio_key = next_options.jio_key,
      hash;
    delete next_options.jio_key;
    next_options.page = "view";

    hash = getDisplayUrlFor(jio_key, next_options);
    return new RSVP.Queue()
      .push(function () {
        return synchronousChangeState(hash);
      });
  }


  function execChangeCommand(previous_options, next_options, drop_options) {
    var options,
      jio_key,
      hash;
    options = calculateChangeOptions(previous_options,
      next_options, drop_options);

    jio_key = options.jio_key;
    delete options.jio_key;
    hash = getDisplayUrlFor(jio_key, options);
    return new RSVP.Queue()
      .push(function () {
        return synchronousChangeState(hash);
      });
  }


  //////////////////////////////////////////////////////////////////
  // Command URL functions
  //////////////////////////////////////////////////////////////////
  function routeMethodLess() {
    // Nothing. Go to setting page
    return synchronousChangeState(
      getDisplayUrlFor(undefined, {page: "index"})
    );

  }


  function routeDisplay(gadget, command_options) {
    var args = command_options.args,
      path = command_options.path;
    args.jio_key = path;
     // Store current options to handle navigation
    gadget.props.options = JSON.parse(JSON.stringify(args));
    if (args.page === undefined) {
      return routeMethodLess(gadget);
    }
    if (path === undefined || path === '') {
      return {
        url: MAIN_PAGE_PREFIX + "page_" + args.page + ".html",
        options: args
      };
    }
    return gadget.jio_get(path)
      .push(function (doc) {
        var sub_options = {},
          base_portal_type = doc.portal_type
            .toLowerCase().replace(/\s/g, "_");
        sub_options = {
          doc: doc,
          jio_key: path,
          extended_search: args.extended_search,
          begin_from: args.begin_from
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
  }


  function routeCommand(command_options) {
    var args = command_options.args,
      key,
      split_list,
      previous_options = {},
      next_options = {},
      drop_options = {},
      valid = true;
    // Rebuild the previous and next parameter dict
    for (key in args) {
      if (args.hasOwnProperty(key)) {
        split_list = key.split('.', 2);
        if (split_list.length !== 2) {
          valid = false;
          break;
        }
        if (split_list[0] === PREVIOUS_KEY) {
          previous_options[split_list[1]] = args[key];
        } else if (split_list[0] === NEXT_KEY) {
          next_options[split_list[1]] = args[key];
        } else if (split_list[0] === DROP_KEY) {
          drop_options[split_list[1]] = args[key];
        } else {
          valid = false;
          break;
        }
      }
    }
    if (!valid) {
      throw new Error('Unsupported parameters: ' + key);
    }

    if (command_options.path === COMMAND_DISPLAY_STATE) {
      return execDisplayCommand(next_options);
    }
    if (command_options.path === COMMAND_INDEX_STATE) {
      return execIndexCommand(next_options);
    }
    if (command_options.path === COMMAND_CHANGE_STATE ||
        command_options.path === COMMAND_STORE_AND_CHANGE_STATE) {
      return execChangeCommand(previous_options, next_options, drop_options);
    }
    throw new Error('Unsupported command ' + command_options.path);

  }


  function listenHashChange(gadget) {
    // Handle hash in this format: #$path1/path2?a=b&c=d
    function extractHashAndDispatch(evt) {
      var hash = (evt.newURL || window.location.toString()).split('#')[1],
        split,
        command = "",
        query = "",
        subhashes,
        subhash,
        keyvalue,
        index,
        key,
        tmp,
        args = {};
      if (hash !== undefined) {
        split = hash.split('?');
        command = split[0] || "";
        query = split[1] || "";
      }
      subhashes = query.split('&');
      for (index in subhashes) {
        if (subhashes.hasOwnProperty(index)) {
          subhash = subhashes[index];
          if (subhash !== '') {
            keyvalue = subhash.split('=');
            if (keyvalue.length === 2) {
              key = decodeURIComponent(keyvalue[0]);
              tmp = decodeURIComponent(keyvalue[1]);
              if (endsWith(key, ":json")) {
                tmp = JSON.parse(tmp);
              }
              args[key] = tmp;
            }
          }
        }
      }

      return gadget.renderApplication({
        method: command[0],
        path: command.substr(1),
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

    .declareMethod('getCommandUrlFor', function (options) {
      var command = options.command,
        absolute_url = options.absolute_url,
        hash,
        args = options.options,
        valid = true,
        key;
      // Only authorize 'command', 'options', 'absolute_url' keys
      // Drop all other kind of parameters, to detect issue more easily
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if ((key !== 'command') && (key !== 'options') &&
              (key !== 'absolute_url')) {
            valid = false;
          }
        }
      }
      if (valid && (options.command) &&
          (VALID_URL_COMMAND_DICT.hasOwnProperty(options.command))) {
        hash = getCommandUrlFor(this, command, args);
      } else {
        hash = getCommandUrlFor(this, 'error', options);
      }

      if (absolute_url) {
        hash = new URL(hash, window.location.href).href;
      }
      return hash;
    })

    .declareMethod('redirect', function (options) {
      if (options !== undefined && options.toExternal) {
        window.location.replace(options.url);
        return RSVP.timeout(REDIRECT_TIMEOUT); // timeout if not redirected
      }
      return this.getCommandUrlFor(options)
        .push(function (hash) {
          window.location.replace(hash);
            // prevent returning unexpected response
            // wait for the hash change to occur
            // fail if nothing happens
          return RSVP.timeout(REDIRECT_TIMEOUT);
        });
    })




    .declareMethod('route', function (command_options) {
      var gadget = this;

      if (command_options.method === PREFIX_DISPLAY) {
        return routeDisplay(gadget, command_options);
      }
      if (command_options.method === PREFIX_COMMAND) {
        return routeCommand(command_options);
      }
      if (command_options.method) {
        throw new Error('Unsupported hash method: ' + command_options.method);
      }
      return routeMethodLess(gadget);
    })

    .declareMethod('getUrlParameter', function (key) {
      return this.props.options[key];
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