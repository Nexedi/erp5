/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker, importScripts,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */





/*************************************************************************/
/**************************** ROQUE WW EVENTS ****************************/
/*************************************************************************/

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
	defaultView: self.window,
};

importScripts('babylon.js', 'babylon.gui.js');
importScripts('rsvp.js',
              'GameManager.js',
              'DroneManager.js',
              'MapManager.js',
              'ObstacleManager.js',
              'DroneAaileFixeAPI.js',
              'DroneLogAPI.js',
              'DroneAPI.js',
              'gadget_erp5_page_game_logic.js');

function mainToWorker(evt) {
  switch (evt.data.type) {
    case 'start':
      var offscreen_canvas = prepareCanvas(evt.data);
      RSVP = window.RSVP;
      return new RSVP.Queue()
        .push(function () {
          postMessage({'type': 'started'});
          return runGame(offscreen_canvas, evt.data.script,
                         evt.data.game_parameters_json, evt.data.log);
        })
        .push(function (result) {
          return postMessage({'type': 'finished', 'result': result});
        }, function(error) {
          console.log("ERROR:", error);
          return postMessage({'type': 'error', 'error': error});
        });
      break;
    case 'update':
      return new RSVP.Queue()
        .push(function () {
          return updateGame();
        })
        .push(function () {
          return postMessage({'type': 'updated'});
        });
      break;
    case 'event':
      handleEvent(evt.data);
      break;
    default:
      throw new Error('Unsupported message ' + JSON.stringify(evt.data));
  }
};

// Doesn't work without it
class HTMLElement {}

self.handlers = new Map();
self.canvas = null;

// getBoundingInfo()
const rect = {
	top: 0,
	left: 0,
	right: 0,
	bottom: 0,
	x: 0,
	y: 0,
	height: 0,
	width: 0,
};

function bindHandler(targetName, eventName, fn, opt) {
	const handlerId = targetName + eventName;
  console.log("[WEBWORKER] bindHandler. handlerId:", handlerId);
	handlers.set(handlerId, fn);
	postMessage({
		type: 'event',
		targetName: targetName,
		eventName: eventName,
		opt: opt,
	})
}

function handleEvent(event) {
	const handlerId = event.targetName + event.eventName;
	event.eventClone.preventDefault = noop;
	event.eventClone.target = self.canvas;
	if (!handlers.has(handlerId)) {
		throw new Error('Unknown handlerId: ' + handlerId);
	}
	handlers.get(handlerId)(event.eventClone);
}

function prepareCanvas(data) {
	const canvas = data.canvas;
  self.canvas = canvas;
	canvas.clientWidth = data.width;
	canvas.clientHeight = data.height;
	canvas.width = data.width;
	canvas.height = data.height;
	rect.right = rect.width = data.width;
	rect.bottom = rect.height = data.height;
	canvas.setAttribute = function (name, value) {
		postMessage({
			type: 'canvasMethod',
			method: 'setAttribute',
			args: [name, value],
		})
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
			args: [],
		})
	};
	// noinspection JSUnusedGlobalSymbols
	const style = {
		set touchAction(value) {
			postMessage({
				type: 'canvasStyle',
				name: 'touchAction',
				value: value,
			})
		}
	};
	Object.defineProperty(canvas, 'style', {get() {return style}});
	return canvas;
}

function noop() {}

(function (worker) {
  worker.onmessage = mainToWorker;
  worker.postMessage({
    'type': 'loaded'
  });
}(this));