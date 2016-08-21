/*
 * (c) Copyright Ascensio System SIA 2010-2016
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

(
/**
* @param {Window} window
* @param {undefined} undefined
 */
function (window, undefined) {
    var cElementType = AscCommonExcel.cElementType;
    var cBaseFunction = AscCommonExcel.cBaseFunction;
    var cFormulaFunctionGroup = AscCommonExcel.cFormulaFunctionGroup;

    cFormulaFunctionGroup['Cube'] = cFormulaFunctionGroup['Cube'] || [];
    cFormulaFunctionGroup['Cube'].push(
        cCUBEKPIMEMBER,
        cCUBEMEMBER,
        cCUBEMEMBERPROPERTY,
        cCUBERANKEDMEMBER,
        cCUBESET,
        cCUBESETCOUNT,
        cCUBEVALUE
    );

function cCUBEKPIMEMBER() {
//    cBaseFunction.call( this, "CUBEKPIMEMBER" );

    this.name = "CUBEKPIMEMBER";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBEKPIMEMBER.prototype = Object.create( cBaseFunction.prototype );

function cCUBEMEMBER() {
//    cBaseFunction.call( this, "CUBEMEMBER" );

    this.name = "CUBEMEMBER";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBEMEMBER.prototype = Object.create( cBaseFunction.prototype );

function cCUBEMEMBERPROPERTY() {
//    cBaseFunction.call( this, "CUBEMEMBERPROPERTY" );

    this.name = "CUBEMEMBERPROPERTY";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBEMEMBERPROPERTY.prototype = Object.create( cBaseFunction.prototype );

function cCUBERANKEDMEMBER() {
//    cBaseFunction.call( this, "CUBERANKEDMEMBER" );

    this.name = "CUBERANKEDMEMBER";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBERANKEDMEMBER.prototype = Object.create( cBaseFunction.prototype );

function cCUBESET() {
//    cBaseFunction.call( this, "CUBESET" );

    this.name = "CUBESET";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBESET.prototype = Object.create( cBaseFunction.prototype );

function cCUBESETCOUNT() {
//    cBaseFunction.call( this, "CUBESETCOUNT" );

    this.name = "CUBESETCOUNT";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBESETCOUNT.prototype = Object.create( cBaseFunction.prototype );

function cCUBEVALUE() {
//    cBaseFunction.call( this, "CUBEVALUE" );

    this.name = "CUBEVALUE";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 255;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cCUBEVALUE.prototype = Object.create( cBaseFunction.prototype );
})(window);