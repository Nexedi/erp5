/*global window, rJS, RSVP, loopEventListener, document, jIO, URI, URL, Blob */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, loopEventListener, document, jIO, URI, URL, Blob) {
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

    // Display a jio document with only the passed parameters
    COMMAND_DISPLAY_STATE = "display",
    // Display a jio document with only the passed parameters + the history
    COMMAND_KEEP_HISTORY_AND_DISPLAY_STATE = "display_with_history",
    // Store the jio key for the person document of the user
    COMMAND_LOGIN = "login",
    // Display a raw string URL
    COMMAND_RAW = "raw",
    // Redisplay the page with the same parameters
    COMMAND_RELOAD = "reload",
    // Display the latest state stored for a jio document
    COMMAND_DISPLAY_STORED_STATE = "display_stored_state",
    // Display the current jio document, but change some URL parameters
    COMMAND_CHANGE_STATE = "change",
    // Like change, but also store the current jio document display state
    COMMAND_STORE_AND_CHANGE_STATE = "store_and_change",
    // Display one entry index from a selection
    COMMAND_INDEX_STATE = "index",
    // Display previous entry index from a selection
    COMMAND_SELECTION_PREVIOUS = "selection_previous",
    // Display next entry index from a selection
    COMMAND_SELECTION_NEXT = "selection_next",
    // Display previously accessed document
    COMMAND_HISTORY_PREVIOUS = "history_previous",
    // Store the current document in history and display the next one
    COMMAND_PUSH_HISTORY = "push_history",
    // Change UI language
    COMMAND_CHANGE_LANGUAGE = "change_language",
    VALID_URL_COMMAND_DICT = {},
    STICKY_PARAMETER_LIST = ['editable'];

  VALID_URL_COMMAND_DICT[COMMAND_DISPLAY_STATE] = null;
  VALID_URL_COMMAND_DICT[COMMAND_KEEP_HISTORY_AND_DISPLAY_STATE] = null;
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
  VALID_URL_COMMAND_DICT[COMMAND_CHANGE_LANGUAGE] = null;

  function dropStickyParameterEntry(options) {
    // Drop sticky parameters from an options dict
    // Do not modify the options parameters, to prevent any unexpected side effect
    var i,
      result = JSON.parse(JSON.stringify(options));
    for (i = 0; i < STICKY_PARAMETER_LIST.length; i += 1) {
      delete result[STICKY_PARAMETER_LIST[i]];
    }
    return result;
  }

  function copyStickyParameterDict(previous_options, next_options, drop_options) {
    var i,
      key;
    // Keep sticky parameters if they are currently defined in URL
    if (drop_options === undefined) {
      drop_options = {};
    }
    for (i = 0; i < STICKY_PARAMETER_LIST.length; i += 1) {
      key = STICKY_PARAMETER_LIST[i];
      // Check that sticky parameter previously exist and that it was not modified
      if (previous_options.hasOwnProperty(key) && (!(next_options.hasOwnProperty(key) || drop_options.hasOwnProperty(key)))) {
        next_options[key] = previous_options[key];
      }
    }
  }

  function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
  }

  //////////////////////////////////////////////////////////////////
  // Change URL functions
  //////////////////////////////////////////////////////////////////
  function synchronousChangeState(hash) {
    window.location.replace(hash);
    // Prevent execution of all next asynchronous code
    throw new RSVP.CancellationError('Redirecting to ' + hash);
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
    // Drop sticky parameters
    options = dropStickyParameterEntry(options);

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
    if (command === COMMAND_CHANGE_LANGUAGE) {
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting("website_url_set");
        })
        .push(function (result) {
          var param_list =  window.location.hash.split('#')[1],
            new_url = JSON.parse(result)[options.language];
          if (param_list) {
            new_url += '#' + param_list;
          }
          return new_url;
        });
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

  function execDisplayStoredStateCommand(gadget, next_options) {
    // console.warn(command_options);
    var jio_key = next_options.jio_key,
      queue;
    delete next_options.jio_key;

    if (jio_key) {
      queue = gadget.props.jio_state_gadget.get(jio_key)
        .push(function (options) {
          calculateChangeOptions(options, next_options);
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
      queue,
      display_url;
    options = calculateChangeOptions(previous_options, next_options, drop_options);

    jio_key = options.jio_key;
    delete options.jio_key;

    display_url = getDisplayUrlFor(jio_key, options);

    if (jio_key) {
      queue = gadget.props.jio_state_gadget.put(jio_key, dropStickyParameterEntry(options));
    } else {
      queue = new RSVP.Queue();
    }

    return queue
      .push(function () {
        return synchronousChangeState(display_url);
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
        var tmp;
        next_options.history = id;
        if (gadget.props.form_content) {
          tmp = gadget.props.form_content;
          delete gadget.props.form_content;
          return gadget.props.jio_form_content.putAttachment('/', id, new Blob([JSON.stringify(tmp)], {type: "application/json"}));
        }
      })
      .push(function () {
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

  function execKeepHistoryAndDisplayCommand(gadget, previous_options, next_options) {
    next_options.selection = previous_options.selection;
    next_options.history = previous_options.history;
    copyStickyParameterDict(previous_options, next_options);
    return execDisplayCommand(gadget, next_options);
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
            var options = {
              selection: previous_options.selection,
              selection_index: parseInt(previous_options.selection_index || '0', 10) + 1,
              history: previous_options.history
            };
            copyStickyParameterDict(previous_options, options);
            return addNavigationHistoryAndDisplay(
              gadget,
              result.data.rows[0].id,
              options
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
            var options = {
              selection: previous_options.selection,
              selection_index: parseInt(previous_options.selection_index, 10) - 1,
              history: previous_options.history
            };
            copyStickyParameterDict(previous_options, options);
            return addNavigationHistoryAndDisplay(
              gadget,
              result.data.rows[0].id,
              options
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

  function redirectToParent(gadget, jio_key, previous_options) {
    return gadget.jio_getAttachment(jio_key, "links")
      .push(function (erp5_document) {
        var parent_link = erp5_document._links.parent,
          uri,
          options = {};
        if (parent_link !== undefined) {
          uri = new URI(parent_link.href);
          copyStickyParameterDict(previous_options, options);
          return addNavigationHistoryAndDisplay(gadget, uri.segment(2), options);
        }
      }, function (error) {
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          var options = {};
          copyStickyParameterDict(previous_options, options);
          return gadget.redirect({command: 'display', options: options});
        }
        throw error;
      });
  }

  function execHistoryPreviousCommand(gadget, previous_options, load_options) {
    var history = previous_options.history,
      jio_key = previous_options.jio_key,
      relation_index = previous_options.relation_index,
      field = previous_options.back_field,
      queue =  new RSVP.Queue(),
      previous_id;
    if (history === undefined) {
      if (jio_key !== undefined) {
        return redirectToParent(gadget, jio_key, previous_options);
      }
    }
    if (previous_options.back_field) {
      queue
        .push(function () {
          return gadget.props.jio_form_content.getAttachment('/', history);
        })
        .push(function (results) {
          return jIO.util.readBlobAsText(results);
        }, function (error) {
          if ((error instanceof jIO.util.jIOError) &&
              (error.status_code === 404)) {
            return;
          }
          throw error;
        })
        .push(function (results) {
          if (results) {
            results = JSON.parse(results.target.result);
            if (load_options.uid) {
              results[field].value_text_list[relation_index] =  "";
              results[field].value_relative_url_list[relation_index] = load_options.jio_key;
              results[field].value_uid_list[relation_index] = load_options.uid;
            }
            gadget.props.form_content = results;
          }
        });
    }

    queue
      .push(function () {
        return gadget.props.jio_gadget.get(history);
      })
      .push(function (history) {
        previous_id = history.previous_history_id;
        return gadget.props.jio_gadget.get(history.options_id);
      })
      .push(function (result) {
        var result_list = [result, previous_id],
          options = result_list[0].data,
          next_jio_key = options.jio_key;
        delete options.jio_key;

        copyStickyParameterDict(previous_options, options);
        return addNavigationHistoryAndDisplay(gadget, next_jio_key, options);
      }, function (error) {
        // XXX Check if 404
        if ((error instanceof jIO.util.jIOError) &&
            (error.status_code === 404)) {
          return redirectToParent(gadget, jio_key, previous_options);
          // return [{data: {}}, undefined];
        }
        throw error;
      });
    return queue;
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
  function routeMethodLess(gadget, previous_options) {
    // Nothing. Go to front page
    // If no frontpage is configured, his may comes from missing configuration on website
    // or default HTML gadget modification date more recent than the website modification date
    return gadget.getSetting("frontpage_gadget")
      .push(function (result) {
        var options = {page: result};
        if (previous_options === undefined) {
          previous_options = {};
        }
        copyStickyParameterDict(previous_options, options);
        return synchronousChangeState(
          getDisplayUrlFor(undefined, options)
        );
      });
  }

  function routeDisplay(gadget, command_options) {
    if (command_options.path) {
      if (command_options.args.page === undefined) {
        return gadget.getSetting("jio_document_page_gadget", "form")
          .push(function (jio_document_page_gadget) {
            return synchronousChangeState(
              getDisplayUrlFor(command_options.path, {
                page: jio_document_page_gadget,
                editable: command_options.args.editable,
                view: command_options.args.view || 'view',
                selection: command_options.args.selection,
                selection_index: command_options.args.selection_index,
                history: command_options.args.history,
                extended_search: command_options.args.extended_search
              })
            );
          });
      }
    }

    if (command_options.args.page === undefined) {
      return routeMethodLess(gadget, command_options.args);
    }

    command_options.args.jio_key = command_options.path || undefined;

    // Store current options to handle navigation
    gadget.props.options = JSON.parse(JSON.stringify(command_options.args));

    if (command_options.args.page === 'history') {
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


    if (gadget.props.form_content) {
      command_options.args.form_content = gadget.props.form_content;
      delete gadget.props.form_content;
    }
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

    // Do not calculate this while generating the URL string to not do this too much time
    copyStickyParameterDict(previous_options, next_options, drop_options);

    if (command_options.path === COMMAND_DISPLAY_STATE) {
      return execDisplayCommand(gadget, next_options);
    }
    if (command_options.path === COMMAND_KEEP_HISTORY_AND_DISPLAY_STATE) {
      return execKeepHistoryAndDisplayCommand(gadget, previous_options, next_options);
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
      return execHistoryPreviousCommand(gadget, previous_options, next_options);
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
              key = decodeURIComponent(keyvalue[0].replace(/\+/gm, "%20"));
              tmp = decodeURIComponent(keyvalue[1].replace(/\+/gm, "%20"));
              if (tmp && (endsWith(key, ":json"))) {
                tmp = JSON.parse(tmp);
              }
              args[key] = tmp;
            }
          }
        }
      }

      //execute an url command without saving
      if (gadget.props.modified && command[0] === PREFIX_COMMAND && !gadget.props.form_content) {
        if (!window.confirm(gadget.props.warning_message)) {
          //back to previous hash
          gadget.props.hasUnsaved = true;
          return synchronousChangeState(evt.oldURL);
        }
      }
      //don't rerender old page when back to the previous hash
      if (gadget.props.hasUnsaved) {
        gadget.props.hasUnsaved = false;
        return;
      }
      return gadget.route({
        method: command[0],
        path: command.substr(1),
        args: args
      });
    }

    function catchError(evt) {
      return new RSVP.Queue()
        .push(function () {
          return extractHashAndDispatch(evt);
        })
        .push(undefined, function (error) {
          return gadget.renderError(error);
        });
    }

    var result = loopEventListener(window, 'hashchange', false,
                                   catchError),
      event = document.createEvent("Event");
    event.initEvent('hashchange', true, true);
    event.newURL = window.location.toString();
    window.dispatchEvent(event);
    return result;
  }


  rJS(window)
    .ready(function (gadget) {
      gadget.props = {
        options: {}
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
    .ready(function (g) {
      return g.getDeclaredGadget("jio_form_content")
        .push(function (jio_form_content) {
          g.props.jio_form_content = jio_form_content;
          return jio_form_content.createJio({
            type: "local",
            sessiononly: true
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
      this.props.form_content = options.form_content;
      // XXX Should we make it a second method parameter
      this.props.keep_message = true;
      delete options.form_content;
      return this.getCommandUrlFor(options)
        .push(function (hash) {
          return synchronousChangeState(hash);
        });
    })

    .declareMethod('getUrlParameter', function (key) {
      return this.props.options[key];
    })

    .declareMethod('route', function (command_options) {
      var gadget = this,
        result;

      if (command_options.method === PREFIX_DISPLAY) {
        result = routeDisplay(gadget, command_options);
      } else if (command_options.method === PREFIX_COMMAND) {
        result = routeCommand(gadget, command_options);
      } else {
        if (command_options.method) {
          throw new Error('Unsupported hash method: ' + command_options.method);
        }
        result = routeMethodLess(gadget, command_options.args);
      }
      return new RSVP.Queue()
        .push(function () {
          return result;
        })
        .push(function (route_result) {
          if ((route_result !== undefined) && (route_result.url !== undefined)) {
            return gadget.renderApplication(route_result, gadget.props.keep_message)
              .push(function (result) {
                gadget.props.keep_message = false;
                return result;
              });
          }
        });
    })

    .declareMethod('start', function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting("selected_language"),
            gadget.getSetting("default_selected_language"),
            gadget.getSetting("language_map"),
            gadget.translate("This page contains unsaved changes, do you really want to leave the page ?")
          ]);
        })
        .push(function (results) {
          if (results[1] !== results[0] && results[0] && JSON.parse(results[2]).hasOwnProperty(results[0])) {
            return gadget.redirect({
              command: COMMAND_CHANGE_LANGUAGE,
              options: {
                language: results[0]
              }
            });
          }
          gadget.props.warning_message = results[3];
          return gadget.listenHashChange();
        })
        .push(undefined, function (error) {
          if (error instanceof RSVP.CancellationError) {
            return;
          }
          throw error;
        });
    })
    .declareMethod('notify', function (options) {
      this.props.modified = (options && options.modified);
    })

    .declareAcquiredMethod('renderApplication', 'renderApplication')
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_getAttachment', 'jio_getAttachment')
    .declareAcquiredMethod('setSetting', 'setSetting')
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod('renderError', 'reportServiceError')
    .declareAcquiredMethod('translate', 'translate')

    .declareJob('listenHashChange', function () {
      return listenHashChange(this);
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        window,
        'beforeunload',
        false,
        function (event) {
          if (gadget.props.modified) {
            event.returnValue = 'fake';
          }
          return 'fake';
        }
      );
    });
}(window, rJS, RSVP, loopEventListener, document, jIO, URI, URL, Blob));