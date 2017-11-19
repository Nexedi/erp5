/*jslint browser:true, indent:2*/
/*global define, require*/ // Require.JS

define(function () {
  'use strict';

  return {
    /**
     * @param {String} name This is the name of the desired resource module.
     * @param {Function} req Provides a "require" to load other modules.
     * @param {Function} load Pass the module's result to this function.
     * @param {Object} config Provides the optimizer's configuration.
     */
    load: function (name, req, load) { // , config
      req([name], function (result) {
        if (typeof(window) !== 'undefined') {
          window[name] = result;
        }
        load(result);
      });
    }
  };
});
