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
    var cErrorType = AscCommonExcel.cErrorType;
    var cNumber = AscCommonExcel.cNumber;
    var cString = AscCommonExcel.cString;
    var cBool = AscCommonExcel.cBool;
    var cError = AscCommonExcel.cError;
    var cArea = AscCommonExcel.cArea;
    var cArea3D = AscCommonExcel.cArea3D;
    var cRef = AscCommonExcel.cRef;
    var cRef3D = AscCommonExcel.cRef3D;
    var cArray = AscCommonExcel.cArray;
    var cBaseFunction = AscCommonExcel.cBaseFunction;
    var cFormulaFunctionGroup = AscCommonExcel.cFormulaFunctionGroup;
    
    cFormulaFunctionGroup['Information'] = cFormulaFunctionGroup['Information'] || [];
    cFormulaFunctionGroup['Information'].push(
        cERROR_TYPE,
        cISBLANK,
        cISERR,
        cISERROR,
        cISEVEN,
        cISLOGICAL,
        cISNA,
        cISNONTEXT,
        cISNUMBER,
        cISODD,
        cISREF,
        cISTEXT,
        cN,
        cNA,
        cTYPE
    );
/*
 здесь вынесены функции, которы по назначению не могут быть использованы в веб редакторах документах.
 либо они будут реализованы с усеченным функционалом позже.
 "INFO" :function(){
 cBaseFunction.call(this,"INFO");
 },
 "CELL" :function(){
 cBaseFunction.call(this,"CELL");
 },
 */

function cERROR_TYPE() {
//    cBaseFunction.call( this, "ERROR.TYPE" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ERROR.TYPE";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cERROR_TYPE.prototype = Object.create( cBaseFunction.prototype );
cERROR_TYPE.prototype.Calculate = function ( arg ) {
    function typeError( elem ) {
        if ( elem instanceof cError ) {
            switch ( elem.errorType ) {
                case cErrorType.null_value:
                    return new cNumber( 1 );
                case cErrorType.division_by_zero:
                    return new cNumber( 2 );
                case cErrorType.wrong_value_type:
                    return new cNumber( 3 );
                case cErrorType.bad_reference :
                    return new cNumber( 4 );
                case cErrorType.wrong_name :
                    return new cNumber( 5 );
                case cErrorType.not_numeric :
                    return new cNumber( 6 );
                case cErrorType.not_available :
                    return new cNumber( 7 );
                case cErrorType.getting_data :
                    return new cNumber( 8 );
                default:
                    return new cError( cErrorType.not_available );
            }
        }
        else {
            return new cError( cErrorType.not_available );
        }
    }

    var arg0 = arg[0];
    if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cArray ) {
        var ret = new cArray();
        arg0.foreach( function ( elem, r, c ) {
            if ( !ret.array[r] )
                ret.addRow();
            ret.addElement( found_operand );
        } );
        return this.value = ret;
    }
    return this.value = typeError( arg0 );
};
cERROR_TYPE.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISBLANK() {
//    cBaseFunction.call( this, "ISBLANK" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISBLANK";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISBLANK.prototype = Object.create( cBaseFunction.prototype );
cISBLANK.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }
    if ( arg0 instanceof AscCommonExcel.cEmpty )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISBLANK.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISERR() {
//    cBaseFunction.call( this, "ISERR" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISERR";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISERR.prototype = Object.create( cBaseFunction.prototype );
cISERR.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cError && arg0.errorType != cErrorType.not_available )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISERR.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISERROR() {
//    cBaseFunction.call( this, "ISERROR" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISERROR";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISERROR.prototype = Object.create( cBaseFunction.prototype );
cISERROR.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cError )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISERROR.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISEVEN() {
//    cBaseFunction.call( this, "ISEVEN" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISEVEN";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISEVEN.prototype = Object.create( cBaseFunction.prototype );
cISEVEN.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cError )
        return this.value = arg0;

    var arg0 = arg0.tocNumber();
    if ( arg0 instanceof cError )
        return this.value = arg0;
    else
        return this.value = new cBool( (arg0.getValue() & 1) == 0 );
};
cISEVEN.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(number)"
    };
};

