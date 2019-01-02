/*
 * js_channel is a very lightweight abstraction on top of
 * postMessage which defines message formats and semantics
 * to support interactions more rich than just message passing
 * js_channel supports:
 *  + query/response - traditional rpc
 *  + query/update/response - incremental async return of results
 *    to a query
 *  + notifications - fire and forget
 *  + error handling
 *
 * js_channel is based heavily on json-rpc, but is focused at the
 * problem of inter-iframe RPC.
 *
 * Message types:
 *  There are 5 types of messages that can flow over this channel,
 *  and you may determine what type of message an object is by
 *  examining its parameters:
 *  1. Requests
 *    + integer id
 *    + string method
 *    + (optional) any params
 *  2. Callback Invocations (or just "Callbacks")
 *    + integer id
 *    + string callback
 *    + (optional) params
 *  3. Error Responses (or just "Errors)
 *    + integer id
 *    + string error
 *    + (optional) string message
 *  4. Responses
 *    + integer id
 *    + (optional) any result
 *  5. Notifications
 *    + string method
 *    + (optional) any params
 */

;var Channel = (function() {
    "use strict";

    // current transaction id, start out at a random *odd* number between 1 and a million
    // There is one current transaction counter id per page, and it's shared between
    // channel instances.  That means of all messages posted from a single javascript
    // evaluation context, we'll never have two with the same id.
    var s_curTranId = Math.floor(Math.random()*1000001);

    // no two bound channels in the same javascript evaluation context may have the same origin, scope, and window.
    // futher if two bound channels have the same window and scope, they may not have *overlapping* origins
    // (either one or both support '*').  This restriction allows a single onMessage handler to efficiently
    // route messages based on origin and scope.  The s_boundChans maps origins to scopes, to message
    // handlers.  Request and Notification messages are routed using this table.
    // Finally, channels are inserted into this table when built, and removed when destroyed.
    var s_boundChans = { };

    // add a channel to s_boundChans, throwing if a dup exists
    function s_addBoundChan(win, origin, scope, handler) {
        function hasWin(arr) {
            for (var i = 0; i < arr.length; i++) if (arr[i].win === win) return true;
            return false;
        }

        // does she exist?
        var exists = false;


        if (origin === '*') {
            // we must check all other origins, sadly.
            for (var k in s_boundChans) {
                if (!s_boundChans.hasOwnProperty(k)) continue;
                if (k === '*') continue;
                if (typeof s_boundChans[k][scope] === 'object') {
                    exists = hasWin(s_boundChans[k][scope]);
                    if (exists) break;
                }
            }
        } else {
            // we must check only '*'
            if ((s_boundChans['*'] && s_boundChans['*'][scope])) {
                exists = hasWin(s_boundChans['*'][scope]);
            }
            if (!exists && s_boundChans[origin] && s_boundChans[origin][scope])
            {
                exists = hasWin(s_boundChans[origin][scope]);
            }
        }
        if (exists) throw "A channel is already bound to the same window which overlaps with origin '"+ origin +"' and has scope '"+scope+"'";

        if (typeof s_boundChans[origin] != 'object') s_boundChans[origin] = { };
        if (typeof s_boundChans[origin][scope] != 'object') s_boundChans[origin][scope] = [ ];
        s_boundChans[origin][scope].push({win: win, handler: handler});
    }

    function s_removeBoundChan(win, origin, scope) {
        var arr = s_boundChans[origin][scope];
        for (var i = 0; i < arr.length; i++) {
            if (arr[i].win === win) {
                arr.splice(i,1);
            }
        }
        if (s_boundChans[origin][scope].length === 0) {
            delete s_boundChans[origin][scope];
        }
    }

    function s_isArray(obj) {
        if (Array.isArray) return Array.isArray(obj);
        else {
            return (obj.constructor.toString().indexOf("Array") != -1);
        }
    }

    // No two outstanding outbound messages may have the same id, period.  Given that, a single table
    // mapping "transaction ids" to message handlers, allows efficient routing of Callback, Error, and
    // Response messages.  Entries are added to this table when requests are sent, and removed when
    // responses are received.
    var s_transIds = { };

    // class singleton onMessage handler
    // this function is registered once and all incoming messages route through here.  This
    // arrangement allows certain efficiencies, message data is only parsed once and dispatch
    // is more efficient, especially for large numbers of simultaneous channels.
    var s_onMessage = function(e) {
        try {
          var m = JSON.parse(e.data);
          if (typeof m !== 'object' || m === null) throw "malformed";
        } catch(e) {
          // just ignore any posted messages that do not consist of valid JSON
          return;
        }

        var w = e.source;
        var o = e.origin;
        var s, i, meth;

        if (typeof m.method === 'string') {
            var ar = m.method.split('::');
            if (ar.length == 2) {
                s = ar[0];
                meth = ar[1];
            } else {
                meth = m.method;
            }
        }

        if (typeof m.id !== 'undefined') i = m.id;

        // w is message source window
        // o is message origin
        // m is parsed message
        // s is message scope
        // i is message id (or undefined)
        // meth is unscoped method name
        // ^^ based on these factors we can route the message

        // if it has a method it's either a notification or a request,
        // route using s_boundChans
        if (typeof meth === 'string') {
            var delivered = false;
            if (s_boundChans[o] && s_boundChans[o][s]) {
                for (var j = 0; j < s_boundChans[o][s].length; j++) {
                    if (s_boundChans[o][s][j].win === w) {
                        s_boundChans[o][s][j].handler(o, meth, m);
                        delivered = true;
                        break;
                    }
                }
            }

            if (!delivered && s_boundChans['*'] && s_boundChans['*'][s]) {
                for (var j = 0; j < s_boundChans['*'][s].length; j++) {
                    if (s_boundChans['*'][s][j].win === w) {
                        s_boundChans['*'][s][j].handler(o, meth, m);
                        break;
                    }
                }
            }
        }
        // otherwise it must have an id (or be poorly formed
        else if (typeof i != 'undefined') {
            if (s_transIds[i]) s_transIds[i](o, meth, m);
        }
    };

    // Setup postMessage event listeners
    if (window.addEventListener) window.addEventListener('message', s_onMessage, false);
    else if(window.attachEvent) window.attachEvent('onmessage', s_onMessage);

    /* a messaging channel is constructed from a window and an origin.
     * the channel will assert that all messages received over the
     * channel match the origin
     *
     * Arguments to Channel.build(cfg):
     *
     *   cfg.window - the remote window with which we'll communicate
     *   cfg.origin - the expected origin of the remote window, may be '*'
     *                which matches any origin
     *   cfg.scope  - the 'scope' of messages.  a scope string that is
     *                prepended to message names.  local and remote endpoints
     *                of a single channel must agree upon scope. Scope may
     *                not contain double colons ('::').
     *   cfg.debugOutput - A boolean value.  If true and window.console.log is
     *                a function, then debug strings will be emitted to that
     *                function.
     *   cfg.debugOutput - A boolean value.  If true and window.console.log is
     *                a function, then debug strings will be emitted to that
     *                function.
     *   cfg.postMessageObserver - A function that will be passed two arguments,
     *                an origin and a message.  It will be passed these immediately
     *                before messages are posted.
     *   cfg.gotMessageObserver - A function that will be passed two arguments,
     *                an origin and a message.  It will be passed these arguments
     *                immediately after they pass scope and origin checks, but before
     *                they are processed.
     *   cfg.onReady - A function that will be invoked when a channel becomes "ready",
     *                this occurs once both sides of the channel have been
     *                instantiated and an application level handshake is exchanged.
     *                the onReady function will be passed a single argument which is
     *                the channel object that was returned from build().
     */
    return {
        build: function(cfg) {
            var debug = function(m) {
                if (cfg.debugOutput && window.console && window.console.log) {
                    // try to stringify, if it doesn't work we'll let javascript's built in toString do its magic
                    try { if (typeof m !== 'string') m = JSON.stringify(m); } catch(e) { }
                    console.log("["+chanId+"] " + m);
                }
            };

            /* browser capabilities check */
            if (!window.postMessage) throw("jschannel cannot run this browser, no postMessage");
            if (!window.JSON || !window.JSON.stringify || ! window.JSON.parse) {
                throw("jschannel cannot run this browser, no JSON parsing/serialization");
            }

            /* basic argument validation */
            if (typeof cfg != 'object') throw("Channel build invoked without a proper object argument");

            if (!cfg.window || !cfg.window.postMessage) throw("Channel.build() called without a valid window argument");

            /* we'd have to do a little more work to be able to run multiple channels that intercommunicate the same
             * window...  Not sure if we care to support that */
            if (window === cfg.window) throw("target window is same as present window -- not allowed");

            // let's require that the client specify an origin.  if we just assume '*' we'll be
            // propagating unsafe practices.  that would be lame.
            var validOrigin = false;
            if (typeof cfg.origin === 'string') {
                var oMatch;
                if (cfg.origin === "*") validOrigin = true;
                // allow valid domains under http and https.  Also, trim paths off otherwise valid origins.
                else if (null !== (oMatch = cfg.origin.match(/^https?:\/\/(?:[-a-zA-Z0-9_\.])+(?::\d+)?/))) {
                    cfg.origin = oMatch[0].toLowerCase();
                    validOrigin = true;
                }
            }

            if (!validOrigin) throw ("Channel.build() called with an invalid origin");

            if (typeof cfg.scope !== 'undefined') {
                if (typeof cfg.scope !== 'string') throw 'scope, when specified, must be a string';
                if (cfg.scope.split('::').length > 1) throw "scope may not contain double colons: '::'";
            }

            /* private variables */
            // generate a random and psuedo unique id for this channel
            var chanId = (function () {
                var text = "";
                var alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
                for(var i=0; i < 5; i++) text += alpha.charAt(Math.floor(Math.random() * alpha.length));
                return text;
            })();

            // registrations: mapping method names to call objects
            var regTbl = { };
            // current oustanding sent requests
            var outTbl = { };
            // current oustanding received requests
            var inTbl = { };
            // are we ready yet?  when false we will block outbound messages.
            var ready = false;
            var pendingQueue = [ ];

            var createTransaction = function(id,origin,callbacks) {
                var shouldDelayReturn = false;
                var completed = false;

                return {
                    origin: origin,
                    invoke: function(cbName, v) {
                        // verify in table
                        if (!inTbl[id]) throw "attempting to invoke a callback of a nonexistent transaction: " + id;
                        // verify that the callback name is valid
                        var valid = false;
                        for (var i = 0; i < callbacks.length; i++) if (cbName === callbacks[i]) { valid = true; break; }
                        if (!valid) throw "request supports no such callback '" + cbName + "'";

                        // send callback invocation
                        postMessage({ id: id, callback: cbName, params: v});
                    },
                    error: function(error, message) {
                        completed = true;
                        // verify in table
                        if (!inTbl[id]) throw "error called for nonexistent message: " + id;

                        // remove transaction from table
                        delete inTbl[id];

                        // send error
                        postMessage({ id: id, error: error, message: message });
                    },
                    complete: function(v) {
                        completed = true;
                        // verify in table
                        if (!inTbl[id]) throw "complete called for nonexistent message: " + id;
                        // remove transaction from table
                        delete inTbl[id];
                        // send complete
                        postMessage({ id: id, result: v });
                    },
                    delayReturn: function(delay) {
                        if (typeof delay === 'boolean') {
                            shouldDelayReturn = (delay === true);
                        }
                        return shouldDelayReturn;
                    },
                    completed: function() {
                        return completed;
                    }
                };
            };

            var setTransactionTimeout = function(transId, timeout, method) {
              return window.setTimeout(function() {
                if (outTbl[transId]) {
                  // XXX: what if client code raises an exception here?
                  var msg = "timeout (" + timeout + "ms) exceeded on method '" + method + "'";
                  (1,outTbl[transId].error)("timeout_error", msg);
                  delete outTbl[transId];
                  delete s_transIds[transId];
                }
              }, timeout);
            };

            var onMessage = function(origin, method, m) {
                // if an observer was specified at allocation time, invoke it
                if (typeof cfg.gotMessageObserver === 'function') {
                    // pass observer a clone of the object so that our
                    // manipulations are not visible (i.e. method unscoping).
                    // This is not particularly efficient, but then we expect
                    // that message observers are primarily for debugging anyway.
                    try {
                        cfg.gotMessageObserver(origin, m);
                    } catch (e) {
                        debug("gotMessageObserver() raised an exception: " + e.toString());
                    }
                }

                // now, what type of message is this?
                if (m.id && method) {
                    // a request!  do we have a registered handler for this request?
                    if (regTbl[method]) {
                        var trans = createTransaction(m.id, origin, m.callbacks ? m.callbacks : [ ]);
                        inTbl[m.id] = { };
                        try {
                            // callback handling.  we'll magically create functions inside the parameter list for each
                            // callback
                            if (m.callbacks && s_isArray(m.callbacks) && m.callbacks.length > 0) {
                                for (var i = 0; i < m.callbacks.length; i++) {
                                    var path = m.callbacks[i];
                                    var obj = m.params;
                                    var pathItems = path.split('/');
                                    for (var j = 0; j < pathItems.length - 1; j++) {
                                        var cp = pathItems[j];
                                        if (typeof obj[cp] !== 'object') obj[cp] = { };
                                        obj = obj[cp];
                                    }
                                    obj[pathItems[pathItems.length - 1]] = (function() {
                                        var cbName = path;
                                        return function(params) {
                                            return trans.invoke(cbName, params);
                                        };
                                    })();
                                }
                            }
                            var resp = regTbl[method](trans, m.params);
                            if (!trans.delayReturn() && !trans.completed()) trans.complete(resp);
                        } catch(e) {
                            // automagic handling of exceptions:
                            var error = "runtime_error";
                            var message = null;
                            // * if it's a string then it gets an error code of 'runtime_error' and string is the message
                            if (typeof e === 'string') {
                                message = e;
                            } else if (typeof e === 'object') {
                                // either an array or an object
                                // * if it's an array of length two, then  array[0] is the code, array[1] is the error message
                                if (e && s_isArray(e) && e.length == 2) {
                                    error = e[0];
                                    message = e[1];
                                }
                                // * if it's an object then we'll look form error and message parameters
                                else if (typeof e.error === 'string') {
                                    error = e.error;
                                    if (!e.message) message = "";
                                    else if (typeof e.message === 'string') message = e.message;
                                    else e = e.message; // let the stringify/toString message give us a reasonable verbose error string
                                }
                            }

                            // message is *still* null, let's try harder
                            if (message === null) {
                                try {
                                    message = JSON.stringify(e);
                                    /* On MSIE8, this can result in 'out of memory', which
                                     * leaves message undefined. */
                                    if (typeof(message) == 'undefined')
                                      message = e.toString();
                                } catch (e2) {
                                    message = e.toString();
                                }
                            }

                            trans.error(error,message);
                        }
                    }
                } else if (m.id && m.callback) {
                    if (!outTbl[m.id] ||!outTbl[m.id].callbacks || !outTbl[m.id].callbacks[m.callback])
                    {
                        debug("ignoring invalid callback, id:"+m.id+ " (" + m.callback +")");
                    } else {
                        // XXX: what if client code raises an exception here?
                        outTbl[m.id].callbacks[m.callback](m.params);
                    }
                } else if (m.id) {
                    if (!outTbl[m.id]) {
                        debug("ignoring invalid response: " + m.id);
                    } else {
                        // XXX: what if client code raises an exception here?
                        if (m.error) {
                            (1,outTbl[m.id].error)(m.error, m.message);
                        } else {
                            if (m.result !== undefined) (1,outTbl[m.id].success)(m.result);
                            else (1,outTbl[m.id].success)();
                        }
                        delete outTbl[m.id];
                        delete s_transIds[m.id];
                    }
                } else if (method) {
                    // tis a notification.
                    if (regTbl[method]) {
                        // yep, there's a handler for that.
                        // transaction has only origin for notifications.
                        regTbl[method]({ origin: origin }, m.params);
                        // if the client throws, we'll just let it bubble out
                        // what can we do?  Also, here we'll ignore return values
                    }
                }
            };

            // now register our bound channel for msg routing
            s_addBoundChan(cfg.window, cfg.origin, ((typeof cfg.scope === 'string') ? cfg.scope : ''), onMessage);

            // scope method names based on cfg.scope specified when the Channel was instantiated
            var scopeMethod = function(m) {
                if (typeof cfg.scope === 'string' && cfg.scope.length) m = [cfg.scope, m].join("::");
                return m;
            };

            // a small wrapper around postmessage whose primary function is to handle the
            // case that clients start sending messages before the other end is "ready"
            var postMessage = function(msg, force) {
                if (!msg) throw "postMessage called with null message";

                // delay posting if we're not ready yet.
                var verb = (ready ? "post  " : "queue ");
                debug(verb + " message: " + JSON.stringify(msg));
                if (!force && !ready) {
                    pendingQueue.push(msg);
                } else {
                    if (typeof cfg.postMessageObserver === 'function') {
                        try {
                            cfg.postMessageObserver(cfg.origin, msg);
                        } catch (e) {
                            debug("postMessageObserver() raised an exception: " + e.toString());
                        }
                    }

                    cfg.window.postMessage(JSON.stringify(msg), cfg.origin);
                }
            };

            var onReady = function(trans, type) {
                debug('ready msg received');
                if (ready) throw "received ready message while in ready state.  help!";

                if (type === 'ping') {
                    chanId += '-R';
                } else {
                    chanId += '-L';
                }

                obj.unbind('__ready'); // now this handler isn't needed any more.
                ready = true;
                debug('ready msg accepted.');

                if (type === 'ping') {
                    obj.notify({ method: '__ready', params: 'pong' });
                }

                // flush queue
                while (pendingQueue.length) {
                    postMessage(pendingQueue.pop());
                }

                // invoke onReady observer if provided
                if (typeof cfg.onReady === 'function') cfg.onReady(obj);
            };

            var obj = {
                // tries to unbind a bound message handler.  returns false if not possible
                unbind: function (method) {
                    if (regTbl[method]) {
                        if (!(delete regTbl[method])) throw ("can't delete method: " + method);
                        return true;
                    }
                    return false;
                },
                bind: function (method, cb) {
                    if (!method || typeof method !== 'string') throw "'method' argument to bind must be string";
                    if (!cb || typeof cb !== 'function') throw "callback missing from bind params";

                    if (regTbl[method]) throw "method '"+method+"' is already bound!";
                    regTbl[method] = cb;
                    return this;
                },
                call: function(m) {
                    if (!m) throw 'missing arguments to call function';
                    if (!m.method || typeof m.method !== 'string') throw "'method' argument to call must be string";
                    if (!m.success || typeof m.success !== 'function') throw "'success' callback missing from call";

                    // now it's time to support the 'callback' feature of jschannel.  We'll traverse the argument
                    // object and pick out all of the functions that were passed as arguments.
                    var callbacks = { };
                    var callbackNames = [ ];

                    var pruneFunctions = function (path, obj) {
                        if (typeof obj === 'object') {
                            for (var k in obj) {
                                if (!obj.hasOwnProperty(k)) continue;
                                var np = path + (path.length ? '/' : '') + k;
                                if (typeof obj[k] === 'function') {
                                    callbacks[np] = obj[k];
                                    callbackNames.push(np);
                                    delete obj[k];
                                } else if (typeof obj[k] === 'object') {
                                    pruneFunctions(np, obj[k]);
                                }
                            }
                        }
                    };
                    pruneFunctions("", m.params);

                    // build a 'request' message and send it
                    var msg = { id: s_curTranId, method: scopeMethod(m.method), params: m.params };
                    if (callbackNames.length) msg.callbacks = callbackNames;

                    if (m.timeout)
                      // XXX: This function returns a timeout ID, but we don't do anything with it.
                      // We might want to keep track of it so we can cancel it using clearTimeout()
                      // when the transaction completes.
                      setTransactionTimeout(s_curTranId, m.timeout, scopeMethod(m.method));

                    // insert into the transaction table
                    outTbl[s_curTranId] = { callbacks: callbacks, error: m.error, success: m.success };
                    s_transIds[s_curTranId] = onMessage;

                    // increment current id
                    s_curTranId++;

                    postMessage(msg);
                },
                notify: function(m) {
                    if (!m) throw 'missing arguments to notify function';
                    if (!m.method || typeof m.method !== 'string') throw "'method' argument to notify must be string";

                    // no need to go into any transaction table
                    postMessage({ method: scopeMethod(m.method), params: m.params });
                },
                destroy: function () {
                    s_removeBoundChan(cfg.window, cfg.origin, ((typeof cfg.scope === 'string') ? cfg.scope : ''));
                    if (window.removeEventListener) window.removeEventListener('message', onMessage, false);
                    else if(window.detachEvent) window.detachEvent('onmessage', onMessage);
                    ready = false;
                    regTbl = { };
                    inTbl = { };
                    outTbl = { };
                    cfg.origin = null;
                    pendingQueue = [ ];
                    debug("channel destroyed");
                    chanId = "";
                }
            };

            obj.bind('__ready', onReady);
            setTimeout(function() {
                postMessage({ method: scopeMethod('__ready'), params: "ping" }, true);
            }, 0);

            return obj;
        }
    };
})();
;/*
 * DOMParser HTML extension
 * 2012-09-04
 *
 * By Eli Grey, http://eligrey.com
 * Public domain.
 * NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.
 */
