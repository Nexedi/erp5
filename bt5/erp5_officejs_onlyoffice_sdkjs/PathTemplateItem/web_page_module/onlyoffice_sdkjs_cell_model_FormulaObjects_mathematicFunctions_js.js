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

(/**
 * @param {Window} window
 * @param {undefined} undefined
 */
	function (window, undefined) {
	var cElementType = AscCommonExcel.cElementType;
	var cErrorType = AscCommonExcel.cErrorType;
	var cExcelSignificantDigits = AscCommonExcel.cExcelSignificantDigits;
	var cNumber = AscCommonExcel.cNumber;
	var cString = AscCommonExcel.cString;
	var cBool = AscCommonExcel.cBool;
	var cError = AscCommonExcel.cError;
	var cArea = AscCommonExcel.cArea;
	var cArea3D = AscCommonExcel.cArea3D;
	var cRef = AscCommonExcel.cRef;
	var cRef3D = AscCommonExcel.cRef3D;
	var cEmpty = AscCommonExcel.cEmpty;
	var cArray = AscCommonExcel.cArray;
	var cBaseFunction = AscCommonExcel.cBaseFunction;
	var cFormulaFunctionGroup = AscCommonExcel.cFormulaFunctionGroup;

	var _func = AscCommonExcel._func;

	cFormulaFunctionGroup['Mathematic'] = cFormulaFunctionGroup['Mathematic'] || [];
	cFormulaFunctionGroup['Mathematic'].push(cABS, cACOS, cACOSH, cASIN, cASINH, cATAN, cATAN2, cATANH, cCEILING,
		cCOMBIN, cCOS, cCOSH, cDEGREES, cECMA_CEILING, cEVEN, cEXP, cFACT, cFACTDOUBLE, cFLOOR, cGCD, cINT,
		cISO_CEILING, cLCM, cLN, cLOG, cLOG10, cMDETERM, cMINVERSE, cMMULT, cMOD, cMROUND, cMULTINOMIAL, cODD, cPI,
		cPOWER, cPRODUCT, cQUOTIENT, cRADIANS, cRAND, cRANDBETWEEN, cROMAN, cROUND, cROUNDDOWN, cROUNDUP, cSERIESSUM,
		cSIGN, cSIN, cSINH, cSQRT, cSQRTPI, cSUBTOTAL, cSUM, cSUMIF, cSUMIFS, cSUMPRODUCT, cSUMSQ, cSUMX2MY2, cSUMX2PY2,
		cSUMXMY2, cTAN, cTANH, cTRUNC);

	var cSubTotalFunctionType = {
		includes: {
			AVERAGE: 1, COUNT: 2, COUNTA: 3, MAX: 4, MIN: 5, PRODUCT: 6, STDEV: 7, STDEVP: 8, SUM: 9, VAR: 10, VARP: 11
		}, excludes: {
			AVERAGE: 101,
			COUNT: 102,
			COUNTA: 103,
			MAX: 104,
			MIN: 105,
			PRODUCT: 106,
			STDEV: 107,
			STDEVP: 108,
			SUM: 109,
			VAR: 110,
			VARP: 111
		}
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cABS() {
		this.name = "ABS";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cABS.prototype = Object.create(cBaseFunction.prototype);
	cABS.prototype.constructor = cABS;
	cABS.prototype.argumentsMin = 1;
	cABS.prototype.argumentsMax = 1;
	cABS.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					this.array[r][c] = new cNumber(Math.abs(elem.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			return this.value = new cNumber(Math.abs(arg0.getValue()));
		}
		return this.value = arg0;
	};
	cABS.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		}
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cACOS() {
		this.name = "ACOS";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cACOS.prototype = Object.create(cBaseFunction.prototype);
	cACOS.prototype.constructor = cACOS;
	cACOS.prototype.argumentsMin = 1;
	cACOS.prototype.argumentsMax = 1;
	cACOS.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.acos(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.acos(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cACOS.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cACOSH() {
		this.name = "ACOSH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cACOSH.prototype = Object.create(cBaseFunction.prototype);
	cACOSH.prototype.constructor = cACOSH;
	cACOSH.prototype.argumentsMin = 1;
	cACOSH.prototype.argumentsMax = 1;
	cACOSH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.acosh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.acosh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cACOSH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cASIN() {
		this.name = "ASIN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cASIN.prototype = Object.create(cBaseFunction.prototype);
	cASIN.prototype.constructor = cASIN;
	cASIN.prototype.argumentsMin = 1;
	cASIN.prototype.argumentsMax = 1;
	cASIN.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.asin(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.asin(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cASIN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cASINH() {
		this.name = "ASINH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cASINH.prototype = Object.create(cBaseFunction.prototype);
	cASINH.prototype.constructor = cASINH;
	cASINH.prototype.argumentsMin = 1;
	cASINH.prototype.argumentsMax = 1;
	cASINH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.asinh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.asinh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cASINH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cATAN() {
		this.name = "ATAN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cATAN.prototype = Object.create(cBaseFunction.prototype);
	cATAN.prototype.constructor = cATAN;
	cATAN.prototype.argumentsMin = 1;
	cATAN.prototype.argumentsMax = 1;
	cATAN.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.atan(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else {
			var a = Math.atan(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
	};
	cATAN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cATAN2() {
		this.name = "ATAN2";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cATAN2.prototype = Object.create(cBaseFunction.prototype);
	cATAN2.prototype.constructor = cATAN2;
	cATAN2.prototype.argumentsMin = 2;
	cATAN2.prototype.argumentsMax = 2;
	cATAN2.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();
		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem, b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] =
							a.getValue() == 0 && b.getValue() == 0 ? new cError(cErrorType.division_by_zero) :
								new cNumber(Math.atan2(b.getValue(), a.getValue()))
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] =
						a.getValue() == 0 && b.getValue() == 0 ? new cError(cErrorType.division_by_zero) :
							new cNumber(Math.atan2(b.getValue(), a.getValue()))
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] =
						a.getValue() == 0 && b.getValue() == 0 ? new cError(cErrorType.division_by_zero) :
							new cNumber(Math.atan2(b.getValue(), a.getValue()))
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		return this.value = (    arg0 instanceof cError ? arg0 : arg1 instanceof cError ? arg1 :
					arg1.getValue() == 0 && arg0.getValue() == 0 ? new cError(cErrorType.division_by_zero) :
						new cNumber(Math.atan2(arg1.getValue(), arg0.getValue()))
		)
	};
	cATAN2.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, y )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cATANH() {
		this.name = "ATANH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cATANH.prototype = Object.create(cBaseFunction.prototype);
	cATANH.prototype.constructor = cATANH;
	cATANH.prototype.argumentsMin = 1;
	cATANH.prototype.argumentsMax = 1;
	cATANH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.atanh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.atanh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cATANH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCEILING() {
		this.name = "CEILING";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cCEILING.prototype = Object.create(cBaseFunction.prototype);
	cCEILING.prototype.constructor = cCEILING;
	cCEILING.prototype.argumentsMin = 2;
	cCEILING.prototype.argumentsMax = 2;
	cCEILING.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg[0].tocNumber();
		arg1 = arg[1].tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		function ceilingHelper(number, significance) {
			if (significance == 0) {
				return new cNumber(0.0);
			}
			if (number > 0 && significance < 0) {
				return new cError(cErrorType.not_numeric);
			} else if (number / significance === Infinity) {
				return new cError(cErrorType.not_numeric);
			} else {
				var quotient = number / significance;
				if (quotient == 0) {
					return new cNumber(0.0);
				}
				var quotientTr = Math.floor(quotient);

				var nolpiat = 5 * Math.sign(quotient) *
					Math.pow(10, Math.floor(Math.log10(Math.abs(quotient))) - cExcelSignificantDigits);

				if (Math.abs(quotient - quotientTr) > nolpiat) {
					++quotientTr;
				}
				return new cNumber(quotientTr * significance);
			}
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem, b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = ceilingHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = ceilingHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = ceilingHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		return this.value = ceilingHelper(arg0.getValue(), arg1.getValue());

	};
	cCEILING.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, significance )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCOMBIN() {
		this.name = "COMBIN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cCOMBIN.prototype = Object.create(cBaseFunction.prototype);
	cCOMBIN.prototype.constructor = cCOMBIN;
	cCOMBIN.prototype.argumentsMin = 2;
	cCOMBIN.prototype.argumentsMax = 2;
	cCOMBIN.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem, b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = new cNumber(Math.binomCoeff(a.getValue(), b.getValue()));
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {

					if (a.getValue() <= 0 || b.getValue() <= 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					}

					this.array[r][c] = new cNumber(Math.binomCoeff(a.getValue(), b.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {

					if (a.getValue() <= 0 || b.getValue() <= 0 || a.getValue() < b.getValue()) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					}

					this.array[r][c] = new cNumber(Math.binomCoeff(a.getValue(), b.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		if (arg0.getValue() <= 0 || arg1.getValue() <= 0 || arg0.getValue() < arg1.getValue()) {
			return this.value = new cError(cErrorType.not_numeric);
		}

		return this.value = new cNumber(Math.binomCoeff(arg0.getValue(), arg1.getValue()));
	};
	cCOMBIN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( number , number-chosen )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCOS() {
		this.name = "COS";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cCOS.prototype = Object.create(cBaseFunction.prototype);
	cCOS.prototype.constructor = cCOS;
	cCOS.prototype.argumentsMin = 1;
	cCOS.prototype.argumentsMax = 1;
	cCOS.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.cos(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.cos(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cCOS.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCOSH() {
		this.name = "COSH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cCOSH.prototype = Object.create(cBaseFunction.prototype);
	cCOSH.prototype.constructor = cCOSH;
	cCOSH.prototype.argumentsMin = 1;
	cCOSH.prototype.argumentsMax = 1;
	cCOSH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.cosh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.cosh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cCOSH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cDEGREES() {
		this.name = "DEGREES";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cDEGREES.prototype = Object.create(cBaseFunction.prototype);
	cDEGREES.prototype.constructor = cDEGREES;
	cDEGREES.prototype.argumentsMin = 1;
	cDEGREES.prototype.argumentsMax = 1;
	cDEGREES.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = elem.getValue();
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a * 180 / Math.PI);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = arg0.getValue();
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a * 180 / Math.PI);
		}
		return this.value = arg0;

	};
	cDEGREES.prototype.getInfo = function () {
		return {
			name: this.name, args: "( angle )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cECMA_CEILING() {
		cBaseFunction.call(this, "ECMA_CEILING");
	}

	cECMA_CEILING.prototype = Object.create(cBaseFunction.prototype);
	cECMA_CEILING.prototype.constructor = cECMA_CEILING;

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cEVEN() {
		this.name = "EVEN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cEVEN.prototype = Object.create(cBaseFunction.prototype);
	cEVEN.prototype.constructor = cEVEN;
	cEVEN.prototype.argumentsMin = 1;
	cEVEN.prototype.argumentsMax = 1;
	cEVEN.prototype.Calculate = function (arg) {

		function evenHelper(arg) {
			var arg0 = arg.getValue();
			if (arg0 >= 0) {
				arg0 = Math.ceil(arg0);
				if ((arg0 & 1) == 0) {
					return new cNumber(arg0);
				} else {
					return new cNumber(arg0 + 1);
				}
			} else {
				arg0 = Math.floor(arg0);
				if ((arg0 & 1) == 0) {
					return new cNumber(arg0);
				} else {
					return new cNumber(arg0 - 1);
				}
			}
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}

		arg0 = arg0.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					this.array[r][c] = evenHelper(elem);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg0 instanceof cNumber) {
			return this.value = evenHelper(arg0);
		}
		return this.value = new cError(cErrorType.wrong_value_type);
	};
	cEVEN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cEXP() {
		this.name = "EXP";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cEXP.prototype = Object.create(cBaseFunction.prototype);
	cEXP.prototype.constructor = cEXP;
	cEXP.prototype.argumentsMin = 1;
	cEXP.prototype.argumentsMax = 1;
	cEXP.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.exp(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		}
		if (!(arg0 instanceof cNumber)) {
			return this.value = new cError(cErrorType.not_numeric);
		} else {
			var a = Math.exp(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
	};
	cEXP.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cFACT() {
		this.name = "FACT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cFACT.prototype = Object.create(cBaseFunction.prototype);
	cFACT.prototype.constructor = cFACT;
	cFACT.prototype.argumentsMin = 1;
	cFACT.prototype.argumentsMax = 1;
	cFACT.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					if (elem.getValue() < 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					} else {
						var a = Math.fact(elem.getValue());
						this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
					}
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			if (arg0.getValue() < 0) {
				return this.value = new cError(cErrorType.not_numeric);
			}
			var a = Math.fact(arg0.getValue());
			return this.value = isNaN(a) || a == Infinity ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cFACT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cFACTDOUBLE() {
		this.name = "FACTDOUBLE";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cFACTDOUBLE.prototype = Object.create(cBaseFunction.prototype);
	cFACTDOUBLE.prototype.constructor = cFACTDOUBLE;
	cFACTDOUBLE.prototype.argumentsMin = 1;
	cFACTDOUBLE.prototype.argumentsMax = 1;
	cFACTDOUBLE.prototype.Calculate = function (arg) {
		function factDouble(n) {
			if (n == 0) {
				return 0;
			} else if (n < 0) {
				return Number.NaN;
			} else if (n > 300) {
				return Number.Infinity;
			}
			n = Math.floor(n);
			var res = n, _n = n, ost = -(_n & 1);
			n -= 2;

			while (n != ost) {
				res *= n;
				n -= 2;
			}
			return res;
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					if (elem.getValue() < 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					} else {
						var a = factDouble(elem.getValue());
						this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
					}
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			if (arg0.getValue() < 0) {
				return this.value = new cError(cErrorType.not_numeric);
			}
			var a = factDouble(arg0.getValue());
			return this.value = isNaN(a) || a == Infinity ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cFACTDOUBLE.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cFLOOR() {
		this.name = "FLOOR";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cFLOOR.prototype = Object.create(cBaseFunction.prototype);
	cFLOOR.prototype.constructor = cFLOOR;
	cFLOOR.prototype.argumentsMin = 2;
	cFLOOR.prototype.argumentsMax = 2;
	cFLOOR.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		arg0 = arg[0].tocNumber();
		arg1 = arg[1].tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		function floorHelper(number, significance) {
			if (significance == 0) {
				return new cNumber(0.0);
			}
			if (( number > 0 && significance < 0 ) || ( number < 0 && significance > 0 )) {
				return new cError(cErrorType.not_numeric);
			} else if (number / significance === Infinity) {
				return new cError(cErrorType.not_numeric);
			} else {
				var quotient = number / significance;
				if (quotient == 0) {
					return new cNumber(0.0);
				}

				var nolpiat = 5 * ( quotient < 0 ? -1.0 : quotient > 0 ? 1.0 : 0.0 ) *
					Math.pow(10, Math.floor(Math.log10(Math.abs(quotient))) - cExcelSignificantDigits);

				return new cNumber(Math.floor(quotient + nolpiat) * significance);
			}
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = floorHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem;
				var b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = floorHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0;
				var b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = floorHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		if (arg0 instanceof cString || arg1 instanceof cString) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = floorHelper(arg0.getValue(), arg1.getValue());
	};
	cFLOOR.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, significance )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cGCD() {
		this.name = "GCD";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cGCD.prototype = Object.create(cBaseFunction.prototype);
	cGCD.prototype.constructor = cGCD;
	cGCD.prototype.argumentsMin = 1;
	cGCD.prototype.Calculate = function (arg) {

		var _gcd = 0, argArr;

		function gcd(a, b) {
			var _a = parseInt(a), _b = parseInt(b);
			while (_b != 0)
				_b = _a % (_a = _b);
			return _a;
		}

		for (var i = 0; i < this.getArguments(); i++) {
			var argI = arg[i];

			if (argI instanceof cArea || argI instanceof cArea3D) {
				argArr = argI.getValue();
				for (var j = 0; j < argArr.length; j++) {

					if (argArr[j] instanceof cError) {
						return this.value = argArr[j];
					}

					if (argArr[j] instanceof cString) {
						continue;
					}

					if (argArr[j] instanceof cBool) {
						argArr[j] = argArr[j].tocNumber();
					}

					if (argArr[j].getValue() < 0) {
						return this.value = new cError(cErrorType.not_numeric);
					}

					_gcd = gcd(_gcd, argArr[j].getValue());
				}
			} else if (argI instanceof cArray) {
				argArr = argI.tocNumber();

				if (argArr.foreach(function (arrElem) {

						if (arrElem instanceof cError) {
							_gcd = arrElem;
							return true;
						}

						if (arrElem instanceof cBool) {
							arrElem = arrElem.tocNumber();
						}

						if (arrElem instanceof cString) {
							return;
						}

						if (arrElem.getValue() < 0) {
							_gcd = new cError(cErrorType.not_numeric);
							return true;
						}
						_gcd = gcd(_gcd, arrElem.getValue());

					})) {
					return this.value = _gcd;
				}
			} else {
				argI = argI.tocNumber();

				if (argI.getValue() < 0) {
					return this.value = new cError(cErrorType.not_numeric);
				}

				if (argI instanceof cError) {
					return this.value = argI;
				}

				_gcd = gcd(_gcd, argI.getValue())
			}
		}

		return this.value = new cNumber(_gcd);

	};
	cGCD.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cINT() {
		this.name = "INT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cINT.prototype = Object.create(cBaseFunction.prototype);
	cINT.prototype.constructor = cINT;
	cINT.prototype.argumentsMin = 1;
	cINT.prototype.argumentsMax = 1;
	cINT.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg0 instanceof cString) {
			this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					this.array[r][c] = new cNumber(Math.floor(elem.getValue()))
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			return this.value = new cNumber(Math.floor(arg0.getValue()))
		}

		return this.value = new cNumber(Math.floor(arg0.getValue()));
	};
	cINT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cISO_CEILING() {
		cBaseFunction.call(this, "ISO_CEILING");
	}

	cISO_CEILING.prototype = Object.create(cBaseFunction.prototype);
	cISO_CEILING.prototype.constructor = cISO_CEILING;

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cLCM() {
		this.name = "LCM";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cLCM.prototype = Object.create(cBaseFunction.prototype);
	cLCM.prototype.constructor = cLCM;
	cLCM.prototype.argumentsMin = 1;
	cLCM.prototype.Calculate = function (arg) {

		var _lcm = 1, argArr;

		function gcd(a, b) {
			var _a = parseInt(a), _b = parseInt(b);
			while (_b != 0)
				_b = _a % (_a = _b);
			return _a;
		}

		function lcm(a, b) {
			return Math.abs(parseInt(a) * parseInt(b)) / gcd(a, b);
		}

		for (var i = 0; i < this.getArguments(); i++) {
			var argI = arg[i];

			if (argI instanceof cArea || argI instanceof cArea3D) {
				argArr = argI.getValue();
				for (var j = 0; j < argArr.length; j++) {

					if (argArr[j] instanceof cError) {
						return this.value = argArr[j];
					}

					if (argArr[j] instanceof cString) {
						continue;
					}

					if (argArr[j] instanceof cBool) {
						argArr[j] = argArr[j].tocNumber();
					}

					if (argArr[j].getValue() <= 0) {
						return this.value = new cError(cErrorType.not_numeric);
					}

					_lcm = lcm(_lcm, argArr[j].getValue());
				}
			} else if (argI instanceof cArray) {
				argArr = argI.tocNumber();

				if (argArr.foreach(function (arrElem) {

						if (arrElem instanceof cError) {
							_lcm = arrElem;
							return true;
						}

						if (arrElem instanceof cBool) {
							arrElem = arrElem.tocNumber();
						}

						if (arrElem instanceof cString) {
							return;
						}

						if (arrElem.getValue() <= 0) {
							_lcm = new cError(cErrorType.not_numeric);
							return true;
						}
						_lcm = lcm(_lcm, arrElem.getValue());

					})) {
					return this.value = _lcm;
				}
			} else {
				argI = argI.tocNumber();

				if (argI.getValue() <= 0) {
					return this.value = new cError(cErrorType.not_numeric);
				}

				if (argI instanceof cError) {
					return this.value = argI;
				}

				_lcm = lcm(_lcm, argI.getValue())
			}
		}

		return this.value = new cNumber(_lcm);

	};
	cLCM.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cLN() {
		this.name = "LN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cLN.prototype = Object.create(cBaseFunction.prototype);
	cLN.prototype.constructor = cLN;
	cLN.prototype.argumentsMin = 1;
	cLN.prototype.argumentsMax = 1;
	cLN.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg0 instanceof cString) {
			return this.value = new cError(cErrorType.wrong_value_type);
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					if (elem.getValue() <= 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					} else {
						this.array[r][c] = new cNumber(Math.log(elem.getValue()));
					}
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			if (arg0.getValue() <= 0) {
				return this.value = new cError(cErrorType.not_numeric);
			} else {
				return this.value = new cNumber(Math.log(arg0.getValue()));
			}
		}
	};
	cLN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cLOG() {
		this.name = "LOG";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cLOG.prototype = Object.create(cBaseFunction.prototype);
	cLOG.prototype.constructor = cLOG;
	cLOG.prototype.argumentsMin = 1;
	cLOG.prototype.argumentsMax = 2;
	cLOG.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cNumber(10);
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = new cNumber(Math.log(a.getValue()) / Math.log(b.getValue()));
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1 ? arg1 : new cNumber(10);
				if (a instanceof cNumber && b instanceof cNumber) {

					if (a.getValue() <= 0 || a.getValue() <= 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					}

					this.array[r][c] = new cNumber(Math.log(a.getValue()) / Math.log(b.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {

					if (a.getValue() <= 0 || a.getValue() <= 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					}

					this.array[r][c] = new cNumber(Math.log(a.getValue()) / Math.log(b.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		if (!(arg0 instanceof cNumber) || ( arg1 && !(arg0 instanceof cNumber) )) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg0.getValue() <= 0 || ( arg1 && arg1.getValue() <= 0 )) {
			return this.value = new cError(cErrorType.not_numeric);
		}

		return this.value = new cNumber(Math.log(arg0.getValue()) / Math.log(arg1.getValue()));
	};
	cLOG.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x [ , base ] )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cLOG10() {
		this.name = "LOG10";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cLOG10.prototype = Object.create(cBaseFunction.prototype);
	cLOG10.prototype.constructor = cLOG10;
	cLOG10.prototype.argumentsMin = 1;
	cLOG10.prototype.argumentsMax = 1;
	cLOG10.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg0 instanceof cString) {
			return this.value = new cError(cErrorType.wrong_value_type);
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					if (elem.getValue() <= 0) {
						this.array[r][c] = new cError(cErrorType.not_numeric);
					} else {
						this.array[r][c] = new cNumber(Math.log10(elem.getValue()));
					}
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			if (arg0.getValue() <= 0) {
				return this.value = new cError(cErrorType.not_numeric);
			} else {
				return this.value = new cNumber(Math.log10(arg0.getValue()));
			}
		}
	};
	cLOG10.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMDETERM() {
		this.name = "MDETERM";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMDETERM.prototype = Object.create(cBaseFunction.prototype);
	cMDETERM.prototype.constructor = cMDETERM;
	cMDETERM.prototype.argumentsMin = 1;
	cMDETERM.prototype.argumentsMax = 1;
	cMDETERM.prototype.numFormat = AscCommonExcel.cNumFormatNone;
	cMDETERM.prototype.Calculate = function (arg) {

		function determ(A) {
			var N = A.length, denom = 1, exchanges = 0, i, j;

			for (i = 0; i < N; i++) {
				for (j = 0; j < A[i].length; j++) {
					if (A[i][j] instanceof cEmpty || A[i][j] instanceof cString) {
						return NaN;
					}
				}
			}

			for (i = 0; i < N - 1; i++) {
				var maxN = i, maxValue = Math.abs(A[i][i] instanceof cEmpty ? NaN : A[i][i]);
				for (j = i + 1; j < N; j++) {
					var value = Math.abs(A[j][i] instanceof cEmpty ? NaN : A[j][i]);
					if (value > maxValue) {
						maxN = j;
						maxValue = value;
					}
				}
				if (maxN > i) {
					var temp = A[i];
					A[i] = A[maxN];
					A[maxN] = temp;
					exchanges++;
				} else {
					if (maxValue == 0) {
						return maxValue;
					}
				}
				var value1 = A[i][i] instanceof cEmpty ? NaN : A[i][i];
				for (j = i + 1; j < N; j++) {
					var value2 = A[j][i] instanceof cEmpty ? NaN : A[j][i];
					A[j][i] = 0;
					for (var k = i + 1; k < N; k++) {
						A[j][k] = (A[j][k] * value1 - A[i][k] * value2) / denom;
					}
				}
				denom = value1;
			}

			if (exchanges % 2) {
				return -A[N - 1][N - 1];
			} else {
				return A[N - 1][N - 1];
			}
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else {
			return this.value = new cError(cErrorType.not_available);
		}

		if (arg0[0].length != arg0.length) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = determ(arg0);

		if (!isNaN(arg0)) {
			return this.value = new cNumber(arg0);
		} else {
			return this.value = new cError(cErrorType.not_available);
		}
	};
	cMDETERM.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMINVERSE() {
		this.name = "MINVERSE";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMINVERSE.prototype = Object.create(cBaseFunction.prototype);
	cMINVERSE.prototype.constructor = cMINVERSE;
	cMINVERSE.prototype.argumentsMin = 1;
	cMINVERSE.prototype.argumentsMax = 1;
	cMINVERSE.prototype.numFormat = AscCommonExcel.cNumFormatNone;
	cMINVERSE.prototype.Calculate = function (arg) {

		function Determinant(A) {
			var N = A.length, B = [], denom = 1, exchanges = 0, i, j;

			for (i = 0; i < N; ++i) {
				B[i] = [];
				for (j = 0; j < N; ++j) {
					B[i][j] = A[i][j];
				}
			}

			for (i = 0; i < N - 1; ++i) {
				var maxN = i, maxValue = Math.abs(B[i][i]);
				for (j = i + 1; j < N; ++j) {
					var value = Math.abs(B[j][i]);
					if (value > maxValue) {
						maxN = j;
						maxValue = value;
					}
				}
				if (maxN > i) {
					var temp = B[i];
					B[i] = B[maxN];
					B[maxN] = temp;
					++exchanges;
				} else {
					if (maxValue == 0) {
						return maxValue;
					}
				}
				var value1 = B[i][i];
				for (j = i + 1; j < N; ++j) {
					var value2 = B[j][i];
					B[j][i] = 0;
					for (var k = i + 1; k < N; ++k) {
						B[j][k] = (B[j][k] * value1 - B[i][k] * value2) / denom;
					}
				}
				denom = value1;
			}
			if (exchanges % 2) {
				return -B[N - 1][N - 1];
			} else {
				return B[N - 1][N - 1];
			}
		}

		function MatrixCofactor(i, j, __A) {        //Алгебраическое дополнение матрицы
			var N = __A.length, sign = ((i + j) % 2 == 0) ? 1 : -1;

			for (var m = 0; m < N; m++) {
				for (var n = j + 1; n < N; n++) {
					__A[m][n - 1] = __A[m][n];
				}
				__A[m].length--;
			}
			for (var k = (i + 1); k < N; k++) {
				__A[k - 1] = __A[k];
			}
			__A.length--;

			return sign * Determinant(__A);
		}

		function AdjugateMatrix(_A) {             //Союзная (присоединённая) матрица к A. (матрица adj(A), составленная из алгебраических дополнений A).
			var N = _A.length, B = [], adjA = [];

			for (var i = 0; i < N; i++) {
				adjA[i] = [];
				for (var j = 0; j < N; j++) {
					for (var m = 0; m < N; m++) {
						B[m] = [];
						for (var n = 0; n < N; n++) {
							B[m][n] = _A[m][n];
						}
					}
					adjA[i][j] = MatrixCofactor(j, i, B);
				}
			}

			return adjA;
		}

		function InverseMatrix(A) {
			var i, j;
			for (i = 0; i < A.length; i++) {
				for (j = 0; j < A[i].length; j++) {
					if (A[i][j] instanceof cEmpty || A[i][j] instanceof cString) {
						return new cError(cErrorType.not_available);
					} else {
						A[i][j] = A[i][j].getValue();
					}
				}
			}

			var detA = Determinant(A), invertA, res;

			if (detA != 0) {
				invertA = AdjugateMatrix(A);
				var datA = 1 / detA;
				for (i = 0; i < invertA.length; i++) {
					for (j = 0; j < invertA[i].length; j++) {
						invertA[i][j] = new cNumber(datA * invertA[i][j]);
					}
				}
				res = new cArray();
				res.fillFromArray(invertA);
			} else {
				res = new cError(cErrorType.not_available);
			}

			return res;
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else {
			return this.value = new cError(cErrorType.not_available);
		}

		if (arg0[0].length != arg0.length) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = InverseMatrix(arg0);
	};
	cMINVERSE.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMMULT() {
		this.name = "MMULT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMMULT.prototype = Object.create(cBaseFunction.prototype);
	cMMULT.prototype.constructor = cMMULT;
	cMMULT.prototype.argumentsMin = 2;
	cMMULT.prototype.argumentsMax = 2;
	cMMULT.prototype.numFormat = AscCommonExcel.cNumFormatNone;
	cMMULT.prototype.Calculate = function (arg) {

		function mult(A, B) {
			var i, j;
			for (i = 0; i < A.length; i++) {
				for (j = 0; j < A[i].length; j++) {
					if (A[i][j] instanceof cEmpty || A[i][j] instanceof cString) {
						return new cError(cErrorType.not_available);
					}
				}
			}
			for (i = 0; i < B.length; i++) {
				for (j = 0; j < B[i].length; j++) {
					if (B[i][j] instanceof cEmpty || B[i][j] instanceof cString) {
						return new cError(cErrorType.not_available);
					}
				}
			}

			if (A.length != B[0].length) {
				return new cError(cErrorType.wrong_value_type);
			}
			var C = new Array(A.length);
			for (i = 0; i < A.length; i++) {
				C[i] = new Array(B[0].length);
				for (j = 0; j < B[0].length; j++) {
					C[i][j] = 0;
					for (var k = 0; k < B.length; k++) {
						C[i][j] += A[i][k].getValue() * B[k][j].getValue();
					}
					C[i][j] = new cNumber(C[i][j]);
				}
			}
			var res = new cArray();
			res.fillFromArray(C);
			return res;
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else {
			return this.value = new cError(cErrorType.not_available);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArray) {
			arg1 = arg1.getMatrix();
		} else {
			return this.value = new cError(cErrorType.not_available);
		}

		return this.value = mult(arg0, arg1);

	};
	cMMULT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array1, array2 )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMOD() {
		this.name = "MOD";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMOD.prototype = Object.create(cBaseFunction.prototype);
	cMOD.prototype.constructor = cMOD;
	cMOD.prototype.argumentsMin = 2;
	cMOD.prototype.argumentsMax = 2;
	cMOD.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = new cNumber((b.getValue() < 0 ? -1 : 1) *
							( Math.abs(a.getValue()) % Math.abs(b.getValue()) ));
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {

					this.array[r][c] =
						new cNumber((b.getValue() < 0 ? -1 : 1) * ( Math.abs(a.getValue()) % Math.abs(b.getValue()) ));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] =
						new cNumber((b.getValue() < 0 ? -1 : 1) * ( Math.abs(a.getValue()) % Math.abs(b.getValue()) ));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		if (!(arg0 instanceof cNumber) || ( arg1 && !(arg0 instanceof cNumber) )) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg1.getValue() == 0) {
			return this.value = new cError(cErrorType.division_by_zero);
		}

		return this.value =
			new cNumber((arg1.getValue() < 0 ? -1 : 1) * ( Math.abs(arg0.getValue()) % Math.abs(arg1.getValue()) ));

	};
	cMOD.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, y )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMROUND() {
		this.name = "MROUND";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMROUND.prototype = Object.create(cBaseFunction.prototype);
	cMROUND.prototype.constructor = cMROUND;
	cMROUND.prototype.argumentsMin = 2;
	cMROUND.prototype.argumentsMax = 2;
	cMROUND.prototype.Calculate = function (arg) {

		var multiple;

		function mroundHelper(num) {
			var multiplier = Math.pow(10, Math.floor(Math.log10(Math.abs(num))) - cExcelSignificantDigits + 1);
			var nolpiat = 0.5 * (num > 0 ? 1 : num < 0 ? -1 : 0) * multiplier;
			var y = (num + nolpiat) / multiplier;
			y = y / Math.abs(y) * Math.floor(Math.abs(y));
			var x = y * multiplier / multiple;

			// var x = number / multiple;
			nolpiat =
				5 * (x / Math.abs(x)) * Math.pow(10, Math.floor(Math.log10(Math.abs(x))) - cExcelSignificantDigits);
			x = x + nolpiat;
			x = x | x;

			return x * multiple;
		}

		function f(a, b, r, c) {
			if (a instanceof cNumber && b instanceof cNumber) {
				if (a.getValue() == 0) {
					this.array[r][c] = new cNumber(0);
				} else if (a.getValue() < 0 && b.getValue() > 0 || arg0.getValue() > 0 && b.getValue() < 0) {
					this.array[r][c] = new cError(cErrorType.not_numeric);
				} else {
					multiple = b.getValue();
					this.array[r][c] = new cNumber(mroundHelper(a.getValue() + b.getValue() / 2))
				}
			} else {
				this.array[r][c] = new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}
		if (arg0 instanceof cString || arg1 instanceof cString) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					f.call(this, elem, arg1.getElementRowCol(r, c), r, c)
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				f.call(this, elem, arg1, r, c);
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				f.call(this, arg0, elem, r, c)
			});
			return this.value = arg1;
		}

		if (arg1.getValue() == 0) {
			return this.value = new cNumber(0);
		}

		if (arg0.getValue() < 0 && arg1.getValue() > 0 || arg0.getValue() > 0 && arg1.getValue() < 0) {
			return this.value = new cError(cErrorType.not_numeric);
		}

		multiple = arg1.getValue();
		return this.value = new cNumber(mroundHelper(arg0.getValue() + arg1.getValue() / 2));
	};
	cMROUND.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, multiple )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cMULTINOMIAL() {
		this.name = "MULTINOMIAL";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cMULTINOMIAL.prototype = Object.create(cBaseFunction.prototype);
	cMULTINOMIAL.prototype.constructor = cMULTINOMIAL;
	cMULTINOMIAL.prototype.argumentsMin = 1;
	cMULTINOMIAL.prototype.Calculate = function (arg) {
		var arg0 = new cNumber(0), fact = 1;

		for (var i = 0; i < arg.length; i++) {
			if (arg[i] instanceof cArea || arg[i] instanceof cArea3D) {
				var _arrVal = arg[i].getValue();
				for (var j = 0; j < _arrVal.length; j++) {
					if (_arrVal[j] instanceof cNumber) {
						if (_arrVal[j].getValue() < 0) {
							return this.value = new cError(cError.not_numeric);
						}
						arg0 = _func[arg0.type][_arrVal[j].type](arg0, _arrVal[j], "+");
						fact *= Math.fact(_arrVal[j].getValue());
					} else if (_arrVal[j] instanceof cError) {
						return this.value = _arrVal[j];
					} else {
						return this.value = new cError(cError.wrong_value_type);
					}
				}
			} else if (arg[i] instanceof cArray) {
				if (arg[i].foreach(function (arrElem) {
						if (arrElem instanceof cNumber) {
							if (arrElem.getValue() < 0) {
								return true;
							}

							arg0 = _func[arg0.type][arrElem.type](arg0, arrElem, "+");
							fact *= Math.fact(arrElem.getValue());
						} else {
							return true;
						}
					})) {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			} else if (arg[i] instanceof cRef || arg[i] instanceof cRef3D) {
				var _arg = arg[i].getValue();

				if (_arg.getValue() < 0) {
					return this.value = new cError(cErrorType.not_numeric);
				}

				if (_arg instanceof cNumber) {
					if (_arg.getValue() < 0) {
						return this.value = new cError(cError.not_numeric);
					}
					arg0 = _func[arg0.type][_arg.type](arg0, _arg, "+");
					fact *= Math.fact(_arg.getValue());
				} else if (_arg instanceof cError) {
					return this.value = _arg;
				} else {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			} else if (arg[i] instanceof cNumber) {

				if (arg[i].getValue() < 0) {
					return this.value = new cError(cErrorType.not_numeric);
				}

				arg0 = _func[arg0.type][arg[i].type](arg0, arg[i], "+");
				fact *= Math.fact(arg[i].getValue());
			} else if (arg[i] instanceof cError) {
				return this.value = arg[i];
			} else {
				return this.value = new cError(cErrorType.wrong_value_type);
			}

			if (arg0 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}

		if (arg0.getValue() > 170) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = new cNumber(Math.fact(arg0.getValue()) / fact);
	};
	cMULTINOMIAL.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cODD() {
		this.name = "ODD";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cODD.prototype = Object.create(cBaseFunction.prototype);
	cODD.prototype.constructor = cODD;
	cODD.prototype.argumentsMin = 1;
	cODD.prototype.argumentsMax = 1;
	cODD.prototype.Calculate = function (arg) {

		function oddHelper(arg) {
			var arg0 = arg.getValue();
			if (arg0 >= 0) {
				arg0 = Math.ceil(arg0);
				if ((arg0 & 1) == 1) {
					return new cNumber(arg0);
				} else {
					return new cNumber(arg0 + 1);
				}
			} else {
				arg0 = Math.floor(arg0);
				if ((arg0 & 1) == 1) {
					return new cNumber(arg0);
				} else {
					return new cNumber(arg0 - 1);
				}
			}
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					this.array[r][c] = oddHelper(elem);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg0 instanceof cNumber) {
			return this.value = oddHelper(arg0);
		}
		return this.value = new cError(cErrorType.wrong_value_type);

	};
	cODD.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cPI() {
		this.name = "PI";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cPI.prototype = Object.create(cBaseFunction.prototype);
	cPI.prototype.constructor = cPI;
	cPI.prototype.argumentsMax = 0;
	cPI.prototype.Calculate = function () {
		return new cNumber(Math.PI);
	};
	cPI.prototype.getInfo = function () {
		return {
			name: this.name, args: "()"
		}
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cPOWER() {
		this.name = "POWER";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cPOWER.prototype = Object.create(cBaseFunction.prototype);
	cPOWER.prototype.constructor = cPOWER;
	cPOWER.prototype.argumentsMin = 2;
	cPOWER.prototype.argumentsMax = 2;
	cPOWER.prototype.Calculate = function (arg) {

		function powerHelper(a, b) {
			if (a == 0 && b < 0) {
				return new cError(cErrorType.division_by_zero);
			}
			if (a == 0 && b == 0) {
				return new cError(cErrorType.not_numeric);
			}

			return new cNumber(Math.pow(a, b));
		}

		function f(a, b, r, c) {
			if (a instanceof cNumber && b instanceof cNumber) {
				this.array[r][c] = powerHelper(a.getValue(), b.getValue());
			} else {
				this.array[r][c] = new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg1 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					f.call(this, elem, arg1.getElementRowCol(r, c), r, c);
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				f.call(this, elem, arg1, r, c)
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				f.call(this, arg0, elem, r, c);
			});
			return this.value = arg1;
		}

		if (!(arg0 instanceof cNumber) || ( arg1 && !(arg0 instanceof cNumber) )) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = powerHelper(arg0.getValue(), arg1.getValue());

	};
	cPOWER.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x, y )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cPRODUCT() {
		this.name = "PRODUCT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cPRODUCT.prototype = Object.create(cBaseFunction.prototype);
	cPRODUCT.prototype.constructor = cPRODUCT;
	cPRODUCT.prototype.argumentsMin = 1;
	cPRODUCT.prototype.Calculate = function (arg) {
		var element, arg0 = new cNumber(1);
		for (var i = 0; i < arg.length; i++) {
			element = arg[i];
			if (cElementType.cellsRange === element.type || cElementType.cellsRange3D === element.type) {
				var _arrVal = element.getValue(this.checkExclude, this.excludeHiddenRows);
				for (var j = 0; j < _arrVal.length; j++) {
					arg0 = _func[arg0.type][_arrVal[j].type](arg0, _arrVal[j], "*");
					if (cElementType.error === arg0.type) {
						return this.value = arg0;
					}
				}
			} else if (cElementType.cell === element.type || cElementType.cell3D === element.type) {
				if (!this.checkExclude || !element.isHidden(this.excludeHiddenRows)) {
					var _arg = element.getValue();
					arg0 = _func[arg0.type][_arg.type](arg0, _arg, "*");
				}
			} else if (cElementType.array === element.type) {
				element.foreach(function (elem) {
					if (cElementType.string === elem.type || cElementType.bool === elem.type ||
						cElementType.empty === elem.type) {
						return;
					}

					arg0 = _func[arg0.type][elem.type](arg0, elem, "*");
				})
			} else {
				arg0 = _func[arg0.type][element.type](arg0, element, "*");
			}
			if (cElementType.error === arg0.type) {
				return this.value = arg0;
			}

		}
		return this.value = arg0;
	};
	cPRODUCT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cQUOTIENT() {
		this.name = "QUOTIENT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cQUOTIENT.prototype = Object.create(cBaseFunction.prototype);
	cQUOTIENT.prototype.constructor = cQUOTIENT;
	cQUOTIENT.prototype.argumentsMin = 2;
	cQUOTIENT.prototype.argumentsMax = 2;
	cQUOTIENT.prototype.Calculate = function (arg) {

		function quotient(a, b) {
			if (b.getValue() != 0) {
				return new cNumber(parseInt(a.getValue() / b.getValue()));
			} else {
				return new cError(cErrorType.division_by_zero);
			}
		}

		function f(a, b, r, c) {
			if (a instanceof cNumber && b instanceof cNumber) {
				this.array[r][c] = quotient(a, b);
			} else {
				this.array[r][c] = new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg1 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					f.call(this, elem, arg1.getElementRowCol(r, c), r, c);
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				f.call(this, elem, arg1, r, c)
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				f.call(this, arg0, elem, r, c);
			});
			return this.value = arg1;
		}

		if (!(arg0 instanceof cNumber) || ( arg1 && !(arg0 instanceof cNumber) )) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}


		return this.value = quotient(arg0, arg1);
	};
	cQUOTIENT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( dividend , divisor )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cRADIANS() {
		this.name = "RADIANS";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cRADIANS.prototype = Object.create(cBaseFunction.prototype);
	cRADIANS.prototype.constructor = cRADIANS;
	cRADIANS.prototype.argumentsMin = 1;
	cRADIANS.prototype.argumentsMax = 1;
	cRADIANS.prototype.Calculate = function (arg) {

		function radiansHelper(ang) {
			return ang * Math.PI / 180
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();

		if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					this.array[r][c] = new cNumber(radiansHelper(elem.getValue()));
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			return this.value = ( arg0 instanceof cError ? arg0 : new cNumber(radiansHelper(arg0.getValue())) );
		}

		return this.value = arg0;

	};
	cRADIANS.prototype.getInfo = function () {
		return {
			name: this.name, args: "( angle )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cRAND() {
		this.name = "RAND";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cRAND.prototype = Object.create(cBaseFunction.prototype);
	cRAND.prototype.constructor = cRAND;
	cRAND.prototype.argumentsMax = 0;
	cRAND.prototype.Calculate = function () {
		return this.setCA(new cNumber(Math.random()), true);
	};
	cRAND.prototype.getInfo = function () {
		return {
			name: this.name, args: "()"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cRANDBETWEEN() {
		this.name = "RANDBETWEEN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cRANDBETWEEN.prototype = Object.create(cBaseFunction.prototype);
	cRANDBETWEEN.prototype.constructor = cRANDBETWEEN;
	cRANDBETWEEN.prototype.argumentsMin = 2;
	cRANDBETWEEN.prototype.argumentsMax = 2;
	cRANDBETWEEN.prototype.Calculate = function (arg) {

		function randBetween(a, b) {
			return new cNumber(Math.round(Math.random() * Math.abs(a - b)) + a);
		}

		function f(a, b, r, c) {
			if (a instanceof cNumber && b instanceof cNumber) {
				this.array[r][c] = randBetween(a.getValue(), b.getValue());
			} else {
				this.array[r][c] = new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg1 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					f.call(this, elem, arg1.getElementRowCol(r, c), r, c);
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				f.call(this, elem, arg1, r, c)
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				f.call(this, arg0, elem, r, c);
			});
			return this.value = arg1;
		}

		if (!(arg0 instanceof cNumber) || ( arg1 && !(arg0 instanceof cNumber) )) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}


		return this.setCA(new cNumber(randBetween(arg0.getValue(), arg1.getValue())), true);
	};
	cRANDBETWEEN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( lower-bound , upper-bound )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cROMAN() {
		this.name = "ROMAN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cROMAN.prototype = Object.create(cBaseFunction.prototype);
	cROMAN.prototype.constructor = cROMAN;
	cROMAN.prototype.argumentsMin = 2;
	cROMAN.prototype.argumentsMax = 2;
	cROMAN.prototype.Calculate = function (arg) {
		function roman(num, mode) {
			if ((mode >= 0) && (mode < 5) && (num >= 0) && (num < 4000)) {
				var chars = ['M', 'D', 'C', 'L', 'X', 'V', 'I'], values = [1000, 500, 100, 50, 10, 5,
					1], maxIndex = values.length - 1, aRoman = "", index, digit, index2, steps;
				for (var i = 0; i <= maxIndex / 2; i++) {
					index = 2 * i;
					digit = parseInt(num / values[index]);

					if ((digit % 5) == 4) {
						index2 = (digit == 4) ? index - 1 : index - 2;
						steps = 0;
						while ((steps < mode) && (index < maxIndex)) {
							steps++;
							if (values[index2] - values[index + 1] <= num) {
								index++;
							} else {
								steps = mode;
							}
						}
						aRoman += chars[index];
						aRoman += chars[index2];
						num = ( num + values[index] );
						num = ( num - values[index2] );
					} else {
						if (digit > 4) {
							aRoman += chars[index - 1];
						}
						for (var j = digit % 5; j > 0; j--) {
							aRoman += chars[index];
						}
						num %= values[index];
					}
				}
				return new cString(aRoman);
			} else {
				return new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D || arg1 instanceof cArea || arg1 instanceof cArea3D) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = arg0.tocNumber();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = roman(a.getValue(), b.getValue());
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem, b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roman(a.getValue(), b.getValue());
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0, b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roman(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		return this.value = roman(arg0.getValue(), arg1.getValue());

	};
	cROMAN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( number, form )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cROUND() {
		this.name = "ROUND";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cROUND.prototype = Object.create(cBaseFunction.prototype);
	cROUND.prototype.constructor = cROUND;
	cROUND.prototype.argumentsMin = 2;
	cROUND.prototype.argumentsMax = 2;
	cROUND.prototype.Calculate = function (arg) {

		function SignZeroPositive(number) {
			return number < 0 ? -1 : 1;
		}

		function truncate(n) {
			return Math[n > 0 ? "floor" : "ceil"](n);
		}

		function Floor(number, significance) {
			var quotient = number / significance;
			if (quotient == 0) {
				return 0;
			}
			var nolpiat = 5 * Math.sign(quotient) *
				Math.pow(10, Math.floor(Math.log10(Math.abs(quotient))) - cExcelSignificantDigits);
			return truncate(quotient + nolpiat) * significance;
		}

		function roundHelper(number, num_digits) {
			if (num_digits > AscCommonExcel.cExcelMaxExponent) {
				if (Math.abs(number) < 1 || num_digits < 1e10) // The values are obtained experimentally
				{
					return new cNumber(number);
				}
				return new cNumber(0);
			} else if (num_digits < AscCommonExcel.cExcelMinExponent) {
				if (Math.abs(number) < 0.01) // The values are obtained experimentally
				{
					return new cNumber(number);
				}
				return new cNumber(0);
			}

			var significance = SignZeroPositive(number) * Math.pow(10, -truncate(num_digits));

			number += significance / 2;

			if (number / significance == Infinity) {
				return new cNumber(number);
			}

			return new cNumber(Floor(number, significance));

		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cRef || arg0 instanceof cRef3D) {
			arg0 = arg0.getValue();
			if (arg0 instanceof cError) {
				return this.value = arg0;
			} else if (arg0 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg0 = arg0.tocNumber();
			}
		} else {
			arg0 = arg0.tocNumber();
		}

		if (arg1 instanceof cRef || arg1 instanceof cRef3D) {
			arg1 = arg1.getValue();
			if (arg1 instanceof cError) {
				return this.value = arg1;
			} else if (arg1 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg1 = arg1.tocNumber();
			}
		} else {
			arg1 = arg1.tocNumber();
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = roundHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem;
				var b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roundHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0;
				var b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roundHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		var number = arg0.getValue(), num_digits = arg1.getValue();

		return this.value = roundHelper(number, num_digits);

	};
	cROUND.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x , number-digits )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cROUNDDOWN() {
		this.name = "ROUNDDOWN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cROUNDDOWN.prototype = Object.create(cBaseFunction.prototype);
	cROUNDDOWN.prototype.constructor = cROUNDDOWN;
	cROUNDDOWN.prototype.argumentsMin = 2;
	cROUNDDOWN.prototype.argumentsMax = 2;
	cROUNDDOWN.prototype.Calculate = function (arg) {
		function rounddownHelper(number, num_digits) {
			if (num_digits > AscCommonExcel.cExcelMaxExponent) {
				if (Math.abs(number) >= 1e-100 || num_digits <= 98303) { // The values are obtained experimentally
					return new cNumber(number);
				}
				return new cNumber(0);
			} else if (num_digits < AscCommonExcel.cExcelMinExponent) {
				if (Math.abs(number) >= 1e100) { // The values are obtained experimentally
					return new cNumber(number);
				}
				return new cNumber(0);
			}

			var significance = Math.pow(10, -( num_digits | num_digits ));

			if (Number.POSITIVE_INFINITY == Math.abs(number / significance)) {
				return new cNumber(number);
			}
			var x = number * Math.pow(10, num_digits);
			x = x | x;
			return new cNumber(x * significance);
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cRef || arg0 instanceof cRef3D) {
			arg0 = arg0.getValue();
			if (arg0 instanceof cError) {
				return this.value = arg0;
			} else if (arg0 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg0 = arg0.tocNumber();
			}
		} else {
			arg0 = arg0.tocNumber();
		}

		if (arg1 instanceof cRef || arg1 instanceof cRef3D) {
			arg1 = arg1.getValue();
			if (arg1 instanceof cError) {
				return this.value = arg1;
			} else if (arg1 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg1 = arg1.tocNumber();
			}
		} else {
			arg1 = arg1.tocNumber();
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = rounddownHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem;
				var b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = rounddownHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0;
				var b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = rounddownHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		var number = arg0.getValue(), num_digits = arg1.getValue();
		return this.value = rounddownHelper(number, num_digits);

	};
	cROUNDDOWN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x , number-digits )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cROUNDUP() {
		this.name = "ROUNDUP";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cROUNDUP.prototype = Object.create(cBaseFunction.prototype);
	cROUNDUP.prototype.constructor = cROUNDUP;
	cROUNDUP.prototype.argumentsMin = 2;
	cROUNDUP.prototype.argumentsMax = 2;
	cROUNDUP.prototype.Calculate = function (arg) {
		function roundupHelper(number, num_digits) {
			if (num_digits > AscCommonExcel.cExcelMaxExponent) {
				if (Math.abs(number) >= 1e-100 || num_digits <= 98303) { // The values are obtained experimentally
					return new cNumber(number);
				}
				return new cNumber(0);
			} else if (num_digits < AscCommonExcel.cExcelMinExponent) {
				if (Math.abs(number) >= 1e100) { // The values are obtained experimentally
					return new cNumber(number);
				}
				return new cNumber(0);
			}

			var significance = Math.pow(10, -( num_digits | num_digits ));

			if (Number.POSITIVE_INFINITY == Math.abs(number / significance)) {
				return new cNumber(number);
			}
			var x = number * Math.pow(10, num_digits);
			x = (x | x) + (x > 0 ? 1 : x < 0 ? -1 : 0) * 1;
			return new cNumber(x * significance);
		}

		var arg0 = arg[0], arg1 = arg[1];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cRef || arg0 instanceof cRef3D) {
			arg0 = arg0.getValue();
			if (arg0 instanceof cError) {
				return this.value = arg0;
			} else if (arg0 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg0 = arg0.tocNumber();
			}
		} else {
			arg0 = arg0.tocNumber();
		}

		if (arg1 instanceof cRef || arg1 instanceof cRef3D) {
			arg1 = arg1.getValue();
			if (arg1 instanceof cError) {
				return this.value = arg1;
			} else if (arg1 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg1 = arg1.tocNumber();
			}
		} else {
			arg1 = arg1.tocNumber();
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = roundupHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem;
				var b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roundupHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0;
				var b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = roundupHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		var number = arg0.getValue(), num_digits = arg1.getValue();
		return this.value = roundupHelper(number, num_digits);

	};
	cROUNDUP.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x , number-digits )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSERIESSUM() {
		this.name = "SERIESSUM";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSERIESSUM.prototype = Object.create(cBaseFunction.prototype);
	cSERIESSUM.prototype.constructor = cSERIESSUM;
	cSERIESSUM.prototype.argumentsMin = 4;
	cSERIESSUM.prototype.argumentsMax = 4;
	cSERIESSUM.prototype.Calculate = function (arg) {

		function SERIESSUM(x, n, m, a) {

			x = x.getValue();
			n = n.getValue();
			m = m.getValue();

			for (var i = 0; i < a.length; i++) {
				if (!( a[i] instanceof cNumber)) {
					return new cError(cErrorType.wrong_value_type);
				}
				a[i] = a[i].getValue();
			}

			function sumSeries(x, n, m, a) {
				var sum = 0;
				for (var i = 0; i < a.length; i++) {
					sum += a[i] * Math.pow(x, n + i * m)
				}
				return sum;
			}

			return new cNumber(sumSeries(x, n, m, a));
		}

		var arg0 = arg[0], arg1 = arg[1], arg2 = arg[2], arg3 = arg[3];
		if (arg0 instanceof cNumber || arg0 instanceof cRef || arg0 instanceof cRef3D) {
			arg0 = arg0.tocNumber();
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg1 instanceof cNumber || arg1 instanceof cRef || arg1 instanceof cRef3D) {
			arg1 = arg1.tocNumber();
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg2 instanceof cNumber || arg2 instanceof cRef || arg2 instanceof cRef3D) {
			arg2 = arg2.tocNumber();
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg3 instanceof cNumber || arg3 instanceof cRef || arg3 instanceof cRef3D) {
			arg3 = [arg3.tocNumber()];
		} else if (arg3 instanceof cArea || arg3 instanceof cArea3D) {
			arg3 = arg3.getValue();
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = SERIESSUM(arg0, arg1, arg2, arg3);

	};
	cSERIESSUM.prototype.getInfo = function () {
		return {
			name: this.name, args: "( input-value , initial-power , step , coefficients )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSIGN() {
		this.name = "SIGN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSIGN.prototype = Object.create(cBaseFunction.prototype);
	cSIGN.prototype.constructor = cSIGN;
	cSIGN.prototype.argumentsMin = 1;
	cSIGN.prototype.argumentsMax = 1;
	cSIGN.prototype.Calculate = function (arg) {

		function signHelper(arg) {
			if (arg < 0) {
				return new cNumber(-1.0);
			} else if (arg == 0) {
				return new cNumber(0.0);
			} else {
				return new cNumber(1.0);
			}
		}

		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}

		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = elem.getValue();
					this.array[r][c] = signHelper(a)
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = arg0.getValue();
			return this.value = signHelper(a);
		}
		return this.value = arg0;

	};
	cSIGN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSIN() {
		this.name = "SIN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSIN.prototype = Object.create(cBaseFunction.prototype);
	cSIN.prototype.constructor = cSIN;
	cSIN.prototype.argumentsMin = 1;
	cSIN.prototype.argumentsMax = 1;
	cSIN.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.sin(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.sin(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cSIN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSINH() {
		this.name = "SINH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSINH.prototype = Object.create(cBaseFunction.prototype);
	cSINH.prototype.constructor = cSINH;
	cSINH.prototype.argumentsMin = 1;
	cSINH.prototype.argumentsMax = 1;
	cSINH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.sinh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.sinh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cSINH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSQRT() {
		this.name = "SQRT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSQRT.prototype = Object.create(cBaseFunction.prototype);
	cSQRT.prototype.constructor = cSQRT;
	cSQRT.prototype.argumentsMin = 1;
	cSQRT.prototype.argumentsMax = 1;
	cSQRT.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.sqrt(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.sqrt(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cSQRT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSQRTPI() {
		this.name = "SQRTPI";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSQRTPI.prototype = Object.create(cBaseFunction.prototype);
	cSQRTPI.prototype.constructor = cSQRTPI;
	cSQRTPI.prototype.argumentsMin = 1;
	cSQRTPI.prototype.argumentsMax = 1;
	cSQRTPI.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.sqrt(elem.getValue() * Math.PI);
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.sqrt(arg0.getValue() * Math.PI);
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cSQRTPI.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUBTOTAL() {
		this.name = "SUBTOTAL";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUBTOTAL.prototype = Object.create(cBaseFunction.prototype);
	cSUBTOTAL.prototype.constructor = cSUBTOTAL;
	cSUBTOTAL.prototype.argumentsMin = 1;
	cSUBTOTAL.prototype.Calculate = function (arg) {
		var f, exclude = false, arg0 = arg[0];

		if (cElementType.cellsRange === arg0.type || cElementType.cellsRange3D === arg0.type) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (cElementType.number !== arg0.type) {
			return this.value = arg0;
		}

		arg0 = arg0.getValue();

		switch (arg0) {
			case cSubTotalFunctionType.excludes.AVERAGE:
				exclude = true;
			case cSubTotalFunctionType.includes.AVERAGE:
				f = new AscCommonExcel.cAVERAGE();
				break;
			case cSubTotalFunctionType.excludes.COUNT:
				exclude = true;
			case cSubTotalFunctionType.includes.COUNT:
				f = new AscCommonExcel.cCOUNT();
				break;
			case cSubTotalFunctionType.excludes.COUNTA:
				exclude = true;
			case cSubTotalFunctionType.includes.COUNTA:
				f = new AscCommonExcel.cCOUNTA();
				break;
			case cSubTotalFunctionType.excludes.MAX:
				exclude = true;
			case cSubTotalFunctionType.includes.MAX:
				f = new AscCommonExcel.cMAX();
				f.setArgumentsCount(arg.length - 1);
				break;
			case cSubTotalFunctionType.excludes.MIN:
				exclude = true;
			case cSubTotalFunctionType.includes.MIN:
				f = new AscCommonExcel.cMIN();
				f.setArgumentsCount(arg.length - 1);
				break;
			case cSubTotalFunctionType.excludes.PRODUCT:
				exclude = true;
			case cSubTotalFunctionType.includes.PRODUCT:
				f = new cPRODUCT();
				break;
			case cSubTotalFunctionType.excludes.STDEV:
				exclude = true;
			case cSubTotalFunctionType.includes.STDEV:
				f = new AscCommonExcel.cSTDEV();
				break;
			case cSubTotalFunctionType.excludes.STDEVP:
				exclude = true;
			case cSubTotalFunctionType.includes.STDEVP:
				f = new AscCommonExcel.cSTDEVP();
				break;
			case cSubTotalFunctionType.excludes.SUM:
				exclude = true;
			case cSubTotalFunctionType.includes.SUM:
				f = new cSUM();
				break;
			case cSubTotalFunctionType.excludes.VAR:
				exclude = true;
			case cSubTotalFunctionType.includes.VAR:
				f = new AscCommonExcel.cVAR();
				break;
			case cSubTotalFunctionType.excludes.VARP:
				exclude = true;
			case cSubTotalFunctionType.includes.VARP:
				f = new AscCommonExcel.cVARP();
				break;
		}
		if (f) {
			f.checkExclude = true;
			f.excludeHiddenRows = exclude;
			this.value = f.Calculate(arg.slice(1));
		}

		return this.value;
	};
	cSUBTOTAL.prototype.getInfo = function () {
		return {
			name: this.name, args: "( function-number , argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUM() {
		this.name = "SUM";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUM.prototype = Object.create(cBaseFunction.prototype);
	cSUM.prototype.constructor = cSUM;
	cSUM.prototype.argumentsMin = 1;
	cSUM.prototype.Calculate = function (arg) {
		var element, _arg, arg0 = new cNumber(0);
		for (var i = 0; i < arg.length; i++) {
			element = arg[i];
			if (cElementType.cellsRange === element.type || cElementType.cellsRange3D === element.type) {
				var _arrVal = element.getValue(this.checkExclude, this.excludeHiddenRows);
				for (var j = 0; j < _arrVal.length; j++) {
					if (cElementType.bool !== _arrVal[j].type && cElementType.string !== _arrVal[j].type) {
						arg0 = _func[arg0.type][_arrVal[j].type](arg0, _arrVal[j], "+");
					}
					if (cElementType.error === arg0.type) {
						return this.value = arg0;
					}
				}
			} else if (cElementType.cell === element.type || cElementType.cell3D === element.type) {
				if (!this.checkExclude || !element.isHidden(this.excludeHiddenRows)) {
					_arg = element.getValue();
					if (cElementType.bool !== _arg.type && cElementType.string !== _arg.type) {
						arg0 = _func[arg0.type][_arg.type](arg0, _arg, "+");
					}
				}
			} else if (cElementType.array === element.type) {
				element.foreach(function (arrElem) {
					if (cElementType.bool !== arrElem.type && cElementType.string !== arrElem.type &&
						cElementType.empty !== arrElem.type) {
						arg0 = _func[arg0.type][arrElem.type](arg0, arrElem, "+");
					}
				});
			} else {
				_arg = element.tocNumber();
				arg0 = _func[arg0.type][_arg.type](arg0, _arg, "+");
			}
			if (cElementType.error === arg0.type) {
				return this.value = arg0;
			}

		}

		return this.value = arg0;
	};
	cSUM.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMIF() {
		this.name = "SUMIF";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMIF.prototype = Object.create(cBaseFunction.prototype);
	cSUMIF.prototype.constructor = cSUMIF;
	cSUMIF.prototype.argumentsMin = 2;
	cSUMIF.prototype.argumentsMax = 3;
	cSUMIF.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1], arg2 = arg[2] ? arg[2] : arg[0], _sum = 0, matchingInfo;
		if (cElementType.cell !== arg0.type && cElementType.cell3D !== arg0.type &&
			cElementType.cellsRange !== arg0.type) {
			if (cElementType.cellsRange3D === arg0.type) {
				arg0 = arg0.tocArea();
				if (!arg0) {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			} else {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}

		if (cElementType.cell !== arg2.type && cElementType.cell3D !== arg2.type &&
			cElementType.cellsRange !== arg2.type) {
			if (cElementType.cellsRange3D === arg2.type) {
				arg2 = arg2.tocArea();
				if (!arg2) {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			} else {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}

		if (cElementType.cellsRange === arg1.type || cElementType.cellsRange3D === arg1.type) {
			arg1 = arg1.cross(arguments[1].bbox);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg1 = arg1.tocString();

		if (cElementType.string !== arg1.type) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		matchingInfo = AscCommonExcel.matchingValue(arg1.toString());
		if (cElementType.cellsRange === arg0.type) {
			var arg0Matrix = arg0.getMatrix(), arg2Matrix = arg2.getMatrix(), valMatrix2;
			for (var i = 0; i < arg0Matrix.length; i++) {
				for (var j = 0; j < arg0Matrix[i].length; j++) {
					if (arg2Matrix[i] && (valMatrix2 = arg2Matrix[i][j]) && cElementType.number === valMatrix2.type &&
						AscCommonExcel.matching(arg0Matrix[i][j], matchingInfo)) {
						_sum += valMatrix2.getValue();
					}
				}
			}
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = new cNumber(_sum);
	};
	cSUMIF.prototype.getInfo = function () {
		return {
			name: this.name, args: "( cell-range, selection-criteria [ , sum-range ] )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMIFS() {
		this.name = "SUMIFS";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMIFS.prototype = Object.create(cBaseFunction.prototype);
	cSUMIFS.prototype.constructor = cSUMIFS;
	cSUMIFS.prototype.argumentsMin = 3;
	cSUMIFS.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (cElementType.cell !== arg0.type && cElementType.cell3D !== arg0.type &&
			cElementType.cellsRange !== arg0.type) {
			if (cElementType.cellsRange3D === arg0.type) {
				arg0 = arg0.tocArea();
				if (!arg0) {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			} else {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}

		var arg0Matrix = arg0.getMatrix();
		var i, j, arg1, arg2, matchingInfo;
		for (var k = 1; k < arg.length; k += 2) {
			arg1 = arg[k];
			arg2 = arg[k + 1];

			if (cElementType.cell !== arg1.type && cElementType.cell3D !== arg1.type &&
				cElementType.cellsRange !== arg1.type) {
				if (cElementType.cellsRange3D === arg1.type) {
					arg1 = arg1.tocArea();
					if (!arg1) {
						return this.value = new cError(cErrorType.wrong_value_type);
					}
				} else {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
			}

			if (cElementType.cellsRange === arg2.type || cElementType.cellsRange3D === arg2.type) {
				arg2 = arg2.cross(arguments[1].bbox);
			} else if (cElementType.array === arg2.type) {
				arg2 = arg2.getElementRowCol(0, 0);
			}

			arg2 = arg2.tocString();

			if (cElementType.string !== arg2.type) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}

			matchingInfo = AscCommonExcel.matchingValue(arg2.toString());

			var arg1Matrix = arg1.getMatrix();
			if (arg0Matrix.length !== arg1Matrix.length) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
			for (i = 0; i < arg1Matrix.length; ++i) {
				if (arg0Matrix[i].length !== arg1Matrix[i].length) {
					return this.value = new cError(cErrorType.wrong_value_type);
				}
				for (j = 0; j < arg1Matrix[i].length; ++j) {
					if (arg0Matrix[i][j] && !AscCommonExcel.matching(arg1Matrix[i][j], matchingInfo)) {
						arg0Matrix[i][j] = null;
					}
				}
			}
		}

		var _sum = 0;
		var valMatrix0;
		for (i = 0; i < arg0Matrix.length; ++i) {
			for (j = 0; j < arg0Matrix[i].length; ++j) {
				if ((valMatrix0 = arg0Matrix[i][j]) && cElementType.number === valMatrix0.type) {
					_sum += valMatrix0.getValue();
				}
			}
		}
		return this.value = new cNumber(_sum);
	};
	cSUMIFS.prototype.checkArguments = function () {
		return 1 === this.argumentsCurrent % 2 && cBaseFunction.prototype.checkArguments.apply(this, arguments);
	};
	cSUMIFS.prototype.getInfo = function () {
		return {
			name: this.name, args: "(sum-range, criteria_range1, criteria1, [criteria_range2, criteria2], ...)"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMPRODUCT() {
		this.name = "SUMPRODUCT";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMPRODUCT.prototype = Object.create(cBaseFunction.prototype);
	cSUMPRODUCT.prototype.constructor = cSUMPRODUCT;
	cSUMPRODUCT.prototype.argumentsMin = 1;
	cSUMPRODUCT.prototype.Calculate = function (arg) {
		var arg0 = new cNumber(0), resArr = [], col = 0, row = 0, res = 1, _res = [], i;

		for (i = 0; i < arg.length; i++) {

			if (arg[i] instanceof cArea3D) {
				return this.value = new cError(cErrorType.bad_reference);
			}

			if (arg[i] instanceof cArea || arg[i] instanceof cArray) {
				resArr[i] = arg[i].getMatrix();
			} else if (arg[i] instanceof cRef || arg[i] instanceof cRef3D) {
				resArr[i] = [[arg[i].getValue()]];
			} else {
				resArr[i] = [[arg[i]]];
			}

			row = Math.max(resArr[0].length, row);
			col = Math.max(resArr[0][0].length, col);

			if (row != resArr[i].length || col != resArr[i][0].length) {
				return this.value = new cError(cErrorType.not_numeric);
			}

			if (arg[i] instanceof cError) {
				return this.value = arg[i];
			}
		}

		for (var iRow = 0; iRow < row; iRow++) {
			for (var iCol = 0; iCol < col; iCol++) {
				res = 1;
				for (var iRes = 0; iRes < resArr.length; iRes++) {
					arg0 = resArr[iRes][iRow][iCol];
					if (arg0 instanceof cError) {
						return this.value = arg0;
					} else if (arg0 instanceof cString) {
						if (arg0.tocNumber() instanceof cError) {
							res *= 0;
						} else {
							res *= arg0.tocNumber().getValue();
						}
					} else {
						res *= arg0.tocNumber().getValue();
					}
				}
				_res.push(res);
			}
		}
		res = 0;
		for (i = 0; i < _res.length; i++) {
			res += _res[i]
		}

		return this.value = new cNumber(res);
	};
	cSUMPRODUCT.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMSQ() {
		this.name = "SUMSQ";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMSQ.prototype = Object.create(cBaseFunction.prototype);
	cSUMSQ.prototype.constructor = cSUMSQ;
	cSUMSQ.prototype.argumentsMin = 1;
	cSUMSQ.prototype.Calculate = function (arg) {
		var arg0 = new cNumber(0), _arg;

		function sumsqHelper(a, b) {
			var c = _func[b.type][b.type](b, b, "*");
			return _func[a.type][c.type](a, c, "+");
		}

		for (var i = 0; i < arg.length; i++) {
			if (arg[i] instanceof cArea || arg[i] instanceof cArea3D) {
				var _arrVal = arg[i].getValue();
				for (var j = 0; j < _arrVal.length; j++) {
					if (_arrVal[j] instanceof cNumber) {
						arg0 = sumsqHelper(arg0, _arrVal[j]);
					} else if (_arrVal[j] instanceof cError) {
						return this.value = _arrVal[j];
					}
				}
			} else if (arg[i] instanceof cRef || arg[i] instanceof cRef3D) {
				_arg = arg[i].getValue();
				if (_arg instanceof cNumber) {
					arg0 = sumsqHelper(arg0, _arg);
				}
			} else if (arg[i] instanceof cArray) {
				arg[i].foreach(function (arrElem) {
					if (arrElem instanceof cNumber) {
						arg0 = sumsqHelper(arg0, arrElem);
					}
				})
			} else {
				_arg = arg[i].tocNumber();
				arg0 = sumsqHelper(arg0, _arg);
			}
			if (arg0 instanceof cError) {
				return this.value = arg0;
			}

		}

		return this.value = arg0;
	};
	cSUMSQ.prototype.getInfo = function () {
		return {
			name: this.name, args: "( argument-list )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMX2MY2() {
		this.name = "SUMX2MY2";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMX2MY2.prototype = Object.create(cBaseFunction.prototype);
	cSUMX2MY2.prototype.constructor = cSUMX2MY2;
	cSUMX2MY2.prototype.argumentsMin = 2;
	cSUMX2MY2.prototype.argumentsMax = 2;
	cSUMX2MY2.prototype.Calculate = function (arg) {

		function sumX2MY2(a, b, _3d) {
			var sum = 0, i, j;

			function a2Mb2(a, b) {
				return a * a - b * b;
			}

			if (!_3d) {
				if (a.length == b.length && a[0].length == b[0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							if (a[i][j] instanceof cNumber && b[i][j] instanceof cNumber) {
								sum += a2Mb2(a[i][j].getValue(), b[i][j].getValue())
							} else {
								return new cError(cErrorType.wrong_value_type);
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			} else {
				if (a.length == b.length && a[0].length == b[0].length && a[0][0].length == b[0][0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							for (var k = 0; k < a[0][0].length; k++) {
								if (a[i][j][k] instanceof cNumber && b[i][j][k] instanceof cNumber) {
									sum += a2Mb2(a[i][j][k].getValue(), b[i][j][k].getValue())
								} else {
									return new cError(cErrorType.wrong_value_type);
								}
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			}
		}

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea3D && arg1 instanceof cArea3D) {
			return this.value = sumX2MY2(arg0.getMatrix(), arg1.getMatrix(), true);
		}

		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else if (arg0 instanceof cError) {
			return this.value = arg0;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArray || arg1 instanceof cArea3D) {
			arg1 = arg1.getMatrix();
		} else if (arg1 instanceof cError) {
			return this.value = arg1;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = sumX2MY2(arg0, arg1, false);
	};
	cSUMX2MY2.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array-1 , array-2 )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMX2PY2() {
		this.name = "SUMX2PY2";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMX2PY2.prototype = Object.create(cBaseFunction.prototype);
	cSUMX2PY2.prototype.constructor = cSUMX2PY2;
	cSUMX2PY2.prototype.argumentsMin = 2;
	cSUMX2PY2.prototype.argumentsMax = 2;
	cSUMX2PY2.prototype.Calculate = function (arg) {

		function sumX2MY2(a, b, _3d) {
			var sum = 0, i, j;

			function a2Mb2(a, b) {
				return a * a + b * b;
			}

			if (!_3d) {
				if (a.length == b.length && a[0].length == b[0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							if (a[i][j] instanceof cNumber && b[i][j] instanceof cNumber) {
								sum += a2Mb2(a[i][j].getValue(), b[i][j].getValue())
							} else {
								return new cError(cErrorType.wrong_value_type);
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			} else {
				if (a.length == b.length && a[0].length == b[0].length && a[0][0].length == b[0][0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							for (var k = 0; k < a[0][0].length; k++) {
								if (a[i][j][k] instanceof cNumber && b[i][j][k] instanceof cNumber) {
									sum += a2Mb2(a[i][j][k].getValue(), b[i][j][k].getValue())
								} else {
									return new cError(cErrorType.wrong_value_type);
								}
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			}
		}

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea3D && arg1 instanceof cArea3D) {
			return this.value = sumX2MY2(arg0.getMatrix(), arg1.getMatrix(), true);
		}

		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else if (arg0 instanceof cError) {
			return this.value = arg0;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArray || arg1 instanceof cArea3D) {
			arg1 = arg1.getMatrix();
		} else if (arg1 instanceof cError) {
			return this.value = arg1;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = sumX2MY2(arg0, arg1, false);
	};
	cSUMX2PY2.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array-1 , array-2 )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cSUMXMY2() {
		this.name = "SUMXMY2";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cSUMXMY2.prototype = Object.create(cBaseFunction.prototype);
	cSUMXMY2.prototype.constructor = cSUMXMY2;
	cSUMXMY2.prototype.argumentsMin = 2;
	cSUMXMY2.prototype.argumentsMax = 2;
	cSUMXMY2.prototype.Calculate = function (arg) {

		function sumX2MY2(a, b, _3d) {
			var sum = 0, i, j;

			function a2Mb2(a, b) {
				return ( a - b ) * ( a - b );
			}

			if (!_3d) {
				if (a.length == b.length && a[0].length == b[0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							if (a[i][j] instanceof cNumber && b[i][j] instanceof cNumber) {
								sum += a2Mb2(a[i][j].getValue(), b[i][j].getValue())
							} else {
								return new cError(cErrorType.wrong_value_type);
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			} else {
				if (a.length == b.length && a[0].length == b[0].length && a[0][0].length == b[0][0].length) {
					for (i = 0; i < a.length; i++) {
						for (j = 0; j < a[0].length; j++) {
							for (var k = 0; k < a[0][0].length; k++) {
								if (a[i][j][k] instanceof cNumber && b[i][j][k] instanceof cNumber) {
									sum += a2Mb2(a[i][j][k].getValue(), b[i][j][k].getValue())
								} else {
									return new cError(cErrorType.wrong_value_type);
								}
							}
						}
					}
					return new cNumber(sum);
				} else {
					return new cError(cErrorType.wrong_value_type);
				}
			}
		}

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea3D && arg1 instanceof cArea3D) {
			return this.value = sumX2MY2(arg0.getMatrix(), arg1.getMatrix(), true);
		}

		if (arg0 instanceof cArea || arg0 instanceof cArray) {
			arg0 = arg0.getMatrix();
		} else if (arg0 instanceof cError) {
			return this.value = arg0;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArray || arg1 instanceof cArea3D) {
			arg1 = arg1.getMatrix();
		} else if (arg1 instanceof cError) {
			return this.value = arg1;
		} else {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		return this.value = sumX2MY2(arg0, arg1, false);
	};
	cSUMXMY2.prototype.getInfo = function () {
		return {
			name: this.name, args: "( array-1 , array-2 )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cTAN() {
		this.name = "TAN";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cTAN.prototype = Object.create(cBaseFunction.prototype);
	cTAN.prototype.constructor = cTAN;
	cTAN.prototype.argumentsMin = 1;
	cTAN.prototype.argumentsMax = 1;
	cTAN.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.tan(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.tan(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cTAN.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cTANH() {
		this.name = "TANH";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cTANH.prototype = Object.create(cBaseFunction.prototype);
	cTANH.prototype.constructor = cTANH;
	cTANH.prototype.argumentsMin = 1;
	cTANH.prototype.argumentsMax = 1;
	cTANH.prototype.Calculate = function (arg) {
		var arg0 = arg[0];
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				if (elem instanceof cNumber) {
					var a = Math.tanh(elem.getValue());
					this.array[r][c] = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			})
		} else {
			var a = Math.tanh(arg0.getValue());
			return this.value = isNaN(a) ? new cError(cErrorType.not_numeric) : new cNumber(a);
		}
		return this.value = arg0;
	};
	cTANH.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x )"
		};
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cTRUNC() {
		this.name = "TRUNC";
		this.value = null;
		this.argumentsCurrent = 0;
	}

	cTRUNC.prototype = Object.create(cBaseFunction.prototype);
	cTRUNC.prototype.constructor = cTRUNC;
	cTRUNC.prototype.argumentsMin = 1;
	cTRUNC.prototype.argumentsMax = 2;
	cTRUNC.prototype.Calculate = function (arg) {

		function truncHelper(a, b) {
			var c = a < 0 ? 1 : 0;
			if (b == 0) {
				return new cNumber(a.toString().substr(0, 1 + c));
			} else if (b > 0) {
				return new cNumber(a.toString().substr(0, b + 2 + c));
			} else {
				return new cNumber(0);
			}
		}

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cNumber(0);
		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1].bbox);
		}
		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1].bbox);
		}

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		if (arg0 instanceof cRef || arg0 instanceof cRef3D) {
			arg0 = arg0.getValue();
			if (arg0 instanceof cError) {
				return this.value = arg0;
			} else if (arg0 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg0 = arg0.tocNumber();
			}
		} else {
			arg0 = arg0.tocNumber();
		}

		if (arg1 instanceof cRef || arg1 instanceof cRef3D) {
			arg1 = arg1.getValue();
			if (arg1 instanceof cError) {
				return this.value = arg1;
			} else if (arg1 instanceof cString) {
				return this.value = new cError(cErrorType.wrong_value_type);
			} else {
				arg1 = arg1.tocNumber();
			}
		} else {
			arg1 = arg1.tocNumber();
		}

		if (arg0 instanceof cArray && arg1 instanceof cArray) {
			if (arg0.getCountElement() != arg1.getCountElement() || arg0.getRowCount() != arg1.getRowCount()) {
				return this.value = new cError(cErrorType.not_available);
			} else {
				arg0.foreach(function (elem, r, c) {
					var a = elem;
					var b = arg1.getElementRowCol(r, c);
					if (a instanceof cNumber && b instanceof cNumber) {
						this.array[r][c] = truncHelper(a.getValue(), b.getValue())
					} else {
						this.array[r][c] = new cError(cErrorType.wrong_value_type);
					}
				});
				return this.value = arg0;
			}
		} else if (arg0 instanceof cArray) {
			arg0.foreach(function (elem, r, c) {
				var a = elem;
				var b = arg1;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = truncHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg0;
		} else if (arg1 instanceof cArray) {
			arg1.foreach(function (elem, r, c) {
				var a = arg0;
				var b = elem;
				if (a instanceof cNumber && b instanceof cNumber) {
					this.array[r][c] = truncHelper(a.getValue(), b.getValue())
				} else {
					this.array[r][c] = new cError(cErrorType.wrong_value_type);
				}
			});
			return this.value = arg1;
		}

		return this.value = truncHelper(arg0.getValue(), arg1.getValue());
	};
	cTRUNC.prototype.getInfo = function () {
		return {
			name: this.name, args: "( x [ , number-digits ] )"
		};
	};
})(window);
