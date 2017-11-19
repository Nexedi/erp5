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

var editor = undefined;
var window = {};
var navigator = {};
navigator.userAgent = "chrome";
window.navigator = navigator;
window.location = {};

window.location.protocol = "";
window.location.host = "";
window.location.href = "";
window.location.pathname = "";

window.XMLHttpRequest = function () {};

window.NATIVE_EDITOR_ENJINE = true;
window.NATIVE_EDITOR_ENJINE_SYNC_RECALC = true;
window.IS_NATIVE_EDITOR = true;

var document = {};
window.document = document;

window["Asc"] = {};
var Asc = window["Asc"];

window["AscFonts"] = {};
var AscFonts = window["AscFonts"];

window["AscCommon"] = {};
var AscCommon = window["AscCommon"];

window["AscFormat"] = {};
var AscFormat = window["AscFormat"];

window["AscDFH"] = {};
var AscDFH = window["AscDFH"];

window["AscCH"] = {};
var AscCH = window["AscCH"];

window["AscCommonExcel"] = {};
var AscCommonExcel = window["AscCommonExcel"];

window["AscCommonWord"] = {};
var AscCommonWord = window["AscCommonWord"];

window["AscCommonSlide"] = {};
var AscCommonSlide = window["AscCommonSlide"];

function ConvertJSC_Array(_array)
{
	var _len = _array.length;
	var ret = new Uint8Array(_len);
	for (var i = 0; i < _len; i++)
		ret[i] = _array.getAt(i);
	return ret;
}

function Image() {
    this.src = "";
    this.onload = function()
    {
    }
    this.onerror = function()
    {
    }
}
function _image_data() {
    this.data = null;
    this.length = 0;
}

function native_pattern_fill() {
}
native_pattern_fill.prototype = {
    setTransform : function(transform) {}
};

function native_gradient_fill() {
}
native_gradient_fill.prototype = {
    addColorStop : function(offset,color) {}
};

function native_context2d(parent) {
    this.canvas = parent;

    this.globalAlpha = 0;
    this.globalCompositeOperation = "";
    this.fillStyle = "";
    this.strokeStyle = "";

    this.lineWidth = 0;
    this.lineCap = 0;
    this.lineJoin = 0;
    this.miterLimit = 0;
    this.shadowOffsetX = 0;
    this.shadowOffsetY = 0;
    this.shadowBlur = 0;
    this.shadowColor = 0;
    this.font = "";
    this.textAlign = 0;
    this.textBaseline = 0;
}
native_context2d.prototype = {
    save : function() {},
    restore : function() {},

    scale : function(x,y) {},
    rotate : function(angle) {},
    translate : function(x,y) {},
    transform : function(m11,m12,m21,m22,dx,dy) {},
    setTransform : function(m11,m12,m21,m22,dx,dy) {},

    createLinearGradient : function(x0,y0,x1,y1) { return new native_gradient_fill(); },
    createRadialGradient : function(x0,y0,r0,x1,y1,r1) { return null; },
    createPattern : function(image,repetition) { return new native_pattern_fill(); },

    clearRect : function(x,y,w,h) {},
    fillRect : function(x,y,w,h) {},
    strokeRect : function(x,y,w,h) {},

    beginPath : function() {},
    closePath : function() {},
    moveTo : function(x,y) {},
    lineTo : function(x,y) {},
    quadraticCurveTo : function(cpx,cpy,x,y) {},
    bezierCurveTo : function(cp1x,cp1y,cp2x,cp2y,x,y) {},
    arcTo : function(x1,y1,x2,y2,radius) {},
    rect : function(x,y,w,h) {},
    arc : function(x,y,radius,startAngle,endAngle,anticlockwise) {},

    fill : function() {},
    stroke : function() {},
    clip : function() {},
    isPointInPath : function(x,y) {},
    drawFocusRing : function(element,xCaret,yCaret,canDrawCustom) {},

    fillText : function(text,x,y,maxWidth) {},
    strokeText : function(text,x,y,maxWidth) {},
    measureText : function(text) {},

    drawImage : function(img_elem,dx_or_sx,dy_or_sy,dw_or_sw,dh_or_sh,dx,dy,dw,dh) {},

    createImageData : function(imagedata_or_sw,sh)
    {
        var _data = new _image_data();
        _data.length = imagedata_or_sw * sh * 4;
        _data.data = (typeof(Uint8Array) != 'undefined') ? new Uint8Array(_data.length) : new Array(_data.length);
        return _data;
    },
    getImageData : function(sx,sy,sw,sh) {},
    putImageData : function(image_data,dx,dy,dirtyX,dirtyY,dirtyWidth,dirtyHeight) {}
};

