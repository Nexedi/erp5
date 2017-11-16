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
(function (/** Window */window, undefined) {

    /*
     * Import
     * -----------------------------------------------------------------------------
     */

    var asc = window["Asc"];

    function colorObjToAscColor(color) {
        var oRes = null;
        var r = color.getR();
        var g = color.getG();
        var b = color.getB();
        var bTheme = false;
        if(color instanceof AscCommonExcel.ThemeColor && null != color.theme)
        {
            var array_colors_types = [6, 15, 7, 16, 0, 1, 2, 3, 4, 5];
            var themePresentation = array_colors_types[color.theme];
            var tintExcel = 0;
            if(null != color.tint)
                tintExcel = color.tint;
            var tintPresentation = 0;
            var basecolor = AscCommonExcel.g_oColorManager.getThemeColor(color.theme);
            var oThemeColorTint = AscCommonExcel.g_oThemeColorsDefaultModsSpreadsheet[AscCommon.GetDefaultColorModsIndex(basecolor.getR(), basecolor.getG(), basecolor.getB())];
            if(null != oThemeColorTint)
            {
                for(var i = 0 , length = oThemeColorTint.length; i < length; ++i)
                {
                    var cur = oThemeColorTint[i];
                    //0.005 установлено экспериментально
                    if(Math.abs(cur - tintExcel) < 0.005)
                    {
                        bTheme = true;
                        tintPresentation = i;
                        break;
                    }
                }
            }
            if(bTheme)
            {
                oRes = new Asc.asc_CColor();
                oRes.r = r;
                oRes.g = g;
                oRes.b = b;
                oRes.a = 255;
                oRes.type = Asc.c_oAscColor.COLOR_TYPE_SCHEME;
                oRes.value = themePresentation;
            }
        }
        if(false == bTheme)
            oRes = AscCommon.CreateAscColorCustom(r, g, b);
        return oRes;
    }

    var oldPpi = undefined,
        cvt = undefined;

    /**
     * Gets ratio to convert units
     * @param {Number} fromUnits  Units (0=px, 1=pt, 2=in, 3=mm)
     * @param {Number} toUnits    Units (0=px, 1=pt, 2=in, 3=mm)
     * @param {Number} ppi        Points per inch
     * @return {Number}  Ratio
     */
    function getCvtRatio(fromUnits, toUnits, ppi) {
        if (ppi !== oldPpi || oldPpi === undefined) {
            var _ppi  = 1 / ppi,
                _72   = 1 / 72,
                _25_4 = 1 / 25.4;
            cvt = [
                /*    px          pt       in        mm    */
                /*px*/[         1,   72*_ppi,   _ppi,  25.4*_ppi ],
                /*pt*/[   ppi*_72,         1,    _72,   25.4*_72 ],
                /*in*/[       ppi,        72,      1,       25.4 ],
                /*mm*/[ ppi*_25_4,  72*_25_4,  _25_4,          1 ]
            ];
            oldPpi = ppi;
        }
        return cvt[fromUnits][toUnits];
    }

    /**
     * Округляет текущее значение в pt таким образом, чтобы при переводе его в px при указанном DPI получалось
     * целое число пикселей
     * @param {type} origPt
     * @param {type} ppi
     * @param {type} pxAddon
     * @returns {Number}
     */
    function calcNearestPt(origPt, ppi, pxAddon) {
        var a = pxAddon !== undefined ? pxAddon : 0,
            x = origPt * ppi / 72,
            y = x | x,
            p = x - y < .000000001 ? 0 : 1; // to fix float number precision caused by binary presentation
        return (y + p + a) / ppi * 72;
    }

    /**
     * @constructor
     */
    function Matrix() {
        if ( !(this instanceof Matrix) ) {
            return new Matrix();
        }

        this.sx  = 1.0;
        this.shx = 0.0;
        this.shy = 0.0;
        this.sy  = 1.0;
        this.tx  = 0.0;
        this.ty  = 0.0;

        return this;
    }
    Matrix.prototype.reset = function () {
        this.sx  = 1.0;
        this.shx = 0.0;
        this.shy = 0.0;
        this.sy  = 1.0;
        this.tx  = 0.0;
        this.ty  = 0.0;
    };

    Matrix.prototype.assign = function (sx, shx, shy, sy, tx, ty) {
        this.sx  = sx;
        this.shx = shx;
        this.shy = shy;
        this.sy  = sy;
        this.tx  = tx;
        this.ty  = ty;
    };

    Matrix.prototype.copyFrom = function (matrix) {
        this.sx  = matrix.sx;
        this.shx = matrix.shx;
        this.shy = matrix.shy;
        this.sy  = matrix.sy;
        this.tx  = matrix.tx;
        this.ty  = matrix.ty;
    };

    Matrix.prototype.clone = function () {
        var m = new Matrix();
        m.copyFrom(this);
        return m;
    };

    Matrix.prototype.multiply = function (matrix, order) {
        if (AscCommon.MATRIX_ORDER_PREPEND === order) {
            var m = matrix.clone();
            m.multiply(this, AscCommon.MATRIX_ORDER_APPEND);
            this.copyFrom(m);
        } else {
            var t0   = this.sx  * matrix.sx  + this.shy * matrix.shx;
            var t2   = this.shx * matrix.sx  + this.sy  * matrix.shx;
            var t4   = this.tx  * matrix.sx  + this.ty  * matrix.shx + matrix.tx;
            this.shy = this.sx  * matrix.shy + this.shy * matrix.sy;
            this.sy  = this.shx * matrix.shy + this.sy  * matrix.sy;
            this.ty  = this.tx  * matrix.shy + this.ty  * matrix.sy + matrix.ty;
            this.sx  = t0;
            this.shx = t2;
            this.tx  = t4;
        }
    };

    Matrix.prototype.translate = function (x, y, order) {
        var m = new Matrix();
        m.tx  = x;
        m.ty  = y;
        this.multiply(m, order);
    };

    Matrix.prototype.scale = function (x, y, order) {
        var m = new Matrix();
        m.sx  = x;
        m.sy  = y;
        this.multiply(m, order);
    };

    Matrix.prototype.rotate = function (a, order) {
        var m = new Matrix();
        var rad = AscCommon.deg2rad(a);
        m.sx  = Math.cos(rad);
        m.shx = Math.sin(rad);
        m.shy = -Math.sin(rad);
        m.sy  = Math.cos(rad);
        this.multiply(m, order);
    };

    Matrix.prototype.rotateAt = function (a, x, y, order) {
        this.translate(-x, -y, order);
        this.rotate(a, order);
        this.translate(x, y, order);
    };

    Matrix.prototype.determinant = function () {
        return this.sx * this.sy - this.shy * this.shx;
    };

    Matrix.prototype.invert = function () {
        var det = this.determinant();
        if (0.0001 > det) {return;}
        var d = 1 / det;

        var t0 = this.sy * d;
        this.sy =  this.sx * d;
        this.shy = -this.shy * d;
        this.shx = -this.shx * d;

        var t4 = -this.tx * t0  - this.ty * this.shx;
        this.ty = -this.tx * this.shy - this.ty * this.sy;

        this.sx = t0;
        this.tx = t4;
    };

    Matrix.prototype.transformPointX = function (x, y) {
        return x * this.sx  + y * this.shx + this.tx;
    };

    Matrix.prototype.transformPointY = function (x, y) {
        return x * this.shy + y * this.sy  + this.ty;
    };

    /** Calculates rotation angle */
    Matrix.prototype.getRotation = function () {
        var x1 = 0.0;
        var y1 = 0.0;
        var x2 = 1.0;
        var y2 = 0.0;
        this.transformPoint(x1, y1);
        this.transformPoint(x2, y2);
        var a = Math.atan2(y2-y1, x2-x1);
        return AscCommon.rad2deg(a);
    };

    /**
     * Creates font properties
     * -----------------------------------------------------------------------------
     * @constructor
     * @param {String} family     Font family
     * @param {Number} size       Font size
     * @param {Boolean} bold      Font style - bold
     * @param {Boolean} italic    Font style - italic
     * @param {String} underline  Font style - type of underline
     * @param {String} strikeout  Font style - type of strike-out
     *
     * @memberOf Asc
     */
    function FontProperties(family, size, bold, italic, underline, strikeout) {
        this.FontFamily = {Name: family, Index: -1, Angle : 0};
        this.FontSize   = size;
        this.Bold       = !!bold;
        this.Italic     = !!italic;
        this.Underline  = underline;
        this.Strikeout  = strikeout;

        return this;
    }
    /**
     * Assigns font preperties from another object
     * @param {FontProperties} font
     */
    FontProperties.prototype.copyFrom = function (font) {
        this.FontFamily.Name  = font.FontFamily.Name;
        this.FontFamily.Index = font.FontFamily.Index;
        this.FontSize  = font.FontSize;
        this.Bold      = font.Bold;
        this.Italic    = font.Italic;
        this.Underline = font.Underline;
        this.Strikeout = font.Strikeout;
    };

    /** @return {FontProperties} */
    FontProperties.prototype.clone = function () {
        return new FontProperties(this.FontFamily.Name, this.FontSize,
            this.Bold, this.Italic, this.Underline, this.Strikeout);
    };

    FontProperties.prototype.isEqual = function (font) {
        return font !== undefined &&
            this.FontFamily.Name.toLowerCase() === font.FontFamily.Name.toLowerCase() &&
            this.FontSize === font.FontSize &&
            this.Bold === font.Bold &&
            this.Italic === font.Italic;
    };



    /**
     * Creates text metrics
     * -----------------------------------------------------------------------------
     * @constructor
     * @param {Number} width
     * @param {Number} height
     * @param {Number} lineHeight
     * @param {Number} baseline
     * @param {Number} descender
     * @param {Number} fontSize
     * @param {Number} centerline
     * @param {Number} widthBB
     *
     * @memberOf Asc
     */
    function TextMetrics(width, height, lineHeight, baseline, descender, fontSize, centerline, widthBB) {
        if ( !(this instanceof TextMetrics) ) {
            return new TextMetrics(width, height, lineHeight, baseline, descender, fontSize, centerline, widthBB);
        }

        this.width      = width !== undefined ? width : 0;
        this.height     = height !== undefined ? height : 0;
        this.lineHeight = lineHeight !== undefined ? lineHeight : 0;
        this.baseline   = baseline !== undefined ? baseline : 0;
        this.descender  = descender !== undefined ? descender : 0;
        this.fontSize   = fontSize !== undefined ? fontSize : 0;
        this.centerline = centerline !== undefined ? centerline : 0;
        this.widthBB    = widthBB !== undefined ? widthBB : 0;

        return this;
    }



    /**
     * Creates font metrics
     * -----------------------------------------------------------------------------
     * @constructor
     *
     * @memberOf Asc
     */
    function FontMetrics () {
        this.ascender = 0;
        this.descender = 0;
        this.lineGap = 0;

        this.nat_scale = 0;
        this.nat_y1 = 0;
        this.nat_y2 = 0;
    }

    FontMetrics.prototype.clone = function () {
        var res = new FontMetrics();
        res.ascender = this.ascender;
        res.descender = this.descender;
        res.lineGap = this.lineGap;

        res.nat_scale = this.nat_scale;
        res.nat_y1 = this.nat_y1;
        res.nat_y2 = this.nat_y2;
        return res;
    };


    /**
     * Emulates scalable canvas context
     * -----------------------------------------------------------------------------
     * @constructor
     * @param {Object} settings  Settings : {
	 *   canvas : HTMLElement
	 *   units  : units (0=px, 1=pt, 2=in, 3=mm)
	 *   font   : FontProperties
	 * }
     *
     * @memberOf Asc
     */
    function DrawingContext(settings) {
        this.canvas = null;
        this.ctx = null;

        // JS TO BRIDGE
        this.nctx = window["native"];
        this.napi_fmt = [{},{},{},{}];
        this.deviceDPI = this.nctx["GetDeviceDPI"]();
        this.deviceScale = this.nctx["GetDeviceScale"]();

        this.setCanvas(settings.canvas);

        this.ppiX = 96.0 * this.deviceScale * (96.0 / (this.deviceDPI * this.deviceScale));
        this.ppiY = 96.0 * this.deviceScale * (96.0 / (this.deviceDPI * this.deviceScale));

        this.ppiX = this.deviceDPI; //96.0 * this.deviceScale * (96.0 / (this.deviceDPI * this.deviceScale));
        this.ppiY = this.deviceDPI; //96.0 * this.deviceScale * (96.0 / (this.deviceDPI * this.deviceScale));

        this._mct  = new Matrix();  // units transform
        this._mt   = new Matrix();  // user transform
        this._mbt  = new Matrix();  // bound transform
        this._mft  = new Matrix();  // full transform
        this._mift = new Matrix();  // inverted full transform
        this._im   = new Matrix();

        this.scaleFactor = 1;

        this.units  = 3/*mm*/;
        this.changeUnits(undefined !== settings.units ? settings.units : this.units);

        this.fmgrGraphics = undefined !== settings.fmgrGraphics ? settings.fmgrGraphics : null;
        if (null === this.fmgrGraphics) {
            throw "Can not set graphics in DrawingContext";
        }

        /** @type FontProperties */
        this.font = undefined !== settings.font ? settings.font : null;
        // Font должен быть передан (он общий для всех DrawingContext, т.к. может возникнуть ситуация как в баге http://bugzilla.onlyoffice.com/show_bug.cgi?id=19784)
        if (null === this.font) {
            throw "Can not set font in DrawingContext";
        }

        // AscCommon.CColor
        this.fillColor = new AscCommon.CColor(255, 255, 255);

        return this;
    }

    /**
     * Returns width of drawing context in current units
     * @param {Number} [units]  Единицы измерения (0=px, 1=pt, 2=in, 3=mm) в которых будет возвращена ширина
     * @return {Number}
     */
    DrawingContext.prototype.getWidth = function (units) {
        var i = units >= 0 && units <=3 ? units : this.units;
        return this.canvas.width * getCvtRatio(0/*px*/, i, this.ppiX);
    };

    /**
     * Returns height of drawing context in current units
     * @param {Number} [units]  Единицы измерения (0=px, 1=pt, 2=in, 3=mm) в которых будет возвращена высота
     * @return {Number}
     */
    DrawingContext.prototype.getHeight = function (units) {
        var i = units >= 0 && units <=3 ? units : this.units;
        return this.canvas.height * getCvtRatio(0/*px*/, i, this.ppiY);
    };

    /**
     * Returns canvas element
     * @type {Element}
     */
    DrawingContext.prototype.getCanvas = function () {
        return this.canvas;
    };

    /**
     *
     * @param canvas
     */
    DrawingContext.prototype.setCanvas = function (canvas) {    // NOT USE
        if (null == canvas) {return;}
        this.canvas = canvas;
        this.ctx = this.canvas.getContext("2d");
    };

    /**
     * Returns pixels per inch ratio
     * @type {Number}
     */
    DrawingContext.prototype.getPPIX = function () {
        return this.ppiX;
    };

    /**
     * Returns pixels per inch ratio
     * @type {Number}
     */
    DrawingContext.prototype.getPPIY = function () {
        return this.ppiY;
    };

    /**
     * Returns currrent units (0=px, 1=pt, 2=in, 3=mm)
     * @type {Number}
     */
    DrawingContext.prototype.getUnits = function () {
        return this.units;
    };

    DrawingContext.prototype.moveImageDataSafari = function (sx, sy, w, h, x, y) {
        var sr = this._calcRect(sx, sy, w, h);
        var r = this._calcRect(x, y);
        var imgData = this.ctx.getImageData(sr.x, sr.y, sr.w, sr.h);

        var minX, maxX, minY, maxY;
        if (sx < x) {
            minX = sr.x;
            maxX = r.x;
        } else {
            minX = r.x;
            maxX = sr.x;
        }
        if (sy < y) {
            minY = sr.y;
            maxY = r.y;
        } else {
            minY = r.y;
            maxY = sr.y;
        }
        this.ctx.clearRect(minX, minY, maxX + sr.w, maxY + sr.h);
        this.ctx.putImageData(imgData, r.x, r.y);
        return this;
    };
    DrawingContext.prototype.moveImageData = function (sx, sy, w, h, x, y) {
        var sr = this._calcRect(sx, sy, w, h);
        var r = this._calcRect(x, y);

        this.ctx.save();
        this.ctx.globalCompositeOperation = 'copy';
        this.ctx.beginPath();
        this.ctx.rect(r.x, r.y, sr.w, sr.h);
        this.ctx.clip();

        this.ctx.drawImage(this.getCanvas(), sr.x, sr.y, sr.w, sr.h, r.x, r.y, sr.w, sr.h);

        this.ctx.restore();
        this.ctx.beginPath();

        return this;
    };

    /**
     * Changes units of drawing context
     * @param {Number} units  New units of drawing context (0=px, 1=pt, 2=in, 3=mm)
     */
    DrawingContext.prototype.changeUnits = function (units) {
        var i = units >= 0 && units <=3 ? units : 0;
        this._mct.sx = getCvtRatio(i, 0/*px*/, this.ppiX);
        this._mct.sy = getCvtRatio(i, 0/*px*/, this.ppiY);
        this._calcMFT();
        this.units = units;
        return this;
    };

    /**
     * Returns currrent zoom ratio
     * @type {Number}
     */
    DrawingContext.prototype.getZoom = function () {
        return this.scaleFactor;
    };

    /**
     * Changes scale factor of drawing context by changing its PPI
     * @param {Number} factor
     */
    DrawingContext.prototype.changeZoom = function (factor) {
        if (factor <= 0) {throw "Scale factor must be >= 0";}

        factor = Asc.round(factor * 1000) / 1000;

        this.ppiX = Asc.round(this.ppiX / this.scaleFactor * factor * 1000) / 1000;
        this.ppiY = Asc.round(this.ppiY / this.scaleFactor * factor * 1000) / 1000;
        this.scaleFactor = factor;

        // reinitialize
        this.changeUnits(this.units);
        this.setFont(this.font);

        return this;
    };

    /**
     * Resets dimensions of drawing context (canvas 'width' and 'height' attributes)
     * @param {Number} width   New width in current units
     * @param {Number} height  New height in current units
     */
    DrawingContext.prototype.resetSize = function (width, height) {
        var w = Asc.round( width  * getCvtRatio(this.units, 0/*px*/, this.ppiX) ),
            h = Asc.round( height * getCvtRatio(this.units, 0/*px*/, this.ppiY) );
        if (w !== this.canvas.width) {
            this.canvas.width = w;
        }
        if (h !== this.canvas.height) {
            this.canvas.height = h;
        }
        return this;
    };

    /**
     * Expands dimensions of drawing context (canvas 'width' and 'height' attributes)
     * @param {Number} width   New width in current units
     * @param {Number} height  New height in current units
     */
    DrawingContext.prototype.expand = function (width, height) {
        var w = Asc.round( width  * getCvtRatio(this.units, 0/*px*/, this.ppiX) ),
            h = Asc.round( height * getCvtRatio(this.units, 0/*px*/, this.ppiY) );
        if (w > this.canvas.width) {
            this.canvas.width = w;
        }
        if (h > this.canvas.height) {
            this.canvas.height = h;
        }
        return this;
    };

    // Canvas methods

    DrawingContext.prototype.clear = function () {
        this.clearRect(0, 0, this.getWidth(), this.getHeight());
        return this;
    };
 
    DrawingContext.prototype.AddClipRect = function () {
 
        return this;
    };
 
    DrawingContext.prototype.RemoveClipRect = function (x, y, w, h) {
 
        return this;
    };

    DrawingContext.prototype.save = function () {
        this.nctx["PD_Save"]();
        return this;
    };

    DrawingContext.prototype.restore = function () {
        this.nctx["PD_Restore"]();
        return this;
    };

    DrawingContext.prototype.scale = function (kx, ky) {
        //TODO: implement scale()
        return this;
    };

    DrawingContext.prototype.rotate = function (a) {
        //TODO: implement rotate()
        return this;
    };

    DrawingContext.prototype.translate = function (dx, dy) {
        //TODO: implement translate()
        return this;
    };

    DrawingContext.prototype.transform = function (sx, shy, shx, sy, tx, ty) {
        //TODO: implement transform()
        return this;
    };

    DrawingContext.prototype.setTransform = function(sx, shy, shx, sy, tx, ty) {
        this._mbt.assign(sx, shx, shy, sy, tx, ty);
        return this;
    };

    DrawingContext.prototype.setTextTransform = function(sx, shy, shx, sy, tx, ty) {
        this._mt.assign(sx, shx, shy, sy, tx, ty);
        return this;
    };

    DrawingContext.prototype.updateTransforms = function() {
        this._calcMFT();

        //this.fmgrGraphics[1].SetTextMatrix(
        //    this._mt.sx, this._mt.shy, this._mt.shx, this._mt.sy, this._mt.tx, this._mt.ty);

        this.nctx["PD_transform"](this._mt.sx, this._mt.shy, this._mt.shx, this._mt.sy, this._mt.tx, this._mt.ty);
    };

    DrawingContext.prototype.resetTransforms = function(){
        this.setTransform(this._im.sx, this._im.shy, this._im.shx, this._im.sy, this._im.tx, this._im.ty);
        this.setTextTransform(this._im.sx, this._im.shy, this._im.shx, this._im.sy, this._im.tx, this._im.ty);
        this._calcMFT();
    };

    // Style methods

    DrawingContext.prototype.getFillStyle = function () {
        return this.ctx.fillStyle;
    };

    DrawingContext.prototype.getStrokeStyle = function () {
        return this.ctx.strokeStyle;
    };

    DrawingContext.prototype.getLineWidth = function () {
        return this.ctx.lineWidth;
    };

    DrawingContext.prototype.getLineCap = function () {
        return this.ctx.lineCap;
    };

    DrawingContext.prototype.getLineJoin = function () {
        return this.ctx.lineJoin;
    };

    /**
     * @param {AscCommonExcel.RgbColor || AscCommonExcel.ThemeColor || AscCommon.CColor} val
     * @returns {DrawingContext}
     */
    DrawingContext.prototype.setFillStyle = function (val) {
        var _r = val.getR();
        var _g = val.getG();
        var _b = val.getB();
        var _a = val.getA();
        //this.fillColor = new AscCommon.CColor(_r, _g, _b, _a);
        //this.ctx.fillStyle = "rgba(" + _r + "," + _g + "," + _b + "," + _a + ")";
        this.nctx["PD_b_color1"](_r,_g,_b,_a * 255);
        return this;
    };

    DrawingContext.prototype.setFillPattern = function (val) {
        this.ctx.fillStyle = val;
        return this;
    };

    /**
     * @param {AscCommonExcel.RgbColor || AscCommonExcel.ThemeColor || AscCommon.CColor} val
     * @returns {DrawingContext}
     */
    DrawingContext.prototype.setStrokeStyle = function (val) {
        var _r = val.getR();
        var _g = val.getG();
        var _b = val.getB();
        var _a = val.getA();
        this.nctx["PD_p_color"](_r,_g,_b,_a * 255);
        return this;
    };

    DrawingContext.prototype.setLineWidth = function (width) {
        this.nctx["PD_p_width"](width);
        return this;
    };

    DrawingContext.prototype.setLineCap = function (cap) {
        this.ctx.lineCap = cap;
        return this;
    };

    DrawingContext.prototype.setLineJoin = function (join) {
        this.ctx.lineJoin = join;
        return this;
    };
 
    DrawingContext.prototype.setLineDash = function (segments) {
        //TODO: 
        return this;
	};

    DrawingContext.prototype.fillRect = function (x, y, w, h) {
        var r = this._calcRect(x, y, w, h);
        this.nctx["PD_rect"](r.x, r.y, r.w, r.h);
        this.nctx["PD_Fill"]();
        return this;
    };

    DrawingContext.prototype.strokeRect = function (x, y, w, h) {
        var isEven = 0 !== this.ctx.lineWidth % 2 ? 0.5 : 0;
        var r = this._calcRect(x, y, w, h);
        this.nctx["PD_rect"](r.x + isEven, r.y + isEven, r.w, r.h);
        this.nctx["PD_Stroke"]();
        return this;
    };

    DrawingContext.prototype.clearRect = function (x, y, w, h) {
        var r = this._calcRect(x, y, w, h);
        this.ctx.clearRect(r.x, r.y, r.w, r.h);
        return this;
    };

    DrawingContext.prototype.clearRectByX = function (x, y, w, h) {
        var r = this._calcRect(x, y, w, h);
        this.ctx.clearRect(r.x - 1, r.y, r.w + 1, r.h);
    };
    DrawingContext.prototype.clearRectByY = function (x, y, w, h) {
        var r = this._calcRect(x, y, w, h);
        this.ctx.clearRect(r.x, r.y - 1, r.w, r.h + 1);
    };

    // Font and text methods

    DrawingContext.prototype.getFont = function () {
        return this.font.clone();
    };

    DrawingContext.prototype.getFontFamily = function () {
        return this.font.FontFamily.Name;
    };

    DrawingContext.prototype.getFontSize = function () {
        return this.font.FontSize;
    };

    /**
     * @param {Number} [units]  Units of result (0=px, 1=pt, 2=in, 3=mm)
     * @return {FontMetrics}
     */
    DrawingContext.prototype.getFontMetrics = function (units) {
        var fm = this.napi_fmt[3];
        var d  = Math.abs(fm.m_lDescender);
        var r  = getCvtRatio(0/*px*/, units >= 0 && units <=3 ? units : this.units, this.ppiX);
        var factor = this.getFontSize() * r / fm.m_lUnits_Per_Em;

        var res = new FontMetrics();
        res.ascender = factor * fm.m_lAscender;
        res.descender = factor * d;
        res.lineGap	= factor * (fm.m_lLineHeight - fm.m_lAscender - d);

        var face = g_oTextMeasurer.Measurer['GetFace']();
        res.nat_scale = face[0];
        res.nat_y1 = face[1];
        res.nat_y2 = face[2];

        return res;
    };

    /**
     *
     * @param font
     * @param [angle]
     * @returns {DrawingContext}
     */
    DrawingContext.prototype.setFont = function (font, angle) {

        var italic, bold, fontStyle, r;

        this.font.copyFrom(font);
        this.font.FontSize = this.font.FontSize * 2.54 * this.scaleFactor * 96.0 / 72.0;
        // this.font.FontSize = this.font.FontSize * 2.54 * this.scaleFactor * this.deviceDPI / 72.0;

        // this.font.FontSize = this.font.FontSize * 2.54 * this.scaleFactor *
        //     this.deviceScale * this.deviceDPI / 96.0 * (96.0 / (this.deviceDPI * this.deviceScale));

        italic = true === font.Italic;
        bold   = true === font.Bold;

        fontStyle = AscFonts.FontStyle.FontStyleRegular;
        if ( !italic && bold )
            fontStyle = AscFonts.FontStyle.FontStyleBold;
        else if ( italic && !bold )
            fontStyle = AscFonts.FontStyle.FontStyleItalic;
        else if ( italic && bold )
            fontStyle = AscFonts.FontStyle.FontStyleBoldItalic;

        var _fontinfo, _info, flag, napi_fontInfo;

        if (angle && 0 != angle) {
            _fontinfo = AscFonts.g_fontApplication.GetFontInfo(this.font.FontFamily.Name, fontStyle, this.LastFontOriginInfo);
            _info = GetLoadInfoForMeasurer(_fontinfo, fontStyle);

            flag = 0;
            if (_info.NeedBold)     flag |= 0x01;
            if (_info.NeedItalic)   flag |= 0x02;
            if (_info.SrcBold)      flag |= 0x04;
            if (_info.SrcItalic)    flag |= 0x08;

            napi_fontInfo = g_oTextMeasurer.Measurer["LoadFont"](_info.Path, _info.FaceIndex, this.font.FontSize, flag);

            this.napi_fmt[1].m_lUnits_Per_Em    = napi_fontInfo[3];
            this.napi_fmt[1].m_lAscender        = napi_fontInfo[0];
            this.napi_fmt[1].m_lDescender       = napi_fontInfo[2];
            this.napi_fmt[1].m_lLineHeight      = napi_fontInfo[2];

            r = true;

            //this.fmgrGraphics[1].SetTextMatrix(
            //    this._mt.sx, this._mt.shy, this._mt.shx, this._mt.sy, this._mt.tx, this._mt.ty);

            this.nctx["PD_transform"](this._mt.sx, this._mt.shy, this._mt.shx, this._mt.sy, this._mt.tx, this._mt.ty);

        } else {

            _fontinfo = AscFonts.g_fontApplication.GetFontInfo(this.font.FontFamily.Name, fontStyle, this.LastFontOriginInfo);
            _info = GetLoadInfoForMeasurer(_fontinfo, fontStyle);

            flag = 0;
            if (_info.NeedBold)     flag |= 0x01;
            if (_info.NeedItalic)   flag |= 0x02;
            if (_info.SrcBold)      flag |= 0x04;
            if (_info.SrcItalic)    flag |= 0x08;

            napi_fontInfo = g_oTextMeasurer.Measurer["LoadFont"](_info.Path, _info.FaceIndex, this.font.FontSize, flag);

            this.nctx["PD_LoadFont"](_info.Path, _info.FaceIndex, this.font.FontSize, flag);

            this.napi_fmt[0].m_lUnits_Per_Em  = napi_fontInfo[3];
            this.napi_fmt[0].m_lAscender      = napi_fontInfo[0];
            this.napi_fmt[0].m_lDescender     = napi_fontInfo[2];
            this.napi_fmt[0].m_lLineHeight    = napi_fontInfo[2];

            this.napi_fmt[3].m_lUnits_Per_Em  = napi_fontInfo[3];
            this.napi_fmt[3].m_lAscender      = napi_fontInfo[0];
            this.napi_fmt[3].m_lDescender     = napi_fontInfo[2];
            this.napi_fmt[3].m_lLineHeight    = napi_fontInfo[2];

            //var dKoef = g_dKoef_pt_to_mm * font.FontSize / napi_fontInfo[3];
            //
            //this.napi_fmt[0].m_lUnits_Per_Em    = napi_fontInfo[3];
            //this.napi_fmt[0].m_lAscender        = napi_fontInfo[0];// * dKoef;
            //this.napi_fmt[0].m_lDescender       = napi_fontInfo[2];// * dKoef;
            //this.napi_fmt[0].m_lLineHeight      = napi_fontInfo[2];// * dKoef;
            //
            //this.napi_fmt[3].m_lUnits_Per_Em    = napi_fontInfo[3];
            //this.napi_fmt[3].m_lAscender        = napi_fontInfo[0];// * dKoef;
            //this.napi_fmt[3].m_lDescender       = napi_fontInfo[2];// * dKoef;
            //this.napi_fmt[3].m_lLineHeight      = napi_fontInfo[2];// * dKoef;

            r = true;

            //===================================================================

        }

        if (r === false) {
            throw "Can not use " + font.FontFamily.Name + " font. (Check whether font file is loaded)";
        }

        return this;
    };

    /**
     * Returns dimensions of first char of string
     * @param {String} text   Character to measure
     * @param {Number} units  Units (0 = px, 1 = pt, 2 = in, 3 = mm)
     * @return {TextMetrics}  Returns the char dimension
     */
    DrawingContext.prototype.measureChar = function (text, units) {
        return this.measureText(text.charAt(0), units);
    };

    /**
     * Returns dimensions of string
     * @param {String} text   String to measure
     * @param {Number} units  Units (0 = px, 1 = pt, 2 = in, 3 = mm)
     * @return {TextMetrics}  Returns the dimension of string {width: w, height: h}
     */
    DrawingContext.prototype.measureText = function (text, units) {
        var fm = this.napi_fmt[3],  //this.fmgrGraphics[3],
            r  = getCvtRatio(0/*px*/, units >= 0 && units <=3 ? units : this.units, this.ppiX);
        for (var tmp, w = 0, w2 = 0, i = 0; i < text.length; ++i) {

            var bounds = g_oTextMeasurer.Measurer["GetDrawingBox"](text.charCodeAt(i));
            tmp = {
                fAdvanceX: bounds[0],
                oBBox: {
                    fMinX:  bounds[1],
                    fMaxX:  bounds[2],
                    fMinY:  bounds[3],
                    fMaxY:  bounds[4]
                }
            };

            w += Asc.round(tmp.fAdvanceX); // asc_round - убрали что бы текст не скакал
        }
        w2 = w - tmp.fAdvanceX + tmp.oBBox.fMaxX - tmp.oBBox.fMinX + 1;
        return this._calcTextMetrics(w * r, w2 * r, fm, r);
    };

    DrawingContext.prototype.fillGlyph = function (pGlyph, fmgr) {
        var nW = pGlyph.oBitmap.nWidth;
        var nH = pGlyph.oBitmap.nHeight;

        if ( !(nW > 0 && nH > 0) ) {return;}

        var nX = Asc.floor(fmgr.m_oGlyphString.m_fX + pGlyph.fX + pGlyph.oBitmap.nX);
        var nY = Asc.floor(fmgr.m_oGlyphString.m_fY + pGlyph.fY - pGlyph.oBitmap.nY);

        var _r = this.fillColor.r;
        var _g = this.fillColor.g;
        var _b = this.fillColor.b;

		pGlyph.oBitmap.oGlyphData.checkColor(_r, _g, _b, nW, nH);
		pGlyph.oBitmap.draw(this.ctx, nX, nY);
    };

    DrawingContext.prototype.fillText = function (text, x, y, maxWidth, charWidths, angle) {

        //var manager = angle ? this.fmgrGraphics[1] : this.fmgrGraphics[0];

        var _x = this._mift.transformPointX(x, y);
        var _y = this._mift.transformPointY(x, y);

        var length = text.length, lUnicode;
        for (var i = 0; i < length; ++i) {

            lUnicode = text.charCodeAt(i);

            //TODO: cache
            // if (null != this.LastFontOriginInfo.Replace)
            //   lUnicode = g_fontApplication.GetReplaceGlyph(lUnicode, this.LastFontOriginInfo.Replace);

            this.nctx["PD_FillText"](_x, _y, lUnicode);

            _x += Asc.round(g_oTextMeasurer.Measurer["MeasureChar"](lUnicode));
        }

        return this;
    };

    // Path methods

    DrawingContext.prototype.beginPath = function () {
        this.nctx["PD_PathStart"]();
        return this;
    };

    DrawingContext.prototype.closePath = function () {
        this.nctx["PD_PathClose"]();
        return this;
    };

    DrawingContext.prototype.moveTo = function (x, y) {
        var r = this._calcRect(x, y);
        this.nctx["PD_PathMoveTo"](r.x, r.y);
        return this;
    };

    DrawingContext.prototype.lineTo = function (x, y) {
        var r = this._calcRect(x, y);
        this.nctx["PD_PathLineTo"](r.x, r.y);
        return this;
    };

    DrawingContext.prototype.lineDiag = function (x1, y1, x2, y2) {
        var isEven = 0 !== this.ctx.lineWidth % 2 ? 0.5 : 0;
        var r1 = this._calcRect(x1, y1);
        var r2 = this._calcRect(x2, y2);
        this.nctx["PD_PathMoveTo"](r1.x + isEven, r1.y + isEven);
        this.nctx["PD_PathLineTo"](r2.x + isEven, r2.y + isEven);
        return this;
    };
    DrawingContext.prototype.lineHor = function (x1, y, x2) {
        var isEven = 0 !== this.ctx.lineWidth % 2 ? 0.5 : 0;
        var r1 = this._calcRect(x1, y);
        var r2 = this._calcRect(x2, y);
        this.nctx["PD_PathMoveTo"](r1.x, r1.y + isEven);
        this.nctx["PD_PathLineTo"](r2.x, r2.y + isEven);
        return this;
    };
    DrawingContext.prototype.lineVer = function (x, y1, y2) {
        var isEven = 0 !== this.ctx.lineWidth % 2 ? 0.5 : 0;
        var r1 = this._calcRect(x, y1);
        var r2 = this._calcRect(x, y2);
        this.nctx["PD_PathMoveTo"](r1.x + isEven, r1.y);
        this.nctx["PD_PathLineTo"](r2.x + isEven, r2.y);
        return this;
    };

    // Отрисовка на 1px меньше
    DrawingContext.prototype.lineHorPrevPx = function (x1, y, x2) {
        var isEven = (0 !== this.ctx.lineWidth % 2 ? 0.5 : 0) - 1;
        var r1 = this._calcRect(x1, y);
        var r2 = this._calcRect(x2, y);
        this.nctx["PD_PathMoveTo"](r1.x, r1.y + isEven);
        this.nctx["PD_PathLineTo"](r2.x, r2.y + isEven);
        return this;
    };
    DrawingContext.prototype.lineVerPrevPx = function (x, y1, y2) {
        var isEven = (0 !== this.ctx.lineWidth % 2 ? 0.5 : 0) - 1;
        var r1 = this._calcRect(x, y1);
        var r2 = this._calcRect(x, y2);
        this.nctx["PD_PathMoveTo"](r1.x + isEven, r1.y);
        this.nctx["PD_PathLineTo"](r2.x + isEven, r2.y);
        return this;
    };

    DrawingContext.prototype.dashLineCleverHor = function (x1, y, x2) {
        var w_dot = AscCommonExcel.c_oAscCoAuthoringDottedWidth, w_dist = AscCommonExcel.c_oAscCoAuthoringDottedDistance;
        var _x1 = this._mct.transformPointX(x1, y);
        var _y  = this._mct.transformPointY(x1, y) - 1;
        var _x2 = this._mct.transformPointX(x2, y);
        var ctx = this.ctx;

        _x1 = (_x1 >> 0) + 0.5;
        _y  = (_y  >> 0) + 0.5;
        _x2 = (_x2 >> 0) + 0.5;

        for (; _x1 < _x2; _x1 += w_dist) {
            this.nctx["PD_PathMoveTo"](_x1, _y);
            _x1 += w_dot;

            if (_x1 > _x2)
                _x1 = _x2;

            this.nctx["PD_PathLineTo"](_x1, _y);
        }
    };
    DrawingContext.prototype.dashLineCleverVer = function (x, y1, y2) {
        var w_dot = AscCommonExcel.c_oAscCoAuthoringDottedWidth, w_dist = AscCommonExcel.c_oAscCoAuthoringDottedDistance;
        var _y1 = this._mct.transformPointY(x, y1);
        var _x  = this._mct.transformPointX(x, y1) - 1;
        var _y2 = this._mct.transformPointY(x, y2);
        var ctx = this.ctx;

        _y1 = (_y1 >> 0) + 0.5;
        _x  = (_x  >> 0) + 0.5;
        _y2 = (_y2 >> 0) + 0.5;

        for (; _y1 < _y2; _y1 += w_dist) {
            this.nctx["PD_PathMoveTo"](_x, _y1);
            _y1 += w_dot;

            if (_y1 > _y2)
                _y1 = _y2;

            this.nctx["PD_PathLineTo"](_x, _y1);
        }
    };

    DrawingContext.prototype.dashLine = function (x1, y1, x2, y2, w_dot, w_dist) {
        var len = Math.sqrt ((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1));
        if (len < 1)
            len = 1;

        var len_x1 = Math.abs(w_dot *(x2 - x1)/len);
        var len_y1 = Math.abs(w_dot *(y2 - y1)/len);
        var len_x2 = Math.abs(w_dist*(x2 - x1)/len);
        var len_y2 = Math.abs(w_dist*(y2 - y1)/len);
        var i, j;

        if (x1 <= x2 && y1 <= y2) {
            for (i = x1, j = y1; i < x2 || j < y2; i += len_x2, j += len_y2) {
                this.nctx["PD_PathMoveTo"](i, j);

                i += len_x1;
                j += len_y1;

                if (i > x2)
                    i = x2;
                if (j > y2)
                    j = y2;

                this.nctx["PD_PathLineTo"](i, j);
            }
        } else if (x1 <= x2 && y1 > y2) {
            for (i = x1, j = y1; i < x2 || j > y2; i += len_x2, j -= len_y2) {
                this.nctx["PD_PathMoveTo"](i, j);

                i += len_x1;
                j -= len_y1;

                if (i > x2)
                    i = x2;
                if (j < y2)
                    j = y2;

                this.nctx["PD_PathLineTo"](i, j);
            }
        } else if (x1 > x2 && y1 <= y2) {
            for (i = x1, j = y1; i > x2 || j < y2; i -= len_x2, j += len_y2) {
                this.nctx["PD_PathMoveTo"](i, j);

                i -= len_x1;
                j += len_y1;

                if (i < x2)
                    i = x2;
                if (j > y2)
                    j = y2;

                this.nctx["PD_PathLineTo"](i, j);
            }
        } else {
            for (i = x1, j = y1; i > x2 || j > y2; i -= len_x2, j -= len_y2) {
                this.nctx["PD_PathMoveTo"](i, j);

                i -= len_x1;
                j -= len_y1;

                if (i < x2)
                    i = x2;
                if (j < y2)
                    j = y2;

                this.nctx["PD_PathLineTo"](i, j);
            }
        }
    };

    DrawingContext.prototype.dashRect = function (x1, y1, x2, y2, x3, y3, x4, y4, w_dot, w_dist) {
        this.dashLine(x1, y1, x2, y2, w_dot, w_dist);
        this.dashLine(x2, y2, x4, y4, w_dot, w_dist);
        this.dashLine(x4, y4, x3, y3, w_dot, w_dist);
        this.dashLine(x3, y3, x1, y1, w_dot, w_dist);
    };

    DrawingContext.prototype.rect = function (x, y, w, h) {
        var r = this._calcRect(x, y, w, h);
        this.nctx["PD_rect"](r.x, r.y, r.w, r.h);
        return this;
    };

    DrawingContext.prototype.arc = function (x, y, radius, startAngle, endAngle, antiClockwise, dx, dy) {
        var r = this._calcRect(x, y);
        dx = typeof dx !== "undefined" ? dx : 0;
        dy = typeof dy !== "undefined" ? dy : 0;
        this.ctx.arc(r.x + dx, r.y + dy, radius, startAngle, endAngle, antiClockwise);
        return this;
    };

    DrawingContext.prototype.bezierCurveTo = function (x1, y1, x2, y2, x3, y3) {
        var p1 = this._calcRect(x1, y1),
            p2 = this._calcRect(x2, y2),
            p3 = this._calcRect(x3, y3);
        this.nctx["PD_PathCurveTo"](p1.x, p1.y, p2.x, p2.y, p3.x, p3.y);
        //this.ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y);
        return this;
    };

    DrawingContext.prototype.fill = function () {
        this.nctx["PD_Fill"]();
        return this;
    };

    DrawingContext.prototype.stroke = function () {
        this.nctx["PD_Stroke"]();
        return this;
    };

    DrawingContext.prototype.clip = function () {
        this.nctx["PD_clip"]();
        return this;
    };

    // Image methods
    DrawingContext.prototype.drawImage = function (img, sx, sy, sw, sh, dx, dy, dw, dh) {
        var sr = this._calcRect(sx, sy, sw, sh),
            dr = this._calcRect(dx, dy, dw, dh);
        this.ctx.drawImage(img, sr.x, sr.y, sr.w, sr.h, dr.x, dr.y, dr.w, dr.h);
        return this;
    };

    // Private methods

    DrawingContext.prototype._calcRect = function (x, y, w, h) {
        var wh = w !== undefined && h !== undefined,
            x2 = x + w,
            y2 = y + h,
            _x = this._mft.transformPointX(x, y),
            _y = this._mft.transformPointY(x, y);
        return {
            x: Asc.round(_x),
            y: Asc.round(_y),
            w: wh ? Asc.round(this._mft.transformPointX(x2, y2) - _x) : undefined,
            h: wh ? Asc.round(this._mft.transformPointY(x2, y2) - _y) : undefined
        };
    };

    DrawingContext.prototype._calcMFT = function () {
        this._mft = this._mct.clone();
        this._mft.multiply(this._mbt, AscCommon.MATRIX_ORDER_PREPEND);
        this._mft.multiply(this._mt, AscCommon.MATRIX_ORDER_PREPEND);

        this._mift = this._mt.clone();
        this._mift.invert();
        this._mift.multiply(this._mft, AscCommon.MATRIX_ORDER_PREPEND);
    };

    /**
     * @param {Number} w         Ширина текста
     * @param {Number} wBB       Ширина Bound Box текста
     * @param {AscFonts.CFontManager} fm  Объект AscFonts.CFontManager для получения метрик шрифта
     * @param {Number} r         Коэффициент перевода pt -> в текущие единицы измерения (this.units)
     * @return {TextMetrics}
     */
    DrawingContext.prototype._calcTextMetrics = function (w, wBB, fm, r) {
        var factor = this.getFontSize() * r / fm.m_lUnits_Per_Em,
            l = fm.m_lLineHeight * factor,
            b = fm.m_lAscender * factor,
            d = Math.abs(fm.m_lDescender * factor);
        return new TextMetrics(w, b + d, l, b, d, this.font.FontSize, 0, wBB);
    };


    /*
     * Export
     * -----------------------------------------------------------------------------
     */

    window["Asc"].getCvtRatio      = getCvtRatio;
    window["Asc"].calcNearestPt    = calcNearestPt;
    window["Asc"].colorObjToAscColor = colorObjToAscColor;

    window["Asc"].FontProperties   = FontProperties;
    window["Asc"].TextMetrics      = TextMetrics;
    window["Asc"].FontMetrics      = FontMetrics;
    window["Asc"].DrawingContext   = DrawingContext;
    window["Asc"].Matrix           = Matrix;

})(window);
