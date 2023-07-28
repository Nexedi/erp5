/*global window, rJS, domsugar, RSVP, Set, Worker,
  requestAnimationFrame, cancelAnimationFrame*/
/*jslint nomen: true, indent: 2, maxlen: 80, white: true, evil: false */

(function (window, rJS, domsugar, RSVP, Set, Worker,
           requestAnimationFrame, cancelAnimationFrame) {
  "use strict";

  // Events props to send to worker
  var mouseEventFields = new Set(['altKey', 'bubbles', 'button', 'buttons',
    'cancelBubble', 'cancelable', 'clientX', 'clientY', 'composed', 'ctrlKey',
    'defaultPrevented', 'detail', 'eventPhase', 'fromElement', 'isTrusted',
    'layerX', 'layerY', 'metaKey', 'movementX', 'movementY', 'offsetX', 'pageX',
    'offsetY', 'pageY', 'relatedTarget', 'returnValue', 'screenX', 'screenY',
    'shiftKey', 'timeStamp', 'type', 'which', 'x', 'wheelDelta', 'wheelDeltaX',
    'wheelDeltaY', 'y', 'deltaX', 'deltaY', 'deltaZ', 'deltaMode'
    ]), game_result, canvas, offscreen, game_manager, container, background,
    fullscreen = false, fullscreen_delay,
    //TODO. Drop hardcoded values
    WIDTH = (window.innerWidth > 680) ? 680 : window.innerWidth * 0.96,
    HEIGHT = 340;

  //////////////////////////////////////////
  // Webworker
  //////////////////////////////////////////
  function handleWorker(url, callback) {
    var worker;

    function canceller() {
      worker.terminate();
    }

    function resolver(resolve, reject) {
      worker = new Worker(url);

      function handleError(error) {
        canceller();
        reject(error);
      }

      worker.onerror = handleError;
      var result;
      try {
        result = callback(worker);
      } catch (e) {
        return handleError(e);
      }

      new RSVP.Queue(result)
        .push(function (value) {
          canceller();
          console.log('resolve handle worker', value);
          resolve(value);
        }, handleError);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  //////////////////////////////////////////
  // promiseAnimationFrame
  //////////////////////////////////////////
  function promiseAnimationFrame() {
    var request_id;

    function canceller() {
      cancelAnimationFrame(request_id);
    }

    function resolver(resolve) {
      request_id = requestAnimationFrame(resolve);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  //////////////////////////////////////////
  // DroneGameManager
  //////////////////////////////////////////
  function DroneGameManager(gadget) {
    this._gadget = gadget;
    if (!(this instanceof DroneGameManager)) {
      return new DroneGameManager();
    }
  }
  DroneGameManager.prototype = {
    constructor: DroneGameManager,
    pause: function pauseGameManager() {
      console.log('pausing', this.loop_promise);
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not pause the game if not started');
      }
      if (this.hasOwnProperty('pause_defer')) {
        throw new Error('Can not pause the game if already paused');
      }
      this.pause_defer = RSVP.defer();
      var pause_defer = this.pause_defer;
      this.loop_promise
        .push(function () {
          return pause_defer.promise;
        });
    },
    unpause: function continueGameManager() {
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not unpause the game if not started');
      }
      if (!this.hasOwnProperty('pause_defer')) {
        throw new Error('Can not unpause the game if not paused');
      }
      this.pause_defer.resolve('unpause');
      var pause_defer = this.pause_defer;
      delete this.pause_defer;
    },
    quit: function stopGameManager() {
      if (!this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not quit the game if not started');
      }
      this.loop_promise.cancel('Stopping game manager');
      console.log('stopping game manager');
      delete this.loop_promise;
      delete this.pause_defer;
    },
    result: function resultGameManager() {
      return game_result;
    },
    fullscreen: function fullScreenGameManager() {
      return new RSVP.Queue()
        .push(function () {
          fullscreen = !fullscreen;
        })
        .push(function () {
          return RSVP.delay(fullscreen_delay);
        });
    },
    play: function startGameManager(options) {
      if (this.hasOwnProperty('loop_promise')) {
        throw new Error('Can not start the game if already started');
      }

      this.loop_promise = new RSVP.Queue();
      var loop_promise = this.loop_promise,
        context = this;
      this.pause();

      return RSVP.Queue(RSVP.any([
        loop_promise,
        handleWorker('gadget_erp5_page_babylonjs_web_worker.js',
                     function (worker) {

            var message_error_handler_defer = RSVP.defer(),
              update_defer = null;

            function step() {
              context.loop_promise
                .push(function () {
                  worker.postMessage({
                    type: 'update',
                    fullscreen: fullscreen
                  });
                  update_defer = RSVP.defer();
                  return RSVP.all([
                    promiseAnimationFrame(),
                    update_defer.promise
                  ]);
                })
                .push(step);
            }

            function cloneEvent(event) {
              event.preventDefault();
              var eventClone = {};
              for (let field of mouseEventFields) {
                eventClone[field] = event[field];
              }
              return eventClone;
            }

            function bindEvent(data) {
              var target;
              switch (data.targetName) {
              case 'window':
                target = window;
                break;
              case 'canvas':
                target = options.canvas_original;
                break;
              case 'document':
                target = document;
                break;
              }
              if (!target) {
                console.error('Unknown target: ' + data.targetName);
                return;
              }
              target.addEventListener(data.eventName, function (e) {
                // We can`t pass original event to the worker
                var eventClone = cloneEvent(e);
                if (eventClone.type === "pointerout") {
                  return;
                }
                worker.postMessage({
                  type: 'event',
                  targetName: data.targetName,
                  eventName: data.eventName,
                  eventClone: eventClone
                });
              }, data.opt);
            }

            function workerToMain(evt) {
              switch (evt.data.type) {
              case 'loaded':
                return worker.postMessage({
                  type: 'start',
                  logic_url_list: options.logic_url_list,
                  canvas: options.canvas,
                  width: options.width,
                  height: options.height,
                  game_parameters: options.game_parameters
                }, [options.canvas]);
              case 'started':
                console.log('GAME: started');
                if (context._gadget) {
                  var loading =
                      context._gadget.element.querySelector('#loading');
                  if (loading) { loading.innerHTML = ""; }
                  context._gadget.element.querySelector('#maximize')
                    .style.visibility = 'visible';
                }
                context.unpause();
                return step();
              case 'updated':
                return update_defer.resolve('updated');
              case 'finished':
                console.log('GAME: finished');
                game_result = evt.data.result;
                return context.quit();
              case 'event':
                bindEvent(evt.data);
                break;
              case 'canvasMethod':
                options.canvas_original[evt.data.method](...evt.data.args);
                break;
              case 'canvasStyle':
                options.canvas_original.style[evt.data.name] = evt.data.value;
                break;
              case 'error':
                message_error_handler_defer.reject(evt.data.error);
                break;
              default:
                message_error_handler_defer.reject(
                  new Error('Unsupported message ' + JSON.stringify(evt.data))
                );
              }
            }

            worker.onmessage = workerToMain;
            // Always quit the game when the worker callback usage is over
            // to prevent trying to call pause
            return message_error_handler_defer.promise;
          })
      ]))
        .push(undefined, function (error) {
          // As the loop_promise will be cancelled at some point when calling
          // quit, we will get a CancellationError as result.
          // This is expected, and play must be successfully resolved
          if (!(error instanceof RSVP.CancellationError)) {
            throw error;
          }
        });
    }
  };

  rJS(window)

    .declareAcquiredMethod('triggerMaximize', 'triggerMaximize')
    .allowPublicAcquisition('triggerMaximize', function (param_list) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return game_manager.fullscreen();
        })
        .push(function () {
          container.classList.toggle("fullscreen");
          background.style.visibility = 'visible';
          return gadget.triggerMaximize.apply(gadget, param_list);
        })
        .push(undefined, function (error) {
          if (!(error instanceof RSVP.CancellationError)) {
            throw error;
          }
          return game_manager.fullscreen()
            .push(function () {
              container.classList.toggle("fullscreen");
              background.style.visibility = 'hidden';
              container.scrollIntoView();
            });
        });
    })
    .declareMethod('render', function render(options) {
      var gadget = this,
        loading = domsugar('span', ["Loading..."]),
        maximize = domsugar('div');
      background = domsugar('div');
      container = domsugar('div');
      maximize.id = 'maximize';
      maximize.style.visibility = 'hidden';
      canvas = domsugar('canvas');
      loading.id = "loading";
      container.className = 'container';
      background.id = "background";
      background.className = 'fullscreen-background';
      background.style.visibility = 'hidden';
      container.appendChild(canvas);
      domsugar(gadget.element, [loading, maximize, background, container]);
      canvas.width = WIDTH;
      canvas.height = HEIGHT;
      // https://doc.babylonjs.com/divingDeeper/scene/offscreenCanvas
      offscreen = canvas.transferControlToOffscreen();
      fullscreen_delay = 6.5 * options.game_parameters.simulation_speed + 40;
      fullscreen_delay = 60; //TODO find a good calculation for this
      options.game_parameters.fullscreen = {};
      options.game_parameters.fullscreen.width = window.innerWidth;
      if (window.innerHeight < window.innerWidth) {
        options.game_parameters.fullscreen.height = window.innerHeight;
      } else {
        options.game_parameters.fullscreen.height = window.innerWidth * 0.6;
      }
      return gadget.changeState({
        logic_file_list: options.logic_file_list,
        game_parameters: options.game_parameters
      });
    })
    .onStateChange(function () {
      var gadget = this, div_max = gadget.element.querySelector('#maximize');
      return gadget.declareGadget("gadget_button_maximize.html", {
        scope: 'maximize',
        element: div_max,
        sandbox: 'public'
      });
    })
    .declareMethod('getContent', function getContent() {
      container.scrollIntoView();
      var gadget = this;
      return gadget.runGame({
        logic_file_list: gadget.state.logic_file_list,
        game_parameters: gadget.state.game_parameters
      });
    })
    .declareMethod('runGame', function runGame(options) {
      options.canvas = offscreen;
      options.canvas_original = canvas;
      options.width = canvas.width;
      options.height = canvas.height;
      options.logic_url_list = options.logic_file_list;
      var gadget = this;
      game_manager = new DroneGameManager(gadget);
      return game_manager.play(options)
      .push(function () {
        gadget.element.querySelector('#maximize').style.visibility = 'hidden';
        return game_manager.result();
      });
    });
}(window, rJS, domsugar, RSVP, Set, Worker,
  requestAnimationFrame, cancelAnimationFrame));