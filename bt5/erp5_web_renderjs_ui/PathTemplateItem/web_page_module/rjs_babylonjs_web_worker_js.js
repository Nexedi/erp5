/*global self, window, rJS, jIO, RSVP, console, importScripts, bindHandler,
handlers, prepareCanvas, postMessage, runGame, updateGame, handleEvent*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

self.window = {
  addEventListener: function (event, fn, opt) {
    bindHandler('window', event, fn, opt);
  },
  setTimeout: self.setTimeout.bind(self),
  PointerEvent: true
};

self.document = {
  addEventListener: function (event, fn, opt) {
    bindHandler('document', event, fn, opt);
  },
  // Uses to detect wheel event like at src/Inputs/scene.inputManager.ts:797
  createElement: function () {
    return {onwheel: true};
  },
  defaultView: self.window
};

importScripts('babylon.js', 'babylon.gui.js', 'rsvp.js');

function mainToWorker(evt) {
  var i, offscreen_canvas;
  switch (evt.data.type) {
  case 'start':
    console.log("[WEB WORKER] Ready to handle the folliwing events:",
                handlers.keys());
    for (i = 0; i < evt.data.logic_url_list.length; i += 1) {
      importScripts(evt.data.logic_url_list[i]);
    }
    offscreen_canvas = prepareCanvas(evt.data);
    RSVP = window.RSVP;
    return new RSVP.Queue()
      .push(function () {
        postMessage({'type': 'started'});
        return runGame(offscreen_canvas, evt.data.game_parameters);
      })
      .push(function (result) {
        return postMessage({'type': 'finished', 'result': result});
      }, function (error) {
        console.log("ERROR:", error);
        return postMessage({'type': 'error', 'error': error});
      });
  case 'update':
    return new RSVP.Queue()
      .push(function () {
        return updateGame(evt.data.fullscreen);
      })
      .push(function () {
        return postMessage({'type': 'updated'});
      }, function (error) {
        console.log("ERROR:", error);
        return postMessage({'type': 'error', 'error': error});
      });
  case 'event':
    return new RSVP.Queue(handleEvent(evt.data))
      .push(undefined, function (error) {
        console.log("ERROR:", error);
        return postMessage({'type': 'error', 'error': error});
      });
  default:
    throw new Error('Unsupported message ' + JSON.stringify(evt.data));
  }
}

// Doesn't work without it
class HTMLElement {}

self.handlers = new Map();
self.canvas = null;

// getBoundingInfo()
var rect = {
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  x: 0,
  y: 0,
  height: 0,
  width: 0
};

function bindHandler(targetName, eventName, fn, opt) {
  var handlerId = targetName + eventName;
  handlers.set(handlerId, fn);
  postMessage({
    type: 'event',
    targetName: targetName,
    eventName: eventName,
    opt: opt
  });
}

function noop() {}

function handleEvent(event) {
  var handlerId = event.targetName + event.eventName;
  event.eventClone.preventDefault = noop;
  event.eventClone.target = self.canvas;
  if (!handlers.has(handlerId)) {
    throw new Error('Unknown handlerId: ' + handlerId);
  }
  handlers.get(handlerId)(event.eventClone);
}

function prepareCanvas(data) {
  var canvas = data.canvas, style;
  self.canvas = canvas;
  canvas.width = data.width;
  canvas.height = data.height;
  rect.right = rect.width = data.width;
  rect.bottom = rect.height = data.height;
  canvas.setAttribute = function (name, value) {
    postMessage({
      type: 'canvasMethod',
      method: 'setAttribute',
      args: [name, value]
    });
  };
  canvas.addEventListener = function (event, fn, opt) {
    bindHandler('canvas', event, fn, opt);
  };
  canvas.getBoundingClientRect = function () {
    return rect;
  };
  canvas.focus = function () {
    postMessage({
      type: 'canvasMethod',
      method: 'focus',
      args: []
    });
  };
  // noinspection JSUnusedGlobalSymbols
  style = {
    set touchAction (value) {
      postMessage({
        type: 'canvasStyle',
        name: 'touchAction',
        value: value
      });
    }
  };
  Object.defineProperty(canvas, 'style', {get () { return style }});
  return canvas;
}

(function (worker) {
  worker.onmessage = mainToWorker;
  worker.postMessage({
    'type': 'loaded'
  });
}(this));