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
define([
], function () {
    'use strict';
    var FormulaResourcePath = Common.Gateway.props.base_url +
      'web-apps/apps/spreadsheeteditor/main/resources/formula-lang/';

    SSE.Views = SSE.Views || {};

    SSE.Views.FormulaLang = new(function() {
        var langJson = {},
            langDescJson = {};

        var _createXMLHTTPObject = function() {
            var xmlhttp;
            try {
                xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");
            }
            catch (e) {
                try {
                    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
                }
                catch (E) {
                    xmlhttp = false;
                }
            }
            if (!xmlhttp && typeof XMLHttpRequest != 'undefined') {
                xmlhttp = new XMLHttpRequest();
            }
            return xmlhttp;
        };

        var _get = function(lang) {
            if (!lang) return '';
            lang = lang.toLowerCase() ;

            if (langJson[lang])
                return langJson[lang];
            else if (lang == 'en')
                return undefined;
            else {
                try {
                    var xhrObj = _createXMLHTTPObject();
                    if (xhrObj && lang) {
                        xhrObj.open('GET', FormulaResourcePath + lang + '.json', false);
                        xhrObj.send('');
                        langJson[lang] = eval("(" + xhrObj.responseText + ")");
                        return langJson[lang];
                    }
                }
                catch (e) {
                }
            }

            return null;
        };


        var _getDescription = function(lang) {
            if (!lang) return '';
            lang = lang.toLowerCase() ;

            if (langDescJson[lang])
                return langDescJson[lang];
            else {
                try {
                    var xhrObj = _createXMLHTTPObject();
                    if (xhrObj && lang) {
                        xhrObj.open('GET', FormulaResourcePath + lang + '_desc.json', false);
                        xhrObj.send('');
                        if (xhrObj.status == 200)
                            langDescJson[lang] = eval("(" + xhrObj.responseText + ")");
                        else {
                            xhrObj.open('GET', FormulaResourcePath + 'en_desc.json', false);
                            xhrObj.send('');
                            langDescJson[lang] = eval("(" + xhrObj.responseText + ")");
                        }
                        return langDescJson[lang];
                    }
                }
                catch (e) {
                }
            }

            return null;
        };

        return {
            get: _get,
            getDescription: _getDescription
        };
    })();
});
