define([
    'common/main/lib/component/Window',
    'common/main/lib/component/LoadMask'
], function () {
    'use strict';
    Common.Views.RenderJSDialog = Common.UI.Window.extend(_.extend({
        initialize : function(options) {
            var _options = {};
            _.extend(_options,  {
                title: this.textTitle,
                width: 1024,
                height: 621,
                header: true
            }, options);

            this.template = [
                '<div id="<%= scope %>"></div>'
            ].join('');

            _options.tpl = _.template(this.template)(_options);

            Common.UI.Window.prototype.initialize.call(this, _options);
        },

        render: function() {
            var q,
                me = this,
                element;
            Common.UI.Window.prototype.render.call(this);
            element = document.getElementById(this.options.scope);
            this.$window.find('> .body').css({height: 'auto', overflow: 'hidden'});

            // this.loadMask = new Common.UI.LoadMask({owner: $(element)});
            // this.loadMask.setTitle(this.textLoading);
            // this.loadMask.show();

            if (!me.gadget) {
                q = Common.Gateway.declareGadget(this.options.gadget_url, {
                    scope: this.options.scope,
                    element: element,
                    sandbox: "iframe"
                })
                    .push(function (sub_gadget) {
                        me.gadget = sub_gadget;
                        var iframe = sub_gadget.element.querySelector("iframe");
                        iframe.width        = '100%';
                        iframe.height       = "585px";
                        iframe.setAttribute("frameBorder","0");
                        // iframe.style = "border: none;";
                        // iframe.align        = "top";
                        // iframe.scrolling    = "no";

                        // this._eventfunc = function(msg) {
                        //     me._onWindowMessage(msg);
                        // };
                        // this._bindWindowEvents.call(this);
                        //
                        // this.on('close', function(obj){
                        //     me._unbindWindowEvents();
                        // });
                    });
            } else {
                q = RSVP.Queue();
            }
            return q.push(function () {
                return me.gadget.render(me.options.gadget_render_opt);
            })
                .push(undefined, function () {
                    // XXX
                    return;
                })
                .push(function () {
                    me._onLoad();
                });
        },

        _bindWindowEvents: function() {
            if (window.addEventListener) {
                window.addEventListener("message", this._eventfunc, false);
            } else if (window.attachEvent) {
                window.attachEvent("onmessage", this._eventfunc);
            }
        },

        _unbindWindowEvents: function() {
            if (window.removeEventListener) {
                window.removeEventListener("message", this._eventfunc);
            } else if (window.detachEvent) {
                window.detachEvent("onmessage", this._eventfunc);
            }
        },

        _onWindowMessage: function(msg) {
            // TODO: check message origin
            if (msg && window.JSON) {
                try {
                    this._onMessage.call(this, window.JSON.parse(msg.data));
                } catch(e) {}
            }
        },

        _onMessage: function(msg) {
            if (msg && msg.file !== undefined) {
                Common.NotificationCenter.trigger('window:close', this);
                var me = this;
                setTimeout(function() {
                    if ( !_.isEmpty(msg.file) ) {
                        me.trigger('mailmergerecepients', me, msg.file);
                    }
                }, 50);
            }
        },

        _onLoad: function() {
            if (this.loadMask)
                this.loadMask.hide();
        },

        textTitle   : 'Select Data Source',
        textLoading : 'Loading'
    }, Common.Views.RenderJSDialog || {}));

});