function native_canvas()
{
    this.id = "";
    this.width = 300;
    this.height = 150;

    this.nodeType = 1;
}
native_canvas.prototype =
{
    getContext : function(type)
    {
        if (type == "2d")
            return new native_context2d(this);
        return null;
    },

    toDataUrl : function(type)
    {
        return "";
    },

    addEventListener : function()
    {
    },

    attr : function()
    {
    }
};

var _null_object = {};
_null_object.length = 0;
_null_object.nodeType = 1;
_null_object.offsetWidth = 1;
_null_object.offsetHeight = 1;
_null_object.clientWidth = 1;
_null_object.clientHeight = 1;
_null_object.scrollWidth = 1;
_null_object.scrollHeight = 1;
_null_object.style = {};
_null_object.documentElement = _null_object;
_null_object.body = _null_object;
_null_object.ownerDocument = _null_object;
_null_object.defaultView = _null_object;

_null_object.addEventListener = function(){};
_null_object.setAttribute = function(){};
_null_object.getElementsByTagName = function() { return []; };
_null_object.appendChild = function() {};
_null_object.removeChild = function() {};
_null_object.insertBefore = function() {};
_null_object.childNodes = [];
_null_object.parent = _null_object;
_null_object.parentNode = _null_object;
_null_object.find = function() { return this; };
_null_object.appendTo = function() { return this; };
_null_object.css = function() { return this; };
_null_object.width = function() { return 1; };
_null_object.height = function() { return 1; };
_null_object.attr = function() { return this; };
_null_object.prop = function() { return this; };
_null_object.val = function() { return this; };
_null_object.remove = function() {};
_null_object.getComputedStyle = function() { return null; };
_null_object.getContext = function(type) {
    if (type == "2d")
        return new native_context2d(this);
    return null;
};

window._null_object = _null_object;

document.createElement = function(type) {
    if (type && type.toLowerCase)
    {
        if (type.toLowerCase() == "canvas")
            return new native_canvas();
    }

    return _null_object;
};

function _return_empty_html_element() { return _null_object; }

document.createDocumentFragment = _return_empty_html_element;
document.getElementsByTagName = function(tag) {
    var ret = [];
    if ("head" == tag)
        ret.push(_null_object);
    return ret;
};
document.insertBefore = function() {};
document.appendChild = function() {};
document.removeChild = function() {};
document.getElementById = function() { return _null_object; };
document.createComment = function() { return undefined; };

document.documentElement = _null_object;
document.body = _null_object;

var native = CreateNativeEngine();
window.native = native;
window["native"] = native;

var _api = null;

window.NativeSupportTimeouts = true;
window.NativeTimeoutObject = {};

function setTimeout(func, interval) {
    if (!window.NativeSupportTimeouts)
        return;

    var id = window["native"]["GenerateTimeoutId"](interval);
    window.NativeTimeoutObject["" + id] = {"func": func, repeat: false};

    return id;
}

function clearTimeout(id) {
    if (!window.NativeSupportTimeouts)
        return;

    window.NativeTimeoutObject["" + id] = undefined;
    window["native"]["ClearTimeout"](id);
}

function setInterval(func, interval) {
    if (!window.NativeSupportTimeouts)
        return;

    var id = window["native"]["GenerateTimeoutId"](interval);
    window.NativeTimeoutObject["" + id] = {func: func, repeat: true, interval: interval};

    return id;
}
function clearInterval(id) {
    if (!window.NativeSupportTimeouts)
        return;

    window.NativeTimeoutObject["" + id] = undefined;
    window["native"]["ClearTimeout"](id);
}

function offline_timeoutFire(id) {
    if (!window.NativeSupportTimeouts)
        return;

    var prop = "" + id;

    if (undefined === window.NativeTimeoutObject[prop]) {
        return;
    }

    var func = window.NativeTimeoutObject[prop].func;
    var repeat = window.NativeTimeoutObject[prop].repeat;
    var interval = window.NativeTimeoutObject[prop].interval;

    window.NativeTimeoutObject[prop] = undefined;

    if (!func)
        return;

    func.call(null);

    if (repeat) {
        setInterval(func, interval);
    }

    func = null;
}

window.clearTimeout = clearTimeout;
window.setTimeout = setTimeout;
window.clearInterval = clearInterval;
window.setInterval = setInterval;

var console = {
    log : function(param) { window["native"]["consoleLog"](param); },
    time : function (param) {},
    timeEnd : function (param) {}
};

window["NativeCorrectImageUrlOnPaste"] = function(url) {
    return window["native"]["CorrectImageUrlOnPaste"](url);
};
window["NativeCorrectImageUrlOnCopy"] = function(url) {
    return window["native"]["CorrectImageUrlOnCopy"](url);
};

var global_memory_stream_menu = CreateNativeMemoryStream();

window['SockJS'] = createSockJS();
