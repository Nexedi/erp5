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
	var cErrorType = AscCommonExcel.cErrorType;
	var cNumber = AscCommonExcel.cNumber;
	var cString = AscCommonExcel.cString;
	var cError = AscCommonExcel.cError;
	var cArea = AscCommonExcel.cArea;
	var cArea3D = AscCommonExcel.cArea3D;
	var cArray = AscCommonExcel.cArray;
	var cUndefined = AscCommonExcel.cUndefined;
	var cBaseFunction = AscCommonExcel.cBaseFunction;
	var cFormulaFunctionGroup = AscCommonExcel.cFormulaFunctionGroup;

	var rtl_math_erf = AscCommonExcel.rtl_math_erf;

	var rg_validBINNumber = /^[01]{1,10}$/, rg_validDEC2BINNumber = /^-?[0-9]{1,3}$/, rg_validDEC2OCTNumber = /^-?[0-9]{1,9}$/, rg_validDEC2HEXNumber = /^-?[0-9]{1,12}$/, rg_validHEXNumber = /^[0-9A-F]{1,10}$/i, rg_validOCTNumber = /^[0-7]{1,10}$/, rg_complex_number = new XRegExp("^(?<real>[-+]?(?:\\d*(?:\\.\\d+)?(?:[Ee][+-]?\\d+)?))?(?<img>([-+]?(\\d*(?:\\.\\d+)?(?:[Ee][+-]?\\d+)?)?[ij])?)", "g");

	var NumberBase = {
		BIN: 2, OCT: 8, DEC: 10, HEX: 16
	};

	var f_PI_DIV_2 = Math.PI / 2;
	var f_PI_DIV_4 = Math.PI / 4;
	var f_2_DIV_PI = 2 / Math.PI;

	function BesselJ(x, N) {
		if (N < 0) {
			return new cError(cErrorType.not_numeric);
		}
		if (x === 0.0) {
			return new cNumber((N == 0) ? 1 : 0);
		}

		/*  The algorithm works only for x>0, therefore remember sign. BesselJ
		 with integer order N is an even function for even N (means J(-x)=J(x))
		 and an odd function for odd N (means J(-x)=-J(x)).*/
		var fSign = (N % 2 == 1 && x < 0) ? -1 : 1;
		var fX = Math.abs(x);

		var fMaxIteration = 9000000; //experimental, for to return in < 3 seconds
		var fEstimateIteration = fX * 1.5 + N;
		var bAsymptoticPossible = Math.pow(fX, 0.4) > N;
		if (fEstimateIteration > fMaxIteration) {
			if (bAsymptoticPossible) {
				return new cNumber(fSign * Math.sqrt(f_2_DIV_PI / fX) * Math.cos(fX - N * f_PI_DIV_2 - f_PI_DIV_4));
			} else {
				return new cError(cErrorType.not_numeric);
			}
		}

		var epsilon = 1.0e-15; // relative error
		var bHasfound = false, k = 0, u;

		// first used with k=1
		var m_bar, g_bar, g_bar_delta_u, g = 0, delta_u = 0, f_bar = -1;  // f_bar_k = 1/f_k, but only used for k=0

		if (N == 0) {
			u = 1;
			g_bar_delta_u = 0;
			g_bar = -2 / fX;
			delta_u = g_bar_delta_u / g_bar;
			u = u + delta_u;
			g = -1 / g_bar;
			f_bar = f_bar * g;
			k = 2;
		} else {
			u = 0;
			for (k = 1; k <= N - 1; k = k + 1) {
				m_bar = 2 * Math.fmod(k - 1, 2) * f_bar;
				g_bar_delta_u = -g * delta_u - m_bar * u; // alpha_k = 0.0
				g_bar = m_bar - 2 * k / fX + g;
				delta_u = g_bar_delta_u / g_bar;
				u = u + delta_u;
				g = -1 / g_bar;
				f_bar = f_bar * g;
			}
			// Step alpha_N = 1.0
			m_bar = 2 * Math.fmod(k - 1, 2) * f_bar;
			g_bar_delta_u = f_bar - g * delta_u - m_bar * u; // alpha_k = 1.0
			g_bar = m_bar - 2 * k / fX + g;
			delta_u = g_bar_delta_u / g_bar;
			u = u + delta_u;
			g = -1 / g_bar;
			f_bar = f_bar * g;
			k = k + 1;
		}
		// Loop until desired accuracy, always alpha_k = 0.0
		do {
			m_bar = 2 * Math.fmod(k - 1, 2) * f_bar;
			g_bar_delta_u = -g * delta_u - m_bar * u;
			g_bar = m_bar - 2 * k / fX + g;
			delta_u = g_bar_delta_u / g_bar;
			u = u + delta_u;
			g = -1 / g_bar;
			f_bar = f_bar * g;
			bHasfound = (Math.abs(delta_u) <= Math.abs(u) * epsilon);
			k = k + 1;
		} while (!bHasfound && k <= fMaxIteration);
		if (bHasfound) {
			return new cNumber(u * fSign);
		} else {
			return new cError(cErrorType.not_numeric);
		}// unlikely to happen
	}

	function BesselI(x, n) {
		var nMaxIteration = 20000, fXHalf = x / 2, fResult = 0, fEpsilon = 1.0E-30;
		if (n < 0) {
			return new cError(cErrorType.not_numeric);
		}

		/*  Start the iteration without TERM(n,0), which is set here.

		 TERM(n,0) = (x/2)^n / n!
		 */
		var nK = 0, fTerm = 1;
		// avoid overflow in Fak(n)
		/*for ( nK = 1; nK <= n; ++nK ) {
		 fTerm = fTerm / nK * fXHalf;
		 }*/

		fTerm = Math.pow(fXHalf, n) / Math.fact(n);

		fResult = fTerm;    // Start result with TERM(n,0).
		if (fTerm !== 0) {
			nK = 1;
			do {
				fTerm = Math.pow(fXHalf, n + 2 * nK) / ( Math.fact(nK) * Math.fact(n + nK) );

				/*  Calculation of TERM(n,k) from TERM(n,k-1):

				 (x/2)^(n+2k)
				 TERM(n,k)  =  --------------
				 k! (n+k)!

				 (x/2)^2 (x/2)^(n+2(k-1))
				 =  --------------------------
				 k (k-1)! (n+k) (n+k-1)!

				 (x/2)^2     (x/2)^(n+2(k-1))
				 =  --------- * ------------------
				 k(n+k)      (k-1)! (n+k-1)!

				 x^2/4
				 =  -------- TERM(n,k-1)
				 k(n+k)
				 */
//            fTerm = fTerm * fXHalf / nK * fXHalf / (nK + n);
				fResult = fResult + fTerm;
				nK++;
			} while ((Math.abs(fTerm) > Math.abs(fResult) * fEpsilon) && (nK < nMaxIteration));

		}
		return new cNumber(fResult);
	}

	function Besselk0(fNum) {
		var fRet, y;

		if (fNum <= 2) {

			y = fNum * fNum / 4.0;
			fRet=(-Math.log(fNum / 2.0) * BesselI(fNum, 0)) + (-0.57721566 + y * (0.42278420
				+y * (0.23069756 + y * (0.3488590e-1 + y * (0.262698e-2
				+y * (0.10750e-3 + y * 0.74e-5))))));

		} else {
			y = 2 / fNum;
			fRet = Math.exp(-fNum) / Math.sqrt(fNum) * ( 1.25331414 + y * ( -0.7832358e-1 + y * ( 0.2189568e-1 +
				y * ( -0.1062446e-1 + y * ( 0.587872e-2 + y * ( -0.251540e-2 + y * 0.53208e-3 ) ) ) ) ) );
		}

		return new cNumber(fRet);
	}

	function Besselk1(fNum) {
		var fRet, y;

		if (fNum <= 2) {
			y = fNum * fNum / 4.0;
			fRet=(Math.log(fNum / 2.0) * BesselI(fNum, 1))+(1.0 / fNum)*(1.0 + y * (0.15443144
				+ y * (-0.67278579 + y * (-0.18156897 + y * (-0.1919402e-1
				+ y * (-0.110404e-2 + y * (-0.4686e-4)))))));
		} else {
			y = 2 / fNum;
			fRet = Math.exp(-fNum) / Math.sqrt(fNum) * ( 1.25331414 + y * ( 0.23498619 + y * ( -0.3655620e-1 +
				y * ( 0.1504268e-1 + y * ( -0.780353e-2 + y * ( 0.325614e-2 + y * ( -0.68245e-3 ) ) ) ) ) ) );
		}

		return new cNumber(fRet);
	}

	function bessi0(x){
		var ax = Math.abs(x), fRet, y;

		if (ax < 3.75) {
			y = x / 3.75;
			y *= y;
			fRet = 1.0 + y*(3.5156229 + y*(3.0899424 + y*(1.2067492 + y*(0.2659732 + y*(0.360768e-1 + y*0.45813e-2)))));
		} else {
			y = 3.75 / ax;
			fRet = (Math.exp(ax) / Math.sqrt(ax))*(0.39894228 + y*(0.1328592e-1
				+ y*(0.225319e-2 + y*(-0.157565e-2 + y*(0.916281e-2
				+ y*(-0.2057706e-1 + y*(0.2635537e-1 + y*(-0.1647633e-1
				+ y*0.392377e-2))))))));
		}
		return fRet;
	}

	function bessi(x, n){
		var max = 1.0e10;
		var min = 1.0e-10;
		var ACC  = 40.0;

		var bi, bim, bip, tox, res;
		if (x === 0.0){
			return new cNumber(0.0);
		} else {
			tox = 2.0 / Math.abs(x);
			bip = res = 0.0;
			bi = 1.0;
			for (var j = 2 * (n + parseInt(Math.sqrt(ACC * n))); j>0; j--) {
				bim = bip + j * tox * bi;
				bip = bi;
				bi = bim;
				if (Math.abs(bi) > max) {
					res *= min;
					bi *= min;
					bip *= min;
				}
				if (j === n){
					res = bip;
				}
			}
			res *= bessi0(x) / bi;
			return x < 0.0 && (n & 1) ? new cNumber(-res) : new cNumber(res);
		}
	}

	function BesselK(fNum, nOrder) {
		switch (nOrder) {
			case 0:
				return Besselk0(fNum);
			case 1:
				return Besselk1(fNum);
			default: {
				var fBkp;

				var fTox = 2 / fNum, fBkm = Besselk0(fNum), fBk = Besselk1(fNum);

				if (fBkm instanceof cError) {
					return fBkm;
				}
				if (fBk instanceof cError) {
					return fBk;
				}

				fBkm = fBkm.getValue();
				fBk = fBk.getValue();

				for (var n = 1; n < nOrder; n++) {
					fBkp = fBkm + n * fTox * fBk;
					fBkm = fBk;
					fBk = fBkp;
				}

				return new cNumber(fBk);
			}
		}
	}

	// See #i31656# for a commented version of this implementation, attachment #desc6
	// http://www.openoffice.org/nonav/issues/showattachment.cgi/63609/Comments%20to%20the%20implementation%20of%20the%20Bessel%20functions.odt
	function Bessely0(fX) {
		if (fX <= 0) {
			return new cError(cErrorType.not_numeric);
		}
		var fMaxIteration = 9000000; // should not be reached
		if (fX > 5.0e+6) { // iteration is not considerable better then approximation
			return new cNumber(Math.sqrt(1 / Math.PI / fX) * (Math.sin(fX) - Math.cos(fX)));
		}
		var epsilon = 1.0e-15, EulerGamma = 0.57721566490153286060;
		var alpha = Math.log10(fX / 2) + EulerGamma;
		var u = alpha;

		var k = 1, m_bar = 0, g_bar_delta_u = 0, g_bar = -2 / fX;
		var delta_u = g_bar_delta_u / g_bar, g = -1 / g_bar, f_bar = -1 * g, sign_alpha = 1, km1mod2, bHasFound = false;
		k = k + 1;
		do {
			km1mod2 = Math.fmod(k - 1, 2);
			m_bar = (2 * km1mod2) * f_bar;
			if (km1mod2 == 0) {
				alpha = 0;
			} else {
				alpha = sign_alpha * (4 / k);
				sign_alpha = -sign_alpha;
			}
			g_bar_delta_u = f_bar * alpha - g * delta_u - m_bar * u;
			g_bar = m_bar - (2 * k) / fX + g;
			delta_u = g_bar_delta_u / g_bar;
			u = u + delta_u;
			g = -1 / g_bar;
			f_bar = f_bar * g;
			bHasFound = (Math.abs(delta_u) <= Math.abs(u) * epsilon);
			k = k + 1;
		} while (!bHasFound && k < fMaxIteration);
		if (bHasFound) {
			return new cNumber(u * f_2_DIV_PI);
		} else {
			return new cError(cErrorType.not_numeric);
		}
	}

	// See #i31656# for a commented version of this implementation, attachment #desc6
	// http://www.openoffice.org/nonav/issues/showattachment.cgi/63609/Comments%20to%20the%20implementation%20of%20the%20Bessel%20functions.odt
	function Bessely1(fX) {
		if (fX <= 0) {
			return new cError(cErrorType.not_numeric);
		}
		var fMaxIteration = 9000000; // should not be reached
		if (fX > 5e+6) { // iteration is not considerable better then approximation
			return new cNumber(-Math.sqrt(1 / Math.PI / fX) * (Math.sin(fX) + Math.cos(fX)));
		}
		var epsilon = 1.0e-15, EulerGamma = 0.57721566490153286060, alpha = 1 /
			fX, f_bar = -1, u = alpha, k = 1, m_bar = 0;
		alpha = 1 - EulerGamma - Math.log10(fX / 2);
		var g_bar_delta_u = -alpha, g_bar = -2 / fX, delta_u = g_bar_delta_u / g_bar;
		u = u + delta_u;
		var g = -1 / g_bar;
		f_bar = f_bar * g;
		var sign_alpha = -1, km1mod2, //will be (k-1) mod 2
			q, // will be (k-1) div 2
			bHasFound = false;
		k = k + 1;
		do {
			km1mod2 = Math.fmod(k - 1, 2);
			m_bar = (2 * km1mod2) * f_bar;
			q = (k - 1) / 2;
			if (km1mod2 == 0) { // k is odd
				alpha = sign_alpha * (1 / q + 1 / (q + 1));
				sign_alpha = -sign_alpha;
			} else {
				alpha = 0;
			}
			g_bar_delta_u = f_bar * alpha - g * delta_u - m_bar * u;
			g_bar = m_bar - (2 * k) / fX + g;
			delta_u = g_bar_delta_u / g_bar;
			u = u + delta_u;
			g = -1 / g_bar;
			f_bar = f_bar * g;
			bHasFound = (Math.abs(delta_u) <= Math.abs(u) * epsilon);
			k = k + 1;
		} while (!bHasFound && k < fMaxIteration);
		if (bHasFound) {
			return new cNumber(-u * 2 / Math.PI);
		} else {
			return new cError(cErrorType.not_numeric);
		}
	}

	function _Bessely0(fNum) {

		if (fNum < 8.0) {
			var y = (fNum * fNum);
			var f1 = -2957821389.0 + y * (7062834065.0 + y * (-512359803.6 + y * (10879881.29 + y * (-86327.92757 + y * 228.4622733))));
			var f2 = 40076544269.0 + y * (745249964.8 + y * (7189466.438 + y * (47447.26470 + y * (226.1030244 + y))));
			var fRet = f1 / f2 + 0.636619772 * BesselJ(fNum, 0) * Math.log(fNum);
		}
		else {
			var z = 8.0 / fNum;
			var y = (z * z);
			var xx = fNum - 0.785398164;
			var f1 = 1 + y * (-0.1098628627e-2 + y * (0.2734510407e-4 + y * (-0.2073370639e-5 + y * 0.2093887211e-6)));
			var f2 = -0.1562499995e-1 + y * (0.1430488765e-3 + y * (-0.6911147651e-5 + y * (0.7621095161e-6 + y * (-0.934945152e-7))));
			var fRet = Math.sqrt(0.636619772 / fNum) * (Math.sin(xx) * f1 + z * Math.cos(xx) * f2);
		}

		return new cNumber(fRet);
	}


	function _Bessely1(fNum) {
		var z, xx , y, fRet, ans1, ans2;
		if (fNum < 8.0) {
			y = fNum * fNum;
			ans1 = fNum *(-0.4900604943e13 + y * (0.1275274390e13 + y * (-0.5153438139e11 + y * (0.7349264551e9 + y * (-0.4237922726e7 + y * 0.8511937935e4)))));
			ans2 = 0.2499580570e14 + y * (0.4244419664e12 + y * (0.3733650367e10 + y * (0.2245904002e8 + y * (0.1020426050e6 + y * (0.3549632885e3 + y)))));
			fRet=(ans1 / ans2) + 0.636619772 * (BesselJ(fNum) * Math.log(fNum) - 1.0 / fNum);
		} else {
			z = 8.0 / fNum;
			y = z * z;
			xx = fNum - 2.356194491;
			ans1 = 1.0 + y * (0.183105e-2 + y * (-0.3516396496e-4 + y * (0.2457520174e-5 + y * (-0.240337019e-6))));
			ans2 = 0.04687499995 + y * (-0.2002690873e-3 + y * (0.8449199096e-5 + y * (-0.88228987e-6 + y * 0.105787412e-6)));
			fRet = Math.sqrt(0.636619772 / fNum) * (Math.sin(xx) * ans1 + z * Math.cos(xx) * ans2);
		}

		return new cNumber(fRet);
	}

	function BesselY(fNum, nOrder) {
		switch (nOrder) {
			case 0:
				return _Bessely0(fNum);
			case 1:
				return _Bessely1(fNum);
			default: {
				var fByp, fTox = 2 / fNum, fBym = _Bessely0(fNum), fBy = _Bessely1(fNum);

				if (fBym instanceof cError) {
					return fBym;
				}
				if (fBy instanceof cError) {
					return fBy;
				}

				fBym = fBym.getValue();
				fBy = fBy.getValue();

				for (var n = 1; n < nOrder; n++) {
					fByp = n * fTox * fBy - fBym;
					fBym = fBy;
					fBy = fByp;
				}

				return new cNumber(fBy);
			}
		}
	}

	function validBINNumber(n) {
		return rg_validBINNumber.test(n);
	}

	function validDEC2BINNumber(n) {
		return rg_validDEC2BINNumber.test(n);
	}

	function validDEC2OCTNumber(n) {
		return rg_validDEC2OCTNumber.test(n);
	}

	function validDEC2HEXNumber(n) {
		return rg_validDEC2HEXNumber.test(n);
	}

	function validHEXNumber(n) {
		return rg_validHEXNumber.test(n);
	}

	function validOCTNumber(n) {
		return rg_validOCTNumber.test(n);
	}

	function convertFromTo(src, from, to, charLim) {
		var res = parseInt(src, from).toString(to);
		if (charLim == undefined) {
			return new cString(res.toUpperCase());
		} else {
			charLim = parseInt(charLim);
			if (charLim >= res.length) {
				return new cString(( '0'.repeat(charLim - res.length) + res).toUpperCase());
			} else {
				return new cError(cErrorType.not_numeric);
			}
		}
	}

	function Complex(r, i, suffix) {
		if (arguments.length == 1) {
			return this.ParseString(arguments[0]);
		} else {
			this.real = r;
			this.img = i;
			this.suffix = suffix ? suffix : "i";
			return this;
		}
	}

	Complex.prototype = {

		constructor: Complex, toString: function () {
			var res = [];
			var hasImag = this.img != 0, hasReal = !hasImag || (this.real != 0);

			if (hasReal) {

				res.push(this.real);
			}
			if (hasImag) {
				if (this.img == 1) {
					if (hasReal) {
						res.push('+');
					}
				} else if (this.img == -1) {
					res.push("-");
				} else {
					this.img > 0 && hasReal ? res.push("+" + this.img) : res.push(this.img);
				}
				res.push(this.suffix ? this.suffix : "i");
			}
			return res.join("");
		}, Real: function () {
			return this.real;
		}, Imag: function () {
			return this.img;
		}, Abs: function () {
			return Math.sqrt(this.real * this.real + this.img * this.img);
		}, Arg: function () {
			if (this.real == 0.0 && this.img == 0.0) {
				return new cError(cErrorType.division_by_zero);
			}

			var phi = Math.acos(this.real / this.Abs());

			if (this.img < 0.0) {
				phi = -phi;
			}

			return phi;
		}, Conj: function () {
			var c = new Complex(this.real, -this.img, this.suffix);
			return c.toString();
		}, Cos: function () {
			if (this.img) {
				var a = Math.cos(this.real) * Math.cosh(this.img);
				this.img = -( Math.sin(this.real) * Math.sinh(this.img) );
				this.real = a;
			} else {
				this.real = Math.cos(this.real);
			}
		}, Tan: function () {
			if (this.img) {
				var a = Math.sin(2 * this.real) / (Math.cos(2 * this.real) + Math.cosh(2 * this.img));
				this.img = Math.sinh(2 * this.img) / (Math.cos(2 * this.real) + Math.cosh(2 * this.img));
				this.real = a;
			} else {
				this.real = Math.tan(this.real);
			}
		}, Cot: function () {
			if (this.img) {
				var a = Math.sin(2 * this.real) / (Math.cosh(2 * this.img) - Math.cos(2 * this.real));
				this.img = -(Math.sinh(2 * this.img) / (Math.cosh(2 * this.img) - Math.cos(2 * this.real)));
				this.real = a;
			} else {
				this.real = 1 / Math.tan(this.real);
			}
		}, Cosh: function () {
			if (this.img) {
				var a = Math.cosh(this.real) * Math.cos(this.img);
				this.img = Math.sinh(this.real) * Math.sin(this.img);
				this.real = a;
			} else {
				this.real = Math.cosh(this.real);
			}
		}, Csc: function () {
			if (this.img) {
				var a = (2 * Math.sin(this.real) * Math.cosh(this.img)) / (Math.cosh(2 * this.img) - Math.cos(2 *this.real));
				this.img = (-2 * Math.cos(this.real) * Math.sinh(this.img)) / (Math.cosh(2 * this.img) - Math.cos(2 *this.real));
				this.real = a;
			} else {
				this.real = 1 / Math.sin(this.real);
			}
		}, Csch: function () {
			if (this.img) {
				var a = (2 * Math.sinh(this.real) * Math.cos(this.img)) / (Math.cosh(2 * this.real) - Math.cos(2 *this.img));
				this.img = (-2 * Math.cosh(this.real) * Math.sin(this.img)) / (Math.cosh(2 * this.real) - Math.cos(2 *this.img));
				this.real = a;
			} else {
				this.real = 1 / Math.sinh(this.real);
			}
		}, Sec: function () {
			if (this.img) {
				var a = (2 * Math.cos(this.real) * Math.cosh(this.img)) / (Math.cosh(2 * this.img) + Math.cos(2 *this.real));
				this.img = (2 * Math.sin(this.real) * Math.sinh(this.img)) / (Math.cosh(2 * this.img) + Math.cos(2 *this.real));
				this.real = a;
			} else {
				this.real = 1 / Math.cos(this.real);
			}
		}, Sech: function () {
			if (this.img) {
				var a = (2 * Math.cosh(this.real) * Math.cos(this.img)) / (Math.cosh(2 * this.real) + Math.cos(2 *this.img));
				this.img = (-2 * Math.sinh(this.real) * Math.sin(this.img)) / (Math.cosh(2 * this.real) + Math.cos(2 *this.img));
				this.real = a;
			} else {
				this.real = 1 / Math.cosh(this.real);
			}
		}, Sin: function () {
			if (this.img) {
				var a = Math.sin(this.real) * Math.cosh(this.img);
				this.img = Math.cos(this.real) * Math.sinh(this.img);
				this.real = a;
			} else {
				this.real = Math.sin(this.real);
			}
		}, Sinh: function () {
			if (this.img) {
				var a = Math.sinh(this.real) * Math.cos(this.img);
				this.img = Math.cosh(this.real) * Math.sin(this.img);
				this.real = a;
			} else {
				this.real = Math.sinh(this.real);
			}
		}, Div: function (comp) {

			var a = this.real, b = this.img, c = comp.real, d = comp.img, f = 1 / (c * c + d * d);

			if (Math.abs(f) == Infinity) {
				return new cError(cErrorType.not_numeric);
			}

			return new Complex((a * c + b * d) * f, (b * c - a * d) * f, this.suffix);

		}, Exp: function () {

			var e = Math.exp(this.real), c = Math.cos(this.img), s = Math.sin(this.img);

			this.real = e * c;
			this.img = e * s;

		}, Ln: function () {

			var abs = this.Abs(), arg = this.Arg();

			if (abs == 0 || arg instanceof cError) {
				return new cError(cErrorType.not_numeric);
			}

			this.real = Math.ln(abs);
			this.img = arg;

		}, Log10: function () {

			var c = new Complex(Math.ln(10), 0);
			var r = this.Ln();

			if (r instanceof cError) {
				return r;
			}

			c = this.Div(c);

			if (c instanceof cError) {
				return c;
			}

			this.real = c.real;
			this.img = c.img;

		}, Log2: function () {

			var c = new Complex(Math.ln(2), 0);
			var r = this.Ln();

			if (r instanceof cError) {
				return r;
			}

			c = this.Div(c);

			if (c instanceof cError) {
				return c;
			}

			this.real = c.real;
			this.img = c.img;

		}, Power: function (power) {

			if (this.real == 0 && this.img == 0) {
				if (power > 0) {
					this.real = this.img = 0;
					return true;
				} else {
					return false;
				}
			} else {

				var p = this.Abs(), phi;

				phi = Math.acos(this.real / p);
				if (this.img < 0) {
					phi = -phi;
				}

				p = Math.pow(p, power);
				phi *= power;

				this.real = Math.cos(phi) * p;
				this.img = Math.sin(phi) * p;

				return true;
			}

		}, Product: function (comp) {

			var a = this.real, b = this.img, c = comp.real, d = comp.img;

			this.real = a * c - b * d;
			this.img = a * d + b * c;

		}, SQRT: function () {

			if (this.real || this.img) {
				var abs = this.Abs(), arg = this.Arg();

				this.real = Math.sqrt(abs) * Math.cos(arg / 2);
				this.img = Math.sqrt(abs) * Math.sin(arg / 2);

			}

		}, Sub: function (comp) {

			this.real -= comp.real;
			this.img -= comp.img;

		}, Sum: function (comp) {

			this.real += comp.real;
			this.img += comp.img;

		}, isImagUnit: function (c) {
			return c == 'i' || c == 'j';
		}, parseComplexStr: function (s) {
			var match = XRegExp.exec(s, rg_complex_number), r, i, suf;
			if (match) {
				r = match["real"];
				i = match["img"];

				if (!(r || i)) {
					return new cError(cErrorType.not_numeric);
				}

				if (i) {
					suf = i[i.length - 1];
					i = i.substr(0, i.length - 1);
					if (i.length == 1 && (i[0] == "-" || i[0] == "+" )) {
						i = parseFloat(i + "1");
					} else {
						i = parseFloat(i);
					}
				} else {
					i = 0;
				}

				if (r) {
					r = parseFloat(r);
				} else {
					r = 0;
				}

				return new Complex(r, i, suf ? suf : "i");

			} else {
				return new cError(cErrorType.not_numeric);
			}
		}, ParseString: function (rStr) {

			var pStr = {pStr: rStr}, f = {f: undefined};

			if (rStr.length == 0) {
				this.real = 0;
				this.img = 0;
				this.suffix = "i";
				return this;
			}

			if (this.isImagUnit(pStr.pStr[0]) && rStr.length == 1) {
				this.real = 0;
				this.img = 1;
				this.suffix = pStr;
				return this;
			}

			if (!this.ParseDouble(pStr, f)) {
				return new cError(cErrorType.not_numeric);
			}

			switch (pStr.pStr[0] + "") {
				case '-':   // imag part follows
				case '+': {
					var r = f.f;

					if (this.isImagUnit(pStr.pStr[1])) {
						this.c = pStr.pStr[1];
						if (pStr.pStr[2] === undefined) {
							this.real = f.f;
							this.img = ( pStr.pStr[0] == '+' ) ? 1.0 : -1.0;
							return this;
						}
					} else if (this.ParseDouble(pStr, f) && this.isImagUnit(pStr.pStr[0])) {
						this.c = pStr.pStr;
						if (pStr.pStr[2] === undefined) {
							this.real = r;
							this.img = f.f;
							return this;
						}
					}
					break;
				}
				case 'j':
				case 'i':
					this.c = pStr;
					if (pStr.pStr[1] === undefined) {
						this.img = f.f;
						this.real = 0.0;
						return this;
					}
					break;
				case "undefined":     // only real-part
					this.real = f.f;
					this.img = 0.0;
					return this;
			}
			return new cError(cErrorType.not_numeric);
		}, ParseDouble: function (rp, rRet) {

			function isnum(c) {
				return c >= '0' && c <= '9';
			}


			function iscomma(c) {
				return c == '.' || c == ',';
			}


			function isexpstart(c) {
				return c == 'e' || c == 'E';
			}


			function isimagunit(c) {
				return c == 'i' || c == 'j';
			}

			var fInt = 0.0, fFrac = 0.0, fMult = 0.1, // multiplier to multiply digits with, when adding fractional ones
				nExp = 0, nMaxExp = 307, nDigCnt = 18, // max. number of digits to read in, rest doesn't matter
				State = {
					end: 0,
					sign: 1,
					intstart: 2,
					int: 3,
					ignoreintdigs: 4,
					frac: 5,
					ignorefracdigs: 6,
					expsign: 7,
					exp: 8
				}, eS = State.sign, bNegNum = false, bNegExp = false, p = rp.pStr, c, i = 0;

			while (eS) {
				c = p[i];
				switch (eS) {
					case State.sign:
						if (isnum(c)) {
							fInt = parseFloat(c);
							nDigCnt--;
							eS = State.int;
						} else if (c == '-') {
							bNegNum = true;
							eS = State.intstart;
						} else if (c == '+') {
							eS = State.intstart;
						} else if (iscomma(c)) {
							eS = State.frac;
						} else {
							return false;
						}
						break;
					case State.intstart:
						if (isnum(c)) {
							fInt = parseFloat(c);
							nDigCnt--;
							eS = State.int;
						} else if (iscomma(c)) {
							eS = State.frac;
						} else if (isimagunit(c)) {
							rRet.f = 0.0;
							return true;
						} else {
							return false;
						}
						break;
					case State.int:
						if (isnum(c)) {
							fInt *= 10.0;
							fInt += parseFloat(c);
							nDigCnt--;
							if (!nDigCnt) {
								eS = State.ignoreintdigs;
							}
						} else if (iscomma(c)) {
							eS = State.frac;
						} else if (isexpstart(c)) {
							eS = State.expsign;
						} else {
							eS = State.end;
						}
						break;
					case State.ignoreintdigs:
						if (isnum(c)) {
							nExp++;
						}     // just multiply num with 10... ;-)
						else if (iscomma(c)) {
							eS = State.frac;
						} else if (isexpstart(c)) {
							eS = State.expsign;
						} else {
							eS = State.end;
						}
						break;
					case State.frac:
						if (isnum(c)) {
							fFrac += parseFloat(c) * fMult;
							nDigCnt--;
							if (nDigCnt) {
								fMult *= 0.1;
							} else {
								eS = State.ignorefracdigs;
							}
						} else if (isexpstart(c)) {
							eS = State.expsign;
						} else {
							eS = State.end;
						}
						break;
					case State.ignorefracdigs:
						if (isexpstart(c)) {
							eS = State.expsign;
						} else if (!isnum(c)) {
							eS = State.end;
						}
						break;
					case State.expsign:
						if (isnum(c)) {
							nExp = parseFloat(c);
							eS = State.exp;
						} else if (c == '-') {
							bNegExp = true;
							eS = State.exp;
						} else if (c != '+') {
							eS = State.end;
						}
						break;
					case State.exp:
						if (isnum(c)) {
							nExp *= 10;
							nExp += parseFloat(c);
							if (nExp > nMaxExp) {
								return false;
							}
						} else {
							eS = State.end;
						}
						break;
					case State.end:     // to avoid compiler warning
						break;      // loop exits anyway
				}

				i++;
			}

			i--;        // set pointer back to last
			rp.pStr = p.substr(i);

			fInt += fFrac;
			var nLog10 = Math.log10(fInt);

			if (bNegExp) {
				nExp = -nExp;
			}

			if (nLog10 + nExp > nMaxExp) {
				return false;
			}

			fInt = fInt * Math.pow(10.0, nExp);

			if (bNegNum) {
				fInt = -fInt;
			}

			rRet.f = fInt;

			return true;
		}

	};

	cFormulaFunctionGroup['Engineering'] = cFormulaFunctionGroup['Engineering'] || [];
	cFormulaFunctionGroup['Engineering'].push(cBESSELI, cBESSELJ, cBESSELK, cBESSELY, cBIN2DEC, cBIN2HEX, cBIN2OCT,
		cBITAND, cBITLSHIFT, cBITOR, cBITRSHIFT, cBITXOR, cCOMPLEX, cCONVERT, cDEC2BIN, cDEC2HEX, cDEC2OCT, cDELTA,
		cERF, cERF_PRECISE, cERFC, cERFC_PRECISE, cGESTEP, cHEX2BIN, cHEX2DEC, cHEX2OCT, cIMABS, cIMAGINARY,
		cIMARGUMENT, cIMCONJUGATE, cIMCOS, cIMCOSH, cIMCOT, cIMCSC, cIMCSCH, cIMDIV, cIMEXP, cIMLN, cIMLOG10, cIMLOG2,
		cIMPOWER, cIMPRODUCT, cIMREAL, cIMSEC, cIMSECH, cIMSIN, cIMSINH, cIMSQRT, cIMSUB, cIMSUM, cIMTAN, cOCT2BIN,
		cOCT2DEC, cOCT2HEX);

	cFormulaFunctionGroup['NotRealised'] = cFormulaFunctionGroup['NotRealised'] || [];
	cFormulaFunctionGroup['NotRealised'].push(cCONVERT);

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBESSELI() {
		cBaseFunction.call(this, "BESSELI");
	}

	cBESSELI.prototype = Object.create(cBaseFunction.prototype);
	cBESSELI.prototype.constructor = cBESSELI;
	cBESSELI.prototype.argumentsMin = 2;
	cBESSELI.prototype.argumentsMax = 2;
	cBESSELI.prototype.Calculate = function ( arg ) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var x = argArray[0];
			var n = argArray[1];

			if ( n < 0 ){
				return new cError( cErrorType.not_numeric );
			}
			if(x < 0){
				x = Math.abs(x);
			}
			n = Math.floor(n);

			return bessi( x, n );
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBESSELJ() {
		cBaseFunction.call(this, "BESSELJ");
	}

	cBESSELJ.prototype = Object.create(cBaseFunction.prototype);
	cBESSELJ.prototype.constructor = cBESSELJ;
	cBESSELJ.prototype.argumentsMin = 2;
	cBESSELJ.prototype.argumentsMax = 2;
	cBESSELJ.prototype.Calculate = function ( arg ) {
		//результаты вычислений как в LO
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var x = argArray[0];
			var n = argArray[1];

			if ( n < 0 ){
				return new cError( cErrorType.not_numeric );
			}
			if(x < 0){
				x = Math.abs(x);
			}
			n = Math.floor(n);

			return BesselJ( x, n );
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};


	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBESSELK() {
		cBaseFunction.call(this, "BESSELK");
	}

	cBESSELK.prototype = Object.create(cBaseFunction.prototype);
	cBESSELK.prototype.constructor = cBESSELK;
	cBESSELK.prototype.argumentsMin = 2;
	cBESSELK.prototype.argumentsMax = 2;
	cBESSELK.prototype.Calculate = function ( arg ) {
		//результаты вычислений как в LO
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var x = argArray[0];
			var n = argArray[1];

			if ( n < 0 || x < 0){
				return new cError( cErrorType.not_numeric );
			}

			n = Math.floor(n);

			return BesselK( x, n );
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};


	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBESSELY() {
		cBaseFunction.call(this, "BESSELY");
	}

	cBESSELY.prototype = Object.create(cBaseFunction.prototype);
	cBESSELY.prototype.constructor = cBESSELY;
	cBESSELY.prototype.argumentsMin = 2;
	cBESSELY.prototype.argumentsMax = 2;
	cBESSELY.prototype.Calculate = function ( arg ) {
		//результаты вычислений как в LO
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var x = argArray[0];
			var n = argArray[1];

			if ( n < 0 || x < 0){
				return new cError( cErrorType.not_numeric );
			}

			n = Math.floor(n);

			return BesselY( x, n );
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};


	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBIN2DEC() {
		cBaseFunction.call(this, "BIN2DEC");
	}

	cBIN2DEC.prototype = Object.create(cBaseFunction.prototype);
	cBIN2DEC.prototype.constructor = cBIN2DEC;
	cBIN2DEC.prototype.argumentsMin = 1;
	cBIN2DEC.prototype.argumentsMax = 1;
	cBIN2DEC.prototype.Calculate = function (arg) {
		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();

		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (validBINNumber(arg0)) {
			var substr = arg0.toString();
			if (substr.length == 10 && substr.substring(0, 1) == "1") {
				this.value = new cNumber(parseInt(substr.substring(1), NumberBase.BIN) - 512);
			} else {
				this.value = new cNumber(parseInt(arg0, NumberBase.BIN));
			}
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBIN2HEX() {
		cBaseFunction.call(this, "BIN2HEX");
	}

	cBIN2HEX.prototype = Object.create(cBaseFunction.prototype);
	cBIN2HEX.prototype.constructor = cBIN2HEX;
	cBIN2HEX.prototype.argumentsMin = 1;
	cBIN2HEX.prototype.argumentsMax = 2;
	cBIN2HEX.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.not_numeric);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validBINNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			var substr = arg0.toString();
			if (substr.length === 10 && substr.substring(0, 1) === '1') {
				this.value =
					new cString((1099511627264 + parseInt(substr.substring(1), NumberBase.BIN)).toString(NumberBase.HEX)
						.toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.BIN, NumberBase.HEX, arg1);
			}
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBIN2OCT() {
		cBaseFunction.call(this, "BIN2OCT");
	}

	cBIN2OCT.prototype = Object.create(cBaseFunction.prototype);
	cBIN2OCT.prototype.constructor = cBIN2OCT;
	cBIN2OCT.prototype.argumentsMin = 1;
	cBIN2OCT.prototype.argumentsMax = 2;
	cBIN2OCT.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.not_numeric);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validBINNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			var substr = arg0.toString();
			if (substr.length === 10 && substr.substring(0, 1) === '1') {
				this.value =
					new cString((1073741312 + parseInt(substr.substring(1), NumberBase.BIN)).toString(NumberBase.OCT)
						.toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.BIN, NumberBase.OCT, arg1);
			}
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBITAND() {
		cBaseFunction.call(this, "BITAND");
	}

	cBITAND.prototype = Object.create(cBaseFunction.prototype);
	cBITAND.prototype.constructor = cBITAND;
	cBITAND.prototype.argumentsMin = 2;
	cBITAND.prototype.argumentsMax = 2;
	cBITAND.prototype.isXLFN = true;
	cBITAND.prototype.Calculate = function (arg) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var arg0 = Math.floor(argArray[0]);
			var arg1 = Math.floor(argArray[1]);

			if ( arg0 < 0 || arg1 < 0 /*|| arg0 > 2^48 || arg1 > 2^48*/){
				return  new cError(cErrorType.not_numeric);
			}

			var res = arg0 & arg1;
			return null !== res && !isNaN(res) ? new cNumber(res) : new cError(cErrorType.wrong_value_type);
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBITLSHIFT() {
		cBaseFunction.call(this, "BITLSHIFT");
	}

	cBITLSHIFT.prototype = Object.create(cBaseFunction.prototype);
	cBITLSHIFT.prototype.constructor = cBITLSHIFT;
	cBITLSHIFT.prototype.argumentsMin = 2;
	cBITLSHIFT.prototype.argumentsMax = 2;
	cBITLSHIFT.prototype.isXLFN = true;
	cBITLSHIFT.prototype.Calculate = function (arg) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var arg0 = Math.floor(argArray[0]);
			var arg1 = Math.floor(argArray[1]);

			if ( arg0 < 0 /*|| arg0 >= 2^48*/){
				return  new cError(cErrorType.not_numeric);
			}

			var res;
			if (arg1 < 0){
				res = Math.floor( arg0 / Math.pow( 2.0, -arg1));
			}else if (arg1 === 0){
				res = arg0;
			}else{
				res = arg0 * Math.pow( 2.0, arg1);
			}

			return null !== res && !isNaN(res) ? new cNumber(res) : new cError(cErrorType.wrong_value_type);
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBITOR() {
		cBaseFunction.call(this, "BITOR");
	}

	cBITOR.prototype = Object.create(cBaseFunction.prototype);
	cBITOR.prototype.constructor = cBITOR;
	cBITOR.prototype.argumentsMin = 2;
	cBITOR.prototype.argumentsMax = 2;
	cBITOR.prototype.isXLFN = true;
	cBITOR.prototype.Calculate = function (arg) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var arg0 = Math.floor(argArray[0]);
			var arg1 = Math.floor(argArray[1]);

			if ( arg0 < 0 || arg1 < 0 /*|| arg0 > 2^48 || arg1 > 2^48*/){
				return  new cError(cErrorType.not_numeric);
			}

			var res = arg0 | arg1;
			return null !== res && !isNaN(res) ? new cNumber(res) : new cError(cErrorType.wrong_value_type);
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBITRSHIFT() {
		cBaseFunction.call(this, "BITRSHIFT");
	}

	cBITRSHIFT.prototype = Object.create(cBaseFunction.prototype);
	cBITRSHIFT.prototype.constructor = cBITRSHIFT;
	cBITRSHIFT.prototype.argumentsMin = 2;
	cBITRSHIFT.prototype.argumentsMax = 2;
	cBITRSHIFT.prototype.isXLFN = true;
	cBITRSHIFT.prototype.Calculate = function (arg) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var arg0 = Math.floor(argArray[0]);
			var arg1 = Math.floor(argArray[1]);

			if ( arg0 < 0 /*|| arg0 >= 2^48*/){
				return  new cError(cErrorType.not_numeric);
			}

			var res;
			if (arg1 < 0){
				res = Math.floor( arg0 * Math.pow( 2.0, -arg1));
			}else if (arg1 === 0){
				res = arg0;
			}else{
				res = Math.floor( arg0 / Math.pow( 2.0, arg1));
			}

			return null !== res && !isNaN(res) ? new cNumber(res) : new cError(cErrorType.wrong_value_type);
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cBITXOR() {
		cBaseFunction.call(this, "BITXOR");
	}

	cBITXOR.prototype = Object.create(cBaseFunction.prototype);
	cBITXOR.prototype.constructor = cBITXOR;
	cBITXOR.prototype.argumentsMin = 2;
	cBITXOR.prototype.argumentsMax = 2;
	cBITXOR.prototype.isXLFN = true;
	cBITXOR.prototype.Calculate = function (arg) {
		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcFunc = function(argArray){
			var arg0 = Math.floor(argArray[0]);
			var arg1 = Math.floor(argArray[1]);

			if ( arg0 < 0 || arg1 < 0 /*|| arg0 > 2^48 || arg1 > 2^48*/){
				return  new cError(cErrorType.not_numeric);
			}

			var res = arg0 ^ arg1;
			return null !== res && !isNaN(res) ? new cNumber(res) : new cError(cErrorType.wrong_value_type);
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcFunc);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCOMPLEX() {
		cBaseFunction.call(this, "COMPLEX");
	}

	cCOMPLEX.prototype = Object.create(cBaseFunction.prototype);
	cCOMPLEX.prototype.constructor = cCOMPLEX;
	cCOMPLEX.prototype.argumentsMin = 2;
	cCOMPLEX.prototype.argumentsMax = 3;
	cCOMPLEX.prototype.Calculate = function (arg) {

		var real = arg[0], img = arg[1], suf = !arg[2] || arg[2] instanceof AscCommonExcel.cEmpty ? new cString("i") :
			arg[2];
		if (real instanceof cArea || img instanceof cArea3D) {
			real = real.cross(arguments[1]);
		} else if (real instanceof cArray) {
			real = real.getElement(0);
		}

		if (img instanceof cArea || img instanceof cArea3D) {
			img = img.cross(arguments[1]);
		} else if (img instanceof cArray) {
			img = img.getElement(0);
		}

		if (suf instanceof cArea || suf instanceof cArea3D) {
			suf = suf.cross(arguments[1]);
		} else if (suf instanceof cArray) {
			suf = suf.getElement(0);
		}

		real = real.tocNumber();
		img = img.tocNumber();
		suf = suf.tocString();

		if (real instanceof cError) {
			return this.value = real;
		}
		if (img instanceof cError) {
			return this.value = img;
		}
		if (suf instanceof cError) {
			return this.value = suf;
		}

		real = real.getValue();
		img = img.getValue();
		suf = suf.getValue();

		if (suf != "i" && suf != "j") {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		var c = new Complex(real, img, suf);

		this.value = new cString(c.toString());

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cCONVERT() {
		cBaseFunction.call(this, "CONVERT");
	}

	cCONVERT.prototype = Object.create(cBaseFunction.prototype);
	cCONVERT.prototype.constructor = cCONVERT;

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cDEC2BIN() {
		cBaseFunction.call(this, "DEC2BIN");
	}

	cDEC2BIN.prototype = Object.create(cBaseFunction.prototype);
	cDEC2BIN.prototype.constructor = cDEC2BIN;
	cDEC2BIN.prototype.argumentsMin = 1;
	cDEC2BIN.prototype.argumentsMax = 2;
	cDEC2BIN.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = Math.floor(arg0.getValue());

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validDEC2BINNumber(arg0) && arg0 >= -512 && arg0 <= 511 &&
			( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			if (arg0 < 0) {
				this.value = new cString('1' + '0'.repeat(9 - (512 + arg0).toString(NumberBase.BIN).length) +
					(512 + arg0).toString(NumberBase.BIN).toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.DEC, NumberBase.BIN, arg1);
			}

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cDEC2HEX() {
		cBaseFunction.call(this, "DEC2HEX");
	}

	cDEC2HEX.prototype = Object.create(cBaseFunction.prototype);
	cDEC2HEX.prototype.constructor = cDEC2HEX;
	cDEC2HEX.prototype.argumentsMin = 1;
	cDEC2HEX.prototype.argumentsMax = 2;
	cDEC2HEX.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = Math.floor(arg0.getValue());

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validDEC2HEXNumber(arg0) && arg0 >= -549755813888 && arg0 <= 549755813887 &&
			( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			if (arg0 < 0) {
				this.value = new cString((1099511627776 + arg0).toString(NumberBase.HEX).toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.DEC, NumberBase.HEX, arg1);
			}

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cDEC2OCT() {
		cBaseFunction.call(this, "DEC2OCT");
	}

	cDEC2OCT.prototype = Object.create(cBaseFunction.prototype);
	cDEC2OCT.prototype.constructor = cDEC2OCT;
	cDEC2OCT.prototype.argumentsMin = 1;
	cDEC2OCT.prototype.argumentsMax = 2;
	cDEC2OCT.prototype.Calculate = function (arg) {
		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocNumber();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = Math.floor(arg0.getValue());

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validDEC2OCTNumber(arg0) && arg0 >= -536870912 && arg0 <= 536870911 &&
			( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			if (arg0 < 0) {
				this.value = new cString((1073741824 + arg0).toString(NumberBase.OCT).toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.DEC, NumberBase.OCT, arg1);
			}

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cDELTA() {
		cBaseFunction.call(this, "DELTA");
	}

	cDELTA.prototype = Object.create(cBaseFunction.prototype);
	cDELTA.prototype.constructor = cDELTA;
	cDELTA.prototype.argumentsMin = 1;
	cDELTA.prototype.argumentsMax = 2;
	cDELTA.prototype.Calculate = function (arg) {

		var number1 = arg[0], number2 = !arg[1] ? new cNumber(0) : arg[1];

		if (number1 instanceof cArea || number2 instanceof cArea3D) {
			number1 = number1.cross(arguments[1]);
		} else if (number1 instanceof cArray) {
			number1 = number1.getElement(0);
		}

		if (number2 instanceof cArea || number2 instanceof cArea3D) {
			number2 = number2.cross(arguments[1]);
		} else if (number2 instanceof cArray) {
			number2 = number2.getElement(0);
		}

		number1 = number1.tocNumber();
		number2 = number2.tocNumber();

		if (number1 instanceof cError) {
			return this.value = number1;
		}
		if (number2 instanceof cError) {
			return this.value = number2;
		}

		number1 = number1.getValue();
		number2 = number2.getValue();

		this.value = new cNumber(number1 == number2 ? 1 : 0);

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cERF() {
		cBaseFunction.call(this, "ERF");
	}

	cERF.prototype = Object.create(cBaseFunction.prototype);
	cERF.prototype.constructor = cERF;
	cERF.prototype.argumentsMin = 1;
	cERF.prototype.argumentsMax = 2;
	cERF.prototype.Calculate = function (arg) {

		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();
		argClone[1] = argClone[1] ? argClone[1].tocNumber() : new cUndefined();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcErf = function(argArray) {
			var a = argArray[0];
			var b = argArray[1];

			var res;
			if(undefined !== b){
				res = new cNumber(rtl_math_erf(b) - rtl_math_erf(a));
			}else{
				res = new cNumber(rtl_math_erf(a));
			}

			return res;
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcErf);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cERF_PRECISE() {
		cBaseFunction.call(this, "ERF.PRECISE");
	}

	cERF_PRECISE.prototype = Object.create(cBaseFunction.prototype);
	cERF_PRECISE.prototype.constructor = cERF_PRECISE;
	cERF_PRECISE.prototype.argumentsMin = 1;
	cERF_PRECISE.prototype.argumentsMax = 1;
	cERF_PRECISE.prototype.isXLFN = true;
	cERF_PRECISE.prototype.Calculate = function (arg) {

		var oArguments = this._prepareArguments(arg, arguments[1], true);
		var argClone = oArguments.args;

		argClone[0] = argClone[0].tocNumber();

		var argError;
		if (argError = this._checkErrorArg(argClone)) {
			return this.value = argError;
		}

		var calcErf = function(argArray) {
			var a = argArray[0];
			return new cNumber(rtl_math_erf(a));
		};

		return this.value = this._findArrayInNumberArguments(oArguments, calcErf);
	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cERFC() {
		cBaseFunction.call(this, "ERFC");
	}

	cERFC.prototype = Object.create(cBaseFunction.prototype);
	cERFC.prototype.constructor = cERFC;
	cERFC.prototype.argumentsMin = 1;
	cERFC.prototype.argumentsMax = 1;
	cERFC.prototype.Calculate = function (arg) {

		var a = arg[0];
		if (a instanceof cArea || a instanceof cArea3D) {
			a = a.cross(arguments[1]);
		} else if (a instanceof cArray) {
			a = a.getElement(0);
		}

		a = a.tocNumber();
		if (a instanceof cError) {
			return this.value = a;
		}

		a = a.getValue();

		this.value = new cNumber(AscCommonExcel.rtl_math_erfc(a));

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {cERFC}
	 */
	function cERFC_PRECISE() {
		cERFC.call(this);
		this.name = "ERFC.PRECISE";
	}

	cERFC_PRECISE.prototype = Object.create(cERFC.prototype);
	cERFC_PRECISE.prototype.constructor = cERFC_PRECISE;
	cERFC_PRECISE.prototype.isXLFN = true;

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cGESTEP() {
		cBaseFunction.call(this, "GESTEP");
	}

	cGESTEP.prototype = Object.create(cBaseFunction.prototype);
	cGESTEP.prototype.constructor = cGESTEP;
	cGESTEP.prototype.argumentsMin = 1;
	cGESTEP.prototype.argumentsMax = 2;
	cGESTEP.prototype.Calculate = function (arg) {

		var number1 = arg[0], number2 = !arg[1] ? new cNumber(0) : arg[1];

		if (number1 instanceof cArea || number2 instanceof cArea3D) {
			number1 = number1.cross(arguments[1]);
		} else if (number1 instanceof cArray) {
			number1 = number1.getElement(0);
		}

		if (number2 instanceof cArea || number2 instanceof cArea3D) {
			number2 = number2.cross(arguments[1]);
		} else if (number2 instanceof cArray) {
			number2 = number2.getElement(0);
		}

		number1 = number1.tocNumber();
		number2 = number2.tocNumber();

		if (number1 instanceof cError) {
			return this.value = number1;
		}
		if (number2 instanceof cError) {
			return this.value = number2;
		}

		number1 = number1.getValue();
		number2 = number2.getValue();

		this.value = new cNumber(number1 >= number2 ? 1 : 0);

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cHEX2BIN() {
		cBaseFunction.call(this, "HEX2BIN");
	}

	cHEX2BIN.prototype = Object.create(cBaseFunction.prototype);
	cHEX2BIN.prototype.constructor = cHEX2BIN;
	cHEX2BIN.prototype.argumentsMin = 1;
	cHEX2BIN.prototype.argumentsMax = 2;
	cHEX2BIN.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validHEXNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			var negative = (arg0.length === 10 && arg0.substring(0, 1).toUpperCase() === 'F'), arg0DEC = (negative) ?
				parseInt(arg0, NumberBase.HEX) - 1099511627776 : parseInt(arg0, NumberBase.HEX);

			if (arg0DEC < -512 || arg0DEC > 511) {
				this.value = new cError(cErrorType.not_numeric)
			} else {

				if (negative) {
					var str = (512 + arg0DEC).toString(NumberBase.BIN);
					this.value = new cString('1' + '0'.repeat(9 - str.length) + str);
				} else {
					this.value = convertFromTo(arg0DEC, NumberBase.DEC, NumberBase.BIN, arg1);
				}

			}
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cHEX2DEC() {
		cBaseFunction.call(this, "HEX2DEC");
	}

	cHEX2DEC.prototype = Object.create(cBaseFunction.prototype);
	cHEX2DEC.prototype.constructor = cHEX2DEC;
	cHEX2DEC.prototype.argumentsMin = 1;
	cHEX2DEC.prototype.argumentsMax = 1;
	cHEX2DEC.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (validHEXNumber(arg0)) {

			arg0 = parseInt(arg0, NumberBase.HEX);
			this.value = new cNumber((arg0 >= 549755813888) ? arg0 - 1099511627776 : arg0);

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cHEX2OCT() {
		cBaseFunction.call(this, "HEX2OCT");
	}

	cHEX2OCT.prototype = Object.create(cBaseFunction.prototype);
	cHEX2OCT.prototype.constructor = cHEX2OCT;
	cHEX2OCT.prototype.argumentsMin = 1;
	cHEX2OCT.prototype.argumentsMax = 2;
	cHEX2OCT.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validHEXNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			arg0 = parseInt(arg0, NumberBase.HEX);

			if (arg0 > 536870911 && arg0 < 1098974756864) {
				this.value = new cError(cErrorType.not_numeric);
			} else {

				if (arg0 >= 1098974756864) {
					this.value = new cString((arg0 - 1098437885952).toString(NumberBase.OCT).toUpperCase());
				} else {
					this.value = convertFromTo(arg0, NumberBase.DEC, NumberBase.OCT, arg1);
				}

			}

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMABS() {
		cBaseFunction.call(this, "IMABS");
	}

	cIMABS.prototype = Object.create(cBaseFunction.prototype);
	cIMABS.prototype.constructor = cIMABS;
	cIMABS.prototype.argumentsMin = 1;
	cIMABS.prototype.argumentsMax = 1;
	cIMABS.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		this.value = new cNumber(c.Abs());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMAGINARY() {
		cBaseFunction.call(this, "IMAGINARY");
	}

	cIMAGINARY.prototype = Object.create(cBaseFunction.prototype);
	cIMAGINARY.prototype.constructor = cIMAGINARY;
	cIMAGINARY.prototype.argumentsMin = 1;
	cIMAGINARY.prototype.argumentsMax = 1;
	cIMAGINARY.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		this.value = new cNumber(c.Imag());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMARGUMENT() {
		cBaseFunction.call(this, "IMARGUMENT");
	}

	cIMARGUMENT.prototype = Object.create(cBaseFunction.prototype);
	cIMARGUMENT.prototype.constructor = cIMARGUMENT;
	cIMARGUMENT.prototype.argumentsMin = 1;
	cIMARGUMENT.prototype.argumentsMax = 1;
	cIMARGUMENT.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		this.value = new cNumber(c.Arg());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCONJUGATE() {
		cBaseFunction.call(this, "IMCONJUGATE");
	}

	cIMCONJUGATE.prototype = Object.create(cBaseFunction.prototype);
	cIMCONJUGATE.prototype.constructor = cIMCONJUGATE;
	cIMCONJUGATE.prototype.argumentsMin = 1;
	cIMCONJUGATE.prototype.argumentsMax = 1;
	cIMCONJUGATE.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		this.value = new cString(c.Conj());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCOS() {
		cBaseFunction.call(this, "IMCOS");
	}

	cIMCOS.prototype = Object.create(cBaseFunction.prototype);
	cIMCOS.prototype.constructor = cIMCOS;
	cIMCOS.prototype.argumentsMin = 1;
	cIMCOS.prototype.argumentsMax = 1;
	cIMCOS.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Cos();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCOSH() {
		cBaseFunction.call(this, "IMCOSH");
	}

	cIMCOSH.prototype = Object.create(cBaseFunction.prototype);
	cIMCOSH.prototype.constructor = cIMCOSH;
	cIMCOSH.prototype.argumentsMin = 1;
	cIMCOSH.prototype.argumentsMax = 1;
	cIMCOSH.prototype.isXLFN = true;
	cIMCOSH.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Cosh();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCOT() {
		cBaseFunction.call(this, "IMCOT");
	}

	cIMCOT.prototype = Object.create(cBaseFunction.prototype);
	cIMCOT.prototype.constructor = cIMCOT;
	cIMCOT.prototype.argumentsMin = 1;
	cIMCOT.prototype.argumentsMax = 1;
	cIMCOT.prototype.isXLFN = true;
	cIMCOT.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if(0 == arg0.value){
			return this.value = new cError(cErrorType.not_numeric);
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Cot();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCSC() {
		cBaseFunction.call(this, "IMCSC");
	}
	//TODO проверить!!!
	cIMCSC.prototype = Object.create(cBaseFunction.prototype);
	cIMCSC.prototype.constructor = cIMCSC;
	cIMCSC.prototype.argumentsMin = 1;
	cIMCSC.prototype.argumentsMax = 1;
	cIMCSC.prototype.isXLFN = true;
	cIMCSC.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		if(0 == arg0.value){
			return this.value = new cError(cErrorType.not_numeric);
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Csc();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMCSCH() {
		cBaseFunction.call(this, "IMCSCH");
	}
	//TODO проверить!!!
	cIMCSCH.prototype = Object.create(cBaseFunction.prototype);
	cIMCSCH.prototype.constructor = cIMCSCH;
	cIMCSCH.prototype.argumentsMin = 1;
	cIMCSCH.prototype.argumentsMax = 1;
	cIMCSCH.prototype.isXLFN = true;
	cIMCSCH.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		if(0 == arg0.value){
			return this.value = new cError(cErrorType.not_numeric);
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Csch();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMDIV() {
		cBaseFunction.call(this, "IMDIV");
	}

	cIMDIV.prototype = Object.create(cBaseFunction.prototype);
	cIMDIV.prototype.constructor = cIMDIV;
	cIMDIV.prototype.argumentsMin = 2;
	cIMDIV.prototype.argumentsMax = 2;
	cIMDIV.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}


		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		arg1 = arg1.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		var c1 = new Complex(arg0.toString()), c2 = new Complex(arg1.toString()), c3;

		if (c1 instanceof cError || c2 instanceof cError) {
			return this.value = new cError(cErrorType.not_numeric);
		}

		c3 = c1.Div(c2);

		this.value = new cString(c3.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMEXP() {
		cBaseFunction.call(this, "IMEXP");
	}

	cIMEXP.prototype = Object.create(cBaseFunction.prototype);
	cIMEXP.prototype.constructor = cIMEXP;
	cIMEXP.prototype.argumentsMin = 1;
	cIMEXP.prototype.argumentsMax = 1;
	cIMEXP.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Exp();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMLN() {
		cBaseFunction.call(this, "IMLN");
	}

	cIMLN.prototype = Object.create(cBaseFunction.prototype);
	cIMLN.prototype.constructor = cIMLN;
	cIMLN.prototype.argumentsMin = 1;
	cIMLN.prototype.argumentsMax = 1;
	cIMLN.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		var r = c.Ln();

		if (r instanceof cError) {
			return r;
		}

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMLOG10() {
		cBaseFunction.call(this, "IMLOG10");
	}

	cIMLOG10.prototype = Object.create(cBaseFunction.prototype);
	cIMLOG10.prototype.constructor = cIMLOG10;
	cIMLOG10.prototype.argumentsMin = 1;
	cIMLOG10.prototype.argumentsMax = 1;
	cIMLOG10.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		var r = c.Log10();

		if (r instanceof cError) {
			return r;
		}

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMLOG2() {
		cBaseFunction.call(this, "IMLOG2");
	}

	cIMLOG2.prototype = Object.create(cBaseFunction.prototype);
	cIMLOG2.prototype.constructor = cIMLOG2;
	cIMLOG2.prototype.argumentsMin = 1;
	cIMLOG2.prototype.argumentsMax = 1;
	cIMLOG2.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		var r = c.Log2();

		if (r instanceof cError) {
			return r;
		}

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMPOWER() {
		cBaseFunction.call(this, "IMPOWER");
	}

	cIMPOWER.prototype = Object.create(cBaseFunction.prototype);
	cIMPOWER.prototype.constructor = cIMPOWER;
	cIMPOWER.prototype.argumentsMin = 2;
	cIMPOWER.prototype.argumentsMax = 2;
	cIMPOWER.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		arg1 = arg1.tocNumber();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		if (c.Power(arg1.getValue())) {
			this.value = new cString(c.toString());
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMPRODUCT() {
		cBaseFunction.call(this, "IMPRODUCT");
	}

	cIMPRODUCT.prototype = Object.create(cBaseFunction.prototype);
	cIMPRODUCT.prototype.constructor = cIMPRODUCT;
	cIMPRODUCT.prototype.argumentsMin = 1;
	cIMPRODUCT.prototype.Calculate = function (arg) {
		var arg0 = arg[0], t = this;

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString()), c1;

		if (c instanceof cError) {
			return this.value = c;
		}

		for (var i = 1; i < this.getArguments(); i++) {

			var argI = arg[i];
			if (argI instanceof cArea || argI instanceof cArea3D) {
				var argIArr = argI.getValue(), _arg;
				for (var j = 0; j < argIArr.length; j++) {
					_arg = argIArr[i].tocString();

					if (_arg instanceof cError) {
						return this.value = _arg;
					}

					c1 = new Complex(_arg.toString());

					if (c1 instanceof cError) {
						return this.value = c1;
					}

					c.Product(c1);

				}
				continue;
			} else if (argI instanceof cArray) {
				argI.foreach(function (elem) {
					var e = elem.tocString();
					if (e instanceof cError) {
						return t.value = e;
					}

					c1 = new Complex(e.toString());

					if (c1 instanceof cError) {
						return t.value = c1;
					}

					c.Product(c1);

				});
				continue;
			}

			argI = argI.tocString();

			if (argI instanceof cError) {
				return this.value = argI;
			}

			c1 = new Complex(argI.toString());

			c.Product(c1);

		}

		if (c instanceof cError) {
			this.value = c;
		} else {
			this.value = new cString(c.toString());
		}

		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMREAL() {
		cBaseFunction.call(this, "IMREAL");
	}

	cIMREAL.prototype = Object.create(cBaseFunction.prototype);
	cIMREAL.prototype.constructor = cIMREAL;
	cIMREAL.prototype.argumentsMin = 1;
	cIMREAL.prototype.argumentsMax = 1;
	cIMREAL.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		this.value = new cNumber(c.real);
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSEC() {
		cBaseFunction.call(this, "IMSEC");
	}
	cIMSEC.prototype = Object.create(cBaseFunction.prototype);
	cIMSEC.prototype.constructor = cIMSEC;
	cIMSEC.prototype.argumentsMin = 1;
	cIMSEC.prototype.argumentsMax = 1;
	cIMSEC.prototype.isXLFN = true;
	cIMSEC.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Sec();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSECH() {
		cBaseFunction.call(this, "IMSECH");
	}
	cIMSECH.prototype = Object.create(cBaseFunction.prototype);
	cIMSECH.prototype.constructor = cIMSECH;
	cIMSECH.prototype.argumentsMin = 1;
	cIMSECH.prototype.argumentsMax = 1;
	cIMSECH.prototype.isXLFN = true;
	cIMSECH.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Sech();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};



	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSIN() {
		cBaseFunction.call(this, "IMSIN");
	}

	cIMSIN.prototype = Object.create(cBaseFunction.prototype);
	cIMSIN.prototype.constructor = cIMSIN;
	cIMSIN.prototype.argumentsMin = 1;
	cIMSIN.prototype.argumentsMax = 1;
	cIMSIN.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Sin();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSINH() {
		cBaseFunction.call(this, "IMSINH");
	}

	cIMSINH.prototype = Object.create(cBaseFunction.prototype);
	cIMSINH.prototype.constructor = cIMSINH;
	cIMSINH.prototype.argumentsMin = 1;
	cIMSINH.prototype.argumentsMax = 1;
	cIMSINH.prototype.isXLFN = true;
	cIMSINH.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Sinh();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSQRT() {
		cBaseFunction.call(this, "IMSQRT");
	}

	cIMSQRT.prototype = Object.create(cBaseFunction.prototype);
	cIMSQRT.prototype.constructor = cIMSQRT;
	cIMSQRT.prototype.argumentsMin = 1;
	cIMSQRT.prototype.argumentsMax = 1;
	cIMSQRT.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.SQRT();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSUB() {
		cBaseFunction.call(this, "IMSUB");
	}

	cIMSUB.prototype = Object.create(cBaseFunction.prototype);
	cIMSUB.prototype.constructor = cIMSUB;
	cIMSUB.prototype.argumentsMin = 2;
	cIMSUB.prototype.argumentsMax = 2;
	cIMSUB.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}


		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		arg1 = arg1.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}
		if (arg1 instanceof cError) {
			return this.value = arg1;
		}

		var c1 = new Complex(arg0.toString()), c2 = new Complex(arg1.toString());

		if (c1 instanceof cError || c2 instanceof cError) {
			return this.value = new cError(cErrorType.not_numeric);
		}

		c1.Sub(c2);

		this.value = new cString(c1.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMSUM() {
		cBaseFunction.call(this, "IMSUM");
	}

	cIMSUM.prototype = Object.create(cBaseFunction.prototype);
	cIMSUM.prototype.constructor = cIMSUM;
	cIMSUM.prototype.argumentsMin = 1;
	cIMSUM.prototype.Calculate = function (arg) {

		var arg0 = arg[0], t = this;

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		var c = new Complex(arg0.toString()), c1;

		if (c instanceof cError) {
			return this.value = c;
		}

		for (var i = 1; i < this.getArguments(); i++) {

			var argI = arg[i];
			if (argI instanceof cArea || argI instanceof cArea3D) {
				var argIArr = argI.getValue(), _arg;
				for (var j = 0; j < argIArr.length; j++) {
					_arg = argIArr[i].tocString();

					if (_arg instanceof cError) {
						return this.value = _arg;
					}

					c1 = new Complex(_arg.toString());

					if (c1 instanceof cError) {
						return this.value = c1;
					}

					c.Sum(c1);

				}
				continue;
			} else if (argI instanceof cArray) {
				argI.foreach(function (elem) {
					var e = elem.tocString();
					if (e instanceof cError) {
						return t.value = e;
					}

					c1 = new Complex(e.toString());

					if (c1 instanceof cError) {
						return t.value = c1;
					}

					c.Sum(c1);

				});
				continue;
			}

			argI = argI.tocString();

			if (argI instanceof cError) {
				return this.value = argI;
			}

			c1 = new Complex(argI.toString());

			c.Sum(c1);

		}

		if (c instanceof cError) {
			this.value = c;
		} else {
			this.value = new cString(c.toString());
		}

		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cIMTAN() {
		cBaseFunction.call(this, "IMTAN");
	}
	//TODO проверить!!!
	cIMTAN.prototype = Object.create(cBaseFunction.prototype);
	cIMTAN.prototype.constructor = cIMTAN;
	cIMTAN.prototype.argumentsMin = 1;
	cIMTAN.prototype.argumentsMax = 1;
	cIMTAN.prototype.isXLFN = true;
	cIMTAN.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		if(arg0.value === true || arg0.value === false){
			return this.value = new cError(cErrorType.wrong_value_type);
		}

		var c = new Complex(arg0.toString());

		if (c instanceof cError) {
			return this.value = c;
		}

		c.Tan();

		this.value = new cString(c.toString());
		this.value.numFormat = 0;

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cOCT2BIN() {
		cBaseFunction.call(this, "OCT2BIN");
	}

	cOCT2BIN.prototype = Object.create(cBaseFunction.prototype);
	cOCT2BIN.prototype.constructor = cOCT2BIN;
	cOCT2BIN.prototype.argumentsMin = 1;
	cOCT2BIN.prototype.argumentsMax = 2;
	cOCT2BIN.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validOCTNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			var negative = (arg0.length === 10 && arg0.substring(0, 1).toUpperCase() === '7'), arg0DEC = (negative) ?
				parseInt(arg0, NumberBase.OCT) - 1073741824 : parseInt(arg0, NumberBase.OCT);

			if (arg0DEC < -512 || arg0DEC > 511) {
				this.value = new cError(cErrorType.not_numeric)
			} else {

				if (negative) {
					var str = (512 + arg0DEC).toString(NumberBase.BIN);
					this.value = new cString(('1' + '0'.repeat(9 - str.length) + str).toUpperCase());
				} else {
					this.value = convertFromTo(arg0DEC, NumberBase.DEC, NumberBase.BIN, arg1);
				}

			}
		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cOCT2DEC() {
		cBaseFunction.call(this, "OCT2DEC");
	}

	cOCT2DEC.prototype = Object.create(cBaseFunction.prototype);
	cOCT2DEC.prototype.constructor = cOCT2DEC;
	cOCT2DEC.prototype.argumentsMin = 1;
	cOCT2DEC.prototype.argumentsMax = 1;
	cOCT2DEC.prototype.Calculate = function (arg) {

		var arg0 = arg[0];

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();

		if (arg0 instanceof cError) {
			return this.value = arg0;
		}

		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (validOCTNumber(arg0)) {

			arg0 = parseInt(arg0, NumberBase.OCT);
			this.value = new cNumber((arg0 >= 536870912) ? arg0 - 1073741824 : arg0);

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};

	/**
	 * @constructor
	 * @extends {AscCommonExcel.cBaseFunction}
	 */
	function cOCT2HEX() {
		cBaseFunction.call(this, "OCT2HEX");
	}

	cOCT2HEX.prototype = Object.create(cBaseFunction.prototype);
	cOCT2HEX.prototype.constructor = cOCT2HEX;
	cOCT2HEX.prototype.argumentsMin = 1;
	cOCT2HEX.prototype.argumentsMax = 2;
	cOCT2HEX.prototype.Calculate = function (arg) {

		var arg0 = arg[0], arg1 = arg[1] ? arg[1] : new cUndefined();

		if (arg0 instanceof cArea || arg0 instanceof cArea3D) {
			arg0 = arg0.cross(arguments[1]);
		} else if (arg0 instanceof cArray) {
			arg0 = arg0.getElementRowCol(0, 0);
		}

		if (arg1 instanceof cArea || arg1 instanceof cArea3D) {
			arg1 = arg1.cross(arguments[1]);
		} else if (arg1 instanceof cArray) {
			arg1 = arg1.getElementRowCol(0, 0);
		}

		arg0 = arg0.tocString();
		if (arg0 instanceof cError) {
			return this.value = new cError(cErrorType.wrong_value_type);
		}
		arg0 = arg0.getValue();

		if (arg0.length == 0) {
			arg0 = 0;
		}

		if (!(arg1 instanceof cUndefined)) {
			arg1 = arg1.tocNumber();
			if (arg1 instanceof cError) {
				return this.value = new cError(cErrorType.wrong_value_type);
			}
		}
		arg1 = arg1.getValue();

		if (validHEXNumber(arg0) && ( arg1 > 0 && arg1 <= 10 || arg1 == undefined )) {

			arg0 = parseInt(arg0, NumberBase.OCT);

			if (arg0 >= 536870912) {
				this.value = new cString(('ff' + (arg0 + 3221225472).toString(NumberBase.HEX)).toUpperCase());
			} else {
				this.value = convertFromTo(arg0, NumberBase.DEC, NumberBase.HEX, arg1);
			}

		} else {
			this.value = new cError(cErrorType.not_numeric);
		}

		return this.value;

	};
})(window);
