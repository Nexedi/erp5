/*global RSVP, FileReader, renderJS */
/*jslint unparam: true */
(function(window, RSVP, FileReader, renderJS) {
    "use strict";
    window.loopEventListener = renderJS.loopEventListener;

    window.promiseEventListener = function(target, type, useCapture) {
        //////////////////////////
        // Resolve the promise as soon as the event is triggered
        // eventListener is removed when promise is cancelled/resolved/rejected
        //////////////////////////
        var handle_event_callback;
        function canceller() {
            target.removeEventListener(type, handle_event_callback, useCapture);
        }
        function resolver(resolve) {
            handle_event_callback = function(evt) {
                canceller();
                evt.stopPropagation();
                evt.preventDefault();
                resolve(evt);
                return false;
            };
            target.addEventListener(type, handle_event_callback, useCapture);
        }
        return new RSVP.Promise(resolver, canceller);
    };
    window.promiseReadAsText = function(file) {
        return new RSVP.Promise(function(resolve, reject) {
            var reader = new FileReader();
            reader.onload = function(evt) {
                resolve(evt.target.result);
            };
            reader.onerror = function(evt) {
                reject(evt);
            };
            reader.readAsText(file);
        });
    };
})(window, RSVP, FileReader, renderJS);