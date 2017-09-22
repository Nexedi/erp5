/*
 * (c) Copyright Ascensio System SIA 2010-2017
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

"use strict";

(	/**
 * @param {Window} window
 * @param {undefined} undefined
 */
	function (window, undefined) {
		/*
		 * Import
		 * -----------------------------------------------------------------------------
		 */
		var prot;

		/**
		 * Класс language для получения списка языков в проверке орфографии
		 * -----------------------------------------------------------------------------
		 * @constructor
		 * @memberOf Asc
		 * @param id
		 * @param name
		 * @return {*}
		 */
		function asc_CLanguage (name, id) {
			this.name	= name;			// имя языка
			this.id		= id;			// уникальный id языка

			return this;
		}

		asc_CLanguage.prototype = {
			constructor: asc_CLanguage,
			asc_getId: function () { return this.id; },
			asc_getName: function () { return this.name; },
			asc_setId: function (val) { this.id = val; },
			asc_setName: function (val) { this.name = val; }
		};

		//---------------------------------------------------------export---------------------------------------------------
		window['AscCommon'] = window['AscCommon'] || {};
		window["AscCommon"].asc_CLanguage = asc_CLanguage;
		prot = asc_CLanguage.prototype;
		prot["asc_getId"]			= prot.asc_getId;
		prot["asc_getName"]			= prot.asc_getName;
		prot["asc_setId"]			= prot.asc_setId;
		prot["asc_setName"]			= prot.asc_setName;
	}
)(window);
