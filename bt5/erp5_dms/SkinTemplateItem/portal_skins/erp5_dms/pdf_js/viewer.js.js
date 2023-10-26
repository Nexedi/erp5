/**
 * @licstart The following is the entire license notice for the
 * JavaScript code in this page
 *
 * Copyright 2023 Mozilla Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @licend The above is the entire license notice for the
 * JavaScript code in this page
 */

/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ([
/* 0 */,
/* 1 */
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {



  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.GenericCom = void 0;
  __webpack_require__(2);
  __webpack_require__(116);
  var _app = __webpack_require__(121);
  var _preferences = __webpack_require__(225);
  var _download_manager = __webpack_require__(226);
  var _genericl10n = __webpack_require__(227);
  var _generic_scripting = __webpack_require__(229);
  ;
  const GenericCom = {};
  exports.GenericCom = GenericCom;
  class GenericPreferences extends _preferences.BasePreferences {
    async _writeToStorage(prefObj) {
      localStorage.setItem("pdfjs.preferences", JSON.stringify(prefObj));
    }
    async _readFromStorage(prefObj) {
      return JSON.parse(localStorage.getItem("pdfjs.preferences"));
    }
  }
  class GenericExternalServices extends _app.DefaultExternalServices {
    static createDownloadManager() {
      return new _download_manager.DownloadManager();
    }
    static createPreferences() {
      return new GenericPreferences();
    }
    static createL10n(_ref) {
      let {
        locale = "en-US"
      } = _ref;
      return new _genericl10n.GenericL10n(locale);
    }
    static createScripting(_ref2) {
      let {
        sandboxBundleSrc
      } = _ref2;
      return new _generic_scripting.GenericScripting(sandboxBundleSrc);
    }
  }
  _app.PDFViewerApplication.externalServices = GenericExternalServices;
  
  /***/ }),
  /* 2 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  __webpack_require__(3);
  __webpack_require__(102);
  __webpack_require__(111);
  __webpack_require__(112);
  __webpack_require__(113);
  __webpack_require__(114);
  
  /***/ }),
  /* 3 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var IS_PURE = __webpack_require__(37);
  var IS_NODE = __webpack_require__(70);
  var global = __webpack_require__(5);
  var call = __webpack_require__(9);
  var defineBuiltIn = __webpack_require__(49);
  var setPrototypeOf = __webpack_require__(71);
  var setToStringTag = __webpack_require__(74);
  var setSpecies = __webpack_require__(75);
  var aCallable = __webpack_require__(32);
  var isCallable = __webpack_require__(22);
  var isObject = __webpack_require__(21);
  var anInstance = __webpack_require__(77);
  var speciesConstructor = __webpack_require__(78);
  var task = (__webpack_require__(83).set);
  var microtask = __webpack_require__(91);
  var hostReportErrors = __webpack_require__(95);
  var perform = __webpack_require__(96);
  var Queue = __webpack_require__(92);
  var InternalStateModule = __webpack_require__(53);
  var NativePromiseConstructor = __webpack_require__(97);
  var PromiseConstructorDetection = __webpack_require__(98);
  var newPromiseCapabilityModule = __webpack_require__(101);
  var PROMISE = 'Promise';
  var FORCED_PROMISE_CONSTRUCTOR = PromiseConstructorDetection.CONSTRUCTOR;
  var NATIVE_PROMISE_REJECTION_EVENT = PromiseConstructorDetection.REJECTION_EVENT;
  var NATIVE_PROMISE_SUBCLASSING = PromiseConstructorDetection.SUBCLASSING;
  var getInternalPromiseState = InternalStateModule.getterFor(PROMISE);
  var setInternalState = InternalStateModule.set;
  var NativePromisePrototype = NativePromiseConstructor && NativePromiseConstructor.prototype;
  var PromiseConstructor = NativePromiseConstructor;
  var PromisePrototype = NativePromisePrototype;
  var TypeError = global.TypeError;
  var document = global.document;
  var process = global.process;
  var newPromiseCapability = newPromiseCapabilityModule.f;
  var newGenericPromiseCapability = newPromiseCapability;
  var DISPATCH_EVENT = !!(document && document.createEvent && global.dispatchEvent);
  var UNHANDLED_REJECTION = 'unhandledrejection';
  var REJECTION_HANDLED = 'rejectionhandled';
  var PENDING = 0;
  var FULFILLED = 1;
  var REJECTED = 2;
  var HANDLED = 1;
  var UNHANDLED = 2;
  var Internal, OwnPromiseCapability, PromiseWrapper, nativeThen;
  var isThenable = function (it) {
   var then;
   return isObject(it) && isCallable(then = it.then) ? then : false;
  };
  var callReaction = function (reaction, state) {
   var value = state.value;
   var ok = state.state === FULFILLED;
   var handler = ok ? reaction.ok : reaction.fail;
   var resolve = reaction.resolve;
   var reject = reaction.reject;
   var domain = reaction.domain;
   var result, then, exited;
   try {
    if (handler) {
     if (!ok) {
      if (state.rejection === UNHANDLED)
       onHandleUnhandled(state);
      state.rejection = HANDLED;
     }
     if (handler === true)
      result = value;
     else {
      if (domain)
       domain.enter();
      result = handler(value);
      if (domain) {
       domain.exit();
       exited = true;
      }
     }
     if (result === reaction.promise) {
      reject(TypeError('Promise-chain cycle'));
     } else if (then = isThenable(result)) {
      call(then, result, resolve, reject);
     } else
      resolve(result);
    } else
     reject(value);
   } catch (error) {
    if (domain && !exited)
     domain.exit();
    reject(error);
   }
  };
  var notify = function (state, isReject) {
   if (state.notified)
    return;
   state.notified = true;
   microtask(function () {
    var reactions = state.reactions;
    var reaction;
    while (reaction = reactions.get()) {
     callReaction(reaction, state);
    }
    state.notified = false;
    if (isReject && !state.rejection)
     onUnhandled(state);
   });
  };
  var dispatchEvent = function (name, promise, reason) {
   var event, handler;
   if (DISPATCH_EVENT) {
    event = document.createEvent('Event');
    event.promise = promise;
    event.reason = reason;
    event.initEvent(name, false, true);
    global.dispatchEvent(event);
   } else
    event = {
     promise: promise,
     reason: reason
    };
   if (!NATIVE_PROMISE_REJECTION_EVENT && (handler = global['on' + name]))
    handler(event);
   else if (name === UNHANDLED_REJECTION)
    hostReportErrors('Unhandled promise rejection', reason);
  };
  var onUnhandled = function (state) {
   call(task, global, function () {
    var promise = state.facade;
    var value = state.value;
    var IS_UNHANDLED = isUnhandled(state);
    var result;
    if (IS_UNHANDLED) {
     result = perform(function () {
      if (IS_NODE) {
       process.emit('unhandledRejection', value, promise);
      } else
       dispatchEvent(UNHANDLED_REJECTION, promise, value);
     });
     state.rejection = IS_NODE || isUnhandled(state) ? UNHANDLED : HANDLED;
     if (result.error)
      throw result.value;
    }
   });
  };
  var isUnhandled = function (state) {
   return state.rejection !== HANDLED && !state.parent;
  };
  var onHandleUnhandled = function (state) {
   call(task, global, function () {
    var promise = state.facade;
    if (IS_NODE) {
     process.emit('rejectionHandled', promise);
    } else
     dispatchEvent(REJECTION_HANDLED, promise, state.value);
   });
  };
  var bind = function (fn, state, unwrap) {
   return function (value) {
    fn(state, value, unwrap);
   };
  };
  var internalReject = function (state, value, unwrap) {
   if (state.done)
    return;
   state.done = true;
   if (unwrap)
    state = unwrap;
   state.value = value;
   state.state = REJECTED;
   notify(state, true);
  };
  var internalResolve = function (state, value, unwrap) {
   if (state.done)
    return;
   state.done = true;
   if (unwrap)
    state = unwrap;
   try {
    if (state.facade === value)
     throw TypeError("Promise can't be resolved itself");
    var then = isThenable(value);
    if (then) {
     microtask(function () {
      var wrapper = { done: false };
      try {
       call(then, value, bind(internalResolve, wrapper, state), bind(internalReject, wrapper, state));
      } catch (error) {
       internalReject(wrapper, error, state);
      }
     });
    } else {
     state.value = value;
     state.state = FULFILLED;
     notify(state, false);
    }
   } catch (error) {
    internalReject({ done: false }, error, state);
   }
  };
  if (FORCED_PROMISE_CONSTRUCTOR) {
   PromiseConstructor = function Promise(executor) {
    anInstance(this, PromisePrototype);
    aCallable(executor);
    call(Internal, this);
    var state = getInternalPromiseState(this);
    try {
     executor(bind(internalResolve, state), bind(internalReject, state));
    } catch (error) {
     internalReject(state, error);
    }
   };
   PromisePrototype = PromiseConstructor.prototype;
   Internal = function Promise(executor) {
    setInternalState(this, {
     type: PROMISE,
     done: false,
     notified: false,
     parent: false,
     reactions: new Queue(),
     rejection: false,
     state: PENDING,
     value: undefined
    });
   };
   Internal.prototype = defineBuiltIn(PromisePrototype, 'then', function then(onFulfilled, onRejected) {
    var state = getInternalPromiseState(this);
    var reaction = newPromiseCapability(speciesConstructor(this, PromiseConstructor));
    state.parent = true;
    reaction.ok = isCallable(onFulfilled) ? onFulfilled : true;
    reaction.fail = isCallable(onRejected) && onRejected;
    reaction.domain = IS_NODE ? process.domain : undefined;
    if (state.state === PENDING)
     state.reactions.add(reaction);
    else
     microtask(function () {
      callReaction(reaction, state);
     });
    return reaction.promise;
   });
   OwnPromiseCapability = function () {
    var promise = new Internal();
    var state = getInternalPromiseState(promise);
    this.promise = promise;
    this.resolve = bind(internalResolve, state);
    this.reject = bind(internalReject, state);
   };
   newPromiseCapabilityModule.f = newPromiseCapability = function (C) {
    return C === PromiseConstructor || C === PromiseWrapper ? new OwnPromiseCapability(C) : newGenericPromiseCapability(C);
   };
   if (!IS_PURE && isCallable(NativePromiseConstructor) && NativePromisePrototype !== Object.prototype) {
    nativeThen = NativePromisePrototype.then;
    if (!NATIVE_PROMISE_SUBCLASSING) {
     defineBuiltIn(NativePromisePrototype, 'then', function then(onFulfilled, onRejected) {
      var that = this;
      return new PromiseConstructor(function (resolve, reject) {
       call(nativeThen, that, resolve, reject);
      }).then(onFulfilled, onRejected);
     }, { unsafe: true });
    }
    try {
     delete NativePromisePrototype.constructor;
    } catch (error) {
    }
    if (setPrototypeOf) {
     setPrototypeOf(NativePromisePrototype, PromisePrototype);
    }
   }
  }
  $({
   global: true,
   constructor: true,
   wrap: true,
   forced: FORCED_PROMISE_CONSTRUCTOR
  }, { Promise: PromiseConstructor });
  setToStringTag(PromiseConstructor, PROMISE, false, true);
  setSpecies(PROMISE);
  
  /***/ }),
  /* 4 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var getOwnPropertyDescriptor = (__webpack_require__(6).f);
  var createNonEnumerableProperty = __webpack_require__(45);
  var defineBuiltIn = __webpack_require__(49);
  var defineGlobalProperty = __webpack_require__(39);
  var copyConstructorProperties = __webpack_require__(57);
  var isForced = __webpack_require__(69);
  module.exports = function (options, source) {
   var TARGET = options.target;
   var GLOBAL = options.global;
   var STATIC = options.stat;
   var FORCED, target, key, targetProperty, sourceProperty, descriptor;
   if (GLOBAL) {
    target = global;
   } else if (STATIC) {
    target = global[TARGET] || defineGlobalProperty(TARGET, {});
   } else {
    target = (global[TARGET] || {}).prototype;
   }
   if (target)
    for (key in source) {
     sourceProperty = source[key];
     if (options.dontCallGetSet) {
      descriptor = getOwnPropertyDescriptor(target, key);
      targetProperty = descriptor && descriptor.value;
     } else
      targetProperty = target[key];
     FORCED = isForced(GLOBAL ? key : TARGET + (STATIC ? '.' : '#') + key, options.forced);
     if (!FORCED && targetProperty !== undefined) {
      if (typeof sourceProperty == typeof targetProperty)
       continue;
      copyConstructorProperties(sourceProperty, targetProperty);
     }
     if (options.sham || targetProperty && targetProperty.sham) {
      createNonEnumerableProperty(sourceProperty, 'sham', true);
     }
     defineBuiltIn(target, key, sourceProperty, options);
    }
  };
  
  /***/ }),
  /* 5 */
  /***/ (function(module) {
  
  
  var check = function (it) {
   return it && it.Math === Math && it;
  };
  module.exports = check(typeof globalThis == 'object' && globalThis) || check(typeof window == 'object' && window) || check(typeof self == 'object' && self) || check(typeof global == 'object' && global) || (function () {
   return this;
  }()) || this || Function('return this')();
  
  /***/ }),
  /* 6 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var call = __webpack_require__(9);
  var propertyIsEnumerableModule = __webpack_require__(11);
  var createPropertyDescriptor = __webpack_require__(12);
  var toIndexedObject = __webpack_require__(13);
  var toPropertyKey = __webpack_require__(19);
  var hasOwn = __webpack_require__(40);
  var IE8_DOM_DEFINE = __webpack_require__(43);
  var $getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  exports.f = DESCRIPTORS ? $getOwnPropertyDescriptor : function getOwnPropertyDescriptor(O, P) {
   O = toIndexedObject(O);
   P = toPropertyKey(P);
   if (IE8_DOM_DEFINE)
    try {
     return $getOwnPropertyDescriptor(O, P);
    } catch (error) {
    }
   if (hasOwn(O, P))
    return createPropertyDescriptor(!call(propertyIsEnumerableModule.f, O, P), O[P]);
  };
  
  /***/ }),
  /* 7 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  module.exports = !fails(function () {
   return Object.defineProperty({}, 1, {
    get: function () {
     return 7;
    }
   })[1] !== 7;
  });
  
  /***/ }),
  /* 8 */
  /***/ ((module) => {
  
  
  module.exports = function (exec) {
   try {
    return !!exec();
   } catch (error) {
    return true;
   }
  };
  
  /***/ }),
  /* 9 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NATIVE_BIND = __webpack_require__(10);
  var call = Function.prototype.call;
  module.exports = NATIVE_BIND ? call.bind(call) : function () {
   return call.apply(call, arguments);
  };
  
  /***/ }),
  /* 10 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  module.exports = !fails(function () {
   var test = function () {
   }.bind();
   return typeof test != 'function' || test.hasOwnProperty('prototype');
  });
  
  /***/ }),
  /* 11 */
  /***/ ((__unused_webpack_module, exports) => {
  
  
  var $propertyIsEnumerable = {}.propertyIsEnumerable;
  var getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  var NASHORN_BUG = getOwnPropertyDescriptor && !$propertyIsEnumerable.call({ 1: 2 }, 1);
  exports.f = NASHORN_BUG ? function propertyIsEnumerable(V) {
   var descriptor = getOwnPropertyDescriptor(this, V);
   return !!descriptor && descriptor.enumerable;
  } : $propertyIsEnumerable;
  
  /***/ }),
  /* 12 */
  /***/ ((module) => {
  
  
  module.exports = function (bitmap, value) {
   return {
    enumerable: !(bitmap & 1),
    configurable: !(bitmap & 2),
    writable: !(bitmap & 4),
    value: value
   };
  };
  
  /***/ }),
  /* 13 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var IndexedObject = __webpack_require__(14);
  var requireObjectCoercible = __webpack_require__(17);
  module.exports = function (it) {
   return IndexedObject(requireObjectCoercible(it));
  };
  
  /***/ }),
  /* 14 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var fails = __webpack_require__(8);
  var classof = __webpack_require__(16);
  var $Object = Object;
  var split = uncurryThis(''.split);
  module.exports = fails(function () {
   return !$Object('z').propertyIsEnumerable(0);
  }) ? function (it) {
   return classof(it) === 'String' ? split(it, '') : $Object(it);
  } : $Object;
  
  /***/ }),
  /* 15 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NATIVE_BIND = __webpack_require__(10);
  var FunctionPrototype = Function.prototype;
  var call = FunctionPrototype.call;
  var uncurryThisWithBind = NATIVE_BIND && FunctionPrototype.bind.bind(call, call);
  module.exports = NATIVE_BIND ? uncurryThisWithBind : function (fn) {
   return function () {
    return call.apply(fn, arguments);
   };
  };
  
  /***/ }),
  /* 16 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var toString = uncurryThis({}.toString);
  var stringSlice = uncurryThis(''.slice);
  module.exports = function (it) {
   return stringSlice(toString(it), 8, -1);
  };
  
  /***/ }),
  /* 17 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isNullOrUndefined = __webpack_require__(18);
  var $TypeError = TypeError;
  module.exports = function (it) {
   if (isNullOrUndefined(it))
    throw $TypeError("Can't call method on " + it);
   return it;
  };
  
  /***/ }),
  /* 18 */
  /***/ ((module) => {
  
  
  module.exports = function (it) {
   return it === null || it === undefined;
  };
  
  /***/ }),
  /* 19 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toPrimitive = __webpack_require__(20);
  var isSymbol = __webpack_require__(24);
  module.exports = function (argument) {
   var key = toPrimitive(argument, 'string');
   return isSymbol(key) ? key : key + '';
  };
  
  /***/ }),
  /* 20 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var isObject = __webpack_require__(21);
  var isSymbol = __webpack_require__(24);
  var getMethod = __webpack_require__(31);
  var ordinaryToPrimitive = __webpack_require__(34);
  var wellKnownSymbol = __webpack_require__(35);
  var $TypeError = TypeError;
  var TO_PRIMITIVE = wellKnownSymbol('toPrimitive');
  module.exports = function (input, pref) {
   if (!isObject(input) || isSymbol(input))
    return input;
   var exoticToPrim = getMethod(input, TO_PRIMITIVE);
   var result;
   if (exoticToPrim) {
    if (pref === undefined)
     pref = 'default';
    result = call(exoticToPrim, input, pref);
    if (!isObject(result) || isSymbol(result))
     return result;
    throw $TypeError("Can't convert object to primitive value");
   }
   if (pref === undefined)
    pref = 'number';
   return ordinaryToPrimitive(input, pref);
  };
  
  /***/ }),
  /* 21 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isCallable = __webpack_require__(22);
  var $documentAll = __webpack_require__(23);
  var documentAll = $documentAll.all;
  module.exports = $documentAll.IS_HTMLDDA ? function (it) {
   return typeof it == 'object' ? it !== null : isCallable(it) || it === documentAll;
  } : function (it) {
   return typeof it == 'object' ? it !== null : isCallable(it);
  };
  
  /***/ }),
  /* 22 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $documentAll = __webpack_require__(23);
  var documentAll = $documentAll.all;
  module.exports = $documentAll.IS_HTMLDDA ? function (argument) {
   return typeof argument == 'function' || argument === documentAll;
  } : function (argument) {
   return typeof argument == 'function';
  };
  
  /***/ }),
  /* 23 */
  /***/ ((module) => {
  
  
  var documentAll = typeof document == 'object' && document.all;
  var IS_HTMLDDA = typeof documentAll == 'undefined' && documentAll !== undefined;
  module.exports = {
   all: documentAll,
   IS_HTMLDDA: IS_HTMLDDA
  };
  
  /***/ }),
  /* 24 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  var isCallable = __webpack_require__(22);
  var isPrototypeOf = __webpack_require__(26);
  var USE_SYMBOL_AS_UID = __webpack_require__(27);
  var $Object = Object;
  module.exports = USE_SYMBOL_AS_UID ? function (it) {
   return typeof it == 'symbol';
  } : function (it) {
   var $Symbol = getBuiltIn('Symbol');
   return isCallable($Symbol) && isPrototypeOf($Symbol.prototype, $Object(it));
  };
  
  /***/ }),
  /* 25 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var isCallable = __webpack_require__(22);
  var aFunction = function (argument) {
   return isCallable(argument) ? argument : undefined;
  };
  module.exports = function (namespace, method) {
   return arguments.length < 2 ? aFunction(global[namespace]) : global[namespace] && global[namespace][method];
  };
  
  /***/ }),
  /* 26 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  module.exports = uncurryThis({}.isPrototypeOf);
  
  /***/ }),
  /* 27 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NATIVE_SYMBOL = __webpack_require__(28);
  module.exports = NATIVE_SYMBOL && !Symbol.sham && typeof Symbol.iterator == 'symbol';
  
  /***/ }),
  /* 28 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var V8_VERSION = __webpack_require__(29);
  var fails = __webpack_require__(8);
  var global = __webpack_require__(5);
  var $String = global.String;
  module.exports = !!Object.getOwnPropertySymbols && !fails(function () {
   var symbol = Symbol('symbol detection');
   return !$String(symbol) || !(Object(symbol) instanceof Symbol) || !Symbol.sham && V8_VERSION && V8_VERSION < 41;
  });
  
  /***/ }),
  /* 29 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var userAgent = __webpack_require__(30);
  var process = global.process;
  var Deno = global.Deno;
  var versions = process && process.versions || Deno && Deno.version;
  var v8 = versions && versions.v8;
  var match, version;
  if (v8) {
   match = v8.split('.');
   version = match[0] > 0 && match[0] < 4 ? 1 : +(match[0] + match[1]);
  }
  if (!version && userAgent) {
   match = userAgent.match(/Edge\/(\d+)/);
   if (!match || match[1] >= 74) {
    match = userAgent.match(/Chrome\/(\d+)/);
    if (match)
     version = +match[1];
   }
  }
  module.exports = version;
  
  /***/ }),
  /* 30 */
  /***/ ((module) => {
  
  
  module.exports = typeof navigator != 'undefined' && String(navigator.userAgent) || '';
  
  /***/ }),
  /* 31 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aCallable = __webpack_require__(32);
  var isNullOrUndefined = __webpack_require__(18);
  module.exports = function (V, P) {
   var func = V[P];
   return isNullOrUndefined(func) ? undefined : aCallable(func);
  };
  
  /***/ }),
  /* 32 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isCallable = __webpack_require__(22);
  var tryToString = __webpack_require__(33);
  var $TypeError = TypeError;
  module.exports = function (argument) {
   if (isCallable(argument))
    return argument;
   throw $TypeError(tryToString(argument) + ' is not a function');
  };
  
  /***/ }),
  /* 33 */
  /***/ ((module) => {
  
  
  var $String = String;
  module.exports = function (argument) {
   try {
    return $String(argument);
   } catch (error) {
    return 'Object';
   }
  };
  
  /***/ }),
  /* 34 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var isCallable = __webpack_require__(22);
  var isObject = __webpack_require__(21);
  var $TypeError = TypeError;
  module.exports = function (input, pref) {
   var fn, val;
   if (pref === 'string' && isCallable(fn = input.toString) && !isObject(val = call(fn, input)))
    return val;
   if (isCallable(fn = input.valueOf) && !isObject(val = call(fn, input)))
    return val;
   if (pref !== 'string' && isCallable(fn = input.toString) && !isObject(val = call(fn, input)))
    return val;
   throw $TypeError("Can't convert object to primitive value");
  };
  
  /***/ }),
  /* 35 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var shared = __webpack_require__(36);
  var hasOwn = __webpack_require__(40);
  var uid = __webpack_require__(42);
  var NATIVE_SYMBOL = __webpack_require__(28);
  var USE_SYMBOL_AS_UID = __webpack_require__(27);
  var Symbol = global.Symbol;
  var WellKnownSymbolsStore = shared('wks');
  var createWellKnownSymbol = USE_SYMBOL_AS_UID ? Symbol['for'] || Symbol : Symbol && Symbol.withoutSetter || uid;
  module.exports = function (name) {
   if (!hasOwn(WellKnownSymbolsStore, name)) {
    WellKnownSymbolsStore[name] = NATIVE_SYMBOL && hasOwn(Symbol, name) ? Symbol[name] : createWellKnownSymbol('Symbol.' + name);
   }
   return WellKnownSymbolsStore[name];
  };
  
  /***/ }),
  /* 36 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var IS_PURE = __webpack_require__(37);
  var store = __webpack_require__(38);
  (module.exports = function (key, value) {
   return store[key] || (store[key] = value !== undefined ? value : {});
  })('versions', []).push({
   version: '3.32.2',
   mode: IS_PURE ? 'pure' : 'global',
   copyright: '© 2014-2023 Denis Pushkarev (zloirock.ru)',
   license: 'https://github.com/zloirock/core-js/blob/v3.32.2/LICENSE',
   source: 'https://github.com/zloirock/core-js'
  });
  
  /***/ }),
  /* 37 */
  /***/ ((module) => {
  
  
  module.exports = false;
  
  /***/ }),
  /* 38 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var defineGlobalProperty = __webpack_require__(39);
  var SHARED = '__core-js_shared__';
  var store = global[SHARED] || defineGlobalProperty(SHARED, {});
  module.exports = store;
  
  /***/ }),
  /* 39 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var defineProperty = Object.defineProperty;
  module.exports = function (key, value) {
   try {
    defineProperty(global, key, {
     value: value,
     configurable: true,
     writable: true
    });
   } catch (error) {
    global[key] = value;
   }
   return value;
  };
  
  /***/ }),
  /* 40 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var toObject = __webpack_require__(41);
  var hasOwnProperty = uncurryThis({}.hasOwnProperty);
  module.exports = Object.hasOwn || function hasOwn(it, key) {
   return hasOwnProperty(toObject(it), key);
  };
  
  /***/ }),
  /* 41 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var requireObjectCoercible = __webpack_require__(17);
  var $Object = Object;
  module.exports = function (argument) {
   return $Object(requireObjectCoercible(argument));
  };
  
  /***/ }),
  /* 42 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var id = 0;
  var postfix = Math.random();
  var toString = uncurryThis(1.0.toString);
  module.exports = function (key) {
   return 'Symbol(' + (key === undefined ? '' : key) + ')_' + toString(++id + postfix, 36);
  };
  
  /***/ }),
  /* 43 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var fails = __webpack_require__(8);
  var createElement = __webpack_require__(44);
  module.exports = !DESCRIPTORS && !fails(function () {
   return Object.defineProperty(createElement('div'), 'a', {
    get: function () {
     return 7;
    }
   }).a !== 7;
  });
  
  /***/ }),
  /* 44 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var isObject = __webpack_require__(21);
  var document = global.document;
  var EXISTS = isObject(document) && isObject(document.createElement);
  module.exports = function (it) {
   return EXISTS ? document.createElement(it) : {};
  };
  
  /***/ }),
  /* 45 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var definePropertyModule = __webpack_require__(46);
  var createPropertyDescriptor = __webpack_require__(12);
  module.exports = DESCRIPTORS ? function (object, key, value) {
   return definePropertyModule.f(object, key, createPropertyDescriptor(1, value));
  } : function (object, key, value) {
   object[key] = value;
   return object;
  };
  
  /***/ }),
  /* 46 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var IE8_DOM_DEFINE = __webpack_require__(43);
  var V8_PROTOTYPE_DEFINE_BUG = __webpack_require__(47);
  var anObject = __webpack_require__(48);
  var toPropertyKey = __webpack_require__(19);
  var $TypeError = TypeError;
  var $defineProperty = Object.defineProperty;
  var $getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  var ENUMERABLE = 'enumerable';
  var CONFIGURABLE = 'configurable';
  var WRITABLE = 'writable';
  exports.f = DESCRIPTORS ? V8_PROTOTYPE_DEFINE_BUG ? function defineProperty(O, P, Attributes) {
   anObject(O);
   P = toPropertyKey(P);
   anObject(Attributes);
   if (typeof O === 'function' && P === 'prototype' && 'value' in Attributes && WRITABLE in Attributes && !Attributes[WRITABLE]) {
    var current = $getOwnPropertyDescriptor(O, P);
    if (current && current[WRITABLE]) {
     O[P] = Attributes.value;
     Attributes = {
      configurable: CONFIGURABLE in Attributes ? Attributes[CONFIGURABLE] : current[CONFIGURABLE],
      enumerable: ENUMERABLE in Attributes ? Attributes[ENUMERABLE] : current[ENUMERABLE],
      writable: false
     };
    }
   }
   return $defineProperty(O, P, Attributes);
  } : $defineProperty : function defineProperty(O, P, Attributes) {
   anObject(O);
   P = toPropertyKey(P);
   anObject(Attributes);
   if (IE8_DOM_DEFINE)
    try {
     return $defineProperty(O, P, Attributes);
    } catch (error) {
    }
   if ('get' in Attributes || 'set' in Attributes)
    throw $TypeError('Accessors not supported');
   if ('value' in Attributes)
    O[P] = Attributes.value;
   return O;
  };
  
  /***/ }),
  /* 47 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var fails = __webpack_require__(8);
  module.exports = DESCRIPTORS && fails(function () {
   return Object.defineProperty(function () {
   }, 'prototype', {
    value: 42,
    writable: false
   }).prototype !== 42;
  });
  
  /***/ }),
  /* 48 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isObject = __webpack_require__(21);
  var $String = String;
  var $TypeError = TypeError;
  module.exports = function (argument) {
   if (isObject(argument))
    return argument;
   throw $TypeError($String(argument) + ' is not an object');
  };
  
  /***/ }),
  /* 49 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isCallable = __webpack_require__(22);
  var definePropertyModule = __webpack_require__(46);
  var makeBuiltIn = __webpack_require__(50);
  var defineGlobalProperty = __webpack_require__(39);
  module.exports = function (O, key, value, options) {
   if (!options)
    options = {};
   var simple = options.enumerable;
   var name = options.name !== undefined ? options.name : key;
   if (isCallable(value))
    makeBuiltIn(value, name, options);
   if (options.global) {
    if (simple)
     O[key] = value;
    else
     defineGlobalProperty(key, value);
   } else {
    try {
     if (!options.unsafe)
      delete O[key];
     else if (O[key])
      simple = true;
    } catch (error) {
    }
    if (simple)
     O[key] = value;
    else
     definePropertyModule.f(O, key, {
      value: value,
      enumerable: false,
      configurable: !options.nonConfigurable,
      writable: !options.nonWritable
     });
   }
   return O;
  };
  
  /***/ }),
  /* 50 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var fails = __webpack_require__(8);
  var isCallable = __webpack_require__(22);
  var hasOwn = __webpack_require__(40);
  var DESCRIPTORS = __webpack_require__(7);
  var CONFIGURABLE_FUNCTION_NAME = (__webpack_require__(51).CONFIGURABLE);
  var inspectSource = __webpack_require__(52);
  var InternalStateModule = __webpack_require__(53);
  var enforceInternalState = InternalStateModule.enforce;
  var getInternalState = InternalStateModule.get;
  var $String = String;
  var defineProperty = Object.defineProperty;
  var stringSlice = uncurryThis(''.slice);
  var replace = uncurryThis(''.replace);
  var join = uncurryThis([].join);
  var CONFIGURABLE_LENGTH = DESCRIPTORS && !fails(function () {
   return defineProperty(function () {
   }, 'length', { value: 8 }).length !== 8;
  });
  var TEMPLATE = String(String).split('String');
  var makeBuiltIn = module.exports = function (value, name, options) {
   if (stringSlice($String(name), 0, 7) === 'Symbol(') {
    name = '[' + replace($String(name), /^Symbol\(([^)]*)\)/, '$1') + ']';
   }
   if (options && options.getter)
    name = 'get ' + name;
   if (options && options.setter)
    name = 'set ' + name;
   if (!hasOwn(value, 'name') || CONFIGURABLE_FUNCTION_NAME && value.name !== name) {
    if (DESCRIPTORS)
     defineProperty(value, 'name', {
      value: name,
      configurable: true
     });
    else
     value.name = name;
   }
   if (CONFIGURABLE_LENGTH && options && hasOwn(options, 'arity') && value.length !== options.arity) {
    defineProperty(value, 'length', { value: options.arity });
   }
   try {
    if (options && hasOwn(options, 'constructor') && options.constructor) {
     if (DESCRIPTORS)
      defineProperty(value, 'prototype', { writable: false });
    } else if (value.prototype)
     value.prototype = undefined;
   } catch (error) {
   }
   var state = enforceInternalState(value);
   if (!hasOwn(state, 'source')) {
    state.source = join(TEMPLATE, typeof name == 'string' ? name : '');
   }
   return value;
  };
  Function.prototype.toString = makeBuiltIn(function toString() {
   return isCallable(this) && getInternalState(this).source || inspectSource(this);
  }, 'toString');
  
  /***/ }),
  /* 51 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var hasOwn = __webpack_require__(40);
  var FunctionPrototype = Function.prototype;
  var getDescriptor = DESCRIPTORS && Object.getOwnPropertyDescriptor;
  var EXISTS = hasOwn(FunctionPrototype, 'name');
  var PROPER = EXISTS && function something() {
  }.name === 'something';
  var CONFIGURABLE = EXISTS && (!DESCRIPTORS || DESCRIPTORS && getDescriptor(FunctionPrototype, 'name').configurable);
  module.exports = {
   EXISTS: EXISTS,
   PROPER: PROPER,
   CONFIGURABLE: CONFIGURABLE
  };
  
  /***/ }),
  /* 52 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var isCallable = __webpack_require__(22);
  var store = __webpack_require__(38);
  var functionToString = uncurryThis(Function.toString);
  if (!isCallable(store.inspectSource)) {
   store.inspectSource = function (it) {
    return functionToString(it);
   };
  }
  module.exports = store.inspectSource;
  
  /***/ }),
  /* 53 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NATIVE_WEAK_MAP = __webpack_require__(54);
  var global = __webpack_require__(5);
  var isObject = __webpack_require__(21);
  var createNonEnumerableProperty = __webpack_require__(45);
  var hasOwn = __webpack_require__(40);
  var shared = __webpack_require__(38);
  var sharedKey = __webpack_require__(55);
  var hiddenKeys = __webpack_require__(56);
  var OBJECT_ALREADY_INITIALIZED = 'Object already initialized';
  var TypeError = global.TypeError;
  var WeakMap = global.WeakMap;
  var set, get, has;
  var enforce = function (it) {
   return has(it) ? get(it) : set(it, {});
  };
  var getterFor = function (TYPE) {
   return function (it) {
    var state;
    if (!isObject(it) || (state = get(it)).type !== TYPE) {
     throw TypeError('Incompatible receiver, ' + TYPE + ' required');
    }
    return state;
   };
  };
  if (NATIVE_WEAK_MAP || shared.state) {
   var store = shared.state || (shared.state = new WeakMap());
   store.get = store.get;
   store.has = store.has;
   store.set = store.set;
   set = function (it, metadata) {
    if (store.has(it))
     throw TypeError(OBJECT_ALREADY_INITIALIZED);
    metadata.facade = it;
    store.set(it, metadata);
    return metadata;
   };
   get = function (it) {
    return store.get(it) || {};
   };
   has = function (it) {
    return store.has(it);
   };
  } else {
   var STATE = sharedKey('state');
   hiddenKeys[STATE] = true;
   set = function (it, metadata) {
    if (hasOwn(it, STATE))
     throw TypeError(OBJECT_ALREADY_INITIALIZED);
    metadata.facade = it;
    createNonEnumerableProperty(it, STATE, metadata);
    return metadata;
   };
   get = function (it) {
    return hasOwn(it, STATE) ? it[STATE] : {};
   };
   has = function (it) {
    return hasOwn(it, STATE);
   };
  }
  module.exports = {
   set: set,
   get: get,
   has: has,
   enforce: enforce,
   getterFor: getterFor
  };
  
  /***/ }),
  /* 54 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var isCallable = __webpack_require__(22);
  var WeakMap = global.WeakMap;
  module.exports = isCallable(WeakMap) && /native code/.test(String(WeakMap));
  
  /***/ }),
  /* 55 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var shared = __webpack_require__(36);
  var uid = __webpack_require__(42);
  var keys = shared('keys');
  module.exports = function (key) {
   return keys[key] || (keys[key] = uid(key));
  };
  
  /***/ }),
  /* 56 */
  /***/ ((module) => {
  
  
  module.exports = {};
  
  /***/ }),
  /* 57 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var hasOwn = __webpack_require__(40);
  var ownKeys = __webpack_require__(58);
  var getOwnPropertyDescriptorModule = __webpack_require__(6);
  var definePropertyModule = __webpack_require__(46);
  module.exports = function (target, source, exceptions) {
   var keys = ownKeys(source);
   var defineProperty = definePropertyModule.f;
   var getOwnPropertyDescriptor = getOwnPropertyDescriptorModule.f;
   for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    if (!hasOwn(target, key) && !(exceptions && hasOwn(exceptions, key))) {
     defineProperty(target, key, getOwnPropertyDescriptor(source, key));
    }
   }
  };
  
  /***/ }),
  /* 58 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  var uncurryThis = __webpack_require__(15);
  var getOwnPropertyNamesModule = __webpack_require__(59);
  var getOwnPropertySymbolsModule = __webpack_require__(68);
  var anObject = __webpack_require__(48);
  var concat = uncurryThis([].concat);
  module.exports = getBuiltIn('Reflect', 'ownKeys') || function ownKeys(it) {
   var keys = getOwnPropertyNamesModule.f(anObject(it));
   var getOwnPropertySymbols = getOwnPropertySymbolsModule.f;
   return getOwnPropertySymbols ? concat(keys, getOwnPropertySymbols(it)) : keys;
  };
  
  /***/ }),
  /* 59 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  var internalObjectKeys = __webpack_require__(60);
  var enumBugKeys = __webpack_require__(67);
  var hiddenKeys = enumBugKeys.concat('length', 'prototype');
  exports.f = Object.getOwnPropertyNames || function getOwnPropertyNames(O) {
   return internalObjectKeys(O, hiddenKeys);
  };
  
  /***/ }),
  /* 60 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var hasOwn = __webpack_require__(40);
  var toIndexedObject = __webpack_require__(13);
  var indexOf = (__webpack_require__(61).indexOf);
  var hiddenKeys = __webpack_require__(56);
  var push = uncurryThis([].push);
  module.exports = function (object, names) {
   var O = toIndexedObject(object);
   var i = 0;
   var result = [];
   var key;
   for (key in O)
    !hasOwn(hiddenKeys, key) && hasOwn(O, key) && push(result, key);
   while (names.length > i)
    if (hasOwn(O, key = names[i++])) {
     ~indexOf(result, key) || push(result, key);
    }
   return result;
  };
  
  /***/ }),
  /* 61 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toIndexedObject = __webpack_require__(13);
  var toAbsoluteIndex = __webpack_require__(62);
  var lengthOfArrayLike = __webpack_require__(65);
  var createMethod = function (IS_INCLUDES) {
   return function ($this, el, fromIndex) {
    var O = toIndexedObject($this);
    var length = lengthOfArrayLike(O);
    var index = toAbsoluteIndex(fromIndex, length);
    var value;
    if (IS_INCLUDES && el !== el)
     while (length > index) {
      value = O[index++];
      if (value !== value)
       return true;
     }
    else
     for (; length > index; index++) {
      if ((IS_INCLUDES || index in O) && O[index] === el)
       return IS_INCLUDES || index || 0;
     }
    return !IS_INCLUDES && -1;
   };
  };
  module.exports = {
   includes: createMethod(true),
   indexOf: createMethod(false)
  };
  
  /***/ }),
  /* 62 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toIntegerOrInfinity = __webpack_require__(63);
  var max = Math.max;
  var min = Math.min;
  module.exports = function (index, length) {
   var integer = toIntegerOrInfinity(index);
   return integer < 0 ? max(integer + length, 0) : min(integer, length);
  };
  
  /***/ }),
  /* 63 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var trunc = __webpack_require__(64);
  module.exports = function (argument) {
   var number = +argument;
   return number !== number || number === 0 ? 0 : trunc(number);
  };
  
  /***/ }),
  /* 64 */
  /***/ ((module) => {
  
  
  var ceil = Math.ceil;
  var floor = Math.floor;
  module.exports = Math.trunc || function trunc(x) {
   var n = +x;
   return (n > 0 ? floor : ceil)(n);
  };
  
  /***/ }),
  /* 65 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toLength = __webpack_require__(66);
  module.exports = function (obj) {
   return toLength(obj.length);
  };
  
  /***/ }),
  /* 66 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toIntegerOrInfinity = __webpack_require__(63);
  var min = Math.min;
  module.exports = function (argument) {
   return argument > 0 ? min(toIntegerOrInfinity(argument), 0x1FFFFFFFFFFFFF) : 0;
  };
  
  /***/ }),
  /* 67 */
  /***/ ((module) => {
  
  
  module.exports = [
   'constructor',
   'hasOwnProperty',
   'isPrototypeOf',
   'propertyIsEnumerable',
   'toLocaleString',
   'toString',
   'valueOf'
  ];
  
  /***/ }),
  /* 68 */
  /***/ ((__unused_webpack_module, exports) => {
  
  
  exports.f = Object.getOwnPropertySymbols;
  
  /***/ }),
  /* 69 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  var isCallable = __webpack_require__(22);
  var replacement = /#|\.prototype\./;
  var isForced = function (feature, detection) {
   var value = data[normalize(feature)];
   return value === POLYFILL ? true : value === NATIVE ? false : isCallable(detection) ? fails(detection) : !!detection;
  };
  var normalize = isForced.normalize = function (string) {
   return String(string).replace(replacement, '.').toLowerCase();
  };
  var data = isForced.data = {};
  var NATIVE = isForced.NATIVE = 'N';
  var POLYFILL = isForced.POLYFILL = 'P';
  module.exports = isForced;
  
  /***/ }),
  /* 70 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var classof = __webpack_require__(16);
  module.exports = classof(global.process) === 'process';
  
  /***/ }),
  /* 71 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThisAccessor = __webpack_require__(72);
  var anObject = __webpack_require__(48);
  var aPossiblePrototype = __webpack_require__(73);
  module.exports = Object.setPrototypeOf || ('__proto__' in {} ? (function () {
   var CORRECT_SETTER = false;
   var test = {};
   var setter;
   try {
    setter = uncurryThisAccessor(Object.prototype, '__proto__', 'set');
    setter(test, []);
    CORRECT_SETTER = test instanceof Array;
   } catch (error) {
   }
   return function setPrototypeOf(O, proto) {
    anObject(O);
    aPossiblePrototype(proto);
    if (CORRECT_SETTER)
     setter(O, proto);
    else
     O.__proto__ = proto;
    return O;
   };
  }()) : undefined);
  
  /***/ }),
  /* 72 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var aCallable = __webpack_require__(32);
  module.exports = function (object, key, method) {
   try {
    return uncurryThis(aCallable(Object.getOwnPropertyDescriptor(object, key)[method]));
   } catch (error) {
   }
  };
  
  /***/ }),
  /* 73 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isCallable = __webpack_require__(22);
  var $String = String;
  var $TypeError = TypeError;
  module.exports = function (argument) {
   if (typeof argument == 'object' || isCallable(argument))
    return argument;
   throw $TypeError("Can't set " + $String(argument) + ' as a prototype');
  };
  
  /***/ }),
  /* 74 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var defineProperty = (__webpack_require__(46).f);
  var hasOwn = __webpack_require__(40);
  var wellKnownSymbol = __webpack_require__(35);
  var TO_STRING_TAG = wellKnownSymbol('toStringTag');
  module.exports = function (target, TAG, STATIC) {
   if (target && !STATIC)
    target = target.prototype;
   if (target && !hasOwn(target, TO_STRING_TAG)) {
    defineProperty(target, TO_STRING_TAG, {
     configurable: true,
     value: TAG
    });
   }
  };
  
  /***/ }),
  /* 75 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  var defineBuiltInAccessor = __webpack_require__(76);
  var wellKnownSymbol = __webpack_require__(35);
  var DESCRIPTORS = __webpack_require__(7);
  var SPECIES = wellKnownSymbol('species');
  module.exports = function (CONSTRUCTOR_NAME) {
   var Constructor = getBuiltIn(CONSTRUCTOR_NAME);
   if (DESCRIPTORS && Constructor && !Constructor[SPECIES]) {
    defineBuiltInAccessor(Constructor, SPECIES, {
     configurable: true,
     get: function () {
      return this;
     }
    });
   }
  };
  
  /***/ }),
  /* 76 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var makeBuiltIn = __webpack_require__(50);
  var defineProperty = __webpack_require__(46);
  module.exports = function (target, name, descriptor) {
   if (descriptor.get)
    makeBuiltIn(descriptor.get, name, { getter: true });
   if (descriptor.set)
    makeBuiltIn(descriptor.set, name, { setter: true });
   return defineProperty.f(target, name, descriptor);
  };
  
  /***/ }),
  /* 77 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isPrototypeOf = __webpack_require__(26);
  var $TypeError = TypeError;
  module.exports = function (it, Prototype) {
   if (isPrototypeOf(Prototype, it))
    return it;
   throw $TypeError('Incorrect invocation');
  };
  
  /***/ }),
  /* 78 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var anObject = __webpack_require__(48);
  var aConstructor = __webpack_require__(79);
  var isNullOrUndefined = __webpack_require__(18);
  var wellKnownSymbol = __webpack_require__(35);
  var SPECIES = wellKnownSymbol('species');
  module.exports = function (O, defaultConstructor) {
   var C = anObject(O).constructor;
   var S;
   return C === undefined || isNullOrUndefined(S = anObject(C)[SPECIES]) ? defaultConstructor : aConstructor(S);
  };
  
  /***/ }),
  /* 79 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isConstructor = __webpack_require__(80);
  var tryToString = __webpack_require__(33);
  var $TypeError = TypeError;
  module.exports = function (argument) {
   if (isConstructor(argument))
    return argument;
   throw $TypeError(tryToString(argument) + ' is not a constructor');
  };
  
  /***/ }),
  /* 80 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var fails = __webpack_require__(8);
  var isCallable = __webpack_require__(22);
  var classof = __webpack_require__(81);
  var getBuiltIn = __webpack_require__(25);
  var inspectSource = __webpack_require__(52);
  var noop = function () {
  };
  var empty = [];
  var construct = getBuiltIn('Reflect', 'construct');
  var constructorRegExp = /^\s*(?:class|function)\b/;
  var exec = uncurryThis(constructorRegExp.exec);
  var INCORRECT_TO_STRING = !constructorRegExp.exec(noop);
  var isConstructorModern = function isConstructor(argument) {
   if (!isCallable(argument))
    return false;
   try {
    construct(noop, empty, argument);
    return true;
   } catch (error) {
    return false;
   }
  };
  var isConstructorLegacy = function isConstructor(argument) {
   if (!isCallable(argument))
    return false;
   switch (classof(argument)) {
   case 'AsyncFunction':
   case 'GeneratorFunction':
   case 'AsyncGeneratorFunction':
    return false;
   }
   try {
    return INCORRECT_TO_STRING || !!exec(constructorRegExp, inspectSource(argument));
   } catch (error) {
    return true;
   }
  };
  isConstructorLegacy.sham = true;
  module.exports = !construct || fails(function () {
   var called;
   return isConstructorModern(isConstructorModern.call) || !isConstructorModern(Object) || !isConstructorModern(function () {
    called = true;
   }) || called;
  }) ? isConstructorLegacy : isConstructorModern;
  
  /***/ }),
  /* 81 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var TO_STRING_TAG_SUPPORT = __webpack_require__(82);
  var isCallable = __webpack_require__(22);
  var classofRaw = __webpack_require__(16);
  var wellKnownSymbol = __webpack_require__(35);
  var TO_STRING_TAG = wellKnownSymbol('toStringTag');
  var $Object = Object;
  var CORRECT_ARGUMENTS = classofRaw((function () {
   return arguments;
  }())) === 'Arguments';
  var tryGet = function (it, key) {
   try {
    return it[key];
   } catch (error) {
   }
  };
  module.exports = TO_STRING_TAG_SUPPORT ? classofRaw : function (it) {
   var O, tag, result;
   return it === undefined ? 'Undefined' : it === null ? 'Null' : typeof (tag = tryGet(O = $Object(it), TO_STRING_TAG)) == 'string' ? tag : CORRECT_ARGUMENTS ? classofRaw(O) : (result = classofRaw(O)) === 'Object' && isCallable(O.callee) ? 'Arguments' : result;
  };
  
  /***/ }),
  /* 82 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var wellKnownSymbol = __webpack_require__(35);
  var TO_STRING_TAG = wellKnownSymbol('toStringTag');
  var test = {};
  test[TO_STRING_TAG] = 'z';
  module.exports = String(test) === '[object z]';
  
  /***/ }),
  /* 83 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var apply = __webpack_require__(84);
  var bind = __webpack_require__(85);
  var isCallable = __webpack_require__(22);
  var hasOwn = __webpack_require__(40);
  var fails = __webpack_require__(8);
  var html = __webpack_require__(87);
  var arraySlice = __webpack_require__(88);
  var createElement = __webpack_require__(44);
  var validateArgumentsLength = __webpack_require__(89);
  var IS_IOS = __webpack_require__(90);
  var IS_NODE = __webpack_require__(70);
  var set = global.setImmediate;
  var clear = global.clearImmediate;
  var process = global.process;
  var Dispatch = global.Dispatch;
  var Function = global.Function;
  var MessageChannel = global.MessageChannel;
  var String = global.String;
  var counter = 0;
  var queue = {};
  var ONREADYSTATECHANGE = 'onreadystatechange';
  var $location, defer, channel, port;
  fails(function () {
   $location = global.location;
  });
  var run = function (id) {
   if (hasOwn(queue, id)) {
    var fn = queue[id];
    delete queue[id];
    fn();
   }
  };
  var runner = function (id) {
   return function () {
    run(id);
   };
  };
  var eventListener = function (event) {
   run(event.data);
  };
  var globalPostMessageDefer = function (id) {
   global.postMessage(String(id), $location.protocol + '//' + $location.host);
  };
  if (!set || !clear) {
   set = function setImmediate(handler) {
    validateArgumentsLength(arguments.length, 1);
    var fn = isCallable(handler) ? handler : Function(handler);
    var args = arraySlice(arguments, 1);
    queue[++counter] = function () {
     apply(fn, undefined, args);
    };
    defer(counter);
    return counter;
   };
   clear = function clearImmediate(id) {
    delete queue[id];
   };
   if (IS_NODE) {
    defer = function (id) {
     process.nextTick(runner(id));
    };
   } else if (Dispatch && Dispatch.now) {
    defer = function (id) {
     Dispatch.now(runner(id));
    };
   } else if (MessageChannel && !IS_IOS) {
    channel = new MessageChannel();
    port = channel.port2;
    channel.port1.onmessage = eventListener;
    defer = bind(port.postMessage, port);
   } else if (global.addEventListener && isCallable(global.postMessage) && !global.importScripts && $location && $location.protocol !== 'file:' && !fails(globalPostMessageDefer)) {
    defer = globalPostMessageDefer;
    global.addEventListener('message', eventListener, false);
   } else if (ONREADYSTATECHANGE in createElement('script')) {
    defer = function (id) {
     html.appendChild(createElement('script'))[ONREADYSTATECHANGE] = function () {
      html.removeChild(this);
      run(id);
     };
    };
   } else {
    defer = function (id) {
     setTimeout(runner(id), 0);
    };
   }
  }
  module.exports = {
   set: set,
   clear: clear
  };
  
  /***/ }),
  /* 84 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NATIVE_BIND = __webpack_require__(10);
  var FunctionPrototype = Function.prototype;
  var apply = FunctionPrototype.apply;
  var call = FunctionPrototype.call;
  module.exports = typeof Reflect == 'object' && Reflect.apply || (NATIVE_BIND ? call.bind(apply) : function () {
   return call.apply(apply, arguments);
  });
  
  /***/ }),
  /* 85 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(86);
  var aCallable = __webpack_require__(32);
  var NATIVE_BIND = __webpack_require__(10);
  var bind = uncurryThis(uncurryThis.bind);
  module.exports = function (fn, that) {
   aCallable(fn);
   return that === undefined ? fn : NATIVE_BIND ? bind(fn, that) : function () {
    return fn.apply(that, arguments);
   };
  };
  
  /***/ }),
  /* 86 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var classofRaw = __webpack_require__(16);
  var uncurryThis = __webpack_require__(15);
  module.exports = function (fn) {
   if (classofRaw(fn) === 'Function')
    return uncurryThis(fn);
  };
  
  /***/ }),
  /* 87 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  module.exports = getBuiltIn('document', 'documentElement');
  
  /***/ }),
  /* 88 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  module.exports = uncurryThis([].slice);
  
  /***/ }),
  /* 89 */
  /***/ ((module) => {
  
  
  var $TypeError = TypeError;
  module.exports = function (passed, required) {
   if (passed < required)
    throw $TypeError('Not enough arguments');
   return passed;
  };
  
  /***/ }),
  /* 90 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var userAgent = __webpack_require__(30);
  module.exports = /(?:ipad|iphone|ipod).*applewebkit/i.test(userAgent);
  
  /***/ }),
  /* 91 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var bind = __webpack_require__(85);
  var getOwnPropertyDescriptor = (__webpack_require__(6).f);
  var macrotask = (__webpack_require__(83).set);
  var Queue = __webpack_require__(92);
  var IS_IOS = __webpack_require__(90);
  var IS_IOS_PEBBLE = __webpack_require__(93);
  var IS_WEBOS_WEBKIT = __webpack_require__(94);
  var IS_NODE = __webpack_require__(70);
  var MutationObserver = global.MutationObserver || global.WebKitMutationObserver;
  var document = global.document;
  var process = global.process;
  var Promise = global.Promise;
  var queueMicrotaskDescriptor = getOwnPropertyDescriptor(global, 'queueMicrotask');
  var microtask = queueMicrotaskDescriptor && queueMicrotaskDescriptor.value;
  var notify, toggle, node, promise, then;
  if (!microtask) {
   var queue = new Queue();
   var flush = function () {
    var parent, fn;
    if (IS_NODE && (parent = process.domain))
     parent.exit();
    while (fn = queue.get())
     try {
      fn();
     } catch (error) {
      if (queue.head)
       notify();
      throw error;
     }
    if (parent)
     parent.enter();
   };
   if (!IS_IOS && !IS_NODE && !IS_WEBOS_WEBKIT && MutationObserver && document) {
    toggle = true;
    node = document.createTextNode('');
    new MutationObserver(flush).observe(node, { characterData: true });
    notify = function () {
     node.data = toggle = !toggle;
    };
   } else if (!IS_IOS_PEBBLE && Promise && Promise.resolve) {
    promise = Promise.resolve(undefined);
    promise.constructor = Promise;
    then = bind(promise.then, promise);
    notify = function () {
     then(flush);
    };
   } else if (IS_NODE) {
    notify = function () {
     process.nextTick(flush);
    };
   } else {
    macrotask = bind(macrotask, global);
    notify = function () {
     macrotask(flush);
    };
   }
   microtask = function (fn) {
    if (!queue.head)
     notify();
    queue.add(fn);
   };
  }
  module.exports = microtask;
  
  /***/ }),
  /* 92 */
  /***/ ((module) => {
  
  
  var Queue = function () {
   this.head = null;
   this.tail = null;
  };
  Queue.prototype = {
   add: function (item) {
    var entry = {
     item: item,
     next: null
    };
    var tail = this.tail;
    if (tail)
     tail.next = entry;
    else
     this.head = entry;
    this.tail = entry;
   },
   get: function () {
    var entry = this.head;
    if (entry) {
     var next = this.head = entry.next;
     if (next === null)
      this.tail = null;
     return entry.item;
    }
   }
  };
  module.exports = Queue;
  
  /***/ }),
  /* 93 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var userAgent = __webpack_require__(30);
  module.exports = /ipad|iphone|ipod/i.test(userAgent) && typeof Pebble != 'undefined';
  
  /***/ }),
  /* 94 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var userAgent = __webpack_require__(30);
  module.exports = /web0s(?!.*chrome)/i.test(userAgent);
  
  /***/ }),
  /* 95 */
  /***/ ((module) => {
  
  
  module.exports = function (a, b) {
   try {
    arguments.length === 1 ? console.error(a) : console.error(a, b);
   } catch (error) {
   }
  };
  
  /***/ }),
  /* 96 */
  /***/ ((module) => {
  
  
  module.exports = function (exec) {
   try {
    return {
     error: false,
     value: exec()
    };
   } catch (error) {
    return {
     error: true,
     value: error
    };
   }
  };
  
  /***/ }),
  /* 97 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  module.exports = global.Promise;
  
  /***/ }),
  /* 98 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var global = __webpack_require__(5);
  var NativePromiseConstructor = __webpack_require__(97);
  var isCallable = __webpack_require__(22);
  var isForced = __webpack_require__(69);
  var inspectSource = __webpack_require__(52);
  var wellKnownSymbol = __webpack_require__(35);
  var IS_BROWSER = __webpack_require__(99);
  var IS_DENO = __webpack_require__(100);
  var IS_PURE = __webpack_require__(37);
  var V8_VERSION = __webpack_require__(29);
  var NativePromisePrototype = NativePromiseConstructor && NativePromiseConstructor.prototype;
  var SPECIES = wellKnownSymbol('species');
  var SUBCLASSING = false;
  var NATIVE_PROMISE_REJECTION_EVENT = isCallable(global.PromiseRejectionEvent);
  var FORCED_PROMISE_CONSTRUCTOR = isForced('Promise', function () {
   var PROMISE_CONSTRUCTOR_SOURCE = inspectSource(NativePromiseConstructor);
   var GLOBAL_CORE_JS_PROMISE = PROMISE_CONSTRUCTOR_SOURCE !== String(NativePromiseConstructor);
   if (!GLOBAL_CORE_JS_PROMISE && V8_VERSION === 66)
    return true;
   if (IS_PURE && !(NativePromisePrototype['catch'] && NativePromisePrototype['finally']))
    return true;
   if (!V8_VERSION || V8_VERSION < 51 || !/native code/.test(PROMISE_CONSTRUCTOR_SOURCE)) {
    var promise = new NativePromiseConstructor(function (resolve) {
     resolve(1);
    });
    var FakePromise = function (exec) {
     exec(function () {
     }, function () {
     });
    };
    var constructor = promise.constructor = {};
    constructor[SPECIES] = FakePromise;
    SUBCLASSING = promise.then(function () {
    }) instanceof FakePromise;
    if (!SUBCLASSING)
     return true;
   }
   return !GLOBAL_CORE_JS_PROMISE && (IS_BROWSER || IS_DENO) && !NATIVE_PROMISE_REJECTION_EVENT;
  });
  module.exports = {
   CONSTRUCTOR: FORCED_PROMISE_CONSTRUCTOR,
   REJECTION_EVENT: NATIVE_PROMISE_REJECTION_EVENT,
   SUBCLASSING: SUBCLASSING
  };
  
  /***/ }),
  /* 99 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var IS_DENO = __webpack_require__(100);
  var IS_NODE = __webpack_require__(70);
  module.exports = !IS_DENO && !IS_NODE && typeof window == 'object' && typeof document == 'object';
  
  /***/ }),
  /* 100 */
  /***/ ((module) => {
  
  
  module.exports = typeof Deno == 'object' && Deno && typeof Deno.version == 'object';
  
  /***/ }),
  /* 101 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aCallable = __webpack_require__(32);
  var $TypeError = TypeError;
  var PromiseCapability = function (C) {
   var resolve, reject;
   this.promise = new C(function ($$resolve, $$reject) {
    if (resolve !== undefined || reject !== undefined)
     throw $TypeError('Bad Promise constructor');
    resolve = $$resolve;
    reject = $$reject;
   });
   this.resolve = aCallable(resolve);
   this.reject = aCallable(reject);
  };
  module.exports.f = function (C) {
   return new PromiseCapability(C);
  };
  
  /***/ }),
  /* 102 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var call = __webpack_require__(9);
  var aCallable = __webpack_require__(32);
  var newPromiseCapabilityModule = __webpack_require__(101);
  var perform = __webpack_require__(96);
  var iterate = __webpack_require__(103);
  var PROMISE_STATICS_INCORRECT_ITERATION = __webpack_require__(109);
  $({
   target: 'Promise',
   stat: true,
   forced: PROMISE_STATICS_INCORRECT_ITERATION
  }, {
   all: function all(iterable) {
    var C = this;
    var capability = newPromiseCapabilityModule.f(C);
    var resolve = capability.resolve;
    var reject = capability.reject;
    var result = perform(function () {
     var $promiseResolve = aCallable(C.resolve);
     var values = [];
     var counter = 0;
     var remaining = 1;
     iterate(iterable, function (promise) {
      var index = counter++;
      var alreadyCalled = false;
      remaining++;
      call($promiseResolve, C, promise).then(function (value) {
       if (alreadyCalled)
        return;
       alreadyCalled = true;
       values[index] = value;
       --remaining || resolve(values);
      }, reject);
     });
     --remaining || resolve(values);
    });
    if (result.error)
     reject(result.value);
    return capability.promise;
   }
  });
  
  /***/ }),
  /* 103 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var bind = __webpack_require__(85);
  var call = __webpack_require__(9);
  var anObject = __webpack_require__(48);
  var tryToString = __webpack_require__(33);
  var isArrayIteratorMethod = __webpack_require__(104);
  var lengthOfArrayLike = __webpack_require__(65);
  var isPrototypeOf = __webpack_require__(26);
  var getIterator = __webpack_require__(106);
  var getIteratorMethod = __webpack_require__(107);
  var iteratorClose = __webpack_require__(108);
  var $TypeError = TypeError;
  var Result = function (stopped, result) {
   this.stopped = stopped;
   this.result = result;
  };
  var ResultPrototype = Result.prototype;
  module.exports = function (iterable, unboundFunction, options) {
   var that = options && options.that;
   var AS_ENTRIES = !!(options && options.AS_ENTRIES);
   var IS_RECORD = !!(options && options.IS_RECORD);
   var IS_ITERATOR = !!(options && options.IS_ITERATOR);
   var INTERRUPTED = !!(options && options.INTERRUPTED);
   var fn = bind(unboundFunction, that);
   var iterator, iterFn, index, length, result, next, step;
   var stop = function (condition) {
    if (iterator)
     iteratorClose(iterator, 'normal', condition);
    return new Result(true, condition);
   };
   var callFn = function (value) {
    if (AS_ENTRIES) {
     anObject(value);
     return INTERRUPTED ? fn(value[0], value[1], stop) : fn(value[0], value[1]);
    }
    return INTERRUPTED ? fn(value, stop) : fn(value);
   };
   if (IS_RECORD) {
    iterator = iterable.iterator;
   } else if (IS_ITERATOR) {
    iterator = iterable;
   } else {
    iterFn = getIteratorMethod(iterable);
    if (!iterFn)
     throw $TypeError(tryToString(iterable) + ' is not iterable');
    if (isArrayIteratorMethod(iterFn)) {
     for (index = 0, length = lengthOfArrayLike(iterable); length > index; index++) {
      result = callFn(iterable[index]);
      if (result && isPrototypeOf(ResultPrototype, result))
       return result;
     }
     return new Result(false);
    }
    iterator = getIterator(iterable, iterFn);
   }
   next = IS_RECORD ? iterable.next : iterator.next;
   while (!(step = call(next, iterator)).done) {
    try {
     result = callFn(step.value);
    } catch (error) {
     iteratorClose(iterator, 'throw', error);
    }
    if (typeof result == 'object' && result && isPrototypeOf(ResultPrototype, result))
     return result;
   }
   return new Result(false);
  };
  
  /***/ }),
  /* 104 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var wellKnownSymbol = __webpack_require__(35);
  var Iterators = __webpack_require__(105);
  var ITERATOR = wellKnownSymbol('iterator');
  var ArrayPrototype = Array.prototype;
  module.exports = function (it) {
   return it !== undefined && (Iterators.Array === it || ArrayPrototype[ITERATOR] === it);
  };
  
  /***/ }),
  /* 105 */
  /***/ ((module) => {
  
  
  module.exports = {};
  
  /***/ }),
  /* 106 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var aCallable = __webpack_require__(32);
  var anObject = __webpack_require__(48);
  var tryToString = __webpack_require__(33);
  var getIteratorMethod = __webpack_require__(107);
  var $TypeError = TypeError;
  module.exports = function (argument, usingIterator) {
   var iteratorMethod = arguments.length < 2 ? getIteratorMethod(argument) : usingIterator;
   if (aCallable(iteratorMethod))
    return anObject(call(iteratorMethod, argument));
   throw $TypeError(tryToString(argument) + ' is not iterable');
  };
  
  /***/ }),
  /* 107 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var classof = __webpack_require__(81);
  var getMethod = __webpack_require__(31);
  var isNullOrUndefined = __webpack_require__(18);
  var Iterators = __webpack_require__(105);
  var wellKnownSymbol = __webpack_require__(35);
  var ITERATOR = wellKnownSymbol('iterator');
  module.exports = function (it) {
   if (!isNullOrUndefined(it))
    return getMethod(it, ITERATOR) || getMethod(it, '@@iterator') || Iterators[classof(it)];
  };
  
  /***/ }),
  /* 108 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var anObject = __webpack_require__(48);
  var getMethod = __webpack_require__(31);
  module.exports = function (iterator, kind, value) {
   var innerResult, innerError;
   anObject(iterator);
   try {
    innerResult = getMethod(iterator, 'return');
    if (!innerResult) {
     if (kind === 'throw')
      throw value;
     return value;
    }
    innerResult = call(innerResult, iterator);
   } catch (error) {
    innerError = true;
    innerResult = error;
   }
   if (kind === 'throw')
    throw value;
   if (innerError)
    throw innerResult;
   anObject(innerResult);
   return value;
  };
  
  /***/ }),
  /* 109 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var NativePromiseConstructor = __webpack_require__(97);
  var checkCorrectnessOfIteration = __webpack_require__(110);
  var FORCED_PROMISE_CONSTRUCTOR = (__webpack_require__(98).CONSTRUCTOR);
  module.exports = FORCED_PROMISE_CONSTRUCTOR || !checkCorrectnessOfIteration(function (iterable) {
   NativePromiseConstructor.all(iterable).then(undefined, function () {
   });
  });
  
  /***/ }),
  /* 110 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var wellKnownSymbol = __webpack_require__(35);
  var ITERATOR = wellKnownSymbol('iterator');
  var SAFE_CLOSING = false;
  try {
   var called = 0;
   var iteratorWithReturn = {
    next: function () {
     return { done: !!called++ };
    },
    'return': function () {
     SAFE_CLOSING = true;
    }
   };
   iteratorWithReturn[ITERATOR] = function () {
    return this;
   };
   Array.from(iteratorWithReturn, function () {
    throw 2;
   });
  } catch (error) {
  }
  module.exports = function (exec, SKIP_CLOSING) {
   try {
    if (!SKIP_CLOSING && !SAFE_CLOSING)
     return false;
   } catch (error) {
    return false;
   }
   var ITERATION_SUPPORT = false;
   try {
    var object = {};
    object[ITERATOR] = function () {
     return {
      next: function () {
       return { done: ITERATION_SUPPORT = true };
      }
     };
    };
    exec(object);
   } catch (error) {
   }
   return ITERATION_SUPPORT;
  };
  
  /***/ }),
  /* 111 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var IS_PURE = __webpack_require__(37);
  var FORCED_PROMISE_CONSTRUCTOR = (__webpack_require__(98).CONSTRUCTOR);
  var NativePromiseConstructor = __webpack_require__(97);
  var getBuiltIn = __webpack_require__(25);
  var isCallable = __webpack_require__(22);
  var defineBuiltIn = __webpack_require__(49);
  var NativePromisePrototype = NativePromiseConstructor && NativePromiseConstructor.prototype;
  $({
   target: 'Promise',
   proto: true,
   forced: FORCED_PROMISE_CONSTRUCTOR,
   real: true
  }, {
   'catch': function (onRejected) {
    return this.then(undefined, onRejected);
   }
  });
  if (!IS_PURE && isCallable(NativePromiseConstructor)) {
   var method = getBuiltIn('Promise').prototype['catch'];
   if (NativePromisePrototype['catch'] !== method) {
    defineBuiltIn(NativePromisePrototype, 'catch', method, { unsafe: true });
   }
  }
  
  /***/ }),
  /* 112 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var call = __webpack_require__(9);
  var aCallable = __webpack_require__(32);
  var newPromiseCapabilityModule = __webpack_require__(101);
  var perform = __webpack_require__(96);
  var iterate = __webpack_require__(103);
  var PROMISE_STATICS_INCORRECT_ITERATION = __webpack_require__(109);
  $({
   target: 'Promise',
   stat: true,
   forced: PROMISE_STATICS_INCORRECT_ITERATION
  }, {
   race: function race(iterable) {
    var C = this;
    var capability = newPromiseCapabilityModule.f(C);
    var reject = capability.reject;
    var result = perform(function () {
     var $promiseResolve = aCallable(C.resolve);
     iterate(iterable, function (promise) {
      call($promiseResolve, C, promise).then(capability.resolve, reject);
     });
    });
    if (result.error)
     reject(result.value);
    return capability.promise;
   }
  });
  
  /***/ }),
  /* 113 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var call = __webpack_require__(9);
  var newPromiseCapabilityModule = __webpack_require__(101);
  var FORCED_PROMISE_CONSTRUCTOR = (__webpack_require__(98).CONSTRUCTOR);
  $({
   target: 'Promise',
   stat: true,
   forced: FORCED_PROMISE_CONSTRUCTOR
  }, {
   reject: function reject(r) {
    var capability = newPromiseCapabilityModule.f(this);
    call(capability.reject, undefined, r);
    return capability.promise;
   }
  });
  
  /***/ }),
  /* 114 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var getBuiltIn = __webpack_require__(25);
  var IS_PURE = __webpack_require__(37);
  var NativePromiseConstructor = __webpack_require__(97);
  var FORCED_PROMISE_CONSTRUCTOR = (__webpack_require__(98).CONSTRUCTOR);
  var promiseResolve = __webpack_require__(115);
  var PromiseConstructorWrapper = getBuiltIn('Promise');
  var CHECK_WRAPPER = IS_PURE && !FORCED_PROMISE_CONSTRUCTOR;
  $({
   target: 'Promise',
   stat: true,
   forced: IS_PURE || FORCED_PROMISE_CONSTRUCTOR
  }, {
   resolve: function resolve(x) {
    return promiseResolve(CHECK_WRAPPER && this === PromiseConstructorWrapper ? NativePromiseConstructor : this, x);
   }
  });
  
  /***/ }),
  /* 115 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var anObject = __webpack_require__(48);
  var isObject = __webpack_require__(21);
  var newPromiseCapability = __webpack_require__(101);
  module.exports = function (C, x) {
   anObject(C);
   if (isObject(x) && x.constructor === C)
    return x;
   var promiseCapability = newPromiseCapability.f(C);
   var resolve = promiseCapability.resolve;
   resolve(x);
   return promiseCapability.promise;
  };
  
  /***/ }),
  /* 116 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var DESCRIPTORS = __webpack_require__(7);
  var global = __webpack_require__(5);
  var getBuiltIn = __webpack_require__(25);
  var uncurryThis = __webpack_require__(15);
  var call = __webpack_require__(9);
  var isCallable = __webpack_require__(22);
  var isObject = __webpack_require__(21);
  var isArray = __webpack_require__(117);
  var hasOwn = __webpack_require__(40);
  var toString = __webpack_require__(118);
  var lengthOfArrayLike = __webpack_require__(65);
  var createProperty = __webpack_require__(119);
  var fails = __webpack_require__(8);
  var parseJSONString = __webpack_require__(120);
  var NATIVE_SYMBOL = __webpack_require__(28);
  var JSON = global.JSON;
  var Number = global.Number;
  var SyntaxError = global.SyntaxError;
  var nativeParse = JSON && JSON.parse;
  var enumerableOwnProperties = getBuiltIn('Object', 'keys');
  var getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  var at = uncurryThis(''.charAt);
  var slice = uncurryThis(''.slice);
  var exec = uncurryThis(/./.exec);
  var push = uncurryThis([].push);
  var IS_DIGIT = /^\d$/;
  var IS_NON_ZERO_DIGIT = /^[1-9]$/;
  var IS_NUMBER_START = /^(?:-|\d)$/;
  var IS_WHITESPACE = /^[\t\n\r ]$/;
  var PRIMITIVE = 0;
  var OBJECT = 1;
  var $parse = function (source, reviver) {
   source = toString(source);
   var context = new Context(source, 0, '');
   var root = context.parse();
   var value = root.value;
   var endIndex = context.skip(IS_WHITESPACE, root.end);
   if (endIndex < source.length) {
    throw SyntaxError('Unexpected extra character: "' + at(source, endIndex) + '" after the parsed data at: ' + endIndex);
   }
   return isCallable(reviver) ? internalize({ '': value }, '', reviver, root) : value;
  };
  var internalize = function (holder, name, reviver, node) {
   var val = holder[name];
   var unmodified = node && val === node.value;
   var context = unmodified && typeof node.source == 'string' ? { source: node.source } : {};
   var elementRecordsLen, keys, len, i, P;
   if (isObject(val)) {
    var nodeIsArray = isArray(val);
    var nodes = unmodified ? node.nodes : nodeIsArray ? [] : {};
    if (nodeIsArray) {
     elementRecordsLen = nodes.length;
     len = lengthOfArrayLike(val);
     for (i = 0; i < len; i++) {
      internalizeProperty(val, i, internalize(val, '' + i, reviver, i < elementRecordsLen ? nodes[i] : undefined));
     }
    } else {
     keys = enumerableOwnProperties(val);
     len = lengthOfArrayLike(keys);
     for (i = 0; i < len; i++) {
      P = keys[i];
      internalizeProperty(val, P, internalize(val, P, reviver, hasOwn(nodes, P) ? nodes[P] : undefined));
     }
    }
   }
   return call(reviver, holder, name, val, context);
  };
  var internalizeProperty = function (object, key, value) {
   if (DESCRIPTORS) {
    var descriptor = getOwnPropertyDescriptor(object, key);
    if (descriptor && !descriptor.configurable)
     return;
   }
   if (value === undefined)
    delete object[key];
   else
    createProperty(object, key, value);
  };
  var Node = function (value, end, source, nodes) {
   this.value = value;
   this.end = end;
   this.source = source;
   this.nodes = nodes;
  };
  var Context = function (source, index) {
   this.source = source;
   this.index = index;
  };
  Context.prototype = {
   fork: function (nextIndex) {
    return new Context(this.source, nextIndex);
   },
   parse: function () {
    var source = this.source;
    var i = this.skip(IS_WHITESPACE, this.index);
    var fork = this.fork(i);
    var chr = at(source, i);
    if (exec(IS_NUMBER_START, chr))
     return fork.number();
    switch (chr) {
    case '{':
     return fork.object();
    case '[':
     return fork.array();
    case '"':
     return fork.string();
    case 't':
     return fork.keyword(true);
    case 'f':
     return fork.keyword(false);
    case 'n':
     return fork.keyword(null);
    }
    throw SyntaxError('Unexpected character: "' + chr + '" at: ' + i);
   },
   node: function (type, value, start, end, nodes) {
    return new Node(value, end, type ? null : slice(this.source, start, end), nodes);
   },
   object: function () {
    var source = this.source;
    var i = this.index + 1;
    var expectKeypair = false;
    var object = {};
    var nodes = {};
    while (i < source.length) {
     i = this.until([
      '"',
      '}'
     ], i);
     if (at(source, i) === '}' && !expectKeypair) {
      i++;
      break;
     }
     var result = this.fork(i).string();
     var key = result.value;
     i = result.end;
     i = this.until([':'], i) + 1;
     i = this.skip(IS_WHITESPACE, i);
     result = this.fork(i).parse();
     createProperty(nodes, key, result);
     createProperty(object, key, result.value);
     i = this.until([
      ',',
      '}'
     ], result.end);
     var chr = at(source, i);
     if (chr === ',') {
      expectKeypair = true;
      i++;
     } else if (chr === '}') {
      i++;
      break;
     }
    }
    return this.node(OBJECT, object, this.index, i, nodes);
   },
   array: function () {
    var source = this.source;
    var i = this.index + 1;
    var expectElement = false;
    var array = [];
    var nodes = [];
    while (i < source.length) {
     i = this.skip(IS_WHITESPACE, i);
     if (at(source, i) === ']' && !expectElement) {
      i++;
      break;
     }
     var result = this.fork(i).parse();
     push(nodes, result);
     push(array, result.value);
     i = this.until([
      ',',
      ']'
     ], result.end);
     if (at(source, i) === ',') {
      expectElement = true;
      i++;
     } else if (at(source, i) === ']') {
      i++;
      break;
     }
    }
    return this.node(OBJECT, array, this.index, i, nodes);
   },
   string: function () {
    var index = this.index;
    var parsed = parseJSONString(this.source, this.index + 1);
    return this.node(PRIMITIVE, parsed.value, index, parsed.end);
   },
   number: function () {
    var source = this.source;
    var startIndex = this.index;
    var i = startIndex;
    if (at(source, i) === '-')
     i++;
    if (at(source, i) === '0')
     i++;
    else if (exec(IS_NON_ZERO_DIGIT, at(source, i)))
     i = this.skip(IS_DIGIT, ++i);
    else
     throw SyntaxError('Failed to parse number at: ' + i);
    if (at(source, i) === '.')
     i = this.skip(IS_DIGIT, ++i);
    if (at(source, i) === 'e' || at(source, i) === 'E') {
     i++;
     if (at(source, i) === '+' || at(source, i) === '-')
      i++;
     var exponentStartIndex = i;
     i = this.skip(IS_DIGIT, i);
     if (exponentStartIndex === i)
      throw SyntaxError("Failed to parse number's exponent value at: " + i);
    }
    return this.node(PRIMITIVE, Number(slice(source, startIndex, i)), startIndex, i);
   },
   keyword: function (value) {
    var keyword = '' + value;
    var index = this.index;
    var endIndex = index + keyword.length;
    if (slice(this.source, index, endIndex) !== keyword)
     throw SyntaxError('Failed to parse value at: ' + index);
    return this.node(PRIMITIVE, value, index, endIndex);
   },
   skip: function (regex, i) {
    var source = this.source;
    for (; i < source.length; i++)
     if (!exec(regex, at(source, i)))
      break;
    return i;
   },
   until: function (array, i) {
    i = this.skip(IS_WHITESPACE, i);
    var chr = at(this.source, i);
    for (var j = 0; j < array.length; j++)
     if (array[j] === chr)
      return i;
    throw SyntaxError('Unexpected character: "' + chr + '" at: ' + i);
   }
  };
  var NO_SOURCE_SUPPORT = fails(function () {
   var unsafeInt = '9007199254740993';
   var source;
   nativeParse(unsafeInt, function (key, value, context) {
    source = context.source;
   });
   return source !== unsafeInt;
  });
  var PROPER_BASE_PARSE = NATIVE_SYMBOL && !fails(function () {
   return 1 / nativeParse('-0 \t') !== -Infinity;
  });
  $({
   target: 'JSON',
   stat: true,
   forced: NO_SOURCE_SUPPORT
  }, {
   parse: function parse(text, reviver) {
    return PROPER_BASE_PARSE && !isCallable(reviver) ? nativeParse(text) : $parse(text, reviver);
   }
  });
  
  /***/ }),
  /* 117 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var classof = __webpack_require__(16);
  module.exports = Array.isArray || function isArray(argument) {
   return classof(argument) === 'Array';
  };
  
  /***/ }),
  /* 118 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var classof = __webpack_require__(81);
  var $String = String;
  module.exports = function (argument) {
   if (classof(argument) === 'Symbol')
    throw TypeError('Cannot convert a Symbol value to a string');
   return $String(argument);
  };
  
  /***/ }),
  /* 119 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toPropertyKey = __webpack_require__(19);
  var definePropertyModule = __webpack_require__(46);
  var createPropertyDescriptor = __webpack_require__(12);
  module.exports = function (object, key, value) {
   var propertyKey = toPropertyKey(key);
   if (propertyKey in object)
    definePropertyModule.f(object, propertyKey, createPropertyDescriptor(0, value));
   else
    object[propertyKey] = value;
  };
  
  /***/ }),
  /* 120 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var hasOwn = __webpack_require__(40);
  var $SyntaxError = SyntaxError;
  var $parseInt = parseInt;
  var fromCharCode = String.fromCharCode;
  var at = uncurryThis(''.charAt);
  var slice = uncurryThis(''.slice);
  var exec = uncurryThis(/./.exec);
  var codePoints = {
   '\\"': '"',
   '\\\\': '\\',
   '\\/': '/',
   '\\b': '\b',
   '\\f': '\f',
   '\\n': '\n',
   '\\r': '\r',
   '\\t': '\t'
  };
  var IS_4_HEX_DIGITS = /^[\da-f]{4}$/i;
  var IS_C0_CONTROL_CODE = /^[\u0000-\u001F]$/;
  module.exports = function (source, i) {
   var unterminated = true;
   var value = '';
   while (i < source.length) {
    var chr = at(source, i);
    if (chr === '\\') {
     var twoChars = slice(source, i, i + 2);
     if (hasOwn(codePoints, twoChars)) {
      value += codePoints[twoChars];
      i += 2;
     } else if (twoChars === '\\u') {
      i += 2;
      var fourHexDigits = slice(source, i, i + 4);
      if (!exec(IS_4_HEX_DIGITS, fourHexDigits))
       throw $SyntaxError('Bad Unicode escape at: ' + i);
      value += fromCharCode($parseInt(fourHexDigits, 16));
      i += 4;
     } else
      throw $SyntaxError('Unknown escape sequence: "' + twoChars + '"');
    } else if (chr === '"') {
     unterminated = false;
     i++;
     break;
    } else {
     if (exec(IS_C0_CONTROL_CODE, chr))
      throw $SyntaxError('Bad control character in string literal at: ' + i);
     value += chr;
     i++;
    }
   }
   if (unterminated)
    throw $SyntaxError('Unterminated string at: ' + i);
   return {
    value: value,
    end: i
   };
  };
  
  /***/ }),
  /* 121 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFViewerApplication = exports.PDFPrintServiceFactory = exports.DefaultExternalServices = void 0;
  __webpack_require__(122);
  __webpack_require__(2);
  __webpack_require__(131);
  __webpack_require__(136);
  __webpack_require__(142);
  __webpack_require__(145);
  __webpack_require__(146);
  __webpack_require__(147);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  var _app_options = __webpack_require__(183);
  var _event_utils = __webpack_require__(184);
  var _pdf_link_service = __webpack_require__(185);
  var _webAlt_text_manager = __webpack_require__(186);
  var _webAnnotation_editor_params = __webpack_require__(187);
  var _overlay_manager = __webpack_require__(188);
  var _password_prompt = __webpack_require__(189);
  var _webPdf_attachment_viewer = __webpack_require__(190);
  var _webPdf_cursor_tools = __webpack_require__(192);
  var _webPdf_document_properties = __webpack_require__(194);
  var _webPdf_find_bar = __webpack_require__(195);
  var _pdf_find_controller = __webpack_require__(196);
  var _pdf_history = __webpack_require__(200);
  var _webPdf_layer_viewer = __webpack_require__(201);
  var _webPdf_outline_viewer = __webpack_require__(202);
  var _webPdf_presentation_mode = __webpack_require__(203);
  var _pdf_rendering_queue = __webpack_require__(204);
  var _pdf_scripting_manager = __webpack_require__(206);
  var _webPdf_sidebar = __webpack_require__(207);
  var _webPdf_thumbnail_viewer = __webpack_require__(208);
  var _pdf_viewer = __webpack_require__(210);
  var _webSecondary_toolbar = __webpack_require__(222);
  var _webToolbar = __webpack_require__(223);
  var _view_history = __webpack_require__(224);
  const FORCE_PAGES_LOADED_TIMEOUT = 10000;
  const WHEEL_ZOOM_DISABLED_TIMEOUT = 1000;
  const ViewOnLoad = {
    UNKNOWN: -1,
    PREVIOUS: 0,
    INITIAL: 1
  };
  const ViewerCssTheme = {
    AUTOMATIC: 0,
    LIGHT: 1,
    DARK: 2
  };
  class DefaultExternalServices {
    constructor() {
      throw new Error("Cannot initialize DefaultExternalServices.");
    }
    static updateFindControlState(data) {}
    static updateFindMatchesCount(data) {}
    static initPassiveLoading(callbacks) {}
    static reportTelemetry(data) {}
    static createDownloadManager() {
      throw new Error("Not implemented: createDownloadManager");
    }
    static createPreferences() {
      throw new Error("Not implemented: createPreferences");
    }
    static createL10n(options) {
      throw new Error("Not implemented: createL10n");
    }
    static createScripting(options) {
      throw new Error("Not implemented: createScripting");
    }
    static get supportsPinchToZoom() {
      return (0, _pdfjsLib.shadow)(this, "supportsPinchToZoom", true);
    }
    static get supportsIntegratedFind() {
      return (0, _pdfjsLib.shadow)(this, "supportsIntegratedFind", false);
    }
    static get supportsDocumentFonts() {
      return (0, _pdfjsLib.shadow)(this, "supportsDocumentFonts", true);
    }
    static get supportedMouseWheelZoomModifierKeys() {
      return (0, _pdfjsLib.shadow)(this, "supportedMouseWheelZoomModifierKeys", {
        ctrlKey: true,
        metaKey: true
      });
    }
    static get isInAutomation() {
      return (0, _pdfjsLib.shadow)(this, "isInAutomation", false);
    }
    static updateEditorStates(data) {
      throw new Error("Not implemented: updateEditorStates");
    }
    static get canvasMaxAreaInBytes() {
      return (0, _pdfjsLib.shadow)(this, "canvasMaxAreaInBytes", -1);
    }
    static getNimbusExperimentData() {
      return (0, _pdfjsLib.shadow)(this, "getNimbusExperimentData", Promise.resolve(null));
    }
  }
  exports.DefaultExternalServices = DefaultExternalServices;
  const PDFViewerApplication = {
    initialBookmark: document.location.hash.substring(1),
    _initializedCapability: new _pdfjsLib.PromiseCapability(),
    appConfig: null,
    pdfDocument: null,
    pdfLoadingTask: null,
    printService: null,
    pdfViewer: null,
    pdfThumbnailViewer: null,
    pdfRenderingQueue: null,
    pdfPresentationMode: null,
    pdfDocumentProperties: null,
    pdfLinkService: null,
    pdfHistory: null,
    pdfSidebar: null,
    pdfOutlineViewer: null,
    pdfAttachmentViewer: null,
    pdfLayerViewer: null,
    pdfCursorTools: null,
    pdfScriptingManager: null,
    store: null,
    downloadManager: null,
    overlayManager: null,
    preferences: null,
    toolbar: null,
    secondaryToolbar: null,
    eventBus: null,
    l10n: null,
    annotationEditorParams: null,
    isInitialViewSet: false,
    downloadComplete: false,
    isViewerEmbedded: window.parent !== window,
    url: "",
    baseUrl: "",
    _downloadUrl: "",
    externalServices: DefaultExternalServices,
    _boundEvents: Object.create(null),
    documentInfo: null,
    metadata: null,
    _contentDispositionFilename: null,
    _contentLength: null,
    _saveInProgress: false,
    _wheelUnusedTicks: 0,
    _wheelUnusedFactor: 1,
    _touchUnusedTicks: 0,
    _touchUnusedFactor: 1,
    _PDFBug: null,
    _hasAnnotationEditors: false,
    _title: document.title,
    _printAnnotationStoragePromise: null,
    _touchInfo: null,
    _isCtrlKeyDown: false,
    _nimbusDataPromise: null,
    async initialize(appConfig) {
      this.preferences = this.externalServices.createPreferences();
      this.appConfig = appConfig;
      await this._initializeOptions();
      this._forceCssTheme();
      await this._initializeL10n();
      if (this.isViewerEmbedded && _app_options.AppOptions.get("externalLinkTarget") === _pdf_link_service.LinkTarget.NONE) {
        _app_options.AppOptions.set("externalLinkTarget", _pdf_link_service.LinkTarget.TOP);
      }
      await this._initializeViewerComponents();
      this.bindEvents();
      this.bindWindowEvents();
      const appContainer = appConfig.appContainer || document.documentElement;
      this.l10n.translate(appContainer).then(() => {
        this.eventBus.dispatch("localized", {
          source: this
        });
      });
      this._initializedCapability.resolve();
    },
    async _initializeOptions() {
      if (_app_options.AppOptions.get("disablePreferences")) {
        if (_app_options.AppOptions.get("pdfBugEnabled")) {
          await this._parseHashParams();
        }
        return;
      }
      if (_app_options.AppOptions._hasUserOptions()) {
        console.warn("_initializeOptions: The Preferences may override manually set AppOptions; " + 'please use the "disablePreferences"-option in order to prevent that.');
      }
      try {
        _app_options.AppOptions.setAll(await this.preferences.getAll());
      } catch (reason) {
        console.error(`_initializeOptions: "${reason.message}".`);
      }
      if (_app_options.AppOptions.get("pdfBugEnabled")) {
        await this._parseHashParams();
      }
    },
    async _parseHashParams() {
      const hash = document.location.hash.substring(1);
      if (!hash) {
        return;
      }
      const {
          mainContainer,
          viewerContainer
        } = this.appConfig,
        params = (0, _ui_utils.parseQueryString)(hash);
      if (params.get("disableworker") === "true") {
        try {
          await loadFakeWorker();
        } catch (ex) {
          console.error(`_parseHashParams: "${ex.message}".`);
        }
      }
      if (params.has("disablerange")) {
        _app_options.AppOptions.set("disableRange", params.get("disablerange") === "true");
      }
      if (params.has("disablestream")) {
        _app_options.AppOptions.set("disableStream", params.get("disablestream") === "true");
      }
      if (params.has("disableautofetch")) {
        _app_options.AppOptions.set("disableAutoFetch", params.get("disableautofetch") === "true");
      }
      if (params.has("disablefontface")) {
        _app_options.AppOptions.set("disableFontFace", params.get("disablefontface") === "true");
      }
      if (params.has("disablehistory")) {
        _app_options.AppOptions.set("disableHistory", params.get("disablehistory") === "true");
      }
      if (params.has("verbosity")) {
        _app_options.AppOptions.set("verbosity", params.get("verbosity") | 0);
      }
      if (params.has("textlayer")) {
        switch (params.get("textlayer")) {
          case "off":
            _app_options.AppOptions.set("textLayerMode", _ui_utils.TextLayerMode.DISABLE);
            break;
          case "visible":
          case "shadow":
          case "hover":
            viewerContainer.classList.add(`textLayer-${params.get("textlayer")}`);
            try {
              await loadPDFBug(this);
              this._PDFBug.loadCSS();
            } catch (ex) {
              console.error(`_parseHashParams: "${ex.message}".`);
            }
            break;
        }
      }
      if (params.has("pdfbug")) {
        _app_options.AppOptions.set("pdfBug", true);
        _app_options.AppOptions.set("fontExtraProperties", true);
        const enabled = params.get("pdfbug").split(",");
        try {
          await loadPDFBug(this);
          this._PDFBug.init(mainContainer, enabled);
        } catch (ex) {
          console.error(`_parseHashParams: "${ex.message}".`);
        }
      }
      if (params.has("locale")) {
        _app_options.AppOptions.set("locale", params.get("locale"));
      }
    },
    async _initializeL10n() {
      this.l10n = this.externalServices.createL10n({
        locale: _app_options.AppOptions.get("locale")
      });
      const dir = await this.l10n.getDirection();
      document.getElementsByTagName("html")[0].dir = dir;
    },
    _forceCssTheme() {
      const cssTheme = _app_options.AppOptions.get("viewerCssTheme");
      if (cssTheme === ViewerCssTheme.AUTOMATIC || !Object.values(ViewerCssTheme).includes(cssTheme)) {
        return;
      }
      try {
        const styleSheet = document.styleSheets[0];
        const cssRules = (styleSheet === null || styleSheet === void 0 ? void 0 : styleSheet.cssRules) || [];
        for (let i = 0, ii = cssRules.length; i < ii; i++) {
          var _rule$media;
          const rule = cssRules[i];
          if (rule instanceof CSSMediaRule && ((_rule$media = rule.media) === null || _rule$media === void 0 ? void 0 : _rule$media[0]) === "(prefers-color-scheme: dark)") {
            if (cssTheme === ViewerCssTheme.LIGHT) {
              styleSheet.deleteRule(i);
              return;
            }
            const darkRules = /^@media \(prefers-color-scheme: dark\) {\n\s*([\w\s-.,:;/\\{}()]+)\n}$/.exec(rule.cssText);
            if (darkRules !== null && darkRules !== void 0 && darkRules[1]) {
              styleSheet.deleteRule(i);
              styleSheet.insertRule(darkRules[1], i);
            }
            return;
          }
        }
      } catch (reason) {
        console.error(`_forceCssTheme: "${reason === null || reason === void 0 ? void 0 : reason.message}".`);
      }
    },
    async _initializeViewerComponents() {
      var _appConfig$sidebar, _appConfig$secondaryT, _appConfig$secondaryT2, _appConfig$sidebar2, _appConfig$sidebar3, _appConfig$sidebar4;
      const {
        appConfig,
        externalServices,
        l10n
      } = this;
      const eventBus = externalServices.isInAutomation ? new _event_utils.AutomationEventBus() : new _event_utils.EventBus();
      this.eventBus = eventBus;
      this.overlayManager = new _overlay_manager.OverlayManager();
      const pdfRenderingQueue = new _pdf_rendering_queue.PDFRenderingQueue();
      pdfRenderingQueue.onIdle = this._cleanup.bind(this);
      this.pdfRenderingQueue = pdfRenderingQueue;
      const pdfLinkService = new _pdf_link_service.PDFLinkService({
        eventBus,
        externalLinkTarget: _app_options.AppOptions.get("externalLinkTarget"),
        externalLinkRel: _app_options.AppOptions.get("externalLinkRel"),
        ignoreDestinationZoom: _app_options.AppOptions.get("ignoreDestinationZoom")
      });
      this.pdfLinkService = pdfLinkService;
      const downloadManager = externalServices.createDownloadManager();
      this.downloadManager = downloadManager;
      const findController = new _pdf_find_controller.PDFFindController({
        linkService: pdfLinkService,
        eventBus,
        updateMatchesCountOnProgress: true
      });
      this.findController = findController;
      const pdfScriptingManager = new _pdf_scripting_manager.PDFScriptingManager({
        eventBus,
        sandboxBundleSrc: _app_options.AppOptions.get("sandboxBundleSrc"),
        externalServices,
        docProperties: this._scriptingDocProperties.bind(this)
      });
      this.pdfScriptingManager = pdfScriptingManager;
      const container = appConfig.mainContainer,
        viewer = appConfig.viewerContainer;
      const annotationEditorMode = _app_options.AppOptions.get("annotationEditorMode");
      const isOffscreenCanvasSupported = _app_options.AppOptions.get("isOffscreenCanvasSupported") && _pdfjsLib.FeatureTest.isOffscreenCanvasSupported;
      const pageColors = _app_options.AppOptions.get("forcePageColors") || window.matchMedia("(forced-colors: active)").matches ? {
        background: _app_options.AppOptions.get("pageColorsBackground"),
        foreground: _app_options.AppOptions.get("pageColorsForeground")
      } : null;
      const altTextManager = appConfig.altTextDialog ? new _webAlt_text_manager.AltTextManager(appConfig.altTextDialog, container, this.overlayManager, eventBus) : null;
      const pdfViewer = new _pdf_viewer.PDFViewer({
        container,
        viewer,
        eventBus,
        renderingQueue: pdfRenderingQueue,
        linkService: pdfLinkService,
        downloadManager,
        altTextManager,
        findController,
        scriptingManager: _app_options.AppOptions.get("enableScripting") && pdfScriptingManager,
        l10n,
        textLayerMode: _app_options.AppOptions.get("textLayerMode"),
        annotationMode: _app_options.AppOptions.get("annotationMode"),
        annotationEditorMode,
        imageResourcesPath: _app_options.AppOptions.get("imageResourcesPath"),
        enablePrintAutoRotate: _app_options.AppOptions.get("enablePrintAutoRotate"),
        isOffscreenCanvasSupported,
        maxCanvasPixels: _app_options.AppOptions.get("maxCanvasPixels"),
        enablePermissions: _app_options.AppOptions.get("enablePermissions"),
        pageColors
      });
      this.pdfViewer = pdfViewer;
      pdfRenderingQueue.setViewer(pdfViewer);
      pdfLinkService.setViewer(pdfViewer);
      pdfScriptingManager.setViewer(pdfViewer);
      if ((_appConfig$sidebar = appConfig.sidebar) !== null && _appConfig$sidebar !== void 0 && _appConfig$sidebar.thumbnailView) {
        this.pdfThumbnailViewer = new _webPdf_thumbnail_viewer.PDFThumbnailViewer({
          container: appConfig.sidebar.thumbnailView,
          eventBus,
          renderingQueue: pdfRenderingQueue,
          linkService: pdfLinkService,
          l10n,
          pageColors
        });
        pdfRenderingQueue.setThumbnailViewer(this.pdfThumbnailViewer);
      }
      if (!this.isViewerEmbedded && !_app_options.AppOptions.get("disableHistory")) {
        this.pdfHistory = new _pdf_history.PDFHistory({
          linkService: pdfLinkService,
          eventBus
        });
        pdfLinkService.setHistory(this.pdfHistory);
      }
      if (!this.supportsIntegratedFind && appConfig.findBar) {
        this.findBar = new _webPdf_find_bar.PDFFindBar(appConfig.findBar, eventBus, l10n);
      }
      if (appConfig.annotationEditorParams) {
        if (annotationEditorMode !== _pdfjsLib.AnnotationEditorType.DISABLE) {
          if (_app_options.AppOptions.get("enableStampEditor") && isOffscreenCanvasSupported) {
            var _appConfig$toolbar;
            (_appConfig$toolbar = appConfig.toolbar) === null || _appConfig$toolbar === void 0 || (_appConfig$toolbar = _appConfig$toolbar.editorStampButton) === null || _appConfig$toolbar === void 0 || _appConfig$toolbar.classList.remove("hidden");
          }
          this.annotationEditorParams = new _webAnnotation_editor_params.AnnotationEditorParams(appConfig.annotationEditorParams, eventBus);
        } else {
          for (const id of ["editorModeButtons", "editorModeSeparator"]) {
            var _document$getElementB;
            (_document$getElementB = document.getElementById(id)) === null || _document$getElementB === void 0 || _document$getElementB.classList.add("hidden");
          }
        }
      }
      if (appConfig.documentProperties) {
        this.pdfDocumentProperties = new _webPdf_document_properties.PDFDocumentProperties(appConfig.documentProperties, this.overlayManager, eventBus, l10n, () => this._docFilename);
      }
      if ((_appConfig$secondaryT = appConfig.secondaryToolbar) !== null && _appConfig$secondaryT !== void 0 && _appConfig$secondaryT.cursorHandToolButton) {
        this.pdfCursorTools = new _webPdf_cursor_tools.PDFCursorTools({
          container,
          eventBus,
          cursorToolOnLoad: _app_options.AppOptions.get("cursorToolOnLoad")
        });
      }
      if (appConfig.toolbar) {
        this.toolbar = new _webToolbar.Toolbar(appConfig.toolbar, eventBus, l10n);
      }
      if (appConfig.secondaryToolbar) {
        this.secondaryToolbar = new _webSecondary_toolbar.SecondaryToolbar(appConfig.secondaryToolbar, eventBus);
      }
      if (this.supportsFullscreen && (_appConfig$secondaryT2 = appConfig.secondaryToolbar) !== null && _appConfig$secondaryT2 !== void 0 && _appConfig$secondaryT2.presentationModeButton) {
        this.pdfPresentationMode = new _webPdf_presentation_mode.PDFPresentationMode({
          container,
          pdfViewer,
          eventBus
        });
      }
      if (appConfig.passwordOverlay) {
        this.passwordPrompt = new _password_prompt.PasswordPrompt(appConfig.passwordOverlay, this.overlayManager, l10n, this.isViewerEmbedded);
      }
      if ((_appConfig$sidebar2 = appConfig.sidebar) !== null && _appConfig$sidebar2 !== void 0 && _appConfig$sidebar2.outlineView) {
        this.pdfOutlineViewer = new _webPdf_outline_viewer.PDFOutlineViewer({
          container: appConfig.sidebar.outlineView,
          eventBus,
          linkService: pdfLinkService,
          downloadManager
        });
      }
      if ((_appConfig$sidebar3 = appConfig.sidebar) !== null && _appConfig$sidebar3 !== void 0 && _appConfig$sidebar3.attachmentsView) {
        this.pdfAttachmentViewer = new _webPdf_attachment_viewer.PDFAttachmentViewer({
          container: appConfig.sidebar.attachmentsView,
          eventBus,
          downloadManager
        });
      }
      if ((_appConfig$sidebar4 = appConfig.sidebar) !== null && _appConfig$sidebar4 !== void 0 && _appConfig$sidebar4.layersView) {
        this.pdfLayerViewer = new _webPdf_layer_viewer.PDFLayerViewer({
          container: appConfig.sidebar.layersView,
          eventBus,
          l10n
        });
      }
      if (appConfig.sidebar) {
        this.pdfSidebar = new _webPdf_sidebar.PDFSidebar({
          elements: appConfig.sidebar,
          eventBus,
          l10n
        });
        this.pdfSidebar.onToggled = this.forceRendering.bind(this);
        this.pdfSidebar.onUpdateThumbnails = () => {
          for (const pageView of pdfViewer.getCachedPageViews()) {
            if (pageView.renderingState === _ui_utils.RenderingStates.FINISHED) {
              var _this$pdfThumbnailVie;
              (_this$pdfThumbnailVie = this.pdfThumbnailViewer.getThumbnail(pageView.id - 1)) === null || _this$pdfThumbnailVie === void 0 || _this$pdfThumbnailVie.setImage(pageView);
            }
          }
          this.pdfThumbnailViewer.scrollThumbnailIntoView(pdfViewer.currentPageNumber);
        };
      }
    },
    async run(config) {
      var _params$get;
      await this.initialize(config);
      const {
        appConfig,
        eventBus
      } = this;
      let file;
      const queryString = document.location.search.substring(1);
      const params = (0, _ui_utils.parseQueryString)(queryString);
      file = (_params$get = params.get("file")) !== null && _params$get !== void 0 ? _params$get : _app_options.AppOptions.get("defaultUrl");
      validateFileURL(file);
      const fileInput = appConfig.openFileInput;
      fileInput.value = null;
      fileInput.addEventListener("change", function (evt) {
        const {
          files
        } = evt.target;
        if (!files || files.length === 0) {
          return;
        }
        eventBus.dispatch("fileinputchange", {
          source: this,
          fileInput: evt.target
        });
      });
      appConfig.mainContainer.addEventListener("dragover", function (evt) {
        evt.preventDefault();
        evt.dataTransfer.dropEffect = evt.dataTransfer.effectAllowed === "copy" ? "copy" : "move";
      });
      appConfig.mainContainer.addEventListener("drop", function (evt) {
        evt.preventDefault();
        const {
          files
        } = evt.dataTransfer;
        if (!files || files.length === 0) {
          return;
        }
        eventBus.dispatch("fileinputchange", {
          source: this,
          fileInput: evt.dataTransfer
        });
      });
      if (!this.supportsDocumentFonts) {
        _app_options.AppOptions.set("disableFontFace", true);
        this.l10n.get("web_fonts_disabled").then(msg => {
          console.warn(msg);
        });
      }
      if (!this.supportsPrinting) {
        var _appConfig$toolbar2, _appConfig$secondaryT3;
        (_appConfig$toolbar2 = appConfig.toolbar) === null || _appConfig$toolbar2 === void 0 || (_appConfig$toolbar2 = _appConfig$toolbar2.print) === null || _appConfig$toolbar2 === void 0 || _appConfig$toolbar2.classList.add("hidden");
        (_appConfig$secondaryT3 = appConfig.secondaryToolbar) === null || _appConfig$secondaryT3 === void 0 || _appConfig$secondaryT3.printButton.classList.add("hidden");
      }
      if (!this.supportsFullscreen) {
        var _appConfig$secondaryT4;
        (_appConfig$secondaryT4 = appConfig.secondaryToolbar) === null || _appConfig$secondaryT4 === void 0 || _appConfig$secondaryT4.presentationModeButton.classList.add("hidden");
      }
      if (this.supportsIntegratedFind) {
        var _appConfig$toolbar3;
        (_appConfig$toolbar3 = appConfig.toolbar) === null || _appConfig$toolbar3 === void 0 || (_appConfig$toolbar3 = _appConfig$toolbar3.viewFind) === null || _appConfig$toolbar3 === void 0 || _appConfig$toolbar3.classList.add("hidden");
      }
      appConfig.mainContainer.addEventListener("transitionend", function (evt) {
        if (evt.target === this) {
          eventBus.dispatch("resize", {
            source: this
          });
        }
      }, true);
      if (file) {
        this.open({
          url: file
        });
      } else {
        this._hideViewBookmark();
      }
    },
    get initialized() {
      return this._initializedCapability.settled;
    },
    get initializedPromise() {
      return this._initializedCapability.promise;
    },
    zoomIn(steps, scaleFactor) {
      if (this.pdfViewer.isInPresentationMode) {
        return;
      }
      this.pdfViewer.increaseScale({
        drawingDelay: _app_options.AppOptions.get("defaultZoomDelay"),
        steps,
        scaleFactor
      });
    },
    zoomOut(steps, scaleFactor) {
      if (this.pdfViewer.isInPresentationMode) {
        return;
      }
      this.pdfViewer.decreaseScale({
        drawingDelay: _app_options.AppOptions.get("defaultZoomDelay"),
        steps,
        scaleFactor
      });
    },
    zoomReset() {
      if (this.pdfViewer.isInPresentationMode) {
        return;
      }
      this.pdfViewer.currentScaleValue = _ui_utils.DEFAULT_SCALE_VALUE;
    },
    get pagesCount() {
      return this.pdfDocument ? this.pdfDocument.numPages : 0;
    },
    get page() {
      return this.pdfViewer.currentPageNumber;
    },
    set page(val) {
      this.pdfViewer.currentPageNumber = val;
    },
    get supportsPrinting() {
      return PDFPrintServiceFactory.instance.supportsPrinting;
    },
    get supportsFullscreen() {
      return (0, _pdfjsLib.shadow)(this, "supportsFullscreen", document.fullscreenEnabled);
    },
    get supportsPinchToZoom() {
      return this.externalServices.supportsPinchToZoom;
    },
    get supportsIntegratedFind() {
      return this.externalServices.supportsIntegratedFind;
    },
    get supportsDocumentFonts() {
      return this.externalServices.supportsDocumentFonts;
    },
    get loadingBar() {
      const barElement = document.getElementById("loadingBar");
      const bar = barElement ? new _ui_utils.ProgressBar(barElement) : null;
      return (0, _pdfjsLib.shadow)(this, "loadingBar", bar);
    },
    get supportedMouseWheelZoomModifierKeys() {
      return this.externalServices.supportedMouseWheelZoomModifierKeys;
    },
    initPassiveLoading(file) {
      throw new Error("Not implemented: initPassiveLoading");
    },
    setTitleUsingUrl() {
      let url = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : "";
      let downloadUrl = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      this.url = url;
      this.baseUrl = url.split("#")[0];
      if (downloadUrl) {
        this._downloadUrl = downloadUrl === url ? this.baseUrl : downloadUrl.split("#")[0];
      }
      if ((0, _pdfjsLib.isDataScheme)(url)) {
        this._hideViewBookmark();
      }
      let title = (0, _pdfjsLib.getPdfFilenameFromUrl)(url, "");
      if (!title) {
        try {
          title = decodeURIComponent((0, _pdfjsLib.getFilenameFromUrl)(url)) || url;
        } catch {
          title = url;
        }
      }
      this.setTitle(title);
    },
    setTitle() {
      let title = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : this._title;
      this._title = title;
      if (this.isViewerEmbedded) {
        return;
      }
      const editorIndicator = this._hasAnnotationEditors && !this.pdfRenderingQueue.printing;
      document.title = `${editorIndicator ? "* " : ""}${title}`;
    },
    get _docFilename() {
      return this._contentDispositionFilename || (0, _pdfjsLib.getPdfFilenameFromUrl)(this.url);
    },
    _hideViewBookmark() {
      const {
        secondaryToolbar
      } = this.appConfig;
      secondaryToolbar === null || secondaryToolbar === void 0 || secondaryToolbar.viewBookmarkButton.classList.add("hidden");
      if (secondaryToolbar !== null && secondaryToolbar !== void 0 && secondaryToolbar.presentationModeButton.classList.contains("hidden")) {
        var _document$getElementB2;
        (_document$getElementB2 = document.getElementById("viewBookmarkSeparator")) === null || _document$getElementB2 === void 0 || _document$getElementB2.classList.add("hidden");
      }
    },
    async close() {
      var _this$pdfDocument, _this$pdfSidebar, _this$pdfOutlineViewe, _this$pdfAttachmentVi, _this$pdfLayerViewer, _this$pdfHistory, _this$findBar, _this$toolbar, _this$secondaryToolba, _this$_PDFBug;
      this._unblockDocumentLoadEvent();
      this._hideViewBookmark();
      if (!this.pdfLoadingTask) {
        return;
      }
      if (((_this$pdfDocument = this.pdfDocument) === null || _this$pdfDocument === void 0 ? void 0 : _this$pdfDocument.annotationStorage.size) > 0 && this._annotationStorageModified) {
        try {
          await this.save();
        } catch {}
      }
      const promises = [];
      promises.push(this.pdfLoadingTask.destroy());
      this.pdfLoadingTask = null;
      if (this.pdfDocument) {
        var _this$pdfThumbnailVie2, _this$pdfDocumentProp;
        this.pdfDocument = null;
        (_this$pdfThumbnailVie2 = this.pdfThumbnailViewer) === null || _this$pdfThumbnailVie2 === void 0 || _this$pdfThumbnailVie2.setDocument(null);
        this.pdfViewer.setDocument(null);
        this.pdfLinkService.setDocument(null);
        (_this$pdfDocumentProp = this.pdfDocumentProperties) === null || _this$pdfDocumentProp === void 0 || _this$pdfDocumentProp.setDocument(null);
      }
      this.pdfLinkService.externalLinkEnabled = true;
      this.store = null;
      this.isInitialViewSet = false;
      this.downloadComplete = false;
      this.url = "";
      this.baseUrl = "";
      this._downloadUrl = "";
      this.documentInfo = null;
      this.metadata = null;
      this._contentDispositionFilename = null;
      this._contentLength = null;
      this._saveInProgress = false;
      this._hasAnnotationEditors = false;
      promises.push(this.pdfScriptingManager.destroyPromise, this.passwordPrompt.close());
      this.setTitle();
      (_this$pdfSidebar = this.pdfSidebar) === null || _this$pdfSidebar === void 0 || _this$pdfSidebar.reset();
      (_this$pdfOutlineViewe = this.pdfOutlineViewer) === null || _this$pdfOutlineViewe === void 0 || _this$pdfOutlineViewe.reset();
      (_this$pdfAttachmentVi = this.pdfAttachmentViewer) === null || _this$pdfAttachmentVi === void 0 || _this$pdfAttachmentVi.reset();
      (_this$pdfLayerViewer = this.pdfLayerViewer) === null || _this$pdfLayerViewer === void 0 || _this$pdfLayerViewer.reset();
      (_this$pdfHistory = this.pdfHistory) === null || _this$pdfHistory === void 0 || _this$pdfHistory.reset();
      (_this$findBar = this.findBar) === null || _this$findBar === void 0 || _this$findBar.reset();
      (_this$toolbar = this.toolbar) === null || _this$toolbar === void 0 || _this$toolbar.reset();
      (_this$secondaryToolba = this.secondaryToolbar) === null || _this$secondaryToolba === void 0 || _this$secondaryToolba.reset();
      (_this$_PDFBug = this._PDFBug) === null || _this$_PDFBug === void 0 || _this$_PDFBug.cleanup();
      await Promise.all(promises);
    },
    async open(args) {
      var _args;
      let deprecatedArgs = false;
      if (typeof args === "string") {
        args = {
          url: args
        };
        deprecatedArgs = true;
      } else if ((_args = args) !== null && _args !== void 0 && _args.byteLength) {
        args = {
          data: args
        };
        deprecatedArgs = true;
      }
      if (deprecatedArgs) {
        console.error("The `PDFViewerApplication.open` signature was updated, please use an object instead.");
      }
      if (this.pdfLoadingTask) {
        await this.close();
      }
      const workerParams = _app_options.AppOptions.getAll(_app_options.OptionKind.WORKER);
      Object.assign(_pdfjsLib.GlobalWorkerOptions, workerParams);
      if (args.url) {
        this.setTitleUsingUrl(args.originalUrl || args.url, args.url);
      }
      const apiParams = _app_options.AppOptions.getAll(_app_options.OptionKind.API);
      const params = {
        canvasMaxAreaInBytes: this.externalServices.canvasMaxAreaInBytes,
        ...apiParams,
        ...args
      };
      const loadingTask = (0, _pdfjsLib.getDocument)(params);
      this.pdfLoadingTask = loadingTask;
      loadingTask.onPassword = (updateCallback, reason) => {
        if (this.isViewerEmbedded) {
          this._unblockDocumentLoadEvent();
        }
        this.pdfLinkService.externalLinkEnabled = false;
        this.passwordPrompt.setUpdateCallback(updateCallback, reason);
        this.passwordPrompt.open();
      };
      loadingTask.onProgress = _ref => {
        let {
          loaded,
          total
        } = _ref;
        this.progress(loaded / total);
      };
      return loadingTask.promise.then(pdfDocument => {
        this.load(pdfDocument);
      }, reason => {
        if (loadingTask !== this.pdfLoadingTask) {
          return undefined;
        }
        let key = "loading_error";
        if (reason instanceof _pdfjsLib.InvalidPDFException) {
          key = "invalid_file_error";
        } else if (reason instanceof _pdfjsLib.MissingPDFException) {
          key = "missing_file_error";
        } else if (reason instanceof _pdfjsLib.UnexpectedResponseException) {
          key = "unexpected_response_error";
        }
        return this.l10n.get(key).then(msg => {
          this._documentError(msg, {
            message: reason === null || reason === void 0 ? void 0 : reason.message
          });
          throw reason;
        });
      });
    },
    _ensureDownloadComplete() {
      if (this.pdfDocument && this.downloadComplete) {
        return;
      }
      throw new Error("PDF document not downloaded.");
    },
    async download() {
      let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      const url = this._downloadUrl,
        filename = this._docFilename;
      try {
        this._ensureDownloadComplete();
        const data = await this.pdfDocument.getData();
        const blob = new Blob([data], {
          type: "application/pdf"
        });
        await this.downloadManager.download(blob, url, filename, options);
      } catch {
        await this.downloadManager.downloadUrl(url, filename, options);
      }
    },
    async save() {
      let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (this._saveInProgress) {
        return;
      }
      this._saveInProgress = true;
      await this.pdfScriptingManager.dispatchWillSave();
      const url = this._downloadUrl,
        filename = this._docFilename;
      try {
        this._ensureDownloadComplete();
        const data = await this.pdfDocument.saveDocument();
        const blob = new Blob([data], {
          type: "application/pdf"
        });
        await this.downloadManager.download(blob, url, filename, options);
      } catch (reason) {
        console.error(`Error when saving the document: ${reason.message}`);
        await this.download(options);
      } finally {
        await this.pdfScriptingManager.dispatchDidSave();
        this._saveInProgress = false;
      }
      if (this._hasAnnotationEditors) {
        this.externalServices.reportTelemetry({
          type: "editing",
          data: {
            type: "save"
          }
        });
      }
    },
    downloadOrSave() {
      var _this$pdfDocument2;
      let options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (((_this$pdfDocument2 = this.pdfDocument) === null || _this$pdfDocument2 === void 0 ? void 0 : _this$pdfDocument2.annotationStorage.size) > 0) {
        this.save(options);
      } else {
        this.download(options);
      }
    },
    openInExternalApp() {
      this.downloadOrSave({
        openInExternalApp: true
      });
    },
    _documentError(message) {
      var _moreInfo$message;
      let moreInfo = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      this._unblockDocumentLoadEvent();
      this._otherError(message, moreInfo);
      this.eventBus.dispatch("documenterror", {
        source: this,
        message,
        reason: (_moreInfo$message = moreInfo === null || moreInfo === void 0 ? void 0 : moreInfo.message) !== null && _moreInfo$message !== void 0 ? _moreInfo$message : null
      });
    },
    _otherError(message) {
      let moreInfo = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      const moreInfoText = [`PDF.js v${_pdfjsLib.version || "?"} (build: ${_pdfjsLib.build || "?"})`];
      if (moreInfo) {
        moreInfoText.push(`Message: ${moreInfo.message}`);
        if (moreInfo.stack) {
          moreInfoText.push(`Stack: ${moreInfo.stack}`);
        } else {
          if (moreInfo.filename) {
            moreInfoText.push(`File: ${moreInfo.filename}`);
          }
          if (moreInfo.lineNumber) {
            moreInfoText.push(`Line: ${moreInfo.lineNumber}`);
          }
        }
      }
      console.error(`${message}\n\n${moreInfoText.join("\n")}`);
    },
    progress(level) {
      var _this$pdfDocument$loa, _this$pdfDocument3;
      if (!this.loadingBar || this.downloadComplete) {
        return;
      }
      const percent = Math.round(level * 100);
      if (percent <= this.loadingBar.percent) {
        return;
      }
      this.loadingBar.percent = percent;
      if ((_this$pdfDocument$loa = (_this$pdfDocument3 = this.pdfDocument) === null || _this$pdfDocument3 === void 0 ? void 0 : _this$pdfDocument3.loadingParams.disableAutoFetch) !== null && _this$pdfDocument$loa !== void 0 ? _this$pdfDocument$loa : _app_options.AppOptions.get("disableAutoFetch")) {
        this.loadingBar.setDisableAutoFetch();
      }
    },
    load(pdfDocument) {
      var _this$toolbar2, _this$secondaryToolba2, _this$pdfDocumentProp2, _this$pdfThumbnailVie3;
      this.pdfDocument = pdfDocument;
      pdfDocument.getDownloadInfo().then(_ref2 => {
        var _this$loadingBar;
        let {
          length
        } = _ref2;
        this._contentLength = length;
        this.downloadComplete = true;
        (_this$loadingBar = this.loadingBar) === null || _this$loadingBar === void 0 || _this$loadingBar.hide();
        firstPagePromise.then(() => {
          this.eventBus.dispatch("documentloaded", {
            source: this
          });
        });
      });
      const pageLayoutPromise = pdfDocument.getPageLayout().catch(() => {});
      const pageModePromise = pdfDocument.getPageMode().catch(() => {});
      const openActionPromise = pdfDocument.getOpenAction().catch(() => {});
      (_this$toolbar2 = this.toolbar) === null || _this$toolbar2 === void 0 || _this$toolbar2.setPagesCount(pdfDocument.numPages, false);
      (_this$secondaryToolba2 = this.secondaryToolbar) === null || _this$secondaryToolba2 === void 0 || _this$secondaryToolba2.setPagesCount(pdfDocument.numPages);
      this.pdfLinkService.setDocument(pdfDocument);
      (_this$pdfDocumentProp2 = this.pdfDocumentProperties) === null || _this$pdfDocumentProp2 === void 0 || _this$pdfDocumentProp2.setDocument(pdfDocument);
      const pdfViewer = this.pdfViewer;
      pdfViewer.setDocument(pdfDocument);
      const {
        firstPagePromise,
        onePageRendered,
        pagesPromise
      } = pdfViewer;
      (_this$pdfThumbnailVie3 = this.pdfThumbnailViewer) === null || _this$pdfThumbnailVie3 === void 0 || _this$pdfThumbnailVie3.setDocument(pdfDocument);
      const storedPromise = (this.store = new _view_history.ViewHistory(pdfDocument.fingerprints[0])).getMultiple({
        page: null,
        zoom: _ui_utils.DEFAULT_SCALE_VALUE,
        scrollLeft: "0",
        scrollTop: "0",
        rotation: null,
        sidebarView: _ui_utils.SidebarView.UNKNOWN,
        scrollMode: _ui_utils.ScrollMode.UNKNOWN,
        spreadMode: _ui_utils.SpreadMode.UNKNOWN
      }).catch(() => {});
      firstPagePromise.then(pdfPage => {
        var _this$loadingBar2;
        (_this$loadingBar2 = this.loadingBar) === null || _this$loadingBar2 === void 0 || _this$loadingBar2.setWidth(this.appConfig.viewerContainer);
        this._initializeAnnotationStorageCallbacks(pdfDocument);
        Promise.all([_ui_utils.animationStarted, storedPromise, pageLayoutPromise, pageModePromise, openActionPromise]).then(async _ref3 => {
          let [timeStamp, stored, pageLayout, pageMode, openAction] = _ref3;
          const viewOnLoad = _app_options.AppOptions.get("viewOnLoad");
          this._initializePdfHistory({
            fingerprint: pdfDocument.fingerprints[0],
            viewOnLoad,
            initialDest: openAction === null || openAction === void 0 ? void 0 : openAction.dest
          });
          const initialBookmark = this.initialBookmark;
          const zoom = _app_options.AppOptions.get("defaultZoomValue");
          let hash = zoom ? `zoom=${zoom}` : null;
          let rotation = null;
          let sidebarView = _app_options.AppOptions.get("sidebarViewOnLoad");
          let scrollMode = _app_options.AppOptions.get("scrollModeOnLoad");
          let spreadMode = _app_options.AppOptions.get("spreadModeOnLoad");
          if (stored !== null && stored !== void 0 && stored.page && viewOnLoad !== ViewOnLoad.INITIAL) {
            hash = `page=${stored.page}&zoom=${zoom || stored.zoom},` + `${stored.scrollLeft},${stored.scrollTop}`;
            rotation = parseInt(stored.rotation, 10);
            if (sidebarView === _ui_utils.SidebarView.UNKNOWN) {
              sidebarView = stored.sidebarView | 0;
            }
            if (scrollMode === _ui_utils.ScrollMode.UNKNOWN) {
              scrollMode = stored.scrollMode | 0;
            }
            if (spreadMode === _ui_utils.SpreadMode.UNKNOWN) {
              spreadMode = stored.spreadMode | 0;
            }
          }
          if (pageMode && sidebarView === _ui_utils.SidebarView.UNKNOWN) {
            sidebarView = (0, _ui_utils.apiPageModeToSidebarView)(pageMode);
          }
          if (pageLayout && scrollMode === _ui_utils.ScrollMode.UNKNOWN && spreadMode === _ui_utils.SpreadMode.UNKNOWN) {
            const modes = (0, _ui_utils.apiPageLayoutToViewerModes)(pageLayout);
            spreadMode = modes.spreadMode;
          }
          this.setInitialView(hash, {
            rotation,
            sidebarView,
            scrollMode,
            spreadMode
          });
          this.eventBus.dispatch("documentinit", {
            source: this
          });
          if (!this.isViewerEmbedded) {
            pdfViewer.focus();
          }
          await Promise.race([pagesPromise, new Promise(resolve => {
            setTimeout(resolve, FORCE_PAGES_LOADED_TIMEOUT);
          })]);
          if (!initialBookmark && !hash) {
            return;
          }
          if (pdfViewer.hasEqualPageSizes) {
            return;
          }
          this.initialBookmark = initialBookmark;
          pdfViewer.currentScaleValue = pdfViewer.currentScaleValue;
          this.setInitialView(hash);
        }).catch(() => {
          this.setInitialView();
        }).then(function () {
          pdfViewer.update();
        });
      });
      pagesPromise.then(() => {
        this._unblockDocumentLoadEvent();
        this._initializeAutoPrint(pdfDocument, openActionPromise);
      }, reason => {
        this.l10n.get("loading_error").then(msg => {
          this._documentError(msg, {
            message: reason === null || reason === void 0 ? void 0 : reason.message
          });
        });
      });
      onePageRendered.then(data => {
        this.externalServices.reportTelemetry({
          type: "pageInfo",
          timestamp: data.timestamp
        });
        if (this.pdfOutlineViewer) {
          pdfDocument.getOutline().then(outline => {
            if (pdfDocument !== this.pdfDocument) {
              return;
            }
            this.pdfOutlineViewer.render({
              outline,
              pdfDocument
            });
          });
        }
        if (this.pdfAttachmentViewer) {
          pdfDocument.getAttachments().then(attachments => {
            if (pdfDocument !== this.pdfDocument) {
              return;
            }
            this.pdfAttachmentViewer.render({
              attachments
            });
          });
        }
        if (this.pdfLayerViewer) {
          pdfViewer.optionalContentConfigPromise.then(optionalContentConfig => {
            if (pdfDocument !== this.pdfDocument) {
              return;
            }
            this.pdfLayerViewer.render({
              optionalContentConfig,
              pdfDocument
            });
          });
        }
      });
      this._initializePageLabels(pdfDocument);
      this._initializeMetadata(pdfDocument);
    },
    async _scriptingDocProperties(pdfDocument) {
      var _this$metadata, _this$metadata2;
      if (!this.documentInfo) {
        await new Promise(resolve => {
          this.eventBus._on("metadataloaded", resolve, {
            once: true
          });
        });
        if (pdfDocument !== this.pdfDocument) {
          return null;
        }
      }
      if (!this._contentLength) {
        await new Promise(resolve => {
          this.eventBus._on("documentloaded", resolve, {
            once: true
          });
        });
        if (pdfDocument !== this.pdfDocument) {
          return null;
        }
      }
      return {
        ...this.documentInfo,
        baseURL: this.baseUrl,
        filesize: this._contentLength,
        filename: this._docFilename,
        metadata: (_this$metadata = this.metadata) === null || _this$metadata === void 0 ? void 0 : _this$metadata.getRaw(),
        authors: (_this$metadata2 = this.metadata) === null || _this$metadata2 === void 0 ? void 0 : _this$metadata2.get("dc:creator"),
        numPages: this.pagesCount,
        URL: this.url
      };
    },
    async _initializeAutoPrint(pdfDocument, openActionPromise) {
      const [openAction, jsActions] = await Promise.all([openActionPromise, this.pdfViewer.enableScripting ? null : pdfDocument.getJSActions()]);
      if (pdfDocument !== this.pdfDocument) {
        return;
      }
      let triggerAutoPrint = (openAction === null || openAction === void 0 ? void 0 : openAction.action) === "Print";
      if (jsActions) {
        console.warn("Warning: JavaScript support is not enabled");
        for (const name in jsActions) {
          if (triggerAutoPrint) {
            break;
          }
          switch (name) {
            case "WillClose":
            case "WillSave":
            case "DidSave":
            case "WillPrint":
            case "DidPrint":
              continue;
          }
          triggerAutoPrint = jsActions[name].some(js => _ui_utils.AutoPrintRegExp.test(js));
        }
      }
      if (triggerAutoPrint) {
        this.triggerPrinting();
      }
    },
    async _initializeMetadata(pdfDocument) {
      var _this$_contentDisposi, _this$_contentLength;
      const {
        info,
        metadata,
        contentDispositionFilename,
        contentLength
      } = await pdfDocument.getMetadata();
      if (pdfDocument !== this.pdfDocument) {
        return;
      }
      this.documentInfo = info;
      this.metadata = metadata;
      (_this$_contentDisposi = this._contentDispositionFilename) !== null && _this$_contentDisposi !== void 0 ? _this$_contentDisposi : this._contentDispositionFilename = contentDispositionFilename;
      (_this$_contentLength = this._contentLength) !== null && _this$_contentLength !== void 0 ? _this$_contentLength : this._contentLength = contentLength;
      console.log(`PDF ${pdfDocument.fingerprints[0]} [${info.PDFFormatVersion} ` + `${(info.Producer || "-").trim()} / ${(info.Creator || "-").trim()}] ` + `(PDF.js: ${_pdfjsLib.version || "?"} [${_pdfjsLib.build || "?"}])`);
      let pdfTitle = info.Title;
      const metadataTitle = metadata === null || metadata === void 0 ? void 0 : metadata.get("dc:title");
      if (metadataTitle) {
        if (metadataTitle !== "Untitled" && !/[\uFFF0-\uFFFF]/g.test(metadataTitle)) {
          pdfTitle = metadataTitle;
        }
      }
      if (pdfTitle) {
        this.setTitle(`${pdfTitle} - ${this._contentDispositionFilename || this._title}`);
      } else if (this._contentDispositionFilename) {
        this.setTitle(this._contentDispositionFilename);
      }
      if (info.IsXFAPresent && !info.IsAcroFormPresent && !pdfDocument.isPureXfa) {
        if (pdfDocument.loadingParams.enableXfa) {
          console.warn("Warning: XFA Foreground documents are not supported");
        } else {
          console.warn("Warning: XFA support is not enabled");
        }
      } else if ((info.IsAcroFormPresent || info.IsXFAPresent) && !this.pdfViewer.renderForms) {
        console.warn("Warning: Interactive form support is not enabled");
      }
      if (info.IsSignaturesPresent) {
        console.warn("Warning: Digital signatures validation is not supported");
      }
      this.eventBus.dispatch("metadataloaded", {
        source: this
      });
    },
    async _initializePageLabels(pdfDocument) {
      const labels = await pdfDocument.getPageLabels();
      if (pdfDocument !== this.pdfDocument) {
        return;
      }
      if (!labels || _app_options.AppOptions.get("disablePageLabels")) {
        return;
      }
      const numLabels = labels.length;
      let standardLabels = 0,
        emptyLabels = 0;
      for (let i = 0; i < numLabels; i++) {
        const label = labels[i];
        if (label === (i + 1).toString()) {
          standardLabels++;
        } else if (label === "") {
          emptyLabels++;
        } else {
          break;
        }
      }
      if (standardLabels >= numLabels || emptyLabels >= numLabels) {
        return;
      }
      const {
        pdfViewer,
        pdfThumbnailViewer,
        toolbar
      } = this;
      pdfViewer.setPageLabels(labels);
      pdfThumbnailViewer === null || pdfThumbnailViewer === void 0 || pdfThumbnailViewer.setPageLabels(labels);
      toolbar === null || toolbar === void 0 || toolbar.setPagesCount(numLabels, true);
      toolbar === null || toolbar === void 0 || toolbar.setPageNumber(pdfViewer.currentPageNumber, pdfViewer.currentPageLabel);
    },
    _initializePdfHistory(_ref4) {
      let {
        fingerprint,
        viewOnLoad,
        initialDest = null
      } = _ref4;
      if (!this.pdfHistory) {
        return;
      }
      this.pdfHistory.initialize({
        fingerprint,
        resetHistory: viewOnLoad === ViewOnLoad.INITIAL,
        updateUrl: _app_options.AppOptions.get("historyUpdateUrl")
      });
      if (this.pdfHistory.initialBookmark) {
        this.initialBookmark = this.pdfHistory.initialBookmark;
        this.initialRotation = this.pdfHistory.initialRotation;
      }
      if (initialDest && !this.initialBookmark && viewOnLoad === ViewOnLoad.UNKNOWN) {
        this.initialBookmark = JSON.stringify(initialDest);
        this.pdfHistory.push({
          explicitDest: initialDest,
          pageNumber: null
        });
      }
    },
    _initializeAnnotationStorageCallbacks(pdfDocument) {
      if (pdfDocument !== this.pdfDocument) {
        return;
      }
      const {
        annotationStorage
      } = pdfDocument;
      annotationStorage.onSetModified = () => {
        window.addEventListener("beforeunload", beforeUnload);
        this._annotationStorageModified = true;
      };
      annotationStorage.onResetModified = () => {
        window.removeEventListener("beforeunload", beforeUnload);
        delete this._annotationStorageModified;
      };
      annotationStorage.onAnnotationEditor = typeStr => {
        this._hasAnnotationEditors = !!typeStr;
        this.setTitle();
        if (typeStr) {
          this.externalServices.reportTelemetry({
            type: "editing",
            data: {
              type: typeStr
            }
          });
        }
      };
    },
    setInitialView(storedHash) {
      var _this$pdfSidebar2, _this$toolbar3, _this$secondaryToolba3;
      let {
        rotation,
        sidebarView,
        scrollMode,
        spreadMode
      } = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
      const setRotation = angle => {
        if ((0, _ui_utils.isValidRotation)(angle)) {
          this.pdfViewer.pagesRotation = angle;
        }
      };
      const setViewerModes = (scroll, spread) => {
        if ((0, _ui_utils.isValidScrollMode)(scroll)) {
          this.pdfViewer.scrollMode = scroll;
        }
        if ((0, _ui_utils.isValidSpreadMode)(spread)) {
          this.pdfViewer.spreadMode = spread;
        }
      };
      this.isInitialViewSet = true;
      (_this$pdfSidebar2 = this.pdfSidebar) === null || _this$pdfSidebar2 === void 0 || _this$pdfSidebar2.setInitialView(sidebarView);
      setViewerModes(scrollMode, spreadMode);
      if (this.initialBookmark) {
        setRotation(this.initialRotation);
        delete this.initialRotation;
        this.pdfLinkService.setHash(this.initialBookmark);
        this.initialBookmark = null;
      } else if (storedHash) {
        setRotation(rotation);
        this.pdfLinkService.setHash(storedHash);
      }
      (_this$toolbar3 = this.toolbar) === null || _this$toolbar3 === void 0 || _this$toolbar3.setPageNumber(this.pdfViewer.currentPageNumber, this.pdfViewer.currentPageLabel);
      (_this$secondaryToolba3 = this.secondaryToolbar) === null || _this$secondaryToolba3 === void 0 || _this$secondaryToolba3.setPageNumber(this.pdfViewer.currentPageNumber);
      if (!this.pdfViewer.currentScaleValue) {
        this.pdfViewer.currentScaleValue = _ui_utils.DEFAULT_SCALE_VALUE;
      }
    },
    _cleanup() {
      var _this$pdfThumbnailVie4;
      if (!this.pdfDocument) {
        return;
      }
      this.pdfViewer.cleanup();
      (_this$pdfThumbnailVie4 = this.pdfThumbnailViewer) === null || _this$pdfThumbnailVie4 === void 0 || _this$pdfThumbnailVie4.cleanup();
      this.pdfDocument.cleanup();
    },
    forceRendering() {
      var _this$pdfSidebar3;
      this.pdfRenderingQueue.printing = !!this.printService;
      this.pdfRenderingQueue.isThumbnailViewEnabled = ((_this$pdfSidebar3 = this.pdfSidebar) === null || _this$pdfSidebar3 === void 0 ? void 0 : _this$pdfSidebar3.visibleView) === _ui_utils.SidebarView.THUMBS;
      this.pdfRenderingQueue.renderHighestPriority();
    },
    beforePrint() {
      this._printAnnotationStoragePromise = this.pdfScriptingManager.dispatchWillPrint().catch(() => {}).then(() => {
        var _this$pdfDocument4;
        return (_this$pdfDocument4 = this.pdfDocument) === null || _this$pdfDocument4 === void 0 ? void 0 : _this$pdfDocument4.annotationStorage.print;
      });
      if (this.printService) {
        return;
      }
      if (!this.supportsPrinting) {
        this.l10n.get("printing_not_supported").then(msg => {
          this._otherError(msg);
        });
        return;
      }
      if (!this.pdfViewer.pageViewsReady) {
        this.l10n.get("printing_not_ready").then(msg => {
          window.alert(msg);
        });
        return;
      }
      const pagesOverview = this.pdfViewer.getPagesOverview();
      const printContainer = this.appConfig.printContainer;
      const printResolution = _app_options.AppOptions.get("printResolution");
      const optionalContentConfigPromise = this.pdfViewer.optionalContentConfigPromise;
      const printService = PDFPrintServiceFactory.instance.createPrintService(this.pdfDocument, pagesOverview, printContainer, printResolution, optionalContentConfigPromise, this._printAnnotationStoragePromise, this.l10n);
      this.printService = printService;
      this.forceRendering();
      this.setTitle();
      printService.layout();
      if (this._hasAnnotationEditors) {
        this.externalServices.reportTelemetry({
          type: "editing",
          data: {
            type: "print"
          }
        });
      }
    },
    afterPrint() {
      if (this._printAnnotationStoragePromise) {
        this._printAnnotationStoragePromise.then(() => {
          this.pdfScriptingManager.dispatchDidPrint();
        });
        this._printAnnotationStoragePromise = null;
      }
      if (this.printService) {
        var _this$pdfDocument5;
        this.printService.destroy();
        this.printService = null;
        (_this$pdfDocument5 = this.pdfDocument) === null || _this$pdfDocument5 === void 0 || _this$pdfDocument5.annotationStorage.resetModified();
      }
      this.forceRendering();
      this.setTitle();
    },
    rotatePages(delta) {
      this.pdfViewer.pagesRotation += delta;
    },
    requestPresentationMode() {
      var _this$pdfPresentation;
      (_this$pdfPresentation = this.pdfPresentationMode) === null || _this$pdfPresentation === void 0 || _this$pdfPresentation.request();
    },
    triggerPrinting() {
      if (!this.supportsPrinting) {
        return;
      }
      window.print();
    },
    bindEvents() {
      const {
        eventBus,
        _boundEvents
      } = this;
      _boundEvents.beforePrint = this.beforePrint.bind(this);
      _boundEvents.afterPrint = this.afterPrint.bind(this);
      eventBus._on("resize", webViewerResize);
      eventBus._on("hashchange", webViewerHashchange);
      eventBus._on("beforeprint", _boundEvents.beforePrint);
      eventBus._on("afterprint", _boundEvents.afterPrint);
      eventBus._on("pagerender", webViewerPageRender);
      eventBus._on("pagerendered", webViewerPageRendered);
      eventBus._on("updateviewarea", webViewerUpdateViewarea);
      eventBus._on("pagechanging", webViewerPageChanging);
      eventBus._on("scalechanging", webViewerScaleChanging);
      eventBus._on("rotationchanging", webViewerRotationChanging);
      eventBus._on("sidebarviewchanged", webViewerSidebarViewChanged);
      eventBus._on("pagemode", webViewerPageMode);
      eventBus._on("namedaction", webViewerNamedAction);
      eventBus._on("presentationmodechanged", webViewerPresentationModeChanged);
      eventBus._on("presentationmode", webViewerPresentationMode);
      eventBus._on("switchannotationeditormode", webViewerSwitchAnnotationEditorMode);
      eventBus._on("switchannotationeditorparams", webViewerSwitchAnnotationEditorParams);
      eventBus._on("print", webViewerPrint);
      eventBus._on("download", webViewerDownload);
      eventBus._on("openinexternalapp", webViewerOpenInExternalApp);
      eventBus._on("firstpage", webViewerFirstPage);
      eventBus._on("lastpage", webViewerLastPage);
      eventBus._on("nextpage", webViewerNextPage);
      eventBus._on("previouspage", webViewerPreviousPage);
      eventBus._on("zoomin", webViewerZoomIn);
      eventBus._on("zoomout", webViewerZoomOut);
      eventBus._on("zoomreset", webViewerZoomReset);
      eventBus._on("pagenumberchanged", webViewerPageNumberChanged);
      eventBus._on("scalechanged", webViewerScaleChanged);
      eventBus._on("rotatecw", webViewerRotateCw);
      eventBus._on("rotateccw", webViewerRotateCcw);
      eventBus._on("optionalcontentconfig", webViewerOptionalContentConfig);
      eventBus._on("switchscrollmode", webViewerSwitchScrollMode);
      eventBus._on("scrollmodechanged", webViewerScrollModeChanged);
      eventBus._on("switchspreadmode", webViewerSwitchSpreadMode);
      eventBus._on("spreadmodechanged", webViewerSpreadModeChanged);
      eventBus._on("documentproperties", webViewerDocumentProperties);
      eventBus._on("findfromurlhash", webViewerFindFromUrlHash);
      eventBus._on("updatefindmatchescount", webViewerUpdateFindMatchesCount);
      eventBus._on("updatefindcontrolstate", webViewerUpdateFindControlState);
      if (_app_options.AppOptions.get("pdfBug")) {
        _boundEvents.reportPageStatsPDFBug = reportPageStatsPDFBug;
        eventBus._on("pagerendered", _boundEvents.reportPageStatsPDFBug);
        eventBus._on("pagechanging", _boundEvents.reportPageStatsPDFBug);
      }
      eventBus._on("fileinputchange", webViewerFileInputChange);
      eventBus._on("openfile", webViewerOpenFile);
    },
    bindWindowEvents() {
      const {
        eventBus,
        _boundEvents
      } = this;
      function addWindowResolutionChange() {
        let evt = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
        if (evt) {
          webViewerResolutionChange(evt);
        }
        const mediaQueryList = window.matchMedia(`(resolution: ${window.devicePixelRatio || 1}dppx)`);
        mediaQueryList.addEventListener("change", addWindowResolutionChange, {
          once: true
        });
        _boundEvents.removeWindowResolutionChange || (_boundEvents.removeWindowResolutionChange = function () {
          mediaQueryList.removeEventListener("change", addWindowResolutionChange);
          _boundEvents.removeWindowResolutionChange = null;
        });
      }
      addWindowResolutionChange();
      _boundEvents.windowResize = () => {
        eventBus.dispatch("resize", {
          source: window
        });
      };
      _boundEvents.windowHashChange = () => {
        eventBus.dispatch("hashchange", {
          source: window,
          hash: document.location.hash.substring(1)
        });
      };
      _boundEvents.windowBeforePrint = () => {
        eventBus.dispatch("beforeprint", {
          source: window
        });
      };
      _boundEvents.windowAfterPrint = () => {
        eventBus.dispatch("afterprint", {
          source: window
        });
      };
      _boundEvents.windowUpdateFromSandbox = event => {
        eventBus.dispatch("updatefromsandbox", {
          source: window,
          detail: event.detail
        });
      };
      window.addEventListener("visibilitychange", webViewerVisibilityChange);
      window.addEventListener("wheel", webViewerWheel, {
        passive: false
      });
      window.addEventListener("touchstart", webViewerTouchStart, {
        passive: false
      });
      window.addEventListener("touchmove", webViewerTouchMove, {
        passive: false
      });
      window.addEventListener("touchend", webViewerTouchEnd, {
        passive: false
      });
      window.addEventListener("click", webViewerClick);
      window.addEventListener("keydown", webViewerKeyDown);
      window.addEventListener("keyup", webViewerKeyUp);
      window.addEventListener("resize", _boundEvents.windowResize);
      window.addEventListener("hashchange", _boundEvents.windowHashChange);
      window.addEventListener("beforeprint", _boundEvents.windowBeforePrint);
      window.addEventListener("afterprint", _boundEvents.windowAfterPrint);
      window.addEventListener("updatefromsandbox", _boundEvents.windowUpdateFromSandbox);
    },
    unbindEvents() {
      const {
        eventBus,
        _boundEvents
      } = this;
      eventBus._off("resize", webViewerResize);
      eventBus._off("hashchange", webViewerHashchange);
      eventBus._off("beforeprint", _boundEvents.beforePrint);
      eventBus._off("afterprint", _boundEvents.afterPrint);
      eventBus._off("pagerender", webViewerPageRender);
      eventBus._off("pagerendered", webViewerPageRendered);
      eventBus._off("updateviewarea", webViewerUpdateViewarea);
      eventBus._off("pagechanging", webViewerPageChanging);
      eventBus._off("scalechanging", webViewerScaleChanging);
      eventBus._off("rotationchanging", webViewerRotationChanging);
      eventBus._off("sidebarviewchanged", webViewerSidebarViewChanged);
      eventBus._off("pagemode", webViewerPageMode);
      eventBus._off("namedaction", webViewerNamedAction);
      eventBus._off("presentationmodechanged", webViewerPresentationModeChanged);
      eventBus._off("presentationmode", webViewerPresentationMode);
      eventBus._off("print", webViewerPrint);
      eventBus._off("download", webViewerDownload);
      eventBus._off("openinexternalapp", webViewerOpenInExternalApp);
      eventBus._off("firstpage", webViewerFirstPage);
      eventBus._off("lastpage", webViewerLastPage);
      eventBus._off("nextpage", webViewerNextPage);
      eventBus._off("previouspage", webViewerPreviousPage);
      eventBus._off("zoomin", webViewerZoomIn);
      eventBus._off("zoomout", webViewerZoomOut);
      eventBus._off("zoomreset", webViewerZoomReset);
      eventBus._off("pagenumberchanged", webViewerPageNumberChanged);
      eventBus._off("scalechanged", webViewerScaleChanged);
      eventBus._off("rotatecw", webViewerRotateCw);
      eventBus._off("rotateccw", webViewerRotateCcw);
      eventBus._off("optionalcontentconfig", webViewerOptionalContentConfig);
      eventBus._off("switchscrollmode", webViewerSwitchScrollMode);
      eventBus._off("scrollmodechanged", webViewerScrollModeChanged);
      eventBus._off("switchspreadmode", webViewerSwitchSpreadMode);
      eventBus._off("spreadmodechanged", webViewerSpreadModeChanged);
      eventBus._off("documentproperties", webViewerDocumentProperties);
      eventBus._off("findfromurlhash", webViewerFindFromUrlHash);
      eventBus._off("updatefindmatchescount", webViewerUpdateFindMatchesCount);
      eventBus._off("updatefindcontrolstate", webViewerUpdateFindControlState);
      if (_boundEvents.reportPageStatsPDFBug) {
        eventBus._off("pagerendered", _boundEvents.reportPageStatsPDFBug);
        eventBus._off("pagechanging", _boundEvents.reportPageStatsPDFBug);
        _boundEvents.reportPageStatsPDFBug = null;
      }
      eventBus._off("fileinputchange", webViewerFileInputChange);
      eventBus._off("openfile", webViewerOpenFile);
      _boundEvents.beforePrint = null;
      _boundEvents.afterPrint = null;
    },
    unbindWindowEvents() {
      var _boundEvents$removeWi;
      const {
        _boundEvents
      } = this;
      window.removeEventListener("visibilitychange", webViewerVisibilityChange);
      window.removeEventListener("wheel", webViewerWheel, {
        passive: false
      });
      window.removeEventListener("touchstart", webViewerTouchStart, {
        passive: false
      });
      window.removeEventListener("touchmove", webViewerTouchMove, {
        passive: false
      });
      window.removeEventListener("touchend", webViewerTouchEnd, {
        passive: false
      });
      window.removeEventListener("click", webViewerClick);
      window.removeEventListener("keydown", webViewerKeyDown);
      window.removeEventListener("keyup", webViewerKeyUp);
      window.removeEventListener("resize", _boundEvents.windowResize);
      window.removeEventListener("hashchange", _boundEvents.windowHashChange);
      window.removeEventListener("beforeprint", _boundEvents.windowBeforePrint);
      window.removeEventListener("afterprint", _boundEvents.windowAfterPrint);
      window.removeEventListener("updatefromsandbox", _boundEvents.windowUpdateFromSandbox);
      (_boundEvents$removeWi = _boundEvents.removeWindowResolutionChange) === null || _boundEvents$removeWi === void 0 || _boundEvents$removeWi.call(_boundEvents);
      _boundEvents.windowResize = null;
      _boundEvents.windowHashChange = null;
      _boundEvents.windowBeforePrint = null;
      _boundEvents.windowAfterPrint = null;
      _boundEvents.windowUpdateFromSandbox = null;
    },
    _accumulateTicks(ticks, prop) {
      if (this[prop] > 0 && ticks < 0 || this[prop] < 0 && ticks > 0) {
        this[prop] = 0;
      }
      this[prop] += ticks;
      const wholeTicks = Math.trunc(this[prop]);
      this[prop] -= wholeTicks;
      return wholeTicks;
    },
    _accumulateFactor(previousScale, factor, prop) {
      if (factor === 1) {
        return 1;
      }
      if (this[prop] > 1 && factor < 1 || this[prop] < 1 && factor > 1) {
        this[prop] = 1;
      }
      const newFactor = Math.floor(previousScale * factor * this[prop] * 100) / (100 * previousScale);
      this[prop] = factor / newFactor;
      return newFactor;
    },
    _centerAtPos(previousScale, x, y) {
      const {
        pdfViewer
      } = this;
      const scaleDiff = pdfViewer.currentScale / previousScale - 1;
      if (scaleDiff !== 0) {
        const [top, left] = pdfViewer.containerTopLeft;
        pdfViewer.container.scrollLeft += (x - left) * scaleDiff;
        pdfViewer.container.scrollTop += (y - top) * scaleDiff;
      }
    },
    _unblockDocumentLoadEvent() {
      var _document$blockUnbloc, _document;
      (_document$blockUnbloc = (_document = document).blockUnblockOnload) === null || _document$blockUnbloc === void 0 || _document$blockUnbloc.call(_document, false);
      this._unblockDocumentLoadEvent = () => {};
    },
    get scriptingReady() {
      return this.pdfScriptingManager.ready;
    }
  };
  exports.PDFViewerApplication = PDFViewerApplication;
  {
    const HOSTED_VIEWER_ORIGINS = ["null", "http://mozilla.github.io", "https://mozilla.github.io"];
    var validateFileURL = function (file) {
      if (!file) {
        return;
      }
      try {
        const viewerOrigin = new URL(window.location.href).origin || "null";
        if (HOSTED_VIEWER_ORIGINS.includes(viewerOrigin)) {
          return;
        }
        const fileOrigin = new URL(file, window.location.href).origin;
        if (fileOrigin !== viewerOrigin) {
          throw new Error("file origin does not match viewer's");
        }
      } catch (ex) {
        PDFViewerApplication.l10n.get("loading_error").then(msg => {
          PDFViewerApplication._documentError(msg, {
            message: ex === null || ex === void 0 ? void 0 : ex.message
          });
        });
        throw ex;
      }
    };
  }
  async function loadFakeWorker() {
    _pdfjsLib.GlobalWorkerOptions.workerSrc || (_pdfjsLib.GlobalWorkerOptions.workerSrc = _app_options.AppOptions.get("workerSrc"));
    await (0, _pdfjsLib.loadScript)(_pdfjsLib.PDFWorker.workerSrc);
  }
  async function loadPDFBug(self) {
    const {
      debuggerScriptPath
    } = self.appConfig;
    const {
      PDFBug
    } = await import(debuggerScriptPath);
    self._PDFBug = PDFBug;
  }
  function reportPageStatsPDFBug(_ref5) {
    var _globalThis$Stats, _pageView$pdfPage;
    let {
      pageNumber
    } = _ref5;
    if (!((_globalThis$Stats = globalThis.Stats) !== null && _globalThis$Stats !== void 0 && _globalThis$Stats.enabled)) {
      return;
    }
    const pageView = PDFViewerApplication.pdfViewer.getPageView(pageNumber - 1);
    globalThis.Stats.add(pageNumber, pageView === null || pageView === void 0 || (_pageView$pdfPage = pageView.pdfPage) === null || _pageView$pdfPage === void 0 ? void 0 : _pageView$pdfPage.stats);
  }
  function webViewerPageRender(_ref6) {
    let {
      pageNumber
    } = _ref6;
    if (pageNumber === PDFViewerApplication.page) {
      var _PDFViewerApplication;
      (_PDFViewerApplication = PDFViewerApplication.toolbar) === null || _PDFViewerApplication === void 0 || _PDFViewerApplication.updateLoadingIndicatorState(true);
    }
  }
  function webViewerPageRendered(_ref7) {
    var _PDFViewerApplication3;
    let {
      pageNumber,
      error
    } = _ref7;
    if (pageNumber === PDFViewerApplication.page) {
      var _PDFViewerApplication2;
      (_PDFViewerApplication2 = PDFViewerApplication.toolbar) === null || _PDFViewerApplication2 === void 0 || _PDFViewerApplication2.updateLoadingIndicatorState(false);
    }
    if (((_PDFViewerApplication3 = PDFViewerApplication.pdfSidebar) === null || _PDFViewerApplication3 === void 0 ? void 0 : _PDFViewerApplication3.visibleView) === _ui_utils.SidebarView.THUMBS) {
      var _PDFViewerApplication4;
      const pageView = PDFViewerApplication.pdfViewer.getPageView(pageNumber - 1);
      const thumbnailView = (_PDFViewerApplication4 = PDFViewerApplication.pdfThumbnailViewer) === null || _PDFViewerApplication4 === void 0 ? void 0 : _PDFViewerApplication4.getThumbnail(pageNumber - 1);
      if (pageView) {
        thumbnailView === null || thumbnailView === void 0 || thumbnailView.setImage(pageView);
      }
    }
    if (error) {
      PDFViewerApplication.l10n.get("rendering_error").then(msg => {
        PDFViewerApplication._otherError(msg, error);
      });
    }
  }
  function webViewerPageMode(_ref8) {
    var _PDFViewerApplication5;
    let {
      mode
    } = _ref8;
    let view;
    switch (mode) {
      case "thumbs":
        view = _ui_utils.SidebarView.THUMBS;
        break;
      case "bookmarks":
      case "outline":
        view = _ui_utils.SidebarView.OUTLINE;
        break;
      case "attachments":
        view = _ui_utils.SidebarView.ATTACHMENTS;
        break;
      case "layers":
        view = _ui_utils.SidebarView.LAYERS;
        break;
      case "none":
        view = _ui_utils.SidebarView.NONE;
        break;
      default:
        console.error('Invalid "pagemode" hash parameter: ' + mode);
        return;
    }
    (_PDFViewerApplication5 = PDFViewerApplication.pdfSidebar) === null || _PDFViewerApplication5 === void 0 || _PDFViewerApplication5.switchView(view, true);
  }
  function webViewerNamedAction(evt) {
    var _PDFViewerApplication6;
    switch (evt.action) {
      case "GoToPage":
        (_PDFViewerApplication6 = PDFViewerApplication.appConfig.toolbar) === null || _PDFViewerApplication6 === void 0 || _PDFViewerApplication6.pageNumber.select();
        break;
      case "Find":
        if (!PDFViewerApplication.supportsIntegratedFind) {
          PDFViewerApplication === null || PDFViewerApplication === void 0 || PDFViewerApplication.findBar.toggle();
        }
        break;
      case "Print":
        PDFViewerApplication.triggerPrinting();
        break;
      case "SaveAs":
        PDFViewerApplication.downloadOrSave();
        break;
    }
  }
  function webViewerPresentationModeChanged(evt) {
    PDFViewerApplication.pdfViewer.presentationModeState = evt.state;
  }
  function webViewerSidebarViewChanged(_ref9) {
    let {
      view
    } = _ref9;
    PDFViewerApplication.pdfRenderingQueue.isThumbnailViewEnabled = view === _ui_utils.SidebarView.THUMBS;
    if (PDFViewerApplication.isInitialViewSet) {
      var _PDFViewerApplication7;
      (_PDFViewerApplication7 = PDFViewerApplication.store) === null || _PDFViewerApplication7 === void 0 || _PDFViewerApplication7.set("sidebarView", view).catch(() => {});
    }
  }
  function webViewerUpdateViewarea(_ref10) {
    let {
      location
    } = _ref10;
    if (PDFViewerApplication.isInitialViewSet) {
      var _PDFViewerApplication8;
      (_PDFViewerApplication8 = PDFViewerApplication.store) === null || _PDFViewerApplication8 === void 0 || _PDFViewerApplication8.setMultiple({
        page: location.pageNumber,
        zoom: location.scale,
        scrollLeft: location.left,
        scrollTop: location.top,
        rotation: location.rotation
      }).catch(() => {});
    }
    if (PDFViewerApplication.appConfig.secondaryToolbar) {
      const href = PDFViewerApplication.pdfLinkService.getAnchorUrl(location.pdfOpenParams);
      PDFViewerApplication.appConfig.secondaryToolbar.viewBookmarkButton.href = href;
    }
  }
  function webViewerScrollModeChanged(evt) {
    if (PDFViewerApplication.isInitialViewSet && !PDFViewerApplication.pdfViewer.isInPresentationMode) {
      var _PDFViewerApplication9;
      (_PDFViewerApplication9 = PDFViewerApplication.store) === null || _PDFViewerApplication9 === void 0 || _PDFViewerApplication9.set("scrollMode", evt.mode).catch(() => {});
    }
  }
  function webViewerSpreadModeChanged(evt) {
    if (PDFViewerApplication.isInitialViewSet && !PDFViewerApplication.pdfViewer.isInPresentationMode) {
      var _PDFViewerApplication10;
      (_PDFViewerApplication10 = PDFViewerApplication.store) === null || _PDFViewerApplication10 === void 0 || _PDFViewerApplication10.set("spreadMode", evt.mode).catch(() => {});
    }
  }
  function webViewerResize() {
    const {
      pdfDocument,
      pdfViewer,
      pdfRenderingQueue
    } = PDFViewerApplication;
    if (pdfRenderingQueue.printing && window.matchMedia("print").matches) {
      return;
    }
    if (!pdfDocument) {
      return;
    }
    const currentScaleValue = pdfViewer.currentScaleValue;
    if (currentScaleValue === "auto" || currentScaleValue === "page-fit" || currentScaleValue === "page-width") {
      pdfViewer.currentScaleValue = currentScaleValue;
    }
    pdfViewer.update();
  }
  function webViewerHashchange(evt) {
    var _PDFViewerApplication11;
    const hash = evt.hash;
    if (!hash) {
      return;
    }
    if (!PDFViewerApplication.isInitialViewSet) {
      PDFViewerApplication.initialBookmark = hash;
    } else if (!((_PDFViewerApplication11 = PDFViewerApplication.pdfHistory) !== null && _PDFViewerApplication11 !== void 0 && _PDFViewerApplication11.popStateInProgress)) {
      PDFViewerApplication.pdfLinkService.setHash(hash);
    }
  }
  {
    var webViewerFileInputChange = function (evt) {
      var _PDFViewerApplication12;
      if ((_PDFViewerApplication12 = PDFViewerApplication.pdfViewer) !== null && _PDFViewerApplication12 !== void 0 && _PDFViewerApplication12.isInPresentationMode) {
        return;
      }
      const file = evt.fileInput.files[0];
      PDFViewerApplication.open({
        url: URL.createObjectURL(file),
        originalUrl: file.name
      });
    };
    var webViewerOpenFile = function (evt) {
      const fileInput = PDFViewerApplication.appConfig.openFileInput;
      fileInput.click();
    };
  }
  function webViewerPresentationMode() {
    PDFViewerApplication.requestPresentationMode();
  }
  function webViewerSwitchAnnotationEditorMode(evt) {
    PDFViewerApplication.pdfViewer.annotationEditorMode = evt;
  }
  function webViewerSwitchAnnotationEditorParams(evt) {
    PDFViewerApplication.pdfViewer.annotationEditorParams = evt;
  }
  function webViewerPrint() {
    PDFViewerApplication.triggerPrinting();
  }
  function webViewerDownload() {
    PDFViewerApplication.downloadOrSave();
  }
  function webViewerOpenInExternalApp() {
    PDFViewerApplication.openInExternalApp();
  }
  function webViewerFirstPage() {
    PDFViewerApplication.page = 1;
  }
  function webViewerLastPage() {
    PDFViewerApplication.page = PDFViewerApplication.pagesCount;
  }
  function webViewerNextPage() {
    PDFViewerApplication.pdfViewer.nextPage();
  }
  function webViewerPreviousPage() {
    PDFViewerApplication.pdfViewer.previousPage();
  }
  function webViewerZoomIn() {
    PDFViewerApplication.zoomIn();
  }
  function webViewerZoomOut() {
    PDFViewerApplication.zoomOut();
  }
  function webViewerZoomReset() {
    PDFViewerApplication.zoomReset();
  }
  function webViewerPageNumberChanged(evt) {
    const pdfViewer = PDFViewerApplication.pdfViewer;
    if (evt.value !== "") {
      PDFViewerApplication.pdfLinkService.goToPage(evt.value);
    }
    if (evt.value !== pdfViewer.currentPageNumber.toString() && evt.value !== pdfViewer.currentPageLabel) {
      var _PDFViewerApplication13;
      (_PDFViewerApplication13 = PDFViewerApplication.toolbar) === null || _PDFViewerApplication13 === void 0 || _PDFViewerApplication13.setPageNumber(pdfViewer.currentPageNumber, pdfViewer.currentPageLabel);
    }
  }
  function webViewerScaleChanged(evt) {
    PDFViewerApplication.pdfViewer.currentScaleValue = evt.value;
  }
  function webViewerRotateCw() {
    PDFViewerApplication.rotatePages(90);
  }
  function webViewerRotateCcw() {
    PDFViewerApplication.rotatePages(-90);
  }
  function webViewerOptionalContentConfig(evt) {
    PDFViewerApplication.pdfViewer.optionalContentConfigPromise = evt.promise;
  }
  function webViewerSwitchScrollMode(evt) {
    PDFViewerApplication.pdfViewer.scrollMode = evt.mode;
  }
  function webViewerSwitchSpreadMode(evt) {
    PDFViewerApplication.pdfViewer.spreadMode = evt.mode;
  }
  function webViewerDocumentProperties() {
    var _PDFViewerApplication14;
    (_PDFViewerApplication14 = PDFViewerApplication.pdfDocumentProperties) === null || _PDFViewerApplication14 === void 0 || _PDFViewerApplication14.open();
  }
  function webViewerFindFromUrlHash(evt) {
    PDFViewerApplication.eventBus.dispatch("find", {
      source: evt.source,
      type: "",
      query: evt.query,
      caseSensitive: false,
      entireWord: false,
      highlightAll: true,
      findPrevious: false,
      matchDiacritics: true
    });
  }
  function webViewerUpdateFindMatchesCount(_ref11) {
    let {
      matchesCount
    } = _ref11;
    if (PDFViewerApplication.supportsIntegratedFind) {
      PDFViewerApplication.externalServices.updateFindMatchesCount(matchesCount);
    } else {
      PDFViewerApplication.findBar.updateResultsCount(matchesCount);
    }
  }
  function webViewerUpdateFindControlState(_ref12) {
    let {
      state,
      previous,
      matchesCount,
      rawQuery
    } = _ref12;
    if (PDFViewerApplication.supportsIntegratedFind) {
      PDFViewerApplication.externalServices.updateFindControlState({
        result: state,
        findPrevious: previous,
        matchesCount,
        rawQuery
      });
    } else {
      var _PDFViewerApplication15;
      (_PDFViewerApplication15 = PDFViewerApplication.findBar) === null || _PDFViewerApplication15 === void 0 || _PDFViewerApplication15.updateUIState(state, previous, matchesCount);
    }
  }
  function webViewerScaleChanging(evt) {
    var _PDFViewerApplication16;
    (_PDFViewerApplication16 = PDFViewerApplication.toolbar) === null || _PDFViewerApplication16 === void 0 || _PDFViewerApplication16.setPageScale(evt.presetValue, evt.scale);
    PDFViewerApplication.pdfViewer.update();
  }
  function webViewerRotationChanging(evt) {
    if (PDFViewerApplication.pdfThumbnailViewer) {
      PDFViewerApplication.pdfThumbnailViewer.pagesRotation = evt.pagesRotation;
    }
    PDFViewerApplication.forceRendering();
    PDFViewerApplication.pdfViewer.currentPageNumber = evt.pageNumber;
  }
  function webViewerPageChanging(_ref13) {
    var _PDFViewerApplication17, _PDFViewerApplication18, _PDFViewerApplication19, _PDFViewerApplication21;
    let {
      pageNumber,
      pageLabel
    } = _ref13;
    (_PDFViewerApplication17 = PDFViewerApplication.toolbar) === null || _PDFViewerApplication17 === void 0 || _PDFViewerApplication17.setPageNumber(pageNumber, pageLabel);
    (_PDFViewerApplication18 = PDFViewerApplication.secondaryToolbar) === null || _PDFViewerApplication18 === void 0 || _PDFViewerApplication18.setPageNumber(pageNumber);
    if (((_PDFViewerApplication19 = PDFViewerApplication.pdfSidebar) === null || _PDFViewerApplication19 === void 0 ? void 0 : _PDFViewerApplication19.visibleView) === _ui_utils.SidebarView.THUMBS) {
      var _PDFViewerApplication20;
      (_PDFViewerApplication20 = PDFViewerApplication.pdfThumbnailViewer) === null || _PDFViewerApplication20 === void 0 || _PDFViewerApplication20.scrollThumbnailIntoView(pageNumber);
    }
    const currentPage = PDFViewerApplication.pdfViewer.getPageView(pageNumber - 1);
    (_PDFViewerApplication21 = PDFViewerApplication.toolbar) === null || _PDFViewerApplication21 === void 0 || _PDFViewerApplication21.updateLoadingIndicatorState((currentPage === null || currentPage === void 0 ? void 0 : currentPage.renderingState) === _ui_utils.RenderingStates.RUNNING);
  }
  function webViewerResolutionChange(evt) {
    PDFViewerApplication.pdfViewer.refresh();
  }
  function webViewerVisibilityChange(evt) {
    if (document.visibilityState === "visible") {
      setZoomDisabledTimeout();
    }
  }
  let zoomDisabledTimeout = null;
  function setZoomDisabledTimeout() {
    if (zoomDisabledTimeout) {
      clearTimeout(zoomDisabledTimeout);
    }
    zoomDisabledTimeout = setTimeout(function () {
      zoomDisabledTimeout = null;
    }, WHEEL_ZOOM_DISABLED_TIMEOUT);
  }
  function webViewerWheel(evt) {
    const {
      pdfViewer,
      supportedMouseWheelZoomModifierKeys,
      supportsPinchToZoom
    } = PDFViewerApplication;
    if (pdfViewer.isInPresentationMode) {
      return;
    }
    const deltaMode = evt.deltaMode;
    let scaleFactor = Math.exp(-evt.deltaY / 100);
    const isBuiltInMac = false;
    const isPinchToZoom = evt.ctrlKey && !PDFViewerApplication._isCtrlKeyDown && deltaMode === WheelEvent.DOM_DELTA_PIXEL && evt.deltaX === 0 && (Math.abs(scaleFactor - 1) < 0.05 || isBuiltInMac) && evt.deltaZ === 0;
    if (isPinchToZoom || evt.ctrlKey && supportedMouseWheelZoomModifierKeys.ctrlKey || evt.metaKey && supportedMouseWheelZoomModifierKeys.metaKey) {
      evt.preventDefault();
      if (zoomDisabledTimeout || document.visibilityState === "hidden" || PDFViewerApplication.overlayManager.active) {
        return;
      }
      const previousScale = pdfViewer.currentScale;
      if (isPinchToZoom && supportsPinchToZoom) {
        scaleFactor = PDFViewerApplication._accumulateFactor(previousScale, scaleFactor, "_wheelUnusedFactor");
        if (scaleFactor < 1) {
          PDFViewerApplication.zoomOut(null, scaleFactor);
        } else if (scaleFactor > 1) {
          PDFViewerApplication.zoomIn(null, scaleFactor);
        } else {
          return;
        }
      } else {
        const delta = (0, _ui_utils.normalizeWheelEventDirection)(evt);
        let ticks = 0;
        if (deltaMode === WheelEvent.DOM_DELTA_LINE || deltaMode === WheelEvent.DOM_DELTA_PAGE) {
          if (Math.abs(delta) >= 1) {
            ticks = Math.sign(delta);
          } else {
            ticks = PDFViewerApplication._accumulateTicks(delta, "_wheelUnusedTicks");
          }
        } else {
          const PIXELS_PER_LINE_SCALE = 30;
          ticks = PDFViewerApplication._accumulateTicks(delta / PIXELS_PER_LINE_SCALE, "_wheelUnusedTicks");
        }
        if (ticks < 0) {
          PDFViewerApplication.zoomOut(-ticks);
        } else if (ticks > 0) {
          PDFViewerApplication.zoomIn(ticks);
        } else {
          return;
        }
      }
      PDFViewerApplication._centerAtPos(previousScale, evt.clientX, evt.clientY);
    } else {
      setZoomDisabledTimeout();
    }
  }
  function webViewerTouchStart(evt) {
    if (PDFViewerApplication.pdfViewer.isInPresentationMode || evt.touches.length < 2) {
      return;
    }
    evt.preventDefault();
    if (evt.touches.length !== 2 || PDFViewerApplication.overlayManager.active) {
      PDFViewerApplication._touchInfo = null;
      return;
    }
    let [touch0, touch1] = evt.touches;
    if (touch0.identifier > touch1.identifier) {
      [touch0, touch1] = [touch1, touch0];
    }
    PDFViewerApplication._touchInfo = {
      touch0X: touch0.pageX,
      touch0Y: touch0.pageY,
      touch1X: touch1.pageX,
      touch1Y: touch1.pageY
    };
  }
  function webViewerTouchMove(evt) {
    if (!PDFViewerApplication._touchInfo || evt.touches.length !== 2) {
      return;
    }
    const {
      pdfViewer,
      _touchInfo,
      supportsPinchToZoom
    } = PDFViewerApplication;
    let [touch0, touch1] = evt.touches;
    if (touch0.identifier > touch1.identifier) {
      [touch0, touch1] = [touch1, touch0];
    }
    const {
      pageX: page0X,
      pageY: page0Y
    } = touch0;
    const {
      pageX: page1X,
      pageY: page1Y
    } = touch1;
    const {
      touch0X: pTouch0X,
      touch0Y: pTouch0Y,
      touch1X: pTouch1X,
      touch1Y: pTouch1Y
    } = _touchInfo;
    if (Math.abs(pTouch0X - page0X) <= 1 && Math.abs(pTouch0Y - page0Y) <= 1 && Math.abs(pTouch1X - page1X) <= 1 && Math.abs(pTouch1Y - page1Y) <= 1) {
      return;
    }
    _touchInfo.touch0X = page0X;
    _touchInfo.touch0Y = page0Y;
    _touchInfo.touch1X = page1X;
    _touchInfo.touch1Y = page1Y;
    if (pTouch0X === page0X && pTouch0Y === page0Y) {
      const v1X = pTouch1X - page0X;
      const v1Y = pTouch1Y - page0Y;
      const v2X = page1X - page0X;
      const v2Y = page1Y - page0Y;
      const det = v1X * v2Y - v1Y * v2X;
      if (Math.abs(det) > 0.02 * Math.hypot(v1X, v1Y) * Math.hypot(v2X, v2Y)) {
        return;
      }
    } else if (pTouch1X === page1X && pTouch1Y === page1Y) {
      const v1X = pTouch0X - page1X;
      const v1Y = pTouch0Y - page1Y;
      const v2X = page0X - page1X;
      const v2Y = page0Y - page1Y;
      const det = v1X * v2Y - v1Y * v2X;
      if (Math.abs(det) > 0.02 * Math.hypot(v1X, v1Y) * Math.hypot(v2X, v2Y)) {
        return;
      }
    } else {
      const diff0X = page0X - pTouch0X;
      const diff1X = page1X - pTouch1X;
      const diff0Y = page0Y - pTouch0Y;
      const diff1Y = page1Y - pTouch1Y;
      const dotProduct = diff0X * diff1X + diff0Y * diff1Y;
      if (dotProduct >= 0) {
        return;
      }
    }
    evt.preventDefault();
    const distance = Math.hypot(page0X - page1X, page0Y - page1Y) || 1;
    const pDistance = Math.hypot(pTouch0X - pTouch1X, pTouch0Y - pTouch1Y) || 1;
    const previousScale = pdfViewer.currentScale;
    if (supportsPinchToZoom) {
      const newScaleFactor = PDFViewerApplication._accumulateFactor(previousScale, distance / pDistance, "_touchUnusedFactor");
      if (newScaleFactor < 1) {
        PDFViewerApplication.zoomOut(null, newScaleFactor);
      } else if (newScaleFactor > 1) {
        PDFViewerApplication.zoomIn(null, newScaleFactor);
      } else {
        return;
      }
    } else {
      const PIXELS_PER_LINE_SCALE = 30;
      const ticks = PDFViewerApplication._accumulateTicks((distance - pDistance) / PIXELS_PER_LINE_SCALE, "_touchUnusedTicks");
      if (ticks < 0) {
        PDFViewerApplication.zoomOut(-ticks);
      } else if (ticks > 0) {
        PDFViewerApplication.zoomIn(ticks);
      } else {
        return;
      }
    }
    PDFViewerApplication._centerAtPos(previousScale, (page0X + page1X) / 2, (page0Y + page1Y) / 2);
  }
  function webViewerTouchEnd(evt) {
    if (!PDFViewerApplication._touchInfo) {
      return;
    }
    evt.preventDefault();
    PDFViewerApplication._touchInfo = null;
    PDFViewerApplication._touchUnusedTicks = 0;
    PDFViewerApplication._touchUnusedFactor = 1;
  }
  function webViewerClick(evt) {
    var _PDFViewerApplication22, _appConfig$toolbar4, _appConfig$secondaryT5;
    if (!((_PDFViewerApplication22 = PDFViewerApplication.secondaryToolbar) !== null && _PDFViewerApplication22 !== void 0 && _PDFViewerApplication22.isOpen)) {
      return;
    }
    const appConfig = PDFViewerApplication.appConfig;
    if (PDFViewerApplication.pdfViewer.containsElement(evt.target) || (_appConfig$toolbar4 = appConfig.toolbar) !== null && _appConfig$toolbar4 !== void 0 && _appConfig$toolbar4.container.contains(evt.target) && evt.target !== ((_appConfig$secondaryT5 = appConfig.secondaryToolbar) === null || _appConfig$secondaryT5 === void 0 ? void 0 : _appConfig$secondaryT5.toggleButton)) {
      PDFViewerApplication.secondaryToolbar.close();
    }
  }
  function webViewerKeyUp(evt) {
    if (evt.key === "Control") {
      PDFViewerApplication._isCtrlKeyDown = false;
    }
  }
  function webViewerKeyDown(evt) {
    var _PDFViewerApplication24, _PDFViewerApplication25, _PDFViewerApplication26, _PDFViewerApplication27, _PDFViewerApplication28;
    PDFViewerApplication._isCtrlKeyDown = evt.key === "Control";
    if (PDFViewerApplication.overlayManager.active) {
      return;
    }
    const {
      eventBus,
      pdfViewer
    } = PDFViewerApplication;
    const isViewerInPresentationMode = pdfViewer.isInPresentationMode;
    let handled = false,
      ensureViewerFocused = false;
    const cmd = (evt.ctrlKey ? 1 : 0) | (evt.altKey ? 2 : 0) | (evt.shiftKey ? 4 : 0) | (evt.metaKey ? 8 : 0);
    if (cmd === 1 || cmd === 8 || cmd === 5 || cmd === 12) {
      switch (evt.keyCode) {
        case 70:
          if (!PDFViewerApplication.supportsIntegratedFind && !evt.shiftKey) {
            var _PDFViewerApplication23;
            (_PDFViewerApplication23 = PDFViewerApplication.findBar) === null || _PDFViewerApplication23 === void 0 || _PDFViewerApplication23.open();
            handled = true;
          }
          break;
        case 71:
          if (!PDFViewerApplication.supportsIntegratedFind) {
            const {
              state
            } = PDFViewerApplication.findController;
            if (state) {
              const newState = {
                source: window,
                type: "again",
                findPrevious: cmd === 5 || cmd === 12
              };
              eventBus.dispatch("find", {
                ...state,
                ...newState
              });
            }
            handled = true;
          }
          break;
        case 61:
        case 107:
        case 187:
        case 171:
          PDFViewerApplication.zoomIn();
          handled = true;
          break;
        case 173:
        case 109:
        case 189:
          PDFViewerApplication.zoomOut();
          handled = true;
          break;
        case 48:
        case 96:
          if (!isViewerInPresentationMode) {
            setTimeout(function () {
              PDFViewerApplication.zoomReset();
            });
            handled = false;
          }
          break;
        case 38:
          if (isViewerInPresentationMode || PDFViewerApplication.page > 1) {
            PDFViewerApplication.page = 1;
            handled = true;
            ensureViewerFocused = true;
          }
          break;
        case 40:
          if (isViewerInPresentationMode || PDFViewerApplication.page < PDFViewerApplication.pagesCount) {
            PDFViewerApplication.page = PDFViewerApplication.pagesCount;
            handled = true;
            ensureViewerFocused = true;
          }
          break;
      }
    }
    if (cmd === 1 || cmd === 8) {
      switch (evt.keyCode) {
        case 83:
          eventBus.dispatch("download", {
            source: window
          });
          handled = true;
          break;
        case 79:
          {
            eventBus.dispatch("openfile", {
              source: window
            });
            handled = true;
          }
          break;
      }
    }
    if (cmd === 3 || cmd === 10) {
      switch (evt.keyCode) {
        case 80:
          PDFViewerApplication.requestPresentationMode();
          handled = true;
          PDFViewerApplication.externalServices.reportTelemetry({
            type: "buttons",
            data: {
              id: "presentationModeKeyboard"
            }
          });
          break;
        case 71:
          if (PDFViewerApplication.appConfig.toolbar) {
            PDFViewerApplication.appConfig.toolbar.pageNumber.select();
            handled = true;
          }
          break;
      }
    }
    if (handled) {
      if (ensureViewerFocused && !isViewerInPresentationMode) {
        pdfViewer.focus();
      }
      evt.preventDefault();
      return;
    }
    const curElement = (0, _ui_utils.getActiveOrFocusedElement)();
    const curElementTagName = curElement === null || curElement === void 0 ? void 0 : curElement.tagName.toUpperCase();
    if (curElementTagName === "INPUT" || curElementTagName === "TEXTAREA" || curElementTagName === "SELECT" || curElement !== null && curElement !== void 0 && curElement.isContentEditable) {
      if (evt.keyCode !== 27) {
        return;
      }
    }
    if (cmd === 0) {
      let turnPage = 0,
        turnOnlyIfPageFit = false;
      switch (evt.keyCode) {
        case 38:
        case 33:
          if (pdfViewer.isVerticalScrollbarEnabled) {
            turnOnlyIfPageFit = true;
          }
          turnPage = -1;
          break;
        case 8:
          if (!isViewerInPresentationMode) {
            turnOnlyIfPageFit = true;
          }
          turnPage = -1;
          break;
        case 37:
          if (pdfViewer.isHorizontalScrollbarEnabled) {
            turnOnlyIfPageFit = true;
          }
        case 75:
        case 80:
          turnPage = -1;
          break;
        case 27:
          if ((_PDFViewerApplication24 = PDFViewerApplication.secondaryToolbar) !== null && _PDFViewerApplication24 !== void 0 && _PDFViewerApplication24.isOpen) {
            PDFViewerApplication.secondaryToolbar.close();
            handled = true;
          }
          if (!PDFViewerApplication.supportsIntegratedFind && (_PDFViewerApplication25 = PDFViewerApplication.findBar) !== null && _PDFViewerApplication25 !== void 0 && _PDFViewerApplication25.opened) {
            PDFViewerApplication.findBar.close();
            handled = true;
          }
          break;
        case 40:
        case 34:
          if (pdfViewer.isVerticalScrollbarEnabled) {
            turnOnlyIfPageFit = true;
          }
          turnPage = 1;
          break;
        case 13:
        case 32:
          if (!isViewerInPresentationMode) {
            turnOnlyIfPageFit = true;
          }
          turnPage = 1;
          break;
        case 39:
          if (pdfViewer.isHorizontalScrollbarEnabled) {
            turnOnlyIfPageFit = true;
          }
        case 74:
        case 78:
          turnPage = 1;
          break;
        case 36:
          if (isViewerInPresentationMode || PDFViewerApplication.page > 1) {
            PDFViewerApplication.page = 1;
            handled = true;
            ensureViewerFocused = true;
          }
          break;
        case 35:
          if (isViewerInPresentationMode || PDFViewerApplication.page < PDFViewerApplication.pagesCount) {
            PDFViewerApplication.page = PDFViewerApplication.pagesCount;
            handled = true;
            ensureViewerFocused = true;
          }
          break;
        case 83:
          (_PDFViewerApplication26 = PDFViewerApplication.pdfCursorTools) === null || _PDFViewerApplication26 === void 0 || _PDFViewerApplication26.switchTool(_ui_utils.CursorTool.SELECT);
          break;
        case 72:
          (_PDFViewerApplication27 = PDFViewerApplication.pdfCursorTools) === null || _PDFViewerApplication27 === void 0 || _PDFViewerApplication27.switchTool(_ui_utils.CursorTool.HAND);
          break;
        case 82:
          PDFViewerApplication.rotatePages(90);
          break;
        case 115:
          (_PDFViewerApplication28 = PDFViewerApplication.pdfSidebar) === null || _PDFViewerApplication28 === void 0 || _PDFViewerApplication28.toggle();
          break;
      }
      if (turnPage !== 0 && (!turnOnlyIfPageFit || pdfViewer.currentScaleValue === "page-fit")) {
        if (turnPage > 0) {
          pdfViewer.nextPage();
        } else {
          pdfViewer.previousPage();
        }
        handled = true;
      }
    }
    if (cmd === 4) {
      switch (evt.keyCode) {
        case 13:
        case 32:
          if (!isViewerInPresentationMode && pdfViewer.currentScaleValue !== "page-fit") {
            break;
          }
          pdfViewer.previousPage();
          handled = true;
          break;
        case 82:
          PDFViewerApplication.rotatePages(-90);
          break;
      }
    }
    if (!handled && !isViewerInPresentationMode) {
      if (evt.keyCode >= 33 && evt.keyCode <= 40 || evt.keyCode === 32 && curElementTagName !== "BUTTON") {
        ensureViewerFocused = true;
      }
    }
    if (ensureViewerFocused && !pdfViewer.containsElement(curElement)) {
      pdfViewer.focus();
    }
    if (handled) {
      evt.preventDefault();
    }
  }
  function beforeUnload(evt) {
    evt.preventDefault();
    evt.returnValue = "";
    return false;
  }
  function webViewerAnnotationEditorStatesChanged(data) {
    PDFViewerApplication.externalServices.updateEditorStates(data);
  }
  function webViewerReportTelemetry(_ref14) {
    let {
      details
    } = _ref14;
    PDFViewerApplication.externalServices.reportTelemetry(details);
  }
  const PDFPrintServiceFactory = {
    instance: {
      supportsPrinting: false,
      createPrintService() {
        throw new Error("Not implemented: createPrintService");
      }
    }
  };
  exports.PDFPrintServiceFactory = PDFPrintServiceFactory;
  
  /***/ }),
  /* 122 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var global = __webpack_require__(5);
  var apply = __webpack_require__(84);
  var wrapErrorConstructorWithCause = __webpack_require__(123);
  var WEB_ASSEMBLY = 'WebAssembly';
  var WebAssembly = global[WEB_ASSEMBLY];
  var FORCED = Error('e', { cause: 7 }).cause !== 7;
  var exportGlobalErrorCauseWrapper = function (ERROR_NAME, wrapper) {
   var O = {};
   O[ERROR_NAME] = wrapErrorConstructorWithCause(ERROR_NAME, wrapper, FORCED);
   $({
    global: true,
    constructor: true,
    arity: 1,
    forced: FORCED
   }, O);
  };
  var exportWebAssemblyErrorCauseWrapper = function (ERROR_NAME, wrapper) {
   if (WebAssembly && WebAssembly[ERROR_NAME]) {
    var O = {};
    O[ERROR_NAME] = wrapErrorConstructorWithCause(WEB_ASSEMBLY + '.' + ERROR_NAME, wrapper, FORCED);
    $({
     target: WEB_ASSEMBLY,
     stat: true,
     constructor: true,
     arity: 1,
     forced: FORCED
    }, O);
   }
  };
  exportGlobalErrorCauseWrapper('Error', function (init) {
   return function Error(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('EvalError', function (init) {
   return function EvalError(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('RangeError', function (init) {
   return function RangeError(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('ReferenceError', function (init) {
   return function ReferenceError(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('SyntaxError', function (init) {
   return function SyntaxError(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('TypeError', function (init) {
   return function TypeError(message) {
    return apply(init, this, arguments);
   };
  });
  exportGlobalErrorCauseWrapper('URIError', function (init) {
   return function URIError(message) {
    return apply(init, this, arguments);
   };
  });
  exportWebAssemblyErrorCauseWrapper('CompileError', function (init) {
   return function CompileError(message) {
    return apply(init, this, arguments);
   };
  });
  exportWebAssemblyErrorCauseWrapper('LinkError', function (init) {
   return function LinkError(message) {
    return apply(init, this, arguments);
   };
  });
  exportWebAssemblyErrorCauseWrapper('RuntimeError', function (init) {
   return function RuntimeError(message) {
    return apply(init, this, arguments);
   };
  });
  
  /***/ }),
  /* 123 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  var hasOwn = __webpack_require__(40);
  var createNonEnumerableProperty = __webpack_require__(45);
  var isPrototypeOf = __webpack_require__(26);
  var setPrototypeOf = __webpack_require__(71);
  var copyConstructorProperties = __webpack_require__(57);
  var proxyAccessor = __webpack_require__(124);
  var inheritIfRequired = __webpack_require__(125);
  var normalizeStringArgument = __webpack_require__(126);
  var installErrorCause = __webpack_require__(127);
  var installErrorStack = __webpack_require__(128);
  var DESCRIPTORS = __webpack_require__(7);
  var IS_PURE = __webpack_require__(37);
  module.exports = function (FULL_NAME, wrapper, FORCED, IS_AGGREGATE_ERROR) {
   var STACK_TRACE_LIMIT = 'stackTraceLimit';
   var OPTIONS_POSITION = IS_AGGREGATE_ERROR ? 2 : 1;
   var path = FULL_NAME.split('.');
   var ERROR_NAME = path[path.length - 1];
   var OriginalError = getBuiltIn.apply(null, path);
   if (!OriginalError)
    return;
   var OriginalErrorPrototype = OriginalError.prototype;
   if (!IS_PURE && hasOwn(OriginalErrorPrototype, 'cause'))
    delete OriginalErrorPrototype.cause;
   if (!FORCED)
    return OriginalError;
   var BaseError = getBuiltIn('Error');
   var WrappedError = wrapper(function (a, b) {
    var message = normalizeStringArgument(IS_AGGREGATE_ERROR ? b : a, undefined);
    var result = IS_AGGREGATE_ERROR ? new OriginalError(a) : new OriginalError();
    if (message !== undefined)
     createNonEnumerableProperty(result, 'message', message);
    installErrorStack(result, WrappedError, result.stack, 2);
    if (this && isPrototypeOf(OriginalErrorPrototype, this))
     inheritIfRequired(result, this, WrappedError);
    if (arguments.length > OPTIONS_POSITION)
     installErrorCause(result, arguments[OPTIONS_POSITION]);
    return result;
   });
   WrappedError.prototype = OriginalErrorPrototype;
   if (ERROR_NAME !== 'Error') {
    if (setPrototypeOf)
     setPrototypeOf(WrappedError, BaseError);
    else
     copyConstructorProperties(WrappedError, BaseError, { name: true });
   } else if (DESCRIPTORS && STACK_TRACE_LIMIT in OriginalError) {
    proxyAccessor(WrappedError, OriginalError, STACK_TRACE_LIMIT);
    proxyAccessor(WrappedError, OriginalError, 'prepareStackTrace');
   }
   copyConstructorProperties(WrappedError, OriginalError);
   if (!IS_PURE)
    try {
     if (OriginalErrorPrototype.name !== ERROR_NAME) {
      createNonEnumerableProperty(OriginalErrorPrototype, 'name', ERROR_NAME);
     }
     OriginalErrorPrototype.constructor = WrappedError;
    } catch (error) {
    }
   return WrappedError;
  };
  
  /***/ }),
  /* 124 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var defineProperty = (__webpack_require__(46).f);
  module.exports = function (Target, Source, key) {
   key in Target || defineProperty(Target, key, {
    configurable: true,
    get: function () {
     return Source[key];
    },
    set: function (it) {
     Source[key] = it;
    }
   });
  };
  
  /***/ }),
  /* 125 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isCallable = __webpack_require__(22);
  var isObject = __webpack_require__(21);
  var setPrototypeOf = __webpack_require__(71);
  module.exports = function ($this, dummy, Wrapper) {
   var NewTarget, NewTargetPrototype;
   if (setPrototypeOf && isCallable(NewTarget = dummy.constructor) && NewTarget !== Wrapper && isObject(NewTargetPrototype = NewTarget.prototype) && NewTargetPrototype !== Wrapper.prototype)
    setPrototypeOf($this, NewTargetPrototype);
   return $this;
  };
  
  /***/ }),
  /* 126 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var toString = __webpack_require__(118);
  module.exports = function (argument, $default) {
   return argument === undefined ? arguments.length < 2 ? '' : $default : toString(argument);
  };
  
  /***/ }),
  /* 127 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isObject = __webpack_require__(21);
  var createNonEnumerableProperty = __webpack_require__(45);
  module.exports = function (O, options) {
   if (isObject(options) && 'cause' in options) {
    createNonEnumerableProperty(O, 'cause', options.cause);
   }
  };
  
  /***/ }),
  /* 128 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var createNonEnumerableProperty = __webpack_require__(45);
  var clearErrorStack = __webpack_require__(129);
  var ERROR_STACK_INSTALLABLE = __webpack_require__(130);
  var captureStackTrace = Error.captureStackTrace;
  module.exports = function (error, C, stack, dropEntries) {
   if (ERROR_STACK_INSTALLABLE) {
    if (captureStackTrace)
     captureStackTrace(error, C);
    else
     createNonEnumerableProperty(error, 'stack', clearErrorStack(stack, dropEntries));
   }
  };
  
  /***/ }),
  /* 129 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var $Error = Error;
  var replace = uncurryThis(''.replace);
  var TEST = function (arg) {
   return String($Error(arg).stack);
  }('zxcasd');
  var V8_OR_CHAKRA_STACK_ENTRY = /\n\s*at [^:]*:[^\n]*/;
  var IS_V8_OR_CHAKRA_STACK = V8_OR_CHAKRA_STACK_ENTRY.test(TEST);
  module.exports = function (stack, dropEntries) {
   if (IS_V8_OR_CHAKRA_STACK && typeof stack == 'string' && !$Error.prepareStackTrace) {
    while (dropEntries--)
     stack = replace(stack, V8_OR_CHAKRA_STACK_ENTRY, '');
   }
   return stack;
  };
  
  /***/ }),
  /* 130 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  var createPropertyDescriptor = __webpack_require__(12);
  module.exports = !fails(function () {
   var error = Error('a');
   if (!('stack' in error))
    return true;
   Object.defineProperty(error, 'stack', createPropertyDescriptor(1, 7));
   return error.stack !== 7;
  });
  
  /***/ }),
  /* 131 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var $includes = (__webpack_require__(61).includes);
  var fails = __webpack_require__(8);
  var addToUnscopables = __webpack_require__(132);
  var BROKEN_ON_SPARSE = fails(function () {
   return !Array(1).includes();
  });
  $({
   target: 'Array',
   proto: true,
   forced: BROKEN_ON_SPARSE
  }, {
   includes: function includes(el) {
    return $includes(this, el, arguments.length > 1 ? arguments[1] : undefined);
   }
  });
  addToUnscopables('includes');
  
  /***/ }),
  /* 132 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var wellKnownSymbol = __webpack_require__(35);
  var create = __webpack_require__(133);
  var defineProperty = (__webpack_require__(46).f);
  var UNSCOPABLES = wellKnownSymbol('unscopables');
  var ArrayPrototype = Array.prototype;
  if (ArrayPrototype[UNSCOPABLES] === undefined) {
   defineProperty(ArrayPrototype, UNSCOPABLES, {
    configurable: true,
    value: create(null)
   });
  }
  module.exports = function (key) {
   ArrayPrototype[UNSCOPABLES][key] = true;
  };
  
  /***/ }),
  /* 133 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var anObject = __webpack_require__(48);
  var definePropertiesModule = __webpack_require__(134);
  var enumBugKeys = __webpack_require__(67);
  var hiddenKeys = __webpack_require__(56);
  var html = __webpack_require__(87);
  var documentCreateElement = __webpack_require__(44);
  var sharedKey = __webpack_require__(55);
  var GT = '>';
  var LT = '<';
  var PROTOTYPE = 'prototype';
  var SCRIPT = 'script';
  var IE_PROTO = sharedKey('IE_PROTO');
  var EmptyConstructor = function () {
  };
  var scriptTag = function (content) {
   return LT + SCRIPT + GT + content + LT + '/' + SCRIPT + GT;
  };
  var NullProtoObjectViaActiveX = function (activeXDocument) {
   activeXDocument.write(scriptTag(''));
   activeXDocument.close();
   var temp = activeXDocument.parentWindow.Object;
   activeXDocument = null;
   return temp;
  };
  var NullProtoObjectViaIFrame = function () {
   var iframe = documentCreateElement('iframe');
   var JS = 'java' + SCRIPT + ':';
   var iframeDocument;
   iframe.style.display = 'none';
   html.appendChild(iframe);
   iframe.src = String(JS);
   iframeDocument = iframe.contentWindow.document;
   iframeDocument.open();
   iframeDocument.write(scriptTag('document.F=Object'));
   iframeDocument.close();
   return iframeDocument.F;
  };
  var activeXDocument;
  var NullProtoObject = function () {
   try {
    activeXDocument = new ActiveXObject('htmlfile');
   } catch (error) {
   }
   NullProtoObject = typeof document != 'undefined' ? document.domain && activeXDocument ? NullProtoObjectViaActiveX(activeXDocument) : NullProtoObjectViaIFrame() : NullProtoObjectViaActiveX(activeXDocument);
   var length = enumBugKeys.length;
   while (length--)
    delete NullProtoObject[PROTOTYPE][enumBugKeys[length]];
   return NullProtoObject();
  };
  hiddenKeys[IE_PROTO] = true;
  module.exports = Object.create || function create(O, Properties) {
   var result;
   if (O !== null) {
    EmptyConstructor[PROTOTYPE] = anObject(O);
    result = new EmptyConstructor();
    EmptyConstructor[PROTOTYPE] = null;
    result[IE_PROTO] = O;
   } else
    result = NullProtoObject();
   return Properties === undefined ? result : definePropertiesModule.f(result, Properties);
  };
  
  /***/ }),
  /* 134 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var V8_PROTOTYPE_DEFINE_BUG = __webpack_require__(47);
  var definePropertyModule = __webpack_require__(46);
  var anObject = __webpack_require__(48);
  var toIndexedObject = __webpack_require__(13);
  var objectKeys = __webpack_require__(135);
  exports.f = DESCRIPTORS && !V8_PROTOTYPE_DEFINE_BUG ? Object.defineProperties : function defineProperties(O, Properties) {
   anObject(O);
   var props = toIndexedObject(Properties);
   var keys = objectKeys(Properties);
   var length = keys.length;
   var index = 0;
   var key;
   while (length > index)
    definePropertyModule.f(O, key = keys[index++], props[key]);
   return O;
  };
  
  /***/ }),
  /* 135 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var internalObjectKeys = __webpack_require__(60);
  var enumBugKeys = __webpack_require__(67);
  module.exports = Object.keys || function keys(O) {
   return internalObjectKeys(O, enumBugKeys);
  };
  
  /***/ }),
  /* 136 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var exec = __webpack_require__(137);
  $({
   target: 'RegExp',
   proto: true,
   forced: /./.exec !== exec
  }, { exec: exec });
  
  /***/ }),
  /* 137 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var uncurryThis = __webpack_require__(15);
  var toString = __webpack_require__(118);
  var regexpFlags = __webpack_require__(138);
  var stickyHelpers = __webpack_require__(139);
  var shared = __webpack_require__(36);
  var create = __webpack_require__(133);
  var getInternalState = (__webpack_require__(53).get);
  var UNSUPPORTED_DOT_ALL = __webpack_require__(140);
  var UNSUPPORTED_NCG = __webpack_require__(141);
  var nativeReplace = shared('native-string-replace', String.prototype.replace);
  var nativeExec = RegExp.prototype.exec;
  var patchedExec = nativeExec;
  var charAt = uncurryThis(''.charAt);
  var indexOf = uncurryThis(''.indexOf);
  var replace = uncurryThis(''.replace);
  var stringSlice = uncurryThis(''.slice);
  var UPDATES_LAST_INDEX_WRONG = (function () {
   var re1 = /a/;
   var re2 = /b*/g;
   call(nativeExec, re1, 'a');
   call(nativeExec, re2, 'a');
   return re1.lastIndex !== 0 || re2.lastIndex !== 0;
  }());
  var UNSUPPORTED_Y = stickyHelpers.BROKEN_CARET;
  var NPCG_INCLUDED = /()??/.exec('')[1] !== undefined;
  var PATCH = UPDATES_LAST_INDEX_WRONG || NPCG_INCLUDED || UNSUPPORTED_Y || UNSUPPORTED_DOT_ALL || UNSUPPORTED_NCG;
  if (PATCH) {
   patchedExec = function exec(string) {
    var re = this;
    var state = getInternalState(re);
    var str = toString(string);
    var raw = state.raw;
    var result, reCopy, lastIndex, match, i, object, group;
    if (raw) {
     raw.lastIndex = re.lastIndex;
     result = call(patchedExec, raw, str);
     re.lastIndex = raw.lastIndex;
     return result;
    }
    var groups = state.groups;
    var sticky = UNSUPPORTED_Y && re.sticky;
    var flags = call(regexpFlags, re);
    var source = re.source;
    var charsAdded = 0;
    var strCopy = str;
    if (sticky) {
     flags = replace(flags, 'y', '');
     if (indexOf(flags, 'g') === -1) {
      flags += 'g';
     }
     strCopy = stringSlice(str, re.lastIndex);
     if (re.lastIndex > 0 && (!re.multiline || re.multiline && charAt(str, re.lastIndex - 1) !== '\n')) {
      source = '(?: ' + source + ')';
      strCopy = ' ' + strCopy;
      charsAdded++;
     }
     reCopy = new RegExp('^(?:' + source + ')', flags);
    }
    if (NPCG_INCLUDED) {
     reCopy = new RegExp('^' + source + '$(?!\\s)', flags);
    }
    if (UPDATES_LAST_INDEX_WRONG)
     lastIndex = re.lastIndex;
    match = call(nativeExec, sticky ? reCopy : re, strCopy);
    if (sticky) {
     if (match) {
      match.input = stringSlice(match.input, charsAdded);
      match[0] = stringSlice(match[0], charsAdded);
      match.index = re.lastIndex;
      re.lastIndex += match[0].length;
     } else
      re.lastIndex = 0;
    } else if (UPDATES_LAST_INDEX_WRONG && match) {
     re.lastIndex = re.global ? match.index + match[0].length : lastIndex;
    }
    if (NPCG_INCLUDED && match && match.length > 1) {
     call(nativeReplace, match[0], reCopy, function () {
      for (i = 1; i < arguments.length - 2; i++) {
       if (arguments[i] === undefined)
        match[i] = undefined;
      }
     });
    }
    if (match && groups) {
     match.groups = object = create(null);
     for (i = 0; i < groups.length; i++) {
      group = groups[i];
      object[group[0]] = match[group[1]];
     }
    }
    return match;
   };
  }
  module.exports = patchedExec;
  
  /***/ }),
  /* 138 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var anObject = __webpack_require__(48);
  module.exports = function () {
   var that = anObject(this);
   var result = '';
   if (that.hasIndices)
    result += 'd';
   if (that.global)
    result += 'g';
   if (that.ignoreCase)
    result += 'i';
   if (that.multiline)
    result += 'm';
   if (that.dotAll)
    result += 's';
   if (that.unicode)
    result += 'u';
   if (that.unicodeSets)
    result += 'v';
   if (that.sticky)
    result += 'y';
   return result;
  };
  
  /***/ }),
  /* 139 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  var global = __webpack_require__(5);
  var $RegExp = global.RegExp;
  var UNSUPPORTED_Y = fails(function () {
   var re = $RegExp('a', 'y');
   re.lastIndex = 2;
   return re.exec('abcd') !== null;
  });
  var MISSED_STICKY = UNSUPPORTED_Y || fails(function () {
   return !$RegExp('a', 'y').sticky;
  });
  var BROKEN_CARET = UNSUPPORTED_Y || fails(function () {
   var re = $RegExp('^r', 'gy');
   re.lastIndex = 2;
   return re.exec('str') !== null;
  });
  module.exports = {
   BROKEN_CARET: BROKEN_CARET,
   MISSED_STICKY: MISSED_STICKY,
   UNSUPPORTED_Y: UNSUPPORTED_Y
  };
  
  /***/ }),
  /* 140 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  var global = __webpack_require__(5);
  var $RegExp = global.RegExp;
  module.exports = fails(function () {
   var re = $RegExp('.', 's');
   return !(re.dotAll && re.exec('\n') && re.flags === 's');
  });
  
  /***/ }),
  /* 141 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var fails = __webpack_require__(8);
  var global = __webpack_require__(5);
  var $RegExp = global.RegExp;
  module.exports = fails(function () {
   var re = $RegExp('(?<a>b)', 'g');
   return re.exec('b').groups.a !== 'b' || 'b'.replace(re, '$<a>c') !== 'bc';
  });
  
  /***/ }),
  /* 142 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var toObject = __webpack_require__(41);
  var lengthOfArrayLike = __webpack_require__(65);
  var setArrayLength = __webpack_require__(143);
  var doesNotExceedSafeInteger = __webpack_require__(144);
  var fails = __webpack_require__(8);
  var INCORRECT_TO_LENGTH = fails(function () {
   return [].push.call({ length: 0x100000000 }, 1) !== 4294967297;
  });
  var properErrorOnNonWritableLength = function () {
   try {
    Object.defineProperty([], 'length', { writable: false }).push();
   } catch (error) {
    return error instanceof TypeError;
   }
  };
  var FORCED = INCORRECT_TO_LENGTH || !properErrorOnNonWritableLength();
  $({
   target: 'Array',
   proto: true,
   arity: 1,
   forced: FORCED
  }, {
   push: function push(item) {
    var O = toObject(this);
    var len = lengthOfArrayLike(O);
    var argCount = arguments.length;
    doesNotExceedSafeInteger(len + argCount);
    for (var i = 0; i < argCount; i++) {
     O[len] = arguments[i];
     len++;
    }
    setArrayLength(O, len);
    return len;
   }
  });
  
  /***/ }),
  /* 143 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var isArray = __webpack_require__(117);
  var $TypeError = TypeError;
  var getOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
  var SILENT_ON_NON_WRITABLE_LENGTH_SET = DESCRIPTORS && !(function () {
   if (this !== undefined)
    return true;
   try {
    Object.defineProperty([], 'length', { writable: false }).length = 1;
   } catch (error) {
    return error instanceof TypeError;
   }
  }());
  module.exports = SILENT_ON_NON_WRITABLE_LENGTH_SET ? function (O, length) {
   if (isArray(O) && !getOwnPropertyDescriptor(O, 'length').writable) {
    throw $TypeError('Cannot set read only .length');
   }
   return O.length = length;
  } : function (O, length) {
   return O.length = length;
  };
  
  /***/ }),
  /* 144 */
  /***/ ((module) => {
  
  
  var $TypeError = TypeError;
  var MAX_SAFE_INTEGER = 0x1FFFFFFFFFFFFF;
  module.exports = function (it) {
   if (it > MAX_SAFE_INTEGER)
    throw $TypeError('Maximum allowed index exceeded');
   return it;
  };
  
  /***/ }),
  /* 145 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var defineBuiltIn = __webpack_require__(49);
  var uncurryThis = __webpack_require__(15);
  var toString = __webpack_require__(118);
  var validateArgumentsLength = __webpack_require__(89);
  var $URLSearchParams = URLSearchParams;
  var URLSearchParamsPrototype = $URLSearchParams.prototype;
  var append = uncurryThis(URLSearchParamsPrototype.append);
  var $delete = uncurryThis(URLSearchParamsPrototype['delete']);
  var forEach = uncurryThis(URLSearchParamsPrototype.forEach);
  var push = uncurryThis([].push);
  var params = new $URLSearchParams('a=1&a=2&b=3');
  params['delete']('a', 1);
  params['delete']('b', undefined);
  if (params + '' !== 'a=2') {
   defineBuiltIn(URLSearchParamsPrototype, 'delete', function (name) {
    var length = arguments.length;
    var $value = length < 2 ? undefined : arguments[1];
    if (length && $value === undefined)
     return $delete(this, name);
    var entries = [];
    forEach(this, function (v, k) {
     push(entries, {
      key: k,
      value: v
     });
    });
    validateArgumentsLength(length, 1);
    var key = toString(name);
    var value = toString($value);
    var index = 0;
    var dindex = 0;
    var found = false;
    var entriesLength = entries.length;
    var entry;
    while (index < entriesLength) {
     entry = entries[index++];
     if (found || entry.key === key) {
      found = true;
      $delete(this, entry.key);
     } else
      dindex++;
    }
    while (dindex < entriesLength) {
     entry = entries[dindex++];
     if (!(entry.key === key && entry.value === value))
      append(this, entry.key, entry.value);
    }
   }, {
    enumerable: true,
    unsafe: true
   });
  }
  
  /***/ }),
  /* 146 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var defineBuiltIn = __webpack_require__(49);
  var uncurryThis = __webpack_require__(15);
  var toString = __webpack_require__(118);
  var validateArgumentsLength = __webpack_require__(89);
  var $URLSearchParams = URLSearchParams;
  var URLSearchParamsPrototype = $URLSearchParams.prototype;
  var getAll = uncurryThis(URLSearchParamsPrototype.getAll);
  var $has = uncurryThis(URLSearchParamsPrototype.has);
  var params = new $URLSearchParams('a=1');
  if (params.has('a', 2) || !params.has('a', undefined)) {
   defineBuiltIn(URLSearchParamsPrototype, 'has', function has(name) {
    var length = arguments.length;
    var $value = length < 2 ? undefined : arguments[1];
    if (length && $value === undefined)
     return $has(this, name);
    var values = getAll(this, name);
    validateArgumentsLength(length, 1);
    var value = toString($value);
    var index = 0;
    while (index < values.length) {
     if (values[index++] === value)
      return true;
    }
    return false;
   }, {
    enumerable: true,
    unsafe: true
   });
  }
  
  /***/ }),
  /* 147 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var uncurryThis = __webpack_require__(15);
  var defineBuiltInAccessor = __webpack_require__(76);
  var URLSearchParamsPrototype = URLSearchParams.prototype;
  var forEach = uncurryThis(URLSearchParamsPrototype.forEach);
  if (DESCRIPTORS && !('size' in URLSearchParamsPrototype)) {
   defineBuiltInAccessor(URLSearchParamsPrototype, 'size', {
    get: function size() {
     var count = 0;
     forEach(this, function () {
      count++;
     });
     return count;
    },
    configurable: true,
    enumerable: true
   });
  }
  
  /***/ }),
  /* 148 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  __webpack_require__(122);
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.animationStarted = exports.VERTICAL_PADDING = exports.UNKNOWN_SCALE = exports.TextLayerMode = exports.SpreadMode = exports.SidebarView = exports.ScrollMode = exports.SCROLLBAR_PADDING = exports.RenderingStates = exports.ProgressBar = exports.PresentationModeState = exports.OutputScale = exports.MIN_SCALE = exports.MAX_SCALE = exports.MAX_AUTO_SCALE = exports.DEFAULT_SCALE_VALUE = exports.DEFAULT_SCALE_DELTA = exports.DEFAULT_SCALE = exports.CursorTool = exports.AutoPrintRegExp = void 0;
  exports.apiPageLayoutToViewerModes = apiPageLayoutToViewerModes;
  exports.apiPageModeToSidebarView = apiPageModeToSidebarView;
  exports.approximateFraction = approximateFraction;
  exports.backtrackBeforeAllVisibleElements = backtrackBeforeAllVisibleElements;
  exports.binarySearchFirstItem = binarySearchFirstItem;
  exports.docStyle = void 0;
  exports.getActiveOrFocusedElement = getActiveOrFocusedElement;
  exports.getPageSizeInches = getPageSizeInches;
  exports.getVisibleElements = getVisibleElements;
  exports.isPortraitOrientation = isPortraitOrientation;
  exports.isValidRotation = isValidRotation;
  exports.isValidScrollMode = isValidScrollMode;
  exports.isValidSpreadMode = isValidSpreadMode;
  exports.normalizeWheelEventDelta = normalizeWheelEventDelta;
  exports.normalizeWheelEventDirection = normalizeWheelEventDirection;
  exports.parseQueryString = parseQueryString;
  exports.removeNullCharacters = removeNullCharacters;
  exports.roundToDivide = roundToDivide;
  exports.scrollIntoView = scrollIntoView;
  exports.toggleCheckedBtn = toggleCheckedBtn;
  exports.toggleExpandedBtn = toggleExpandedBtn;
  exports.watchScroll = watchScroll;
  __webpack_require__(145);
  __webpack_require__(146);
  __webpack_require__(147);
  __webpack_require__(136);
  __webpack_require__(149);
  __webpack_require__(155);
  __webpack_require__(158);
  __webpack_require__(169);
  __webpack_require__(171);
  __webpack_require__(173);
  __webpack_require__(175);
  __webpack_require__(177);
  __webpack_require__(179);
  __webpack_require__(142);
  __webpack_require__(181);
  __webpack_require__(131);
  __webpack_require__(2);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  const DEFAULT_SCALE_VALUE = "auto";
  exports.DEFAULT_SCALE_VALUE = DEFAULT_SCALE_VALUE;
  const DEFAULT_SCALE = 1.0;
  exports.DEFAULT_SCALE = DEFAULT_SCALE;
  const DEFAULT_SCALE_DELTA = 1.1;
  exports.DEFAULT_SCALE_DELTA = DEFAULT_SCALE_DELTA;
  const MIN_SCALE = 0.1;
  exports.MIN_SCALE = MIN_SCALE;
  const MAX_SCALE = 10.0;
  exports.MAX_SCALE = MAX_SCALE;
  const UNKNOWN_SCALE = 0;
  exports.UNKNOWN_SCALE = UNKNOWN_SCALE;
  const MAX_AUTO_SCALE = 1.25;
  exports.MAX_AUTO_SCALE = MAX_AUTO_SCALE;
  const SCROLLBAR_PADDING = 40;
  exports.SCROLLBAR_PADDING = SCROLLBAR_PADDING;
  const VERTICAL_PADDING = 5;
  exports.VERTICAL_PADDING = VERTICAL_PADDING;
  const RenderingStates = {
    INITIAL: 0,
    RUNNING: 1,
    PAUSED: 2,
    FINISHED: 3
  };
  exports.RenderingStates = RenderingStates;
  const PresentationModeState = {
    UNKNOWN: 0,
    NORMAL: 1,
    CHANGING: 2,
    FULLSCREEN: 3
  };
  exports.PresentationModeState = PresentationModeState;
  const SidebarView = {
    UNKNOWN: -1,
    NONE: 0,
    THUMBS: 1,
    OUTLINE: 2,
    ATTACHMENTS: 3,
    LAYERS: 4
  };
  exports.SidebarView = SidebarView;
  const TextLayerMode = {
    DISABLE: 0,
    ENABLE: 1,
    ENABLE_PERMISSIONS: 2
  };
  exports.TextLayerMode = TextLayerMode;
  const ScrollMode = {
    UNKNOWN: -1,
    VERTICAL: 0,
    HORIZONTAL: 1,
    WRAPPED: 2,
    PAGE: 3
  };
  exports.ScrollMode = ScrollMode;
  const SpreadMode = {
    UNKNOWN: -1,
    NONE: 0,
    ODD: 1,
    EVEN: 2
  };
  exports.SpreadMode = SpreadMode;
  const CursorTool = {
    SELECT: 0,
    HAND: 1,
    ZOOM: 2
  };
  exports.CursorTool = CursorTool;
  const AutoPrintRegExp = /\bprint\s*\(/;
  exports.AutoPrintRegExp = AutoPrintRegExp;
  class OutputScale {
    constructor() {
      const pixelRatio = window.devicePixelRatio || 1;
      this.sx = pixelRatio;
      this.sy = pixelRatio;
    }
    get scaled() {
      return this.sx !== 1 || this.sy !== 1;
    }
  }
  exports.OutputScale = OutputScale;
  function scrollIntoView(element, spot) {
    let scrollMatches = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
    let parent = element.offsetParent;
    if (!parent) {
      console.error("offsetParent is not set -- cannot scroll");
      return;
    }
    let offsetY = element.offsetTop + element.clientTop;
    let offsetX = element.offsetLeft + element.clientLeft;
    while (parent.clientHeight === parent.scrollHeight && parent.clientWidth === parent.scrollWidth || scrollMatches && (parent.classList.contains("markedContent") || getComputedStyle(parent).overflow === "hidden")) {
      offsetY += parent.offsetTop;
      offsetX += parent.offsetLeft;
      parent = parent.offsetParent;
      if (!parent) {
        return;
      }
    }
    if (spot) {
      if (spot.top !== undefined) {
        offsetY += spot.top;
      }
      if (spot.left !== undefined) {
        offsetX += spot.left;
        parent.scrollLeft = offsetX;
      }
    }
    parent.scrollTop = offsetY;
  }
  function watchScroll(viewAreaElement, callback) {
    const debounceScroll = function (evt) {
      if (rAF) {
        return;
      }
      rAF = window.requestAnimationFrame(function viewAreaElementScrolled() {
        rAF = null;
        const currentX = viewAreaElement.scrollLeft;
        const lastX = state.lastX;
        if (currentX !== lastX) {
          state.right = currentX > lastX;
        }
        state.lastX = currentX;
        const currentY = viewAreaElement.scrollTop;
        const lastY = state.lastY;
        if (currentY !== lastY) {
          state.down = currentY > lastY;
        }
        state.lastY = currentY;
        callback(state);
      });
    };
    const state = {
      right: true,
      down: true,
      lastX: viewAreaElement.scrollLeft,
      lastY: viewAreaElement.scrollTop,
      _eventHandler: debounceScroll
    };
    let rAF = null;
    viewAreaElement.addEventListener("scroll", debounceScroll, true);
    return state;
  }
  function parseQueryString(query) {
    const params = new Map();
    for (const [key, value] of new URLSearchParams(query)) {
      params.set(key.toLowerCase(), value);
    }
    return params;
  }
  const InvisibleCharactersRegExp = /[\x01-\x1F]/g;
  function removeNullCharacters(str) {
    let replaceInvisible = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
    if (typeof str !== "string") {
      console.error(`The argument must be a string.`);
      return str;
    }
    if (replaceInvisible) {
      str = str.replaceAll(InvisibleCharactersRegExp, " ");
    }
    return str.replaceAll("\x00", "");
  }
  function binarySearchFirstItem(items, condition) {
    let start = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 0;
    let minIndex = start;
    let maxIndex = items.length - 1;
    if (maxIndex < 0 || !condition(items[maxIndex])) {
      return items.length;
    }
    if (condition(items[minIndex])) {
      return minIndex;
    }
    while (minIndex < maxIndex) {
      const currentIndex = minIndex + maxIndex >> 1;
      const currentItem = items[currentIndex];
      if (condition(currentItem)) {
        maxIndex = currentIndex;
      } else {
        minIndex = currentIndex + 1;
      }
    }
    return minIndex;
  }
  function approximateFraction(x) {
    if (Math.floor(x) === x) {
      return [x, 1];
    }
    const xinv = 1 / x;
    const limit = 8;
    if (xinv > limit) {
      return [1, limit];
    } else if (Math.floor(xinv) === xinv) {
      return [1, xinv];
    }
    const x_ = x > 1 ? xinv : x;
    let a = 0,
      b = 1,
      c = 1,
      d = 1;
    while (true) {
      const p = a + c,
        q = b + d;
      if (q > limit) {
        break;
      }
      if (x_ <= p / q) {
        c = p;
        d = q;
      } else {
        a = p;
        b = q;
      }
    }
    let result;
    if (x_ - a / b < c / d - x_) {
      result = x_ === x ? [a, b] : [b, a];
    } else {
      result = x_ === x ? [c, d] : [d, c];
    }
    return result;
  }
  function roundToDivide(x, div) {
    const r = x % div;
    return r === 0 ? x : Math.round(x - r + div);
  }
  function getPageSizeInches(_ref) {
    let {
      view,
      userUnit,
      rotate
    } = _ref;
    const [x1, y1, x2, y2] = view;
    const changeOrientation = rotate % 180 !== 0;
    const width = (x2 - x1) / 72 * userUnit;
    const height = (y2 - y1) / 72 * userUnit;
    return {
      width: changeOrientation ? height : width,
      height: changeOrientation ? width : height
    };
  }
  function backtrackBeforeAllVisibleElements(index, views, top) {
    if (index < 2) {
      return index;
    }
    let elt = views[index].div;
    let pageTop = elt.offsetTop + elt.clientTop;
    if (pageTop >= top) {
      elt = views[index - 1].div;
      pageTop = elt.offsetTop + elt.clientTop;
    }
    for (let i = index - 2; i >= 0; --i) {
      elt = views[i].div;
      if (elt.offsetTop + elt.clientTop + elt.clientHeight <= pageTop) {
        break;
      }
      index = i;
    }
    return index;
  }
  function getVisibleElements(_ref2) {
    let {
      scrollEl,
      views,
      sortByVisibility = false,
      horizontal = false,
      rtl = false
    } = _ref2;
    const top = scrollEl.scrollTop,
      bottom = top + scrollEl.clientHeight;
    const left = scrollEl.scrollLeft,
      right = left + scrollEl.clientWidth;
    function isElementBottomAfterViewTop(view) {
      const element = view.div;
      const elementBottom = element.offsetTop + element.clientTop + element.clientHeight;
      return elementBottom > top;
    }
    function isElementNextAfterViewHorizontally(view) {
      const element = view.div;
      const elementLeft = element.offsetLeft + element.clientLeft;
      const elementRight = elementLeft + element.clientWidth;
      return rtl ? elementLeft < right : elementRight > left;
    }
    const visible = [],
      ids = new Set(),
      numViews = views.length;
    let firstVisibleElementInd = binarySearchFirstItem(views, horizontal ? isElementNextAfterViewHorizontally : isElementBottomAfterViewTop);
    if (firstVisibleElementInd > 0 && firstVisibleElementInd < numViews && !horizontal) {
      firstVisibleElementInd = backtrackBeforeAllVisibleElements(firstVisibleElementInd, views, top);
    }
    let lastEdge = horizontal ? right : -1;
    for (let i = firstVisibleElementInd; i < numViews; i++) {
      const view = views[i],
        element = view.div;
      const currentWidth = element.offsetLeft + element.clientLeft;
      const currentHeight = element.offsetTop + element.clientTop;
      const viewWidth = element.clientWidth,
        viewHeight = element.clientHeight;
      const viewRight = currentWidth + viewWidth;
      const viewBottom = currentHeight + viewHeight;
      if (lastEdge === -1) {
        if (viewBottom >= bottom) {
          lastEdge = viewBottom;
        }
      } else if ((horizontal ? currentWidth : currentHeight) > lastEdge) {
        break;
      }
      if (viewBottom <= top || currentHeight >= bottom || viewRight <= left || currentWidth >= right) {
        continue;
      }
      const hiddenHeight = Math.max(0, top - currentHeight) + Math.max(0, viewBottom - bottom);
      const hiddenWidth = Math.max(0, left - currentWidth) + Math.max(0, viewRight - right);
      const fractionHeight = (viewHeight - hiddenHeight) / viewHeight,
        fractionWidth = (viewWidth - hiddenWidth) / viewWidth;
      const percent = fractionHeight * fractionWidth * 100 | 0;
      visible.push({
        id: view.id,
        x: currentWidth,
        y: currentHeight,
        view,
        percent,
        widthPercent: fractionWidth * 100 | 0
      });
      ids.add(view.id);
    }
    const first = visible[0],
      last = visible.at(-1);
    if (sortByVisibility) {
      visible.sort(function (a, b) {
        const pc = a.percent - b.percent;
        if (Math.abs(pc) > 0.001) {
          return -pc;
        }
        return a.id - b.id;
      });
    }
    return {
      first,
      last,
      views: visible,
      ids
    };
  }
  function normalizeWheelEventDirection(evt) {
    let delta = Math.hypot(evt.deltaX, evt.deltaY);
    const angle = Math.atan2(evt.deltaY, evt.deltaX);
    if (-0.25 * Math.PI < angle && angle < 0.75 * Math.PI) {
      delta = -delta;
    }
    return delta;
  }
  function normalizeWheelEventDelta(evt) {
    const deltaMode = evt.deltaMode;
    let delta = normalizeWheelEventDirection(evt);
    const MOUSE_PIXELS_PER_LINE = 30;
    const MOUSE_LINES_PER_PAGE = 30;
    if (deltaMode === WheelEvent.DOM_DELTA_PIXEL) {
      delta /= MOUSE_PIXELS_PER_LINE * MOUSE_LINES_PER_PAGE;
    } else if (deltaMode === WheelEvent.DOM_DELTA_LINE) {
      delta /= MOUSE_LINES_PER_PAGE;
    }
    return delta;
  }
  function isValidRotation(angle) {
    return Number.isInteger(angle) && angle % 90 === 0;
  }
  function isValidScrollMode(mode) {
    return Number.isInteger(mode) && Object.values(ScrollMode).includes(mode) && mode !== ScrollMode.UNKNOWN;
  }
  function isValidSpreadMode(mode) {
    return Number.isInteger(mode) && Object.values(SpreadMode).includes(mode) && mode !== SpreadMode.UNKNOWN;
  }
  function isPortraitOrientation(size) {
    return size.width <= size.height;
  }
  const animationStarted = new Promise(function (resolve) {
    window.requestAnimationFrame(resolve);
  });
  exports.animationStarted = animationStarted;
  const docStyle = document.documentElement.style;
  exports.docStyle = docStyle;
  function clamp(v, min, max) {
    return Math.min(Math.max(v, min), max);
  }
  var _classList = /*#__PURE__*/new WeakMap();
  var _disableAutoFetchTimeout = /*#__PURE__*/new WeakMap();
  var _percent = /*#__PURE__*/new WeakMap();
  var _style = /*#__PURE__*/new WeakMap();
  var _visible = /*#__PURE__*/new WeakMap();
  class ProgressBar {
    constructor(bar) {
      _classPrivateFieldInitSpec(this, _classList, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _disableAutoFetchTimeout, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _percent, {
        writable: true,
        value: 0
      });
      _classPrivateFieldInitSpec(this, _style, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _visible, {
        writable: true,
        value: true
      });
      _classPrivateFieldSet(this, _classList, bar.classList);
      _classPrivateFieldSet(this, _style, bar.style);
    }
    get percent() {
      return _classPrivateFieldGet(this, _percent);
    }
    set percent(val) {
      _classPrivateFieldSet(this, _percent, clamp(val, 0, 100));
      if (isNaN(val)) {
        _classPrivateFieldGet(this, _classList).add("indeterminate");
        return;
      }
      _classPrivateFieldGet(this, _classList).remove("indeterminate");
      _classPrivateFieldGet(this, _style).setProperty("--progressBar-percent", `${_classPrivateFieldGet(this, _percent)}%`);
    }
    setWidth(viewer) {
      if (!viewer) {
        return;
      }
      const container = viewer.parentNode;
      const scrollbarWidth = container.offsetWidth - viewer.offsetWidth;
      if (scrollbarWidth > 0) {
        _classPrivateFieldGet(this, _style).setProperty("--progressBar-end-offset", `${scrollbarWidth}px`);
      }
    }
    setDisableAutoFetch() {
      let delay = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 5000;
      if (isNaN(_classPrivateFieldGet(this, _percent))) {
        return;
      }
      if (_classPrivateFieldGet(this, _disableAutoFetchTimeout)) {
        clearTimeout(_classPrivateFieldGet(this, _disableAutoFetchTimeout));
      }
      this.show();
      _classPrivateFieldSet(this, _disableAutoFetchTimeout, setTimeout(() => {
        _classPrivateFieldSet(this, _disableAutoFetchTimeout, null);
        this.hide();
      }, delay));
    }
    hide() {
      if (!_classPrivateFieldGet(this, _visible)) {
        return;
      }
      _classPrivateFieldSet(this, _visible, false);
      _classPrivateFieldGet(this, _classList).add("hidden");
    }
    show() {
      if (_classPrivateFieldGet(this, _visible)) {
        return;
      }
      _classPrivateFieldSet(this, _visible, true);
      _classPrivateFieldGet(this, _classList).remove("hidden");
    }
  }
  exports.ProgressBar = ProgressBar;
  function getActiveOrFocusedElement() {
    let curRoot = document;
    let curActiveOrFocused = curRoot.activeElement || curRoot.querySelector(":focus");
    while ((_curActiveOrFocused = curActiveOrFocused) !== null && _curActiveOrFocused !== void 0 && _curActiveOrFocused.shadowRoot) {
      var _curActiveOrFocused;
      curRoot = curActiveOrFocused.shadowRoot;
      curActiveOrFocused = curRoot.activeElement || curRoot.querySelector(":focus");
    }
    return curActiveOrFocused;
  }
  function apiPageLayoutToViewerModes(layout) {
    let scrollMode = ScrollMode.VERTICAL,
      spreadMode = SpreadMode.NONE;
    switch (layout) {
      case "SinglePage":
        scrollMode = ScrollMode.PAGE;
        break;
      case "OneColumn":
        break;
      case "TwoPageLeft":
        scrollMode = ScrollMode.PAGE;
      case "TwoColumnLeft":
        spreadMode = SpreadMode.ODD;
        break;
      case "TwoPageRight":
        scrollMode = ScrollMode.PAGE;
      case "TwoColumnRight":
        spreadMode = SpreadMode.EVEN;
        break;
    }
    return {
      scrollMode,
      spreadMode
    };
  }
  function apiPageModeToSidebarView(mode) {
    switch (mode) {
      case "UseNone":
        return SidebarView.NONE;
      case "UseThumbs":
        return SidebarView.THUMBS;
      case "UseOutlines":
        return SidebarView.OUTLINE;
      case "UseAttachments":
        return SidebarView.ATTACHMENTS;
      case "UseOC":
        return SidebarView.LAYERS;
    }
    return SidebarView.NONE;
  }
  function toggleCheckedBtn(button, toggle) {
    let view = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
    button.classList.toggle("toggled", toggle);
    button.setAttribute("aria-checked", toggle);
    view === null || view === void 0 || view.classList.toggle("hidden", !toggle);
  }
  function toggleExpandedBtn(button, toggle) {
    let view = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
    button.classList.toggle("toggled", toggle);
    button.setAttribute("aria-expanded", toggle);
    view === null || view === void 0 || view.classList.toggle("hidden", !toggle);
  }
  
  /***/ }),
  /* 149 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var apply = __webpack_require__(84);
  var call = __webpack_require__(9);
  var uncurryThis = __webpack_require__(15);
  var fixRegExpWellKnownSymbolLogic = __webpack_require__(150);
  var fails = __webpack_require__(8);
  var anObject = __webpack_require__(48);
  var isCallable = __webpack_require__(22);
  var isNullOrUndefined = __webpack_require__(18);
  var toIntegerOrInfinity = __webpack_require__(63);
  var toLength = __webpack_require__(66);
  var toString = __webpack_require__(118);
  var requireObjectCoercible = __webpack_require__(17);
  var advanceStringIndex = __webpack_require__(151);
  var getMethod = __webpack_require__(31);
  var getSubstitution = __webpack_require__(153);
  var regExpExec = __webpack_require__(154);
  var wellKnownSymbol = __webpack_require__(35);
  var REPLACE = wellKnownSymbol('replace');
  var max = Math.max;
  var min = Math.min;
  var concat = uncurryThis([].concat);
  var push = uncurryThis([].push);
  var stringIndexOf = uncurryThis(''.indexOf);
  var stringSlice = uncurryThis(''.slice);
  var maybeToString = function (it) {
   return it === undefined ? it : String(it);
  };
  var REPLACE_KEEPS_$0 = (function () {
   return 'a'.replace(/./, '$0') === '$0';
  }());
  var REGEXP_REPLACE_SUBSTITUTES_UNDEFINED_CAPTURE = (function () {
   if (/./[REPLACE]) {
    return /./[REPLACE]('a', '$0') === '';
   }
   return false;
  }());
  var REPLACE_SUPPORTS_NAMED_GROUPS = !fails(function () {
   var re = /./;
   re.exec = function () {
    var result = [];
    result.groups = { a: '7' };
    return result;
   };
   return ''.replace(re, '$<a>') !== '7';
  });
  fixRegExpWellKnownSymbolLogic('replace', function (_, nativeReplace, maybeCallNative) {
   var UNSAFE_SUBSTITUTE = REGEXP_REPLACE_SUBSTITUTES_UNDEFINED_CAPTURE ? '$' : '$0';
   return [
    function replace(searchValue, replaceValue) {
     var O = requireObjectCoercible(this);
     var replacer = isNullOrUndefined(searchValue) ? undefined : getMethod(searchValue, REPLACE);
     return replacer ? call(replacer, searchValue, O, replaceValue) : call(nativeReplace, toString(O), searchValue, replaceValue);
    },
    function (string, replaceValue) {
     var rx = anObject(this);
     var S = toString(string);
     if (typeof replaceValue == 'string' && stringIndexOf(replaceValue, UNSAFE_SUBSTITUTE) === -1 && stringIndexOf(replaceValue, '$<') === -1) {
      var res = maybeCallNative(nativeReplace, rx, S, replaceValue);
      if (res.done)
       return res.value;
     }
     var functionalReplace = isCallable(replaceValue);
     if (!functionalReplace)
      replaceValue = toString(replaceValue);
     var global = rx.global;
     var fullUnicode;
     if (global) {
      fullUnicode = rx.unicode;
      rx.lastIndex = 0;
     }
     var results = [];
     var result;
     while (true) {
      result = regExpExec(rx, S);
      if (result === null)
       break;
      push(results, result);
      if (!global)
       break;
      var matchStr = toString(result[0]);
      if (matchStr === '')
       rx.lastIndex = advanceStringIndex(S, toLength(rx.lastIndex), fullUnicode);
     }
     var accumulatedResult = '';
     var nextSourcePosition = 0;
     for (var i = 0; i < results.length; i++) {
      result = results[i];
      var matched = toString(result[0]);
      var position = max(min(toIntegerOrInfinity(result.index), S.length), 0);
      var captures = [];
      var replacement;
      for (var j = 1; j < result.length; j++)
       push(captures, maybeToString(result[j]));
      var namedCaptures = result.groups;
      if (functionalReplace) {
       var replacerArgs = concat([matched], captures, position, S);
       if (namedCaptures !== undefined)
        push(replacerArgs, namedCaptures);
       replacement = toString(apply(replaceValue, undefined, replacerArgs));
      } else {
       replacement = getSubstitution(matched, S, position, captures, namedCaptures, replaceValue);
      }
      if (position >= nextSourcePosition) {
       accumulatedResult += stringSlice(S, nextSourcePosition, position) + replacement;
       nextSourcePosition = position + matched.length;
      }
     }
     return accumulatedResult + stringSlice(S, nextSourcePosition);
    }
   ];
  }, !REPLACE_SUPPORTS_NAMED_GROUPS || !REPLACE_KEEPS_$0 || REGEXP_REPLACE_SUBSTITUTES_UNDEFINED_CAPTURE);
  
  /***/ }),
  /* 150 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  __webpack_require__(136);
  var uncurryThis = __webpack_require__(86);
  var defineBuiltIn = __webpack_require__(49);
  var regexpExec = __webpack_require__(137);
  var fails = __webpack_require__(8);
  var wellKnownSymbol = __webpack_require__(35);
  var createNonEnumerableProperty = __webpack_require__(45);
  var SPECIES = wellKnownSymbol('species');
  var RegExpPrototype = RegExp.prototype;
  module.exports = function (KEY, exec, FORCED, SHAM) {
   var SYMBOL = wellKnownSymbol(KEY);
   var DELEGATES_TO_SYMBOL = !fails(function () {
    var O = {};
    O[SYMBOL] = function () {
     return 7;
    };
    return ''[KEY](O) !== 7;
   });
   var DELEGATES_TO_EXEC = DELEGATES_TO_SYMBOL && !fails(function () {
    var execCalled = false;
    var re = /a/;
    if (KEY === 'split') {
     re = {};
     re.constructor = {};
     re.constructor[SPECIES] = function () {
      return re;
     };
     re.flags = '';
     re[SYMBOL] = /./[SYMBOL];
    }
    re.exec = function () {
     execCalled = true;
     return null;
    };
    re[SYMBOL]('');
    return !execCalled;
   });
   if (!DELEGATES_TO_SYMBOL || !DELEGATES_TO_EXEC || FORCED) {
    var uncurriedNativeRegExpMethod = uncurryThis(/./[SYMBOL]);
    var methods = exec(SYMBOL, ''[KEY], function (nativeMethod, regexp, str, arg2, forceStringMethod) {
     var uncurriedNativeMethod = uncurryThis(nativeMethod);
     var $exec = regexp.exec;
     if ($exec === regexpExec || $exec === RegExpPrototype.exec) {
      if (DELEGATES_TO_SYMBOL && !forceStringMethod) {
       return {
        done: true,
        value: uncurriedNativeRegExpMethod(regexp, str, arg2)
       };
      }
      return {
       done: true,
       value: uncurriedNativeMethod(str, regexp, arg2)
      };
     }
     return { done: false };
    });
    defineBuiltIn(String.prototype, KEY, methods[0]);
    defineBuiltIn(RegExpPrototype, SYMBOL, methods[1]);
   }
   if (SHAM)
    createNonEnumerableProperty(RegExpPrototype[SYMBOL], 'sham', true);
  };
  
  /***/ }),
  /* 151 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var charAt = (__webpack_require__(152).charAt);
  module.exports = function (S, index, unicode) {
   return index + (unicode ? charAt(S, index).length : 1);
  };
  
  /***/ }),
  /* 152 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var toIntegerOrInfinity = __webpack_require__(63);
  var toString = __webpack_require__(118);
  var requireObjectCoercible = __webpack_require__(17);
  var charAt = uncurryThis(''.charAt);
  var charCodeAt = uncurryThis(''.charCodeAt);
  var stringSlice = uncurryThis(''.slice);
  var createMethod = function (CONVERT_TO_STRING) {
   return function ($this, pos) {
    var S = toString(requireObjectCoercible($this));
    var position = toIntegerOrInfinity(pos);
    var size = S.length;
    var first, second;
    if (position < 0 || position >= size)
     return CONVERT_TO_STRING ? '' : undefined;
    first = charCodeAt(S, position);
    return first < 0xD800 || first > 0xDBFF || position + 1 === size || (second = charCodeAt(S, position + 1)) < 0xDC00 || second > 0xDFFF ? CONVERT_TO_STRING ? charAt(S, position) : first : CONVERT_TO_STRING ? stringSlice(S, position, position + 2) : (first - 0xD800 << 10) + (second - 0xDC00) + 0x10000;
   };
  };
  module.exports = {
   codeAt: createMethod(false),
   charAt: createMethod(true)
  };
  
  /***/ }),
  /* 153 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var toObject = __webpack_require__(41);
  var floor = Math.floor;
  var charAt = uncurryThis(''.charAt);
  var replace = uncurryThis(''.replace);
  var stringSlice = uncurryThis(''.slice);
  var SUBSTITUTION_SYMBOLS = /\$([$&'`]|\d{1,2}|<[^>]*>)/g;
  var SUBSTITUTION_SYMBOLS_NO_NAMED = /\$([$&'`]|\d{1,2})/g;
  module.exports = function (matched, str, position, captures, namedCaptures, replacement) {
   var tailPos = position + matched.length;
   var m = captures.length;
   var symbols = SUBSTITUTION_SYMBOLS_NO_NAMED;
   if (namedCaptures !== undefined) {
    namedCaptures = toObject(namedCaptures);
    symbols = SUBSTITUTION_SYMBOLS;
   }
   return replace(replacement, symbols, function (match, ch) {
    var capture;
    switch (charAt(ch, 0)) {
    case '$':
     return '$';
    case '&':
     return matched;
    case '`':
     return stringSlice(str, 0, position);
    case "'":
     return stringSlice(str, tailPos);
    case '<':
     capture = namedCaptures[stringSlice(ch, 1, -1)];
     break;
    default:
     var n = +ch;
     if (n === 0)
      return match;
     if (n > m) {
      var f = floor(n / 10);
      if (f === 0)
       return match;
      if (f <= m)
       return captures[f - 1] === undefined ? charAt(ch, 1) : captures[f - 1] + charAt(ch, 1);
      return match;
     }
     capture = captures[n - 1];
    }
    return capture === undefined ? '' : capture;
   });
  };
  
  /***/ }),
  /* 154 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var anObject = __webpack_require__(48);
  var isCallable = __webpack_require__(22);
  var classof = __webpack_require__(16);
  var regexpExec = __webpack_require__(137);
  var $TypeError = TypeError;
  module.exports = function (R, S) {
   var exec = R.exec;
   if (isCallable(exec)) {
    var result = call(exec, R, S);
    if (result !== null)
     anObject(result);
    return result;
   }
   if (classof(R) === 'RegExp')
    return call(regexpExec, R, S);
   throw $TypeError('RegExp#exec called on incompatible receiver');
  };
  
  /***/ }),
  /* 155 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var call = __webpack_require__(9);
  var uncurryThis = __webpack_require__(15);
  var requireObjectCoercible = __webpack_require__(17);
  var isCallable = __webpack_require__(22);
  var isNullOrUndefined = __webpack_require__(18);
  var isRegExp = __webpack_require__(156);
  var toString = __webpack_require__(118);
  var getMethod = __webpack_require__(31);
  var getRegExpFlags = __webpack_require__(157);
  var getSubstitution = __webpack_require__(153);
  var wellKnownSymbol = __webpack_require__(35);
  var IS_PURE = __webpack_require__(37);
  var REPLACE = wellKnownSymbol('replace');
  var $TypeError = TypeError;
  var indexOf = uncurryThis(''.indexOf);
  var replace = uncurryThis(''.replace);
  var stringSlice = uncurryThis(''.slice);
  var max = Math.max;
  var stringIndexOf = function (string, searchValue, fromIndex) {
   if (fromIndex > string.length)
    return -1;
   if (searchValue === '')
    return fromIndex;
   return indexOf(string, searchValue, fromIndex);
  };
  $({
   target: 'String',
   proto: true
  }, {
   replaceAll: function replaceAll(searchValue, replaceValue) {
    var O = requireObjectCoercible(this);
    var IS_REG_EXP, flags, replacer, string, searchString, functionalReplace, searchLength, advanceBy, replacement;
    var position = 0;
    var endOfLastMatch = 0;
    var result = '';
    if (!isNullOrUndefined(searchValue)) {
     IS_REG_EXP = isRegExp(searchValue);
     if (IS_REG_EXP) {
      flags = toString(requireObjectCoercible(getRegExpFlags(searchValue)));
      if (!~indexOf(flags, 'g'))
       throw $TypeError('`.replaceAll` does not allow non-global regexes');
     }
     replacer = getMethod(searchValue, REPLACE);
     if (replacer) {
      return call(replacer, searchValue, O, replaceValue);
     } else if (IS_PURE && IS_REG_EXP) {
      return replace(toString(O), searchValue, replaceValue);
     }
    }
    string = toString(O);
    searchString = toString(searchValue);
    functionalReplace = isCallable(replaceValue);
    if (!functionalReplace)
     replaceValue = toString(replaceValue);
    searchLength = searchString.length;
    advanceBy = max(1, searchLength);
    position = stringIndexOf(string, searchString, 0);
    while (position !== -1) {
     replacement = functionalReplace ? toString(replaceValue(searchString, position, string)) : getSubstitution(searchString, string, position, [], undefined, replaceValue);
     result += stringSlice(string, endOfLastMatch, position) + replacement;
     endOfLastMatch = position + searchLength;
     position = stringIndexOf(string, searchString, position + advanceBy);
    }
    if (endOfLastMatch < string.length) {
     result += stringSlice(string, endOfLastMatch);
    }
    return result;
   }
  });
  
  /***/ }),
  /* 156 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var isObject = __webpack_require__(21);
  var classof = __webpack_require__(16);
  var wellKnownSymbol = __webpack_require__(35);
  var MATCH = wellKnownSymbol('match');
  module.exports = function (it) {
   var isRegExp;
   return isObject(it) && ((isRegExp = it[MATCH]) !== undefined ? !!isRegExp : classof(it) === 'RegExp');
  };
  
  /***/ }),
  /* 157 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  var hasOwn = __webpack_require__(40);
  var isPrototypeOf = __webpack_require__(26);
  var regExpFlags = __webpack_require__(138);
  var RegExpPrototype = RegExp.prototype;
  module.exports = function (R) {
   var flags = R.flags;
   return flags === undefined && !('flags' in RegExpPrototype) && !hasOwn(R, 'flags') && isPrototypeOf(RegExpPrototype, R) ? call(regExpFlags, R) : flags;
  };
  
  /***/ }),
  /* 158 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var difference = __webpack_require__(159);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('difference')
  }, { difference: difference });
  
  /***/ }),
  /* 159 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var SetHelpers = __webpack_require__(161);
  var clone = __webpack_require__(162);
  var size = __webpack_require__(165);
  var getSetRecord = __webpack_require__(166);
  var iterateSet = __webpack_require__(163);
  var iterateSimple = __webpack_require__(164);
  var has = SetHelpers.has;
  var remove = SetHelpers.remove;
  module.exports = function difference(other) {
   var O = aSet(this);
   var otherRec = getSetRecord(other);
   var result = clone(O);
   if (size(O) <= otherRec.size)
    iterateSet(O, function (e) {
     if (otherRec.includes(e))
      remove(result, e);
    });
   else
    iterateSimple(otherRec.getIterator(), function (e) {
     if (has(O, e))
      remove(result, e);
    });
   return result;
  };
  
  /***/ }),
  /* 160 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var has = (__webpack_require__(161).has);
  module.exports = function (it) {
   has(it);
   return it;
  };
  
  /***/ }),
  /* 161 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var SetPrototype = Set.prototype;
  module.exports = {
   Set: Set,
   add: uncurryThis(SetPrototype.add),
   has: uncurryThis(SetPrototype.has),
   remove: uncurryThis(SetPrototype['delete']),
   proto: SetPrototype
  };
  
  /***/ }),
  /* 162 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var SetHelpers = __webpack_require__(161);
  var iterate = __webpack_require__(163);
  var Set = SetHelpers.Set;
  var add = SetHelpers.add;
  module.exports = function (set) {
   var result = new Set();
   iterate(set, function (it) {
    add(result, it);
   });
   return result;
  };
  
  /***/ }),
  /* 163 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThis = __webpack_require__(15);
  var iterateSimple = __webpack_require__(164);
  var SetHelpers = __webpack_require__(161);
  var Set = SetHelpers.Set;
  var SetPrototype = SetHelpers.proto;
  var forEach = uncurryThis(SetPrototype.forEach);
  var keys = uncurryThis(SetPrototype.keys);
  var next = keys(new Set()).next;
  module.exports = function (set, fn, interruptible) {
   return interruptible ? iterateSimple({
    iterator: keys(set),
    next: next
   }, fn) : forEach(set, fn);
  };
  
  /***/ }),
  /* 164 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var call = __webpack_require__(9);
  module.exports = function (record, fn, ITERATOR_INSTEAD_OF_RECORD) {
   var iterator = ITERATOR_INSTEAD_OF_RECORD ? record : record.iterator;
   var next = record.next;
   var step, result;
   while (!(step = call(next, iterator)).done) {
    result = fn(step.value);
    if (result !== undefined)
     return result;
   }
  };
  
  /***/ }),
  /* 165 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var uncurryThisAccessor = __webpack_require__(72);
  var SetHelpers = __webpack_require__(161);
  module.exports = uncurryThisAccessor(SetHelpers.proto, 'size', 'get') || function (set) {
   return set.size;
  };
  
  /***/ }),
  /* 166 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aCallable = __webpack_require__(32);
  var anObject = __webpack_require__(48);
  var call = __webpack_require__(9);
  var toIntegerOrInfinity = __webpack_require__(63);
  var getIteratorDirect = __webpack_require__(167);
  var INVALID_SIZE = 'Invalid size';
  var $RangeError = RangeError;
  var $TypeError = TypeError;
  var max = Math.max;
  var SetRecord = function (set, size, has, keys) {
   this.set = set;
   this.size = size;
   this.has = has;
   this.keys = keys;
  };
  SetRecord.prototype = {
   getIterator: function () {
    return getIteratorDirect(anObject(call(this.keys, this.set)));
   },
   includes: function (it) {
    return call(this.has, this.set, it);
   }
  };
  module.exports = function (obj) {
   anObject(obj);
   var numSize = +obj.size;
   if (numSize !== numSize)
    throw $TypeError(INVALID_SIZE);
   var intSize = toIntegerOrInfinity(numSize);
   if (intSize < 0)
    throw $RangeError(INVALID_SIZE);
   return new SetRecord(obj, max(intSize, 0), aCallable(obj.has), aCallable(obj.keys));
  };
  
  /***/ }),
  /* 167 */
  /***/ ((module) => {
  
  
  module.exports = function (obj) {
   return {
    iterator: obj,
    next: obj.next,
    done: false
   };
  };
  
  /***/ }),
  /* 168 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var getBuiltIn = __webpack_require__(25);
  var createSetLike = function (size) {
   return {
    size: size,
    has: function () {
     return false;
    },
    keys: function () {
     return {
      next: function () {
       return { done: true };
      }
     };
    }
   };
  };
  module.exports = function (name) {
   var Set = getBuiltIn('Set');
   try {
    new Set()[name](createSetLike(0));
    try {
     new Set()[name](createSetLike(-1));
     return false;
    } catch (error2) {
     return true;
    }
   } catch (error) {
    return false;
   }
  };
  
  /***/ }),
  /* 169 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var fails = __webpack_require__(8);
  var intersection = __webpack_require__(170);
  var setMethodAcceptSetLike = __webpack_require__(168);
  var INCORRECT = !setMethodAcceptSetLike('intersection') || fails(function () {
   return Array.from(new Set([
    1,
    2,
    3
   ]).intersection(new Set([
    3,
    2
   ]))) !== '3,2';
  });
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: INCORRECT
  }, { intersection: intersection });
  
  /***/ }),
  /* 170 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var SetHelpers = __webpack_require__(161);
  var size = __webpack_require__(165);
  var getSetRecord = __webpack_require__(166);
  var iterateSet = __webpack_require__(163);
  var iterateSimple = __webpack_require__(164);
  var Set = SetHelpers.Set;
  var add = SetHelpers.add;
  var has = SetHelpers.has;
  module.exports = function intersection(other) {
   var O = aSet(this);
   var otherRec = getSetRecord(other);
   var result = new Set();
   if (size(O) > otherRec.size) {
    iterateSimple(otherRec.getIterator(), function (e) {
     if (has(O, e))
      add(result, e);
    });
   } else {
    iterateSet(O, function (e) {
     if (otherRec.includes(e))
      add(result, e);
    });
   }
   return result;
  };
  
  /***/ }),
  /* 171 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var isDisjointFrom = __webpack_require__(172);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('isDisjointFrom')
  }, { isDisjointFrom: isDisjointFrom });
  
  /***/ }),
  /* 172 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var has = (__webpack_require__(161).has);
  var size = __webpack_require__(165);
  var getSetRecord = __webpack_require__(166);
  var iterateSet = __webpack_require__(163);
  var iterateSimple = __webpack_require__(164);
  var iteratorClose = __webpack_require__(108);
  module.exports = function isDisjointFrom(other) {
   var O = aSet(this);
   var otherRec = getSetRecord(other);
   if (size(O) <= otherRec.size)
    return iterateSet(O, function (e) {
     if (otherRec.includes(e))
      return false;
    }, true) !== false;
   var iterator = otherRec.getIterator();
   return iterateSimple(iterator, function (e) {
    if (has(O, e))
     return iteratorClose(iterator, 'normal', false);
   }) !== false;
  };
  
  /***/ }),
  /* 173 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var isSubsetOf = __webpack_require__(174);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('isSubsetOf')
  }, { isSubsetOf: isSubsetOf });
  
  /***/ }),
  /* 174 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var size = __webpack_require__(165);
  var iterate = __webpack_require__(163);
  var getSetRecord = __webpack_require__(166);
  module.exports = function isSubsetOf(other) {
   var O = aSet(this);
   var otherRec = getSetRecord(other);
   if (size(O) > otherRec.size)
    return false;
   return iterate(O, function (e) {
    if (!otherRec.includes(e))
     return false;
   }, true) !== false;
  };
  
  /***/ }),
  /* 175 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var isSupersetOf = __webpack_require__(176);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('isSupersetOf')
  }, { isSupersetOf: isSupersetOf });
  
  /***/ }),
  /* 176 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var has = (__webpack_require__(161).has);
  var size = __webpack_require__(165);
  var getSetRecord = __webpack_require__(166);
  var iterateSimple = __webpack_require__(164);
  var iteratorClose = __webpack_require__(108);
  module.exports = function isSupersetOf(other) {
   var O = aSet(this);
   var otherRec = getSetRecord(other);
   if (size(O) < otherRec.size)
    return false;
   var iterator = otherRec.getIterator();
   return iterateSimple(iterator, function (e) {
    if (!has(O, e))
     return iteratorClose(iterator, 'normal', false);
   }) !== false;
  };
  
  /***/ }),
  /* 177 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var symmetricDifference = __webpack_require__(178);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('symmetricDifference')
  }, { symmetricDifference: symmetricDifference });
  
  /***/ }),
  /* 178 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var SetHelpers = __webpack_require__(161);
  var clone = __webpack_require__(162);
  var getSetRecord = __webpack_require__(166);
  var iterateSimple = __webpack_require__(164);
  var add = SetHelpers.add;
  var has = SetHelpers.has;
  var remove = SetHelpers.remove;
  module.exports = function symmetricDifference(other) {
   var O = aSet(this);
   var keysIter = getSetRecord(other).getIterator();
   var result = clone(O);
   iterateSimple(keysIter, function (e) {
    if (has(O, e))
     remove(result, e);
    else
     add(result, e);
   });
   return result;
  };
  
  /***/ }),
  /* 179 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var union = __webpack_require__(180);
  var setMethodAcceptSetLike = __webpack_require__(168);
  $({
   target: 'Set',
   proto: true,
   real: true,
   forced: !setMethodAcceptSetLike('union')
  }, { union: union });
  
  /***/ }),
  /* 180 */
  /***/ ((module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var aSet = __webpack_require__(160);
  var add = (__webpack_require__(161).add);
  var clone = __webpack_require__(162);
  var getSetRecord = __webpack_require__(166);
  var iterateSimple = __webpack_require__(164);
  module.exports = function union(other) {
   var O = aSet(this);
   var keysIter = getSetRecord(other).getIterator();
   var result = clone(O);
   iterateSimple(keysIter, function (it) {
    add(result, it);
   });
   return result;
  };
  
  /***/ }),
  /* 181 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var toObject = __webpack_require__(41);
  var lengthOfArrayLike = __webpack_require__(65);
  var toIntegerOrInfinity = __webpack_require__(63);
  var addToUnscopables = __webpack_require__(132);
  $({
   target: 'Array',
   proto: true
  }, {
   at: function at(index) {
    var O = toObject(this);
    var len = lengthOfArrayLike(O);
    var relativeIndex = toIntegerOrInfinity(index);
    var k = relativeIndex >= 0 ? relativeIndex : len + relativeIndex;
    return k < 0 || k >= len ? undefined : O[k];
   }
  });
  addToUnscopables('at');
  
  /***/ }),
  /* 182 */
  /***/ ((module) => {
  
  
  
  module.exports = globalThis.pdfjsLib;
  
  /***/ }),
  /* 183 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.compatibilityParams = exports.OptionKind = exports.AppOptions = void 0;
  __webpack_require__(136);
  __webpack_require__(122);
  const compatibilityParams = Object.create(null);
  exports.compatibilityParams = compatibilityParams;
  {
    const userAgent = navigator.userAgent || "";
    const platform = navigator.platform || "";
    const maxTouchPoints = navigator.maxTouchPoints || 1;
    const isAndroid = /Android/.test(userAgent);
    const isIOS = /\b(iPad|iPhone|iPod)(?=;)/.test(userAgent) || platform === "MacIntel" && maxTouchPoints > 1;
    (function checkCanvasSizeLimitation() {
      if (isIOS || isAndroid) {
        compatibilityParams.maxCanvasPixels = 5242880;
      }
    })();
  }
  const OptionKind = {
    VIEWER: 0x02,
    API: 0x04,
    WORKER: 0x08,
    PREFERENCE: 0x80
  };
  exports.OptionKind = OptionKind;
  const defaultOptions = {
    annotationEditorMode: {
      value: 0,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    annotationMode: {
      value: 2,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    cursorToolOnLoad: {
      value: 0,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    defaultZoomDelay: {
      value: 400,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    defaultZoomValue: {
      value: "",
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    disableHistory: {
      value: false,
      kind: OptionKind.VIEWER
    },
    disablePageLabels: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    enablePermissions: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    enablePrintAutoRotate: {
      value: true,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    enableScripting: {
      value: true,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    enableStampEditor: {
      value: true,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    externalLinkRel: {
      value: "noopener noreferrer nofollow",
      kind: OptionKind.VIEWER
    },
    externalLinkTarget: {
      value: 0,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    historyUpdateUrl: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    ignoreDestinationZoom: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    imageResourcesPath: {
      value: "./images/",
      kind: OptionKind.VIEWER
    },
    maxCanvasPixels: {
      value: 16777216,
      kind: OptionKind.VIEWER
    },
    forcePageColors: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    pageColorsBackground: {
      value: "Canvas",
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    pageColorsForeground: {
      value: "CanvasText",
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    pdfBugEnabled: {
      value: false,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    printResolution: {
      value: 150,
      kind: OptionKind.VIEWER
    },
    sidebarViewOnLoad: {
      value: -1,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    scrollModeOnLoad: {
      value: -1,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    spreadModeOnLoad: {
      value: -1,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    textLayerMode: {
      value: 1,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    viewerCssTheme: {
      value: 0,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    viewOnLoad: {
      value: 0,
      kind: OptionKind.VIEWER + OptionKind.PREFERENCE
    },
    cMapPacked: {
      value: true,
      kind: OptionKind.API
    },
    cMapUrl: {
      value: "../web/cmaps/",
      kind: OptionKind.API
    },
    disableAutoFetch: {
      value: false,
      kind: OptionKind.API + OptionKind.PREFERENCE
    },
    disableFontFace: {
      value: false,
      kind: OptionKind.API + OptionKind.PREFERENCE
    },
    disableRange: {
      value: false,
      kind: OptionKind.API + OptionKind.PREFERENCE
    },
    disableStream: {
      value: false,
      kind: OptionKind.API + OptionKind.PREFERENCE
    },
    docBaseUrl: {
      value: "",
      kind: OptionKind.API
    },
    enableXfa: {
      value: true,
      kind: OptionKind.API + OptionKind.PREFERENCE
    },
    fontExtraProperties: {
      value: false,
      kind: OptionKind.API
    },
    isEvalSupported: {
      value: true,
      kind: OptionKind.API
    },
    isOffscreenCanvasSupported: {
      value: true,
      kind: OptionKind.API
    },
    maxImageSize: {
      value: -1,
      kind: OptionKind.API
    },
    pdfBug: {
      value: false,
      kind: OptionKind.API
    },
    standardFontDataUrl: {
      value: "../web/standard_fonts/",
      kind: OptionKind.API
    },
    verbosity: {
      value: 1,
      kind: OptionKind.API
    },
    workerPort: {
      value: null,
      kind: OptionKind.WORKER
    },
    workerSrc: {
      value: "../build/pdf.worker.js",
      kind: OptionKind.WORKER
    }
  };
  {
    defaultOptions.defaultUrl = {
      value: "compressed.tracemonkey-pldi-09.pdf",
      kind: OptionKind.VIEWER
    };
    defaultOptions.disablePreferences = {
      value: false,
      kind: OptionKind.VIEWER
    };
    defaultOptions.locale = {
      value: navigator.language || "en-US",
      kind: OptionKind.VIEWER
    };
    defaultOptions.sandboxBundleSrc = {
      value: "../build/pdf.sandbox.js",
      kind: OptionKind.VIEWER
    };
  }
  const userOptions = Object.create(null);
  class AppOptions {
    constructor() {
      throw new Error("Cannot initialize AppOptions.");
    }
    static get(name) {
      const userOption = userOptions[name];
      if (userOption !== undefined) {
        return userOption;
      }
      const defaultOption = defaultOptions[name];
      if (defaultOption !== undefined) {
        var _compatibilityParams$;
        return (_compatibilityParams$ = compatibilityParams[name]) !== null && _compatibilityParams$ !== void 0 ? _compatibilityParams$ : defaultOption.value;
      }
      return undefined;
    }
    static getAll() {
      let kind = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      const options = Object.create(null);
      for (const name in defaultOptions) {
        var _compatibilityParams$2;
        const defaultOption = defaultOptions[name];
        if (kind) {
          if ((kind & defaultOption.kind) === 0) {
            continue;
          }
          if (kind === OptionKind.PREFERENCE) {
            const value = defaultOption.value,
              valueType = typeof value;
            if (valueType === "boolean" || valueType === "string" || valueType === "number" && Number.isInteger(value)) {
              options[name] = value;
              continue;
            }
            throw new Error(`Invalid type for preference: ${name}`);
          }
        }
        const userOption = userOptions[name];
        options[name] = userOption !== undefined ? userOption : (_compatibilityParams$2 = compatibilityParams[name]) !== null && _compatibilityParams$2 !== void 0 ? _compatibilityParams$2 : defaultOption.value;
      }
      return options;
    }
    static set(name, value) {
      userOptions[name] = value;
    }
    static setAll(options) {
      for (const name in options) {
        userOptions[name] = options[name];
      }
    }
    static remove(name) {
      delete userOptions[name];
    }
  }
  exports.AppOptions = AppOptions;
  {
    AppOptions._hasUserOptions = function () {
      return Object.keys(userOptions).length > 0;
    };
  }
  
  /***/ }),
  /* 184 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.WaitOnType = exports.EventBus = exports.AutomationEventBus = void 0;
  exports.waitOnEventOrTimeout = waitOnEventOrTimeout;
  __webpack_require__(2);
  __webpack_require__(122);
  __webpack_require__(142);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  const WaitOnType = {
    EVENT: "event",
    TIMEOUT: "timeout"
  };
  exports.WaitOnType = WaitOnType;
  function waitOnEventOrTimeout(_ref) {
    let {
      target,
      name,
      delay = 0
    } = _ref;
    return new Promise(function (resolve, reject) {
      if (typeof target !== "object" || !(name && typeof name === "string") || !(Number.isInteger(delay) && delay >= 0)) {
        throw new Error("waitOnEventOrTimeout - invalid parameters.");
      }
      function handler(type) {
        if (target instanceof EventBus) {
          target._off(name, eventHandler);
        } else {
          target.removeEventListener(name, eventHandler);
        }
        if (timeout) {
          clearTimeout(timeout);
        }
        resolve(type);
      }
      const eventHandler = handler.bind(null, WaitOnType.EVENT);
      if (target instanceof EventBus) {
        target._on(name, eventHandler);
      } else {
        target.addEventListener(name, eventHandler);
      }
      const timeoutHandler = handler.bind(null, WaitOnType.TIMEOUT);
      const timeout = setTimeout(timeoutHandler, delay);
    });
  }
  var _listeners = /*#__PURE__*/new WeakMap();
  class EventBus {
    constructor() {
      _classPrivateFieldInitSpec(this, _listeners, {
        writable: true,
        value: Object.create(null)
      });
    }
    on(eventName, listener) {
      let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      this._on(eventName, listener, {
        external: true,
        once: options === null || options === void 0 ? void 0 : options.once
      });
    }
    off(eventName, listener) {
      let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      this._off(eventName, listener, {
        external: true,
        once: options === null || options === void 0 ? void 0 : options.once
      });
    }
    dispatch(eventName, data) {
      const eventListeners = _classPrivateFieldGet(this, _listeners)[eventName];
      if (!eventListeners || eventListeners.length === 0) {
        return;
      }
      let externalListeners;
      for (const {
        listener,
        external,
        once
      } of eventListeners.slice(0)) {
        if (once) {
          this._off(eventName, listener);
        }
        if (external) {
          (externalListeners || (externalListeners = [])).push(listener);
          continue;
        }
        listener(data);
      }
      if (externalListeners) {
        for (const listener of externalListeners) {
          listener(data);
        }
        externalListeners = null;
      }
    }
    _on(eventName, listener) {
      var _classPrivateFieldGet2;
      let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      const eventListeners = (_classPrivateFieldGet2 = _classPrivateFieldGet(this, _listeners))[eventName] || (_classPrivateFieldGet2[eventName] = []);
      eventListeners.push({
        listener,
        external: (options === null || options === void 0 ? void 0 : options.external) === true,
        once: (options === null || options === void 0 ? void 0 : options.once) === true
      });
    }
    _off(eventName, listener) {
      let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      const eventListeners = _classPrivateFieldGet(this, _listeners)[eventName];
      if (!eventListeners) {
        return;
      }
      for (let i = 0, ii = eventListeners.length; i < ii; i++) {
        if (eventListeners[i].listener === listener) {
          eventListeners.splice(i, 1);
          return;
        }
      }
    }
  }
  exports.EventBus = EventBus;
  class AutomationEventBus extends EventBus {
    dispatch(eventName, data) {
      throw new Error("Not implemented: AutomationEventBus.dispatch");
    }
  }
  exports.AutomationEventBus = AutomationEventBus;
  
  /***/ }),
  /* 185 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.SimpleLinkService = exports.PDFLinkService = exports.LinkTarget = void 0;
  __webpack_require__(122);
  __webpack_require__(2);
  __webpack_require__(131);
  __webpack_require__(136);
  __webpack_require__(149);
  __webpack_require__(155);
  __webpack_require__(116);
  __webpack_require__(142);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classStaticPrivateMethodGet(receiver, classConstructor, method) { _classCheckPrivateStaticAccess(receiver, classConstructor); return method; }
  function _classCheckPrivateStaticAccess(receiver, classConstructor) { if (receiver !== classConstructor) { throw new TypeError("Private static access of wrong provenance"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  const DEFAULT_LINK_REL = "noopener noreferrer nofollow";
  const LinkTarget = {
    NONE: 0,
    SELF: 1,
    BLANK: 2,
    PARENT: 3,
    TOP: 4
  };
  exports.LinkTarget = LinkTarget;
  function addLinkAttributes(link) {
    let {
      url,
      target,
      rel,
      enabled = true
    } = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
    if (!url || typeof url !== "string") {
      throw new Error('A valid "url" parameter must provided.');
    }
    if (enabled) {
      link.href = link.title = url;
    } else {
      link.href = "";
      link.title = `Disabled: ${url}`;
      link.onclick = () => {
        return false;
      };
    }
    let targetStr = "";
    switch (target) {
      case LinkTarget.NONE:
        break;
      case LinkTarget.SELF:
        targetStr = "_self";
        break;
      case LinkTarget.BLANK:
        targetStr = "_blank";
        break;
      case LinkTarget.PARENT:
        targetStr = "_parent";
        break;
      case LinkTarget.TOP:
        targetStr = "_top";
        break;
    }
    link.target = targetStr;
    link.rel = typeof rel === "string" ? rel : DEFAULT_LINK_REL;
  }
  var _pagesRefCache = /*#__PURE__*/new WeakMap();
  var _goToDestinationHelper = /*#__PURE__*/new WeakSet();
  class PDFLinkService {
    constructor() {
      let {
        eventBus,
        externalLinkTarget = null,
        externalLinkRel = null,
        ignoreDestinationZoom = false
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      _classPrivateMethodInitSpec(this, _goToDestinationHelper);
      _classPrivateFieldInitSpec(this, _pagesRefCache, {
        writable: true,
        value: new Map()
      });
      this.eventBus = eventBus;
      this.externalLinkTarget = externalLinkTarget;
      this.externalLinkRel = externalLinkRel;
      this.externalLinkEnabled = true;
      this._ignoreDestinationZoom = ignoreDestinationZoom;
      this.baseUrl = null;
      this.pdfDocument = null;
      this.pdfViewer = null;
      this.pdfHistory = null;
    }
    setDocument(pdfDocument) {
      let baseUrl = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      this.baseUrl = baseUrl;
      this.pdfDocument = pdfDocument;
      _classPrivateFieldGet(this, _pagesRefCache).clear();
    }
    setViewer(pdfViewer) {
      this.pdfViewer = pdfViewer;
    }
    setHistory(pdfHistory) {
      this.pdfHistory = pdfHistory;
    }
    get pagesCount() {
      return this.pdfDocument ? this.pdfDocument.numPages : 0;
    }
    get page() {
      return this.pdfViewer.currentPageNumber;
    }
    set page(value) {
      this.pdfViewer.currentPageNumber = value;
    }
    get rotation() {
      return this.pdfViewer.pagesRotation;
    }
    set rotation(value) {
      this.pdfViewer.pagesRotation = value;
    }
    get isInPresentationMode() {
      return this.pdfViewer.isInPresentationMode;
    }
    async goToDestination(dest) {
      if (!this.pdfDocument) {
        return;
      }
      let namedDest, explicitDest;
      if (typeof dest === "string") {
        namedDest = dest;
        explicitDest = await this.pdfDocument.getDestination(dest);
      } else {
        namedDest = null;
        explicitDest = await dest;
      }
      if (!Array.isArray(explicitDest)) {
        console.error(`PDFLinkService.goToDestination: "${explicitDest}" is not ` + `a valid destination array, for dest="${dest}".`);
        return;
      }
      _classPrivateMethodGet(this, _goToDestinationHelper, _goToDestinationHelper2).call(this, dest, namedDest, explicitDest);
    }
    goToPage(val) {
      if (!this.pdfDocument) {
        return;
      }
      const pageNumber = typeof val === "string" && this.pdfViewer.pageLabelToPageNumber(val) || val | 0;
      if (!(Number.isInteger(pageNumber) && pageNumber > 0 && pageNumber <= this.pagesCount)) {
        console.error(`PDFLinkService.goToPage: "${val}" is not a valid page.`);
        return;
      }
      if (this.pdfHistory) {
        this.pdfHistory.pushCurrentPosition();
        this.pdfHistory.pushPage(pageNumber);
      }
      this.pdfViewer.scrollPageIntoView({
        pageNumber
      });
    }
    addLinkAttributes(link, url) {
      let newWindow = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
      addLinkAttributes(link, {
        url,
        target: newWindow ? LinkTarget.BLANK : this.externalLinkTarget,
        rel: this.externalLinkRel,
        enabled: this.externalLinkEnabled
      });
    }
    getDestinationHash(dest) {
      if (typeof dest === "string") {
        if (dest.length > 0) {
          return this.getAnchorUrl("#" + escape(dest));
        }
      } else if (Array.isArray(dest)) {
        const str = JSON.stringify(dest);
        if (str.length > 0) {
          return this.getAnchorUrl("#" + escape(str));
        }
      }
      return this.getAnchorUrl("");
    }
    getAnchorUrl(anchor) {
      return this.baseUrl ? this.baseUrl + anchor : anchor;
    }
    setHash(hash) {
      if (!this.pdfDocument) {
        return;
      }
      let pageNumber, dest;
      if (hash.includes("=")) {
        const params = (0, _ui_utils.parseQueryString)(hash);
        if (params.has("search")) {
          const query = params.get("search").replaceAll('"', ""),
            phrase = params.get("phrase") === "true";
          this.eventBus.dispatch("findfromurlhash", {
            source: this,
            query: phrase ? query : query.match(/\S+/g)
          });
        }
        if (params.has("page")) {
          pageNumber = params.get("page") | 0 || 1;
        }
        if (params.has("zoom")) {
          const zoomArgs = params.get("zoom").split(",");
          const zoomArg = zoomArgs[0];
          const zoomArgNumber = parseFloat(zoomArg);
          if (!zoomArg.includes("Fit")) {
            dest = [null, {
              name: "XYZ"
            }, zoomArgs.length > 1 ? zoomArgs[1] | 0 : null, zoomArgs.length > 2 ? zoomArgs[2] | 0 : null, zoomArgNumber ? zoomArgNumber / 100 : zoomArg];
          } else if (zoomArg === "Fit" || zoomArg === "FitB") {
            dest = [null, {
              name: zoomArg
            }];
          } else if (zoomArg === "FitH" || zoomArg === "FitBH" || zoomArg === "FitV" || zoomArg === "FitBV") {
            dest = [null, {
              name: zoomArg
            }, zoomArgs.length > 1 ? zoomArgs[1] | 0 : null];
          } else if (zoomArg === "FitR") {
            if (zoomArgs.length !== 5) {
              console.error('PDFLinkService.setHash: Not enough parameters for "FitR".');
            } else {
              dest = [null, {
                name: zoomArg
              }, zoomArgs[1] | 0, zoomArgs[2] | 0, zoomArgs[3] | 0, zoomArgs[4] | 0];
            }
          } else {
            console.error(`PDFLinkService.setHash: "${zoomArg}" is not a valid zoom value.`);
          }
        }
        if (dest) {
          this.pdfViewer.scrollPageIntoView({
            pageNumber: pageNumber || this.page,
            destArray: dest,
            allowNegativeOffset: true
          });
        } else if (pageNumber) {
          this.page = pageNumber;
        }
        if (params.has("pagemode")) {
          this.eventBus.dispatch("pagemode", {
            source: this,
            mode: params.get("pagemode")
          });
        }
        if (params.has("nameddest")) {
          this.goToDestination(params.get("nameddest"));
        }
      } else {
        dest = unescape(hash);
        try {
          dest = JSON.parse(dest);
          if (!Array.isArray(dest)) {
            dest = dest.toString();
          }
        } catch {}
        if (typeof dest === "string" || _classStaticPrivateMethodGet(PDFLinkService, PDFLinkService, _isValidExplicitDestination).call(PDFLinkService, dest)) {
          this.goToDestination(dest);
          return;
        }
        console.error(`PDFLinkService.setHash: "${unescape(hash)}" is not a valid destination.`);
      }
    }
    executeNamedAction(action) {
      var _this$pdfHistory, _this$pdfHistory2;
      switch (action) {
        case "GoBack":
          (_this$pdfHistory = this.pdfHistory) === null || _this$pdfHistory === void 0 || _this$pdfHistory.back();
          break;
        case "GoForward":
          (_this$pdfHistory2 = this.pdfHistory) === null || _this$pdfHistory2 === void 0 || _this$pdfHistory2.forward();
          break;
        case "NextPage":
          this.pdfViewer.nextPage();
          break;
        case "PrevPage":
          this.pdfViewer.previousPage();
          break;
        case "LastPage":
          this.page = this.pagesCount;
          break;
        case "FirstPage":
          this.page = 1;
          break;
        default:
          break;
      }
      this.eventBus.dispatch("namedaction", {
        source: this,
        action
      });
    }
    async executeSetOCGState(action) {
      const pdfDocument = this.pdfDocument;
      const optionalContentConfig = await this.pdfViewer.optionalContentConfigPromise;
      if (pdfDocument !== this.pdfDocument) {
        return;
      }
      let operator;
      for (const elem of action.state) {
        switch (elem) {
          case "ON":
          case "OFF":
          case "Toggle":
            operator = elem;
            continue;
        }
        switch (operator) {
          case "ON":
            optionalContentConfig.setVisibility(elem, true);
            break;
          case "OFF":
            optionalContentConfig.setVisibility(elem, false);
            break;
          case "Toggle":
            const group = optionalContentConfig.getGroup(elem);
            if (group) {
              optionalContentConfig.setVisibility(elem, !group.visible);
            }
            break;
        }
      }
      this.pdfViewer.optionalContentConfigPromise = Promise.resolve(optionalContentConfig);
    }
    cachePageRef(pageNum, pageRef) {
      if (!pageRef) {
        return;
      }
      const refStr = pageRef.gen === 0 ? `${pageRef.num}R` : `${pageRef.num}R${pageRef.gen}`;
      _classPrivateFieldGet(this, _pagesRefCache).set(refStr, pageNum);
    }
    _cachedPageNumber(pageRef) {
      if (!pageRef) {
        return null;
      }
      const refStr = pageRef.gen === 0 ? `${pageRef.num}R` : `${pageRef.num}R${pageRef.gen}`;
      return _classPrivateFieldGet(this, _pagesRefCache).get(refStr) || null;
    }
  }
  exports.PDFLinkService = PDFLinkService;
  function _goToDestinationHelper2(rawDest) {
    let namedDest = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    let explicitDest = arguments.length > 2 ? arguments[2] : undefined;
    const destRef = explicitDest[0];
    let pageNumber;
    if (typeof destRef === "object" && destRef !== null) {
      pageNumber = this._cachedPageNumber(destRef);
      if (!pageNumber) {
        this.pdfDocument.getPageIndex(destRef).then(pageIndex => {
          this.cachePageRef(pageIndex + 1, destRef);
          _classPrivateMethodGet(this, _goToDestinationHelper, _goToDestinationHelper2).call(this, rawDest, namedDest, explicitDest);
        }).catch(() => {
          console.error(`PDFLinkService.#goToDestinationHelper: "${destRef}" is not ` + `a valid page reference, for dest="${rawDest}".`);
        });
        return;
      }
    } else if (Number.isInteger(destRef)) {
      pageNumber = destRef + 1;
    } else {
      console.error(`PDFLinkService.#goToDestinationHelper: "${destRef}" is not ` + `a valid destination reference, for dest="${rawDest}".`);
      return;
    }
    if (!pageNumber || pageNumber < 1 || pageNumber > this.pagesCount) {
      console.error(`PDFLinkService.#goToDestinationHelper: "${pageNumber}" is not ` + `a valid page number, for dest="${rawDest}".`);
      return;
    }
    if (this.pdfHistory) {
      this.pdfHistory.pushCurrentPosition();
      this.pdfHistory.push({
        namedDest,
        explicitDest,
        pageNumber
      });
    }
    this.pdfViewer.scrollPageIntoView({
      pageNumber,
      destArray: explicitDest,
      ignoreDestinationZoom: this._ignoreDestinationZoom
    });
  }
  function _isValidExplicitDestination(dest) {
    if (!Array.isArray(dest)) {
      return false;
    }
    const destLength = dest.length;
    if (destLength < 2) {
      return false;
    }
    const page = dest[0];
    if (!(typeof page === "object" && Number.isInteger(page.num) && Number.isInteger(page.gen)) && !(Number.isInteger(page) && page >= 0)) {
      return false;
    }
    const zoom = dest[1];
    if (!(typeof zoom === "object" && typeof zoom.name === "string")) {
      return false;
    }
    let allowNull = true;
    switch (zoom.name) {
      case "XYZ":
        if (destLength !== 5) {
          return false;
        }
        break;
      case "Fit":
      case "FitB":
        return destLength === 2;
      case "FitH":
      case "FitBH":
      case "FitV":
      case "FitBV":
        if (destLength !== 3) {
          return false;
        }
        break;
      case "FitR":
        if (destLength !== 6) {
          return false;
        }
        allowNull = false;
        break;
      default:
        return false;
    }
    for (let i = 2; i < destLength; i++) {
      const param = dest[i];
      if (!(typeof param === "number" || allowNull && param === null)) {
        return false;
      }
    }
    return true;
  }
  class SimpleLinkService {
    constructor() {
      this.externalLinkEnabled = true;
    }
    get pagesCount() {
      return 0;
    }
    get page() {
      return 0;
    }
    set page(value) {}
    get rotation() {
      return 0;
    }
    set rotation(value) {}
    get isInPresentationMode() {
      return false;
    }
    async goToDestination(dest) {}
    goToPage(val) {}
    addLinkAttributes(link, url) {
      let newWindow = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
      addLinkAttributes(link, {
        url,
        enabled: this.externalLinkEnabled
      });
    }
    getDestinationHash(dest) {
      return "#";
    }
    getAnchorUrl(hash) {
      return "#";
    }
    setHash(hash) {}
    executeNamedAction(action) {}
    executeSetOCGState(action) {}
    cachePageRef(pageNum, pageRef) {}
  }
  exports.SimpleLinkService = SimpleLinkService;
  
  /***/ }),
  /* 186 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.AltTextManager = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _boundUpdateUIState = /*#__PURE__*/new WeakMap();
  var _boundSetPosition = /*#__PURE__*/new WeakMap();
  var _boundOnClick = /*#__PURE__*/new WeakMap();
  var _currentEditor = /*#__PURE__*/new WeakMap();
  var _cancelButton = /*#__PURE__*/new WeakMap();
  var _dialog = /*#__PURE__*/new WeakMap();
  var _eventBus = /*#__PURE__*/new WeakMap();
  var _hasUsedPointer = /*#__PURE__*/new WeakMap();
  var _optionDescription = /*#__PURE__*/new WeakMap();
  var _optionDecorative = /*#__PURE__*/new WeakMap();
  var _overlayManager = /*#__PURE__*/new WeakMap();
  var _saveButton = /*#__PURE__*/new WeakMap();
  var _textarea = /*#__PURE__*/new WeakMap();
  var _uiManager = /*#__PURE__*/new WeakMap();
  var _previousAltText = /*#__PURE__*/new WeakMap();
  var _svgElement = /*#__PURE__*/new WeakMap();
  var _rectElement = /*#__PURE__*/new WeakMap();
  var _container = /*#__PURE__*/new WeakMap();
  var _telemetryData = /*#__PURE__*/new WeakMap();
  var _createSVGElement = /*#__PURE__*/new WeakSet();
  var _setPosition = /*#__PURE__*/new WeakSet();
  var _finish = /*#__PURE__*/new WeakSet();
  var _close = /*#__PURE__*/new WeakSet();
  var _updateUIState = /*#__PURE__*/new WeakSet();
  var _save = /*#__PURE__*/new WeakSet();
  var _onClick = /*#__PURE__*/new WeakSet();
  var _removeOnClickListeners = /*#__PURE__*/new WeakSet();
  class AltTextManager {
    constructor(_ref, container, overlayManager, eventBus) {
      let {
        dialog: _dialog2,
        optionDescription,
        optionDecorative,
        textarea,
        cancelButton,
        saveButton
      } = _ref;
      _classPrivateMethodInitSpec(this, _removeOnClickListeners);
      _classPrivateMethodInitSpec(this, _onClick);
      _classPrivateMethodInitSpec(this, _save);
      _classPrivateMethodInitSpec(this, _updateUIState);
      _classPrivateMethodInitSpec(this, _close);
      _classPrivateMethodInitSpec(this, _finish);
      _classPrivateMethodInitSpec(this, _setPosition);
      _classPrivateMethodInitSpec(this, _createSVGElement);
      _classPrivateFieldInitSpec(this, _boundUpdateUIState, {
        writable: true,
        value: _classPrivateMethodGet(this, _updateUIState, _updateUIState2).bind(this)
      });
      _classPrivateFieldInitSpec(this, _boundSetPosition, {
        writable: true,
        value: _classPrivateMethodGet(this, _setPosition, _setPosition2).bind(this)
      });
      _classPrivateFieldInitSpec(this, _boundOnClick, {
        writable: true,
        value: _classPrivateMethodGet(this, _onClick, _onClick2).bind(this)
      });
      _classPrivateFieldInitSpec(this, _currentEditor, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _cancelButton, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _dialog, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _eventBus, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _hasUsedPointer, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _optionDescription, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _optionDecorative, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _overlayManager, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _saveButton, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _textarea, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _uiManager, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _previousAltText, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _svgElement, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _rectElement, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _container, {
        writable: true,
        value: void 0
      });
      _classPrivateFieldInitSpec(this, _telemetryData, {
        writable: true,
        value: null
      });
      _classPrivateFieldSet(this, _dialog, _dialog2);
      _classPrivateFieldSet(this, _optionDescription, optionDescription);
      _classPrivateFieldSet(this, _optionDecorative, optionDecorative);
      _classPrivateFieldSet(this, _textarea, textarea);
      _classPrivateFieldSet(this, _cancelButton, cancelButton);
      _classPrivateFieldSet(this, _saveButton, saveButton);
      _classPrivateFieldSet(this, _overlayManager, overlayManager);
      _classPrivateFieldSet(this, _eventBus, eventBus);
      _classPrivateFieldSet(this, _container, container);
      _dialog2.addEventListener("close", _classPrivateMethodGet(this, _close, _close2).bind(this));
      _dialog2.addEventListener("contextmenu", event => {
        if (event.target !== _classPrivateFieldGet(this, _textarea)) {
          event.preventDefault();
        }
      });
      cancelButton.addEventListener("click", _classPrivateMethodGet(this, _finish, _finish2).bind(this));
      saveButton.addEventListener("click", _classPrivateMethodGet(this, _save, _save2).bind(this));
      optionDescription.addEventListener("change", _classPrivateFieldGet(this, _boundUpdateUIState));
      optionDecorative.addEventListener("change", _classPrivateFieldGet(this, _boundUpdateUIState));
      _classPrivateFieldGet(this, _overlayManager).register(_dialog2);
    }
    get _elements() {
      return (0, _pdfjsLib.shadow)(this, "_elements", [_classPrivateFieldGet(this, _optionDescription), _classPrivateFieldGet(this, _optionDecorative), _classPrivateFieldGet(this, _textarea), _classPrivateFieldGet(this, _saveButton), _classPrivateFieldGet(this, _cancelButton)]);
    }
    async editAltText(uiManager, editor) {
      if (_classPrivateFieldGet(this, _currentEditor) || !editor) {
        return;
      }
      _classPrivateMethodGet(this, _createSVGElement, _createSVGElement2).call(this);
      _classPrivateFieldSet(this, _hasUsedPointer, false);
      for (const element of this._elements) {
        element.addEventListener("click", _classPrivateFieldGet(this, _boundOnClick));
      }
      const {
        altText,
        decorative
      } = editor.altTextData;
      if (decorative === true) {
        _classPrivateFieldGet(this, _optionDecorative).checked = true;
        _classPrivateFieldGet(this, _optionDescription).checked = false;
      } else {
        _classPrivateFieldGet(this, _optionDecorative).checked = false;
        _classPrivateFieldGet(this, _optionDescription).checked = true;
      }
      _classPrivateFieldSet(this, _previousAltText, _classPrivateFieldGet(this, _textarea).value = (altText === null || altText === void 0 ? void 0 : altText.trim()) || "");
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this);
      _classPrivateFieldSet(this, _currentEditor, editor);
      _classPrivateFieldSet(this, _uiManager, uiManager);
      _classPrivateFieldGet(this, _uiManager).removeEditListeners();
      _classPrivateFieldGet(this, _eventBus)._on("resize", _classPrivateFieldGet(this, _boundSetPosition));
      try {
        await _classPrivateFieldGet(this, _overlayManager).open(_classPrivateFieldGet(this, _dialog));
        _classPrivateMethodGet(this, _setPosition, _setPosition2).call(this);
      } catch (ex) {
        _classPrivateMethodGet(this, _close, _close2).call(this);
        throw ex;
      }
    }
    destroy() {
      var _classPrivateFieldGet2;
      _classPrivateFieldSet(this, _uiManager, null);
      _classPrivateMethodGet(this, _finish, _finish2).call(this);
      (_classPrivateFieldGet2 = _classPrivateFieldGet(this, _svgElement)) === null || _classPrivateFieldGet2 === void 0 || _classPrivateFieldGet2.remove();
      _classPrivateFieldSet(this, _svgElement, _classPrivateFieldSet(this, _rectElement, null));
    }
  }
  exports.AltTextManager = AltTextManager;
  function _createSVGElement2() {
    if (_classPrivateFieldGet(this, _svgElement)) {
      return;
    }
    const svgFactory = new _pdfjsLib.DOMSVGFactory();
    const svg = _classPrivateFieldSet(this, _svgElement, svgFactory.createElement("svg"));
    svg.setAttribute("width", "0");
    svg.setAttribute("height", "0");
    const defs = svgFactory.createElement("defs");
    svg.append(defs);
    const mask = svgFactory.createElement("mask");
    defs.append(mask);
    mask.setAttribute("id", "alttext-manager-mask");
    mask.setAttribute("maskContentUnits", "objectBoundingBox");
    let rect = svgFactory.createElement("rect");
    mask.append(rect);
    rect.setAttribute("fill", "white");
    rect.setAttribute("width", "1");
    rect.setAttribute("height", "1");
    rect.setAttribute("x", "0");
    rect.setAttribute("y", "0");
    rect = _classPrivateFieldSet(this, _rectElement, svgFactory.createElement("rect"));
    mask.append(rect);
    rect.setAttribute("fill", "black");
    _classPrivateFieldGet(this, _dialog).append(svg);
  }
  function _setPosition2() {
    if (!_classPrivateFieldGet(this, _currentEditor)) {
      return;
    }
    const dialog = _classPrivateFieldGet(this, _dialog);
    const {
      style
    } = dialog;
    const {
      x: containerX,
      y: containerY,
      width: containerW,
      height: containerH
    } = _classPrivateFieldGet(this, _container).getBoundingClientRect();
    const {
      innerWidth: windowW,
      innerHeight: windowH
    } = window;
    const {
      width: dialogW,
      height: dialogH
    } = dialog.getBoundingClientRect();
    const {
      x,
      y,
      width,
      height
    } = _classPrivateFieldGet(this, _currentEditor).getClientDimensions();
    const MARGIN = 10;
    const isLTR = _classPrivateFieldGet(this, _uiManager).direction === "ltr";
    const xs = Math.max(x, containerX);
    const xe = Math.min(x + width, containerX + containerW);
    const ys = Math.max(y, containerY);
    const ye = Math.min(y + height, containerY + containerH);
    _classPrivateFieldGet(this, _rectElement).setAttribute("width", `${(xe - xs) / windowW}`);
    _classPrivateFieldGet(this, _rectElement).setAttribute("height", `${(ye - ys) / windowH}`);
    _classPrivateFieldGet(this, _rectElement).setAttribute("x", `${xs / windowW}`);
    _classPrivateFieldGet(this, _rectElement).setAttribute("y", `${ys / windowH}`);
    let left = null;
    let top = Math.max(y, 0);
    top += Math.min(windowH - (top + dialogH), 0);
    if (isLTR) {
      if (x + width + MARGIN + dialogW < windowW) {
        left = x + width + MARGIN;
      } else if (x > dialogW + MARGIN) {
        left = x - dialogW - MARGIN;
      }
    } else if (x > dialogW + MARGIN) {
      left = x - dialogW - MARGIN;
    } else if (x + width + MARGIN + dialogW < windowW) {
      left = x + width + MARGIN;
    }
    if (left === null) {
      top = null;
      left = Math.max(x, 0);
      left += Math.min(windowW - (left + dialogW), 0);
      if (y > dialogH + MARGIN) {
        top = y - dialogH - MARGIN;
      } else if (y + height + MARGIN + dialogH < windowH) {
        top = y + height + MARGIN;
      }
    }
    if (top !== null) {
      dialog.classList.add("positioned");
      if (isLTR) {
        style.left = `${left}px`;
      } else {
        style.right = `${windowW - left - dialogW}px`;
      }
      style.top = `${top}px`;
    } else {
      dialog.classList.remove("positioned");
      style.left = "";
      style.top = "";
    }
  }
  function _finish2() {
    if (_classPrivateFieldGet(this, _overlayManager).active === _classPrivateFieldGet(this, _dialog)) {
      _classPrivateFieldGet(this, _overlayManager).close(_classPrivateFieldGet(this, _dialog));
    }
  }
  function _close2() {
    var _classPrivateFieldGet3;
    _classPrivateFieldGet(this, _eventBus).dispatch("reporttelemetry", {
      source: this,
      details: {
        type: "editing",
        subtype: _classPrivateFieldGet(this, _currentEditor).editorType,
        data: _classPrivateFieldGet(this, _telemetryData) || {
          action: "alt_text_cancel",
          alt_text_keyboard: !_classPrivateFieldGet(this, _hasUsedPointer)
        }
      }
    });
    _classPrivateFieldSet(this, _telemetryData, null);
    _classPrivateMethodGet(this, _removeOnClickListeners, _removeOnClickListeners2).call(this);
    (_classPrivateFieldGet3 = _classPrivateFieldGet(this, _uiManager)) === null || _classPrivateFieldGet3 === void 0 || _classPrivateFieldGet3.addEditListeners();
    _classPrivateFieldGet(this, _eventBus)._off("resize", _classPrivateFieldGet(this, _boundSetPosition));
    _classPrivateFieldSet(this, _currentEditor, null);
    _classPrivateFieldSet(this, _uiManager, null);
  }
  function _updateUIState2() {
    _classPrivateFieldGet(this, _textarea).disabled = _classPrivateFieldGet(this, _optionDecorative).checked;
  }
  function _save2() {
    const altText = _classPrivateFieldGet(this, _textarea).value.trim();
    const decorative = _classPrivateFieldGet(this, _optionDecorative).checked;
    _classPrivateFieldGet(this, _currentEditor).altTextData = {
      altText,
      decorative
    };
    _classPrivateFieldSet(this, _telemetryData, {
      action: "alt_text_save",
      alt_text_description: !!altText,
      alt_text_edit: !!_classPrivateFieldGet(this, _previousAltText) && _classPrivateFieldGet(this, _previousAltText) !== altText,
      alt_text_decorative: decorative,
      alt_text_keyboard: !_classPrivateFieldGet(this, _hasUsedPointer)
    });
    _classPrivateMethodGet(this, _finish, _finish2).call(this);
  }
  function _onClick2(evt) {
    if (evt.detail === 0) {
      return;
    }
    _classPrivateFieldSet(this, _hasUsedPointer, true);
    _classPrivateMethodGet(this, _removeOnClickListeners, _removeOnClickListeners2).call(this);
  }
  function _removeOnClickListeners2() {
    for (const element of this._elements) {
      element.removeEventListener("click", _classPrivateFieldGet(this, _boundOnClick));
    }
  }
  
  /***/ }),
  /* 187 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.AnnotationEditorParams = void 0;
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _bindListeners = /*#__PURE__*/new WeakSet();
  class AnnotationEditorParams {
    constructor(options, eventBus) {
      _classPrivateMethodInitSpec(this, _bindListeners);
      this.eventBus = eventBus;
      _classPrivateMethodGet(this, _bindListeners, _bindListeners2).call(this, options);
    }
  }
  exports.AnnotationEditorParams = AnnotationEditorParams;
  function _bindListeners2(_ref) {
    let {
      editorFreeTextFontSize,
      editorFreeTextColor,
      editorInkColor,
      editorInkThickness,
      editorInkOpacity,
      editorStampAddImage
    } = _ref;
    const dispatchEvent = (typeStr, value) => {
      this.eventBus.dispatch("switchannotationeditorparams", {
        source: this,
        type: _pdfjsLib.AnnotationEditorParamsType[typeStr],
        value
      });
    };
    editorFreeTextFontSize.addEventListener("input", function () {
      dispatchEvent("FREETEXT_SIZE", this.valueAsNumber);
    });
    editorFreeTextColor.addEventListener("input", function () {
      dispatchEvent("FREETEXT_COLOR", this.value);
    });
    editorInkColor.addEventListener("input", function () {
      dispatchEvent("INK_COLOR", this.value);
    });
    editorInkThickness.addEventListener("input", function () {
      dispatchEvent("INK_THICKNESS", this.valueAsNumber);
    });
    editorInkOpacity.addEventListener("input", function () {
      dispatchEvent("INK_OPACITY", this.valueAsNumber);
    });
    editorStampAddImage.addEventListener("click", () => {
      dispatchEvent("CREATE");
    });
    this.eventBus._on("annotationeditorparamschanged", evt => {
      for (const [type, value] of evt.details) {
        switch (type) {
          case _pdfjsLib.AnnotationEditorParamsType.FREETEXT_SIZE:
            editorFreeTextFontSize.value = value;
            break;
          case _pdfjsLib.AnnotationEditorParamsType.FREETEXT_COLOR:
            editorFreeTextColor.value = value;
            break;
          case _pdfjsLib.AnnotationEditorParamsType.INK_COLOR:
            editorInkColor.value = value;
            break;
          case _pdfjsLib.AnnotationEditorParamsType.INK_THICKNESS:
            editorInkThickness.value = value;
            break;
          case _pdfjsLib.AnnotationEditorParamsType.INK_OPACITY:
            editorInkOpacity.value = value;
            break;
        }
      }
    });
  }
  
  /***/ }),
  /* 188 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.OverlayManager = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  var _overlays = /*#__PURE__*/new WeakMap();
  var _active = /*#__PURE__*/new WeakMap();
  class OverlayManager {
    constructor() {
      _classPrivateFieldInitSpec(this, _overlays, {
        writable: true,
        value: new WeakMap()
      });
      _classPrivateFieldInitSpec(this, _active, {
        writable: true,
        value: null
      });
    }
    get active() {
      return _classPrivateFieldGet(this, _active);
    }
    async register(dialog) {
      let canForceClose = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      if (typeof dialog !== "object") {
        throw new Error("Not enough parameters.");
      } else if (_classPrivateFieldGet(this, _overlays).has(dialog)) {
        throw new Error("The overlay is already registered.");
      }
      _classPrivateFieldGet(this, _overlays).set(dialog, {
        canForceClose
      });
      dialog.addEventListener("cancel", evt => {
        _classPrivateFieldSet(this, _active, null);
      });
    }
    async open(dialog) {
      if (!_classPrivateFieldGet(this, _overlays).has(dialog)) {
        throw new Error("The overlay does not exist.");
      } else if (_classPrivateFieldGet(this, _active)) {
        if (_classPrivateFieldGet(this, _active) === dialog) {
          throw new Error("The overlay is already active.");
        } else if (_classPrivateFieldGet(this, _overlays).get(dialog).canForceClose) {
          await this.close();
        } else {
          throw new Error("Another overlay is currently active.");
        }
      }
      _classPrivateFieldSet(this, _active, dialog);
      dialog.showModal();
    }
    async close() {
      let dialog = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : _classPrivateFieldGet(this, _active);
      if (!_classPrivateFieldGet(this, _overlays).has(dialog)) {
        throw new Error("The overlay does not exist.");
      } else if (!_classPrivateFieldGet(this, _active)) {
        throw new Error("The overlay is currently not active.");
      } else if (_classPrivateFieldGet(this, _active) !== dialog) {
        throw new Error("Another overlay is currently active.");
      }
      dialog.close();
      _classPrivateFieldSet(this, _active, null);
    }
  }
  exports.OverlayManager = OverlayManager;
  
  /***/ }),
  /* 189 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PasswordPrompt = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _activeCapability = /*#__PURE__*/new WeakMap();
  var _updateCallback = /*#__PURE__*/new WeakMap();
  var _reason = /*#__PURE__*/new WeakMap();
  var _verify = /*#__PURE__*/new WeakSet();
  var _cancel = /*#__PURE__*/new WeakSet();
  var _invokeCallback = /*#__PURE__*/new WeakSet();
  class PasswordPrompt {
    constructor(options, overlayManager, l10n) {
      let isViewerEmbedded = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;
      _classPrivateMethodInitSpec(this, _invokeCallback);
      _classPrivateMethodInitSpec(this, _cancel);
      _classPrivateMethodInitSpec(this, _verify);
      _classPrivateFieldInitSpec(this, _activeCapability, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _updateCallback, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _reason, {
        writable: true,
        value: null
      });
      this.dialog = options.dialog;
      this.label = options.label;
      this.input = options.input;
      this.submitButton = options.submitButton;
      this.cancelButton = options.cancelButton;
      this.overlayManager = overlayManager;
      this.l10n = l10n;
      this._isViewerEmbedded = isViewerEmbedded;
      this.submitButton.addEventListener("click", _classPrivateMethodGet(this, _verify, _verify2).bind(this));
      this.cancelButton.addEventListener("click", this.close.bind(this));
      this.input.addEventListener("keydown", e => {
        if (e.keyCode === 13) {
          _classPrivateMethodGet(this, _verify, _verify2).call(this);
        }
      });
      this.overlayManager.register(this.dialog, true);
      this.dialog.addEventListener("close", _classPrivateMethodGet(this, _cancel, _cancel2).bind(this));
    }
    async open() {
      if (_classPrivateFieldGet(this, _activeCapability)) {
        await _classPrivateFieldGet(this, _activeCapability).promise;
      }
      _classPrivateFieldSet(this, _activeCapability, new _pdfjsLib.PromiseCapability());
      try {
        await this.overlayManager.open(this.dialog);
      } catch (ex) {
        _classPrivateFieldGet(this, _activeCapability).resolve();
        throw ex;
      }
      const passwordIncorrect = _classPrivateFieldGet(this, _reason) === _pdfjsLib.PasswordResponses.INCORRECT_PASSWORD;
      if (!this._isViewerEmbedded || passwordIncorrect) {
        this.input.focus();
      }
      this.label.textContent = await this.l10n.get(`password_${passwordIncorrect ? "invalid" : "label"}`);
    }
    async close() {
      if (this.overlayManager.active === this.dialog) {
        this.overlayManager.close(this.dialog);
      }
    }
    async setUpdateCallback(updateCallback, reason) {
      if (_classPrivateFieldGet(this, _activeCapability)) {
        await _classPrivateFieldGet(this, _activeCapability).promise;
      }
      _classPrivateFieldSet(this, _updateCallback, updateCallback);
      _classPrivateFieldSet(this, _reason, reason);
    }
  }
  exports.PasswordPrompt = PasswordPrompt;
  function _verify2() {
    const password = this.input.value;
    if ((password === null || password === void 0 ? void 0 : password.length) > 0) {
      _classPrivateMethodGet(this, _invokeCallback, _invokeCallback2).call(this, password);
    }
  }
  function _cancel2() {
    _classPrivateMethodGet(this, _invokeCallback, _invokeCallback2).call(this, new Error("PasswordPrompt cancelled."));
    _classPrivateFieldGet(this, _activeCapability).resolve();
  }
  function _invokeCallback2(password) {
    if (!_classPrivateFieldGet(this, _updateCallback)) {
      return;
    }
    this.close();
    this.input.value = "";
    _classPrivateFieldGet(this, _updateCallback).call(this, password);
    _classPrivateFieldSet(this, _updateCallback, null);
  }
  
  /***/ }),
  /* 190 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFAttachmentViewer = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _base_tree_viewer = __webpack_require__(191);
  var _event_utils = __webpack_require__(184);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _appendAttachment = /*#__PURE__*/new WeakSet();
  class PDFAttachmentViewer extends _base_tree_viewer.BaseTreeViewer {
    constructor(options) {
      super(options);
      _classPrivateMethodInitSpec(this, _appendAttachment);
      this.downloadManager = options.downloadManager;
      this.eventBus._on("fileattachmentannotation", _classPrivateMethodGet(this, _appendAttachment, _appendAttachment2).bind(this));
    }
    reset() {
      let keepRenderedCapability = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      super.reset();
      this._attachments = null;
      if (!keepRenderedCapability) {
        this._renderedCapability = new _pdfjsLib.PromiseCapability();
      }
      this._pendingDispatchEvent = false;
    }
    async _dispatchEvent(attachmentsCount) {
      this._renderedCapability.resolve();
      if (attachmentsCount === 0 && !this._pendingDispatchEvent) {
        this._pendingDispatchEvent = true;
        await (0, _event_utils.waitOnEventOrTimeout)({
          target: this.eventBus,
          name: "annotationlayerrendered",
          delay: 1000
        });
        if (!this._pendingDispatchEvent) {
          return;
        }
      }
      this._pendingDispatchEvent = false;
      this.eventBus.dispatch("attachmentsloaded", {
        source: this,
        attachmentsCount
      });
    }
    _bindLink(element, _ref) {
      let {
        content,
        filename
      } = _ref;
      element.onclick = () => {
        this.downloadManager.openOrDownloadData(element, content, filename);
        return false;
      };
    }
    render(_ref2) {
      let {
        attachments,
        keepRenderedCapability = false
      } = _ref2;
      if (this._attachments) {
        this.reset(keepRenderedCapability);
      }
      this._attachments = attachments || null;
      if (!attachments) {
        this._dispatchEvent(0);
        return;
      }
      const fragment = document.createDocumentFragment();
      let attachmentsCount = 0;
      for (const name in attachments) {
        const item = attachments[name];
        const content = item.content,
          filename = (0, _pdfjsLib.getFilenameFromUrl)(item.filename, true);
        const div = document.createElement("div");
        div.className = "treeItem";
        const element = document.createElement("a");
        this._bindLink(element, {
          content,
          filename
        });
        element.textContent = this._normalizeTextContent(filename);
        div.append(element);
        fragment.append(div);
        attachmentsCount++;
      }
      this._finishRendering(fragment, attachmentsCount);
    }
  }
  exports.PDFAttachmentViewer = PDFAttachmentViewer;
  function _appendAttachment2(_ref3) {
    let {
      filename,
      content
    } = _ref3;
    const renderedPromise = this._renderedCapability.promise;
    renderedPromise.then(() => {
      if (renderedPromise !== this._renderedCapability.promise) {
        return;
      }
      const attachments = this._attachments || Object.create(null);
      for (const name in attachments) {
        if (filename === name) {
          return;
        }
      }
      attachments[filename] = {
        filename,
        content
      };
      this.render({
        attachments,
        keepRenderedCapability: true
      });
    });
  }
  
  /***/ }),
  /* 191 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.BaseTreeViewer = void 0;
  __webpack_require__(122);
  var _ui_utils = __webpack_require__(148);
  const TREEITEM_OFFSET_TOP = -100;
  const TREEITEM_SELECTED_CLASS = "selected";
  class BaseTreeViewer {
    constructor(options) {
      if (this.constructor === BaseTreeViewer) {
        throw new Error("Cannot initialize BaseTreeViewer.");
      }
      this.container = options.container;
      this.eventBus = options.eventBus;
      this.reset();
    }
    reset() {
      this._pdfDocument = null;
      this._lastToggleIsShow = true;
      this._currentTreeItem = null;
      this.container.textContent = "";
      this.container.classList.remove("treeWithDeepNesting");
    }
    _dispatchEvent(count) {
      throw new Error("Not implemented: _dispatchEvent");
    }
    _bindLink(element, params) {
      throw new Error("Not implemented: _bindLink");
    }
    _normalizeTextContent(str) {
      return (0, _ui_utils.removeNullCharacters)(str, true) || "\u2013";
    }
    _addToggleButton(div) {
      let hidden = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      const toggler = document.createElement("div");
      toggler.className = "treeItemToggler";
      if (hidden) {
        toggler.classList.add("treeItemsHidden");
      }
      toggler.onclick = evt => {
        evt.stopPropagation();
        toggler.classList.toggle("treeItemsHidden");
        if (evt.shiftKey) {
          const shouldShowAll = !toggler.classList.contains("treeItemsHidden");
          this._toggleTreeItem(div, shouldShowAll);
        }
      };
      div.prepend(toggler);
    }
    _toggleTreeItem(root) {
      let show = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      this._lastToggleIsShow = show;
      for (const toggler of root.querySelectorAll(".treeItemToggler")) {
        toggler.classList.toggle("treeItemsHidden", !show);
      }
    }
    _toggleAllTreeItems() {
      this._toggleTreeItem(this.container, !this._lastToggleIsShow);
    }
    _finishRendering(fragment, count) {
      let hasAnyNesting = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
      if (hasAnyNesting) {
        this.container.classList.add("treeWithDeepNesting");
        this._lastToggleIsShow = !fragment.querySelector(".treeItemsHidden");
      }
      this.container.append(fragment);
      this._dispatchEvent(count);
    }
    render(params) {
      throw new Error("Not implemented: render");
    }
    _updateCurrentTreeItem() {
      let treeItem = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      if (this._currentTreeItem) {
        this._currentTreeItem.classList.remove(TREEITEM_SELECTED_CLASS);
        this._currentTreeItem = null;
      }
      if (treeItem) {
        treeItem.classList.add(TREEITEM_SELECTED_CLASS);
        this._currentTreeItem = treeItem;
      }
    }
    _scrollToCurrentTreeItem(treeItem) {
      if (!treeItem) {
        return;
      }
      let currentNode = treeItem.parentNode;
      while (currentNode && currentNode !== this.container) {
        if (currentNode.classList.contains("treeItem")) {
          const toggler = currentNode.firstElementChild;
          toggler === null || toggler === void 0 || toggler.classList.remove("treeItemsHidden");
        }
        currentNode = currentNode.parentNode;
      }
      this._updateCurrentTreeItem(treeItem);
      this.container.scrollTo(treeItem.offsetLeft, treeItem.offsetTop + TREEITEM_OFFSET_TOP);
    }
  }
  exports.BaseTreeViewer = BaseTreeViewer;
  
  /***/ }),
  /* 192 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFCursorTools = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  var _grab_to_pan = __webpack_require__(193);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _active = /*#__PURE__*/new WeakMap();
  var _prevActive = /*#__PURE__*/new WeakMap();
  var _addEventListeners = /*#__PURE__*/new WeakSet();
  class PDFCursorTools {
    constructor(_ref) {
      let {
        container,
        eventBus,
        cursorToolOnLoad = _ui_utils.CursorTool.SELECT
      } = _ref;
      _classPrivateMethodInitSpec(this, _addEventListeners);
      _classPrivateFieldInitSpec(this, _active, {
        writable: true,
        value: _ui_utils.CursorTool.SELECT
      });
      _classPrivateFieldInitSpec(this, _prevActive, {
        writable: true,
        value: null
      });
      this.container = container;
      this.eventBus = eventBus;
      _classPrivateMethodGet(this, _addEventListeners, _addEventListeners2).call(this);
      Promise.resolve().then(() => {
        this.switchTool(cursorToolOnLoad);
      });
    }
    get activeTool() {
      return _classPrivateFieldGet(this, _active);
    }
    switchTool(tool) {
      if (_classPrivateFieldGet(this, _prevActive) !== null) {
        return;
      }
      if (tool === _classPrivateFieldGet(this, _active)) {
        return;
      }
      const disableActiveTool = () => {
        switch (_classPrivateFieldGet(this, _active)) {
          case _ui_utils.CursorTool.SELECT:
            break;
          case _ui_utils.CursorTool.HAND:
            this._handTool.deactivate();
            break;
          case _ui_utils.CursorTool.ZOOM:
        }
      };
      switch (tool) {
        case _ui_utils.CursorTool.SELECT:
          disableActiveTool();
          break;
        case _ui_utils.CursorTool.HAND:
          disableActiveTool();
          this._handTool.activate();
          break;
        case _ui_utils.CursorTool.ZOOM:
        default:
          console.error(`switchTool: "${tool}" is an unsupported value.`);
          return;
      }
      _classPrivateFieldSet(this, _active, tool);
      this.eventBus.dispatch("cursortoolchanged", {
        source: this,
        tool
      });
    }
    get _handTool() {
      return (0, _pdfjsLib.shadow)(this, "_handTool", new _grab_to_pan.GrabToPan({
        element: this.container
      }));
    }
  }
  exports.PDFCursorTools = PDFCursorTools;
  function _addEventListeners2() {
    this.eventBus._on("switchcursortool", evt => {
      this.switchTool(evt.tool);
    });
    let annotationEditorMode = _pdfjsLib.AnnotationEditorType.NONE,
      presentationModeState = _ui_utils.PresentationModeState.NORMAL;
    const disableActive = () => {
      var _classPrivateFieldGet2;
      const prevActive = _classPrivateFieldGet(this, _active);
      this.switchTool(_ui_utils.CursorTool.SELECT);
      (_classPrivateFieldGet2 = _classPrivateFieldGet(this, _prevActive)) !== null && _classPrivateFieldGet2 !== void 0 ? _classPrivateFieldGet2 : _classPrivateFieldSet(this, _prevActive, prevActive);
    };
    const enableActive = () => {
      const prevActive = _classPrivateFieldGet(this, _prevActive);
      if (prevActive !== null && annotationEditorMode === _pdfjsLib.AnnotationEditorType.NONE && presentationModeState === _ui_utils.PresentationModeState.NORMAL) {
        _classPrivateFieldSet(this, _prevActive, null);
        this.switchTool(prevActive);
      }
    };
    this.eventBus._on("secondarytoolbarreset", evt => {
      if (_classPrivateFieldGet(this, _prevActive) !== null) {
        annotationEditorMode = _pdfjsLib.AnnotationEditorType.NONE;
        presentationModeState = _ui_utils.PresentationModeState.NORMAL;
        enableActive();
      }
    });
    this.eventBus._on("annotationeditormodechanged", _ref2 => {
      let {
        mode
      } = _ref2;
      annotationEditorMode = mode;
      if (mode === _pdfjsLib.AnnotationEditorType.NONE) {
        enableActive();
      } else {
        disableActive();
      }
    });
    this.eventBus._on("presentationmodechanged", _ref3 => {
      let {
        state
      } = _ref3;
      presentationModeState = state;
      if (state === _ui_utils.PresentationModeState.NORMAL) {
        enableActive();
      } else if (state === _ui_utils.PresentationModeState.FULLSCREEN) {
        disableActive();
      }
    });
  }
  
  /***/ }),
  /* 193 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.GrabToPan = void 0;
  __webpack_require__(122);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const CSS_CLASS_GRAB = "grab-to-pan-grab";
  var _onMouseDown = /*#__PURE__*/new WeakSet();
  var _onMouseMove = /*#__PURE__*/new WeakSet();
  var _endPan = /*#__PURE__*/new WeakSet();
  class GrabToPan {
    constructor(_ref) {
      let {
        element
      } = _ref;
      _classPrivateMethodInitSpec(this, _endPan);
      _classPrivateMethodInitSpec(this, _onMouseMove);
      _classPrivateMethodInitSpec(this, _onMouseDown);
      this.element = element;
      this.document = element.ownerDocument;
      this.activate = this.activate.bind(this);
      this.deactivate = this.deactivate.bind(this);
      this.toggle = this.toggle.bind(this);
      this._onMouseDown = _classPrivateMethodGet(this, _onMouseDown, _onMouseDown2).bind(this);
      this._onMouseMove = _classPrivateMethodGet(this, _onMouseMove, _onMouseMove2).bind(this);
      this._endPan = _classPrivateMethodGet(this, _endPan, _endPan2).bind(this);
      const overlay = this.overlay = document.createElement("div");
      overlay.className = "grab-to-pan-grabbing";
    }
    activate() {
      if (!this.active) {
        this.active = true;
        this.element.addEventListener("mousedown", this._onMouseDown, true);
        this.element.classList.add(CSS_CLASS_GRAB);
      }
    }
    deactivate() {
      if (this.active) {
        this.active = false;
        this.element.removeEventListener("mousedown", this._onMouseDown, true);
        this._endPan();
        this.element.classList.remove(CSS_CLASS_GRAB);
      }
    }
    toggle() {
      if (this.active) {
        this.deactivate();
      } else {
        this.activate();
      }
    }
    ignoreTarget(node) {
      return node.matches("a[href], a[href] *, input, textarea, button, button *, select, option");
    }
  }
  exports.GrabToPan = GrabToPan;
  function _onMouseDown2(event) {
    if (event.button !== 0 || this.ignoreTarget(event.target)) {
      return;
    }
    if (event.originalTarget) {
      try {
        event.originalTarget.tagName;
      } catch {
        return;
      }
    }
    this.scrollLeftStart = this.element.scrollLeft;
    this.scrollTopStart = this.element.scrollTop;
    this.clientXStart = event.clientX;
    this.clientYStart = event.clientY;
    this.document.addEventListener("mousemove", this._onMouseMove, true);
    this.document.addEventListener("mouseup", this._endPan, true);
    this.element.addEventListener("scroll", this._endPan, true);
    event.preventDefault();
    event.stopPropagation();
    const focusedElement = document.activeElement;
    if (focusedElement && !focusedElement.contains(event.target)) {
      focusedElement.blur();
    }
  }
  function _onMouseMove2(event) {
    this.element.removeEventListener("scroll", this._endPan, true);
    if (!(event.buttons & 1)) {
      this._endPan();
      return;
    }
    const xDiff = event.clientX - this.clientXStart;
    const yDiff = event.clientY - this.clientYStart;
    this.element.scrollTo({
      top: this.scrollTopStart - yDiff,
      left: this.scrollLeftStart - xDiff,
      behavior: "instant"
    });
    if (!this.overlay.parentNode) {
      document.body.append(this.overlay);
    }
  }
  function _endPan2() {
    this.element.removeEventListener("scroll", this._endPan, true);
    this.document.removeEventListener("mousemove", this._onMouseMove, true);
    this.document.removeEventListener("mouseup", this._endPan, true);
    this.overlay.remove();
  }
  
  /***/ }),
  /* 194 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFDocumentProperties = void 0;
  __webpack_require__(131);
  __webpack_require__(2);
  __webpack_require__(122);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const DEFAULT_FIELD_CONTENT = "-";
  const NON_METRIC_LOCALES = ["en-us", "en-lr", "my"];
  const US_PAGE_NAMES = {
    "8.5x11": "Letter",
    "8.5x14": "Legal"
  };
  const METRIC_PAGE_NAMES = {
    "297x420": "A3",
    "210x297": "A4"
  };
  function getPageName(size, isPortrait, pageNames) {
    const width = isPortrait ? size.width : size.height;
    const height = isPortrait ? size.height : size.width;
    return pageNames[`${width}x${height}`];
  }
  var _fieldData = /*#__PURE__*/new WeakMap();
  var _reset = /*#__PURE__*/new WeakSet();
  var _updateUI = /*#__PURE__*/new WeakSet();
  var _parseFileSize = /*#__PURE__*/new WeakSet();
  var _parsePageSize = /*#__PURE__*/new WeakSet();
  var _parseDate = /*#__PURE__*/new WeakSet();
  var _parseLinearization = /*#__PURE__*/new WeakSet();
  class PDFDocumentProperties {
    constructor(_ref, overlayManager, eventBus, l10n, fileNameLookup) {
      let {
        dialog,
        fields,
        closeButton
      } = _ref;
      _classPrivateMethodInitSpec(this, _parseLinearization);
      _classPrivateMethodInitSpec(this, _parseDate);
      _classPrivateMethodInitSpec(this, _parsePageSize);
      _classPrivateMethodInitSpec(this, _parseFileSize);
      _classPrivateMethodInitSpec(this, _updateUI);
      _classPrivateMethodInitSpec(this, _reset);
      _classPrivateFieldInitSpec(this, _fieldData, {
        writable: true,
        value: null
      });
      this.dialog = dialog;
      this.fields = fields;
      this.overlayManager = overlayManager;
      this.l10n = l10n;
      this._fileNameLookup = fileNameLookup;
      _classPrivateMethodGet(this, _reset, _reset2).call(this);
      closeButton.addEventListener("click", this.close.bind(this));
      this.overlayManager.register(this.dialog);
      eventBus._on("pagechanging", evt => {
        this._currentPageNumber = evt.pageNumber;
      });
      eventBus._on("rotationchanging", evt => {
        this._pagesRotation = evt.pagesRotation;
      });
      this._isNonMetricLocale = true;
      l10n.getLanguage().then(locale => {
        this._isNonMetricLocale = NON_METRIC_LOCALES.includes(locale);
      });
    }
    async open() {
      await Promise.all([this.overlayManager.open(this.dialog), this._dataAvailableCapability.promise]);
      const currentPageNumber = this._currentPageNumber;
      const pagesRotation = this._pagesRotation;
      if (_classPrivateFieldGet(this, _fieldData) && currentPageNumber === _classPrivateFieldGet(this, _fieldData)._currentPageNumber && pagesRotation === _classPrivateFieldGet(this, _fieldData)._pagesRotation) {
        _classPrivateMethodGet(this, _updateUI, _updateUI2).call(this);
        return;
      }
      const {
        info,
        contentLength
      } = await this.pdfDocument.getMetadata();
      const [fileName, fileSize, creationDate, modificationDate, pageSize, isLinearized] = await Promise.all([this._fileNameLookup(), _classPrivateMethodGet(this, _parseFileSize, _parseFileSize2).call(this, contentLength), _classPrivateMethodGet(this, _parseDate, _parseDate2).call(this, info.CreationDate), _classPrivateMethodGet(this, _parseDate, _parseDate2).call(this, info.ModDate), this.pdfDocument.getPage(currentPageNumber).then(pdfPage => {
        return _classPrivateMethodGet(this, _parsePageSize, _parsePageSize2).call(this, (0, _ui_utils.getPageSizeInches)(pdfPage), pagesRotation);
      }), _classPrivateMethodGet(this, _parseLinearization, _parseLinearization2).call(this, info.IsLinearized)]);
      _classPrivateFieldSet(this, _fieldData, Object.freeze({
        fileName,
        fileSize,
        title: info.Title,
        author: info.Author,
        subject: info.Subject,
        keywords: info.Keywords,
        creationDate,
        modificationDate,
        creator: info.Creator,
        producer: info.Producer,
        version: info.PDFFormatVersion,
        pageCount: this.pdfDocument.numPages,
        pageSize,
        linearized: isLinearized,
        _currentPageNumber: currentPageNumber,
        _pagesRotation: pagesRotation
      }));
      _classPrivateMethodGet(this, _updateUI, _updateUI2).call(this);
      const {
        length
      } = await this.pdfDocument.getDownloadInfo();
      if (contentLength === length) {
        return;
      }
      const data = Object.assign(Object.create(null), _classPrivateFieldGet(this, _fieldData));
      data.fileSize = await _classPrivateMethodGet(this, _parseFileSize, _parseFileSize2).call(this, length);
      _classPrivateFieldSet(this, _fieldData, Object.freeze(data));
      _classPrivateMethodGet(this, _updateUI, _updateUI2).call(this);
    }
    async close() {
      this.overlayManager.close(this.dialog);
    }
    setDocument(pdfDocument) {
      if (this.pdfDocument) {
        _classPrivateMethodGet(this, _reset, _reset2).call(this);
        _classPrivateMethodGet(this, _updateUI, _updateUI2).call(this, true);
      }
      if (!pdfDocument) {
        return;
      }
      this.pdfDocument = pdfDocument;
      this._dataAvailableCapability.resolve();
    }
  }
  exports.PDFDocumentProperties = PDFDocumentProperties;
  function _reset2() {
    this.pdfDocument = null;
    _classPrivateFieldSet(this, _fieldData, null);
    this._dataAvailableCapability = new _pdfjsLib.PromiseCapability();
    this._currentPageNumber = 1;
    this._pagesRotation = 0;
  }
  function _updateUI2() {
    let reset = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
    if (reset || !_classPrivateFieldGet(this, _fieldData)) {
      for (const id in this.fields) {
        this.fields[id].textContent = DEFAULT_FIELD_CONTENT;
      }
      return;
    }
    if (this.overlayManager.active !== this.dialog) {
      return;
    }
    for (const id in this.fields) {
      const content = _classPrivateFieldGet(this, _fieldData)[id];
      this.fields[id].textContent = content || content === 0 ? content : DEFAULT_FIELD_CONTENT;
    }
  }
  async function _parseFileSize2() {
    let fileSize = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;
    const kb = fileSize / 1024,
      mb = kb / 1024;
    if (!kb) {
      return undefined;
    }
    return this.l10n.get(`document_properties_${mb >= 1 ? "mb" : "kb"}`, {
      size_mb: mb >= 1 && (+mb.toPrecision(3)).toLocaleString(),
      size_kb: mb < 1 && (+kb.toPrecision(3)).toLocaleString(),
      size_b: fileSize.toLocaleString()
    });
  }
  async function _parsePageSize2(pageSizeInches, pagesRotation) {
    if (!pageSizeInches) {
      return undefined;
    }
    if (pagesRotation % 180 !== 0) {
      pageSizeInches = {
        width: pageSizeInches.height,
        height: pageSizeInches.width
      };
    }
    const isPortrait = (0, _ui_utils.isPortraitOrientation)(pageSizeInches);
    let sizeInches = {
      width: Math.round(pageSizeInches.width * 100) / 100,
      height: Math.round(pageSizeInches.height * 100) / 100
    };
    let sizeMillimeters = {
      width: Math.round(pageSizeInches.width * 25.4 * 10) / 10,
      height: Math.round(pageSizeInches.height * 25.4 * 10) / 10
    };
    let rawName = getPageName(sizeInches, isPortrait, US_PAGE_NAMES) || getPageName(sizeMillimeters, isPortrait, METRIC_PAGE_NAMES);
    if (!rawName && !(Number.isInteger(sizeMillimeters.width) && Number.isInteger(sizeMillimeters.height))) {
      const exactMillimeters = {
        width: pageSizeInches.width * 25.4,
        height: pageSizeInches.height * 25.4
      };
      const intMillimeters = {
        width: Math.round(sizeMillimeters.width),
        height: Math.round(sizeMillimeters.height)
      };
      if (Math.abs(exactMillimeters.width - intMillimeters.width) < 0.1 && Math.abs(exactMillimeters.height - intMillimeters.height) < 0.1) {
        rawName = getPageName(intMillimeters, isPortrait, METRIC_PAGE_NAMES);
        if (rawName) {
          sizeInches = {
            width: Math.round(intMillimeters.width / 25.4 * 100) / 100,
            height: Math.round(intMillimeters.height / 25.4 * 100) / 100
          };
          sizeMillimeters = intMillimeters;
        }
      }
    }
    const [{
      width,
      height
    }, unit, name, orientation] = await Promise.all([this._isNonMetricLocale ? sizeInches : sizeMillimeters, this.l10n.get(`document_properties_page_size_unit_${this._isNonMetricLocale ? "inches" : "millimeters"}`), rawName && this.l10n.get(`document_properties_page_size_name_${rawName.toLowerCase()}`), this.l10n.get(`document_properties_page_size_orientation_${isPortrait ? "portrait" : "landscape"}`)]);
    return this.l10n.get(`document_properties_page_size_dimension_${name ? "name_" : ""}string`, {
      width: width.toLocaleString(),
      height: height.toLocaleString(),
      unit,
      name,
      orientation
    });
  }
  async function _parseDate2(inputDate) {
    const dateObject = _pdfjsLib.PDFDateString.toDateObject(inputDate);
    if (!dateObject) {
      return undefined;
    }
    return this.l10n.get("document_properties_date_string", {
      date: dateObject.toLocaleDateString(),
      time: dateObject.toLocaleTimeString()
    });
  }
  function _parseLinearization2(isLinearized) {
    return this.l10n.get(`document_properties_linearized_${isLinearized ? "yes" : "no"}`);
  }
  
  /***/ }),
  /* 195 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFFindBar = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdf_find_controller = __webpack_require__(196);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const MATCHES_COUNT_LIMIT = 1000;
  var _adjustWidth = /*#__PURE__*/new WeakSet();
  class PDFFindBar {
    constructor(options, eventBus, l10n) {
      _classPrivateMethodInitSpec(this, _adjustWidth);
      this.opened = false;
      this.bar = options.bar;
      this.toggleButton = options.toggleButton;
      this.findField = options.findField;
      this.highlightAll = options.highlightAllCheckbox;
      this.caseSensitive = options.caseSensitiveCheckbox;
      this.matchDiacritics = options.matchDiacriticsCheckbox;
      this.entireWord = options.entireWordCheckbox;
      this.findMsg = options.findMsg;
      this.findResultsCount = options.findResultsCount;
      this.findPreviousButton = options.findPreviousButton;
      this.findNextButton = options.findNextButton;
      this.eventBus = eventBus;
      this.l10n = l10n;
      this.toggleButton.addEventListener("click", () => {
        this.toggle();
      });
      this.findField.addEventListener("input", () => {
        this.dispatchEvent("");
      });
      this.bar.addEventListener("keydown", e => {
        switch (e.keyCode) {
          case 13:
            if (e.target === this.findField) {
              this.dispatchEvent("again", e.shiftKey);
            }
            break;
          case 27:
            this.close();
            break;
        }
      });
      this.findPreviousButton.addEventListener("click", () => {
        this.dispatchEvent("again", true);
      });
      this.findNextButton.addEventListener("click", () => {
        this.dispatchEvent("again", false);
      });
      this.highlightAll.addEventListener("click", () => {
        this.dispatchEvent("highlightallchange");
      });
      this.caseSensitive.addEventListener("click", () => {
        this.dispatchEvent("casesensitivitychange");
      });
      this.entireWord.addEventListener("click", () => {
        this.dispatchEvent("entirewordchange");
      });
      this.matchDiacritics.addEventListener("click", () => {
        this.dispatchEvent("diacriticmatchingchange");
      });
      this.eventBus._on("resize", _classPrivateMethodGet(this, _adjustWidth, _adjustWidth2).bind(this));
    }
    reset() {
      this.updateUIState();
    }
    dispatchEvent(type) {
      let findPrev = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      this.eventBus.dispatch("find", {
        source: this,
        type,
        query: this.findField.value,
        caseSensitive: this.caseSensitive.checked,
        entireWord: this.entireWord.checked,
        highlightAll: this.highlightAll.checked,
        findPrevious: findPrev,
        matchDiacritics: this.matchDiacritics.checked
      });
    }
    updateUIState(state, previous, matchesCount) {
      let findMsg = Promise.resolve("");
      let status = "";
      switch (state) {
        case _pdf_find_controller.FindState.FOUND:
          break;
        case _pdf_find_controller.FindState.PENDING:
          status = "pending";
          break;
        case _pdf_find_controller.FindState.NOT_FOUND:
          findMsg = this.l10n.get("find_not_found");
          status = "notFound";
          break;
        case _pdf_find_controller.FindState.WRAPPED:
          findMsg = this.l10n.get(`find_reached_${previous ? "top" : "bottom"}`);
          break;
      }
      this.findField.setAttribute("data-status", status);
      this.findField.setAttribute("aria-invalid", state === _pdf_find_controller.FindState.NOT_FOUND);
      findMsg.then(msg => {
        this.findMsg.setAttribute("data-status", status);
        this.findMsg.textContent = msg;
        _classPrivateMethodGet(this, _adjustWidth, _adjustWidth2).call(this);
      });
      this.updateResultsCount(matchesCount);
    }
    updateResultsCount() {
      let {
        current = 0,
        total = 0
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      const limit = MATCHES_COUNT_LIMIT;
      let matchCountMsg = Promise.resolve("");
      if (total > 0) {
        if (total > limit) {
          let key = "find_match_count_limit";
          matchCountMsg = this.l10n.get(key, {
            limit
          });
        } else {
          let key = "find_match_count";
          matchCountMsg = this.l10n.get(key, {
            current,
            total
          });
        }
      }
      matchCountMsg.then(msg => {
        this.findResultsCount.textContent = msg;
        _classPrivateMethodGet(this, _adjustWidth, _adjustWidth2).call(this);
      });
    }
    open() {
      if (!this.opened) {
        this.opened = true;
        (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, true, this.bar);
      }
      this.findField.select();
      this.findField.focus();
      _classPrivateMethodGet(this, _adjustWidth, _adjustWidth2).call(this);
    }
    close() {
      if (!this.opened) {
        return;
      }
      this.opened = false;
      (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, false, this.bar);
      this.eventBus.dispatch("findbarclose", {
        source: this
      });
    }
    toggle() {
      if (this.opened) {
        this.close();
      } else {
        this.open();
      }
    }
  }
  exports.PDFFindBar = PDFFindBar;
  function _adjustWidth2() {
    if (!this.opened) {
      return;
    }
    this.bar.classList.remove("wrapContainers");
    const findbarHeight = this.bar.clientHeight;
    const inputContainerHeight = this.bar.firstElementChild.clientHeight;
    if (findbarHeight > inputContainerHeight) {
      this.bar.classList.add("wrapContainers");
    }
  }
  
  /***/ }),
  /* 196 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  __webpack_require__(122);
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFFindController = exports.FindState = void 0;
  __webpack_require__(158);
  __webpack_require__(169);
  __webpack_require__(171);
  __webpack_require__(173);
  __webpack_require__(175);
  __webpack_require__(177);
  __webpack_require__(179);
  __webpack_require__(136);
  __webpack_require__(142);
  __webpack_require__(197);
  __webpack_require__(198);
  __webpack_require__(149);
  __webpack_require__(155);
  __webpack_require__(2);
  var _ui_utils = __webpack_require__(148);
  var _pdf_find_utils = __webpack_require__(199);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  const FindState = {
    FOUND: 0,
    NOT_FOUND: 1,
    WRAPPED: 2,
    PENDING: 3
  };
  exports.FindState = FindState;
  const FIND_TIMEOUT = 250;
  const MATCH_SCROLL_OFFSET_TOP = -50;
  const MATCH_SCROLL_OFFSET_LEFT = -400;
  const CHARACTERS_TO_NORMALIZE = {
    "\u2010": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201A": "'",
    "\u201B": "'",
    "\u201C": '"',
    "\u201D": '"',
    "\u201E": '"',
    "\u201F": '"',
    "\u00BC": "1/4",
    "\u00BD": "1/2",
    "\u00BE": "3/4"
  };
  const DIACRITICS_EXCEPTION = new Set([0x3099, 0x309a, 0x094d, 0x09cd, 0x0a4d, 0x0acd, 0x0b4d, 0x0bcd, 0x0c4d, 0x0ccd, 0x0d3b, 0x0d3c, 0x0d4d, 0x0dca, 0x0e3a, 0x0eba, 0x0f84, 0x1039, 0x103a, 0x1714, 0x1734, 0x17d2, 0x1a60, 0x1b44, 0x1baa, 0x1bab, 0x1bf2, 0x1bf3, 0x2d7f, 0xa806, 0xa82c, 0xa8c4, 0xa953, 0xa9c0, 0xaaf6, 0xabed, 0x0c56, 0x0f71, 0x0f72, 0x0f7a, 0x0f7b, 0x0f7c, 0x0f7d, 0x0f80, 0x0f74]);
  let DIACRITICS_EXCEPTION_STR;
  const DIACRITICS_REG_EXP = /[\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}]+/gu;
  const SPECIAL_CHARS_REG_EXP = /([.*+?^${}()|[\]\\])|([!-#%-\*,-\/:;\?@\[-\]_\{\}\xA1\xA7\xAB\xB6\xB7\xBB\xBF\u037E\u0387\u055A-\u055F\u0589\u058A\u05BE\u05C0\u05C3\u05C6\u05F3\u05F4\u0609\u060A\u060C\u060D\u061B\u061D-\u061F\u066A-\u066D\u06D4\u0700-\u070D\u07F7-\u07F9\u0830-\u083E\u085E\u0964\u0965\u0970\u09FD\u0A76\u0AF0\u0C77\u0C84\u0DF4\u0E4F\u0E5A\u0E5B\u0F04-\u0F12\u0F14\u0F3A-\u0F3D\u0F85\u0FD0-\u0FD4\u0FD9\u0FDA\u104A-\u104F\u10FB\u1360-\u1368\u1400\u166E\u169B\u169C\u16EB-\u16ED\u1735\u1736\u17D4-\u17D6\u17D8-\u17DA\u1800-\u180A\u1944\u1945\u1A1E\u1A1F\u1AA0-\u1AA6\u1AA8-\u1AAD\u1B5A-\u1B60\u1B7D\u1B7E\u1BFC-\u1BFF\u1C3B-\u1C3F\u1C7E\u1C7F\u1CC0-\u1CC7\u1CD3\u2010-\u2027\u2030-\u2043\u2045-\u2051\u2053-\u205E\u207D\u207E\u208D\u208E\u2308-\u230B\u2329\u232A\u2768-\u2775\u27C5\u27C6\u27E6-\u27EF\u2983-\u2998\u29D8-\u29DB\u29FC\u29FD\u2CF9-\u2CFC\u2CFE\u2CFF\u2D70\u2E00-\u2E2E\u2E30-\u2E4F\u2E52-\u2E5D\u3001-\u3003\u3008-\u3011\u3014-\u301F\u3030\u303D\u30A0\u30FB\uA4FE\uA4FF\uA60D-\uA60F\uA673\uA67E\uA6F2-\uA6F7\uA874-\uA877\uA8CE\uA8CF\uA8F8-\uA8FA\uA8FC\uA92E\uA92F\uA95F\uA9C1-\uA9CD\uA9DE\uA9DF\uAA5C-\uAA5F\uAADE\uAADF\uAAF0\uAAF1\uABEB\uFD3E\uFD3F\uFE10-\uFE19\uFE30-\uFE52\uFE54-\uFE61\uFE63\uFE68\uFE6A\uFE6B\uFF01-\uFF03\uFF05-\uFF0A\uFF0C-\uFF0F\uFF1A\uFF1B\uFF1F\uFF20\uFF3B-\uFF3D\uFF3F\uFF5B\uFF5D\uFF5F-\uFF65\u{10100}-\u{10102}\u{1039F}\u{103D0}\u{1056F}\u{10857}\u{1091F}\u{1093F}\u{10A50}-\u{10A58}\u{10A7F}\u{10AF0}-\u{10AF6}\u{10B39}-\u{10B3F}\u{10B99}-\u{10B9C}\u{10EAD}\u{10F55}-\u{10F59}\u{10F86}-\u{10F89}\u{11047}-\u{1104D}\u{110BB}\u{110BC}\u{110BE}-\u{110C1}\u{11140}-\u{11143}\u{11174}\u{11175}\u{111C5}-\u{111C8}\u{111CD}\u{111DB}\u{111DD}-\u{111DF}\u{11238}-\u{1123D}\u{112A9}\u{1144B}-\u{1144F}\u{1145A}\u{1145B}\u{1145D}\u{114C6}\u{115C1}-\u{115D7}\u{11641}-\u{11643}\u{11660}-\u{1166C}\u{116B9}\u{1173C}-\u{1173E}\u{1183B}\u{11944}-\u{11946}\u{119E2}\u{11A3F}-\u{11A46}\u{11A9A}-\u{11A9C}\u{11A9E}-\u{11AA2}\u{11B00}-\u{11B09}\u{11C41}-\u{11C45}\u{11C70}\u{11C71}\u{11EF7}\u{11EF8}\u{11F43}-\u{11F4F}\u{11FFF}\u{12470}-\u{12474}\u{12FF1}\u{12FF2}\u{16A6E}\u{16A6F}\u{16AF5}\u{16B37}-\u{16B3B}\u{16B44}\u{16E97}-\u{16E9A}\u{16FE2}\u{1BC9F}\u{1DA87}-\u{1DA8B}\u{1E95E}\u{1E95F}])|(\s+)|([\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}])|([A-Za-z\xAA\xB5\xBA\xC0-\xD6\xD8-\xF6\xF8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0370-\u0374\u0376\u0377\u037A-\u037D\u037F\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u052F\u0531-\u0556\u0559\u0560-\u0588\u05D0-\u05EA\u05EF-\u05F2\u0620-\u064A\u066E\u066F\u0671-\u06D3\u06D5\u06E5\u06E6\u06EE\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0815\u081A\u0824\u0828\u0840-\u0858\u0860-\u086A\u0870-\u0887\u0889-\u088E\u08A0-\u08C9\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0980\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC\u09DD\u09DF-\u09E1\u09F0\u09F1\u09FC\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0\u0AE1\u0AF9\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D\u0B5C\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C39\u0C3D\u0C58-\u0C5A\u0C5D\u0C60\u0C61\u0C80\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDD\u0CDE\u0CE0\u0CE1\u0CF1\u0CF2\u0D04-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D\u0D4E\u0D54-\u0D56\u0D5F-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E30\u0E32\u0E33\u0E40-\u0E46\u0E81\u0E82\u0E84\u0E86-\u0E8A\u0E8C-\u0EA3\u0EA5\u0EA7-\u0EB0\u0EB2\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8C\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F5\u13F8-\u13FD\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u16F1-\u16F8\u1700-\u1711\u171F-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1878\u1880-\u1884\u1887-\u18A8\u18AA\u18B0-\u18F5\u1900-\u191E\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19B0-\u19C9\u1A00-\u1A16\u1A20-\u1A54\u1AA7\u1B05-\u1B33\u1B45-\u1B4C\u1B83-\u1BA0\u1BAE\u1BAF\u1BBA-\u1BE5\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1C80-\u1C88\u1C90-\u1CBA\u1CBD-\u1CBF\u1CE9-\u1CEC\u1CEE-\u1CF3\u1CF5\u1CF6\u1CFA\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2183\u2184\u2C00-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2E2F\u3005\u3006\u3031-\u3035\u303B\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312F\u3131-\u318E\u31A0-\u31BF\u31F0-\u31FF\u3400-\u4DBF\u4E00-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA67F-\uA69D\uA6A0-\uA6E5\uA717-\uA71F\uA722-\uA788\uA78B-\uA7CA\uA7D0\uA7D1\uA7D3\uA7D5-\uA7D9\uA7F2-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA8F2-\uA8F7\uA8FB\uA8FD\uA8FE\uA90A-\uA925\uA930-\uA946\uA960-\uA97C\uA984-\uA9B2\uA9CF\uA9E0-\uA9E4\uA9E6-\uA9EF\uA9FA-\uA9FE\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAA60-\uAA76\uAA7A\uAA7E-\uAAAF\uAAB1\uAAB5\uAAB6\uAAB9-\uAABD\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEA\uAAF2-\uAAF4\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uAB30-\uAB5A\uAB5C-\uAB69\uAB70-\uABE2\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC\u{10000}-\u{1000B}\u{1000D}-\u{10026}\u{10028}-\u{1003A}\u{1003C}\u{1003D}\u{1003F}-\u{1004D}\u{10050}-\u{1005D}\u{10080}-\u{100FA}\u{10280}-\u{1029C}\u{102A0}-\u{102D0}\u{10300}-\u{1031F}\u{1032D}-\u{10340}\u{10342}-\u{10349}\u{10350}-\u{10375}\u{10380}-\u{1039D}\u{103A0}-\u{103C3}\u{103C8}-\u{103CF}\u{10400}-\u{1049D}\u{104B0}-\u{104D3}\u{104D8}-\u{104FB}\u{10500}-\u{10527}\u{10530}-\u{10563}\u{10570}-\u{1057A}\u{1057C}-\u{1058A}\u{1058C}-\u{10592}\u{10594}\u{10595}\u{10597}-\u{105A1}\u{105A3}-\u{105B1}\u{105B3}-\u{105B9}\u{105BB}\u{105BC}\u{10600}-\u{10736}\u{10740}-\u{10755}\u{10760}-\u{10767}\u{10780}-\u{10785}\u{10787}-\u{107B0}\u{107B2}-\u{107BA}\u{10800}-\u{10805}\u{10808}\u{1080A}-\u{10835}\u{10837}\u{10838}\u{1083C}\u{1083F}-\u{10855}\u{10860}-\u{10876}\u{10880}-\u{1089E}\u{108E0}-\u{108F2}\u{108F4}\u{108F5}\u{10900}-\u{10915}\u{10920}-\u{10939}\u{10980}-\u{109B7}\u{109BE}\u{109BF}\u{10A00}\u{10A10}-\u{10A13}\u{10A15}-\u{10A17}\u{10A19}-\u{10A35}\u{10A60}-\u{10A7C}\u{10A80}-\u{10A9C}\u{10AC0}-\u{10AC7}\u{10AC9}-\u{10AE4}\u{10B00}-\u{10B35}\u{10B40}-\u{10B55}\u{10B60}-\u{10B72}\u{10B80}-\u{10B91}\u{10C00}-\u{10C48}\u{10C80}-\u{10CB2}\u{10CC0}-\u{10CF2}\u{10D00}-\u{10D23}\u{10E80}-\u{10EA9}\u{10EB0}\u{10EB1}\u{10F00}-\u{10F1C}\u{10F27}\u{10F30}-\u{10F45}\u{10F70}-\u{10F81}\u{10FB0}-\u{10FC4}\u{10FE0}-\u{10FF6}\u{11003}-\u{11037}\u{11071}\u{11072}\u{11075}\u{11083}-\u{110AF}\u{110D0}-\u{110E8}\u{11103}-\u{11126}\u{11144}\u{11147}\u{11150}-\u{11172}\u{11176}\u{11183}-\u{111B2}\u{111C1}-\u{111C4}\u{111DA}\u{111DC}\u{11200}-\u{11211}\u{11213}-\u{1122B}\u{1123F}\u{11240}\u{11280}-\u{11286}\u{11288}\u{1128A}-\u{1128D}\u{1128F}-\u{1129D}\u{1129F}-\u{112A8}\u{112B0}-\u{112DE}\u{11305}-\u{1130C}\u{1130F}\u{11310}\u{11313}-\u{11328}\u{1132A}-\u{11330}\u{11332}\u{11333}\u{11335}-\u{11339}\u{1133D}\u{11350}\u{1135D}-\u{11361}\u{11400}-\u{11434}\u{11447}-\u{1144A}\u{1145F}-\u{11461}\u{11480}-\u{114AF}\u{114C4}\u{114C5}\u{114C7}\u{11580}-\u{115AE}\u{115D8}-\u{115DB}\u{11600}-\u{1162F}\u{11644}\u{11680}-\u{116AA}\u{116B8}\u{11700}-\u{1171A}\u{11740}-\u{11746}\u{11800}-\u{1182B}\u{118A0}-\u{118DF}\u{118FF}-\u{11906}\u{11909}\u{1190C}-\u{11913}\u{11915}\u{11916}\u{11918}-\u{1192F}\u{1193F}\u{11941}\u{119A0}-\u{119A7}\u{119AA}-\u{119D0}\u{119E1}\u{119E3}\u{11A00}\u{11A0B}-\u{11A32}\u{11A3A}\u{11A50}\u{11A5C}-\u{11A89}\u{11A9D}\u{11AB0}-\u{11AF8}\u{11C00}-\u{11C08}\u{11C0A}-\u{11C2E}\u{11C40}\u{11C72}-\u{11C8F}\u{11D00}-\u{11D06}\u{11D08}\u{11D09}\u{11D0B}-\u{11D30}\u{11D46}\u{11D60}-\u{11D65}\u{11D67}\u{11D68}\u{11D6A}-\u{11D89}\u{11D98}\u{11EE0}-\u{11EF2}\u{11F02}\u{11F04}-\u{11F10}\u{11F12}-\u{11F33}\u{11FB0}\u{12000}-\u{12399}\u{12480}-\u{12543}\u{12F90}-\u{12FF0}\u{13000}-\u{1342F}\u{13441}-\u{13446}\u{14400}-\u{14646}\u{16800}-\u{16A38}\u{16A40}-\u{16A5E}\u{16A70}-\u{16ABE}\u{16AD0}-\u{16AED}\u{16B00}-\u{16B2F}\u{16B40}-\u{16B43}\u{16B63}-\u{16B77}\u{16B7D}-\u{16B8F}\u{16E40}-\u{16E7F}\u{16F00}-\u{16F4A}\u{16F50}\u{16F93}-\u{16F9F}\u{16FE0}\u{16FE1}\u{16FE3}\u{17000}-\u{187F7}\u{18800}-\u{18CD5}\u{18D00}-\u{18D08}\u{1AFF0}-\u{1AFF3}\u{1AFF5}-\u{1AFFB}\u{1AFFD}\u{1AFFE}\u{1B000}-\u{1B122}\u{1B132}\u{1B150}-\u{1B152}\u{1B155}\u{1B164}-\u{1B167}\u{1B170}-\u{1B2FB}\u{1BC00}-\u{1BC6A}\u{1BC70}-\u{1BC7C}\u{1BC80}-\u{1BC88}\u{1BC90}-\u{1BC99}\u{1D400}-\u{1D454}\u{1D456}-\u{1D49C}\u{1D49E}\u{1D49F}\u{1D4A2}\u{1D4A5}\u{1D4A6}\u{1D4A9}-\u{1D4AC}\u{1D4AE}-\u{1D4B9}\u{1D4BB}\u{1D4BD}-\u{1D4C3}\u{1D4C5}-\u{1D505}\u{1D507}-\u{1D50A}\u{1D50D}-\u{1D514}\u{1D516}-\u{1D51C}\u{1D51E}-\u{1D539}\u{1D53B}-\u{1D53E}\u{1D540}-\u{1D544}\u{1D546}\u{1D54A}-\u{1D550}\u{1D552}-\u{1D6A5}\u{1D6A8}-\u{1D6C0}\u{1D6C2}-\u{1D6DA}\u{1D6DC}-\u{1D6FA}\u{1D6FC}-\u{1D714}\u{1D716}-\u{1D734}\u{1D736}-\u{1D74E}\u{1D750}-\u{1D76E}\u{1D770}-\u{1D788}\u{1D78A}-\u{1D7A8}\u{1D7AA}-\u{1D7C2}\u{1D7C4}-\u{1D7CB}\u{1DF00}-\u{1DF1E}\u{1DF25}-\u{1DF2A}\u{1E030}-\u{1E06D}\u{1E100}-\u{1E12C}\u{1E137}-\u{1E13D}\u{1E14E}\u{1E290}-\u{1E2AD}\u{1E2C0}-\u{1E2EB}\u{1E4D0}-\u{1E4EB}\u{1E7E0}-\u{1E7E6}\u{1E7E8}-\u{1E7EB}\u{1E7ED}\u{1E7EE}\u{1E7F0}-\u{1E7FE}\u{1E800}-\u{1E8C4}\u{1E900}-\u{1E943}\u{1E94B}\u{1EE00}-\u{1EE03}\u{1EE05}-\u{1EE1F}\u{1EE21}\u{1EE22}\u{1EE24}\u{1EE27}\u{1EE29}-\u{1EE32}\u{1EE34}-\u{1EE37}\u{1EE39}\u{1EE3B}\u{1EE42}\u{1EE47}\u{1EE49}\u{1EE4B}\u{1EE4D}-\u{1EE4F}\u{1EE51}\u{1EE52}\u{1EE54}\u{1EE57}\u{1EE59}\u{1EE5B}\u{1EE5D}\u{1EE5F}\u{1EE61}\u{1EE62}\u{1EE64}\u{1EE67}-\u{1EE6A}\u{1EE6C}-\u{1EE72}\u{1EE74}-\u{1EE77}\u{1EE79}-\u{1EE7C}\u{1EE7E}\u{1EE80}-\u{1EE89}\u{1EE8B}-\u{1EE9B}\u{1EEA1}-\u{1EEA3}\u{1EEA5}-\u{1EEA9}\u{1EEAB}-\u{1EEBB}\u{20000}-\u{2A6DF}\u{2A700}-\u{2B739}\u{2B740}-\u{2B81D}\u{2B820}-\u{2CEA1}\u{2CEB0}-\u{2EBE0}\u{2F800}-\u{2FA1D}\u{30000}-\u{3134A}\u{31350}-\u{323AF}])/gu;
  const NOT_DIACRITIC_FROM_END_REG_EXP = /([^\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}])[\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}]*$/u;
  const NOT_DIACRITIC_FROM_START_REG_EXP = /^[\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}]*([^\u0300-\u036F\u0483-\u0489\u0591-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7\u06E8\u06EA-\u06ED\u0711\u0730-\u074A\u07A6-\u07B0\u07EB-\u07F3\u07FD\u0816-\u0819\u081B-\u0823\u0825-\u0827\u0829-\u082D\u0859-\u085B\u0898-\u089F\u08CA-\u08E1\u08E3-\u0903\u093A-\u093C\u093E-\u094F\u0951-\u0957\u0962\u0963\u0981-\u0983\u09BC\u09BE-\u09C4\u09C7\u09C8\u09CB-\u09CD\u09D7\u09E2\u09E3\u09FE\u0A01-\u0A03\u0A3C\u0A3E-\u0A42\u0A47\u0A48\u0A4B-\u0A4D\u0A51\u0A70\u0A71\u0A75\u0A81-\u0A83\u0ABC\u0ABE-\u0AC5\u0AC7-\u0AC9\u0ACB-\u0ACD\u0AE2\u0AE3\u0AFA-\u0AFF\u0B01-\u0B03\u0B3C\u0B3E-\u0B44\u0B47\u0B48\u0B4B-\u0B4D\u0B55-\u0B57\u0B62\u0B63\u0B82\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCD\u0BD7\u0C00-\u0C04\u0C3C\u0C3E-\u0C44\u0C46-\u0C48\u0C4A-\u0C4D\u0C55\u0C56\u0C62\u0C63\u0C81-\u0C83\u0CBC\u0CBE-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCD\u0CD5\u0CD6\u0CE2\u0CE3\u0CF3\u0D00-\u0D03\u0D3B\u0D3C\u0D3E-\u0D44\u0D46-\u0D48\u0D4A-\u0D4D\u0D57\u0D62\u0D63\u0D81-\u0D83\u0DCA\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E31\u0E34-\u0E3A\u0E47-\u0E4E\u0EB1\u0EB4-\u0EBC\u0EC8-\u0ECE\u0F18\u0F19\u0F35\u0F37\u0F39\u0F3E\u0F3F\u0F71-\u0F84\u0F86\u0F87\u0F8D-\u0F97\u0F99-\u0FBC\u0FC6\u102B-\u103E\u1056-\u1059\u105E-\u1060\u1062-\u1064\u1067-\u106D\u1071-\u1074\u1082-\u108D\u108F\u109A-\u109D\u135D-\u135F\u1712-\u1715\u1732-\u1734\u1752\u1753\u1772\u1773\u17B4-\u17D3\u17DD\u180B-\u180D\u180F\u1885\u1886\u18A9\u1920-\u192B\u1930-\u193B\u1A17-\u1A1B\u1A55-\u1A5E\u1A60-\u1A7C\u1A7F\u1AB0-\u1ACE\u1B00-\u1B04\u1B34-\u1B44\u1B6B-\u1B73\u1B80-\u1B82\u1BA1-\u1BAD\u1BE6-\u1BF3\u1C24-\u1C37\u1CD0-\u1CD2\u1CD4-\u1CE8\u1CED\u1CF4\u1CF7-\u1CF9\u1DC0-\u1DFF\u20D0-\u20F0\u2CEF-\u2CF1\u2D7F\u2DE0-\u2DFF\u302A-\u302F\u3099\u309A\uA66F-\uA672\uA674-\uA67D\uA69E\uA69F\uA6F0\uA6F1\uA802\uA806\uA80B\uA823-\uA827\uA82C\uA880\uA881\uA8B4-\uA8C5\uA8E0-\uA8F1\uA8FF\uA926-\uA92D\uA947-\uA953\uA980-\uA983\uA9B3-\uA9C0\uA9E5\uAA29-\uAA36\uAA43\uAA4C\uAA4D\uAA7B-\uAA7D\uAAB0\uAAB2-\uAAB4\uAAB7\uAAB8\uAABE\uAABF\uAAC1\uAAEB-\uAAEF\uAAF5\uAAF6\uABE3-\uABEA\uABEC\uABED\uFB1E\uFE00-\uFE0F\uFE20-\uFE2F\u{101FD}\u{102E0}\u{10376}-\u{1037A}\u{10A01}-\u{10A03}\u{10A05}\u{10A06}\u{10A0C}-\u{10A0F}\u{10A38}-\u{10A3A}\u{10A3F}\u{10AE5}\u{10AE6}\u{10D24}-\u{10D27}\u{10EAB}\u{10EAC}\u{10EFD}-\u{10EFF}\u{10F46}-\u{10F50}\u{10F82}-\u{10F85}\u{11000}-\u{11002}\u{11038}-\u{11046}\u{11070}\u{11073}\u{11074}\u{1107F}-\u{11082}\u{110B0}-\u{110BA}\u{110C2}\u{11100}-\u{11102}\u{11127}-\u{11134}\u{11145}\u{11146}\u{11173}\u{11180}-\u{11182}\u{111B3}-\u{111C0}\u{111C9}-\u{111CC}\u{111CE}\u{111CF}\u{1122C}-\u{11237}\u{1123E}\u{11241}\u{112DF}-\u{112EA}\u{11300}-\u{11303}\u{1133B}\u{1133C}\u{1133E}-\u{11344}\u{11347}\u{11348}\u{1134B}-\u{1134D}\u{11357}\u{11362}\u{11363}\u{11366}-\u{1136C}\u{11370}-\u{11374}\u{11435}-\u{11446}\u{1145E}\u{114B0}-\u{114C3}\u{115AF}-\u{115B5}\u{115B8}-\u{115C0}\u{115DC}\u{115DD}\u{11630}-\u{11640}\u{116AB}-\u{116B7}\u{1171D}-\u{1172B}\u{1182C}-\u{1183A}\u{11930}-\u{11935}\u{11937}\u{11938}\u{1193B}-\u{1193E}\u{11940}\u{11942}\u{11943}\u{119D1}-\u{119D7}\u{119DA}-\u{119E0}\u{119E4}\u{11A01}-\u{11A0A}\u{11A33}-\u{11A39}\u{11A3B}-\u{11A3E}\u{11A47}\u{11A51}-\u{11A5B}\u{11A8A}-\u{11A99}\u{11C2F}-\u{11C36}\u{11C38}-\u{11C3F}\u{11C92}-\u{11CA7}\u{11CA9}-\u{11CB6}\u{11D31}-\u{11D36}\u{11D3A}\u{11D3C}\u{11D3D}\u{11D3F}-\u{11D45}\u{11D47}\u{11D8A}-\u{11D8E}\u{11D90}\u{11D91}\u{11D93}-\u{11D97}\u{11EF3}-\u{11EF6}\u{11F00}\u{11F01}\u{11F03}\u{11F34}-\u{11F3A}\u{11F3E}-\u{11F42}\u{13440}\u{13447}-\u{13455}\u{16AF0}-\u{16AF4}\u{16B30}-\u{16B36}\u{16F4F}\u{16F51}-\u{16F87}\u{16F8F}-\u{16F92}\u{16FE4}\u{16FF0}\u{16FF1}\u{1BC9D}\u{1BC9E}\u{1CF00}-\u{1CF2D}\u{1CF30}-\u{1CF46}\u{1D165}-\u{1D169}\u{1D16D}-\u{1D172}\u{1D17B}-\u{1D182}\u{1D185}-\u{1D18B}\u{1D1AA}-\u{1D1AD}\u{1D242}-\u{1D244}\u{1DA00}-\u{1DA36}\u{1DA3B}-\u{1DA6C}\u{1DA75}\u{1DA84}\u{1DA9B}-\u{1DA9F}\u{1DAA1}-\u{1DAAF}\u{1E000}-\u{1E006}\u{1E008}-\u{1E018}\u{1E01B}-\u{1E021}\u{1E023}\u{1E024}\u{1E026}-\u{1E02A}\u{1E08F}\u{1E130}-\u{1E136}\u{1E2AE}\u{1E2EC}-\u{1E2EF}\u{1E4EC}-\u{1E4EF}\u{1E8D0}-\u{1E8D6}\u{1E944}-\u{1E94A}\u{E0100}-\u{E01EF}])/u;
  const SYLLABLES_REG_EXP = /[\uAC00-\uD7AF\uFA6C\uFACF-\uFAD1\uFAD5-\uFAD7]+/g;
  const SYLLABLES_LENGTHS = new Map();
  const FIRST_CHAR_SYLLABLES_REG_EXP = "[\\u1100-\\u1112\\ud7a4-\\ud7af\\ud84a\\ud84c\\ud850\\ud854\\ud857\\ud85f]";
  const NFKC_CHARS_TO_NORMALIZE = new Map();
  let noSyllablesRegExp = null;
  let withSyllablesRegExp = null;
  function normalize(text) {
    const syllablePositions = [];
    let m;
    while ((m = SYLLABLES_REG_EXP.exec(text)) !== null) {
      let {
        index
      } = m;
      for (const char of m[0]) {
        let len = SYLLABLES_LENGTHS.get(char);
        if (!len) {
          len = char.normalize("NFD").length;
          SYLLABLES_LENGTHS.set(char, len);
        }
        syllablePositions.push([len, index++]);
      }
    }
    let normalizationRegex;
    if (syllablePositions.length === 0 && noSyllablesRegExp) {
      normalizationRegex = noSyllablesRegExp;
    } else if (syllablePositions.length > 0 && withSyllablesRegExp) {
      normalizationRegex = withSyllablesRegExp;
    } else {
      const replace = Object.keys(CHARACTERS_TO_NORMALIZE).join("");
      const toNormalizeWithNFKC = (0, _pdf_find_utils.getNormalizeWithNFKC)();
      const CJK = "(?:\\p{Ideographic}|[\u3040-\u30FF])";
      const HKDiacritics = "(?:\u3099|\u309A)";
      const regexp = `([${replace}])|([${toNormalizeWithNFKC}])|(${HKDiacritics}\\n)|(\\p{M}+(?:-\\n)?)|(\\S-\\n)|(${CJK}\\n)|(\\n)`;
      if (syllablePositions.length === 0) {
        normalizationRegex = noSyllablesRegExp = new RegExp(regexp + "|(\\u0000)", "gum");
      } else {
        normalizationRegex = withSyllablesRegExp = new RegExp(regexp + `|(${FIRST_CHAR_SYLLABLES_REG_EXP})`, "gum");
      }
    }
    const rawDiacriticsPositions = [];
    while ((m = DIACRITICS_REG_EXP.exec(text)) !== null) {
      rawDiacriticsPositions.push([m[0].length, m.index]);
    }
    let normalized = text.normalize("NFD");
    const positions = [[0, 0]];
    let rawDiacriticsIndex = 0;
    let syllableIndex = 0;
    let shift = 0;
    let shiftOrigin = 0;
    let eol = 0;
    let hasDiacritics = false;
    normalized = normalized.replace(normalizationRegex, (match, p1, p2, p3, p4, p5, p6, p7, p8, i) => {
      var _syllablePositions$sy;
      i -= shiftOrigin;
      if (p1) {
        const replacement = CHARACTERS_TO_NORMALIZE[p1];
        const jj = replacement.length;
        for (let j = 1; j < jj; j++) {
          positions.push([i - shift + j, shift - j]);
        }
        shift -= jj - 1;
        return replacement;
      }
      if (p2) {
        let replacement = NFKC_CHARS_TO_NORMALIZE.get(p2);
        if (!replacement) {
          replacement = p2.normalize("NFKC");
          NFKC_CHARS_TO_NORMALIZE.set(p2, replacement);
        }
        const jj = replacement.length;
        for (let j = 1; j < jj; j++) {
          positions.push([i - shift + j, shift - j]);
        }
        shift -= jj - 1;
        return replacement;
      }
      if (p3) {
        var _rawDiacriticsPositio;
        hasDiacritics = true;
        if (i + eol === ((_rawDiacriticsPositio = rawDiacriticsPositions[rawDiacriticsIndex]) === null || _rawDiacriticsPositio === void 0 ? void 0 : _rawDiacriticsPositio[1])) {
          ++rawDiacriticsIndex;
        } else {
          positions.push([i - 1 - shift + 1, shift - 1]);
          shift -= 1;
          shiftOrigin += 1;
        }
        positions.push([i - shift + 1, shift]);
        shiftOrigin += 1;
        eol += 1;
        return p3.charAt(0);
      }
      if (p4) {
        var _rawDiacriticsPositio2;
        const hasTrailingDashEOL = p4.endsWith("\n");
        const len = hasTrailingDashEOL ? p4.length - 2 : p4.length;
        hasDiacritics = true;
        let jj = len;
        if (i + eol === ((_rawDiacriticsPositio2 = rawDiacriticsPositions[rawDiacriticsIndex]) === null || _rawDiacriticsPositio2 === void 0 ? void 0 : _rawDiacriticsPositio2[1])) {
          jj -= rawDiacriticsPositions[rawDiacriticsIndex][0];
          ++rawDiacriticsIndex;
        }
        for (let j = 1; j <= jj; j++) {
          positions.push([i - 1 - shift + j, shift - j]);
        }
        shift -= jj;
        shiftOrigin += jj;
        if (hasTrailingDashEOL) {
          i += len - 1;
          positions.push([i - shift + 1, 1 + shift]);
          shift += 1;
          shiftOrigin += 1;
          eol += 1;
          return p4.slice(0, len);
        }
        return p4;
      }
      if (p5) {
        const len = p5.length - 2;
        positions.push([i - shift + len, 1 + shift]);
        shift += 1;
        shiftOrigin += 1;
        eol += 1;
        return p5.slice(0, -2);
      }
      if (p6) {
        const len = p6.length - 1;
        positions.push([i - shift + len, shift]);
        shiftOrigin += 1;
        eol += 1;
        return p6.slice(0, -1);
      }
      if (p7) {
        positions.push([i - shift + 1, shift - 1]);
        shift -= 1;
        shiftOrigin += 1;
        eol += 1;
        return " ";
      }
      if (i + eol === ((_syllablePositions$sy = syllablePositions[syllableIndex]) === null || _syllablePositions$sy === void 0 ? void 0 : _syllablePositions$sy[1])) {
        const newCharLen = syllablePositions[syllableIndex][0] - 1;
        ++syllableIndex;
        for (let j = 1; j <= newCharLen; j++) {
          positions.push([i - (shift - j), shift - j]);
        }
        shift -= newCharLen;
        shiftOrigin += newCharLen;
      }
      return p8;
    });
    positions.push([normalized.length, shift]);
    return [normalized, positions, hasDiacritics];
  }
  function getOriginalIndex(diffs, pos, len) {
    if (!diffs) {
      return [pos, len];
    }
    const start = pos;
    const end = pos + len - 1;
    let i = (0, _ui_utils.binarySearchFirstItem)(diffs, x => x[0] >= start);
    if (diffs[i][0] > start) {
      --i;
    }
    let j = (0, _ui_utils.binarySearchFirstItem)(diffs, x => x[0] >= end, i);
    if (diffs[j][0] > end) {
      --j;
    }
    const oldStart = start + diffs[i][1];
    const oldEnd = end + diffs[j][1];
    const oldLen = oldEnd + 1 - oldStart;
    return [oldStart, oldLen];
  }
  var _state = /*#__PURE__*/new WeakMap();
  var _updateMatchesCountOnProgress = /*#__PURE__*/new WeakMap();
  var _visitedPagesCount = /*#__PURE__*/new WeakMap();
  var _onFind = /*#__PURE__*/new WeakSet();
  var _reset = /*#__PURE__*/new WeakSet();
  var _query = /*#__PURE__*/new WeakMap();
  var _shouldDirtyMatch = /*#__PURE__*/new WeakSet();
  var _isEntireWord = /*#__PURE__*/new WeakSet();
  var _calculateRegExpMatch = /*#__PURE__*/new WeakSet();
  var _convertToRegExpString = /*#__PURE__*/new WeakSet();
  var _calculateMatch = /*#__PURE__*/new WeakSet();
  var _extractText = /*#__PURE__*/new WeakSet();
  var _updatePage = /*#__PURE__*/new WeakSet();
  var _updateAllPages = /*#__PURE__*/new WeakSet();
  var _nextMatch = /*#__PURE__*/new WeakSet();
  var _matchesReady = /*#__PURE__*/new WeakSet();
  var _nextPageMatch = /*#__PURE__*/new WeakSet();
  var _advanceOffsetPage = /*#__PURE__*/new WeakSet();
  var _updateMatch = /*#__PURE__*/new WeakSet();
  var _onFindBarClose = /*#__PURE__*/new WeakSet();
  var _requestMatchesCount = /*#__PURE__*/new WeakSet();
  var _updateUIResultsCount = /*#__PURE__*/new WeakSet();
  var _updateUIState = /*#__PURE__*/new WeakSet();
  class PDFFindController {
    constructor(_ref) {
      let {
        linkService: _linkService,
        eventBus,
        updateMatchesCountOnProgress = true
      } = _ref;
      _classPrivateMethodInitSpec(this, _updateUIState);
      _classPrivateMethodInitSpec(this, _updateUIResultsCount);
      _classPrivateMethodInitSpec(this, _requestMatchesCount);
      _classPrivateMethodInitSpec(this, _onFindBarClose);
      _classPrivateMethodInitSpec(this, _updateMatch);
      _classPrivateMethodInitSpec(this, _advanceOffsetPage);
      _classPrivateMethodInitSpec(this, _nextPageMatch);
      _classPrivateMethodInitSpec(this, _matchesReady);
      _classPrivateMethodInitSpec(this, _nextMatch);
      _classPrivateMethodInitSpec(this, _updateAllPages);
      _classPrivateMethodInitSpec(this, _updatePage);
      _classPrivateMethodInitSpec(this, _extractText);
      _classPrivateMethodInitSpec(this, _calculateMatch);
      _classPrivateMethodInitSpec(this, _convertToRegExpString);
      _classPrivateMethodInitSpec(this, _calculateRegExpMatch);
      _classPrivateMethodInitSpec(this, _isEntireWord);
      _classPrivateMethodInitSpec(this, _shouldDirtyMatch);
      _classPrivateFieldInitSpec(this, _query, {
        get: _get_query,
        set: void 0
      });
      _classPrivateMethodInitSpec(this, _reset);
      _classPrivateMethodInitSpec(this, _onFind);
      _classPrivateFieldInitSpec(this, _state, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _updateMatchesCountOnProgress, {
        writable: true,
        value: true
      });
      _classPrivateFieldInitSpec(this, _visitedPagesCount, {
        writable: true,
        value: 0
      });
      this._linkService = _linkService;
      this._eventBus = eventBus;
      _classPrivateFieldSet(this, _updateMatchesCountOnProgress, updateMatchesCountOnProgress);
      this.onIsPageVisible = null;
      _classPrivateMethodGet(this, _reset, _reset2).call(this);
      eventBus._on("find", _classPrivateMethodGet(this, _onFind, _onFind2).bind(this));
      eventBus._on("findbarclose", _classPrivateMethodGet(this, _onFindBarClose, _onFindBarClose2).bind(this));
    }
    get highlightMatches() {
      return this._highlightMatches;
    }
    get pageMatches() {
      return this._pageMatches;
    }
    get pageMatchesLength() {
      return this._pageMatchesLength;
    }
    get selected() {
      return this._selected;
    }
    get state() {
      return _classPrivateFieldGet(this, _state);
    }
    setDocument(pdfDocument) {
      if (this._pdfDocument) {
        _classPrivateMethodGet(this, _reset, _reset2).call(this);
      }
      if (!pdfDocument) {
        return;
      }
      this._pdfDocument = pdfDocument;
      this._firstPageCapability.resolve();
    }
    scrollMatchIntoView(_ref2) {
      let {
        element = null,
        selectedLeft = 0,
        pageIndex = -1,
        matchIndex = -1
      } = _ref2;
      if (!this._scrollMatches || !element) {
        return;
      } else if (matchIndex === -1 || matchIndex !== this._selected.matchIdx) {
        return;
      } else if (pageIndex === -1 || pageIndex !== this._selected.pageIdx) {
        return;
      }
      this._scrollMatches = false;
      const spot = {
        top: MATCH_SCROLL_OFFSET_TOP,
        left: selectedLeft + MATCH_SCROLL_OFFSET_LEFT
      };
      (0, _ui_utils.scrollIntoView)(element, spot, true);
    }
  }
  exports.PDFFindController = PDFFindController;
  function _onFind2(state) {
    if (!state) {
      return;
    }
    if (state.phraseSearch === false) {
      console.error("The `phraseSearch`-parameter was removed, please provide " + "an Array of strings in the `query`-parameter instead.");
      if (typeof state.query === "string") {
        state.query = state.query.match(/\S+/g);
      }
    }
    const pdfDocument = this._pdfDocument;
    const {
      type
    } = state;
    if (_classPrivateFieldGet(this, _state) === null || _classPrivateMethodGet(this, _shouldDirtyMatch, _shouldDirtyMatch2).call(this, state)) {
      this._dirtyMatch = true;
    }
    _classPrivateFieldSet(this, _state, state);
    if (type !== "highlightallchange") {
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, FindState.PENDING);
    }
    this._firstPageCapability.promise.then(() => {
      if (!this._pdfDocument || pdfDocument && this._pdfDocument !== pdfDocument) {
        return;
      }
      _classPrivateMethodGet(this, _extractText, _extractText2).call(this);
      const findbarClosed = !this._highlightMatches;
      const pendingTimeout = !!this._findTimeout;
      if (this._findTimeout) {
        clearTimeout(this._findTimeout);
        this._findTimeout = null;
      }
      if (!type) {
        this._findTimeout = setTimeout(() => {
          _classPrivateMethodGet(this, _nextMatch, _nextMatch2).call(this);
          this._findTimeout = null;
        }, FIND_TIMEOUT);
      } else if (this._dirtyMatch) {
        _classPrivateMethodGet(this, _nextMatch, _nextMatch2).call(this);
      } else if (type === "again") {
        _classPrivateMethodGet(this, _nextMatch, _nextMatch2).call(this);
        if (findbarClosed && _classPrivateFieldGet(this, _state).highlightAll) {
          _classPrivateMethodGet(this, _updateAllPages, _updateAllPages2).call(this);
        }
      } else if (type === "highlightallchange") {
        if (pendingTimeout) {
          _classPrivateMethodGet(this, _nextMatch, _nextMatch2).call(this);
        } else {
          this._highlightMatches = true;
        }
        _classPrivateMethodGet(this, _updateAllPages, _updateAllPages2).call(this);
      } else {
        _classPrivateMethodGet(this, _nextMatch, _nextMatch2).call(this);
      }
    });
  }
  function _reset2() {
    this._highlightMatches = false;
    this._scrollMatches = false;
    this._pdfDocument = null;
    this._pageMatches = [];
    this._pageMatchesLength = [];
    _classPrivateFieldSet(this, _visitedPagesCount, 0);
    _classPrivateFieldSet(this, _state, null);
    this._selected = {
      pageIdx: -1,
      matchIdx: -1
    };
    this._offset = {
      pageIdx: null,
      matchIdx: null,
      wrapped: false
    };
    this._extractTextPromises = [];
    this._pageContents = [];
    this._pageDiffs = [];
    this._hasDiacritics = [];
    this._matchesCountTotal = 0;
    this._pagesToSearch = null;
    this._pendingFindMatches = new Set();
    this._resumePageIdx = null;
    this._dirtyMatch = false;
    clearTimeout(this._findTimeout);
    this._findTimeout = null;
    this._firstPageCapability = new _pdfjsLib.PromiseCapability();
  }
  function _get_query() {
    const {
      query
    } = _classPrivateFieldGet(this, _state);
    if (typeof query === "string") {
      if (query !== this._rawQuery) {
        this._rawQuery = query;
        [this._normalizedQuery] = normalize(query);
      }
      return this._normalizedQuery;
    }
    return (query || []).filter(q => !!q).map(q => normalize(q)[0]);
  }
  function _shouldDirtyMatch2(state) {
    var _this$onIsPageVisible, _this$onIsPageVisible2;
    const newQuery = state.query,
      prevQuery = _classPrivateFieldGet(this, _state).query;
    const newType = typeof newQuery,
      prevType = typeof prevQuery;
    if (newType !== prevType) {
      return true;
    }
    if (newType === "string") {
      if (newQuery !== prevQuery) {
        return true;
      }
    } else if (JSON.stringify(newQuery) !== JSON.stringify(prevQuery)) {
      return true;
    }
    switch (state.type) {
      case "again":
        const pageNumber = this._selected.pageIdx + 1;
        const linkService = this._linkService;
        return pageNumber >= 1 && pageNumber <= linkService.pagesCount && pageNumber !== linkService.page && !((_this$onIsPageVisible = (_this$onIsPageVisible2 = this.onIsPageVisible) === null || _this$onIsPageVisible2 === void 0 ? void 0 : _this$onIsPageVisible2.call(this, pageNumber)) !== null && _this$onIsPageVisible !== void 0 ? _this$onIsPageVisible : true);
      case "highlightallchange":
        return false;
    }
    return true;
  }
  function _isEntireWord2(content, startIdx, length) {
    let match = content.slice(0, startIdx).match(NOT_DIACRITIC_FROM_END_REG_EXP);
    if (match) {
      const first = content.charCodeAt(startIdx);
      const limit = match[1].charCodeAt(0);
      if ((0, _pdf_find_utils.getCharacterType)(first) === (0, _pdf_find_utils.getCharacterType)(limit)) {
        return false;
      }
    }
    match = content.slice(startIdx + length).match(NOT_DIACRITIC_FROM_START_REG_EXP);
    if (match) {
      const last = content.charCodeAt(startIdx + length - 1);
      const limit = match[1].charCodeAt(0);
      if ((0, _pdf_find_utils.getCharacterType)(last) === (0, _pdf_find_utils.getCharacterType)(limit)) {
        return false;
      }
    }
    return true;
  }
  function _calculateRegExpMatch2(query, entireWord, pageIndex, pageContent) {
    const matches = this._pageMatches[pageIndex] = [];
    const matchesLength = this._pageMatchesLength[pageIndex] = [];
    if (!query) {
      return;
    }
    const diffs = this._pageDiffs[pageIndex];
    let match;
    while ((match = query.exec(pageContent)) !== null) {
      if (entireWord && !_classPrivateMethodGet(this, _isEntireWord, _isEntireWord2).call(this, pageContent, match.index, match[0].length)) {
        continue;
      }
      const [matchPos, matchLen] = getOriginalIndex(diffs, match.index, match[0].length);
      if (matchLen) {
        matches.push(matchPos);
        matchesLength.push(matchLen);
      }
    }
  }
  function _convertToRegExpString2(query, hasDiacritics) {
    const {
      matchDiacritics
    } = _classPrivateFieldGet(this, _state);
    let isUnicode = false;
    query = query.replaceAll(SPECIAL_CHARS_REG_EXP, (match, p1, p2, p3, p4, p5) => {
      if (p1) {
        return `[ ]*\\${p1}[ ]*`;
      }
      if (p2) {
        return `[ ]*${p2}[ ]*`;
      }
      if (p3) {
        return "[ ]+";
      }
      if (matchDiacritics) {
        return p4 || p5;
      }
      if (p4) {
        return DIACRITICS_EXCEPTION.has(p4.charCodeAt(0)) ? p4 : "";
      }
      if (hasDiacritics) {
        isUnicode = true;
        return `${p5}\\p{M}*`;
      }
      return p5;
    });
    const trailingSpaces = "[ ]*";
    if (query.endsWith(trailingSpaces)) {
      query = query.slice(0, query.length - trailingSpaces.length);
    }
    if (matchDiacritics) {
      if (hasDiacritics) {
        DIACRITICS_EXCEPTION_STR || (DIACRITICS_EXCEPTION_STR = String.fromCharCode(...DIACRITICS_EXCEPTION));
        isUnicode = true;
        query = `${query}(?=[${DIACRITICS_EXCEPTION_STR}]|[^\\p{M}]|$)`;
      }
    }
    return [isUnicode, query];
  }
  function _calculateMatch2(pageIndex) {
    var _this$visitedPagesCou;
    let query = _classPrivateFieldGet(this, _query);
    if (query.length === 0) {
      return;
    }
    const {
      caseSensitive,
      entireWord
    } = _classPrivateFieldGet(this, _state);
    const pageContent = this._pageContents[pageIndex];
    const hasDiacritics = this._hasDiacritics[pageIndex];
    let isUnicode = false;
    if (typeof query === "string") {
      [isUnicode, query] = _classPrivateMethodGet(this, _convertToRegExpString, _convertToRegExpString2).call(this, query, hasDiacritics);
    } else {
      query = query.sort().reverse().map(q => {
        const [isUnicodePart, queryPart] = _classPrivateMethodGet(this, _convertToRegExpString, _convertToRegExpString2).call(this, q, hasDiacritics);
        isUnicode || (isUnicode = isUnicodePart);
        return `(${queryPart})`;
      }).join("|");
    }
    const flags = `g${isUnicode ? "u" : ""}${caseSensitive ? "" : "i"}`;
    query = query ? new RegExp(query, flags) : null;
    _classPrivateMethodGet(this, _calculateRegExpMatch, _calculateRegExpMatch2).call(this, query, entireWord, pageIndex, pageContent);
    if (_classPrivateFieldGet(this, _state).highlightAll) {
      _classPrivateMethodGet(this, _updatePage, _updatePage2).call(this, pageIndex);
    }
    if (this._resumePageIdx === pageIndex) {
      this._resumePageIdx = null;
      _classPrivateMethodGet(this, _nextPageMatch, _nextPageMatch2).call(this);
    }
    const pageMatchesCount = this._pageMatches[pageIndex].length;
    this._matchesCountTotal += pageMatchesCount;
    if (_classPrivateFieldGet(this, _updateMatchesCountOnProgress)) {
      if (pageMatchesCount > 0) {
        _classPrivateMethodGet(this, _updateUIResultsCount, _updateUIResultsCount2).call(this);
      }
    } else if (_classPrivateFieldSet(this, _visitedPagesCount, (_this$visitedPagesCou = _classPrivateFieldGet(this, _visitedPagesCount), ++_this$visitedPagesCou)) === this._linkService.pagesCount) {
      _classPrivateMethodGet(this, _updateUIResultsCount, _updateUIResultsCount2).call(this);
    }
  }
  function _extractText2() {
    if (this._extractTextPromises.length > 0) {
      return;
    }
    let promise = Promise.resolve();
    const textOptions = {
      disableNormalization: true
    };
    for (let i = 0, ii = this._linkService.pagesCount; i < ii; i++) {
      const extractTextCapability = new _pdfjsLib.PromiseCapability();
      this._extractTextPromises[i] = extractTextCapability.promise;
      promise = promise.then(() => {
        return this._pdfDocument.getPage(i + 1).then(pdfPage => {
          return pdfPage.getTextContent(textOptions);
        }).then(textContent => {
          const strBuf = [];
          for (const textItem of textContent.items) {
            strBuf.push(textItem.str);
            if (textItem.hasEOL) {
              strBuf.push("\n");
            }
          }
          [this._pageContents[i], this._pageDiffs[i], this._hasDiacritics[i]] = normalize(strBuf.join(""));
          extractTextCapability.resolve();
        }, reason => {
          console.error(`Unable to get text content for page ${i + 1}`, reason);
          this._pageContents[i] = "";
          this._pageDiffs[i] = null;
          this._hasDiacritics[i] = false;
          extractTextCapability.resolve();
        });
      });
    }
  }
  function _updatePage2(index) {
    if (this._scrollMatches && this._selected.pageIdx === index) {
      this._linkService.page = index + 1;
    }
    this._eventBus.dispatch("updatetextlayermatches", {
      source: this,
      pageIndex: index
    });
  }
  function _updateAllPages2() {
    this._eventBus.dispatch("updatetextlayermatches", {
      source: this,
      pageIndex: -1
    });
  }
  function _nextMatch2() {
    const previous = _classPrivateFieldGet(this, _state).findPrevious;
    const currentPageIndex = this._linkService.page - 1;
    const numPages = this._linkService.pagesCount;
    this._highlightMatches = true;
    if (this._dirtyMatch) {
      this._dirtyMatch = false;
      this._selected.pageIdx = this._selected.matchIdx = -1;
      this._offset.pageIdx = currentPageIndex;
      this._offset.matchIdx = null;
      this._offset.wrapped = false;
      this._resumePageIdx = null;
      this._pageMatches.length = 0;
      this._pageMatchesLength.length = 0;
      _classPrivateFieldSet(this, _visitedPagesCount, 0);
      this._matchesCountTotal = 0;
      _classPrivateMethodGet(this, _updateAllPages, _updateAllPages2).call(this);
      for (let i = 0; i < numPages; i++) {
        if (this._pendingFindMatches.has(i)) {
          continue;
        }
        this._pendingFindMatches.add(i);
        this._extractTextPromises[i].then(() => {
          this._pendingFindMatches.delete(i);
          _classPrivateMethodGet(this, _calculateMatch, _calculateMatch2).call(this, i);
        });
      }
    }
    const query = _classPrivateFieldGet(this, _query);
    if (query.length === 0) {
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, FindState.FOUND);
      return;
    }
    if (this._resumePageIdx) {
      return;
    }
    const offset = this._offset;
    this._pagesToSearch = numPages;
    if (offset.matchIdx !== null) {
      const numPageMatches = this._pageMatches[offset.pageIdx].length;
      if (!previous && offset.matchIdx + 1 < numPageMatches || previous && offset.matchIdx > 0) {
        offset.matchIdx = previous ? offset.matchIdx - 1 : offset.matchIdx + 1;
        _classPrivateMethodGet(this, _updateMatch, _updateMatch2).call(this, true);
        return;
      }
      _classPrivateMethodGet(this, _advanceOffsetPage, _advanceOffsetPage2).call(this, previous);
    }
    _classPrivateMethodGet(this, _nextPageMatch, _nextPageMatch2).call(this);
  }
  function _matchesReady2(matches) {
    const offset = this._offset;
    const numMatches = matches.length;
    const previous = _classPrivateFieldGet(this, _state).findPrevious;
    if (numMatches) {
      offset.matchIdx = previous ? numMatches - 1 : 0;
      _classPrivateMethodGet(this, _updateMatch, _updateMatch2).call(this, true);
      return true;
    }
    _classPrivateMethodGet(this, _advanceOffsetPage, _advanceOffsetPage2).call(this, previous);
    if (offset.wrapped) {
      offset.matchIdx = null;
      if (this._pagesToSearch < 0) {
        _classPrivateMethodGet(this, _updateMatch, _updateMatch2).call(this, false);
        return true;
      }
    }
    return false;
  }
  function _nextPageMatch2() {
    if (this._resumePageIdx !== null) {
      console.error("There can only be one pending page.");
    }
    let matches = null;
    do {
      const pageIdx = this._offset.pageIdx;
      matches = this._pageMatches[pageIdx];
      if (!matches) {
        this._resumePageIdx = pageIdx;
        break;
      }
    } while (!_classPrivateMethodGet(this, _matchesReady, _matchesReady2).call(this, matches));
  }
  function _advanceOffsetPage2(previous) {
    const offset = this._offset;
    const numPages = this._linkService.pagesCount;
    offset.pageIdx = previous ? offset.pageIdx - 1 : offset.pageIdx + 1;
    offset.matchIdx = null;
    this._pagesToSearch--;
    if (offset.pageIdx >= numPages || offset.pageIdx < 0) {
      offset.pageIdx = previous ? numPages - 1 : 0;
      offset.wrapped = true;
    }
  }
  function _updateMatch2() {
    let found = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
    let state = FindState.NOT_FOUND;
    const wrapped = this._offset.wrapped;
    this._offset.wrapped = false;
    if (found) {
      const previousPage = this._selected.pageIdx;
      this._selected.pageIdx = this._offset.pageIdx;
      this._selected.matchIdx = this._offset.matchIdx;
      state = wrapped ? FindState.WRAPPED : FindState.FOUND;
      if (previousPage !== -1 && previousPage !== this._selected.pageIdx) {
        _classPrivateMethodGet(this, _updatePage, _updatePage2).call(this, previousPage);
      }
    }
    _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, state, _classPrivateFieldGet(this, _state).findPrevious);
    if (this._selected.pageIdx !== -1) {
      this._scrollMatches = true;
      _classPrivateMethodGet(this, _updatePage, _updatePage2).call(this, this._selected.pageIdx);
    }
  }
  function _onFindBarClose2(evt) {
    const pdfDocument = this._pdfDocument;
    this._firstPageCapability.promise.then(() => {
      if (!this._pdfDocument || pdfDocument && this._pdfDocument !== pdfDocument) {
        return;
      }
      if (this._findTimeout) {
        clearTimeout(this._findTimeout);
        this._findTimeout = null;
      }
      if (this._resumePageIdx) {
        this._resumePageIdx = null;
        this._dirtyMatch = true;
      }
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, FindState.FOUND);
      this._highlightMatches = false;
      _classPrivateMethodGet(this, _updateAllPages, _updateAllPages2).call(this);
    });
  }
  function _requestMatchesCount2() {
    const {
      pageIdx,
      matchIdx
    } = this._selected;
    let current = 0,
      total = this._matchesCountTotal;
    if (matchIdx !== -1) {
      for (let i = 0; i < pageIdx; i++) {
        var _this$_pageMatches$i;
        current += ((_this$_pageMatches$i = this._pageMatches[i]) === null || _this$_pageMatches$i === void 0 ? void 0 : _this$_pageMatches$i.length) || 0;
      }
      current += matchIdx + 1;
    }
    if (current < 1 || current > total) {
      current = total = 0;
    }
    return {
      current,
      total
    };
  }
  function _updateUIResultsCount2() {
    this._eventBus.dispatch("updatefindmatchescount", {
      source: this,
      matchesCount: _classPrivateMethodGet(this, _requestMatchesCount, _requestMatchesCount2).call(this)
    });
  }
  function _updateUIState2(state) {
    var _classPrivateFieldGet2, _classPrivateFieldGet3;
    let previous = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
    if (!_classPrivateFieldGet(this, _updateMatchesCountOnProgress) && (_classPrivateFieldGet(this, _visitedPagesCount) !== this._linkService.pagesCount || state === FindState.PENDING)) {
      return;
    }
    this._eventBus.dispatch("updatefindcontrolstate", {
      source: this,
      state,
      previous,
      matchesCount: _classPrivateMethodGet(this, _requestMatchesCount, _requestMatchesCount2).call(this),
      rawQuery: (_classPrivateFieldGet2 = (_classPrivateFieldGet3 = _classPrivateFieldGet(this, _state)) === null || _classPrivateFieldGet3 === void 0 ? void 0 : _classPrivateFieldGet3.query) !== null && _classPrivateFieldGet2 !== void 0 ? _classPrivateFieldGet2 : null
    });
  }
  
  /***/ }),
  /* 197 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var global = __webpack_require__(5);
  var uncurryThis = __webpack_require__(15);
  var isForced = __webpack_require__(69);
  var inheritIfRequired = __webpack_require__(125);
  var createNonEnumerableProperty = __webpack_require__(45);
  var getOwnPropertyNames = (__webpack_require__(59).f);
  var isPrototypeOf = __webpack_require__(26);
  var isRegExp = __webpack_require__(156);
  var toString = __webpack_require__(118);
  var getRegExpFlags = __webpack_require__(157);
  var stickyHelpers = __webpack_require__(139);
  var proxyAccessor = __webpack_require__(124);
  var defineBuiltIn = __webpack_require__(49);
  var fails = __webpack_require__(8);
  var hasOwn = __webpack_require__(40);
  var enforceInternalState = (__webpack_require__(53).enforce);
  var setSpecies = __webpack_require__(75);
  var wellKnownSymbol = __webpack_require__(35);
  var UNSUPPORTED_DOT_ALL = __webpack_require__(140);
  var UNSUPPORTED_NCG = __webpack_require__(141);
  var MATCH = wellKnownSymbol('match');
  var NativeRegExp = global.RegExp;
  var RegExpPrototype = NativeRegExp.prototype;
  var SyntaxError = global.SyntaxError;
  var exec = uncurryThis(RegExpPrototype.exec);
  var charAt = uncurryThis(''.charAt);
  var replace = uncurryThis(''.replace);
  var stringIndexOf = uncurryThis(''.indexOf);
  var stringSlice = uncurryThis(''.slice);
  var IS_NCG = /^\?<[^\s\d!#%&*+<=>@^][^\s!#%&*+<=>@^]*>/;
  var re1 = /a/g;
  var re2 = /a/g;
  var CORRECT_NEW = new NativeRegExp(re1) !== re1;
  var MISSED_STICKY = stickyHelpers.MISSED_STICKY;
  var UNSUPPORTED_Y = stickyHelpers.UNSUPPORTED_Y;
  var BASE_FORCED = DESCRIPTORS && (!CORRECT_NEW || MISSED_STICKY || UNSUPPORTED_DOT_ALL || UNSUPPORTED_NCG || fails(function () {
   re2[MATCH] = false;
   return NativeRegExp(re1) !== re1 || NativeRegExp(re2) === re2 || String(NativeRegExp(re1, 'i')) !== '/a/i';
  }));
  var handleDotAll = function (string) {
   var length = string.length;
   var index = 0;
   var result = '';
   var brackets = false;
   var chr;
   for (; index <= length; index++) {
    chr = charAt(string, index);
    if (chr === '\\') {
     result += chr + charAt(string, ++index);
     continue;
    }
    if (!brackets && chr === '.') {
     result += '[\\s\\S]';
    } else {
     if (chr === '[') {
      brackets = true;
     } else if (chr === ']') {
      brackets = false;
     }
     result += chr;
    }
   }
   return result;
  };
  var handleNCG = function (string) {
   var length = string.length;
   var index = 0;
   var result = '';
   var named = [];
   var names = {};
   var brackets = false;
   var ncg = false;
   var groupid = 0;
   var groupname = '';
   var chr;
   for (; index <= length; index++) {
    chr = charAt(string, index);
    if (chr === '\\') {
     chr += charAt(string, ++index);
    } else if (chr === ']') {
     brackets = false;
    } else if (!brackets)
     switch (true) {
     case chr === '[':
      brackets = true;
      break;
     case chr === '(':
      if (exec(IS_NCG, stringSlice(string, index + 1))) {
       index += 2;
       ncg = true;
      }
      result += chr;
      groupid++;
      continue;
     case chr === '>' && ncg:
      if (groupname === '' || hasOwn(names, groupname)) {
       throw new SyntaxError('Invalid capture group name');
      }
      names[groupname] = true;
      named[named.length] = [
       groupname,
       groupid
      ];
      ncg = false;
      groupname = '';
      continue;
     }
    if (ncg)
     groupname += chr;
    else
     result += chr;
   }
   return [
    result,
    named
   ];
  };
  if (isForced('RegExp', BASE_FORCED)) {
   var RegExpWrapper = function RegExp(pattern, flags) {
    var thisIsRegExp = isPrototypeOf(RegExpPrototype, this);
    var patternIsRegExp = isRegExp(pattern);
    var flagsAreUndefined = flags === undefined;
    var groups = [];
    var rawPattern = pattern;
    var rawFlags, dotAll, sticky, handled, result, state;
    if (!thisIsRegExp && patternIsRegExp && flagsAreUndefined && pattern.constructor === RegExpWrapper) {
     return pattern;
    }
    if (patternIsRegExp || isPrototypeOf(RegExpPrototype, pattern)) {
     pattern = pattern.source;
     if (flagsAreUndefined)
      flags = getRegExpFlags(rawPattern);
    }
    pattern = pattern === undefined ? '' : toString(pattern);
    flags = flags === undefined ? '' : toString(flags);
    rawPattern = pattern;
    if (UNSUPPORTED_DOT_ALL && 'dotAll' in re1) {
     dotAll = !!flags && stringIndexOf(flags, 's') > -1;
     if (dotAll)
      flags = replace(flags, /s/g, '');
    }
    rawFlags = flags;
    if (MISSED_STICKY && 'sticky' in re1) {
     sticky = !!flags && stringIndexOf(flags, 'y') > -1;
     if (sticky && UNSUPPORTED_Y)
      flags = replace(flags, /y/g, '');
    }
    if (UNSUPPORTED_NCG) {
     handled = handleNCG(pattern);
     pattern = handled[0];
     groups = handled[1];
    }
    result = inheritIfRequired(NativeRegExp(pattern, flags), thisIsRegExp ? this : RegExpPrototype, RegExpWrapper);
    if (dotAll || sticky || groups.length) {
     state = enforceInternalState(result);
     if (dotAll) {
      state.dotAll = true;
      state.raw = RegExpWrapper(handleDotAll(pattern), rawFlags);
     }
     if (sticky)
      state.sticky = true;
     if (groups.length)
      state.groups = groups;
    }
    if (pattern !== rawPattern)
     try {
      createNonEnumerableProperty(result, 'source', rawPattern === '' ? '(?:)' : rawPattern);
     } catch (error) {
     }
    return result;
   };
   for (var keys = getOwnPropertyNames(NativeRegExp), index = 0; keys.length > index;) {
    proxyAccessor(RegExpWrapper, NativeRegExp, keys[index++]);
   }
   RegExpPrototype.constructor = RegExpWrapper;
   RegExpWrapper.prototype = RegExpPrototype;
   defineBuiltIn(global, 'RegExp', RegExpWrapper, { constructor: true });
  }
  setSpecies('RegExp');
  
  /***/ }),
  /* 198 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var DESCRIPTORS = __webpack_require__(7);
  var UNSUPPORTED_DOT_ALL = __webpack_require__(140);
  var classof = __webpack_require__(16);
  var defineBuiltInAccessor = __webpack_require__(76);
  var getInternalState = (__webpack_require__(53).get);
  var RegExpPrototype = RegExp.prototype;
  var $TypeError = TypeError;
  if (DESCRIPTORS && UNSUPPORTED_DOT_ALL) {
   defineBuiltInAccessor(RegExpPrototype, 'dotAll', {
    configurable: true,
    get: function dotAll() {
     if (this === RegExpPrototype)
      return undefined;
     if (classof(this) === 'RegExp') {
      return !!getInternalState(this).dotAll;
     }
     throw $TypeError('Incompatible receiver, RegExp required');
    }
   });
  }
  
  /***/ }),
  /* 199 */
  /***/ ((__unused_webpack_module, exports) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.CharacterType = void 0;
  exports.getCharacterType = getCharacterType;
  exports.getNormalizeWithNFKC = getNormalizeWithNFKC;
  const CharacterType = {
    SPACE: 0,
    ALPHA_LETTER: 1,
    PUNCT: 2,
    HAN_LETTER: 3,
    KATAKANA_LETTER: 4,
    HIRAGANA_LETTER: 5,
    HALFWIDTH_KATAKANA_LETTER: 6,
    THAI_LETTER: 7
  };
  exports.CharacterType = CharacterType;
  function isAlphabeticalScript(charCode) {
    return charCode < 0x2e80;
  }
  function isAscii(charCode) {
    return (charCode & 0xff80) === 0;
  }
  function isAsciiAlpha(charCode) {
    return charCode >= 0x61 && charCode <= 0x7a || charCode >= 0x41 && charCode <= 0x5a;
  }
  function isAsciiDigit(charCode) {
    return charCode >= 0x30 && charCode <= 0x39;
  }
  function isAsciiSpace(charCode) {
    return charCode === 0x20 || charCode === 0x09 || charCode === 0x0d || charCode === 0x0a;
  }
  function isHan(charCode) {
    return charCode >= 0x3400 && charCode <= 0x9fff || charCode >= 0xf900 && charCode <= 0xfaff;
  }
  function isKatakana(charCode) {
    return charCode >= 0x30a0 && charCode <= 0x30ff;
  }
  function isHiragana(charCode) {
    return charCode >= 0x3040 && charCode <= 0x309f;
  }
  function isHalfwidthKatakana(charCode) {
    return charCode >= 0xff60 && charCode <= 0xff9f;
  }
  function isThai(charCode) {
    return (charCode & 0xff80) === 0x0e00;
  }
  function getCharacterType(charCode) {
    if (isAlphabeticalScript(charCode)) {
      if (isAscii(charCode)) {
        if (isAsciiSpace(charCode)) {
          return CharacterType.SPACE;
        } else if (isAsciiAlpha(charCode) || isAsciiDigit(charCode) || charCode === 0x5f) {
          return CharacterType.ALPHA_LETTER;
        }
        return CharacterType.PUNCT;
      } else if (isThai(charCode)) {
        return CharacterType.THAI_LETTER;
      } else if (charCode === 0xa0) {
        return CharacterType.SPACE;
      }
      return CharacterType.ALPHA_LETTER;
    }
    if (isHan(charCode)) {
      return CharacterType.HAN_LETTER;
    } else if (isKatakana(charCode)) {
      return CharacterType.KATAKANA_LETTER;
    } else if (isHiragana(charCode)) {
      return CharacterType.HIRAGANA_LETTER;
    } else if (isHalfwidthKatakana(charCode)) {
      return CharacterType.HALFWIDTH_KATAKANA_LETTER;
    }
    return CharacterType.ALPHA_LETTER;
  }
  let NormalizeWithNFKC;
  function getNormalizeWithNFKC() {
    NormalizeWithNFKC || (NormalizeWithNFKC = ` ¨ª¯²-µ¸-º¼-¾Ĳ-ĳĿ-ŀŉſǄ-ǌǱ-ǳʰ-ʸ˘-˝ˠ-ˤʹͺ;΄-΅·ϐ-ϖϰ-ϲϴ-ϵϹևٵ-ٸक़-य़ড়-ঢ়য়ਲ਼ਸ਼ਖ਼-ਜ਼ਫ਼ଡ଼-ଢ଼ำຳໜ-ໝ༌གྷཌྷདྷབྷཛྷཀྵჼᴬ-ᴮᴰ-ᴺᴼ-ᵍᵏ-ᵪᵸᶛ-ᶿẚ-ẛάέήίόύώΆ᾽-῁ΈΉ῍-῏ΐΊ῝-῟ΰΎ῭-`ΌΏ´-῾ - ‑‗․-… ″-‴‶-‷‼‾⁇-⁉⁗ ⁰-ⁱ⁴-₎ₐ-ₜ₨℀-℃℅-ℇ℉-ℓℕ-№ℙ-ℝ℠-™ℤΩℨK-ℭℯ-ℱℳ-ℹ℻-⅀ⅅ-ⅉ⅐-ⅿ↉∬-∭∯-∰〈-〉①-⓪⨌⩴-⩶⫝̸ⱼ-ⱽⵯ⺟⻳⼀-⿕　〶〸-〺゛-゜ゟヿㄱ-ㆎ㆒-㆟㈀-㈞㈠-㉇㉐-㉾㊀-㏿ꚜ-ꚝꝰꟲ-ꟴꟸ-ꟹꭜ-ꭟꭩ豈-嗀塚晴凞-羽蘒諸逸-都飯-舘並-龎ﬀ-ﬆﬓ-ﬗיִײַ-זּטּ-לּמּנּ-סּףּ-פּצּ-ﮱﯓ-ﴽﵐ-ﶏﶒ-ﷇﷰ-﷼︐-︙︰-﹄﹇-﹒﹔-﹦﹨-﹫ﹰ-ﹲﹴﹶ-ﻼ！-ﾾￂ-ￇￊ-ￏￒ-ￗￚ-ￜ￠-￦`);
    return NormalizeWithNFKC;
  }
  
  /***/ }),
  /* 200 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFHistory = void 0;
  exports.isDestArraysEqual = isDestArraysEqual;
  exports.isDestHashesEqual = isDestHashesEqual;
  __webpack_require__(2);
  var _ui_utils = __webpack_require__(148);
  var _event_utils = __webpack_require__(184);
  const HASH_CHANGE_TIMEOUT = 1000;
  const POSITION_UPDATED_THRESHOLD = 50;
  const UPDATE_VIEWAREA_TIMEOUT = 1000;
  function getCurrentHash() {
    return document.location.hash;
  }
  class PDFHistory {
    constructor(_ref) {
      let {
        linkService,
        eventBus
      } = _ref;
      this.linkService = linkService;
      this.eventBus = eventBus;
      this._initialized = false;
      this._fingerprint = "";
      this.reset();
      this._boundEvents = null;
      this.eventBus._on("pagesinit", () => {
        this._isPagesLoaded = false;
        this.eventBus._on("pagesloaded", evt => {
          this._isPagesLoaded = !!evt.pagesCount;
        }, {
          once: true
        });
      });
    }
    initialize(_ref2) {
      let {
        fingerprint,
        resetHistory = false,
        updateUrl = false
      } = _ref2;
      if (!fingerprint || typeof fingerprint !== "string") {
        console.error('PDFHistory.initialize: The "fingerprint" must be a non-empty string.');
        return;
      }
      if (this._initialized) {
        this.reset();
      }
      const reInitialized = this._fingerprint !== "" && this._fingerprint !== fingerprint;
      this._fingerprint = fingerprint;
      this._updateUrl = updateUrl === true;
      this._initialized = true;
      this._bindEvents();
      const state = window.history.state;
      this._popStateInProgress = false;
      this._blockHashChange = 0;
      this._currentHash = getCurrentHash();
      this._numPositionUpdates = 0;
      this._uid = this._maxUid = 0;
      this._destination = null;
      this._position = null;
      if (!this._isValidState(state, true) || resetHistory) {
        const {
          hash,
          page,
          rotation
        } = this._parseCurrentHash(true);
        if (!hash || reInitialized || resetHistory) {
          this._pushOrReplaceState(null, true);
          return;
        }
        this._pushOrReplaceState({
          hash,
          page,
          rotation
        }, true);
        return;
      }
      const destination = state.destination;
      this._updateInternalState(destination, state.uid, true);
      if (destination.rotation !== undefined) {
        this._initialRotation = destination.rotation;
      }
      if (destination.dest) {
        this._initialBookmark = JSON.stringify(destination.dest);
        this._destination.page = null;
      } else if (destination.hash) {
        this._initialBookmark = destination.hash;
      } else if (destination.page) {
        this._initialBookmark = `page=${destination.page}`;
      }
    }
    reset() {
      if (this._initialized) {
        this._pageHide();
        this._initialized = false;
        this._unbindEvents();
      }
      if (this._updateViewareaTimeout) {
        clearTimeout(this._updateViewareaTimeout);
        this._updateViewareaTimeout = null;
      }
      this._initialBookmark = null;
      this._initialRotation = null;
    }
    push(_ref3) {
      let {
        namedDest = null,
        explicitDest,
        pageNumber
      } = _ref3;
      if (!this._initialized) {
        return;
      }
      if (namedDest && typeof namedDest !== "string") {
        console.error("PDFHistory.push: " + `"${namedDest}" is not a valid namedDest parameter.`);
        return;
      } else if (!Array.isArray(explicitDest)) {
        console.error("PDFHistory.push: " + `"${explicitDest}" is not a valid explicitDest parameter.`);
        return;
      } else if (!this._isValidPage(pageNumber)) {
        if (pageNumber !== null || this._destination) {
          console.error("PDFHistory.push: " + `"${pageNumber}" is not a valid pageNumber parameter.`);
          return;
        }
      }
      const hash = namedDest || JSON.stringify(explicitDest);
      if (!hash) {
        return;
      }
      let forceReplace = false;
      if (this._destination && (isDestHashesEqual(this._destination.hash, hash) || isDestArraysEqual(this._destination.dest, explicitDest))) {
        if (this._destination.page) {
          return;
        }
        forceReplace = true;
      }
      if (this._popStateInProgress && !forceReplace) {
        return;
      }
      this._pushOrReplaceState({
        dest: explicitDest,
        hash,
        page: pageNumber,
        rotation: this.linkService.rotation
      }, forceReplace);
      if (!this._popStateInProgress) {
        this._popStateInProgress = true;
        Promise.resolve().then(() => {
          this._popStateInProgress = false;
        });
      }
    }
    pushPage(pageNumber) {
      var _this$_destination;
      if (!this._initialized) {
        return;
      }
      if (!this._isValidPage(pageNumber)) {
        console.error(`PDFHistory.pushPage: "${pageNumber}" is not a valid page number.`);
        return;
      }
      if (((_this$_destination = this._destination) === null || _this$_destination === void 0 ? void 0 : _this$_destination.page) === pageNumber) {
        return;
      }
      if (this._popStateInProgress) {
        return;
      }
      this._pushOrReplaceState({
        dest: null,
        hash: `page=${pageNumber}`,
        page: pageNumber,
        rotation: this.linkService.rotation
      });
      if (!this._popStateInProgress) {
        this._popStateInProgress = true;
        Promise.resolve().then(() => {
          this._popStateInProgress = false;
        });
      }
    }
    pushCurrentPosition() {
      if (!this._initialized || this._popStateInProgress) {
        return;
      }
      this._tryPushCurrentPosition();
    }
    back() {
      if (!this._initialized || this._popStateInProgress) {
        return;
      }
      const state = window.history.state;
      if (this._isValidState(state) && state.uid > 0) {
        window.history.back();
      }
    }
    forward() {
      if (!this._initialized || this._popStateInProgress) {
        return;
      }
      const state = window.history.state;
      if (this._isValidState(state) && state.uid < this._maxUid) {
        window.history.forward();
      }
    }
    get popStateInProgress() {
      return this._initialized && (this._popStateInProgress || this._blockHashChange > 0);
    }
    get initialBookmark() {
      return this._initialized ? this._initialBookmark : null;
    }
    get initialRotation() {
      return this._initialized ? this._initialRotation : null;
    }
    _pushOrReplaceState(destination) {
      let forceReplace = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      const shouldReplace = forceReplace || !this._destination;
      const newState = {
        fingerprint: this._fingerprint,
        uid: shouldReplace ? this._uid : this._uid + 1,
        destination
      };
      this._updateInternalState(destination, newState.uid);
      let newUrl;
      if (this._updateUrl && destination !== null && destination !== void 0 && destination.hash) {
        const baseUrl = document.location.href.split("#")[0];
        if (!baseUrl.startsWith("file://")) {
          newUrl = `${baseUrl}#${destination.hash}`;
        }
      }
      if (shouldReplace) {
        window.history.replaceState(newState, "", newUrl);
      } else {
        window.history.pushState(newState, "", newUrl);
      }
    }
    _tryPushCurrentPosition() {
      let temporary = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      if (!this._position) {
        return;
      }
      let position = this._position;
      if (temporary) {
        position = Object.assign(Object.create(null), this._position);
        position.temporary = true;
      }
      if (!this._destination) {
        this._pushOrReplaceState(position);
        return;
      }
      if (this._destination.temporary) {
        this._pushOrReplaceState(position, true);
        return;
      }
      if (this._destination.hash === position.hash) {
        return;
      }
      if (!this._destination.page && (POSITION_UPDATED_THRESHOLD <= 0 || this._numPositionUpdates <= POSITION_UPDATED_THRESHOLD)) {
        return;
      }
      let forceReplace = false;
      if (this._destination.page >= position.first && this._destination.page <= position.page) {
        if (this._destination.dest !== undefined || !this._destination.first) {
          return;
        }
        forceReplace = true;
      }
      this._pushOrReplaceState(position, forceReplace);
    }
    _isValidPage(val) {
      return Number.isInteger(val) && val > 0 && val <= this.linkService.pagesCount;
    }
    _isValidState(state) {
      let checkReload = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      if (!state) {
        return false;
      }
      if (state.fingerprint !== this._fingerprint) {
        if (checkReload) {
          if (typeof state.fingerprint !== "string" || state.fingerprint.length !== this._fingerprint.length) {
            return false;
          }
          const [perfEntry] = performance.getEntriesByType("navigation");
          if ((perfEntry === null || perfEntry === void 0 ? void 0 : perfEntry.type) !== "reload") {
            return false;
          }
        } else {
          return false;
        }
      }
      if (!Number.isInteger(state.uid) || state.uid < 0) {
        return false;
      }
      if (state.destination === null || typeof state.destination !== "object") {
        return false;
      }
      return true;
    }
    _updateInternalState(destination, uid) {
      let removeTemporary = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
      if (this._updateViewareaTimeout) {
        clearTimeout(this._updateViewareaTimeout);
        this._updateViewareaTimeout = null;
      }
      if (removeTemporary && destination !== null && destination !== void 0 && destination.temporary) {
        delete destination.temporary;
      }
      this._destination = destination;
      this._uid = uid;
      this._maxUid = Math.max(this._maxUid, uid);
      this._numPositionUpdates = 0;
    }
    _parseCurrentHash() {
      let checkNameddest = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      const hash = unescape(getCurrentHash()).substring(1);
      const params = (0, _ui_utils.parseQueryString)(hash);
      const nameddest = params.get("nameddest") || "";
      let page = params.get("page") | 0;
      if (!this._isValidPage(page) || checkNameddest && nameddest.length > 0) {
        page = null;
      }
      return {
        hash,
        page,
        rotation: this.linkService.rotation
      };
    }
    _updateViewarea(_ref4) {
      let {
        location
      } = _ref4;
      if (this._updateViewareaTimeout) {
        clearTimeout(this._updateViewareaTimeout);
        this._updateViewareaTimeout = null;
      }
      this._position = {
        hash: location.pdfOpenParams.substring(1),
        page: this.linkService.page,
        first: location.pageNumber,
        rotation: location.rotation
      };
      if (this._popStateInProgress) {
        return;
      }
      if (POSITION_UPDATED_THRESHOLD > 0 && this._isPagesLoaded && this._destination && !this._destination.page) {
        this._numPositionUpdates++;
      }
      if (UPDATE_VIEWAREA_TIMEOUT > 0) {
        this._updateViewareaTimeout = setTimeout(() => {
          if (!this._popStateInProgress) {
            this._tryPushCurrentPosition(true);
          }
          this._updateViewareaTimeout = null;
        }, UPDATE_VIEWAREA_TIMEOUT);
      }
    }
    _popState(_ref5) {
      let {
        state
      } = _ref5;
      const newHash = getCurrentHash(),
        hashChanged = this._currentHash !== newHash;
      this._currentHash = newHash;
      if (!state) {
        this._uid++;
        const {
          hash,
          page,
          rotation
        } = this._parseCurrentHash();
        this._pushOrReplaceState({
          hash,
          page,
          rotation
        }, true);
        return;
      }
      if (!this._isValidState(state)) {
        return;
      }
      this._popStateInProgress = true;
      if (hashChanged) {
        this._blockHashChange++;
        (0, _event_utils.waitOnEventOrTimeout)({
          target: window,
          name: "hashchange",
          delay: HASH_CHANGE_TIMEOUT
        }).then(() => {
          this._blockHashChange--;
        });
      }
      const destination = state.destination;
      this._updateInternalState(destination, state.uid, true);
      if ((0, _ui_utils.isValidRotation)(destination.rotation)) {
        this.linkService.rotation = destination.rotation;
      }
      if (destination.dest) {
        this.linkService.goToDestination(destination.dest);
      } else if (destination.hash) {
        this.linkService.setHash(destination.hash);
      } else if (destination.page) {
        this.linkService.page = destination.page;
      }
      Promise.resolve().then(() => {
        this._popStateInProgress = false;
      });
    }
    _pageHide() {
      if (!this._destination || this._destination.temporary) {
        this._tryPushCurrentPosition();
      }
    }
    _bindEvents() {
      if (this._boundEvents) {
        return;
      }
      this._boundEvents = {
        updateViewarea: this._updateViewarea.bind(this),
        popState: this._popState.bind(this),
        pageHide: this._pageHide.bind(this)
      };
      this.eventBus._on("updateviewarea", this._boundEvents.updateViewarea);
      window.addEventListener("popstate", this._boundEvents.popState);
      window.addEventListener("pagehide", this._boundEvents.pageHide);
    }
    _unbindEvents() {
      if (!this._boundEvents) {
        return;
      }
      this.eventBus._off("updateviewarea", this._boundEvents.updateViewarea);
      window.removeEventListener("popstate", this._boundEvents.popState);
      window.removeEventListener("pagehide", this._boundEvents.pageHide);
      this._boundEvents = null;
    }
  }
  exports.PDFHistory = PDFHistory;
  function isDestHashesEqual(destHash, pushHash) {
    if (typeof destHash !== "string" || typeof pushHash !== "string") {
      return false;
    }
    if (destHash === pushHash) {
      return true;
    }
    const nameddest = (0, _ui_utils.parseQueryString)(destHash).get("nameddest");
    if (nameddest === pushHash) {
      return true;
    }
    return false;
  }
  function isDestArraysEqual(firstDest, secondDest) {
    function isEntryEqual(first, second) {
      if (typeof first !== typeof second) {
        return false;
      }
      if (Array.isArray(first) || Array.isArray(second)) {
        return false;
      }
      if (first !== null && typeof first === "object" && second !== null) {
        if (Object.keys(first).length !== Object.keys(second).length) {
          return false;
        }
        for (const key in first) {
          if (!isEntryEqual(first[key], second[key])) {
            return false;
          }
        }
        return true;
      }
      return first === second || Number.isNaN(first) && Number.isNaN(second);
    }
    if (!(Array.isArray(firstDest) && Array.isArray(secondDest))) {
      return false;
    }
    if (firstDest.length !== secondDest.length) {
      return false;
    }
    for (let i = 0, ii = firstDest.length; i < ii; i++) {
      if (!isEntryEqual(firstDest[i], secondDest[i])) {
        return false;
      }
    }
    return true;
  }
  
  /***/ }),
  /* 201 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFLayerViewer = void 0;
  __webpack_require__(2);
  __webpack_require__(142);
  __webpack_require__(122);
  var _base_tree_viewer = __webpack_require__(191);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _updateLayers = /*#__PURE__*/new WeakSet();
  class PDFLayerViewer extends _base_tree_viewer.BaseTreeViewer {
    constructor(options) {
      super(options);
      _classPrivateMethodInitSpec(this, _updateLayers);
      this.l10n = options.l10n;
      this.eventBus._on("optionalcontentconfigchanged", evt => {
        _classPrivateMethodGet(this, _updateLayers, _updateLayers2).call(this, evt.promise);
      });
      this.eventBus._on("resetlayers", () => {
        _classPrivateMethodGet(this, _updateLayers, _updateLayers2).call(this);
      });
      this.eventBus._on("togglelayerstree", this._toggleAllTreeItems.bind(this));
    }
    reset() {
      super.reset();
      this._optionalContentConfig = null;
      this._optionalContentHash = null;
    }
    _dispatchEvent(layersCount) {
      this.eventBus.dispatch("layersloaded", {
        source: this,
        layersCount
      });
    }
    _bindLink(element, _ref) {
      let {
        groupId,
        input
      } = _ref;
      const setVisibility = () => {
        this._optionalContentConfig.setVisibility(groupId, input.checked);
        this._optionalContentHash = this._optionalContentConfig.getHash();
        this.eventBus.dispatch("optionalcontentconfig", {
          source: this,
          promise: Promise.resolve(this._optionalContentConfig)
        });
      };
      element.onclick = evt => {
        if (evt.target === input) {
          setVisibility();
          return true;
        } else if (evt.target !== element) {
          return true;
        }
        input.checked = !input.checked;
        setVisibility();
        return false;
      };
    }
    async _setNestedName(element, _ref2) {
      let {
        name = null
      } = _ref2;
      if (typeof name === "string") {
        element.textContent = this._normalizeTextContent(name);
        return;
      }
      element.textContent = await this.l10n.get("additional_layers");
      element.style.fontStyle = "italic";
    }
    _addToggleButton(div, _ref3) {
      let {
        name = null
      } = _ref3;
      super._addToggleButton(div, name === null);
    }
    _toggleAllTreeItems() {
      if (!this._optionalContentConfig) {
        return;
      }
      super._toggleAllTreeItems();
    }
    render(_ref4) {
      let {
        optionalContentConfig,
        pdfDocument
      } = _ref4;
      if (this._optionalContentConfig) {
        this.reset();
      }
      this._optionalContentConfig = optionalContentConfig || null;
      this._pdfDocument = pdfDocument || null;
      const groups = optionalContentConfig === null || optionalContentConfig === void 0 ? void 0 : optionalContentConfig.getOrder();
      if (!groups) {
        this._dispatchEvent(0);
        return;
      }
      this._optionalContentHash = optionalContentConfig.getHash();
      const fragment = document.createDocumentFragment(),
        queue = [{
          parent: fragment,
          groups
        }];
      let layersCount = 0,
        hasAnyNesting = false;
      while (queue.length > 0) {
        const levelData = queue.shift();
        for (const groupId of levelData.groups) {
          const div = document.createElement("div");
          div.className = "treeItem";
          const element = document.createElement("a");
          div.append(element);
          if (typeof groupId === "object") {
            hasAnyNesting = true;
            this._addToggleButton(div, groupId);
            this._setNestedName(element, groupId);
            const itemsDiv = document.createElement("div");
            itemsDiv.className = "treeItems";
            div.append(itemsDiv);
            queue.push({
              parent: itemsDiv,
              groups: groupId.order
            });
          } else {
            const group = optionalContentConfig.getGroup(groupId);
            const input = document.createElement("input");
            this._bindLink(element, {
              groupId,
              input
            });
            input.type = "checkbox";
            input.checked = group.visible;
            const label = document.createElement("label");
            label.textContent = this._normalizeTextContent(group.name);
            label.append(input);
            element.append(label);
            layersCount++;
          }
          levelData.parent.append(div);
        }
      }
      this._finishRendering(fragment, layersCount, hasAnyNesting);
    }
  }
  exports.PDFLayerViewer = PDFLayerViewer;
  async function _updateLayers2() {
    let promise = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
    if (!this._optionalContentConfig) {
      return;
    }
    const pdfDocument = this._pdfDocument;
    const optionalContentConfig = await (promise || pdfDocument.getOptionalContentConfig());
    if (pdfDocument !== this._pdfDocument) {
      return;
    }
    if (promise) {
      if (optionalContentConfig.getHash() === this._optionalContentHash) {
        return;
      }
    } else {
      this.eventBus.dispatch("optionalcontentconfig", {
        source: this,
        promise: Promise.resolve(optionalContentConfig)
      });
    }
    this.render({
      optionalContentConfig,
      pdfDocument: this._pdfDocument
    });
  }
  
  /***/ }),
  /* 202 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFOutlineViewer = void 0;
  __webpack_require__(142);
  __webpack_require__(2);
  __webpack_require__(122);
  var _base_tree_viewer = __webpack_require__(191);
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  class PDFOutlineViewer extends _base_tree_viewer.BaseTreeViewer {
    constructor(options) {
      super(options);
      this.linkService = options.linkService;
      this.downloadManager = options.downloadManager;
      this.eventBus._on("toggleoutlinetree", this._toggleAllTreeItems.bind(this));
      this.eventBus._on("currentoutlineitem", this._currentOutlineItem.bind(this));
      this.eventBus._on("pagechanging", evt => {
        this._currentPageNumber = evt.pageNumber;
      });
      this.eventBus._on("pagesloaded", evt => {
        this._isPagesLoaded = !!evt.pagesCount;
        if (this._currentOutlineItemCapability && !this._currentOutlineItemCapability.settled) {
          this._currentOutlineItemCapability.resolve(this._isPagesLoaded);
        }
      });
      this.eventBus._on("sidebarviewchanged", evt => {
        this._sidebarView = evt.view;
      });
    }
    reset() {
      super.reset();
      this._outline = null;
      this._pageNumberToDestHashCapability = null;
      this._currentPageNumber = 1;
      this._isPagesLoaded = null;
      if (this._currentOutlineItemCapability && !this._currentOutlineItemCapability.settled) {
        this._currentOutlineItemCapability.resolve(false);
      }
      this._currentOutlineItemCapability = null;
    }
    _dispatchEvent(outlineCount) {
      var _this$_pdfDocument;
      this._currentOutlineItemCapability = new _pdfjsLib.PromiseCapability();
      if (outlineCount === 0 || (_this$_pdfDocument = this._pdfDocument) !== null && _this$_pdfDocument !== void 0 && _this$_pdfDocument.loadingParams.disableAutoFetch) {
        this._currentOutlineItemCapability.resolve(false);
      } else if (this._isPagesLoaded !== null) {
        this._currentOutlineItemCapability.resolve(this._isPagesLoaded);
      }
      this.eventBus.dispatch("outlineloaded", {
        source: this,
        outlineCount,
        currentOutlineItemPromise: this._currentOutlineItemCapability.promise
      });
    }
    _bindLink(element, _ref) {
      let {
        url,
        newWindow,
        action,
        attachment,
        dest,
        setOCGState
      } = _ref;
      const {
        linkService
      } = this;
      if (url) {
        linkService.addLinkAttributes(element, url, newWindow);
        return;
      }
      if (action) {
        element.href = linkService.getAnchorUrl("");
        element.onclick = () => {
          linkService.executeNamedAction(action);
          return false;
        };
        return;
      }
      if (attachment) {
        element.href = linkService.getAnchorUrl("");
        element.onclick = () => {
          this.downloadManager.openOrDownloadData(element, attachment.content, attachment.filename);
          return false;
        };
        return;
      }
      if (setOCGState) {
        element.href = linkService.getAnchorUrl("");
        element.onclick = () => {
          linkService.executeSetOCGState(setOCGState);
          return false;
        };
        return;
      }
      element.href = linkService.getDestinationHash(dest);
      element.onclick = evt => {
        this._updateCurrentTreeItem(evt.target.parentNode);
        if (dest) {
          linkService.goToDestination(dest);
        }
        return false;
      };
    }
    _setStyles(element, _ref2) {
      let {
        bold,
        italic
      } = _ref2;
      if (bold) {
        element.style.fontWeight = "bold";
      }
      if (italic) {
        element.style.fontStyle = "italic";
      }
    }
    _addToggleButton(div, _ref3) {
      let {
        count,
        items
      } = _ref3;
      let hidden = false;
      if (count < 0) {
        let totalCount = items.length;
        if (totalCount > 0) {
          const queue = [...items];
          while (queue.length > 0) {
            const {
              count: nestedCount,
              items: nestedItems
            } = queue.shift();
            if (nestedCount > 0 && nestedItems.length > 0) {
              totalCount += nestedItems.length;
              queue.push(...nestedItems);
            }
          }
        }
        if (Math.abs(count) === totalCount) {
          hidden = true;
        }
      }
      super._addToggleButton(div, hidden);
    }
    _toggleAllTreeItems() {
      if (!this._outline) {
        return;
      }
      super._toggleAllTreeItems();
    }
    render(_ref4) {
      let {
        outline,
        pdfDocument
      } = _ref4;
      if (this._outline) {
        this.reset();
      }
      this._outline = outline || null;
      this._pdfDocument = pdfDocument || null;
      if (!outline) {
        this._dispatchEvent(0);
        return;
      }
      const fragment = document.createDocumentFragment();
      const queue = [{
        parent: fragment,
        items: outline
      }];
      let outlineCount = 0,
        hasAnyNesting = false;
      while (queue.length > 0) {
        const levelData = queue.shift();
        for (const item of levelData.items) {
          const div = document.createElement("div");
          div.className = "treeItem";
          const element = document.createElement("a");
          this._bindLink(element, item);
          this._setStyles(element, item);
          element.textContent = this._normalizeTextContent(item.title);
          div.append(element);
          if (item.items.length > 0) {
            hasAnyNesting = true;
            this._addToggleButton(div, item);
            const itemsDiv = document.createElement("div");
            itemsDiv.className = "treeItems";
            div.append(itemsDiv);
            queue.push({
              parent: itemsDiv,
              items: item.items
            });
          }
          levelData.parent.append(div);
          outlineCount++;
        }
      }
      this._finishRendering(fragment, outlineCount, hasAnyNesting);
    }
    async _currentOutlineItem() {
      if (!this._isPagesLoaded) {
        throw new Error("_currentOutlineItem: All pages have not been loaded.");
      }
      if (!this._outline || !this._pdfDocument) {
        return;
      }
      const pageNumberToDestHash = await this._getPageNumberToDestHash(this._pdfDocument);
      if (!pageNumberToDestHash) {
        return;
      }
      this._updateCurrentTreeItem(null);
      if (this._sidebarView !== _ui_utils.SidebarView.OUTLINE) {
        return;
      }
      for (let i = this._currentPageNumber; i > 0; i--) {
        const destHash = pageNumberToDestHash.get(i);
        if (!destHash) {
          continue;
        }
        const linkElement = this.container.querySelector(`a[href="${destHash}"]`);
        if (!linkElement) {
          continue;
        }
        this._scrollToCurrentTreeItem(linkElement.parentNode);
        break;
      }
    }
    async _getPageNumberToDestHash(pdfDocument) {
      if (this._pageNumberToDestHashCapability) {
        return this._pageNumberToDestHashCapability.promise;
      }
      this._pageNumberToDestHashCapability = new _pdfjsLib.PromiseCapability();
      const pageNumberToDestHash = new Map(),
        pageNumberNesting = new Map();
      const queue = [{
        nesting: 0,
        items: this._outline
      }];
      while (queue.length > 0) {
        const levelData = queue.shift(),
          currentNesting = levelData.nesting;
        for (const {
          dest,
          items
        } of levelData.items) {
          let explicitDest, pageNumber;
          if (typeof dest === "string") {
            explicitDest = await pdfDocument.getDestination(dest);
            if (pdfDocument !== this._pdfDocument) {
              return null;
            }
          } else {
            explicitDest = dest;
          }
          if (Array.isArray(explicitDest)) {
            const [destRef] = explicitDest;
            if (typeof destRef === "object" && destRef !== null) {
              pageNumber = this.linkService._cachedPageNumber(destRef);
              if (!pageNumber) {
                try {
                  pageNumber = (await pdfDocument.getPageIndex(destRef)) + 1;
                  if (pdfDocument !== this._pdfDocument) {
                    return null;
                  }
                  this.linkService.cachePageRef(pageNumber, destRef);
                } catch {}
              }
            } else if (Number.isInteger(destRef)) {
              pageNumber = destRef + 1;
            }
            if (Number.isInteger(pageNumber) && (!pageNumberToDestHash.has(pageNumber) || currentNesting > pageNumberNesting.get(pageNumber))) {
              const destHash = this.linkService.getDestinationHash(dest);
              pageNumberToDestHash.set(pageNumber, destHash);
              pageNumberNesting.set(pageNumber, currentNesting);
            }
          }
          if (items.length > 0) {
            queue.push({
              nesting: currentNesting + 1,
              items
            });
          }
        }
      }
      this._pageNumberToDestHashCapability.resolve(pageNumberToDestHash.size > 0 ? pageNumberToDestHash : null);
      return this._pageNumberToDestHashCapability.promise;
    }
  }
  exports.PDFOutlineViewer = PDFOutlineViewer;
  
  /***/ }),
  /* 203 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFPresentationMode = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const DELAY_BEFORE_HIDING_CONTROLS = 3000;
  const ACTIVE_SELECTOR = "pdfPresentationMode";
  const CONTROLS_SELECTOR = "pdfPresentationModeControls";
  const MOUSE_SCROLL_COOLDOWN_TIME = 50;
  const PAGE_SWITCH_THRESHOLD = 0.1;
  const SWIPE_MIN_DISTANCE_THRESHOLD = 50;
  const SWIPE_ANGLE_THRESHOLD = Math.PI / 6;
  var _state = /*#__PURE__*/new WeakMap();
  var _args = /*#__PURE__*/new WeakMap();
  var _mouseWheel = /*#__PURE__*/new WeakSet();
  var _notifyStateChange = /*#__PURE__*/new WeakSet();
  var _enter = /*#__PURE__*/new WeakSet();
  var _exit = /*#__PURE__*/new WeakSet();
  var _mouseDown = /*#__PURE__*/new WeakSet();
  var _contextMenu = /*#__PURE__*/new WeakSet();
  var _showControls = /*#__PURE__*/new WeakSet();
  var _hideControls = /*#__PURE__*/new WeakSet();
  var _resetMouseScrollState = /*#__PURE__*/new WeakSet();
  var _touchSwipe = /*#__PURE__*/new WeakSet();
  var _addWindowListeners = /*#__PURE__*/new WeakSet();
  var _removeWindowListeners = /*#__PURE__*/new WeakSet();
  var _fullscreenChange = /*#__PURE__*/new WeakSet();
  var _addFullscreenChangeListeners = /*#__PURE__*/new WeakSet();
  var _removeFullscreenChangeListeners = /*#__PURE__*/new WeakSet();
  class PDFPresentationMode {
    constructor(_ref) {
      let {
        container,
        pdfViewer,
        eventBus
      } = _ref;
      _classPrivateMethodInitSpec(this, _removeFullscreenChangeListeners);
      _classPrivateMethodInitSpec(this, _addFullscreenChangeListeners);
      _classPrivateMethodInitSpec(this, _fullscreenChange);
      _classPrivateMethodInitSpec(this, _removeWindowListeners);
      _classPrivateMethodInitSpec(this, _addWindowListeners);
      _classPrivateMethodInitSpec(this, _touchSwipe);
      _classPrivateMethodInitSpec(this, _resetMouseScrollState);
      _classPrivateMethodInitSpec(this, _hideControls);
      _classPrivateMethodInitSpec(this, _showControls);
      _classPrivateMethodInitSpec(this, _contextMenu);
      _classPrivateMethodInitSpec(this, _mouseDown);
      _classPrivateMethodInitSpec(this, _exit);
      _classPrivateMethodInitSpec(this, _enter);
      _classPrivateMethodInitSpec(this, _notifyStateChange);
      _classPrivateMethodInitSpec(this, _mouseWheel);
      _classPrivateFieldInitSpec(this, _state, {
        writable: true,
        value: _ui_utils.PresentationModeState.UNKNOWN
      });
      _classPrivateFieldInitSpec(this, _args, {
        writable: true,
        value: null
      });
      this.container = container;
      this.pdfViewer = pdfViewer;
      this.eventBus = eventBus;
      this.contextMenuOpen = false;
      this.mouseScrollTimeStamp = 0;
      this.mouseScrollDelta = 0;
      this.touchSwipeState = null;
    }
    async request() {
      const {
        container,
        pdfViewer
      } = this;
      if (this.active || !pdfViewer.pagesCount || !container.requestFullscreen) {
        return false;
      }
      _classPrivateMethodGet(this, _addFullscreenChangeListeners, _addFullscreenChangeListeners2).call(this);
      _classPrivateMethodGet(this, _notifyStateChange, _notifyStateChange2).call(this, _ui_utils.PresentationModeState.CHANGING);
      const promise = container.requestFullscreen();
      _classPrivateFieldSet(this, _args, {
        pageNumber: pdfViewer.currentPageNumber,
        scaleValue: pdfViewer.currentScaleValue,
        scrollMode: pdfViewer.scrollMode,
        spreadMode: null,
        annotationEditorMode: null
      });
      if (pdfViewer.spreadMode !== _ui_utils.SpreadMode.NONE && !(pdfViewer.pageViewsReady && pdfViewer.hasEqualPageSizes)) {
        console.warn("Ignoring Spread modes when entering PresentationMode, " + "since the document may contain varying page sizes.");
        _classPrivateFieldGet(this, _args).spreadMode = pdfViewer.spreadMode;
      }
      if (pdfViewer.annotationEditorMode !== _pdfjsLib.AnnotationEditorType.DISABLE) {
        _classPrivateFieldGet(this, _args).annotationEditorMode = pdfViewer.annotationEditorMode;
      }
      try {
        await promise;
        pdfViewer.focus();
        return true;
      } catch {
        _classPrivateMethodGet(this, _removeFullscreenChangeListeners, _removeFullscreenChangeListeners2).call(this);
        _classPrivateMethodGet(this, _notifyStateChange, _notifyStateChange2).call(this, _ui_utils.PresentationModeState.NORMAL);
      }
      return false;
    }
    get active() {
      return _classPrivateFieldGet(this, _state) === _ui_utils.PresentationModeState.CHANGING || _classPrivateFieldGet(this, _state) === _ui_utils.PresentationModeState.FULLSCREEN;
    }
  }
  exports.PDFPresentationMode = PDFPresentationMode;
  function _mouseWheel2(evt) {
    if (!this.active) {
      return;
    }
    evt.preventDefault();
    const delta = (0, _ui_utils.normalizeWheelEventDelta)(evt);
    const currentTime = Date.now();
    const storedTime = this.mouseScrollTimeStamp;
    if (currentTime > storedTime && currentTime - storedTime < MOUSE_SCROLL_COOLDOWN_TIME) {
      return;
    }
    if (this.mouseScrollDelta > 0 && delta < 0 || this.mouseScrollDelta < 0 && delta > 0) {
      _classPrivateMethodGet(this, _resetMouseScrollState, _resetMouseScrollState2).call(this);
    }
    this.mouseScrollDelta += delta;
    if (Math.abs(this.mouseScrollDelta) >= PAGE_SWITCH_THRESHOLD) {
      const totalDelta = this.mouseScrollDelta;
      _classPrivateMethodGet(this, _resetMouseScrollState, _resetMouseScrollState2).call(this);
      const success = totalDelta > 0 ? this.pdfViewer.previousPage() : this.pdfViewer.nextPage();
      if (success) {
        this.mouseScrollTimeStamp = currentTime;
      }
    }
  }
  function _notifyStateChange2(state) {
    _classPrivateFieldSet(this, _state, state);
    this.eventBus.dispatch("presentationmodechanged", {
      source: this,
      state
    });
  }
  function _enter2() {
    _classPrivateMethodGet(this, _notifyStateChange, _notifyStateChange2).call(this, _ui_utils.PresentationModeState.FULLSCREEN);
    this.container.classList.add(ACTIVE_SELECTOR);
    setTimeout(() => {
      this.pdfViewer.scrollMode = _ui_utils.ScrollMode.PAGE;
      if (_classPrivateFieldGet(this, _args).spreadMode !== null) {
        this.pdfViewer.spreadMode = _ui_utils.SpreadMode.NONE;
      }
      this.pdfViewer.currentPageNumber = _classPrivateFieldGet(this, _args).pageNumber;
      this.pdfViewer.currentScaleValue = "page-fit";
      if (_classPrivateFieldGet(this, _args).annotationEditorMode !== null) {
        this.pdfViewer.annotationEditorMode = {
          mode: _pdfjsLib.AnnotationEditorType.NONE
        };
      }
    }, 0);
    _classPrivateMethodGet(this, _addWindowListeners, _addWindowListeners2).call(this);
    _classPrivateMethodGet(this, _showControls, _showControls2).call(this);
    this.contextMenuOpen = false;
    window.getSelection().removeAllRanges();
  }
  function _exit2() {
    const pageNumber = this.pdfViewer.currentPageNumber;
    this.container.classList.remove(ACTIVE_SELECTOR);
    setTimeout(() => {
      _classPrivateMethodGet(this, _removeFullscreenChangeListeners, _removeFullscreenChangeListeners2).call(this);
      _classPrivateMethodGet(this, _notifyStateChange, _notifyStateChange2).call(this, _ui_utils.PresentationModeState.NORMAL);
      this.pdfViewer.scrollMode = _classPrivateFieldGet(this, _args).scrollMode;
      if (_classPrivateFieldGet(this, _args).spreadMode !== null) {
        this.pdfViewer.spreadMode = _classPrivateFieldGet(this, _args).spreadMode;
      }
      this.pdfViewer.currentScaleValue = _classPrivateFieldGet(this, _args).scaleValue;
      this.pdfViewer.currentPageNumber = pageNumber;
      if (_classPrivateFieldGet(this, _args).annotationEditorMode !== null) {
        this.pdfViewer.annotationEditorMode = {
          mode: _classPrivateFieldGet(this, _args).annotationEditorMode
        };
      }
      _classPrivateFieldSet(this, _args, null);
    }, 0);
    _classPrivateMethodGet(this, _removeWindowListeners, _removeWindowListeners2).call(this);
    _classPrivateMethodGet(this, _hideControls, _hideControls2).call(this);
    _classPrivateMethodGet(this, _resetMouseScrollState, _resetMouseScrollState2).call(this);
    this.contextMenuOpen = false;
  }
  function _mouseDown2(evt) {
    var _evt$target$parentNod;
    if (this.contextMenuOpen) {
      this.contextMenuOpen = false;
      evt.preventDefault();
      return;
    }
    if (evt.button !== 0) {
      return;
    }
    if (evt.target.href && (_evt$target$parentNod = evt.target.parentNode) !== null && _evt$target$parentNod !== void 0 && _evt$target$parentNod.hasAttribute("data-internal-link")) {
      return;
    }
    evt.preventDefault();
    if (evt.shiftKey) {
      this.pdfViewer.previousPage();
    } else {
      this.pdfViewer.nextPage();
    }
  }
  function _contextMenu2() {
    this.contextMenuOpen = true;
  }
  function _showControls2() {
    if (this.controlsTimeout) {
      clearTimeout(this.controlsTimeout);
    } else {
      this.container.classList.add(CONTROLS_SELECTOR);
    }
    this.controlsTimeout = setTimeout(() => {
      this.container.classList.remove(CONTROLS_SELECTOR);
      delete this.controlsTimeout;
    }, DELAY_BEFORE_HIDING_CONTROLS);
  }
  function _hideControls2() {
    if (!this.controlsTimeout) {
      return;
    }
    clearTimeout(this.controlsTimeout);
    this.container.classList.remove(CONTROLS_SELECTOR);
    delete this.controlsTimeout;
  }
  function _resetMouseScrollState2() {
    this.mouseScrollTimeStamp = 0;
    this.mouseScrollDelta = 0;
  }
  function _touchSwipe2(evt) {
    if (!this.active) {
      return;
    }
    if (evt.touches.length > 1) {
      this.touchSwipeState = null;
      return;
    }
    switch (evt.type) {
      case "touchstart":
        this.touchSwipeState = {
          startX: evt.touches[0].pageX,
          startY: evt.touches[0].pageY,
          endX: evt.touches[0].pageX,
          endY: evt.touches[0].pageY
        };
        break;
      case "touchmove":
        if (this.touchSwipeState === null) {
          return;
        }
        this.touchSwipeState.endX = evt.touches[0].pageX;
        this.touchSwipeState.endY = evt.touches[0].pageY;
        evt.preventDefault();
        break;
      case "touchend":
        if (this.touchSwipeState === null) {
          return;
        }
        let delta = 0;
        const dx = this.touchSwipeState.endX - this.touchSwipeState.startX;
        const dy = this.touchSwipeState.endY - this.touchSwipeState.startY;
        const absAngle = Math.abs(Math.atan2(dy, dx));
        if (Math.abs(dx) > SWIPE_MIN_DISTANCE_THRESHOLD && (absAngle <= SWIPE_ANGLE_THRESHOLD || absAngle >= Math.PI - SWIPE_ANGLE_THRESHOLD)) {
          delta = dx;
        } else if (Math.abs(dy) > SWIPE_MIN_DISTANCE_THRESHOLD && Math.abs(absAngle - Math.PI / 2) <= SWIPE_ANGLE_THRESHOLD) {
          delta = dy;
        }
        if (delta > 0) {
          this.pdfViewer.previousPage();
        } else if (delta < 0) {
          this.pdfViewer.nextPage();
        }
        break;
    }
  }
  function _addWindowListeners2() {
    this.showControlsBind = _classPrivateMethodGet(this, _showControls, _showControls2).bind(this);
    this.mouseDownBind = _classPrivateMethodGet(this, _mouseDown, _mouseDown2).bind(this);
    this.mouseWheelBind = _classPrivateMethodGet(this, _mouseWheel, _mouseWheel2).bind(this);
    this.resetMouseScrollStateBind = _classPrivateMethodGet(this, _resetMouseScrollState, _resetMouseScrollState2).bind(this);
    this.contextMenuBind = _classPrivateMethodGet(this, _contextMenu, _contextMenu2).bind(this);
    this.touchSwipeBind = _classPrivateMethodGet(this, _touchSwipe, _touchSwipe2).bind(this);
    window.addEventListener("mousemove", this.showControlsBind);
    window.addEventListener("mousedown", this.mouseDownBind);
    window.addEventListener("wheel", this.mouseWheelBind, {
      passive: false
    });
    window.addEventListener("keydown", this.resetMouseScrollStateBind);
    window.addEventListener("contextmenu", this.contextMenuBind);
    window.addEventListener("touchstart", this.touchSwipeBind);
    window.addEventListener("touchmove", this.touchSwipeBind);
    window.addEventListener("touchend", this.touchSwipeBind);
  }
  function _removeWindowListeners2() {
    window.removeEventListener("mousemove", this.showControlsBind);
    window.removeEventListener("mousedown", this.mouseDownBind);
    window.removeEventListener("wheel", this.mouseWheelBind, {
      passive: false
    });
    window.removeEventListener("keydown", this.resetMouseScrollStateBind);
    window.removeEventListener("contextmenu", this.contextMenuBind);
    window.removeEventListener("touchstart", this.touchSwipeBind);
    window.removeEventListener("touchmove", this.touchSwipeBind);
    window.removeEventListener("touchend", this.touchSwipeBind);
    delete this.showControlsBind;
    delete this.mouseDownBind;
    delete this.mouseWheelBind;
    delete this.resetMouseScrollStateBind;
    delete this.contextMenuBind;
    delete this.touchSwipeBind;
  }
  function _fullscreenChange2() {
    if (document.fullscreenElement) {
      _classPrivateMethodGet(this, _enter, _enter2).call(this);
    } else {
      _classPrivateMethodGet(this, _exit, _exit2).call(this);
    }
  }
  function _addFullscreenChangeListeners2() {
    this.fullscreenChangeBind = _classPrivateMethodGet(this, _fullscreenChange, _fullscreenChange2).bind(this);
    window.addEventListener("fullscreenchange", this.fullscreenChangeBind);
  }
  function _removeFullscreenChangeListeners2() {
    window.removeEventListener("fullscreenchange", this.fullscreenChangeBind);
    delete this.fullscreenChangeBind;
  }
  
  /***/ }),
  /* 204 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFRenderingQueue = void 0;
  __webpack_require__(2);
  __webpack_require__(205);
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  const CLEANUP_TIMEOUT = 30000;
  class PDFRenderingQueue {
    constructor() {
      this.pdfViewer = null;
      this.pdfThumbnailViewer = null;
      this.onIdle = null;
      this.highestPriorityPage = null;
      this.idleTimeout = null;
      this.printing = false;
      this.isThumbnailViewEnabled = false;
      Object.defineProperty(this, "hasViewer", {
        value: () => !!this.pdfViewer
      });
    }
    setViewer(pdfViewer) {
      this.pdfViewer = pdfViewer;
    }
    setThumbnailViewer(pdfThumbnailViewer) {
      this.pdfThumbnailViewer = pdfThumbnailViewer;
    }
    isHighestPriority(view) {
      return this.highestPriorityPage === view.renderingId;
    }
    renderHighestPriority(currentlyVisiblePages) {
      var _this$pdfThumbnailVie;
      if (this.idleTimeout) {
        clearTimeout(this.idleTimeout);
        this.idleTimeout = null;
      }
      if (this.pdfViewer.forceRendering(currentlyVisiblePages)) {
        return;
      }
      if (this.isThumbnailViewEnabled && (_this$pdfThumbnailVie = this.pdfThumbnailViewer) !== null && _this$pdfThumbnailVie !== void 0 && _this$pdfThumbnailVie.forceRendering()) {
        return;
      }
      if (this.printing) {
        return;
      }
      if (this.onIdle) {
        this.idleTimeout = setTimeout(this.onIdle.bind(this), CLEANUP_TIMEOUT);
      }
    }
    getHighestPriority(visible, views, scrolledDown) {
      let preRenderExtra = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;
      const visibleViews = visible.views,
        numVisible = visibleViews.length;
      if (numVisible === 0) {
        return null;
      }
      for (let i = 0; i < numVisible; i++) {
        const view = visibleViews[i].view;
        if (!this.isViewFinished(view)) {
          return view;
        }
      }
      const firstId = visible.first.id,
        lastId = visible.last.id;
      if (lastId - firstId + 1 > numVisible) {
        const visibleIds = visible.ids;
        for (let i = 1, ii = lastId - firstId; i < ii; i++) {
          const holeId = scrolledDown ? firstId + i : lastId - i;
          if (visibleIds.has(holeId)) {
            continue;
          }
          const holeView = views[holeId - 1];
          if (!this.isViewFinished(holeView)) {
            return holeView;
          }
        }
      }
      let preRenderIndex = scrolledDown ? lastId : firstId - 2;
      let preRenderView = views[preRenderIndex];
      if (preRenderView && !this.isViewFinished(preRenderView)) {
        return preRenderView;
      }
      if (preRenderExtra) {
        preRenderIndex += scrolledDown ? 1 : -1;
        preRenderView = views[preRenderIndex];
        if (preRenderView && !this.isViewFinished(preRenderView)) {
          return preRenderView;
        }
      }
      return null;
    }
    isViewFinished(view) {
      return view.renderingState === _ui_utils.RenderingStates.FINISHED;
    }
    renderView(view) {
      switch (view.renderingState) {
        case _ui_utils.RenderingStates.FINISHED:
          return false;
        case _ui_utils.RenderingStates.PAUSED:
          this.highestPriorityPage = view.renderingId;
          view.resume();
          break;
        case _ui_utils.RenderingStates.RUNNING:
          this.highestPriorityPage = view.renderingId;
          break;
        case _ui_utils.RenderingStates.INITIAL:
          this.highestPriorityPage = view.renderingId;
          view.draw().finally(() => {
            this.renderHighestPriority();
          }).catch(reason => {
            if (reason instanceof _pdfjsLib.RenderingCancelledException) {
              return;
            }
            console.error(`renderView: "${reason}"`);
          });
          break;
      }
      return true;
    }
  }
  exports.PDFRenderingQueue = PDFRenderingQueue;
  
  /***/ }),
  /* 205 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var IS_PURE = __webpack_require__(37);
  var NativePromiseConstructor = __webpack_require__(97);
  var fails = __webpack_require__(8);
  var getBuiltIn = __webpack_require__(25);
  var isCallable = __webpack_require__(22);
  var speciesConstructor = __webpack_require__(78);
  var promiseResolve = __webpack_require__(115);
  var defineBuiltIn = __webpack_require__(49);
  var NativePromisePrototype = NativePromiseConstructor && NativePromiseConstructor.prototype;
  var NON_GENERIC = !!NativePromiseConstructor && fails(function () {
   NativePromisePrototype['finally'].call({
    then: function () {
    }
   }, function () {
   });
  });
  $({
   target: 'Promise',
   proto: true,
   real: true,
   forced: NON_GENERIC
  }, {
   'finally': function (onFinally) {
    var C = speciesConstructor(this, getBuiltIn('Promise'));
    var isFunction = isCallable(onFinally);
    return this.then(isFunction ? function (x) {
     return promiseResolve(C, onFinally()).then(function () {
      return x;
     });
    } : onFinally, isFunction ? function (e) {
     return promiseResolve(C, onFinally()).then(function () {
      throw e;
     });
    } : onFinally);
   }
  });
  if (!IS_PURE && isCallable(NativePromiseConstructor)) {
   var method = getBuiltIn('Promise').prototype['finally'];
   if (NativePromisePrototype['finally'] !== method) {
    defineBuiltIn(NativePromisePrototype, 'finally', method, { unsafe: true });
   }
  }
  
  /***/ }),
  /* 206 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFScriptingManager = void 0;
  __webpack_require__(2);
  __webpack_require__(158);
  __webpack_require__(169);
  __webpack_require__(171);
  __webpack_require__(173);
  __webpack_require__(175);
  __webpack_require__(177);
  __webpack_require__(179);
  __webpack_require__(122);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  var _closeCapability = /*#__PURE__*/new WeakMap();
  var _destroyCapability = /*#__PURE__*/new WeakMap();
  var _docProperties = /*#__PURE__*/new WeakMap();
  var _eventBus = /*#__PURE__*/new WeakMap();
  var _externalServices = /*#__PURE__*/new WeakMap();
  var _pdfDocument = /*#__PURE__*/new WeakMap();
  var _pdfViewer = /*#__PURE__*/new WeakMap();
  var _ready = /*#__PURE__*/new WeakMap();
  var _sandboxBundleSrc = /*#__PURE__*/new WeakMap();
  var _scripting = /*#__PURE__*/new WeakMap();
  var _willPrintCapability = /*#__PURE__*/new WeakMap();
  var _updateFromSandbox = /*#__PURE__*/new WeakSet();
  var _dispatchPageOpen = /*#__PURE__*/new WeakSet();
  var _dispatchPageClose = /*#__PURE__*/new WeakSet();
  var _initScripting = /*#__PURE__*/new WeakSet();
  var _destroyScripting = /*#__PURE__*/new WeakSet();
  class PDFScriptingManager {
    constructor(_ref) {
      let {
        eventBus,
        sandboxBundleSrc = null,
        externalServices = null,
        docProperties = null
      } = _ref;
      _classPrivateMethodInitSpec(this, _destroyScripting);
      _classPrivateMethodInitSpec(this, _initScripting);
      _classPrivateMethodInitSpec(this, _dispatchPageClose);
      _classPrivateMethodInitSpec(this, _dispatchPageOpen);
      _classPrivateMethodInitSpec(this, _updateFromSandbox);
      _classPrivateFieldInitSpec(this, _closeCapability, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _destroyCapability, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _docProperties, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _eventBus, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _externalServices, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _pdfDocument, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _pdfViewer, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _ready, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _sandboxBundleSrc, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _scripting, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _willPrintCapability, {
        writable: true,
        value: null
      });
      _classPrivateFieldSet(this, _eventBus, eventBus);
      _classPrivateFieldSet(this, _sandboxBundleSrc, sandboxBundleSrc);
      _classPrivateFieldSet(this, _externalServices, externalServices);
      _classPrivateFieldSet(this, _docProperties, docProperties);
    }
    setViewer(pdfViewer) {
      _classPrivateFieldSet(this, _pdfViewer, pdfViewer);
    }
    async setDocument(pdfDocument) {
      var _classPrivateFieldGet5;
      if (_classPrivateFieldGet(this, _pdfDocument)) {
        await _classPrivateMethodGet(this, _destroyScripting, _destroyScripting2).call(this);
      }
      _classPrivateFieldSet(this, _pdfDocument, pdfDocument);
      if (!pdfDocument) {
        return;
      }
      const [objects, calculationOrder, docActions] = await Promise.all([pdfDocument.getFieldObjects(), pdfDocument.getCalculationOrderIds(), pdfDocument.getJSActions()]);
      if (!objects && !docActions) {
        await _classPrivateMethodGet(this, _destroyScripting, _destroyScripting2).call(this);
        return;
      }
      if (pdfDocument !== _classPrivateFieldGet(this, _pdfDocument)) {
        return;
      }
      try {
        _classPrivateFieldSet(this, _scripting, _classPrivateMethodGet(this, _initScripting, _initScripting2).call(this));
      } catch (error) {
        console.error(`setDocument: "${error.message}".`);
        await _classPrivateMethodGet(this, _destroyScripting, _destroyScripting2).call(this);
        return;
      }
      this._internalEvents.set("updatefromsandbox", event => {
        if ((event === null || event === void 0 ? void 0 : event.source) === window) {
          _classPrivateMethodGet(this, _updateFromSandbox, _updateFromSandbox2).call(this, event.detail);
        }
      });
      this._internalEvents.set("dispatcheventinsandbox", event => {
        var _classPrivateFieldGet2;
        (_classPrivateFieldGet2 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet2 === void 0 || _classPrivateFieldGet2.dispatchEventInSandbox(event.detail);
      });
      this._internalEvents.set("pagechanging", _ref2 => {
        let {
          pageNumber,
          previous
        } = _ref2;
        if (pageNumber === previous) {
          return;
        }
        _classPrivateMethodGet(this, _dispatchPageClose, _dispatchPageClose2).call(this, previous);
        _classPrivateMethodGet(this, _dispatchPageOpen, _dispatchPageOpen2).call(this, pageNumber);
      });
      this._internalEvents.set("pagerendered", _ref3 => {
        let {
          pageNumber
        } = _ref3;
        if (!this._pageOpenPending.has(pageNumber)) {
          return;
        }
        if (pageNumber !== _classPrivateFieldGet(this, _pdfViewer).currentPageNumber) {
          return;
        }
        _classPrivateMethodGet(this, _dispatchPageOpen, _dispatchPageOpen2).call(this, pageNumber);
      });
      this._internalEvents.set("pagesdestroy", async () => {
        var _classPrivateFieldGet3, _classPrivateFieldGet4;
        await _classPrivateMethodGet(this, _dispatchPageClose, _dispatchPageClose2).call(this, _classPrivateFieldGet(this, _pdfViewer).currentPageNumber);
        await ((_classPrivateFieldGet3 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet3 === void 0 ? void 0 : _classPrivateFieldGet3.dispatchEventInSandbox({
          id: "doc",
          name: "WillClose"
        }));
        (_classPrivateFieldGet4 = _classPrivateFieldGet(this, _closeCapability)) === null || _classPrivateFieldGet4 === void 0 || _classPrivateFieldGet4.resolve();
      });
      for (const [name, listener] of this._internalEvents) {
        _classPrivateFieldGet(this, _eventBus)._on(name, listener);
      }
      try {
        const docProperties = await _classPrivateFieldGet(this, _docProperties).call(this, pdfDocument);
        if (pdfDocument !== _classPrivateFieldGet(this, _pdfDocument)) {
          return;
        }
        await _classPrivateFieldGet(this, _scripting).createSandbox({
          objects,
          calculationOrder,
          appInfo: {
            platform: navigator.platform,
            language: navigator.language
          },
          docInfo: {
            ...docProperties,
            actions: docActions
          }
        });
        _classPrivateFieldGet(this, _eventBus).dispatch("sandboxcreated", {
          source: this
        });
      } catch (error) {
        console.error(`setDocument: "${error.message}".`);
        await _classPrivateMethodGet(this, _destroyScripting, _destroyScripting2).call(this);
        return;
      }
      await ((_classPrivateFieldGet5 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet5 === void 0 ? void 0 : _classPrivateFieldGet5.dispatchEventInSandbox({
        id: "doc",
        name: "Open"
      }));
      await _classPrivateMethodGet(this, _dispatchPageOpen, _dispatchPageOpen2).call(this, _classPrivateFieldGet(this, _pdfViewer).currentPageNumber, true);
      Promise.resolve().then(() => {
        if (pdfDocument === _classPrivateFieldGet(this, _pdfDocument)) {
          _classPrivateFieldSet(this, _ready, true);
        }
      });
    }
    async dispatchWillSave() {
      var _classPrivateFieldGet6;
      return (_classPrivateFieldGet6 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet6 === void 0 ? void 0 : _classPrivateFieldGet6.dispatchEventInSandbox({
        id: "doc",
        name: "WillSave"
      });
    }
    async dispatchDidSave() {
      var _classPrivateFieldGet7;
      return (_classPrivateFieldGet7 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet7 === void 0 ? void 0 : _classPrivateFieldGet7.dispatchEventInSandbox({
        id: "doc",
        name: "DidSave"
      });
    }
    async dispatchWillPrint() {
      var _classPrivateFieldGet8;
      if (!_classPrivateFieldGet(this, _scripting)) {
        return;
      }
      await ((_classPrivateFieldGet8 = _classPrivateFieldGet(this, _willPrintCapability)) === null || _classPrivateFieldGet8 === void 0 ? void 0 : _classPrivateFieldGet8.promise);
      _classPrivateFieldSet(this, _willPrintCapability, new _pdfjsLib.PromiseCapability());
      try {
        await _classPrivateFieldGet(this, _scripting).dispatchEventInSandbox({
          id: "doc",
          name: "WillPrint"
        });
      } catch (ex) {
        _classPrivateFieldGet(this, _willPrintCapability).resolve();
        _classPrivateFieldSet(this, _willPrintCapability, null);
        throw ex;
      }
      await _classPrivateFieldGet(this, _willPrintCapability).promise;
    }
    async dispatchDidPrint() {
      var _classPrivateFieldGet9;
      return (_classPrivateFieldGet9 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet9 === void 0 ? void 0 : _classPrivateFieldGet9.dispatchEventInSandbox({
        id: "doc",
        name: "DidPrint"
      });
    }
    get destroyPromise() {
      var _classPrivateFieldGet10;
      return ((_classPrivateFieldGet10 = _classPrivateFieldGet(this, _destroyCapability)) === null || _classPrivateFieldGet10 === void 0 ? void 0 : _classPrivateFieldGet10.promise) || null;
    }
    get ready() {
      return _classPrivateFieldGet(this, _ready);
    }
    get _internalEvents() {
      return (0, _pdfjsLib.shadow)(this, "_internalEvents", new Map());
    }
    get _pageOpenPending() {
      return (0, _pdfjsLib.shadow)(this, "_pageOpenPending", new Set());
    }
    get _visitedPages() {
      return (0, _pdfjsLib.shadow)(this, "_visitedPages", new Map());
    }
  }
  exports.PDFScriptingManager = PDFScriptingManager;
  async function _updateFromSandbox2(detail) {
    var _classPrivateFieldGet11;
    const pdfViewer = _classPrivateFieldGet(this, _pdfViewer);
    const isInPresentationMode = pdfViewer.isInPresentationMode || pdfViewer.isChangingPresentationMode;
    const {
      id,
      siblings,
      command,
      value
    } = detail;
    if (!id) {
      switch (command) {
        case "clear":
          console.clear();
          break;
        case "error":
          console.error(value);
          break;
        case "layout":
          if (!isInPresentationMode) {
            const modes = (0, _ui_utils.apiPageLayoutToViewerModes)(value);
            pdfViewer.spreadMode = modes.spreadMode;
          }
          break;
        case "page-num":
          pdfViewer.currentPageNumber = value + 1;
          break;
        case "print":
          await pdfViewer.pagesPromise;
          _classPrivateFieldGet(this, _eventBus).dispatch("print", {
            source: this
          });
          break;
        case "println":
          console.log(value);
          break;
        case "zoom":
          if (!isInPresentationMode) {
            pdfViewer.currentScaleValue = value;
          }
          break;
        case "SaveAs":
          _classPrivateFieldGet(this, _eventBus).dispatch("download", {
            source: this
          });
          break;
        case "FirstPage":
          pdfViewer.currentPageNumber = 1;
          break;
        case "LastPage":
          pdfViewer.currentPageNumber = pdfViewer.pagesCount;
          break;
        case "NextPage":
          pdfViewer.nextPage();
          break;
        case "PrevPage":
          pdfViewer.previousPage();
          break;
        case "ZoomViewIn":
          if (!isInPresentationMode) {
            pdfViewer.increaseScale();
          }
          break;
        case "ZoomViewOut":
          if (!isInPresentationMode) {
            pdfViewer.decreaseScale();
          }
          break;
        case "WillPrintFinished":
          (_classPrivateFieldGet11 = _classPrivateFieldGet(this, _willPrintCapability)) === null || _classPrivateFieldGet11 === void 0 || _classPrivateFieldGet11.resolve();
          _classPrivateFieldSet(this, _willPrintCapability, null);
          break;
      }
      return;
    }
    if (isInPresentationMode && detail.focus) {
      return;
    }
    delete detail.id;
    delete detail.siblings;
    const ids = siblings ? [id, ...siblings] : [id];
    for (const elementId of ids) {
      const element = document.querySelector(`[data-element-id="${elementId}"]`);
      if (element) {
        element.dispatchEvent(new CustomEvent("updatefromsandbox", {
          detail
        }));
      } else {
        var _classPrivateFieldGet12;
        (_classPrivateFieldGet12 = _classPrivateFieldGet(this, _pdfDocument)) === null || _classPrivateFieldGet12 === void 0 || _classPrivateFieldGet12.annotationStorage.setValue(elementId, detail);
      }
    }
  }
  async function _dispatchPageOpen2(pageNumber) {
    let initialize = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
    const pdfDocument = _classPrivateFieldGet(this, _pdfDocument),
      visitedPages = this._visitedPages;
    if (initialize) {
      _classPrivateFieldSet(this, _closeCapability, new _pdfjsLib.PromiseCapability());
    }
    if (!_classPrivateFieldGet(this, _closeCapability)) {
      return;
    }
    const pageView = _classPrivateFieldGet(this, _pdfViewer).getPageView(pageNumber - 1);
    if ((pageView === null || pageView === void 0 ? void 0 : pageView.renderingState) !== _ui_utils.RenderingStates.FINISHED) {
      this._pageOpenPending.add(pageNumber);
      return;
    }
    this._pageOpenPending.delete(pageNumber);
    const actionsPromise = (async (_pageView$pdfPage, _classPrivateFieldGet13) => {
      const actions = await (!visitedPages.has(pageNumber) ? (_pageView$pdfPage = pageView.pdfPage) === null || _pageView$pdfPage === void 0 ? void 0 : _pageView$pdfPage.getJSActions() : null);
      if (pdfDocument !== _classPrivateFieldGet(this, _pdfDocument)) {
        return;
      }
      await ((_classPrivateFieldGet13 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet13 === void 0 ? void 0 : _classPrivateFieldGet13.dispatchEventInSandbox({
        id: "page",
        name: "PageOpen",
        pageNumber,
        actions
      }));
    })();
    visitedPages.set(pageNumber, actionsPromise);
  }
  async function _dispatchPageClose2(pageNumber) {
    var _classPrivateFieldGet14;
    const pdfDocument = _classPrivateFieldGet(this, _pdfDocument),
      visitedPages = this._visitedPages;
    if (!_classPrivateFieldGet(this, _closeCapability)) {
      return;
    }
    if (this._pageOpenPending.has(pageNumber)) {
      return;
    }
    const actionsPromise = visitedPages.get(pageNumber);
    if (!actionsPromise) {
      return;
    }
    visitedPages.set(pageNumber, null);
    await actionsPromise;
    if (pdfDocument !== _classPrivateFieldGet(this, _pdfDocument)) {
      return;
    }
    await ((_classPrivateFieldGet14 = _classPrivateFieldGet(this, _scripting)) === null || _classPrivateFieldGet14 === void 0 ? void 0 : _classPrivateFieldGet14.dispatchEventInSandbox({
      id: "page",
      name: "PageClose",
      pageNumber
    }));
  }
  function _initScripting2() {
    _classPrivateFieldSet(this, _destroyCapability, new _pdfjsLib.PromiseCapability());
    if (_classPrivateFieldGet(this, _scripting)) {
      throw new Error("#initScripting: Scripting already exists.");
    }
    return _classPrivateFieldGet(this, _externalServices).createScripting({
      sandboxBundleSrc: _classPrivateFieldGet(this, _sandboxBundleSrc)
    });
  }
  async function _destroyScripting2() {
    var _classPrivateFieldGet16, _classPrivateFieldGet17;
    if (!_classPrivateFieldGet(this, _scripting)) {
      var _classPrivateFieldGet15;
      _classPrivateFieldSet(this, _pdfDocument, null);
      (_classPrivateFieldGet15 = _classPrivateFieldGet(this, _destroyCapability)) === null || _classPrivateFieldGet15 === void 0 || _classPrivateFieldGet15.resolve();
      return;
    }
    if (_classPrivateFieldGet(this, _closeCapability)) {
      await Promise.race([_classPrivateFieldGet(this, _closeCapability).promise, new Promise(resolve => {
        setTimeout(resolve, 1000);
      })]).catch(() => {});
      _classPrivateFieldSet(this, _closeCapability, null);
    }
    _classPrivateFieldSet(this, _pdfDocument, null);
    try {
      await _classPrivateFieldGet(this, _scripting).destroySandbox();
    } catch {}
    (_classPrivateFieldGet16 = _classPrivateFieldGet(this, _willPrintCapability)) === null || _classPrivateFieldGet16 === void 0 || _classPrivateFieldGet16.reject(new Error("Scripting destroyed."));
    _classPrivateFieldSet(this, _willPrintCapability, null);
    for (const [name, listener] of this._internalEvents) {
      _classPrivateFieldGet(this, _eventBus)._off(name, listener);
    }
    this._internalEvents.clear();
    this._pageOpenPending.clear();
    this._visitedPages.clear();
    _classPrivateFieldSet(this, _scripting, null);
    _classPrivateFieldSet(this, _ready, false);
    (_classPrivateFieldGet17 = _classPrivateFieldGet(this, _destroyCapability)) === null || _classPrivateFieldGet17 === void 0 || _classPrivateFieldGet17.resolve();
  }
  
  /***/ }),
  /* 207 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFSidebar = void 0;
  __webpack_require__(122);
  __webpack_require__(2);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const SIDEBAR_WIDTH_VAR = "--sidebar-width";
  const SIDEBAR_MIN_WIDTH = 200;
  const SIDEBAR_RESIZING_CLASS = "sidebarResizing";
  const UI_NOTIFICATION_CLASS = "pdfSidebarNotification";
  var _isRTL = /*#__PURE__*/new WeakMap();
  var _mouseMoveBound = /*#__PURE__*/new WeakMap();
  var _mouseUpBound = /*#__PURE__*/new WeakMap();
  var _outerContainerWidth = /*#__PURE__*/new WeakMap();
  var _width = /*#__PURE__*/new WeakMap();
  var _dispatchEvent = /*#__PURE__*/new WeakSet();
  var _showUINotification = /*#__PURE__*/new WeakSet();
  var _hideUINotification = /*#__PURE__*/new WeakSet();
  var _addEventListeners = /*#__PURE__*/new WeakSet();
  var _updateWidth = /*#__PURE__*/new WeakSet();
  var _mouseMove = /*#__PURE__*/new WeakSet();
  var _mouseUp = /*#__PURE__*/new WeakSet();
  class PDFSidebar {
    constructor(_ref) {
      let {
        elements,
        eventBus,
        l10n
      } = _ref;
      _classPrivateMethodInitSpec(this, _mouseUp);
      _classPrivateMethodInitSpec(this, _mouseMove);
      _classPrivateMethodInitSpec(this, _updateWidth);
      _classPrivateMethodInitSpec(this, _addEventListeners);
      _classPrivateMethodInitSpec(this, _hideUINotification);
      _classPrivateMethodInitSpec(this, _showUINotification);
      _classPrivateMethodInitSpec(this, _dispatchEvent);
      _classPrivateFieldInitSpec(this, _isRTL, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _mouseMoveBound, {
        writable: true,
        value: _classPrivateMethodGet(this, _mouseMove, _mouseMove2).bind(this)
      });
      _classPrivateFieldInitSpec(this, _mouseUpBound, {
        writable: true,
        value: _classPrivateMethodGet(this, _mouseUp, _mouseUp2).bind(this)
      });
      _classPrivateFieldInitSpec(this, _outerContainerWidth, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _width, {
        writable: true,
        value: null
      });
      this.isOpen = false;
      this.active = _ui_utils.SidebarView.THUMBS;
      this.isInitialViewSet = false;
      this.isInitialEventDispatched = false;
      this.onToggled = null;
      this.onUpdateThumbnails = null;
      this.outerContainer = elements.outerContainer;
      this.sidebarContainer = elements.sidebarContainer;
      this.toggleButton = elements.toggleButton;
      this.resizer = elements.resizer;
      this.thumbnailButton = elements.thumbnailButton;
      this.outlineButton = elements.outlineButton;
      this.attachmentsButton = elements.attachmentsButton;
      this.layersButton = elements.layersButton;
      this.thumbnailView = elements.thumbnailView;
      this.outlineView = elements.outlineView;
      this.attachmentsView = elements.attachmentsView;
      this.layersView = elements.layersView;
      this._outlineOptionsContainer = elements.outlineOptionsContainer;
      this._currentOutlineItemButton = elements.currentOutlineItemButton;
      this.eventBus = eventBus;
      this.l10n = l10n;
      l10n.getDirection().then(dir => {
        _classPrivateFieldSet(this, _isRTL, dir === "rtl");
      });
      _classPrivateMethodGet(this, _addEventListeners, _addEventListeners2).call(this);
    }
    reset() {
      this.isInitialViewSet = false;
      this.isInitialEventDispatched = false;
      _classPrivateMethodGet(this, _hideUINotification, _hideUINotification2).call(this, true);
      this.switchView(_ui_utils.SidebarView.THUMBS);
      this.outlineButton.disabled = false;
      this.attachmentsButton.disabled = false;
      this.layersButton.disabled = false;
      this._currentOutlineItemButton.disabled = true;
    }
    get visibleView() {
      return this.isOpen ? this.active : _ui_utils.SidebarView.NONE;
    }
    setInitialView() {
      let view = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : _ui_utils.SidebarView.NONE;
      if (this.isInitialViewSet) {
        return;
      }
      this.isInitialViewSet = true;
      if (view === _ui_utils.SidebarView.NONE || view === _ui_utils.SidebarView.UNKNOWN) {
        _classPrivateMethodGet(this, _dispatchEvent, _dispatchEvent2).call(this);
        return;
      }
      this.switchView(view, true);
      if (!this.isInitialEventDispatched) {
        _classPrivateMethodGet(this, _dispatchEvent, _dispatchEvent2).call(this);
      }
    }
    switchView(view) {
      let forceOpen = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      const isViewChanged = view !== this.active;
      let forceRendering = false;
      switch (view) {
        case _ui_utils.SidebarView.NONE:
          if (this.isOpen) {
            this.close();
          }
          return;
        case _ui_utils.SidebarView.THUMBS:
          if (this.isOpen && isViewChanged) {
            forceRendering = true;
          }
          break;
        case _ui_utils.SidebarView.OUTLINE:
          if (this.outlineButton.disabled) {
            return;
          }
          break;
        case _ui_utils.SidebarView.ATTACHMENTS:
          if (this.attachmentsButton.disabled) {
            return;
          }
          break;
        case _ui_utils.SidebarView.LAYERS:
          if (this.layersButton.disabled) {
            return;
          }
          break;
        default:
          console.error(`PDFSidebar.switchView: "${view}" is not a valid view.`);
          return;
      }
      this.active = view;
      (0, _ui_utils.toggleCheckedBtn)(this.thumbnailButton, view === _ui_utils.SidebarView.THUMBS, this.thumbnailView);
      (0, _ui_utils.toggleCheckedBtn)(this.outlineButton, view === _ui_utils.SidebarView.OUTLINE, this.outlineView);
      (0, _ui_utils.toggleCheckedBtn)(this.attachmentsButton, view === _ui_utils.SidebarView.ATTACHMENTS, this.attachmentsView);
      (0, _ui_utils.toggleCheckedBtn)(this.layersButton, view === _ui_utils.SidebarView.LAYERS, this.layersView);
      this._outlineOptionsContainer.classList.toggle("hidden", view !== _ui_utils.SidebarView.OUTLINE);
      if (forceOpen && !this.isOpen) {
        this.open();
        return;
      }
      if (forceRendering) {
        this.onUpdateThumbnails();
        this.onToggled();
      }
      if (isViewChanged) {
        _classPrivateMethodGet(this, _dispatchEvent, _dispatchEvent2).call(this);
      }
    }
    open() {
      if (this.isOpen) {
        return;
      }
      this.isOpen = true;
      (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, true);
      this.outerContainer.classList.add("sidebarMoving", "sidebarOpen");
      if (this.active === _ui_utils.SidebarView.THUMBS) {
        this.onUpdateThumbnails();
      }
      this.onToggled();
      _classPrivateMethodGet(this, _dispatchEvent, _dispatchEvent2).call(this);
      _classPrivateMethodGet(this, _hideUINotification, _hideUINotification2).call(this);
    }
    close() {
      if (!this.isOpen) {
        return;
      }
      this.isOpen = false;
      (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, false);
      this.outerContainer.classList.add("sidebarMoving");
      this.outerContainer.classList.remove("sidebarOpen");
      this.onToggled();
      _classPrivateMethodGet(this, _dispatchEvent, _dispatchEvent2).call(this);
    }
    toggle() {
      if (this.isOpen) {
        this.close();
      } else {
        this.open();
      }
    }
    get outerContainerWidth() {
      return _classPrivateFieldGet(this, _outerContainerWidth) || _classPrivateFieldSet(this, _outerContainerWidth, this.outerContainer.clientWidth);
    }
  }
  exports.PDFSidebar = PDFSidebar;
  function _dispatchEvent2() {
    if (this.isInitialViewSet) {
      this.isInitialEventDispatched || (this.isInitialEventDispatched = true);
    }
    this.eventBus.dispatch("sidebarviewchanged", {
      source: this,
      view: this.visibleView
    });
  }
  function _showUINotification2() {
    this.toggleButton.setAttribute("data-l10n-id", "toggle_sidebar_notification2");
    this.l10n.translate(this.toggleButton);
    if (!this.isOpen) {
      this.toggleButton.classList.add(UI_NOTIFICATION_CLASS);
    }
  }
  function _hideUINotification2() {
    let reset = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
    if (this.isOpen || reset) {
      this.toggleButton.classList.remove(UI_NOTIFICATION_CLASS);
    }
    if (reset) {
      this.toggleButton.setAttribute("data-l10n-id", "toggle_sidebar");
      this.l10n.translate(this.toggleButton);
    }
  }
  function _addEventListeners2() {
    this.sidebarContainer.addEventListener("transitionend", evt => {
      if (evt.target === this.sidebarContainer) {
        this.outerContainer.classList.remove("sidebarMoving");
      }
    });
    this.toggleButton.addEventListener("click", () => {
      this.toggle();
    });
    this.thumbnailButton.addEventListener("click", () => {
      this.switchView(_ui_utils.SidebarView.THUMBS);
    });
    this.outlineButton.addEventListener("click", () => {
      this.switchView(_ui_utils.SidebarView.OUTLINE);
    });
    this.outlineButton.addEventListener("dblclick", () => {
      this.eventBus.dispatch("toggleoutlinetree", {
        source: this
      });
    });
    this.attachmentsButton.addEventListener("click", () => {
      this.switchView(_ui_utils.SidebarView.ATTACHMENTS);
    });
    this.layersButton.addEventListener("click", () => {
      this.switchView(_ui_utils.SidebarView.LAYERS);
    });
    this.layersButton.addEventListener("dblclick", () => {
      this.eventBus.dispatch("resetlayers", {
        source: this
      });
    });
    this._currentOutlineItemButton.addEventListener("click", () => {
      this.eventBus.dispatch("currentoutlineitem", {
        source: this
      });
    });
    const onTreeLoaded = (count, button, view) => {
      button.disabled = !count;
      if (count) {
        _classPrivateMethodGet(this, _showUINotification, _showUINotification2).call(this);
      } else if (this.active === view) {
        this.switchView(_ui_utils.SidebarView.THUMBS);
      }
    };
    this.eventBus._on("outlineloaded", evt => {
      onTreeLoaded(evt.outlineCount, this.outlineButton, _ui_utils.SidebarView.OUTLINE);
      evt.currentOutlineItemPromise.then(enabled => {
        if (!this.isInitialViewSet) {
          return;
        }
        this._currentOutlineItemButton.disabled = !enabled;
      });
    });
    this.eventBus._on("attachmentsloaded", evt => {
      onTreeLoaded(evt.attachmentsCount, this.attachmentsButton, _ui_utils.SidebarView.ATTACHMENTS);
    });
    this.eventBus._on("layersloaded", evt => {
      onTreeLoaded(evt.layersCount, this.layersButton, _ui_utils.SidebarView.LAYERS);
    });
    this.eventBus._on("presentationmodechanged", evt => {
      if (evt.state === _ui_utils.PresentationModeState.NORMAL && this.visibleView === _ui_utils.SidebarView.THUMBS) {
        this.onUpdateThumbnails();
      }
    });
    this.resizer.addEventListener("mousedown", evt => {
      if (evt.button !== 0) {
        return;
      }
      this.outerContainer.classList.add(SIDEBAR_RESIZING_CLASS);
      window.addEventListener("mousemove", _classPrivateFieldGet(this, _mouseMoveBound));
      window.addEventListener("mouseup", _classPrivateFieldGet(this, _mouseUpBound));
    });
    this.eventBus._on("resize", evt => {
      if (evt.source !== window) {
        return;
      }
      _classPrivateFieldSet(this, _outerContainerWidth, null);
      if (!_classPrivateFieldGet(this, _width)) {
        return;
      }
      if (!this.isOpen) {
        _classPrivateMethodGet(this, _updateWidth, _updateWidth2).call(this, _classPrivateFieldGet(this, _width));
        return;
      }
      this.outerContainer.classList.add(SIDEBAR_RESIZING_CLASS);
      const updated = _classPrivateMethodGet(this, _updateWidth, _updateWidth2).call(this, _classPrivateFieldGet(this, _width));
      Promise.resolve().then(() => {
        this.outerContainer.classList.remove(SIDEBAR_RESIZING_CLASS);
        if (updated) {
          this.eventBus.dispatch("resize", {
            source: this
          });
        }
      });
    });
  }
  function _updateWidth2() {
    let width = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;
    const maxWidth = Math.floor(this.outerContainerWidth / 2);
    if (width > maxWidth) {
      width = maxWidth;
    }
    if (width < SIDEBAR_MIN_WIDTH) {
      width = SIDEBAR_MIN_WIDTH;
    }
    if (width === _classPrivateFieldGet(this, _width)) {
      return false;
    }
    _classPrivateFieldSet(this, _width, width);
    _ui_utils.docStyle.setProperty(SIDEBAR_WIDTH_VAR, `${width}px`);
    return true;
  }
  function _mouseMove2(evt) {
    let width = evt.clientX;
    if (_classPrivateFieldGet(this, _isRTL)) {
      width = this.outerContainerWidth - width;
    }
    _classPrivateMethodGet(this, _updateWidth, _updateWidth2).call(this, width);
  }
  function _mouseUp2(evt) {
    this.outerContainer.classList.remove(SIDEBAR_RESIZING_CLASS);
    this.eventBus.dispatch("resize", {
      source: this
    });
    window.removeEventListener("mousemove", _classPrivateFieldGet(this, _mouseMoveBound));
    window.removeEventListener("mouseup", _classPrivateFieldGet(this, _mouseUpBound));
  }
  
  /***/ }),
  /* 208 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFThumbnailViewer = void 0;
  __webpack_require__(122);
  __webpack_require__(142);
  __webpack_require__(2);
  var _ui_utils = __webpack_require__(148);
  var _pdf_thumbnail_view = __webpack_require__(209);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const THUMBNAIL_SCROLL_MARGIN = -19;
  const THUMBNAIL_SELECTED_CLASS = "selected";
  var _ensurePdfPageLoaded = /*#__PURE__*/new WeakSet();
  var _getScrollAhead = /*#__PURE__*/new WeakSet();
  class PDFThumbnailViewer {
    constructor(_ref) {
      let {
        container,
        eventBus,
        linkService,
        renderingQueue,
        l10n,
        pageColors
      } = _ref;
      _classPrivateMethodInitSpec(this, _getScrollAhead);
      _classPrivateMethodInitSpec(this, _ensurePdfPageLoaded);
      this.container = container;
      this.eventBus = eventBus;
      this.linkService = linkService;
      this.renderingQueue = renderingQueue;
      this.l10n = l10n;
      this.pageColors = pageColors || null;
      this.scroll = (0, _ui_utils.watchScroll)(this.container, this._scrollUpdated.bind(this));
      this._resetView();
    }
    _scrollUpdated() {
      this.renderingQueue.renderHighestPriority();
    }
    getThumbnail(index) {
      return this._thumbnails[index];
    }
    _getVisibleThumbs() {
      return (0, _ui_utils.getVisibleElements)({
        scrollEl: this.container,
        views: this._thumbnails
      });
    }
    scrollThumbnailIntoView(pageNumber) {
      if (!this.pdfDocument) {
        return;
      }
      const thumbnailView = this._thumbnails[pageNumber - 1];
      if (!thumbnailView) {
        console.error('scrollThumbnailIntoView: Invalid "pageNumber" parameter.');
        return;
      }
      if (pageNumber !== this._currentPageNumber) {
        const prevThumbnailView = this._thumbnails[this._currentPageNumber - 1];
        prevThumbnailView.div.classList.remove(THUMBNAIL_SELECTED_CLASS);
        thumbnailView.div.classList.add(THUMBNAIL_SELECTED_CLASS);
      }
      const {
        first,
        last,
        views
      } = this._getVisibleThumbs();
      if (views.length > 0) {
        let shouldScroll = false;
        if (pageNumber <= first.id || pageNumber >= last.id) {
          shouldScroll = true;
        } else {
          for (const {
            id,
            percent
          } of views) {
            if (id !== pageNumber) {
              continue;
            }
            shouldScroll = percent < 100;
            break;
          }
        }
        if (shouldScroll) {
          (0, _ui_utils.scrollIntoView)(thumbnailView.div, {
            top: THUMBNAIL_SCROLL_MARGIN
          });
        }
      }
      this._currentPageNumber = pageNumber;
    }
    get pagesRotation() {
      return this._pagesRotation;
    }
    set pagesRotation(rotation) {
      if (!(0, _ui_utils.isValidRotation)(rotation)) {
        throw new Error("Invalid thumbnails rotation angle.");
      }
      if (!this.pdfDocument) {
        return;
      }
      if (this._pagesRotation === rotation) {
        return;
      }
      this._pagesRotation = rotation;
      const updateArgs = {
        rotation
      };
      for (const thumbnail of this._thumbnails) {
        thumbnail.update(updateArgs);
      }
    }
    cleanup() {
      for (const thumbnail of this._thumbnails) {
        if (thumbnail.renderingState !== _ui_utils.RenderingStates.FINISHED) {
          thumbnail.reset();
        }
      }
      _pdf_thumbnail_view.TempImageFactory.destroyCanvas();
    }
    _resetView() {
      this._thumbnails = [];
      this._currentPageNumber = 1;
      this._pageLabels = null;
      this._pagesRotation = 0;
      this.container.textContent = "";
    }
    setDocument(pdfDocument) {
      if (this.pdfDocument) {
        this._cancelRendering();
        this._resetView();
      }
      this.pdfDocument = pdfDocument;
      if (!pdfDocument) {
        return;
      }
      const firstPagePromise = pdfDocument.getPage(1);
      const optionalContentConfigPromise = pdfDocument.getOptionalContentConfig();
      firstPagePromise.then(firstPdfPage => {
        var _this$_thumbnails$;
        const pagesCount = pdfDocument.numPages;
        const viewport = firstPdfPage.getViewport({
          scale: 1
        });
        for (let pageNum = 1; pageNum <= pagesCount; ++pageNum) {
          const thumbnail = new _pdf_thumbnail_view.PDFThumbnailView({
            container: this.container,
            eventBus: this.eventBus,
            id: pageNum,
            defaultViewport: viewport.clone(),
            optionalContentConfigPromise,
            linkService: this.linkService,
            renderingQueue: this.renderingQueue,
            l10n: this.l10n,
            pageColors: this.pageColors
          });
          this._thumbnails.push(thumbnail);
        }
        (_this$_thumbnails$ = this._thumbnails[0]) === null || _this$_thumbnails$ === void 0 || _this$_thumbnails$.setPdfPage(firstPdfPage);
        const thumbnailView = this._thumbnails[this._currentPageNumber - 1];
        thumbnailView.div.classList.add(THUMBNAIL_SELECTED_CLASS);
      }).catch(reason => {
        console.error("Unable to initialize thumbnail viewer", reason);
      });
    }
    _cancelRendering() {
      for (const thumbnail of this._thumbnails) {
        thumbnail.cancelRendering();
      }
    }
    setPageLabels(labels) {
      if (!this.pdfDocument) {
        return;
      }
      if (!labels) {
        this._pageLabels = null;
      } else if (!(Array.isArray(labels) && this.pdfDocument.numPages === labels.length)) {
        this._pageLabels = null;
        console.error("PDFThumbnailViewer_setPageLabels: Invalid page labels.");
      } else {
        this._pageLabels = labels;
      }
      for (let i = 0, ii = this._thumbnails.length; i < ii; i++) {
        var _this$_pageLabels$i, _this$_pageLabels;
        this._thumbnails[i].setPageLabel((_this$_pageLabels$i = (_this$_pageLabels = this._pageLabels) === null || _this$_pageLabels === void 0 ? void 0 : _this$_pageLabels[i]) !== null && _this$_pageLabels$i !== void 0 ? _this$_pageLabels$i : null);
      }
    }
    forceRendering() {
      const visibleThumbs = this._getVisibleThumbs();
      const scrollAhead = _classPrivateMethodGet(this, _getScrollAhead, _getScrollAhead2).call(this, visibleThumbs);
      const thumbView = this.renderingQueue.getHighestPriority(visibleThumbs, this._thumbnails, scrollAhead);
      if (thumbView) {
        _classPrivateMethodGet(this, _ensurePdfPageLoaded, _ensurePdfPageLoaded2).call(this, thumbView).then(() => {
          this.renderingQueue.renderView(thumbView);
        });
        return true;
      }
      return false;
    }
  }
  exports.PDFThumbnailViewer = PDFThumbnailViewer;
  async function _ensurePdfPageLoaded2(thumbView) {
    if (thumbView.pdfPage) {
      return thumbView.pdfPage;
    }
    try {
      const pdfPage = await this.pdfDocument.getPage(thumbView.id);
      if (!thumbView.pdfPage) {
        thumbView.setPdfPage(pdfPage);
      }
      return pdfPage;
    } catch (reason) {
      console.error("Unable to get page for thumb view", reason);
      return null;
    }
  }
  function _getScrollAhead2(visible) {
    var _visible$first, _visible$last;
    if (((_visible$first = visible.first) === null || _visible$first === void 0 ? void 0 : _visible$first.id) === 1) {
      return true;
    } else if (((_visible$last = visible.last) === null || _visible$last === void 0 ? void 0 : _visible$last.id) === this._thumbnails.length) {
      return false;
    }
    return this.scroll.down;
  }
  
  /***/ }),
  /* 209 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.TempImageFactory = exports.PDFThumbnailView = void 0;
  __webpack_require__(122);
  __webpack_require__(2);
  __webpack_require__(205);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classStaticPrivateFieldSpecSet(receiver, classConstructor, descriptor, value) { _classCheckPrivateStaticAccess(receiver, classConstructor); _classCheckPrivateStaticFieldDescriptor(descriptor, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classStaticPrivateFieldSpecGet(receiver, classConstructor, descriptor) { _classCheckPrivateStaticAccess(receiver, classConstructor); _classCheckPrivateStaticFieldDescriptor(descriptor, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classCheckPrivateStaticFieldDescriptor(descriptor, action) { if (descriptor === undefined) { throw new TypeError("attempted to " + action + " private static field before its declaration"); } }
  function _classCheckPrivateStaticAccess(receiver, classConstructor) { if (receiver !== classConstructor) { throw new TypeError("Private static access of wrong provenance"); } }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  const DRAW_UPSCALE_FACTOR = 2;
  const MAX_NUM_SCALING_STEPS = 3;
  const THUMBNAIL_WIDTH = 98;
  class TempImageFactory {
    static getCanvas(width, height) {
      const tempCanvas = _classStaticPrivateFieldSpecGet(this, TempImageFactory, _tempCanvas) || _classStaticPrivateFieldSpecSet(this, TempImageFactory, _tempCanvas, document.createElement("canvas"));
      tempCanvas.width = width;
      tempCanvas.height = height;
      const ctx = tempCanvas.getContext("2d", {
        alpha: false
      });
      ctx.save();
      ctx.fillStyle = "rgb(255, 255, 255)";
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
      return [tempCanvas, tempCanvas.getContext("2d")];
    }
    static destroyCanvas() {
      const tempCanvas = _classStaticPrivateFieldSpecGet(this, TempImageFactory, _tempCanvas);
      if (tempCanvas) {
        tempCanvas.width = 0;
        tempCanvas.height = 0;
      }
      _classStaticPrivateFieldSpecSet(this, TempImageFactory, _tempCanvas, null);
    }
  }
  exports.TempImageFactory = TempImageFactory;
  var _tempCanvas = {
    writable: true,
    value: null
  };
  var _updateDims = /*#__PURE__*/new WeakSet();
  var _finishRenderTask = /*#__PURE__*/new WeakSet();
  class PDFThumbnailView {
    constructor(_ref) {
      let {
        container,
        eventBus,
        id,
        defaultViewport,
        optionalContentConfigPromise,
        linkService,
        renderingQueue,
        l10n,
        pageColors
      } = _ref;
      _classPrivateMethodInitSpec(this, _finishRenderTask);
      _classPrivateMethodInitSpec(this, _updateDims);
      this.id = id;
      this.renderingId = "thumbnail" + id;
      this.pageLabel = null;
      this.pdfPage = null;
      this.rotation = 0;
      this.viewport = defaultViewport;
      this.pdfPageRotate = defaultViewport.rotation;
      this._optionalContentConfigPromise = optionalContentConfigPromise || null;
      this.pageColors = pageColors || null;
      this.eventBus = eventBus;
      this.linkService = linkService;
      this.renderingQueue = renderingQueue;
      this.renderTask = null;
      this.renderingState = _ui_utils.RenderingStates.INITIAL;
      this.resume = null;
      this.l10n = l10n;
      const anchor = document.createElement("a");
      anchor.href = linkService.getAnchorUrl("#page=" + id);
      this._thumbPageTitle.then(msg => {
        anchor.title = msg;
      });
      anchor.onclick = function () {
        linkService.goToPage(id);
        return false;
      };
      this.anchor = anchor;
      const div = document.createElement("div");
      div.className = "thumbnail";
      div.setAttribute("data-page-number", this.id);
      this.div = div;
      _classPrivateMethodGet(this, _updateDims, _updateDims2).call(this);
      const img = document.createElement("div");
      img.className = "thumbnailImage";
      this._placeholderImg = img;
      div.append(img);
      anchor.append(div);
      container.append(anchor);
    }
    setPdfPage(pdfPage) {
      this.pdfPage = pdfPage;
      this.pdfPageRotate = pdfPage.rotate;
      const totalRotation = (this.rotation + this.pdfPageRotate) % 360;
      this.viewport = pdfPage.getViewport({
        scale: 1,
        rotation: totalRotation
      });
      this.reset();
    }
    reset() {
      var _this$image;
      this.cancelRendering();
      this.renderingState = _ui_utils.RenderingStates.INITIAL;
      this.div.removeAttribute("data-loaded");
      (_this$image = this.image) === null || _this$image === void 0 || _this$image.replaceWith(this._placeholderImg);
      _classPrivateMethodGet(this, _updateDims, _updateDims2).call(this);
      if (this.image) {
        this.image.removeAttribute("src");
        delete this.image;
      }
    }
    update(_ref2) {
      let {
        rotation = null
      } = _ref2;
      if (typeof rotation === "number") {
        this.rotation = rotation;
      }
      const totalRotation = (this.rotation + this.pdfPageRotate) % 360;
      this.viewport = this.viewport.clone({
        scale: 1,
        rotation: totalRotation
      });
      this.reset();
    }
    cancelRendering() {
      if (this.renderTask) {
        this.renderTask.cancel();
        this.renderTask = null;
      }
      this.resume = null;
    }
    _getPageDrawContext() {
      let upscaleFactor = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 1;
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d", {
        alpha: false
      });
      const outputScale = new _ui_utils.OutputScale();
      canvas.width = upscaleFactor * this.canvasWidth * outputScale.sx | 0;
      canvas.height = upscaleFactor * this.canvasHeight * outputScale.sy | 0;
      const transform = outputScale.scaled ? [outputScale.sx, 0, 0, outputScale.sy, 0, 0] : null;
      return {
        ctx,
        canvas,
        transform
      };
    }
    _convertCanvasToImage(canvas) {
      if (this.renderingState !== _ui_utils.RenderingStates.FINISHED) {
        throw new Error("_convertCanvasToImage: Rendering has not finished.");
      }
      const reducedCanvas = this._reduceImage(canvas);
      const image = document.createElement("img");
      image.className = "thumbnailImage";
      this._thumbPageCanvas.then(msg => {
        image.setAttribute("aria-label", msg);
      });
      image.src = reducedCanvas.toDataURL();
      this.image = image;
      this.div.setAttribute("data-loaded", true);
      this._placeholderImg.replaceWith(image);
      reducedCanvas.width = 0;
      reducedCanvas.height = 0;
    }
    async draw() {
      if (this.renderingState !== _ui_utils.RenderingStates.INITIAL) {
        console.error("Must be in new state before drawing");
        return undefined;
      }
      const {
        pdfPage
      } = this;
      if (!pdfPage) {
        this.renderingState = _ui_utils.RenderingStates.FINISHED;
        throw new Error("pdfPage is not loaded");
      }
      this.renderingState = _ui_utils.RenderingStates.RUNNING;
      const {
        ctx,
        canvas,
        transform
      } = this._getPageDrawContext(DRAW_UPSCALE_FACTOR);
      const drawViewport = this.viewport.clone({
        scale: DRAW_UPSCALE_FACTOR * this.scale
      });
      const renderContinueCallback = cont => {
        if (!this.renderingQueue.isHighestPriority(this)) {
          this.renderingState = _ui_utils.RenderingStates.PAUSED;
          this.resume = () => {
            this.renderingState = _ui_utils.RenderingStates.RUNNING;
            cont();
          };
          return;
        }
        cont();
      };
      const renderContext = {
        canvasContext: ctx,
        transform,
        viewport: drawViewport,
        optionalContentConfigPromise: this._optionalContentConfigPromise,
        pageColors: this.pageColors
      };
      const renderTask = this.renderTask = pdfPage.render(renderContext);
      renderTask.onContinue = renderContinueCallback;
      const resultPromise = renderTask.promise.then(() => _classPrivateMethodGet(this, _finishRenderTask, _finishRenderTask2).call(this, renderTask, canvas), error => _classPrivateMethodGet(this, _finishRenderTask, _finishRenderTask2).call(this, renderTask, canvas, error));
      resultPromise.finally(() => {
        canvas.width = 0;
        canvas.height = 0;
        this.eventBus.dispatch("thumbnailrendered", {
          source: this,
          pageNumber: this.id,
          pdfPage: this.pdfPage
        });
      });
      return resultPromise;
    }
    setImage(pageView) {
      if (this.renderingState !== _ui_utils.RenderingStates.INITIAL) {
        return;
      }
      const {
        thumbnailCanvas: canvas,
        pdfPage,
        scale
      } = pageView;
      if (!canvas) {
        return;
      }
      if (!this.pdfPage) {
        this.setPdfPage(pdfPage);
      }
      if (scale < this.scale) {
        return;
      }
      this.renderingState = _ui_utils.RenderingStates.FINISHED;
      this._convertCanvasToImage(canvas);
    }
    _reduceImage(img) {
      const {
        ctx,
        canvas
      } = this._getPageDrawContext();
      if (img.width <= 2 * canvas.width) {
        ctx.drawImage(img, 0, 0, img.width, img.height, 0, 0, canvas.width, canvas.height);
        return canvas;
      }
      let reducedWidth = canvas.width << MAX_NUM_SCALING_STEPS;
      let reducedHeight = canvas.height << MAX_NUM_SCALING_STEPS;
      const [reducedImage, reducedImageCtx] = TempImageFactory.getCanvas(reducedWidth, reducedHeight);
      while (reducedWidth > img.width || reducedHeight > img.height) {
        reducedWidth >>= 1;
        reducedHeight >>= 1;
      }
      reducedImageCtx.drawImage(img, 0, 0, img.width, img.height, 0, 0, reducedWidth, reducedHeight);
      while (reducedWidth > 2 * canvas.width) {
        reducedImageCtx.drawImage(reducedImage, 0, 0, reducedWidth, reducedHeight, 0, 0, reducedWidth >> 1, reducedHeight >> 1);
        reducedWidth >>= 1;
        reducedHeight >>= 1;
      }
      ctx.drawImage(reducedImage, 0, 0, reducedWidth, reducedHeight, 0, 0, canvas.width, canvas.height);
      return canvas;
    }
    get _thumbPageTitle() {
      var _this$pageLabel;
      return this.l10n.get("thumb_page_title", {
        page: (_this$pageLabel = this.pageLabel) !== null && _this$pageLabel !== void 0 ? _this$pageLabel : this.id
      });
    }
    get _thumbPageCanvas() {
      var _this$pageLabel2;
      return this.l10n.get("thumb_page_canvas", {
        page: (_this$pageLabel2 = this.pageLabel) !== null && _this$pageLabel2 !== void 0 ? _this$pageLabel2 : this.id
      });
    }
    setPageLabel(label) {
      this.pageLabel = typeof label === "string" ? label : null;
      this._thumbPageTitle.then(msg => {
        this.anchor.title = msg;
      });
      if (this.renderingState !== _ui_utils.RenderingStates.FINISHED) {
        return;
      }
      this._thumbPageCanvas.then(msg => {
        var _this$image2;
        (_this$image2 = this.image) === null || _this$image2 === void 0 || _this$image2.setAttribute("aria-label", msg);
      });
    }
  }
  exports.PDFThumbnailView = PDFThumbnailView;
  function _updateDims2() {
    const {
      width,
      height
    } = this.viewport;
    const ratio = width / height;
    this.canvasWidth = THUMBNAIL_WIDTH;
    this.canvasHeight = this.canvasWidth / ratio | 0;
    this.scale = this.canvasWidth / width;
    const {
      style
    } = this.div;
    style.setProperty("--thumbnail-width", `${this.canvasWidth}px`);
    style.setProperty("--thumbnail-height", `${this.canvasHeight}px`);
  }
  async function _finishRenderTask2(renderTask, canvas) {
    let error = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
    if (renderTask === this.renderTask) {
      this.renderTask = null;
    }
    if (error instanceof _pdfjsLib.RenderingCancelledException) {
      return;
    }
    this.renderingState = _ui_utils.RenderingStates.FINISHED;
    this._convertCanvasToImage(canvas);
    if (error) {
      throw error;
    }
  }
  
  /***/ }),
  /* 210 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PagesCountLimit = exports.PDFViewer = exports.PDFPageViewBuffer = void 0;
  __webpack_require__(131);
  __webpack_require__(158);
  __webpack_require__(169);
  __webpack_require__(171);
  __webpack_require__(173);
  __webpack_require__(175);
  __webpack_require__(177);
  __webpack_require__(179);
  __webpack_require__(122);
  __webpack_require__(2);
  __webpack_require__(142);
  __webpack_require__(205);
  var _resizeObserverPolyfill = _interopRequireDefault(__webpack_require__(211));
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  var _l10n_utils = __webpack_require__(213);
  var _pdf_page_view = __webpack_require__(214);
  var _pdf_rendering_queue = __webpack_require__(204);
  var _pdf_link_service = __webpack_require__(185);
  let _Symbol$iterator;
  function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  const DEFAULT_CACHE_SIZE = 10;
  const PagesCountLimit = {
    FORCE_SCROLL_MODE_PAGE: 15000,
    FORCE_LAZY_PAGE_INIT: 7500,
    PAUSE_EAGER_PAGE_INIT: 250
  };
  exports.PagesCountLimit = PagesCountLimit;
  function isValidAnnotationEditorMode(mode) {
    return Object.values(_pdfjsLib.AnnotationEditorType).includes(mode) && mode !== _pdfjsLib.AnnotationEditorType.DISABLE;
  }
  var _buf = /*#__PURE__*/new WeakMap();
  var _size = /*#__PURE__*/new WeakMap();
  var _destroyFirstView = /*#__PURE__*/new WeakSet();
  _Symbol$iterator = Symbol.iterator;
  class PDFPageViewBuffer {
    constructor(size) {
      _classPrivateMethodInitSpec(this, _destroyFirstView);
      _classPrivateFieldInitSpec(this, _buf, {
        writable: true,
        value: new Set()
      });
      _classPrivateFieldInitSpec(this, _size, {
        writable: true,
        value: 0
      });
      _classPrivateFieldSet(this, _size, size);
    }
    push(view) {
      const buf = _classPrivateFieldGet(this, _buf);
      if (buf.has(view)) {
        buf.delete(view);
      }
      buf.add(view);
      if (buf.size > _classPrivateFieldGet(this, _size)) {
        _classPrivateMethodGet(this, _destroyFirstView, _destroyFirstView2).call(this);
      }
    }
    resize(newSize) {
      let idsToKeep = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      _classPrivateFieldSet(this, _size, newSize);
      const buf = _classPrivateFieldGet(this, _buf);
      if (idsToKeep) {
        const ii = buf.size;
        let i = 1;
        for (const view of buf) {
          if (idsToKeep.has(view.id)) {
            buf.delete(view);
            buf.add(view);
          }
          if (++i > ii) {
            break;
          }
        }
      }
      while (buf.size > _classPrivateFieldGet(this, _size)) {
        _classPrivateMethodGet(this, _destroyFirstView, _destroyFirstView2).call(this);
      }
    }
    has(view) {
      return _classPrivateFieldGet(this, _buf).has(view);
    }
    [_Symbol$iterator]() {
      return _classPrivateFieldGet(this, _buf).keys();
    }
  }
  exports.PDFPageViewBuffer = PDFPageViewBuffer;
  function _destroyFirstView2() {
    const firstView = _classPrivateFieldGet(this, _buf).keys().next().value;
    firstView === null || firstView === void 0 || firstView.destroy();
    _classPrivateFieldGet(this, _buf).delete(firstView);
  }
  var _buffer = /*#__PURE__*/new WeakMap();
  var _altTextManager = /*#__PURE__*/new WeakMap();
  var _annotationEditorMode = /*#__PURE__*/new WeakMap();
  var _annotationEditorUIManager = /*#__PURE__*/new WeakMap();
  var _annotationMode = /*#__PURE__*/new WeakMap();
  var _containerTopLeft = /*#__PURE__*/new WeakMap();
  var _copyCallbackBound = /*#__PURE__*/new WeakMap();
  var _enablePermissions = /*#__PURE__*/new WeakMap();
  var _getAllTextInProgress = /*#__PURE__*/new WeakMap();
  var _hiddenCopyElement = /*#__PURE__*/new WeakMap();
  var _interruptCopyCondition = /*#__PURE__*/new WeakMap();
  var _previousContainerHeight = /*#__PURE__*/new WeakMap();
  var _resizeObserver = /*#__PURE__*/new WeakMap();
  var _scrollModePageState = /*#__PURE__*/new WeakMap();
  var _onVisibilityChange = /*#__PURE__*/new WeakMap();
  var _scaleTimeoutId = /*#__PURE__*/new WeakMap();
  var _textLayerMode = /*#__PURE__*/new WeakMap();
  var _layerProperties = /*#__PURE__*/new WeakSet();
  var _initializePermissions = /*#__PURE__*/new WeakSet();
  var _onePageRenderedOrForceFetch = /*#__PURE__*/new WeakSet();
  var _copyCallback = /*#__PURE__*/new WeakSet();
  var _ensurePageViewVisible = /*#__PURE__*/new WeakSet();
  var _scrollIntoView = /*#__PURE__*/new WeakSet();
  var _isSameScale = /*#__PURE__*/new WeakSet();
  var _setScaleUpdatePages = /*#__PURE__*/new WeakSet();
  var _pageWidthScaleFactor = /*#__PURE__*/new WeakMap();
  var _setScale = /*#__PURE__*/new WeakSet();
  var _resetCurrentPageView = /*#__PURE__*/new WeakSet();
  var _ensurePdfPageLoaded = /*#__PURE__*/new WeakSet();
  var _getScrollAhead = /*#__PURE__*/new WeakSet();
  var _updateContainerHeightCss = /*#__PURE__*/new WeakSet();
  var _resizeObserverCallback = /*#__PURE__*/new WeakSet();
  class PDFViewer {
    constructor(_options) {
      var _this$container, _this$viewer, _options$textLayerMod, _options$annotationMo, _options$annotationEd, _options$isOffscreenC;
      _classPrivateMethodInitSpec(this, _resizeObserverCallback);
      _classPrivateMethodInitSpec(this, _updateContainerHeightCss);
      _classPrivateMethodInitSpec(this, _getScrollAhead);
      _classPrivateMethodInitSpec(this, _ensurePdfPageLoaded);
      _classPrivateMethodInitSpec(this, _resetCurrentPageView);
      _classPrivateMethodInitSpec(this, _setScale);
      _classPrivateFieldInitSpec(this, _pageWidthScaleFactor, {
        get: _get_pageWidthScaleFactor,
        set: void 0
      });
      _classPrivateMethodInitSpec(this, _setScaleUpdatePages);
      _classPrivateMethodInitSpec(this, _isSameScale);
      _classPrivateMethodInitSpec(this, _scrollIntoView);
      _classPrivateMethodInitSpec(this, _ensurePageViewVisible);
      _classPrivateMethodInitSpec(this, _copyCallback);
      _classPrivateMethodInitSpec(this, _onePageRenderedOrForceFetch);
      _classPrivateMethodInitSpec(this, _initializePermissions);
      _classPrivateMethodInitSpec(this, _layerProperties);
      _classPrivateFieldInitSpec(this, _buffer, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _altTextManager, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _annotationEditorMode, {
        writable: true,
        value: _pdfjsLib.AnnotationEditorType.NONE
      });
      _classPrivateFieldInitSpec(this, _annotationEditorUIManager, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _annotationMode, {
        writable: true,
        value: _pdfjsLib.AnnotationMode.ENABLE_FORMS
      });
      _classPrivateFieldInitSpec(this, _containerTopLeft, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _copyCallbackBound, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _enablePermissions, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _getAllTextInProgress, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _hiddenCopyElement, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _interruptCopyCondition, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _previousContainerHeight, {
        writable: true,
        value: 0
      });
      _classPrivateFieldInitSpec(this, _resizeObserver, {
        writable: true,
        value: new _resizeObserverPolyfill.default(_classPrivateMethodGet(this, _resizeObserverCallback, _resizeObserverCallback2).bind(this))
      });
      _classPrivateFieldInitSpec(this, _scrollModePageState, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _onVisibilityChange, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _scaleTimeoutId, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _textLayerMode, {
        writable: true,
        value: _ui_utils.TextLayerMode.ENABLE
      });
      const viewerVersion = '3.11.176';
      if (_pdfjsLib.version !== viewerVersion) {
        throw new Error(`The API version "${_pdfjsLib.version}" does not match the Viewer version "${viewerVersion}".`);
      }
      this.container = _options.container;
      this.viewer = _options.viewer || _options.container.firstElementChild;
      if (((_this$container = this.container) === null || _this$container === void 0 ? void 0 : _this$container.tagName) !== "DIV" || ((_this$viewer = this.viewer) === null || _this$viewer === void 0 ? void 0 : _this$viewer.tagName) !== "DIV") {
        throw new Error("Invalid `container` and/or `viewer` option.");
      }
      if (this.container.offsetParent && getComputedStyle(this.container).position !== "absolute") {
        throw new Error("The `container` must be absolutely positioned.");
      }
      _classPrivateFieldGet(this, _resizeObserver).observe(this.container);
      this.eventBus = _options.eventBus;
      this.linkService = _options.linkService || new _pdf_link_service.SimpleLinkService();
      this.downloadManager = _options.downloadManager || null;
      this.findController = _options.findController || null;
      _classPrivateFieldSet(this, _altTextManager, _options.altTextManager || null);
      if (this.findController) {
        this.findController.onIsPageVisible = pageNumber => this._getVisiblePages().ids.has(pageNumber);
      }
      this._scriptingManager = _options.scriptingManager || null;
      _classPrivateFieldSet(this, _textLayerMode, (_options$textLayerMod = _options.textLayerMode) !== null && _options$textLayerMod !== void 0 ? _options$textLayerMod : _ui_utils.TextLayerMode.ENABLE);
      _classPrivateFieldSet(this, _annotationMode, (_options$annotationMo = _options.annotationMode) !== null && _options$annotationMo !== void 0 ? _options$annotationMo : _pdfjsLib.AnnotationMode.ENABLE_FORMS);
      _classPrivateFieldSet(this, _annotationEditorMode, (_options$annotationEd = _options.annotationEditorMode) !== null && _options$annotationEd !== void 0 ? _options$annotationEd : _pdfjsLib.AnnotationEditorType.NONE);
      this.imageResourcesPath = _options.imageResourcesPath || "";
      this.enablePrintAutoRotate = _options.enablePrintAutoRotate || false;
      this.removePageBorders = _options.removePageBorders || false;
      if (_options.useOnlyCssZoom) {
        console.error("useOnlyCssZoom was removed, please use `maxCanvasPixels = 0` instead.");
        _options.maxCanvasPixels = 0;
      }
      this.isOffscreenCanvasSupported = (_options$isOffscreenC = _options.isOffscreenCanvasSupported) !== null && _options$isOffscreenC !== void 0 ? _options$isOffscreenC : true;
      this.maxCanvasPixels = _options.maxCanvasPixels;
      this.l10n = _options.l10n || _l10n_utils.NullL10n;
      _classPrivateFieldSet(this, _enablePermissions, _options.enablePermissions || false);
      this.pageColors = _options.pageColors || null;
      this.defaultRenderingQueue = !_options.renderingQueue;
      if (this.defaultRenderingQueue) {
        this.renderingQueue = new _pdf_rendering_queue.PDFRenderingQueue();
        this.renderingQueue.setViewer(this);
      } else {
        this.renderingQueue = _options.renderingQueue;
      }
      this.scroll = (0, _ui_utils.watchScroll)(this.container, this._scrollUpdate.bind(this));
      this.presentationModeState = _ui_utils.PresentationModeState.UNKNOWN;
      this._onBeforeDraw = this._onAfterDraw = null;
      this._resetView();
      if (this.removePageBorders) {
        this.viewer.classList.add("removePageBorders");
      }
      _classPrivateMethodGet(this, _updateContainerHeightCss, _updateContainerHeightCss2).call(this);
      this.eventBus._on("thumbnailrendered", _ref => {
        let {
          pageNumber,
          pdfPage
        } = _ref;
        const pageView = this._pages[pageNumber - 1];
        if (!_classPrivateFieldGet(this, _buffer).has(pageView)) {
          pdfPage === null || pdfPage === void 0 || pdfPage.cleanup();
        }
      });
    }
    get pagesCount() {
      return this._pages.length;
    }
    getPageView(index) {
      return this._pages[index];
    }
    getCachedPageViews() {
      return new Set(_classPrivateFieldGet(this, _buffer));
    }
    get pageViewsReady() {
      return this._pagesCapability.settled && this._pages.every(pageView => pageView === null || pageView === void 0 ? void 0 : pageView.pdfPage);
    }
    get renderForms() {
      return _classPrivateFieldGet(this, _annotationMode) === _pdfjsLib.AnnotationMode.ENABLE_FORMS;
    }
    get enableScripting() {
      return !!this._scriptingManager;
    }
    get currentPageNumber() {
      return this._currentPageNumber;
    }
    set currentPageNumber(val) {
      if (!Number.isInteger(val)) {
        throw new Error("Invalid page number.");
      }
      if (!this.pdfDocument) {
        return;
      }
      if (!this._setCurrentPageNumber(val, true)) {
        console.error(`currentPageNumber: "${val}" is not a valid page.`);
      }
    }
    _setCurrentPageNumber(val) {
      var _this$_pageLabels, _this$_pageLabels2;
      let resetCurrentPageView = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      if (this._currentPageNumber === val) {
        if (resetCurrentPageView) {
          _classPrivateMethodGet(this, _resetCurrentPageView, _resetCurrentPageView2).call(this);
        }
        return true;
      }
      if (!(0 < val && val <= this.pagesCount)) {
        return false;
      }
      const previous = this._currentPageNumber;
      this._currentPageNumber = val;
      this.eventBus.dispatch("pagechanging", {
        source: this,
        pageNumber: val,
        pageLabel: (_this$_pageLabels = (_this$_pageLabels2 = this._pageLabels) === null || _this$_pageLabels2 === void 0 ? void 0 : _this$_pageLabels2[val - 1]) !== null && _this$_pageLabels !== void 0 ? _this$_pageLabels : null,
        previous
      });
      if (resetCurrentPageView) {
        _classPrivateMethodGet(this, _resetCurrentPageView, _resetCurrentPageView2).call(this);
      }
      return true;
    }
    get currentPageLabel() {
      var _this$_pageLabels3, _this$_pageLabels4;
      return (_this$_pageLabels3 = (_this$_pageLabels4 = this._pageLabels) === null || _this$_pageLabels4 === void 0 ? void 0 : _this$_pageLabels4[this._currentPageNumber - 1]) !== null && _this$_pageLabels3 !== void 0 ? _this$_pageLabels3 : null;
    }
    set currentPageLabel(val) {
      if (!this.pdfDocument) {
        return;
      }
      let page = val | 0;
      if (this._pageLabels) {
        const i = this._pageLabels.indexOf(val);
        if (i >= 0) {
          page = i + 1;
        }
      }
      if (!this._setCurrentPageNumber(page, true)) {
        console.error(`currentPageLabel: "${val}" is not a valid page.`);
      }
    }
    get currentScale() {
      return this._currentScale !== _ui_utils.UNKNOWN_SCALE ? this._currentScale : _ui_utils.DEFAULT_SCALE;
    }
    set currentScale(val) {
      if (isNaN(val)) {
        throw new Error("Invalid numeric scale.");
      }
      if (!this.pdfDocument) {
        return;
      }
      _classPrivateMethodGet(this, _setScale, _setScale2).call(this, val, {
        noScroll: false
      });
    }
    get currentScaleValue() {
      return this._currentScaleValue;
    }
    set currentScaleValue(val) {
      if (!this.pdfDocument) {
        return;
      }
      _classPrivateMethodGet(this, _setScale, _setScale2).call(this, val, {
        noScroll: false
      });
    }
    get pagesRotation() {
      return this._pagesRotation;
    }
    set pagesRotation(rotation) {
      if (!(0, _ui_utils.isValidRotation)(rotation)) {
        throw new Error("Invalid pages rotation angle.");
      }
      if (!this.pdfDocument) {
        return;
      }
      rotation %= 360;
      if (rotation < 0) {
        rotation += 360;
      }
      if (this._pagesRotation === rotation) {
        return;
      }
      this._pagesRotation = rotation;
      const pageNumber = this._currentPageNumber;
      this.refresh(true, {
        rotation
      });
      if (this._currentScaleValue) {
        _classPrivateMethodGet(this, _setScale, _setScale2).call(this, this._currentScaleValue, {
          noScroll: true
        });
      }
      this.eventBus.dispatch("rotationchanging", {
        source: this,
        pagesRotation: rotation,
        pageNumber
      });
      if (this.defaultRenderingQueue) {
        this.update();
      }
    }
    get firstPagePromise() {
      return this.pdfDocument ? this._firstPageCapability.promise : null;
    }
    get onePageRendered() {
      return this.pdfDocument ? this._onePageRenderedCapability.promise : null;
    }
    get pagesPromise() {
      return this.pdfDocument ? this._pagesCapability.promise : null;
    }
    async getAllText() {
      const texts = [];
      const buffer = [];
      for (let pageNum = 1, pagesCount = this.pdfDocument.numPages; pageNum <= pagesCount; ++pageNum) {
        if (_classPrivateFieldGet(this, _interruptCopyCondition)) {
          return null;
        }
        buffer.length = 0;
        const page = await this.pdfDocument.getPage(pageNum);
        const {
          items
        } = await page.getTextContent();
        for (const item of items) {
          if (item.str) {
            buffer.push(item.str);
          }
          if (item.hasEOL) {
            buffer.push("\n");
          }
        }
        texts.push((0, _ui_utils.removeNullCharacters)(buffer.join("")));
      }
      return texts.join("\n");
    }
    setDocument(pdfDocument) {
      if (this.pdfDocument) {
        var _this$findController, _this$_scriptingManag;
        this.eventBus.dispatch("pagesdestroy", {
          source: this
        });
        this._cancelRendering();
        this._resetView();
        (_this$findController = this.findController) === null || _this$findController === void 0 || _this$findController.setDocument(null);
        (_this$_scriptingManag = this._scriptingManager) === null || _this$_scriptingManag === void 0 || _this$_scriptingManag.setDocument(null);
        if (_classPrivateFieldGet(this, _annotationEditorUIManager)) {
          _classPrivateFieldGet(this, _annotationEditorUIManager).destroy();
          _classPrivateFieldSet(this, _annotationEditorUIManager, null);
        }
      }
      this.pdfDocument = pdfDocument;
      if (!pdfDocument) {
        return;
      }
      const pagesCount = pdfDocument.numPages;
      const firstPagePromise = pdfDocument.getPage(1);
      const optionalContentConfigPromise = pdfDocument.getOptionalContentConfig();
      const permissionsPromise = _classPrivateFieldGet(this, _enablePermissions) ? pdfDocument.getPermissions() : Promise.resolve();
      if (pagesCount > PagesCountLimit.FORCE_SCROLL_MODE_PAGE) {
        console.warn("Forcing PAGE-scrolling for performance reasons, given the length of the document.");
        const mode = this._scrollMode = _ui_utils.ScrollMode.PAGE;
        this.eventBus.dispatch("scrollmodechanged", {
          source: this,
          mode
        });
      }
      this._pagesCapability.promise.then(() => {
        this.eventBus.dispatch("pagesloaded", {
          source: this,
          pagesCount
        });
      }, () => {});
      this._onBeforeDraw = evt => {
        const pageView = this._pages[evt.pageNumber - 1];
        if (!pageView) {
          return;
        }
        _classPrivateFieldGet(this, _buffer).push(pageView);
      };
      this.eventBus._on("pagerender", this._onBeforeDraw);
      this._onAfterDraw = evt => {
        if (evt.cssTransform || this._onePageRenderedCapability.settled) {
          return;
        }
        this._onePageRenderedCapability.resolve({
          timestamp: evt.timestamp
        });
        this.eventBus._off("pagerendered", this._onAfterDraw);
        this._onAfterDraw = null;
        if (_classPrivateFieldGet(this, _onVisibilityChange)) {
          document.removeEventListener("visibilitychange", _classPrivateFieldGet(this, _onVisibilityChange));
          _classPrivateFieldSet(this, _onVisibilityChange, null);
        }
      };
      this.eventBus._on("pagerendered", this._onAfterDraw);
      Promise.all([firstPagePromise, permissionsPromise]).then(_ref2 => {
        var _this$pageColors, _this$pageColors2;
        let [firstPdfPage, permissions] = _ref2;
        if (pdfDocument !== this.pdfDocument) {
          return;
        }
        this._firstPageCapability.resolve(firstPdfPage);
        this._optionalContentConfigPromise = optionalContentConfigPromise;
        const {
          annotationEditorMode,
          annotationMode,
          textLayerMode
        } = _classPrivateMethodGet(this, _initializePermissions, _initializePermissions2).call(this, permissions);
        if (textLayerMode !== _ui_utils.TextLayerMode.DISABLE) {
          const element = _classPrivateFieldSet(this, _hiddenCopyElement, document.createElement("div"));
          element.id = "hiddenCopyElement";
          this.viewer.before(element);
        }
        if (annotationEditorMode !== _pdfjsLib.AnnotationEditorType.DISABLE) {
          const mode = annotationEditorMode;
          if (pdfDocument.isPureXfa) {
            console.warn("Warning: XFA-editing is not implemented.");
          } else if (isValidAnnotationEditorMode(mode)) {
            _classPrivateFieldSet(this, _annotationEditorUIManager, new _pdfjsLib.AnnotationEditorUIManager(this.container, this.viewer, _classPrivateFieldGet(this, _altTextManager), this.eventBus, pdfDocument, this.pageColors));
            if (mode !== _pdfjsLib.AnnotationEditorType.NONE) {
              _classPrivateFieldGet(this, _annotationEditorUIManager).updateMode(mode);
            }
          } else {
            console.error(`Invalid AnnotationEditor mode: ${mode}`);
          }
        }
        const layerProperties = _classPrivateMethodGet(this, _layerProperties, _layerProperties2).bind(this);
        const viewerElement = this._scrollMode === _ui_utils.ScrollMode.PAGE ? null : this.viewer;
        const scale = this.currentScale;
        const viewport = firstPdfPage.getViewport({
          scale: scale * _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS
        });
        this.viewer.style.setProperty("--scale-factor", viewport.scale);
        if (((_this$pageColors = this.pageColors) === null || _this$pageColors === void 0 ? void 0 : _this$pageColors.foreground) === "CanvasText" || ((_this$pageColors2 = this.pageColors) === null || _this$pageColors2 === void 0 ? void 0 : _this$pageColors2.background) === "Canvas") {
          this.viewer.style.setProperty("--hcm-highligh-filter", pdfDocument.filterFactory.addHighlightHCMFilter("CanvasText", "Canvas", "HighlightText", "Highlight"));
        }
        for (let pageNum = 1; pageNum <= pagesCount; ++pageNum) {
          const pageView = new _pdf_page_view.PDFPageView({
            container: viewerElement,
            eventBus: this.eventBus,
            id: pageNum,
            scale,
            defaultViewport: viewport.clone(),
            optionalContentConfigPromise,
            renderingQueue: this.renderingQueue,
            textLayerMode,
            annotationMode,
            imageResourcesPath: this.imageResourcesPath,
            isOffscreenCanvasSupported: this.isOffscreenCanvasSupported,
            maxCanvasPixels: this.maxCanvasPixels,
            pageColors: this.pageColors,
            l10n: this.l10n,
            layerProperties
          });
          this._pages.push(pageView);
        }
        const firstPageView = this._pages[0];
        if (firstPageView) {
          firstPageView.setPdfPage(firstPdfPage);
          this.linkService.cachePageRef(1, firstPdfPage.ref);
        }
        if (this._scrollMode === _ui_utils.ScrollMode.PAGE) {
          _classPrivateMethodGet(this, _ensurePageViewVisible, _ensurePageViewVisible2).call(this);
        } else if (this._spreadMode !== _ui_utils.SpreadMode.NONE) {
          this._updateSpreadMode();
        }
        _classPrivateMethodGet(this, _onePageRenderedOrForceFetch, _onePageRenderedOrForceFetch2).call(this).then(async () => {
          var _this$findController2, _this$_scriptingManag2;
          (_this$findController2 = this.findController) === null || _this$findController2 === void 0 || _this$findController2.setDocument(pdfDocument);
          (_this$_scriptingManag2 = this._scriptingManager) === null || _this$_scriptingManag2 === void 0 || _this$_scriptingManag2.setDocument(pdfDocument);
          if (_classPrivateFieldGet(this, _hiddenCopyElement)) {
            _classPrivateFieldSet(this, _copyCallbackBound, _classPrivateMethodGet(this, _copyCallback, _copyCallback2).bind(this, textLayerMode));
            document.addEventListener("copy", _classPrivateFieldGet(this, _copyCallbackBound));
          }
          if (_classPrivateFieldGet(this, _annotationEditorUIManager)) {
            this.eventBus.dispatch("annotationeditormodechanged", {
              source: this,
              mode: _classPrivateFieldGet(this, _annotationEditorMode)
            });
          }
          if (pdfDocument.loadingParams.disableAutoFetch || pagesCount > PagesCountLimit.FORCE_LAZY_PAGE_INIT) {
            this._pagesCapability.resolve();
            return;
          }
          let getPagesLeft = pagesCount - 1;
          if (getPagesLeft <= 0) {
            this._pagesCapability.resolve();
            return;
          }
          for (let pageNum = 2; pageNum <= pagesCount; ++pageNum) {
            const promise = pdfDocument.getPage(pageNum).then(pdfPage => {
              const pageView = this._pages[pageNum - 1];
              if (!pageView.pdfPage) {
                pageView.setPdfPage(pdfPage);
              }
              this.linkService.cachePageRef(pageNum, pdfPage.ref);
              if (--getPagesLeft === 0) {
                this._pagesCapability.resolve();
              }
            }, reason => {
              console.error(`Unable to get page ${pageNum} to initialize viewer`, reason);
              if (--getPagesLeft === 0) {
                this._pagesCapability.resolve();
              }
            });
            if (pageNum % PagesCountLimit.PAUSE_EAGER_PAGE_INIT === 0) {
              await promise;
            }
          }
        });
        this.eventBus.dispatch("pagesinit", {
          source: this
        });
        pdfDocument.getMetadata().then(_ref3 => {
          let {
            info
          } = _ref3;
          if (pdfDocument !== this.pdfDocument) {
            return;
          }
          if (info.Language) {
            this.viewer.lang = info.Language;
          }
        });
        if (this.defaultRenderingQueue) {
          this.update();
        }
      }).catch(reason => {
        console.error("Unable to initialize viewer", reason);
        this._pagesCapability.reject(reason);
      });
    }
    setPageLabels(labels) {
      if (!this.pdfDocument) {
        return;
      }
      if (!labels) {
        this._pageLabels = null;
      } else if (!(Array.isArray(labels) && this.pdfDocument.numPages === labels.length)) {
        this._pageLabels = null;
        console.error(`setPageLabels: Invalid page labels.`);
      } else {
        this._pageLabels = labels;
      }
      for (let i = 0, ii = this._pages.length; i < ii; i++) {
        var _this$_pageLabels$i, _this$_pageLabels5;
        this._pages[i].setPageLabel((_this$_pageLabels$i = (_this$_pageLabels5 = this._pageLabels) === null || _this$_pageLabels5 === void 0 ? void 0 : _this$_pageLabels5[i]) !== null && _this$_pageLabels$i !== void 0 ? _this$_pageLabels$i : null);
      }
    }
    _resetView() {
      this._pages = [];
      this._currentPageNumber = 1;
      this._currentScale = _ui_utils.UNKNOWN_SCALE;
      this._currentScaleValue = null;
      this._pageLabels = null;
      _classPrivateFieldSet(this, _buffer, new PDFPageViewBuffer(DEFAULT_CACHE_SIZE));
      this._location = null;
      this._pagesRotation = 0;
      this._optionalContentConfigPromise = null;
      this._firstPageCapability = new _pdfjsLib.PromiseCapability();
      this._onePageRenderedCapability = new _pdfjsLib.PromiseCapability();
      this._pagesCapability = new _pdfjsLib.PromiseCapability();
      this._scrollMode = _ui_utils.ScrollMode.VERTICAL;
      this._previousScrollMode = _ui_utils.ScrollMode.UNKNOWN;
      this._spreadMode = _ui_utils.SpreadMode.NONE;
      _classPrivateFieldSet(this, _scrollModePageState, {
        previousPageNumber: 1,
        scrollDown: true,
        pages: []
      });
      if (this._onBeforeDraw) {
        this.eventBus._off("pagerender", this._onBeforeDraw);
        this._onBeforeDraw = null;
      }
      if (this._onAfterDraw) {
        this.eventBus._off("pagerendered", this._onAfterDraw);
        this._onAfterDraw = null;
      }
      if (_classPrivateFieldGet(this, _onVisibilityChange)) {
        document.removeEventListener("visibilitychange", _classPrivateFieldGet(this, _onVisibilityChange));
        _classPrivateFieldSet(this, _onVisibilityChange, null);
      }
      this.viewer.textContent = "";
      this._updateScrollMode();
      this.viewer.removeAttribute("lang");
      if (_classPrivateFieldGet(this, _hiddenCopyElement)) {
        document.removeEventListener("copy", _classPrivateFieldGet(this, _copyCallbackBound));
        _classPrivateFieldSet(this, _copyCallbackBound, null);
        _classPrivateFieldGet(this, _hiddenCopyElement).remove();
        _classPrivateFieldSet(this, _hiddenCopyElement, null);
      }
    }
    _scrollUpdate() {
      if (this.pagesCount === 0) {
        return;
      }
      this.update();
    }
    pageLabelToPageNumber(label) {
      if (!this._pageLabels) {
        return null;
      }
      const i = this._pageLabels.indexOf(label);
      if (i < 0) {
        return null;
      }
      return i + 1;
    }
    scrollPageIntoView(_ref4) {
      let {
        pageNumber,
        destArray = null,
        allowNegativeOffset = false,
        ignoreDestinationZoom = false
      } = _ref4;
      if (!this.pdfDocument) {
        return;
      }
      const pageView = Number.isInteger(pageNumber) && this._pages[pageNumber - 1];
      if (!pageView) {
        console.error(`scrollPageIntoView: "${pageNumber}" is not a valid pageNumber parameter.`);
        return;
      }
      if (this.isInPresentationMode || !destArray) {
        this._setCurrentPageNumber(pageNumber, true);
        return;
      }
      let x = 0,
        y = 0;
      let width = 0,
        height = 0,
        widthScale,
        heightScale;
      const changeOrientation = pageView.rotation % 180 !== 0;
      const pageWidth = (changeOrientation ? pageView.height : pageView.width) / pageView.scale / _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS;
      const pageHeight = (changeOrientation ? pageView.width : pageView.height) / pageView.scale / _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS;
      let scale = 0;
      switch (destArray[1].name) {
        case "XYZ":
          x = destArray[2];
          y = destArray[3];
          scale = destArray[4];
          x = x !== null ? x : 0;
          y = y !== null ? y : pageHeight;
          break;
        case "Fit":
        case "FitB":
          scale = "page-fit";
          break;
        case "FitH":
        case "FitBH":
          y = destArray[2];
          scale = "page-width";
          if (y === null && this._location) {
            x = this._location.left;
            y = this._location.top;
          } else if (typeof y !== "number" || y < 0) {
            y = pageHeight;
          }
          break;
        case "FitV":
        case "FitBV":
          x = destArray[2];
          width = pageWidth;
          height = pageHeight;
          scale = "page-height";
          break;
        case "FitR":
          x = destArray[2];
          y = destArray[3];
          width = destArray[4] - x;
          height = destArray[5] - y;
          let hPadding = _ui_utils.SCROLLBAR_PADDING,
            vPadding = _ui_utils.VERTICAL_PADDING;
          if (this.removePageBorders) {
            hPadding = vPadding = 0;
          }
          widthScale = (this.container.clientWidth - hPadding) / width / _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS;
          heightScale = (this.container.clientHeight - vPadding) / height / _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS;
          scale = Math.min(Math.abs(widthScale), Math.abs(heightScale));
          break;
        default:
          console.error(`scrollPageIntoView: "${destArray[1].name}" is not a valid destination type.`);
          return;
      }
      if (!ignoreDestinationZoom) {
        if (scale && scale !== this._currentScale) {
          this.currentScaleValue = scale;
        } else if (this._currentScale === _ui_utils.UNKNOWN_SCALE) {
          this.currentScaleValue = _ui_utils.DEFAULT_SCALE_VALUE;
        }
      }
      if (scale === "page-fit" && !destArray[4]) {
        _classPrivateMethodGet(this, _scrollIntoView, _scrollIntoView2).call(this, pageView);
        return;
      }
      const boundingRect = [pageView.viewport.convertToViewportPoint(x, y), pageView.viewport.convertToViewportPoint(x + width, y + height)];
      let left = Math.min(boundingRect[0][0], boundingRect[1][0]);
      let top = Math.min(boundingRect[0][1], boundingRect[1][1]);
      if (!allowNegativeOffset) {
        left = Math.max(left, 0);
        top = Math.max(top, 0);
      }
      _classPrivateMethodGet(this, _scrollIntoView, _scrollIntoView2).call(this, pageView, {
        left,
        top
      });
    }
    _updateLocation(firstPage) {
      const currentScale = this._currentScale;
      const currentScaleValue = this._currentScaleValue;
      const normalizedScaleValue = parseFloat(currentScaleValue) === currentScale ? Math.round(currentScale * 10000) / 100 : currentScaleValue;
      const pageNumber = firstPage.id;
      const currentPageView = this._pages[pageNumber - 1];
      const container = this.container;
      const topLeft = currentPageView.getPagePoint(container.scrollLeft - firstPage.x, container.scrollTop - firstPage.y);
      const intLeft = Math.round(topLeft[0]);
      const intTop = Math.round(topLeft[1]);
      let pdfOpenParams = `#page=${pageNumber}`;
      if (!this.isInPresentationMode) {
        pdfOpenParams += `&zoom=${normalizedScaleValue},${intLeft},${intTop}`;
      }
      this._location = {
        pageNumber,
        scale: normalizedScaleValue,
        top: intTop,
        left: intLeft,
        rotation: this._pagesRotation,
        pdfOpenParams
      };
    }
    update() {
      const visible = this._getVisiblePages();
      const visiblePages = visible.views,
        numVisiblePages = visiblePages.length;
      if (numVisiblePages === 0) {
        return;
      }
      const newCacheSize = Math.max(DEFAULT_CACHE_SIZE, 2 * numVisiblePages + 1);
      _classPrivateFieldGet(this, _buffer).resize(newCacheSize, visible.ids);
      this.renderingQueue.renderHighestPriority(visible);
      const isSimpleLayout = this._spreadMode === _ui_utils.SpreadMode.NONE && (this._scrollMode === _ui_utils.ScrollMode.PAGE || this._scrollMode === _ui_utils.ScrollMode.VERTICAL);
      const currentId = this._currentPageNumber;
      let stillFullyVisible = false;
      for (const page of visiblePages) {
        if (page.percent < 100) {
          break;
        }
        if (page.id === currentId && isSimpleLayout) {
          stillFullyVisible = true;
          break;
        }
      }
      this._setCurrentPageNumber(stillFullyVisible ? currentId : visiblePages[0].id);
      this._updateLocation(visible.first);
      this.eventBus.dispatch("updateviewarea", {
        source: this,
        location: this._location
      });
    }
    containsElement(element) {
      return this.container.contains(element);
    }
    focus() {
      this.container.focus();
    }
    get _isContainerRtl() {
      return getComputedStyle(this.container).direction === "rtl";
    }
    get isInPresentationMode() {
      return this.presentationModeState === _ui_utils.PresentationModeState.FULLSCREEN;
    }
    get isChangingPresentationMode() {
      return this.presentationModeState === _ui_utils.PresentationModeState.CHANGING;
    }
    get isHorizontalScrollbarEnabled() {
      return this.isInPresentationMode ? false : this.container.scrollWidth > this.container.clientWidth;
    }
    get isVerticalScrollbarEnabled() {
      return this.isInPresentationMode ? false : this.container.scrollHeight > this.container.clientHeight;
    }
    _getVisiblePages() {
      const views = this._scrollMode === _ui_utils.ScrollMode.PAGE ? _classPrivateFieldGet(this, _scrollModePageState).pages : this._pages,
        horizontal = this._scrollMode === _ui_utils.ScrollMode.HORIZONTAL,
        rtl = horizontal && this._isContainerRtl;
      return (0, _ui_utils.getVisibleElements)({
        scrollEl: this.container,
        views,
        sortByVisibility: true,
        horizontal,
        rtl
      });
    }
    cleanup() {
      for (const pageView of this._pages) {
        if (pageView.renderingState !== _ui_utils.RenderingStates.FINISHED) {
          pageView.reset();
        }
      }
    }
    _cancelRendering() {
      for (const pageView of this._pages) {
        pageView.cancelRendering();
      }
    }
    forceRendering(currentlyVisiblePages) {
      const visiblePages = currentlyVisiblePages || this._getVisiblePages();
      const scrollAhead = _classPrivateMethodGet(this, _getScrollAhead, _getScrollAhead2).call(this, visiblePages);
      const preRenderExtra = this._spreadMode !== _ui_utils.SpreadMode.NONE && this._scrollMode !== _ui_utils.ScrollMode.HORIZONTAL;
      const pageView = this.renderingQueue.getHighestPriority(visiblePages, this._pages, scrollAhead, preRenderExtra);
      if (pageView) {
        _classPrivateMethodGet(this, _ensurePdfPageLoaded, _ensurePdfPageLoaded2).call(this, pageView).then(() => {
          this.renderingQueue.renderView(pageView);
        });
        return true;
      }
      return false;
    }
    get hasEqualPageSizes() {
      const firstPageView = this._pages[0];
      for (let i = 1, ii = this._pages.length; i < ii; ++i) {
        const pageView = this._pages[i];
        if (pageView.width !== firstPageView.width || pageView.height !== firstPageView.height) {
          return false;
        }
      }
      return true;
    }
    getPagesOverview() {
      let initialOrientation;
      return this._pages.map(pageView => {
        const viewport = pageView.pdfPage.getViewport({
          scale: 1
        });
        const orientation = (0, _ui_utils.isPortraitOrientation)(viewport);
        if (initialOrientation === undefined) {
          initialOrientation = orientation;
        } else if (this.enablePrintAutoRotate && orientation !== initialOrientation) {
          return {
            width: viewport.height,
            height: viewport.width,
            rotation: (viewport.rotation - 90) % 360
          };
        }
        return {
          width: viewport.width,
          height: viewport.height,
          rotation: viewport.rotation
        };
      });
    }
    get optionalContentConfigPromise() {
      if (!this.pdfDocument) {
        return Promise.resolve(null);
      }
      if (!this._optionalContentConfigPromise) {
        console.error("optionalContentConfigPromise: Not initialized yet.");
        return this.pdfDocument.getOptionalContentConfig();
      }
      return this._optionalContentConfigPromise;
    }
    set optionalContentConfigPromise(promise) {
      if (!(promise instanceof Promise)) {
        throw new Error(`Invalid optionalContentConfigPromise: ${promise}`);
      }
      if (!this.pdfDocument) {
        return;
      }
      if (!this._optionalContentConfigPromise) {
        return;
      }
      this._optionalContentConfigPromise = promise;
      this.refresh(false, {
        optionalContentConfigPromise: promise
      });
      this.eventBus.dispatch("optionalcontentconfigchanged", {
        source: this,
        promise
      });
    }
    get scrollMode() {
      return this._scrollMode;
    }
    set scrollMode(mode) {
      if (this._scrollMode === mode) {
        return;
      }
      if (!(0, _ui_utils.isValidScrollMode)(mode)) {
        throw new Error(`Invalid scroll mode: ${mode}`);
      }
      if (this.pagesCount > PagesCountLimit.FORCE_SCROLL_MODE_PAGE) {
        return;
      }
      this._previousScrollMode = this._scrollMode;
      this._scrollMode = mode;
      this.eventBus.dispatch("scrollmodechanged", {
        source: this,
        mode
      });
      this._updateScrollMode(this._currentPageNumber);
    }
    _updateScrollMode() {
      let pageNumber = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      const scrollMode = this._scrollMode,
        viewer = this.viewer;
      viewer.classList.toggle("scrollHorizontal", scrollMode === _ui_utils.ScrollMode.HORIZONTAL);
      viewer.classList.toggle("scrollWrapped", scrollMode === _ui_utils.ScrollMode.WRAPPED);
      if (!this.pdfDocument || !pageNumber) {
        return;
      }
      if (scrollMode === _ui_utils.ScrollMode.PAGE) {
        _classPrivateMethodGet(this, _ensurePageViewVisible, _ensurePageViewVisible2).call(this);
      } else if (this._previousScrollMode === _ui_utils.ScrollMode.PAGE) {
        this._updateSpreadMode();
      }
      if (this._currentScaleValue && isNaN(this._currentScaleValue)) {
        _classPrivateMethodGet(this, _setScale, _setScale2).call(this, this._currentScaleValue, {
          noScroll: true
        });
      }
      this._setCurrentPageNumber(pageNumber, true);
      this.update();
    }
    get spreadMode() {
      return this._spreadMode;
    }
    set spreadMode(mode) {
      if (this._spreadMode === mode) {
        return;
      }
      if (!(0, _ui_utils.isValidSpreadMode)(mode)) {
        throw new Error(`Invalid spread mode: ${mode}`);
      }
      this._spreadMode = mode;
      this.eventBus.dispatch("spreadmodechanged", {
        source: this,
        mode
      });
      this._updateSpreadMode(this._currentPageNumber);
    }
    _updateSpreadMode() {
      let pageNumber = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
      if (!this.pdfDocument) {
        return;
      }
      const viewer = this.viewer,
        pages = this._pages;
      if (this._scrollMode === _ui_utils.ScrollMode.PAGE) {
        _classPrivateMethodGet(this, _ensurePageViewVisible, _ensurePageViewVisible2).call(this);
      } else {
        viewer.textContent = "";
        if (this._spreadMode === _ui_utils.SpreadMode.NONE) {
          for (const pageView of this._pages) {
            viewer.append(pageView.div);
          }
        } else {
          const parity = this._spreadMode - 1;
          let spread = null;
          for (let i = 0, ii = pages.length; i < ii; ++i) {
            if (spread === null) {
              spread = document.createElement("div");
              spread.className = "spread";
              viewer.append(spread);
            } else if (i % 2 === parity) {
              spread = spread.cloneNode(false);
              viewer.append(spread);
            }
            spread.append(pages[i].div);
          }
        }
      }
      if (!pageNumber) {
        return;
      }
      if (this._currentScaleValue && isNaN(this._currentScaleValue)) {
        _classPrivateMethodGet(this, _setScale, _setScale2).call(this, this._currentScaleValue, {
          noScroll: true
        });
      }
      this._setCurrentPageNumber(pageNumber, true);
      this.update();
    }
    _getPageAdvance(currentPageNumber) {
      let previous = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
      switch (this._scrollMode) {
        case _ui_utils.ScrollMode.WRAPPED:
          {
            const {
                views
              } = this._getVisiblePages(),
              pageLayout = new Map();
            for (const {
              id,
              y,
              percent,
              widthPercent
            } of views) {
              if (percent === 0 || widthPercent < 100) {
                continue;
              }
              let yArray = pageLayout.get(y);
              if (!yArray) {
                pageLayout.set(y, yArray || (yArray = []));
              }
              yArray.push(id);
            }
            for (const yArray of pageLayout.values()) {
              const currentIndex = yArray.indexOf(currentPageNumber);
              if (currentIndex === -1) {
                continue;
              }
              const numPages = yArray.length;
              if (numPages === 1) {
                break;
              }
              if (previous) {
                for (let i = currentIndex - 1, ii = 0; i >= ii; i--) {
                  const currentId = yArray[i],
                    expectedId = yArray[i + 1] - 1;
                  if (currentId < expectedId) {
                    return currentPageNumber - expectedId;
                  }
                }
              } else {
                for (let i = currentIndex + 1, ii = numPages; i < ii; i++) {
                  const currentId = yArray[i],
                    expectedId = yArray[i - 1] + 1;
                  if (currentId > expectedId) {
                    return expectedId - currentPageNumber;
                  }
                }
              }
              if (previous) {
                const firstId = yArray[0];
                if (firstId < currentPageNumber) {
                  return currentPageNumber - firstId + 1;
                }
              } else {
                const lastId = yArray[numPages - 1];
                if (lastId > currentPageNumber) {
                  return lastId - currentPageNumber + 1;
                }
              }
              break;
            }
            break;
          }
        case _ui_utils.ScrollMode.HORIZONTAL:
          {
            break;
          }
        case _ui_utils.ScrollMode.PAGE:
        case _ui_utils.ScrollMode.VERTICAL:
          {
            if (this._spreadMode === _ui_utils.SpreadMode.NONE) {
              break;
            }
            const parity = this._spreadMode - 1;
            if (previous && currentPageNumber % 2 !== parity) {
              break;
            } else if (!previous && currentPageNumber % 2 === parity) {
              break;
            }
            const {
                views
              } = this._getVisiblePages(),
              expectedId = previous ? currentPageNumber - 1 : currentPageNumber + 1;
            for (const {
              id,
              percent,
              widthPercent
            } of views) {
              if (id !== expectedId) {
                continue;
              }
              if (percent > 0 && widthPercent === 100) {
                return 2;
              }
              break;
            }
            break;
          }
      }
      return 1;
    }
    nextPage() {
      const currentPageNumber = this._currentPageNumber,
        pagesCount = this.pagesCount;
      if (currentPageNumber >= pagesCount) {
        return false;
      }
      const advance = this._getPageAdvance(currentPageNumber, false) || 1;
      this.currentPageNumber = Math.min(currentPageNumber + advance, pagesCount);
      return true;
    }
    previousPage() {
      const currentPageNumber = this._currentPageNumber;
      if (currentPageNumber <= 1) {
        return false;
      }
      const advance = this._getPageAdvance(currentPageNumber, true) || 1;
      this.currentPageNumber = Math.max(currentPageNumber - advance, 1);
      return true;
    }
    increaseScale() {
      let {
        drawingDelay,
        scaleFactor,
        steps
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (!this.pdfDocument) {
        return;
      }
      let newScale = this._currentScale;
      if (scaleFactor > 1) {
        newScale = Math.round(newScale * scaleFactor * 100) / 100;
      } else {
        var _steps;
        (_steps = steps) !== null && _steps !== void 0 ? _steps : steps = 1;
        do {
          newScale = Math.ceil((newScale * _ui_utils.DEFAULT_SCALE_DELTA).toFixed(2) * 10) / 10;
        } while (--steps > 0 && newScale < _ui_utils.MAX_SCALE);
      }
      _classPrivateMethodGet(this, _setScale, _setScale2).call(this, Math.min(_ui_utils.MAX_SCALE, newScale), {
        noScroll: false,
        drawingDelay
      });
    }
    decreaseScale() {
      let {
        drawingDelay,
        scaleFactor,
        steps
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (!this.pdfDocument) {
        return;
      }
      let newScale = this._currentScale;
      if (scaleFactor > 0 && scaleFactor < 1) {
        newScale = Math.round(newScale * scaleFactor * 100) / 100;
      } else {
        var _steps2;
        (_steps2 = steps) !== null && _steps2 !== void 0 ? _steps2 : steps = 1;
        do {
          newScale = Math.floor((newScale / _ui_utils.DEFAULT_SCALE_DELTA).toFixed(2) * 10) / 10;
        } while (--steps > 0 && newScale > _ui_utils.MIN_SCALE);
      }
      _classPrivateMethodGet(this, _setScale, _setScale2).call(this, Math.max(_ui_utils.MIN_SCALE, newScale), {
        noScroll: false,
        drawingDelay
      });
    }
    get containerTopLeft() {
      return _classPrivateFieldGet(this, _containerTopLeft) || _classPrivateFieldSet(this, _containerTopLeft, [this.container.offsetTop, this.container.offsetLeft]);
    }
    get annotationEditorMode() {
      return _classPrivateFieldGet(this, _annotationEditorUIManager) ? _classPrivateFieldGet(this, _annotationEditorMode) : _pdfjsLib.AnnotationEditorType.DISABLE;
    }
    set annotationEditorMode(_ref5) {
      let {
        mode,
        editId = null
      } = _ref5;
      if (!_classPrivateFieldGet(this, _annotationEditorUIManager)) {
        throw new Error(`The AnnotationEditor is not enabled.`);
      }
      if (_classPrivateFieldGet(this, _annotationEditorMode) === mode) {
        return;
      }
      if (!isValidAnnotationEditorMode(mode)) {
        throw new Error(`Invalid AnnotationEditor mode: ${mode}`);
      }
      if (!this.pdfDocument) {
        return;
      }
      _classPrivateFieldSet(this, _annotationEditorMode, mode);
      this.eventBus.dispatch("annotationeditormodechanged", {
        source: this,
        mode
      });
      _classPrivateFieldGet(this, _annotationEditorUIManager).updateMode(mode, editId);
    }
    set annotationEditorParams(_ref6) {
      let {
        type,
        value
      } = _ref6;
      if (!_classPrivateFieldGet(this, _annotationEditorUIManager)) {
        throw new Error(`The AnnotationEditor is not enabled.`);
      }
      _classPrivateFieldGet(this, _annotationEditorUIManager).updateParams(type, value);
    }
    refresh() {
      let noUpdate = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      let updateArgs = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : Object.create(null);
      if (!this.pdfDocument) {
        return;
      }
      for (const pageView of this._pages) {
        pageView.update(updateArgs);
      }
      if (_classPrivateFieldGet(this, _scaleTimeoutId) !== null) {
        clearTimeout(_classPrivateFieldGet(this, _scaleTimeoutId));
        _classPrivateFieldSet(this, _scaleTimeoutId, null);
      }
      if (!noUpdate) {
        this.update();
      }
    }
  }
  exports.PDFViewer = PDFViewer;
  function _layerProperties2() {
    const self = this;
    return {
      get annotationEditorUIManager() {
        return _classPrivateFieldGet(self, _annotationEditorUIManager);
      },
      get annotationStorage() {
        var _self$pdfDocument;
        return (_self$pdfDocument = self.pdfDocument) === null || _self$pdfDocument === void 0 ? void 0 : _self$pdfDocument.annotationStorage;
      },
      get downloadManager() {
        return self.downloadManager;
      },
      get enableScripting() {
        return !!self._scriptingManager;
      },
      get fieldObjectsPromise() {
        var _self$pdfDocument2;
        return (_self$pdfDocument2 = self.pdfDocument) === null || _self$pdfDocument2 === void 0 ? void 0 : _self$pdfDocument2.getFieldObjects();
      },
      get findController() {
        return self.findController;
      },
      get hasJSActionsPromise() {
        var _self$pdfDocument3;
        return (_self$pdfDocument3 = self.pdfDocument) === null || _self$pdfDocument3 === void 0 ? void 0 : _self$pdfDocument3.hasJSActions();
      },
      get linkService() {
        return self.linkService;
      }
    };
  }
  function _initializePermissions2(permissions) {
    const params = {
      annotationEditorMode: _classPrivateFieldGet(this, _annotationEditorMode),
      annotationMode: _classPrivateFieldGet(this, _annotationMode),
      textLayerMode: _classPrivateFieldGet(this, _textLayerMode)
    };
    if (!permissions) {
      return params;
    }
    if (!permissions.includes(_pdfjsLib.PermissionFlag.COPY) && _classPrivateFieldGet(this, _textLayerMode) === _ui_utils.TextLayerMode.ENABLE) {
      params.textLayerMode = _ui_utils.TextLayerMode.ENABLE_PERMISSIONS;
    }
    if (!permissions.includes(_pdfjsLib.PermissionFlag.MODIFY_CONTENTS)) {
      params.annotationEditorMode = _pdfjsLib.AnnotationEditorType.DISABLE;
    }
    if (!permissions.includes(_pdfjsLib.PermissionFlag.MODIFY_ANNOTATIONS) && !permissions.includes(_pdfjsLib.PermissionFlag.FILL_INTERACTIVE_FORMS) && _classPrivateFieldGet(this, _annotationMode) === _pdfjsLib.AnnotationMode.ENABLE_FORMS) {
      params.annotationMode = _pdfjsLib.AnnotationMode.ENABLE;
    }
    return params;
  }
  function _onePageRenderedOrForceFetch2() {
    if (document.visibilityState === "hidden" || !this.container.offsetParent || this._getVisiblePages().views.length === 0) {
      return Promise.resolve();
    }
    const visibilityChangePromise = new Promise(resolve => {
      _classPrivateFieldSet(this, _onVisibilityChange, () => {
        if (document.visibilityState !== "hidden") {
          return;
        }
        resolve();
        document.removeEventListener("visibilitychange", _classPrivateFieldGet(this, _onVisibilityChange));
        _classPrivateFieldSet(this, _onVisibilityChange, null);
      });
      document.addEventListener("visibilitychange", _classPrivateFieldGet(this, _onVisibilityChange));
    });
    return Promise.race([this._onePageRenderedCapability.promise, visibilityChangePromise]);
  }
  function _copyCallback2(textLayerMode, event) {
    const selection = document.getSelection();
    const {
      focusNode,
      anchorNode
    } = selection;
    if (anchorNode && focusNode && selection.containsNode(_classPrivateFieldGet(this, _hiddenCopyElement))) {
      if (_classPrivateFieldGet(this, _getAllTextInProgress) || textLayerMode === _ui_utils.TextLayerMode.ENABLE_PERMISSIONS) {
        event.preventDefault();
        event.stopPropagation();
        return;
      }
      _classPrivateFieldSet(this, _getAllTextInProgress, true);
      const savedCursor = this.container.style.cursor;
      this.container.style.cursor = "wait";
      const interruptCopy = ev => _classPrivateFieldSet(this, _interruptCopyCondition, ev.key === "Escape");
      window.addEventListener("keydown", interruptCopy);
      this.getAllText().then(async text => {
        if (text !== null) {
          await navigator.clipboard.writeText(text);
        }
      }).catch(reason => {
        console.warn(`Something goes wrong when extracting the text: ${reason.message}`);
      }).finally(() => {
        _classPrivateFieldSet(this, _getAllTextInProgress, false);
        _classPrivateFieldSet(this, _interruptCopyCondition, false);
        window.removeEventListener("keydown", interruptCopy);
        this.container.style.cursor = savedCursor;
      });
      event.preventDefault();
      event.stopPropagation();
    }
  }
  function _ensurePageViewVisible2() {
    if (this._scrollMode !== _ui_utils.ScrollMode.PAGE) {
      throw new Error("#ensurePageViewVisible: Invalid scrollMode value.");
    }
    const pageNumber = this._currentPageNumber,
      state = _classPrivateFieldGet(this, _scrollModePageState),
      viewer = this.viewer;
    viewer.textContent = "";
    state.pages.length = 0;
    if (this._spreadMode === _ui_utils.SpreadMode.NONE && !this.isInPresentationMode) {
      const pageView = this._pages[pageNumber - 1];
      viewer.append(pageView.div);
      state.pages.push(pageView);
    } else {
      const pageIndexSet = new Set(),
        parity = this._spreadMode - 1;
      if (parity === -1) {
        pageIndexSet.add(pageNumber - 1);
      } else if (pageNumber % 2 !== parity) {
        pageIndexSet.add(pageNumber - 1);
        pageIndexSet.add(pageNumber);
      } else {
        pageIndexSet.add(pageNumber - 2);
        pageIndexSet.add(pageNumber - 1);
      }
      const spread = document.createElement("div");
      spread.className = "spread";
      if (this.isInPresentationMode) {
        const dummyPage = document.createElement("div");
        dummyPage.className = "dummyPage";
        spread.append(dummyPage);
      }
      for (const i of pageIndexSet) {
        const pageView = this._pages[i];
        if (!pageView) {
          continue;
        }
        spread.append(pageView.div);
        state.pages.push(pageView);
      }
      viewer.append(spread);
    }
    state.scrollDown = pageNumber >= state.previousPageNumber;
    state.previousPageNumber = pageNumber;
  }
  function _scrollIntoView2(pageView) {
    let pageSpot = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    const {
      div,
      id
    } = pageView;
    if (this._currentPageNumber !== id) {
      this._setCurrentPageNumber(id);
    }
    if (this._scrollMode === _ui_utils.ScrollMode.PAGE) {
      _classPrivateMethodGet(this, _ensurePageViewVisible, _ensurePageViewVisible2).call(this);
      this.update();
    }
    if (!pageSpot && !this.isInPresentationMode) {
      const left = div.offsetLeft + div.clientLeft,
        right = left + div.clientWidth;
      const {
        scrollLeft,
        clientWidth
      } = this.container;
      if (this._scrollMode === _ui_utils.ScrollMode.HORIZONTAL || left < scrollLeft || right > scrollLeft + clientWidth) {
        pageSpot = {
          left: 0,
          top: 0
        };
      }
    }
    (0, _ui_utils.scrollIntoView)(div, pageSpot);
    if (!this._currentScaleValue && this._location) {
      this._location = null;
    }
  }
  function _isSameScale2(newScale) {
    return newScale === this._currentScale || Math.abs(newScale - this._currentScale) < 1e-15;
  }
  function _setScaleUpdatePages2(newScale, newValue, _ref7) {
    let {
      noScroll = false,
      preset = false,
      drawingDelay = -1
    } = _ref7;
    this._currentScaleValue = newValue.toString();
    if (_classPrivateMethodGet(this, _isSameScale, _isSameScale2).call(this, newScale)) {
      if (preset) {
        this.eventBus.dispatch("scalechanging", {
          source: this,
          scale: newScale,
          presetValue: newValue
        });
      }
      return;
    }
    this.viewer.style.setProperty("--scale-factor", newScale * _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS);
    const postponeDrawing = drawingDelay >= 0 && drawingDelay < 1000;
    this.refresh(true, {
      scale: newScale,
      drawingDelay: postponeDrawing ? drawingDelay : -1
    });
    if (postponeDrawing) {
      _classPrivateFieldSet(this, _scaleTimeoutId, setTimeout(() => {
        _classPrivateFieldSet(this, _scaleTimeoutId, null);
        this.refresh();
      }, drawingDelay));
    }
    this._currentScale = newScale;
    if (!noScroll) {
      let page = this._currentPageNumber,
        dest;
      if (this._location && !(this.isInPresentationMode || this.isChangingPresentationMode)) {
        page = this._location.pageNumber;
        dest = [null, {
          name: "XYZ"
        }, this._location.left, this._location.top, null];
      }
      this.scrollPageIntoView({
        pageNumber: page,
        destArray: dest,
        allowNegativeOffset: true
      });
    }
    this.eventBus.dispatch("scalechanging", {
      source: this,
      scale: newScale,
      presetValue: preset ? newValue : undefined
    });
    if (this.defaultRenderingQueue) {
      this.update();
    }
  }
  function _get_pageWidthScaleFactor() {
    if (this._spreadMode !== _ui_utils.SpreadMode.NONE && this._scrollMode !== _ui_utils.ScrollMode.HORIZONTAL) {
      return 2;
    }
    return 1;
  }
  function _setScale2(value, options) {
    let scale = parseFloat(value);
    if (scale > 0) {
      options.preset = false;
      _classPrivateMethodGet(this, _setScaleUpdatePages, _setScaleUpdatePages2).call(this, scale, value, options);
    } else {
      const currentPage = this._pages[this._currentPageNumber - 1];
      if (!currentPage) {
        return;
      }
      let hPadding = _ui_utils.SCROLLBAR_PADDING,
        vPadding = _ui_utils.VERTICAL_PADDING;
      if (this.isInPresentationMode) {
        hPadding = vPadding = 4;
        if (this._spreadMode !== _ui_utils.SpreadMode.NONE) {
          hPadding *= 2;
        }
      } else if (this.removePageBorders) {
        hPadding = vPadding = 0;
      } else if (this._scrollMode === _ui_utils.ScrollMode.HORIZONTAL) {
        [hPadding, vPadding] = [vPadding, hPadding];
      }
      const pageWidthScale = (this.container.clientWidth - hPadding) / currentPage.width * currentPage.scale / _classPrivateFieldGet(this, _pageWidthScaleFactor);
      const pageHeightScale = (this.container.clientHeight - vPadding) / currentPage.height * currentPage.scale;
      switch (value) {
        case "page-actual":
          scale = 1;
          break;
        case "page-width":
          scale = pageWidthScale;
          break;
        case "page-height":
          scale = pageHeightScale;
          break;
        case "page-fit":
          scale = Math.min(pageWidthScale, pageHeightScale);
          break;
        case "auto":
          const horizontalScale = (0, _ui_utils.isPortraitOrientation)(currentPage) ? pageWidthScale : Math.min(pageHeightScale, pageWidthScale);
          scale = Math.min(_ui_utils.MAX_AUTO_SCALE, horizontalScale);
          break;
        default:
          console.error(`#setScale: "${value}" is an unknown zoom value.`);
          return;
      }
      options.preset = true;
      _classPrivateMethodGet(this, _setScaleUpdatePages, _setScaleUpdatePages2).call(this, scale, value, options);
    }
  }
  function _resetCurrentPageView2() {
    const pageView = this._pages[this._currentPageNumber - 1];
    if (this.isInPresentationMode) {
      _classPrivateMethodGet(this, _setScale, _setScale2).call(this, this._currentScaleValue, {
        noScroll: true
      });
    }
    _classPrivateMethodGet(this, _scrollIntoView, _scrollIntoView2).call(this, pageView);
  }
  async function _ensurePdfPageLoaded2(pageView) {
    if (pageView.pdfPage) {
      return pageView.pdfPage;
    }
    try {
      var _this$linkService$_ca, _this$linkService;
      const pdfPage = await this.pdfDocument.getPage(pageView.id);
      if (!pageView.pdfPage) {
        pageView.setPdfPage(pdfPage);
      }
      if (!((_this$linkService$_ca = (_this$linkService = this.linkService)._cachedPageNumber) !== null && _this$linkService$_ca !== void 0 && _this$linkService$_ca.call(_this$linkService, pdfPage.ref))) {
        this.linkService.cachePageRef(pageView.id, pdfPage.ref);
      }
      return pdfPage;
    } catch (reason) {
      console.error("Unable to get page for page view", reason);
      return null;
    }
  }
  function _getScrollAhead2(visible) {
    var _visible$first, _visible$last;
    if (((_visible$first = visible.first) === null || _visible$first === void 0 ? void 0 : _visible$first.id) === 1) {
      return true;
    } else if (((_visible$last = visible.last) === null || _visible$last === void 0 ? void 0 : _visible$last.id) === this.pagesCount) {
      return false;
    }
    switch (this._scrollMode) {
      case _ui_utils.ScrollMode.PAGE:
        return _classPrivateFieldGet(this, _scrollModePageState).scrollDown;
      case _ui_utils.ScrollMode.HORIZONTAL:
        return this.scroll.right;
    }
    return this.scroll.down;
  }
  function _updateContainerHeightCss2() {
    let height = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : this.container.clientHeight;
    if (height !== _classPrivateFieldGet(this, _previousContainerHeight)) {
      _classPrivateFieldSet(this, _previousContainerHeight, height);
      _ui_utils.docStyle.setProperty("--viewer-container-height", `${height}px`);
    }
  }
  function _resizeObserverCallback2(entries) {
    for (const entry of entries) {
      if (entry.target === this.container) {
        _classPrivateMethodGet(this, _updateContainerHeightCss, _updateContainerHeightCss2).call(this, Math.floor(entry.borderBoxSize[0].blockSize));
        _classPrivateFieldSet(this, _containerTopLeft, null);
        break;
      }
    }
  }
  
  /***/ }),
  /* 211 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports["default"] = void 0;
  __webpack_require__(142);
  __webpack_require__(212);
  __webpack_require__(122);
  var MapShim = function () {
    if (typeof Map !== 'undefined') {
      return Map;
    }
    function getIndex(arr, key) {
      var result = -1;
      arr.some(function (entry, index) {
        if (entry[0] === key) {
          result = index;
          return true;
        }
        return false;
      });
      return result;
    }
    return function () {
      function class_1() {
        this.__entries__ = [];
      }
      Object.defineProperty(class_1.prototype, "size", {
        get: function () {
          return this.__entries__.length;
        },
        enumerable: true,
        configurable: true
      });
      class_1.prototype.get = function (key) {
        var index = getIndex(this.__entries__, key);
        var entry = this.__entries__[index];
        return entry && entry[1];
      };
      class_1.prototype.set = function (key, value) {
        var index = getIndex(this.__entries__, key);
        if (~index) {
          this.__entries__[index][1] = value;
        } else {
          this.__entries__.push([key, value]);
        }
      };
      class_1.prototype.delete = function (key) {
        var entries = this.__entries__;
        var index = getIndex(entries, key);
        if (~index) {
          entries.splice(index, 1);
        }
      };
      class_1.prototype.has = function (key) {
        return !!~getIndex(this.__entries__, key);
      };
      class_1.prototype.clear = function () {
        this.__entries__.splice(0);
      };
      class_1.prototype.forEach = function (callback, ctx) {
        if (ctx === void 0) {
          ctx = null;
        }
        for (var _i = 0, _a = this.__entries__; _i < _a.length; _i++) {
          var entry = _a[_i];
          callback.call(ctx, entry[1], entry[0]);
        }
      };
      return class_1;
    }();
  }();
  var isBrowser = typeof window !== 'undefined' && typeof document !== 'undefined' && window.document === document;
  var global$1 = function () {
    if (typeof global !== 'undefined' && global.Math === Math) {
      return global;
    }
    if (typeof self !== 'undefined' && self.Math === Math) {
      return self;
    }
    if (typeof window !== 'undefined' && window.Math === Math) {
      return window;
    }
    return Function('return this')();
  }();
  var requestAnimationFrame$1 = function () {
    if (typeof requestAnimationFrame === 'function') {
      return requestAnimationFrame.bind(global$1);
    }
    return function (callback) {
      return setTimeout(function () {
        return callback(Date.now());
      }, 1000 / 60);
    };
  }();
  var trailingTimeout = 2;
  function throttle(callback, delay) {
    var leadingCall = false,
      trailingCall = false,
      lastCallTime = 0;
    function resolvePending() {
      if (leadingCall) {
        leadingCall = false;
        callback();
      }
      if (trailingCall) {
        proxy();
      }
    }
    function timeoutCallback() {
      requestAnimationFrame$1(resolvePending);
    }
    function proxy() {
      var timeStamp = Date.now();
      if (leadingCall) {
        if (timeStamp - lastCallTime < trailingTimeout) {
          return;
        }
        trailingCall = true;
      } else {
        leadingCall = true;
        trailingCall = false;
        setTimeout(timeoutCallback, delay);
      }
      lastCallTime = timeStamp;
    }
    return proxy;
  }
  var REFRESH_DELAY = 20;
  var transitionKeys = ['top', 'right', 'bottom', 'left', 'width', 'height', 'size', 'weight'];
  var mutationObserverSupported = typeof MutationObserver !== 'undefined';
  var ResizeObserverController = function () {
    function ResizeObserverController() {
      this.connected_ = false;
      this.mutationEventsAdded_ = false;
      this.mutationsObserver_ = null;
      this.observers_ = [];
      this.onTransitionEnd_ = this.onTransitionEnd_.bind(this);
      this.refresh = throttle(this.refresh.bind(this), REFRESH_DELAY);
    }
    ResizeObserverController.prototype.addObserver = function (observer) {
      if (!~this.observers_.indexOf(observer)) {
        this.observers_.push(observer);
      }
      if (!this.connected_) {
        this.connect_();
      }
    };
    ResizeObserverController.prototype.removeObserver = function (observer) {
      var observers = this.observers_;
      var index = observers.indexOf(observer);
      if (~index) {
        observers.splice(index, 1);
      }
      if (!observers.length && this.connected_) {
        this.disconnect_();
      }
    };
    ResizeObserverController.prototype.refresh = function () {
      var changesDetected = this.updateObservers_();
      if (changesDetected) {
        this.refresh();
      }
    };
    ResizeObserverController.prototype.updateObservers_ = function () {
      var activeObservers = this.observers_.filter(function (observer) {
        return observer.gatherActive(), observer.hasActive();
      });
      activeObservers.forEach(function (observer) {
        return observer.broadcastActive();
      });
      return activeObservers.length > 0;
    };
    ResizeObserverController.prototype.connect_ = function () {
      if (!isBrowser || this.connected_) {
        return;
      }
      document.addEventListener('transitionend', this.onTransitionEnd_);
      window.addEventListener('resize', this.refresh);
      if (mutationObserverSupported) {
        this.mutationsObserver_ = new MutationObserver(this.refresh);
        this.mutationsObserver_.observe(document, {
          attributes: true,
          childList: true,
          characterData: true,
          subtree: true
        });
      } else {
        document.addEventListener('DOMSubtreeModified', this.refresh);
        this.mutationEventsAdded_ = true;
      }
      this.connected_ = true;
    };
    ResizeObserverController.prototype.disconnect_ = function () {
      if (!isBrowser || !this.connected_) {
        return;
      }
      document.removeEventListener('transitionend', this.onTransitionEnd_);
      window.removeEventListener('resize', this.refresh);
      if (this.mutationsObserver_) {
        this.mutationsObserver_.disconnect();
      }
      if (this.mutationEventsAdded_) {
        document.removeEventListener('DOMSubtreeModified', this.refresh);
      }
      this.mutationsObserver_ = null;
      this.mutationEventsAdded_ = false;
      this.connected_ = false;
    };
    ResizeObserverController.prototype.onTransitionEnd_ = function (_a) {
      var _b = _a.propertyName,
        propertyName = _b === void 0 ? '' : _b;
      var isReflowProperty = transitionKeys.some(function (key) {
        return !!~propertyName.indexOf(key);
      });
      if (isReflowProperty) {
        this.refresh();
      }
    };
    ResizeObserverController.getInstance = function () {
      if (!this.instance_) {
        this.instance_ = new ResizeObserverController();
      }
      return this.instance_;
    };
    ResizeObserverController.instance_ = null;
    return ResizeObserverController;
  }();
  var defineConfigurable = function (target, props) {
    for (var _i = 0, _a = Object.keys(props); _i < _a.length; _i++) {
      var key = _a[_i];
      Object.defineProperty(target, key, {
        value: props[key],
        enumerable: false,
        writable: false,
        configurable: true
      });
    }
    return target;
  };
  var getWindowOf = function (target) {
    var ownerGlobal = target && target.ownerDocument && target.ownerDocument.defaultView;
    return ownerGlobal || global$1;
  };
  var emptyRect = createRectInit(0, 0, 0, 0);
  function toFloat(value) {
    return parseFloat(value) || 0;
  }
  function getBordersSize(styles) {
    var positions = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      positions[_i - 1] = arguments[_i];
    }
    return positions.reduce(function (size, position) {
      var value = styles['border-' + position + '-width'];
      return size + toFloat(value);
    }, 0);
  }
  function getPaddings(styles) {
    var positions = ['top', 'right', 'bottom', 'left'];
    var paddings = {};
    for (var _i = 0, positions_1 = positions; _i < positions_1.length; _i++) {
      var position = positions_1[_i];
      var value = styles['padding-' + position];
      paddings[position] = toFloat(value);
    }
    return paddings;
  }
  function getSVGContentRect(target) {
    var bbox = target.getBBox();
    return createRectInit(0, 0, bbox.width, bbox.height);
  }
  function getHTMLElementContentRect(target) {
    var clientWidth = target.clientWidth,
      clientHeight = target.clientHeight;
    if (!clientWidth && !clientHeight) {
      return emptyRect;
    }
    var styles = getWindowOf(target).getComputedStyle(target);
    var paddings = getPaddings(styles);
    var horizPad = paddings.left + paddings.right;
    var vertPad = paddings.top + paddings.bottom;
    var width = toFloat(styles.width),
      height = toFloat(styles.height);
    if (styles.boxSizing === 'border-box') {
      if (Math.round(width + horizPad) !== clientWidth) {
        width -= getBordersSize(styles, 'left', 'right') + horizPad;
      }
      if (Math.round(height + vertPad) !== clientHeight) {
        height -= getBordersSize(styles, 'top', 'bottom') + vertPad;
      }
    }
    if (!isDocumentElement(target)) {
      var vertScrollbar = Math.round(width + horizPad) - clientWidth;
      var horizScrollbar = Math.round(height + vertPad) - clientHeight;
      if (Math.abs(vertScrollbar) !== 1) {
        width -= vertScrollbar;
      }
      if (Math.abs(horizScrollbar) !== 1) {
        height -= horizScrollbar;
      }
    }
    return createRectInit(paddings.left, paddings.top, width, height);
  }
  var isSVGGraphicsElement = function () {
    if (typeof SVGGraphicsElement !== 'undefined') {
      return function (target) {
        return target instanceof getWindowOf(target).SVGGraphicsElement;
      };
    }
    return function (target) {
      return target instanceof getWindowOf(target).SVGElement && typeof target.getBBox === 'function';
    };
  }();
  function isDocumentElement(target) {
    return target === getWindowOf(target).document.documentElement;
  }
  function getContentRect(target) {
    if (!isBrowser) {
      return emptyRect;
    }
    if (isSVGGraphicsElement(target)) {
      return getSVGContentRect(target);
    }
    return getHTMLElementContentRect(target);
  }
  function createReadOnlyRect(_a) {
    var x = _a.x,
      y = _a.y,
      width = _a.width,
      height = _a.height;
    var Constr = typeof DOMRectReadOnly !== 'undefined' ? DOMRectReadOnly : Object;
    var rect = Object.create(Constr.prototype);
    defineConfigurable(rect, {
      x: x,
      y: y,
      width: width,
      height: height,
      top: y,
      right: x + width,
      bottom: height + y,
      left: x
    });
    return rect;
  }
  function createRectInit(x, y, width, height) {
    return {
      x: x,
      y: y,
      width: width,
      height: height
    };
  }
  var ResizeObservation = function () {
    function ResizeObservation(target) {
      this.broadcastWidth = 0;
      this.broadcastHeight = 0;
      this.contentRect_ = createRectInit(0, 0, 0, 0);
      this.target = target;
    }
    ResizeObservation.prototype.isActive = function () {
      var rect = getContentRect(this.target);
      this.contentRect_ = rect;
      return rect.width !== this.broadcastWidth || rect.height !== this.broadcastHeight;
    };
    ResizeObservation.prototype.broadcastRect = function () {
      var rect = this.contentRect_;
      this.broadcastWidth = rect.width;
      this.broadcastHeight = rect.height;
      return rect;
    };
    return ResizeObservation;
  }();
  var ResizeObserverEntry = function () {
    function ResizeObserverEntry(target, rectInit) {
      var contentRect = createReadOnlyRect(rectInit);
      defineConfigurable(this, {
        target: target,
        contentRect: contentRect
      });
    }
    return ResizeObserverEntry;
  }();
  var ResizeObserverSPI = function () {
    function ResizeObserverSPI(callback, controller, callbackCtx) {
      this.activeObservations_ = [];
      this.observations_ = new MapShim();
      if (typeof callback !== 'function') {
        throw new TypeError('The callback provided as parameter 1 is not a function.');
      }
      this.callback_ = callback;
      this.controller_ = controller;
      this.callbackCtx_ = callbackCtx;
    }
    ResizeObserverSPI.prototype.observe = function (target) {
      if (!arguments.length) {
        throw new TypeError('1 argument required, but only 0 present.');
      }
      if (typeof Element === 'undefined' || !(Element instanceof Object)) {
        return;
      }
      if (!(target instanceof getWindowOf(target).Element)) {
        throw new TypeError('parameter 1 is not of type "Element".');
      }
      var observations = this.observations_;
      if (observations.has(target)) {
        return;
      }
      observations.set(target, new ResizeObservation(target));
      this.controller_.addObserver(this);
      this.controller_.refresh();
    };
    ResizeObserverSPI.prototype.unobserve = function (target) {
      if (!arguments.length) {
        throw new TypeError('1 argument required, but only 0 present.');
      }
      if (typeof Element === 'undefined' || !(Element instanceof Object)) {
        return;
      }
      if (!(target instanceof getWindowOf(target).Element)) {
        throw new TypeError('parameter 1 is not of type "Element".');
      }
      var observations = this.observations_;
      if (!observations.has(target)) {
        return;
      }
      observations.delete(target);
      if (!observations.size) {
        this.controller_.removeObserver(this);
      }
    };
    ResizeObserverSPI.prototype.disconnect = function () {
      this.clearActive();
      this.observations_.clear();
      this.controller_.removeObserver(this);
    };
    ResizeObserverSPI.prototype.gatherActive = function () {
      var _this = this;
      this.clearActive();
      this.observations_.forEach(function (observation) {
        if (observation.isActive()) {
          _this.activeObservations_.push(observation);
        }
      });
    };
    ResizeObserverSPI.prototype.broadcastActive = function () {
      if (!this.hasActive()) {
        return;
      }
      var ctx = this.callbackCtx_;
      var entries = this.activeObservations_.map(function (observation) {
        return new ResizeObserverEntry(observation.target, observation.broadcastRect());
      });
      this.callback_.call(ctx, entries, ctx);
      this.clearActive();
    };
    ResizeObserverSPI.prototype.clearActive = function () {
      this.activeObservations_.splice(0);
    };
    ResizeObserverSPI.prototype.hasActive = function () {
      return this.activeObservations_.length > 0;
    };
    return ResizeObserverSPI;
  }();
  var observers = typeof WeakMap !== 'undefined' ? new WeakMap() : new MapShim();
  var ResizeObserver = function () {
    function ResizeObserver(callback) {
      if (!(this instanceof ResizeObserver)) {
        throw new TypeError('Cannot call a class as a function.');
      }
      if (!arguments.length) {
        throw new TypeError('1 argument required, but only 0 present.');
      }
      var controller = ResizeObserverController.getInstance();
      var observer = new ResizeObserverSPI(callback, controller, this);
      observers.set(this, observer);
    }
    return ResizeObserver;
  }();
  ['observe', 'unobserve', 'disconnect'].forEach(function (method) {
    ResizeObserver.prototype[method] = function () {
      var _a;
      return (_a = observers.get(this))[method].apply(_a, arguments);
    };
  });
  var index = function () {
    if (typeof global$1.ResizeObserver !== 'undefined') {
      return global$1.ResizeObserver;
    }
    return ResizeObserver;
  }();
  var _default = index;
  exports["default"] = _default;
  
  /***/ }),
  /* 212 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  var $ = __webpack_require__(4);
  var global = __webpack_require__(5);
  var defineBuiltInAccessor = __webpack_require__(76);
  var DESCRIPTORS = __webpack_require__(7);
  var $TypeError = TypeError;
  var defineProperty = Object.defineProperty;
  var INCORRECT_VALUE = global.self !== global;
  try {
   if (DESCRIPTORS) {
    var descriptor = Object.getOwnPropertyDescriptor(global, 'self');
    if (INCORRECT_VALUE || !descriptor || !descriptor.get || !descriptor.enumerable) {
     defineBuiltInAccessor(global, 'self', {
      get: function self() {
       return global;
      },
      set: function self(value) {
       if (this !== global)
        throw $TypeError('Illegal invocation');
       defineProperty(global, 'self', {
        value: value,
        writable: true,
        configurable: true,
        enumerable: true
       });
      },
      configurable: true,
      enumerable: true
     });
    }
   } else
    $({
     global: true,
     simple: true,
     forced: INCORRECT_VALUE
    }, { self: global });
  } catch (error) {
  }
  
  /***/ }),
  /* 213 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.NullL10n = void 0;
  exports.getL10nFallback = getL10nFallback;
  __webpack_require__(136);
  __webpack_require__(149);
  __webpack_require__(155);
  __webpack_require__(2);
  const DEFAULT_L10N_STRINGS = {
    of_pages: "of {{pagesCount}}",
    page_of_pages: "({{pageNumber}} of {{pagesCount}})",
    document_properties_kb: "{{size_kb}} KB ({{size_b}} bytes)",
    document_properties_mb: "{{size_mb}} MB ({{size_b}} bytes)",
    document_properties_date_string: "{{date}}, {{time}}",
    document_properties_page_size_unit_inches: "in",
    document_properties_page_size_unit_millimeters: "mm",
    document_properties_page_size_orientation_portrait: "portrait",
    document_properties_page_size_orientation_landscape: "landscape",
    document_properties_page_size_name_a3: "A3",
    document_properties_page_size_name_a4: "A4",
    document_properties_page_size_name_letter: "Letter",
    document_properties_page_size_name_legal: "Legal",
    document_properties_page_size_dimension_string: "{{width}} × {{height}} {{unit}} ({{orientation}})",
    document_properties_page_size_dimension_name_string: "{{width}} × {{height}} {{unit}} ({{name}}, {{orientation}})",
    document_properties_linearized_yes: "Yes",
    document_properties_linearized_no: "No",
    additional_layers: "Additional Layers",
    page_landmark: "Page {{page}}",
    thumb_page_title: "Page {{page}}",
    thumb_page_canvas: "Thumbnail of Page {{page}}",
    find_reached_top: "Reached top of document, continued from bottom",
    find_reached_bottom: "Reached end of document, continued from top",
    "find_match_count[one]": "{{current}} of {{total}} match",
    "find_match_count[other]": "{{current}} of {{total}} matches",
    "find_match_count_limit[one]": "More than {{limit}} match",
    "find_match_count_limit[other]": "More than {{limit}} matches",
    find_not_found: "Phrase not found",
    page_scale_width: "Page Width",
    page_scale_fit: "Page Fit",
    page_scale_auto: "Automatic Zoom",
    page_scale_actual: "Actual Size",
    page_scale_percent: "{{scale}}%",
    loading_error: "An error occurred while loading the PDF.",
    invalid_file_error: "Invalid or corrupted PDF file.",
    missing_file_error: "Missing PDF file.",
    unexpected_response_error: "Unexpected server response.",
    rendering_error: "An error occurred while rendering the page.",
    annotation_date_string: "{{date}}, {{time}}",
    printing_not_supported: "Warning: Printing is not fully supported by this browser.",
    printing_not_ready: "Warning: The PDF is not fully loaded for printing.",
    web_fonts_disabled: "Web fonts are disabled: unable to use embedded PDF fonts.",
    free_text2_default_content: "Start typing…",
    editor_free_text2_aria_label: "Text Editor",
    editor_ink2_aria_label: "Draw Editor",
    editor_ink_canvas_aria_label: "User-created image",
    editor_alt_text_button_label: "Alt text",
    editor_alt_text_edit_button_label: "Edit alt text",
    editor_alt_text_decorative_tooltip: "Marked as decorative"
  };
  {
    DEFAULT_L10N_STRINGS.print_progress_percent = "{{progress}}%";
  }
  function getL10nFallback(key, args) {
    switch (key) {
      case "find_match_count":
        key = `find_match_count[${args.total === 1 ? "one" : "other"}]`;
        break;
      case "find_match_count_limit":
        key = `find_match_count_limit[${args.limit === 1 ? "one" : "other"}]`;
        break;
    }
    return DEFAULT_L10N_STRINGS[key] || "";
  }
  function formatL10nValue(text, args) {
    if (!args) {
      return text;
    }
    return text.replaceAll(/\{\{\s*(\w+)\s*\}\}/g, (all, name) => {
      return name in args ? args[name] : "{{" + name + "}}";
    });
  }
  const NullL10n = {
    async getLanguage() {
      return "en-us";
    },
    async getDirection() {
      return "ltr";
    },
    async get(key) {
      let args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      let fallback = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : getL10nFallback(key, args);
      return formatL10nValue(fallback, args);
    },
    async translate(element) {}
  };
  exports.NullL10n = NullL10n;
  
  /***/ }),
  /* 214 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFPageView = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  __webpack_require__(142);
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  var _annotation_editor_layer_builder = __webpack_require__(215);
  var _annotation_layer_builder = __webpack_require__(216);
  var _app_options = __webpack_require__(183);
  var _l10n_utils = __webpack_require__(213);
  var _pdf_link_service = __webpack_require__(185);
  var _struct_tree_layer_builder = __webpack_require__(217);
  var _text_accessibility = __webpack_require__(218);
  var _text_highlighter = __webpack_require__(219);
  var _text_layer_builder = __webpack_require__(220);
  var _xfa_layer_builder = __webpack_require__(221);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  const MAX_CANVAS_PIXELS = _app_options.compatibilityParams.maxCanvasPixels || 16777216;
  const DEFAULT_LAYER_PROPERTIES = () => {
    return null;
  };
  var _annotationMode = /*#__PURE__*/new WeakMap();
  var _hasRestrictedScaling = /*#__PURE__*/new WeakMap();
  var _layerProperties = /*#__PURE__*/new WeakMap();
  var _loadingId = /*#__PURE__*/new WeakMap();
  var _previousRotation = /*#__PURE__*/new WeakMap();
  var _renderError = /*#__PURE__*/new WeakMap();
  var _renderingState = /*#__PURE__*/new WeakMap();
  var _textLayerMode = /*#__PURE__*/new WeakMap();
  var _useThumbnailCanvas = /*#__PURE__*/new WeakMap();
  var _viewportMap = /*#__PURE__*/new WeakMap();
  var _setDimensions = /*#__PURE__*/new WeakSet();
  var _renderAnnotationLayer = /*#__PURE__*/new WeakSet();
  var _renderAnnotationEditorLayer = /*#__PURE__*/new WeakSet();
  var _renderXfaLayer = /*#__PURE__*/new WeakSet();
  var _renderTextLayer = /*#__PURE__*/new WeakSet();
  var _renderStructTreeLayer = /*#__PURE__*/new WeakSet();
  var _buildXfaTextContentItems = /*#__PURE__*/new WeakSet();
  var _finishRenderTask = /*#__PURE__*/new WeakSet();
  class PDFPageView {
    constructor(options) {
      var _options$textLayerMod, _options$annotationMo, _options$isOffscreenC, _options$maxCanvasPix, _this$renderingQueue;
      _classPrivateMethodInitSpec(this, _finishRenderTask);
      _classPrivateMethodInitSpec(this, _buildXfaTextContentItems);
      _classPrivateMethodInitSpec(this, _renderStructTreeLayer);
      _classPrivateMethodInitSpec(this, _renderTextLayer);
      _classPrivateMethodInitSpec(this, _renderXfaLayer);
      _classPrivateMethodInitSpec(this, _renderAnnotationEditorLayer);
      _classPrivateMethodInitSpec(this, _renderAnnotationLayer);
      _classPrivateMethodInitSpec(this, _setDimensions);
      _classPrivateFieldInitSpec(this, _annotationMode, {
        writable: true,
        value: _pdfjsLib.AnnotationMode.ENABLE_FORMS
      });
      _classPrivateFieldInitSpec(this, _hasRestrictedScaling, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _layerProperties, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _loadingId, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _previousRotation, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _renderError, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _renderingState, {
        writable: true,
        value: _ui_utils.RenderingStates.INITIAL
      });
      _classPrivateFieldInitSpec(this, _textLayerMode, {
        writable: true,
        value: _ui_utils.TextLayerMode.ENABLE
      });
      _classPrivateFieldInitSpec(this, _useThumbnailCanvas, {
        writable: true,
        value: {
          directDrawing: true,
          initialOptionalContent: true,
          regularAnnotations: true
        }
      });
      _classPrivateFieldInitSpec(this, _viewportMap, {
        writable: true,
        value: new WeakMap()
      });
      const container = options.container;
      const defaultViewport = options.defaultViewport;
      this.id = options.id;
      this.renderingId = "page" + this.id;
      _classPrivateFieldSet(this, _layerProperties, options.layerProperties || DEFAULT_LAYER_PROPERTIES);
      this.pdfPage = null;
      this.pageLabel = null;
      this.rotation = 0;
      this.scale = options.scale || _ui_utils.DEFAULT_SCALE;
      this.viewport = defaultViewport;
      this.pdfPageRotate = defaultViewport.rotation;
      this._optionalContentConfigPromise = options.optionalContentConfigPromise || null;
      _classPrivateFieldSet(this, _textLayerMode, (_options$textLayerMod = options.textLayerMode) !== null && _options$textLayerMod !== void 0 ? _options$textLayerMod : _ui_utils.TextLayerMode.ENABLE);
      _classPrivateFieldSet(this, _annotationMode, (_options$annotationMo = options.annotationMode) !== null && _options$annotationMo !== void 0 ? _options$annotationMo : _pdfjsLib.AnnotationMode.ENABLE_FORMS);
      this.imageResourcesPath = options.imageResourcesPath || "";
      this.isOffscreenCanvasSupported = (_options$isOffscreenC = options.isOffscreenCanvasSupported) !== null && _options$isOffscreenC !== void 0 ? _options$isOffscreenC : true;
      this.maxCanvasPixels = (_options$maxCanvasPix = options.maxCanvasPixels) !== null && _options$maxCanvasPix !== void 0 ? _options$maxCanvasPix : MAX_CANVAS_PIXELS;
      this.pageColors = options.pageColors || null;
      this.eventBus = options.eventBus;
      this.renderingQueue = options.renderingQueue;
      this.l10n = options.l10n || _l10n_utils.NullL10n;
      this.renderTask = null;
      this.resume = null;
      this._isStandalone = !((_this$renderingQueue = this.renderingQueue) !== null && _this$renderingQueue !== void 0 && _this$renderingQueue.hasViewer());
      this._container = container;
      if (options.useOnlyCssZoom) {
        console.error("useOnlyCssZoom was removed, please use `maxCanvasPixels = 0` instead.");
        this.maxCanvasPixels = 0;
      }
      this._annotationCanvasMap = null;
      this.annotationLayer = null;
      this.annotationEditorLayer = null;
      this.textLayer = null;
      this.zoomLayer = null;
      this.xfaLayer = null;
      this.structTreeLayer = null;
      const div = document.createElement("div");
      div.className = "page";
      div.setAttribute("data-page-number", this.id);
      div.setAttribute("role", "region");
      this.l10n.get("page_landmark", {
        page: this.id
      }).then(msg => {
        div.setAttribute("aria-label", msg);
      });
      this.div = div;
      _classPrivateMethodGet(this, _setDimensions, _setDimensions2).call(this);
      container === null || container === void 0 || container.append(div);
      if (this._isStandalone) {
        container === null || container === void 0 || container.style.setProperty("--scale-factor", this.scale * _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS);
        const {
          optionalContentConfigPromise
        } = options;
        if (optionalContentConfigPromise) {
          optionalContentConfigPromise.then(optionalContentConfig => {
            if (optionalContentConfigPromise !== this._optionalContentConfigPromise) {
              return;
            }
            _classPrivateFieldGet(this, _useThumbnailCanvas).initialOptionalContent = optionalContentConfig.hasInitialVisibility;
          });
        }
      }
    }
    get renderingState() {
      return _classPrivateFieldGet(this, _renderingState);
    }
    set renderingState(state) {
      if (state === _classPrivateFieldGet(this, _renderingState)) {
        return;
      }
      _classPrivateFieldSet(this, _renderingState, state);
      if (_classPrivateFieldGet(this, _loadingId)) {
        clearTimeout(_classPrivateFieldGet(this, _loadingId));
        _classPrivateFieldSet(this, _loadingId, null);
      }
      switch (state) {
        case _ui_utils.RenderingStates.PAUSED:
          this.div.classList.remove("loading");
          break;
        case _ui_utils.RenderingStates.RUNNING:
          this.div.classList.add("loadingIcon");
          _classPrivateFieldSet(this, _loadingId, setTimeout(() => {
            this.div.classList.add("loading");
            _classPrivateFieldSet(this, _loadingId, null);
          }, 0));
          break;
        case _ui_utils.RenderingStates.INITIAL:
        case _ui_utils.RenderingStates.FINISHED:
          this.div.classList.remove("loadingIcon", "loading");
          break;
      }
    }
    setPdfPage(pdfPage) {
      var _this$pageColors, _this$pageColors2;
      if (this._isStandalone && (((_this$pageColors = this.pageColors) === null || _this$pageColors === void 0 ? void 0 : _this$pageColors.foreground) === "CanvasText" || ((_this$pageColors2 = this.pageColors) === null || _this$pageColors2 === void 0 ? void 0 : _this$pageColors2.background) === "Canvas")) {
        var _this$_container;
        (_this$_container = this._container) === null || _this$_container === void 0 || _this$_container.style.setProperty("--hcm-highligh-filter", pdfPage.filterFactory.addHighlightHCMFilter("CanvasText", "Canvas", "HighlightText", "Highlight"));
      }
      this.pdfPage = pdfPage;
      this.pdfPageRotate = pdfPage.rotate;
      const totalRotation = (this.rotation + this.pdfPageRotate) % 360;
      this.viewport = pdfPage.getViewport({
        scale: this.scale * _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS,
        rotation: totalRotation
      });
      _classPrivateMethodGet(this, _setDimensions, _setDimensions2).call(this);
      this.reset();
    }
    destroy() {
      var _this$pdfPage;
      this.reset();
      (_this$pdfPage = this.pdfPage) === null || _this$pdfPage === void 0 || _this$pdfPage.cleanup();
    }
    get _textHighlighter() {
      return (0, _pdfjsLib.shadow)(this, "_textHighlighter", new _text_highlighter.TextHighlighter({
        pageIndex: this.id - 1,
        eventBus: this.eventBus,
        findController: _classPrivateFieldGet(this, _layerProperties).call(this).findController
      }));
    }
    _resetZoomLayer() {
      let removeFromDOM = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      if (!this.zoomLayer) {
        return;
      }
      const zoomLayerCanvas = this.zoomLayer.firstChild;
      _classPrivateFieldGet(this, _viewportMap).delete(zoomLayerCanvas);
      zoomLayerCanvas.width = 0;
      zoomLayerCanvas.height = 0;
      if (removeFromDOM) {
        this.zoomLayer.remove();
      }
      this.zoomLayer = null;
    }
    reset() {
      var _this$annotationLayer, _this$annotationEdito, _this$xfaLayer, _this$textLayer, _this$structTreeLayer;
      let {
        keepZoomLayer = false,
        keepAnnotationLayer = false,
        keepAnnotationEditorLayer = false,
        keepXfaLayer = false,
        keepTextLayer = false
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      this.cancelRendering({
        keepAnnotationLayer,
        keepAnnotationEditorLayer,
        keepXfaLayer,
        keepTextLayer
      });
      this.renderingState = _ui_utils.RenderingStates.INITIAL;
      const div = this.div;
      const childNodes = div.childNodes,
        zoomLayerNode = keepZoomLayer && this.zoomLayer || null,
        annotationLayerNode = keepAnnotationLayer && ((_this$annotationLayer = this.annotationLayer) === null || _this$annotationLayer === void 0 ? void 0 : _this$annotationLayer.div) || null,
        annotationEditorLayerNode = keepAnnotationEditorLayer && ((_this$annotationEdito = this.annotationEditorLayer) === null || _this$annotationEdito === void 0 ? void 0 : _this$annotationEdito.div) || null,
        xfaLayerNode = keepXfaLayer && ((_this$xfaLayer = this.xfaLayer) === null || _this$xfaLayer === void 0 ? void 0 : _this$xfaLayer.div) || null,
        textLayerNode = keepTextLayer && ((_this$textLayer = this.textLayer) === null || _this$textLayer === void 0 ? void 0 : _this$textLayer.div) || null;
      for (let i = childNodes.length - 1; i >= 0; i--) {
        const node = childNodes[i];
        switch (node) {
          case zoomLayerNode:
          case annotationLayerNode:
          case annotationEditorLayerNode:
          case xfaLayerNode:
          case textLayerNode:
            continue;
        }
        node.remove();
      }
      div.removeAttribute("data-loaded");
      if (annotationLayerNode) {
        this.annotationLayer.hide();
      }
      if (annotationEditorLayerNode) {
        this.annotationEditorLayer.hide();
      }
      if (xfaLayerNode) {
        this.xfaLayer.hide();
      }
      if (textLayerNode) {
        this.textLayer.hide();
      }
      (_this$structTreeLayer = this.structTreeLayer) === null || _this$structTreeLayer === void 0 || _this$structTreeLayer.hide();
      if (!zoomLayerNode) {
        if (this.canvas) {
          _classPrivateFieldGet(this, _viewportMap).delete(this.canvas);
          this.canvas.width = 0;
          this.canvas.height = 0;
          delete this.canvas;
        }
        this._resetZoomLayer();
      }
    }
    update(_ref) {
      let {
        scale = 0,
        rotation = null,
        optionalContentConfigPromise = null,
        drawingDelay = -1
      } = _ref;
      this.scale = scale || this.scale;
      if (typeof rotation === "number") {
        this.rotation = rotation;
      }
      if (optionalContentConfigPromise instanceof Promise) {
        this._optionalContentConfigPromise = optionalContentConfigPromise;
        optionalContentConfigPromise.then(optionalContentConfig => {
          if (optionalContentConfigPromise !== this._optionalContentConfigPromise) {
            return;
          }
          _classPrivateFieldGet(this, _useThumbnailCanvas).initialOptionalContent = optionalContentConfig.hasInitialVisibility;
        });
      }
      _classPrivateFieldGet(this, _useThumbnailCanvas).directDrawing = true;
      const totalRotation = (this.rotation + this.pdfPageRotate) % 360;
      this.viewport = this.viewport.clone({
        scale: this.scale * _pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS,
        rotation: totalRotation
      });
      _classPrivateMethodGet(this, _setDimensions, _setDimensions2).call(this);
      if (this._isStandalone) {
        var _this$_container2;
        (_this$_container2 = this._container) === null || _this$_container2 === void 0 || _this$_container2.style.setProperty("--scale-factor", this.viewport.scale);
      }
      if (this.canvas) {
        let onlyCssZoom = false;
        if (_classPrivateFieldGet(this, _hasRestrictedScaling)) {
          if (this.maxCanvasPixels === 0) {
            onlyCssZoom = true;
          } else if (this.maxCanvasPixels > 0) {
            const {
              width,
              height
            } = this.viewport;
            const {
              sx,
              sy
            } = this.outputScale;
            onlyCssZoom = (Math.floor(width) * sx | 0) * (Math.floor(height) * sy | 0) > this.maxCanvasPixels;
          }
        }
        const postponeDrawing = !onlyCssZoom && drawingDelay >= 0 && drawingDelay < 1000;
        if (postponeDrawing || onlyCssZoom) {
          if (postponeDrawing && this.renderingState !== _ui_utils.RenderingStates.FINISHED) {
            this.cancelRendering({
              keepZoomLayer: true,
              keepAnnotationLayer: true,
              keepAnnotationEditorLayer: true,
              keepXfaLayer: true,
              keepTextLayer: true,
              cancelExtraDelay: drawingDelay
            });
            this.renderingState = _ui_utils.RenderingStates.FINISHED;
            _classPrivateFieldGet(this, _useThumbnailCanvas).directDrawing = false;
          }
          this.cssTransform({
            target: this.canvas,
            redrawAnnotationLayer: true,
            redrawAnnotationEditorLayer: true,
            redrawXfaLayer: true,
            redrawTextLayer: !postponeDrawing,
            hideTextLayer: postponeDrawing
          });
          if (postponeDrawing) {
            return;
          }
          this.eventBus.dispatch("pagerendered", {
            source: this,
            pageNumber: this.id,
            cssTransform: true,
            timestamp: performance.now(),
            error: _classPrivateFieldGet(this, _renderError)
          });
          return;
        }
        if (!this.zoomLayer && !this.canvas.hidden) {
          this.zoomLayer = this.canvas.parentNode;
          this.zoomLayer.style.position = "absolute";
        }
      }
      if (this.zoomLayer) {
        this.cssTransform({
          target: this.zoomLayer.firstChild
        });
      }
      this.reset({
        keepZoomLayer: true,
        keepAnnotationLayer: true,
        keepAnnotationEditorLayer: true,
        keepXfaLayer: true,
        keepTextLayer: true
      });
    }
    cancelRendering() {
      let {
        keepAnnotationLayer = false,
        keepAnnotationEditorLayer = false,
        keepXfaLayer = false,
        keepTextLayer = false,
        cancelExtraDelay = 0
      } = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      if (this.renderTask) {
        this.renderTask.cancel(cancelExtraDelay);
        this.renderTask = null;
      }
      this.resume = null;
      if (this.textLayer && (!keepTextLayer || !this.textLayer.div)) {
        this.textLayer.cancel();
        this.textLayer = null;
      }
      if (this.structTreeLayer && !this.textLayer) {
        this.structTreeLayer = null;
      }
      if (this.annotationLayer && (!keepAnnotationLayer || !this.annotationLayer.div)) {
        this.annotationLayer.cancel();
        this.annotationLayer = null;
        this._annotationCanvasMap = null;
      }
      if (this.annotationEditorLayer && (!keepAnnotationEditorLayer || !this.annotationEditorLayer.div)) {
        this.annotationEditorLayer.cancel();
        this.annotationEditorLayer = null;
      }
      if (this.xfaLayer && (!keepXfaLayer || !this.xfaLayer.div)) {
        var _this$_textHighlighte;
        this.xfaLayer.cancel();
        this.xfaLayer = null;
        (_this$_textHighlighte = this._textHighlighter) === null || _this$_textHighlighte === void 0 || _this$_textHighlighte.disable();
      }
    }
    cssTransform(_ref2) {
      let {
        target,
        redrawAnnotationLayer = false,
        redrawAnnotationEditorLayer = false,
        redrawXfaLayer = false,
        redrawTextLayer = false,
        hideTextLayer = false
      } = _ref2;
      if (!target.hasAttribute("zooming")) {
        target.setAttribute("zooming", true);
        const {
          style
        } = target;
        style.width = style.height = "";
      }
      const originalViewport = _classPrivateFieldGet(this, _viewportMap).get(target);
      if (this.viewport !== originalViewport) {
        const relativeRotation = this.viewport.rotation - originalViewport.rotation;
        const absRotation = Math.abs(relativeRotation);
        let scaleX = 1,
          scaleY = 1;
        if (absRotation === 90 || absRotation === 270) {
          const {
            width,
            height
          } = this.viewport;
          scaleX = height / width;
          scaleY = width / height;
        }
        target.style.transform = `rotate(${relativeRotation}deg) scale(${scaleX}, ${scaleY})`;
      }
      if (redrawAnnotationLayer && this.annotationLayer) {
        _classPrivateMethodGet(this, _renderAnnotationLayer, _renderAnnotationLayer2).call(this);
      }
      if (redrawAnnotationEditorLayer && this.annotationEditorLayer) {
        _classPrivateMethodGet(this, _renderAnnotationEditorLayer, _renderAnnotationEditorLayer2).call(this);
      }
      if (redrawXfaLayer && this.xfaLayer) {
        _classPrivateMethodGet(this, _renderXfaLayer, _renderXfaLayer2).call(this);
      }
      if (this.textLayer) {
        if (hideTextLayer) {
          var _this$structTreeLayer2;
          this.textLayer.hide();
          (_this$structTreeLayer2 = this.structTreeLayer) === null || _this$structTreeLayer2 === void 0 || _this$structTreeLayer2.hide();
        } else if (redrawTextLayer) {
          _classPrivateMethodGet(this, _renderTextLayer, _renderTextLayer2).call(this);
        }
      }
    }
    get width() {
      return this.viewport.width;
    }
    get height() {
      return this.viewport.height;
    }
    getPagePoint(x, y) {
      return this.viewport.convertToPdfPoint(x, y);
    }
    async draw() {
      if (this.renderingState !== _ui_utils.RenderingStates.INITIAL) {
        console.error("Must be in new state before drawing");
        this.reset();
      }
      const {
        div,
        l10n,
        pageColors,
        pdfPage,
        viewport
      } = this;
      if (!pdfPage) {
        this.renderingState = _ui_utils.RenderingStates.FINISHED;
        throw new Error("pdfPage is not loaded");
      }
      this.renderingState = _ui_utils.RenderingStates.RUNNING;
      const canvasWrapper = document.createElement("div");
      canvasWrapper.classList.add("canvasWrapper");
      div.append(canvasWrapper);
      if (!this.textLayer && _classPrivateFieldGet(this, _textLayerMode) !== _ui_utils.TextLayerMode.DISABLE && !pdfPage.isPureXfa) {
        this._accessibilityManager || (this._accessibilityManager = new _text_accessibility.TextAccessibilityManager());
        this.textLayer = new _text_layer_builder.TextLayerBuilder({
          highlighter: this._textHighlighter,
          accessibilityManager: this._accessibilityManager,
          isOffscreenCanvasSupported: this.isOffscreenCanvasSupported,
          enablePermissions: _classPrivateFieldGet(this, _textLayerMode) === _ui_utils.TextLayerMode.ENABLE_PERMISSIONS
        });
        div.append(this.textLayer.div);
      }
      if (!this.annotationLayer && _classPrivateFieldGet(this, _annotationMode) !== _pdfjsLib.AnnotationMode.DISABLE) {
        const {
          annotationStorage,
          downloadManager,
          enableScripting,
          fieldObjectsPromise,
          hasJSActionsPromise,
          linkService
        } = _classPrivateFieldGet(this, _layerProperties).call(this);
        this._annotationCanvasMap || (this._annotationCanvasMap = new Map());
        this.annotationLayer = new _annotation_layer_builder.AnnotationLayerBuilder({
          pageDiv: div,
          pdfPage,
          annotationStorage,
          imageResourcesPath: this.imageResourcesPath,
          renderForms: _classPrivateFieldGet(this, _annotationMode) === _pdfjsLib.AnnotationMode.ENABLE_FORMS,
          linkService,
          downloadManager,
          l10n,
          enableScripting,
          hasJSActionsPromise,
          fieldObjectsPromise,
          annotationCanvasMap: this._annotationCanvasMap,
          accessibilityManager: this._accessibilityManager
        });
      }
      const renderContinueCallback = cont => {
        var _showCanvas;
        (_showCanvas = showCanvas) === null || _showCanvas === void 0 || _showCanvas(false);
        if (this.renderingQueue && !this.renderingQueue.isHighestPriority(this)) {
          this.renderingState = _ui_utils.RenderingStates.PAUSED;
          this.resume = () => {
            this.renderingState = _ui_utils.RenderingStates.RUNNING;
            cont();
          };
          return;
        }
        cont();
      };
      const {
        width,
        height
      } = viewport;
      const canvas = document.createElement("canvas");
      canvas.setAttribute("role", "presentation");
      canvas.hidden = true;
      const hasHCM = !!(pageColors !== null && pageColors !== void 0 && pageColors.background && pageColors !== null && pageColors !== void 0 && pageColors.foreground);
      let showCanvas = isLastShow => {
        if (!hasHCM || isLastShow) {
          canvas.hidden = false;
          showCanvas = null;
        }
      };
      canvasWrapper.append(canvas);
      this.canvas = canvas;
      const ctx = canvas.getContext("2d", {
        alpha: false
      });
      const outputScale = this.outputScale = new _ui_utils.OutputScale();
      if (this.maxCanvasPixels === 0) {
        const invScale = 1 / this.scale;
        outputScale.sx *= invScale;
        outputScale.sy *= invScale;
        _classPrivateFieldSet(this, _hasRestrictedScaling, true);
      } else if (this.maxCanvasPixels > 0) {
        const pixelsInViewport = width * height;
        const maxScale = Math.sqrt(this.maxCanvasPixels / pixelsInViewport);
        if (outputScale.sx > maxScale || outputScale.sy > maxScale) {
          outputScale.sx = maxScale;
          outputScale.sy = maxScale;
          _classPrivateFieldSet(this, _hasRestrictedScaling, true);
        } else {
          _classPrivateFieldSet(this, _hasRestrictedScaling, false);
        }
      }
      const sfx = (0, _ui_utils.approximateFraction)(outputScale.sx);
      const sfy = (0, _ui_utils.approximateFraction)(outputScale.sy);
      canvas.width = (0, _ui_utils.roundToDivide)(width * outputScale.sx, sfx[0]);
      canvas.height = (0, _ui_utils.roundToDivide)(height * outputScale.sy, sfy[0]);
      const {
        style
      } = canvas;
      style.width = (0, _ui_utils.roundToDivide)(width, sfx[1]) + "px";
      style.height = (0, _ui_utils.roundToDivide)(height, sfy[1]) + "px";
      _classPrivateFieldGet(this, _viewportMap).set(canvas, viewport);
      const transform = outputScale.scaled ? [outputScale.sx, 0, 0, outputScale.sy, 0, 0] : null;
      const renderContext = {
        canvasContext: ctx,
        transform,
        viewport,
        annotationMode: _classPrivateFieldGet(this, _annotationMode),
        optionalContentConfigPromise: this._optionalContentConfigPromise,
        annotationCanvasMap: this._annotationCanvasMap,
        pageColors
      };
      const renderTask = this.renderTask = this.pdfPage.render(renderContext);
      renderTask.onContinue = renderContinueCallback;
      const resultPromise = renderTask.promise.then(async () => {
        var _showCanvas2;
        (_showCanvas2 = showCanvas) === null || _showCanvas2 === void 0 || _showCanvas2(true);
        await _classPrivateMethodGet(this, _finishRenderTask, _finishRenderTask2).call(this, renderTask);
        _classPrivateMethodGet(this, _renderTextLayer, _renderTextLayer2).call(this);
        if (this.annotationLayer) {
          await _classPrivateMethodGet(this, _renderAnnotationLayer, _renderAnnotationLayer2).call(this);
        }
        if (!this.annotationEditorLayer) {
          var _this$annotationLayer2;
          const {
            annotationEditorUIManager
          } = _classPrivateFieldGet(this, _layerProperties).call(this);
          if (!annotationEditorUIManager) {
            return;
          }
          this.annotationEditorLayer = new _annotation_editor_layer_builder.AnnotationEditorLayerBuilder({
            uiManager: annotationEditorUIManager,
            pageDiv: div,
            pdfPage,
            l10n,
            accessibilityManager: this._accessibilityManager,
            annotationLayer: (_this$annotationLayer2 = this.annotationLayer) === null || _this$annotationLayer2 === void 0 ? void 0 : _this$annotationLayer2.annotationLayer
          });
        }
        _classPrivateMethodGet(this, _renderAnnotationEditorLayer, _renderAnnotationEditorLayer2).call(this);
      }, error => {
        if (!(error instanceof _pdfjsLib.RenderingCancelledException)) {
          var _showCanvas3;
          (_showCanvas3 = showCanvas) === null || _showCanvas3 === void 0 || _showCanvas3(true);
        }
        return _classPrivateMethodGet(this, _finishRenderTask, _finishRenderTask2).call(this, renderTask, error);
      });
      if (pdfPage.isPureXfa) {
        if (!this.xfaLayer) {
          const {
            annotationStorage,
            linkService
          } = _classPrivateFieldGet(this, _layerProperties).call(this);
          this.xfaLayer = new _xfa_layer_builder.XfaLayerBuilder({
            pageDiv: div,
            pdfPage,
            annotationStorage,
            linkService
          });
        } else if (this.xfaLayer.div) {
          div.append(this.xfaLayer.div);
        }
        _classPrivateMethodGet(this, _renderXfaLayer, _renderXfaLayer2).call(this);
      }
      div.setAttribute("data-loaded", true);
      this.eventBus.dispatch("pagerender", {
        source: this,
        pageNumber: this.id
      });
      return resultPromise;
    }
    setPageLabel(label) {
      this.pageLabel = typeof label === "string" ? label : null;
      if (this.pageLabel !== null) {
        this.div.setAttribute("data-page-label", this.pageLabel);
      } else {
        this.div.removeAttribute("data-page-label");
      }
    }
    get thumbnailCanvas() {
      const {
        directDrawing,
        initialOptionalContent,
        regularAnnotations
      } = _classPrivateFieldGet(this, _useThumbnailCanvas);
      return directDrawing && initialOptionalContent && regularAnnotations ? this.canvas : null;
    }
  }
  exports.PDFPageView = PDFPageView;
  function _setDimensions2() {
    const {
      viewport
    } = this;
    if (this.pdfPage) {
      if (_classPrivateFieldGet(this, _previousRotation) === viewport.rotation) {
        return;
      }
      _classPrivateFieldSet(this, _previousRotation, viewport.rotation);
    }
    (0, _pdfjsLib.setLayerDimensions)(this.div, viewport, true, false);
  }
  async function _renderAnnotationLayer2() {
    let error = null;
    try {
      await this.annotationLayer.render(this.viewport, "display");
    } catch (ex) {
      console.error(`#renderAnnotationLayer: "${ex}".`);
      error = ex;
    } finally {
      this.eventBus.dispatch("annotationlayerrendered", {
        source: this,
        pageNumber: this.id,
        error
      });
    }
  }
  async function _renderAnnotationEditorLayer2() {
    let error = null;
    try {
      await this.annotationEditorLayer.render(this.viewport, "display");
    } catch (ex) {
      console.error(`#renderAnnotationEditorLayer: "${ex}".`);
      error = ex;
    } finally {
      this.eventBus.dispatch("annotationeditorlayerrendered", {
        source: this,
        pageNumber: this.id,
        error
      });
    }
  }
  async function _renderXfaLayer2() {
    let error = null;
    try {
      const result = await this.xfaLayer.render(this.viewport, "display");
      if (result !== null && result !== void 0 && result.textDivs && this._textHighlighter) {
        _classPrivateMethodGet(this, _buildXfaTextContentItems, _buildXfaTextContentItems2).call(this, result.textDivs);
      }
    } catch (ex) {
      console.error(`#renderXfaLayer: "${ex}".`);
      error = ex;
    } finally {
      this.eventBus.dispatch("xfalayerrendered", {
        source: this,
        pageNumber: this.id,
        error
      });
    }
  }
  async function _renderTextLayer2() {
    const {
      pdfPage,
      textLayer,
      viewport
    } = this;
    if (!textLayer) {
      return;
    }
    let error = null;
    try {
      if (!textLayer.renderingDone) {
        const readableStream = pdfPage.streamTextContent({
          includeMarkedContent: true,
          disableNormalization: true
        });
        textLayer.setTextContentSource(readableStream);
      }
      await textLayer.render(viewport);
    } catch (ex) {
      if (ex instanceof _pdfjsLib.AbortException) {
        return;
      }
      console.error(`#renderTextLayer: "${ex}".`);
      error = ex;
    }
    this.eventBus.dispatch("textlayerrendered", {
      source: this,
      pageNumber: this.id,
      numTextDivs: textLayer.numTextDivs,
      error
    });
    _classPrivateMethodGet(this, _renderStructTreeLayer, _renderStructTreeLayer2).call(this);
  }
  async function _renderStructTreeLayer2() {
    var _this$structTreeLayer3, _this$structTreeLayer4;
    if (!this.textLayer) {
      return;
    }
    this.structTreeLayer || (this.structTreeLayer = new _struct_tree_layer_builder.StructTreeLayerBuilder());
    const tree = await (!this.structTreeLayer.renderingDone ? this.pdfPage.getStructTree() : null);
    const treeDom = (_this$structTreeLayer3 = this.structTreeLayer) === null || _this$structTreeLayer3 === void 0 ? void 0 : _this$structTreeLayer3.render(tree);
    if (treeDom) {
      var _this$canvas;
      (_this$canvas = this.canvas) === null || _this$canvas === void 0 || _this$canvas.append(treeDom);
    }
    (_this$structTreeLayer4 = this.structTreeLayer) === null || _this$structTreeLayer4 === void 0 || _this$structTreeLayer4.show();
  }
  async function _buildXfaTextContentItems2(textDivs) {
    const text = await this.pdfPage.getTextContent();
    const items = [];
    for (const item of text.items) {
      items.push(item.str);
    }
    this._textHighlighter.setTextMapping(textDivs, items);
    this._textHighlighter.enable();
  }
  async function _finishRenderTask2(renderTask) {
    let error = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    if (renderTask === this.renderTask) {
      this.renderTask = null;
    }
    if (error instanceof _pdfjsLib.RenderingCancelledException) {
      _classPrivateFieldSet(this, _renderError, null);
      return;
    }
    _classPrivateFieldSet(this, _renderError, error);
    this.renderingState = _ui_utils.RenderingStates.FINISHED;
    this._resetZoomLayer(true);
    _classPrivateFieldGet(this, _useThumbnailCanvas).regularAnnotations = !renderTask.separateAnnots;
    this.eventBus.dispatch("pagerendered", {
      source: this,
      pageNumber: this.id,
      cssTransform: false,
      timestamp: performance.now(),
      error: _classPrivateFieldGet(this, _renderError)
    });
    if (error) {
      throw error;
    }
  }
  
  /***/ }),
  /* 215 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.AnnotationEditorLayerBuilder = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _l10n_utils = __webpack_require__(213);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  var _annotationLayer = /*#__PURE__*/new WeakMap();
  var _uiManager = /*#__PURE__*/new WeakMap();
  class AnnotationEditorLayerBuilder {
    constructor(options) {
      _classPrivateFieldInitSpec(this, _annotationLayer, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _uiManager, {
        writable: true,
        value: void 0
      });
      this.pageDiv = options.pageDiv;
      this.pdfPage = options.pdfPage;
      this.accessibilityManager = options.accessibilityManager;
      this.l10n = options.l10n || _l10n_utils.NullL10n;
      this.annotationEditorLayer = null;
      this.div = null;
      this._cancelled = false;
      _classPrivateFieldSet(this, _uiManager, options.uiManager);
      _classPrivateFieldSet(this, _annotationLayer, options.annotationLayer || null);
    }
    async render(viewport) {
      let intent = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "display";
      if (intent !== "display") {
        return;
      }
      if (this._cancelled) {
        return;
      }
      const clonedViewport = viewport.clone({
        dontFlip: true
      });
      if (this.div) {
        this.annotationEditorLayer.update({
          viewport: clonedViewport
        });
        this.show();
        return;
      }
      const div = this.div = document.createElement("div");
      div.className = "annotationEditorLayer";
      div.tabIndex = 0;
      div.hidden = true;
      div.dir = _classPrivateFieldGet(this, _uiManager).direction;
      this.pageDiv.append(div);
      this.annotationEditorLayer = new _pdfjsLib.AnnotationEditorLayer({
        uiManager: _classPrivateFieldGet(this, _uiManager),
        div,
        accessibilityManager: this.accessibilityManager,
        pageIndex: this.pdfPage.pageNumber - 1,
        l10n: this.l10n,
        viewport: clonedViewport,
        annotationLayer: _classPrivateFieldGet(this, _annotationLayer)
      });
      const parameters = {
        viewport: clonedViewport,
        div,
        annotations: null,
        intent
      };
      this.annotationEditorLayer.render(parameters);
      this.show();
    }
    cancel() {
      this._cancelled = true;
      if (!this.div) {
        return;
      }
      this.pageDiv = null;
      this.annotationEditorLayer.destroy();
      this.div.remove();
    }
    hide() {
      if (!this.div) {
        return;
      }
      this.div.hidden = true;
    }
    show() {
      if (!this.div || this.annotationEditorLayer.isEmpty) {
        return;
      }
      this.div.hidden = false;
    }
  }
  exports.AnnotationEditorLayerBuilder = AnnotationEditorLayerBuilder;
  
  /***/ }),
  /* 216 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.AnnotationLayerBuilder = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _l10n_utils = __webpack_require__(213);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _onPresentationModeChanged = /*#__PURE__*/new WeakMap();
  var _updatePresentationModeState = /*#__PURE__*/new WeakSet();
  class AnnotationLayerBuilder {
    constructor(_ref) {
      let {
        pageDiv,
        pdfPage,
        linkService,
        downloadManager,
        annotationStorage = null,
        imageResourcesPath = "",
        renderForms = true,
        l10n = _l10n_utils.NullL10n,
        enableScripting = false,
        hasJSActionsPromise = null,
        fieldObjectsPromise = null,
        annotationCanvasMap = null,
        accessibilityManager = null
      } = _ref;
      _classPrivateMethodInitSpec(this, _updatePresentationModeState);
      _classPrivateFieldInitSpec(this, _onPresentationModeChanged, {
        writable: true,
        value: null
      });
      this.pageDiv = pageDiv;
      this.pdfPage = pdfPage;
      this.linkService = linkService;
      this.downloadManager = downloadManager;
      this.imageResourcesPath = imageResourcesPath;
      this.renderForms = renderForms;
      this.l10n = l10n;
      this.annotationStorage = annotationStorage;
      this.enableScripting = enableScripting;
      this._hasJSActionsPromise = hasJSActionsPromise || Promise.resolve(false);
      this._fieldObjectsPromise = fieldObjectsPromise || Promise.resolve(null);
      this._annotationCanvasMap = annotationCanvasMap;
      this._accessibilityManager = accessibilityManager;
      this.annotationLayer = null;
      this.div = null;
      this._cancelled = false;
      this._eventBus = linkService.eventBus;
    }
    async render(viewport) {
      let intent = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "display";
      if (this.div) {
        if (this._cancelled || !this.annotationLayer) {
          return;
        }
        this.annotationLayer.update({
          viewport: viewport.clone({
            dontFlip: true
          })
        });
        return;
      }
      const [annotations, hasJSActions, fieldObjects] = await Promise.all([this.pdfPage.getAnnotations({
        intent
      }), this._hasJSActionsPromise, this._fieldObjectsPromise]);
      if (this._cancelled) {
        return;
      }
      const div = this.div = document.createElement("div");
      div.className = "annotationLayer";
      this.pageDiv.append(div);
      if (annotations.length === 0) {
        this.hide();
        return;
      }
      this.annotationLayer = new _pdfjsLib.AnnotationLayer({
        div,
        accessibilityManager: this._accessibilityManager,
        annotationCanvasMap: this._annotationCanvasMap,
        l10n: this.l10n,
        page: this.pdfPage,
        viewport: viewport.clone({
          dontFlip: true
        })
      });
      await this.annotationLayer.render({
        annotations,
        imageResourcesPath: this.imageResourcesPath,
        renderForms: this.renderForms,
        linkService: this.linkService,
        downloadManager: this.downloadManager,
        annotationStorage: this.annotationStorage,
        enableScripting: this.enableScripting,
        hasJSActions,
        fieldObjects
      });
      if (this.linkService.isInPresentationMode) {
        _classPrivateMethodGet(this, _updatePresentationModeState, _updatePresentationModeState2).call(this, _ui_utils.PresentationModeState.FULLSCREEN);
      }
      if (!_classPrivateFieldGet(this, _onPresentationModeChanged)) {
        var _this$_eventBus;
        _classPrivateFieldSet(this, _onPresentationModeChanged, evt => {
          _classPrivateMethodGet(this, _updatePresentationModeState, _updatePresentationModeState2).call(this, evt.state);
        });
        (_this$_eventBus = this._eventBus) === null || _this$_eventBus === void 0 || _this$_eventBus._on("presentationmodechanged", _classPrivateFieldGet(this, _onPresentationModeChanged));
      }
    }
    cancel() {
      this._cancelled = true;
      if (_classPrivateFieldGet(this, _onPresentationModeChanged)) {
        var _this$_eventBus2;
        (_this$_eventBus2 = this._eventBus) === null || _this$_eventBus2 === void 0 || _this$_eventBus2._off("presentationmodechanged", _classPrivateFieldGet(this, _onPresentationModeChanged));
        _classPrivateFieldSet(this, _onPresentationModeChanged, null);
      }
    }
    hide() {
      if (!this.div) {
        return;
      }
      this.div.hidden = true;
    }
  }
  exports.AnnotationLayerBuilder = AnnotationLayerBuilder;
  function _updatePresentationModeState2(state) {
    if (!this.div) {
      return;
    }
    let disableFormElements = false;
    switch (state) {
      case _ui_utils.PresentationModeState.FULLSCREEN:
        disableFormElements = true;
        break;
      case _ui_utils.PresentationModeState.NORMAL:
        break;
      default:
        return;
    }
    for (const section of this.div.childNodes) {
      if (section.hasAttribute("data-internal-link")) {
        continue;
      }
      section.inert = disableFormElements;
    }
  }
  
  /***/ }),
  /* 217 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  __webpack_require__(122);
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.StructTreeLayerBuilder = void 0;
  __webpack_require__(136);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  const PDF_ROLE_TO_HTML_ROLE = {
    Document: null,
    DocumentFragment: null,
    Part: "group",
    Sect: "group",
    Div: "group",
    Aside: "note",
    NonStruct: "none",
    P: null,
    H: "heading",
    Title: null,
    FENote: "note",
    Sub: "group",
    Lbl: null,
    Span: null,
    Em: null,
    Strong: null,
    Link: "link",
    Annot: "note",
    Form: "form",
    Ruby: null,
    RB: null,
    RT: null,
    RP: null,
    Warichu: null,
    WT: null,
    WP: null,
    L: "list",
    LI: "listitem",
    LBody: null,
    Table: "table",
    TR: "row",
    TH: "columnheader",
    TD: "cell",
    THead: "columnheader",
    TBody: null,
    TFoot: null,
    Caption: null,
    Figure: "figure",
    Formula: null,
    Artifact: null
  };
  const HEADING_PATTERN = /^H(\d+)$/;
  var _treeDom = /*#__PURE__*/new WeakMap();
  var _setAttributes = /*#__PURE__*/new WeakSet();
  var _walk = /*#__PURE__*/new WeakSet();
  class StructTreeLayerBuilder {
    constructor() {
      _classPrivateMethodInitSpec(this, _walk);
      _classPrivateMethodInitSpec(this, _setAttributes);
      _classPrivateFieldInitSpec(this, _treeDom, {
        writable: true,
        value: undefined
      });
    }
    get renderingDone() {
      return _classPrivateFieldGet(this, _treeDom) !== undefined;
    }
    render(structTree) {
      if (_classPrivateFieldGet(this, _treeDom) !== undefined) {
        return _classPrivateFieldGet(this, _treeDom);
      }
      const treeDom = _classPrivateMethodGet(this, _walk, _walk2).call(this, structTree);
      treeDom === null || treeDom === void 0 || treeDom.classList.add("structTree");
      return _classPrivateFieldSet(this, _treeDom, treeDom);
    }
    hide() {
      if (_classPrivateFieldGet(this, _treeDom) && !_classPrivateFieldGet(this, _treeDom).hidden) {
        _classPrivateFieldGet(this, _treeDom).hidden = true;
      }
    }
    show() {
      var _classPrivateFieldGet2;
      if ((_classPrivateFieldGet2 = _classPrivateFieldGet(this, _treeDom)) !== null && _classPrivateFieldGet2 !== void 0 && _classPrivateFieldGet2.hidden) {
        _classPrivateFieldGet(this, _treeDom).hidden = false;
      }
    }
  }
  exports.StructTreeLayerBuilder = StructTreeLayerBuilder;
  function _setAttributes2(structElement, htmlElement) {
    const {
      alt,
      id,
      lang
    } = structElement;
    if (alt !== undefined) {
      htmlElement.setAttribute("aria-label", (0, _ui_utils.removeNullCharacters)(alt));
    }
    if (id !== undefined) {
      htmlElement.setAttribute("aria-owns", id);
    }
    if (lang !== undefined) {
      htmlElement.setAttribute("lang", (0, _ui_utils.removeNullCharacters)(lang, true));
    }
  }
  function _walk2(node) {
    if (!node) {
      return null;
    }
    const element = document.createElement("span");
    if ("role" in node) {
      const {
        role
      } = node;
      const match = role.match(HEADING_PATTERN);
      if (match) {
        element.setAttribute("role", "heading");
        element.setAttribute("aria-level", match[1]);
      } else if (PDF_ROLE_TO_HTML_ROLE[role]) {
        element.setAttribute("role", PDF_ROLE_TO_HTML_ROLE[role]);
      }
    }
    _classPrivateMethodGet(this, _setAttributes, _setAttributes2).call(this, node, element);
    if (node.children) {
      if (node.children.length === 1 && "id" in node.children[0]) {
        _classPrivateMethodGet(this, _setAttributes, _setAttributes2).call(this, node.children[0], element);
      } else {
        for (const kid of node.children) {
          element.append(_classPrivateMethodGet(this, _walk, _walk2).call(this, kid));
        }
      }
    }
    return element;
  }
  
  /***/ }),
  /* 218 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.TextAccessibilityManager = void 0;
  __webpack_require__(122);
  __webpack_require__(131);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classStaticPrivateMethodGet(receiver, classConstructor, method) { _classCheckPrivateStaticAccess(receiver, classConstructor); return method; }
  function _classCheckPrivateStaticAccess(receiver, classConstructor) { if (receiver !== classConstructor) { throw new TypeError("Private static access of wrong provenance"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  var _enabled = /*#__PURE__*/new WeakMap();
  var _textChildren = /*#__PURE__*/new WeakMap();
  var _textNodes = /*#__PURE__*/new WeakMap();
  var _waitingElements = /*#__PURE__*/new WeakMap();
  var _addIdToAriaOwns = /*#__PURE__*/new WeakSet();
  class TextAccessibilityManager {
    constructor() {
      _classPrivateMethodInitSpec(this, _addIdToAriaOwns);
      _classPrivateFieldInitSpec(this, _enabled, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _textChildren, {
        writable: true,
        value: null
      });
      _classPrivateFieldInitSpec(this, _textNodes, {
        writable: true,
        value: new Map()
      });
      _classPrivateFieldInitSpec(this, _waitingElements, {
        writable: true,
        value: new Map()
      });
    }
    setTextMapping(textDivs) {
      _classPrivateFieldSet(this, _textChildren, textDivs);
    }
    enable() {
      if (_classPrivateFieldGet(this, _enabled)) {
        throw new Error("TextAccessibilityManager is already enabled.");
      }
      if (!_classPrivateFieldGet(this, _textChildren)) {
        throw new Error("Text divs and strings have not been set.");
      }
      _classPrivateFieldSet(this, _enabled, true);
      _classPrivateFieldSet(this, _textChildren, _classPrivateFieldGet(this, _textChildren).slice());
      _classPrivateFieldGet(this, _textChildren).sort(_classStaticPrivateMethodGet(TextAccessibilityManager, TextAccessibilityManager, _compareElementPositions));
      if (_classPrivateFieldGet(this, _textNodes).size > 0) {
        const textChildren = _classPrivateFieldGet(this, _textChildren);
        for (const [id, nodeIndex] of _classPrivateFieldGet(this, _textNodes)) {
          const element = document.getElementById(id);
          if (!element) {
            _classPrivateFieldGet(this, _textNodes).delete(id);
            continue;
          }
          _classPrivateMethodGet(this, _addIdToAriaOwns, _addIdToAriaOwns2).call(this, id, textChildren[nodeIndex]);
        }
      }
      for (const [element, isRemovable] of _classPrivateFieldGet(this, _waitingElements)) {
        this.addPointerInTextLayer(element, isRemovable);
      }
      _classPrivateFieldGet(this, _waitingElements).clear();
    }
    disable() {
      if (!_classPrivateFieldGet(this, _enabled)) {
        return;
      }
      _classPrivateFieldGet(this, _waitingElements).clear();
      _classPrivateFieldSet(this, _textChildren, null);
      _classPrivateFieldSet(this, _enabled, false);
    }
    removePointerInTextLayer(element) {
      var _owns;
      if (!_classPrivateFieldGet(this, _enabled)) {
        _classPrivateFieldGet(this, _waitingElements).delete(element);
        return;
      }
      const children = _classPrivateFieldGet(this, _textChildren);
      if (!children || children.length === 0) {
        return;
      }
      const {
        id
      } = element;
      const nodeIndex = _classPrivateFieldGet(this, _textNodes).get(id);
      if (nodeIndex === undefined) {
        return;
      }
      const node = children[nodeIndex];
      _classPrivateFieldGet(this, _textNodes).delete(id);
      let owns = node.getAttribute("aria-owns");
      if ((_owns = owns) !== null && _owns !== void 0 && _owns.includes(id)) {
        owns = owns.split(" ").filter(x => x !== id).join(" ");
        if (owns) {
          node.setAttribute("aria-owns", owns);
        } else {
          node.removeAttribute("aria-owns");
          node.setAttribute("role", "presentation");
        }
      }
    }
    addPointerInTextLayer(element, isRemovable) {
      const {
        id
      } = element;
      if (!id) {
        return null;
      }
      if (!_classPrivateFieldGet(this, _enabled)) {
        _classPrivateFieldGet(this, _waitingElements).set(element, isRemovable);
        return null;
      }
      if (isRemovable) {
        this.removePointerInTextLayer(element);
      }
      const children = _classPrivateFieldGet(this, _textChildren);
      if (!children || children.length === 0) {
        return null;
      }
      const index = (0, _ui_utils.binarySearchFirstItem)(children, node => _classStaticPrivateMethodGet(TextAccessibilityManager, TextAccessibilityManager, _compareElementPositions).call(TextAccessibilityManager, element, node) < 0);
      const nodeIndex = Math.max(0, index - 1);
      const child = children[nodeIndex];
      _classPrivateMethodGet(this, _addIdToAriaOwns, _addIdToAriaOwns2).call(this, id, child);
      _classPrivateFieldGet(this, _textNodes).set(id, nodeIndex);
      const parent = child.parentNode;
      return parent !== null && parent !== void 0 && parent.classList.contains("markedContent") ? parent.id : null;
    }
    moveElementInDOM(container, element, contentElement, isRemovable) {
      const id = this.addPointerInTextLayer(contentElement, isRemovable);
      if (!container.hasChildNodes()) {
        container.append(element);
        return id;
      }
      const children = Array.from(container.childNodes).filter(node => node !== element);
      if (children.length === 0) {
        return id;
      }
      const elementToCompare = contentElement || element;
      const index = (0, _ui_utils.binarySearchFirstItem)(children, node => _classStaticPrivateMethodGet(TextAccessibilityManager, TextAccessibilityManager, _compareElementPositions).call(TextAccessibilityManager, elementToCompare, node) < 0);
      if (index === 0) {
        children[0].before(element);
      } else {
        children[index - 1].after(element);
      }
      return id;
    }
  }
  exports.TextAccessibilityManager = TextAccessibilityManager;
  function _compareElementPositions(e1, e2) {
    const rect1 = e1.getBoundingClientRect();
    const rect2 = e2.getBoundingClientRect();
    if (rect1.width === 0 && rect1.height === 0) {
      return +1;
    }
    if (rect2.width === 0 && rect2.height === 0) {
      return -1;
    }
    const top1 = rect1.y;
    const bot1 = rect1.y + rect1.height;
    const mid1 = rect1.y + rect1.height / 2;
    const top2 = rect2.y;
    const bot2 = rect2.y + rect2.height;
    const mid2 = rect2.y + rect2.height / 2;
    if (mid1 <= top2 && mid2 >= bot1) {
      return -1;
    }
    if (mid2 <= top1 && mid1 >= bot2) {
      return +1;
    }
    const centerX1 = rect1.x + rect1.width / 2;
    const centerX2 = rect2.x + rect2.width / 2;
    return centerX1 - centerX2;
  }
  function _addIdToAriaOwns2(id, node) {
    const owns = node.getAttribute("aria-owns");
    if (!(owns !== null && owns !== void 0 && owns.includes(id))) {
      node.setAttribute("aria-owns", owns ? `${owns} ${id}` : id);
    }
    node.removeAttribute("role");
  }
  
  /***/ }),
  /* 219 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.TextHighlighter = void 0;
  __webpack_require__(122);
  __webpack_require__(142);
  __webpack_require__(131);
  class TextHighlighter {
    constructor(_ref) {
      let {
        findController,
        eventBus,
        pageIndex
      } = _ref;
      this.findController = findController;
      this.matches = [];
      this.eventBus = eventBus;
      this.pageIdx = pageIndex;
      this._onUpdateTextLayerMatches = null;
      this.textDivs = null;
      this.textContentItemsStr = null;
      this.enabled = false;
    }
    setTextMapping(divs, texts) {
      this.textDivs = divs;
      this.textContentItemsStr = texts;
    }
    enable() {
      if (!this.textDivs || !this.textContentItemsStr) {
        throw new Error("Text divs and strings have not been set.");
      }
      if (this.enabled) {
        throw new Error("TextHighlighter is already enabled.");
      }
      this.enabled = true;
      if (!this._onUpdateTextLayerMatches) {
        this._onUpdateTextLayerMatches = evt => {
          if (evt.pageIndex === this.pageIdx || evt.pageIndex === -1) {
            this._updateMatches();
          }
        };
        this.eventBus._on("updatetextlayermatches", this._onUpdateTextLayerMatches);
      }
      this._updateMatches();
    }
    disable() {
      if (!this.enabled) {
        return;
      }
      this.enabled = false;
      if (this._onUpdateTextLayerMatches) {
        this.eventBus._off("updatetextlayermatches", this._onUpdateTextLayerMatches);
        this._onUpdateTextLayerMatches = null;
      }
      this._updateMatches(true);
    }
    _convertMatches(matches, matchesLength) {
      if (!matches) {
        return [];
      }
      const {
        textContentItemsStr
      } = this;
      let i = 0,
        iIndex = 0;
      const end = textContentItemsStr.length - 1;
      const result = [];
      for (let m = 0, mm = matches.length; m < mm; m++) {
        let matchIdx = matches[m];
        while (i !== end && matchIdx >= iIndex + textContentItemsStr[i].length) {
          iIndex += textContentItemsStr[i].length;
          i++;
        }
        if (i === textContentItemsStr.length) {
          console.error("Could not find a matching mapping");
        }
        const match = {
          begin: {
            divIdx: i,
            offset: matchIdx - iIndex
          }
        };
        matchIdx += matchesLength[m];
        while (i !== end && matchIdx > iIndex + textContentItemsStr[i].length) {
          iIndex += textContentItemsStr[i].length;
          i++;
        }
        match.end = {
          divIdx: i,
          offset: matchIdx - iIndex
        };
        result.push(match);
      }
      return result;
    }
    _renderMatches(matches) {
      if (matches.length === 0) {
        return;
      }
      const {
        findController,
        pageIdx
      } = this;
      const {
        textContentItemsStr,
        textDivs
      } = this;
      const isSelectedPage = pageIdx === findController.selected.pageIdx;
      const selectedMatchIdx = findController.selected.matchIdx;
      const highlightAll = findController.state.highlightAll;
      let prevEnd = null;
      const infinity = {
        divIdx: -1,
        offset: undefined
      };
      function beginText(begin, className) {
        const divIdx = begin.divIdx;
        textDivs[divIdx].textContent = "";
        return appendTextToDiv(divIdx, 0, begin.offset, className);
      }
      function appendTextToDiv(divIdx, fromOffset, toOffset, className) {
        let div = textDivs[divIdx];
        if (div.nodeType === Node.TEXT_NODE) {
          const span = document.createElement("span");
          div.before(span);
          span.append(div);
          textDivs[divIdx] = span;
          div = span;
        }
        const content = textContentItemsStr[divIdx].substring(fromOffset, toOffset);
        const node = document.createTextNode(content);
        if (className) {
          const span = document.createElement("span");
          span.className = `${className} appended`;
          span.append(node);
          div.append(span);
          return className.includes("selected") ? span.offsetLeft : 0;
        }
        div.append(node);
        return 0;
      }
      let i0 = selectedMatchIdx,
        i1 = i0 + 1;
      if (highlightAll) {
        i0 = 0;
        i1 = matches.length;
      } else if (!isSelectedPage) {
        return;
      }
      let lastDivIdx = -1;
      let lastOffset = -1;
      for (let i = i0; i < i1; i++) {
        const match = matches[i];
        const begin = match.begin;
        if (begin.divIdx === lastDivIdx && begin.offset === lastOffset) {
          continue;
        }
        lastDivIdx = begin.divIdx;
        lastOffset = begin.offset;
        const end = match.end;
        const isSelected = isSelectedPage && i === selectedMatchIdx;
        const highlightSuffix = isSelected ? " selected" : "";
        let selectedLeft = 0;
        if (!prevEnd || begin.divIdx !== prevEnd.divIdx) {
          if (prevEnd !== null) {
            appendTextToDiv(prevEnd.divIdx, prevEnd.offset, infinity.offset);
          }
          beginText(begin);
        } else {
          appendTextToDiv(prevEnd.divIdx, prevEnd.offset, begin.offset);
        }
        if (begin.divIdx === end.divIdx) {
          selectedLeft = appendTextToDiv(begin.divIdx, begin.offset, end.offset, "highlight" + highlightSuffix);
        } else {
          selectedLeft = appendTextToDiv(begin.divIdx, begin.offset, infinity.offset, "highlight begin" + highlightSuffix);
          for (let n0 = begin.divIdx + 1, n1 = end.divIdx; n0 < n1; n0++) {
            textDivs[n0].className = "highlight middle" + highlightSuffix;
          }
          beginText(end, "highlight end" + highlightSuffix);
        }
        prevEnd = end;
        if (isSelected) {
          findController.scrollMatchIntoView({
            element: textDivs[begin.divIdx],
            selectedLeft,
            pageIndex: pageIdx,
            matchIndex: selectedMatchIdx
          });
        }
      }
      if (prevEnd) {
        appendTextToDiv(prevEnd.divIdx, prevEnd.offset, infinity.offset);
      }
    }
    _updateMatches() {
      let reset = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      if (!this.enabled && !reset) {
        return;
      }
      const {
        findController,
        matches,
        pageIdx
      } = this;
      const {
        textContentItemsStr,
        textDivs
      } = this;
      let clearedUntilDivIdx = -1;
      for (const match of matches) {
        const begin = Math.max(clearedUntilDivIdx, match.begin.divIdx);
        for (let n = begin, end = match.end.divIdx; n <= end; n++) {
          const div = textDivs[n];
          div.textContent = textContentItemsStr[n];
          div.className = "";
        }
        clearedUntilDivIdx = match.end.divIdx + 1;
      }
      if (!(findController !== null && findController !== void 0 && findController.highlightMatches) || reset) {
        return;
      }
      const pageMatches = findController.pageMatches[pageIdx] || null;
      const pageMatchesLength = findController.pageMatchesLength[pageIdx] || null;
      this.matches = this._convertMatches(pageMatches, pageMatchesLength);
      this._renderMatches(this.matches);
    }
  }
  exports.TextHighlighter = TextHighlighter;
  
  /***/ }),
  /* 220 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.TextLayerBuilder = void 0;
  __webpack_require__(2);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _ui_utils = __webpack_require__(148);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  var _enablePermissions = /*#__PURE__*/new WeakMap();
  var _rotation = /*#__PURE__*/new WeakMap();
  var _scale = /*#__PURE__*/new WeakMap();
  var _textContentSource = /*#__PURE__*/new WeakMap();
  var _finishRendering = /*#__PURE__*/new WeakSet();
  var _bindMouse = /*#__PURE__*/new WeakSet();
  class TextLayerBuilder {
    constructor(_ref) {
      let {
        highlighter = null,
        accessibilityManager = null,
        isOffscreenCanvasSupported = true,
        enablePermissions = false
      } = _ref;
      _classPrivateMethodInitSpec(this, _bindMouse);
      _classPrivateMethodInitSpec(this, _finishRendering);
      _classPrivateFieldInitSpec(this, _enablePermissions, {
        writable: true,
        value: false
      });
      _classPrivateFieldInitSpec(this, _rotation, {
        writable: true,
        value: 0
      });
      _classPrivateFieldInitSpec(this, _scale, {
        writable: true,
        value: 0
      });
      _classPrivateFieldInitSpec(this, _textContentSource, {
        writable: true,
        value: null
      });
      this.textContentItemsStr = [];
      this.renderingDone = false;
      this.textDivs = [];
      this.textDivProperties = new WeakMap();
      this.textLayerRenderTask = null;
      this.highlighter = highlighter;
      this.accessibilityManager = accessibilityManager;
      this.isOffscreenCanvasSupported = isOffscreenCanvasSupported;
      _classPrivateFieldSet(this, _enablePermissions, enablePermissions === true);
      this.div = document.createElement("div");
      this.div.className = "textLayer";
      this.hide();
    }
    get numTextDivs() {
      return this.textDivs.length;
    }
    async render(viewport) {
      var _this$highlighter, _this$accessibilityMa, _this$accessibilityMa2;
      if (!_classPrivateFieldGet(this, _textContentSource)) {
        throw new Error('No "textContentSource" parameter specified.');
      }
      const scale = viewport.scale * (globalThis.devicePixelRatio || 1);
      const {
        rotation
      } = viewport;
      if (this.renderingDone) {
        const mustRotate = rotation !== _classPrivateFieldGet(this, _rotation);
        const mustRescale = scale !== _classPrivateFieldGet(this, _scale);
        if (mustRotate || mustRescale) {
          this.hide();
          (0, _pdfjsLib.updateTextLayer)({
            container: this.div,
            viewport,
            textDivs: this.textDivs,
            textDivProperties: this.textDivProperties,
            isOffscreenCanvasSupported: this.isOffscreenCanvasSupported,
            mustRescale,
            mustRotate
          });
          _classPrivateFieldSet(this, _scale, scale);
          _classPrivateFieldSet(this, _rotation, rotation);
        }
        this.show();
        return;
      }
      this.cancel();
      (_this$highlighter = this.highlighter) === null || _this$highlighter === void 0 || _this$highlighter.setTextMapping(this.textDivs, this.textContentItemsStr);
      (_this$accessibilityMa = this.accessibilityManager) === null || _this$accessibilityMa === void 0 || _this$accessibilityMa.setTextMapping(this.textDivs);
      this.textLayerRenderTask = (0, _pdfjsLib.renderTextLayer)({
        textContentSource: _classPrivateFieldGet(this, _textContentSource),
        container: this.div,
        viewport,
        textDivs: this.textDivs,
        textDivProperties: this.textDivProperties,
        textContentItemsStr: this.textContentItemsStr,
        isOffscreenCanvasSupported: this.isOffscreenCanvasSupported
      });
      await this.textLayerRenderTask.promise;
      _classPrivateMethodGet(this, _finishRendering, _finishRendering2).call(this);
      _classPrivateFieldSet(this, _scale, scale);
      _classPrivateFieldSet(this, _rotation, rotation);
      this.show();
      (_this$accessibilityMa2 = this.accessibilityManager) === null || _this$accessibilityMa2 === void 0 || _this$accessibilityMa2.enable();
    }
    hide() {
      if (!this.div.hidden) {
        var _this$highlighter2;
        (_this$highlighter2 = this.highlighter) === null || _this$highlighter2 === void 0 || _this$highlighter2.disable();
        this.div.hidden = true;
      }
    }
    show() {
      if (this.div.hidden && this.renderingDone) {
        var _this$highlighter3;
        this.div.hidden = false;
        (_this$highlighter3 = this.highlighter) === null || _this$highlighter3 === void 0 || _this$highlighter3.enable();
      }
    }
    cancel() {
      var _this$highlighter4, _this$accessibilityMa3;
      if (this.textLayerRenderTask) {
        this.textLayerRenderTask.cancel();
        this.textLayerRenderTask = null;
      }
      (_this$highlighter4 = this.highlighter) === null || _this$highlighter4 === void 0 || _this$highlighter4.disable();
      (_this$accessibilityMa3 = this.accessibilityManager) === null || _this$accessibilityMa3 === void 0 || _this$accessibilityMa3.disable();
      this.textContentItemsStr.length = 0;
      this.textDivs.length = 0;
      this.textDivProperties = new WeakMap();
    }
    setTextContentSource(source) {
      this.cancel();
      _classPrivateFieldSet(this, _textContentSource, source);
    }
  }
  exports.TextLayerBuilder = TextLayerBuilder;
  function _finishRendering2() {
    this.renderingDone = true;
    const endOfContent = document.createElement("div");
    endOfContent.className = "endOfContent";
    this.div.append(endOfContent);
    _classPrivateMethodGet(this, _bindMouse, _bindMouse2).call(this);
  }
  function _bindMouse2() {
    const {
      div
    } = this;
    div.addEventListener("mousedown", evt => {
      const end = div.querySelector(".endOfContent");
      if (!end) {
        return;
      }
      let adjustTop = evt.target !== div;
      adjustTop && (adjustTop = getComputedStyle(end).getPropertyValue("-moz-user-select") !== "none");
      if (adjustTop) {
        const divBounds = div.getBoundingClientRect();
        const r = Math.max(0, (evt.pageY - divBounds.top) / divBounds.height);
        end.style.top = (r * 100).toFixed(2) + "%";
      }
      end.classList.add("active");
    });
    div.addEventListener("mouseup", () => {
      const end = div.querySelector(".endOfContent");
      if (!end) {
        return;
      }
      end.style.top = "";
      end.classList.remove("active");
    });
    div.addEventListener("copy", event => {
      if (!_classPrivateFieldGet(this, _enablePermissions)) {
        const selection = document.getSelection();
        event.clipboardData.setData("text/plain", (0, _ui_utils.removeNullCharacters)((0, _pdfjsLib.normalizeUnicode)(selection.toString())));
      }
      event.preventDefault();
      event.stopPropagation();
    });
  }
  
  /***/ }),
  /* 221 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.XfaLayerBuilder = void 0;
  __webpack_require__(2);
  var _pdfjsLib = __webpack_require__(182);
  class XfaLayerBuilder {
    constructor(_ref) {
      let {
        pageDiv,
        pdfPage,
        annotationStorage = null,
        linkService,
        xfaHtml = null
      } = _ref;
      this.pageDiv = pageDiv;
      this.pdfPage = pdfPage;
      this.annotationStorage = annotationStorage;
      this.linkService = linkService;
      this.xfaHtml = xfaHtml;
      this.div = null;
      this._cancelled = false;
    }
    async render(viewport) {
      let intent = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "display";
      if (intent === "print") {
        const parameters = {
          viewport: viewport.clone({
            dontFlip: true
          }),
          div: this.div,
          xfaHtml: this.xfaHtml,
          annotationStorage: this.annotationStorage,
          linkService: this.linkService,
          intent
        };
        const div = document.createElement("div");
        this.pageDiv.append(div);
        parameters.div = div;
        return _pdfjsLib.XfaLayer.render(parameters);
      }
      const xfaHtml = await this.pdfPage.getXfa();
      if (this._cancelled || !xfaHtml) {
        return {
          textDivs: []
        };
      }
      const parameters = {
        viewport: viewport.clone({
          dontFlip: true
        }),
        div: this.div,
        xfaHtml,
        annotationStorage: this.annotationStorage,
        linkService: this.linkService,
        intent
      };
      if (this.div) {
        return _pdfjsLib.XfaLayer.update(parameters);
      }
      this.div = document.createElement("div");
      this.pageDiv.append(this.div);
      parameters.div = this.div;
      return _pdfjsLib.XfaLayer.render(parameters);
    }
    cancel() {
      this._cancelled = true;
    }
    hide() {
      if (!this.div) {
        return;
      }
      this.div.hidden = true;
    }
  }
  exports.XfaLayerBuilder = XfaLayerBuilder;
  
  /***/ }),
  /* 222 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.SecondaryToolbar = void 0;
  __webpack_require__(142);
  __webpack_require__(122);
  var _ui_utils = __webpack_require__(148);
  var _pdf_viewer = __webpack_require__(210);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  var _updateUIState = /*#__PURE__*/new WeakSet();
  var _bindClickListeners = /*#__PURE__*/new WeakSet();
  var _bindCursorToolsListener = /*#__PURE__*/new WeakSet();
  var _bindScrollModeListener = /*#__PURE__*/new WeakSet();
  var _bindSpreadModeListener = /*#__PURE__*/new WeakSet();
  class SecondaryToolbar {
    constructor(options, eventBus) {
      _classPrivateMethodInitSpec(this, _bindSpreadModeListener);
      _classPrivateMethodInitSpec(this, _bindScrollModeListener);
      _classPrivateMethodInitSpec(this, _bindCursorToolsListener);
      _classPrivateMethodInitSpec(this, _bindClickListeners);
      _classPrivateMethodInitSpec(this, _updateUIState);
      this.toolbar = options.toolbar;
      this.toggleButton = options.toggleButton;
      this.buttons = [{
        element: options.presentationModeButton,
        eventName: "presentationmode",
        close: true
      }, {
        element: options.printButton,
        eventName: "print",
        close: true
      }, {
        element: options.downloadButton,
        eventName: "download",
        close: true
      }, {
        element: options.viewBookmarkButton,
        eventName: null,
        close: true
      }, {
        element: options.firstPageButton,
        eventName: "firstpage",
        close: true
      }, {
        element: options.lastPageButton,
        eventName: "lastpage",
        close: true
      }, {
        element: options.pageRotateCwButton,
        eventName: "rotatecw",
        close: false
      }, {
        element: options.pageRotateCcwButton,
        eventName: "rotateccw",
        close: false
      }, {
        element: options.cursorSelectToolButton,
        eventName: "switchcursortool",
        eventDetails: {
          tool: _ui_utils.CursorTool.SELECT
        },
        close: true
      }, {
        element: options.cursorHandToolButton,
        eventName: "switchcursortool",
        eventDetails: {
          tool: _ui_utils.CursorTool.HAND
        },
        close: true
      }, {
        element: options.scrollPageButton,
        eventName: "switchscrollmode",
        eventDetails: {
          mode: _ui_utils.ScrollMode.PAGE
        },
        close: true
      }, {
        element: options.scrollVerticalButton,
        eventName: "switchscrollmode",
        eventDetails: {
          mode: _ui_utils.ScrollMode.VERTICAL
        },
        close: true
      }, {
        element: options.scrollHorizontalButton,
        eventName: "switchscrollmode",
        eventDetails: {
          mode: _ui_utils.ScrollMode.HORIZONTAL
        },
        close: true
      }, {
        element: options.scrollWrappedButton,
        eventName: "switchscrollmode",
        eventDetails: {
          mode: _ui_utils.ScrollMode.WRAPPED
        },
        close: true
      }, {
        element: options.spreadNoneButton,
        eventName: "switchspreadmode",
        eventDetails: {
          mode: _ui_utils.SpreadMode.NONE
        },
        close: true
      }, {
        element: options.spreadOddButton,
        eventName: "switchspreadmode",
        eventDetails: {
          mode: _ui_utils.SpreadMode.ODD
        },
        close: true
      }, {
        element: options.spreadEvenButton,
        eventName: "switchspreadmode",
        eventDetails: {
          mode: _ui_utils.SpreadMode.EVEN
        },
        close: true
      }, {
        element: options.documentPropertiesButton,
        eventName: "documentproperties",
        close: true
      }];
      this.buttons.push({
        element: options.openFileButton,
        eventName: "openfile",
        close: true
      });
      this.items = {
        firstPage: options.firstPageButton,
        lastPage: options.lastPageButton,
        pageRotateCw: options.pageRotateCwButton,
        pageRotateCcw: options.pageRotateCcwButton
      };
      this.eventBus = eventBus;
      this.opened = false;
      _classPrivateMethodGet(this, _bindClickListeners, _bindClickListeners2).call(this);
      _classPrivateMethodGet(this, _bindCursorToolsListener, _bindCursorToolsListener2).call(this, options);
      _classPrivateMethodGet(this, _bindScrollModeListener, _bindScrollModeListener2).call(this, options);
      _classPrivateMethodGet(this, _bindSpreadModeListener, _bindSpreadModeListener2).call(this, options);
      this.reset();
    }
    get isOpen() {
      return this.opened;
    }
    setPageNumber(pageNumber) {
      this.pageNumber = pageNumber;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this);
    }
    setPagesCount(pagesCount) {
      this.pagesCount = pagesCount;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this);
    }
    reset() {
      this.pageNumber = 0;
      this.pagesCount = 0;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this);
      this.eventBus.dispatch("secondarytoolbarreset", {
        source: this
      });
    }
    open() {
      if (this.opened) {
        return;
      }
      this.opened = true;
      (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, true, this.toolbar);
    }
    close() {
      if (!this.opened) {
        return;
      }
      this.opened = false;
      (0, _ui_utils.toggleExpandedBtn)(this.toggleButton, false, this.toolbar);
    }
    toggle() {
      if (this.opened) {
        this.close();
      } else {
        this.open();
      }
    }
  }
  exports.SecondaryToolbar = SecondaryToolbar;
  function _updateUIState2() {
    this.items.firstPage.disabled = this.pageNumber <= 1;
    this.items.lastPage.disabled = this.pageNumber >= this.pagesCount;
    this.items.pageRotateCw.disabled = this.pagesCount === 0;
    this.items.pageRotateCcw.disabled = this.pagesCount === 0;
  }
  function _bindClickListeners2() {
    this.toggleButton.addEventListener("click", this.toggle.bind(this));
    for (const {
      element,
      eventName,
      close,
      eventDetails
    } of this.buttons) {
      element.addEventListener("click", evt => {
        if (eventName !== null) {
          this.eventBus.dispatch(eventName, {
            source: this,
            ...eventDetails
          });
        }
        if (close) {
          this.close();
        }
        this.eventBus.dispatch("reporttelemetry", {
          source: this,
          details: {
            type: "buttons",
            data: {
              id: element.id
            }
          }
        });
      });
    }
  }
  function _bindCursorToolsListener2(_ref) {
    let {
      cursorSelectToolButton,
      cursorHandToolButton
    } = _ref;
    this.eventBus._on("cursortoolchanged", _ref2 => {
      let {
        tool
      } = _ref2;
      (0, _ui_utils.toggleCheckedBtn)(cursorSelectToolButton, tool === _ui_utils.CursorTool.SELECT);
      (0, _ui_utils.toggleCheckedBtn)(cursorHandToolButton, tool === _ui_utils.CursorTool.HAND);
    });
  }
  function _bindScrollModeListener2(_ref3) {
    let {
      scrollPageButton,
      scrollVerticalButton,
      scrollHorizontalButton,
      scrollWrappedButton,
      spreadNoneButton,
      spreadOddButton,
      spreadEvenButton
    } = _ref3;
    const scrollModeChanged = _ref4 => {
      let {
        mode
      } = _ref4;
      (0, _ui_utils.toggleCheckedBtn)(scrollPageButton, mode === _ui_utils.ScrollMode.PAGE);
      (0, _ui_utils.toggleCheckedBtn)(scrollVerticalButton, mode === _ui_utils.ScrollMode.VERTICAL);
      (0, _ui_utils.toggleCheckedBtn)(scrollHorizontalButton, mode === _ui_utils.ScrollMode.HORIZONTAL);
      (0, _ui_utils.toggleCheckedBtn)(scrollWrappedButton, mode === _ui_utils.ScrollMode.WRAPPED);
      const forceScrollModePage = this.pagesCount > _pdf_viewer.PagesCountLimit.FORCE_SCROLL_MODE_PAGE;
      scrollPageButton.disabled = forceScrollModePage;
      scrollVerticalButton.disabled = forceScrollModePage;
      scrollHorizontalButton.disabled = forceScrollModePage;
      scrollWrappedButton.disabled = forceScrollModePage;
      const isHorizontal = mode === _ui_utils.ScrollMode.HORIZONTAL;
      spreadNoneButton.disabled = isHorizontal;
      spreadOddButton.disabled = isHorizontal;
      spreadEvenButton.disabled = isHorizontal;
    };
    this.eventBus._on("scrollmodechanged", scrollModeChanged);
    this.eventBus._on("secondarytoolbarreset", evt => {
      if (evt.source === this) {
        scrollModeChanged({
          mode: _ui_utils.ScrollMode.VERTICAL
        });
      }
    });
  }
  function _bindSpreadModeListener2(_ref5) {
    let {
      spreadNoneButton,
      spreadOddButton,
      spreadEvenButton
    } = _ref5;
    const spreadModeChanged = _ref6 => {
      let {
        mode
      } = _ref6;
      (0, _ui_utils.toggleCheckedBtn)(spreadNoneButton, mode === _ui_utils.SpreadMode.NONE);
      (0, _ui_utils.toggleCheckedBtn)(spreadOddButton, mode === _ui_utils.SpreadMode.ODD);
      (0, _ui_utils.toggleCheckedBtn)(spreadEvenButton, mode === _ui_utils.SpreadMode.EVEN);
    };
    this.eventBus._on("spreadmodechanged", spreadModeChanged);
    this.eventBus._on("secondarytoolbarreset", evt => {
      if (evt.source === this) {
        spreadModeChanged({
          mode: _ui_utils.SpreadMode.NONE
        });
      }
    });
  }
  
  /***/ }),
  /* 223 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.Toolbar = void 0;
  __webpack_require__(142);
  __webpack_require__(122);
  __webpack_require__(2);
  var _ui_utils = __webpack_require__(148);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateMethodInitSpec(obj, privateSet) { _checkPrivateRedeclaration(obj, privateSet); privateSet.add(obj); }
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  function _classPrivateMethodGet(receiver, privateSet, fn) { if (!privateSet.has(receiver)) { throw new TypeError("attempted to get private field on non-instance"); } return fn; }
  const PAGE_NUMBER_LOADING_INDICATOR = "visiblePageIsLoading";
  var _wasLocalized = /*#__PURE__*/new WeakMap();
  var _bindListeners = /*#__PURE__*/new WeakSet();
  var _bindEditorToolsListener = /*#__PURE__*/new WeakSet();
  var _updateUIState = /*#__PURE__*/new WeakSet();
  var _adjustScaleWidth = /*#__PURE__*/new WeakSet();
  class Toolbar {
    constructor(_options, eventBus, _l10n) {
      _classPrivateMethodInitSpec(this, _adjustScaleWidth);
      _classPrivateMethodInitSpec(this, _updateUIState);
      _classPrivateMethodInitSpec(this, _bindEditorToolsListener);
      _classPrivateMethodInitSpec(this, _bindListeners);
      _classPrivateFieldInitSpec(this, _wasLocalized, {
        writable: true,
        value: false
      });
      this.toolbar = _options.container;
      this.eventBus = eventBus;
      this.l10n = _l10n;
      this.buttons = [{
        element: _options.previous,
        eventName: "previouspage"
      }, {
        element: _options.next,
        eventName: "nextpage"
      }, {
        element: _options.zoomIn,
        eventName: "zoomin"
      }, {
        element: _options.zoomOut,
        eventName: "zoomout"
      }, {
        element: _options.print,
        eventName: "print"
      }, {
        element: _options.download,
        eventName: "download"
      }, {
        element: _options.editorFreeTextButton,
        eventName: "switchannotationeditormode",
        eventDetails: {
          get mode() {
            const {
              classList
            } = _options.editorFreeTextButton;
            return classList.contains("toggled") ? _pdfjsLib.AnnotationEditorType.NONE : _pdfjsLib.AnnotationEditorType.FREETEXT;
          }
        }
      }, {
        element: _options.editorInkButton,
        eventName: "switchannotationeditormode",
        eventDetails: {
          get mode() {
            const {
              classList
            } = _options.editorInkButton;
            return classList.contains("toggled") ? _pdfjsLib.AnnotationEditorType.NONE : _pdfjsLib.AnnotationEditorType.INK;
          }
        }
      }, {
        element: _options.editorStampButton,
        eventName: "switchannotationeditormode",
        eventDetails: {
          get mode() {
            const {
              classList
            } = _options.editorStampButton;
            return classList.contains("toggled") ? _pdfjsLib.AnnotationEditorType.NONE : _pdfjsLib.AnnotationEditorType.STAMP;
          }
        }
      }];
      this.buttons.push({
        element: _options.openFile,
        eventName: "openfile"
      });
      this.items = {
        numPages: _options.numPages,
        pageNumber: _options.pageNumber,
        scaleSelect: _options.scaleSelect,
        customScaleOption: _options.customScaleOption,
        previous: _options.previous,
        next: _options.next,
        zoomIn: _options.zoomIn,
        zoomOut: _options.zoomOut
      };
      _classPrivateMethodGet(this, _bindListeners, _bindListeners2).call(this, _options);
      this.reset();
    }
    setPageNumber(pageNumber, pageLabel) {
      this.pageNumber = pageNumber;
      this.pageLabel = pageLabel;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, false);
    }
    setPagesCount(pagesCount, hasPageLabels) {
      this.pagesCount = pagesCount;
      this.hasPageLabels = hasPageLabels;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, true);
    }
    setPageScale(pageScaleValue, pageScale) {
      this.pageScaleValue = (pageScaleValue || pageScale).toString();
      this.pageScale = pageScale;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, false);
    }
    reset() {
      this.pageNumber = 0;
      this.pageLabel = null;
      this.hasPageLabels = false;
      this.pagesCount = 0;
      this.pageScaleValue = _ui_utils.DEFAULT_SCALE_VALUE;
      this.pageScale = _ui_utils.DEFAULT_SCALE;
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, true);
      this.updateLoadingIndicatorState();
      this.eventBus.dispatch("toolbarreset", {
        source: this
      });
    }
    updateLoadingIndicatorState() {
      let loading = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
      const {
        pageNumber
      } = this.items;
      pageNumber.classList.toggle(PAGE_NUMBER_LOADING_INDICATOR, loading);
    }
  }
  exports.Toolbar = Toolbar;
  function _bindListeners2(options) {
    const {
      pageNumber,
      scaleSelect
    } = this.items;
    const self = this;
    for (const {
      element,
      eventName,
      eventDetails
    } of this.buttons) {
      element.addEventListener("click", evt => {
        if (eventName !== null) {
          this.eventBus.dispatch(eventName, {
            source: this,
            ...eventDetails
          });
        }
      });
    }
    pageNumber.addEventListener("click", function () {
      this.select();
    });
    pageNumber.addEventListener("change", function () {
      self.eventBus.dispatch("pagenumberchanged", {
        source: self,
        value: this.value
      });
    });
    scaleSelect.addEventListener("change", function () {
      if (this.value === "custom") {
        return;
      }
      self.eventBus.dispatch("scalechanged", {
        source: self,
        value: this.value
      });
    });
    scaleSelect.addEventListener("click", function (evt) {
      const target = evt.target;
      if (this.value === self.pageScaleValue && target.tagName.toUpperCase() === "OPTION") {
        this.blur();
      }
    });
    scaleSelect.oncontextmenu = _pdfjsLib.noContextMenu;
    this.eventBus._on("localized", () => {
      _classPrivateFieldSet(this, _wasLocalized, true);
      _classPrivateMethodGet(this, _adjustScaleWidth, _adjustScaleWidth2).call(this);
      _classPrivateMethodGet(this, _updateUIState, _updateUIState2).call(this, true);
    });
    _classPrivateMethodGet(this, _bindEditorToolsListener, _bindEditorToolsListener2).call(this, options);
  }
  function _bindEditorToolsListener2(_ref) {
    let {
      editorFreeTextButton,
      editorFreeTextParamsToolbar,
      editorInkButton,
      editorInkParamsToolbar,
      editorStampButton,
      editorStampParamsToolbar
    } = _ref;
    const editorModeChanged = _ref2 => {
      let {
        mode
      } = _ref2;
      (0, _ui_utils.toggleCheckedBtn)(editorFreeTextButton, mode === _pdfjsLib.AnnotationEditorType.FREETEXT, editorFreeTextParamsToolbar);
      (0, _ui_utils.toggleCheckedBtn)(editorInkButton, mode === _pdfjsLib.AnnotationEditorType.INK, editorInkParamsToolbar);
      (0, _ui_utils.toggleCheckedBtn)(editorStampButton, mode === _pdfjsLib.AnnotationEditorType.STAMP, editorStampParamsToolbar);
      const isDisable = mode === _pdfjsLib.AnnotationEditorType.DISABLE;
      editorFreeTextButton.disabled = isDisable;
      editorInkButton.disabled = isDisable;
      editorStampButton.disabled = isDisable;
    };
    this.eventBus._on("annotationeditormodechanged", editorModeChanged);
    this.eventBus._on("toolbarreset", evt => {
      if (evt.source === this) {
        editorModeChanged({
          mode: _pdfjsLib.AnnotationEditorType.DISABLE
        });
      }
    });
  }
  function _updateUIState2() {
    let resetNumPages = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
    if (!_classPrivateFieldGet(this, _wasLocalized)) {
      return;
    }
    const {
      pageNumber,
      pagesCount,
      pageScaleValue,
      pageScale,
      items
    } = this;
    if (resetNumPages) {
      if (this.hasPageLabels) {
        items.pageNumber.type = "text";
      } else {
        items.pageNumber.type = "number";
        this.l10n.get("of_pages", {
          pagesCount
        }).then(msg => {
          items.numPages.textContent = msg;
        });
      }
      items.pageNumber.max = pagesCount;
    }
    if (this.hasPageLabels) {
      items.pageNumber.value = this.pageLabel;
      this.l10n.get("page_of_pages", {
        pageNumber,
        pagesCount
      }).then(msg => {
        items.numPages.textContent = msg;
      });
    } else {
      items.pageNumber.value = pageNumber;
    }
    items.previous.disabled = pageNumber <= 1;
    items.next.disabled = pageNumber >= pagesCount;
    items.zoomOut.disabled = pageScale <= _ui_utils.MIN_SCALE;
    items.zoomIn.disabled = pageScale >= _ui_utils.MAX_SCALE;
    this.l10n.get("page_scale_percent", {
      scale: Math.round(pageScale * 10000) / 100
    }).then(msg => {
      let predefinedValueFound = false;
      for (const option of items.scaleSelect.options) {
        if (option.value !== pageScaleValue) {
          option.selected = false;
          continue;
        }
        option.selected = true;
        predefinedValueFound = true;
      }
      if (!predefinedValueFound) {
        items.customScaleOption.textContent = msg;
        items.customScaleOption.selected = true;
      }
    });
  }
  async function _adjustScaleWidth2() {
    const {
      items,
      l10n
    } = this;
    const predefinedValuesPromise = Promise.all([l10n.get("page_scale_auto"), l10n.get("page_scale_actual"), l10n.get("page_scale_fit"), l10n.get("page_scale_width")]);
    await _ui_utils.animationStarted;
    const style = getComputedStyle(items.scaleSelect);
    const scaleSelectWidth = parseFloat(style.getPropertyValue("--scale-select-width"));
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d", {
      alpha: false
    });
    ctx.font = `${style.fontSize} ${style.fontFamily}`;
    let maxWidth = 0;
    for (const predefinedValue of await predefinedValuesPromise) {
      const {
        width
      } = ctx.measureText(predefinedValue);
      if (width > maxWidth) {
        maxWidth = width;
      }
    }
    maxWidth += 0.3 * scaleSelectWidth;
    if (maxWidth > scaleSelectWidth) {
      const container = items.scaleSelect.parentNode;
      container.style.setProperty("--scale-select-width", `${maxWidth}px`);
    }
    canvas.width = 0;
    canvas.height = 0;
  }
  
  /***/ }),
  /* 224 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.ViewHistory = void 0;
  __webpack_require__(116);
  __webpack_require__(142);
  __webpack_require__(2);
  const DEFAULT_VIEW_HISTORY_CACHE_SIZE = 20;
  class ViewHistory {
    constructor(fingerprint) {
      let cacheSize = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : DEFAULT_VIEW_HISTORY_CACHE_SIZE;
      this.fingerprint = fingerprint;
      this.cacheSize = cacheSize;
      this._initializedPromise = this._readFromStorage().then(databaseStr => {
        const database = JSON.parse(databaseStr || "{}");
        let index = -1;
        if (!Array.isArray(database.files)) {
          database.files = [];
        } else {
          while (database.files.length >= this.cacheSize) {
            database.files.shift();
          }
          for (let i = 0, ii = database.files.length; i < ii; i++) {
            const branch = database.files[i];
            if (branch.fingerprint === this.fingerprint) {
              index = i;
              break;
            }
          }
        }
        if (index === -1) {
          index = database.files.push({
            fingerprint: this.fingerprint
          }) - 1;
        }
        this.file = database.files[index];
        this.database = database;
      });
    }
    async _writeToStorage() {
      const databaseStr = JSON.stringify(this.database);
      localStorage.setItem("pdfjs.history", databaseStr);
    }
    async _readFromStorage() {
      return localStorage.getItem("pdfjs.history");
    }
    async set(name, val) {
      await this._initializedPromise;
      this.file[name] = val;
      return this._writeToStorage();
    }
    async setMultiple(properties) {
      await this._initializedPromise;
      for (const name in properties) {
        this.file[name] = properties[name];
      }
      return this._writeToStorage();
    }
    async get(name, defaultValue) {
      await this._initializedPromise;
      const val = this.file[name];
      return val !== undefined ? val : defaultValue;
    }
    async getMultiple(properties) {
      await this._initializedPromise;
      const values = Object.create(null);
      for (const name in properties) {
        const val = this.file[name];
        values[name] = val !== undefined ? val : properties[name];
      }
      return values;
    }
  }
  exports.ViewHistory = ViewHistory;
  
  /***/ }),
  /* 225 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.BasePreferences = void 0;
  __webpack_require__(122);
  __webpack_require__(2);
  var _app_options = __webpack_require__(183);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  function _classPrivateFieldSet(receiver, privateMap, value) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "set"); _classApplyDescriptorSet(receiver, descriptor, value); return value; }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorSet(receiver, descriptor, value) { if (descriptor.set) { descriptor.set.call(receiver, value); } else { if (!descriptor.writable) { throw new TypeError("attempted to set read only private field"); } descriptor.value = value; } }
  var _defaults = /*#__PURE__*/new WeakMap();
  var _prefs = /*#__PURE__*/new WeakMap();
  var _initializedPromise = /*#__PURE__*/new WeakMap();
  class BasePreferences {
    constructor() {
      _classPrivateFieldInitSpec(this, _defaults, {
        writable: true,
        value: Object.freeze({
          "annotationEditorMode": 0,
          "annotationMode": 2,
          "cursorToolOnLoad": 0,
          "defaultZoomDelay": 400,
          "defaultZoomValue": "",
          "disablePageLabels": false,
          "enablePermissions": false,
          "enablePrintAutoRotate": true,
          "enableScripting": true,
          "enableStampEditor": true,
          "externalLinkTarget": 0,
          "historyUpdateUrl": false,
          "ignoreDestinationZoom": false,
          "forcePageColors": false,
          "pageColorsBackground": "Canvas",
          "pageColorsForeground": "CanvasText",
          "pdfBugEnabled": false,
          "sidebarViewOnLoad": -1,
          "scrollModeOnLoad": -1,
          "spreadModeOnLoad": -1,
          "textLayerMode": 1,
          "viewerCssTheme": 0,
          "viewOnLoad": 0,
          "disableAutoFetch": false,
          "disableFontFace": false,
          "disableRange": false,
          "disableStream": false,
          "enableXfa": true
        })
      });
      _classPrivateFieldInitSpec(this, _prefs, {
        writable: true,
        value: Object.create(null)
      });
      _classPrivateFieldInitSpec(this, _initializedPromise, {
        writable: true,
        value: null
      });
      if (this.constructor === BasePreferences) {
        throw new Error("Cannot initialize BasePreferences.");
      }
      _classPrivateFieldSet(this, _initializedPromise, this._readFromStorage(_classPrivateFieldGet(this, _defaults)).then(prefs => {
        for (const name in _classPrivateFieldGet(this, _defaults)) {
          const prefValue = prefs === null || prefs === void 0 ? void 0 : prefs[name];
          if (typeof prefValue === typeof _classPrivateFieldGet(this, _defaults)[name]) {
            _classPrivateFieldGet(this, _prefs)[name] = prefValue;
          }
        }
      }));
    }
    async _writeToStorage(prefObj) {
      throw new Error("Not implemented: _writeToStorage");
    }
    async _readFromStorage(prefObj) {
      throw new Error("Not implemented: _readFromStorage");
    }
    async reset() {
      await _classPrivateFieldGet(this, _initializedPromise);
      const prefs = _classPrivateFieldGet(this, _prefs);
      _classPrivateFieldSet(this, _prefs, Object.create(null));
      return this._writeToStorage(_classPrivateFieldGet(this, _defaults)).catch(reason => {
        _classPrivateFieldSet(this, _prefs, prefs);
        throw reason;
      });
    }
    async set(name, value) {
      await _classPrivateFieldGet(this, _initializedPromise);
      const defaultValue = _classPrivateFieldGet(this, _defaults)[name],
        prefs = _classPrivateFieldGet(this, _prefs);
      if (defaultValue === undefined) {
        throw new Error(`Set preference: "${name}" is undefined.`);
      } else if (value === undefined) {
        throw new Error("Set preference: no value is specified.");
      }
      const valueType = typeof value,
        defaultType = typeof defaultValue;
      if (valueType !== defaultType) {
        if (valueType === "number" && defaultType === "string") {
          value = value.toString();
        } else {
          throw new Error(`Set preference: "${value}" is a ${valueType}, expected a ${defaultType}.`);
        }
      } else if (valueType === "number" && !Number.isInteger(value)) {
        throw new Error(`Set preference: "${value}" must be an integer.`);
      }
      _classPrivateFieldGet(this, _prefs)[name] = value;
      return this._writeToStorage(_classPrivateFieldGet(this, _prefs)).catch(reason => {
        _classPrivateFieldSet(this, _prefs, prefs);
        throw reason;
      });
    }
    async get(name) {
      var _classPrivateFieldGet2;
      await _classPrivateFieldGet(this, _initializedPromise);
      const defaultValue = _classPrivateFieldGet(this, _defaults)[name];
      if (defaultValue === undefined) {
        throw new Error(`Get preference: "${name}" is undefined.`);
      }
      return (_classPrivateFieldGet2 = _classPrivateFieldGet(this, _prefs)[name]) !== null && _classPrivateFieldGet2 !== void 0 ? _classPrivateFieldGet2 : defaultValue;
    }
    async getAll() {
      await _classPrivateFieldGet(this, _initializedPromise);
      const obj = Object.create(null);
      for (const name in _classPrivateFieldGet(this, _defaults)) {
        var _classPrivateFieldGet3;
        obj[name] = (_classPrivateFieldGet3 = _classPrivateFieldGet(this, _prefs)[name]) !== null && _classPrivateFieldGet3 !== void 0 ? _classPrivateFieldGet3 : _classPrivateFieldGet(this, _defaults)[name];
      }
      return obj;
    }
  }
  exports.BasePreferences = BasePreferences;
  
  /***/ }),
  /* 226 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.DownloadManager = void 0;
  __webpack_require__(122);
  __webpack_require__(145);
  __webpack_require__(146);
  __webpack_require__(147);
  var _pdfjsLib = __webpack_require__(182);
  function _classPrivateFieldInitSpec(obj, privateMap, value) { _checkPrivateRedeclaration(obj, privateMap); privateMap.set(obj, value); }
  function _checkPrivateRedeclaration(obj, privateCollection) { if (privateCollection.has(obj)) { throw new TypeError("Cannot initialize the same private elements twice on an object"); } }
  function _classPrivateFieldGet(receiver, privateMap) { var descriptor = _classExtractFieldDescriptor(receiver, privateMap, "get"); return _classApplyDescriptorGet(receiver, descriptor); }
  function _classExtractFieldDescriptor(receiver, privateMap, action) { if (!privateMap.has(receiver)) { throw new TypeError("attempted to " + action + " private field on non-instance"); } return privateMap.get(receiver); }
  function _classApplyDescriptorGet(receiver, descriptor) { if (descriptor.get) { return descriptor.get.call(receiver); } return descriptor.value; }
  ;
  function download(blobUrl, filename) {
    const a = document.createElement("a");
    if (!a.click) {
      throw new Error('DownloadManager: "a.click()" is not supported.');
    }
    a.href = blobUrl;
    a.target = "_parent";
    if ("download" in a) {
      a.download = filename;
    }
    (document.body || document.documentElement).append(a);
    a.click();
    a.remove();
  }
  var _openBlobUrls = /*#__PURE__*/new WeakMap();
  class DownloadManager {
    constructor() {
      _classPrivateFieldInitSpec(this, _openBlobUrls, {
        writable: true,
        value: new WeakMap()
      });
    }
    downloadUrl(url, filename, _options) {
      if (!(0, _pdfjsLib.createValidAbsoluteUrl)(url, "http://example.com")) {
        console.error(`downloadUrl - not a valid URL: ${url}`);
        return;
      }
      download(url + "#pdfjs.action=download", filename);
    }
    downloadData(data, filename, contentType) {
      const blobUrl = URL.createObjectURL(new Blob([data], {
        type: contentType
      }));
      download(blobUrl, filename);
    }
    openOrDownloadData(element, data, filename) {
      const isPdfData = (0, _pdfjsLib.isPdfFile)(filename);
      const contentType = isPdfData ? "application/pdf" : "";
      if (isPdfData) {
        let blobUrl = _classPrivateFieldGet(this, _openBlobUrls).get(element);
        if (!blobUrl) {
          blobUrl = URL.createObjectURL(new Blob([data], {
            type: contentType
          }));
          _classPrivateFieldGet(this, _openBlobUrls).set(element, blobUrl);
        }
        let viewerUrl;
        viewerUrl = "?file=" + encodeURIComponent(blobUrl + "#" + filename);
        try {
          window.open(viewerUrl);
          return true;
        } catch (ex) {
          console.error(`openOrDownloadData: ${ex}`);
          URL.revokeObjectURL(blobUrl);
          _classPrivateFieldGet(this, _openBlobUrls).delete(element);
        }
      }
      this.downloadData(data, filename, contentType);
      return false;
    }
    download(blob, url, filename, _options) {
      const blobUrl = URL.createObjectURL(blob);
      download(blobUrl, filename);
    }
  }
  exports.DownloadManager = DownloadManager;
  
  /***/ }),
  /* 227 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.GenericL10n = void 0;
  __webpack_require__(2);
  __webpack_require__(228);
  var _l10n_utils = __webpack_require__(213);
  const PARTIAL_LANG_CODES = {
    en: "en-US",
    es: "es-ES",
    fy: "fy-NL",
    ga: "ga-IE",
    gu: "gu-IN",
    hi: "hi-IN",
    hy: "hy-AM",
    nb: "nb-NO",
    ne: "ne-NP",
    nn: "nn-NO",
    pa: "pa-IN",
    pt: "pt-PT",
    sv: "sv-SE",
    zh: "zh-CN"
  };
  function fixupLangCode(langCode) {
    return PARTIAL_LANG_CODES[langCode === null || langCode === void 0 ? void 0 : langCode.toLowerCase()] || langCode;
  }
  class GenericL10n {
    constructor(lang) {
      const {
        webL10n
      } = document;
      this._lang = lang;
      this._ready = new Promise((resolve, reject) => {
        webL10n.setLanguage(fixupLangCode(lang), () => {
          resolve(webL10n);
        });
      });
    }
    async getLanguage() {
      const l10n = await this._ready;
      return l10n.getLanguage();
    }
    async getDirection() {
      const l10n = await this._ready;
      return l10n.getDirection();
    }
    async get(key) {
      let args = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      let fallback = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : (0, _l10n_utils.getL10nFallback)(key, args);
      const l10n = await this._ready;
      return l10n.get(key, args, fallback);
    }
    async translate(element) {
      const l10n = await this._ready;
      return l10n.translate(element);
    }
  }
  exports.GenericL10n = GenericL10n;
  
  /***/ }),
  /* 228 */
  /***/ ((__unused_webpack_module, __unused_webpack_exports, __webpack_require__) => {
  
  
  
  __webpack_require__(116);
  __webpack_require__(136);
  __webpack_require__(149);
  document.webL10n = function (window, document) {
    var gL10nData = {};
    var gTextData = '';
    var gTextProp = 'textContent';
    var gLanguage = '';
    var gMacros = {};
    var gReadyState = 'loading';
    var gAsyncResourceLoading = true;
    function getL10nResourceLinks() {
      return document.querySelectorAll('link[type="application/l10n"]');
    }
    function getL10nDictionary() {
      var script = document.querySelector('script[type="application/l10n"]');
      return script ? JSON.parse(script.innerHTML) : null;
    }
    function getTranslatableChildren(element) {
      return element ? element.querySelectorAll('*[data-l10n-id]') : [];
    }
    function getL10nAttributes(element) {
      if (!element) return {};
      var l10nId = element.getAttribute('data-l10n-id');
      var l10nArgs = element.getAttribute('data-l10n-args');
      var args = {};
      if (l10nArgs) {
        try {
          args = JSON.parse(l10nArgs);
        } catch (e) {
          console.warn('could not parse arguments for #' + l10nId);
        }
      }
      return {
        id: l10nId,
        args: args
      };
    }
    function xhrLoadText(url, onSuccess, onFailure) {
      onSuccess = onSuccess || function _onSuccess(data) {};
      onFailure = onFailure || function _onFailure() {};
      var xhr = new XMLHttpRequest();
      xhr.open('GET', url, gAsyncResourceLoading);
      if (xhr.overrideMimeType) {
        xhr.overrideMimeType('text/plain; charset=utf-8');
      }
      xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
          if (xhr.status == 200 || xhr.status === 0) {
            onSuccess(xhr.responseText);
          } else {
            onFailure();
          }
        }
      };
      xhr.onerror = onFailure;
      xhr.ontimeout = onFailure;
      try {
        xhr.send(null);
      } catch (e) {
        onFailure();
      }
    }
    function parseResource(href, lang, successCallback, failureCallback) {
      var baseURL = href.replace(/[^\/]*$/, '') || './';
      function evalString(text) {
        if (text.lastIndexOf('\\') < 0) return text;
        return text.replace(/\\\\/g, '\\').replace(/\\n/g, '\n').replace(/\\r/g, '\r').replace(/\\t/g, '\t').replace(/\\b/g, '\b').replace(/\\f/g, '\f').replace(/\\{/g, '{').replace(/\\}/g, '}').replace(/\\"/g, '"').replace(/\\'/g, "'");
      }
      function parseProperties(text, parsedPropertiesCallback) {
        var dictionary = {};
        var reBlank = /^\s*|\s*$/;
        var reComment = /^\s*#|^\s*$/;
        var reSection = /^\s*\[(.*)\]\s*$/;
        var reImport = /^\s*@import\s+url\((.*)\)\s*$/i;
        var reSplit = /^([^=\s]*)\s*=\s*(.+)$/;
        function parseRawLines(rawText, extendedSyntax, parsedRawLinesCallback) {
          var entries = rawText.replace(reBlank, '').split(/[\r\n]+/);
          var currentLang = '*';
          var genericLang = lang.split('-', 1)[0];
          var skipLang = false;
          var match = '';
          function nextEntry() {
            while (true) {
              if (!entries.length) {
                parsedRawLinesCallback();
                return;
              }
              var line = entries.shift();
              if (reComment.test(line)) continue;
              if (extendedSyntax) {
                match = reSection.exec(line);
                if (match) {
                  currentLang = match[1].toLowerCase();
                  skipLang = currentLang !== '*' && currentLang !== lang && currentLang !== genericLang;
                  continue;
                } else if (skipLang) {
                  continue;
                }
                match = reImport.exec(line);
                if (match) {
                  loadImport(baseURL + match[1], nextEntry);
                  return;
                }
              }
              var tmp = line.match(reSplit);
              if (tmp && tmp.length == 3) {
                dictionary[tmp[1]] = evalString(tmp[2]);
              }
            }
          }
          nextEntry();
        }
        function loadImport(url, callback) {
          xhrLoadText(url, function (content) {
            parseRawLines(content, false, callback);
          }, function () {
            console.warn(url + ' not found.');
            callback();
          });
        }
        parseRawLines(text, true, function () {
          parsedPropertiesCallback(dictionary);
        });
      }
      xhrLoadText(href, function (response) {
        gTextData += response;
        parseProperties(response, function (data) {
          for (var key in data) {
            var id,
              prop,
              index = key.lastIndexOf('.');
            if (index > 0) {
              id = key.substring(0, index);
              prop = key.substring(index + 1);
            } else {
              id = key;
              prop = gTextProp;
            }
            if (!gL10nData[id]) {
              gL10nData[id] = {};
            }
            gL10nData[id][prop] = data[key];
          }
          if (successCallback) {
            successCallback();
          }
        });
      }, failureCallback);
    }
    function loadLocale(lang, callback) {
      if (lang) {
        lang = lang.toLowerCase();
      }
      callback = callback || function _callback() {};
      clear();
      gLanguage = lang;
      var langLinks = getL10nResourceLinks();
      var langCount = langLinks.length;
      if (langCount === 0) {
        var dict = getL10nDictionary();
        if (dict && dict.locales && dict.default_locale) {
          console.log('using the embedded JSON directory, early way out');
          gL10nData = dict.locales[lang];
          if (!gL10nData) {
            var defaultLocale = dict.default_locale.toLowerCase();
            for (var anyCaseLang in dict.locales) {
              anyCaseLang = anyCaseLang.toLowerCase();
              if (anyCaseLang === lang) {
                gL10nData = dict.locales[lang];
                break;
              } else if (anyCaseLang === defaultLocale) {
                gL10nData = dict.locales[defaultLocale];
              }
            }
          }
          callback();
        } else {
          console.log('no resource to load, early way out');
        }
        gReadyState = 'complete';
        return;
      }
      var onResourceLoaded = null;
      var gResourceCount = 0;
      onResourceLoaded = function () {
        gResourceCount++;
        if (gResourceCount >= langCount) {
          callback();
          gReadyState = 'complete';
        }
      };
      function L10nResourceLink(link) {
        var href = link.href;
        this.load = function (lang, callback) {
          parseResource(href, lang, callback, function () {
            console.warn(href + ' not found.');
            console.warn('"' + lang + '" resource not found');
            gLanguage = '';
            callback();
          });
        };
      }
      for (var i = 0; i < langCount; i++) {
        var resource = new L10nResourceLink(langLinks[i]);
        resource.load(lang, onResourceLoaded);
      }
    }
    function clear() {
      gL10nData = {};
      gTextData = '';
      gLanguage = '';
    }
    function getPluralRules(lang) {
      var locales2rules = {
        'af': 3,
        'ak': 4,
        'am': 4,
        'ar': 1,
        'asa': 3,
        'az': 0,
        'be': 11,
        'bem': 3,
        'bez': 3,
        'bg': 3,
        'bh': 4,
        'bm': 0,
        'bn': 3,
        'bo': 0,
        'br': 20,
        'brx': 3,
        'bs': 11,
        'ca': 3,
        'cgg': 3,
        'chr': 3,
        'cs': 12,
        'cy': 17,
        'da': 3,
        'de': 3,
        'dv': 3,
        'dz': 0,
        'ee': 3,
        'el': 3,
        'en': 3,
        'eo': 3,
        'es': 3,
        'et': 3,
        'eu': 3,
        'fa': 0,
        'ff': 5,
        'fi': 3,
        'fil': 4,
        'fo': 3,
        'fr': 5,
        'fur': 3,
        'fy': 3,
        'ga': 8,
        'gd': 24,
        'gl': 3,
        'gsw': 3,
        'gu': 3,
        'guw': 4,
        'gv': 23,
        'ha': 3,
        'haw': 3,
        'he': 2,
        'hi': 4,
        'hr': 11,
        'hu': 0,
        'id': 0,
        'ig': 0,
        'ii': 0,
        'is': 3,
        'it': 3,
        'iu': 7,
        'ja': 0,
        'jmc': 3,
        'jv': 0,
        'ka': 0,
        'kab': 5,
        'kaj': 3,
        'kcg': 3,
        'kde': 0,
        'kea': 0,
        'kk': 3,
        'kl': 3,
        'km': 0,
        'kn': 0,
        'ko': 0,
        'ksb': 3,
        'ksh': 21,
        'ku': 3,
        'kw': 7,
        'lag': 18,
        'lb': 3,
        'lg': 3,
        'ln': 4,
        'lo': 0,
        'lt': 10,
        'lv': 6,
        'mas': 3,
        'mg': 4,
        'mk': 16,
        'ml': 3,
        'mn': 3,
        'mo': 9,
        'mr': 3,
        'ms': 0,
        'mt': 15,
        'my': 0,
        'nah': 3,
        'naq': 7,
        'nb': 3,
        'nd': 3,
        'ne': 3,
        'nl': 3,
        'nn': 3,
        'no': 3,
        'nr': 3,
        'nso': 4,
        'ny': 3,
        'nyn': 3,
        'om': 3,
        'or': 3,
        'pa': 3,
        'pap': 3,
        'pl': 13,
        'ps': 3,
        'pt': 3,
        'rm': 3,
        'ro': 9,
        'rof': 3,
        'ru': 11,
        'rwk': 3,
        'sah': 0,
        'saq': 3,
        'se': 7,
        'seh': 3,
        'ses': 0,
        'sg': 0,
        'sh': 11,
        'shi': 19,
        'sk': 12,
        'sl': 14,
        'sma': 7,
        'smi': 7,
        'smj': 7,
        'smn': 7,
        'sms': 7,
        'sn': 3,
        'so': 3,
        'sq': 3,
        'sr': 11,
        'ss': 3,
        'ssy': 3,
        'st': 3,
        'sv': 3,
        'sw': 3,
        'syr': 3,
        'ta': 3,
        'te': 3,
        'teo': 3,
        'th': 0,
        'ti': 4,
        'tig': 3,
        'tk': 3,
        'tl': 4,
        'tn': 3,
        'to': 0,
        'tr': 0,
        'ts': 3,
        'tzm': 22,
        'uk': 11,
        'ur': 3,
        've': 3,
        'vi': 0,
        'vun': 3,
        'wa': 4,
        'wae': 3,
        'wo': 0,
        'xh': 3,
        'xog': 3,
        'yo': 0,
        'zh': 0,
        'zu': 3
      };
      function isIn(n, list) {
        return list.indexOf(n) !== -1;
      }
      function isBetween(n, start, end) {
        return start <= n && n <= end;
      }
      var pluralRules = {
        '0': function (n) {
          return 'other';
        },
        '1': function (n) {
          if (isBetween(n % 100, 3, 10)) return 'few';
          if (n === 0) return 'zero';
          if (isBetween(n % 100, 11, 99)) return 'many';
          if (n == 2) return 'two';
          if (n == 1) return 'one';
          return 'other';
        },
        '2': function (n) {
          if (n !== 0 && n % 10 === 0) return 'many';
          if (n == 2) return 'two';
          if (n == 1) return 'one';
          return 'other';
        },
        '3': function (n) {
          if (n == 1) return 'one';
          return 'other';
        },
        '4': function (n) {
          if (isBetween(n, 0, 1)) return 'one';
          return 'other';
        },
        '5': function (n) {
          if (isBetween(n, 0, 2) && n != 2) return 'one';
          return 'other';
        },
        '6': function (n) {
          if (n === 0) return 'zero';
          if (n % 10 == 1 && n % 100 != 11) return 'one';
          return 'other';
        },
        '7': function (n) {
          if (n == 2) return 'two';
          if (n == 1) return 'one';
          return 'other';
        },
        '8': function (n) {
          if (isBetween(n, 3, 6)) return 'few';
          if (isBetween(n, 7, 10)) return 'many';
          if (n == 2) return 'two';
          if (n == 1) return 'one';
          return 'other';
        },
        '9': function (n) {
          if (n === 0 || n != 1 && isBetween(n % 100, 1, 19)) return 'few';
          if (n == 1) return 'one';
          return 'other';
        },
        '10': function (n) {
          if (isBetween(n % 10, 2, 9) && !isBetween(n % 100, 11, 19)) return 'few';
          if (n % 10 == 1 && !isBetween(n % 100, 11, 19)) return 'one';
          return 'other';
        },
        '11': function (n) {
          if (isBetween(n % 10, 2, 4) && !isBetween(n % 100, 12, 14)) return 'few';
          if (n % 10 === 0 || isBetween(n % 10, 5, 9) || isBetween(n % 100, 11, 14)) return 'many';
          if (n % 10 == 1 && n % 100 != 11) return 'one';
          return 'other';
        },
        '12': function (n) {
          if (isBetween(n, 2, 4)) return 'few';
          if (n == 1) return 'one';
          return 'other';
        },
        '13': function (n) {
          if (isBetween(n % 10, 2, 4) && !isBetween(n % 100, 12, 14)) return 'few';
          if (n != 1 && isBetween(n % 10, 0, 1) || isBetween(n % 10, 5, 9) || isBetween(n % 100, 12, 14)) return 'many';
          if (n == 1) return 'one';
          return 'other';
        },
        '14': function (n) {
          if (isBetween(n % 100, 3, 4)) return 'few';
          if (n % 100 == 2) return 'two';
          if (n % 100 == 1) return 'one';
          return 'other';
        },
        '15': function (n) {
          if (n === 0 || isBetween(n % 100, 2, 10)) return 'few';
          if (isBetween(n % 100, 11, 19)) return 'many';
          if (n == 1) return 'one';
          return 'other';
        },
        '16': function (n) {
          if (n % 10 == 1 && n != 11) return 'one';
          return 'other';
        },
        '17': function (n) {
          if (n == 3) return 'few';
          if (n === 0) return 'zero';
          if (n == 6) return 'many';
          if (n == 2) return 'two';
          if (n == 1) return 'one';
          return 'other';
        },
        '18': function (n) {
          if (n === 0) return 'zero';
          if (isBetween(n, 0, 2) && n !== 0 && n != 2) return 'one';
          return 'other';
        },
        '19': function (n) {
          if (isBetween(n, 2, 10)) return 'few';
          if (isBetween(n, 0, 1)) return 'one';
          return 'other';
        },
        '20': function (n) {
          if ((isBetween(n % 10, 3, 4) || n % 10 == 9) && !(isBetween(n % 100, 10, 19) || isBetween(n % 100, 70, 79) || isBetween(n % 100, 90, 99))) return 'few';
          if (n % 1000000 === 0 && n !== 0) return 'many';
          if (n % 10 == 2 && !isIn(n % 100, [12, 72, 92])) return 'two';
          if (n % 10 == 1 && !isIn(n % 100, [11, 71, 91])) return 'one';
          return 'other';
        },
        '21': function (n) {
          if (n === 0) return 'zero';
          if (n == 1) return 'one';
          return 'other';
        },
        '22': function (n) {
          if (isBetween(n, 0, 1) || isBetween(n, 11, 99)) return 'one';
          return 'other';
        },
        '23': function (n) {
          if (isBetween(n % 10, 1, 2) || n % 20 === 0) return 'one';
          return 'other';
        },
        '24': function (n) {
          if (isBetween(n, 3, 10) || isBetween(n, 13, 19)) return 'few';
          if (isIn(n, [2, 12])) return 'two';
          if (isIn(n, [1, 11])) return 'one';
          return 'other';
        }
      };
      var index = locales2rules[lang.replace(/-.*$/, '')];
      if (!(index in pluralRules)) {
        console.warn('plural form unknown for [' + lang + ']');
        return function () {
          return 'other';
        };
      }
      return pluralRules[index];
    }
    gMacros.plural = function (str, param, key, prop) {
      var n = parseFloat(param);
      if (isNaN(n)) return str;
      if (prop != gTextProp) return str;
      if (!gMacros._pluralRules) {
        gMacros._pluralRules = getPluralRules(gLanguage);
      }
      var index = '[' + gMacros._pluralRules(n) + ']';
      if (n === 0 && key + '[zero]' in gL10nData) {
        str = gL10nData[key + '[zero]'][prop];
      } else if (n == 1 && key + '[one]' in gL10nData) {
        str = gL10nData[key + '[one]'][prop];
      } else if (n == 2 && key + '[two]' in gL10nData) {
        str = gL10nData[key + '[two]'][prop];
      } else if (key + index in gL10nData) {
        str = gL10nData[key + index][prop];
      } else if (key + '[other]' in gL10nData) {
        str = gL10nData[key + '[other]'][prop];
      }
      return str;
    };
    function getL10nData(key, args, fallback) {
      var data = gL10nData[key];
      if (!data) {
        console.warn('#' + key + ' is undefined.');
        if (!fallback) {
          return null;
        }
        data = fallback;
      }
      var rv = {};
      for (var prop in data) {
        var str = data[prop];
        str = substIndexes(str, args, key, prop);
        str = substArguments(str, args, key);
        rv[prop] = str;
      }
      return rv;
    }
    function substIndexes(str, args, key, prop) {
      var reIndex = /\{\[\s*([a-zA-Z]+)\(([a-zA-Z]+)\)\s*\]\}/;
      var reMatch = reIndex.exec(str);
      if (!reMatch || !reMatch.length) return str;
      var macroName = reMatch[1];
      var paramName = reMatch[2];
      var param;
      if (args && paramName in args) {
        param = args[paramName];
      } else if (paramName in gL10nData) {
        param = gL10nData[paramName];
      }
      if (macroName in gMacros) {
        var macro = gMacros[macroName];
        str = macro(str, param, key, prop);
      }
      return str;
    }
    function substArguments(str, args, key) {
      var reArgs = /\{\{\s*(.+?)\s*\}\}/g;
      return str.replace(reArgs, function (matched_text, arg) {
        if (args && arg in args) {
          return args[arg];
        }
        if (arg in gL10nData) {
          return gL10nData[arg];
        }
        console.log('argument {{' + arg + '}} for #' + key + ' is undefined.');
        return matched_text;
      });
    }
    function translateElement(element) {
      var l10n = getL10nAttributes(element);
      if (!l10n.id) return;
      var data = getL10nData(l10n.id, l10n.args);
      if (!data) {
        console.warn('#' + l10n.id + ' is undefined.');
        return;
      }
      if (data[gTextProp]) {
        if (getChildElementCount(element) === 0) {
          element[gTextProp] = data[gTextProp];
        } else {
          var children = element.childNodes;
          var found = false;
          for (var i = 0, l = children.length; i < l; i++) {
            if (children[i].nodeType === 3 && /\S/.test(children[i].nodeValue)) {
              if (found) {
                children[i].nodeValue = '';
              } else {
                children[i].nodeValue = data[gTextProp];
                found = true;
              }
            }
          }
          if (!found) {
            var textNode = document.createTextNode(data[gTextProp]);
            element.prepend(textNode);
          }
        }
        delete data[gTextProp];
      }
      for (var k in data) {
        element[k] = data[k];
      }
    }
    function getChildElementCount(element) {
      if (element.children) {
        return element.children.length;
      }
      if (typeof element.childElementCount !== 'undefined') {
        return element.childElementCount;
      }
      var count = 0;
      for (var i = 0; i < element.childNodes.length; i++) {
        count += element.nodeType === 1 ? 1 : 0;
      }
      return count;
    }
    function translateFragment(element) {
      element = element || document.documentElement;
      var children = getTranslatableChildren(element);
      var elementCount = children.length;
      for (var i = 0; i < elementCount; i++) {
        translateElement(children[i]);
      }
      translateElement(element);
    }
    return {
      get: function (key, args, fallbackString) {
        var index = key.lastIndexOf('.');
        var prop = gTextProp;
        if (index > 0) {
          prop = key.substring(index + 1);
          key = key.substring(0, index);
        }
        var fallback;
        if (fallbackString) {
          fallback = {};
          fallback[prop] = fallbackString;
        }
        var data = getL10nData(key, args, fallback);
        if (data && prop in data) {
          return data[prop];
        }
        return '{{' + key + '}}';
      },
      getData: function () {
        return gL10nData;
      },
      getText: function () {
        return gTextData;
      },
      getLanguage: function () {
        return gLanguage;
      },
      setLanguage: function (lang, callback) {
        loadLocale(lang, function () {
          if (callback) callback();
        });
      },
      getDirection: function () {
        var rtlList = ['ar', 'he', 'fa', 'ps', 'ur'];
        var shortCode = gLanguage.split('-', 1)[0];
        return rtlList.indexOf(shortCode) >= 0 ? 'rtl' : 'ltr';
      },
      translate: translateFragment,
      getReadyState: function () {
        return gReadyState;
      },
      ready: function (callback) {
        if (!callback) {
          return;
        } else if (gReadyState == 'complete' || gReadyState == 'interactive') {
          window.setTimeout(function () {
            callback();
          });
        } else if (document.addEventListener) {
          document.addEventListener('localized', function once() {
            document.removeEventListener('localized', once);
            callback();
          });
        }
      }
    };
  }(window, document);
  
  /***/ }),
  /* 229 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.GenericScripting = void 0;
  exports.docProperties = docProperties;
  __webpack_require__(2);
  var _pdfjsLib = __webpack_require__(182);
  async function docProperties(pdfDocument) {
    const url = "",
      baseUrl = url.split("#")[0];
    let {
      info,
      metadata,
      contentDispositionFilename,
      contentLength
    } = await pdfDocument.getMetadata();
    if (!contentLength) {
      const {
        length
      } = await pdfDocument.getDownloadInfo();
      contentLength = length;
    }
    return {
      ...info,
      baseURL: baseUrl,
      filesize: contentLength,
      filename: contentDispositionFilename || (0, _pdfjsLib.getPdfFilenameFromUrl)(url),
      metadata: metadata === null || metadata === void 0 ? void 0 : metadata.getRaw(),
      authors: metadata === null || metadata === void 0 ? void 0 : metadata.get("dc:creator"),
      numPages: pdfDocument.numPages,
      URL: url
    };
  }
  class GenericScripting {
    constructor(sandboxBundleSrc) {
      this._ready = (0, _pdfjsLib.loadScript)(sandboxBundleSrc, true).then(() => {
        return window.pdfjsSandbox.QuickJSSandbox();
      });
    }
    async createSandbox(data) {
      const sandbox = await this._ready;
      sandbox.create(data);
    }
    async dispatchEventInSandbox(event) {
      const sandbox = await this._ready;
      setTimeout(() => sandbox.dispatchEvent(event), 0);
    }
    async destroySandbox() {
      const sandbox = await this._ready;
      sandbox.nukeSandbox();
    }
  }
  exports.GenericScripting = GenericScripting;
  
  /***/ }),
  /* 230 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.PDFPrintService = void 0;
  __webpack_require__(2);
  __webpack_require__(145);
  __webpack_require__(146);
  __webpack_require__(147);
  __webpack_require__(122);
  var _pdfjsLib = __webpack_require__(182);
  var _app = __webpack_require__(121);
  var _print_utils = __webpack_require__(231);
  let activeService = null;
  let dialog = null;
  let overlayManager = null;
  function renderPage(activeServiceOnEntry, pdfDocument, pageNumber, size, printResolution, optionalContentConfigPromise, printAnnotationStoragePromise) {
    const scratchCanvas = activeService.scratchCanvas;
    const PRINT_UNITS = printResolution / _pdfjsLib.PixelsPerInch.PDF;
    scratchCanvas.width = Math.floor(size.width * PRINT_UNITS);
    scratchCanvas.height = Math.floor(size.height * PRINT_UNITS);
    const ctx = scratchCanvas.getContext("2d");
    ctx.save();
    ctx.fillStyle = "rgb(255, 255, 255)";
    ctx.fillRect(0, 0, scratchCanvas.width, scratchCanvas.height);
    ctx.restore();
    return Promise.all([pdfDocument.getPage(pageNumber), printAnnotationStoragePromise]).then(function (_ref) {
      let [pdfPage, printAnnotationStorage] = _ref;
      const renderContext = {
        canvasContext: ctx,
        transform: [PRINT_UNITS, 0, 0, PRINT_UNITS, 0, 0],
        viewport: pdfPage.getViewport({
          scale: 1,
          rotation: size.rotation
        }),
        intent: "print",
        annotationMode: _pdfjsLib.AnnotationMode.ENABLE_STORAGE,
        optionalContentConfigPromise,
        printAnnotationStorage
      };
      return pdfPage.render(renderContext).promise;
    });
  }
  class PDFPrintService {
    constructor(pdfDocument, pagesOverview, printContainer, printResolution) {
      let optionalContentConfigPromise = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : null;
      let printAnnotationStoragePromise = arguments.length > 5 && arguments[5] !== undefined ? arguments[5] : null;
      let l10n = arguments.length > 6 ? arguments[6] : undefined;
      this.pdfDocument = pdfDocument;
      this.pagesOverview = pagesOverview;
      this.printContainer = printContainer;
      this._printResolution = printResolution || 150;
      this._optionalContentConfigPromise = optionalContentConfigPromise || pdfDocument.getOptionalContentConfig();
      this._printAnnotationStoragePromise = printAnnotationStoragePromise || Promise.resolve();
      this.l10n = l10n;
      this.currentPage = -1;
      this.scratchCanvas = document.createElement("canvas");
    }
    layout() {
      this.throwIfInactive();
      const body = document.querySelector("body");
      body.setAttribute("data-pdfjsprinting", true);
      const {
        width,
        height
      } = this.pagesOverview[0];
      const hasEqualPageSizes = this.pagesOverview.every(size => size.width === width && size.height === height);
      if (!hasEqualPageSizes) {
        console.warn("Not all pages have the same size. The printed result may be incorrect!");
      }
      this.pageStyleSheet = document.createElement("style");
      this.pageStyleSheet.textContent = `@page { size: ${width}pt ${height}pt;}`;
      body.append(this.pageStyleSheet);
    }
    destroy() {
      if (activeService !== this) {
        return;
      }
      this.printContainer.textContent = "";
      const body = document.querySelector("body");
      body.removeAttribute("data-pdfjsprinting");
      if (this.pageStyleSheet) {
        this.pageStyleSheet.remove();
        this.pageStyleSheet = null;
      }
      this.scratchCanvas.width = this.scratchCanvas.height = 0;
      this.scratchCanvas = null;
      activeService = null;
      ensureOverlay().then(function () {
        if (overlayManager.active === dialog) {
          overlayManager.close(dialog);
        }
      });
    }
    renderPages() {
      if (this.pdfDocument.isPureXfa) {
        (0, _print_utils.getXfaHtmlForPrinting)(this.printContainer, this.pdfDocument);
        return Promise.resolve();
      }
      const pageCount = this.pagesOverview.length;
      const renderNextPage = (resolve, reject) => {
        this.throwIfInactive();
        if (++this.currentPage >= pageCount) {
          renderProgress(pageCount, pageCount, this.l10n);
          resolve();
          return;
        }
        const index = this.currentPage;
        renderProgress(index, pageCount, this.l10n);
        renderPage(this, this.pdfDocument, index + 1, this.pagesOverview[index], this._printResolution, this._optionalContentConfigPromise, this._printAnnotationStoragePromise).then(this.useRenderedPage.bind(this)).then(function () {
          renderNextPage(resolve, reject);
        }, reject);
      };
      return new Promise(renderNextPage);
    }
    useRenderedPage() {
      this.throwIfInactive();
      const img = document.createElement("img");
      const scratchCanvas = this.scratchCanvas;
      if ("toBlob" in scratchCanvas) {
        scratchCanvas.toBlob(function (blob) {
          img.src = URL.createObjectURL(blob);
        });
      } else {
        img.src = scratchCanvas.toDataURL();
      }
      const wrapper = document.createElement("div");
      wrapper.className = "printedPage";
      wrapper.append(img);
      this.printContainer.append(wrapper);
      return new Promise(function (resolve, reject) {
        img.onload = resolve;
        img.onerror = reject;
      });
    }
    performPrint() {
      this.throwIfInactive();
      return new Promise(resolve => {
        setTimeout(() => {
          if (!this.active) {
            resolve();
            return;
          }
          print.call(window);
          setTimeout(resolve, 20);
        }, 0);
      });
    }
    get active() {
      return this === activeService;
    }
    throwIfInactive() {
      if (!this.active) {
        throw new Error("This print request was cancelled or completed.");
      }
    }
  }
  exports.PDFPrintService = PDFPrintService;
  const print = window.print;
  window.print = function () {
    if (activeService) {
      console.warn("Ignored window.print() because of a pending print job.");
      return;
    }
    ensureOverlay().then(function () {
      if (activeService) {
        overlayManager.open(dialog);
      }
    });
    try {
      dispatchEvent("beforeprint");
    } finally {
      if (!activeService) {
        console.error("Expected print service to be initialized.");
        ensureOverlay().then(function () {
          if (overlayManager.active === dialog) {
            overlayManager.close(dialog);
          }
        });
        return;
      }
      const activeServiceOnEntry = activeService;
      activeService.renderPages().then(function () {
        return activeServiceOnEntry.performPrint();
      }).catch(function () {}).then(function () {
        if (activeServiceOnEntry.active) {
          abort();
        }
      });
    }
  };
  function dispatchEvent(eventType) {
    const event = new CustomEvent(eventType, {
      bubbles: false,
      cancelable: false,
      detail: "custom"
    });
    window.dispatchEvent(event);
  }
  function abort() {
    if (activeService) {
      activeService.destroy();
      dispatchEvent("afterprint");
    }
  }
  function renderProgress(index, total, l10n) {
    dialog || (dialog = document.getElementById("printServiceDialog"));
    const progress = Math.round(100 * index / total);
    const progressBar = dialog.querySelector("progress");
    const progressPerc = dialog.querySelector(".relative-progress");
    progressBar.value = progress;
    l10n.get("print_progress_percent", {
      progress
    }).then(msg => {
      progressPerc.textContent = msg;
    });
  }
  window.addEventListener("keydown", function (event) {
    if (event.keyCode === 80 && (event.ctrlKey || event.metaKey) && !event.altKey && (!event.shiftKey || window.chrome || window.opera)) {
      window.print();
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  }, true);
  if ("onbeforeprint" in window) {
    const stopPropagationIfNeeded = function (event) {
      if (event.detail !== "custom") {
        event.stopImmediatePropagation();
      }
    };
    window.addEventListener("beforeprint", stopPropagationIfNeeded);
    window.addEventListener("afterprint", stopPropagationIfNeeded);
  }
  let overlayPromise;
  function ensureOverlay() {
    if (!overlayPromise) {
      overlayManager = _app.PDFViewerApplication.overlayManager;
      if (!overlayManager) {
        throw new Error("The overlay manager has not yet been initialized.");
      }
      dialog || (dialog = document.getElementById("printServiceDialog"));
      overlayPromise = overlayManager.register(dialog, true);
      document.getElementById("printCancel").onclick = abort;
      dialog.addEventListener("close", abort);
    }
    return overlayPromise;
  }
  _app.PDFPrintServiceFactory.instance = {
    supportsPrinting: true,
    createPrintService(pdfDocument, pagesOverview, printContainer, printResolution, optionalContentConfigPromise, printAnnotationStoragePromise, l10n) {
      if (activeService) {
        throw new Error("The print service is created and active.");
      }
      activeService = new PDFPrintService(pdfDocument, pagesOverview, printContainer, printResolution, optionalContentConfigPromise, printAnnotationStoragePromise, l10n);
      return activeService;
    }
  };
  
  /***/ }),
  /* 231 */
  /***/ ((__unused_webpack_module, exports, __webpack_require__) => {
  
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  exports.getXfaHtmlForPrinting = getXfaHtmlForPrinting;
  var _pdfjsLib = __webpack_require__(182);
  var _pdf_link_service = __webpack_require__(185);
  var _xfa_layer_builder = __webpack_require__(221);
  function getXfaHtmlForPrinting(printContainer, pdfDocument) {
    const xfaHtml = pdfDocument.allXfaHtml;
    const linkService = new _pdf_link_service.SimpleLinkService();
    const scale = Math.round(_pdfjsLib.PixelsPerInch.PDF_TO_CSS_UNITS * 100) / 100;
    for (const xfaPage of xfaHtml.children) {
      const page = document.createElement("div");
      page.className = "xfaPrintedPage";
      printContainer.append(page);
      const builder = new _xfa_layer_builder.XfaLayerBuilder({
        pageDiv: page,
        pdfPage: null,
        annotationStorage: pdfDocument.annotationStorage,
        linkService,
        xfaHtml: xfaPage
      });
      const viewport = (0, _pdfjsLib.getXfaPageViewport)(xfaPage, {
        scale
      });
      builder.render(viewport, "print");
    }
  }
  
  /***/ })
  /******/ 	]);
  /************************************************************************/
  /******/ 	// The module cache
  /******/ 	var __webpack_module_cache__ = {};
  /******/ 	
  /******/ 	// The require function
  /******/ 	function __webpack_require__(moduleId) {
  /******/ 		// Check if module is in cache
  /******/ 		var cachedModule = __webpack_module_cache__[moduleId];
  /******/ 		if (cachedModule !== undefined) {
  /******/ 			return cachedModule.exports;
  /******/ 		}
  /******/ 		// Create a new module (and put it into the cache)
  /******/ 		var module = __webpack_module_cache__[moduleId] = {
  /******/ 			// no module.id needed
  /******/ 			// no module.loaded needed
  /******/ 			exports: {}
  /******/ 		};
  /******/ 	
  /******/ 		// Execute the module function
  /******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
  /******/ 	
  /******/ 		// Return the exports of the module
  /******/ 		return module.exports;
  /******/ 	}
  /******/ 	
  /************************************************************************/
  var __webpack_exports__ = {};
  // This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
  (() => {
  var exports = __webpack_exports__;
  
  
  Object.defineProperty(exports, "__esModule", ({
    value: true
  }));
  Object.defineProperty(exports, "PDFViewerApplication", ({
    enumerable: true,
    get: function () {
      return _app.PDFViewerApplication;
    }
  }));
  exports.PDFViewerApplicationConstants = void 0;
  Object.defineProperty(exports, "PDFViewerApplicationOptions", ({
    enumerable: true,
    get: function () {
      return _app_options.AppOptions;
    }
  }));
  __webpack_require__(1);
  __webpack_require__(230);
  var _ui_utils = __webpack_require__(148);
  var _app_options = __webpack_require__(183);
  var _pdf_link_service = __webpack_require__(185);
  var _app = __webpack_require__(121);
  var _document$blockUnbloc, _document;
  const pdfjsVersion = '3.11.176';
  const pdfjsBuild = 'd413cf835';
  const AppConstants = {
    LinkTarget: _pdf_link_service.LinkTarget,
    RenderingStates: _ui_utils.RenderingStates,
    ScrollMode: _ui_utils.ScrollMode,
    SpreadMode: _ui_utils.SpreadMode
  };
  exports.PDFViewerApplicationConstants = AppConstants;
  window.PDFViewerApplication = _app.PDFViewerApplication;
  window.PDFViewerApplicationConstants = AppConstants;
  window.PDFViewerApplicationOptions = _app_options.AppOptions;
  function getViewerConfiguration() {
    return {
      appContainer: document.body,
      mainContainer: document.getElementById("viewerContainer"),
      viewerContainer: document.getElementById("viewer"),
      toolbar: {
        container: document.getElementById("toolbarViewer"),
        numPages: document.getElementById("numPages"),
        pageNumber: document.getElementById("pageNumber"),
        scaleSelect: document.getElementById("scaleSelect"),
        customScaleOption: document.getElementById("customScaleOption"),
        previous: document.getElementById("previous"),
        next: document.getElementById("next"),
        zoomIn: document.getElementById("zoomIn"),
        zoomOut: document.getElementById("zoomOut"),
        viewFind: document.getElementById("viewFind"),
        openFile: document.getElementById("openFile"),
        print: document.getElementById("print"),
        editorFreeTextButton: document.getElementById("editorFreeText"),
        editorFreeTextParamsToolbar: document.getElementById("editorFreeTextParamsToolbar"),
        editorInkButton: document.getElementById("editorInk"),
        editorInkParamsToolbar: document.getElementById("editorInkParamsToolbar"),
        editorStampButton: document.getElementById("editorStamp"),
        editorStampParamsToolbar: document.getElementById("editorStampParamsToolbar"),
        download: document.getElementById("download")
      },
      secondaryToolbar: {
        toolbar: document.getElementById("secondaryToolbar"),
        toggleButton: document.getElementById("secondaryToolbarToggle"),
        presentationModeButton: document.getElementById("presentationMode"),
        openFileButton: document.getElementById("secondaryOpenFile"),
        printButton: document.getElementById("secondaryPrint"),
        downloadButton: document.getElementById("secondaryDownload"),
        viewBookmarkButton: document.getElementById("viewBookmark"),
        firstPageButton: document.getElementById("firstPage"),
        lastPageButton: document.getElementById("lastPage"),
        pageRotateCwButton: document.getElementById("pageRotateCw"),
        pageRotateCcwButton: document.getElementById("pageRotateCcw"),
        cursorSelectToolButton: document.getElementById("cursorSelectTool"),
        cursorHandToolButton: document.getElementById("cursorHandTool"),
        scrollPageButton: document.getElementById("scrollPage"),
        scrollVerticalButton: document.getElementById("scrollVertical"),
        scrollHorizontalButton: document.getElementById("scrollHorizontal"),
        scrollWrappedButton: document.getElementById("scrollWrapped"),
        spreadNoneButton: document.getElementById("spreadNone"),
        spreadOddButton: document.getElementById("spreadOdd"),
        spreadEvenButton: document.getElementById("spreadEven"),
        documentPropertiesButton: document.getElementById("documentProperties")
      },
      sidebar: {
        outerContainer: document.getElementById("outerContainer"),
        sidebarContainer: document.getElementById("sidebarContainer"),
        toggleButton: document.getElementById("sidebarToggle"),
        resizer: document.getElementById("sidebarResizer"),
        thumbnailButton: document.getElementById("viewThumbnail"),
        outlineButton: document.getElementById("viewOutline"),
        attachmentsButton: document.getElementById("viewAttachments"),
        layersButton: document.getElementById("viewLayers"),
        thumbnailView: document.getElementById("thumbnailView"),
        outlineView: document.getElementById("outlineView"),
        attachmentsView: document.getElementById("attachmentsView"),
        layersView: document.getElementById("layersView"),
        outlineOptionsContainer: document.getElementById("outlineOptionsContainer"),
        currentOutlineItemButton: document.getElementById("currentOutlineItem")
      },
      findBar: {
        bar: document.getElementById("findbar"),
        toggleButton: document.getElementById("viewFind"),
        findField: document.getElementById("findInput"),
        highlightAllCheckbox: document.getElementById("findHighlightAll"),
        caseSensitiveCheckbox: document.getElementById("findMatchCase"),
        matchDiacriticsCheckbox: document.getElementById("findMatchDiacritics"),
        entireWordCheckbox: document.getElementById("findEntireWord"),
        findMsg: document.getElementById("findMsg"),
        findResultsCount: document.getElementById("findResultsCount"),
        findPreviousButton: document.getElementById("findPrevious"),
        findNextButton: document.getElementById("findNext")
      },
      passwordOverlay: {
        dialog: document.getElementById("passwordDialog"),
        label: document.getElementById("passwordText"),
        input: document.getElementById("password"),
        submitButton: document.getElementById("passwordSubmit"),
        cancelButton: document.getElementById("passwordCancel")
      },
      documentProperties: {
        dialog: document.getElementById("documentPropertiesDialog"),
        closeButton: document.getElementById("documentPropertiesClose"),
        fields: {
          fileName: document.getElementById("fileNameField"),
          fileSize: document.getElementById("fileSizeField"),
          title: document.getElementById("titleField"),
          author: document.getElementById("authorField"),
          subject: document.getElementById("subjectField"),
          keywords: document.getElementById("keywordsField"),
          creationDate: document.getElementById("creationDateField"),
          modificationDate: document.getElementById("modificationDateField"),
          creator: document.getElementById("creatorField"),
          producer: document.getElementById("producerField"),
          version: document.getElementById("versionField"),
          pageCount: document.getElementById("pageCountField"),
          pageSize: document.getElementById("pageSizeField"),
          linearized: document.getElementById("linearizedField")
        }
      },
      altTextDialog: {
        dialog: document.getElementById("altTextDialog"),
        optionDescription: document.getElementById("descriptionButton"),
        optionDecorative: document.getElementById("decorativeButton"),
        textarea: document.getElementById("descriptionTextarea"),
        cancelButton: document.getElementById("altTextCancel"),
        saveButton: document.getElementById("altTextSave")
      },
      annotationEditorParams: {
        editorFreeTextFontSize: document.getElementById("editorFreeTextFontSize"),
        editorFreeTextColor: document.getElementById("editorFreeTextColor"),
        editorInkColor: document.getElementById("editorInkColor"),
        editorInkThickness: document.getElementById("editorInkThickness"),
        editorInkOpacity: document.getElementById("editorInkOpacity"),
        editorStampAddImage: document.getElementById("editorStampAddImage")
      },
      printContainer: document.getElementById("printContainer"),
      openFileInput: document.getElementById("fileInput"),
      debuggerScriptPath: "./debugger.js"
    };
  }
  function webViewerLoad() {
    return "ERP5 patch: disable here";
    const config = getViewerConfiguration();
    const event = new CustomEvent("webviewerloaded", {
      bubbles: true,
      cancelable: true,
      detail: {
        source: window
      }
    });
    try {
      parent.document.dispatchEvent(event);
    } catch (ex) {
      console.error(`webviewerloaded: ${ex}`);
      document.dispatchEvent(event);
    }
    _app.PDFViewerApplication.run(config);
  }
  (_document$blockUnbloc = (_document = document).blockUnblockOnload) === null || _document$blockUnbloc === void 0 || _document$blockUnbloc.call(_document, true);
  if (document.readyState === "interactive" || document.readyState === "complete") {
    webViewerLoad();
  } else {
    document.addEventListener("DOMContentLoaded", webViewerLoad, true);
  }
  })();
  
  /******/ })()
  ;
  //# sourceMappingURL=viewer.js.map