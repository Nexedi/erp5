/*global window, rJS, RSVP, loopEventListener, document, jIO, URI, URL */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, loopEventListener, document, jIO, URI, URL) {
  "use strict";

  // Keep reference of the latest allDocs params which reach to this view
  // var SELECTION_KEY = "s",
  // Keep reference in the global navigation pattern
  // HISTORY KEY = "h"
  // Current display parameter
  // DISPLAY KEY = "d"
  var PREVIOUS_KEY = "p",
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
  // Selection functions
  //////////////////////////////////////////////////////////////////
  function getSelection(gadget, selection_id) {
    return gadget.props.jio_gadget.get(selection_id)
      .push(function (result) {
        return result.data;
      });
  }

  function addHistory(gadget, options, previous_selection_id) {
    var options_blob = {
      type: "options",
      data: options
    },
      blob_id;

    return gadget.props.jio_gadget.post(options_blob)
      .push(function (result) {
        blob_id = result;
        return gadget.props.jio_gadget.get(previous_selection_id)
          .push(undefined, function () {
            previous_selection_id = undefined;
          });
      })
      .push(function () {
        var data_history = {
          type: "history",
          options_id: blob_id,
          previous_history_id: previous_selection_id
        };
        return gadget.props.jio_gadget.post(data_history);
      })
      .push(function (id) {
        return id;
      });
  }

  function addSelection(gadget, options) {
    var data_blob = {
      type: "selection",
      data: options
    };
    return gadget.props.jio_gadget.post(data_blob);
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
        result += prefix + PREVIOUS_KEY + "." + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);
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
          result += prefix + NEXT_KEY + "." + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);
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
        result += prefix + encodeURIComponent(key) + "=" + encodeURIComponent(tmp);
        prefix = '&';
      }
    }
    return result;
  }

  //////////////////////////////////////////////////////////////////
  // navigation history functions
  //////////////////////////////////////////////////////////////////
  function addNavigationHistoryAndDisplay(gadget, jio_key, options) {
    var hash = getDisplayUrlFor(jio_key, options),
      queue;
    /*jslint regexp: true*/
    if (jio_key && /^[^\/]+_module\/[^\/]+$/.test(jio_key)) {
      /*jslint regexp: false*/
      // This only work for remote access to ERP5...
      queue = gadget.props.jio_navigation_gadget.put(jio_key, {
        access_time: (new Date().getTime()),
        hash: hash
      })
        .push(function () {
          return gadget.props.jio_navigation_gadget.allDocs({
            sort_on: [['access_time', 'descending']],
            // Max number of history entry
            limit: [30, 9999]
          });
        })
        .push(function (result_list) {
          // Remove old accessed documents
          var i,
            promise_list = [];
          for (i = 0; i < result_list.data.rows.length; i += 1) {
            promise_list.push(
              gadget.props.jio_navigation_gadget.remove(result_list.data.rows[i].id)
            );
          }
          return RSVP.all(promise_list);
        });
    } else {
      queue = new RSVP.Queue();
    }
    return queue
      .push(function () {
        return synchronousChangeState(hash);
      });
  }

  //////////////////////////////////////////////////////////////////
  // exec command functions
  //////////////////////////////////////////////////////////////////
  function execDisplayCommand(gadget, next_options) {
    // console.warn(command_options);
    var jio_key = next_options.jio_key;
    delete next_options.jio_key;
    return addNavigationHistoryAndDisplay(gadget, jio_key, next_options);
  }

  function execDisplayStoredStateCommand(gadget, next_options) {
    // console.warn(command_options);
    var jio_key = next_options.jio_key,
      queue;
    delete next_options.jio_key;

    if (jio_key) {
      queue = gadget.props.jio_state_gadget.get(jio_key)
        .push(function (options) {
          next_options = options;
        }, function (error) {
          if ((error instanceof jIO.util.jIOError) &&
              (error.status_code === 404)) {
            return;
          }
          throw error;
        });
    } else {
      queue = new RSVP.Queue();
    }
    return queue
      .push(function () {
        return addNavigationHistoryAndDisplay(gadget, jio_key, next_options);
      });
  }

  function calculateChangeOptions(previous_options, next_options, drop_options) {
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

  function execChangeCommand(previous_options, next_options, drop_options) {
    var options,
      jio_key;
    options = calculateChangeOptions(previous_options, next_options, drop_options);

    jio_key = options.jio_key;
    delete options.jio_key;
    return synchronousChangeState(
      getDisplayUrlFor(jio_key, options)
    );
  }

  function execStoreAndChangeCommand(gadget, previous_options, next_options, drop_options) {
    var options,
      jio_key,
      queue;
    options = calculateChangeOptions(previous_options, next_options, drop_options);

    jio_key = options.jio_key;
    delete options.jio_key;

    if (jio_key) {
      queue = gadget.props.jio_state_gadget.put(jio_key, options);
    } else {
      queue = new RSVP.Queue();
    }


    return queue
      .push(function () {
        return synchronousChangeState(
          getDisplayUrlFor(jio_key, options)
        );
      });
  }

  function execIndexCommand(gadget, previous_options, next_options) {
    var jio_key = next_options.jio_key,
      selection_options = {};
    delete next_options.jio_key;
    // selection_options.index = next_options.index;
    selection_options.query = next_options.query;
    selection_options.list_method_template = next_options.list_method_template;
    selection_options["sort_list:json"] = next_options["sort_list:json"] || [];
    // Store selection in local DB
    return addSelection(gadget, selection_options)
      .push(function (id) {
        next_options.selection = id;
        // XXX Implement history management
        return addHistory(gadget, previous_options);
      })
      .push(function (id) {
        next_options.history = id;
        return addNavigationHistoryAndDisplay(gadget, jio_key, next_options);
      });
  }

  function execPushHistoryCommand(gadget, previous_options, next_options) {
    var jio_key = next_options.jio_key;
    delete next_options.jio_key;
    // XXX Hack to support create dialog
    delete previous_options.view;
    delete previous_options.page;
    return addHistory(gadget, previous_options)
      .push(function (id) {
        next_options.history = id;
        return addNavigationHistoryAndDisplay(gadget, jio_key, next_options);
      });
  }

  function execSelectionNextCommand(gadget, previous_options) {
    if (previous_options.selection === undefined) {
      return synchronousChangeState(
        getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
      );
    }
    // Get the selection parameters
    // Query all docs with those parameters + expected index
    // Redirect to the result document
    return getSelection(gadget, previous_options.selection)
      .push(function (selection) {
        return gadget.jio_allDocs({
          "query": selection.query,
          "list_method_template": selection.list_method_template,
          "limit": [parseInt(previous_options.selection_index || '0', 10) + 1, 1],
          "sort_on": selection["sort_list:json"]
        })
          .push(function (result) {
            if (result.data.rows.length === 0) {
              return synchronousChangeState(
                getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
              );
            }
            return addNavigationHistoryAndDisplay(
              gadget,
              result.data.rows[0].id,
              {
                selection: previous_options.selection,
                selection_index: parseInt(previous_options.selection_index || '0', 10) + 1,
                history: previous_options.history
              }
            );
          });
      }, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return synchronousChangeState(
            getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
          );
        }
        throw error;
      });
  }

  function execSelectionPreviousCommand(gadget, previous_options) {
    if (previous_options.selection === undefined) {
      return synchronousChangeState(
        getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
      );
    }
    // Get the selection parameters
    // Query all docs with those parameters + expected index
    // Redirect to the result document
    return getSelection(gadget, previous_options.selection)
      .push(function (selection) {
        if (parseInt(previous_options.selection_index || '0', 10) < 1) {
          return synchronousChangeState(
            getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
          );
        }
        return gadget.jio_allDocs({
          "query": selection.query,
          "list_method_template": selection.list_method_template,
          "limit": [parseInt(previous_options.selection_index, 10) - 1, 1],
          "sort_on": selection["sort_list:json"]
        })
          .push(function (result) {
            if (result.data.rows.length === 0) {
              return synchronousChangeState(
                getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
              );
            }
            return addNavigationHistoryAndDisplay(
              gadget,
              result.data.rows[0].id,
              {
                selection: previous_options.selection,
                selection_index: parseInt(previous_options.selection_index, 10) - 1,
                history: previous_options.history
              }
            );
          });
      }, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return synchronousChangeState(
            getCommandUrlFor(gadget, COMMAND_HISTORY_PREVIOUS, previous_options)
          );
        }
        throw error;
      });
  }

  function redirectToParent(gadget, jio_key) {
    return gadget.jio_getAttachment(jio_key, "links")
      .push(function (erp5_document) {
        var parent_link = erp5_document._links.parent,
          uri;
        if (parent_link !== undefined) {
          uri = new URI(parent_link.href);

          return addNavigationHistoryAndDisplay(gadget, uri.segment(2), {});
        }
      });
  }

  function execHistoryPreviousCommand(gadget, previous_options) {
    var history = previous_options.history,
      jio_key = previous_options.jio_key,
      previous_id;
    if (history === undefined) {
      if (jio_key !== undefined) {
        return redirectToParent(gadget, jio_key);
      }
    }

    return gadget.props.jio_gadget.get(history)
      .push(function (history) {
        previous_id = history.previous_history_id;
        return gadget.props.jio_gadget.get(history.options_id);
      })
      .push(function (result) {
        return [result, previous_id];
      }, function (error) {
        // XXX Check if 404
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return redirectToParent(gadget, jio_key);
          // return [{data: {}}, undefined];
        }
        throw error;
      })
      .push(function (result_list) {
        var options = result_list[0].data,
          next_jio_key = options.jio_key;
        delete options.jio_key;
        return addNavigationHistoryAndDisplay(gadget, next_jio_key, options);
      });
  }


  function execLoginCommand(gadget, previous_options, next_options) {
    var me = next_options.me;
    return gadget.setSetting('me', me)
      .push(function () {
        return execDisplayCommand(gadget, previous_options);
      });
  }

  function execReloadCommand(previous_options) {
    var jio_key = previous_options.jio_key;
    delete previous_options.jio_key;
    return synchronousChangeState(
      getDisplayUrlFor(jio_key, previous_options)
    );
  }

  //////////////////////////////////////////////////////////////////
  // Command URL functions
  //////////////////////////////////////////////////////////////////
  function routeMethodLess() {
    // Nothing. Go to front page
    return synchronousChangeState(
      getDisplayUrlFor(undefined, {page: 'worklist'})
    );
  }

  function routeDisplay(gadget, command_options) {
    if (command_options.path) {
      if (command_options.args.page === undefined) {
        return synchronousChangeState(
          getDisplayUrlFor(command_options.path, {
            page: 'form',
            editable: command_options.args.editable,
            view: command_options.args.view || 'view',
            selection: command_options.args.selection,
            selection_index: command_options.args.selection_index,
            history: command_options.args.history
          })
        );
      }
    } else if (command_options.args.page === 'history') {
      // This is an adhoc route to handle local navigation history
      return gadget.props.jio_navigation_gadget.allDocs({
        sort_on: [['access_time', 'descending']]
      })
        .push(function (result) {
          var result_list = result.data.rows,
            id_list = [],
            i;
          for (i = 0; i < result_list.length; i += 1) {
            id_list.push(result_list[i].id);
          }

          return {
            url: "gadget_erp5_page_" + command_options.args.page + ".html",
            // XXX Drop this options thing.
            // Implement a "getSelection" method
            options: {
              id_list: id_list
            }
          };
        });
    }

    if (command_options.args.page === undefined) {
      return routeMethodLess();
    }

    command_options.args.jio_key = command_options.path || undefined;

    // Store current options to handle navigation
    gadget.props.options = JSON.parse(JSON.stringify(command_options.args));

    return {
      url: "gadget_erp5_page_" + command_options.args.page + ".html",
      // XXX Drop this options thing.
      // Implement a "getSelection" method
      options: command_options.args
      // options: {}
    };

  }

  function routeCommand(gadget, command_options) {
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
      return execDisplayCommand(gadget, next_options);
    }
    if (command_options.path === COMMAND_DISPLAY_STORED_STATE) {
      return execDisplayStoredStateCommand(gadget, next_options);
    }
    if (command_options.path === COMMAND_INDEX_STATE) {
      return execIndexCommand(gadget, previous_options, next_options);
    }
    if (command_options.path === COMMAND_CHANGE_STATE) {
      return execChangeCommand(previous_options, next_options, drop_options);
    }
    if (command_options.path === COMMAND_STORE_AND_CHANGE_STATE) {
      return execStoreAndChangeCommand(gadget, previous_options, next_options, drop_options);
    }
    if (command_options.path === COMMAND_SELECTION_NEXT) {
      return execSelectionNextCommand(gadget, previous_options);
    }
    if (command_options.path === COMMAND_SELECTION_PREVIOUS) {
      return execSelectionPreviousCommand(gadget, previous_options);
    }
    if (command_options.path === COMMAND_HISTORY_PREVIOUS) {
      return execHistoryPreviousCommand(gadget, previous_options);
    }
    if (command_options.path === COMMAND_PUSH_HISTORY) {
      return execPushHistoryCommand(gadget, previous_options, next_options);
    }
    if (command_options.path === COMMAND_LOGIN) {
      return execLoginCommand(gadget, previous_options, next_options);
    }
    if (command_options.path === COMMAND_RELOAD) {
      return execReloadCommand(previous_options);
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
        options: {},
        start_deferred: RSVP.defer()
      };
    })

    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_selection")
        .push(function (jio_gadget) {
          gadget.props.jio_gadget = jio_gadget;
          return jio_gadget.createJio({
            type: "sha",
            sub_storage: {
              type: "indexeddb",
              database: "selection"
            }
          });
        });
    })

    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_navigation_history")
        .push(function (jio_gadget) {
          gadget.props.jio_navigation_gadget = jio_gadget;
          return jio_gadget.createJio({
            type: "query",
            sub_storage: {
              type: "indexeddb",
              database: "navigation_history"
            }
          });
        });
    })

    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_document_state")
        .push(function (jio_gadget) {
          gadget.props.jio_state_gadget = jio_gadget;
          return jio_gadget.createJio({
            type: "indexeddb",
            database: "document_state"
          });
        });
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
          if ((key !== 'command') && (key !== 'options') && (key !== 'absolute_url')) {
            valid = false;
          }
        }
      }
      if (valid && (options.command) && (VALID_URL_COMMAND_DICT.hasOwnProperty(options.command))) {
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
      return this.getCommandUrlFor(options)
        .push(function (hash) {
          window.location.replace(hash);

          // prevent returning unexpected response
          // wait for the hash change to occur
          // fail if nothing happens
          return RSVP.timeout(REDIRECT_TIMEOUT);
        });
    })

    .declareMethod('getUrlParameter', function (key) {
      return this.props.options[key];
    })

    .declareMethod('route', function (command_options) {
      var gadget = this;

      if (command_options.method === PREFIX_DISPLAY) {
        return routeDisplay(gadget, command_options);
      }
      if (command_options.method === PREFIX_COMMAND) {
        return routeCommand(gadget, command_options);
      }
      if (command_options.method) {
        throw new Error('Unsupported hash method: ' + command_options.method);
      }
      return routeMethodLess();
    })

    .declareMethod('start', function () {
      this.props.start_deferred.resolve();
    })

    .declareAcquiredMethod('renderApplication', 'renderApplication')
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('setSetting', 'setSetting')

    .declareService(function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.props.start_deferred.promise;
        })
        .push(function () {
          // console.info('router service: listen to hash change');
          return listenHashChange(gadget);
        });
    });

}(window, rJS, RSVP, loopEventListener, document, jIO, URI, URL));
