/*
 *
 * (c) Copyright Ascensio System Limited 2010-2017
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation. In accordance with
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 * that Ascensio System SIA expressly excludes the warranty of non-infringement
 * of any third-party rights.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,
 * EU, LV-1021.
 *
 * The  interactive user interfaces in modified source and object code versions
 * of the Program must display Appropriate Legal Notices, as required under
 * Section 5 of the GNU AGPL version 3.
 *
 * Pursuant to Section 7(b) of the License you must retain the original Product
 * logo when distributing the program. Pursuant to Section 7(e) we decline to
 * grant you any rights under trademark law for use of our trademarks.
 *
 * All the Product's GUI elements, including illustrations and icon sets, as
 * well as technical writing content are licensed under the terms of the
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
*/
/**
 *  Statusbar.js
 *
 *  Statusbar controller
 *
 *  Created by Maxim Kadushkin on 8 April 2014
 *  Copyright (c) 2014 Ascensio System SIA. All rights reserved.
 *
 */

define([
    'core',
    'presentationeditor/main/app/view/Statusbar'
], function () {
    'use strict';

    PE.Controllers.Statusbar = Backbone.Controller.extend(_.extend({
        models: [],
        collections: [],
        views: [
            'Statusbar'
        ],

        initialize: function() {
            this.addListeners({
                'Statusbar': {
                }
            });
            this._state = {
                zoom_type: undefined,
                zoom_percent: undefined
            };
        },

        events: function() {
            return {
                'click #btn-zoom-down': _.bind(this.zoomDocument,this,'down'),
                'click #btn-zoom-up': _.bind(this.zoomDocument,this,'up')
            };
        },

        onLaunch: function() {
            this.statusbar = this.createView('Statusbar', {
                storeUsers: this.getApplication().getCollection('Common.Collections.Users')
            }).render();
            this.statusbar.$el.css('z-index', 1);

            this.bindViewEvents(this.statusbar, this.events);

            $('#status-label-zoom').css('min-width', 70);

            this.statusbar.btnZoomToPage.on('click', _.bind(this.onBtnZoomTo, this, 'topage'));
            this.statusbar.btnZoomToWidth.on('click', _.bind(this.onBtnZoomTo, this, 'towidth'));
            this.statusbar.zoomMenu.on('item:click', _.bind(this.menuZoomClick, this));
            this.statusbar.btnPreview.on('click', _.bind(this.onPreview, this));
        },

        setApi: function(api) {
            this.api = api;
            this.api.asc_registerCallback('asc_onZoomChange',   _.bind(this._onZoomChange, this));

            this.statusbar.setApi(api);
        },

        onBtnZoomTo: function(d, b, e) {
            this._state.zoom_type = undefined;
            this._state.zoom_percent = undefined;
            if (!b.pressed)
                this.api.zoomCustomMode(); else
                this.api[d=='topage'?'zoomFitToPage':'zoomFitToWidth']();
            Common.NotificationCenter.trigger('edit:complete', this.statusbar);
        },

        zoomDocument: function(d, e) {
            this._state.zoom_type = undefined;
            this._state.zoom_percent = undefined;
            switch (d) {
                case 'up':      this.api.zoomIn(); break;
                case 'down':    this.api.zoomOut(); break;
            }
            Common.NotificationCenter.trigger('edit:complete', this.statusbar);
        },

        menuZoomClick: function(menu, item) {
            this._state.zoom_type = undefined;
            this._state.zoom_percent = undefined;
            this.api.zoom(item.value);
            Common.NotificationCenter.trigger('edit:complete', this.statusbar);
        },

        onPreview: function(btn, e) {
            var previewPanel = PE.getController('Viewport').getView('DocumentPreview'),
                me = this,
                isResized = false;
            if (previewPanel && me.api) {
                previewPanel.show();
                var onWindowResize = function() {
                    if (isResized) return;
                    isResized = true;
                    Common.NotificationCenter.off('window:resize', onWindowResize);

                    var current = me.api.getCurrentPage();
                    me.api.StartDemonstration('presentation-preview', _.isNumber(current) ? current : 0);

                    Common.component.Analytics.trackEvent('Status Bar', 'Preview');
                };
                if (!me.statusbar.mode.isDesktopApp && !Common.Utils.isIE11) {
                    Common.NotificationCenter.on('window:resize', onWindowResize);
                    me.fullScreen(document.documentElement);
                    setTimeout(function(){
                        onWindowResize();
                    }, 100);
                } else
                    onWindowResize();
            }
        },

        fullScreen: function(element) {
            if (element) {
                if(element.requestFullscreen) {
                    element.requestFullscreen();
                } else if(element.webkitRequestFullscreen) {
                    element.webkitRequestFullscreen();
                } else if(element.mozRequestFullScreen) {
                    element.mozRequestFullScreen();
                } else if(element.msRequestFullscreen) {
                    element.msRequestFullscreen();
                }
            }
        },

        /*
        *   api events
        * */

         _onZoomChange: function(percent, type) {
             if (this._state.zoom_type !== type) {
                 this.statusbar.btnZoomToPage.toggle(type == 2, true);
                 this.statusbar.btnZoomToWidth.toggle(type == 1, true);
                 this._state.zoom_type = type;
             }
             if (this._state.zoom_percent !== percent) {
                 $('#status-label-zoom').text(Common.Utils.String.format(this.zoomText, percent));
                 this._state.zoom_percent = percent;
             }
        },

        setStatusCaption: function(text, force, delay) {
            if (this.timerCaption && ( ((new Date()) < this.timerCaption) || text.length==0 ) && !force )
                return;

            this.timerCaption = undefined;
            if (text.length) {
                this.statusbar.showStatusMessage(text);
                if (delay>0)
                    this.timerCaption = (new Date()).getTime() + delay;
            } else
                this.statusbar.clearStatusMessage();
        },

        createDelayedElements: function() {
            this.statusbar.$el.css('z-index', '');
        },

        zoomText        : 'Zoom {0}%'
    }, PE.Controllers.Statusbar || {}));
});