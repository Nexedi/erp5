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
 *    FormulaDialog.js
 *
 *    Formula Dialog Controller
 *
 *    Created by Alexey.Musinov on  14/04/2014
 *    Copyright (c) 2014 Ascensio System SIA. All rights reserved.
 *
 */

define([
    'core',
    'spreadsheeteditor/main/app/collection/FormulaGroups',
    'spreadsheeteditor/main/app/view/FormulaDialog'
], function () {
    'use strict';

    SSE.Controllers = SSE.Controllers || {};

    SSE.Controllers.FormulaDialog = Backbone.Controller.extend({
        models: [],
        views: [
            'FormulaDialog'
        ],
        collections: [
            'FormulaGroups'
        ],

        initialize: function () {
            var me = this;
            this.addListeners({
                'FileMenu': {
                    'settings:apply': function() {
                        me.needUpdateFormula = true;
                    }
                }
            });
        },

        setApi: function (api) {
            this.api = api;

            if (this.formulasGroups && this.api) {
                this.loadingFormulas();

                var me = this;

                this.formulas = new SSE.Views.FormulaDialog({
                    api             : this.api,
                    toolclose       : 'hide',
                    formulasGroups  : this.formulasGroups,
                    handler         : function (func) {
                        if (func && me.api) {
                            me.api.asc_insertFormula(func, Asc.c_oAscPopUpSelectorType.Func);
                        }
                    }
                });

                this.formulas.on({
                    'hide': function () {
                        if (me.api) {
                            me.api.asc_enableKeyEvents(true);
                        }
                    }
                });
            }

            return this;
        },

        setMode: function(mode) {
            this.mode = mode;
            return this;
        },

        onLaunch: function () {
            this.formulasGroups = this.getApplication().getCollection('FormulaGroups');
        },

        showDialog: function () {
            if (this.formulas) {
                if (this.needUpdateFormula)
                    this.updateFormulas();
                this.needUpdateFormula = false;
                this.formulas.show();
            }
        },
        hideDialog: function () {
            if (this.formulas && this.formulas.isVisible()) {
                this.formulas.hide();
            }
        },

        loadingFormulas: function () {
            var i = 0, j = 0,
                ascGroupName,
                ascFunctions,
                functions,
                store = this.formulasGroups,
                formulaGroup = null,
                index = 0,
                funcInd = 0,
                info = null,
                allFunctions = [],
                allFunctionsGroup = null;

            if (store) {
                var value = Common.localStorage.getItem("sse-settings-func-locale");
                if (value===null)
                    value = ((this.mode.lang) ? this.mode.lang : 'en').split("-")[0].toLowerCase();
                value = SSE.Views.FormulaLang.getDescription(value);

                allFunctionsGroup = new SSE.Models.FormulaGroup ({
                    name    : 'All',
                    index   : index,
                    store   : store
                });

                if (allFunctionsGroup) {
                    index += 1;

                    store.push(allFunctionsGroup);

                    info = this.api.asc_getFormulasInfo();

                    for (i = 0; i < info.length; i += 1) {
                        ascGroupName = info[i].asc_getGroupName();
                        ascFunctions = info[i].asc_getFormulasArray();

                        formulaGroup = new SSE.Models.FormulaGroup({
                            name  : ascGroupName,
                            index : index,
                            store : store
                        });

                        index += 1;

                        functions = [];

                        for (j = 0; j < ascFunctions.length; j += 1) {
                            var funcname = ascFunctions[j].asc_getName();
                            var func = new SSE.Models.FormulaModel({
                                index : funcInd,
                                group : ascGroupName,
                                name  : ascFunctions[j].asc_getLocaleName(),
                                args  : (value && value[funcname]) ? value[funcname].a : '',
                                desc  : (value && value[funcname]) ? value[funcname].d : ''
                            });

                            funcInd += 1;

                            functions.push(func);
                            allFunctions.push(func);
                        }

                        formulaGroup.set('functions', functions);
                        store.push(formulaGroup);
                    }

                    allFunctionsGroup.set('functions',
                       _.sortBy(allFunctions, function (model) {return model.get('name'); }));
                }
            }
        },

        updateFormulas: function () {
            this.formulasGroups.reset();
            this.loadingFormulas();
            if (this.formulas.$window) {
                this.formulas.fillFormulasGroups();
                this.formulas.fillFunctions('All');
            }
        }
    });
});
