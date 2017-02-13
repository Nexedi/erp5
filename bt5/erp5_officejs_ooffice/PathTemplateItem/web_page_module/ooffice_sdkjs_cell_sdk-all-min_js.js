/*
 Copyright (c) Ascensio System SIA 2012-2016. All rights reserved

 http://www.onlyoffice.com

 Version: undefined (build:undefined)
*/
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
var AscBrowser = {
    userAgent : "",
    isIE : false,
    isMacOs : false,
    isSafariMacOs : false,
    isAppleDevices : false,
    isAndroid : false,
    isMobile : false,
	isMobileVersion : false,
    isGecko : false,
    isChrome : false,
    isOpera : false,
    isWebkit : false,
    isSafari : false,
    isArm : false,
    isMozilla : false,
	isRetina : false
};

// user agent lower case
AscBrowser.userAgent = navigator.userAgent.toLowerCase();

// ie detect
AscBrowser.isIE =  (AscBrowser.userAgent.indexOf("msie") > -1 ||
                    AscBrowser.userAgent.indexOf("trident") > -1 ||
					AscBrowser.userAgent.indexOf("edge") > -1);

AscBrowser.isIE9 =  (AscBrowser.userAgent.indexOf("msie9") > -1 || AscBrowser.userAgent.indexOf("msie 9") > -1);
AscBrowser.isIE10 =  (AscBrowser.userAgent.indexOf("msie10") > -1 || AscBrowser.userAgent.indexOf("msie 10") > -1);

// macOs detect
AscBrowser.isMacOs = (AscBrowser.userAgent.indexOf('mac') > -1);

// chrome detect
AscBrowser.isChrome = !AscBrowser.isIE && (AscBrowser.userAgent.indexOf("chrome") > -1);

// safari detect
AscBrowser.isSafari = !AscBrowser.isIE && !AscBrowser.isChrome && (AscBrowser.userAgent.indexOf("safari") > -1);

// macOs safari detect
AscBrowser.isSafariMacOs = (AscBrowser.isSafari && AscBrowser.isMacOs);

// apple devices detect
AscBrowser.isAppleDevices = (AscBrowser.userAgent.indexOf("ipad") > -1 ||
                             AscBrowser.userAgent.indexOf("iphone") > -1 ||
                             AscBrowser.userAgent.indexOf("ipod") > -1);

// android devices detect
AscBrowser.isAndroid = (AscBrowser.userAgent.indexOf("android") > -1);

// mobile detect
AscBrowser.isMobile = /android|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od|ad)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent || navigator.vendor || window.opera);

// gecko detect
AscBrowser.isGecko = (AscBrowser.userAgent.indexOf("gecko/") > -1);

// opera detect
AscBrowser.isOpera = (!!window.opera || AscBrowser.userAgent.indexOf("opr/") > -1);

// webkit detect
AscBrowser.isWebkit = !AscBrowser.isIE && (AscBrowser.userAgent.indexOf("webkit") > -1);

// arm detect
AscBrowser.isArm = (AscBrowser.userAgent.indexOf("arm") > -1);

AscBrowser.isMozilla = !AscBrowser.isIE && (AscBrowser.userAgent.indexOf("firefox") > -1);

AscBrowser.isLinuxOS = (AscBrowser.userAgent.indexOf(" linux ") > -1);

AscBrowser.zoom = 1;

AscBrowser.checkZoom = function()
{
    if (AscBrowser.isChrome && !AscBrowser.isOpera && document && document.firstElementChild && document.body)
    {
        document.firstElementChild.style.zoom = "reset";
        AscBrowser.zoom = document.body.clientWidth / window.innerWidth;
		
		AscBrowser.isRetina = (Math.abs(2 - (window.devicePixelRatio / AscBrowser.zoom)) < 0.01);
    }
};

AscBrowser.checkZoom();
// detect retina (http://habrahabr.ru/post/159419/)
AscBrowser.isRetina = (Math.abs(2 - (window.devicePixelRatio / AscBrowser.zoom)) < 0.01);

    //--------------------------------------------------------export----------------------------------------------------
    window['AscCommon'] = window['AscCommon'] || {};
    window['AscCommon'].AscBrowser = AscBrowser; // ToDo убрать window['AscBrowser']
})(window);

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

(/**
 * @param {Window} window
 * @param {undefined} undefined
 */
	function(window, undefined)
{
	var g_cCharDelimiter      = String.fromCharCode(5);
	var FONT_THUMBNAIL_HEIGHT = (7 * 96.0 / 25.4) >> 0;
	var c_oAscMaxColumnWidth  = 255;
	var c_oAscMaxRowHeight    = 409;

	//files type for Saving & DownloadAs
	var c_oAscFileType = {
		UNKNOWN : 0,
		PDF     : 0x0201,
		HTML    : 0x0803,

		// Word
		DOCX : 0x0041,
		DOC  : 0x0042,
		ODT  : 0x0043,
		RTF  : 0x0044,
		TXT  : 0x0045,
		MHT  : 0x0047,
		EPUB : 0x0048,
		FB2  : 0x0049,
		MOBI : 0x004a,
		DOCY : 0x1001,
		JSON : 0x0808,	// Для mail-merge

		// Excel
		XLSX : 0x0101,
		XLS  : 0x0102,
		ODS  : 0x0103,
		CSV  : 0x0104,
		XLSY : 0x1002,

		// PowerPoint
		PPTX : 0x0081,
		PPT  : 0x0082,
		ODP  : 0x0083
	};

	var c_oAscError = {
		Level : {
			Critical   : -1,
			NoCritical : 0
		},
		ID    : {
			ServerSaveComplete   : 3,
			ConvertationProgress : 2,
			DownloadProgress     : 1,
			No                   : 0,
			Unknown              : -1,
			ConvertationTimeout  : -2,
			ConvertationError    : -3,
			DownloadError        : -4,
			UnexpectedGuid       : -5,
			Database             : -6,
			FileRequest          : -7,
			FileVKey             : -8,
			UplImageSize         : -9,
			UplImageExt          : -10,
			UplImageFileCount    : -11,
			NoSupportClipdoard   : -12,
			UplImageUrl          : -13,

			StockChartError       : -17,
			CoAuthoringDisconnect : -18,
			ConvertationPassword  : -19,
			VKeyEncrypt           : -20,
			KeyExpire             : -21,
			UserCountExceed       : -22,

			SplitCellMaxRows     : -30,
			SplitCellMaxCols     : -31,
			SplitCellRowsDivider : -32,

			MobileUnexpectedCharCount : -35,

			// Mail Merge
			MailMergeLoadFile : -40,
			MailMergeSaveFile : -41,

			// for AutoFilter
			AutoFilterDataRangeError         : -50,
			AutoFilterChangeFormatTableError : -51,
			AutoFilterChangeError            : -52,
			AutoFilterMoveToHiddenRangeError : -53,
			LockedAllError                   : -54,
			LockedWorksheetRename            : -55,
			FTChangeTableRangeError          : -56,
			FTRangeIncludedOtherTables       : -57,

			PasteMaxRangeError   : -64,
			PastInMergeAreaError : -65,

			DataRangeError  : -72,
			CannotMoveRange : -71,

			MaxDataSeriesError : -80,
			CannotFillRange    : -81,

			UserDrop : -100,
			Warning  : -101,

			/* для формул */
			FrmlWrongCountParentheses   : -300,
			FrmlWrongOperator           : -301,
			FrmlWrongMaxArgument        : -302,
			FrmlWrongCountArgument      : -303,
			FrmlWrongFunctionName       : -304,
			FrmlAnotherParsingError     : -305,
			FrmlWrongArgumentRange      : -306,
			FrmlOperandExpected         : -307,
			FrmlParenthesesCorrectCount : -308,
			FrmlWrongReferences         : -309,

			InvalidReferenceOrName : -310,
			LockCreateDefName      : -311,

			OpenWarning : 500
		}
	};

	var c_oAscAsyncAction = {
		Open               : 0,  // открытие документа
		Save               : 1,  // сохранение
		LoadDocumentFonts  : 2,  // загружаем фонты документа (сразу после открытия)
		LoadDocumentImages : 3,  // загружаем картинки документа (сразу после загрузки шрифтов)
		LoadFont           : 4,  // подгрузка нужного шрифта
		LoadImage          : 5,  // подгрузка картинки
		DownloadAs         : 6,  // cкачать
		Print              : 7,  // конвертация в PDF и сохранение у пользователя
		UploadImage        : 8,  // загрузка картинки

		ApplyChanges : 9,  // применение изменений от другого пользователя.

		SlowOperation     : 11, // медленная операция
		LoadTheme         : 12, // загрузка темы
		MailMergeLoadFile : 13, // загрузка файла для mail merge
		DownloadMerge     : 14, // cкачать файл с mail merge
		SendMailMerge     : 15  // рассылка mail merge по почте
	};

	var c_oAscAdvancedOptionsID = {
		CSV : 0,
		TXT : 1
	};

	var c_oAscAdvancedOptionsAction = {
		None : 0,
		Open : 1,
		Save : 2
	};

	// Режимы отрисовки
	var c_oAscFontRenderingModeType = {
		noHinting             : 1,
		hinting               : 2,
		hintingAndSubpixeling : 3
	};

	var c_oAscAsyncActionType = {
		Information      : 0,
		BlockInteraction : 1
	};

	var DownloadType = {
		None      : '',
		Download  : 'asc_onDownloadUrl',
		Print     : 'asc_onPrintUrl',
		MailMerge : 'asc_onSaveMailMerge'
	};

	var CellValueType = {
		Number : 0,
		String : 1,
		Bool   : 2,
		Error  : 3
	};

	//NumFormat defines
	var c_oAscNumFormatType = {
		General    : 0,
		Custom     : 1,
		Text       : 2,
		Number     : 3,
		Integer    : 4,
		Scientific : 5,
		Currency   : 6,
		Date       : 7,
		Time       : 8,
		Percent    : 9,
		Fraction   : 10,
		Accounting : 11
	};

	var c_oAscDrawingLayerType = {
		BringToFront : 0,
		SendToBack   : 1,
		BringForward : 2,
		SendBackward : 3
	};

	var c_oAscCellAnchorType = {
		cellanchorAbsolute : 0,
		cellanchorOneCell  : 1,
		cellanchorTwoCell  : 2
	};

	var c_oAscChartDefines = {
		defaultChartWidth  : 478,
		defaultChartHeight : 286
	};

	var c_oAscStyleImage = {
		Default  : 0,
		Document : 1
	};

	var c_oAscTypeSelectElement = {
		Paragraph  : 0,
		Table      : 1,
		Image      : 2,
		Header     : 3,
		Hyperlink  : 4,
		SpellCheck : 5,
		Shape      : 6,
		Slide      : 7,
		Chart      : 8,
		Math       : 9,
		MailMerge  : 10
	};

	var c_oAscLineDrawingRule = {
		Left   : 0,
		Center : 1,
		Right  : 2,
		Top    : 0,
		Bottom : 2
	};

	var align_Right   = 0;
	var align_Left    = 1;
	var align_Center  = 2;
	var align_Justify = 3;


	var linerule_AtLeast = 0x00;
	var linerule_Auto    = 0x01;
	var linerule_Exact   = 0x02;

	var c_oAscShdClear = 0;
	var c_oAscShdNil   = 1;

	var vertalign_Baseline    = 0;
	var vertalign_SuperScript = 1;
	var vertalign_SubScript   = 2;
	var hdrftr_Header         = 0x01;
	var hdrftr_Footer         = 0x02;

	var c_oAscDropCap = {
		None   : 0x00,
		Drop   : 0x01,
		Margin : 0x02
	};


	var c_oAscChartTitleShowSettings = {
		none      : 0,
		overlay   : 1,
		noOverlay : 2
	};

	var c_oAscChartHorAxisLabelShowSettings = {
		none      : 0,
		noOverlay : 1
	};

	var c_oAscChartVertAxisLabelShowSettings = {
		none       : 0,
		rotated    : 1,
		vertical   : 2,
		horizontal : 3
	};

	var c_oAscChartLegendShowSettings = {
		none         : 0,
		left         : 1,
		top          : 2,
		right        : 3,
		bottom       : 4,
		leftOverlay  : 5,
		rightOverlay : 6,
		layout       : 7,
		topRight     : 8 // ToDo добавить в меню
	};

	var c_oAscChartDataLabelsPos = {
		none    : 0,
		b       : 1,
		bestFit : 2,
		ctr     : 3,
		inBase  : 4,
		inEnd   : 5,
		l       : 6,
		outEnd  : 7,
		r       : 8,
		t       : 9
	};

	var c_oAscChartCatAxisSettings = {
		none        : 0,
		leftToRight : 1,
		rightToLeft : 2,
		noLabels    : 3
	};

	var c_oAscChartValAxisSettings = {
		none      : 0,
		byDefault : 1,
		thousands : 2,
		millions  : 3,
		billions  : 4,
		log       : 5
	};

	var c_oAscAxisTypeSettings = {
		vert : 0,
		hor  : 1
	};

	var c_oAscGridLinesSettings = {
		none       : 0,
		major      : 1,
		minor      : 2,
		majorMinor : 3
	};


	var c_oAscChartTypeSettings = {
		barNormal              : 0,
		barStacked             : 1,
		barStackedPer          : 2,
		barNormal3d            : 3,
		barStacked3d           : 4,
		barStackedPer3d        : 5,
		barNormal3dPerspective : 6,
		lineNormal             : 7,
		lineStacked            : 8,
		lineStackedPer         : 9,
		lineNormalMarker       : 10,
		lineStackedMarker      : 11,
		lineStackedPerMarker   : 12,
		line3d                 : 13,
		pie                    : 14,
		pie3d                  : 15,
		hBarNormal             : 16,
		hBarStacked            : 17,
		hBarStackedPer         : 18,
		hBarNormal3d           : 19,
		hBarStacked3d          : 20,
		hBarStackedPer3d       : 21,
		areaNormal             : 22,
		areaStacked            : 23,
		areaStackedPer         : 24,
		doughnut               : 25,
		stock                  : 26,
		scatter                : 27,
		scatterLine            : 28,
		scatterLineMarker      : 29,
		scatterMarker          : 30,
		scatterNone            : 31,
		scatterSmooth          : 32,
		scatterSmoothMarker    : 33,
		unknown                : 34
	};


	var c_oAscValAxisRule = {
		auto  : 0,
		fixed : 1
	};

	var c_oAscValAxUnits = {
		none              : 0,
		BILLIONS          : 1,
		HUNDRED_MILLIONS  : 2,
		HUNDREDS          : 3,
		HUNDRED_THOUSANDS : 4,
		MILLIONS          : 5,
		TEN_MILLIONS      : 6,
		TEN_THOUSANDS     : 7,
		TRILLIONS         : 8,
		CUSTOM            : 9,
		THOUSANDS         : 10

	};

	var c_oAscTickMark = {
		TICK_MARK_CROSS : 0,
		TICK_MARK_IN    : 1,
		TICK_MARK_NONE  : 2,
		TICK_MARK_OUT   : 3
	};

	var c_oAscTickLabelsPos = {
		TICK_LABEL_POSITION_HIGH    : 0,
		TICK_LABEL_POSITION_LOW     : 1,
		TICK_LABEL_POSITION_NEXT_TO : 2,
		TICK_LABEL_POSITION_NONE    : 3
	};

	var c_oAscCrossesRule = {
		auto     : 0,
		maxValue : 1,
		value    : 2,
		minValue : 3
	};

	var c_oAscHorAxisType = {
		auto : 0,
		date : 1,
		text : 2
	};

	var c_oAscBetweenLabelsRule = {
		auto   : 0,
		manual : 1
	};

	var c_oAscLabelsPosition = {
		byDivisions      : 0,
		betweenDivisions : 1
	};


	var c_oAscAxisType = {
		auto : 0,
		date : 1,
		text : 2,
		cat  : 3,
		val  : 4
	};

	var c_oAscHAnchor = {
		Margin : 0x00,
		Page   : 0x01,
		Text   : 0x02,

		PageInternal : 0xFF // только для внутреннего использования
	};

	var c_oAscXAlign = {
		Center  : 0x00,
		Inside  : 0x01,
		Left    : 0x02,
		Outside : 0x03,
		Right   : 0x04
	};
	var c_oAscYAlign = {
		Bottom  : 0x00,
		Center  : 0x01,
		Inline  : 0x02,
		Inside  : 0x03,
		Outside : 0x04,
		Top     : 0x05
	};

	var c_oAscVAnchor = {
		Margin : 0x00,
		Page   : 0x01,
		Text   : 0x02
	};

	var c_oAscRelativeFromH = {
		Character     : 0x00,
		Column        : 0x01,
		InsideMargin  : 0x02,
		LeftMargin    : 0x03,
		Margin        : 0x04,
		OutsideMargin : 0x05,
		Page          : 0x06,
		RightMargin   : 0x07
	};

	var c_oAscSizeRelFromH = {
		sizerelfromhMargin        : 0,
		sizerelfromhPage          : 1,
		sizerelfromhLeftMargin    : 2,
		sizerelfromhRightMargin   : 3,
		sizerelfromhInsideMargin  : 4,
		sizerelfromhOutsideMargin : 5
	};

	var c_oAscSizeRelFromV = {
		sizerelfromvMargin        : 0,
		sizerelfromvPage          : 1,
		sizerelfromvTopMargin     : 2,
		sizerelfromvBottomMargin  : 3,
		sizerelfromvInsideMargin  : 4,
		sizerelfromvOutsideMargin : 5
	};

	var c_oAscRelativeFromV = {
		BottomMargin  : 0x00,
		InsideMargin  : 0x01,
		Line          : 0x02,
		Margin        : 0x03,
		OutsideMargin : 0x04,
		Page          : 0x05,
		Paragraph     : 0x06,
		TopMargin     : 0x07
	};

	// image wrap style
	var c_oAscWrapStyle = {
		Inline : 0,
		Flow   : 1
	};

	// Толщина бордера
	var c_oAscBorderWidth     = {
		None   : 0,	// 0px
		Thin   : 1,	// 1px
		Medium : 2,	// 2px
		Thick  : 3		// 3px
	};
	// Располагаются в порядке значимости для отрисовки
	var c_oAscBorderStyles    = {
		None             : 0,
		Double           : 1,
		Hair             : 2,
		DashDotDot       : 3,
		DashDot          : 4,
		Dotted           : 5,
		Dashed           : 6,
		Thin             : 7,
		MediumDashDotDot : 8,
		SlantDashDot     : 9,
		MediumDashDot    : 10,
		MediumDashed     : 11,
		Medium           : 12,
		Thick            : 13
	};
	var c_oAscBorderType      = {
		Hor  : 1,
		Ver  : 2,
		Diag : 3
	};
	// PageOrientation
	var c_oAscPageOrientation = {
		PagePortrait  : 0x00,
		PageLandscape : 0x01
	};
	/**
	 * lock types
	 * @const
	 */
	var c_oAscLockTypes       = {
		kLockTypeNone   : 1, // никто не залочил данный объект
		kLockTypeMine   : 2, // данный объект залочен текущим пользователем
		kLockTypeOther  : 3, // данный объект залочен другим(не текущим) пользователем
		kLockTypeOther2 : 4, // данный объект залочен другим(не текущим) пользователем (обновления уже пришли)
		kLockTypeOther3 : 5  // данный объект был залочен (обновления пришли) и снова стал залочен
	};

	var c_oAscFormatPainterState = {
		kOff      : 0,
		kOn       : 1,
		kMultiple : 2
	};

	var c_oAscSaveTypes = {
		PartStart   : 0,
		Part        : 1,
		Complete    : 2,
		CompleteAll : 3
	};

	var c_oAscColor = {
		COLOR_TYPE_NONE   : 0,
		COLOR_TYPE_SRGB   : 1,
		COLOR_TYPE_PRST   : 2,
		COLOR_TYPE_SCHEME : 3,
		COLOR_TYPE_SYS    : 4
	};

	var c_oAscFill = {
		FILL_TYPE_NONE   : 0,
		FILL_TYPE_BLIP   : 1,
		FILL_TYPE_NOFILL : 2,
		FILL_TYPE_SOLID  : 3,
		FILL_TYPE_GRAD   : 4,
		FILL_TYPE_PATT   : 5,
		FILL_TYPE_GRP    : 6
	};

	// Chart defines
	var c_oAscChartType    = {
		line     : "Line",
		bar      : "Bar",
		hbar     : "HBar",
		area     : "Area",
		pie      : "Pie",
		scatter  : "Scatter",
		stock    : "Stock",
		doughnut : "Doughnut"
	};
	var c_oAscChartSubType = {
		normal     : "normal",
		stacked    : "stacked",
		stackedPer : "stackedPer"
	};

	var c_oAscFillGradType = {
		GRAD_LINEAR : 1,
		GRAD_PATH   : 2
	};
	var c_oAscFillBlipType = {
		STRETCH : 1,
		TILE    : 2
	};
	var c_oAscStrokeType   = {
		STROKE_NONE  : 0,
		STROKE_COLOR : 1
	};

	var c_oAscVerticalTextAlign = {
		TEXT_ALIGN_BOTTOM : 0, // (Text Anchor Enum ( Bottom ))
		TEXT_ALIGN_CTR    : 1, // (Text Anchor Enum ( Center ))
		TEXT_ALIGN_DIST   : 2, // (Text Anchor Enum ( Distributed ))
		TEXT_ALIGN_JUST   : 3, // (Text Anchor Enum ( Justified ))
		TEXT_ALIGN_TOP    : 4  // Top
	};

	var c_oAscVertDrawingText = {
		normal  : 1,
		vert    : 3,
		vert270 : 4
	};
	var c_oAscLineJoinType    = {
		Round : 1,
		Bevel : 2,
		Miter : 3
	};
	var c_oAscLineCapType     = {
		Flat   : 0,
		Round  : 1,
		Square : 2
	};
	var c_oAscLineBeginType   = {
		None     : 0,
		Arrow    : 1,
		Diamond  : 2,
		Oval     : 3,
		Stealth  : 4,
		Triangle : 5
	};
	var c_oAscLineBeginSize   = {
		small_small : 0,
		small_mid   : 1,
		small_large : 2,
		mid_small   : 3,
		mid_mid     : 4,
		mid_large   : 5,
		large_small : 6,
		large_mid   : 7,
		large_large : 8
	};
	var c_oAscCsvDelimiter    = {
		None      : 0,
		Tab       : 1,
		Semicolon : 2,
		Сolon     : 3,
		Comma     : 4,
		Space     : 5
	};
	var c_oAscUrlType         = {
		Invalid : 0,
		Http    : 1,
		Email   : 2
	};

	var c_oAscCellTextDirection = {
		LRTB : 0x00,
		TBRL : 0x01,
		BTLR : 0x02
	};

	var c_oAscDocumentUnits = {
		Millimeter : 0,
		Inch       : 1,
		Point      : 2
	};

	var c_oAscMouseMoveDataTypes = {
		Common       : 0,
		Hyperlink    : 1,
		LockedObject : 2
	};

	// selection type
	var c_oAscSelectionType = {
		RangeCells     : 1,
		RangeCol       : 2,
		RangeRow       : 3,
		RangeMax       : 4,
		RangeImage     : 5,
		RangeChart     : 6,
		RangeShape     : 7,
		RangeShapeText : 8,
		RangeChartText : 9,
		RangeFrozen    : 10
	};
	var c_oAscInsertOptions = {
		InsertCellsAndShiftRight : 1,
		InsertCellsAndShiftDown  : 2,
		InsertColumns            : 3,
		InsertRows               : 4,
		InsertTableRowAbove      : 5,
		InsertTableRowBelow      : 6,
		InsertTableColLeft       : 7,
		InsertTableColRight      : 8
	};

	var c_oAscDeleteOptions = {
		DeleteCellsAndShiftLeft : 1,
		DeleteCellsAndShiftTop  : 2,
		DeleteColumns           : 3,
		DeleteRows              : 4,
		DeleteTable             : 5
	};


	// Print default options (in mm)
	var c_oAscPrintDefaultSettings = {
		// Размеры страницы при печати
		PageWidth       : 210,
		PageHeight      : 297,
		PageOrientation : c_oAscPageOrientation.PagePortrait,

		// Поля для страницы при печати
		PageLeftField   : 17.8,
		PageRightField  : 17.8,
		PageTopField    : 19.1,
		PageBottomField : 19.1,

		PageGridLines : 0,
		PageHeadings  : 0
	};

	var c_oZoomType = {
		FitToPage  : 1,
		FitToWidth : 2,
		CustomMode : 3
	};

	var c_oAscEncodings    = [
		[0, 28596, "ISO-8859-6", "Arabic (ISO 8859-6)"],
		[1, 720, "DOS-720", "Arabic (OEM 720)"],
		[2, 1256, "windows-1256", "Arabic (Windows)"],

		[3, 28594, "ISO-8859-4", "Baltic (ISO 8859-4)"],
		[4, 28603, "ISO-8859-13", "Baltic (ISO 8859-13)"],
		[5, 775, "IBM775", "Baltic (OEM 775)"],
		[6, 1257, "windows-1257", "Baltic (Windows)"],

		[7, 28604, "ISO-8859-14", "Celtic (ISO 8859-14)"],

		[8, 28595, "ISO-8859-5", "Cyrillic (ISO 8859-5)"],
		[9, 20866, "KOI8-R", "Cyrillic (KOI8-R)"],
		[10, 21866, "KOI8-U", "Cyrillic (KOI8-U)"],
		[11, 10007, "x-mac-cyrillic", "Cyrillic (Mac)"],
		[12, 855, "IBM855", "Cyrillic (OEM 855)"],
		[13, 866, "cp866", "Cyrillic (OEM 866)"],
		[14, 1251, "windows-1251", "Cyrillic (Windows)"],

		[15, 852, "IBM852", "Central European (OEM 852)"],
		[16, 1250, "windows-1250", "Central European (Windows)"],

		[17, 950, "Big5", "Chinese (Big5 Traditional)"],
		[18, 936, "GB2312", "Central (GB2312 Simplified)"],

		[19, 28592, "ISO-8859-2", "Eastern European (ISO 8859-2)"],

		[20, 28597, "ISO-8859-7", "Greek (ISO 8859-7)"],
		[21, 737, "IBM737", "Greek (OEM 737)"],
		[22, 869, "IBM869", "Greek (OEM 869)"],
		[23, 1253, "windows-1253", "Greek (Windows)"],

		[24, 28598, "ISO-8859-8", "Hebrew (ISO 8859-8)"],
		[25, 862, "DOS-862", "Hebrew (OEM 862)"],
		[26, 1255, "windows-1255", "Hebrew (Windows)"],

		[27, 932, "Shift_JIS", "Japanese (Shift-JIS)"],

		[28, 949, "KS_C_5601-1987", "Korean (Windows)"],
		[29, 51949, "EUC-KR", "Korean (EUC)"],

		[30, 861, "IBM861", "North European (Icelandic OEM 861)"],
		[31, 865, "IBM865", "North European (Nordic OEM 865)"],

		[32, 874, "windows-874", "Thai (TIS-620)"],

		[33, 28593, "ISO-8859-3", "Turkish (ISO 8859-3)"],
		[34, 28599, "ISO-8859-9", "Turkish (ISO 8859-9)"],
		[35, 857, "IBM857", "Turkish (OEM 857)"],
		[36, 1254, "windows-1254", "Turkish (Windows)"],

		[37, 28591, "ISO-8859-1", "Western European (ISO-8859-1)"],
		[38, 28605, "ISO-8859-15", "Western European (ISO-8859-15)"],
		[39, 850, "IBM850", "Western European (OEM 850)"],
		[40, 858, "IBM858", "Western European (OEM 858)"],
		[41, 860, "IBM860", "Western European (OEM 860 : Portuguese)"],
		[42, 863, "IBM863", "Western European (OEM 863 : French)"],
		[43, 437, "IBM437", "Western European (OEM-US)"],
		[44, 1252, "windows-1252", "Western European (Windows)"],

		[45, 1258, "windows-1258", "Vietnamese (Windows)"],

		[46, 65001, "UTF-8", "Unicode (UTF-8)"],
		[47, 65000, "UTF-7", "Unicode (UTF-7)"],

		[48, 1200, "UTF-16", "Unicode (UTF-16)"],
		[49, 1201, "UTF-16BE", "Unicode (UTF-16 Big Endian)"],

		[50, 12000, "UTF-32", "Unicode (UTF-32)"],
		[51, 12001, "UTF-32BE", "Unicode (UTF-32 Big Endian)"]
	];
	var c_oAscEncodingsMap = {
		"437"   : 43, "720" : 1, "737" : 21, "775" : 5, "850" : 39, "852" : 15, "855" : 12, "857" : 35, "858" : 40, "860" : 41, "861" : 30, "862" : 25, "863" : 42, "865" : 31, "866" : 13, "869" : 22, "874" : 32, "932" : 27, "936" : 18, "949" : 28, "950" : 17, "1200" : 48, "1201" : 49, "1250" : 16, "1251" : 14, "1252" : 44, "1253" : 23, "1254" : 36, "1255" : 26, "1256" : 2, "1257" : 6, "1258" : 45, "10007" : 11, "12000" : 50, "12001" : 51, "20866" : 9, "21866" : 10, "28591" : 37, "28592" : 19,
		"28593" : 33, "28594" : 3, "28595" : 8, "28596" : 0, "28597" : 20, "28598" : 24, "28599" : 34, "28603" : 4, "28604" : 7, "28605" : 38, "51949" : 29, "65000" : 47, "65001" : 46
	};
	var c_oAscCodePageUtf8 = 46;//65001

	// https://support.office.com/en-us/article/Excel-specifications-and-limits-16c69c74-3d6a-4aaf-ba35-e6eb276e8eaa?ui=en-US&rs=en-US&ad=US&fromAR=1
	var c_oAscMaxTooltipLength       = 256;
	var c_oAscMaxCellOrCommentLength = 32767;
	var c_oAscMaxFormulaLength       = 8192;

	var locktype_None   = 1; // никто не залочил данный объект
	var locktype_Mine   = 2; // данный объект залочен текущим пользователем
	var locktype_Other  = 3; // данный объект залочен другим(не текущим) пользователем
	var locktype_Other2 = 4; // данный объект залочен другим(не текущим) пользователем (обновления уже пришли)
	var locktype_Other3 = 5; // данный объект был залочен (обновления пришли) и снова стал залочен

	var changestype_None                 = 0; // Ничего не происходит с выделенным элементом (проверка идет через дополнительный параметр)
	var changestype_Paragraph_Content    = 1; // Добавление/удаление элементов в параграф
	var changestype_Paragraph_Properties = 2; // Изменение свойств параграфа
	var changestype_Document_Content     = 10; // Добавление/удаление элементов в Document или в DocumentContent
	var changestype_Document_Content_Add = 11; // Добавление элемента в класс Document или в класс DocumentContent
	var changestype_Document_SectPr      = 12; // Изменения свойств данной секции (размер страницы, поля и ориентация)
	var changestype_Document_Styles      = 13; // Изменяем стили документа (добавление/удаление/модифицирование)
	var changestype_Table_Properties     = 20; // Любые изменения в таблице
	var changestype_Table_RemoveCells    = 21; // Удаление ячеек (строк или столбцов)
	var changestype_Image_Properties     = 23; // Изменения настроек картинки
	var changestype_HdrFtr               = 30; // Изменения в колонтитуле (любые изменения)
	var changestype_Remove               = 40; // Удаление, через кнопку backspace (Удаление назад)
	var changestype_Delete               = 41; // Удаление, через кнопку delete (Удаление вперед)
	var changestype_Drawing_Props        = 51; // Изменение свойств фигуры
	var changestype_ColorScheme          = 60; // Изменение свойств фигуры
	var changestype_Text_Props           = 61; // Изменение свойств фигуры
	var changestype_RemoveSlide          = 62; // Изменение свойств фигуры
	var changestype_PresentationProps    = 63; // Изменение темы, цветовой схемы, размера слайда;
	var changestype_Theme                = 64; // Изменение темы;
	var changestype_SlideSize            = 65; // Изменение цветовой схемы;
	var changestype_SlideBg              = 66; // Изменение цветовой схемы;
	var changestype_SlideTiming          = 67; // Изменение цветовой схемы;
	var changestype_MoveComment          = 68;
	var changestype_AddSp                = 69;
	var changestype_AddComment           = 70;
	var changestype_Layout               = 71;
	var changestype_AddShape             = 72;
	var changestype_AddShapes            = 73;

	var changestype_2_InlineObjectMove       = 1; // Передвигаем объект в заданную позцию (проверяем место, в которое пытаемся передвинуть)
	var changestype_2_HdrFtr                 = 2; // Изменения с колонтитулом
	var changestype_2_Comment                = 3; // Работает с комментариями
	var changestype_2_Element_and_Type       = 4; // Проверяем возможно ли сделать изменение заданного типа с заданным элементом(а не с текущим)
	var changestype_2_ElementsArray_and_Type = 5; // Аналогично предыдущему, только идет массив элементов
	var changestype_2_AdditionalTypes        = 6; // Дополнительные проверки типа 1

	var contentchanges_Add    = 1;
	var contentchanges_Remove = 2;

	var offlineMode = '_offline_';

	//------------------------------------------------------------export--------------------------------------------------
	var prot;
	window['Asc']                          = window['Asc'] || {};
	window['Asc']['FONT_THUMBNAIL_HEIGHT'] = FONT_THUMBNAIL_HEIGHT;
	window['Asc']['c_oAscMaxColumnWidth']  = window['Asc'].c_oAscMaxColumnWidth = c_oAscMaxColumnWidth;
	window['Asc']['c_oAscMaxRowHeight'] = window['Asc'].c_oAscMaxRowHeight = c_oAscMaxRowHeight;
	window['Asc']['c_oAscFileType'] = window['Asc'].c_oAscFileType = c_oAscFileType;
	prot                         = c_oAscFileType;
	prot['UNKNOWN']              = prot.UNKNOWN;
	prot['PDF']                  = prot.PDF;
	prot['HTML']                 = prot.HTML;
	prot['DOCX']                 = prot.DOCX;
	prot['DOC']                  = prot.DOC;
	prot['ODT']                  = prot.ODT;
	prot['RTF']                  = prot.RTF;
	prot['TXT']                  = prot.TXT;
	prot['MHT']                  = prot.MHT;
	prot['EPUB']                 = prot.EPUB;
	prot['FB2']                  = prot.FB2;
	prot['MOBI']                 = prot.MOBI;
	prot['DOCY']                 = prot.DOCY;
	prot['JSON']                 = prot.JSON;
	prot['XLSX']                 = prot.XLSX;
	prot['XLS']                  = prot.XLS;
	prot['ODS']                  = prot.ODS;
	prot['CSV']                  = prot.CSV;
	prot['XLSY']                 = prot.XLSY;
	prot['PPTX']                 = prot.PPTX;
	prot['PPT']                  = prot.PPT;
	prot['ODP']                  = prot.ODP;
	window['Asc']['c_oAscError'] = window['Asc'].c_oAscError = c_oAscError;
	prot                                     = c_oAscError;
	prot['Level']                            = prot.Level;
	prot['ID']                               = prot.ID;
	prot                                     = c_oAscError.Level;
	prot['Critical']                         = prot.Critical;
	prot['NoCritical']                       = prot.NoCritical;
	prot                                     = c_oAscError.ID;
	prot['ServerSaveComplete']               = prot.ServerSaveComplete;
	prot['ConvertationProgress']             = prot.ConvertationProgress;
	prot['DownloadProgress']                 = prot.DownloadProgress;
	prot['No']                               = prot.No;
	prot['Unknown']                          = prot.Unknown;
	prot['ConvertationTimeout']              = prot.ConvertationTimeout;
	prot['ConvertationError']                = prot.ConvertationError;
	prot['DownloadError']                    = prot.DownloadError;
	prot['UnexpectedGuid']                   = prot.UnexpectedGuid;
	prot['Database']                         = prot.Database;
	prot['FileRequest']                      = prot.FileRequest;
	prot['FileVKey']                         = prot.FileVKey;
	prot['UplImageSize']                     = prot.UplImageSize;
	prot['UplImageExt']                      = prot.UplImageExt;
	prot['UplImageFileCount']                = prot.UplImageFileCount;
	prot['NoSupportClipdoard']               = prot.NoSupportClipdoard;
	prot['UplImageUrl']                      = prot.UplImageUrl;
	prot['StockChartError']                  = prot.StockChartError;
	prot['CoAuthoringDisconnect']            = prot.CoAuthoringDisconnect;
	prot['ConvertationPassword']             = prot.ConvertationPassword;
	prot['VKeyEncrypt']                      = prot.VKeyEncrypt;
	prot['KeyExpire']                        = prot.KeyExpire;
	prot['UserCountExceed']                  = prot.UserCountExceed;
	prot['SplitCellMaxRows']                 = prot.SplitCellMaxRows;
	prot['SplitCellMaxCols']                 = prot.SplitCellMaxCols;
	prot['SplitCellRowsDivider']             = prot.SplitCellRowsDivider;
	prot['MobileUnexpectedCharCount']        = prot.MobileUnexpectedCharCount;
	prot['MailMergeLoadFile']                = prot.MailMergeLoadFile;
	prot['MailMergeSaveFile']                = prot.MailMergeSaveFile;
	prot['AutoFilterDataRangeError']         = prot.AutoFilterDataRangeError;
	prot['AutoFilterChangeFormatTableError'] = prot.AutoFilterChangeFormatTableError;
	prot['AutoFilterChangeError']            = prot.AutoFilterChangeError;
	prot['AutoFilterMoveToHiddenRangeError'] = prot.AutoFilterMoveToHiddenRangeError;
	prot['LockedAllError']                   = prot.LockedAllError;
	prot['LockedWorksheetRename']            = prot.LockedWorksheetRename;
	prot['FTChangeTableRangeError']          = prot.FTChangeTableRangeError;
	prot['FTRangeIncludedOtherTables']       = prot.FTRangeIncludedOtherTables;
	prot['PasteMaxRangeError']               = prot.PasteMaxRangeError;
	prot['PastInMergeAreaError']             = prot.PastInMergeAreaError;
	prot['DataRangeError']                   = prot.DataRangeError;
	prot['CannotMoveRange']                  = prot.CannotMoveRange;
	prot['MaxDataSeriesError']               = prot.MaxDataSeriesError;
	prot['CannotFillRange']                  = prot.CannotFillRange;
	prot['UserDrop']                         = prot.UserDrop;
	prot['Warning']                          = prot.Warning;
	prot['FrmlWrongCountParentheses']        = prot.FrmlWrongCountParentheses;
	prot['FrmlWrongOperator']                = prot.FrmlWrongOperator;
	prot['FrmlWrongMaxArgument']             = prot.FrmlWrongMaxArgument;
	prot['FrmlWrongCountArgument']           = prot.FrmlWrongCountArgument;
	prot['FrmlWrongFunctionName']            = prot.FrmlWrongFunctionName;
	prot['FrmlAnotherParsingError']          = prot.FrmlAnotherParsingError;
	prot['FrmlWrongArgumentRange']           = prot.FrmlWrongArgumentRange;
	prot['FrmlOperandExpected']              = prot.FrmlOperandExpected;
	prot['FrmlParenthesesCorrectCount']      = prot.FrmlParenthesesCorrectCount;
	prot['FrmlWrongReferences']              = prot.FrmlWrongReferences;
	prot['InvalidReferenceOrName']           = prot.InvalidReferenceOrName;
	prot['LockCreateDefName']                = prot.LockCreateDefName;
	prot['OpenWarning']                      = prot.OpenWarning;
	window['Asc']['c_oAscAsyncAction']       = window['Asc'].c_oAscAsyncAction = c_oAscAsyncAction;
	prot                                     = c_oAscAsyncAction;
	prot['Open']                             = prot.Open;
	prot['Save']                             = prot.Save;
	prot['LoadDocumentFonts']                = prot.LoadDocumentFonts;
	prot['LoadDocumentImages']               = prot.LoadDocumentImages;
	prot['LoadFont']                         = prot.LoadFont;
	prot['LoadImage']                        = prot.LoadImage;
	prot['DownloadAs']                       = prot.DownloadAs;
	prot['Print']                            = prot.Print;
	prot['UploadImage']                      = prot.UploadImage;
	prot['ApplyChanges']                     = prot.ApplyChanges;
	prot['SlowOperation']                    = prot.SlowOperation;
	prot['LoadTheme']                        = prot.LoadTheme;
	prot['MailMergeLoadFile']                = prot.MailMergeLoadFile;
	prot['DownloadMerge']                    = prot.DownloadMerge;
	prot['SendMailMerge']                    = prot.SendMailMerge;
	window['Asc']['c_oAscAdvancedOptionsID'] = window['Asc'].c_oAscAdvancedOptionsID = c_oAscAdvancedOptionsID;
	prot                                         = c_oAscAdvancedOptionsID;
	prot['CSV']                                  = prot.CSV;
	prot['TXT']                                  = prot.TXT;
	window['Asc']['c_oAscFontRenderingModeType'] = window['Asc'].c_oAscFontRenderingModeType = c_oAscFontRenderingModeType;
	prot                                   = c_oAscFontRenderingModeType;
	prot['noHinting']                      = prot.noHinting;
	prot['hinting']                        = prot.hinting;
	prot['hintingAndSubpixeling']          = prot.hintingAndSubpixeling;
	window['Asc']['c_oAscAsyncActionType'] = window['Asc'].c_oAscAsyncActionType = c_oAscAsyncActionType;
	prot                                 = c_oAscAsyncActionType;
	prot['Information']                  = prot.Information;
	prot['BlockInteraction']             = prot.BlockInteraction;
	window['Asc']['c_oAscNumFormatType'] = window['Asc'].c_oAscNumFormatType = c_oAscNumFormatType;
	prot                                     = c_oAscNumFormatType;
	prot['General']                          = prot.General;
	prot['Custom']                           = prot.Custom;
	prot['Text']                             = prot.Text;
	prot['Number']                           = prot.Number;
	prot['Integer']                          = prot.Integer;
	prot['Scientific']                       = prot.Scientific;
	prot['Currency']                         = prot.Currency;
	prot['Date']                             = prot.Date;
	prot['Time']                             = prot.Time;
	prot['Percent']                          = prot.Percent;
	prot['Fraction']                         = prot.Fraction;
	prot['Accounting']                       = prot.Accounting;
	window['Asc']['c_oAscDrawingLayerType']  = c_oAscDrawingLayerType;
	prot                                     = c_oAscDrawingLayerType;
	prot['BringToFront']                     = prot.BringToFront;
	prot['SendToBack']                       = prot.SendToBack;
	prot['BringForward']                     = prot.BringForward;
	prot['SendBackward']                     = prot.SendBackward;
	window['Asc']['c_oAscTypeSelectElement'] = window['Asc'].c_oAscTypeSelectElement = c_oAscTypeSelectElement;
	prot                              = c_oAscTypeSelectElement;
	prot['Paragraph']                 = prot.Paragraph;
	prot['Table']                     = prot.Table;
	prot['Image']                     = prot.Image;
	prot['Header']                    = prot.Header;
	prot['Hyperlink']                 = prot.Hyperlink;
	prot['SpellCheck']                = prot.SpellCheck;
	prot['Shape']                     = prot.Shape;
	prot['Slide']                     = prot.Slide;
	prot['Chart']                     = prot.Chart;
	prot['Math']                      = prot.Math;
	prot['MailMerge']                 = prot.MailMerge;
	window['Asc']['linerule_AtLeast'] = window['Asc'].linerule_AtLeast = linerule_AtLeast;
	window['Asc']['linerule_Auto'] = window['Asc'].linerule_Auto = linerule_Auto;
	window['Asc']['linerule_Exact'] = window['Asc'].linerule_Exact = linerule_Exact;
	window['Asc']['c_oAscShdClear'] = window['Asc'].c_oAscShdClear = c_oAscShdClear;
	window['Asc']['c_oAscShdNil'] = window['Asc'].c_oAscShdNil = c_oAscShdNil;
	window['Asc']['c_oAscDropCap'] = window['Asc'].c_oAscDropCap = c_oAscDropCap;
	prot                                          = c_oAscDropCap;
	prot['None']                                  = prot.None;
	prot['Drop']                                  = prot.Drop;
	prot['Margin']                                = prot.Margin;
	window['Asc']['c_oAscChartTitleShowSettings'] = window['Asc'].c_oAscChartTitleShowSettings = c_oAscChartTitleShowSettings;
	prot                                                 = c_oAscChartTitleShowSettings;
	prot['none']                                         = prot.none;
	prot['overlay']                                      = prot.overlay;
	prot['noOverlay']                                    = prot.noOverlay;
	window['Asc']['c_oAscChartHorAxisLabelShowSettings'] = window['Asc'].c_oAscChartHorAxisLabelShowSettings = c_oAscChartHorAxisLabelShowSettings;
	prot                                                  = c_oAscChartHorAxisLabelShowSettings;
	prot['none']                                          = prot.none;
	prot['noOverlay']                                     = prot.noOverlay;
	window['Asc']['c_oAscChartVertAxisLabelShowSettings'] = window['Asc'].c_oAscChartVertAxisLabelShowSettings = c_oAscChartVertAxisLabelShowSettings;
	prot                                           = c_oAscChartVertAxisLabelShowSettings;
	prot['none']                                   = prot.none;
	prot['rotated']                                = prot.rotated;
	prot['vertical']                               = prot.vertical;
	prot['horizontal']                             = prot.horizontal;
	window['Asc']['c_oAscChartLegendShowSettings'] = window['Asc'].c_oAscChartLegendShowSettings = c_oAscChartLegendShowSettings;
	prot                                      = c_oAscChartLegendShowSettings;
	prot['none']                              = prot.none;
	prot['left']                              = prot.left;
	prot['top']                               = prot.top;
	prot['right']                             = prot.right;
	prot['bottom']                            = prot.bottom;
	prot['leftOverlay']                       = prot.leftOverlay;
	prot['rightOverlay']                      = prot.rightOverlay;
	prot['layout']                            = prot.layout;
	prot['topRight']                          = prot.topRight;
	window['Asc']['c_oAscChartDataLabelsPos'] = window['Asc'].c_oAscChartDataLabelsPos = c_oAscChartDataLabelsPos;
	prot                                     = c_oAscChartDataLabelsPos;
	prot['none']                             = prot.none;
	prot['b']                                = prot.b;
	prot['bestFit']                          = prot.bestFit;
	prot['ctr']                              = prot.ctr;
	prot['inBase']                           = prot.inBase;
	prot['inEnd']                            = prot.inEnd;
	prot['l']                                = prot.l;
	prot['outEnd']                           = prot.outEnd;
	prot['r']                                = prot.r;
	prot['t']                                = prot.t;
	window['Asc']['c_oAscGridLinesSettings'] = window['Asc'].c_oAscGridLinesSettings = c_oAscGridLinesSettings;
	prot                                     = c_oAscGridLinesSettings;
	prot['none']                             = prot.none;
	prot['major']                            = prot.major;
	prot['minor']                            = prot.minor;
	prot['majorMinor']                       = prot.majorMinor;
	window['Asc']['c_oAscChartTypeSettings'] = window['Asc'].c_oAscChartTypeSettings = c_oAscChartTypeSettings;
	prot                               = c_oAscChartTypeSettings;
	prot['barNormal']                  = prot.barNormal;
	prot['barStacked']                 = prot.barStacked;
	prot['barStackedPer']              = prot.barStackedPer;
	prot['barNormal3d']                = prot.barNormal3d;
	prot['barStacked3d']               = prot.barStacked3d;
	prot['barStackedPer3d']            = prot.barStackedPer3d;
	prot['barNormal3dPerspective']     = prot.barNormal3dPerspective;
	prot['lineNormal']                 = prot.lineNormal;
	prot['lineStacked']                = prot.lineStacked;
	prot['lineStackedPer']             = prot.lineStackedPer;
	prot['lineNormalMarker']           = prot.lineNormalMarker;
	prot['lineStackedMarker']          = prot.lineStackedMarker;
	prot['lineStackedPerMarker']       = prot.lineStackedPerMarker;
	prot['line3d']                     = prot.line3d;
	prot['pie']                        = prot.pie;
	prot['pie3d']                      = prot.pie3d;
	prot['hBarNormal']                 = prot.hBarNormal;
	prot['hBarStacked']                = prot.hBarStacked;
	prot['hBarStackedPer']             = prot.hBarStackedPer;
	prot['hBarNormal3d']               = prot.hBarNormal3d;
	prot['hBarStacked3d']              = prot.hBarStacked3d;
	prot['hBarStackedPer3d']           = prot.hBarStackedPer3d;
	prot['areaNormal']                 = prot.areaNormal;
	prot['areaStacked']                = prot.areaStacked;
	prot['areaStackedPer']             = prot.areaStackedPer;
	prot['doughnut']                   = prot.doughnut;
	prot['stock']                      = prot.stock;
	prot['scatter']                    = prot.scatter;
	prot['scatterLine']                = prot.scatterLine;
	prot['scatterLineMarker']          = prot.scatterLineMarker;
	prot['scatterMarker']              = prot.scatterMarker;
	prot['scatterNone']                = prot.scatterNone;
	prot['scatterSmooth']              = prot.scatterSmooth;
	prot['scatterSmoothMarker']        = prot.scatterSmoothMarker;
	prot['unknown']                    = prot.unknown;
	window['Asc']['c_oAscValAxisRule'] = window['Asc'].c_oAscValAxisRule = c_oAscValAxisRule;
	prot                              = c_oAscValAxisRule;
	prot['auto']                      = prot.auto;
	prot['fixed']                     = prot.fixed;
	window['Asc']['c_oAscValAxUnits'] = window['Asc'].c_oAscValAxUnits = c_oAscValAxUnits;
	prot                            = c_oAscValAxUnits;
	prot['BILLIONS']                = prot.BILLIONS;
	prot['HUNDRED_MILLIONS']        = prot.HUNDRED_MILLIONS;
	prot['HUNDREDS']                = prot.HUNDREDS;
	prot['HUNDRED_THOUSANDS']       = prot.HUNDRED_THOUSANDS;
	prot['MILLIONS']                = prot.MILLIONS;
	prot['TEN_MILLIONS']            = prot.TEN_MILLIONS;
	prot['TEN_THOUSANDS']           = prot.TEN_THOUSANDS;
	prot['TRILLIONS']               = prot.TRILLIONS;
	prot['CUSTOM']                  = prot.CUSTOM;
	prot['THOUSANDS']               = prot.THOUSANDS;
	window['Asc']['c_oAscTickMark'] = window['Asc'].c_oAscTickMark = c_oAscTickMark;
	prot                                 = c_oAscTickMark;
	prot['TICK_MARK_CROSS']              = prot.TICK_MARK_CROSS;
	prot['TICK_MARK_IN']                 = prot.TICK_MARK_IN;
	prot['TICK_MARK_NONE']               = prot.TICK_MARK_NONE;
	prot['TICK_MARK_OUT']                = prot.TICK_MARK_OUT;
	window['Asc']['c_oAscTickLabelsPos'] = window['Asc'].c_oAscTickLabelsPos = c_oAscTickLabelsPos;
	prot                                = c_oAscTickLabelsPos;
	prot['TICK_LABEL_POSITION_HIGH']    = prot.TICK_LABEL_POSITION_HIGH;
	prot['TICK_LABEL_POSITION_LOW']     = prot.TICK_LABEL_POSITION_LOW;
	prot['TICK_LABEL_POSITION_NEXT_TO'] = prot.TICK_LABEL_POSITION_NEXT_TO;
	prot['TICK_LABEL_POSITION_NONE']    = prot.TICK_LABEL_POSITION_NONE;
	window['Asc']['c_oAscCrossesRule']  = window['Asc'].c_oAscCrossesRule = c_oAscCrossesRule;
	prot                                     = c_oAscCrossesRule;
	prot['auto']                             = prot.auto;
	prot['maxValue']                         = prot.maxValue;
	prot['value']                            = prot.value;
	prot['minValue']                         = prot.minValue;
	window['Asc']['c_oAscBetweenLabelsRule'] = window['Asc'].c_oAscBetweenLabelsRule = c_oAscBetweenLabelsRule;
	prot                                  = c_oAscBetweenLabelsRule;
	prot['auto']                          = prot.auto;
	prot['manual']                        = prot.manual;
	window['Asc']['c_oAscLabelsPosition'] = window['Asc'].c_oAscLabelsPosition = c_oAscLabelsPosition;
	prot                            = c_oAscLabelsPosition;
	prot['byDivisions']             = prot.byDivisions;
	prot['betweenDivisions']        = prot.betweenDivisions;
	window['Asc']['c_oAscAxisType'] = window['Asc'].c_oAscAxisType = c_oAscAxisType;
	prot                           = c_oAscAxisType;
	prot['auto']                   = prot.auto;
	prot['date']                   = prot.date;
	prot['text']                   = prot.text;
	prot['cat']                    = prot.cat;
	prot['val']                    = prot.val;
	window['Asc']['c_oAscHAnchor'] = window['Asc'].c_oAscHAnchor = c_oAscHAnchor;
	prot                          = c_oAscHAnchor;
	prot['Margin']                = prot.Margin;
	prot['Page']                  = prot.Page;
	prot['Text']                  = prot.Text;
	prot['PageInternal']          = prot.PageInternal;
	window['Asc']['c_oAscXAlign'] = window['Asc'].c_oAscXAlign = c_oAscXAlign;
	prot                          = c_oAscXAlign;
	prot['Center']                = prot.Center;
	prot['Inside']                = prot.Inside;
	prot['Left']                  = prot.Left;
	prot['Outside']               = prot.Outside;
	prot['Right']                 = prot.Right;
	window['Asc']['c_oAscYAlign'] = window['Asc'].c_oAscYAlign = c_oAscYAlign;
	prot                           = c_oAscYAlign;
	prot['Bottom']                 = prot.Bottom;
	prot['Center']                 = prot.Center;
	prot['Inline']                 = prot.Inline;
	prot['Inside']                 = prot.Inside;
	prot['Outside']                = prot.Outside;
	prot['Top']                    = prot.Top;
	window['Asc']['c_oAscVAnchor'] = window['Asc'].c_oAscVAnchor = c_oAscVAnchor;
	prot                                 = c_oAscVAnchor;
	prot['Margin']                       = prot.Margin;
	prot['Page']                         = prot.Page;
	prot['Text']                         = prot.Text;
	window['Asc']['c_oAscRelativeFromH'] = window['Asc'].c_oAscRelativeFromH = c_oAscRelativeFromH;
	prot                                 = c_oAscRelativeFromH;
	prot['Character']                    = prot.Character;
	prot['Column']                       = prot.Column;
	prot['InsideMargin']                 = prot.InsideMargin;
	prot['LeftMargin']                   = prot.LeftMargin;
	prot['Margin']                       = prot.Margin;
	prot['OutsideMargin']                = prot.OutsideMargin;
	prot['Page']                         = prot.Page;
	prot['RightMargin']                  = prot.RightMargin;
	window['Asc']['c_oAscRelativeFromV'] = window['Asc'].c_oAscRelativeFromV = c_oAscRelativeFromV;
	prot                                   = c_oAscRelativeFromV;
	prot['BottomMargin']                   = prot.BottomMargin;
	prot['InsideMargin']                   = prot.InsideMargin;
	prot['Line']                           = prot.Line;
	prot['Margin']                         = prot.Margin;
	prot['OutsideMargin']                  = prot.OutsideMargin;
	prot['Page']                           = prot.Page;
	prot['Paragraph']                      = prot.Paragraph;
	prot['TopMargin']                      = prot.TopMargin;
	window['Asc']['c_oAscPageOrientation'] = window['Asc'].c_oAscPageOrientation = c_oAscPageOrientation;
	prot                         = c_oAscPageOrientation;
	prot['PagePortrait']         = prot.PagePortrait;
	prot['PageLandscape']        = prot.PageLandscape;
	window['Asc']['c_oAscColor'] = window['Asc'].c_oAscColor = c_oAscColor;
	prot                        = c_oAscColor;
	prot['COLOR_TYPE_NONE']     = prot.COLOR_TYPE_NONE;
	prot['COLOR_TYPE_SRGB']     = prot.COLOR_TYPE_SRGB;
	prot['COLOR_TYPE_PRST']     = prot.COLOR_TYPE_PRST;
	prot['COLOR_TYPE_SCHEME']   = prot.COLOR_TYPE_SCHEME;
	prot['COLOR_TYPE_SYS']      = prot.COLOR_TYPE_SYS;
	window['Asc']['c_oAscFill'] = window['Asc'].c_oAscFill = c_oAscFill;
	prot                                = c_oAscFill;
	prot['FILL_TYPE_NONE']              = prot.FILL_TYPE_NONE;
	prot['FILL_TYPE_BLIP']              = prot.FILL_TYPE_BLIP;
	prot['FILL_TYPE_NOFILL']            = prot.FILL_TYPE_NOFILL;
	prot['FILL_TYPE_SOLID']             = prot.FILL_TYPE_SOLID;
	prot['FILL_TYPE_GRAD']              = prot.FILL_TYPE_GRAD;
	prot['FILL_TYPE_PATT']              = prot.FILL_TYPE_PATT;
	prot['FILL_TYPE_GRP']               = prot.FILL_TYPE_GRP;
	window['Asc']['c_oAscFillGradType'] = window['Asc'].c_oAscFillGradType = c_oAscFillGradType;
	prot                                = c_oAscFillGradType;
	prot['GRAD_LINEAR']                 = prot.GRAD_LINEAR;
	prot['GRAD_PATH']                   = prot.GRAD_PATH;
	window['Asc']['c_oAscFillBlipType'] = window['Asc'].c_oAscFillBlipType = c_oAscFillBlipType;
	prot                              = c_oAscFillBlipType;
	prot['STRETCH']                   = prot.STRETCH;
	prot['TILE']                      = prot.TILE;
	window['Asc']['c_oAscStrokeType'] = window['Asc'].c_oAscStrokeType = c_oAscStrokeType;
	prot                                     = c_oAscStrokeType;
	prot['STROKE_NONE']                      = prot.STROKE_NONE;
	prot['STROKE_COLOR']                     = prot.STROKE_COLOR;
	window['Asc']['c_oAscVerticalTextAlign'] = c_oAscVerticalTextAlign;
	prot                                     = c_oAscVerticalTextAlign;
	prot['TEXT_ALIGN_BOTTOM']                = prot.TEXT_ALIGN_BOTTOM;
	prot['TEXT_ALIGN_CTR']                   = prot.TEXT_ALIGN_CTR;
	prot['TEXT_ALIGN_DIST']                  = prot.TEXT_ALIGN_DIST;
	prot['TEXT_ALIGN_JUST']                  = prot.TEXT_ALIGN_JUST;
	prot['TEXT_ALIGN_TOP']                   = prot.TEXT_ALIGN_TOP;
	window['Asc']['c_oAscVertDrawingText']   = c_oAscVertDrawingText;
	prot                                     = c_oAscVertDrawingText;
	prot['normal']                           = prot.normal;
	prot['vert']                             = prot.vert;
	prot['vert270']                          = prot.vert270;
	window['Asc']['c_oAscLineJoinType']      = c_oAscLineJoinType;
	prot                                     = c_oAscLineJoinType;
	prot['Round']                            = prot.Round;
	prot['Bevel']                            = prot.Bevel;
	prot['Miter']                            = prot.Miter;
	window['Asc']['c_oAscLineCapType']       = c_oAscLineCapType;
	prot                                     = c_oAscLineCapType;
	prot['Flat']                             = prot.Flat;
	prot['Round']                            = prot.Round;
	prot['Square']                           = prot.Square;
	window['Asc']['c_oAscLineBeginType']     = c_oAscLineBeginType;
	prot                                     = c_oAscLineBeginType;
	prot['None']                             = prot.None;
	prot['Arrow']                            = prot.Arrow;
	prot['Diamond']                          = prot.Diamond;
	prot['Oval']                             = prot.Oval;
	prot['Stealth']                          = prot.Stealth;
	prot['Triangle']                         = prot.Triangle;
	window['Asc']['c_oAscLineBeginSize']     = c_oAscLineBeginSize;
	prot                                     = c_oAscLineBeginSize;
	prot['small_small']                      = prot.small_small;
	prot['small_mid']                        = prot.small_mid;
	prot['small_large']                      = prot.small_large;
	prot['mid_small']                        = prot.mid_small;
	prot['mid_mid']                          = prot.mid_mid;
	prot['mid_large']                        = prot.mid_large;
	prot['large_small']                      = prot.large_small;
	prot['large_mid']                        = prot.large_mid;
	prot['large_large']                      = prot.large_large;
	window['Asc']['c_oAscCellTextDirection'] = window['Asc'].c_oAscCellTextDirection = c_oAscCellTextDirection;
	prot                                 = c_oAscCellTextDirection;
	prot['LRTB']                         = prot.LRTB;
	prot['TBRL']                         = prot.TBRL;
	prot['BTLR']                         = prot.BTLR;
	window['Asc']['c_oAscDocumentUnits'] = window['Asc'].c_oAscDocumentUnits = c_oAscDocumentUnits;
	prot                                    = c_oAscDocumentUnits;
	prot['Millimeter']                      = prot.Millimeter;
	prot['Inch']                            = prot.Inch;
	prot['Point']                           = prot.Point;
	window['Asc']['c_oAscMaxTooltipLength'] = window['Asc'].c_oAscMaxTooltipLength = c_oAscMaxTooltipLength;
	window['Asc']['c_oAscMaxCellOrCommentLength'] = window['Asc'].c_oAscMaxCellOrCommentLength = c_oAscMaxCellOrCommentLength;
	window['Asc']['c_oAscSelectionType'] = window['Asc'].c_oAscSelectionType = c_oAscSelectionType;
	prot                                 = c_oAscSelectionType;
	prot['RangeCells']                   = prot.RangeCells;
	prot['RangeCol']                     = prot.RangeCol;
	prot['RangeRow']                     = prot.RangeRow;
	prot['RangeMax']                     = prot.RangeMax;
	prot['RangeImage']                   = prot.RangeImage;
	prot['RangeChart']                   = prot.RangeChart;
	prot['RangeShape']                   = prot.RangeShape;
	prot['RangeShapeText']               = prot.RangeShapeText;
	prot['RangeChartText']               = prot.RangeChartText;
	prot['RangeFrozen']                  = prot.RangeFrozen;
	window['Asc']['c_oAscInsertOptions'] = window['Asc'].c_oAscInsertOptions = c_oAscInsertOptions;
	prot                                 = c_oAscInsertOptions;
	prot['InsertCellsAndShiftRight']     = prot.InsertCellsAndShiftRight;
	prot['InsertCellsAndShiftDown']      = prot.InsertCellsAndShiftDown;
	prot['InsertColumns']                = prot.InsertColumns;
	prot['InsertRows']                   = prot.InsertRows;
	prot['InsertTableRowAbove']          = prot.InsertTableRowAbove;
	prot['InsertTableRowBelow']          = prot.InsertTableRowBelow;
	prot['InsertTableColLeft']           = prot.InsertTableColLeft;
	prot['InsertTableColRight']          = prot.InsertTableColRight;
	window['Asc']['c_oAscDeleteOptions'] = window['Asc'].c_oAscDeleteOptions = c_oAscDeleteOptions;
	prot                            = c_oAscDeleteOptions;
	prot['DeleteCellsAndShiftLeft'] = prot.DeleteCellsAndShiftLeft;
	prot['DeleteCellsAndShiftTop']  = prot.DeleteCellsAndShiftTop;
	prot['DeleteColumns']           = prot.DeleteColumns;
	prot['DeleteRows']              = prot.DeleteRows;
	prot['DeleteTable']             = prot.DeleteTable;

	window['AscCommon']                             = window['AscCommon'] || {};
	window["AscCommon"].g_cCharDelimiter            = g_cCharDelimiter;
	window["AscCommon"].bDate1904                   = false;
	window["AscCommon"].c_oAscAdvancedOptionsAction = c_oAscAdvancedOptionsAction;
	window["AscCommon"].DownloadType                = DownloadType;
	window["AscCommon"].CellValueType               = CellValueType;
	window["AscCommon"].c_oAscCellAnchorType        = c_oAscCellAnchorType;
	window["AscCommon"].c_oAscChartDefines          = c_oAscChartDefines;
	window["AscCommon"].c_oAscStyleImage            = c_oAscStyleImage;
	window["AscCommon"].c_oAscLineDrawingRule       = c_oAscLineDrawingRule;
	window["AscCommon"].align_Right                 = align_Right;
	window["AscCommon"].align_Left                  = align_Left;
	window["AscCommon"].align_Center                = align_Center;
	window["AscCommon"].align_Justify               = align_Justify;
	window["AscCommon"].vertalign_Baseline          = vertalign_Baseline;
	window["AscCommon"].vertalign_SuperScript       = vertalign_SuperScript;
	window["AscCommon"].vertalign_SubScript         = vertalign_SubScript;
	window["AscCommon"].hdrftr_Header               = hdrftr_Header;
	window["AscCommon"].hdrftr_Footer               = hdrftr_Footer;
	window["AscCommon"].c_oAscSizeRelFromH          = c_oAscSizeRelFromH;
	window["AscCommon"].c_oAscSizeRelFromV          = c_oAscSizeRelFromV;
	window["AscCommon"].c_oAscWrapStyle             = c_oAscWrapStyle;
	window["AscCommon"].c_oAscBorderWidth           = c_oAscBorderWidth;
	window["AscCommon"].c_oAscBorderStyles          = c_oAscBorderStyles;
	window["AscCommon"].c_oAscBorderType            = c_oAscBorderType;
	window["AscCommon"].c_oAscLockTypes             = c_oAscLockTypes;
	window["AscCommon"].c_oAscFormatPainterState    = c_oAscFormatPainterState;
	window["AscCommon"].c_oAscSaveTypes             = c_oAscSaveTypes;
	window["AscCommon"].c_oAscChartType             = c_oAscChartType;
	window["AscCommon"].c_oAscChartSubType          = c_oAscChartSubType;
	window["AscCommon"].c_oAscCsvDelimiter          = c_oAscCsvDelimiter;
	window["AscCommon"].c_oAscUrlType               = c_oAscUrlType;
	window["AscCommon"].c_oAscMouseMoveDataTypes    = c_oAscMouseMoveDataTypes;
	window["AscCommon"].c_oAscPrintDefaultSettings  = c_oAscPrintDefaultSettings;
	window["AscCommon"].c_oZoomType                 = c_oZoomType;
	window["AscCommon"].c_oAscEncodings             = c_oAscEncodings;
	window["AscCommon"].c_oAscEncodingsMap          = c_oAscEncodingsMap;
	window["AscCommon"].c_oAscCodePageUtf8          = c_oAscCodePageUtf8;
	window["AscCommon"].c_oAscMaxFormulaLength      = c_oAscMaxFormulaLength;

	window["AscCommon"].locktype_None   = locktype_None;
	window["AscCommon"].locktype_Mine   = locktype_Mine;
	window["AscCommon"].locktype_Other  = locktype_Other;
	window["AscCommon"].locktype_Other2 = locktype_Other2;
	window["AscCommon"].locktype_Other3 = locktype_Other3;

	window["AscCommon"].changestype_None                     = changestype_None;
	window["AscCommon"].changestype_Paragraph_Content        = changestype_Paragraph_Content;
	window["AscCommon"].changestype_Paragraph_Properties     = changestype_Paragraph_Properties;
	window["AscCommon"].changestype_Document_Content         = changestype_Document_Content;
	window["AscCommon"].changestype_Document_Content_Add     = changestype_Document_Content_Add;
	window["AscCommon"].changestype_Document_SectPr          = changestype_Document_SectPr;
	window["AscCommon"].changestype_Document_Styles          = changestype_Document_Styles;
	window["AscCommon"].changestype_Table_Properties         = changestype_Table_Properties;
	window["AscCommon"].changestype_Table_RemoveCells        = changestype_Table_RemoveCells;
	window["AscCommon"].changestype_Image_Properties         = changestype_Image_Properties;
	window["AscCommon"].changestype_HdrFtr                   = changestype_HdrFtr;
	window["AscCommon"].changestype_Remove                   = changestype_Remove;
	window["AscCommon"].changestype_Delete                   = changestype_Delete;
	window["AscCommon"].changestype_Drawing_Props            = changestype_Drawing_Props;
	window["AscCommon"].changestype_ColorScheme              = changestype_ColorScheme;
	window["AscCommon"].changestype_Text_Props               = changestype_Text_Props;
	window["AscCommon"].changestype_RemoveSlide              = changestype_RemoveSlide;
	window["AscCommon"].changestype_Theme                    = changestype_Theme;
	window["AscCommon"].changestype_SlideSize                = changestype_SlideSize;
	window["AscCommon"].changestype_SlideBg                  = changestype_SlideBg;
	window["AscCommon"].changestype_SlideTiming              = changestype_SlideTiming;
	window["AscCommon"].changestype_MoveComment              = changestype_MoveComment;
	window["AscCommon"].changestype_AddComment               = changestype_AddComment;
	window["AscCommon"].changestype_Layout                   = changestype_Layout;
	window["AscCommon"].changestype_AddShape                 = changestype_AddShape;
	window["AscCommon"].changestype_AddShapes                = changestype_AddShapes;
	window["AscCommon"].changestype_2_InlineObjectMove       = changestype_2_InlineObjectMove;
	window["AscCommon"].changestype_2_HdrFtr                 = changestype_2_HdrFtr;
	window["AscCommon"].changestype_2_Comment                = changestype_2_Comment;
	window["AscCommon"].changestype_2_Element_and_Type       = changestype_2_Element_and_Type;
	window["AscCommon"].changestype_2_ElementsArray_and_Type = changestype_2_ElementsArray_and_Type;
	window["AscCommon"].changestype_2_AdditionalTypes        = changestype_2_AdditionalTypes;
	window["AscCommon"].contentchanges_Add                   = contentchanges_Add;
	window["AscCommon"].contentchanges_Remove                = contentchanges_Remove;

	window["AscCommon"].offlineMode = offlineMode;

	// ----------------------------- plugins ------------------------------- //
	var EPluginDataType =
		{
			none : "none",
			text : "text",
			ole  : "ole",
			html : "html"
		};

	window["Asc"]["EPluginDataType"] = window["Asc"].EPluginDataType = EPluginDataType;
	prot         = EPluginDataType;
	prot['none'] = prot.none;
	prot['text'] = prot.text;
	prot['ole']  = prot.ole;
	prot['html'] = prot.html;

	function CPluginVariation()
	{
		this.description = "";
		this.url         = "";
		this.baseUrl     = "";
		this.index       = 0;     // сверху не выставляем. оттуда в каком порядке пришли - в таком порядке и работают

		this.icons          = ["1x", "2x"];
		this.isViewer       = false;
		this.EditorsSupport = ["word", "cell", "slide"];

		this.isVisual     = false;      // визуальный ли
		this.isModal      = false;      // модальное ли окно (используется только для визуального)
		this.isInsideMode = false;      // отрисовка не в окне а внутри редактора (в панели) (используется только для визуального немодального)

		this.initDataType = EPluginDataType.none;
		this.initData     = "";

		this.isUpdateOleOnResize = false;

		this.buttons = [{"text" : "Ok", "primary" : true}, {"text" : "Cancel", "primary" : false}];
	}

	CPluginVariation.prototype["get_Description"] = function()
	{
		return this.description;
	};
	CPluginVariation.prototype["set_Description"] = function(value)
	{
		this.description = value;
	};
	CPluginVariation.prototype["get_Url"]         = function()
	{
		return this.url;
	};
	CPluginVariation.prototype["set_Url"]         = function(value)
	{
		this.url = value;
	};

	CPluginVariation.prototype["get_Icons"] = function()
	{
		return this.icons;
	};
	CPluginVariation.prototype["set_Icons"] = function(value)
	{
		this.icons = value;
	};

	CPluginVariation.prototype["get_Viewer"]         = function()
	{
		return this.isViewer;
	};
	CPluginVariation.prototype["set_Viewer"]         = function(value)
	{
		this.isViewer = value;
	};
	CPluginVariation.prototype["get_EditorsSupport"] = function()
	{
		return this.EditorsSupport;
	};
	CPluginVariation.prototype["set_EditorsSupport"] = function(value)
	{
		this.EditorsSupport = value;
	};


	CPluginVariation.prototype["get_Visual"]     = function()
	{
		return this.isVisual;
	};
	CPluginVariation.prototype["set_Visual"]     = function(value)
	{
		this.isVisual = value;
	};
	CPluginVariation.prototype["get_Modal"]      = function()
	{
		return this.isModal;
	};
	CPluginVariation.prototype["set_Modal"]      = function(value)
	{
		this.isModal = value;
	};
	CPluginVariation.prototype["get_InsideMode"] = function()
	{
		return this.isInsideMode;
	};
	CPluginVariation.prototype["set_InsideMode"] = function(value)
	{
		this.isInsideMode = value;
	};

	CPluginVariation.prototype["get_InitDataType"] = function()
	{
		return this.initDataType;
	};
	CPluginVariation.prototype["set_InitDataType"] = function(value)
	{
		this.initDataType = value;
	};
	CPluginVariation.prototype["get_InitData"]     = function()
	{
		return this.initData;
	};
	CPluginVariation.prototype["set_InitData"]     = function(value)
	{
		this.initData = value;
	};

	CPluginVariation.prototype["get_UpdateOleOnResize"] = function()
	{
		return this.isUpdateOleOnResize;
	};
	CPluginVariation.prototype["set_UpdateOleOnResize"] = function(value)
	{
		this.isUpdateOleOnResize = value;
	};
	CPluginVariation.prototype["get_Buttons"]           = function()
	{
		return this.buttons;
	};
	CPluginVariation.prototype["set_Buttons"]           = function(value)
	{
		this.buttons = value;
	};

	CPluginVariation.prototype["serialize"]   = function()
	{
		var _object            = {};
		_object["description"] = this.description;
		_object["url"]         = this.url;
		_object["index"]       = this.index;

		_object["icons"]          = this.icons;
		_object["isViewer"]       = this.isViewer;
		_object["EditorsSupport"] = this.EditorsSupport;

		_object["isVisual"]     = this.isVisual;
		_object["isModal"]      = this.isModal;
		_object["isInsideMode"] = this.isInsideMode;

		_object["initDataType"] = this.initDataType;
		_object["initData"]     = this.initData;

		_object["isUpdateOleOnResize"] = this.isUpdateOleOnResize;

		_object["buttons"] = this.buttons;
		return _object;
	}
	CPluginVariation.prototype["deserialize"] = function(_object)
	{
		this.description = (_object["description"] != null) ? _object["description"] : this.description;
		this.url         = (_object["url"] != null) ? _object["url"] : this.url;
		this.index       = (_object["index"] != null) ? _object["index"] : this.index;

		this.icons          = (_object["icons"] != null) ? _object["icons"] : this.icons;
		this.isViewer       = (_object["isViewer"] != null) ? _object["isViewer"] : this.isViewer;
		this.EditorsSupport = (_object["EditorsSupport"] != null) ? _object["EditorsSupport"] : this.EditorsSupport;

		this.isVisual     = (_object["isVisual"] != null) ? _object["isVisual"] : this.isVisual;
		this.isModal      = (_object["isModal"] != null) ? _object["isModal"] : this.isModal;
		this.isInsideMode = (_object["isInsideMode"] != null) ? _object["isInsideMode"] : this.isInsideMode;

		this.initDataType = (_object["initDataType"] != null) ? _object["initDataType"] : this.initDataType;
		this.initData     = (_object["initData"] != null) ? _object["initData"] : this.initData;

		this.isUpdateOleOnResize = (_object["isUpdateOleOnResize"] != null) ? _object["isUpdateOleOnResize"] : this.isUpdateOleOnResize;

		this.buttons = (_object["buttons"] != null) ? _object["buttons"] : this.buttons;
	}

	function CPlugin()
	{
		this.name    = "";
		this.guid    = "";
		this.baseUrl = "";

		this.variations = [];
	}

	CPlugin.prototype["get_Name"]    = function()
	{
		return this.name;
	};
	CPlugin.prototype["set_Name"]    = function(value)
	{
		this.name = value;
	};
	CPlugin.prototype["get_Guid"]    = function()
	{
		return this.guid;
	};
	CPlugin.prototype["set_Guid"]    = function(value)
	{
		this.guid = value;
	};
	CPlugin.prototype["get_BaseUrl"] = function()
	{
		return this.baseUrl;
	};
	CPlugin.prototype["set_BaseUrl"] = function(value)
	{
		this.baseUrl = value;
	};

	CPlugin.prototype["get_Variations"] = function()
	{
		return this.variations;
	};
	CPlugin.prototype["set_Variations"] = function(value)
	{
		this.variations = value;
	};

	CPlugin.prototype["serialize"]   = function()
	{
		var _object           = {};
		_object["name"]       = this.name;
		_object["guid"]       = this.guid;
		_object["baseUrl"]    = this.baseUrl;
		_object["variations"] = [];
		for (var i = 0; i < this.variations.length; i++)
		{
			_object["variations"].push(this.variations[i].serialize());
		}
		return _object;
	}
	CPlugin.prototype["deserialize"] = function(_object)
	{
		this.name       = (_object["name"] != null) ? _object["name"] : this.name;
		this.guid       = (_object["guid"] != null) ? _object["guid"] : this.guid;
		this.baseUrl    = (_object["baseUrl"] != null) ? _object["baseUrl"] : this.baseUrl;
		this.variations = [];
		for (var i = 0; i < _object["variations"].length; i++)
		{
			var _variation = new CPluginVariation();
			_variation["deserialize"](_object["variations"][i]);
			this.variations.push(_variation);
		}
	}

	window["Asc"]["CPluginVariation"] = window["Asc"].CPluginVariation = CPluginVariation;
	window["Asc"]["CPlugin"] = window["Asc"].CPlugin = CPlugin;
	// --------------------------------------------------------------------- //
})(window);

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

(/**
 * @param {Window} window
 * @param {undefined} undefined
 */
  function(window, undefined) {
  /**
   * Класс user для совместного редактирования/просмотра документа
   * -----------------------------------------------------------------------------
   *
   * @constructor
   * @memberOf Asc
   */
  function asc_CUser(val) {
    this.id = null;					// уникальный id - пользователя
    this.idOriginal = null;	// уникальный id - пользователя
    this.userName = null;		// имя пользователя
    this.state = undefined;	// состояние (true - подключен, false - отключился)
    this.indexUser = -1;		// Индекс пользователя (фактически равно числу заходов в документ на сервере)
    this.color = null;			// цвет пользователя
    this.view = false;			// просмотр(true), редактор(false)

    this._setUser(val);
    return this;
  }

  asc_CUser.prototype._setUser = function(val) {
    if (val) {
      this.id = val['id'];
      this.idOriginal = val['idOriginal'];
      this.userName = val['username'];
      this.indexUser = val['indexUser'];
      this.color = AscCommon.getUserColorById(this.idOriginal, this.userName, false, true);
      this.view = val['view'];
    }
  };
  asc_CUser.prototype.asc_getId = function() {
    return this.id;
  };
  asc_CUser.prototype.asc_getUserName = function() {
    return this.userName;
  };
  asc_CUser.prototype.asc_getState = function() {
    return this.state;
  };
  asc_CUser.prototype.asc_getColor = function() {
    return '#' + ('000000' + this.color.toString(16)).substr(-6);
  };
  asc_CUser.prototype.asc_getView = function() {
    return this.view;
  };
  asc_CUser.prototype.setId = function(val) {
    this.id = val;
  };
  asc_CUser.prototype.setUserName = function(val) {
    this.userName = val;
  };
  asc_CUser.prototype.setState = function(val) {
    this.state = val;
  };

  var ConnectionState = {
    Reconnect: -1,	// reconnect state
    None: 0,	// not initialized
    WaitAuth: 1,	// waiting session id
    Authorized: 2,	// authorized
    ClosedCoAuth: 3,	// closed coauthoring
    ClosedAll: 4,	// closed all

    SaveChanges: 10		// save
  };

  var c_oEditorId = {
    Word:0,
    Spreadsheet:1,
    Presentation:2
  };

  /*
   * Export
   * -----------------------------------------------------------------------------
   */
  var prot;
  window['AscCommon'] = window['AscCommon'] || {};
  window["AscCommon"].asc_CUser = asc_CUser;
  prot = asc_CUser.prototype;
  prot["asc_getId"] = prot.asc_getId;
  prot["asc_getUserName"] = prot.asc_getUserName;
  prot["asc_getState"] = prot.asc_getState;
  prot["asc_getColor"] = prot.asc_getColor;
  prot["asc_getView"] = prot.asc_getView;

  window["AscCommon"].ConnectionState = ConnectionState;
  window["AscCommon"].c_oEditorId = c_oEditorId;
})(window);
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

(function(window, undefined) {
  'use strict';

  var asc_coAuthV = '3.0.9';
  var ConnectionState = AscCommon.ConnectionState;
  var c_oEditorId = AscCommon.c_oEditorId;

  // Класс надстройка, для online и offline работы
  function CDocsCoApi(options) {
    this._CoAuthoringApi = new DocsCoApi();
    this._onlineWork = false;

    if (options) {
      this.onAuthParticipantsChanged = options.onAuthParticipantsChanged;
      this.onParticipantsChanged = options.onParticipantsChanged;
      this.onMessage = options.onMessage;
      this.onCursor =  options.onCursor;
      this.onLocksAcquired = options.onLocksAcquired;
      this.onLocksReleased = options.onLocksReleased;
      this.onLocksReleasedEnd = options.onLocksReleasedEnd; // ToDo переделать на массив release locks
      this.onDisconnect = options.onDisconnect;
      this.onWarning = options.onWarning;
      this.onFirstLoadChangesEnd = options.onFirstLoadChangesEnd;
      this.onConnectionStateChanged = options.onConnectionStateChanged;
      this.onSetIndexUser = options.onSetIndexUser;
      this.onSpellCheckInit = options.onSpellCheckInit;
      this.onSaveChanges = options.onSaveChanges;
      this.onStartCoAuthoring = options.onStartCoAuthoring;
      this.onEndCoAuthoring = options.onEndCoAuthoring;
      this.onUnSaveLock = options.onUnSaveLock;
      this.onRecalcLocks = options.onRecalcLocks;
      this.onDocumentOpen = options.onDocumentOpen;
      this.onFirstConnect = options.onFirstConnect;
      this.onLicense = options.onLicense;
    }
  }

  CDocsCoApi.prototype.init = function(user, docid, documentCallbackUrl, token, editorType, documentFormatSave) {
    if (this._CoAuthoringApi && this._CoAuthoringApi.isRightURL()) {
      var t = this;
      this._CoAuthoringApi.onAuthParticipantsChanged = function(e, count) {
        t.callback_OnAuthParticipantsChanged(e, count);
      };
      this._CoAuthoringApi.onParticipantsChanged = function(e, count) {
        t.callback_OnParticipantsChanged(e, count);
      };
      this._CoAuthoringApi.onMessage = function(e, clear) {
        t.callback_OnMessage(e, clear);
      };
      this._CoAuthoringApi.onCursor = function(e) {
        t.callback_OnCursor(e);
      };
      this._CoAuthoringApi.onLocksAcquired = function(e) {
        t.callback_OnLocksAcquired(e);
      };
      this._CoAuthoringApi.onLocksReleased = function(e, bChanges) {
        t.callback_OnLocksReleased(e, bChanges);
      };
      this._CoAuthoringApi.onLocksReleasedEnd = function() {
        t.callback_OnLocksReleasedEnd();
      };
      this._CoAuthoringApi.onDisconnect = function(e, isDisconnectAtAll, isCloseCoAuthoring) {
        t.callback_OnDisconnect(e, isDisconnectAtAll, isCloseCoAuthoring);
      };
      this._CoAuthoringApi.onWarning = function(e) {
        t.callback_OnWarning(e);
      };
      this._CoAuthoringApi.onFirstLoadChangesEnd = function() {
        t.callback_OnFirstLoadChangesEnd();
      };
      this._CoAuthoringApi.onConnectionStateChanged = function(e) {
        t.callback_OnConnectionStateChanged(e);
      };
      this._CoAuthoringApi.onSetIndexUser = function(e) {
        t.callback_OnSetIndexUser(e);
      };
      this._CoAuthoringApi.onSpellCheckInit = function(e) {
        t.callback_OnSpellCheckInit(e);
      };
      this._CoAuthoringApi.onSaveChanges = function(e, userId, bFirstLoad) {
        t.callback_OnSaveChanges(e, userId, bFirstLoad);
      };
      // Callback есть пользователей больше 1
      this._CoAuthoringApi.onStartCoAuthoring = function(e) {
        t.callback_OnStartCoAuthoring(e);
      };
      this._CoAuthoringApi.onEndCoAuthoring = function(e) {
        t.callback_OnEndCoAuthoring(e);
      };
      this._CoAuthoringApi.onUnSaveLock = function() {
        t.callback_OnUnSaveLock();
      };
      this._CoAuthoringApi.onRecalcLocks = function(e) {
        t.callback_OnRecalcLocks(e);
      };
      this._CoAuthoringApi.onDocumentOpen = function(data) {
        t.callback_OnDocumentOpen(data);
      };
      this._CoAuthoringApi.onFirstConnect = function() {
        t.callback_OnFirstConnect();
      };
      this._CoAuthoringApi.onLicense = function(res) {
        t.callback_OnLicense(res);
      };

      this._CoAuthoringApi.init(user, docid, documentCallbackUrl, token, editorType, documentFormatSave);
      this._onlineWork = true;
    } else {
      // Фиктивные вызовы
      this.onFirstConnect();
      this.onLicense(null);
    }
  };

  CDocsCoApi.prototype.getDocId = function() {
    if (this._CoAuthoringApi) {
      return this._CoAuthoringApi.getDocId()
    }
    return undefined;
  };
  CDocsCoApi.prototype.setDocId = function(docId) {
    if (this._CoAuthoringApi) {
      return this._CoAuthoringApi.setDocId(docId)
    }
  };

  CDocsCoApi.prototype.auth = function(isViewer, opt_openCmd) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.auth(isViewer, opt_openCmd);
    } else {
      // Фиктивные вызовы
      this.callback_OnSpellCheckInit('');
      this.callback_OnSetIndexUser('123');
      this.onFirstLoadChangesEnd();
    }
  };

  CDocsCoApi.prototype.set_url = function(url) {
    if (this._CoAuthoringApi) {
      this._CoAuthoringApi.set_url(url);
    }
  };

  CDocsCoApi.prototype.get_onlineWork = function() {
    return this._onlineWork;
  };

  CDocsCoApi.prototype.get_state = function() {
    if (this._CoAuthoringApi) {
      return this._CoAuthoringApi.get_state();
    }

    return 0;
  };

  CDocsCoApi.prototype.openDocument = function(data) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.openDocument(data);
    }
  };

  CDocsCoApi.prototype.sendRawData = function(data) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.sendRawData(data);
    }
  };

  CDocsCoApi.prototype.getMessages = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.getMessages();
    }
  };

  CDocsCoApi.prototype.sendMessage = function(message) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.sendMessage(message);
    }
  };

  CDocsCoApi.prototype.sendCursor = function(cursor) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.sendCursor(cursor);
    }
  };

  CDocsCoApi.prototype.sendChangesError = function(data) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.sendChangesError(data);
    }
  };

  CDocsCoApi.prototype.askLock = function(arrayBlockId, callback) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.askLock(arrayBlockId, callback);
    } else {
      var t = this;
      window.setTimeout(function() {
        if (callback && _.isFunction(callback)) {
          var lengthArray = (arrayBlockId) ? arrayBlockId.length : 0;
          if (0 < lengthArray) {
            callback({"lock": arrayBlockId[0]});
            // Фиктивные вызовы
            for (var i = 0; i < lengthArray; ++i) {
              t.callback_OnLocksAcquired({"state": 2, "block": arrayBlockId[i]});
            }
          }
        }
      }, 1);
    }
  };

  CDocsCoApi.prototype.askSaveChanges = function(callback) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.askSaveChanges(callback);
    } else {
      window.setTimeout(function() {
        if (callback && _.isFunction(callback)) {
          // Фиктивные вызовы
          callback({"saveLock": false});
        }
      }, 100);
    }
  };

  CDocsCoApi.prototype.unSaveLock = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.unSaveLock();
    } else {
      var t = this;
      window.setTimeout(function() {
        // Фиктивные вызовы
        t.callback_OnUnSaveLock();
      }, 100);
    }
  };

  CDocsCoApi.prototype.saveChanges = function(arrayChanges, deleteIndex, excelAdditionalInfo) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.saveChanges(arrayChanges, null, deleteIndex, excelAdditionalInfo);
    }
  };

  CDocsCoApi.prototype.unLockDocument = function(isSave) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.unLockDocument(isSave);
    }
  };

  CDocsCoApi.prototype.getUsers = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.getUsers();
    }
  };

  CDocsCoApi.prototype.getUserConnectionId = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      return this._CoAuthoringApi.getUserConnectionId();
    }
    return null;
  };
  
  CDocsCoApi.prototype.get_indexUser = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      return this._CoAuthoringApi.get_indexUser();
    }
    return null;
  };

  CDocsCoApi.prototype.get_isAuth = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      return this._CoAuthoringApi.get_isAuth();
    }
    return null;
  };

  CDocsCoApi.prototype.releaseLocks = function(blockId) {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.releaseLocks(blockId);
    }
  };

  CDocsCoApi.prototype.disconnect = function() {
    if (this._CoAuthoringApi && this._onlineWork) {
      this._CoAuthoringApi.disconnect();
    }
  };

  CDocsCoApi.prototype.callback_OnAuthParticipantsChanged = function(e, count) {
    if (this.onAuthParticipantsChanged) {
      this.onAuthParticipantsChanged(e, count);
    }
  };

  CDocsCoApi.prototype.callback_OnParticipantsChanged = function(e, count) {
    if (this.onParticipantsChanged) {
      this.onParticipantsChanged(e, count);
    }
  };

  CDocsCoApi.prototype.callback_OnMessage = function(e, clear) {
    if (this.onMessage) {
      this.onMessage(e, clear);
    }
  };

  CDocsCoApi.prototype.callback_OnCursor = function(e) {
    if (this.onCursor) {
      this.onCursor(e);
    }
  };

  CDocsCoApi.prototype.callback_OnLocksAcquired = function(e) {
    if (this.onLocksAcquired) {
      this.onLocksAcquired(e);
    }
  };

  CDocsCoApi.prototype.callback_OnLocksReleased = function(e, bChanges) {
    if (this.onLocksReleased) {
      this.onLocksReleased(e, bChanges);
    }
  };

  CDocsCoApi.prototype.callback_OnLocksReleasedEnd = function() {
    if (this.onLocksReleasedEnd) {
      this.onLocksReleasedEnd();
    }
  };

  /**
   * Event об отсоединении от сервера
   * @param {jQuery} e  event об отсоединении с причиной
   * @param {Bool} isDisconnectAtAll  окончательно ли отсоединяемся(true) или будем пробовать сделать reconnect(false) + сами отключились
   * @param {Bool} isCloseCoAuthoring
   */
  CDocsCoApi.prototype.callback_OnDisconnect = function(e, isDisconnectAtAll, isCloseCoAuthoring) {
    if (this.onDisconnect) {
      this.onDisconnect(e, isDisconnectAtAll, isCloseCoAuthoring);
    }
  };

  CDocsCoApi.prototype.callback_OnWarning = function(e) {
    if (this.onWarning) {
      this.onWarning(e);
    }
  };

  CDocsCoApi.prototype.callback_OnFirstLoadChangesEnd = function() {
    if (this.onFirstLoadChangesEnd) {
      this.onFirstLoadChangesEnd();
    }
  };

  CDocsCoApi.prototype.callback_OnConnectionStateChanged = function(e) {
    if (this.onConnectionStateChanged) {
      this.onConnectionStateChanged(e);
    }
  };

  CDocsCoApi.prototype.callback_OnSetIndexUser = function(e) {
    if (this.onSetIndexUser) {
      this.onSetIndexUser(e);
    }
  };
  CDocsCoApi.prototype.callback_OnSpellCheckInit = function(e) {
    if (this.onSpellCheckInit) {
      this.onSpellCheckInit(e);
    }
  };

  CDocsCoApi.prototype.callback_OnSaveChanges = function(e, userId, bFirstLoad) {
    if (this.onSaveChanges) {
      this.onSaveChanges(e, userId, bFirstLoad);
    }
  };
  CDocsCoApi.prototype.callback_OnStartCoAuthoring = function(e) {
    if (this.onStartCoAuthoring) {
      this.onStartCoAuthoring(e);
    }
  };
  CDocsCoApi.prototype.callback_OnEndCoAuthoring = function(e) {
    if (this.onEndCoAuthoring) {
      this.onEndCoAuthoring(e);
    }
  };

  CDocsCoApi.prototype.callback_OnUnSaveLock = function() {
    if (this.onUnSaveLock) {
      this.onUnSaveLock();
    }
  };

  CDocsCoApi.prototype.callback_OnRecalcLocks = function(e) {
    if (this.onRecalcLocks) {
      this.onRecalcLocks(e);
    }
  };
  CDocsCoApi.prototype.callback_OnDocumentOpen = function(e) {
    if (this.onDocumentOpen) {
      this.onDocumentOpen(e);
    }
  };
  CDocsCoApi.prototype.callback_OnFirstConnect = function() {
    if (this.onFirstConnect) {
      this.onFirstConnect();
    }
  };
  CDocsCoApi.prototype.callback_OnLicense = function(res) {
    if (this.onLicense) {
      this.onLicense(res);
    }
  };

  function LockBufferElement(arrayBlockId, callback) {
    this._arrayBlockId = arrayBlockId;
    this._callback = callback;
  }

  function DocsCoApi(options) {
    if (options) {
      this.onAuthParticipantsChanged = options.onAuthParticipantsChanged;
      this.onParticipantsChanged = options.onParticipantsChanged;
      this.onMessage = options.onMessage;
      this.onCursor = options.onCursor;
      this.onLocksAcquired = options.onLocksAcquired;
      this.onLocksReleased = options.onLocksReleased;
      this.onLocksReleasedEnd = options.onLocksReleasedEnd; // ToDo переделать на массив release locks
      this.onRelockFailed = options.onRelockFailed;
      this.onDisconnect = options.onDisconnect;
      this.onWarning = options.onWarning;
      this.onSetIndexUser = options.onSetIndexUser;
      this.onSpellCheckInit = options.onSpellCheckInit;
      this.onSaveChanges = options.onSaveChanges;
      this.onFirstLoadChangesEnd = options.onFirstLoadChangesEnd;
      this.onConnectionStateChanged = options.onConnectionStateChanged;
      this.onUnSaveLock = options.onUnSaveLock;
      this.onRecalcLocks = options.onRecalcLocks;
      this.onDocumentOpen = options.onDocumentOpen;
      this.onFirstConnect = options.onFirstConnect;
      this.onLicense = options.onLicense;
    }
    this._state = ConnectionState.None;
    // Online-пользователи в документе
    this._participants = {};
    this._countEditUsers = 0;
    this._countUsers = 0;

    this.isLicenseInit = false;
    this._locks = {};
    this._msgBuffer = [];
    this._lockCallbacks = {};
    this._lockCallbacksErrorTimerId = {};
    this._saveCallback = [];
    this.saveLockCallbackErrorTimeOutId = null;
    this.saveCallbackErrorTimeOutId = null;
    this.unSaveLockCallbackErrorTimeOutId = null;
    this._id = null;
    this._indexUser = -1;
    // Если пользователей больше 1, то совместно редактируем
    this.isCoAuthoring = false;
    // Мы сами отключились от совместного редактирования
    this.isCloseCoAuthoring = false;

    // Максимальное число изменений, посылаемое на сервер (не может быть нечетным, т.к. пересчет обоих индексов должен быть)
    this.maxCountSaveChanges = 20000;
    // Текущий индекс для колличества изменений
    this.currentIndex = 0;
    // Индекс, с которого мы начинаем сохранять изменения
    this.deleteIndex = 0;
    // Массив изменений
    this.arrayChanges = null;
    // Время последнего сохранения (для разрыва соединения)
    this.lastOtherSaveTime = -1;
    // Локальный индекс изменений
    this.changesIndex = 0;
    // Дополнительная информация для Excel
    this.excelAdditionalInfo = null;

    this._url = "";

    this.reconnectTimeout = null;
    this.attemptCount = 0;
    this.maxAttemptCount = 50;
    this.reconnectInterval = 2000;
    this.errorTimeOut = 10000;
    this.errorTimeOutSave = 60000;	// ToDo стоит переделать это, т.к. могут дублироваться изменения...

    this._docid = null;
    this._documentCallbackUrl = null;
    this._token = null;
    this._user = null;
    this._userId = "Anonymous";
    this.ownedLockBlocks = [];
    this.sockjs_url = null;
    this.sockjs = null;
    this.editorType = -1;
    this._isExcel = false;
    this._isPresentation = false;
    this._isAuth = false;
    this._documentFormatSave = 0;
    this._isViewer = false;
    this._isReSaveAfterAuth = false;	// Флаг для сохранения после повторной авторизации (для разрыва соединения во время сохранения)
    this._lockBuffer = [];
  }

  DocsCoApi.prototype.isRightURL = function() {
    return ("" != this._url);
  };

  DocsCoApi.prototype.set_url = function(url) {
    this._url = url;
  };

  DocsCoApi.prototype.get_state = function() {
    return this._state;
  };

  DocsCoApi.prototype.get_indexUser = function() {
    return this._indexUser;
  };

  DocsCoApi.prototype.get_isAuth = function() {
    return this._isAuth
  };

  DocsCoApi.prototype.getSessionId = function() {
    return this._id;
  };

  DocsCoApi.prototype.getUserConnectionId = function() {
    return this._userId;
  };

  DocsCoApi.prototype.getLocks = function() {
    return this._locks;
  };

  DocsCoApi.prototype._sendBufferedLocks = function() {
    var elem;
    for (var i = 0, length = this._lockBuffer.length; i < length; ++i) {
      elem = this._lockBuffer[i];
      this.askLock(elem._arrayBlockId, elem._callback);
    }
    this._lockBuffer = [];
  };

  DocsCoApi.prototype.askLock = function(arrayBlockId, callback) {
    if (ConnectionState.SaveChanges === this._state) {
      // Мы в режиме сохранения. Lock-и запросим после окончания.
      this._lockBuffer.push(new LockBufferElement(arrayBlockId, callback));
      return;
    }

    // ask all elements in array
    var t = this;
    var i = 0;
    var lengthArray = (arrayBlockId) ? arrayBlockId.length : 0;
    var isLock = false;
    var idLockInArray = null;
    for (; i < lengthArray; ++i) {
      idLockInArray = (this._isExcel || this._isPresentation) ? arrayBlockId[i]['guid'] : arrayBlockId[i];
      if (this._locks[idLockInArray] && 0 !== this._locks[idLockInArray].state) {
        isLock = true;
        break;
      }
    }
    if (0 === lengthArray) {
      isLock = true;
    }

    idLockInArray = (this._isExcel || this._isPresentation) ? arrayBlockId[0]['guid'] : arrayBlockId[0];

    if (!isLock) {
      if (this._lockCallbacksErrorTimerId.hasOwnProperty(idLockInArray)) {
        // Два раза для одного id нельзя запрашивать lock, не дождавшись ответа
        return;
      }
      //Ask
      this._locks[idLockInArray] = {'state': 1};//1-asked for block
      if (callback) {
        this._lockCallbacks[idLockInArray] = callback;

        //Set reconnectTimeout
        this._lockCallbacksErrorTimerId[idLockInArray] = window.setTimeout(function() {
          if (t._lockCallbacks.hasOwnProperty(idLockInArray)) {
            //Not signaled already
            t._lockCallbacks[idLockInArray]({error: 'Timed out'});
            delete t._lockCallbacks[idLockInArray];
            delete t._lockCallbacksErrorTimerId[idLockInArray];
          }
        }, this.errorTimeOut);
      }
      this._send({"type": 'getLock', 'block': arrayBlockId});
    } else {
      // Вернем ошибку, т.к. залочены элементы
      window.setTimeout(function() {
        if (callback && _.isFunction(callback)) {
          callback({error: idLockInArray + '-lock'});
        }
      }, 100);
    }
  };

  DocsCoApi.prototype.askSaveChanges = function(callback) {
    if (this._saveCallback[this._saveCallback.length - 1]) {
      // Мы еще не отработали старый callback и ждем ответа
      return;
    }

    // Очищаем предыдущий таймер
    if (null !== this.saveLockCallbackErrorTimeOutId) {
      clearTimeout(this.saveLockCallbackErrorTimeOutId);
    }

    // Проверим состояние, если мы не подсоединились, то сразу отправим ошибку
    if (ConnectionState.Authorized !== this._state) {
      this.saveLockCallbackErrorTimeOutId = window.setTimeout(function() {
        if (callback && _.isFunction(callback)) {
          // Фиктивные вызовы
          callback({error: "No connection"});
        }
      }, 100);
      return;
    }
    if (callback && _.isFunction(callback)) {
      var t = this;
      var indexCallback = this._saveCallback.length;
      this._saveCallback[indexCallback] = callback;

      //Set reconnectTimeout
      this.saveLockCallbackErrorTimeOutId = window.setTimeout(function() {
        t.saveLockCallbackErrorTimeOutId = null;
        var oTmpCallback = t._saveCallback[indexCallback];
        if (oTmpCallback) {
          t._saveCallback[indexCallback] = null;
          //Not signaled already
          oTmpCallback({error: "Timed out"});
        }
      }, this.errorTimeOut);
    }
    this._send({"type": "isSaveLock"});
  };

  DocsCoApi.prototype.unSaveLock = function() {
    // ToDo при разрыве соединения нужно перестать делать unSaveLock!
    var t = this;
    this.unSaveLockCallbackErrorTimeOutId = window.setTimeout(function() {
      t.unSaveLockCallbackErrorTimeOutId = null;
      t.unSaveLock();
    }, this.errorTimeOut);
    this._send({"type": "unSaveLock"});
  };

  DocsCoApi.prototype.releaseLocks = function(blockId) {
    if (this._locks[blockId] && 2 === this._locks[blockId].state /*lock is ours*/) {
      //Ask
      this._locks[blockId] = {"state": 0};//0-released
    }
  };

  DocsCoApi.prototype._reSaveChanges = function() {
    this.saveChanges(this.arrayChanges, this.currentIndex);
  };

  DocsCoApi.prototype.saveChanges = function(arrayChanges, currentIndex, deleteIndex, excelAdditionalInfo) {
    if (null === currentIndex) {
      this.deleteIndex = deleteIndex;
      if (null != this.deleteIndex && -1 !== this.deleteIndex) {
        this.deleteIndex += this.changesIndex;
      }
      this.currentIndex = 0;
      this.arrayChanges = arrayChanges;
      this.excelAdditionalInfo = excelAdditionalInfo;
    } else {
      this.currentIndex = currentIndex;
    }
    var startIndex = this.currentIndex * this.maxCountSaveChanges;
    var endIndex = Math.min(this.maxCountSaveChanges * (this.currentIndex + 1), arrayChanges.length);
    if (endIndex === arrayChanges.length) {
      for (var key in this._locks) if (this._locks.hasOwnProperty(key)) {
        if (2 === this._locks[key].state /*lock is ours*/) {
          delete this._locks[key];
        }
      }
    }

    //Set errorTimeout
    var t = this;
    this.saveCallbackErrorTimeOutId = window.setTimeout(function() {
      t.saveCallbackErrorTimeOutId = null;
      t._reSaveChanges();
    }, this.errorTimeOutSave);

    // Выставляем состояние сохранения
    this._state = ConnectionState.SaveChanges;

    this._send({'type': 'saveChanges', 'changes': JSON.stringify(arrayChanges.slice(startIndex, endIndex)),
      'startSaveChanges': (startIndex === 0), 'endSaveChanges': (endIndex === arrayChanges.length),
      'isCoAuthoring': this.isCoAuthoring, 'isExcel': this._isExcel, 'deleteIndex': this.deleteIndex,
      'excelAdditionalInfo': this.excelAdditionalInfo ? JSON.stringify(this.excelAdditionalInfo) : null});
  };

  DocsCoApi.prototype.unLockDocument = function(isSave) {
    this._send({'type': 'unLockDocument', 'isSave': isSave});
  };

  DocsCoApi.prototype.getUsers = function() {
    // Специально для возможности получения после прохождения авторизации (Стоит переделать)
    if (this.onAuthParticipantsChanged) {
      this.onAuthParticipantsChanged(this._participants, this._countUsers);
    }
  };

  DocsCoApi.prototype.disconnect = function() {
    // Отключаемся сами
    this.isCloseCoAuthoring = true;
    this._send({"type": "close"});
    this._state = ConnectionState.ClosedCoAuth;
  };

  DocsCoApi.prototype.openDocument = function(data) {
    this._send({"type": "openDocument", "message": data});
  };

  DocsCoApi.prototype.sendRawData = function(data) {
    this._sendRaw(data);
  };

  DocsCoApi.prototype.getMessages = function() {
    this._send({"type": "getMessages"});
  };

  DocsCoApi.prototype.sendMessage = function(message) {
    if (typeof message === 'string') {
      this._send({"type": "message", "message": message});
    }
  };

  DocsCoApi.prototype.sendCursor = function(cursor) {
    if (typeof cursor === 'string') {
      this._send({"type": "cursor", "cursor": cursor});
    }
  };

  DocsCoApi.prototype.sendChangesError = function(data) {
    if (typeof data === 'string') {
      this._send({'type': 'changesError', 'stack': data});
    }
  };

  DocsCoApi.prototype._sendPrebuffered = function() {
    for (var i = 0; i < this._msgBuffer.length; i++) {
      this._sendRaw(this._msgBuffer[i]);
    }
    this._msgBuffer = [];
  };

  DocsCoApi.prototype._send = function(data) {
    if (data !== null && typeof data === "object") {
      if (this._state > 0) {
        this.sockjs.send(JSON.stringify(data));
      } else {
        this._msgBuffer.push(JSON.stringify(data));
      }
    }
  };

  DocsCoApi.prototype._sendRaw = function(data) {
    if (data !== null && typeof data === "string") {
      if (this._state > 0) {
        this.sockjs.send(data);
      } else {
        this._msgBuffer.push(data);
      }
    }
  };

  DocsCoApi.prototype._onMessages = function(data, clear) {
    if (data["messages"] && this.onMessage) {
      this.onMessage(data["messages"], clear);
    }
  };

  DocsCoApi.prototype._onCursor = function(data) {
    if (data["messages"] && this.onCursor) {
      this.onCursor(data["messages"]);
    }
  };

  DocsCoApi.prototype._onGetLock = function(data) {
    if (data["locks"]) {
      for (var key in data["locks"]) {
        if (data["locks"].hasOwnProperty(key)) {
          var lock = data["locks"][key], blockTmp = (this._isExcel || this._isPresentation) ? lock["block"]["guid"] : key, blockValue = (this._isExcel || this._isPresentation) ? lock["block"] : key;
          if (lock !== null) {
            var changed = true;
            if (this._locks[blockTmp] && 1 !== this._locks[blockTmp].state /*asked for it*/) {
              //Exists
              //Check lock state
              changed = !(this._locks[blockTmp].state === (lock["sessionId"] === this._id ? 2 : 3) && this._locks[blockTmp]["user"] === lock["user"] && this._locks[blockTmp]["time"] === lock["time"] && this._locks[blockTmp]["block"] === blockTmp);
            }

            if (changed) {
              this._locks[blockTmp] = {"state": lock["sessionId"] === this._id ? 2 : 3, "user": lock["user"], "time": lock["time"], "block": blockTmp, "blockValue": blockValue};//2-acquired by me!
            }
            if (this._lockCallbacks.hasOwnProperty(blockTmp) && this._lockCallbacks[blockTmp] !== null && _.isFunction(this._lockCallbacks[blockTmp])) {
              if (lock["sessionId"] === this._id) {
                //Do call back
                this._lockCallbacks[blockTmp]({"lock": this._locks[blockTmp]});
              } else {
                this._lockCallbacks[blockTmp]({"error": "Already locked by " + lock["user"]});
              }
              if (this._lockCallbacksErrorTimerId.hasOwnProperty(blockTmp)) {
                clearTimeout(this._lockCallbacksErrorTimerId[blockTmp]);
                delete this._lockCallbacksErrorTimerId[blockTmp];
              }
              delete this._lockCallbacks[blockTmp];
            }
            if (this.onLocksAcquired && changed) {
              this.onLocksAcquired(this._locks[blockTmp]);
            }
          }
        }
      }
    }
  };

  DocsCoApi.prototype._onReleaseLock = function(data) {
    if (data["locks"]) {
      var bSendEnd = false;
      for (var block in data["locks"]) {
        if (data["locks"].hasOwnProperty(block)) {
          var lock = data["locks"][block], blockTmp = (this._isExcel || this._isPresentation) ? lock["block"]["guid"] : lock["block"];
          if (lock !== null) {
            this._locks[blockTmp] = {"state": 0, "user": lock["user"], "time": lock["time"], "changes": lock["changes"], "block": lock["block"]};
            if (this.onLocksReleased) {
              // false - user not save changes
              this.onLocksReleased(this._locks[blockTmp], false);
              bSendEnd = true;
            }
          }
        }
      }
      if (bSendEnd && this.onLocksReleasedEnd) {
        this.onLocksReleasedEnd();
      }
    }
  };

  DocsCoApi.prototype._documentOpen = function(data) {
    this.onDocumentOpen(data);
  };

  DocsCoApi.prototype._onSaveChanges = function(data) {
    if (data["locks"]) {
      var bSendEnd = false;
      for (var block in data["locks"]) {
        if (data["locks"].hasOwnProperty(block)) {
          var lock = data["locks"][block], blockTmp = (this._isExcel || this._isPresentation) ? lock["block"]["guid"] : lock["block"];
          if (lock !== null) {
            this._locks[blockTmp] = {"state": 0, "user": lock["user"], "time": lock["time"], "changes": lock["changes"], "block": lock["block"]};
            if (this.onLocksReleased) {
              // true - lock with save
              this.onLocksReleased(this._locks[blockTmp], true);
              bSendEnd = true;
            }
          }
        }
      }
      if (bSendEnd && this.onLocksReleasedEnd) {
        this.onLocksReleasedEnd();
      }
    }
    this._updateChanges(data["changes"], data["changesIndex"], false);

    if (this.onRecalcLocks) {
      this.onRecalcLocks(data["excelAdditionalInfo"]);
    }
  };

  DocsCoApi.prototype._onStartCoAuthoring = function(isStartEvent) {
    if (false === this.isCoAuthoring) {
      this.isCoAuthoring = true;
      if (this.onStartCoAuthoring) {
        this.onStartCoAuthoring(isStartEvent);
      }
    }
  };

  DocsCoApi.prototype._onEndCoAuthoring = function(isStartEvent) {
    if (true === this.isCoAuthoring) {
      this.isCoAuthoring = false;
      if (this.onEndCoAuthoring) {
        this.onEndCoAuthoring(isStartEvent);
      }
    }
  };

  DocsCoApi.prototype._onSaveLock = function(data) {
    if (undefined != data["saveLock"] && null != data["saveLock"]) {
      var indexCallback = this._saveCallback.length - 1;
      var oTmpCallback = this._saveCallback[indexCallback];
      if (oTmpCallback) {
        // Очищаем предыдущий таймер
        if (null !== this.saveLockCallbackErrorTimeOutId) {
          clearTimeout(this.saveLockCallbackErrorTimeOutId);
          this.saveLockCallbackErrorTimeOutId = null;
        }

        this._saveCallback[indexCallback] = null;
        oTmpCallback(data);
      }
    }
  };

  DocsCoApi.prototype._onUnSaveLock = function(data) {
    // Очищаем предыдущий таймер сохранения
    if (null !== this.saveCallbackErrorTimeOutId) {
      clearTimeout(this.saveCallbackErrorTimeOutId);
      this.saveCallbackErrorTimeOutId = null;
    }
    // Очищаем предыдущий таймер снятия блокировки
    if (null !== this.unSaveLockCallbackErrorTimeOutId) {
      clearTimeout(this.unSaveLockCallbackErrorTimeOutId);
      this.unSaveLockCallbackErrorTimeOutId = null;
    }

    // Возвращаем состояние
    this._state = ConnectionState.Authorized;

    // Делаем отложенные lock-и
    this._sendBufferedLocks();

    if (-1 !== data['index']) {
      this.changesIndex = data['index'];
    }

    if (this.onUnSaveLock) {
      this.onUnSaveLock();
    }
  };

  DocsCoApi.prototype._updateChanges = function(allServerChanges, changesIndex, bFirstLoad) {
    if (this.onSaveChanges) {
      this.changesIndex = changesIndex;
      if (allServerChanges) {
        for (var i = 0; i < allServerChanges.length; ++i) {
          var change = allServerChanges[i];
          var changesOneUser = change['change'];
          if (changesOneUser) {
            if (change['user'] !== this._userId) {
              this.lastOtherSaveTime = change['time'];
            }
            this.onSaveChanges(JSON.parse(changesOneUser), change['useridoriginal'], bFirstLoad);
          }
        }
      }
    }
  };

  DocsCoApi.prototype._onSetIndexUser = function(data) {
    if (this.onSetIndexUser) {
      this.onSetIndexUser(data);
    }
  };
  DocsCoApi.prototype._onSpellCheckInit = function(data) {
    if (this.onSpellCheckInit) {
      this.onSpellCheckInit(data);
    }
  };

  DocsCoApi.prototype._onSavePartChanges = function(data) {
    // Очищаем предыдущий таймер
    if (null !== this.saveCallbackErrorTimeOutId) {
      clearTimeout(this.saveCallbackErrorTimeOutId);
      this.saveCallbackErrorTimeOutId = null;
    }

    if (-1 !== data['changesIndex']) {
      this.changesIndex = data['changesIndex'];
    }

    this.saveChanges(this.arrayChanges, this.currentIndex + 1);
  };

  DocsCoApi.prototype._onPreviousLocks = function(locks, previousLocks) {
    var i = 0;
    if (locks && previousLocks) {
      for (var block in locks) {
        if (locks.hasOwnProperty(block)) {
          var lock = locks[block];
          if (lock !== null && lock["block"]) {
            //Find in previous
            for (i = 0; i < previousLocks.length; i++) {
              if (previousLocks[i] === lock["block"] && lock["sessionId"] === this._id) {
                //Lock is ours
                previousLocks.remove(i);
                break;
              }
            }
          }
        }
      }
      if (previousLocks.length > 0 && this.onRelockFailed) {
        this.onRelockFailed(previousLocks);
      }
      previousLocks = [];
    }
  };

  DocsCoApi.prototype._onAuthParticipantsChanged = function(participants) {
    this._participants = {};
    this._countEditUsers = 0;
    this._countUsers = 0;

    if (participants) {
      var tmpUser;
      for (var i = 0; i < participants.length; ++i) {
        tmpUser = new AscCommon.asc_CUser(participants[i]);
        this._participants[tmpUser.asc_getId()] = tmpUser;
        // Считаем только число редакторов
        if (!tmpUser.asc_getView()) {
          ++this._countEditUsers;
        }
        ++this._countUsers;
      }

      if (this.onAuthParticipantsChanged) {
        this.onAuthParticipantsChanged(this._participants, this._countUsers);
      }

      // Посылаем эвент о совместном редактировании
      if (1 < this._countEditUsers) {
        this._onStartCoAuthoring(/*isStartEvent*/true);
      } else {
        this._onEndCoAuthoring(/*isStartEvent*/true);
      }
    }
  };

  DocsCoApi.prototype._onConnectionStateChanged = function(data) {
    var userStateChanged = null, userId, stateChanged = false, isEditUser = true;
    if (this.onConnectionStateChanged) {
      userStateChanged = new AscCommon.asc_CUser(data['user']);
      userStateChanged.setState(data["state"]);

      userId = userStateChanged.asc_getId();
      isEditUser = !userStateChanged.asc_getView();
      if (userStateChanged.asc_getState()) {
        this._participants[userId] = userStateChanged;
        ++this._countUsers;
        if (isEditUser) {
          ++this._countEditUsers;
        }
        stateChanged = true;
      } else if (this._participants.hasOwnProperty(userId)) {
        delete this._participants[userId];
        --this._countUsers;
        if (isEditUser) {
          --this._countEditUsers;
        }
        stateChanged = true;
      }

      if (stateChanged) {
        // Посылаем эвент о совместном редактировании
        if (1 < this._countEditUsers) {
          this._onStartCoAuthoring(/*isStartEvent*/false);
        } else {
          this._onEndCoAuthoring(/*isStartEvent*/false);
        }

        this.onParticipantsChanged(this._participants, this._countUsers);
        this.onConnectionStateChanged(userStateChanged);
      }
    }
  };

  DocsCoApi.prototype._onDrop = function(data) {
    this.disconnect();
    this.onDisconnect(data ? data['description'] : '', true, this.isCloseCoAuthoring);
  };

  DocsCoApi.prototype._onWarning = function(data) {
    this.onWarning(data ? data['description'] : '');
  };

  DocsCoApi.prototype._onLicense = function(data) {
    if (!this.isLicenseInit) {
      this.isLicenseInit = true;
      this.onLicense(data['license']);
    }
  };

  DocsCoApi.prototype._onAuth = function(data) {
    var t = this;
    if (true === this._isAuth) {
      this._state = ConnectionState.Authorized;
      // Мы должны только соединиться для получения файла. Совместное редактирование уже было отключено.
      if (this.isCloseCoAuthoring)
        return;

      // Мы уже авторизовывались, нужно обновить пользователей (т.к. пользователи могли входить и выходить пока у нас не было соединения)
      this._onAuthParticipantsChanged(data['participants']);

      //if (this.ownedLockBlocks && this.ownedLockBlocks.length > 0) {
      //	this._onPreviousLocks(data["locks"], this.ownedLockBlocks);
      //}
      this._onMessages(data, true);
      this._onGetLock(data);

      if (this._isReSaveAfterAuth) {
        var callbackAskSaveChanges = function(e) {
          if (false === e["saveLock"]) {
            t._reSaveChanges();
          } else {
            setTimeout(function() {
              t.askSaveChanges(callbackAskSaveChanges);
            }, 1000);
          }
        };
        this.askSaveChanges(callbackAskSaveChanges);
      }

      return;
    }
    if (data['result'] === 1) {
      // Выставляем флаг, что мы уже авторизовывались
      this._isAuth = true;

      //TODO: add checks
      this._state = ConnectionState.Authorized;
      this._id = data['sessionId'];

      this._onAuthParticipantsChanged(data['participants']);

      this._onSpellCheckInit(data['g_cAscSpellCheckUrl']);
      this._onSetIndexUser(this._indexUser = data['indexUser']);
      this._userId = this._user.asc_getId() + this._indexUser;

      this._onMessages(data, false);
      this._onGetLock(data);

      // Применения изменений пользователя
      if (window['AscApplyChanges'] && window['AscChanges']) {
        var userOfflineChanges = window['AscChanges'], changeOneUser;
        for (var i = 0; i < userOfflineChanges.length; ++i) {
          changeOneUser = userOfflineChanges[i];
          for (var j = 0; j < changeOneUser.length; ++j)
            this.onSaveChanges(changeOneUser[j], null, true);
        }
      }
      this._updateChanges(data["changes"], data["changesIndex"], true);
      // Посылать нужно всегда, т.к. на это рассчитываем при открытии
      if (this.onFirstLoadChangesEnd) {
        this.onFirstLoadChangesEnd();
      }

      //Send prebuffered
      this._sendPrebuffered();
    }
    //TODO: Add errors
  };

  DocsCoApi.prototype.init = function(user, docid, documentCallbackUrl, token, editorType, documentFormatSave) {
    this._user = user;
    this._docid = null;
    this._documentCallbackUrl = documentCallbackUrl;
    this._token = token;
    this.ownedLockBlocks = [];
    this.sockjs_url = null;
    this.editorType = editorType;
    this._isExcel = c_oEditorId.Spreadsheet === editorType;
    this._isPresentation = c_oEditorId.Presentation === editorType;
    this._isAuth = false;
    this._documentFormatSave = documentFormatSave;

    this.setDocId(docid);
    this._initSocksJs();
  };
  DocsCoApi.prototype.getDocId = function() {
    return this._docid;
  };
  DocsCoApi.prototype.setDocId = function(docid) {
    //todo возможно надо менять sockjs_url
    this._docid = docid;
    this.sockjs_url = '/doc/' + docid + '/c';
  };
  // Авторизация (ее нужно делать после выставления состояния редактора view-mode)
  DocsCoApi.prototype.auth = function(isViewer, opt_openCmd) {
    this._isViewer = isViewer;
    if (this._locks) {
      this.ownedLockBlocks = [];
      //If we already have locks
      for (var block in this._locks) if (this._locks.hasOwnProperty(block)) {
        var lock = this._locks[block];
        if (lock["state"] === 2) {
          //Our lock.
          this.ownedLockBlocks.push(lock["blockValue"]);
        }
      }
      this._locks = {};
    }
    this._send({
      'type': 'auth',
      'docid': this._docid,
      'documentCallbackUrl': this._documentCallbackUrl,
      'token': this._token,
      'user': {
        'id': this._user.asc_getId(),
        'username': this._user.asc_getUserName(),
        'indexUser': this._indexUser
      },
      'editorType': this.editorType,
      'lastOtherSaveTime': this.lastOtherSaveTime,
      'block': this.ownedLockBlocks,
      'sessionId': this._id,
      'documentFormatSave': this._documentFormatSave,
      'view': this._isViewer,
      'isCloseCoAuthoring': this.isCloseCoAuthoring,
      'openCmd': opt_openCmd,
      'version': asc_coAuthV
    });
  };

  DocsCoApi.prototype._initSocksJs = function() {
    var t = this;
	//ограничиваем transports WebSocket и XHR / JSONP polling, как и engine.io https://github.com/socketio/engine.io
	//при переборе streaming transports у клиента с wirewall происходило зацикливание(не повторялось в версии sock.js 0.3.4)
	var sockjs = this.sockjs = new (this._getSockJs())(this.sockjs_url, null, {transports: ['websocket', 'xdr-polling', 'xhr-polling', 'iframe-xhr-polling', 'jsonp-polling']});

    sockjs.onopen = function() {
      if (t.reconnectTimeout) {
        clearTimeout(t.reconnectTimeout);
        t.reconnectTimeout = null;
        t.attemptCount = 0;
      }

      t._state = ConnectionState.WaitAuth;
        t.onFirstConnect();
    };
    sockjs.onmessage = function(e) {
      //TODO: add checks and error handling
      //Get data type
      var dataObject = JSON.parse(e.data);
      var type = dataObject['type'];
      switch (type) {
        case 'auth'        :
          t._onAuth(dataObject);
          break;
        case 'message'      :
          t._onMessages(dataObject, false);
          break;
        case 'cursor'       :
          t._onCursor(dataObject);
          break;
        case 'getLock'      :
          t._onGetLock(dataObject);
          break;
        case 'releaseLock'    :
          t._onReleaseLock(dataObject);
          break;
        case 'connectState'    :
          t._onConnectionStateChanged(dataObject);
          break;
        case 'saveChanges'    :
          t._onSaveChanges(dataObject);
          break;
        case 'saveLock'      :
          t._onSaveLock(dataObject);
          break;
        case 'unSaveLock'    :
          t._onUnSaveLock(dataObject);
          break;
        case 'savePartChanges'  :
          t._onSavePartChanges(dataObject);
          break;
        case 'drop'        :
          t._onDrop(dataObject);
          break;
        case 'waitAuth'      : /*Ждем, когда придет auth, документ залочен*/
          break;
        case 'error'      : /*Старая версия sdk*/
          t._onDrop(dataObject);
          break;
        case 'documentOpen'    :
          t._documentOpen(dataObject);
          break;
        case 'warning':
          t._onWarning(dataObject);
          break;
        case 'license':
          t._onLicense(dataObject);
      }
    };
    sockjs.onclose = function(evt) {
      if (ConnectionState.SaveChanges === t._state) {
        // Мы сохраняли изменения и разорвалось соединение
        t._isReSaveAfterAuth = true;
        // Очищаем предыдущий таймер
        if (null !== t.saveCallbackErrorTimeOutId) {
          clearTimeout(t.saveCallbackErrorTimeOutId);
        }
      }
      t._state = ConnectionState.Reconnect;
      var bIsDisconnectAtAll = (4001 === evt.code || t.attemptCount >= t.maxAttemptCount);
      if (bIsDisconnectAtAll) {
        t._state = ConnectionState.ClosedAll;
      }
      if (t.onDisconnect) {
        t.onDisconnect(evt.reason, bIsDisconnectAtAll, t.isCloseCoAuthoring);
      }
      //Try reconect
      if (!bIsDisconnectAtAll) {
        t._tryReconnect();
      }
    };

    return sockjs;
  };

  DocsCoApi.prototype._tryReconnect = function() {
    var t = this;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      t.reconnectTimeout = null;
    }
    ++this.attemptCount;
    this.reconnectTimeout = setTimeout(function() {
      delete t.sockjs;
      t._initSocksJs();
    }, this.reconnectInterval);

  };

  DocsCoApi.prototype._getSockJs = function() {
    return window['SockJS'] ? window['SockJS'] : require('sockjs');
  };

  //----------------------------------------------------------export----------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window['AscCommon'].CDocsCoApi = CDocsCoApi;
})(window);
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

(	/**
	 * @param {Window} window
	 * @param {undefined} undefined
	 */
	function (window, undefined) {
      // Import
      var prot;
      var c_oAscMouseMoveDataTypes = AscCommon.c_oAscMouseMoveDataTypes;

      var c_oAscColor = Asc.c_oAscColor;
      var c_oAscFill = Asc.c_oAscFill;
      var c_oAscFillGradType = Asc.c_oAscFillGradType;
      var c_oAscFillBlipType = Asc.c_oAscFillBlipType;
      var c_oAscStrokeType = Asc.c_oAscStrokeType;
      var c_oAscChartTypeSettings = Asc.c_oAscChartTypeSettings;
      var c_oAscTickMark = Asc.c_oAscTickMark;
      var c_oAscAxisType = Asc.c_oAscAxisType;
      var c_oAscDropCap = Asc.c_oAscDropCap;
      // ---------------------------------------------------------------------------------------------------------------

      var c_oAscArrUserColors = [16757719, 7929702, 56805, 10081791, 12884479, 16751001, 6748927, 16762931, 6865407,
          15650047, 16737894, 3407768, 16759142, 10852863, 6750176, 16774656, 13926655, 13815039, 3397375, 11927347,
          16752947, 9404671, 4980531, 16744678, 3407830, 15919360, 16731553, 52479, 13330175, 16743219, 3386367, 14221056,
          16737966, 1896960, 65484, 10970879, 16759296, 16711680, 13496832, 62072, 49906, 16734720, 10682112, 7890687,
          16731610, 65406, 38655, 16747008, 59890, 12733951, 15859712, 47077, 15050496, 15224319, 10154496, 58807, 16724950,
          1759488, 9981439, 15064320, 15893248, 16724883, 58737, 15007744, 36594, 12772608, 12137471, 6442495, 15039488,
          16718470, 14274816, 53721, 16718545, 1625088, 15881472, 13419776, 32985, 16711800, 1490688, 16711884, 8991743,
          13407488, 41932, 7978752, 15028480, 52387, 15007927, 12114176, 1421824, 55726, 13041893, 10665728, 30924, 49049,
          14241024, 36530, 11709440, 13397504, 45710, 34214];

      function CreateAscColorCustom(r, g, b, auto)
      {
          var ret = new asc_CColor();
          ret.type = c_oAscColor.COLOR_TYPE_SRGB;
          ret.r = r;
          ret.g = g;
          ret.b = b;
          ret.a = 255;
          ret.Auto = ( undefined === auto ? false : auto );
          return ret;
      }

      function CreateAscColor(unicolor)
      {
          if (null == unicolor || null == unicolor.color)
              return new asc_CColor();

          var ret = new asc_CColor();
          ret.r = unicolor.RGBA.R;
          ret.g = unicolor.RGBA.G;
          ret.b = unicolor.RGBA.B;
          ret.a = unicolor.RGBA.A;

          var _color = unicolor.color;
          switch (_color.type)
          {
              case c_oAscColor.COLOR_TYPE_SRGB:
              case c_oAscColor.COLOR_TYPE_SYS:
              {
                  break;
              }
              case c_oAscColor.COLOR_TYPE_PRST:
              case c_oAscColor.COLOR_TYPE_SCHEME:
              {
                  ret.type = _color.type;
                  ret.value = _color.id;
                  break;
              }
              default:
                  break;
          }
          return ret;
      }

    /**
     * Класс asc_CAscEditorPermissions для прав редакторов
     * -----------------------------------------------------------------------------
     *
     * @constructor
     * @memberOf Asc
     */
    function asc_CAscEditorPermissions() {
        this.canLicense = false;
        this.isLight = false;
        this.canCoAuthoring = true;
        this.canReaderMode = true;
        this.canBranding = false;
        this.isAutosaveEnable = true;
        this.AutosaveMinInterval = 300;
        this.isAnalyticsEnable = false;
        return this;
    }
    asc_CAscEditorPermissions.prototype.asc_getCanLicense = function(){ return this.canLicense; };
    asc_CAscEditorPermissions.prototype.asc_getCanCoAuthoring = function(){ return this.canCoAuthoring; };
    asc_CAscEditorPermissions.prototype.asc_getCanReaderMode = function(){ return this.canReaderMode; };
    asc_CAscEditorPermissions.prototype.asc_getCanBranding = function(){ return this.canBranding; };
    asc_CAscEditorPermissions.prototype.asc_getIsAutosaveEnable = function(){ return this.isAutosaveEnable; };
    asc_CAscEditorPermissions.prototype.asc_getAutosaveMinInterval = function(){ return this.AutosaveMinInterval; };
    asc_CAscEditorPermissions.prototype.asc_getIsAnalyticsEnable = function(){ return this.isAnalyticsEnable; };
    asc_CAscEditorPermissions.prototype.asc_getIsLight = function(){ return this.isLight; };

    asc_CAscEditorPermissions.prototype.asc_setCanLicense = function(v){ this.canLicense = v; };
    asc_CAscEditorPermissions.prototype.asc_setCanBranding = function(v){ this.canBranding = v; };
    asc_CAscEditorPermissions.prototype.asc_setIsLight = function(v){ this.isLight = v; };

      /** @constructor */
      function asc_ValAxisSettings()
      {
          this.minValRule       = null;
          this.minVal            = null;
          this.maxValRule       = null;
          this.maxVal            = null;
          this.invertValOrder   = null;
          this.logScale          = null;
          this.logBase          = null;

          this.dispUnitsRule    = null;
          this.units            = null;



          this.showUnitsOnChart = null;
          this.majorTickMark      = null;
          this.minorTickMark      = null;
          this.tickLabelsPos      = null;
          this.crossesRule        = null;
          this.crosses            = null;
          this.axisType           = c_oAscAxisType.val;
      }
      asc_ValAxisSettings.prototype =
      {

          putAxisType: function(v)
          {
              this.axisType = v;
          },

          putMinValRule: function(v)
          {
              this.minValRule = v;
          },
          putMinVal: function(v)
          {
              this.minVal = v;
          },
          putMaxValRule: function(v)
          {
              this.maxValRule = v;
          },
          putMaxVal: function(v)
          {
              this.maxVal = v;
          },
          putInvertValOrder: function(v)
          {
              this.invertValOrder =  v;
          },
          putLogScale: function(v)
          {
              this.logScale =  v;
          },
          putLogBase: function(v)
          {
              this.logBase =  v;
          },
          putUnits: function(v)
          {
              this.units = v;
          },
          putShowUnitsOnChart: function(v)
          {
              this.showUnitsOnChart =  v;
          },
          putMajorTickMark: function(v)
          {
              this.majorTickMark =  v;
          },
          putMinorTickMark: function(v)
          {
              this.minorTickMark =  v;
          },
          putTickLabelsPos: function(v)
          {
              this.tickLabelsPos =  v;
          },
          putCrossesRule: function(v)
          {
              this.crossesRule =  v;
          },
          putCrosses: function(v)
          {
              this.crosses =  v;
          },



          putDispUnitsRule: function(v)
          {
              this.dispUnitsRule = v;
          },

          getAxisType: function()
          {
              return this.axisType;
          },

          getDispUnitsRule: function()
          {
              return this.dispUnitsRule;
          },

          getMinValRule: function()
          {
              return this.minValRule;
          },
          getMinVal: function()
          {
              return this.minVal;
          },
          getMaxValRule: function()
          {
              return this.maxValRule;
          },
          getMaxVal: function()
          {
              return this.maxVal;
          },
          getInvertValOrder: function()
          {
              return this.invertValOrder;
          },
          getLogScale: function()
          {
              return this.logScale;
          },
          getLogBase: function()
          {
              return this.logBase;
          },
          getUnits: function()
          {
              return this.units;
          },
          getShowUnitsOnChart: function()
          {
              return this.showUnitsOnChart;
          },
          getMajorTickMark: function()
          {
              return this.majorTickMark;
          },
          getMinorTickMark: function()
          {
              return this.minorTickMark;
          },
          getTickLabelsPos: function()
          {
              return this.tickLabelsPos;
          },
          getCrossesRule: function()
          {
              return this.crossesRule;
          },
          getCrosses: function()
          {
              return this.crosses;
          },
          setDefault: function()
          {
              this.putMinValRule(Asc.c_oAscValAxisRule.auto);
              this.putMaxValRule(Asc.c_oAscValAxisRule.auto);
              this.putTickLabelsPos(Asc.c_oAscTickLabelsPos.TICK_LABEL_POSITION_NEXT_TO);
              this.putInvertValOrder(false);
              this.putDispUnitsRule(Asc.c_oAscValAxUnits.none);
              this.putMajorTickMark(c_oAscTickMark.TICK_MARK_OUT);
              this.putMinorTickMark(c_oAscTickMark.TICK_MARK_NONE);
              this.putCrossesRule(Asc.c_oAscCrossesRule.auto);
          }
      };

      /** @constructor */
      function asc_CatAxisSettings()
      {
          this.intervalBetweenTick       = null;
          this.intervalBetweenLabelsRule = null;
          this.intervalBetweenLabels     = null;
          this.invertCatOrder            = null;
          this.labelsAxisDistance        = null;
          this.majorTickMark             = null;
          this.minorTickMark             = null;
          this.tickLabelsPos             = null;
          this.crossesRule               = null;
          this.crosses                   = null;
          this.labelsPosition            = null;
          this.axisType                  = c_oAscAxisType.cat;
          this.crossMinVal               = null;
          this.crossMaxVal               = null;
      }
      asc_CatAxisSettings.prototype =
      {

          putIntervalBetweenTick: function(v)
          {
              this.intervalBetweenTick = v;
          },
          putIntervalBetweenLabelsRule: function(v)
          {
              this.intervalBetweenLabelsRule = v;
          },
          putIntervalBetweenLabels: function(v)
          {
              this.intervalBetweenLabels = v;
          },
          putInvertCatOrder: function(v)
          {
              this.invertCatOrder = v;
          },
          putLabelsAxisDistance: function(v)
          {
              this.labelsAxisDistance = v;
          },
          putMajorTickMark: function(v)
          {
              this.majorTickMark = v;
          },
          putMinorTickMark: function(v)
          {
              this.minorTickMark = v;
          },
          putTickLabelsPos: function(v)
          {
              this.tickLabelsPos = v;
          },
          putCrossesRule: function(v)
          {
              this.crossesRule = v;
          },
          putCrosses: function(v)
          {
              this.crosses = v;
          },

          putAxisType: function(v)
          {
              this.axisType = v;
          },

          putLabelsPosition: function(v)
          {
              this.labelsPosition = v;
          },

          getIntervalBetweenTick: function(v)
          {
              return this.intervalBetweenTick;
          },

          getIntervalBetweenLabelsRule: function()
          {
              return this.intervalBetweenLabelsRule ;
          },
          getIntervalBetweenLabels: function()
          {
              return this.intervalBetweenLabels ;
          },
          getInvertCatOrder: function()
          {
              return this.invertCatOrder ;
          },
          getLabelsAxisDistance: function()
          {
              return this.labelsAxisDistance ;
          },
          getMajorTickMark: function()
          {
              return this.majorTickMark ;
          },
          getMinorTickMark: function()
          {
              return this.minorTickMark ;
          },
          getTickLabelsPos: function()
          {
              return this.tickLabelsPos;
          },
          getCrossesRule: function()
          {
              return this.crossesRule ;
          },
          getCrosses: function()
          {
              return this.crosses;
          },

          getAxisType: function()
          {
              return this.axisType;
          },

          getLabelsPosition: function()
          {
              return this.labelsPosition;
          },

          getCrossMinVal: function()
          {
              return this.crossMinVal;
          },

          getCrossMaxVal: function()
          {
              return this.crossMaxVal;
          },



          putCrossMinVal: function(val)
          {
              this.crossMinVal = val;
          },

          putCrossMaxVal: function(val)
          {
              this.crossMaxVal = val;
          },

          setDefault: function()
          {
              this.putIntervalBetweenLabelsRule(Asc.c_oAscBetweenLabelsRule.auto);
              this.putLabelsPosition(Asc.c_oAscLabelsPosition.betweenDivisions);
              this.putTickLabelsPos(Asc.c_oAscTickLabelsPos.TICK_LABEL_POSITION_NEXT_TO);
              this.putLabelsAxisDistance(100);
              this.putMajorTickMark(c_oAscTickMark.TICK_MARK_OUT);
              this.putMinorTickMark(c_oAscTickMark.TICK_MARK_NONE);
              this.putIntervalBetweenTick(1);
              this.putCrossesRule(Asc.c_oAscCrossesRule.auto);
          }
      };

      /** @constructor */
      function asc_ChartSettings()
      {
          this.style         = null;
          this.title         = null;
          this.rowCols       = null;
          this.horAxisLabel  = null;
          this.vertAxisLabel = null;
          this.legendPos     = null;
          this.dataLabelsPos = null;
          this.vertAx        = null;
          this.horAx         = null;
          this.horGridLines  = null;
          this.vertGridLines = null;
          this.type = null;
          this.showSerName = null;
          this.showCatName = null;
          this.showVal    = null;
          this.separator = null;
          this.horAxisProps = null;
          this.vertAxisProps = null;
          this.range = null;
          this.inColumns = null;

          this.showMarker = null;
          this.bLine = null;
          this.smooth = null;
          this.showHorAxis = null;
          this.showVerAxis = null;
      }
      asc_ChartSettings.prototype =
      {
          putShowMarker: function(v)
          {
              this.showMarker = v;
          },

          getShowMarker: function()
          {
              return this.showMarker;
          },

          putLine: function(v)
          {
              this.bLine = v;
          },

          getLine: function()
          {
              return this.bLine;
          },


          putSmooth: function(v)
          {
              this.smooth = v;
          },

          getSmooth: function()
          {
              return this.smooth;
          },

          putStyle: function(index)
          {
              this.style = parseInt(index, 10);
          },

          getStyle: function()
          {
              return this.style;
          },

          putRange: function(range)
          {
              this.range = range;
          },

          getRange: function()
          {
              return this.range;
          },

          putInColumns: function(inColumns)
          {
              this.inColumns = inColumns;
          },

          getInColumns: function()
          {
              return this.inColumns;
          },

          putTitle: function(v)
          {
              this.title = v;
          },

          getTitle: function()
          {
              return this.title;
          },

          putRowCols: function(v)
          {
              this.rowCols = v;
          },

          getRowCols: function()
          {
              return this.rowCols;
          },

          putHorAxisLabel: function(v)
          {
              this.horAxisLabel = v;
          },
          putVertAxisLabel: function(v)
          {
              this.vertAxisLabel = v;
          },
          putLegendPos: function(v)
          {
              this.legendPos = v;
          },
          putDataLabelsPos: function(v)
          {
              this.dataLabelsPos = v;
          },
          putCatAx: function(v)
          {
              this.vertAx = v;
          },
          putValAx: function(v)
          {
              this.horAx = v;
          },

          getHorAxisLabel: function(v)
          {
              return this.horAxisLabel;
          },
          getVertAxisLabel: function(v)
          {
              return this.vertAxisLabel;
          },
          getLegendPos: function(v)
          {
              return this.legendPos;
          },
          getDataLabelsPos: function(v)
          {
              return this.dataLabelsPos;
          },
          getVertAx: function(v)
          {
              return this.vertAx;
          },
          getHorAx: function(v)
          {
              return this.horAx;
          },

          putHorGridLines: function(v)
          {
              this.horGridLines = v;
          },

          getHorGridLines: function(v)
          {
              return this.horGridLines;
          },

          putVertGridLines: function(v)
          {
              this.vertGridLines = v;
          },

          getVertGridLines: function()
          {
              return this.vertGridLines;
          },

          getType: function()
          {
              return this.type;
          },

          putType: function(v)
          {
              return this.type = v;
          },

          putShowSerName: function(v)
          {
              return this.showSerName = v;
          },
          putShowCatName: function(v)
          {
              return this.showCatName = v;
          },
          putShowVal: function(v)
          {
              return this.showVal = v;
          },


          getShowSerName: function()
          {
              return this.showSerName;
          },
          getShowCatName: function()
          {
              return this.showCatName;
          },
          getShowVal: function()
          {
              return this.showVal;
          },

          putSeparator: function(v)
          {
              this.separator = v;
          },

          getSeparator: function()
          {
              return this.separator;
          },

          putHorAxisProps: function(v)
          {
              this.horAxisProps = v;
          },

          getHorAxisProps: function()
          {
              return this.horAxisProps;
          },


          putVertAxisProps: function(v)
          {
              this.vertAxisProps = v;
          },

          getVertAxisProps: function()
          {
              return this.vertAxisProps;
          },

          changeType: function(type)
          {
              if(this.type === type)
                  return;

              var bSwapGridLines = ((this.type === c_oAscChartTypeSettings.hBarNormal || this.type === c_oAscChartTypeSettings.hBarStacked || this.type === c_oAscChartTypeSettings.hBarStackedPer)
              !== (type === c_oAscChartTypeSettings.hBarNormal || type === c_oAscChartTypeSettings.hBarStacked || type === c_oAscChartTypeSettings.hBarStackedPer)   );
              var bSwapLines = ((
                type === c_oAscChartTypeSettings.lineNormal          ||
                type === c_oAscChartTypeSettings.lineStacked                  ||
                type === c_oAscChartTypeSettings.lineStackedPer               ||
                type === c_oAscChartTypeSettings.lineNormalMarker             ||
                type === c_oAscChartTypeSettings.lineStackedMarker            ||
                type === c_oAscChartTypeSettings.lineStackedPerMarker

              ) !== (

                this.type === c_oAscChartTypeSettings.lineNormal          ||
                this.type === c_oAscChartTypeSettings.lineStacked                  ||
                this.type === c_oAscChartTypeSettings.lineStackedPer               ||
                this.type === c_oAscChartTypeSettings.lineNormalMarker             ||
                this.type === c_oAscChartTypeSettings.lineStackedMarker            ||
                this.type === c_oAscChartTypeSettings.lineStackedPerMarker
              ));
              var bSwapScatter = ((this.type === c_oAscChartTypeSettings.scatter) !== (type === c_oAscChartTypeSettings.scatter));



              var nOldType = this.type;
              this.putType(type);

              var hor_axis_settings = this.getHorAxisProps();
              var vert_axis_settings = this.getVertAxisProps();
              var new_hor_axis_settings, new_vert_axis_settings, oTempVal;
              if(bSwapGridLines)
              {
                  oTempVal = hor_axis_settings;
                  hor_axis_settings = vert_axis_settings;
                  vert_axis_settings = oTempVal;
                  this.putHorAxisProps(hor_axis_settings);
                  this.putVertAxisProps(vert_axis_settings);

                  oTempVal = this.horGridLines;
                  this.putHorGridLines(this.vertGridLines);
                  this.putVertGridLines(oTempVal);
              }
              switch(type)
              {
                  case c_oAscChartTypeSettings.pie                 :
                  case c_oAscChartTypeSettings.doughnut            :
                  {
                      this.putHorAxisProps(null);
                      this.putVertAxisProps(null);
                      this.putHorAxisLabel(null);
                      this.putVertAxisLabel(null);
                      this.putShowHorAxis(null);
                      this.putShowVerAxis(null);
                      break;
                  }
                  case c_oAscChartTypeSettings.barNormal           :
                  case c_oAscChartTypeSettings.barStacked          :
                  case c_oAscChartTypeSettings.barStackedPer       :
                  case c_oAscChartTypeSettings.lineNormal          :
                  case c_oAscChartTypeSettings.lineStacked         :
                  case c_oAscChartTypeSettings.lineStackedPer      :
                  case c_oAscChartTypeSettings.lineNormalMarker    :
                  case c_oAscChartTypeSettings.lineStackedMarker   :
                  case c_oAscChartTypeSettings.lineStackedPerMarker:
                  case c_oAscChartTypeSettings.areaNormal          :
                  case c_oAscChartTypeSettings.areaStacked         :
                  case c_oAscChartTypeSettings.areaStackedPer      :
                  case c_oAscChartTypeSettings.stock               :
                  {
                      if(!hor_axis_settings || hor_axis_settings.getAxisType() !== c_oAscAxisType.cat)
                      {
                          new_hor_axis_settings = new asc_CatAxisSettings();
                          new_hor_axis_settings.setDefault();
                          this.putHorAxisProps(new_hor_axis_settings);
                      }
                      if(!vert_axis_settings || vert_axis_settings.getAxisType() !== c_oAscAxisType.val)
                      {
                          new_vert_axis_settings = new asc_ValAxisSettings();
                          new_vert_axis_settings.setDefault();
                          this.putVertAxisProps(new_vert_axis_settings);
                      }

                      if(bSwapLines)
                      {
                          this.putShowMarker(false);
                          this.putSmooth(null);
                          this.putLine(true);
                      }
                      if(nOldType === c_oAscChartTypeSettings.hBarNormal || nOldType === c_oAscChartTypeSettings.hBarStacked || nOldType === c_oAscChartTypeSettings.hBarStackedPer){
                          var bTemp = this.showHorAxis;
                          this.putShowHorAxis(this.showVerAxis)
                          this.putShowVerAxis(bTemp);
                      }
                      else if(nOldType === c_oAscChartTypeSettings.pie || nOldType === c_oAscChartTypeSettings.doughnut)
                      {
                          this.putShowHorAxis(true);
                          this.putShowVerAxis(true);
                      }
                      break;
                  }
                  case c_oAscChartTypeSettings.hBarNormal          :
                  case c_oAscChartTypeSettings.hBarStacked         :
                  case c_oAscChartTypeSettings.hBarStackedPer      :
                  {
                      if(!hor_axis_settings || hor_axis_settings.getAxisType() !== c_oAscAxisType.val)
                      {
                          new_hor_axis_settings = new asc_ValAxisSettings();
                          new_hor_axis_settings.setDefault();
                          this.putHorAxisProps(new_hor_axis_settings);
                      }
                      if(!vert_axis_settings || vert_axis_settings.getAxisType() !== c_oAscAxisType.cat)
                      {
                          new_vert_axis_settings = new asc_CatAxisSettings();
                          new_vert_axis_settings.setDefault();
                          this.putVertAxisProps(new_vert_axis_settings);
                      }
                      if(nOldType === c_oAscChartTypeSettings.pie || nOldType === c_oAscChartTypeSettings.doughnut){
                          this.putShowHorAxis(true);
                          this.putShowVerAxis(true);
                      }
                      else if(nOldType !== c_oAscChartTypeSettings.hBarNormal
                        && nOldType !== c_oAscChartTypeSettings.hBarStacked
                        && nOldType !== c_oAscChartTypeSettings.hBarStackedPer){
                          var bTemp = this.showHorAxis;
                          this.putShowHorAxis(this.showVerAxis)
                          this.putShowVerAxis(bTemp);
                      }
                      //this.putHorGridLines(c_oAscGridLinesSettings.none);
                      //this.putVertGridLines(c_oAscGridLinesSettings.major);
                      break;
                  }
                  case c_oAscChartTypeSettings.scatter             :
                  case c_oAscChartTypeSettings.scatterLine         :
                  case c_oAscChartTypeSettings.scatterLineMarker   :
                  case c_oAscChartTypeSettings.scatterMarker       :
                  case c_oAscChartTypeSettings.scatterNone         :
                  case c_oAscChartTypeSettings.scatterSmooth       :
                  case c_oAscChartTypeSettings.scatterSmoothMarker :
                  {
                      if(!hor_axis_settings || hor_axis_settings.getAxisType() !== c_oAscAxisType.val)
                      {
                          new_hor_axis_settings = new asc_ValAxisSettings();
                          new_hor_axis_settings.setDefault();
                          this.putHorAxisProps(new_hor_axis_settings);
                      }
                      if(!vert_axis_settings || vert_axis_settings.getAxisType() !== c_oAscAxisType.val)
                      {
                          new_vert_axis_settings = new asc_ValAxisSettings();
                          new_vert_axis_settings.setDefault();
                          this.putVertAxisProps(new_vert_axis_settings);
                      }
                      //this.putHorGridLines(c_oAscGridLinesSettings.major);
                      //this.putVertGridLines(c_oAscGridLinesSettings.major);
                      if(bSwapScatter)
                      {
                          this.putShowMarker(true);
                          this.putSmooth(null);
                          this.putLine(false);
                      }
                      if(nOldType === c_oAscChartTypeSettings.hBarNormal || nOldType === c_oAscChartTypeSettings.hBarStacked || nOldType === c_oAscChartTypeSettings.hBarStackedPer){
                          var bTemp = this.showHorAxis;
                          this.putShowHorAxis(this.showVerAxis)
                          this.putShowVerAxis(bTemp);
                      }
                      else if(nOldType === c_oAscChartTypeSettings.pie || nOldType === c_oAscChartTypeSettings.doughnut){
                          this.putShowHorAxis(true);
                          this.putShowVerAxis(true);
                      }
                      break;
                  }
              }
          },

          putShowHorAxis: function(v){
              this.showHorAxis = v;
          },
          getShowHorAxis: function(){
              return this.showHorAxis;
          },

          putShowVerAxis: function(v){
              this.showVerAxis = v;
          },
          getShowVerAxis: function(){
              return this.showVerAxis;
          }
      };

      /** @constructor */
      function asc_CRect (x, y, width, height) {
          // private members
          this._x = x;
          this._y = y;
          this._width = width;
          this._height = height;
      }

      asc_CRect.prototype = {
          asc_getX:		function () { return this._x; },
          asc_getY:		function () { return this._y; },
          asc_getWidth:	function () { return this._width; },
          asc_getHeight:	function () { return this._height; }
      };

      /**
       * Класс CColor для работы с цветами
       * -----------------------------------------------------------------------------
       *
       * @constructor
       * @memberOf window
       */

      function CColor (r,g,b,a){
          this.r = (undefined == r) ? 0 : r;
          this.g = (undefined == g) ? 0 : g;
          this.b = (undefined == b) ? 0 : b;
          this.a = (undefined == a) ? 1 : a;
      }

      CColor.prototype = {
          constructor: CColor,
          getR: function(){return this.r},
          get_r: function(){return this.r},
          put_r: function(v){this.r = v; this.hex = undefined;},
          getG: function(){return this.g},
          get_g: function(){return this.g;},
          put_g: function(v){this.g = v; this.hex = undefined;},
          getB: function(){return this.b},
          get_b: function(){return this.b;},
          put_b: function(v){this.b = v; this.hex = undefined;},
          getA: function(){return this.a},
          get_hex: function()
          {
              if(!this.hex)
              {
                  var r = this.r.toString(16);
                  var g = this.g.toString(16);
                  var b = this.b.toString(16);
                  this.hex = ( r.length == 1? "0" + r: r) +
                    ( g.length == 1? "0" + g: g) +
                    ( b.length == 1? "0" + b: b);
              }
              return this.hex;
          },

          Compare: function(Color) {
              return (this.r === Color.r && this.g === Color.g && this.b === Color.b && this.a === Color.a);
          },
          Copy: function() {
              return new CColor(this.r, this.g, this.b, this.a);
          }
      };

      function asc_CColor() {
          this.type = c_oAscColor.COLOR_TYPE_SRGB;
          this.value = null;
          this.r = 0;
          this.g = 0;
          this.b = 0;
          this.a = 255;

          this.Auto = false;

          this.Mods = [];
          this.ColorSchemeId = -1;

          if (1 === arguments.length) {
              this.r = arguments[0].r;
              this.g = arguments[0].g;
              this.b = arguments[0].b;
          } else {
              if (3 <= arguments.length) {
                  this.r = arguments[0];
                  this.g = arguments[1];
                  this.b = arguments[2];
              }
              if (4 === arguments.length)
                  this.a = arguments[3];
          }
      }

      asc_CColor.prototype = {
          asc_getR: function() { return this.r },
          asc_putR: function(v) { this.r = v; this.hex = undefined; },
          asc_getG: function() { return this.g; },
          asc_putG: function(v) { this.g = v; this.hex = undefined; },
          asc_getB: function() { return this.b; },
          asc_putB: function(v) { this.b = v; this.hex = undefined; },
          asc_getA: function() { return this.a; },
          asc_putA: function(v) { this.a = v; this.hex = undefined; },
          asc_getType: function() { return this.type; },
          asc_putType: function(v) { this.type = v; },
          asc_getValue: function() { return this.value; },
          asc_putValue: function(v) { this.value = v; },
          asc_getHex: function() {
              if(!this.hex)
              {
                  var a = this.a.toString(16);
                  var r = this.r.toString(16);
                  var g = this.g.toString(16);
                  var b = this.b.toString(16);
                  this.hex = ( a.length == 1? "0" + a: a) +
                    ( r.length == 1? "0" + r: r) +
                    ( g.length == 1? "0" + g: g) +
                    ( b.length == 1? "0" + b: b);
              }
              return this.hex;
          },
          asc_getColor: function() {
              var ret = new CColor(this.r, this.g, this.b);
              return ret;
          },
          asc_putAuto: function(v){this.Auto = v;},
          asc_getAuto: function(){return this.Auto;}
      };

      function asc_CTextBorder (obj)
      {
          if (obj)
          {
              if(obj.Color instanceof asc_CColor)
              {
                  this.Color = obj.Color;
              }
              else
              {
                  this.Color = (undefined != obj.Color && null != obj.Color) ? CreateAscColorCustom(obj.Color.r, obj.Color.g, obj.Color.b) : null;
              }
              this.Size = (undefined != obj.Size) ? obj.Size : null;
              this.Value = (undefined != obj.Value) ? obj.Value : null;
              this.Space = (undefined != obj.Space) ? obj.Space : null;
          }
          else
          {
              this.Color = CreateAscColorCustom(0,0,0);
              this.Size  = 0.5 * AscCommonWord.g_dKoef_pt_to_mm;
              this.Value = AscCommonWord.border_Single;
              this.Space = 0;
          }
      }
      asc_CTextBorder.prototype.asc_getColor = function(){return this.Color; };
      asc_CTextBorder.prototype.asc_putColor = function(v){this.Color = v;};
      asc_CTextBorder.prototype.asc_getSize = function(){return this.Size; };
      asc_CTextBorder.prototype.asc_putSize = function(v){this.Size = v;};
      asc_CTextBorder.prototype.asc_getValue = function(){return this.Value; };
      asc_CTextBorder.prototype.asc_putValue = function(v){this.Value = v;};
      asc_CTextBorder.prototype.asc_getSpace = function(){return this.Space; };
      asc_CTextBorder.prototype.asc_putSpace = function(v){this.Space = v;};
      asc_CTextBorder.prototype.asc_getForSelectedCells = function(){return this.ForSelectedCells; };
      asc_CTextBorder.prototype.asc_putForSelectedCells = function(v){this.ForSelectedCells = v;};

      function asc_CParagraphBorders(obj) {

          if (obj) {
              this.Left = (undefined != obj.Left && null != obj.Left) ? new asc_CTextBorder (obj.Left) : null;
              this.Top = (undefined != obj.Top && null != obj.Top) ? new asc_CTextBorder (obj.Top) : null;
              this.Right = (undefined != obj.Right && null != obj.Right) ? new asc_CTextBorder (obj.Right) : null;
              this.Bottom = (undefined != obj.Bottom && null != obj.Bottom) ? new asc_CTextBorder (obj.Bottom) : null;
              this.Between = (undefined != obj.Between && null != obj.Between) ? new asc_CTextBorder (obj.Between) : null;
          }
          else {
              this.Left = null;
              this.Top = null;
              this.Right = null;
              this.Bottom = null;
              this.Between = null;
          }
      }

      asc_CParagraphBorders.prototype = {
          asc_getLeft: function(){return this.Left; },
          asc_putLeft: function(v){this.Left = (v) ? new asc_CTextBorder (v) : null;},
          asc_getTop: function(){return this.Top; },
          asc_putTop: function(v){this.Top = (v) ? new asc_CTextBorder (v) : null;},
          asc_getRight: function(){return this.Right; },
          asc_putRight: function(v){this.Right = (v) ? new asc_CTextBorder (v) : null;},
          asc_getBottom: function(){return this.Bottom; },
          asc_putBottom: function(v){this.Bottom = (v) ? new asc_CTextBorder (v) : null;},
          asc_getBetween: function(){return this.Between; },
          asc_putBetween: function(v){this.Between = (v) ? new asc_CTextBorder (v) : null;}
      };

      function asc_CListType(obj) {

          if (obj) {
              this.Type = (undefined == obj.Type) ? null : obj.Type;
              this.SubType = (undefined == obj.Type) ? null : obj.SubType;
          }
          else {
              this.Type = null;
              this.SubType = null;
          }
      }
      asc_CListType.prototype.asc_getListType = function() { return this.Type; };
      asc_CListType.prototype.asc_getListSubType = function() { return this.SubType; };

      function asc_CTextFontFamily(obj) {

          if (obj) {
              this.Name = (undefined != obj.Name) ? obj.Name : null; 		// "Times New Roman"
              this.Index = (undefined != obj.Index) ? obj.Index : null;	// -1
          }
          else {
              this.Name = "Times New Roman";
              this.Index = -1;
          }
      }

      asc_CTextFontFamily.prototype = {
          asc_getName: function () { return this.Name; },
          asc_getIndex: function () { return this.Index; }
      };

      /** @constructor */
      function asc_CParagraphTab(Pos, Value) {
          this.Pos   = Pos;
          this.Value = Value;
      }

      asc_CParagraphTab.prototype = {
          asc_getValue: function (){ return this.Value; },
          asc_putValue: function (v){ this.Value = v; },
          asc_getPos: function (){ return this.Pos; },
          asc_putPos: function (v){ this.Pos = v; }
      };

      /** @constructor */
      function asc_CParagraphTabs(obj) {
          this.Tabs = [];

          if ( undefined != obj ) {
              var Count = obj.Tabs.length;
              for (var Index = 0; Index < Count; Index++)
              {
                  this.Tabs.push( new asc_CParagraphTab(obj.Tabs[Index].Pos, obj.Tabs[Index].Value) );
              }
          }
      }

      asc_CParagraphTabs.prototype = {
          asc_getCount: function (){ return this.Tabs.length; },
          asc_getTab: function (Index){ return this.Tabs[Index]; },
          asc_addTab: function (Tab){ this.Tabs.push(Tab) },
          asc_clear: function (){ this.Tabs.length = 0; }
      };

      /** @constructor */
      function asc_CParagraphShd(obj) {

          if (obj) {
              this.Value = (undefined != obj.Value) ? obj.Value : null;
              if(obj.Unifill && obj.Unifill.fill && obj.Unifill.fill.type === c_oAscFill.FILL_TYPE_SOLID && obj.Unifill.fill.color)
              {
                  this.Color = CreateAscColor(obj.Unifill.fill.color);
              }
              else
              {
                  this.Color = (undefined != obj.Color && null != obj.Color) ? CreateAscColorCustom( obj.Color.r, obj.Color.g, obj.Color.b ) : null;
              }
          }
          else {
              this.Value = Asc.c_oAscShdNil;
              this.Color = CreateAscColorCustom(255, 255, 255);
          }
      }

      asc_CParagraphShd.prototype = {
          asc_getValue: function (){ return this.Value; },
          asc_putValue: function (v){ this.Value = v; },
          asc_getColor: function (){ return this.Color; },
          asc_putColor: function (v){ this.Color = (v) ? v : null; }
      };

      function asc_CParagraphFrame(obj)
      {
          if ( obj )
          {
              this.FromDropCapMenu = false;

              this.DropCap = obj.DropCap;
              this.H       = obj.H;
              this.HAnchor = obj.HAnchor;
              this.HRule   = obj.HRule;
              this.HSpace  = obj.HSpace;
              this.Lines   = obj.Lines;
              this.VAnchor = obj.VAnchor;
              this.VSpace  = obj.VSpace;
              this.W       = obj.W;
              this.Wrap    = obj.Wrap;
              this.X       = obj.X;
              this.XAlign  = obj.XAlign;
              this.Y       = obj.Y;
              this.YAlign  = obj.YAlign;
              this.Brd     = (undefined != obj.Brd     && null != obj.Brd) ? new asc_CParagraphBorders(obj.Brd) : null;
              this.Shd     = (undefined != obj.Shd     && null != obj.Shd)     ? new asc_CParagraphShd(obj.Shd) : null;
              this.FontFamily = (undefined != obj.FontFamily && null != obj.FontFamily) ? new asc_CTextFontFamily (obj.FontFamily) : null;
          }
          else
          {
              this.FromDropCapMenu = false;

              this.DropCap = undefined;
              this.H       = undefined;
              this.HAnchor = undefined;
              this.HRule   = undefined;
              this.HSpace  = undefined;
              this.Lines   = undefined;
              this.VAnchor = undefined;
              this.VSpace  = undefined;
              this.W       = undefined;
              this.Wrap    = undefined;
              this.X       = undefined;
              this.XAlign  = undefined;
              this.Y       = undefined;
              this.YAlign  = undefined;
              this.Shd     = null;
              this.Brd     = null;
              this.FontFamily = null;
          }
      }
      asc_CParagraphFrame.prototype.asc_getDropCap = function () { return this.DropCap; };
      asc_CParagraphFrame.prototype.asc_putDropCap = function (v) { this.DropCap = v; };
      asc_CParagraphFrame.prototype.asc_getH = function () { return this.H; };
      asc_CParagraphFrame.prototype.asc_putH = function (v) { this.H = v; };
      asc_CParagraphFrame.prototype.asc_getHAnchor = function () { return this.HAnchor; };
      asc_CParagraphFrame.prototype.asc_putHAnchor = function (v) { this.HAnchor = v; };
      asc_CParagraphFrame.prototype.asc_getHRule = function () { return this.HRule; };
      asc_CParagraphFrame.prototype.asc_putHRule = function (v) { this.HRule = v; };
      asc_CParagraphFrame.prototype.asc_getHSpace = function () { return this.HSpace; };
      asc_CParagraphFrame.prototype.asc_putHSpace = function (v) { this.HSpace = v; };
      asc_CParagraphFrame.prototype.asc_getLines = function () { return this.Lines; };
      asc_CParagraphFrame.prototype.asc_putLines = function (v) { this.Lines = v; };
      asc_CParagraphFrame.prototype.asc_getVAnchor = function () { return this.VAnchor; };
      asc_CParagraphFrame.prototype.asc_putVAnchor = function (v) { this.VAnchor = v; };
      asc_CParagraphFrame.prototype.asc_getVSpace = function () { return this.VSpace; };
      asc_CParagraphFrame.prototype.asc_putVSpace = function (v) { this.VSpace = v; };
      asc_CParagraphFrame.prototype.asc_getW = function () { return this.W; };
      asc_CParagraphFrame.prototype.asc_putW = function (v) { this.W = v; };
      asc_CParagraphFrame.prototype.asc_getWrap = function () { return this.Wrap; };
      asc_CParagraphFrame.prototype.asc_putWrap = function (v) { this.Wrap = v; };
      asc_CParagraphFrame.prototype.asc_getX = function () { return this.X; };
      asc_CParagraphFrame.prototype.asc_putX = function (v) { this.X = v; };
      asc_CParagraphFrame.prototype.asc_getXAlign = function () { return this.XAlign; };
      asc_CParagraphFrame.prototype.asc_putXAlign = function (v) { this.XAlign = v; };
      asc_CParagraphFrame.prototype.asc_getY = function () { return this.Y; };
      asc_CParagraphFrame.prototype.asc_putY = function (v) { this.Y = v; };
      asc_CParagraphFrame.prototype.asc_getYAlign = function () { return this.YAlign; };
      asc_CParagraphFrame.prototype.asc_putYAlign = function (v) { this.YAlign = v; };
      asc_CParagraphFrame.prototype.asc_getBorders = function () { return this.Brd; };
      asc_CParagraphFrame.prototype.asc_putBorders = function (v) { this.Brd = v; };
      asc_CParagraphFrame.prototype.asc_getShade = function () { return this.Shd; };
      asc_CParagraphFrame.prototype.asc_putShade = function (v) { this.Shd = v; };
      asc_CParagraphFrame.prototype.asc_getFontFamily = function () { return this.FontFamily; };
      asc_CParagraphFrame.prototype.asc_putFontFamily = function (v) { this.FontFamily = v; };
      asc_CParagraphFrame.prototype.asc_putFromDropCapMenu = function (v) { this.FromDropCapMenu = v; };

      /** @constructor */
      function asc_CParagraphSpacing(obj) {

          if (obj) {
              this.Line     = (undefined != obj.Line    ) ? obj.Line     : null; // Расстояние между строками внутри абзаца
              this.LineRule = (undefined != obj.LineRule) ? obj.LineRule : null; // Тип расстрояния между строками
              this.Before   = (undefined != obj.Before  ) ? obj.Before   : null; // Дополнительное расстояние до абзаца
              this.After    = (undefined != obj.After   ) ? obj.After    : null; // Дополнительное расстояние после абзаца
          }
          else {
              this.Line     = undefined; // Расстояние между строками внутри абзаца
              this.LineRule = undefined; // Тип расстрояния между строками
              this.Before   = undefined; // Дополнительное расстояние до абзаца
              this.After    = undefined; // Дополнительное расстояние после абзаца
          }
      }

      asc_CParagraphSpacing.prototype = {
          asc_getLine: function () { return this.Line; },
          asc_getLineRule: function () { return this.LineRule; },
          asc_getBefore: function () { return this.Before; },
          asc_getAfter: function () { return this.After; }
      };

      /** @constructor */
      function asc_CParagraphInd(obj) {
          if (obj) {
              this.Left      = (undefined != obj.Left     ) ? obj.Left      : null; // Левый отступ
              this.Right     = (undefined != obj.Right    ) ? obj.Right     : null; // Правый отступ
              this.FirstLine = (undefined != obj.FirstLine) ? obj.FirstLine : null; // Первая строка
          }
          else {
              this.Left      = undefined; // Левый отступ
              this.Right     = undefined; // Правый отступ
              this.FirstLine = undefined; // Первая строка
          }
      }

      asc_CParagraphInd.prototype = {
          asc_getLeft: function () { return this.Left; },
          asc_putLeft: function (v) { this.Left = v; },
          asc_getRight: function () { return this.Right; },
          asc_putRight: function (v) { this.Right = v; },
          asc_getFirstLine: function () { return this.FirstLine; },
          asc_putFirstLine: function (v) { this.FirstLine = v; }
      };

      /** @constructor */
      function asc_CParagraphProperty(obj) {

          if (obj) {
              this.ContextualSpacing = (undefined != obj.ContextualSpacing)              ? obj.ContextualSpacing : null;
              this.Ind               = (undefined != obj.Ind     && null != obj.Ind)     ? new asc_CParagraphInd (obj.Ind) : null;
              this.KeepLines         = (undefined != obj.KeepLines)                      ? obj.KeepLines : null;
              this.KeepNext          = (undefined != obj.KeepNext)                       ? obj.KeepNext  : undefined;
              this.WidowControl      = (undefined != obj.WidowControl                    ? obj.WidowControl : undefined );
              this.PageBreakBefore   = (undefined != obj.PageBreakBefore)                ? obj.PageBreakBefore : null;
              this.Spacing           = (undefined != obj.Spacing && null != obj.Spacing) ? new asc_CParagraphSpacing (obj.Spacing) : null;
              this.Brd               = (undefined != obj.Brd     && null != obj.Brd)     ? new asc_CParagraphBorders (obj.Brd) : null;
              this.Shd               = (undefined != obj.Shd     && null != obj.Shd)     ? new asc_CParagraphShd (obj.Shd) : null;
              this.Tabs              = (undefined != obj.Tabs)                           ? new asc_CParagraphTabs(obj.Tabs) : undefined;
              this.DefaultTab        = AscCommonWord.Default_Tab_Stop;
              this.Locked            = (undefined != obj.Locked  && null != obj.Locked ) ? obj.Locked : false;
              this.CanAddTable       = (undefined != obj.CanAddTable )                   ? obj.CanAddTable : true;

              this.FramePr           = (undefined != obj.FramePr )                       ? new asc_CParagraphFrame( obj.FramePr ) : undefined;
              this.CanAddDropCap     = (undefined != obj.CanAddDropCap )                 ? obj.CanAddDropCap : false;
              this.CanAddImage       = (undefined != obj.CanAddImage )                   ? obj.CanAddImage   : false;

              this.Subscript         = (undefined != obj.Subscript)                      ? obj.Subscript : undefined;
              this.Superscript       = (undefined != obj.Superscript)                    ? obj.Superscript : undefined;
              this.SmallCaps         = (undefined != obj.SmallCaps)                      ? obj.SmallCaps : undefined;
              this.AllCaps           = (undefined != obj.AllCaps)                        ? obj.AllCaps : undefined;
              this.Strikeout         = (undefined != obj.Strikeout)                      ? obj.Strikeout : undefined;
              this.DStrikeout        = (undefined != obj.DStrikeout)                     ? obj.DStrikeout : undefined;
              this.TextSpacing       = (undefined != obj.TextSpacing)                    ? obj.TextSpacing : undefined;
              this.Position          = (undefined != obj.Position)                       ? obj.Position : undefined;
          }
          else {
              //ContextualSpacing : false,            // Удалять ли интервал между параграфами одинакового стиля
              //
              //    Ind :
              //    {
              //        Left      : 0,                    // Левый отступ
              //        Right     : 0,                    // Правый отступ
              //        FirstLine : 0                     // Первая строка
              //    },
              //
              //    Jc : align_Left,                      // Прилегание параграфа
              //
              //    KeepLines : false,                    // переносить параграф на новую страницу,
              //                                          // если на текущей он целиком не убирается
              //    KeepNext  : false,                    // переносить параграф вместе со следующим параграфом
              //
              //    PageBreakBefore : false,              // начинать параграф с новой страницы

              this.ContextualSpacing = undefined;
              this.Ind               = new asc_CParagraphInd();
              this.KeepLines         = undefined;
              this.KeepNext          = undefined;
              this.WidowControl      = undefined;
              this.PageBreakBefore   = undefined;
              this.Spacing           = new asc_CParagraphSpacing();
              this.Brd               = undefined;
              this.Shd               = undefined;
              this.Locked            = false;
              this.CanAddTable       = true;
              this.Tabs              = undefined;

              this.Subscript         = undefined;
              this.Superscript       = undefined;
              this.SmallCaps         = undefined;
              this.AllCaps           = undefined;
              this.Strikeout         = undefined;
              this.DStrikeout        = undefined;
              this.TextSpacing       = undefined;
              this.Position          = undefined;
          }
      }

      asc_CParagraphProperty.prototype = {

          asc_getContextualSpacing: function () { return this.ContextualSpacing; },
          asc_putContextualSpacing: function (v) { this.ContextualSpacing = v; },
          asc_getInd: function () { return this.Ind; },
          asc_putInd: function (v) { this.Ind = v; },
          asc_getKeepLines: function () { return this.KeepLines; },
          asc_putKeepLines: function (v) { this.KeepLines = v; },
          asc_getKeepNext: function () { return this.KeepNext; },
          asc_putKeepNext: function (v) { this.KeepNext = v; },
          asc_getPageBreakBefore: function (){ return this.PageBreakBefore; },
          asc_putPageBreakBefore: function (v){ this.PageBreakBefore = v; },
          asc_getWidowControl: function (){ return this.WidowControl; },
          asc_putWidowControl: function (v){ this.WidowControl = v; },
          asc_getSpacing: function () { return this.Spacing; },
          asc_putSpacing: function (v) { this.Spacing = v; },
          asc_getBorders: function () { return this.Brd; },
          asc_putBorders: function (v) { this.Brd = v; },
          asc_getShade: function () { return this.Shd; },
          asc_putShade: function (v) { this.Shd = v; },
          asc_getLocked: function() { return this.Locked; },
          asc_getCanAddTable: function() { return this.CanAddTable; },
          asc_getSubscript: function () { return this.Subscript; },
          asc_putSubscript: function (v) { this.Subscript = v; },
          asc_getSuperscript: function () { return this.Superscript; },
          asc_putSuperscript: function (v) { this.Superscript = v; },
          asc_getSmallCaps: function () { return this.SmallCaps; },
          asc_putSmallCaps: function (v) { this.SmallCaps = v; },
          asc_getAllCaps: function () { return this.AllCaps; },
          asc_putAllCaps: function (v) { this.AllCaps = v; },
          asc_getStrikeout: function () { return this.Strikeout; },
          asc_putStrikeout: function (v) { this.Strikeout = v; },
          asc_getDStrikeout: function () { return this.DStrikeout; },
          asc_putDStrikeout: function (v) { this.DStrikeout = v; },
          asc_getTextSpacing: function () { return this.TextSpacing; },
          asc_putTextSpacing: function (v) { this.TextSpacing = v; },
          asc_getPosition: function () { return this.Position; },
          asc_putPosition: function (v) { this.Position = v; },
          asc_getTabs: function () { return this.Tabs; },
          asc_putTabs: function (v) { this.Tabs = v; },
          asc_getDefaultTab: function () { return this.DefaultTab; },
          asc_putDefaultTab: function (v) { this.DefaultTab = v; },

          asc_getFramePr: function () { return this.FramePr; },
          asc_putFramePr: function (v) { this.FramePr = v; },
          asc_getCanAddDropCap: function() { return this.CanAddDropCap; },
          asc_getCanAddImage: function() { return this.CanAddImage; }
      };

      /** @constructor */
      function asc_CTexture() {
          this.Id = 0;
          this.Image = "";
      }

      asc_CTexture.prototype = {
          asc_getId: function() { return this.Id; },
          asc_getImage: function() { return this.Image; }
      };

      /** @constructor */
      function asc_CImageSize( width, height, isCorrect ) {
          this.Width = (undefined == width) ? 0.0 : width;
          this.Height = (undefined == height) ? 0.0 : height;
          this.IsCorrect = isCorrect;
      }

      asc_CImageSize.prototype = {
          asc_getImageWidth: function() { return this.Width; },
          asc_getImageHeight: function() { return this.Height; },
          asc_getIsCorrect: function() { return this.IsCorrect; }
      };

      /** @constructor */
      function asc_CPaddings(obj) {

          if ( obj ) {
              this.Left = (undefined == obj.Left) ? null : obj.Left;
              this.Top = (undefined == obj.Top) ? null : obj.Top;
              this.Bottom = (undefined == obj.Bottom) ? null : obj.Bottom;
              this.Right = (undefined == obj.Right) ? null : obj.Right;
          }
          else {
              this.Left = null;
              this.Top = null;
              this.Bottom = null;
              this.Right = null;
          }
      }

      asc_CPaddings.prototype = {
          asc_getLeft: function() { return this.Left; },
          asc_putLeft: function(v) { this.Left = v; },
          asc_getTop: function() { return this.Top; },
          asc_putTop: function(v) { this.Top = v; },
          asc_getBottom: function() { return this.Bottom; },
          asc_putBottom: function(v) { this.Bottom = v; },
          asc_getRight: function() { return this.Right; },
          asc_putRight: function(v) { this.Right = v; }
      };

      /** @constructor */
      function asc_CShapeProperty() {
          this.type = null; // custom
          this.fill = null;
          this.stroke = null;
          this.paddings = null;
          this.canFill = true;
          this.canChangeArrows = false;
          this.bFromChart = false;
          this.Locked = false;
          this.w = null;
          this.h = null;
          this.vert = null;
          this.verticalTextAlign = null;
          this.textArtProperties = null;
          this.lockAspect = null;
      }

      asc_CShapeProperty.prototype = {
          asc_getType: function() { return this.type; },
          asc_putType: function(v) { this.type = v; },
          asc_getFill: function() { return this.fill; },
          asc_putFill: function(v) { this.fill = v; },
          asc_getStroke: function() { return this.stroke; },
          asc_putStroke: function(v) { this.stroke = v; },
          asc_getPaddings: function() { return this.paddings; },
          asc_putPaddings: function(v) { this.paddings = v; },
          asc_getCanFill: function() { return this.canFill; },
          asc_putCanFill: function(v) { this.canFill = v; },
          asc_getCanChangeArrows: function() { return this.canChangeArrows; },
          asc_setCanChangeArrows: function(v) { this.canChangeArrows = v; },
          asc_getFromChart: function() { return this.bFromChart; },
          asc_setFromChart: function(v) { this.bFromChart = v; },
          asc_getLocked: function() { return this.Locked; },
          asc_setLocked: function(v) { this.Locked = v; },

          asc_getWidth: function(){return this.w},
          asc_putWidth: function(v){this.w = v;},
          asc_getHeight: function(){return this.h},
          asc_putHeight: function(v){this.h = v;},
          asc_getVerticalTextAlign: function(){return this.verticalTextAlign},
          asc_putVerticalTextAlign: function(v){this.verticalTextAlign = v;},
          asc_getVert: function(){return this.vert},
          asc_putVert: function(v){this.vert = v;},
          asc_getTextArtProperties: function(){return this.textArtProperties},
          asc_putTextArtProperties: function(v){this.textArtProperties = v;},
          asc_getLockAspect: function(){return this.lockAspect},
          asc_putLockAspect: function(v){this.lockAspect = v;}
      };

      function asc_TextArtProperties(obj)
      {
          if(obj)
          {
              this.Fill  = obj.Fill;//asc_Fill
              this.Line  = obj.Line;//asc_Stroke
              this.Form  = obj.Form;//srting
              this.Style = obj.Style;//
          }
          else
          {
              this.Fill  = undefined;
              this.Line  = undefined;
              this.Form  = undefined;
              this.Style = undefined;
          }
      }

      asc_TextArtProperties.prototype.asc_putFill = function(oAscFill) {
          this.Fill = oAscFill;
      };
      asc_TextArtProperties.prototype.asc_getFill = function() {
          return this.Fill;
      };
      asc_TextArtProperties.prototype.asc_putLine = function(oAscStroke) {
          this.Line = oAscStroke;
      };
      asc_TextArtProperties.prototype.asc_getLine = function() {
          return this.Line;
      };
      asc_TextArtProperties.prototype.asc_putForm = function(sForm) {
          this.Form = sForm;
      };
      asc_TextArtProperties.prototype.asc_getForm = function() {
          return this.Form;
      };
      asc_TextArtProperties.prototype.asc_putStyle = function(Style) {
          this.Style = Style;
      };
      asc_TextArtProperties.prototype.asc_getStyle = function() {
          return this.Style;
      };

    /** @constructor */
    function asc_CChartTranslate() {
        this.title = "Diagram Title";
        this.xAxis = "X Axis";
        this.yAxis = "Y Axis";
        this.series = "Series";
    }

    asc_CChartTranslate.prototype = {
        asc_getTitle: function() { return this.title; },
        asc_setTitle: function(val) { this.title = val; },

        asc_getXAxis: function() { return this.xAxis; },
        asc_setXAxis: function(val) { this.xAxis = val; },

        asc_getYAxis: function() { return this.yAxis; },
        asc_setYAxis: function(val) { this.yAxis = val; },

        asc_getSeries: function() { return this.series; },
        asc_setSeries: function(val) { this.series = val; }
    };

      function asc_TextArtTranslate()
      {
          this.DefaultText = "Your text here";
      }

      asc_TextArtTranslate.prototype.asc_setDefaultText = function(sText)
      {
          this.DefaultText = sText;
      };

      function CImagePositionH(obj)
      {
          if ( obj )
          {
              this.RelativeFrom = ( undefined === obj.RelativeFrom ) ? undefined : obj.RelativeFrom;
              this.UseAlign     = ( undefined === obj.UseAlign     ) ? undefined : obj.UseAlign;
              this.Align        = ( undefined === obj.Align        ) ? undefined : obj.Align;
              this.Value        = ( undefined === obj.Value        ) ? undefined : obj.Value;
              this.Percent      = ( undefined === obj.Percent      ) ? undefined : obj.Percent;
          }
          else
          {
              this.RelativeFrom = undefined;
              this.UseAlign     = undefined;
              this.Align        = undefined;
              this.Value        = undefined;
              this.Percent      = undefined;
          }
      }

      CImagePositionH.prototype.get_RelativeFrom = function()  { return this.RelativeFrom; };
      CImagePositionH.prototype.put_RelativeFrom = function(v) { this.RelativeFrom = v; };
      CImagePositionH.prototype.get_UseAlign = function()  { return this.UseAlign; };
      CImagePositionH.prototype.put_UseAlign = function(v) { this.UseAlign = v; };
      CImagePositionH.prototype.get_Align = function()  { return this.Align; };
      CImagePositionH.prototype.put_Align = function(v) { this.Align = v; };
      CImagePositionH.prototype.get_Value = function()  { return this.Value; };
      CImagePositionH.prototype.put_Value = function(v) { this.Value = v; };
      CImagePositionH.prototype.get_Percent = function() {return this.Percent};
      CImagePositionH.prototype.put_Percent = function(v) {this.Percent = v;};

      function CImagePositionV(obj)
      {
          if ( obj )
          {
              this.RelativeFrom = ( undefined === obj.RelativeFrom ) ? undefined : obj.RelativeFrom;
              this.UseAlign     = ( undefined === obj.UseAlign     ) ? undefined : obj.UseAlign;
              this.Align        = ( undefined === obj.Align        ) ? undefined : obj.Align;
              this.Value        = ( undefined === obj.Value        ) ? undefined : obj.Value;
              this.Percent      = ( undefined === obj.Percent      ) ? undefined : obj.Percent;
          }
          else
          {
              this.RelativeFrom = undefined;
              this.UseAlign     = undefined;
              this.Align        = undefined;
              this.Value        = undefined;
              this.Percent      = undefined;
          }
      }

      CImagePositionV.prototype.get_RelativeFrom = function()  { return this.RelativeFrom; };
      CImagePositionV.prototype.put_RelativeFrom = function(v) { this.RelativeFrom = v; };
      CImagePositionV.prototype.get_UseAlign = function()  { return this.UseAlign; };
      CImagePositionV.prototype.put_UseAlign = function(v) { this.UseAlign = v; };
      CImagePositionV.prototype.get_Align = function()  { return this.Align; };
      CImagePositionV.prototype.put_Align = function(v) { this.Align = v; };
      CImagePositionV.prototype.get_Value = function()  { return this.Value; };
      CImagePositionV.prototype.put_Value = function(v) { this.Value = v; };
      CImagePositionV.prototype.get_Percent = function() {return this.Percent};
      CImagePositionV.prototype.put_Percent = function(v) {this.Percent = v;};

      function CPosition( obj )
      {
          if (obj)
          {
              this.X = (undefined == obj.X) ? null : obj.X;
              this.Y = (undefined == obj.Y) ? null : obj.Y;
          }
          else
          {
              this.X = null;
              this.Y = null;
          }
      }
      CPosition.prototype.get_X = function() { return this.X; };
      CPosition.prototype.put_X = function(v) { this.X = v; };
      CPosition.prototype.get_Y = function() { return this.Y; };
      CPosition.prototype.put_Y = function(v) { this.Y = v; };

      /** @constructor */
      function asc_CImgProperty( obj ) {

          if( obj ) {
              this.CanBeFlow = (undefined != obj.CanBeFlow) ? obj.CanBeFlow : true;

              this.Width         = (undefined != obj.Width        ) ? obj.Width                          : undefined;
              this.Height        = (undefined != obj.Height       ) ? obj.Height                         : undefined;
              this.WrappingStyle = (undefined != obj.WrappingStyle) ? obj.WrappingStyle                  : undefined;
              this.Paddings      = (undefined != obj.Paddings     ) ? new asc_CPaddings (obj.Paddings)       : undefined;
              this.Position      = (undefined != obj.Position     ) ? new CPosition (obj.Position)       : undefined;
              this.AllowOverlap  = (undefined != obj.AllowOverlap ) ? obj.AllowOverlap                   : undefined;
              this.PositionH     = (undefined != obj.PositionH    ) ? new CImagePositionH(obj.PositionH) : undefined;
              this.PositionV     = (undefined != obj.PositionV    ) ? new CImagePositionV(obj.PositionV) : undefined;

              this.SizeRelH       = (undefined != obj.SizeRelH) ? new CImagePositionH(obj.SizeRelH) : undefined;
              this.SizeRelV       = (undefined != obj.SizeRelV) ? new CImagePositionV(obj.SizeRelV) : undefined;

              this.Internal_Position = (undefined != obj.Internal_Position) ? obj.Internal_Position : null;

              this.ImageUrl = (undefined != obj.ImageUrl) ? obj.ImageUrl : null;
              this.Locked   = (undefined != obj.Locked) ? obj.Locked : false;
              this.lockAspect = (undefined != obj.lockAspect) ? obj.lockAspect : false;


              this.ChartProperties = (undefined != obj.ChartProperties) ? obj.ChartProperties : null;
              this.ShapeProperties = (undefined != obj.ShapeProperties) ? obj.ShapeProperties : null;

              this.ChangeLevel = (undefined != obj.ChangeLevel) ? obj.ChangeLevel : null;
              this.Group = (obj.Group != undefined) ? obj.Group : null;

              this.fromGroup = obj.fromGroup != undefined ? obj.fromGroup : null;
              this.severalCharts = obj.severalCharts != undefined ? obj.severalCharts : false;
              this.severalChartTypes = obj.severalChartTypes != undefined ? obj.severalChartTypes : undefined;
              this.severalChartStyles = obj.severalChartStyles != undefined ? obj.severalChartStyles : undefined;
              this.verticalTextAlign = obj.verticalTextAlign != undefined ? obj.verticalTextAlign : undefined;
              this.vert = obj.vert != undefined ? obj.vert : undefined;

              //oleObjects
              this.pluginGuid = obj.pluginGuid !== undefined ? obj.pluginGuid : undefined;
              this.pluginData = obj.pluginData !== undefined ? obj.pluginData : undefined;
              this.oleWidth   = obj.oleWidth != undefined ? obj.oleWidth : undefined;
              this.oleHeight  = obj.oleHeight != undefined ? obj.oleHeight : undefined;
          }
          else {
              this.CanBeFlow = true;
              this.Width         = undefined;
              this.Height        = undefined;
              this.WrappingStyle = undefined;
              this.Paddings      = undefined;
              this.Position      = undefined;
              this.PositionH     = undefined;
              this.PositionV     = undefined;

              this.SizeRelH       = undefined;
              this.SizeRelV       = undefined;

              this.Internal_Position = null;
              this.ImageUrl = null;
              this.Locked   = false;

              this.ChartProperties = null;
              this.ShapeProperties = null;
              this.ImageProperties = null;

              this.ChangeLevel = null;
              this.Group = null;
              this.fromGroup = null;
              this.severalCharts = false;
              this.severalChartTypes = undefined;
              this.severalChartStyles = undefined;
              this.verticalTextAlign = undefined;
              this.vert = undefined;

              //oleObjects
              this.pluginGuid = undefined;
              this.pluginData = undefined;

              this.oleWidth   = undefined;
              this.oleHeight  = undefined;
          }
      }

      asc_CImgProperty.prototype = {
          asc_getChangeLevel: function() { return this.ChangeLevel; },
          asc_putChangeLevel: function(v) { this.ChangeLevel = v; },

          asc_getCanBeFlow: function() { return this.CanBeFlow; },
          asc_getWidth: function() { return this.Width; },
          asc_putWidth: function(v) { this.Width = v; },
          asc_getHeight: function() { return this.Height; },
          asc_putHeight: function(v) { this.Height = v; },
          asc_getWrappingStyle: function() { return this.WrappingStyle; },
          asc_putWrappingStyle: function(v) { this.WrappingStyle = v; },

          // Возвращается объект класса Asc.asc_CPaddings
          asc_getPaddings: function() { return this.Paddings; },
          // Аргумент объект класса Asc.asc_CPaddings
          asc_putPaddings: function(v) { this.Paddings = v; },
          asc_getAllowOverlap: function() {return this.AllowOverlap;},
          asc_putAllowOverlap: function(v) {this.AllowOverlap = v;},
          // Возвращается объект класса CPosition
          asc_getPosition: function() { return this.Position; },
          // Аргумент объект класса CPosition
          asc_putPosition: function(v) { this.Position = v; },
          asc_getPositionH: function()  { return this.PositionH; },
          asc_putPositionH: function(v) { this.PositionH = v; },
          asc_getPositionV: function()  { return this.PositionV; },
          asc_putPositionV: function(v) { this.PositionV = v; },

          asc_getSizeRelH: function()
          {
              return this.SizeRelH;
          },

          asc_putSizeRelH: function(v)
          {
              this.SizeRelH = v;
          },

          asc_getSizeRelV: function()
          {
              return this.SizeRelV;
          },

          asc_putSizeRelV: function(v)
          {
              this.SizeRelV = v;
          },

          asc_getValue_X: function(RelativeFrom) { if ( null != this.Internal_Position ) return this.Internal_Position.Calculate_X_Value(RelativeFrom);  return 0; },
          asc_getValue_Y: function(RelativeFrom) { if ( null != this.Internal_Position ) return this.Internal_Position.Calculate_Y_Value(RelativeFrom);  return 0; },

          asc_getImageUrl: function() { return this.ImageUrl; },
          asc_putImageUrl: function(v) { this.ImageUrl = v; },
          asc_getGroup: function() { return this.Group; },
          asc_putGroup: function(v) { this.Group = v; },
          asc_getFromGroup: function() { return this.fromGroup; },
          asc_putFromGroup: function(v) { this.fromGroup = v; },

          asc_getisChartProps: function() { return this.isChartProps; },
          asc_putisChartPross: function(v) { this.isChartProps = v; },

          asc_getSeveralCharts: function() { return this.severalCharts; },
          asc_putSeveralCharts: function(v) { this.severalCharts = v; },
          asc_getSeveralChartTypes: function() { return this.severalChartTypes; },
          asc_putSeveralChartTypes: function(v) { this.severalChartTypes = v; },

          asc_getSeveralChartStyles: function() { return this.severalChartStyles; },
          asc_putSeveralChartStyles: function(v) { this.severalChartStyles = v; },

          asc_getVerticalTextAlign: function() { return this.verticalTextAlign; },
          asc_putVerticalTextAlign: function(v) { this.verticalTextAlign = v; },
          asc_getVert: function() { return this.vert; },
          asc_putVert: function(v) { this.vert = v; },

          asc_getLocked: function() { return this.Locked; },
          asc_getLockAspect: function(){
              return this.lockAspect;
          },
          asc_putLockAspect: function(v){
              this.lockAspect = v;
          },
          asc_getChartProperties: function() { return this.ChartProperties; },
          asc_putChartProperties: function(v) { this.ChartProperties = v; },
          asc_getShapeProperties: function() { return this.ShapeProperties; },
          asc_putShapeProperties: function(v) { this.ShapeProperties = v; },

          asc_getOriginSize: function(api)
          {
              if(AscFormat.isRealNumber(this.oleWidth) && AscFormat.isRealNumber(this.oleHeight)){
                  return new asc_CImageSize( this.oleWidth, this.oleHeight, true );
              }
              var _section_select = api.WordControl.m_oLogicDocument.Get_PageSizesByDrawingObjects();
              var _page_width             = AscCommon.Page_Width;
              var _page_height            = AscCommon.Page_Height;
              var _page_x_left_margin     = AscCommon.X_Left_Margin;
              var _page_y_top_margin      = AscCommon.Y_Top_Margin;
              var _page_x_right_margin    = AscCommon.X_Right_Margin;
              var _page_y_bottom_margin   = AscCommon.Y_Bottom_Margin;

              if (_section_select)
              {
                  if (_section_select.W)
                      _page_width = _section_select.W;

                  if (_section_select.H)
                      _page_height = _section_select.H;
              }

              var _image = api.ImageLoader.map_image_index[AscCommon.getFullImageSrc2(this.ImageUrl)];
              if (_image != undefined && _image.Image != null && _image.Status == AscFonts.ImageLoadStatus.Complete)
              {
                  var _w = Math.max(1, _page_width - (_page_x_left_margin + _page_x_right_margin));
                  var _h = Math.max(1, _page_height - (_page_y_top_margin + _page_y_bottom_margin));

                  var bIsCorrect = false;
                  if (_image.Image != null)
                  {
                      var __w = Math.max(parseInt(_image.Image.width * AscCommon.g_dKoef_pix_to_mm), 1);
                      var __h = Math.max(parseInt(_image.Image.height * AscCommon.g_dKoef_pix_to_mm), 1);

                      var dKoef = Math.max(__w / _w, __h / _h);
                      if (dKoef > 1)
                      {
                          _w = Math.max(5, __w / dKoef);
                          _h = Math.max(5, __h / dKoef);

                          bIsCorrect = true;
                      }
                      else
                      {
                          _w = __w;
                          _h = __h;
                      }
                  }

                  return new asc_CImageSize( parseInt(_w), parseInt(_h), bIsCorrect);
              }
              return new asc_CImageSize( 50, 50, false );
          },

          //oleObjects
          asc_getPluginGuid: function(){
              return this.pluginGuid;
          },

          asc_putPluginGuid: function(v){
              this.pluginGuid = v;
          },

          asc_getPluginData: function(){
              return this.pluginData;
          },

          asc_putPluginData: function(v){
              this.pluginData = v;
          }
      };

      /** @constructor */
      function asc_CSelectedObject( type, val ) {
          this.Type = (undefined != type) ? type : null;
          this.Value = (undefined != val) ? val : null;
      }

      asc_CSelectedObject.prototype = {
          asc_getObjectType: function() { return this.Type; },
          asc_getObjectValue: function() { return this.Value; }
      };

      function asc_CShapeFill() {
          this.type = null;
          this.fill = null;
          this.transparent = null;
      }

      asc_CShapeFill.prototype = {
          asc_getType: function() { return this.type; },
          asc_putType: function(v) { this.type = v; },
          asc_getFill: function() { return this.fill; },
          asc_putFill: function(v) { this.fill = v; },
          asc_getTransparent: function() { return this.transparent; },
          asc_putTransparent: function(v) { this.transparent = v; },
          asc_CheckForseSet: function()
          {
              if(null != this.transparent)
              {
                  return true;
              }
              if(null != this.fill && this.fill.Positions != null)
              {
                  return true;
              }
              return false;
          }
      }

      function asc_CFillBlip() {
          this.type = c_oAscFillBlipType.STRETCH;
          this.url = "";
          this.texture_id = null;
      }

      asc_CFillBlip.prototype = {
          asc_getType: function(){return this.type},
          asc_putType: function(v){this.type = v;},
          asc_getUrl: function(){return this.url;},
          asc_putUrl: function(v){this.url = v;},
          asc_getTextureId: function(){return this.texture_id;},
          asc_putTextureId: function(v){this.texture_id = v;}
      }

      function asc_CFillHatch() {
          this.PatternType = undefined;
          this.fgClr = undefined;
          this.bgClr = undefined;
      }

      asc_CFillHatch.prototype = {
          asc_getPatternType: function(){return this.PatternType;},
          asc_putPatternType: function(v){this.PatternType = v;},
          asc_getColorFg: function(){return this.fgClr;},
          asc_putColorFg: function(v){this.fgClr = v;},
          asc_getColorBg: function(){return this.bgClr;},
          asc_putColorBg: function(v){this.bgClr = v;}
      };

      function asc_CFillGrad() {
          this.Colors = undefined;
          this.Positions = undefined;
          this.GradType = 0;

          this.LinearAngle = undefined;
          this.LinearScale = true;

          this.PathType = 0;
      }

      asc_CFillGrad.prototype = {
          asc_getColors: function(){return this.Colors;},
          asc_putColors: function(v){this.Colors = v;},
          asc_getPositions: function(){return this.Positions;},
          asc_putPositions: function(v){this.Positions = v;},
          asc_getGradType: function(){return this.GradType;},
          asc_putGradType: function(v){this.GradType = v;},
          asc_getLinearAngle: function(){return this.LinearAngle;},
          asc_putLinearAngle: function(v){this.LinearAngle = v;},
          asc_getLinearScale: function(){return this.LinearScale;},
          asc_putLinearScale: function(v){this.LinearScale = v;},
          asc_getPathType: function(){return this.PathType;},
          asc_putPathType: function(v){this.PathType = v;}
      };

      function asc_CFillSolid() {
          this.color = new asc_CColor();
      }

      asc_CFillSolid.prototype = {
          asc_getColor: function() { return this.color },
          asc_putColor: function(v) { this.color = v; }
      };

      function asc_CStroke() {
          this.type = null;
          this.width = null;
          this.color = null;

          this.LineJoin = null;
          this.LineCap = null;

          this.LineBeginStyle = null;
          this.LineBeginSize = null;

          this.LineEndStyle = null;
          this.LineEndSize = null;

          this.canChangeArrows = false;
      }

      asc_CStroke.prototype = {
          asc_getType: function(){return this.type;},
          asc_putType: function(v){this.type = v;},
          asc_getWidth: function(){return this.width;},
          asc_putWidth: function(v){this.width = v;},
          asc_getColor: function(){return this.color;},
          asc_putColor: function(v){this.color = v;},

          asc_getLinejoin: function(){return this.LineJoin;},
          asc_putLinejoin: function(v){this.LineJoin = v;},
          asc_getLinecap: function(){return this.LineCap;},
          asc_putLinecap: function(v){this.LineCap = v;},

          asc_getLinebeginstyle: function(){return this.LineBeginStyle;},
          asc_putLinebeginstyle: function(v){this.LineBeginStyle = v;},
          asc_getLinebeginsize: function(){return this.LineBeginSize;},
          asc_putLinebeginsize: function(v){this.LineBeginSize = v;},
          asc_getLineendstyle: function(){return this.LineEndStyle;},
          asc_putLineendstyle: function(v){this.LineEndStyle = v;},
          asc_getLineendsize: function(){return this.LineEndSize;},
          asc_putLineendsize: function(v){this.LineEndSize = v;},

          asc_getCanChangeArrows: function(){return this.canChangeArrows;}
      };

      // цвет. может быть трех типов:
      // c_oAscColor.COLOR_TYPE_SRGB		: value - не учитывается
      // c_oAscColor.COLOR_TYPE_PRST		: value - имя стандартного цвета (map_prst_color)
      // c_oAscColor.COLOR_TYPE_SCHEME	: value - тип цвета в схеме
      // c_oAscColor.COLOR_TYPE_SYS		: конвертируется в srgb
      function CAscColorScheme()
      {
          this.Colors = [];
          this.Name = "";
      }
      CAscColorScheme.prototype.get_colors = function() { return this.Colors; };
      CAscColorScheme.prototype.get_name = function() { return this.Name; };

      //-----------------------------------------------------------------
      // События движения мыши
      //-----------------------------------------------------------------
      function CMouseMoveData( obj )
      {
          if( obj )
          {
              this.Type  = ( undefined != obj.Type ) ? obj.Type : c_oAscMouseMoveDataTypes.Common;
              this.X_abs = ( undefined != obj.X_abs ) ? obj.X_abs : 0;
              this.Y_abs = ( undefined != obj.Y_abs ) ? obj.Y_abs : 0;

              switch ( this.Type )
              {
                  case c_oAscMouseMoveDataTypes.Hyperlink :
                  {
                      this.Hyperlink = ( undefined != obj.PageNum ) ? obj.PageNum : 0;
                      break;
                  }

                  case c_oAscMouseMoveDataTypes.LockedObject :
                  {
                      this.UserId           = ( undefined != obj.UserId ) ? obj.UserId : "";
                      this.HaveChanges      = ( undefined != obj.HaveChanges ) ? obj.HaveChanges : false;
                      this.LockedObjectType = ( undefined != obj.LockedObjectType ) ? obj.LockedObjectType : Asc.c_oAscMouseMoveLockedObjectType.Common;
                      break;
                  }
              }
          }
          else
          {
              this.Type  = c_oAscMouseMoveDataTypes.Common;
              this.X_abs = 0;
              this.Y_abs = 0;
          }
      }
      CMouseMoveData.prototype.get_Type  = function()  { return this.Type; };
      CMouseMoveData.prototype.get_X = function()  { return this.X_abs; };
      CMouseMoveData.prototype.get_Y = function()  { return this.Y_abs; };
      CMouseMoveData.prototype.get_Hyperlink = function()  { return this.Hyperlink; };
      CMouseMoveData.prototype.get_UserId = function() { return this.UserId; };
      CMouseMoveData.prototype.get_HaveChanges = function() { return this.HaveChanges; };
      CMouseMoveData.prototype.get_LockedObjectType = function() { return this.LockedObjectType; };

      function asc_CUserInfo(obj)
      {
          if(obj)
          {
              if(typeof obj.Id != 'undefined'){
                  this.Id = obj.Id;
              }
              if(typeof obj.FullName != 'undefined'){
                  this.FullName = obj.FullName;
              }
              if(typeof obj.FirstName != 'undefined'){
                  this.FirstName = obj.FirstName;
              }
              if(typeof obj.LastName != 'undefined'){
                  this.LastName = obj.LastName;
              }
          }
          else
          {
              this.Id       = null;
              this.FullName = null;
              this.FirstName = null;
              this.LastName = null;
          }
      }
      asc_CUserInfo.prototype.asc_putId =   asc_CUserInfo.prototype.put_Id = function(v){this.Id = v;};
      asc_CUserInfo.prototype.asc_getId =   asc_CUserInfo.prototype.get_Id = function(){return this.Id;};
      asc_CUserInfo.prototype.asc_putFullName =  asc_CUserInfo.prototype.put_FullName = function(v){this.FullName = v;};
      asc_CUserInfo.prototype.asc_getFullName =  asc_CUserInfo.prototype.get_FullName = function(){return this.FullName;};
      asc_CUserInfo.prototype.asc_putFirstName = asc_CUserInfo.prototype.put_FirstName = function(v){this.FirstName = v;};
      asc_CUserInfo.prototype.asc_getFirstName = asc_CUserInfo.prototype.get_FirstName = function(){return this.FirstName;};
      asc_CUserInfo.prototype.asc_putLastName =  asc_CUserInfo.prototype.put_LastName = function(v){this.LastName = v;};
      asc_CUserInfo.prototype.asc_getLastName =  asc_CUserInfo.prototype.get_LastName = function(){return this.LastName;};

      function asc_CDocInfo (obj){
          if(obj){
              if (typeof obj.Id != 'undefined'){
                  this.Id = obj.Id;
              }
              if (typeof obj.Url != 'undefined'){
                  this.Url = obj.Url;
              }
              if (typeof obj.Title != 'undefined'){
                  this.Title = obj.Title;
              }
              if (typeof obj.Format != 'undefined'){
                  this.Format = obj.Format;
              }
              if (typeof obj.VKey != 'undefined'){
                  this.VKey = obj.VKey;
              }
              if (typeof obj.UserId != 'undefined'){
                  this.UserId = obj.UserId;
              }

              if(typeof obj.UserInfo != 'undefined'){
                  this.UserInfo = new asc_CUserInfo(obj.UserInfo);
              }

              if (typeof obj.Options != 'undefined'){
                  this.Options = obj.Options;
              }
              if (typeof obj.CallbackUrl != 'undefined'){
                  this.CallbackUrl = obj.CallbackUrl;
              }
              if (obj.OfflineApp === true)
                  this.OfflineApp = true;

              this.TemplateReplacement = (null != obj.TemplateReplacement ? obj.TemplateReplacement : null);

          }
          else
          {
              this.Id                  = null;
              this.Url                 = null;
              this.Title               = null;
              this.Format              = null;
              this.VKey                = null;
              this.UserInfo            = null;
              this.Options             = null;
              this.CallbackUrl         = null;
              this.TemplateReplacement = null;
          }
      }
      asc_CDocInfo.prototype.get_Id =  asc_CDocInfo.prototype.asc_getId = function(){return this.Id};
      asc_CDocInfo.prototype.put_Id =  asc_CDocInfo.prototype.asc_putId = function(v){this.Id = v;};
      asc_CDocInfo.prototype.get_Url = asc_CDocInfo.prototype.asc_getUrl = function(){return this.Url;};
      asc_CDocInfo.prototype.put_Url = asc_CDocInfo.prototype.asc_putUrl = function(v){this.Url = v;};
      asc_CDocInfo.prototype.get_Title =  asc_CDocInfo.prototype.asc_getTitle = function(){return this.Title;};
      asc_CDocInfo.prototype.put_Title =  asc_CDocInfo.prototype.asc_putTitle = function(v){this.Title = v;};
      asc_CDocInfo.prototype.get_Format = asc_CDocInfo.prototype.asc_getFormat = function(){return this.Format;};
      asc_CDocInfo.prototype.put_Format = asc_CDocInfo.prototype.asc_putFormat = function(v){this.Format = v;};
      asc_CDocInfo.prototype.get_VKey = asc_CDocInfo.prototype.asc_getVKey = function(){return this.VKey;};
      asc_CDocInfo.prototype.put_VKey = asc_CDocInfo.prototype.asc_putVKey = function(v){this.VKey = v;};
      asc_CDocInfo.prototype.get_OfflineApp = asc_CDocInfo.prototype.asc_getOfflineApp = function(){return this.OfflineApp;};
      asc_CDocInfo.prototype.put_OfflineApp = asc_CDocInfo.prototype.asc_putOfflineApp = function(v){this.OfflineApp = v;};
      asc_CDocInfo.prototype.get_UserId =  asc_CDocInfo.prototype.asc_getUserId = function(){return (this.UserInfo ? this.UserInfo.get_Id() : null );};
      asc_CDocInfo.prototype.get_UserName = asc_CDocInfo.prototype.asc_getUserName = function(){
          return (this.UserInfo ? this.UserInfo.get_FullName() : null );
      };
      asc_CDocInfo.prototype.get_Options =  asc_CDocInfo.prototype.asc_getOptions = function(){return this.Options;};
      asc_CDocInfo.prototype.put_Options =  asc_CDocInfo.prototype.asc_putOptions = function(v){this.Options = v;};
      asc_CDocInfo.prototype.get_CallbackUrl = asc_CDocInfo.prototype.asc_getCallbackUrl = function(){return this.CallbackUrl;};
      asc_CDocInfo.prototype.put_CallbackUrl = asc_CDocInfo.prototype.asc_putCallbackUrl = function(v){this.CallbackUrl = v;};
      asc_CDocInfo.prototype.get_TemplateReplacement = asc_CDocInfo.prototype.asc_getTemplateReplacement = function(){return this.TemplateReplacement;};
      asc_CDocInfo.prototype.put_TemplateReplacement = asc_CDocInfo.prototype.asc_putTemplateReplacement = function(v){this.TemplateReplacement = v;};
      asc_CDocInfo.prototype.get_UserInfo =  asc_CDocInfo.prototype.asc_getUserInfo = function(){return this.UserInfo;};
      asc_CDocInfo.prototype.put_UserInfo =  asc_CDocInfo.prototype.asc_putUserInfo = function(v){this.UserInfo = v;};

      function COpenProgress() {
          this.Type = Asc.c_oAscAsyncAction.Open;

          this.FontsCount = 0;
          this.CurrentFont = 0;

          this.ImagesCount = 0;
          this.CurrentImage = 0;
      }

      COpenProgress.prototype.asc_getType = function(){return this.Type};
      COpenProgress.prototype.asc_getFontsCount = function(){return this.FontsCount};
      COpenProgress.prototype.asc_getCurrentFont = function(){return this.CurrentFont};
      COpenProgress.prototype.asc_getImagesCount = function(){return this.ImagesCount};
      COpenProgress.prototype.asc_getCurrentImage = function(){return this.CurrentImage};

      function CErrorData()
      {
          this.Value = 0;
      }

      CErrorData.prototype.put_Value = function(v){ this.Value = v; };
      CErrorData.prototype.get_Value = function() { return this.Value; };

      function CAscMathType()
      {
          this.Id     = 0;

          this.X = 0;
          this.Y = 0;
      }
      CAscMathType.prototype.get_Id = function(){ return this.Id; };
      CAscMathType.prototype.get_X = function(){ return this.X; };
      CAscMathType.prototype.get_Y = function(){ return this.Y; };

      function CAscMathCategory()
      {
          this.Id     = 0;
          this.Data   = [];

          this.W      = 0;
          this.H      = 0;
      }

      CAscMathCategory.prototype.get_Id = function(){ return this.Id; };
      CAscMathCategory.prototype.get_Data = function(){ return this.Data; };
      CAscMathCategory.prototype.get_W = function(){ return this.W; };
      CAscMathCategory.prototype.get_H = function(){ return this.H; };
      CAscMathCategory.prototype.private_Sort = function(){ this.Data.sort( function(a,b){ return a.Id- b.Id; } ); };

      function CStyleImage(name, type, image, uiPriority) {
          this.name = name;
          this.type = type;
          this.image = image;
          this.uiPriority = uiPriority;
      }
      CStyleImage.prototype.asc_getName = CStyleImage.prototype.get_Name = function() { return this.name; };
      CStyleImage.prototype.asc_getType = CStyleImage.prototype.get_Type = function() { return this.type; };
      CStyleImage.prototype.asc_getImage = function() { return this.image; };

      /*
       * Export
       * -----------------------------------------------------------------------------
       */
      window['AscCommon'] = window['AscCommon'] || {};
      window['Asc'] = window['Asc'] || {};

      window['Asc']['c_oAscArrUserColors'] = window['Asc'].c_oAscArrUserColors = c_oAscArrUserColors;

      window["AscCommon"].CreateAscColorCustom = CreateAscColorCustom;
      window["AscCommon"].CreateAscColor = CreateAscColor;

    window["AscCommon"].asc_CAscEditorPermissions = asc_CAscEditorPermissions;
    prot = asc_CAscEditorPermissions.prototype;
    prot["asc_getCanLicense"] = prot.asc_getCanLicense;
    prot["asc_getCanCoAuthoring"] = prot.asc_getCanCoAuthoring;
    prot["asc_getCanReaderMode"] = prot.asc_getCanReaderMode;
    prot["asc_getCanBranding"] = prot.asc_getCanBranding;
    prot["asc_getIsAutosaveEnable"] = prot.asc_getIsAutosaveEnable;
    prot["asc_getAutosaveMinInterval"] = prot.asc_getAutosaveMinInterval;
    prot["asc_getIsAnalyticsEnable"] = prot.asc_getIsAnalyticsEnable;
    prot["asc_getIsLight"] = prot.asc_getIsLight;

      window["AscCommon"].asc_ValAxisSettings = asc_ValAxisSettings;
      prot = asc_ValAxisSettings.prototype;
      prot["putMinValRule"] = prot.putMinValRule;
      prot["putMinVal"] = prot.putMinVal;
      prot["putMaxValRule"] = prot.putMaxValRule;
      prot["putMaxVal"] = prot.putMaxVal;
      prot["putInvertValOrder"] = prot.putInvertValOrder;
      prot["putLogScale"] = prot.putLogScale;
      prot["putLogBase"] = prot.putLogBase;
      prot["putUnits"] = prot.putUnits;
      prot["putShowUnitsOnChart"] = prot.putShowUnitsOnChart;
      prot["putMajorTickMark"] = prot.putMajorTickMark;
      prot["putMinorTickMark"] = prot.putMinorTickMark;
      prot["putTickLabelsPos"] = prot.putTickLabelsPos;
      prot["putCrossesRule"] = prot.putCrossesRule;
      prot["putCrosses"] = prot.putCrosses;
      prot["putDispUnitsRule"] = prot.putDispUnitsRule;
      prot["getDispUnitsRule"] = prot.getDispUnitsRule;
      prot["putAxisType"] = prot.putAxisType;
      prot["getAxisType"] = prot.getAxisType;
      prot["getMinValRule"] = prot.getMinValRule;
      prot["getMinVal"] = prot.getMinVal;
      prot["getMaxValRule"] = prot.getMaxValRule;
      prot["getMaxVal"] = prot.getMaxVal;
      prot["getInvertValOrder"] = prot.getInvertValOrder;
      prot["getLogScale"] = prot.getLogScale;
      prot["getLogBase"] = prot.getLogBase;
      prot["getUnits"] = prot.getUnits;
      prot["getShowUnitsOnChart"] = prot.getShowUnitsOnChart;
      prot["getMajorTickMark"] = prot.getMajorTickMark;
      prot["getMinorTickMark"] = prot.getMinorTickMark;
      prot["getTickLabelsPos"] = prot.getTickLabelsPos;
      prot["getCrossesRule"] = prot.getCrossesRule;
      prot["getCrosses"] = prot.getCrosses;
      prot["setDefault"] = prot.setDefault;

      window["AscCommon"].asc_CatAxisSettings = asc_CatAxisSettings;
      prot = asc_CatAxisSettings.prototype;
      prot["putIntervalBetweenTick"] = prot.putIntervalBetweenTick;
      prot["putIntervalBetweenLabelsRule"] = prot.putIntervalBetweenLabelsRule;
      prot["putIntervalBetweenLabels"] = prot.putIntervalBetweenLabels;
      prot["putInvertCatOrder"] = prot.putInvertCatOrder;
      prot["putLabelsAxisDistance"] = prot.putLabelsAxisDistance;
      prot["putMajorTickMark"] = prot.putMajorTickMark;
      prot["putMinorTickMark"] = prot.putMinorTickMark;
      prot["putTickLabelsPos"] = prot.putTickLabelsPos;
      prot["putCrossesRule"] = prot.putCrossesRule;
      prot["putCrosses"] = prot.putCrosses;
      prot["putAxisType"] = prot.putAxisType;
      prot["putLabelsPosition"] = prot.putLabelsPosition;
      prot["putCrossMaxVal"] = prot.putCrossMaxVal;
      prot["putCrossMinVal"] = prot.putCrossMinVal;
      prot["getIntervalBetweenTick"] = prot.getIntervalBetweenTick;
      prot["getIntervalBetweenLabelsRule"] = prot.getIntervalBetweenLabelsRule;
      prot["getIntervalBetweenLabels"] = prot.getIntervalBetweenLabels;
      prot["getInvertCatOrder"] = prot.getInvertCatOrder;
      prot["getLabelsAxisDistance"] = prot.getLabelsAxisDistance;
      prot["getMajorTickMark"] = prot.getMajorTickMark;
      prot["getMinorTickMark"] = prot.getMinorTickMark;
      prot["getTickLabelsPos"] = prot.getTickLabelsPos;
      prot["getCrossesRule"] = prot.getCrossesRule;
      prot["getCrosses"] = prot.getCrosses;
      prot["getAxisType"] = prot.getAxisType;
      prot["getLabelsPosition"] = prot.getLabelsPosition;
      prot["getCrossMaxVal"] = prot.getCrossMaxVal;
      prot["getCrossMinVal"] = prot.getCrossMinVal;
      prot["setDefault"] = prot.setDefault;

      window["AscCommon"].asc_ChartSettings = asc_ChartSettings;
      prot = asc_ChartSettings.prototype;
      prot["putStyle"] = prot.putStyle;
      prot["putTitle"] = prot.putTitle;
      prot["putRowCols"] = prot.putRowCols;
      prot["putHorAxisLabel"] = prot.putHorAxisLabel;
      prot["putVertAxisLabel"] = prot.putVertAxisLabel;
      prot["putLegendPos"] = prot.putLegendPos;
      prot["putDataLabelsPos"] = prot.putDataLabelsPos;
      prot["putCatAx"] = prot.putCatAx;
      prot["putValAx"] = prot.putValAx;
      prot["getStyle"] = prot.getStyle;
      prot["getTitle"] = prot.getTitle;
      prot["getRowCols"] = prot.getRowCols;
      prot["getHorAxisLabel"] = prot.getHorAxisLabel;
      prot["getVertAxisLabel"] = prot.getVertAxisLabel;
      prot["getLegendPos"] = prot.getLegendPos;
      prot["getDataLabelsPos"] = prot.getDataLabelsPos;
      prot["getHorAx"] = prot.getHorAx;
      prot["getVertAx"] = prot.getVertAx;
      prot["getHorGridLines"] = prot.getHorGridLines;
      prot["putHorGridLines"] = prot.putHorGridLines;
      prot["getVertGridLines"] = prot.getVertGridLines;
      prot["putVertGridLines"] = prot.putVertGridLines;
      prot["getType"] = prot.getType;
      prot["putType"] = prot.putType;
      prot["putShowSerName"] = prot.putShowSerName;
      prot["getShowSerName"] = prot.getShowSerName;
      prot["putShowCatName"] = prot.putShowCatName;
      prot["getShowCatName"] = prot.getShowCatName;
      prot["putShowVal"] = prot.putShowVal;
      prot["getShowVal"] = prot.getShowVal;
      prot["putSeparator"] = prot.putSeparator;
      prot["getSeparator"] = prot.getSeparator;
      prot["putHorAxisProps"] = prot.putHorAxisProps;
      prot["getHorAxisProps"] = prot.getHorAxisProps;
      prot["putVertAxisProps"] = prot.putVertAxisProps;
      prot["getVertAxisProps"] = prot.getVertAxisProps;
      prot["putRange"] = prot.putRange;
      prot["getRange"] = prot.getRange;
      prot["putInColumns"] = prot.putInColumns;
      prot["getInColumns"] = prot.getInColumns;
      prot["putShowMarker"] = prot.putShowMarker;
      prot["getShowMarker"] = prot.getShowMarker;
      prot["putLine"] = prot.putLine;
      prot["getLine"] = prot.getLine;
      prot["putSmooth"] = prot.putSmooth;
      prot["getSmooth"] = prot.getSmooth;
      prot["changeType"] = prot.changeType;
      prot["putShowHorAxis"] = prot.putShowHorAxis;
      prot["getShowHorAxis"] = prot.getShowHorAxis;
      prot["putShowVerAxis"]   = prot.putShowVerAxis;
      prot["getShowVerAxis"]   = prot.getShowVerAxis;

      window["AscCommon"].asc_CRect = asc_CRect;
      prot = asc_CRect.prototype;
      prot["asc_getX"]			= prot.asc_getX;
      prot["asc_getY"]			= prot.asc_getY;
      prot["asc_getWidth"]		= prot.asc_getWidth;
      prot["asc_getHeight"]		= prot.asc_getHeight;

      window["AscCommon"].CColor = CColor;
      prot = CColor.prototype;
      prot["getR"]	= prot.getR;
      prot["get_r"]	= prot.get_r;
      prot["put_r"]	= prot.put_r;
      prot["getG"]	= prot.getG;
      prot["get_g"]	= prot.get_g;
      prot["put_g"]	= prot.put_g;
      prot["getB"]	= prot.getB;
      prot["get_b"]	= prot.get_b;
      prot["put_b"]	= prot.put_b;
      prot["getA"]	= prot.getA;
      prot["get_hex"]	= prot.get_hex;

      window["Asc"]["asc_CColor"] = window["Asc"].asc_CColor = asc_CColor;
      prot = asc_CColor.prototype;
      prot["get_r"] = prot["asc_getR"] = prot.asc_getR;
      prot["put_r"] = prot["asc_putR"] = prot.asc_putR;
      prot["get_g"] = prot["asc_getG"] = prot.asc_getG;
      prot["put_g"] = prot["asc_putG"] = prot.asc_putG;
      prot["get_b"] = prot["asc_getB"] = prot.asc_getB;
      prot["put_b"] = prot["asc_putB"] = prot.asc_putB;
      prot["get_a"] = prot["asc_getA"] = prot.asc_getA;
      prot["put_a"] = prot["asc_putA"] = prot.asc_putA;
      prot["get_auto"] = prot["asc_getAuto"] = prot.asc_getAuto;
      prot["put_auto"] = prot["asc_putAuto"] = prot.asc_putAuto;
      prot["get_type"] = prot["asc_getType"] = prot.asc_getType;
      prot["put_type"] = prot["asc_putType"] = prot.asc_putType;
      prot["get_value"] = prot["asc_getValue"] = prot.asc_getValue;
      prot["put_value"] = prot["asc_putValue"] = prot.asc_putValue;
      prot["get_hex"] = prot["asc_getHex"] = prot.asc_getHex;
      prot["get_color"] = prot["asc_getColor"] = prot.asc_getColor;
      prot["get_hex"] = prot["asc_getHex"] = prot.asc_getHex;

      window["Asc"]["asc_CTextBorder"] = window["Asc"].asc_CTextBorder = asc_CTextBorder;
      prot = asc_CTextBorder.prototype;
      prot["get_Color"] = prot["asc_getColor"] = prot.asc_getColor;
      prot["put_Color"] = prot["asc_putColor"] = prot.asc_putColor;
      prot["get_Size"] = prot["asc_getSize"] = prot.asc_getSize;
      prot["put_Size"] = prot["asc_putSize"] = prot.asc_putSize;
      prot["get_Value"] = prot["asc_getValue"] = prot.asc_getValue;
      prot["put_Value"] = prot["asc_putValue"] = prot.asc_putValue;
      prot["get_Space"] = prot["asc_getSpace"] = prot.asc_getSpace;
      prot["put_Space"] = prot["asc_putSpace"] = prot.asc_putSpace;
      prot["get_ForSelectedCells"] = prot["asc_getForSelectedCells"] = prot.asc_getForSelectedCells;
      prot["put_ForSelectedCells"] = prot["asc_putForSelectedCells"] = prot.asc_putForSelectedCells;

      window["Asc"]["asc_CParagraphBorders"] = asc_CParagraphBorders;
      prot = asc_CParagraphBorders.prototype;
      prot["get_Left"] = prot["asc_getLeft"] = prot.asc_getLeft;
      prot["put_Left"] = prot["asc_putLeft"] = prot.asc_putLeft;
      prot["get_Top"] = prot["asc_getTop"] = prot.asc_getTop;
      prot["put_Top"] = prot["asc_putTop"] = prot.asc_putTop;
      prot["get_Right"] = prot["asc_getRight"] = prot.asc_getRight;
      prot["put_Right"] = prot["asc_putRight"] = prot.asc_putRight;
      prot["get_Bottom"] = prot["asc_getBottom"] = prot.asc_getBottom;
      prot["put_Bottom"] = prot["asc_putBottom"] = prot.asc_putBottom;
      prot["get_Between"] = prot["asc_getBetween"] = prot.asc_getBetween;
      prot["put_Between"] = prot["asc_putBetween"] = prot.asc_putBetween;

      window["AscCommon"].asc_CListType = asc_CListType;
      prot = asc_CListType.prototype;
      prot["get_ListType"] = prot["asc_getListType"] = prot.asc_getListType;
      prot["get_ListSubType"] = prot["asc_getListSubType"] = prot.asc_getListSubType;

      window["AscCommon"].asc_CTextFontFamily = asc_CTextFontFamily;
      prot = asc_CTextFontFamily.prototype;
      prot["get_Name"] = prot["asc_getName"] = prot.asc_getName;
      prot["get_Index"] = prot["asc_getIndex"] = prot.asc_getIndex;

      window["Asc"]["asc_CParagraphTab"] = window["Asc"].asc_CParagraphTab = asc_CParagraphTab;
      prot = asc_CParagraphTab.prototype;
      prot["get_Value"] = prot["asc_getValue"] = prot.asc_getValue;
      prot["put_Value"] = prot["asc_putValue"] = prot.asc_putValue;
      prot["get_Pos"] = prot["asc_getPos"] = prot.asc_getPos;
      prot["put_Pos"] = prot["asc_putPos"] = prot.asc_putPos;

      window["Asc"]["asc_CParagraphTabs"] = window["Asc"].asc_CParagraphTabs = asc_CParagraphTabs;
      prot = asc_CParagraphTabs.prototype;
      prot["get_Count"] = prot["asc_getCount"] = prot.asc_getCount;
      prot["get_Tab"] = prot["asc_getTab"] = prot.asc_getTab;
      prot["add_Tab"] = prot["asc_addTab"] = prot.asc_addTab;
      prot["clear"] = prot.clear = prot["asc_clear"] = prot.asc_clear;

      window["Asc"]["asc_CParagraphShd"] = window["Asc"].asc_CParagraphShd = asc_CParagraphShd;
      prot = asc_CParagraphShd.prototype;
      prot["get_Value"] = prot["asc_getValue"] = prot.asc_getValue;
      prot["put_Value"] = prot["asc_putValue"] = prot.asc_putValue;
      prot["get_Color"] = prot["asc_getColor"] = prot.asc_getColor;
      prot["put_Color"] = prot["asc_putColor"] = prot.asc_putColor;

      window["Asc"]["asc_CParagraphFrame"] = window["Asc"].asc_CParagraphFrame = asc_CParagraphFrame;
      prot = asc_CParagraphFrame.prototype;
      prot["asc_getDropCap"]         = prot["get_DropCap"]         = prot.asc_getDropCap;
      prot["asc_putDropCap"]         = prot["put_DropCap"]         = prot.asc_putDropCap;
      prot["asc_getH"]               = prot["get_H"]               = prot.asc_getH;
      prot["asc_putH"]               = prot["put_H"]               = prot.asc_putH;
      prot["asc_getHAnchor"]         = prot["get_HAnchor"]         = prot.asc_getHAnchor;
      prot["asc_putHAnchor"]         = prot["put_HAnchor"]         = prot.asc_putHAnchor;
      prot["asc_getHRule"]           = prot["get_HRule"]           = prot.asc_getHRule;
      prot["asc_putHRule"]           = prot["put_HRule"]           = prot.asc_putHRule;
      prot["asc_getHSpace"]          = prot["get_HSpace"]          = prot.asc_getHSpace;
      prot["asc_putHSpace"]          = prot["put_HSpace"]          = prot.asc_putHSpace;
      prot["asc_getLines"]           = prot["get_Lines"]           = prot.asc_getLines;
      prot["asc_putLines"]           = prot["put_Lines"]           = prot.asc_putLines;
      prot["asc_getVAnchor"]         = prot["get_VAnchor"]         = prot.asc_getVAnchor;
      prot["asc_putVAnchor"]         = prot["put_VAnchor"]         = prot.asc_putVAnchor;
      prot["asc_getVSpace"]          = prot["get_VSpace"]          = prot.asc_getVSpace;
      prot["asc_putVSpace"]          = prot["put_VSpace"]          = prot.asc_putVSpace;
      prot["asc_getW"]               = prot["get_W"]               = prot.asc_getW;
      prot["asc_putW"]               = prot["put_W"]               = prot.asc_putW;
      prot["asc_getWrap"]            = prot["get_Wrap"]            = prot.asc_getWrap;
      prot["asc_putWrap"]            = prot["put_Wrap"]            = prot.asc_putWrap;
      prot["asc_getX"]               = prot["get_X"]               = prot.asc_getX;
      prot["asc_putX"]               = prot["put_X"]               = prot.asc_putX;
      prot["asc_getXAlign"]          = prot["get_XAlign"]          = prot.asc_getXAlign;
      prot["asc_putXAlign"]          = prot["put_XAlign"]          = prot.asc_putXAlign;
      prot["asc_getY"]               = prot["get_Y"]               = prot.asc_getY;
      prot["asc_putY"]               = prot["put_Y"]               = prot.asc_putY;
      prot["asc_getYAlign"]          = prot["get_YAlign"]          = prot.asc_getYAlign;
      prot["asc_putYAlign"]          = prot["put_YAlign"]          = prot.asc_putYAlign;
      prot["asc_getBorders"]         = prot["get_Borders"]         = prot.asc_getBorders;
      prot["asc_putBorders"]         = prot["put_Borders"]         = prot.asc_putBorders;
      prot["asc_getShade"]           = prot["get_Shade"]           = prot.asc_getShade;
      prot["asc_putShade"]           = prot["put_Shade"]           = prot.asc_putShade;
      prot["asc_getFontFamily"]      = prot["get_FontFamily"]      = prot.asc_getFontFamily;
      prot["asc_putFontFamily"]      = prot["put_FontFamily"]      = prot.asc_putFontFamily;
      prot["asc_putFromDropCapMenu"] = prot["put_FromDropCapMenu"] = prot.asc_putFromDropCapMenu;

      window["AscCommon"].asc_CParagraphSpacing = asc_CParagraphSpacing;
      prot = asc_CParagraphSpacing.prototype;
      prot["get_Line"] = prot["asc_getLine"] = prot.asc_getLine;
      prot["get_LineRule"] = prot["asc_getLineRule"] = prot.asc_getLineRule;
      prot["get_Before"] = prot["asc_getBefore"] = prot.asc_getBefore;
      prot["get_After"] = prot["asc_getAfter"] = prot.asc_getAfter;

      window["Asc"]["asc_CParagraphInd"] = window["Asc"].asc_CParagraphInd = asc_CParagraphInd;
      prot = asc_CParagraphInd.prototype;
      prot["get_Left"] = prot["asc_getLeft"] = prot.asc_getLeft;
      prot["put_Left"] = prot["asc_putLeft"] = prot.asc_putLeft;
      prot["get_Right"] = prot["asc_getRight"] = prot.asc_getRight;
      prot["put_Right"] = prot["asc_putRight"] = prot.asc_putRight;
      prot["get_FirstLine"] = prot["asc_getFirstLine"] = prot.asc_getFirstLine;
      prot["put_FirstLine"] = prot["asc_putFirstLine"] = prot.asc_putFirstLine;

      window["Asc"]["asc_CParagraphProperty"] = window["Asc"].asc_CParagraphProperty = asc_CParagraphProperty;
      prot = asc_CParagraphProperty.prototype;
      prot["get_ContextualSpacing"] = prot["asc_getContextualSpacing"] = prot.asc_getContextualSpacing;
      prot["put_ContextualSpacing"] = prot["asc_putContextualSpacing"] = prot.asc_putContextualSpacing;
      prot["get_Ind"] = prot["asc_getInd"] = prot.asc_getInd;
      prot["put_Ind"] = prot["asc_putInd"] = prot.asc_putInd;
      prot["get_KeepLines"] = prot["asc_getKeepLines"] = prot.asc_getKeepLines;
      prot["put_KeepLines"] = prot["asc_putKeepLines"] = prot.asc_putKeepLines;
      prot["get_KeepNext"] = prot["asc_getKeepNext"] = prot.asc_getKeepNext;
      prot["put_KeepNext"] = prot["asc_putKeepNext"] = prot.asc_putKeepNext;
      prot["get_PageBreakBefore"] = prot["asc_getPageBreakBefore"] = prot.asc_getPageBreakBefore;
      prot["put_PageBreakBefore"] = prot["asc_putPageBreakBefore"] = prot.asc_putPageBreakBefore;
      prot["get_WidowControl"] = prot["asc_getWidowControl"] = prot.asc_getWidowControl;
      prot["put_WidowControl"] = prot["asc_putWidowControl"] = prot.asc_putWidowControl;
      prot["get_Spacing"] = prot["asc_getSpacing"] = prot.asc_getSpacing;
      prot["put_Spacing"] = prot["asc_putSpacing"] = prot.asc_putSpacing;
      prot["get_Borders"] = prot["asc_getBorders"] = prot.asc_getBorders;
      prot["put_Borders"] = prot["asc_putBorders"] = prot.asc_putBorders;
      prot["get_Shade"] = prot["asc_getShade"] = prot.asc_getShade;
      prot["put_Shade"] = prot["asc_putShade"] = prot.asc_putShade;
      prot["get_Locked"] = prot["asc_getLocked"] = prot.asc_getLocked;
      prot["get_CanAddTable"] = prot["asc_getCanAddTable"] = prot.asc_getCanAddTable;
      prot["get_Subscript"] = prot["asc_getSubscript"] = prot.asc_getSubscript;
      prot["put_Subscript"] = prot["asc_putSubscript"] = prot.asc_putSubscript;
      prot["get_Superscript"] = prot["asc_getSuperscript"] = prot.asc_getSuperscript;
      prot["put_Superscript"] = prot["asc_putSuperscript"] = prot.asc_putSuperscript;
      prot["get_SmallCaps"] = prot["asc_getSmallCaps"] = prot.asc_getSmallCaps;
      prot["put_SmallCaps"] = prot["asc_putSmallCaps"] = prot.asc_putSmallCaps;
      prot["get_AllCaps"] = prot["asc_getAllCaps"] = prot.asc_getAllCaps;
      prot["put_AllCaps"] = prot["asc_putAllCaps"] = prot.asc_putAllCaps;
      prot["get_Strikeout"] = prot["asc_getStrikeout"] = prot.asc_getStrikeout;
      prot["put_Strikeout"] = prot["asc_putStrikeout"] = prot.asc_putStrikeout;
      prot["get_DStrikeout"] = prot["asc_getDStrikeout"] = prot.asc_getDStrikeout;
      prot["put_DStrikeout"] = prot["asc_putDStrikeout"] = prot.asc_putDStrikeout;
      prot["get_TextSpacing"] = prot["asc_getTextSpacing"] = prot.asc_getTextSpacing;
      prot["put_TextSpacing"] = prot["asc_putTextSpacing"] = prot.asc_putTextSpacing;
      prot["get_Position"] = prot["asc_getPosition"] = prot.asc_getPosition;
      prot["put_Position"] = prot["asc_putPosition"] = prot.asc_putPosition;
      prot["get_Tabs"] = prot["asc_getTabs"] = prot.asc_getTabs;
      prot["put_Tabs"] = prot["asc_putTabs"] = prot.asc_putTabs;
      prot["get_DefaultTab"] = prot["asc_getDefaultTab"] = prot.asc_getDefaultTab;
      prot["put_DefaultTab"] = prot["asc_putDefaultTab"] = prot.asc_putDefaultTab;
      prot["get_FramePr"] = prot["asc_getFramePr"] = prot.asc_getFramePr;
      prot["put_FramePr"] = prot["asc_putFramePr"] = prot.asc_putFramePr;
      prot["get_CanAddDropCap"] = prot["asc_getCanAddDropCap"] = prot.asc_getCanAddDropCap;
      prot["get_CanAddImage"] = prot["asc_getCanAddImage"] = prot.asc_getCanAddImage;

      window["AscCommon"].asc_CTexture = asc_CTexture;
      prot = asc_CTexture.prototype;
      prot["get_id"] = prot["asc_getId"] = prot.asc_getId;
      prot["get_image"] = prot["asc_getImage"] = prot.asc_getImage;

      window["AscCommon"].asc_CImageSize = asc_CImageSize;
      prot = asc_CImageSize.prototype;
      prot["get_ImageWidth"] = prot["asc_getImageWidth"] = prot.asc_getImageWidth;
      prot["get_ImageHeight"] = prot["asc_getImageHeight"] = prot.asc_getImageHeight;
      prot["get_IsCorrect"] = prot["asc_getIsCorrect"] = prot.asc_getIsCorrect;

      window["Asc"]["asc_CPaddings"] = window["Asc"].asc_CPaddings = asc_CPaddings;
      prot = asc_CPaddings.prototype;
      prot["get_Left"] = prot["asc_getLeft"] = prot.asc_getLeft;
      prot["put_Left"] = prot["asc_putLeft"] = prot.asc_putLeft;
      prot["get_Top"] = prot["asc_getTop"] = prot.asc_getTop;
      prot["put_Top"] = prot["asc_putTop"] = prot.asc_putTop;
      prot["get_Bottom"] = prot["asc_getBottom"] = prot.asc_getBottom;
      prot["put_Bottom"] = prot["asc_putBottom"] = prot.asc_putBottom;
      prot["get_Right"] = prot["asc_getRight"] = prot.asc_getRight;
      prot["put_Right"] = prot["asc_putRight"] = prot.asc_putRight;

      window["Asc"]["asc_CShapeProperty"] = window["Asc"].asc_CShapeProperty = asc_CShapeProperty;
      prot = asc_CShapeProperty.prototype;
      prot["get_type"] = prot["asc_getType"] = prot.asc_getType;
      prot["put_type"] = prot["asc_putType"] = prot.asc_putType;
      prot["get_fill"] = prot["asc_getFill"] = prot.asc_getFill;
      prot["put_fill"] = prot["asc_putFill"] = prot.asc_putFill;
      prot["get_stroke"] = prot["asc_getStroke"] = prot.asc_getStroke;
      prot["put_stroke"] = prot["asc_putStroke"] = prot.asc_putStroke;
      prot["get_paddings"] = prot["asc_getPaddings"] = prot.asc_getPaddings;
      prot["put_paddings"] = prot["asc_putPaddings"] = prot.asc_putPaddings;
      prot["get_CanFill"] = prot["asc_getCanFill"] = prot.asc_getCanFill;
      prot["put_CanFill"] = prot["asc_putCanFill"] = prot.asc_putCanFill;
      prot["get_CanChangeArrows"] = prot["asc_getCanChangeArrows"] = prot.asc_getCanChangeArrows;
      prot["set_CanChangeArrows"] = prot["asc_setCanChangeArrows"] = prot.asc_setCanChangeArrows;
      prot["get_FromChart"] = prot["asc_getFromChart"] = prot.asc_getFromChart;
      prot["set_FromChart"] = prot["asc_setFromChart"] = prot.asc_setFromChart;
      prot["get_Locked"] = prot["asc_getLocked"] = prot.asc_getLocked;
      prot["set_Locked"] = prot["asc_setLocked"] = prot.asc_setLocked;
      prot["get_Width"] = prot["asc_getWidth"] = prot.asc_getWidth;
      prot["put_Width"] = prot["asc_putWidth"] = prot.asc_putWidth;
      prot["get_Height"] = prot["asc_getHeight"] = prot.asc_getHeight;
      prot["put_Height"] = prot["asc_putHeight"] = prot.asc_putHeight;
      prot["get_VerticalTextAlign"] = prot["asc_getVerticalTextAlign"] = prot.asc_getVerticalTextAlign;
      prot["put_VerticalTextAlign"] = prot["asc_putVerticalTextAlign"] = prot.asc_putVerticalTextAlign;
      prot["get_Vert"] = prot["asc_getVert"] = prot.asc_getVert;
      prot["put_Vert"] = prot["asc_putVert"] = prot.asc_putVert;
      prot["get_TextArtProperties"] = prot["asc_getTextArtProperties"] = prot.asc_getTextArtProperties;
      prot["put_TextArtProperties"] = prot["asc_putTextArtProperties"] = prot.asc_putTextArtProperties;
      prot["get_LockAspect"] = prot["asc_getLockAspect"] = prot.asc_getLockAspect;
      prot["put_LockAspect"] = prot["asc_putLockAspect"] = prot.asc_putLockAspect;

      window["Asc"]["asc_TextArtProperties"] = window["Asc"].asc_TextArtProperties = asc_TextArtProperties;
      prot = asc_TextArtProperties.prototype;
      prot["asc_putFill"] = prot.asc_putFill;
      prot["asc_getFill"] = prot.asc_getFill;
      prot["asc_putLine"] = prot.asc_putLine;
      prot["asc_getLine"] = prot.asc_getLine;
      prot["asc_putForm"] = prot.asc_putForm;
      prot["asc_getForm"] = prot.asc_getForm;
      prot["asc_putStyle"] = prot.asc_putStyle;
      prot["asc_getStyle"] = prot.asc_getStyle;

    window["Asc"]["asc_CChartTranslate"] = window["Asc"].asc_CChartTranslate = asc_CChartTranslate;
    prot = asc_CChartTranslate.prototype;
    prot["asc_getTitle"] = prot.asc_getTitle;
    prot["asc_setTitle"] = prot.asc_setTitle;
    prot["asc_getXAxis"] = prot.asc_getXAxis;
    prot["asc_setXAxis"] = prot.asc_setXAxis;
    prot["asc_getYAxis"] = prot.asc_getYAxis;
    prot["asc_setYAxis"] = prot.asc_setYAxis;
    prot["asc_getSeries"] = prot.asc_getSeries;
    prot["asc_setSeries"] = prot.asc_setSeries;

      window["Asc"]["asc_TextArtTranslate"] = window["Asc"].asc_TextArtTranslate = asc_TextArtTranslate;
      prot = asc_TextArtTranslate.prototype;
      prot["asc_setDefaultText"] = prot.asc_setDefaultText;

      window['Asc']['CImagePositionH'] = window["Asc"].CImagePositionH = CImagePositionH;
      prot = CImagePositionH.prototype;
      prot['get_RelativeFrom'] = prot.get_RelativeFrom;
      prot['put_RelativeFrom'] = prot.put_RelativeFrom;
      prot['get_UseAlign'] = prot.get_UseAlign;
      prot['put_UseAlign'] = prot.put_UseAlign;
      prot['get_Align'] = prot.get_Align;
      prot['put_Align'] = prot.put_Align;
      prot['get_Value'] = prot.get_Value;
      prot['put_Value'] = prot.put_Value;
      prot['get_Percent'] = prot.get_Percent;
      prot['put_Percent'] = prot.put_Percent;

      window['Asc']['CImagePositionV'] = window["Asc"].CImagePositionV = CImagePositionV;
      prot = CImagePositionV.prototype;
      prot['get_RelativeFrom'] = prot.get_RelativeFrom;
      prot['put_RelativeFrom'] = prot.put_RelativeFrom;
      prot['get_UseAlign'] = prot.get_UseAlign;
      prot['put_UseAlign'] = prot.put_UseAlign;
      prot['get_Align'] = prot.get_Align;
      prot['put_Align'] = prot.put_Align;
      prot['get_Value'] = prot.get_Value;
      prot['put_Value'] = prot.put_Value;
      prot['get_Percent'] = prot.get_Percent;
      prot['put_Percent'] = prot.put_Percent;

      window['Asc']['CPosition'] = window["Asc"].CPosition = CPosition;
      prot = CPosition.prototype;
      prot['get_X'] = prot.get_X;
      prot['put_X'] = prot.put_X;
      prot['get_Y'] = prot.get_Y;
      prot['put_Y'] = prot.put_Y;

      window["Asc"]["asc_CImgProperty"] = window["Asc"].asc_CImgProperty = asc_CImgProperty;
      prot = asc_CImgProperty.prototype;
      prot["get_ChangeLevel"] = prot["asc_getChangeLevel"] = prot.asc_getChangeLevel;
      prot["put_ChangeLevel"] = prot["asc_putChangeLevel"] = prot.asc_putChangeLevel;
      prot["get_CanBeFlow"] = prot["asc_getCanBeFlow"] = prot.asc_getCanBeFlow;
      prot["get_Width"] =  prot["asc_getWidth"] = prot.asc_getWidth;
      prot["put_Width"] = prot["asc_putWidth"] = prot.asc_putWidth;
      prot["get_Height"] = prot["asc_getHeight"] = prot.asc_getHeight;
      prot["put_Height"] = prot["asc_putHeight"] = prot.asc_putHeight;
      prot["get_WrappingStyle"] = prot["asc_getWrappingStyle"] = prot.asc_getWrappingStyle;
      prot["put_WrappingStyle"] = prot["asc_putWrappingStyle"] = prot.asc_putWrappingStyle;
      prot["get_Paddings"] = prot["asc_getPaddings"] = prot.asc_getPaddings;
      prot["put_Paddings"] = prot["asc_putPaddings"] = prot.asc_putPaddings;
      prot["get_AllowOverlap"] = prot["asc_getAllowOverlap"] = prot.asc_getAllowOverlap;
      prot["put_AllowOverlap"] = prot["asc_putAllowOverlap"] = prot.asc_putAllowOverlap;
      prot["get_Position"] = prot["asc_getPosition"] = prot.asc_getPosition;
      prot["put_Position"] = prot["asc_putPosition"] = prot.asc_putPosition;
      prot["get_PositionH"] = prot["asc_getPositionH"] = prot.asc_getPositionH;
      prot["put_PositionH"] = prot["asc_putPositionH"] = prot.asc_putPositionH;
      prot["get_PositionV"] = prot["asc_getPositionV"] = prot.asc_getPositionV;
      prot["put_PositionV"] = prot["asc_putPositionV"] = prot.asc_putPositionV;
      prot["get_SizeRelH"] = prot["asc_getSizeRelH"] = prot.asc_getSizeRelH;
      prot["put_SizeRelH"] = prot["asc_putSizeRelH"] = prot.asc_putSizeRelH;
      prot["get_SizeRelV"] = prot["asc_getSizeRelV"] = prot.asc_getSizeRelV;
      prot["put_SizeRelV"] = prot["asc_putSizeRelV"] = prot.asc_putSizeRelV;
      prot["get_Value_X"] = prot["asc_getValue_X"] = prot.asc_getValue_X;
      prot["get_Value_Y"] = prot["asc_getValue_Y"] = prot.asc_getValue_Y;
      prot["get_ImageUrl"] = prot["asc_getImageUrl"] = prot.asc_getImageUrl;
      prot["put_ImageUrl"] = prot["asc_putImageUrl"] = prot.asc_putImageUrl;
      prot["get_Group"] = prot["asc_getGroup"] = prot.asc_getGroup;
      prot["put_Group"] = prot["asc_putGroup"] = prot.asc_putGroup;
      prot["get_FromGroup"] = prot["asc_getFromGroup"] = prot.asc_getFromGroup;
      prot["put_FromGroup"] = prot["asc_putFromGroup"] = prot.asc_putFromGroup;
      prot["get_isChartProps"] = prot["asc_getisChartProps"] = prot.asc_getisChartProps;
      prot["put_isChartPross"] = prot["asc_putisChartPross"] = prot.asc_putisChartPross;
      prot["get_SeveralCharts"] = prot["asc_getSeveralCharts"] = prot.asc_getSeveralCharts;
      prot["put_SeveralCharts"] = prot["asc_putSeveralCharts"] = prot.asc_putSeveralCharts;
      prot["get_SeveralChartTypes"] = prot["asc_getSeveralChartTypes"] = prot.asc_getSeveralChartTypes;
      prot["put_SeveralChartTypes"] = prot["asc_putSeveralChartTypes"] = prot.asc_putSeveralChartTypes;
      prot["get_SeveralChartStyles"] = prot["asc_getSeveralChartStyles"] = prot.asc_getSeveralChartStyles;
      prot["put_SeveralChartStyles"] = prot["asc_putSeveralChartStyles"] = prot.asc_putSeveralChartStyles;
      prot["get_VerticalTextAlign"] = prot["asc_getVerticalTextAlign"] = prot.asc_getVerticalTextAlign;
      prot["put_VerticalTextAlign"] = prot["asc_putVerticalTextAlign"] = prot.asc_putVerticalTextAlign;
      prot["get_Vert"] = prot["asc_getVert"] = prot.asc_getVert;
      prot["put_Vert"] = prot["asc_putVert"] = prot.asc_putVert;
      prot["get_Locked"] = prot["asc_getLocked"] = prot.asc_getLocked;
      prot["getLockAspect"] = prot["asc_getLockAspect"] = prot.asc_getLockAspect;
      prot["putLockAspect"] = prot["asc_putLockAspect"] = prot.asc_putLockAspect;
      prot["get_ChartProperties"] = prot["asc_getChartProperties"] = prot.asc_getChartProperties;
      prot["put_ChartProperties"] = prot["asc_putChartProperties"] = prot.asc_putChartProperties;
      prot["get_ShapeProperties"] = prot["asc_getShapeProperties"] = prot.asc_getShapeProperties;
      prot["put_ShapeProperties"] = prot["asc_putShapeProperties"] = prot.asc_putShapeProperties;
      prot["get_OriginSize"] = prot["asc_getOriginSize"] = prot.asc_getOriginSize;
      prot["get_PluginGuid"] = prot["asc_getPluginGuid"] = prot.asc_getPluginGuid;
      prot["put_PluginGuid"] = prot["asc_putPluginGuid"] = prot.asc_putPluginGuid;
      prot["get_PluginData"] = prot["asc_getPluginData"] = prot.asc_getPluginData;
      prot["put_PluginData"] = prot["asc_putPluginData"] = prot.asc_putPluginData;

      window["AscCommon"].asc_CSelectedObject = asc_CSelectedObject;
      prot = asc_CSelectedObject.prototype;
      prot["get_ObjectType"] = prot["asc_getObjectType"] = prot.asc_getObjectType;
      prot["get_ObjectValue"] = prot["asc_getObjectValue"] = prot.asc_getObjectValue;

      window["Asc"]["asc_CShapeFill"] = window["Asc"].asc_CShapeFill = asc_CShapeFill;
      prot = asc_CShapeFill.prototype;
      prot["get_type"] = prot["asc_getType"] = prot.asc_getType;
      prot["put_type"] = prot["asc_putType"] = prot.asc_putType;
      prot["get_fill"] = prot["asc_getFill"] = prot.asc_getFill;
      prot["put_fill"] = prot["asc_putFill"] = prot.asc_putFill;
      prot["get_transparent"] = prot["asc_getTransparent"] = prot.asc_getTransparent;
      prot["put_transparent"] = prot["asc_putTransparent"] = prot.asc_putTransparent;
      prot["asc_CheckForseSet"] = prot["asc_CheckForseSet"] = prot.asc_CheckForseSet;

      window["Asc"]["asc_CFillBlip"] = window["Asc"].asc_CFillBlip = asc_CFillBlip;
      prot = asc_CFillBlip.prototype;
      prot["get_type"] = prot["asc_getType"] = prot.asc_getType;
      prot["put_type"] = prot["asc_putType"] = prot.asc_putType;
      prot["get_url"] = prot["asc_getUrl"] = prot.asc_getUrl;
      prot["put_url"] = prot["asc_putUrl"] = prot.asc_putUrl;
      prot["get_texture_id"] = prot["asc_getTextureId"] = prot.asc_getTextureId;
      prot["put_texture_id"] = prot["asc_putTextureId"] = prot.asc_putTextureId;

      window["Asc"]["asc_CFillHatch"] = window["Asc"].asc_CFillHatch = asc_CFillHatch;
      prot = asc_CFillHatch.prototype;
      prot["get_pattern_type"] = prot["asc_getPatternType"] = prot.asc_getPatternType;
      prot["put_pattern_type"] = prot["asc_putPatternType"] = prot.asc_putPatternType;
      prot["get_color_fg"] = prot["asc_getColorFg"] = prot.asc_getColorFg;
      prot["put_color_fg"] = prot["asc_putColorFg"] = prot.asc_putColorFg;
      prot["get_color_bg"] = prot["asc_getColorBg"] = prot.asc_getColorBg;
      prot["put_color_bg"] = prot["asc_putColorBg"] = prot.asc_putColorBg;

      window["Asc"]["asc_CFillGrad"] = window["Asc"].asc_CFillGrad = asc_CFillGrad;
      prot = asc_CFillGrad.prototype;
      prot["get_colors"] = prot["asc_getColors"] = prot.asc_getColors;
      prot["put_colors"] = prot["asc_putColors"] = prot.asc_putColors;
      prot["get_positions"] = prot["asc_getPositions"] = prot.asc_getPositions;
      prot["put_positions"] = prot["asc_putPositions"] = prot.asc_putPositions;
      prot["get_grad_type"] = prot["asc_getGradType"] = prot.asc_getGradType;
      prot["put_grad_type"] = prot["asc_putGradType"] = prot.asc_putGradType;
      prot["get_linear_angle"] = prot["asc_getLinearAngle"] = prot.asc_getLinearAngle;
      prot["put_linear_angle"] = prot["asc_putLinearAngle"] = prot.asc_putLinearAngle;
      prot["get_linear_scale"] = prot["asc_getLinearScale"] = prot.asc_getLinearScale;
      prot["put_linear_scale"] = prot["asc_putLinearScale"] = prot.asc_putLinearScale;
      prot["get_path_type"] = prot["asc_getPathType"] = prot.asc_getPathType;
      prot["put_path_type"] = prot["asc_putPathType"] = prot.asc_putPathType;

      window["Asc"]["asc_CFillSolid"] = window["Asc"].asc_CFillSolid = asc_CFillSolid;
      prot = asc_CFillSolid.prototype;
      prot["get_color"] = prot["asc_getColor"] = prot.asc_getColor;
      prot["put_color"] = prot["asc_putColor"] = prot.asc_putColor;

      window["Asc"]["asc_CStroke"] = window["Asc"].asc_CStroke = asc_CStroke;
      prot = asc_CStroke.prototype;
      prot["get_type"] = prot["asc_getType"] = prot.asc_getType;
      prot["put_type"] = prot["asc_putType"] = prot.asc_putType;
      prot["get_width"] = prot["asc_getWidth"] = prot.asc_getWidth;
      prot["put_width"] = prot["asc_putWidth"] = prot.asc_putWidth;
      prot["get_color"] = prot["asc_getColor"] = prot.asc_getColor;
      prot["put_color"] = prot["asc_putColor"] = prot.asc_putColor;
      prot["get_linejoin"] = prot["asc_getLinejoin"] = prot.asc_getLinejoin;
      prot["put_linejoin"] =prot["asc_putLinejoin"] = prot.asc_putLinejoin;
      prot["get_linecap"] = prot["asc_getLinecap"] = prot.asc_getLinecap;
      prot["put_linecap"] = prot["asc_putLinecap"] = prot.asc_putLinecap;
      prot["get_linebeginstyle"] = prot["asc_getLinebeginstyle"] = prot.asc_getLinebeginstyle;
      prot["put_linebeginstyle"] = prot["asc_putLinebeginstyle"] = prot.asc_putLinebeginstyle;
      prot["get_linebeginsize"] = prot["asc_getLinebeginsize"] = prot.asc_getLinebeginsize;
      prot["put_linebeginsize"] = prot["asc_putLinebeginsize"] = prot.asc_putLinebeginsize;
      prot["get_lineendstyle"] = prot["asc_getLineendstyle"] = prot.asc_getLineendstyle;
      prot["put_lineendstyle"] = prot["asc_putLineendstyle"] = prot.asc_putLineendstyle;
      prot["get_lineendsize"] = prot["asc_getLineendsize"] = prot.asc_getLineendsize;
      prot["put_lineendsize"] = prot["asc_putLineendsize"] = prot.asc_putLineendsize;
      prot["get_canChangeArrows"] = prot["asc_getCanChangeArrows"] = prot.asc_getCanChangeArrows;

      window["AscCommon"].CAscColorScheme = CAscColorScheme;
      prot = CAscColorScheme.prototype;
      prot["get_colors"] =  prot.get_colors;
      prot["get_name"] = prot.get_name;

      window["AscCommon"].CMouseMoveData = CMouseMoveData;
      prot = CMouseMoveData.prototype;
      prot["get_Type"] =  prot.get_Type;
      prot["get_X"] =  prot.get_X;
      prot["get_Y"] = prot.get_Y;
      prot["get_Hyperlink"] =  prot.get_Hyperlink;
      prot["get_UserId"] =  prot.get_UserId;
      prot["get_HaveChanges"] = prot.get_HaveChanges;
      prot["get_LockedObjectType"] = prot.get_LockedObjectType;

      window["Asc"]["asc_CUserInfo"] = window["Asc"].asc_CUserInfo = asc_CUserInfo;
      prot = asc_CUserInfo.prototype;
      prot["asc_putId"] =        prot["put_Id"]         = prot.asc_putId;
      prot["asc_getId"] =        prot["get_Id"]         = prot.asc_getId;
      prot["asc_putFullName"] =  prot["put_FullName"]   = prot.asc_putFullName;
      prot["asc_getFullName"] =  prot["get_FullName"]   = prot.asc_getFullName;
      prot["asc_putFirstName"] = prot["put_FirstName"]  = prot.asc_putFirstName;
      prot["asc_getFirstName"] = prot["get_FirstName"]  = prot.asc_getFirstName;
      prot["asc_putLastName"] =  prot["put_LastName"]   = prot.asc_putLastName;
      prot["asc_getLastName"] =  prot["get_LastName"]   = prot.asc_getLastName;

      window["Asc"]["asc_CDocInfo"] = window["Asc"].asc_CDocInfo = asc_CDocInfo;
      prot = asc_CDocInfo.prototype;
      prot["get_Id"]                  = prot["asc_getId"]                  =   prot.asc_getId;
      prot["put_Id"]                  = prot["asc_putId"]                  =   prot.asc_putId;
      prot["get_Url"]                 = prot["asc_getUrl"]                 =   prot.asc_getUrl;
      prot["put_Url"]                 = prot["asc_putUrl"]                 =   prot.asc_putUrl;
      prot["get_Title"]               = prot["asc_getTitle"]               =   prot.asc_getTitle;
      prot["put_Title"]               = prot["asc_putTitle"]               =   prot.asc_putTitle;
      prot["get_Format"]              = prot["asc_getFormat"]              =   prot.asc_getFormat;
      prot["put_Format"]              = prot["asc_putFormat"]              =   prot.asc_putFormat;
      prot["get_VKey"]                = prot["asc_getVKey"]                =   prot.asc_getVKey;
      prot["put_VKey"]                = prot["asc_putVKey"]                =   prot.asc_putVKey;
      prot["get_OfflineApp"]          = prot["asc_getOfflineApp"]          =   prot.asc_getOfflineApp;
      prot["put_OfflineApp"]          = prot["asc_putOfflineApp"]          =   prot.asc_putOfflineApp;
      prot["get_UserId"]              = prot["asc_getUserId"]              =   prot.asc_getUserId;
      prot["get_UserName"]            = prot["asc_getUserName"]            =   prot.asc_getUserName;
      prot["get_Options"]             = prot["asc_getOptions"]             =   prot.asc_getOptions;
      prot["put_Options"]             = prot["asc_putOptions"]             =   prot.asc_putOptions;
      prot["get_CallbackUrl"]         = prot["asc_getCallbackUrl"]         =   prot.asc_getCallbackUrl;
      prot["put_CallbackUrl"]         = prot["asc_putCallbackUrl"]         =   prot.asc_putCallbackUrl;
      prot["get_TemplateReplacement"] = prot["asc_getTemplateReplacement"] =   prot.asc_getTemplateReplacement;
      prot["put_TemplateReplacement"] = prot["asc_putTemplateReplacement"] =   prot.asc_putTemplateReplacement;
      prot["get_UserInfo"]            = prot["asc_getUserInfo"]            =   prot.asc_getUserInfo;
      prot["put_UserInfo"]            = prot["asc_putUserInfo"]            =   prot.asc_putUserInfo;

      window["AscCommon"].COpenProgress = COpenProgress;
      prot = COpenProgress.prototype;
      prot["asc_getType"] =  prot.asc_getType;
      prot["asc_getFontsCount"] =  prot.asc_getFontsCount;
      prot["asc_getCurrentFont"] = prot.asc_getCurrentFont;
      prot["asc_getImagesCount"] =  prot.asc_getImagesCount;
      prot["asc_getCurrentImage"] =  prot.asc_getCurrentImage;

      window["AscCommon"].CErrorData = CErrorData;
      prot = CErrorData.prototype;
      prot["put_Value"] = prot.put_Value;
      prot["get_Value"] = prot.get_Value;

      window["AscCommon"].CAscMathType = CAscMathType;
      prot = CAscMathType.prototype;
      prot["get_Id"] = prot.get_Id;
      prot["get_X"] = prot.get_X;
      prot["get_Y"] = prot.get_Y;

      window["AscCommon"].CAscMathCategory = CAscMathCategory;
      prot = CAscMathCategory.prototype;
      prot["get_Id"] = prot.get_Id;
      prot["get_Data"] = prot.get_Data;
      prot["get_W"] = prot.get_W;
      prot["get_H"] = prot.get_H;

      window["AscCommon"].CStyleImage = CStyleImage;
      prot = CStyleImage.prototype;
      prot["asc_getName"] = prot["get_Name"] = prot.asc_getName;
      prot["asc_getType"] = prot["get_Type"] = prot.asc_getType;
      prot["asc_getImage"] = prot.asc_getImage;
})(window);

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
(function(window, undefined){

//зависимости
//stream
//memory
//c_oAscChartType
//todo
//BinaryCommonWriter

var c_oSerConstants = {
    ErrorFormat: -2,
    ErrorUnknown: -1,
    ReadOk:0,
    ReadUnknown:1,
    ErrorStream:0x55
};
var c_oSerPropLenType = {
    Null:0,
    Byte:1,
    Short:2,
    Three:3,
    Long:4,
    Double:5,
    Variable:6
};
var c_oSer_ColorObjectType =
{
    Rgb: 0,
    Type: 1,
    Theme: 2,
    Tint: 3
};
var c_oSer_ColorType =
{
    Auto: 0
};
var c_oSerBorderType = {
    Color: 0,
    Space: 1,
    Size: 2,
    Value: 3,
	ColorTheme: 4
};
var c_oSerBordersType = {
    left: 0,
    top: 1,
    right: 2,
    bottom: 3,
    insideV: 4,
    insideH: 5,
    start: 6,
    end: 7,
    tl2br: 8,
    tr2bl: 9,
    bar: 10,
    between: 11
};
var c_oSerPaddingType = {
    left: 0,
    top: 1,
    right: 2,
    bottom: 3
};
var c_oSerShdType = {
    Value: 0,
    Color: 1,
	ColorTheme: 2
};
  var c_oSer_ColorThemeType = {
    Auto: 0,
    Color: 1,
    Tint: 2,
    Shade: 3
  };

function BinaryCommonWriter(memory)
{
    this.memory = memory;
}
BinaryCommonWriter.prototype.WriteItem = function(type, fWrite)
{
    //type
    this.memory.WriteByte(type);
    this.WriteItemWithLength(fWrite);
};
BinaryCommonWriter.prototype.WriteItemStart = function(type)
{
	this.memory.WriteByte(type);
    return this.WriteItemWithLengthStart(fWrite);
};
BinaryCommonWriter.prototype.WriteItemEnd = function(nStart)
{
	this.WriteItemWithLengthEnd(nStart);
};
BinaryCommonWriter.prototype.WriteItemWithLength = function(fWrite)
{
    var nStart = this.WriteItemWithLengthStart();
    fWrite();
    this.WriteItemWithLengthEnd(nStart);
};
BinaryCommonWriter.prototype.WriteItemWithLengthStart = function()
{
    //Запоминаем позицию чтобы в конце записать туда длину
    var nStart = this.memory.GetCurPosition();
    this.memory.Skip(4);
    return nStart;
};
BinaryCommonWriter.prototype.WriteItemWithLengthEnd = function(nStart)
{
    //Length
    var nEnd = this.memory.GetCurPosition();
    this.memory.Seek(nStart);
    this.memory.WriteLong(nEnd - nStart - 4);
    this.memory.Seek(nEnd);
};
BinaryCommonWriter.prototype.WriteBorder = function(border)
{
	var _this = this;
    if(null != border.Value)
    {
        var color = null;
        if (null != border.Color)
            color = border.Color;
        else if (null != border.Unifill) {
            var doc = editor.WordControl.m_oLogicDocument;
            border.Unifill.check(doc.Get_Theme(), doc.Get_ColorMap());
            var RGBA = border.Unifill.getRGBAColor();
            color = new AscCommonWord.CDocumentColor(RGBA.R, RGBA.G, RGBA.B);
        }
        if (null != color && !color.Auto)
            this.WriteColor(c_oSerBorderType.Color, color);
        if (null != border.Space) {
            this.memory.WriteByte(c_oSerBorderType.Space);
            this.memory.WriteByte(c_oSerPropLenType.Double);
            this.memory.WriteDouble(border.Space);
        }
        if (null != border.Size) {
            this.memory.WriteByte(c_oSerBorderType.Size);
            this.memory.WriteByte(c_oSerPropLenType.Double);
            this.memory.WriteDouble(border.Size);
        }
        if (null != border.Unifill || (null != border.Color && border.Color.Auto)) {
            this.memory.WriteByte(c_oSerBorderType.ColorTheme);
            this.memory.WriteByte(c_oSerPropLenType.Variable);
            this.WriteItemWithLength(function () { _this.WriteColorTheme(border.Unifill, border.Color); });
        }

        this.memory.WriteByte(c_oSerBorderType.Value);
        this.memory.WriteByte(c_oSerPropLenType.Byte);
        this.memory.WriteByte(border.Value);
    }
};
BinaryCommonWriter.prototype.WriteBorders = function(Borders)
{
    var oThis = this;
    //Left
    if(null != Borders.Left)
        this.WriteItem(c_oSerBordersType.left, function(){oThis.WriteBorder(Borders.Left);});
    //Top
    if(null != Borders.Top)
        this.WriteItem(c_oSerBordersType.top, function(){oThis.WriteBorder(Borders.Top);});
    //Right
    if(null != Borders.Right)
        this.WriteItem(c_oSerBordersType.right, function(){oThis.WriteBorder(Borders.Right);});
    //Bottom
    if(null != Borders.Bottom)
        this.WriteItem(c_oSerBordersType.bottom, function(){oThis.WriteBorder(Borders.Bottom);});
    //InsideV
    if(null != Borders.InsideV)
        this.WriteItem(c_oSerBordersType.insideV, function(){oThis.WriteBorder(Borders.InsideV);});
    //InsideH
    if(null != Borders.InsideH)
        this.WriteItem(c_oSerBordersType.insideH, function(){oThis.WriteBorder(Borders.InsideH);});
    //Between
    if(null != Borders.Between)
        this.WriteItem(c_oSerBordersType.between, function(){oThis.WriteBorder(Borders.Between);});
};
BinaryCommonWriter.prototype.WriteColor = function(type, color)
{
    this.memory.WriteByte(type);
    this.memory.WriteByte(c_oSerPropLenType.Three);
    this.memory.WriteByte(color.r);
    this.memory.WriteByte(color.g);
    this.memory.WriteByte(color.b);
};
BinaryCommonWriter.prototype.WriteShd = function(Shd)
{
	var _this = this;
    //Value
    if(null != Shd.Value)
    {
        this.memory.WriteByte(c_oSerShdType.Value);
        this.memory.WriteByte(c_oSerPropLenType.Byte);
        this.memory.WriteByte(Shd.Value);
    }
    //Value
    var color = null;
    if (null != Shd.Color)
        color = Shd.Color;
    else if (null != Shd.Unifill) {
        var doc = editor.WordControl.m_oLogicDocument;
        Shd.Unifill.check(doc.Get_Theme(), doc.Get_ColorMap());
        var RGBA = Shd.Unifill.getRGBAColor();
        color = new AscCommonWord.CDocumentColor(RGBA.R, RGBA.G, RGBA.B);
    }
    if (null != color && !color.Auto)
        this.WriteColor(c_oSerShdType.Color, color);
	if(null != Shd.Unifill || (null != Shd.Color && Shd.Color.Auto))
    {
		this.memory.WriteByte(c_oSerShdType.ColorTheme);
		this.memory.WriteByte(c_oSerPropLenType.Variable);
		this.WriteItemWithLength(function(){_this.WriteColorTheme(Shd.Unifill, Shd.Color);});
    }
};
BinaryCommonWriter.prototype.WritePaddings = function(Paddings)
{
    //left
    if(null != Paddings.L)
    {
        this.memory.WriteByte(c_oSerPaddingType.left);
        this.memory.WriteByte(c_oSerPropLenType.Double);
        this.memory.WriteDouble(Paddings.L);
    }
    //top
    if(null != Paddings.T)
    {
        this.memory.WriteByte(c_oSerPaddingType.top);
        this.memory.WriteByte(c_oSerPropLenType.Double);
        this.memory.WriteDouble(Paddings.T);
    }
    //Right
    if(null != Paddings.R)
    {
        this.memory.WriteByte(c_oSerPaddingType.right);
        this.memory.WriteByte(c_oSerPropLenType.Double);
        this.memory.WriteDouble(Paddings.R);
    }
    //bottom
    if(null != Paddings.B)
    {
        this.memory.WriteByte(c_oSerPaddingType.bottom);
        this.memory.WriteByte(c_oSerPropLenType.Double);
        this.memory.WriteDouble(Paddings.B);
    }
};
BinaryCommonWriter.prototype.WriteColorSpreadsheet = function(color)
{
	if(color instanceof AscCommonExcel.ThemeColor)
	{
		if(null != color.theme)
		{
			this.memory.WriteByte(c_oSer_ColorObjectType.Theme);
			this.memory.WriteByte(c_oSerPropLenType.Byte);
			this.memory.WriteByte(color.theme);
		}
		if(null != color.tint)
		{
			this.memory.WriteByte(c_oSer_ColorObjectType.Tint);
			this.memory.WriteByte(c_oSerPropLenType.Double);
			this.memory.WriteDouble2(color.tint);
		}
	}
	else
	{
		this.memory.WriteByte(c_oSer_ColorObjectType.Rgb);
		this.memory.WriteByte(c_oSerPropLenType.Long);
		this.memory.WriteLong(color.getRgb());
	}
};
BinaryCommonWriter.prototype.WriteColorTheme = function(unifill, color)
{
	if(null != color && color.Auto){
		this.memory.WriteByte(c_oSer_ColorThemeType.Auto);
		this.memory.WriteByte(c_oSerPropLenType.Null);
	}
	if (null != unifill && null != unifill.fill && null != unifill.fill.color && unifill.fill.color.color instanceof AscFormat.CSchemeColor) {
		var uniColor = unifill.fill.color;
		if(null != uniColor.color){
      var EThemeColor = AscCommonWord.EThemeColor;
			var nFormatId = EThemeColor.themecolorNone;
			switch(uniColor.color.id){
				case 0: nFormatId = EThemeColor.themecolorAccent1;break;
				case 1: nFormatId = EThemeColor.themecolorAccent2;break;
				case 2: nFormatId = EThemeColor.themecolorAccent3;break;
				case 3: nFormatId = EThemeColor.themecolorAccent4;break;
				case 4: nFormatId = EThemeColor.themecolorAccent5;break;
				case 5: nFormatId = EThemeColor.themecolorAccent6;break;
				case 6: nFormatId = EThemeColor.themecolorBackground1;break;
				case 7: nFormatId = EThemeColor.themecolorBackground2;break;
				case 8: nFormatId = EThemeColor.themecolorDark1;break;
				case 9: nFormatId = EThemeColor.themecolorDark2;break;
				case 10: nFormatId = EThemeColor.themecolorFollowedHyperlink;break;
				case 11: nFormatId = EThemeColor.themecolorHyperlink;break;
				case 12: nFormatId = EThemeColor.themecolorLight1;break;
				case 13: nFormatId = EThemeColor.themecolorLight2;break;
				case 14: nFormatId = EThemeColor.themecolorNone;break;
				case 15: nFormatId = EThemeColor.themecolorText1;break;
				case 16: nFormatId = EThemeColor.themecolorText2;break;
			}
			this.memory.WriteByte(c_oSer_ColorThemeType.Color);
			this.memory.WriteByte(c_oSerPropLenType.Byte);
			this.memory.WriteByte(nFormatId);
		}
		if(null != uniColor.Mods){
			for(var i = 0, length = uniColor.Mods.Mods.length; i < length; ++i){
				var mod = uniColor.Mods.Mods[i];
				if("wordTint" == mod.name){
					this.memory.WriteByte(c_oSer_ColorThemeType.Tint);
					this.memory.WriteByte(c_oSerPropLenType.Byte);
					this.memory.WriteByte(Math.round(mod.val));
				}
				else if("wordShade" == mod.name){
					this.memory.WriteByte(c_oSer_ColorThemeType.Shade);
					this.memory.WriteByte(c_oSerPropLenType.Byte);
					this.memory.WriteByte(Math.round(mod.val));
				}
			}
		}
	}
};
function Binary_CommonReader(stream)
{
    this.stream = stream;
}

Binary_CommonReader.prototype.ReadTable = function(fReadContent)
{
    var res = c_oSerConstants.ReadOk;
    //stLen
    res = this.stream.EnterFrame(4);
    if(c_oSerConstants.ReadOk != res)
        return res;
    var stLen = this.stream.GetULongLE();
    //Смотрим есть ли данные под всю таблицу в дальнейшем спокойно пользуемся get функциями
    res = this.stream.EnterFrame(stLen);
    if(c_oSerConstants.ReadOk != res)
        return res;
    return this.Read1(stLen, fReadContent);
};
Binary_CommonReader.prototype.Read1 = function(stLen, fRead)
{
    var res = c_oSerConstants.ReadOk;
    var stCurPos = 0;
    while(stCurPos < stLen)
    {
		this.stream.bLast = false;
        //stItem
        var type = this.stream.GetUChar();
        var length = this.stream.GetULongLE();
		if (stCurPos + length + 5 >= stLen)
			this.stream.bLast = true;
        res = fRead(type, length);
        if(res === c_oSerConstants.ReadUnknown)
        {
            res = this.stream.Skip2(length);
            if(c_oSerConstants.ReadOk != res)
                return res;
        }
        else if(res !== c_oSerConstants.ReadOk)
            return res;
        stCurPos += length + 5;
    }
    return res;
};
Binary_CommonReader.prototype.Read2 = function(stLen, fRead)
{
    var res = c_oSerConstants.ReadOk;
    var stCurPos = 0;
    while(stCurPos < stLen)
    {
        //stItem
        var type = this.stream.GetUChar();
        var lenType = this.stream.GetUChar();
        var nCurPosShift = 2;
        var nRealLen;
        switch(lenType)
        {
            case c_oSerPropLenType.Null: nRealLen = 0;break;
            case c_oSerPropLenType.Byte: nRealLen = 1;break;
            case c_oSerPropLenType.Short: nRealLen = 2;break;
            case c_oSerPropLenType.Three: nRealLen = 3;break;
            case c_oSerPropLenType.Long:
            case c_oSerPropLenType.Double: nRealLen = 4;break;
            case c_oSerPropLenType.Variable:
                nRealLen = this.stream.GetULongLE();
                nCurPosShift += 4;
                break;
            default:return c_oSerConstants.ErrorUnknown;
        }
        res = fRead(type, nRealLen);
        if(res === c_oSerConstants.ReadUnknown)
        {
            res = this.stream.Skip2(nRealLen);
            if(c_oSerConstants.ReadOk != res)
                return res;
        }
        else if(res !== c_oSerConstants.ReadOk)
            return res;
        stCurPos += nRealLen + nCurPosShift;
    }
    return res;
};
Binary_CommonReader.prototype.Read2Spreadsheet = function(stLen, fRead)
{
    var res = c_oSerConstants.ReadOk;
    var stCurPos = 0;
    while(stCurPos < stLen)
    {
        //stItem
        var type = this.stream.GetUChar();
        var lenType = this.stream.GetUChar();
        var nCurPosShift = 2;
        var nRealLen;
        switch(lenType)
        {
            case c_oSerPropLenType.Null: nRealLen = 0;break;
            case c_oSerPropLenType.Byte: nRealLen = 1;break;
            case c_oSerPropLenType.Short: nRealLen = 2;break;
            case c_oSerPropLenType.Three: nRealLen = 3;break;
            case c_oSerPropLenType.Long: nRealLen = 4;break;
            case c_oSerPropLenType.Double: nRealLen = 8;break;
            case c_oSerPropLenType.Variable:
                nRealLen = this.stream.GetULongLE();
                nCurPosShift += 4;
                break;
            default:return c_oSerConstants.ErrorUnknown;
        }
        res = fRead(type, nRealLen);
        if(res === c_oSerConstants.ReadUnknown)
        {
            res = this.stream.Skip2(nRealLen);
            if(c_oSerConstants.ReadOk != res)
                return res;
        }
        else if(res !== c_oSerConstants.ReadOk)
            return res;
        stCurPos += nRealLen + nCurPosShift;
    }
    return res;
};
Binary_CommonReader.prototype.ReadDouble = function()
{
    var dRes = 0.0;
    dRes |= this.stream.GetUChar();
    dRes |= this.stream.GetUChar() << 8;
    dRes |= this.stream.GetUChar() << 16;
    dRes |= this.stream.GetUChar() << 24;
    dRes /= 100000;
    return dRes;
};
Binary_CommonReader.prototype.ReadColor = function()
{
    var r = this.stream.GetUChar();
    var g = this.stream.GetUChar();
    var b = this.stream.GetUChar();
    return new AscCommonWord.CDocumentColor(r, g, b);
};
Binary_CommonReader.prototype.ReadShd = function(type, length, Shd, themeColor)
{
    var res = c_oSerConstants.ReadOk;
	var oThis = this;
    switch(type)
    {
        case c_oSerShdType.Value: Shd.Value = this.stream.GetUChar();break;
        case c_oSerShdType.Color: Shd.Color = this.ReadColor();break;
		case c_oSerShdType.ColorTheme:
			res = this.Read2(length, function(t, l){
				return oThis.ReadColorTheme(t, l, themeColor);
			});
			break;
        default:
            res = c_oSerConstants.ReadUnknown;
            break;
    }
    return res;
};
Binary_CommonReader.prototype.ReadColorSpreadsheet = function(type, length, color)
{
    var res = c_oSerConstants.ReadOk;
    if ( c_oSer_ColorObjectType.Type == type )
        color.auto = (c_oSer_ColorType.Auto == this.stream.GetUChar());
    else if ( c_oSer_ColorObjectType.Rgb == type )
        color.rgb = 0xffffff & this.stream.GetULongLE();
	else if ( c_oSer_ColorObjectType.Theme == type )
        color.theme = this.stream.GetUChar();
	else if ( c_oSer_ColorObjectType.Tint == type )
        color.tint = this.stream.GetDoubleLE();
    else
        res = c_oSerConstants.ReadUnknown;
    return res;
};
Binary_CommonReader.prototype.ReadColorTheme = function(type, length, color)
{
    var res = c_oSerConstants.ReadOk;
    if ( c_oSer_ColorThemeType.Auto == type )
        color.Auto = true;
	else if ( c_oSer_ColorThemeType.Color == type )
        color.Color = this.stream.GetByte();
	else if ( c_oSer_ColorThemeType.Tint == type )
        color.Tint = this.stream.GetByte();
	else if ( c_oSer_ColorThemeType.Shade == type )
        color.Shade = this.stream.GetByte();
    else
        res = c_oSerConstants.ReadUnknown;
    return res;
};
/** @constructor */
function FT_Stream2(data, size) {
    this.obj = null;
    this.data = data;
    this.size = size;
    this.pos = 0;
    this.cur = 0;
	this.bLast = false;
}

FT_Stream2.prototype.Seek = function(_pos) {
	if (_pos > this.size)
		return c_oSerConstants.ErrorStream;
	this.pos = _pos;
	return c_oSerConstants.ReadOk;
};
FT_Stream2.prototype.Seek2 = function(_cur) {
	if (_cur > this.size)
		return c_oSerConstants.ErrorStream;
	this.cur = _cur;
	return c_oSerConstants.ReadOk;
};
FT_Stream2.prototype.Skip = function(_skip) {
	if (_skip < 0)
		return c_oSerConstants.ErrorStream;
	return this.Seek(this.pos + _skip);
};
FT_Stream2.prototype.Skip2 = function(_skip) {
	if (_skip < 0)
		return c_oSerConstants.ErrorStream;
	return this.Seek2(this.cur + _skip);
};

// 1 bytes
FT_Stream2.prototype.GetUChar = function() {
	if (this.cur >= this.size)
		return 0;
	return this.data[this.cur++];
};
FT_Stream2.prototype.GetChar = function() {
	if (this.cur >= this.size)
        return 0;
    var m = this.data[this.cur++];
    if (m > 127)
        m -= 256;
    return m;
};
FT_Stream2.prototype.GetByte = function() {
	return this.GetUChar();
};
FT_Stream2.prototype.GetBool = function() {
	var Value = this.GetUChar();
	return ( Value == 0 ? false : true );
};
// 2 byte
FT_Stream2.prototype.GetUShortLE = function() {
	if (this.cur + 1 >= this.size)
		return 0;
	return (this.data[this.cur++] | this.data[this.cur++] << 8);
};
// 4 byte
FT_Stream2.prototype.GetULongLE = function() {
	if (this.cur + 3 >= this.size)
		return 0;
	return (this.data[this.cur++] | this.data[this.cur++] << 8 | this.data[this.cur++] << 16 | this.data[this.cur++] << 24);
};
FT_Stream2.prototype.GetLongLE = function() {
	return this.GetULongLE();
};
FT_Stream2.prototype.GetLong = function() {
	return this.GetULongLE();
};
FT_Stream2.prototype.GetDoubleLE = function() {
	if (this.cur + 7 >= this.size)
		return 0;
	var arr = [];
	for(var i = 0; i < 8; ++i)
		arr.push(this.GetUChar());
	return this.doubleDecodeLE754(arr);
};
FT_Stream2.prototype.doubleDecodeLE754 = function(a) {
	var s, e, m, i, d, nBits, mLen, eLen, eBias, eMax;
	var el = {len:8, mLen:52, rt:0};
	mLen = el.mLen, eLen = el.len*8-el.mLen-1, eMax = (1<<eLen)-1, eBias = eMax>>1;

	i = (el.len-1); d = -1; s = a[i]; i+=d; nBits = -7;
	for (e = s&((1<<(-nBits))-1), s>>=(-nBits), nBits += eLen; nBits > 0; e=e*256+a[i], i+=d, nBits-=8);
	for (m = e&((1<<(-nBits))-1), e>>=(-nBits), nBits += mLen; nBits > 0; m=m*256+a[i], i+=d, nBits-=8);

	switch (e)
	{
		case 0:
			// Zero, or denormalized number
			e = 1-eBias;
			break;
		case eMax:
			// NaN, or +/-Infinity
			return m?NaN:((s?-1:1)*Infinity);
		default:
			// Normalized number
			m = m + Math.pow(2, mLen);
			e = e - eBias;
			break;
	}
	return (s?-1:1) * m * Math.pow(2, e-mLen);
};
// 3 byte
FT_Stream2.prototype.GetUOffsetLE = function() {
	if (this.cur + 2 >= this.size)
		return c_oSerConstants.ReadOk;
	return (this.data[this.cur++] | this.data[this.cur++] << 8 | this.data[this.cur++] << 16);
};
FT_Stream2.prototype.GetString2 = function() {
	var Len = this.GetLong();
	return this.GetString2LE(Len);
};
//String
FT_Stream2.prototype.GetString2LE = function(len) {
	if (this.cur + len > this.size)
		return "";
	var a = [];
	for (var i = 0; i + 1 < len; i+=2)
		a.push(String.fromCharCode(this.data[this.cur + i] | this.data[this.cur + i + 1] << 8));
	this.cur += len;
	return a.join("");
};
FT_Stream2.prototype.GetString = function() {
	var Len = this.GetLong();
	if (this.cur + 2 * Len > this.size)
		return "";
	var t = "";
	for (var i = 0; i + 1 < 2 * Len; i+=2) {
		var uni = this.data[this.cur + i];
		uni |= this.data[this.cur + i + 1] << 8;
		t += String.fromCharCode(uni);
	}
	this.cur += 2 * Len;
	return t;
};
FT_Stream2.prototype.GetCurPos = function() {
	return this.cur;
};
FT_Stream2.prototype.GetSize = function() {
	return this.size;
};
FT_Stream2.prototype.EnterFrame = function(count) {
	if (this.size - this.pos < count)
		return c_oSerConstants.ErrorStream;

	this.cur = this.pos;
	this.pos += count;
	return c_oSerConstants.ReadOk;
};
FT_Stream2.prototype.GetDouble = function() {
	var dRes = 0.0;
	dRes |= this.GetUChar();
	dRes |= this.GetUChar() << 8;
	dRes |= this.GetUChar() << 16;
	dRes |= this.GetUChar() << 24;
	dRes /= 100000;
	return dRes;
};
var gc_nMaxRow = 1048576;
var gc_nMaxCol = 16384;
var gc_nMaxRow0 = gc_nMaxRow - 1;
var gc_nMaxCol0 = gc_nMaxCol - 1;
/**
 * @constructor
 */
function CellAddressUtils(){
	this._oCodeA = 'A'.charCodeAt(0);
	this._aColnumToColstr = [];
	this.oCellAddressCache = {};
	this.colnumToColstrFromWsView = function (col) {
		var sResult = this._aColnumToColstr[col];
		if (null != sResult)
			return sResult;

		if(col == 0) return "";

		var col0 = col - 1;
		var text = String.fromCharCode(65 + (col0 % 26));
		return (this._aColnumToColstr[col] = (col0 < 26 ? text : this.colnumToColstrFromWsView(Math.floor(col0 / 26)) + text));
	};
	this.colnumToColstr = function(num){
		var sResult = this._aColnumToColstr[num];
		if(!sResult){
			// convert 1 to A, 2 to B, ..., 27 to AA etc.
			sResult = "";
			if(num > 0){
				var columnNumber = num;
				var currentLetterNumber;
				while(columnNumber > 0){
					currentLetterNumber = (columnNumber - 1) % 26;
					sResult = String.fromCharCode(currentLetterNumber + 65) + sResult;
					columnNumber = (columnNumber - (currentLetterNumber + 1)) / 26;
				}
			}
			this._aColnumToColstr[num] = sResult;
		}
		return sResult;
	};
	this.colstrToColnum = function(col_str) {
		//convert A to 1; AA to 27
		var col_num = 0;
		for (var i = 0; i < col_str.length; ++i)
			col_num = 26 * col_num + (col_str.charCodeAt(i) - this._oCodeA + 1);
		return col_num;
	};
	this.getCellId = function(row, col){
		return g_oCellAddressUtils.colnumToColstr(col + 1) + (row + 1);
	};
	this.getCellAddress = function(sId)
	{
		var oRes = this.oCellAddressCache[sId];
		if(null == oRes)
		{
			oRes = new CellAddress(sId);
			this.oCellAddressCache[sId] = oRes;
		}
		return oRes;
	};
}
var g_oCellAddressUtils = new CellAddressUtils();
/**
 * @constructor
 */
function CellAddress(){
	var argc = arguments.length;
	this._valid = true;
	this._invalidId = false;
	this._invalidCoord = false;
	this.id = null;
	this.row = null;
	this.col = null;
	this.bRowAbs = false;
	this.bColAbs = false;
	this.bIsCol = false;
	this.bIsRow = false;
	this.colLetter = null;
	if(1 == argc){
		//Сразу пришло ID вида "A1"
		this.id = arguments[0].toUpperCase();
		this._invalidCoord = true;
		this._checkId();
	}
	else if(2 == argc){
		//адрес вида (1,1) = "A1". Внутренний формат начинается с 1
		this.row = arguments[0];
		this.col = arguments[1];
		this._checkCoord();
		this._invalidId = true;
	}
	else if(3 == argc){
		//тоже самое что и 2 аргумента, только 0-based
		this.row = arguments[0] + 1;
		this.col = arguments[1] + 1;
		this._checkCoord();
		this._invalidId = true;
	}
}
CellAddress.prototype._isDigit=function(symbol){
	return '0' <= symbol && symbol <= '9';
};
CellAddress.prototype._isAlpha=function(symbol){
	return 'A' <= symbol && symbol <= 'Z';
};
CellAddress.prototype._checkId=function(){
	this._invalidCoord = true;
	this._recalculate(true, false);
	this._checkCoord();
};
CellAddress.prototype._checkCoord=function(){
	if( !(this.row >= 1 && this.row <= gc_nMaxRow) )
		this._valid = false;
	else if( !(this.col >= 1 && this.col <= gc_nMaxCol) )
		this._valid = false;
	else
		this._valid = true;
};
CellAddress.prototype._recalculate=function(bCoord, bId){
	if(bCoord && this._invalidCoord){
		this._invalidCoord = false;
		var sId = this.id;
		this.row = this.col = 0;//выставляем невалидные значения, чтобы не присваивать их при каждом else
		var indexes = {}, i = -1, indexesCount = 0;
		while ((i = sId.indexOf("$", i + 1)) != -1) {
		    indexes[i - indexesCount++] = 1;//отнимаем количество, чтобы индексы указывали на следующий после них символ после удаления $
		}
		if (indexesCount <= 2) {
		    if (indexesCount > 0)
		        sId = sId.replace(/\$/g, "");
		    var nIdLength = sId.length;
		    if (nIdLength > 0) {
		        var nIndex = 0;
		        while (this._isAlpha(sId.charAt(nIndex)) && nIndex < nIdLength)
		            nIndex++;
		        if (0 == nIndex) {
		            //  (1,Infinity)
		            this.bIsRow = true;
		            this.col = 1;
		            this.colLetter = g_oCellAddressUtils.colnumToColstr(this.col);
		            this.row = sId.substring(nIndex) - 0;
		            //this.id = this.colLetter + this.row;
		            if (null != indexes[0]) {
		                this.bRowAbs = true;
		                indexesCount--;
		            }
		        }
		        else if (nIndex == nIdLength) {
		            //  (Infinity,1)
		            this.bIsCol = true;
		            this.colLetter = sId;
		            this.col = g_oCellAddressUtils.colstrToColnum(this.colLetter);
		            this.row = 1;
		            //this.id = this.colLetter + this.row;
		            if (null != indexes[0]) {
		                this.bColAbs = true;
		                indexesCount--;
		            }
		        }
		        else {
		            this.colLetter = sId.substring(0, nIndex);
		            this.col = g_oCellAddressUtils.colstrToColnum(this.colLetter);
		            this.row = sId.substring(nIndex) - 0;
		            if (null != indexes[0]) {
		                this.bColAbs = true;
		                indexesCount--;
		            }
		            if (null != indexes[nIndex]) {
		                this.bRowAbs = true;
		                indexesCount--;
		            }
		        }
		        if (indexesCount > 0) {
		            this.row = this.col = 0;
		        }
		    }
		}
	}
	else if(bId && this._invalidId){
		this._invalidId = false;
		this.colLetter = g_oCellAddressUtils.colnumToColstr(this.col);
		if(this.bIsCol)
			this.id = this.colLetter;
		else if(this.bIsRow)
			this.id = this.row;
		else
			this.id = this.colLetter + this.row;
	}
};
CellAddress.prototype.isValid=function(){
	return this._valid;
};
CellAddress.prototype.getID=function(){
	this._recalculate(false, true);
	return this.id;
};
CellAddress.prototype.getIDAbsolute=function(){
	this._recalculate(true, false);
	return "$" + this.getColLetter() + "$" + this.getRow();
};
CellAddress.prototype.getRow=function(){
	this._recalculate(true, false);
	return this.row;
};
CellAddress.prototype.getRow0=function(){
	//0 - based
	this._recalculate(true, false);
	return this.row - 1;
};
CellAddress.prototype.getRowAbs=function(){
	this._recalculate(true, false);
	return this.bRowAbs;
};
CellAddress.prototype.getIsRow=function(){
	this._recalculate(true, false);
	return this.bIsRow;
};
CellAddress.prototype.getCol=function(){
	this._recalculate(true, false);
	return this.col;
};
CellAddress.prototype.getCol0=function(){
	//0 - based
	this._recalculate(true, false);
	return this.col - 1;
};
CellAddress.prototype.getColAbs=function(){
	this._recalculate(true, false);
	return this.bColAbs;
};
CellAddress.prototype.getIsCol=function(){
	this._recalculate(true, false);
	return this.bIsCol;
};
CellAddress.prototype.getColLetter=function(){
	this._recalculate(false, true);
	return this.colLetter;
};
CellAddress.prototype.setRow=function(val){
	if( !(this.row >= 0 && this.row <= gc_nMaxRow) )
		this._valid = false;
	this._invalidId = true;
	this.row = val;
};
CellAddress.prototype.setCol=function(val){
	if( !(val >= 0 && val <= gc_nMaxCol) )
		return;
	this._invalidId = true;
	this.col = val;
};
CellAddress.prototype.setId=function(val){
	this._invalidCoord = true;
	this.id = val;
	this._checkId();
};
CellAddress.prototype.moveRow=function(diff){
	var val = this.row + diff;
	if( !(val >= 0 && val <= gc_nMaxRow) )
		return;
	this._invalidId = true;
	this.row = val;
};
CellAddress.prototype.moveCol=function(diff){
	var val = this.col + diff;
	if( !( val >= 0 && val <= gc_nMaxCol) )
		return;
	this._invalidId = true;
	this.col = val;
};

function isRealObject(obj)
{
    return obj !== null && typeof obj === "object";
}

  function FileStream(data, size)
  {
    this.obj = null;
    this.data = data;
    this.size = size;
    this.pos = 0;
    this.cur = 0;

    this.Seek = function(_pos)
    {
      if (_pos > this.size)
        return 1;
      this.pos = _pos;
      return 0;
    }
    this.Seek2 = function(_cur)
    {
      if (_cur > this.size)
        return 1;
      this.cur = _cur;
      return 0;
    }
    this.Skip = function(_skip)
    {
      if (_skip < 0)
        return 1;
      return this.Seek(this.pos + _skip);
    }
    this.Skip2 = function(_skip)
    {
      if (_skip < 0)
        return 1;
      return this.Seek2(this.cur + _skip);
    }

    // 1 bytes
    this.GetUChar = function()
    {
      if (this.cur >= this.size)
        return 0;
      return this.data[this.cur++];
    }
    this.GetBool = function()
    {
      if (this.cur >= this.size)
        return 0;
      return (this.data[this.cur++] == 1) ? true : false;
    }

    // 2 byte
    this.GetUShort = function()
    {
      if (this.cur + 1 >= this.size)
        return 0;
      return (this.data[this.cur++] | this.data[this.cur++] << 8);
    }

    // 4 byte
    this.GetULong = function()
    {
      if (this.cur + 3 >= this.size)
        return 0;
      var r =  (this.data[this.cur++] | this.data[this.cur++] << 8 | this.data[this.cur++] << 16 | this.data[this.cur++] << 24);
      if (r < 0)
        r += (0xFFFFFFFF + 1);
      return r;
    }

    this.GetLong = function()
    {
      if (this.cur + 3 >= this.size)
        return 0;
      return (this.data[this.cur++] | this.data[this.cur++] << 8 | this.data[this.cur++] << 16 | this.data[this.cur++] << 24);
    }

    //String
    this.GetString = function(len)
    {
      len *= 2;
      if (this.cur + len > this.size)
        return "";
      var t = "";
      for (var i = 0; i < len; i+=2)
      {
        var _c = this.data[this.cur + i + 1] << 8 | this.data[this.cur + i];
        if (_c == 0)
          break;

        t += String.fromCharCode(_c);
      }
      this.cur += len;
      return t;
    }
    this.GetString1 = function(len)
    {
      if (this.cur + len > this.size)
        return "";
      var t = "";
      for (var i = 0; i < len; i++)
      {
        var _c = this.data[this.cur + i];
        if (_c == 0)
          break;

        t += String.fromCharCode(_c);
      }
      this.cur += len;
      return t;
    }
    this.GetString2 = function()
    {
      var len = this.GetULong();
      return this.GetString(len);
    }

    this.GetString2A = function()
    {
      var len = this.GetULong();
      return this.GetString1(len);
    }

    this.EnterFrame = function(count)
    {
      if (this.pos >= this.size || this.size - this.pos < count)
        return 1;

      this.cur = this.pos;
      this.pos += count;
      return 0;
    }

    this.SkipRecord = function()
    {
      var _len = this.GetULong();
      this.Skip2(_len);
    }

    this.GetPercentage = function()
    {
      var s = this.GetString2();
      var _len = s.length;
      if (_len == 0)
        return null;

      var _ret = null;
      if ((_len - 1) == s.indexOf("%"))
      {
        s.substring(0, _len - 1);
        _ret = parseFloat(s);
        if (isNaN(_ret))
          _ret = null;
      }
      else
      {
        _ret = parseFloat(s);
        if (isNaN(_ret))
          _ret = null;
        else
          _ret /= 1000;
      }

      return _ret;
    }
  }

  //----------------------------------------------------------export----------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window['AscCommon'].c_oSerConstants = c_oSerConstants;
  window['AscCommon'].c_oSerPropLenType = c_oSerPropLenType;
  window['AscCommon'].c_oSer_ColorType = c_oSer_ColorType;
  window['AscCommon'].c_oSerBorderType = c_oSerBorderType;
  window['AscCommon'].c_oSerBordersType = c_oSerBordersType;
  window['AscCommon'].c_oSerPaddingType = c_oSerPaddingType;
  window['AscCommon'].g_tabtype_left = 0;
  window['AscCommon'].g_tabtype_right = 1;
  window['AscCommon'].g_tabtype_center = 2;
  window['AscCommon'].g_tabtype_clear = 3;
  window['AscCommon'].BinaryCommonWriter = BinaryCommonWriter;
  window['AscCommon'].Binary_CommonReader = Binary_CommonReader;
  window['AscCommon'].FT_Stream2 = FT_Stream2;
  window['AscCommon'].gc_nMaxRow = gc_nMaxRow;
  window['AscCommon'].gc_nMaxCol = gc_nMaxCol;
  window['AscCommon'].gc_nMaxRow0 = gc_nMaxRow0;
  window['AscCommon'].gc_nMaxCol0 = gc_nMaxCol0;
  window['AscCommon'].g_oCellAddressUtils = g_oCellAddressUtils;
  window['AscCommon'].CellAddress = CellAddress;
  window['AscCommon'].isRealObject = isRealObject;
  window['AscCommon'].FileStream = FileStream;
  window['AscCommon'].g_nodeAttributeStart = 0xFA;
  window['AscCommon'].g_nodeAttributeEnd = 0xFB;
})(window);

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
// Import
var AscBrowser = AscCommon.AscBrowser;
var locktype_None = AscCommon.locktype_None;
var locktype_Mine = AscCommon.locktype_Mine;
var locktype_Other = AscCommon.locktype_Other;
var locktype_Other2 = AscCommon.locktype_Other2;
var locktype_Other3 = AscCommon.locktype_Other3;
var contentchanges_Add = AscCommon.contentchanges_Add;
var CColor = AscCommon.CColor;
var g_oCellAddressUtils = AscCommon.g_oCellAddressUtils;

var c_oAscFileType = Asc.c_oAscFileType;

if (typeof String.prototype.startsWith != 'function') {
	String.prototype.startsWith = function (str){
		return this.indexOf(str) === 0;
	};
	String.prototype['startsWith'] = String.prototype.startsWith;
}
if (typeof String.prototype.endsWith !== 'function') {
	String.prototype.endsWith = function(suffix) {
		return this.indexOf(suffix, this.length - suffix.length) !== -1;
	};
	String.prototype['endsWith'] = String.prototype.endsWith;
}
if (typeof String.prototype.repeat !== 'function') {
    String.prototype.repeat = function(count) {
        'use strict';
        if (this == null) {
            throw new TypeError('can\'t convert ' + this + ' to object');
        }
        var str = '' + this;
        count = +count;
        if (count != count) {
            count = 0;
        }
        if (count < 0) {
            throw new RangeError('repeat count must be non-negative');
        }
        if (count == Infinity) {
            throw new RangeError('repeat count must be less than infinity');
        }
        count = Math.floor(count);
        if (str.length == 0 || count == 0) {
            return '';
        }
        // Обеспечение того, что count является 31-битным целым числом, позволяет нам значительно
        // соптимизировать главную часть функции. Впрочем, большинство современных (на август
        // 2014 года) браузеров не обрабатывают строки, длиннее 1 << 28 символов, так что:
        if (str.length * count >= 1 << 28) {
            throw new RangeError('repeat count must not overflow maximum string size');
        }
        var rpt = '';
        for (;;) {
            if ((count & 1) == 1) {
                rpt += str;
            }
            count >>>= 1;
            if (count == 0) {
                break;
            }
            str += str;
        }
        return rpt;
    };
	String.prototype['repeat'] = String.prototype.repeat;
}
// Extend javascript String type
String.prototype.strongMatch = function(regExp){
    if (regExp && regExp instanceof RegExp) {
        var arr = this.toString().match(regExp);
        return !!(arr && arr.length > 0 && arr[0].length == this.length);
    }

    return false;
};

if (typeof require =="function" && !window["XRegExp"]){window["XRegExp"] = require("xregexp");}

var oZipChanges = null;
var sDownloadServiceLocalUrl = "/downloadas";
var sUploadServiceLocalUrl = "/upload";
var sUploadServiceLocalUrlOld = "/uploadold";
var nMaxRequestLength = 5242880;//5mb <requestLimits maxAllowedContentLength="30000000" /> default 30mb

function getEncodingParams() {
	var res = [];
	for(var i = 0; i < AscCommon.c_oAscEncodings.length; ++i) {
		var encoding = AscCommon.c_oAscEncodings[i];
		var newElem = {'codepage': encoding[0], 'name': encoding[3]};
		res.push(newElem);
	}
	return res;
}
function DocumentUrls(){
	this.urls = {};
	this.urlsReverse = {};
  this.documentUrl = "";
	this.imageCount = 0;
}
DocumentUrls.prototype = {
	mediaPrefix: 'media/',
	init: function (urls) {
		this.addUrls(urls);
	},
	getUrls: function () {
		return this.urls;
	},
	addUrls : function(urls){
		for(var i in urls){
			var url = urls[i];
			this.urls[i] = url;
			this.urlsReverse[url] = i;
			this.imageCount++;
		}
	},
	addImageUrl : function(strPath, url){
		var urls = {};
		urls[this.mediaPrefix + strPath] = url;
		this.addUrls(urls);
	},
	getImageUrl : function(strPath){
		return this.getUrl(this.mediaPrefix + strPath);
	},
	getImageLocal : function(url){
		var imageLocal = this.getLocal(url);
		if(imageLocal && this.mediaPrefix == imageLocal.substring(0, this.mediaPrefix.length))
			imageLocal = imageLocal.substring(this.mediaPrefix.length);
		return imageLocal;
	},
	imagePath2Local : function(imageLocal){
		if(imageLocal && this.mediaPrefix == imageLocal.substring(0, this.mediaPrefix.length))
			imageLocal = imageLocal.substring(this.mediaPrefix.length);
		return imageLocal;
	},
	getUrl : function(strPath){
		if(this.urls){
			return this.urls[strPath];
		}
		return null;
	},
	getLocal : function(url){
		if(this.urlsReverse){
			var res = this.urlsReverse[url];
			if (!res && typeof editor !== 'undefined' && editor.ThemeLoader && 0 == url.indexOf(editor.ThemeLoader.ThemesUrlAbs)) {
				res = url.substring(editor.ThemeLoader.ThemesUrlAbs.length);
			}
			return res;
		}
		return null;
	},
	getMaxIndex : function(url){
		return this.imageCount;
	}
};
var g_oDocumentUrls = new DocumentUrls();

function OpenFileResult () {
	this.bSerFormat = false;
	this.data = null;
	this.url = null;
	this.changes = null;
}

function saveWithParts(fSendCommand, fCallback, fCallbackRequest, oAdditionalData, dataContainer) {
	var index = dataContainer.index;
	if(null == dataContainer.part && (!dataContainer.data || dataContainer.data.length <= nMaxRequestLength)){
		oAdditionalData["savetype"] = AscCommon.c_oAscSaveTypes.CompleteAll;
	}
	else{
		if(0 == index){
			oAdditionalData["savetype"] = AscCommon.c_oAscSaveTypes.PartStart;
			dataContainer.count = Math.ceil(dataContainer.data.length / nMaxRequestLength);
		} else if(index != dataContainer.count - 1){
			oAdditionalData["savetype"] = AscCommon.c_oAscSaveTypes.Part;
		} else {
			oAdditionalData["savetype"] = AscCommon.c_oAscSaveTypes.Complete;
		}
		dataContainer.part = dataContainer.data.substring(index * nMaxRequestLength, (index + 1) * nMaxRequestLength);
	}
	dataContainer.index++;
	oAdditionalData["saveindex"] = dataContainer.index;
	fSendCommand(function (incomeObject) {
		if(null != incomeObject && "ok" == incomeObject["status"]){
			if(dataContainer.index < dataContainer.count) {
				oAdditionalData["savekey"] = incomeObject["data"];
        saveWithParts(fSendCommand, fCallback, fCallbackRequest, oAdditionalData, dataContainer);
			} else if(fCallbackRequest){
				fCallbackRequest(incomeObject);
			}
		} else {
			fCallbackRequest ? fCallbackRequest(incomeObject) : fCallback(incomeObject);
		}
	}, oAdditionalData, dataContainer);
}

function loadFileContent(url, callback) {
  asc_ajax({
    url: url,
    dataType: "text",
    success: callback,
    error: function() {
      callback(null);
    }
  });
}

function getJSZipUtils() {
  return window['JSZipUtils'] ? window['JSZipUtils'] : require('jsziputils');
}
function getImageFromChanges (name) {
	var file;
	var ext = GetFileExtension(name);
	if (null !== ext && oZipChanges && (file = oZipChanges.files[name])) {
		var oFileArray = file.asUint8Array();
		return 'data:image/' + ext + ';base64,' + AscCommon.Base64Encode(oFileArray, oFileArray.length, 0);
	}
	return null;
}
function openFileCommand(binUrl, changesUrl, Signature, callback) {
  var bError = false, oResult = new OpenFileResult(), bEndLoadFile = false, bEndLoadChanges = false;
  var onEndOpen = function() {
    if (bEndLoadFile && bEndLoadChanges) {
      if (callback) {
        callback(bError, oResult);
      }
    }
  };
  var sFileUrl = binUrl;
  sFileUrl = sFileUrl.replace(/\\/g, "/");
  asc_ajax({
    url: sFileUrl,
    dataType: "text",
    success: function(result) {
      //получаем url к папке с файлом
      var url;
      var nIndex = sFileUrl.lastIndexOf("/");
      url = (-1 !== nIndex) ? sFileUrl.substring(0, nIndex + 1) : sFileUrl;
      if (0 < result.length) {
        oResult.bSerFormat = Signature === result.substring(0, Signature.length);
        oResult.data = result;
        oResult.url = url;
      } else {
        bError = true;
      }
      bEndLoadFile = true;
      onEndOpen();
    },
    error: function() {
      bEndLoadFile = true;
      bError = true;
      onEndOpen();
    }
  });
  if (null != changesUrl) {
    getJSZipUtils().getBinaryContent(changesUrl, function(err, data) {
      bEndLoadChanges = true;
      if (err) {
        bError = true;
        onEndOpen();
        return;
      }

      oZipChanges = new (require('jszip'))(data);
      oResult.changes = [];
      for (var i in oZipChanges.files) {
        if (i.endsWith('.json')) {
          // Заглушка на имя файла (стоило его начинать с цифры)
          oResult.changes[parseInt(i.slice('changes'.length))] = JSON.parse(oZipChanges.files[i].asText());
        }
      }
      onEndOpen();
    });
  } else {
    bEndLoadChanges = true;
  }
}
function sendCommand(editor, fCallback, rdata, dataContainer) {
  //json не должен превышать размера 2097152, иначе при его чтении будет exception
  var docConnectionId = editor.CoAuthoringApi.getDocId();
  if (docConnectionId && docConnectionId !== rdata["id"]) {
    //на случай если поменялся documentId в Version History
    rdata['docconnectionid'] = docConnectionId;
  }
  if (null == rdata["savetype"]) {
    editor.CoAuthoringApi.openDocument(rdata);
    return;
  }
  rdata["userconnectionid"] = editor.CoAuthoringApi.getUserConnectionId();
  asc_ajax({
    type: 'POST',
    url: sDownloadServiceLocalUrl + '/' + rdata["id"] + '?cmd=' + encodeURIComponent(JSON.stringify(rdata)),
    data: dataContainer.part || dataContainer.data,
    contentType: "application/octet-stream",
    error: function() {
      if (fCallback) {
        fCallback(null, true);
      }
    },
    success: function(msg) {
      if (fCallback) {
        fCallback(JSON.parse(msg), true);
      }
    }
  });
}

function mapAscServerErrorToAscError(nServerError) {
	var nRes = Asc.c_oAscError.ID.Unknown;
	switch (nServerError) {
		case c_oAscServerError.NoError : nRes = Asc.c_oAscError.ID.No; break;
		case c_oAscServerError.TaskQueue :
		case c_oAscServerError.TaskResult : nRes = Asc.c_oAscError.ID.Database; break;
		case c_oAscServerError.ConvertDownload : nRes = Asc.c_oAscError.ID.DownloadError; break;
		case c_oAscServerError.ConvertTimeout : nRes = Asc.c_oAscError.ID.ConvertationTimeout; break;
		case c_oAscServerError.ConvertDRM :
		case c_oAscServerError.ConvertPASSWORD :
		case c_oAscServerError.ConvertMS_OFFCRYPTO : nRes = Asc.c_oAscError.ID.ConvertationPassword; break;
		case c_oAscServerError.ConvertCONVERT_CORRUPTED :
		case c_oAscServerError.ConvertLIBREOFFICE :
		case c_oAscServerError.ConvertPARAMS :
		case c_oAscServerError.ConvertNEED_PARAMS :
		case c_oAscServerError.ConvertUnknownFormat :
		case c_oAscServerError.ConvertReadFile :
		case c_oAscServerError.Convert : nRes = Asc.c_oAscError.ID.ConvertationError; break;
		case c_oAscServerError.UploadContentLength : nRes = Asc.c_oAscError.ID.UplImageSize; break;
		case c_oAscServerError.UploadExtension : nRes = Asc.c_oAscError.ID.UplImageExt; break;
		case c_oAscServerError.UploadCountFiles : nRes = Asc.c_oAscError.ID.UplImageFileCount; break;
		case c_oAscServerError.VKey : nRes = Asc.c_oAscError.ID.FileVKey; break;
		case c_oAscServerError.VKeyEncrypt : nRes = Asc.c_oAscError.ID.VKeyEncrypt; break;
		case c_oAscServerError.VKeyKeyExpire : nRes = Asc.c_oAscError.ID.KeyExpire; break;
		case c_oAscServerError.VKeyUserCountExceed : nRes = Asc.c_oAscError.ID.UserCountExceed; break;
		case c_oAscServerError.Storage :
		case c_oAscServerError.StorageFileNoFound :
		case c_oAscServerError.StorageRead :
		case c_oAscServerError.StorageWrite :
		case c_oAscServerError.StorageRemoveDir :
		case c_oAscServerError.StorageCreateDir :
		case c_oAscServerError.StorageGetInfo :
		case c_oAscServerError.Upload :
		case c_oAscServerError.ReadRequestStream :
		case c_oAscServerError.Unknown : nRes = Asc.c_oAscError.ID.Unknown; break;
	}
	return nRes;
}

function joinUrls(base, relative) {
    //http://stackoverflow.com/questions/14780350/convert-relative-path-to-absolute-using-javascript
    var stack = base.split("/"),
        parts = relative.split("/");
    stack.pop(); // remove current file name (or empty string)
                 // (omit if "base" is the current folder without trailing slash)
    for (var i=0; i<parts.length; i++) {
        if (parts[i] == ".")
            continue;
        if (parts[i] == "..")
            stack.pop();
        else
            stack.push(parts[i]);
    }
    return stack.join("/");
}
function getFullImageSrc2 (src) {
	if (window["NATIVE_EDITOR_ENJINE"])
		return src;

	var start = src.slice(0, 6);
	if (0 === start.indexOf('theme') && editor.ThemeLoader){
		return  editor.ThemeLoader.ThemesUrlAbs + src;
	}

	if (0 !== start.indexOf('http:') && 0 !== start.indexOf('data:') && 0 !== start.indexOf('https:') &&
		0 !== start.indexOf('file:') && 0 !== start.indexOf('ftp:')){
			var srcFull = g_oDocumentUrls.getImageUrl(src);
			if(srcFull){
				return srcFull;
			}
		}
	return src;
}

function fSortAscending( a, b ) {
    return a - b;
}
function fSortDescending( a, b ) {
    return b - a;
}
function fOnlyUnique(value, index, self) {
  return self.indexOf(value) === index;
}
function isLeadingSurrogateChar(nCharCode) {
    return (nCharCode >= 0xD800 && nCharCode <= 0xDFFF);
}
function decodeSurrogateChar(nLeadingChar, nTrailingChar) {
    if (nLeadingChar < 0xDC00 && nTrailingChar >= 0xDC00 && nTrailingChar <= 0xDFFF)
        return 0x10000 + ((nLeadingChar & 0x3FF) << 10) | (nTrailingChar & 0x3FF);
    else
        return null;
}
function encodeSurrogateChar(nUnicode) {
    if(nUnicode < 0x10000)
    {
        return String.fromCharCode(nUnicode);
    }
    else
    {
        nUnicode = nUnicode - 0x10000;
        var nLeadingChar = 0xD800 | (nUnicode >> 10);
        var nTrailingChar = 0xDC00 | (nUnicode & 0x3FF);
        return String.fromCharCode(nLeadingChar) + String.fromCharCode(nTrailingChar);
    }
}

function convertUnicodeToUTF16(sUnicode)
{
    var sUTF16 = "";
    var nLength = sUnicode.length;
    for (var nPos = 0; nPos < nLength; nPos++)
    {
        sUTF16 += encodeSurrogateChar(sUnicode[nPos]);
    }

    return sUTF16;
}
function convertUTF16toUnicode(sUTF16)
{
    var sUnicode = [];
    var nLength = sUTF16.length;
    for (var nPos = 0; nPos < nLength; nPos++)
    {
        var nUnicode = null;
        var nCharCode = sUTF16.charCodeAt(nPos);
        if (isLeadingSurrogateChar(nCharCode))
        {
            if (nPos + 1 < nLength)
            {
                nPos++;
                var nTrailingChar = sUTF16.charCodeAt(nPos);
                nUnicode = decodeSurrogateChar(nCharCode, nTrailingChar);
            }
        }
        else
            nUnicode = nCharCode;

        if (null !== nUnicode)
            sUnicode.push(nUnicode);
    }

    return sUnicode;
}

/**
 * @constructor
 */
function test_ws_name() {
    var self = new XRegExp( "[^\\p{L}(\\p{L}\\d._)*]" );
    self.regexp_letter = new XRegExp( "^\\p{L}[\\p{L}\\d.]*$" );
    self.regexp_left_bracket = new XRegExp( "\\[" );
    self.regexp_right_bracket = new XRegExp( "\\]" );
    self.regexp_left_brace = new XRegExp( "\\{" );
    self.regexp_right_brace = new XRegExp( "\\}" );
    self.regexp_number_mark = new XRegExp( "№" );
    self.regexp_special_letters = new XRegExp( "[\\'\\*\\[\\]\\\\:\\/]" );
    self.sheet_name_character_special = new XRegExp( "('')|[^\\'\\*\\[\\]\\:/\\?]" );
    self.sheet_name_start_character_special = new XRegExp( "^[^\\'\\*\\[\\]\\:/\\?]" );
    self.sheet_name_end_character_special = new XRegExp( "[^\\'\\*\\[\\]\\:/\\?]$" );
    self.sheet_name_character = new XRegExp( "[-+*/^&%<=>:\\'\\[\\]\\?\\s]" );
    self.book_name_character_special =
        self.book_name_start_character_special = new XRegExp( "[^\\'\\*\\[\\]\\:\\?]" );
    self.apostrophe = new XRegExp( "'" );
    self.srt_left_bracket = "[";
    self.srt_right_bracket = "]";
    self.srt_left_brace = "{";
    self.srt_right_brace = "}";
    self.srt_number_letter = "№";

    self.matchRec = function ( str, left, right ) {
        return XRegExp.matchRecursive( str, "\\" + left, "\\" + right, "g" )
    };

    self.test = function ( str ) {
        var matchRec, splitStr = str, res;
        if ( this.regexp_left_bracket.test( str ) || this.regexp_right_bracket.test( str ) ) {
            try {
                if ( str[0] != "[" )
                    return false;

                matchRec = this.matchRec( str, this.srt_left_bracket, this.srt_right_bracket );

                if ( matchRec.length > 1 ) {
                    return false;
                }
                else if ( matchRec[0] == "" ) {
                    return false;
                }
                else if ( this.regexp_special_letters.test( matchRec[i] ) ) {
                    return false;
                }
                splitStr = str.split( "[" + matchRec[0] + "]" )[1];
            }
            catch( e ) {
                return false;
            }
        }
        res = this.sheet_name_start_character_special.test( splitStr ) &&
            this.sheet_name_end_character_special.test( splitStr ) && !XRegExp.test( splitStr, this );

        this.sheet_name_start_character_special.lastIndex = 0;
        this.sheet_name_end_character_special.lastIndex = 0;
        XRegExp.lastIndex = 0;
        this.regexp_special_letters.lastIndex = 0;
        this.regexp_right_bracket.lastIndex = 0;
        this.regexp_left_bracket.lastIndex = 0;

        return res;
    };

    return self;
}

function test_ws_name2() {
    var str_namedRanges = "[A-Z\u005F\u0080-\u0081\u0083\u0085-\u0087\u0089-\u008A\u008C-\u0091\u0093-\u0094\u0096-\u0097\u0099-\u009A\u009C-\u009F\u00A1-\u00A5\u00A7-\u00A8\u00AA\u00AD\u00AF-\u00BA\u00BC-\u02B8\u02BB-\u02C1\u02C7\u02C9-\u02CB\u02CD\u02D0-\u02D1\u02D8-\u02DB\u02DD\u02E0-\u02E4\u02EE\u0370-\u0373\u0376-\u0377\u037A-\u037D\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u0523\u0531-\u0556\u0559\u0561-\u0587\u05D0-\u05EA\u05F0-\u05F2\u0621-\u064A\u066E-\u066F\u0671-\u06D3\u06D5\u06E5-\u06E6\u06EE-\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4-\u07F5\u07FA\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0972\u097B-\u097F\u0985-\u098C\u098F-\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC-\u09DD\u09DF-\u09E1\u09F0-\u09F1\u0A05-\u0A0A\u0A0F-\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32-\u0A33\u0A35-\u0A36\u0A38-\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2-\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0-\u0AE1\u0B05-\u0B0C\u0B0F-\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32-\u0B33\u0B35-\u0B39\u0B3D\u0B5C-\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99-\u0B9A\u0B9C\u0B9E-\u0B9F\u0BA3-\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C33\u0C35-\u0C39\u0C3D\u0C58-\u0C59\u0C60-\u0C61\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDE\u0CE0-\u0CE1\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D28\u0D2A-\u0D39\u0D3D\u0D60-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E3A\u0E40-\u0E4E\u0E81-\u0E82\u0E84\u0E87-\u0E88\u0E8A\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA-\u0EAB\u0EAD-\u0EB0\u0EB2-\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDD\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8B\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065-\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10D0-\u10FA\u10FC\u1100-\u1159\u115F-\u11A2\u11A8-\u11F9\u1200-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F4\u1401-\u166C\u166F-\u1676\u1681-\u169A\u16A0-\u16EA\u16EE-\u16F0\u1700-\u170C\u170E-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1877\u1880-\u18A8\u18AA\u1900-\u191C\u1950-\u196D\u1970-\u1974\u1980-\u19A9\u19C1-\u19C7\u1A00-\u1A16\u1B05-\u1B33\u1B45-\u1B4B\u1B83-\u1BA0\u1BAE-\u1BAF\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2010\u2013-\u2016\u2018\u201C-\u201D\u2020-\u2021\u2025-\u2027\u2030\u2032-\u2033\u2035\u203B\u2071\u2074\u207F\u2081-\u2084\u2090-\u2094\u2102-\u2103\u2105\u2107\u2109-\u2113\u2115-\u2116\u2119-\u211D\u2121-\u2122\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2153-\u2154\u215B-\u215E\u2160-\u2188\u2190-\u2199\u21D2\u21D4\u2200\u2202-\u2203\u2207-\u2208\u220B\u220F\u2211\u2215\u221A\u221D-\u2220\u2223\u2225\u2227-\u222C\u222E\u2234-\u2237\u223C-\u223D\u2248\u224C\u2252\u2260-\u2261\u2264-\u2267\u226A-\u226B\u226E-\u226F\u2282-\u2283\u2286-\u2287\u2295\u2299\u22A5\u22BF\u2312\u2460-\u24B5\u24D0-\u24E9\u2500-\u254B\u2550-\u2574\u2581-\u258F\u2592-\u2595\u25A0-\u25A1\u25A3-\u25A9\u25B2-\u25B3\u25B6-\u25B7\u25BC-\u25BD\u25C0-\u25C1\u25C6-\u25C8\u25CB\u25CE-\u25D1\u25E2-\u25E5\u25EF\u2605-\u2606\u2609\u260E-\u260F\u261C\u261E\u2640\u2642\u2660-\u2661\u2663-\u2665\u2667-\u266A\u266C-\u266D\u266F\u2C00-\u2C2E\u2C30-\u2C5E\u2C60-\u2C6F\u2C71-\u2C7D\u2C80-\u2CE4\u2D00-\u2D25\u2D30-\u2D65\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u3000-\u3003\u3005-\u3017\u301D-\u301F\u3021-\u3029\u3031-\u3035\u3038-\u303C\u3041-\u3096\u309B-\u309F\u30A1-\u30FF\u3105-\u312D\u3131-\u318E\u31A0-\u31B7\u31F0-\u321C\u3220-\u3229\u3231-\u3232\u3239\u3260-\u327B\u327F\u32A3-\u32A8\u3303\u330D\u3314\u3318\u3322-\u3323\u3326-\u3327\u332B\u3336\u333B\u3349-\u334A\u334D\u3351\u3357\u337B-\u337E\u3380-\u3384\u3388-\u33CA\u33CD-\u33D3\u33D5-\u33D6\u33D8\u33DB-\u33DD\u3400-\u4DB5\u4E00-\u9FC3\uA000-\uA48C\uA500-\uA60C\uA610-\uA61F\uA62A-\uA62B\uA640-\uA65F\uA662-\uA66E\uA680-\uA697\uA722-\uA787\uA78B-\uA78C\uA7FB-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA90A-\uA925\uA930-\uA946\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAC00-\uD7A3\uE000-\uF848\uF900-\uFA2D\uFA30-\uFA6A\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40-\uFB41\uFB43-\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE30-\uFE31\uFE33-\uFE44\uFE49-\uFE52\uFE54-\uFE57\uFE59-\uFE66\uFE68-\uFE6B\uFE70-\uFE74\uFE76-\uFEFC\uFF01-\uFF5E\uFF61-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC\uFFE0-\uFFE6]",
        str_namedSheetsRange = "\u0001-\u0026\u0028-\u0029\u002B-\u002D\u003B-\u003E\u0040\u005E\u0060\u007B-\u007F\u0082\u0084\u008B\u0092\u0095\u0098\u009B\u00A0\u00A6\u00A9\u00AB-\u00AC\u00AE\u00BB\u0378-\u0379\u037E-\u0383\u0387\u038B\u038D\u03A2\u0524-\u0530\u0557-\u0558\u055A-\u0560\u0588-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EF\u05F3-\u05FF\u0604-\u0605\u0609-\u060A\u060C-\u060D\u061B-\u061E\u0620\u065F\u066A-\u066D\u06D4\u0700-\u070E\u074B-\u074C\u07B2-\u07BF\u07F7-\u07F9\u07FB-\u0900\u093A-\u093B\u094E-\u094F\u0955-\u0957\u0964-\u0965\u0970\u0973-\u097A\u0980\u0984\u098D-\u098E\u0991-\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA-\u09BB\u09C5-\u09C6\u09C9-\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4-\u09E5\u09FB-\u0A00\u0A04\u0A0B-\u0A0E\u0A11-\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A-\u0A3B\u0A3D\u0A43-\u0A46\u0A49-\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA-\u0ABB\u0AC6\u0ACA\u0ACE-\u0ACF\u0AD1-\u0ADF\u0AE4-\u0AE5\u0AF0\u0AF2-\u0B00\u0B04\u0B0D-\u0B0E\u0B11-\u0B12\u0B29\u0B31\u0B34\u0B3A-\u0B3B\u0B45-\u0B46\u0B49-\u0B4A\u0B4E-\u0B55\u0B58-\u0B5B\u0B5E\u0B64-\u0B65\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE-\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BFB-\u0C00\u0C04\u0C0D\u0C11\u0C29\u0C34\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5A-\u0C5F\u0C64-\u0C65\u0C70-\u0C77\u0C80-\u0C81\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA-\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4-\u0CE5\u0CF0\u0CF3-\u0D01\u0D04\u0D0D\u0D11\u0D29\u0D3A-\u0D3C\u0D45\u0D49\u0D4E-\u0D56\u0D58-\u0D5F\u0D64-\u0D65\u0D76-\u0D78\u0D80-\u0D81\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE-\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3E\u0E4F\u0E5A-\u0E80\u0E83\u0E85-\u0E86\u0E89\u0E8B-\u0E8C\u0E8E-\u0E93\u0E98\u0EA0\u0EA4\u0EA6\u0EA8-\u0EA9\u0EAC\u0EBA\u0EBE-\u0EBF\u0EC5\u0EC7\u0ECE-\u0ECF\u0EDA-\u0EDB\u0EDE-\u0EFF\u0F04-\u0F12\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F8C-\u0F8F\u0F98\u0FBD\u0FCD\u0FD0-\u0FFF\u104A-\u104F\u109A-\u109D\u10C6-\u10CF\u10FB\u10FD-\u10FF\u115A-\u115E\u11A3-\u11A7\u11FA-\u11FF\u1249\u124E-\u124F\u1257\u1259\u125E-\u125F\u1289\u128E-\u128F\u12B1\u12B6-\u12B7\u12BF\u12C1\u12C6-\u12C7\u12D7\u1311\u1316-\u1317\u135B-\u135E\u1361-\u1368\u137D-\u137F\u139A-\u139F\u13F5-\u1400\u166D-\u166E\u1677-\u167F\u169B-\u169F\u16EB-\u16ED\u16F1-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DA\u17DE-\u17DF\u17EA-\u17EF\u17FA-\u180A\u180F\u181A-\u181F\u1878-\u187F\u18AB-\u18FF\u191D-\u191F\u192C-\u192F\u193C-\u193F\u1941-\u1945\u196E-\u196F\u1975-\u197F\u19AA-\u19AF\u19CA-\u19CF\u19DA-\u19DF\u1A1C-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B60\u1B7D-\u1B7F\u1BAB-\u1BAD\u1BBA-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E-\u1CFF\u1DE7-\u1DFD\u1F16-\u1F17\u1F1E-\u1F1F\u1F46-\u1F47\u1F4E-\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E-\u1F7F\u1FB5\u1FC5\u1FD4-\u1FD5\u1FDC\u1FF0-\u1FF1\u1FF5\u1FFF\u2011-\u2012\u2017\u2019-\u201B\u201E-\u201F\u2022-\u2024\u2031\u2034\u2036-\u203A\u203C-\u2043\u2045-\u2051\u2053-\u205E\u2065-\u2069\u2072-\u2073\u207D-\u207E\u208D-\u208F\u2095-\u209F\u20B6-\u20CF\u20F1-\u20FF\u2150-\u2152\u2189-\u218F\u2329-\u232A\u23E8-\u23FF\u2427-\u243F\u244B-\u245F\u269E-\u269F\u26BD-\u26BF\u26C4-\u2700\u2705\u270A-\u270B\u2728\u274C\u274E\u2753-\u2755\u2757\u275F-\u2760\u2768-\u2775\u2795-\u2797\u27B0\u27BF\u27C5-\u27C6\u27CB\u27CD-\u27CF\u27E6-\u27EF\u2983-\u2998\u29D8-\u29DB\u29FC-\u29FD\u2B4D-\u2B4F\u2B55-\u2BFF\u2C2F\u2C5F\u2C70\u2C7E-\u2C7F\u2CEB-\u2CFC\u2CFE-\u2CFF\u2D26-\u2D2F\u2D66-\u2D6E\u2D70-\u2D7F\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u2FEF\u2FFC-\u2FFF\u3018-\u301C\u3030\u303D\u3040\u3097-\u3098\u30A0\u3100-\u3104\u312E-\u3130\u318F\u31B8-\u31BF\u31E4-\u31EF\u321F\u3244-\u324F\u32FF\u4DB6-\u4DBF\u9FC4-\u9FFF\uA48D-\uA48F\uA4C7-\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA660-\uA661\uA673-\uA67B\uA67E\uA698-\uA6FF\uA78D-\uA7FA\uA82C-\uA83F\uA874-\uA87F\uA8C5-\uA8CF\uA8DA-\uA8FF\uA92F\uA954-\uA9FF\uAA37-\uAA3F\uAA4E-\uAA4F\uAA5A-\uABFF\uD7A4-\uD7FF\uFA2E-\uFA2F\uFA6B-\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90-\uFD91\uFDC8-\uFDEF\uFDFE-\uFDFF\uFE10-\uFE1F\uFE27-\uFE2F\uFE32\uFE45-\uFE48\uFE53\uFE58\uFE67\uFE6C-\uFE6F\uFE75\uFEFD-\uFEFE\uFF00\uFF5F-\uFF60\uFFBF-\uFFC1\uFFC8-\uFFC9\uFFD0-\uFFD1\uFFD8-\uFFD9\uFFDD-\uFFDF\uFFE7\uFFEF-\uFFF8\uFFFE-\uFFFF",
        str_operator = ",\\s-+/^&%<=>",
        str_excludeCharts = "'*\\[\\]\\:/?";

    this.regExp_namedRanges = new RegExp(str_namedRanges,"i");
    this.regExp_namedSheetsRange = new RegExp("["+str_namedSheetsRange+"]","ig");
//    /[-+*\/^&%<=>:]/,
    this.regExp_strOperator = new RegExp("["+str_operator+"]","ig");
    this.regExp_strExcludeCharts = new RegExp("["+str_excludeCharts+"]","ig");

    this.test = function(str){
        var ch1 = str.substr(0,1);

        this.regExp_strExcludeCharts.lastIndex = 0;
        this.regExp_namedRanges.lastIndex = 0;
        this.regExp_namedSheetsRange.lastIndex = 0;
        this.regExp_strOperator.lastIndex = 0;

        if( this.regExp_strExcludeCharts.test(str) ){//если содержутся недопустимые символы.
            return undefined;
        }

        if( !this.regExp_namedRanges.test(ch1) ){//если первый символ находится не в str_namedRanges, то однозначно надо экранировать
            return false;
        }
        else{
            if( this.regExp_namedSheetsRange.test( str ) || this.regExp_strOperator.test(str) ){//первый символ допустимый. проверяем всю строку на наличие символов, с которыми необходимо экранировать
                return false;
            }
            //проверка на то, что название листа не совпадает с допустимым адресом ячейки, как в A1 так и RC стилях.
            var match = str.match( rx_ref );
            if (match != null) {
                var m1 = match[1], m2 = match[2];
                if ( match.length >= 3 && g_oCellAddressUtils.colstrToColnum( m1.substr( 0, (m1.length - m2.length) ) ) <= AscCommon.gc_nMaxCol && parseInt( m2 ) <= AscCommon.gc_nMaxRow ) {
                    return false;
                }
            }
            return true;
        }
    };

    return this;

}

function test_defName(){
    var nameRangeRE = new RegExp("(^(["+str_namedRanges+"_])(["+str_namedRanges+"_0-9]*)$)","i" );

    this.test = function(str){
        var match, m1, m2;
        if( !nameRangeRE.test(str) ){
            return false;
        }

        match = str.match( rx_ref );
        if (match != null) {
            m1 = match[1];
            m2 = match[2];
            if ( match.length >= 3 && g_oCellAddressUtils.colstrToColnum( m1.substr( 0, (m1.length - m2.length) ) ) <= AscCommon.gc_nMaxCol && parseInt( m2 ) <= AscCommon.gc_nMaxRow ) {
                return false;
            }
        }

        return true;
    };

    return this;
}

  var cStrucTableReservedWords = {
    all: "#All", data: "#Data", headers: "#Headers", totals: "#Totals", thisrow: "#This Row", at: "@"
  };
  var FormulaTablePartInfo = {
    all: 1,
    data: 2,
    headers: 3,
    totals: 4,
    thisRow: 5,
    columns: 6
  };
  
var cStrucTableLocalColumns = null,
	cBoolLocal = {},
	cErrorOrigin = {"nil":"#NULL!","div":"#DIV\/0!","value":"#VALUE!","ref":"#REF!","name":"#NAME?","num":"#NUM!","na":"#N\/A","getdata":"#GETTING_DATA","uf":"#UNSUPPORTED_FUNCTION!"},
	cErrorLocal = {};

function build_local_rx(data){
	build_rx_table_local(data?data["StructureTables"]:null);
    build_rx_bool_local(data?data["CONST_TRUE_FALSE"]:null);
    build_rx_error_local(data?data["CONST_ERROR"]:null);

}

function build_rx_table_local(local){
	rx_table_local = build_rx_table(local);
}
function build_rx_table(local){
  cStrucTableLocalColumns = ( local ? local : {"h": "Headers", "d": "Data", "a": "All", "tr": "This row", "t": "Totals"} );
    var loc_all = cStrucTableLocalColumns['a'],
        loc_headers = cStrucTableLocalColumns['h'],
        loc_data = cStrucTableLocalColumns['d'],
        loc_totals = cStrucTableLocalColumns['t'],
        loc_this_row = cStrucTableLocalColumns['tr'],
        structured_tables_headata = new XRegExp('(?:\\[\\#'+loc_headers+'\\]\\,\\[\\#'+loc_data+'\\])'),
        structured_tables_datals = new XRegExp('(?:\\[\\#'+loc_data+'\\]\\,\\[\\#'+loc_totals+'\\])' ),
        structured_tables_userColumn = new XRegExp('(?:[' + str_namedRanges + '\\d.]|\\u0027[#\\[\\]\\u0027]|\\u0020)+'),
        structured_tables_reservedColumn = new XRegExp('\\#(?:'+loc_all+'|'+loc_headers+'|'+loc_totals+'|'+loc_data+'|'+loc_this_row+')|@');

	return XRegExp.build( '^(?<tableName>{{tableName}})\\[(?<columnName>{{columnName}})?\\]', {
        "tableName" : new XRegExp( "^(:?[" + str_namedRanges + "][" + str_namedRanges + "\\d.]*)" ),
        "columnName": XRegExp.build( '(?<reservedColumn>{{reservedColumn}})|(?<oneColumn>{{userColumn}})|(?<columnRange>{{userColumnRange}})|(?<hdtcc>{{hdtcc}})', {
            "userColumn"     : structured_tables_userColumn,
            "reservedColumn" : structured_tables_reservedColumn,
            "userColumnRange": XRegExp.build( '\\[(?<colStart>{{uc}})\\]\\:\\[(?<colEnd>{{uc}})\\]', {
                "uc": structured_tables_userColumn
            } ),
            "hdtcc"          : XRegExp.build( '(?<hdt>\\[{{rc}}\\]|{{hd}}|{{dt}})(?:\\,(?:\\[(?<hdtcstart>{{uc}})\\])(?:\\:(?:\\[(?<hdtcend>{{uc}})\\]))?)?', {
                "rc": structured_tables_reservedColumn,
				"hd": structured_tables_headata,
				"dt": structured_tables_datals,
				"uc": structured_tables_userColumn
            } )
        } )
    }, 'i' );
}
function build_rx_bool_local(local){
	rx_bool_local = build_rx_bool(local);
}
function build_rx_bool(local){
  // ToDo переделать на более правильную реализацию. Не особо правильное копирование
  local = local ? local : {"t":"TRUE","f":"FALSE"};
  var t = cBoolLocal['t'] = local['t'];
  var f = cBoolLocal['f'] = local['f'];

	build_rx_array_local(local);
	return new RegExp( "^("+t+"|"+f+")([-+*\\/^&%<=>: ;),]|$)","i" );
}

function build_rx_error_local(local){
	rx_error_local = build_rx_error(local);
}
function build_rx_error(local){
  // ToDo переделать на более правильную реализацию. Не особо правильное копирование
  local = local ? local : {"nil":"#NULL!","div":"#DIV\/0!","value":"#VALUE!","ref":"#REF!","name":"#NAME\\?","num":"#NUM!","na":"#N\/A","getdata":"#GETTING_DATA","uf":"#UNSUPPORTED_FUNCTION!"};
	cErrorLocal['nil'] = local['nil'];
  cErrorLocal['div'] = local['div'];
  cErrorLocal['value'] = local['value'];
  cErrorLocal['ref'] = local['ref'];
  cErrorLocal['name'] = local['name'];
  cErrorLocal['num'] = local['num'];
  cErrorLocal['na'] = local['na'];
  cErrorLocal['getdata'] = local['getdata'];
  cErrorLocal['uf'] = local['uf'];

	return new RegExp( "^(" + 	cErrorLocal["nil"] 		+ "|" +
								cErrorLocal["div"] 		+ "|" +
								cErrorLocal["value"] 	+ "|" +
								cErrorLocal["ref"] 		+ "|" +
								cErrorLocal["name"] 	+ "|" +
								cErrorLocal["num"] 		+ "|" +
								cErrorLocal["na"] 		+ "|" +
								cErrorLocal["getdata"] 	+ "|" +
								cErrorLocal["uf"] 		+ ")", "i" );
}

function build_rx_array_local(localBool, digitSepar, localError){
	var localBool = ( localBool ? localBool : {"t":"TRUE","f":"FALSE"} );
	rx_array_local = build_rx_array(localBool, digitSepar, localError);
}
function build_rx_array(localBool, digitSepar, localError){
	return new RegExp("^\\{(([+-]?\\d*(\\d|\\"+digitSepar+")\\d*([eE][+-]?\\d+)?)?(\"((\"\"|[^\"])*)\")?"+
			          "(#NULL!|#DIV\/0!|#VALUE!|#REF!|#NAME\\?|#NUM!|#UNSUPPORTED_FUNCTION!|#N\/A|#GETTING_DATA|"+
			          localBool["t"]+"|"+localBool["f"]+")?["+FormulaSeparators.arrayRowSeparator+"\\"+FormulaSeparators.arrayColSeparator +"]?)*\\}","i");

}

var PostMessageType = {
    UploadImage:0,
    ExtensionExist:1
};

var c_oAscServerError = {
    NoError:0,
    Unknown:-1,
    ReadRequestStream:-3,

    TaskQueue:-20,

    TaskResult:-40,

    Storage:-60,
    StorageFileNoFound:-61,
    StorageRead:-62,
    StorageWrite:-63,
    StorageRemoveDir:-64,
    StorageCreateDir:-65,
    StorageGetInfo:-66,

    Convert:-80,
    ConvertDownload:-81,
    ConvertUnknownFormat:-82,
    ConvertTimeout:-83,
    ConvertReadFile:-84,
    ConvertMS_OFFCRYPTO:-85,
    ConvertCONVERT_CORRUPTED:-86,
    ConvertLIBREOFFICE:-87,
    ConvertPARAMS:-88,
    ConvertNEED_PARAMS:-89,
    ConvertDRM:-90,
    ConvertPASSWORD:-91,

    Upload:-100,
    UploadContentLength:-101,
    UploadExtension:-102,
    UploadCountFiles:-103,

    VKey:-120,
    VKeyEncrypt:-121,
    VKeyKeyExpire:-122,
    VKeyUserCountExceed:-123
};

var c_oAscImageUploadProp = {//Не все браузеры позволяют получить информацию о файле до загрузки(например ie9), меняя параметры здесь надо поменять аналогичные параметры в web.common
    MaxFileSize:25000000, //25 mb
    SupportedFormats:[ "jpg", "jpeg", "jpe", "png", "gif", "bmp"]
};

/**
 *
 * @param sName
 * @returns {*}
 * @constructor
 */
function GetFileExtension (sName) {
	var nIndex = sName ? sName.lastIndexOf(".") : -1;
	if (-1 != nIndex)
		return sName.substring(nIndex + 1).toLowerCase();
	return null;
}
function changeFileExtention (sName, sNewExt) {
  var sOldExt = GetFileExtension(sName);
  if(sOldExt) {
    return sName.substring(0, sName.length - sOldExt.length) + sNewExt;
  } else {
    return sName + '.' + sNewExt;
  }
}
function getExtentionByFormat (format) {
  switch(format) {
    case c_oAscFileType.PDF: return 'pdf'; break;
    case c_oAscFileType.HTML: return 'html'; break;
    // Word
    case c_oAscFileType.DOCX: return 'docx'; break;
    case c_oAscFileType.DOC: return 'doc'; break;
    case c_oAscFileType.ODT: return 'odt'; break;
    case c_oAscFileType.RTF: return 'rtf'; break;
    case c_oAscFileType.TXT: return 'txt'; break;
    case c_oAscFileType.MHT: return 'mht'; break;
    case c_oAscFileType.EPUB: return 'epub'; break;
    case c_oAscFileType.FB2: return 'fb2'; break;
    case c_oAscFileType.MOBI: return 'mobi'; break;
    case c_oAscFileType.DOCY: return 'doct'; break;
    case c_oAscFileType.JSON: return 'json'; break;
    // Excel
    case c_oAscFileType.XLSX: return 'xlsx'; break;
    case c_oAscFileType.XLS: return 'xls'; break;
    case c_oAscFileType.ODS: return 'ods'; break;
    case c_oAscFileType.CSV: return 'csv'; break;
    case c_oAscFileType.XLSY: return 'xlst'; break;
    // PowerPoint
    case c_oAscFileType.PPTX: return 'pptx'; break;
    case c_oAscFileType.PPT: return 'ppt'; break;
    case c_oAscFileType.ODP: return 'odp'; break;
  }
  return '';
}
function InitOnMessage (callback) {
	if (window.addEventListener) {
		window.addEventListener("message", function (event) {
			if (null != event && null != event.data) {
				try {
					var data = JSON.parse(event.data);
					if (null != data && null != data["type"] && PostMessageType.UploadImage == data["type"]) {
						if (c_oAscServerError.NoError == data["error"]) {
							var urls = data["urls"];
							if (urls) {
								g_oDocumentUrls.addUrls(urls);
								var firstUrl;
								for (var i in urls) {
									if (urls.hasOwnProperty(i)) {
										firstUrl = urls[i];
										break;
									}
								}
								callback(Asc.c_oAscError.ID.No, firstUrl);
							}

						} else
							callback(mapAscServerErrorToAscError(data["error"]));
					}
				} catch (err) {
				}
			}
		}, false);
	}
}
function ShowImageFileDialog (documentId, documentUserId, callback, callbackOld) {
	var fileName;
	if ("undefined" != typeof(FileReader)) {
		fileName = GetUploadInput(function (e) {
			if (e && e.target && e.target.files) {
				var nError = ValidateUploadImage(e.target.files);
				callback(mapAscServerErrorToAscError(nError), e.target.files);
			} else {
				callback(Asc.c_oAscError.ID.Unknown);
			}
		});
	} else {
		var frameWindow = GetUploadIFrame();
		var content = '<html><head></head><body><form action="'+sUploadServiceLocalUrlOld+'/'+documentId+'/'+documentUserId+'/'+g_oDocumentUrls.getMaxIndex()+'" method="POST" enctype="multipart/form-data"><input id="apiiuFile" name="apiiuFile" type="file" accept="image/*" size="1"><input id="apiiuSubmit" name="apiiuSubmit" type="submit" style="display:none;"></form></body></html>';
		frameWindow.document.open();
		frameWindow.document.write(content);
		frameWindow.document.close();

		fileName = frameWindow.document.getElementById("apiiuFile");
		var fileSubmit = frameWindow.document.getElementById("apiiuSubmit");

		fileName.onchange = function (e) {
			if (e && e.target && e.target.files) {
				var nError = ValidateUploadImage(e.target.files);
				if (c_oAscServerError.NoError != nError) {
					callbackOld(mapAscServerErrorToAscError(nError));
					return;
				}
			}
			callbackOld(Asc.c_oAscError.ID.No);
			fileSubmit.click();
		};
	}

	//todo пересмотреть opera
	if (AscBrowser.isOpera)
		setTimeout( function(){fileName.click();}, 0);
	else
		fileName.click();
}
function InitDragAndDrop (oHtmlElement, callback) {
	if ("undefined" != typeof(FileReader) && null != oHtmlElement) {
		oHtmlElement["ondragover"] = function (e) {
			e.preventDefault();
			e.dataTransfer.dropEffect = CanDropFiles(e) ? 'copy' : 'none';
			return false;
		};
		oHtmlElement["ondrop"] = function (e) {
			e.preventDefault();
			var files = e.dataTransfer.files;
			var nError = ValidateUploadImage(files);
			callback(mapAscServerErrorToAscError(nError), files);
		};
	}
}
function UploadImageFiles (files, documentId, documentUserId, callback) {
  if (files.length > 0) {
    var file = files[0];
    Common.Gateway.jio_putAttachment(documentId, undefined, file)
      .push(function (image_url) {
        callback(Asc.c_oAscError.ID.No, 'jio:' + image_url);
      })
      .push(undefined, function (error) {
        console.log(error);
        callback(Asc.c_oAscError.ID.Unknown);
      });
  } else {
    callback(Asc.c_oAscError.ID.Unknown);
  }
}
function ValidateUploadImage( files ) {
	var nRes = c_oAscServerError.NoError;
	if (files.length > 0) {
		for (var i = 0, length = files.length; i < length; i++) {
			var file = files[i];
			//проверяем расширение файла
			var sName = file.fileName || file.name;
			if (sName) {
				var bSupported = false;
				var ext = GetFileExtension(sName);
				if (null !== ext) {
					for (var j = 0, length2 = c_oAscImageUploadProp.SupportedFormats.length; j < length2; j++) {
						if (c_oAscImageUploadProp.SupportedFormats[j] == ext) {
							bSupported = true;
							break;
						}
					}
				}
				if (false == bSupported)
					nRes = c_oAscServerError.UploadExtension;
			}
			if (Asc.c_oAscError.ID.No == nRes) {
				var nSize = file.fileSize || file.size;
				if (nSize && c_oAscImageUploadProp.MaxFileSize < nSize)
					nRes = c_oAscServerError.UploadContentLength;
			}
			if (c_oAscServerError.NoError != nRes)
				break;
		}
	} else
		nRes = c_oAscServerError.UploadCountFiles;
	return nRes;
}
function CanDropFiles( event ) {
    var bRes = false;
    if ( event.dataTransfer.types ) {
        for ( var i = 0, length = event.dataTransfer.types.length; i < length; ++i ) {
            var type = event.dataTransfer.types[i];
            if ( type == "Files" ) {
                if ( event.dataTransfer.items ) {
                    for ( var j = 0, length2 = event.dataTransfer.items.length; j < length2; j++ ) {
                        var item = event.dataTransfer.items[j];
                        if ( item.type && item.kind && "file" == item.kind.toLowerCase() ) {
                            bRes = false;
                            for ( var k = 0, length3 = c_oAscImageUploadProp.SupportedFormats.length; k < length3; k++ ) {
                                if ( -1 != item.type.indexOf( c_oAscImageUploadProp.SupportedFormats[k] ) ) {
                                    bRes = true;
                                    break;
                                }
                            }
                            if ( false == bRes )
                                break;
                        }
                    }
                }
                else
                    bRes = true;
                break;
            }
        }
    }
    return bRes;
}
function GetUploadIFrame() {
    var sIFrameName = "apiImageUpload";
    var oImageUploader = document.getElementById( sIFrameName );
    if ( !oImageUploader ) {
        var frame = document.createElement( "iframe" );
        frame.name = sIFrameName;
        frame.id = sIFrameName;
        frame.setAttribute( "style", "position:absolute;left:-2px;top:-2px;width:1px;height:1px;z-index:-1000;" );
        document.body.appendChild( frame );
    }
    return window.frames[sIFrameName];
}
function GetUploadInput(onchange) {
    var inputName = 'apiiuFile';
    var input = document.getElementById( inputName );
    //удаляем чтобы очистить input от предыдущего ввода
    if (input) {
        document.body.removeChild(input);
    }
    input = document.createElement("input");
    input.setAttribute('id', inputName);
    input.setAttribute('name', inputName);
    input.setAttribute('type', 'file');
    input.setAttribute('accept', 'image/*');
    input.setAttribute('style', 'position:absolute;left:-2px;top:-2px;width:1px;height:1px;z-index:-1000;');
    input.onchange = onchange;
    document.body.appendChild( input );
    return input;
}

  var FormulaSeparators = {
    arrayRowSeparatorDef : ';',
    arrayColSeparatorDef : ',',
    digitSeparatorDef : '.',
    functionArgumentSeparatorDef: ',',
    arrayRowSeparator : ';',
    arrayColSeparator : ',',
    digitSeparator : '.',
    functionArgumentSeparator : ','
  };

var g_oCodeSpace = 32; // Code of space
var g_arrCodeOperators = [37, 38, 42, 43, 45, 47, 58, 94]; // Code of operators [%, &, *, +, -, /, :, ^]
var g_oStartCodeOperatorsCompare = 60; // Start code of operators <=>
var g_oEndCodeOperatorsCompare = 62; // End code of operators <=>
var g_oCodeLeftParentheses = 40; // Code of (
var g_oCodeRightParentheses = 41; // Code of )
var g_oCodeLeftBrace = 123; // Code of {
var g_oCodeRightBrace = 125; // Code of }

/*Functions that checks of an element in formula*/
var str_namedRanges = "A-Za-z\u005F\u0080-\u0081\u0083\u0085-\u0087\u0089-\u008A\u008C-\u0091\u0093-\u0094\u0096-\u0097\u0099-\u009A\u009C-\u009F\u00A1-\u00A5\u00A7-\u00A8\u00AA\u00AD\u00AF-\u00BA\u00BC-\u02B8\u02BB-\u02C1\u02C7\u02C9-\u02CB\u02CD\u02D0-\u02D1\u02D8-\u02DB\u02DD\u02E0-\u02E4\u02EE\u0370-\u0373\u0376-\u0377\u037A-\u037D\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u0523\u0531-\u0556\u0559\u0561-\u0587\u05D0-\u05EA\u05F0-\u05F2\u0621-\u064A\u066E-\u066F\u0671-\u06D3\u06D5\u06E5-\u06E6\u06EE-\u06EF\u06FA-\u06FC\u06FF\u0710\u0712-\u072F\u074D-\u07A5\u07B1\u07CA-\u07EA\u07F4-\u07F5\u07FA\u0904-\u0939\u093D\u0950\u0958-\u0961\u0971-\u0972\u097B-\u097F\u0985-\u098C\u098F-\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD\u09CE\u09DC-\u09DD\u09DF-\u09E1\u09F0-\u09F1\u0A05-\u0A0A\u0A0F-\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32-\u0A33\u0A35-\u0A36\u0A38-\u0A39\u0A59-\u0A5C\u0A5E\u0A72-\u0A74\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2-\u0AB3\u0AB5-\u0AB9\u0ABD\u0AD0\u0AE0-\u0AE1\u0B05-\u0B0C\u0B0F-\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32-\u0B33\u0B35-\u0B39\u0B3D\u0B5C-\u0B5D\u0B5F-\u0B61\u0B71\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99-\u0B9A\u0B9C\u0B9E-\u0B9F\u0BA3-\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BD0\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C33\u0C35-\u0C39\u0C3D\u0C58-\u0C59\u0C60-\u0C61\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD\u0CDE\u0CE0-\u0CE1\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D28\u0D2A-\u0D39\u0D3D\u0D60-\u0D61\u0D7A-\u0D7F\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0E01-\u0E3A\u0E40-\u0E4E\u0E81-\u0E82\u0E84\u0E87-\u0E88\u0E8A\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA-\u0EAB\u0EAD-\u0EB0\u0EB2-\u0EB3\u0EBD\u0EC0-\u0EC4\u0EC6\u0EDC-\u0EDD\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F88-\u0F8B\u1000-\u102A\u103F\u1050-\u1055\u105A-\u105D\u1061\u1065-\u1066\u106E-\u1070\u1075-\u1081\u108E\u10A0-\u10C5\u10D0-\u10FA\u10FC\u1100-\u1159\u115F-\u11A2\u11A8-\u11F9\u1200-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u1380-\u138F\u13A0-\u13F4\u1401-\u166C\u166F-\u1676\u1681-\u169A\u16A0-\u16EA\u16EE-\u16F0\u1700-\u170C\u170E-\u1711\u1720-\u1731\u1740-\u1751\u1760-\u176C\u176E-\u1770\u1780-\u17B3\u17D7\u17DC\u1820-\u1877\u1880-\u18A8\u18AA\u1900-\u191C\u1950-\u196D\u1970-\u1974\u1980-\u19A9\u19C1-\u19C7\u1A00-\u1A16\u1B05-\u1B33\u1B45-\u1B4B\u1B83-\u1BA0\u1BAE-\u1BAF\u1C00-\u1C23\u1C4D-\u1C4F\u1C5A-\u1C7D\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u200e\u2010\u2013-\u2016\u2018\u201C-\u201D\u2020-\u2021\u2025-\u2027\u2030\u2032-\u2033\u2035\u203B\u2071\u2074\u207F\u2081-\u2084\u2090-\u2094\u2102-\u2103\u2105\u2107\u2109-\u2113\u2115-\u2116\u2119-\u211D\u2121-\u2122\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2153-\u2154\u215B-\u215E\u2160-\u2188\u2190-\u2199\u21D2\u21D4\u2200\u2202-\u2203\u2207-\u2208\u220B\u220F\u2211\u2215\u221A\u221D-\u2220\u2223\u2225\u2227-\u222C\u222E\u2234-\u2237\u223C-\u223D\u2248\u224C\u2252\u2260-\u2261\u2264-\u2267\u226A-\u226B\u226E-\u226F\u2282-\u2283\u2286-\u2287\u2295\u2299\u22A5\u22BF\u2312\u2460-\u24B5\u24D0-\u24E9\u2500-\u254B\u2550-\u2574\u2581-\u258F\u2592-\u2595\u25A0-\u25A1\u25A3-\u25A9\u25B2-\u25B3\u25B6-\u25B7\u25BC-\u25BD\u25C0-\u25C1\u25C6-\u25C8\u25CB\u25CE-\u25D1\u25E2-\u25E5\u25EF\u2605-\u2606\u2609\u260E-\u260F\u261C\u261E\u2640\u2642\u2660-\u2661\u2663-\u2665\u2667-\u266A\u266C-\u266D\u266F\u2C00-\u2C2E\u2C30-\u2C5E\u2C60-\u2C6F\u2C71-\u2C7D\u2C80-\u2CE4\u2D00-\u2D25\u2D30-\u2D65\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u3000-\u3003\u3005-\u3017\u301D-\u301F\u3021-\u3029\u3031-\u3035\u3038-\u303C\u3041-\u3096\u309B-\u309F\u30A1-\u30FF\u3105-\u312D\u3131-\u318E\u31A0-\u31B7\u31F0-\u321C\u3220-\u3229\u3231-\u3232\u3239\u3260-\u327B\u327F\u32A3-\u32A8\u3303\u330D\u3314\u3318\u3322-\u3323\u3326-\u3327\u332B\u3336\u333B\u3349-\u334A\u334D\u3351\u3357\u337B-\u337E\u3380-\u3384\u3388-\u33CA\u33CD-\u33D3\u33D5-\u33D6\u33D8\u33DB-\u33DD\u3400-\u4DB5\u4E00-\u9FC3\uA000-\uA48C\uA500-\uA60C\uA610-\uA61F\uA62A-\uA62B\uA640-\uA65F\uA662-\uA66E\uA680-\uA697\uA722-\uA787\uA78B-\uA78C\uA7FB-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA822\uA840-\uA873\uA882-\uA8B3\uA90A-\uA925\uA930-\uA946\uAA00-\uAA28\uAA40-\uAA42\uAA44-\uAA4B\uAC00-\uD7A3\uE000-\uF848\uF900-\uFA2D\uFA30-\uFA6A\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D\uFB1F-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40-\uFB41\uFB43-\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE30-\uFE31\uFE33-\uFE44\uFE49-\uFE52\uFE54-\uFE57\uFE59-\uFE66\uFE68-\uFE6B\uFE70-\uFE74\uFE76-\uFEFC\uFF01-\uFF5E\uFF61-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC\uFFE0-\uFFE6",
    str_namedSheetsRange = "\u0001-\u0026\u0028-\u0029\u002B-\u002D\u003B-\u003E\u0040\u005E\u0060\u007B-\u007F\u0082\u0084\u008B\u0092\u0095\u0098\u009B\u00A0\u00A6\u00A9\u00AB-\u00AC\u00AE\u00BB\u0378-\u0379\u037E-\u0383\u0387\u038B\u038D\u03A2\u0524-\u0530\u0557-\u0558\u055A-\u0560\u0588-\u0590\u05BE\u05C0\u05C3\u05C6\u05C8-\u05CF\u05EB-\u05EF\u05F3-\u05FF\u0604-\u0605\u0609-\u060A\u060C-\u060D\u061B-\u061E\u0620\u065F\u066A-\u066D\u06D4\u0700-\u070E\u074B-\u074C\u07B2-\u07BF\u07F7-\u07F9\u07FB-\u0900\u093A-\u093B\u094E-\u094F\u0955-\u0957\u0964-\u0965\u0970\u0973-\u097A\u0980\u0984\u098D-\u098E\u0991-\u0992\u09A9\u09B1\u09B3-\u09B5\u09BA-\u09BB\u09C5-\u09C6\u09C9-\u09CA\u09CF-\u09D6\u09D8-\u09DB\u09DE\u09E4-\u09E5\u09FB-\u0A00\u0A04\u0A0B-\u0A0E\u0A11-\u0A12\u0A29\u0A31\u0A34\u0A37\u0A3A-\u0A3B\u0A3D\u0A43-\u0A46\u0A49-\u0A4A\u0A4E-\u0A50\u0A52-\u0A58\u0A5D\u0A5F-\u0A65\u0A76-\u0A80\u0A84\u0A8E\u0A92\u0AA9\u0AB1\u0AB4\u0ABA-\u0ABB\u0AC6\u0ACA\u0ACE-\u0ACF\u0AD1-\u0ADF\u0AE4-\u0AE5\u0AF0\u0AF2-\u0B00\u0B04\u0B0D-\u0B0E\u0B11-\u0B12\u0B29\u0B31\u0B34\u0B3A-\u0B3B\u0B45-\u0B46\u0B49-\u0B4A\u0B4E-\u0B55\u0B58-\u0B5B\u0B5E\u0B64-\u0B65\u0B72-\u0B81\u0B84\u0B8B-\u0B8D\u0B91\u0B96-\u0B98\u0B9B\u0B9D\u0BA0-\u0BA2\u0BA5-\u0BA7\u0BAB-\u0BAD\u0BBA-\u0BBD\u0BC3-\u0BC5\u0BC9\u0BCE-\u0BCF\u0BD1-\u0BD6\u0BD8-\u0BE5\u0BFB-\u0C00\u0C04\u0C0D\u0C11\u0C29\u0C34\u0C3A-\u0C3C\u0C45\u0C49\u0C4E-\u0C54\u0C57\u0C5A-\u0C5F\u0C64-\u0C65\u0C70-\u0C77\u0C80-\u0C81\u0C84\u0C8D\u0C91\u0CA9\u0CB4\u0CBA-\u0CBB\u0CC5\u0CC9\u0CCE-\u0CD4\u0CD7-\u0CDD\u0CDF\u0CE4-\u0CE5\u0CF0\u0CF3-\u0D01\u0D04\u0D0D\u0D11\u0D29\u0D3A-\u0D3C\u0D45\u0D49\u0D4E-\u0D56\u0D58-\u0D5F\u0D64-\u0D65\u0D76-\u0D78\u0D80-\u0D81\u0D84\u0D97-\u0D99\u0DB2\u0DBC\u0DBE-\u0DBF\u0DC7-\u0DC9\u0DCB-\u0DCE\u0DD5\u0DD7\u0DE0-\u0DF1\u0DF4-\u0E00\u0E3B-\u0E3E\u0E4F\u0E5A-\u0E80\u0E83\u0E85-\u0E86\u0E89\u0E8B-\u0E8C\u0E8E-\u0E93\u0E98\u0EA0\u0EA4\u0EA6\u0EA8-\u0EA9\u0EAC\u0EBA\u0EBE-\u0EBF\u0EC5\u0EC7\u0ECE-\u0ECF\u0EDA-\u0EDB\u0EDE-\u0EFF\u0F04-\u0F12\u0F3A-\u0F3D\u0F48\u0F6D-\u0F70\u0F85\u0F8C-\u0F8F\u0F98\u0FBD\u0FCD\u0FD0-\u0FFF\u104A-\u104F\u109A-\u109D\u10C6-\u10CF\u10FB\u10FD-\u10FF\u115A-\u115E\u11A3-\u11A7\u11FA-\u11FF\u1249\u124E-\u124F\u1257\u1259\u125E-\u125F\u1289\u128E-\u128F\u12B1\u12B6-\u12B7\u12BF\u12C1\u12C6-\u12C7\u12D7\u1311\u1316-\u1317\u135B-\u135E\u1361-\u1368\u137D-\u137F\u139A-\u139F\u13F5-\u1400\u166D-\u166E\u1677-\u167F\u169B-\u169F\u16EB-\u16ED\u16F1-\u16FF\u170D\u1715-\u171F\u1735-\u173F\u1754-\u175F\u176D\u1771\u1774-\u177F\u17D4-\u17D6\u17D8-\u17DA\u17DE-\u17DF\u17EA-\u17EF\u17FA-\u180A\u180F\u181A-\u181F\u1878-\u187F\u18AB-\u18FF\u191D-\u191F\u192C-\u192F\u193C-\u193F\u1941-\u1945\u196E-\u196F\u1975-\u197F\u19AA-\u19AF\u19CA-\u19CF\u19DA-\u19DF\u1A1C-\u1AFF\u1B4C-\u1B4F\u1B5A-\u1B60\u1B7D-\u1B7F\u1BAB-\u1BAD\u1BBA-\u1BFF\u1C38-\u1C3F\u1C4A-\u1C4C\u1C7E-\u1CFF\u1DE7-\u1DFD\u1F16-\u1F17\u1F1E-\u1F1F\u1F46-\u1F47\u1F4E-\u1F4F\u1F58\u1F5A\u1F5C\u1F5E\u1F7E-\u1F7F\u1FB5\u1FC5\u1FD4-\u1FD5\u1FDC\u1FF0-\u1FF1\u1FF5\u1FFF\u200e\u2011-\u2012\u2017\u2019-\u201B\u201E-\u201F\u2022-\u2024\u2031\u2034\u2036-\u203A\u203C-\u2043\u2045-\u2051\u2053-\u205E\u2065-\u2069\u2072-\u2073\u207D-\u207E\u208D-\u208F\u2095-\u209F\u20B6-\u20CF\u20F1-\u20FF\u2150-\u2152\u2189-\u218F\u2329-\u232A\u23E8-\u23FF\u2427-\u243F\u244B-\u245F\u269E-\u269F\u26BD-\u26BF\u26C4-\u2700\u2705\u270A-\u270B\u2728\u274C\u274E\u2753-\u2755\u2757\u275F-\u2760\u2768-\u2775\u2795-\u2797\u27B0\u27BF\u27C5-\u27C6\u27CB\u27CD-\u27CF\u27E6-\u27EF\u2983-\u2998\u29D8-\u29DB\u29FC-\u29FD\u2B4D-\u2B4F\u2B55-\u2BFF\u2C2F\u2C5F\u2C70\u2C7E-\u2C7F\u2CEB-\u2CFC\u2CFE-\u2CFF\u2D26-\u2D2F\u2D66-\u2D6E\u2D70-\u2D7F\u2D97-\u2D9F\u2DA7\u2DAF\u2DB7\u2DBF\u2DC7\u2DCF\u2DD7\u2DDF\u2E00-\u2E2E\u2E30-\u2E7F\u2E9A\u2EF4-\u2EFF\u2FD6-\u2FEF\u2FFC-\u2FFF\u3018-\u301C\u3030\u303D\u3040\u3097-\u3098\u30A0\u3100-\u3104\u312E-\u3130\u318F\u31B8-\u31BF\u31E4-\u31EF\u321F\u3244-\u324F\u32FF\u4DB6-\u4DBF\u9FC4-\u9FFF\uA48D-\uA48F\uA4C7-\uA4FF\uA60D-\uA60F\uA62C-\uA63F\uA660-\uA661\uA673-\uA67B\uA67E\uA698-\uA6FF\uA78D-\uA7FA\uA82C-\uA83F\uA874-\uA87F\uA8C5-\uA8CF\uA8DA-\uA8FF\uA92F\uA954-\uA9FF\uAA37-\uAA3F\uAA4E-\uAA4F\uAA5A-\uABFF\uD7A4-\uD7FF\uFA2E-\uFA2F\uFA6B-\uFA6F\uFADA-\uFAFF\uFB07-\uFB12\uFB18-\uFB1C\uFB37\uFB3D\uFB3F\uFB42\uFB45\uFBB2-\uFBD2\uFD3E-\uFD4F\uFD90-\uFD91\uFDC8-\uFDEF\uFDFE-\uFDFF\uFE10-\uFE1F\uFE27-\uFE2F\uFE32\uFE45-\uFE48\uFE53\uFE58\uFE67\uFE6C-\uFE6F\uFE75\uFEFD-\uFEFE\uFF00\uFF5F-\uFF60\uFFBF-\uFFC1\uFFC8-\uFFC9\uFFD0-\uFFD1\uFFD8-\uFFD9\uFFDD-\uFFDF\uFFE7\uFFEF-\uFFF8\uFFFE-\uFFFF",
    rx_operators = /^ *[-+*\/^&%<=>:] */,
    rg = new XRegExp( "^((?:_xlfn.)?[\\p{L}\\d.]+ *)[-+*/^&%<=>:;\\(\\)]" ),
    rgRange = /^(\$?[A-Za-z]+\$?\d+:\$?[A-Za-z]+\$?\d+)(?:[-+*\/^&%<=>: ;),]|$)/,
    rgCols = /^(\$?[A-Za-z]+:\$?[A-Za-z]+)(?:[-+*\/^&%<=>: ;),]|$)/,
    rgRows = /^(\$?\d+:\$?\d+)(?:[-+*\/^&%<=>: ;),]|$)/,
    rx_ref = /^ *(\$?[A-Za-z]{1,3}\$?(\d{1,7}))([-+*\/^&%<=>: ;),]|$)/,
    rx_refAll = /^(\$?[A-Za-z]+\$?(\d+))([-+*\/^&%<=>: ;),]|$)/,
    rx_ref3D_non_quoted = new XRegExp( "^(?<name_from>["+str_namedRanges+"]["+str_namedRanges+"\\d.]*)(:(?<name_to>["+str_namedRanges+"]["+str_namedRanges+"\\d.]*))?!","i" ),
    rx_ref3D_quoted = new XRegExp( "^'(?<name_from>(?:''|[^\\[\\]'\\/*?:])*)(?::(?<name_to>(?:''|[^\\[\\]'\\/*?:])*))?'!" ),
    rx_ref3D = new XRegExp( "^(?<name_from>[^:]+)(:(?<name_to>[^:]+))?!" ),
    rx_number = /^ *[+-]?\d*(\d|\.)\d*([eE][+-]?\d+)?/,
    rx_RightParentheses = /^ *\)/,
    rx_Comma = /^ *[,;] */,
    rx_arraySeparators = /^ *[,;] */,

    rx_error = build_rx_error(null ),
    rx_error_local = build_rx_error(null),

    rx_bool = build_rx_bool(null),
    rx_bool_local = build_rx_bool(null),
    rx_string = /^\"((\"\"|[^\"])*)\"/,
    rx_test_ws_name = new test_ws_name2(),
    rx_space_g = /\s/g,
    rx_space = /\s/,
	rx_intersect = /^ +/,
    rg_str_allLang = /[A-Za-z\xAA\xB5\xBA\xC0-\xD6\xD8-\xF6\xF8-\u02C1\u02C6-\u02D1\u02E0-\u02E4\u02EC\u02EE\u0345\u0370-\u0374\u0376\u0377\u037A-\u037D\u0386\u0388-\u038A\u038C\u038E-\u03A1\u03A3-\u03F5\u03F7-\u0481\u048A-\u0527\u0531-\u0556\u0559\u0561-\u0587\u05B0-\u05BD\u05BF\u05C1\u05C2\u05C4\u05C5\u05C7\u05D0-\u05EA\u05F0-\u05F2\u0610-\u061A\u0620-\u0657\u0659-\u065F\u066E-\u06D3\u06D5-\u06DC\u06E1-\u06E8\u06ED-\u06EF\u06FA-\u06FC\u06FF\u0710-\u073F\u074D-\u07B1\u07CA-\u07EA\u07F4\u07F5\u07FA\u0800-\u0817\u081A-\u082C\u0840-\u0858\u08A0\u08A2-\u08AC\u08E4-\u08E9\u08F0-\u08FE\u0900-\u093B\u093D-\u094C\u094E-\u0950\u0955-\u0963\u0971-\u0977\u0979-\u097F\u0981-\u0983\u0985-\u098C\u098F\u0990\u0993-\u09A8\u09AA-\u09B0\u09B2\u09B6-\u09B9\u09BD-\u09C4\u09C7\u09C8\u09CB\u09CC\u09CE\u09D7\u09DC\u09DD\u09DF-\u09E3\u09F0\u09F1\u0A01-\u0A03\u0A05-\u0A0A\u0A0F\u0A10\u0A13-\u0A28\u0A2A-\u0A30\u0A32\u0A33\u0A35\u0A36\u0A38\u0A39\u0A3E-\u0A42\u0A47\u0A48\u0A4B\u0A4C\u0A51\u0A59-\u0A5C\u0A5E\u0A70-\u0A75\u0A81-\u0A83\u0A85-\u0A8D\u0A8F-\u0A91\u0A93-\u0AA8\u0AAA-\u0AB0\u0AB2\u0AB3\u0AB5-\u0AB9\u0ABD-\u0AC5\u0AC7-\u0AC9\u0ACB\u0ACC\u0AD0\u0AE0-\u0AE3\u0B01-\u0B03\u0B05-\u0B0C\u0B0F\u0B10\u0B13-\u0B28\u0B2A-\u0B30\u0B32\u0B33\u0B35-\u0B39\u0B3D-\u0B44\u0B47\u0B48\u0B4B\u0B4C\u0B56\u0B57\u0B5C\u0B5D\u0B5F-\u0B63\u0B71\u0B82\u0B83\u0B85-\u0B8A\u0B8E-\u0B90\u0B92-\u0B95\u0B99\u0B9A\u0B9C\u0B9E\u0B9F\u0BA3\u0BA4\u0BA8-\u0BAA\u0BAE-\u0BB9\u0BBE-\u0BC2\u0BC6-\u0BC8\u0BCA-\u0BCC\u0BD0\u0BD7\u0C01-\u0C03\u0C05-\u0C0C\u0C0E-\u0C10\u0C12-\u0C28\u0C2A-\u0C33\u0C35-\u0C39\u0C3D-\u0C44\u0C46-\u0C48\u0C4A-\u0C4C\u0C55\u0C56\u0C58\u0C59\u0C60-\u0C63\u0C82\u0C83\u0C85-\u0C8C\u0C8E-\u0C90\u0C92-\u0CA8\u0CAA-\u0CB3\u0CB5-\u0CB9\u0CBD-\u0CC4\u0CC6-\u0CC8\u0CCA-\u0CCC\u0CD5\u0CD6\u0CDE\u0CE0-\u0CE3\u0CF1\u0CF2\u0D02\u0D03\u0D05-\u0D0C\u0D0E-\u0D10\u0D12-\u0D3A\u0D3D-\u0D44\u0D46-\u0D48\u0D4A-\u0D4C\u0D4E\u0D57\u0D60-\u0D63\u0D7A-\u0D7F\u0D82\u0D83\u0D85-\u0D96\u0D9A-\u0DB1\u0DB3-\u0DBB\u0DBD\u0DC0-\u0DC6\u0DCF-\u0DD4\u0DD6\u0DD8-\u0DDF\u0DF2\u0DF3\u0E01-\u0E3A\u0E40-\u0E46\u0E4D\u0E81\u0E82\u0E84\u0E87\u0E88\u0E8A\u0E8D\u0E94-\u0E97\u0E99-\u0E9F\u0EA1-\u0EA3\u0EA5\u0EA7\u0EAA\u0EAB\u0EAD-\u0EB9\u0EBB-\u0EBD\u0EC0-\u0EC4\u0EC6\u0ECD\u0EDC-\u0EDF\u0F00\u0F40-\u0F47\u0F49-\u0F6C\u0F71-\u0F81\u0F88-\u0F97\u0F99-\u0FBC\u1000-\u1036\u1038\u103B-\u103F\u1050-\u1062\u1065-\u1068\u106E-\u1086\u108E\u109C\u109D\u10A0-\u10C5\u10C7\u10CD\u10D0-\u10FA\u10FC-\u1248\u124A-\u124D\u1250-\u1256\u1258\u125A-\u125D\u1260-\u1288\u128A-\u128D\u1290-\u12B0\u12B2-\u12B5\u12B8-\u12BE\u12C0\u12C2-\u12C5\u12C8-\u12D6\u12D8-\u1310\u1312-\u1315\u1318-\u135A\u135F\u1380-\u138F\u13A0-\u13F4\u1401-\u166C\u166F-\u167F\u1681-\u169A\u16A0-\u16EA\u16EE-\u16F0\u1700-\u170C\u170E-\u1713\u1720-\u1733\u1740-\u1753\u1760-\u176C\u176E-\u1770\u1772\u1773\u1780-\u17B3\u17B6-\u17C8\u17D7\u17DC\u1820-\u1877\u1880-\u18AA\u18B0-\u18F5\u1900-\u191C\u1920-\u192B\u1930-\u1938\u1950-\u196D\u1970-\u1974\u1980-\u19AB\u19B0-\u19C9\u1A00-\u1A1B\u1A20-\u1A5E\u1A61-\u1A74\u1AA7\u1B00-\u1B33\u1B35-\u1B43\u1B45-\u1B4B\u1B80-\u1BA9\u1BAC-\u1BAF\u1BBA-\u1BE5\u1BE7-\u1BF1\u1C00-\u1C35\u1C4D-\u1C4F\u1C5A-\u1C7D\u1CE9-\u1CEC\u1CEE-\u1CF3\u1CF5\u1CF6\u1D00-\u1DBF\u1E00-\u1F15\u1F18-\u1F1D\u1F20-\u1F45\u1F48-\u1F4D\u1F50-\u1F57\u1F59\u1F5B\u1F5D\u1F5F-\u1F7D\u1F80-\u1FB4\u1FB6-\u1FBC\u1FBE\u1FC2-\u1FC4\u1FC6-\u1FCC\u1FD0-\u1FD3\u1FD6-\u1FDB\u1FE0-\u1FEC\u1FF2-\u1FF4\u1FF6-\u1FFC\u2071\u207F\u2090-\u209C\u2102\u2107\u210A-\u2113\u2115\u2119-\u211D\u2124\u2126\u2128\u212A-\u212D\u212F-\u2139\u213C-\u213F\u2145-\u2149\u214E\u2160-\u2188\u24B6-\u24E9\u2C00-\u2C2E\u2C30-\u2C5E\u2C60-\u2CE4\u2CEB-\u2CEE\u2CF2\u2CF3\u2D00-\u2D25\u2D27\u2D2D\u2D30-\u2D67\u2D6F\u2D80-\u2D96\u2DA0-\u2DA6\u2DA8-\u2DAE\u2DB0-\u2DB6\u2DB8-\u2DBE\u2DC0-\u2DC6\u2DC8-\u2DCE\u2DD0-\u2DD6\u2DD8-\u2DDE\u2DE0-\u2DFF\u2E2F\u3005-\u3007\u3021-\u3029\u3031-\u3035\u3038-\u303C\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF\u3105-\u312D\u3131-\u318E\u31A0-\u31BA\u31F0-\u31FF\u3400-\u4DB5\u4E00-\u9FCC\uA000-\uA48C\uA4D0-\uA4FD\uA500-\uA60C\uA610-\uA61F\uA62A\uA62B\uA640-\uA66E\uA674-\uA67B\uA67F-\uA697\uA69F-\uA6EF\uA717-\uA71F\uA722-\uA788\uA78B-\uA78E\uA790-\uA793\uA7A0-\uA7AA\uA7F8-\uA801\uA803-\uA805\uA807-\uA80A\uA80C-\uA827\uA840-\uA873\uA880-\uA8C3\uA8F2-\uA8F7\uA8FB\uA90A-\uA92A\uA930-\uA952\uA960-\uA97C\uA980-\uA9B2\uA9B4-\uA9BF\uA9CF\uAA00-\uAA36\uAA40-\uAA4D\uAA60-\uAA76\uAA7A\uAA80-\uAABE\uAAC0\uAAC2\uAADB-\uAADD\uAAE0-\uAAEF\uAAF2-\uAAF5\uAB01-\uAB06\uAB09-\uAB0E\uAB11-\uAB16\uAB20-\uAB26\uAB28-\uAB2E\uABC0-\uABEA\uAC00-\uD7A3\uD7B0-\uD7C6\uD7CB-\uD7FB\uF900-\uFA6D\uFA70-\uFAD9\uFB00-\uFB06\uFB13-\uFB17\uFB1D-\uFB28\uFB2A-\uFB36\uFB38-\uFB3C\uFB3E\uFB40\uFB41\uFB43\uFB44\uFB46-\uFBB1\uFBD3-\uFD3D\uFD50-\uFD8F\uFD92-\uFDC7\uFDF0-\uFDFB\uFE70-\uFE74\uFE76-\uFEFC\uFF21-\uFF3A\uFF41-\uFF5A\uFF66-\uFFBE\uFFC2-\uFFC7\uFFCA-\uFFCF\uFFD2-\uFFD7\uFFDA-\uFFDC]/,
    rx_name = new XRegExp( "^(?<name>" + "[" + str_namedRanges + "][" + str_namedRanges + "\\d.]*)([-+*\\/^&%<=>: ;),]|$)" ),
    rx_defName = new test_defName(),
    rx_arraySeparatorsDef = /^ *[,;] */,
    rx_numberDef = /^ *[+-]?\d*(\d|\.)\d*([eE][+-]?\d+)?/,
    rx_CommaDef = /^ *[,;] */,

	rx_array_local = /^\{(([+-]?\d*(\d|\.)\d*([eE][+-]?\d+)?)?(\"((\"\"|[^\"])*)\")?(#NULL!|#DIV\/0!|#VALUE!|#REF!|#NAME\?|#NUM!|#UNSUPPORTED_FUNCTION!|#N\/A|#GETTING_DATA|FALSE|TRUE)?[,;]?)*\}/i,
    rx_array =       /^\{(([+-]?\d*(\d|\.)\d*([eE][+-]?\d+)?)?(\"((\"\"|[^\"])*)\")?(#NULL!|#DIV\/0!|#VALUE!|#REF!|#NAME\?|#NUM!|#UNSUPPORTED_FUNCTION!|#N\/A|#GETTING_DATA|FALSE|TRUE)?[,;]?)*\}/i,

	rx_ControlSymbols = /^ *[\u0000-\u001F\u007F-\u009F] */,

    emailRe = /^(mailto:)?([a-z0-9'\._-]+@[a-z0-9\.-]+\.[a-z0-9]{2,4})([a-яё0-9\._%+-=\? :&]*)/i,
    ipRe = /^(((https?)|(ftps?)):\/\/)?([\-\wа-яё]*:?[\-\wа-яё]*@)?(((1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9])\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))(:\d+)?(\/[%\-\wа-яё]*(\.[\wа-яё]{2,})?(([\wа-яё\-\.\?\\\/+@&#;:`~=%!,\(\)]*)(\.[\wа-яё]{2,})?)*)*\/?/i,
    hostnameRe = /^(((https?)|(ftps?)):\/\/)?([\-\wа-яё]*:?[\-\wа-яё]*@)?(([\-\wа-яё]+\.)+[\wа-яё\-]{2,}(:\d+)?(\/[%\-\wа-яё]*(\.[\wа-яё]{2,})?(([\wа-яё\-\.\?\\\/+@&#;:`~=%!,\(\)]*)(\.[\wа-яё]{2,})?)*)*\/?)/i,
    localRe = /^(((https?)|(ftps?)):\/\/)([\-\wа-яё]*:?[\-\wа-яё]*@)?(([\-\wа-яё]+)(:\d+)?(\/[%\-\wа-яё]*(\.[\wа-яё]{2,})?(([\wа-яё\-\.\?\\\/+@&#;:`~=%!,\(\)]*)(\.[\wа-яё]{2,})?)*)*\/?)/i,

	rx_table = build_rx_table(null),
	rx_table_local = build_rx_table(null);

function getUrlType(url) {
  var checkvalue = url.replace(new RegExp(' ', 'g'), '%20');
  var isEmail;
  var isvalid = checkvalue.strongMatch(hostnameRe);
  !isvalid && (isvalid = checkvalue.strongMatch(ipRe));
  !isvalid && (isvalid = checkvalue.strongMatch(localRe));
  isEmail = checkvalue.strongMatch(emailRe);
  !isvalid && (isvalid = isEmail);

  return isvalid ? (isEmail ? AscCommon.c_oAscUrlType.Email : AscCommon.c_oAscUrlType.Http) : AscCommon.c_oAscUrlType.Invalid;
}
function prepareUrl(url, type) {
  if (!/(((^https?)|(^ftp)):\/\/)|(^mailto:)/i.test(url)) {
    url = ( (AscCommon.c_oAscUrlType.Email == type) ? 'mailto:' : 'http://' ) + url;
  }

  return url.replace(new RegExp("%20", 'g'), " ");
}

/**
 * вспомогательный объект для парсинга формул и проверки строки по регуляркам указанным выше.
 * @constructor
 */
function parserHelper() {
	this.operand_str = null;
	this.pCurrPos = null;
}
parserHelper.prototype._reset = function () {
	this.operand_str = null;
	this.pCurrPos = null;
};
parserHelper.prototype.isControlSymbols = function ( formula, start_pos, digitDelim ) {
    if ( this instanceof parserHelper ) {
        this._reset();
    }

    var match = (formula.substring( start_pos )).match( rx_ControlSymbols );
    if (match != null) {
        this.operand_str = match[0];
        this.pCurrPos += match[0].length;
        return true;
    }
    return false;
};
parserHelper.prototype.isOperator = function(formula, start_pos) {
  // ToDo нужно ли это?
  if (this instanceof parserHelper) {
    this._reset();
  }

  var code, find = false, length = formula.length;
  while (start_pos !== length) {
    code = formula.charCodeAt(start_pos);
    if (-1 !== g_arrCodeOperators.indexOf(code)) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      find = true;
      break;
    } else if (g_oStartCodeOperatorsCompare <= code && code <= g_oEndCodeOperatorsCompare) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      while (start_pos !== length) {
        code = formula.charCodeAt(start_pos);
        if (g_oStartCodeOperatorsCompare > code || code > g_oEndCodeOperatorsCompare) {
          break;
        }
        this.operand_str += formula[start_pos];
        ++start_pos;
      }
      find = true;
      break;
    } else if (code === g_oCodeSpace) {
      ++start_pos;
    } else {
      break;
    }
  }
  if (find) {
    while (start_pos !== length) {
      code = formula.charCodeAt(start_pos);
      if (code !== g_oCodeSpace) {
        break;
      }
      ++start_pos;
    }
    this.pCurrPos = start_pos;
    return true;
  }
  return false;
};
parserHelper.prototype.isFunc = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var frml = formula.substring( start_pos );
	var match = (frml).match( rg );

	if (match != null) {
		if ( match.length == 2 ) {
			this.pCurrPos += match[1].length;
			this.operand_str = match[1];
			return true;
		}
	}
	return false;
};
parserHelper.prototype.isArea = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var subSTR = formula.substring( start_pos );
	var match = subSTR.match( rgRange ) || subSTR.match( rgCols ) || subSTR.match( rgRows );
	if (match != null) {
        var m0 = match[1].split(":");
        if( g_oCellAddressUtils.getCellAddress(m0[0]).isValid() && g_oCellAddressUtils.getCellAddress(m0[1]).isValid() ){
            this.pCurrPos += match[1].length;
            this.operand_str = match[1];
            return true;
        }
	}
	return false;
};
parserHelper.prototype.isRef = function ( formula, start_pos, allRef ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}
	var substr = formula.substring( start_pos );
	var match = substr.match( rx_ref );
	if (match != null) {
		var m0 = match[0], m1 = match[1], m2 = match[2];
		if (  g_oCellAddressUtils.getCellAddress(m1).isValid() /*match.length >= 3 && g_oCellAddressUtils.colstrToColnum( m1.substr( 0, (m1.length - m2.length) ) ) <= gc_nMaxCol && parseInt( m2 ) <= gc_nMaxRow*/ ) {
			this.pCurrPos += m0.indexOf( " " ) > -1 ? m0.length - 1 : m1.length;
			this.operand_str = m1;
			return true;
		} else if ( allRef ) {
			match = substr.match( rx_refAll );
			if ( (match != null || match != undefined) && match.length >= 3 ) {
				var m1 = match[1];
				this.pCurrPos += m1.length;
				this.operand_str = m1;
				return true;
			}
		}
	}

	return false;
};
parserHelper.prototype.is3DRef = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

    var subSTR = formula.substring( start_pos ),
        match = XRegExp.exec( subSTR, rx_ref3D_quoted ) || XRegExp.exec( subSTR, rx_ref3D_non_quoted );

	if (match != null) {
		this.pCurrPos += match[0].length;
		this.operand_str = match[1];
		return [ true, match["name_from"] ? match["name_from"].replace( /''/g, "'" ) : null, match["name_to"] ? match["name_to"].replace( /''/g, "'" ) : null ];
	}
	return [false, null, null];
};
parserHelper.prototype.isNextPtg = function(formula, start_pos, digitDelim) {
  if (this instanceof parserHelper) {
    this._reset();
  }

  var subSTR = formula.substring(start_pos), match;
  if (subSTR.match(rx_RightParentheses) == null && subSTR.match(digitDelim ? rx_Comma : rx_CommaDef) == null &&
    subSTR.match(rx_operators) == null && (match = subSTR.match(rx_intersect)) != null) {
    this.pCurrPos += match[0].length;
    this.operand_str = match[0][0];
    return true;
  }
  return false;
};
parserHelper.prototype.isNumber = function ( formula, start_pos, digitDelim ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( digitDelim?rx_number:rx_numberDef );
	if (match != null) {
		this.operand_str = match[0].replace(FormulaSeparators.digitSeparator,FormulaSeparators.digitSeparatorDef);
		this.pCurrPos += match[0].length;

		return true;
	}
	return false;
};
parserHelper.prototype.isLeftParentheses = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

  var code, find = false, length = formula.length;
  while (start_pos !== length) {
    code = formula.charCodeAt(start_pos);
    if (code === g_oCodeLeftParentheses) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      find = true;
      break;
    } else if (code === g_oCodeSpace) {
      ++start_pos;
    } else {
      break;
    }
  }

  if (find) {
    while (start_pos !== length) {
      code = formula.charCodeAt(start_pos);
      if (code !== g_oCodeSpace) {
        break;
      }
      ++start_pos;
    }
    this.pCurrPos = start_pos;
    return true;
  }
  return false;
};
parserHelper.prototype.isRightParentheses = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

  var code, find = false, length = formula.length;
  while (start_pos !== length) {
    code = formula.charCodeAt(start_pos);
    if (code === g_oCodeRightParentheses) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      find = true;
      break;
    } else if (code === g_oCodeSpace) {
      ++start_pos;
    } else {
      break;
    }
  }

  if (find) {
    while (start_pos !== length) {
      code = formula.charCodeAt(start_pos);
      if (code !== g_oCodeSpace) {
        break;
      }
      ++start_pos;
    }
    this.pCurrPos = start_pos;
    return true;
  }
};
parserHelper.prototype.isComma = function ( formula, start_pos, digitDelim ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( digitDelim?rx_Comma:rx_CommaDef );
	if (match != null) {
		this.operand_str = match[0];
		this.pCurrPos += match[0].length;

		return true;
	}
	return false;
};
parserHelper.prototype.isArraySeparator = function ( formula, start_pos, digitDelim ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( digitDelim?rx_arraySeparators:rx_arraySeparatorsDef );
	if (match != null) {
		this.operand_str = match[0];
		this.pCurrPos += match[0].length;

		return true;
	}
	return false;
};
parserHelper.prototype.isError = function ( formula, start_pos, local ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( local?rx_error_local:rx_error );
	if (match != null) {
		this.operand_str = match[0];
		this.pCurrPos += match[0].length;
		return true;
	}
	return false;
};
parserHelper.prototype.isBoolean = function ( formula, start_pos, local ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( local?rx_bool_local:rx_bool );
	if (match != null) {
		this.operand_str = match[1];
		this.pCurrPos += match[1].length;
		return true;
	}
	return false;
};
parserHelper.prototype.isString = function ( formula, start_pos ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( rx_string );
	if (match != null) {
		this.operand_str = match[1].replace( "\"\"", "\"" );
		this.pCurrPos += match[0].length;
		return true;
	}
	return false;
};
parserHelper.prototype.isName = function ( formula, start_pos, wb, ws ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

    var subSTR = formula.substring( start_pos ),
        match = XRegExp.exec( subSTR, rx_name );

	if (match != null) {
		var name = match["name"];
		if ( name && name.length != 0 && name != cBoolLocal["t"] && name != cBoolLocal["f"]/*&& wb.DefinedNames && wb.isDefinedNamesExists( name, ws ? ws.getId() : null )*/ ) {
			this.pCurrPos += name.length;
			this.operand_str = name;
			return [ true, name ];
		}
		this.operand_str = name;
	}
	return [false];
};
parserHelper.prototype.isArray = function ( formula, start_pos, digitDelim ) {
	if ( this instanceof parserHelper ) {
		this._reset();
	}

	var match = (formula.substring( start_pos )).match( digitDelim?rx_array_local:rx_array );

	if (match != null) {
		this.operand_str = match[0].substring( 1, match[0].length - 1 );
		this.pCurrPos += match[0].length;
		return true;
	}

	return false;
};
parserHelper.prototype.isLeftBrace = function ( formula, start_pos ) {
  if ( this instanceof parserHelper ) {
    this._reset();
  }

  var code, find = false, length = formula.length;
  while (start_pos !== length) {
    code = formula.charCodeAt(start_pos);
    if (code === g_oCodeLeftBrace) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      find = true;
      break;
    } else if (code === g_oCodeSpace) {
      ++start_pos;
    } else {
      break;
    }
  }

  if (find) {
    while (start_pos !== length) {
      code = formula.charCodeAt(start_pos);
      if (code !== g_oCodeSpace) {
        break;
      }
      ++start_pos;
    }
    this.pCurrPos = start_pos;
    return true;
  }
};
parserHelper.prototype.isRightBrace = function ( formula, start_pos ) {
  if ( this instanceof parserHelper ) {
    this._reset();
  }

  var code, find = false, length = formula.length;
  while (start_pos !== length) {
    code = formula.charCodeAt(start_pos);
    if (code === g_oCodeRightBrace) {
      this.operand_str = formula[start_pos];
      ++start_pos;
      find = true;
      break;
    } else if (code === g_oCodeSpace) {
      ++start_pos;
    } else {
      break;
    }
  }

  if (find) {
    while (start_pos !== length) {
      code = formula.charCodeAt(start_pos);
      if (code !== g_oCodeSpace) {
        break;
      }
      ++start_pos;
    }
    this.pCurrPos = start_pos;
    return true;
  }
};
parserHelper.prototype.isTable = function ( formula, start_pos, local ){
    if ( this instanceof parserHelper ) {
        this._reset();
    }

    var subSTR = formula.substring( start_pos ),
        match = XRegExp.exec( subSTR, local?rx_table_local:rx_table );

    if ( match != null && match["tableName"] ) {
        this.operand_str = match[0];
        this.pCurrPos += match[0].length;
        return match;
    }

    return false;
};
// Парсим ссылку на диапазон в листе
parserHelper.prototype.parse3DRef = function ( formula ) {
	// Сначала получаем лист
	var is3DRefResult = this.is3DRef( formula, 0 );
	if ( is3DRefResult && true === is3DRefResult[0] ) {
		// Имя листа в ссылке
		var sheetName = is3DRefResult[1];
		// Ищем начало range
		var indexStartRange = formula.indexOf( "!" ) + 1;
		if ( this.isArea( formula, indexStartRange ) ) {
			if ( this.operand_str.length == formula.substring( indexStartRange ).length )
				return {sheet:sheetName, range:this.operand_str};
			else
				return null;
		} else if ( this.isRef( formula, indexStartRange ) ) {
			if ( this.operand_str.length == formula.substring( indexStartRange ).length )
				return {sheet:sheetName, range:this.operand_str};
			else
				return null;
		}
	}
	// Возвращаем ошибку
	return null;
};
// Возвращает ссылку на диапазон с листом (название листа экранируется)
parserHelper.prototype.get3DRef = function (sheet, range) {
	sheet = sheet.split(":");
	var wsFrom = sheet[0],
		wsTo = sheet[1] === undefined ? wsFrom : sheet[1];
	if ( rx_test_ws_name.test( wsFrom ) && rx_test_ws_name.test( wsTo ) ) {
		return (wsFrom !== wsTo ? wsFrom + ":" + wsTo : wsFrom) + "!" + range;
	} else {
		wsFrom = wsFrom.replace( /'/g, "''" );
		wsTo = wsTo.replace( /'/g, "''" );
		return "'" + (wsFrom !== wsTo ? wsFrom + ":" + wsTo : wsFrom) + "'!" + range;
	}
};
// Возвращает экранируемое название листа
parserHelper.prototype.getEscapeSheetName = function (sheet) {
	return rx_test_ws_name.test(sheet) ? sheet : "'" + sheet.replace(/'/g, "''") + "'";
};
/**
 * Проверяем ссылку на валидность для диаграммы или автофильтра
 * @param {AscCommonExcel.Workbook} model
 * @param {AscCommonExcel.WorkbookView} wb
 * @param {Asc.c_oAscSelectionDialogType} dialogType
 * @param {string} dataRange
 * @param {boolean} fullCheck
 * @param {boolean} isRows
 * @param {Asc.c_oAscChartTypeSettings} chartType
 * @returns {*}
 */
parserHelper.prototype.checkDataRange = function (model, wb, dialogType, dataRange, fullCheck, isRows, chartType) {
    var sDataRange = dataRange, sheetModel;
	if (Asc.c_oAscSelectionDialogType.Chart === dialogType) {
		dataRange = parserHelp.parse3DRef(dataRange);
        if(dataRange)
        {
            sheetModel =  model.getWorksheetByName(dataRange.sheet);
        }
		if (null === dataRange || !sheetModel)
			return Asc.c_oAscError.ID.DataRangeError;
		dataRange = AscCommonExcel.g_oRangeCache.getAscRange(dataRange.range);
	} else
		dataRange = AscCommonExcel.g_oRangeCache.getAscRange(dataRange);

	if (null === dataRange)
		return Asc.c_oAscError.ID.DataRangeError;

	if (fullCheck) {
		if (Asc.c_oAscSelectionDialogType.Chart === dialogType) {
			// Проверка максимального дипазона
			var maxSeries = 255;
			var minStockVal = 4;

			var intervalValues, intervalSeries;
			if (isRows) {
				intervalSeries = dataRange.r2 - dataRange.r1 + 1;
				intervalValues = dataRange.c2 - dataRange.c1 + 1;
			} else {
				intervalSeries = dataRange.c2 - dataRange.c1 + 1;
				intervalValues = dataRange.r2 - dataRange.r1 + 1;
			}

			if (Asc.c_oAscChartTypeSettings.stock === chartType) {
                var chartSettings = new AscCommon.asc_ChartSettings();
                chartSettings.putType(Asc.c_oAscChartTypeSettings.stock);
                chartSettings.putRange(sDataRange);
                chartSettings.putInColumns(!isRows);
                var chartSeries = AscFormat.getChartSeries (sheetModel, chartSettings).series;
				if (minStockVal !== chartSeries.length || !chartSeries[0].Val || !chartSeries[0].Val.NumCache || chartSeries[0].Val.NumCache.length < minStockVal)
					return Asc.c_oAscError.ID.StockChartError;
			} else if (intervalSeries > maxSeries)
				return Asc.c_oAscError.ID.MaxDataSeriesError;
		} else if (Asc.c_oAscSelectionDialogType.FormatTable === dialogType) {
			// ToDo убрать эту проверку, заменить на более грамотную после правки функции _searchFilters
			if (true === wb.getWorksheet().model.autoFilters.isRangeIntersectionTableOrFilter(dataRange))
				return  Asc.c_oAscError.ID.AutoFilterDataRangeError;
		} else if (Asc.c_oAscSelectionDialogType.FormatTableChangeRange === dialogType) {
			// ToDo убрать эту проверку, заменить на более грамотную после правки функции _searchFilters
			var checkChangeRange = wb.getWorksheet().af_checkChangeRange(dataRange);
			if (null !== checkChangeRange)
				return checkChangeRange;
		}
	}
	return Asc.c_oAscError.ID.No;
};
parserHelper.prototype.setDigitSeparator = function( sep ){
    if( sep != FormulaSeparators.digitSeparatorDef ){
      FormulaSeparators.digitSeparator = sep;
      FormulaSeparators.arrayRowSeparator = ";";
      FormulaSeparators.arrayColSeparator = "\\";
      FormulaSeparators.functionArgumentSeparator = ";";
        rx_number = new RegExp("^ *[+-]?\\d*(\\d|\\"+ FormulaSeparators.digitSeparator +")\\d*([eE][+-]?\\d+)?");
        rx_Comma = new RegExp("^ *["+FormulaSeparators.functionArgumentSeparator+"] *");
//		build_rx_array_local( cBoolLocal, digitSeparator, null);
        rx_arraySeparators = new RegExp("^ *["+FormulaSeparators.arrayRowSeparator+"\\"+FormulaSeparators.arrayColSeparator+"] *");
    }
    else{
      FormulaSeparators.arrayRowSeparator = FormulaSeparators.arrayRowSeparatorDef;
      FormulaSeparators.arrayColSeparator = FormulaSeparators.arrayColSeparatorDef;
      FormulaSeparators.digitSeparator = FormulaSeparators.digitSeparatorDef;
      FormulaSeparators.functionArgumentSeparator = FormulaSeparators.functionArgumentSeparatorDef;
        rx_number = new RegExp("^ *[+-]?\\d*(\\d|\\"+ FormulaSeparators.digitSeparatorDef +")\\d*([eE][+-]?\\d+)?");
        rx_Comma = new RegExp("^ *["+FormulaSeparators.functionArgumentSeparatorDef+"] *");
//		build_rx_array_local( cBoolLocal, digitSeparatorDef, null);
        rx_arraySeparators = new RegExp("^ *["+FormulaSeparators.arrayRowSeparatorDef+"\\"+FormulaSeparators.arrayColSeparatorDef+"] *");
    }
};
  parserHelper.prototype.getColumnTypeByName = function(value) {
    var res;
    switch (value.toLowerCase()) {
      case "#" + cStrucTableLocalColumns['a'].toLocaleLowerCase():
      case cStrucTableReservedWords.all.toLocaleLowerCase():
        res = FormulaTablePartInfo.all;
        break;
      case "#" + cStrucTableLocalColumns['d'].toLocaleLowerCase():
      case cStrucTableReservedWords.data.toLocaleLowerCase():
        res = FormulaTablePartInfo.data;
        break;
      case "#" + cStrucTableLocalColumns['h'].toLocaleLowerCase():
      case cStrucTableReservedWords.headers.toLocaleLowerCase():
        res = FormulaTablePartInfo.headers;
        break;
      case "#" + cStrucTableLocalColumns['t'].toLocaleLowerCase():
      case cStrucTableReservedWords.totals.toLocaleLowerCase():
        res = FormulaTablePartInfo.totals;
        break;
      case "#" + cStrucTableLocalColumns['tr'].toLocaleLowerCase():
      case cStrucTableReservedWords.at.toLocaleLowerCase():
      case cStrucTableReservedWords.thisrow.toLocaleLowerCase():
        res = FormulaTablePartInfo.thisRow;
        break;
      default:
        res = FormulaTablePartInfo.data;
        break;
    }
    return res;
  };
  parserHelper.prototype.getColumnNameByType = function(value, local) {
    switch (value) {
      case FormulaTablePartInfo.all:
      {
        if (local) {
          return "#" + cStrucTableLocalColumns['a'];
        }
        return cStrucTableReservedWords.all;
      }
      case FormulaTablePartInfo.data:
      {
        if (local) {
          return "#" + cStrucTableLocalColumns['d'];
        }
        return cStrucTableReservedWords.data;
      }
      case FormulaTablePartInfo.headers:
      {
        if (local) {
          return "#" + cStrucTableLocalColumns['h'];
        }
        return cStrucTableReservedWords.headers;
      }
      case FormulaTablePartInfo.totals:
      {
        if (local) {
          return "#" + cStrucTableLocalColumns['t'];
        }
        return cStrucTableReservedWords.totals;
      }
      case FormulaTablePartInfo.thisRow:
      {
        if (local) {
          return "#" + cStrucTableLocalColumns['tr'];
        }
        return cStrucTableReservedWords.thisrow;
      }
    }
    return null;
  };

var parserHelp = new parserHelper();

var kCurFormatPainterWord = '';
if (AscBrowser.isIE)
// Пути указаны относительно html в меню, не надо их исправлять
// и коммитить на пути относительно тестового меню
	kCurFormatPainterWord = 'url(../../../sdk/Common/Images/text_copy.cur), pointer';
else if (AscBrowser.isOpera)
	kCurFormatPainterWord = 'pointer';
else
	kCurFormatPainterWord = "url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABIAAAATCAYAAACdkl3yAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAJxJREFUeNrslGEOwBAMhVtxM5yauxnColWJzt+9pFkl9vWlBeac4VINYG4h3vueFUeKIHLOjRTsp+pdKaX6QY2jufripobpzRoB0ro6qdW5I+q3qGxowXONI9LACcBBBMYhA/RuFJxA+WnXK1CBJJg0kKMD2cc8hNKe25P9gxSy01VY3pjdhHYgCCG0RYyR5Bphpk8kMofHjh4BBgA9UXIXw7elTAAAAABJRU5ErkJggg==') 2 11, pointer";

  function extendClass (Child, Parent) {
    var F = function() { };
    F.prototype = Parent.prototype;
    Child.prototype = new F();
    Child.prototype.constructor = Child;
    Child.superclass = Parent.prototype;
  }

function asc_ajax (obj) {
	var url = "", type = "GET",
		async = true, data = null, dataType = "text/xml",
		error = null, success = null, httpRequest = null,
		contentType = "application/x-www-form-urlencoded",

		init = function (obj){
			if ( typeof obj.url !== 'undefined' ){
				url = obj.url;
			}
			if ( typeof obj.type !== 'undefined' ){
				type = obj.type;
			}
			if ( typeof obj.async !== 'undefined' ){
				async = obj.async;
			}
			if ( typeof obj.data !== 'undefined' ){
				data = obj.data;
			}
			if ( typeof obj.dataType !== 'undefined' ){
				dataType = obj.dataType;
			}
			if ( typeof obj.error !== 'undefined' ){
				error = obj.error;
			}
			if ( typeof obj.success !== 'undefined' ){
				success = obj.success;
			}
			if ( typeof (obj.contentType) !== 'undefined' ){
				contentType = obj.contentType;
			}

			if (window.XMLHttpRequest) { // Mozilla, Safari, ...
				httpRequest = new XMLHttpRequest();
				if (httpRequest.overrideMimeType) {
					httpRequest.overrideMimeType(dataType);
				}
			}
			else if (window.ActiveXObject) { // IE
				try {
					httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
				}
				catch (e) {
					try {
						httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
					}
					catch (e) {}
				}
			}

			httpRequest.onreadystatechange = function(){
				respons(this);
			};
			send();
		},

		send = function(){
			httpRequest.open(type, url, async);
			if (type === "POST")
				httpRequest.setRequestHeader("Content-Type", contentType);
			httpRequest.send(data);
		},

		respons = function(httpRequest){
			switch (httpRequest.readyState)
			{
				case 0:
					// The object has been created, but not initialized (the open method has not been called).
					break;
				case 1:
					// A request has been opened, but the send method has not been called.
					break;
				case 2:
					// The send method has been called. No data is available yet.
					break;
				case 3:
					// Some data has been received; however, neither responseText nor responseBody is available.
					break;
				case 4:
					if (httpRequest.status === 200 || httpRequest.status === 1223) {
						if (typeof success === "function")
							success(httpRequest.responseText);
					} else {
						if (typeof error === "function")
							error(httpRequest,httpRequest.statusText,httpRequest.status);
					}
					break;
			}
		};

	init(obj);
}


function CIdCounter ()
{
    this.m_sUserId        = null;
    this.m_bLoad          = true;
    this.m_bRead          = false;
    this.m_nIdCounterLoad = 0; // Счетчик Id для загрузки
    this.m_nIdCounterEdit = 0; // Счетчик Id для работы
}
CIdCounter.prototype.Get_NewId = function()
{
    if (true === this.m_bLoad || null === this.m_sUserId)
    {
        this.m_nIdCounterLoad++;
        return ("" + this.m_nIdCounterLoad);
    }
    else
    {
        this.m_nIdCounterEdit++;
        return ("" + this.m_sUserId + "_" + this.m_nIdCounterEdit);
    }
};
CIdCounter.prototype.Set_UserId = function(sUserId)
{
    this.m_sUserId = sUserId;
};
CIdCounter.prototype.Set_Load = function(bValue)
{
    this.m_bLoad = bValue;
};
CIdCounter.prototype.Clear = function()
{
    this.m_sUserId        = null;
    this.m_bLoad          = true;
    this.m_nIdCounterLoad = 0; // Счетчик Id для загрузки
    this.m_nIdCounterEdit = 0; // Счетчик Id для работы
};

function CTableId()
{
    this.m_aPairs = null;
    this.m_bTurnOff = false;
    this.Id = null;
    this.isInit = false;
}
CTableId.prototype.checkInit = function()
{
  return this.isInit;
};
CTableId.prototype.init = function()
{
  this.m_aPairs   = {};
  this.m_bTurnOff = false;
  this.Id         = g_oIdCounter.Get_NewId();
  this.Add(this, this.Id);
  this.isInit = true;
};
CTableId.prototype.Add = function(Class, Id)
{
    if (false === this.m_bTurnOff)
    {
        Class.Id = Id;
        this.m_aPairs[Id] = Class;

      AscCommon.History.Add(this, { Type : AscDFH.historyitem_TableId_Add, Id : Id, Class : Class  });
    }
};
CTableId.prototype.TurnOff = function()
{
    this.m_bTurnOff = true;
};
CTableId.prototype.TurnOn = function()
{
    this.m_bTurnOff = false;
};
/*
 Получаем указатель на класс по Id
 */
CTableId.prototype.Get_ById = function(Id)
{
    if ("" === Id)
        return null;

    if ("undefined" != typeof(this.m_aPairs[Id]))
        return this.m_aPairs[Id];

    return null;
};
/*
 Получаем Id, по классу (вообще, данную функцию лучше не использовать)
 */
CTableId.prototype.Get_ByClass = function(Class)
{
    if ("undefined" != typeof( Class.Get_Id ))
        return Class.Get_Id();

    if ("undefined" != typeof( Class.GetId() ))
        return Class.GetId();

    return null;
};
CTableId.prototype.Reset_Id = function(Class, Id_new, Id_old)
{
    if (Class === this.m_aPairs[Id_old])
    {
        delete this.m_aPairs[Id_old];
        this.m_aPairs[Id_new] = Class;

      AscCommon.History.Add(this, { Type : AscDFH.historyitem_TableId_Reset, Id_new : Id_new, Id_old : Id_old  });
    }
    else
    {
        this.Add(Class, Id_new);
    }
};
CTableId.prototype.Get_Id = function()
{
    return this.Id;
};
CTableId.prototype.Clear = function()
{
    this.m_aPairs = {};
    this.m_bTurnOff = false;
    this.Add(this, g_oIdCounter.Get_NewId());
};
//-----------------------------------------------------------------------------------
// Функции для работы с Undo/Redo
//-----------------------------------------------------------------------------------
CTableId.prototype.Undo = function(Data)
{
    // Ничего не делаем (можно удалять/добавлять ссылки на классы в данном классе
    // но это не обяательно, т.к. Id всегда уникальные)
};
CTableId.prototype.Redo = function(Redo)
{
    // Ничего не делаем (можно удалять/добавлять ссылки на классы в данном классе
    // но это не обяательно, т.к. Id всегда уникальные)
};
CTableId.prototype.Refresh_RecalcData = function(Data)
{
    // Ничего не делаем, добавление/удаление классов не влияет на пересчет
};
//-----------------------------------------------------------------------------------
// Функции для работы с совместным редактирования
//-----------------------------------------------------------------------------------
CTableId.prototype.Read_Class_FromBinary = function(Reader)
{
    var ElementType = Reader.GetLong();
    var Element = null;

    // Временно отключаем регистрацию новых классов
    this.m_bTurnOff = true;

    switch( ElementType )
    {
        case AscDFH.historyitem_type_Paragraph                : Element = new AscCommonWord.Paragraph(); break;
        case AscDFH.historyitem_type_TextPr                   : Element = new AscCommonWord.ParaTextPr(); break;
        case AscDFH.historyitem_type_Hyperlink                : Element = new AscCommonWord.ParaHyperlink(); break;
        case AscDFH.historyitem_type_Drawing                  : Element = new AscCommonWord.ParaDrawing(); break;
        case AscDFH.historyitem_type_Table                    : Element = new AscCommonWord.CTable(); break;
        case AscDFH.historyitem_type_TableRow                 : Element = new AscCommonWord.CTableRow(); break;
        case AscDFH.historyitem_type_TableCell                : Element = new AscCommonWord.CTableCell(); break;
        case AscDFH.historyitem_type_DocumentContent          : Element = new AscCommonWord.CDocumentContent(); break;
        case AscDFH.historyitem_type_HdrFtr                   : Element = new AscCommonWord.CHeaderFooter(); break;
        case AscDFH.historyitem_type_AbstractNum              : Element = new AscCommonWord.CAbstractNum(); break;
        case AscDFH.historyitem_type_Comment                  : Element = new AscCommon.CComment(); break;
        case AscDFH.historyitem_type_Style                    : Element = new AscCommonWord.CStyle(); break;
        case AscDFH.historyitem_type_CommentMark              : Element = new AscCommon.ParaComment(); break;
        case AscDFH.historyitem_type_ParaRun                  : Element = new AscCommonWord.ParaRun(); break;
        case AscDFH.historyitem_type_Section                  : Element = new AscCommonWord.CSectionPr(); break;
        case AscDFH.historyitem_type_Field                    : Element = new AscCommonWord.ParaField(); break;

        case AscDFH.historyitem_type_DefaultShapeDefinition   : Element = new AscFormat.DefaultShapeDefinition(); break;
        case AscDFH.historyitem_type_CNvPr                    : Element = new AscFormat.CNvPr(); break;
        case AscDFH.historyitem_type_NvPr                     : Element = new AscFormat.NvPr(); break;
        case AscDFH.historyitem_type_Ph                       : Element = new AscFormat.Ph(); break;
        case AscDFH.historyitem_type_UniNvPr                  : Element = new AscFormat.UniNvPr(); break;
        case AscDFH.historyitem_type_StyleRef                 : Element = new AscFormat.StyleRef(); break;
        case AscDFH.historyitem_type_FontRef                  : Element = new AscFormat.FontRef(); break;
        case AscDFH.historyitem_type_Chart                    : Element = new AscFormat.CChart(); break;
        case AscDFH.historyitem_type_ChartSpace               : Element = new AscFormat.CChartSpace(); break;
        case AscDFH.historyitem_type_Legend                   : Element = new AscFormat.CLegend(); break;
        case AscDFH.historyitem_type_Layout                   : Element = new AscFormat.CLayout(); break;
        case AscDFH.historyitem_type_LegendEntry              : Element = new AscFormat.CLegendEntry(); break;
        case AscDFH.historyitem_type_PivotFmt                 : Element = new AscFormat.CPivotFmt(); break;
        case AscDFH.historyitem_type_DLbl                     : Element = new AscFormat.CDLbl(); break;
        case AscDFH.historyitem_type_Marker                   : Element = new AscFormat.CMarker(); break;
        case AscDFH.historyitem_type_PlotArea                 : Element = new AscFormat.CPlotArea(); break;
        case AscDFH.historyitem_type_NumFmt                   : Element = new AscFormat.CNumFmt(); break;
        case AscDFH.historyitem_type_Scaling                  : Element = new AscFormat.CScaling(); break;
        case AscDFH.historyitem_type_DTable                   : Element = new AscFormat.CDTable(); break;
        case AscDFH.historyitem_type_LineChart                : Element = new AscFormat.CLineChart(); break;
        case AscDFH.historyitem_type_DLbls                    : Element = new AscFormat.CDLbls(); break;
        case AscDFH.historyitem_type_UpDownBars               : Element = new AscFormat.CUpDownBars(); break;
        case AscDFH.historyitem_type_BarChart                 : Element = new AscFormat.CBarChart(); break;
        case AscDFH.historyitem_type_BubbleChart              : Element = new AscFormat.CBubbleChart(); break;
        case AscDFH.historyitem_type_DoughnutChart            : Element = new AscFormat.CDoughnutChart(); break;
        case AscDFH.historyitem_type_OfPieChart               : Element = new AscFormat.COfPieChart(); break;
        case AscDFH.historyitem_type_PieChart                 : Element = new AscFormat.CPieChart(); break;
        case AscDFH.historyitem_type_RadarChart               : Element = new AscFormat.CRadarChart(); break;
        case AscDFH.historyitem_type_ScatterChart             : Element = new AscFormat.CScatterChart(); break;
        case AscDFH.historyitem_type_StockChart               : Element = new AscFormat.CStockChart(); break;
        case AscDFH.historyitem_type_SurfaceChart             : Element = new AscFormat.CSurfaceChart(); break;
        case AscDFH.historyitem_type_BandFmt                  : Element = new AscFormat.CBandFmt(); break;
        case AscDFH.historyitem_type_AreaChart                : Element = new AscFormat.CAreaChart(); break;
        case AscDFH.historyitem_type_ScatterSer               : Element = new AscFormat.CScatterSeries(); break;
        case AscDFH.historyitem_type_DPt                      : Element = new AscFormat.CDPt(); break;
        case AscDFH.historyitem_type_ErrBars                  : Element = new AscFormat.CErrBars(); break;
        case AscDFH.historyitem_type_MinusPlus                : Element = new AscFormat.CMinusPlus(); break;
        case AscDFH.historyitem_type_NumLit                   : Element = new AscFormat.CNumLit(); break;
        case AscDFH.historyitem_type_NumericPoint             : Element = new AscFormat.CNumericPoint(); break;
        case AscDFH.historyitem_type_NumRef                   : Element = new AscFormat.CNumRef(); break;
        case AscDFH.historyitem_type_TrendLine                : Element = new AscFormat.CTrendLine(); break;
        case AscDFH.historyitem_type_Tx                       : Element = new AscFormat.CTx(); break;
        case AscDFH.historyitem_type_StrRef                   : Element = new AscFormat.CStrRef(); break;
        case AscDFH.historyitem_type_StrCache                 : Element = new AscFormat.CStrCache(); break;
        case AscDFH.historyitem_type_StrPoint                 : Element = new AscFormat.CStringPoint(); break;
        case AscDFH.historyitem_type_XVal                     : Element = new AscFormat.CXVal(); break;
        case AscDFH.historyitem_type_MultiLvlStrRef           : Element = new AscFormat.CMultiLvlStrRef(); break;
        case AscDFH.historyitem_type_MultiLvlStrCache         : Element = new AscFormat.CMultiLvlStrCache(); break;
        case AscDFH.historyitem_type_StringLiteral            : Element = new AscFormat.CStringLiteral(); break;
        case AscDFH.historyitem_type_YVal                     : Element = new AscFormat.CYVal(); break;
        case AscDFH.historyitem_type_AreaSeries               : Element = new AscFormat.CAreaSeries(); break;
        case AscDFH.historyitem_type_Cat                      : Element = new AscFormat.CCat(); break;
        case AscDFH.historyitem_type_PictureOptions           : Element = new AscFormat.CPictureOptions(); break;
        case AscDFH.historyitem_type_RadarSeries              : Element = new AscFormat.CRadarSeries(); break;
        case AscDFH.historyitem_type_BarSeries                : Element = new AscFormat.CBarSeries(); break;
        case AscDFH.historyitem_type_LineSeries               : Element = new AscFormat.CLineSeries(); break;
        case AscDFH.historyitem_type_PieSeries                : Element = new AscFormat.CPieSeries(); break;
        case AscDFH.historyitem_type_SurfaceSeries            : Element = new AscFormat.CSurfaceSeries(); break;
        case AscDFH.historyitem_type_BubbleSeries             : Element = new AscFormat.CBubbleSeries(); break;
        case AscDFH.historyitem_type_ExternalData             : Element = new AscFormat.CExternalData(); break;
        case AscDFH.historyitem_type_PivotSource              : Element = new AscFormat.CPivotSource(); break;
        case AscDFH.historyitem_type_Protection               : Element = new AscFormat.CProtection(); break;
        case AscDFH.historyitem_type_ChartWall                : Element = new AscFormat.CChartWall(); break;
        case AscDFH.historyitem_type_View3d                   : Element = new AscFormat.CView3d(); break;
        case AscDFH.historyitem_type_ChartText                : Element = new AscFormat.CChartText(); break;
        case AscDFH.historyitem_type_ShapeStyle               : Element = new AscFormat.CShapeStyle(); break;
        case AscDFH.historyitem_type_Xfrm                     : Element = new AscFormat.CXfrm(); break;
        case AscDFH.historyitem_type_SpPr                     : Element = new AscFormat.CSpPr(); break;
        case AscDFH.historyitem_type_ClrScheme                : Element = new AscFormat.ClrScheme(); break;
        case AscDFH.historyitem_type_ClrMap                   : Element = new AscFormat.ClrMap(); break;
        case AscDFH.historyitem_type_ExtraClrScheme           : Element = new AscFormat.ExtraClrScheme(); break;
        case AscDFH.historyitem_type_FontCollection           : Element = new AscFormat.FontCollection(); break;
        case AscDFH.historyitem_type_FontScheme               : Element = new AscFormat.FontScheme(); break;
        case AscDFH.historyitem_type_FormatScheme             : Element = new AscFormat.FmtScheme(); break;
        case AscDFH.historyitem_type_ThemeElements            : Element = new AscFormat.ThemeElements(); break;
        case AscDFH.historyitem_type_HF                       : Element = new AscFormat.HF(); break;
        case AscDFH.historyitem_type_BgPr                     : Element = new AscFormat.CBgPr(); break;
        case AscDFH.historyitem_type_Bg                       : Element = new AscFormat.CBg(); break;
        case AscDFH.historyitem_type_PrintSettings            : Element = new AscFormat.CPrintSettings(); break;
        case AscDFH.historyitem_type_HeaderFooterChart        : Element = new AscFormat.CHeaderFooterChart(); break;
        case AscDFH.historyitem_type_PageMarginsChart         : Element = new AscFormat.CPageMarginsChart(); break;
        case AscDFH.historyitem_type_PageSetup                : Element = new AscFormat.CPageSetup(); break;
        case AscDFH.historyitem_type_Shape                    : Element = new AscFormat.CShape(); break;
        case AscDFH.historyitem_type_DispUnits                : Element = new AscFormat.CDispUnits(); break;
        case AscDFH.historyitem_type_GroupShape               : Element = new AscFormat.CGroupShape(); break;
        case AscDFH.historyitem_type_ImageShape               : Element = new AscFormat.CImageShape(); break;
        case AscDFH.historyitem_type_Geometry                 : Element = new AscFormat.Geometry(); break;
        case AscDFH.historyitem_type_Path                     : Element = new AscFormat.Path(); break;
        case AscDFH.historyitem_type_TextBody                 : Element = new AscFormat.CTextBody(); break;
        case AscDFH.historyitem_type_CatAx                    : Element = new AscFormat.CCatAx(); break;
        case AscDFH.historyitem_type_ValAx                    : Element = new AscFormat.CValAx(); break;
        case AscDFH.historyitem_type_WrapPolygon              : Element = new AscCommonWord.CWrapPolygon(); break;
        case AscDFH.historyitem_type_DateAx                   : Element = new AscFormat.CDateAx(); break;
        case AscDFH.historyitem_type_SerAx                    : Element = new AscFormat.CSerAx(); break;
        case AscDFH.historyitem_type_Title                    : Element = new AscFormat.CTitle(); break;
        case AscDFH.historyitem_type_OleObject                : Element = new AscFormat.COleObject(); break;

        case AscDFH.historyitem_type_Math						: Element = new AscCommonWord.ParaMath(false); break;
        case AscDFH.historyitem_type_MathContent				: Element = new AscCommonWord.CMathContent(); break;
        case AscDFH.historyitem_type_acc						: Element = new AscCommonWord.CAccent(); break;
        case AscDFH.historyitem_type_bar						: Element = new AscCommonWord.CBar(); break;
        case AscDFH.historyitem_type_box						: Element = new AscCommonWord.CBox(); break;
        case AscDFH.historyitem_type_borderBox					: Element = new AscCommonWord.CBorderBox(); break;
        case AscDFH.historyitem_type_delimiter					: Element = new AscCommonWord.CDelimiter(); break;
        case AscDFH.historyitem_type_eqArr						: Element = new AscCommonWord.CEqArray(); break;
        case AscDFH.historyitem_type_frac                      : Element = new AscCommonWord.CFraction(); break;
        case AscDFH.historyitem_type_mathFunc					: Element = new AscCommonWord.CMathFunc(); break;
        case AscDFH.historyitem_type_groupChr					: Element = new AscCommonWord.CGroupCharacter(); break;
        case AscDFH.historyitem_type_lim						: Element = new AscCommonWord.CLimit(); break;
        case AscDFH.historyitem_type_matrix					: Element = new AscCommonWord.CMathMatrix(); break;
        case AscDFH.historyitem_type_nary						: Element = new AscCommonWord.CNary(); break;
        case AscDFH.historyitem_type_phant						: Element = new AscCommonWord.CPhantom(); break;
        case AscDFH.historyitem_type_rad						: Element = new AscCommonWord.CRadical(); break;
        case AscDFH.historyitem_type_deg_subsup				: Element = new AscCommonWord.CDegreeSubSup(); break;
        case AscDFH.historyitem_type_deg						: Element = new AscCommonWord.CDegree(); break;
        case AscDFH.historyitem_type_Slide                     : Element = new AscCommonSlide.Slide(); break;
        case  AscDFH.historyitem_type_SlideLayout              : Element = new AscCommonSlide.SlideLayout(); break;
        case  AscDFH.historyitem_type_SlideMaster              : Element = new AscCommonSlide.MasterSlide(); break;
        case  AscDFH.historyitem_type_SlideComments            : Element = new AscCommonSlide.SlideComments(); break;
        case  AscDFH.historyitem_type_PropLocker               : Element = new AscCommonSlide.PropLocker(); break;
        case  AscDFH.historyitem_type_Theme                    : Element = new AscFormat.CTheme(); break;
        case  AscDFH.historyitem_type_GraphicFrame             : Element = new AscFormat.CGraphicFrame(); break;
    }

    if ( null !== Element )
        Element.Read_FromBinary2(Reader);

    // Включаем назад регистрацию новых классов
    this.m_bTurnOff = false;

    return Element;
};
CTableId.prototype.Save_Changes = function(Data, Writer)
{
    // Сохраняем изменения из тех, которые используются для Undo/Redo в бинарный файл.
    // Long : тип класса
    // Long : тип изменений

    Writer.WriteLong( AscDFH.historyitem_type_TableId );

    var Type = Data.Type;

    // Пишем тип
    Writer.WriteLong( Type );
    switch ( Type )
    {
        case AscDFH.historyitem_TableId_Add :
        {
            // String   : Id элемента
            // Varibale : сам элемент

            Writer.WriteString2( Data.Id );
            Data.Class.Write_ToBinary2( Writer );

            break;
        }

        case AscDFH.historyitem_TableId_Reset:
        {
            // String : Id_new
            // String : Id_old

            Writer.WriteString2( Data.Id_new );
            Writer.WriteString2( Data.Id_old );

            break;
        }

        case AscDFH.historyitem_TableId_Description:
        {
            // Long : FileCheckSum
            // Long : FileSize
            // Long : Description
            // Long : ItemsCount
            // Long : PointIndex
            // Long : StartPoint
            // Long : LastPoint
            // Long : SumIndex
            // Long : DeletedIndex
            // String : Версия SDK

            Writer.WriteLong(Data.FileCheckSum);
            Writer.WriteLong(Data.FileSize);
            Writer.WriteLong(Data.Description);
            Writer.WriteLong(Data.ItemsCount);
            Writer.WriteLong(Data.PointIndex);
            Writer.WriteLong(Data.StartPoint);
            Writer.WriteLong(Data.LastPoint);
            Writer.WriteLong(Data.SumIndex);
            Writer.WriteLong(null === Data.DeletedIndex ? -10 : Data.DeletedIndex);
            Writer.WriteString2("undefined.undefined.@@Rev");

            break;
        }
    }
};
CTableId.prototype.Save_Changes2 = function(Data, Writer)
{
    return false;
};
CTableId.prototype.Load_Changes = function(Reader, Reader2)
{
    // Сохраняем изменения из тех, которые используются для Undo/Redo в бинарный файл.
    // Long : тип класса
    // Long : тип изменений

    var ClassType = Reader.GetLong();
    if ( AscDFH.historyitem_type_TableId != ClassType )
        return;

    var Type = Reader.GetLong();

    switch ( Type )
    {
        case AscDFH.historyitem_Common_AddWatermark:
        {
            var sUrl = Reader.GetString2();
            if('undefined' != typeof editor && editor.WordControl && editor.WordControl.m_oLogicDocument)
            {
                var oLogicDocument = editor.WordControl.m_oLogicDocument;
                if(oLogicDocument instanceof AscCommonWord.CDocument)
                {
                    var oParaDrawing = oLogicDocument.DrawingObjects.getTrialImage(sUrl);
                    var oFirstParagraph = oLogicDocument.Get_FirstParagraph();
                    AscFormat.ExecuteNoHistory(function(){
                        var oRun = new AscCommonWord.ParaRun();
                        oRun.Content.splice(0, 0, oParaDrawing);
                        oFirstParagraph.Content.splice(0, 0, oRun);
						oLogicDocument.DrawingObjects.addGraphicObject(oParaDrawing);
                    }, this, []);
                }
                else if(oLogicDocument instanceof AscCommonSlide.CPresentation)
                {
                    if(oLogicDocument.Slides[0])
                    {
                        var oDrawing = oLogicDocument.Slides[0].graphicObjects.createWatermarkImage(sUrl);
                        oDrawing.spPr.xfrm.offX = (oLogicDocument.Width - oDrawing.spPr.xfrm.extX)/2;
                        oDrawing.spPr.xfrm.offY = (oLogicDocument.Height - oDrawing.spPr.xfrm.extY)/2;
						oDrawing.parent = oLogicDocument.Slides[0];
                        oLogicDocument.Slides[0].cSld.spTree.push(oDrawing);
                    }
                }
            }
            else
            {
                var oWsModel = window["Asc"]["editor"].wbModel.aWorksheets[0];
                if(oWsModel)
                {
                    var objectRender = new AscFormat.DrawingObjects();
                    var oNewDrawing = objectRender.createDrawingObject(AscCommon.c_oAscCellAnchorType.cellanchorAbsolute);
                    var oImage = AscFormat.DrawingObjectsController.prototype.createWatermarkImage(sUrl);
                    oNewDrawing.ext.cx = oImage.spPr.xfrm.extX;
                    oNewDrawing.ext.cy = oImage.spPr.xfrm.extY;
                    oNewDrawing.graphicObject = oImage;
                    oWsModel.Drawings.push(oNewDrawing);
                }
            }
            break;
        }
        case AscDFH.historyitem_TableId_Add:
        {
            // String   : Id элемента
            // Varibale : сам элемент

            var Id    = Reader.GetString2();
            var Class = this.Read_Class_FromBinary( Reader );

            this.m_aPairs[Id] = Class;

            break;
        }

        case AscDFH.historyitem_TableId_Reset:
        {
            // String : Id_new
            // String : Id_old

            var Id_new = Reader.GetString2();
            var Id_old = Reader.GetString2();

            if ( "undefined" != this.m_aPairs[Id_old] )
            {
                var Class = this.m_aPairs[Id_old];
                delete this.m_aPairs[Id_old];
                this.m_aPairs[Id_new] = Class;
                Class.Id = Id_new;
            }

            break;
        }

        case AscDFH.historyitem_TableId_Description:
        {
            // Long : FileCheckSum
            // Long : FileSize
            // Long : Description
            // Long : ItemsCount
            // Long : PointIndex
            // Long : StartPoint
            // Long : LastPoint
            // Long : SumIndex
            // Long : DeletedIndex
            // String : Версия SDK

            var FileCheckSum = Reader.GetLong();
            var FileSize     = Reader.GetLong();
            var Description  = Reader.GetLong();
            var ItemsCount   = Reader.GetLong();
            var PointIndex   = Reader.GetLong();
            var StartPoint   = Reader.GetLong();
            var LastPoint    = Reader.GetLong();
            var SumIndex     = Reader.GetLong();
            var DeletedIndex = Reader.GetLong();
            var VersionString= Reader.GetString2();

            //                // CollaborativeEditing LOG
            //                console.log("ItemsCount2  " + CollaborativeEditing.m_nErrorLog_PointChangesCount);
            //                if (CollaborativeEditing.m_nErrorLog_PointChangesCount !== CollaborativeEditing.m_nErrorLog_SavedPCC)
            //                    console.log("========================= BAD Changes Count in Point =============================");
            //
            //                if (CollaborativeEditing.m_nErrorLog_CurPointIndex + 1 !== PointIndex && 0 !== PointIndex)
            //                    console.log("========================= BAD Point index ========================================");
            //
            //                var bBadSumIndex = false;
            //                if (0 === PointIndex)
            //                {
            //                    CollaborativeEditing.m_nErrorLog_SumIndex = 0;
            //                }
            //                else
            //                {
            //                    CollaborativeEditing.m_nErrorLog_SumIndex += CollaborativeEditing.m_nErrorLog_SavedPCC + 1; // Потому что мы не учитываем данное изменение
            //                    if (PointIndex === StartPoint)
            //                    {
            //                        if (CollaborativeEditing.m_nErrorLog_SumIndex !== SumIndex)
            //                            bBadSumIndex = true;
            //
            //                        console.log("SumIndex2    " + CollaborativeEditing.m_nErrorLog_SumIndex);
            //                        CollaborativeEditing.m_nErrorLog_SumIndex = SumIndex;
            //                    }
            //                }
            //
            //                console.log("----------------------------");
            //                console.log("FileCheckSum " + FileCheckSum);
            //                console.log("FileSize     " + FileSize);
            //                console.log("Description  " + Description + " " + AscDFH.Get_HistoryPointStringDescription(Description));
            //                console.log("PointIndex   " + PointIndex);
            //                console.log("StartPoint   " + StartPoint);
            //                console.log("LastPoint    " + LastPoint);
            //                console.log("ItemsCount   " + ItemsCount);
            //                console.log("SumIndex     " + SumIndex);
            //                console.log("DeletedIndex " + (-10 === DeletedIndex ? null : DeletedIndex));
            //
            //                // -1 Чтобы не учитывалось данное изменение
            //                CollaborativeEditing.m_nErrorLog_SavedPCC          = ItemsCount;
            //                CollaborativeEditing.m_nErrorLog_PointChangesCount = -1;
            //                CollaborativeEditing.m_nErrorLog_CurPointIndex     = PointIndex;
            //
            //                if (bBadSumIndex)
            //                    console.log("========================= BAD Sum index ==========================================");

            break;
        }
    }

    return true;
};
CTableId.prototype.Unlock = function(Data)
{
    // Ничего не делаем
};

function CLock()
{
    this.Type   = locktype_None;
    this.UserId = null;
}

CLock.prototype.Get_Type = function()
{
	return this.Type;
};
CLock.prototype.Set_Type = function(NewType, Redraw)
{
	if ( NewType === locktype_None )
		this.UserId = null;

	this.Type = NewType;

	if ( false != Redraw )
	{
		// TODO: переделать перерисовку тут
		var DrawingDocument = editor.WordControl.m_oLogicDocument.DrawingDocument;
		DrawingDocument.ClearCachePages();
		DrawingDocument.FirePaint();
	}
};
CLock.prototype.Check = function(Id)
{
	if ( this.Type === locktype_Mine )
    AscCommon.CollaborativeEditing.Add_CheckLock( false );
	else if ( this.Type === locktype_Other || this.Type === locktype_Other2 || this.Type === locktype_Other3 )
    AscCommon.CollaborativeEditing.Add_CheckLock( true );
	else
    AscCommon.CollaborativeEditing.Add_CheckLock( Id );
};
CLock.prototype.Lock = function(bMine)
{
	if ( locktype_None === this.Type )
	{
		if ( true === bMine )
			this.Type = locktype_Mine;
		else
			true.Type = locktype_Other;
	}
};
CLock.prototype.Is_Locked = function()
{
	if ( locktype_None != this.Type && locktype_Mine != this.Type )
		return true;

	return false;
};
CLock.prototype.Set_UserId = function(UserId)
{
	this.UserId = UserId;
};
CLock.prototype.Get_UserId = function()
{
	return this.UserId;
};
CLock.prototype.Have_Changes = function()
{
	if ( locktype_Other2 === this.Type || locktype_Other3 === this.Type )
		return true;

	return false;
};


function CContentChanges()
{
    this.m_aChanges = [];
}

CContentChanges.prototype.Add = function(Changes)
{
	this.m_aChanges.push( Changes );
};
CContentChanges.prototype.Clear = function()
{
	this.m_aChanges.length = 0;
};
CContentChanges.prototype.Check = function(Type, Pos)
{
	var CurPos = Pos;
	var Count = this.m_aChanges.length;
	for ( var Index = 0; Index < Count; Index++ )
	{
		var NewPos = this.m_aChanges[Index].Check_Changes(Type, CurPos);
		if ( false === NewPos )
			return false;

		CurPos = NewPos;
	}

	return CurPos;
};
CContentChanges.prototype.Refresh = function()
{
	var Count = this.m_aChanges.length;
	for ( var Index = 0; Index < Count; Index++ )
	{
		this.m_aChanges[Index].Refresh_BinaryData();
	}
};

function CContentChangesElement(Type, Pos, Count, Data) {
	this.m_nType	= Type;  // Тип изменений (удаление или добавление)
	this.m_nCount	= Count; // Количество добавленных/удаленных элементов
	this.m_pData	= Data;  // Связанные с данным изменением данные из истории

	// Разбиваем сложное действие на простейшие
	this.m_aPositions = this.Make_ArrayOfSimpleActions( Type, Pos, Count );
}

CContentChangesElement.prototype.Refresh_BinaryData = function()
{
	var Binary_Writer = AscCommon.History.BinaryWriter;
	var Binary_Pos = Binary_Writer.GetCurPosition();

	this.m_pData.Data.UseArray = true;
	this.m_pData.Data.PosArray = this.m_aPositions;

	Binary_Writer.WriteString2(this.m_pData.Class.Get_Id());
	this.m_pData.Class.Save_Changes( this.m_pData.Data, Binary_Writer );

	var Binary_Len = Binary_Writer.GetCurPosition() - Binary_Pos;

	this.m_pData.Binary.Pos = Binary_Pos;
	this.m_pData.Binary.Len = Binary_Len;
};
CContentChangesElement.prototype.Check_Changes = function(Type, Pos)
{
	var CurPos = Pos;
	if ( contentchanges_Add === Type )
	{
		for ( var Index = 0; Index < this.m_nCount; Index++ )
		{
			if ( false !== this.m_aPositions[Index] )
			{
				if ( CurPos <= this.m_aPositions[Index] )
					this.m_aPositions[Index]++;
				else
				{
					if ( contentchanges_Add === this.m_nType )
						CurPos++;
					else //if ( contentchanges_Remove === this.m_nType )
						CurPos--;
				}
			}
		}
	}
	else //if ( contentchanges_Remove === Type )
	{
		for ( var Index = 0; Index < this.m_nCount; Index++ )
		{
			if ( false !== this.m_aPositions[Index] )
			{
				if ( CurPos < this.m_aPositions[Index] )
					this.m_aPositions[Index]--;
				else if ( CurPos > this.m_aPositions[Index] )
				{
					if ( contentchanges_Add === this.m_nType )
						CurPos++;
					else //if ( contentchanges_Remove === this.m_nType )
						CurPos--;
				}
				else //if ( CurPos === this.m_aPositions[Index] )
				{
					if ( AscCommon.contentchanges_Remove === this.m_nType )
					{
						// Отмечаем, что действия совпали
						this.m_aPositions[Index] = false;
						return false;
					}
					else
					{
						CurPos++;
					}
				}
			}
		}
	}

	return CurPos;
};
CContentChangesElement.prototype.Make_ArrayOfSimpleActions = function(Type, Pos, Count)
{
	// Разбиваем действие на простейшие
	var Positions = [];
	if ( contentchanges_Add === Type )
	{
		for ( var Index = 0; Index < Count; Index++ )
			Positions[Index] = Pos + Index;
	}
	else //if ( contentchanges_Remove === Type )
	{
		for ( var Index = 0; Index < Count; Index++ )
			Positions[Index] = Pos;
	}

	return Positions;
};
var g_oUserColorById = {}, g_oUserNextColorIndex = 0;
function getUserColorById(userId, userName, isDark, isNumericValue)
{
    if ((!userId || "" === userId) && (!userName || "" === userName))
        return new CColor(0, 0, 0, 255);

    var res;
    if (g_oUserColorById.hasOwnProperty(userId))
    {
        res = g_oUserColorById[userId];
    }
    else if (g_oUserColorById.hasOwnProperty(userName))
    {
        res = g_oUserColorById[userName];
    }
    else
    {
        var nColor = Asc.c_oAscArrUserColors[g_oUserNextColorIndex % Asc.c_oAscArrUserColors.length];
        ++g_oUserNextColorIndex;

      res = g_oUserColorById[userId||userName] = new CUserCacheColor(nColor);
    }

    if (!res)
        return new CColor(0, 0, 0, 255);

    var oColor = true === isDark ? res.Dark : res.Light;
    return true === isNumericValue ? ((oColor.r << 16) & 0xFF0000) | ((oColor.g << 8) & 0xFF00) | (oColor.b & 0xFF) : oColor;
}
  
  function isNullOrEmptyString(str) {
    return (str == undefined) || (str == null) || (str == "");
  }
  
function CUserCacheColor(nColor)
{
  this.Light = null;
  this.Dark  = null;
  this.init(nColor);
}
CUserCacheColor.prototype.init = function(nColor) {
  var r = (nColor >> 16) & 0xFF;
  var g = (nColor >> 8) & 0xFF;
  var b = nColor & 0xFF;

  var Y  = Math.max(0, Math.min(255,       0.299    * r + 0.587    * g + 0.114    * b));
  var Cb = Math.max(0, Math.min(255, 128 - 0.168736 * r - 0.331264 * g + 0.5      * b));
  var Cr = Math.max(0, Math.min(255, 128 + 0.5      * r - 0.418688 * g - 0.081312 * b));

  if (Y > 63)
    Y = 63;

  var R = Math.max(0, Math.min(255, Y                        + 1.402   * (Cr - 128))) | 0;
  var G = Math.max(0, Math.min(255, Y - 0.34414 * (Cb - 128) - 0.71414 * (Cr - 128))) | 0;
  var B = Math.max(0, Math.min(255, Y + 1.772   * (Cb - 128)                       )) | 0;

  this.Light = new CColor(r, g, b, 255);
  this.Dark  = new CColor(R, G, B, 255);
};

  function loadScript(url, callback) {
    if (window["NATIVE_EDITOR_ENJINE"] === true || window["Native"] !== undefined)
    {
        callback();
        return;
    }

    if (window["AscDesktopEditor"])
    {
        var _ret_param = window["AscDesktopEditor"]["LoadJS"](url);
        if (_ret_param == 1)
        {
            setTimeout(callback, 1);
            return;
        }
        else if (_ret_param == 2)
        {
            window["asc_desktop_localModuleId"] = "sdk-all.js";
            window["asc_desktop_context"] = { "completeLoad" : function() { return callback(); } };
            return;
        }
    }

    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;

    script.onreadystatechange = callback;
    script.onload = callback;

    // Fire the loading
    document.head.appendChild(script);
  }
  function loadSdk(sdkName, callback) {
    if (window['AscNotLoadAllScript']) {
      callback();
    } else {
      loadScript('./../../../../sdkjs/' + sdkName + '/sdk-all.js', callback);
    }
  }

var g_oIdCounter = new CIdCounter();
var g_oTableId = new CTableId();

window["SetDoctRendererParams"] = function(_params)
{
	if (_params["retina"] === true)
		AscBrowser.isRetina = true;
};
  
  //------------------------------------------------------------export---------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window["AscCommon"].getEncodingParams = getEncodingParams;
  window["AscCommon"].saveWithParts = saveWithParts;
  window["AscCommon"].loadFileContent = loadFileContent;
  window["AscCommon"].getImageFromChanges = getImageFromChanges;
  window["AscCommon"].openFileCommand = openFileCommand;
  window["AscCommon"].sendCommand = sendCommand;
  window["AscCommon"].mapAscServerErrorToAscError = mapAscServerErrorToAscError;
  window["AscCommon"].joinUrls = joinUrls;
  window["AscCommon"].getFullImageSrc2 = getFullImageSrc2;
  window["AscCommon"].fSortAscending = fSortAscending;
  window["AscCommon"].fSortDescending = fSortDescending;
  window["AscCommon"].fOnlyUnique = fOnlyUnique;
  window["AscCommon"].isLeadingSurrogateChar = isLeadingSurrogateChar;
  window["AscCommon"].decodeSurrogateChar = decodeSurrogateChar;
  window["AscCommon"].encodeSurrogateChar = encodeSurrogateChar;
  window["AscCommon"].convertUnicodeToUTF16 = convertUnicodeToUTF16;
  window["AscCommon"].convertUTF16toUnicode = convertUTF16toUnicode;
  window["AscCommon"].build_local_rx = build_local_rx;
  window["AscCommon"].GetFileExtension = GetFileExtension;
  window["AscCommon"].changeFileExtention = changeFileExtention;
  window["AscCommon"].getExtentionByFormat = getExtentionByFormat;
  window["AscCommon"].InitOnMessage = InitOnMessage;
  window["AscCommon"].ShowImageFileDialog = ShowImageFileDialog;
  window["AscCommon"].InitDragAndDrop = InitDragAndDrop;
  window["AscCommon"].UploadImageFiles = UploadImageFiles;
  window["AscCommon"].CanDropFiles = CanDropFiles;
  window["AscCommon"].getUrlType = getUrlType;
  window["AscCommon"].prepareUrl = prepareUrl;
  window["AscCommon"].extendClass = extendClass;
  window["AscCommon"].getUserColorById = getUserColorById;
  window["AscCommon"].isNullOrEmptyString = isNullOrEmptyString;

  window["AscCommon"].DocumentUrls = DocumentUrls;
  window["AscCommon"].CLock = CLock;
  window["AscCommon"].CContentChanges = CContentChanges;
  window["AscCommon"].CContentChangesElement = CContentChangesElement;

  window["AscCommon"].loadSdk = loadSdk;

  window["AscCommon"].g_oDocumentUrls = g_oDocumentUrls;
  window["AscCommon"].FormulaTablePartInfo = FormulaTablePartInfo;
  window["AscCommon"].cBoolLocal = cBoolLocal;
  window["AscCommon"].cErrorOrigin = cErrorOrigin;
  window["AscCommon"].cErrorLocal = cErrorLocal;
  window["AscCommon"].FormulaSeparators = FormulaSeparators;
  window["AscCommon"].rx_space_g = rx_space_g;
  window["AscCommon"].rx_space = rx_space;
  window["AscCommon"].rx_defName = rx_defName;

  window["AscCommon"].kCurFormatPainterWord = kCurFormatPainterWord;
  window["AscCommon"].parserHelp = parserHelp;
  window["AscCommon"].g_oIdCounter = g_oIdCounter;
  window["AscCommon"].g_oTableId = g_oTableId;
})(window);

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
	function ( window, undefined) {

		/** @constructor */
		function asc_CAdvancedOptions(id,opt){
			this.optionId = null;
			this.options = null;

			switch(id){
				case Asc.c_oAscAdvancedOptionsID.CSV:
					this.optionId = id;
					this.options = new asc_CCSVOptions(opt);
					break;
				case Asc.c_oAscAdvancedOptionsID.TXT:
					this.optionId = id;
					this.options = new asc_CTXTOptions(opt);
					break;
			}
		}
		asc_CAdvancedOptions.prototype.asc_getOptionId = function(){ return this.optionId; };
		asc_CAdvancedOptions.prototype.asc_getOptions = function(){ return this.options; };

		/** @constructor */
		function asc_CCSVOptions(opt){
			this.codePages = function(){
				var arr = [], c, encodings = opt["encodings"];
				for(var i = 0; i < encodings.length; i++ ){
					c = new asc_CCodePage();
					c.init(encodings[i]);
					arr.push(c);
				}
				return arr;
			}();
			this.recommendedSettings = new asc_CCSVAdvancedOptions (opt["codepage"], /*opt["delimiter"]*/AscCommon.c_oAscCsvDelimiter.Comma); // ToDo разделитель пока только "," http://bugzserver/show_bug.cgi?id=31009
		}
		asc_CCSVOptions.prototype.asc_getCodePages = function(){ return this.codePages;};
		asc_CCSVOptions.prototype.asc_getRecommendedSettings = function () { return this.recommendedSettings; };

		/** @constructor */
		function asc_CTXTOptions(opt){
			this.codePages = function(){
				var arr = [], c, encodings = opt["encodings"];
				for(var i = 0; i < encodings.length; i++ ){
					c = new asc_CCodePage();
					c.init(encodings[i]);
					arr.push(c);
				}
				return arr;
			}();
			this.recommendedSettings = new asc_CTXTAdvancedOptions (opt["codepage"]);
		}
		asc_CTXTOptions.prototype.asc_getCodePages = function(){ return this.codePages;};
		asc_CTXTOptions.prototype.asc_getRecommendedSettings = function () { return this.recommendedSettings; };

		/** @constructor */
		function asc_CCSVAdvancedOptions(codepage,delimiter){
			this.codePage = codepage;
			this.delimiter = delimiter;
		}
		asc_CCSVAdvancedOptions.prototype.asc_getDelimiter = function(){return this.delimiter;};
		asc_CCSVAdvancedOptions.prototype.asc_setDelimiter = function(v){this.delimiter = v;};
		asc_CCSVAdvancedOptions.prototype.asc_getCodePage = function(){return this.codePage;};
		asc_CCSVAdvancedOptions.prototype.asc_setCodePage = function(v){this.codePage = v;};
		
		/** @constructor */
		function asc_CTXTAdvancedOptions(codepage){
			this.codePage = codepage;
		}
		asc_CTXTAdvancedOptions.prototype.asc_getCodePage = function(){return this.codePage;};
		asc_CTXTAdvancedOptions.prototype.asc_setCodePage = function(v){this.codePage = v;};

		/** @constructor */
		function asc_CCodePage(){
			this.codePageName = null;
			this.codePage = null;
			this.text = null;
		}
		asc_CCodePage.prototype.init = function (encoding) {
			this.codePageName = encoding["name"];
			this.codePage = encoding["codepage"];
			this.text = encoding["text"];
		};
		asc_CCodePage.prototype.asc_getCodePageName = function(){return this.codePageName;};
		asc_CCodePage.prototype.asc_setCodePageName = function(v){this.codePageName = v;};
		asc_CCodePage.prototype.asc_getCodePage = function(){return this.codePage;};
		asc_CCodePage.prototype.asc_setCodePage = function(v){this.codePage = v;};
		asc_CCodePage.prototype.asc_getText = function(){return this.text;};
		asc_CCodePage.prototype.asc_setText = function(v){this.text = v;};

		/** @constructor */
		function asc_CDelimiter(delimiter){
			this.delimiterName = delimiter;
		}
		asc_CDelimiter.prototype.asc_getDelimiterName = function(){return this.delimiterName;};
		asc_CDelimiter.prototype.asc_setDelimiterName = function(v){ this.delimiterName = v;};

		/** @constructor */
		function asc_CFormulaGroup(name){
			this.groupName = name;
			this.formulasArray = [];
		}
		asc_CFormulaGroup.prototype.asc_getGroupName = function() { return this.groupName; };
		asc_CFormulaGroup.prototype.asc_getFormulasArray = function() { return this.formulasArray; };
		asc_CFormulaGroup.prototype.asc_addFormulaElement = function(o) { return this.formulasArray.push(o); };

		/** @constructor */
		function asc_CFormula(o){
			this.name = o.name;
			this.arg = o.args;
		}
		asc_CFormula.prototype.asc_getName = function () {
			return this.name;
		};
		asc_CFormula.prototype.asc_getLocaleName = function () {
			return AscCommonExcel.cFormulaFunctionToLocale ? AscCommonExcel.cFormulaFunctionToLocale[this.name] : this.name;
		};
		asc_CFormula.prototype.asc_getArguments = function () {
			return this.arg;
		};

		//----------------------------------------------------------export----------------------------------------------------
		var prot;
		window['Asc'] = window['Asc'] || {};
		window['AscCommon'] = window['AscCommon'] || {};
		window["AscCommon"].asc_CAdvancedOptions = asc_CAdvancedOptions;
		prot = asc_CAdvancedOptions.prototype;
		prot["asc_getOptionId"]			= prot.asc_getOptionId;
		prot["asc_getOptions"]			= prot.asc_getOptions;

		prot = asc_CCSVOptions.prototype;
		prot["asc_getCodePages"]			= prot.asc_getCodePages;
		prot["asc_getRecommendedSettings"]	= prot.asc_getRecommendedSettings;

		prot = asc_CTXTOptions.prototype;
		prot["asc_getCodePages"]			= prot.asc_getCodePages;
		prot["asc_getRecommendedSettings"]	= prot.asc_getRecommendedSettings;

		window["Asc"].asc_CCSVAdvancedOptions = window["Asc"]["asc_CCSVAdvancedOptions"] = asc_CCSVAdvancedOptions;
		prot = asc_CCSVAdvancedOptions.prototype;
		prot["asc_getDelimiter"] = prot.asc_getDelimiter;
		prot["asc_setDelimiter"] = prot.asc_setDelimiter;
		prot["asc_getCodePage"] = prot.asc_getCodePage;
		prot["asc_setCodePage"] = prot.asc_setCodePage;

		window["Asc"].asc_CTXTAdvancedOptions = window["Asc"]["asc_CTXTAdvancedOptions"] = asc_CTXTAdvancedOptions;
		prot = asc_CTXTAdvancedOptions.prototype;
		prot["asc_getCodePage"] = prot.asc_getCodePage;
		prot["asc_setCodePage"] = prot.asc_setCodePage;

		prot = asc_CCodePage.prototype;
		prot["asc_getCodePageName"]		= prot.asc_getCodePageName;
		prot["asc_setCodePageName"]		= prot.asc_setCodePageName;
		prot["asc_getCodePage"]			= prot.asc_getCodePage;
		prot["asc_setCodePage"]			= prot.asc_setCodePage;
		prot["asc_getText"]				= prot.asc_getText;
		prot["asc_setText"]				= prot.asc_setText;

		prot = asc_CDelimiter.prototype;
		prot["asc_getDelimiterName"]			= prot.asc_getDelimiterName;
		prot["asc_setDelimiterName"]			= prot.asc_setDelimiterName;

		window["AscCommon"].asc_CFormulaGroup = asc_CFormulaGroup;
		prot = asc_CFormulaGroup.prototype;
		prot["asc_getGroupName"]				= prot.asc_getGroupName;
		prot["asc_getFormulasArray"]			= prot.asc_getFormulasArray;
		prot["asc_addFormulaElement"]			= prot.asc_addFormulaElement;

		window["AscCommon"].asc_CFormula = asc_CFormula;
		prot = asc_CFormula.prototype;
		prot["asc_getName"]				= prot.asc_getName;
		prot["asc_getLocaleName"]	= prot.asc_getLocaleName;
		prot["asc_getArguments"]		= prot.asc_getArguments;
	}
)(window);
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
// Используем [] вместо new Array() для ускорения (http://jsperf.com/creation-array)
// Используем {} вместо new Object() для ускорения (http://jsperf.com/creation-object)

  // Import
  var CColor = AscCommon.CColor;

var c_oAscConfirm = {
  ConfirmReplaceRange: 0,
  ConfirmPutMergeRange: 1
};

var c_oAscAlignType = {
  NONE: "none",
  LEFT: "left",
  CENTER: "center",
  RIGHT: "right",
  JUSTIFY: "justify",
  TOP: "top",
  MIDDLE: "center",
  BOTTOM: "bottom"
};

var c_oAscMergeOptions = {
  Unmerge: 0,
  Merge: 1,
  MergeCenter: 2,
  MergeAcross: 3
};

var c_oAscSortOptions = {
  Ascending: 1,
  Descending: 2,
  ByColorFill: 3,
  ByColorFont: 4
};

var c_oAscBorderOptions = {
  Top: 0,
  Right: 1,
  Bottom: 2,
  Left: 3,
  DiagD: 4,
  DiagU: 5,
  InnerV: 6,
  InnerH: 7
};

var c_oAscCleanOptions = {
  All: 0,
  Text: 1,
  Format: 2,
  Formula: 4,
  Comments: 5,
  Hyperlinks: 6
};

var c_oAscDrawDepOptions = {
  Master: 0,
  Slave: 1,
  Clear: 2
};

var c_oAscSelectionDialogType = {
  None: 0,
  FormatTable: 1,
  Chart: 2,
  DefinedName: 3,
  FormatTableChangeRange: 4
};

var c_oAscGraphicOption = {
  ScrollVertical: 1,
  ScrollHorizontal: 2
};

var c_oAscHyperlinkType = {
  WebLink: 1,
  RangeLink: 2
};

var c_oAscMouseMoveType = {
  None: 0,
  Hyperlink: 1,
  Comment: 2,
  LockedObject: 3,
  ResizeColumn: 4,
  ResizeRow: 5
};

var c_oAscMouseMoveLockedObjectType = {
  None: -1,
  Range: 0,
  TableProperties: 1,
  Sheet: 2
};



var c_oAscLockTypeElem = {
  Range: 1,
  Object: 2,
  Sheet: 3
};

var c_oAscLockTypeElemSubType = {
  DeleteColumns: 1,
  InsertColumns: 2,
  DeleteRows: 3,
  InsertRows: 4,
  ChangeProperties: 5,
  DefinedNames: 6
};

var c_oAscRecalcIndexTypes = {
  RecalcIndexAdd: 1,
  RecalcIndexRemove: 2
};

// Тип печати
var c_oAscPrintType = {
  ActiveSheets: 0,	// Активные листы
  EntireWorkbook: 1,	// Всю книгу
  Selection: 2		// Выделенный фрагмент
};

/** @enum */
var c_oAscCustomAutoFilter = {
  equals: 1,
  isGreaterThan: 2,
  isGreaterThanOrEqualTo: 3,
  isLessThan: 4,
  isLessThanOrEqualTo: 5,
  doesNotEqual: 6,
  beginsWith: 7,
  doesNotBeginWith: 8,
  endsWith: 9,
  doesNotEndWith: 10,
  contains: 11,
  doesNotContain: 12
};

    /** @enum */
var c_oAscDynamicAutoFilter = {
    aboveAverage: 1,
    belowAverage: 2,
    lastMonth: 3,
    lastQuarter: 4,
    lastWeek: 5,
    lastYear: 6,
    m1: 7,
    m10: 8,
    m11: 9,
    m12: 10,
    m2: 11,
    m3: 12,
    m4: 13,
    m5: 14,
    m6: 15,
    m7: 16,
    m8: 17,
    m9: 18,
    nextMonth: 19,
    nextQuarter: 20,
    nextWeek: 21,
    nextYear: 22,
    q1: 23,
    q2: 24,
    q3: 25,
    q4: 26,
    thisMonth: 27,
    thisQuarter: 28,
    thisWeek: 29,
    thisYear: 30,
    today: 31,
    tomorrow: 32,
    yearToDate: 33,
    yesterday: 34
};

var c_oAscTop10AutoFilter = {
    max: 1,
    min: 2
}

var c_oAscChangeFilterOptions = {
  filter: 1,
  style: 2
};

var c_oAscChangeSelectionFormatTable = {
	all: 1,
	data: 2,
	row: 3,
	column: 4
};

var c_oAscChangeTableStyleInfo = {
	columnFirst: 1,
	columnLast: 2,
	columnBanded: 3,
	rowHeader: 4,
	rowTotal: 5,
	rowBanded: 6,
	filterButton: 7
};

// Состояние редактора ячейки
var c_oAscCellEditorState = {
  editEnd: 0,				// Окончание редактирования
  editStart: 1,				// Начало редактирования
  editEmptyCell: 2,				// Редактирование пустой ячейки (доступны функции и свойства текста)
  editText: 3,				// Редактирование текста, числа, даты и др. формата, кроме формулы
  editFormula: 4				// Редактирование формулы
};

// Состояние select-а
var c_oAscCellEditorSelectState = {
  no    : 0,
  char  : 1,
  word  : 2
};

// Пересчитывать ли ширину столбца
var c_oAscCanChangeColWidth = {
  none: 0,	// not recalc
  numbers: 1,	// only numbers
  all: 2	// numbers + text
};

var c_oAscPaneState = {
  Frozen: "frozen",
  FrozenSplit: "frozenSplit"
};

var c_oAscFindLookIn = {
  Formulas: 1,
  Value: 2,
  Annotations: 3
};

var c_oTargetType = {
  None: 0,
  ColumnResize: 1,
  RowResize: 2,
  FillHandle: 3,
  MoveRange: 4,
  MoveResizeRange: 5,
  FilterObject: 6,
  ColumnHeader: 7,
  RowHeader: 8,
  Corner: 9,
  Hyperlink: 10,
  Cells: 11,
  Shape: 12,
  FrozenAnchorH: 14,
  FrozenAnchorV: 15
};

var c_oAscAutoFilterTypes = {
  ColorFilter: 0,
  CustomFilters: 1,
  DynamicFilter: 2,
  Top10: 3,
  Filters: 4,
  None: 5
};

var c_oAscCoAuthoringMeBorderColor = new CColor(22, 156, 0);
var c_oAscCoAuthoringOtherBorderColor = new CColor(238, 53, 37);
var c_oAscCoAuthoringLockTablePropertiesBorderColor = new CColor(255, 144, 0);
var c_oAscCoAuthoringDottedWidth = 4;
var c_oAscCoAuthoringDottedDistance = 2;

var c_oAscFormulaRangeBorderColor = [
  new CColor(95, 140, 237),
  new CColor(235, 94, 96),
  new CColor(141, 97, 194),
  new CColor(45, 150, 57),
  new CColor(191, 76, 145),
  new CColor(227, 130, 34),
  new CColor(55, 127, 158)
];

var c_oAscLockNameFrozenPane = "frozenPane";
var c_oAscLockNameTabColor = "tabColor";

var c_oAscGetDefinedNamesList = {
  Worksheet: 0,
  WorksheetWorkbook: 1,
  All: 2
};

var c_oAscDefinedNameReason = {
  WrongName: -1,
  IsLocked: -2,
  Existed: -3,
  LockDefNameManager: -4,
  NameReserved: -5,
  OK: 0
};

var c_oAscPopUpSelectorType = {
  None: 0,
  Func: 1,
  Range: 2,
  Table: 3
};
  /** @enum */
  var c_oSerFormat = {
    Version		: 2, //1.0.0.2
    Signature	: "XLSY"
  };

  //----------------------------------------------------------export----------------------------------------------------
  window['AscCommonExcel'] = window['AscCommonExcel'] || {};
  window['AscCommonExcel'].c_oAscAlignType = c_oAscAlignType;
  window['AscCommonExcel'].c_oAscDrawDepOptions = c_oAscDrawDepOptions;
  window['AscCommonExcel'].c_oAscGraphicOption = c_oAscGraphicOption;
  window['AscCommonExcel'].c_oAscLockTypeElem = c_oAscLockTypeElem;
  window['AscCommonExcel'].c_oAscLockTypeElemSubType = c_oAscLockTypeElemSubType;
  window['AscCommonExcel'].c_oAscRecalcIndexTypes = c_oAscRecalcIndexTypes;
  window['AscCommonExcel'].c_oAscCellEditorSelectState = c_oAscCellEditorSelectState;
  window['AscCommonExcel'].c_oAscCanChangeColWidth = c_oAscCanChangeColWidth;
  window['AscCommonExcel'].c_oAscPaneState = c_oAscPaneState;
  window['AscCommonExcel'].c_oTargetType = c_oTargetType;
  window['AscCommonExcel'].c_oAscCoAuthoringMeBorderColor = c_oAscCoAuthoringMeBorderColor;
  window['AscCommonExcel'].c_oAscCoAuthoringOtherBorderColor = c_oAscCoAuthoringOtherBorderColor;
  window['AscCommonExcel'].c_oAscCoAuthoringLockTablePropertiesBorderColor = c_oAscCoAuthoringLockTablePropertiesBorderColor;
  window['AscCommonExcel'].c_oAscCoAuthoringDottedWidth = c_oAscCoAuthoringDottedWidth;
  window['AscCommonExcel'].c_oAscCoAuthoringDottedDistance = c_oAscCoAuthoringDottedDistance;
  window['AscCommonExcel'].c_oAscFormulaRangeBorderColor = c_oAscFormulaRangeBorderColor;
  window['AscCommonExcel'].c_oAscLockNameFrozenPane = c_oAscLockNameFrozenPane;
  window['AscCommonExcel'].c_oAscLockNameTabColor = c_oAscLockNameTabColor;

  window['AscCommon'] = window['AscCommon'] || {};
  window['AscCommon'].c_oSerFormat = c_oSerFormat;
  window['AscCommon'].CurFileVersion = c_oSerFormat.Version;

  var prot;
  window['Asc'] = window['Asc'] || {};
  window['Asc']['c_oAscSortOptions'] = window['Asc'].c_oAscSortOptions = c_oAscSortOptions;
  prot = c_oAscSortOptions;
  prot['Ascending'] = prot.Ascending;
  prot['Descending'] = prot.Descending;
  prot['ByColorFill'] = prot.ByColorFill;
  prot['ByColorFont'] = prot.ByColorFont;
  window['Asc']['c_oAscConfirm'] = window['Asc'].c_oAscConfirm = c_oAscConfirm;
  prot = c_oAscConfirm;
  prot['ConfirmReplaceRange'] = prot.ConfirmReplaceRange;
  prot['ConfirmPutMergeRange'] = prot.ConfirmPutMergeRange;
  window['Asc']['c_oAscMergeOptions'] = window['Asc'].c_oAscMergeOptions = c_oAscMergeOptions;
  prot = c_oAscMergeOptions;
  prot['Unmerge'] = prot.Unmerge;
  prot['Merge'] = prot.Merge;
  prot['MergeCenter'] = prot.MergeCenter;
  prot['MergeAcross'] = prot.MergeAcross;
  window['Asc']['c_oAscBorderOptions'] = window['Asc'].c_oAscBorderOptions = c_oAscBorderOptions;
  prot = c_oAscBorderOptions;
  prot['Top'] = prot.Top;
  prot['Right'] = prot.Right;
  prot['Bottom'] = prot.Bottom;
  prot['Left'] = prot.Left;
  prot['DiagD'] = prot.DiagD;
  prot['DiagU'] = prot.DiagU;
  prot['InnerV'] = prot.InnerV;
  prot['InnerH'] = prot.InnerH;
  window['Asc']['c_oAscCleanOptions'] = window['Asc'].c_oAscCleanOptions = c_oAscCleanOptions;
  prot = c_oAscCleanOptions;
  prot['All'] = prot.All;
  prot['Text'] = prot.Text;
  prot['Format'] = prot.Format;
  prot['Formula'] = prot.Formula;
  prot['Comments'] = prot.Comments;
  prot['Hyperlinks'] = prot.Hyperlinks;
  window['Asc']['c_oAscSelectionDialogType'] = window['Asc'].c_oAscSelectionDialogType = c_oAscSelectionDialogType;
  prot = c_oAscSelectionDialogType;
  prot['None'] = prot.None;
  prot['FormatTable'] = prot.FormatTable;
  prot['Chart'] = prot.Chart;
  prot['DefinedName'] = prot.DefinedName;
  prot['FormatTableChangeRange'] = prot.FormatTableChangeRange;
  window['Asc']['c_oAscHyperlinkType'] = window['Asc'].c_oAscHyperlinkType = c_oAscHyperlinkType;
  prot = c_oAscHyperlinkType;
  prot['WebLink'] = prot.WebLink;
  prot['RangeLink'] = prot.RangeLink;
  window['Asc']['c_oAscMouseMoveType'] = window['Asc'].c_oAscMouseMoveType = c_oAscMouseMoveType;
  prot = c_oAscMouseMoveType;
  prot['None'] = prot.None;
  prot['Hyperlink'] = prot.Hyperlink;
  prot['Comment'] = prot.Comment;
  prot['LockedObject'] = prot.LockedObject;
  prot['ResizeColumn'] = prot.ResizeColumn;
  prot['ResizeRow'] = prot.ResizeRow;
  window['Asc']['c_oAscMouseMoveLockedObjectType'] = window['Asc'].c_oAscMouseMoveLockedObjectType = c_oAscMouseMoveLockedObjectType;
  prot = c_oAscMouseMoveLockedObjectType;
  prot['None'] = prot.None;
  prot['Range'] = prot.Range;
  prot['TableProperties'] = prot.TableProperties;
  prot['Sheet'] = prot.Sheet;
  window['Asc']['c_oAscPrintType'] = window['Asc'].c_oAscPrintType = c_oAscPrintType;
  prot = c_oAscPrintType;
  prot['ActiveSheets'] = prot.ActiveSheets;
  prot['EntireWorkbook'] = prot.EntireWorkbook;
  prot['Selection'] = prot.Selection;
  window['Asc']['c_oAscCustomAutoFilter'] = window['Asc'].c_oAscCustomAutoFilter = c_oAscCustomAutoFilter;
  prot = c_oAscCustomAutoFilter;
  prot['equals'] = prot.equals;
  prot['isGreaterThan'] = prot.isGreaterThan;
  prot['isGreaterThanOrEqualTo'] = prot.isGreaterThanOrEqualTo;
  prot['isLessThan'] = prot.isLessThan;
  prot['isLessThanOrEqualTo'] = prot.isLessThanOrEqualTo;
  prot['doesNotEqual'] = prot.doesNotEqual;
  prot['beginsWith'] = prot.beginsWith;
  prot['doesNotBeginWith'] = prot.doesNotBeginWith;
  prot['endsWith'] = prot.endsWith;
  prot['doesNotEndWith'] = prot.doesNotEndWith;
  prot['contains'] = prot.contains;
  prot['doesNotContain'] = prot.doesNotContain;
  window['Asc']['c_oAscDynamicAutoFilter'] = window['Asc'].c_oAscDynamicAutoFilter = c_oAscDynamicAutoFilter;
  prot = c_oAscDynamicAutoFilter;
  prot['aboveAverage'] = prot.aboveAverage;
  prot['belowAverage'] = prot.belowAverage;
  window['Asc']['c_oAscTop10AutoFilter'] = window['Asc'].c_oAscTop10AutoFilter = c_oAscTop10AutoFilter;
  prot = c_oAscTop10AutoFilter;
  prot['max'] = prot.max;
  prot['min'] = prot.min;
  window['Asc']['c_oAscChangeFilterOptions'] = window['Asc'].c_oAscChangeFilterOptions = c_oAscChangeFilterOptions;
  prot = c_oAscChangeFilterOptions;
  prot['filter'] = prot.filter;
  prot['style'] = prot.style;
  window['Asc']['c_oAscCellEditorState'] = window['Asc'].c_oAscCellEditorState = c_oAscCellEditorState;
  prot = c_oAscCellEditorState;
  prot['editEnd'] = prot.editEnd;
  prot['editStart'] = prot.editStart;
  prot['editEmptyCell'] = prot.editEmptyCell;
  prot['editText'] = prot.editText;
  prot['editFormula'] = prot.editFormula;
  window['Asc']['c_oAscChangeSelectionFormatTable'] = window['Asc'].c_oAscChangeSelectionFormatTable = c_oAscChangeSelectionFormatTable;
  prot = c_oAscChangeSelectionFormatTable;
  prot['all'] = prot.all;
  prot['data'] = prot.data;
  prot['row'] = prot.row;
  prot['column'] = prot.column;
  window['Asc']['c_oAscChangeTableStyleInfo'] = window['Asc'].c_oAscChangeTableStyleInfo = c_oAscChangeTableStyleInfo;
  prot = c_oAscChangeTableStyleInfo;
  prot['columnFirst'] = prot.columnFirst;
  prot['columnLast'] = prot.columnLast;
  prot['columnBanded'] = prot.columnBanded;
  prot['rowHeader'] = prot.rowHeader;
  prot['rowTotal'] = prot.rowTotal;
  prot['rowBanded'] = prot.rowBanded;
  prot['filterButton'] = prot.filterButton;
  window['Asc']['c_oAscAutoFilterTypes'] = window['Asc'].c_oAscAutoFilterTypes = c_oAscAutoFilterTypes;
  prot = c_oAscAutoFilterTypes;
  prot['ColorFilter'] = prot.ColorFilter;
  prot['CustomFilters'] = prot.CustomFilters;
  prot['DynamicFilter'] = prot.DynamicFilter;
  prot['Top10'] = prot.Top10;
  prot['Filters'] = prot.Filters;
  window['Asc']['c_oAscFindLookIn'] = window['Asc'].c_oAscFindLookIn = c_oAscFindLookIn;
  prot = c_oAscFindLookIn;
  prot['Formulas'] = prot.Formulas;
  prot['Value'] = prot.Value;
  prot['Annotations'] = prot.Annotations;
  window['Asc']['c_oAscGetDefinedNamesList'] = window['Asc'].c_oAscGetDefinedNamesList = c_oAscGetDefinedNamesList;
  prot = c_oAscGetDefinedNamesList;
  prot['Worksheet'] = prot.Worksheet;
  prot['WorksheetWorkbook'] = prot.WorksheetWorkbook;
  prot['All'] = prot.All;
  window['Asc']['c_oAscDefinedNameReason'] = window['Asc'].c_oAscDefinedNameReason = c_oAscDefinedNameReason;
  prot = c_oAscDefinedNameReason;
  prot['WrongName'] = prot.WrongName;
  prot['IsLocked'] = prot.IsLocked;
  prot['Existed'] = prot.Existed;
  prot['LockDefNameManager'] = prot.LockDefNameManager;
  prot['NameReserved'] = prot.NameReserved;
  prot['OK'] = prot.OK;
  window['Asc']['c_oAscPopUpSelectorType'] = window['Asc'].c_oAscPopUpSelectorType = c_oAscPopUpSelectorType;
  prot = c_oAscPopUpSelectorType;
  prot['None'] = prot.None;
  prot['Func'] = prot.Func;
  prot['Range'] = prot.Range;
  prot['Table'] = prot.Table;
})(window);

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
		// Import
		var c_oAscPrintDefaultSettings = AscCommon.c_oAscPrintDefaultSettings;
		var gc_nMaxRow0 = AscCommon.gc_nMaxRow0;
		var gc_nMaxCol0 = AscCommon.gc_nMaxCol0;
		var g_oCellAddressUtils = AscCommon.g_oCellAddressUtils;

		var c_oAscSelectionType = Asc.c_oAscSelectionType;


		/** @const */
		var kLeftLim1 = .999999999999999;
		var MAX_EXCEL_INT = 1e308;
		var MIN_EXCEL_INT = -MAX_EXCEL_INT;

		/** @const */
		var kUndefinedL = "undefined";
		/** @const */
		var kNullL = "null";
		/** @const */
		var kObjectL = "object";
		/** @const */
		var kFunctionL = "function";
		/** @const */
		var kNumberL = "number";
		/** @const */
		var kArrayL = "array";

		function applyFunction(callback) {
			if (kFunctionL === typeof callback)
				callback.apply(null, Array.prototype.slice.call(arguments, 1));
		}

		function typeOf(obj) {
			if (obj === undefined) {return kUndefinedL;}
			if (obj === null) {return kNullL;}
			return Object.prototype.toString.call(obj).slice(8, -1).toLowerCase();
		}

		function lastIndexOf(s, regExp, fromIndex) {
			var end = fromIndex >= 0 && fromIndex <= s.length ? fromIndex : s.length;
			for (var i = end - 1; i >= 0; --i) {
				var j = s.slice(i, end).search(regExp);
				if (j >= 0) {return i + j;}
			}
			return -1;
		}

		function search(arr, fn) {
			for (var i = 0; i < arr.length; ++i) {
				if ( fn(arr[i]) ) {return i;}
			}
			return -1;
		}

		function getUniqueRangeColor (arrRanges, curElem, tmpColors) {
			var colorIndex, j, range = arrRanges[curElem];
			for (j = 0; j < curElem; ++j) {
				if (range.isEqual(arrRanges[j])) {
					colorIndex = tmpColors[j];
					break;
				}
			}
			return colorIndex;
		}

		function getMinValueOrNull (val1, val2) {
			return null === val2 ? val1 : (null === val1 ? val2 : Math.min(val1, val2));
		}


		function round(x) {
			var y = x + (x >= 0 ? .5 : -.5);
			return y | y;
			//return Math.round(x);
		}

		function floor(x) {
			var y = x | x;
			y -= x < 0 && y > x ? 1 : 0;
			return y + (x - y > kLeftLim1 ? 1 : 0); // to fix float number precision caused by binary presentation
			//return Math.floor(x);
		}

		function ceil(x) {
			var y = x | x;
			y += x > 0 && y < x ? 1 : 0;
			return y - (y - x > kLeftLim1 ? 1 : 0); // to fix float number precision caused by binary presentation
			//return Math.ceil(x);
		}

		function incDecFonSize (bIncrease, oValue) {
			// Закон изменения размеров :
			// Результатом должно быть ближайшее из отрезка [8,72] по следующим числам 8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72
			// Если значение меньше или равно 8 и мы уменьшаем, то ничего не меняется
			// Если значение больше или равно 72 и мы увеличиваем, то ничего не меняется

			var aSizes = [8,9,10,11,12,14,16,18,20,22,24,26,28,36,48,72];
			var nLength = aSizes.length;
			var i;
			if (true === bIncrease) {
				if (oValue >= aSizes[nLength - 1])
					return null;
				for (i = 0; i < nLength; ++i)
					if (aSizes[i] > oValue)
						break;
			} else {
				if (oValue <= aSizes[0])
					return null;
				for (i = nLength - 1; i >= 0; --i)
					if (aSizes[i] < oValue)
						break;
			}

			return aSizes[i];
		}

		// Определяет времени работы функции
		function profileTime(fn/*[, arguments]*/) {
			var start, end, arg = [], i;
			if (arguments.length) {
				if (arguments.length > 1) {
					for (i = 1; i < arguments.length; ++i)
						arg.push(arguments[i]);
					start = new Date();
					fn.apply(window, arg);
					end = new Date();
				} else {
					start = new Date();
					fn();
					end = new Date();
				}
				return end.getTime() - start.getTime();
			}
			return undefined;
		}


		/**
		 * Rectangle region of cells
		 * @constructor
		 * @memberOf Asc
		 * @param c1 {Number} Left side of range.
		 * @param r1 {Number} Top side of range.
		 * @param c2 {Number} Right side of range (inclusively).
		 * @param r2 {Number} Bottom side of range (inclusively).
		 * @param normalize {Boolean=} Optional. If true, range will be converted to form (left,top) - (right,bottom).
		 * @return {Range}
		 */
		function Range(c1, r1, c2, r2, normalize) {
			if ( !(this instanceof Range) ) {return new Range(c1, r1, c2, r2, normalize);}

			/** @type Number */
			this.c1 = c1;
			/** @type Number */
			this.r1 = r1;
			/** @type Number */
			this.c2 = c2;
			/** @type Number */
			this.r2 = r2;
			this.r1Abs = false;
			this.c1Abs = false;
			this.r2Abs = false;
			this.c2Abs = false;

			return normalize ? this.normalize() : this;
		}

		Range.prototype = {

			constructor: Range,

			assign: function (c1, r1, c2, r2, normalize) {
				if (typeOf(c1) !== kNumberL || typeOf(c2) !== kNumberL ||
				    typeOf(r1) !== kNumberL || typeOf(r2) !== kNumberL) {
					throw "Error: range.assign("+c1+","+r1+","+c2+","+r2+") - numerical args are expected";
				}
				this.c1 = c1;
				this.r1 = r1;
				this.c2 = c2;
				this.r2 = r2;
				return normalize ? this.normalize() : this;
			},
			assign2: function (range) {
				return this.assign(range.c1, range.r1, range.c2, range.r2);
			},

			clone: function (normalize) {
			    var oRes = new Range(this.c1, this.r1, this.c2, this.r2, normalize);
			    oRes.r1Abs = this.r1Abs;
			    oRes.c1Abs = this.c1Abs;
			    oRes.r2Abs = this.r2Abs;
			    oRes.c2Abs = this.c2Abs;
			    return oRes;
			},

			normalize: function () {
				var tmp;
				if (this.c1 > this.c2){
					tmp = this.c1;
					this.c1 = this.c2;
					this.c2 = tmp;
				}
				if (this.r1 > this.r2){
					tmp = this.r1;
					this.r1 = this.r2;
					this.r2 = tmp;
				}
				return this;
			},

			isEqual: function (range) {
				return range && this.c1 === range.c1 && this.r1 === range.r1 && this.c2 === range.c2 && this.r2 === range.r2;
			},

			isEqualAll: function (range) {
			    return this.isEqual(range) && this.r1Abs === range.r1Abs && this.r2Abs === range.r2Abs && this.c1Abs === range.c1Abs && this.c2Abs === range.c2Abs;
			},

			contains: function (c, r) {
				return this.c1 <= c && c <= this.c2 && this.r1 <= r && r <= this.r2;
			},
			
			containsRange: function (range) {
				return this.contains(range.c1, range.r1) && this.contains(range.c2, range.r2);
			},

			containsFirstLineRange: function (range) {
				return this.contains(range.c1, range.r1) && this.contains(range.c2, range.r1);
			},

			intersection: function (range) {
				var s1 = this.clone(true),
				    s2 = range instanceof Range ? range.clone(true) :
				                                  new Range(range.c1, range.r1, range.c2, range.r2, true);

				if (s2.c1 > s1.c2 || s2.c2 < s1.c1 || s2.r1 > s1.r2 || s2.r2 < s1.r1) {return null;}

				return new Range(
						s2.c1 >= s1.c1 && s2.c1 <= s1.c2 ? s2.c1 : s1.c1,
						s2.r1 >= s1.r1 && s2.r1 <= s1.r2 ? s2.r1 : s1.r1,
						Math.min(s1.c2, s2.c2),
						Math.min(s1.r2, s2.r2));
			},
			
			intersectionSimple: function (range) {
				var oRes = null;
				var r1 = Math.max(this.r1, range.r1);
				var c1 = Math.max(this.c1, range.c1);
				var r2 = Math.min(this.r2, range.r2);
				var c2 = Math.min(this.c2, range.c2);
				if(r1 <= r2 && c1 <= c2)
					oRes = new Range(c1, r1, c2, r2);
				return oRes;
			},
			
			isIntersect: function (range) {
				var bRes = true;
				if(range.r2 < this.r1 || this.r2 < range.r1)
					bRes = false;
				else if(range.c2 < this.c1 || this.c2 < range.c1)
					bRes = false;
				return bRes;
			},

			isOneCell : function(){
				return this.r1 == this.r2 && this.c1 == this.c2;
			},

			union: function (range) {
				var s1 = this.clone(true),
				    s2 = range instanceof Range ? range.clone(true) :
				                                  new Range(range.c1, range.r1, range.c2, range.r2, true);

				return new Range(
						Math.min(s1.c1, s2.c1), Math.min(s1.r1, s2.r1),
						Math.max(s1.c2, s2.c2), Math.max(s1.r2, s2.r2));
			},
			
			union2: function (range) {
				this.c1 = Math.min(this.c1, range.c1);
				this.c2 = Math.max(this.c2, range.c2);
				this.r1 = Math.min(this.r1, range.r1);
				this.r2 = Math.max(this.r2, range.r2);
			},
			
			setOffset : function(offset){
                if ( this.r1 == 0 && this.r2 == gc_nMaxRow0 && offset.offsetRow != 0 || this.c1 == 0 && this.c2 == gc_nMaxCol0 && offset.offsetCol != 0 ) {
                    return;
                }
				this.setOffsetFirst(offset);
				this.setOffsetLast(offset);
			},

			setOffsetFirst : function(offset){
                this.c1 += offset.offsetCol;
                if( this.c1 < 0 ) {
                    this.c1 = 0;
                }
                if( this.c1 > gc_nMaxCol0 ) {
                    this.c1 = gc_nMaxCol0;
                }
                this.r1 += offset.offsetRow;
				if( this.r1 < 0 )
					this.r1 = 0;
                if( this.r1 > gc_nMaxRow0 )
                    this.r1 = gc_nMaxRow0;
			},

			setOffsetLast : function(offset){
				this.c2 += offset.offsetCol;
				if( this.c2 < 0 )
					this.c2 = 0;
                if( this.c2 > gc_nMaxCol0 )
					this.c2 = gc_nMaxCol0;
				this.r2 += offset.offsetRow;
				if( this.r2 < 0 )
					this.r2 = 0;
                if( this.r2 > gc_nMaxRow0 )
                    this.r2 = gc_nMaxRow0;
			},
			
			getName : function() {
			    var sRes = "";
			    if (0 == this.c1 && gc_nMaxCol0 == this.c2 && false == this.c1Abs && false == this.c2Abs) {
			        if (this.r1Abs)
			            sRes += "$";
			        sRes += (this.r1 + 1) + ":";
			        if (this.r2Abs)
			            sRes += "$";
			        sRes += (this.r2 + 1);
			    }
			    else if (0 == this.r1 && gc_nMaxRow0 == this.r2 && false == this.r1Abs && false == this.r2Abs) {
			        if (this.c1Abs)
			            sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1) + ":";
			        if (this.c2Abs)
			            sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
			    }
			    else {
			        if (this.c1Abs)
			            sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1);
			        if (this.r1Abs)
			            sRes += "$";
			        sRes += (this.r1 + 1);
			        if (!this.isOneCell()) {
			            sRes += ":";
			            if (this.c2Abs)
			                sRes += "$";
			            sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
			            if (this.r2Abs)
			                sRes += "$";
			            sRes += (this.r2 + 1);
			        }
			    }
			    return sRes;
			},

            getAbsName : function() {
			    var sRes = "";
			    if (0 == this.c1 && gc_nMaxCol0 == this.c2 && false == this.c1Abs && false == this.c2Abs) {
                    sRes += "$";
			        sRes += (this.r1 + 1) + ":";
                    sRes += "$";
			        sRes += (this.r2 + 1);
			    }
			    else if (0 == this.r1 && gc_nMaxRow0 == this.r2 && false == this.r1Abs && false == this.r2Abs) {
                    sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1) + ":";
                    sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
			    }
			    else {
                    sRes += "$";
			        sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1);
                    sRes += "$";
			        sRes += (this.r1 + 1);
			        if (!this.isOneCell()) {
			            sRes += ":";
		                sRes += "$";
			            sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
		                sRes += "$";
			            sRes += (this.r2 + 1);
			        }
			    }
			    return sRes;
			},

            getAbsName2 : function(absCol1,absRow1,absCol2,absRow2) {
                var sRes = "";
                if (0 == this.c1 && gc_nMaxCol0 == this.c2 && false == this.c1Abs && false == this.c2Abs) {
                    if (absRow1)
                        sRes += "$";
                    sRes += (this.r1 + 1) + ":";
                    if (absRow2)
                        sRes += "$";
                    sRes += (this.r2 + 1);
                }
                else if (0 == this.r1 && gc_nMaxRow0 == this.r2 && false == this.r1Abs && false == this.r2Abs) {
                    if (absCol1)
                        sRes += "$";
                    sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1) + ":";
                    if (absCol2)
                        sRes += "$";
                    sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
                }
                else {
                    if (absCol1)
                        sRes += "$";
                    sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1);
                    if (absRow1)
                        sRes += "$";
                    sRes += (this.r1 + 1);
                    if (!this.isOneCell()) {
                        sRes += ":";
                        if (absCol2)
                            sRes += "$";
                        sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
                        if (absRow2)
                            sRes += "$";
                        sRes += (this.r2 + 1);
                    }
                }
                return sRes;
            },

			getAllRange: function () {
				var result;
				if (c_oAscSelectionType.RangeMax === this.type)
					result = new Range(0, 0, gc_nMaxCol0, gc_nMaxRow0);
				else if (c_oAscSelectionType.RangeCol === this.type)
					result = new Range(this.c1, 0, this.c2, gc_nMaxRow0);
				else if (c_oAscSelectionType.RangeRow === this.type)
					result = new Range(0, this.r1, gc_nMaxCol0, this.r2);
				else
					result = this.clone();

				return result;
			}
		};

		/**
		 *
     * @constructor
		 * @extends {Range}
     */
		function Range3D() {
			this.sheet = '';

			if (2 == arguments.length) {
				var range = arguments[0];
				Range3D.superclass.constructor.call(this, range.c1, range.r1, range.c2, range.r2);
				// ToDo стоит пересмотреть конструкторы.
				this.r1Abs = range.r1Abs;
				this.c1Abs = range.c1Abs;
				this.r2Abs = range.r2Abs;
				this.c2Abs = range.c2Abs;

				this.sheet = arguments[1];
			} else if (arguments.length > 1) {
				ActiveRange.superclass.constructor.apply(this, arguments);
			} else {
				ActiveRange.superclass.constructor.call(this, 0, 0, 0, 0);
      }
		}
		AscCommon.extendClass(Range3D, Range);
		Range3D.prototype.isIntersect = function () {
			var oRes = true;
			
			if (2 == arguments.length) {
				oRes = this.sheet === arguments[1];
			}
			return oRes && Range3D.superclass.isIntersect.apply(this, arguments);
		};
		Range3D.prototype.clone = function(){
			var oRes = new Range3D(ActiveRange.superclass.clone.apply(this, arguments), this.sheet);
			return oRes;
		};

    /**
     *
     * @constructor
     * @extends {Range}
     */
		function ActiveRange(){
			if(1 == arguments.length)
			{
				var range = arguments[0];
				ActiveRange.superclass.constructor.call(this, range.c1, range.r1, range.c2, range.r2);
				// ToDo стоит пересмотреть конструкторы.
				this.r1Abs = range.r1Abs;
				this.c1Abs = range.c1Abs;
				this.r2Abs = range.r2Abs;
				this.c2Abs = range.c2Abs;
			}
			else if(arguments.length > 1)
				ActiveRange.superclass.constructor.apply(this, arguments);
			else
				ActiveRange.superclass.constructor.call(this, 0, 0, 0, 0);
			this.type = c_oAscSelectionType.RangeCells;
			this.startCol = 0; // Активная ячейка в выделении
			this.startRow = 0; // Активная ячейка в выделении
			this._updateAdditionalData();
		}
		AscCommon.extendClass(ActiveRange, Range);
		
		ActiveRange.prototype.assign = function () {
			ActiveRange.superclass.assign.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype.assign2 = function () {
			ActiveRange.superclass.assign2.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype.clone = function(){
			var oRes = new ActiveRange(ActiveRange.superclass.clone.apply(this, arguments));
			oRes.type = this.type;
			oRes.startCol = this.startCol;
			oRes.startRow = this.startRow;
			return oRes;
		};
		ActiveRange.prototype.normalize = function () {
			ActiveRange.superclass.normalize.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype.isEqualAll = function () {
			var bRes = ActiveRange.superclass.isEqual.apply(this, arguments);
			if(bRes && arguments.length > 0)
			{
				var range = arguments[0];
				bRes = this.type == range.type && this.startCol == range.startCol && this.startRow == range.startRow;
			}
			return bRes;
		};
		ActiveRange.prototype.contains = function () {
			return ActiveRange.superclass.contains.apply(this, arguments);
		};
		ActiveRange.prototype.containsRange = function () {
			return ActiveRange.superclass.containsRange.apply(this, arguments);
		};
		ActiveRange.prototype.containsFirstLineRange = function () {
			return ActiveRange.superclass.containsFirstLineRange.apply(this, arguments);
		};
		ActiveRange.prototype.intersection = function () {
			var oRes = ActiveRange.superclass.intersection.apply(this, arguments);
			if(null != oRes)
			{
				oRes = new ActiveRange(oRes);
				oRes._updateAdditionalData();
			}
			return oRes;
		};
		ActiveRange.prototype.intersectionSimple = function () {
			var oRes = ActiveRange.superclass.intersectionSimple.apply(this, arguments);
			if(null != oRes)
			{
				oRes = new ActiveRange(oRes);
				oRes._updateAdditionalData();
			}
			return oRes;
		};
		ActiveRange.prototype.union = function () {
			var oRes = new ActiveRange(ActiveRange.superclass.union.apply(this, arguments));
			oRes._updateAdditionalData();
			return oRes;
		};
		ActiveRange.prototype.union2 = function () {
			ActiveRange.superclass.union2.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype.setOffset = function(offset){
			this.setOffsetFirst(offset);
			this.setOffsetLast(offset);
		};
		ActiveRange.prototype.setOffsetFirst = function(offset){
			ActiveRange.superclass.setOffsetFirst.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype.setOffsetLast = function(offset){
			ActiveRange.superclass.setOffsetLast.apply(this, arguments);
			this._updateAdditionalData();
			return this;
		};
		ActiveRange.prototype._updateAdditionalData = function(){
			//меняем выделеную ячейку, если она не входит в диапазон
			//возможно, в будующем придется пределать логику, пока нет примеров, когда это работает плохо
			if(!this.contains(this.startCol, this.startRow))
			{
				this.startCol = this.c1;
				this.startRow = this.r1;
			}
			//не меняем тип выделения, если это не выделение ячееек
			// if(this.type == c_oAscSelectionType.RangeCells || this.type == c_oAscSelectionType.RangeCol ||
				// this.type == c_oAscSelectionType.RangeRow || this.type == c_oAscSelectionType.RangeMax)
			// {
				// if(0 == this.r1 && 0 == this.c1 && gc_nMaxRow0 == this.r2 && gc_nMaxCol0 == this.c2)
					// this.type = c_oAscSelectionType.RangeMax;
				// else if(0 == this.r1 && gc_nMaxRow0 == this.r2)
					// this.type = c_oAscSelectionType.RangeCol;
				// else if(0 == this.c1 && gc_nMaxCol0 == this.c2)
					// this.type = c_oAscSelectionType.RangeRow;
				// else
					// this.type = c_oAscSelectionType.RangeCells;
			// }
		};

    /**
     *
     * @constructor
     * @extends {Range}
     */
		function FormulaRange(){
			if(1 == arguments.length)
			{
				var range = arguments[0];
				FormulaRange.superclass.constructor.call(this, range.c1, range.r1, range.c2, range.r2);
			}
			else if(arguments.length > 1)
				FormulaRange.superclass.constructor.apply(this, arguments);
			else
				FormulaRange.superclass.constructor.call(this, 0, 0, 0, 0);
			this.r1Abs = false;
			this.c1Abs = false;
			this.r2Abs = false;
			this.c2Abs = false;
		}
		AscCommon.extendClass(FormulaRange, Range);
		FormulaRange.prototype.clone = function(){
			var oRes = new FormulaRange(FormulaRange.superclass.clone.apply(this, arguments));
			oRes.r1Abs = this.r1Abs;
			oRes.c1Abs = this.c1Abs;
			oRes.r2Abs = this.r2Abs;
			oRes.c2Abs = this.c2Abs;
			return oRes;
		};
		FormulaRange.prototype.intersection = function () {
			var oRes = FormulaRange.superclass.intersection.apply(this, arguments);
			if(null != oRes)
				oRes = new FormulaRange(oRes);
			return oRes;
		};
		FormulaRange.prototype.intersectionSimple = function () {
			var oRes = FormulaRange.superclass.intersectionSimple.apply(this, arguments);
			if(null != oRes)
				oRes = new FormulaRange(oRes);
			return oRes;
		};
		FormulaRange.prototype.union = function () {
			return new FormulaRange(FormulaRange.superclass.union.apply(this, arguments));
		};
		FormulaRange.prototype.getName = function () {
			var sRes = "";
			if(0 == this.c1 && gc_nMaxCol0 == this.c2)
			{
				if(this.r1Abs)
					sRes += "$";
				sRes += (this.r1 + 1) + ":";
				if(this.r2Abs)
					sRes += "$";
				sRes += (this.r2 + 1);
			}
			else if(0 == this.r1 && gc_nMaxRow0 == this.r2)
			{
				if(this.c1Abs)
					sRes += "$";
				sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1) + ":";
				if(this.c2Abs)
					sRes += "$";
				sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
			}
			else
			{
				if(this.c1Abs)
					sRes += "$";
				sRes += g_oCellAddressUtils.colnumToColstr(this.c1 + 1);
				if(this.r1Abs)
					sRes += "$";
				sRes += (this.r1 + 1);
				if(!this.isOneCell())
				{
					sRes += ":";
					if(this.c2Abs)
						sRes += "$";
					sRes += g_oCellAddressUtils.colnumToColstr(this.c2 + 1);
					if(this.r2Abs)
						sRes += "$";
					sRes += (this.r2 + 1);
				}
			}
			return sRes;
		};

		function MultiplyRange(ranges) {
			this.ranges = ranges;
		}
		MultiplyRange.prototype.isIntersect = function(range) {
			for (var i = 0; i < this.ranges.length; ++i) {
				if (range.isIntersect(this.ranges[i])) {
					return true;
				}
			}
			return false;
		};

		function VisibleRange(visibleRange, offsetX, offsetY) {
			this.visibleRange = visibleRange;
			this.offsetX = offsetX;
			this.offsetY = offsetY;
		}

		function RangeCache()
		{
			this.oCache = {};
		}
		RangeCache.prototype = {
			getAscRange : function(sRange)
			{
				return this._getRange(sRange, 1);
			},
			getRange3D : function(sRange)
			{
				var res = AscCommon.parserHelp.parse3DRef(sRange);
				if (!res) {
					return null;
				}
				var range = this._getRange(res.range, 1);
				return range ? new Range3D(range, res.sheet) : null;
			},
			getActiveRange : function(sRange)
			{
				return this._getRange(sRange, 2);
			},
			getFormulaRange : function(sRange)
			{
				return this._getRange(sRange, 3);
			},
			_getRange : function(sRange, type)
			{
				var oRes = null;
				var oCacheVal = this.oCache[sRange];
				if(null == oCacheVal)
				{
				    var oFirstAddr, oLastAddr;
				    var bIsSingle = true;
					var nIndex = sRange.indexOf(":");
					if(-1 != nIndex)
					{
					    bIsSingle = false;
						oFirstAddr = g_oCellAddressUtils.getCellAddress(sRange.substring(0, nIndex));
						oLastAddr = g_oCellAddressUtils.getCellAddress(sRange.substring(nIndex + 1));
					}
					else
						oFirstAddr = oLastAddr = g_oCellAddressUtils.getCellAddress(sRange);
					oCacheVal = { first: null, last: null, ascRange: null, formulaRange: null, activeRange: null };
                    //последнее условие, чтобы не распознавалось "A", "1"(должно быть "A:A", "1:1")
					if (oFirstAddr.isValid() && oLastAddr.isValid() && (!bIsSingle || (!oFirstAddr.getIsRow() && !oFirstAddr.getIsCol())))
					{
					    oCacheVal.first = oFirstAddr;
					    oCacheVal.last = oLastAddr;
					}
					this.oCache[sRange] = oCacheVal;
				}
				if (1 == type)
				    oRes = oCacheVal.ascRange;
				else if (2 == type)
				    oRes = oCacheVal.activeRange;
				else
				    oRes = oCacheVal.formulaRange;
				if (null == oRes && null != oCacheVal.first && null != oCacheVal.last) {
				    var r1 = oCacheVal.first.getRow0(), r2 = oCacheVal.last.getRow0(), c1 = oCacheVal.first.getCol0(), c2 = oCacheVal.last.getCol0();
				    if (oCacheVal.first.getIsRow() && oCacheVal.last.getIsRow()) {
				        c1 = 0;
				        c2 = gc_nMaxCol0;
				    }
				    if (oCacheVal.first.getIsCol() && oCacheVal.last.getIsCol()) {
				        r1 = 0;
				        r2 = gc_nMaxRow0;
				    }
				    if (r1 > r2) {
				        var temp = r1;
				        r1 = r2;
				        r2 = temp;
				    }
				    if (c1 > c2) {
				        var temp = c1;
				        c1 = c2;
				        c2 = temp;
				    }

				    if (1 == type) {
				        if (null == oCacheVal.ascRange) {
				            var oAscRange = new Range(c1, r1, c2, r2);
				            oAscRange.r1Abs = oCacheVal.first.getRowAbs();
				            oAscRange.c1Abs = oCacheVal.first.getColAbs();
				            oAscRange.r2Abs = oCacheVal.last.getRowAbs();
				            oAscRange.c2Abs = oCacheVal.last.getColAbs();
				            oCacheVal.ascRange = oAscRange;
				        }
				        oRes = oCacheVal.ascRange;
				    }
				    else if (2 == type) {
				        if (null == oCacheVal.activeRange) {
				            var oActiveRange = new ActiveRange(c1, r1, c2, r2);
				            oActiveRange.r1Abs = oCacheVal.first.getRowAbs();
				            oActiveRange.c1Abs = oCacheVal.first.getColAbs();
				            oActiveRange.r2Abs = oCacheVal.last.getRowAbs();
				            oActiveRange.c2Abs = oCacheVal.last.getColAbs();
				            var bCol = 0 == r1 && gc_nMaxRow0 == r2;
				            var bRow = 0 == c1 && gc_nMaxCol0 == c2;
				            if (bCol && bRow)
				                oActiveRange.type = c_oAscSelectionType.RangeMax;
				            else if (bCol)
				                oActiveRange.type = c_oAscSelectionType.RangeCol;
				            else if (bRow)
				                oActiveRange.type = c_oAscSelectionType.RangeRow;
				            else
				                oActiveRange.type = c_oAscSelectionType.RangeCells;
				            oActiveRange.startCol = oActiveRange.c1;
				            oActiveRange.startRow = oActiveRange.r1;
				            oCacheVal.activeRange = oActiveRange;
				        }
				        oRes = oCacheVal.activeRange;
				    }
				    else {
				        if (null == oCacheVal.formulaRange) {
				            var oFormulaRange = new FormulaRange(c1, r1, c2, r2);
				            oFormulaRange.r1Abs = oCacheVal.first.getRowAbs();
				            oFormulaRange.c1Abs = oCacheVal.first.getColAbs();
				            oFormulaRange.r2Abs = oCacheVal.last.getRowAbs();
				            oFormulaRange.c2Abs = oCacheVal.last.getColAbs();
				            oCacheVal.formulaRange = oFormulaRange;
				        }
				        oRes = oCacheVal.formulaRange;
				    }
				}
				return oRes;
			}
		};
		var g_oRangeCache = new RangeCache();
		/**
		 * @constructor
		 * @memberOf Asc
		 */
		function HandlersList(handlers) {
			if ( !(this instanceof HandlersList) ) {return new HandlersList(handlers);}
			this.handlers = handlers || {};
			return this;
		}

		HandlersList.prototype = {

			constructor: HandlersList,

			trigger: function (eventName) {
				var h = this.handlers[eventName], t = typeOf(h), a = Array.prototype.slice.call(arguments, 1), i;
				if (t === kFunctionL) {
					return h.apply(this, a);
				}
				if (t === kArrayL) {
					for (i = 0; i < h.length; i += 1) {
						if (typeOf(h[i]) === kFunctionL) {h[i].apply(this, a);}
					}
					return true;
				}
				return false;
			},

			add: function (eventName, eventHandler, replaceOldHandler) {
				var th = this.handlers, h, old, t;
				if (replaceOldHandler || !th.hasOwnProperty(eventName)) {
					th[eventName] = eventHandler;
				} else {
					old = h = th[eventName];
					t = typeOf(old);
					if (t !== kArrayL) {
						h = th[eventName] = [];
						if (t === kFunctionL) {h.push(old);}
					}
					h.push(eventHandler);
				}
			},

			remove: function (eventName, eventHandler) {
				var th = this.handlers, h = th[eventName], i;
				if (th.hasOwnProperty(eventName)) {
					if (typeOf(h) !== kArrayL || typeOf(eventHandler) !== kFunctionL) {
						delete th[eventName];
						return true;
					}
					for (i = h.length - 1; i >= 0; i -= 1) {
						if (h[i] === eventHandler) {
							delete h[i];
							return true;
						}
					}
				}
				return false;
			}

		};


		function outputDebugStr(channel) {
			var c = window.console;
			if (Asc.g_debug_mode && c && c[channel] && c[channel].apply) {
				c[channel].apply(this, Array.prototype.slice.call(arguments, 1));
			}
		}
		
		function trim(val)
		{
			if(!String.prototype.trim)
				return val.trim();
			else
				return val.replace(/^\s+|\s+$/g,'');  
		}

		function isNumberInfinity(val) {
		    var valTrim = trim(val);
		    var valInt = valTrim - 0;
		    return valInt == valTrim && valTrim.length > 0 && MIN_EXCEL_INT < valInt && valInt < MAX_EXCEL_INT;//
		}

		function arrayToLowerCase(array) {
			var result = [];
			for (var i = 0, length = array.length; i < length; ++i)
				result.push(array[i].toLowerCase());
			return result;
		}

		function isFixedWidthCell(frag) {
			for (var i = 0; i < frag.length; ++i) {
				var f = frag[i].format;
				if (f && f.repeat) {return true;}
			}
			return false;
		}

		function truncFracPart(frag) {
			var s = frag.reduce(function (prev,val) {return prev + val.text;}, "");
			// Проверка scientific format
			if (s.search(/E/i) >= 0) {
				return frag;
			}
			// Поиск десятичной точки
			var pos = s.search(/[,\.]/);
			if (pos >= 0) {
				frag[0].text = s.slice(0, pos);
				frag.splice(1, frag.length - 1);
			}
			return frag;
		}

		function getEndValueRange (dx, start, v1, v2) {
			var x1, x2;
			if (0 !== dx) {
				if (start === v1) {
					x1 = v1;
					x2 = v2;
				} else if (start === v2) {
					x1 = v2;
					x2 = v1;
				} else {
					if (0 > dx) {
						x1 = v2;
						x2 = v1;
					} else {
						x1 = v1;
						x2 = v2;
					}
				}
			} else {
				x1 = v1;
				x2 = v2;
			}
			return {x1: x1, x2: x2};
		}

		//-----------------------------------------------------------------
		// События движения мыши
		//-----------------------------------------------------------------
		/** @constructor */
		function asc_CMouseMoveData (obj) {
			if ( !(this instanceof asc_CMouseMoveData) ) {
				return new asc_CMouseMoveData(obj);
			}
			
			if (obj) {
				this.type = obj.type;
				this.x = obj.x;
				this.reverseX = obj.reverseX;	// Отображать комментарий слева от ячейки
				this.y = obj.y;
				this.hyperlink = obj.hyperlink;
				this.aCommentIndexes = obj.aCommentIndexes;
				this.userId = obj.userId;
				this.lockedObjectType = obj.lockedObjectType;

				// Для resize
				this.sizeCCOrPt = obj.sizeCCOrPt;
				this.sizePx = obj.sizePx;
			}

			return this;
		}
		asc_CMouseMoveData.prototype = {
			constructor: asc_CMouseMoveData,
			asc_getType: function () { return this.type; },
			asc_getX: function () { return this.x; },
			asc_getReverseX: function () { return this.reverseX; },
			asc_getY: function () { return this.y; },
			asc_getHyperlink: function () { return this.hyperlink; },
			asc_getCommentIndexes: function () { return this.aCommentIndexes; },
			asc_getUserId: function () { return this.userId; },
			asc_getLockedObjectType: function () { return this.lockedObjectType; },
			asc_getSizeCCOrPt: function () { return this.sizeCCOrPt; },
			asc_getSizePx: function () { return this.sizePx; }
		};

		// Гиперссылка
		/** @constructor */
		function asc_CHyperlink (obj) {
			if (!(this instanceof asc_CHyperlink)) {
				return new asc_CHyperlink(obj);
			}

			// Класс Hyperlink из модели
			this.hyperlinkModel = null != obj ? obj : new AscCommonExcel.Hyperlink();
			// Используется только для выдачи наружу и выставлении обратно
			this.text = null;

			return this;
		}
		asc_CHyperlink.prototype = {
			constructor: asc_CHyperlink,
			asc_getType: function () { return this.hyperlinkModel.getHyperlinkType(); },
			asc_getHyperlinkUrl: function () { return this.hyperlinkModel.Hyperlink; },
			asc_getTooltip: function () { return this.hyperlinkModel.Tooltip; },
			asc_getLocation: function () { return this.hyperlinkModel.getLocation(); },
			asc_getSheet: function () { return this.hyperlinkModel.LocationSheet; },
			asc_getRange: function () { return this.hyperlinkModel.LocationRange; },
			asc_getText: function () { return this.text; },

			asc_setType: function (val) {
				// В принципе эта функция избыточна
				switch (val) {
					case Asc.c_oAscHyperlinkType.WebLink:
						this.hyperlinkModel.setLocation(null);
						break;
					case Asc.c_oAscHyperlinkType.RangeLink:
						this.hyperlinkModel.Hyperlink = null;
						break;
				}
			},
			asc_setHyperlinkUrl: function (val) { this.hyperlinkModel.Hyperlink = val; },
			asc_setTooltip: function (val) { this.hyperlinkModel.Tooltip = val ? val.slice(0, Asc.c_oAscMaxTooltipLength) : val; },
			asc_setLocation: function (val) { this.hyperlinkModel.setLocation(val); },
			asc_setSheet: function (val) { this.hyperlinkModel.setLocationSheet(val); },
			asc_setRange: function (val) { this.hyperlinkModel.setLocationRange(val); },
			asc_setText: function (val) { this.text = val; }
		};

		/** @constructor */
		function asc_CPageMargins (obj) {
			if (obj) {
				this.left = obj.left;
				this.right = obj.right;
				this.top = obj.top;
				this.bottom = obj.bottom;
			}

			return this;
		}
		asc_CPageMargins.prototype.init = function () {
			if (null == this.left)
				this.left = c_oAscPrintDefaultSettings.PageLeftField;
			if (null == this.top)
				this.top = c_oAscPrintDefaultSettings.PageTopField;
			if (null == this.right)
				this.right = c_oAscPrintDefaultSettings.PageRightField;
			if (null == this.bottom)
				this.bottom = c_oAscPrintDefaultSettings.PageBottomField;
		};
		asc_CPageMargins.prototype.asc_getLeft = function () { return this.left; };
		asc_CPageMargins.prototype.asc_getRight = function () { return this.right; };
		asc_CPageMargins.prototype.asc_getTop = function () { return this.top; };
		asc_CPageMargins.prototype.asc_getBottom = function () { return this.bottom; };
		asc_CPageMargins.prototype.asc_setLeft = function (val) { this.left = val; };
		asc_CPageMargins.prototype.asc_setRight = function (val) { this.right = val; };
		asc_CPageMargins.prototype.asc_setTop = function (val) { this.top = val; };
		asc_CPageMargins.prototype.asc_setBottom = function (val) { this.bottom = val; };
		/** @constructor */
		function asc_CPageSetup () {
			this.orientation = c_oAscPrintDefaultSettings.PageOrientation;
			this.width = c_oAscPrintDefaultSettings.PageWidth;
			this.height = c_oAscPrintDefaultSettings.PageHeight;

			this.fitToWidth = false; //ToDo can be a number
			this.fitToHeight = false; //ToDo can be a number

			// ToDo
			this.blackAndWhite = false;
			this.cellComments = 0; // none ST_CellComments
			this.copies = 1;
			this.draft = false;
			this.errors = 0; // displayed ST_PrintError
			this.firstPageNumber = -1;
			this.pageOrder = 0; // downThenOver ST_PageOrder
			this.scale = 100;
			this.useFirstPageNumber = false;
			this.usePrinterDefaults = true;

			return this;
		}
		asc_CPageSetup.prototype.asc_getOrientation = function () { return this.orientation; };
		asc_CPageSetup.prototype.asc_getWidth = function () { return this.width; };
		asc_CPageSetup.prototype.asc_getHeight = function () { return this.height; };
		asc_CPageSetup.prototype.asc_setOrientation = function (val) { this.orientation = val; };
		asc_CPageSetup.prototype.asc_setWidth = function (val) { this.width = val; };
		asc_CPageSetup.prototype.asc_setHeight = function (val) { this.height = val; };
		asc_CPageSetup.prototype.asc_getFitToWidth = function () { return this.fitToWidth; };
		asc_CPageSetup.prototype.asc_getFitToHeight = function () { return this.fitToHeight; };
		asc_CPageSetup.prototype.asc_setFitToWidth = function (val) { this.fitToWidth = val; };
		asc_CPageSetup.prototype.asc_setFitToHeight = function (val) { this.fitToHeight = val; };

		/** @constructor */
		function asc_CPageOptions (obj) {
			if (obj) {
				this.pageMargins = obj.pageMargins;
				this.pageSetup = obj.pageSetup;
				this.gridLines = obj.gridLines;
				this.headings = obj.headings;
			}

			return this;
		}
		asc_CPageOptions.prototype.init = function () {
			if (!this.pageMargins)
				this.pageMargins = new asc_CPageMargins();
			this.pageMargins.init();

			if (!this.pageSetup)
				this.pageSetup = new asc_CPageSetup();

			if (null == this.gridLines)
				this.gridLines = c_oAscPrintDefaultSettings.PageGridLines;
			if (null == this.headings)
				this.headings = c_oAscPrintDefaultSettings.PageHeadings;
		};
		asc_CPageOptions.prototype.asc_getPageMargins = function () { return this.pageMargins; };
		asc_CPageOptions.prototype.asc_getPageSetup = function () { return this.pageSetup; };
		asc_CPageOptions.prototype.asc_getGridLines = function () { return this.gridLines; };
		asc_CPageOptions.prototype.asc_getHeadings = function () { return this.headings; };
		asc_CPageOptions.prototype.asc_setPageMargins = function (val) { this.pageMargins = val; };
		asc_CPageOptions.prototype.asc_setPageSetup = function (val) { this.pageSetup = val; };
		asc_CPageOptions.prototype.asc_setGridLines = function (val) { this.gridLines = val; };
		asc_CPageOptions.prototype.asc_setHeadings = function (val) { this.headings = val; };

		function CPagePrint () {
			this.pageWidth = 0;
			this.pageHeight = 0;

			this.pageClipRectLeft = 0;
			this.pageClipRectTop = 0;
			this.pageClipRectWidth = 0;
			this.pageClipRectHeight = 0;

			this.pageRange = null;

			this.leftFieldInPt = 0;
			this.topFieldInPt = 0;
			this.rightFieldInPt = 0;
			this.bottomFieldInPt = 0;

			this.pageGridLines = false;
			this.pageHeadings = false;

			this.indexWorksheet = -1;

			this.startOffset = 0;
			this.startOffsetPt = 0;

			return this;
		}
		function CPrintPagesData () {
			this.arrPages = null;
			this.currentIndex = 0;

			return this;
		}
		/** @constructor */
		function asc_CAdjustPrint () {
			// Вид печати
			this.printType = Asc.c_oAscPrintType.ActiveSheets;
			// ToDo сюда же start и end page index

			return this;
		}
		asc_CAdjustPrint.prototype.asc_getPrintType = function () { return this.printType; };
		asc_CAdjustPrint.prototype.asc_setPrintType = function (val) { this.printType = val; };

		/** @constructor */
		function asc_CLockInfo () {
			this["sheetId"] = null;
			this["type"] = null;
			this["subType"] = null;
			this["guid"] = null;
			this["rangeOrObjectId"] = null;
		}

		/** @constructor */
		function asc_CCollaborativeRange (c1, r1, c2, r2) {
			this["c1"] = c1;
			this["r1"] = r1;
			this["c2"] = c2;
			this["r2"] = r2;
		}

		var g_oCSheetViewSettingsProperties = {
				showGridLines		: 0,
				showRowColHeaders	: 1
			};
		/** @constructor */
		function asc_CSheetViewSettings () {
			this.Properties = g_oCSheetViewSettingsProperties;

			// Показывать ли сетку
			this.showGridLines = null;
			// Показывать обозначения строк и столбцов
			this.showRowColHeaders = null;

			// Закрепление области
			this.pane = null;

			return this;
		}

		asc_CSheetViewSettings.prototype = {
			constructor: asc_CSheetViewSettings,
			clone: function () {
				var result = new asc_CSheetViewSettings();
				result.showGridLines = this.showGridLines;
				result.showRowColHeaders = this.showRowColHeaders;
				if (this.pane)
					result.pane = this.pane.clone();
				return result;
			},
			isEqual: function (settings) {
				return this.asc_getShowGridLines() === settings.asc_getShowGridLines() &&
					this.asc_getShowRowColHeaders() === settings.asc_getShowRowColHeaders();
			},
			setSettings: function (settings) {
				this.showGridLines = settings.showGridLines;
				this.showRowColHeaders = settings.showRowColHeaders;
			},
			asc_getShowGridLines: function () { return false !== this.showGridLines; },
			asc_getShowRowColHeaders: function () { return false !== this.showRowColHeaders; },
			asc_getIsFreezePane: function () { return null !== this.pane && this.pane.isInit(); },
			asc_setShowGridLines: function (val) { this.showGridLines = val; },
			asc_setShowRowColHeaders: function (val) { this.showRowColHeaders = val; },
			getType : function () {
				return AscCommonExcel.UndoRedoDataTypes.SheetViewSettings;
			},
			getProperties : function () {
				return this.Properties;
			},
			getProperty : function (nType) {
				switch (nType) {
					case this.Properties.showGridLines: return this.showGridLines;break;
					case this.Properties.showRowColHeaders: return this.showRowColHeaders;break;
				}
			},
			setProperty : function (nType, value) {
				switch (nType) {
					case this.Properties.showGridLines: this.showGridLines = value;break;
					case this.Properties.showRowColHeaders: this.showRowColHeaders = value;break;
				}
			}
		};

		/** @constructor */
		function asc_CPane () {
			this.state = null;
			this.topLeftCell = null;
			this.xSplit = 0;
			this.ySplit = 0;
			// CellAddress для удобства
			this.topLeftFrozenCell = null;

			return this;
		}
		asc_CPane.prototype.isInit = function () {
			return null !== this.topLeftFrozenCell;
		};
		asc_CPane.prototype.clone = function() {
			var res = new asc_CPane();
			res.state = this.state;
			res.topLeftCell = this.topLeftCell;
			res.xSplit = this.xSplit;
			res.ySplit = this.ySplit;
			res.topLeftFrozenCell = this.topLeftFrozenCell ?
				new AscCommon.CellAddress(this.topLeftFrozenCell.row, this.topLeftFrozenCell.col) : null;
			return res;
		};
		asc_CPane.prototype.init = function() {
			// ToDo Обрабатываем пока только frozen и frozenSplit
			if ((AscCommonExcel.c_oAscPaneState.Frozen === this.state || AscCommonExcel.c_oAscPaneState.FrozenSplit === this.state) &&
				(0 < this.xSplit || 0 < this.ySplit)) {
				this.topLeftFrozenCell = new AscCommon.CellAddress(this.ySplit, this.xSplit, 0);
				if (!this.topLeftFrozenCell.isValid())
					this.topLeftFrozenCell = null;
			}
		};

		function RedoObjectParam () {
			this.bIsOn = false;
			this.bIsReInit = false;
			this.oChangeWorksheetUpdate = {};
			this.bUpdateWorksheetByModel = false;
			this.bOnSheetsChanged = false;
			this.oOnUpdateTabColor = {};
			this.oOnUpdateSheetViewSettings = {};
			this.bAddRemoveRowCol = false;
		}


    /** @constructor */
    function asc_CStylesPainter() {
      this.defaultStyles = null;
      this.docStyles = null;

      this.styleThumbnailWidth = 112;
      this.styleThumbnailHeight = 38;
      this.styleThumbnailWidthPt = this.styleThumbnailWidth * 72 / 96;
      this.styleThumbnailHeightPt = this.styleThumbnailHeight * 72 / 96;

      this.styleThumbnailWidthWithRetina = this.styleThumbnailWidth;
      this.styleThumbnailHeightWithRetina = this.styleThumbnailHeight;
      if (AscCommon.AscBrowser.isRetina) {
        this.styleThumbnailWidthWithRetina <<= 1;
        this.styleThumbnailHeightWithRetina <<= 1;
      }
    }

    asc_CStylesPainter.prototype = {
      constructor: asc_CStylesPainter,
      asc_getStyleThumbnailWidth: function() {
        return this.styleThumbnailWidthWithRetina;
      },
      asc_getStyleThumbnailHeight: function() {
        return this.styleThumbnailHeightWithRetina;
      },
      asc_getDefaultStyles: function() {
        return this.defaultStyles;
      },
      asc_getDocStyles: function() {
        return this.docStyles;
      },
      generateStylesAll: function(cellStylesAll, fmgrGraphics, oFont, stringRenderer) {
        this.generateDefaultStyles(cellStylesAll, fmgrGraphics, oFont, stringRenderer);
        this.generateDocumentStyles(cellStylesAll, fmgrGraphics, oFont, stringRenderer);
      },
      generateDefaultStyles: function(cellStylesAll, fmgrGraphics, oFont, stringRenderer) {
        var cellStyles = cellStylesAll.DefaultStyles;

        var oCanvas = document.createElement('canvas');
        oCanvas.width = this.styleThumbnailWidthWithRetina;
        oCanvas.height = this.styleThumbnailHeightWithRetina;
        var oGraphics = new Asc.DrawingContext({canvas: oCanvas, units: 1/*pt*/, fmgrGraphics: fmgrGraphics, font: oFont});

        var oStyle, oCustomStyle;
        this.defaultStyles = [];
        for (var i = 0; i < cellStyles.length; ++i) {
          oStyle = cellStyles[i];
          if (oStyle.Hidden) {
            continue;
          }
          // ToDo Возможно стоит переписать немного, чтобы не пробегать каждый раз по массиву custom-стилей (нужно генерировать AllStyles)
          oCustomStyle = cellStylesAll.getCustomStyleByBuiltinId(oStyle.BuiltinId);

          this.drawStyle(oGraphics, stringRenderer, oCustomStyle || oStyle, oStyle.Name);
          this.defaultStyles.push(new AscCommon.CStyleImage(oStyle.Name, AscCommon.c_oAscStyleImage.Default, oCanvas.toDataURL("image/png")));
        }
      },
      generateDocumentStyles: function(cellStylesAll, fmgrGraphics, oFont, stringRenderer) {
        var cellStyles = cellStylesAll.CustomStyles;

        var oCanvas = document.createElement('canvas');
        oCanvas.width = this.styleThumbnailWidthWithRetina;
        oCanvas.height = this.styleThumbnailHeightWithRetina;
        var oGraphics = new Asc.DrawingContext({canvas: oCanvas, units: 1/*pt*/, fmgrGraphics: fmgrGraphics, font: oFont});

        var oStyle;
        this.docStyles = [];
        for (var i = 0; i < cellStyles.length; ++i) {
          oStyle = cellStyles[i];
          if (oStyle.Hidden || null != oStyle.BuiltinId) {
            continue;
          }

          this.drawStyle(oGraphics, stringRenderer, oStyle, oStyle.Name);
          this.docStyles.push(new AscCommon.CStyleImage(oStyle.Name, AscCommon.c_oAscStyleImage.Document, oCanvas.toDataURL("image/png")));
        }
      },
      drawStyle: function(oGraphics, stringRenderer, oStyle, sStyleName) {
        oGraphics.clear();
        // Fill cell
        var oColor = oStyle.getFill();
        if (null !== oColor) {
          oGraphics.setFillStyle(oColor);
          oGraphics.fillRect(0, 0, this.styleThumbnailWidthPt, this.styleThumbnailHeightPt);
        }

        var drawBorder = function(b, x1, y1, x2, y2) {
          if (null != b && AscCommon.c_oAscBorderStyles.None !== b.s) {
            oGraphics.setStrokeStyle(b.c);

            // ToDo поправить
            oGraphics.setLineWidth(b.w).beginPath().moveTo(x1, y1).lineTo(x2, y2).stroke();
          }
        };

        // borders
        var oBorders = oStyle.getBorder();
        drawBorder(oBorders.l, 0, 0, 0, this.styleThumbnailHeightPt);
        drawBorder(oBorders.r, this.styleThumbnailWidthPt, 0, this.styleThumbnailWidthPt, this.styleThumbnailHeightPt);
        drawBorder(oBorders.t, 0, 0, this.styleThumbnailWidthPt, 0);
        drawBorder(oBorders.b, 0, this.styleThumbnailHeightPt, this.styleThumbnailWidthPt, this.styleThumbnailHeightPt);

        // Draw text
        var fc = oStyle.getFontColor();
        var oFontColor = fc !== null ? fc : new AscCommon.CColor(0, 0, 0);
        var format = oStyle.getFont();
        // Для размера шрифта делаем ограничение для превью в 16pt (у Excel 18pt, но и высота превью больше 22px)
        var oFont = new Asc.FontProperties(format.fn, (16 < format.fs) ? 16 : format.fs, format.b, format.i, format.u, format.s);

        var width_padding = 3; // 4 * 72 / 96

        var tm = stringRenderer.measureString(sStyleName);
        // Текст будем рисовать по центру (в Excel чуть по другому реализовано, у них постоянный отступ снизу)
        var textY = 0.5 * (this.styleThumbnailHeightPt - tm.height);
        oGraphics.setFont(oFont);
        oGraphics.setFillStyle(oFontColor);
        oGraphics.fillText(sStyleName, width_padding, textY + tm.baseline);
      }
    };

		/** @constructor */
		function asc_CSheetPr() {
			if (!(this instanceof asc_CSheetPr)) {
				return new asc_CSheetPr();
			}

			this.CodeName = null;
			this.EnableFormatConditionsCalculation = null;
			this.FilterMode = null;
			this.Published = null;
			this.SyncHorizontal = null;
			this.SyncRef = null;
			this.SyncVertical = null;
			this.TransitionEntry = null;
			this.TransitionEvaluation = null;

			this.TabColor = null;

			return this;
		}
		asc_CSheetPr.prototype.clone = function()  {
			var res = new asc_CSheetPr();

			res.CodeName = this.CodeName;
			res.EnableFormatConditionsCalculation = this.EnableFormatConditionsCalculation;
			res.FilterMode = this.FilterMode;
			res.Published = this.Published;
			res.SyncHorizontal = this.SyncHorizontal;
			res.SyncRef = this.SyncRef;
			res.SyncVertical = this.SyncVertical;
			res.TransitionEntry = this.TransitionEntry;
			res.TransitionEvaluation = this.TransitionEvaluation;
			if (this.TabColor)
				res.TabColor = this.TabColor.clone();

			return res;
		};

		// Математическая информация о выделении
		/** @constructor */
		function asc_CSelectionMathInfo() {
			this.count = 0;
			this.countNumbers = 0;
			this.sum = null;
			this.average = null;
			this.min = null;
			this.max = null;
		}

		asc_CSelectionMathInfo.prototype = {
			constructor: asc_CSelectionMathInfo,
			asc_getCount: function () { return this.count; },
			asc_getCountNumbers: function () { return this.countNumbers; },
			asc_getSum: function () { return this.sum; },
			asc_getAverage: function () { return this.average; },
			asc_getMin: function () { return this.min; },
			asc_getMax: function () { return this.max; }
		};

		/** @constructor */
		function asc_CFindOptions() {
			this.findWhat = "";							// текст, который ищем
			this.scanByRows = true;						// просмотр по строкам/столбцам
			this.scanForward = true;					// поиск вперед/назад
			this.isMatchCase = false;					// учитывать регистр
			this.isWholeCell = false;					// ячейка целиком
			this.scanOnOnlySheet = true;				// искать только на листе/в книге
			this.lookIn = Asc.c_oAscFindLookIn.Formulas;	// искать в формулах/значениях/примечаниях

			this.replaceWith = "";						// текст, на который заменяем (если у нас замена)
			this.isReplaceAll = false;					// заменить все (если у нас замена)

			// внутренние переменные
			this.activeRange = null;
			this.indexInArray = 0;
			this.countFind = 0;
			this.countReplace = 0;
			this.countFindAll = 0;
			this.countReplaceAll = 0;
			this.sheetIndex = -1;
		}
		asc_CFindOptions.prototype.clone = function () {
			var result = new asc_CFindOptions();
			result.findWhat = this.findWhat;
			result.scanByRows = this.scanByRows;
			result.scanForward = this.scanForward;
			result.isMatchCase = this.isMatchCase;
			result.isWholeCell = this.isWholeCell;
			result.scanOnOnlySheet = this.scanOnOnlySheet;
			result.lookIn = this.lookIn;

			result.replaceWith = this.replaceWith;
			result.isReplaceAll = this.isReplaceAll;

			result.activeRange = this.activeRange ? this.activeRange.clone() : null;
			result.indexInArray = this.indexInArray;
			result.countFind = this.countFind;
			result.countReplace = this.countReplace;
			result.countFindAll = this.countFindAll;
			result.countReplaceAll = this.countReplaceAll;
			result.sheetIndex = this.sheetIndex;
			return result;
		};
		asc_CFindOptions.prototype.isEqual = function (obj) {
			return null != obj && this.findWhat === obj.findWhat && this.scanByRows === obj.scanByRows &&
				this.scanForward === obj.scanForward && this.isMatchCase === obj.isMatchCase &&
				this.isWholeCell === obj.isWholeCell && this.scanOnOnlySheet === obj.scanOnOnlySheet &&
				this.lookIn === obj.lookIn;
		};
		asc_CFindOptions.prototype.clearFindAll = function () {
			this.countFindAll = 0;
			this.countReplaceAll = 0;
		};
		asc_CFindOptions.prototype.updateFindAll = function () {
			this.countFindAll += this.countFind;
			this.countReplaceAll += this.countReplace;
		};

		asc_CFindOptions.prototype.asc_setFindWhat = function (val) {this.findWhat = val;};
		asc_CFindOptions.prototype.asc_setScanByRows = function (val) {this.scanByRows = val;};
		asc_CFindOptions.prototype.asc_setScanForward = function (val) {this.scanForward = val;};
		asc_CFindOptions.prototype.asc_setIsMatchCase = function (val) {this.isMatchCase = val;};
		asc_CFindOptions.prototype.asc_setIsWholeCell = function (val) {this.isWholeCell = val;};
		asc_CFindOptions.prototype.asc_setScanOnOnlySheet = function (val) {this.scanOnOnlySheet = val;};
		asc_CFindOptions.prototype.asc_setLookIn = function (val) {this.lookIn = val;};
		asc_CFindOptions.prototype.asc_setReplaceWith = function (val) {this.replaceWith = val;};
		asc_CFindOptions.prototype.asc_setIsReplaceAll = function (val) {this.isReplaceAll = val;};

		/** @constructor */
		function asc_CCompleteMenu(name, type) {
			this.name = name;
			this.type = type;
		}
		asc_CCompleteMenu.prototype.asc_getName = function () {return this.name;};
		asc_CCompleteMenu.prototype.asc_getType = function () {return this.type;};

		/*
		 * Export
		 * -----------------------------------------------------------------------------
		 */
		var prot;
		window['Asc'] = window['Asc'] || {};
		window['AscCommonExcel'] = window['AscCommonExcel'] || {};
		window["AscCommonExcel"].applyFunction = applyFunction;
		window["Asc"].typeOf = typeOf;
		window["Asc"].lastIndexOf = lastIndexOf;
		window["Asc"].search = search;
		window["Asc"].getUniqueRangeColor = getUniqueRangeColor;
		window["Asc"].getMinValueOrNull = getMinValueOrNull;
		window["Asc"].round = round;
		window["Asc"].floor = floor;
		window["Asc"].ceil = ceil;
		window["Asc"].incDecFonSize = incDecFonSize;
		window["Asc"].outputDebugStr = outputDebugStr;
		window["Asc"].profileTime = profileTime;
		window["Asc"].isNumberInfinity = isNumberInfinity;
		window["Asc"].trim = trim;
		window["Asc"].arrayToLowerCase = arrayToLowerCase;
		window["Asc"].isFixedWidthCell = isFixedWidthCell;
		window["Asc"].truncFracPart = truncFracPart;
		window["Asc"].getEndValueRange = getEndValueRange;

		window["Asc"].Range = Range;
		window["AscCommonExcel"].Range3D = Range3D;
		window["AscCommonExcel"].ActiveRange = ActiveRange;
		window["AscCommonExcel"].FormulaRange = FormulaRange;
		window["AscCommonExcel"].MultiplyRange = MultiplyRange;
		window["AscCommonExcel"].VisibleRange = VisibleRange;
		window["AscCommonExcel"].g_oRangeCache = g_oRangeCache;

		window["AscCommonExcel"].HandlersList = HandlersList;

		window["AscCommonExcel"].RedoObjectParam = RedoObjectParam;

		window["AscCommonExcel"].asc_CMouseMoveData = asc_CMouseMoveData;
		prot = asc_CMouseMoveData.prototype;
		prot["asc_getType"] = prot.asc_getType;
		prot["asc_getX"] = prot.asc_getX;
		prot["asc_getReverseX"] = prot.asc_getReverseX;
		prot["asc_getY"] = prot.asc_getY;
		prot["asc_getHyperlink"] = prot.asc_getHyperlink;		
		prot["asc_getCommentIndexes"] = prot.asc_getCommentIndexes;
		prot["asc_getUserId"] = prot.asc_getUserId;
		prot["asc_getLockedObjectType"] = prot.asc_getLockedObjectType;
		prot["asc_getSizeCCOrPt"] = prot.asc_getSizeCCOrPt;
		prot["asc_getSizePx"] = prot.asc_getSizePx;

		window["Asc"]["asc_CHyperlink"] = window["Asc"].asc_CHyperlink = asc_CHyperlink;
		prot = asc_CHyperlink.prototype;
		prot["asc_getType"] = prot.asc_getType;
		prot["asc_getHyperlinkUrl"] = prot.asc_getHyperlinkUrl;
		prot["asc_getTooltip"] = prot.asc_getTooltip;
		prot["asc_getLocation"] = prot.asc_getLocation;
		prot["asc_getSheet"] = prot.asc_getSheet;
		prot["asc_getRange"] = prot.asc_getRange;
		prot["asc_getText"] = prot.asc_getText;
		prot["asc_setType"] = prot.asc_setType;
		prot["asc_setHyperlinkUrl"] = prot.asc_setHyperlinkUrl;
		prot["asc_setTooltip"] = prot.asc_setTooltip;
		prot["asc_setLocation"] = prot.asc_setLocation;
		prot["asc_setSheet"] = prot.asc_setSheet;
		prot["asc_setRange"] = prot.asc_setRange;
		prot["asc_setText"] = prot.asc_setText;

		window["Asc"]["asc_CPageMargins"] = window["Asc"].asc_CPageMargins = asc_CPageMargins;
		prot = asc_CPageMargins.prototype;
		prot["asc_getLeft"] = prot.asc_getLeft;
		prot["asc_getRight"] = prot.asc_getRight;
		prot["asc_getTop"] = prot.asc_getTop;
		prot["asc_getBottom"] = prot.asc_getBottom;
		prot["asc_setLeft"] = prot.asc_setLeft;
		prot["asc_setRight"] = prot.asc_setRight;
		prot["asc_setTop"] = prot.asc_setTop;
		prot["asc_setBottom"] = prot.asc_setBottom;

		window["Asc"]["asc_CPageSetup"] = window["Asc"].asc_CPageSetup = asc_CPageSetup;
		prot = asc_CPageSetup.prototype;
		prot["asc_getOrientation"] = prot.asc_getOrientation;
		prot["asc_getWidth"] = prot.asc_getWidth;
		prot["asc_getHeight"] = prot.asc_getHeight;
		prot["asc_setOrientation"] = prot.asc_setOrientation;
		prot["asc_setWidth"] = prot.asc_setWidth;
		prot["asc_setHeight"] = prot.asc_setHeight;
		prot["asc_getFitToWidth"] = prot.asc_getFitToWidth;
		prot["asc_getFitToHeight"] = prot.asc_getFitToHeight;
		prot["asc_setFitToWidth"] = prot.asc_setFitToWidth;
		prot["asc_setFitToHeight"] = prot.asc_setFitToHeight;

		window["Asc"]["asc_CPageOptions"] = window["Asc"].asc_CPageOptions = asc_CPageOptions;
		prot = asc_CPageOptions.prototype;
		prot["asc_getPageMargins"] = prot.asc_getPageMargins;
		prot["asc_getPageSetup"] = prot.asc_getPageSetup;
		prot["asc_getGridLines"] = prot.asc_getGridLines;
		prot["asc_getHeadings"] = prot.asc_getHeadings;
		prot["asc_setPageMargins"] = prot.asc_setPageMargins;
		prot["asc_setPageSetup"] = prot.asc_setPageSetup;
		prot["asc_setGridLines"] = prot.asc_setGridLines;
		prot["asc_setHeadings"] = prot.asc_setHeadings;

		window["AscCommonExcel"].CPagePrint = CPagePrint;
		window["AscCommonExcel"].CPrintPagesData = CPrintPagesData;

		window["Asc"]["asc_CAdjustPrint"] = window["Asc"].asc_CAdjustPrint = asc_CAdjustPrint;
		prot = asc_CAdjustPrint.prototype;
		prot["asc_getPrintType"] = prot.asc_getPrintType;
		prot["asc_setPrintType"] = prot.asc_setPrintType;

		window["AscCommonExcel"].asc_CLockInfo = asc_CLockInfo;

		window["AscCommonExcel"].asc_CCollaborativeRange = asc_CCollaborativeRange;

		window["AscCommonExcel"].asc_CSheetViewSettings = asc_CSheetViewSettings;
		prot = asc_CSheetViewSettings.prototype;
		prot["asc_getShowGridLines"] = prot.asc_getShowGridLines;
		prot["asc_getShowRowColHeaders"] = prot.asc_getShowRowColHeaders;
		prot["asc_getIsFreezePane"] = prot.asc_getIsFreezePane;
		prot["asc_setShowGridLines"] = prot.asc_setShowGridLines;
		prot["asc_setShowRowColHeaders"] = prot.asc_setShowRowColHeaders;

		window["AscCommonExcel"].asc_CPane = asc_CPane;

		window["AscCommonExcel"].asc_CStylesPainter = asc_CStylesPainter;
		prot = asc_CStylesPainter.prototype;
		prot["asc_getStyleThumbnailWidth"] = prot.asc_getStyleThumbnailWidth;
		prot["asc_getStyleThumbnailHeight"] = prot.asc_getStyleThumbnailHeight;
		prot["asc_getDefaultStyles"] = prot.asc_getDefaultStyles;
		prot["asc_getDocStyles"] = prot.asc_getDocStyles;

		window["AscCommonExcel"].asc_CSheetPr = asc_CSheetPr;

		window["AscCommonExcel"].asc_CSelectionMathInfo = asc_CSelectionMathInfo;
		prot = asc_CSelectionMathInfo.prototype;
		prot["asc_getCount"] = prot.asc_getCount;
		prot["asc_getCountNumbers"] = prot.asc_getCountNumbers;
		prot["asc_getSum"] = prot.asc_getSum;
		prot["asc_getAverage"] = prot.asc_getAverage;
		prot["asc_getMin"] = prot.asc_getMin;
		prot["asc_getMax"] = prot.asc_getMax;

		window["Asc"]["asc_CFindOptions"] = window["Asc"].asc_CFindOptions = asc_CFindOptions;
		prot = asc_CFindOptions.prototype;
		prot["asc_setFindWhat"] = prot.asc_setFindWhat;
		prot["asc_setScanByRows"] = prot.asc_setScanByRows;
		prot["asc_setScanForward"] = prot.asc_setScanForward;
		prot["asc_setIsMatchCase"] = prot.asc_setIsMatchCase;
		prot["asc_setIsWholeCell"] = prot.asc_setIsWholeCell;
		prot["asc_setScanOnOnlySheet"] = prot.asc_setScanOnOnlySheet;
		prot["asc_setLookIn"] = prot.asc_setLookIn;
		prot["asc_setReplaceWith"] = prot.asc_setReplaceWith;
		prot["asc_setIsReplaceAll"] = prot.asc_setIsReplaceAll;

		window["AscCommonExcel"].asc_CCompleteMenu = asc_CCompleteMenu;
		prot = asc_CCompleteMenu.prototype;
		prot["asc_getName"] = prot.asc_getName;
		prot["asc_getType"] = prot.asc_getType;
})(window);

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
		/*
		 * Import
		 * -----------------------------------------------------------------------------
		*/
		var asc = window["Asc"],
			asc_typeOf = asc.typeOf;


		/** @constructor */
		function asc_CHandlersList(handlers) {
			this.handlers = handlers || {};
			return this;
		}

		asc_CHandlersList.prototype.hasTrigger = function (eventName) {
			return null != this.handlers[eventName];
		};

		asc_CHandlersList.prototype.trigger = function (eventName) {
			var h = this.handlers[eventName], t = asc_typeOf(h), a = Array.prototype.slice.call(arguments, 1), i;
			if (t === "function") {
				return h.apply(this, a);
			}
			if (t === "array") {
				for (i = 0; i < h.length; i += 1) {
					if (asc_typeOf(h[i]) === "function") {h[i].apply(this, a);}
				}
				return true;
			}
			return false;
		};
		asc_CHandlersList.prototype.add = function (eventName, eventHandler, replaceOldHandler) {
			var th = this.handlers, h, old, t;
			if (replaceOldHandler || !th.hasOwnProperty(eventName)) {
				th[eventName] = eventHandler;
			} else {
				old = h = th[eventName];
				t = asc_typeOf(old);
				if (t !== "array") {
					h = th[eventName] = [];
					if (t === "function") {h.push(old);}
				}
				h.push(eventHandler);
			}
		};
		asc_CHandlersList.prototype.remove = function (eventName, eventHandler) {
			var th = this.handlers, h = th[eventName], i;
			if (th.hasOwnProperty(eventName)) {
				if (asc_typeOf(h) !== "array" || asc_typeOf(eventHandler) !== "function") {
					delete th[eventName];
					return true;
				}
				for (i = h.length - 1; i >= 0; i -= 1) {
					if (h[i] === eventHandler) {
						delete h[i];
						return true;
					}
				}
			}
			return false;
		};

		//---------------------------------------------------------export---------------------------------------------------
		window['AscCommonExcel'] = window['AscCommonExcel'] || {};
		AscCommonExcel.asc_CHandlersList = asc_CHandlersList;
	}
)(window);
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

(function (window, undefined) {
		/*
		 * Import
		 * -----------------------------------------------------------------------------
		 */
		var asc_applyFunction	= AscCommonExcel.applyFunction;
		var asc_Range			= Asc.Range;

		var c_oAscLockTypes = AscCommon.c_oAscLockTypes;

		var c_oAscRecalcIndexTypes = AscCommonExcel.c_oAscRecalcIndexTypes;
		var c_oAscLockTypeElemSubType = AscCommonExcel.c_oAscLockTypeElemSubType;
		var c_oAscLockTypeElem = AscCommonExcel.c_oAscLockTypeElem;

		/**
		 * Отвечает за совместное редактирование
		 * -----------------------------------------------------------------------------
		 *
		 * @constructor
		 * @memberOf AscCommonExcel
		 */
		function CCollaborativeEditing (handlers, isViewerMode) {
			if ( !(this instanceof CCollaborativeEditing) ) {
				return new CCollaborativeEditing ();
			}

			this.m_nUseType					= 1;  // 1 - 1 клиент и мы сохраняем историю, -1 - несколько клиентов, 0 - переход из -1 в 1

			this.handlers					= new AscCommonExcel.asc_CHandlersList(handlers);
			this.m_bIsViewerMode			= !!isViewerMode; // Режим Viewer-а
			this.m_bGlobalLock				= false; // Глобальный lock
			this.m_bGlobalLockEditCell		= false; // Глобальный lock (для редактирования ячейки) - отключаем смену select-а, но разрешаем сразу вводить
			this.m_arrCheckLocks			= [];    // Массив для проверки залоченности объектов, которые мы собираемся изменять

			this.m_arrNeedUnlock			= []; // Массив со списком залоченных объектов(которые были залочены другими пользователями)
			this.m_arrNeedUnlock2			= []; // Массив со списком залоченных объектов(которые были залочены на данном клиенте)

			this.m_arrChanges				= []; // Массив с изменениями других пользователей

			this.m_oRecalcIndexColumns		= {};
			this.m_oRecalcIndexRows			= {};

			this.m_oInsertColumns			= {}; // Массив листов с массивами списков добавленных колонок
			this.m_oInsertRows				= {}; // Массив листов с массивами списков добавленных строк

      this.m_bFast  = false;

			this.init();

			return this;
		}

		CCollaborativeEditing.prototype.init = function () {
		};

		// Очищаем индексы пересчета (при открытии это необходимо)
		CCollaborativeEditing.prototype.clearRecalcIndex = function () {
			delete this.m_oRecalcIndexColumns;
			delete this.m_oRecalcIndexRows;
			this.m_oRecalcIndexColumns = {};
			this.m_oRecalcIndexRows = {};
		};

		// Начало совместного редактирования
		CCollaborativeEditing.prototype.startCollaborationEditing = function() {
			this.m_nUseType = -1;
		};

		// Временное окончание совместного редактирования
		CCollaborativeEditing.prototype.endCollaborationEditing = function() {
			if (this.m_nUseType <= 0)
				this.m_nUseType = 0;
		};

		// Выставление режима view
		CCollaborativeEditing.prototype.setViewerMode = function (isViewerMode) {
			this.m_bIsViewerMode = isViewerMode;
		};

  CCollaborativeEditing.prototype.setFast = function (bFast) {
    return this.m_bFast = bFast;
  };
  CCollaborativeEditing.prototype.getFast = function () {
    return this.m_bFast;
  };
		CCollaborativeEditing.prototype.getCollaborativeEditing = function () {
			if (this.m_bIsViewerMode)
				return false;
			return 1 !== this.m_nUseType;
		};

  CCollaborativeEditing.prototype.haveOtherChanges = function () {
    return 0 < this.m_arrChanges.length;
  };

		CCollaborativeEditing.prototype.getOwnLocksLength = function () {
			return this.m_arrNeedUnlock2.length;
		};

		//-----------------------------------------------------------------------------------
		// Функции для проверки залоченности объектов
		//-----------------------------------------------------------------------------------
		CCollaborativeEditing.prototype.getGlobalLock = function () {
			return this.m_bGlobalLock;
		};
		CCollaborativeEditing.prototype.getGlobalLockEditCell = function () {
			return this.m_bGlobalLockEditCell;
		};
		CCollaborativeEditing.prototype.onStartEditCell = function () {
			// Вызывать эту функцию только в случае редактирования ячейки и если мы не одни редактируем!!!
			if (this.getCollaborativeEditing())
				this.m_bGlobalLockEditCell = true;
		};
		CCollaborativeEditing.prototype.onStopEditCell = function () {
			// Вызывать эту функцию только в случае окончания редактирования ячейки!!!
			this.m_bGlobalLockEditCell = false;
		};
		CCollaborativeEditing.prototype.onStartCheckLock = function () {
			this.m_arrCheckLocks.length = 0;
		};
		CCollaborativeEditing.prototype.addCheckLock = function (oItem) {
			this.m_arrCheckLocks.push (oItem);
		};
		CCollaborativeEditing.prototype.onEndCheckLock = function (callback) {
			var t = this;
			if (this.m_arrCheckLocks.length > 0) {
				// Отправляем запрос на сервер со списком элементов
				this.handlers.trigger("askLock", this.m_arrCheckLocks, function (result) {t.onCallbackAskLock (result, callback);});

				if (undefined !== callback) {
					// Ставим глобальный лок (только если мы не одни и ждем ответа!)
					this.m_bGlobalLock = true;
				}
			}
			else {
				asc_applyFunction(callback, true);

				// Снимаем глобальный лок (для редактирования ячейки)
				this.m_bGlobalLockEditCell = false;
			}
		};

		CCollaborativeEditing.prototype.onCallbackAskLock = function(result, callback) {
			// Снимаем глобальный лок
			this.m_bGlobalLock = false;
			// Снимаем глобальный лок (для редактирования ячейки)
			this.m_bGlobalLockEditCell = false;

			if (result["lock"]) {
				// Пробегаемся по массиву и проставляем, что залочено нами
				var count = this.m_arrCheckLocks.length;
				for (var i = 0; i < count; ++i) {
					var oItem = this.m_arrCheckLocks[i];

					if (true !== oItem && false !== oItem) // сравниваем по значению и типу обязательно
					{
						var oNewLock = new CLock(oItem);
						oNewLock.setType (c_oAscLockTypes.kLockTypeMine);
						this.addUnlock2 (oNewLock);
					}
				}

				asc_applyFunction(callback, true);
			} else if (result["error"]) {
				asc_applyFunction(callback, false);
			}
		};
		CCollaborativeEditing.prototype.addUnlock = function (LockClass) {
			this.m_arrNeedUnlock.push (LockClass);
		};
		CCollaborativeEditing.prototype.addUnlock2 = function (Lock) {
			this.m_arrNeedUnlock2.push (Lock);
			this.handlers.trigger("updateDocumentCanSave");
		};

		CCollaborativeEditing.prototype.removeUnlock = function (Lock) {
			for (var i = 0; i < this.m_arrNeedUnlock.length; ++i)
				if (Lock.Element["guid"] === this.m_arrNeedUnlock[i].Element["guid"]) {
					this.m_arrNeedUnlock.splice(i, 1);
					return true;
				}
			return false;
		};

		CCollaborativeEditing.prototype.addChanges = function (oChanges) {
			this.m_arrChanges.push (oChanges);
		};

		// Возвращает - нужно ли отправлять end action
		CCollaborativeEditing.prototype.applyChanges = function () {
			var t = this;
			var length = this.m_arrChanges.length;
			// Принимаем изменения
			if (0 < length) {
				this.handlers.trigger("applyChanges", this.m_arrChanges, function () {
					t.m_arrChanges.splice(0, length);
					t.handlers.trigger("updateAfterApplyChanges");
				});

				return false;
			}

			return true;
		};

		CCollaborativeEditing.prototype.sendChanges = function (IsUserSave) {
			// Когда не совместное редактирование чистить ничего не нужно, но отправлять нужно.
			var bIsCollaborative = this.getCollaborativeEditing();

			var bCheckRedraw = false,
                bRedrawGraphicObjects = false,
                bUnlockDefName = false,
                dN;
			if (bIsCollaborative && (0 < this.m_arrNeedUnlock.length ||
				0 < this.m_arrNeedUnlock2.length)) {
				bCheckRedraw = true;
				this.handlers.trigger("cleanSelection");
			}

			var oLock = null;
			// Очищаем свои изменения
			while (bIsCollaborative && 0 < this.m_arrNeedUnlock2.length) {
				oLock = this.m_arrNeedUnlock2.shift();
				oLock.setType(c_oAscLockTypes.kLockTypeNone, false);

                var drawing = AscCommon.g_oTableId.Get_ById(oLock.Element["rangeOrObjectId"]);
                if(drawing && drawing.lockType !== c_oAscLockTypes.kLockTypeNone) {
                    drawing.lockType = c_oAscLockTypes.kLockTypeNone;
                    bRedrawGraphicObjects = true;
                }
                if(!bUnlockDefName){
                    bUnlockDefName = this.handlers.trigger("checkDefNameLock", oLock);
                }

				this.handlers.trigger("releaseLocks", oLock.Element["guid"]);
			}
			// Очищаем примененные чужие изменения
			var nIndex = 0;
			var nCount = this.m_arrNeedUnlock.length;
			for (;bIsCollaborative && nIndex < nCount; ++nIndex) {
				oLock = this.m_arrNeedUnlock[nIndex];
				if (c_oAscLockTypes.kLockTypeOther2 === oLock.getType()) {
					if (!this.handlers.trigger("checkCommentRemoveLock", oLock.Element)) {
						drawing = AscCommon.g_oTableId.Get_ById(oLock.Element["rangeOrObjectId"]);
						if(drawing && drawing.lockType !== c_oAscLockTypes.kLockTypeNone) {
							drawing.lockType = c_oAscLockTypes.kLockTypeNone;
							bRedrawGraphicObjects = true;
						}
                        if(!bUnlockDefName){
                            bUnlockDefName = this.handlers.trigger("checkDefNameLock", oLock);
                        }
					}

					this.m_arrNeedUnlock.splice(nIndex, 1);
					--nIndex;
					--nCount;
				}
			}

			// Отправляем на сервер изменения
			this.handlers.trigger("sendChanges", this.getRecalcIndexSave(this.m_oRecalcIndexColumns), this.getRecalcIndexSave(this.m_oRecalcIndexRows));

			if (bIsCollaborative) {
				// Пересчитываем lock-и от чужих пользователей
				this._recalcLockArrayOthers();

				// Очищаем свои изменения (удаляем массив добавленных строк/столбцов)
				delete this.m_oInsertColumns;
				delete this.m_oInsertRows;
				this.m_oInsertColumns = {};
				this.m_oInsertRows = {};
				// Очищаем свои пересчетные индексы
				this.clearRecalcIndex();

				// Чистим Undo/Redo
				AscCommon.History.Clear();

				// Перерисовываем
				if (bCheckRedraw) {
					this.handlers.trigger("drawSelection");
					this.handlers.trigger("drawFrozenPaneLines");
					this.handlers.trigger("updateAllSheetsLock");
					this.handlers.trigger("showComments");
				}

				if (bCheckRedraw || bRedrawGraphicObjects)
					this.handlers.trigger("showDrawingObjects");

//                if(bUnlockDefName){
                    this.handlers.trigger("unlockDefName");
//                }

				if (0 === this.m_nUseType)
					this.m_nUseType = 1;
			} else {
				// Обновляем точку последнего сохранения в истории
				AscCommon.History.Reset_SavedIndex(IsUserSave);
			}
		};

		CCollaborativeEditing.prototype.getRecalcIndexSave = function (oRecalcIndex) {
			var bHasIndex = false;
			var result = {};
			var element = null;
			for (var sheetId in oRecalcIndex) {
				if (!oRecalcIndex.hasOwnProperty(sheetId))
					continue;
				result[sheetId] = {"_arrElements": []};
				for (var i = 0, length = oRecalcIndex[sheetId]._arrElements.length; i < length; ++i) {
					bHasIndex = true;
					element = oRecalcIndex[sheetId]._arrElements[i];
					result[sheetId]["_arrElements"].push({"_recalcType" : element._recalcType,
						"_position" : element._position, "_count" : element._count,
						"m_bIsSaveIndex" : element.m_bIsSaveIndex});
				}
			}

			return bHasIndex ? result : null;
		};

		CCollaborativeEditing.prototype.S4 = function () {
			return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
		};
		CCollaborativeEditing.prototype.createGUID = function () {
			return (this.S4() + this.S4() + "-" + this.S4() + "-" + this.S4() + "-" + this.S4() + "-" + this.S4() + this.S4() + this.S4());
		};

		CCollaborativeEditing.prototype.getLockInfo = function (typeElem, subType, sheetId, info) {
			var oLockInfo = new AscCommonExcel.asc_CLockInfo();
			oLockInfo["sheetId"] = sheetId;
			oLockInfo["type"] = typeElem;
			oLockInfo["subType"] = subType;
			oLockInfo["guid"] = this.createGUID();
			oLockInfo["rangeOrObjectId"] = info;
			return oLockInfo;
		};

		CCollaborativeEditing.prototype.getLockByElem = function (element, type) {
			var arrayElements = (c_oAscLockTypes.kLockTypeMine === type) ? this.m_arrNeedUnlock2 : this.m_arrNeedUnlock;
			for (var i = 0; i < arrayElements.length; ++i)
				if (element["guid"] === arrayElements[i].Element["guid"])
					return arrayElements[i];
			return null;
		};

		/**
		 * Проверка lock для элемента
		 * @param {asc_CLockInfo} element  элемент для проверки lock
		 * @param {c_oAscLockTypes} type сами(kLockTypeMine) или кто-то другой
		 * @param {Boolean} bCheckOnlyLockAll проверять только lock для свойств всего листа (либо только проверять удален ли лист, а не просто залочен)
		 */
		CCollaborativeEditing.prototype.getLockIntersection = function (element, type, bCheckOnlyLockAll) {
			var arrayElements = (c_oAscLockTypes.kLockTypeMine === type) ? this.m_arrNeedUnlock2 : this.m_arrNeedUnlock;
			var oUnlockElement = null, rangeTmp1, rangeTmp2;
			for (var i = 0; i < arrayElements.length; ++i) {
				oUnlockElement = arrayElements[i].Element;
				if (c_oAscLockTypeElem.Sheet === element["type"] && element["type"] === oUnlockElement["type"]) {
					// Проверка только на удаление листа (если проверка для себя, то выходим не сразу, т.к. нужно проверить lock от других элементов)
					if ((c_oAscLockTypes.kLockTypeMine !== type && false === bCheckOnlyLockAll) ||
						element["sheetId"] === oUnlockElement["sheetId"]) {
						// Если кто-то залочил sheet, то больше никто не может лочить sheet-ы (иначе можно удалить все листы)
						return arrayElements[i];
					}
				}
				if (element["sheetId"] !== oUnlockElement["sheetId"])
					continue;

				if (null !== element["subType"] && null !== oUnlockElement["subType"])
					return arrayElements[i];

				// Не учитываем lock от ChangeProperties (только если это не lock листа)
				if (true === bCheckOnlyLockAll ||
					(c_oAscLockTypeElemSubType.ChangeProperties === oUnlockElement["subType"]
						&& c_oAscLockTypeElem.Sheet !== element["type"]))
					continue;

				if (element["type"] === oUnlockElement["type"]) {
					if (element["type"] === c_oAscLockTypeElem.Object) {
						if (element["rangeOrObjectId"] === oUnlockElement["rangeOrObjectId"])
							return arrayElements[i];
					} else if (element["type"] === c_oAscLockTypeElem.Range) {
						// Не учитываем lock от Insert
						if (c_oAscLockTypeElemSubType.InsertRows === oUnlockElement["subType"] || c_oAscLockTypeElemSubType.InsertColumns === oUnlockElement["subType"])
							continue;
						rangeTmp1 = oUnlockElement["rangeOrObjectId"];
						rangeTmp2 = element["rangeOrObjectId"];
						if (rangeTmp2["c1"] > rangeTmp1["c2"] || rangeTmp2["c2"] < rangeTmp1["c1"] || rangeTmp2["r1"] > rangeTmp1["r2"] || rangeTmp2["r2"] < rangeTmp1["r1"])
							continue;
						return arrayElements[i];
					}
				} else if (oUnlockElement["type"] === c_oAscLockTypeElem.Sheet ||
					(element["type"] === c_oAscLockTypeElem.Sheet && c_oAscLockTypes.kLockTypeMine !== type)) {
					// Если кто-то уже залочил лист или мы пытаемся сами залочить и проверяем на чужие lock
					return arrayElements[i];
				}
			}
			return false;
		};

		CCollaborativeEditing.prototype.getLockElem = function (typeElem, type, sheetId) {
			var arrayElements = (c_oAscLockTypes.kLockTypeMine === type) ? this.m_arrNeedUnlock2 : this.m_arrNeedUnlock;
			var count = arrayElements.length;
			var element = null, oRangeOrObjectId = null;
			var result = [];
			var c1, c2, r1, r2;

			if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId)) {
				this.m_oRecalcIndexColumns[sheetId] = new CRecalcIndex();
			}
			if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId)) {
				this.m_oRecalcIndexRows[sheetId] = new CRecalcIndex();
			}

			for (var i = 0; i < count; ++i) {
				element = arrayElements[i].Element;
				if (element["sheetId"] !== sheetId || element["type"] !== typeElem)
					continue;

				// Отображать залоченность удаленных текущим пользователем строк/столбцов не нужно (уже нечего отображать)
				if (c_oAscLockTypes.kLockTypeMine === type && c_oAscLockTypeElem.Range === typeElem &&
					(c_oAscLockTypeElemSubType.DeleteColumns === element["subType"] ||
						c_oAscLockTypeElemSubType.DeleteRows === element["subType"]))
					continue;
				// Отображать залоченность добавленных другим пользователем строк/столбцов не нужно (еще нечего отображать)
				if (c_oAscLockTypeElem.Range === typeElem &&
					(c_oAscLockTypeElemSubType.InsertColumns === element["subType"] ||
						c_oAscLockTypeElemSubType.InsertRows === element["subType"]))
					continue;
				// Отображать lock-диапазон для lockAll(всего листа) не нужно
				if (c_oAscLockTypeElemSubType.ChangeProperties === element["subType"])
					continue;

				oRangeOrObjectId = element["rangeOrObjectId"];
				// Для диапазона нужно сделать пересчет с учетом удаленных или добавленных строк/столбцов
				if (c_oAscLockTypeElem.Range === typeElem) {
					// Пересчитывать для удаленных строк/столбцов у другого пользователя не нужно
					if (c_oAscLockTypes.kLockTypeMine !== type && c_oAscLockTypeElem.Range === typeElem &&
						(c_oAscLockTypeElemSubType.DeleteColumns === element["subType"] ||
							c_oAscLockTypeElemSubType.DeleteRows === element["subType"])) {
						c1 = oRangeOrObjectId["c1"];
						c2 = oRangeOrObjectId["c2"];
						r1 = oRangeOrObjectId["r1"];
						r2 = oRangeOrObjectId["r2"];
					} else {
						c1 = this.m_oRecalcIndexColumns[sheetId].getLockOther(oRangeOrObjectId["c1"], type);
						c2 = this.m_oRecalcIndexColumns[sheetId].getLockOther(oRangeOrObjectId["c2"], type);
						r1 = this.m_oRecalcIndexRows[sheetId].getLockOther(oRangeOrObjectId["r1"], type);
						r2 = this.m_oRecalcIndexRows[sheetId].getLockOther(oRangeOrObjectId["r2"], type);
					}
					if (null === c1 || null === c2 || null === r1 || null === r2)
						continue;

					oRangeOrObjectId = new asc_Range(c1, r1, c2, r2);
				}

				result.push(oRangeOrObjectId);
			}

			return result;
		};

		CCollaborativeEditing.prototype.getLockCellsMe = function (sheetId) {
			return this.getLockElem(c_oAscLockTypeElem.Range, c_oAscLockTypes.kLockTypeMine, sheetId);
		};
		CCollaborativeEditing.prototype.getLockCellsOther = function (sheetId) {
			return this.getLockElem(c_oAscLockTypeElem.Range, c_oAscLockTypes.kLockTypeOther, sheetId);
		};
		CCollaborativeEditing.prototype.getLockObjectsMe = function (sheetId) {
			return this.getLockElem(c_oAscLockTypeElem.Object, c_oAscLockTypes.kLockTypeMine, sheetId);
		};
		CCollaborativeEditing.prototype.getLockObjectsOther = function (sheetId) {
			return this.getLockElem(c_oAscLockTypeElem.Object, c_oAscLockTypes.kLockTypeOther, sheetId);
		};
		/**
		 * Проверка lock для всего листа
		 * @param {Number} sheetId  элемент для проверки lock
		 * @return {Asc.c_oAscMouseMoveLockedObjectType} oLockedObjectType
		 */
		CCollaborativeEditing.prototype.isLockAllOther = function (sheetId) {
			var arrayElements = this.m_arrNeedUnlock;
			var count = arrayElements.length;
			var element = null;
			var oLockedObjectType = Asc.c_oAscMouseMoveLockedObjectType.None;

			for (var i = 0; i < count; ++i) {
				element = arrayElements[i].Element;
				if (element["sheetId"] === sheetId) {
					if (element["type"] === c_oAscLockTypeElem.Sheet) {
						oLockedObjectType = Asc.c_oAscMouseMoveLockedObjectType.Sheet;
						break;
					} else if (element["type"] === c_oAscLockTypeElem.Range && null !== element["subType"])
						oLockedObjectType = Asc.c_oAscMouseMoveLockedObjectType.TableProperties;
				}
			}
			return oLockedObjectType;
		};

		CCollaborativeEditing.prototype._recalcLockArray = function (typeLock, oRecalcIndexColumns, oRecalcIndexRows) {
			var arrayElements = (c_oAscLockTypes.kLockTypeMine === typeLock) ? this.m_arrNeedUnlock2 : this.m_arrNeedUnlock;
			var count = arrayElements.length;
			var element = null, oRangeOrObjectId = null;
			var i;
			var sheetId = -1;

			for (i = 0; i < count; ++i) {
				element = arrayElements[i].Element;
				// Для удаления пересчитывать индексы не нужно
				if (c_oAscLockTypeElem.Range !== element["type"] ||
					c_oAscLockTypeElemSubType.InsertColumns === element["subType"] ||
					c_oAscLockTypeElemSubType.InsertRows === element["subType"] ||
					c_oAscLockTypeElemSubType.DeleteColumns === element["subType"] ||
					c_oAscLockTypeElemSubType.DeleteRows === element["subType"])
					continue;
				sheetId = element["sheetId"];

				oRangeOrObjectId = element["rangeOrObjectId"];

				if (oRecalcIndexColumns && oRecalcIndexColumns.hasOwnProperty(sheetId)) {
					// Пересчет колонок
					oRangeOrObjectId["c1"] = oRecalcIndexColumns[sheetId].getLockMe(oRangeOrObjectId["c1"]);
					oRangeOrObjectId["c2"] = oRecalcIndexColumns[sheetId].getLockMe(oRangeOrObjectId["c2"]);
				}
				if (oRecalcIndexRows && oRecalcIndexRows.hasOwnProperty(sheetId)) {
					// Пересчет строк
					oRangeOrObjectId["r1"] = oRecalcIndexRows[sheetId].getLockMe(oRangeOrObjectId["r1"]);
					oRangeOrObjectId["r2"] = oRecalcIndexRows[sheetId].getLockMe(oRangeOrObjectId["r2"]);
				}
			}
		};
		// Пересчет только для чужих Lock при сохранении на клиенте, который добавлял/удалял строки или столбцы
		CCollaborativeEditing.prototype._recalcLockArrayOthers = function () {
			var typeLock = c_oAscLockTypes.kLockTypeOther;
			var arrayElements = (c_oAscLockTypes.kLockTypeMine === typeLock) ? this.m_arrNeedUnlock2 : this.m_arrNeedUnlock;
			var count = arrayElements.length;
			var element = null, oRangeOrObjectId = null;
			var i;
			var sheetId = -1;

			for (i = 0; i < count; ++i) {
				element = arrayElements[i].Element;
				if (c_oAscLockTypeElem.Range !== element["type"] ||
					c_oAscLockTypeElemSubType.InsertColumns === element["subType"] ||
					c_oAscLockTypeElemSubType.InsertRows === element["subType"])
					continue;
				sheetId = element["sheetId"];

				oRangeOrObjectId = element["rangeOrObjectId"];

				if (this.m_oRecalcIndexColumns.hasOwnProperty(sheetId)) {
					// Пересчет колонок
					oRangeOrObjectId["c1"] = this.m_oRecalcIndexColumns[sheetId].getLockOther(oRangeOrObjectId["c1"]);
					oRangeOrObjectId["c2"] = this.m_oRecalcIndexColumns[sheetId].getLockOther(oRangeOrObjectId["c2"]);
				}
				if (this.m_oRecalcIndexRows.hasOwnProperty(sheetId)) {
					// Пересчет строк
					oRangeOrObjectId["r1"] = this.m_oRecalcIndexRows[sheetId].getLockOther(oRangeOrObjectId["r1"]);
					oRangeOrObjectId["r2"] = this.m_oRecalcIndexRows[sheetId].getLockOther(oRangeOrObjectId["r2"]);
				}
			}
		};

		CCollaborativeEditing.prototype.addRecalcIndex = function (type, oRecalcIndex) {
			if (null == oRecalcIndex)
				return null;
			var nIndex = 0;
			var nRecalcType = c_oAscRecalcIndexTypes.RecalcIndexAdd;
			var oRecalcIndexElement = null;
			var oRecalcIndexResult = {};

			var oRecalcIndexTmp = ("0" === type) ? this.m_oRecalcIndexColumns : this.m_oRecalcIndexRows;
			for (var sheetId in oRecalcIndex) {
				if (oRecalcIndex.hasOwnProperty(sheetId)) {
					if (!oRecalcIndexTmp.hasOwnProperty(sheetId)) {
						oRecalcIndexTmp[sheetId] = new CRecalcIndex();
					}
					if (!oRecalcIndexResult.hasOwnProperty(sheetId)) {
						oRecalcIndexResult[sheetId] = new CRecalcIndex();
					}
					for (; nIndex < oRecalcIndex[sheetId]["_arrElements"].length; ++nIndex) {
						oRecalcIndexElement = oRecalcIndex[sheetId]["_arrElements"][nIndex];
						if (true === oRecalcIndexElement["m_bIsSaveIndex"])
							continue;
						nRecalcType = (c_oAscRecalcIndexTypes.RecalcIndexAdd === oRecalcIndexElement["_recalcType"]) ?
							c_oAscRecalcIndexTypes.RecalcIndexRemove : c_oAscRecalcIndexTypes.RecalcIndexAdd;
						oRecalcIndexTmp[sheetId].add(nRecalcType, oRecalcIndexElement["_position"],
							oRecalcIndexElement["_count"], /*bIsSaveIndex*/true);
						// Дублируем для возврата результата (нам нужно пересчитать только по последнему индексу
						oRecalcIndexResult[sheetId].add(nRecalcType, oRecalcIndexElement["_position"],
							oRecalcIndexElement["_count"], /*bIsSaveIndex*/true);
					}
				}
			}

			return oRecalcIndexResult;
		};

		// Undo для добавления/удаления столбцов
		CCollaborativeEditing.prototype.undoCols = function (sheetId, count) {
      if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId))
        return;
      this.m_oRecalcIndexColumns[sheetId].remove(count);
		};
		// Undo для добавления/удаления строк
		CCollaborativeEditing.prototype.undoRows = function (sheetId, count) {
      if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId))
        return;
      this.m_oRecalcIndexRows[sheetId].remove(count);
		};

		CCollaborativeEditing.prototype.removeCols = function (sheetId, position, count) {
      if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId)) {
        this.m_oRecalcIndexColumns[sheetId] = new CRecalcIndex();
      }
      this.m_oRecalcIndexColumns[sheetId].add(c_oAscRecalcIndexTypes.RecalcIndexRemove, position,
        count, /*bIsSaveIndex*/false);
		};
		CCollaborativeEditing.prototype.addCols = function (sheetId, position, count) {
      if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId)) {
        this.m_oRecalcIndexColumns[sheetId] = new CRecalcIndex();
      }
      this.m_oRecalcIndexColumns[sheetId].add(c_oAscRecalcIndexTypes.RecalcIndexAdd, position,
        count, /*bIsSaveIndex*/false);
		};
		CCollaborativeEditing.prototype.removeRows = function (sheetId, position, count) {
      if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId)) {
        this.m_oRecalcIndexRows[sheetId] = new CRecalcIndex();
      }
      this.m_oRecalcIndexRows[sheetId].add(c_oAscRecalcIndexTypes.RecalcIndexRemove, position,
        count, /*bIsSaveIndex*/false);
		};
		CCollaborativeEditing.prototype.addRows = function (sheetId, position, count) {
      if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId)) {
        this.m_oRecalcIndexRows[sheetId] = new CRecalcIndex();
      }
      this.m_oRecalcIndexRows[sheetId].add(c_oAscRecalcIndexTypes.RecalcIndexAdd, position,
        count, /*bIsSaveIndex*/false);
		};
		CCollaborativeEditing.prototype.addColsRange = function (sheetId, range) {
			if (!this.m_oInsertColumns.hasOwnProperty(sheetId)) {
				this.m_oInsertColumns[sheetId] = [];
			}
			var arrInsertColumns = this.m_oInsertColumns[sheetId];
			// Перед добавлением нужно передвинуть имеющиеся
			var countCols = range.c2 - range.c1 + 1;
			var isAddNewRange = true;
			for (var i = 0; i < arrInsertColumns.length; ++i) {
				if (arrInsertColumns[i].c1 > range.c1) {
					arrInsertColumns[i].c1 += countCols;
					arrInsertColumns[i].c2 += countCols;
				} else if (arrInsertColumns[i].c1 <= range.c1 && arrInsertColumns[i].c2 >= range.c1) {
					arrInsertColumns[i].c2 += countCols;
					isAddNewRange = false;
				}
			}
			if (isAddNewRange)
				arrInsertColumns.push(range);
		};
		CCollaborativeEditing.prototype.addRowsRange = function (sheetId, range) {
			if (!this.m_oInsertRows.hasOwnProperty(sheetId)) {
				this.m_oInsertRows[sheetId] = [];
			}
			var arrInsertRows = this.m_oInsertRows[sheetId];
			// Перед добавлением нужно передвинуть имеющиеся
			var countRows = range.r2 - range.r1 + 1;
			var isAddNewRange = true;
			for (var i = 0; i < arrInsertRows.length; ++i) {
				if (arrInsertRows[i].r1 > range.r1) {
					arrInsertRows[i].r1 += countRows;
					arrInsertRows[i].r2 += countRows;
				} else if (arrInsertRows[i].r1 <= range.r1 && arrInsertRows[i].r2 >= range.r1) {
					arrInsertRows[i].r2 += countRows;
					isAddNewRange = false;
				}
			}
			if (isAddNewRange)
				arrInsertRows.push(range);
		};
		CCollaborativeEditing.prototype.removeColsRange = function (sheetId, range) {
			if (!this.m_oInsertColumns.hasOwnProperty(sheetId))
				return;
			var arrInsertColumns = this.m_oInsertColumns[sheetId];
			// Нужно убрать те колонки, которые входят в диапазон
			var countCols = range.c2 - range.c1 + 1;
			for (var i = 0; i < arrInsertColumns.length; ++i) {
				if (arrInsertColumns[i].c1 > range.c2) {
					// Справа от удаляемого диапазона
					arrInsertColumns[i].c1 -= countCols;
					arrInsertColumns[i].c2 -= countCols;
				} else if (arrInsertColumns[i].c1 >= range.c1 && arrInsertColumns[i].c2 <= range.c2) {
					// Полностью включение в удаляемый диапазон
					arrInsertColumns.splice(i, 1);
					i -= 1;
				} else if (arrInsertColumns[i].c1 >= range.c1 && arrInsertColumns[i].c1 <= range.c2 && arrInsertColumns[i].c2 > range.c2) {
					// Частичное включение начала диапазона
					arrInsertColumns[i].c1 = range.c2 + 1;
					arrInsertColumns[i].c1 -= countCols;
					arrInsertColumns[i].c2 -= countCols;
				} else if (arrInsertColumns[i].c1 < range.c1 && arrInsertColumns[i].c2 >= range.c1 && arrInsertColumns[i].c2 <= range.c2) {
					// Частичное включение окончания диапазона
					arrInsertColumns[i].c2 = range.c1 - 1;
				} else if (arrInsertColumns[i].c1 < range.c1 && arrInsertColumns[i].c2 > range.c2) {
					// Удаляемый диапазон внутри нашего диапазона
					arrInsertColumns[i].c2 -= countCols;
				}
			}
		};
		CCollaborativeEditing.prototype.removeRowsRange = function (sheetId, range) {
			if (!this.m_oInsertRows.hasOwnProperty(sheetId))
				return;
			var arrInsertRows = this.m_oInsertRows[sheetId];
			// Нужно убрать те строки, которые входят в диапазон
			var countRows = range.r2 - range.r1 + 1;
			for (var i = 0; i < arrInsertRows.length; ++i) {
				if (arrInsertRows[i].r1 > range.r2) {
					// Снизу от удаляемого диапазона
					arrInsertRows[i].r1 -= countRows;
					arrInsertRows[i].r2 -= countRows;
				} else if (arrInsertRows[i].r1 >= range.r1 && arrInsertRows[i].r2 <= range.r2) {
					// Полностью включение в удаляемый диапазон
					arrInsertRows.splice(i, 1);
					i -= 1;
				} else if (arrInsertRows[i].r1 >= range.r1 && arrInsertRows[i].r1 <= range.r2 && arrInsertRows[i].r2 > range.r2) {
					// Частичное включение начала диапазона
					arrInsertRows[i].r1 = range.r2 + 1;
					arrInsertRows[i].r1 -= countRows;
					arrInsertRows[i].r2 -= countRows;
				} else if (arrInsertRows[i].r1 < range.r1 && arrInsertRows[i].r2 >= range.r1 && arrInsertRows[i].r2 <= range.r2) {
					// Частичное включение окончания диапазона
					arrInsertRows[i].r2 = range.r1 - 1;
				} else if (arrInsertRows[i].r1 < range.r1 && arrInsertRows[i].r2 > range.r2) {
					// Удаляемый диапазон внутри нашего диапазона
					arrInsertRows[i].r2 -= countRows;
				}
			}
		};
		CCollaborativeEditing.prototype.isIntersectionInCols = function (sheetId, col) {
			if (!this.m_oInsertColumns.hasOwnProperty(sheetId))
				return false;
			var arrInsertColumns = this.m_oInsertColumns[sheetId];
			for (var i = 0; i < arrInsertColumns.length; ++i) {
				if (arrInsertColumns[i].c1 <= col && col <= arrInsertColumns[i].c2)
					return true;
			}
			return false;
		};
		CCollaborativeEditing.prototype.isIntersectionInRows = function (sheetId, row) {
			if (!this.m_oInsertRows.hasOwnProperty(sheetId))
				return false;
			var arrInsertRows = this.m_oInsertRows[sheetId];
			for (var i = 0; i < arrInsertRows.length; ++i) {
				if (arrInsertRows[i].r1 <= row && row <= arrInsertRows[i].r2)
					return true;
			}
			return false;
		};
		CCollaborativeEditing.prototype.getArrayInsertColumnsBySheetId = function (sheetId) {
			if (!this.m_oInsertColumns.hasOwnProperty(sheetId))
				return [];

			return this.m_oInsertColumns[sheetId];
		};
		CCollaborativeEditing.prototype.getArrayInsertRowsBySheetId = function (sheetId) {
			if (!this.m_oInsertRows.hasOwnProperty(sheetId))
				return [];

			return this.m_oInsertRows[sheetId];
		};
		CCollaborativeEditing.prototype.getLockMeColumn = function (sheetId, col) {
			if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId))
				return col;
			return this.m_oRecalcIndexColumns[sheetId].getLockMe(col);
		};
		CCollaborativeEditing.prototype.getLockMeRow = function (sheetId, row) {
			if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId))
				return row;
			return this.m_oRecalcIndexRows[sheetId].getLockMe(row);
		};
		// Только когда от других пользователей изменения колонок (для пересчета)
		CCollaborativeEditing.prototype.getLockMeColumn2 = function (sheetId, col) {
			if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId))
				return col;
			return this.m_oRecalcIndexColumns[sheetId].getLockMe2(col);
		};
		// Только когда от других пользователей изменения строк (для пересчета)
		CCollaborativeEditing.prototype.getLockMeRow2 = function (sheetId, row) {
			if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId))
				return row;
			return this.m_oRecalcIndexRows[sheetId].getLockMe2(row);
		};
		// Только для принятия изменений от других пользователей! (для пересчета только в сохранении)
		CCollaborativeEditing.prototype.getLockOtherColumn2 = function (sheetId, col) {
			if (!this.m_oRecalcIndexColumns.hasOwnProperty(sheetId))
				return col;
			return this.m_oRecalcIndexColumns[sheetId].getLockSaveOther(col);
		};
		// Только для принятия изменений от других пользователей! (для пересчета только в сохранении)
		CCollaborativeEditing.prototype.getLockOtherRow2 = function (sheetId, row) {
			if (!this.m_oRecalcIndexRows.hasOwnProperty(sheetId))
				return row;
			return this.m_oRecalcIndexRows[sheetId].getLockSaveOther(row);
		};

		/**
		 * Отвечает за лок в совместном редактировании
		 * -----------------------------------------------------------------------------
		 *
		 * @constructor
		 * @memberOf Asc
		 */
		function CLock(element) {
			this.Type   = c_oAscLockTypes.kLockTypeNone;
			this.UserId = null;
			this.Element = element;

			this.init();

			return this;
		}

		CLock.prototype.init = function () {
		};
		CLock.prototype.getType = function () {
			return this.Type;
		};
		CLock.prototype.setType = function (newType) {
			if (newType === c_oAscLockTypes.kLockTypeNone)
				this.UserId = null;

			this.Type = newType;
		};

		CLock.prototype.Lock = function(bMine) {
			if (c_oAscLockTypes.kLockTypeNone === this.Type)
			{
				if (true === bMine)
					this.Type = c_oAscLockTypes.kLockTypeMine;
				else
					this.Type = c_oAscLockTypes.kLockTypeOther;
			}
		};

		CLock.prototype.setUserId = function(UserId) {
			this.UserId = UserId;
		};

		function CRecalcIndexElement(recalcType, position, bIsSaveIndex) {
			if ( !(this instanceof CRecalcIndexElement) ) {
				return new CRecalcIndexElement (recalcType, position, bIsSaveIndex);
			}

			this._recalcType	= recalcType;		// Тип изменений (удаление или добавление)
			this._position		= position;			// Позиция, в которой произошли изменения
			this._count			= 1;				// Считаем все изменения за простейшие
			this.m_bIsSaveIndex	= !!bIsSaveIndex;	// Это индексы из изменений других пользователей (которые мы еще не применили)

			return this;
		}

		// Пересчет для других
		CRecalcIndexElement.prototype.getLockOther = function (position, type) {
			var inc = (c_oAscRecalcIndexTypes.RecalcIndexAdd === this._recalcType) ? +1 : -1;
			if (position === this._position && c_oAscRecalcIndexTypes.RecalcIndexRemove === this._recalcType &&
				true === this.m_bIsSaveIndex) {
				// Мы еще не применили чужие изменения (поэтому для insert не нужно отрисовывать)
				// RecalcIndexRemove (потому что перевертываем для правильной отработки, от другого пользователя
				// пришло RecalcIndexAdd
				return null;
			} else if (position === this._position &&
				c_oAscRecalcIndexTypes.RecalcIndexRemove === this._recalcType &&
				c_oAscLockTypes.kLockTypeMine === type && false === this.m_bIsSaveIndex) {
				// Для пользователя, который удалил столбец, рисовать залоченные ранее в данном столбце ячейки
				// не нужно
				return null;
			} else if (position < this._position)
				return position;
			else
				return (position + inc);
		};
		// Пересчет для других (только для сохранения)
		CRecalcIndexElement.prototype.getLockSaveOther = function (position, type) {
			if (this.m_bIsSaveIndex)
				return position;

			var inc = (c_oAscRecalcIndexTypes.RecalcIndexAdd === this._recalcType) ? +1 : -1;
			if (position === this._position && c_oAscRecalcIndexTypes.RecalcIndexRemove === this._recalcType &&
				true === this.m_bIsSaveIndex) {
				// Мы еще не применили чужие изменения (поэтому для insert не нужно отрисовывать)
				// RecalcIndexRemove (потому что перевертываем для правильной отработки, от другого пользователя
				// пришло RecalcIndexAdd
				return null;
			} else if (position === this._position &&
				c_oAscRecalcIndexTypes.RecalcIndexRemove === this._recalcType &&
				c_oAscLockTypes.kLockTypeMine === type && false === this.m_bIsSaveIndex) {
				// Для пользователя, который удалил столбец, рисовать залоченные ранее в данном столбце ячейки
				// не нужно
				return null;
			} else if (position < this._position)
				return position;
			else
				return (position + inc);
		};
		// Пересчет для себя
		CRecalcIndexElement.prototype.getLockMe = function (position) {
			var inc = (c_oAscRecalcIndexTypes.RecalcIndexAdd === this._recalcType) ? -1 : +1;
			if (position < this._position)
				return position;
			else
				return (position + inc);
		};
		// Только когда от других пользователей изменения (для пересчета)
		CRecalcIndexElement.prototype.getLockMe2 = function (position) {
			var inc = (c_oAscRecalcIndexTypes.RecalcIndexAdd === this._recalcType) ? -1 : +1;
			if (true !== this.m_bIsSaveIndex || position < this._position)
				return position;
			else
				return (position + inc);
		};

		function CRecalcIndex() {
			if ( !(this instanceof CRecalcIndex) ) {
				return new CRecalcIndex ();
			}

			this._arrElements = [];		// Массив CRecalcIndexElement

			return this;
		}

		CRecalcIndex.prototype.add = function (recalcType, position, count, bIsSaveIndex) {
			for (var i = 0; i < count; ++i)
				this._arrElements.push(new CRecalcIndexElement(recalcType, position, bIsSaveIndex));
		};
		// Удаляет из пересчета, для undo
		CRecalcIndex.prototype.remove = function (count) {
			for (var i = 0; i < count; ++i)
				this._arrElements.pop();
		};
		CRecalcIndex.prototype.clear = function () {
			this._arrElements.length = 0;
		};

		// Пересчет для других
		CRecalcIndex.prototype.getLockOther = function (position, type) {
			var newPosition = position;
			/*var count = this._arrElements.length;
			 for (var i = 0; i < count; ++i) {
			 newPosition = this._arrElements[i].getLockOther(newPosition, type);
			 if (null === newPosition)
			 break;
			 }*/

			var count = this._arrElements.length;
			if (0 >= count)
				return newPosition;
			// Для пересчета, когда добавил сам - обратный порядок
			// Для пересчета, когда добавил кто-то другой - прямой
			var bIsDirect = !this._arrElements[0].m_bIsSaveIndex;
			var i;
			if (bIsDirect) {
				for (i = 0; i < count; ++i) {
					newPosition = this._arrElements[i].getLockOther(newPosition, type);
					if (null === newPosition)
						break;
				}
			} else {
				for (i = count - 1; i >= 0; --i) {
					newPosition = this._arrElements[i].getLockOther(newPosition, type);
					if (null === newPosition)
						break;
				}
			}

			return newPosition;
		};
		// Пересчет для других (только для сохранения)
		CRecalcIndex.prototype.getLockSaveOther = function (position, type) {
			var newPosition = position;
			var count = this._arrElements.length;
			for (var i = 0; i < count; ++i) {
				newPosition = this._arrElements[i].getLockSaveOther(newPosition, type);
				if (null === newPosition)
					break;
			}

			return newPosition;
		};
		// Пересчет для себя
		CRecalcIndex.prototype.getLockMe = function (position) {
			var newPosition = position;
			var count = this._arrElements.length;
			if (0 >= count)
				return newPosition;
			// Для пересчета, когда добавил сам - обратный порядок
			// Для пересчета, когда добавил кто-то другой - прямой
			var bIsDirect = this._arrElements[0].m_bIsSaveIndex;
			var i;
			if (bIsDirect) {
				for (i = 0; i < count; ++i) {
					newPosition = this._arrElements[i].getLockMe(newPosition);
					if (null === newPosition)
						break;
				}
			} else {
				for (i = count - 1; i >= 0; --i) {
					newPosition = this._arrElements[i].getLockMe(newPosition);
					if (null === newPosition)
						break;
				}
			}

			return newPosition;
		};
		// Только когда от других пользователей изменения (для пересчета)
		CRecalcIndex.prototype.getLockMe2 = function (position) {
			var newPosition = position;
			var count = this._arrElements.length;
			if (0 >= count)
				return newPosition;
			// Для пересчета, когда добавил сам - обратный порядок
			// Для пересчета, когда добавил кто-то другой - прямой
			var bIsDirect = this._arrElements[0].m_bIsSaveIndex;
			var i;
			if (bIsDirect) {
				for (i = 0; i < count; ++i) {
					newPosition = this._arrElements[i].getLockMe2(newPosition);
					if (null === newPosition)
						break;
				}
			} else {
				for (i = count - 1; i >= 0; --i) {
					newPosition = this._arrElements[i].getLockMe2(newPosition);
					if (null === newPosition)
						break;
				}
			}

			return newPosition;
		};

		//----------------------------------------------------------export----------------------------------------------------
		window['Asc'] = window['Asc'] || {};
		window['AscCommonExcel'] = window['AscCommonExcel'] || {};
		window['AscCommonExcel'].CLock = CLock;

		window['AscCommonExcel'].CCollaborativeEditing = CCollaborativeEditing;
		window['Asc'].CRecalcIndexElement = CRecalcIndexElement;
		window['Asc'].CRecalcIndex = CRecalcIndex;
	}
)(window);

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

(function(window, undefined)
{
	// Import
	var offlineMode = AscCommon.offlineMode;
	var c_oEditorId = AscCommon.c_oEditorId;

	var c_oAscError           = Asc.c_oAscError;
	var c_oAscAsyncAction     = Asc.c_oAscAsyncAction;
	var c_oAscAsyncActionType = Asc.c_oAscAsyncActionType;

	var ASC_DOCS_API_USE_EMBEDDED_FONTS = "@@ASC_DOCS_API_USE_EMBEDDED_FONTS";

	/** @constructor */
	function baseEditorsApi(config, editorId)
	{
		this.editorId      = editorId;
		this.isLoadFullApi = false;
		this.openResult    = null;

		this.HtmlElementName = config['id-view'] || '';
		this.HtmlElement     = null;

		this.isMobileVersion = (config['mobile'] === true);

		this.isViewMode = false;

		this.FontLoader  = null;
		this.ImageLoader = null;

		this.LoadedObject        = null;
		this.DocumentType        = 0; // 0 - empty, 1 - test, 2 - document (from json)
		this.DocInfo             = null;
		this.documentVKey        = null;
		this.documentId          = undefined;
		this.documentUserId      = undefined;
		this.documentUrl         = "null";
		this.documentUrlChanges  = null;
		this.documentCallbackUrl = undefined;		// Ссылка для отправления информации о документе
		this.documentFormat      = "null";
		this.documentTitle       = "null";
		this.documentFormatSave  = Asc.c_oAscFileType.UNKNOWN;

		this.documentOpenOptions = undefined;		// Опции при открытии (пока только опции для CSV)

		// Тип состояния на данный момент (сохранение, открытие или никакое)
		this.advancedOptionsAction = AscCommon.c_oAscAdvancedOptionsAction.None;
		// Тип скачивания файлы(download или event).нужен для txt, csv. запоминаем на asc_DownloadAs используем asc_setAdvancedOptions
		this.downloadType          = AscCommon.DownloadType.None;
		this.OpenDocumentProgress  = new AscCommon.COpenProgress();
		var sProtocol              = window.location.protocol;
		this.documentOrigin        = ((sProtocol && '' !== sProtocol) ? sProtocol + '//' : '') + window.location.host; // for presentation theme url
		this.documentPathname      = window.location.pathname; // for presentation theme url

		// Переменная отвечает, получили ли мы ответ с сервера совместного редактирования
		this.ServerIdWaitComplete = false;

		// Long action
		this.IsLongActionCurrent       = 0;
		this.LongActionCallbacks       = [];
		this.LongActionCallbacksParams = [];

		// AutoSave
		this.autoSaveGap = 0;					// Интервал автосохранения (0 - означает, что автосохранения нет) в милесекундах

		this.isDocumentCanSave = false;			// Флаг, говорит о возможности сохранять документ (активна кнопка save или нет)

		// Chart
		this.chartTranslate        = null;
		this.textArtTranslate      = null;
		this.chartPreviewManager   = null;
		this.textArtPreviewManager = null;
		this.shapeElementId        = null;
		// Режим вставки диаграмм в редакторе документов
		this.isChartEditor         = false;
		this.isOpenedChartFrame    = false;

		// CoAuthoring and Chat
		this.User                   = undefined;
		this.CoAuthoringApi         = new AscCommon.CDocsCoApi();
		this.isCoAuthoringEnable    = true;
		// Массив lock-ов, которые были на открытии документа
		this.arrPreOpenLocksObjects = [];

		// Spell Checking
		this.SpellCheckUrl = '';    // Ссылка сервиса для проверки орфографии

		// Результат получения лицензии
		this.licenseResult       = null;
		// Подключились ли уже к серверу
		this.isOnFirstConnectEnd = false;
		// Получили ли лицензию
		this.isOnLoadLicense     = false;

		this.canSave    = true;        // Флаг нужен чтобы не происходило сохранение пока не завершится предыдущее сохранение
		this.IsUserSave = false;    // Флаг, контролирующий сохранение было сделано пользователем или нет (по умолчанию - нет)

		// Version History
		this.VersionHistory = null;				// Объект, который отвечает за точку в списке версий

		//Флаги для применения свойств через слайдеры
		this.noCreatePoint     = false;
		this.exucuteHistory    = false;
		this.exucuteHistoryEnd = false;

		// На этапе сборки значение переменной ASC_DOCS_API_USE_EMBEDDED_FONTS может менятся.
		// По дефолту встроенные шрифты использоваться не будут, как и при любом значении
		// ASC_DOCS_API_USE_EMBEDDED_FONTS, кроме "true"(написание от регистра не зависит).

		// Использовать ли обрезанные шрифты
		this.isUseEmbeddedCutFonts = ("true" == ASC_DOCS_API_USE_EMBEDDED_FONTS.toLowerCase());

		this.tmpFocus = null;

		this.fCurCallback = null;

		this.pluginsManager = null;

		this.isLockTargetUpdate = false;

		return this;
	}

	baseEditorsApi.prototype._init                           = function()
	{
		var t            = this;
		//Asc.editor = Asc['editor'] = AscCommon['editor'] = AscCommon.editor = this; // ToDo сделать это!
		this.HtmlElement = document.getElementById(this.HtmlElementName);

		// init OnMessage
		AscCommon.InitOnMessage(function(error, url)
		{
			if (c_oAscError.ID.No !== error)
			{
				t.sendEvent("asc_onError", error, c_oAscError.Level.NoCritical);
			}
			else
			{
				t._addImageUrl(url);
			}

			t.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);
		});

		AscCommon.loadSdk(this._editorNameById(), function()
		{
			t.isLoadFullApi = true;

			if (t.DocInfo && t.DocInfo.get_OfflineApp())
			{
				t._OfflineAppDocumentStartLoad();
			}

			t._onEndLoadSdk();
			t.onEndLoadFile(null);
		});
	};
	baseEditorsApi.prototype._editorNameById                 = function()
	{
		var res = '';
		switch (this.editorId)
		{
			case c_oEditorId.Word:
				res = 'word';
				break;
			case c_oEditorId.Spreadsheet:
				res = 'cell';
				break;
			case c_oEditorId.Presentation:
				res = 'slide';
				break;
		}
		return res;
	};
	baseEditorsApi.prototype.getEditorId                     = function()
	{
		return this.editorId;
	};
	baseEditorsApi.prototype.asc_GetFontThumbnailsPath       = function()
	{
		return '../Common/Images/';
	};
	baseEditorsApi.prototype.asc_getDocumentName             = function()
	{
		return this.documentTitle;
	};
	baseEditorsApi.prototype.asc_setDocInfo                  = function(oDocInfo)
	{
		if (oDocInfo)
		{
			this.DocInfo = oDocInfo;
		}

		if (this.DocInfo)
		{
			this.documentId          = this.DocInfo.get_Id();
			this.documentUserId      = this.DocInfo.get_UserId();
			this.documentUrl         = this.DocInfo.get_Url();
			this.documentTitle       = this.DocInfo.get_Title();
			this.documentFormat      = this.DocInfo.get_Format();
			this.documentCallbackUrl = this.DocInfo.get_CallbackUrl();
			this.documentVKey        = this.DocInfo.get_VKey();

			this.documentOpenOptions = this.DocInfo.asc_getOptions();

			this.User = new AscCommon.asc_CUser();
			this.User.setId(this.DocInfo.get_UserId());
			this.User.setUserName(this.DocInfo.get_UserName());

			//чтобы в versionHistory был один documentId для auth и open
			this.CoAuthoringApi.setDocId(this.documentId);
		}

		if (undefined !== window["AscDesktopEditor"] && offlineMode != this.documentUrl)
		{
			window["AscDesktopEditor"]["SetDocumentName"](this.documentTitle);
		}
	};
	baseEditorsApi.prototype.asc_enableKeyEvents             = function(isEnabled)
	{
	};
	// Copy/Past/Cut
	baseEditorsApi.prototype.asc_IsFocus                     = function(bIsNaturalFocus)
	{
	};
	// target pos
	baseEditorsApi.prototype.asc_LockTargetUpdate		     = function(isLock)
	{
		this.isLockTargetUpdate = isLock;
	};
	// Просмотр PDF
	baseEditorsApi.prototype.isPdfViewer                     = function()
	{
		return false;
	};
	// Events
	baseEditorsApi.prototype.sendEvent                       = function()
	{
	};
	baseEditorsApi.prototype.SendOpenProgress                = function()
	{
		this.sendEvent("asc_onOpenDocumentProgress", this.OpenDocumentProgress);
	};
	baseEditorsApi.prototype.sync_InitEditorFonts            = function(gui_fonts)
	{
		if (!this.isViewMode) {
			this.sendEvent("asc_onInitEditorFonts", gui_fonts);
		}
	};
	baseEditorsApi.prototype.sync_StartAction                = function(type, id)
	{
		this.sendEvent('asc_onStartAction', type, id);
		//console.log("asc_onStartAction: type = " + type + " id = " + id);

		if (c_oAscAsyncActionType.BlockInteraction === type)
		{
			this.incrementCounterLongAction();
		}
	};
	baseEditorsApi.prototype.sync_EndAction                  = function(type, id)
	{
		this.sendEvent('asc_onEndAction', type, id);
		//console.log("asc_onEndAction: type = " + type + " id = " + id);

		if (c_oAscAsyncActionType.BlockInteraction === type)
		{
			this.decrementCounterLongAction();
		}
	};
	baseEditorsApi.prototype.sync_TryUndoInFastCollaborative = function()
	{
		this.sendEvent("asc_OnTryUndoInFastCollaborative");
	};
	baseEditorsApi.prototype.asc_enableKeyEvents             = function(val)
	{
	};
	baseEditorsApi.prototype.asc_setViewMode                 = function()
	{
	};
	baseEditorsApi.prototype.getViewMode                     = function()
	{
	};
	baseEditorsApi.prototype.isLongAction                    = function()
	{
		return (0 !== this.IsLongActionCurrent);
	};
	baseEditorsApi.prototype.incrementCounterLongAction      = function()
	{
		++this.IsLongActionCurrent;
	};
	baseEditorsApi.prototype.decrementCounterLongAction      = function()
	{
		this.IsLongActionCurrent--;
		if (this.IsLongActionCurrent < 0)
		{
			this.IsLongActionCurrent = 0;
		}

		if (!this.isLongAction())
		{
			var _length = this.LongActionCallbacks.length;
			for (var i = 0; i < _length; i++)
			{
				this.LongActionCallbacks[i](this.LongActionCallbacksParams[i]);
			}
			this.LongActionCallbacks.splice(0, _length);
			this.LongActionCallbacksParams.splice(0, _length);
		}
	};
	baseEditorsApi.prototype.checkLongActionCallback         = function(_callback, _param)
	{
		if (this.isLongAction())
		{
			this.LongActionCallbacks[this.LongActionCallbacks.length]             = _callback;
			this.LongActionCallbacksParams[this.LongActionCallbacksParams.length] = _param;
			return false;
		}
		else
		{
			return true;
		}
	};
	/**
	 * Функция для загрузчика шрифтов (нужно ли грузить default шрифты). Для Excel всегда возвращаем false
	 * @returns {boolean}
	 */
	baseEditorsApi.prototype.IsNeedDefaultFonts = function()
	{
		var res = false;
		switch (this.editorId)
		{
			case c_oEditorId.Word:
				res = !this.isPdfViewer();
				break;
			case c_oEditorId.Presentation:
				res = true;
				break;
		}
		return res;
	};
	baseEditorsApi.prototype.onPrint                             = function()
	{
		this.sendEvent("asc_onPrint");
	};
	// Open
	baseEditorsApi.prototype.asc_LoadDocument                    = function(isVersionHistory, isRepeat)
	{
		// Меняем тип состояния (на открытие)
		this.advancedOptionsAction = AscCommon.c_oAscAdvancedOptionsAction.Open;
		var rData                  = null;
		if (offlineMode !== this.documentUrl)
		{
			rData = {
				"c"             : 'open',
				"id"            : this.documentId,
				"userid"        : this.documentUserId,
				"format"        : this.documentFormat,
				"vkey"          : this.documentVKey,
				"url"           : this.documentUrl,
				"title"         : this.documentTitle,
				"embeddedfonts" : this.isUseEmbeddedCutFonts,
				"viewmode"      : this.getViewMode()
			};
			if (isVersionHistory)
			{
				//чтобы результат пришел только этому соединению, а не всем кто в документе
				rData["userconnectionid"] = this.CoAuthoringApi.getUserConnectionId();
			}
		}
		this.CoAuthoringApi.auth(this.getViewMode(), rData);

		if (!isRepeat) {
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);
		}

		if (offlineMode === this.documentUrl)
		{
			this.documentUrl = '/sdkjs/' + this._editorNameById() + '/document/';
			this.DocInfo.asc_putOfflineApp(true);
		}
	};
	baseEditorsApi.prototype._OfflineAppDocumentStartLoad        = function()
	{
		var t             = this;
		var scriptElem    = document.createElement('script');
		scriptElem.onload = scriptElem.onerror = function()
		{
			t._OfflineAppDocumentEndLoad();
		};

		scriptElem.setAttribute('src', this.documentUrl + 'editor.js');
		scriptElem.setAttribute('type', 'text/javascript');
		document.getElementsByTagName('head')[0].appendChild(scriptElem);
	};
	baseEditorsApi.prototype._onOpenCommand                      = function(data)
	{
	};
	baseEditorsApi.prototype._onNeedParams                       = function(data)
	{
	};
	baseEditorsApi.prototype.asyncServerIdEndLoaded              = function()
	{
	};
	baseEditorsApi.prototype.asyncFontStartLoaded                = function()
	{
		// здесь прокинуть евент о заморозке меню
		this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
	};
	baseEditorsApi.prototype.asyncImageStartLoaded               = function()
	{
		// здесь прокинуть евент о заморозке меню
	};
	baseEditorsApi.prototype.asyncImagesDocumentStartLoaded      = function()
	{
		// евент о заморозке не нужен... оно и так заморожено
		// просто нужно вывести информацию в статус бар (что началась загрузка картинок)
	};
	// Save
	baseEditorsApi.prototype.processSavedFile                    = function(url, downloadType)
	{
		if (AscCommon.DownloadType.None !== downloadType)
		{
			this.sendEvent(downloadType, url, function(hasError)
			{
			});
		}
		else
		{
			AscCommon.getFile(url);
		}
	};
	// Выставление интервала автосохранения (0 - означает, что автосохранения нет)
	baseEditorsApi.prototype.asc_setAutoSaveGap                  = function(autoSaveGap)
	{
		if (typeof autoSaveGap === "number")
		{
			this.autoSaveGap = autoSaveGap * 1000; // Нам выставляют в секундах
		}
	};
	// send chart message
	baseEditorsApi.prototype.asc_coAuthoringChatSendMessage      = function(message)
	{
		this.CoAuthoringApi.sendMessage(message);
	};
	// get chart messages
	baseEditorsApi.prototype.asc_coAuthoringChatGetMessages      = function()
	{
		this.CoAuthoringApi.getMessages();
	};
	// get users, возвращается массив users
	baseEditorsApi.prototype.asc_coAuthoringGetUsers             = function()
	{
		this.CoAuthoringApi.getUsers();
	};
	// get permissions
	baseEditorsApi.prototype.asc_getEditorPermissions            = function()
	{
		this._coAuthoringInit();
	};
	baseEditorsApi.prototype._onEndPermissions                   = function()
	{
		if (this.isOnFirstConnectEnd && this.isOnLoadLicense)
		{
			this.sendEvent('asc_onGetEditorPermissions', new AscCommon.asc_CAscEditorPermissions());
		}
	};
	// CoAuthoring
	baseEditorsApi.prototype._coAuthoringInit                    = function()
	{
		var t = this;
		//Если User не задан, отключаем коавторинг.
		if (null == this.User || null == this.User.asc_getId())
		{
			this.User = new AscCommon.asc_CUser();
			this.User.setId("Unknown");
			this.User.setUserName("Unknown");
		}
		//в обычном серверном режиме портим ссылку, потому что CoAuthoring теперь имеет встроенный адрес
		//todo надо использовать проверку get_OfflineApp
		if (!(window['NATIVE_EDITOR_ENJINE'] || offlineMode === this.documentUrl))
		{
			this.CoAuthoringApi.set_url(null);
		}

		this.CoAuthoringApi.onMessage                 = function(e, clear)
		{
			t.sendEvent('asc_onCoAuthoringChatReceiveMessage', e, clear);
		};
		this.CoAuthoringApi.onAuthParticipantsChanged = function(e, count)
		{
			t.sendEvent("asc_onAuthParticipantsChanged", e, count);
		};
		this.CoAuthoringApi.onParticipantsChanged     = function(e, CountEditUsers)
		{
			t.sendEvent("asc_onParticipantsChanged", e, CountEditUsers);
		};
		this.CoAuthoringApi.onSpellCheckInit          = function(e)
		{
			t.SpellCheckUrl = e;
			t._coSpellCheckInit();
		};
		this.CoAuthoringApi.onSetIndexUser            = function(e)
		{
			AscCommon.g_oIdCounter.Set_UserId('' + e);
		};
		this.CoAuthoringApi.onFirstLoadChangesEnd     = function()
		{
			t.asyncServerIdEndLoaded();
		};
		this.CoAuthoringApi.onFirstConnect            = function()
		{
			if (t.isOnFirstConnectEnd)
			{
				if (t.CoAuthoringApi.get_isAuth()) {
					t.CoAuthoringApi.auth(t.getViewMode());
				} else {
					//первый запрос или ответ не дошел надо повторить открытие
					t.asc_LoadDocument(false, true);
				}
			}
			else
			{
				t.isOnFirstConnectEnd = true;
				t._onEndPermissions();
			}
		};
		this.CoAuthoringApi.onLicense                 = function(res)
		{
			t.licenseResult   = res;
			t.isOnLoadLicense = true;
			t._onEndPermissions();
		};
		this.CoAuthoringApi.onWarning                 = function(e)
		{
			t.sendEvent('asc_onError', c_oAscError.ID.Warning, c_oAscError.Level.NoCritical);
		};
		/**
		 * Event об отсоединении от сервера
		 * @param {jQuery} e  event об отсоединении с причиной
		 * @param {Bool} isDisconnectAtAll  окончательно ли отсоединяемся(true) или будем пробовать сделать reconnect(false) + сами отключились
		 * @param {Bool} isCloseCoAuthoring
		 */
		this.CoAuthoringApi.onDisconnect = function(e, isDisconnectAtAll, isCloseCoAuthoring)
		{
			if (AscCommon.ConnectionState.None === t.CoAuthoringApi.get_state())
			{
				t.asyncServerIdEndLoaded();
			}
			if (isDisconnectAtAll)
			{
				// Посылаем наверх эвент об отключении от сервера
				t.sendEvent('asc_onCoAuthoringDisconnect');
				// И переходим в режим просмотра т.к. мы не можем сохранить файл
				t.asc_setViewMode(true);
				t.sendEvent('asc_onError', isCloseCoAuthoring ? c_oAscError.ID.UserDrop : c_oAscError.ID.CoAuthoringDisconnect, c_oAscError.Level.NoCritical);
			}
		};
		this.CoAuthoringApi.onDocumentOpen = function(inputWrap)
		{
			if (inputWrap["data"])
			{
				var input = inputWrap["data"];
				switch (input["type"])
				{
					case 'reopen':
					case 'open':
						switch (input["status"])
						{
							case "updateversion":
							case "ok":
								var urls = input["data"];
								AscCommon.g_oDocumentUrls.init(urls);
								if (null != urls['Editor.bin'])
								{
									if ('ok' === input["status"] || t.getViewMode())
									{
										t._onOpenCommand(urls['Editor.bin']);
									}
									else
									{
										t.sendEvent("asc_onDocumentUpdateVersion", function()
										{
											if (t.isCoAuthoringEnable)
											{
												t.asc_coAuthoringDisconnect();
											}
											t._onOpenCommand(urls['Editor.bin']);
										})
									}
								}
								else
								{
									t.sendEvent("asc_onError", c_oAscError.ID.ConvertationError, c_oAscError.Level.Critical);
								}
								break;
							case "needparams":
								t._onNeedParams(input["data"]);
								break;
							case "needpassword":
								t.sendEvent("asc_onError", Asc.c_oAscError.ID.ConvertationPassword, c_oAscError.Level.Critical);
								break;
							case "err":
								t.sendEvent("asc_onError", AscCommon.mapAscServerErrorToAscError(parseInt(input["data"])), c_oAscError.Level.Critical);
								break;
						}
						break;
					default:
						if (t.fCurCallback)
						{
							t.fCurCallback(input);
							t.fCurCallback = null;
						}
						else
						{
							t.sendEvent("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
						}
						break;
				}
			}
		};

		this._coAuthoringInitEnd();
		this.CoAuthoringApi.init(this.User, this.documentId, this.documentCallbackUrl, 'fghhfgsjdgfjs', this.editorId, this.documentFormatSave);
	};
	baseEditorsApi.prototype._coAuthoringInitEnd                 = function()
	{
	};
	// server disconnect
	baseEditorsApi.prototype.asc_coAuthoringDisconnect           = function()
	{
		this.CoAuthoringApi.disconnect();
		this.isCoAuthoringEnable = false;

		// Выставляем view-режим
		this.asc_setViewMode(true);
	};
	baseEditorsApi.prototype.asc_stopSaving                      = function()
	{
		this.incrementCounterLongAction();
	};
	baseEditorsApi.prototype.asc_continueSaving                  = function()
	{
		this.decrementCounterLongAction();
	};
	// SpellCheck
	baseEditorsApi.prototype._coSpellCheckInit                   = function()
	{
	};
	// Images & Charts & TextArts
	baseEditorsApi.prototype.asc_setChartTranslate               = function(translate)
	{
		this.chartTranslate = translate;
	};
	baseEditorsApi.prototype.asc_setTextArtTranslate             = function(translate)
	{
		this.textArtTranslate = translate;
	};
	baseEditorsApi.prototype.asc_getChartPreviews                = function(chartType)
	{
		return this.chartPreviewManager.getChartPreviews(chartType);
	};
	baseEditorsApi.prototype.asc_getTextArtPreviews              = function()
	{
		return this.textArtPreviewManager.getWordArtStyles();
	};
	baseEditorsApi.prototype.asc_onOpenChartFrame                = function()
	{
		this.isOpenedChartFrame = true;
	};
	baseEditorsApi.prototype.asc_onCloseChartFrame               = function()
	{
		this.isOpenedChartFrame = false;
	};
	baseEditorsApi.prototype.asc_setInterfaceDrawImagePlaceShape = function(elementId)
	{
		this.shapeElementId = elementId;
	};
	baseEditorsApi.prototype.asc_getPropertyEditorShapes         = function()
	{
		return [AscCommon.g_oAutoShapesGroups, AscCommon.g_oAutoShapesTypes];
	};
	baseEditorsApi.prototype.asc_getPropertyEditorTextArts       = function()
	{
		return [AscCommon.g_oPresetTxWarpGroups, AscCommon.g_PresetTxWarpTypes];
	};
	// Add image
	baseEditorsApi.prototype._addImageUrl                        = function()
	{
	};
	baseEditorsApi.prototype.asc_addImage                        = function()
	{
		var t = this;
		AscCommon.ShowImageFileDialog(this.documentId, this.documentUserId, function(error, files)
		{
			t._uploadCallback(error, files);
		}, function(error)
		{
			if (c_oAscError.ID.No !== error)
			{
				t.sendEvent("asc_onError", error, c_oAscError.Level.NoCritical);
			}
			t.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);
		});
	};
	baseEditorsApi.prototype._uploadCallback                     = function(error, files)
	{
		var t = this;
		if (c_oAscError.ID.No !== error)
		{
			this.sendEvent("asc_onError", error, c_oAscError.Level.NoCritical);
		}
		else
		{
			AscCommon.UploadImageFiles(files, this.documentId, this.documentUserId, function(error, url)
			{
				if (c_oAscError.ID.No !== error)
				{
					t.sendEvent("asc_onError", error, c_oAscError.Level.NoCritical);
				}
				else
				{
					t._addImageUrl(url);
				}
			});
		}
	};

	//метод, который подменяет callback загрузки в каждом редакторе, TODO: переделать, сделать одинаково в о всех редакторах
	baseEditorsApi.prototype.asc_replaceLoadImageCallback = function(fCallback)
	{
	};

	baseEditorsApi.prototype.asc_loadLocalImageAndAction = function(sLocalImage, fCallback)
	{
		this.ImageLoader.LoadImage(AscCommon.getFullImageSrc2(sLocalImage), 1);
		this.asc_replaceLoadImageCallback(fCallback);
	};

	baseEditorsApi.prototype.asc_checkImageUrlAndAction = function(sImageUrl, fCallback)
	{
		var sLocalImage = AscCommon.g_oDocumentUrls.getImageLocal(sImageUrl);
		if (sLocalImage)
		{
			this.asc_loadLocalImageAndAction(sLocalImage, fCallback);
			return;
		}
		var oThis = this;
		AscCommon.sendImgUrls(oThis, [sImageUrl], function(data)
		{
			if (data[0] && data[0].path != null)
			{
				oThis.asc_loadLocalImageAndAction(AscCommon.g_oDocumentUrls.imagePath2Local(data[0].path), fCallback);
			}
		}, this.editorId === c_oEditorId.Spreadsheet);
	};

	baseEditorsApi.prototype.asc_addOleObject = function(oPluginData)
	{
		Asc.CPluginData_wrap(oPluginData);
		var oThis      = this;
		var oThis      = this;
		var sImgSrc    = oPluginData.getAttribute("imgSrc");
		var nWidthPix  = oPluginData.getAttribute("widthPix");
		var nHeightPix = oPluginData.getAttribute("heightPix");
		var fWidth     = oPluginData.getAttribute("width");
		var fHeight    = oPluginData.getAttribute("height");
		var sData      = oPluginData.getAttribute("data");
		var sGuid      = oPluginData.getAttribute("guid");
		if (typeof sImgSrc === "string" && sImgSrc.length > 0 && typeof sData === "string"
			&& typeof sGuid === "string" && sGuid.length > 0
			&& AscFormat.isRealNumber(nWidthPix) && AscFormat.isRealNumber(nHeightPix)
			&& AscFormat.isRealNumber(fWidth) && AscFormat.isRealNumber(fHeight)
		)
			this.asc_checkImageUrlAndAction(sImgSrc, function(oImage)
			{
				oThis.asc_addOleObjectAction(AscCommon.g_oDocumentUrls.getImageLocal(oImage.src), sData, sGuid, fWidth, fHeight, nWidthPix, nHeightPix);
			});
	};

	baseEditorsApi.prototype.asc_editOleObject = function(oPluginData)
	{
		Asc.CPluginData_wrap(oPluginData);
		var oThis      = this;
		var bResize    = oPluginData.getAttribute("resize");
		var sImgSrc    = oPluginData.getAttribute("imgSrc");
		var oOleObject = AscCommon.g_oTableId.Get_ById(oPluginData.getAttribute("objectId"));
		var nWidthPix  = oPluginData.getAttribute("widthPix");
		var nHeightPix = oPluginData.getAttribute("heightPix");
		var sData      = oPluginData.getAttribute("data");
		if (typeof sImgSrc === "string" && sImgSrc.length > 0 && typeof sData === "string"
			&& oOleObject && AscFormat.isRealNumber(nWidthPix) && AscFormat.isRealNumber(nHeightPix))
		{
			this.asc_checkImageUrlAndAction(sImgSrc, function(oImage)
			{
				oThis.asc_editOleObjectAction(bResize, oOleObject, AscCommon.g_oDocumentUrls.getImageLocal(oImage.src), sData, nWidthPix, nHeightPix);
			});
		}
	};

	baseEditorsApi.prototype.asc_addOleObjectAction = function(sLocalUrl, sData, sApplicationId, fWidth, fHeight)
	{
	};

	baseEditorsApi.prototype.asc_editOleObjectAction = function(bResize, oOleObject, sImageUrl, sData, nPixWidth, nPixHeight)
	{
	};

	// Version History
	baseEditorsApi.prototype.asc_showRevision   = function(newObj)
	{
	};
	baseEditorsApi.prototype.asc_undoAllChanges = function()
	{
	};
	/**
	 * Эта функция возвращает true, если есть изменения или есть lock-и в документе
	 */
	baseEditorsApi.prototype.asc_isDocumentCanSave = function()
	{
		return this.isDocumentCanSave;
	};
	// Offline mode
	baseEditorsApi.prototype.asc_isOffline  = function()
	{
		return (window.location.protocol.indexOf("file") == 0) ? true : false;
	};
	baseEditorsApi.prototype.asc_getUrlType = function(url)
	{
		return AscCommon.getUrlType(url);
	};

	baseEditorsApi.prototype.openDocument  = function()
	{
	};
	baseEditorsApi.prototype.onEndLoadFile = function(result)
	{
		if (result)
		{
			this.openResult = result;
		}
		if (this.isLoadFullApi && this.openResult)
		{
			this.openDocument(this.openResult);
		}

	};
	baseEditorsApi.prototype._onEndLoadSdk = function()
	{
		// init drag&drop
		var t = this;
		AscCommon.InitDragAndDrop(this.HtmlElement, function(error, files)
		{
			t._uploadCallback(error, files);
		});

		AscFonts.g_fontApplication.Init();

		this.FontLoader  = AscCommon.g_font_loader;
		this.ImageLoader = AscCommon.g_image_loader;
		this.FontLoader.put_Api(this);
		this.ImageLoader.put_Api(this);
		this.FontLoader.SetStandartFonts();

		this.chartTranslate        = this.chartTranslate ? this.chartTranslate : new Asc.asc_CChartTranslate();
		this.textArtTranslate      = this.textArtTranslate ? this.textArtTranslate : new Asc.asc_TextArtTranslate();
		this.chartPreviewManager   = new AscCommon.ChartPreviewManager();
		this.textArtPreviewManager = new AscCommon.TextArtPreviewManager();

		AscFormat.initStyleManager();

		if (null !== this.tmpFocus)
		{
			this.asc_enableKeyEvents(this.tmpFocus);
		}

		this.pluginsManager     = Asc.createPluginsManager(this);
	};

	baseEditorsApi.prototype.sendStandartTextures = function()
	{
		var _count = AscCommon.g_oUserTexturePresets.length;
		var arr    = new Array(_count),
			b_LoadImage = this._editorNameById() === 'cell';
		for (var i = 0; i < _count; ++i)
		{
			arr[i]       = new AscCommon.asc_CTexture();
			arr[i].Id    = i;
			arr[i].Image = AscCommon.g_oUserTexturePresets[i];
			if (b_LoadImage) {
				this.ImageLoader.LoadImage(AscCommon.g_oUserTexturePresets[i], 1);
			}
		}

		this.sendEvent('asc_onInitStandartTextures', arr);
	};

	// plugins
	baseEditorsApi.prototype.asc_pluginsRegister   = function(basePath, plugins)
	{
		if (null != this.pluginsManager)
			this.pluginsManager.register(basePath, plugins);
	};
	baseEditorsApi.prototype.asc_pluginRun         = function(guid, variation, pluginData)
	{
		if (null != this.pluginsManager)
			this.pluginsManager.run(guid, variation, pluginData);
	};
	baseEditorsApi.prototype.asc_pluginResize      = function(pluginData)
	{
		if (null != this.pluginsManager)
			this.pluginsManager.runResize(pluginData);
	};
	baseEditorsApi.prototype.asc_pluginButtonClick = function(id)
	{
		if (null != this.pluginsManager)
			this.pluginsManager.buttonClick(id);
	};

	// Builder
	baseEditorsApi.prototype.asc_nativeInitBuilder = function()
	{
		this.asc_setDocInfo(new Asc.asc_CDocInfo());
	};
	baseEditorsApi.prototype.asc_SetSilentMode     = function()
	{
	};
	baseEditorsApi.prototype.asc_canPaste          = function()
	{
		return false;
	};
	baseEditorsApi.prototype.asc_Recalculate       = function()
	{
	};


	//----------------------------------------------------------export----------------------------------------------------
	window['AscCommon']                = window['AscCommon'] || {};
	window['AscCommon'].baseEditorsApi = baseEditorsApi;
})(window);

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

var g_oLicenseResult = {
  Error       : 1,
  Expired     : 2,
  Success     : 3,
  UnknownUser : 4,
  Connections : 5
};

var g_sLicenseDefaultUrl = "/license";
var g_sPublicRSAKey = '-----BEGIN CERTIFICATE-----MIIBvTCCASYCCQD55fNzc0WF7TANBgkqhkiG9w0BAQUFADAjMQswCQYDVQQGEwJKUDEUMBIGA1UEChMLMDAtVEVTVC1SU0EwHhcNMTAwNTI4MDIwODUxWhcNMjAwNTI1MDIwODUxWjAjMQswCQYDVQQGEwJKUDEUMBIGA1UEChMLMDAtVEVTVC1SU0EwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBANGEYXtfgDRlWUSDn3haY4NVVQiKI9CzThoua9+DxJuiseyzmBBe7Roh1RPqdvmtOHmEPbJ+kXZYhbozzPRbFGHCJyBfCLzQfVos9/qUQ88u83b0SFA2MGmQWQAlRtLy66EkR4rDRwTj2DzR4EEXgEKpIvo8VBs/3+sHLF3ESgAhAgMBAAEwDQYJKoZIhvcNAQEFBQADgYEAEZ6mXFFq3AzfaqWHmCy1ARjlauYAa8ZmUFnLm0emg9dkVBJ63aEqARhtok6bDQDzSJxiLpCEF6G4b/Nv/M/MLyhP+OoOTmETMegAVQMq71choVJyOFE5BtQa6M/lCHEOya5QUfoRF2HF9EjRF44K3OK+u3ivTSj3zwjtpudY5Xo=-----END CERTIFICATE-----';

function CheckLicense(licenseUrl, customerId, userId, userFirstName, userLastName, callback) {
  callback(true, g_oLicenseResult.Success);
  return;

  licenseUrl = licenseUrl ? licenseUrl : g_sLicenseDefaultUrl;
  g_fGetJSZipUtils().getBinaryContent(licenseUrl, function(err, data) {
    if (err) {
      callback(true, g_oLicenseResult.Error);
      return;
    }

    try {
      var tmpSize;
      var maxSize = 0x4000;
      var sTextData = '';
      for (var i = 0; i < data.byteLength; i += maxSize) {
        tmpSize = data.byteLength - i;
        sTextData += String.fromCharCode.apply(null, new Uint8Array(data, i, (tmpSize < maxSize) ? tmpSize : maxSize));
      }
      var oLicense = JSON.parse(sTextData);

      var hSig = oLicense['signature'];
      delete oLicense['signature'];

      var x509 = new X509();
      x509.readCertPEM(g_sPublicRSAKey);
      var isValid = x509.subjectPublicKeyRSA.verifyString(JSON.stringify(oLicense), hSig);
      callback(false, isValid ? CheckUserInLicense(customerId, userId, userFirstName, userLastName, oLicense) : g_oLicenseResult.Error);
    } catch (e) {
      callback(true, g_oLicenseResult.Error);
    }
  });
}
/**
 *
 * @param customerId
 * @param userId
 * @param userFirstName
 * @param userLastName
 * @param oLicense
 * @returns {boolean}
 */
function CheckUserInLicense(customerId, userId, userFirstName, userLastName, oLicense) {
  var res = g_oLicenseResult.Error;
  var superuser = 'onlyoffice';
  try {
    if (oLicense['users']) {
      var userName = (null == userFirstName ? '' : userFirstName) + (null == userLastName ? '' : userLastName);
      var sUserHash = CryptoJS.SHA256(userId + userName).toString(CryptoJS.enc.Hex).toLowerCase();
      var checkUserHash = false;
      if (customerId === oLicense['customer_id'] || oLicense['customer_id'] === (sUserHash = superuser)) {
        // users для новой версии - массив
        checkUserHash = (-1 !== oLicense['users'].indexOf(sUserHash));
        res = g_oLicenseResult.UnknownUser;
      }
      if (checkUserHash) {
        var endDate = new Date(oLicense['end_date']);
        res = (endDate >= new Date()) ? g_oLicenseResult.Success : g_oLicenseResult.Expired;
      }
    }
  } catch (e) {
    res = g_oLicenseResult.Error;
  }
  return res;
}

AscCommon.baseEditorsApi.prototype._onCheckLicenseEnd = function(err, res) {
  this.licenseResult = {err: err, res: res};
  this._onEndPermissions();
};
AscCommon.baseEditorsApi.prototype._onEndPermissions = function () {
  if (this.isOnFirstConnectEnd && this.isOnLoadLicense) {
    var oResult = new AscCommon.asc_CAscEditorPermissions();
    if (null !== this.licenseResult) {
      var type = this.licenseResult['type'];
      oResult.asc_setCanLicense(g_oLicenseResult.Success === type);
      oResult.asc_setCanBranding(g_oLicenseResult.Error !== type); // Для тех, у кого есть лицензия, branding доступен
      oResult.asc_setCanBranding(g_oLicenseResult.Error !== type); // Для тех, у кого есть лицензия, branding доступен
      oResult.asc_setIsLight(this.licenseResult['light']);
    }
    this.sendEvent('asc_onGetEditorPermissions', oResult);
  }
};

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

var editor;
(/**
 * @param {Window} window
 * @param {undefined} undefined
 */
  function(window, undefined) {
  var asc = window["Asc"];
  var prot;

  var c_oAscAdvancedOptionsAction = AscCommon.c_oAscAdvancedOptionsAction;
  var DownloadType = AscCommon.DownloadType;
  var c_oAscLockTypes = AscCommon.c_oAscLockTypes;
  var CColor = AscCommon.CColor;
  var g_oDocumentUrls = AscCommon.g_oDocumentUrls;
  var sendCommand = AscCommon.sendCommand;
  var mapAscServerErrorToAscError = AscCommon.mapAscServerErrorToAscError;
  var parserHelp = AscCommon.parserHelp;
  var g_oIdCounter = AscCommon.g_oIdCounter;
  var g_oTableId = AscCommon.g_oTableId;

  var c_oAscLockTypeElem = AscCommonExcel.c_oAscLockTypeElem;

  var c_oAscError = asc.c_oAscError;
  var c_oAscFileType = asc.c_oAscFileType;
  var c_oAscAsyncAction = asc.c_oAscAsyncAction;
  var c_oAscAdvancedOptionsID = asc.c_oAscAdvancedOptionsID;
  var c_oAscAsyncActionType = asc.c_oAscAsyncActionType;

  var History = null;


  /**
   *
   * @param config
   * @param eventsHandlers
   * @constructor
   * @returns {spreadsheet_api}
   * @extends {AscCommon.baseEditorsApi}
   */
  function spreadsheet_api(config) {
    spreadsheet_api.superclass.constructor.call(this, config, AscCommon.c_oEditorId.Spreadsheet);

    /************ private!!! **************/
    this.topLineEditorName = config['id-input'] || '';
    this.topLineEditorElement = null;

    this.controller = null;

    this.handlers = new AscCommonExcel.asc_CHandlersList();
    // Вид печати
    this.adjustPrint = null;

    this.fontRenderingMode = Asc.c_oAscFontRenderingModeType.hintingAndSubpixeling;
    this.wb = null;
    this.wbModel = null;
    this.tmpLocale = null;

    this.documentFormatSave = c_oAscFileType.XLSX;

    // объекты, нужные для отправки в тулбар (шрифты, стили)
    this._gui_control_colors = null;
    this._gui_color_schemes = null;
    this.GuiControlColorsMap = null;
    this.IsSendStandartColors = false;

    this.asyncMethodCallback = undefined;

    // Переменная отвечает, загрузились ли фонты
    this.FontLoadWaitComplete = false;
    // Переменная отвечает, отрисовали ли мы все (иначе при рестарте, получится переинициализация)
    this.DocumentLoadComplete = false;
    // Переменная, которая отвечает, послали ли мы окончание открытия документа
    this.IsSendDocumentLoadCompleate = false;
    //текущий обьект куда записываются информация для update, когда принимаются изменения в native редакторе
    this.oRedoObjectParamNative = null;

    this.collaborativeEditing = null;

    // AutoSave
    this.lastSaveTime = null;				// Время последнего сохранения
    this.autoSaveGapRealTime = 30;	  // Интервал быстрого автосохранения (когда выставлен флаг realtime) - 30 мс.
    this.autoSaveGapFast = 2000;			// Интервал быстрого автосохранения (когда человек один) - 2 сек.
    this.autoSaveGapSlow = 10 * 60 * 1000;	// Интервал медленного автосохранения (когда совместно) - 10 минут

    // Shapes
    this.isStartAddShape = false;
    this.shapeElementId = null;
    this.textArtElementId = null;
    this.isImageChangeUrl = false;
    this.isShapeImageChangeUrl = false;
    this.isTextArtChangeUrl = false;

    //находится ли фокус в рабочей области редактора(используется для copy/paste в MAC)
    // ToDo убрать, когда Гоша поправит clipboard.js
    this.IsFocus = null;

    this.formulasList = null;	// Список всех формул

    this._init();
    return this;
  }
  AscCommon.extendClass(spreadsheet_api, AscCommon.baseEditorsApi);

  spreadsheet_api.prototype.sendEvent = function() {
    this.handlers.trigger.apply(this.handlers, arguments);
  };

  spreadsheet_api.prototype._init = function() {
    spreadsheet_api.superclass._init.call(this);
    this.topLineEditorElement = document.getElementById(this.topLineEditorName);
    // ToDo нужно ли это
    asc['editor'] = ( asc['editor'] || this );
    AscCommon.AscBrowser.checkZoom();
  };

  spreadsheet_api.prototype.asc_CheckGuiControlColors = function() {
    // потом реализовать проверку на то, что нужно ли посылать

    var arr_colors = new Array(10);
    var _count = arr_colors.length;
    for (var i = 0; i < _count; ++i) {
      var color = AscCommonExcel.g_oColorManager.getThemeColor(i);
      arr_colors[i] = new CColor(color.getR(), color.getG(), color.getB());
    }

    // теперь проверим
    var bIsSend = false;
    if (this.GuiControlColorsMap != null) {
      for (var i = 0; i < _count; ++i) {
        var _color1 = this.GuiControlColorsMap[i];
        var _color2 = arr_colors[i];

        if ((_color1.r !== _color2.r) || (_color1.g !== _color2.g) || (_color1.b !== _color2.b)) {
          bIsSend = true;
          break;
        }
      }
    } else {
      this.GuiControlColorsMap = new Array(_count);
      bIsSend = true;
    }

    if (bIsSend) {
      for (var i = 0; i < _count; ++i) {
        this.GuiControlColorsMap[i] = arr_colors[i];
      }

      this.asc_SendControlColors();
    }
  };

  spreadsheet_api.prototype.asc_SendControlColors = function() {
    var standart_colors = null;
    if (!this.IsSendStandartColors) {
      var standartColors = AscCommon.g_oStandartColors;
      var _c_s = standartColors.length;
      standart_colors = new Array(_c_s);

      for (var i = 0; i < _c_s; ++i) {
        standart_colors[i] = new CColor(standartColors[i].R, standartColors[i].G, standartColors[i].B);
      }

      this.IsSendStandartColors = true;
    }

    var _count = this.GuiControlColorsMap.length;

    var _ret_array = new Array(_count * 6);
    var _cur_index = 0;

    for (var i = 0; i < _count; ++i) {
      var basecolor = AscCommonExcel.g_oColorManager.getThemeColor(i);
      var aTints = AscCommonExcel.g_oThemeColorsDefaultModsSpreadsheet[AscCommon.GetDefaultColorModsIndex(basecolor.getR(), basecolor.getG(), basecolor.getB())];
      for (var j = 0, length = aTints.length; j < length; ++j) {
        var tint = aTints[j];
        var color = AscCommonExcel.g_oColorManager.getThemeColor(i, tint);
        _ret_array[_cur_index] = new CColor(color.getR(), color.getG(), color.getB());
        _cur_index++;
      }
    }

    this.asc_SendThemeColors(_ret_array, standart_colors);
  };

  spreadsheet_api.prototype.asc_SendThemeColorScheme = function() {
    var infos = [];
    var _index = 0;

    var _c = null;

    // user scheme
    var oColorScheme = AscCommon.g_oUserColorScheme;
    var _count_defaults = oColorScheme.length;
    for (var i = 0; i < _count_defaults; ++i) {
      var _obj = oColorScheme[i];
      infos[_index] = new AscCommon.CAscColorScheme();
      infos[_index].Name = _obj.name;

      _c = _obj.dk1;
      infos[_index].Colors[0] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.lt1;
      infos[_index].Colors[1] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.dk2;
      infos[_index].Colors[2] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.lt2;
      infos[_index].Colors[3] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent1;
      infos[_index].Colors[4] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent2;
      infos[_index].Colors[5] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent3;
      infos[_index].Colors[6] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent4;
      infos[_index].Colors[7] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent5;
      infos[_index].Colors[8] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.accent6;
      infos[_index].Colors[9] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.hlink;
      infos[_index].Colors[10] = new CColor(_c.R, _c.G, _c.B);

      _c = _obj.folHlink;
      infos[_index].Colors[11] = new CColor(_c.R, _c.G, _c.B);

      ++_index;
    }

    // theme colors
    var _theme = this.wbModel.theme;
    var _extra = _theme.extraClrSchemeLst;
    var _count = _extra.length;
    var _rgba = {R: 0, G: 0, B: 0, A: 255};
    for (var i = 0; i < _count; ++i) {
      var _scheme = _extra[i].clrScheme;

      infos[_index] = new AscCommon.CAscColorScheme();
      infos[_index].Name = _scheme.name;

      _scheme.colors[8].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[8].RGBA;
      infos[_index].Colors[0] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[12].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[12].RGBA;
      infos[_index].Colors[1] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[9].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[9].RGBA;
      infos[_index].Colors[2] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[13].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[13].RGBA;
      infos[_index].Colors[3] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[0].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[0].RGBA;
      infos[_index].Colors[4] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[1].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[1].RGBA;
      infos[_index].Colors[5] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[2].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[2].RGBA;
      infos[_index].Colors[6] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[3].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[3].RGBA;
      infos[_index].Colors[7] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[4].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[4].RGBA;
      infos[_index].Colors[8] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[5].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[5].RGBA;
      infos[_index].Colors[9] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[11].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[11].RGBA;
      infos[_index].Colors[10] = new CColor(_c.R, _c.G, _c.B);

      _scheme.colors[10].Calculate(_theme, null, null, null, _rgba);
      _c = _scheme.colors[10].RGBA;
      infos[_index].Colors[11] = new CColor(_c.R, _c.G, _c.B);

      _index++;
    }

    this.asc_SendThemeColorSchemes(infos);
  };

  spreadsheet_api.prototype.asc_getLocaleExample = function(val, number, date) {
    var res = '';
    var cultureInfo = AscCommon.g_aCultureInfos[val];
    if (cultureInfo) {
      var numFormatDigit = AscCommon.oNumFormatCache.get('#,##0.00');

      var formatDate = AscCommonExcel.getShortDateFormat(cultureInfo);
      formatDate += " h:mm";
      if (cultureInfo.AMDesignator && cultureInfo.PMDesignator) {
        formatDate += " AM/PM";
      }
      var numFormatDate = AscCommon.oNumFormatCache.get(formatDate);

      res += numFormatDigit.formatToChart(number, cultureInfo);
      res += '; ';
      res += numFormatDate.formatToChart(date.getExcelDateWithTime(), cultureInfo);
    }
    return res;
  };
  spreadsheet_api.prototype.asc_getLocaleCurrency = function(val) {
    var cultureInfo = AscCommon.g_aCultureInfos[val];
    if (!cultureInfo) {
      cultureInfo = AscCommon.g_aCultureInfos[1033];
    }
    return AscCommonExcel.getCurrencyFormat(cultureInfo, true, true, true);
  };
  spreadsheet_api.prototype.asc_setLocale = function(val) {
    if (!this.isLoadFullApi) {
      this.tmpLocale = val;
      return;
    }
    if (null === val) {
      return;
    }
    AscCommon.setCurrentCultureInfo(val);
    parserHelp.setDigitSeparator(AscCommon.g_oDefaultCultureInfo.NumberDecimalSeparator);
	  if (this.wbModel) {
      AscCommon.oGeneralEditFormatCache.cleanCache();
      AscCommon.oNumFormatCache.cleanCache();
      this.wbModel.rebuildColors();
      if (this.IsSendDocumentLoadCompleate) {
        this._onUpdateAfterApplyChanges();
      }
    }
  };

  spreadsheet_api.prototype.asc_LoadEmptyDocument = function() {
    this.CoAuthoringApi.auth(this.getViewMode());
    this.onEndLoadFile(true);
  };

  spreadsheet_api.prototype._openDocument = function(data) {
    var wb = new AscCommonExcel.Workbook(this.handlers, this);
    this.initGlobalObjects(wb);
    this.wbModel = wb;
    var oBinaryFileReader = new AscCommonExcel.BinaryFileReader();
    oBinaryFileReader.Read(data, wb);
    g_oIdCounter.Set_Load(false);
    return wb;
  };

  spreadsheet_api.prototype.initGlobalObjects = function(wbModel) {
    // History & global counters
    History.init(wbModel);

    g_oTableId.init();
    AscCommonExcel.g_oUndoRedoCell = new AscCommonExcel.UndoRedoCell(wbModel);
    AscCommonExcel.g_oUndoRedoWorksheet = new AscCommonExcel.UndoRedoWoorksheet(wbModel);
    AscCommonExcel.g_oUndoRedoWorkbook = new AscCommonExcel.UndoRedoWorkbook(wbModel);
    AscCommonExcel.g_oUndoRedoCol = new AscCommonExcel.UndoRedoRowCol(wbModel, false);
    AscCommonExcel.g_oUndoRedoRow = new AscCommonExcel.UndoRedoRowCol(wbModel, true);
    AscCommonExcel.g_oUndoRedoComment = new AscCommonExcel.UndoRedoComment(wbModel);
    AscCommonExcel.g_oUndoRedoAutoFilters = new AscCommonExcel.UndoRedoAutoFilters(wbModel);
  };

  spreadsheet_api.prototype.asc_DownloadAs = function(typeFile, bIsDownloadEvent) {//передаем число соответствующее своему формату. например  c_oAscFileType.XLSX
    if (!this.canSave || this.isChartEditor || c_oAscAdvancedOptionsAction.None !== this.advancedOptionsAction) {
      return;
    }

    if (c_oAscFileType.PDF === typeFile) {
      this.adjustPrint = new Asc.asc_CAdjustPrint();
    }
    this._asc_downloadAs(typeFile, c_oAscAsyncAction.DownloadAs, {downloadType: bIsDownloadEvent ? DownloadType.Download: DownloadType.None});
  };

  spreadsheet_api.prototype.asc_Save = function(isAutoSave) {
    if (!this.canSave || this.isChartEditor || c_oAscAdvancedOptionsAction.None !== this.advancedOptionsAction || this.isLongAction()) {
      return;
    }

    this.IsUserSave = !isAutoSave;
    if (this.IsUserSave) {
      this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);
    }
    /* Нужно закрыть редактор (до выставления флага canSave, т.к. мы должны успеть отправить
     asc_onDocumentModifiedChanged для подписки на сборку) Баг http://bugzserver/show_bug.cgi?id=28331 */
    this.asc_closeCellEditor();

    // Не даем пользователю сохранять, пока не закончится сохранение
    this.canSave = false;

    var t = this;
    this.CoAuthoringApi.askSaveChanges(function(e) {
      t.onSaveCallback(e);
    });
  };

  spreadsheet_api.prototype.asc_Print = function(adjustPrint, bIsDownloadEvent) {
    if (window["AscDesktopEditor"]) {
      window.AscDesktopEditor_PrintData = adjustPrint;
      window["AscDesktopEditor"]["Print"]();
      return;
    }

    this.adjustPrint = adjustPrint ? adjustPrint : new Asc.asc_CAdjustPrint();
    this._asc_downloadAs(c_oAscFileType.PDF, c_oAscAsyncAction.Print, {downloadType: bIsDownloadEvent ? DownloadType.Print: DownloadType.None});
  };

  spreadsheet_api.prototype.asc_Copy = function() {
    if (window["AscDesktopEditor"]) {

      var _e = {};
      _e.ctrlKey = true;
      _e.shiftKey = false;
      _e.which = 67;

	  window["AscDesktopEditorButtonMode"] = true;
	  
	  if (!this.asc_getCellEditMode())
		this.controller._onWindowKeyDown(_e);
	  else
		this.wb.cellEditor._onWindowKeyDown(_e);
	  
	  window["AscDesktopEditorButtonMode"] = false;

      return;
    }

    var result = this.wb.copyToClipboardButton();
    this.wb.restoreFocus();
    return result;
  };

  spreadsheet_api.prototype.asc_Paste = function() {
    if (window["AscDesktopEditor"]) {

      var _e = {};
      _e.ctrlKey = true;
      _e.shiftKey = false;
      _e.which = 86;

	  window["AscDesktopEditorButtonMode"] = true;
      
	  if (!this.asc_getCellEditMode())
		this.controller._onWindowKeyDown(_e);
	  else
		this.wb.cellEditor._onWindowKeyDown(_e);
	
	  window["AscDesktopEditorButtonMode"] = false;

      return;
    }

    var result = this.wb.pasteFromClipboardButton();
    this.wb.restoreFocus();
    return result;
  };

  spreadsheet_api.prototype.asc_Cut = function() {
    if (window["AscDesktopEditor"]) {

      var _e = {};
      _e.ctrlKey = true;
      _e.shiftKey = false;
      _e.which = 88;

	  window["AscDesktopEditorButtonMode"] = true;
      
	  if (!this.asc_getCellEditMode())
		this.controller._onWindowKeyDown(_e);
	  else
		this.wb.cellEditor._onWindowKeyDown(_e);	  
	  
	  window["AscDesktopEditorButtonMode"] = false;

      return;
    }

    var result = this.wb.cutToClipboardButton();
    this.wb.restoreFocus();
    return result;
  };

  spreadsheet_api.prototype.asc_CheckCopy = function(_clipboard /* CClipboardData */, _formats)
  {
	var result = this.wb.checkCopyToClipboard(_clipboard, _formats);
	return result;
  };
  
  spreadsheet_api.prototype.asc_bIsEmptyClipboard = function() {
    var result = this.wb.bIsEmptyClipboard();
    this.wb.restoreFocus();
    return result;
  };

  spreadsheet_api.prototype.asc_Undo = function() {
    this.wb.undo();
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_Redo = function() {
    this.wb.redo();
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_Resize = function() {
    if (this.wb) {
      this.wb.resize();
    }
  };

  spreadsheet_api.prototype.asc_addAutoFilter = function(styleName, addFormatTableOptionsObj) {
    var ws = this.wb.getWorksheet();
    return ws.addAutoFilter(styleName, addFormatTableOptionsObj);
  };

  spreadsheet_api.prototype.asc_changeAutoFilter = function(tableName, optionType, val) {
    var ws = this.wb.getWorksheet();
    return ws.changeAutoFilter(tableName, optionType, val);
  };

  spreadsheet_api.prototype.asc_applyAutoFilter = function(autoFilterObject) {
    var ws = this.wb.getWorksheet();
    ws.applyAutoFilter(autoFilterObject);
  };
  
  spreadsheet_api.prototype.asc_applyAutoFilterByType = function(autoFilterObject) {
    var ws = this.wb.getWorksheet();
    ws.applyAutoFilterByType(autoFilterObject);
  };
  
  spreadsheet_api.prototype.asc_reapplyAutoFilter = function(displayName) {
    var ws = this.wb.getWorksheet();
    ws.reapplyAutoFilter(displayName);
  };

  spreadsheet_api.prototype.asc_sortColFilter = function(type, cellId, displayName, color) {
    var ws = this.wb.getWorksheet();
    ws.sortColFilter(type, cellId, displayName, color);
  };

  spreadsheet_api.prototype.asc_getAddFormatTableOptions = function(range) {
    var ws = this.wb.getWorksheet();
    return ws.getAddFormatTableOptions(range);
  };

  spreadsheet_api.prototype.asc_clearFilter = function() {
    var ws = this.wb.getWorksheet();
    return ws.clearFilter();
  };
  
  spreadsheet_api.prototype.asc_clearFilterColumn = function(cellId, displayName) {
    var ws = this.wb.getWorksheet();
    return ws.clearFilterColumn(cellId, displayName);
  };
  
  spreadsheet_api.prototype.asc_changeSelectionFormatTable = function(tableName, optionType) {
    var ws = this.wb.getWorksheet();
    return ws.af_changeSelectionFormatTable(tableName, optionType);
  };
  
  spreadsheet_api.prototype.asc_changeFormatTableInfo = function(tableName, optionType, val) {
    var ws = this.wb.getWorksheet();
    return ws.af_changeFormatTableInfo(tableName, optionType, val);
  };
  
  spreadsheet_api.prototype.asc_insertCellsInTable = function(tableName, optionType) {
    var ws = this.wb.getWorksheet();
    return ws.af_insertCellsInTable(tableName, optionType);
  };
  
  spreadsheet_api.prototype.asc_deleteCellsInTable = function(tableName, optionType) {
    var ws = this.wb.getWorksheet();
    return ws.af_deleteCellsInTable(tableName, optionType);
  };
  
  spreadsheet_api.prototype.asc_changeDisplayNameTable = function(tableName, newName) {
    var ws = this.wb.getWorksheet();
    return ws.af_changeDisplayNameTable(tableName, newName);
  };
  
  spreadsheet_api.prototype.asc_changeTableRange = function(tableName, range) {
    var ws = this.wb.getWorksheet();
    return ws.af_changeTableRange(tableName, range);
  };
  
  spreadsheet_api.prototype.asc_getTablePictures = function (props) 
  { 
	return this.wb.getTablePictures(props); 
  };

  spreadsheet_api.prototype.asc_setMobileVersion = function(isMobile) {
    this.isMobileVersion = isMobile;
    AscCommon.AscBrowser.isMobileVersion = isMobile;
  };

  spreadsheet_api.prototype.getViewMode = function() {
    return this.isViewMode;
  };

  spreadsheet_api.prototype.asc_setViewMode = function(isViewerMode) {
    if (!this.isLoadFullApi) {
      this.isViewMode = isViewerMode;
      return;
    }
    this.controller.setViewerMode(isViewerMode);
    if (this.collaborativeEditing) {
      this.collaborativeEditing.setViewerMode(isViewerMode);
    }

    if (false === isViewerMode) {
      // Загружаем не обрезанные шрифты для полной версии (при редактировании)
      if (this.FontLoader.embedded_cut_manager.bIsCutFontsUse) {
        this.FontLoader.embedded_cut_manager.bIsCutFontsUse = false;
        this.asyncMethodCallback = undefined;
        this.FontLoader.LoadDocumentFonts(this.wbModel.generateFontMap2());
      }

      this.isUseEmbeddedCutFonts = false;

      // Отправка стилей
      this._sendWorkbookStyles();
      if (this.wb) {
        this.wb._initCommentsToSave();
      }

      if (this.IsSendDocumentLoadCompleate && this.collaborativeEditing) {
        // Принимаем чужие изменения
        this.collaborativeEditing.applyChanges();
        // Пересылаем свои изменения
        this.collaborativeEditing.sendChanges();
      }
    }
  };

  spreadsheet_api.prototype.asc_setUseEmbeddedCutFonts = function(bUse) {
    this.isUseEmbeddedCutFonts = bUse;
  };

  /*
   idOption идентификатор дополнительного параметра, пока c_oAscAdvancedOptionsID.CSV.
   option - какие свойства применить, пока массив. для CSV объект asc_CCSVAdvancedOptions(codepage, delimiter)
   exp:	asc_setAdvancedOptions(c_oAscAdvancedOptionsID.CSV, new Asc.asc_CCSVAdvancedOptions(1200, c_oAscCsvDelimiter.Comma) );
   */
  spreadsheet_api.prototype.asc_setAdvancedOptions = function(idOption, option) {
    switch (idOption) {
      case c_oAscAdvancedOptionsID.CSV:
        // Проверяем тип состояния в данный момент
        if (this.advancedOptionsAction === c_oAscAdvancedOptionsAction.Open) {
          var v = {
            "id": this.documentId,
            "userid": this.documentUserId,
            "format": this.documentFormat,
            "vkey": this.documentVKey,
            "c": "reopen",
            "url": this.documentUrl,
            "title": this.documentTitle,
            "embeddedfonts": this.isUseEmbeddedCutFonts,
            "delimiter": option.asc_getDelimiter(),
            "codepage": option.asc_getCodePage()};

          sendCommand(this, null, v);
        } else if (this.advancedOptionsAction === c_oAscAdvancedOptionsAction.Save) {
          var options = {CSVOptions: option, downloadType: this.downloadType};
          this.downloadType = DownloadType.None;
          this._asc_downloadAs(c_oAscFileType.CSV, c_oAscAsyncAction.DownloadAs, options);
        }
        break;
    }
  };
  // Опции страницы (для печати)
  spreadsheet_api.prototype.asc_setPageOptions = function(options, index) {
    var sheetIndex = (undefined !== index && null !== index) ? index : this.wbModel.getActive();
    this.wbModel.getWorksheet(sheetIndex).PagePrintOptions = options;
  };

  spreadsheet_api.prototype.asc_getPageOptions = function(index) {
    var sheetIndex = (undefined !== index && null !== index) ? index : this.wbModel.getActive();
    return this.wbModel.getWorksheet(sheetIndex).PagePrintOptions;
  };

  spreadsheet_api.prototype._onNeedParams = function(data) {
    var t = this;
    // Проверяем, возможно нам пришли опции для CSV
    if (this.documentOpenOptions) {
      var codePageCsv = AscCommon.c_oAscEncodingsMap[this.documentOpenOptions["codePage"]] || AscCommon.c_oAscCodePageUtf8, delimiterCsv = this.documentOpenOptions["delimiter"];
      if (null != codePageCsv && null != delimiterCsv) {
        this.asc_setAdvancedOptions(c_oAscAdvancedOptionsID.CSV, new asc.asc_CCSVAdvancedOptions(codePageCsv, delimiterCsv));
        return;
      }
    }
    if (data) {
      AscCommon.loadFileContent(data, function(result) {
        if (null === result) {
          t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.Critical);
          return;
        }
        var cp = JSON.parse(result);
        cp['encodings'] = AscCommon.getEncodingParams();
        t.handlers.trigger("asc_onAdvancedOptions", new AscCommon.asc_CAdvancedOptions(c_oAscAdvancedOptionsID.CSV, cp), t.advancedOptionsAction);
      });
    } else {
      t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
    }
  };
  spreadsheet_api.prototype._onOpenCommand = function(data) {
    var t = this;
    AscCommon.openFileCommand(data, this.documentUrlChanges, AscCommon.c_oSerFormat.Signature, function(error, result) {
      if (error || !result.bSerFormat) {
        var oError = {returnCode: c_oAscError.Level.Critical, val: c_oAscError.ID.Unknown};
        t.handlers.trigger("asc_onError", oError.val, oError.returnCode);
        return;
      }

      t.onEndLoadFile(result.data);
    });
  };

  spreadsheet_api.prototype._OfflineAppDocumentEndLoad = function() {
    var data = getTestWorkbook();
    var sData = data + "";
    if (AscCommon.c_oSerFormat.Signature === sData.substring(0, AscCommon.c_oSerFormat.Signature.length)) {
      this.openDocument(sData);
    }
  };

  spreadsheet_api.prototype._asc_save2 = function() {
    var oBinaryFileWriter = new AscCommonExcel.BinaryFileWriter(this.wbModel);
    var dataContainer = {data: null, part: null, index: 0, count: 0};
    dataContainer.data = oBinaryFileWriter.Write();
    var filetype = 0x1002;
    var oAdditionalData = {};
    oAdditionalData["c"] = "sfct";
    oAdditionalData["id"] = this.documentId;
    oAdditionalData["userid"] = this.documentUserId;
    oAdditionalData["vkey"] = this.documentVKey;
    oAdditionalData["outputformat"] = filetype;
    oAdditionalData["title"] = AscCommon.changeFileExtention(this.documentTitle, AscCommon.getExtentionByFormat(filetype));
    this.wb._initCommentsToSave();
    oAdditionalData["savetype"] = AscCommon.c_oAscSaveTypes.CompleteAll;
    var t = this;
    t.fCurCallback = function(incomeObject) {
      if (null != input && "save" == input["type"]) {
        if ('ok' == input["status"]) {
          var url = input["data"];
          if (url) {
            t.processSavedFile(url, false);
          } else {
            t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
          }
        } else {
          t.handlers.trigger("asc_onError", mapAscServerErrorToAscError(parseInt(input["data"])), c_oAscError.Level.NoCritical);
        }
      } else {
        t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
      }
    };
    AscCommon.saveWithParts(function(fCallback1, oAdditionalData1, dataContainer1) {
      sendCommand(t, fCallback1, oAdditionalData1, dataContainer1);
    }, t.fCurCallback, null, oAdditionalData, dataContainer);
  };

  spreadsheet_api.prototype._asc_downloadAs = function(sFormat, actionType, options) { //fCallback({returnCode:"", ...})
    var t = this;
    if (!options) {
      options = {};
    }
    if (actionType) {
      this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, actionType);
    }
    // Меняем тип состояния (на сохранение)
    this.advancedOptionsAction = c_oAscAdvancedOptionsAction.Save;
    
    //sFormat: xlsx, xls, ods, csv, html
    var dataContainer = {data: null, part: null, index: 0, count: 0};
    var command = "save";
    var oAdditionalData = {};
    oAdditionalData["c"] = command;
    oAdditionalData["id"] = this.documentId;
    oAdditionalData["userid"] = this.documentUserId;
    oAdditionalData["vkey"] = this.documentVKey;
    oAdditionalData["outputformat"] = sFormat;
    oAdditionalData["title"] = AscCommon.changeFileExtention(this.documentTitle, AscCommon.getExtentionByFormat(sFormat));
    if (DownloadType.Print === options.downloadType) {
      oAdditionalData["inline"] = 1;
    }
    if (c_oAscFileType.PDF === sFormat) {
      var printPagesData = this.wb.calcPagesPrint(this.adjustPrint);
      var pdf_writer = new AscCommonExcel.CPdfPrinter();
      var isEndPrint = this.wb.printSheet(pdf_writer, printPagesData);

      dataContainer.data = pdf_writer.DocumentRenderer.Memory.GetBase64Memory();
    } else if (c_oAscFileType.CSV === sFormat && !options.CSVOptions) {
      // Мы открывали команду, надо ее закрыть.
      if (actionType) {
        this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, actionType);
      }
      var cp = {'delimiter': AscCommon.c_oAscCsvDelimiter.Comma, 'codepage': AscCommon.c_oAscCodePageUtf8, 'encodings': AscCommon.getEncodingParams()};
      this.downloadType = options.downloadType;
      this.handlers.trigger("asc_onAdvancedOptions", new AscCommon.asc_CAdvancedOptions(c_oAscAdvancedOptionsID.CSV, cp), this.advancedOptionsAction);
      return;
    } else {
      this.wb._initCommentsToSave();
      var oBinaryFileWriter = new AscCommonExcel.BinaryFileWriter(this.wbModel);
      if (c_oAscFileType.CSV === sFormat) {
        if (options.CSVOptions instanceof asc.asc_CCSVAdvancedOptions) {
          oAdditionalData["codepage"] = options.CSVOptions.asc_getCodePage();
          oAdditionalData["delimiter"] = options.CSVOptions.asc_getDelimiter();
        }
      }
      dataContainer.data = oBinaryFileWriter.Write();
    }
    var fCallback = function(input) {
      var error = c_oAscError.ID.Unknown;
      if (null != input && command == input["type"]) {
        if ('ok' == input["status"]) {
          var url = input["data"];
          if (url) {
            error = c_oAscError.ID.No;
            t.processSavedFile(url, options.downloadType);
          }
        } else {
          error = mapAscServerErrorToAscError(parseInt(input["data"]));
        }
      }
      if (c_oAscError.ID.No != error) {
        t.handlers.trigger("asc_onError", error, c_oAscError.Level.NoCritical);
      }
      // Меняем тип состояния (на никакое)
      t.advancedOptionsAction = c_oAscAdvancedOptionsAction.None;
      if (actionType) {
        t.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, actionType);
      }
    };
    t.fCurCallback = fCallback;
    AscCommon.saveWithParts(function(fCallback1, oAdditionalData1, dataContainer1) {
      sendCommand(t, fCallback1, oAdditionalData1, dataContainer1);
    }, fCallback, null, oAdditionalData, dataContainer);
  };

  spreadsheet_api.prototype.asc_isDocumentModified = function() {
    if (!this.canSave || this.asc_getCellEditMode()) {
      // Пока идет сохранение или редактирование ячейки, мы не закрываем документ
      return true;
    } else if (History && History.Is_Modified) {
      return History.Is_Modified();
    }
    return false;
  };

  spreadsheet_api.prototype.asc_getCanUndo = function() {
    return History.Can_Undo();
  };
  spreadsheet_api.prototype.asc_getCanRedo = function() {
    return History.Can_Redo();
  };


  // Actions and callbacks interface

  /*
   * asc_onStartAction			(type, id)
   * asc_onEndAction				(type, id)
   * asc_onInitEditorFonts		(gui_fonts)
   * asc_onInitEditorStyles		(gui_styles)
   * asc_onOpenDocumentProgress	(AscCommon.COpenProgress)
   * asc_onAdvancedOptions		(asc_CAdvancedOptions, ascAdvancedOptionsAction)	- эвент на получение дополнительных опций (открытие/сохранение CSV)
   * asc_onError					(c_oAscError.ID, c_oAscError.Level)					- эвент об ошибке
   * asc_onEditCell				(Asc.c_oAscCellEditorState)								- эвент на редактирование ячейки с состоянием (переходами из формулы и обратно)
   * asc_onEditorSelectionChanged	(asc_CFont)											- эвент на смену информации о выделении в редакторе ячейки
   * asc_onSelectionChanged		(asc_CCellInfo)										- эвент на смену информации о выделении
   * asc_onSelectionNameChanged	(sName)												- эвент на смену имени выделения (Id-ячейки, число выделенных столбцов/строк, имя диаграммы и др.)
   * asc_onSelection
   *
   * Changed	(asc_CSelectionMathInfo)							- эвент на смену математической информации о выделении
   * asc_onZoomChanged			(zoom)
   * asc_onSheetsChanged			()													- эвент на обновление списка листов
   * asc_onActiveSheetChanged		(indexActiveSheet)									- эвент на обновление активного листа
   * asc_onCanUndoChanged			(bCanUndo)											- эвент на обновление возможности undo
   * asc_onCanRedoChanged			(bCanRedo)											- эвент на обновление возможности redo
   * asc_onSaveUrl				(sUrl, callback(hasError))							- эвент на сохранение файла на сервер по url
   * asc_onDocumentModifiedChanged(bIsModified)										- эвент на обновление статуса "изменен ли файл"
   * asc_onMouseMove				(asc_CMouseMoveData)								- эвент на наведение мышкой на гиперлинк или комментарий
   * asc_onHyperlinkClick			(sUrl)												- эвент на нажатие гиперлинка
   * asc_onCoAuthoringDisconnect	()													- эвент об отключении от сервера без попытки reconnect
   * asc_onSelectionRangeChanged	(selectRange)										- эвент о выборе диапазона для диаграммы (после нажатия кнопки выбора)
   * asc_onRenameCellTextEnd		(countCellsFind, countCellsReplace)					- эвент об окончании замены текста в ячейках (мы не можем сразу прислать ответ)
   * asc_onWorkbookLocked			(result)											- эвент залочена ли работа с листами или нет
   * asc_onWorksheetLocked		(index, result)										- эвент залочен ли лист или нет
   * asc_onGetEditorPermissions	(permission)										- эвент о правах редактора
   * asc_onStopFormatPainter		()													- эвент об окончании форматирования по образцу
   * asc_onUpdateSheetSettings	()													- эвент об обновлении свойств листа (закрепленная область, показывать сетку/заголовки)
   * asc_onUpdateTabColor			(index)												- эвент об обновлении цвета иконки листа
   * asc_onDocumentCanSaveChanged	(bIsCanSave)										- эвент об обновлении статуса "можно ли сохранять файл"
   * asc_onDocumentUpdateVersion	(callback)											- эвент о том, что файл собрался и не может больше редактироваться
   * asc_onContextMenu			(event)												- эвент на контекстное меню
   * asc_onDocumentContentReady ()                        - эвент об окончании загрузки документа
   */

  spreadsheet_api.prototype.asc_registerCallback = function(name, callback, replaceOldCallback) {
    this.handlers.add(name, callback, replaceOldCallback);
    return;

    /*
     Не самая хорошая схема для отправки эвентов:
     проверяем, подписан ли кто-то на эвент? Если да, то отправляем и больше ничего не делаем.
     Если никто не подписан, то сохраняем у себя переменную и как только кто-то подписывается - отправляем ее
     */
    if (null !== this._gui_control_colors && "asc_onSendThemeColors" === name) {
      this.handlers.trigger("asc_onSendThemeColors", this._gui_control_colors.Colors, this._gui_control_colors.StandartColors);
      this._gui_control_colors = null;
    } else if (null !== this._gui_color_schemes && "asc_onSendThemeColorSchemes" === name) {
      this.handlers.trigger("asc_onSendThemeColorSchemes", this._gui_color_schemes);
      this._gui_color_schemes = null;
    }
  };

  spreadsheet_api.prototype.asc_unregisterCallback = function(name, callback) {
    this.handlers.remove(name, callback);
  };

  spreadsheet_api.prototype.asc_getController = function() {
    return this.controller;
//				return null;
  };

  spreadsheet_api.prototype.asc_SetDocumentPlaceChangedEnabled = function(val) {
    this.wb.setDocumentPlaceChangedEnabled(val);
  };

  spreadsheet_api.prototype.asc_SetFastCollaborative = function(bFast) {
    if (this.collaborativeEditing) {
      AscCommon.CollaborativeEditing.Set_Fast(bFast);
      this.collaborativeEditing.setFast(bFast);
    }
  };

  // Посылает эвент о том, что обновились листы
  spreadsheet_api.prototype.sheetsChanged = function() {
    this.handlers.trigger("asc_onSheetsChanged");
  };

  spreadsheet_api.prototype.asyncFontsDocumentStartLoaded = function() {
    this.OpenDocumentProgress.Type = c_oAscAsyncAction.LoadDocumentFonts;
    this.OpenDocumentProgress.FontsCount = this.FontLoader.fonts_loading.length;
    this.OpenDocumentProgress.CurrentFont = 0;
    this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentFonts);
  };

  spreadsheet_api.prototype.asyncFontsDocumentEndLoaded = function() {
    this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentFonts);

    if (this.asyncMethodCallback !== undefined) {
      this.asyncMethodCallback();
      this.asyncMethodCallback = undefined;
    } else {
      // Шрифты загрузились, возможно стоит подождать совместное редактирование
      this.FontLoadWaitComplete = true;
      if (this.ServerIdWaitComplete) {
        this._openDocumentEndCallback();
      }
    }
  };

  spreadsheet_api.prototype.asyncFontEndLoaded = function(font) {
    this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
  };

  spreadsheet_api.prototype._loadFonts = function(fonts, callback) {
    if (window["NATIVE_EDITOR_ENJINE"]) {
      return callback();
    }
    this.asyncMethodCallback = callback;
    var arrLoadFonts = [];
    for (var i in fonts)
      arrLoadFonts.push(new AscFonts.CFont(i, 0, "", 0));
    History.loadFonts(arrLoadFonts);
    this.FontLoader.LoadDocumentFonts2(arrLoadFonts);
  };

  spreadsheet_api.prototype.openDocument = function(sData) {
    if (true === sData) {
      // Empty Document
      sData = AscCommonExcel.getEmptyWorkbook() + "";
      if (sData.length && (AscCommon.c_oSerFormat.Signature === sData.substring(0, AscCommon.c_oSerFormat.Signature.length))) {
        this.isChartEditor = true;
      } else {
        return;
      }
    }

    this.wbModel = this._openDocument(sData);

    this.FontLoader.LoadDocumentFonts(this.wbModel.generateFontMap2());

    // Какая-то непонятная заглушка, чтобы не падало в ipad
    if (this.isMobileVersion) {
      AscCommon.AscBrowser.isSafariMacOs = false;
      AscCommon.PasteElementsId.PASTE_ELEMENT_ID = "wrd_pastebin";
      AscCommon.PasteElementsId.ELEMENT_DISPAY_STYLE = "none";
    }

    if (AscCommon.AscBrowser.isSafariMacOs) {
      setInterval(AscCommonExcel.SafariIntervalFocus2, 10);
    }
  };

  // Соединились с сервером
  spreadsheet_api.prototype.asyncServerIdEndLoaded = function() {
    // С сервером соединились, возможно стоит подождать загрузку шрифтов
    this.ServerIdWaitComplete = true;
    if (this.FontLoadWaitComplete) {
      this._openDocumentEndCallback();
    }
  };

  // Эвент о пришедщих изменениях
  spreadsheet_api.prototype.syncCollaborativeChanges = function() {
    // Для быстрого сохранения уведомлять не нужно.
    if (!this.collaborativeEditing.getFast()) {
      this.handlers.trigger("asc_onCollaborativeChanges");
    }
  };

  // Применение изменений документа, пришедших при открытии
  // Их нужно применять после того, как мы создали WorkbookView
  // т.к. автофильтры, диаграммы, изображения и комментарии завязаны на WorksheetView (ToDo переделать)
  spreadsheet_api.prototype._applyFirstLoadChanges = function() {
    if (this.IsSendDocumentLoadCompleate) {
      return;
    }
    if (this.collaborativeEditing.applyChanges()) {
      // Изменений не было
      this.IsSendDocumentLoadCompleate = true;
      this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);
      this.handlers.trigger('asc_onDocumentContentReady');
    }
  };

  /////////////////////////////////////////////////////////////////////////
  ///////////////////CoAuthoring and Chat api//////////////////////////////
  /////////////////////////////////////////////////////////////////////////
  spreadsheet_api.prototype._coAuthoringInitEnd = function() {
    var t = this;
    this.collaborativeEditing = new AscCommonExcel.CCollaborativeEditing(/*handlers*/{
      "askLock": function() {
        t.CoAuthoringApi.askLock.apply(t.CoAuthoringApi, arguments);
      },
      "releaseLocks": function() {
        t.CoAuthoringApi.releaseLocks.apply(t.CoAuthoringApi, arguments);
      },
      "sendChanges": function() {
        t._onSaveChanges.apply(t, arguments);
      },
      "applyChanges": function() {
        t._onApplyChanges.apply(t, arguments);
      },
      "updateAfterApplyChanges": function() {
        t._onUpdateAfterApplyChanges.apply(t, arguments);
      },
      "drawSelection": function() {
        t._onDrawSelection.apply(t, arguments);
      },
      "drawFrozenPaneLines": function() {
        t._onDrawFrozenPaneLines.apply(t, arguments);
      },
      "updateAllSheetsLock": function() {
        t._onUpdateAllSheetsLock.apply(t, arguments);
      },
      "showDrawingObjects": function() {
        t._onShowDrawingObjects.apply(t, arguments);
      },
      "showComments": function() {
        t._onShowComments.apply(t, arguments);
      },
      "cleanSelection": function() {
        t._onCleanSelection.apply(t, arguments);
      },
      "updateDocumentCanSave": function() {
        t._onUpdateDocumentCanSave();
      },
      "checkCommentRemoveLock": function(lockElem) {
        return t._onCheckCommentRemoveLock(lockElem);
      },
      "unlockDefName": function() {
        t._onUnlockDefName.apply(t, arguments);
      },
      "checkDefNameLock": function(lockElem) {
        return t._onCheckDefNameLock(lockElem);
      }
    }, this.getViewMode());

    this.CoAuthoringApi.onConnectionStateChanged = function(e) {
      t.handlers.trigger("asc_onConnectionStateChanged", e);
    };
    this.CoAuthoringApi.onLocksAcquired = function(e) {
      if (!t.IsSendDocumentLoadCompleate) {
        // Пока документ еще не загружен, будем сохранять функцию и аргументы
        t.arrPreOpenLocksObjects.push(function(){t.CoAuthoringApi.onLocksAcquired(e);});
        return;
      }

      if (2 != e["state"]) {
        var elementValue = e["blockValue"];
        var lockElem = t.collaborativeEditing.getLockByElem(elementValue, c_oAscLockTypes.kLockTypeOther);
        if (null === lockElem) {
          lockElem = new AscCommonExcel.CLock(elementValue);
          t.collaborativeEditing.addUnlock(lockElem);
        }

        var drawing, lockType = lockElem.Element["type"];
        var oldType = lockElem.getType();
        if (c_oAscLockTypes.kLockTypeOther2 === oldType || c_oAscLockTypes.kLockTypeOther3 === oldType) {
          lockElem.setType(c_oAscLockTypes.kLockTypeOther3, true);
        } else {
          lockElem.setType(c_oAscLockTypes.kLockTypeOther, true);
        }

        // Выставляем ID пользователя, залочившего данный элемент
        lockElem.setUserId(e["user"]);

        if (lockType === c_oAscLockTypeElem.Object) {
          drawing = g_oTableId.Get_ById(lockElem.Element["rangeOrObjectId"]);
          if (drawing) {
            drawing.lockType = lockElem.Type;
          }
        }

        if (t.wb) {
          // Шлем update для toolbar-а, т.к. когда select в lock ячейке нужно заблокировать toolbar
          t.wb._onWSSelectionChanged(/*info*/null);

          // Шлем update для листов
          t._onUpdateSheetsLock(lockElem);

          t._onUpdateDefinedNames(lockElem);

          var ws = t.wb.getWorksheet();
          var lockSheetId = lockElem.Element["sheetId"];
          if (lockSheetId === ws.model.getId()) {
            if (lockType === c_oAscLockTypeElem.Object) {
              // Нужно ли обновлять закрепление областей
              if (t._onUpdateFrozenPane(lockElem)) {
                ws.draw();
              } else if (drawing && ws.model === drawing.worksheet) {
                if (ws.objectRender) {
                  ws.objectRender.showDrawingObjects(true);
                }
              }
            } else if (lockType === c_oAscLockTypeElem.Range || lockType === c_oAscLockTypeElem.Sheet) {
              ws.updateSelection();
            }
          } else if (-1 !== lockSheetId && 0 === lockSheetId.indexOf(AscCommonExcel.CCellCommentator.sStartCommentId)) {
            // Коммментарий
            t.handlers.trigger("asc_onLockComment", lockElem.Element["rangeOrObjectId"], e["user"]);
          }
        }
      }
    };
    this.CoAuthoringApi.onLocksReleased = function(e, bChanges) {
      if (!t.IsSendDocumentLoadCompleate) {
        // Пока документ еще не загружен, будем сохранять функцию и аргументы
        t.arrPreOpenLocksObjects.push(function(){t.CoAuthoringApi.onLocksReleased(e, bChanges);});
        return;
      }

      var element = e["block"];
      var lockElem = t.collaborativeEditing.getLockByElem(element, c_oAscLockTypes.kLockTypeOther);
      if (null != lockElem) {
        var curType = lockElem.getType();

        var newType = c_oAscLockTypes.kLockTypeNone;
        if (curType === c_oAscLockTypes.kLockTypeOther) {
          if (true != bChanges) {
            newType = c_oAscLockTypes.kLockTypeNone;
          } else {
            newType = c_oAscLockTypes.kLockTypeOther2;
          }
        } else if (curType === c_oAscLockTypes.kLockTypeMine) {
          // Такого быть не должно
          newType = c_oAscLockTypes.kLockTypeMine;
        } else if (curType === c_oAscLockTypes.kLockTypeOther2 || curType === c_oAscLockTypes.kLockTypeOther3) {
          newType = c_oAscLockTypes.kLockTypeOther2;
        }

        if (t.wb) {
          t.wb.getWorksheet().cleanSelection();
        }

        var drawing;
        if (c_oAscLockTypes.kLockTypeNone !== newType) {
          lockElem.setType(newType, true);
        } else {
          // Удаляем из lock-ов, тот, кто правил ушел и не сохранил
          t.collaborativeEditing.removeUnlock(lockElem);
          if (!t._onCheckCommentRemoveLock(lockElem.Element)) {
            if (lockElem.Element["type"] === c_oAscLockTypeElem.Object) {
              drawing = g_oTableId.Get_ById(lockElem.Element["rangeOrObjectId"]);
              if (drawing) {
                drawing.lockType = c_oAscLockTypes.kLockTypeNone;
              }
            }
          }
        }
        if (t.wb) {
          // Шлем update для листов
          t._onUpdateSheetsLock(lockElem);
          /*снимаем лок для DefName*/
          t.handlers.trigger("asc_onLockDefNameManager",Asc.c_oAscDefinedNameReason.OK);
        }
      }
    };
    this.CoAuthoringApi.onLocksReleasedEnd = function() {
      if (!t.IsSendDocumentLoadCompleate) {
        // Пока документ еще не загружен ничего не делаем
        return;
      }

      if (t.wb) {
        // Шлем update для toolbar-а, т.к. когда select в lock ячейке нужно сбросить блокировку toolbar
        t.wb._onWSSelectionChanged(/*info*/null);

        var worksheet = t.wb.getWorksheet();
        worksheet.cleanSelection();
        worksheet._drawSelection();
        worksheet._drawFrozenPaneLines();
        if (worksheet.objectRender) {
          worksheet.objectRender.showDrawingObjects(true);
        }
      }
    };
    this.CoAuthoringApi.onSaveChanges = function(e, userId, bFirstLoad) {
      t.collaborativeEditing.addChanges(e);
      if (!bFirstLoad && t.IsSendDocumentLoadCompleate) {
        t.syncCollaborativeChanges();
      }
    };
    this.CoAuthoringApi.onRecalcLocks = function(excelAdditionalInfo) {
      if (!excelAdditionalInfo) {
        return;
      }

      var tmpAdditionalInfo = JSON.parse(excelAdditionalInfo);
      // Это мы получили recalcIndexColumns и recalcIndexRows
      var oRecalcIndexColumns = t.collaborativeEditing.addRecalcIndex('0', tmpAdditionalInfo['indexCols']);
      var oRecalcIndexRows = t.collaborativeEditing.addRecalcIndex('1', tmpAdditionalInfo['indexRows']);

      // Теперь нужно пересчитать индексы для lock-элементов
      if (null !== oRecalcIndexColumns || null !== oRecalcIndexRows) {
        t.collaborativeEditing._recalcLockArray(c_oAscLockTypes.kLockTypeMine, oRecalcIndexColumns, oRecalcIndexRows);
        t.collaborativeEditing._recalcLockArray(c_oAscLockTypes.kLockTypeOther, oRecalcIndexColumns, oRecalcIndexRows);
      }
    };
    this.CoAuthoringApi.onStartCoAuthoring = function(isStartEvent) {
      t.startCollaborationEditing();

      // На старте не нужно ничего делать
      if (!isStartEvent) {
        // Когда документ еще не загружен, нужно отпустить lock (при быстром открытии 2-мя пользователями)
        if (!t.IsSendDocumentLoadCompleate) {
          t.CoAuthoringApi.unLockDocument(false);
        } else {
          // Принимаем чужие изменения
          t.collaborativeEditing.applyChanges();
          // Пересылаем свои изменения
          t.collaborativeEditing.sendChanges();
        }
      }
    };
    this.CoAuthoringApi.onEndCoAuthoring = function(isStartEvent) {
      t.endCollaborationEditing();
    };
  };

  spreadsheet_api.prototype._onSaveChanges = function(recalcIndexColumns, recalcIndexRows) {
    if (this.IsSendDocumentLoadCompleate) {
      var arrChanges = this.wbModel.SerializeHistory();
      var deleteIndex = History.Get_DeleteIndex();
      var excelAdditionalInfo = null;
      if (this.collaborativeEditing.getCollaborativeEditing()) {
        // Пересчетные индексы добавляем только если мы не одни
        if (recalcIndexColumns || recalcIndexRows) {
          excelAdditionalInfo = {"indexCols": recalcIndexColumns, "indexRows": recalcIndexRows};
        }
      }
      if (0 < arrChanges.length || null !== deleteIndex || null !== excelAdditionalInfo) {
        this.CoAuthoringApi.saveChanges(arrChanges, deleteIndex, excelAdditionalInfo);
        History.CanNotAddChanges = true;
      } else {
        this.CoAuthoringApi.unLockDocument(true);
      }
    }
  };

  spreadsheet_api.prototype._onApplyChanges = function(changes, fCallback) {
    this.wbModel.DeserializeHistory(changes, fCallback);
  };

  spreadsheet_api.prototype._onUpdateAfterApplyChanges = function() {
    if (!this.IsSendDocumentLoadCompleate) {
      // При открытии после принятия изменений мы должны сбросить пересчетные индексы
      this.collaborativeEditing.clearRecalcIndex();
      this.IsSendDocumentLoadCompleate = true;
      this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);
      this.handlers.trigger('asc_onDocumentContentReady');
    } else if (this.wb && !window["NATIVE_EDITOR_ENJINE"]) {
      // Нужно послать 'обновить свойства' (иначе для удаления данных не обновится строка формул).
      // ToDo Возможно стоит обновлять только строку формул
      AscCommon.CollaborativeEditing.Load_Images();
      this.wb._onWSSelectionChanged(null);
      this.wb.getWorksheet().updateVisibleRange();
    }
  };

  spreadsheet_api.prototype._onCleanSelection = function() {
    if (this.wb) {
      this.wb.getWorksheet().cleanSelection();
    }
  };

  spreadsheet_api.prototype._onDrawSelection = function() {
    if (this.wb) {
      this.wb.getWorksheet()._drawSelection();
    }
  };

  spreadsheet_api.prototype._onDrawFrozenPaneLines = function() {
    if (this.wb) {
      this.wb.getWorksheet()._drawFrozenPaneLines();
    }
  };

  spreadsheet_api.prototype._onUpdateAllSheetsLock = function() {
    var t = this;
    if (t.wbModel) {
      // Шлем update для листов
      t.handlers.trigger("asc_onWorkbookLocked", t.asc_isWorkbookLocked());
      var i, length, wsModel, wsIndex;
      for (i = 0, length = t.wbModel.getWorksheetCount(); i < length; ++i) {
        wsModel = t.wbModel.getWorksheet(i);
        wsIndex = wsModel.getIndex();
        t.handlers.trigger("asc_onWorksheetLocked", wsIndex, t.asc_isWorksheetLockedOrDeleted(wsIndex));
      }
    }
  };

  spreadsheet_api.prototype._onShowDrawingObjects = function() {
    if (this.wb) {
      var ws = this.wb.getWorksheet();
      if (ws && ws.objectRender) {
        ws.objectRender.showDrawingObjects(true);
      }
    }
  };

  spreadsheet_api.prototype._onShowComments = function() {
    if (this.wb) {
      this.wb.getWorksheet().cellCommentator.drawCommentCells();
    }
  };

  spreadsheet_api.prototype._onUpdateSheetsLock = function(lockElem) {
    var t = this;
    // Шлем update для листов, т.к. нужно залочить лист
    if (c_oAscLockTypeElem.Sheet === lockElem.Element["type"]) {
      t.handlers.trigger("asc_onWorkbookLocked", t.asc_isWorkbookLocked());
    }
    // Шлем update для листа
    var wsModel = t.wbModel.getWorksheetById(lockElem.Element["sheetId"]);
    if (wsModel) {
      var wsIndex = wsModel.getIndex();
      t.handlers.trigger("asc_onWorksheetLocked", wsIndex, t.asc_isWorksheetLockedOrDeleted(wsIndex));
    }
  };

  spreadsheet_api.prototype._onUpdateFrozenPane = function(lockElem) {
    return (c_oAscLockTypeElem.Object === lockElem.Element["type"] && lockElem.Element["rangeOrObjectId"] === AscCommonExcel.c_oAscLockNameFrozenPane);
  };

  spreadsheet_api.prototype._sendWorkbookStyles = function() {
    if (this.wbModel) {

        if (!window['IS_NATIVE_EDITOR']) {
            // Для нативной версии не генерируем стили
            if (window["NATIVE_EDITOR_ENJINE"] && (!this.handlers.hasTrigger("asc_onInitTablePictures") || !this.handlers.hasTrigger("asc_onInitEditorStyles"))) {
                return;
            }
        }

      // Отправка стилей форматированных таблиц
      this.handlers.trigger("asc_onInitTablePictures", this.wb.getTablePictures());
      // Отправка стилей ячеек
      this.handlers.trigger("asc_onInitEditorStyles", this.wb.getCellStyles());
    }
  };

  spreadsheet_api.prototype.startCollaborationEditing = function() {
    // Начинаем совместное редактирование
    this.collaborativeEditing.startCollaborationEditing();
  };

  spreadsheet_api.prototype.endCollaborationEditing = function() {
    // Временно заканчиваем совместное редактирование
    this.collaborativeEditing.endCollaborationEditing();
  };

  // End Load document
  spreadsheet_api.prototype._openDocumentEndCallback = function() {
    // Не инициализируем дважды
    if (this.DocumentLoadComplete) {
      return;
    }

    this.wb = new AscCommonExcel.WorkbookView(this.wbModel, this.controller, this.handlers, this.HtmlElement, this.topLineEditorElement, this, this.collaborativeEditing, this.fontRenderingMode);

    this.DocumentLoadComplete = true;

    this.asc_CheckGuiControlColors();
    this.asc_SendThemeColorScheme();
    this.asc_ApplyColorScheme(false);

    this.sendStandartTextures();

    // Применяем пришедшие при открытии изменения
    this._applyFirstLoadChanges();
    // Применяем все lock-и (ToDo возможно стоит пересмотреть вообще Lock-и)
    for (var i = 0; i < this.arrPreOpenLocksObjects.length; ++i) {
      this.arrPreOpenLocksObjects[i]();
    }
    this.arrPreOpenLocksObjects = [];

    // Меняем тип состояния (на никакое)
    this.advancedOptionsAction = c_oAscAdvancedOptionsAction.None;

    // Были ошибки при открытии, посылаем предупреждение
    if (0 < this.wbModel.openErrors.length) {
      this.sendEvent('asc_onError', c_oAscError.ID.OpenWarning, c_oAscError.Level.NoCritical);
    }

    //this.asc_Resize(); // Убрал, т.к. сверху приходит resize (http://bugzserver/show_bug.cgi?id=14680)
  };

  // Переход на диапазон в листе
  spreadsheet_api.prototype._asc_setWorksheetRange = function(val) {
    // Получаем sheet по имени
    var ws = this.wbModel.getWorksheetByName(val.asc_getSheet());
    if (!ws || ws.getHidden()) {
      return;
    }
    // Индекс листа
    var sheetIndex = ws.getIndex();
    // Если не совпали индекс листа и индекс текущего, то нужно сменить
    if (this.asc_getActiveWorksheetIndex() !== sheetIndex) {
      // Меняем активный лист
      this.asc_showWorksheet(sheetIndex);
      // Посылаем эвент о смене активного листа
      this.handlers.trigger("asc_onActiveSheetChanged", sheetIndex);
    }
    var range = ws.getRange2(val.asc_getRange());
    if (null !== range) {
      this.wb._onSetSelection(range.getBBox0(), /*validRange*/ true);
    }
  };

  spreadsheet_api.prototype.onSaveCallback = function(e) {
    var t = this;
    var nState;
    if (false == e["saveLock"]) {
      if (this.isLongAction()) {
        // Мы не можем в этот момент сохранять, т.к. попали в ситуацию, когда мы залочили сохранение и успели нажать вставку до ответа
        // Нужно снять lock с сохранения
        this.CoAuthoringApi.onUnSaveLock = function() {
          t.canSave = true;
          t.IsUserSave = false;
          t.lastSaveTime = null;
        };
        this.CoAuthoringApi.unSaveLock();
        return;
      }

      if (!this.IsUserSave) {
        this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);
      }

      AscCommon.CollaborativeEditing.Clear_CollaborativeMarks();
      // Принимаем чужие изменения
      this.collaborativeEditing.applyChanges();

      this.CoAuthoringApi.onUnSaveLock = function() {
        t.CoAuthoringApi.onUnSaveLock = null;

        if (t.collaborativeEditing.getCollaborativeEditing()) {
          // Шлем update для toolbar-а, т.к. когда select в lock ячейке нужно заблокировать toolbar
          t.wb._onWSSelectionChanged(/*info*/null);
        }

        t.canSave = true;
        t.IsUserSave = false;
        t.lastSaveTime = null;

        t.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);
        // Обновляем состояние возможности сохранения документа
        t.onUpdateDocumentModified(History.Is_Modified());

        t.jio_save();
        if (undefined !== window["AscDesktopEditor"]) {
          window["AscDesktopEditor"]["OnSave"]();
        }
      };

      // Пересылаем всегда, но чистим только если началось совместное редактирование
      // Пересылаем свои изменения
      this.collaborativeEditing.sendChanges(this.IsUserSave);
    } else {
      nState = t.CoAuthoringApi.get_state();
      if (AscCommon.ConnectionState.ClosedCoAuth === nState || AscCommon.ConnectionState.ClosedAll === nState) {
        // Отключаемся от сохранения, соединение потеряно
        if (this.IsUserSave) {
          this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);
        }
        this.IsUserSave = false;
        this.canSave = true;
      } else {
        // Если автосохранение, то не будем ждать ответа, а просто перезапустим таймер на немного
        if (!this.IsUserSave) {
          this.canSave = true;
          return;
        }

        setTimeout(function() {
          t.CoAuthoringApi.askSaveChanges(function(event) {
            t.onSaveCallback(event);
          });
        }, 1000);
      }
    }
  };

  spreadsheet_api.prototype._getIsLockObjectSheet = function(lockInfo, callback) {
    if (false === this.collaborativeEditing.getCollaborativeEditing()) {
      // Пользователь редактирует один: не ждем ответа, а сразу продолжаем редактирование
      AscCommonExcel.applyFunction(callback, true);
      callback = undefined;
    }
    if (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeMine, /*bCheckOnlyLockAll*/false)) {
      // Редактируем сами
      AscCommonExcel.applyFunction(callback, true);
      return;
    } else if (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeOther, /*bCheckOnlyLockAll*/false)) {
      // Уже ячейку кто-то редактирует
      AscCommonExcel.applyFunction(callback, false);
      return;
    }

    this.collaborativeEditing.onStartCheckLock();
    this.collaborativeEditing.addCheckLock(lockInfo);
    this.collaborativeEditing.onEndCheckLock(callback);
  };
  // Залочена ли панель для закрепления
  spreadsheet_api.prototype._isLockedTabColor = function(index, callback) {
    var sheetId = this.wbModel.getWorksheet(index).getId();
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Object, null, sheetId, AscCommonExcel.c_oAscLockNameTabColor);

    if (false === this.collaborativeEditing.getCollaborativeEditing()) {
      // Пользователь редактирует один: не ждем ответа, а сразу продолжаем редактирование
      AscCommonExcel.applyFunction(callback, true);
      callback = undefined;
    }
    if (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeMine, /*bCheckOnlyLockAll*/false)) {
      // Редактируем сами
      AscCommonExcel.applyFunction(callback, true);
      return;
    } else if (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeOther, /*bCheckOnlyLockAll*/false)) {
      // Уже ячейку кто-то редактирует
      AscCommonExcel.applyFunction(callback, false);
      return;
    }

    this.collaborativeEditing.onStartCheckLock();
    this.collaborativeEditing.addCheckLock(lockInfo);
    this.collaborativeEditing.onEndCheckLock(callback);
  };

  spreadsheet_api.prototype._addWorksheet = function(name, i) {
    this.wbModel.createWorksheet(i, name);
    this.wb.spliceWorksheet(i, 0, null);
    this.asc_showWorksheet(i);
    // Посылаем callback об изменении списка листов
    this.sheetsChanged();
  };

  // Workbook interface

  spreadsheet_api.prototype.asc_getWorksheetsCount = function() {
    return this.wbModel.getWorksheetCount();
  };

  spreadsheet_api.prototype.asc_getWorksheetName = function(index) {
    return this.wbModel.getWorksheet(index).getName();
  };

  spreadsheet_api.prototype.asc_getWorksheetTabColor = function(index) {
    return this.wbModel.getWorksheet(index).getTabColor();
  };
  spreadsheet_api.prototype.asc_setWorksheetTabColor = function(index, color) {
    var t = this;
    var changeTabColorCallback = function(res) {
      if (res) {
        color = AscCommonExcel.CorrectAscColor(color);
        t.wbModel.getWorksheet(index).setTabColor(color);
      }
    };
    this._isLockedTabColor(index, changeTabColorCallback);
  };

  spreadsheet_api.prototype.asc_getActiveWorksheetIndex = function() {
    return this.wbModel.getActive();
  };

  spreadsheet_api.prototype.asc_getActiveWorksheetId = function() {
    var activeIndex = this.wbModel.getActive();
    return this.wbModel.getWorksheet(activeIndex).getId();
  };

  spreadsheet_api.prototype.asc_getWorksheetId = function(index) {
    return this.wbModel.getWorksheet(index).getId();
  };

  spreadsheet_api.prototype.asc_isWorksheetHidden = function(index) {
    return this.wbModel.getWorksheet(index).getHidden();
  };

  spreadsheet_api.prototype.asc_getDefinedNames = function(defNameListId) {
    return this.wb.getDefinedNames(defNameListId);
  };

  spreadsheet_api.prototype.asc_setDefinedNames = function(defName) {
//            return this.wb.setDefinedNames(defName);
    // Проверка глобального лока
    if (this.collaborativeEditing.getGlobalLock()) {
      return;
    }
    return this.wb.editDefinedNames(null, defName);
  };

  spreadsheet_api.prototype.asc_editDefinedNames = function(oldName, newName) {
    // Проверка глобального лока
    if (this.collaborativeEditing.getGlobalLock()) {
      return;
    }

    return this.wb.editDefinedNames(oldName, newName);
  };

  spreadsheet_api.prototype.asc_delDefinedNames = function(oldName) {
    // Проверка глобального лока
    if (this.collaborativeEditing.getGlobalLock()) {
      return;
    }
    return this.wb.delDefinedNames(oldName);
  };

  spreadsheet_api.prototype.asc_checkDefinedName = function(checkName, scope) {
    return this.wb.checkDefName(checkName, scope);
  };

  spreadsheet_api.prototype.asc_getDefaultDefinedName = function() {
    return this.wb.getDefaultDefinedName();
  };

  spreadsheet_api.prototype._onUpdateDefinedNames = function(lockElem) {
//      if( lockElem.Element["subType"] == AscCommonExcel.c_oAscLockTypeElemSubType.DefinedNames ){
      if( lockElem.Element["sheetId"] == -1 && lockElem.Element["rangeOrObjectId"] != -1 && !this.collaborativeEditing.getFast() ){
          var dN = this.wbModel.dependencyFormulas.defNameList[lockElem.Element["rangeOrObjectId"]];
          if (dN) {
              dN.isLock = lockElem.UserId;
              this.handlers.trigger("asc_onRefreshDefNameList",dN.getAscCDefName());
          }
          this.handlers.trigger("asc_onLockDefNameManager",Asc.c_oAscDefinedNameReason.LockDefNameManager);
      }
  };

  spreadsheet_api.prototype._onUnlockDefName = function() {
    this.wb.unlockDefName();
  };

  spreadsheet_api.prototype._onCheckDefNameLock = function() {
    return this.wb._onCheckDefNameLock();
  };

  // Залочена ли работа с листом
  spreadsheet_api.prototype.asc_isWorksheetLockedOrDeleted = function(index) {
    var ws = this.wbModel.getWorksheet(index);
    var sheetId = null;
    if (null === ws || undefined === ws) {
      sheetId = this.asc_getActiveWorksheetId();
    } else {
      sheetId = ws.getId();
    }

    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);
    // Проверим, редактирует ли кто-то лист
    return (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeOther, /*bCheckOnlyLockAll*/false));
  };

  // Залочена ли работа с листами
  spreadsheet_api.prototype.asc_isWorkbookLocked = function() {
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, null, null);
    // Проверим, редактирует ли кто-то лист
    return (false !== this.collaborativeEditing.getLockIntersection(lockInfo, c_oAscLockTypes.kLockTypeOther, /*bCheckOnlyLockAll*/false));
  };

  spreadsheet_api.prototype.asc_getHiddenWorksheets = function() {
    var model = this.wbModel;
    var len = model.getWorksheetCount();
    var i, ws, res = [];

    for (i = 0; i < len; ++i) {
      ws = model.getWorksheet(i);
      if (ws.getHidden()) {
        res.push({"index": i, "name": ws.getName()});
      }
    }
    return res;
  };

  spreadsheet_api.prototype.asc_showWorksheet = function(index) {
    if (typeof index === "number" && undefined !== index && null !== index) {
      var t = this;
      var ws = this.wbModel.getWorksheet(index);
      var isHidden = ws.getHidden();
      var showWorksheetCallback = function(res) {
        if (res) {
          t.wbModel.getWorksheet(index).setHidden(false);
          t.wb.showWorksheet(index);
          if (isHidden) {
            // Посылаем callback об изменении списка листов
            t.sheetsChanged();
          }
        }
      };
      if (isHidden) {
        var sheetId = this.wbModel.getWorksheet(index).getId();
        var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);
        this._getIsLockObjectSheet(lockInfo, showWorksheetCallback);
      } else {
        showWorksheetCallback(true);
      }
    }
  };

  spreadsheet_api.prototype.asc_showActiveWorksheet = function() {
    this.wb.showWorksheet(this.wbModel.getActive());
  };

  spreadsheet_api.prototype.asc_hideWorksheet = function() {
    var t = this;
    // Колличество листов
    var countWorksheets = this.asc_getWorksheetsCount();
    // Колличество скрытых листов
    var arrHideWorksheets = this.asc_getHiddenWorksheets();
    var countHideWorksheets = arrHideWorksheets.length;
    // Вдруг остался один лист
    if (countWorksheets <= countHideWorksheets + 1) {
      return false;
    }

    var model = this.wbModel;
    // Активный лист
    var activeWorksheet = model.getActive();
    var sheetId = this.wbModel.getWorksheet(activeWorksheet).getId();
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);

    var hideWorksheetCallback = function(res) {
      if (res) {
        t.wbModel.getWorksheet(activeWorksheet).setHidden(true);
      }
    };

    this._getIsLockObjectSheet(lockInfo, hideWorksheetCallback);
    return true;
  };

  spreadsheet_api.prototype.asc_renameWorksheet = function(name) {
    // Проверка глобального лока
    if (this.collaborativeEditing.getGlobalLock()) {
      return false;
    }

    var i = this.wbModel.getActive();
    var sheetId = this.wbModel.getWorksheet(i).getId();
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);

    var t = this;
    var renameCallback = function(res) {
      if (res) {
        t.wbModel.getWorksheet(i).setName(name);
        t.sheetsChanged();
      } else {
        t.handlers.trigger("asc_onError", c_oAscError.ID.LockedWorksheetRename, c_oAscError.Level.NoCritical);
      }
    };

    this._getIsLockObjectSheet(lockInfo, renameCallback);
    return true;
  };

  spreadsheet_api.prototype.asc_addWorksheet = function(name) {
    var i = this.wbModel.getActive();
    this._addWorksheet(name, i + 1);
  };

  spreadsheet_api.prototype.asc_insertWorksheet = function(name) {
    var i = this.wbModel.getActive();
    this._addWorksheet(name, i);
  };

  // Удаление листа
  spreadsheet_api.prototype.asc_deleteWorksheet = function() {
    // Проверка глобального лока
    if (this.collaborativeEditing.getGlobalLock()) {
      return false;
    }

    var i = this.wbModel.getActive();
    var activeSheet = this.wbModel.getWorksheet(i);
    var activeName = activeSheet.sName;
    var sheetId = activeSheet.getId();
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);

    var t = this;
    var deleteCallback = function(res) {
      if (res) {

        History.Create_NewPoint();
        History.StartTransaction();

        // Нужно проверить все диаграммы, ссылающиеся на удаляемый лист
        for (var key in t.wb.model.aWorksheets) {
          var wsModel = t.wb.model.aWorksheets[key];
          if (wsModel) {
            History.TurnOff();
            var ws = t.wb.getWorksheet(wsModel.index);
            History.TurnOn();
            wsModel.oDrawingOjectsManager.updateChartReferencesWidthHistory(parserHelp.getEscapeSheetName(activeName), parserHelp.getEscapeSheetName(wsModel.sName));
            if (ws && ws.objectRender && ws.objectRender.controller) {
              ws.objectRender.controller.recalculate2(true);
            }
          }
        }

        // Удаляем Worksheet и получаем новый активный индекс (-1 означает, что ничего не удалилось)
        var activeNow = t.wbModel.removeWorksheet(i);
        if (-1 !== activeNow) {
          t.wb.removeWorksheet(i);
          t.asc_showWorksheet(activeNow);
          // Посылаем callback об изменении списка листов
          t.sheetsChanged();
        }
        History.EndTransaction();
      }
    };

    this._getIsLockObjectSheet(lockInfo, deleteCallback);
    return true;
  };

  spreadsheet_api.prototype.asc_moveWorksheet = function(where) {
    var i = this.wbModel.getActive();
    var d = i < where ? +1 : -1;
    // Мы должны поместить слева от заданного значения, поэтому если идем вправо, то вычтем 1
    if (1 === d) {
      where -= 1;
    }

    this.wb.replaceWorksheet(i, where);
    this.wbModel.replaceWorksheet(i, where);

    // Обновим текущий номер
    this.asc_showWorksheet(where);
    // Посылаем callback об изменении списка листов
    this.sheetsChanged();
  };

  spreadsheet_api.prototype.asc_copyWorksheet = function(where, newName) {
    var scale = this.asc_getZoom();
    var i = this.wbModel.getActive();

    // ToDo уйти от lock для листа при копировании
    var sheetId = this.wbModel.getWorksheet(i).getId();
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Sheet, /*subType*/null, sheetId, sheetId);
    var t = this;
    var copyWorksheet = function(res) {
      if (res) {
        // ToDo перейти от wsViews на wsViewsId (сейчас вызываем раньше, чем в модели, т.к. там будет sortDependency
        // и cleanCellCache, который создаст уже скопированный лист(и splice сработает неправильно))
        History.Create_NewPoint();
        t.wb.copyWorksheet(i, where);
        t.wbModel.copyWorksheet(i, where, newName);
        // Делаем активным скопированный
        t.asc_showWorksheet(where);
        t.asc_setZoom(scale);
        // Посылаем callback об изменении списка листов
        t.sheetsChanged();
      }
    };

    this._getIsLockObjectSheet(lockInfo, copyWorksheet);
  };

  spreadsheet_api.prototype.asc_cleanSelection = function() {
    this.wb.getWorksheet().cleanSelection();
  };

  spreadsheet_api.prototype.asc_getZoom = function() {
    return this.wb.getZoom();
  };

  spreadsheet_api.prototype.asc_setZoom = function(scale) {
    this.wb.changeZoom(scale);
  };

  spreadsheet_api.prototype.asc_enableKeyEvents = function(isEnabled) {
    if (!this.isLoadFullApi) {
      this.tmpFocus = isEnabled;
      return;
    }

    if (this.wb) {
      this.wb.enableKeyEventsHandler(isEnabled);
    }
    //наличие фокуса в рабочей области редактора(используется для copy/paste в MAC)
    this.IsFocus = isEnabled;
  };

  spreadsheet_api.prototype.asc_IsFocus = function(bIsNaturalFocus) {
    var res = true;
    if (this.wb) {
      res = this.wb.getEnableKeyEventsHandler(bIsNaturalFocus);
    }
    return res;
  };

  spreadsheet_api.prototype.asc_searchEnabled = function(bIsEnabled) {
  };

  spreadsheet_api.prototype.asc_findText = function(options) {
    if (window["NATIVE_EDITOR_ENJINE"]) {
      if (this.wb.findCellText(options)) {
        var ws = this.wb.getWorksheet();
        return [ws.getCellLeftRelative(ws.activeRange.c1, 0), ws.getCellTopRelative(ws.activeRange.r1, 0)];
      }

      return null;
    }

    var d = this.wb.findCellText(options);
    if (d) {
      if (d.deltaX) {
        this.controller.scrollHorizontal(d.deltaX);
      }
      if (d.deltaY) {
        this.controller.scrollVertical(d.deltaY);
      }
    }
    return !!d;
  };

  spreadsheet_api.prototype.asc_replaceText = function(options) {
    options.lookIn = Asc.c_oAscFindLookIn.Formulas; // При замене поиск только в формулах
    this.wb.replaceCellText(options);
  };

  spreadsheet_api.prototype.asc_endFindText = function() {
    // Нужно очистить поиск
    this.wb._cleanFindResults();
  };

  /**
   * Делает активной указанную ячейку
   * @param {String} reference  Ссылка на ячейку вида A1 или R1C1
   */
  spreadsheet_api.prototype.asc_findCell = function (reference) {
    if (this.wb.cellEditor.isOpened) {
      return;
    }
    var d = this.wb.findCell(reference);
    if (!d) {
      if (!this.isViewMode) {
        this.handlers.trigger("asc_onError", c_oAscError.ID.InvalidReferenceOrName, c_oAscError.Level.NoCritical);
      }
      return;
    }

    // Получаем sheet по имени
    var ws = this.wbModel.getWorksheetByName(d.sheet);
    if (!ws || ws.getHidden()) {
      return;
    }
    // Индекс листа
    var sheetIndex = ws.getIndex();
    // Если не совпали индекс листа и индекс текущего, то нужно сменить
    if (this.asc_getActiveWorksheetIndex() !== sheetIndex) {
      // Меняем активный лист
      this.asc_showWorksheet(sheetIndex);
      // Посылаем эвент о смене активного листа
      this.handlers.trigger("asc_onActiveSheetChanged", sheetIndex);
    }

    ws = this.wb.getWorksheet();
    d = d.range ? ws.setSelection(d.range, true) : null;

    if (d) {
      if (d.deltaX) {
        this.controller.scrollHorizontal(d.deltaX);
      }
      if (d.deltaY) {
        this.controller.scrollVertical(d.deltaY);
      }
    } else {
      this.handlers.trigger("asc_onError", c_oAscError.ID.InvalidReferenceOrName, c_oAscError.Level.NoCritical);
    }
  };

  spreadsheet_api.prototype.asc_closeCellEditor = function() {
    this.wb.closeCellEditor();
  };


  // Spreadsheet interface

  spreadsheet_api.prototype.asc_getColumnWidth = function() {
    var ws = this.wb.getWorksheet();
    return ws.getSelectedColumnWidthInSymbols();
  };

  spreadsheet_api.prototype.asc_setColumnWidth = function(width) {
    this.wb.getWorksheet().changeWorksheet("colWidth", width);
  };

  spreadsheet_api.prototype.asc_showColumns = function() {
    this.wb.getWorksheet().changeWorksheet("showCols");
  };

  spreadsheet_api.prototype.asc_hideColumns = function() {
    this.wb.getWorksheet().changeWorksheet("hideCols");
  };

  spreadsheet_api.prototype.asc_getRowHeight = function() {
    var ws = this.wb.getWorksheet();
    return ws.getSelectedRowHeight();
  };

  spreadsheet_api.prototype.asc_setRowHeight = function(height) {
    this.wb.getWorksheet().changeWorksheet("rowHeight", height);
  };

  spreadsheet_api.prototype.asc_showRows = function() {
    this.wb.getWorksheet().changeWorksheet("showRows");
  };

  spreadsheet_api.prototype.asc_hideRows = function() {
    this.wb.getWorksheet().changeWorksheet("hideRows");
  };

  spreadsheet_api.prototype.asc_insertCells = function(options) {
    this.wb.getWorksheet().changeWorksheet("insCell", options);
  };

  spreadsheet_api.prototype.asc_deleteCells = function(options) {
    this.wb.getWorksheet().changeWorksheet("delCell", options);
  };

  spreadsheet_api.prototype.asc_mergeCells = function(options) {
    this.wb.getWorksheet().setSelectionInfo("merge", options);
  };

  spreadsheet_api.prototype.asc_sortCells = function(options) {
    this.wb.getWorksheet().setSelectionInfo("sort", options);
  };

  spreadsheet_api.prototype.asc_emptyCells = function(options) {
    this.wb.emptyCells(options);
  };

  spreadsheet_api.prototype.asc_drawDepCells = function(se) {
    /* ToDo
     if( se != AscCommonExcel.c_oAscDrawDepOptions.Clear )
     this.wb.getWorksheet().prepareDepCells(se);
     else
     this.wb.getWorksheet().cleanDepCells();*/
  };

  // Потеряем ли мы что-то при merge ячеек
  spreadsheet_api.prototype.asc_mergeCellsDataLost = function(options) {
    return this.wb.getWorksheet().getSelectionMergeInfo(options);
  };

  spreadsheet_api.prototype.asc_getSheetViewSettings = function() {
    return this.wb.getWorksheet().getSheetViewSettings();
  };

  spreadsheet_api.prototype.asc_setSheetViewSettings = function(options) {
    this.wb.getWorksheet().changeWorksheet("sheetViewSettings", options);
  };

  // Images & Charts

  spreadsheet_api.prototype.asc_drawingObjectsExist = function() {
    for (var i = 0; i < this.wb.model.aWorksheets.length; i++) {
      if (this.wb.model.aWorksheets[i].Drawings && this.wb.model.aWorksheets[i].Drawings.length) {
        return true;
      }
    }
    return false;
  };

  spreadsheet_api.prototype.asc_getChartObject = function() {		// Return new or existing chart. For image return null
    this.asc_onOpenChartFrame();
    var ws = this.wb.getWorksheet();
    return ws.objectRender.getAscChartObject();
  };

  spreadsheet_api.prototype.asc_addChartDrawingObject = function(chart) {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.addChartDrawingObject(chart);
  };

  spreadsheet_api.prototype.asc_editChartDrawingObject = function(chart) {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.editChartDrawingObject(chart);
  };

  spreadsheet_api.prototype.asc_addImageDrawingObject = function(imageUrl, callback) {
    var t = this;
    if (!callback) {
      callback = function (url) {
        //g_oDocumentUrls.addUrls(urls);
        var ws = t.wb.getWorksheet();
        ws.objectRender.addImageDrawingObject('jio:' + url, null);
      };
    }
    //this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);
    return new RSVP.Queue()
      .push(function () {
        return  imageUrl;
      })
      .push(AscCommon.downloadUrlAsBlob)
      .push(function (blob) {
        return Common.Gateway.jio_putAttachment(t.documentId, undefined, blob);
      })
      .push(callback)
      //.push(function () {t.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);})
      .push(undefined, function (error) {
        console.log(error);
        t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
        //t.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);
      });
  };

  spreadsheet_api.prototype.asc_showImageFileDialog = function() {
    // ToDo заменить на общую функцию для всех
    this.asc_addImage();
  };
  spreadsheet_api.prototype._addImageUrl = function(url) {
    var ws = this.wb.getWorksheet();
    if (ws) {
      if (this.isImageChangeUrl || this.isShapeImageChangeUrl || this.isTextArtChangeUrl) {
        ws.objectRender.editImageDrawingObject(url);
      } else {
        ws.objectRender.addImageDrawingObject(url, null);
      }
    }
  };
  spreadsheet_api.prototype.asc_setSelectedDrawingObjectLayer = function(layerType) {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.setGraphicObjectLayer(layerType);
  };
  spreadsheet_api.prototype.asc_addTextArt = function(nStyle) {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.addTextArt(nStyle);
  };

  spreadsheet_api.prototype.asc_checkDataRange = function(dialogType, dataRange, fullCheck, isRows, chartType) {
    return parserHelp.checkDataRange(this.wbModel, this.wb, dialogType, dataRange, fullCheck, isRows, chartType);
  };

  // Для вставки диаграмм в Word
  spreadsheet_api.prototype.asc_getBinaryFileWriter = function() {
    this.wb._initCommentsToSave();
    return new AscCommonExcel.BinaryFileWriter(this.wbModel);
  };

  spreadsheet_api.prototype.asc_getWordChartObject = function() {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.getWordChartObject();
  };

  spreadsheet_api.prototype.asc_cleanWorksheet = function() {
    var ws = this.wb.getWorksheet();	// Для удаления данных листа и диаграмм
    if (ws.objectRender) {
      ws.objectRender.cleanWorksheet();
    }
  };

  // Выставление данных (пока используется только для MailMerge)
  spreadsheet_api.prototype.asc_setData = function(oData) {
    this.wb.getWorksheet().setData(oData);
  };
  // Получение данных
  spreadsheet_api.prototype.asc_getData = function() {
    this.asc_closeCellEditor();
    return this.wb.getWorksheet().getData();
  };

  // Cell comment interface
  spreadsheet_api.prototype.asc_addComment = function(oComment) {
  };

  spreadsheet_api.prototype.asc_changeComment = function(id, oComment) {
    if (oComment.bDocument) {
      this.wb.cellCommentator.changeComment(id, oComment);
    } else {
      var ws = this.wb.getWorksheet();
      ws.cellCommentator.changeComment(id, oComment);
    }
  };

  spreadsheet_api.prototype.asc_selectComment = function(id) {
    var ws = this.wb.getWorksheet();
    ws.cellCommentator.selectComment(id, /*bMove*/true);
  };

  spreadsheet_api.prototype.asc_showComment = function(id, bNew) {
    var ws = this.wb.getWorksheet();
    ws.cellCommentator.showComment(id, bNew);
  };

  spreadsheet_api.prototype.asc_findComment = function(id) {
    var ws = this.wb.getWorksheet();
    return ws.cellCommentator.findComment(id);
  };

  spreadsheet_api.prototype.asc_removeComment = function(id) {
    var ws = this.wb.getWorksheet();
    ws.cellCommentator.removeComment(id);
    this.wb.cellCommentator.removeComment(id);
  };

  spreadsheet_api.prototype.asc_getComments = function(col, row) {
    var ws = this.wb.getWorksheet();
    return ws.cellCommentator.getComments(col, row);
  };

  spreadsheet_api.prototype.asc_getDocumentComments = function() {
    return this.wb.cellCommentator.getDocumentComments();
  };

  spreadsheet_api.prototype.asc_showComments = function() {
    var ws = this.wb.getWorksheet();
    return ws.cellCommentator.showComments();
  };

  spreadsheet_api.prototype.asc_hideComments = function() {
    var ws = this.wb.getWorksheet();
    return ws.cellCommentator.hideComments();
  };

  // Shapes
  spreadsheet_api.prototype.setStartPointHistory = function() {
    this.noCreatePoint = true;
    this.exucuteHistory = true;
    this.asc_stopSaving();
  };

  spreadsheet_api.prototype.setEndPointHistory = function() {
    this.noCreatePoint = false;
    this.exucuteHistoryEnd = true;
    this.asc_continueSaving();
  };

  spreadsheet_api.prototype.asc_startAddShape = function(sPreset) {
    this.isStartAddShape = this.controller.isShapeAction = true;
    var ws = this.wb.getWorksheet();
    ws.objectRender.controller.startTrackNewShape(sPreset);
  };

  spreadsheet_api.prototype.asc_endAddShape = function() {
    this.isStartAddShape = false;
    this.handlers.trigger("asc_onEndAddShape");
  };

  spreadsheet_api.prototype.asc_isAddAutoshape = function() {
    return this.isStartAddShape;
  };

  spreadsheet_api.prototype.asc_canAddShapeHyperlink = function() {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.controller.canAddHyperlink();
  };

  spreadsheet_api.prototype.asc_canGroupGraphicsObjects = function() {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.controller.canGroup();
  };

  spreadsheet_api.prototype.asc_groupGraphicsObjects = function() {
    var ws = this.wb.getWorksheet();
    ws.objectRender.groupGraphicObjects();
  };

  spreadsheet_api.prototype.asc_canUnGroupGraphicsObjects = function() {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.controller.canUnGroup();
  };

  spreadsheet_api.prototype.asc_unGroupGraphicsObjects = function() {
    var ws = this.wb.getWorksheet();
    ws.objectRender.unGroupGraphicObjects();
  };

  spreadsheet_api.prototype.asc_changeShapeType = function(value) {
    this.asc_setGraphicObjectProps(new Asc.asc_CImgProperty({ShapeProperties: {type: value}}));
  };

  spreadsheet_api.prototype.asc_getGraphicObjectProps = function() {
    var ws = this.wb.getWorksheet();
    if (ws && ws.objectRender && ws.objectRender.controller) {
      return ws.objectRender.controller.getGraphicObjectProps();
    }
    return null;
  };

  spreadsheet_api.prototype.asc_setGraphicObjectProps = function(props) {

    var ws = this.wb.getWorksheet();
    var fReplaceCallback = null, sImageUrl = null;
    if(!AscCommon.isNullOrEmptyString(props.ImageUrl)){
      if(!g_oDocumentUrls.getImageLocal(props.ImageUrl)){
        sImageUrl = props.ImageUrl;
        fReplaceCallback = function(sLocalUrl){
          props.ImageUrl = sLocalUrl;
        }
      }
    }
    else if(props.ShapeProperties && props.ShapeProperties.fill && props.ShapeProperties.fill.fill &&
    !AscCommon.isNullOrEmptyString(props.ShapeProperties.fill.fill.url)){
      if(!g_oDocumentUrls.getImageLocal(props.ShapeProperties.fill.fill.url)){
        sImageUrl = props.ShapeProperties.fill.fill.url;
        fReplaceCallback = function(sLocalUrl){
          props.ShapeProperties.fill.fill.url = sLocalUrl;
        }
      }
    }
    if(fReplaceCallback){

      if (window["AscDesktopEditor"])
      {
        var firstUrl = window["AscDesktopEditor"]["LocalFileGetImageUrl"](sImageUrl);
		firstUrl = g_oDocumentUrls.getImageUrl(firstUrl);
        fReplaceCallback(firstUrl);
        ws.objectRender.setGraphicObjectProps(props);
        return;
      }

      this.asc_addImageDrawingObject(sImageUrl, function (url) {
        fReplaceCallback('jio:' + url);
        ws.objectRender.setGraphicObjectProps(props);
      });
    }
    else{
      ws.objectRender.setGraphicObjectProps(props);
    }
  };

  spreadsheet_api.prototype.asc_getOriginalImageSize = function() {
    var ws = this.wb.getWorksheet();
    return ws.objectRender.getOriginalImageSize();
  };

  spreadsheet_api.prototype.asc_setInterfaceDrawImagePlaceTextArt = function(elementId) {
    this.textArtElementId = elementId;
  };

  spreadsheet_api.prototype.asc_changeImageFromFile = function() {
    this.isImageChangeUrl = true;
    this.asc_addImage();
  };

  spreadsheet_api.prototype.asc_changeShapeImageFromFile = function() {
    this.isShapeImageChangeUrl = true;
    this.asc_addImage();
  };

  spreadsheet_api.prototype.asc_changeArtImageFromFile = function() {
    this.isTextArtChangeUrl = true;
    this.asc_addImage();
  };

  spreadsheet_api.prototype.asc_putPrLineSpacing = function(type, value) {
    var ws = this.wb.getWorksheet();
    ws.objectRender.controller.putPrLineSpacing(type, value);
  };

  spreadsheet_api.prototype.asc_putLineSpacingBeforeAfter = function(type, value) { // "type == 0" means "Before", "type == 1" means "After"
    var ws = this.wb.getWorksheet();
    ws.objectRender.controller.putLineSpacingBeforeAfter(type, value);
  };

  spreadsheet_api.prototype.asc_setDrawImagePlaceParagraph = function(element_id, props) {
    var ws = this.wb.getWorksheet();
    ws.objectRender.setDrawImagePlaceParagraph(element_id, props);
  };

    spreadsheet_api.prototype.asc_replaceLoadImageCallback = function(fCallback){
        if(this.wb){
            var ws = this.wb.getWorksheet();
            if(ws.objectRender){
                ws.objectRender.asyncImageEndLoaded = fCallback;
            }
        }
    };

  spreadsheet_api.prototype.asyncImageEndLoaded = function(_image) {
    if (this.wb) {
      var ws = this.wb.getWorksheet();
      if (ws.objectRender.asyncImageEndLoaded) {
        ws.objectRender.asyncImageEndLoaded(_image);
      }
    }
  };

  spreadsheet_api.prototype.asyncImagesDocumentEndLoaded = function() {
    if (c_oAscAdvancedOptionsAction.None === this.advancedOptionsAction && this.wb && !window["NATIVE_EDITOR_ENJINE"]) {
      var ws = this.wb.getWorksheet();
      ws.objectRender.showDrawingObjects(true);
      ws.objectRender.controller.getGraphicObjectProps();
    }
  };

  spreadsheet_api.prototype.asyncImageEndLoadedBackground = function() {
    var worksheet = this.wb.getWorksheet();
    if (worksheet && worksheet.objectRender) {
      var drawing_area = worksheet.objectRender.drawingArea;
      if (drawing_area) {
        for (var i = 0; i < drawing_area.frozenPlaces.length; ++i) {
          worksheet.objectRender.showDrawingObjects(false, new AscFormat.GraphicOption(worksheet, AscCommonExcel.c_oAscGraphicOption.ScrollVertical, drawing_area.frozenPlaces[i].range, {offsetX: 0, offsetY: 0}));
            worksheet.objectRender.controller && worksheet.objectRender.controller.getGraphicObjectProps();
        }
      }
    }
  };

  // Frozen pane
  spreadsheet_api.prototype.asc_freezePane = function() {
    this.wb.getWorksheet().freezePane();
  };

  // Cell interface
  spreadsheet_api.prototype.asc_getCellInfo = function(bExt) {
    return this.wb.getWorksheet().getSelectionInfo(!!bExt);
  };

  // Получить координаты активной ячейки
  spreadsheet_api.prototype.asc_getActiveCellCoord = function() {
    return this.wb.getWorksheet().getActiveCellCoord();
  };

  // Получить координаты для каких-либо действий (для общей схемы)
  spreadsheet_api.prototype.asc_getAnchorPosition = function() {
    return this.asc_getActiveCellCoord();
  };

  // Получаем свойство: редактируем мы сейчас или нет
  spreadsheet_api.prototype.asc_getCellEditMode = function() {
    return this.wb ? this.wb.getCellEditMode() : false;
  };

  spreadsheet_api.prototype.asc_getIsTrackShape = function()  {
    return this.wb ? this.wb.getIsTrackShape() : false;
  };

  spreadsheet_api.prototype.asc_setCellFontName = function(fontName) {
    var t = this, fonts = {};
    fonts[fontName] = 1;
    t._loadFonts(fonts, function() {
      var ws = t.wb.getWorksheet();
      if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellFontName) {
        ws.objectRender.controller.setCellFontName(fontName);
      } else {
        t.wb.setFontAttributes("fn", fontName);
        t.wb.restoreFocus();
      }
    });
  };

  spreadsheet_api.prototype.asc_setCellFontSize = function(fontSize) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellFontSize) {
      ws.objectRender.controller.setCellFontSize(fontSize);
    } else {
      this.wb.setFontAttributes("fs", fontSize);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellBold = function(isBold) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellBold) {
      ws.objectRender.controller.setCellBold(isBold);
    } else {
      this.wb.setFontAttributes("b", isBold);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellItalic = function(isItalic) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellItalic) {
      ws.objectRender.controller.setCellItalic(isItalic);
    } else {
      this.wb.setFontAttributes("i", isItalic);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellUnderline = function(isUnderline) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellUnderline) {
      ws.objectRender.controller.setCellUnderline(isUnderline);
    } else {
      this.wb.setFontAttributes("u", isUnderline ? Asc.EUnderline.underlineSingle : Asc.EUnderline.underlineNone);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellStrikeout = function(isStrikeout) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellStrikeout) {
      ws.objectRender.controller.setCellStrikeout(isStrikeout);
    } else {
      this.wb.setFontAttributes("s", isStrikeout);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellSubscript = function(isSubscript) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellSubscript) {
      ws.objectRender.controller.setCellSubscript(isSubscript);
    } else {
      this.wb.setFontAttributes("fa", isSubscript ? "subscript" : "none");
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellSuperscript = function(isSuperscript) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellSuperscript) {
      ws.objectRender.controller.setCellSuperscript(isSuperscript);
    } else {
      this.wb.setFontAttributes("fa", isSuperscript ? "superscript" : "none");
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellAlign = function(align) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellAlign) {
      ws.objectRender.controller.setCellAlign(align);
    } else {
      this.wb.getWorksheet().setSelectionInfo("a", align);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellVertAlign = function(align) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellVertAlign) {
      ws.objectRender.controller.setCellVertAlign(align);
    } else {
      this.wb.getWorksheet().setSelectionInfo("va", align);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellTextWrap = function(isWrapped) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellTextWrap) {
      ws.objectRender.controller.setCellTextWrap(isWrapped);
    } else {
      this.wb.getWorksheet().setSelectionInfo("wrap", isWrapped);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellTextShrink = function(isShrinked) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellTextShrink) {
      ws.objectRender.controller.setCellTextShrink(isShrinked);
    } else {
      this.wb.getWorksheet().setSelectionInfo("shrink", isShrinked);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellTextColor = function(color) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellTextColor) {
      ws.objectRender.controller.setCellTextColor(color);
    } else {
      if (color instanceof Asc.asc_CColor) {
        color = AscCommonExcel.CorrectAscColor(color);
        this.wb.setFontAttributes("c", color);
        this.wb.restoreFocus();
      }
    }

  };

  spreadsheet_api.prototype.asc_setCellBackgroundColor = function(color) {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellBackgroundColor) {
      ws.objectRender.controller.setCellBackgroundColor(color);
    } else {
      if (color instanceof Asc.asc_CColor || null == color) {
        if (null != color) {
          color = AscCommonExcel.CorrectAscColor(color);
        }
        this.wb.getWorksheet().setSelectionInfo("bc", color);
        this.wb.restoreFocus();
      }
    }
  };

  spreadsheet_api.prototype.asc_setCellBorders = function(borders) {
    this.wb.getWorksheet().setSelectionInfo("border", borders);
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_setCellFormat = function(format) {
    this.wb.getWorksheet().setSelectionInfo("format", format);
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_setCellAngle = function(angle) {

    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.setCellAngle) {
      ws.objectRender.controller.setCellAngle(angle);
    } else {
      this.wb.getWorksheet().setSelectionInfo("angle", angle);
      this.wb.restoreFocus();
    }
  };

  spreadsheet_api.prototype.asc_setCellStyle = function(name) {
    this.wb.getWorksheet().setSelectionInfo("style", name);
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_increaseCellDigitNumbers = function() {
    this.wb.getWorksheet().setSelectionInfo("changeDigNum", +1);
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_decreaseCellDigitNumbers = function() {
    this.wb.getWorksheet().setSelectionInfo("changeDigNum", -1);
    this.wb.restoreFocus();
  };

  // Увеличение размера шрифта
  spreadsheet_api.prototype.asc_increaseFontSize = function() {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.increaseFontSize) {
      ws.objectRender.controller.increaseFontSize();
    } else {
      this.wb.changeFontSize("changeFontSize", true);
      this.wb.restoreFocus();
    }
  };

  // Уменьшение размера шрифта
  spreadsheet_api.prototype.asc_decreaseFontSize = function() {
    var ws = this.wb.getWorksheet();
    if (ws.objectRender.selectedGraphicObjectsExists() && ws.objectRender.controller.decreaseFontSize) {
      ws.objectRender.controller.decreaseFontSize();
    } else {
      this.wb.changeFontSize("changeFontSize", false);
      this.wb.restoreFocus();
    }
  };

  // Формат по образцу
  spreadsheet_api.prototype.asc_formatPainter = function(stateFormatPainter) {
    if (this.wb) {
      this.wb.formatPainter(stateFormatPainter);
    }
  };

  spreadsheet_api.prototype.asc_onMouseUp = function(event, x, y) {
    this.controller._onWindowMouseUpExternal(event, x, y);
  };

  //

  spreadsheet_api.prototype.asc_selectFunction = function() {

  };

  spreadsheet_api.prototype.asc_insertHyperlink = function(options) {
    this.wb.insertHyperlink(options);
  };

  spreadsheet_api.prototype.asc_removeHyperlink = function() {
    this.wb.removeHyperlink();
  };

  spreadsheet_api.prototype.asc_insertFormula = function(functionName, type, autoComplete) {
    this.wb.insertFormulaInEditor(functionName, type, autoComplete);
    this.wb.restoreFocus();
  };

  spreadsheet_api.prototype.asc_getFormulasInfo = function() {
    return this.formulasList;
  };
  spreadsheet_api.prototype.asc_getFormulaLocaleName = function(name) {
    return AscCommonExcel.cFormulaFunctionToLocale ? AscCommonExcel.cFormulaFunctionToLocale[name] : name;
  };

  spreadsheet_api.prototype.asc_recalc = function(isRecalcWB) {
    this.wbModel.recalcWB(isRecalcWB);
  };

  spreadsheet_api.prototype.asc_setFontRenderingMode = function(mode) {
    if (mode !== this.fontRenderingMode) {
      this.fontRenderingMode = mode;
      if (this.wb) {
        this.wb.setFontRenderingMode(mode, /*isInit*/false);
      }
    }
  };

  /**
   * Режим выбора диапазона
   * @param {Asc.c_oAscSelectionDialogType} selectionDialogType
   * @param selectRange
   */
  spreadsheet_api.prototype.asc_setSelectionDialogMode = function(selectionDialogType, selectRange) {
    this.controller.setSelectionDialogMode(Asc.c_oAscSelectionDialogType.None !== selectionDialogType);
    if (this.wb) {
      this.wb._onStopFormatPainter();
      this.wb.setSelectionDialogMode(selectionDialogType, selectRange);
    }
  };

  spreadsheet_api.prototype.asc_SendThemeColors = function(colors, standart_colors) {
    this._gui_control_colors = { Colors: colors, StandartColors: standart_colors };
    var ret = this.handlers.trigger("asc_onSendThemeColors", colors, standart_colors);
    if (false !== ret) {
      this._gui_control_colors = null;
    }
  };

  spreadsheet_api.prototype.asc_SendThemeColorSchemes = function(param) {
    this._gui_color_schemes = param;
    var ret = this.handlers.trigger("asc_onSendThemeColorSchemes", param);
    if (false !== ret) {
      this._gui_color_schemes = null;
    }
  };
  spreadsheet_api.prototype.asc_ChangeColorScheme = function(index_scheme) {
    var t = this;
    var onChangeColorScheme = function(res) {
      if (res) {
        var theme = t.wbModel.theme;

        var oldClrScheme = theme.themeElements.clrScheme;
        var oColorScheme = AscCommon.g_oUserColorScheme;
        var _count_defaults = oColorScheme.length;
        if (index_scheme < _count_defaults) {
          var _obj = oColorScheme[index_scheme];
          var scheme = new AscFormat.ClrScheme();
          scheme.name = _obj.name;
          var _c;

          _c = _obj.dk1;
          scheme.colors[8] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.lt1;
          scheme.colors[12] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.dk2;
          scheme.colors[9] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.lt2;
          scheme.colors[13] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent1;
          scheme.colors[0] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent2;
          scheme.colors[1] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent3;
          scheme.colors[2] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent4;
          scheme.colors[3] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent5;
          scheme.colors[4] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.accent6;
          scheme.colors[5] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.hlink;
          scheme.colors[11] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          _c = _obj.folHlink;
          scheme.colors[10] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

          theme.themeElements.clrScheme = scheme;
        } else {
          index_scheme -= _count_defaults;

          if (index_scheme < 0 || index_scheme >= theme.extraClrSchemeLst.length) {
            return;
          }

          theme.themeElements.clrScheme = theme.extraClrSchemeLst[index_scheme].clrScheme.createDuplicate();
        }
        History.Create_NewPoint();
        //не делаем Duplicate потому что предполагаем что схема не будет менять частями, а только обьектом целиком.
        History.Add(AscCommonExcel.g_oUndoRedoWorkbook, AscCH.historyitem_Workbook_ChangeColorScheme, null, null, new AscCommonExcel.UndoRedoData_ClrScheme(oldClrScheme, theme.themeElements.clrScheme));
        t.asc_AfterChangeColorScheme();
      }
    };
    // ToDo поправить заглушку, сделать новый тип lock element-а
    var sheetId = -1; // Делаем не существующий лист и не существующий объект
    var lockInfo = this.collaborativeEditing.getLockInfo(c_oAscLockTypeElem.Object, /*subType*/null, sheetId, sheetId);
    this._getIsLockObjectSheet(lockInfo, onChangeColorScheme);
  };
  spreadsheet_api.prototype.asc_AfterChangeColorScheme = function() {
    this.wbModel.rebuildColors();
    this.asc_CheckGuiControlColors();
    this.asc_ApplyColorScheme(true);
  };
  spreadsheet_api.prototype.asc_ApplyColorScheme = function(bRedraw) {

    if (window['IS_NATIVE_EDITOR'] || !window["NATIVE_EDITOR_ENJINE"]) {
      var wsViews = Asc["editor"].wb.wsViews;
      for (var i = 0; i < wsViews.length; ++i) {
        if (wsViews[i] && wsViews[i].objectRender && wsViews[i].objectRender.controller) {
          wsViews[i].objectRender.controller.startRecalculate();
        }
      }
      this.chartPreviewManager.clearPreviews();
      this.textArtPreviewManager.clear();
    }

    // На view-режиме не нужно отправлять стили
    if (true !== this.getViewMode() && !this.isMobileVersion) {
      // Отправка стилей
      this._sendWorkbookStyles();
    }

    if (bRedraw) {
      this.handlers.trigger("asc_onUpdateChartStyles");
      this.wb.drawWS();
    }
  };

  /////////////////////////////////////////////////////////////////////////
  ////////////////////////////AutoSave api/////////////////////////////////
  /////////////////////////////////////////////////////////////////////////
  spreadsheet_api.prototype._autoSave = function() {
    if ((0 === this.autoSaveGap && (!this.collaborativeEditing.getFast() || !this.collaborativeEditing.getCollaborativeEditing()))
      || this.asc_getCellEditMode() || this.asc_getIsTrackShape() || this.isOpenedChartFrame ||
      !History.IsEndTransaction() || !this.canSave) {
      return;
    }
    if (!History.Is_Modified(true) && !(this.collaborativeEditing.getCollaborativeEditing() && 0 !== this.collaborativeEditing.getOwnLocksLength())) {
      if (this.collaborativeEditing.getFast() && this.collaborativeEditing.haveOtherChanges()) {
        AscCommon.CollaborativeEditing.Clear_CollaborativeMarks();

        // Принимаем чужие изменения
        this.collaborativeEditing.applyChanges();
        // Пересылаем свои изменения (просто стираем чужие lock-и, т.к. своих изменений нет)
        this.collaborativeEditing.sendChanges();
        // Шлем update для toolbar-а, т.к. когда select в lock ячейке нужно заблокировать toolbar
        this.wb._onWSSelectionChanged(/*info*/null);
      }
      return;
    }
    if (null === this.lastSaveTime) {
      this.lastSaveTime = new Date();
      return;
    }
    var saveGap = this.collaborativeEditing.getFast() ? this.autoSaveGapRealTime :
      (this.collaborativeEditing.getCollaborativeEditing() ? this.autoSaveGapSlow : this.autoSaveGapFast);
    var gap = new Date() - this.lastSaveTime - saveGap;
    if (0 <= gap) {
      this.asc_Save(true);
    }
  };

  spreadsheet_api.prototype._onUpdateDocumentCanSave = function() {
    // Можно модифицировать это условие на более быстрое (менять самим состояние в аргументах, а не запрашивать каждый раз)
    var tmp = History.Is_Modified() || (this.collaborativeEditing.getCollaborativeEditing() && 0 !== this.collaborativeEditing.getOwnLocksLength());
    if (tmp !== this.isDocumentCanSave) {
      this.isDocumentCanSave = tmp;
      this.handlers.trigger('asc_onDocumentCanSaveChanged', this.isDocumentCanSave);
    }
  };

  spreadsheet_api.prototype._onCheckCommentRemoveLock = function(lockElem) {
    var res = false;
    var sheetId = lockElem["sheetId"];
    if (-1 !== sheetId && 0 === sheetId.indexOf(AscCommonExcel.CCellCommentator.sStartCommentId)) {
      // Коммментарий
      res = true;
      this.handlers.trigger("asc_onUnLockComment", lockElem["rangeOrObjectId"]);
    }
    return res;
  };

  spreadsheet_api.prototype.onUpdateDocumentModified = function(bIsModified) {
    // Обновляем только после окончания сохранения
    if (this.canSave) {
      this.handlers.trigger("asc_onDocumentModifiedChanged", bIsModified);
      this._onUpdateDocumentCanSave();

      if (undefined !== window["AscDesktopEditor"]) {
        window["AscDesktopEditor"]["onDocumentModifiedChanged"](bIsModified);
      }
    }
  };

  // Выставление локали
  spreadsheet_api.prototype.asc_setLocalization = function(oLocalizedData) {
    if (null == oLocalizedData) {
      AscCommonExcel.cFormulaFunctionLocalized = null;
      AscCommonExcel.cFormulaFunctionToLocale = null;
    } else {
      AscCommonExcel.cFormulaFunctionLocalized = {};
      AscCommonExcel.cFormulaFunctionToLocale = {};
      var localName;
      for (var i in AscCommonExcel.cFormulaFunction) {
        localName = oLocalizedData[i] ? oLocalizedData[i] : null;
        localName = localName ? localName : i;
        AscCommonExcel.cFormulaFunctionLocalized[localName] = AscCommonExcel.cFormulaFunction[i];
        AscCommonExcel.cFormulaFunctionToLocale[i] = localName;
      }
    }
    AscCommon.build_local_rx(oLocalizedData?oLocalizedData["LocalFormulaOperands"]:null);
    if (this.wb) {
      this.wb.initFormulasList();
    }
    if (this.wbModel) {
      this.wbModel.rebuildColors();
    }
  };

  spreadsheet_api.prototype.asc_nativeOpenFile = function(base64File, version) {
    asc["editor"] = this;

    this.SpellCheckUrl = '';

    this.User = new AscCommon.asc_CUser();
    this.User.setId("TM");
    this.User.setUserName("native");

    this.wbModel = new AscCommonExcel.Workbook(this.handlers, this);
    this.initGlobalObjects(this.wbModel);

    var oBinaryFileReader = new AscCommonExcel.BinaryFileReader();

    if (undefined === version) {
      oBinaryFileReader.Read(base64File, this.wbModel);
    } else {
      AscCommon.CurFileVersion = version;
      oBinaryFileReader.ReadData(base64File, this.wbModel);
    }
    g_oIdCounter.Set_Load(false);

    this._coAuthoringInit();
    this.wb = new AscCommonExcel.WorkbookView(this.wbModel, this.controller, this.handlers, window["_null_object"], window["_null_object"], this, this.collaborativeEditing, this.fontRenderingMode);
  };

  spreadsheet_api.prototype.asc_nativeCalculateFile = function() {
    window['DoctRendererMode'] = true;	
    this.wb._nativeCalculate();
  };

  spreadsheet_api.prototype.asc_nativeApplyChanges = function(changes) {
    for (var i = 0, l = changes.length; i < l; ++i) {
      this.CoAuthoringApi.onSaveChanges(changes[i], null, true);
    }
    this.collaborativeEditing.applyChanges();
  };

  spreadsheet_api.prototype.asc_nativeApplyChanges2 = function(data, isFull) {
    if (null != this.wbModel) {
      this.oRedoObjectParamNative = this.wbModel.DeserializeHistoryNative(this.oRedoObjectParamNative, data, isFull);
    }
    if (isFull) {
      this._onUpdateAfterApplyChanges();
    }
  };

  spreadsheet_api.prototype.asc_nativeGetFile = function() {
    this.wb._initCommentsToSave();
    var oBinaryFileWriter = new AscCommonExcel.BinaryFileWriter(this.wbModel);
    return oBinaryFileWriter.Write();
  };
  spreadsheet_api.prototype.asc_nativeGetFileData = function() {
    this.wb._initCommentsToSave();
    var oBinaryFileWriter = new AscCommonExcel.BinaryFileWriter(this.wbModel);
    oBinaryFileWriter.Write2();

    var _header = oBinaryFileWriter.WriteFileHeader(oBinaryFileWriter.Memory.GetCurPosition());
    window["native"]["Save_End"](_header, oBinaryFileWriter.Memory.GetCurPosition());

    return oBinaryFileWriter.Memory.ImData.data;
  };

  spreadsheet_api.prototype.asc_nativeCheckPdfRenderer = function(_memory1, _memory2) {
    if (true) {
      // pos не должен минимизироваться!!!

      _memory1.Copy = _memory1["Copy"];
      _memory1.ClearNoAttack = _memory1["ClearNoAttack"];
      _memory1.WriteByte = _memory1["WriteByte"];
      _memory1.WriteBool = _memory1["WriteBool"];
      _memory1.WriteLong = _memory1["WriteLong"];
      _memory1.WriteDouble = _memory1["WriteDouble"];
      _memory1.WriteString = _memory1["WriteString"];
      _memory1.WriteString2 = _memory1["WriteString2"];

      _memory2.Copy = _memory1["Copy"];
      _memory2.ClearNoAttack = _memory1["ClearNoAttack"];
      _memory2.WriteByte = _memory1["WriteByte"];
      _memory2.WriteBool = _memory1["WriteBool"];
      _memory2.WriteLong = _memory1["WriteLong"];
      _memory2.WriteDouble = _memory1["WriteDouble"];
      _memory2.WriteString = _memory1["WriteString"];
      _memory2.WriteString2 = _memory1["WriteString2"];
    }

    var _printer = new AscCommonExcel.CPdfPrinter();
    _printer.DocumentRenderer.Memory = _memory1;
    _printer.DocumentRenderer.VectorMemoryForPrint = _memory2;
    return _printer;
  };

  spreadsheet_api.prototype.asc_nativeCalculate = function() {
  };

  spreadsheet_api.prototype.asc_nativePrint = function (_printer, _page, _param) {
    var _adjustPrint = window.AscDesktopEditor_PrintData || new Asc.asc_CAdjustPrint();
    window.AscDesktopEditor_PrintData = undefined;

    if (1 == _param) {
      _adjustPrint.asc_setPrintType(Asc.c_oAscPrintType.EntireWorkbook);
      var pageSetup;
      var countWorksheets = this.wbModel.getWorksheetCount();
      for (var j = 0; j < countWorksheets; ++j) {
        pageSetup = this.wbModel.getWorksheet(j).PagePrintOptions.asc_getPageSetup();
        pageSetup.asc_setFitToWidth(true);
        pageSetup.asc_setFitToHeight(true);
      }
    }

    var _printPagesData = this.wb.calcPagesPrint(_adjustPrint);

    if (undefined === _printer && _page === undefined) {
      var pdf_writer = new AscCommonExcel.CPdfPrinter();
      var isEndPrint = this.wb.printSheet(pdf_writer, _printPagesData);

      if (undefined !== window["AscDesktopEditor"]) {
        var pagescount = pdf_writer.DocumentRenderer.m_lPagesCount;

        window["AscDesktopEditor"]["Print_Start"](this.documentId + "/", pagescount, "", -1);

        for (var i = 0; i < pagescount; i++) {
          var _start = pdf_writer.DocumentRenderer.m_arrayPages[i].StartOffset;
          var _end = pdf_writer.DocumentRenderer.Memory.pos;
          if (i != (pagescount - 1)) {
            _end = pdf_writer.DocumentRenderer.m_arrayPages[i + 1].StartOffset;
          }

          window["AscDesktopEditor"]["Print_Page"](
            pdf_writer.DocumentRenderer.Memory.GetBase64Memory2(_start, _end - _start),
            pdf_writer.DocumentRenderer.m_arrayPages[i].Width, pdf_writer.DocumentRenderer.m_arrayPages[i].Height);
        }

        window["AscDesktopEditor"]["Print_End"]();
      }
      return pdf_writer.DocumentRenderer.Memory;
    }

    var isEndPrint = this.wb.printSheet(_printer, _printPagesData);
    return _printer.DocumentRenderer.Memory;
  };

  spreadsheet_api.prototype.asc_nativePrintPagesCount = function() {
    return 1;
  };

  spreadsheet_api.prototype.asc_nativeGetPDF = function(_param) {
    var _ret = this.asc_nativePrint(undefined, undefined, _param);

    window["native"]["Save_End"]("", _ret.GetCurPosition());
    return _ret.data;
  };

  spreadsheet_api.prototype.asc_canPaste = function () {
    History.Create_NewPoint();
    History.StartTransaction();
    return true;
  };
  spreadsheet_api.prototype.asc_Recalculate = function () {
    History.EndTransaction();
    this._onUpdateAfterApplyChanges();
  };

  spreadsheet_api.prototype._onEndLoadSdk = function() {
    History = AscCommon.History;

    if (this.isMobileVersion)
        this.asc_setMobileVersion(true);

    spreadsheet_api.superclass._onEndLoadSdk.call(this);

    this.controller = new AscCommonExcel.asc_CEventsController();

    this.formulasList = AscCommonExcel.getFormulasInfo();
    this.asc_setLocale(this.tmpLocale);
    this.asc_setViewMode(this.isViewMode);
  };

  /*
   * Export
   * -----------------------------------------------------------------------------
   */

  window["AscDesktopEditor_Save"] = function() {
    return window["Asc"]["editor"].asc_Save(false);
  };

  asc["spreadsheet_api"] = spreadsheet_api;
  prot = spreadsheet_api.prototype;

  prot["asc_GetFontThumbnailsPath"] = prot.asc_GetFontThumbnailsPath;
  prot["asc_setDocInfo"] = prot.asc_setDocInfo;
  prot["asc_getLocaleExample"] = prot.asc_getLocaleExample;
  prot["asc_getLocaleCurrency"] = prot.asc_getLocaleCurrency;
  prot["asc_setLocale"] = prot.asc_setLocale;
  prot["asc_getEditorPermissions"] = prot.asc_getEditorPermissions;
  prot["asc_LoadDocument"] = prot.asc_LoadDocument;
  prot["asc_LoadEmptyDocument"] = prot.asc_LoadEmptyDocument;
  prot["asc_DownloadAs"] = prot.asc_DownloadAs;
  prot["asc_Save"] = prot.asc_Save;
  prot["asc_Print"] = prot.asc_Print;
  prot["asc_Resize"] = prot.asc_Resize;
  prot["asc_Copy"] = prot.asc_Copy;
  prot["asc_Paste"] = prot.asc_Paste;
  prot["asc_Cut"] = prot.asc_Cut;
  prot["asc_Undo"] = prot.asc_Undo;
  prot["asc_Redo"] = prot.asc_Redo;

  prot["asc_getDocumentName"] = prot.asc_getDocumentName;
  prot["asc_isDocumentModified"] = prot.asc_isDocumentModified;
  prot["asc_isDocumentCanSave"] = prot.asc_isDocumentCanSave;
  prot["asc_getCanUndo"] = prot.asc_getCanUndo;
  prot["asc_getCanRedo"] = prot.asc_getCanRedo;

  prot["asc_setAutoSaveGap"] = prot.asc_setAutoSaveGap;

  prot["asc_setMobileVersion"] = prot.asc_setMobileVersion;
  prot["asc_setViewMode"] = prot.asc_setViewMode;
  prot["asc_setUseEmbeddedCutFonts"] = prot.asc_setUseEmbeddedCutFonts;
  prot["asc_setAdvancedOptions"] = prot.asc_setAdvancedOptions;
  prot["asc_setPageOptions"] = prot.asc_setPageOptions;
  prot["asc_getPageOptions"] = prot.asc_getPageOptions;

  prot["asc_registerCallback"] = prot.asc_registerCallback;
  prot["asc_unregisterCallback"] = prot.asc_unregisterCallback;

  prot["asc_getController"] = prot.asc_getController;
  prot["asc_changeArtImageFromFile"] = prot.asc_changeArtImageFromFile;

  prot["asc_SetDocumentPlaceChangedEnabled"] = prot.asc_SetDocumentPlaceChangedEnabled;
  prot["asc_SetFastCollaborative"] = prot.asc_SetFastCollaborative;

  // Workbook interface

  prot["asc_getWorksheetsCount"] = prot.asc_getWorksheetsCount;
  prot["asc_getWorksheetName"] = prot.asc_getWorksheetName;
  prot["asc_getWorksheetTabColor"] = prot.asc_getWorksheetTabColor;
  prot["asc_setWorksheetTabColor"] = prot.asc_setWorksheetTabColor;
  prot["asc_getActiveWorksheetIndex"] = prot.asc_getActiveWorksheetIndex;
  prot["asc_getActiveWorksheetId"] = prot.asc_getActiveWorksheetId;
  prot["asc_getWorksheetId"] = prot.asc_getWorksheetId;
  prot["asc_isWorksheetHidden"] = prot.asc_isWorksheetHidden;
  prot["asc_isWorksheetLockedOrDeleted"] = prot.asc_isWorksheetLockedOrDeleted;
  prot["asc_isWorkbookLocked"] = prot.asc_isWorkbookLocked;
  prot["asc_getHiddenWorksheets"] = prot.asc_getHiddenWorksheets;
  prot["asc_showWorksheet"] = prot.asc_showWorksheet;
  prot["asc_showActiveWorksheet"] = prot.asc_showActiveWorksheet;
  prot["asc_hideWorksheet"] = prot.asc_hideWorksheet;
  prot["asc_renameWorksheet"] = prot.asc_renameWorksheet;
  prot["asc_addWorksheet"] = prot.asc_addWorksheet;
  prot["asc_insertWorksheet"] = prot.asc_insertWorksheet;
  prot["asc_deleteWorksheet"] = prot.asc_deleteWorksheet;
  prot["asc_moveWorksheet"] = prot.asc_moveWorksheet;
  prot["asc_copyWorksheet"] = prot.asc_copyWorksheet;
  prot["asc_cleanSelection"] = prot.asc_cleanSelection;
  prot["asc_getZoom"] = prot.asc_getZoom;
  prot["asc_setZoom"] = prot.asc_setZoom;
  prot["asc_enableKeyEvents"] = prot.asc_enableKeyEvents;
  prot["asc_searchEnabled"] = prot.asc_searchEnabled;
  prot["asc_findText"] = prot.asc_findText;
  prot["asc_replaceText"] = prot.asc_replaceText;
  prot["asc_endFindText"] = prot.asc_endFindText;
  prot["asc_findCell"] = prot.asc_findCell;
  prot["asc_closeCellEditor"] = prot.asc_closeCellEditor;

  // Spreadsheet interface

  prot["asc_getColumnWidth"] = prot.asc_getColumnWidth;
  prot["asc_setColumnWidth"] = prot.asc_setColumnWidth;
  prot["asc_showColumns"] = prot.asc_showColumns;
  prot["asc_hideColumns"] = prot.asc_hideColumns;
  prot["asc_getRowHeight"] = prot.asc_getRowHeight;
  prot["asc_setRowHeight"] = prot.asc_setRowHeight;
  prot["asc_showRows"] = prot.asc_showRows;
  prot["asc_hideRows"] = prot.asc_hideRows;
  prot["asc_insertCells"] = prot.asc_insertCells;
  prot["asc_deleteCells"] = prot.asc_deleteCells;
  prot["asc_mergeCells"] = prot.asc_mergeCells;
  prot["asc_sortCells"] = prot.asc_sortCells;
  prot["asc_emptyCells"] = prot.asc_emptyCells;
  prot["asc_mergeCellsDataLost"] = prot.asc_mergeCellsDataLost;
  prot["asc_getSheetViewSettings"] = prot.asc_getSheetViewSettings;
  prot["asc_setSheetViewSettings"] = prot.asc_setSheetViewSettings;

  // Defined Names
  prot["asc_getDefinedNames"] = prot.asc_getDefinedNames;
  prot["asc_setDefinedNames"] = prot.asc_setDefinedNames;
  prot["asc_editDefinedNames"] = prot.asc_editDefinedNames;
  prot["asc_delDefinedNames"] = prot.asc_delDefinedNames;
  prot["asc_getDefaultDefinedName"] = prot.asc_getDefaultDefinedName;
  prot["asc_checkDefinedName"] = prot.asc_checkDefinedName;

  // Auto filters interface + format as table
  prot["asc_addAutoFilter"] = prot.asc_addAutoFilter;
  prot["asc_changeAutoFilter"] = prot.asc_changeAutoFilter;
  prot["asc_applyAutoFilter"] = prot.asc_applyAutoFilter;
  prot["asc_applyAutoFilterByType"] = prot.asc_applyAutoFilterByType;
  prot["asc_reapplyAutoFilter"] = prot.asc_reapplyAutoFilter;
  prot["asc_sortColFilter"] = prot.asc_sortColFilter;
  prot["asc_getAddFormatTableOptions"] = prot.asc_getAddFormatTableOptions;
  prot["asc_clearFilter"] = prot.asc_clearFilter;
  prot["asc_clearFilterColumn"] = prot.asc_clearFilterColumn;
  prot["asc_changeSelectionFormatTable"] = prot.asc_changeSelectionFormatTable;
  prot["asc_changeFormatTableInfo"] = prot.asc_changeFormatTableInfo;
  prot["asc_insertCellsInTable"] = prot.asc_insertCellsInTable;
  prot["asc_deleteCellsInTable"] = prot.asc_deleteCellsInTable;
  prot["asc_changeDisplayNameTable"] = prot.asc_changeDisplayNameTable;
  prot["asc_changeTableRange"] = prot.asc_changeTableRange;
  prot["asc_getTablePictures"] = prot.asc_getTablePictures;

  // Drawing objects interface

  prot["asc_showDrawingObjects"] = prot.asc_showDrawingObjects;
  prot["asc_setChartTranslate"] = prot.asc_setChartTranslate;
  prot["asc_setTextArtTranslate"] = prot.asc_setTextArtTranslate;
  prot["asc_drawingObjectsExist"] = prot.asc_drawingObjectsExist;
  prot["asc_getChartObject"] = prot.asc_getChartObject;
  prot["asc_addChartDrawingObject"] = prot.asc_addChartDrawingObject;
  prot["asc_editChartDrawingObject"] = prot.asc_editChartDrawingObject;
  prot["asc_addImageDrawingObject"] = prot.asc_addImageDrawingObject;
  prot["asc_setSelectedDrawingObjectLayer"] = prot.asc_setSelectedDrawingObjectLayer;
  prot["asc_getChartPreviews"] = prot.asc_getChartPreviews;
  prot["asc_getTextArtPreviews"] = prot.asc_getTextArtPreviews;
  prot['asc_getPropertyEditorShapes'] = prot.asc_getPropertyEditorShapes;
  prot['asc_getPropertyEditorTextArts'] = prot.asc_getPropertyEditorTextArts;
  prot["asc_checkDataRange"] = prot.asc_checkDataRange;
  prot["asc_getBinaryFileWriter"] = prot.asc_getBinaryFileWriter;
  prot["asc_getWordChartObject"] = prot.asc_getWordChartObject;
  prot["asc_cleanWorksheet"] = prot.asc_cleanWorksheet;
  prot["asc_showImageFileDialog"] = prot.asc_showImageFileDialog;
  prot["asc_addImage"] = prot.asc_addImage;
  prot["asc_setData"] = prot.asc_setData;
  prot["asc_getData"] = prot.asc_getData;
  prot["asc_onCloseChartFrame"] = prot.asc_onCloseChartFrame;

  // Cell comment interface
  prot["asc_addComment"] = prot.asc_addComment;
  prot["asc_changeComment"] = prot.asc_changeComment;
  prot["asc_findComment"] = prot.asc_findComment;
  prot["asc_removeComment"] = prot.asc_removeComment;
  prot["asc_showComment"] = prot.asc_showComment;
  prot["asc_selectComment"] = prot.asc_selectComment;

  prot["asc_showComments"] = prot.asc_showComments;
  prot["asc_hideComments"] = prot.asc_hideComments;

  prot["asc_getComments"] = prot.asc_getComments;
  prot["asc_getDocumentComments"] = prot.asc_getDocumentComments;

  // Shapes
  prot["setStartPointHistory"] = prot.setStartPointHistory;
  prot["setEndPointHistory"] = prot.setEndPointHistory;
  prot["asc_startAddShape"] = prot.asc_startAddShape;
  prot["asc_endAddShape"] = prot.asc_endAddShape;
  prot["asc_isAddAutoshape"] = prot.asc_isAddAutoshape;
  prot["asc_canAddShapeHyperlink"] = prot.asc_canAddShapeHyperlink;
  prot["asc_canGroupGraphicsObjects"] = prot.asc_canGroupGraphicsObjects;
  prot["asc_groupGraphicsObjects"] = prot.asc_groupGraphicsObjects;
  prot["asc_canUnGroupGraphicsObjects"] = prot.asc_canUnGroupGraphicsObjects;
  prot["asc_unGroupGraphicsObjects"] = prot.asc_unGroupGraphicsObjects;
  prot["asc_getGraphicObjectProps"] = prot.asc_getGraphicObjectProps;
  prot["asc_setGraphicObjectProps"] = prot.asc_setGraphicObjectProps;
  prot["asc_getOriginalImageSize"] = prot.asc_getOriginalImageSize;
  prot["asc_changeShapeType"] = prot.asc_changeShapeType;
  prot["asc_setInterfaceDrawImagePlaceShape"] = prot.asc_setInterfaceDrawImagePlaceShape;
  prot["asc_setInterfaceDrawImagePlaceTextArt"] = prot.asc_setInterfaceDrawImagePlaceTextArt;
  prot["asc_changeImageFromFile"] = prot.asc_changeImageFromFile;
  prot["asc_putPrLineSpacing"] = prot.asc_putPrLineSpacing;
  prot["asc_addTextArt"] = prot.asc_addTextArt;
  prot["asc_putLineSpacingBeforeAfter"] = prot.asc_putLineSpacingBeforeAfter;
  prot["asc_setDrawImagePlaceParagraph"] = prot.asc_setDrawImagePlaceParagraph;
  prot["asc_changeShapeImageFromFile"] = prot.asc_changeShapeImageFromFile;

  // Frozen pane
  prot["asc_freezePane"] = prot.asc_freezePane;

  // Cell interface
  prot["asc_getCellInfo"] = prot.asc_getCellInfo;
  prot["asc_getActiveCellCoord"] = prot.asc_getActiveCellCoord;
  prot["asc_getAnchorPosition"] = prot.asc_getAnchorPosition;
  prot["asc_setCellFontName"] = prot.asc_setCellFontName;
  prot["asc_setCellFontSize"] = prot.asc_setCellFontSize;
  prot["asc_setCellBold"] = prot.asc_setCellBold;
  prot["asc_setCellItalic"] = prot.asc_setCellItalic;
  prot["asc_setCellUnderline"] = prot.asc_setCellUnderline;
  prot["asc_setCellStrikeout"] = prot.asc_setCellStrikeout;
  prot["asc_setCellSubscript"] = prot.asc_setCellSubscript;
  prot["asc_setCellSuperscript"] = prot.asc_setCellSuperscript;
  prot["asc_setCellAlign"] = prot.asc_setCellAlign;
  prot["asc_setCellVertAlign"] = prot.asc_setCellVertAlign;
  prot["asc_setCellTextWrap"] = prot.asc_setCellTextWrap;
  prot["asc_setCellTextShrink"] = prot.asc_setCellTextShrink;
  prot["asc_setCellTextColor"] = prot.asc_setCellTextColor;
  prot["asc_setCellBackgroundColor"] = prot.asc_setCellBackgroundColor;
  prot["asc_setCellBorders"] = prot.asc_setCellBorders;
  prot["asc_setCellFormat"] = prot.asc_setCellFormat;
  prot["asc_setCellAngle"] = prot.asc_setCellAngle;
  prot["asc_setCellStyle"] = prot.asc_setCellStyle;
  prot["asc_increaseCellDigitNumbers"] = prot.asc_increaseCellDigitNumbers;
  prot["asc_decreaseCellDigitNumbers"] = prot.asc_decreaseCellDigitNumbers;
  prot["asc_increaseFontSize"] = prot.asc_increaseFontSize;
  prot["asc_decreaseFontSize"] = prot.asc_decreaseFontSize;
  prot["asc_formatPainter"] = prot.asc_formatPainter;

  prot["asc_onMouseUp"] = prot.asc_onMouseUp;

  prot["asc_selectFunction"] = prot.asc_selectFunction;
  prot["asc_insertHyperlink"] = prot.asc_insertHyperlink;
  prot["asc_removeHyperlink"] = prot.asc_removeHyperlink;
  prot["asc_insertFormula"] = prot.asc_insertFormula;
  prot["asc_getFormulasInfo"] = prot.asc_getFormulasInfo;
  prot["asc_getFormulaLocaleName"] = prot.asc_getFormulaLocaleName;
  prot["asc_setFontRenderingMode"] = prot.asc_setFontRenderingMode;
  prot["asc_setSelectionDialogMode"] = prot.asc_setSelectionDialogMode;
  prot["asc_ChangeColorScheme"] = prot.asc_ChangeColorScheme;
  /////////////////////////////////////////////////////////////////////////
  ///////////////////CoAuthoring and Chat api//////////////////////////////
  /////////////////////////////////////////////////////////////////////////
  prot["asc_coAuthoringChatSendMessage"] = prot.asc_coAuthoringChatSendMessage;
  prot["asc_coAuthoringGetUsers"] = prot.asc_coAuthoringGetUsers;
  prot["asc_coAuthoringChatGetMessages"] = prot.asc_coAuthoringChatGetMessages;
  prot["asc_coAuthoringDisconnect"] = prot.asc_coAuthoringDisconnect;

  // other
  prot["asc_stopSaving"] = prot.asc_stopSaving;
  prot["asc_continueSaving"] = prot.asc_continueSaving;

  // Version History
  prot["asc_undoAllChanges"] = prot.asc_undoAllChanges;

  prot["asc_setLocalization"] = prot.asc_setLocalization;

  // native
  prot["asc_nativeOpenFile"] = prot.asc_nativeOpenFile;
  prot["asc_nativeCalculateFile"] = prot.asc_nativeCalculateFile;
  prot["asc_nativeApplyChanges"] = prot.asc_nativeApplyChanges;
  prot["asc_nativeApplyChanges2"] = prot.asc_nativeApplyChanges2;
  prot["asc_nativeGetFile"] = prot.asc_nativeGetFile;
  prot["asc_nativeGetFileData"] = prot.asc_nativeGetFileData;
  prot["asc_nativeCheckPdfRenderer"] = prot.asc_nativeCheckPdfRenderer;
  prot["asc_nativeCalculate"] = prot.asc_nativeCalculate;
  prot["asc_nativePrint"] = prot.asc_nativePrint;
  prot["asc_nativePrintPagesCount"] = prot.asc_nativePrintPagesCount;
  prot["asc_nativeGetPDF"] = prot.asc_nativeGetPDF;
  
  prot['asc_isOffline'] = prot.asc_isOffline;
  prot['asc_getUrlType'] = prot.asc_getUrlType;

  // Builder
  prot['asc_nativeInitBuilder'] = prot.asc_nativeInitBuilder;
  prot['asc_SetSilentMode'] = prot.asc_SetSilentMode;

  // plugins
  prot["asc_pluginsRegister"]       = prot.asc_pluginsRegister;
  prot["asc_pluginRun"]             = prot.asc_pluginRun;
  prot["asc_pluginResize"]          = prot.asc_pluginResize;
  prot["asc_pluginButtonClick"]     = prot.asc_pluginButtonClick;
  prot["asc_addOleObject"]          = prot.asc_addOleObject;
  prot["asc_editOleObject"]         = prot.asc_editOleObject;
})(window);

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

AscCommon.baseEditorsApi.prototype._onEndPermissions = function()
{
	if (this.isOnFirstConnectEnd && this.isOnLoadLicense)
	{
		var oResult = new AscCommon.asc_CAscEditorPermissions();
		oResult.asc_setCanLicense(true);
		oResult.asc_setCanBranding(true);
		this.sendEvent('asc_onGetEditorPermissions', oResult);
	}
};
"use strict";

AscCommon.readBlobAsDataURL = function (blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", function () {
      resolve(fr.result);
    });
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsDataURL(blob);
  }, function () {
    fr.abort();
  });
};

AscCommon.downloadUrlAsBlob = function (url) {
  var xhr = new XMLHttpRequest();
  return new RSVP.Promise(function (resolve, reject) {
    xhr.open("GET", url);
    xhr.responseType = "blob";//force the HTTP response, response-type header to be blob
    xhr.onload = function () {
      if (this.status === 200) {
        resolve(xhr.response);
      } else {
        reject(this.status)
      }
    };
    xhr.onerror = reject;
    xhr.send();
  }, function () {
    xhr.abort();
  });
};

AscCommon.baseEditorsApi.prototype.jio_open = function () {
  var t = this,
    g = Common.Gateway;
  g.jio_getAttachment('/', 'body.txt')
    .push(undefined, function (error) {
      if (error.status_code === 404) {
        return g.props.value;
      }
      throw error;
    })
    .push(function (doc) {
      if (!doc) {
        switch (g.props.documentType) {
          case "presentation":
            doc = t.getEmpty();
            break;
          case "spreadsheet":
            doc = "XLSY;v2;2286;BAKAAgAAA+cHAAAEAwgAAADqCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGMFAAAAEQAAAAEMAAAABwEAAAAACAEAAAAABAoAAAAFAAAAAAUAAAAABnwAAAAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRABxoAAAAEBgoAAABBAHIAaQBhAGwABgUAAAAAAAAkQAcaAAAABAYKAAAAQQByAGkAYQBsAAYFAAAAAAAAJEAHGgAAAAQGCgAAAEEAcgBpAGEAbAAGBQAAAAAAACRACB8AAAAJGgAAAAAGDgAAAEcARQBOAEUAUgBBAEwAAQSkAAAADhYDAAADPwAAAAABAQEBAQMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAgAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQCAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAAAAAAkEAAAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQAAAAACQQAAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAAAAAAJBAAAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKwAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQpAAAAAyEAAAAAAQABAQADAQEGBAAAAAAHBAAAAAAIBAEAAAAJBCwAAAADIQAAAAABAAEBAAMBAQYEAAAAAAcEAAAAAAgEAQAAAAkEKgAAAAMhAAAAAAEAAQEAAwEBBgQAAAAABwQAAAAACAQBAAAACQQJAAAAAkoAAAADRQAAAAABAAEBAAMBAAYEAAAAAAcEAAAAAAgEAAAAAAkEpAAAAAwEAAAAAA0GGAAAAAABBAEEAAAAAAUBAAYEAAAAAAcBAAgBAA8qAQAAECkAAAAABAAAAAAAAAABAQAAAAAEDAAAAE4AbwByAG0AYQBsAAUEAAAAAAAAABAnAAAAAAQAAAADAAAAAQEAAAAABAoAAABDAG8AbQBtAGEABQQAAAAPAAAAEC8AAAAABAAAAAYAAAABAQAAAAAEEgAAAEMAbwBtAG0AYQAgAFsAMABdAAUEAAAAEAAAABAtAAAAAAQAAAAEAAAAAQEAAAAABBAAAABDAHUAcgByAGUAbgBjAHkABQQAAAARAAAAEDUAAAAABAAAAAcAAAABAQAAAAAEGAAAAEMAdQByAHIAZQBuAGMAeQAgAFsAMABdAAUEAAAAEgAAABArAAAAAAQAAAAFAAAAAQEAAAAABA4AAABQAGUAcgBjAGUAbgB0AAUEAAAAEwAAABgAAAAAAwAAAAEBAAELAAAAAgYAAAAABAAAAADjAAAAAN4AAAABGwAAAAAGDAAAAFMAaABlAGUAdAAxAAEEAQAAAAIBAgIkAAAAAx8AAAABAQACBAEEAAADBAEAAAAEBAAAAAAFBXnalahdiStABAQAAABBADEAFhEAAAAXDAAAAAQBAAAAAQYBAAAAAQsKAAAAAQWamZmZmZkpQA48AAAAAAVxPQrXowA0QAEFKFyPwvUIOkACBXE9CtejADRAAwUoXI/C9Qg6QAQFcT0K16MANEAFBXE9CtejADRADwYAAAAAAQEBAQkQBgAAAAABAQEBAAkAAAAAGAYAAAACAQAAAAAAAAAA";
            break;
          case "text":
            doc = "DOCY;v4;8985;BQCAAgAACYYCAAAFvAIAAAbYDwAABzMQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAAAADIAAAAAJAAAAAABAAEBAQIBAgMBAwQBBAUBBQYBCgcBCwgBCAkBCQoBBgsBBwEEAAAAQQ4TABgNAAAAGwAAAAkGFQAAAAoFOMEBAAsBAQwFAAAAAA0FCWIFAAFMAAAABAYKAAAAQQByAGkAYQBsAAUGCgAAAEEAcgBpAGEAbAAGBgoAAABBAHIAaQBhAGwABwYKAAAAQQByAGkAYQBsAAgEFgAAABYEFgAAAAKiDAAAACoAAAABAgAAAGEAAgwAAABOAG8AcgBtAGEAbAAJAQAAAAMIAQAAAAEKAQAAAAEAugAAAAECAAAAMQACEgAAAGgAZQBhAGQAaQBuAGcAIAAxAAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAAJAAAABVcAAAAAAQEEBgoAAABBAHIAaQBhAGwABQYKAAAAQQByAGkAYQBsAAYGCgAAAEEAcgBpAGEAbAAHBgoAAABBAHIAaQBhAGwACAQwAAAACQMAAAAUAQEWBDAAAAAGGAAAAAYBAQcBAQkGDAAAAAwFSusMAA0FAAAAAAC6AAAAAQIAAAAyAAISAAAAaABlAGEAZABpAG4AZwAgADIACQEAAAADAwIAAABhAAQCAAAAYQAKAQAAAAELBAAAAAkAAAAOAQAAAAEFUQAAAAABAQQGCgAAAEEAcgBpAGEAbAAFBgoAAABBAHIAaQBhAGwABgYKAAAAQQByAGkAYQBsAAcGCgAAAEEAcgBpAGEAbAAIBCgAAAAJAwAAABQBAQYYAAAABgEBBwEBCQYMAAAADAUJYgUADQUAAAAAAMYAAAABAgAAADMAAhIAAABoAGUAYQBkAGkAbgBnACAAMwAJAQAAAAMDAgAAAGEABAIAAABhAAoBAAAAAQsEAAAACQAAAA4BAAAAAQVdAAAAAAEBAQEBBAYKAAAAQQByAGkAYQBsAAUGCgAAAEEAcgBpAGEAbAAGBgoAAABBAHIAaQBhAGwABwYKAAAAQQByAGkAYQBsAAgEJAAAAAkDAAAAFAEBFQEBFgQkAAAABhgAAAAGAQEHAQEJBgwAAAAMBQliBQANBQAAAAAAugAAAAECAAAANAACEgAAAGgAZQBhAGQAaQBuAGcAIAA0AAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAAJAAAADgEAAAABBVEAAAAEBgoAAABBAHIAaQBhAGwABQYKAAAAQQByAGkAYQBsAAYGCgAAAEEAcgBpAGEAbAAHBgoAAABBAHIAaQBhAGwACAQgAAAACQMjIyMWBCAAAAAGGAAAAAYBAQcBAQkGDAAAAAwFCWIFAA0FAAAAAADAAAAAAQIAAAA1AAISAAAAaABlAGEAZABpAG4AZwAgADUACQEAAAADAwIAAABhAAQCAAAAYQAKAQAAAAELBAAAAAkAAAAOAQAAAAEFVwAAAAABAQQGCgAAAEEAcgBpAGEAbAAFBgoAAABBAHIAaQBhAGwABgYKAAAAQQByAGkAYQBsAAcGCgAAAEEAcgBpAGEAbAAIBBwAAAAJA0RERBQBARYEHAAAAAYYAAAABgEBBwEBCQYMAAAADAUJYgUADQUAAAAAAMAAAAABAgAAADYAAhIAAABoAGUAYQBkAGkAbgBnACAANgAJAQAAAAMDAgAAAGEABAIAAABhAAoBAAAAAQsEAAAACQAAAA4BAAAAAQVXAAAAAQEBBAYKAAAAQQByAGkAYQBsAAUGCgAAAEEAcgBpAGEAbAAGBgoAAABBAHIAaQBhAGwABwYKAAAAQQByAGkAYQBsAAgEHAAAAAkDIyMjFQEBFgQcAAAABhgAAAAGAQEHAQEJBgwAAAAMBQliBQANBQAAAAAAwAAAAAECAAAANwACEgAAAGgAZQBhAGQAaQBuAGcAIAA3AAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAAJAAAADgEAAAABBVcAAAAAAQEEBgoAAABBAHIAaQBhAGwABQYKAAAAQQByAGkAYQBsAAYGCgAAAEEAcgBpAGEAbAAHBgoAAABBAHIAaQBhAGwACAQYAAAACQNgYGAUAQEWBBgAAAAGGAAAAAYBAQcBAQkGDAAAAAwFCWIFAA0FAAAAAAC6AAAAAQIAAAA4AAISAAAAaABlAGEAZABpAG4AZwAgADgACQEAAAADAwIAAABhAAQCAAAAYQAKAQAAAAELBAAAAAkAAAAOAQAAAAEFUQAAAAQGCgAAAEEAcgBpAGEAbAAFBgoAAABBAHIAaQBhAGwABgYKAAAAQQByAGkAYQBsAAcGCgAAAEEAcgBpAGEAbAAIBBgAAAAJA0RERBYEGAAAAAYYAAAABgEBBwEBCQYMAAAADAUJYgUADQUAAAAAAMAAAAABAgAAADkAAhIAAABoAGUAYQBkAGkAbgBnACAAOQAJAQAAAAMDAgAAAGEABAIAAABhAAoBAAAAAQsEAAAACQAAAA4BAAAAAQVXAAAAAQEBBAYKAAAAQQByAGkAYQBsAAUGCgAAAEEAcgBpAGEAbAAGBgoAAABBAHIAaQBhAGwABwYKAAAAQQByAGkAYQBsAAgEFwAAAAkDREREFQEBFgQXAAAABhgAAAAGAQEHAQEJBgwAAAAMBQliBQANBQAAAAAAkgAAAAEEAAAAYQAxAAIYAAAATgBvAHIAbQBhAGwAIABUAGEAYgBsAGUACQEAAAAECAEAAAABCwQAAABjAAAADQEAAAABDgEAAAABB0YAAAADBAAAAAAAAAAFOAAAAAAJAAAAAAEBAgRsAAAAAQkAAAAAAQECBAAAAAACCQAAAAABAQIEbAAAAAMJAAAAAAEBAgQAAAAAAD0AAAABBAAAAGEAMgACDgAAAE4AbwAgAEwAaQBzAHQACQEAAAACCAEAAAABCwQAAABjAAAADQEAAAABDgEAAAABAHQAAAABBAAAAGEAMwACDAAAAGYAbwBvAHQAZQByAAkBAAAAAwMCAAAAYQALBAAAAGMAAAAOAQAAAAEGOQAAAAkGDwAAAAoFoIYBAAsBAQ0FAAAAABEGHgAAABIGCQAAABQBAhMFbOF9ABIGCQAAABQBARMFvMn7AAB0AAAAAQQAAABhADUAAgwAAABoAGUAYQBkAGUAcgAJAQAAAAMDAgAAAGEACwQAAABjAAAADgEAAAABBjkAAAAJBg8AAAAKBaCGAQALAQENBQAAAAARBh4AAAASBgkAAAAUAQITBWzhfQASBgkAAAAUAQETBbzJ+wAAUQAAAAEEAAAAYQA3AAIUAAAATgBvACAAUwBwAGEAYwBpAG4AZwAJAQAAAAMKAQAAAAELBAAAAAEAAAAGFQAAAAkGDwAAAAoFoIYBAAsBAQ0FAAAAAABrAAAAAQQAAAAyADEAAgoAAABRAHUAbwB0AGUACQEAAAADAwIAAABhAAQCAAAAYQAKAQAAAAELBAAAAB0AAAAFFwAAAAEBAQgEEgAAAAkDNzc3FQEBFgQSAAAABg8AAAABBgYAAAACBegVegAFAQMAvQAAAAEEAAAAYQA4AAIQAAAAUwB1AGIAdABpAHQAbABlAAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAALAAAABVcAAAABAQEEBgoAAABBAHIAaQBhAGwABQYKAAAAQQByAGkAYQBsAAYGCgAAAEEAcgBpAGEAbAAHBgoAAABBAHIAaQBhAGwACAQ0AAAACQNEREQVAQEWBDQAAAAGGwAAABYGBgAAABcEAQAAAAkGCQAAAAoFoIYBAAsBAQD/AAAAAQQAAABhAGEAAhoAAABJAG4AdABlAG4AcwBlACAAUQB1AG8AdABlAAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAAeAAAABR0AAAAAAQEBAQEIBBMAAAAJA0ZGRhQBARUBARYEEwAAAAaNAAAAAQYMAAAAAgW9Qg8AAwW9Qg8ABQEDDgYIAAAAAAEAAQPu7u4bBmQAAAAAFAAAAAADgICAAQU3JwIAAgXmRAAAAwEBARQAAAAAA4CAgAEFzYkAAAIF5kQAAAMBAQIUAAAAAAOAgIABBTcnAgACBeZEAAADAQEDFAAAAAADgICAAQXNiQAAAgXmRAAAAwEBANsAAAABBgAAAGEAZgAyAAIKAAAAVABpAHQAbABlAAkBAAAAAwMCAAAAYQAEAgAAAGEACgEAAAABCwQAAAAKAAAABVcAAAAAAQEEBgoAAABBAHIAaQBhAGwABQYKAAAAQQByAGkAYQBsAAYGCgAAAEEAcgBpAGEAbAAHBgoAAABBAHIAaQBhAGwACARIAAAACQMAAAAUAQEWBEgAAAAGPQAAAAABAQkGFQAAAAoFoIYBAAsBAQwFDhMIAA0FNycCABsGGQAAAAMUAAAAAAMAAAABBQAAAAACBWmdAQADAQEAXAAAAAEGAAAAYQBmADUAAhwAAABMAGkAcwB0ACAAUABhAHIAYQBnAHIAYQBwAGgACQEAAAADAwIAAABhAAoBAAAAAQsEAAAAIgAAAAYPAAAAAAEBAQYGAAAAAgXwYBMAVwAAAAAFAAAAAgAAAAAESAAAAAAPAAAAAAWdckABAQUJMcUBAgEAASQAAAAABTfILQABBXqFHgACBangFgADBXqFHgAEBfBgEwAFBSUVEwACBgAAAAABAAEBAOISAAAD3RIAABTYEgAA+gAMAAAATwBmAGYAaQBjAGUAIABUAGgAZQBtAGUA+wCrEgAAABUBAAD6AAYAAABPAGYAZgBpAGMAZQD7DB4AAAAEGQAAAPoABgAAAHcAaQBuAGQAbwB3AAH/Av8D//sNDQAAAAEIAAAA+gDuAewC4fsIJgAAAAQhAAAA+gAKAAAAdwBpAG4AZABvAHcAVABlAHgAdAABAAIAAwD7Cg0AAAABCAAAAPoAgAEAAoD7AA0AAAABCAAAAPoATwGBAr37CQ0AAAABCAAAAPoAHwFJAn37AQ0AAAABCAAAAPoAwAFQAk37Ag0AAAABCAAAAPoAmwG7Aln7Aw0AAAABCAAAAPoAgAFkAqL7Cw0AAAABCAAAAPoAAAEAAv/7BA0AAAABCAAAAPoASwGsAsb7BQ0AAAABCAAAAPoA9wGWAkb7AaMKAAD6ABAAAABPAGYAZgBpAGMAZQAgAEMAbABhAHMAcwBpAGMAIAAyAPsAOQUAAAARAAAA+gMFAAAAQQByAGkAYQBsAPsBEQAAAPoDBQAAAEEAcgBpAGEAbAD7AhEAAAD6AwUAAABBAHIAaQBhAGwA+wPyBAAAHgAAAAAkAAAA+gAEAAAASgBwAGEAbgABCAAAAC3/M/8gADD/tDC3MMMwrzD7ABgAAAD6AAQAAABIAGEAbgBnAAECAAAAdK28ufsAGAAAAPoABAAAAEgAYQBuAHMAAQIAAADRnlNP+wAeAAAA+gAEAAAASABhAG4AdAABBQAAAK5f345ja9Ge1Jr7AB4AAAD6AAQAAABBAHIAYQBiAAEFAAAAQQByAGkAYQBsAPsAHgAAAPoABAAAAEgAZQBiAHIAAQUAAABBAHIAaQBhAGwA+wAoAAAA+gAEAAAAVABoAGEAaQABCgAAAEMAbwByAGQAaQBhACAATgBlAHcA+wAeAAAA+gAEAAAARQB0AGgAaQABBQAAAE4AeQBhAGwAYQD7ACAAAAD6AAQAAABCAGUAbgBnAAEGAAAAVgByAGkAbgBkAGEA+wAgAAAA+gAEAAAARwB1AGoAcgABBgAAAFMAaAByAHUAdABpAPsAJAAAAPoABAAAAEsAaABtAHIAAQgAAABEAGEAdQBuAFAAZQBuAGgA+wAeAAAA+gAEAAAASwBuAGQAYQABBQAAAFQAdQBuAGcAYQD7AB4AAAD6AAQAAABHAHUAcgB1AAEFAAAAUgBhAGEAdgBpAPsAJAAAAPoABAAAAEMAYQBuAHMAAQgAAABFAHUAcABoAGUAbQBpAGEA+wA8AAAA+gAEAAAAQwBoAGUAcgABFAAAAFAAbABhAG4AdABhAGcAZQBuAGUAdAAgAEMAaABlAHIAbwBrAGUAZQD7ADgAAAD6AAQAAABZAGkAaQBpAAESAAAATQBpAGMAcgBvAHMAbwBmAHQAIABZAGkAIABCAGEAaQB0AGkA+wA4AAAA+gAEAAAAVABpAGIAdAABEgAAAE0AaQBjAHIAbwBzAG8AZgB0ACAASABpAG0AYQBsAGEAeQBhAPsAIgAAAPoABAAAAFQAaABhAGEAAQcAAABNAFYAIABCAG8AbABpAPsAIAAAAPoABAAAAEQAZQB2AGEAAQYAAABNAGEAbgBnAGEAbAD7ACIAAAD6AAQAAABUAGUAbAB1AAEHAAAARwBhAHUAdABhAG0AaQD7AB4AAAD6AAQAAABUAGEAbQBsAAEFAAAATABhAHQAaABhAPsANgAAAPoABAAAAFMAeQByAGMAAREAAABFAHMAdAByAGEAbgBnAGUAbABvACAARQBkAGUAcwBzAGEA+wAiAAAA+gAEAAAATwByAHkAYQABBwAAAEsAYQBsAGkAbgBnAGEA+wAiAAAA+gAEAAAATQBsAHkAbQABBwAAAEsAYQByAHQAaQBrAGEA+wAmAAAA+gAEAAAATABhAG8AbwABCQAAAEQAbwBrAEMAaABhAG0AcABhAPsALAAAAPoABAAAAFMAaQBuAGgAAQwAAABJAHMAawBvAG8AbABhACAAUABvAHQAYQD7ADIAAAD6AAQAAABNAG8AbgBnAAEPAAAATQBvAG4AZwBvAGwAaQBhAG4AIABCAGEAaQB0AGkA+wAeAAAA+gAEAAAAVgBpAGUAdAABBQAAAEEAcgBpAGEAbAD7ADQAAAD6AAQAAABVAGkAZwBoAAEQAAAATQBpAGMAcgBvAHMAbwBmAHQAIABVAGkAZwBoAHUAcgD7ACIAAAD6AAQAAABHAGUAbwByAAEHAAAAUwB5AGwAZgBhAGUAbgD7ATkFAAAAEQAAAPoDBQAAAEEAcgBpAGEAbAD7AREAAAD6AwUAAABBAHIAaQBhAGwA+wIRAAAA+gMFAAAAQQByAGkAYQBsAPsD8gQAAB4AAAAAJAAAAPoABAAAAEoAcABhAG4AAQgAAAAt/zP/IAAw/7QwtzDDMK8w+wAYAAAA+gAEAAAASABhAG4AZwABAgAAAHStvLn7ABgAAAD6AAQAAABIAGEAbgBzAAECAAAA0Z5TT/sAHgAAAPoABAAAAEgAYQBuAHQAAQUAAACuX9+OY2vRntSa+wAeAAAA+gAEAAAAQQByAGEAYgABBQAAAEEAcgBpAGEAbAD7AB4AAAD6AAQAAABIAGUAYgByAAEFAAAAQQByAGkAYQBsAPsAKAAAAPoABAAAAFQAaABhAGkAAQoAAABDAG8AcgBkAGkAYQAgAE4AZQB3APsAHgAAAPoABAAAAEUAdABoAGkAAQUAAABOAHkAYQBsAGEA+wAgAAAA+gAEAAAAQgBlAG4AZwABBgAAAFYAcgBpAG4AZABhAPsAIAAAAPoABAAAAEcAdQBqAHIAAQYAAABTAGgAcgB1AHQAaQD7ACQAAAD6AAQAAABLAGgAbQByAAEIAAAARABhAHUAbgBQAGUAbgBoAPsAHgAAAPoABAAAAEsAbgBkAGEAAQUAAABUAHUAbgBnAGEA+wAeAAAA+gAEAAAARwB1AHIAdQABBQAAAFIAYQBhAHYAaQD7ACQAAAD6AAQAAABDAGEAbgBzAAEIAAAARQB1AHAAaABlAG0AaQBhAPsAPAAAAPoABAAAAEMAaABlAHIAARQAAABQAGwAYQBuAHQAYQBnAGUAbgBlAHQAIABDAGgAZQByAG8AawBlAGUA+wA4AAAA+gAEAAAAWQBpAGkAaQABEgAAAE0AaQBjAHIAbwBzAG8AZgB0ACAAWQBpACAAQgBhAGkAdABpAPsAOAAAAPoABAAAAFQAaQBiAHQAARIAAABNAGkAYwByAG8AcwBvAGYAdAAgAEgAaQBtAGEAbABhAHkAYQD7ACIAAAD6AAQAAABUAGgAYQBhAAEHAAAATQBWACAAQgBvAGwAaQD7ACAAAAD6AAQAAABEAGUAdgBhAAEGAAAATQBhAG4AZwBhAGwA+wAiAAAA+gAEAAAAVABlAGwAdQABBwAAAEcAYQB1AHQAYQBtAGkA+wAeAAAA+gAEAAAAVABhAG0AbAABBQAAAEwAYQB0AGgAYQD7ADYAAAD6AAQAAABTAHkAcgBjAAERAAAARQBzAHQAcgBhAG4AZwBlAGwAbwAgAEUAZABlAHMAcwBhAPsAIgAAAPoABAAAAE8AcgB5AGEAAQcAAABLAGEAbABpAG4AZwBhAPsAIgAAAPoABAAAAE0AbAB5AG0AAQcAAABLAGEAcgB0AGkAawBhAPsAJgAAAPoABAAAAEwAYQBvAG8AAQkAAABEAG8AawBDAGgAYQBtAHAAYQD7ACwAAAD6AAQAAABTAGkAbgBoAAEMAAAASQBzAGsAbwBvAGwAYQAgAFAAbwB0AGEA+wAyAAAA+gAEAAAATQBvAG4AZwABDwAAAE0AbwBuAGcAbwBsAGkAYQBuACAAQgBhAGkAdABpAPsAHgAAAPoABAAAAFYAaQBlAHQAAQUAAABBAHIAaQBhAGwA+wA0AAAA+gAEAAAAVQBpAGcAaAABEAAAAE0AaQBjAHIAbwBzAG8AZgB0ACAAVQBpAGcAaAB1AHIA+wAiAAAA+gAEAAAARwBlAG8AcgABBwAAAFMAeQBsAGYAYQBlAG4A+wLkBgAA+gAGAAAATwBmAGYAaQBjAGUA+wCyAgAAAwAAAAATAAAAAw4AAAAACQAAAAMEAAAA+gAO+wBDAQAABD4BAAD6AQH7ACcBAAADAAAAAFwAAAD6AAAAAAD7AFAAAAADSwAAAPoADvsAQgAAAAIAAAABGAAAAPoABgAAAGEAOgB0AGkAbgB0AAFQwwAA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAHgkwQA+wBcAAAA+gC4iAAA+wBQAAAAA0sAAAD6AA77AEIAAAACAAAAARgAAAD6AAYAAABhADoAdABpAG4AdAABiJAAAPsBHAAAAPoACAAAAGEAOgBzAGEAdABNAG8AZAAB4JMEAPsAXAAAAPoAoIYBAPsAUAAAAANLAAAA+gAO+wBCAAAAAgAAAAEYAAAA+gAGAAAAYQA6AHQAaQBuAHQAAZg6AAD7ARwAAAD6AAgAAABhADoAcwBhAHQATQBvAGQAATBXBQD7AQkAAAD6AEAx9wABAfsASQEAAAREAQAA+gEB+wAtAQAAAwAAAABeAAAA+gAAAAAA+wBSAAAAA00AAAD6AA77AEQAAAACAAAAARoAAAD6AAcAAABhADoAcwBoAGEAZABlAAE4xwAA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAHQ+wEA+wBeAAAA+gCAOAEA+wBSAAAAA00AAAD6AA77AEQAAAACAAAAARoAAAD6AAcAAABhADoAcwBoAGEAZABlAAFIawEA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAHQ+wEA+wBeAAAA+gCghgEA+wBSAAAAA00AAAD6AA77AEQAAAACAAAAARoAAAD6AAcAAABhADoAcwBoAGEAZABlAAEwbwEA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAFYDwIA+wEJAAAA+gBAMfcAAQD7AQoBAAADAAAAAIMAAAD6AAABAAIBAzUlAAD7AFwAAAADVwAAAABSAAAAA00AAAD6AA77AEQAAAACAAAAARoAAAD6AAcAAABhADoAcwBoAGEAZABlAAEYcwEA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAEomgEA+wEEAAAA+gAG+wIHAAAA+gAAAAAA+wA6AAAA+gAAAQACAQM4YwAA+wATAAAAAw4AAAAACQAAAAMEAAAA+gAO+wEEAAAA+gAG+wIHAAAA+gAAAAAA+wA6AAAA+gAAAQACAQPUlAAA+wATAAAAAw4AAAAACQAAAAMEAAAA+gAO+wEEAAAA+gAG+wIHAAAA+gAAAAAA+wITAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAPuAgAAAwAAAAATAAAAAw4AAAAACQAAAAMEAAAA+gAO+wCmAQAABKEBAAD6AQH7AEgBAAADAAAAAFwAAAD6AAAAAAD7AFAAAAADSwAAAPoADvsAQgAAAAIAAAABGAAAAPoABgAAAGEAOgB0AGkAbgB0AAFAnAAA+wEcAAAA+gAIAAAAYQA6AHMAYQB0AE0AbwBkAAEwVwUA+wB7AAAA+gBAnAAA+wBvAAAAA2oAAAD6AA77AGEAAAADAAAAARgAAAD6AAYAAABhADoAdABpAG4AdAAByK8AAPsBGgAAAPoABwAAAGEAOgBzAGgAYQBkAGUAAbiCAQD7ARwAAAD6AAgAAABhADoAcwBhAHQATQBvAGQAATBXBQD7AF4AAAD6AKCGAQD7AFIAAAADTQAAAPoADvsARAAAAAIAAAABGgAAAPoABwAAAGEAOgBzAGgAYQBkAGUAASBOAAD7ARwAAAD6AAgAAABhADoAcwBhAHQATQBvAGQAARjkAwD7AksAAAD6AAD7AEIAAAD6AAUAAAA1ADAAMAAwADAAAQYAAAAtADgAMAAwADAAMAACBQAAADUAMAAwADAAMAADBgAAADEAOAAwADAAMAAwAPsAIgEAAAQdAQAA+gEB+wDIAAAAAgAAAABcAAAA+gAAAAAA+wBQAAAAA0sAAAD6AA77AEIAAAACAAAAARgAAAD6AAYAAABhADoAdABpAG4AdAABgDgBAPsBHAAAAPoACAAAAGEAOgBzAGEAdABNAG8AZAAB4JMEAPsAXgAAAPoAoIYBAPsAUgAAAANNAAAA+gAO+wBEAAAAAgAAAAEaAAAA+gAHAAAAYQA6AHMAaABhAGQAZQABMHUAAPsBHAAAAPoACAAAAGEAOgBzAGEAdABNAG8AZAABQA0DAPsCRwAAAPoAAPsAPgAAAPoABQAAADUAMAAwADAAMAABBQAAADUAMAAwADAAMAACBQAAADUAMAAwADAAMAADBQAAADUAMAAwADAAMAD7BAQAAAAAAAAA";
            break;
        }
      }
      t._OfflineAppDocumentEndLoad('', doc);
    })
    .push(undefined, function (error) {
      console.log(error);
    });
};

AscCommon.baseEditorsApi.prototype.jio_save = function () {
  var t = this,
    g = Common.Gateway,
    result = {},
    data = t.asc_nativeGetFile();
  if (g.props.save_defer) {
    // if we are run from getContent
    result[g.props.key] = data;
    g.props.save_defer.resolve(result);
    g.props.save_defer = null;
  } else {
    // TODO: rewrite to put_attachment
    return g.jio_putAttachment('/', 'body.txt', data)
      .push(undefined, function (error) {
        console.log(error);
      });
  }
};

AscCommon.loadSdk = function (sdkName, callback) {
  var queue,
    list_files;
  function loadScript(src) {
    return new RSVP.Promise(function (resolve, reject) {
      var s;
      s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = reject;
      document.head.appendChild(s);
    });
  }
  if (window['AscNotLoadAllScript']) {
    callback();
  } else {
    queue = new RSVP.Queue();

    switch (sdkName) {
      case 'word':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../word/Editor/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/Format/Constants.js",
          "../common/Drawings/CommonController.js",
          "../word/Editor/GraphicObjects/DrawingStates.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",
          "../common/Scrolls/iscroll.js",

          "../common/wordcopypaste.js",

          "../cell/utils/utils.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",

          "../word/Drawing/translations.js",
          "../word/Editor/GraphicObjects/Format/ShapePrototype.js",
          "../word/Editor/GraphicObjects/Format/ImagePrototype.js",
          "../word/Editor/GraphicObjects/Format/GroupPrototype.js",
          "../word/Editor/GraphicObjects/Format/ChartSpacePrototype.js",
          "../word/Editor/GraphicObjects/GraphicObjects.js",
          "../word/Editor/GraphicObjects/GraphicPage.js",
          "../word/Editor/GraphicObjects/WrapManager.js",
          "../word/Editor/Comments.js",
          "../word/Editor/Styles.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/Field.js",
          "../word/Editor/Run.js",
          "../word/Editor/Math.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/Sections.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/Common.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/Search.js",
          "../word/Editor/FontClassification.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootEndNote.js",

          "../word/Drawing/Graphics.js",
          "../word/Drawing/ShapeDrawer.js",

          "../word/Drawing/DrawingDocument.js",
          "../word/Drawing/GraphicsEvents.js",
          "../word/Drawing/Rulers.js",
          "../word/Drawing/HtmlPage.js",
          "../word/Drawing/documentrenderer.js",
          "../word/apiCommon.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",

          "../word/apiBuilder.js",

          "../common/clipboard_base.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../word/Local/api_jio.js"
        ];
        break;
      case 'cell':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../cell/model/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/Format/Constants.js",
          "../common/Drawings/CommonController.js",
          "../common/Drawings/States.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/CollaborativeEditingBase.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",
          "../cell/view/iscroll.js",

          "../common/wordcopypaste.js",

          "../cell/model/UndoRedo.js",
          "../cell/model/clipboard.js",
          "../cell/model/autofilters.js",
          "../cell/graphics/DrawingContext.js",
          "../cell/graphics/pdfprinter.js",
          "../cell/model/ConditionalFormatting.js",
          "../cell/model/FormulaObjects/parserFormula.js",
          "../cell/model/FormulaObjects/_xlfnFunctions.js",
          "../cell/model/FormulaObjects/dateandtimeFunctions.js",
          "../cell/model/FormulaObjects/engineeringFunctions.js",
          "../cell/model/FormulaObjects/cubeFunctions.js",
          "../cell/model/FormulaObjects/databaseFunctions.js",
          "../cell/model/FormulaObjects/textanddataFunctions.js",
          "../cell/model/FormulaObjects/statisticalFunctions.js",
          "../cell/model/FormulaObjects/financialFunctions.js",
          "../cell/model/FormulaObjects/mathematicFunctions.js",
          "../cell/model/FormulaObjects/lookupandreferenceFunctions.js",
          "../cell/model/FormulaObjects/informationFunctions.js",
          "../cell/model/FormulaObjects/logicalFunctions.js",
          "../cell/model/CellComment.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",
          "../cell/view/mobileTouch.js",
          "../cell/view/StringRender.js",
          "../cell/view/CellTextRender.js",
          "../cell/view/CellEditorView.js",
          "../cell/view/EventsController.js",
          "../cell/view/WorkbookView.js",
          "../cell/view/WorksheetView.js",
          "../cell/view/DrawingObjectsController.js",
          "../cell/model/DrawingObjects/Graphics.js",
          "../cell/model/DrawingObjects/ShapeDrawer.js",
          "../cell/model/DrawingObjects/DrawingDocument.js",
          "../cell/model/DrawingObjects/GlobalCounters.js",
          "../cell/model/DrawingObjects/Format/ShapePrototype.js",
          "../cell/model/DrawingObjects/Format/ImagePrototype.js",
          "../cell/model/DrawingObjects/Format/GroupPrototype.js",
          "../cell/model/DrawingObjects/Format/ChartSpacePrototype.js",

          "../word/Editor/Comments.js",
          "../word/Editor/Styles.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/Field.js",
          "../word/Editor/Run.js",
          "../word/Editor/Math.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/Sections.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/FontClassification.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootEndNote.js",
          "../word/Editor/GraphicObjects/WrapManager.js",
          "../word/Editor/Common.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",
          "../word/apiCommon.js",

          "../cell/apiBuilder.js",

          "../common/clipboard_base.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../cell/Local/api_jio.js"
        ];
        break;
      case 'slide':
        list_files = [
          "../common/downloaderfiles.js",
          "../common/NumFormat.js",
          "../common/SerializeChart.js",

          "../common/FontsFreeType/font_engine.js",
          "../common/FontsFreeType/FontFile.js",
          "../common/FontsFreeType/font_map.js",
          "../common/FontsFreeType/FontManager.js",

          "../common/Drawings/Metafile.js",
          "../common/FontsFreeType/TextMeasurer.js",
          "../common/Drawings/WorkEvents.js",

          "../word/Editor/History.js",

          "../common/Shapes/EditorSettings.js",
          "../common/Shapes/Serialize.js",
          "../common/Shapes/SerializeWriter.js",

          "../common/Drawings/Hit.js",
          "../common/Drawings/ArcTo.js",
          "../common/Drawings/ColorArray.js",

          "../common/Drawings/Format/Constants.js",
          "../common/Drawings/CommonController.js",
          "../common/Drawings/States.js",
          "../common/Drawings/Format/CreateGeometry.js",
          "../common/Drawings/Format/Geometry.js",
          "../common/Drawings/Format/Format.js",
          "../common/Drawings/Format/GraphicObjectBase.js",
          "../common/Drawings/Format/Shape.js",
          "../slide/Editor/Format/ShapePrototype.js",
          "../common/Drawings/Format/Path.js",
          "../common/Drawings/Format/Image.js",
          "../common/Drawings/Format/GroupShape.js",
          "../common/Drawings/Format/ChartSpace.js",
          "../common/Drawings/Format/ChartFormat.js",
          "../common/Drawings/Format/TextBody.js",
          "../slide/Editor/Format/TextBodyPrototype.js",
          "../common/Drawings/Format/GraphicFrame.js",
          "../common/Charts/charts.js",
          "../common/Charts/DrawingArea.js",
          "../common/Charts/DrawingObjects.js",
          "../common/Charts/3DTransformation.js",
          "../common/Charts/ChartsDrawer.js",
          "../common/Drawings/TrackObjects/AdjustmentTracks.js",
          "../common/Drawings/TrackObjects/MoveTracks.js",
          "../common/Drawings/TrackObjects/NewShapeTracks.js",
          "../common/Drawings/TrackObjects/PolyLine.js",
          "../common/Drawings/TrackObjects/ResizeTracks.js",
          "../common/Drawings/TrackObjects/RotateTracks.js",
          "../common/Drawings/TrackObjects/Spline.js",
          "../common/Drawings/DrawingObjectsHandlers.js",
          "../common/Drawings/TextDrawer.js",

          "../common/Drawings/Externals.js",
          "../common/GlobalLoaders.js",
          "../common/Controls.js",
          "../common/Overlay.js",
          "../common/Drawings/HatchPattern.js",

          "../common/scroll.js",

          "../common/wordcopypaste.js",

          "../slide/themes/Themes.js",

          "../cell/utils/utils.js",
          "../cell/model/WorkbookElems.js",
          "../cell/model/Workbook.js",
          "../cell/model/Serialize.js",
          "../cell/model/CellInfo.js",
          "../cell/view/DrawingObjectsController.js",

          "../slide/Drawing/ThemeLoader.js",
          "../word/Editor/Serialize2.js",
          "../word/Editor/Styles.js",
          "../slide/Editor/Format/StylesPrototype.js",
          "../word/Editor/Numbering.js",
          "../word/Drawing/GraphicsEvents.js",
          "../word/Drawing/Rulers.js",
          "../word/Editor/Table.js",
          "../word/Editor/Table/TableRecalculate.js",
          "../word/Editor/Table/TableDraw.js",
          "../word/Editor/Table/TableRow.js",
          "../word/Editor/Table/TableCell.js",
          "../word/Editor/Common.js",
          "../word/Editor/Sections.js",

          "../word/Drawing/Graphics.js",
          "../word/Drawing/ShapeDrawer.js",

          "../slide/Drawing/Transitions.js",
          "../slide/Drawing/DrawingDocument.js",
          "../slide/Drawing/HtmlPage.js",
          "../slide/Editor/Format/Presentation.js",
          "../slide/Editor/DrawingObjectsController.js",
          "../slide/Editor/Format/Slide.js",
          "../slide/Editor/Format/SlideMaster.js",
          "../slide/Editor/Format/Layout.js",
          "../slide/Editor/Format/Comments.js",
          "../word/Editor/Styles.js",
          "../word/Editor/Numbering.js",
          "../word/Editor/ParagraphContent.js",
          "../word/Editor/ParagraphContentBase.js",
          "../word/Editor/Hyperlink.js",
          "../word/Editor/Field.js",
          "../word/Editor/Run.js",
          "../word/Math/mathTypes.js",
          "../word/Math/mathText.js",
          "../word/Math/mathContent.js",
          "../word/Math/base.js",
          "../word/Math/fraction.js",
          "../word/Math/degree.js",
          "../word/Math/matrix.js",
          "../word/Math/limit.js",
          "../word/Math/nary.js",
          "../word/Math/radical.js",
          "../word/Math/operators.js",
          "../word/Math/accent.js",
          "../word/Math/borderBox.js",
          "../word/Editor/FlowObjects.js",
          "../word/Editor/Paragraph.js",
          "../word/Editor/Paragraph_Recalculate.js",
          "../word/Editor/DocumentContentBase.js",
          "../word/Editor/Document.js",
          "../word/Editor/DocumentContent.js",
          "../word/Editor/DocumentControllerBase.js",
          "../word/Editor/HeaderFooter.js",
          "../word/Editor/Math.js",
          "../word/Editor/Spelling.js",
          "../word/Editor/Footnotes.js",
          "../word/Editor/FootEndNote.js",
          "../word/Editor/Search.js",
          "../word/Editor/FontClassification.js",

          "../slide/Editor/Format/ImagePrototype.js",
          "../slide/Editor/Format/GroupPrototype.js",
          "../slide/Editor/Format/ChartSpacePrototype.js",
          "../slide/apiCommon.js",
          "../word/apiCommon.js",

          "../common/clipboard_base.js",
          "../common/Drawings/Format/OleObject.js",
          "../common/plugins.js",
          "../common/Local/common_jio.js",
          "../slide/Local/api_jio.js"
        ];
        break;
    }

    list_files.forEach(function (url) {
      url = url.replace('../', './sdkjs/');
      queue.push(function () {
        return loadScript(url);
      });
    });
    queue.push(callback);
  }
};