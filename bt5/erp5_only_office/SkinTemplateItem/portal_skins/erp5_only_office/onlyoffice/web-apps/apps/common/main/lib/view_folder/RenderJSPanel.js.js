/**
 * User: Julia.Radzhabova
 * Date: 17.05.16
 * Time: 15:38
 */

if (Common === undefined)
  var Common = {};

Common.Views = Common.Views || {};

define([
  'common/main/lib/util/utils',
  'common/main/lib/component/BaseView',
  'common/main/lib/component/Layout',
  'common/main/lib/component/Window'
], function (template) {
  'use strict';

  Common.Views.RenderJSPanel = Common.UI.BaseView.extend(_.extend({
    initialize: function (options) {
      _.extend(this, options);
      Common.UI.BaseView.prototype.initialize.call(this, arguments);
    },

    render: function () {
      var me = this,
        element = me.$el[0],
        q = RSVP.Queue();

      if (!me.gadget) {
        q = Common.Gateway.declareGadget(this.gadget_url, {
          scope: this.scope,
          element: element,
          sandbox: "iframe"
        })
          .push(function (sub_gadget) {
            me.gadget = sub_gadget;
            var iframe = sub_gadget.element.querySelector("iframe");
            iframe.width = '100%';
            iframe.height = (Common.Utils.innerHeight() - 80) + 'px';
            iframe.setAttribute("frameBorder", "0");
          });
      } else {
        q = RSVP.Queue();
      }
      return q.push(function () {
        return me.gadget.render(me.gadget_render_opt);
      })
        .push(function () {
          return me;
        })
        .push(undefined, function (e) {
          console.error(e);
        });

    },

    show: function () {
        Common.UI.BaseView.prototype.show.call(this,arguments);
        this.fireEvent('show', this );
    },

    hide: function () {
        Common.UI.BaseView.prototype.hide.call(this,arguments);
        this.fireEvent('hide', this );
    }

  }, Common.Views.RenderJSPanel || {}));
});