function cISLOGICAL() {
//    cBaseFunction.call( this, "ISLOGICAL" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISLOGICAL";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISLOGICAL.prototype = Object.create( cBaseFunction.prototype );
cISLOGICAL.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cBool )
        return this.value = new cBool( true );
    else return this.value = new cBool( false );
};
cISLOGICAL.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISNA() {
//    cBaseFunction.call( this, "ISNA" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISNA";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISNA.prototype = Object.create( cBaseFunction.prototype );
cISNA.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cError && arg0.errorType == cErrorType.not_available )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISNA.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISNONTEXT() {
//    cBaseFunction.call( this, "ISNONTEXT" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISNONTEXT";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISNONTEXT.prototype = Object.create( cBaseFunction.prototype );
cISNONTEXT.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }
    if ( !(arg0 instanceof cString) )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISNONTEXT.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISNUMBER() {
//    cBaseFunction.call( this, "ISNUMBER" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISNUMBER";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISNUMBER.prototype = Object.create( cBaseFunction.prototype );
cISNUMBER.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cNumber )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISNUMBER.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISODD() {
//    cBaseFunction.call( this, "ISODD" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISODD";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISODD.prototype = Object.create( cBaseFunction.prototype );
cISODD.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cError )
        return this.value = arg0;

    var arg0 = arg0.tocNumber();
    if ( arg0 instanceof cError )
        return this.value = arg0;
    else
        return this.value = new cBool( (arg0.getValue() & 1) == 1 );
};
cISODD.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(number)"
    };
};

function cISREF() {
//    cBaseFunction.call( this, "ISREF" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISREF";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISREF.prototype = Object.create( cBaseFunction.prototype );
cISREF.prototype.Calculate = function ( arg ) {
    if ( (arg[0] instanceof cRef || arg[0] instanceof cArea || arg[0] instanceof cArea3D || arg[0] instanceof cRef3D) && arg[0].isValid && arg[0].isValid() )
        return this.value = new cBool( true );
    else return this.value = new cBool( false );
};
cISREF.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cISTEXT() {
//    cBaseFunction.call( this, "ISTEXT" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "ISTEXT";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cISTEXT.prototype = Object.create( cBaseFunction.prototype );
cISTEXT.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        arg0 = arg0.getElement( 0 );
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cString )
        return this.value = new cBool( true );
    else
        return this.value = new cBool( false );
};
cISTEXT.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cN() {
//    cBaseFunction.call( this, "N" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );
//    this.setFormat( this.formatType.noneFormat );

    this.name = "N";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.noneFormat;

}

cN.prototype = Object.create( cBaseFunction.prototype );
cN.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArray ) {
        var arr = new cArray();
        arg.foreach( function ( elem, r, c ) {
            if ( elem instanceof cNumber || elem instanceof cError )
                arr.array[r][c] = elem;
            else if ( elem instanceof cBool )
                arr.array[r][c] = elem.tocNumber();
            else
                arr.array[r][c] = new cNumber( 0 );
        } )
        return this.value = arr;
    }
    else if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cNumber || arg0 instanceof cError )
        return this.value = arg0;
    else if ( arg0 instanceof cBool )
        return this.value = arg0.tocNumber();
    else
        return this.value = new cNumber( 0 );

};
cN.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};

function cNA() {
//    cBaseFunction.call( this, "NA" );
//    this.setArgumentsMin( 0 );
//    this.setArgumentsMax( 0 );

    this.name = "NA";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 0;
    this.argumentsCurrent = 0;
    this.argumentsMax = 0;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cNA.prototype = Object.create( cBaseFunction.prototype );
cNA.prototype.Calculate = function () {
    return this.value = new cError( cErrorType.not_available );
};
cNA.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"()"
    };
};

function cTYPE() {
//    cBaseFunction.call( this, "TYPE" );
//    this.setArgumentsMin( 1 );
//    this.setArgumentsMax( 1 );

    this.name = "TYPE";
    this.type = cElementType.func;
    this.value = null;
    this.argumentsMin = 1;
    this.argumentsCurrent = 0;
    this.argumentsMax = 1;
    this.formatType = {
        def:-1, //подразумевается формат первой ячейки входящей в формулу.
        noneFormat:-2
    };
    this.numFormat = this.formatType.def;

}

cTYPE.prototype = Object.create( cBaseFunction.prototype );
cTYPE.prototype.Calculate = function ( arg ) {
    var arg0 = arg[0];
    if ( arg0 instanceof cArea || arg0 instanceof cArea3D ) {
        arg0 = arg0.cross( arguments[1].first );
    }
    else if ( arg0 instanceof cRef || arg0 instanceof cRef3D ) {
        arg0 = arg0.getValue();
    }

    if ( arg0 instanceof cNumber )
        return this.value = new cNumber( 1 );
    else if ( arg0 instanceof cString )
        return this.value = new cNumber( 2 )
    else if ( arg0 instanceof cBool )
        return this.value = new cNumber( 4 )
    else if ( arg0 instanceof cError )
        return this.value = new cNumber( 16 )
    else
        return this.value = new cNumber( 64 );
};
cTYPE.prototype.getInfo = function () {
    return {
        name:this.name,
        args:"(value)"
    };
};
})(window);