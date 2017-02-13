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

(function(window) {
  'use strict';

  // Класс надстройка, для online и offline работы
  var CSpellCheckApi = function(options) {
    this._SpellCheckApi = new SpellCheckApi();
    this._onlineWork = false;

    if (options) {
      this.onDisconnect = options.onDisconnect;
      this.onSpellCheck = options.onSpellCheck;
    }
  };

  CSpellCheckApi.prototype.init = function(docid) {
    if (this._SpellCheckApi && this._SpellCheckApi.isRightURL()) {
      var t = this;
      this._SpellCheckApi.onDisconnect = function(e, isDisconnectAtAll, isCloseCoAuthoring) {
        t.callback_OnDisconnect(e, isDisconnectAtAll, isCloseCoAuthoring);
      };
      this._SpellCheckApi.onSpellCheck = function(e) {
        t.callback_OnSpellCheck(e);
      };

      this._SpellCheckApi.init(docid);
      this._onlineWork = true;
    }
  };

  CSpellCheckApi.prototype.set_url = function(url) {
    if (this._SpellCheckApi) {
      this._SpellCheckApi.set_url(url);
    }
  };

  CSpellCheckApi.prototype.get_state = function() {
    if (this._SpellCheckApi) {
      return this._SpellCheckApi.get_state();
    }

    return 0;
  };

  CSpellCheckApi.prototype.disconnect = function() {
    if (this._SpellCheckApi && this._onlineWork) {
      this._SpellCheckApi.disconnect();
    }
  };

  CSpellCheckApi.prototype.spellCheck = function(spellCheckData) {
    if (this._SpellCheckApi && this._onlineWork) {
      this._SpellCheckApi.spellCheck(spellCheckData);
    }
  };

  CSpellCheckApi.prototype.callback_OnSpellCheck = function(e) {
    if (this.onSpellCheck) {
      return this.onSpellCheck(e);
    }
  };

  /**
   * Event об отсоединении от сервера
   * @param {jQuery} e  event об отсоединении с причиной
   * @param {Bool} isDisconnectAtAll  окончательно ли отсоединяемся(true) или будем пробовать сделать reconnect(false) + сами отключились
   */
  CSpellCheckApi.prototype.callback_OnDisconnect = function(e, isDisconnectAtAll, isCloseCoAuthoring) {
    if (this.onDisconnect) {
      return this.onDisconnect(e, isDisconnectAtAll, isCloseCoAuthoring);
    }
  };

  /** States
   * -1 - reconnect state
   *  0 - not initialized
   *  1 - opened
   *  3 - closed
   */
  var SpellCheckApi = function(options) {
    if (options) {
      this.onDisconnect = options.onDisconnect;
      this.onConnect = options.onConnect;
      this.onSpellCheck = options.onSpellCheck;
    }
    this._state = 0;
    // Мы сами отключились от совместного редактирования
    this.isCloseCoAuthoring = false;

    // Массив данных, который стоит отправить как только подключимся
    this.dataNeedSend = [];

    this._url = "";
  };

  SpellCheckApi.prototype.isRightURL = function() {
    return ("" != this._url);
  };

  SpellCheckApi.prototype.set_url = function(url) {
    this._url = url;
  };

  SpellCheckApi.prototype.get_state = function() {
    return this._state;
  };

  SpellCheckApi.prototype.spellCheck = function(spellCheckData) {
    this._send({"type": "spellCheck", "spellCheckData": spellCheckData});
  };

  SpellCheckApi.prototype.disconnect = function() {
    // Отключаемся сами
    this.isCloseCoAuthoring = true;
    return this.sockjs.close();
  };

  SpellCheckApi.prototype._send = function(data) {
    if (data !== null && typeof data === "object") {
      if (this._state > 0) {
        this.sockjs.send(JSON.stringify(data));
      } else {
        this.dataNeedSend.push(data);
      }
    }
  };

  SpellCheckApi.prototype._sendAfterConnect = function() {
    var data;
    while (this._state > 0 && undefined !== (data = this.dataNeedSend.shift()))
      this._send(data);
  };

  SpellCheckApi.prototype._onSpellCheck = function(data) {
    if (undefined !== data["spellCheckData"] && this.onSpellCheck) {
      this.onSpellCheck(data["spellCheckData"]);
    }
  };

  var reconnectTimeout, attemptCount = 0;

  function initSocksJs(url, docsCoApi) {
    var sockjs = new (_getSockJs())(url, null, {debug: true});

    sockjs.onopen = function() {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        attemptCount = 0;
      }
      docsCoApi._state = 1; // Opened state
      if (docsCoApi.onConnect) {
        docsCoApi.onConnect();
      }

      // Отправляем все данные, которые пришли до соединения с сервером
      docsCoApi._sendAfterConnect();
    };

    sockjs.onmessage = function(e) {
      //TODO: add checks and error handling
      //Get data type
      var dataObject = JSON.parse(e.data);
      var type = dataObject.type;
      switch (type) {
        case 'spellCheck'  :
          docsCoApi._onSpellCheck(dataObject);
          break;
      }
    };
    sockjs.onclose = function(evt) {
      docsCoApi._state = -1; // Reconnect state
      var bIsDisconnectAtAll = attemptCount >= 20 || docsCoApi.isCloseCoAuthoring;
      if (bIsDisconnectAtAll) {
        docsCoApi._state = 3;
      } // Closed state
      if (docsCoApi.onDisconnect) {
        docsCoApi.onDisconnect(evt.reason, bIsDisconnectAtAll, docsCoApi.isCloseCoAuthoring);
      }
      if (docsCoApi.isCloseCoAuthoring) {
        return;
      }
      //Try reconect
      if (attemptCount < 20) {
        tryReconnect();
      }
    };

    function tryReconnect() {
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
      attemptCount++;
      reconnectTimeout = setTimeout(function() {
        delete docsCoApi.sockjs;
        docsCoApi.sockjs = initSocksJs(url, docsCoApi);
      }, 500 * attemptCount);

    }

    return sockjs;
  }

  function _getSockJs() {
    return window['SockJS'] ? window['SockJS'] : require('sockjs');
  }

  SpellCheckApi.prototype.init = function(docid) {
    this._docid = docid;
    //Begin send auth
    this.sockjs_url = this._url + '/doc/' + docid + '/c';
    this.sockjs = initSocksJs(this.sockjs_url, this);
  };

  //-----------------------------------------------------------export---------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window["AscCommon"].CSpellCheckApi = CSpellCheckApi;
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
var g_spellCheckLanguages = [];
//{ "ar", 0x0001 },
//{ "bg", 0x0002 },
//{ "ca", 0x0003 },
//{ "zh-Hans", 0x0004 },
//{ "cs", 0x0005 },
//{ "da", 0x0006 },
//{ "de", 0x0007 },
//{ "el", 0x0008 },
//{ "en", 0x0009 },
//{ "es", 0x000a },
//{ "fi", 0x000b },
//{ "fr", 0x000c },
//{ "he", 0x000d },
//{ "hu", 0x000e },
//{ "is", 0x000f },
//{ "it", 0x0010 },
//{ "ja", 0x0011 },
//{ "ko", 0x0012 },
//{ "nl", 0x0013 },
//{ "no", 0x0014 },
//{ "pl", 0x0015 },
//{ "pt", 0x0016 },
//{ "rm", 0x0017 },
//{ "ro", 0x0018 },
//{ "ru", 0x0019 },
//{ "hr", 0x001a },
//{ "sk", 0x001b },
//{ "sq", 0x001c },
//{ "sv", 0x001d },
//{ "th", 0x001e },
//{ "tr", 0x001f },
//{ "ur", 0x0020 },
//{ "id", 0x0021 },
//{ "uk", 0x0022 },
//{ "be", 0x0023 },
//{ "sl", 0x0024 },
//{ "et", 0x0025 },
//{ "lv", 0x0026 },
//{ "lt", 0x0027 },
//{ "tg", 0x0028 },
//{ "fa", 0x0029 },
//{ "vi", 0x002a },
//{ "hy", 0x002b },
//{ "az", 0x002c },
//{ "eu", 0x002d },
//{ "hsb", 0x002e },
//{ "mk", 0x002f },
//{ "tn", 0x0032 },
//{ "xh", 0x0034 },
//{ "zu", 0x0035 },
//{ "af", 0x0036 },
//{ "ka", 0x0037 },
//{ "fo", 0x0038 },
//{ "hi", 0x0039 },
//{ "mt", 0x003a },
//{ "se", 0x003b },
//{ "ga", 0x003c },
//{ "ms", 0x003e },
//{ "kk", 0x003f },
//{ "ky", 0x0040 },
//{ "sw", 0x0041 },
//{ "tk", 0x0042 },
//{ "uz", 0x0043 },
//{ "tt", 0x0044 },
//{ "bn", 0x0045 },
//{ "pa", 0x0046 },
//{ "gu", 0x0047 },
//{ "or", 0x0048 },
//{ "ta", 0x0049 },
//{ "te", 0x004a },
//{ "kn", 0x004b },
//{ "ml", 0x004c },
//{ "as", 0x004d },
//{ "mr", 0x004e },
//{ "sa", 0x004f },
//{ "mn", 0x0050 },
//{ "bo", 0x0051 },
//{ "cy", 0x0052 },
//{ "km", 0x0053 },
//{ "lo", 0x0054 },
//{ "gl", 0x0056 },
//{ "kok", 0x0057 },
//{ "syr", 0x005a },
//{ "si", 0x005b },
//{ "iu", 0x005d },
//{ "am", 0x005e },
//{ "tzm", 0x005f },
//{ "ne", 0x0061 },
//{ "fy", 0x0062 },
//{ "ps", 0x0063 },
//{ "fil", 0x0064 },
//{ "dv", 0x0065 },
//{ "ha", 0x0068 },
//{ "yo", 0x006a },
//{ "quz", 0x006b },
//{ "nso", 0x006c },
//{ "ba", 0x006d },
//{ "lb", 0x006e },
//{ "kl", 0x006f },
//{ "ig", 0x0070 },
//{ "ii", 0x0078 },
//{ "arn", 0x007a },
//{ "moh", 0x007c },
//{ "br", 0x007e },
//{ "ug", 0x0080 },
//{ "mi", 0x0081 },
//{ "oc", 0x0082 },
//{ "co", 0x0083 },
//{ "gsw", 0x0084 },
//{ "sah", 0x0085 },
//{ "qut", 0x0086 },
//{ "rw", 0x0087 },
//{ "wo", 0x0088 },
//{ "prs", 0x008c },
//{ "gd", 0x0091 },
//{ "ar-SA", 0x0401 },
//{ "bg-BG", 0x0402 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ca-ES", 0x0403));
//{ "zh-TW", 0x0404 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("cs-CZ", 0x0405));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("da-DK", 0x0406));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-DE", 0x0407));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("el-GR", 0x0408));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-US", 0x0409));
//{ "es-ES_tradnl", 0x040a },
//{ "fi-FI", 0x040b },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("fr-FR", 0x040c));
//{ "he-IL", 0x040d },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("hu-HU", 0x040e));
//{ "is-IS", 0x040f },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("it-IT", 0x0410));
//{ "ja-JP", 0x0411 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ko-KR", 0x0412));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nl-NL", 0x0413));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nb-NO", 0x0414));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pl-PL", 0x0415));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pt-BR", 0x0416));
//{ "rm-CH", 0x0417 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ro-RO", 0x0418));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("ru-RU", 0x0419));
//{ "hr-HR", 0x041a },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sk-SK", 0x041b));
//{ "sq-AL", 0x041c },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("sv-SE", 0x041d));
//{ "th-TH", 0x041e },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("tr-TR", 0x041f));
//{ "ur-PK", 0x0420 },
//{ "id-ID", 0x0421 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("uk-UA", 0x0422));
//{ "be-BY", 0x0423 },
//{ "sl-SI", 0x0424 },
//{ "et-EE", 0x0425 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("lv-LV", 0x0426));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("lt-LT", 0x0427));
//{ "tg-Cyrl-TJ", 0x0428 },
//{ "fa-IR", 0x0429 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("vi-VN", 0x042a));
//{ "hy-AM", 0x042b },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("az-Latn-AZ", 0x042c));
//{ "eu-ES", 0x042d },
//{ "wen-DE", 0x042e },
//{ "mk-MK", 0x042f },
//{ "st-ZA", 0x0430 },
//{ "ts-ZA", 0x0431 },
//{ "tn-ZA", 0x0432 },
//{ "ven-ZA", 0x0433 },
//{ "xh-ZA", 0x0434 },
//{ "zu-ZA", 0x0435 },
//{ "af-ZA", 0x0436 },
//{ "ka-GE", 0x0437 },
//{ "fo-FO", 0x0438 },
//{ "hi-IN", 0x0439 },
//{ "mt-MT", 0x043a },
//{ "se-NO", 0x043b },
//{ "ms-MY", 0x043e },
//{ "kk-KZ", 0x043f },
//{ "ky-KG", 0x0440 },
//{ "sw-KE", 0x0441 },
//{ "tk-TM", 0x0442 },
//{ "uz-Latn-UZ", 0x0443 },
//{ "tt-RU", 0x0444 },
//{ "bn-IN", 0x0445 },
//{ "pa-IN", 0x0446 },
//{ "gu-IN", 0x0447 },
//{ "or-IN", 0x0448 },
//{ "ta-IN", 0x0449 },
//{ "te-IN", 0x044a },
//{ "kn-IN", 0x044b },
//{ "ml-IN", 0x044c },
//{ "as-IN", 0x044d },
//{ "mr-IN", 0x044e },
//{ "sa-IN", 0x044f },
//{ "mn-MN", 0x0450 },
//{ "bo-CN", 0x0451 },
//{ "cy-GB", 0x0452 },
//{ "km-KH", 0x0453 },
//{ "lo-LA", 0x0454 },
//{ "my-MM", 0x0455 },
//{ "gl-ES", 0x0456 },
//{ "kok-IN", 0x0457 },
//{ "mni", 0x0458 },
//{ "sd-IN", 0x0459 },
//{ "syr-SY", 0x045a },
//{ "si-LK", 0x045b },
//{ "chr-US", 0x045c },
//{ "iu-Cans-CA", 0x045d },
//{ "am-ET", 0x045e },
//{ "tmz", 0x045f },
//{ "ne-NP", 0x0461 },
//{ "fy-NL", 0x0462 },
//{ "ps-AF", 0x0463 },
//{ "fil-PH", 0x0464 },
//{ "dv-MV", 0x0465 },
//{ "bin-NG", 0x0466 },
//{ "fuv-NG", 0x0467 },
//{ "ha-Latn-NG", 0x0468 },
//{ "ibb-NG", 0x0469 },
//{ "yo-NG", 0x046a },
//{ "quz-BO", 0x046b },
//{ "nso-ZA", 0x046c },
//{ "ba-RU", 0x046d },
//{ "lb-LU", 0x046e },
//{ "kl-GL", 0x046f },
//{ "ig-NG", 0x0470 },
//{ "kr-NG", 0x0471 },
//{ "gaz-ET", 0x0472 },
//{ "ti-ER", 0x0473 },
//{ "gn-PY", 0x0474 },
//{ "haw-US", 0x0475 },
//{ "so-SO", 0x0477 },
//{ "ii-CN", 0x0478 },
//{ "pap-AN", 0x0479 },
//{ "arn-CL", 0x047a },
//{ "moh-CA", 0x047c },
//{ "br-FR", 0x047e },
//{ "ug-CN", 0x0480 },
//{ "mi-NZ", 0x0481 },
//{ "oc-FR", 0x0482 },
//{ "co-FR", 0x0483 },
//{ "gsw-FR", 0x0484 },
//{ "sah-RU", 0x0485 },
//{ "qut-GT", 0x0486 },
//{ "rw-RW", 0x0487 },
//{ "wo-SN", 0x0488 },
//{ "prs-AF", 0x048c },
//{ "plt-MG", 0x048d },
//{ "gd-GB", 0x0491 },
//{ "ar-IQ", 0x0801 },
//{ "zh-CN", 0x0804 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-CH", 0x0807));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-GB", 0x0809));
//{ "es-MX", 0x080a },
//{ "fr-BE", 0x080c },
//{ "it-CH", 0x0810 },
//{ "nl-BE", 0x0813 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("nn-NO", 0x0814));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("pt-PT", 0x0816));
//{ "ro-MO", 0x0818 },
//{ "ru-MO", 0x0819 },
//{ "sr-Latn-CS", 0x081a },
//{ "sv-FI", 0x081d },
//{ "ur-IN", 0x0820 },
//{ "az-Cyrl-AZ", 0x082c },
//{ "dsb-DE", 0x082e },
//{ "se-SE", 0x083b },
//{ "ga-IE", 0x083c },
//{ "ms-BN", 0x083e },
//{ "uz-Cyrl-UZ", 0x0843 },
//{ "bn-BD", 0x0845 },
//{ "pa-PK", 0x0846 },
//{ "mn-Mong-CN", 0x0850 },
//{ "bo-BT", 0x0851 },
//{ "sd-PK", 0x0859 },
//{ "iu-Latn-CA", 0x085d },
//{ "tzm-Latn-DZ", 0x085f },
//{ "ne-IN", 0x0861 },
//{ "quz-EC", 0x086b },
//{ "ti-ET", 0x0873 },
//{ "ar-EG", 0x0c01 },
//{ "zh-HK", 0x0c04 },
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("de-AT", 0x0c07));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("en-AU", 0x0c09));
g_spellCheckLanguages.push(new AscCommon.asc_CLanguage("es-ES", 0x0c0a));
//{ "fr-CA", 0x0c0c },
//{ "sr-Cyrl-CS", 0x0c1a },
//{ "se-FI", 0x0c3b },
//{ "tmz-MA", 0x0c5f },
//{ "quz-PE", 0x0c6b },
//{ "ar-LY", 0x1001 },
//{ "zh-SG", 0x1004 },
//{ "de-LU", 0x1007 },
//{ "en-CA", 0x1009 },
//{ "es-GT", 0x100a },
//{ "fr-CH", 0x100c },
//{ "hr-BA", 0x101a },
//{ "smj-NO", 0x103b },
//{ "ar-DZ", 0x1401 },
//{ "zh-MO", 0x1404 },
//{ "de-LI", 0x1407 },
//{ "en-NZ", 0x1409 },
//{ "es-CR", 0x140a },
//{ "fr-LU", 0x140c },
//{ "bs-Latn-BA", 0x141a },
//{ "smj-SE", 0x143b },
//{ "ar-MA", 0x1801 },
//{ "en-IE", 0x1809 },
//{ "es-PA", 0x180a },
//{ "fr-MC", 0x180c },
//{ "sr-Latn-BA", 0x181a },
//{ "sma-NO", 0x183b },
//{ "ar-TN", 0x1c01 },
//{ "en-ZA", 0x1c09 },
//{ "es-DO", 0x1c0a },
//{ "fr-West", 0x1c0c },
//{ "sr-Cyrl-BA", 0x1c1a },
//{ "sma-SE", 0x1c3b },
//{ "ar-OM", 0x2001 },
//{ "en-JM", 0x2009 },
//{ "es-VE", 0x200a },
//{ "fr-RE", 0x200c },
//{ "bs-Cyrl-BA", 0x201a },
//{ "sms-FI", 0x203b },
//{ "ar-YE", 0x2401 },
//{ "en-CB", 0x2409 },
//{ "es-CO", 0x240a },
//{ "fr-CG", 0x240c },
//{ "sr-Latn-RS", 0x241a },
//{ "smn-FI", 0x243b },
//{ "ar-SY", 0x2801 },
//{ "en-BZ", 0x2809 },
//{ "es-PE", 0x280a },
//{ "fr-SN", 0x280c },
//{ "sr-Cyrl-RS", 0x281a },
//{ "ar-JO", 0x2c01 },
//{ "en-TT", 0x2c09 },
//{ "es-AR", 0x2c0a },
//{ "fr-CM", 0x2c0c },
//{ "sr-Latn-ME", 0x2c1a },
//{ "ar-LB", 0x3001 },
//{ "en-ZW", 0x3009 },
//{ "es-EC", 0x300a },
//{ "fr-CI", 0x300c },
//{ "sr-Cyrl-ME", 0x301a },
//{ "ar-KW", 0x3401 },
//{ "en-PH", 0x3409 },
//{ "es-CL", 0x340a },
//{ "fr-ML", 0x340c },
//{ "ar-AE", 0x3801 },
//{ "en-ID", 0x3809 },
//{ "es-UY", 0x380a },
//{ "fr-MA", 0x380c },
//{ "ar-BH", 0x3c01 },
//{ "en-HK", 0x3c09 },
//{ "es-PY", 0x3c0a },
//{ "fr-HT", 0x3c0c },
//{ "ar-QA", 0x4001 },
//{ "en-IN", 0x4009 },
//{ "es-BO", 0x400a },
//{ "en-MY", 0x4409 },
//{ "es-SV", 0x440a },
//{ "en-SG", 0x4809 },
//{ "es-HN", 0x480a },
//{ "es-NI", 0x4c0a },
//{ "es-PR", 0x500a },
//{ "es-US", 0x540a },
//{ "bs-Cyrl", 0x641a },
//{ "bs-Latn", 0x681a },
//{ "sr-Cyrl", 0x6c1a },
//{ "sr-Latn", 0x701a },
//{ "smn", 0x703b },
//{ "az-Cyrl", 0x742c },
//{ "sms", 0x743b },
//{ "zh", 0x7804 },
//{ "nn", 0x7814 },
//{ "bs", 0x781a },
//{ "az-Latn", 0x782c },
//{ "sma", 0x783b },
//{ "uz-Cyrl", 0x7843 },
//{ "mn-Cyrl", 0x7850 },
//{ "iu-Cans", 0x785d },
//{ "zh-Hant", 0x7c04 },
//{ "nb", 0x7c14 },
//{ "sr", 0x7c1a },
//{ "tg-Cyrl", 0x7c28 },
//{ "dsb", 0x7c2e },
//{ "smj", 0x7c3b },
//{ "uz-Latn", 0x7c43 },
//{ "mn-Mong", 0x7c50 },
//{ "iu-Latn", 0x7c5d },
//{ "tzm-Latn", 0x7c5f },
//{ "ha-Latn", 0x7c68 },

  //-----------------------------------------------------------export---------------------------------------------------
  window['AscCommon'] = window['AscCommon'] || {};
  window["AscCommon"].g_spellCheckLanguages = g_spellCheckLanguages;
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

/** @enum {number} */
var c_oAscZoomType = {
	Current  : 0,
	FitWidth : 1,
	FitPage  : 2
};

/** @enum {number} */
var c_oAscAlignType = {
	LEFT    : 0,
	CENTER  : 1,
	RIGHT   : 2,
	JUSTIFY : 3,
	TOP     : 4,
	MIDDLE  : 5,
	BOTTOM  : 6
};

/** @enum {number} */
var c_oAscWrapStyle2 = {
	Inline       : 0,
	Square       : 1,
	Tight        : 2,
	Through      : 3,
	TopAndBottom : 4,
	Behind       : 5,
	InFront      : 6
};

/** @enum {number} */
var c_oAscTableSelectionType = {
	Cell   : 0,
	Row    : 1,
	Column : 2,
	Table  : 3
};

/** @enum {number} */
var c_oAscContextMenuTypes = {
	Common       : 0, // Обычное контекстное меню
	ChangeHdrFtr : 1  // Специальное контестное меню для попадания в колонтитул
};

/** @enum {number} */
var c_oAscMouseMoveLockedObjectType = {
	Common : 0,
	Header : 1,
	Footer : 2
};

/** @enum {number} */
var c_oAscCollaborativeMarksShowType = {
	None        : -1,
	All         : 0,
	LastChanges : 1
};

/**
 * Типы горизонтального прилегания для автофигур.
 * @type {{Center: number, Inside: number, Left: number, Outside: number, Right: number}}
 * @enum {number}
 */
var c_oAscAlignH = {
	Center  : 0x00,
	Inside  : 0x01,
	Left    : 0x02,
	Outside : 0x03,
	Right   : 0x04
};

/** @enum {number} */
var c_oAscChangeLevel = {
	BringToFront  : 0x00,
	BringForward  : 0x01,
	SendToBack    : 0x02,
	BringBackward : 0x03
};

/**
 * Типы вертикального прилегания для автофигур.
 * @type {{Bottom: number, Center: number, Inside: number, Outside: number, Top: number}}
 * @enum {number}
 */
var c_oAscAlignV = {
	Bottom  : 0x00,
	Center  : 0x01,
	Inside  : 0x02,
	Outside : 0x03,
	Top     : 0x04
};

/** @enum {number} */
var c_oAscVertAlignJc = {
	Top    : 0x00, // var vertalignjc_Top    = 0x00;
	Center : 0x01, // var vertalignjc_Center = 0x01;
	Bottom : 0x02  // var vertalignjc_Bottom = 0x02
};

/** @enum {number} */
var c_oAscTableLayout = {
	AutoFit : 0x00,
	Fixed   : 0x01
};

/** @enum {number} */
var c_oAscAlignShapeType = {
	ALIGN_LEFT   : 0,
	ALIGN_RIGHT  : 1,
	ALIGN_TOP    : 2,
	ALIGN_BOTTOM : 3,
	ALIGN_CENTER : 4,
	ALIGN_MIDDLE : 5
};

var TABLE_STYLE_WIDTH_PIX  = 70;
var TABLE_STYLE_HEIGHT_PIX = 50;

/** @enum {number} */
var c_oAscSectionBreakType = {
	NextPage   : 0x00,
	OddPage    : 0x01,
	EvenPage   : 0x02,
	Continuous : 0x03,
	Column     : 0x04
};

/** @enum {number} */
var c_oAscMathMainType = {
	Symbol        : 0x00,
	Fraction      : 0x01,
	Script        : 0x02,
	Radical       : 0x03,
	Integral      : 0x04,
	LargeOperator : 0x05,
	Bracket       : 0x06,
	Function      : 0x07,
	Accent        : 0x08,
	LimitLog      : 0x09,
	Operator      : 0x0a,
	Matrix        : 0x0b,
	Empty_Content : 0x0c
};

var c_oAscMathMainTypeStrings                               = {};
c_oAscMathMainTypeStrings[c_oAscMathMainType.Symbol]        = "Symbols";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Fraction]      = "Fraction";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Script]        = "Script";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Radical]       = "Radical";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Integral]      = "Integral";
c_oAscMathMainTypeStrings[c_oAscMathMainType.LargeOperator] = "LargeOperator";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Bracket]       = "Bracket";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Function]      = "Function";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Accent]        = "Accent";
c_oAscMathMainTypeStrings[c_oAscMathMainType.LimitLog]      = "LimitLog";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Operator]      = "Operator";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Matrix]        = "Matrix";
c_oAscMathMainTypeStrings[c_oAscMathMainType.Empty_Content] = "Empty_Content";

/** @enum {number} */
var c_oAscMathType = {
	//----------------------------------------------------------------------------------------------------------------------
	Symbol_pm                               : 0x00000000,
	Symbol_infinity                         : 0x00000001,
	Symbol_equals                           : 0x00000002,
	Symbol_neq                              : 0x00000003,
	Symbol_about                            : 0x00000004,
	Symbol_times                            : 0x00000005,
	Symbol_div                              : 0x00000006,
	Symbol_factorial                        : 0x00000007,
	Symbol_propto                           : 0x00000008,
	Symbol_less                             : 0x00000009,
	Symbol_ll                               : 0x0000000a,
	Symbol_greater                          : 0x0000000b,
	Symbol_gg                               : 0x0000000c,
	Symbol_leq                              : 0x0000000d,
	Symbol_geq                              : 0x0000000e,
	Symbol_mp                               : 0x0000000f,
	Symbol_cong                             : 0x00000010,
	Symbol_approx                           : 0x00000011,
	Symbol_equiv                            : 0x00000012,
	Symbol_forall                           : 0x00000013,
	Symbol_additional                       : 0x00000014,
	Symbol_partial                          : 0x00000015,
	Symbol_sqrt                             : 0x00000016,
	Symbol_cbrt                             : 0x00000017,
	Symbol_qdrt                             : 0x00000018,
	Symbol_cup                              : 0x00000019,
	Symbol_cap                              : 0x0000001a,
	Symbol_emptyset                         : 0x0000001b,
	Symbol_percent                          : 0x0000001c,
	Symbol_degree                           : 0x0000001d,
	Symbol_fahrenheit                       : 0x0000001e,
	Symbol_celsius                          : 0x0000001f,
	Symbol_inc                              : 0x00000020,
	Symbol_nabla                            : 0x00000021,
	Symbol_exists                           : 0x00000022,
	Symbol_notexists                        : 0x00000023,
	Symbol_in                               : 0x00000024,
	Symbol_ni                               : 0x00000025,
	Symbol_leftarrow                        : 0x00000026,
	Symbol_uparrow                          : 0x00000027,
	Symbol_rightarrow                       : 0x00000028,
	Symbol_downarrow                        : 0x00000029,
	Symbol_leftrightarrow                   : 0x0000002a,
	Symbol_therefore                        : 0x0000002b,
	Symbol_plus                             : 0x0000002c,
	Symbol_minus                            : 0x0000002d,
	Symbol_not                              : 0x0000002e,
	Symbol_ast                              : 0x0000002f,
	Symbol_bullet                           : 0x00000030,
	Symbol_vdots                            : 0x00000031,
	Symbol_cdots                            : 0x00000032,
	Symbol_rddots                           : 0x00000033,
	Symbol_ddots                            : 0x00000034,
	Symbol_aleph                            : 0x00000035,
	Symbol_beth                             : 0x00000036,
	Symbol_QED                              : 0x00000037,
	Symbol_alpha                            : 0x00010000,
	Symbol_beta                             : 0x00010001,
	Symbol_gamma                            : 0x00010002,
	Symbol_delta                            : 0x00010003,
	Symbol_varepsilon                       : 0x00010004,
	Symbol_epsilon                          : 0x00010005,
	Symbol_zeta                             : 0x00010006,
	Symbol_eta                              : 0x00010007,
	Symbol_theta                            : 0x00010008,
	Symbol_vartheta                         : 0x00010009,
	Symbol_iota                             : 0x0001000a,
	Symbol_kappa                            : 0x0001000b,
	Symbol_lambda                           : 0x0001000c,
	Symbol_mu                               : 0x0001000d,
	Symbol_nu                               : 0x0001000e,
	Symbol_xsi                              : 0x0001000f,
	Symbol_o                                : 0x00010010,
	Symbol_pi                               : 0x00010011,
	Symbol_varpi                            : 0x00010012,
	Symbol_rho                              : 0x00010013,
	Symbol_varrho                           : 0x00010014,
	Symbol_sigma                            : 0x00010015,
	Symbol_varsigma                         : 0x00010016,
	Symbol_tau                              : 0x00010017,
	Symbol_upsilon                          : 0x00010018,
	Symbol_varphi                           : 0x00010019,
	Symbol_phi                              : 0x0001001a,
	Symbol_chi                              : 0x0001001b,
	Symbol_psi                              : 0x0001001c,
	Symbol_omega                            : 0x0001001d,
	Symbol_Alpha                            : 0x00020000,
	Symbol_Beta                             : 0x00020001,
	Symbol_Gamma                            : 0x00020002,
	Symbol_Delta                            : 0x00020003,
	Symbol_Epsilon                          : 0x00020004,
	Symbol_Zeta                             : 0x00020005,
	Symbol_Eta                              : 0x00020006,
	Symbol_Theta                            : 0x00020007,
	Symbol_Iota                             : 0x00020008,
	Symbol_Kappa                            : 0x00020009,
	Symbol_Lambda                           : 0x0002000a,
	Symbol_Mu                               : 0x0002000b,
	Symbol_Nu                               : 0x0002000c,
	Symbol_Xsi                              : 0x0002000d,
	Symbol_O                                : 0x0002000e,
	Symbol_Pi                               : 0x0002000f,
	Symbol_Rho                              : 0x00020010,
	Symbol_Sigma                            : 0x00020011,
	Symbol_Tau                              : 0x00020012,
	Symbol_Upsilon                          : 0x00020013,
	Symbol_Phi                              : 0x00020014,
	Symbol_Chi                              : 0x00020015,
	Symbol_Psi                              : 0x00020016,
	Symbol_Omega                            : 0x00020017,
	//----------------------------------------------------------------------------------------------------------------------
	FractionVertical                        : 0x01000000,
	FractionDiagonal                        : 0x01000001,
	FractionHorizontal                      : 0x01000002,
	FractionSmall                           : 0x01000003,
	FractionDifferential_1                  : 0x01010000,
	FractionDifferential_2                  : 0x01010001,
	FractionDifferential_3                  : 0x01010002,
	FractionDifferential_4                  : 0x01010003,
	FractionPi_2                            : 0x01010004,
	//----------------------------------------------------------------------------------------------------------------------
	ScriptSup                               : 0x02000000,
	ScriptSub                               : 0x02000001,
	ScriptSubSup                            : 0x02000002,
	ScriptSubSupLeft                        : 0x02000003,
	ScriptCustom_1                          : 0x02010000,
	ScriptCustom_2                          : 0x02010001,
	ScriptCustom_3                          : 0x02010002,
	ScriptCustom_4                          : 0x02010003,
	//----------------------------------------------------------------------------------------------------------------------
	RadicalSqrt                             : 0x03000000,
	RadicalRoot_n                           : 0x03000001,
	RadicalRoot_2                           : 0x03000002,
	RadicalRoot_3                           : 0x03000003,
	RadicalCustom_1                         : 0x03010000,
	RadicalCustom_2                         : 0x03010001,
	//----------------------------------------------------------------------------------------------------------------------
	Integral                                : 0x04000000,
	IntegralSubSup                          : 0x04000001,
	IntegralCenterSubSup                    : 0x04000002,
	IntegralDouble                          : 0x04000003,
	IntegralDoubleSubSup                    : 0x04000004,
	IntegralDoubleCenterSubSup              : 0x04000005,
	IntegralTriple                          : 0x04000006,
	IntegralTripleSubSup                    : 0x04000007,
	IntegralTripleCenterSubSup              : 0x04000008,
	IntegralOriented                        : 0x04010000,
	IntegralOrientedSubSup                  : 0x04010001,
	IntegralOrientedCenterSubSup            : 0x04010002,
	IntegralOrientedDouble                  : 0x04010003,
	IntegralOrientedDoubleSubSup            : 0x04010004,
	IntegralOrientedDoubleCenterSubSup      : 0x04010005,
	IntegralOrientedTriple                  : 0x04010006,
	IntegralOrientedTripleSubSup            : 0x04010007,
	IntegralOrientedTripleCenterSubSup      : 0x04010008,
	Integral_dx                             : 0x04020000,
	Integral_dy                             : 0x04020001,
	Integral_dtheta                         : 0x04020002,
	//----------------------------------------------------------------------------------------------------------------------
	LargeOperator_Sum                       : 0x05000000,
	LargeOperator_Sum_CenterSubSup          : 0x05000001,
	LargeOperator_Sum_SubSup                : 0x05000002,
	LargeOperator_Sum_CenterSub             : 0x05000003,
	LargeOperator_Sum_Sub                   : 0x05000004,
	LargeOperator_Prod                      : 0x05010000,
	LargeOperator_Prod_CenterSubSup         : 0x05010001,
	LargeOperator_Prod_SubSup               : 0x05010002,
	LargeOperator_Prod_CenterSub            : 0x05010003,
	LargeOperator_Prod_Sub                  : 0x05010004,
	LargeOperator_CoProd                    : 0x05010005,
	LargeOperator_CoProd_CenterSubSup       : 0x05010006,
	LargeOperator_CoProd_SubSup             : 0x05010007,
	LargeOperator_CoProd_CenterSub          : 0x05010008,
	LargeOperator_CoProd_Sub                : 0x05010009,
	LargeOperator_Union                     : 0x05020000,
	LargeOperator_Union_CenterSubSup        : 0x05020001,
	LargeOperator_Union_SubSup              : 0x05020002,
	LargeOperator_Union_CenterSub           : 0x05020003,
	LargeOperator_Union_Sub                 : 0x05020004,
	LargeOperator_Intersection              : 0x05020005,
	LargeOperator_Intersection_CenterSubSup : 0x05020006,
	LargeOperator_Intersection_SubSup       : 0x05020007,
	LargeOperator_Intersection_CenterSub    : 0x05020008,
	LargeOperator_Intersection_Sub          : 0x05020009,
	LargeOperator_Disjunction               : 0x05030000,
	LargeOperator_Disjunction_CenterSubSup  : 0x05030001,
	LargeOperator_Disjunction_SubSup        : 0x05030002,
	LargeOperator_Disjunction_CenterSub     : 0x05030003,
	LargeOperator_Disjunction_Sub           : 0x05030004,
	LargeOperator_Conjunction               : 0x05030005,
	LargeOperator_Conjunction_CenterSubSup  : 0x05030006,
	LargeOperator_Conjunction_SubSup        : 0x05030007,
	LargeOperator_Conjunction_CenterSub     : 0x05030008,
	LargeOperator_Conjunction_Sub           : 0x05030009,
	LargeOperator_Custom_1                  : 0x05040000,
	LargeOperator_Custom_2                  : 0x05040001,
	LargeOperator_Custom_3                  : 0x05040002,
	LargeOperator_Custom_4                  : 0x05040003,
	LargeOperator_Custom_5                  : 0x05040004,
	//----------------------------------------------------------------------------------------------------------------------
	Bracket_Round                           : 0x06000000,
	Bracket_Square                          : 0x06000001,
	Bracket_Curve                           : 0x06000002,
	Bracket_Angle                           : 0x06000003,
	Bracket_LowLim                          : 0x06000004,
	Bracket_UppLim                          : 0x06000005,
	Bracket_Line                            : 0x06000006,
	Bracket_LineDouble                      : 0x06000007,
	Bracket_Square_OpenOpen                 : 0x06000008,
	Bracket_Square_CloseClose               : 0x06000009,
	Bracket_Square_CloseOpen                : 0x0600000a,
	Bracket_SquareDouble                    : 0x0600000b,
	Bracket_Round_Delimiter_2               : 0x06010000,
	Bracket_Curve_Delimiter_2               : 0x06010001,
	Bracket_Angle_Delimiter_2               : 0x06010002,
	Bracket_Angle_Delimiter_3               : 0x06010003,
	Bracket_Round_OpenNone                  : 0x06020000,
	Bracket_Round_NoneOpen                  : 0x06020001,
	Bracket_Square_OpenNone                 : 0x06020002,
	Bracket_Square_NoneOpen                 : 0x06020003,
	Bracket_Curve_OpenNone                  : 0x06020004,
	Bracket_Curve_NoneOpen                  : 0x06020005,
	Bracket_Angle_OpenNone                  : 0x06020006,
	Bracket_Angle_NoneOpen                  : 0x06020007,
	Bracket_LowLim_OpenNone                 : 0x06020008,
	Bracket_LowLim_NoneNone                 : 0x06020009,
	Bracket_UppLim_OpenNone                 : 0x0602000a,
	Bracket_UppLim_NoneOpen                 : 0x0602000b,
	Bracket_Line_OpenNone                   : 0x0602000c,
	Bracket_Line_NoneOpen                   : 0x0602000d,
	Bracket_LineDouble_OpenNone             : 0x0602000e,
	Bracket_LineDouble_NoneOpen             : 0x0602000f,
	Bracket_SquareDouble_OpenNone           : 0x06020010,
	Bracket_SquareDouble_NoneOpen           : 0x06020011,
	Bracket_Custom_1                        : 0x06030000,
	Bracket_Custom_2                        : 0x06030001,
	Bracket_Custom_3                        : 0x06030002,
	Bracket_Custom_4                        : 0x06030003,
	Bracket_Custom_5                        : 0x06040000,
	Bracket_Custom_6                        : 0x06040001,
	Bracket_Custom_7                        : 0x06040002,
	//----------------------------------------------------------------------------------------------------------------------
	Function_Sin                            : 0x07000000,
	Function_Cos                            : 0x07000001,
	Function_Tan                            : 0x07000002,
	Function_Csc                            : 0x07000003,
	Function_Sec                            : 0x07000004,
	Function_Cot                            : 0x07000005,
	Function_1_Sin                          : 0x07010000,
	Function_1_Cos                          : 0x07010001,
	Function_1_Tan                          : 0x07010002,
	Function_1_Csc                          : 0x07010003,
	Function_1_Sec                          : 0x07010004,
	Function_1_Cot                          : 0x07010005,
	Function_Sinh                           : 0x07020000,
	Function_Cosh                           : 0x07020001,
	Function_Tanh                           : 0x07020002,
	Function_Csch                           : 0x07020003,
	Function_Sech                           : 0x07020004,
	Function_Coth                           : 0x07020005,
	Function_1_Sinh                         : 0x07030000,
	Function_1_Cosh                         : 0x07030001,
	Function_1_Tanh                         : 0x07030002,
	Function_1_Csch                         : 0x07030003,
	Function_1_Sech                         : 0x07030004,
	Function_1_Coth                         : 0x07030005,
	Function_Custom_1                       : 0x07040000,
	Function_Custom_2                       : 0x07040001,
	Function_Custom_3                       : 0x07040002,
	//----------------------------------------------------------------------------------------------------------------------
	Accent_Dot                              : 0x08000000,
	Accent_DDot                             : 0x08000001,
	Accent_DDDot                            : 0x08000002,
	Accent_Hat                              : 0x08000003,
	Accent_Check                            : 0x08000004,
	Accent_Accent                           : 0x08000005,
	Accent_Grave                            : 0x08000006,
	Accent_Smile                            : 0x08000007,
	Accent_Tilde                            : 0x08000008,
	Accent_Bar                              : 0x08000009,
	Accent_DoubleBar                        : 0x0800000a,
	Accent_CurveBracketTop                  : 0x0800000b,
	Accent_CurveBracketBot                  : 0x0800000c,
	Accent_GroupTop                         : 0x0800000d,
	Accent_GroupBot                         : 0x0800000e,
	Accent_ArrowL                           : 0x0800000f,
	Accent_ArrowR                           : 0x08000010,
	Accent_ArrowD                           : 0x08000011,
	Accent_HarpoonL                         : 0x08000012,
	Accent_HarpoonR                         : 0x08000013,
	Accent_BorderBox                        : 0x08010000,
	Accent_BorderBoxCustom                  : 0x08010001,
	Accent_BarTop                           : 0x08020000,
	Accent_BarBot                           : 0x08020001,
	Accent_Custom_1                         : 0x08030000,
	Accent_Custom_2                         : 0x08030001,
	Accent_Custom_3                         : 0x08030002,
	//----------------------------------------------------------------------------------------------------------------------
	LimitLog_LogBase                        : 0x09000000,
	LimitLog_Log                            : 0x09000001,
	LimitLog_Lim                            : 0x09000002,
	LimitLog_Min                            : 0x09000003,
	LimitLog_Max                            : 0x09000004,
	LimitLog_Ln                             : 0x09000005,
	LimitLog_Custom_1                       : 0x09010000,
	LimitLog_Custom_2                       : 0x09010001,
	//----------------------------------------------------------------------------------------------------------------------
	Operator_ColonEquals                    : 0x0a000000,
	Operator_EqualsEquals                   : 0x0a000001,
	Operator_PlusEquals                     : 0x0a000002,
	Operator_MinusEquals                    : 0x0a000003,
	Operator_Definition                     : 0x0a000004,
	Operator_UnitOfMeasure                  : 0x0a000005,
	Operator_DeltaEquals                    : 0x0a000006,
	Operator_ArrowL_Top                     : 0x0a010000,
	Operator_ArrowR_Top                     : 0x0a010001,
	Operator_ArrowL_Bot                     : 0x0a010002,
	Operator_ArrowR_Bot                     : 0x0a010003,
	Operator_DoubleArrowL_Top               : 0x0a010004,
	Operator_DoubleArrowR_Top               : 0x0a010005,
	Operator_DoubleArrowL_Bot               : 0x0a010006,
	Operator_DoubleArrowR_Bot               : 0x0a010007,
	Operator_ArrowD_Top                     : 0x0a010008,
	Operator_ArrowD_Bot                     : 0x0a010009,
	Operator_DoubleArrowD_Top               : 0x0a01000a,
	Operator_DoubleArrowD_Bot               : 0x0a01000b,
	Operator_Custom_1                       : 0x0a020000,
	Operator_Custom_2                       : 0x0a020001,
	//----------------------------------------------------------------------------------------------------------------------
	Matrix_1_2                              : 0x0b000000,
	Matrix_2_1                              : 0x0b000001,
	Matrix_1_3                              : 0x0b000002,
	Matrix_3_1                              : 0x0b000003,
	Matrix_2_2                              : 0x0b000004,
	Matrix_2_3                              : 0x0b000005,
	Matrix_3_2                              : 0x0b000006,
	Matrix_3_3                              : 0x0b000007,
	Matrix_Dots_Center                      : 0x0b010000,
	Matrix_Dots_Baseline                    : 0x0b010001,
	Matrix_Dots_Vertical                    : 0x0b010002,
	Matrix_Dots_Diagonal                    : 0x0b010003,
	Matrix_Identity_2                       : 0x0b020000,
	Matrix_Identity_2_NoZeros               : 0x0b020001,
	Matrix_Identity_3                       : 0x0b020002,
	Matrix_Identity_3_NoZeros               : 0x0b020003,
	Matrix_2_2_RoundBracket                 : 0x0b030000,
	Matrix_2_2_SquareBracket                : 0x0b030001,
	Matrix_2_2_LineBracket                  : 0x0b030002,
	Matrix_2_2_DLineBracket                 : 0x0b030003,
	Matrix_Flat_Round                       : 0x0b040000,
	Matrix_Flat_Square                      : 0x0b040001,
	//----------------------------------------------------------------------------------------------------------------------
	Default_Text                            : 0x0c000000
};

/** @enum {number} */
var c_oAscMathInterfaceType = {
	Common        : 0x00,
	Fraction      : 0x01,
	Script        : 0x02,
	Radical       : 0x03,
	LargeOperator : 0x04,
	Delimiter     : 0x05,
	Function      : 0x06,
	Accent        : 0x07,
	BorderBox     : 0x08,
	Bar           : 0x09,
	Box           : 0x0a,
	Limit         : 0x0b,
	GroupChar     : 0x0c,
	Matrix        : 0x0d,
	EqArray       : 0x0e,
	Phantom       : 0x0f
};

/** @enum {number} */
var c_oAscMathInterfaceBarPos = {
	Top    : 0,
	Bottom : 1
};

/** @enum {number} */
var c_oAscMathInterfaceScript = {
	None      : 0x000,  // Удаление скрипта
	Sup       : 0x001,
	Sub       : 0x002,
	SubSup    : 0x003,
	PreSubSup : 0x004
};

/** @enum {number} */
var c_oAscMathInterfaceFraction = {
	Bar    : 0x001,
	Skewed : 0x002,
	Linear : 0x003,
	NoBar  : 0x004
};

/** @enum {number} */
var c_oAscMathInterfaceLimitPos = {
	None   : -1,  // Удаление предела
	Top    : 0,
	Bottom : 1
};

/** @enum {number} */
var c_oAscMathInterfaceMatrixMatrixAlign = {
	Top    : 0,
	Center : 1,
	Bottom : 2
};

/** @enum {number} */
var c_oAscMathInterfaceMatrixColumnAlign = {
	Left   : 0,
	Center : 1,
	Right  : 2
};

/** @enum {number} */
var c_oAscMathInterfaceMatrixRowRule = {
	Single     : 0x00,
	OneAndHalf : 0x01,
	Double     : 0x02,
	Exactly    : 0x03,
	Multiple   : 0x04

};

/** @enum {number} */
var c_oAscMathInterfaceMatrixColumnRule = {
	Single     : 0x00,
	OneAndHalf : 0x01,
	Double     : 0x02,
	Exactly    : 0x03,
	Multiple   : 0x04
};

/** @enum {number} */
var c_oAscMathInterfaceEqArrayAlign = {
	Top    : 0,
	Center : 1,
	Bottom : 2
};

/** @enum {number} */
var c_oAscMathInterfaceEqArrayLineRule = {
	Single     : 0x00,
	OneAndHalf : 0x01,
	Double     : 0x02,
	Exactly    : 0x03,
	Multiple   : 0x04
};

/** @enum {number} */
var c_oAscMathInterfaceNaryLimitLocation = {
	UndOvr : 0,
	SubSup : 1
};

/** @enum {number} */
var c_oAscMathInterfaceGroupCharPos = {
	None   : -1,  // Удаление GroupChar
	Top    : 0,
	Bottom : 1
};

/** @enum {number} */
var c_oAscMathInterfaceSettingsBrkBin = {
	BreakRepeat : 0x00,
	BreakBefore : 0x01,
	BreakAfter  : 0x02
};

/** @enum {number} */
var c_oAscMathInterfaceSettingsAlign = {
	Left    : 0,
	Center  : 1,
	Right   : 2,
	Justify : 3
};

/** @enum {number} */
var c_oAscRevisionsChangeType = {
	Unknown : 0x00,
	TextAdd : 0x01,
	TextRem : 0x02,
	ParaAdd : 0x03,
	ParaRem : 0x04,
	TextPr  : 0x05,
	ParaPr  : 0x06
};

/** @enum {number} */
var c_oAscRevisionsObjectType = {
	Image        : 0,
	Shape        : 1,
	Chart        : 2,
	MathEquation : 3
};

var c_oSerFormat = {
	Version   : 5, //1.0.0.5
	Signature : "DOCY"
};

window["flat_desine"] = false;

//------------------------------------------------------------export---------------------------------------------------
var prot;
window['Asc'] = window['Asc'] || {};
prot          = window['Asc']['c_oAscWrapStyle2'] = c_oAscWrapStyle2;
prot['Inline']       = c_oAscWrapStyle2.Inline;
prot['Square']       = c_oAscWrapStyle2.Square;
prot['Tight']        = c_oAscWrapStyle2.Tight;
prot['Through']      = c_oAscWrapStyle2.Through;
prot['TopAndBottom'] = c_oAscWrapStyle2.TopAndBottom;
prot['Behind']       = c_oAscWrapStyle2.Behind;
prot['InFront']      = c_oAscWrapStyle2.InFront;

prot = window['Asc']['c_oAscContextMenuTypes'] = window['Asc'].c_oAscContextMenuTypes = c_oAscContextMenuTypes;
prot['Common']       = c_oAscContextMenuTypes.Common;
prot['ChangeHdrFtr'] = c_oAscContextMenuTypes.ChangeHdrFtr;

prot = window['Asc']['c_oAscCollaborativeMarksShowType'] = c_oAscCollaborativeMarksShowType;
prot['None']        = c_oAscCollaborativeMarksShowType.None;
prot['All']         = c_oAscCollaborativeMarksShowType.All;
prot['LastChanges'] = c_oAscCollaborativeMarksShowType.LastChanges;

prot = window['Asc']['c_oAscAlignH'] = c_oAscAlignH;
prot['Center']  = c_oAscAlignH.Center;
prot['Inside']  = c_oAscAlignH.Inside;
prot['Left']    = c_oAscAlignH.Left;
prot['Outside'] = c_oAscAlignH.Outside;
prot['Right']   = c_oAscAlignH.Right;

prot = window['Asc']['c_oAscAlignV'] = c_oAscAlignV;
prot['Bottom']  = c_oAscAlignV.Bottom;
prot['Center']  = c_oAscAlignV.Center;
prot['Inside']  = c_oAscAlignV.Inside;
prot['Outside'] = c_oAscAlignV.Outside;
prot['Top']     = c_oAscAlignV.Top;

prot = window['Asc']['c_oAscChangeLevel'] = c_oAscChangeLevel;
prot['BringToFront']  = c_oAscChangeLevel.BringToFront;
prot['BringForward']  = c_oAscChangeLevel.BringForward;
prot['SendToBack']    = c_oAscChangeLevel.SendToBack;
prot['BringBackward'] = c_oAscChangeLevel.BringBackward;

prot = window['Asc']['c_oAscVertAlignJc'] = c_oAscVertAlignJc;
prot['Top']    = c_oAscVertAlignJc.Top;
prot['Center'] = c_oAscVertAlignJc.Center;
prot['Bottom'] = c_oAscVertAlignJc.Bottom;

prot = window['Asc']['c_oAscTableLayout'] = c_oAscTableLayout;
prot['AutoFit'] = c_oAscTableLayout.AutoFit;
prot['Fixed']   = c_oAscTableLayout.Fixed;

prot = window['Asc']['c_oAscAlignShapeType'] = c_oAscAlignShapeType;
prot['ALIGN_LEFT']   = c_oAscAlignShapeType.ALIGN_LEFT;
prot['ALIGN_RIGHT']  = c_oAscAlignShapeType.ALIGN_RIGHT;
prot['ALIGN_TOP']    = c_oAscAlignShapeType.ALIGN_TOP;
prot['ALIGN_BOTTOM'] = c_oAscAlignShapeType.ALIGN_BOTTOM;
prot['ALIGN_CENTER'] = c_oAscAlignShapeType.ALIGN_CENTER;
prot['ALIGN_MIDDLE'] = c_oAscAlignShapeType.ALIGN_MIDDLE;

prot = window['Asc']['c_oAscSectionBreakType'] = c_oAscSectionBreakType;
prot['NextPage']   = c_oAscSectionBreakType.NextPage;
prot['OddPage']    = c_oAscSectionBreakType.OddPage;
prot['EvenPage']   = c_oAscSectionBreakType.EvenPage;
prot['Continuous'] = c_oAscSectionBreakType.Continuous;
prot['Column']     = c_oAscSectionBreakType.Column;

prot = window['Asc']['c_oAscMathInterfaceType'] = c_oAscMathInterfaceType;
prot['Common']        = c_oAscMathInterfaceType.Common;
prot['Fraction']      = c_oAscMathInterfaceType.Fraction;
prot['Script']        = c_oAscMathInterfaceType.Script;
prot['Radical']       = c_oAscMathInterfaceType.Radical;
prot['LargeOperator'] = c_oAscMathInterfaceType.LargeOperator;
prot['Delimiter']     = c_oAscMathInterfaceType.Delimiter;
prot['Function']      = c_oAscMathInterfaceType.Function;
prot['Accent']        = c_oAscMathInterfaceType.Accent;
prot['BorderBox']     = c_oAscMathInterfaceType.BorderBox;
prot['Bar']           = c_oAscMathInterfaceType.Bar;
prot['Limit']         = c_oAscMathInterfaceType.Limit;
prot['GroupChar']     = c_oAscMathInterfaceType.GroupChar;
prot['Matrix']        = c_oAscMathInterfaceType.Matrix;
prot['EqArray']       = c_oAscMathInterfaceType.EqArray;
prot['Phantom']       = c_oAscMathInterfaceType.Phantom;

prot = window['Asc']['c_oAscMathInterfaceBarPos'] = c_oAscMathInterfaceBarPos;
prot['Top']    = c_oAscMathInterfaceBarPos.Top;
prot['Bottom'] = c_oAscMathInterfaceBarPos.Bottom;

prot = window['Asc']['c_oAscMathInterfaceScript'] = c_oAscMathInterfaceScript;
prot['None']      = c_oAscMathInterfaceScript.None;
prot['Sup']       = c_oAscMathInterfaceScript.Sup;
prot['Sub']       = c_oAscMathInterfaceScript.Sub;
prot['SubSup']    = c_oAscMathInterfaceScript.SubSup;
prot['PreSubSup'] = c_oAscMathInterfaceScript.PreSubSup;

prot = window['Asc']['c_oAscMathInterfaceFraction'] = c_oAscMathInterfaceFraction;
prot['None']   = c_oAscMathInterfaceFraction.Bar;
prot['Skewed'] = c_oAscMathInterfaceFraction.Skewed;
prot['Linear'] = c_oAscMathInterfaceFraction.Linear;
prot['NoBar']  = c_oAscMathInterfaceFraction.NoBar;

prot = window['Asc']['c_oAscMathInterfaceLimitPos'] = c_oAscMathInterfaceLimitPos;
prot['None']   = c_oAscMathInterfaceLimitPos.None;
prot['Top']    = c_oAscMathInterfaceLimitPos.Top;
prot['Bottom'] = c_oAscMathInterfaceLimitPos.Bottom;

prot = window['Asc']['c_oAscMathInterfaceMatrixMatrixAlign'] = c_oAscMathInterfaceMatrixMatrixAlign;
prot['Top']    = c_oAscMathInterfaceMatrixMatrixAlign.Top;
prot['Center'] = c_oAscMathInterfaceMatrixMatrixAlign.Center;
prot['Bottom'] = c_oAscMathInterfaceMatrixMatrixAlign.Bottom;

prot = window['Asc']['c_oAscMathInterfaceMatrixColumnAlign'] = c_oAscMathInterfaceMatrixColumnAlign;
prot['Left']   = c_oAscMathInterfaceMatrixColumnAlign.Left;
prot['Center'] = c_oAscMathInterfaceMatrixColumnAlign.Center;
prot['Right']  = c_oAscMathInterfaceMatrixColumnAlign.Right;

prot = window['Asc']['c_oAscMathInterfaceEqArrayAlign'] = c_oAscMathInterfaceEqArrayAlign;
prot['Top']    = c_oAscMathInterfaceEqArrayAlign.Top;
prot['Center'] = c_oAscMathInterfaceEqArrayAlign.Center;
prot['Bottom'] = c_oAscMathInterfaceEqArrayAlign.Bottom;

prot = window['Asc']['c_oAscMathInterfaceNaryLimitLocation'] = c_oAscMathInterfaceNaryLimitLocation;
prot['UndOvr'] = c_oAscMathInterfaceNaryLimitLocation.UndOvr;
prot['SubSup'] = c_oAscMathInterfaceNaryLimitLocation.SubSup;

prot = window['Asc']['c_oAscMathInterfaceGroupCharPos'] = c_oAscMathInterfaceGroupCharPos;
prot['None']   = c_oAscMathInterfaceGroupCharPos.None;
prot['Top']    = c_oAscMathInterfaceGroupCharPos.Top;
prot['Bottom'] = c_oAscMathInterfaceGroupCharPos.Bottom;

prot = window['Asc']['c_oAscRevisionsChangeType'] = c_oAscRevisionsChangeType;
prot['Unknown'] = c_oAscRevisionsChangeType.Unknown;
prot['TextAdd'] = c_oAscRevisionsChangeType.TextAdd;
prot['TextRem'] = c_oAscRevisionsChangeType.TextRem;
prot['ParaAdd'] = c_oAscRevisionsChangeType.ParaAdd;
prot['ParaRem'] = c_oAscRevisionsChangeType.ParaRem;
prot['TextPr']  = c_oAscRevisionsChangeType.TextPr;
prot['ParaPr']  = c_oAscRevisionsChangeType.ParaPr;

window['AscCommon']                = window['AscCommon'] || {};
window['AscCommon'].c_oSerFormat   = c_oSerFormat;
window['AscCommon'].CurFileVersion = c_oSerFormat.Version;

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

var FOREIGN_CURSOR_LABEL_HIDETIME = 1500;

function CCollaborativeChanges()
{
    this.m_pData         = null;
    this.m_oColor        = null;
}

CCollaborativeChanges.prototype.Set_Data = function(pData)
{
    this.m_pData = pData;
};
CCollaborativeChanges.prototype.Set_Color = function(oColor)
{
    this.m_oColor = oColor;
};
CCollaborativeChanges.prototype.Set_FromUndoRedo = function(Class, Data, Binary)
{
    if ( "undefined" === typeof(Class.Get_Id) )
        return false;

    // Преобразуем данные в бинарный файл
    this.m_pData  = this.Internal_Save_Data( Class, Data, Binary );

    return true;
};
CCollaborativeChanges.prototype.Apply_Data = function()
{
    var LoadData  = this.Internal_Load_Data(this.m_pData);
    var ClassId   = LoadData.Reader.GetString2();
    var ReaderPos = LoadData.Reader.GetCurPos();
    var Type      = LoadData.Reader.GetLong();
    var Class     = null;

    if (AscDFH.historyitem_type_HdrFtr === Type)
        Class = editor.WordControl.m_oLogicDocument.HdrFtr;
    else
        Class = AscCommon.g_oTableId.Get_ById(ClassId);

    LoadData.Reader.Seek2(ReaderPos);

    if (null != Class)
        return Class.Load_Changes(LoadData.Reader, LoadData.Reader2, this.m_oColor);
    else
        return false;
};
CCollaborativeChanges.prototype.Internal_Load_Data = function(szSrc)
{
    var srcLen = szSrc.length;
    var index =  -1;

    while (true)
    {
        index++;
        var _c = szSrc.charCodeAt(index);
        if (_c == ";".charCodeAt(0))
        {
            index++;
            break;
        }
    }

    var bPost = false;
    // Ищем следующее вхождение ";"
    while (index < srcLen)
    {
        index++;
        var _c = szSrc.charCodeAt(index);
        if (_c == ";".charCodeAt(0))
        {
            index++;
            bPost = true;
            break;
        }
    }

    if ( true === bPost )
        return { Reader : this.Internal_Load_Data2(szSrc, 0, index - 1), Reader2 : this.Internal_Load_Data2(szSrc, index, srcLen ) };
    else
        return { Reader : this.Internal_Load_Data2(szSrc, 0, szSrc.length), Reader2 : null };
};
CCollaborativeChanges.prototype.Internal_Load_Data2 = function(szSrc, offset, srcLen)
{
    var nWritten = 0;

    var index =  -1 + offset;
    var dst_len = "";

    while (true)
    {
        index++;
        var _c = szSrc.charCodeAt(index);
        if (_c == ";".charCodeAt(0))
        {
            index++;
            break;
        }

        dst_len += String.fromCharCode(_c);
    }

    var dstLen = parseInt(dst_len);

    var pointer = AscFonts.g_memory.Alloc(dstLen);
    var stream = new AscCommon.FT_Stream2(pointer.data, dstLen);
    stream.obj = pointer.obj;

    var dstPx = stream.data;

    if (window.chrome)
    {
        while (index < srcLen)
        {
            var dwCurr = 0;
            var i;
            var nBits = 0;
            for (i=0; i<4; i++)
            {
                if (index >= srcLen)
                    break;
                var nCh = AscFonts.DecodeBase64Char(szSrc.charCodeAt(index++));
                if (nCh == -1)
                {
                    i--;
                    continue;
                }
                dwCurr <<= 6;
                dwCurr |= nCh;
                nBits += 6;
            }

            dwCurr <<= 24-nBits;
            for (i=0; i<nBits/8; i++)
            {
                dstPx[nWritten++] = ((dwCurr & 0x00ff0000) >>> 16);
                dwCurr <<= 8;
            }
        }
    }
    else
    {
        var p = AscFonts.b64_decode;
        while (index < srcLen)
        {
            var dwCurr = 0;
            var i;
            var nBits = 0;
            for (i=0; i<4; i++)
            {
                if (index >= srcLen)
                    break;
                var nCh = p[szSrc.charCodeAt(index++)];
                if (nCh == undefined)
                {
                    i--;
                    continue;
                }
                dwCurr <<= 6;
                dwCurr |= nCh;
                nBits += 6;
            }

            dwCurr <<= 24-nBits;
            for (i=0; i<nBits/8; i++)
            {
                dstPx[nWritten++] = ((dwCurr & 0x00ff0000) >>> 16);
                dwCurr <<= 8;
            }
        }
    }

    return stream;
};
CCollaborativeChanges.prototype.Internal_Save_Data = function(Class, Data, Binary)
{
    var Writer = AscCommon.History.BinaryWriter;
    var Pos = Binary.Pos;
    var Len = Binary.Len;

    if ( "undefined" != typeof(Class.Save_Changes2) )
    {
        AscCommon.CollaborativeEditing.InitMemory();
        var Writer2 = AscCommon.CollaborativeEditing.m_oMemory;
        Writer2.Seek(0);
        if ( true === Class.Save_Changes2( Data, Writer2 ) )
            return Len + ";" + Writer.GetBase64Memory2(Pos, Len) + ";" + Writer2.GetCurPosition() + ";" + Writer2.GetBase64Memory();
    }

    return Len + ";" + Writer.GetBase64Memory2(Pos, Len);
};




function CCollaborativeEditingBase()
{
    this.m_nUseType     = 1;  // 1 - 1 клиент и мы сохраняем историю, -1 - несколько клиентов, 0 - переход из -1 в 1

    this.m_aUsers       = []; // Список текущих пользователей, редактирующих данный документ
    this.m_aChanges     = []; // Массив с изменениями других пользователей

    this.m_aNeedUnlock  = []; // Массив со списком залоченных объектов(которые были залочены другими пользователями)
    this.m_aNeedUnlock2 = []; // Массив со списком залоченных объектов(которые были залочены на данном клиенте)
    this.m_aNeedLock    = []; // Массив со списком залоченных объектов(которые были залочены, но еще не были добавлены на данном клиенте)

    this.m_aLinkData    = []; // Массив, указателей, которые нам надо выставить при загрузке чужих изменений
    this.m_aEndActions  = []; // Массив действий, которые надо выполнить после принятия чужих изменений


    this.m_bGlobalLock  = false;         // Запрещаем производить любые "редактирующие" действия (т.е. то, что в историю запишется)
    this.m_bGlobalLockSelection = false; // Запрещаем изменять селект и курсор
    this.m_aCheckLocks  = [];    // Массив для проверки залоченности объектов, которые мы собираемся изменять

    this.m_aNewObjects  = []; // Массив со списком чужих новых объектов
    this.m_aNewImages   = []; // Массив со списком картинок, которые нужно будет загрузить на сервере
    this.m_aDC          = {}; // Массив(ассоциативный) классов DocumentContent
    this.m_aChangedClasses = {}; // Массив(ассоциативный) классов, в которых есть изменения выделенные цветом

    this.m_oMemory      = null; // Глобальные класс для сохранения (создадим позднее, когда понадобится)

    this.m_aCursorsToUpdate        = {}; // Курсоры, которые нужно обновить после принятия изменений
    this.m_aCursorsToUpdateShortId = {};

    //// CollaborativeEditing LOG
    //this.m_nErrorLog_PointChangesCount = 0;
    //this.m_nErrorLog_SavedPCC          = 0;
    //this.m_nErrorLog_CurPointIndex     = -1;
    //this.m_nErrorLog_SumIndex          = 0;

    this.m_bFast  = false;

    this.m_oLogicDocument     = null;
    this.m_aDocumentPositions = new CDocumentPositionsManager();
    this.m_aForeignCursorsPos = new CDocumentPositionsManager();
    this.m_aForeignCursors    = {};
    this.m_aForeignCursorsId  = {};
}

CCollaborativeEditingBase.prototype.Clear = function()
{
    this.m_nUseType = 1;

    this.m_aUsers = [];
    this.m_aChanges = [];
    this.m_aNeedUnlock = [];
    this.m_aNeedUnlock2 = [];
    this.m_aNeedLock = [];
    this.m_aLinkData = [];
    this.m_aEndActions = [];
    this.m_aCheckLocks = [];
    this.m_aNewObjects = [];
    this.m_aNewImages = [];
};
CCollaborativeEditingBase.prototype.Set_Fast = function(bFast)
{
    this.m_bFast = bFast;

    if (false === bFast)
        this.Remove_AllForeignCursors();
};
CCollaborativeEditingBase.prototype.Is_Fast = function()
{
    return this.m_bFast;
};
CCollaborativeEditingBase.prototype.Is_SingleUser = function()
{
    if (1 === this.m_nUseType)
        return true;

    return false;
};
CCollaborativeEditingBase.prototype.Start_CollaborationEditing = function()
{
    this.m_nUseType = -1;
};
CCollaborativeEditingBase.prototype.End_CollaborationEditing = function()
{
    if (this.m_nUseType <= 0)
        this.m_nUseType = 0;
};
CCollaborativeEditingBase.prototype.Add_User = function(UserId)
{
    if (-1 === this.Find_User(UserId))
        this.m_aUsers.push(UserId);
};
CCollaborativeEditingBase.prototype.Find_User = function(UserId)
{
    var Len = this.m_aUsers.length;
    for (var Index = 0; Index < Len; Index++)
    {
        if (this.m_aUsers[Index] === UserId)
            return Index;
    }

    return -1;
};
CCollaborativeEditingBase.prototype.Remove_User = function(UserId)
{
    var Pos = this.Find_User( UserId );
    if ( -1 != Pos )
        this.m_aUsers.splice( Pos, 1 );
};
CCollaborativeEditingBase.prototype.Add_Changes = function(Changes)
{
    this.m_aChanges.push(Changes);
};
CCollaborativeEditingBase.prototype.Add_Unlock = function(LockClass)
{
    this.m_aNeedUnlock.push( LockClass );
};
CCollaborativeEditingBase.prototype.Add_Unlock2 = function(Lock)
{
    this.m_aNeedUnlock2.push(Lock);
    editor._onUpdateDocumentCanSave();
};
CCollaborativeEditingBase.prototype.Have_OtherChanges = function()
{
    return (0 < this.m_aChanges.length);
};
CCollaborativeEditingBase.prototype.Apply_Changes = function()
{
    var OtherChanges = (this.m_aChanges.length > 0);

    // Если нет чужих изменений, тогда и делать ничего не надо
    if (true === OtherChanges)
    {
        editor.WordControl.m_oLogicDocument.Stop_Recalculate();
        editor.WordControl.m_oLogicDocument.EndPreview_MailMergeResult();

        editor.sync_StartAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.ApplyChanges);

        var LogicDocument = editor.WordControl.m_oLogicDocument;

        var DocState;
        if (true !== this.Is_Fast())
        {
            DocState = LogicDocument.Get_SelectionState2();
            this.m_aCursorsToUpdate = {};
        }
        else
        {
            DocState = LogicDocument.Save_DocumentStateBeforeLoadChanges();
            this.Clear_DocumentPositions();

            if (DocState.Pos)
                this.Add_DocumentPosition(DocState.Pos);
            if (DocState.StartPos)
                this.Add_DocumentPosition(DocState.StartPos);
            if (DocState.EndPos)
                this.Add_DocumentPosition(DocState.EndPos);
        }

        this.Clear_NewImages();

        this.Apply_OtherChanges();

        // После того как мы приняли чужие изменения, мы должны залочить новые объекты, которые были залочены
        this.Lock_NeedLock();

        if (true !== this.Is_Fast())
        {
            LogicDocument.Set_SelectionState2(DocState);
        }
        else
        {
            if (DocState.Pos)
                this.Update_DocumentPosition(DocState.Pos);
            if (DocState.StartPos)
                this.Update_DocumentPosition(DocState.StartPos);
            if (DocState.EndPos)
                this.Update_DocumentPosition(DocState.EndPos);

            LogicDocument.Load_DocumentStateAfterLoadChanges(DocState);
            this.Refresh_ForeignCursors();
        }

        this.OnStart_Load_Objects();
    }
};
CCollaborativeEditingBase.prototype.Apply_OtherChanges = function()
{
    // Чтобы заново созданные параграфы не отображались залоченными
    AscCommon.g_oIdCounter.Set_Load( true );

    // Применяем изменения, пока они есть
    var _count = this.m_aChanges.length;
    for (var i = 0; i < _count; i++)
    {
        if (window["NATIVE_EDITOR_ENJINE"] === true && window["native"]["CheckNextChange"])
        {
            if (!window["native"]["CheckNextChange"]())
                break;
        }

        var Changes = this.m_aChanges[i];
        Changes.Apply_Data();
        //// CollaborativeEditing LOG
        //this.m_nErrorLog_PointChangesCount++;
    }

    this.m_aChanges = [];

    // У новых элементов выставляем указатели на другие классы
    this.Apply_LinkData();

    // Делаем проверки корректности новых изменений
    this.Check_MergeData();

    this.OnEnd_ReadForeignChanges();

    AscCommon.g_oIdCounter.Set_Load( false );
};
CCollaborativeEditingBase.prototype.getOwnLocksLength = function()
{
    return this.m_aNeedUnlock2.length;
};
CCollaborativeEditingBase.prototype.Send_Changes = function()
{
};
CCollaborativeEditingBase.prototype.Release_Locks = function()
{
};
CCollaborativeEditingBase.prototype.OnStart_Load_Objects = function()
{
    AscCommon.CollaborativeEditing.m_bGlobalLock = true;
    AscCommon.CollaborativeEditing.m_bGlobalLockSelection = true;
    // Вызываем функцию для загрузки необходимых элементов (новые картинки и шрифты)
    editor.pre_Save(AscCommon.CollaborativeEditing.m_aNewImages);
};
CCollaborativeEditingBase.prototype.OnEnd_Load_Objects = function()
{
};
//-----------------------------------------------------------------------------------
// Функции для работы с ссылками, у новых объектов
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Clear_LinkData = function()
{
    this.m_aLinkData.length = 0;
};
CCollaborativeEditingBase.prototype.Add_LinkData = function(Class, LinkData)
{
    this.m_aLinkData.push( { Class : Class, LinkData : LinkData } );
};
CCollaborativeEditingBase.prototype.Apply_LinkData = function()
{
    var Count = this.m_aLinkData.length;
    for ( var Index = 0; Index < Count; Index++ )
    {
        var Item = this.m_aLinkData[Index];
        Item.Class.Load_LinkData( Item.LinkData );
    }

    this.Clear_LinkData();
};
//-----------------------------------------------------------------------------------
// Функции для проверки корректности новых изменений
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Check_MergeData = function()
{
};
//-----------------------------------------------------------------------------------
// Функции для проверки залоченности объектов
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Get_GlobalLock = function()
{
    return this.m_bGlobalLock;
};
CCollaborativeEditingBase.prototype.OnStart_CheckLock = function()
{
    this.m_aCheckLocks.length = 0;
};
CCollaborativeEditingBase.prototype.Add_CheckLock = function(oItem)
{
    this.m_aCheckLocks.push(oItem);
};
CCollaborativeEditingBase.prototype.OnEnd_CheckLock = function()
{
};
CCollaborativeEditingBase.prototype.OnCallback_AskLock = function(result)
{
};
//-----------------------------------------------------------------------------------
// Функции для работы с залоченными объектами, которые еще не были добавлены
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Reset_NeedLock = function()
{
    this.m_aNeedLock = {};
};
CCollaborativeEditingBase.prototype.Add_NeedLock = function(Id, sUser)
{
    this.m_aNeedLock[Id] = sUser;
};
CCollaborativeEditingBase.prototype.Remove_NeedLock = function(Id)
{
    delete this.m_aNeedLock[Id];
};
CCollaborativeEditingBase.prototype.Lock_NeedLock = function()
{
    for ( var Id in this.m_aNeedLock )
    {
        var Class = AscCommon.g_oTableId.Get_ById( Id );

        if ( null != Class )
        {
            var Lock = Class.Lock;
            Lock.Set_Type( AscCommon.locktype_Other, false );
            if(Class.getObjectType && Class.getObjectType() === AscDFH.historyitem_type_Slide)
            {
                editor.WordControl.m_oLogicDocument.DrawingDocument.UnLockSlide && editor.WordControl.m_oLogicDocument.DrawingDocument.UnLockSlide(Class.num);
            }
            Lock.Set_UserId( this.m_aNeedLock[Id] );
        }
    }

    this.Reset_NeedLock();
};
//-----------------------------------------------------------------------------------
// Функции для работы с новыми объектами, созданными на других клиентах
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Clear_NewObjects = function()
{
    this.m_aNewObjects.length = 0;
};
CCollaborativeEditingBase.prototype.Add_NewObject = function(Class)
{
    this.m_aNewObjects.push(Class);
    Class.FromBinary = true;
};
CCollaborativeEditingBase.prototype.Clear_EndActions = function()
{
    this.m_aEndActions.length = 0;
};
CCollaborativeEditingBase.prototype.Add_EndActions = function(Class, Data)
{
    this.m_aEndActions.push({Class : Class, Data : Data});
};
CCollaborativeEditingBase.prototype.OnEnd_ReadForeignChanges = function()
{
    var Count = this.m_aNewObjects.length;

    for (var Index = 0; Index < Count; Index++)
    {
        var Class = this.m_aNewObjects[Index];
        Class.FromBinary = false;
    }

    Count = this.m_aEndActions.length;
    for (var Index = 0; Index < Count; Index++)
    {
        var Item = this.m_aEndActions[Index];
        Item.Class.Process_EndLoad(Item.Data);
    }

    this.Clear_EndActions();
    this.Clear_NewObjects();
};
//-----------------------------------------------------------------------------------
// Функции для работы с новыми объектами, созданными на других клиентах
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Clear_NewImages = function()
{
    this.m_aNewImages.length = 0;
};
CCollaborativeEditingBase.prototype.Add_NewImage = function(Url)
{
    this.m_aNewImages.push( Url );
};
//-----------------------------------------------------------------------------------
// Функции для работы с массивом m_aDC
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Add_NewDC = function(Class)
{
    var Id = Class.Get_Id();
    this.m_aDC[Id] = Class;
};
CCollaborativeEditingBase.prototype.Clear_DCChanges = function()
{
    for (var Id in this.m_aDC)
    {
        this.m_aDC[Id].Clear_ContentChanges();
    }

    // Очищаем массив
    this.m_aDC = {};
};
CCollaborativeEditingBase.prototype.Refresh_DCChanges = function()
{
    for (var Id in this.m_aDC)
    {
        this.m_aDC[Id].Refresh_ContentChanges();
    }

    this.Clear_DCChanges();
};
//-----------------------------------------------------------------------------------
// Функции для работы с отметками изменений
//-----------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Add_ChangedClass = function(Class)
{
    var Id = Class.Get_Id();
    this.m_aChangedClasses[Id] = Class;
};
CCollaborativeEditingBase.prototype.Clear_CollaborativeMarks = function(bRepaint)
{
    for ( var Id in this.m_aChangedClasses )
    {
        this.m_aChangedClasses[Id].Clear_CollaborativeMarks();
    }

    // Очищаем массив
    this.m_aChangedClasses = {};


    if (true === bRepaint)
    {
        editor.WordControl.m_oLogicDocument.DrawingDocument.ClearCachePages();
        editor.WordControl.m_oLogicDocument.DrawingDocument.FirePaint();
    }
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с обновлением курсоров после принятия изменений
//----------------------------------------------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Add_ForeignCursorToUpdate = function(UserId, CursorInfo, UserShortId)
{
    this.m_aCursorsToUpdate[UserId] = CursorInfo;
    this.m_aCursorsToUpdateShortId[UserId] = UserShortId;
};
CCollaborativeEditingBase.prototype.Refresh_ForeignCursors = function()
{
    if (!this.m_oLogicDocument)
        return;

    for (var UserId in this.m_aCursorsToUpdate)
    {
        var CursorInfo = this.m_aCursorsToUpdate[UserId];
        this.m_oLogicDocument.Update_ForeignCursor(CursorInfo, UserId, false, this.m_aCursorsToUpdateShortId[UserId]);

        if (this.Add_ForeignCursorToShow)
            this.Add_ForeignCursorToShow(UserId);
    }
    this.m_aCursorsToUpdate = {};
    this.m_aCursorsToUpdateShortId = {};
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с сохраненными позициями в Word-документах. Они объявлены в базовом классе, потому что вызываются
// из общих классов Paragraph, Run, Table. Вообщем, для совместимости.
//----------------------------------------------------------------------------------------------------------------------
CCollaborativeEditingBase.prototype.Clear_DocumentPositions = function(){
    this.m_aDocumentPositions.Clear_DocumentPositions();
};
CCollaborativeEditingBase.prototype.Add_DocumentPosition = function(DocumentPos){
    this.m_aDocumentPositions.Add_DocumentPosition(DocumentPos);
};
CCollaborativeEditingBase.prototype.Add_ForeignCursor = function(UserId, DocumentPos, UserShortId){
    this.m_aForeignCursorsPos.Remove_DocumentPosition(this.m_aCursorsToUpdate[UserId]);
    this.m_aForeignCursors[UserId] = DocumentPos;
    this.m_aForeignCursorsPos.Add_DocumentPosition(DocumentPos);
    this.m_aForeignCursorsId[UserId] = UserShortId;
};
CCollaborativeEditingBase.prototype.Remove_ForeignCursor = function(UserId){
    this.m_aForeignCursorsPos.Remove_DocumentPosition(this.m_aCursorsToUpdate[UserId]);
    delete this.m_aForeignCursors[UserId];
};
CCollaborativeEditingBase.prototype.Remove_AllForeignCursors = function(){};
CCollaborativeEditingBase.prototype.Update_DocumentPositionsOnAdd = function(Class, Pos){
    this.m_aDocumentPositions.Update_DocumentPositionsOnAdd(Class, Pos);
    this.m_aForeignCursorsPos.Update_DocumentPositionsOnAdd(Class, Pos);
};
CCollaborativeEditingBase.prototype.Update_DocumentPositionsOnRemove = function(Class, Pos, Count){
    this.m_aDocumentPositions.Update_DocumentPositionsOnRemove(Class, Pos, Count);
    this.m_aForeignCursorsPos.Update_DocumentPositionsOnRemove(Class, Pos, Count);
};
CCollaborativeEditingBase.prototype.OnStart_SplitRun = function(SplitRun, SplitPos){
    this.m_aDocumentPositions.OnStart_SplitRun(SplitRun, SplitPos);
    this.m_aForeignCursorsPos.OnStart_SplitRun(SplitRun, SplitPos);
};
CCollaborativeEditingBase.prototype.OnEnd_SplitRun = function(NewRun){
    this.m_aDocumentPositions.OnEnd_SplitRun(NewRun);
    this.m_aForeignCursorsPos.OnEnd_SplitRun(NewRun);
};
CCollaborativeEditingBase.prototype.Update_DocumentPosition = function(DocPos){
    this.m_aDocumentPositions.Update_DocumentPosition(DocPos);
};
CCollaborativeEditingBase.prototype.Update_ForeignCursorsPositions = function(){

};
CCollaborativeEditingBase.prototype.InitMemory = function() {
    if (!this.m_oMemory) {
        this.m_oMemory = new AscCommon.CMemory();
    }
};


//----------------------------------------------------------------------------------------------------------------------
// Класс для работы с сохраненными позициями документа.
//----------------------------------------------------------------------------------------------------------------------
//   Принцип следующий. Заданная позиция - это Run + Позиция внутри данного Run.
//   Если заданный ран был разбит (операция Split), тогда отслеживаем куда перешла
//   заданная позиция, в новый ран или осталась в старом? Если в новый, тогда сохраняем
//   новый ран как отдельную позицию в массив m_aDocumentPositions, и добавляем мап
//   старой позиции в новую m_aDocumentPositionsMap. В конце действия, когда нам нужно
//   определить где же находистся наша позиция, мы сначала проверяем Map, если в нем есть
//   конечная позиция, проверяем является ли заданная позиция валидной в документе.
//   Если да, тогда выставляем ее, если нет, тогда берем Run исходной позиции, и
//   пытаемся сформировать полную позицию по данному Run. Если и это не получается,
//   тогда восстанавливаем позицию по измененной полной исходной позиции.
//----------------------------------------------------------------------------------------------------------------------
function CDocumentPositionsManager()
{
    this.m_aDocumentPositions      = [];
    this.m_aDocumentPositionsSplit = [];
    this.m_aDocumentPositionsMap   = [];
}
CDocumentPositionsManager.prototype.Clear_DocumentPositions = function()
{
    this.m_aDocumentPositions      = [];
    this.m_aDocumentPositionsSplit = [];
    this.m_aDocumentPositionsMap   = [];
};
CDocumentPositionsManager.prototype.Add_DocumentPosition = function(Position)
{
    this.m_aDocumentPositions.push(Position);
};
CDocumentPositionsManager.prototype.Update_DocumentPositionsOnAdd = function(Class, Pos)
{
    for (var PosIndex = 0, PosCount = this.m_aDocumentPositions.length; PosIndex < PosCount; ++PosIndex)
    {
        var DocPos = this.m_aDocumentPositions[PosIndex];
        for (var ClassPos = 0, ClassLen = DocPos.length; ClassPos < ClassLen; ++ClassPos)
        {
            var _Pos = DocPos[ClassPos];
            if (Class === _Pos.Class && _Pos.Position && _Pos.Position >= Pos)
            {
                _Pos.Position++;
                break;
            }
        }
    }
};
CDocumentPositionsManager.prototype.Update_DocumentPositionsOnRemove = function(Class, Pos, Count)
{
    for (var PosIndex = 0, PosCount = this.m_aDocumentPositions.length; PosIndex < PosCount; ++PosIndex)
    {
        var DocPos = this.m_aDocumentPositions[PosIndex];
        for (var ClassPos = 0, ClassLen = DocPos.length; ClassPos < ClassLen; ++ClassPos)
        {
            var _Pos = DocPos[ClassPos];
            if (Class === _Pos.Class && _Pos.Position)
            {
                if (_Pos.Position > Pos + Count)
                {
                    _Pos.Position -= Count;
                }
                else if (_Pos.Position >= Pos)
                {
                    // Элемент, в котором находится наша позиция, удаляется. Ставим специальную отметку об этом.
                    _Pos.Position = Pos;
                    _Pos.Deleted = true;
                }

                break;
            }
        }
    }
};
CDocumentPositionsManager.prototype.OnStart_SplitRun = function(SplitRun, SplitPos)
{
    this.m_aDocumentPositionsSplit = [];

    for (var PosIndex = 0, PosCount = this.m_aDocumentPositions.length; PosIndex < PosCount; ++PosIndex)
    {
        var DocPos = this.m_aDocumentPositions[PosIndex];
        for (var ClassPos = 0, ClassLen = DocPos.length; ClassPos < ClassLen; ++ClassPos)
        {
            var _Pos = DocPos[ClassPos];
            if (SplitRun === _Pos.Class && _Pos.Position && _Pos.Position >= SplitPos)
            {
                this.m_aDocumentPositionsSplit.push({DocPos : DocPos, NewRunPos : _Pos.Position - SplitPos});
            }
        }
    }
};
CDocumentPositionsManager.prototype.OnEnd_SplitRun = function(NewRun)
{
    if (!NewRun)
        return;

    for (var PosIndex = 0, PosCount = this.m_aDocumentPositionsSplit.length; PosIndex < PosCount; ++PosIndex)
    {
        var NewDocPos = [];
        NewDocPos.push({Class : NewRun, Position : this.m_aDocumentPositionsSplit[PosIndex].NewRunPos});
        this.m_aDocumentPositions.push(NewDocPos);
        this.m_aDocumentPositionsMap.push({StartPos : this.m_aDocumentPositionsSplit[PosIndex].DocPos, EndPos : NewDocPos});
    }
};
CDocumentPositionsManager.prototype.Update_DocumentPosition = function(DocPos)
{
    // Смотрим куда мапится заданная позиция
    var NewDocPos = DocPos;
    for (var PosIndex = 0, PosCount = this.m_aDocumentPositionsMap.length; PosIndex < PosCount; ++PosIndex)
    {
        if (this.m_aDocumentPositionsMap[PosIndex].StartPos === NewDocPos)
            NewDocPos = this.m_aDocumentPositionsMap[PosIndex].EndPos;
    }

    // Нашли результирующую позицию. Проверим является ли она валидной для документа.
    if (NewDocPos !== DocPos && NewDocPos.length === 1 && NewDocPos[0].Class instanceof AscCommonWord.ParaRun)
    {
        var Run = NewDocPos[0].Class;
        var Para = Run.Get_Paragraph();
        if (AscCommonWord.CanUpdatePosition(Para, Run))
        {
            DocPos.length = 0;
            DocPos.push({Class : Run, Position : NewDocPos[0].Position});
            Run.Get_DocumentPositionFromObject(DocPos);
        }
    }
    // Возможно ран с позицией переместился в другой класс
    else if (DocPos.length > 0 && DocPos[DocPos.length - 1].Class instanceof AscCommonWord.ParaRun)
    {
        var Run = DocPos[DocPos.length - 1].Class;
        var RunPos = DocPos[DocPos.length - 1].Position;
        var Para = Run.Get_Paragraph();
        if (AscCommonWord.CanUpdatePosition(Para, Run))
        {
            DocPos.length = 0;
            DocPos.push({Class : Run, Position : RunPos});
            Run.Get_DocumentPositionFromObject(DocPos);
        }
    }
};
CDocumentPositionsManager.prototype.Remove_DocumentPosition = function(DocPos)
{
    for (var Pos = 0, Count = this.m_aDocumentPositions.length; Pos < Count; ++Pos)
    {
        if (this.m_aDocumentPositions[Pos] === DocPos)
        {
            this.m_aDocumentPositions.splice(Pos, 1);
            return;
        }
    }
};

    //--------------------------------------------------------export----------------------------------------------------
    window['AscCommon'] = window['AscCommon'] || {};
    window['AscCommon'].FOREIGN_CURSOR_LABEL_HIDETIME = FOREIGN_CURSOR_LABEL_HIDETIME;
    window['AscCommon'].CCollaborativeChanges = CCollaborativeChanges;
    window['AscCommon'].CCollaborativeEditingBase = CCollaborativeEditingBase;
    window['AscCommon'].CDocumentPositionsManager = CDocumentPositionsManager;
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

/**
 *
 * @constructor
 * @extends {AscCommon.CCollaborativeEditingBase}
 */
function CWordCollaborativeEditing()
{
    CWordCollaborativeEditing.superclass.constructor.call(this);

    this.m_oLogicDocument        = null;
    this.m_aDocumentPositions    = new AscCommon.CDocumentPositionsManager();
    this.m_aForeignCursorsPos    = new AscCommon.CDocumentPositionsManager();
    this.m_aForeignCursors       = {};
    this.m_aForeignCursorsXY     = {};
    this.m_aForeignCursorsToShow = {};
}

AscCommon.extendClass(CWordCollaborativeEditing, AscCommon.CCollaborativeEditingBase);

CWordCollaborativeEditing.prototype.Send_Changes = function(IsUserSave, AdditionalInfo, IsUpdateInterface)
{
    // Пересчитываем позиции
    this.Refresh_DCChanges();

    // Генерируем свои изменения
    var StartPoint = ( null === AscCommon.History.SavedIndex ? 0 : AscCommon.History.SavedIndex + 1 );
    var LastPoint = -1;

    if (this.m_nUseType <= 0)
    {
        // (ненужные точки предварительно удаляем)
        AscCommon.History.Clear_Redo();
        LastPoint = AscCommon.History.Points.length - 1;
    }
    else
    {
        LastPoint = AscCommon.History.Index;
    }

    // Просчитаем сколько изменений на сервер пересылать не надо
    var SumIndex = 0;
    var StartPoint2 = Math.min(StartPoint, LastPoint + 1);
    for (var PointIndex = 0; PointIndex < StartPoint2; PointIndex++)
    {
        var Point = AscCommon.History.Points[PointIndex];
        SumIndex += Point.Items.length;
    }
    var deleteIndex = ( null === AscCommon.History.SavedIndex ? null : SumIndex );

    var aChanges = [];
    for (var PointIndex = StartPoint; PointIndex <= LastPoint; PointIndex++)
    {
        var Point = AscCommon.History.Points[PointIndex];
        AscCommon.History.Update_PointInfoItem(PointIndex, StartPoint, LastPoint, SumIndex, deleteIndex);

        for (var Index = 0; Index < Point.Items.length; Index++)
        {
            var Item = Point.Items[Index];
            var oChanges = new AscCommon.CCollaborativeChanges();
            oChanges.Set_FromUndoRedo(Item.Class, Item.Data, Item.Binary);
            aChanges.push(oChanges.m_pData);
        }
    }

    var UnlockCount = this.m_aNeedUnlock.length;
    this.Release_Locks();

    var UnlockCount2 = this.m_aNeedUnlock2.length;
    for (var Index = 0; Index < UnlockCount2; Index++)
    {
        var Class = this.m_aNeedUnlock2[Index];
        Class.Lock.Set_Type(AscCommon.locktype_None, false);
        editor.CoAuthoringApi.releaseLocks(Class.Get_Id());
    }

    this.m_aNeedUnlock.length = 0;
    this.m_aNeedUnlock2.length = 0;

    var deleteIndex = ( null === AscCommon.History.SavedIndex ? null : SumIndex );
    if (0 < aChanges.length || null !== deleteIndex) {
        editor.CoAuthoringApi.saveChanges(aChanges, deleteIndex, AdditionalInfo);
        AscCommon.History.CanNotAddChanges = true;
    } else
        editor.CoAuthoringApi.unLockDocument(true);

    if (-1 === this.m_nUseType)
    {
        // Чистим Undo/Redo только во время совместного редактирования
        AscCommon.History.Clear();
        AscCommon.History.SavedIndex = null;
    }
    else if (0 === this.m_nUseType)
    {
        // Чистим Undo/Redo только во время совместного редактирования
        AscCommon.History.Clear();
        AscCommon.History.SavedIndex = null;

        this.m_nUseType = 1;
    }
    else
    {
        // Обновляем точку последнего сохранения в истории
        AscCommon.History.Reset_SavedIndex(IsUserSave);
    }

    if (false !== IsUpdateInterface)
    {
        // Обновляем интерфейс
        editor.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
    }

    // TODO: Пока у нас обнуляется история на сохранении нужно обновлять Undo/Redo
    editor.WordControl.m_oLogicDocument.Document_UpdateUndoRedoState();

    // Свои локи не проверяем. Когда все пользователи выходят, происходит перерисовка и свои локи уже не рисуются.
    if (0 !== UnlockCount || 1 !== this.m_nUseType)
    {
        // Перерисовываем документ (для обновления локов)
        editor.WordControl.m_oLogicDocument.DrawingDocument.ClearCachePages();
        editor.WordControl.m_oLogicDocument.DrawingDocument.FirePaint();
    }
};
CWordCollaborativeEditing.prototype.Release_Locks = function()
{
    var UnlockCount = this.m_aNeedUnlock.length;
    for (var Index = 0; Index < UnlockCount; Index++)
    {
        var CurLockType = this.m_aNeedUnlock[Index].Lock.Get_Type();
        if (AscCommon.locktype_Other3 != CurLockType && AscCommon.locktype_Other != CurLockType)
        {
            this.m_aNeedUnlock[Index].Lock.Set_Type(AscCommon.locktype_None, false);

            if (this.m_aNeedUnlock[Index] instanceof AscCommonWord.CHeaderFooterController)
                editor.sync_UnLockHeaderFooters();
            else if (this.m_aNeedUnlock[Index] instanceof AscCommonWord.CDocument)
                editor.sync_UnLockDocumentProps();
            else if (this.m_aNeedUnlock[Index] instanceof AscCommon.CComment)
                editor.sync_UnLockComment(this.m_aNeedUnlock[Index].Get_Id());
            else if (this.m_aNeedUnlock[Index] instanceof AscCommonWord.CGraphicObjects)
                editor.sync_UnLockDocumentSchema();
        }
        else if (AscCommon.locktype_Other3 === CurLockType)
        {
            this.m_aNeedUnlock[Index].Lock.Set_Type(AscCommon.locktype_Other, false);
        }
    }
};
CWordCollaborativeEditing.prototype.OnEnd_Load_Objects = function()
{
    // Данная функция вызывается, когда загрузились внешние объекты (картинки и шрифты)

    // Снимаем лок
    AscCommon.CollaborativeEditing.m_bGlobalLock = false;
    AscCommon.CollaborativeEditing.m_bGlobalLockSelection = false;

    // Запускаем полный пересчет документа
    var LogicDocument = editor.WordControl.m_oLogicDocument;

    var RecalculateData =
    {
        Inline   : { Pos : 0, PageNum : 0 },
        Flow     : [],
        HdrFtr   : [],
        Drawings : {
            All : true,
            Map : {}
        }
    };

    LogicDocument.Reset_RecalculateCache();

    LogicDocument.Recalculate(false, false, RecalculateData);
    LogicDocument.Document_UpdateSelectionState();
    LogicDocument.Document_UpdateInterfaceState();

    editor.sync_EndAction(Asc.c_oAscAsyncActionType.BlockInteraction, Asc.c_oAscAsyncAction.ApplyChanges);
};
CWordCollaborativeEditing.prototype.Check_MergeData = function()
{
    var LogicDocument = editor.WordControl.m_oLogicDocument;
    LogicDocument.Comments.Check_MergeData();
};
CWordCollaborativeEditing.prototype.OnStart_CheckLock = function()
{
    this.m_aCheckLocks.length = 0;
};
CWordCollaborativeEditing.prototype.Add_CheckLock = function(oItem)
{
    this.m_aCheckLocks.push(oItem);
};
CWordCollaborativeEditing.prototype.OnEnd_CheckLock = function(DontLockInFastMode)
{
    var aIds = [];

    var Count = this.m_aCheckLocks.length;
    for (var Index = 0; Index < Count; Index++)
    {
        var oItem = this.m_aCheckLocks[Index];

        if (true === oItem) // сравниваем по значению и типу обязательно
            return true;
        else if (false !== oItem)
            aIds.push(oItem);
    }

    if (true === DontLockInFastMode && true === this.Is_Fast())
        return false;

    if (aIds.length > 0)
    {
        // Отправляем запрос на сервер со списком Id
        editor.CoAuthoringApi.askLock(aIds, this.OnCallback_AskLock);

        // Ставим глобальный лок, только во время совместного редактирования
        if (-1 === this.m_nUseType)
            this.m_bGlobalLock = true;
        else
        {
            // Пробегаемся по массиву и проставляем, что залочено нами
            var Count = this.m_aCheckLocks.length;
            for (var Index = 0; Index < Count; Index++)
            {
                var oItem = this.m_aCheckLocks[Index];

                if (true !== oItem && false !== oItem) // сравниваем по значению и типу обязательно
                {
                    var Class = AscCommon.g_oTableId.Get_ById(oItem);
                    if (null != Class)
                    {
                        Class.Lock.Set_Type(AscCommon.locktype_Mine, false);
                        this.Add_Unlock2(Class);
                    }
                }
            }

            this.m_aCheckLocks.length = 0;
        }
    }

    return false;
};
CWordCollaborativeEditing.prototype.OnCallback_AskLock = function(result)
{
    var oThis   = AscCommon.CollaborativeEditing;
    var oEditor = editor;

    if (true === oThis.m_bGlobalLock)
    {
        // Здесь проверяем есть ли длинная операция, если она есть, то до ее окончания нельзя делать
        // Undo, иначе точка истории уберется, а изменения допишутся в предыдущую.
        if (false == oEditor.checkLongActionCallback(oThis.OnCallback_AskLock, result))
            return;

        // Снимаем глобальный лок
        oThis.m_bGlobalLock = false;

        if (result["lock"])
        {
            // Пробегаемся по массиву и проставляем, что залочено нами

            var Count = oThis.m_aCheckLocks.length;
            for (var Index = 0; Index < Count; Index++)
            {
                var oItem = oThis.m_aCheckLocks[Index];

                if (true !== oItem && false !== oItem) // сравниваем по значению и типу обязательно
                {
                    var Class = AscCommon.g_oTableId.Get_ById(oItem);
                    if (null != Class)
                    {
                        Class.Lock.Set_Type(AscCommon.locktype_Mine);
                        oThis.Add_Unlock2(Class);
                    }
                }
            }
        }
        else if (result["error"])
        {
            // Если у нас началось редактирование диаграммы, а вернулось, что ее редактировать нельзя,
            // посылаем сообщение о закрытии редактора диаграмм.
            if (true === oEditor.isChartEditor)
                oEditor.sync_closeChartEditor();

            // Делаем откат на 1 шаг назад и удаляем из Undo/Redo эту последнюю точку
            oEditor.WordControl.m_oLogicDocument.Document_Undo();
            AscCommon.History.Clear_Redo();
        }

        oEditor.isChartEditor = false;
    }
};
//----------------------------------------------------------------------------------------------------------------------
// Функции для работы с сохраненными позициями документа.
//----------------------------------------------------------------------------------------------------------------------
CWordCollaborativeEditing.prototype.Clear_DocumentPositions = function()
{
    this.m_aDocumentPositions.Clear_DocumentPositions();
};
CWordCollaborativeEditing.prototype.Add_DocumentPosition = function(DocumentPos)
{
    this.m_aDocumentPositions.Add_DocumentPosition(DocumentPos);
};
CWordCollaborativeEditing.prototype.Add_ForeignCursor = function(UserId, DocumentPos, UserShortId)
{
    this.m_aForeignCursorsPos.Remove_DocumentPosition(this.m_aCursorsToUpdate[UserId]);
    this.m_aForeignCursors[UserId] = DocumentPos;
    this.m_aForeignCursorsPos.Add_DocumentPosition(DocumentPos);
    this.m_aForeignCursorsId[UserId] = UserShortId;
};
CWordCollaborativeEditing.prototype.Remove_ForeignCursor = function(UserId)
{
    this.m_aForeignCursorsPos.Remove_DocumentPosition(this.m_aCursorsToUpdate[UserId]);
    delete this.m_aForeignCursors[UserId];

    var DrawingDocument = this.m_oLogicDocument.DrawingDocument;
    DrawingDocument.Collaborative_RemoveTarget(UserId);
    this.Remove_ForeignCursorXY(UserId);
    this.Remove_ForeignCursorToShow(UserId);
};
CWordCollaborativeEditing.prototype.Remove_AllForeignCursors = function()
{
    for (var UserId in this.m_aForeignCursors)
    {
        this.Remove_ForeignCursor(UserId);
    }
};
CWordCollaborativeEditing.prototype.Update_DocumentPositionsOnAdd = function(Class, Pos)
{
    this.m_aDocumentPositions.Update_DocumentPositionsOnAdd(Class, Pos);
    this.m_aForeignCursorsPos.Update_DocumentPositionsOnAdd(Class, Pos);
};
CWordCollaborativeEditing.prototype.Update_DocumentPositionsOnRemove = function(Class, Pos, Count)
{
    this.m_aDocumentPositions.Update_DocumentPositionsOnRemove(Class, Pos, Count);
    this.m_aForeignCursorsPos.Update_DocumentPositionsOnRemove(Class, Pos, Count);
};
CWordCollaborativeEditing.prototype.OnStart_SplitRun = function(SplitRun, SplitPos)
{
    this.m_aDocumentPositions.OnStart_SplitRun(SplitRun, SplitPos);
    this.m_aForeignCursorsPos.OnStart_SplitRun(SplitRun, SplitPos);
};
CWordCollaborativeEditing.prototype.OnEnd_SplitRun = function(NewRun)
{
    this.m_aDocumentPositions.OnEnd_SplitRun(NewRun);
    this.m_aForeignCursorsPos.OnEnd_SplitRun(NewRun);
};
CWordCollaborativeEditing.prototype.Update_DocumentPosition = function(DocPos)
{
    this.m_aDocumentPositions.Update_DocumentPosition(DocPos);
};
CWordCollaborativeEditing.prototype.Update_ForeignCursorsPositions = function()
{
    for (var UserId in this.m_aForeignCursors)
    {
        var DocPos = this.m_aForeignCursors[UserId];
        if (!DocPos || DocPos.length <= 0)
            continue;

        this.m_aForeignCursorsPos.Update_DocumentPosition(DocPos);

        var Run      = DocPos[DocPos.length - 1].Class;
        var InRunPos = DocPos[DocPos.length - 1].Position;

        this.Update_ForeignCursorPosition(UserId, Run, InRunPos, false);
    }
};
CWordCollaborativeEditing.prototype.Update_ForeignCursorPosition = function(UserId, Run, InRunPos, isRemoveLabel)
{
    var DrawingDocument = this.m_oLogicDocument.DrawingDocument;

    if (!(Run instanceof AscCommonWord.ParaRun))
        return;

    var Paragraph = Run.Get_Paragraph();

    if (!Paragraph)
    {
        DrawingDocument.Collaborative_RemoveTarget(UserId);
        return;
    }

    var ParaContentPos = Paragraph.Get_PosByElement(Run);
    if (!ParaContentPos)
    {
        DrawingDocument.Collaborative_RemoveTarget(UserId);
        return;
    }
    ParaContentPos.Update(InRunPos, ParaContentPos.Get_Depth() + 1);

    var XY = Paragraph.Get_XYByContentPos(ParaContentPos);
    if (XY && XY.Height > 0.001)
    {
        var ShortId = this.m_aForeignCursorsId[UserId] ? this.m_aForeignCursorsId[UserId] : UserId;
        DrawingDocument.Collaborative_UpdateTarget(UserId, ShortId, XY.X, XY.Y, XY.Height, XY.PageNum, Paragraph.Get_ParentTextTransform());
        this.Add_ForeignCursorXY(UserId, XY.X, XY.Y, XY.PageNum, XY.Height, Paragraph, isRemoveLabel);

        if (true === this.m_aForeignCursorsToShow[UserId])
        {
            this.Show_ForeignCursorLabel(UserId);
            this.Remove_ForeignCursorToShow(UserId);
        }
    }
    else
    {
        DrawingDocument.Collaborative_RemoveTarget(UserId);
        this.Remove_ForeignCursorXY(UserId);
        this.Remove_ForeignCursorToShow(UserId);
    }
};
CWordCollaborativeEditing.prototype.Check_ForeignCursorsLabels = function(X, Y, PageIndex)
{
    if (!this.m_oLogicDocument)
        return;

    var DrawingDocument = this.m_oLogicDocument.Get_DrawingDocument();
    var Px7 = DrawingDocument.GetMMPerDot(7);
    var Px3 = DrawingDocument.GetMMPerDot(3);

    for (var UserId in this.m_aForeignCursorsXY)
    {
        var Cursor = this.m_aForeignCursorsXY[UserId];
        if ((true === Cursor.Transform && Cursor.PageIndex === PageIndex && Cursor.X0 - Px3 < X && X < Cursor.X1 + Px3 && Cursor.Y0 - Px3 < Y && Y < Cursor.Y1 + Px3)
            || (Math.abs(X - Cursor.X) < Px7 && Cursor.Y - Px3 < Y && Y < Cursor.Y + Cursor.H + Px3 && Cursor.PageIndex === PageIndex))
        {
                this.Show_ForeignCursorLabel(UserId);
        }
    }
};
CWordCollaborativeEditing.prototype.Show_ForeignCursorLabel = function(UserId)
{
    if (!this.m_oLogicDocument)
        return;

    var Api = this.m_oLogicDocument.Get_Api();
    var DrawingDocument = this.m_oLogicDocument.Get_DrawingDocument();

    if (!this.m_aForeignCursorsXY[UserId])
        return;

    var Cursor = this.m_aForeignCursorsXY[UserId];
    if (Cursor.ShowId)
        clearTimeout(Cursor.ShowId);

    Cursor.ShowId = setTimeout(function()
    {
        Cursor.ShowId = null;
        Api.sync_HideForeignCursorLabel(UserId);
    }, AscCommon.FOREIGN_CURSOR_LABEL_HIDETIME);

    var UserShortId = this.m_aForeignCursorsId[UserId] ? this.m_aForeignCursorsId[UserId] : UserId;
    var Color  = AscCommon.getUserColorById(UserShortId, null, true);
    var Coords = DrawingDocument.Collaborative_GetTargetPosition(UserId);
    if (!Color || !Coords)
        return;

    this.Update_ForeignCursorLabelPosition(UserId, Coords.X, Coords.Y, Color);
};
CWordCollaborativeEditing.prototype.Add_ForeignCursorToShow = function(UserId)
{
    this.m_aForeignCursorsToShow[UserId] = true;
};
CWordCollaborativeEditing.prototype.Remove_ForeignCursorToShow = function(UserId)
{
    delete this.m_aForeignCursorsToShow[UserId];
};
CWordCollaborativeEditing.prototype.Add_ForeignCursorXY = function(UserId, X, Y, PageIndex, H, Paragraph, isRemoveLabel)
{
    var Cursor;
    if (!this.m_aForeignCursorsXY[UserId])
    {
        Cursor = {X: X, Y: Y, H: H, PageIndex: PageIndex, Transform: false, ShowId: null};
        this.m_aForeignCursorsXY[UserId] = Cursor;
    }
    else
    {
        Cursor = this.m_aForeignCursorsXY[UserId];
        if (Cursor.ShowId)
        {
            if (true === isRemoveLabel)
            {
                var Api = this.m_oLogicDocument.Get_Api();
                clearTimeout(Cursor.ShowId);
                Cursor.ShowId = null;
                Api.sync_HideForeignCursorLabel(UserId);
            }
        }
        else
        {
            Cursor.ShowId = null;
        }

        Cursor.X         = X;
        Cursor.Y         = Y;
        Cursor.PageIndex = PageIndex;
        Cursor.H         = H;
    }

    var Transform = Paragraph.Get_ParentTextTransform();
    if (Transform)
    {
        Cursor.Transform = true;
        var X0 = Transform.TransformPointX(Cursor.X, Cursor.Y);
        var Y0 = Transform.TransformPointY(Cursor.X, Cursor.Y);
        var X1 = Transform.TransformPointX(Cursor.X, Cursor.Y + Cursor.H);
        var Y1 = Transform.TransformPointY(Cursor.X, Cursor.Y + Cursor.H);

        Cursor.X0 = Math.min(X0, X1);
        Cursor.Y0 = Math.min(Y0, Y1);
        Cursor.X1 = Math.max(X0, X1);
        Cursor.Y1 = Math.max(Y0, Y1);
    }
    else
    {
        Cursor.Transform = false;
    }

};
CWordCollaborativeEditing.prototype.Remove_ForeignCursorXY = function(UserId)
{
    if (this.m_aForeignCursorsXY[UserId])
    {
        if (this.m_aForeignCursorsXY[UserId].ShowId)
        {
            var Api = this.m_oLogicDocument.Get_Api();
            Api.sync_HideForeignCursorLabel(UserId);
            clearTimeout(this.m_aForeignCursorsXY[UserId].ShowId);
        }

        delete this.m_aForeignCursorsXY[UserId];
    }
};
CWordCollaborativeEditing.prototype.Update_ForeignCursorLabelPosition = function(UserId, X, Y, Color)
{
    if (!this.m_oLogicDocument)
        return;

    var Cursor = this.m_aForeignCursorsXY[UserId];
    if (!Cursor || !Cursor.ShowId)
        return;

    var Api = this.m_oLogicDocument.Get_Api();
    Api.sync_ShowForeignCursorLabel(UserId, X, Y, Color);
};

//--------------------------------------------------------export----------------------------------------------------
window['AscCommon'] = window['AscCommon'] || {};
window['AscCommon'].CWordCollaborativeEditing = CWordCollaborativeEditing;
window['AscCommon'].CollaborativeEditing = new CWordCollaborativeEditing();

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

(function(window, document)
{

	// Import
	var g_fontApplication = null;

	var c_oAscAdvancedOptionsAction      = AscCommon.c_oAscAdvancedOptionsAction;
	var DownloadType                     = AscCommon.DownloadType;
	var c_oAscFormatPainterState         = AscCommon.c_oAscFormatPainterState;
	var locktype_None                    = AscCommon.locktype_None;
	var locktype_Mine                    = AscCommon.locktype_Mine;
	var locktype_Other                   = AscCommon.locktype_Other;
	var locktype_Other2                  = AscCommon.locktype_Other2;
	var locktype_Other3                  = AscCommon.locktype_Other3;
	var changestype_None                 = AscCommon.changestype_None;
	var changestype_Paragraph_Content    = AscCommon.changestype_Paragraph_Content;
	var changestype_Paragraph_Properties = AscCommon.changestype_Paragraph_Properties;
	var changestype_Table_Properties     = AscCommon.changestype_Table_Properties;
	var changestype_Table_RemoveCells    = AscCommon.changestype_Table_RemoveCells;
	var changestype_HdrFtr               = AscCommon.changestype_HdrFtr;
	var asc_CTextFontFamily              = AscCommon.asc_CTextFontFamily;
	var asc_CSelectedObject              = AscCommon.asc_CSelectedObject;
	var g_oDocumentUrls                  = AscCommon.g_oDocumentUrls;
	var sendCommand                      = AscCommon.sendCommand;
	var mapAscServerErrorToAscError      = AscCommon.mapAscServerErrorToAscError;
	var g_oIdCounter                     = AscCommon.g_oIdCounter;
	var g_oTableId                       = AscCommon.g_oTableId;
	var PasteElementsId                  = null;
	var global_mouseEvent                = null;
	var History                          = null;

	var c_oAscError                 = Asc.c_oAscError;
	var c_oAscFileType              = Asc.c_oAscFileType;
	var c_oAscAsyncAction           = Asc.c_oAscAsyncAction;
	var c_oAscAdvancedOptionsID     = Asc.c_oAscAdvancedOptionsID;
	var c_oAscFontRenderingModeType = Asc.c_oAscFontRenderingModeType;
	var c_oAscAsyncActionType       = Asc.c_oAscAsyncActionType;
	var c_oAscTypeSelectElement     = Asc.c_oAscTypeSelectElement;
	var c_oAscFill                  = Asc.c_oAscFill;
	var asc_CImgProperty            = Asc.asc_CImgProperty;
	var asc_CShapeFill              = Asc.asc_CShapeFill;
	var asc_CFillBlip               = Asc.asc_CFillBlip;

	function CAscSection()
	{
		this.PageWidth  = 0;
		this.PageHeight = 0;

		this.MarginLeft   = 0;
		this.MarginRight  = 0;
		this.MarginTop    = 0;
		this.MarginBottom = 0;
	}

	CAscSection.prototype.get_PageWidth    = function()
	{
		return this.PageWidth;
	};
	CAscSection.prototype.get_PageHeight   = function()
	{
		return this.PageHeight;
	};
	CAscSection.prototype.get_MarginLeft   = function()
	{
		return this.MarginLeft;
	};
	CAscSection.prototype.get_MarginRight  = function()
	{
		return this.MarginRight;
	};
	CAscSection.prototype.get_MarginTop    = function()
	{
		return this.MarginTop;
	};
	CAscSection.prototype.get_MarginBottom = function()
	{
		return this.MarginBottom;
	};

	function CHeaderProp(obj)
	{
		/*{
		 Type : hdrftr_Footer (hdrftr_Header),
		 Position : 12.5,
		 DifferentFirst : true/false,
		 DifferentEvenOdd : true/false,
		 }*/
		if (obj)
		{
			this.Type             = (undefined != obj.Type) ? obj.Type : null;
			this.Position         = (undefined != obj.Position) ? obj.Position : null;
			this.DifferentFirst   = (undefined != obj.DifferentFirst) ? obj.DifferentFirst : null;
			this.DifferentEvenOdd = (undefined != obj.DifferentEvenOdd) ? obj.DifferentEvenOdd : null;
			this.LinkToPrevious   = (undefined != obj.LinkToPrevious) ? obj.LinkToPrevious : null;
			this.Locked           = (undefined != obj.Locked) ? obj.Locked : false;
		}
		else
		{
			this.Type             = AscCommon.hdrftr_Footer;
			this.Position         = 12.5;
			this.DifferentFirst   = false;
			this.DifferentEvenOdd = false;
			this.LinkToPrevious   = null;
			this.Locked           = false;
		}
	}

	CHeaderProp.prototype.get_Type             = function()
	{
		return this.Type;
	};
	CHeaderProp.prototype.put_Type             = function(v)
	{
		this.Type = v;
	};
	CHeaderProp.prototype.get_Position         = function()
	{
		return this.Position;
	};
	CHeaderProp.prototype.put_Position         = function(v)
	{
		this.Position = v;
	};
	CHeaderProp.prototype.get_DifferentFirst   = function()
	{
		return this.DifferentFirst;
	};
	CHeaderProp.prototype.put_DifferentFirst   = function(v)
	{
		this.DifferentFirst = v;
	};
	CHeaderProp.prototype.get_DifferentEvenOdd = function()
	{
		return this.DifferentEvenOdd;
	};
	CHeaderProp.prototype.put_DifferentEvenOdd = function(v)
	{
		this.DifferentEvenOdd = v;
	};
	CHeaderProp.prototype.get_LinkToPrevious   = function()
	{
		return this.LinkToPrevious;
	};
	CHeaderProp.prototype.get_Locked           = function()
	{
		return this.Locked;
	};

	var DocumentPageSize = new function()
	{
		this.oSizes    = [{name : "US Letter", w_mm : 215.9, h_mm : 279.4, w_tw : 12240, h_tw : 15840},
			{name : "US Legal", w_mm : 215.9, h_mm : 355.6, w_tw : 12240, h_tw : 20160},
			{name : "A4", w_mm : 210, h_mm : 297, w_tw : 11907, h_tw : 16839},
			{name : "A5", w_mm : 148.1, h_mm : 209.9, w_tw : 8391, h_tw : 11907},
			{name : "B5", w_mm : 176, h_mm : 250.1, w_tw : 9979, h_tw : 14175},
			{name : "Envelope #10", w_mm : 104.8, h_mm : 241.3, w_tw : 5940, h_tw : 13680},
			{name : "Envelope DL", w_mm : 110.1, h_mm : 220.1, w_tw : 6237, h_tw : 12474},
			{name : "Tabloid", w_mm : 279.4, h_mm : 431.7, w_tw : 15842, h_tw : 24477},
			{name : "A3", w_mm : 297, h_mm : 420.1, w_tw : 16840, h_tw : 23820},
			{name : "Tabloid Oversize", w_mm : 304.8, h_mm : 457.1, w_tw : 17282, h_tw : 25918},
			{name : "ROC 16K", w_mm : 196.8, h_mm : 273, w_tw : 11164, h_tw : 15485},
			{name : "Envelope Coukei 3", w_mm : 119.9, h_mm : 234.9, w_tw : 6798, h_tw : 13319},
			{name : "Super B/A3", w_mm : 330.2, h_mm : 482.5, w_tw : 18722, h_tw : 27358}
		];
		this.sizeEpsMM = 0.5;
		this.getSize   = function(widthMm, heightMm)
		{
			for (var index in this.oSizes)
			{
				var item = this.oSizes[index];
				if (Math.abs(widthMm - item.w_mm) < this.sizeEpsMM && Math.abs(heightMm - item.h_mm) < this.sizeEpsMM)
					return item;
			}
			return {w_mm : widthMm, h_mm : heightMm};
		};
	};

	function CMailMergeSendData(obj)
	{
		if (obj)
		{
			if (typeof obj.from != 'undefined')
			{
				this["from"] = obj.from;
			}
			if (typeof obj.to != 'undefined')
			{
				this["to"] = obj.to;
			}
			if (typeof obj.subject != 'undefined')
			{
				this["subject"] = obj.subject;
			}
			if (typeof obj.mailFormat != 'undefined')
			{
				this["mailFormat"] = obj.mailFormat;
			}
			if (typeof obj.fileName != 'undefined')
			{
				this["fileName"] = obj.fileName;
			}
			if (typeof obj.message != 'undefined')
			{
				this["message"] = obj.message;
			}
			if (typeof obj.recordFrom != 'undefined')
			{
				this["recordFrom"] = obj.recordFrom;
			}
			if (typeof obj.recordTo != 'undefined')
			{
				this["recordTo"] = obj.recordTo;
			}
		}
		else
		{
			this["from"]        = null;
			this["to"]          = null;
			this["subject"]     = null;
			this["mailFormat"]  = null;
			this["fileName"]    = null;
			this["message"]     = null;
			this["recordFrom"]  = null;
			this["recordTo"]    = null;
			this["recordCount"] = null;
			this["userId"]      = null;
		}
	}

	CMailMergeSendData.prototype.get_From        = function()
	{
		return this["from"]
	};
	CMailMergeSendData.prototype.put_From        = function(v)
	{
		this["from"] = v;
	};
	CMailMergeSendData.prototype.get_To          = function()
	{
		return this["to"]
	};
	CMailMergeSendData.prototype.put_To          = function(v)
	{
		this["to"] = v;
	};
	CMailMergeSendData.prototype.get_Subject     = function()
	{
		return this["subject"]
	};
	CMailMergeSendData.prototype.put_Subject     = function(v)
	{
		this["subject"] = v;
	};
	CMailMergeSendData.prototype.get_MailFormat  = function()
	{
		return this["mailFormat"]
	};
	CMailMergeSendData.prototype.put_MailFormat  = function(v)
	{
		this["mailFormat"] = v;
	};
	CMailMergeSendData.prototype.get_FileName    = function()
	{
		return this["fileName"]
	};
	CMailMergeSendData.prototype.put_FileName    = function(v)
	{
		this["fileName"] = v;
	};
	CMailMergeSendData.prototype.get_Message     = function()
	{
		return this["message"]
	};
	CMailMergeSendData.prototype.put_Message     = function(v)
	{
		this["message"] = v;
	};
	CMailMergeSendData.prototype.get_RecordFrom  = function()
	{
		return this["recordFrom"]
	};
	CMailMergeSendData.prototype.put_RecordFrom  = function(v)
	{
		this["recordFrom"] = v;
	};
	CMailMergeSendData.prototype.get_RecordTo    = function()
	{
		return this["recordTo"]
	};
	CMailMergeSendData.prototype.put_RecordTo    = function(v)
	{
		this["recordTo"] = v;
	};
	CMailMergeSendData.prototype.get_RecordCount = function()
	{
		return this["recordCount"]
	};
	CMailMergeSendData.prototype.put_RecordCount = function(v)
	{
		this["recordCount"] = v;
	};
	CMailMergeSendData.prototype.get_UserId      = function()
	{
		return this["userId"]
	};
	CMailMergeSendData.prototype.put_UserId      = function(v)
	{
		this["userId"] = v;
	};

	// пользоваться так:
	// подрубить его последним из скриптов к страничке
	// и вызвать, после подгрузки (конец метода OnInit <- Drawing/HtmlPage.js)
	// var _api = new asc_docs_api();
	// _api.init(oWordControl);

	/**
	 *
	 * @param config
	 * @constructor
	 * @extends {AscCommon.baseEditorsApi}
	 */
	function asc_docs_api(config)
	{
		asc_docs_api.superclass.constructor.call(this, config, AscCommon.c_oEditorId.Word);

		if (window["AscDesktopEditor"])
		{
			window["AscDesktopEditor"]["CreateEditorApi"]();
		}

		/************ private!!! **************/
		this.WordControl = null;

		this.documentFormatSave = c_oAscFileType.DOCX;

		//todo убрать из native, copypaste, chart, loadfont
		this.InterfaceLocale = null;

		this.ShowParaMarks        = false;
		this.ShowSnapLines        = true;
		this.isAddSpaceBetweenPrg = false;
		this.isPageBreakBefore    = false;
		this.isKeepLinesTogether  = false;

		this.isPaintFormat              = c_oAscFormatPainterState.kOff;
		this.isMarkerFormat             = false;
		this.isViewMode                 = false;
		this.isStartAddShape            = false;
		this.addShapePreset             = "";
		this.isShowTableEmptyLine       = true;
		this.isShowTableEmptyLineAttack = false;

		this.isApplyChangesOnOpen        = false;
		this.isApplyChangesOnOpenEnabled = true;

		this.IsSpellCheckCurrentWord = false;

		this.mailMergeFileData = null;

		this.isCoMarksDraw  = false;
		this.tmpCoMarksDraw = false;
		this.tmpViewRulers  = null;
		this.tmpZoomType    = null;

		// Spell Checking
		this.SpellCheckApi      = (window["AscDesktopEditor"] === undefined) ? new AscCommon.CSpellCheckApi() : new CSpellCheckApi_desktop();
		this.isSpellCheckEnable = true;

		// это чтобы сразу показать ридер, без возможности вернуться в редактор/вьюер
		this.isOnlyReaderMode = false;

		/**************************************/

		this.bInit_word_control = false;
		this.isDocumentModify   = false;

		this.isImageChangeUrl      = false;
		this.isShapeImageChangeUrl = false;

		this.tmpFontRenderingMode = null;
		this.FontAsyncLoadType    = 0;
		this.FontAsyncLoadParam   = null;

		this.isPasteFonts_Images = false;
		this.isLoadNoCutFonts    = false;

		this.pasteCallback       = null;
		this.pasteImageMap       = null;
		this.EndActionLoadImages = 0;

		this.isSaveFonts_Images = false;
		this.saveImageMap       = null;

		this.isLoadImagesCustom = false;
		this.loadCustomImageMap = null;

		this.ServerImagesWaitComplete = false;

		this.DocumentOrientation = false;

		this.SelectedObjectsStack = [];

		this.nCurPointItemsLength = -1;
		this.isDocumentEditor     = true;

		this.CurrentTranslate = null;

		this.CollaborativeMarksShowType = c_oAscCollaborativeMarksShowType.All;

		// объекты, нужные для отправки в тулбар (шрифты, стили)
		this._gui_control_colors = null;
		this._gui_color_schemes  = null;

		this.DocumentReaderMode = null;

		this.ParcedDocument              = false;
		this.isStartCoAuthoringOnEndLoad = false;	// Подсоединились раньше, чем документ загрузился

		if (window.editor == undefined)
		{
			window.editor = this;
			window.editor;
			window['editor'] = window.editor;

			if (window["NATIVE_EDITOR_ENJINE"])
				editor = window.editor;
		}

		this.RevisionChangesStack = [];

		//g_clipboardBase.Init(this);

		this._init();
	}

	AscCommon.extendClass(asc_docs_api, AscCommon.baseEditorsApi);

	asc_docs_api.prototype.sendEvent           = function()
	{
		this.asc_fireCallback.apply(this, arguments);
	};
	// Просмотр PDF
	asc_docs_api.prototype.isPdfViewer         = function()
	{
		return (null === this.WordControl.m_oLogicDocument);
	};
	asc_docs_api.prototype.LoadFontsFromServer = function(_fonts)
	{
		if (undefined === _fonts)
			_fonts = ["Arial", "Symbol", "Wingdings", "Courier New", "Times New Roman"];
		this.FontLoader.LoadFontsFromServer(_fonts);
	};

	asc_docs_api.prototype.SetCollaborativeMarksShowType = function(Type)
	{
		if (c_oAscCollaborativeMarksShowType.None !== this.CollaborativeMarksShowType && c_oAscCollaborativeMarksShowType.None === Type && this.WordControl && this.WordControl.m_oLogicDocument)
		{
			this.CollaborativeMarksShowType = Type;
			AscCommon.CollaborativeEditing.Clear_CollaborativeMarks(true);
		}
		else
		{
			this.CollaborativeMarksShowType = Type;
		}
	};

	asc_docs_api.prototype.GetCollaborativeMarksShowType = function(Type)
	{
		return this.CollaborativeMarksShowType;
	};

	asc_docs_api.prototype.Clear_CollaborativeMarks = function()
	{
		AscCommon.CollaborativeEditing.Clear_CollaborativeMarks(true);
	};

	asc_docs_api.prototype.SetLanguage = function(langId)
	{
		langId = langId.toLowerCase();
		if (undefined !== AscCommonWord.translations_map[langId])
			this.CurrentTranslate = AscCommonWord.translations_map[langId];
	};

	asc_docs_api.prototype.TranslateStyleName   = function(style_name)
	{
		var ret = this.CurrentTranslate.DefaultStyles[style_name];

		if (ret !== undefined)
			return ret;

		return style_name;
	};
	asc_docs_api.prototype.CheckChangedDocument = function()
	{
		if (true === History.Have_Changes())
		{
			// дублирование евента. когда будет undo-redo - тогда
			// эти евенты начнут отличаться
			this.SetDocumentModified(true);
		}
		else
		{
			this.SetDocumentModified(false);
		}

		this._onUpdateDocumentCanSave();
	};
	asc_docs_api.prototype.SetUnchangedDocument = function()
	{
		this.SetDocumentModified(false);
		this._onUpdateDocumentCanSave();
	};

	asc_docs_api.prototype.SetDocumentModified = function(bValue)
	{
		this.isDocumentModify = bValue;
		this.asc_fireCallback("asc_onDocumentModifiedChanged");

		if (undefined !== window["AscDesktopEditor"])
		{
			window["AscDesktopEditor"]["onDocumentModifiedChanged"](bValue);
		}
	};

	asc_docs_api.prototype.isDocumentModified = function()
	{
		if (!this.canSave)
		{
			// Пока идет сохранение, мы не закрываем документ
			return true;
		}
		return this.isDocumentModify;
	};

	asc_docs_api.prototype.sync_BeginCatchSelectedElements = function()
	{
		if (0 != this.SelectedObjectsStack.length)
			this.SelectedObjectsStack.splice(0, this.SelectedObjectsStack.length);

		if (this.WordControl && this.WordControl.m_oDrawingDocument)
			this.WordControl.m_oDrawingDocument.StartTableStylesCheck();
	};
	asc_docs_api.prototype.sync_EndCatchSelectedElements   = function()
	{
		if (this.WordControl && this.WordControl.m_oDrawingDocument)
			this.WordControl.m_oDrawingDocument.EndTableStylesCheck();

		this.asc_fireCallback("asc_onFocusObject", this.SelectedObjectsStack);
	};
	asc_docs_api.prototype.getSelectedElements             = function(bUpdate)
	{
		if (true === bUpdate)
			this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();

		return this.SelectedObjectsStack;
	};
	asc_docs_api.prototype.sync_ChangeLastSelectedElement  = function(type, obj)
	{
		var oUnkTypeObj = null;

		switch (type)
		{
			case c_oAscTypeSelectElement.Paragraph:
				oUnkTypeObj = new Asc.asc_CParagraphProperty(obj);
				break;
			case c_oAscTypeSelectElement.Image:
				oUnkTypeObj = new asc_CImgProperty(obj);
				break;
			case c_oAscTypeSelectElement.Table:
				oUnkTypeObj = new CTableProp(obj);
				break;
			case c_oAscTypeSelectElement.Header:
				oUnkTypeObj = new CHeaderProp(obj);
				break;
		}

		var _i       = this.SelectedObjectsStack.length - 1;
		var bIsFound = false;
		while (_i >= 0)
		{
			if (this.SelectedObjectsStack[_i].Type == type)
			{

				this.SelectedObjectsStack[_i].Value = oUnkTypeObj;
				bIsFound                            = true;
				break;
			}
			_i--;
		}

		if (!bIsFound)
		{
			this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(type, oUnkTypeObj);
		}
	};

	asc_docs_api.prototype.Init = function()
	{
		this.WordControl.Init();
	};

	asc_docs_api.prototype.asc_setLocale = function(val)
	{
		this.InterfaceLocale = val;
	};

	asc_docs_api.prototype.SetTextBoxInputMode = function(bIsEA)
	{
		this.WordControl.SetTextBoxMode(bIsEA);
	};
	asc_docs_api.prototype.GetTextBoxInputMode = function()
	{
		return this.WordControl.TextBoxInputMode;
	};

	asc_docs_api.prototype.ChangeReaderMode  = function()
	{
		return this.WordControl.ChangeReaderMode();
	};
	asc_docs_api.prototype.SetReaderModeOnly = function()
	{
		this.isOnlyReaderMode                       = true;
		if (this.ImageLoader)
			this.ImageLoader.bIsAsyncLoadDocumentImages = false;
	};

	asc_docs_api.prototype.IncreaseReaderFontSize = function()
	{
		return this.WordControl.IncreaseReaderFontSize();
	};
	asc_docs_api.prototype.DecreaseReaderFontSize = function()
	{
		return this.WordControl.DecreaseReaderFontSize();
	};

	asc_docs_api.prototype.CreateCSS = function()
	{
		if (window["flat_desine"] === true)
		{
			AscCommonWord.updateGlobalSkin(AscCommonWord.GlobalSkinFlat);
		}

		var _head = document.getElementsByTagName('head')[0];

		var style0       = document.createElement('style');
		style0.type      = 'text/css';
		style0.innerHTML = ".block_elem { position:absolute;padding:0;margin:0; }";
		_head.appendChild(style0);

		var style2       = document.createElement('style');
		style2.type      = 'text/css';
		style2.innerHTML = ".buttonRuler {\
background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAwCAYAAAAYX/pXAAAABGdBTUEAALGPC/xhBQAAAAlwSFlzAAAOwwAADsMBx2+oZAAAABp0RVh0U29mdHdhcmUAUGFpbnQuTkVUIHYzLjUuMTAw9HKhAAABhElEQVRIS62Uwa6CMBBF/VQNQcOCBS5caOICApEt3+Wv+AcmfQ7pbdreqY+CJifTdjpng727aZrMFmbB+/3erYEE+/3egMPhMPP57QR/EJCgKAoTs1hQlqURjsdjAESyPp1O7pwEVVWZ1+s1VyB7DemRoK5rN+CvNaRPgqZpgqHz+UwSnEklweVyCQbivX8mlQTX65UGfG63m+vLXRLc7/ekQHoAexK0bWs0uq5TKwli8Afq+94Mw+CQPe78K5D6eDzMOI4GVcCdr4IlOMEWfiP4fJpVkEDLA38ghgR+DgB/ICYQ5OYBCez7d1mAvQZ6gcBmAK010A8ENg8c9u2rZ6iBwL51R7z3z1ADgc2DJDYPZnA3ENi3rhLlgauBAO8/JpUHJEih5QF6iwRaHqC3SPANJ9jCbwTP53MVJNDywB+IIYGfA8AfiAkEqTyQDEAO+HlAgtw8IEFuHpAgNw9IkJsHJMjNAxLk5gEJ8P5jUnlAghRaHqC3SKDlAXqLBN9wgvVM5g/dFuEU6U2wnAAAAABJRU5ErkJggg==);\
background-position: 0px 0px;\
background-repeat: no-repeat;\
}";
		_head.appendChild(style2);

		var style3       = document.createElement('style');
		style3.type      = 'text/css';
		style3.innerHTML = ".buttonPrevPage {\
background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAABgBAMAAADm/++TAAAABGdBTUEAALGPC/xhBQAAABJQTFRFAAAA////UVNVu77Cenp62Nrc3x8hMQAAAAF0Uk5TAEDm2GYAAABySURBVCjPY2AgETDBGEoKUAElJcJSxANjKGAwDQWDYAKMIBhDSRXCCFJSIixF0GS4M+AMExcwcCbAcIQxBEUgDEdBQcJSBE2GO4PU6IJHASxS4NGER4p28YWIAlikwKMJjxTt4gsRBbBIgUcTHini4wsAwMmIvYZODL0AAAAASUVORK5CYII=);\
background-position: 0px 0px;\
background-repeat: no-repeat;\
}";
		_head.appendChild(style3);

		var style4       = document.createElement('style');
		style4.type      = 'text/css';
		style4.innerHTML = ".buttonNextPage {\
background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAABgBAMAAADm/++TAAAABGdBTUEAALGPC/xhBQAAABJQTFRFAAAA////UVNVu77Cenp62Nrc3x8hMQAAAAF0Uk5TAEDm2GYAAABySURBVCjPY2AgETDBGEoKUAElJcJSxANjKGAwDQWDYAKMIBhDSRXCCFJSIixF0GS4M+AMExcwcCbAcIQxBEUgDEdBQcJSBE2GO4PU6IJHASxS4NGER4p28YWIAlikwKMJjxTt4gsRBbBIgUcTHini4wsAwMmIvYZODL0AAAAASUVORK5CYII=);\
background-position: 0px -48px;\
background-repeat: no-repeat;\
}";
		_head.appendChild(style4);
	};

	asc_docs_api.prototype.CreateComponents = function()
	{
		this.CreateCSS();

		if (this.HtmlElement != null)
			this.HtmlElement.innerHTML = "<div id=\"id_main\" class=\"block_elem\" style=\"-moz-user-select:none;-khtml-user-select:none;user-select:none;background-color:" + AscCommonWord.GlobalSkin.BackgroundColor + ";overflow:hidden;\" UNSELECTABLE=\"on\">\
								<div id=\"id_panel_left\" class=\"block_elem\">\
									<canvas id=\"id_buttonTabs\" class=\"block_elem\"></canvas>\
									<canvas id=\"id_vert_ruler\" class=\"block_elem\"></canvas>\
								</div>\
									<div id=\"id_panel_top\" class=\"block_elem\">\
									<canvas id=\"id_hor_ruler\" class=\"block_elem\"></canvas>\
									</div>\
                                    <div id=\"id_main_view\" class=\"block_elem\" style=\"overflow:hidden\">\
                                        <canvas id=\"id_viewer\" class=\"block_elem\" style=\"-webkit-user-select: none; background-color:" + AscCommonWord.GlobalSkin.BackgroundColor + ";z-index:1\"></canvas>\
									    <canvas id=\"id_viewer_overlay\" class=\"block_elem\" style=\"-webkit-user-select: none; z-index:2\"></canvas>\
									    <canvas id=\"id_target_cursor\" class=\"block_elem\" width=\"1\" height=\"1\" style=\"-webkit-user-select: none;width:2px;height:13px;display:none;z-index:4;\"></canvas>\
                                    </div>\
								</div>\
									<div id=\"id_panel_right\" class=\"block_elem\" style=\"margin-right:1px;background-color:" + AscCommonWord.GlobalSkin.BackgroundScroll + ";\">\
									<div id=\"id_buttonRulers\" class=\"block_elem buttonRuler\"></div>\
									<div id=\"id_vertical_scroll\" style=\"left:0;top:0px;width:14px;overflow:hidden;position:absolute;\">\
									<div id=\"panel_right_scroll\" class=\"block_elem\" style=\"left:0;top:0;width:1px;height:6000px;\"></div>\
									</div>\
									<div id=\"id_buttonPrevPage\" class=\"block_elem buttonPrevPage\"></div>\
									<div id=\"id_buttonNextPage\" class=\"block_elem buttonNextPage\"></div>\
								</div>\
									<div id=\"id_horscrollpanel\" class=\"block_elem\" style=\"margin-bottom:1px;background-color:" + AscCommonWord.GlobalSkin.BackgroundScroll + ";\">\
									<div id=\"id_horizontal_scroll\" style=\"left:0px;top:0;height:14px;overflow:hidden;position:absolute;width:100%;\">\
										<div id=\"panel_hor_scroll\" class=\"block_elem\" style=\"left:0;top:0;width:6000px;height:1px;\"></div>\
									</div>\
									</div>";
	};

	asc_docs_api.prototype.GetCopyPasteDivId = function()
	{
		if (this.isMobileVersion)
			return this.WordControl.Name;
		return "";
	};

	asc_docs_api.prototype.ContentToHTML = function(bIsRet)
	{
		this.DocumentReaderMode            = new AscCommon.CDocumentReaderMode();
		var _old                           = PasteElementsId.copyPasteUseBinary;
		PasteElementsId.copyPasteUseBinary = false;
		this.WordControl.m_oLogicDocument.Select_All();
		AscCommon.Editor_Copy(this);
		this.WordControl.m_oLogicDocument.Selection_Remove();
		PasteElementsId.copyPasteUseBinary = _old;
		this.DocumentReaderMode            = null;
		return document.getElementById("SelectId").innerHTML;
	};

	asc_docs_api.prototype.InitEditor = function()
	{
		this.WordControl.m_oLogicDocument                    = new AscCommonWord.CDocument(this.WordControl.m_oDrawingDocument);
		this.WordControl.m_oDrawingDocument.m_oLogicDocument = this.WordControl.m_oLogicDocument;
		if (!this.isSpellCheckEnable)
			this.WordControl.m_oLogicDocument.TurnOff_CheckSpelling();

		if (this.WordControl.MobileTouchManager)
			this.WordControl.MobileTouchManager.LogicDocument = this.WordControl.m_oLogicDocument;
	};

	asc_docs_api.prototype.InitViewer = function()
	{
		this.WordControl.m_oDrawingDocument.m_oDocumentRenderer = new AscCommonWord.CDocMeta();
	};

	asc_docs_api.prototype.OpenDocument = function(url, gObject)
	{
		this.isOnlyReaderMode = false;
		this.InitViewer();
		this.LoadedObject         = null;
		this.DocumentType         = 1;
		this.ServerIdWaitComplete = true;

		this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);

		this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.Load(url, gObject);
		this.FontLoader.LoadDocumentFonts(this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.Fonts, true);
	};

	asc_docs_api.prototype.OpenDocument2 = function(url, gObject)
	{
		this.InitEditor();
		this.DocumentType   = 2;
		this.LoadedObjectDS = this.WordControl.m_oLogicDocument.CopyStyle();

		g_oIdCounter.Set_Load(true);

		var openParams        = {checkFileSize : this.isMobileVersion, charCount : 0, parCount : 0};
		var oBinaryFileReader = new AscCommonWord.BinaryFileReader(this.WordControl.m_oLogicDocument, openParams);
		if (oBinaryFileReader.Read(gObject))
		{
			if (History && History.Update_FileDescription)
				History.Update_FileDescription(oBinaryFileReader.stream);

			g_oIdCounter.Set_Load(false);
			this.LoadedObject = 1;

			this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);

			// проверяем какие шрифты нужны
			this.WordControl.m_oDrawingDocument.CheckFontNeeds();
			AscCommon.pptx_content_loader.CheckImagesNeeds(this.WordControl.m_oLogicDocument);

			//this.FontLoader.LoadEmbeddedFonts(this.DocumentUrl, this.WordControl.m_oLogicDocument.EmbeddedFonts);
			this.FontLoader.LoadDocumentFonts(this.WordControl.m_oLogicDocument.Fonts, false);
		}
		else
			editor.asc_fireCallback("asc_onError", c_oAscError.ID.MobileUnexpectedCharCount, c_oAscError.Level.Critical);

		//callback
		editor.DocumentOrientation = (null == editor.WordControl.m_oLogicDocument) ? true : !editor.WordControl.m_oLogicDocument.Orientation;
		var sizeMM;
		if (editor.DocumentOrientation)
			sizeMM = DocumentPageSize.getSize(AscCommon.Page_Width, AscCommon.Page_Height);
		else
			sizeMM = DocumentPageSize.getSize(AscCommon.Page_Height, AscCommon.Page_Width);
		editor.sync_DocSizeCallback(sizeMM.w_mm, sizeMM.h_mm);
		editor.sync_PageOrientCallback(editor.get_DocumentOrientation());

		this.ParcedDocument = true;
		if (this.isStartCoAuthoringOnEndLoad)
		{
			this.CoAuthoringApi.onStartCoAuthoring(true);
			this.isStartCoAuthoringOnEndLoad = false;
		}

		if (this.isMobileVersion)
		{
			AscCommon.AscBrowser.isSafariMacOs   = false;
			PasteElementsId.PASTE_ELEMENT_ID     = "wrd_pastebin";
			PasteElementsId.ELEMENT_DISPAY_STYLE = "none";
		}

		if (AscCommon.AscBrowser.isSafariMacOs)
			setInterval(AscCommon.SafariIntervalFocus, 10);
	};
	// Callbacks
	/* все имена callback'оф начинаются с On. Пока сделаны:
	 OnBold,
	 OnItalic,
	 OnUnderline,
	 OnTextPrBaseline(возвращается расположение строки - supstring, superstring, baseline),
	 OnPrAlign(выравнивание по ширине, правому краю, левому краю, по центру),
	 OnListType( возвращается AscCommon.asc_CListType )

	 фейк-функции ожидающие TODO:
	 Print,Undo,Redo,Copy,Cut,Paste,Share,Save,Download & callbacks
	 OnFontName, OnFontSize, OnLineSpacing

	 OnFocusObject( возвращается массив asc_CSelectedObject )
	 OnInitEditorStyles( возвращается CStylesPainter )
	 OnSearchFound( возвращается CSearchResult );
	 OnParaSpacingLine( возвращается AscCommon.asc_CParagraphSpacing )
	 OnLineSpacing( не используется? )
	 OnTextColor( возвращается AscCommon.CColor )
	 OnTextHightLight( возвращается AscCommon.CColor )
	 OnInitEditorFonts( возвращается массив объектов СFont )
	 OnFontFamily( возвращается asc_CTextFontFamily )
	 */
	var _callbacks = {};

	asc_docs_api.prototype.asc_registerCallback = function(name, callback)
	{
		if (!_callbacks.hasOwnProperty(name))
			_callbacks[name] = [];
		_callbacks[name].push(callback);
	};

	asc_docs_api.prototype.asc_unregisterCallback = function(name, callback)
	{
		if (_callbacks.hasOwnProperty(name))
		{
			for (var i = _callbacks[name].length - 1; i >= 0; --i)
			{
				if (_callbacks[name][i] == callback)
					_callbacks[name].splice(i, 1);
			}
		}
	};

	asc_docs_api.prototype.asc_fireCallback = function(name)
	{
		if (_callbacks.hasOwnProperty(name))
		{
			for (var i = 0; i < _callbacks[name].length; ++i)
			{
				_callbacks[name][i].apply(this || window, Array.prototype.slice.call(arguments, 1));
			}
			return true;
		}
		return false;
	};

	asc_docs_api.prototype.asc_checkNeedCallback = function(name)
	{
		if (_callbacks.hasOwnProperty(name))
		{
			return true;
		}
		return false;
	};

	// тут методы, замены евентов
	asc_docs_api.prototype.get_PropertyThemeColors       = function()
	{
		var _ret = [this._gui_control_colors.Colors, this._gui_control_colors.StandartColors];
		return _ret;
	};
	asc_docs_api.prototype.get_PropertyThemeColorSchemes = function()
	{
		return this._gui_color_schemes;
	};
	// -------

	/////////////////////////////////////////////////////////////////////////
	///////////////////CoAuthoring and Chat api//////////////////////////////
	/////////////////////////////////////////////////////////////////////////
	// Init CoAuthoring
	asc_docs_api.prototype._coAuthoringSetChange = function(change, oColor)
	{
		var oChange = new AscCommon.CCollaborativeChanges();
		oChange.Set_Data(change);
		oChange.Set_Color(oColor);
		AscCommon.CollaborativeEditing.Add_Changes(oChange);
	};

	asc_docs_api.prototype._coAuthoringSetChanges = function(e, oColor)
	{
		var Count = e.length;
		for (var Index = 0; Index < Count; ++Index)
			this._coAuthoringSetChange(e[Index], oColor);
	};

	asc_docs_api.prototype._coAuthoringInitEnd = function()
	{
		var t                                        = this;
		this.CoAuthoringApi.onCursor                 = function(e)
		{
			if (true === AscCommon.CollaborativeEditing.Is_Fast())
			{
				t.WordControl.m_oLogicDocument.Update_ForeignCursor(e[e.length - 1]['cursor'], e[e.length - 1]['user'], true, e[e.length - 1]['useridoriginal']);
			}
		};
		this.CoAuthoringApi.onConnectionStateChanged = function(e)
		{
			if (true === AscCommon.CollaborativeEditing.Is_Fast() && false === e['state'])
			{
				t.WordControl.m_oLogicDocument.Remove_ForeignCursor(e['id']);
			}
			t.asc_fireCallback("asc_onConnectionStateChanged", e);
		};
		this.CoAuthoringApi.onLocksAcquired          = function(e)
		{
			if (t.isApplyChangesOnOpenEnabled)
			{
				// Пока документ еще не загружен, будем сохранять функцию и аргументы
				t.arrPreOpenLocksObjects.push(function()
				{
					t.CoAuthoringApi.onLocksAcquired(e);
				});
				return;
			}

			if (2 != e["state"])
			{
				var Id    = e["block"];
				var Class = g_oTableId.Get_ById(Id);
				if (null != Class)
				{
					var Lock = Class.Lock;

					var OldType = Class.Lock.Get_Type();
					if (locktype_Other2 === OldType || locktype_Other3 === OldType)
					{
						Lock.Set_Type(locktype_Other3, true);
					}
					else
					{
						Lock.Set_Type(locktype_Other, true);
					}

					// Выставляем ID пользователя, залочившего данный элемент
					Lock.Set_UserId(e["user"]);

					if (Class instanceof AscCommonWord.CHeaderFooterController)
					{
						t.sync_LockHeaderFooters();
					}
					else if (Class instanceof AscCommonWord.CDocument)
					{
						t.sync_LockDocumentProps();
					}
					else if (Class instanceof AscCommon.CComment)
					{
						t.sync_LockComment(Class.Get_Id(), e["user"]);
					}
					else if (Class instanceof AscCommonWord.CGraphicObjects)
					{
						t.sync_LockDocumentSchema();
					}

					// Теперь обновлять состояние необходимо, чтобы обновить локи в режиме рецензирования.
					t.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
				}
				else
				{
					AscCommon.CollaborativeEditing.Add_NeedLock(Id, e["user"]);
				}
			}
		};
		this.CoAuthoringApi.onLocksReleased          = function(e, bChanges)
		{
			if (t.isApplyChangesOnOpenEnabled)
			{
				// Пока документ еще не загружен, будем сохранять функцию и аргументы
				t.arrPreOpenLocksObjects.push(function()
				{
					t.CoAuthoringApi.onLocksReleased(e, bChanges);
				});
				return;
			}

			var Id    = e["block"];
			var Class = g_oTableId.Get_ById(Id);
			if (null != Class)
			{
				var Lock = Class.Lock;
				if ("undefined" != typeof(Lock))
				{
					var CurType = Lock.Get_Type();

					var NewType = locktype_None;

					if (CurType === locktype_Other)
					{
						if (true != bChanges)
						{
							NewType = locktype_None;
						}
						else
						{
							NewType = locktype_Other2;
							AscCommon.CollaborativeEditing.Add_Unlock(Class);
						}
					}
					else if (CurType === locktype_Mine)
					{
						// Такого быть не должно
						NewType = locktype_Mine;
					}
					else if (CurType === locktype_Other2 || CurType === locktype_Other3)
					{
						NewType = locktype_Other2;
					}

					Lock.Set_Type(NewType, true);

					// Теперь обновлять состояние необходимо, чтобы обновить локи в режиме рецензирования.
					t.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();

					if (Class instanceof AscCommonWord.CHeaderFooterController)
					{
						if (NewType !== locktype_Mine && NewType !== locktype_None)
						{
							t.sync_LockHeaderFooters();
						}
						else
						{
							t.sync_UnLockHeaderFooters();
						}
					}
					else if (Class instanceof AscCommonWord.CDocument)
					{
						if (NewType !== locktype_Mine && NewType !== locktype_None)
						{
							t.sync_LockDocumentProps();
						}
						else
						{
							t.sync_UnLockDocumentProps();
						}
					}
					else if (Class instanceof AscCommon.CComment)
					{
						if (NewType !== locktype_Mine && NewType !== locktype_None)
						{
							t.sync_LockComment(Class.Get_Id(), e["user"]);
						}
						else
						{
							t.sync_UnLockComment(Class.Get_Id());
						}
					}
					else if (Class instanceof AscCommonWord.CGraphicObjects)
					{
						if (NewType !== locktype_Mine && NewType !== locktype_None)
						{
							t.sync_LockDocumentSchema();
						}
						else
						{
							t.sync_UnLockDocumentSchema();
						}
					}
				}
			}
			else
			{
				AscCommon.CollaborativeEditing.Remove_NeedLock(Id);
			}
		};
		this.CoAuthoringApi.onSaveChanges            = function(e, userId, bFirstLoad)
		{
			var bUseColor;
			if (bFirstLoad)
			{
				bUseColor = -1 === AscCommon.CollaborativeEditing.m_nUseType;
			}
			if (t.CollaborativeMarksShowType === c_oAscCollaborativeMarksShowType.None)
			{
				bUseColor = false;
			}

			var oCommonColor = AscCommon.getUserColorById(userId, null, false, false);
			var oColor       = false === bUseColor ? null : oCommonColor;
			t._coAuthoringSetChange(e, oColor);
			// т.е. если bSendEvent не задан, то посылаем  сообщение + когда загрузился документ
			if (!bFirstLoad && t.bInit_word_control)
			{
				t.sync_CollaborativeChanges();
			}
		};
		this.CoAuthoringApi.onRecalcLocks            = function(e)
		{
			if (e && true === AscCommon.CollaborativeEditing.Is_Fast())
			{
				var CursorInfo = JSON.parse(e);
				AscCommon.CollaborativeEditing.Add_ForeignCursorToUpdate(CursorInfo.UserId, CursorInfo.CursorInfo, CursorInfo.UserShortId);
			}
		};
		this.CoAuthoringApi.onStartCoAuthoring       = function(isStartEvent)
		{
			AscCommon.CollaborativeEditing.Start_CollaborationEditing();
			t.asc_setDrawCollaborationMarks(true);

			if (t.ParcedDocument)
			{
				t.WordControl.m_oLogicDocument.DrawingDocument.Start_CollaborationEditing();

				if (!isStartEvent)
				{
					if (true != History.Is_Clear())
					{
						AscCommon.CollaborativeEditing.Apply_Changes();
						AscCommon.CollaborativeEditing.Send_Changes();
					}
					else
					{
						// Изменений нет, но нужно сбросить lock
						t.CoAuthoringApi.unLockDocument(true);
					}
				}
			}
			else
			{
				t.isStartCoAuthoringOnEndLoad = true;
				if (!isStartEvent)
				{
					// Документ еще не подгрузился, но нужно сбросить lock
					t.CoAuthoringApi.unLockDocument(false);
				}
			}
		};
		this.CoAuthoringApi.onEndCoAuthoring         = function(isStartEvent)
		{
			AscCommon.CollaborativeEditing.End_CollaborationEditing();
			t.asc_setDrawCollaborationMarks(false);
		};
	};

	/////////////////////////////////////////////////////////////////////////
	//////////////////////////SpellChecking api//////////////////////////////
	/////////////////////////////////////////////////////////////////////////
	// Init SpellCheck
	asc_docs_api.prototype._coSpellCheckInit = function()
	{
		if (!this.SpellCheckApi)
		{
			return; // Error
		}

		var t = this;
		if (!window["AscDesktopEditor"])
		{
			if (this.SpellCheckUrl && this.isSpellCheckEnable)
				this.SpellCheckApi.set_url(this.SpellCheckUrl);

			this.SpellCheckApi.onSpellCheck = function(e)
			{
				var incomeObject = JSON.parse(e);
				t.SpellCheck_CallBack(incomeObject);
			};
		}

		this.SpellCheckApi.init(this.documentId);
	};
	//----------------------------------------------------------------------------------------------------------------------
	// SpellCheck_CallBack
	//          Функция ответа от сервера.
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.SpellCheck_CallBack = function(Obj)
	{
		if (undefined != Obj && undefined != Obj["ParagraphId"])
		{
			var ParaId    = Obj["ParagraphId"];
			var Paragraph = g_oTableId.Get_ById(ParaId);
			var Type      = Obj["type"];
			if (null != Paragraph)
			{
				if ("spell" === Type)
				{
					Paragraph.SpellChecker.Check_CallBack(Obj["RecalcId"], Obj["usrCorrect"]);
					Paragraph.ReDraw();
				}
				else if ("suggest" === Type)
				{
					Paragraph.SpellChecker.Check_CallBack2(Obj["RecalcId"], Obj["ElementId"], Obj["usrSuggest"]);
					this.sync_SpellCheckVariantsFound();
				}
			}
		}
	};

	asc_docs_api.prototype.asc_getSpellCheckLanguages = function()
	{
		return AscCommon.g_spellCheckLanguages;
	};
	asc_docs_api.prototype.asc_SpellCheckDisconnect   = function()
	{
		if (!this.SpellCheckApi)
			return; // Error
		this.SpellCheckApi.disconnect();
		this.isSpellCheckEnable = false;
		if (this.WordControl.m_oLogicDocument)
			this.WordControl.m_oLogicDocument.TurnOff_CheckSpelling();
	};
	asc_docs_api.prototype._onUpdateDocumentCanSave   = function()
	{
		var CollEditing = AscCommon.CollaborativeEditing;

		// Можно модифицировать это условие на более быстрое (менять самим состояние в аргументах, а не запрашивать каждый раз)
		var isCanSave = this.isDocumentModified() || (true !== CollEditing.Is_SingleUser() && 0 !== CollEditing.getOwnLocksLength());

		if (true === CollEditing.Is_Fast() && true !== CollEditing.Is_SingleUser())
			isCanSave = false;

		if (isCanSave !== this.isDocumentCanSave)
		{
			this.isDocumentCanSave = isCanSave;
			this.asc_fireCallback('asc_onDocumentCanSaveChanged', this.isDocumentCanSave);
		}
	};

	// get functions
	// Возвращает
	//{
	// ParaPr :
	// {
	//    ContextualSpacing : false,            // Удалять ли интервал между параграфами одинакового стиля
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
	//
	//    Spacing :
	//    {
	//        Line     : 1.15,                  // Расстояние между строками внутри абзаца
	//        LineRule : linerule_Auto,         // Тип расстрояния между строками
	//        Before   : 0,                     // Дополнительное расстояние до абзаца
	//        After    : 10 * g_dKoef_pt_to_mm  // Дополнительное расстояние после абзаца
	//    },
	//
	//    Shd :
	//    {
	//        Value : shd_Nil,
	//        Color :
	//        {
	//            r : 255,
	//            g : 255,
	//            b : 255
	//        }
	//    },
	//
	//    WidowControl : true,                  // Запрет висячих строк
	//
	//    Tabs : []
	// },
	//
	// TextPr :
	// {
	//    Bold       : false,
	//    Italic     : false,
	//    Underline  : false,
	//    Strikeout  : false,
	//    FontFamily :
	//    {
	//        Name  : "Times New Roman",
	//        Index : -1
	//    },
	//    FontSize   : 12,
	//    Color      :
	//    {
	//        r : 0,
	//        g : 0,
	//        b : 0
	//    },
	//    VertAlign : vertalign_Baseline,
	//    HighLight : highlight_None
	// }
	//}


	asc_docs_api.prototype.put_FramePr = function(Obj)
	{
		if (undefined != Obj.FontFamily)
		{
			var loader     = AscCommon.g_font_loader;
			var fontinfo   = g_fontApplication.GetFontInfo(Obj.FontFamily);
			var isasync    = loader.LoadFont(fontinfo, editor.asyncFontEndLoaded_DropCap, Obj);
			Obj.FontFamily = new asc_CTextFontFamily({Name : fontinfo.Name, Index : -1});

			if (false === isasync)
			{
				if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
				{
					this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetFramePrWithFontFamily);
					this.WordControl.m_oLogicDocument.Set_ParagraphFramePr(Obj);
				}
			}
		}
		else
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetFramePr);
				this.WordControl.m_oLogicDocument.Set_ParagraphFramePr(Obj);
			}
		}
	};

	asc_docs_api.prototype.asyncFontEndLoaded_MathDraw = function(Obj)
	{
		this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
		Obj.Generate2();
	};
	asc_docs_api.prototype.sendMathTypesToMenu         = function(_math)
	{
		this.asc_fireCallback("asc_onMathTypes", _math);
	};

	asc_docs_api.prototype.asyncFontEndLoaded_DropCap = function(Obj)
	{
		this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetFramePrWithFontFamilyLong);
			this.WordControl.m_oLogicDocument.Set_ParagraphFramePr(Obj);
		}
		// отжать заморозку меню
	};

	asc_docs_api.prototype.asc_addDropCap = function(bInText)
	{
		this.WordControl.m_oLogicDocument.Add_DropCap(bInText);
	};

	asc_docs_api.prototype.removeDropcap = function(bDropCap)
	{
		this.WordControl.m_oLogicDocument.Remove_DropCap(bDropCap);
	};

	// Paragraph properties
	function CParagraphPropEx(obj)
	{
		if (obj)
		{
			this.ContextualSpacing = (undefined != obj.ContextualSpacing) ? obj.ContextualSpacing : null;
			this.Ind               = (undefined != obj.Ind && null != obj.Ind) ? new Asc.asc_CParagraphInd(obj.Ind) : null;
			this.Jc                = (undefined != obj.Jc) ? obj.Jc : null;
			this.KeepLines         = (undefined != obj.KeepLines) ? obj.KeepLines : null;
			this.KeepNext          = (undefined != obj.KeepNext) ? obj.KeepNext : null;
			this.PageBreakBefore   = (undefined != obj.PageBreakBefore) ? obj.PageBreakBefore : null;
			this.Spacing           = (undefined != obj.Spacing && null != obj.Spacing) ? new AscCommon.asc_CParagraphSpacing(obj.Spacing) : null;
			this.Shd               = (undefined != obj.Shd && null != obj.Shd) ? new Asc.asc_CParagraphShd(obj.Shd) : null;
			this.WidowControl      = (undefined != obj.WidowControl) ? obj.WidowControl : null;                  // Запрет висячих строк
			this.Tabs              = obj.Tabs;
		}
		else
		{
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
			this.ContextualSpacing = false;
			this.Ind               = new Asc.asc_CParagraphInd();
			this.Jc                = AscCommon.align_Left;
			this.KeepLines         = false;
			this.KeepNext          = false;
			this.PageBreakBefore   = false;
			this.Spacing           = new AscCommon.asc_CParagraphSpacing();
			this.Shd               = new Asc.asc_CParagraphShd();
			this.WidowControl      = true;                  // Запрет висячих строк
			this.Tabs              = null;
		}
	}

	CParagraphPropEx.prototype.get_ContextualSpacing = function()
	{
		return this.ContextualSpacing;
	};
	CParagraphPropEx.prototype.get_Ind               = function()
	{
		return this.Ind;
	};
	CParagraphPropEx.prototype.get_Jc                = function()
	{
		return this.Jc;
	};
	CParagraphPropEx.prototype.get_KeepLines         = function()
	{
		return this.KeepLines;
	};
	CParagraphPropEx.prototype.get_KeepNext          = function()
	{
		return this.KeepNext;
	};
	CParagraphPropEx.prototype.get_PageBreakBefore   = function()
	{
		return this.PageBreakBefore;
	};
	CParagraphPropEx.prototype.get_Spacing           = function()
	{
		return this.Spacing;
	};
	CParagraphPropEx.prototype.get_Shd               = function()
	{
		return this.Shd;
	};
	CParagraphPropEx.prototype.get_WidowControl      = function()
	{
		return this.WidowControl;
	};
	CParagraphPropEx.prototype.get_Tabs              = function()
	{
		return this.Tabs;
	};

	// Text properties
	// TextPr :
	// {
	//    Bold       : false,
	//    Italic     : false,
	//    Underline  : false,
	//    Strikeout  : false,
	//    FontFamily :
	//    {
	//        Name  : "Times New Roman",
	//        Index : -1
	//    },
	//    FontSize   : 12,
	//    Color      :
	//    {
	//        r : 0,
	//        g : 0,
	//        b : 0
	//    },
	//    VertAlign : vertalign_Baseline,
	//    HighLight : highlight_None
	// }

	// CTextProp
	function CTextProp(obj)
	{
		if (obj)
		{
			this.Bold       = (undefined != obj.Bold) ? obj.Bold : null;
			this.Italic     = (undefined != obj.Italic) ? obj.Italic : null;
			this.Underline  = (undefined != obj.Underline) ? obj.Underline : null;
			this.Strikeout  = (undefined != obj.Strikeout) ? obj.Strikeout : null;
			this.FontFamily = (undefined != obj.FontFamily && null != obj.FontFamily) ? new asc_CTextFontFamily(obj.FontFamily) : null;
			this.FontSize   = (undefined != obj.FontSize) ? obj.FontSize : null;
			this.Color      = (undefined != obj.Color && null != obj.Color) ? AscCommon.CreateAscColorCustom(obj.Color.r, obj.Color.g, obj.Color.b) : null;
			this.VertAlign  = (undefined != obj.VertAlign) ? obj.VertAlign : null;
			this.HighLight  = (undefined != obj.HighLight) ? obj.HighLight == AscCommonWord.highlight_None ? obj.HighLight : new AscCommon.CColor(obj.HighLight.r, obj.HighLight.g, obj.HighLight.b) : null;
			this.DStrikeout = (undefined != obj.DStrikeout) ? obj.DStrikeout : null;
			this.Spacing    = (undefined != obj.Spacing) ? obj.Spacing : null;
			this.Caps       = (undefined != obj.Caps) ? obj.Caps : null;
			this.SmallCaps  = (undefined != obj.SmallCaps) ? obj.SmallCaps : null;
		}
		else
		{
			//    Bold       : false,
			//    Italic     : false,
			//    Underline  : false,
			//    Strikeout  : false,
			//    FontFamily :
			//    {
			//        Name  : "Times New Roman",
			//        Index : -1
			//    },
			//    FontSize   : 12,
			//    Color      :
			//    {
			//        r : 0,
			//        g : 0,
			//        b : 0
			//    },
			//    VertAlign : vertalign_Baseline,
			//    HighLight : highlight_None
			this.Bold       = false;
			this.Italic     = false;
			this.Underline  = false;
			this.Strikeout  = false;
			this.FontFamily = new asc_CTextFontFamily();
			this.FontSize   = 12;
			this.Color      = AscCommon.CreateAscColorCustom(0, 0, 0);
			this.VertAlign  = AscCommon.vertalign_Baseline;
			this.HighLight  = AscCommonWord.highlight_None;
			this.DStrikeout = false;
			this.Spacing    = 0;
			this.Caps       = false;
			this.SmallCaps  = false;
		}
	}

	CTextProp.prototype.get_Bold       = function()
	{
		return this.Bold;
	};
	CTextProp.prototype.get_Italic     = function()
	{
		return this.Italic;
	};
	CTextProp.prototype.get_Underline  = function()
	{
		return this.Underline;
	};
	CTextProp.prototype.get_Strikeout  = function()
	{
		return this.Strikeout;
	};
	CTextProp.prototype.get_FontFamily = function()
	{
		return this.FontFamily;
	};
	CTextProp.prototype.get_FontSize   = function()
	{
		return this.FontSize;
	};
	CTextProp.prototype.get_Color      = function()
	{
		return this.Color;
	};
	CTextProp.prototype.get_VertAlign  = function()
	{
		return this.VertAlign;
	};
	CTextProp.prototype.get_HighLight  = function()
	{
		return this.HighLight;
	};

	CTextProp.prototype.get_Spacing = function()
	{
		return this.Spacing;
	};

	CTextProp.prototype.get_DStrikeout = function()
	{
		return this.DStrikeout;
	};

	CTextProp.prototype.get_Caps = function()
	{
		return this.Caps;
	};

	CTextProp.prototype.get_SmallCaps = function()
	{
		return this.SmallCaps;
	};


	// paragraph and text properties objects container
	function CParagraphAndTextProp(paragraphProp, textProp)
	{
		this.ParaPr = (undefined != paragraphProp && null != paragraphProp) ? new CParagraphPropEx(paragraphProp) : null;
		this.TextPr = (undefined != textProp && null != textProp) ? new CTextProp(textProp) : null;
	}

	CParagraphAndTextProp.prototype.get_ParaPr = function()
	{
		return this.ParaPr;
	};
	CParagraphAndTextProp.prototype.get_TextPr = function()
	{
		return this.TextPr;
	};

	//
	asc_docs_api.prototype.get_TextProps = function()
	{
		var Doc    = this.WordControl.m_oLogicDocument;
		var ParaPr = Doc.Get_Paragraph_ParaPr();
		var TextPr = Doc.Get_Paragraph_TextPr();

		// return { ParaPr: ParaPr, TextPr : TextPr };
		return new CParagraphAndTextProp(ParaPr, TextPr);	// uncomment if this method will be used externally. 20/03/2012 uncommented for testers
	};

	// -------
	asc_docs_api.prototype.GetJSONLogicDocument = function()
	{
		return JSON.stringify(this.WordControl.m_oLogicDocument);
	};

	asc_docs_api.prototype.get_ContentCount = function()
	{
		return this.WordControl.m_oLogicDocument.Content.length;
	};

	asc_docs_api.prototype.select_Element = function(Index)
	{
		var Document = this.WordControl.m_oLogicDocument;

		if (true === Document.Selection.Use)
			Document.Selection_Remove();

		Document.DrawingDocument.SelectEnabled(true);
		Document.DrawingDocument.TargetEnd();

		Document.Selection.Use   = true;
		Document.Selection.Start = false;
		Document.Selection.Flag  = AscCommon.selectionflag_Common;

		Document.Selection.StartPos = Index;
		Document.Selection.EndPos   = Index;

		Document.Content[Index].Selection.Use      = true;
		Document.Content[Index].Selection.StartPos = Document.Content[Index].Internal_GetStartPos();
		Document.Content[Index].Selection.EndPos   = Document.Content[Index].Content.length - 1;

		Document.Selection_Draw();
	};

	asc_docs_api.prototype.UpdateTextPr        = function(TextPr)
	{
		if ("undefined" != typeof(TextPr))
		{
			this.sync_BoldCallBack(TextPr.Bold);
			this.sync_ItalicCallBack(TextPr.Italic);
			this.sync_UnderlineCallBack(TextPr.Underline);
			this.sync_StrikeoutCallBack(TextPr.Strikeout);
			this.sync_TextPrFontSizeCallBack(TextPr.FontSize);
			this.sync_TextPrFontFamilyCallBack(TextPr.FontFamily);
			this.sync_VerticalAlign(TextPr.VertAlign);
			this.sync_TextHighLight(TextPr.HighLight);
			this.sync_TextSpacing(TextPr.Spacing);
			this.sync_TextDStrikeout(TextPr.DStrikeout);
			this.sync_TextCaps(TextPr.Caps);
			this.sync_TextSmallCaps(TextPr.SmallCaps);
			this.sync_TextPosition(TextPr.Position);
			this.sync_TextLangCallBack(TextPr.Lang);
			this.sync_TextColor(TextPr);
		}
	};
	asc_docs_api.prototype.UpdateParagraphProp = function(ParaPr)
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//{
		//    ParaPr.Locked      = true;
		//    ParaPr.CanAddTable = false;
		//}

		// var prgrhPr = this.get_TextProps();
		// var prProp = {};
		// prProp.Ind = prgrhPr.ParaPr.Ind;
		// prProp.ContextualSpacing = prgrhPr.ParaPr.ContextualSpacing;
		// prProp.Spacing = prgrhPr.ParaPr.Spacing;
		// prProp.PageBreakBefore = prgrhPr.ParaPr.PageBreakBefore;
		// prProp.KeepLines = prgrhPr.ParaPr.KeepLines;

		// {
		//    ContextualSpacing : false,            // Удалять ли интервал между параграфами одинакового стиля
		//
		//    Ind :
		//    {
		//        Left      : 0,                    // Левый отступ
		//        Right     : 0,                    // Правый отступ
		//        FirstLine : 0                     // Первая строка
		//    },
		//    Jc : align_Left,                      // Прилегание параграфа
		//    KeepLines : false,                    // переносить параграф на новую страницу,
		//                                          // если на текущей он целиком не убирается
		//    PageBreakBefore : false,              // начинать параграф с новой страницы
		//
		//    Spacing :
		//    {
		//        Line     : 1.15,                  // Расстояние между строками внутри абзаца
		//        LineRule : linerule_Auto,         // Тип расстрояния между строками
		//        Before   : 0,                     // Дополнительное расстояние до абзаца
		//        After    : 10 * g_dKoef_pt_to_mm  // Дополнительное расстояние после абзаца
		//    }
		//	}

		// TODO: как только разъединят настройки параграфа и текста переделать тут
		var TextPr         = editor.WordControl.m_oLogicDocument.Get_Paragraph_TextPr();
		ParaPr.Subscript   = TextPr.VertAlign === AscCommon.vertalign_SubScript;
		ParaPr.Superscript = TextPr.VertAlign === AscCommon.vertalign_SuperScript;
		ParaPr.Strikeout   = TextPr.Strikeout;
		ParaPr.DStrikeout  = TextPr.DStrikeout;
		ParaPr.AllCaps     = TextPr.Caps;
		ParaPr.SmallCaps   = TextPr.SmallCaps;
		ParaPr.TextSpacing = TextPr.Spacing;
		ParaPr.Position    = TextPr.Position;
		//-----------------------------------------------------------------------------

		if (true === ParaPr.Spacing.AfterAutoSpacing)
			ParaPr.Spacing.After = AscCommonWord.spacing_Auto;
		else if (undefined === ParaPr.Spacing.AfterAutoSpacing)
			ParaPr.Spacing.After = AscCommonWord.UnknownValue;

		if (true === ParaPr.Spacing.BeforeAutoSpacing)
			ParaPr.Spacing.Before = AscCommonWord.spacing_Auto;
		else if (undefined === ParaPr.Spacing.BeforeAutoSpacing)
			ParaPr.Spacing.Before = AscCommonWord.UnknownValue;

		if (-1 === ParaPr.PStyle)
			ParaPr.StyleName = "";
		else if (undefined === ParaPr.PStyle || undefined === this.WordControl.m_oLogicDocument.Styles.Style[ParaPr.PStyle])
			ParaPr.StyleName = this.WordControl.m_oLogicDocument.Styles.Style[this.WordControl.m_oLogicDocument.Styles.Get_Default_Paragraph()].Name;
		else
			ParaPr.StyleName = this.WordControl.m_oLogicDocument.Styles.Style[ParaPr.PStyle].Name;

		var NumType    = -1;
		var NumSubType = -1;
		if (!(null == ParaPr.NumPr || 0 === ParaPr.NumPr.NumId || "0" === ParaPr.NumPr.NumId))
		{
			var Numb = this.WordControl.m_oLogicDocument.Numbering.Get_AbstractNum(ParaPr.NumPr.NumId);

			if (undefined !== Numb && undefined !== Numb.Lvl[ParaPr.NumPr.Lvl])
			{
				var res    = AscCommonWord.getNumInfoLvl(Numb.Lvl[ParaPr.NumPr.Lvl]);
				NumType    = res.NumType;
				NumSubType = res.NumSubType;
			}
		}

		ParaPr.ListType = {Type : NumType, SubType : NumSubType};

		if (undefined !== ParaPr.FramePr && undefined !== ParaPr.FramePr.Wrap)
		{
			if (AscCommonWord.wrap_NotBeside === ParaPr.FramePr.Wrap)
				ParaPr.FramePr.Wrap = false;
			else if (AscCommonWord.wrap_Around === ParaPr.FramePr.Wrap)
				ParaPr.FramePr.Wrap = true;
			else
				ParaPr.FramePr.Wrap = undefined;
		}

		this.sync_ParaSpacingLine(ParaPr.Spacing);
		this.Update_ParaInd(ParaPr.Ind);
		this.sync_PrAlignCallBack(ParaPr.Jc);
		this.sync_ParaStyleName(ParaPr.StyleName);
		this.sync_ListType(ParaPr.ListType);
		this.sync_PrPropCallback(ParaPr);
	};

	/*----------------------------------------------------------------*/
	/*functions for working with clipboard, document*/
	/*TODO: Print,Undo,Redo,Copy,Cut,Paste,Share,Save,DownloadAs,ReturnToDocuments(вернуться на предыдущую страницу) & callbacks for these functions*/
	asc_docs_api.prototype.asc_Print      = function(bIsDownloadEvent)
	{
		if (window["AscDesktopEditor"])
		{
			if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
			{
				if (window["AscDesktopEditor"]["IsSupportNativePrint"](this.DocumentUrl) === true)
				{
					window["AscDesktopEditor"]["Print"]();
					return;
				}
			}
			else
			{
				window["AscDesktopEditor"]["Print"]();
				return;
			}
		}
		this._print(c_oAscAsyncAction.Print, bIsDownloadEvent ? DownloadType.Print : DownloadType.None);
	};
	asc_docs_api.prototype._print         = function(actionType, downloadType)
	{
		var command;
		var options = {isNoData : false, downloadType : downloadType};
		if (null == this.WordControl.m_oLogicDocument)
		{
			command          = 'savefromorigin';
			options.isNoData = true;
		}
		else
		{
			command = 'save';
		}
		this._downloadAs(command, c_oAscFileType.PDF, actionType, options, null);
	};
	asc_docs_api.prototype.Undo           = function()
	{
		this.WordControl.m_oLogicDocument.Document_Undo();
	};
	asc_docs_api.prototype.Redo           = function()
	{
		this.WordControl.m_oLogicDocument.Document_Redo();
	};
	asc_docs_api.prototype.Copy           = function()
	{
		if (window["AscDesktopEditor"])
		{
			var _e     = new AscCommon.CKeyboardEvent();
			_e.CtrlKey = true;
			_e.KeyCode = 67;

			window["AscDesktopEditorButtonMode"] = true;
			this.WordControl.m_oLogicDocument.OnKeyDown(_e);
			window["AscDesktopEditorButtonMode"] = false;

			return;
		}
		return AscCommon.Editor_Copy_Button(this);
	};
	asc_docs_api.prototype.Update_ParaTab = function(Default_Tab, ParaTabs)
	{
		this.WordControl.m_oDrawingDocument.Update_ParaTab(Default_Tab, ParaTabs);
	};
	asc_docs_api.prototype.Cut            = function()
	{
		if (window["AscDesktopEditor"])
		{
			var _e     = new AscCommon.CKeyboardEvent();
			_e.CtrlKey = true;
			_e.KeyCode = 88;

			window["AscDesktopEditorButtonMode"] = true;
			this.WordControl.m_oLogicDocument.OnKeyDown(_e);
			window["AscDesktopEditorButtonMode"] = false;

			return;
		}
		return AscCommon.Editor_Copy_Button(this, true);
	};
	asc_docs_api.prototype.Paste          = function()
	{
		if (window["AscDesktopEditor"])
		{
			var _e     = new AscCommon.CKeyboardEvent();
			_e.CtrlKey = true;
			_e.KeyCode = 86;

			window["AscDesktopEditorButtonMode"] = true;
			this.WordControl.m_oLogicDocument.OnKeyDown(_e);
			window["AscDesktopEditorButtonMode"] = false;

			return;
		}

		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			if (!window.GlobalPasteFlag)
			{
				if (!AscCommon.AscBrowser.isSafariMacOs)
				{
					window.GlobalPasteFlag = true;
					return AscCommon.Editor_Paste_Button(this);
				}
				else
				{
					if (0 === window.GlobalPasteFlagCounter)
					{
						AscCommon.SafariIntervalFocus();
						window.GlobalPasteFlag = true;
						return AscCommon.Editor_Paste_Button(this);
					}
				}
			}
		}
	};

	asc_docs_api.prototype.Share = function()
	{

	};

	asc_docs_api.prototype.asc_CheckCopy = function(_clipboard /* CClipboardData */, _formats)
	{
		if (!this.WordControl.m_oLogicDocument)
		{
			var _text_object = (AscCommon.c_oAscClipboardDataFormat.Text & _formats) ? {Text : ""} : null;
			var _html_data   = this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.Copy(_text_object);

			//TEXT
			if (AscCommon.c_oAscClipboardDataFormat.Text & _formats)
			{
				_clipboard.pushData(AscCommon.c_oAscClipboardDataFormat.Text, _text_object.Text);
			}
			//HTML
			if (AscCommon.c_oAscClipboardDataFormat.Html & _formats)
			{
				_clipboard.pushData(AscCommon.c_oAscClipboardDataFormat.Html, _html_data);
			}
			return;
		}

		var sBase64 = null, _data;

		//TEXT
		if (AscCommon.c_oAscClipboardDataFormat.Text & _formats)
		{
			_data = this.WordControl.m_oLogicDocument.Get_SelectedText();
			_clipboard.pushData(AscCommon.c_oAscClipboardDataFormat.Text, _data)
		}
		//HTML
		if (AscCommon.c_oAscClipboardDataFormat.Html & _formats)
		{
			var oCopyProcessor = new AscCommon.CopyProcessor(this);
			sBase64            = oCopyProcessor.Start();
			_data              = oCopyProcessor.getInnerHtml();

			_clipboard.pushData(AscCommon.c_oAscClipboardDataFormat.Html, _data)
		}
		//INTERNAL
		if (AscCommon.c_oAscClipboardDataFormat.Internal & _formats)
		{
			if (sBase64 === null)
			{
				var oCopyProcessor = new AscCommon.CopyProcessor(this);
				sBase64            = oCopyProcessor.Start();
			}

			_data = sBase64;
			_clipboard.pushData(AscCommon.c_oAscClipboardDataFormat.Internal, _data)
		}
	};

	asc_docs_api.prototype.asc_SelectionCut = function()
	{
		var _logicDoc = this.WordControl.m_oLogicDocument;
		if (!_logicDoc)
			return;

		if (false === _logicDoc.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			History.Create_NewPoint(AscDFH.historydescription_Cut);
			_logicDoc.Remove(1, true, true);
			_logicDoc.Document_UpdateSelectionState();
		}
	};

	asc_docs_api.prototype.asc_PasteData = function(_format, data1, data2)
	{
		this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_PasteHotKey);
		switch (_format)
		{
			case AscCommon.c_oAscClipboardDataFormat.HtmlElement:
				AscCommon.Editor_Paste_Exec(this, data1, data2);
				break;
			case AscCommon.c_oAscClipboardDataFormat.Internal:
				AscCommon.Editor_Paste_Exec(this, null, null, data1);
				break;
			default:
				break;
		}
	};

	asc_docs_api.prototype.onSaveCallback = function(e)
	{
		var t = this;
		if (false == e["saveLock"])
		{
			if (this.isLongAction())
			{
				// Мы не можем в этот момент сохранять, т.к. попали в ситуацию, когда мы залочили сохранение и успели нажать вставку до ответа
				// Нужно снять lock с сохранения
				this.CoAuthoringApi.onUnSaveLock = function()
				{
					t.canSave    = true;
					t.IsUserSave = false;
				};
				this.CoAuthoringApi.unSaveLock();
				return;
			}
			this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);

			if (c_oAscCollaborativeMarksShowType.LastChanges === this.CollaborativeMarksShowType)
			{
				AscCommon.CollaborativeEditing.Clear_CollaborativeMarks();
			}

			// Принимаем чужие изменения
			var HaveOtherChanges = AscCommon.CollaborativeEditing.Have_OtherChanges();
			AscCommon.CollaborativeEditing.Apply_Changes();

			this.CoAuthoringApi.onUnSaveLock = function()
			{
				t.CoAuthoringApi.onUnSaveLock = null;

				// Выставляем, что документ не модифицирован
				t.CheckChangedDocument();
				t.canSave    = true;
				t.IsUserSave = false;
				t.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.Save);

				// Обновляем состояние возможности сохранения документа
				t._onUpdateDocumentCanSave();

				t.jio_save();
				if (undefined !== window["AscDesktopEditor"])
				{
					window["AscDesktopEditor"]["OnSave"]();
				}
			};

			var CursorInfo = null;
			if (true === AscCommon.CollaborativeEditing.Is_Fast())
			{
				CursorInfo = History.Get_DocumentPositionBinary();
			}

			// Пересылаем свои изменения
			AscCommon.CollaborativeEditing.Send_Changes(this.IsUserSave, {
				UserId      : this.CoAuthoringApi.getUserConnectionId(),
				UserShortId : this.DocInfo.get_UserId(),
				CursorInfo  : CursorInfo
			}, HaveOtherChanges);
		}
		else
		{
			var nState = this.CoAuthoringApi.get_state();
			if (AscCommon.ConnectionState.ClosedCoAuth === nState || AscCommon.ConnectionState.ClosedAll === nState)
			{
				// Отключаемся от сохранения, соединение потеряно
				this.canSave    = true;
				this.IsUserSave = false;
			}
			else
			{
				var TimeoutInterval = (true === AscCommon.CollaborativeEditing.Is_Fast() ? 1 : 1000);
				setTimeout(function()
				{
					t.CoAuthoringApi.askSaveChanges(function(event)
					{
						t.onSaveCallback(event);
					});
				}, TimeoutInterval);
			}
		}
	};

	asc_docs_api.prototype.asc_Save           = function(isAutoSave)
	{
		this.IsUserSave = !isAutoSave;
		if (true === this.canSave && !this.isLongAction())
		{
			this.canSave = false;

			var t = this;
			this.CoAuthoringApi.askSaveChanges(function(e)
			{
				t.onSaveCallback(e);
			});
		}
	};
	asc_docs_api.prototype.asc_DownloadOrigin = function(bIsDownloadEvent)
	{
		//скачивание оригинального pdf, djvu, xps
		var downloadType = bIsDownloadEvent ? DownloadType.Download : DownloadType.None;
		var rData        = {
			"id"    : this.documentId,
			"c"     : 'pathurl',
			"title" : this.documentTitle,
			"data"  : 'origin.' + this.documentFormat
		};
		var t            = this;
		t.fCurCallback   = function(input)
		{
			if (null != input && "pathurl" == input["type"])
			{
				if ('ok' == input["status"])
				{
					var url = input["data"];
					if (url)
					{
						t.processSavedFile(url, downloadType);
					}
					else
					{
						t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
					}
				}
				else
				{
					t.handlers.trigger("asc_onError", mapAscServerErrorToAscError(parseInt(input["data"])),
						c_oAscError.Level.NoCritical);
				}
			}
			else
			{
				t.handlers.trigger("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.NoCritical);
			}
		};
		sendCommand(this, null, rData);
	};
	asc_docs_api.prototype.asc_DownloadAs     = function(typeFile, bIsDownloadEvent)
	{//передаем число соответствующее своему формату.
		var actionType = this.mailMergeFileData ? c_oAscAsyncAction.MailMergeLoadFile : c_oAscAsyncAction.DownloadAs;
		var options    = {downloadType : bIsDownloadEvent ? DownloadType.Download : DownloadType.None};
		this._downloadAs("save", typeFile, actionType, options, null);
	};
	asc_docs_api.prototype.Resize             = function()
	{
		if (false === this.bInit_word_control)
			return;
		this.WordControl.OnResize(false);
	};
	asc_docs_api.prototype.AddURL             = function(url)
	{

	};
	asc_docs_api.prototype.Help               = function()
	{

	};
	/*
	 idOption идентификатор дополнительного параметра, c_oAscAdvancedOptionsID.TXT.
	 option - какие свойства применить, пока массив. для TXT объект asc_CTXTAdvancedOptions(codepage)
	 exp:	asc_setAdvancedOptions(c_oAscAdvancedOptionsID.TXT, new Asc.asc_CCSVAdvancedOptions(1200) );
	 */
	asc_docs_api.prototype.asc_setAdvancedOptions       = function(idOption, option)
	{
		switch (idOption)
		{
			case c_oAscAdvancedOptionsID.TXT:
				// Проверяем тип состояния в данный момент
				if (this.advancedOptionsAction === c_oAscAdvancedOptionsAction.Open)
				{
					var rData = {
						"id"            : this.documentId,
						"userid"        : this.documentUserId,
						"format"        : this.documentFormat,
						"vkey"          : this.documentVKey,
						"c"             : "reopen",
						"url"           : this.documentUrl,
						"title"         : this.documentTitle,
						"codepage"      : option.asc_getCodePage(),
						"embeddedfonts" : this.isUseEmbeddedCutFonts
					};
					sendCommand(this, null, rData);
				}
				else if (this.advancedOptionsAction === c_oAscAdvancedOptionsAction.Save)
				{
					var options       = {txtOptions : option, downloadType : this.downloadType};
					this.downloadType = DownloadType.None;
					this._downloadAs("save", c_oAscFileType.TXT, c_oAscAsyncAction.DownloadAs, options, null);
				}
				break;
		}
	};
	asc_docs_api.prototype.SetFontRenderingMode         = function(mode)
	{
		if (!this.isLoadFullApi)
		{
			this.tmpFontRenderingMode = mode;
			return;
		}

		if (c_oAscFontRenderingModeType.noHinting === mode)
			AscCommon.SetHintsProps(false, false);
		else if (c_oAscFontRenderingModeType.hinting === mode)
			AscCommon.SetHintsProps(true, false);
		else if (c_oAscFontRenderingModeType.hintingAndSubpixeling === mode)
			AscCommon.SetHintsProps(true, true);

		this.WordControl.m_oDrawingDocument.ClearCachePages();
		AscCommon.g_fontManager.ClearFontsRasterCache();

		if (window.g_fontManager2 !== undefined && window.g_fontManager2 !== null)
			window.g_fontManager2.ClearFontsRasterCache();

		if (this.bInit_word_control)
			this.WordControl.OnScroll();
	};
	asc_docs_api.prototype.processSavedFile             = function(url, downloadType)
	{
		var t = this;
		if (this.mailMergeFileData)
		{
			this.mailMergeFileData = null;
			AscCommon.loadFileContent(url, function(result)
			{
				if (null === result)
				{
					t.asc_fireCallback("asc_onError", c_oAscError.ID.MailMergeLoadFile, c_oAscError.Level.NoCritical);
					return;
				}
				try
				{
					t.asc_StartMailMergeByList(JSON.parse(result));
				} catch (e)
				{
					t.asc_fireCallback("asc_onError", c_oAscError.ID.MailMergeLoadFile, c_oAscError.Level.NoCritical);
				}
			});
		}
		else
		{
			asc_docs_api.superclass.processSavedFile.call(this, url, downloadType);
		}
	};
	asc_docs_api.prototype.startGetDocInfo              = function()
	{
		/*
		 Возвращаем объект следующего вида:
		 {
		 PageCount: 12,
		 WordsCount: 2321,
		 ParagraphCount: 45,
		 SymbolsCount: 232345,
		 SymbolsWSCount: 34356
		 }
		 */
		this.sync_GetDocInfoStartCallback();

		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			var _render = this.WordControl.m_oDrawingDocument.m_oDocumentRenderer;

			var obj = {
				PageCount      : _render.PagesCount,
				WordsCount     : _render.CountWords,
				ParagraphCount : _render.CountParagraphs,
				SymbolsCount   : _render.CountSymbols,
				SymbolsWSCount : (_render.CountSymbols + _render.CountSpaces)
			};

			this.asc_fireCallback("asc_onDocInfo", new CDocInfoProp(obj));

			this.sync_GetDocInfoEndCallback();
		}
		else
		{
			this.WordControl.m_oLogicDocument.Statistics_Start();
		}
	};
	asc_docs_api.prototype.stopGetDocInfo               = function()
	{
		this.sync_GetDocInfoStopCallback();

		if (null != this.WordControl.m_oLogicDocument)
			this.WordControl.m_oLogicDocument.Statistics_Stop();
	};
	asc_docs_api.prototype.sync_DocInfoCallback         = function(obj)
	{
		this.asc_fireCallback("asc_onDocInfo", new CDocInfoProp(obj));
	};
	asc_docs_api.prototype.sync_GetDocInfoStartCallback = function()
	{
		this.asc_fireCallback("asc_onGetDocInfoStart");
	};
	asc_docs_api.prototype.sync_GetDocInfoStopCallback  = function()
	{
		this.asc_fireCallback("asc_onGetDocInfoStop");
	};
	asc_docs_api.prototype.sync_GetDocInfoEndCallback   = function()
	{
		this.asc_fireCallback("asc_onGetDocInfoEnd");
	};
	asc_docs_api.prototype.sync_CanUndoCallback         = function(bCanUndo)
	{
		if (true === AscCommon.CollaborativeEditing.Is_Fast() && true !== AscCommon.CollaborativeEditing.Is_SingleUser())
			bCanUndo = false;

		this.asc_fireCallback("asc_onCanUndo", bCanUndo);
	};
	asc_docs_api.prototype.sync_CanRedoCallback         = function(bCanRedo)
	{
		if (true === AscCommon.CollaborativeEditing.Is_Fast() && true !== AscCommon.CollaborativeEditing.Is_SingleUser())
			bCanRedo = false;

		this.asc_fireCallback("asc_onCanRedo", bCanRedo);
	};

	asc_docs_api.prototype.can_CopyCut = function()
	{
		return this.WordControl.m_oLogicDocument.Can_CopyCut();
	};

	asc_docs_api.prototype.sync_CanCopyCutCallback = function(bCanCopyCut)
	{
		this.asc_fireCallback("asc_onCanCopyCut", bCanCopyCut);
	};

	asc_docs_api.prototype.setStartPointHistory = function()
	{
		this.noCreatePoint  = true;
		this.exucuteHistory = true;
		this.incrementCounterLongAction();
		this.WordControl.m_oLogicDocument.TurnOff_InterfaceEvents();
	};
	asc_docs_api.prototype.setEndPointHistory   = function()
	{
		this.noCreatePoint     = false;
		this.exucuteHistoryEnd = true;
		this.decrementCounterLongAction();
		this.WordControl.m_oLogicDocument.TurnOn_InterfaceEvents();
	};

	function CDocInfoProp(obj)
	{
		if (obj)
		{
			this.PageCount      = obj.PageCount;
			this.WordsCount     = obj.WordsCount;
			this.ParagraphCount = obj.ParagraphCount;
			this.SymbolsCount   = obj.SymbolsCount;
			this.SymbolsWSCount = obj.SymbolsWSCount;
		}
		else
		{
			this.PageCount      = -1;
			this.WordsCount     = -1;
			this.ParagraphCount = -1;
			this.SymbolsCount   = -1;
			this.SymbolsWSCount = -1;
		}
	}

	CDocInfoProp.prototype.get_PageCount      = function()
	{
		return this.PageCount;
	};
	CDocInfoProp.prototype.put_PageCount      = function(v)
	{
		this.PageCount = v;
	};
	CDocInfoProp.prototype.get_WordsCount     = function()
	{
		return this.WordsCount;
	};
	CDocInfoProp.prototype.put_WordsCount     = function(v)
	{
		this.WordsCount = v;
	};
	CDocInfoProp.prototype.get_ParagraphCount = function()
	{
		return this.ParagraphCount;
	};
	CDocInfoProp.prototype.put_ParagraphCount = function(v)
	{
		this.ParagraphCount = v;
	};
	CDocInfoProp.prototype.get_SymbolsCount   = function()
	{
		return this.SymbolsCount;
	};
	CDocInfoProp.prototype.put_SymbolsCount   = function(v)
	{
		this.SymbolsCount = v;
	};
	CDocInfoProp.prototype.get_SymbolsWSCount = function()
	{
		return this.SymbolsWSCount;
	};
	CDocInfoProp.prototype.put_SymbolsWSCount = function(v)
	{
		this.SymbolsWSCount = v;
	};

	/*callbacks*/
	/*asc_docs_api.prototype.sync_CursorLockCallBack = function(isLock){
	 this.asc_fireCallback("asc_onCursorLock",isLock);
	 }*/
	asc_docs_api.prototype.sync_UndoCallBack       = function()
	{
		this.asc_fireCallback("asc_onUndo");
	};
	asc_docs_api.prototype.sync_RedoCallBack       = function()
	{
		this.asc_fireCallback("asc_onRedo");
	};
	asc_docs_api.prototype.sync_CopyCallBack       = function()
	{
		this.asc_fireCallback("asc_onCopy");
	};
	asc_docs_api.prototype.sync_CutCallBack        = function()
	{
		this.asc_fireCallback("asc_onCut");
	};
	asc_docs_api.prototype.sync_PasteCallBack      = function()
	{
		this.asc_fireCallback("asc_onPaste");
	};
	asc_docs_api.prototype.sync_ShareCallBack      = function()
	{
		this.asc_fireCallback("asc_onShare");
	};
	asc_docs_api.prototype.sync_SaveCallBack       = function()
	{
		this.asc_fireCallback("asc_onSave");
	};
	asc_docs_api.prototype.sync_DownloadAsCallBack = function()
	{
		this.asc_fireCallback("asc_onDownload");
	};

	asc_docs_api.prototype.sync_AddURLCallback  = function()
	{
		this.asc_fireCallback("asc_onAddURL");
	};
	asc_docs_api.prototype.sync_ErrorCallback   = function(errorID, errorLevel)
	{
		this.asc_fireCallback("asc_onError", errorID, errorLevel);
	};
	asc_docs_api.prototype.sync_HelpCallback    = function(url)
	{
		this.asc_fireCallback("asc_onHelp", url);
	};
	asc_docs_api.prototype.sync_UpdateZoom      = function(zoom)
	{
		this.asc_fireCallback("asc_onZoom", zoom);
	};
	asc_docs_api.prototype.ClearPropObjCallback = function(prop)
	{//колбэк предшествующий приходу свойств объекта, prop а всякий случай
		this.asc_fireCallback("asc_onClearPropObj", prop);
	};

	/*----------------------------------------------------------------*/
	/*functions for working with headers*/
	/*
	 структура заголовков, предварительно, выглядит так
	 {
	 headerText: "Header1",//заголовок
	 pageNumber: 0, //содержит номер страницы, где находится искомая последовательность
	 X: 0,//координаты по OX начала последовательности на данной страницы
	 Y: 0,//координаты по OY начала последовательности на данной страницы
	 level: 0//уровень заголовка
	 }
	 заголовки приходят либо в списке, либо последовательно.
	 */
	// CHeader
	function CHeader(obj)
	{
		if (obj)
		{
			this.headerText = (undefined != obj.headerText) ? obj.headerText : null;	//заголовок
			this.pageNumber = (undefined != obj.pageNumber) ? obj.pageNumber : null;	//содержит номер страницы, где находится искомая последовательность
			this.X          = (undefined != obj.X) ? obj.X : null;								//координаты по OX начала последовательности на данной страницы
			this.Y          = (undefined != obj.Y) ? obj.Y : null;								//координаты по OY начала последовательности на данной страницы
			this.level      = (undefined != obj.level) ? obj.level : null;					//позиция заголовка
		}
		else
		{
			this.headerText = null;				//заголовок
			this.pageNumber = null;				//содержит номер страницы, где находится искомая последовательность
			this.X          = null;						//координаты по OX начала последовательности на данной страницы
			this.Y          = null;						//координаты по OY начала последовательности на данной страницы
			this.level      = null;					//позиция заголовка
		}
	}

	CHeader.prototype.get_headerText = function()
	{
		return this.headerText;
	};
	CHeader.prototype.get_pageNumber = function()
	{
		return this.pageNumber;
	};
	CHeader.prototype.get_X          = function()
	{
		return this.X;
	};
	CHeader.prototype.get_Y          = function()
	{
		return this.Y;
	};
	CHeader.prototype.get_Level      = function()
	{
		return this.level;
	};
	var _fakeHeaders                 = [
		new CHeader({headerText : "Header1", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header2", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header3", pageNumber : 0, X : 0, Y : 0, level : 2}),
		new CHeader({headerText : "Header4", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 2}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 3}),
		new CHeader({headerText : "Header3", pageNumber : 0, X : 0, Y : 0, level : 4}),
		new CHeader({headerText : "Header3", pageNumber : 0, X : 0, Y : 0, level : 5}),
		new CHeader({headerText : "Header3", pageNumber : 0, X : 0, Y : 0, level : 6}),
		new CHeader({headerText : "Header4", pageNumber : 0, X : 0, Y : 0, level : 7}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 8}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 2}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 3}),
		new CHeader({headerText : "Header6", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 0}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 1}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 0}),
		new CHeader({headerText : "Header5", pageNumber : 0, X : 0, Y : 0, level : 0})
	];

	asc_docs_api.prototype.CollectHeaders                  = function()
	{
		this.sync_ReturnHeadersCallback(_fakeHeaders);
	};
	asc_docs_api.prototype.GetActiveHeader                 = function()
	{

	};
	asc_docs_api.prototype.gotoHeader                      = function(page, X, Y)
	{
		this.goToPage(page);
	};
	asc_docs_api.prototype.sync_ChangeActiveHeaderCallback = function(position, header)
	{
		this.asc_fireCallback("asc_onChangeActiveHeader", position, new CHeader(header));
	};
	asc_docs_api.prototype.sync_ReturnHeadersCallback      = function(headers)
	{
		var _headers = [];
		for (var i = 0; i < headers.length; i++)
		{
			_headers[i] = new CHeader(headers[i]);
		}

		this.asc_fireCallback("asc_onReturnHeaders", _headers);
	};
	/*----------------------------------------------------------------*/
	/*functions for working with search*/
	/*
	 структура поиска, предварительно, выглядит так
	 {
	 text: "...<b>слово поиска</b>...",
	 pageNumber: 0, //содержит номер страницы, где находится искомая последовательность
	 X: 0,//координаты по OX начала последовательности на данной страницы
	 Y: 0//координаты по OY начала последовательности на данной страницы
	 }
	 */

	asc_docs_api.prototype.asc_searchEnabled = function(bIsEnabled)
	{
		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.SearchResults.IsSearch = false;
			this.WordControl.OnUpdateOverlay();
		}
	};

	asc_docs_api.prototype.asc_findText = function(text, isNext, isMatchCase)
	{
		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.findText(text, isMatchCase, isNext);
			return this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.SearchResults.Count;
		}

		var SearchEngine = editor.WordControl.m_oLogicDocument.Search(text, {MatchCase : isMatchCase});

		var Id = this.WordControl.m_oLogicDocument.Search_GetId(isNext);

		if (null != Id)
			this.WordControl.m_oLogicDocument.Search_Select(Id);

		return SearchEngine.Count;
	};

	asc_docs_api.prototype.asc_replaceText = function(text, replaceWith, isReplaceAll, isMatchCase)
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		this.WordControl.m_oLogicDocument.Search(text, {MatchCase : isMatchCase});

		if (true === isReplaceAll)
			this.WordControl.m_oLogicDocument.Search_Replace(replaceWith, true, -1);
		else
		{
			var CurId      = this.WordControl.m_oLogicDocument.SearchEngine.CurId;
			var bDirection = this.WordControl.m_oLogicDocument.SearchEngine.Direction;
			if (-1 != CurId)
				this.WordControl.m_oLogicDocument.Search_Replace(replaceWith, false, CurId);

			var Id = this.WordControl.m_oLogicDocument.Search_GetId(bDirection);

			if (null != Id)
			{
				this.WordControl.m_oLogicDocument.Search_Select(Id);
				return true;
			}

			return false;
		}
	};

	asc_docs_api.prototype.asc_selectSearchingResults = function(bShow)
	{
		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.SearchResults.Show = bShow;
			this.WordControl.OnUpdateOverlay();
			return;
		}
		this.WordControl.m_oLogicDocument.Search_Set_Selection(bShow);
	};

	asc_docs_api.prototype.asc_isSelectSearchingResults = function()
	{
		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			return this.WordControl.m_oDrawingDocument.m_oDocumentRenderer.SearchResults.Show;
		}
		return this.WordControl.m_oLogicDocument.Search_Get_Selection();
	};

	asc_docs_api.prototype.sync_ReplaceAllCallback = function(ReplaceCount, OverallCount)
	{
		this.asc_fireCallback("asc_onReplaceAll", ReplaceCount, OverallCount);
	};

	asc_docs_api.prototype.sync_SearchEndCallback = function()
	{
		this.asc_fireCallback("asc_onSearchEnd");
	};
	/*----------------------------------------------------------------*/
	/*functions for working with font*/
	/*setters*/
	asc_docs_api.prototype.put_TextPrFontName = function(name)
	{
		var loader   = AscCommon.g_font_loader;
		var fontinfo = g_fontApplication.GetFontInfo(name);
		var isasync  = loader.LoadFont(fontinfo);
		if (false === isasync)
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextFontName);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
					FontFamily : {
						Name  : name,
						Index : -1
					}
				}));
			}
		}
	};
	asc_docs_api.prototype.put_TextPrFontSize = function(size)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextFontSize);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({FontSize : Math.min(size, 100)}));
		}
	};

	asc_docs_api.prototype.put_TextPrBold       = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextBold);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Bold : value}));
		}
	};
	asc_docs_api.prototype.put_TextPrItalic     = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextItalic);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Italic : value}));
		}
	};
	asc_docs_api.prototype.put_TextPrUnderline  = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextUnderline);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Underline : value}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};
	asc_docs_api.prototype.put_TextPrStrikeout  = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextStrikeout);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
				Strikeout  : value,
				DStrikeout : false
			}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};
	asc_docs_api.prototype.put_TextPrDStrikeout = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextDStrikeout);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
				DStrikeout : value,
				Strikeout  : false
			}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};
	asc_docs_api.prototype.put_TextPrSpacing    = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextSpacing);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Spacing : value}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};

	asc_docs_api.prototype.put_TextPrCaps = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextCaps);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
				Caps      : value,
				SmallCaps : false
			}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};

	asc_docs_api.prototype.put_TextPrSmallCaps = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextSmallCaps);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
				SmallCaps : value,
				Caps      : false
			}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};


	asc_docs_api.prototype.put_TextPrPosition = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextPosition);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Position : value}));

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};

	asc_docs_api.prototype.put_TextPrLang = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextLang);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Lang : {Val : value}}));

			this.WordControl.m_oLogicDocument.Spelling.Check_CurParas();

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};


	asc_docs_api.prototype.put_PrLineSpacing          = function(Type, Value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphLineSpacing);
			this.WordControl.m_oLogicDocument.Set_ParagraphSpacing({LineRule : Type, Line : Value});

			var ParaPr = this.get_TextProps().ParaPr;
			if (null != ParaPr)
				this.sync_ParaSpacingLine(ParaPr.Spacing);
		}
	};
	asc_docs_api.prototype.put_LineSpacingBeforeAfter = function(type, value)//"type == 0" means "Before", "type == 1" means "After"
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphLineSpacingBeforeAfter);
			switch (type)
			{
				case 0:
				{
					if (AscCommonWord.spacing_Auto === value)
						this.WordControl.m_oLogicDocument.Set_ParagraphSpacing({BeforeAutoSpacing : true});
					else
						this.WordControl.m_oLogicDocument.Set_ParagraphSpacing({
							Before            : value,
							BeforeAutoSpacing : false
						});

					break;
				}
				case 1:
				{
					if (AscCommonWord.spacing_Auto === value)
						this.WordControl.m_oLogicDocument.Set_ParagraphSpacing({AfterAutoSpacing : true});
					else
						this.WordControl.m_oLogicDocument.Set_ParagraphSpacing({
							After            : value,
							AfterAutoSpacing : false
						});

					break;
				}
			}
		}
	};
	asc_docs_api.prototype.FontSizeIn                 = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_IncFontSize);
			this.WordControl.m_oLogicDocument.Paragraph_IncDecFontSize(true);
		}
	};
	asc_docs_api.prototype.FontSizeOut                = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_DecFontSize);
			this.WordControl.m_oLogicDocument.Paragraph_IncDecFontSize(false);
		}
	};
	// Object:
	// {
	//    Bottom :
	//    {
	//        Color : { r : 0, g : 0, b : 0 },
	//        Value : border_Single,
	//        Size  : 0.5 * g_dKoef_pt_to_mm
	//        Space : 0
	//    },
	//    Left :
	//    {
	//        ....
	//    }
	//    Right :
	//    {
	//        ....
	//    }
	//    Top :
	//    {
	//        ....
	//    }
	//    },
	//    Between :
	//    {
	//        ....
	//    }
	// }


	asc_docs_api.prototype.put_Borders = function(Obj)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphBorders);
			this.WordControl.m_oLogicDocument.Set_ParagraphBorders(Obj);
		}
	};
	/*callbacks*/
	asc_docs_api.prototype.sync_BoldCallBack             = function(isBold)
	{
		this.asc_fireCallback("asc_onBold", isBold);
	};
	asc_docs_api.prototype.sync_ItalicCallBack           = function(isItalic)
	{
		this.asc_fireCallback("asc_onItalic", isItalic);
	};
	asc_docs_api.prototype.sync_UnderlineCallBack        = function(isUnderline)
	{
		this.asc_fireCallback("asc_onUnderline", isUnderline);
	};
	asc_docs_api.prototype.sync_StrikeoutCallBack        = function(isStrikeout)
	{
		this.asc_fireCallback("asc_onStrikeout", isStrikeout);
	};
	asc_docs_api.prototype.sync_TextPrFontFamilyCallBack = function(FontFamily)
	{
		if (undefined != FontFamily)
			this.asc_fireCallback("asc_onFontFamily", new asc_CTextFontFamily(FontFamily));
		else
			this.asc_fireCallback("asc_onFontFamily", new asc_CTextFontFamily({Name : "", Index : -1}));
	};
	asc_docs_api.prototype.sync_TextPrFontSizeCallBack   = function(FontSize)
	{
		this.asc_fireCallback("asc_onFontSize", FontSize);
	};
	asc_docs_api.prototype.sync_PrLineSpacingCallBack    = function(LineSpacing)
	{
		this.asc_fireCallback("asc_onLineSpacing", new Asc.asc_CParagraphInd(LineSpacing));
	};
	asc_docs_api.prototype.sync_InitEditorStyles         = function(styles_painter)
	{
		if (!this.isViewMode) {
			this.asc_fireCallback("asc_onInitEditorStyles", styles_painter);
		}
	};
	asc_docs_api.prototype.sync_InitEditorTableStyles    = function(styles, is_retina_enabled)
	{
		if (!this.isViewMode) {
			this.asc_fireCallback("asc_onInitTableTemplates", styles, is_retina_enabled);
		}
	};


	/*----------------------------------------------------------------*/
	/*functions for working with paragraph*/
	/*setters*/
	// Right = 0; Left = 1; Center = 2; Justify = 3; or using enum that written above

	/* структура для параграфа
	 Ind :
	 {
	 Left      : 0,                    // Левый отступ
	 Right     : 0,                    // Правый отступ
	 FirstLine : 0                     // Первая строка
	 }
	 Spacing :
	 {
	 Line     : 1.15,                  // Расстояние между строками внутри абзаца
	 LineRule : linerule_Auto,         // Тип расстрояния между строками
	 Before   : 0,                     // Дополнительное расстояние до абзаца
	 After    : 10 * g_dKoef_pt_to_mm  // Дополнительное расстояние после абзаца
	 },
	 KeepLines : false,                    // переносить параграф на новую страницу,
	 // если на текущей он целиком не убирается
	 PageBreakBefore : false
	 */

	asc_docs_api.prototype.paraApply = function(Props)
	{
		var Additional = undefined;
		if (undefined != Props.DefaultTab)
			Additional = {
				Type      : AscCommon.changestype_2_Element_and_Type,
				Element   : this.WordControl.m_oLogicDocument,
				CheckType : AscCommon.changestype_Document_SectPr
			};

		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties, Additional))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphPr);

			// TODO: Сделать так, чтобы пересчет был всего 1 здесь
			if ("undefined" != typeof(Props.ContextualSpacing) && null != Props.ContextualSpacing)
				this.WordControl.m_oLogicDocument.Set_ParagraphContextualSpacing(Props.ContextualSpacing);

			if ("undefined" != typeof(Props.Ind) && null != Props.Ind)
				this.WordControl.m_oLogicDocument.Set_ParagraphIndent(Props.Ind);

			if ("undefined" != typeof(Props.Jc) && null != Props.Jc)
				this.WordControl.m_oLogicDocument.Set_ParagraphAlign(Props.Jc);

			if ("undefined" != typeof(Props.KeepLines) && null != Props.KeepLines)
				this.WordControl.m_oLogicDocument.Set_ParagraphKeepLines(Props.KeepLines);

			if (undefined != Props.KeepNext && null != Props.KeepNext)
				this.WordControl.m_oLogicDocument.Set_ParagraphKeepNext(Props.KeepNext);

			if (undefined != Props.WidowControl && null != Props.WidowControl)
				this.WordControl.m_oLogicDocument.Set_ParagraphWidowControl(Props.WidowControl);

			if ("undefined" != typeof(Props.PageBreakBefore) && null != Props.PageBreakBefore)
				this.WordControl.m_oLogicDocument.Set_ParagraphPageBreakBefore(Props.PageBreakBefore);

			if ("undefined" != typeof(Props.Spacing) && null != Props.Spacing)
				this.WordControl.m_oLogicDocument.Set_ParagraphSpacing(Props.Spacing);

			if ("undefined" != typeof(Props.Shd) && null != Props.Shd)
			{
				var Unifill        = new AscFormat.CUniFill();
				Unifill.fill       = new AscFormat.CSolidFill();
				Unifill.fill.color = AscFormat.CorrectUniColor(Props.Shd.Color, Unifill.fill.color, 1);
				this.WordControl.m_oLogicDocument.Set_ParagraphShd(
					{
						Value   : Props.Shd.Value,
						Color   : {
							r : Props.Shd.Color.asc_getR(),
							g : Props.Shd.Color.asc_getG(),
							b : Props.Shd.Color.asc_getB()
						},
						Unifill : Unifill
					});
			}

			if ("undefined" != typeof(Props.Brd) && null != Props.Brd)
			{
				if (Props.Brd.Left && Props.Brd.Left.Color)
				{
					Props.Brd.Left.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.Left.Color);
				}
				if (Props.Brd.Top && Props.Brd.Top.Color)
				{
					Props.Brd.Top.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.Top.Color);
				}
				if (Props.Brd.Right && Props.Brd.Right.Color)
				{
					Props.Brd.Right.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.Right.Color);
				}
				if (Props.Brd.Bottom && Props.Brd.Bottom.Color)
				{
					Props.Brd.Bottom.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.Bottom.Color);
				}
				if (Props.Brd.InsideH && Props.Brd.InsideH.Color)
				{
					Props.Brd.InsideH.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.InsideH.Color);
				}
				if (Props.Brd.InsideV && Props.Brd.InsideV.Color)
				{
					Props.Brd.InsideV.Unifill = AscFormat.CreateUnifillFromAscColor(Props.Brd.InsideV.Color);
				}

				this.WordControl.m_oLogicDocument.Set_ParagraphBorders(Props.Brd);
			}

			if (undefined != Props.Tabs)
			{
				var Tabs = new AscCommonWord.CParaTabs();
				Tabs.Set_FromObject(Props.Tabs.Tabs);
				this.WordControl.m_oLogicDocument.Set_ParagraphTabs(Tabs);
			}

			if (undefined != Props.DefaultTab)
			{
				this.WordControl.m_oLogicDocument.Set_DocumentDefaultTab(Props.DefaultTab);
			}


			// TODO: как только разъединят настройки параграфа и текста переделать тут
			var TextPr = new AscCommonWord.CTextPr();

			if (true === Props.Subscript)
				TextPr.VertAlign = AscCommon.vertalign_SubScript;
			else if (true === Props.Superscript)
				TextPr.VertAlign = AscCommon.vertalign_SuperScript;
			else if (false === Props.Superscript || false === Props.Subscript)
				TextPr.VertAlign = AscCommon.vertalign_Baseline;

			if (undefined != Props.Strikeout)
			{
				TextPr.Strikeout  = Props.Strikeout;
				TextPr.DStrikeout = false;
			}

			if (undefined != Props.DStrikeout)
			{
				TextPr.DStrikeout = Props.DStrikeout;
				if (true === TextPr.DStrikeout)
					TextPr.Strikeout = false;
			}

			if (undefined != Props.SmallCaps)
			{
				TextPr.SmallCaps = Props.SmallCaps;
				TextPr.AllCaps   = false;
			}

			if (undefined != Props.AllCaps)
			{
				TextPr.Caps = Props.AllCaps;
				if (true === TextPr.AllCaps)
					TextPr.SmallCaps = false;
			}

			if (undefined != Props.TextSpacing)
				TextPr.Spacing = Props.TextSpacing;

			if (undefined != Props.Position)
				TextPr.Position = Props.Position;

			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr(TextPr));
			this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
		}
	};

	asc_docs_api.prototype.put_PrAlign        = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphAlign);
			this.WordControl.m_oLogicDocument.Set_ParagraphAlign(value);
		}
	};
	// 0- baseline, 2-subscript, 1-superscript
	asc_docs_api.prototype.put_TextPrBaseline = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextVertAlign);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({VertAlign : value}));
		}
	};
	/*
	 Во всех случаях SubType = 0 означает, что нажали просто на кнопку
	 c выбором типа списка, без выбора подтипа.

	 Маркированный список Type = 0
	 нет          - SubType = -1
	 черная точка - SubType = 1
	 круг         - SubType = 2
	 квадрат      - SubType = 3
	 картинка     - SubType = -1
	 4 ромба      - SubType = 4
	 ч/б стрелка  - SubType = 5
	 галка        - SubType = 6
	 ромб         - SubType = 7

	 Нумерованный список Type = 1
	 нет - SubType = -1
	 1.  - SubType = 1
	 1)  - SubType = 2
	 I.  - SubType = 3
	 A.  - SubType = 4
	 a)  - SubType = 5
	 a.  - SubType = 6
	 i.  - SubType = 7

	 Многоуровневый список Type = 2
	 нет           - SubType = -1
	 1)a)i)        - SubType = 1
	 1.1.1         - SubType = 2
	 маркированный - SubType = 3
	 */
	asc_docs_api.prototype.put_ListType = function(type, subtype)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			var NumberInfo =
				{
					Type    : 0,
					SubType : -1
				};

			NumberInfo.Type    = type;
			NumberInfo.SubType = subtype;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphNumbering);
			this.WordControl.m_oLogicDocument.Set_ParagraphNumbering(NumberInfo);
		}
	};
	asc_docs_api.prototype.put_Style    = function(name)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphStyle);
			this.WordControl.m_oLogicDocument.Set_ParagraphStyle(name);
		}
	};

	asc_docs_api.prototype.SetDeviceInputHelperId = function(idKeyboard)
	{
		if (window.ID_KEYBOARD_AREA === undefined && this.WordControl.m_oMainView != null)
		{
			window.ID_KEYBOARD_AREA = document.getElementById(idKeyboard);

			window.ID_KEYBOARD_AREA.onkeypress = function(e)
			{
				if (false === editor.WordControl.IsFocus)
				{
					editor.WordControl.IsFocus = true;
					var ret                    = editor.WordControl.onKeyPress(e);
					editor.WordControl.IsFocus = false;
					return ret;
				}
			}
			window.ID_KEYBOARD_AREA.onkeydown  = function(e)
			{
				if (false === editor.WordControl.IsFocus)
				{
					editor.WordControl.IsFocus = true;
					var ret                    = editor.WordControl.onKeyDown(e);
					editor.WordControl.IsFocus = false;
					return ret;
				}
			}
		}
	};

	asc_docs_api.prototype.put_ShowSnapLines = function(isShow)
	{
		this.ShowSnapLines = isShow;
	};
	asc_docs_api.prototype.get_ShowSnapLines = function()
	{
		return this.ShowSnapLines;
	};

	asc_docs_api.prototype.put_ShowParaMarks      = function(isShow)
	{
		/*
		 if (window.IsAddDiv === undefined && this.WordControl.m_oMainView != null)
		 {
		 window.IsAddDiv = true;

		 var _div = this.WordControl.m_oMainView.HtmlElement;

		 var test = document.createElement('textarea');
		 test.id = "area_id";

		 test.setAttribute("style", "font-family:arial;font-size:12pt;position:absolute;resize:none;padding:2px;margin:0px;font-weight:normal;box-sizing:content-box;-moz-box-sizing:content-box;-webkit-box-sizing:content-box;z-index:1000");
		 test.style.border = "2px solid #4363A4";

		 test.style.width = "100px";
		 //this.TextBoxInput.style.height = "40px";
		 test.rows = 1;

		 _div.appendChild(test);

		 test.onkeypress = function(e){
		 return editor.WordControl.onKeyPress(e);
		 }
		 test.onkeydown = function(e){
		 return editor.WordControl.onKeyDown(e);
		 }
		 }
		 */

		this.ShowParaMarks = isShow;
		this.WordControl.OnRePaintAttack();

		if (true === this.isMarkerFormat)
			this.sync_MarkerFormatCallback(false);

		return this.ShowParaMarks;
	};
	asc_docs_api.prototype.get_ShowParaMarks      = function()
	{
		return this.ShowParaMarks;
	};
	asc_docs_api.prototype.put_ShowTableEmptyLine = function(isShow)
	{
		this.isShowTableEmptyLine = isShow;
		this.WordControl.OnRePaintAttack();

		if (true === this.isMarkerFormat)
			this.sync_MarkerFormatCallback(false);

		return this.isShowTableEmptyLine;
	};
	asc_docs_api.prototype.get_ShowTableEmptyLine = function()
	{
		return this.isShowTableEmptyLine;
	};
	asc_docs_api.prototype.put_PageBreak          = function(isBreak)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.isPageBreakBefore = isBreak;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphPageBreakBefore);
			this.WordControl.m_oLogicDocument.Set_ParagraphPageBreakBefore(isBreak);
			this.sync_PageBreakCallback(isBreak);
		}
	};

	asc_docs_api.prototype.put_WidowControl = function(bValue)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphWidowControl);
			this.WordControl.m_oLogicDocument.Set_ParagraphWidowControl(bValue);
			this.sync_WidowControlCallback(bValue);
		}
	};

	asc_docs_api.prototype.put_KeepLines = function(isKeepLines)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.isKeepLinesTogether = isKeepLines;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphKeepLines);
			this.WordControl.m_oLogicDocument.Set_ParagraphKeepLines(isKeepLines);
			this.sync_KeepLinesCallback(isKeepLines);
		}
	};

	asc_docs_api.prototype.put_KeepNext = function(isKeepNext)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphKeepNext);
			this.WordControl.m_oLogicDocument.Set_ParagraphKeepNext(isKeepNext);
			this.sync_KeepNextCallback(isKeepNext);
		}
	};

	asc_docs_api.prototype.put_AddSpaceBetweenPrg = function(isSpacePrg)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.isAddSpaceBetweenPrg = isSpacePrg;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphContextualSpacing);
			this.WordControl.m_oLogicDocument.Set_ParagraphContextualSpacing(isSpacePrg);
		}
	};
	asc_docs_api.prototype.put_LineHighLight      = function(is_flag, r, g, b)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			if (false === is_flag)
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextHighlightNone);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({HighLight : AscCommonWord.highlight_None}));
			}
			else
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextHighlightColor);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
					HighLight : {
						r : r,
						g : g,
						b : b
					}
				}));
			}
		}
	};
	asc_docs_api.prototype.put_TextColor          = function(color)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextColor);

			if (true === color.Auto)
			{
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
					Color      : {
						Auto : true,
						r    : 0,
						g    : 0,
						b    : 0
					}, Unifill : undefined
				}));
			}
			else
			{
				var Unifill        = new AscFormat.CUniFill();
				Unifill.fill       = new AscFormat.CSolidFill();
				Unifill.fill.color = AscFormat.CorrectUniColor(color, Unifill.fill.color, 1);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({Unifill : Unifill}));
			}

			if (true === this.isMarkerFormat)
				this.sync_MarkerFormatCallback(false);
		}
	};
	asc_docs_api.prototype.put_ParagraphShade     = function(is_flag, color, isOnlyPara)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphShd);

			if (true === isOnlyPara)
				this.WordControl.m_oLogicDocument.Set_UseTextShd(false);

			if (false === is_flag)
				this.WordControl.m_oLogicDocument.Set_ParagraphShd({Value : Asc.c_oAscShdNil});
			else
			{
				var Unifill        = new AscFormat.CUniFill();
				Unifill.fill       = new AscFormat.CSolidFill();
				Unifill.fill.color = AscFormat.CorrectUniColor(color, Unifill.fill.color, 1);
				this.WordControl.m_oLogicDocument.Set_ParagraphShd({
					Value   : Asc.c_oAscShdClear,
					Color   : {
						r : color.asc_getR(),
						g : color.asc_getG(),
						b : color.asc_getB()
					},
					Unifill : Unifill
				});
			}

			this.WordControl.m_oLogicDocument.Set_UseTextShd(true);
		}
	};
	asc_docs_api.prototype.put_PrIndent           = function(value, levelValue)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphIndent);
			this.WordControl.m_oLogicDocument.Set_ParagraphIndent({Left : value, ChangeLevel : levelValue});
		}
	};
	asc_docs_api.prototype.IncreaseIndent         = function()
	{
		this.WordControl.m_oLogicDocument.IncreaseIndent();
	};
	asc_docs_api.prototype.DecreaseIndent         = function()
	{
		this.WordControl.m_oLogicDocument.DecreaseIndent();
	};
	asc_docs_api.prototype.put_PrIndentRight      = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphIndentRight);
			this.WordControl.m_oLogicDocument.Set_ParagraphIndent({Right : value});
		}
	};
	asc_docs_api.prototype.put_PrFirstLineIndent  = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetParagraphIndentFirstLine);
			this.WordControl.m_oLogicDocument.Set_ParagraphIndent({FirstLine : value});
		}
	};
	asc_docs_api.prototype.put_Margins            = function(left, top, right, bottom)
	{
		this.WordControl.m_oLogicDocument.Set_DocumentMargin({Left : left, Top : top, Right : right, Bottom : bottom});
	};
	asc_docs_api.prototype.getFocusObject         = function()
	{//возвратит тип элемента - параграф c_oAscTypeSelectElement.Paragraph, изображение c_oAscTypeSelectElement.Image, таблица c_oAscTypeSelectElement.Table, колонтитул c_oAscTypeSelectElement.Header.

	};

	/*callbacks*/
	asc_docs_api.prototype.sync_VerticalAlign     = function(typeBaseline)
	{
		this.asc_fireCallback("asc_onVerticalAlign", typeBaseline);
	};
	asc_docs_api.prototype.sync_PrAlignCallBack   = function(value)
	{
		this.asc_fireCallback("asc_onPrAlign", value);
	};
	asc_docs_api.prototype.sync_ListType          = function(NumPr)
	{
		this.asc_fireCallback("asc_onListType", new AscCommon.asc_CListType(NumPr));
	};
	asc_docs_api.prototype.sync_TextColor         = function(TextPr)
	{
		if (TextPr.Unifill && TextPr.Unifill.fill && TextPr.Unifill.fill.type === c_oAscFill.FILL_TYPE_SOLID && TextPr.Unifill.fill.color)
		{
			this.asc_fireCallback("asc_onTextColor", AscCommon.CreateAscColor(TextPr.Unifill.fill.color));
		}
		else if (undefined != TextPr.Color)
		{
			this.asc_fireCallback("asc_onTextColor", AscCommon.CreateAscColorCustom(TextPr.Color.r, TextPr.Color.g, TextPr.Color.b, TextPr.Color.Auto));
		}
	};
	asc_docs_api.prototype.sync_TextHighLight     = function(HighLight)
	{
		if (undefined != HighLight)
			this.asc_fireCallback("asc_onTextHighLight", new AscCommon.CColor(HighLight.r, HighLight.g, HighLight.b));
	};
	asc_docs_api.prototype.sync_TextSpacing       = function(Spacing)
	{
		this.asc_fireCallback("asc_onTextSpacing", Spacing);
	};
	asc_docs_api.prototype.sync_TextDStrikeout    = function(Value)
	{
		this.asc_fireCallback("asc_onTextDStrikeout", Value);
	};
	asc_docs_api.prototype.sync_TextCaps          = function(Value)
	{
		this.asc_fireCallback("asc_onTextCaps", Value);
	};
	asc_docs_api.prototype.sync_TextSmallCaps     = function(Value)
	{
		this.asc_fireCallback("asc_onTextSmallCaps", Value);
	};
	asc_docs_api.prototype.sync_TextPosition      = function(Value)
	{
		this.asc_fireCallback("asc_onTextPosition", Value);
	};
	asc_docs_api.prototype.sync_TextLangCallBack  = function(Lang)
	{
		this.asc_fireCallback("asc_onTextLanguage", Lang.Val);
	};
	asc_docs_api.prototype.sync_ParaStyleName     = function(Name)
	{
		this.asc_fireCallback("asc_onParaStyleName", Name);
	};
	asc_docs_api.prototype.sync_ParaSpacingLine   = function(SpacingLine)
	{
		if (true === SpacingLine.AfterAutoSpacing)
			SpacingLine.After = AscCommonWord.spacing_Auto;
		else if (undefined === SpacingLine.AfterAutoSpacing)
			SpacingLine.After = AscCommonWord.UnknownValue;

		if (true === SpacingLine.BeforeAutoSpacing)
			SpacingLine.Before = AscCommonWord.spacing_Auto;
		else if (undefined === SpacingLine.BeforeAutoSpacing)
			SpacingLine.Before = AscCommonWord.UnknownValue;

		this.asc_fireCallback("asc_onParaSpacingLine", new AscCommon.asc_CParagraphSpacing(SpacingLine));
	};
	asc_docs_api.prototype.sync_PageBreakCallback = function(isBreak)
	{
		this.asc_fireCallback("asc_onPageBreak", isBreak);
	};

	asc_docs_api.prototype.sync_WidowControlCallback = function(bValue)
	{
		this.asc_fireCallback("asc_onWidowControl", bValue);
	};

	asc_docs_api.prototype.sync_KeepNextCallback = function(bValue)
	{
		this.asc_fireCallback("asc_onKeepNext", bValue);
	};

	asc_docs_api.prototype.sync_KeepLinesCallback       = function(isKeepLines)
	{
		this.asc_fireCallback("asc_onKeepLines", isKeepLines);
	};
	asc_docs_api.prototype.sync_ShowParaMarksCallback   = function()
	{
		this.asc_fireCallback("asc_onShowParaMarks");
	};
	asc_docs_api.prototype.sync_SpaceBetweenPrgCallback = function()
	{
		this.asc_fireCallback("asc_onSpaceBetweenPrg");
	};
	asc_docs_api.prototype.sync_PrPropCallback          = function(prProp)
	{
		var _len = this.SelectedObjectsStack.length;
		if (_len > 0)
		{
			if (this.SelectedObjectsStack[_len - 1].Type == c_oAscTypeSelectElement.Paragraph)
			{
				this.SelectedObjectsStack[_len - 1].Value = new Asc.asc_CParagraphProperty(prProp);
				return;
			}
		}

		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Paragraph, new Asc.asc_CParagraphProperty(prProp));
	};

	asc_docs_api.prototype.sync_MathPropCallback = function(MathProp)
	{
		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Math, MathProp);
	};

	asc_docs_api.prototype.sync_EndAddShape = function()
	{
		editor.asc_fireCallback("asc_onEndAddShape");
		if (this.WordControl.m_oDrawingDocument.m_sLockedCursorType == "crosshair")
		{
			this.WordControl.m_oDrawingDocument.UnlockCursorType();
		}
	};

	asc_docs_api.prototype.SetDrawingFreeze = function(bIsFreeze)
	{
		this.WordControl.DrawingFreeze = bIsFreeze;

		var _elem1 = document.getElementById("id_main");
		if (_elem1)
		{
			var _elem2 = document.getElementById("id_horscrollpanel");
			var _elem3 = document.getElementById("id_panel_right");
			if (bIsFreeze)
			{
				_elem1.style.display = "none";
				_elem2.style.display = "none";
				_elem3.style.display = "none";
			}
			else
			{
				_elem1.style.display = "block";
				_elem2.style.display = "block";
				_elem3.style.display = "block";
			}
		}

		if (!bIsFreeze)
			this.WordControl.OnScroll();
	};

	//----------------------------------------------------------------------------------------------------------------------
	// Работаем с формулами
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.asc_SetMathProps = function(MathProps)
	{
		this.WordControl.m_oLogicDocument.Set_MathProps(MathProps);
	};

	asc_docs_api.prototype["asc_SetMathProps"] = asc_docs_api.prototype.asc_SetMathProps;
	//----------------------------------------------------------------------------------------------------------------------
	// Работаем с настройками секции
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.change_PageOrient       = function(isPortrait)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
		{
			this.WordControl.m_oDrawingDocument.m_bIsUpdateDocSize = true;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetPageOrientation);
			if (isPortrait)
			{
				this.WordControl.m_oLogicDocument.Set_DocumentOrientation(Asc.c_oAscPageOrientation.PagePortrait);
				this.DocumentOrientation = isPortrait;
			}
			else
			{
				this.WordControl.m_oLogicDocument.Set_DocumentOrientation(Asc.c_oAscPageOrientation.PageLandscape);
				this.DocumentOrientation = isPortrait;
			}
			this.sync_PageOrientCallback(editor.get_DocumentOrientation());
		}
	};
	asc_docs_api.prototype.get_DocumentOrientation = function()
	{
		return this.DocumentOrientation;
	};
	asc_docs_api.prototype.change_DocSize          = function(width, height)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
		{
			this.WordControl.m_oDrawingDocument.m_bIsUpdateDocSize = true;
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetPageSize);
			if (this.DocumentOrientation)
				this.WordControl.m_oLogicDocument.Set_DocumentPageSize(width, height);
			else
				this.WordControl.m_oLogicDocument.Set_DocumentPageSize(height, width);
		}
	};

	asc_docs_api.prototype.get_DocumentWidth = function()
	{
		return AscCommon.Page_Width;
	};

	asc_docs_api.prototype.get_DocumentHeight = function()
	{
		return AscCommon.Page_Height;
	};

	asc_docs_api.prototype.asc_SetSectionProps       = function(Props)
	{
		this.WordControl.m_oLogicDocument.Set_SectionProps(Props);
	};
	asc_docs_api.prototype.asc_GetSectionProps       = function()
	{
		return this.WordControl.m_oLogicDocument.Get_SectionProps();
	};
	asc_docs_api.prototype.sync_SectionPropsCallback = function(Props)
	{
		this.asc_fireCallback("asc_onSectionProps", Props);
	};
	asc_docs_api.prototype["asc_SetSectionProps"]    = asc_docs_api.prototype.asc_SetSectionProps;
	asc_docs_api.prototype["asc_GetSectionProps"]    = asc_docs_api.prototype.asc_GetSectionProps;

	asc_docs_api.prototype.asc_SetColumnsProps       = function(ColumnsProps)
	{
		this.WordControl.m_oLogicDocument.Set_ColumnsProps(ColumnsProps);
	};
	asc_docs_api.prototype.asc_GetColumnsProps       = function()
	{
		return this.WordControl.m_oLogicDocument.Get_ColumnsProps();
	};
	asc_docs_api.prototype["asc_SetColumnsProps"]    = asc_docs_api.prototype.asc_SetColumnsProps;
	asc_docs_api.prototype["asc_GetColumnsProps"]    = asc_docs_api.prototype.asc_GetColumnsProps;
	asc_docs_api.prototype.sync_ColumnsPropsCallback = function(ColumnsProps)
	{
		this.asc_fireCallback("asc_onColumnsProps", ColumnsProps);
	};

	asc_docs_api.prototype.put_AddPageBreak              = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			var Document = this.WordControl.m_oLogicDocument;

			if (null === Document.Hyperlink_Check(false))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageBreak);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaNewLine(AscCommonWord.break_Page));
			}
		}
	};
	asc_docs_api.prototype.put_AddColumnBreak            = function()
	{
		var Document = this.WordControl.m_oLogicDocument;
		if (false === Document.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			if (null === Document.Hyperlink_Check(false))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageBreak);
				this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaNewLine(AscCommonWord.break_Column));
			}
		}
	};
	asc_docs_api.prototype.Update_ParaInd                = function(Ind)
	{
		var FirstLine = 0,
			Left      = 0,
			Right     = 0;
		if ("undefined" != typeof(Ind))
		{
			if ("undefined" != typeof(Ind.FirstLine))
			{
				FirstLine = Ind.FirstLine;
			}
			if ("undefined" != typeof(Ind.Left))
			{
				Left = Ind.Left;
			}
			if ("undefined" != typeof(Ind.Right))
			{
				Right = Ind.Right;
			}
		}

		var bIsUpdate = false;
		var _ruler    = this.WordControl.m_oHorRuler;
		if (_ruler.m_dIndentLeft != Left)
		{
			_ruler.m_dIndentLeft = Left;
			bIsUpdate            = true;
		}
		if (_ruler != (FirstLine + Left))
		{
			_ruler.m_dIndentLeftFirst = (FirstLine + Left);
			bIsUpdate                 = true;
		}
		if (_ruler.m_dIndentRight != Right)
		{
			_ruler.m_dIndentRight = Right;
			bIsUpdate             = true;
		}
		if (bIsUpdate)
			this.WordControl.UpdateHorRuler();
	};
	asc_docs_api.prototype.Internal_Update_Ind_FirstLine = function(FirstLine, Left)
	{
		if (this.WordControl.m_oHorRuler.m_dIndentLeftFirst != (FirstLine + Left))
		{
			this.WordControl.m_oHorRuler.m_dIndentLeftFirst = (FirstLine + Left);
			this.WordControl.UpdateHorRuler();
		}
	};
	asc_docs_api.prototype.Internal_Update_Ind_Left      = function(Left)
	{
		if (this.WordControl.m_oHorRuler.m_dIndentLeft != Left)
		{
			this.WordControl.m_oHorRuler.m_dIndentLeft = Left;
			this.WordControl.UpdateHorRuler();
		}
	};
	asc_docs_api.prototype.Internal_Update_Ind_Right     = function(Right)
	{
		if (this.WordControl.m_oHorRuler.m_dIndentRight != Right)
		{
			this.WordControl.m_oHorRuler.m_dIndentRight = Right;
			this.WordControl.UpdateHorRuler();
		}
	};

	// "where" где нижний или верхний, align выравнивание
	asc_docs_api.prototype.put_PageNum = function(where, align)
	{
		if (where >= 0)
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_None, {Type : AscCommon.changestype_2_HdrFtr}))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageNumToHdrFtr);
				this.WordControl.m_oLogicDocument.Document_AddPageNum(where, align);
			}
		}
		else
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddPageNumToCurrentPos);
				this.WordControl.m_oLogicDocument.Document_AddPageNum(where, align);
			}
		}
	};

	asc_docs_api.prototype.put_HeadersAndFootersDistance = function(value)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_HdrFtr))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetHdrFtrDistance);
			this.WordControl.m_oLogicDocument.Document_SetHdrFtrDistance(value);
		}
	};

	asc_docs_api.prototype.HeadersAndFooters_DifferentFirstPage = function(isOn)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_HdrFtr))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetHdrFtrFirstPage);
			this.WordControl.m_oLogicDocument.Document_SetHdrFtrFirstPage(isOn);
		}
	};

	asc_docs_api.prototype.HeadersAndFooters_DifferentOddandEvenPage = function(isOn)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_HdrFtr))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetHdrFtrEvenAndOdd);
			this.WordControl.m_oLogicDocument.Document_SetHdrFtrEvenAndOddHeaders(isOn);
		}
	};

	asc_docs_api.prototype.HeadersAndFooters_LinkToPrevious = function(isOn)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_HdrFtr))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetHdrFtrLink);
			this.WordControl.m_oLogicDocument.Document_SetHdrFtrLink(isOn);
		}
	};

	/*структура для передачи настроек колонтитулов
	 {
	 Type : hdrftr_Footer (hdrftr_Header),
	 Position : 12.5,
	 DifferentFirst : true/false,
	 DifferentEvenOdd : true/false,
	 }
	 */
	/*callback*/
	asc_docs_api.prototype.sync_DocSizeCallback               = function(width, height)
	{
		this.asc_fireCallback("asc_onDocSize", width, height);
	};
	asc_docs_api.prototype.sync_PageOrientCallback            = function(isPortrait)
	{
		this.asc_fireCallback("asc_onPageOrient", isPortrait);
	};
	asc_docs_api.prototype.sync_HeadersAndFootersPropCallback = function(hafProp)
	{
		if (true === hafProp)
			hafProp.Locked = true;

		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Header, new CHeaderProp(hafProp));
	};

	/*----------------------------------------------------------------*/
	/*functions for working with table*/
	asc_docs_api.prototype.put_Table               = function(col, row)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Document_Content_Add))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddTable);
			this.WordControl.m_oLogicDocument.Add_InlineTable(col, row);
		}
	};
	asc_docs_api.prototype.addRowAbove             = function(count)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableAddRowAbove);
			this.WordControl.m_oLogicDocument.Table_AddRow(true);
		}
	};
	asc_docs_api.prototype.addRowBelow             = function(count)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableAddRowBelow);
			this.WordControl.m_oLogicDocument.Table_AddRow(false);
		}
	};
	asc_docs_api.prototype.addColumnLeft           = function(count)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableAddColumnLeft);
			this.WordControl.m_oLogicDocument.Table_AddCol(true);
		}
	};
	asc_docs_api.prototype.addColumnRight          = function(count)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableAddColumnRight);
			this.WordControl.m_oLogicDocument.Table_AddCol(false);
		}
	};
	asc_docs_api.prototype.remRow                  = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_RemoveCells))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableRemoveRow);
			this.WordControl.m_oLogicDocument.Table_RemoveRow();
		}
	};
	asc_docs_api.prototype.remColumn               = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_RemoveCells))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_TableRemoveColumn);
			this.WordControl.m_oLogicDocument.Table_RemoveCol();
		}
	};
	asc_docs_api.prototype.remTable                = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_RemoveCells))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveTable);
			this.WordControl.m_oLogicDocument.Table_RemoveTable();
		}
	};
	asc_docs_api.prototype.selectRow               = function()
	{
		this.WordControl.m_oLogicDocument.Table_Select(c_oAscTableSelectionType.Row);
	};
	asc_docs_api.prototype.selectColumn            = function()
	{
		this.WordControl.m_oLogicDocument.Table_Select(c_oAscTableSelectionType.Column);
	};
	asc_docs_api.prototype.selectCell              = function()
	{
		this.WordControl.m_oLogicDocument.Table_Select(c_oAscTableSelectionType.Cell);
	};
	asc_docs_api.prototype.selectTable             = function()
	{
		this.WordControl.m_oLogicDocument.Table_Select(c_oAscTableSelectionType.Table);
	};
	asc_docs_api.prototype.setColumnWidth          = function(width)
	{

	};
	asc_docs_api.prototype.setRowHeight            = function(height)
	{

	};
	asc_docs_api.prototype.set_TblDistanceFromText = function(left, top, right, bottom)
	{

	};
	asc_docs_api.prototype.CheckBeforeMergeCells   = function()
	{
		return this.WordControl.m_oLogicDocument.Table_CheckMerge();
	};
	asc_docs_api.prototype.CheckBeforeSplitCells   = function()
	{
		return this.WordControl.m_oLogicDocument.Table_CheckSplit();
	};
	asc_docs_api.prototype.MergeCells              = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_MergeTableCells);
			this.WordControl.m_oLogicDocument.Table_MergeCells();
		}
	};
	asc_docs_api.prototype.SplitCell               = function(Cols, Rows)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SplitTableCells);
			this.WordControl.m_oLogicDocument.Table_SplitCell(Cols, Rows);
		}
	};
	asc_docs_api.prototype.widthTable              = function(width)
	{

	};
	asc_docs_api.prototype.put_CellsMargin         = function(left, top, right, bottom)
	{

	};
	asc_docs_api.prototype.set_TblWrap             = function(type)
	{

	};
	asc_docs_api.prototype.set_TblIndentLeft       = function(spacing)
	{

	};
	asc_docs_api.prototype.set_Borders             = function(typeBorders, size, Color)
	{//если size == 0 то границы нет.

	};
	asc_docs_api.prototype.set_TableBackground     = function(Color)
	{

	};
	asc_docs_api.prototype.set_AlignCell           = function(align)
	{// c_oAscAlignType.RIGHT, c_oAscAlignType.LEFT, c_oAscAlignType.CENTER
		switch (align)
		{
			case c_oAscAlignType.LEFT :
				break;
			case c_oAscAlignType.CENTER :
				break;
			case c_oAscAlignType.RIGHT :
				break;
		}
	};
	asc_docs_api.prototype.set_TblAlign            = function(align)
	{// c_oAscAlignType.RIGHT, c_oAscAlignType.LEFT, c_oAscAlignType.CENTER
		switch (align)
		{
			case c_oAscAlignType.LEFT :
				break;
			case c_oAscAlignType.CENTER :
				break;
			case c_oAscAlignType.RIGHT :
				break;
		}
	};
	asc_docs_api.prototype.set_SpacingBetweenCells = function(isOn, spacing)
	{// c_oAscAlignType.RIGHT, c_oAscAlignType.LEFT, c_oAscAlignType.CENTER
		if (isOn)
		{

		}
	};

	// CBackground
	// Value : тип заливки(прозрачная или нет),
	// Color : { r : 0, g : 0, b : 0 }
	function CBackground(obj)
	{
		if (obj)
		{
			this.Color = (undefined != obj.Color && null != obj.Color) ? AscCommon.CreateAscColorCustom(obj.Color.r, obj.Color.g, obj.Color.b) : null;
			this.Value = (undefined != obj.Value) ? obj.Value : null;
		}
		else
		{
			this.Color = AscCommon.CreateAscColorCustom(0, 0, 0);
			this.Value = 1;
		}
	}

	CBackground.prototype.get_Color = function()
	{
		return this.Color;
	};
	CBackground.prototype.put_Color = function(v)
	{
		this.Color = (v) ? v : null;
	};
	CBackground.prototype.get_Value = function()
	{
		return this.Value;
	};
	CBackground.prototype.put_Value = function(v)
	{
		this.Value = v;
	};

	function CTablePositionH(obj)
	{
		if (obj)
		{
			this.RelativeFrom = ( undefined === obj.RelativeFrom ) ? Asc.c_oAscHAnchor.Margin : obj.RelativeFrom;
			this.UseAlign     = ( undefined === obj.UseAlign     ) ? false : obj.UseAlign;
			this.Align        = ( undefined === obj.Align        ) ? undefined : obj.Align;
			this.Value        = ( undefined === obj.Value        ) ? 0 : obj.Value;
		}
		else
		{
			this.RelativeFrom = Asc.c_oAscHAnchor.Column;
			this.UseAlign     = false;
			this.Align        = undefined;
			this.Value        = 0;
		}
	}

	CTablePositionH.prototype.get_RelativeFrom = function()
	{
		return this.RelativeFrom;
	};
	CTablePositionH.prototype.put_RelativeFrom = function(v)
	{
		this.RelativeFrom = v;
	};
	CTablePositionH.prototype.get_UseAlign     = function()
	{
		return this.UseAlign;
	};
	CTablePositionH.prototype.put_UseAlign     = function(v)
	{
		this.UseAlign = v;
	};
	CTablePositionH.prototype.get_Align        = function()
	{
		return this.Align;
	};
	CTablePositionH.prototype.put_Align        = function(v)
	{
		this.Align = v;
	};
	CTablePositionH.prototype.get_Value        = function()
	{
		return this.Value;
	};
	CTablePositionH.prototype.put_Value        = function(v)
	{
		this.Value = v;
	};

	function CTablePositionV(obj)
	{
		if (obj)
		{
			this.RelativeFrom = ( undefined === obj.RelativeFrom ) ? Asc.c_oAscVAnchor.Text : obj.RelativeFrom;
			this.UseAlign     = ( undefined === obj.UseAlign     ) ? false : obj.UseAlign;
			this.Align        = ( undefined === obj.Align        ) ? undefined : obj.Align;
			this.Value        = ( undefined === obj.Value        ) ? 0 : obj.Value;
		}
		else
		{
			this.RelativeFrom = Asc.c_oAscVAnchor.Text;
			this.UseAlign     = false;
			this.Align        = undefined;
			this.Value        = 0;
		}
	}

	CTablePositionV.prototype.get_RelativeFrom = function()
	{
		return this.RelativeFrom;
	};
	CTablePositionV.prototype.put_RelativeFrom = function(v)
	{
		this.RelativeFrom = v;
	};
	CTablePositionV.prototype.get_UseAlign     = function()
	{
		return this.UseAlign;
	};
	CTablePositionV.prototype.put_UseAlign     = function(v)
	{
		this.UseAlign = v;
	};
	CTablePositionV.prototype.get_Align        = function()
	{
		return this.Align;
	};
	CTablePositionV.prototype.put_Align        = function(v)
	{
		this.Align = v;
	};
	CTablePositionV.prototype.get_Value        = function()
	{
		return this.Value;
	};
	CTablePositionV.prototype.put_Value        = function(v)
	{
		this.Value = v;
	};

	function CTablePropLook(obj)
	{
		this.FirstCol = false;
		this.FirstRow = false;
		this.LastCol  = false;
		this.LastRow  = false;
		this.BandHor  = false;
		this.BandVer  = false;

		if (obj)
		{
			this.FirstCol = ( undefined === obj.m_bFirst_Col ? false : obj.m_bFirst_Col );
			this.FirstRow = ( undefined === obj.m_bFirst_Row ? false : obj.m_bFirst_Row );
			this.LastCol  = ( undefined === obj.m_bLast_Col ? false : obj.m_bLast_Col );
			this.LastRow  = ( undefined === obj.m_bLast_Row ? false : obj.m_bLast_Row );
			this.BandHor  = ( undefined === obj.m_bBand_Hor ? false : obj.m_bBand_Hor );
			this.BandVer  = ( undefined === obj.m_bBand_Ver ? false : obj.m_bBand_Ver );
		}
	}

	CTablePropLook.prototype.get_FirstCol = function()
	{
		return this.FirstCol;
	};
	CTablePropLook.prototype.put_FirstCol = function(v)
	{
		this.FirstCol = v;
	};
	CTablePropLook.prototype.get_FirstRow = function()
	{
		return this.FirstRow;
	};
	CTablePropLook.prototype.put_FirstRow = function(v)
	{
		this.FirstRow = v;
	};
	CTablePropLook.prototype.get_LastCol  = function()
	{
		return this.LastCol;
	};
	CTablePropLook.prototype.put_LastCol  = function(v)
	{
		this.LastCol = v;
	};
	CTablePropLook.prototype.get_LastRow  = function()
	{
		return this.LastRow;
	};
	CTablePropLook.prototype.put_LastRow  = function(v)
	{
		this.LastRow = v;
	};
	CTablePropLook.prototype.get_BandHor  = function()
	{
		return this.BandHor;
	};
	CTablePropLook.prototype.put_BandHor  = function(v)
	{
		this.BandHor = v;
	};
	CTablePropLook.prototype.get_BandVer  = function()
	{
		return this.BandVer;
	};
	CTablePropLook.prototype.put_BandVer  = function(v)
	{
		this.BandVer = v;
	};

	function CTableProp(tblProp)
	{
		if (tblProp)
		{
			this.CanBeFlow           = (undefined != tblProp.CanBeFlow ? tblProp.CanBeFlow : false );
			this.CellSelect          = (undefined != tblProp.CellSelect ? tblProp.CellSelect : false );
			this.CellSelect          = (undefined != tblProp.CellSelect) ? tblProp.CellSelect : false;
			this.TableWidth          = (undefined != tblProp.TableWidth) ? tblProp.TableWidth : null;
			this.TableSpacing        = (undefined != tblProp.TableSpacing) ? tblProp.TableSpacing : null;
			this.TableDefaultMargins = (undefined != tblProp.TableDefaultMargins && null != tblProp.TableDefaultMargins) ? new Asc.asc_CPaddings(tblProp.TableDefaultMargins) : null;

			this.CellMargins = (undefined != tblProp.CellMargins && null != tblProp.CellMargins) ? new CMargins(tblProp.CellMargins) : null;

			this.TableAlignment     = (undefined != tblProp.TableAlignment) ? tblProp.TableAlignment : null;
			this.TableIndent        = (undefined != tblProp.TableIndent) ? tblProp.TableIndent : null;
			this.TableWrappingStyle = (undefined != tblProp.TableWrappingStyle) ? tblProp.TableWrappingStyle : null;

			this.TablePaddings = (undefined != tblProp.TablePaddings && null != tblProp.TablePaddings) ? new Asc.asc_CPaddings(tblProp.TablePaddings) : null;

			this.TableBorders      = (undefined != tblProp.TableBorders && null != tblProp.TableBorders) ? new CBorders(tblProp.TableBorders) : null;
			this.CellBorders       = (undefined != tblProp.CellBorders && null != tblProp.CellBorders) ? new CBorders(tblProp.CellBorders) : null;
			this.TableBackground   = (undefined != tblProp.TableBackground && null != tblProp.TableBackground) ? new CBackground(tblProp.TableBackground) : null;
			this.CellsBackground   = (undefined != tblProp.CellsBackground && null != tblProp.CellsBackground) ? new CBackground(tblProp.CellsBackground) : null;
			this.Position          = (undefined != tblProp.Position && null != tblProp.Position) ? new Asc.CPosition(tblProp.Position) : null;
			this.PositionH         = ( undefined != tblProp.PositionH && null != tblProp.PositionH ) ? new CTablePositionH(tblProp.PositionH) : undefined;
			this.PositionV         = ( undefined != tblProp.PositionV && null != tblProp.PositionV ) ? new CTablePositionV(tblProp.PositionV) : undefined;
			this.Internal_Position = ( undefined != tblProp.Internal_Position ) ? tblProp.Internal_Position : undefined;

			this.ForSelectedCells   = (undefined != tblProp.ForSelectedCells) ? tblProp.ForSelectedCells : true;
			this.TableStyle         = (undefined != tblProp.TableStyle) ? tblProp.TableStyle : null;
			this.TableLook          = (undefined != tblProp.TableLook) ? new CTablePropLook(tblProp.TableLook) : null;
			this.RowsInHeader       = (undefined != tblProp.RowsInHeader) ? tblProp.RowsInHeader : 0;
			this.CellsVAlign        = (undefined != tblProp.CellsVAlign) ? tblProp.CellsVAlign : c_oAscVertAlignJc.Top;
			this.AllowOverlap       = (undefined != tblProp.AllowOverlap) ? tblProp.AllowOverlap : undefined;
			this.TableLayout        = tblProp.TableLayout;
			this.CellsTextDirection = tblProp.CellsTextDirection;
			this.CellsNoWrap        = tblProp.CellsNoWrap;
			this.CellsWidth         = tblProp.CellsWidth;
			this.Locked             = (undefined != tblProp.Locked) ? tblProp.Locked : false;
			this.PercentFullWidth   = tblProp.PercentFullWidth;
		}
		else
		{
			//Все свойства класса CTableProp должны быть undefined если они не изменялись
			//this.CanBeFlow = false;
			this.CellSelect = false; //обязательное свойство
			/*this.TableWidth = null;
			 this.TableSpacing = null;
			 this.TableDefaultMargins = new Asc.asc_CPaddings ();

			 this.CellMargins = new CMargins ();

			 this.TableAlignment = 0;
			 this.TableIndent = 0;
			 this.TableWrappingStyle = c_oAscWrapStyle.Inline;

			 this.TablePaddings = new Asc.asc_CPaddings ();

			 this.TableBorders = new CBorders ();
			 this.CellBorders = new CBorders ();
			 this.TableBackground = new CBackground ();
			 this.CellsBackground = new CBackground ();;
			 this.Position = new CPosition ();
			 this.ForSelectedCells = true;*/

			this.Locked = false;
		}
	}

	CTableProp.prototype.get_Width              = function()
	{
		return this.TableWidth;
	};
	CTableProp.prototype.put_Width              = function(v)
	{
		this.TableWidth = v;
	};
	CTableProp.prototype.get_Spacing            = function()
	{
		return this.TableSpacing;
	};
	CTableProp.prototype.put_Spacing            = function(v)
	{
		this.TableSpacing = v;
	};
	CTableProp.prototype.get_DefaultMargins     = function()
	{
		return this.TableDefaultMargins;
	};
	CTableProp.prototype.put_DefaultMargins     = function(v)
	{
		this.TableDefaultMargins = v;
	};
	CTableProp.prototype.get_CellMargins        = function()
	{
		return this.CellMargins;
	};
	CTableProp.prototype.put_CellMargins        = function(v)
	{
		this.CellMargins = v;
	};
	CTableProp.prototype.get_TableAlignment     = function()
	{
		return this.TableAlignment;
	};
	CTableProp.prototype.put_TableAlignment     = function(v)
	{
		this.TableAlignment = v;
	};
	CTableProp.prototype.get_TableIndent        = function()
	{
		return this.TableIndent;
	};
	CTableProp.prototype.put_TableIndent        = function(v)
	{
		this.TableIndent = v;
	};
	CTableProp.prototype.get_TableWrap          = function()
	{
		return this.TableWrappingStyle;
	};
	CTableProp.prototype.put_TableWrap          = function(v)
	{
		this.TableWrappingStyle = v;
	};
	CTableProp.prototype.get_TablePaddings      = function()
	{
		return this.TablePaddings;
	};
	CTableProp.prototype.put_TablePaddings      = function(v)
	{
		this.TablePaddings = v;
	};
	CTableProp.prototype.get_TableBorders       = function()
	{
		return this.TableBorders;
	};
	CTableProp.prototype.put_TableBorders       = function(v)
	{
		this.TableBorders = v;
	};
	CTableProp.prototype.get_CellBorders        = function()
	{
		return this.CellBorders;
	};
	CTableProp.prototype.put_CellBorders        = function(v)
	{
		this.CellBorders = v;
	};
	CTableProp.prototype.get_TableBackground    = function()
	{
		return this.TableBackground;
	};
	CTableProp.prototype.put_TableBackground    = function(v)
	{
		this.TableBackground = v;
	};
	CTableProp.prototype.get_CellsBackground    = function()
	{
		return this.CellsBackground;
	};
	CTableProp.prototype.put_CellsBackground    = function(v)
	{
		this.CellsBackground = v;
	};
	CTableProp.prototype.get_Position           = function()
	{
		return this.Position;
	};
	CTableProp.prototype.put_Position           = function(v)
	{
		this.Position = v;
	};
	CTableProp.prototype.get_PositionH          = function()
	{
		return this.PositionH;
	};
	CTableProp.prototype.put_PositionH          = function(v)
	{
		this.PositionH = v;
	};
	CTableProp.prototype.get_PositionV          = function()
	{
		return this.PositionV;
	};
	CTableProp.prototype.put_PositionV          = function(v)
	{
		this.PositionV = v;
	};
	CTableProp.prototype.get_Value_X            = function(RelativeFrom)
	{
		if (undefined != this.Internal_Position) return this.Internal_Position.Calculate_X_Value(RelativeFrom);
		return 0;
	};
	CTableProp.prototype.get_Value_Y            = function(RelativeFrom)
	{
		if (undefined != this.Internal_Position) return this.Internal_Position.Calculate_Y_Value(RelativeFrom);
		return 0;
	};
	CTableProp.prototype.get_ForSelectedCells   = function()
	{
		return this.ForSelectedCells;
	};
	CTableProp.prototype.put_ForSelectedCells   = function(v)
	{
		this.ForSelectedCells = v;
	};
	CTableProp.prototype.put_CellSelect         = function(v)
	{
		this.CellSelect = v;
	};
	CTableProp.prototype.get_CellSelect         = function()
	{
		return this.CellSelect
	};
	CTableProp.prototype.get_CanBeFlow          = function()
	{
		return this.CanBeFlow;
	};
	CTableProp.prototype.get_RowsInHeader       = function()
	{
		return this.RowsInHeader;
	};
	CTableProp.prototype.put_RowsInHeader       = function(v)
	{
		this.RowsInHeader = v;
	};
	CTableProp.prototype.get_Locked             = function()
	{
		return this.Locked;
	};
	CTableProp.prototype.get_CellsVAlign        = function()
	{
		return this.CellsVAlign;
	};
	CTableProp.prototype.put_CellsVAlign        = function(v)
	{
		this.CellsVAlign = v;
	};
	CTableProp.prototype.get_TableLook          = function()
	{
		return this.TableLook;
	};
	CTableProp.prototype.put_TableLook          = function(v)
	{
		this.TableLook = v;
	};
	CTableProp.prototype.get_TableStyle         = function()
	{
		return this.TableStyle;
	};
	CTableProp.prototype.put_TableStyle         = function(v)
	{
		this.TableStyle = v;
	};
	CTableProp.prototype.get_AllowOverlap       = function()
	{
		return this.AllowOverlap;
	};
	CTableProp.prototype.put_AllowOverlap       = function(v)
	{
		this.AllowOverlap = v;
	};
	CTableProp.prototype.get_TableLayout        = function()
	{
		return this.TableLayout;
	};
	CTableProp.prototype.put_TableLayout        = function(v)
	{
		this.TableLayout = v;
	};
	CTableProp.prototype.get_CellsTextDirection = function()
	{
		return this.CellsTextDirection;
	};
	CTableProp.prototype.put_CellsTextDirection = function(v)
	{
		this.CellsTextDirection = v;
	};
	CTableProp.prototype.get_CellsNoWrap        = function()
	{
		return this.CellsNoWrap;
	};
	CTableProp.prototype.put_CellsNoWrap        = function(v)
	{
		this.CellsNoWrap = v;
	};
	CTableProp.prototype.get_CellsWidth         = function()
	{
		return this.CellsWidth;
	};
	CTableProp.prototype.put_CellsWidth         = function(v)
	{
		this.CellsWidth = v;
	};
	CTableProp.prototype.get_PercentFullWidth   = function()
	{
		return this.PercentFullWidth;
	};


	function CBorders(obj)
	{
		if (obj)
		{
			this.Left    = (undefined != obj.Left && null != obj.Left) ? new Asc.asc_CTextBorder(obj.Left) : null;
			this.Top     = (undefined != obj.Top && null != obj.Top) ? new Asc.asc_CTextBorder(obj.Top) : null;
			this.Right   = (undefined != obj.Right && null != obj.Right) ? new Asc.asc_CTextBorder(obj.Right) : null;
			this.Bottom  = (undefined != obj.Bottom && null != obj.Bottom) ? new Asc.asc_CTextBorder(obj.Bottom) : null;
			this.InsideH = (undefined != obj.InsideH && null != obj.InsideH) ? new Asc.asc_CTextBorder(obj.InsideH) : null;
			this.InsideV = (undefined != obj.InsideV && null != obj.InsideV) ? new Asc.asc_CTextBorder(obj.InsideV) : null;
		}
		//Все свойства класса CBorders должны быть undefined если они не изменялись
		/*else
		 {
		 this.Left = null;
		 this.Top = null;
		 this.Right = null;
		 this.Bottom = null;
		 this.InsideH = null;
		 this.InsideV = null;
		 }*/
	}

	CBorders.prototype.get_Left    = function()
	{
		return this.Left;
	};
	CBorders.prototype.put_Left    = function(v)
	{
		this.Left = (v) ? new Asc.asc_CTextBorder(v) : null;
	};
	CBorders.prototype.get_Top     = function()
	{
		return this.Top;
	};
	CBorders.prototype.put_Top     = function(v)
	{
		this.Top = (v) ? new Asc.asc_CTextBorder(v) : null;
	};
	CBorders.prototype.get_Right   = function()
	{
		return this.Right;
	};
	CBorders.prototype.put_Right   = function(v)
	{
		this.Right = (v) ? new Asc.asc_CTextBorder(v) : null;
	};
	CBorders.prototype.get_Bottom  = function()
	{
		return this.Bottom;
	};
	CBorders.prototype.put_Bottom  = function(v)
	{
		this.Bottom = (v) ? new Asc.asc_CTextBorder(v) : null;
	};
	CBorders.prototype.get_InsideH = function()
	{
		return this.InsideH;
	};
	CBorders.prototype.put_InsideH = function(v)
	{
		this.InsideH = (v) ? new Asc.asc_CTextBorder(v) : null;
	};
	CBorders.prototype.get_InsideV = function()
	{
		return this.InsideV;
	};
	CBorders.prototype.put_InsideV = function(v)
	{
		this.InsideV = (v) ? new Asc.asc_CTextBorder(v) : null;
	};


	// CMargins
	function CMargins(obj)
	{
		if (obj)
		{
			this.Left   = (undefined != obj.Left) ? obj.Left : null;
			this.Right  = (undefined != obj.Right) ? obj.Right : null;
			this.Top    = (undefined != obj.Top) ? obj.Top : null;
			this.Bottom = (undefined != obj.Bottom) ? obj.Bottom : null;
			this.Flag   = (undefined != obj.Flag) ? obj.Flag : null;
		}
		else
		{
			this.Left   = null;
			this.Right  = null;
			this.Top    = null;
			this.Bottom = null;
			this.Flag   = null;
		}
	}

	CMargins.prototype.get_Left   = function()
	{
		return this.Left;
	};
	CMargins.prototype.put_Left   = function(v)
	{
		this.Left = v;
	};
	CMargins.prototype.get_Right  = function()
	{
		return this.Right;
	};
	CMargins.prototype.put_Right  = function(v)
	{
		this.Right = v;
	};
	CMargins.prototype.get_Top    = function()
	{
		return this.Top;
	};
	CMargins.prototype.put_Top    = function(v)
	{
		this.Top = v;
	};
	CMargins.prototype.get_Bottom = function()
	{
		return this.Bottom;
	};
	CMargins.prototype.put_Bottom = function(v)
	{
		this.Bottom = v;
	};
	CMargins.prototype.get_Flag   = function()
	{
		return this.Flag;
	};
	CMargins.prototype.put_Flag   = function(v)
	{
		this.Flag = v;
	};

	/*
	 {
	 TableWidth   : null - галочка убрана, либо заданное значение в мм
	 TableSpacing : null - галочка убрана, либо заданное значение в мм

	 TableDefaultMargins :  // маргины для всей таблицы(значение по умолчанию)
	 {
	 Left   : 1.9,
	 Right  : 1.9,
	 Top    : 0,
	 Bottom : 0
	 }

	 CellMargins :
	 {
	 Left   : 1.9, (null - неопределенное значение)
	 Right  : 1.9, (null - неопределенное значение)
	 Top    : 0,   (null - неопределенное значение)
	 Bottom : 0,   (null - неопределенное значение)
	 Flag   : 0 - У всех выделенных ячеек значение берется из TableDefaultMargins
	 1 - У выделенных ячеек есть ячейки с дефолтовыми значениями, и есть со своими собственными
	 2 - У всех ячеек свои собственные значения
	 }

	 TableAlignment : 0, 1, 2 (слева, по центру, справа)
	 TableIndent : значение в мм,
	 TableWrappingStyle : 0, 1 (inline, flow)
	 TablePaddings:
	 {
	 Left   : 3.2,
	 Right  : 3.2,
	 Top    : 0,
	 Bottom : 0
	 }

	 TableBorders : // границы таблицы
	 {
	 Bottom :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Left :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Right :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Top :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 InsideH :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 InsideV :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 }
	 }

	 CellBorders : // границы выделенных ячеек
	 {
	 ForSelectedCells : true,

	 Bottom :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Left :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Right :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 Top :
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 InsideH : // данного элемента может не быть, если у выделенных ячеек
	 // нет горизонтальных внутренних границ
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 },

	 InsideV : // данного элемента может не быть, если у выделенных ячеек
	 // нет вертикальных внутренних границ
	 {
	 Color : { r : 0, g : 0, b : 0 },
	 Value : border_Single,
	 Size  : 0.5 * g_dKoef_pt_to_mm
	 Space :
	 }
	 }

	 TableBackground :
	 {
	 Value : тип заливки(прозрачная или нет),
	 Color : { r : 0, g : 0, b : 0 }
	 }
	 CellsBackground : null если заливка не определена для выделенных ячеек
	 {
	 Value : тип заливки(прозрачная или нет),
	 Color : { r : 0, g : 0, b : 0 }
	 }

	 Position:
	 {
	 X:0,
	 Y:0
	 }
	 }
	 */
	asc_docs_api.prototype.tblApply = function(obj)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Table_Properties))
		{
			if (obj.CellBorders)
			{
				if (obj.CellBorders.Left && obj.CellBorders.Left.Color)
				{
					obj.CellBorders.Left.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.Left.Color);
				}
				if (obj.CellBorders.Top && obj.CellBorders.Top.Color)
				{
					obj.CellBorders.Top.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.Top.Color);
				}
				if (obj.CellBorders.Right && obj.CellBorders.Right.Color)
				{
					obj.CellBorders.Right.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.Right.Color);
				}
				if (obj.CellBorders.Bottom && obj.CellBorders.Bottom.Color)
				{
					obj.CellBorders.Bottom.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.Bottom.Color);
				}
				if (obj.CellBorders.InsideH && obj.CellBorders.InsideH.Color)
				{
					obj.CellBorders.InsideH.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.InsideH.Color);
				}
				if (obj.CellBorders.InsideV && obj.CellBorders.InsideV.Color)
				{
					obj.CellBorders.InsideV.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellBorders.InsideV.Color);
				}
			}
			if (obj.CellsBackground && obj.CellsBackground.Color)
			{
				obj.CellsBackground.Unifill = AscFormat.CreateUnifillFromAscColor(obj.CellsBackground.Color);
			}

			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ApplyTablePr);
			this.WordControl.m_oLogicDocument.Set_TableProps(obj);
		}
	};
	/*callbacks*/
	asc_docs_api.prototype.sync_AddTableCallback            = function()
	{
		this.asc_fireCallback("asc_onAddTable");
	};
	asc_docs_api.prototype.sync_AlignCellCallback           = function(align)
	{
		this.asc_fireCallback("asc_onAlignCell", align);
	};
	asc_docs_api.prototype.sync_TblPropCallback             = function(tblProp)
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//    tblProp.Locked = true;

		// TODO: вызвать функцию asc_onInitTableTemplatesв зависимости от TableLook
		if (tblProp.CellsBackground && tblProp.CellsBackground.Unifill)
		{
			var LogicDocument = this.WordControl.m_oLogicDocument;
			tblProp.CellsBackground.Unifill.check(LogicDocument.Get_Theme(), LogicDocument.Get_ColorMap());
			var RGBA                      = tblProp.CellsBackground.Unifill.getRGBAColor();
			tblProp.CellsBackground.Color = new AscCommonWord.CDocumentColor(RGBA.R, RGBA.G, RGBA.B, false);
		}
		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Table, new CTableProp(tblProp));
	};
	asc_docs_api.prototype.sync_TblWrapStyleChangedCallback = function(style)
	{
		this.asc_fireCallback("asc_onTblWrapStyleChanged", style);
	};
	asc_docs_api.prototype.sync_TblAlignChangedCallback     = function(style)
	{
		this.asc_fireCallback("asc_onTblAlignChanged", style);
	};

	/*----------------------------------------------------------------*/
	/*functions for working with images*/
	asc_docs_api.prototype.ChangeImageFromFile      = function()
	{
		this.isImageChangeUrl = true;
		this.asc_addImage();
	};
	asc_docs_api.prototype.ChangeShapeImageFromFile = function()
	{
		this.isShapeImageChangeUrl = true;
		this.asc_addImage();
	};

	asc_docs_api.prototype.AddImage     = function()
	{
		this.asc_addImage();
	};
	asc_docs_api.prototype.AddImageUrl2 = function(url)
	{
		this.AddImageUrl(AscCommon.getFullImageSrc2(url));
	};

	asc_docs_api.prototype._addImageUrl      = function(url)
	{
		// ToDo пока временная функция для стыковки.
		this.AddImageUrl(url);
	};
	asc_docs_api.prototype.AddImageUrl       = function(url, imgProp, callback)
	{
		if (g_oDocumentUrls.getLocal(url))
		{
			this.AddImageUrlAction(url, imgProp);
		}
		else
		{
			var t = this;
			if (!callback) {
				callback = function (url) {
					//g_oDocumentUrls.addUrls(urls);
					t.AddImageUrlAction('jio:' + url, imgProp);
				};
			}
			//this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.UploadImage);
			return new RSVP.Queue()
				.push(function () {
					return url;
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
		}
	};
	asc_docs_api.prototype.AddImageUrlAction = function(url, imgProp)
	{
		var _image = this.ImageLoader.LoadImage(url, 1);
		if (null != _image)
		{
			var _w = Math.max(1, AscCommon.Page_Width - (AscCommon.X_Left_Margin + AscCommon.X_Right_Margin));
			var _h = Math.max(1, AscCommon.Page_Height - (AscCommon.Y_Top_Margin + AscCommon.Y_Bottom_Margin));
			if (_image.Image != null)
			{
				var __w = Math.max(parseInt(_image.Image.width * AscCommon.g_dKoef_pix_to_mm), 1);
				var __h = Math.max(parseInt(_image.Image.height * AscCommon.g_dKoef_pix_to_mm), 1);
				_w      = Math.max(5, Math.min(_w, __w));
				_h      = Math.max(5, Math.min(parseInt(_w * __h / __w)));
			}

			var src = _image.src;
			if (this.isShapeImageChangeUrl)
			{
				var AscShapeProp       = new Asc.asc_CShapeProperty();
				AscShapeProp.fill      = new asc_CShapeFill();
				AscShapeProp.fill.type = c_oAscFill.FILL_TYPE_BLIP;
				AscShapeProp.fill.fill = new asc_CFillBlip();
				AscShapeProp.fill.fill.asc_putUrl(src);
				this.ImgApply(new asc_CImgProperty({ShapeProperties : AscShapeProp}));
				this.isShapeImageChangeUrl = false;
			}
			else if (this.isImageChangeUrl)
			{
				var AscImageProp      = new asc_CImgProperty();
				AscImageProp.ImageUrl = src;
				this.ImgApply(AscImageProp);
				this.isImageChangeUrl = false;
			}
			else
			{
				if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
				{
					var imageLocal = g_oDocumentUrls.getImageLocal(src);
					if (imageLocal)
					{
						src = imageLocal;
					}

					this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddImageUrl);
					if (undefined === imgProp || undefined === imgProp.WrappingStyle || 0 == imgProp.WrappingStyle)
						this.WordControl.m_oLogicDocument.Add_InlineImage(_w, _h, src);
					else
						this.WordControl.m_oLogicDocument.Add_InlineImage(_w, _h, src, null, true);
				}
			}
		}
		else
		{
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);
			this.asyncImageEndLoaded2 = function(_image)
			{
				var _w = Math.max(1, AscCommon.Page_Width - (AscCommon.X_Left_Margin + AscCommon.X_Right_Margin));
				var _h = Math.max(1, AscCommon.Page_Height - (AscCommon.Y_Top_Margin + AscCommon.Y_Bottom_Margin));
				if (_image.Image != null)
				{
					var __w = Math.max(parseInt(_image.Image.width * AscCommon.g_dKoef_pix_to_mm), 1);
					var __h = Math.max(parseInt(_image.Image.height * AscCommon.g_dKoef_pix_to_mm), 1);
					_w      = Math.max(5, Math.min(_w, __w));
					_h      = Math.max(5, Math.min(parseInt(_w * __h / __w)));
				}
				var src = _image.src;

				if (this.isShapeImageChangeUrl)
				{
					var AscShapeProp       = new Asc.asc_CShapeProperty();
					AscShapeProp.fill      = new asc_CShapeFill();
					AscShapeProp.fill.type = c_oAscFill.FILL_TYPE_BLIP;
					AscShapeProp.fill.fill = new asc_CFillBlip();
					AscShapeProp.fill.fill.asc_putUrl(src);
					this.ImgApply(new asc_CImgProperty({ShapeProperties : AscShapeProp}));
					this.isShapeImageChangeUrl = false;
				}
				else if (this.isImageChangeUrl)
				{
					var AscImageProp      = new asc_CImgProperty();
					AscImageProp.ImageUrl = src;
					this.ImgApply(AscImageProp);
					this.isImageChangeUrl = false;
				}
				else
				{

					if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
					{
						var imageLocal = g_oDocumentUrls.getImageLocal(src);
						if (imageLocal)
						{
							src = imageLocal;
						}
						this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddImageUrlLong);
						if (undefined === imgProp || undefined === imgProp.WrappingStyle || 0 == imgProp.WrappingStyle)
							this.WordControl.m_oLogicDocument.Add_InlineImage(_w, _h, src);
						else
							this.WordControl.m_oLogicDocument.Add_InlineImage(_w, _h, src, null, true);
					}
				}
				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);

				this.asyncImageEndLoaded2 = null;
			}
		}
	};
	/*
	 Добавляем картинку на заданную страницу. Преполагаем, что картинка уже доступна по ссылке.
	 */
	asc_docs_api.prototype.AddImageToPage = function(sUrl, nPageIndex, dX, dY, dW, dH)
	{
		var LogicDocument = this.WordControl.m_oLogicDocument;

		var oldClickCount            = global_mouseEvent.ClickCount;
		global_mouseEvent.Button     = 0;
		global_mouseEvent.ClickCount = 1;
		LogicDocument.OnMouseDown(global_mouseEvent, dX, dY, nPageIndex);
		LogicDocument.OnMouseUp(global_mouseEvent, dX, dY, nPageIndex);
		LogicDocument.OnMouseMove(global_mouseEvent, dX, dY, nPageIndex);
		global_mouseEvent.ClickCount = oldClickCount;

		if (false === LogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			var oPosH = new Asc.CImagePositionH();
			oPosH.put_RelativeFrom(Asc.c_oAscRelativeFromH.Page);
			oPosH.put_Align(false);
			oPosH.put_Value(dX);
			var oPosV = new Asc.CImagePositionV();
			oPosV.put_RelativeFrom(Asc.c_oAscRelativeFromV.Page);
			oPosV.put_Align(false);
			oPosV.put_Value(dY);
			var oImageProps = new asc_CImgProperty();
			oImageProps.asc_putWrappingStyle(c_oAscWrapStyle2.Square);
			oImageProps.asc_putPositionH(oPosH);
			oImageProps.asc_putPositionV(oPosV);

			LogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddImageToPage);
			LogicDocument.Start_SilentMode();
			LogicDocument.Add_InlineImage(dW, dH, sUrl);
			LogicDocument.Set_ImageProps(oImageProps);
			LogicDocument.End_SilentMode(true);
		}
	};
	/* В качестве параметра  передается объект класса Asc.asc_CImgProperty, он же приходит на OnImgProp
	 Asc.asc_CImgProperty заменяет пережнюю структуру:
	 если параметр не имеет значения то передвать следует null, напримере inline-картинок: в качестве left,top,bottom,right,X,Y,ImageUrl необходимо передавать null.
	 {
	 Width: 0,
	 Height: 0,
	 WrappingStyle: 0,
	 Paddings: { Left : 0, Top : 0, Bottom: 0, Right: 0 },
	 Position : {X : 0, Y : 0},
	 ImageUrl : ""
	 }
	 */
	asc_docs_api.prototype.ImgApply                = function(obj)
	{

		if (!AscCommon.isRealObject(obj))
			return;
		var ImagePr = obj, AdditionalData, LogicDocument = this.WordControl.m_oLogicDocument;

		/*проверка корректности данных для биржевой диаграммы*/
		if (obj.ChartProperties && obj.ChartProperties.type === Asc.c_oAscChartTypeSettings.stock)
		{
			if (!AscFormat.CheckStockChart(this.WordControl.m_oLogicDocument.DrawingObjects, this))
			{
				return;
			}
		}

		/*изменение z-индекса*/
		if (AscFormat.isRealNumber(ImagePr.ChangeLevel))
		{
			switch (ImagePr.ChangeLevel)
			{
				case 0:
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.bringToFront();
					break;
				}
				case 1:
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.bringForward();
					break;
				}
				case 2:
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.sendToBack();
					break;
				}
				case 3:
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.bringBackward();
				}
			}
			return;
		}

		/*параграфы в которых лежат выделенные ParaDrawing*/
		var aParagraphs = [], aSelectedObjects = this.WordControl.m_oLogicDocument.DrawingObjects.selectedObjects, i, j, oParentParagraph;
		for (i = 0; i < aSelectedObjects.length; ++i)
		{
			oParentParagraph = aSelectedObjects[i].parent.Get_ParentParagraph();
			AscFormat.checkObjectInArray(aParagraphs, oParentParagraph);
		}


		AdditionalData = {
			Type      : AscCommon.changestype_2_ElementsArray_and_Type,
			Elements  : aParagraphs,
			CheckType : changestype_Paragraph_Content
		};
		/*группировка и разгруппировка*/
		if (ImagePr.Group === 1 || ImagePr.Group === -1)
		{
			if (false == this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Drawing_Props, AdditionalData))
			{
				History.Create_NewPoint(AscDFH.historydescription_Document_GroupUnGroup);
				if (ImagePr.Group === 1)
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.groupSelectedObjects();
				}
				else
				{
					this.WordControl.m_oLogicDocument.DrawingObjects.unGroupSelectedObjects();
				}
			}
			return;
		}


		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Image_Properties))
		{
			if (ImagePr.ShapeProperties)
				ImagePr.ImageUrl = "";


			var sImageUrl = null, fReplaceCallback = null, bImageUrl = false, sImageToDownLoad = "";
			if (!AscCommon.isNullOrEmptyString(ImagePr.ImageUrl))
			{
				if (!g_oDocumentUrls.getImageLocal(ImagePr.ImageUrl))
				{
					sImageUrl        = ImagePr.ImageUrl;
					fReplaceCallback = function(sUrl)
					{
						ImagePr.ImageUrl = sUrl;
						sImageToDownLoad = sUrl;
					}
				}
				sImageToDownLoad = ImagePr.ImageUrl;
			}
			else if (ImagePr.ShapeProperties && ImagePr.ShapeProperties.fill &&
				ImagePr.ShapeProperties.fill.fill && !AscCommon.isNullOrEmptyString(ImagePr.ShapeProperties.fill.fill.url))
			{
				if (!g_oDocumentUrls.getImageLocal(ImagePr.ShapeProperties.fill.fill.url))
				{
					sImageUrl        = ImagePr.ShapeProperties.fill.fill.url;
					fReplaceCallback = function(sUrl)
					{
						ImagePr.ShapeProperties.fill.fill.url = sUrl;
						sImageToDownLoad                      = sUrl;
					}
				}
				sImageToDownLoad = ImagePr.ShapeProperties.fill.fill.url;
			}

			var oApi = this;

			if (!AscCommon.isNullOrEmptyString(sImageToDownLoad))
			{

				var fApplyCallback = function()
				{
					var _img = oApi.ImageLoader.LoadImage(sImageToDownLoad, 1);
					if (null != _img)
					{
						oApi.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ApplyImagePrWithUrl);
						oApi.WordControl.m_oLogicDocument.Set_ImageProps(ImagePr);
					}
					else
					{
						oApi.asyncImageEndLoaded2 = function(_image)
						{
							oApi.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ApplyImagePrWithUrlLong);
							oApi.WordControl.m_oLogicDocument.Set_ImageProps(ImagePr);
						}
					}
				};

				if (sImageUrl)
				{

					if (window["AscDesktopEditor"])
					{
						var _url = window["AscDesktopEditor"]["LocalFileGetImageUrl"](sImageToDownLoad);
						_url     = g_oDocumentUrls.getImageUrl(_url);
						fReplaceCallback(_url);
						fApplyCallback();
						return;
					}

					this.AddImageUrl(sImageToDownLoad, undefined, function (url) {
						//g_oDocumentUrls.addUrls(urls);
						fReplaceCallback('jio:' + url);
						fApplyCallback();
					});
				}
				else
				{
					fApplyCallback();
				}
			}
			else
			{
				ImagePr.ImageUrl = null;
				if (!this.noCreatePoint || this.exucuteHistory)
				{
					if (!this.noCreatePoint && !this.exucuteHistory && this.exucuteHistoryEnd)
					{
						if (-1 !== this.nCurPointItemsLength)
						{
							History.UndoLastPoint();
						}
						else
						{
							History.Create_NewPoint(AscDFH.historydescription_Document_ApplyImagePr);
						}
						this.WordControl.m_oLogicDocument.Set_ImageProps(ImagePr);
						this.exucuteHistoryEnd    = false;
						this.nCurPointItemsLength = -1;
					}
					else
					{
						this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ApplyImagePr);
						this.WordControl.m_oLogicDocument.Set_ImageProps(ImagePr);
					}
					if (this.exucuteHistory)
					{
						this.exucuteHistory = false;
						var oPoint          = History.Points[History.Index];
						if (oPoint)
						{
							this.nCurPointItemsLength = oPoint.Items.length;
						}
					}
				}
				else
				{
					var bNeedCheckChangesCount = false;
					if (-1 !== this.nCurPointItemsLength)
					{
						History.UndoLastPoint();
					}
					else
					{
						bNeedCheckChangesCount = true;
						History.Create_NewPoint(AscDFH.historydescription_Document_ApplyImagePr);
					}
					this.WordControl.m_oLogicDocument.Set_ImageProps(ImagePr);
					if (bNeedCheckChangesCount)
					{
						var oPoint = History.Points[History.Index];
						if (oPoint)
						{
							this.nCurPointItemsLength = oPoint.Items.length;
						}
					}
				}
			}
		}
	};
	asc_docs_api.prototype.set_Size                = function(width, height)
	{

	};
	asc_docs_api.prototype.set_ConstProportions    = function(isOn)
	{
		if (isOn)
		{

		}
		else
		{

		}
	};
	asc_docs_api.prototype.set_WrapStyle           = function(type)
	{

	};
	asc_docs_api.prototype.deleteImage             = function()
	{

	};
	asc_docs_api.prototype.set_ImgDistanceFromText = function(left, top, right, bottom)
	{

	};
	asc_docs_api.prototype.set_PositionOnPage      = function(X, Y)
	{//расположение от начала страницы

	};
	asc_docs_api.prototype.get_OriginalSizeImage   = function()
	{
		if (0 == this.SelectedObjectsStack.length)
			return null;
		var obj = this.SelectedObjectsStack[this.SelectedObjectsStack.length - 1];
		if (obj == null)
			return null;
		if (obj.Type == c_oAscTypeSelectElement.Image)
			return obj.Value.asc_getOriginSize(this);
	};

	asc_docs_api.prototype.ShapeApply = function(shapeProps)
	{
		// нужно определить, картинка это или нет
		var image_url = "";
		if (shapeProps.fill != null)
		{
			if (shapeProps.fill.fill != null && shapeProps.fill.type == c_oAscFill.FILL_TYPE_BLIP)
			{
				image_url = shapeProps.fill.fill.asc_getUrl();

				var _tx_id = shapeProps.fill.fill.asc_getTextureId();
				if (null != _tx_id && 0 <= _tx_id && _tx_id < AscCommon.g_oUserTexturePresets.length)
				{
					image_url = AscCommon.g_oUserTexturePresets[_tx_id];
				}
			}
		}
		if (image_url != "")
		{
			var _image = this.ImageLoader.LoadImage(image_url, 1);

			var imageLocal = g_oDocumentUrls.getImageLocal(image_url);
			if (imageLocal)
			{
				shapeProps.fill.fill.asc_putUrl(imageLocal); // erase documentUrl
			}

			if (null != _image)
			{
				this.WordControl.m_oLogicDocument.ShapeApply(shapeProps);
				this.WordControl.m_oDrawingDocument.DrawImageTextureFillShape(image_url);
			}
			else
			{
				this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);

				var oProp                 = shapeProps;
				this.asyncImageEndLoaded2 = function(_image)
				{
					this.WordControl.m_oLogicDocument.ShapeApply(oProp);
					this.WordControl.m_oDrawingDocument.DrawImageTextureFillShape(image_url);

					this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);
					this.asyncImageEndLoaded2 = null;
				}
			}
		}
		else
		{
			this.WordControl.m_oLogicDocument.ShapeApply(shapeProps);
		}
	};
	/*callbacks*/
	asc_docs_api.prototype.sync_AddImageCallback            = function()
	{
		this.asc_fireCallback("asc_onAddImage");
	};
	asc_docs_api.prototype.sync_ImgPropCallback             = function(imgProp)
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//    imgProp.Locked = true;

		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Image, new asc_CImgProperty(imgProp));
	};
	asc_docs_api.prototype.sync_ImgWrapStyleChangedCallback = function(style)
	{
		this.asc_fireCallback("asc_onImgWrapStyleChanged", style);
	};


	asc_docs_api.prototype.asc_addOleObjectAction = function(sLocalUrl, sData, sApplicationId, fWidth, fHeight, nWidthPix, nHeightPix)
	{
		var _image = this.ImageLoader.LoadImage(AscCommon.getFullImageSrc2(sLocalUrl), 1);
		if (null != _image)//картинка уже должна быть загружена
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddOleObject);
				this.WordControl.m_oLogicDocument.Add_OleObject(fWidth, fHeight, nWidthPix, nHeightPix, sLocalUrl, sData, sApplicationId);
			}
		}
	};

	asc_docs_api.prototype.asc_editOleObjectAction = function(bResize, oOleObject, sImageUrl, sData, nPixWidth, nPixHeight)
	{
		if (oOleObject)
		{
			if (!bResize)
			{
				if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
				{
					this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_EditOleObject);
					this.WordControl.m_oLogicDocument.Edit_OleObject(oOleObject, sData, sImageUrl, nPixWidth, nPixHeight);
					this.WordControl.m_oLogicDocument.Recalculate();
                    this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
				}
			}
			else
			{
				this.WordControl.m_oLogicDocument.Edit_OleObject(oOleObject, sData, sImageUrl, nPixWidth, nPixHeight);
				this.WordControl.m_oLogicDocument.Recalculate();
                this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
			}
		}
	};
	//-----------------------------------------------------------------
	// События контекстного меню
	//-----------------------------------------------------------------

	function CContextMenuData(obj)
	{
		if (obj)
		{
			this.Type  = ( undefined != obj.Type ) ? obj.Type : Asc.c_oAscContextMenuTypes.Common;
			this.X_abs = ( undefined != obj.X_abs ) ? obj.X_abs : 0;
			this.Y_abs = ( undefined != obj.Y_abs ) ? obj.Y_abs : 0;

			switch (this.Type)
			{
				case Asc.c_oAscContextMenuTypes.ChangeHdrFtr :
				{
					this.PageNum = ( undefined != obj.PageNum ) ? obj.PageNum : 0;
					this.Header  = ( undefined != obj.Header  ) ? obj.Header : true;

					break;
				}
			}
		}
		else
		{
			this.Type  = Asc.c_oAscContextMenuTypes.Common;
			this.X_abs = 0;
			this.Y_abs = 0;
		}
	}

	CContextMenuData.prototype.get_Type    = function()
	{
		return this.Type;
	};
	CContextMenuData.prototype.get_X       = function()
	{
		return this.X_abs;
	};
	CContextMenuData.prototype.get_Y       = function()
	{
		return this.Y_abs;
	};
	CContextMenuData.prototype.get_PageNum = function()
	{
		return this.PageNum;
	};
	CContextMenuData.prototype.is_Header   = function()
	{
		return this.Header;
	};

	asc_docs_api.prototype.sync_ContextMenuCallback = function(Data)
	{
		this.asc_fireCallback("asc_onContextMenu", new CContextMenuData(Data));
	};


	asc_docs_api.prototype.sync_MouseMoveStartCallback = function()
	{
		this.asc_fireCallback("asc_onMouseMoveStart");
	};

	asc_docs_api.prototype.sync_MouseMoveEndCallback = function()
	{
		this.asc_fireCallback("asc_onMouseMoveEnd");
	};

	asc_docs_api.prototype.sync_MouseMoveCallback = function(Data)
	{
		this.asc_fireCallback("asc_onMouseMove", Data);
	};

	asc_docs_api.prototype.sync_ShowForeignCursorLabel = function(UserId, X, Y, Color)
	{
		this.asc_fireCallback("asc_onShowForeignCursorLabel", UserId, X, Y, new AscCommon.CColor(Color.r, Color.g, Color.b, 255));
	};
	asc_docs_api.prototype.sync_HideForeignCursorLabel = function(UserId)
	{
		this.asc_fireCallback("asc_onHideForeignCursorLabel", UserId);
	};

	//-----------------------------------------------------------------
	// Функции для работы с гиперссылками
	//-----------------------------------------------------------------
	asc_docs_api.prototype.can_AddHyperlink = function()
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//    return false;

		var bCanAdd = this.WordControl.m_oLogicDocument.Hyperlink_CanAdd(true);
		if (true === bCanAdd)
			return this.WordControl.m_oLogicDocument.Get_SelectedText(true);

		return false;
	};

	// HyperProps - объект CHyperlinkProperty
	asc_docs_api.prototype.add_Hyperlink = function(HyperProps)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddHyperlink);
			this.WordControl.m_oLogicDocument.Hyperlink_Add(HyperProps);
		}
	};

	// HyperProps - объект CHyperlinkProperty
	asc_docs_api.prototype.change_Hyperlink = function(HyperProps)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ChangeHyperlink);
			this.WordControl.m_oLogicDocument.Hyperlink_Modify(HyperProps);
		}
	};

	asc_docs_api.prototype.remove_Hyperlink = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveHyperlink);
			this.WordControl.m_oLogicDocument.Hyperlink_Remove();
		}
	};

	function CHyperlinkProperty(obj)
	{
		if (obj)
		{
			this.Text    = (undefined != obj.Text   ) ? obj.Text : null;
			this.Value   = (undefined != obj.Value  ) ? obj.Value : "";
			this.ToolTip = (undefined != obj.ToolTip) ? obj.ToolTip : "";
		}
		else
		{
			this.Text    = null;
			this.Value   = "";
			this.ToolTip = "";
		}
	}

	CHyperlinkProperty.prototype.get_Value   = function()
	{
		return this.Value;
	};
	CHyperlinkProperty.prototype.put_Value   = function(v)
	{
		this.Value = v;
	};
	CHyperlinkProperty.prototype.get_ToolTip = function()
	{
		return this.ToolTip;
	};
	CHyperlinkProperty.prototype.put_ToolTip = function(v)
	{
		this.ToolTip = v ? v.slice(0, Asc.c_oAscMaxTooltipLength) : v;
	};
	CHyperlinkProperty.prototype.get_Text    = function()
	{
		return this.Text;
	};
	CHyperlinkProperty.prototype.put_Text    = function(v)
	{
		this.Text = v;
	};

	asc_docs_api.prototype.sync_HyperlinkPropCallback = function(hyperProp)
	{
		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.Hyperlink, new CHyperlinkProperty(hyperProp));
	};

	asc_docs_api.prototype.sync_HyperlinkClickCallback = function(Url)
	{
		this.asc_fireCallback("asc_onHyperlinkClick", Url);
	};

	asc_docs_api.prototype.sync_CanAddHyperlinkCallback = function(bCanAdd)
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//    this.asc_fireCallback("asc_onCanAddHyperlink", false);
		//else
		this.asc_fireCallback("asc_onCanAddHyperlink", bCanAdd);
	};

	asc_docs_api.prototype.sync_DialogAddHyperlink = function()
	{
		this.asc_fireCallback("asc_onDialogAddHyperlink");
	};

	asc_docs_api.prototype.sync_DialogAddHyperlink = function()
	{
		this.asc_fireCallback("asc_onDialogAddHyperlink");
	};

	//-----------------------------------------------------------------
	// Функции для работы с орфографией
	//-----------------------------------------------------------------
	function asc_CSpellCheckProperty(Word, Checked, Variants, ParaId, ElemId)
	{
		this.Word     = Word;
		this.Checked  = Checked;
		this.Variants = Variants;

		this.ParaId = ParaId;
		this.ElemId = ElemId;
	}

	asc_CSpellCheckProperty.prototype.get_Word     = function()
	{
		return this.Word;
	};
	asc_CSpellCheckProperty.prototype.get_Checked  = function()
	{
		return this.Checked;
	};
	asc_CSpellCheckProperty.prototype.get_Variants = function()
	{
		return this.Variants;
	};

	asc_docs_api.prototype.sync_SpellCheckCallback = function(Word, Checked, Variants, ParaId, ElemId)
	{
		this.SelectedObjectsStack[this.SelectedObjectsStack.length] = new asc_CSelectedObject(c_oAscTypeSelectElement.SpellCheck, new asc_CSpellCheckProperty(Word, Checked, Variants, ParaId, ElemId));
	};

	asc_docs_api.prototype.sync_SpellCheckVariantsFound = function()
	{
		this.asc_fireCallback("asc_onSpellCheckVariantsFound");
	};

	asc_docs_api.prototype.asc_replaceMisspelledWord = function(Word, SpellCheckProperty)
	{
		var ParaId = SpellCheckProperty.ParaId;
		var ElemId = SpellCheckProperty.ElemId;

		var Paragraph = g_oTableId.Get_ById(ParaId);
		if (null != Paragraph && false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_None, {
				Type      : AscCommon.changestype_2_Element_and_Type,
				Element   : Paragraph,
				CheckType : changestype_Paragraph_Content
			}))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ReplaceMisspelledWord);
			Paragraph.Replace_MisspelledWord(Word, ElemId);
			this.WordControl.m_oLogicDocument.Recalculate();
			Paragraph.Document_SetThisElementCurrent(true);
		}
	};

	asc_docs_api.prototype.asc_ignoreMisspelledWord = function(SpellCheckProperty, bAll)
	{
		if (false === bAll)
		{
			var ParaId = SpellCheckProperty.ParaId;
			var ElemId = SpellCheckProperty.ElemId;

			var Paragraph = g_oTableId.Get_ById(ParaId);
			if (null != Paragraph)
			{
				Paragraph.Ignore_MisspelledWord(ElemId);
			}
		}
		else
		{
			var LogicDocument = editor.WordControl.m_oLogicDocument;
			LogicDocument.Spelling.Add_Word(SpellCheckProperty.Word);
			LogicDocument.DrawingDocument.ClearCachePages();
			LogicDocument.DrawingDocument.FirePaint();
		}
	};

	asc_docs_api.prototype.asc_setDefaultLanguage = function(Lang)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Document_SectPr))
		{
			History.Create_NewPoint(AscDFH.historydescription_Document_SetDefaultLanguage);
			editor.WordControl.m_oLogicDocument.Set_DefaultLanguage(Lang);
		}
	};

	asc_docs_api.prototype.asc_getDefaultLanguage = function()
	{
		return editor.WordControl.m_oLogicDocument.Get_DefaultLanguage();
	};

	asc_docs_api.prototype.asc_getKeyboardLanguage = function()
	{
		if (undefined !== window["asc_current_keyboard_layout"])
			return window["asc_current_keyboard_layout"];
		return -1;
	};

	asc_docs_api.prototype.asc_setSpellCheck = function(isOn)
	{
		if (editor.WordControl.m_oLogicDocument)
		{
			editor.WordControl.m_oLogicDocument.Spelling.Use = isOn;
			editor.WordControl.m_oDrawingDocument.ClearCachePages();
			editor.WordControl.m_oDrawingDocument.FirePaint();
		}
	};
	//-----------------------------------------------------------------
	// Функции для работы с комментариями
	//-----------------------------------------------------------------
	function asc_CCommentDataWord(obj)
	{
		if (obj)
		{
			this.m_sText      = (undefined != obj.m_sText     ) ? obj.m_sText : "";
			this.m_sTime      = (undefined != obj.m_sTime     ) ? obj.m_sTime : "";
			this.m_sUserId    = (undefined != obj.m_sUserId   ) ? obj.m_sUserId : "";
			this.m_sQuoteText = (undefined != obj.m_sQuoteText) ? obj.m_sQuoteText : null;
			this.m_bSolved    = (undefined != obj.m_bSolved   ) ? obj.m_bSolved : false;
			this.m_sUserName  = (undefined != obj.m_sUserName ) ? obj.m_sUserName : "";
			this.m_aReplies   = [];
			if (undefined != obj.m_aReplies)
			{
				var Count = obj.m_aReplies.length;
				for (var Index = 0; Index < Count; Index++)
				{
					var Reply = new asc_CCommentDataWord(obj.m_aReplies[Index]);
					this.m_aReplies.push(Reply);
				}
			}
		}
		else
		{
			this.m_sText      = "";
			this.m_sTime      = "";
			this.m_sUserId    = "";
			this.m_sQuoteText = null;
			this.m_bSolved    = false;
			this.m_sUserName  = "";
			this.m_aReplies   = [];
		}
	}

	asc_CCommentDataWord.prototype.asc_getText         = function()
	{
		return this.m_sText;
	};
	asc_CCommentDataWord.prototype.asc_putText         = function(v)
	{
		this.m_sText = v ? v.slice(0, Asc.c_oAscMaxCellOrCommentLength) : v;
	};
	asc_CCommentDataWord.prototype.asc_getTime         = function()
	{
		return this.m_sTime;
	};
	asc_CCommentDataWord.prototype.asc_putTime         = function(v)
	{
		this.m_sTime = v;
	};
	asc_CCommentDataWord.prototype.asc_getUserId       = function()
	{
		return this.m_sUserId;
	};
	asc_CCommentDataWord.prototype.asc_putUserId       = function(v)
	{
		this.m_sUserId = v;
	};
	asc_CCommentDataWord.prototype.asc_getUserName     = function()
	{
		return this.m_sUserName;
	};
	asc_CCommentDataWord.prototype.asc_putUserName     = function(v)
	{
		this.m_sUserName = v;
	};
	asc_CCommentDataWord.prototype.asc_getQuoteText    = function()
	{
		return this.m_sQuoteText;
	};
	asc_CCommentDataWord.prototype.asc_putQuoteText    = function(v)
	{
		this.m_sQuoteText = v;
	};
	asc_CCommentDataWord.prototype.asc_getSolved       = function()
	{
		return this.m_bSolved;
	};
	asc_CCommentDataWord.prototype.asc_putSolved       = function(v)
	{
		this.m_bSolved = v;
	};
	asc_CCommentDataWord.prototype.asc_getReply        = function(i)
	{
		return this.m_aReplies[i];
	};
	asc_CCommentDataWord.prototype.asc_addReply        = function(v)
	{
		this.m_aReplies.push(v);
	};
	asc_CCommentDataWord.prototype.asc_getRepliesCount = function(v)
	{
		return this.m_aReplies.length;
	};


	asc_docs_api.prototype.asc_showComments = function()
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		this.WordControl.m_oLogicDocument.Show_Comments();
	};

	asc_docs_api.prototype.asc_hideComments = function()
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		this.WordControl.m_oLogicDocument.Hide_Comments();
		editor.sync_HideComment();
	};

	asc_docs_api.prototype.asc_addComment = function(AscCommentData)
	{
	};

	asc_docs_api.prototype.asc_removeComment = function(Id)
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_None, {
				Type : AscCommon.changestype_2_Comment,
				Id   : Id
			}))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_RemoveComment);
			this.WordControl.m_oLogicDocument.Remove_Comment(Id, true, true);
		}
	};

	asc_docs_api.prototype.asc_changeComment = function(Id, AscCommentData)
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_None, {
				Type : AscCommon.changestype_2_Comment,
				Id   : Id
			}))
		{
			var CommentData = new AscCommon.CCommentData();
			CommentData.Read_FromAscCommentData(AscCommentData);

			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ChangeComment);
			this.WordControl.m_oLogicDocument.Change_Comment(Id, CommentData);

			this.sync_ChangeCommentData(Id, CommentData);
		}
	};

	asc_docs_api.prototype.asc_selectComment = function(Id)
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		this.WordControl.m_oLogicDocument.Select_Comment(Id, true);
	};

	asc_docs_api.prototype.asc_showComment = function(Id)
	{
		this.WordControl.m_oLogicDocument.Show_Comment(Id);
	};

	asc_docs_api.prototype.can_AddQuotedComment = function()
	{
		//if ( true === CollaborativeEditing.Get_GlobalLock() )
		//    return false;

		return this.WordControl.m_oLogicDocument.CanAdd_Comment();
	};

	asc_docs_api.prototype.sync_RemoveComment = function(Id)
	{
		this.asc_fireCallback("asc_onRemoveComment", Id);
	};

	asc_docs_api.prototype.sync_AddComment = function(Id, CommentData)
	{
		var AscCommentData = new asc_CCommentDataWord(CommentData);
		this.asc_fireCallback("asc_onAddComment", Id, AscCommentData);
	};

	asc_docs_api.prototype.sync_ShowComment = function(Id, X, Y)
	{
		// TODO: Переделать на нормальный массив
		this.asc_fireCallback("asc_onShowComment", [Id], X, Y);
	};

	asc_docs_api.prototype.sync_HideComment = function()
	{
		this.asc_fireCallback("asc_onHideComment");
	};

	asc_docs_api.prototype.sync_UpdateCommentPosition = function(Id, X, Y)
	{
		// TODO: Переделать на нормальный массив
		this.asc_fireCallback("asc_onUpdateCommentPosition", [Id], X, Y);
	};

	asc_docs_api.prototype.sync_ChangeCommentData = function(Id, CommentData)
	{
		var AscCommentData = new asc_CCommentDataWord(CommentData);
		this.asc_fireCallback("asc_onChangeCommentData", Id, AscCommentData);
	};

	asc_docs_api.prototype.sync_LockComment = function(Id, UserId)
	{
		this.asc_fireCallback("asc_onLockComment", Id, UserId);
	};

	asc_docs_api.prototype.sync_UnLockComment = function(Id)
	{
		this.asc_fireCallback("asc_onUnLockComment", Id);
	};

	asc_docs_api.prototype.asc_getComments        = function()
	{
		var ResComments   = [];
		var LogicDocument = this.WordControl.m_oLogicDocument;
		if (undefined != LogicDocument)
		{
			var DocComments = LogicDocument.Comments;
			for (var Id in DocComments.m_aComments)
			{
				var AscCommentData = new asc_CCommentDataWord(DocComments.m_aComments[Id].Data);
				ResComments.push({"Id" : Id, "Comment" : AscCommentData});
			}
		}

		return ResComments;
	};
	//-----------------------------------------------------------------
	asc_docs_api.prototype.sync_LockHeaderFooters = function()
	{
		this.asc_fireCallback("asc_onLockHeaderFooters");
	};

	asc_docs_api.prototype.sync_LockDocumentProps = function()
	{
		this.asc_fireCallback("asc_onLockDocumentProps");
	};

	asc_docs_api.prototype.sync_UnLockHeaderFooters = function()
	{
		this.asc_fireCallback("asc_onUnLockHeaderFooters");
	};

	asc_docs_api.prototype.sync_UnLockDocumentProps = function()
	{
		this.asc_fireCallback("asc_onUnLockDocumentProps");
	};

	asc_docs_api.prototype.sync_CollaborativeChanges = function()
	{
		if (true !== AscCommon.CollaborativeEditing.Is_Fast())
			this.asc_fireCallback("asc_onCollaborativeChanges");
	};

	asc_docs_api.prototype.sync_LockDocumentSchema = function()
	{
		this.asc_fireCallback("asc_onLockDocumentSchema");
	};

	asc_docs_api.prototype.sync_UnLockDocumentSchema = function()
	{
		this.asc_fireCallback("asc_onUnLockDocumentSchema");
	};


	/*----------------------------------------------------------------*/
	/*functions for working with zoom & navigation*/
	asc_docs_api.prototype.zoomIn         = function()
	{
		this.WordControl.zoom_In();
	};
	asc_docs_api.prototype.zoomOut        = function()
	{
		this.WordControl.zoom_Out();
	};
	asc_docs_api.prototype.zoomFitToPage  = function()
	{
		if (!this.isLoadFullApi)
		{
			this.tmpZoomType = AscCommon.c_oZoomType.FitToPage;
			return;
		}
		this.WordControl.zoom_FitToPage();
	};
	asc_docs_api.prototype.zoomFitToWidth = function()
	{
		if (!this.isLoadFullApi)
		{
			this.tmpZoomType = AscCommon.c_oZoomType.FitToWidth;
			return;
		}
		this.WordControl.zoom_FitToWidth();
	};
	asc_docs_api.prototype.zoomCustomMode = function()
	{
		if (!this.isLoadFullApi)
		{
			this.tmpZoomType = AscCommon.c_oZoomType.CustomMode;
			return;
		}
		this.WordControl.m_nZoomType = 0;
		this.WordControl.zoom_Fire(0, this.WordControl.m_nZoomValue);
	};
	asc_docs_api.prototype.zoom100        = function()
	{
		this.zoom(100);
	};
	asc_docs_api.prototype.zoom           = function(percent)
	{
		var _old_val                  = this.WordControl.m_nZoomValue;
		this.WordControl.m_nZoomValue = percent;
		this.WordControl.m_nZoomType  = 0;
		this.WordControl.zoom_Fire(0, _old_val);
	};
	asc_docs_api.prototype.goToPage       = function(number)
	{
		this.WordControl.GoToPage(number);
	};
	asc_docs_api.prototype.getCountPages  = function()
	{
		return this.WordControl.m_oDrawingDocument.m_lPagesCount;
	};
	asc_docs_api.prototype.getCurrentPage = function()
	{
		return this.WordControl.m_oDrawingDocument.m_lCurrentPage;
	};
	/*callbacks*/
	asc_docs_api.prototype.sync_zoomChangeCallback  = function(percent, type)
	{	//c_oAscZoomType.Current, c_oAscZoomType.FitWidth, c_oAscZoomType.FitPage
		this.asc_fireCallback("asc_onZoomChange", percent, type);
	};
	asc_docs_api.prototype.sync_countPagesCallback  = function(count)
	{
		this.asc_fireCallback("asc_onCountPages", count);
	};
	asc_docs_api.prototype.sync_currentPageCallback = function(number)
	{
		this.asc_fireCallback("asc_onCurrentPage", number);
	};

	/*----------------------------------------------------------------*/
	asc_docs_api.prototype.asc_enableKeyEvents = function(value)
	{
		if (!this.isLoadFullApi)
		{
			this.tmpFocus = value;
			return;
		}

		if (this.WordControl.IsFocus != value)
		{
			this.WordControl.IsFocus = value;

			if (this.WordControl.IsFocus && null != this.WordControl.TextBoxInput)
				this.WordControl.TextBoxInput.focus();

			this.asc_fireCallback("asc_onEnableKeyEventsChanged", value);
		}
	};
	asc_docs_api.prototype.asc_IsFocus         = function(bIsNaturalFocus)
	{
		var _ret = false;
		if (this.WordControl.IsFocus)
			_ret = true;
		if (_ret && bIsNaturalFocus && this.WordControl.TextBoxInputFocus)
			_ret = false;
		return _ret;
	};

	asc_docs_api.prototype.asyncServerIdEndLoaded = function()
	{
		this.ServerIdWaitComplete = true;
		if (true == this.ServerImagesWaitComplete)
			this.OpenDocumentEndCallback();
	};

	// работа с шрифтами
	asc_docs_api.prototype.asyncFontsDocumentStartLoaded = function()
	{
		// здесь прокинуть евент о заморозке меню
		// и нужно вывести информацию в статус бар
		if (this.isPasteFonts_Images)
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadFont);
		else if (this.isSaveFonts_Images)
			this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
		else
		{
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentFonts);

			// заполним прогресс
			var _progress         = this.OpenDocumentProgress;
			_progress.Type        = c_oAscAsyncAction.LoadDocumentFonts;
			_progress.FontsCount  = this.FontLoader.fonts_loading.length;
			_progress.CurrentFont = 0;

			var _loader_object = this.WordControl.m_oLogicDocument;
			var _count         = 0;
			if (_loader_object !== undefined && _loader_object != null)
			{
				for (var i in _loader_object.ImageMap)
				{
					if (this.DocInfo.get_OfflineApp())
					{
						var localUrl = _loader_object.ImageMap[i];
						g_oDocumentUrls.addImageUrl(localUrl, this.documentUrl + 'media/' + localUrl);
					}
					++_count;
				}
			}

			_progress.ImagesCount  = _count;
			_progress.CurrentImage = 0;
		}
	};
	asc_docs_api.prototype.GenerateStyles                = function()
	{
		if (window["NATIVE_EDITOR_ENJINE"] === true)
		{
			if (!this.asc_checkNeedCallback("asc_onInitEditorStyles"))
				return;
		}

		var StylesPainter = new AscCommonWord.CStylesPainter();
		var LogicDocument = this.WordControl.m_oLogicDocument;
		if (LogicDocument)
		{
			var isTrackRevision = LogicDocument.Is_TrackRevisions();
			var isShowParaMarks = LogicDocument.Is_ShowParagraphMarks();

			if (true === isTrackRevision)
				LogicDocument.Set_TrackRevisions(false);

			if (true === isShowParaMarks)
				LogicDocument.Set_ShowParagraphMarks(false, false);

			StylesPainter.GenerateStyles(this, (null == this.LoadedObject) ? this.WordControl.m_oLogicDocument.Get_Styles().Style : this.LoadedObjectDS);

			if (true === isTrackRevision)
				LogicDocument.Set_TrackRevisions(true);

			if (true === isShowParaMarks)
				LogicDocument.Set_ShowParagraphMarks(true, false);
		}
	};
	asc_docs_api.prototype.asyncFontsDocumentEndLoaded   = function()
	{
		// все, шрифты загружены. Теперь нужно подгрузить картинки
		if (this.isPasteFonts_Images)
			this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadFont);
		else if (this.isSaveFonts_Images)
			this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);
		else
			this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentFonts);

		this.EndActionLoadImages = 0;
		if (this.isPasteFonts_Images)
		{
			var _count = 0;
			for (var i in this.pasteImageMap)
				++_count;

			if (_count > 0)
			{
				this.EndActionLoadImages = 2;
				this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);
			}

			var _oldAsyncLoadImages                     = this.ImageLoader.bIsAsyncLoadDocumentImages;
			this.ImageLoader.bIsAsyncLoadDocumentImages = false;
			this.ImageLoader.LoadDocumentImages(this.pasteImageMap, false);
			this.ImageLoader.bIsAsyncLoadDocumentImages = true;
			return;
		}
		else if (this.isSaveFonts_Images)
		{
			var _count = 0;
			for (var i in this.saveImageMap)
				++_count;

			if (_count > 0)
			{
				this.EndActionLoadImages = 2;
				this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadImage);
			}

			this.ImageLoader.LoadDocumentImages(this.saveImageMap, false);
			return;
		}

		if (!this.FontLoader.embedded_cut_manager.bIsCutFontsUse)
			this.GenerateStyles();

		if (null != this.WordControl.m_oLogicDocument)
		{
			this.WordControl.m_oDrawingDocument.CheckGuiControlColors();
			this.WordControl.m_oDrawingDocument.SendThemeColorScheme();
			this.asc_fireCallback("asc_onUpdateChartStyles");
		}

		if (this.isLoadNoCutFonts)
		{
			this.isLoadNoCutFonts = false;
			this.asc_setViewMode(false);
			return;
		}

		// открытие после загрузки документа

		var _loader_object = this.WordControl.m_oLogicDocument;
		if (null == _loader_object)
			_loader_object = this.WordControl.m_oDrawingDocument.m_oDocumentRenderer;

		var _count = 0;
		for (var i in _loader_object.ImageMap)
			++_count;

		if (!this.isOnlyReaderMode)
		{
			// add const textures
			var _st_count = AscCommon.g_oUserTexturePresets.length;
			for (var i = 0; i < _st_count; i++)
				_loader_object.ImageMap[_count + i] = AscCommon.g_oUserTexturePresets[i];

			if (this.OpenDocumentProgress && !this.ImageLoader.bIsAsyncLoadDocumentImages)
			{
				this.OpenDocumentProgress.ImagesCount += _st_count;
			}
		}

		if (_count > 0)
		{
			this.EndActionLoadImages = 1;
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentImages);
		}

		this.ImageLoader.bIsLoadDocumentFirst = true;
		this.ImageLoader.LoadDocumentImages(_loader_object.ImageMap, true);
	};

	asc_docs_api.prototype.CreateFontsCharMap = function()
	{
		var _info = new CFontsCharMap();
		_info.StartWork();

		this.WordControl.m_oLogicDocument.Document_CreateFontCharMap(_info);

		return _info.EndWork();
	};

	asc_docs_api.prototype.sync_SendThemeColors       = function(colors, standart_colors)
	{
		this._gui_control_colors = {Colors : colors, StandartColors : standart_colors};
		this.asc_fireCallback("asc_onSendThemeColors", colors, standart_colors);
	};
	asc_docs_api.prototype.sync_SendThemeColorSchemes = function(param)
	{
		this._gui_color_schemes = param;
	};

	asc_docs_api.prototype.ChangeColorScheme            = function(index_scheme)
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		var _changer = this.WordControl.m_oLogicDocument.DrawingObjects;
		if (null == _changer)
			return;

		var theme = this.WordControl.m_oLogicDocument.theme;

		var oColorScheme    = AscCommon.g_oUserColorScheme;
		var _count_defaults = oColorScheme.length;

		if (this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_ColorScheme) === false)
		{
			History.Create_NewPoint(AscDFH.historydescription_Document_ChangeColorScheme);
			var data = {Type : AscDFH.historyitem_ChangeColorScheme, oldScheme : theme.themeElements.clrScheme};

			if (index_scheme < _count_defaults)
			{
				var _obj    = oColorScheme[index_scheme];
				var scheme  = new AscFormat.ClrScheme();
				scheme.name = _obj.name;
				var _c      = null;

				_c               = _obj.dk1;
				scheme.colors[8] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c                = _obj.lt1;
				scheme.colors[12] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.dk2;
				scheme.colors[9] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c                = _obj.lt2;
				scheme.colors[13] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent1;
				scheme.colors[0] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent2;
				scheme.colors[1] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent3;
				scheme.colors[2] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent4;
				scheme.colors[3] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent5;
				scheme.colors[4] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c               = _obj.accent6;
				scheme.colors[5] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c                = _obj.hlink;
				scheme.colors[11] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				_c                = _obj.folHlink;
				scheme.colors[10] = AscFormat.CreateUniColorRGB(_c.R, _c.G, _c.B);

				theme.themeElements.clrScheme = scheme;
				/*_changer.calculateAfterChangeTheme();

				 // TODO:
				 this.WordControl.m_oDrawingDocument.ClearCachePages();
				 this.WordControl.OnScroll();*/
			}
			else
			{
				index_scheme -= _count_defaults;

				if (index_scheme < 0 || index_scheme >= theme.extraClrSchemeLst.length)
					return;

				theme.themeElements.clrScheme = theme.extraClrSchemeLst[index_scheme].clrScheme.createDuplicate();
				/*_changer.calculateAfterChangeTheme();

				 // TODO:
				 this.WordControl.m_oDrawingDocument.ClearCachePages();
				 this.WordControl.OnScroll();*/
			}

			data.newScheme = theme.themeElements.clrScheme;
			History.Add(this.WordControl.m_oLogicDocument.DrawingObjects, data);
			this.WordControl.m_oDrawingDocument.CheckGuiControlColors();
			this.chartPreviewManager.clearPreviews();
			this.textArtPreviewManager.clear();
			this.asc_fireCallback("asc_onUpdateChartStyles");
			this.WordControl.m_oLogicDocument.Recalculate();


			// TODO:
			this.WordControl.m_oDrawingDocument.ClearCachePages();
			this.WordControl.OnScroll();

			this.WordControl.m_oDrawingDocument.CheckGuiControlColors();
			this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
		}

	};
	asc_docs_api.prototype.asyncImagesDocumentEndLoaded = function()
	{
		this.ImageLoader.bIsLoadDocumentFirst = false;
		var _bIsOldPaste                      = this.isPasteFonts_Images;

		if (null != this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
		{
			if (this.EndActionLoadImages == 1)
			{
				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentImages);
			}
			else if (this.EndActionLoadImages == 2)
			{
				if (this.isPasteFonts_Images)
					this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);
				else
					this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadImage);
			}
			this.EndActionLoadImages = 0;

			this.WordControl.m_oDrawingDocument.OpenDocument();

			this.LoadedObject = null;

			this.bInit_word_control = true;

			if (false === this.isPasteFonts_Images)
				this.asc_fireCallback("asc_onDocumentContentReady");

			this.WordControl.InitControl();

			if (this.isViewMode)
				this.asc_setViewMode(true);
			return;
		}

		// на методе OpenDocumentEndCallback может поменяться this.EndActionLoadImages
		if (this.EndActionLoadImages == 1)
		{
			this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadDocumentImages);
		}
		else if (this.EndActionLoadImages == 2)
		{
			if (_bIsOldPaste)
				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadImage);
			else
				this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadImage);
		}
		this.EndActionLoadImages = 0;

		// размораживаем меню... и начинаем считать документ
		if (false === this.isPasteFonts_Images && false === this.isSaveFonts_Images && false === this.isLoadImagesCustom)
		{
			this.ServerImagesWaitComplete = true;
			if (true == this.ServerIdWaitComplete)
				this.OpenDocumentEndCallback();
		}
		else
		{
			if (this.isPasteFonts_Images)
			{
				this.isPasteFonts_Images = false;
				this.pasteImageMap       = null;
				this.decrementCounterLongAction();
				this.pasteCallback();
				window.GlobalPasteFlag        = false;
				window.GlobalPasteFlagCounter = 0;
				this.pasteCallback            = null;
			}
			else if (this.isSaveFonts_Images)
			{
				this.isSaveFonts_Images = false;
				this.saveImageMap       = null;
				this.pre_SaveCallback();

				if (this.bInit_word_control === false)
				{
					this.bInit_word_control = true;
					this.asc_fireCallback("asc_onDocumentContentReady");
				}
			}
			else if (this.isLoadImagesCustom)
			{
				this.isLoadImagesCustom = false;
				this.loadCustomImageMap = null;

				if (!this.ImageLoader.bIsAsyncLoadDocumentImages)
					this.SyncLoadImages_callback();
			}
		}
	};

	asc_docs_api.prototype.OpenDocumentEndCallback = function()
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		if (0 == this.DocumentType)
			this.WordControl.m_oLogicDocument.LoadEmptyDocument();
		else if (1 == this.DocumentType)
		{
			this.WordControl.m_oLogicDocument.LoadTestDocument();
		}
		else
		{
			if (this.LoadedObject)
			{
				if (1 != this.LoadedObject)
				{
					this.WordControl.m_oLogicDocument.fromJfdoc(this.LoadedObject);
					this.WordControl.m_oDrawingDocument.TargetStart();
					this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
				}
				else
				{
					var Document = this.WordControl.m_oLogicDocument;

					if (this.isApplyChangesOnOpenEnabled)
					{
						this.isApplyChangesOnOpenEnabled = false;
						AscCommon.CollaborativeEditing.Apply_Changes();
						AscCommon.CollaborativeEditing.Release_Locks();

						this.isApplyChangesOnOpen = true;

						// Применяем все lock-и (ToDo возможно стоит пересмотреть вообще Lock-и)
						for (var i = 0; i < this.arrPreOpenLocksObjects.length; ++i)
						{
							this.arrPreOpenLocksObjects[i]();
						}
						this.arrPreOpenLocksObjects = [];
					}

					//                History.RecalcData_Add( { Type : AscDFH.historyitem_recalctype_Inline, Data : { Pos : 0, PageNum : 0 } } );

					//Recalculate для Document
					Document.CurPos.ContentPos = 0;
					//                History.RecalcData_Add({Type: AscDFH.historyitem_recalctype_Drawing, All: true});

					var RecalculateData =
						{
							Inline   : {Pos : 0, PageNum : 0},
							Flow     : [],
							HdrFtr   : [],
							Drawings : {
								All : true,
								Map : {}
							}
						};

					if (!this.isOnlyReaderMode)
					{
						if (false === this.isSaveFonts_Images)
							Document.Recalculate(false, false, RecalculateData);

						this.WordControl.m_oDrawingDocument.TargetStart();
					}
					else
					{
						Document.Recalculate_AllTables();
						var data = {All : true};
						Document.DrawingObjects.recalculate_(data);
						Document.DrawingObjects.recalculateText_(data);

						if (!this.WordControl.IsReaderMode())
							this.ChangeReaderMode();
						else
							this.WordControl.UpdateReaderContent();
					}
				}
			}
		}

		if (false === this.isSaveFonts_Images)
		{
			this.bInit_word_control = true;
			this.asc_fireCallback("asc_onDocumentContentReady");
		}

		this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
		//this.WordControl.m_oLogicDocument.Document_UpdateRulersState();
		this.WordControl.m_oLogicDocument.Document_UpdateSelectionState();
		this.LoadedObject = null;

		this.WordControl.InitControl();

		if (!this.isViewMode)
		{
			this.sendStandartTextures();
			this.WordControl.m_oDrawingDocument.SendMathToMenu();

			if (this.shapeElementId)
			{
				this.WordControl.m_oDrawingDocument.InitGuiCanvasShape(this.shapeElementId);
			}
		}

		if (this.isViewMode)
			this.asc_setViewMode(true);

		// Меняем тип состояния (на никакое)
		this.advancedOptionsAction = c_oAscAdvancedOptionsAction.None;
	};

	asc_docs_api.prototype.UpdateInterfaceState = function()
	{
		if (this.WordControl.m_oLogicDocument != null)
		{
			this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
		}
	};

	asc_docs_api.prototype.asyncFontEndLoaded = function(fontinfo)
	{
		this.sync_EndAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadFont);

		var _fontSelections = g_fontApplication.g_fontSelections;
		if (_fontSelections.CurrentLoadedObj != null)
		{
			var _rfonts = _fontSelections.getSetupRFonts(_fontSelections.CurrentLoadedObj);
			this.WordControl.m_oLogicDocument.TextBox_Put(_fontSelections.CurrentLoadedObj.text, _rfonts);
			this.WordControl.ReinitTB();

			_fontSelections.CurrentLoadedObj = null;
			this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.LoadFont);
			return;
		}

		if (this.FontAsyncLoadType == 1)
		{
			this.FontAsyncLoadType = 0;
			this.asc_AddMath2(this.FontAsyncLoadParam);
			this.FontAsyncLoadParam = null;
			return;
		}

		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_SetTextFontNameLong);
			this.WordControl.m_oLogicDocument.Paragraph_Add(new AscCommonWord.ParaTextPr({
				FontFamily : {
					Name  : fontinfo.Name,
					Index : -1
				}
			}));
			this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();
		}
		// отжать заморозку меню
	};

	asc_docs_api.prototype.asc_replaceLoadImageCallback = function(fCallback)
	{
		this.asyncImageEndLoaded2 = fCallback;
	};

	asc_docs_api.prototype.asyncImageEndLoaded = function(_image)
	{
		// отжать заморозку меню
		if (this.asyncImageEndLoaded2)
			this.asyncImageEndLoaded2(_image);
		else
		{
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddImage);
				this.WordControl.m_oLogicDocument.Add_InlineImage(50, 50, _image.src);
			}
		}
	};

	asc_docs_api.prototype.openDocument = function(sData)
	{
		if (sData.changes && this.VersionHistory)
		{
			this.VersionHistory.changes = sData.changes;
			this.VersionHistory.applyChanges(this);
		}

		if (sData.bSerFormat)
			this.OpenDocument2(sData.url, sData.data);
		else
			this.OpenDocument(sData.url, sData.data);
	};

	asc_docs_api.prototype.asyncImageEndLoadedBackground = function(_image)
	{
		this.WordControl.m_oDrawingDocument.CheckRasterImageOnScreen(_image.src);
	};
	asc_docs_api.prototype.IsAsyncOpenDocumentImages     = function()
	{
		return true;
	};

	asc_docs_api.prototype.pre_Paste = function(_fonts, _images, callback)
	{
		if (undefined !== window["Native"] && undefined !== window["Native"]["GetImageUrl"])
		{
			callback();
			window.GlobalPasteFlag        = false;
			window.GlobalPasteFlagCounter = 0;
			return;
		}

		this.pasteCallback = callback;
		this.pasteImageMap = _images;

		var _count = 0;
		for (var i in this.pasteImageMap)
			++_count;
		if (0 == _count && false === this.FontLoader.CheckFontsNeedLoading(_fonts))
		{
			// никаких евентов. ничего грузить не нужно. сделано для сафари под макОс.
			// там при LongActions теряется фокус и вставляются пробелы
			this.decrementCounterLongAction();
			this.pasteCallback();
			window.GlobalPasteFlag        = false;
			window.GlobalPasteFlagCounter = 0;
			this.pasteCallback            = null;

			if (-1 != window.PasteEndTimerId)
			{
				clearTimeout(window.PasteEndTimerId);
				window.PasteEndTimerId = -1;

				document.body.style.MozUserSelect          = "none";
				document.body.style["-khtml-user-select"]  = "none";
				document.body.style["-o-user-select"]      = "none";
				document.body.style["user-select"]         = "none";
				document.body.style["-webkit-user-select"] = "none";

				var pastebin = AscCommon.Editor_Paste_GetElem(this, true);

				if (!AscCommon.AscBrowser.isSafariMacOs)
					pastebin.onpaste = null;

				pastebin.style.display = PasteElementsId.ELEMENT_DISPAY_STYLE;
			}

			return;
		}

		this.isPasteFonts_Images = true;
		this.FontLoader.LoadDocumentFonts2(_fonts);
	};

	asc_docs_api.prototype.pre_Save = function(_images)
	{
		this.isSaveFonts_Images = true;
		this.saveImageMap       = _images;
		this.WordControl.m_oDrawingDocument.CheckFontNeeds();
		this.FontLoader.LoadDocumentFonts2(this.WordControl.m_oLogicDocument.Fonts);
	};

	asc_docs_api.prototype.SyncLoadImages          = function(_images)
	{
		this.isLoadImagesCustom = true;
		this.loadCustomImageMap = _images;

		var _count  = 0;
		var _loaded = this.ImageLoader.map_image_index;

		var _new_len = this.loadCustomImageMap.length;
		for (var i = 0; i < _new_len; i++)
		{
			if (undefined !== _loaded[this.loadCustomImageMap[i]])
			{
				this.loadCustomImageMap.splice(i, 1);
				i--;
				_new_len--;
				continue;
			}
			++_count;
		}

		if (_count > 0)
		{
			this.EndActionLoadImages = 2;
			this.sync_StartAction(c_oAscAsyncActionType.Information, c_oAscAsyncAction.LoadImage);
		}

		this.ImageLoader.LoadDocumentImages(this.loadCustomImageMap, false);
	};
	asc_docs_api.prototype.SyncLoadImages_callback = function()
	{
		this.WordControl.OnRePaintAttack();
	};

	asc_docs_api.prototype.pre_SaveCallback = function()
	{
		AscCommon.CollaborativeEditing.OnEnd_Load_Objects();

		if (this.isApplyChangesOnOpen)
		{
			this.isApplyChangesOnOpen = false;
			this.OpenDocumentEndCallback();
		}
	};

	asc_docs_api.prototype.initEvents2MobileAdvances = function()
	{
		//this.WordControl.initEvents2MobileAdvances();
	};
	asc_docs_api.prototype.ViewScrollToX             = function(x)
	{
		this.WordControl.m_oScrollHorApi.scrollToX(x);
	};
	asc_docs_api.prototype.ViewScrollToY             = function(y)
	{
		this.WordControl.m_oScrollVerApi.scrollToY(y);
	};
	asc_docs_api.prototype.GetDocWidthPx             = function()
	{
		return this.WordControl.m_dDocumentWidth;
	};
	asc_docs_api.prototype.GetDocHeightPx            = function()
	{
		return this.WordControl.m_dDocumentHeight;
	};
	asc_docs_api.prototype.ClearSearch               = function()
	{
		return this.WordControl.m_oDrawingDocument.EndSearch(true);
	};
	asc_docs_api.prototype.GetCurrentVisiblePage     = function()
	{
		var lPage1 = this.WordControl.m_oDrawingDocument.m_lDrawingFirst;
		var lPage2 = lPage1 + 1;

		if (lPage2 > this.WordControl.m_oDrawingDocument.m_lDrawingEnd)
			return lPage1;

		var lWindHeight = this.WordControl.m_oEditor.HtmlElement.height;
		var arPages     = this.WordControl.m_oDrawingDocument.m_arrPages;

		var dist1 = arPages[lPage1].drawingPage.bottom;
		var dist2 = lWindHeight - arPages[lPage2].drawingPage.top;

		if (dist1 > dist2)
			return lPage1;

		return lPage2;
	};

	asc_docs_api.prototype.asc_SetDocumentPlaceChangedEnabled = function(bEnabled)
	{
		if (this.WordControl)
			this.WordControl.m_bDocumentPlaceChangedEnabled = bEnabled;
	};

	asc_docs_api.prototype.asc_SetViewRulers       = function(bRulers)
	{
		//if (false === this.bInit_word_control || true === this.isViewMode)
		//    return;

		if (!this.isLoadFullApi)
		{
			this.tmpViewRulers = bRulers;
			return;
		}

		if (this.WordControl.m_bIsRuler != bRulers)
		{
			this.WordControl.m_bIsRuler = bRulers;
			this.WordControl.checkNeedRules();
			this.WordControl.OnResize(true);
		}
	};
	asc_docs_api.prototype.asc_SetViewRulersChange = function()
	{
		//if (false === this.bInit_word_control || true === this.isViewMode)
		//    return;

		this.WordControl.m_bIsRuler = !this.WordControl.m_bIsRuler;
		this.WordControl.checkNeedRules();
		this.WordControl.OnResize(true);
		return this.WordControl.m_bIsRuler;
	};
	asc_docs_api.prototype.asc_GetViewRulers       = function()
	{
		return this.WordControl.m_bIsRuler;
	};

	asc_docs_api.prototype.asc_SetDocumentUnits = function(_units)
	{
		if (this.WordControl && this.WordControl.m_oHorRuler && this.WordControl.m_oVerRuler)
		{
			this.WordControl.m_oHorRuler.Units = _units;
			this.WordControl.m_oVerRuler.Units = _units;
			this.WordControl.UpdateHorRulerBack(true);
			this.WordControl.UpdateVerRulerBack(true);
		}
	};

	asc_docs_api.prototype.SetMobileVersion = function(val)
	{
		this.isMobileVersion = val;
		if (this.isMobileVersion)
		{
			this.WordControl.bIsRetinaSupport         = false; // ipad имеет проблемы с большими картинками
			this.WordControl.bIsRetinaNoSupportAttack = true;
			this.WordControl.m_bIsRuler               = false;
			this.ShowParaMarks                        = false;

			this.SetFontRenderingMode(1);
		}
	};

	asc_docs_api.prototype.GoToHeader = function(pageNumber)
	{
		if (this.WordControl.m_oDrawingDocument.IsFreezePage(pageNumber))
			return;

		var bForceRedraw  = false;
		var LogicDocument = this.WordControl.m_oLogicDocument;
		if (AscCommonWord.docpostype_HdrFtr !== LogicDocument.CurPos.Type)
		{
			LogicDocument.CurPos.Type = AscCommonWord.docpostype_HdrFtr;
			bForceRedraw              = true;
		}

		var oldClickCount            = global_mouseEvent.ClickCount;
		global_mouseEvent.Button     = 0;
		global_mouseEvent.ClickCount = 1;

		LogicDocument.OnMouseDown(global_mouseEvent, 0, 0, pageNumber);
		LogicDocument.OnMouseUp(global_mouseEvent, 0, 0, pageNumber);
		LogicDocument.OnMouseMove(global_mouseEvent, 0, 0, pageNumber);
		LogicDocument.Cursor_MoveLeft();
		LogicDocument.Document_UpdateInterfaceState();

		global_mouseEvent.ClickCount = oldClickCount;

		if (true === bForceRedraw)
		{
			this.WordControl.m_oDrawingDocument.ClearCachePages();
			this.WordControl.m_oDrawingDocument.FirePaint();
		}
	};

	asc_docs_api.prototype.GoToFooter = function(pageNumber)
	{
		if (this.WordControl.m_oDrawingDocument.IsFreezePage(pageNumber))
			return;

		var bForceRedraw  = false;
		var LogicDocument = this.WordControl.m_oLogicDocument;
		if (AscCommonWord.docpostype_HdrFtr !== LogicDocument.CurPos.Type)
		{
			LogicDocument.CurPos.Type = AscCommonWord.docpostype_HdrFtr;
			bForceRedraw              = true;
		}

		var oldClickCount            = global_mouseEvent.ClickCount;
		global_mouseEvent.Button     = 0;
		global_mouseEvent.ClickCount = 1;

		LogicDocument.OnMouseDown(global_mouseEvent, 0, AscCommon.Page_Height, pageNumber);
		LogicDocument.OnMouseUp(global_mouseEvent, 0, AscCommon.Page_Height, pageNumber);
		LogicDocument.OnMouseMove(global_mouseEvent, 0, 0, pageNumber);
		LogicDocument.Cursor_MoveLeft();
		LogicDocument.Document_UpdateInterfaceState();

		global_mouseEvent.ClickCount = oldClickCount;

		if (true === bForceRedraw)
		{
			this.WordControl.m_oDrawingDocument.ClearCachePages();
			this.WordControl.m_oDrawingDocument.FirePaint();
		}
	};

	asc_docs_api.prototype.ExitHeader_Footer = function(pageNumber)
	{
		if (this.WordControl.m_oDrawingDocument.IsFreezePage(pageNumber))
			return;

		var oldClickCount            = global_mouseEvent.ClickCount;
		global_mouseEvent.ClickCount = 2;
		this.WordControl.m_oLogicDocument.OnMouseDown(global_mouseEvent, 0, AscCommon.Page_Height / 2, pageNumber);
		this.WordControl.m_oLogicDocument.OnMouseUp(global_mouseEvent, 0, AscCommon.Page_Height / 2, pageNumber);

		this.WordControl.m_oLogicDocument.Document_UpdateInterfaceState();

		global_mouseEvent.ClickCount = oldClickCount;
	};

	asc_docs_api.prototype.GetCurrentPixOffsetY = function()
	{
		return this.WordControl.m_dScrollY;
	};

	asc_docs_api.prototype.SetPaintFormat = function(_value)
	{
		var value = ( true === _value ? c_oAscFormatPainterState.kOn : ( false === _value ? c_oAscFormatPainterState.kOff : _value ) );

		this.isPaintFormat = value;

		if (c_oAscFormatPainterState.kOff !== value)
			this.WordControl.m_oLogicDocument.Document_Format_Copy();
	};

	asc_docs_api.prototype.ChangeShapeType = function(value)
	{
		this.ImgApply(new asc_CImgProperty({ShapeProperties : {type : value}}));
	};

	asc_docs_api.prototype.sync_PaintFormatCallback = function(_value)
	{
		var value = ( true === _value ? c_oAscFormatPainterState.kOn : ( false === _value ? c_oAscFormatPainterState.kOff : _value ) );

		this.isPaintFormat = value;
		return this.asc_fireCallback("asc_onPaintFormatChanged", value);
	};
	asc_docs_api.prototype.SetMarkerFormat          = function(value, is_flag, r, g, b)
	{
		this.isMarkerFormat = value;

		if (this.isMarkerFormat)
		{
			this.WordControl.m_oLogicDocument.Paragraph_SetHighlight(is_flag, r, g, b);
			this.WordControl.m_oLogicDocument.Document_Format_Copy();
		}
	};

	asc_docs_api.prototype.sync_MarkerFormatCallback = function(value)
	{
		this.isMarkerFormat = value;
		return this.asc_fireCallback("asc_onMarkerFormatChanged", value);
	};

	asc_docs_api.prototype.StartAddShape = function(sPreset, is_apply)
	{
		this.isStartAddShape = true;
		this.addShapePreset  = sPreset;
		if (is_apply)
		{
			this.WordControl.m_oDrawingDocument.LockCursorType("crosshair");
		}
		else
		{
			editor.sync_EndAddShape();
			editor.sync_StartAddShapeCallback(false);
		}
	};

	asc_docs_api.prototype.AddTextArt = function(nStyle)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			History.Create_NewPoint(AscDFH.historydescription_Document_AddTextArt);
			this.WordControl.m_oLogicDocument.Add_TextArt(nStyle);
		}
	};


	asc_docs_api.prototype.sync_StartAddShapeCallback = function(value)
	{
		this.isStartAddShape = value;
		return this.asc_fireCallback("asc_onStartAddShapeChanged", value);
	};

	asc_docs_api.prototype.CanGroup = function()
	{
		return this.WordControl.m_oLogicDocument.CanGroup();
	};

	asc_docs_api.prototype.CanUnGroup = function()
	{
		return this.WordControl.m_oLogicDocument.CanUnGroup();
	};

	asc_docs_api.prototype.CanChangeWrapPolygon = function()
	{
		return this.WordControl.m_oLogicDocument.CanChangeWrapPolygon();
	};

	asc_docs_api.prototype.StartChangeWrapPolygon = function()
	{
		return this.WordControl.m_oLogicDocument.StartChangeWrapPolygon();
	};


	asc_docs_api.prototype.ClearFormating = function()
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_ClearFormatting);
			this.WordControl.m_oLogicDocument.Paragraph_ClearFormatting();
		}
	};

	asc_docs_api.prototype.GetSectionInfo = function()
	{
		var obj = new CAscSection();

		// TODO: Переделать данную функцию, если она вообще нужна
		obj.PageWidth  = 297;
		obj.PageHeight = 210;

		obj.MarginLeft   = 30;
		obj.MarginRight  = 15;
		obj.MarginTop    = 20;
		obj.MarginBottom = 20;

		return obj;
	};

	asc_docs_api.prototype.add_SectionBreak = function(_Type)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddSectionBreak);
			this.WordControl.m_oLogicDocument.Add_SectionBreak(_Type);
		}
	};

	asc_docs_api.prototype.getViewMode     = function()
	{
		return this.isViewMode;
	};
	asc_docs_api.prototype.asc_setViewMode = function(isViewMode)
	{
		if (!this.isLoadFullApi)
		{
			this.isViewMode = isViewMode;
			return;
		}

		if (isViewMode)
		{
			this.asc_SpellCheckDisconnect();

			this.isViewMode                              = true;
			this.ShowParaMarks                           = false;
			AscCommon.CollaborativeEditing.m_bGlobalLock = true;
			//this.isShowTableEmptyLine = false;
			//this.WordControl.m_bIsRuler = true;

			if (null == this.WordControl.m_oDrawingDocument.m_oDocumentRenderer)
			{
				this.WordControl.m_oDrawingDocument.ClearCachePages();
				this.WordControl.HideRulers();
			}
			else
			{
				this.WordControl.HideRulers();
				this.WordControl.OnScroll();
			}
		}
		else
		{
			if (this.bInit_word_control === true && this.FontLoader.embedded_cut_manager.bIsCutFontsUse)
			{
				this.isLoadNoCutFonts                               = true;
				this.FontLoader.embedded_cut_manager.bIsCutFontsUse = false;
				this.FontLoader.LoadDocumentFonts(this.WordControl.m_oLogicDocument.Fonts, true);
				return;
			}

			// быстрого перехода больше нет
			/*
			 if ( this.bInit_word_control === true )
			 {
			 CollaborativeEditing.Apply_Changes();
			 CollaborativeEditing.Release_Locks();
			 }
			 */

			this.isUseEmbeddedCutFonts = false;

			this.isViewMode = false;
			//this.WordControl.m_bIsRuler = true;
			this.WordControl.checkNeedRules();
			this.WordControl.m_oDrawingDocument.ClearCachePages();
			this.WordControl.OnResize(true);
		}
	};

	asc_docs_api.prototype.SetUseEmbeddedCutFonts = function(bUse)
	{
		this.isUseEmbeddedCutFonts = bUse;
	};

	asc_docs_api.prototype.OnMouseUp = function(x, y)
	{
		this.WordControl.onMouseUpExternal(x, y);
	};

	asc_docs_api.prototype.asyncImageEndLoaded2       = null;
	asc_docs_api.prototype._OfflineAppDocumentEndLoad = function()
	{
		var bIsViewer = false;
		var sData     = window["editor_bin"];
		if (undefined == sData)
			return;
		if (AscCommon.c_oSerFormat.Signature !== sData.substring(0, AscCommon.c_oSerFormat.Signature.length))
		{
			bIsViewer = true;
		}

		if (bIsViewer)
		{
			this.OpenDocument(this.documentUrl, sData);
		}
		else
		{
			this.OpenDocument2(this.documentUrl, sData);
		}
	};

	asc_docs_api.prototype.SetDrawImagePlaceParagraph = function(element_id, props)
	{
		this.WordControl.m_oDrawingDocument.InitGuiCanvasTextProps(element_id);
		this.WordControl.m_oDrawingDocument.DrawGuiCanvasTextProps(props);
	};

	asc_docs_api.prototype.asc_getMasterCommentId = function()
	{
		return -1;
	};

	asc_docs_api.prototype.asc_getAnchorPosition = function()
	{
		var AnchorPos = this.WordControl.m_oLogicDocument.Get_SelectionAnchorPos();
		return new AscCommon.asc_CRect(AnchorPos.X0, AnchorPos.Y, AnchorPos.X1 - AnchorPos.X0, 0);
	};

	asc_docs_api.prototype.spellCheck = function(rdata)
	{
		//console.log("start - " + rdata);
		// ToDo проверка на подключение
		switch (rdata.type)
		{
			case "spell":
			case "suggest":
				this.SpellCheckApi.spellCheck(JSON.stringify(rdata));
				break;
		}
	};

	window["asc_nativeOnSpellCheck"] = function(response)
	{
		if (editor.SpellCheckApi)
			editor.SpellCheckApi.onSpellCheck(response);
	};

	asc_docs_api.prototype._onNeedParams  = function(data)
	{
		var cp = {'codepage' : AscCommon.c_oAscCodePageUtf8, 'encodings' : AscCommon.getEncodingParams()};
		this.asc_fireCallback("asc_onAdvancedOptions", new AscCommon.asc_CAdvancedOptions(c_oAscAdvancedOptionsID.TXT, cp), this.advancedOptionsAction);
	};
	asc_docs_api.prototype._onOpenCommand = function(data)
	{
		var t = this;
		AscCommon.openFileCommand(data, this.documentUrlChanges, AscCommon.c_oSerFormat.Signature, function(error, result)
		{
			if (error)
			{
				t.asc_fireCallback("asc_onError", c_oAscError.ID.Unknown, c_oAscError.Level.Critical);
				return;
			}
			t.onEndLoadFile(result);
		});
	};
	asc_docs_api.prototype._downloadAs    = function(command, filetype, actionType, options, fCallbackRequest)
	{
		var t = this;
		if (!options)
		{
			options = {};
		}
		if (actionType)
		{
			this.sync_StartAction(c_oAscAsyncActionType.BlockInteraction, actionType);
		}
		// Меняем тип состояния (на сохранение)
		this.advancedOptionsAction = c_oAscAdvancedOptionsAction.Save;

		var dataContainer               = {data : null, part : null, index : 0, count : 0};
		var oAdditionalData             = {};
		oAdditionalData["c"]            = command;
		oAdditionalData["id"]           = this.documentId;
		oAdditionalData["userid"]       = this.documentUserId;
		oAdditionalData["vkey"]         = this.documentVKey;
		oAdditionalData["outputformat"] = filetype;
		oAdditionalData["title"]        = AscCommon.changeFileExtention(this.documentTitle, AscCommon.getExtentionByFormat(filetype));
		oAdditionalData["savetype"]     = AscCommon.c_oAscSaveTypes.CompleteAll;
		if ('savefromorigin' === command)
		{
			oAdditionalData["format"] = this.documentFormat;
		}
		if (DownloadType.Print === options.downloadType)
		{
			oAdditionalData["inline"] = 1;
		}
		if (options.isNoData)
		{
			;//nothing
		}
		else if (null == options.oDocumentMailMerge && c_oAscFileType.PDF === filetype)
		{
			var dd             = this.WordControl.m_oDrawingDocument;
			dataContainer.data = dd.ToRendererPart();
			//console.log(oAdditionalData["data"]);
		}
		else if (c_oAscFileType.JSON === filetype)
		{
			oAdditionalData['url']       = this.mailMergeFileData['url'];
			oAdditionalData['format']    = this.mailMergeFileData['fileType'];
			// ToDo select csv params
			oAdditionalData['codepage']  = AscCommon.c_oAscCodePageUtf8;
			oAdditionalData['delimiter'] = AscCommon.c_oAscCsvDelimiter.Comma
		}
		else if (c_oAscFileType.TXT === filetype && !options.txtOptions && null == options.oDocumentMailMerge && null == options.oMailMergeSendData)
		{
			// Мы открывали команду, надо ее закрыть.
			if (actionType)
			{
				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, actionType);
			}
			var cp            = {
				'codepage'  : AscCommon.c_oAscCodePageUtf8,
				'encodings' : AscCommon.getEncodingParams()
			};
			this.downloadType = options.downloadType;
			this.asc_fireCallback("asc_onAdvancedOptions", new AscCommon.asc_CAdvancedOptions(c_oAscAdvancedOptionsID.TXT, cp), this.advancedOptionsAction);
			return;
		}
		else if (c_oAscFileType.HTML === filetype && null == options.oDocumentMailMerge && null == options.oMailMergeSendData)
		{
			//в asc_nativeGetHtml будет вызван select all, чтобы выделился документ должны выйти из колонтитулов и автофигур
			var _e     = new AscCommon.CKeyboardEvent();
			_e.CtrlKey = false;
			_e.KeyCode = 27;
			this.WordControl.m_oLogicDocument.OnKeyDown(_e);
			//сделано через сервер, потому что нет простого механизма сохранения на клиенте
			dataContainer.data = '\ufeff' + window["asc_docs_api"].prototype["asc_nativeGetHtml"].call(this);
		}
		else
		{
			if (options.txtOptions instanceof Asc.asc_CTXTAdvancedOptions)
			{
				oAdditionalData["codepage"] = options.txtOptions.asc_getCodePage();
			}
			var oLogicDocument;
			if (null != options.oDocumentMailMerge)
				oLogicDocument = options.oDocumentMailMerge;
			else
				oLogicDocument = this.WordControl.m_oLogicDocument;
			var oBinaryFileWriter;
			if (null != options.oMailMergeSendData && c_oAscFileType.HTML == options.oMailMergeSendData.get_MailFormat())
				oBinaryFileWriter = new AscCommonWord.BinaryFileWriter(oLogicDocument, false, true);
			else
				oBinaryFileWriter = new AscCommonWord.BinaryFileWriter(oLogicDocument);
			dataContainer.data = oBinaryFileWriter.Write();
		}
		if (null != options.oMailMergeSendData)
		{
			oAdditionalData["mailmergesend"] = options.oMailMergeSendData;
			var MailMergeMap                 = this.WordControl.m_oLogicDocument.MailMergeMap;
			var aJsonOut                     = [];
			if (MailMergeMap.length > 0)
			{
				var oFirstRow = MailMergeMap[0];
				var aRowOut   = [];
				for (var i in oFirstRow)
					aRowOut.push(i);
				aJsonOut.push(aRowOut);
			}
			//todo может надо запоминать порядок for in в первом столбце, если for in будет по-разному обходить строки
			for (var i = 0; i < MailMergeMap.length; ++i)
			{
				var oRow    = MailMergeMap[i];
				var aRowOut = [];
				for (var j in oRow)
					aRowOut.push(oRow[j]);
				aJsonOut.push(aRowOut);
			}
			dataContainer.data = dataContainer.data.length + ';' + dataContainer.data + JSON.stringify(aJsonOut);
		}
		var fCallback = null;
		if (!options.isNoCallback)
		{
			fCallback = function(input)
			{
				var error = c_oAscError.ID.Unknown;
				//input = {'type': command, 'status': 'err', 'data': -80};
				if (null != input && command == input['type'])
				{
					if ('ok' == input['status'])
					{
						if (options.isNoUrl)
						{
							error = c_oAscError.ID.No;
						}
						else
						{
							var url = input['data'];
							if (url)
							{
								error = c_oAscError.ID.No;
								t.processSavedFile(url, options.downloadType);
							}
						}
					}
					else
					{
						error = mapAscServerErrorToAscError(parseInt(input["data"]));
					}
				}
				if (c_oAscError.ID.No != error)
				{
					t.asc_fireCallback('asc_onError', options.errorDirect || error, c_oAscError.Level.NoCritical);
				}
				// Меняем тип состояния (на никакое)
				t.advancedOptionsAction = c_oAscAdvancedOptionsAction.None;
				if (actionType)
				{
					t.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, actionType);
				}
			};
		}
		this.fCurCallback = fCallback;
		AscCommon.saveWithParts(function(fCallback1, oAdditionalData1, dataContainer1)
		{
			sendCommand(t, fCallback1, oAdditionalData1, dataContainer1);
		}, fCallback, fCallbackRequest, oAdditionalData, dataContainer);
	}

	// Вставка диаграмм
	asc_docs_api.prototype.asc_getChartObject = function(type)
	{
		this.isChartEditor = true;		// Для совместного редактирования
		if (!AscFormat.isRealNumber(type))
		{
			this.asc_onOpenChartFrame();
			this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Drawing_Props);
		}

		return this.WordControl.m_oLogicDocument.Get_ChartObject(type);
	};

	asc_docs_api.prototype.asc_addChartDrawingObject = function(options)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			History.Create_NewPoint(AscDFH.historydescription_Document_AddChart);
			this.WordControl.m_oLogicDocument.Add_InlineImage(null, null, null, options);
		}
	};
	asc_docs_api.prototype.asc_doubleClickOnChart    = function(obj)
	{
		this.isChartEditor = true;	// Для совместного редактирования
		this.asc_onOpenChartFrame();
		this.WordControl.onMouseUpMainSimple();
		this.asc_fireCallback("asc_doubleClickOnChart", obj);
	};

	asc_docs_api.prototype.asc_editChartDrawingObject = function(chartBinary)
	{
		/**/

		// Находим выделенную диаграмму и накатываем бинарник
		if (AscFormat.isObject(chartBinary))
		{
			var binary = chartBinary["binary"];
			if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			{
				History.Create_NewPoint(AscDFH.historydescription_Document_EditChart);
				this.WordControl.m_oLogicDocument.Edit_Chart(binary);
			}
		}
	};

	asc_docs_api.prototype.sync_closeChartEditor = function()
	{
		this.asc_fireCallback("asc_onCloseChartEditor");
	};

	asc_docs_api.prototype.asc_setDrawCollaborationMarks = function(bDraw)
	{
		if (!this.isLoadFullApi)
		{
			this.tmpCoMarksDraw = bDraw;
			return;
		}

		if (bDraw !== this.isCoMarksDraw)
		{
			this.isCoMarksDraw = bDraw;
			this.WordControl.m_oDrawingDocument.ClearCachePages();
			this.WordControl.m_oDrawingDocument.FirePaint();
		}
	};

	asc_docs_api.prototype.asc_AddMath = function(Type)
	{
		var loader   = AscCommon.g_font_loader;
		var fontinfo = g_fontApplication.GetFontInfo("Cambria Math");
		var isasync  = loader.LoadFont(fontinfo);
		if (false === isasync)
		{
			return this.asc_AddMath2(Type);
		}
		else
		{
			this.FontAsyncLoadType  = 1;
			this.FontAsyncLoadParam = Type;
		}
	};

	asc_docs_api.prototype.asc_AddMath2 = function(Type)
	{
		if (false === this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
		{
			this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddMath);
			var MathElement = new AscCommonWord.MathMenu(Type);
			this.WordControl.m_oLogicDocument.Paragraph_Add(MathElement);
		}
	};

	//----------------------------------------------------------------------------------------------------------------------
	// Функции для работы с MailMerge
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.asc_StartMailMerge              = function(oData)
	{
	};
	asc_docs_api.prototype.asc_StartMailMergeByList        = function(aList)
	{
	};
	asc_docs_api.prototype.asc_GetReceptionsCount          = function()
	{
	};
	asc_docs_api.prototype.asc_GetMailMergeFieldsNameList  = function()
	{
	};
	asc_docs_api.prototype.asc_AddMailMergeField           = function(Name)
	{
	};
	asc_docs_api.prototype.asc_SetHighlightMailMergeFields = function(Value)
	{
	};
	asc_docs_api.prototype.asc_PreviewMailMergeResult      = function(Index)
	{
	};
	asc_docs_api.prototype.asc_EndPreviewMailMergeResult   = function()
	{
	};
	asc_docs_api.prototype.sync_StartMailMerge             = function()
	{
	};
	asc_docs_api.prototype.sync_PreviewMailMergeResult     = function(Index)
	{
	};
	asc_docs_api.prototype.sync_EndPreviewMailMergeResult  = function()
	{
	};
	asc_docs_api.prototype.sync_HighlightMailMergeFields   = function(Value)
	{
	};
	asc_docs_api.prototype.asc_getMailMergeData            = function()
	{
	};
	asc_docs_api.prototype.asc_setMailMergeData            = function(aList)
	{
	};
	asc_docs_api.prototype.asc_sendMailMergeData           = function(oData)
	{
	};
	asc_docs_api.prototype.asc_GetMailMergeFiledValue      = function(nIndex, sName)
	{
	};
	//----------------------------------------------------------------------------------------------------------------------
	// Работаем со стилями
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.asc_GetStyleFromFormatting = function()
	{
		return null;
	};
	asc_docs_api.prototype.asc_AddNewStyle            = function(oStyle)
	{
	};
	asc_docs_api.prototype.asc_RemoveStyle            = function(sName)
	{
	};
	asc_docs_api.prototype.asc_RemoveAllCustomStyles  = function()
	{
	};
	asc_docs_api.prototype.asc_IsStyleDefault         = function(sName)
	{
		return true;
	};
	asc_docs_api.prototype.asc_IsDefaultStyleChanged  = function(sName)
	{
		return false;
	};
	asc_docs_api.prototype.asc_GetStyleNameById       = function(StyleId)
	{
		return this.WordControl.m_oLogicDocument.Get_StyleNameById(StyleId);
	};
	//----------------------------------------------------------------------------------------------------------------------
	// Работаем с рецензированием
	//----------------------------------------------------------------------------------------------------------------------
	asc_docs_api.prototype.asc_SetTrackRevisions               = function(bTrack)
	{
	};
	asc_docs_api.prototype.asc_IsTrackRevisions                = function()
	{
		return false;
	};
	asc_docs_api.prototype.sync_BeginCatchRevisionsChanges     = function()
	{
	};
	asc_docs_api.prototype.sync_EndCatchRevisionsChanges       = function()
	{
	};
	asc_docs_api.prototype.sync_AddRevisionsChange             = function(Change)
	{
	};
	asc_docs_api.prototype.asc_AcceptChanges                   = function(Change)
	{
	};
	asc_docs_api.prototype.asc_RejectChanges                   = function(Change)
	{
	};
	asc_docs_api.prototype.asc_HaveRevisionsChanges            = function()
	{
		return false
	};
	asc_docs_api.prototype.asc_HaveNewRevisionsChanges         = function()
	{
		return false
	};
	asc_docs_api.prototype.asc_GetNextRevisionsChange          = function()
	{
	};
	asc_docs_api.prototype.asc_GetPrevRevisionsChange          = function()
	{
	};
	asc_docs_api.prototype.sync_UpdateRevisionsChangesPosition = function(X, Y)
	{
	};
	asc_docs_api.prototype.asc_AcceptAllChanges                = function()
	{
	};
	asc_docs_api.prototype.asc_RejectAllChanges                = function()
	{
	};

	asc_docs_api.prototype.asc_undoAllChanges       = function()
	{
		this.WordControl.m_oLogicDocument.Document_Undo({All : true});
	};
	asc_docs_api.prototype.asc_CloseFile            = function()
	{
		History.Clear();
		g_oIdCounter.Clear();
		g_oTableId.Clear();
		AscCommon.CollaborativeEditing.Clear();
		this.isApplyChangesOnOpenEnabled = true;

		var oLogicDocument = this.WordControl.m_oLogicDocument;
		oLogicDocument.Stop_Recalculate();
		oLogicDocument.Stop_CheckSpelling();
		AscCommon.pptx_content_loader.ImageMapChecker = {};

		this.WordControl.m_oDrawingDocument.CloseFile();
	};
	asc_docs_api.prototype.asc_SetFastCollaborative = function(isOn)
	{
		if (AscCommon.CollaborativeEditing)
			AscCommon.CollaborativeEditing.Set_Fast(isOn);
	};

	asc_docs_api.prototype._onEndLoadSdk = function()
	{
		History           = AscCommon.History;
		g_fontApplication = AscFonts.g_fontApplication;
		PasteElementsId   = AscCommon.PasteElementsId;
		global_mouseEvent = AscCommon.global_mouseEvent;

		g_oTableId.init();
		this.WordControl      = new AscCommonWord.CEditorPage(this);
		this.WordControl.Name = this.HtmlElementName;

		this.CurrentTranslate = AscCommonWord.translations_map["en"];

		//выставляем тип copypaste
		PasteElementsId.g_bIsDocumentCopyPaste = true;

		this.CreateComponents();
		this.WordControl.Init();

		if (this.tmpFontRenderingMode)
		{
			this.SetFontRenderingMode(this.tmpFontRenderingMode);
		}
		if (null !== this.tmpViewRulers)
		{
			this.asc_SetViewRulers(this.tmpViewRulers);
		}
		if (null !== this.tmpZoomType)
		{
			switch (this.tmpZoomType)
			{
				case AscCommon.c_oZoomType.FitToPage:
					this.zoomFitToPage();
					break;
				case AscCommon.c_oZoomType.FitToWidth:
					this.zoomFitToWidth();
					break;
				case AscCommon.c_oZoomType.CustomMode:
					this.zoomCustomMode();
					break;
			}
		}

		if (this.isMobileVersion)
			this.SetMobileVersion(true);

		this.asc_setViewMode(this.isViewMode);
		this.asc_setDrawCollaborationMarks(this.tmpCoMarksDraw);

		asc_docs_api.superclass._onEndLoadSdk.call(this);

		if (this.isOnlyReaderMode)
			this.ImageLoader.bIsAsyncLoadDocumentImages = false;
	};

	asc_docs_api.prototype.asc_Recalculate = function(bIsUpdateInterface)
	{
		if (!this.WordControl.m_oLogicDocument)
			return;

		return this.WordControl.m_oLogicDocument.Recalculate_FromStart(bIsUpdateInterface);
	};

	asc_docs_api.prototype.asc_canPaste = function()
	{
		if (!this.WordControl ||
			!this.WordControl.m_oLogicDocument ||
			this.WordControl.m_oLogicDocument.Document_Is_SelectionLocked(changestype_Paragraph_Content))
			return false;

		this.WordControl.m_oLogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_AddSectionBreak);
		return true;
	};

	window["asc_docs_api"]                                      = asc_docs_api;
	window["asc_docs_api"].prototype["asc_nativeOpenFile"]      = function(base64File, version)
	{
		this.SpellCheckUrl = '';

		this.User = new AscCommon.asc_CUser();
		this.User.setId("TM");
		this.User.setUserName("native");

		this.WordControl.m_bIsRuler = false;
		this.WordControl.Init();

		this.InitEditor();
		this.DocumentType   = 2;
		this.LoadedObjectDS = this.WordControl.m_oLogicDocument.CopyStyle();

		g_oIdCounter.Set_Load(true);

		var openParams        = {checkFileSize : this.isMobileVersion, charCount : 0, parCount : 0};
		var oBinaryFileReader = new AscCommonWord.BinaryFileReader(this.WordControl.m_oLogicDocument, openParams);

		if (undefined === version)
		{
			if (oBinaryFileReader.Read(base64File))
			{
				g_oIdCounter.Set_Load(false);
				this.LoadedObject = 1;

				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);
			}
			else
				this.asc_fireCallback("asc_onError", c_oAscError.ID.MobileUnexpectedCharCount, c_oAscError.Level.Critical);
		}
		else
		{
			AscCommon.CurFileVersion = version;
			if (oBinaryFileReader.ReadData(base64File))
			{
				g_oIdCounter.Set_Load(false);
				this.LoadedObject = 1;

				this.sync_EndAction(c_oAscAsyncActionType.BlockInteraction, c_oAscAsyncAction.Open);
			}
			else
				this.asc_fireCallback("asc_onError", c_oAscError.ID.MobileUnexpectedCharCount, c_oAscError.Level.Critical);
		}

		if (window["NATIVE_EDITOR_ENJINE"] === true && undefined != window["native"])
		{
			AscCommon.CDocsCoApi.prototype.askSaveChanges = function(callback)
			{
				callback({"saveLock" : false});
			};
			AscCommon.CDocsCoApi.prototype.saveChanges    = function(arrayChanges, deleteIndex, excelAdditionalInfo)
			{
				if (window["native"]["SaveChanges"])
					window["native"]["SaveChanges"](arrayChanges.join("\",\""), deleteIndex, arrayChanges.length);
			};
		}

		if (undefined != window["Native"])
			return;

		//callback
		this.DocumentOrientation = (null == editor.WordControl.m_oLogicDocument) ? true : !editor.WordControl.m_oLogicDocument.Orientation;
		var sizeMM;
		if (this.DocumentOrientation)
			sizeMM = DocumentPageSize.getSize(AscCommon.Page_Width, AscCommon.Page_Height);
		else
			sizeMM = DocumentPageSize.getSize(AscCommon.Page_Height, AscCommon.Page_Width);
		this.sync_DocSizeCallback(sizeMM.w_mm, sizeMM.h_mm);
		this.sync_PageOrientCallback(editor.get_DocumentOrientation());

		if (this.GenerateNativeStyles !== undefined)
		{
			this.GenerateNativeStyles();

			if (this.WordControl.m_oDrawingDocument.CheckTableStylesOne !== undefined)
				this.WordControl.m_oDrawingDocument.CheckTableStylesOne();
		}
	};
	window["asc_docs_api"].prototype["asc_nativeCalculateFile"] = function()
	{
		if (null == this.WordControl.m_oLogicDocument)
			return;

		var Document = this.WordControl.m_oLogicDocument;

		if ((window["NATIVE_EDITOR_ENJINE"] === undefined) && this.isApplyChangesOnOpenEnabled)
		{
			this.isApplyChangesOnOpenEnabled = false;
			if (1 === AscCommon.CollaborativeEditing.m_nUseType)
			{
				this.isApplyChangesOnOpen = true;
				AscCommon.CollaborativeEditing.Apply_Changes();
				AscCommon.CollaborativeEditing.Release_Locks();
				return;
			}
		}

		Document.CurPos.ContentPos = 0;

		var RecalculateData =
			{
				Inline   : {Pos : 0, PageNum : 0},
				Flow     : [],
				HdrFtr   : [],
				Drawings : {
					All : true,
					Map : {}
				}
			};

		Document.Recalculate(false, false, RecalculateData);

		Document.Document_UpdateInterfaceState();
		//Document.Document_UpdateRulersState();
		Document.Document_UpdateSelectionState();

		this.ShowParaMarks = false;
	};

	window["asc_docs_api"].prototype["asc_nativeApplyChanges"] = function(changes)
	{
		this._coAuthoringSetChanges(changes, new AscCommonWord.CDocumentColor(191, 255, 199));
		AscCommon.CollaborativeEditing.Apply_OtherChanges();
	};

	window["asc_docs_api"].prototype.asc_SetSilentMode = function(bEnabled)
	{
		if (!this.WordControl.m_oLogicDocument)
			return;
		if (bEnabled)
			this.WordControl.m_oLogicDocument.Start_SilentMode();
		else
			this.WordControl.m_oLogicDocument.End_SilentMode();
	};

	window["asc_docs_api"].prototype["asc_nativeApplyChanges2"] = function(data, isFull)
	{
		// Чтобы заново созданные параграфы не отображались залоченными
		g_oIdCounter.Set_Load(true);

		var stream = new AscCommon.FT_Stream2(data, data.length);
		stream.obj = null;
		var Loader = {Reader : stream, Reader2 : null};
		var _color = new AscCommonWord.CDocumentColor(191, 255, 199);

		// Применяем изменения, пока они есть
		var _count = Loader.Reader.GetLong();

		var _pos = 4;
		for (var i = 0; i < _count; i++)
		{
			if (window["NATIVE_EDITOR_ENJINE"] === true && window["native"]["CheckNextChange"])
			{
				if (!window["native"]["CheckNextChange"]())
					break;
			}

			var _len    = Loader.Reader.GetLong();
			_pos += 4;
			stream.size = _pos + _len;

			var _id       = Loader.Reader.GetString2();
			var _read_pos = Loader.Reader.GetCurPos();

			var Type  = Loader.Reader.GetLong();
			var Class = null;

			if (AscDFH.historyitem_type_HdrFtr === Type)
			{
				Class = editor.WordControl.m_oLogicDocument.HdrFtr;
			}
			else
				Class = g_oTableId.Get_ById(_id);

			stream.Seek(_read_pos);
			stream.Seek2(_read_pos);

			if (null != Class)
				Class.Load_Changes(Loader.Reader, Loader.Reader2, _color);

			_pos += _len;
			stream.Seek2(_pos);
			stream.size = data.length;
		}

		if (isFull)
		{
			AscCommon.CollaborativeEditing.m_aChanges = [];

			// У новых элементов выставляем указатели на другие классы
			AscCommon.CollaborativeEditing.Apply_LinkData();

			// Делаем проверки корректности новых изменений
			AscCommon.CollaborativeEditing.Check_MergeData();

			AscCommon.CollaborativeEditing.OnEnd_ReadForeignChanges();

			if (window["NATIVE_EDITOR_ENJINE"] === true && window["native"]["AddImageInChanges"])
			{
				var _new_images     = AscCommon.CollaborativeEditing.m_aNewImages;
				var _new_images_len = _new_images.length;

				for (var nImage = 0; nImage < _new_images_len; nImage++)
					window["native"]["AddImageInChanges"](_new_images[nImage]);
			}
		}

		g_oIdCounter.Set_Load(false);
	};

	window["asc_docs_api"].prototype["asc_nativeGetFile"] = function()
	{
		var oBinaryFileWriter = new AscCommonWord.BinaryFileWriter(this.WordControl.m_oLogicDocument);
		return oBinaryFileWriter.Write();
	};

	window["asc_docs_api"].prototype["asc_nativeGetFileData"] = function()
	{
		var oBinaryFileWriter = new AscCommonWord.BinaryFileWriter(this.WordControl.m_oLogicDocument);
		var _memory           = oBinaryFileWriter.memory;

		oBinaryFileWriter.Write2();

		var _header = AscCommon.c_oSerFormat.Signature + ";v" + AscCommon.c_oSerFormat.Version + ";" + _memory.GetCurPosition() + ";";
		window["native"]["Save_End"](_header, _memory.GetCurPosition());

		return _memory.ImData.data;
	};

	window["asc_docs_api"].prototype["asc_nativeGetHtml"] = function()
	{
		var _old                           = PasteElementsId.copyPasteUseBinary;
		PasteElementsId.copyPasteUseBinary = false;
		this.WordControl.m_oLogicDocument.Select_All();
		var oCopyProcessor = new AscCommon.CopyProcessor(this);
		oCopyProcessor.Start();
		var _ret = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" /></head><body>" + oCopyProcessor.getInnerHtml() + "</body></html>";
		this.WordControl.m_oLogicDocument.Selection_Remove();
		PasteElementsId.copyPasteUseBinary = _old;
		return _ret;
	};

	window["asc_docs_api"].prototype["asc_AddHtml"] = function(_iframeId)
	{
		var ifr = document.getElementById(_iframeId);

		var frameWindow = window.frames[_iframeId];
		if (frameWindow)
		{
			if (null != frameWindow.document && null != frameWindow.document.body)
			{
				ifr.style.display = "block";
				this.WordControl.m_oLogicDocument.TurnOffHistory();
				AscCommon.Editor_Paste_Exec(this, frameWindow.document.body, ifr);
				this.WordControl.m_oLogicDocument.TurnOnHistory();
			}
		}

		if (ifr)
			document.body.removeChild(ifr);
	};

	window["asc_docs_api"].prototype["asc_nativeCheckPdfRenderer"] = function(_memory1, _memory2)
	{
		if (true)
		{
			// pos не должен минимизироваться!!!

			_memory1.Copy          = _memory1["Copy"];
			_memory1.ClearNoAttack = _memory1["ClearNoAttack"];
			_memory1.WriteByte     = _memory1["WriteByte"];
			_memory1.WriteBool     = _memory1["WriteBool"];
			_memory1.WriteLong     = _memory1["WriteLong"];
			_memory1.WriteDouble   = _memory1["WriteDouble"];
			_memory1.WriteString   = _memory1["WriteString"];
			_memory1.WriteString2  = _memory1["WriteString2"];

			_memory2.Copy          = _memory1["Copy"];
			_memory2.ClearNoAttack = _memory1["ClearNoAttack"];
			_memory2.WriteByte     = _memory1["WriteByte"];
			_memory2.WriteBool     = _memory1["WriteBool"];
			_memory2.WriteLong     = _memory1["WriteLong"];
			_memory2.WriteDouble   = _memory1["WriteDouble"];
			_memory2.WriteString   = _memory1["WriteString"];
			_memory2.WriteString2  = _memory1["WriteString2"];
		}

		var _printer                  = new AscCommon.CDocumentRenderer();
		_printer.Memory               = _memory1;
		_printer.VectorMemoryForPrint = _memory2;
		return _printer;
	};

	window["asc_docs_api"].prototype["asc_nativeCalculate"] = function()
	{
	};

	window["asc_docs_api"].prototype["asc_nativePrint"] = function(_printer, _page)
	{
		if (undefined === _printer && _page === undefined)
		{
			if (undefined !== window["AscDesktopEditor"])
			{
				var _drawing_document = this.WordControl.m_oDrawingDocument;
				var pagescount        = Math.min(_drawing_document.m_lPagesCount, _drawing_document.m_lCountCalculatePages);

				window["AscDesktopEditor"]["Print_Start"](this.DocumentUrl, pagescount, "", this.getCurrentPage());

				var oDocRenderer                  = new AscCommon.CDocumentRenderer();
				oDocRenderer.VectorMemoryForPrint = new AscCommon.CMemory();
				var bOldShowMarks                 = this.ShowParaMarks;
				this.ShowParaMarks                = false;

				for (var i = 0; i < pagescount; i++)
				{
					oDocRenderer.Memory.Seek(0);
					oDocRenderer.VectorMemoryForPrint.ClearNoAttack();

					var page = _drawing_document.m_arrPages[i];
					oDocRenderer.BeginPage(page.width_mm, page.height_mm);
					this.WordControl.m_oLogicDocument.DrawPage(i, oDocRenderer);
					oDocRenderer.EndPage();

					window["AscDesktopEditor"]["Print_Page"](oDocRenderer.Memory.GetBase64Memory(), page.width_mm, page.height_mm);
				}

				this.ShowParaMarks = bOldShowMarks;

				window["AscDesktopEditor"]["Print_End"]();
			}
			return;
		}

		var page = this.WordControl.m_oDrawingDocument.m_arrPages[_page];
		_printer.BeginPage(page.width_mm, page.height_mm);
		this.WordControl.m_oLogicDocument.DrawPage(_page, _printer);
		_printer.EndPage();
	};

	window["asc_docs_api"].prototype["asc_nativePrintPagesCount"] = function()
	{
		return this.WordControl.m_oDrawingDocument.m_lPagesCount;
	};

	window["asc_docs_api"].prototype["asc_nativeGetPDF"] = function()
	{
		var pagescount = this["asc_nativePrintPagesCount"]();

		var _renderer                  = new AscCommon.CDocumentRenderer();
		_renderer.VectorMemoryForPrint = new AscCommon.CMemory();
		var _bOldShowMarks             = this.ShowParaMarks;
		this.ShowParaMarks             = false;

		for (var i = 0; i < pagescount; i++)
		{
			this["asc_nativePrint"](_renderer, i);
		}

		this.ShowParaMarks = _bOldShowMarks;

		window["native"]["Save_End"]("", _renderer.Memory.GetCurPosition());

		return _renderer.Memory.data;
	};

	// cool api (autotests)
	window["asc_docs_api"].prototype["Add_Text"]                     = function(_text)
	{
		this.WordControl.m_oLogicDocument.TextBox_Put(_text);
	};
	window["asc_docs_api"].prototype["Add_NewParagraph"]             = function()
	{
		var LogicDocument = this.WordControl.m_oLogicDocument;
		if (false === LogicDocument.Document_Is_SelectionLocked(AscCommon.changestype_Document_Content_Add))
		{
			LogicDocument.Create_NewHistoryPoint(AscDFH.historydescription_Document_EnterButton);
			LogicDocument.Add_NewParagraph(true);
		}
	};
	window["asc_docs_api"].prototype["Cursor_MoveLeft"]              = function()
	{
		this.WordControl.m_oLogicDocument.Cursor_MoveLeft();
	};
	window["asc_docs_api"].prototype["Cursor_MoveRight"]             = function()
	{
		this.WordControl.m_oLogicDocument.Cursor_MoveRight();
	};
	window["asc_docs_api"].prototype["Cursor_MoveUp"]                = function()
	{
		this.WordControl.m_oLogicDocument.Cursor_MoveUp();
	};
	window["asc_docs_api"].prototype["Cursor_MoveDown"]              = function()
	{
		this.WordControl.m_oLogicDocument.Cursor_MoveDown();
	};
	window["asc_docs_api"].prototype["Get_DocumentRecalcId"]         = function()
	{
		return this.WordControl.m_oLogicDocument.RecalcId;
	};
	window["asc_docs_api"].prototype["asc_IsSpellCheckCurrentWord"]  = function()
	{
		return this.IsSpellCheckCurrentWord;
	};
	window["asc_docs_api"].prototype["asc_putSpellCheckCurrentWord"] = function(value)
	{
		this.IsSpellCheckCurrentWord = value;
	};

	// desktop editor spellcheck
	function CSpellCheckApi_desktop()
	{
		this.docId = undefined;

		this.init = function(docid)
		{
			this.docId = docid;
		};

		this.set_url = function(url)
		{
		};

		this.spellCheck = function(spellData)
		{
			window["AscDesktopEditor"]["SpellCheck"](spellData);
		};

		this.onSpellCheck = function(spellData)
		{
			editor.SpellCheck_CallBack(spellData);
		};

		this.disconnect = function()
		{
			// none
		};
	}

	window["AscDesktopEditor_Save"] = function()
	{
		return editor.asc_Save(false);
	};

	//-------------------------------------------------------------export---------------------------------------------------
	window['Asc']                                                       = window['Asc'] || {};
	CAscSection.prototype['get_PageWidth']                              = CAscSection.prototype.get_PageWidth;
	CAscSection.prototype['get_PageHeight']                             = CAscSection.prototype.get_PageHeight;
	CAscSection.prototype['get_MarginLeft']                             = CAscSection.prototype.get_MarginLeft;
	CAscSection.prototype['get_MarginRight']                            = CAscSection.prototype.get_MarginRight;
	CAscSection.prototype['get_MarginTop']                              = CAscSection.prototype.get_MarginTop;
	CAscSection.prototype['get_MarginBottom']                           = CAscSection.prototype.get_MarginBottom;
	CHeaderProp.prototype['get_Type']                                   = CHeaderProp.prototype.get_Type;
	CHeaderProp.prototype['put_Type']                                   = CHeaderProp.prototype.put_Type;
	CHeaderProp.prototype['get_Position']                               = CHeaderProp.prototype.get_Position;
	CHeaderProp.prototype['put_Position']                               = CHeaderProp.prototype.put_Position;
	CHeaderProp.prototype['get_DifferentFirst']                         = CHeaderProp.prototype.get_DifferentFirst;
	CHeaderProp.prototype['put_DifferentFirst']                         = CHeaderProp.prototype.put_DifferentFirst;
	CHeaderProp.prototype['get_DifferentEvenOdd']                       = CHeaderProp.prototype.get_DifferentEvenOdd;
	CHeaderProp.prototype['put_DifferentEvenOdd']                       = CHeaderProp.prototype.put_DifferentEvenOdd;
	CHeaderProp.prototype['get_LinkToPrevious']                         = CHeaderProp.prototype.get_LinkToPrevious;
	CHeaderProp.prototype['get_Locked']                                 = CHeaderProp.prototype.get_Locked;
	window['Asc']['CMailMergeSendData']                                 = CMailMergeSendData;
	CMailMergeSendData.prototype['get_From']                            = CMailMergeSendData.prototype.get_From;
	CMailMergeSendData.prototype['put_From']                            = CMailMergeSendData.prototype.put_From;
	CMailMergeSendData.prototype['get_To']                              = CMailMergeSendData.prototype.get_To;
	CMailMergeSendData.prototype['put_To']                              = CMailMergeSendData.prototype.put_To;
	CMailMergeSendData.prototype['get_Subject']                         = CMailMergeSendData.prototype.get_Subject;
	CMailMergeSendData.prototype['put_Subject']                         = CMailMergeSendData.prototype.put_Subject;
	CMailMergeSendData.prototype['get_MailFormat']                      = CMailMergeSendData.prototype.get_MailFormat;
	CMailMergeSendData.prototype['put_MailFormat']                      = CMailMergeSendData.prototype.put_MailFormat;
	CMailMergeSendData.prototype['get_FileName']                        = CMailMergeSendData.prototype.get_FileName;
	CMailMergeSendData.prototype['put_FileName']                        = CMailMergeSendData.prototype.put_FileName;
	CMailMergeSendData.prototype['get_Message']                         = CMailMergeSendData.prototype.get_Message;
	CMailMergeSendData.prototype['put_Message']                         = CMailMergeSendData.prototype.put_Message;
	CMailMergeSendData.prototype['get_RecordFrom']                      = CMailMergeSendData.prototype.get_RecordFrom;
	CMailMergeSendData.prototype['put_RecordFrom']                      = CMailMergeSendData.prototype.put_RecordFrom;
	CMailMergeSendData.prototype['get_RecordTo']                        = CMailMergeSendData.prototype.get_RecordTo;
	CMailMergeSendData.prototype['put_RecordTo']                        = CMailMergeSendData.prototype.put_RecordTo;
	CMailMergeSendData.prototype['get_RecordCount']                     = CMailMergeSendData.prototype.get_RecordCount;
	CMailMergeSendData.prototype['put_RecordCount']                     = CMailMergeSendData.prototype.put_RecordCount;
	CMailMergeSendData.prototype['get_UserId']                          = CMailMergeSendData.prototype.get_UserId;
	CMailMergeSendData.prototype['put_UserId']                          = CMailMergeSendData.prototype.put_UserId;
	window['Asc']['asc_docs_api']                                       = asc_docs_api;
	asc_docs_api.prototype['LoadFontsFromServer']                       = asc_docs_api.prototype.LoadFontsFromServer;
	asc_docs_api.prototype['SetCollaborativeMarksShowType']             = asc_docs_api.prototype.SetCollaborativeMarksShowType;
	asc_docs_api.prototype['GetCollaborativeMarksShowType']             = asc_docs_api.prototype.GetCollaborativeMarksShowType;
	asc_docs_api.prototype['Clear_CollaborativeMarks']                  = asc_docs_api.prototype.Clear_CollaborativeMarks;
	asc_docs_api.prototype['SetLanguage']                               = asc_docs_api.prototype.SetLanguage;
	asc_docs_api.prototype['asc_GetFontThumbnailsPath']                 = asc_docs_api.prototype.asc_GetFontThumbnailsPath;
	asc_docs_api.prototype['TranslateStyleName']                        = asc_docs_api.prototype.TranslateStyleName;
	asc_docs_api.prototype['CheckChangedDocument']                      = asc_docs_api.prototype.CheckChangedDocument;
	asc_docs_api.prototype['SetUnchangedDocument']                      = asc_docs_api.prototype.SetUnchangedDocument;
	asc_docs_api.prototype['SetDocumentModified']                       = asc_docs_api.prototype.SetDocumentModified;
	asc_docs_api.prototype['isDocumentModified']                        = asc_docs_api.prototype.isDocumentModified;
	asc_docs_api.prototype['asc_isDocumentCanSave']                     = asc_docs_api.prototype.asc_isDocumentCanSave;
	asc_docs_api.prototype['sync_BeginCatchSelectedElements']           = asc_docs_api.prototype.sync_BeginCatchSelectedElements;
	asc_docs_api.prototype['sync_EndCatchSelectedElements']             = asc_docs_api.prototype.sync_EndCatchSelectedElements;
	asc_docs_api.prototype['getSelectedElements']                       = asc_docs_api.prototype.getSelectedElements;
	asc_docs_api.prototype['sync_ChangeLastSelectedElement']            = asc_docs_api.prototype.sync_ChangeLastSelectedElement;
	asc_docs_api.prototype['asc_getEditorPermissions']                  = asc_docs_api.prototype.asc_getEditorPermissions;
	asc_docs_api.prototype['asc_setDocInfo']                            = asc_docs_api.prototype.asc_setDocInfo;
	asc_docs_api.prototype['asc_setLocale']                             = asc_docs_api.prototype.asc_setLocale;
	asc_docs_api.prototype['asc_LoadDocument']                          = asc_docs_api.prototype.asc_LoadDocument;
	asc_docs_api.prototype['SetTextBoxInputMode']                       = asc_docs_api.prototype.SetTextBoxInputMode;
	asc_docs_api.prototype['GetTextBoxInputMode']                       = asc_docs_api.prototype.GetTextBoxInputMode;
	asc_docs_api.prototype['ChangeReaderMode']                          = asc_docs_api.prototype.ChangeReaderMode;
	asc_docs_api.prototype['SetReaderModeOnly']                         = asc_docs_api.prototype.SetReaderModeOnly;
	asc_docs_api.prototype['IncreaseReaderFontSize']                    = asc_docs_api.prototype.IncreaseReaderFontSize;
	asc_docs_api.prototype['DecreaseReaderFontSize']                    = asc_docs_api.prototype.DecreaseReaderFontSize;
	asc_docs_api.prototype['CreateCSS']                                 = asc_docs_api.prototype.CreateCSS;
	asc_docs_api.prototype['GetCopyPasteDivId']                         = asc_docs_api.prototype.GetCopyPasteDivId;
	asc_docs_api.prototype['ContentToHTML']                             = asc_docs_api.prototype.ContentToHTML;
	asc_docs_api.prototype['InitEditor']                                = asc_docs_api.prototype.InitEditor;
	asc_docs_api.prototype['InitViewer']                                = asc_docs_api.prototype.InitViewer;
	asc_docs_api.prototype['OpenDocument']                              = asc_docs_api.prototype.OpenDocument;
	asc_docs_api.prototype['OpenDocument2']                             = asc_docs_api.prototype.OpenDocument2;
	asc_docs_api.prototype['asc_getDocumentName']                       = asc_docs_api.prototype.asc_getDocumentName;
	asc_docs_api.prototype['asc_registerCallback']                      = asc_docs_api.prototype.asc_registerCallback;
	asc_docs_api.prototype['asc_unregisterCallback']                    = asc_docs_api.prototype.asc_unregisterCallback;
	asc_docs_api.prototype['asc_fireCallback']                          = asc_docs_api.prototype.asc_fireCallback;
	asc_docs_api.prototype['asc_checkNeedCallback']                     = asc_docs_api.prototype.asc_checkNeedCallback;
	asc_docs_api.prototype['asc_getPropertyEditorShapes']               = asc_docs_api.prototype.asc_getPropertyEditorShapes;
	asc_docs_api.prototype['asc_getPropertyEditorTextArts']             = asc_docs_api.prototype.asc_getPropertyEditorTextArts;
	asc_docs_api.prototype['get_PropertyThemeColors']                   = asc_docs_api.prototype.get_PropertyThemeColors;
	asc_docs_api.prototype['get_PropertyThemeColorSchemes']             = asc_docs_api.prototype.get_PropertyThemeColorSchemes;
	asc_docs_api.prototype['_coAuthoringSetChange']                     = asc_docs_api.prototype._coAuthoringSetChange;
	asc_docs_api.prototype['_coAuthoringSetChanges']                    = asc_docs_api.prototype._coAuthoringSetChanges;
	asc_docs_api.prototype['asc_coAuthoringChatSendMessage']            = asc_docs_api.prototype.asc_coAuthoringChatSendMessage;
	asc_docs_api.prototype['asc_coAuthoringChatGetMessages']            = asc_docs_api.prototype.asc_coAuthoringChatGetMessages;
	asc_docs_api.prototype['asc_coAuthoringGetUsers']                   = asc_docs_api.prototype.asc_coAuthoringGetUsers;
	asc_docs_api.prototype['asc_coAuthoringDisconnect']                 = asc_docs_api.prototype.asc_coAuthoringDisconnect;
	asc_docs_api.prototype['asc_getSpellCheckLanguages']                = asc_docs_api.prototype.asc_getSpellCheckLanguages;
	asc_docs_api.prototype['asc_SpellCheckDisconnect']                  = asc_docs_api.prototype.asc_SpellCheckDisconnect;
	asc_docs_api.prototype['_onUpdateDocumentCanSave']                  = asc_docs_api.prototype._onUpdateDocumentCanSave;
	asc_docs_api.prototype['put_FramePr']                               = asc_docs_api.prototype.put_FramePr;
	asc_docs_api.prototype['asyncFontEndLoaded_MathDraw']               = asc_docs_api.prototype.asyncFontEndLoaded_MathDraw;
	asc_docs_api.prototype['sendMathTypesToMenu']                       = asc_docs_api.prototype.sendMathTypesToMenu;
	asc_docs_api.prototype['asyncFontEndLoaded_DropCap']                = asc_docs_api.prototype.asyncFontEndLoaded_DropCap;
	asc_docs_api.prototype['asc_addDropCap']                            = asc_docs_api.prototype.asc_addDropCap;
	asc_docs_api.prototype['removeDropcap']                             = asc_docs_api.prototype.removeDropcap;
	asc_docs_api.prototype['get_TextProps']                             = asc_docs_api.prototype.get_TextProps;
	asc_docs_api.prototype['GetJSONLogicDocument']                      = asc_docs_api.prototype.GetJSONLogicDocument;
	asc_docs_api.prototype['get_ContentCount']                          = asc_docs_api.prototype.get_ContentCount;
	asc_docs_api.prototype['select_Element']                            = asc_docs_api.prototype.select_Element;
	asc_docs_api.prototype['UpdateTextPr']                              = asc_docs_api.prototype.UpdateTextPr;
	asc_docs_api.prototype['UpdateParagraphProp']                       = asc_docs_api.prototype.UpdateParagraphProp;
	asc_docs_api.prototype['asc_Print']                                 = asc_docs_api.prototype.asc_Print;
	asc_docs_api.prototype['Undo']                                      = asc_docs_api.prototype.Undo;
	asc_docs_api.prototype['Redo']                                      = asc_docs_api.prototype.Redo;
	asc_docs_api.prototype['Copy']                                      = asc_docs_api.prototype.Copy;
	asc_docs_api.prototype['Update_ParaTab']                            = asc_docs_api.prototype.Update_ParaTab;
	asc_docs_api.prototype['Cut']                                       = asc_docs_api.prototype.Cut;
	asc_docs_api.prototype['Paste']                                     = asc_docs_api.prototype.Paste;
	asc_docs_api.prototype['Share']                                     = asc_docs_api.prototype.Share;
	asc_docs_api.prototype['asc_Save']                                  = asc_docs_api.prototype.asc_Save;
	asc_docs_api.prototype['asc_DownloadAs']                            = asc_docs_api.prototype.asc_DownloadAs;
	asc_docs_api.prototype['asc_DownloadAsMailMerge']                   = asc_docs_api.prototype.asc_DownloadAsMailMerge;
	asc_docs_api.prototype['asc_DownloadOrigin']                        = asc_docs_api.prototype.asc_DownloadOrigin;
	asc_docs_api.prototype['Resize']                                    = asc_docs_api.prototype.Resize;
	asc_docs_api.prototype['AddURL']                                    = asc_docs_api.prototype.AddURL;
	asc_docs_api.prototype['Help']                                      = asc_docs_api.prototype.Help;
	asc_docs_api.prototype['asc_setAdvancedOptions']                    = asc_docs_api.prototype.asc_setAdvancedOptions;
	asc_docs_api.prototype['SetFontRenderingMode']                      = asc_docs_api.prototype.SetFontRenderingMode;
	asc_docs_api.prototype['startGetDocInfo']                           = asc_docs_api.prototype.startGetDocInfo;
	asc_docs_api.prototype['stopGetDocInfo']                            = asc_docs_api.prototype.stopGetDocInfo;
	asc_docs_api.prototype['sync_DocInfoCallback']                      = asc_docs_api.prototype.sync_DocInfoCallback;
	asc_docs_api.prototype['sync_GetDocInfoStartCallback']              = asc_docs_api.prototype.sync_GetDocInfoStartCallback;
	asc_docs_api.prototype['sync_GetDocInfoStopCallback']               = asc_docs_api.prototype.sync_GetDocInfoStopCallback;
	asc_docs_api.prototype['sync_GetDocInfoEndCallback']                = asc_docs_api.prototype.sync_GetDocInfoEndCallback;
	asc_docs_api.prototype['sync_CanUndoCallback']                      = asc_docs_api.prototype.sync_CanUndoCallback;
	asc_docs_api.prototype['sync_CanRedoCallback']                      = asc_docs_api.prototype.sync_CanRedoCallback;
	asc_docs_api.prototype['can_CopyCut']                               = asc_docs_api.prototype.can_CopyCut;
	asc_docs_api.prototype['sync_CanCopyCutCallback']                   = asc_docs_api.prototype.sync_CanCopyCutCallback;
	asc_docs_api.prototype['setStartPointHistory']                      = asc_docs_api.prototype.setStartPointHistory;
	asc_docs_api.prototype['setEndPointHistory']                        = asc_docs_api.prototype.setEndPointHistory;
	asc_docs_api.prototype['sync_CursorLockCallBack']                   = asc_docs_api.prototype.sync_CursorLockCallBack;
	asc_docs_api.prototype['sync_UndoCallBack']                         = asc_docs_api.prototype.sync_UndoCallBack;
	asc_docs_api.prototype['sync_RedoCallBack']                         = asc_docs_api.prototype.sync_RedoCallBack;
	asc_docs_api.prototype['sync_CopyCallBack']                         = asc_docs_api.prototype.sync_CopyCallBack;
	asc_docs_api.prototype['sync_CutCallBack']                          = asc_docs_api.prototype.sync_CutCallBack;
	asc_docs_api.prototype['sync_PasteCallBack']                        = asc_docs_api.prototype.sync_PasteCallBack;
	asc_docs_api.prototype['sync_ShareCallBack']                        = asc_docs_api.prototype.sync_ShareCallBack;
	asc_docs_api.prototype['sync_SaveCallBack']                         = asc_docs_api.prototype.sync_SaveCallBack;
	asc_docs_api.prototype['sync_DownloadAsCallBack']                   = asc_docs_api.prototype.sync_DownloadAsCallBack;
	asc_docs_api.prototype['sync_StartAction']                          = asc_docs_api.prototype.sync_StartAction;
	asc_docs_api.prototype['sync_EndAction']                            = asc_docs_api.prototype.sync_EndAction;
	asc_docs_api.prototype['sync_AddURLCallback']                       = asc_docs_api.prototype.sync_AddURLCallback;
	asc_docs_api.prototype['sync_ErrorCallback']                        = asc_docs_api.prototype.sync_ErrorCallback;
	asc_docs_api.prototype['sync_HelpCallback']                         = asc_docs_api.prototype.sync_HelpCallback;
	asc_docs_api.prototype['sync_UpdateZoom']                           = asc_docs_api.prototype.sync_UpdateZoom;
	asc_docs_api.prototype['ClearPropObjCallback']                      = asc_docs_api.prototype.ClearPropObjCallback;
	asc_docs_api.prototype['CollectHeaders']                            = asc_docs_api.prototype.CollectHeaders;
	asc_docs_api.prototype['GetActiveHeader']                           = asc_docs_api.prototype.GetActiveHeader;
	asc_docs_api.prototype['gotoHeader']                                = asc_docs_api.prototype.gotoHeader;
	asc_docs_api.prototype['sync_ChangeActiveHeaderCallback']           = asc_docs_api.prototype.sync_ChangeActiveHeaderCallback;
	asc_docs_api.prototype['sync_ReturnHeadersCallback']                = asc_docs_api.prototype.sync_ReturnHeadersCallback;
	asc_docs_api.prototype['asc_searchEnabled']                         = asc_docs_api.prototype.asc_searchEnabled;
	asc_docs_api.prototype['asc_findText']                              = asc_docs_api.prototype.asc_findText;
	asc_docs_api.prototype['asc_replaceText']                           = asc_docs_api.prototype.asc_replaceText;
	asc_docs_api.prototype['asc_selectSearchingResults']                = asc_docs_api.prototype.asc_selectSearchingResults;
	asc_docs_api.prototype['asc_isSelectSearchingResults']              = asc_docs_api.prototype.asc_isSelectSearchingResults;
	asc_docs_api.prototype['sync_ReplaceAllCallback']                   = asc_docs_api.prototype.sync_ReplaceAllCallback;
	asc_docs_api.prototype['sync_SearchEndCallback']                    = asc_docs_api.prototype.sync_SearchEndCallback;
	asc_docs_api.prototype['put_TextPrFontName']                        = asc_docs_api.prototype.put_TextPrFontName;
	asc_docs_api.prototype['put_TextPrFontSize']                        = asc_docs_api.prototype.put_TextPrFontSize;
	asc_docs_api.prototype['put_TextPrBold']                            = asc_docs_api.prototype.put_TextPrBold;
	asc_docs_api.prototype['put_TextPrItalic']                          = asc_docs_api.prototype.put_TextPrItalic;
	asc_docs_api.prototype['put_TextPrUnderline']                       = asc_docs_api.prototype.put_TextPrUnderline;
	asc_docs_api.prototype['put_TextPrStrikeout']                       = asc_docs_api.prototype.put_TextPrStrikeout;
	asc_docs_api.prototype['put_TextPrDStrikeout']                      = asc_docs_api.prototype.put_TextPrDStrikeout;
	asc_docs_api.prototype['put_TextPrSpacing']                         = asc_docs_api.prototype.put_TextPrSpacing;
	asc_docs_api.prototype['put_TextPrCaps']                            = asc_docs_api.prototype.put_TextPrCaps;
	asc_docs_api.prototype['put_TextPrSmallCaps']                       = asc_docs_api.prototype.put_TextPrSmallCaps;
	asc_docs_api.prototype['put_TextPrPosition']                        = asc_docs_api.prototype.put_TextPrPosition;
	asc_docs_api.prototype['put_TextPrLang']                            = asc_docs_api.prototype.put_TextPrLang;
	asc_docs_api.prototype['put_PrLineSpacing']                         = asc_docs_api.prototype.put_PrLineSpacing;
	asc_docs_api.prototype['put_LineSpacingBeforeAfter']                = asc_docs_api.prototype.put_LineSpacingBeforeAfter;
	asc_docs_api.prototype['FontSizeIn']                                = asc_docs_api.prototype.FontSizeIn;
	asc_docs_api.prototype['FontSizeOut']                               = asc_docs_api.prototype.FontSizeOut;
	asc_docs_api.prototype['put_Borders']                               = asc_docs_api.prototype.put_Borders;
	asc_docs_api.prototype['sync_BoldCallBack']                         = asc_docs_api.prototype.sync_BoldCallBack;
	asc_docs_api.prototype['sync_ItalicCallBack']                       = asc_docs_api.prototype.sync_ItalicCallBack;
	asc_docs_api.prototype['sync_UnderlineCallBack']                    = asc_docs_api.prototype.sync_UnderlineCallBack;
	asc_docs_api.prototype['sync_StrikeoutCallBack']                    = asc_docs_api.prototype.sync_StrikeoutCallBack;
	asc_docs_api.prototype['sync_TextPrFontFamilyCallBack']             = asc_docs_api.prototype.sync_TextPrFontFamilyCallBack;
	asc_docs_api.prototype['sync_TextPrFontSizeCallBack']               = asc_docs_api.prototype.sync_TextPrFontSizeCallBack;
	asc_docs_api.prototype['sync_PrLineSpacingCallBack']                = asc_docs_api.prototype.sync_PrLineSpacingCallBack;
	asc_docs_api.prototype['sync_InitEditorTableStyles']                = asc_docs_api.prototype.sync_InitEditorTableStyles;
	asc_docs_api.prototype['paraApply']                                 = asc_docs_api.prototype.paraApply;
	asc_docs_api.prototype['put_PrAlign']                               = asc_docs_api.prototype.put_PrAlign;
	asc_docs_api.prototype['put_TextPrBaseline']                        = asc_docs_api.prototype.put_TextPrBaseline;
	asc_docs_api.prototype['put_ListType']                              = asc_docs_api.prototype.put_ListType;
	asc_docs_api.prototype['put_Style']                                 = asc_docs_api.prototype.put_Style;
	asc_docs_api.prototype['SetDeviceInputHelperId']                    = asc_docs_api.prototype.SetDeviceInputHelperId;
	asc_docs_api.prototype['put_ShowSnapLines']                         = asc_docs_api.prototype.put_ShowSnapLines;
	asc_docs_api.prototype['get_ShowSnapLines']                         = asc_docs_api.prototype.get_ShowSnapLines;
	asc_docs_api.prototype['put_ShowParaMarks']                         = asc_docs_api.prototype.put_ShowParaMarks;
	asc_docs_api.prototype['get_ShowParaMarks']                         = asc_docs_api.prototype.get_ShowParaMarks;
	asc_docs_api.prototype['put_ShowTableEmptyLine']                    = asc_docs_api.prototype.put_ShowTableEmptyLine;
	asc_docs_api.prototype['get_ShowTableEmptyLine']                    = asc_docs_api.prototype.get_ShowTableEmptyLine;
	asc_docs_api.prototype['put_PageBreak']                             = asc_docs_api.prototype.put_PageBreak;
	asc_docs_api.prototype['put_WidowControl']                          = asc_docs_api.prototype.put_WidowControl;
	asc_docs_api.prototype['put_KeepLines']                             = asc_docs_api.prototype.put_KeepLines;
	asc_docs_api.prototype['put_KeepNext']                              = asc_docs_api.prototype.put_KeepNext;
	asc_docs_api.prototype['put_AddSpaceBetweenPrg']                    = asc_docs_api.prototype.put_AddSpaceBetweenPrg;
	asc_docs_api.prototype['put_LineHighLight']                         = asc_docs_api.prototype.put_LineHighLight;
	asc_docs_api.prototype['put_TextColor']                             = asc_docs_api.prototype.put_TextColor;
	asc_docs_api.prototype['put_ParagraphShade']                        = asc_docs_api.prototype.put_ParagraphShade;
	asc_docs_api.prototype['put_PrIndent']                              = asc_docs_api.prototype.put_PrIndent;
	asc_docs_api.prototype['IncreaseIndent']                            = asc_docs_api.prototype.IncreaseIndent;
	asc_docs_api.prototype['DecreaseIndent']                            = asc_docs_api.prototype.DecreaseIndent;
	asc_docs_api.prototype['put_PrIndentRight']                         = asc_docs_api.prototype.put_PrIndentRight;
	asc_docs_api.prototype['put_PrFirstLineIndent']                     = asc_docs_api.prototype.put_PrFirstLineIndent;
	asc_docs_api.prototype['put_Margins']                               = asc_docs_api.prototype.put_Margins;
	asc_docs_api.prototype['getFocusObject']                            = asc_docs_api.prototype.getFocusObject;
	asc_docs_api.prototype['sync_VerticalAlign']                        = asc_docs_api.prototype.sync_VerticalAlign;
	asc_docs_api.prototype['sync_PrAlignCallBack']                      = asc_docs_api.prototype.sync_PrAlignCallBack;
	asc_docs_api.prototype['sync_ListType']                             = asc_docs_api.prototype.sync_ListType;
	asc_docs_api.prototype['sync_TextColor']                            = asc_docs_api.prototype.sync_TextColor;
	asc_docs_api.prototype['sync_TextHighLight']                        = asc_docs_api.prototype.sync_TextHighLight;
	asc_docs_api.prototype['sync_TextSpacing']                          = asc_docs_api.prototype.sync_TextSpacing;
	asc_docs_api.prototype['sync_TextDStrikeout']                       = asc_docs_api.prototype.sync_TextDStrikeout;
	asc_docs_api.prototype['sync_TextCaps']                             = asc_docs_api.prototype.sync_TextCaps;
	asc_docs_api.prototype['sync_TextSmallCaps']                        = asc_docs_api.prototype.sync_TextSmallCaps;
	asc_docs_api.prototype['sync_TextPosition']                         = asc_docs_api.prototype.sync_TextPosition;
	asc_docs_api.prototype['sync_TextLangCallBack']                     = asc_docs_api.prototype.sync_TextLangCallBack;
	asc_docs_api.prototype['sync_ParaStyleName']                        = asc_docs_api.prototype.sync_ParaStyleName;
	asc_docs_api.prototype['sync_ParaSpacingLine']                      = asc_docs_api.prototype.sync_ParaSpacingLine;
	asc_docs_api.prototype['sync_PageBreakCallback']                    = asc_docs_api.prototype.sync_PageBreakCallback;
	asc_docs_api.prototype['sync_WidowControlCallback']                 = asc_docs_api.prototype.sync_WidowControlCallback;
	asc_docs_api.prototype['sync_KeepNextCallback']                     = asc_docs_api.prototype.sync_KeepNextCallback;
	asc_docs_api.prototype['sync_KeepLinesCallback']                    = asc_docs_api.prototype.sync_KeepLinesCallback;
	asc_docs_api.prototype['sync_ShowParaMarksCallback']                = asc_docs_api.prototype.sync_ShowParaMarksCallback;
	asc_docs_api.prototype['sync_SpaceBetweenPrgCallback']              = asc_docs_api.prototype.sync_SpaceBetweenPrgCallback;
	asc_docs_api.prototype['sync_PrPropCallback']                       = asc_docs_api.prototype.sync_PrPropCallback;
	asc_docs_api.prototype['sync_MathPropCallback']                     = asc_docs_api.prototype.sync_MathPropCallback;
	asc_docs_api.prototype['sync_EndAddShape']                          = asc_docs_api.prototype.sync_EndAddShape;
	asc_docs_api.prototype['SetDrawingFreeze']                          = asc_docs_api.prototype.SetDrawingFreeze;
	asc_docs_api.prototype['change_PageOrient']                         = asc_docs_api.prototype.change_PageOrient;
	asc_docs_api.prototype['get_DocumentOrientation']                   = asc_docs_api.prototype.get_DocumentOrientation;
	asc_docs_api.prototype['change_DocSize']                            = asc_docs_api.prototype.change_DocSize;
	asc_docs_api.prototype['get_DocumentWidth']                         = asc_docs_api.prototype.get_DocumentWidth;
	asc_docs_api.prototype['get_DocumentHeight']                        = asc_docs_api.prototype.get_DocumentHeight;
	asc_docs_api.prototype['put_AddPageBreak']                          = asc_docs_api.prototype.put_AddPageBreak;
	asc_docs_api.prototype['put_AddColumnBreak']                        = asc_docs_api.prototype.put_AddColumnBreak;
	asc_docs_api.prototype['Update_ParaInd']                            = asc_docs_api.prototype.Update_ParaInd;
	asc_docs_api.prototype['Internal_Update_Ind_FirstLine']             = asc_docs_api.prototype.Internal_Update_Ind_FirstLine;
	asc_docs_api.prototype['Internal_Update_Ind_Left']                  = asc_docs_api.prototype.Internal_Update_Ind_Left;
	asc_docs_api.prototype['Internal_Update_Ind_Right']                 = asc_docs_api.prototype.Internal_Update_Ind_Right;
	asc_docs_api.prototype['put_PageNum']                               = asc_docs_api.prototype.put_PageNum;
	asc_docs_api.prototype['put_HeadersAndFootersDistance']             = asc_docs_api.prototype.put_HeadersAndFootersDistance;
	asc_docs_api.prototype['HeadersAndFooters_DifferentFirstPage']      = asc_docs_api.prototype.HeadersAndFooters_DifferentFirstPage;
	asc_docs_api.prototype['HeadersAndFooters_DifferentOddandEvenPage'] = asc_docs_api.prototype.HeadersAndFooters_DifferentOddandEvenPage;
	asc_docs_api.prototype['HeadersAndFooters_LinkToPrevious']          = asc_docs_api.prototype.HeadersAndFooters_LinkToPrevious;
	asc_docs_api.prototype['sync_DocSizeCallback']                      = asc_docs_api.prototype.sync_DocSizeCallback;
	asc_docs_api.prototype['sync_PageOrientCallback']                   = asc_docs_api.prototype.sync_PageOrientCallback;
	asc_docs_api.prototype['sync_HeadersAndFootersPropCallback']        = asc_docs_api.prototype.sync_HeadersAndFootersPropCallback;
	asc_docs_api.prototype['put_Table']                                 = asc_docs_api.prototype.put_Table;
	asc_docs_api.prototype['addRowAbove']                               = asc_docs_api.prototype.addRowAbove;
	asc_docs_api.prototype['addRowBelow']                               = asc_docs_api.prototype.addRowBelow;
	asc_docs_api.prototype['addColumnLeft']                             = asc_docs_api.prototype.addColumnLeft;
	asc_docs_api.prototype['addColumnRight']                            = asc_docs_api.prototype.addColumnRight;
	asc_docs_api.prototype['remRow']                                    = asc_docs_api.prototype.remRow;
	asc_docs_api.prototype['remColumn']                                 = asc_docs_api.prototype.remColumn;
	asc_docs_api.prototype['remTable']                                  = asc_docs_api.prototype.remTable;
	asc_docs_api.prototype['selectRow']                                 = asc_docs_api.prototype.selectRow;
	asc_docs_api.prototype['selectColumn']                              = asc_docs_api.prototype.selectColumn;
	asc_docs_api.prototype['selectCell']                                = asc_docs_api.prototype.selectCell;
	asc_docs_api.prototype['selectTable']                               = asc_docs_api.prototype.selectTable;
	asc_docs_api.prototype['setColumnWidth']                            = asc_docs_api.prototype.setColumnWidth;
	asc_docs_api.prototype['setRowHeight']                              = asc_docs_api.prototype.setRowHeight;
	asc_docs_api.prototype['set_TblDistanceFromText']                   = asc_docs_api.prototype.set_TblDistanceFromText;
	asc_docs_api.prototype['CheckBeforeMergeCells']                     = asc_docs_api.prototype.CheckBeforeMergeCells;
	asc_docs_api.prototype['CheckBeforeSplitCells']                     = asc_docs_api.prototype.CheckBeforeSplitCells;
	asc_docs_api.prototype['MergeCells']                                = asc_docs_api.prototype.MergeCells;
	asc_docs_api.prototype['SplitCell']                                 = asc_docs_api.prototype.SplitCell;
	asc_docs_api.prototype['widthTable']                                = asc_docs_api.prototype.widthTable;
	asc_docs_api.prototype['put_CellsMargin']                           = asc_docs_api.prototype.put_CellsMargin;
	asc_docs_api.prototype['set_TblWrap']                               = asc_docs_api.prototype.set_TblWrap;
	asc_docs_api.prototype['set_TblIndentLeft']                         = asc_docs_api.prototype.set_TblIndentLeft;
	asc_docs_api.prototype['set_Borders']                               = asc_docs_api.prototype.set_Borders;
	asc_docs_api.prototype['set_TableBackground']                       = asc_docs_api.prototype.set_TableBackground;
	asc_docs_api.prototype['set_AlignCell']                             = asc_docs_api.prototype.set_AlignCell;
	asc_docs_api.prototype['set_TblAlign']                              = asc_docs_api.prototype.set_TblAlign;
	asc_docs_api.prototype['set_SpacingBetweenCells']                   = asc_docs_api.prototype.set_SpacingBetweenCells;
	asc_docs_api.prototype['tblApply']                                  = asc_docs_api.prototype.tblApply;
	asc_docs_api.prototype['sync_AddTableCallback']                     = asc_docs_api.prototype.sync_AddTableCallback;
	asc_docs_api.prototype['sync_AlignCellCallback']                    = asc_docs_api.prototype.sync_AlignCellCallback;
	asc_docs_api.prototype['sync_TblPropCallback']                      = asc_docs_api.prototype.sync_TblPropCallback;
	asc_docs_api.prototype['sync_TblWrapStyleChangedCallback']          = asc_docs_api.prototype.sync_TblWrapStyleChangedCallback;
	asc_docs_api.prototype['sync_TblAlignChangedCallback']              = asc_docs_api.prototype.sync_TblAlignChangedCallback;
	asc_docs_api.prototype['ChangeImageFromFile']                       = asc_docs_api.prototype.ChangeImageFromFile;
	asc_docs_api.prototype['ChangeShapeImageFromFile']                  = asc_docs_api.prototype.ChangeShapeImageFromFile;
	asc_docs_api.prototype['AddImage']                                  = asc_docs_api.prototype.AddImage;
	asc_docs_api.prototype['asc_addImage']                              = asc_docs_api.prototype.asc_addImage;
	asc_docs_api.prototype['AddImageUrl2']                              = asc_docs_api.prototype.AddImageUrl2;
	asc_docs_api.prototype['AddImageUrl']                               = asc_docs_api.prototype.AddImageUrl;
	asc_docs_api.prototype['AddImageUrlAction']                         = asc_docs_api.prototype.AddImageUrlAction;
	asc_docs_api.prototype['AddImageToPage']                            = asc_docs_api.prototype.AddImageToPage;
	asc_docs_api.prototype['ImgApply']                                  = asc_docs_api.prototype.ImgApply;
	asc_docs_api.prototype['set_Size']                                  = asc_docs_api.prototype.set_Size;
	asc_docs_api.prototype['set_ConstProportions']                      = asc_docs_api.prototype.set_ConstProportions;
	asc_docs_api.prototype['set_WrapStyle']                             = asc_docs_api.prototype.set_WrapStyle;
	asc_docs_api.prototype['deleteImage']                               = asc_docs_api.prototype.deleteImage;
	asc_docs_api.prototype['set_ImgDistanceFromText']                   = asc_docs_api.prototype.set_ImgDistanceFromText;
	asc_docs_api.prototype['set_PositionOnPage']                        = asc_docs_api.prototype.set_PositionOnPage;
	asc_docs_api.prototype['get_OriginalSizeImage']                     = asc_docs_api.prototype.get_OriginalSizeImage;
	asc_docs_api.prototype['ShapeApply']                                = asc_docs_api.prototype.ShapeApply;
	asc_docs_api.prototype['sync_AddImageCallback']                     = asc_docs_api.prototype.sync_AddImageCallback;
	asc_docs_api.prototype['sync_ImgPropCallback']                      = asc_docs_api.prototype.sync_ImgPropCallback;
	asc_docs_api.prototype['sync_ImgWrapStyleChangedCallback']          = asc_docs_api.prototype.sync_ImgWrapStyleChangedCallback;
	asc_docs_api.prototype['sync_ContextMenuCallback']                  = asc_docs_api.prototype.sync_ContextMenuCallback;
	asc_docs_api.prototype['sync_MouseMoveStartCallback']               = asc_docs_api.prototype.sync_MouseMoveStartCallback;
	asc_docs_api.prototype['sync_MouseMoveEndCallback']                 = asc_docs_api.prototype.sync_MouseMoveEndCallback;
	asc_docs_api.prototype['sync_MouseMoveCallback']                    = asc_docs_api.prototype.sync_MouseMoveCallback;
	asc_docs_api.prototype['asc_setChartTranslate']                     = asc_docs_api.prototype.asc_setChartTranslate;
	asc_docs_api.prototype['asc_setTextArtTranslate']                   = asc_docs_api.prototype.asc_setTextArtTranslate;
	asc_docs_api.prototype['can_AddHyperlink']                          = asc_docs_api.prototype.can_AddHyperlink;
	asc_docs_api.prototype['add_Hyperlink']                             = asc_docs_api.prototype.add_Hyperlink;
	asc_docs_api.prototype['change_Hyperlink']                          = asc_docs_api.prototype.change_Hyperlink;
	asc_docs_api.prototype['remove_Hyperlink']                          = asc_docs_api.prototype.remove_Hyperlink;
	asc_docs_api.prototype['sync_HyperlinkPropCallback']                = asc_docs_api.prototype.sync_HyperlinkPropCallback;
	asc_docs_api.prototype['sync_HyperlinkClickCallback']               = asc_docs_api.prototype.sync_HyperlinkClickCallback;
	asc_docs_api.prototype['sync_CanAddHyperlinkCallback']              = asc_docs_api.prototype.sync_CanAddHyperlinkCallback;
	asc_docs_api.prototype['sync_DialogAddHyperlink']                   = asc_docs_api.prototype.sync_DialogAddHyperlink;
	asc_docs_api.prototype['sync_DialogAddHyperlink']                   = asc_docs_api.prototype.sync_DialogAddHyperlink;
	asc_docs_api.prototype['sync_SpellCheckCallback']                   = asc_docs_api.prototype.sync_SpellCheckCallback;
	asc_docs_api.prototype['sync_SpellCheckVariantsFound']              = asc_docs_api.prototype.sync_SpellCheckVariantsFound;
	asc_docs_api.prototype['asc_replaceMisspelledWord']                 = asc_docs_api.prototype.asc_replaceMisspelledWord;
	asc_docs_api.prototype['asc_ignoreMisspelledWord']                  = asc_docs_api.prototype.asc_ignoreMisspelledWord;
	asc_docs_api.prototype['asc_setDefaultLanguage']                    = asc_docs_api.prototype.asc_setDefaultLanguage;
	asc_docs_api.prototype['asc_getDefaultLanguage']                    = asc_docs_api.prototype.asc_getDefaultLanguage;
	asc_docs_api.prototype['asc_getKeyboardLanguage']                   = asc_docs_api.prototype.asc_getKeyboardLanguage;
	asc_docs_api.prototype['asc_setSpellCheck']                         = asc_docs_api.prototype.asc_setSpellCheck;
	asc_docs_api.prototype['asc_showComments']                          = asc_docs_api.prototype.asc_showComments;
	asc_docs_api.prototype['asc_hideComments']                          = asc_docs_api.prototype.asc_hideComments;
	asc_docs_api.prototype['asc_addComment']                            = asc_docs_api.prototype.asc_addComment;
	asc_docs_api.prototype['asc_removeComment']                         = asc_docs_api.prototype.asc_removeComment;
	asc_docs_api.prototype['asc_changeComment']                         = asc_docs_api.prototype.asc_changeComment;
	asc_docs_api.prototype['asc_selectComment']                         = asc_docs_api.prototype.asc_selectComment;
	asc_docs_api.prototype['asc_showComment']                           = asc_docs_api.prototype.asc_showComment;
	asc_docs_api.prototype['can_AddQuotedComment']                      = asc_docs_api.prototype.can_AddQuotedComment;
	asc_docs_api.prototype['sync_RemoveComment']                        = asc_docs_api.prototype.sync_RemoveComment;
	asc_docs_api.prototype['sync_AddComment']                           = asc_docs_api.prototype.sync_AddComment;
	asc_docs_api.prototype['sync_ShowComment']                          = asc_docs_api.prototype.sync_ShowComment;
	asc_docs_api.prototype['sync_HideComment']                          = asc_docs_api.prototype.sync_HideComment;
	asc_docs_api.prototype['sync_UpdateCommentPosition']                = asc_docs_api.prototype.sync_UpdateCommentPosition;
	asc_docs_api.prototype['sync_ChangeCommentData']                    = asc_docs_api.prototype.sync_ChangeCommentData;
	asc_docs_api.prototype['sync_LockComment']                          = asc_docs_api.prototype.sync_LockComment;
	asc_docs_api.prototype['sync_UnLockComment']                        = asc_docs_api.prototype.sync_UnLockComment;
	asc_docs_api.prototype['asc_getComments']                           = asc_docs_api.prototype.asc_getComments;
	asc_docs_api.prototype['sync_LockHeaderFooters']                    = asc_docs_api.prototype.sync_LockHeaderFooters;
	asc_docs_api.prototype['sync_LockDocumentProps']                    = asc_docs_api.prototype.sync_LockDocumentProps;
	asc_docs_api.prototype['sync_UnLockHeaderFooters']                  = asc_docs_api.prototype.sync_UnLockHeaderFooters;
	asc_docs_api.prototype['sync_UnLockDocumentProps']                  = asc_docs_api.prototype.sync_UnLockDocumentProps;
	asc_docs_api.prototype['sync_CollaborativeChanges']                 = asc_docs_api.prototype.sync_CollaborativeChanges;
	asc_docs_api.prototype['sync_LockDocumentSchema']                   = asc_docs_api.prototype.sync_LockDocumentSchema;
	asc_docs_api.prototype['sync_UnLockDocumentSchema']                 = asc_docs_api.prototype.sync_UnLockDocumentSchema;
	asc_docs_api.prototype['zoomIn']                                    = asc_docs_api.prototype.zoomIn;
	asc_docs_api.prototype['zoomOut']                                   = asc_docs_api.prototype.zoomOut;
	asc_docs_api.prototype['zoomFitToPage']                             = asc_docs_api.prototype.zoomFitToPage;
	asc_docs_api.prototype['zoomFitToWidth']                            = asc_docs_api.prototype.zoomFitToWidth;
	asc_docs_api.prototype['zoomCustomMode']                            = asc_docs_api.prototype.zoomCustomMode;
	asc_docs_api.prototype['zoom100']                                   = asc_docs_api.prototype.zoom100;
	asc_docs_api.prototype['zoom']                                      = asc_docs_api.prototype.zoom;
	asc_docs_api.prototype['goToPage']                                  = asc_docs_api.prototype.goToPage;
	asc_docs_api.prototype['getCountPages']                             = asc_docs_api.prototype.getCountPages;
	asc_docs_api.prototype['getCurrentPage']                            = asc_docs_api.prototype.getCurrentPage;
	asc_docs_api.prototype['sync_countPagesCallback']                   = asc_docs_api.prototype.sync_countPagesCallback;
	asc_docs_api.prototype['sync_currentPageCallback']                  = asc_docs_api.prototype.sync_currentPageCallback;
	asc_docs_api.prototype['asc_enableKeyEvents']                       = asc_docs_api.prototype.asc_enableKeyEvents;
	asc_docs_api.prototype['GenerateStyles']                            = asc_docs_api.prototype.GenerateStyles;
	asc_docs_api.prototype['asyncFontsDocumentEndLoaded']               = asc_docs_api.prototype.asyncFontsDocumentEndLoaded;
	asc_docs_api.prototype['CreateFontsCharMap']                        = asc_docs_api.prototype.CreateFontsCharMap;
	asc_docs_api.prototype['sync_SendThemeColors']                      = asc_docs_api.prototype.sync_SendThemeColors;
	asc_docs_api.prototype['sync_SendThemeColorSchemes']                = asc_docs_api.prototype.sync_SendThemeColorSchemes;
	asc_docs_api.prototype['ChangeColorScheme']                         = asc_docs_api.prototype.ChangeColorScheme;
	asc_docs_api.prototype['asyncImagesDocumentEndLoaded']              = asc_docs_api.prototype.asyncImagesDocumentEndLoaded;
	asc_docs_api.prototype['OpenDocumentEndCallback']                   = asc_docs_api.prototype.OpenDocumentEndCallback;
	asc_docs_api.prototype['UpdateInterfaceState']                      = asc_docs_api.prototype.UpdateInterfaceState;
	asc_docs_api.prototype['asyncFontEndLoaded']                        = asc_docs_api.prototype.asyncFontEndLoaded;
	asc_docs_api.prototype['asyncImageEndLoaded']                       = asc_docs_api.prototype.asyncImageEndLoaded;
	asc_docs_api.prototype['asyncImageEndLoadedBackground']             = asc_docs_api.prototype.asyncImageEndLoadedBackground;
	asc_docs_api.prototype['IsAsyncOpenDocumentImages']                 = asc_docs_api.prototype.IsAsyncOpenDocumentImages;
	asc_docs_api.prototype['pre_Paste']                                 = asc_docs_api.prototype.pre_Paste;
	asc_docs_api.prototype['pre_Save']                                  = asc_docs_api.prototype.pre_Save;
	asc_docs_api.prototype['SyncLoadImages']                            = asc_docs_api.prototype.SyncLoadImages;
	asc_docs_api.prototype['SyncLoadImages_callback']                   = asc_docs_api.prototype.SyncLoadImages_callback;
	asc_docs_api.prototype['pre_SaveCallback']                          = asc_docs_api.prototype.pre_SaveCallback;
	asc_docs_api.prototype['initEvents2MobileAdvances']                 = asc_docs_api.prototype.initEvents2MobileAdvances;
	asc_docs_api.prototype['ViewScrollToX']                             = asc_docs_api.prototype.ViewScrollToX;
	asc_docs_api.prototype['ViewScrollToY']                             = asc_docs_api.prototype.ViewScrollToY;
	asc_docs_api.prototype['GetDocWidthPx']                             = asc_docs_api.prototype.GetDocWidthPx;
	asc_docs_api.prototype['GetDocHeightPx']                            = asc_docs_api.prototype.GetDocHeightPx;
	asc_docs_api.prototype['ClearSearch']                               = asc_docs_api.prototype.ClearSearch;
	asc_docs_api.prototype['GetCurrentVisiblePage']                     = asc_docs_api.prototype.GetCurrentVisiblePage;
	asc_docs_api.prototype['asc_setAutoSaveGap']                        = asc_docs_api.prototype.asc_setAutoSaveGap;
	asc_docs_api.prototype['asc_SetDocumentPlaceChangedEnabled']        = asc_docs_api.prototype.asc_SetDocumentPlaceChangedEnabled;
	asc_docs_api.prototype['asc_SetViewRulers']                         = asc_docs_api.prototype.asc_SetViewRulers;
	asc_docs_api.prototype['asc_SetViewRulersChange']                   = asc_docs_api.prototype.asc_SetViewRulersChange;
	asc_docs_api.prototype['asc_GetViewRulers']                         = asc_docs_api.prototype.asc_GetViewRulers;
	asc_docs_api.prototype['asc_SetDocumentUnits']                      = asc_docs_api.prototype.asc_SetDocumentUnits;
	asc_docs_api.prototype['SetMobileVersion']                          = asc_docs_api.prototype.SetMobileVersion;
	asc_docs_api.prototype['GoToHeader']                                = asc_docs_api.prototype.GoToHeader;
	asc_docs_api.prototype['GoToFooter']                                = asc_docs_api.prototype.GoToFooter;
	asc_docs_api.prototype['ExitHeader_Footer']                         = asc_docs_api.prototype.ExitHeader_Footer;
	asc_docs_api.prototype['GetCurrentPixOffsetY']                      = asc_docs_api.prototype.GetCurrentPixOffsetY;
	asc_docs_api.prototype['SetPaintFormat']                            = asc_docs_api.prototype.SetPaintFormat;
	asc_docs_api.prototype['ChangeShapeType']                           = asc_docs_api.prototype.ChangeShapeType;
	asc_docs_api.prototype['sync_PaintFormatCallback']                  = asc_docs_api.prototype.sync_PaintFormatCallback;
	asc_docs_api.prototype['SetMarkerFormat']                           = asc_docs_api.prototype.SetMarkerFormat;
	asc_docs_api.prototype['sync_MarkerFormatCallback']                 = asc_docs_api.prototype.sync_MarkerFormatCallback;
	asc_docs_api.prototype['StartAddShape']                             = asc_docs_api.prototype.StartAddShape;
	asc_docs_api.prototype['AddTextArt']                                = asc_docs_api.prototype.AddTextArt;
	asc_docs_api.prototype['sync_StartAddShapeCallback']                = asc_docs_api.prototype.sync_StartAddShapeCallback;
	asc_docs_api.prototype['CanGroup']                                  = asc_docs_api.prototype.CanGroup;
	asc_docs_api.prototype['CanUnGroup']                                = asc_docs_api.prototype.CanUnGroup;
	asc_docs_api.prototype['CanChangeWrapPolygon']                      = asc_docs_api.prototype.CanChangeWrapPolygon;
	asc_docs_api.prototype['StartChangeWrapPolygon']                    = asc_docs_api.prototype.StartChangeWrapPolygon;
	asc_docs_api.prototype['ClearFormating']                            = asc_docs_api.prototype.ClearFormating;
	asc_docs_api.prototype['GetSectionInfo']                            = asc_docs_api.prototype.GetSectionInfo;
	asc_docs_api.prototype['add_SectionBreak']                          = asc_docs_api.prototype.add_SectionBreak;
	asc_docs_api.prototype['asc_setViewMode']                           = asc_docs_api.prototype.asc_setViewMode;
	asc_docs_api.prototype['SetUseEmbeddedCutFonts']                    = asc_docs_api.prototype.SetUseEmbeddedCutFonts;
	asc_docs_api.prototype['OnMouseUp']                                 = asc_docs_api.prototype.OnMouseUp;
	asc_docs_api.prototype['asyncImageEndLoaded2']                      = asc_docs_api.prototype.asyncImageEndLoaded2;
	asc_docs_api.prototype['SetDrawImagePlaceParagraph']                = asc_docs_api.prototype.SetDrawImagePlaceParagraph;
	asc_docs_api.prototype['asc_getMasterCommentId']                    = asc_docs_api.prototype.asc_getMasterCommentId;
	asc_docs_api.prototype['asc_getAnchorPosition']                     = asc_docs_api.prototype.asc_getAnchorPosition;
	asc_docs_api.prototype['asc_getChartObject']                        = asc_docs_api.prototype.asc_getChartObject;
	asc_docs_api.prototype['asc_addChartDrawingObject']                 = asc_docs_api.prototype.asc_addChartDrawingObject;
	asc_docs_api.prototype['asc_doubleClickOnChart']                    = asc_docs_api.prototype.asc_doubleClickOnChart;
	asc_docs_api.prototype['asc_onCloseChartFrame']                     = asc_docs_api.prototype.asc_onCloseChartFrame;
	asc_docs_api.prototype['asc_editChartDrawingObject']                = asc_docs_api.prototype.asc_editChartDrawingObject;
	asc_docs_api.prototype['asc_getChartPreviews']                      = asc_docs_api.prototype.asc_getChartPreviews;
	asc_docs_api.prototype['asc_getTextArtPreviews']                    = asc_docs_api.prototype.asc_getTextArtPreviews;
	asc_docs_api.prototype['sync_closeChartEditor']                     = asc_docs_api.prototype.sync_closeChartEditor;
	asc_docs_api.prototype['asc_setDrawCollaborationMarks']             = asc_docs_api.prototype.asc_setDrawCollaborationMarks;
	asc_docs_api.prototype['asc_AddMath']                               = asc_docs_api.prototype.asc_AddMath;
	asc_docs_api.prototype['asc_AddMath2']                              = asc_docs_api.prototype.asc_AddMath2;
	asc_docs_api.prototype['asc_StartMailMerge']                        = asc_docs_api.prototype.asc_StartMailMerge;
	asc_docs_api.prototype['asc_StartMailMergeByList']                  = asc_docs_api.prototype.asc_StartMailMergeByList;
	asc_docs_api.prototype['asc_GetReceptionsCount']                    = asc_docs_api.prototype.asc_GetReceptionsCount;
	asc_docs_api.prototype['asc_GetMailMergeFieldsNameList']            = asc_docs_api.prototype.asc_GetMailMergeFieldsNameList;
	asc_docs_api.prototype['asc_AddMailMergeField']                     = asc_docs_api.prototype.asc_AddMailMergeField;
	asc_docs_api.prototype['asc_SetHighlightMailMergeFields']           = asc_docs_api.prototype.asc_SetHighlightMailMergeFields;
	asc_docs_api.prototype['asc_PreviewMailMergeResult']                = asc_docs_api.prototype.asc_PreviewMailMergeResult;
	asc_docs_api.prototype['asc_EndPreviewMailMergeResult']             = asc_docs_api.prototype.asc_EndPreviewMailMergeResult;
	asc_docs_api.prototype['sync_StartMailMerge']                       = asc_docs_api.prototype.sync_StartMailMerge;
	asc_docs_api.prototype['sync_PreviewMailMergeResult']               = asc_docs_api.prototype.sync_PreviewMailMergeResult;
	asc_docs_api.prototype['sync_EndPreviewMailMergeResult']            = asc_docs_api.prototype.sync_EndPreviewMailMergeResult;
	asc_docs_api.prototype['sync_HighlightMailMergeFields']             = asc_docs_api.prototype.sync_HighlightMailMergeFields;
	asc_docs_api.prototype['asc_getMailMergeData']                      = asc_docs_api.prototype.asc_getMailMergeData;
	asc_docs_api.prototype['asc_setMailMergeData']                      = asc_docs_api.prototype.asc_setMailMergeData;
	asc_docs_api.prototype['asc_sendMailMergeData']                     = asc_docs_api.prototype.asc_sendMailMergeData;
	asc_docs_api.prototype['asc_GetMailMergeFiledValue']                = asc_docs_api.prototype.asc_GetMailMergeFiledValue;
	asc_docs_api.prototype['asc_GetStyleFromFormatting']                = asc_docs_api.prototype.asc_GetStyleFromFormatting;
	asc_docs_api.prototype['asc_AddNewStyle']                           = asc_docs_api.prototype.asc_AddNewStyle;
	asc_docs_api.prototype['asc_RemoveStyle']                           = asc_docs_api.prototype.asc_RemoveStyle;
	asc_docs_api.prototype['asc_RemoveAllCustomStyles']                 = asc_docs_api.prototype.asc_RemoveAllCustomStyles;
	asc_docs_api.prototype['asc_IsStyleDefault']                        = asc_docs_api.prototype.asc_IsStyleDefault;
	asc_docs_api.prototype['asc_IsDefaultStyleChanged']                 = asc_docs_api.prototype.asc_IsDefaultStyleChanged;
	asc_docs_api.prototype['asc_GetStyleNameById']                      = asc_docs_api.prototype.asc_GetStyleNameById;
	asc_docs_api.prototype['asc_SetTrackRevisions']                     = asc_docs_api.prototype.asc_SetTrackRevisions;
	asc_docs_api.prototype['asc_IsTrackRevisions']                      = asc_docs_api.prototype.asc_IsTrackRevisions;
	asc_docs_api.prototype['sync_BeginCatchRevisionsChanges']           = asc_docs_api.prototype.sync_BeginCatchRevisionsChanges;
	asc_docs_api.prototype['sync_EndCatchRevisionsChanges']             = asc_docs_api.prototype.sync_EndCatchRevisionsChanges;
	asc_docs_api.prototype['sync_AddRevisionsChange']                   = asc_docs_api.prototype.sync_AddRevisionsChange;
	asc_docs_api.prototype['asc_AcceptChanges']                         = asc_docs_api.prototype.asc_AcceptChanges;
	asc_docs_api.prototype['asc_RejectChanges']                         = asc_docs_api.prototype.asc_RejectChanges;
	asc_docs_api.prototype['asc_HaveRevisionsChanges']                  = asc_docs_api.prototype.asc_HaveRevisionsChanges;
	asc_docs_api.prototype['asc_HaveNewRevisionsChanges']               = asc_docs_api.prototype.asc_HaveNewRevisionsChanges;
	asc_docs_api.prototype['asc_GetNextRevisionsChange']                = asc_docs_api.prototype.asc_GetNextRevisionsChange;
	asc_docs_api.prototype['asc_GetPrevRevisionsChange']                = asc_docs_api.prototype.asc_GetPrevRevisionsChange;
	asc_docs_api.prototype['sync_UpdateRevisionsChangesPosition']       = asc_docs_api.prototype.sync_UpdateRevisionsChangesPosition;
	asc_docs_api.prototype['asc_AcceptAllChanges']                      = asc_docs_api.prototype.asc_AcceptAllChanges;
	asc_docs_api.prototype['asc_RejectAllChanges']                      = asc_docs_api.prototype.asc_RejectAllChanges;
	asc_docs_api.prototype['asc_stopSaving']                            = asc_docs_api.prototype.asc_stopSaving;
	asc_docs_api.prototype['asc_continueSaving']                        = asc_docs_api.prototype.asc_continueSaving;
	asc_docs_api.prototype['asc_undoAllChanges']                        = asc_docs_api.prototype.asc_undoAllChanges;
	asc_docs_api.prototype['asc_CloseFile']                             = asc_docs_api.prototype.asc_CloseFile;
	asc_docs_api.prototype['asc_addComment']                            = asc_docs_api.prototype.asc_addComment;
	asc_docs_api.prototype['asc_SetFastCollaborative']                  = asc_docs_api.prototype.asc_SetFastCollaborative;
	asc_docs_api.prototype['asc_isOffline']                             = asc_docs_api.prototype.asc_isOffline;
	asc_docs_api.prototype['asc_getUrlType']                            = asc_docs_api.prototype.asc_getUrlType;
	asc_docs_api.prototype["asc_setInterfaceDrawImagePlaceShape"]       = asc_docs_api.prototype.asc_setInterfaceDrawImagePlaceShape;
	asc_docs_api.prototype["asc_pluginsRegister"]                       = asc_docs_api.prototype.asc_pluginsRegister;
	asc_docs_api.prototype["asc_pluginRun"]                             = asc_docs_api.prototype.asc_pluginRun;
	asc_docs_api.prototype["asc_pluginResize"]                          = asc_docs_api.prototype.asc_pluginResize;
	asc_docs_api.prototype["asc_pluginButtonClick"]                     = asc_docs_api.prototype.asc_pluginButtonClick;
	asc_docs_api.prototype["asc_nativeInitBuilder"]                     = asc_docs_api.prototype.asc_nativeInitBuilder;
	asc_docs_api.prototype["asc_SetSilentMode"]                         = asc_docs_api.prototype.asc_SetSilentMode;
	asc_docs_api.prototype["asc_addOleObject"]                          = asc_docs_api.prototype.asc_addOleObject;
	asc_docs_api.prototype["asc_editOleObject"]                         = asc_docs_api.prototype.asc_editOleObject;

	CParagraphPropEx.prototype['get_ContextualSpacing'] = CParagraphPropEx.prototype.get_ContextualSpacing;
	CParagraphPropEx.prototype['get_Ind']               = CParagraphPropEx.prototype.get_Ind;
	CParagraphPropEx.prototype['get_Jc']                = CParagraphPropEx.prototype.get_Jc;
	CParagraphPropEx.prototype['get_KeepLines']         = CParagraphPropEx.prototype.get_KeepLines;
	CParagraphPropEx.prototype['get_KeepNext']          = CParagraphPropEx.prototype.get_KeepNext;
	CParagraphPropEx.prototype['get_PageBreakBefore']   = CParagraphPropEx.prototype.get_PageBreakBefore;
	CParagraphPropEx.prototype['get_Spacing']           = CParagraphPropEx.prototype.get_Spacing;
	CParagraphPropEx.prototype['get_Shd']               = CParagraphPropEx.prototype.get_Shd;
	CParagraphPropEx.prototype['get_WidowControl']      = CParagraphPropEx.prototype.get_WidowControl;
	CParagraphPropEx.prototype['get_Tabs']              = CParagraphPropEx.prototype.get_Tabs;
	CTextProp.prototype['get_Bold']                     = CTextProp.prototype.get_Bold;
	CTextProp.prototype['get_Italic']                   = CTextProp.prototype.get_Italic;
	CTextProp.prototype['get_Underline']                = CTextProp.prototype.get_Underline;
	CTextProp.prototype['get_Strikeout']                = CTextProp.prototype.get_Strikeout;
	CTextProp.prototype['get_FontFamily']               = CTextProp.prototype.get_FontFamily;
	CTextProp.prototype['get_FontSize']                 = CTextProp.prototype.get_FontSize;
	CTextProp.prototype['get_Color']                    = CTextProp.prototype.get_Color;
	CTextProp.prototype['get_VertAlign']                = CTextProp.prototype.get_VertAlign;
	CTextProp.prototype['get_HighLight']                = CTextProp.prototype.get_HighLight;
	CTextProp.prototype['get_Spacing']                  = CTextProp.prototype.get_Spacing;
	CTextProp.prototype['get_DStrikeout']               = CTextProp.prototype.get_DStrikeout;
	CTextProp.prototype['get_Caps']                     = CTextProp.prototype.get_Caps;
	CTextProp.prototype['get_SmallCaps']                = CTextProp.prototype.get_SmallCaps;
	CParagraphAndTextProp.prototype['get_ParaPr']       = CParagraphAndTextProp.prototype.get_ParaPr;
	CParagraphAndTextProp.prototype['get_TextPr']       = CParagraphAndTextProp.prototype.get_TextPr;
	CDocInfoProp.prototype['get_PageCount']             = CDocInfoProp.prototype.get_PageCount;
	CDocInfoProp.prototype['put_PageCount']             = CDocInfoProp.prototype.put_PageCount;
	CDocInfoProp.prototype['get_WordsCount']            = CDocInfoProp.prototype.get_WordsCount;
	CDocInfoProp.prototype['put_WordsCount']            = CDocInfoProp.prototype.put_WordsCount;
	CDocInfoProp.prototype['get_ParagraphCount']        = CDocInfoProp.prototype.get_ParagraphCount;
	CDocInfoProp.prototype['put_ParagraphCount']        = CDocInfoProp.prototype.put_ParagraphCount;
	CDocInfoProp.prototype['get_SymbolsCount']          = CDocInfoProp.prototype.get_SymbolsCount;
	CDocInfoProp.prototype['put_SymbolsCount']          = CDocInfoProp.prototype.put_SymbolsCount;
	CDocInfoProp.prototype['get_SymbolsWSCount']        = CDocInfoProp.prototype.get_SymbolsWSCount;
	CDocInfoProp.prototype['put_SymbolsWSCount']        = CDocInfoProp.prototype.put_SymbolsWSCount;
	CHeader.prototype['get_headerText']                 = CHeader.prototype.get_headerText;
	CHeader.prototype['get_pageNumber']                 = CHeader.prototype.get_pageNumber;
	CHeader.prototype['get_X']                          = CHeader.prototype.get_X;
	CHeader.prototype['get_Y']                          = CHeader.prototype.get_Y;
	CHeader.prototype['get_Level']                      = CHeader.prototype.get_Level;
	window['Asc']['CBackground']                        = window['Asc'].CBackground = CBackground;
	CBackground.prototype['get_Color']            = CBackground.prototype.get_Color;
	CBackground.prototype['put_Color']            = CBackground.prototype.put_Color;
	CBackground.prototype['get_Value']            = CBackground.prototype.get_Value;
	CBackground.prototype['put_Value']            = CBackground.prototype.put_Value;
	window['Asc']['CTablePositionH']              = CTablePositionH;
	CTablePositionH.prototype['get_RelativeFrom'] = CTablePositionH.prototype.get_RelativeFrom;
	CTablePositionH.prototype['put_RelativeFrom'] = CTablePositionH.prototype.put_RelativeFrom;
	CTablePositionH.prototype['get_UseAlign']     = CTablePositionH.prototype.get_UseAlign;
	CTablePositionH.prototype['put_UseAlign']     = CTablePositionH.prototype.put_UseAlign;
	CTablePositionH.prototype['get_Align']        = CTablePositionH.prototype.get_Align;
	CTablePositionH.prototype['put_Align']        = CTablePositionH.prototype.put_Align;
	CTablePositionH.prototype['get_Value']        = CTablePositionH.prototype.get_Value;
	CTablePositionH.prototype['put_Value']        = CTablePositionH.prototype.put_Value;
	window['Asc']['CTablePositionV']              = CTablePositionV;
	CTablePositionV.prototype['get_RelativeFrom'] = CTablePositionV.prototype.get_RelativeFrom;
	CTablePositionV.prototype['put_RelativeFrom'] = CTablePositionV.prototype.put_RelativeFrom;
	CTablePositionV.prototype['get_UseAlign']     = CTablePositionV.prototype.get_UseAlign;
	CTablePositionV.prototype['put_UseAlign']     = CTablePositionV.prototype.put_UseAlign;
	CTablePositionV.prototype['get_Align']        = CTablePositionV.prototype.get_Align;
	CTablePositionV.prototype['put_Align']        = CTablePositionV.prototype.put_Align;
	CTablePositionV.prototype['get_Value']        = CTablePositionV.prototype.get_Value;
	CTablePositionV.prototype['put_Value']        = CTablePositionV.prototype.put_Value;
	window['Asc']['CTablePropLook']               = window['Asc'].CTablePropLook = CTablePropLook;
	CTablePropLook.prototype['get_FirstCol'] = CTablePropLook.prototype.get_FirstCol;
	CTablePropLook.prototype['put_FirstCol'] = CTablePropLook.prototype.put_FirstCol;
	CTablePropLook.prototype['get_FirstRow'] = CTablePropLook.prototype.get_FirstRow;
	CTablePropLook.prototype['put_FirstRow'] = CTablePropLook.prototype.put_FirstRow;
	CTablePropLook.prototype['get_LastCol']  = CTablePropLook.prototype.get_LastCol;
	CTablePropLook.prototype['put_LastCol']  = CTablePropLook.prototype.put_LastCol;
	CTablePropLook.prototype['get_LastRow']  = CTablePropLook.prototype.get_LastRow;
	CTablePropLook.prototype['put_LastRow']  = CTablePropLook.prototype.put_LastRow;
	CTablePropLook.prototype['get_BandHor']  = CTablePropLook.prototype.get_BandHor;
	CTablePropLook.prototype['put_BandHor']  = CTablePropLook.prototype.put_BandHor;
	CTablePropLook.prototype['get_BandVer']  = CTablePropLook.prototype.get_BandVer;
	CTablePropLook.prototype['put_BandVer']  = CTablePropLook.prototype.put_BandVer;
	window['Asc']['CTableProp']              = window['Asc'].CTableProp = CTableProp;
	CTableProp.prototype['get_Width']              = CTableProp.prototype.get_Width;
	CTableProp.prototype['put_Width']              = CTableProp.prototype.put_Width;
	CTableProp.prototype['get_Spacing']            = CTableProp.prototype.get_Spacing;
	CTableProp.prototype['put_Spacing']            = CTableProp.prototype.put_Spacing;
	CTableProp.prototype['get_DefaultMargins']     = CTableProp.prototype.get_DefaultMargins;
	CTableProp.prototype['put_DefaultMargins']     = CTableProp.prototype.put_DefaultMargins;
	CTableProp.prototype['get_CellMargins']        = CTableProp.prototype.get_CellMargins;
	CTableProp.prototype['put_CellMargins']        = CTableProp.prototype.put_CellMargins;
	CTableProp.prototype['get_TableAlignment']     = CTableProp.prototype.get_TableAlignment;
	CTableProp.prototype['put_TableAlignment']     = CTableProp.prototype.put_TableAlignment;
	CTableProp.prototype['get_TableIndent']        = CTableProp.prototype.get_TableIndent;
	CTableProp.prototype['put_TableIndent']        = CTableProp.prototype.put_TableIndent;
	CTableProp.prototype['get_TableWrap']          = CTableProp.prototype.get_TableWrap;
	CTableProp.prototype['put_TableWrap']          = CTableProp.prototype.put_TableWrap;
	CTableProp.prototype['get_TablePaddings']      = CTableProp.prototype.get_TablePaddings;
	CTableProp.prototype['put_TablePaddings']      = CTableProp.prototype.put_TablePaddings;
	CTableProp.prototype['get_TableBorders']       = CTableProp.prototype.get_TableBorders;
	CTableProp.prototype['put_TableBorders']       = CTableProp.prototype.put_TableBorders;
	CTableProp.prototype['get_CellBorders']        = CTableProp.prototype.get_CellBorders;
	CTableProp.prototype['put_CellBorders']        = CTableProp.prototype.put_CellBorders;
	CTableProp.prototype['get_TableBackground']    = CTableProp.prototype.get_TableBackground;
	CTableProp.prototype['put_TableBackground']    = CTableProp.prototype.put_TableBackground;
	CTableProp.prototype['get_CellsBackground']    = CTableProp.prototype.get_CellsBackground;
	CTableProp.prototype['put_CellsBackground']    = CTableProp.prototype.put_CellsBackground;
	CTableProp.prototype['get_Position']           = CTableProp.prototype.get_Position;
	CTableProp.prototype['put_Position']           = CTableProp.prototype.put_Position;
	CTableProp.prototype['get_PositionH']          = CTableProp.prototype.get_PositionH;
	CTableProp.prototype['put_PositionH']          = CTableProp.prototype.put_PositionH;
	CTableProp.prototype['get_PositionV']          = CTableProp.prototype.get_PositionV;
	CTableProp.prototype['put_PositionV']          = CTableProp.prototype.put_PositionV;
	CTableProp.prototype['get_Value_X']            = CTableProp.prototype.get_Value_X;
	CTableProp.prototype['get_Value_Y']            = CTableProp.prototype.get_Value_Y;
	CTableProp.prototype['get_ForSelectedCells']   = CTableProp.prototype.get_ForSelectedCells;
	CTableProp.prototype['put_ForSelectedCells']   = CTableProp.prototype.put_ForSelectedCells;
	CTableProp.prototype['put_CellSelect']         = CTableProp.prototype.put_CellSelect;
	CTableProp.prototype['get_CellSelect']         = CTableProp.prototype.get_CellSelect;
	CTableProp.prototype['get_CanBeFlow']          = CTableProp.prototype.get_CanBeFlow;
	CTableProp.prototype['get_RowsInHeader']       = CTableProp.prototype.get_RowsInHeader;
	CTableProp.prototype['put_RowsInHeader']       = CTableProp.prototype.put_RowsInHeader;
	CTableProp.prototype['get_Locked']             = CTableProp.prototype.get_Locked;
	CTableProp.prototype['get_CellsVAlign']        = CTableProp.prototype.get_CellsVAlign;
	CTableProp.prototype['put_CellsVAlign']        = CTableProp.prototype.put_CellsVAlign;
	CTableProp.prototype['get_TableLook']          = CTableProp.prototype.get_TableLook;
	CTableProp.prototype['put_TableLook']          = CTableProp.prototype.put_TableLook;
	CTableProp.prototype['get_TableStyle']         = CTableProp.prototype.get_TableStyle;
	CTableProp.prototype['put_TableStyle']         = CTableProp.prototype.put_TableStyle;
	CTableProp.prototype['get_AllowOverlap']       = CTableProp.prototype.get_AllowOverlap;
	CTableProp.prototype['put_AllowOverlap']       = CTableProp.prototype.put_AllowOverlap;
	CTableProp.prototype['get_TableLayout']        = CTableProp.prototype.get_TableLayout;
	CTableProp.prototype['put_TableLayout']        = CTableProp.prototype.put_TableLayout;
	CTableProp.prototype['get_CellsTextDirection'] = CTableProp.prototype.get_CellsTextDirection;
	CTableProp.prototype['put_CellsTextDirection'] = CTableProp.prototype.put_CellsTextDirection;
	CTableProp.prototype['get_CellsNoWrap']        = CTableProp.prototype.get_CellsNoWrap;
	CTableProp.prototype['put_CellsNoWrap']        = CTableProp.prototype.put_CellsNoWrap;
	CTableProp.prototype['get_CellsWidth']         = CTableProp.prototype.get_CellsWidth;
	CTableProp.prototype['put_CellsWidth']         = CTableProp.prototype.put_CellsWidth;
	CTableProp.prototype['get_PercentFullWidth']   = CTableProp.prototype.get_PercentFullWidth;
	window['Asc']['CBorders']                      = window['Asc'].CBorders = CBorders;
	CBorders.prototype['get_Left']    = CBorders.prototype.get_Left;
	CBorders.prototype['put_Left']    = CBorders.prototype.put_Left;
	CBorders.prototype['get_Top']     = CBorders.prototype.get_Top;
	CBorders.prototype['put_Top']     = CBorders.prototype.put_Top;
	CBorders.prototype['get_Right']   = CBorders.prototype.get_Right;
	CBorders.prototype['put_Right']   = CBorders.prototype.put_Right;
	CBorders.prototype['get_Bottom']  = CBorders.prototype.get_Bottom;
	CBorders.prototype['put_Bottom']  = CBorders.prototype.put_Bottom;
	CBorders.prototype['get_InsideH'] = CBorders.prototype.get_InsideH;
	CBorders.prototype['put_InsideH'] = CBorders.prototype.put_InsideH;
	CBorders.prototype['get_InsideV'] = CBorders.prototype.get_InsideV;
	CBorders.prototype['put_InsideV'] = CBorders.prototype.put_InsideV;
	window['Asc']['CMargins']         = window['Asc'].CMargins = CMargins;
	CMargins.prototype['get_Left']            = CMargins.prototype.get_Left;
	CMargins.prototype['put_Left']            = CMargins.prototype.put_Left;
	CMargins.prototype['get_Right']           = CMargins.prototype.get_Right;
	CMargins.prototype['put_Right']           = CMargins.prototype.put_Right;
	CMargins.prototype['get_Top']             = CMargins.prototype.get_Top;
	CMargins.prototype['put_Top']             = CMargins.prototype.put_Top;
	CMargins.prototype['get_Bottom']          = CMargins.prototype.get_Bottom;
	CMargins.prototype['put_Bottom']          = CMargins.prototype.put_Bottom;
	CMargins.prototype['get_Flag']            = CMargins.prototype.get_Flag;
	CMargins.prototype['put_Flag']            = CMargins.prototype.put_Flag;
	CContextMenuData.prototype['get_Type']    = CContextMenuData.prototype.get_Type;
	CContextMenuData.prototype['get_X']       = CContextMenuData.prototype.get_X;
	CContextMenuData.prototype['get_Y']       = CContextMenuData.prototype.get_Y;
	CContextMenuData.prototype['get_PageNum'] = CContextMenuData.prototype.get_PageNum;
	CContextMenuData.prototype['is_Header']   = CContextMenuData.prototype.is_Header;
	window['Asc']['CHyperlinkProperty']       = window['Asc'].CHyperlinkProperty = CHyperlinkProperty;
	CHyperlinkProperty.prototype['get_Value']             = CHyperlinkProperty.prototype.get_Value;
	CHyperlinkProperty.prototype['put_Value']             = CHyperlinkProperty.prototype.put_Value;
	CHyperlinkProperty.prototype['get_ToolTip']           = CHyperlinkProperty.prototype.get_ToolTip;
	CHyperlinkProperty.prototype['put_ToolTip']           = CHyperlinkProperty.prototype.put_ToolTip;
	CHyperlinkProperty.prototype['get_Text']              = CHyperlinkProperty.prototype.get_Text;
	CHyperlinkProperty.prototype['put_Text']              = CHyperlinkProperty.prototype.put_Text;
	asc_CSpellCheckProperty.prototype['get_Word']         = asc_CSpellCheckProperty.prototype.get_Word;
	asc_CSpellCheckProperty.prototype['get_Checked']      = asc_CSpellCheckProperty.prototype.get_Checked;
	asc_CSpellCheckProperty.prototype['get_Variants']     = asc_CSpellCheckProperty.prototype.get_Variants;
	window['Asc']['asc_CCommentDataWord']                 = asc_CCommentDataWord;
	asc_CCommentDataWord.prototype['asc_getText']         = asc_CCommentDataWord.prototype.asc_getText;
	asc_CCommentDataWord.prototype['asc_putText']         = asc_CCommentDataWord.prototype.asc_putText;
	asc_CCommentDataWord.prototype['asc_getTime']         = asc_CCommentDataWord.prototype.asc_getTime;
	asc_CCommentDataWord.prototype['asc_putTime']         = asc_CCommentDataWord.prototype.asc_putTime;
	asc_CCommentDataWord.prototype['asc_getUserId']       = asc_CCommentDataWord.prototype.asc_getUserId;
	asc_CCommentDataWord.prototype['asc_putUserId']       = asc_CCommentDataWord.prototype.asc_putUserId;
	asc_CCommentDataWord.prototype['asc_getUserName']     = asc_CCommentDataWord.prototype.asc_getUserName;
	asc_CCommentDataWord.prototype['asc_putUserName']     = asc_CCommentDataWord.prototype.asc_putUserName;
	asc_CCommentDataWord.prototype['asc_getQuoteText']    = asc_CCommentDataWord.prototype.asc_getQuoteText;
	asc_CCommentDataWord.prototype['asc_putQuoteText']    = asc_CCommentDataWord.prototype.asc_putQuoteText;
	asc_CCommentDataWord.prototype['asc_getSolved']       = asc_CCommentDataWord.prototype.asc_getSolved;
	asc_CCommentDataWord.prototype['asc_putSolved']       = asc_CCommentDataWord.prototype.asc_putSolved;
	asc_CCommentDataWord.prototype['asc_getReply']        = asc_CCommentDataWord.prototype.asc_getReply;
	asc_CCommentDataWord.prototype['asc_addReply']        = asc_CCommentDataWord.prototype.asc_addReply;
	asc_CCommentDataWord.prototype['asc_getRepliesCount'] = asc_CCommentDataWord.prototype.asc_getRepliesCount;
})(window, window.document);

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