/*! @source https://gist.github.com/1129031 */
(function (DOMParser) {
  "use strict";
  var DOMParser_proto = DOMParser.prototype,
    real_parseFromString = DOMParser_proto.parseFromString;

  // Firefox/Opera/IE throw errors on unsupported types
  try {
    // WebKit returns null on unsupported types
    if ((new DOMParser()).parseFromString("", "text/html")) {
      // text/html parsing is natively supported
      return;
    }
  } catch (ignore) {}

  DOMParser_proto.parseFromString = function (markup, type) {
    var result, doc, doc_elt, first_elt;
    if (/^\s*text\/html\s*(?:;|$)/i.test(type)) {
      doc = document.implementation.createHTMLDocument("");
      doc_elt = doc.documentElement;

      doc_elt.innerHTML = markup;
      first_elt = doc_elt.firstElementChild;

      if (doc_elt.childElementCount === 1
          && first_elt.localName.toLowerCase() === "html") {
        doc.replaceChild(first_elt, doc_elt);
      }

      result = doc;
    } else {
      result = real_parseFromString.apply(this, arguments);
    }
    return result;
  };
}(DOMParser));

;/*! RenderJs */
/*global console */
/*jslint nomen: true*/
function loopEventListener(target, type, useCapture, callback) {
  "use strict";
  //////////////////////////
  // Infinite event listener (promise is never resolved)
  // eventListener is removed when promise is cancelled/rejected
  //////////////////////////
  var handle_event_callback,
    callback_promise;

  function cancelResolver() {
    if ((callback_promise !== undefined) &&
        (typeof callback_promise.cancel === "function")) {
      callback_promise.cancel();
    }
  }

  function canceller() {
    if (handle_event_callback !== undefined) {
      target.removeEventListener(type, handle_event_callback, useCapture);
    }
    cancelResolver();
  }
  function itsANonResolvableTrap(resolve, reject) {

    handle_event_callback = function (evt) {
      evt.stopPropagation();
      evt.preventDefault();
      cancelResolver();
      callback_promise = new RSVP.Queue()
        .push(function () {
          return callback(evt);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            canceller();
            reject(error);
          }
        });
    };

    target.addEventListener(type, handle_event_callback, useCapture);
  }
  return new RSVP.Promise(itsANonResolvableTrap, canceller);
}

