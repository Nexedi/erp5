/*
 *
 * (c) Copyright Ascensio System Limited 2010-2016
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
 *  Viewport.js
 *
 *  Viewport view
 *
 *  Created by Alexander Yuzhin on 12/27/13
 *  Copyright (c) 2013 Ascensio System SIA. All rights reserved.
 *
 */

define([
    'text!documenteditor/main/app/template/Viewport.template',
    'jquery',
    'underscore',
    'backbone',
    'common/main/lib/component/Layout'
], function (viewportTemplate, $, _, Backbone) {
    'use strict';

    DE.Views.Viewport = Backbone.View.extend({
        el: '#viewport',

        // Compile our stats template
        template: _.template(viewportTemplate),

        // Delegated events for creating new items, and clearing completed ones.
        events: {
        },

        // Set innerHTML and get the references to the DOM elements
        initialize: function() {
            //
        },

        // Render layout
        render: function() {
            var el = $(this.el);
            el.html(this.template({}));

            // Workaround Safari's scrolling problem
            if (Common.Utils.isSafari) {
                $('body').addClass('safari');
                $('body').mousewheel(function(e){
                    e.preventDefault();
                    e.stopPropagation();
                });
            } else if (Common.Utils.isChrome) {
                $('body').addClass('chrome');
            }

            var $container = $('#viewport-vbox-layout', el);
            var items = $container.find(' > .layout-item');
            this.vlayout = new Common.UI.VBoxLayout({
                box: $container,
                items: [{
                        el: items[0],
                        rely: true
                    }, {
                        el: items[1],
                        rely: true
                    }, {
                        el: items[2],
                        stretch: true
                    }, {
                        el: items[3],
                        height: 25
                    }
                ]
            });

            $container = $('#viewport-hbox-layout', el);
            items = $container.find(' > .layout-item');
            this.hlayout = new Common.UI.HBoxLayout({
                box: $container,
                items: [{ // left menu chat & comment
                        el: items[0],
                        rely: true,
                        resize: {
                            hidden: true,
                            autohide: false,
                            min: 300,
                            max: 600
                    }}, { // history versions
                        el: items[3],
                        rely: true,
                        resize: {
                                hidden: true,
                                autohide: false,
                                min: 300,
                                max: 600
                        }
                    }, { // sdk
                        el: items[1],
                        stretch: true
                    }, { // right menu
                        el: $(items[2]).hide(),
                        rely: true
                    }
                ]
            });

            return this;
        },

        applyEditorMode: function() {
            var me              = this,
                toolbarView     = DE.getController('Toolbar').getView('Toolbar'),
                rightMenuView   = DE.getController('RightMenu').getView('RightMenu'),
                statusBarView   = DE.getController('Statusbar').getView('Statusbar');

            me._toolbar     = toolbarView.render(this.mode);
            me._rightMenu   = rightMenuView.render(this.mode);

            var value = Common.localStorage.getItem('de-hidden-status');
            if (value !== null && parseInt(value) == 1)
                statusBarView.setVisible(false);
        },

        setMode: function(mode) {
            if (mode.isDisconnected) {
                /** coauthoring begin **/
                if (_.isUndefined(this.mode))
                    this.mode = {};

                this.mode.canCoAuthoring = false;
                /** coauthoring end **/
            } else {
                this.mode = mode;
            }
        }
    });
});