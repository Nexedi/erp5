/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker, importScripts,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
// game.js

var handlers = new Map();

var document = {
  addEventListener: function () {},
  createElement: function () {}
};

(function (worker) {
  importScripts('babylon.js', 'babylon.gui.js');
}(this));

/*var window = {
  addEventListener: function () {}
};*/
var window = {
  addEventListener: function (event, fn, opt) {
    bindHandler('window', event, fn, opt);
  },
  PointerEvent: true
};

document = {
  addEventListener: function (event, fn, opt) {
    bindHandler('document', event, fn, opt);
  },
	// Uses to detect wheel event like at src/Inputs/scene.inputManager.ts:797
  createElement: function () {
    return {onwheel: true};
  },
  defaultView: window
};

function bindHandler(targetName, eventName, fn, opt) {
  console.log("bindHandler. eventName:", eventName);
	const handlerId = targetName + eventName;
	handlers.set(handlerId, fn);
	postMessage({
		type: 'event',
		targetName: targetName,
		eventName: eventName,
		opt: opt,
	})
}

function prepareCanvas(data) {
	const canvas = data.canvas;
	//self.canvas = canvas;
	canvas.clientWidth = data.width;
	canvas.clientHeight = data.height;
	canvas.width = data.width;
	canvas.height = data.height;
  //This seems to be needed for resize
	/*rect.right = rect.width = data.width;
	rect.bottom = rect.height = data.height;
  canvas.getBoundingClientRect = function () {
		return rect;
	};*/
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

// game.js
(function (worker) {
  console.log('worker loading');
  var offscreen_canvas;
  worker.onmessage = function (evt) {
    //console.log('Worker: Message received from main script', evt.data);
    var type = evt.data.type;
    if (type === 'start') {
      console.log('Worker: Message received from main script', evt.data);
      //offscreen_canvas = evt.data.canvas;
      offscreen_canvas = prepareCanvas(evt.data);
      console.log("offscreen_canvas:", offscreen_canvas);
      /*offscreen_canvas.addEventListener = function (event, fn, opt) {
        bindHandler('canvas', event, fn, opt);
      };*/
      //override createElement as it is needed by babylon to create a canvas
      document.createElement = function (type) {
        if (type === 'canvas') {
          return offscreen_canvas;//evt.data.canvas;
        }
        return {onwheel: true};
      }
      //TODO evt.data.logic_url should contain the list of scripts
      importScripts(
                    'rsvp.js',
                    'GameManager.js',
                    'DroneManager.js',
                    'MapManager.js',
                    'ObstacleManager.js',
                    'DroneAaileFixeAPI.js',
                    'DroneLogAPI.js',
                    'DroneAPI.js',
                    evt.data.logic_url);
      RSVP = window.RSVP;
      window = undefined;
      return new RSVP.Queue()
        .push(function () {
          //return runGame(evt.data.canvas, evt.data.script,
          return runGame(offscreen_canvas, evt.data.script,
                         evt.data.game_parameters_json, evt.data.log);
        })
        .push(function () {
          return worker.postMessage({'type': 'started'});
        });
    }
    if (type === 'update') {
      return new RSVP.Queue()
        .push(function () {
          return updateGame();
        })
        .push(function () {
          return worker.postMessage({'type': 'updated'});
        });
    }
    if (type === 'mousewheel') {
      //console.log("[TODO] mousewheel event in WW!!");
      //offscreen_canvas.trigger("mousewheel");
      return eventGame();
      return;
    }
    throw new Error('Unsupported message ' + JSON.stringify(evt.data));
    //self.postMessage('nutnut', evt);
  };
  worker.postMessage({
    'type': 'loaded'
  });
  //throw new Error('argh');
}(this));