/*
 * renderJs - Generic Gadget library renderer.
 * http://www.renderjs.org/documentation
 */
(function (document, window, RSVP, DOMParser, Channel, undefined) {
  "use strict";

  var gadget_model_dict = {},
    javascript_registration_dict = {},
    stylesheet_registration_dict = {},
    gadget_loading_klass,
    loading_klass_promise,
    renderJS;

  function removeHash(url) {
    var index = url.indexOf('#');
    if (index > 0) {
      url = url.substring(0, index);
    }
    return url;
  }

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget
  /////////////////////////////////////////////////////////////////
  function RenderJSGadget() {
    if (!(this instanceof RenderJSGadget)) {
      return new RenderJSGadget();
    }
  }
  RenderJSGadget.prototype.__title = "";
  RenderJSGadget.prototype.__interface_list = [];
  RenderJSGadget.prototype.__path = "";
  RenderJSGadget.prototype.__html = "";
  RenderJSGadget.prototype.__required_css_list = [];
  RenderJSGadget.prototype.__required_js_list = [];

  function clearGadgetInternalParameters(g) {
    g.__sub_gadget_dict = {};
    g.__monitor = new RSVP.Monitor();
    g.__monitor.fail(console.error);
  }

  function loadSubGadgetDOMDeclaration(g) {
    var element_list = g.__element.querySelectorAll('[data-gadget-scope]'),
      element,
      promise_list = [],
      scope,
      url,
      sandbox,
      i;

    for (i = 0; i < element_list.length; i += 1) {
      element = element_list[i];
      scope = element.getAttribute("data-gadget-scope");
      url = element.getAttribute("data-gadget-url");
      sandbox = element.getAttribute("data-gadget-sandbox");
      if ((scope !== null) && (url !== null)) {
        promise_list.push(g.declareGadget(url, {
          element: element,
          scope: scope || undefined,
          sandbox: sandbox || undefined
        }));
      }
    }

    return RSVP.all(promise_list);
  }

  RenderJSGadget.__ready_list = [clearGadgetInternalParameters,
                                 loadSubGadgetDOMDeclaration];
  RenderJSGadget.ready = function (callback) {
    this.__ready_list.push(callback);
    return this;
  };

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget.declareMethod
  /////////////////////////////////////////////////////////////////
  RenderJSGadget.declareMethod = function (name, callback) {
    this.prototype[name] = function () {
      var context = this,
        argument_list = arguments;

      return new RSVP.Queue()
        .push(function () {
          return callback.apply(context, argument_list);
        });
    };
    // Allow chain
    return this;
  };

  RenderJSGadget
    .declareMethod('getInterfaceList', function () {
      // Returns the list of gadget prototype
      return this.__interface_list;
    })
    .declareMethod('getRequiredCSSList', function () {
      // Returns a list of CSS required by the gadget
      return this.__required_css_list;
    })
    .declareMethod('getRequiredJSList', function () {
      // Returns a list of JS required by the gadget
      return this.__required_js_list;
    })
    .declareMethod('getPath', function () {
      // Returns the path of the code of a gadget
      return this.__path;
    })
    .declareMethod('getTitle', function () {
      // Returns the title of a gadget
      return this.__title;
    })
    .declareMethod('getElement', function () {
      // Returns the DOM Element of a gadget
      if (this.__element === undefined) {
        throw new Error("No element defined");
      }
      return this.__element;
    });

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget.declareAcquiredMethod
  /////////////////////////////////////////////////////////////////
  function acquire(child_gadget, method_name, argument_list) {
    var gadget = this,
      key,
      gadget_scope;

    for (key in gadget.__sub_gadget_dict) {
      if (gadget.__sub_gadget_dict.hasOwnProperty(key)) {
        if (gadget.__sub_gadget_dict[key] === child_gadget) {
          gadget_scope = key;
        }
      }
    }
    return new RSVP.Queue()
      .push(function () {
        // Do not specify default __acquired_method_dict on prototype
        // to prevent modifying this default value (with
        // allowPublicAcquiredMethod for example)
        var aq_dict = gadget.__acquired_method_dict || {};
        if (aq_dict.hasOwnProperty(method_name)) {
          return aq_dict[method_name].apply(gadget,
                                            [argument_list, gadget_scope]);
        }
        throw new renderJS.AcquisitionError("aq_dynamic is not defined");
      })
      .push(undefined, function (error) {
        if (error instanceof renderJS.AcquisitionError) {
          return gadget.__aq_parent(method_name, argument_list);
        }
        throw error;
      });
  }

  RenderJSGadget.declareAcquiredMethod =
    function (name, method_name_to_acquire) {
      this.prototype[name] = function () {
        var argument_list = Array.prototype.slice.call(arguments, 0),
          gadget = this;
        return new RSVP.Queue()
          .push(function () {
            return gadget.__aq_parent(method_name_to_acquire, argument_list);
          });
      };

      // Allow chain
      return this;
    };
  RenderJSGadget.declareAcquiredMethod("aq_pleasePublishMyState",
                                       "pleasePublishMyState");

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget.declareListener
  /////////////////////////////////////////////////////////////////
  RenderJSGadget.declareListener = function (name, callback) {
    this.prototype[name] = function () {
      var argument_list = Array.prototype.slice.call(arguments, 0),
        gadget = this;
      console.log("Trying to start listener " + name);
      gadget.__monitor.monitor(callback.apply(this, argument_list));
    };

    // Allow chain
    return this;
  };

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget.allowPublicAcquisition
  /////////////////////////////////////////////////////////////////
  RenderJSGadget.allowPublicAcquisition =
    function (method_name, callback) {
      this.prototype.__acquired_method_dict[method_name] = callback;

      // Allow chain
      return this;
    };

  // Set aq_parent on gadget_instance which call acquire on parent_gadget
  function setAqParent(gadget_instance, parent_gadget) {
    gadget_instance.__aq_parent = function (method_name, argument_list) {
      return acquire.apply(parent_gadget, [gadget_instance, method_name,
                                           argument_list]);
    };
  }

  function pleasePublishMyState(param_list, child_gadget_scope) {
    var new_param = {},
      key;
    for (key in this.state_parameter_dict) {
      if (this.state_parameter_dict.hasOwnProperty(key)) {
        new_param[key] = this.state_parameter_dict[key];
      }
    }
    if (child_gadget_scope === undefined) {
      throw new Error("gadget scope is mandatory");
    }
    new_param[child_gadget_scope] = param_list[0];
    param_list = [new_param];
    return this.aq_pleasePublishMyState.apply(this, param_list);
  }

  /////////////////////////////////////////////////////////////////
  // RenderJSEmbeddedGadget
  /////////////////////////////////////////////////////////////////
  // Class inheritance
  function RenderJSEmbeddedGadget() {
    if (!(this instanceof RenderJSEmbeddedGadget)) {
      return new RenderJSEmbeddedGadget();
    }
    RenderJSGadget.call(this);
  }
  RenderJSEmbeddedGadget.__ready_list = RenderJSGadget.__ready_list.slice();
  RenderJSEmbeddedGadget.ready =
    RenderJSGadget.ready;
  RenderJSEmbeddedGadget.prototype = new RenderJSGadget();
  RenderJSEmbeddedGadget.prototype.constructor = RenderJSEmbeddedGadget;

  /////////////////////////////////////////////////////////////////
  // privateDeclarePublicGadget
  /////////////////////////////////////////////////////////////////
  function privateDeclarePublicGadget(url, options, parent_gadget) {
    var gadget_instance;
    if (options.element === undefined) {
      options.element = document.createElement("div");
    }

    function loadDependency(method, url) {
      return function () {
        return method(url);
      };
    }

    return new RSVP.Queue()
      .push(function () {
        return renderJS.declareGadgetKlass(url);
      })
      // Get the gadget class and instanciate it
      .push(function (Klass) {
        var i,
          template_node_list = Klass.__template_element.body.childNodes;
        gadget_loading_klass = Klass;
        gadget_instance = new Klass();
        gadget_instance.__element = options.element;
        for (i = 0; i < template_node_list.length; i += 1) {
          gadget_instance.__element.appendChild(
            template_node_list[i].cloneNode(true)
          );
        }
        setAqParent(gadget_instance, parent_gadget);
        // Load dependencies if needed
        return RSVP.all([
          gadget_instance.getRequiredJSList(),
          gadget_instance.getRequiredCSSList()
        ]);
      })
      // Load all JS/CSS
      .push(function (all_list) {
        var q = new RSVP.Queue(),
          i;
        // Load JS
        for (i = 0; i < all_list[0].length; i += 1) {
          q.push(loadDependency(renderJS.declareJS, all_list[0][i]));
        }
        // Load CSS
        for (i = 0; i < all_list[1].length; i += 1) {
          q.push(loadDependency(renderJS.declareCSS, all_list[1][i]));
        }
        return q;
      })
      .push(function () {
        return gadget_instance;
      });
  }

  /////////////////////////////////////////////////////////////////
  // RenderJSIframeGadget
  /////////////////////////////////////////////////////////////////
  function RenderJSIframeGadget() {
    if (!(this instanceof RenderJSIframeGadget)) {
      return new RenderJSIframeGadget();
    }
    RenderJSGadget.call(this);
  }
  RenderJSIframeGadget.__ready_list = RenderJSGadget.__ready_list.slice();
  RenderJSIframeGadget.ready =
    RenderJSGadget.ready;
  RenderJSIframeGadget.prototype = new RenderJSGadget();
  RenderJSIframeGadget.prototype.constructor = RenderJSIframeGadget;

  /////////////////////////////////////////////////////////////////
  // privateDeclareIframeGadget
  /////////////////////////////////////////////////////////////////
  function privateDeclareIframeGadget(url, options, parent_gadget) {
    var gadget_instance,
      iframe,
      node,
      iframe_loading_deferred = RSVP.defer();
    if (options.element === undefined) {
      throw new Error("DOM element is required to create Iframe Gadget " +
                      url);
    }

    // Check if the element is attached to the DOM
    node = options.element.parentNode;
    while (node !== null) {
      if (node === document) {
        break;
      }
      node = node.parentNode;
    }
    if (node === null) {
      throw new Error("The parent element is not attached to the DOM for " +
                      url);
    }

    gadget_instance = new RenderJSIframeGadget();
    setAqParent(gadget_instance, parent_gadget);
    iframe = document.createElement("iframe");
//    gadget_instance.element.setAttribute("seamless", "seamless");
    iframe.setAttribute("src", url);
    gadget_instance.__path = url;
    gadget_instance.__element = options.element;
    // Attach it to the DOM
    options.element.appendChild(iframe);

    // XXX Manage unbind when deleting the gadget

    // Create the communication channel with the iframe
    gadget_instance.__chan = Channel.build({
      window: iframe.contentWindow,
      origin: "*",
      scope: "renderJS"
    });

    // Create new method from the declareMethod call inside the iframe
    gadget_instance.__chan.bind("declareMethod",
                                function (trans, method_name) {
        gadget_instance[method_name] = function () {
          var argument_list = arguments;
          return new RSVP.Promise(function (resolve, reject) {
            gadget_instance.__chan.call({
              method: "methodCall",
              params: [
                method_name,
                Array.prototype.slice.call(argument_list, 0)],
              success: function (s) {
                resolve(s);
              },
              error: function (e) {
                reject(e);
              }
            });
          });
        };
        return "OK";
      });

    // Wait for the iframe to be loaded before continuing
    gadget_instance.__chan.bind("ready", function (trans) {
      iframe_loading_deferred.resolve(gadget_instance);
      return "OK";
    });
    gadget_instance.__chan.bind("failed", function (trans, params) {
      iframe_loading_deferred.reject(params);
      return "OK";
    });
    gadget_instance.__chan.bind("acquire", function (trans, params) {
      gadget_instance.__aq_parent.apply(gadget_instance, params)
        .then(function (g) {
          trans.complete(g);
        }).fail(function (e) {
          trans.error(e.toString());
        });
      trans.delayReturn(true);
    });

    return RSVP.any([
      iframe_loading_deferred.promise,
      // Timeout to prevent non renderJS embeddable gadget
      // XXX Maybe using iframe.onload/onerror would be safer?
      RSVP.timeout(5000)
    ]);
  }

  /////////////////////////////////////////////////////////////////
  // RenderJSGadget.declareGadget
  /////////////////////////////////////////////////////////////////
  RenderJSGadget
    .declareMethod('declareGadget', function (url, options) {
      var queue,
        parent_gadget = this,
        local_loading_klass_promise,
        previous_loading_klass_promise = loading_klass_promise;

      if (options === undefined) {
        options = {};
      }
      if (options.sandbox === undefined) {
        options.sandbox = "public";
      }

      // transform url to absolute url if it is relative
      url = renderJS.getAbsoluteURL(url, this.__path);
      // Change the global variable to update the loading queue
      loading_klass_promise = new RSVP.Queue()
        // Wait for previous gadget loading to finish first
        .push(function () {
          return previous_loading_klass_promise;
        })
        .push(undefined, function () {
          // Forget previous declareGadget error
          return;
        })
        .push(function () {
          var method;
          if (options.sandbox === "public") {
            method = privateDeclarePublicGadget;
          } else if (options.sandbox === "iframe") {
            method = privateDeclareIframeGadget;
          } else {
            throw new Error("Unsupported sandbox options '" +
                            options.sandbox + "'");
          }
          return method(url, options, parent_gadget);
        })
        // Set the HTML context
        .push(function (gadget_instance) {
          // Drop the current loading klass info used by selector
          gadget_loading_klass = undefined;
          return gadget_instance;
        })
        .push(undefined, function (e) {
          // Drop the current loading klass info used by selector
          // even in case of error
          gadget_loading_klass = undefined;
          throw e;
        });
      local_loading_klass_promise = loading_klass_promise;

      queue = new RSVP.Queue()
        .push(function () {
          return local_loading_klass_promise;
        })
        // Set the HTML context
        .push(function (gadget_instance) {
          var i;
          // Trigger calling of all ready callback
          function ready_wrapper() {
            return gadget_instance;
          }
          for (i = 0; i < gadget_instance.constructor.__ready_list.length;
               i += 1) {
            // Put a timeout?
            queue.push(gadget_instance.constructor.__ready_list[i]);
            // Always return the gadget instance after ready function
            queue.push(ready_wrapper);
          }

          // Store local reference to the gadget instance
          if (options.scope !== undefined) {
            parent_gadget.__sub_gadget_dict[options.scope] = gadget_instance;
            gadget_instance.__element.setAttribute("data-gadget-scope",
                                                   options.scope);
          }

          // Put some attribute to ease page layout comprehension
          gadget_instance.__element.setAttribute("data-gadget-url", url);
          gadget_instance.__element.setAttribute("data-gadget-sandbox",
                                                 options.sandbox);

          return gadget_instance;
        });
      return queue;
    })
    .declareMethod('getDeclaredGadget', function (gadget_scope) {
      if (!this.__sub_gadget_dict.hasOwnProperty(gadget_scope)) {
        throw new Error("Gadget scope '" + gadget_scope + "' is not known.");
      }
      return this.__sub_gadget_dict[gadget_scope];
    })
    .declareMethod('dropGadget', function (gadget_scope) {
      if (!this.__sub_gadget_dict.hasOwnProperty(gadget_scope)) {
        throw new Error("Gadget scope '" + gadget_scope + "' is not known.");
      }
      // http://perfectionkills.com/understanding-delete/
      delete this.__sub_gadget_dict[gadget_scope];
    });

  /////////////////////////////////////////////////////////////////
  // renderJS selector
  /////////////////////////////////////////////////////////////////
  renderJS = function (selector) {
    var result;
    if (selector === window) {
      // window is the 'this' value when loading a javascript file
      // In this case, use the current loading gadget constructor
      result = gadget_loading_klass;
    }
    if (result === undefined) {
      throw new Error("Unknown selector '" + selector + "'");
    }
    return result;
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.AcquisitionError
  /////////////////////////////////////////////////////////////////
  renderJS.AcquisitionError = function (message) {
    this.name = "AcquisitionError";
    if ((message !== undefined) && (typeof message !== "string")) {
      throw new TypeError('You must pass a string.');
    }
    this.message = message || "Acquisition failed";
  };
  renderJS.AcquisitionError.prototype = new Error();
  renderJS.AcquisitionError.prototype.constructor =
    renderJS.AcquisitionError;

  /////////////////////////////////////////////////////////////////
  // renderJS.getAbsoluteURL
  /////////////////////////////////////////////////////////////////
  renderJS.getAbsoluteURL = function (url, base_url) {
    var doc, base, link,
      html = "<!doctype><html><head></head></html>",
      isAbsoluteOrDataURL = new RegExp('^(?:[a-z]+:)?//|data:', 'i');

    if (url && base_url && !isAbsoluteOrDataURL.test(url)) {
      doc = (new DOMParser()).parseFromString(html, 'text/html');
      base = doc.createElement('base');
      link = doc.createElement('link');
      doc.head.appendChild(base);
      doc.head.appendChild(link);
      base.href = base_url;
      link.href = url;
      return link.href;
    }
    return url;
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.declareJS
  /////////////////////////////////////////////////////////////////
  renderJS.declareJS = function (url) {
    // Prevent infinite recursion if loading render.js
    // more than once
    var result;
    if (javascript_registration_dict.hasOwnProperty(url)) {
      result = RSVP.resolve();
    } else {
      result = new RSVP.Promise(function (resolve, reject) {
        var newScript;
        newScript = document.createElement('script');
        newScript.type = 'text/javascript';
        newScript.src = url;
        newScript.onload = function () {
          javascript_registration_dict[url] = null;
          resolve();
        };
        newScript.onerror = function (e) {
          reject(e);
        };
        document.head.appendChild(newScript);
      });
    }
    return result;
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.declareCSS
  /////////////////////////////////////////////////////////////////
  renderJS.declareCSS = function (url) {
    // https://github.com/furf/jquery-getCSS/blob/master/jquery.getCSS.js
    // No way to cleanly check if a css has been loaded
    // So, always resolve the promise...
    // http://requirejs.org/docs/faq-advanced.html#css
    var result;
    if (stylesheet_registration_dict.hasOwnProperty(url)) {
      result = RSVP.resolve();
    } else {
      result = new RSVP.Promise(function (resolve, reject) {
        var link;
        link = document.createElement('link');
        link.rel = 'stylesheet';
        link.type = 'text/css';
        link.href = url;
        link.onload = function () {
          stylesheet_registration_dict[url] = null;
          resolve();
        };
        link.onerror = function (e) {
          reject(e);
        };
        document.head.appendChild(link);
      });
    }
    return result;
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.declareGadgetKlass
  /////////////////////////////////////////////////////////////////
  renderJS.declareGadgetKlass = function (url) {
    var result,
      xhr;

    function parse() {
      var tmp_constructor,
        key,
        parsed_html;
      if (!gadget_model_dict.hasOwnProperty(url)) {
        // Class inheritance
        tmp_constructor = function () {
          RenderJSGadget.call(this);
        };
        tmp_constructor.__ready_list = RenderJSGadget.__ready_list.slice();
        tmp_constructor.declareMethod =
          RenderJSGadget.declareMethod;
        tmp_constructor.declareListener =
          RenderJSGadget.declareListener;
        tmp_constructor.declareAcquiredMethod =
          RenderJSGadget.declareAcquiredMethod;
        tmp_constructor.allowPublicAcquisition =
          RenderJSGadget.allowPublicAcquisition;
        tmp_constructor.ready =
          RenderJSGadget.ready;
        tmp_constructor.prototype = new RenderJSGadget();
        tmp_constructor.prototype.constructor = tmp_constructor;
        tmp_constructor.prototype.__path = url;
        tmp_constructor.prototype.__acquired_method_dict = {};
        tmp_constructor.allowPublicAcquisition("pleasePublishMyState",
                                               pleasePublishMyState);
        // https://developer.mozilla.org/en-US/docs/HTML_in_XMLHttpRequest
        // https://developer.mozilla.org/en-US/docs/Web/API/DOMParser
        // https://developer.mozilla.org/en-US/docs/Code_snippets/HTML_to_DOM
        tmp_constructor.__template_element =
          (new DOMParser()).parseFromString(xhr.responseText, "text/html");
        parsed_html = renderJS.parseGadgetHTMLDocument(
          tmp_constructor.__template_element,
          url
        );
        for (key in parsed_html) {
          if (parsed_html.hasOwnProperty(key)) {
            tmp_constructor.prototype['__' + key] = parsed_html[key];
          }
        }

        gadget_model_dict[url] = tmp_constructor;
      }

      return gadget_model_dict[url];
    }

    function resolver(resolve, reject) {
      function handler() {
        var tmp_result;
        try {
          if (xhr.readyState === 0) {
            // UNSENT
            reject(xhr);
          } else if (xhr.readyState === 4) {
            // DONE
            if ((xhr.status < 200) || (xhr.status >= 300) ||
                (!/^text\/html[;]?/.test(
                  xhr.getResponseHeader("Content-Type") || ""
                ))) {
              reject(xhr);
            } else {
              tmp_result = parse();
              resolve(tmp_result);
            }
          }
        } catch (e) {
          reject(e);
        }
      }

      xhr = new XMLHttpRequest();
      xhr.open("GET", url);
      xhr.onreadystatechange = handler;
      xhr.setRequestHeader('Accept', 'text/html');
      xhr.withCredentials = true;
      xhr.send();
    }

    function canceller() {
      if ((xhr !== undefined) && (xhr.readyState !== xhr.DONE)) {
        xhr.abort();
      }
    }

    if (gadget_model_dict.hasOwnProperty(url)) {
      // Return klass object if it already exists
      result = RSVP.resolve(gadget_model_dict[url]);
    } else {
      // Fetch the HTML page and parse it
      result = new RSVP.Promise(resolver, canceller);
    }
    return result;
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.clearGadgetKlassList
  /////////////////////////////////////////////////////////////////
  // For test purpose only
  renderJS.clearGadgetKlassList = function () {
    gadget_model_dict = {};
    javascript_registration_dict = {};
    stylesheet_registration_dict = {};
  };

  /////////////////////////////////////////////////////////////////
  // renderJS.parseGadgetHTMLDocument
  /////////////////////////////////////////////////////////////////
  renderJS.parseGadgetHTMLDocument = function (document_element, url) {
    var settings = {
        title: "",
        interface_list: [],
        required_css_list: [],
        required_js_list: []
      },
      i,
      element,
      isAbsoluteURL = new RegExp('^(?:[a-z]+:)?//', 'i');

    if (!url || !isAbsoluteURL.test(url)) {
      throw new Error("The url should be absolute: " + url);
    }

    if (document_element.nodeType === 9) {
      settings.title = document_element.title;

      for (i = 0; i < document_element.head.children.length; i += 1) {
        element = document_element.head.children[i];
        if (element.href !== null) {
          // XXX Manage relative URL during extraction of URLs
          // element.href returns absolute URL in firefox but "" in chrome;
          if (element.rel === "stylesheet") {
            settings.required_css_list.push(
              renderJS.getAbsoluteURL(element.getAttribute("href"), url)
            );
          } else if (element.nodeName === "SCRIPT" &&
                     (element.type === "text/javascript" ||
                      !element.type)) {
            settings.required_js_list.push(
              renderJS.getAbsoluteURL(element.getAttribute("src"), url)
            );
          } else if (element.rel === "http://www.renderjs.org/rel/interface") {
            settings.interface_list.push(
              renderJS.getAbsoluteURL(element.getAttribute("href"), url)
            );
          }
        }
      }
    } else {
      throw new Error("The first parameter should be an HTMLDocument");
    }
    return settings;
  };

  /////////////////////////////////////////////////////////////////
  // global
  /////////////////////////////////////////////////////////////////
  window.rJS = window.renderJS = renderJS;
  window.__RenderJSGadget = RenderJSGadget;
  window.__RenderJSEmbeddedGadget = RenderJSEmbeddedGadget;
  window.__RenderJSIframeGadget = RenderJSIframeGadget;

  ///////////////////////////////////////////////////
  // Bootstrap process. Register the self gadget.
  ///////////////////////////////////////////////////

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

  function bootstrap() {
    var url = removeHash(window.location.href),
      tmp_constructor,
      root_gadget,
      loading_gadget_promise = new RSVP.Queue(),
      declare_method_count = 0,
      embedded_channel,
      notifyReady,
      notifyDeclareMethod,
      gadget_ready = false,
      last_acquisition_gadget;

    // Create the gadget class for the current url
    if (gadget_model_dict.hasOwnProperty(url)) {
      throw new Error("bootstrap should not be called twice");
    }
    loading_klass_promise = new RSVP.Promise(function (resolve, reject) {
      if (window.self === window.top) {

        last_acquisition_gadget = new RenderJSGadget();
        last_acquisition_gadget.__acquired_method_dict = {
          getTopURL: function () {
            return url;
          },
          pleaseRedirectMyHash: function (param_list) {
            window.location.replace(param_list[0]);
          },
          pleasePublishMyState: function (param_list) {
            var key,
              first = true,
              hash = "#";
            param_list[0] = mergeSubDict(param_list[0]);
            for (key in param_list[0]) {
              if (param_list[0].hasOwnProperty(key)) {
                if (!first) {
                  hash += "&";
                }
                hash += encodeURIComponent(key) + "=" +
                  encodeURIComponent(param_list[0][key]);
                first = false;
              }
            }
            return hash;
          }
        };
        // Stop acquisition on the last acquisition gadget
        // Do not put this on the klass, as their could be multiple instances
        last_acquisition_gadget.__aq_parent = function (method_name) {
          throw new renderJS.AcquisitionError(
            "No gadget provides " + method_name
          );
        };

        // XXX Copy/Paste from declareGadgetKlass
        tmp_constructor = function () {
          RenderJSGadget.call(this);
        };
        tmp_constructor.declareMethod = RenderJSGadget.declareMethod;
        tmp_constructor.declareListener =
          RenderJSGadget.declareListener;
        tmp_constructor.declareAcquiredMethod =
          RenderJSGadget.declareAcquiredMethod;
        tmp_constructor.allowPublicAcquisition =
          RenderJSGadget.allowPublicAcquisition;
        tmp_constructor.__ready_list = RenderJSGadget.__ready_list.slice();
        tmp_constructor.ready = RenderJSGadget.ready;
        tmp_constructor.prototype = new RenderJSGadget();
        tmp_constructor.prototype.constructor = tmp_constructor;
        tmp_constructor.prototype.__path = url;
        gadget_model_dict[url] = tmp_constructor;

        // Create the root gadget instance and put it in the loading stack
        root_gadget = new gadget_model_dict[url]();

        setAqParent(root_gadget, last_acquisition_gadget);

      } else {
        // Create the communication channel
        embedded_channel = Channel.build({
          window: window.parent,
          origin: "*",
          scope: "renderJS"
        });
        // Create the root gadget instance and put it in the loading stack
        tmp_constructor = RenderJSEmbeddedGadget;
        tmp_constructor.__ready_list = RenderJSGadget.__ready_list.slice();
        tmp_constructor.prototype.__path = url;
        root_gadget = new RenderJSEmbeddedGadget();

        // Bind calls to renderJS method on the instance
        embedded_channel.bind("methodCall", function (trans, v) {
          root_gadget[v[0]].apply(root_gadget, v[1]).then(function (g) {
            trans.complete(g);
          }).fail(function (e) {
            trans.error(e.toString());
          });
          trans.delayReturn(true);
        });

        // Notify parent about gadget instanciation
        notifyReady = function () {
          if ((declare_method_count === 0) && (gadget_ready === true)) {
            embedded_channel.notify({method: "ready"});
          }
        };

        // Inform parent gadget about declareMethod calls here.
        notifyDeclareMethod = function (name) {
          declare_method_count += 1;
          embedded_channel.call({
            method: "declareMethod",
            params: name,
            success: function () {
              declare_method_count -= 1;
              notifyReady();
            },
            error: function () {
              declare_method_count -= 1;
            }
          });
        };

        notifyDeclareMethod("getInterfaceList");
        notifyDeclareMethod("getRequiredCSSList");
        notifyDeclareMethod("getRequiredJSList");
        notifyDeclareMethod("getPath");
        notifyDeclareMethod("getTitle");

        // Surcharge declareMethod to inform parent window
        tmp_constructor.declareMethod = function (name, callback) {
          var result = RenderJSGadget.declareMethod.apply(
              this,
              [name, callback]
            );
          notifyDeclareMethod(name);
          return result;
        };

        tmp_constructor.declareListener =
          RenderJSGadget.declareListener;
        tmp_constructor.declareAcquiredMethod =
          RenderJSGadget.declareAcquiredMethod;
        tmp_constructor.allowPublicAcquisition =
          RenderJSGadget.allowPublicAcquisition;

        // Define __aq_parent to inform parent window
        tmp_constructor.prototype.__aq_parent = function (method_name,
          argument_list) {
          return new RSVP.Promise(function (resolve, reject) {
            embedded_channel.call({
              method: "acquire",
              params: [
                method_name,
                argument_list
              ],
              success: function (s) {
                resolve(s);
              },
              error: function (e) {
                reject(e);
              }
            });
          });
        };
      }

      tmp_constructor.prototype.__acquired_method_dict = {};
      tmp_constructor.allowPublicAcquisition("pleasePublishMyState",
                                             pleasePublishMyState);
      gadget_loading_klass = tmp_constructor;

      function init() {
        // XXX HTML properties can only be set when the DOM is fully loaded
        var settings = renderJS.parseGadgetHTMLDocument(document, url),
          j,
          key;
        for (key in settings) {
          if (settings.hasOwnProperty(key)) {
            tmp_constructor.prototype['__' + key] = settings[key];
          }
        }
        tmp_constructor.__template_element = document.createElement("div");
        root_gadget.__element = document.body;
        for (j = 0; j < root_gadget.__element.childNodes.length; j += 1) {
          tmp_constructor.__template_element.appendChild(
            root_gadget.__element.childNodes[j].cloneNode(true)
          );
        }
        RSVP.all([root_gadget.getRequiredJSList(),
                  root_gadget.getRequiredCSSList()])
          .then(function (all_list) {
            var i,
              js_list = all_list[0],
              css_list = all_list[1];
            for (i = 0; i < js_list.length; i += 1) {
              javascript_registration_dict[js_list[i]] = null;
            }
            for (i = 0; i < css_list.length; i += 1) {
              stylesheet_registration_dict[css_list[i]] = null;
            }
            gadget_loading_klass = undefined;
            return root_gadget;
          }).then(resolve, function (e) {
            reject(e);
            /*global console */
            console.error(e);
            throw e;
          });
      }
      document.addEventListener('DOMContentLoaded', init, false);
    });

    loading_gadget_promise
      .push(function () {
        return loading_klass_promise;
      })
      .push(function (root_gadget) {
        var i;

        function ready_wrapper() {
          return root_gadget;
        }

        if (window.top !== window.self) {
          tmp_constructor.ready(function () {
            var base = document.createElement('base');
            return root_gadget.__aq_parent('getTopURL', [])
              .then(function (topURL) {
                base.href = topURL;
                base.target = "_top";
                document.head.appendChild(base);
              });
          });
        }

        loading_gadget_promise.push(ready_wrapper);
        for (i = 0; i < tmp_constructor.__ready_list.length; i += 1) {
          // Put a timeout?
          loading_gadget_promise
            .push(tmp_constructor.__ready_list[i])
            // Always return the gadget instance after ready function
            .push(ready_wrapper);
        }
      });
    if (window.self !== window.top) {
      // Inform parent window that gadget is correctly loaded
      loading_gadget_promise
        .then(function () {
          gadget_ready = true;
          notifyReady();
        })
        .fail(function (e) {
          embedded_channel.notify({method: "failed", params: e.toString()});
          throw e;
        });
    } else {
      // XXX Bootstrap run
      loading_gadget_promise
        .then(function () {

          function extractHashAndDispatch(evt) {
            var hash = evt.newURL.split('#')[1],
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

            if (root_gadget.render !== undefined) {
              return root_gadget.render(options);
            }
          }

          // XXX Manually trigger hashchange event!
          return RSVP.all([
            extractHashAndDispatch({newURL: window.location.toString()}),
            loopEventListener(window, 'hashchange', false,
                                   extractHashAndDispatch)
          ]);

        }).fail(function (e) {
          // XXX Do not crash the application if it fails
          // Where to write the error?
          if (e.constructor === XMLHttpRequest) {
            console.error(e);
            e = {
              readyState: e.readyState,
              status: e.status,
              statusText: e.statusText,
              response_headers: e.getAllResponseHeaders()
            };
          }
          if (e.constructor === Array ||
              e.constructor === String ||
              e.constructor === Object) {
            try {
              e = JSON.stringify(e);
            } catch (exception) {
              console.error(exception);
            }
          }
          console.warn(e);
          document.getElementsByTagName('body')[0].textContent = e;
        });


    }

  }
  bootstrap();

}(document, window, RSVP, DOMParser, Channel));
